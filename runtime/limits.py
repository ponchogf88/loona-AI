"""Honest v1 performance envelope: single operator, local/LAN use.

LOONA v1 runs one FastAPI process on one Mac with no auth and no queueing
beyond these soft caps. It is NOT built for many simultaneous strangers —
see ROADMAP.md for multi-seat/auth/hosted plans. These limits exist so a
noisy client (or a study with several testers) degrades gracefully instead
of pegging the CPU or wedging the single Ollama/DeepSeek connection.
"""
from __future__ import annotations

import time
from collections import defaultdict, deque

from fastapi import HTTPException

RATE_LIMIT_WINDOW_SECONDS = 60.0
RATE_LIMIT_MAX_REQUESTS = 40  # per IP per window — matches README.md's published limit
MAX_CONCURRENT_CHATS = 4

_hits: dict[str, deque] = defaultdict(deque)
_inflight_chats = 0


def allow(client_ip: str) -> tuple[bool, str]:
    """Sliding-window rate limit per IP. Returns (ok, reason_if_blocked)."""
    now = time.time()
    window = _hits[client_ip]
    while window and now - window[0] > RATE_LIMIT_WINDOW_SECONDS:
        window.popleft()
    if len(window) >= RATE_LIMIT_MAX_REQUESTS:
        return False, f"rate limit: max {RATE_LIMIT_MAX_REQUESTS} req/min por IP"
    window.append(now)
    return True, ""


class Inflight:
    """`with limits.Inflight():` caps concurrent /api/chat calls at MAX_CONCURRENT_CHATS.

    Raises HTTPException(429) immediately on entry if saturated, instead of
    queueing — a v1 caller should retry, not wait indefinitely behind a
    single Ollama/DeepSeek connection.
    """

    def __enter__(self):
        global _inflight_chats
        if _inflight_chats >= MAX_CONCURRENT_CHATS:
            raise HTTPException(
                status_code=429,
                detail=(
                    f"LOONA ya tiene {MAX_CONCURRENT_CHATS} chats en curso "
                    "(límite v1 single-operator), intenta de nuevo en unos segundos"
                ),
            )
        _inflight_chats += 1
        return self

    def __exit__(self, exc_type, exc, tb):
        global _inflight_chats
        _inflight_chats -= 1
        return False
