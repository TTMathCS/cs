"""Animations for the Strings pages (loaded by make_frames.py, which supplies anim, F and show)."""


def GR(cells, note, cls=None, info=None):
    f = {"cells": [list(r) for r in cells], "note": note, "cls": cls or {}}
    if info: f["info"] = info
    return f


@anim
def kmp():
    t, p = "ABABDABACDABABCABAB", "ABABCABAB"; n, m = len(t), len(p)
    pi = [0] * m; k = 0
    for i in range(1, m):
        while k and p[i] != p[k]: k = pi[k - 1]
        if p[i] == p[k]: k += 1
        pi[i] = k
    fr = []

    def row(shift):
        r = [None] * n
        for j in range(m):
            if 0 <= shift + j < n: r[shift + j] = p[j]
        return r

    def frame(note, shift, k, i, state, kinfo=None):
        cls = {f"1,{shift + j}": "done" for j in range(k)}
        cls.update({f"0,{shift + j}": "done" for j in range(k)})
        if i is not None:
            cls[f"0,{i}"] = state; cls[f"1,{i}"] = state
        return GR([list(t), row(shift)], note, cls, ["pi = " + show(pi), f"matched so far: k = {k if kinfo is None else kinfo}"])
    fr.append(frame("The prefix table pi of the pattern is ready. Line the pattern up under the text", 0, 0, None, ""))
    k = 0
    for i, ch in enumerate(t):
        while k and ch != p[k]:
            shift = i - k
            fr.append(frame(f"text[{i}] = {ch} ≠ pattern[{k}] = {p[k]}: mismatch", shift, k, i, "hot"))
            nk = pi[k - 1]
            fr.append(frame(f"Do not go back in the text. pi[{k-1}] = {nk}: the last {nk} matched letters are already a start of the pattern, so slide it to keep them",
                            i - nk, nk, None, ""))
            k = nk
        shift = i - k
        if ch == p[k]:
            k += 1
            fr.append(frame(f"text[{i}] = {ch} = pattern[{k-1}]: match, k = {k}", shift, k - 1, i, "cmp", k))
        else:
            fr.append(frame(f"text[{i}] = {ch} ≠ pattern[0]: move on", shift, 0, i, "hot"))
        if k == m:
            s = i - m + 1
            fr.append(GR([list(t), row(s)], f"All {m} letters match: the pattern starts at position {s}",
                         {**{f"0,{s+j}": "path" for j in range(m)}, **{f"1,{s+j}": "path" for j in range(m)}}, ["pi = " + show(pi)]))
            k = pi[k - 1]
    return {"view": "grid", "title": "KMP: searching for ABABCABAB", "rows": ["text", "pattern"], "cols": list(range(n)),
            "corner": "", "frames": fr, "speed": 800}


@anim
def rabin_karp():
    t, p, mod, base = "stars on mars", "mars", 13, 256; n, m = len(t), len(p)
    high = pow(base, m - 1, mod); hp = ht = 0
    for i in range(m):
        hp = (hp * base + ord(p[i])) % mod; ht = (ht * base + ord(t[i])) % mod
    cells = [[c if c != " " else "␣" for c in t]]
    fr = [GR(cells, f"Hash of the pattern \"mars\" (mod {mod}) is {hp}. A small modulus is used here so false alarms show up",
             info=[f"hash(pattern) = {hp}"])]
    for s in range(n - m + 1):
        win = {f"0,{s+j}": "active" for j in range(m)}
        word = t[s:s + m]
        if ht == hp:
            if word == p:
                fr.append(GR(cells, f"Window {s} \"{word}\": hash {ht} = {hp}, and the letters match: found at {s}",
                             {f"0,{s+j}": "path" for j in range(m)}, [f"hash(window) = {ht}", f"hash(pattern) = {hp}"]))
            else:
                fr.append(GR(cells, f"Window {s} \"{word}\": hash {ht} = {hp}, but the letters differ: a false alarm",
                             {f"0,{s+j}": "hot" for j in range(m)}, [f"hash(window) = {ht}", f"hash(pattern) = {hp}"]))
        else:
            fr.append(GR(cells, f"Window {s} \"{word}\": hash {ht} ≠ {hp}, so it cannot match; no letters compared", win,
                         [f"hash(window) = {ht}", f"hash(pattern) = {hp}"]))
        if s + m < n:
            ht = ((ht - ord(t[s]) * high) * base + ord(t[s + m])) % mod
    fr.append(GR(cells, "Done: one real match and 3 false alarms. With a modulus near a billion, false alarms almost never happen",
                 {f"0,{9+j}": "path" for j in range(m)}))
    return {"view": "grid", "title": "Rabin-Karp: \"mars\" in \"stars on mars\", hashes mod 13", "rows": ["text"], "cols": list(range(n)),
            "corner": "", "frames": fr, "speed": 1000}


@anim
def z_algorithm():
    s = "aabxaabxaa"; n = len(s); z = [None] * n; z[0] = n
    fr = []

    def frame(note, i=None, l=0, r=0, cmp=()):
        cls = {}
        for j in range(l, r): cls[f"0,{j}"] = "active"
        for j in range(0, r - l if r > l else 0): cls.setdefault(f"0,{j}", "active dim")
        for a, b in cmp: cls[f"0,{a}"] = "cmp"; cls[f"0,{b}"] = "cmp"
        if i is not None: cls[f"1,{i}"] = "hot"
        return GR([list(s), list(z)], note, cls, [f"[l, r) = [{l}, {r})"])
    fr.append(frame(f"z[i] = how many letters starting at i match the start of the string. z[0] = {n} by convention"))
    l = r = 0; zz = [0] * n; zz[0] = n
    for i in range(1, n):
        if i < r:
            zz[i] = min(r - i, zz[i - l])
            fr.append(frame(f"i = {i} is inside the box [{l}, {r}), a copy of the start: reuse z[{i - l}] = {zz[i - l]}, capped at r − i = {r - i}: start at {zz[i]}", i, l, r))
        cmps = []
        while i + zz[i] < n and s[zz[i]] == s[i + zz[i]]:
            cmps.append((zz[i], i + zz[i])); zz[i] += 1
        z[i] = zz[i]
        if i + zz[i] > r:
            l, r = i, i + zz[i]
        stop = f"; stops at s[{i + zz[i]}] ≠ s[{zz[i]}]" if i + zz[i] < n else "; reached the end"
        fr.append(frame(f"z[{i}] = {zz[i]}" + (f": compared {len(cmps)} more letter(s)" if cmps else ": no new letters matched") + stop, i, l, r, cmps))
    fr.append(GR([list(s), list(z)], "Done. Every letter was matched at most once by a new comparison, so the work is O(n)", {}))
    return {"view": "grid", "title": "Z-algorithm on aabxaabxaa", "rows": ["s", "z"], "cols": list(range(n)), "corner": "", "frames": fr, "speed": 1100}
