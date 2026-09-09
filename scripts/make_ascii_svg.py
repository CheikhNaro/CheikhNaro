#!/usr/bin/env python3

from pathlib import Path
from PIL import Image, ImageEnhance
import html


# ------------------------------------------------------------
# Configuration
# ------------------------------------------------------------

SRC = Path("source-prepped.png")
OUTPUT = Path("assets/ascii.svg")

COLS = 100
ROWS = 53

CELL_W = 8
CELL_H = 15

RAMP = " .`:-=+*cs#%@"

CONTRAST = 1.05
BRIGHTNESS = 1.0
GAMMA = 1.18

WHITE_FLOOR = 0.80

PAD = 20
TITLEBAR_H = 30
STATUS_H = 30

ART_W = COLS * CELL_W
ART_H = ROWS * CELL_H

CANVAS_W = ART_W + PAD * 2
CANVAS_H = TITLEBAR_H + ART_H + STATUS_H + PAD


# ------------------------------------------------------------
# Palette du post original
# ------------------------------------------------------------

BACKGROUND = "#0d1117"
BACKGROUND_TOP = "#111722"
FRAME = "#30363d"

TITLE_TEXT = "#7d8590"

# Gris clair utilisé pour l'ASCII dans le post
ASCII_COLOR = "#39d353"

CURSOR = "#c9d1d9"


# ------------------------------------------------------------
# Animation
# ------------------------------------------------------------

ROW_DURATION = 0.11
STAGGER = 0.11


# ------------------------------------------------------------
# Conversion image → ASCII
# ------------------------------------------------------------

def generate_ascii_rows():

    image = Image.open(SRC).convert("L")

    image = ImageEnhance.Brightness(image).enhance(
        BRIGHTNESS
    )

    image = ImageEnhance.Contrast(image).enhance(
        CONTRAST
    )

    image = image.resize(
        (COLS, ROWS),
        Image.LANCZOS,
    )

    pixels = image.load()

    rows = []

    for y in range(ROWS):

        chars = []

        for x in range(COLS):

            luminance = pixels[x, y] / 255.0

            # Gamma
            luminance = pow(
                luminance,
                GAMMA,
            )

            # Zones très claires = espace
            if luminance >= WHITE_FLOOR:
                chars.append(" ")
                continue

            index = int(
                (1.0 - luminance)
                * (len(RAMP) - 1)
                + 0.5
            )

            index = max(
                0,
                min(
                    len(RAMP) - 1,
                    index,
                ),
            )

            chars.append(
                RAMP[index]
            )

        rows.append(
            "".join(chars)
        )

    return rows


# ------------------------------------------------------------
# Création du SVG
# ------------------------------------------------------------

