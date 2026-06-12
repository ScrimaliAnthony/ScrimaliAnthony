#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import datetime as dt
from pathlib import Path
from xml.sax.saxutils import escape

# ─────────────────────────────
# Configuration générale
# ─────────────────────────────

WIDTH, HEIGHT = 1200, 360

LEFT_PAD = 70
RIGHT_PAD = 70
TOP = 70
BOTTOM = 235

TODAY = dt.date.today()
YEAR = TODAY.year

START = dt.date(YEAR, 1, 1)
END = dt.date(YEAR + 1, 1, 1)
TOTAL_DAYS = (END - START).days

OUTPUTS = {
    "light": Path("timeline-light.svg"),
    "dark": Path("timeline-dark.svg"),
}

MONTH_LABELS = [
    "Jan", "Fév", "Mar", "Avr", "Mai", "Juin",
    "Juil", "Aoû", "Sep", "Oct", "Nov", "Déc",
]

LANES = {
    "school": {
        "ratio": 0.25,
        "color": "#2F81F7",
        "label": "École (Epitech)",
    },
    "company": {
        "ratio": 0.50,
        "color": "#F97316",
        "label": "Entreprise (CGI)",
    },
    "personal": {
        "ratio": 0.75,
        "color": "#EC4899",
        "label": "Personnel",
    },
}

TYPE_COLORS = {
    "certification": "#3FB950",
    "diploma": "#22D3EE",
    "project": "#EAB308",
}

THEMES = {
    "light": {
        "background": "#F8F8EA",
        "border": "#D9D9C3",
        "text": "#111827",
        "muted": "#374151",
        "week": "#F3B3B3",
        "month": "#DC2626",
        "current": "#16A34A",
    },
    "dark": {
        "background": "#0D1117",
        "border": "#30363D",
        "text": "#F0F6FC",
        "muted": "#C9D1D9",
        "week": "#30363D",
        "month": "#FF7B72",
        "current": "#3FB950",
    },
}


# ─────────────────────────────
# Données
# ─────────────────────────────

with open("data/events.json", encoding="utf-8") as f:
    EVENTS = json.load(f)


# ─────────────────────────────
# Helpers
# ─────────────────────────────

def x_from_date(date: dt.date) -> float:
    days = (date - START).days
    return LEFT_PAD + (days / TOTAL_DAYS) * (WIDTH - LEFT_PAD - RIGHT_PAD)


def lane_y(line: str) -> float:
    usable_height = BOTTOM - TOP
    return TOP + LANES[line]["ratio"] * usable_height


