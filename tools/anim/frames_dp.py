"""Animations for the Dynamic programming pages (loaded by make_frames.py, which supplies anim, F and show)."""


def GR(cells, note, cls=None, info=None):
    f = {"cells": [list(r) for r in cells], "note": note, "cls": cls or {}}
    if info: f["info"] = info
    return f


@anim
def fibonacci():
    n = 10; f = [None] * (n + 1); fr = []
    fr.append(F(f, f"Fill a table F[0..{n}] from the bottom up. Each value is worked out once"))
    f[0] = 0; fr.append(F(f, "F(0) = 0: a starting value", {0: "done"}))
    f[1] = 1; fr.append(F(f, "F(1) = 1: the other starting value", {1: "done"}, done=[0]))
    for i in range(2, n + 1):
        f[i] = f[i - 1] + f[i - 2]
        fr.append(F(f, f"F({i}) = F({i-1}) + F({i-2}) = {f[i-1]} + {f[i-2]} = {f[i]}", {i - 2: "cmp", i - 1: "cmp", i: "hot"}, done=range(i)))
    fr.append(F(f, f"Done: F({n}) = {f[n]} with {n - 1} additions. The plain recursion makes 177 calls for the same answer", done=range(n + 1)))
    return {"view": "array", "boxes": True, "title": "Fibonacci, bottom-up", "frames": fr}


@anim
def coin_change():
    coins = [1, 3, 4]; amount = 6; INF = "∞"
    best = [0] + [INF] * amount; last = [0] * (amount + 1); fr = []
    fr.append(F(best, f"Coins {show(coins)}, amount {amount}. best[x] = fewest coins for x; best[0] = 0", {0: "done"}))
    for x in range(1, amount + 1):
        for c in coins:
            if c > x:
                continue
            cand = best[x - c] + 1 if best[x - c] != INF else INF
            better = cand != INF and (best[x] == INF or cand < best[x])
            note = f"x = {x}, coin {c}: best[{x - c}] + 1 = {cand}" + (f" < {best[x]}: better" if better and best[x] != INF else (" (first way found)" if better else f", not better than {best[x]}"))
            if better:
                best[x] = cand; last[x] = c
            fr.append(F(best, note, {x - c: "cmp", x: "hot" if better else "active"}, done=range(x)))
    used, x = [], amount
    while x > 0:
        used.append(last[x]); x -= last[x]
    path, x = [], amount
    while x > 0:
        path.append(x); x -= last[x]
    fr.append(F(best, f"best[{amount}] = {best[amount]}: walk back through the last coins used: {' + '.join(map(str, used))} = {amount}. "
                      f"Greedy (largest coin first) would take 4 + 1 + 1, three coins", {p: "path" for p in path + [0]}))
    return {"view": "array", "boxes": True, "title": "Coin change: coins 1, 3, 4 for the amount 6", "frames": fr, "speed": 900}


@anim
def knapsack():
    W = [1, 3, 4, 5]; V = [1, 4, 5, 7]; cap = 7; n = len(W)
    best = [[0] * (cap + 1) for _ in range(n + 1)]
    cells = [[0] * (cap + 1)] + [[None] * (cap + 1) for _ in range(n)]
    fr = [GR(cells, "Row 0: with no items, every capacity is worth 0", {f"0,{c}": "done" for c in range(cap + 1)})]
    for i in range(1, n + 1):
        w, v = W[i - 1], V[i - 1]
        for c in range(cap + 1):
            best[i][c] = best[i - 1][c]
            cls = {f"{i-1},{c}": "cmp"}
            if w <= c and best[i - 1][c - w] + v > best[i][c]:
                best[i][c] = best[i - 1][c - w] + v
                cls = {f"{i-1},{c}": "dim", f"{i-1},{c-w}": "cmp"}
                note = f"Item {i-1} (w {w}, v {v}), capacity {c}: take it: {best[i-1][c-w]} + {v} = {best[i][c]} beats leaving it ({best[i-1][c]})"
            elif w <= c:
                cls[f"{i-1},{c-w}"] = "dim"
                note = f"Item {i-1} (w {w}, v {v}), capacity {c}: taking it gives {best[i-1][c-w]} + {v} = {best[i-1][c-w] + v}, no better than {best[i][c]}: leave it"
            else:
                note = f"Item {i-1} (w {w}), capacity {c}: too heavy, copy the value above ({best[i][c]})"
            cells[i][c] = best[i][c]; cls[f"{i},{c}"] = "hot"
            fr.append(GR(cells, note, cls))
    path, c = {}, cap
    for i in range(n, 0, -1):
        path[f"{i},{c}"] = "path"
        if best[i][c] != best[i - 1][c]:
            c -= W[i - 1]
    path[f"0,{c}"] = "path"
    fr.append(GR(cells, f"Best value {best[n][cap]}. Walking back up, the value changes at items 2 and 1: take them (weights 4 + 3, values 5 + 4)", path))
    return {"view": "grid", "title": "0/1 knapsack, capacity 7: items (weight, value) = (1, 1), (3, 4), (4, 5), (5, 7)",
            "rows": ["none"] + [f"item {i} ({W[i]}, {V[i]})" for i in range(n)], "cols": list(range(cap + 1)), "corner": "cap →",
            "frames": fr, "speed": 800}


