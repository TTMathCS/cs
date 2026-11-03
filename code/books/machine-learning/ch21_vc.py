"""Chapter 21: shattering and the growth function, by brute force.
Thresholds, intervals, half-planes and rectangles; Sauer's lemma checked;
and a one-parameter class, sign(sin(w x)), with infinite VC dimension."""
from itertools import product
from math import comb, pi

import numpy as np


def labelings_rays(xs):
    """h_t(x) = 1[x >= t] on 1-D points: every cut of the sorted points."""
    order = np.argsort(xs)
    out = set()
    for cut in range(len(xs) + 1):
        lab = np.zeros(len(xs), dtype=int)
        lab[order[cut:]] = 1
        out.add(tuple(lab))
    return out


def labelings_intervals(xs):
    """h_{a,b}(x) = 1[a <= x <= b]: a contiguous block of the sorted points, or nothing."""
    order = np.argsort(xs)
    n = len(xs)
    out = {tuple([0] * n)}
    for i in range(n):
        for j in range(i, n):
            lab = np.zeros(n, dtype=int)
            lab[order[i:j + 1]] = 1
            out.add(tuple(lab))
    return out


def labelings_halfplanes(pts):
    """h_{w,b}(x) = 1[w.x + b >= 0] in the plane, exactly, for points in general
    position: between two critical directions (where two projections tie) the
    order of the projections does not change, so one direction per arc is enough."""
    n = len(pts)
    crit = []
    for i in range(n):
        for j in range(i + 1, n):
            d = pts[j] - pts[i]
            a = np.arctan2(d[1], d[0]) + pi / 2
            crit += [a % (2 * pi), (a + pi) % (2 * pi)]
    if not crit:
        crit = [0.0, pi]
    crit = np.sort(np.array(crit))
    mids = (crit + np.roll(crit, -1)) / 2
    mids[-1] = (crit[-1] + crit[0] + 2 * pi) / 2
    out = set()
    for th in mids:
        proj = pts @ np.array([np.cos(th), np.sin(th)])
        order = np.argsort(proj)
        for cut in range(n + 1):
            lab = np.zeros(n, dtype=int)
            lab[order[cut:]] = 1
            out.add(tuple(lab))
    return out


def labelings_rectangles(pts):
    """Axis-aligned rectangles: a labeling is realised iff the bounding box of
    the positive points contains no negative point."""
    n = len(pts)
    out = set()
    for lab in product([0, 1], repeat=n):
        lab = np.array(lab)
        pos = pts[lab == 1]
        if len(pos) == 0:
            out.add(tuple(lab)); continue
        lo, hi = pos.min(axis=0), pos.max(axis=0)
        inside = np.all((pts >= lo) & (pts <= hi), axis=1)
        if not np.any(inside & (lab == 0)):
            out.add(tuple(lab))
    return out


def sauer(n, d):
    return sum(comb(n, i) for i in range(d + 1))


rng = np.random.default_rng(3)

print("1. can the class shatter these points?  (labelings realised / 2^n)")
print(f"   rays, 1 point:        {len(labelings_rays(np.array([0.4])))}/2")
print(f"   rays, 2 points:       {len(labelings_rays(np.array([0.2, 0.7])))}/4")
print(f"   intervals, 2 points:  {len(labelings_intervals(np.array([0.2, 0.7])))}/4")
print(f"   intervals, 3 points:  {len(labelings_intervals(np.array([0.2, 0.5, 0.7])))}/8"
      "   (1, 0, 1 is missing)")
tri = np.array([[0.0, 0.0], [1.0, 0.0], [0.3, 1.0]])
sq = np.array([[0.0, 0.0], [1.0, 0.0], [1.0, 1.0], [0.0, 1.0]])
print(f"   half-planes, triangle:  {len(labelings_halfplanes(tri))}/8")
print(f"   half-planes, square:    {len(labelings_halfplanes(sq + rng.normal(0, 1e-6, sq.shape)))}/16"
      "  (the two XOR labelings are missing)")
diamond = np.array([[0.0, 1.0], [1.0, 0.0], [0.0, -1.0], [-1.0, 0.0]])
print(f"   rectangles, diamond:    {len(labelings_rectangles(diamond))}/16")
best5 = max(len(labelings_rectangles(rng.random((5, 2)))) for _ in range(300))
print(f"   rectangles, 5 points:   at most {best5}/32 over 300 random sets")

print("\n2. growth function tau(n) against Sauer's bound and 2^n")
print("    n   intervals  Sauer d=2   half-planes  n^2-n+2  Sauer d=3     2^n")
for n in range(1, 11):
    xs = rng.random(n)
    pts = rng.random((n, 2))
    ti = len(labelings_intervals(xs))
    th = len(labelings_halfplanes(pts))
    print(f"  {n:3d}   {ti:9d}  {sauer(n, 2):9d}   {th:11d}  {n * n - n + 2:7d}  {sauer(n, 3):9d}  {2 ** n:6d}")

print("\n3. sign(sin(w x)) shatters x_i = 10^-i for every n (one parameter!)")
for n in range(1, 7):
    xs = 10.0 ** -np.arange(1, n + 1)
    ok = 0
    for lab in product([0, 1], repeat=n):
        w = pi * (1 + sum((1 - l) * 10 ** (i + 1) for i, l in enumerate(lab)))
        pred = (np.sin(w * xs) > 0).astype(int)
        ok += tuple(pred) == lab
    print(f"   n = {n}: {ok}/{2 ** n} labelings realised")
