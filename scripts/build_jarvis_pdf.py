#!/usr/bin/env python3
"""Generate the LOONA Jarvis step-by-step guide PDF."""

from __future__ import annotations

from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    CondPageBreak,
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

OUT = Path("/Users/imac/loona/docs/LOONA_Jarvis_Guia.pdf")

NAVY = colors.HexColor("#0B1F3A")
NAVY_MID = colors.HexColor("#16325A")
GOLD = colors.HexColor("#C9A227")
GOLD_SOFT = colors.HexColor("#E8D48B")
CREAM = colors.HexColor("#F7F4EC")
INK = colors.HexColor("#1C2430")
MUTED = colors.HexColor("#5A6573")
RULE = colors.HexColor("#D8D2C4")
ROW = colors.HexColor("#F3F0E7")
OK = colors.HexColor("#1F6B4A")
WARN = colors.HexColor("#8A4B12")
BAD = colors.HexColor("#8B1E2D")
WHITE = colors.white


def styles():
    base = getSampleStyleSheet()
    s = {}
    s["cover_kicker"] = ParagraphStyle(
        "cover_kicker",
        fontName="Helvetica",
        fontSize=10,
        leading=13,
        textColor=GOLD,
        alignment=TA_LEFT,
        tracking=1.4,
        spaceAfter=8,
    )
    s["cover_title"] = ParagraphStyle(
        "cover_title",
        fontName="Helvetica-Bold",
        fontSize=22,
        leading=27,
        textColor=WHITE,
        alignment=TA_LEFT,
        spaceAfter=8,
    )
    s["cover_sub"] = ParagraphStyle(
        "cover_sub",
        fontName="Helvetica",
        fontSize=11,
        leading=15.5,
        textColor=GOLD_SOFT,
        alignment=TA_LEFT,
        spaceAfter=2,
    )
    s["h1"] = ParagraphStyle(
        "h1",
        fontName="Helvetica-Bold",
        fontSize=16,
        leading=20,
        textColor=NAVY,
        spaceBefore=16,
        spaceAfter=8,
    )
    s["h2"] = ParagraphStyle(
        "h2",
        fontName="Helvetica-Bold",
        fontSize=12.5,
        leading=16,
        textColor=NAVY_MID,
        spaceBefore=12,
        spaceAfter=6,
    )
    s["h3"] = ParagraphStyle(
        "h3",
        fontName="Helvetica-Bold",
        fontSize=11,
        leading=14,
        textColor=INK,
        spaceBefore=9,
        spaceAfter=4,
    )
    s["body"] = ParagraphStyle(
        "body",
        fontName="Helvetica",
        fontSize=9.5,
        leading=13.4,
        textColor=INK,
        alignment=TA_JUSTIFY,
        spaceAfter=7,
    )
    s["lead"] = ParagraphStyle(
        "lead",
        fontName="Helvetica",
        fontSize=10.5,
        leading=15,
        textColor=INK,
        alignment=TA_JUSTIFY,
        spaceAfter=10,
    )
    s["note"] = ParagraphStyle(
        "note",
        fontName="Helvetica-Oblique",
        fontSize=9,
        leading=12.5,
        textColor=MUTED,
        alignment=TA_LEFT,
        spaceBefore=2,
        spaceAfter=8,
        leftIndent=8,
        borderPadding=4,
    )
    s["bullet"] = ParagraphStyle(
        "bullet",
        fontName="Helvetica",
        fontSize=9.5,
        leading=13.2,
        textColor=INK,
        leftIndent=4,
        spaceAfter=2,
    )
    s["code"] = ParagraphStyle(
        "code",
        fontName="Courier",
        fontSize=8,
        leading=11.2,
        textColor=NAVY,
        backColor=CREAM,
        leftIndent=6,
        rightIndent=6,
        spaceBefore=3,
        spaceAfter=7,
    )
    s["th"] = ParagraphStyle(
        "th",
        fontName="Helvetica-Bold",
        fontSize=8,
        leading=11,
        textColor=WHITE,
    )
    s["td"] = ParagraphStyle(
        "td",
        fontName="Helvetica",
        fontSize=8,
        leading=11,
        textColor=INK,
    )
    s["td_b"] = ParagraphStyle(
        "td_b",
        fontName="Helvetica-Bold",
        fontSize=8,
        leading=11,
        textColor=NAVY,
    )
    s["caption"] = ParagraphStyle(
        "caption",
        fontName="Helvetica-Oblique",
        fontSize=8,
        leading=11,
        textColor=MUTED,
        spaceAfter=10,
        spaceBefore=2,
    )
    s["footer"] = ParagraphStyle(
        "footer",
        fontName="Helvetica",
        fontSize=8,
        textColor=MUTED,
        alignment=TA_LEFT,
    )
    s["toc"] = ParagraphStyle(
        "toc",
        fontName="Helvetica",
        fontSize=10,
        leading=16,
        textColor=INK,
        leftIndent=6,
    )
    s["step_num"] = ParagraphStyle(
        "step_num",
        fontName="Helvetica-Bold",
        fontSize=10,
        leading=13,
        textColor=GOLD,
        spaceBefore=8,
        spaceAfter=2,
    )
    s["quote"] = ParagraphStyle(
        "quote",
        fontName="Helvetica-Oblique",
        fontSize=10,
        leading=14,
        textColor=NAVY,
        leftIndent=14,
        rightIndent=10,
        spaceBefore=6,
        spaceAfter=10,
    )
    return s


S = styles()
PW = 7.0 * inch  # printable width with 0.75" margins on letter


def P(text, style="body"):
    return Paragraph(text, S[style])


def bullets(items):
    return ListFlowable(
        [ListItem(P(i, "bullet"), leftIndent=12, bulletColor=GOLD) for i in items],
        bulletType="bullet",
        start="•",
        leftIndent=16,
        bulletFontName="Helvetica",
        bulletFontSize=9,
        spaceAfter=8,
    )


def code_block(lines: str):
    html = lines.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    html = html.replace("\n", "<br/>")
    return Paragraph(html, S["code"])


def table(headers, rows, widths, first_col_bold=True):
    head = [Paragraph(h, S["th"]) for h in headers]
    data = [head]
    for row in rows:
        cells = []
        for i, cell in enumerate(row):
            style = S["td_b"] if (first_col_bold and i == 0) else S["td"]
            cells.append(Paragraph(str(cell), style))
        data.append(cells)
    t = Table(data, colWidths=widths, repeatRows=1)
    t.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), NAVY),
                ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
                ("BACKGROUND", (0, 1), (-1, -1), CREAM),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [CREAM, ROW]),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 5),
                ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ("GRID", (0, 0), (-1, -1), 0.3, RULE),
                ("LINEBELOW", (0, 0), (-1, 0), 1.2, GOLD),
            ]
        )
    )
    return t


def callout(title, body, fill=CREAM, bar=GOLD):
    inner = Table(
        [[P(f"<b>{title}</b>", "h3")], [P(body, "body")]],
        colWidths=[PW - 16],
    )
    inner.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), fill),
                ("LEFTPADDING", (0, 0), (-1, -1), 10),
                ("RIGHTPADDING", (0, 0), (-1, -1), 10),
                ("TOPPADDING", (0, 0), (0, 0), 8),
                ("BOTTOMPADDING", (0, -1), (-1, -1), 6),
                ("LINEBEFORE", (0, 0), (0, -1), 4, bar),
            ]
        )
    )
    return inner


