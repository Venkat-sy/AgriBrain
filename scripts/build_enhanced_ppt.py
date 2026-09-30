"""
AI-Driven Digital Twin Framework — Enhanced PPT
Corporate Blue/Gray/White Theme · 21 Slides · 16:9
"""
import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN, MSO_VERTICAL_ANCHOR

# ─── Palette ────────────────────────────────────────────────────────────────
BLUE       = RGBColor(0x1E, 0x3A, 0x8A)
BLUE_DARK  = RGBColor(0x1E, 0x2A, 0x5E)
BLUE_LT    = RGBColor(0xE8, 0xF0, 0xFE)
GRAY       = RGBColor(0x6B, 0x72, 0x80)
GRAY_LT    = RGBColor(0xF3, 0xF4, 0xF6)
GRAY_MED   = RGBColor(0xE0, 0xE0, 0xE0)
DARK       = RGBColor(0x11, 0x18, 0x27)
WHITE      = RGBColor(0xFF, 0xFF, 0xFF)
GREEN      = RGBColor(0x16, 0xA3, 0x4A)
GREEN_LT   = RGBColor(0xE8, 0xF5, 0xE9)
ORANGE     = RGBColor(0xEA, 0x58, 0x00)
ORANGE_LT  = RGBColor(0xFF, 0xF3, 0xE0)
RED        = RGBColor(0xDC, 0x26, 0x26)
RED_LT     = RGBColor(0xFF, 0xEB, 0xEE)
TEAL       = RGBColor(0x00, 0x96, 0x88)
TEAL_LT    = RGBColor(0xE0, 0xFD, 0xF7)
PURPLE     = RGBColor(0x7B, 0x1F, 0xA2)
PURPLE_LT  = RGBColor(0xF3, 0xE5, 0xF5)

# ─── Dimensions ────────────────────────────────────────────────────────────
W = Inches(13.333)   # slide width
H = Inches(7.5)      # slide height
ML = Inches(0.6)     # margin-left
MR = Inches(0.6)     # margin-right
MW = Inches(12.13)   # margin-width  (W - 2*ML)
HEADER_H = Inches(0.5)
FOOTER_BOTTOM = Inches(7.05)

# ─── Helpers ───────────────────────────────────────────────────────────────
def _f(val):
    """Convert font size (int or float) to Pt() for python-pptx."""
    if val is None:
        return Pt(13)
    if isinstance(val, Pt):
        return val
    if hasattr(val, 'emu'):  # Length, Emu, etc.
        return val
    try:
        return Pt(int(float(val)))
    except (TypeError, ValueError):
        return Pt(13)

def blank(prs):
    return prs.slides.add_slide(prs.slide_layouts[6])

def rrect(slide, l, t, w, h, fill, line=None, lw=0.75):
    sh = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, l, t, w, h)
    sh.fill.solid(); sh.fill.fore_color.rgb = fill
    if line:
        sh.line.color.rgb = line; sh.line.width = Pt(lw)
    else:
        sh.line.fill.background()
    return sh

def rect(slide, l, t, w, h, fill):
    sh = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, l, t, w, h)
    sh.fill.solid(); sh.fill.fore_color.rgb = fill
    sh.line.fill.background()
    return sh

def oval(slide, l, t, w, h, fill):
    sh = slide.shapes.add_shape(MSO_SHAPE.OVAL, l, t, w, h)
    sh.fill.solid(); sh.fill.fore_color.rgb = fill
    sh.line.fill.background()
    return sh

def txt(slide, l, t, w, h, text,
        size=13, bold=False, italic=False, color=DARK,
        align=PP_ALIGN.LEFT, anchor=MSO_VERTICAL_ANCHOR.TOP,
        wrap=True, ls=None):
    tb = slide.shapes.add_textbox(l, t, w, h)
    tf = tb.text_frame
    tf.word_wrap = wrap
    tf.vertical_anchor = anchor
    for line in text.split('\n'):
        p = tf.paragraphs[0] if not tf.paragraphs[0].text else tf.add_paragraph()
        p.alignment = align
        if ls is not None:
            p.line_spacing = ls
        r = p.add_run()
        r.text = line
        r.font.name = 'Calibri'
        r.font.size = _f(size)
        r.font.bold = bold
        r.font.italic = italic
        r.font.color.rgb = color
    return tb

def bullets(slide, l, t, w, h, items, size=11, bc=BLUE, tc=DARK, ls=1.25, sp=4):
    tb = slide.shapes.add_textbox(l, t, w, h)
    tf = tb.text_frame
    tf.word_wrap = True
    for i, item in enumerate(items):
        lvl = item[0] if isinstance(item, tuple) else 0
        body = item[1] if isinstance(item, tuple) else item
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.level = lvl
        p.alignment = PP_ALIGN.LEFT
        p.line_spacing = ls
        p.space_after = Pt(sp)
        r1 = p.add_run()
        r1.text = "• " if lvl == 0 else "  – "
        r1.font.name = 'Calibri'; r1.font.size = _f(size)
        r1.font.bold = True; r1.font.color.rgb = bc
        r2 = p.add_run()
        r2.text = body
        r2.font.name = 'Calibri'; r2.font.size = _f(size)
        r2.font.color.rgb = tc
    return tb

def badge(slide, l, t, text, bg=BLUE, size=10):
    w = Inches(0.5 + len(text) * 0.085)
    rrect(slide, l, t, w, Inches(0.33), bg)
    txt(slide, l, t, w, Inches(0.33), text, size=size, bold=True,
        color=WHITE, align=PP_ALIGN.CENTER, anchor=MSO_VERTICAL_ANCHOR.MIDDLE)

def header(slide, title, subtitle=""):
    rect(slide, Inches(0), Inches(0), W, HEADER_H, BLUE)
    txt(slide, Inches(0.6), Inches(0.07), Inches(10.0), Inches(0.36),
        title, size=16, bold=True, color=WHITE,
        anchor=MSO_VERTICAL_ANCHOR.MIDDLE)
    if subtitle:
        txt(slide, Inches(0.6), Inches(0.32), Inches(10.0), Inches(0.22),
            subtitle, size=9, italic=True, color=RGBColor(0xCC, 0xE4, 0xFF),
            anchor=MSO_VERTICAL_ANCHOR.MIDDLE)

def footer(slide, text="AI-Driven Digital Twin Framework • Final Year Project"):
    rect(slide, Inches(0), FOOTER_BOTTOM, W, Inches(0.45), GRAY_LT)
    txt(slide, Inches(0.6), FOOTER_BOTTOM + Inches(0.07),
        Inches(10.0), Inches(0.3), text, size=9, italic=True,
        color=GRAY, anchor=MSO_VERTICAL_ANCHOR.MIDDLE)
    txt(slide, Inches(11.0), FOOTER_BOTTOM + Inches(0.07),
        Inches(1.8), Inches(0.3), "NMAMIT", size=9, color=GRAY,
        align=PP_ALIGN.RIGHT, anchor=MSO_VERTICAL_ANCHOR.MIDDLE)

