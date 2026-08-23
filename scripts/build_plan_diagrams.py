#!/usr/bin/env python3
"""Engineering diagrams for the LOONA plan PDF — Pillow only."""

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

OUT = Path("/Users/imac/loona/refs/diagrams")
OUT.mkdir(parents=True, exist_ok=True)

BG = (7, 11, 18)
INK = (232, 238, 246)
MUTED = (139, 151, 168)
TEAL = (94, 234, 212)
VIO = (124, 92, 255)
GOLD = (201, 162, 39)
BOX = (18, 24, 38)
EDGE = (42, 53, 72)


def font(size, bold=False):
    candidates = [
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf" if bold else "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
        "/Library/Fonts/Arial.ttf",
    ]
    for p in candidates:
        try:
            return ImageFont.truetype(p, size)
        except Exception:
            continue
    return ImageFont.load_default()


F_TITLE = font(28, True)
F_H = font(18, True)
F_B = font(15)
F_S = font(13)


def new(w=1400, h=820):
    im = Image.new("RGB", (w, h), BG)
    dr = ImageDraw.Draw(im)
    return im, dr


def rbox(dr, xy, fill=BOX, outline=TEAL, rad=16, width=2):
    dr.rounded_rectangle(xy, radius=rad, fill=fill, outline=outline, width=width)


def center(dr, box, text, fnt, fill=INK):
    x0, y0, x1, y1 = box
    dr.text(((x0 + x1) / 2, (y0 + y1) / 2), text, font=fnt, fill=fill, anchor="mm", align="center")


def multiline(dr, cx, y, lines, fnt, fill=INK, gap=20):
    for i, line in enumerate(lines):
        dr.text((cx, y + i * gap), line, font=fnt, fill=fill, anchor="ma")


def arrow(dr, a, b, fill=VIO, w=3):
    dr.line([a, b], fill=fill, width=w)
    # simple chevron
    x, y = b
    sx, sy = a
    import math
    ang = math.atan2(y - sy, x - sx)
    s = 12
    p1 = (x - s * math.cos(ang - 0.45), y - s * math.sin(ang - 0.45))
    p2 = (x - s * math.cos(ang + 0.45), y - s * math.sin(ang + 0.45))
    dr.polygon([b, p1, p2], fill=fill)


def titled_box(dr, xy, title, lines, outline=TEAL):
    rbox(dr, xy, outline=outline)
    x0, y0, x1, y1 = xy
    dr.text(((x0 + x1) / 2, y0 + 22), title, font=F_H, fill=outline, anchor="ma")
    if lines:
        multiline(dr, (x0 + x1) / 2, y0 + 50, lines, F_S, INK, 20)


def save(im, name):
    path = OUT / name
    im.save(path, "PNG")
    print("wrote", path, im.size)


# 1 architecture
im, dr = new()
dr.text((700, 36), "LOONA — arquitectura de contenedores (este iMac)", font=F_TITLE, fill=INK, anchor="ma")
titled_box(dr, (40, 80, 340, 220), "Humano", ["voz / teclado / Telegram"], GOLD)
titled_box(dr, (430, 80, 970, 220), "HUD World View", ["Three.js + Config  ·  127.0.0.1:8766"], TEAL)
titled_box(dr, (1060, 80, 1360, 220), "herdr LOONA", ["Agy · Claude · Codex"], VIO)
arrow(dr, (340, 150), (430, 150), TEAL)
arrow(dr, (970, 150), (1060, 150), VIO)
titled_box(dr, (360, 300, 1040, 500), "Control plane  runtime/", [
    "FastAPI o OpenClaw Gateway",
    "/api/health   /api/config   /api/knowledge   /api/chat",
    "guardrail middleware  ·  bind 127.0.0.1",
], TEAL)
arrow(dr, (700, 220), (700, 300), TEAL)
titled_box(dr, (40, 560, 420, 750), "Brain", ["Grok / Gemini / Claude", "Ollama fallback  ·  cap diario"], VIO)
titled_box(dr, (500, 560, 900, 750), "Memory", ["SOUL.md  ·  MEMORY.md", "wiki de sesiones"], TEAL)
titled_box(dr, (980, 560, 1360, 750), "Tools", ["files · exec · MCP · cron", "sandbox on"], GOLD)
arrow(dr, (500, 500), (230, 560), VIO)
arrow(dr, (700, 500), (700, 560), TEAL)
arrow(dr, (900, 500), (1170, 560), GOLD)
dr.text((700, 790), "Intel i5-6500  ·  6k–16k partículas  ·  no mlx  ·  no Flightdeck nativo", font=F_S, fill=MUTED, anchor="ma")
save(im, "01_architecture.png")

# 2 agent graph
im, dr = new()
dr.text((700, 36), "Grafo de orquestación y write-paths", font=F_TITLE, fill=INK, anchor="ma")
titled_box(dr, (460, 70, 940, 200), "Grok Lead", ["plan PDF · harness · verify DoD"], GOLD)
titled_box(dr, (40, 280, 430, 470), "Agy  wB:p1", ["WRITE  hud/  refs/  assets/", "World View + Config UI"], TEAL)
titled_box(dr, (485, 280, 915, 470), "Claude  wB:p2", ["WRITE  runtime/  scripts/", "API + OpenClaw / Ollama"], VIO)
titled_box(dr, (970, 280, 1360, 470), "Codex  wB:p3", ["WRITE  docs/ identity/ config/", "schema + STATUS"], GOLD)
arrow(dr, (540, 200), (235, 280), TEAL)
arrow(dr, (700, 200), (700, 280), VIO)
arrow(dr, (860, 200), (1165, 280), GOLD)
titled_box(dr, (200, 560, 1200, 760), "Contratos", [
    "Codex schema  →  Claude valida PUT /api/config",
    "Claude /api/*  →  Agy fetch     ·     Agy screenshots  →  Grok verify",
    "Todos escriben docs/STATUS.md  →  Grok re-dispatch hasta DoD verde",
], INK)
save(im, "02_agent_graph.png")

