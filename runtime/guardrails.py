"""Text guardrails for LOONA — blocks secret-reading and publish/destructive intents.

Applies to inbound chat text per docs/GOVERNANCE.md guardrails and identity/SOUL.md "Nunca".
"""
import re

_SECRET_PATTERNS = [
    r"\.env\b",
    r"\bapi[\s_-]?key(s)?\b",
    r"\bllavero\b",
    r"\bkeychain\b",
    r"\bcredencial(es)?\b",
    r"\bsecret(s)?\b",
    r"\btoken(s)?\s+de\s+acceso\b",
]

_PUBLISH_PATTERNS = [
    r"\bpublica(r)?\b.*\b(instagram|tiktok|twitter|\bx\b)\b",
    r"\bpost(ea|ear)?\b.*\b(instagram|tiktok|twitter|\bx\b)\b",
    r"\bpublish\b.*\b(instagram|tiktok|twitter|\bx\b)\b",
    r"\bsube(lo)?\b.*\b(instagram|tiktok|twitter|\bx\b)\b",
    r"\bpost to\b.*\b(instagram|tiktok|twitter|x)\b",
]

_DESTRUCTIVE_PATTERNS = [
    r"rm\s+-rf",
    r"\bformat(ea)?\b.*disco",
    r"\bdrop\s+table\b",
    r"\bdelete\s+from\b.*\bwhere\s+1\s*=\s*1\b",
]

_ALL = [
    ("secret_read", _SECRET_PATTERNS),
    ("publish", _PUBLISH_PATTERNS),
    ("destructive", _DESTRUCTIVE_PATTERNS),
]

_COMPILED = [
    (label, [re.compile(p, re.IGNORECASE) for p in patterns])
    for label, patterns in _ALL
]


def check_text(text: str) -> tuple[bool, str | None, str | None]:
    """Returns (blocked, reason_label, matched_pattern)."""
    if not text:
        return False, None, None
    for label, patterns in _COMPILED:
        for pattern in patterns:
            if pattern.search(text):
                return True, label, pattern.pattern
    return False, None, None
