"""Tarjeta para el Nest Hub — lockup + texto corto + clima. Un beat, no loop.

Día 6 de docs/PLAN_CASA_APEX.md: la Choza muestra una tarjeta estática
(marca + lo que LOONA dice + clima de Monterrey). Compone con ffmpeg
drawtext sobre brand/lockup.png y deja el .jpg en state/captures para
que media_lan lo sirva en la LAN.
"""
from __future__ import annotations

import subprocess
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

BRAND_LOCKUP = Path(__file__).resolve().parent.parent / "brand" / "lockup.png"
FONT = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
GOLD = "0xE8D5A3"
CAPTURES = Path(__file__).resolve().parent / "state" / "captures"

MAX_TEXT = 48


def _dt_escape(text: str) -> str:
    return text.replace("\\", "\\\\").replace(":", "\\:").replace("'", "\\'").replace(",", "\\,")


def _drawtext(text: str, y: int, size: int) -> str:
    return (
        f"drawtext=fontfile='{FONT}':text='{_dt_escape(text)}':"
        f"fontcolor={GOLD}:fontsize={size}:x=(w-text_w)/2:y={y}:"
        f"box=1:boxcolor=0x000000@0.55:boxborderw=16"
    )


def _weather_line(w: dict) -> str:
    t, hi, lo = w.get("temp"), w.get("high"), w.get("low")
    if t is None:
        return "Monterrey · sin dato de clima"
    span = f" · máx {hi} / mín {lo}" if hi is not None and lo is not None else ""
    return f"Monterrey · {t}° · {w.get('label', 'sin dato')}{span}"[:72]


def build_card(text: str, weather: dict) -> Path:
    """Compone lockup + texto + clima y devuelve el .jpg guardado en captures."""
    CAPTURES.mkdir(parents=True, exist_ok=True)
    name = datetime.now(ZoneInfo("America/Monterrey")).strftime("card-%Y%m%d-%H%M%S.jpg")
    out = CAPTURES / name
    raw = (text or "Estoy aquí, en la Choza.").strip()
    line = raw if len(raw) <= MAX_TEXT else raw[: MAX_TEXT - 1] + "…"
    vf = f"scale=1280:720,{_drawtext(line, 540, 38)},{_drawtext(_weather_line(weather), 620, 30)}"
    cmd = [
        "ffmpeg", "-y", "-loglevel", "error",
        "-i", str(BRAND_LOCKUP),
        "-vf", vf,
        "-q:v", "3",
        str(out),
    ]
    subprocess.run(cmd, check=True, timeout=30)
    return out
