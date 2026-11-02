"""Animations for the Number theory pages (loaded by make_frames.py, which supplies anim, F and show)."""


def GR(cells, note, cls=None, info=None, rows=None):
    f = {"cells": [list(r) for r in cells], "note": note, "cls": cls or {}}
    if info: f["info"] = info
    if rows: f["rows"] = rows
    return f


@anim
def gcd():
    a, b = 1071, 462; cells = []; rows = []; fr = []
    fr.append(GR([[a, b, None, None]], f"Find gcd({a}, {b}). Each step: divide a by b and keep the remainder", rows=["1"]))
    k = 1
    while b:
        q, r = divmod(a, b)
        cells.append([a, b, q, r]); rows.append(str(k))
        fr.append(GR(cells, f"{a} = {q} × {b} + {r}: any common divisor of {a} and {b} also divides {r}",
                     {f"{k-1},3": "hot", f"{k-1},1": "cmp"}, rows=list(rows)))
        a, b = b, r; k += 1
        if b:
            fr.append(GR(cells + [[a, b, None, None]], f"Now gcd({a}, {b}): the old b and the remainder", {f"{k-1},0": "cmp", f"{k-1},1": "hot"}, rows=rows + [str(k)]))
    fr.append(GR(cells, f"The remainder is 0, so the last divisor, {a}, is the gcd. {len(cells)} divisions", {f"{len(cells)-1},1": "path"}, rows=rows))
    return {"view": "grid", "title": "Euclid's algorithm on 1071 and 462", "cols": ["a", "b", "a ÷ b", "a mod b"], "rows": ["1"], "corner": "step", "frames": fr}


@anim
def sieve():
    n = 50; R, C = 5, 10
    is_p = [True] * (n + 1); is_p[0] = is_p[1] = False
    def cells(): return [[r * C + c + 1 for c in range(C)] for r in range(R)]
    def pos(k): return f"{(k - 1) // C},{(k - 1) % C}"
    def base_cls():
        cls = {pos(1): "dim"}
        for k in range(2, n + 1):
            if not is_p[k]: cls[pos(k)] = "dim"
        return cls
    fr = [GR(cells(), "The numbers 1 to 50. 1 is not prime; start with 2", base_cls())]
    p = 2
    while p * p <= n:
        if is_p[p]:
            mult = list(range(p * p, n + 1, p))
            cls = base_cls(); cls[pos(p)] = "done"
            for k in mult: cls[pos(k)] = "hot"
            fr.append(GR(cells(), f"{p} is prime. Cross out its multiples from {p}×{p} = {p*p}: " + ", ".join(map(str, mult[:8])) + (" ..." if len(mult) > 8 else ""), cls))
            for k in mult: is_p[k] = False
            done = {pos(q): "done" for q in range(2, p + 1) if is_p[q]}
            fr.append(GR(cells(), f"Multiples of {p} are gone. The next number not crossed out is the next prime", {**base_cls(), **done}))
        p += 1
    cls = base_cls(); cls.update({pos(k): "done" for k in range(2, n + 1) if is_p[k]})
    fr.append(GR(cells(), "The next prime is 11, and 11×11 = 121 > 50, so stop: everything left is prime. 15 primes up to 50", cls))
    return {"view": "grid", "title": "Sieve of Eratosthenes up to 50", "frames": fr, "speed": 1400}


@anim
def fast_power():
    a, n = 3, 13; bits = []; m = n
    while m: bits.append(m & 1); m >>= 1
    L = len(bits); sq = [None] * L; res = [None] * L
    fr = [GR([bits, sq, res], f"{n} in binary is {bin(n)[2:]} (read right to left here: bit 0 first). So 3^13 = 3^8 · 3^4 · 3^1")]
    cur, result = a, 1
    for i in range(L):
        sq[i] = f"3^{2**i} = {cur}"
        if bits[i]:
            result *= cur; res[i] = result
            fr.append(GR([bits, sq, res], f"Bit {i} is 1: multiply the result by 3^{2**i} = {cur}, giving {result}", {f"0,{i}": "cmp", f"1,{i}": "hot", f"2,{i}": "done"}))
        else:
            res[i] = result
            fr.append(GR([bits, sq, res], f"Bit {i} is 0: skip 3^{2**i}; the result stays {result}", {f"0,{i}": "cmp", f"1,{i}": "dim"}))
        cur *= cur
    fr.append(GR([bits, sq, res], f"3^13 = {result} with {L - 1} squarings and {sum(bits)} multiplications (the first one by 1), instead of 12 multiplications",
                 {f"2,{L-1}": "path"}))
    return {"view": "grid", "title": "Square and multiply: 3 to the power 13", "rows": ["bit of 13", "square", "result"],
            "cols": [f"bit {i}" for i in range(L)], "corner": "", "frames": fr, "speed": 1500}