# ─── SLIDE 1 — Title ────────────────────────────────────────────────────────
def slide_01(prs):
    s = blank(prs)
    rect(s, Inches(0), Inches(0), W, H, BLUE)
    rect(s, Inches(0), Inches(0), W, Inches(3.5), BLUE_DARK)
    rect(s, Inches(0), Inches(3.5), W, Inches(0.08), GREEN)
    rect(s, Inches(0), Inches(3.58), W, Inches(3.92), WHITE)

    txt(s, Inches(0.8), Inches(0.7), Inches(10.0), Inches(0.5),
        "FINAL YEAR PROJECT", size=12, bold=True, color=GREEN)
    txt(s, Inches(0.8), Inches(1.2), Inches(11.0), Inches(1.0),
        "AI-Driven Digital Twin\nFramework for Sustainable Agriculture",
        size=36, bold=True, color=WHITE, ls=1.1)
    txt(s, Inches(0.8), Inches(2.4), Inches(11.0), Inches(0.6),
        "A What-If Simulation System for Crop Yield,\nIrrigation, and Risk Assessment",
        size=16, italic=True, color=RGBColor(0xB3, 0xE5, 0xFC), ls=1.3)

    for i, (label, name, role) in enumerate([
        ("PRESENTED BY", "K. Venkatesh Hebbar", "8th Sem, B.E. CCE"),
        ("GUIDE", "Mr. Krishna Prasad D S", "Asst. Professor, CCE"),
        ("COORDINATOR", "Dr. Radhakrishna", "Dept. of CCE"),
    ]):
        x = Inches(0.8 + i * 4.05)
        rrect(s, x, Inches(4.0), Inches(3.75), Inches(1.7),
              RGBColor(0x16, 0x4B, 0x7D))
        txt(s, x + Inches(0.15), Inches(4.1), Inches(3.4), Inches(0.28),
            label, size=9, bold=True, color=GREEN)
        txt(s, x + Inches(0.15), Inches(4.4), Inches(3.4), Inches(0.5),
            name, size=16, bold=True, color=WHITE)
        txt(s, x + Inches(0.15), Inches(5.0), Inches(3.4), Inches(0.4),
            role, size=10, color=RGBColor(0xB3, 0xE5, 0xFC))

    txt(s, Inches(0.8), Inches(5.9), Inches(11.0), Inches(0.4),
        "Department of Computer and Communication Engineering",
        size=13, bold=True, color=GRAY, align=PP_ALIGN.CENTER)
    txt(s, Inches(0.8), Inches(6.25), Inches(11.0), Inches(0.35),
        "NMAM Institute of Technology, Nitte (Deemed-to-be University)",
        size=11, italic=True, color=GRAY, align=PP_ALIGN.CENTER)
    txt(s, Inches(10.5), Inches(6.9), Inches(2.5), Inches(0.35),
        "September 2026", size=11, color=GRAY, align=PP_ALIGN.RIGHT)
    print("  ✓ Slide 1")

# ─── SLIDE 2 — Introduction ─────────────────────────────────────────────────
def slide_02(prs):
    s = blank(prs); header(s, "Introduction: Digital Agriculture",
                            "Transforming Indian smallholder farming through data & AI")
    footer(s)

    badge(s, Inches(0.6), Inches(0.75), "CHALLENGE", GRAY)
    txt(s, Inches(0.6), Inches(1.15), Inches(5.7), Inches(0.4),
        "India's Agricultural Challenge", size=15, bold=True, color=BLUE_DARK)
    bullets(s, Inches(0.6), Inches(1.65), Inches(5.7), Inches(2.6), [
        "Agriculture supports 58% of India's population; 86% of farms < 2 ha",
        "Climate unpredictability & soil degradation threaten yields",
        "Water scarcity: 80% of freshwater used in farming",
        "Static fertilizer advice ignores field-level variation",
    ], size=11)

    rrect(s, Inches(0.6), Inches(4.4), Inches(5.7), Inches(2.3), BLUE_LT,
          line=BLUE, lw=1.0)
    txt(s, Inches(0.8), Inches(4.5), Inches(5.3), Inches(0.3),
        "SDG Alignment", size=12, bold=True, color=BLUE_DARK)
    bullets(s, Inches(0.8), Inches(4.85), Inches(5.3), Inches(1.7), [
        "SDG 2: Zero Hunger — improved yields",
        "SDG 6: Clean Water — precision irrigation",
        "SDG 12: Responsible Production — fertilizer optimization",
        "SDG 13: Climate Action — risk prediction",
    ], size=10.5)

    badge(s, Inches(6.7), Inches(0.75), "SOLUTION", BLUE)
    txt(s, Inches(6.7), Inches(1.15), Inches(6.0), Inches(0.4),
        "Our AI-Driven Framework", size=15, bold=True, color=BLUE_DARK)
    for i, (title, body) in enumerate([
        ("IoT Sensors", "Real-time NPK, pH, moisture & weather data"),
        ("Machine Learning", "Yield, irrigation & risk predictions"),
        ("Digital Twin + XAI", "What-if simulation + SHAP explanations"),
    ]):
        y = Inches(1.7 + i * 1.7)
        rrect(s, Inches(6.7), y, Inches(6.0), Inches(1.45), BLUE_LT,
              line=BLUE, lw=1.0)
        oval(s, Inches(6.9), y + Inches(0.18), Inches(0.5), Inches(0.5), BLUE)
        txt(s, Inches(7.55), y + Inches(0.15), Inches(5.0), Inches(0.35),
            title, size=13, bold=True, color=BLUE_DARK)
        txt(s, Inches(7.55), y + Inches(0.58), Inches(5.0), Inches(0.7),
            body, size=11, color=GRAY, ls=1.2)
    print("  ✓ Slide 2")

# ─── SLIDE 3 — Literature Survey ───────────────────────────────────────────
def slide_03(prs):
    s = blank(prs); header(s, "Literature Survey: Methods & Algorithms",
                            "12 peer-reviewed papers — Nature, Elsevier, Frontiers")
    footer(s)

    methods = [
        ("Deep Learning + SHAP", "2023", "High accuracy with transparent explanations", BLUE),
        ("Lightweight Edge ML", "2023", "On-device inference — no cloud dependency", GREEN),
        ("Hybrid ML — RF + XGBoost", "2024", "Ensemble methods for tabular agricultural data", BLUE),
        ("Agentic AI", "2025", "Autonomous decision support agents", ORANGE),
        ("Feature Correlation KNN", "2026", "Isolates impactful soil variables", GRAY),
    ]
    positions = [
        (Inches(0.6), Inches(0.65)), (Inches(4.85), Inches(0.65)), (Inches(9.1), Inches(0.65)),
        (Inches(0.6), Inches(2.6)), (Inches(4.85), Inches(2.6)),
    ]
    for i, (method, year, desc, color) in enumerate(methods):
        x, y = positions[i]
        rrect(s, x, y, Inches(3.95), Inches(1.65), GRAY_LT, line=color, lw=1.2)
        txt(s, x + Inches(0.15), y + Inches(0.15), Inches(3.65), Inches(0.35),
            method, size=12, bold=True, color=color)
        txt(s, x + Inches(0.15), y + Inches(0.52), Inches(3.65), Inches(0.28),
            year, size=10, italic=True, color=GRAY)
        txt(s, x + Inches(0.15), y + Inches(0.88), Inches(3.65), Inches(0.55),
            desc, size=11, color=DARK, ls=1.2)

    rrect(s, Inches(0.6), Inches(4.4), MW, Inches(1.1), BLUE_LT, line=BLUE, lw=1.0)
    txt(s, Inches(0.8), Inches(4.48), Inches(11.7), Inches(0.28),
        "Key Insight: All five methods achieve strong accuracy — but each omits one critical capability.",
        size=11, bold=True, color=BLUE_DARK)
    txt(s, Inches(0.8), Inches(4.8), Inches(11.7), Inches(0.55),
        "No single work combines prediction + simulation + transparent explanation. "
        "We adopt Hybrid ML (RF + XGBoost) + Digital Twin + SHAP → unified framework.",
        size=10, color=GRAY, ls=1.2)

    rrect(s, Inches(0.6), Inches(5.65), MW, Inches(1.05), GRAY_LT, line=GRAY, lw=0.5)
    txt(s, Inches(0.8), Inches(5.72), Inches(11.7), Inches(0.28),
        "Gap: None address Digital Twin simulation or real-time SHAP dashboards",
        size=11, bold=True, color=RED)
    txt(s, Inches(0.8), Inches(6.05), Inches(11.7), Inches(0.55),
        "Source: Peer-reviewed papers from IEEE, Elsevier, Frontiers, Nature (2023–2026). "
        "Table summarises algorithmic approaches used in each study.",
        size=9, italic=True, color=GRAY, ls=1.2)
    print("  ✓ Slide 3")

