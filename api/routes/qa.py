"""
Q&A streaming route.

POST /ecg/{ecg_id}/qa — ask a follow-up question about an ECG analysis.
Returns a streaming response (text/event-stream).

Context assembly (Node 3.1 fix): forwards only BeatSummary + DiagnosticResult
findings (not the full FeatureObject) to stay within token budget.
"""

from __future__ import annotations
import json
import os

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from api.db import get_db, load_result

router = APIRouter(prefix="/ecg", tags=["qa"])

QA_SYSTEM = """You are a clinical ECG analysis assistant for YouOwnECG.
You help clinicians understand ECG findings. You answer questions about the
specific ECG analysis provided. You do NOT diagnose patients — you explain
the ECG evidence.

Always end every response with:
AI-GENERATED — NOT A CLINICAL DIAGNOSIS — CLINICAL CORRELATION REQUIRED"""


class QARequest(BaseModel):
    question: str


@router.post("/{ecg_id}/qa")
async def qa_stream(ecg_id: str, body: QARequest):
    """
    Stream a Q&A response about a specific ECG analysis.
    Returns text/event-stream.
    """
    db = await get_db()
    result = await load_result(db, ecg_id)
    await db.close()

    if result is None:
        raise HTTPException(status_code=404, detail=f"ECG ID {ecg_id!r} not found")

    api_key = os.environ.get("DEEPSEEK_API_KEY", "")
    if not api_key:
        raise HTTPException(status_code=503, detail="DeepSeek API key not configured")

    context = _build_qa_context(result)

    return StreamingResponse(
        _stream_qa(body.question, context, ecg_id),
        media_type="text/event-stream",
    )


def _build_qa_context(result: dict) -> str:
    """Build bounded Q&A context (BeatSummary + findings only — not full FeatureObject)."""
    measurements = result.get("measurements", {})
    findings = result.get("findings", [])

    ctx = {
        "measurements": {
            "heart_rate_bpm": measurements.get("heart_rate_ventricular_bpm"),
            "pr_ms": measurements.get("pr_interval_ms"),
            "qrs_ms": measurements.get("qrs_duration_global_ms"),
            "qtc_bazett_ms": measurements.get("qtc_bazett_ms"),
            "rhythm": measurements.get("rhythm"),
            "qrs_axis_deg": measurements.get("qrs_axis_deg"),
            "beat_counts": measurements.get("beat_class_counts"),
        },
        "findings": [
            {
                "finding_type": f.get("finding_type"),
                "confidence": f.get("confidence"),
                "clinical_summary": f.get("clinical_summary"),
                "technical_detail": f.get("technical_detail"),
            }
            for f in findings[:7]   # top 7 (Miller's Law)
        ],
        "stat_alerts": result.get("stat_alerts", []),
    }
    return json.dumps(ctx, separators=(",", ":"))


async def _stream_qa(question: str, context: str, ecg_id: str):
    """Generator that streams Q&A tokens as SSE events."""
    import httpx

    headers = {
        "Authorization": f"Bearer {os.environ['DEEPSEEK_API_KEY']}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": os.environ.get("DEEPSEEK_MODEL", "deepseek-reasoner"),
        "messages": [
            {"role": "system", "content": QA_SYSTEM},
            {
                "role": "user",
                "content": f"<ecg_analysis>\n{context}\n</ecg_analysis>\n\nQuestion: {question}",
            },
        ],
        "stream": True,
        "temperature": 0,
        "max_tokens": 1024,
    }

    base_url = os.environ.get("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1")

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            async with client.stream(
                "POST",
                f"{base_url}/chat/completions",
                headers=headers,
                json=payload,
            ) as response:
                async for line in response.aiter_lines():
                    if not line.startswith("data: "):
                        continue
                    data = line[6:]
                    if data.strip() == "[DONE]":
                        yield "data: [DONE]\n\n"
                        return
                    try:
                        chunk = json.loads(data)
                        delta = chunk["choices"][0]["delta"].get("content", "")
                        if delta:
                            yield f"data: {json.dumps({'text': delta})}\n\n"
                    except (json.JSONDecodeError, KeyError, IndexError):
                        continue
    except Exception as exc:
        yield f"data: {json.dumps({'error': str(exc)})}\n\n"
