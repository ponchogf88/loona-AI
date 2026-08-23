#!/usr/bin/env python3
"""Visual Gumroad guide — shots first, almost no wall of text."""

from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    Image,
    KeepTogether,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

OUT = Path("/Users/imac/loona/docs/GUMROAD_LOONA.pdf")
SHOTS = [
    Path("/Users/imac/loona/refs/product/01-world.png"),
    Path("/Users/imac/loona/refs/hud/world.png"),
    Path("/Users/imac/loona/refs/zoey/f001.jpg"),
]
DIAG = Path("/Users/imac/loona/refs/diagrams/01_architecture.png")
HUD2 = Path("/Users/imac/loona/refs/hud/config.png")
NAVY = colors.HexColor("#0B0A09")
GOLD = colors.HexColor("#C9A36A")
INK = colors.HexColor("#F4EAD8")
MUTED = colors.HexColor("#A89880")
PW = 7.0 * inch


def st():
    return {
        "k": ParagraphStyle("k", fontName="Helvetica", fontSize=9, textColor=GOLD, alignment=TA_CENTER, leading=12),
        "h": ParagraphStyle("h", fontName="Helvetica-Bold", fontSize=22, textColor=NAVY, leading=26, spaceAfter=8),
        "b": ParagraphStyle("b", fontName="Helvetica", fontSize=10, textColor=NAVY, leading=14, spaceAfter=6),
        "c": ParagraphStyle("c", fontName="Helvetica-Oblique", fontSize=8, textColor=MUTED, alignment=TA_CENTER, spaceAfter=10),
        "cap": ParagraphStyle("cap", fontName="Helvetica-Bold", fontSize=11, textColor=NAVY, alignment=TA_LEFT, spaceBefore=4),
    }


S = st()


def P(t, k="b"):
    return Paragraph(t, S[k])


def shot(path, caption, h=3.4 * inch):
    if not path.exists():
        return P(f"[falta foto: {path.name}]", "c")
    im = Image(str(path))
    im.drawHeight = h
    im.drawWidth = h * im.imageWidth / im.imageHeight
    if im.drawWidth > PW:
        im.drawWidth = PW
        im.drawHeight = PW * Image(str(path)).imageHeight / Image(str(path)).imageWidth
    im.hAlign = "CENTER"
    return KeepTogether([im, P(caption, "c")])


def header(c, doc):
    w, h = letter
    c.saveState()
    c.setFillColor(NAVY)
    c.rect(0, h - 22, w, 22, fill=1, stroke=0)
    c.setFillColor(GOLD)
    c.setFont("Helvetica", 8)
    c.drawString(36, h - 14, "LOONA  ·  guía visual")
    c.drawRightString(w - 36, h - 14, str(doc.page))
    c.restoreState()


def build():
    story = []
    hero = Table([[P("GUMROAD  ·  PRODUCTO", "k")], [P("LOONA", "h")], [P("World View · voz · noticias · 24/7 en tu Mac", "b")]], colWidths=[PW])
    hero.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F7F1E6")),
        ("BOX", (0, 0), (-1, -1), 0, GOLD),
        ("LEFTPADDING", (0, 0), (-1, -1), 16),
        ("TOPPADDING", (0, 0), (0, 0), 16),
        ("BOTTOMPADDING", (0, -1), (-1, -1), 16),
    ]))
    story.append(hero)
    story.append(Spacer(1, 10))
    story.append(P("01  ·  Ábrela como programa, no como pestaña", "cap"))
    story.append(P("Aplicaciones → LOONA.app  ·  el cerebro ya está en 127.0.0.1:8766", "b"))
    story.append(shot(SHOTS[1] if SHOTS[1].exists() else SHOTS[2], "World View. Cara de luz, no un dashboard."))
    story.append(PageBreak())
    story.append(P("02  ·  Noticias en pantallita CRT", "cap"))
    story.append(P("Botón NOTICIAS. Flash + línea. Fotos reales. Cerrar = apagado de TV.", "b"))
    story.append(shot(HUD2 if HUD2.exists() else SHOTS[1], "Controles y pulso. Glass, no formularios."))
    story.append(P("03  ·  Timeline (día / semana / quincena / mes / año)", "cap"))
    story.append(P("Sin cuadrícula de letras. Eje + puntos. AGENDA abre la proyección.", "b"))
    story.append(P("04  ·  Voz", "cap"))
    story.append(P("MIC o espacio. Habla Dalia Neural (es-MX), no el robot del sistema.", "b"))
    story.append(PageBreak())
    story.append(P("05  ·  Cómo está hecha", "cap"))
    story.append(P("HUD glass + FastAPI local + DeepSeek/Gemini + edge-tts + LaunchAgent. Un host.", "b"))
    story.append(P("Keys en runtime/.env · estudio en GET /api/metrics · uso en usage.jsonl", "b"))
    story.append(P("06  ·  Estudio de uso masivo", "cap"))
    story.append(P("15 min por tester: 3 chats, noticias, timeline, MIC. Exporta usage.jsonl. Ver docs/STUDY.md.", "b"))
    story.append(P("Zip: código MIT + app scripts + este PDF. Sin API keys.", "c"))
    OUT.parent.mkdir(parents=True, exist_ok=True)
    SimpleDocTemplate(
        str(OUT), pagesize=letter,
        leftMargin=0.75 * inch, rightMargin=0.75 * inch,
        topMargin=0.5 * inch, bottomMargin=0.45 * inch,
        title="LOONA — guía visual Gumroad",
    ).build(story, onFirstPage=header, onLaterPages=header)
    print("wrote", OUT, OUT.stat().st_size)


if __name__ == "__main__":
    build()
