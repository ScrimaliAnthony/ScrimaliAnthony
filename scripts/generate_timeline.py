#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
import datetime
from xml.sax.saxutils import escape

# — CONFIGURATION VISUELLE —
WIDTH, HEIGHT = 1200, 360        # Hauteur augmentée
LEFT_PAD, RIGHT_PAD = 50, 50
TOP = 50
BOTTOM = HEIGHT - 100           # On réserve 100 px en bas pour la légende et la bulle
YEAR = datetime.date.today().year
START = datetime.date(YEAR, 1, 1)
WEEK_WIDTH = (WIDTH - LEFT_PAD - RIGHT_PAD) / 53

# Couleurs “craie” et positions des 3 rails
usable_height = BOTTOM - TOP
lanes = {
    "school":   {"y": TOP + 0.1 * usable_height, "color": "#A3B18A", "label": "École (Epitech)"},
    "company":  {"y": TOP + 0.5 * usable_height, "color": "#EEE2B7", "label": "Entreprise (CGI)"},
    "personal": {"y": TOP + 0.9 * usable_height, "color": "#CDB4DB", "label": "Personnel"}
}

# Couleurs des points selon type
type_colors = {
    "certification": "#81B29A",
    "diploma":        "#AAB7F7",
    "project":        "#F3DFA2"
}

# Chargement des événements
with open('data/events.json', encoding='utf-8') as f:
    events = json.load(f)

def week_index(d: datetime.date) -> int:
    return (d - START).days // 7

today = datetime.date.today()
current_wi = week_index(today)

# — DÉBUT SVG —
svg = [
    '<?xml version="1.0" encoding="UTF-8"?>',
    '<svg '
      'xmlns="http://www.w3.org/2000/svg" '
      'xmlns:xlink="http://www.w3.org/1999/xlink" '
      f'width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}">',
    """
    <style>
      .month-line  { stroke: #c00; stroke-width: 2; }
      .week-line   { stroke: #f88; stroke-width: 1; }
      .current     { stroke: #0a0; stroke-width: 2; }
      .sonar       { animation: pulse 2s ease-out infinite; }
      .hitbox      { fill: transparent; cursor: pointer; }
      .tooltip-box { visibility: hidden; }
      .tooltip:hover .tooltip-box { visibility: visible; }
      @keyframes pulse {
        0%   { r: 4;   opacity: 0.8; }
        100% { r: 20;  opacity: 0;   }
      }
      text { font-family: sans-serif; }
    </style>
    """
]

# — TRACÉS DES SEMAINES & MOIS —
for wi in range(54):
    x = LEFT_PAD + wi * WEEK_WIDTH
    cls = 'current' if wi == current_wi else 'week-line'
    svg.append(f'<line x1="{x}" y1="{TOP}" x2="{x}" y2="{BOTTOM}" class="{cls}" />')

for m in range(1,13):
    d = datetime.date(YEAR, m, 1)
    wi = week_index(d)
    x = LEFT_PAD + wi * WEEK_WIDTH
    svg.append(f'<line x1="{x}" y1="{TOP}" x2="{x}" y2="{BOTTOM}" class="month-line" />')
    svg.append(
        f'<text x="{x}" y="{TOP-5}" text-anchor="middle" font-size="12" fill="#c00">'
        f'{d.strftime("%b")}</text>'
    )

# — RAILS HORIZONTAUX —
for info in lanes.values():
    y = info["y"]
    svg.append(
        f'<line x1="{LEFT_PAD}" y1="{y}" x2="{WIDTH-RIGHT_PAD}" y2="{y}" '
        f'stroke="{info["color"]}" stroke-width="2"/>'
    )

# — ÉVÉNEMENTS AVEC HITBOX, SONAR & BULLE PERSONNALISÉE —
for ev in events:
    d      = datetime.date.fromisoformat(ev["date"])
    wi     = week_index(d)
    x      = LEFT_PAD + wi * WEEK_WIDTH
    lane   = lanes[ev["line"]]
    y      = lane["y"]
    color  = type_colors.get(ev["type"], "#000")
    label  = escape(ev["label"])
    detail = escape(ev.get("detail", ""))
    link   = ev.get("link", "")   # optionnel dans ton JSON

    svg.append('<g class="tooltip">')
    # plus grande zone de survol
    svg.append(f'<circle class="hitbox" cx="{x}" cy="{y}" r="10"/>')
    # point
    svg.append(f'<circle cx="{x}" cy="{y}" r="4" fill="{color}"/>')
    # onde sonar
    svg.append(f'<circle class="sonar" cx="{x}" cy="{y}" fill="{color}"/>')
    # label fixe au-dessus
    svg.append(
        f'<text x="{x}" y="{y-8}" text-anchor="middle" font-size="10" fill="#000">'
        f'{label}</text>'
    )
    # bulles stylées
    # dimensions fixes ; tu peux ajuster width/height si nécessaire
    bx, by = x+12, y-80
    svg.append(f'<g class="tooltip-box">')
    svg.append(
        f'<rect x="{bx}" y="{by}" width="160" height="60" '
        f'rx="5" ry="5" fill="#FFF" stroke="#666" stroke-width="1"/>'
    )
    # texte de détail (une seule ligne, tronqué si trop long)
    svg.append(
        f'<text x="{bx+8}" y="{by+20}" font-size="10" fill="#000">'
        f'{detail}</text>'
    )
    # lien cliquable (fonctionnera si le SVG est inline ; en externe, GitHub peut le bloquer)
    if link:
        svg.append(
            f'<a xlink:href="{escape(link)}" target="_blank">'
            f'<text x="{bx+8}" y="{by+35}" font-size="10" fill="#06C" text-decoration="underline">'
            f'Voir plus...</text>'
            f'</a>'
        )
    svg.append('</g>')
    svg.append('</g>')

# — LÉGENDE SOUS LA TIMELINE (UNE SEULE LIGNE) —
legend_start_y = BOTTOM + 20
available_width = WIDTH - LEFT_PAD - RIGHT_PAD
# construction de la liste
legend_items = []
for k,info in lanes.items():
    legend_items.append({"shape":"line","color":info["color"],"label":info["label"]})
for t,lbl in [("certification","Certification"),("diploma","Diplôme"),("project","Projet")]:
    legend_items.append({"shape":"circle","color":type_colors[t],"label":lbl})
n = len(legend_items)
spacing = available_width / n

for i,item in enumerate(legend_items):
    lx = LEFT_PAD + i * spacing
    if item["shape"] == "line":
        svg.append(
            f'<line x1="{lx}" y1="{legend_start_y}" x2="{lx+30}" y2="{legend_start_y}" '
            f'stroke="{item["color"]}" stroke-width="4"/>'
        )
        tx, ty = lx+35, legend_start_y+4
    else:
        svg.append(f'<circle cx="{lx}" cy="{legend_start_y}" r="5" fill="{item["color"]}"/>')
        tx, ty = lx+10, legend_start_y+4
    svg.append(
        f'<text x="{tx}" y="{ty}" font-size="12" fill="#000">'
        f'{item["label"]}</text>'
    )

svg.append('</svg>')

# — ÉCRITURE DU FICHIER —
with open('timeline.svg','w', encoding='utf-8') as f:
    f.write('\n'.join(svg))
