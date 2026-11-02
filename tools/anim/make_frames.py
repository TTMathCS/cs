#!/usr/bin/env python3
"""Writes docs/anim/<name>.json: the frames of every "Watch it step by step" animation.

Each animation runs the real algorithm on a small example and records a frame at every interesting moment, with a
sentence saying what happened. javascripts/anim.js draws the frames; nothing plays until the reader presses Play.
Run: python3 tools/anim/make_frames.py   (then mkdocs build --strict)
"""
import json, pathlib, sys

OUT = pathlib.Path(__file__).resolve().parent.parent.parent / "docs" / "anim"
ANIMS = {}


def anim(fn):
    ANIMS[fn.__name__.replace("_", "-")] = fn
    return fn


def F(a, note, cls=None, done=(), ptr=None, info=None, dim=()):
    f = {"a": list(a), "note": note}
    if cls: f["cls"] = {str(k): v for k, v in cls.items()}
    if done: f["done"] = sorted(set(done))
    if dim: f["dim"] = sorted(set(dim))
    if ptr: f["ptr"] = ptr
    if info: f["info"] = info
    return f


def show(a):
    return "[" + ", ".join(map(str, a)) + "]"


# ---------------------------------------------------------------- sorting
@anim
def bubble_sort():
    a = [5, 1, 4, 2, 8, 3]; n = len(a); fr = [F(a, "Start: " + show(a))]; done = []
    for end in range(n - 1, 0, -1):
        swapped = False
        for i in range(end):
            fr.append(F(a, f"Compare {a[i]} and {a[i+1]}", {i: "cmp", i + 1: "cmp"}, done))
            if a[i] > a[i + 1]:
                a[i], a[i + 1] = a[i + 1], a[i]; swapped = True
                fr.append(F(a, f"{a[i+1]} > {a[i]}: swap them", {i: "hot", i + 1: "hot"}, done))
        done.append(end)
        fr.append(F(a, f"Pass over: {a[end]} has bubbled to the end and is in its final place", done=done))
        if not swapped:
            done = list(range(n))
            fr.append(F(a, "No swaps in that pass, so the list is sorted: stop early", done=done)); break
    else:
        done = list(range(n)); fr.append(F(a, "Sorted: " + show(a), done=done))
    return {"view": "array", "title": "Bubble sort on " + show([5, 1, 4, 2, 8, 3]), "frames": fr}


@anim
def selection_sort():
    a = [29, 10, 14, 37, 13, 5]; n = len(a); fr = [F(a, "Start: " + show(a))]
    for i in range(n - 1):
        s = i
        fr.append(F(a, f"Look for the smallest value from position {i} on", {i: "active"}, range(i), {"i": i}))
        for j in range(i + 1, n):
            fr.append(F(a, f"Is {a[j]} smaller than the smallest so far, {a[s]}?", {s: "active", j: "cmp"}, range(i), {"i": i, "min": s}))
            if a[j] < a[s]:
                s = j
        a[i], a[s] = a[s], a[i]
        fr.append(F(a, f"Smallest is {a[i]}: swap it into position {i}", {i: "hot", s: "hot"} if s != i else {i: "hot"}, range(i)))
    fr.append(F(a, "Sorted: " + show(a), done=range(n)))
    return {"view": "array", "title": "Selection sort on " + show([29, 10, 14, 37, 13, 5]), "frames": fr}


@anim
def insertion_sort():
    a = [12, 11, 13, 5, 6, 9]; n = len(a); fr = [F(a, "Start: the first value alone is a sorted list", done=[0])]
    for i in range(1, n):
        key = a[i]; j = i - 1
        fr.append(F(a, f"Take {key} and insert it into the sorted part on its left", {i: "active"}, range(i), {"key": i}))
        while j >= 0 and a[j] > key:
            a[j + 1] = a[j]
            fr.append(F(a[:j + 1] + [a[j]] + a[j + 2:], f"{a[j]} > {key}: shift {a[j]} one place right", {j + 1: "hot", j: "cmp"}, range(i + 1)))
            j -= 1
        a[j + 1] = key
        fr.append(F(a, f"Drop {key} into position {j+1}: the first {i+1} values are sorted", {j + 1: "active"}, range(i + 1)))
    fr.append(F(a, "Sorted: " + show(a), done=range(n)))
    return {"view": "array", "title": "Insertion sort on " + show([12, 11, 13, 5, 6, 9]), "frames": fr}