def create_svg(rows):

    parts = []

    parts.append(
        '<?xml version="1.0" encoding="UTF-8"?>'
    )

    parts.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'width="{CANVAS_W}" '
        f'height="{CANVAS_H}" '
        f'viewBox="0 0 {CANVAS_W} {CANVAS_H}" '
        f'font-family="ui-monospace, SFMono-Regular, '
        f'Menlo, Consolas, monospace">'
    )

    # --------------------------------------------------------
    # Gradient background
    # --------------------------------------------------------

    parts.append(
        '<defs>'
        f'<linearGradient id="bg" '
        f'x1="0" y1="0" x2="0" y2="1">'
        f'<stop offset="0" '
        f'stop-color="{BACKGROUND_TOP}"/>'
        f'<stop offset="1" '
        f'stop-color="{BACKGROUND}"/>'
        f'</linearGradient>'
        '</defs>'
    )

    parts.append(
        f'<rect '
        f'width="{CANVAS_W}" '
        f'height="{CANVAS_H}" '
        f'rx="12" '
        f'fill="url(#bg)"/>'
    )

    # --------------------------------------------------------
    # Border
    # --------------------------------------------------------

    parts.append(
        f'<rect '
        f'x="0.5" '
        f'y="0.5" '
        f'width="{CANVAS_W - 1}" '
        f'height="{CANVAS_H - 1}" '
        f'rx="12" '
        f'fill="none" '
        f'stroke="{FRAME}" '
        f'stroke-width="1"/>'
    )

    # --------------------------------------------------------
    # Title bar
    # --------------------------------------------------------

    parts.append(
        f'<line '
        f'x1="0" '
        f'y1="{TITLEBAR_H}" '
        f'x2="{CANVAS_W}" '
        f'y2="{TITLEBAR_H}" '
        f'stroke="{FRAME}"/>'
    )

    # Terminal dots
    dots = [
        "#ff5f56",
        "#ffbd2e",
        "#27c93f",
    ]

    for i, color in enumerate(dots):

        parts.append(
            f'<circle '
            f'cx="{PAD + i * 16}" '
            f'cy="{TITLEBAR_H / 2}" '
            f'r="5" '
            f'fill="{color}"/>'
        )

    # Titre
    parts.append(
        f'<text '
        f'x="{CANVAS_W / 2}" '
        f'y="{TITLEBAR_H / 2 + 4}" '
        f'fill="{TITLE_TEXT}" '
        f'font-size="12" '
        f'text-anchor="middle">'
        f'cheikh@github: ~$ ./portrait.sh'
        f'</text>'
    )

    # --------------------------------------------------------
    # ASCII
    # --------------------------------------------------------

    art_top = (
        TITLEBAR_H
        + PAD * 0.35
    )

    font_size = CELL_H * 0.86

    for row_index, line in enumerate(rows):

        y = (
            art_top
            + row_index * CELL_H
            + CELL_H * 0.74
        )

        row_y = (
            art_top
            + row_index * CELL_H
        )

        delay = (
            row_index * STAGGER
        )

        safe_line = html.escape(
            line
        )

        text = (
            f'<text '
            f'xml:space="preserve" '
            f'x="{PAD}" '
            f'y="{y:.1f}" '
            f'fill="{ASCII_COLOR}" '
            f'font-size="{font_size:.1f}" '
            f'textLength="{ART_W}" '
            f'lengthAdjust="spacing">'
            f'{safe_line}'
            f'</text>'
        )

        # Clip animation
        parts.append(
            f'<clipPath id="row-{row_index}">'
            f'<rect '
            f'x="{PAD}" '
            f'y="{row_y:.1f}" '
            f'height="{CELL_H}" '
            f'width="0">'
            f'<animate '
            f'attributeName="width" '
            f'from="0" '
            f'to="{ART_W}" '
            f'begin="{delay:.3f}s" '
            f'dur="{ROW_DURATION:.2f}s" '
            f'fill="freeze"/>'
            f'</rect>'
            f'</clipPath>'
        )

        parts.append(
            f'<g clip-path="url(#row-{row_index})">'
            f'{text}'
            f'</g>'
        )

        # Curseur
        parts.append(
            f'<rect '
            f'y="{row_y + 1:.1f}" '
            f'width="{CELL_W}" '
            f'height="{CELL_H - 2}" '
            f'fill="{CURSOR}" '
            f'opacity="0">'
            f'<animate '
            f'attributeName="x" '
            f'from="{PAD}" '
            f'to="{PAD + ART_W}" '
            f'begin="{delay:.3f}s" '
            f'dur="{ROW_DURATION:.2f}s" '
            f'fill="freeze"/>'
            f'<set '
            f'attributeName="opacity" '
            f'from="0" '
            f'to="0.85" '
            f'begin="{delay:.3f}s"/>'
            f'<set '
            f'attributeName="opacity" '
            f'to="0" '
            f'begin="{delay + ROW_DURATION:.3f}s"/>'
            f'</rect>'
        )

    # --------------------------------------------------------
    # Status bar
    # --------------------------------------------------------

    status_line_y = (
        TITLEBAR_H
        + ART_H
        + PAD * 0.35
    )

    status_y = (
        status_line_y + 19
    )

    parts.append(
        f'<line '
        f'x1="0" '
        f'y1="{status_line_y:.1f}" '
        f'x2="{CANVAS_W}" '
        f'y2="{status_line_y:.1f}" '
        f'stroke="{FRAME}"/>'
    )

    parts.append(
        f'<text '
        f'x="{PAD}" '
        f'y="{status_y:.1f}" '
        f'fill="{TITLE_TEXT}" '
        f'font-size="13">'
        f'cheikh@github:~$ '
        f'<tspan fill="{ASCII_COLOR}">'
        f'whoami'
        f'</tspan>'
        f'</text>'
    )

    parts.append(
        "</svg>"
    )

    return "".join(parts)


# ------------------------------------------------------------
# Main
# ------------------------------------------------------------

def main():

    print("→ Génération du portrait ASCII...")

    rows = generate_ascii_rows()

    svg = create_svg(rows)

    OUTPUT.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    OUTPUT.write_text(
        svg,
        encoding="utf-8",
    )

    print(
        f"✓ Portrait créé : {OUTPUT}"
    )

    print(
        f"  Dimensions : "
        f"{CANVAS_W} × {CANVAS_H}"
    )


if __name__ == "__main__":
    main()