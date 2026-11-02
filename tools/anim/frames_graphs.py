"""Animations for the Graphs pages (loaded by make_frames.py, which supplies anim, F and show)."""
import heapq, math
from collections import deque

G8 = [(0, 1), (0, 2), (1, 3), (2, 3), (3, 4), (4, 5), (2, 5), (6, 7)]
P8 = {0: (60, 150), 1: (170, 60), 2: (170, 240), 3: (290, 150), 4: (400, 60), 5: (400, 240), 6: (500, 80), 7: (500, 220)}


def M(a, b):
    return {**a, **b}


def nodes_of(pos):
    return [{"id": k, "x": x, "y": y} for k, (x, y) in pos.items()]


def eidx(edges, u, v):
    for i, e in enumerate(edges):
        a, b = e[0], e[1]
        if (a, b) == (u, v) or (a, b) == (v, u):
            return i
    return None


def G(note, n=None, e=None, nl=None, info=None):
    f = {"note": note}
    if n: f["n"] = {str(k): v for k, v in n.items()}
    if e: f["e"] = {str(k): v for k, v in e.items()}
    if nl: f["nl"] = {str(k): v for k, v in nl.items()}
    if info: f["info"] = info
    return f


@anim
def bfs():
    adj = [[] for _ in range(8)]
    for u, v in G8: adj[u].append(v); adj[v].append(u)
    dist = [-1] * 8; dist[0] = 0; q = deque([0]); tree = {}; fr = []
    def state(cur=None):
        n = {v: ("done" if dist[v] != -1 and v not in q else "active") for v in range(8) if dist[v] != -1}
        if cur is not None: n[cur] = "cmp"
        return n
    fr.append(G("Start at 0: distance 0. Put it in the queue", state(), nl={0: 0}, info=["queue: [0]"]))
    while q:
        u = q.popleft()
        for v in adj[u]:
            if dist[v] == -1:
                dist[v] = dist[u] + 1; q.append(v); tree[eidx(G8, u, v)] = "path"
                fr.append(G(f"Take {u} from the queue; its neighbour {v} is new: distance {dist[v]}, join the queue",
                            state(u), M(tree, {eidx(G8, u, v): "hot"}), {k: dist[k] for k in range(8) if dist[k] != -1}, ["queue: " + show(list(q))]))
        fr.append(G(f"{u} is finished", state(), tree, {k: dist[k] for k in range(8) if dist[k] != -1}, ["queue: " + show(list(q))]))
    fr.append(G("Queue empty. Purple edges form the shortest-path tree; 6 and 7 cannot be reached", state(), tree, {k: dist[k] for k in range(8) if dist[k] != -1}))
    return {"view": "graph", "w": 560, "h": 290, "nodes": nodes_of(P8), "edges": [{"u": u, "v": v} for u, v in G8],
            "title": "Breadth-first search from 0 (numbers above: distance in edges)", "frames": fr}


@anim
def dfs():
    adj = [[] for _ in range(8)]
    for u, v in G8: adj[u].append(v); adj[v].append(u)
    seen, stack_path, fr, tree, order = set(), [], [], {}, []
    def n():
        d = {v: "done" for v in seen}
        for v in stack_path: d[v] = "active"
        if stack_path: d[stack_path[-1]] = "cmp"
        return d
    def visit(u, p):
        seen.add(u); stack_path.append(u); order.append(u)
        if p is not None: tree[eidx(G8, p, u)] = "path"
        fr.append(G(f"Visit {u}" + (f" from {p}" if p is not None else "") + ": go deeper", n(), dict(tree), info=["call stack: " + show(stack_path), "order: " + show(order)]))
        for v in adj[u]:
            if v not in seen:
                visit(v, u)
        stack_path.pop()
        fr.append(G(f"{u} has no unvisited neighbours left: back up" + (f" to {stack_path[-1]}" if stack_path else ""), n(), dict(tree), info=["call stack: " + show(stack_path), "order: " + show(order)]))
    visit(0, None)
    fr.append(G("Done with the component of 0. A new search would start at 6 for the second component", n(), dict(tree)))
    return {"view": "graph", "w": 560, "h": 290, "nodes": nodes_of(P8), "edges": [{"u": u, "v": v} for u, v in G8],
            "title": "Depth-first search from 0", "frames": fr}