# 3 sequence
im, dr = new(1400, 880)
dr.text((700, 36), "Secuencia — un turno de chat (texto, día 1)", font=F_TITLE, fill=INK, anchor="ma")
xs = [("HUD", 180), ("API", 520), ("Guardrail", 860), ("Brain", 1200)]
for name, x in xs:
    dr.text((x, 90), name, font=F_H, fill=TEAL, anchor="ma")
    dr.line((x, 110, x, 820), fill=EDGE, width=2)
steps = [
    (160, 180, 520, "POST /api/chat {text}"),
    (230, 520, 860, "classify risk"),
    (300, 860, 520, "allow | ask | block"),
    (370, 520, 1200, "si allow: messages + SOUL"),
    (440, 1200, 520, "stream tokens"),
    (510, 520, 180, "JSON / SSE reply"),
    (620, 520, 180, "si block: reason (nunca al brain)"),
]
for y, x1, x2, label in steps:
    arrow(dr, (x1, y), (x2, y), VIO)
    dr.text(((x1 + x2) / 2, y - 16), label, font=F_S, fill=INK, anchor="ma")
dr.text((700, 850), "Publish / secret-read no llegan al modelo. Computer-use fuera de /loona → ASK.", font=F_S, fill=MUTED, anchor="ma")
save(im, "03_sequence_chat.png")

# 4 FSM
im, dr = new()
dr.text((700, 36), "Máquina de estados del harness", font=F_TITLE, fill=INK, anchor="ma")
titled_box(dr, (60, 200, 300, 360), "IDLE", ["espera brief"], TEAL)
titled_box(dr, (420, 80, 700, 230), "READ", ["SOUL + STATUS"], VIO)
titled_box(dr, (820, 200, 1100, 360), "BUILD", ["siguiente P0"], TEAL)
titled_box(dr, (820, 460, 1100, 620), "EVIDENCE", ["STATUS.md"], GOLD)
titled_box(dr, (420, 580, 700, 740), "VERIFY", ["Grok · 8 pruebas"], GOLD)
titled_box(dr, (60, 460, 300, 620), "BLOCKED", ["error exacto"], (224, 90, 106))
arrow(dr, (180, 200), (420, 160), TEAL)
arrow(dr, (700, 160), (820, 240), VIO)
arrow(dr, (960, 360), (960, 460), GOLD)
arrow(dr, (820, 540), (300, 540), TEAL)
arrow(dr, (180, 460), (180, 360), TEAL)
arrow(dr, (560, 580), (560, 230), GOLD)
dr.text((700, 790), "Nadie declara DONE global. Grok verifica. Re-dispatch si falta evidencia.", font=F_S, fill=MUTED, anchor="ma")
save(im, "04_loop_fsm.png")

# 5 data flow
im, dr = new()
dr.text((700, 36), "Flujo de datos y secretos", font=F_TITLE, fill=INK, anchor="ma")
titled_box(dr, (40, 100, 440, 380), "Disco (repo)", ["identity/*.md", "config/*.json", "hud/  runtime/", "SIN keys"], TEAL)
titled_box(dr, (500, 100, 900, 380), "Runtime RAM", [".env / keychain", "sesión de chat", "rate limit diario"], VIO)
titled_box(dr, (960, 100, 1360, 380), "Fuera del host", ["Provider LLM", "Telegram fase 2", "NUNCA train Zoey"], GOLD)
arrow(dr, (440, 240), (500, 240), TEAL)
arrow(dr, (900, 240), (960, 240), VIO)
titled_box(dr, (160, 460, 1240, 740), "Política", [
    "Audio sale solo si voice.mode != typed-only y STT cloud está elegido",
    "Knowledge = Markdown local; export = zip del repo",
    "Redactar secret-shaped strings antes de TTS",
    "API y Gateway escuchan 127.0.0.1 — no port-forward",
], INK)
save(im, "05_data_flow.png")

# 6 DAG
im, dr = new()
dr.text((700, 36), "DAG de entrega — loop 1 en paralelo, luego integrate", font=F_TITLE, fill=INK, anchor="ma")
titled_box(dr, (40, 100, 420, 300), "L1  Codex", ["schema + MEMORY", "STATUS vivo"], GOLD)
titled_box(dr, (490, 100, 910, 300), "L1  Agy", ["HUD partículas", "Config UI"], TEAL)
titled_box(dr, (980, 100, 1360, 300), "L1  Claude", ["/api stub+real", "loona-up.sh"], VIO)
titled_box(dr, (240, 400, 1160, 560), "L2  Integrate", [
    "HUD consume /api   ·   schema valida   ·   Knowledge lee SOUL",
], INK)
titled_box(dr, (240, 620, 1160, 760), "L3  Grok verify", [
    "8 pruebas DoD   ·   screenshots   ·   re-dispatch o DONE",
], GOLD)
arrow(dr, (230, 300), (500, 400), GOLD)
arrow(dr, (700, 300), (700, 400), TEAL)
arrow(dr, (1170, 300), (900, 400), VIO)
arrow(dr, (700, 560), (700, 620), GOLD)
save(im, "06_wbs_dag.png")

print("ok")
