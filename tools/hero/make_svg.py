#!/usr/bin/env python3
"""Writes cs-hero.svg (1600x900): the banner on the home page.

Nine real places on Mars, placed by latitude and longitude, joined by roads whose lengths are the true great-circle
distances (Mars mean radius 3389.5 km). The orange route is the shortest one from Erebus Montes to Gale crater,
found by Dijkstra's algorithm in this script, so the picture is a correct answer, not a drawing of one. Sorting bars,
a recursion tree and the formulas the site explains fill the rest.
"""
import heapq, math, pathlib

W, H = 1600, 900
R_MARS = 3389.5
PLACES = {  # name: (latitude N, longitude E), from the USGS Gazetteer of Planetary Nomenclature
    "Erebus Montes": (35.7, -175.0),
    "Olympus Mons": (18.65, -133.8),
    "Ascraeus Mons": (11.92, -104.08),
    "Valles Marineris": (-13.9, -59.2),
    "Elysium Mons": (25.02, 147.21),
    "Utopia Planitia": (47.97, 134.26),
    "Gale crater": (-5.4, 137.8),
    "Jezero crater": (18.38, 77.58),
    "Hellas Planitia": (-42.4, 70.5),
}
ROADS = [("Erebus Montes", "Olympus Mons"), ("Erebus Montes", "Elysium Mons"), ("Erebus Montes", "Utopia Planitia"),
         ("Olympus Mons", "Ascraeus Mons"), ("Ascraeus Mons", "Valles Marineris"),          ("Elysium Mons", "Gale crater"), ("Utopia Planitia", "Elysium Mons"), ("Utopia Planitia", "Jezero crater"),
         ("Jezero crater", "Gale crater"), ("Jezero crater", "Hellas Planitia"), ("Gale crater", "Hellas Planitia"),
         ("Olympus Mons", "Gale crater")]


def east(lon):            # 0..360 east, with the picture centred near 180
    return lon % 360


def xy(name):
    lat, lon = PLACES[name]
    x = 110 + (east(lon) - 60) / (310 - 60) * (W - 220)
    y = 90 + (52 - lat) / 98 * 640
    return x, y


def dist(a, b):
    (la1, lo1), (la2, lo2) = PLACES[a], PLACES[b]
    p1, p2, dl = math.radians(la1), math.radians(la2), math.radians(lo2 - lo1)
    c = math.sin(p1) * math.sin(p2) + math.cos(p1) * math.cos(p2) * math.cos(dl)
    return R_MARS * math.acos(max(-1, min(1, c)))


def dijkstra(src, dst):
    g = {p: [] for p in PLACES}
    for a, b in ROADS:
        d = dist(a, b); g[a].append((b, d)); g[b].append((a, d))
    best, prev, pq = {src: 0}, {}, [(0, src)]
    while pq:
        d, u = heapq.heappop(pq)
        if d > best[u]:
            continue
        for v, w in g[u]:
            if d + w < best.get(v, math.inf):
                best[v] = d + w; prev[v] = u; heapq.heappush(pq, (d + w, v))
    path = [dst]
    while path[-1] != src:
        path.append(prev[path[-1]])
    return path[::-1], best[dst]


LABEL = {"Utopia Planitia": (0, -28, "middle"), "Erebus Montes": (26, -18, "start"), "Elysium Mons": (-26, -12, "end"),
         "Olympus Mons": (0, -28, "middle"), "Ascraeus Mons": (26, 8, "start"), "Jezero crater": (-26, 8, "end"),
         "Hellas Planitia": (26, 8, "start"), "Gale crater": (0, 48, "middle"), "Valles Marineris": (0, 48, "middle")}