@anim
def topological_sort():
    names = ["maths", "programming", "data struct.", "algorithms", "databases", "ML"]
    E = [(0, 3), (1, 2), (2, 3), (2, 4), (3, 5), (0, 5)]
    pos = {0: (70, 70), 1: (70, 220), 2: (230, 220), 3: (300, 80), 4: (420, 230), 5: (480, 90)}
    indeg = [0] * 6; adj = [[] for _ in range(6)]
    for u, v in E: adj[u].append(v); indeg[v] += 1
    q = deque(v for v in range(6) if indeg[v] == 0); order = []; fr = []; gone = {}
    fr.append(G("Count the arrows into each vertex. 0 and 1 have none: they can come first", {v: "active" for v in q}, nl=dict(enumerate(indeg))))
    while q:
        u = q.popleft(); order.append(u)
        for v in adj[u]:
            indeg[v] -= 1; gone[eidx(E, u, v)] = "dim"
            if indeg[v] == 0: q.append(v)
        nn = {v: "done" for v in order}; nn.update({v: "active" for v in q}); nn[u] = "path"
        fr.append(G(f"Take {names[u]}; remove its arrows. Now ready: " + (", ".join(names[v] for v in q) or "nothing"), nn, dict(gone),
                    {v: indeg[v] for v in range(6) if v not in order}, ["order: " + " > ".join(names[x] for x in order)]))
    return {"view": "graph", "directed": True, "w": 560, "h": 290, "r": 22, "nodes": [{"id": k, "x": x, "y": y, "label": names[k][:4]} for k, (x, y) in pos.items()],
            "edges": [{"u": u, "v": v} for u, v in E], "title": "Kahn's algorithm: an order for courses (numbers: arrows still coming in)", "frames": fr}


MARS = ["Erebus", "Olympus", "Ascraeus", "Valles", "Elysium", "Utopia", "Gale", "Jezero", "Hellas"]
LATLON = [(35.7, -175.0), (18.65, -133.8), (11.92, -104.08), (-13.9, -59.2), (25.02, 147.21), (47.97, 134.26),
          (-5.4, 137.8), (18.38, 77.58), (-42.4, 70.5)]
ROADS = [(0, 1, 2369), (0, 4, 2016), (0, 5, 2305), (1, 2, 1740), (2, 3, 3043), (4, 6, 1879), (5, 4, 1486),
         (5, 7, 3214), (7, 6, 3782), (7, 8, 3616), (6, 8, 4122), (1, 6, 5337)]


@anim
def dijkstra():
    pos = {}
    for i, (la, lo) in enumerate(LATLON):
        pos[i] = (round(40 + ((lo % 360) - 60) / 250 * 480), round(40 + (52 - la) / 98 * 230))
    adj = [[] for _ in range(9)]
    for u, v, w in ROADS: adj[u].append((v, w)); adj[v].append((u, w))
    INF = float("inf"); dist = [INF] * 9; dist[0] = 0; par = [-1] * 9; done = set(); pq = [(0, 0)]; fr = []
    def nl(): return {v: (f"{dist[v]:,}" if dist[v] < INF else "∞") for v in range(9)}
    def tree(): return {eidx(ROADS, v, par[v]): "path" for v in range(9) if par[v] != -1}
    fr.append(G("Start: Erebus Montes is 0 km away; every other place is ∞ for now", {0: "active"}, nl=nl()))
    while pq:
        d, u = heapq.heappop(pq)
        if d > dist[u]: continue
        done.add(u)
        changes = []
        for v, w in adj[u]:
            if v not in done and d + w < dist[v]:
                dist[v] = d + w; par[v] = u; heapq.heappush(pq, (dist[v], v)); changes.append(MARS[v])
        n = {v: "done" for v in done}; n.update({v: "active" for _, v in pq if v not in done}); n[u] = "cmp"
        fr.append(G(f"Settle {MARS[u]} at {dist[u]:,} km (the closest unsettled place). " +
                    (f"Shorter routes found to {', '.join(changes)}" if changes else "No improvements"),
                    n, M(tree(), {eidx(ROADS, u, v): "hot" for v, _ in adj[u] if MARS[v] in changes}), nl()))
    path, t = [], 6
    while t != -1: path.append(t); t = par[t]
    fr.append(G(f"All settled. Shortest route to Gale crater: {' > '.join(MARS[x] for x in reversed(path))}, {dist[6]:,} km",
                {v: "path" for v in path}, {eidx(ROADS, a, b): "path" for a, b in zip(path, path[1:])}, nl()))
    return {"view": "graph", "w": 560, "h": 310, "r": 16, "nodes": [{"id": k, "x": x, "y": y, "label": MARS[k][:3]} for k, (x, y) in pos.items()],
            "edges": [{"u": u, "v": v, "w": w} for u, v, w in ROADS], "title": "Dijkstra from Erebus Montes over real distances on Mars (km)", "frames": fr}


