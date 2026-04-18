#!/usr/bin/env python3
"""
Recreates the Beitrittserklärung (membership declaration) for
FFW – Förderverein Freibad Wacken e.V. as a clean, fillable PDF
with proper AcroForm input fields.

Source: static/files/beitrittserklaerung-foerderverein-2026-03-30.pdf (scanned)
Output: static/files/beitrittserklaerung-foerderverein-fillable.pdf

Layout is matched to the scanned original:
- Left margin ~30 mm, matching scan measurements
- Title left-aligned (not centred) to match original
- Personal fields use underline-only style (no filled box)
- Geb.-Datum on left, Telefon on right (matching original row order)
- SEPA bank fields in a bordered box with internal dividers and
  small annotation labels at the bottom of each cell
"""

import os
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle

OUTPUT_PATH = os.path.join(
    os.path.dirname(__file__),
    "..",
    "static",
    "files",
    "beitrittserklaerung-foerderverein-fillable.pdf",
)

PAGE_W, PAGE_H = A4          # 595.28 x 841.89 pts
MARGIN_L = 30 * mm           # ~85 pts – matches scan left margin
MARGIN_R = PAGE_W - 30 * mm  # ~510 pts
TEXT_W = MARGIN_R - MARGIN_L  # ~425 pts


# ── helpers ─────────────────────────────────────────────────────────────────

def underline_field(c, name, x, y, width, height=14, font_size=10, tooltip=""):
    """AcroForm text field rendered with an underline border only (no fill)."""
    c.acroForm.textfield(
        name=name,
        tooltip=tooltip,
        x=x,
        y=y,
        width=width,
        height=height,
        fontSize=font_size,
        borderWidth=0.5,
        borderStyle="underlined",
        borderColor=colors.black,
        fillColor=colors.white,
        textColor=colors.black,
        forceBorder=True,
    )


def box_field(c, name, x, y, width, height, font_size=9, tooltip=""):
    """AcroForm text field with transparent background for use inside a drawn box."""
    c.acroForm.textfield(
        name=name,
        tooltip=tooltip,
        x=x,
        y=y,
        width=width,
        height=height,
        fontSize=font_size,
        borderWidth=0,
        borderColor=colors.white,
        fillColor=colors.white,
        textColor=colors.black,
        forceBorder=False,
    )


def line(c, x1, y1, x2, y2, width=0.5, dash=None):
    c.setLineWidth(width)
    if dash:
        c.setDash(dash, 2)
    else:
        c.setDash([], 0)
    c.line(x1, y1, x2, y2)
    c.setDash([], 0)


def para(c, text, x, y, width, font="Helvetica", size=9, leading=12):
    """Draw a paragraph starting at (x, y-top); returns y below the last line."""
    style = ParagraphStyle("p", fontName=font, fontSize=size, leading=leading, spaceAfter=0)
    p = Paragraph(text, style)
    _, h = p.wrap(width, 9999)
    p.drawOn(c, x, y - h)
    return y - h


# ── main ────────────────────────────────────────────────────────────────────

