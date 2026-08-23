"""Chromecast / Nest Hub discovery and cast — runtime/cast.py

Día 1-2 de docs/PLAN_CASA_APEX.md: el Hub 2 es boca (Cast de TTS), no
receptor de Gemini. Descubre dispositivos Chromecast/Nest en la LAN y
reproduce audio (mp3 de tts.py) en el primero que parezca el Hub.
"""
from __future__ import annotations

import asyncio
from pathlib import Path
from urllib.parse import quote

DISCOVER_TIMEOUT_S = 6


def _pick_target(devices: list[dict]) -> dict | None:
    """Nest/Hub primero; si no hay match por nombre, el primero disponible."""
    for dev in devices:
        haystack = f"{dev.get('name') or ''} {dev.get('model') or ''}".lower()
        if "nest" in haystack or "hub" in haystack:
            return dev
    return devices[0] if devices else None


def discover(timeout: int = DISCOVER_TIMEOUT_S) -> list[dict]:
    """Bloqueante: usa pychromecast.get_chromecasts(). Llamar via to_thread."""
    import pychromecast

    casts, browser = pychromecast.get_chromecasts(timeout=timeout)
    try:
        devices = []
        for cc in casts:
            info = cc.cast_info
            devices.append(
                {
                    "name": info.friendly_name,
                    "uuid": str(info.uuid),
                    "model": info.model_name,
                    "host": info.host,
                }
            )
        return devices
    finally:
        browser.stop_discovery()


def _play_media(device: dict, url: str, mime: str) -> None:
    """Bloqueante: conecta al cast elegido y reproduce una URL que el Hub pueda bajar.

    Debe desconectar el socket_client del Chromecast antes de salir: si no,
    el hilo de reconexión de pychromecast sigue vivo después de que
    stop_discovery() para el zeroconf, y queda reintentando para siempre
    (100% CPU + logs sin fin — visto en producción, server.log llegó a 31GB).
    """
    import pychromecast

    casts, browser = pychromecast.get_chromecasts(timeout=DISCOVER_TIMEOUT_S)
    target = next((cc for cc in casts if str(cc.cast_info.uuid) == device["uuid"]), None)
    try:
        if target is None:
            raise RuntimeError(f"device {device['name']} ya no está en la LAN")
        target.wait(timeout=10)
        mc = target.media_controller
        mc.play_media(url, mime)
        mc.block_until_active(timeout=15)
    finally:
        if target is not None:
            target.disconnect(timeout=5)
        browser.stop_discovery()


def _play_mp3(device: dict, url: str) -> None:
    _play_media(device, url, "audio/mpeg")


async def list_devices() -> dict:
    devices = await asyncio.to_thread(discover)
    if not devices:
        return {"ok": False, "hint": "Hub en la misma Wi-Fi", "devices": []}
    return {"ok": True, "devices": devices}


async def cast_tts(text: str, tts_url_base: str | None = None) -> dict:
    """Sintetiza con tts.py y reproduce en el Nest Hub. URL debe ser LAN, no 127.0.0.1."""
    from tts import synthesize
    import media_lan

    path: Path = await synthesize(text)
    devices = await asyncio.to_thread(discover)
    target = _pick_target(devices)
    if target is None:
        return {"ok": False, "hint": "Hub en la misma Wi-Fi", "devices": []}

    url = media_lan.url_for(path)
    try:
        await asyncio.to_thread(_play_mp3, target, url)
    except Exception as exc:
        return {"ok": False, "error": str(exc), "device": target}
    return {"ok": True, "device": target, "file": path.name, "url": url}


async def speak_and_card(text: str) -> dict:
    """Voz + tarjeta en un solo beat: card (lockup + frase + clima) muxeada con
    el mp3 de Dalia a un mp4, y un solo cast. Si solo se casteara la imagen,
    el play_media patearía el audio; el mux los mantiene juntos. Un shot, no loop.
    """
    from tts import synthesize
    import card
    import eyes
    import media_lan
    from weather import fetch_weather

    mp3 = await synthesize(text)
    w = await fetch_weather()
    devices = await asyncio.to_thread(discover)
    target = _pick_target(devices)
    if target is None:
        return {"ok": False, "hint": "Hub en la misma Wi-Fi", "devices": []}
    jpg = await asyncio.to_thread(card.build_card, text, w)
    mp4 = await asyncio.to_thread(eyes.mux_still_audio, jpg, mp3)
    url = media_lan.url_for(mp4)
    try:
        await asyncio.to_thread(_play_media, target, url, "video/mp4")
    except Exception as exc:
        return {"ok": False, "error": str(exc), "device": target, "file": mp4.name}
    return {
        "ok": True,
        "device": target,
        "card": jpg.name,
        "file": mp4.name,
        "url": url,
        "text": text,
        "weather": w.get("speak"),
    }


async def cast_card(text: str | None = None) -> dict:
    """Tarjeta (lockup + texto corto + clima) en el Nest Hub. Un beat, no loop."""
    import card
    import media_lan
    from weather import fetch_weather

    w = await fetch_weather()
    devices = await asyncio.to_thread(discover)
    target = _pick_target(devices)
    if target is None:
        return {"ok": False, "hint": "Hub en la misma Wi-Fi", "devices": []}
    jpg = await asyncio.to_thread(card.build_card, text or "Estoy aquí, en la Choza.", w)
    url = media_lan.url_for(jpg)
    try:
        await asyncio.to_thread(_play_media, target, url, "image/jpeg")
    except Exception as exc:
        return {"ok": False, "error": str(exc), "device": target, "file": jpg.name}
    return {
        "ok": True,
        "device": target,
        "file": jpg.name,
        "url": url,
        "text": text,
        "weather": w.get("speak"),
    }


async def cast_amigo(text: str) -> dict:
    """Cámara del iMac + voz Dalia en el Nest Hub (Choza). Un beat, no loop."""
    from tts import synthesize
    import eyes
    import media_lan

    jpg = await asyncio.to_thread(eyes.snap_desktop)
    mp3 = await synthesize(text)
    mp4 = await asyncio.to_thread(eyes.mux_still_audio, jpg, mp3)
    devices = await asyncio.to_thread(discover)
    target = _pick_target(devices)
    if target is None:
        return {
            "ok": False,
            "hint": "Hub en la misma Wi-Fi",
            "devices": [],
            "snap": jpg.name,
        }
    url = media_lan.url_for(mp4)
    try:
        await asyncio.to_thread(_play_media, target, url, "video/mp4")
    except Exception as exc:
        return {"ok": False, "error": str(exc), "device": target, "snap": jpg.name}
    return {
        "ok": True,
        "device": target,
        "snap": jpg.name,
        "file": mp4.name,
        "url": url,
        "text": text,
    }
