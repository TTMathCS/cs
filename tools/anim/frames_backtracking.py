"""Animations for the Backtracking pages (loaded by make_frames.py, which supplies anim, F and show)."""


@anim
def subsets():
    items = [1, 2, 3]; nodes = []; edges = []; order = []
    # build the decision tree: node = tuple of chosen items, by depth; left child = skip, right = take
    def build(path, chosen, depth):
        nid = len(nodes); nodes.append({"id": nid, "chosen": chosen, "depth": depth, "path": path})
        if depth < len(items):
            l = build(path + "0", chosen, depth + 1); edges.append({"u": nid, "v": l})
            r = build(path + "1", chosen + [items[depth]], depth + 1); edges.append({"u": nid, "v": r, "w": f"+{items[depth]}"})
        return nid
    build("", [], 0)
    leaves = [nd for nd in nodes if nd["depth"] == 3]
    xs = {nd["id"]: i for i, nd in enumerate(sorted(leaves, key=lambda d: d["path"]))}
    W, H = 600, 300

    def x_of(nd):
        lo = int(nd["path"].ljust(3, "0"), 2); hi = int(nd["path"].ljust(3, "1"), 2)
        return 40 + (lo + hi) / 2 * (W - 80) / 7
    spec_nodes = [{"id": nd["id"], "x": round(x_of(nd)), "y": 34 + nd["depth"] * 80,
                   "label": ",".join(map(str, nd["chosen"])) or "∅"} for nd in nodes]
    fr = []; seen = set(); out = []
    by_path = {nd["path"]: nd["id"] for nd in nodes}

    def eidx(u, v):
        for i, e in enumerate(edges):
            if e["u"] == u and e["v"] == v: return i

    def frame(note, cur, path_edges):
        n = {str(k): "done" for k in seen}
        for k in out: n[str(k)] = "path"
        n[str(cur)] = "hot"
        e = {str(eidx(a, b)): "hot" for a, b in path_edges}
        return {"note": note, "n": n, "e": e, "info": ["found so far: " + ", ".join("{" + ",".join(map(str, nodes[k]["chosen"])) + "}" for k in out)]}

    def go(path, stack):
        nid = by_path[path]; nd = nodes[nid]
        if nd["depth"] == 3:
            out.append(nid); seen.add(nid)
            fr.append(frame(f"All three items decided: record the subset {{{','.join(map(str, nd['chosen'])) or ' '}}}", nid, stack)); return
        fr.append(frame(f"Item {items[nd['depth']]}: first leave it out", nid, stack))
        seen.add(nid)
        go(path + "0", stack + [(nid, by_path[path + "0"])])
        fr.append(frame(f"Back at this choice: now take {items[nd['depth']]}", nid, stack))
        go(path + "1", stack + [(nid, by_path[path + "1"])])
    go("", [])
    fr.append({"note": "All 8 subsets found. Each leaf of the tree is one subset; the tree has 2³ leaves", "n": {str(k): "path" for k in out}})
    return {"view": "graph", "w": W, "h": H, "r": 22, "nodes": spec_nodes, "edges": edges, "title": "Every subset of {1, 2, 3}", "frames": fr, "speed": 900}


@anim
def n_queens():
    n = 4; place = []; fr = []

    def board(extra=None, cls_extra=None, note=""):
        cells = [["" for _ in range(n)] for _ in range(n)]
        cls = {}
        for r, c in enumerate(place):
            cells[r][c] = "♛"; cls[f"{r},{c}"] = "done"
            for rr in range(n):
                for cc in range(n):
                    if (rr, cc) != (r, c) and rr > r and (cc == c or abs(rr - r) == abs(cc - c)):
                        cls.setdefault(f"{rr},{cc}", "active dim")
        if extra:
            r, c, k = extra; cells[r][c] = "♛" if k != "hot" else "✕"; cls[f"{r},{c}"] = k
        if cls_extra: cls.update(cls_extra)
        return {"cells": cells, "cls": cls, "note": note, "info": ["queens' columns by row: " + show(place)]}

    fr.append(board(note="Put one queen in each row. Faded squares are attacked by queens already placed"))
    def safe(r, c):
        return all(c != pc and abs(r - pr) != abs(c - pc) for pr, pc in enumerate(place))
    def go(r):
        if r == n:
            fr.append(board(note=f"All {n} queens placed with no attacks: a solution " + show(place),
                            cls_extra={f"{rr},{cc}": "path" for rr, cc in enumerate(place)})); return True
        for c in range(n):
            if not safe(r, c):
                fr.append(board((r, c, "hot"), note=f"Row {r}, column {c}: attacked, skip")); continue
            place.append(c)
            fr.append(board(note=f"Row {r}, column {c}: safe, place a queen"))
            if go(r + 1): return True
            place.pop()
            fr.append(board(note=f"No square worked further down: take back the queen at row {r}, column {c} and try the next column"))
        fr.append(board(note=f"Row {r} has no safe column left: back up to row {r - 1}"))
        return False
    go(0)
    return {"view": "grid", "title": "Backtracking: 4 queens on a 4 × 4 board", "rows": list(range(n)), "cols": list(range(n)), "corner": "",
            "frames": fr, "speed": 1000}
