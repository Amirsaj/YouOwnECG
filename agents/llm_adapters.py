"""
Multi-model LLM adapter layer.

Provides a unified call_agent interface for DeepSeek, Claude, GPT-4o, and Gemini.
Each adapter matches the exact signature and return format of agents/deepseek.call_agent.
"""

from __future__ import annotations
import os
import time
import uuid
import json
from typing import Callable, Optional

import httpx

# Cost per 1M tokens (USD)
MODEL_COSTS = {
    "deepseek":  {"input": 0.55,  "output": 2.19,  "model_id": "deepseek-reasoner"},
    "claude":    {"input": 3.00,  "output": 15.00, "model_id": "claude-sonnet-4-20250514"},
    "gpt4o":     {"input": 2.50,  "output": 10.00, "model_id": "gpt-4o"},
    "gemini":    {"input": 0.10,  "output": 0.40,  "model_id": "gemini-2.0-flash"},
}

MAX_RETRIES = 3
TIMEOUT = 300


def get_call_agent(model_name: str) -> Callable:
    """Return the appropriate call_agent function for the given model."""
    if model_name == "deepseek":
        from agents.deepseek import call_agent
        return call_agent
    elif model_name == "claude":
        return _call_agent_claude
    elif model_name == "gpt4o":
        return _call_agent_openai
    elif model_name == "gemini":
        return _call_agent_gemini
    else:
        raise ValueError(f"Unknown model: {model_name}")


async def _call_agent_claude(
    system_prompt: str,
    user_prompt: str,
    agent_name: str,
    ecg_id: str,
    db=None,
) -> dict:
    """Claude adapter using Anthropic Messages API."""
    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not api_key:
        raise RuntimeError("ANTHROPIC_API_KEY not set")

    model_id = MODEL_COSTS["claude"]["model_id"]
    call_id = f"claude-{agent_name}-{uuid.uuid4().hex[:8]}"

    headers = {
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json",
    }

    payload = {
        "model": model_id,
        "max_tokens": 4096,
        "system": system_prompt,
        "messages": [{"role": "user", "content": user_prompt}],
    }

    t0 = time.perf_counter()
    content = ""
    usage = {"prompt_tokens": 0, "completion_tokens": 0, "reasoning_tokens": 0}

    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        for attempt in range(MAX_RETRIES):
            try:
                resp = await client.post(
                    "https://api.anthropic.com/v1/messages",
                    headers=headers,
                    json=payload,
                )
                resp.raise_for_status()
                data = resp.json()

                content = ""
                for block in data.get("content", []):
                    if block.get("type") == "text":
                        content += block["text"]

                u = data.get("usage", {})
                usage = {
                    "prompt_tokens": u.get("input_tokens", 0),
                    "completion_tokens": u.get("output_tokens", 0),
                    "reasoning_tokens": 0,
                }
                break
            except Exception as exc:
                if attempt < MAX_RETRIES - 1:
                    await _async_sleep(5 * (attempt + 1))
                else:
                    raise RuntimeError(f"Claude API failed after {MAX_RETRIES} attempts: {exc}")

    latency = time.perf_counter() - t0

    if db is not None:
        try:
            from api.db import log_agent_call
            await log_agent_call(db, call_id, ecg_id, agent_name, model_id,
                                 usage["prompt_tokens"], usage["completion_tokens"],
                                 usage["reasoning_tokens"], latency)
        except Exception:
            pass

    return {
        "content": content,
        "reasoning_content": "",
        "usage": usage,
        "latency_sec": latency,
        "call_id": call_id,
        "model": model_id,
    }


async def _call_agent_openai(
    system_prompt: str,
    user_prompt: str,
    agent_name: str,
    ecg_id: str,
    db=None,
) -> dict:
    """GPT-4o adapter using OpenAI Chat Completions API."""
    api_key = os.environ.get("OPENAI_API_KEY", "")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY not set")

    model_id = MODEL_COSTS["gpt4o"]["model_id"]
    call_id = f"gpt4o-{agent_name}-{uuid.uuid4().hex[:8]}"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": model_id,
        "max_tokens": 4096,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    }

    t0 = time.perf_counter()
    content = ""
    usage = {"prompt_tokens": 0, "completion_tokens": 0, "reasoning_tokens": 0}

    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        for attempt in range(MAX_RETRIES):
            try:
                resp = await client.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers=headers,
                    json=payload,
                )
                resp.raise_for_status()
                data = resp.json()

                content = data["choices"][0]["message"]["content"]
                u = data.get("usage", {})
                usage = {
                    "prompt_tokens": u.get("prompt_tokens", 0),
                    "completion_tokens": u.get("completion_tokens", 0),
                    "reasoning_tokens": 0,
                }
                break
            except Exception as exc:
                if attempt < MAX_RETRIES - 1:
                    await _async_sleep(5 * (attempt + 1))
                else:
                    raise RuntimeError(f"OpenAI API failed after {MAX_RETRIES} attempts: {exc}")

    latency = time.perf_counter() - t0

    if db is not None:
        try:
            from api.db import log_agent_call
            await log_agent_call(db, call_id, ecg_id, agent_name, model_id,
                                 usage["prompt_tokens"], usage["completion_tokens"],
                                 usage["reasoning_tokens"], latency)
        except Exception:
            pass

    return {
        "content": content,
        "reasoning_content": "",
        "usage": usage,
        "latency_sec": latency,
        "call_id": call_id,
        "model": model_id,
    }


async def _call_agent_gemini(
    system_prompt: str,
    user_prompt: str,
    agent_name: str,
    ecg_id: str,
    db=None,
) -> dict:
    """Gemini adapter using Google AI Studio OpenAI-compatible endpoint."""
    api_key = os.environ.get("GOOGLE_API_KEY", "")
    if not api_key:
        raise RuntimeError("GOOGLE_API_KEY not set")

    model_id = MODEL_COSTS["gemini"]["model_id"]
    call_id = f"gemini-{agent_name}-{uuid.uuid4().hex[:8]}"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": model_id,
        "max_tokens": 4096,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    }

    t0 = time.perf_counter()
    content = ""
    usage = {"prompt_tokens": 0, "completion_tokens": 0, "reasoning_tokens": 0}

    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        for attempt in range(MAX_RETRIES):
            try:
                resp = await client.post(
                    "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions",
                    headers=headers,
                    json=payload,
                )
                resp.raise_for_status()
                data = resp.json()

                content = data["choices"][0]["message"]["content"]
                u = data.get("usage", {})
                usage = {
                    "prompt_tokens": u.get("prompt_tokens", 0),
                    "completion_tokens": u.get("completion_tokens", 0),
                    "reasoning_tokens": 0,
                }
                break
            except Exception as exc:
                if attempt < MAX_RETRIES - 1:
                    await _async_sleep(5 * (attempt + 1))
                else:
                    raise RuntimeError(f"Gemini API failed after {MAX_RETRIES} attempts: {exc}")

    latency = time.perf_counter() - t0

    if db is not None:
        try:
            from api.db import log_agent_call
            await log_agent_call(db, call_id, ecg_id, agent_name, model_id,
                                 usage["prompt_tokens"], usage["completion_tokens"],
                                 usage["reasoning_tokens"], latency)
        except Exception:
            pass

    return {
        "content": content,
        "reasoning_content": "",
        "usage": usage,
        "latency_sec": latency,
        "call_id": call_id,
        "model": model_id,
    }


async def _async_sleep(seconds: float):
    import asyncio
    await asyncio.sleep(seconds)