BF = [(0, 1, 6), (0, 2, 7), (1, 2, 8), (1, 3, 5), (1, 4, -4), (2, 3, -3), (2, 4, 9), (3, 1, -2), (4, 0, 2), (4, 3, 7)]


@anim
def bellman_ford():
    pos = {0: (60, 150), 1: (230, 50), 2: (230, 250), 3: (450, 50), 4: (450, 250)}
    edges = [{"u": u, "v": v, "w": w, "bend": (14 if (v, u) in [(a, b) for a, b, _ in BF] else 0)} for u, v, w in BF]
    INF = float("inf"); d = [INF] * 5; d[0] = 0; fr = []
    def nl(): return {v: ("∞" if d[v] == INF else d[v]) for v in range(5)}
    fr.append(G("Start: s = 0 has distance 0, everything else ∞. Each round relaxes all 10 edges", {0: "active"}, nl=nl()))
    for r in range(1, 5):
        changed = []
        for i, (u, v, w) in enumerate(BF):
            if d[u] != INF and d[u] + w < d[v]:
                d[v] = d[u] + w; changed.append(i)
        fr.append(G(f"Round {r}: " + (", ".join(f"d[{BF[i][1]}] = {d[BF[i][1]]} via {BF[i][0]}" for i in changed) if changed else "nothing changes, so we can stop"),
                    {BF[i][1]: "hot" for i in changed}, {i: "hot" for i in changed}, nl()))
        if not changed: break
    fr.append(G("Final distances. One more round would change nothing, so there is no negative cycle", {v: "done" for v in range(5)}, nl=nl()))
    return {"view": "graph", "directed": True, "w": 520, "h": 300, "nodes": nodes_of(pos), "edges": edges,
            "title": "Bellman-Ford from 0, with negative edges", "frames": fr}


@anim
def floyd_warshall():
    INF = float("inf")
    d = [[0, 3, INF, 7], [8, 0, 2, INF], [5, INF, 0, 1], [2, INF, INF, 0]]; n = 4; fr = []
    def cells(): return [["∞" if x == INF else x for x in row] for row in d]
    fr.append({"cells": cells(), "note": "Start: the direct edges only (∞ = no edge)"})
    for k in range(n):
        ch = {}
        for i in range(n):
            for j in range(n):
                if d[i][k] + d[k][j] < d[i][j]:
                    d[i][j] = d[i][k] + d[k][j]; ch[f"{i},{j}"] = "hot"
        cls = dict(ch)
        for t in range(n):
            cls.setdefault(f"{k},{t}", "cmp"); cls.setdefault(f"{t},{k}", "cmp")
        fr.append({"cells": cells(), "cls": cls, "note": f"k = {k}: allow paths through {k}. Row and column {k} (orange) combine; " +
                   (f"{len(ch)} entries improve (red)" if ch else "nothing improves")})
    fr.append({"cells": cells(), "note": "Done: every entry is a shortest distance", "cls": {f"{i},{j}": "done" for i in range(n) for j in range(n)}})
    return {"view": "grid", "title": "Floyd-Warshall on 4 vertices (row = from, column = to)", "rows": list(range(n)), "cols": list(range(n)), "corner": "", "frames": fr}


KE = [(0, 1, 4), (0, 7, 8), (1, 2, 8), (1, 7, 11), (2, 3, 7), (2, 8, 2), (2, 5, 4), (3, 4, 9),
      (3, 5, 14), (4, 5, 10), (5, 6, 2), (6, 7, 1), (6, 8, 6), (7, 8, 7)]
KP = {0: (40, 150), 1: (140, 50), 2: (270, 50), 3: (400, 50), 4: (510, 150), 5: (400, 250), 6: (270, 250), 7: (140, 250), 8: (205, 150)}


