#!/usr/bin/env python3

import datetime
import json
import os


# ============================================================
# Paths
# ============================================================

HERE = os.path.dirname(__file__)

INPUT = os.path.join(
    HERE,
    "..",
    "data",
    "contributions.json",
)

OUTPUT = os.path.join(
    HERE,
    "..",
    "assets",
    "contrib-heatmap.svg",
)


# ============================================================
# GitHub-style palette
# ============================================================

PALETTE = [
    "#161b22",
    "#0e4429",
    "#006d32",
    "#26a641",
    "#39d353",
    "#69f0a0",
]


# ============================================================
# Layout
# ============================================================

CELL = 12
GAP = 3
STEP = CELL + GAP

PAD = 22

LEFT_LABEL_WIDTH = 30
TOP_LABEL_HEIGHT = 20
TITLEBAR_HEIGHT = 30

BACKGROUND = "#0a0e14"
BACKGROUND_2 = "#0d1420"

FRAME = "#1f6feb"

MUTED = "#7d8590"
TEXT = "#e6edf3"

ACCENT = "#22d3ee"
GREEN = "#39d353"
GOLD = "#f2cc60"


# ============================================================
# Animation
# ============================================================

COLUMN_DELAY = 0.018
ROW_DELAY = 0.045

CELL_DURATION = 0.42


# ============================================================
# Contribution level
# ============================================================

def level_for(count):

    if count == 0:
        return 0

    if count <= 5:
        return 1

    if count <= 15:
        return 2

    if count <= 30:
        return 3

    if count <= 50:
        return 4

    return 5


# ============================================================
# Build calendar grid
# ============================================================

def build_grid(days):

    first_date = datetime.date.fromisoformat(
        days[0]["date"]
    )

    # GitHub calendar starts on Sunday.
    first_weekday = (
        first_date.weekday() + 1
    ) % 7

    grid = []

    column = [
        None
    ] * first_weekday

    for day in days:

        date = datetime.date.fromisoformat(
            day["date"]
        )

        weekday = (
            date.weekday() + 1
        ) % 7

        while len(column) < weekday:
            column.append(None)

        column.append(
            (
                day["date"],
                day["count"],
                level_for(day["count"]),
            )
        )

        if len(column) == 7:

            grid.append(column)

            column = []

    if column:

        while len(column) < 7:
            column.append(None)

        grid.append(column)

    return grid


# ============================================================
# Render SVG
# ============================================================

