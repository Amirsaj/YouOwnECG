"""
SQLite database for audit trail and ECG result storage.

Schema:
  agent_audit_log  — one row per DeepSeek API call (7-year retention)
  ecg_results      — one row per ECG analysis (DiagnosticResult JSON)

Fail-open: errors in audit writes are silently logged but never propagate
to the clinical result path.
"""

from __future__ import annotations
import json
import os
import aiosqlite

DB_PATH = os.environ.get("DB_PATH", "data/youownecg.db")

CREATE_DDL = """
PRAGMA journal_mode=WAL;

CREATE TABLE IF NOT EXISTS agent_audit_log (
    call_id          TEXT PRIMARY KEY,
    ecg_id           TEXT NOT NULL,
    agent_name       TEXT NOT NULL,
    model_id         TEXT NOT NULL,
    prompt_tokens    INTEGER,
    completion_tokens INTEGER,
    reasoning_tokens INTEGER,
    latency_sec      REAL,
    created_at       TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS ecg_results (
    ecg_id           TEXT PRIMARY KEY,
    result_json      TEXT NOT NULL,
    overall_quality  TEXT,
    stat_alert_count INTEGER,
    pipeline_version TEXT,
    model_version    TEXT,
    created_at       TEXT DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_audit_ecg ON agent_audit_log(ecg_id);
CREATE INDEX IF NOT EXISTS idx_results_created ON ecg_results(created_at);
"""


async def get_db() -> aiosqlite.Connection:
    """Open a database connection. Creates tables on first use."""
    os.makedirs(os.path.dirname(DB_PATH) if os.path.dirname(DB_PATH) else ".", exist_ok=True)
    db = await aiosqlite.connect(DB_PATH)
    await db.executescript(CREATE_DDL)
    await db.commit()
    return db


async def save_result(db: aiosqlite.Connection, result) -> None:
    """Persist a DiagnosticResult to ecg_results table."""
    from dataclasses import asdict
    try:
        result_dict = _result_to_dict(result)
        await db.execute(
            """
            INSERT OR REPLACE INTO ecg_results
              (ecg_id, result_json, overall_quality, stat_alert_count, pipeline_version, model_version)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                result.ecg_id,
                json.dumps(result_dict),
                result.overall_quality,
                len(result.stat_alerts),
                result.pipeline_version,
                result.model_version,
            ),
        )
        await db.commit()
    except Exception:
        pass  # fail-open


async def load_result(db: aiosqlite.Connection, ecg_id: str) -> dict | None:
    """Load a DiagnosticResult dict by ecg_id."""
    async with db.execute(
        "SELECT result_json FROM ecg_results WHERE ecg_id = ?", (ecg_id,)
    ) as cursor:
        row = await cursor.fetchone()
    return json.loads(row[0]) if row else None


def _result_to_dict(result) -> dict:
    """Convert DiagnosticResult dataclass to a JSON-serializable dict."""
    from dataclasses import fields, asdict
    import numpy as np

    def _coerce(obj):
        if isinstance(obj, (np.floating, np.float32, np.float64)):
            return round(float(obj), 4)
        if isinstance(obj, np.bool_):
            return bool(obj)
        if isinstance(obj, (np.integer,)):
            return int(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return obj

    def _walk(obj):
        if isinstance(obj, dict):
            return {k: _walk(v) for k, v in obj.items()}
        if isinstance(obj, list):
            return [_walk(v) for v in obj]
        return _coerce(obj)

    try:
        d = asdict(result)
    except Exception:
        d = {"ecg_id": result.ecg_id, "error": "serialization_failed"}
    return _walk(d)
