"""LOONA control plane — runtime/app.py

FastAPI server: serves hud/ as static, exposes health/config/knowledge/chat,
and enforces guardrails on inbound text. Binds 127.0.0.1 only.
"""
import copy
import json
from pathlib import Path

import jsonschema
from fastapi import FastAPI, HTTPException, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

import time

import cast
import guardrails
import limits
import providers
import telemetry

ROOT = Path(__file__).resolve().parent.parent
CONFIG_SCHEMA_PATH = ROOT / "config" / "loona.schema.json"
CONFIG_DEFAULT_PATH = ROOT / "config" / "loona.default.json"
CONFIG_STATE_PATH = Path(__file__).resolve().parent / "state" / "config.json"
SOUL_PATH = ROOT / "identity" / "SOUL.md"
MEMORY_PATH = ROOT / "identity" / "MEMORY.md"
HUD_DIR = ROOT / "hud"

app = FastAPI(title="LOONA runtime")


def _load_schema() -> dict:
    with open(CONFIG_SCHEMA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def _load_default_config() -> dict:
    with open(CONFIG_DEFAULT_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def _load_effective_config() -> dict:
    """runtime-persisted overrides win over config/loona.default.json."""
    if CONFIG_STATE_PATH.exists():
        with open(CONFIG_STATE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return _load_default_config()


def _deep_merge(base: dict, patch: dict) -> dict:
    result = copy.deepcopy(base)
    for key, value in patch.items():
        if isinstance(value, dict) and isinstance(result.get(key), dict):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = value
    return result


def _save_state_config(cfg: dict) -> None:
    CONFIG_STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_STATE_PATH, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2, ensure_ascii=False)
        f.write("\n")


@app.middleware("http")
async def guardrail_middleware(request: Request, call_next):
    if request.method in ("POST", "PUT") and request.url.path.startswith("/api/"):
        body_bytes = await request.body()
        try:
            text_to_check = body_bytes.decode("utf-8", errors="ignore")
        except Exception:
            text_to_check = ""

        blocked, reason, pattern = guardrails.check_text(text_to_check)
        if blocked:
            return JSONResponse(
                status_code=403,
                content={
                    "ok": False,
                    "error": "guardrail_blocked",
                    "reason": reason,
                    "detail": "Esta acción requiere NEED_HUMAN o está prohibida por identity/SOUL.md.",
                },
            )

        async def receive():
            return {"type": "http.request", "body": body_bytes, "more_body": False}

        request = Request(request.scope, receive)

    return await call_next(request)


def _study_on() -> bool:
    return bool(_load_effective_config().get("study", {}).get("enabled"))


@app.get("/api/health")
async def health():
    return {"ok": True, "name": "LOONA", "study": _study_on()}


@app.get("/api/metrics")
async def metrics():
    return {"ok": True, "study_enabled": _study_on(), **telemetry.snapshot()}


class StudyEvent(BaseModel):
    name: str
    meta: dict | None = None
    latency_ms: float | None = None


@app.post("/api/event")
async def study_event(ev: StudyEvent, request: Request):
    if not _study_on():
        return {"ok": True, "recorded": False}
    telemetry.record(ev.name, ev.meta, ev.latency_ms)
    return {"ok": True, "recorded": True}


@app.get("/api/study")
async def get_study():
    return {"ok": True, "enabled": _study_on()}


class StudyToggle(BaseModel):
    enabled: bool


@app.post("/api/study")
async def post_study(toggle: StudyToggle):
    schema = _load_schema()
    current = _load_effective_config()
    merged = _deep_merge(current, {"study": {"enabled": toggle.enabled}})
    try:
        jsonschema.validate(merged, schema)
    except jsonschema.ValidationError as exc:
        raise HTTPException(status_code=422, detail=f"config validation failed: {exc.message}")
    _save_state_config(merged)
    return {"ok": True, "enabled": merged["study"]["enabled"]}


@app.get("/api/config")
async def get_config():
    cfg = _load_effective_config()
    schema = _load_schema()
    try:
        jsonschema.validate(cfg, schema)
    except jsonschema.ValidationError as exc:
        raise HTTPException(status_code=500, detail=f"config invalid against schema: {exc.message}")
    return cfg


class ConfigPatch(BaseModel):
    model_config = {"extra": "allow"}


@app.put("/api/config")
async def put_config(patch: ConfigPatch):
    schema = _load_schema()
    current = _load_effective_config()
    merged = _deep_merge(current, patch.model_dump(exclude_none=False))
    try:
        jsonschema.validate(merged, schema)
    except jsonschema.ValidationError as exc:
        raise HTTPException(status_code=422, detail=f"config validation failed: {exc.message}")
    _save_state_config(merged)
    return merged


@app.get("/api/knowledge")
async def knowledge():
    soul = SOUL_PATH.read_text(encoding="utf-8") if SOUL_PATH.exists() else ""
    memory = MEMORY_PATH.read_text(encoding="utf-8") if MEMORY_PATH.exists() else ""
    return {
        "soul": soul,
        "memory": memory,
        "memory_available": MEMORY_PATH.exists(),
    }


class ChatRequest(BaseModel):
    # hud/js/world.js envía {"message": ...}; se acepta también "text" por el
    # contrato original ({text} -> {reply}).
    text: str | None = None
    message: str | None = None

    def resolved_text(self) -> str:
        value = self.message if self.message is not None else self.text
        if not value:
            raise HTTPException(status_code=422, detail="'message' (o 'text') es requerido")
        return value


def _system_prompt() -> str:
    soul = SOUL_PATH.read_text(encoding="utf-8") if SOUL_PATH.exists() else ""
    return (
        "Eres LOONA. Responde en el personaje descrito abajo; nunca digas que eres "
        "otra cosa (ej. el grupo de K-pop) ni un chatbot genérico.\n\n" + soul
    )


@app.post("/api/chat")
async def chat(req: ChatRequest, request: Request):
    text = req.resolved_text()
    ip = request.client.host if request.client else "local"
    ok, why = limits.allow(ip)
    if not ok:
        raise HTTPException(status_code=429, detail=why)
    cfg = _load_effective_config()
    brain = cfg.get("brain", {})
    t0 = time.perf_counter()
    with limits.Inflight():
        result = await providers.get_reply(
            text,
            ollama_model=brain.get("model", providers.OLLAMA_MODEL),
            system_prompt=_system_prompt(),
            brain=brain,
        )
    ms = (time.perf_counter() - t0) * 1000
    if _study_on():
        telemetry.record("chat", {"provider": result.get("provider")}, ms)
    if result.get("reply") is None:
        raise HTTPException(
            status_code=503,
            detail=f"no brain available: {result.get('error', 'unknown')}",
        )
    speak = " ".join(result["reply"].split())[:220]
    try:
        import asyncio

        asyncio.create_task(cast.speak_and_card(speak))
    except Exception:
        pass
    return {"reply": result["reply"], "provider": result["provider"], "spoke": True}


@app.get("/api/news")
async def news(topic: str | None = None):
    from news import fetch_news

    items = await fetch_news(8, topic=topic)
    return {"ok": True, "topic": topic or "general", "items": items}


@app.get("/api/weather")
async def weather():
    from weather import fetch_weather

    return await fetch_weather()


@app.get("/api/briefing")
async def briefing():
    from briefing import build_briefing

    return await build_briefing()


@app.get("/api/calendar")
async def calendar():
    from calendar_data import build_month_widget

    return build_month_widget()


@app.get("/api/dash/health")
async def dash_health():
    from dash import health_dashboard

    return health_dashboard()


@app.get("/api/dash/finance")
async def dash_finance():
    from dash import finance_dashboard

    return finance_dashboard()


@app.get("/api/dash/exercise")
async def dash_exercise():
    from dash import exercise_dashboard

    return exercise_dashboard()


@app.get("/api/tts")
async def tts(text: str = ""):
    from fastapi.responses import FileResponse

    from tts import synthesize

    if not text.strip():
        raise HTTPException(status_code=422, detail="text required")
    t0 = time.perf_counter()
    try:
        path = await synthesize(text)
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"tts failed: {exc}") from exc
    if _study_on():
        telemetry.record("tts", {}, (time.perf_counter() - t0) * 1000)
    return FileResponse(path, media_type="audio/mpeg")


@app.get("/api/devices")
async def devices():
    return await cast.list_devices()


class CastTtsRequest(BaseModel):
    text: str


class AmigoRequest(BaseModel):
    text: str = "Hola. Ya te veo. Estoy aquí, en la Choza."


class CardRequest(BaseModel):
    text: str | None = None


@app.post("/api/cast/card")
async def cast_card_endpoint(req: CardRequest):
    """Día 6: tarjeta en la Choza — lockup + texto corto + clima. Un beat, no loop."""
    t0 = time.perf_counter()
    result = await cast.cast_card(req.text)
    if _study_on():
        telemetry.record("cast_card", {"ok": result.get("ok")}, (time.perf_counter() - t0) * 1000)
    return result


@app.post("/api/cast/tts")
async def cast_tts_endpoint(req: CastTtsRequest, request: Request):
    if not req.text.strip():
        raise HTTPException(status_code=422, detail="text required")
    t0 = time.perf_counter()
    result = await cast.cast_tts(req.text)
    if _study_on():
        telemetry.record("cast_tts", {"ok": result.get("ok")}, (time.perf_counter() - t0) * 1000)
    return result


@app.get("/api/eyes/status")
async def eyes_status():
    import eyes

    return eyes.status()


@app.get("/api/eyes/snap")
async def eyes_snap(src: str = "desktop"):
    import eufy
    import eyes

    if src == "desktop":
        try:
            path = eyes.snap_desktop()
        except Exception as exc:
            raise HTTPException(status_code=503, detail=str(exc)) from exc
        return {"ok": True, "src": "desktop", "name": path.name, "bytes": path.stat().st_size}

    if src == "eufy":
        if not eufy.rtsp_configured():
            raise HTTPException(
                status_code=501,
                detail="NEED_HUMAN: falta EUFY_RTSP_URL en runtime/.env",
            )
        try:
            path = eyes.snap_eufy()
        except Exception as exc:
            raise HTTPException(status_code=503, detail=str(exc)) from exc
        return {"ok": True, "src": "eufy", "name": path.name, "bytes": path.stat().st_size}

    raise HTTPException(status_code=422, detail="src debe ser 'desktop' o 'eufy'")


@app.post("/api/amigo")
async def amigo(req: AmigoRequest):
    """Un beat de presencia: te ve la cámara del iMac y te habla en el Nest Hub."""
    t0 = time.perf_counter()
    result = await cast.cast_amigo(req.text.strip() or AmigoRequest().text)
    if _study_on():
        telemetry.record("amigo", {"ok": result.get("ok")}, (time.perf_counter() - t0) * 1000)
    return result


@app.get("/api/viva")
async def viva():
    import pet

    return pet.body()


class PetRequest(BaseModel):
    text: str = "hola"


@app.post("/api/pet")
async def pet_command(req: PetRequest):
    """Mascota de casa: luz Eufy (cuando haya mando), mirada, o charla con voz en la Choza."""
    import pet

    intent = pet.parse(req.text)
    if intent in ("light_on", "light_off"):
        said, extra = pet.light_reply(intent == "light_on")
        spoken = await cast.speak_and_card(said)
        return {"ok": True, "intent": intent, "said": said, "spoke": spoken, **extra}
    if intent == "see":
        said = "Te estoy viendo. La Eufy te sigue solita; yo te hablo desde la Choza."
        result = await cast.cast_amigo(said)
        return {"ok": True, "intent": intent, "said": said, "amigo": result}
    cfg = _load_effective_config()
    brain = cfg.get("brain", {})
    result = await providers.get_reply(
        req.text,
        ollama_model=brain.get("model", providers.OLLAMA_MODEL),
        system_prompt=_system_prompt(),
        brain=brain,
    )
    if result.get("reply") is None:
        raise HTTPException(status_code=503, detail=f"no brain available: {result.get('error', 'unknown')}")
    speak = " ".join(result["reply"].split())[:220]
    try:
        import asyncio

        asyncio.create_task(cast.speak_and_card(speak))
    except Exception:
        pass
    return {"ok": True, "intent": "talk", "said": speak, "provider": result["provider"], "spoke": True}


class PetLightRequest(BaseModel):
    on: bool


@app.post("/api/pet/light")
async def pet_light(req: PetLightRequest):
    """Prender/apagar la luz de la Eufy. Nunca truena: sin cuenta/librería P2P, contesta NEED_HUMAN."""
    import eufy

    result = await eufy.spotlight(req.on)
    return {"on": req.on, **result}


@app.get("/api/timeline")
async def timeline(range: str = "week"):
    from calendar_data import build_timeline

    return build_timeline(range)


@app.post("/api/capture")
async def capture(request: Request):
    from datetime import datetime
    from zoneinfo import ZoneInfo

    form = await request.form()
    upload = form.get("file")
    kind = str(form.get("kind") or "photo")
    if upload is None:
        raise HTTPException(status_code=422, detail="file required")
    raw = await upload.read()
    if not raw:
        raise HTTPException(status_code=422, detail="empty file")
    dest_dir = Path(__file__).resolve().parent / "state" / "captures"
    dest_dir.mkdir(parents=True, exist_ok=True)
    ext = "jpg" if kind == "photo" else "webm"
    name = datetime.now(ZoneInfo("America/Monterrey")).strftime("%Y%m%d-%H%M%S") + "." + ext
    path = dest_dir / name
    path.write_bytes(raw)
    if _study_on():
        telemetry.record("capture", {"kind": kind, "bytes": len(raw)})
    return {"ok": True, "kind": kind, "name": name, "path": str(path), "bytes": len(raw)}


@app.get("/api/telegram/status")
async def telegram_status():
    import os

    token = os.environ.get("TELEGRAM_BOT_TOKEN", "")
    return {
        "ok": True,
        "configured": bool(token),
        "hint": None
        if token
        else "Pon TELEGRAM_BOT_TOKEN en runtime/.env (BotFather) y reinicia loona-up.sh",
    }


@app.websocket("/api/live/ws")
async def live_ws_endpoint(websocket: WebSocket, voice: str = "Aoede"):
    import live

    await live.handle_live_websocket(websocket, voice=voice)


if HUD_DIR.exists():
    app.mount("/", StaticFiles(directory=str(HUD_DIR), html=True), name="hud")

