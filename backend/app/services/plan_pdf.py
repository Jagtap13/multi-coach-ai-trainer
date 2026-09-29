"""
Builds a downloadable PDF for a saved workout/meal plan.

Kept separate from the route file so it has no database or FastAPI
dependency - it just takes plain values and returns PDF bytes, which
also makes it easy to unit test.

Font note: ReportLab's built-in fonts (Helvetica) only cover Latin
characters; anything else renders as black boxes. Plans saved while the
language dropdown was set to Hindi/Marathi contain Devanagari text, so we
try to register a Unicode font that includes it (Nirmala UI ships with
Windows 10/11; Noto Sans Devanagari is the usual Linux equivalent). If
none is found we fall back to Helvetica, which still works perfectly for
English plans.
"""
import io
import os
import re
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    HRFlowable,
    KeepTogether,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
)

BODY_FONT = "Helvetica"
BOLD_FONT = "Helvetica-Bold"

# (regular, bold, subfontIndex) tried in order. Windows 10/11 ships
# Nirmala UI as a .ttc collection (index 0 = regular family); older
# Windows used .ttf. Mangal is the classic Windows Devanagari font.
_FONT_CANDIDATES = [
    ("C:/Windows/Fonts/Nirmala.ttc", "C:/Windows/Fonts/NirmalaB.ttc", 0),
    ("C:/Windows/Fonts/Nirmala.ttf", "C:/Windows/Fonts/NirmalaB.ttf", 0),
    ("C:/Windows/Fonts/mangal.ttf", "C:/Windows/Fonts/mangalb.ttf", 0),
    (
        "/usr/share/fonts/truetype/noto/NotoSansDevanagari-Regular.ttf",
        "/usr/share/fonts/truetype/noto/NotoSansDevanagari-Bold.ttf",
        0,
    ),
]


def _register_unicode_font():
    global BODY_FONT, BOLD_FONT
    for regular_path, bold_path, index in _FONT_CANDIDATES:
        if not os.path.exists(regular_path):
            continue
        # Some Windows installs ship only the regular Nirmala weight; in
        # that case reuse it for bold text (headings still stand out via
        # size and colour).
        if not os.path.exists(bold_path):
            bold_path = regular_path
        if True:
            try:
                pdfmetrics.registerFont(TTFont("PlanBody", regular_path, subfontIndex=index))
                pdfmetrics.registerFont(TTFont("PlanBold", bold_path, subfontIndex=index))
                pdfmetrics.registerFontFamily(
                    "PlanBody",
                    normal="PlanBody",
                    bold="PlanBold",
                    italic="PlanBody",
                    boldItalic="PlanBold",
                )
                BODY_FONT, BOLD_FONT = "PlanBody", "PlanBold"
                print(f"[plan_pdf] Using Unicode font: {regular_path}")
                return
            except Exception as e:
                print(f"[plan_pdf] Could not load font {regular_path}: {e}")
    print("[plan_pdf] No Devanagari font found - using Helvetica (English plans only).")


_register_unicode_font()

COACH_LABELS = {
    "bodybuilding": "Bodybuilding",
    "powerlifting": "Powerlifting",
    "nutrition": "Nutrition",
    "fatloss": "Fat Loss",
}

# Same accent colours as the frontend coach cards.
COACH_COLORS = {
    "bodybuilding": "#C0503D",
    "powerlifting": "#3D6B8C",
    "nutrition": "#5C7A4A",
    "fatloss": "#C98A2E",
}

FOOTER_TEXT = "AI-generated fitness guidance - not a substitute for professional medical advice."

# Emoji / dingbat ranges (e.g. the warning sign appended to answers) are
# not in any of our fonts and would render as black boxes.
_EMOJI_RE = re.compile("[\U0001F300-\U0001FAFF\u2600-\u27BF\uFE0F\u200d]")
_REPLACEMENTS = {"\u2192": "->", "\u2264": "<=", "\u2265": ">="}

_BULLET_RE = re.compile(r"^\s*(?:[\*\-\u2022])\s+(.*)$")
_HEADING_RE = re.compile(r"^\s*#{1,6}\s+(.*)$")
_WHOLE_BOLD_RE = re.compile(r"^\s*\*\*(.+?)\*\*:?\s*$")


def _clean(text):
    text = _EMOJI_RE.sub("", text or "")
    for src, dst in _REPLACEMENTS.items():
        text = text.replace(src, dst)
    return text


def _inline(text):
    """Escape for ReportLab's XML-ish markup, then turn **bold** into <b>."""
    text = escape(_clean(text))
    return re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)


