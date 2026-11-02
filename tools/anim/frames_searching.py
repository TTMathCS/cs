"""Animations for the Searching pages (loaded by make_frames.py, which supplies anim, F and show)."""


@anim
def binary_search():
    a = [2, 5, 8, 12, 16, 23, 38, 56, 72, 91]; t = 23; fr = []
    lo, hi = 0, len(a) - 1
    fr.append(dict(F(a, f"Look for {t}. It can be anywhere in positions {lo}..{hi}", ptr={"lo": lo, "hi": hi}), **{}))
    while lo <= hi:
        mid = lo + (hi - lo) // 2
        out = [k for k in range(len(a)) if not lo <= k <= hi]
        fr.append(F(a, f"Middle of {lo}..{hi} is {mid}: compare a[{mid}] = {a[mid]} with {t}", {mid: "cmp"}, dim=out, ptr={"lo": lo, "mid": mid, "hi": hi}))
        if a[mid] == t:
            fr.append(F(a, f"Found {t} at position {mid}, after {len(fr) - 1} looks instead of up to 10", {mid: "path"}, dim=out)); break
        if a[mid] < t:
            lo = mid + 1; why = f"{a[mid]} < {t}: the target is to the right; throw away {mid} and everything left of it"
        else:
            hi = mid - 1; why = f"{a[mid]} > {t}: the target is to the left; throw away {mid} and everything right of it"
        fr.append(F(a, why, dim=[k for k in range(len(a)) if not lo <= k <= hi], ptr={"lo": lo, "hi": hi}))
    return {"view": "array", "boxes": True, "title": f"Binary search for {t} in a sorted list of 10", "frames": fr}


@anim
def ship_capacity():
    w = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]; d = 5; fr = []

    def plan(cap):
        days, load, groups = 1, 0, [[]]
        for x in w:
            if load + x > cap:
                days += 1; load = 0; groups.append([])
            load += x; groups[-1].append(x)
        return days, groups
    lo, hi = max(w), sum(w)
    fr.append(F(w, f"Packages to ship in order within {d} days. The capacity is somewhere in {lo}..{hi}",
                info=[f"lo = {lo} (the heaviest package must fit)", f"hi = {hi} (everything in one day)"]))
    while lo < hi:
        mid = (lo + hi) // 2
        days, groups = plan(mid)
        cls, k = {}, 0
        colors = ["cmp", "active", "path", "done", "hot"]
        for g, grp in enumerate(groups):
            for _ in grp:
                cls[k] = colors[g % len(colors)]; k += 1
        ok = days <= d
        if ok: hi = mid
        else: lo = mid + 1
        fr.append(F(w, f"Try capacity {mid}: needs {days} days, " + (f"which works, so the answer is at most {mid}" if ok else f"too many, so the answer is more than {mid}"),
                    cls, info=["days: " + " | ".join("+".join(map(str, g)) + f" = {sum(g)}" for g in groups), f"now lo = {lo}, hi = {hi}"]))
    days, groups = plan(lo)
    fr.append(F(w, f"lo = hi = {lo}: the smallest capacity that works", {i: "done" for i in range(len(w))},
                info=["days: " + " | ".join("+".join(map(str, g)) + f" = {sum(g)}" for g in groups)]))
    return {"view": "array", "boxes": True, "title": "Binary search on the answer: smallest ship capacity for 5 days", "frames": fr}


@anim
def two_pointers():
    a = [1, 2, 4, 7, 11, 15]; t = 15; i, j = 0, len(a) - 1; fr = [F(a, f"Find two values that add up to {t}. Start at both ends", ptr={"i": i, "j": j})]
    while i < j:
        s = a[i] + a[j]
        if s == t:
            fr.append(F(a, f"{a[i]} + {a[j]} = {t}: found it", {i: "path", j: "path"}, ptr={"i": i, "j": j})); break
        if s < t:
            fr.append(F(a, f"{a[i]} + {a[j]} = {s} < {t}: too small. a[i] cannot pair with anything, so move i right", {i: "cmp", j: "cmp"}, ptr={"i": i, "j": j}))
            i += 1
        else:
            fr.append(F(a, f"{a[i]} + {a[j]} = {s} > {t}: too big. a[j] cannot pair with anything, so move j left", {i: "cmp", j: "cmp"}, ptr={"i": i, "j": j}))
            j -= 1
    return {"view": "array", "boxes": True, "title": f"Two pointers: a pair with sum {t}", "frames": fr}


@anim
def sliding_window():
    s = "abcabcbb"; a = list(s); fr = []; last = {}; left = best = 0; best_at = (0, 0)
    fr.append(F(a, "Find the longest stretch with no repeated letter. The window grows to the right"))
    for right, ch in enumerate(s):
        note = f"Add '{ch}'"
        if ch in last and last[ch] >= left:
            note = f"'{ch}' is already in the window at {last[ch]}: move left to {last[ch] + 1}"
            left = last[ch] + 1
        last[ch] = right
        if right - left + 1 > best:
            best = right - left + 1; best_at = (left, right)
        fr.append(F(a, note + f". Window = \"{s[left:right+1]}\", length {right - left + 1}, best {best}",
                    {**{k: "active" for k in range(left, right + 1)}, right: "cmp"}, ptr={"L": left, "R": right}))
    fr.append(F(a, f"Longest: \"{s[best_at[0]:best_at[1]+1]}\", length {best}", {k: "path" for k in range(best_at[0], best_at[1] + 1)}))
    return {"view": "array", "boxes": True, "title": "Sliding window on \"abcabcbb\"", "frames": fr}