# ─── SLIDE 4 — Limitations ──────────────────────────────────────────────────
def slide_04(prs):
    s = blank(prs); header(s, "Current Limitations in Literature",
                            "Critical gaps preventing real-world deployment")
    footer(s)

    gaps = [
        ("Black-Box Predictions", "Farmers cannot trust AI without explanations",
         "2023–2024 Nature papers", RED, RED_LT),
        ("Sensor Drift Decay", "Long-term sensor degradation drops ML accuracy",
         "2026 IoT-ML evaluation", GRAY, GRAY_LT),
        ("Unstructured Data", "Erratic weather breaks hybrid models",
         "2024 Hybrid ML paper", GRAY, GRAY_LT),
        ("No What-If Testing", "Systems cannot simulate hypothetical scenarios",
         "All surveyed papers", RED, RED_LT),
    ]
    positions = [
        (Inches(0.6), Inches(0.65)), (Inches(6.85), Inches(0.65)),
        (Inches(0.6), Inches(2.9)), (Inches(6.85), Inches(2.9)),
    ]
    for i, (title, desc, src, color, fill) in enumerate(gaps):
        x, y = positions[i]
        rrect(s, x, y, Inches(6.0), Inches(2.0), fill, line=color, lw=1.2)
        oval(s, x + Inches(0.2), y + Inches(0.2), Inches(0.55), Inches(0.55), color)
        txt(s, x + Inches(0.9), y + Inches(0.2), Inches(5.0), Inches(0.35),
            title, size=13, bold=True, color=color)
        txt(s, x + Inches(0.2), y + Inches(0.9), Inches(5.6), Inches(0.65),
            desc, size=11, color=DARK, ls=1.2)
        txt(s, x + Inches(0.2), y + Inches(1.65), Inches(5.6), Inches(0.28),
            f"Source: {src}", size=9, italic=True, color=GRAY)

    rrect(s, Inches(0.6), Inches(5.05), MW, Inches(1.6), GRAY_LT, line=BLUE, lw=1.0)
    txt(s, Inches(0.8), Inches(5.12), Inches(11.7), Inches(0.28),
        "Our Response: Unified Framework Addressing All Four Gaps",
        size=12, bold=True, color=BLUE_DARK)
    bullets(s, Inches(0.8), Inches(5.5), Inches(11.7), Inches(1.0), [
        "Gap 1 (Black-Box): SHAP XAI — every prediction explained",
        "Gap 2 (Sensor Drift): Digital Twin self-corrects via penalty functions",
        "Gap 3 (Unstructured): Digital Twin handles stress scenarios explicitly",
        "Gap 4 (No What-If): Dedicated simulation engine for what-if testing",
    ], size=10.5, bc=GREEN)
    print("  ✓ Slide 4")

# ─── SLIDE 5 — Gap Matrix ───────────────────────────────────────────────────
def slide_05(prs):
    s = blank(prs); header(s, "Research Gap & Our Solution",
                            "From 'Predict Only' to 'Predict + Simulate + Explain'")
    footer(s)

    gap_path = os.path.join(ASSETS, "gap_matrix_visual.png")
    if os.path.exists(gap_path):
        s.shapes.add_picture(gap_path, Inches(0.6), Inches(0.6),
                             width=Inches(5.7))

    badge(s, Inches(6.7), Inches(0.6), "PARADIGM SHIFT", BLUE)
    txt(s, Inches(6.7), Inches(1.0), Inches(6.0), Inches(0.35),
        "The Core Problem", size=14, bold=True, color=RED)
    rrect(s, Inches(6.7), Inches(1.4), Inches(6.0), Inches(1.85), RED_LT,
          line=RED, lw=1.0)
    txt(s, Inches(6.9), Inches(1.55), Inches(5.6), Inches(0.38),
        "Current systems are 'Predict Only' black boxes", size=12, bold=True, color=RED)
    bullets(s, Inches(6.9), Inches(2.0), Inches(5.6), Inches(1.0), [
        "Static recommendations from historical data only",
        "No transparency — farmers reject unexplained AI",
        "Cannot simulate 'what-if' before committing resources",
    ], size=10.5)

    txt(s, Inches(6.7), Inches(3.4), Inches(6.0), Inches(0.35),
        "Our Solution: Predict + Simulate + Explain", size=14, bold=True, color=GREEN)
    rrect(s, Inches(6.7), Inches(3.8), Inches(6.0), Inches(2.9), GREEN_LT,
          line=GREEN, lw=1.0)
    bullets(s, Inches(6.9), Inches(4.05), Inches(5.6), Inches(2.5), [
        "Digital Twin: Virtual farm for what-if testing",
        "SHAP: Transparent reason for every prediction",
        "Interactive Dashboard: Farmer-friendly guidance",
        "Real-time adaptation: Responds to sensor changes",
    ], size=10.5, bc=GREEN)

    rrect(s, Inches(0.6), Inches(5.05), Inches(5.7), Inches(1.6), GRAY_LT,
          line=BLUE, lw=0.75)
    txt(s, Inches(0.8), Inches(5.12), Inches(5.3), Inches(0.28),
        "Research Gap Matrix: Feature coverage across 12 papers", size=10, italic=True, color=GRAY)
    txt(s, Inches(0.8), Inches(5.5), Inches(5.3), Inches(1.0),
        "✓ Crop Yield Prediction (9/12 papers)\n"
        "✓ Explainable AI — SHAP (6/12 papers)\n"
        "✓ IoT Integration (7/12 papers)\n"
        "✗ Irrigation Prediction (0/12 papers)\n"
        "✗ Digital Twin (0/12 papers)\n"
        "✗ Interactive Dashboard (0/12 papers)", size=10, color=DARK, ls=1.3)
    print("  ✓ Slide 5")

