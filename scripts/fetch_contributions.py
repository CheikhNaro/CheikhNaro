#!/usr/bin/env python3

import datetime
import json
import os
import re
import sys

import requests
from bs4 import BeautifulSoup


# ============================================================
# Configuration
# ============================================================

USERNAME = os.environ.get(
    "GH_PROFILE_USER",
    "CheikhNaro",
)

URL = f"https://github.com/users/{USERNAME}/contributions"

OUT_PATH = os.path.join(
    os.path.dirname(__file__),
    "..",
    "data",
    "contributions.json",
)


# ============================================================
# Fetch GitHub contributions
# ============================================================

def fetch_days():

    print(f"→ Récupération des contributions de @{USERNAME}")
    print(f"→ URL : {URL}")

    response = requests.get(
        URL,
        headers={
            "User-Agent": "CheikhNaro-profile-readme/1.0"
        },
        timeout=30,
    )

    response.raise_for_status()

    soup = BeautifulSoup(
        response.text,
        "html.parser",
    )

    cells = soup.select(
        "td.ContributionCalendar-day"
    )

    if not cells:
        print(
            "❌ Impossible de trouver les cellules "
            "du calendrier GitHub.",
            file=sys.stderr,
        )
        print(
            "GitHub a peut-être modifié son HTML.",
            file=sys.stderr,
        )
        sys.exit(1)

    days = []

    for cell in cells:

        date = cell.get("data-date")

        if not date:
            continue

        cell_id = cell.get("id")

        tooltip = None

        if cell_id:
            tooltip = soup.find(
                "tool-tip",
                attrs={"for": cell_id},
            )

        text = (
            tooltip.get_text(strip=True)
            if tooltip
            else ""
        )

        # Aucun commit
        if re.search(
            r"no contributions",
            text,
            re.IGNORECASE,
        ):
            count = 0

        else:
            match = re.match(
                r"(\d+)",
                text,
            )

            count = (
                int(match.group(1))
                if match
                else 0
            )

        days.append(
            {
                "date": date,
                "count": count,
            }
        )

    days.sort(
        key=lambda day: day["date"]
    )

    return days


# ============================================================
# Streaks
# ============================================================

def compute_current_streak(days):

    index = len(days) - 1

    # Aujourd'hui n'est pas forcément terminé.
    if days[index]["count"] == 0:
        index -= 1

    streak = 0
    end_index = index

    while (
        index >= 0
        and days[index]["count"] > 0
    ):
        streak += 1
        index -= 1

    start_index = index + 1

    if streak == 0:
        return 0, None, None

    return (
        streak,
        days[start_index]["date"],
        days[end_index]["date"],
    )


def compute_longest_streak(days):

    longest = 0
    current = 0

    longest_start = None
    longest_end = None

    current_start = None

    for index, day in enumerate(days):

        if day["count"] > 0:

            if current == 0:
                current_start = index

            current += 1

            if current > longest:

                longest = current

                longest_start = (
                    days[current_start]["date"]
                )

                longest_end = (
                    days[index]["date"]
                )

        else:
            current = 0

    return (
        longest,
        longest_start,
        longest_end,
    )


# ============================================================
# Build JSON
# ============================================================

def build_data(days):

    total = sum(
        day["count"]
        for day in days
    )

    active_days = sum(
        1
        for day in days
        if day["count"] > 0
    )

    best_day = max(
        days,
        key=lambda day: day["count"],
    )

    current_streak = (
        compute_current_streak(days)
    )

    longest_streak = (
        compute_longest_streak(days)
    )

    monthly = {}

    for day in days:

        month = day["date"][:7]

        monthly[month] = (
            monthly.get(month, 0)
            + day["count"]
        )

    monthly_list = [
        {
            "month": month,
            "total": total,
        }
        for month, total
        in sorted(monthly.items())
    ]

    return {

        "username": USERNAME,

        "generated_at":
            datetime.datetime.now(
                datetime.UTC
            ).strftime(
                "%Y-%m-%dT%H:%M:%SZ"
            ),

        "range": {
            "start": days[0]["date"],
            "end": days[-1]["date"],
        },

        "total_contributions": total,

        "active_days": active_days,

        "avg_per_active_day": (
            round(
                total / active_days,
                1,
            )
            if active_days
            else 0
        ),

        "current_streak": {
            "length": current_streak[0],
            "start": current_streak[1],
            "end": current_streak[2],
        },

        "longest_streak": {
            "length": longest_streak[0],
            "start": longest_streak[1],
            "end": longest_streak[2],
        },

        "best_day": {
            "date":
                best_day["date"],
            "count":
                best_day["count"],
        },

        "monthly": monthly_list,

        "days": days,
    }


# ============================================================
# Main
# ============================================================

def main():

    days = fetch_days()

    data = build_data(days)

    output_directory = os.path.dirname(
        OUT_PATH
    )

    os.makedirs(
        output_directory,
        exist_ok=True,
    )

    with open(
        OUT_PATH,
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            data,
            file,
            indent=2,
            ensure_ascii=False,
        )

    print()
    print("✓ Contributions récupérées")
    print(
        f"✓ Total : "
        f"{data['total_contributions']}"
    )
    print(
        f"✓ Jours actifs : "
        f"{data['active_days']}"
    )
    print(
        f"✓ Streak actuel : "
        f"{data['current_streak']['length']} jours"
    )
    print(
        f"✓ Plus long streak : "
        f"{data['longest_streak']['length']} jours"
    )
    print(
        f"✓ Meilleur jour : "
        f"{data['best_day']['count']} contributions "
        f"({data['best_day']['date']})"
    )
    print()
    print(
        f"✓ Données sauvegardées dans "
        f"{OUT_PATH}"
    )


if __name__ == "__main__":
    main()