@anim
def merge_sort():
    a = [38, 27, 43, 3, 9, 82, 10]; fr = [F(a, "Start: split in halves until every piece has one value")]

    def go(lo, hi):
        if hi - lo <= 1:
            return
        mid = (lo + hi) // 2
        fr.append(F(a, f"Split positions {lo}..{hi-1} into {lo}..{mid-1} and {mid}..{hi-1}",
                    {k: "active" for k in range(lo, hi)}, dim=[k for k in range(len(a)) if not lo <= k < hi]))
        go(lo, mid); go(mid, hi)
        left, right = a[lo:mid], a[mid:hi]; i = j = 0; k = lo
        while i < len(left) and j < len(right):
            if left[i] <= right[j]:
                a[k] = left[i]; i += 1
            else:
                a[k] = right[j]; j += 1
            k += 1
        while i < len(left): a[k] = left[i]; i += 1; k += 1
        while j < len(right): a[k] = right[j]; j += 1; k += 1
        fr.append(F(a, f"Merge {show(left)} and {show(right)} into {show(a[lo:hi])}",
                    {k: "done" for k in range(lo, hi)}, dim=[k for k in range(len(a)) if not lo <= k < hi]))
    go(0, len(a))
    fr.append(F(a, "Sorted: " + show(a), done=range(len(a))))
    return {"view": "array", "title": "Merge sort on " + show([38, 27, 43, 3, 9, 82, 10]), "frames": fr}


@anim
def quicksort():
    a = [10, 80, 30, 90, 40, 50, 70]; n = len(a); fr = [F(a, "Start: " + show(a))]; final = []

    def go(lo, hi):
        if lo > hi:
            return
        if lo == hi:
            final.append(lo); fr.append(F(a, f"{a[lo]} is alone, so it is in place", done=final)); return
        pivot = a[hi]; i = lo
        fr.append(F(a, f"Pivot is the last value, {pivot}", {hi: "active"}, final, {"i": i, "j": lo},
                    dim=[k for k in range(n) if not lo <= k <= hi and k not in final]))
        for j in range(lo, hi):
            if a[j] < pivot:
                a[i], a[j] = a[j], a[i]
                fr.append(F(a, f"{a[i]} < {pivot}: move it to the small side (position {i})", {hi: "active", i: "hot", j: "hot"}, final, {"i": i + 1, "j": j}))
                i += 1
            else:
                fr.append(F(a, f"{a[j]} >= {pivot}: leave it on the large side", {hi: "active", j: "cmp"}, final, {"i": i, "j": j}))
        a[i], a[hi] = a[hi], a[i]; final.append(i)
        fr.append(F(a, f"Swap the pivot into position {i}: smaller on its left, larger on its right", {i: "hot"}, final))
        go(lo, i - 1); go(i + 1, hi)
    go(0, n - 1)
    fr.append(F(a, "Sorted: " + show(a), done=range(n)))
    return {"view": "array", "title": "Quicksort (Lomuto partition) on " + show([10, 80, 30, 90, 40, 50, 70]), "frames": fr}