def header_footer(canvas, doc):
    canvas.saveState()
    w, h = letter
    canvas.setFillColor(NAVY)
    canvas.rect(0, h - 28, w, 28, fill=1, stroke=0)
    canvas.setFillColor(GOLD)
    canvas.rect(0, h - 31, w, 3, fill=1, stroke=0)
    canvas.setFillColor(WHITE)
    canvas.setFont("Helvetica", 8)
    canvas.drawString(0.75 * inch, h - 19, "LOONA  ·  Tu Jarvis personal")
    canvas.setFont("Helvetica", 8)
    canvas.drawRightString(w - 0.75 * inch, h - 19, "Guía de construcción  ·  12 ago 2026")
    canvas.setFillColor(NAVY)
    canvas.rect(0, 0, w, 26, fill=1, stroke=0)
    canvas.setFillColor(GOLD)
    canvas.rect(0, 26, w, 2, fill=1, stroke=0)
    canvas.setFillColor(WHITE)
    canvas.setFont("Helvetica", 8)
    canvas.drawString(0.75 * inch, 10, "Workspace herdr: LOONA  ·  /Users/imac/loona")
    canvas.drawRightString(w - 0.75 * inch, 10, f"Página {doc.page}")
    canvas.restoreState()


def cover_page(canvas, doc):
    header_footer(canvas, doc)