path, total = dijkstra("Erebus Montes", "Gale crater")
on_path = {frozenset(e) for e in zip(path, path[1:])}
o = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">',
     '<defs><radialGradient id="sky" cx="50%" cy="35%" r="80%"><stop offset="0" stop-color="#3a1c12"/>'
     '<stop offset="0.6" stop-color="#1a0d09"/><stop offset="1" stop-color="#07080c"/></radialGradient>'
     '<linearGradient id="bar" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#eea66f"/>'
     '<stop offset="1" stop-color="#8a3f1f"/></linearGradient></defs>',
     f'<rect width="{W}" height="{H}" fill="url(#sky)"/>']
# faint latitude / longitude grid
for lat in range(-60, 61, 30):
    y = 90 + (52 - lat) / 98 * 640
    o.append(f'<line x1="0" y1="{y:.0f}" x2="{W}" y2="{y:.0f}" stroke="#f4e6d4" stroke-opacity="0.06"/>')
for lon in range(60, 311, 30):
    x = 110 + (lon - 60) / 250 * (W - 220)
    o.append(f'<line x1="{x:.0f}" y1="0" x2="{x:.0f}" y2="{H}" stroke="#f4e6d4" stroke-opacity="0.06"/>')
# roads
for a, b in ROADS:
    (x1, y1), (x2, y2) = xy(a), xy(b)
    hot = frozenset((a, b)) in on_path
    o.append(f'<line x1="{x1:.0f}" y1="{y1:.0f}" x2="{x2:.0f}" y2="{y2:.0f}" stroke="{"#eea66f" if hot else "#cdb096"}" '
             f'stroke-opacity="{1 if hot else 0.35}" stroke-width="{7 if hot else 3}" stroke-linecap="round"/>')
    mx, my = (x1 + x2) / 2, (y1 + y2) / 2
    o.append(f'<rect x="{mx - 34:.0f}" y="{my - 15:.0f}" width="68" height="28" rx="14" fill="#140b08" fill-opacity="0.9"/>')
    o.append(f'<text x="{mx:.0f}" y="{my + 7:.0f}" font-family="IBM Plex Mono, monospace" font-size="20" text-anchor="middle" '
             f'fill="{"#ffd2ad" if hot else "#cdb096"}" fill-opacity="{1 if hot else 0.6}">{dist(a, b):,.0f}</text>')
# places
for p in PLACES:
    x, y = xy(p)
    hot = p in path
    o.append(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{16 if hot else 12}" fill="{"#eea66f" if hot else "#1a100c"}" stroke="#f4e6d4" stroke-width="3"/>')
    dx, dy, anc = LABEL.get(p, (0, 44, "middle"))
    o.append(f'<text x="{x + dx:.0f}" y="{y + dy:.0f}" font-family="IBM Plex Sans, sans-serif" font-size="24" font-weight="600" '
             f'text-anchor="{anc}" fill="#f4e6d4">{p}</text>')
# sorting bars along the bottom
vals = [3, 9, 10, 27, 38, 43, 82]
for i, v in enumerate(vals):
    h = 18 + v * 1.4
    o.append(f'<rect x="{1180 + i * 50}" y="{860 - h:.0f}" width="38" height="{h:.0f}" rx="4" fill="url(#bar)" fill-opacity="0.85"/>')
# formulas
F = [(1010, 640, 26, "d[v] = min(d[v], d[u] + w(u, v))"), (1010, 682, 26, "T(n) = 2T(n/2) + O(n)"),
     (110, 815, 30, f"shortest route: {total:,.0f} km"), (110, 857, 26, "Dijkstra's algorithm, O((V + E) log V)")]
for x, y, fs, t in F:
    o.append(f'<text x="{x}" y="{y}" font-family="IBM Plex Mono, monospace" font-size="{fs}" fill="#f4e6d4" fill-opacity="0.85">{t}</text>')
o.append('</svg>')
out = pathlib.Path(__file__).resolve().parent.parent.parent / "docs" / "images" / "cs-hero.svg"
out.write_text("\n".join(o))
print("route:", " -> ".join(path), f"{total:,.0f} km")
