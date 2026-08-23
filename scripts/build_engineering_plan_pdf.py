#!/usr/bin/env python3
"""LOONA engineering + orchestration plan PDF."""

from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    Image,
    KeepTogether,
    ListFlowable,
    ListItem,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

OUT = Path("/Users/imac/loona/docs/LOONA_Plan_Ingenieria.pdf")
DIAG = Path("/Users/imac/loona/refs/diagrams")
ZOEY = Path("/Users/imac/loona/refs/zoey")

NAVY = colors.HexColor("#070B12")
NAVY2 = colors.HexColor("#121826")
TEAL = colors.HexColor("#5EEAD4")
VIO = colors.HexColor("#7C5CFF")
GOLD = colors.HexColor("#C9A227")
INK = colors.HexColor("#1C2430")
MUTED = colors.HexColor("#5A6573")
CREAM = colors.HexColor("#F4F1EA")
ROW = colors.HexColor("#EAE6DC")
RULE = colors.HexColor("#D4CFC3")
WHITE = colors.white
PW = 7.0 * inch


def styles():
    s = {}
    s["kicker"] = ParagraphStyle("kicker", fontName="Helvetica", fontSize=9, leading=12, textColor=TEAL)
    s["cover_title"] = ParagraphStyle("cover_title", fontName="Helvetica-Bold", fontSize=20, leading=25, textColor=WHITE, spaceAfter=6)
    s["cover_sub"] = ParagraphStyle("cover_sub", fontName="Helvetica", fontSize=10.5, leading=14.5, textColor=colors.HexColor("#C8D4E0"))
    s["h1"] = ParagraphStyle("h1", fontName="Helvetica-Bold", fontSize=15, leading=19, textColor=NAVY, spaceBefore=14, spaceAfter=7)
    s["h2"] = ParagraphStyle("h2", fontName="Helvetica-Bold", fontSize=12, leading=15, textColor=NAVY2, spaceBefore=10, spaceAfter=5)
    s["h3"] = ParagraphStyle("h3", fontName="Helvetica-Bold", fontSize=10.5, leading=13, textColor=INK, spaceBefore=7, spaceAfter=3)
    s["body"] = ParagraphStyle("body", fontName="Helvetica", fontSize=9.3, leading=13, textColor=INK, alignment=TA_JUSTIFY, spaceAfter=6)
    s["lead"] = ParagraphStyle("lead", fontName="Helvetica", fontSize=10.2, leading=14.4, textColor=INK, alignment=TA_JUSTIFY, spaceAfter=8)
    s["note"] = ParagraphStyle("note", fontName="Helvetica-Oblique", fontSize=8.6, leading=12, textColor=MUTED, spaceAfter=7)
    s["bullet"] = ParagraphStyle("bullet", fontName="Helvetica", fontSize=9.2, leading=12.8, textColor=INK)
    s["code"] = ParagraphStyle("code", fontName="Courier", fontSize=7.6, leading=10.4, textColor=NAVY, backColor=CREAM, leftIndent=5, rightIndent=5, spaceBefore=2, spaceAfter=6)
    s["th"] = ParagraphStyle("th", fontName="Helvetica-Bold", fontSize=7.8, leading=10.5, textColor=WHITE)
    s["td"] = ParagraphStyle("td", fontName="Helvetica", fontSize=7.8, leading=10.5, textColor=INK)
    s["td_b"] = ParagraphStyle("td_b", fontName="Helvetica-Bold", fontSize=7.8, leading=10.5, textColor=NAVY)
    s["cap"] = ParagraphStyle("cap", fontName="Helvetica-Oblique", fontSize=8, leading=10.5, textColor=MUTED, spaceAfter=8, spaceBefore=2)
    s["toc"] = ParagraphStyle("toc", fontName="Helvetica", fontSize=10, leading=15, textColor=INK)
    return s


S = styles()


def P(t, st="body"):
    return Paragraph(t, S[st])


def bullets(items):
    return ListFlowable(
        [ListItem(P(i, "bullet"), leftIndent=10) for i in items],
        bulletType="bullet", start="•", leftIndent=14, bulletFontSize=8, spaceAfter=6,
    )


def code(text):
    html = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace("\n", "<br/>")
    return Paragraph(html, S["code"])