# ─── SLIDE 6 — Objectives ──────────────────────────────────────────────────
def slide_06(prs):
    s = blank(prs); header(s, "Project Objectives",
                            "Five measurable goals aligned with research gaps")
    footer(s)

    objectives = [
        ("Crop Yield Prediction",
         "Accurate models for yield forecasting using NPK, pH, weather", GREEN),
        ("Irrigation Prediction",
         "Optimal water usage from soil moisture and weather forecasts", GREEN),
        ("Agricultural Risk Prediction",
         "Climate risks (drought, heat, flood) with probabilistic confidence", GREEN),
        ("Digital Twin Simulation",
         "Localized virtual farm replica for what-if scenario testing", BLUE),
        ("XAI Dashboard",
         "Explainable AI interface with SHAP transparency for every decision", BLUE),
    ]
    for i, (title, desc, color) in enumerate(objectives):
        y = Inches(0.65 + i * 1.25)
        rrect(s, Inches(0.6), y, MW, Inches(1.1), GRAY_LT,
              line=color, lw=1.0)
        rect(s, Inches(0.6), y, Inches(0.12), Inches(1.1), color)
        oval(s, Inches(0.45), y + Inches(0.27), Inches(0.5), Inches(0.5), color)
        txt(s, Inches(0.45), y + Inches(0.32), Inches(0.5), Inches(0.4),
            str(i+1), size=15, bold=True, color=WHITE,
            align=PP_ALIGN.CENTER, anchor=MSO_VERTICAL_ANCHOR.MIDDLE)
        txt(s, Inches(1.05), y + Inches(0.15), Inches(10.5), Inches(0.35),
            title, size=13, bold=True, color=BLUE_DARK)
        txt(s, Inches(1.05), y + Inches(0.58), Inches(10.5), Inches(0.38),
            desc, size=10.5, color=GRAY, ls=1.2)
    print("  ✓ Slide 6")

# ─── SLIDE 7 — Objective Mapping ────────────────────────────────────────────
def slide_07(prs):
    s = blank(prs); header(s, "Objective-to-Literature Mapping",
                            "Each objective grounded in prior work with a clear extension")
    footer(s)

    # Table header
    rect(s, Inches(0.6), Inches(0.65), MW, Inches(0.52), BLUE)
    col_x = [Inches(0.7), Inches(4.1), Inches(8.1)]
    col_w = [Inches(3.3), Inches(3.9), Inches(4.73)]
    for j, (x, w, h) in enumerate(zip(col_x, col_w,
            ["Objective", "Supporting Literature", "Our Extension"])):
        txt(s, x, Inches(0.7), w, Inches(0.42),
            h, size=12, bold=True, color=WHITE,
            anchor=MSO_VERTICAL_ANCHOR.MIDDLE)

    rows = [
        ("Obj 1: Yield Prediction",
         "2023 DL+SHAP, 2024 Hybrid ML",
         "Multi-output regression + uncertainty bounds", GREEN),
        ("Obj 2: Irrigation Prediction",
         "Critical gap in literature",
         "First implementation for Indian smallholder farms", GREEN),
        ("Obj 3: Risk Prediction",
         "2023 Edge ML, 2025 Spatial ML",
         "Combines climate + sensor drift + emissions", GREEN),
        ("Obj 4: Digital Twin",
         "NOT addressed in any paper",
         "Novel: virtual farm + scenario engine", BLUE),
        ("Obj 5: XAI Dashboard",
         "2023 SHAP, 2024 XAI Hybrid",
         "Real-time interface with per-prediction explanation", BLUE),
    ]
    for i, (obj, lit, ext, color) in enumerate(rows):
        y = Inches(1.17 + i * 0.85)
        bg = WHITE if i % 2 == 0 else GRAY_LT
        rect(s, Inches(0.6), y, MW, Inches(0.8), bg)
        txt(s, col_x[0], y, col_w[0], Inches(0.75),
            obj, size=11, bold=True, color=color, anchor=MSO_VERTICAL_ANCHOR.MIDDLE)
        txt(s, col_x[1], y, col_w[1], Inches(0.75),
            lit, size=10, italic=True, color=GRAY, anchor=MSO_VERTICAL_ANCHOR.MIDDLE)
        txt(s, col_x[2], y, col_w[2], Inches(0.75),
            ext, size=10, color=DARK, anchor=MSO_VERTICAL_ANCHOR.MIDDLE)
    print("  ✓ Slide 7")

# ─── SLIDE 8 — Dataset ──────────────────────────────────────────────────────
def slide_08(prs):
    s = blank(prs); header(s, "Dataset & Feature Engineering",
                            "10,000-row synthetic Indian agricultural dataset")
    footer(s)

    txt(s, Inches(0.6), Inches(0.65), Inches(6.4), Inches(0.35),
        "Indian Agricultural Data (10,000 rows)", size=14, bold=True, color=BLUE_DARK)
    bullets(s, Inches(0.6), Inches(1.05), Inches(6.4), Inches(2.1), [
        "Source: Custom generation + Government Soil Health Cards",
        "Crops: 22 Indian varieties (rice, wheat, maize, cotton, sugarcane)",
        "Time span: 2025–2026 agricultural cycles",
        "Split: 80% train / 20% test, stratified by crop",
    ], size=11)

    rrect(s, Inches(0.6), Inches(3.3), Inches(6.4), Inches(2.25), GRAY_LT,
          line=BLUE, lw=1.0)
    txt(s, Inches(0.8), Inches(3.38), Inches(6.0), Inches(0.3),
        "Feature Set (10 inputs)", size=12, bold=True, color=BLUE_DARK)
    bullets(s, Inches(0.8), Inches(3.75), Inches(6.0), Inches(1.65), [
        "Soil: Nitrogen, Phosphorus, Potassium, pH, Moisture",
        "Weather: Rainfall, Temperature, Humidity",
        "Farm: Crop Type, Water Usage, Historical Yield",
        "Total: 10 input features × 10,000 samples",
    ], size=10.5)

    fi_path = os.path.join(ASSETS, "feature_importance.png")
    if os.path.exists(fi_path):
        s.shapes.add_picture(fi_path, Inches(7.2), Inches(0.65),
                             width=Inches(5.75))
    print("  ✓ Slide 8")

# ─── SLIDE 9 — Workflow ────────────────────────────────────────────────────
def slide_09(prs):
    s = blank(prs); header(s, "Proposed Workflow",
                            "Nine-stage pipeline from data to decisions")
    footer(s)

    wf_path = os.path.join(ASSETS, "workflow_diagram.png")
    if os.path.exists(wf_path):
        s.shapes.add_picture(wf_path, Inches(0.6), Inches(0.6),
                             width=MW)

    phases = [
        ("Phase 1: Foundation", "Data collection → cleaning → preprocessing → features", BLUE),
        ("Phase 2: Intelligence", "Model training → prediction (yield, irrigation, risk)", GREEN),
        ("Phase 3: Action", "Digital Twin → SHAP → Dashboard → Decision", ORANGE),
    ]
    y = Inches(5.15)
    for i, (t, d, c) in enumerate(phases):
        x = Inches(0.6 + i * 4.1)
        rrect(s, x, y, Inches(3.85), Inches(1.5), GRAY_LT, line=c, lw=1.0)
        txt(s, x + Inches(0.15), y + Inches(0.15), Inches(3.55), Inches(0.3),
            t, size=12, bold=True, color=c)
        txt(s, x + Inches(0.15), y + Inches(0.55), Inches(3.55), Inches(0.75),
            d, size=10, color=GRAY, ls=1.2)
    print("  ✓ Slide 9")

