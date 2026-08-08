#!/usr/bin/env python3
"""
Certificate generator for SRESTHA Contest 2026.

Usage:
  Single:  python generate_cert.py "Student Name"
  Bulk:    python generate_cert.py --csv students.csv
           python generate_cert.py --csv students.csv --name-col "Full Name"
"""
import sys, os, csv, urllib.request
from PIL import Image, ImageDraw, ImageFont

# ── Paths ───────────────────────────────────────────────────────────────────
BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
TEMPLATE   = os.path.join(BASE_DIR, 'images', 'Srestha_Cert.png')
OUTPUT_DIR = os.path.join(BASE_DIR, 'certificates')
FONT_PATH  = os.path.join(BASE_DIR, 'AlexBrush-Regular.ttf')
FONT_URL   = 'https://github.com/google/fonts/raw/main/ofl/alexbrush/AlexBrush-Regular.ttf'
BODY_FONT  = r'C:\Windows\Fonts\segoeui.ttf'

# ── Layout (template is 2000 × 1414) ────────────────────────────────────────
CREAM_CX      = 1155   # horizontal centre of the cream area
NAME_CY       = 635    # vertical centre for the name (between header and divider)
MAX_NAME_W    = 1500   # maximum pixel width before font shrinks
NAME_FONT_SZ  = 160
BODY_START_Y  = 862    # first description line (below template divider at ~790)
LINE_GAP      = 72

# ── Colours ──────────────────────────────────────────────────────────────────
MAROON     = (116, 19, 31)
BODY_COLOR = (50, 30, 20)

DESCRIPTION = [
    "has successfully participated in the \u015are\u1e63\u1e6dha Contest 2026",
    "a reading and knowledge initiative by ISKCON Abids, Hyderabad,",
    "and has demonstrated commendable understanding and dedication.",
]

# ── Helpers ──────────────────────────────────────────────────────────────────
def ensure_font():
    if not os.path.exists(FONT_PATH):
        print("Downloading Alex Brush font…")
        urllib.request.urlretrieve(FONT_URL, FONT_PATH)
        print("Font ready.")

def draw_centered(draw, text, cx, y, font, fill):
    bbox = draw.textbbox((0, 0), text, font=font)
    x = cx - (bbox[2] - bbox[0]) // 2
    draw.text((x, y), text, font=font, fill=fill)

def generate_certificate(name: str, output_path: str):
    ensure_font()
    img  = Image.open(TEMPLATE).copy()
    draw = ImageDraw.Draw(img)

    # Name — Alex Brush, auto-scale down if too long
    size = NAME_FONT_SZ
    while size > 60:
        name_font = ImageFont.truetype(FONT_PATH, size)
        bbox = draw.textbbox((0, 0), name, font=name_font)
        if (bbox[2] - bbox[0]) <= MAX_NAME_W:
            break
        size -= 5

    bbox   = draw.textbbox((0, 0), name, font=name_font)
    name_y = NAME_CY - (bbox[3] - bbox[1]) // 2
    draw_centered(draw, name, CREAM_CX, name_y, name_font, MAROON)

    # Description — Georgia
    body_font = ImageFont.truetype(BODY_FONT, 46)
    y = BODY_START_Y
    for line in DESCRIPTION:
        draw_centered(draw, line, CREAM_CX, y, body_font, BODY_COLOR)
        y += LINE_GAP

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    img.save(output_path, 'PNG')
    print(f"Saved: {output_path}")

def safe_filename(name):
    return "".join(c if c.isalnum() or c in " -_" else "_" for c in name).strip()

# ── Entry point ──────────────────────────────────────────────────────────────
def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    if sys.argv[1] == '--csv':
        if len(sys.argv) < 3:
            print("Error: provide a CSV path after --csv")
            sys.exit(1)
        csv_path = sys.argv[2]
        name_col = None
        if '--name-col' in sys.argv:
            name_col = sys.argv[sys.argv.index('--name-col') + 1]

        with open(csv_path, newline='', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            if not name_col:
                for h in (reader.fieldnames or []):
                    if any(k in h.lower() for k in ('name', 'student', 'participant')):
                        name_col = h
                        break
                name_col = name_col or (reader.fieldnames or ['name'])[0]
                print(f"Using column: '{name_col}'")
            for row in reader:
                name = (row.get(name_col) or '').strip()
                if name:
                    out = os.path.join(OUTPUT_DIR, f"{safe_filename(name)}.png")
                    generate_certificate(name, out)
    else:
        name = sys.argv[1]
        out  = os.path.join(OUTPUT_DIR, f"{safe_filename(name)}.png")
        generate_certificate(name, out)

if __name__ == '__main__':
    main()
