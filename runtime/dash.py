"""Life dashboards — health / finance / exercise.

Producto (docs/PRODUCT_LOONA.md, .grok/skills/loona-ops "Nunca"): jamás
inventar saldos, peso o números personales de Chuy. Cada campo aquí es o
bien un valor real determinista (la rutina del día, timestamps) o un
placeholder explícito `{"value": null, "placeholder": true}` hasta que
exista una fuente de datos real conectada — ver "note" en cada dashboard
para el NEED_HUMAN puntual de esa sección.
"""
from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo

TZ = ZoneInfo("America/Monterrey")


def _placeholder(**extra) -> dict:
    return {"value": None, "placeholder": True, **extra}


def health_dashboard() -> dict:
    return {
        "ok": True,
        "source": "placeholder",
        "updated": None,
        "metrics": {
            "weight_kg": _placeholder(),
            "sleep_hours_avg": _placeholder(),
            "resting_hr_bpm": _placeholder(),
            "steps_today": _placeholder(),
            "water_l_today": _placeholder(),
            "mood_1_5": _placeholder(),
        },
        "note": (
            "NEED_HUMAN: sin fuente de salud conectada (Apple Health, báscula, "
            "wearable). Ningún valor de esta sección es real todavía."
        ),
    }


def finance_dashboard() -> dict:
    return {
        "ok": True,
        "source": "placeholder",
        "updated": None,
        "currency": "MXN",
        "metrics": {
            "balance_total": _placeholder(),
            "income_month": _placeholder(),
            "expenses_month": _placeholder(),
            "savings_rate_pct": _placeholder(),
            "biz_revenue_month": _placeholder(label="Farmasi / negocio"),
        },
        "note": (
            "NEED_HUMAN: cero acceso a cuentas bancarias o Farmasi. No se "
            "inventan saldos — falta decidir la fuente (entrada manual en el "
            "HUD, export CSV, o API del banco) antes de mostrar números reales."
        ),
    }


def exercise_dashboard() -> dict:
    from briefing import ROUTINES

    now = datetime.now(TZ)
    todays_routine = ROUTINES[now.weekday() % 7]
    return {
        "ok": True,
        "source": "seed",
        "updated": now.isoformat(),
        "today": {"name": todays_routine["name"], "plan": todays_routine["speak"]},
        "metrics": {
            "streak_days": _placeholder(),
            "sessions_week": _placeholder(),
            "minutes_week": _placeholder(),
            "last_completed": _placeholder(),
        },
        "note": (
            "La rutina del día es real (misma rotación semanal que usa el "
            "briefing). Las métricas de cumplimiento son placeholder — "
            "NEED_HUMAN: no hay log de entrenamientos todavía (¿check-in "
            "manual en el HUD? ¿Apple Health?)."
        ),
    }