# ─── SLIDE 10 — Architecture ───────────────────────────────────────────────
def slide_10(prs):
    s = blank(prs); header(s, "System Architecture",
                             "Five-layered integrated platform with data flow")
    footer(s)

    if os.path.exists(ARCH_IMG):
        s.shapes.add_picture(ARCH_IMG, Inches(0.6), Inches(0.6),
                             height=Inches(5.9))

    layers = [
        ("1. Data Layer", "Agricultural dataset · sensors · APIs", GRAY),
        ("2. Processing Layer", "Cleaning · EDA · Feature engineering", GRAY),
        ("3. Intelligence Layer", "RF + XGBoost models (yield, irrigation, risk)", BLUE),
        ("4. Simulation Layer", "Digital Twin with scenario routing", BLUE),
        ("5. Presentation Layer", "Glassmorphism dashboard with SHAP", BLUE),
    ]
    for i, (t, d, c) in enumerate(layers):
        y = Inches(0.65 + i * 1.12)
        oval(s, Inches(7.4), y + Inches(0.18), Inches(0.42), Inches(0.42), c)
        txt(s, Inches(7.95), y + Inches(0.15), Inches(5.0), Inches(0.38),
            t, size=12, bold=True, color=BLUE_DARK, anchor=MSO_VERTICAL_ANCHOR.MIDDLE)
        txt(s, Inches(7.95), y + Inches(0.58), Inches(5.0), Inches(0.38),
            d, size=9, italic=True, color=GRAY)
    print("  ✓ Slide 10")

# ─── SLIDE 11 — Digital Twin ───────────────────────────────────────────────
def slide_11(prs):
    s = blank(prs); header(s, "Digital Twin Simulation Engine",
                            "Virtual farm replica for safe what-if experimentation")
    footer(s)

    dt_path = os.path.join(ASSETS, "digital_twin_diagram.png")
    if os.path.exists(dt_path):
        s.shapes.add_picture(dt_path, Inches(0.6), Inches(0.6),
                             width=Inches(7.2))

    bullets(s, Inches(8.2), Inches(0.65), Inches(4.75), Inches(5.5), [
        (0, "What the Twin Can Do:"),
        (1, "Real-time monitoring of farm state"),
        (1, "What-if scenario testing"),
        (1, "Yield simulation under modified conditions"),
        (1, "Irrigation demand forecasting"),
        (1, "Climate shock stress-testing"),
        (1, "Feedback loop for continuous learning"),
        (0, ""),
        (0, "Key Differentiator:"),
        (1, "Only system in surveyed literature"),
        (1, "Combines prediction + simulation in one platform"),
    ], size=10.5)
    print("  ✓ Slide 11")

# ─── SLIDE 12 — Module 1 Yield ────────────────────────────────────────────
def slide_12(prs):
    s = blank(prs); header(s, "Module 1 — Crop Yield Prediction",
                            "Tree-based regression for accurate, explainable forecasts")
    footer(s)

    specs = [
        ("Inputs", "N, P, K, pH, Crop Type, Weather, Moisture", GREEN),
        ("Algorithms", "Random Forest + XGBoost (ensemble)", BLUE),
        ("Output", "Expected Yield (tons per hectare)", TEAL),
        ("Metrics", "RMSE, MAE, R², Cross-validation", GRAY),
        ("Twin Role", "Core simulation engine for yield scenarios", ORANGE),
    ]
    for i, (k, v, c) in enumerate(specs):
        y = Inches(0.65 + i * 1.28)
        rect(s, Inches(0.6), y, Inches(1.55), Inches(1.1), c)
        txt(s, Inches(0.6), y, Inches(1.55), Inches(1.1),
            k, size=10, bold=True, color=WHITE,
            align=PP_ALIGN.CENTER, anchor=MSO_VERTICAL_ANCHOR.MIDDLE)
        txt(s, Inches(2.3), y + Inches(0.1), Inches(4.2), Inches(0.9),
            v, size=11, color=DARK, anchor=MSO_VERTICAL_ANCHOR.MIDDLE)

    rrect(s, Inches(7.0), Inches(0.65), Inches(6.0), Inches(2.75), GRAY_LT,
          line=BLUE, lw=1.0)
    txt(s, Inches(7.2), Inches(0.75), Inches(5.6), Inches(0.3),
        "Why Tree-Based Models?", size=14, bold=True, color=BLUE_DARK)
    bullets(s, Inches(7.2), Inches(1.2), Inches(5.6), Inches(2.0), [
        "High accuracy on tabular agricultural data",
        "Full SHAP compatibility — transparent predictions",
        "Fast inference (< 10 ms) for edge deployment",
        "Deep learning rejected: opaque + 50× slower",
    ], size=11, bc=BLUE)

    rrect(s, Inches(7.0), Inches(3.55), Inches(6.0), Inches(3.1), BLUE_LT,
          line=BLUE, lw=1.0)
    txt(s, Inches(7.2), Inches(3.65), Inches(5.6), Inches(0.3),
        "Digital Twin Integration", size=14, bold=True, color=BLUE_DARK)
    bullets(s, Inches(7.2), Inches(4.1), Inches(5.6), Inches(2.4), [
        "Twin adjusts yield for hypothetical fertilizer changes",
        "Runs 'what if NPK changed by ±20%?' scenarios",
        "Penalty functions model soil degradation over time",
        "Simulates climate shocks: drought, flood, heat stress",
        "Returns confidence interval with each prediction",
    ], size=11, bc=GREEN)
    print("  ✓ Slide 12")

# ─── SLIDE 13 — Module 2 Irrigation ───────────────────────────────────────
def slide_13(prs):
    s = blank(prs); header(s, "Module 2 — Irrigation Prediction",
                            "Precision water management based on soil & weather")
    footer(s)

    specs = [
        ("Inputs", "Soil Moisture, Temp, Humidity, Rainfall", BLUE),
        ("Algorithms", "Decision Trees + Random Forest (regression)", BLUE),
        ("Output", "Watering schedule (liters + timing)", TEAL),
        ("Metrics", "MAE, RMSE, R², Precision-Recall", GRAY),
        ("Twin Role", "Simulates soil dry-down over 7-day forecast", ORANGE),
    ]
    for i, (k, v, c) in enumerate(specs):
        y = Inches(0.65 + i * 1.28)
        rect(s, Inches(0.6), y, Inches(1.55), Inches(1.1), c)
        txt(s, Inches(0.6), y, Inches(1.55), Inches(1.1),
            k, size=10, bold=True, color=WHITE,
            align=PP_ALIGN.CENTER, anchor=MSO_VERTICAL_ANCHOR.MIDDLE)
        txt(s, Inches(2.3), y + Inches(0.1), Inches(4.2), Inches(0.9),
            v, size=11, color=DARK, anchor=MSO_VERTICAL_ANCHOR.MIDDLE)

    rrect(s, Inches(7.0), Inches(0.65), Inches(6.0), Inches(2.75), GRAY_LT,
          line=BLUE, lw=1.0)
    txt(s, Inches(7.2), Inches(0.75), Inches(5.6), Inches(0.3),
        "Why This Matters for India", size=14, bold=True, color=BLUE_DARK)
    bullets(s, Inches(7.2), Inches(1.2), Inches(5.6), Inches(2.0), [
        "India uses 80% of freshwater for agriculture — 40% wasted",
        "Our system targets 15–30% water savings",
        "Prevents nutrient runoff from over-watering",
        "Lowers electricity costs for farmers",
    ], size=11, bc=BLUE)

    rrect(s, Inches(7.0), Inches(3.55), Inches(6.0), Inches(3.1), BLUE_LT,
          line=BLUE, lw=1.0)
    txt(s, Inches(7.2), Inches(3.65), Inches(5.6), Inches(0.3),
        "Digital Twin Integration", size=14, bold=True, color=BLUE_DARK)
    bullets(s, Inches(7.2), Inches(4.1), Inches(5.6), Inches(2.4), [
        "Twin simulates irrigation under drought scenarios",
        "What-if: 'How much water if rainfall drops 30%?'",
        "Schedules optimal watering windows (early morning)",
        "Predicts moisture deficit for next 7 days",
        "Suggests drip vs. flood based on crop type",
    ], size=11, bc=GREEN)
    print("  ✓ Slide 13")