@anim
def lcs():
    a, b = "ABCBDAB", "BDCABA"; n, m = len(a), len(b)
    L = [[0] * (m + 1) for _ in range(n + 1)]
    cells = [[0] * (m + 1)] + [[0] + [None] * m for _ in range(n)]
    fr = [GR(cells, "L[i][j] = the LCS length of the first i letters of a and the first j of b. Row 0 and column 0 are 0")]
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            if a[i - 1] == b[j - 1]:
                L[i][j] = L[i - 1][j - 1] + 1
                cls = {f"{i-1},{j-1}": "cmp", f"{i},{j}": "done"}
                note = f"{a[i-1]} = {b[j-1]}: a match, take the diagonal + 1 = {L[i][j]}"
            else:
                L[i][j] = max(L[i - 1][j], L[i][j - 1])
                cls = {f"{i-1},{j}": "cmp", f"{i},{j-1}": "cmp", f"{i},{j}": "hot"}
                note = f"{a[i-1]} ≠ {b[j-1]}: the larger of above ({L[i-1][j]}) and left ({L[i][j-1]}) = {L[i][j]}"
            cells[i][j] = L[i][j]
            fr.append(GR(cells, note, cls))
    path, out, i, j = {}, [], n, m
    while i > 0 and j > 0:
        if a[i - 1] == b[j - 1]:
            path[f"{i},{j}"] = "done"; out.append(a[i - 1]); i -= 1; j -= 1
        else:
            path[f"{i},{j}"] = "path"
            if L[i - 1][j] >= L[i][j - 1]: i -= 1
            else: j -= 1
    fr.append(GR(cells, f"Walk back from the corner; each green cell is a matched letter: {''.join(reversed(out))}", path))
    return {"view": "grid", "title": "Longest common subsequence of ABCBDAB and BDCABA",
            "rows": ["∅"] + list(a), "cols": ["∅"] + list(b), "corner": "", "frames": fr, "speed": 650}


@anim
def lis():
    from bisect import bisect_left
    a = [10, 9, 2, 5, 3, 7, 101, 18]; tails = []; tail_at = []; fr = []
    fr.append(F(a, "tails[k] = the smallest value that can end an increasing run of length k+1. Start with no tails",
                info=["tails = []"]))
    for i, x in enumerate(a):
        k = bisect_left(tails, x)
        if k == len(tails):
            tails.append(x); tail_at.append(i); what = f"{x} is bigger than every tail: append it, length {len(tails)}"
        else:
            old = tails[k]; tails[k] = x; tail_at[k] = i
            what = f"{x} replaces {old} at tails[{k}]: a run of length {k + 1} can now end lower, at {x}"
        fr.append(F(a, what, {j: "active" for j in tail_at} | {i: "hot"}, done=(), info=["tails = " + show(tails)]))
    fr.append(F(a, f"Longest increasing subsequence has length {len(tails)}, for example [2, 3, 7, 18] "
                   "(tails itself is not always a real subsequence)", {2: "path", 4: "path", 5: "path", 7: "path"}, info=["tails = " + show(tails)]))
    return {"view": "array", "title": "Longest increasing subsequence of " + show(a) + " in O(n log n)", "frames": fr}


@anim
def edit_distance():
    a, b = "kitten", "sitting"; n, m = len(a), len(b)
    D = [[0] * (m + 1) for _ in range(n + 1)]
    for i in range(n + 1): D[i][0] = i
    for j in range(m + 1): D[0][j] = j
    cells = [list(range(m + 1))] + [[i] + [None] * m for i in range(1, n + 1)]
    fr = [GR(cells, "D[i][j] = edits to turn the first i letters of kitten into the first j of sitting. Edges: all deletes or all inserts")]
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            same = a[i - 1] == b[j - 1]
            opts = [(D[i - 1][j - 1] + (0 if same else 1), "keep" if same else "replace", f"{i-1},{j-1}"),
                    (D[i - 1][j] + 1, "delete", f"{i-1},{j}"), (D[i][j - 1] + 1, "insert", f"{i},{j-1}")]
            v, how, src = min(opts, key=lambda t: t[0])
            D[i][j] = v; cells[i][j] = v
            note = (f"{a[i-1]} = {b[j-1]}: keep it, copy the diagonal: {v}" if how == "keep" else
                    f"{a[i-1]} vs {b[j-1]}: replace {D[i-1][j-1]}+1, delete {D[i-1][j]}+1, insert {D[i][j-1]}+1: best {v} ({how})")
            fr.append(GR(cells, note, {src: "cmp", f"{i},{j}": "done" if how == "keep" else "hot"}))
    path, i, j = {}, n, m
    while i > 0 or j > 0:
        path[f"{i},{j}"] = "path"
        if i > 0 and j > 0 and D[i][j] == D[i - 1][j - 1] + (a[i - 1] != b[j - 1]): i -= 1; j -= 1
        elif i > 0 and D[i][j] == D[i - 1][j] + 1: i -= 1
        else: j -= 1
    path["0,0"] = "path"
    fr.append(GR(cells, "Distance 3. The purple path is one cheapest way: replace k→s, keep itt, replace e→i, keep n, insert g", path))
    return {"view": "grid", "title": "Edit distance from kitten to sitting",
            "rows": ["∅"] + list(a), "cols": ["∅"] + list(b), "corner": "", "frames": fr, "speed": 650}
