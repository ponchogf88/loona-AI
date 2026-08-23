"""Desktop camera snap — FaceTime HD. Not Eufy. Not a surveillance loop."""
from __future__ import annotations

import shutil
import subprocess
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

CAPTURES = Path(__file__).resolve().parent / "state" / "captures"
FFMPEG = shutil.which("ffmpeg") or "/Library/Frameworks/Python.framework/Versions/3.12/bin/ffmpeg"
# AVFoundation: [1] FaceTime HD Camera (Built-in)
DEVICE = "1:"


def status() -> dict:
    import eufy

    return {
        "ok": True,
        "desktop": {
            "src": "desktop",
            "device": "FaceTime HD Camera (Built-in)",
            "ffmpeg": Path(FFMPEG).exists(),
        },
        "eufy": eufy.status(),
    }


def snap_desktop() -> Path:
    """One JPEG from the iMac camera. Caller decides whether to show it."""
    if not Path(FFMPEG).exists():
        raise RuntimeError("ffmpeg no está")
    CAPTURES.mkdir(parents=True, exist_ok=True)
    name = datetime.now(ZoneInfo("America/Monterrey")).strftime("%Y%m%d-%H%M%S") + "-face.jpg"
    dest = CAPTURES / name
    cmd = [
        FFMPEG,
        "-y",
        "-hide_banner",
        "-loglevel",
        "error",
        "-f",
        "avfoundation",
        "-framerate",
        "29.97",
        "-video_size",
        "1280x720",
        "-i",
        DEVICE,
        "-frames:v",
        "1",
        "-update",
        "1",
        "-q:v",
        "3",
        str(dest),
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=20)
    if proc.returncode != 0 or not dest.exists() or dest.stat().st_size < 2000:
        raise RuntimeError((proc.stderr or proc.stdout or "snap vacío").strip()[:400])
    return dest


def snap_eufy() -> Path:
    """1 frame de la Eufy vía ffmpeg. Solo si EUFY_RTSP_URL está en env."""
    import eufy

    return eufy.snap_from_rtsp()


def mux_still_audio(jpg: Path, mp3: Path) -> Path:
    """H264+AAC still+voice so the Hub keeps the face while Dalia habla."""
    dest = jpg.with_suffix(".mp4")
    cmd = [
        FFMPEG,
        "-y",
        "-hide_banner",
        "-loglevel",
        "error",
        "-loop",
        "1",
        "-i",
        str(jpg),
        "-i",
        str(mp3),
        "-c:v",
        "libx264",
        "-tune",
        "stillimage",
        "-pix_fmt",
        "yuv420p",
        "-vf",
        "scale=1280:720",
        "-c:a",
        "aac",
        "-b:a",
        "128k",
        "-shortest",
        "-movflags",
        "+faststart",
        str(dest),
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    if proc.returncode != 0 or not dest.exists() or dest.stat().st_size < 4000:
        raise RuntimeError((proc.stderr or proc.stdout or "mux vacío").strip()[:400])
    return dest