def build():
    story = []

    # ---------- COVER ----------
    hero_inner = Table(
        [
            [P("PROYECTO LOONA  ·  STUDIO OS  ·  AGOSTO 2026", "cover_kicker")],
            [
                P(
                    "Cómo construir tu propio Jarvis:<br/>instrucciones claras, repos reales y cero bait de DM",
                    "cover_title",
                )
            ],
            [
                P(
                    "Guía operativa para Chuy. Un asistente personal siempre encendido, "
                    "con voz, memoria, herramientas y guardrails — no un chatbot con nombre fancy.",
                    "cover_sub",
                )
            ],
        ],
        colWidths=[PW - 8],
    )
    hero_inner.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), NAVY),
                ("LEFTPADDING", (0, 0), (-1, -1), 16),
                ("RIGHTPADDING", (0, 0), (-1, -1), 16),
                ("TOPPADDING", (0, 0), (0, 0), 16),
                ("BOTTOMPADDING", (0, -1), (-1, -1), 16),
                ("TOPPADDING", (0, 1), (-1, -1), 4),
                ("LINEBELOW", (0, -1), (-1, -1), 5, GOLD),
            ]
        )
    )
    story.append(hero_inner)
    story.append(Spacer(1, 12))
    meta = table(
        ["Campo", "Valor"],
        [
            ["Nombre del agente", "LOONA"],
            ["Workspace herdr", "LOONA  (wB)  ·  /Users/imac/loona"],
            ["Máquina de trabajo", "iMac Intel Core i5-6500  ·  24 GB RAM  ·  macOS 12.7.6 Monterey"],
            ["Ya instalado", "Python 3.14  ·  Node 24.18  ·  Ollama 0.32  ·  herdr 0.8"],
            ["Método de investigación", "X (Latest, 6–12 ago 2026) + README oficiales de cada repo"],
            ["Filtro", "Se descartaron tweets que piden DM / “comenta JARVIS” / pack privado"],
            ["Recomendación principal", "OpenClaw (cerebro 24/7) + Personal Jarvis (voz y escritorio)"],
        ],
        [2.1 * inch, 4.9 * inch],
        first_col_bold=True,
    )
    story.append(meta)
    story.append(
        P(
            "Este PDF no es un resumen de hype. Cada paso se puede ejecutar hoy en esta máquina. "
            "Cuando un stack exige Apple Silicon o GPU NVIDIA, se marca como opcional o futuro.",
            "note",
        )
    )

    story.append(P("Contenido", "h1"))
    toc = [
        "1. Introducción — qué es un Jarvis de verdad",
        "2. Radar de X (agosto 2026) — repos públicos, sin DM",
        "3. Equipo y capacidades (hardware)",
        "4. Software, internet e IA",
        "5. Arquitectura recomendada para LOONA",
        "6. Paso a paso A — OpenClaw, el cerebro siempre encendido",
        "7. Paso a paso B — Personal Jarvis, voz y control del Mac",
        "8. Paso a paso C — voz local (Hugging Face speech-to-speech)",
        "9. Identidad, memoria y guardrails de LOONA",
        "10. Primeras 24 horas — checklist de prueba",
        "11. Seguridad, costos y anti-patrones",
        "12. Fuentes y repos canónicos",
    ]
    for item in toc:
        story.append(P(item, "toc"))

    story.append(PageBreak())

    # ---------- 1 INTRO ----------
    story.append(P("1. Introducción — qué es un Jarvis de verdad", "h1"))
    story.append(
        P(
            "En X, “construye tu Jarvis” se volvió un género. La mayoría de esos posts no entregan "
            "un asistente: entregan un chatbot con wake word, o peor, un hilo que termina con "
            "“comenta JARVIS y te lo mando por DM”. Eso no es un proyecto. Es un lead magnet.",
            "lead",
        )
    )
    story.append(
        P(
            "Un Jarvis real no es un modelo. Es un sistema de cinco capas que trabaja por ti "
            "mientras no estás mirando la pantalla. Fluixo lo resumió bien el 12 de agosto de 2026: "
            "identidad, memoria, herramientas, triggers y guardrails. Sin herramientas solo habla. "
            "Sin memoria empieza de cero. Sin triggers tú sigues haciendo el trabajo. Sin guardrails "
            "es un riesgo.",
            "body",
        )
    )
    story.append(
        P(
            "“Everyone wants Jarvis. Most people build a chatbot with a cool name. That is not the same thing.” — @fluixoo, 12 ago 2026",
            "quote",
        )
    )
    story.append(P("Las cinco capas (criterio de diseño de LOONA)", "h2"))
    story.append(
        table(
            ["Capa", "Pregunta que responde", "Si falta"],
            [
                [
                    "Identidad",
                    "¿Quién es LOONA, para quién trabaja, con qué tono, qué nunca hace?",
                    "Suena genérico. Mezcla proyectos. No tiene criterio.",
                ],
                [
                    "Memoria",
                    "¿Qué debe recordar entre sesiones? Preferencias, gente, repos, vetos.",
                    "Cada mañana es un extraño. Repites el mismo briefing.",
                ],
                [
                    "Herramientas",
                    "¿Puede ejecutar? Archivos, terminal, calendario, browser, WhatsApp, código.",
                    "Es un chat. No un asistente.",
                ],
                [
                    "Triggers",
                    "¿Actúa sola? Cron, wake word, mensaje de Telegram, evento de calendario.",
                    "Tú sigues empujando cada tarea.",
                ],
                [
                    "Guardrails",
                    "¿Qué requiere tu sí? Pagos, publish, borrar, DM a terceros, keys.",
                    "Un error caro o un leak de secretos.",
                ],
            ],
            [1.15 * inch, 3.0 * inch, 2.85 * inch],
        )
    )
    story.append(
        P(
            "Definición de done de este proyecto: LOONA responde por voz o por Telegram, "
            "recuerda algo que le dijiste ayer, ejecuta al menos una herramienta real "
            "(archivo, comando o canal) y pide aprobación antes de cualquier acción irreversible.",
            "note",
        )
    )
    story.append(
        callout(
            "Por qué este PDF no te manda a “vibe-code Jarvis en 20 minutos”",
            "Riley Brown (@rileybrown) tiene un tutorial viral de julio 2026: Cursor + GPT-Realtime-2 "
            "y un prompt largo. Es útil como inspiración de tools, pero no es un repo configurable "
            "que puedas versionar, auditar y reabrir en un mes. LOONA necesita código público, "
            "config en disco y un camino de update. Por eso priorizamos repos MIT con installer "
            "y archivo de configuración, no hilos de “pégame este prompt”.",
        )
    )

    # ---------- 2 RADAR X ----------
    story.append(P("2. Radar de X (agosto 2026) — repos públicos, sin DM", "h1"))
    story.append(
        P(
            "Se buscaron tweets recientes (modo Latest) con combinaciones de “build your own Jarvis”, "
            "“personal AI assistant”, “openclaw”, “github.com” y equivalentes en español. "
            "Se excluyeron posts cuyo call-to-action es mandar DM, comentar una palabra o pedir "
            "un pack privado. Se priorizaron los que ya publican el enlace del repositorio.",
            "body",
        )
    )
    story.append(P("Repos que sí pasaron el filtro", "h2"))
    story.append(
        table(
            ["Repo", "Quién lo empuja en X", "Por qué importa para LOONA", "Veredicto"],
            [
                [
                    "openclaw/openclaw<br/>docs.openclaw.ai",
                    "@BuiltByNav, @sanjibxai, @YasKad4 (9–12 ago). ~385k stars.",
                    "Asistente self-hosted 24/7. Gateway + canales (Telegram, WhatsApp, Slack, iMessage). Skills y plugins. MIT. Configurable de verdad.",
                    "<b>CEREBRO BASE</b>",
                ],
                [
                    "PersonalJarvis /<br/>PersonalJarvis<br/>v1.3.0 · MIT",
                    "@PersonalJarvis (10–12 ago). Mac / Windows / Linux.",
                    "Voz, dictado, computer-use, wiki Markdown, wake word propio, Ollama local, Claude/Codex/Gemini como workers. Un comando de install.",
                    "<b>CAPA VOZ / DESKTOP</b>",
                ],
                [
                    "huggingface /<br/>speech-to-<br/>speech<br/>~11.6k stars",
                    "@Marco_Ramilli (8 ago). “Want to build your own Jarvis?”",
                    "Pipeline VAD → STT → LLM → TTS, API compatible con OpenAI Realtime. Local o híbrido. Piezas intercambiables.",
                    "Voz local avanzada",
                ],
                [
                    "MOVI85/flightdeck<br/>MIT",
                    "@Slevin_Fi (26 jul). Wake word “Jarvis”, 80+ skills.",
                    "HUD cinematográfico + Hermes Agent + Whisper local. El más “Iron Man”. Requiere macOS Apple Silicon para la mitad ambient.",
                    "Futuro (no este iMac)",
                ],
                [
                    "memovai/mimiclaw",
                    "@tom_doerr (10 ago). 21 likes, 25 bookmarks.",
                    "ESP32-S3 de ~5 USD + Telegram. Jarvis de hardware barato, no de escritorio.",
                    "Experimento hardware",
                ],
                [
                    "garrytan/gbrain",
                    "@SharavArora, @edsoehnel (abr 2026). CEO de YC.",
                    "Segundo cerebro persistente: meetings, mail, ideas, evidencia. Complemento de memoria, no el orquestador.",
                    "Memoria avanzada (fase 2)",
                ],
            ],
            [1.55 * inch, 1.55 * inch, 2.35 * inch, 1.55 * inch],
        )
    )
    story.append(
        P(
            "Tabla 1. Fuentes de X verificadas contra el README de cada repo el 12 de agosto de 2026.",
            "caption",
        )
    )

    story.append(P("Menciones útiles pero incompletas", "h2"))
    story.append(
        bullets(
            [
                "<b>@fluixoo</b> (12 ago): el marco de 5 capas. Sin repo. Se adopta como doctrina, no como código.",
                "<b>@HernandezFreddy</b> (12 ago): Mac + Firecrawl + OpenClaw. Video corto, sin repo propio; confirma el stack OpenClaw.",
                "<b>@rileybrown</b> (1 jul): tutorial Cursor + GPT-Realtime-2, 1.3k bookmarks. Buen patrón de tools, mal como base versionable.",
                "<b>@nikhilachale/GWEN</b>: voz + Claude + ElevenLabs + macOS. Repo real, pero menos maduro que Personal Jarvis.",
                "<b>@tominaga-h/jarvis-shell</b>: shell AI-nativo en Rust. Interesante, no es un asistente de vida.",
                "<b>iboss21/free-jarvis-template (REGES)</b>: tweet del 11 ago. Wizard configurable, pero Windows-first y voz “needs binaries”. No es el camino de este iMac.",
            ]
        )
    )

    story.append(P("Lo que se descartó a propósito", "h2"))
    story.append(
        table(
            ["Patrón en X", "Por qué se tira", "Ejemplo de esta semana"],
            [
                [
                    "“Comenta JARVIS / drop a 🔥 / DM me la palabra”",
                    "El código no es público. No se puede auditar, clonar ni actualizar. Suele ser un funnel.",
                    "Cientos de hilos de “build your Jarvis” que terminan en inbox.",
                ],
                [
                    "Repo de 1 archivo Python “voice assistant”",
                    "speech_recognition + webbrowser.open. Demo de facultad, no sistema.",
                    "@AyaanAli___ / @Naveen_Royallll — válidos como hobby, no como LOONA.",
                ],
                [
                    "Pack privado en GitHub privado",
                    "Si el autor dice “está en GitHub pero lo tengo private, DM me”, no es configurable para ti.",
                    "@SteviKelly, 12 ago: packet de founder command, repo privado.",
                ],
                [
                    "Flightdeck / AIRI como día 1",
                    "Espectacular, pero asume Apple Silicon, Hermes, ElevenLabs y paciencia de permisos.",
                    "@Stefan_3D_AI (AIRI) y @Slevin_Fi (Flightdeck).",
                ],
            ],
            [1.9 * inch, 2.7 * inch, 2.4 * inch],
        )
    )

    # ---------- 3 HARDWARE ----------
    story.append(P("3. Equipo y capacidades (hardware)", "h1"))
    story.append(
        P(
            "Un Jarvis no pide el mismo hierro si el cerebro vive en la nube o en tu disco. "
            "Esta sección separa lo mínimo para arrancar hoy, lo recomendado para voz cómoda, "
            "y lo que este iMac sí / no puede hacer.",
            "body",
        )
    )
    story.append(P("Tu máquina actual (medida el 12 ago 2026)", "h2"))
    story.append(
        table(
            ["Componente", "Lo que hay", "Implicación para Jarvis"],
            [
                [
                    "CPU",
                    "Intel Core i5-6500 @ 3.20 GHz (4 núcleos, 2015–16)",
                    "Sirve para orquestar. No sirve para modelos locales grandes con latencia de conversación.",
                ],
                [
                    "RAM",
                    "24 GB",
                    "Holgada para OpenClaw + browser + herdr. Justa para un modelo local 7B cuantizado + STT.",
                ],
                [
                    "GPU",
                    "Intel HD 530 integrada (sin CUDA, sin Apple Neural Engine)",
                    "Whisper/TTS locales serán lentos. mlx-audio y Flightdeck nativo no aplican.",
                ],
                [
                    "OS",
                    "macOS 12.7.6 Monterey",
                    "OpenClaw y Personal Jarvis declaran soporte Mac. Evita stacks que piden Sequoia + Swift reciente.",
                ],
                [
                    "Audio",
                    "Micrófono y parlantes del iMac",
                    "Suficiente para el día 1. Un mic USB con mute físico es el primer upgrade barato.",
                ],
            ],
            [1.3 * inch, 2.7 * inch, 3.0 * inch],
        )
    )

    story.append(P("Tres niveles de equipo", "h2"))
    story.append(
        table(
            ["Nivel", "Equipo", "Qué Jarvis te da", "Costo marginal"],
            [
                [
                    "A — Arranque (este iMac)",
                    "iMac actual + mic + internet estable + (opcional) iPhone para Telegram",
                    "Cerebro 24/7 en OpenClaw, voz de escritorio con Personal Jarvis, modelos cloud (Grok/Claude/Gemini). Local solo para cosas chicas (Ollama 3B–7B).",
                    "$0. Ya lo tienes.",
                ],
                [
                    "B — Voz cómoda",
                    "Mic USB (Jabra/Elgato Wave) + audífonos + UPS si lo dejas 24/7 + disco SSD libre ≥ 40 GB",
                    "Menos errores de wake word, dictado usable, modelos STT/TTS cacheados sin llenar el disco.",
                    "USD 40–150",
                ],
                [
                    "C — Jarvis local de verdad",
                    "Apple Silicon 32 GB+ (M-series) o PC/NVIDIA 12 GB VRAM. O un MiniPC/NUC siempre encendido.",
                    "Speech-to-speech local, Flightdeck completo, 14B–32B en casa, privacidad máxima.",
                    "USD 800–2 500. No es el día 1.",
                ],
            ],
            [1.45 * inch, 2.15 * inch, 2.15 * inch, 1.25 * inch],
        )
    )
    story.append(
        callout(
            "Regla honesta para este iMac",
            "No intentes “todo local” el primer fin de semana. El cuello de botella no es la RAM: "
            "es la CPU de 2015 y la GPU integrada. LOONA debe pensar en la nube (Grok / Claude / Gemini, "
            "que ya pagas) y usar el Mac como orquestador, micrófono y ejecutor de tools. "
            "Ollama se reserva para pruebas privadas y fallback, no para la voz en tiempo real.",
            fill=colors.HexColor("#FFF6E0"),
            bar=WARN,
        )
    )
    story.append(Spacer(1, 8))
    story.append(P("Periféricos y “capacidades” que sí importan", "h2"))
    story.append(
        bullets(
            [
                "<b>Micrófono:</b> el del iMac sirve. Si hay eco de los parlantes, usa audífonos. El wake word odia el playback.",
                "<b>Red:</b> 20 Mbps simétricos bastan. Lo crítico es latencia estable, no el gigabit. Evita Wi-Fi saturado si usas voz cloud.",
                "<b>Siempre encendido:</b> un Jarvis de verdad no se apaga. Deja el iMac despierto o mueve OpenClaw a un MiniPC/VPS más adelante.",
                "<b>Teléfono:</b> Telegram o WhatsApp son el “HUD de bolsillo”. No necesitas app nativa el día 1.",
                "<b>Disco:</b> reserva 15–40 GB para modelos Whisper/Piper/Ollama. No los descargues todos.",
                "<b>Cámara:</b> opcional. Solo si más tarde quieres “qué hay en mi pantalla” o computer-use con visión.",
            ]
        )
    )

    # ---------- 4 SOFTWARE ----------
    story.append(P("4. Software, internet e IA", "h1"))
    story.append(P("Ya lo tienes (no instales de más)", "h2"))
    story.append(
        table(
            ["Pieza", "Versión vista", "Rol en LOONA"],
            [
                ["herdr", "0.8.0", "Workspace LOONA. Panes para OpenClaw, Personal Jarvis, logs."],
                ["Node.js", "24.18.0", "Runtime de OpenClaw (pide 22.22.3+ / 24.15+ / 25.9+). Perfecto."],
                ["Python", "3.14.6", "Personal Jarvis pide 3.11+. Si 3.14 rompe wheels, usa 3.12 vía pyenv/brew."],
                ["Ollama", "0.32.0 (cliente)", "Cerebro local opcional. Hoy no hay daemon corriendo: hay que levantarlo."],
                ["Grok / SuperGrok", "pagado", "Cerebro fuerte para razonar, orquestar y verificar."],
                ["Claude + Codex", "panes herdr", "Workers de misiones largas (código, docs)."],
                ["Git + navegador", "sistema", "Clonar repos, dashboard de OpenClaw, HUD."],
            ],
            [1.6 * inch, 1.8 * inch, 3.6 * inch],
        )
    )

    story.append(P("Qué hay que instalar", "h2"))
    story.append(
        table(
            ["Software", "Para qué", "Obligatorio día 1?", "Costo"],
            [
                ["OpenClaw (npm / install.sh)", "Gateway 24/7, canales, skills", "Sí", "Gratis (MIT). Pagas el modelo."],
                ["Personal Jarvis", "Voz, dictado, mouse/teclado, wiki", "Sí, si quieres hablarle al iMac", "Gratis (MIT)."],
                ["Git (si faltara)", "Clonar y versionar LOONA", "Sí", "Gratis"],
                ["Ollama + qwen2.5:3b o 7b", "Fallback local / privacidad", "Recomendado", "Gratis"],
                ["Telegram BotFather", "Canal de bolsillo de LOONA", "Recomendado", "Gratis"],
                ["Cuenta xAI / Anthropic / Google / OpenAI", "Cerebro cloud", "Sí, una basta", "Ya pagado o pay-per-token"],
                ["ElevenLabs / Edge-TTS / Piper", "Voz hablada", "Opcional", "Piper/edge-tts = $0"],
                ["Firecrawl / Exa", "Web search estructurado", "Fase 2", "Free tier o API"],
                ["Obsidian", "Leer la wiki de memoria en humano", "Opcional", "Gratis"],
                ["Docker", "Solo si quieres speech-to-speech aislado", "No", "Gratis"],
            ],
            [1.85 * inch, 1.85 * inch, 1.7 * inch, 1.6 * inch],
        )
    )

    story.append(P("Cuentas e internet (mapa de APIs)", "h2"))
    story.append(
        table(
            ["Servicio", "Se usa para", "Dónde vive la key", "Regla"],
            [
                ["xAI / Grok", "Razonamiento, verify, copy", "Keychain / .env fuera de git", "Preferido del studio"],
                ["Anthropic Claude", "Misiones largas, código", "Igual", "Worker, no default 24/7 si el costo pica"],
                ["Google Gemini", "Barato y multimodal", "Igual", "Buen default de OpenClaw"],
                ["OpenAI Realtime", "Voz sub-segundo", "Igual", "Opcional. Caro si dejas el mic abierto"],
                ["Telegram Bot API", "Hablarle a LOONA del celular", "openclaw config", "El canal más rápido de setupear"],
                ["WhatsApp (OpenClaw)", "Canal de vida real", "pairing + número", "Fase 2. Más fricción que Telegram"],
                ["Ollama local", "Datos que no quieres subir", "localhost:11434", "Sin key"],
            ],
            [1.55 * inch, 1.7 * inch, 1.85 * inch, 1.9 * inch],
        )
    )
    story.append(
        P(
            "Nunca pegues API keys en un tweet, en un prompt de agente público, ni en el repo. "
            "Personal Jarvis las guarda en el llavero del sistema. OpenClaw usa su propio state dir "
            "(~/.openclaw). Añade .env y jarvis.toml con secretos al .gitignore desde el minuto uno.",
            "note",
        )
    )

    # ---------- 5 ARCHITECTURE ----------
    story.append(P("5. Arquitectura recomendada para LOONA", "h1"))
    story.append(
        P(
            "No instales cuatro Jarvis a la vez. Eso es el anti-patrón de la banda: cuatro agentes "
            "peleando el mismo write-path. LOONA tiene un solo nombre, dos procesos, un contrato.",
            "body",
        )
    )
    story.append(
        code_block(
            "TU (voz / Telegram / herdr)\n"
            "  |\n"
            "  +-- Personal Jarvis  ->  oye, habla, dicta, mouse, wiki local\n"
            "  |         |\n"
            "  |         +-- (tareas pesadas) Claude Code / Codex / Gemini CLI\n"
            "  |\n"
            "  +-- OpenClaw Gateway  ->  24/7, skills, cron, canales\n"
            "            |\n"
            "            +-- Cerebro: Grok o Gemini (cloud) + Ollama (fallback)\n"
            "            +-- Memoria: Markdown (~/.openclaw + wiki LOONA)\n"
            "            +-- Canales: Telegram ahora / WhatsApp despues\n"
            "            +-- Tools: exec, browser, files, calendar, scripts"
        )
    )
    story.append(P("Por qué este corte (y no Flightdeck hoy)", "h2"))
    story.append(
        bullets(
            [
                "<b>OpenClaw</b> es lo que X llama “el Jarvis que de verdad existe” en 2026: self-hosted, MIT, canales, skills, un Gateway. Encaja con Node 24 que ya tienes.",
                "<b>Personal Jarvis</b> es el único desktop voice stack maduro, multi-OS, con installer de un comando, wake word configurable (la pondremos en “Loona”) y computer-use.",
                "<b>Flightdeck</b> es el más bonito, pero sus apps nativas (wake, orb, gestures) son Swift/macOS Apple Silicon. En este iMac Intel perderías la mitad ambient.",
                "<b>speech-to-speech</b> se añade cuando la voz cloud moleste o quieras offline. No bloquea el día 1.",
            ]
        )
    )
    story.append(
        callout(
            "Contrato de la banda (founder-studio)",
            "Un write-path por proceso. OpenClaw es dueño de canales y cron. Personal Jarvis es dueño "
            "del micrófono y del escritorio. Grok verifica. Nadie declara “ya quedó” sin una prueba: "
            "un mensaje respondido, un archivo creado, o una URL / log. Free-first: Piper/edge-tts y "
            "Ollama antes de ElevenLabs o un VPS nuevo.",
        )
    )

    # ---------- 6 OPENCLAW ----------
    story.append(P("6. Paso a paso A — OpenClaw, el cerebro siempre encendido", "h1"))
    story.append(
        P(
            "Tiempo estimado: 15–25 minutos. Resultado: un Gateway en el puerto 18789, un dashboard "
            "en el browser y LOONA contestando en el Control UI. Después, Telegram en el celular.",
            "body",
        )
    )

    story.append(P("PASO A1 — Abre el workspace correcto", "step_num"))
    story.append(
        P(
            "El space herdr <b>LOONA</b> ya está creado (id wB) con cwd /Users/imac/loona. "
            "Trabaja ahí, no en likinya. En la TUI: click en LOONA, o <font face='Courier'>ctrl+b</font> "
            "luego <font face='Courier'>w</font>.",
            "body",
        )
    )
    story.append(
        code_block(
            "cd /Users/imac/loona\n"
            "herdr workspace list          # debe aparecer LOONA focused\n"
            "node --version                # v24.18.0 o superior"
        )
    )

    story.append(P("PASO A2 — Instala OpenClaw", "step_num"))
    story.append(
        P(
            "Como ya gestionas Node, puedes ir directo a npm. El installer oficial también instala Node "
            "si faltara. Lee el script antes de pipearlo a bash si te da cosa (es open source).",
            "body",
        )
    )
    story.append(
        code_block(
            "# Opción recomendada en esta máquina (Node ya está):\n"
            "npm install -g openclaw@latest --allow-scripts openclaw\n"
            "\n"
            "# Alternativa oficial (macOS):\n"
            "# curl -fsSL https://openclaw.ai/install.sh | bash\n"
            "\n"
            "openclaw --version\n"
            "openclaw doctor"
        )
    )
    story.append(
        P(
            "Si npm 12 bloquea lifecycle scripts, el flag --allow-scripts openclaw es obligatorio. "
            "Documentado en docs.openclaw.ai/install.",
            "note",
        )
    )

    story.append(P("PASO A3 — Onboarding (modelo + daemon)", "step_num"))
    story.append(
        code_block("openclaw onboard --install-daemon")
    )
    story.append(P("En el wizard, elige en este orden:", "body"))
    story.append(
        bullets(
            [
                "<b>Nombre del agente:</b> LOONA (no “Jarvis”, no “Molty”).",
                "<b>Provider:</b> el que ya pagas. Grok/xAI si el conector está; si no, Gemini (barato) o Anthropic.",
                "<b>API key:</b> pégala solo en el wizard. No la dejes en un .txt del Desktop.",
                "<b>Daemon:</b> sí. En macOS instala un LaunchAgent para que sobreviva logout/reboot.",
                "<b>Canales:</b> salta WhatsApp en el primer pase. Telegram viene en A6.",
                "<b>Skills extra / plugins:</b> skip. Vuelves con <font face='Courier'>openclaw configure</font>.",
            ]
        )
    )

    story.append(P("PASO A4 — Verifica el Gateway", "step_num"))
    story.append(
        code_block(
            "openclaw gateway status     # listening :18789\n"
            "openclaw dashboard          # abre el Control UI\n"
            "openclaw doctor             # debe quedar verde"
        )
    )
    story.append(
        P(
            "En el Control UI escribe: “Eres LOONA. Confirma tu nombre y dime tres tools que tienes.” "
            "Si responde, el cerebro está vivo. Si no, <font face='Courier'>openclaw gateway status</font> "
            "y revisa la key del provider.",
            "body",
        )
    )

    story.append(P("PASO A5 — Identidad en disco (soul + memoria)", "step_num"))
    story.append(
        P(
            "OpenClaw guarda el workspace del agente en su state dir. Crea además un cerebro canónico "
            "dentro del repo LOONA para que la banda (Grok, Codex, Claude) lea la misma verdad.",
            "body",
        )
    )
    story.append(
        code_block(
            "mkdir -p /Users/imac/loona/docs /Users/imac/loona/identity\n"
            "# Crea identity/SOUL.md  (quién es, qué hace, qué nunca hace)\n"
            "# Crea identity/MEMORY.md (hechos estables: zona MTY, studio, proyectos)\n"
            "# Crea docs/BANDA_CEREBRO_LOONA.md  (hecho / falta / sigue)"
        )
    )
    story.append(
        P(
            "Pégalo en el system / workspace de OpenClaw (el wizard y "
            "<font face='Courier'>openclaw configure</font> te dejan apuntar instrucciones). "
            "La sección 9 de este PDF trae el texto listo para copiar.",
            "note",
        )
    )

    story.append(P("PASO A6 — Telegram (el HUD de bolsillo)", "step_num"))
    story.append(
        bullets(
            [
                "En Telegram, habla con <b>@BotFather</b> → /newbot → nombre visible “LOONA” → username tipo loona_jarvis_bot.",
                "Copia el token. Nadie más lo ve.",
                "En el host: conecta el canal Telegram (docs.openclaw.ai/channels/telegram). Suele ser el canal más rápido.",
                "Mándale un “hola” desde tu cuenta. OpenClaw hace pairing por defecto con senders desconocidos.",
                "Aprueba el pairing: <font face='Courier'>openclaw pairing approve telegram &lt;código&gt;</font>.",
                "Prueba: “recuerda que mi zona horaria es América/Monterrey y el proyecto activo de contenido es Likinya”.",
            ]
        )
    )

    story.append(P("PASO A7 — Primera herramienta útil (no un demo)", "step_num"))
    story.append(
        P(
            "Un Jarvis de verdad hace una cosa molesta por ti. Elige UNA, no diez:",
            "body",
        )
    )
    story.append(
        bullets(
            [
                "“Lista los workspaces de herdr y dime cuál está focused.”",
                "“Léeme docs/BANDA_CEREBRO_LOONA.md y dime el P0.”",
                "“Cada día a las 8:00 MTY, mándame por Telegram las 3 tareas abiertas del studio.” (cron de OpenClaw)",
                "“Cuando te escriba ‘radar’, corre un resumen de menciones y no publiques nada.”",
            ]
        )
    )
    story.append(
        P(
            "No le des shell irrestricto el día 1. Lee docs.openclaw.ai/gateway/sandboxing y "
            "docs.openclaw.ai/gateway/security antes de exponer el Gateway fuera de localhost. "
            "DM-capable channels tratan mensajes inbound como input no confiable. Eso no es paranoia: "
            "es el README oficial.",
            "note",
        )
    )

    # ---------- 7 PERSONAL JARVIS ----------
    story.append(P("7. Paso a paso B — Personal Jarvis, voz y control del Mac", "h1"))
    story.append(
        P(
            "Tiempo estimado: 20–40 minutos (incluye descargas de modelos de voz). "
            "Resultado: una app de escritorio que despierta con la palabra <b>Loona</b>, "
            "responde en voz alta, dicta en cualquier campo y puede mover mouse/teclado.",
            "body",
        )
    )
    story.append(
        P(
            "Repo canónico: https://github.com/PersonalJarvis/PersonalJarvis  ·  MIT  ·  v1.3.0+  ·  Python 3.11+",
            "note",
        )
    )

    story.append(P("PASO B1 — Instala (un comando)", "step_num"))
    story.append(
        P(
            "El installer crea un venv, instala deps, precarga modelos de voz y lanza la app. "
            "No pide nada en la terminal: el setup ocurre dentro de la app (idioma, wake word, keys).",
            "body",
        )
    )
    story.append(
        code_block(
            "# Lee el script primero si quieres (recomendado):\n"
            "curl -fsSL https://raw.githubusercontent.com/PersonalJarvis/\\\n"
            "  PersonalJarvis/main/install/install.sh | less\n"
            "\n"
            "# Luego instala:\n"
            "curl -fsSL https://raw.githubusercontent.com/PersonalJarvis/\\\n"
            "  PersonalJarvis/main/install/install.sh | bash"
        )
    )
    story.append(
        P(
            "Alternativa pipx, aislada: <font face='Courier'>pipx install personal-jarvis &amp;&amp; jarvis serve</font>. "
            "O clone manual en /Users/imac/loona/vendor/PersonalJarvis si quieres el código al lado del proyecto.",
            "body",
        )
    )

    story.append(P("PASO B2 — Setup dentro de la app", "step_num"))
    story.append(
        bullets(
            [
                "<b>Idioma:</b> auto (español + inglés). LOONA debe espejear el idioma en el que le hablas.",
                "<b>Wake word:</b> vacío por defecto a propósito. Pon <b>loona</b>. Nada de “Jarvis” — ese nombre está saturado y se activa con videos de Iron Man.",
                "<b>Cerebro (brain tier):</b> usa una key que ya pagas (Gemini / Claude / OpenAI / OpenRouter). En este iMac no pongas el realtime local experimental (pide ~12 GB de GPU/unified memory).",
                "<b>STT:</b> empieza con un provider cloud barato (Groq/Gemini) para que la latencia no te frustre. Pasa a faster-whisper local solo si te molesta subir audio.",
                "<b>TTS:</b> Gemini Flash TTS o Piper local. Evita ElevenLabs hasta que la voz “barata” te moleste de verdad.",
                "<b>Workers:</b> si ya tienes Claude Code / Codex, conéctalos. Las misiones pesadas salen del router a un worktree aislado y un critic las revisa.",
            ]
        )
    )

    story.append(P("PASO B3 — Config fino (opcional pero correcto)", "step_num"))
    story.append(
        P(
            "No necesitas archivo. Si lo quieres versionable (sin secretos), copia el ejemplo oficial:",
            "body",
        )
    )
    story.append(
        code_block(
            "[profile]\n"
            "language = \"auto\"\n"
            "\n"
            "[trigger.wake_word]\n"
            "phrase = \"loona\"\n"
            "engine = \"auto\"\n"
            "\n"
            "[stt]\n"
            "provider = \"groq-api\"          # o gemini-api / faster-whisper\n"
            "\n"
            "[tts]\n"
            "provider = \"gemini-flash-tts\"\n"
            "fallback = \"piper\""
        )
    )
    story.append(
        P(
            "Overrides por ENV: JARVIS__SECTION__KEY=…  ·  Las keys NUNCA van en este toml; viven en el llavero o en .env.",
            "note",
        )
    )

    story.append(P("PASO B4 — Permisos de macOS (el paso que todos se saltan)", "step_num"))
    story.append(
        bullets(
            [
                "Sistema → Seguridad y privacidad → Micrófono: permite Personal Jarvis.",
                "Accesibilidad: permite si vas a usar computer-use (abrir apps, clicks).",
                "Automatización / Accesibilidad: macOS 12 pregunta la primera vez. Si dices que no, el mouse “no hace nada” y parece un bug.",
                "Prueba de audio: di “Loona” y luego “qué hora es”. Si no despierta, baja el umbral o acércate al mic.",
            ]
        )
    )

    story.append(P("PASO B5 — Primeras frases que deben funcionar", "step_num"))
    story.append(
        table(
            ["Dices", "Debe pasar"],
            [
                ["“Loona, recuérdate: Chuy trabaja en Monterrey y el proyecto P1 es Likinya.”", "Queda en la Knowledge Wiki (Markdown en disco)."],
                ["“Ábreme el workspace /Users/imac/loona en el Finder.”", "Computer-use: se ve un borde en pantalla mientras opera."],
                ["“Dicta esto” + hold key", "El texto limpio cae en el campo con foco."],
                ["“Investiga X y déjame un reporte en Outputs.”", "Misión aislada + critic. Tarda minutos. No es silencio: debe decir qué está haciendo."],
            ],
            [3.3 * inch, 3.7 * inch],
        )
    )

    story.append(P("PASO B6 — Cómo convive con OpenClaw (sin pelearse)", "step_num"))
    story.append(
        bullets(
            [
                "Personal Jarvis = cuerpo (mic, voz, escritorio).",
                "OpenClaw = sistema nervioso 24/7 (Telegram, cron, skills cuando el iMac está idle).",
                "No conectes los dos al mismo bot de Telegram el día 1.",
                "Si quieres que la voz dispare al Gateway, hazlo después con un tool/MCP explícito. No lo improvises.",
                "La wiki de Personal Jarvis y SOUL.md de LOONA deben decir lo mismo sobre vetos (no política, no publish sin OK, no keys).",
            ]
        )
    )

    # ---------- 8 SPEECH TO SPEECH ----------
    story.append(P("8. Paso a paso C — voz local (Hugging Face speech-to-speech)", "h1"))
    story.append(
        P(
            "Haz esto solo cuando A y B ya contestan. Es el camino para hablarle a LOONA sin mandar "
            "audio a un proveedor, o para tener latencia tipo “Realtime” con piezas open source.",
            "body",
        )
    )
    story.append(
        P(
            "Repo: https://github.com/huggingface/speech-to-speech  ·  Apache-2.0  ·  "
            "pip install speech-to-speech  ·  Python 3.10+",
            "note",
        )
    )
    story.append(P("Qué es", "h2"))
    story.append(
        P(
            "Un pipeline modular: Silero VAD → STT (Parakeet TDT por default) → LLM (cualquier "
            "OpenAI-compatible, incluido llama.cpp / vLLM / Ollama vía proxy) → TTS (Qwen3-TTS). "
            "Expone ws://localhost:8765/v1/realtime, compatible con clientes OpenAI Realtime. "
            "En este iMac Intel, mlx-audio no aplica; usa los backends CPU/GGML.",
            "body",
        )
    )
    story.append(P("PASO C1 — Instala el paquete", "step_num"))
    story.append(
        code_block(
            "python3 -m venv /Users/imac/loona/.venv-s2s\n"
            "source /Users/imac/loona/.venv-s2s/bin/activate\n"
            "pip install -U pip\n"
            "pip install speech-to-speech"
        )
    )
    story.append(P("PASO C2 — Modo híbrido (recomendado en Intel)", "step_num"))
    story.append(
        P(
            "STT y TTS locales, cerebro cloud. Es el mejor tradeoff en un i5-6500:",
            "body",
        )
    )
    story.append(
        code_block(
            "export OPENAI_API_KEY=...          # o HF_TOKEN / GEMINI / etc.\n"
            "speech-to-speech local \\\n"
            "  --stt parakeet-tdt \\\n"
            "  --llm_backend responses-api \\\n"
            "  --model_name gpt-4o-mini \\\n"
            "  --tts qwen3"
        )
    )
    story.append(P("PASO C3 — Modo 100% local (lento en esta máquina)", "step_num"))
    story.append(
        code_block(
            "# Terminal 1 — sirve un modelo chico\n"
            "ollama serve\n"
            "ollama pull qwen2.5:3b-instruct\n"
            "\n"
            "# Si usas llama.cpp en vez de Ollama:\n"
            "# llama-server -hf ggml-org/gemma-4-E4B-it-GGUF -np 2 -c 8192\n"
            "\n"
            "# Terminal 2\n"
            "speech-to-speech local \\\n"
            "  --stt parakeet-tdt \\\n"
            "  --llm_backend chat-completions \\\n"
            "  --model_name qwen2.5:3b-instruct \\\n"
            "  --responses_api_base_url http://127.0.0.1:11434/v1 \\\n"
            "  --responses_api_api_key ollama \\\n"
            "  --tts qwen3"
        )
    )
    story.append(
        P(
            "La primera corrida descarga checkpoints (varios GB). Hazla con internet. "
            "Después puedes intentar HF_HUB_OFFLINE=1. Si la latencia supera ~8–10 s por turno, "
            "no es que esté roto: es el i5. Vuelve al modo híbrido.",
            "note",
        )
    )

    # ---------- 9 IDENTITY ----------
    story.append(P("9. Identidad, memoria y guardrails de LOONA", "h1"))
    story.append(
        P(
            "Esto es lo que separa un clone de Jarvis de un agente tuyo. Cópialo a "
            "<font face='Courier'>/Users/imac/loona/identity/SOUL.md</font> y conéctalo "
            "como instrucciones de sistema en OpenClaw y como wiki seed en Personal Jarvis.",
            "body",
        )
    )
    story.append(P("Texto canónico de identidad (pegar tal cual y editar lo marcado)", "h2"))
    story.append(
        code_block(
            "# SOUL.md — LOONA\n"
            "Eres LOONA, asistente personal de Chuy (abogado-constructor de sistemas de IA).\n"
            "Zona: Monterrey (América/Monterrey). Idioma: español claro, skills/código en EN si aplica.\n"
            "\n"
            "## Qué eres\n"
            "- Sistema de 5 capas: identidad, memoria, tools, triggers, guardrails.\n"
            "- Haces trabajo. No narres que “podrías” hacerlo.\n"
            "- Reporta siempre: DONE | BLOCKED | NEED_HUMAN | IN_PROGRESS + evidencia.\n"
            "\n"
            "## Proyectos\n"
            "- P1 Likinya (no lo toques salvo que Chuy lo pida en esa sesión).\n"
            "- Este workspace es LOONA. No mezcles write-paths con likinya.\n"
            "\n"
            "## Nunca\n"
            "- Publicar a redes, pagar, o borrar sin NEED_HUMAN.\n"
            "- Inventar URLs, posts live, o “ya quedó” sin proof.\n"
            "- Guardar passwords en el repo. No leer .env en voz alta.\n"
            "- Política, hard-sell, o clonar personas reales.\n"
            "- Pedirle a nadie que te mande un DM con una palabra mágica.\n"
            "\n"
            "## Cómo decides\n"
            "- Free / ya pagado primero (Grok, Claude, Gemini, Ollama).\n"
            "- Una herramienta por turno si basta. No dispares 8 tools de adorno.\n"
            "- Si hay duda de irreversibilidad: pregunta. Una pregunta corta > un desastre."
        )
    )

    story.append(P("Memoria mínima (MEMORY.md)", "h2"))
    story.append(
        bullets(
            [
                "Owner: Chuy. Studio multi-agente (Grok lead, Claude browser, Codex docs, Agy media).",
                "Stack: herdr, Publora, Notion, Drive, Make, browser-use. Free-first.",
                "LOONA vive en /Users/imac/loona. Space herdr: LOONA.",
                "Hardware: iMac Intel 24 GB. No asumir Apple Silicon ni CUDA.",
                "Preferencia de canal: Telegram para móvil, voz solo cuando el iMac está delante.",
            ]
        )
    )

    story.append(P("Guardrails operativos (cópialos a OpenClaw + Personal Jarvis)", "h2"))
    story.append(
        table(
            ["Acción", "Política"],
            [
                ["Leer archivos del workspace LOONA", "Permitido"],
                ["Escribir docs / identity / notas", "Permitido"],
                ["Ejecutar comandos de solo lectura (status, list, doctor)", "Permitido"],
                ["Instalar paquetes, cambiar config de red, LaunchAgents", "Preguntar"],
                ["Computer-use (mouse/teclado) fuera del workspace", "Preguntar"],
                ["Publicar a IG/TT/X, mail masivo, WhatsApp a terceros", "Bloquear salvo OK explícito"],
                ["Leer o pronunciar API keys, .env, llavero", "Bloquear"],
                ["Autonomía 24/7 (cron)", "Solo jobs en lista blanca"],
            ],
            [3.3 * inch, 3.7 * inch],
        )
    )

    # ---------- 10 FIRST 24H ----------
    story.append(P("10. Primeras 24 horas — checklist de prueba", "h1"))
    story.append(
        P(
            "No sigas al Track C ni a Flightdeck hasta tener esta tabla en verde. "
            "Evidencia = captura, log o cita textual. “Creo que sí” no cuenta.",
            "body",
        )
    )
    story.append(
        table(
            ["#", "Prueba", "Cómo se ve el verde"],
            [
                ["1", "OpenClaw doctor + gateway status", "Listening :18789, sin errores de auth"],
                ["2", "Mensaje en Control UI", "LOONA responde con su nombre, no como “assistant”"],
                ["3", "Telegram pairing", "Un hola desde el celular recibe respuesta"],
                ["4", "Memoria", "Le dices un hecho, cierras, reabres, lo recuerda"],
                ["5", "Tool real", "Crea o lee un archivo en /Users/imac/loona/docs y te cita el path"],
                ["6", "Wake word “Loona”", "El orb/app despierta; no se activa con la tele"],
                ["7", "Voz ida y vuelta", "Pregunta hablada → respuesta hablada &lt; 8 s (cloud)"],
                ["8", "Guardrail", "Le pides publicar o leer un .env y se niega / pide OK"],
                ["9", "Costo", "Revisas el usage del provider. Nada se disparó en loop"],
                ["10", "Reboot", "Reinicias el iMac: el daemon de OpenClaw vuelve solo"],
            ],
            [0.45 * inch, 2.55 * inch, 4.0 * inch],
        )
    )

    story.append(P("Orden del día (no improvisar)", "h2"))
    story.append(
        bullets(
            [
                "<b>Mañana (90 min):</b> A1–A5. Para cuando el dashboard conteste.",
                "<b>Mediodía (45 min):</b> A6 Telegram + una skill/tool real.",
                "<b>Tarde (60 min):</b> B1–B5 voz. Si el installer pelea con Python 3.14, instala 3.12 y reintenta.",
                "<b>Noche (20 min):</b> SOUL.md + checklist 1–8. Escribe en BANDA_CEREBRO_LOONA.md qué faltó.",
                "<b>Día 2:</b> un cron útil. Luego speech-to-speech si la voz cloud te estorba.",
            ]
        )
    )

    # ---------- 11 SECURITY ----------
    story.append(P("11. Seguridad, costos y anti-patrones", "h1"))
    story.append(P("Seguridad (de los propios READMEs, no de un guru de X)", "h2"))
    story.append(
        bullets(
            [
                "OpenClaw: trata todo DM como input no confiable. Pairing on. No expongas el Gateway a internet sin el exposure runbook.",
                "Tools corren en el host salvo que actives sandbox. Eso significa que un prompt inyectado puede intentar ejecutar cosas.",
                "Personal Jarvis: wake word es local; el audio solo sale si elegiste STT cloud y después de dirigirte a LOONA.",
                "Flightdeck (si algún día): LAN only, no port-forward. El token del HUD no es la API key de Hermes.",
                "Nunca dejes OPENAI_API_KEY en un LaunchAgent world-readable. umask y permisos 600.",
                "Un archivo SOUL.md no es un sandbox. Los guardrails tienen que vivir en config (ask/block), no solo en prosa.",
            ]
        )
    )
    story.append(P("Costos — cómo no despertar con una factura", "h2"))
    story.append(
        table(
            ["Modo", "Qué consume", "Tope sano día 1"],
            [
                ["Solo OpenClaw + Gemini Flash / Grok ligero", "Tokens de chat + 1–2 tools", "USD 0–2 / día de uso normal"],
                ["Personal Jarvis con STT/TTS cloud + mic abierto", "Audio + realtime si lo encendiste", "Cierra el mic. No dejes realtime 24/7"],
                ["Misiones Claude/Codex cada frase", "Workers caros", "Reserva workers para “investiga / construye”"],
                ["Ollama local", "CPU/RAM, $0 API", "Úsalo de noche o para datos sensibles"],
                ["ElevenLabs Flash", "Créditos por caracter", "Piper/edge-tts primero"],
            ],
            [2.5 * inch, 2.3 * inch, 2.2 * inch],
        )
    )
    story.append(P("Anti-patrones (vistos en X esta semana)", "h2"))
    story.append(
        bullets(
            [
                "Instalar OpenClaw + Flightdeck + Personal Jarvis + 3 “JARVIS.py” el mismo día.",
                "Pedirle a 4 agentes el mismo brief de “hazme Jarvis”.",
                "Creer que 385k stars = seguro de exponer WhatsApp al mundo.",
                "Usar el wake word “Jarvis” y que se dispare con YouTube.",
                "Declarar done porque “el HUD se ve increíble”. El HUD no es el producto. La tarea hecha sí.",
                "Seguir un hilo que termina en Discord de pago o DM. El código bueno ya está en GitHub.",
            ]
        )
    )

    # ---------- 12 SOURCES ----------
    story.append(P("12. Fuentes y repos canónicos", "h1"))
    story.append(
        table(
            ["Fuente", "URL", "Fecha / nota"],
            [
                [
                    "OpenClaw repo",
                    "https://github.com/openclaw/openclaw",
                    "MIT. Installer + Gateway + channels.",
                ],
                [
                    "OpenClaw getting started",
                    "https://docs.openclaw.ai/start/getting-started",
                    "Onboard en ~5 min.",
                ],
                [
                    "OpenClaw install",
                    "https://docs.openclaw.ai/install",
                    "Node 22.22.3+ / 24.15+ / 25.9+.",
                ],
                [
                    "Personal Jarvis",
                    "https://github.com/PersonalJarvis/PersonalJarvis",
                    "v1.3.0, 10–12 ago 2026 en X.",
                ],
                [
                    "HF speech-to-speech",
                    "https://github.com/huggingface/speech-to-speech",
                    "Citado por @Marco_Ramilli, 8 ago.",
                ],
                [
                    "Flightdeck",
                    "https://github.com/MOVI85/flightdeck",
                    "macOS Apple Silicon. Fase futura.",
                ],
                [
                    "mimiclaw (ESP32)",
                    "https://github.com/memovai/mimiclaw",
                    "@tom_doerr, 10 ago.",
                ],
                [
                    "gbrain (memoria)",
                    "https://github.com/garrytan/gbrain",
                    "Garry Tan / YC. Fase 2.",
                ],
                [
                    "5 capas de un assistant",
                    "https://x.com/fluixoo/status/2087488228165030159",
                    "12 ago 2026.",
                ],
                [
                    "OpenClaw en X",
                    "https://x.com/sanjibxai/status/2087078552407814614",
                    "11 ago. 385k stars, MIT.",
                ],
            ],
            [1.7 * inch, 3.15 * inch, 2.15 * inch],
        )
    )

    story.append(Spacer(1, 12))
    story.append(
        KeepTogether(
            [
                callout(
                    "Siguiente movimiento concreto (hoy)",
                    "1) Quédate en el space herdr LOONA.  "
                    "2) Corre el PASO A2 y A3 (instalar + onboard OpenClaw).  "
                    "3) Cuando el dashboard conteste con el nombre LOONA, avísame y hacemos juntos "
                    "Telegram + SOUL.md + el installer de Personal Jarvis.  "
                    "No clones Flightdeck todavía.",
                    fill=colors.HexColor("#EAF1EA"),
                    bar=OK,
                )
            ]
        )
    )
    story.append(Spacer(1, 10))
    story.append(
        P(
            "Documento generado el 12 de agosto de 2026 para el workspace LOONA. "
            "Los stars, versiones y flags de CLI se tomaron de los README oficiales ese día. "
            "Si un installer cambia, manda el repo, no este PDF. Este PDF es el mapa; el repo es la verdad.",
            "caption",
        )
    )

    OUT.parent.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(
        str(OUT),
        pagesize=letter,
        leftMargin=0.75 * inch,
        rightMargin=0.75 * inch,
        topMargin=0.6 * inch,
        bottomMargin=0.5 * inch,
        title="LOONA — Cómo construir tu Jarvis",
        author="Grok  ·  Studio LOONA",
        subject="Guía operativa OpenClaw + Personal Jarvis a partir de repos públicos citados en X",
    )
    doc.build(story, onFirstPage=cover_page, onLaterPages=header_footer)
    print(f"Wrote {OUT} ({OUT.stat().st_size} bytes)")


if __name__ == "__main__":
    build()
