#!/usr/bin/env python3

from pathlib import Path
from html import escape


OUTPUT = Path("assets/info-card.svg")

# ------------------------------------------------------------
# Configuration
# ------------------------------------------------------------

WIDTH = 520
HEIGHT = 330

BACKGROUND = "#f6f6f3"
TEXT = "#111111"
MUTED = "#666666"

FONT = "monospace"

TITLE_SIZE = 18
TEXT_SIZE = 13

LINE_HEIGHT = 25

LEFT_LABEL_X = 25
VALUE_X = 145

TOP = 45

ANIMATION_DELAY = 0.12
ANIMATION_DURATION = 0.35


# ------------------------------------------------------------
# Informations du profil
# ------------------------------------------------------------

LINES = [
    ("label", "OS", "Fedora (btw)"),
    ("label", "WM", "Hyprland"),
    ("label", "Focus", "Web Development"),

    ("empty", "", ""),

    ("label", "Frontend", "React · Next.js · Vue.js"),
    ("label", "Backend", "Laravel · NodeJS · FastAPI"),
    ("label", "Languages", "TypeScript · Python"),
    ("label", "Tools", "Git · Linux"),

    ("empty", "", ""),

    ("label", "Status", "Building..."),
]


# ------------------------------------------------------------
# SVG
# ------------------------------------------------------------

def create_svg():

    parts = [
        '<?xml version="1.0" encoding="UTF-8"?>',

        '<svg xmlns="http://www.w3.org/2000/svg"',
        f'     viewBox="0 0 {WIDTH} {HEIGHT}"',
        f'     width="{WIDTH}"',
        f'     height="{HEIGHT}">',

        "",

        f'<rect width="100%" height="100%" rx="16" fill="{BACKGROUND}"/>',

        "",

        # Header
        f'<text x="25" y="32"',
        f'      font-family="{FONT}"',
        f'      font-size="{TITLE_SIZE}px"',
        f'      font-weight="700"',
        f'      fill="{TEXT}">',
        "cheikh@github",
        "</text>",

        "",

        f'<line x1="25" y1="48" x2="{WIDTH - 25}" y2="48"',
        f'      stroke="{MUTED}" stroke-width="1"/>',

        "",
    ]

    visible_index = 0

    for i, (kind, label, value) in enumerate(LINES):

        y = TOP + 35 + i * LINE_HEIGHT

        if kind == "empty":
            continue

        group_id = f"line-{visible_index}"

        begin = visible_index * ANIMATION_DELAY

        parts.extend([
            f'<g id="{group_id}" opacity="0">',

            "  <animate",
            '    attributeName="opacity"',
            '    from="0"',
            '    to="1"',
            f'    begin="{begin:.2f}s"',
            f'    dur="{ANIMATION_DURATION:.2f}s"',
            '    fill="freeze"/>',

            "",

            f'  <text x="{LEFT_LABEL_X}" y="{y}"',
            f'        font-family="{FONT}"',
            f'        font-size="{TEXT_SIZE}px"',
            '        font-weight="700"',
            f'        fill="{TEXT}">',
            f'    {escape(label)}',
            "  </text>",

            f'  <text x="{VALUE_X}" y="{y}"',
            f'        font-family="{FONT}"',
            f'        font-size="{TEXT_SIZE}px"',
            f'        fill="{TEXT}">',
            f'    {escape(value)}',
            "  </text>",

            "</g>",
            "",
        ])

        visible_index += 1

    parts.extend([
        "</svg>",
    ])

    return "\n".join(parts)


# ------------------------------------------------------------
# Main
# ------------------------------------------------------------

def main():

    OUTPUT.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    print("→ Génération de la carte info...")

    svg = create_svg()

    OUTPUT.write_text(
        svg,
        encoding="utf-8",
    )

    print(f"✓ Carte créée : {OUTPUT}")


if __name__ == "__main__":
    main()