def table(headers, rows, widths):
    data = [[P(h, "th") for h in headers]]
    for r in rows:
        data.append([P(str(c), "td_b" if i == 0 else "td") for i, c in enumerate(r)])
    t = Table(data, colWidths=widths, repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), NAVY),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [CREAM, ROW]),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 3.5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3.5),
        ("GRID", (0, 0), (-1, -1), 0.3, RULE),
        ("LINEBELOW", (0, 0), (-1, 0), 1.4, TEAL),
    ]))
    return t


def fig(path, caption, max_h=3.15 * inch):
    if not path.exists():
        return P(f"[diagrama ausente: {path.name}]", "note")
    im = Image(str(path))
    iw, ih = im.imageWidth, im.imageHeight
    w = PW
    h = w * ih / iw
    if h > max_h:
        h = max_h
        w = h * iw / ih
    im.drawWidth = w
    im.drawHeight = h
    im.hAlign = "CENTER"
    return KeepTogether([im, P(caption, "cap")])


def callout(title, body, bar=TEAL):
    inner = Table([[P(f"<b>{title}</b>", "h3")], [P(body, "body")]], colWidths=[PW - 12])
    inner.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), CREAM),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
        ("TOPPADDING", (0, 0), (0, 0), 6),
        ("BOTTOMPADDING", (0, -1), (-1, -1), 5),
        ("LINEBEFORE", (0, 0), (0, -1), 4, bar),
    ]))
    return inner


def header_footer(c, doc):
    w, h = letter
    c.saveState()
    c.setFillColor(NAVY)
    c.rect(0, h - 26, w, 26, fill=1, stroke=0)
    c.setFillColor(TEAL)
    c.rect(0, h - 28, w, 2, fill=1, stroke=0)
    c.setFillColor(WHITE)
    c.setFont("Helvetica", 8)
    c.drawString(0.7 * inch, h - 17, "LOONA  ·  Plan de ingeniería y orquestación")
    c.drawRightString(w - 0.7 * inch, h - 17, "12 ago 2026  ·  Grok Lead")
    c.setFillColor(NAVY)
    c.rect(0, 0, w, 22, fill=1, stroke=0)
    c.setFillColor(VIO)
    c.rect(0, 22, w, 2, fill=1, stroke=0)
    c.setFillColor(WHITE)
    c.setFont("Helvetica", 8)
    c.drawString(0.7 * inch, 8, "herdr wB  ·  /Users/imac/loona")
    c.drawRightString(w - 0.7 * inch, 8, f"Página {doc.page}")
    c.restoreState()


