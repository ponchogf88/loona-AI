"""Studio timeline — no letter grid, ranges: day / week / quincena / month / year.

Google Calendar (real, opcional): si `runtime/.env` trae
GOOGLE_CALENDAR_ICS_URL (la "dirección secreta en formato iCal" de
Google Calendar → Configuración → tu calendario → Integrar calendario —
NUNCA una API key pegada en chat, es un archivo que Chuy edita él mismo),
se lee y parsea ese feed ICS real en vez del seed de abajo. Sin esa URL,
LOONA cae al seed y lo marca explícitamente como tal (`"source": "seed"`)
para no fingir datos reales. NEED_HUMAN: conseguir esa URL requiere que
Chuy entre a Google Calendar y la copie — no hay forma de automatizarlo
sin credenciales que él mismo debe generar/pegar en el archivo (no en chat).

Limitación conocida: eventos recurrentes (RRULE) del feed real se leen
solo en su primera ocurrencia — expandir recurrencia queda para un
siguiente turno si Chuy confirma que la necesita.
"""
from __future__ import annotations

import os
import time
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

TZ = ZoneInfo("America/Monterrey")

_GOOGLE_CACHE: dict = {"t": 0.0, "events": None}
_GOOGLE_TTL = 300.0  # 5 min — no golpear el feed de Google en cada request


def _fetch_google_events() -> list[dict] | None:
    """Returns real events from GOOGLE_CALENDAR_ICS_URL, or None if not configured/failed."""
    url = os.environ.get("GOOGLE_CALENDAR_ICS_URL", "").strip()
    if not url:
        return None

    now = time.time()
    if _GOOGLE_CACHE["events"] is not None and now - _GOOGLE_CACHE["t"] < _GOOGLE_TTL:
        return _GOOGLE_CACHE["events"]

    try:
        import httpx
        from icalendar import Calendar

        resp = httpx.get(url, timeout=8.0, follow_redirects=True)
        resp.raise_for_status()
        cal = Calendar.from_ical(resp.content)
    except Exception:
        # Feed caído / URL mala / parse error: no tumbar el calendario, caer a seed.
        return _GOOGLE_CACHE["events"]  # último valor bueno conocido (o None)

    window_start = datetime.now(TZ) - timedelta(days=30)
    window_end = datetime.now(TZ) + timedelta(days=180)
    events: list[dict] = []
    for component in cal.walk("VEVENT"):
        dtstart = component.get("dtstart")
        dtend = component.get("dtend")
        summary = component.get("summary")
        if dtstart is None or summary is None:
            continue
        s = dtstart.dt
        e = dtend.dt if dtend is not None else s
        if not isinstance(s, datetime):
            # evento de todo el día (date, no datetime)
            s = datetime.combine(s, datetime.min.time(), tzinfo=TZ)
            e = datetime.combine(e, datetime.min.time(), tzinfo=TZ) if not isinstance(e, datetime) else e
        if s.tzinfo is None:
            s = s.replace(tzinfo=TZ)
        if isinstance(e, datetime) and e.tzinfo is None:
            e = e.replace(tzinfo=TZ)
        elif not isinstance(e, datetime):
            e = s
        if e < window_start or s > window_end:
            continue
        events.append(
            {
                "start": s.astimezone(TZ).replace(tzinfo=None).isoformat(),
                "end": e.astimezone(TZ).replace(tzinfo=None).isoformat(),
                "title": str(summary),
                "kind": "calendar",
            }
        )
    events.sort(key=lambda ev: ev["start"])
    _GOOGLE_CACHE["t"] = now
    _GOOGLE_CACHE["events"] = events
    return events


def _active_events() -> tuple[list[dict], str]:
    """Returns (events, source) — source is 'google_calendar' or 'seed', never silently mixed."""
    google = _fetch_google_events()
    if google is not None:
        return google, "google_calendar"
    return EVENTS, "seed"


# Seed events (fallback honesto si no hay GOOGLE_CALENDAR_ICS_URL). ISO local MTY.
EVENTS = [
    {"start": "2026-08-12T09:00:00", "end": "2026-08-12T11:00:00", "title": "LOONA world view", "kind": "build"},
    {"start": "2026-08-12T13:20:00", "end": "2026-08-12T13:40:00", "title": "Likinya mute live IG/TT/X", "kind": "publish"},
    {"start": "2026-08-13T10:00:00", "end": "2026-08-13T12:00:00", "title": "Stories IG", "kind": "content"},
    {"start": "2026-08-15T16:00:00", "end": "2026-08-15T17:00:00", "title": "Farmasi soft · catálogo", "kind": "biz"},
    {"start": "2026-08-18T09:30:00", "end": "2026-08-18T11:00:00", "title": "Radar X semanal", "kind": "ops"},
    {"start": "2026-08-22T19:00:00", "end": "2026-08-22T20:00:00", "title": "Pack madrugada v2", "kind": "content"},
    {"start": "2026-09-01T09:00:00", "end": "2026-09-01T10:00:00", "title": "Cierre quincena", "kind": "biz"},
    {"start": "2026-12-12T20:00:00", "end": "2026-12-12T21:00:00", "title": "Aniversario LOONA", "kind": "life"},
]