@anim
def heapsort():
    a = [4, 10, 3, 5, 1, 8]; n = len(a); fr = [F(a, "Start: read the list as a tree; position i has children 2i+1 and 2i+2")]

    def sift(i, size, done):
        while True:
            big, l, r = i, 2 * i + 1, 2 * i + 2
            if l < size and a[l] > a[big]: big = l
            if r < size and a[r] > a[big]: big = r
            kids = {k: "cmp" for k in (l, r) if k < size}
            if big == i:
                fr.append(F(a, f"{a[i]} is bigger than its children: it stays", {i: "active", **kids}, done)); return
            a[i], a[big] = a[big], a[i]
            fr.append(F(a, f"Swap {a[big]} down with its bigger child {a[i]}", {i: "hot", big: "hot"}, done))
            i = big
    for i in range(n // 2 - 1, -1, -1):
        fr.append(F(a, f"Build the heap: sift down position {i} ({a[i]})", {i: "active"}))
        sift(i, n, [])
    fr.append(F(a, f"Max-heap built: the largest value, {a[0]}, is at the top", {0: "active"}))
    done = []
    for end in range(n - 1, 0, -1):
        a[0], a[end] = a[end], a[0]; done.append(end)
        fr.append(F(a, f"Swap the top ({a[end]}) to position {end}, its final place", {0: "hot"}, done))
        sift(0, end, done)
    fr.append(F(a, "Sorted: " + show(a), done=range(n)))
    return {"view": "array", "title": "Heapsort on " + show([4, 10, 3, 5, 1, 8]), "frames": fr}


@anim
def counting_sort():
    a = [2, 5, 3, 0, 2, 3, 0, 3]; k = 5; fr = []
    cnt = [0] * (k + 1)
    rows = ["input", "count", "output"]

    def G(note, out, cls=None):
        cells = [a + [None] * 0, cnt + [None] * (len(a) - k - 1), out]
        return {"cells": cells, "note": note, "cls": cls or {}}
    out = [None] * len(a)
    fr.append(G("Values are 0 to 5, so make 6 counters", out))
    for i, x in enumerate(a):
        cnt[x] += 1
        fr.append(G(f"Count {x}: count[{x}] = {cnt[x]}", out, {f"0,{i}": "cmp", f"1,{x}": "hot"}))
    for v in range(1, k + 1):
        cnt[v] += cnt[v - 1]
        fr.append(G(f"Running total: count[{v}] = {cnt[v]} values are at most {v}", out, {f"1,{v}": "hot", f"1,{v-1}": "cmp"}))
    for i in range(len(a) - 1, -1, -1):
        x = a[i]; cnt[x] -= 1; out[cnt[x]] = x
        fr.append(G(f"From the back: {x} goes to output[{cnt[x]}]", list(out), {f"0,{i}": "cmp", f"1,{x}": "hot", f"2,{cnt[x]}": "done"}))
    fr.append(G("Sorted: " + show(out), out, {f"2,{j}": "done" for j in range(len(a))}))
    return {"view": "grid", "title": "Counting sort on " + show(a), "rows": rows, "cols": list(range(len(a))), "corner": "", "frames": fr}


@anim
def radix_sort():
    a = [170, 45, 75, 90, 802, 24, 2, 66]; fr = [F(a, "Start: sort by the ones digit, then tens, then hundreds", )]
    names = {1: "ones", 10: "tens", 100: "hundreds"}
    place = 1
    while max(a) // place > 0:
        fr.append(F(a, f"Look at the {names[place]} digit: " + ", ".join(str((x // place) % 10) for x in a), {i: "cmp" for i in range(len(a))}))
        a = sorted(a, key=lambda x: (x // place) % 10)   # Python's sort is stable, as each radix pass must be
        fr.append(F(a, f"Stable sort by the {names[place]} digit: " + show(a), {i: "active" for i in range(len(a))}))
        place *= 10
    fr.append(F(a, "Sorted: " + show(a), done=range(len(a))))
    return {"view": "array", "title": "Radix sort (base 10) on " + show([170, 45, 75, 90, 802, 24, 2, 66]), "frames": fr}


if __name__ == "__main__":
    import importlib.util
    here = pathlib.Path(__file__).resolve().parent
    for extra in sorted(here.glob("frames_*.py")):        # more animations, one file per topic
        spec = importlib.util.spec_from_file_location(extra.stem, extra)
        mod = importlib.util.module_from_spec(spec)
        mod.anim, mod.F, mod.show = anim, F, show
        sys.modules[extra.stem] = mod
        spec.loader.exec_module(mod)
    OUT.mkdir(parents=True, exist_ok=True)
    only = sys.argv[1:]
    for name, fn in ANIMS.items():
        if only and name not in only:
            continue
        data = fn()
        (OUT / f"{name}.json").write_text(json.dumps(data, separators=(",", ":")))
        print(f"{name}: {len(data['frames'])} frames")