def create_pdf(output_path):
    c = canvas.Canvas(output_path, pagesize=A4)
    c.setTitle("Beitrittserklärung – Förderverein Freibad Wacken e.V.")
    c.setAuthor("FFW – Förderverein Freibad Wacken e.V.")
    c.setSubject("Mitgliedschaft Förderverein Freibad Wacken")

    # ── HEADER ──────────────────────────────────────────────────────────────
    hx = MARGIN_L
    hy = PAGE_H - 15 * mm  # top of header block

    c.setFont("Helvetica-Bold", 10)
    c.drawString(hx, hy, "FFW – Förderverein Freibad Wacken e.V.")

    contact = [
        (9,  "Stefan Timm"),
        (9,  "Schulkamp 8"),
        (9,  "25594 Vaale"),
        (9,  "0172 / 4003312"),
        (9,  "Tel. 04827 – 626 (Freibad)"),
        (9,  "Kontakt: freibad@wacken.de"),
    ]
    lh = 5 * mm
    for i, (size, text) in enumerate(contact):
        c.setFont("Helvetica", size)
        c.drawString(hx, hy - (i + 1) * lh, text)

    # ── SEPARATOR ───────────────────────────────────────────────────────────
    sep_y = hy - len(contact) * lh - 4 * mm
    line(c, MARGIN_L, sep_y, MARGIN_R, sep_y, width=0.3)

    # ── TITLE ───────────────────────────────────────────────────────────────
    # Left-aligned, matching the original scan (title at same x as body text)
    title_y = sep_y - 9 * mm
    c.setFont("Helvetica-Bold", 16)
    c.drawString(MARGIN_L, title_y, "Beitrittserklärung")

    # ── APPLICATION TEXT ────────────────────────────────────────────────────
    app_y = title_y - 9 * mm
    c.setFont("Helvetica", 10)
    c.drawString(MARGIN_L, app_y, "Ich beantrage die Mitgliedschaft im Förderverein Freibad Wacken e. V.")

    # ── PERSONAL DATA FIELDS ────────────────────────────────────────────────
    # Style: label on the left, field fills remaining width with underline border.
    # Field height chosen to give a comfortable writing baseline.
    label_col = 23 * mm   # fixed label column width
    fh = 14               # field height in pts
    gap = 13 * mm         # vertical distance between field baselines

    fy = app_y - 14 * mm

    # Name
    c.setFont("Helvetica", 9)
    c.drawString(MARGIN_L, fy + 3, "Name")
    underline_field(c, "name", MARGIN_L + label_col, fy, TEXT_W - label_col, fh, tooltip="Name")

    # Anschrift
    fy -= gap
    c.setFont("Helvetica", 9)
    c.drawString(MARGIN_L, fy + 3, "Anschrift")
    underline_field(c, "anschrift", MARGIN_L + label_col, fy, TEXT_W - label_col, fh, tooltip="Anschrift")

    # Geb.-Datum (left) | Telefon (right)  – order matches the scan
    fy -= gap
    half = (TEXT_W - label_col) / 2 - 3 * mm

    c.setFont("Helvetica", 9)
    c.drawString(MARGIN_L, fy + 3, "Geb.-Datum")
    underline_field(c, "geb_datum", MARGIN_L + label_col, fy, half, fh, tooltip="Geburtsdatum")

    tel_lx = MARGIN_L + label_col + half + 6 * mm
    c.setFont("Helvetica", 9)
    c.drawString(tel_lx, fy + 3, "Telefon")
    tel_fx = tel_lx + 18 * mm
    underline_field(c, "telefon", tel_fx, fy, MARGIN_R - tel_fx, fh, tooltip="Telefon")

    # E-Mail-Anschrift
    fy -= gap
    c.setFont("Helvetica", 9)
    c.drawString(MARGIN_L, fy + 3, "E-Mail-Anschrift")
    underline_field(c, "email", MARGIN_L + label_col, fy, TEXT_W - label_col, fh, tooltip="E-Mail-Anschrift")

    # Hint
    fy -= 8 * mm
    c.setFont("Helvetica-Oblique", 7.5)
    c.drawString(MARGIN_L + label_col, fy, "(bitte leserlich in Druckbuchstaben)")

    # ── SEPA INTRO ──────────────────────────────────────────────────────────
    sepa_y = fy - 8 * mm
    sepa_intro = (
        "Der Mitgliedsbeitrag beträgt derzeit jährlich <b>15 €</b> (Mindestbeitrag), "
        "für Mitglieder unter 16 Jahren <b>5 €</b>. Die Zahlung soll erfolgen per "
        "SEPA-Lastschrift. Ich ermächtige widerruflich, die zu entrichtenden Zahlungen "
        "bei Fälligkeit durch Lastschrift von meinem/unserem Konto einzuziehen:"
    )
    sepa_y = para(c, sepa_intro, MARGIN_L, sepa_y, TEXT_W, size=9, leading=12)

    # ── SEPA BANK BOX ───────────────────────────────────────────────────────
    # A bordered rectangle with two rows and an internal vertical + horizontal divider.
    # Row 1: Kontoinhaber (left ~63 %) | BIC (right ~37 %)
    # Row 2: IBAN (left ~63 %) | Kreditinstitut / Bank (right ~37 %)
    # Small annotation labels sit at the bottom of each cell; the AcroForm field
    # fills the upper portion of the cell so there is space for the label below it.

    box_top = sepa_y - 3 * mm
    row1_h = 18 * mm   # height of row 1
    row2_h = 14 * mm   # height of row 2
    box_h = row1_h + row2_h
    box_bot = box_top - box_h

    col_split = TEXT_W * 0.63  # vertical divider x-offset from MARGIN_L
    bx = MARGIN_L              # box left x
    bw = TEXT_W                # box width
    div_x = bx + col_split     # x of vertical divider

    # Outer rectangle
    c.setLineWidth(0.5)
    c.rect(bx, box_bot, bw, box_h)

    # Horizontal divider (between rows)
    row_div_y = box_bot + row2_h
    line(c, bx, row_div_y, bx + bw, row_div_y)

    # Vertical divider (both rows)
    line(c, div_x, box_bot, div_x, box_top)

    # ── Row 1: Kontoinhaber | BIC ──────────────────────────────────────────
    ann_h = 9   # height reserved at bottom of each cell for annotation label (pts)
    pad = 2     # small padding from cell walls

    # Kontoinhaber field (left cell of row 1)
    kh_field_h = row1_h - ann_h - 2 * pad  # field height within the cell
    kh_field_y = row_div_y + ann_h + pad
    kh_field_w = col_split - 2 * pad
    box_field(c, "kontoinhaber", bx + pad, kh_field_y, kh_field_w, kh_field_h, tooltip="Kontoinhaber")
    # Annotation label at bottom of Kontoinhaber cell
    c.setFont("Helvetica", 6)
    c.drawString(bx + pad, row_div_y + 2, "(Kontoinhaber, wenn nicht identisch mit Antragsteller)")

    # BIC field (right cell of row 1)
    bic_cell_w = bw - col_split
    bic_field_w = bic_cell_w - 2 * pad
    bic_field_y = row_div_y + ann_h + pad
    box_field(c, "bic", div_x + pad, bic_field_y, bic_field_w, kh_field_h, tooltip="BIC")
    # Annotation label at bottom of BIC cell
    c.setFont("Helvetica", 6)
    c.drawString(div_x + pad, row_div_y + 2, "(BIC, nicht erforderlich wenn IBAN mit DE beginnt)")

    # ── Row 2: IBAN | Kreditinstitut / Bank ───────────────────────────────
    iban_field_h = row2_h - ann_h - 2 * pad
    iban_field_y = box_bot + ann_h + pad
    iban_field_w = col_split - 2 * pad
    box_field(c, "iban", bx + pad, iban_field_y, iban_field_w, iban_field_h, tooltip="IBAN")
    c.setFont("Helvetica", 6)
    c.drawString(bx + pad, box_bot + 2, "(IBAN)")

    bank_field_w = bic_cell_w - 2 * pad
    box_field(c, "kreditinstitut", div_x + pad, iban_field_y, bank_field_w, iban_field_h,
              tooltip="Kreditinstitut / Bank")
    c.setFont("Helvetica", 6)
    c.drawString(div_x + pad, box_bot + 2, "(Kreditinstitut / Bank)")

    # ── SEPA MANDATE TEXT ───────────────────────────────────────────────────
    mandate_y = box_bot - 4 * mm
    mandate = (
        "Ich weise mein Kreditinstitut an, die vom Förderverein Freibad Wacken e.V. auf mein Konto "
        "gezogenen Lastschriften (Gläubiger-ID: DE3300000000069312, Mandatsreferenz: "
        "7952-0007109121-000-0) einzulösen. Ich kann innerhalb von acht Wochen, beginnend mit dem "
        "Belastungsdatum, die Erstattung des belasteten Betrags verlangen. Es gelten dabei die mit "
        "meinem Kreditinstitut vereinbarten Bedingungen. Vor dem erstmaligen Einzug der "
        "SEPA-Lastschrift werde ich über den Einzug in dieser Verfahrensart unterrichtet."
    )
    mandate_y = para(c, mandate, MARGIN_L, mandate_y, TEXT_W, size=9, leading=12)

    # ── SIGNATURE LINE ──────────────────────────────────────────────────────
    sig_y = mandate_y - 12 * mm
    sig_label_y = sig_y - 4 * mm   # label sits below the underline

    sig_sections = [
        ("Ort",          MARGIN_L,              47 * mm),
        ("Datum",        MARGIN_L + 52 * mm,    42 * mm),
        ("Unterschrift", MARGIN_L + 99 * mm,    TEXT_W - 99 * mm),
    ]
    for label, x, width in sig_sections:
        line(c, x, sig_y, x + width - 4 * mm, sig_y, width=0.5)
        c.setFont("Helvetica", 8)
        c.drawString(x, sig_label_y, label)

    # ── FOOTER ──────────────────────────────────────────────────────────────
    footer_y = 17 * mm
    line(c, MARGIN_L, footer_y + 3.5 * mm, MARGIN_R, footer_y + 3.5 * mm, width=0.3)

    c.setFont("Helvetica-Bold", 8)
    c.drawString(MARGIN_L, footer_y, "FFW – Förderverein Freibad Wacken e.V.")

    fl = [
        (7.5, "1. Vorsitzender: Stefan Timm"),
        (7.5, "Schulkamp 8  ·  25594 Vaale"),
        (7.5, "freibad@wacken.de  ·  www.freibad-wacken.de"),
    ]
    for i, (size, text) in enumerate(fl):
        c.setFont("Helvetica", size)
        c.drawString(MARGIN_L, footer_y - (i + 1) * 3.8 * mm, text)

    bank_x = PAGE_W / 2 + 5 * mm
    c.setFont("Helvetica-Bold", 8)
    c.drawString(bank_x, footer_y, "Bankverbindung:")
    for i, text in enumerate(["VReG Itzehoe", "IBAN  DE29 2019 0109 0071 0912 10"]):
        c.setFont("Helvetica", 7.5)
        c.drawString(bank_x, footer_y - (i + 1) * 3.8 * mm, text)

    c.save()
    print(f"✓ PDF created: {os.path.abspath(output_path)}")


if __name__ == "__main__":
    out = os.path.normpath(OUTPUT_PATH)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    create_pdf(out)
