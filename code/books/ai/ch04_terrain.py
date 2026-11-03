"""Chapter 4: path planning on a synthetic Mars-like terrain grid.

The terrain is made up (fixed random seed): gentle hills, three craters with
raised rims, and scattered rocks, on a 60 x 60 grid of 1 m cells. A move goes
to one of the 8 neighbouring cells; its cost is the distance (1 or sqrt 2)
times a slope penalty 1 + slope / (20 degrees); cells steeper than 20
degrees, and rocks, cannot be entered. Since every cost is at least the
distance, the octile distance (the shortest 8-connected distance on an empty
grid) is an admissible, consistent heuristic.
Python with NumPy.
"""
import heapq
import math

import numpy as np

N = 60
MAX_SLOPE = 20.0          # degrees
START, GOAL = (54, 3), (4, 56)


def make_terrain(seed=4):
    rng = np.random.default_rng(seed)
    y, x = np.mgrid[0:N, 0:N].astype(float)
    z = np.zeros((N, N))
    for _ in range(6):                           # broad hills, a few metres high
        cx, cy = rng.uniform(0, N, 2)
        s, a = rng.uniform(8, 16), rng.uniform(-2.5, 2.5)
        z += a * np.exp(-((x - cx) ** 2 + (y - cy) ** 2) / (2 * s * s))
    for cx, cy, r in [(30, 30, 9), (16, 40, 6), (44, 14, 7)]:   # craters
        d = np.hypot(x - cx, y - cy) / r
        z += np.where(d < 1, -3.0 * (1 - d ** 2), 0)            # bowl
        z += 2.0 * np.exp(-((d - 1) ** 2) / 0.02)               # raised rim
    gy, gx = np.gradient(z)                      # metres per metre
    slope = np.degrees(np.arctan(np.hypot(gx, gy)))
    rocks = rng.random((N, N)) < 0.04
    for p in (START, GOAL):                      # keep the ends clear
        rocks[p] = False
    return z, slope, rocks


def plan(slope, rocks, w=1.0, use_h=True, greedy=False):
    blocked = (slope > MAX_SLOPE) | rocks
    gr, gc = GOAL

    def h(r, c):
        if not use_h:
            return 0.0
        dr, dc = abs(r - gr), abs(c - gc)
        return (dr + dc) + (math.sqrt(2) - 2) * min(dr, dc)    # octile

    g = {START: 0.0}
    parent = {START: None}
    pq = [(h(*START), START)]
    closed = set()
    expanded = 0
    while pq:
        _, u = heapq.heappop(pq)
        if u in closed:
            continue
        if u == GOAL:
            break
        closed.add(u)
        expanded += 1
        r, c = u
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                v = (r + dr, c + dc)
                if (dr, dc) == (0, 0) or not (0 <= v[0] < N and 0 <= v[1] < N):
                    continue
                if blocked[v] or v in closed:
                    continue
                step = math.hypot(dr, dc) * (1 + slope[v] / MAX_SLOPE)
                nv = g[u] + step
                if nv < g.get(v, math.inf):
                    g[v], parent[v] = nv, u
                    key = h(*v) if greedy else nv + w * h(*v)
                    heapq.heappush(pq, (key, v))
    path, v = [], GOAL
    while v is not None:
        path.append(v)
        v = parent[v]
    return path[::-1], g[GOAL], expanded, closed


def main():
    z, slope, rocks = make_terrain()
    blocked = (slope > MAX_SLOPE) | rocks
    print(f"terrain {N} x {N}: height {z.min():.1f} to {z.max():.1f} m,"
          f" {np.mean(slope > MAX_SLOPE):.1%} too steep, {rocks.mean():.1%} rocks")
    gr, gc = GOAL
    dr, dc = abs(START[0] - gr), abs(START[1] - gc)
    print(f"start {START}, goal {GOAL}: straight-line {math.hypot(dr, dc):.1f} m,"
          f" octile h = {dr + dc + (math.sqrt(2) - 2) * min(dr, dc):.1f}")
    print(f"  {'planner':22} {'cost':>7} {'cells':>6} {'expanded':>9}")
    results = {}
    for name, kw in [("Dijkstra (h = 0)", dict(use_h=False)),
                     ("A* (octile)", dict()),
                     ("weighted A*, w = 2", dict(w=2.0)),
                     ("greedy best-first", dict(greedy=True))]:
        path, cost, exp, closed = plan(slope, rocks, **kw)
        results[name] = (path, closed)
        print(f"  {name:22} {cost:7.1f} {len(path):6d} {exp:9d}")

    path, closed = results["A* (octile)"]
    on_path = set(path)
    print("\nA* route (every second row; # blocked, o route, . expanded):")
    for r in range(0, N, 2):
        row = ""
        for c in range(N):
            p = (r, c)
            row += ("S" if p == START else "G" if p == GOAL else
                    "o" if p in on_path or (r + 1, c) in on_path else
                    "#" if blocked[p] else "." if p in closed else " ")
        print("  " + row)


if __name__ == "__main__":
    main()
