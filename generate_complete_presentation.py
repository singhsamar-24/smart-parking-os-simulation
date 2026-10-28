"""
Complete Java PBL Presentation Generator for ProjectPulse Enterprise
Academic Project Tracking System | Object Oriented Techniques Using Java (CCSE0355)
Group 3: Samar Singh, Aditi Singh, Chhavi Attri | Faculty Mentor: Ms. Aparna Pandey
NIET Greater Noida, Department of CSE (AI), Session 2026-2027
"""

import os
import sys
import pptx
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

# -----------------------------------------------------------------------------
# PRESENTATION & PALETTE CONSTANTS (Matching 1month ppt.pptx aesthetic)
# -----------------------------------------------------------------------------
SLIDE_WIDTH = Inches(13.333)
SLIDE_HEIGHT = Inches(7.5)

COLOR_CRIMSON = RGBColor(225, 29, 72)        # Primary Crimson Red (#E11D48)
COLOR_CRIMSON_DARK = RGBColor(190, 18, 60)   # Deep Crimson (#BE123C)
COLOR_CRIMSON_LIGHT = RGBColor(254, 226, 226) # Border tint (#FEE2E2)
COLOR_PINK_TINT = RGBColor(255, 241, 242)    # Soft Rose Surface (#FFF1F2)
COLOR_WHITE = RGBColor(255, 255, 255)        # Card Surface
COLOR_TEXT_DARK = RGBColor(15, 23, 42)       # Charcoal Slate (#0F172A)
COLOR_TEXT_MUTED = RGBColor(100, 116, 139)   # Slate Grey (#64748B)
COLOR_TEXT_DIM = RGBColor(148, 163, 184)     # Light Slate (#94A3B8)
COLOR_CARD_BORDER = RGBColor(254, 205, 211)  # Rose 200 border (#FECDD3)
COLOR_BORDER_SUBTLE = RGBColor(226, 232, 240) # Neutral subtle border (#E2E8F0)

COLOR_GREEN_BG = RGBColor(209, 250, 229)     # Emerald 100
COLOR_GREEN_TEXT = RGBColor(5, 150, 105)     # Emerald 600
COLOR_BLUE_BG = RGBColor(219, 234, 254)      # Blue 100
COLOR_BLUE_TEXT = RGBColor(37, 99, 235)      # Blue 600
COLOR_AMBER_BG = RGBColor(254, 243, 199)     # Amber 100
COLOR_AMBER_TEXT = RGBColor(217, 119, 6)     # Amber 600
COLOR_RED_BG = RGBColor(254, 226, 226)       # Red 100
COLOR_RED_TEXT = RGBColor(220, 38, 38)       # Red 600

FONT_DISPLAY = 'Georgia'
FONT_BODY = 'Segoe UI'
FONT_MONO = 'Consolas'

NIET_LOGO_PATH = os.path.abspath('extracted_1month_ppt/niet_logo_trans.png')
NIET_CAMPUS_PATH = os.path.abspath('extracted_1month_ppt/ppt/media/image2.png')