# ─── SLIDE 14 — Module 3 Risk ──────────────────────────────────────────────
def slide_14(prs):
    s = blank(prs); header(s, "Module 3 — Agricultural Risk Prediction",
                            "Early warning system for climate & environmental threats")
    footer(s)

    specs = [
        ("Inputs", "Meteorological anomalies, extreme temps, sensor data", RED),
        ("Algorithm", "XGBoost Classifier (3-class risk)", BLUE),
        ("Output", "Risk probability + recommended action", TEAL),
        ("Metrics", "F1-Score, AUC-ROC, Confusion Matrix", GRAY),
        ("Twin Role", "Stress-tests crop resilience to climate shocks", ORANGE),
    ]
    for i, (k, v, c) in enumerate(specs):
        y = Inches(0.65 + i * 1.28)
        rect(s, Inches(0.6), y, Inches(1.55), Inches(1.1), c)
        txt(s, Inches(0.6), y, Inches(1.55), Inches(1.1),
            k, size=10, bold=True, color=WHITE,
            align=PP_ALIGN.CENTER, anchor=MSO_VERTICAL_ANCHOR.MIDDLE)
        txt(s, Inches(2.3), y + Inches(0.1), Inches(4.2), Inches(0.9),
            v, size=11, color=DARK, anchor=MSO_VERTICAL_ANCHOR.MIDDLE)

    risk_levels = [
        ("LOW", "Optimal conditions — standard practices", GREEN),
        ("MEDIUM", "Monitor closely — prepare contingencies", ORANGE),
        ("HIGH", "Immediate action — activate mitigation plan", RED),
    ]
    for i, (lvl, desc, color) in enumerate(risk_levels):
        y = Inches(0.65 + i * 1.28)
        rrect(s, Inches(7.0), y, Inches(6.0), Inches(1.1), GRAY_LT,
              line=color, lw=1.5)
        oval(s, Inches(7.2), y + Inches(0.28), Inches(0.5), Inches(0.5), color)
        txt(s, Inches(7.85), y + Inches(0.28), Inches(2.0), Inches(0.45),
            lvl, size=15, bold=True, color=color,
            anchor=MSO_VERTICAL_ANCHOR.MIDDLE)
        txt(s, Inches(7.85), y + Inches(0.75), Inches(5.0), Inches(0.3),
            desc, size=10.5, italic=True, color=GRAY)

    rrect(s, Inches(0.6), Inches(6.15), MW, Inches(0.5), ORANGE_LT,
          line=ORANGE, lw=0.75)
    txt(s, Inches(0.8), Inches(6.2), MW, Inches(0.4),
        "Digital Twin: Stress-tests each risk scenario — 'What if drought lasts 14 days?'",
        size=11, bold=True, color=ORANGE, anchor=MSO_VERTICAL_ANCHOR.MIDDLE)
    print("  ✓ Slide 14")

# ─── SLIDE 15 — Results ────────────────────────────────────────────────────
def slide_15(prs):
    s = blank(prs); header(s, "Model Performance & Results",
                            "Benchmark against standard baselines")
    footer(s)

    mc_path = os.path.join(ASSETS, "metrics_comparison.png")
    if os.path.exists(mc_path):
        s.shapes.add_picture(mc_path, Inches(0.6), Inches(0.6),
                             width=Inches(8.2))

    txt(s, Inches(9.1), Inches(0.65), Inches(3.9), Inches(0.35),
        "Best Scores (XGBoost)", size=13, bold=True, color=BLUE_DARK)
    cards = [
        ("87%", "Accuracy", GREEN), ("0.85", "R² Score", BLUE),
        ("1.42", "RMSE (t/ha)", GRAY), ("84%", "F1-Score", GREEN),
    ]
    for i, (val, label, color) in enumerate(cards):
        row, col = divmod(i, 2)
        x = Inches(9.1 + col * 1.95)
        y = Inches(1.1 + row * 1.4)
        rrect(s, x, y, Inches(1.8), Inches(1.2), GRAY_LT,
              line=color, lw=1.5)
        txt(s, x, y + Inches(0.2), Inches(1.8), Inches(0.55),
            val, size=28, bold=True, color=color,
            align=PP_ALIGN.CENTER, anchor=MSO_VERTICAL_ANCHOR.MIDDLE)
        txt(s, x, y + Inches(0.8), Inches(1.8), Inches(0.3),
            label, size=9, color=GRAY,
            align=PP_ALIGN.CENTER, anchor=MSO_VERTICAL_ANCHOR.MIDDLE)

    rrect(s, Inches(0.6), Inches(5.1), MW, Inches(1.55), GRAY_LT,
          line=GRAY, lw=0.5)
    txt(s, Inches(0.8), Inches(5.18), Inches(11.7), Inches(0.3),
        "Comparison vs. Published Baselines", size=12, bold=True, color=BLUE_DARK)
    bullets(s, Inches(0.8), Inches(5.55), Inches(11.7), Inches(0.95), [
        "RF: 82% Acc / 0.76 R² — 12 ms inference — SHAP ✓",
        "XGBoost: 87% Acc / 0.85 R² — 8 ms inference — SHAP ✓",
        "DL (2023): 85% Acc / 0.80 R² — 450 ms inference — Limited SHAP",
        "SVM (2023): 79% Acc / 0.68 R² — 95 ms inference — No SHAP",
    ], size=10)
    print("  ✓ Slide 15")

