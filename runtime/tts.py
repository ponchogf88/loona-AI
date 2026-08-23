"""Neural TTS — Microsoft Edge voices, not the browser robot."""
from __future__ import annotations

import hashlib
from pathlib import Path

CACHE = Path(__file__).resolve().parent / "state" / "tts"
VOICE = "es-MX-DaliaNeural"


def cache_path(text: str) -> Path:
    CACHE.mkdir(parents=True, exist_ok=True)
    digest = hashlib.sha256(f"{VOICE}:{text}".encode("utf-8")).hexdigest()[:24]
    return CACHE / f"{digest}.mp3"


async def synthesize(text: str) -> Path:
    import edge_tts

    clean = " ".join((text or "").split())[:500]
    if not clean:
        raise ValueError("empty")
    dest = cache_path(clean)
    if dest.exists() and dest.stat().st_size > 200:
        return dest
    comm = edge_tts.Communicate(clean, VOICE, rate="-4%", pitch="-2Hz")
    await comm.save(str(dest))
    return dest