class PresentationBuilder:
    def __init__(self):
        self.prs = pptx.Presentation()
        self.prs.slide_width = SLIDE_WIDTH
        self.prs.slide_height = SLIDE_HEIGHT
        self.blank_layout = self.prs.slide_layouts[6]

    def add_slide(self):
        return self.prs.slides.add_slide(self.blank_layout)

    def draw_header(self, slide, num_str, title_w1, title_w2, subtitle="ACADEMIC PROJECT TRACKING SYSTEM"):
        """Draws standard top header with pill badge, serif heading, slogan, and NIET logo."""
        badge = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.6), Inches(0.35), Inches(0.85), Inches(0.85))
        badge.fill.solid()
        badge.fill.fore_color.rgb = COLOR_PINK_TINT
        badge.line.color.rgb = COLOR_CARD_BORDER
        badge.line.width = Pt(1.5)
        tf = badge.text_frame
        tf.word_wrap = False
        tf.vertical_anchor = MSO_ANCHOR.MIDDLE
        p = tf.paragraphs[0]
        p.text = num_str
        p.font.name = FONT_DISPLAY
        p.font.size = Pt(22)
        p.font.bold = True
        p.font.color.rgb = COLOR_CRIMSON
        p.alignment = PP_ALIGN.CENTER

        t_box = slide.shapes.add_textbox(Inches(1.6), Inches(0.30), Inches(7.6), Inches(0.95))
        tf_t = t_box.text_frame
        tf_t.word_wrap = True
        tf_t.margin_top = Inches(0)
        tf_t.margin_left = Inches(0)
        p_title = tf_t.paragraphs[0]
        
        r1 = p_title.add_run()
        r1.text = title_w1 + " "
        r1.font.name = FONT_DISPLAY
        r1.font.size = Pt(26)
        r1.font.bold = True
        r1.font.color.rgb = COLOR_TEXT_DARK
        
        r2 = p_title.add_run()
        r2.text = title_w2
        r2.font.name = FONT_DISPLAY
        r2.font.size = Pt(26)
        r2.font.bold = True
        r2.font.color.rgb = COLOR_CRIMSON

        p_sub = tf_t.add_paragraph()
        r_sub = p_sub.add_run()
        r_sub.text = subtitle
        r_sub.font.name = FONT_BODY
        r_sub.font.size = Pt(9.5)
        r_sub.font.bold = True
        r_sub.font.color.rgb = COLOR_TEXT_MUTED

        line = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(1.6), Inches(1.22), Inches(4.5), Pt(1.5))
        line.fill.solid()
        line.fill.fore_color.rgb = COLOR_CRIMSON
        line.line.fill.background()

        top_r = slide.shapes.add_textbox(Inches(8.5), Inches(0.4), Inches(2.8), Inches(0.4))
        tf_r = top_r.text_frame
        tf_r.margin_top = Inches(0)
        tf_r.margin_right = Inches(0)
        p_r = tf_r.paragraphs[0]
        p_r.alignment = PP_ALIGN.RIGHT
        r_r = p_r.add_run()
        r_r.text = "— LEARN  |  INNOVATE  |  TRANSFORM"
        r_r.font.name = FONT_BODY
        r_r.font.size = Pt(9.5)
        r_r.font.bold = True
        r_r.font.color.rgb = COLOR_TEXT_MUTED

        if os.path.exists(NIET_LOGO_PATH):
            slide.shapes.add_picture(NIET_LOGO_PATH, Inches(11.5), Inches(0.28), Inches(1.3), Inches(0.55))

        f_line = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.6), Inches(6.9), Inches(12.13), Pt(1))
        f_line.fill.solid()
        f_line.fill.fore_color.rgb = COLOR_BORDER_SUBTLE
        f_line.line.fill.background()

        f_box_l = slide.shapes.add_textbox(Inches(0.6), Inches(6.95), Inches(6.0), Inches(0.35))
        p_fl = f_box_l.text_frame.paragraphs[0]
        r_fl = p_fl.add_run()
        r_fl.text = "Department of CSE (AI)  |  Session 2026–27  |  Capstone Project  |  Group 3"
        r_fl.font.name = FONT_BODY
        r_fl.font.size = Pt(9)
        r_fl.font.color.rgb = COLOR_TEXT_MUTED

        f_box_r = slide.shapes.add_textbox(Inches(10.5), Inches(6.92), Inches(2.23), Inches(0.4))
        p_fr = f_box_r.text_frame.paragraphs[0]
        p_fr.alignment = PP_ALIGN.RIGHT
        r_fr = p_fr.add_run()
        r_fr.text = f"{num_str}  —"
        r_fr.font.name = FONT_BODY
        r_fr.font.size = Pt(12)
        r_fr.font.bold = True
        r_fr.font.color.rgb = COLOR_CRIMSON

    def add_card(self, slide, left, top, width, height, bg_rgb=COLOR_WHITE, border_rgb=COLOR_CARD_BORDER, border_pt=1):
        shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
        shape.fill.solid()
        shape.fill.fore_color.rgb = bg_rgb
        if border_rgb:
            shape.line.color.rgb = border_rgb
            shape.line.width = Pt(border_pt)
        else:
            shape.line.fill.background()
        return shape

    def add_bottom_bar(self, slide, title, text, icon="🏆"):
        card = self.add_card(slide, Inches(0.6), Inches(6.08), Inches(12.13), Inches(0.68), bg_rgb=COLOR_PINK_TINT, border_rgb=COLOR_CARD_BORDER)
        
        ibadge = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.75), Inches(6.16), Inches(0.48), Inches(0.48))
        ibadge.fill.solid()
        ibadge.fill.fore_color.rgb = COLOR_WHITE
        ibadge.line.color.rgb = COLOR_CARD_BORDER
        ibadge.line.width = Pt(1)
        tf_i = ibadge.text_frame
        tf_i.vertical_anchor = MSO_ANCHOR.MIDDLE
        p_i = tf_i.paragraphs[0]
        p_i.text = icon
        p_i.font.size = Pt(14)
        p_i.alignment = PP_ALIGN.CENTER

        tbox = slide.shapes.add_textbox(Inches(1.35), Inches(6.12), Inches(11.2), Inches(0.55))
        tf = tbox.text_frame
        tf.word_wrap = True
        tf.vertical_anchor = MSO_ANCHOR.MIDDLE
        p = tf.paragraphs[0]
        
        r_t = p.add_run()
        r_t.text = title + "  "
        r_t.font.name = FONT_BODY
        r_t.font.size = Pt(11)
        r_t.font.bold = True
        r_t.font.color.rgb = COLOR_CRIMSON
        
        r_d = p.add_run()
        r_d.text = text
        r_d.font.name = FONT_BODY
        r_d.font.size = Pt(10)
        r_d.font.color.rgb = COLOR_TEXT_DARK

    def add_chip(self, slide, left, top, text, bg_rgb, text_rgb, width=None, height=Inches(0.28)):
        w = width if width else Inches(len(text) * 0.085 + 0.25)
        chip = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, w, height)
        chip.fill.solid()
        chip.fill.fore_color.rgb = bg_rgb
        chip.line.fill.background()
        tf = chip.text_frame
        tf.vertical_anchor = MSO_ANCHOR.MIDDLE
        tf.margin_left = Inches(0.08)
        tf.margin_right = Inches(0.08)
        p = tf.paragraphs[0]
        p.text = text
        p.font.name = FONT_BODY
        p.font.size = Pt(8.5)
        p.font.bold = True
        p.font.color.rgb = text_rgb
        p.alignment = PP_ALIGN.CENTER
        return chip

    # -------------------------------------------------------------------------
    # SLIDE BUILDERS (All 22 Slides)
    # -------------------------------------------------------------------------

    def build_slide_01_cover(self):
        """Slide 1 — Cover Page matching 1month ppt.pptx image1.png exactly."""
        slide = self.add_slide()

        # Top Red Banner
        top_bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(0.85))
        top_bar.fill.solid()
        top_bar.fill.fore_color.rgb = COLOR_CRIMSON
        top_bar.line.fill.background()
        
        tf_tb = top_bar.text_frame
        tf_tb.vertical_anchor = MSO_ANCHOR.MIDDLE
        p_tb = tf_tb.paragraphs[0]
        p_tb.alignment = PP_ALIGN.CENTER
        r_tb = p_tb.add_run()
        r_tb.text = "Noida Institute of Engineering and Technology, Greater Noida"
        r_tb.font.name = FONT_DISPLAY
        r_tb.font.size = Pt(20)
        r_tb.font.bold = True
        r_tb.font.color.rgb = COLOR_WHITE

        # Sub-banner tagline
        sub_banner = slide.shapes.add_textbox(Inches(0), Inches(0.85), Inches(13.333), Inches(0.35))
        p_sb = sub_banner.text_frame.paragraphs[0]
        p_sb.alignment = PP_ALIGN.CENTER
        r_sb = p_sb.add_run()
        r_sb.text = "(An Autonomous Institute Affiliated to AKTU, Lucknow  ·  Accredited by NAAC 'A' Grade)"
        r_sb.font.name = FONT_BODY
        r_sb.font.size = Pt(9.5)
        r_sb.font.color.rgb = COLOR_TEXT_MUTED

        # NIET Logo
        if os.path.exists(NIET_LOGO_PATH):
            slide.shapes.add_picture(NIET_LOGO_PATH, Inches(5.35), Inches(1.3), Inches(2.6), Inches(1.05))

        # Academic Metadata
        meta_box = slide.shapes.add_textbox(Inches(1.5), Inches(2.35), Inches(10.333), Inches(0.8))
        tf_m = meta_box.text_frame
        p_m1 = tf_m.paragraphs[0]
        p_m1.alignment = PP_ALIGN.CENTER
        r_m1 = p_m1.add_run()
        r_m1.text = "Department of Computer Science & Engineering (Artificial Intelligence)\n"
        r_m1.font.name = FONT_BODY
        r_m1.font.size = Pt(14)
        r_m1.font.bold = True
        r_m1.font.color.rgb = COLOR_TEXT_DARK

        r_m2 = p_m1.add_run()
        r_m2.text = "B.Tech CSE AI Twinning  ·  Semester III  ·  Academic Session 2026–2027  ·  SDG 4 (Quality Education)"
        r_m2.font.name = FONT_BODY
        r_m2.font.size = Pt(11)
        r_m2.font.color.rgb = COLOR_TEXT_MUTED

        # Project Title Display Box (Central Prominence)
        title_card = self.add_card(slide, Inches(1.5), Inches(3.2), Inches(10.333), Inches(1.85), bg_rgb=COLOR_PINK_TINT, border_rgb=COLOR_CARD_BORDER)
        
        tbox = slide.shapes.add_textbox(Inches(1.6), Inches(3.25), Inches(10.133), Inches(1.7))
        tf_t = tbox.text_frame
        tf_t.vertical_anchor = MSO_ANCHOR.MIDDLE
        
        p1 = tf_t.paragraphs[0]
        p1.alignment = PP_ALIGN.CENTER
        r_t1 = p1.add_run()
        r_t1.text = "“ACADEMIC PROJECT TRACKING SYSTEM”\n"
        r_t1.font.name = FONT_DISPLAY
        r_t1.font.size = Pt(26)
        r_t1.font.bold = True
        r_t1.font.color.rgb = COLOR_CRIMSON

        p2 = tf_t.add_paragraph()
        p2.alignment = PP_ALIGN.CENTER
        r_t2 = p2.add_run()
        r_t2.text = "ProjectPulse Enterprise  ·  Continuous Milestone & Assessment Platform\n"
        r_t2.font.name = FONT_BODY
        r_t2.font.size = Pt(14)
        r_t2.font.bold = True
        r_t2.font.color.rgb = COLOR_TEXT_DARK

        p3 = tf_t.add_paragraph()
        p3.alignment = PP_ALIGN.CENTER
        r_t3 = p3.add_run()
        r_t3.text = "Course: Object Oriented Techniques Using Java (CCSE0355)  |  Assignment Type: Capstone Project"
        r_t3.font.name = FONT_BODY
        r_t3.font.size = Pt(11)
        r_t3.font.italic = True
        r_t3.font.color.rgb = COLOR_TEXT_MUTED

        # 3 Bottom Columns (Submitted by, Submitted to, Under Guidance)
        col_w = Inches(3.85)
        gap = Inches(0.29)
        top_c = Inches(5.25)
        h_c = Inches(1.9)

        # Col 1: Submitted By
        c1 = self.add_card(slide, Inches(0.75), top_c, col_w, h_c, bg_rgb=COLOR_WHITE, border_rgb=COLOR_BORDER_SUBTLE)
        tb_c1 = slide.shapes.add_textbox(Inches(0.9), top_c + Inches(0.1), col_w - Inches(0.3), h_c - Inches(0.2))
        tf_c1 = tb_c1.text_frame
        p_c1 = tf_c1.paragraphs[0]
        r = p_c1.add_run()
        r.text = "Submitted by:\n"
        r.font.name = FONT_BODY
        r.font.size = Pt(11)
        r.font.bold = True
        r.font.color.rgb = COLOR_CRIMSON
        
        r = p_c1.add_run()
        r.text = "Group - 3 (B.Tech CSE AI Twinning)\n"
        r.font.name = FONT_BODY
        r.font.size = Pt(12)
        r.font.bold = True
        r.font.color.rgb = COLOR_TEXT_DARK

        r = p_c1.add_run()
        r.text = "• Samar Singh (Roll No. 42)\n• Aditi Singh (Roll No. 03)\n• Chhavi Attri (Roll No. 18)"
        r.font.name = FONT_BODY
        r.font.size = Pt(10.5)
        r.font.color.rgb = COLOR_TEXT_DARK

        # Col 2: Submitted To
        c2 = self.add_card(slide, Inches(0.75) + col_w + gap, top_c, col_w, h_c, bg_rgb=COLOR_WHITE, border_rgb=COLOR_BORDER_SUBTLE)
        tb_c2 = slide.shapes.add_textbox(Inches(0.9) + col_w + gap, top_c + Inches(0.1), col_w - Inches(0.3), h_c - Inches(0.2))
        tf_c2 = tb_c2.text_frame
        p_c2 = tf_c2.paragraphs[0]
        r = p_c2.add_run()
        r.text = "Submitted to:\n"
        r.font.name = FONT_BODY
        r.font.size = Pt(11)
        r.font.bold = True
        r.font.color.rgb = COLOR_CRIMSON
        
        r = p_c2.add_run()
        r.text = "Ms. Aparna Pandey\n"
        r.font.name = FONT_BODY
        r.font.size = Pt(13)
        r.font.bold = True
        r.font.color.rgb = COLOR_TEXT_DARK

        r = p_c2.add_run()
        r.text = "Faculty Mentor & Assistant Professor\nDepartment of CSE (AI)\nNIET Greater Noida"
        r.font.name = FONT_BODY
        r.font.size = Pt(10.5)
        r.font.color.rgb = COLOR_TEXT_MUTED

        # Col 3: Under Guidance
        c3 = self.add_card(slide, Inches(0.75) + (col_w + gap) * 2, top_c, col_w, h_c, bg_rgb=COLOR_WHITE, border_rgb=COLOR_BORDER_SUBTLE)
        tb_c3 = slide.shapes.add_textbox(Inches(0.9) + (col_w + gap) * 2, top_c + Inches(0.1), col_w - Inches(0.3), h_c - Inches(0.2))
        tf_c3 = tb_c3.text_frame
        p_c3 = tf_c3.paragraphs[0]
        r = p_c3.add_run()
        r.text = "Under Guidance:\n"
        r.font.name = FONT_BODY
        r.font.size = Pt(11)
        r.font.bold = True
        r.font.color.rgb = COLOR_CRIMSON
        
        r = p_c3.add_run()
        r.text = "Object Oriented Techniques Using Java\n"
        r.font.name = FONT_BODY
        r.font.size = Pt(12)
        r.font.bold = True
        r.font.color.rgb = COLOR_TEXT_DARK

        r = p_c3.add_run()
        r.text = "Course Code: CCSE0355\nAcademic Session: 2026–2027\nInstitution: NIET Greater Noida"
        r.font.name = FONT_BODY
        r.font.size = Pt(10.5)
        r.font.color.rgb = COLOR_TEXT_MUTED

    def build_slide_02_agenda(self):
        """Slide 2 — Table of Contents matching 1month ppt.pptx image2.png."""
        slide = self.add_slide()

        # Left Column Title & Branding
        l_box = slide.shapes.add_textbox(Inches(0.8), Inches(1.4), Inches(4.2), Inches(4.5))
        tf_l = l_box.text_frame
        tf_l.word_wrap = True
        
        p1 = tf_l.paragraphs[0]
        r = p1.add_run()
        r.text = "Table of\n"
        r.font.name = FONT_DISPLAY
        r.font.size = Pt(40)
        r.font.bold = True
        r.font.color.rgb = COLOR_TEXT_DARK

        r = p1.add_run()
        r.text = "Contents"
        r.font.name = FONT_DISPLAY
        r.font.size = Pt(44)
        r.font.bold = True
        r.font.color.rgb = COLOR_CRIMSON

        line = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(3.0), Inches(2.2), Pt(2.5))
        line.fill.solid()
        line.fill.fore_color.rgb = COLOR_CRIMSON
        line.line.fill.background()

        p2 = tf_l.add_paragraph()
        p2.space_before = Pt(24)
        r = p2.add_run()
        r.text = "A COMPREHENSIVE OVERVIEW OF OUR JAVA CAPSTONE PRESENTATION"
        r.font.name = FONT_BODY
        r.font.size = Pt(11)
        r.font.bold = True
        r.font.color.rgb = COLOR_TEXT_MUTED

        p3 = tf_l.add_paragraph()
        p3.space_before = Pt(12)
        r = p3.add_run()
        r.text = "ProjectPulse Enterprise: Engineered for transparent milestone tracking, continuous evaluation, and multi-tier dual persistence."
        r.font.name = FONT_BODY
        r.font.size = Pt(10)
        r.font.color.rgb = COLOR_TEXT_DARK

        # Top Right NIET Header
        if os.path.exists(NIET_LOGO_PATH):
            slide.shapes.add_picture(NIET_LOGO_PATH, Inches(11.3), Inches(0.3), Inches(1.4), Inches(0.6))
        
        top_r = slide.shapes.add_textbox(Inches(7.8), Inches(0.4), Inches(3.3), Inches(0.4))
        p_r = top_r.text_frame.paragraphs[0]
        p_r.alignment = PP_ALIGN.RIGHT
        r_r = p_r.add_run()
        r_r.text = "— LEARN  |  INNOVATE  |  TRANSFORM"
        r_r.font.name = FONT_BODY
        r_r.font.size = Pt(9.5)
        r_r.font.bold = True
        r_r.font.color.rgb = COLOR_TEXT_MUTED

        # Right Column: 5 Pill Cards matching template
        items = [
            ("01", "📋", "Project Introduction & Motivation", "Problem context, traditional dilemmas, and core project objectives."),
            ("02", "🏗️", "System Architecture & Tech Stack", "3-Tier MVC architecture, Java 17 LTS, Swing, FlatLaf & MySQL 8.x."),
            ("03", "☕", "Object-Oriented Design & Models", "Encapsulation, immutability, class hierarchy, and Singleton pattern."),
            ("04", "💻", "Core Workspaces & Dual Persistence", "Student feed, faculty grading console, MySQL & resilient fallback."),
            ("05", "📊", "Testing, Integrity & Future Scope", "Anti-cramming heuristics, 8 verified tests, and cloud roadmap.")
        ]

        top_start = Inches(1.2)
        card_h = Inches(0.92)
        card_gap = Inches(0.18)
        card_w = Inches(7.4)
        card_left = Inches(5.2)

        for i, (num, icon, title, desc) in enumerate(items):
            c_top = top_start + i * (card_h + card_gap)
            c = self.add_card(slide, card_left, c_top, card_w, card_h, bg_rgb=COLOR_WHITE, border_rgb=COLOR_BORDER_SUBTLE)
            
            # Number badge circle
            nb = slide.shapes.add_shape(MSO_SHAPE.OVAL, card_left + Inches(0.2), c_top + Inches(0.18), Inches(0.56), Inches(0.56))
            nb.fill.solid()
            nb.fill.fore_color.rgb = COLOR_PINK_TINT
            nb.line.color.rgb = COLOR_CARD_BORDER
            nb.line.width = Pt(1)
            tf_nb = nb.text_frame
            tf_nb.vertical_anchor = MSO_ANCHOR.MIDDLE
            p_nb = tf_nb.paragraphs[0]
            p_nb.text = num
            p_nb.font.name = FONT_BODY
            p_nb.font.size = Pt(12)
            p_nb.font.bold = True
            p_nb.font.color.rgb = COLOR_CRIMSON
            p_nb.alignment = PP_ALIGN.CENTER

            # Icon
            ib = slide.shapes.add_textbox(card_left + Inches(0.9), c_top + Inches(0.18), Inches(0.5), Inches(0.56))
            p_ib = ib.text_frame.paragraphs[0]
            p_ib.text = icon
            p_ib.font.size = Pt(16)
            p_ib.alignment = PP_ALIGN.CENTER

            # Content Text
            tb = slide.shapes.add_textbox(card_left + Inches(1.5), c_top + Inches(0.12), Inches(5.3), Inches(0.7))
            tf_b = tb.text_frame
            tf_b.margin_top = Inches(0)
            tf_b.margin_left = Inches(0)
            p_t = tf_b.paragraphs[0]
            r = p_t.add_run()
            r.text = title
            r.font.name = FONT_DISPLAY
            r.font.size = Pt(13)
            r.font.bold = True
            r.font.color.rgb = COLOR_TEXT_DARK

            p_d = tf_b.add_paragraph()
            r = p_d.add_run()
            r.text = desc
            r.font.name = FONT_BODY
            r.font.size = Pt(9.5)
            r.font.color.rgb = COLOR_TEXT_MUTED

            # Right chevron
            chv = slide.shapes.add_textbox(card_left + Inches(6.8), c_top + Inches(0.2), Inches(0.4), Inches(0.5))
            p_ch = chv.text_frame.paragraphs[0]
            r = p_ch.add_run()
            r.text = "›"
            r.font.name = FONT_DISPLAY
            r.font.size = Pt(22)
            r.font.bold = True
            r.font.color.rgb = COLOR_TEXT_DIM

        # Footer
        f_line = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.6), Inches(6.9), Inches(12.13), Pt(1))
        f_line.fill.solid()
        f_line.fill.fore_color.rgb = COLOR_BORDER_SUBTLE
        f_line.line.fill.background()

        f_box_l = slide.shapes.add_textbox(Inches(0.6), Inches(6.95), Inches(5.0), Inches(0.35))
        p_fl = f_box_l.text_frame.paragraphs[0]
        r_fl = p_fl.add_run()
        r_fl.text = "Department of CSE (AI)  |  Session 2026–27"
        r_fl.font.name = FONT_BODY
        r_fl.font.size = Pt(9)
        r_fl.font.color.rgb = COLOR_TEXT_MUTED

        f_box_r = slide.shapes.add_textbox(Inches(8.5), Inches(6.95), Inches(4.23), Inches(0.35))
        p_fr = f_box_r.text_frame.paragraphs[0]
        p_fr.alignment = PP_ALIGN.RIGHT
        r_fr = p_fr.add_run()
        r_fr.text = "— BUILDING A SMARTER TOMORROW  ·  02"
        r_fr.font.name = FONT_BODY
        r_fr.font.size = Pt(9.5)
        r_fr.font.bold = True
        r_fr.font.color.rgb = COLOR_CRIMSON

    def build_slide_03_intro(self):
        """Slide 3 — Project Introduction matching template image3.png."""
        slide = self.add_slide()
        self.draw_header(slide, "03", "Project", "Introduction")

        col_w = Inches(3.8)
        gap = Inches(0.3)
        top_y = Inches(1.5)
        h_y = Inches(4.35)

        # Card 1: Background
        c1 = self.add_card(slide, Inches(0.6), top_y, col_w, h_y)
        self.add_chip(slide, Inches(0.85), top_y + Inches(0.2), "CONTEXT", COLOR_PINK_TINT, COLOR_CRIMSON)
        
        tb = slide.shapes.add_textbox(Inches(0.85), top_y + Inches(0.6), col_w - Inches(0.5), h_y - Inches(0.8))
        tf = tb.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        r = p.add_run()
        r.text = "Background\n"
        r.font.name = FONT_DISPLAY
        r.font.size = Pt(16)
        r.font.bold = True
        r.font.color.rgb = COLOR_TEXT_DARK

        line = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.85), top_y + Inches(1.05), Inches(1.2), Pt(1.5))
        line.fill.solid()
        line.fill.fore_color.rgb = COLOR_CRIMSON
        line.line.fill.background()

        p2 = tf.add_paragraph()
        p2.space_before = Pt(18)
        r = p2.add_run()
        r.text = "Universities generate hundreds of student projects annually. Traditional monitoring methods rely on manual paper diaries, unorganized spreadsheets, and eleventh-hour submissions that obscure genuine, iterative learning.\n\nWithout continuous checkpoints, department coordinators struggle to identify off-track teams early in the semester."
        r.font.name = FONT_BODY
        r.font.size = Pt(10.5)
        r.font.color.rgb = COLOR_TEXT_DARK

        # Card 2: Motivation
        c2 = self.add_card(slide, Inches(0.6) + col_w + gap, top_y, col_w, h_y)
        self.add_chip(slide, Inches(0.6) + col_w + gap + Inches(0.25), top_y + Inches(0.2), "RATIONALE", COLOR_PINK_TINT, COLOR_CRIMSON)

        tb2 = slide.shapes.add_textbox(Inches(0.6) + col_w + gap + Inches(0.25), top_y + Inches(0.6), col_w - Inches(0.5), h_y - Inches(0.8))
        tf2 = tb2.text_frame
        tf2.word_wrap = True
        p = tf2.paragraphs[0]
        r = p.add_run()
        r.text = "Motivation\n"
        r.font.name = FONT_DISPLAY
        r.font.size = Pt(16)
        r.font.bold = True
        r.font.color.rgb = COLOR_TEXT_DARK

        line2 = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.6) + col_w + gap + Inches(0.25), top_y + Inches(1.05), Inches(1.2), Pt(1.5))
        line2.fill.solid()
        line2.fill.fore_color.rgb = COLOR_CRIMSON
        line2.line.fill.background()

        p2 = tf2.add_paragraph()
        p2.space_before = Pt(18)
        r = p2.add_run()
        r.text = "Many students assemble projects in the final 48 hours prior to defense, bypassing methodical software development life cycles.\n\nFaculty members need an immutable, transparent platform that verifies incremental effort over time, rewards consistent work, and provides structured channels for milestone feedback and continuous grading."
        r.font.name = FONT_BODY
        r.font.size = Pt(10.5)
        r.font.color.rgb = COLOR_TEXT_DARK

        # Card 3: Objective & Quote
        c3 = self.add_card(slide, Inches(0.6) + (col_w + gap) * 2, top_y, col_w, h_y)
        self.add_chip(slide, Inches(0.6) + (col_w + gap) * 2 + Inches(0.25), top_y + Inches(0.2), "MISSION", COLOR_PINK_TINT, COLOR_CRIMSON)

        tb3 = slide.shapes.add_textbox(Inches(0.6) + (col_w + gap) * 2 + Inches(0.25), top_y + Inches(0.6), col_w - Inches(0.5), Inches(1.8))
        tf3 = tb3.text_frame
        tf3.word_wrap = True
        p = tf3.paragraphs[0]
        r = p.add_run()
        r.text = "Core Objectives\n"
        r.font.name = FONT_DISPLAY
        r.font.size = Pt(16)
        r.font.bold = True
        r.font.color.rgb = COLOR_TEXT_DARK

        line3 = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.6) + (col_w + gap) * 2 + Inches(0.25), top_y + Inches(1.05), Inches(1.2), Pt(1.5))
        line3.fill.solid()
        line3.fill.fore_color.rgb = COLOR_CRIMSON
        line3.line.fill.background()

        p2 = tf3.add_paragraph()
        p2.space_before = Pt(16)
        r = p2.add_run()
        r.text = "• Java 17 LTS Desktop Platform\n• Dual Student & Teacher Workspaces\n• Tamper-Proof Milestone Locking\n• Automated Anti-Cramming Alerts\n• MySQL + Local Fallback Persistence"
        r.font.name = FONT_BODY
        r.font.size = Pt(10)
        r.font.color.rgb = COLOR_TEXT_DARK

        # Vision Quote Card inside Card 3
        qc = self.add_card(slide, Inches(0.6) + (col_w + gap) * 2 + Inches(0.2), top_y + Inches(2.55), col_w - Inches(0.4), Inches(1.6), bg_rgb=COLOR_PINK_TINT, border_rgb=COLOR_CARD_BORDER)
        tb_q = slide.shapes.add_textbox(Inches(0.6) + (col_w + gap) * 2 + Inches(0.35), top_y + Inches(2.65), col_w - Inches(0.7), Inches(1.4))
        tf_q = tb_q.text_frame
        tf_q.word_wrap = True
        p_q = tf_q.paragraphs[0]
        r = p_q.add_run()
        r.text = "“Better tracking today, brighter research tomorrow.”\n"
        r.font.name = FONT_DISPLAY
        r.font.size = Pt(12)
        r.font.bold = True
        r.font.color.rgb = COLOR_CRIMSON

        p_qa = tf_q.add_paragraph()
        r = p_qa.add_run()
        r.text = "— ProjectPulse Core Philosophy"
        r.font.name = FONT_BODY
        r.font.size = Pt(9.5)
        r.font.italic = True
        r.font.color.rgb = COLOR_TEXT_MUTED

        self.add_bottom_bar(slide, "Guiding Vision:", "Transforming academic project evaluations from opaque end-semester dumps into transparent, continuous learning milestones.", "💡")

    def build_slide_04_problem_statement(self):
        """Slide 4 — Problem Statement."""
        slide = self.add_slide()
        self.draw_header(slide, "04", "Problem", "Statement")

        problems = [
            ("Scattered Communication", "Project updates and requirements are fragmented across WhatsApp groups, email threads, paper project diaries, and sticky notes, causing lost institutional context."),
            ("Untracked Incremental Work", "Faculty advisors cannot verify whether a delivered project represents four months of methodical problem-solving or 48 hours of last-minute assembly."),
            ("Review & Grading Bottlenecks", "Supervising 40+ project teams simultaneously creates immense administrative overhead, leading to delayed feedback and missed milestone deadlines."),
            ("Inadequate Central Reporting", "Department heads lack real-time cohort visibility into completion percentages, delayed teams, and at-risk candidates requiring urgent intervention.")
        ]

        card_w = Inches(5.9)
        card_h = Inches(1.95)
        top_y = Inches(1.55)
        gap_x = Inches(0.33)
        gap_y = Inches(0.22)

        for i, (title, desc) in enumerate(problems):
            row = i // 2
            col = i % 2
            x = Inches(0.6) + col * (card_w + gap_x)
            y = top_y + row * (card_h + gap_y)

            c = self.add_card(slide, x, y, card_w, card_h)
            
            # Icon badge
            ib = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x + Inches(0.25), y + Inches(0.25), Inches(0.55), Inches(0.55))
            ib.fill.solid()
            ib.fill.fore_color.rgb = COLOR_RED_BG
            ib.line.fill.background()
            p_i = ib.text_frame.paragraphs[0]
            p_i.text = f"P{i+1}"
            p_i.font.name = FONT_BODY
            p_i.font.size = Pt(11)
            p_i.font.bold = True
            p_i.font.color.rgb = COLOR_RED_TEXT
            p_i.alignment = PP_ALIGN.CENTER

            # Text box
            tb = slide.shapes.add_textbox(x + Inches(0.95), y + Inches(0.2), card_w - Inches(1.15), card_h - Inches(0.3))
            tf = tb.text_frame
            tf.word_wrap = True
            p = tf.paragraphs[0]
            r = p.add_run()
            r.text = title + "\n"
            r.font.name = FONT_DISPLAY
            r.font.size = Pt(13)
            r.font.bold = True
            r.font.color.rgb = COLOR_TEXT_DARK

            p2 = tf.add_paragraph()
            p2.space_before = Pt(4)
            r = p2.add_run()
            r.text = desc
            r.font.name = FONT_BODY
            r.font.size = Pt(9.5)
            r.font.color.rgb = COLOR_TEXT_MUTED

        self.add_bottom_bar(slide, "Target Problem Scope:", "Addressing subjective end-of-semester evaluation through transparent, verifiable milestone histories and role-tailored consoles.", "🎯")

    def build_slide_05_objectives(self):
        """Slide 5 — Objectives & Scope."""
        slide = self.add_slide()
        self.draw_header(slide, "05", "Project", "Objectives")

        objectives = [
            ("Object-Oriented Architecture", "Apply core Java OOP principles (Encapsulation, Immutability, Separation of Concerns, Singleton Pattern) to mirror real-world academic workflows."),
            ("Role-Based Workspaces", "Deliver tailored environments: Student Workspace for iterative milestone capture and Teacher Assessment Console for continuous evaluation."),
            ("Dynamic Lifecycle & Heuristics", "Implement automated project status resolution (Not Started, In Progress, At Risk, Overdue, Completed) and anti-cramming detection algorithms."),
            ("Dual-Persistence Engine", "Guarantee continuous availability through seamless failover between enterprise MySQL 8.x relational storage and local object serialization with rolling backups.")
        ]

        card_w = Inches(2.8)
        card_h = Inches(4.25)
        top_y = Inches(1.55)
        gap = Inches(0.31)

        for i, (title, desc) in enumerate(objectives):
            x = Inches(0.6) + i * (card_w + gap)
            c = self.add_card(slide, x, top_y, card_w, card_h)
            
            # Step badge
            sb = slide.shapes.add_shape(MSO_SHAPE.OVAL, x + Inches(0.2), top_y + Inches(0.2), Inches(0.55), Inches(0.55))
            sb.fill.solid()
            sb.fill.fore_color.rgb = COLOR_PINK_TINT
            sb.line.color.rgb = COLOR_CARD_BORDER
            sb.line.width = Pt(1)
            p_s = sb.text_frame.paragraphs[0]
            p_s.text = f"0{i+1}"
            p_s.font.name = FONT_DISPLAY
            p_s.font.size = Pt(11)
            p_s.font.bold = True
            p_s.font.color.rgb = COLOR_CRIMSON
            p_s.alignment = PP_ALIGN.CENTER

            tb = slide.shapes.add_textbox(x + Inches(0.2), top_y + Inches(0.9), card_w - Inches(0.4), card_h - Inches(1.0))
            tf = tb.text_frame
            tf.word_wrap = True
            p = tf.paragraphs[0]
            r = p.add_run()
            r.text = title + "\n\n"
            r.font.name = FONT_DISPLAY
            r.font.size = Pt(13)
            r.font.bold = True
            r.font.color.rgb = COLOR_TEXT_DARK

            p2 = tf.add_paragraph()
            r = p2.add_run()
            r.text = desc
            r.font.name = FONT_BODY
            r.font.size = Pt(9.5)
            r.font.color.rgb = COLOR_TEXT_MUTED

        self.add_bottom_bar(slide, "Design Target:", "Developing a robust, production-ready desktop platform that elevates academic governance and research productivity.", "⚡")

    def build_slide_06_proposed_system(self):
        """Slide 6 — Proposed System & End-to-End Workflow."""
        slide = self.add_slide()
        self.draw_header(slide, "06", "Proposed", "System")

        # 8-step pipeline
        steps = [
            ("1. Auth & Login", "Student signs into workspace via SHA-256 credentials."),
            ("2. Project View", "Selects project & reviews active milestones timeline."),
            ("3. Submit Update", "Captures work done, blockers & planned next steps."),
            ("4. Dual Sync", "Update committed to MySQL or serialized locally."),
            ("5. Auto Status", "Dynamic rules evaluate progress against deadline."),
            ("6. Teacher Review", "Faculty reviews deliverables & evaluates on 0–100 scale."),
            ("7. Milestone Lock", "Submission frozen as immutable evaluation artifact."),
            ("8. Cohort Export", "Generates consolidated CSV & executive text reports.")
        ]

        top_y1 = Inches(1.6)
        top_y2 = Inches(3.7)
        card_w = Inches(2.8)
        card_h = Inches(1.8)
        gap = Inches(0.31)

        for i, (title, desc) in enumerate(steps[:4]):
            x = Inches(0.6) + i * (card_w + gap)
            c = self.add_card(slide, x, top_y1, card_w, card_h)
            self.add_chip(slide, x + Inches(0.2), top_y1 + Inches(0.18), f"PHASE {i+1}", COLOR_PINK_TINT, COLOR_CRIMSON)
            
            tb = slide.shapes.add_textbox(x + Inches(0.2), top_y1 + Inches(0.55), card_w - Inches(0.4), card_h - Inches(0.65))
            tf = tb.text_frame
            tf.word_wrap = True
            p = tf.paragraphs[0]
            r = p.add_run()
            r.text = title + "\n"
            r.font.name = FONT_DISPLAY
            r.font.size = Pt(12)
            r.font.bold = True
            r.font.color.rgb = COLOR_TEXT_DARK

            p2 = tf.add_paragraph()
            r = p2.add_run()
            r.text = desc
            r.font.name = FONT_BODY
            r.font.size = Pt(9)
            r.font.color.rgb = COLOR_TEXT_MUTED

        for i, (title, desc) in enumerate(steps[4:]):
            x = Inches(0.6) + i * (card_w + gap)
            c = self.add_card(slide, x, top_y2, card_w, card_h)
            self.add_chip(slide, x + Inches(0.2), top_y2 + Inches(0.18), f"PHASE {i+5}", COLOR_BLUE_BG, COLOR_BLUE_TEXT)
            
            tb = slide.shapes.add_textbox(x + Inches(0.2), top_y2 + Inches(0.55), card_w - Inches(0.4), card_h - Inches(0.65))
            tf = tb.text_frame
            tf.word_wrap = True
            p = tf.paragraphs[0]
            r = p.add_run()
            r.text = title + "\n"
            r.font.name = FONT_DISPLAY
            r.font.size = Pt(12)
            r.font.bold = True
            r.font.color.rgb = COLOR_TEXT_DARK

            p2 = tf.add_paragraph()
            r = p2.add_run()
            r.text = desc
            r.font.name = FONT_BODY
            r.font.size = Pt(9)
            r.font.color.rgb = COLOR_TEXT_MUTED

        self.add_bottom_bar(slide, "End-to-End Governance:", "From initial registration to cohort-wide reporting, every interaction forms a tamper-proof continuous audit trail.", "🔄")

    def build_slide_07_system_architecture(self):
        """Slide 7 — System Architecture (3-Tier Layered Design)."""
        slide = self.add_slide()
        self.draw_header(slide, "07", "System", "Architecture")

        tiers = [
            ("Presentation Tier (GUI & Views)", [
                ("GUIApp.java", "Splash screen, auth portal & role routing engine"),
                ("StudentDashboard.java", "Projects table, milestone timeline, velocity gauges"),
                ("TeacherDashboard.java", "Cohort distribution, grading sliders, report exports"),
                ("UITheme.java", "Adaptive dark/light styling, Inter typography, icon rendering")
            ], COLOR_PINK_TINT, COLOR_CRIMSON),
            ("Business & Domain Tier (Logic & Models)", [
                ("Project.java", "Lifecycle resolution, priority tags, anti-dump checks"),
                ("ProgressUpdate.java", "Milestone entities, immutable timestamps, audit locking"),
                ("User.java", "RBAC credentials, SHA-256 digest validation"),
                ("Enums (Priority & Status)", "LOW/MED/HIGH priority & 5-state lifecycle resolution")
            ], COLOR_BLUE_BG, COLOR_BLUE_TEXT),
            ("Persistence Tier (Dual Engine & Storage)", [
                ("DatabaseManager.java", "JDBC Singleton, auto-schema migration & connection pool"),
                ("ProgressFileManager.java", "Dual-engine sync coordinator & automatic failover"),
                ("MySQL 8.x Database", "Normalized relational tables, foreign keys, cascade rules"),
                ("Local Serialized Storage", "projects.dat fallback + 5 rolling timestamped backups")
            ], COLOR_GREEN_BG, COLOR_GREEN_TEXT)
        ]

        card_w = Inches(3.8)
        card_h = Inches(4.25)
        top_y = Inches(1.55)
        gap = Inches(0.36)

        for i, (tier_title, components, chip_bg, chip_text) in enumerate(tiers):
            x = Inches(0.6) + i * (card_w + gap)
            c = self.add_card(slide, x, top_y, card_w, card_h)
            self.add_chip(slide, x + Inches(0.2), top_y + Inches(0.2), f"TIER 0{i+1}", chip_bg, chip_text)

            tb = slide.shapes.add_textbox(x + Inches(0.2), top_y + Inches(0.6), card_w - Inches(0.4), Inches(0.6))
            p = tb.text_frame.paragraphs[0]
            r = p.add_run()
            r.text = tier_title
            r.font.name = FONT_DISPLAY
            r.font.size = Pt(12)
            r.font.bold = True
            r.font.color.rgb = COLOR_TEXT_DARK

            # Inner items
            y_item = top_y + Inches(1.25)
            for comp_name, comp_desc in components:
                ic = self.add_card(slide, x + Inches(0.18), y_item, card_w - Inches(0.36), Inches(0.65), bg_rgb=COLOR_WHITE, border_rgb=COLOR_BORDER_SUBTLE)
                tb_i = slide.shapes.add_textbox(x + Inches(0.25), y_item + Inches(0.05), card_w - Inches(0.5), Inches(0.55))
                tf_i = tb_i.text_frame
                tf_i.margin_top = Inches(0)
                p_cn = tf_i.paragraphs[0]
                r = p_cn.add_run()
                r.text = comp_name + "\n"
                r.font.name = FONT_MONO
                r.font.size = Pt(9.5)
                r.font.bold = True
                r.font.color.rgb = COLOR_CRIMSON if i == 0 else (COLOR_BLUE_TEXT if i == 1 else COLOR_GREEN_TEXT)

                p_cd = tf_i.add_paragraph()
                r = p_cd.add_run()
                r.text = comp_desc
                r.font.name = FONT_BODY
                r.font.size = Pt(8.5)
                r.font.color.rgb = COLOR_TEXT_MUTED
                y_item += Inches(0.72)

        self.add_bottom_bar(slide, "Architectural Decoupling:", "Strict separation of concerns guarantees UI views operate independently from domain logic and storage engines.", "🏛️")

    def build_slide_08_tech_stack(self):
        """Slide 8 — Technology Stack matching template image6.png."""
        slide = self.add_slide()
        self.draw_header(slide, "08", "Technology", "Stack")

        techs = [
            ("☕ Java 17 LTS", "Language Runtime", "Modern pattern matching, record types, immutable collections, and long-term enterprise platform stability."),
            ("🖥️ Java Swing", "GUI Framework", "Native cross-platform desktop UI framework with hardware acceleration and event-driven architecture."),
            ("🎨 FlatLaf", "Look & Feel", "Contemporary clean Look & Feel library providing adaptive light/dark mode theming and high-DPI scaling."),
            ("🐬 MySQL 8.x", "Relational Database", "ACID-compliant relational database engine managing normalized tables, foreign constraints, and indexing."),
            ("🔌 JDBC Driver", "Data Access", "Type-4 pure Java driver connection pooling enabling fast SQL CRUD transactions and schema migration."),
            ("💾 Serialization", "Resilient Fallback", "Java Object Serialization (projects.dat) with 5-level rolling disaster recovery snapshots.")
        ]

        card_w = Inches(1.85)
        card_h = Inches(4.25)
        top_y = Inches(1.55)
        gap = Inches(0.2)

        for i, (title, role, desc) in enumerate(techs):
            x = Inches(0.6) + i * (card_w + gap)
            c = self.add_card(slide, x, top_y, card_w, card_h)
            
            # Header
            tb = slide.shapes.add_textbox(x + Inches(0.12), top_y + Inches(0.2), card_w - Inches(0.24), card_h - Inches(0.4))
            tf = tb.text_frame
            tf.word_wrap = True
            
            p = tf.paragraphs[0]
            r = p.add_run()
            r.text = title + "\n"
            r.font.name = FONT_DISPLAY
            r.font.size = Pt(11)
            r.font.bold = True
            r.font.color.rgb = COLOR_TEXT_DARK

            p_r = tf.add_paragraph()
            r = p_r.add_run()
            r.text = role + "\n\n"
            r.font.name = FONT_BODY
            r.font.size = Pt(8.5)
            r.font.bold = True
            r.font.color.rgb = COLOR_CRIMSON

            p_d = tf.add_paragraph()
            r = p_d.add_run()
            r.text = desc
            r.font.name = FONT_BODY
            r.font.size = Pt(8.5)
            r.font.color.rgb = COLOR_TEXT_MUTED

        self.add_bottom_bar(slide, "Technology Rationale:", "Selected for maximum desktop responsiveness, rock-solid stability, zero cloud runtime cost, and zero external baggage.", "⚙️")

    def build_slide_09_oops_concepts(self):
        """Slide 9 — Object-Oriented Programming (OOP) Principles Applied."""
        slide = self.add_slide()
        self.draw_header(slide, "09", "OOP", "Concepts")

        pillars = [
            ("Encapsulation & Validation", "All entity fields in Project and User are marked private. Collections (tags, progressHistory) use defensive copying. Mutators like setGrade(int) strictly enforce boundary conditions (0 ≤ grade ≤ 100)."),
            ("Immutability & Audit Integrity", "Audit timestamps in ProgressUpdate are declared final and bound at construction time (submittedOn = LocalDateTime.now()). Prevents retrospective tampering with submission dates."),
            ("Polymorphism & Custom UI", "Swing component hierarchy overrides custom painting engines (paintComponent(Graphics g)) throughout UITheme and dashboards to deliver adaptive dark/light surfaces."),
            ("Separation of Concerns (SoC)", "UI styling is strictly decoupled into UITheme, relational migrations into DatabaseManager, and file recovery into ProgressFileManager without leaky abstractions."),
            ("Singleton Design Pattern", "DatabaseManager enforces a private constructor with a thread-safe static getInstance() accessor, centralizing database connection pooling and preventing connection leaks.")
        ]

        card_w = Inches(12.13)
        card_h = Inches(0.78)
        top_y = Inches(1.55)
        gap = Inches(0.12)

        for i, (title, desc) in enumerate(pillars):
            y = top_y + i * (card_h + gap)
            c = self.add_card(slide, Inches(0.6), y, card_w, card_h)

            # Icon badge
            ib = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.78), y + Inches(0.14), Inches(0.5), Inches(0.5))
            ib.fill.solid()
            ib.fill.fore_color.rgb = COLOR_PINK_TINT
            ib.line.fill.background()
            p_i = ib.text_frame.paragraphs[0]
            p_i.text = f"OOP{i+1}"
            p_i.font.name = FONT_BODY
            p_i.font.size = Pt(8)
            p_i.font.bold = True
            p_i.font.color.rgb = COLOR_CRIMSON
            p_i.alignment = PP_ALIGN.CENTER

            tb = slide.shapes.add_textbox(Inches(1.4), y + Inches(0.08), card_w - Inches(1.6), card_h - Inches(0.16))
            tf = tb.text_frame
            tf.word_wrap = True
            p = tf.paragraphs[0]
            r = p.add_run()
            r.text = title + ": "
            r.font.name = FONT_DISPLAY
            r.font.size = Pt(11)
            r.font.bold = True
            r.font.color.rgb = COLOR_TEXT_DARK

            r2 = p.add_run()
            r2.text = desc
            r2.font.name = FONT_BODY
            r2.font.size = Pt(9.5)
            r2.font.color.rgb = COLOR_TEXT_MUTED

        self.add_bottom_bar(slide, "Pedagogical Core:", "Applying textbook object-oriented tenets directly to solve mission-critical academic data governance challenges.", "🎓")

    def build_slide_10_class_diagram(self):
        """Slide 10 — Class Diagram & Domain Model."""
        slide = self.add_slide()
        self.draw_header(slide, "10", "Domain", "Models")

        # 3 main UML Cards: User, Project, ProgressUpdate
        uml_classes = [
            ("User.java", [
                ("- username: String (PK)", COLOR_TEXT_DARK),
                ("- name: String", COLOR_TEXT_DARK),
                ("- passwordHash: String", COLOR_TEXT_DARK),
                ("- role: String", COLOR_TEXT_DARK),
                ("+ checkPassword(String): boolean", COLOR_CRIMSON),
                ("+ changePassword(String): void", COLOR_CRIMSON),
                ("+ isTeacher(): boolean", COLOR_CRIMSON),
                ("+ isStudent(): boolean", COLOR_CRIMSON)
            ]),
            ("Project.java", [
                ("- id: int (PK)", COLOR_TEXT_DARK),
                ("- title: String", COLOR_TEXT_DARK),
                ("- studentName: String (FK)", COLOR_TEXT_DARK),
                ("- deadline: LocalDate", COLOR_TEXT_DARK),
                ("- priority: Priority", COLOR_TEXT_DARK),
                ("- progressHistory: List<ProgressUpdate>", COLOR_TEXT_DARK),
                ("+ getStatus(): Status", COLOR_CRIMSON),
                ("+ getLatestProgress(): int", COLOR_CRIMSON),
                ("+ isLastMinuteDump(int): boolean", COLOR_CRIMSON),
                ("+ addProgressUpdate(ProgressUpdate): void", COLOR_CRIMSON)
            ]),
            ("ProgressUpdate.java", [
                ("- updateId: int", COLOR_TEXT_DARK),
                ("- submittedOn: LocalDateTime (final)", COLOR_TEXT_DARK),
                ("- progressPercentage: int", COLOR_TEXT_DARK),
                ("- currentStage: String", COLOR_TEXT_DARK),
                ("- workCompleted: List<String>", COLOR_TEXT_DARK),
                ("- problemsFaced: List<String>", COLOR_TEXT_DARK),
                ("- locked: boolean", COLOR_TEXT_DARK),
                ("+ lock(): void", COLOR_CRIMSON),
                ("+ unlock(): void", COLOR_CRIMSON),
                ("+ setTeacherFeedback(String): void", COLOR_CRIMSON)
            ])
        ]

        card_w = Inches(3.8)
        card_h = Inches(4.25)
        top_y = Inches(1.55)
        gap = Inches(0.36)

        for i, (cname, members) in enumerate(uml_classes):
            x = Inches(0.6) + i * (card_w + gap)
            c = self.add_card(slide, x, top_y, card_w, card_h)
            
            # Header bar of UML card
            hbar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, x, top_y, card_w, Inches(0.55))
            hbar.fill.solid()
            hbar.fill.fore_color.rgb = COLOR_PINK_TINT
            hbar.line.fill.background()
            p_h = hbar.text_frame.paragraphs[0]
            p_h.text = cname
            p_h.font.name = FONT_MONO
            p_h.font.size = Pt(11)
            p_h.font.bold = True
            p_h.font.color.rgb = COLOR_CRIMSON
            p_h.alignment = PP_ALIGN.CENTER

            tb = slide.shapes.add_textbox(x + Inches(0.15), top_y + Inches(0.6), card_w - Inches(0.3), card_h - Inches(0.7))
            tf = tb.text_frame
            tf.word_wrap = True
            for mtext, mcolor in members:
                p = tf.add_paragraph() if tf.paragraphs[0].text else tf.paragraphs[0]
                r = p.add_run()
                r.text = mtext
                r.font.name = FONT_MONO
                r.font.size = Pt(8.5)
                r.font.color.rgb = mcolor

        self.add_bottom_bar(slide, "Domain Relationships:", "User (1) owns/oversees Projects (0..*); Project (1) contains ProgressUpdates (0..*) via composition.", "🔗")

    def build_slide_11_student_dashboard(self):
        """Slide 11 — Student Workspace & Milestone Tracking."""
        slide = self.add_slide()
        self.draw_header(slide, "11", "Student", "Workspace")

        features = [
            ("📁 Project Explorer & Overview", "Color-coded status badges (In Progress, At Risk, Completed, Overdue), priority indicators (High, Med, Low), and deadline countdown watches."),
            ("📝 Milestone Submission Dialog", "Comprehensive submission interface capturing current stage, deliverables checklist, blockers faced, planned next steps, and document references."),
            ("⏱️ Interactive Milestone Feed", "Chronological vertical timeline displaying milestone badges, progress percentage completion, teacher comments, and reaction badges."),
            ("📊 Velocity & Analytics Gauges", "Real-time personal completion metrics, total submitted milestones, locked status audit indicators, and days-remaining alerts.")
        ]

        card_w = Inches(5.9)
        card_h = Inches(1.95)
        top_y = Inches(1.55)
        gap_x = Inches(0.33)
        gap_y = Inches(0.22)

        for i, (title, desc) in enumerate(features):
            row = i // 2
            col = i % 2
            x = Inches(0.6) + col * (card_w + gap_x)
            y = top_y + row * (card_h + gap_y)

            c = self.add_card(slide, x, y, card_w, card_h)
            tb = slide.shapes.add_textbox(x + Inches(0.25), y + Inches(0.2), card_w - Inches(0.5), card_h - Inches(0.4))
            tf = tb.text_frame
            tf.word_wrap = True
            p = tf.paragraphs[0]
            r = p.add_run()
            r.text = title + "\n"
            r.font.name = FONT_DISPLAY
            r.font.size = Pt(13)
            r.font.bold = True
            r.font.color.rgb = COLOR_TEXT_DARK

            p2 = tf.add_paragraph()
            p2.space_before = Pt(6)
            r = p2.add_run()
            r.text = desc
            r.font.name = FONT_BODY
            r.font.size = Pt(9.5)
            r.font.color.rgb = COLOR_TEXT_MUTED

        self.add_bottom_bar(slide, "Student Empowerment:", "Encouraging continuous momentum by decomposing semester-long projects into manageable, reviewable milestones.", "🚀")

    def build_slide_12_faculty_console(self):
        """Slide 12 — Faculty Assessment Console."""
        slide = self.add_slide()
        self.draw_header(slide, "12", "Faculty", "Console")

        features = [
            ("👥 Cohort Overview & Filtering", "High-level department-wide table displaying all active student projects with multi-criteria filters (Priority, Status, Grade State, Delayed)."),
            ("🎯 Continuous 0–100 Grading Suite", "Smooth interactive evaluation sliders, automated letter grade computation (A+ to F), and custom teacher feedback notes."),
            ("🏷️ Feedback Preset Chips & Badges", "One-click feedback presets ('Outstanding delivery', 'Expand testing', 'On schedule') and student recognition badges (Great Progress, Needs Work)."),
            ("🔒 Milestone Locking Mechanism", "Allows faculty to freeze student submissions upon review, preventing post-evaluation retrospective tampering and guaranteeing audit compliance.")
        ]

        card_w = Inches(5.9)
        card_h = Inches(1.95)
        top_y = Inches(1.55)
        gap_x = Inches(0.33)
        gap_y = Inches(0.22)

        for i, (title, desc) in enumerate(features):
            row = i // 2
            col = i % 2
            x = Inches(0.6) + col * (card_w + gap_x)
            y = top_y + row * (card_h + gap_y)

            c = self.add_card(slide, x, y, card_w, card_h)
            tb = slide.shapes.add_textbox(x + Inches(0.25), y + Inches(0.2), card_w - Inches(0.5), card_h - Inches(0.4))
            tf = tb.text_frame
            tf.word_wrap = True
            p = tf.paragraphs[0]
            r = p.add_run()
            r.text = title + "\n"
            r.font.name = FONT_DISPLAY
            r.font.size = Pt(13)
            r.font.bold = True
            r.font.color.rgb = COLOR_TEXT_DARK

            p2 = tf.add_paragraph()
            p2.space_before = Pt(6)
            r = p2.add_run()
            r.text = desc
            r.font.name = FONT_BODY
            r.font.size = Pt(9.5)
            r.font.color.rgb = COLOR_TEXT_MUTED

        self.add_bottom_bar(slide, "Continuous Evaluation:", "Equipping faculty with granular visibility to guide struggling students and reward sustained, authentic development.", "👩‍🏫")

    def build_slide_13_database_design(self):
        """Slide 13 — Database Design & Entity Relationships."""
        slide = self.add_slide()
        self.draw_header(slide, "13", "Database", "Design")

        tables = [
            ("users (User Accounts)", [
                ("username", "VARCHAR(100)", "PRIMARY KEY"),
                ("name", "VARCHAR(150)", "NOT NULL"),
                ("password_hash", "VARCHAR(100)", "SHA-256 Digest"),
                ("role", "VARCHAR(20)", "STUDENT / TEACHER"),
                ("registered_on", "DATE", "Registration Date")
            ]),
            ("projects (Project Headers)", [
                ("id", "INT", "PK, AUTO_INCREMENT"),
                ("title", "VARCHAR(255)", "Project Title"),
                ("student_name", "VARCHAR(100)", "FK -> users.username"),
                ("deadline", "DATE", "Scheduled Deadline"),
                ("priority", "VARCHAR(20)", "LOW / MEDIUM / HIGH"),
                ("grade", "INT", "Score (0 - 100)")
            ]),
            ("progress_updates (Milestones)", [
                ("id", "INT", "PK, AUTO_INCREMENT"),
                ("project_id", "INT", "FK -> projects.id"),
                ("progress_percentage", "INT", "Self-reported (0-100)"),
                ("current_stage", "VARCHAR(150)", "Active Phase"),
                ("locked", "BOOLEAN", "Audit Freeze Flag"),
                ("submitted_on", "DATETIME", "Immutable Timestamp")
            ])
        ]

        card_w = Inches(3.8)
        card_h = Inches(4.25)
        top_y = Inches(1.55)
        gap = Inches(0.36)

        for i, (tname, cols) in enumerate(tables):
            x = Inches(0.6) + i * (card_w + gap)
            c = self.add_card(slide, x, top_y, card_w, card_h)
            
            hbar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, x, top_y, card_w, Inches(0.55))
            hbar.fill.solid()
            hbar.fill.fore_color.rgb = COLOR_PINK_TINT
            hbar.line.fill.background()
            p_h = hbar.text_frame.paragraphs[0]
            p_h.text = tname
            p_h.font.name = FONT_MONO
            p_h.font.size = Pt(10)
            p_h.font.bold = True
            p_h.font.color.rgb = COLOR_CRIMSON
            p_h.alignment = PP_ALIGN.CENTER

            tb = slide.shapes.add_textbox(x + Inches(0.12), top_y + Inches(0.6), card_w - Inches(0.24), card_h - Inches(0.7))
            tf = tb.text_frame
            tf.word_wrap = True
            for col_name, col_type, col_desc in cols:
                p = tf.add_paragraph() if tf.paragraphs[0].text else tf.paragraphs[0]
                r = p.add_run()
                r.text = f"{col_name} "
                r.font.name = FONT_MONO
                r.font.size = Pt(9)
                r.font.bold = True
                r.font.color.rgb = COLOR_TEXT_DARK

                r2 = p.add_run()
                r2.text = f"({col_type})\n"
                r2.font.name = FONT_MONO
                r2.font.size = Pt(8)
                r2.font.color.rgb = COLOR_CRIMSON

                p_sub = tf.add_paragraph()
                r3 = p_sub.add_run()
                r3.text = f"  └ {col_desc}"
                r3.font.name = FONT_BODY
                r3.font.size = Pt(8)
                r3.font.color.rgb = COLOR_TEXT_MUTED

        self.add_bottom_bar(slide, "Relational Schema Integrity:", "Configured in 3NF with ON DELETE CASCADE constraints preventing orphaned milestone records.", "🗄️")

    def build_slide_14_data_persistence(self):
        """Slide 14 — Dual-Engine Data Persistence & Resilient Fallback."""
        slide = self.add_slide()
        self.draw_header(slide, "14", "Dual", "Persistence")

        engines = [
            ("Primary Relational Mode (MySQL 8.x)", [
                ("Auto-Migration", "Provisions academic_project_db, tables, primary keys, and cascade foreign constraints automatically."),
                ("In-App Config Dialog", "Allows runtime reconfiguration of host, port, db name, and credentials with instant ping verification."),
                ("ACID Transactions", "Guarantees atomicity and durability across student submissions and faculty grading updates.")
            ], COLOR_BLUE_BG, COLOR_BLUE_TEXT),
            ("Resilient Offline Fallback (Serialization)", [
                ("Seamless Failover", "If MySQL daemon is offline or network drops, system seamlessly switches to local object serialization (projects.dat)."),
                ("Zero Data Loss", "Students and faculty can continue logging progress and evaluating work offline without interruptions."),
                ("Rolling Snapshots", "Maintains up to 5 timestamped rolling disaster-recovery snapshots in Project/backups/ preventing corruption.")
            ], COLOR_GREEN_BG, COLOR_GREEN_TEXT)
        ]

        card_w = Inches(5.9)
        card_h = Inches(4.25)
        top_y = Inches(1.55)
        gap = Inches(0.33)

        for i, (title, points, chip_bg, chip_text) in enumerate(engines):
            x = Inches(0.6) + i * (card_w + gap)
            c = self.add_card(slide, x, top_y, card_w, card_h)
            self.add_chip(slide, x + Inches(0.25), top_y + Inches(0.2), f"ENGINE 0{i+1}", chip_bg, chip_text)

            tb = slide.shapes.add_textbox(x + Inches(0.25), top_y + Inches(0.6), card_w - Inches(0.5), Inches(0.6))
            p = tb.text_frame.paragraphs[0]
            r = p.add_run()
            r.text = title
            r.font.name = FONT_DISPLAY
            r.font.size = Pt(13)
            r.font.bold = True
            r.font.color.rgb = COLOR_TEXT_DARK

            y_item = top_y + Inches(1.3)
            for pname, pdesc in points:
                ic = self.add_card(slide, x + Inches(0.2), y_item, card_w - Inches(0.4), Inches(0.85), bg_rgb=COLOR_WHITE, border_rgb=COLOR_BORDER_SUBTLE)
                tb_i = slide.shapes.add_textbox(x + Inches(0.3), y_item + Inches(0.08), card_w - Inches(0.6), Inches(0.7))
                tf_i = tb_i.text_frame
                tf_i.margin_top = Inches(0)
                p_pn = tf_i.paragraphs[0]
                r = p_pn.add_run()
                r.text = pname + "\n"
                r.font.name = FONT_BODY
                r.font.size = Pt(10)
                r.font.bold = True
                r.font.color.rgb = COLOR_CRIMSON

                p_pd = tf_i.add_paragraph()
                r = p_pd.add_run()
                r.text = pdesc
                r.font.name = FONT_BODY
                r.font.size = Pt(8.5)
                r.font.color.rgb = COLOR_TEXT_MUTED
                y_item += Inches(0.92)

        self.add_bottom_bar(slide, "High-Availability Architecture:", "Dual persistence guarantees uninterrupted classroom and lab operation even during complete database downtime.", "🛡️")

    def build_slide_15_business_logic(self):
        """Slide 15 — Business Logic & Project Status Resolution."""
        slide = self.add_slide()
        self.draw_header(slide, "15", "Lifecycle", "Status")

        # Decision Table
        rules = [
            ("NOT_STARTED", "No progress updates recorded (|history| == 0)", "Default state for newly registered projects awaiting initial plan.", COLOR_BORDER_SUBTLE, COLOR_TEXT_MUTED),
            ("COMPLETED", "Latest self-reported progress reaches 100%", "All project deliverables submitted, verified, and finalized.", COLOR_GREEN_BG, COLOR_GREEN_TEXT),
            ("OVERDUE", "DaysRemaining < 0 and LatestProgress < 100%", "Project has exceeded its scheduled deadline without finishing.", COLOR_RED_BG, COLOR_RED_TEXT),
            ("AT_RISK", "0 ≤ DaysRemaining ≤ 7 and LatestProgress < 60%", "Urgent attention required: less than a week remaining with low progress.", COLOR_AMBER_BG, COLOR_AMBER_TEXT),
            ("IN_PROGRESS", "All other general development conditions", "Active ongoing project moving normally toward milestones.", COLOR_BLUE_BG, COLOR_BLUE_TEXT)
        ]

        card_w = Inches(12.13)
        card_h = Inches(0.78)
        top_y = Inches(1.55)
        gap = Inches(0.12)

        for i, (status, condition, meaning, chip_bg, chip_text) in enumerate(rules):
            y = top_y + i * (card_h + gap)
            c = self.add_card(slide, Inches(0.6), y, card_w, card_h)

            self.add_chip(slide, Inches(0.8), y + Inches(0.24), status, chip_bg, chip_text, width=Inches(1.6))

            tb = slide.shapes.add_textbox(Inches(2.6), y + Inches(0.12), card_w - Inches(2.8), card_h - Inches(0.24))
            tf = tb.text_frame
            tf.word_wrap = True
            p = tf.paragraphs[0]
            r = p.add_run()
            r.text = "Condition: "
            r.font.name = FONT_BODY
            r.font.size = Pt(10)
            r.font.bold = True
            r.font.color.rgb = COLOR_TEXT_DARK

            r2 = p.add_run()
            r2.text = condition + "\n"
            r2.font.name = FONT_MONO
            r2.font.size = Pt(9.5)
            r2.font.color.rgb = COLOR_CRIMSON

            p2 = tf.add_paragraph()
            r3 = p2.add_run()
            r3.text = "Impact: " + meaning
            r3.font.name = FONT_BODY
            r3.font.size = Pt(9)
            r3.font.color.rgb = COLOR_TEXT_MUTED

        self.add_bottom_bar(slide, "Deterministic Status Logic:", "Project status is derived algorithmically from real-time dates and milestone history, avoiding manual tagging errors.", "📐")

    def build_slide_16_anti_cramming(self):
        """Slide 16 — Anti-Cramming Detection & Milestone Integrity."""
        slide = self.add_slide()
        self.draw_header(slide, "16", "Integrity", "Heuristics")

        cards = [
            ("Temporal Clustering Heuristic", "To counter end-of-semester dump submissions where students upload all updates simultaneously:\n\npublic boolean isLastMinuteDump(int minDaysSpread) {\n    if (progressHistory.size() < 2) return false;\n    LocalDate first = progressHistory.get(0).getSubmittedOn().toLocalDate();\n    LocalDate last = progressHistory.get(size() - 1).getSubmittedOn().toLocalDate();\n    return ChronoUnit.DAYS.between(first, last) < minDaysSpread;\n}"),
            ("Advisory Alert, Not Misconduct Proof", "• Configurable Threshold: Flags 3 or more updates submitted across fewer than 5 calendar days.\n• Advisory Nature: Prompts faculty to scrutinize work authenticity during viva defenses.\n• Does Not Block Submissions: Ensures students are not penalized for rapid genuine breakthroughs.\n• Integrated with Audit Locking: Prevents post-hoc editing once teacher inspection begins.")
        ]

        card_w = Inches(5.9)
        card_h = Inches(4.25)
        top_y = Inches(1.55)
        gap = Inches(0.33)

        for i, (title, content) in enumerate(cards):
            x = Inches(0.6) + i * (card_w + gap)
            c = self.add_card(slide, x, top_y, card_w, card_h)
            self.add_chip(slide, x + Inches(0.25), top_y + Inches(0.2), f"HEURISTIC 0{i+1}", COLOR_PINK_TINT, COLOR_CRIMSON)

            tb = slide.shapes.add_textbox(x + Inches(0.25), top_y + Inches(0.6), card_w - Inches(0.5), card_h - Inches(0.8))
            tf = tb.text_frame
            tf.word_wrap = True
            p = tf.paragraphs[0]
            r = p.add_run()
            r.text = title + "\n\n"
            r.font.name = FONT_DISPLAY
            r.font.size = Pt(13)
            r.font.bold = True
            r.font.color.rgb = COLOR_TEXT_DARK

            p2 = tf.add_paragraph()
            r = p2.add_run()
            r.text = content
            r.font.name = FONT_MONO if i == 0 else FONT_BODY
            r.font.size = Pt(8.5) if i == 0 else Pt(10)
            r.font.color.rgb = COLOR_TEXT_MUTED

        self.add_bottom_bar(slide, "Academic Integrity Focus:", "Empowering educators with automated temporal heuristics that differentiate authentic continuous effort from rushed dumps.", "🔍")

    def build_slide_17_security_integrity(self):
        """Slide 17 — Security & Data Integrity Architecture."""
        slide = self.add_slide()
        self.draw_header(slide, "17", "Security", "Architecture")

        pillars = [
            ("Role-Based Access Control", "Strictly separated student and faculty session boundaries. Students can only edit their own projects, while faculty possess global review, grading, and locking privileges."),
            ("Cryptographic SHA-256 Hashing", "User passwords are never stored in plaintext. Passwords are converted to irreversible SHA-256 hex digests prior to database insertion or local serialization."),
            ("Immutable Audit Timestamps", "ProgressUpdate construction binds final LocalDateTime submittedOn timestamps, ensuring submission dates cannot be backdated or falsified."),
            ("Tamper-Proof Milestone Locking", "Once reviewed by a faculty mentor, updates are locked. Attempted edits by students trigger IllegalStateException and are blocked by the UI.")
        ]

        card_w = Inches(5.9)
        card_h = Inches(1.95)
        top_y = Inches(1.55)
        gap_x = Inches(0.33)
        gap_y = Inches(0.22)

        for i, (title, desc) in enumerate(pillars):
            row = i // 2
            col = i % 2
            x = Inches(0.6) + col * (card_w + gap_x)
            y = top_y + row * (card_h + gap_y)

            c = self.add_card(slide, x, y, card_w, card_h)
            tb = slide.shapes.add_textbox(x + Inches(0.25), y + Inches(0.2), card_w - Inches(0.5), card_h - Inches(0.4))
            tf = tb.text_frame
            tf.word_wrap = True
            p = tf.paragraphs[0]
            r = p.add_run()
            r.text = title + "\n"
            r.font.name = FONT_DISPLAY
            r.font.size = Pt(13)
            r.font.bold = True
            r.font.color.rgb = COLOR_TEXT_DARK

            p2 = tf.add_paragraph()
            p2.space_before = Pt(6)
            r = p2.add_run()
            r.text = desc
            r.font.name = FONT_BODY
            r.font.size = Pt(9.5)
            r.font.color.rgb = COLOR_TEXT_MUTED

        self.add_bottom_bar(slide, "Defensive Engineering:", "Layered security controls protect student privacy, prevent credential leakage, and maintain absolute institutional audit integrity.", "🔒")

    def build_slide_18_testing_validation(self):
        """Slide 18 — Verification, Testing & Test Cases Matrix."""
        slide = self.add_slide()
        self.draw_header(slide, "18", "Verification", "Results")

        tests = [
            ("TC-01", "Authentication", "Valid Student Login ('student1' / 'pass123')", "Authenticated; launches Student Dashboard", "PASS"),
            ("TC-02", "Authentication", "Password SHA-256 Hex Digest Hashing", "SHA-256 digest matched in database", "PASS"),
            ("TC-03", "Lifecycle State", "At-Risk Status Trigger (40% prog, 4d left)", "Status dynamically resolves to AT_RISK", "PASS"),
            ("TC-04", "Data Integrity", "Locked Milestone Edit Immutability Attempt", "Throws IllegalStateException; UI blocks edit", "PASS"),
            ("TC-05", "Faculty Grading", "Score Range Enforcement (Slider = 95)", "Saves 95/100, assigns letter grade 'A+'", "PASS"),
            ("TC-06", "Anti-Dump Check", "Clustered Submissions (3 updates in 1 day)", "isLastMinuteDump(5) flags DUMP=YES", "PASS"),
            ("TC-07", "Fault Tolerance", "MySQL Server Offline Failover Scenario", "Seamlessly loads projects.dat fallback", "PASS"),
            ("TC-08", "Reporting Engine", "Sanitized RFC-4180 CSV Cohort Export", "Generates complete cohort_report_<date>.csv", "PASS")
        ]

        card_w = Inches(12.13)
        card_h = Inches(0.48)
        top_y = Inches(1.55)
        gap = Inches(0.08)

        for i, (tcid, module, desc, expected, status) in enumerate(tests):
            y = top_y + i * (card_h + gap)
            c = self.add_card(slide, Inches(0.6), y, card_w, card_h)

            self.add_chip(slide, Inches(0.75), y + Inches(0.1), tcid, COLOR_PINK_TINT, COLOR_CRIMSON, width=Inches(0.8))
            self.add_chip(slide, Inches(1.65), y + Inches(0.1), module, COLOR_BORDER_SUBTLE, COLOR_TEXT_DARK, width=Inches(1.5))

            tb = slide.shapes.add_textbox(Inches(3.3), y + Inches(0.04), Inches(4.5), card_h - Inches(0.08))
            p = tb.text_frame.paragraphs[0]
            r = p.add_run()
            r.text = desc
            r.font.name = FONT_BODY
            r.font.size = Pt(8.5)
            r.font.color.rgb = COLOR_TEXT_DARK

            tb2 = slide.shapes.add_textbox(Inches(7.9), y + Inches(0.04), Inches(3.6), card_h - Inches(0.08))
            p2 = tb2.text_frame.paragraphs[0]
            r = p2.add_run()
            r.text = expected
            r.font.name = FONT_BODY
            r.font.size = Pt(8.5)
            r.font.color.rgb = COLOR_TEXT_MUTED

            self.add_chip(slide, Inches(11.75), y + Inches(0.1), status, COLOR_GREEN_BG, COLOR_GREEN_TEXT, width=Inches(0.8))

        self.add_bottom_bar(slide, "Reported Test Results:", "100% of reported core functional test scenarios validated across authentication, domain logic, and persistence.", "✅")

    def build_slide_19_evolution_results(self):
        """Slide 19 — Integrated Workflow & Evolutionary Comparison."""
        slide = self.add_slide()
        self.draw_header(slide, "19", "Evolutionary", "Progress")

        comparisons = [
            ("User Interface", "Basic unstyled Swing forms, native OS buttons", "FlatLaf Adaptive Dark/Light Mode, Inter typography"),
            ("Data Persistence", "Single local projects.dat file without fallback", "Dual-Engine Sync (MySQL 8.x + 5-Level Rolling Backups)"),
            ("Milestone Tracking", "Static plain text list without stage tags", "Interactive Timeline Feed, Stage Badges & Blockers"),
            ("Faculty Evaluation", "No feedback, score sliders, or reactions", "0–100 Continuous Slider, Letter Grades, Milestone Locks"),
            ("Security & RBAC", "Hardcoded mock passwords in plaintext", "SHA-256 Cryptographic Hashing + Role-Based Workspaces")
        ]

        card_w = Inches(12.13)
        card_h = Inches(0.78)
        top_y = Inches(1.55)
        gap = Inches(0.12)

        for i, (dim, m1, final) in enumerate(comparisons):
            y = top_y + i * (card_h + gap)
            c = self.add_card(slide, Inches(0.6), y, card_w, card_h)

            # Dimension tag
            self.add_chip(slide, Inches(0.8), y + Inches(0.24), dim, COLOR_PINK_TINT, COLOR_CRIMSON, width=Inches(2.2))

            # Month 1 column
            tb_m1 = slide.shapes.add_textbox(Inches(3.2), y + Inches(0.12), Inches(4.2), card_h - Inches(0.24))
            p1 = tb_m1.text_frame.paragraphs[0]
            r = p1.add_run()
            r.text = "Month 1 Review MVP:\n"
            r.font.name = FONT_BODY
            r.font.size = Pt(8.5)
            r.font.bold = True
            r.font.color.rgb = COLOR_TEXT_MUTED
            r2 = p1.add_run()
            r2.text = m1
            r2.font.name = FONT_BODY
            r2.font.size = Pt(9.5)
            r2.font.color.rgb = COLOR_TEXT_DARK

            # Final column
            tb_f = slide.shapes.add_textbox(Inches(7.6), y + Inches(0.12), Inches(4.9), card_h - Inches(0.24))
            p2 = tb_f.text_frame.paragraphs[0]
            r = p2.add_run()
            r.text = "Final Enterprise Delivery:\n"
            r.font.name = FONT_BODY
            r.font.size = Pt(8.5)
            r.font.bold = True
            r.font.color.rgb = COLOR_GREEN_TEXT
            r2 = p2.add_run()
            r2.text = final
            r2.font.name = FONT_BODY
            r2.font.size = Pt(9.5)
            r2.font.bold = True
            r2.font.color.rgb = COLOR_TEXT_DARK

        self.add_bottom_bar(slide, "Iterative Evolution:", "ProjectPulse evolved from an initial desktop prototype into a resilient, production-ready continuous evaluation ecosystem.", "📈")

    def build_slide_20_challenges_solutions(self):
        """Slide 20 — Challenges Encountered & Technical Solutions."""
        slide = self.add_slide()
        self.draw_header(slide, "20", "Challenges", "Overcome")

        challenges = [
            ("Tight UI-Business Coupling", "Direct database and logic calls inside Swing ActionListeners made testing difficult.", "Refactored into strict MVC & DAO layers: domain models handle validation, DatabaseManager handles SQL, and UITheme handles styling."),
            ("MySQL Availability & Crashes", "Application crashed on startup when local MySQL daemon was not running or misconfigured.", "Engineered seamless fallback to local object serialization (projects.dat) with 5 rolling backups and interactive in-app credential config."),
            ("Retrospective Tampering", "Risk of students modifying submitted milestones after teacher feedback or grading.", "Enforced final LocalDateTime timestamps at construction and introduced teacher-controlled milestone locking."),
            ("Cross-Platform Display Scaling", "Standard Swing fonts rendered blurry or clipped on high-DPI Windows laptops.", "Integrated FlatLaf modern Look & Feel with automatic font fallback hierarchy (Inter -> Segoe UI -> SF Pro Text).")
        ]

        card_w = Inches(5.9)
        card_h = Inches(1.95)
        top_y = Inches(1.55)
        gap_x = Inches(0.33)
        gap_y = Inches(0.22)

        for i, (title, problem, solution) in enumerate(challenges):
            row = i // 2
            col = i % 2
            x = Inches(0.6) + col * (card_w + gap_x)
            y = top_y + row * (card_h + gap_y)

            c = self.add_card(slide, x, y, card_w, card_h)
            tb = slide.shapes.add_textbox(x + Inches(0.25), y + Inches(0.15), card_w - Inches(0.5), card_h - Inches(0.3))
            tf = tb.text_frame
            tf.word_wrap = True
            p = tf.paragraphs[0]
            r = p.add_run()
            r.text = title + "\n"
            r.font.name = FONT_DISPLAY
            r.font.size = Pt(12)
            r.font.bold = True
            r.font.color.rgb = COLOR_TEXT_DARK

            p2 = tf.add_paragraph()
            r = p2.add_run()
            r.text = "Challenge: "
            r.font.name = FONT_BODY
            r.font.size = Pt(8.5)
            r.font.bold = True
            r.font.color.rgb = COLOR_RED_TEXT
            r2 = p2.add_run()
            r2.text = problem + "\n"
            r2.font.name = FONT_BODY
            r2.font.size = Pt(8.5)
            r2.font.color.rgb = COLOR_TEXT_MUTED

            p3 = tf.add_paragraph()
            r = p3.add_run()
            r.text = "Solution: "
            r.font.name = FONT_BODY
            r.font.size = Pt(8.5)
            r.font.bold = True
            r.font.color.rgb = COLOR_GREEN_TEXT
            r2 = p3.add_run()
            r2.text = solution
            r2.font.name = FONT_BODY
            r2.font.size = Pt(8.5)
            r2.font.color.rgb = COLOR_TEXT_DARK

        self.add_bottom_bar(slide, "Engineering Rigor:", "Overcoming desktop Java constraints through resilient design patterns, automated failover, and defensive data modeling.", "🛠️")

    def build_slide_21_future_scope(self):
        """Slide 21 — Future Scope & Proposed Enhancements."""
        slide = self.add_slide()
        self.draw_header(slide, "21", "Future", "Roadmap")

        enhancements = [
            ("Cloud-Native Web Transition", "Migrating business and domain logic to a Spring Boot 3 REST API backend paired with a modern React or Angular single-page frontend for cross-device mobile access."),
            ("Automated Git Commit Correlation", "Integrating GitHub and GitLab webhooks to correlate student milestone update timestamps with actual git commit frequency and codebase diffs."),
            ("Institutional Single Sign-On (SSO)", "Integrating with university LDAP, Active Directory, and Google Workspace for seamless student roll-number authentication and role mapping."),
            ("AI-Assisted Milestone Summaries", "Incorporating Large Language Models (LLMs) to automatically detect project divergence, summarize weekly deliverables, and alert department coordinators.")
        ]

        card_w = Inches(2.8)
        card_h = Inches(4.25)
        top_y = Inches(1.55)
        gap = Inches(0.31)

        for i, (title, desc) in enumerate(enhancements):
            x = Inches(0.6) + i * (card_w + gap)
            c = self.add_card(slide, x, top_y, card_w, card_h)
            self.add_chip(slide, x + Inches(0.2), top_y + Inches(0.2), f"PHASE {i+1}", COLOR_PINK_TINT, COLOR_CRIMSON)

            tb = slide.shapes.add_textbox(x + Inches(0.2), top_y + Inches(0.65), card_w - Inches(0.4), card_h - Inches(0.8))
            tf = tb.text_frame
            tf.word_wrap = True
            p = tf.paragraphs[0]
            r = p.add_run()
            r.text = title + "\n\n"
            r.font.name = FONT_DISPLAY
            r.font.size = Pt(13)
            r.font.bold = True
            r.font.color.rgb = COLOR_TEXT_DARK

            p2 = tf.add_paragraph()
            r = p2.add_run()
            r.text = desc
            r.font.name = FONT_BODY
            r.font.size = Pt(9.5)
            r.font.color.rgb = COLOR_TEXT_MUTED

        self.add_bottom_bar(slide, "Strategic Vision:", "Evolution pathway toward a campus-wide, cloud-hosted continuous assessment and research governance ecosystem.", "🔮")

    def build_slide_22_conclusion_refs(self):
        """Slide 22 — Conclusion, References & Acknowledgments."""
        slide = self.add_slide()
        self.draw_header(slide, "22", "Conclusion &", "References")

        # Left Card: Pedagogical Summary
        c1 = self.add_card(slide, Inches(0.6), Inches(1.55), Inches(5.9), Inches(4.25))
        self.add_chip(slide, Inches(0.85), Inches(1.75), "SUMMARY", COLOR_PINK_TINT, COLOR_CRIMSON)

        tb1 = slide.shapes.add_textbox(Inches(0.85), Inches(2.15), Inches(5.4), Inches(3.4))
        tf1 = tb1.text_frame
        tf1.word_wrap = True
        p1 = tf1.paragraphs[0]
        r = p1.add_run()
        r.text = "Pedagogical Impact & Conclusion\n\n"
        r.font.name = FONT_DISPLAY
        r.font.size = Pt(15)
        r.font.bold = True
        r.font.color.rgb = COLOR_TEXT_DARK

        p_desc = tf1.add_paragraph()
        r = p_desc.add_run()
        r.text = "ProjectPulse Enterprise successfully demonstrates how core Object-Oriented Techniques in Java can be harnessed to solve critical academic governance challenges in higher engineering education.\n\nBy replacing unstructured last-minute submissions with an immutable, milestone-driven model, the platform enforces student accountability, equips faculty with continuous evaluation tools, and guarantees high availability through resilient dual persistence.\n\nAligned with SDG 4 (Quality Education), the project establishes a scalable foundation for modern, transparent capstone evaluation."
        r.font.name = FONT_BODY
        r.font.size = Pt(10)
        r.font.color.rgb = COLOR_TEXT_DARK

        # Right Card: References & Acknowledgments
        c2 = self.add_card(slide, Inches(6.83), Inches(1.55), Inches(5.9), Inches(4.25))
        self.add_chip(slide, Inches(7.08), Inches(1.75), "CITATIONS", COLOR_BLUE_BG, COLOR_BLUE_TEXT)

        tb2 = slide.shapes.add_textbox(Inches(7.08), Inches(2.15), Inches(5.4), Inches(3.4))
        tf2 = tb2.text_frame
        tf2.word_wrap = True
        p2 = tf2.paragraphs[0]
        r = p2.add_run()
        r.text = "Academic References & Acknowledgments\n\n"
        r.font.name = FONT_DISPLAY
        r.font.size = Pt(15)
        r.font.bold = True
        r.font.color.rgb = COLOR_TEXT_DARK

        refs = [
            "1. Oracle Corporation, Java SE 17 Platform Specifications, 2024.",
            "2. FormDev Software GmbH, FlatLaf Modern Look & Feel for Java, 2024.",
            "3. MySQL AB & Oracle, MySQL Connector/J 8.3 Developer Reference, 2024.",
            "4. Pressman, R. S., Software Engineering: A Practitioner's Approach, 8th Ed.",
            "5. Gamma, E. et al., Design Patterns: Elements of Reusable OO Software."
        ]
        for ref in refs:
            p_r = tf2.add_paragraph()
            r = p_r.add_run()
            r.text = ref
            r.font.name = FONT_BODY
            r.font.size = Pt(8.5)
            r.font.color.rgb = COLOR_TEXT_MUTED

        p_ack = tf2.add_paragraph()
        p_ack.space_before = Pt(12)
        r = p_ack.add_run()
        r.text = "Special Acknowledgments: Sincere gratitude to Mentor Ms. Aparna Pandey and the Department of CSE (AI), NIET Greater Noida for continuous mentorship."
        r.font.name = FONT_BODY
        r.font.size = Pt(9.5)
        r.font.italic = True
        r.font.bold = True
        r.font.color.rgb = COLOR_CRIMSON

        self.add_bottom_bar(slide, "Thank You!", "Questions, feedback, and discussion are warmly welcomed by Group 3.", "🙏")

    def build_all(self, output_path):
        print("[*] Generating Slide 01: Cover Page...")
        self.build_slide_01_cover()
        print("[*] Generating Slide 02: Table of Contents...")
        self.build_slide_02_agenda()
        print("[*] Generating Slide 03: Project Introduction...")
        self.build_slide_03_intro()
        print("[*] Generating Slide 04: Problem Statement...")
        self.build_slide_04_problem_statement()
        print("[*] Generating Slide 05: Project Objectives...")
        self.build_slide_05_objectives()
        print("[*] Generating Slide 06: Proposed System & Workflow...")
        self.build_slide_06_proposed_system()
        print("[*] Generating Slide 07: System Architecture (3-Tier)...")
        self.build_slide_07_system_architecture()
        print("[*] Generating Slide 08: Technology Stack...")
        self.build_slide_08_tech_stack()
        print("[*] Generating Slide 09: OOP Concepts Applied...")
        self.build_slide_09_oops_concepts()
        print("[*] Generating Slide 10: Domain Models & UML...")
        self.build_slide_10_class_diagram()
        print("[*] Generating Slide 11: Student Workspace...")
        self.build_slide_11_student_dashboard()
        print("[*] Generating Slide 12: Faculty Assessment Console...")
        self.build_slide_12_faculty_console()
        print("[*] Generating Slide 13: Database Design & ERD...")
        self.build_slide_13_database_design()
        print("[*] Generating Slide 14: Dual-Engine Data Persistence...")
        self.build_slide_14_data_persistence()
        print("[*] Generating Slide 15: Lifecycle Status Resolution...")
        self.build_slide_15_business_logic()
        print("[*] Generating Slide 16: Anti-Cramming Heuristics...")
        self.build_slide_16_anti_cramming()
        print("[*] Generating Slide 17: Security Architecture...")
        self.build_slide_17_security_integrity()
        print("[*] Generating Slide 18: Verification & Test Matrix...")
        self.build_slide_18_testing_validation()
        print("[*] Generating Slide 19: Evolutionary Comparison...")
        self.build_slide_19_evolution_results()
        print("[*] Generating Slide 20: Challenges & Solutions...")
        self.build_slide_20_challenges_solutions()
        print("[*] Generating Slide 21: Future Scope & Roadmap...")
        self.build_slide_21_future_scope()
        print("[*] Generating Slide 22: Conclusion & References...")
        self.build_slide_22_conclusion_refs()

        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        self.prs.save(output_path)
        print(f"[SUCCESS] Complete 22-slide presentation generated at: {output_path}")

if __name__ == '__main__':
    target_path = r'C:\Users\darkp\Desktop\pbl 2ndyear\Java\ProjectPulse_Enterprise_Java_PBL.pptx'
    builder = PresentationBuilder()
    builder.build_all(target_path)
