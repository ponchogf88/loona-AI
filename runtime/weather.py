"""Monterrey weather via Open-Meteo — no API key."""
from __future__ import annotations

import time

import httpx

LAT = 25.6866
LON = -100.3161
_CACHE: dict = {"t": 0.0, "data": None}
_TTL = 600.0

WMO = {
    0: "cielo despejado",
    1: "mayormente despejado",
    2: "parcialmente nublado",
    3: "nublado",
    45: "niebla",
    48: "niebla helada",
    51: "llovizna ligera",
    53: "llovizna",
    55: "llovizna fuerte",
    61: "lluvia ligera",
    63: "lluvia",
    65: "lluvia fuerte",
    71: "nieve ligera",
    73: "nieve",
    75: "nieve fuerte",
    80: "chubascos",
    81: "chubascos fuertes",
    82: "chubascos intensos",
    95: "tormenta",
    96: "tormenta con granizo",
    99: "tormenta fuerte",
}


def _label(code: int) -> str:
    return WMO.get(int(code), "condiciones mixtas")


async def fetch_weather() -> dict:
    now = time.time()
    if _CACHE["data"] and now - _CACHE["t"] < _TTL:
        return _CACHE["data"]

    url = (
        "https://api.open-meteo.com/v1/forecast"
        f"?latitude={LAT}&longitude={LON}"
        "&current=temperature_2m,weather_code,relative_humidity_2m,wind_speed_10m"
        "&daily=temperature_2m_max,temperature_2m_min,weather_code"
        "&timezone=America%2FMonterrey"
        "&forecast_days=1"
    )
    fallback = {
        "ok": False,
        "city": "Monterrey",
        "temp": None,
        "label": "sin dato",
        "high": None,
        "low": None,
        "humidity": None,
        "wind": None,
        "speak": "No pude leer el clima de Monterrey.",
    }
    try:
        async with httpx.AsyncClient(timeout=6.0) as client:
            r = await client.get(url)
            r.raise_for_status()
            j = r.json()
    except httpx.HTTPError:
        return fallback

    cur = j.get("current") or {}
    daily = j.get("daily") or {}
    temp = cur.get("temperature_2m")
    code = cur.get("weather_code") or 1
    highs = daily.get("temperature_2m_max") or [None]
    lows = daily.get("temperature_2m_min") or [None]
    label = _label(code)
    data = {
        "ok": True,
        "city": "Monterrey",
        "temp": round(temp) if temp is not None else None,
        "label": label,
        "high": round(highs[0]) if highs[0] is not None else None,
        "low": round(lows[0]) if lows[0] is not None else None,
        "humidity": cur.get("relative_humidity_2m"),
        "wind": cur.get("wind_speed_10m"),
        "code": code,
    }
    t = data["temp"]
    hi = data["high"]
    lo = data["low"]
    if t is not None:
        span = ""
        if hi is not None and lo is not None:
            span = f" Máxima {hi}, mínima {lo}."
        data["speak"] = f"En Monterrey hay {t} grados, {label}.{span}"
    else:
        data["speak"] = "No pude leer el clima de Monterrey."
    _CACHE["t"] = now
    _CACHE["data"] = data
    return data