@anim
def kruskal():
    parent = list(range(9)); fr = []; chosen = {}; total = 0
    def find(x):
        while parent[x] != x: x = parent[x]
        return x
    fr.append(G("Sort the 14 edges by weight; take them cheapest first"))
    for w, u, v in sorted((w, u, v) for u, v, w in KE):
        i = eidx(KE, u, v)
        ru, rv = find(u), find(v)
        if ru != rv:
            parent[ru] = rv; chosen[i] = "path"; total += w
            fr.append(G(f"Edge {u}-{v} ({w}) joins two separate trees: keep it. Total {total}", {u: "cmp", v: "cmp"}, dict(chosen)))
            if len(chosen) == 8: break
        else:
            fr.append(G(f"Edge {u}-{v} ({w}) would close a cycle: skip it", {u: "hot", v: "hot"}, M(chosen, {i: "hot"})))
    fr.append(G(f"8 edges for 9 vertices: a minimum spanning tree of weight {total}", {v: "done" for v in range(9)}, dict(chosen)))
    return {"view": "graph", "w": 560, "h": 300, "nodes": nodes_of(KP), "edges": [{"u": u, "v": v, "w": w} for u, v, w in KE],
            "title": "Kruskal's algorithm", "frames": fr}


@anim
def prim():
    adj = [[] for _ in range(9)]
    for u, v, w in KE: adj[u].append((w, v)); adj[v].append((w, u))
    intree = set(); pq = [(0, 0, -1)]; fr = []; chosen = {}; total = 0
    fr.append(G("Grow one tree from 0. Always add the cheapest edge leaving the tree", {0: "active"}))
    while pq:
        w, v, frm = heapq.heappop(pq)
        if v in intree: continue
        intree.add(v); total += w
        if frm != -1: chosen[eidx(KE, frm, v)] = "path"
        for w2, x in adj[v]:
            if x not in intree: heapq.heappush(pq, (w2, x, v))
        border = {eidx(KE, f, x): "active" for _, x, f in pq if x not in intree and f != -1}
        fr.append(G((f"Cheapest edge leaving the tree: {frm}-{v} ({w}). Add {v}. Total {total}" if frm != -1 else "Take 0"),
                    {**{x: "done" for x in intree}, v: "cmp"}, M(border, chosen)))
    fr.append(G(f"Every vertex is in the tree: weight {total}, the same as Kruskal's", {v: "done" for v in range(9)}, dict(chosen)))
    return {"view": "graph", "w": 560, "h": 300, "nodes": nodes_of(KP), "edges": [{"u": u, "v": v, "w": w} for u, v, w in KE],
            "title": "Prim's algorithm (blue: edges leaving the tree, waiting in the heap)", "frames": fr}


@anim
def scc():
    E = [(0, 1), (1, 2), (2, 0), (2, 3), (3, 4), (4, 5), (5, 3), (6, 5), (6, 7), (7, 6)]
    pos = {0: (60, 80), 1: (170, 40), 2: (150, 200), 3: (290, 140), 4: (400, 50), 5: (430, 230), 6: (520, 150), 7: (540, 280)}
    pos = {k: (x, min(y, 260)) for k, (x, y) in pos.items()}
    n = 8; adj = [[] for _ in range(n)]; radj = [[] for _ in range(n)]
    for u, v in E: adj[u].append(v); radj[v].append(u)
    seen = [False] * n; order = []; fr = []
    def dfs1(u):
        seen[u] = True
        for v in adj[u]:
            if not seen[v]: dfs1(v)
        order.append(u)
        fr.append(G(f"Pass 1: {u} finishes", {**{x: "done" for x in order}, u: "cmp"}, info=["finish order: " + show(order)]))
    fr.append(G("Pass 1: depth-first search on the graph, writing down when each vertex finishes"))
    for u in range(n):
        if not seen[u]: dfs1(u)
    comp = [-1] * n; colours = ["path", "active", "cmp"]
    def dfs2(u, c):
        comp[u] = c
        for v in radj[u]:
            if comp[v] == -1: dfs2(v, c)
    c = 0
    for u in reversed(order):
        if comp[u] == -1:
            dfs2(u, c)
            grp = [v for v in range(n) if comp[v] == c]
            fr.append(G(f"Pass 2, arrows reversed, starting from the latest finisher still free ({u}): reaches {show(grp)}, one component",
                        {v: colours[comp[v]] for v in range(n) if comp[v] != -1},
                        {i: colours[comp[a]] for i, (a, b) in enumerate(E) if comp[a] != -1 and comp[a] == comp[b]}))
            c += 1
    return {"view": "graph", "directed": True, "w": 580, "h": 290, "nodes": nodes_of(pos), "edges": [{"u": u, "v": v, "bend": 12 if (v, u) in E else 0} for u, v in E],
            "title": "Kosaraju's algorithm: strongly connected components", "frames": fr}
