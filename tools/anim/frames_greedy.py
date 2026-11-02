"""Animations for the Greedy pages (loaded by make_frames.py, which supplies anim, F and show)."""
import heapq


@anim
def activity_selection():
    s = [1, 3, 0, 5, 3, 5, 6, 7, 8, 2, 12]
    f = [4, 5, 6, 7, 9, 9, 10, 11, 12, 14, 16]
    order = sorted(range(len(s)), key=lambda i: (f[i], i)); T = 16
    rows = [f"#{i} [{s[i]}, {f[i]})" for i in order]
    base = [["" for _ in range(T)] for _ in order]
    state = {}

    def frame(note, hi=None):
        cls = {}
        for r, i in enumerate(order):
            c = state.get(i, "")
            if i == hi: c = "cmp"
            for t in range(s[i], f[i]):
                cls[f"{r},{t}"] = c or "active"
        return {"cells": base, "note": note, "cls": cls}
    fr = [frame("Activities sorted by finishing time; each bar is the time it uses the room")]
    free = -1
    for i in order:
        fr.append(frame(f"#{i} runs {s[i]} to {f[i]}. The room is free from {max(free, 0)}", i))
        if s[i] >= free:
            state[i] = "done"; free = f[i]
            fr.append(frame(f"It starts in time: take it. The room is now busy until {f[i]}"))
        else:
            state[i] = "active dim"
            fr.append(frame(f"It starts at {s[i]}, before the room is free: skip it"))
    chosen = [i for i in order if state[i] == "done"]
    fr.append(frame(f"Chosen: {', '.join('#' + str(i) for i in chosen)}: {len(chosen)} activities, the most possible"))
    return {"view": "grid", "title": "Activity selection: earliest finish first", "rows": rows, "cols": list(range(T)),
            "corner": "time →", "frames": fr, "speed": 900}


@anim
def huffman():
    freq = [("a", 45), ("b", 13), ("c", 12), ("d", 16), ("e", 9), ("f", 5)]
    n = len(freq); heap = [(c, i) for i, (_, c) in enumerate(freq)]; heapq.heapify(heap)
    cnt = {i: c for i, (_, c) in enumerate(freq)}; left, right = {}, {}; merges = []
    nid = n
    while len(heap) > 1:
        c1, a = heapq.heappop(heap); c2, b = heapq.heappop(heap)
        left[nid], right[nid] = a, b; cnt[nid] = c1 + c2; merges.append((a, b, nid))
        heapq.heappush(heap, (c1 + c2, nid)); nid += 1
    root = nid - 1
    pos, depth, xs = {}, {}, [0]

    def lay(v, d):
        depth[v] = d
        if v < n:
            pos[v] = xs[0]; xs[0] += 1
        else:
            lay(left[v], d + 1); lay(right[v], d + 1); pos[v] = (pos[left[v]] + pos[right[v]]) / 2
    lay(root, 0)
    W, H = 560, 322
    nodes_all = {v: {"id": v, "x": round(40 + pos[v] * (W - 80) / (n - 1)), "y": 34 + depth[v] * 62,
                     "label": (f"{freq[v][0]}:{cnt[v]}" if v < n else str(cnt[v]))} for v in cnt}
    edges_all = []
    for v in left:
        edges_all.append({"u": v, "v": left[v], "w": 0}); edges_all.append({"u": v, "v": right[v], "w": 1})
    fr = []
    alive = set(range(n)); made = set(range(n))

    def frame(note, ncls=None, ecls=None, info=None):
        nodes = [nodes_all[v] for v in sorted(made)]
        edges = [e for e in edges_all if e["u"] in made]
        f = {"nodes": nodes, "edges": edges, "note": note}
        if ncls: f["n"] = {str(k): v for k, v in ncls.items()}
        if ecls:
            f["e"] = {str(i): c for i, e in enumerate(edges) for (u, w), c in ecls.items() if (e["u"], e["v"]) == (u, w)}
        f["info"] = info or ["waiting in the heap: " + ", ".join(nodes_all[v]["label"] for v in sorted(alive, key=lambda v: (cnt[v], v)))]
        return f
    fr.append(frame("Each letter starts as its own one-node tree, weighted by how often it appears"))
    for a, b, v in merges:
        fr.append(frame(f"The two lightest trees: {nodes_all[a]['label']} and {nodes_all[b]['label']}", {a: "cmp", b: "cmp"}))
        made.add(v); alive -= {a, b}; alive.add(v)
        fr.append(frame(f"Join them under a new node of weight {cnt[a]} + {cnt[b]} = {cnt[v]} (left edge 0, right edge 1)",
                        {v: "hot", a: "active", b: "active"}, {(v, a): "hot", (v, b): "hot"}))
    codes = {}

    def walk(v, p):
        if v < n: codes[freq[v][0]] = p
        else: walk(left[v], p + "0"); walk(right[v], p + "1")
    walk(root, "")
    fr.append(frame("Done. A letter's code is the 0s and 1s on the path from the top: " + ", ".join(f"{k} = {codes[k]}" for k, _ in freq),
                    {v: "done" for v in range(n)}, info=["total: 224 bits, against 300 with a fixed 3-bit code"]))
    return {"view": "graph", "w": W, "h": H, "r": 22, "nodes": list(nodes_all.values()), "title": "Building a Huffman tree", "frames": fr}