def render(data):

    days = data["days"]

    grid = build_grid(days)

    columns = len(grid)

    art_width = columns * STEP
    art_height = 7 * STEP

    # --------------------------------------------------------
    # Month labels
    # --------------------------------------------------------

    month_labels = []

    seen_months = set()

    for column_index, column in enumerate(grid):

        for cell in column:

            if cell is None:
                continue

            date = datetime.date.fromisoformat(
                cell[0]
            )

            key = (
                date.year,
                date.month,
            )

            if (
                key not in seen_months
                and date.day <= 7
            ):

                seen_months.add(key)

                month_labels.append(
                    (
                        column_index,
                        date.strftime("%b"),
                    )
                )

            break

    # --------------------------------------------------------
    # Canvas
    # --------------------------------------------------------

    canvas_width = (
        PAD
        + LEFT_LABEL_WIDTH
        + art_width
        + PAD
    )

    stats_height = 88

    canvas_height = (
        TITLEBAR_HEIGHT
        + TOP_LABEL_HEIGHT
        + art_height
        + stats_height
        + PAD
    )

    # --------------------------------------------------------
    # CSS animation
    # --------------------------------------------------------

    css = f"""
    @keyframes cellReveal {{
        0% {{
            opacity: 0;
            transform: translateY(-6px);
        }}

        100% {{
            opacity: 1;
            transform: translateY(0);
        }}
    }}

    .cell {{
        opacity: 0;
        animation:
            cellReveal
            {CELL_DURATION:.2f}s
            cubic-bezier(.2,.8,.2,1)
            both;
    }}
    """.strip()

    parts = [

        f'<svg '
        f'xmlns="http://www.w3.org/2000/svg" '
        f'width="{canvas_width}" '
        f'height="{canvas_height}" '
        f'viewBox="0 0 '
        f'{canvas_width} '
        f'{canvas_height}" '
        f'font-family="ui-monospace, '
        f'SFMono-Regular, Menlo, '
        f'Consolas, monospace">',

        f"<style>{css}</style>",

        "<defs>",

        (
            '<linearGradient id="background" '
            'x1="0" y1="0" x2="0" y2="1">'
        ),

        (
            f'<stop offset="0" '
            f'stop-color="{BACKGROUND_2}"/>'
        ),

        (
            f'<stop offset="1" '
            f'stop-color="{BACKGROUND}"/>'
        ),

        "</linearGradient>",

        "</defs>",

        (
            f'<rect width="100%" '
            f'height="100%" '
            f'rx="12" '
            f'fill="url(#background)"/>'
        ),

        (
            f'<rect x="0.5" y="0.5" '
            f'width="{canvas_width - 1}" '
            f'height="{canvas_height - 1}" '
            f'rx="12" '
            f'fill="none" '
            f'stroke="{FRAME}" '
            f'stroke-width="1" '
            f'stroke-opacity="0.55"/>'
        ),

        (
            f'<line x1="0" y1="{TITLEBAR_HEIGHT}" '
            f'x2="{canvas_width}" '
            f'y2="{TITLEBAR_HEIGHT}" '
            f'stroke="{FRAME}" '
            f'stroke-opacity="0.35"/>'
        ),
    ]

    # --------------------------------------------------------
    # Terminal buttons
    # --------------------------------------------------------

    for index, color in enumerate(
        [
            "#ff5f56",
            "#ffbd2e",
            "#27c93f",
        ]
    ):

        parts.append(
            f'<circle '
            f'cx="{PAD + index * 16}" '
            f'cy="{TITLEBAR_HEIGHT / 2}" '
            f'r="5" '
            f'fill="{color}"/>'
        )

    parts.append(
        f'<text '
        f'x="{canvas_width / 2}" '
        f'y="{TITLEBAR_HEIGHT / 2 + 4}" '
        f'fill="{MUTED}" '
        f'font-size="12" '
        f'text-anchor="middle">'
        f'cheikh@github: ~/contributions --graph'
        f'</text>'
    )

    # --------------------------------------------------------
    # Grid position
    # --------------------------------------------------------

    grid_top = (
        TITLEBAR_HEIGHT
        + TOP_LABEL_HEIGHT
    )

    grid_left = (
        PAD
        + LEFT_LABEL_WIDTH
    )

    # --------------------------------------------------------
    # Month labels
    # --------------------------------------------------------

    for column_index, label in month_labels:

        x = (
            grid_left
            + column_index * STEP
        )

        parts.append(
            f'<text '
            f'x="{x}" '
            f'y="{TITLEBAR_HEIGHT + 14}" '
            f'fill="{MUTED}" '
            f'font-size="10">'
            f'{label}'
            f'</text>'
        )

    # --------------------------------------------------------
    # Weekday labels
    # --------------------------------------------------------

    for row_index, name in [
        (1, "Mon"),
        (3, "Wed"),
        (5, "Fri"),
    ]:

        y = (
            grid_top
            + row_index * STEP
            + CELL * 0.78
        )

        parts.append(
            f'<text '
            f'x="{PAD}" '
            f'y="{y:.1f}" '
            f'fill="{MUTED}" '
            f'font-size="9">'
            f'{name}'
            f'</text>'
        )

    # --------------------------------------------------------
    # Contribution cells
    # --------------------------------------------------------

    for column_index, column in enumerate(grid):

        x = (
            grid_left
            + column_index * STEP
        )

        for row_index, cell in enumerate(column):

            if cell is None:
                continue

            date_string, count, level = cell

            y = (
                grid_top
                + row_index * STEP
            )

            delay = (
                column_index * COLUMN_DELAY
                + row_index * ROW_DELAY
            )

            plural = (
                "s"
                if count != 1
                else ""
            )

            parts.append(

                f'<rect '
                f'class="cell" '
                f'x="{x}" '
                f'y="{y}" '
                f'width="{CELL}" '
                f'height="{CELL}" '
                f'rx="2.5" '
                f'fill="{PALETTE[level]}" '
                f'style="'
                f'animation-delay:{delay:.3f}s'
                f'">'

                f'<title>'
                f'{date_string}: '
                f'{count} contribution{plural}'
                f'</title>'

                f'</rect>'
            )

    # --------------------------------------------------------
    # Legend
    # --------------------------------------------------------

    legend_y = (
        grid_top
        + art_height
        + 6
    )

    legend_x = (
        canvas_width
        - PAD
        - (
            len(PALETTE)
            * (CELL - 1)
            + 70
        )
    )

    parts.append(
        f'<text '
        f'x="{legend_x}" '
        f'y="{legend_y + CELL * 0.8:.1f}" '
        f'fill="{MUTED}" '
        f'font-size="10" '
        f'text-anchor="end">'
        f'Less'
        f'</text>'
    )

    x = legend_x + 8

    for color in PALETTE:

        parts.append(
            f'<rect '
            f'x="{x}" '
            f'y="{legend_y}" '
            f'width="{CELL - 1}" '
            f'height="{CELL - 1}" '
            f'rx="2.2" '
            f'fill="{color}"/>'
        )

        x += CELL

    parts.append(
        f'<text '
        f'x="{x + 4}" '
        f'y="{legend_y + CELL * 0.8:.1f}" '
        f'fill="{MUTED}" '
        f'font-size="10">'
        f'More'
        f'</text>'
    )

    # --------------------------------------------------------
    # Statistics
    # --------------------------------------------------------

    separator_y = (
        legend_y
        + CELL
        + 14
    )

    parts.append(
        f'<line '
        f'x1="0" '
        f'y1="{separator_y}" '
        f'x2="{canvas_width}" '
        f'y2="{separator_y}" '
        f'stroke="{FRAME}" '
        f'stroke-opacity="0.25"/>'
    )

    current_streak = data[
        "current_streak"
    ]["length"]

    longest_streak = data[
        "longest_streak"
    ]["length"]

    total = data[
        "total_contributions"
    ]

    best = data["best_day"]

    date_range = data["range"]

    y = separator_y + 24

    parts.append(
        f'<text '
        f'x="{PAD}" '
        f'y="{y}" '
        f'font-size="13" '
        f'fill="{GREEN}">'

        f'<tspan font-weight="700">'
        f'{total:,}'
        f'</tspan>'

        f'<tspan fill="{MUTED}">'
        f' contributions in the last year'
        f'</tspan>'

        f'</text>'
    )

    parts.append(
        f'<text '
        f'x="{canvas_width - PAD}" '
        f'y="{y}" '
        f'font-size="12" '
        f'fill="{MUTED}" '
        f'text-anchor="end">'
        f'{date_range["start"]}'
        f' → '
        f'{date_range["end"]}'
        f'</text>'
    )

    y += 24

    parts.append(
        f'<text '
        f'x="{PAD}" '
        f'y="{y}" '
        f'font-size="13" '
        f'fill="{MUTED}">'

        f'current streak '

        f'<tspan '
        f'fill="{ACCENT}" '
        f'font-weight="700">'
        f'{current_streak} days'
        f'</tspan>'

        f'<tspan fill="{MUTED}">'
        f'   ·   longest '
        f'</tspan>'

        f'<tspan '
        f'fill="{ACCENT}" '
        f'font-weight="700">'
        f'{longest_streak} days'
        f'</tspan>'

        f'</text>'
    )

    parts.append(
        f'<text '
        f'x="{canvas_width - PAD}" '
        f'y="{y}" '
        f'font-size="12" '
        f'fill="{MUTED}" '
        f'text-anchor="end">'

        f'best day '

        f'<tspan '
        f'fill="{GOLD}" '
        f'font-weight="700">'
        f'{best["count"]}'
        f'</tspan>'

        f' on {best["date"]}'

        f'</text>'
    )

    parts.append("</svg>")

    return "".join(parts)


# ============================================================
# Main
# ============================================================

def main():

    with open(
        INPUT,
        "r",
        encoding="utf-8",
    ) as file:

        data = json.load(file)

    svg = render(data)

    os.makedirs(
        os.path.dirname(OUTPUT),
        exist_ok=True,
    )

    with open(
        OUTPUT,
        "w",
        encoding="utf-8",
    ) as file:

        file.write(svg)

    print(
        f"✓ Heatmap créée : {OUTPUT}"
    )

    print(
        f"✓ Taille : {len(svg):,} bytes"
    )


if __name__ == "__main__":
    main()