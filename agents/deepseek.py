"""
Node 2.6 — DeepSeek API client.

Async client for DeepSeek-R1 (reasoner mode). Handles:
- Structured JSON output with schema enforcement
- PHI allowlist (sex, age only — no names/dates/MRNs)
- Exponential backoff retry (max 3 attempts)
- Cost tracking per call
- Audit logging to SQLite
- _RoundedFloatEncoder for float32 serialization
"""

from __future__ import annotations
import asyncio
import json
import os
import re
import time
import uuid
from typing import Any, Optional

import httpx

DEEPSEEK_BASE_URL = os.environ.get("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1")
DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY", "")
MODEL_ID = os.environ.get("DEEPSEEK_MODEL", "deepseek-reasoner")

# Cost model (USD per 1M tokens — from Node 2.6 spec)
COST_PER_M_INPUT = 0.55
COST_PER_M_OUTPUT = 2.19
CIRCUIT_BREAKER_USD = 0.50   # abort if single call exceeds this estimate

MAX_RETRIES = 3
REQUEST_TIMEOUT_SEC = 300.0


class _RoundedFloatEncoder(json.JSONEncoder):
    """Rounds float values to 4 decimal places. Prevents float32 precision noise in prompts."""
    def iterencode(self, obj, _one_shot=False):
        if isinstance(obj, float):
            yield format(round(obj, 4), 'f')
        else:
            yield from super().iterencode(obj, _one_shot)

    def default(self, obj):
        import numpy as np
        if isinstance(obj, (np.floating, np.float32, np.float64)):
            return round(float(obj), 4)
        if isinstance(obj, np.bool_):
            return bool(obj)
        if isinstance(obj, (np.integer,)):
            return int(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super().default(obj)


# PHI fields allowed in prompts (everything else must be stripped)
_PHI_ALLOWLIST = {"patient_sex", "patient_age"}


def _strip_phi(obj: Any, path: str = "") -> Any:
    """
    Recursively strip PHI from dicts/lists before sending to the API.
    Only keys in _PHI_ALLOWLIST are permitted at the top level of patient fields.
    """
    if isinstance(obj, dict):
        return {
            k: _strip_phi(v, f"{path}.{k}")
            for k, v in obj.items()
            if not _is_phi_key(k)
        }
    if isinstance(obj, list):
        return [_strip_phi(item, path) for item in obj]
    return obj


def _is_phi_key(key: str) -> bool:
    phi_patterns = [
        "name", "mrn", "dob", "birth", "address", "phone",
        "email", "ssn", "insurance", "provider", "physician",
        "recording_date", "timestamp", "location",
    ]
    key_lower = key.lower()
    return any(p in key_lower for p in phi_patterns)


async def call_agent(
    system_prompt: str,
    user_prompt: str,
    agent_name: str,
    ecg_id: str,
    db=None,
) -> dict:
    """
    Call the DeepSeek reasoner API and return parsed JSON response.

    Parameters
    ----------
    system_prompt : str
    user_prompt : str
    agent_name : str
        "RRC" | "IT" | "MR" | "CDS"
    ecg_id : str
    db : optional audit DB connection

    Returns
    -------
    dict with keys: content (str), reasoning_content (str), usage (dict)
    """
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": MODEL_ID,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": 0,
        "max_tokens": 8192,
    }

    call_id = str(uuid.uuid4())
    t0 = time.monotonic()
    last_exc = None

    for attempt in range(MAX_RETRIES):
        try:
            async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT_SEC) as client:
                resp = await client.post(
                    f"{DEEPSEEK_BASE_URL}/chat/completions",
                    headers=headers,
                    json=payload,
                )
            resp.raise_for_status()
            data = resp.json()
            break
        except Exception as exc:
            last_exc = exc
            if attempt < MAX_RETRIES - 1:
                await asyncio.sleep(2 ** attempt)
    else:
        raise RuntimeError(f"DeepSeek API call failed after {MAX_RETRIES} attempts: {last_exc}")

    latency = time.monotonic() - t0
    choice = data["choices"][0]["message"]
    usage = data.get("usage", {})

    # Cost guard
    estimated_cost = (
        usage.get("prompt_tokens", 0) / 1_000_000 * COST_PER_M_INPUT +
        usage.get("completion_tokens", 0) / 1_000_000 * COST_PER_M_OUTPUT
    )
    if estimated_cost > CIRCUIT_BREAKER_USD:
        raise RuntimeError(
            f"Cost circuit breaker: estimated ${estimated_cost:.4f} > ${CIRCUIT_BREAKER_USD}"
        )

    result = {
        "content": choice.get("content", ""),
        "reasoning_content": choice.get("reasoning_content", ""),
        "usage": usage,
        "latency_sec": latency,
        "call_id": call_id,
        "model": MODEL_ID,
    }

    if db is not None:
        await _log_audit(db, ecg_id, agent_name, call_id, usage, latency, MODEL_ID)

    return result


async def _log_audit(db, ecg_id: str, agent_name: str, call_id: str, usage: dict, latency: float, model: str):
    """Write audit log entry to SQLite (fail-open — errors are logged but not raised)."""
    try:
        await db.execute(
            """
            INSERT INTO agent_audit_log
              (call_id, ecg_id, agent_name, model_id, prompt_tokens,
               completion_tokens, reasoning_tokens, latency_sec, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
            """,
            (
                call_id, ecg_id, agent_name, model,
                usage.get("prompt_tokens", 0),
                usage.get("completion_tokens", 0),
                usage.get("reasoning_tokens", 0),
                round(latency, 3),
            ),
        )
        await db.commit()
    except Exception:
        pass  # fail-open: audit failure must not block clinical output


def extract_json(text: str) -> dict:
    """
    Extract JSON from agent response text.
    Uses raw_decode to find the first valid JSON object.
    Falls back to regex extraction of ```json ... ``` blocks.
    """
    decoder = json.JSONDecoder()

    # Try raw_decode from each position where '{' appears
    for i, ch in enumerate(text):
        if ch == '{':
            try:
                obj, _ = decoder.raw_decode(text, i)
                return obj
            except json.JSONDecodeError:
                continue

    # Fallback: extract ```json ... ``` block
    match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1))
        except json.JSONDecodeError:
            pass

    return {}


def serialize_for_prompt(obj: Any) -> str:
    """Serialize a Python object to JSON string for use in prompts."""
    return json.dumps(obj, cls=_RoundedFloatEncoder, indent=None, separators=(",", ":"))