def _parse(s: str) -> datetime:
    return datetime.fromisoformat(s).replace(tzinfo=TZ)


def _window(kind: str, now: datetime) -> tuple[datetime, datetime, str]:
    kind = (kind or "week").lower()
    start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    if kind == "day":
        return start, start + timedelta(days=1), "Hoy"
    if kind == "week":
        monday = start - timedelta(days=start.weekday())
        return monday, monday + timedelta(days=7), "Esta semana"
    if kind in ("quincena", "fortnight"):
        if now.day <= 15:
            a = start.replace(day=1)
            b = start.replace(day=16)
            return a, b, "1–15"
        last = (start.replace(day=28) + timedelta(days=8)).replace(day=1)
        return start.replace(day=16), last, "16–fin"
    if kind == "month":
        nxt = (start.replace(day=28) + timedelta(days=8)).replace(day=1)
        return start.replace(day=1), nxt, start.strftime("%B")
    if kind == "year":
        return start.replace(month=1, day=1), start.replace(year=start.year + 1, month=1, day=1), str(start.year)
    monday = start - timedelta(days=start.weekday())
    return monday, monday + timedelta(days=7), "Esta semana"


def build_timeline(kind: str = "week") -> dict:
    now = datetime.now(TZ)
    a, b, label = _window(kind, now)
    events, source = _active_events()
    rows = []
    for ev in events:
        s = _parse(ev["start"])
        e = _parse(ev["end"])
        if e <= a or s >= b:
            continue
        rows.append(
            {
                "start": s.isoformat(),
                "end": e.isoformat(),
                "title": ev["title"],
                "kind": ev["kind"],
                "when": s.strftime("%d %b · %H:%M"),
                "stamp": s.timestamp(),
            }
        )
    rows.sort(key=lambda r: r["stamp"])
    span = max((b - a).total_seconds(), 1)
    for r in rows:
        s = datetime.fromisoformat(r["start"])
        r["pct"] = max(0.0, min(1.0, (s.timestamp() - a.timestamp()) / span))
        r["now"] = a <= now <= b and abs(s.timestamp() - now.timestamp()) < 3600 * 6
    return {
        "range": kind,
        "label": label,
        "from": a.isoformat(),
        "to": b.isoformat(),
        "now": now.isoformat(),
        "now_pct": max(0.0, min(1.0, (now.timestamp() - a.timestamp()) / span)),
        "items": rows,
        "source": source,
    }


MESES = [
    "enero",
    "febrero",
    "marzo",
    "abril",
    "mayo",
    "junio",
    "julio",
    "agosto",
    "septiembre",
    "octubre",
    "noviembre",
    "diciembre",
]
DIAS = ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"]


def build_month_widget() -> dict:
    now = datetime.now(TZ)
    first = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    nxt = (first.replace(day=28) + timedelta(days=8)).replace(day=1)
    days_in = (nxt - first).days
    lead = first.weekday()
    events, source = _active_events()
    by_day: dict[int, list[str]] = {}
    for ev in events:
        s = _parse(ev["start"])
        if s.year == now.year and s.month == now.month:
            by_day.setdefault(s.day, []).append(ev["title"])

    cells: list[dict] = []
    for _ in range(lead):
        cells.append({"d": None, "today": False, "dots": 0, "titles": []})
    for d in range(1, days_in + 1):
        titles = by_day.get(d, [])
        cells.append(
            {
                "d": d,
                "today": d == now.day,
                "dots": len(titles),
                "titles": titles,
            }
        )

    upcoming = []
    future = []
    for ev in events:
        s = _parse(ev["start"])
        e = _parse(ev["end"])
        if e < now:
            continue
        future.append((s, ev))
    future.sort(key=lambda pair: pair[0])
    for s, ev in future[:3]:
        upcoming.append(
            {
                "title": ev["title"],
                "kind": ev["kind"],
                "when": s.strftime("%d %b · %H:%M"),
                "start": s.isoformat(),
                "today": s.date() == now.date(),
            }
        )

    return {
        "month": MESES[now.month - 1],
        "month_title": f"{MESES[now.month - 1]} {now.year}",
        "year": now.year,
        "dow": ["L", "M", "X", "J", "V", "S", "D"],
        "cells": cells,
        "today": now.day,
        "today_label": f"{DIAS[now.weekday()]} {now.day}",
        "upcoming": upcoming,
        "source": source,
    }
