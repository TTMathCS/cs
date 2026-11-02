"""Animations for the Data structures pages (loaded by make_frames.py, which supplies anim, F and show)."""
import math

W = 560


def heap_layout(a, R=None):
    nodes, edges = [], []
    for i, v in enumerate(a):
        d = int(math.log2(i + 1)); k = i - (2 ** d - 1)
        nodes.append({"id": i, "x": round((k + 0.5) / 2 ** d * W), "y": 40 + d * 70, "label": v})
        if i:
            edges.append({"u": (i - 1) // 2, "v": i})
    return nodes, edges


@anim
def stack_queue():
    s = "a[b(c)d]e"; st = []; fr = [F([""], "Check the brackets of \"a[b(c)d]e\" with a stack")]
    pairs = {")": "(", "]": "[", "}": "{"}
    for ch in s:
        if ch in "([{":
            st.append(ch); fr.append(F(st, f"'{ch}' opens: push it", {len(st) - 1: "active"}))
        elif ch in pairs:
            top = st.pop(); fr.append(F(st + [top], f"'{ch}' closes: pop '{top}', which matches", {len(st): "done"}))
            fr.append(F(st if st else [""], "Stack after the pop" if st else "The stack is empty again"))
        else:
            fr.append(F(st if st else [""], f"'{ch}' is not a bracket: skip it"))
    fr.append(F([""], "End of text and the stack is empty: balanced"))
    q = []
    fr.append(F([""], "Now a queue: values join at the back and leave from the front"))
    for x in range(1, 5):
        q.append(x); fr.append(F(q, f"enqueue {x} at the back", {len(q) - 1: "active"}, ptr={"front": 0, "back": len(q) - 1}))
    for _ in range(2):
        fr.append(F(q, f"dequeue {q[0]} from the front: first in, first out", {0: "hot"}, ptr={"front": 0}))
        q.pop(0)
    fr.append(F(q, "Two left, in the order they arrived", ptr={"front": 0, "back": len(q) - 1}))
    return {"view": "array", "boxes": True, "title": "A stack checking brackets, then a queue", "frames": fr}


@anim
def hash_table():
    words = "the quick brown fox jumps over the lazy dog".split()
    m = 8; buckets = [[] for _ in range(m)]; fr = []

    def h(s):
        x = 0
        for ch in s: x = (31 * x + ord(ch)) & 0xFFFFFFFF
        return x

    def snap(note, hot=None):
        width = max(3, max(len(b) for b in buckets))
        cells = [[f"{k}:{v}" for k, v in b] + [None] * (width - len(b)) for b in buckets]
        cls = {f"{hot[0]},{hot[1]}": "hot"} if hot else {}
        fr.append({"cells": cells, "note": note, "cls": cls})
    snap("8 empty buckets. Each word goes to bucket hash(word) mod 8")
    for w in words:
        b = h(w) % m
        for i, (k, v) in enumerate(buckets[b]):
            if k == w:
                buckets[b][i] = (k, v + 1); snap(f"'{w}': hash mod 8 = {b}. Already there: count becomes {v+1}", (b, i)); break
        else:
            buckets[b].append((w, 1))
            snap(f"'{w}': hash {h(w)} mod 8 = {b}" + (" (a collision: the bucket's list grows)" if len(buckets[b]) > 1 else ""), (b, len(buckets[b]) - 1))
    return {"view": "grid", "title": "Counting words with a hash table (separate chaining)", "rows": [f"bucket {i}" for i in range(m)],
            "cols": ["1st", "2nd", "3rd"], "corner": "", "frames": fr}


@anim
def binary_heap():
    a = []; fr = []

    def snap(note, n=None, hl=None):
        nodes, edges = heap_layout(a)
        fr.append({"nodes": nodes, "edges": edges, "note": note, "n": {str(k): v for k, v in (n or {}).items()}, "info": ["array: " + show(a)]})
    for x in [5, 3, 8, 1, 9, 2]:
        a.append(x); i = len(a) - 1
        snap(f"push {x}: put it at the bottom", {i: "active"})
        while i and a[(i - 1) // 2] > a[i]:
            p = (i - 1) // 2; a[p], a[i] = a[i], a[p]
            snap(f"{a[p]} is smaller than its parent {a[i]}: swap up", {p: "hot", i: "hot"}); i = p
    snap(f"A min-heap: every parent is at most its children, so the smallest, {a[0]}, is on top", {0: "done"})
    top = a[0]; a[0] = a.pop()
    snap(f"pop: take {top} from the top, move the last value {a[0]} to the root", {0: "active"})
    i = 0
    while True:
        l, r, s = 2 * i + 1, 2 * i + 2, i
        if l < len(a) and a[l] < a[s]: s = l
        if r < len(a) and a[r] < a[s]: s = r
        if s == i: break
        a[i], a[s] = a[s], a[i]
        snap(f"{a[i]} is the smaller child: swap {a[s]} down", {i: "hot", s: "hot"}); i = s
    snap(f"Heap repaired: {a[0]} is the new smallest", {0: "done"})
    return {"view": "graph", "w": W, "h": 280, "nodes": [], "title": "A min-heap: push 5, 3, 8, 1, 9, 2, then pop", "frames": fr}


@anim
def bst():
    keys = [50, 30, 70, 20, 40, 60, 80, 35]; tree = {}; fr = []   # key -> (left, right)
    root = None

    def layout():
        order, pos = [], {}
        def ino(k, d):
            if k is None: return
            ino(tree[k][0], d + 1); order.append((k, d)); ino(tree[k][1], d + 1)
        ino(root, 0)
        n = len(order)
        nodes = [{"id": k, "x": round((i + 0.5) / max(n, 1) * W), "y": 36 + d * 62, "label": k} for i, (k, d) in enumerate(order)]
        edges = [{"u": k, "v": c} for k in tree for c in tree[k] if c is not None]
        return nodes, edges

    def snap(note, n):
        nodes, edges = layout()
        fr.append({"nodes": nodes, "edges": edges, "note": note, "n": {str(k): v for k, v in n.items()}})
    for k in keys:
        if root is None:
            root = k; tree[k] = [None, None]; snap(f"insert {k}: the tree is empty, it becomes the root", {k: "active"}); continue
        cur, path = root, []
        while True:
            path.append(cur); side = 0 if k < cur else 1
            if tree[cur][side] is None:
                tree[cur][side] = k; tree[k] = [None, None]; break
            cur = tree[cur][side]
        snap(f"insert {k}: " + ", ".join(f"{'<' if k < p else '>'} {p}" for p in path) + f", so it hangs {'left' if k < path[-1] else 'right'} of {path[-1]}",
             {**{p: "cmp" for p in path}, k: "active"})
    target, cur, path = 60, root, []
    while cur is not None:
        path.append(cur)
        if cur == target: break
        cur = tree[cur][0] if target < cur else tree[cur][1]
    snap(f"search 60: 60 > 50 go right, 60 < 70 go left, found in {len(path)} steps", {**{p: "cmp" for p in path[:-1]}, 60: "path"})
    return {"view": "graph", "w": W, "h": 260, "nodes": [], "title": "Building a binary search tree, then searching it", "frames": fr}


@anim
def union_find():
    n = 8; parent = list(range(n)); size = [1] * n; fr = []

    def layout():
        kids = {i: [j for j in range(n) if parent[j] == i and j != i] for i in range(n)}
        roots = [i for i in range(n) if parent[i] == i]
        nodes, x = [], [0]

        def width(r): return max(1, sum(width(c) for c in kids[r]))
        total = sum(width(r) for r in roots)

        def place(r, d, left):
            wd = width(r); nodes.append({"id": r, "x": round((left + wd / 2) / total * W), "y": 40 + d * 70})
            for c in kids[r]:
                place(c, d + 1, left); left += width(c)
        left = 0
        for r in roots:
            place(r, 0, left); left += width(r)
        edges = [{"u": j, "v": parent[j]} for j in range(n) if parent[j] != j]
        return nodes, edges

    def find(x, seen):
        while parent[x] != x: seen.append(x); x = parent[x]
        return x

    def snap(note, nc):
        nodes, edges = layout()
        fr.append({"nodes": nodes, "edges": edges, "note": note, "n": {str(k): v for k, v in nc.items()}})
    snap("8 items, each its own group: every item is its own leader", {})
    for a, b in [(0, 1), (2, 3), (4, 5), (1, 3), (6, 7), (5, 7), (3, 7), (0, 6)]:
        sa, sb = [], []
        ra, rb = find(a, sa), find(b, sb)
        if ra == rb:
            snap(f"union({a}, {b}): both lead to {ra}: already in the same group", {a: "cmp", b: "cmp", ra: "done"}); continue
        if size[ra] < size[rb]: ra, rb = rb, ra
        parent[rb] = ra; size[ra] += size[rb]
        for x in sa + sb:                       # path compression
            if x != ra: parent[x] = ra
        snap(f"union({a}, {b}): leaders {ra} and {rb}; hang the smaller group under {ra} (size {size[ra]})", {a: "cmp", b: "cmp", ra: "active", rb: "hot"})
    return {"view": "graph", "directed": True, "w": W, "h": 260, "nodes": [], "title": "Union-find: arrows point to the parent; a leader points nowhere", "frames": fr}


@anim
def fenwick_tree():
    a = [5, 2, 9, -3, 5, 20, 10, -7]; n = len(a); t = [0] * (n + 1); fr = []
    rows = ["a[i]", "covers", "t[i]"]

    def cover(i): return f"{i - (i & -i) + 1}..{i}"

    def snap(note, cls):
        fr.append({"cells": [a, [cover(i) for i in range(1, n + 1)], t[1:]], "note": note, "cls": cls})
    for i0, x in enumerate(a):
        i = i0 + 1; touched = []
        while i <= n:
            t[i] += x; touched.append(i); i += i & -i
        snap(f"add a[{i0}] = {x}: update t at " + ", ".join(map(str, touched)) + " (each time add the lowest set bit)",
             {**{f"2,{k-1}": "hot" for k in touched}, f"0,{i0}": "cmp"})
    i, parts, s = 7, [], 0
    while i > 0:
        parts.append(i); s += t[i]; i -= i & -i
    snap(f"prefix sum of the first 7 = " + " + ".join(f"t[{k}]" for k in parts) + f" = {s}: 7 = 111 in binary, so 3 pieces",
         {f"2,{k-1}": "path" for k in parts})
    return {"view": "grid", "title": "A Fenwick tree for [5, 2, 9, -3, 5, 20, 10, -7] (positions 1..8 inside)", "rows": rows,
            "cols": list(range(1, n + 1)), "corner": "i", "frames": fr}


@anim
def segment_tree():
    a = [5, 8, 6, 3, 2, 7, 2, 6]; n = len(a); t = {}; rng = {}
    def build(node, lo, hi):
        rng[node] = (lo, hi)
        if lo == hi: t[node] = a[lo]; return
        m = (lo + hi) // 2; build(2 * node, lo, m); build(2 * node + 1, m + 1, hi); t[node] = min(t[2 * node], t[2 * node + 1])
    build(1, 0, n - 1)
    nodes, edges = [], []
    for node, (lo, hi) in rng.items():
        d = int(math.log2(node)); nodes.append({"id": node, "x": round((lo + hi + 1) / 2 / n * W), "y": 34 + d * 66})
        if node > 1: edges.append({"u": node // 2, "v": node})
    fr = []

    def snap(note, nc):
        ns = [dict(nd, label=t[nd["id"]]) for nd in nodes]
        fr.append({"nodes": ns, "edges": edges, "note": note, "n": {str(k): v for k, v in nc.items()},
                   "nl": {str(k): f"{rng[k][0]}..{rng[k][1]}" if rng[k][0] != rng[k][1] else str(rng[k][0]) for k in rng}})
    snap("Each node stores the minimum of its range (the small label). The root covers 0..7", {})
    used, seen = [], []
    def q(node, l, r):
        lo, hi = rng[node]
        if r < lo or hi < l: return
        seen.append(node)
        if l <= lo and hi <= r: used.append(node); return
        q(2 * node, l, r); q(2 * node + 1, l, r)
    q(1, 1, 6)
    snap("min of a[1..6]: walk down from the root", {k: "cmp" for k in seen if k not in used})
    snap("Use whole nodes that fit inside 1..6: " + ", ".join(f"{rng[k][0]}..{rng[k][1]}" for k in used) + f": the minimum is {min(t[k] for k in used)}",
         {**{k: "cmp" for k in seen if k not in used}, **{k: "path" for k in used}})
    i, node = 4, 1
    a[4] = 9; build(1, 0, n - 1)
    path = []
    while True:
        path.append(node); lo, hi = rng[node]
        if lo == hi: break
        node = 2 * node if i <= (lo + hi) // 2 else 2 * node + 1
    snap("update a[4] = 9: change the leaf, then repair each node on the way back up", {k: "hot" for k in path})
    return {"view": "graph", "w": W, "h": 290, "r": 15, "nodes": [], "title": "A segment tree for range minimum over [5, 8, 6, 3, 2, 7, 2, 6]", "frames": fr}


@anim
def trie():
    words = ["mars", "map", "mare", "moon"]; ids = {"": 0}; edges = []; pos = {}; fr = []; children = {"": []}; ends = set()
    def layout():
        nodes = []; leafx = [0]
        def place(p, d):
            kids = children[p]
            if not kids:
                x = leafx[0]; leafx[0] += 1
            else:
                xs = [place(c, d + 1) for c in kids]; x = sum(xs) / len(xs)
            pos[p] = (x, d); return x
        place("", 0)
        total = max(leafx[0], 1)
        for p, (x, d) in pos.items():
            nodes.append({"id": ids[p], "x": round((x + 0.5) / total * W), "y": 30 + d * 52, "label": p[-1] if p else "*"})
        return nodes
    def snap(note, nc):
        nodes = layout()
        fr.append({"nodes": nodes, "edges": list(edges), "note": note, "n": {str(ids[p]): v for p, v in nc.items()}})
    snap("An empty trie: just the root", {"": "active"})
    for w in words:
        new = []
        for i in range(1, len(w) + 1):
            p = w[:i]
            if p not in ids:
                ids[p] = len(ids); children[p] = []; children[w[:i - 1]].append(p); edges.append({"u": ids[w[:i - 1]], "v": ids[p]}); new.append(p)
        ends.add(w)
        snap(f"insert '{w}': " + (f"shares '{w[:len(w) - len(new)]}', adds {len(new)} new node(s)" if len(new) < len(w) else "all new nodes"),
             {**{w[:i]: "cmp" for i in range(1, len(w) + 1)}, **{p: "active" for p in new}, **{e: "done" for e in ends if e != w}})
    snap("count words starting with 'ma': walk m, a; 3 words pass through that node", {"m": "cmp", "ma": "path", "mars": "done", "map": "done", "mare": "done", "moon": "done"})
    return {"view": "graph", "w": W, "h": 260, "r": 15, "nodes": [], "title": "A trie of mars, map, mare, moon (green: a word ends here)", "frames": fr}