def _styles(accent):
    return {
        "coach": ParagraphStyle(
            "coach", fontName=BOLD_FONT, fontSize=9, leading=12,
            textColor=accent, spaceAfter=2,
        ),
        "title": ParagraphStyle(
            "title", fontName=BOLD_FONT, fontSize=20, leading=25,
            textColor=colors.HexColor("#1C1D1F"), spaceAfter=3,
        ),
        "meta": ParagraphStyle(
            "meta", fontName=BODY_FONT, fontSize=9, leading=12,
            textColor=colors.HexColor("#777777"), spaceAfter=8,
        ),
        "day": ParagraphStyle(
            "day", fontName=BOLD_FONT, fontSize=12.5, leading=16,
            textColor=accent, spaceBefore=12, spaceAfter=4,
        ),
        "subheading": ParagraphStyle(
            "subheading", fontName=BOLD_FONT, fontSize=11, leading=15,
            textColor=colors.HexColor("#1C1D1F"), spaceBefore=8, spaceAfter=3,
        ),
        "body": ParagraphStyle(
            "body", fontName=BODY_FONT, fontSize=10.5, leading=15,
            textColor=colors.HexColor("#2A2B2E"), spaceAfter=5,
        ),
        "bullet": ParagraphStyle(
            "bullet", fontName=BODY_FONT, fontSize=10.5, leading=15,
            textColor=colors.HexColor("#2A2B2E"), leftIndent=14,
            bulletIndent=3, spaceAfter=3,
        ),
    }


def _structured_flowables(plan_data, styles):
    flowables = []
    for day in plan_data.get("days", []):
        heading = Paragraph(_inline(str(day.get("label", ""))), styles["day"])
        items = [
            Paragraph(_inline(str(item)), styles["bullet"], bulletText="\u2022")
            for item in day.get("items", [])
        ]
        if items:
            # Keep the heading with its first item so it never sits alone
            # at the bottom of a page.
            flowables.append(KeepTogether([heading, items[0]]))
            flowables.extend(items[1:])
        else:
            flowables.append(heading)
    return flowables


def _raw_text_flowables(raw_text, styles):
    flowables = []
    for line in _clean(raw_text).splitlines():
        if not line.strip():
            continue

        heading = _HEADING_RE.match(line)
        whole_bold = _WHOLE_BOLD_RE.match(line)
        bullet = _BULLET_RE.match(line)

        if heading:
            flowables.append(Paragraph(_inline(heading.group(1)), styles["subheading"]))
        elif whole_bold:
            flowables.append(Paragraph(_inline(whole_bold.group(1)), styles["subheading"]))
        elif bullet:
            flowables.append(
                Paragraph(_inline(bullet.group(1)), styles["bullet"], bulletText="\u2022")
            )
        else:
            flowables.append(Paragraph(_inline(line), styles["body"]))
    return flowables


def _page_decorator(accent):
    def decorate(canvas, doc):
        width, height = A4
        canvas.saveState()
        canvas.setFillColor(accent)
        canvas.rect(0, height - 6 * mm, width, 6 * mm, stroke=0, fill=1)
        canvas.setFont(BODY_FONT, 8)
        canvas.setFillColor(colors.HexColor("#888888"))
        canvas.drawString(20 * mm, 10 * mm, FOOTER_TEXT)
        canvas.drawRightString(width - 20 * mm, 10 * mm, f"Page {doc.page}")
        canvas.restoreState()

    return decorate


def build_plan_pdf(title, coach_type, created_at, plan_data, raw_text):
    """
    Returns the PDF as bytes.

    plan_data: parsed dict like {"days": [{"label": ..., "items": [...]}]}
               or None. When present we render the structured day-by-day
               layout; otherwise we fall back to formatting raw_text.
    """
    accent = colors.HexColor(COACH_COLORS.get(coach_type, "#3D6B8C"))
    styles = _styles(accent)

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=20 * mm,
        rightMargin=20 * mm,
        topMargin=22 * mm,
        bottomMargin=20 * mm,
        title=_clean(title),
        author="AI Personal Trainer Simulator",
    )

    coach_label = COACH_LABELS.get(coach_type, (coach_type or "").title())
    date_text = created_at.strftime("%d %b %Y") if created_at else ""

    story = [
        Paragraph(escape(coach_label.upper()), styles["coach"]),
        Paragraph(_inline(title), styles["title"]),
        Paragraph(escape(f"Saved {date_text}") if date_text else "", styles["meta"]),
        HRFlowable(width="100%", thickness=0.8, color=accent, spaceAfter=6),
    ]

    if plan_data and plan_data.get("days"):
        story.extend(_structured_flowables(plan_data, styles))
    else:
        story.extend(_raw_text_flowables(raw_text, styles))

    if len(story) == 4:
        story.append(Spacer(1, 6))
        story.append(Paragraph("This plan has no content.", styles["body"]))

    decorate = _page_decorator(accent)
    doc.build(story, onFirstPage=decorate, onLaterPages=decorate)
    return buffer.getvalue()