def build_svg(theme_name: str) -> str:
    theme = THEMES[theme_name]

    svg = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        (
            f'<svg xmlns="http://www.w3.org/2000/svg" '
            f'viewBox="0 0 {WIDTH} {HEIGHT}" '
            f'width="100%" '
            f'preserveAspectRatio="xMidYMid meet">'
        ),
        f"""
<style>
  text {{
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  }}

  .week-line {{
    stroke: {theme["week"]};
    stroke-width: 1;
  }}

  .month-line {{
    stroke: {theme["month"]};
    stroke-width: 2;
  }}

  .current-line {{
    stroke: {theme["current"]};
    stroke-width: 3;
  }}

  .event-label {{
    fill: {theme["text"]};
    font-size: 14px;
    font-weight: 600;
  }}

  .month-label {{
    fill: {theme["month"]};
    font-size: 15px;
    font-weight: 700;
  }}

  .legend-label {{
    fill: {theme["muted"]};
    font-size: 15px;
  }}
</style>
""",
        (
            f'<rect x="0" y="0" width="{WIDTH}" height="{HEIGHT}" '
            f'rx="18" fill="{theme["background"]}" stroke="{theme["border"]}" />'
        ),
    ]

    # ─────────────────────────────
    # Lignes de semaines
    # ─────────────────────────────

    current = START
    while current < END:
        x = x_from_date(current)
        svg.append(
            f'<line x1="{x:.2f}" y1="{TOP}" x2="{x:.2f}" y2="{BOTTOM}" class="week-line" />'
        )
        current += dt.timedelta(days=7)

    # Ligne de fin exacte, sans dépasser après décembre
    x_end = x_from_date(END)
    svg.append(
        f'<line x1="{x_end:.2f}" y1="{TOP}" x2="{x_end:.2f}" y2="{BOTTOM}" class="week-line" />'
    )

    # ─────────────────────────────
    # Lignes et labels de mois
    # ─────────────────────────────

    for month in range(1, 13):
        date = dt.date(YEAR, month, 1)
        x = x_from_date(date)

        svg.append(
            f'<line x1="{x:.2f}" y1="{TOP}" x2="{x:.2f}" y2="{BOTTOM}" class="month-line" />'
        )
        svg.append(
            f'<text x="{x:.2f}" y="{TOP - 12}" text-anchor="middle" class="month-label">'
            f'{MONTH_LABELS[month - 1]}</text>'
        )

    # ─────────────────────────────
    # Ligne du jour courant
    # ─────────────────────────────

    if START <= TODAY < END:
        x_today = x_from_date(TODAY)
        svg.append(
            f'<line x1="{x_today:.2f}" y1="{TOP - 5}" x2="{x_today:.2f}" y2="{BOTTOM + 5}" '
            f'class="current-line" />'
        )

    # ─────────────────────────────
    # Rails horizontaux
    # ─────────────────────────────

    for key, info in LANES.items():
        y = lane_y(key)
        svg.append(
            f'<line x1="{LEFT_PAD}" y1="{y:.2f}" x2="{WIDTH - RIGHT_PAD}" y2="{y:.2f}" '
            f'stroke="{info["color"]}" stroke-width="4" stroke-linecap="round" />'
        )

    # ─────────────────────────────
    # Événements
    # ─────────────────────────────

    sorted_events = sorted(EVENTS, key=lambda item: item["date"])

    for event in sorted_events:
        date = dt.date.fromisoformat(event["date"])

        if not START <= date < END:
            continue

        x = x_from_date(date)
        y = lane_y(event["line"])

        color = TYPE_COLORS.get(event["type"], "#6B7280")
        label = escape(event["label"])

        svg.append("<g>")
        svg.append(
            f'  <circle cx="{x:.2f}" cy="{y:.2f}" r="6" fill="{color}" />'
        )
        svg.append(
            f'  <circle cx="{x:.2f}" cy="{y:.2f}" r="6" fill="{color}" opacity="0.35">'
            f'<animate attributeName="r" values="6;22" dur="2s" repeatCount="indefinite" />'
            f'<animate attributeName="opacity" values="0.35;0" dur="2s" repeatCount="indefinite" />'
            f'</circle>'
        )
        svg.append(
            f'  <text x="{x:.2f}" y="{y - 14:.2f}" text-anchor="middle" class="event-label">'
            f'{label}</text>'
        )
        svg.append("</g>")

    # ─────────────────────────────
    # Légende
    # ─────────────────────────────

    legend_items = []

    for key, info in LANES.items():
        legend_items.append(("line", info["color"], info["label"]))

    legend_items.extend([
        ("circle", TYPE_COLORS["certification"], "Certification"),
        ("circle", TYPE_COLORS["diploma"], "Diplôme"),
        ("circle", TYPE_COLORS["project"], "Projet"),
    ])

    legend_y = BOTTOM + 45
    available_width = WIDTH - LEFT_PAD - RIGHT_PAD
    spacing = available_width / len(legend_items)

    for index, (shape, color, label) in enumerate(legend_items):
        x = LEFT_PAD + index * spacing + 5

        if shape == "line":
            svg.append(
                f'<line x1="{x:.2f}" y1="{legend_y}" x2="{x + 30:.2f}" y2="{legend_y}" '
                f'stroke="{color}" stroke-width="4" stroke-linecap="round" />'
            )
            text_x = x + 40
        else:
            svg.append(
                f'<circle cx="{x:.2f}" cy="{legend_y}" r="6" fill="{color}" />'
            )
            text_x = x + 16

        svg.append(
            f'<text x="{text_x:.2f}" y="{legend_y + 5}" text-anchor="start" class="legend-label">'
            f'{escape(label)}</text>'
        )

    svg.append("</svg>")

    return "\n".join(svg)


# ─────────────────────────────
# Génération
# ─────────────────────────────

for theme_name, output_path in OUTPUTS.items():
    output_path.write_text(build_svg(theme_name), encoding="utf-8")
    print(f"Generated: {output_path}")

# Fallback optionnel pour garder l'ancien chemin si besoin
Path("timeline.svg").write_text(build_svg("light"), encoding="utf-8")
print("Generated: timeline.svg")