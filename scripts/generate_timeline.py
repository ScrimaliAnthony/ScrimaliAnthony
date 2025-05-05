#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
import datetime
from xml.sax.saxutils import escape

# — CONFIGURATION VISUELLE —
WIDTH, HEIGHT = 1200, 380
LEFT_PAD, RIGHT_PAD = 50, 50
TOP, BOTTOM = 50, HEIGHT - 100
YEAR = datetime.date.today().year
START = datetime.date(YEAR, 1, 1)
WEEK_WIDTH = (WIDTH - LEFT_PAD - RIGHT_PAD) / 53

# Rails horizontaux avec espacement égal (25%, 50%, 75%)
usable_height = BOTTOM - TOP
lanes = {
    "school":   {"y": TOP + 0.25 * usable_height, "color": "#1E90FF", "label": "École (Epitech)"},
    "company":  {"y": TOP + 0.5  * usable_height, "color": "#FF8C00", "label": "Entreprise (CGI)"},
    "personal": {"y": TOP + 0.75 * usable_height, "color": "#FF1493", "label": "Personnel"},
}

# Couleurs des points selon type d’événement
type_colors = {
  "certification": "#32CD32",
  "diploma":        "#00CED1",
  "project":        "#FFD700",
}

# Chargement des événements
with open('data/events.json', encoding='utf-8') as f:
    events = json.load(f)


def week_index(d: datetime.date) -> int:
    return (d - START).days // 7


today = datetime.date.today()
current_wi = week_index(today)

# — DÉBUT DU SVG (responsive) —
svg = [
    '<?xml version="1.0" encoding="UTF-8"?>',
    f'<svg xmlns="http://www.w3.org/2000/svg" '
    f'     viewBox="0 0 {WIDTH} {HEIGHT}" '
    f'     width="100%" '
    f'     preserveAspectRatio="xMidYMid meet">',
    """
    <style>
      .month-line  { stroke: #c00;  stroke-width: 2; }
      .week-line   { stroke: #f88;  stroke-width: 1; }
      .current     { stroke: #0a0;  stroke-width: 3; }
      .sonar       { animation: pulse 2s ease-out infinite; }
      @keyframes pulse {
        0%   { r: 5;   opacity: 0.8; }
        100% { r: 20;  opacity: 0;   }
      }
      text { font-family: sans-serif; }
    </style>
    """
]

# 1) Lignes de mois
for m in range(1, 13):
    d = datetime.date(YEAR, m, 1)
    wi = week_index(d)
    x = LEFT_PAD + wi * WEEK_WIDTH
    svg.append(f'<line x1="{x}" y1="{TOP}" x2="{x}" y2="{BOTTOM}" class="month-line" />')
    svg.append(
        f'<text x="{x}" y="{TOP - 5}" text-anchor="middle" font-size="16" fill="#c00">'
        f'{d.strftime("%b")}</text>'
    )

# 2) Lignes de semaines (avec la courante en dernier)
for wi in range(54):
    x = LEFT_PAD + wi * WEEK_WIDTH
    cls = 'current' if wi == current_wi else 'week-line'
    svg.append(f'<line x1="{x}" y1="{TOP}" x2="{x}" y2="{BOTTOM}" class="{cls}" />')

# 3) Rails horizontaux vifs
for info in lanes.values():
    y = info["y"]
    svg.append(
        f'<line x1="{LEFT_PAD}" y1="{y}" x2="{WIDTH - RIGHT_PAD}" y2="{y}" '
        f'stroke="{info["color"]}" stroke-width="3" />'
    )

# 4) Points sonar + labels
for ev in events:
    d      = datetime.date.fromisoformat(ev["date"])
    wi     = week_index(d)
    x      = LEFT_PAD + wi * WEEK_WIDTH
    lane   = lanes[ev["line"]]
    y      = lane["y"]
    color  = type_colors.get(ev["type"], "#000")
    label  = escape(ev["label"])
    svg.append('<g>')
    svg.append(f'  <circle cx="{x}" cy="{y}" r="5" fill="{color}" />')
    svg.append(f'  <circle class="sonar" cx="{x}" cy="{y}" fill="{color}" />')
    svg.append(
        f'  <text x="{x}" y="{y - 10}" text-anchor="middle" font-size="14" fill="#000">'
        f'{label}</text>'
    )
    svg.append('</g>')

# 5) Légende sous la timeline
legend_y = BOTTOM + 20
available_width = WIDTH - LEFT_PAD - RIGHT_PAD
legend_items = []
for _, info in lanes.items():
    legend_items.append(("line", info["color"], info["label"]))
for t, lbl in [("certification","Certification"),("diploma","Diplôme"),("project","Projet")]:
    legend_items.append(("circle", type_colors[t], lbl))

n = len(legend_items)
spacing = available_width / n
for i, (shape, col, lbl) in enumerate(legend_items):
    lx = LEFT_PAD + i * spacing
    if shape == "line":
        svg.append(
            f'<line x1="{lx}" y1="{legend_y}" x2="{lx+30}" y2="{legend_y}" '
            f'stroke="{col}" stroke-width="4" />'
        )
        tx, ty = lx + 35, legend_y + 6
    else:
        svg.append(f'<circle cx="{lx}" cy="{legend_y}" r="6" fill="{col}" />')
        tx, ty = lx + 12, legend_y + 6
    svg.append(
        f'<text x="{tx}" y="{ty}" text-anchor="start" font-size="16" fill="#000">'
        f'{lbl}</text>'
    )

svg.append('</svg>')

# ÉCRITURE DU FICHIER
with open('timeline.svg', 'w', encoding='utf-8') as f:
    f.write('\n'.join(svg))
