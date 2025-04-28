#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
import datetime
from xml.sax.saxutils import escape

# — CONFIGURATION VISUELLE —
WIDTH, HEIGHT = 1200, 380      # +20px en hauteur pour plus d’espace
LEFT_PAD, RIGHT_PAD = 50, 50
TOP, BOTTOM = 50, HEIGHT - 100 # on réserve 100px en bas pour la légende
YEAR = datetime.date.today().year
START = datetime.date(YEAR, 1, 1)
WEEK_WIDTH = (WIDTH - LEFT_PAD - RIGHT_PAD) / 53

# Rails horizontaux
usable_height = BOTTOM - TOP
lanes = {
  "school":   {"y": TOP + 0.1 * usable_height, "color": "#A3B18A", "label": "École (Epitech)"},
  "company":  {"y": TOP + 0.5 * usable_height, "color": "#EEE2B7", "label": "Entreprise (CGI)"},
  "personal": {"y": TOP + 0.9 * usable_height, "color": "#CDB4DB", "label": "Personnel"},
}

# Couleurs des points
type_colors = {
  "certification": "#81B29A",
  "diploma":        "#AAB7F7",
  "project":        "#F3DFA2",
}

# Charger les events
with open('data/events.json', encoding='utf-8') as f:
    events = json.load(f)

def week_index(d: datetime.date) -> int:
    return (d - START).days // 7

today = datetime.date.today()
current_wi = week_index(today)

# — DÉBUT DU SVG —
svg = [
    '<?xml version="1.0" encoding="UTF-8"?>',
    f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}">',
    """
    <style>
      .month-line  { stroke: #c00; stroke-width: 2; }
      .week-line   { stroke: #f88; stroke-width: 1; }
      .current     { stroke: #0a0; stroke-width: 2; }
      .sonar       { animation: pulse 2s ease-out infinite; }
      @keyframes pulse {
        0%   { r: 4;   opacity: 0.8; }
        100% { r: 20;  opacity: 0;   }
      }
      text { font-family: sans-serif; }
    </style>
    """
]

# Lignes de semaines et mois
for wi in range(54):
    x = LEFT_PAD + wi * WEEK_WIDTH
    cls = 'current' if wi == current_wi else 'week-line'
    svg.append(f'<line x1="{x}" y1="{TOP}" x2="{x}" y2="{BOTTOM}" class="{cls}" />')

for m in range(1, 13):
    d = datetime.date(YEAR, m, 1)
    wi = week_index(d)
    x = LEFT_PAD + wi * WEEK_WIDTH
    svg.append(f'<line x1="{x}" y1="{TOP}" x2="{x}" y2="{BOTTOM}" class="month-line" />')
    svg.append(
      f'<text x="{x}" y="{TOP - 5}" text-anchor="middle" font-size="12" fill="#c00">'
      f'{d.strftime("%b")}</text>'
    )

# Rails horizontaux
for info in lanes.values():
    y = info["y"]
    svg.append(
      f'<line x1="{LEFT_PAD}" y1="{y}" x2="{WIDTH - RIGHT_PAD}" y2="{y}" '
      f'stroke="{info["color"]}" stroke-width="2" />'
    )

# Points + sonar + label
for ev in events:
    d      = datetime.date.fromisoformat(ev["date"])
    wi     = week_index(d)
    x      = LEFT_PAD + wi * WEEK_WIDTH
    lane   = lanes[ev["line"]]
    y      = lane["y"]
    color  = type_colors.get(ev["type"], "#000")
    label  = escape(ev["label"])
    svg.append('<g>')
    # point
    svg.append(f'  <circle cx="{x}" cy="{y}" r="4" fill="{color}" />')
    # onde sonar
    svg.append(f'  <circle class="sonar" cx="{x}" cy="{y}" fill="{color}" />')
    # label
    svg.append(
      f'  <text x="{x}" y="{y - 8}" text-anchor="middle" font-size="10" fill="#000">'
      f'{label}</text>'
    )
    svg.append('</g>')

# Légende sous la timeline (une seule ligne)
legend_y = BOTTOM + 20
available_width = WIDTH - LEFT_PAD - RIGHT_PAD
# Construire items rails + points
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
        tx, ty = lx + 35, legend_y + 4
    else:
        svg.append(f'<circle cx="{lx}" cy="{legend_y}" r="5" fill="{col}" />')
        tx, ty = lx + 10, legend_y + 4
    svg.append(
      f'<text x="{tx}" y="{ty}" font-size="12" fill="#000">{lbl}</text>'
    )

svg.append('</svg>')

# ÉCRITURE DU FICHIER
with open('timeline.svg', 'w', encoding='utf-8') as f:
    f.write('\n'.join(svg))
