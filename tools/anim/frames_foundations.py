"""Animations for the Foundations pages (loaded by make_frames.py, which supplies anim, F and show)."""
import math


@anim
def growth():
    ns = [1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024]
    rows = ["log2 n", "n", "n log2 n", "n^2", "2^n"]
    fr = []
    cells = [[None] * len(ns) for _ in rows]
    for c, n in enumerate(ns):
        lg = int(math.log2(n))
        vals = [lg, n, n * lg, n * n, 2 ** n if n <= 64 else "huge"]
        for r, v in enumerate(vals):
            cells[r][c] = f"{v:,}" if isinstance(v, int) else v
        note = f"n = {n}: " + ("a list of one value" if n == 1 else f"2^n already has {len(str(2 ** n))} digits" if n >= 64 else "double n and see what each row does")
        if n == 1024:
            note = "n = 1024: log n is 10, n^2 is about a million, and 2^n has 309 digits: more than the atoms in the universe"
        fr.append({"cells": [row[:] for row in cells], "note": note, "cls": {f"{r},{c}": ("hot" if r >= 3 else "cmp") for r in range(5)}})
    return {"view": "grid", "title": "How step counts grow as n doubles", "rows": rows, "cols": ns, "corner": "n", "frames": fr}


@anim
def hanoi():
    pegs = {"A": [3, 2, 1], "B": [], "C": []}
    fr = []

    def snap(note, hot=None):
        cells = [[pegs[p][i] if i < len(pegs[p]) else None for i in range(3)] for p in "ABC"]
        cls = {}
        if hot:
            r = "ABC".index(hot); cls[f"{r},{len(pegs[hot]) - 1}"] = "hot"
        fr.append({"cells": cells, "note": note, "cls": cls})
    snap("Start: discs 3, 2, 1 on peg A (bottom to top). Goal: move them all to C")

    def go(n, s, t, sp, depth):
        if n == 0:
            return
        if n > 1:
            snap(f"{'  ' * depth}To move {n} discs {s}->{t}: first move the top {n-1} out of the way to {sp}")
        go(n - 1, s, sp, t, depth + 1)
        pegs[t].append(pegs[s].pop())
        snap(f"Move disc {n} from {s} to {t}", t)
        go(n - 1, sp, t, s, depth + 1)
    go(3, "A", "C", "B", 0)
    snap("Done: 7 moves, which is 2^3 - 1")
    return {"view": "grid", "title": "Tower of Hanoi with 3 discs", "rows": ["peg A", "peg B", "peg C"],
            "cols": ["bottom", "middle", "top"], "corner": "", "frames": fr}