# ─── SLIDE 16 — Dashboard ───────────────────────────────────────────────────
def slide_16(prs):
    s = blank(prs); header(s, "Dashboard & Explainable AI (XAI)",
                            "Glassmorphism SPA with SHAP-powered transparency")
    footer(s)

    bullets(s, Inches(0.6), Inches(0.65), Inches(5.8), Inches(2.3), [
        "Visual gauges: NPK, pH, Moisture, Weather",
        "Real-time trend plots (yield, irrigation, risk)",
        "Color-coded risk alerts with actionable thresholds",
        "Interactive NPK sliders for parameter exploration",
        "Tabs: Overview | Field | AI Analytics | Twin | Settings",
    ], size=11)

    rrect(s, Inches(0.6), Inches(3.15), Inches(5.8), Inches(3.55), ORANGE_LT,
          line=ORANGE, lw=1.0)
    txt(s, Inches(0.8), Inches(3.25), Inches(5.4), Inches(0.3),
        "SHAP Explainability Layer", size=13, bold=True, color=BLUE_DARK)
    bullets(s, Inches(0.8), Inches(3.65), Inches(5.4), Inches(2.9), [
        "Feature importance bar chart (global view)",
        "Per-prediction waterfall chart (local)",
        "Example: 'Yield ↓ because pH contributes 60% negative impact'",
        "Trust-building: farmers see why AI recommends an action",
        "Regulatory-ready: decision audit trail available",
    ], size=10.5, bc=ORANGE)

    # Dashboard mockup
    rrect(s, Inches(6.8), Inches(0.65), Inches(6.15), Inches(6.0),
          RGBColor(0x1A, 0x2E, 0x4A), line=GREEN, lw=2.0)
    rect(s, Inches(6.8), Inches(0.65), Inches(6.15), Inches(0.55), BLUE_DARK)
    txt(s, Inches(6.8), Inches(0.65), Inches(6.15), Inches(0.55),
        "Digital Twin Dashboard", size=13, bold=True, color=WHITE,
        align=PP_ALIGN.CENTER, anchor=MSO_VERTICAL_ANCHOR.MIDDLE)

    for i, (lbl, val, col) in enumerate([
        ("Yield", "4.2 t/ha", GREEN), ("Water", "18 L", TEAL), ("Risk", "LOW", GREEN),
    ]):
        x = Inches(7.0 + i * 2.0)
        rrect(s, x, Inches(1.35), Inches(1.85), Inches(0.85),
              RGBColor(0x2A, 0x4A, 0x6A), line=col, lw=0.75)
        txt(s, x, Inches(1.4), Inches(1.85), Inches(0.3),
            lbl, size=9, color=RGBColor(0xB3, 0xE5, 0xFC),
            align=PP_ALIGN.CENTER, anchor=MSO_VERTICAL_ANCHOR.MIDDLE)
        txt(s, x, Inches(1.72), Inches(1.85), Inches(0.42),
            val, size=18, bold=True, color=col,
            align=PP_ALIGN.CENTER, anchor=MSO_VERTICAL_ANCHOR.MIDDLE)

    txt(s, Inches(7.0), Inches(2.35), Inches(5.8), Inches(0.3),
        "SHAP Feature Importance", size=10, bold=True,
        color=RGBColor(0xB3, 0xE5, 0xFC))
    for i, (feat, val, col) in enumerate([
        ("Nitrogen", 0.85, GREEN), ("pH", 0.72, TEAL),
        ("Rainfall", 0.58, ORANGE), ("Phosphorus", 0.42, BLUE),
    ]):
        y = Inches(2.75 + i * 0.38)
        txt(s, Inches(7.0), y, Inches(1.3), Inches(0.28),
            feat, size=9, color=RGBColor(0xB3, 0xE5, 0xFC))
        rect(s, Inches(8.3), y + Inches(0.05), Inches(val * 4.2), Inches(0.22), col)
        txt(s, Inches(12.6), y, Inches(0.35), Inches(0.28),
            f"{val:.2f}", size=9, color=WHITE)

    rrect(s, Inches(7.0), Inches(4.45), Inches(5.75), Inches(0.58), GREEN)
    txt(s, Inches(7.0), Inches(4.45), Inches(5.75), Inches(0.58),
        "Run What-If Simulation", size=12, bold=True, color=WHITE,
        align=PP_ALIGN.CENTER, anchor=MSO_VERTICAL_ANCHOR.MIDDLE)
    txt(s, Inches(7.0), Inches(5.1), Inches(5.75), Inches(0.3),
        "(Live demo in evaluation environment)", size=9, italic=True,
        color=RGBColor(0xB3, 0xE5, 0xFC), align=PP_ALIGN.CENTER)
    print("  ✓ Slide 16")

# ─── SLIDE 17 — Methodology ─────────────────────────────────────────────────
def slide_17(prs):
    s = blank(prs); header(s, "Methodology: Seven-Phase Lifecycle",
                            "Structured execution aligned with academic rigor")
    footer(s)

    phases = [
        ("Phase 1", "Data Collection", "Synthetic + Government SHC API integration", GREEN, True),
        ("Phase 2", "Preprocessing", "Imputation, deduplication, outlier handling", GREEN, True),
        ("Phase 3", "Feature Engineering", "Standard scaling, one-hot encoding, multicollinearity", GREEN, True),
        ("Phase 4", "Model Development", "XGBoost/RF baseline with GridSearchCV tuning", GREEN, True),
        ("Phase 5", "Evaluation", "Stratified k-fold validation, metric reporting", GREEN, True),
        ("Phase 6", "Digital Twin", "Python simulation engine with scenario routing", ORANGE, False),
        ("Phase 7", "Dashboard & Deployment", "Glassmorphism SPA + GitHub Pages CI/CD", ORANGE, False),
    ]
    col_x = [Inches(0.6), Inches(6.85)]
    base_y = Inches(0.65)
    card_h = Inches(1.1)
    card_gap = Inches(0.12)
    for i, (p, t, d, c, done) in enumerate(phases):
        col = 0 if i < 4 else 1
        row = i if col == 0 else i - 4
        x = col_x[col]
        y = base_y + row * (card_h + card_gap)
        rrect(s, x, y, Inches(6.0), card_h, GRAY_LT, line=c, lw=1.2)
        oval(s, x + Inches(0.2), y + Inches(0.27), Inches(0.4), Inches(0.4),
             GREEN if done else ORANGE)
        txt(s, x + Inches(0.7), y + Inches(0.25), Inches(4.6), Inches(0.3),
            t, size=12, bold=True, color=BLUE_DARK)
        txt(s, x + Inches(5.1), y + Inches(0.25), Inches(0.75), Inches(0.3),
            p, size=9, bold=True, color=c, align=PP_ALIGN.RIGHT)
        txt(s, x + Inches(0.7), y + Inches(0.6), Inches(5.1), Inches(0.38),
            d, size=9.5, color=GRAY, ls=1.2)
    print("  ✓ Slide 17")

# ─── SLIDE 18 — Results & Impact ───────────────────────────────────────────
def slide_18(prs):
    s = blank(prs); header(s, "Expected Results & Project Impact",
                            "Five measurable outcomes aligned with objectives")
    footer(s)

    results = [
        ("Improved Yield Prediction", "±10% error vs. baseline 25%", GREEN),
        ("Water Conservation", "15–30% water savings", BLUE),
        ("Early Risk Detection", "48-hour advance warning", ORANGE),
        ("Scenario Simulation", "<2s response time", GRAY),
    ]
    positions = [
        (Inches(0.6), Inches(0.65)), (Inches(6.85), Inches(0.65)),
        (Inches(0.6), Inches(2.85)), (Inches(6.85), Inches(2.85)),
    ]
    for i, (t, m, c) in enumerate(results):
        x, y = positions[i]
        rrect(s, x, y, Inches(6.0), Inches(1.95), GRAY_LT, line=c, lw=1.5)
        txt(s, x + Inches(0.2), y + Inches(0.2), Inches(5.6), Inches(0.38),
            t, size=14, bold=True, color=c)
        txt(s, x + Inches(0.2), y + Inches(0.65), Inches(5.6), Inches(0.3),
            f"Target: {m}", size=11, bold=True, color=DARK)
        txt(s, x + Inches(0.2), y + Inches(1.1), Inches(5.6), Inches(0.65),
            "Objective mapping: Obj 1–3",
            size=10, italic=True, color=GRAY, ls=1.2)

    # Sustainability strip
    rect(s, Inches(0.6), Inches(5.0), MW, Inches(0.62), TEAL)
    txt(s, Inches(0.8), Inches(5.05), MW, Inches(0.52),
        "  SUSTAINABILITY: Long-term soil health preservation + SDG 2, 6, 12, 13 alignment",
        size=11, bold=True, color=WHITE, anchor=MSO_VERTICAL_ANCHOR.MIDDLE)

    rrect(s, Inches(0.6), Inches(5.75), MW, Inches(0.9), TEAL_LT, line=TEAL, lw=1.0)
    txt(s, Inches(0.8), Inches(5.82), Inches(11.7), Inches(0.28),
        "Impact on Indian Agriculture:", size=12, bold=True, color=TEAL)
    txt(s, Inches(0.8), Inches(6.15), Inches(11.7), Inches(0.4),
        "Reduced input waste · Lower carbon footprint · Higher smallholder profitability · "
        "Resilient to climate change · Scalable to regional agricultural zones",
        size=10, color=DARK, ls=1.2)
    print("  ✓ Slide 18")

