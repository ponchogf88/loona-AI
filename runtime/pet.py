"""LOONA mascota — intenciones de casa. No ruedas. No vigilancia 24/7."""
from __future__ import annotations

import os
import re

LIGHT_ON = re.compile(r"\b(prende|enciende|prendele|pon)\b.*\b(luz|foco|spotlight|linterna)\b", re.I)
LIGHT_OFF = re.compile(r"\b(apaga|apagale|quita)\b.*\b(luz|foco|spotlight)\b", re.I)
SEE = re.compile(r"\b(qu[eé]\s+ves|mira|oye|estoy\s+aqu[ií])\b", re.I)


def eufy_ready() -> dict:
    has_rtsp = bool(os.environ.get("EUFY_RTSP_URL"))
    has_account = bool(os.environ.get("EUFY_EMAIL") and os.environ.get("EUFY_PASSWORD"))
    # La librería instalada (pyeufysecurity) solo lee la cuenta cloud; no
    # expone el protocolo P2P propietario que manda el comando de luz. Con
    # o sin cuenta, prender/apagar sigue siendo NEED_HUMAN — ver eufy.spotlight().
    return {
        "model": "T8417",
        "role": "ojo + luz",
        "rtsp_configured": has_rtsp,
        "account_configured": has_account,
        "light": "NEED_HUMAN",
        "hint": (
            "Cuenta lista, pero pyeufysecurity no expone control de luz/spotlight "
            "(solo lectura vía cloud API). Falta un cliente P2P real (eufy-security-ws "
            "o equivalente) para mandar el comando."
            if has_account
            else "Luz y tracking nativo ya los tiene el hardware. Para que LOONA la prenda: cuenta eufy en runtime/.env (EUFY_EMAIL + EUFY_PASSWORD). RTSP/NAS aparte, sin pegar URL en chat."
        ),
    }


def body() -> dict:
    eufy = eufy_ready()
    return {
        "ok": True,
        "alive": True,
        "boca": "Nest Hub 2 Choza",
        "ojo_desktop": "FaceTime iMac",
        "ojo_eufy": eufy,
        "luz": eufy["light"],
        "hud": "Apex / presencia",
        "ruedas": "después",
        "voice": "es-MX-DaliaNeural",
    }


def parse(text: str) -> str:
    t = (text or "").strip()
    if LIGHT_ON.search(t):
        return "light_on"
    if LIGHT_OFF.search(t):
        return "light_off"
    if SEE.search(t):
        return "see"
    return "talk"


def light_reply(on: bool) -> tuple[str, dict]:
    eufy = eufy_ready()
    if eufy["light"] != "ready":
        said = (
            "Tu cuenta eufy ya está puesta, pero la librería solo lee la nube: no trae "
            "el mando de la luz. Falta un cliente P2P real; mientras, el interruptor "
            "sigue en la app."
            if on and eufy["account_configured"]
            else (
                "La luz de la Eufy ya está ahí, potente. Pon la cuenta en el .env "
                "y sigo buscando el mando."
                if on
                else "Todavía no puedo apagarla yo. El mando de la luz sigue en la app, un momento."
            )
        )
        return said, {"ok": False, "intent": "light_on" if on else "light_off", "eufy": eufy}
    said = "Prendo la luz." if on else "Apago la luz."
    return said, {"ok": True, "intent": "light_on" if on else "light_off", "eufy": eufy, "acted": False, "hint": "Claude cablea eufy-security; no fingir el P2P."}
