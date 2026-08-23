"""Opt-in local usage/performance telemetry.

Never phones home. The single source of truth for the opt-in flag is
`config.study.enabled` (see config/loona.schema.json, toggled via
`POST /api/study` or `PUT /api/config`). `runtime/app.py` checks that flag
(`_study_on()`) before calling `record()` — this module does not re-gate,
it just appends. Writes newline-delimited JSON to `runtime/state/usage.jsonl`
(gitignored). See README.md → "Estudio de uso" for how a study exports it.

Eventos documentados (contrato, no forzado en escritura):
session_start, chat, news_open, tts, timeline_range, error
"""
from __future__ import annotations

import json
import time
from pathlib import Path

STATE_DIR = Path(__file__).resolve().parent / "state"
USAGE_LOG_PATH = STATE_DIR / "usage.jsonl"

VALID_EVENTS = {"session_start", "chat", "news_open", "tts", "timeline_range", "error"}

_START_TIME = time.time()


def record_event(event_type: str, data: dict | None = None, latency_ms: float | None = None) -> dict:
    """Append one usage event. Caller is responsible for the opt-in gate."""
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    row = {"ts": time.time(), "type": event_type, "data": data or {}}
    if latency_ms is not None:
        row["latency_ms"] = round(latency_ms, 1)
    with open(USAGE_LOG_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")
    return {"ok": True, "recorded": True}


def _read_events() -> list[dict]:
    if not USAGE_LOG_PATH.exists():
        return []
    rows = []
    with open(USAGE_LOG_PATH, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return rows


def _percentile(values: list[float], pct: float) -> float | None:
    if not values:
        return None
    s = sorted(values)
    k = (len(s) - 1) * pct
    lo = int(k)
    hi = min(lo + 1, len(s) - 1)
    if lo == hi:
        return round(s[lo], 1)
    return round(s[lo] + (s[hi] - s[lo]) * (k - lo), 1)


def compute_metrics() -> dict:
    """Aggregates for GET /api/metrics: latency p50/p95, uptime, counts."""
    rows = _read_events()
    counts: dict[str, int] = {}
    latencies_by_type: dict[str, list[float]] = {}
    for row in rows:
        t = row.get("type", "unknown")
        counts[t] = counts.get(t, 0) + 1
        lat = row.get("latency_ms")
        if isinstance(lat, (int, float)):
            latencies_by_type.setdefault(t, []).append(float(lat))

    latency_stats = {}
    for t in ("chat", "tts"):
        values = latencies_by_type.get(t, [])
        latency_stats[t] = {
            "p50_ms": _percentile(values, 0.5),
            "p95_ms": _percentile(values, 0.95),
            "count": len(values),
        }

    return {
        "uptime_seconds": round(time.time() - _START_TIME, 1),
        "event_counts": counts,
        "total_events": len(rows),
        "latency": latency_stats,
        "usage_log_path": str(USAGE_LOG_PATH),
    }


# aliases matching runtime/app.py's call sites
record = record_event
snapshot = compute_metrics
