"""Eufy T8417 Indoor Cam E30 — cuenta cloud honesta, sin fingir P2P.

eufy_security (paquete pip: pyeufysecurity) solo expone lectura de cuenta:
listar cámaras, imagen de evento, y arrancar/parar stream (cloud o RTSP local
si ya tienes esas credenciales). NO expone comandos de luz/spotlight — eso
vive en el protocolo P2P propietario (lo que sí habla eufy-security-client/
eufy-security-ws en Node, o la app oficial). Como aquí no hay cliente P2P
real, /spotlight siempre contesta NEED_HUMAN. No se inventa un comando que
no existe en la librería instalada.
"""
from __future__ import annotations

import os
import shutil
import subprocess
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

CAPTURES = Path(__file__).resolve().parent / "state" / "captures"
FFMPEG = shutil.which("ffmpeg") or "/Library/Frameworks/Python.framework/Versions/3.12/bin/ffmpeg"
MODEL = "T8417"


def account_configured() -> bool:
    return bool(os.environ.get("EUFY_EMAIL") and os.environ.get("EUFY_PASSWORD"))


def rtsp_configured() -> bool:
    return bool(os.environ.get("EUFY_RTSP_URL"))


def status() -> dict:
    return {
        "model": MODEL,
        "role": "ojo + luz",
        "account_configured": account_configured(),
        "rtsp_configured": rtsp_configured(),
        "library": "eufy_security (pyeufysecurity) — solo lectura de cuenta, sin comandos P2P",
        "hint": None
        if account_configured()
        else "Falta EUFY_EMAIL + EUFY_PASSWORD en runtime/.env para la cuenta.",
    }


async def spotlight(on: bool) -> dict:
    """Prender/apagar la luz de la Eufy.

    Honesto: ninguna combinación de env vars activa esto hoy. La librería
    instalada (eufy_security) no tiene un método de control de luz — solo
    lee info de cámara y arranca/para stream. Falta un cliente P2P real.
    """
    if not account_configured():
        return {
            "ok": False,
            "state": "NEED_HUMAN",
            "reason": "faltan EUFY_EMAIL + EUFY_PASSWORD en runtime/.env",
        }
    return {
        "ok": False,
        "state": "NEED_HUMAN",
        "reason": (
            "cuenta configurada, pero eufy_security no expone control de "
            "luz/spotlight (solo lectura vía cloud API). Falta un cliente "
            "P2P real (eufy-security-ws o equivalente) para mandar el comando."
        ),
    }


def snap_from_rtsp() -> Path:
    """1 frame vía ffmpeg desde EUFY_RTSP_URL. Nunca imprime la URL ni la loguea."""
    url = os.environ.get("EUFY_RTSP_URL")
    if not url:
        raise RuntimeError("NEED_HUMAN: falta EUFY_RTSP_URL en runtime/.env")
    if not Path(FFMPEG).exists():
        raise RuntimeError("ffmpeg no está")
    CAPTURES.mkdir(parents=True, exist_ok=True)
    name = datetime.now(ZoneInfo("America/Monterrey")).strftime("%Y%m%d-%H%M%S") + "-eufy.jpg"
    dest = CAPTURES / name
    cmd = [
        FFMPEG,
        "-y",
        "-hide_banner",
        "-loglevel",
        "error",
        "-rtsp_transport",
        "tcp",
        "-i",
        url,
        "-frames:v",
        "1",
        "-q:v",
        "3",
        str(dest),
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=20)
    if proc.returncode != 0 or not dest.exists() or dest.stat().st_size < 2000:
        detail = (proc.stderr or proc.stdout or "snap vacío").strip()[:400]
        raise RuntimeError(detail.replace(url, "***"))
    return dest
