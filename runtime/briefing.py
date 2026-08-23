"""Morning briefing: greet + exercise + weather + AI news. Spoken by LOONA."""
from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo

TZ = ZoneInfo("America/Monterrey")

ROUTINES = [
    {
        "name": "fuerza de tren superior",
        "speak": "Tres rondas: lagartijas, remo con banda y plancha de cuarenta segundos.",
    },
    {
        "name": "cardio corto",
        "speak": "Veinte minutos: cinco de calentamiento, diez de intervalos y cinco de bajada.",
    },
    {
        "name": "core y postura",
        "speak": "Dead bug, bird dog y plancha lateral. Diez minutos, sin prisa.",
    },
    {
        "name": "piernas y cadera",
        "speak": "Sentadillas al aire, puentes de glúteo y zancadas. Tres series de doce.",
    },
    {
        "name": "HIIT de escritorio",
        "speak": "Ocho rondas de cuarenta segundos: jumping jacks, mountain climbers y sentadilla. Veinte de descanso.",
    },
    {
        "name": "movilidad",
        "speak": "Cuello, hombros, cadera y gato-camello. Quince minutos para destensar.",
    },
    {
        "name": "día suave",
        "speak": "Caminata de treinta minutos afuera. Sin carga. Solo salir.",
    },
]


def _greet(hour: int) -> str:
    if hour < 12:
        return "Buenos días"
    if hour < 20:
        return "Buenas tardes"
    return "Buenas noches"


async def build_briefing() -> dict:
    from news import fetch_news
    from weather import fetch_weather

    now = datetime.now(TZ)
    greet = _greet(now.hour)
    routine = ROUTINES[now.weekday() % 7]
    weather = await fetch_weather()
    news = await fetch_news(6, topic="ai")
    headlines = [it.get("title") or "" for it in news if it.get("title")][:3]
    parts = [
        f"{greet}, Chuy.",
        f"Hoy te toca {routine['name']}. {routine['speak']}",
        weather.get("speak") or "",
    ]
    if headlines:
        parts.append("Noticias de inteligencia artificial.")
        parts.extend(headlines)
    else:
        parts.append("Hoy no pude sintonizar titulares de inteligencia artificial.")
    speech = " ".join(p.strip() for p in parts if p and p.strip())
    return {
        "ok": True,
        "when": now.isoformat(),
        "greet": greet,
        "routine": routine,
        "weather": weather,
        "news": news,
        "speech": speech,
    }
