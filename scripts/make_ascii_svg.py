#!/usr/bin/env python3

from pathlib import Path
from html import escape

from PIL import Image, ImageOps


# ============================================================
# Configuration
# ============================================================

INPUT = Path("source-prepped.png")
OUTPUT = Path("assets/ascii.svg")

# Nombre de caractères horizontalement.
# Plus grand = plus détaillé mais SVG plus lourd.
COLUMNS = 100

# Correction du ratio des caractères monospace.
# Les caractères sont plus hauts que larges.
ASPECT_RATIO = 0.50

# Palette ASCII : du plus clair au plus sombre.
CHARS = " .`:-=+*cs#%@"

# Apparence
FONT_SIZE = 10
LINE_HEIGHT = 12

# Couleur du portrait
TEXT_COLOR = "#111111"

# Fond de la carte
BACKGROUND = "#f6f6f3"

# Animation
LINE_DELAY = 0.045
LINE_DURATION = 0.35


# ============================================================
# Image → ASCII
# ============================================================

def image_to_ascii(image: Image.Image) -> list[str]:
    """
    Transforme une image grayscale en lignes ASCII.
    """

    image = ImageOps.grayscale(image)

    width, height = image.size

    # Les caractères monospace ne sont pas carrés.
    # On corrige donc la hauteur.
    new_height = max(
        1,
        int(height * COLUMNS / width * ASPECT_RATIO)
    )

    image = image.resize(
        (COLUMNS, new_height),
        Image.Resampling.LANCZOS,
    )

    pixels = list(image.getdata())

    lines = []

    for y in range(new_height):
        line = []

        for x in range(COLUMNS):
            value = pixels[y * COLUMNS + x]

            # 0 = noir → dernier caractère
            # 255 = blanc → espace
            index = int(
                (255 - value)
                / 255
                * (len(CHARS) - 1)
            )

            line.append(CHARS[index])

        # On supprime les espaces inutiles à droite.
        lines.append("".join(line).rstrip())

    return lines


# ============================================================
# ASCII → SVG animé
# ============================================================

def create_svg(lines: list[str]) -> str:

    width = COLUMNS * FONT_SIZE * 0.60
    height = len(lines) * LINE_HEIGHT + 30

    parts = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<svg xmlns="http://www.w3.org/2000/svg"',
        f'     viewBox="0 0 {width:.0f} {height:.0f}"',
        f'     width="{width:.0f}"',
        f'     height="{height:.0f}">',
        "",
        f'<rect width="100%" height="100%" rx="14" fill="{BACKGROUND}"/>',
        "",
        f'<g fill="{TEXT_COLOR}"',
        '   font-family="monospace"',
        f'   font-size="{FONT_SIZE}px"',
        '   font-weight="600"',
        '   xml:space="preserve">',
        "",
    ]

    # Chaque ligne possède son propre clipPath.
    for i, line in enumerate(lines):

        y = 18 + i * LINE_HEIGHT

        if not line:
            continue

        escaped = escape(line)

        # Largeur approximative de la ligne
        line_width = max(
            FONT_SIZE * 0.60,
            len(line) * FONT_SIZE * 0.60
        )

        clip_id = f"line-{i}"

        begin = i * LINE_DELAY
        end = begin + LINE_DURATION

        parts.extend([
            f'  <clipPath id="{clip_id}">',
            f'    <rect x="0" y="{y - FONT_SIZE}"',
            f'          width="0" height="{LINE_HEIGHT + 4}">',
            f'      <animate',
            f'        attributeName="width"',
            f'        from="0"',
            f'        to="{line_width:.1f}"',
            f'        begin="{begin:.3f}s"',
            f'        dur="{LINE_DURATION:.3f}s"',
            f'        fill="freeze"/>',
            f'    </rect>',
            f'  </clipPath>',
            "",
            f'  <text x="10" y="{y}"',
            f'        clip-path="url(#{clip_id})">',
            f'    {escaped}',
            f'  </text>',
            "",
        ])

    parts.extend([
        "</g>",
        "</svg>",
    ])

    return "\n".join(parts)


# ============================================================
# Main
# ============================================================

def main():

    if not INPUT.exists():
        raise SystemExit(
            f"Erreur : {INPUT} est introuvable."
        )

    OUTPUT.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    print(f"→ Lecture : {INPUT}")

    image = Image.open(INPUT)

    print(
        f"→ Image originale : "
        f"{image.width} × {image.height}"
    )

    print("→ Conversion en ASCII...")

    lines = image_to_ascii(image)

    print(
        f"→ {len(lines)} lignes × {COLUMNS} colonnes"
    )

    print("→ Génération du SVG animé...")

    svg = create_svg(lines)

    OUTPUT.write_text(
        svg,
        encoding="utf-8",
    )

    print(f"✓ SVG créé : {OUTPUT}")


if __name__ == "__main__":
    main()