def build():
    story = []
    hero = Table(
        [
            [P("ENGINEERING PLAN  ·  AGENTIC ORCHESTRATION  ·  P2 STUDIO", "kicker")],
            [P("LOONA — OS personal self-hosted<br/>con cara de Zoey, paleta propia y más perillas", "cover_title")],
            [P(
                "Plan de ingeniería fullstack: arquitectura, flujos, grafos, gobernanza y harness "
                "para Grok + Antigravity CLI (Agy) + Claude Code + Codex. "
                "Hardware real: iMac Intel i5-6500 / 24 GB / Monterey 12.7.6.",
                "cover_sub",
            )],
        ],
        colWidths=[PW - 6],
    )
    hero.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), NAVY),
        ("LEFTPADDING", (0, 0), (-1, -1), 14),
        ("RIGHTPADDING", (0, 0), (-1, -1), 14),
        ("TOPPADDING", (0, 0), (0, 0), 14),
        ("BOTTOMPADDING", (0, -1), (-1, -1), 14),
        ("LINEBELOW", (0, -1), (-1, -1), 4, TEAL),
    ]))
    story.append(hero)
    story.append(Spacer(1, 10))
    story.append(table(
        ["Campo", "Valor"],
        [
            ["Producto", "LOONA — no se llama Jarvis. No es Zoey OS."],
            ["Inspiración visual", "Zoey OS World View: cabeza de partículas 3D + Knowledge View + companions"],
            ["Diferencia visual", "Paleta teal #5EEAD4 → violeta #7C5CFF (Zoey es ámbar). Más config."],
            ["Ref de video", "Downloads/ScreenRecording_08-12-2026 11-06-01_1.MP4 (27s)"],
            ["Lead", "Grok — orquesta, verifica, único DONE global"],
            ["Agy / Antigravity", "wB:p1 — HUD / World View  ·  write hud/ refs/ assets/"],
            ["Claude Code", "wB:p2 — runtime / API / OpenClaw  ·  write runtime/"],
            ["Codex", "wB:p3 — spec / schema / memoria  ·  write docs/ identity/ config/"],
            ["DoD", "8 pruebas en docs/GOVERNANCE.md. Loops hasta verde."],
        ],
        [1.7 * inch, 5.3 * inch],
    ))

    story.append(P("Contenido", "h1"))
    for i in [
        "1. Misión, DoD y por qué no instalamos Zoey",
        "2. DNA visual (Zoey → LOONA) y superficie de configuración",
        "3. Arquitectura de contenedores y envelope de hardware",
        "4. Flujos: datos, chat, secretos",
        "5. Grafo de agentes, contratos y DAG",
        "6. Harness, gobernanza y máquina de estados",
        "7. Ingeniería del HUD (partículas, config, knowledge)",
        "8. Ingeniería del runtime (API, cerebro, OpenClaw)",
        "9. Loop 1 — briefs por pane (para no pelearse)",
        "10. Verify y criterio de stop",
    ]:
        story.append(P(i, "toc"))

    story.append(PageBreak())
    story.append(P("1. Misión, DoD y por qué no instalamos Zoey", "h1"))
    story.append(P(
        "Zoey OS es un SaaS cerrado (zoeyos.com): World View 3D, companions, Knowledge Base, "
        "skills, 1 000+ integraciones, automations. El video de referencia muestra exactamente eso: "
        "fondo negro, cabeza de puntos ámbar, label ZOEY, flechas, botón KNOWLEDGE VIEW, rail de "
        "tareas y panel KARMA/PULSE. No es open source. Instalar Zoey sería cuenta + trial + "
        "depender de su nube. Eso rompe el contrato del studio (self-hosted, keys nuestras, "
        "free-first) y no corre bien como “dueño” en un iMac Intel de 2015.",
        "lead",
    ))
    story.append(P(
        "LOONA clona el <b>lenguaje visual y la UX</b> (cara de partículas, world view, knowledge, "
        "config, companions), cambia el color, expone <b>más perillas</b> en JSON schema, y corre "
        "100% en 127.0.0.1 con Grok/Claude/Gemini/Ollama. El cerebro 24/7 puede ser OpenClaw; "
        "el cuerpo visual es nuestro HUD.",
        "body",
    ))
    story.append(P("Definition of Done (8 pruebas, todas o nada)", "h2"))
    story.append(table(
        ["#", "Prueba", "Evidencia"],
        [
            ["1", "HUD en http://127.0.0.1:8766", "curl / o screenshot"],
            ["2", "Cabeza de partículas teal→violeta, label LOONA", "refs/hud/world.png"],
            ["3", "Config ≥ 12 controles reales ligados al schema", "refs/hud/config.png"],
            ["4", "Knowledge View muestra SOUL.md", "texto visible en HUD"],
            ["5", "Chat del HUD responde con un modelo", "turno + log"],
            ["6", "Runtime health o OpenClaw doctor verde", "GET /api/health"],
            ["7", "Guardrail bloquea .env y publish", "respuesta de rechazo"],
            ["8", "STATUS.md con hora MTY", "docs/STATUS.md"],
        ],
        [0.4 * inch, 3.5 * inch, 3.1 * inch],
    ))
    story.append(callout(
        "Criterio legal / ético de inspiración",
        "Se permite: paleta propia, geometría de partículas original, layout (centro + rails + chat). "
        "Se prohíbe: extraer CSS/JS de zoeyos.com, usar su wordmark, reclamar compatibilidad. "
        "Zoey es la referencia de UX; LOONA es implementación limpia.",
    ))

    story.append(P("2. DNA visual (Zoey → LOONA) y superficie de configuración", "h1"))
    story.append(P(
        "Del screen recording (27.5 s, 1320×2868, 12 ago 2026) se extrae el sistema visual:",
        "body",
    ))
    story.append(table(
        ["Pieza Zoey (ref)", "Qué hace", "LOONA (delta)"],
        [
            ["Cabeza point-cloud ámbar", "Identidad viva del OS, rota", "Misma idea, gradiente teal→violeta, morph face/sphere/moon"],
            ["Label ZOEY + flechas", "Identidad + switch de vista", "Label LOONA. Flechas ciclan companions"],
            ["KNOWLEDGE VIEW", "Memoria visible", "Panel que lee identity/*.md vía /api/knowledge"],
            ["Rail de tareas (ads, CTR…)", "Trabajo en curso", "Activity widget + companions Brain/Memory/Ops"],
            ["Chat KARMA / PULSE", "Conversación continua", "Chat dock redimensionable, pop-out fase 2"],
            ["Config View (guía oficial)", "Hasta 20 companions, interviews", "JSON schema versionable, ≥12 knobs, sin interviews mágicos"],
        ],
        [1.8 * inch, 2.3 * inch, 2.9 * inch],
    ))
    story.append(P(
        "Más config que Zoey (día 1), todo en config/loona.schema.json:",
        "h2",
    ))
    story.append(bullets([
        "<b>world:</b> particleCount, paletteFrom/To, headMorph, rotationSpeed, bloom, showOrbs",
        "<b>voice:</b> wakeWord=loona, mode typed-only|wake|ptt, stt, tts",
        "<b>brain:</b> provider, model, baseUrl, dailyTokenCap, temperature",
        "<b>memory:</b> soulPath, retentionDays, compound",
        "<b>guardrails:</b> sandbox, allowPublish, allowSecretRead, computer-use, askOnIrreversible",
        "<b>channels:</b> telegram, hud, bind 127.0.0.1",
        "<b>hud:</b> port, chatDefaultWidth, showActivity, knowledgeOpen",
        "<b>companions[]:</b> id, name, role, color, model, skills (máx 8 en este iMac, no 20)",
    ]))

    story.append(PageBreak())
    story.append(P("3. Arquitectura de contenedores y envelope de hardware", "h1"))
    story.append(P(
        "Cuatro contenedores lógicos en un solo host. Nada de Kubernetes. El i5-6500 orquesta; "
        "el modelo pesado vive en la nube ya pagada o en Ollama 3B.",
        "body",
    ))
    story.append(fig(DIAG / "01_architecture.png", "Figura 1. Contenedores: HUD, control plane, brain, memory, tools."))
    story.append(table(
        ["Constraint", "Implicación de diseño"],
        [
            ["CPU 4c / 2015, HD 530", "HUD: Points de Three.js, 6k–16k partículas. Sin bloom caro. Sin mlx-audio."],
            ["24 GB RAM", "Ollama 3B–7B máx. No servir 32B. No Electron+Chrome+Ollama 14B a la vez."],
            ["macOS 12.7.6", "Evitar Swift reciente / Flightdeck nativo. Browser localhost es el shell."],
            ["Node 24 + Python 3.14", "OpenClaw viable. Si 3.14 rompe wheels, runtime en 3.12 o Node."],
            ["Ollama instalado, daemon down", "Claude Code lo levanta o degrada a cloud key."],
        ],
        [2.3 * inch, 4.7 * inch],
    ))

    story.append(P("4. Flujos: datos, chat, secretos", "h1"))
    story.append(P("4.1 Secuencia de un turno", "h2"))
    story.append(fig(DIAG / "03_sequence_chat.png", "Figura 2. POST /api/chat → guardrail → brain → stream. Block no toca al modelo."))
    story.append(P("4.2 Datos y secretos", "h2"))
    story.append(fig(DIAG / "05_data_flow.png", "Figura 3. Repo sin keys. RAM con keychain. Egreso solo al provider elegido."))
    story.append(code(
        "POST /api/chat\n"
        "  → classify(text):  safe | ask | block\n"
        "  → block: {error:'guardrail', rule:'allowSecretRead|allowPublish'}\n"
        "  → ask:   {need_human:true, action:...}\n"
        "  → allow: messages = [SOUL, MEMORY, history, user] → provider"
    ))

    story.append(PageBreak())
    story.append(P("5. Grafo de agentes, contratos y DAG", "h1"))
    story.append(P(
        "Un write-path por agente. Cuatro briefs idénticos es el anti-patrón del studio. "
        "Los contratos son HTTP + JSON schema + STATUS.md — no reuniones.",
        "body",
    ))
    story.append(fig(DIAG / "02_agent_graph.png", "Figura 4. Grok despacha. Agy pinta. Claude sirve. Codex especifica."))
    story.append(fig(DIAG / "06_wbs_dag.png", "Figura 5. Loop 1 en paralelo (L1). Integrate (L2). Verify (L3)."))
    story.append(table(
        ["Contrato", "De", "A", "Forma"],
        [
            ["loona.schema.json", "Codex", "Claude + Agy", "archivo en config/"],
            ["GET/PUT /api/config", "Claude", "Agy", "HTTP 127.0.0.1"],
            ["GET /api/knowledge", "Claude", "Agy", "text/markdown JSON"],
            ["POST /api/chat", "Claude", "Agy", "JSON"],
            ["refs/hud/*.png", "Agy", "Grok", "archivo"],
            ["docs/STATUS.md", "todos", "Grok", "append-only"],
        ],
        [1.6 * inch, 1.2 * inch, 1.3 * inch, 2.9 * inch],
    ))

    story.append(P("6. Harness, gobernanza y máquina de estados", "h1"))
    story.append(P(
        "Canónico en disco: docs/GOVERNANCE.md, docs/HARNESS.md, docs/ROLES.md, identity/SOUL.md. "
        "El harness existe para que un agente idle no se quede esperando permiso. Si su checklist "
        "local no está verde, vuelve al siguiente ítem. Si un contrato ajeno no existe, implementa stub.",
        "body",
    ))
    story.append(fig(DIAG / "04_loop_fsm.png", "Figura 6. IDLE → READ → BUILD → EVIDENCE → (loop | BLOCKED | VERIFY)."))
    story.append(callout(
        "Stop condition",
        "El loop termina cuando Grok (no Agy, no Claude, no Codex) marca las 8 pruebas DoD. "
        "Un HUD bonito sin /api/health no es done. Un API sin cabeza de partículas no es done. "
        "NEED_HUMAN solo por login/MFA/pago/ToS o si OpenClaw pide un wizard interactivo en el pane.",
        bar=VIO,
    ))

    story.append(P("7. Ingeniería del HUD (Agy / Antigravity)", "h1"))
    story.append(bullets([
        "Vanilla HTML/CSS/JS + Three.js desde CDN. Sin React el día 1. Sin Electron.",
        "world.js: BufferGeometry + Points. Posiciones = esfera perturbada (simplex barato o noise 3D).",
        "Color por vértice: mix(paletteFrom, paletteTo, y). Label canvas/sprite “LOONA”.",
        "FPS watchdog: si &lt; 24 durante 2 s, bajar particleCount 20% y persistir via PUT /api/config.",
        "Vistas: World | Knowledge | Config. Teclas: 1/2/3, Esc cierra paneles, [ ] chat width.",
        "Config: un control por propiedad del schema (range, color, select, toggle). No hardcodear.",
        "Si /api/* no está: fallback fetch a /config/loona.default.json por static server.",
    ]))
    story.append(code(
        "hud/\n"
        "  index.html\n"
        "  css/loona.css          # tokens --bg --teal --violet\n"
        "  js/world.js            # partículas + orbs\n"
        "  js/config-view.js      # liga schema\n"
        "  js/chat.js             # POST /api/chat\n"
        "  js/knowledge.js        # GET /api/knowledge"
    ))

    story.append(P("8. Ingeniería del runtime (Claude Code)", "h1"))
    story.append(P(
        "Prioridad A: OpenClaw onboard --install-daemon si el wizard no se atasca en Monterey. "
        "Prioridad B (más fluida en este iMac): FastAPI en runtime/app.py sirviendo HUD estático "
        "y los 4 endpoints. OpenClaw se puede enchufar después como provider.",
        "body",
    ))
    story.append(table(
        ["Endpoint", "Contrato"],
        [
            ["GET /api/health", "{ok:true, name:\"LOONA\", provider, particles}"],
            ["GET /api/config", "objeto válido contra loona.schema.json"],
            ["PUT /api/config", "merge + validar; 400 si viola schema"],
            ["GET /api/knowledge", "{soul, memory} markdown"],
            ["POST /api/chat", "{text} → {reply} o {error, rule}"],
        ],
        [2.2 * inch, 4.8 * inch],
    ))
    story.append(P(
        "Cerebro: LOONA_PROVIDER + key de entorno. Orden de fallback: XAI_API_KEY → GEMINI_API_KEY "
        "→ ANTHROPIC_API_KEY → Ollama localhost. Guardrail regex: .env, api_key, sk-, publish, "
        "instagram.com/p/, rm -rf /.",
        "note",
    ))

    story.append(PageBreak())
    story.append(P("9. Loop 1 — briefs por pane (para no pelearse)", "h1"))
    story.append(P("Estos briefs se pegan tal cual vía herdr agent prompt &lt;pane_id&gt;.", "body"))
    story.append(P("Agy wB:p1 — HUD", "h2"))
    story.append(code(
        "Eres Agy/Antigravity en /Users/imac/loona. WRITE solo hud/ refs/ assets/.\n"
        "Lee identity/SOUL.md docs/GOVERNANCE.md docs/HARNESS.md docs/ROLES.md.\n"
        "Construye World View tipo Zoey (refs/zoey/*.jpg) con paleta teal→violeta,\n"
        "label LOONA, Knowledge View, Config ≥12 knobs, chat panel.\n"
        "Three.js CDN. 6k–16k partículas. Loop HARNESS hasta tu checklist verde.\n"
        "Screenshot refs/hud/world.png y config.png. STATUS.md al cerrar cada turno.\n"
        "NO toques runtime/ ni identity/SOUL.md. NO esperes a Claude: stubea /api."
    ))
    story.append(P("Claude Code wB:p2 — runtime", "h2"))
    story.append(code(
        "Eres Claude Code en /Users/imac/loona. WRITE solo runtime/ y scripts/loona-up.sh.\n"
        "Lee SOUL, GOVERNANCE, HARNESS, ROLES, config/loona.schema.json.\n"
        "Levanta control plane 127.0.0.1 (FastAPI sirviendo hud/ + /api/*).\n"
        "OpenClaw solo si onboard es no-interactivo; si pide wizard, STATUS NEED_HUMAN\n"
        "y sigue con FastAPI. Chat + guardrails. Loop hasta checklist runtime verde.\n"
        "NO edites hud/css ni world.js."
    ))
    story.append(P("Codex wB:p3 — spec", "h2"))
    story.append(code(
        "Eres Codex en /Users/imac/loona. WRITE solo docs/ identity/ config/\n"
        "(excepto no reescribir SOUL.md ni GOVERNANCE.md salvo typos).\n"
        "Completa MEMORY.md, API.md, alinea ARCHITECTURE.md al código que vaya apareciendo,\n"
        "mantén STATUS.md. Schema ya existe: extiende companions/skills si hace falta.\n"
        "Loop HARNESS. NO implementes Three.js ni el server."
    ))

    story.append(P("10. Verify y criterio de stop", "h1"))
    story.append(bullets([
        "Grok corre las 8 pruebas en orden. Falla = re-prompt SOLO al dueño del write-path.",
        "Si Agy pinta ámbar o escribe ZOEY/JARVIS: rechazo visual, no “casi”.",
        "Si Claude expone 0.0.0.0: rollback a 127.0.0.1.",
        "Si Codex y el código divergen: gana el código, Codex actualiza ARCHITECTURE.",
        "Stop = DoD verde + STATUS final. Entonces y solo entonces se habla de Telegram/voz wake.",
    ]))
    story.append(Spacer(1, 8))
    story.append(callout(
        "Orden de ataque ahora",
        "1) Este PDF y los markdown canónicos ya están en disco. "
        "2) Grok despacha los tres panes en paralelo (L1). "
        "3) Integrate L2 cuando existan hud/index.html y runtime health. "
        "4) Verify L3. Re-loop. "
        "5) Voz wake / Telegram = fase 2, no bloquean el DoD del HUD+API.",
        bar=GOLD,
    ))
    story.append(P(
        "Canónicos: identity/SOUL.md · docs/GOVERNANCE.md · docs/HARNESS.md · docs/ROLES.md · "
        "config/loona.schema.json · refs/diagrams/*.png · este PDF.",
        "note",
    ))

    OUT.parent.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(
        str(OUT), pagesize=letter,
        leftMargin=0.75 * inch, rightMargin=0.75 * inch,
        topMargin=0.52 * inch, bottomMargin=0.42 * inch,
        title="LOONA — Plan de ingeniería y orquestación",
        author="Grok Lead",
        subject="Arquitectura, flujos, grafos, harness para Agy, Claude Code y Codex",
    )
    doc.build(story, onFirstPage=header_footer, onLaterPages=header_footer)
    print("Wrote", OUT, OUT.stat().st_size)


if __name__ == "__main__":
    build()