# ─── SLIDE 19 — Status ─────────────────────────────────────────────────────
def slide_19(prs):
    s = blank(prs); header(s, "Project Status & Roadmap",
                            "Transparent progress tracking")
    footer(s)

    cols = [
        ("Completed", GREEN, [
            "Literature Survey (12 papers)",
            "Research Gap Analysis",
            "Dataset Generation (10K rows)",
            "EDA & Visualization",
            "Model Training (RF + XGBoost)",
            "SHAP Explainer Integration",
        ]),
        ("In Progress", ORANGE, [
            "Hyperparameter Tuning (GridSearchCV)",
            "Digital Twin Engine (scenario routing)",
            "Dashboard UI Implementation",
            "End-to-End Testing",
        ]),
        ("Planned", BLUE, [
            "Real-Time IoT Sensor Integration",
            "Cloud Deployment (AWS/GCP)",
            "Mobile PWA",
            "Satellite Imagery Fusion",
        ]),
    ]
    for i, (h, color, items) in enumerate(cols):
        x = Inches(0.6 + i * 4.25)
        rect(s, x, Inches(0.65), Inches(4.0), Inches(0.52), color)
        txt(s, x, Inches(0.68), Inches(4.0), Inches(0.46),
            h.upper(), size=14, bold=True, color=WHITE,
            align=PP_ALIGN.CENTER, anchor=MSO_VERTICAL_ANCHOR.MIDDLE)
        rrect(s, x, Inches(1.17), Inches(4.0), Inches(5.5), GRAY_LT,
              line=color, lw=1.0)
        bullets(s, x + Inches(0.15), Inches(1.35), Inches(3.7), Inches(5.15),
                [(0, it) for it in items], size=11, bc=color)
    print("  ✓ Slide 19")

# ─── SLIDE 20 — Future Scope ───────────────────────────────────────────────
def slide_20(prs):
    s = blank(prs); header(s, "Future Scope & Extensions",
                            "Beyond the final year — long-term research vision")
    footer(s)

    futures = [
        ("IoT Sensors", "Live-streaming soil sensors replacing synthetic data\nMQTT-based real-time data pipeline", GRAY),
        ("Satellite & Drone", "NDVI crop health monitoring + drone-based pest detection", BLUE),
        ("Mobile PWA", "Offline-capable field interface for low-literacy users", GREEN),
        ("Reinforcement Learning", "Self-optimizing AI agents learning from seasonal feedback", GREEN),
        ("Smart Farm Automation", "Direct valve actuation for precise irrigation control", ORANGE),
    ]
    for i, (t, d, c) in enumerate(futures):
        y = Inches(0.65 + i * 1.25)
        rrect(s, Inches(0.6), y, MW, Inches(1.1), GRAY_LT, line=c, lw=1.2)
        oval(s, Inches(0.8), y + Inches(0.28), Inches(0.5), Inches(0.5), c)
        txt(s, Inches(1.45), y + Inches(0.15), Inches(10.5), Inches(0.35),
            t, size=13, bold=True, color=BLUE_DARK)
        txt(s, Inches(1.45), y + Inches(0.55), Inches(10.5), Inches(0.45),
            d, size=9.5, color=GRAY, ls=1.2)
    print("  ✓ Slide 20")

# ─── SLIDE 21 — Conclusion ─────────────────────────────────────────────────
def slide_21(prs):
    s = blank(prs)
    rect(s, Inches(0), Inches(0), W, H, WHITE)
    rect(s, Inches(0), Inches(0), W, Inches(0.85), BLUE)
    txt(s, Inches(0.6), Inches(0.1), Inches(12.0), Inches(0.65),
        "CONCLUSION & THANK YOU", size=16, bold=True, color=WHITE,
        anchor=MSO_VERTICAL_ANCHOR.MIDDLE)

    txt(s, Inches(1.0), Inches(1.8), Inches(11.0), Inches(0.8),
        "Transforming Traditional Farming", size=36, bold=True,
        color=BLUE_DARK, align=PP_ALIGN.CENTER)
    txt(s, Inches(1.0), Inches(2.75), Inches(11.0), Inches(0.8),
        "into Intelligent Sustainable Agriculture", size=36, bold=True,
        color=BLUE_DARK, align=PP_ALIGN.CENTER)
    txt(s, Inches(1.0), Inches(3.65), Inches(11.0), Inches(0.55),
        "through AI-Powered Digital Twins", size=22, italic=True,
        color=GRAY, align=PP_ALIGN.CENTER)

    pillars = [
        ("PREDICT", "Accurate yield, irrigation, risk forecasts", BLUE),
        ("SIMULATE", "What-if scenarios via Digital Twin", GREEN),
        ("EXPLAIN", "Transparent SHAP for every prediction", TEAL),
    ]
    for i, (t, d, c) in enumerate(pillars):
        x = Inches(2.0 + i * 3.75)
        oval(s, x + Inches(0.9), Inches(4.65), Inches(1.5), Inches(1.5), c)
        txt(s, x + Inches(0.9), Inches(4.72), Inches(1.5), Inches(1.35),
            t, size=12, bold=True, color=WHITE,
            align=PP_ALIGN.CENTER, anchor=MSO_VERTICAL_ANCHOR.MIDDLE)
        txt(s, x + Inches(0.85), Inches(6.25), Inches(1.8), Inches(0.5),
            d, size=10, italic=True, color=GRAY, align=PP_ALIGN.CENTER)

    txt(s, Inches(0.6), Inches(6.8), MW, Inches(0.4),
        "Thank You!", size=26, bold=True, color=GREEN,
        align=PP_ALIGN.CENTER)
    txt(s, Inches(0.6), Inches(7.15), MW, Inches(0.3),
        "Questions & Discussion", size=13, italic=True,
        color=GRAY, align=PP_ALIGN.CENTER)
    print("  ✓ Slide 21")

# ─── Assemble ────────────────────────────────────────────────────────────────
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(SCRIPT_DIR, "assets")
ARCH_IMG = os.path.join(SCRIPT_DIR, "system_architecture.jpg")
os.makedirs(ASSETS, exist_ok=True)

prs = Presentation()
prs.slide_width = W
prs.slide_height = H

slide_01(prs)
for fn in [slide_02, slide_03, slide_04, slide_05, slide_06, slide_07,
           slide_08, slide_09, slide_10, slide_11, slide_12, slide_13,
           slide_14, slide_15, slide_16, slide_17, slide_18, slide_19,
           slide_20, slide_21]:
    fn(prs)

output_path = os.path.join(SCRIPT_DIR, "AI_Digital_Twin_Enhanced_Presentation.pptx")
prs.save(output_path)
size = os.path.getsize(output_path)
print(f"\nSaved: {output_path}")
print(f"Slides: {len(prs.slides)}  |  Size: {size:,} bytes ({size//1024} KB)")
