"""Chapter 17: spanning trees, flows and matching, built from scratch.

Kruskal (with union-find), Prim (with a heap) and Boruvka on one graph;
Ford-Fulkerson, Edmonds-Karp and Dinic on one network, with its minimum cut;
a bad case for Ford-Fulkerson; bipartite matching by flow and by Hopcroft-Karp;
Hall's condition; the Hungarian algorithm; min-cost flow; Gale-Shapley.
Standard library only.
"""
import heapq
import itertools
from collections import deque

INF = float("inf")


# ------------------------------------------------------------ union-find
class DSU:
    def __init__(self, items):
        self.parent = {x: x for x in items}
        self.size = {x: 1 for x in items}

    def find(self, x):
        while self.parent[x] != x:
            self.parent[x] = self.parent[self.parent[x]]   # path halving
            x = self.parent[x]
        return x

    def union(self, a, b):
        a, b = self.find(a), self.find(b)
        if a == b:
            return False
        if self.size[a] < self.size[b]:
            a, b = b, a
        self.parent[b] = a
        self.size[a] += self.size[b]
        return True


# ------------------------------------------------------------------ MSTs
def kruskal(vertices, edges, trace=False):
    dsu, tree = DSU(vertices), []
    for w, u, v in sorted(edges):
        ok = dsu.union(u, v)
        if ok:
            tree.append((u, v, w))
        if trace:
            print(f"  {u}-{v} {w}: {'take' if ok else 'skip (would make a cycle)'}")
    return tree


def prim(vertices, edges, root, trace=False):
    adj = {v: [] for v in vertices}
    for w, u, v in edges:
        adj[u].append((w, v))
        adj[v].append((w, u))
    in_tree, tree = {root}, []
    pq = [(w, root, v) for w, v in adj[root]]
    heapq.heapify(pq)
    while pq and len(in_tree) < len(vertices):
        w, u, v = heapq.heappop(pq)
        if v in in_tree:
            continue                       # stale: both ends already in the tree
        in_tree.add(v)
        tree.append((u, v, w))
        if trace:
            print(f"  add {u}-{v} {w}")
        for w2, x in adj[v]:
            if x not in in_tree:
                heapq.heappush(pq, (w2, v, x))
    return tree


def boruvka(vertices, edges, trace=False):
    dsu, tree = DSU(vertices), []
    rnd = 0
    while len(tree) < len(vertices) - 1:
        rnd += 1
        cheapest = {}
        for w, u, v in edges:
            a, b = dsu.find(u), dsu.find(v)
            if a == b:
                continue
            for c in (a, b):              # ties broken by (w, u, v), so no cycles form
                if c not in cheapest or (w, u, v) < cheapest[c]:
                    cheapest[c] = (w, u, v)
        added = []
        for w, u, v in sorted(set(cheapest.values())):
            if dsu.union(u, v):
                tree.append((u, v, w))
                added.append(f"{u}-{v} {w}")
        if trace:
            print(f"  round {rnd}: add {', '.join(added)}")
    return tree


# ------------------------------------------------------------- max flow
class Network:
    """Residual network stored as edge lists; edge i and i^1 are partners."""

    def __init__(self, n):
        self.n, self.head = n, [[] for _ in range(n)]
        self.to, self.cap = [], []

    def add(self, u, v, c):
        self.head[u].append(len(self.to)); self.to.append(v); self.cap.append(c)
        self.head[v].append(len(self.to)); self.to.append(u); self.cap.append(0)

    def copy(self):
        g = Network(self.n)
        g.head = [h[:] for h in self.head]
        g.to, g.cap = self.to[:], self.cap[:]
        return g


def augment_along(g, s, t, prev_edge):
    path, v, b = [], t, INF
    while v != s:
        e = prev_edge[v]
        b = min(b, g.cap[e])
        path.append(e)
        v = g.to[e ^ 1]
    for e in path:
        g.cap[e] -= b
        g.cap[e ^ 1] += b
    verts = [s] + [g.to[e] for e in reversed(path)]
    return b, verts


def ford_fulkerson_dfs(g, s, t):
    """Augment along whatever path a depth-first search finds first."""
    flow, log = 0, []
    while True:
        prev_edge, seen = {}, {s}

        def dfs(u):
            if u == t:
                return True
            for e in g.head[u]:
                v = g.to[e]
                if g.cap[e] > 0 and v not in seen:
                    seen.add(v)
                    prev_edge[v] = e
                    if dfs(v):
                        return True
            return False
        if not dfs(s):
            return flow, log
        b, verts = augment_along(g, s, t, prev_edge)
        flow += b
        log.append((b, verts))


def edmonds_karp(g, s, t):
    flow, log = 0, []
    while True:
        prev_edge, q = {s: None}, deque([s])
        while q and t not in prev_edge:
            u = q.popleft()
            for e in g.head[u]:
                v = g.to[e]
                if g.cap[e] > 0 and v not in prev_edge:
                    prev_edge[v] = e
                    q.append(v)
        if t not in prev_edge:
            return flow, log
        b, verts = augment_along(g, s, t, prev_edge)
        flow += b
        log.append((b, verts))


def dinic(g, s, t):
    flow, phases = 0, []
    while True:
        level = [-1] * g.n
        level[s] = 0
        q = deque([s])
        while q:                            # BFS: build the level graph
            u = q.popleft()
            for e in g.head[u]:
                if g.cap[e] > 0 and level[g.to[e]] < 0:
                    level[g.to[e]] = level[u] + 1
                    q.append(g.to[e])
        if level[t] < 0:
            return flow, phases
        it = [0] * g.n

        def push(u, f):                     # DFS: blocking flow, edges level -> level + 1
            if u == t:
                return f
            while it[u] < len(g.head[u]):
                e = g.head[u][it[u]]
                v = g.to[e]
                if g.cap[e] > 0 and level[v] == level[u] + 1:
                    d = push(v, min(f, g.cap[e]))
                    if d:
                        g.cap[e] -= d
                        g.cap[e ^ 1] += d
                        return d
                it[u] += 1                  # this edge is useless for the rest of the phase
            return 0
        got = 0
        while True:
            d = push(s, INF)
            if not d:
                break
            got += d
        flow += got
        phases.append((level[t], got))


def min_cut(g, s):
    seen, q = {s}, deque([s])
    while q:
        u = q.popleft()
        for e in g.head[u]:
            if g.cap[e] > 0 and g.to[e] not in seen:
                seen.add(g.to[e])
                q.append(g.to[e])
    return seen


# ------------------------------------------------------ bipartite matching
def hopcroft_karp(left, adj):
    match_l = {u: None for u in left}
    match_r = {}
    phases = 0
    while True:
        dist, q = {}, deque()
        for u in left:                      # BFS from all free left vertices
            if match_l[u] is None:
                dist[u] = 0
                q.append(u)
        found = False
        while q:
            u = q.popleft()
            for v in adj[u]:
                w = match_r.get(v)
                if w is None:
                    found = True
                elif w not in dist:
                    dist[w] = dist[u] + 1
                    q.append(w)
        if not found:
            return match_l, phases
        phases += 1

        def try_augment(u):                 # DFS along shortest alternating paths
            for v in adj[u]:
                w = match_r.get(v)
                if w is None or (dist.get(w) == dist[u] + 1 and try_augment(w)):
                    match_l[u], match_r[v] = v, u
                    return True
            dist[u] = INF                   # dead end: skip it for the rest of the phase
            return False
        for u in left:
            if match_l[u] is None:
                try_augment(u)


# -------------------------------------------------------------- Hungarian
def hungarian(cost):
    """Minimum-cost perfect assignment for a square cost matrix, O(n^3)."""
    n = len(cost)
    u, v = [0] * (n + 1), [0] * (n + 1)     # potentials of rows and columns
    p, way = [0] * (n + 1), [0] * (n + 1)   # p[j] = row matched to column j (1-based)
    for i in range(1, n + 1):
        p[0], j0 = i, 0
        minv, used = [INF] * (n + 1), [False] * (n + 1)
        while True:                         # Dijkstra-like search for an augmenting path
            used[j0] = True
            i0, delta, j1 = p[j0], INF, 0
            for j in range(1, n + 1):
                if not used[j]:
                    cur = cost[i0 - 1][j - 1] - u[i0] - v[j]
                    if cur < minv[j]:
                        minv[j], way[j] = cur, j0
                    if minv[j] < delta:
                        delta, j1 = minv[j], j
            for j in range(n + 1):          # shift potentials so a new edge becomes tight
                if used[j]:
                    u[p[j]] += delta
                    v[j] -= delta
                else:
                    minv[j] -= delta
            j0 = j1
            if p[j0] == 0:
                break
        while j0:                           # flip the augmenting path
            j1 = way[j0]
            p[j0] = p[j1]
            j0 = j1
    assign = [0] * n
    for j in range(1, n + 1):
        assign[p[j] - 1] = j - 1
    return assign, sum(cost[i][assign[i]] for i in range(n)), -v[0]


# ---------------------------------------------------------- min-cost flow
def min_cost_flow(n, arcs, s, t, need):
    """Successive shortest paths with Bellman-Ford on the residual graph."""
    to, cap, cost, head = [], [], [], [[] for _ in range(n)]
    for a, b, c, w in arcs:
        for x, y, cc, ww in ((a, b, c, w), (b, a, 0, -w)):
            head[x].append(len(to)); to.append(y); cap.append(cc); cost.append(ww)
    flow = total = 0
    log = []
    while flow < need:
        dist, prev = [INF] * n, [None] * n
        dist[s] = 0
        for _ in range(n - 1):
            for x in range(n):
                if dist[x] == INF:
                    continue
                for e in head[x]:
                    if cap[e] > 0 and dist[x] + cost[e] < dist[to[e]]:
                        dist[to[e]], prev[to[e]] = dist[x] + cost[e], e
        if dist[t] == INF:
            break
        b, v = need - flow, t
        while v != s:
            b = min(b, cap[prev[v]])
            v = to[prev[v] ^ 1]
        v, path = t, [t]
        while v != s:
            cap[prev[v]] -= b
            cap[prev[v] ^ 1] += b
            v = to[prev[v] ^ 1]
            path.append(v)
        flow += b
        total += b * dist[t]
        log.append((b, dist[t], path[::-1]))
    return flow, total, log


# ----------------------------------------------------------- Gale-Shapley
def gale_shapley(prop_pref, recv_pref, trace=False):
    rank = {r: {p: i for i, p in enumerate(lst)} for r, lst in recv_pref.items()}
    nxt = {p: 0 for p in prop_pref}
    engaged = {}                            # receiver -> proposer
    free = deque(prop_pref)
    while free:
        p = free.popleft()
        r = prop_pref[p][nxt[p]]
        nxt[p] += 1
        cur = engaged.get(r)
        if cur is None:
            engaged[r] = p
            msg = "accepts"
        elif rank[r][p] < rank[r][cur]:
            engaged[r] = p
            free.append(cur)
            msg = f"accepts, drops {cur}"
        else:
            free.append(p)
            msg = "rejects"
        if trace:
            print(f"  {p} proposes to {r}: {msg}")
    return {p: r for r, p in engaged.items()}


def blocking_pairs(match, prop_pref, recv_pref):
    partner = {r: p for p, r in match.items()}
    bad = []
    for p, prefs in prop_pref.items():
        for r in prefs[:prefs.index(match[p])]:       # receivers p prefers to its own
            if recv_pref[r].index(p) < recv_pref[r].index(partner[r]):
                bad.append((p, r))
    return bad


def main():
    print("== 17.1-17.2 minimum spanning trees ==")
    V = list("ABCDEFG")
    E = [(7, "A", "B"), (5, "A", "D"), (8, "B", "C"), (9, "B", "D"), (7, "B", "E"),
         (5, "C", "E"), (15, "D", "E"), (6, "D", "F"), (8, "E", "F"), (9, "E", "G"),
         (11, "F", "G")]
    print(" Kruskal:")
    tk = kruskal(V, E, trace=True)
    print(" Prim from A:")
    tp = prim(V, E, "A", trace=True)
    print(" Boruvka:")
    tb = boruvka(V, E, trace=True)
    for name, t in (("Kruskal", tk), ("Prim", tp), ("Boruvka", tb)):
        print(f"  {name:8} weight {sum(w for _, _, w in t)}, edges "
              + " ".join(f"{u}{v}" for u, v, _ in sorted((min(a, b), max(a, b), w) for a, b, w in t)))

    print("== 17.3-17.5 maximum flow ==")
    names = ["s", "a", "b", "c", "d", "t"]
    ix = {x: i for i, x in enumerate(names)}
    arcs = [("s", "a", 10), ("s", "b", 8), ("a", "b", 2), ("a", "c", 5), ("b", "d", 10),
            ("c", "b", 7), ("c", "t", 7), ("d", "c", 6), ("d", "t", 10)]
    base = Network(6)
    for u, v, c in arcs:
        base.add(ix[u], ix[v], c)
    for name, algo in (("Ford-Fulkerson (DFS)", ford_fulkerson_dfs), ("Edmonds-Karp (BFS)", edmonds_karp)):
        g = base.copy()
        f, log = algo(g, ix["s"], ix["t"])
        print(f" {name}: flow {f}")
        for b, verts in log:
            print(f"   push {b:2} along {' '.join(names[x] for x in verts)}")
    g = base.copy()
    f, phases = dinic(g, ix["s"], ix["t"])
    print(f" Dinic: flow {f}; phases (distance to t, flow added): {phases}")
    S = min_cut(g, ix["s"])
    cut = [(u, v, c) for u, v, c in arcs if ix[u] in S and ix[v] not in S]
    print("  min cut S =", {names[x] for x in sorted(S)}, " edges", cut, " capacity", sum(c for *_, c in cut))
    flows = {}
    for e in range(0, len(g.to), 2):
        u, v = names[g.to[e ^ 1]], names[g.to[e]]
        flows[f"{u}{v}"] = g.cap[e ^ 1]
    print("  flow on each edge:", flows)

    print("== 17.5 a bad case for Ford-Fulkerson ==")
    bad = Network(4)                        # s=0, a=1, b=2, t=3
    bad.add(0, 1, 1000); bad.add(0, 2, 1000); bad.add(1, 2, 1); bad.add(1, 3, 1000); bad.add(2, 3, 1000)
    g = bad.copy()
    flow, count, k = 0, 0, 0
    unlucky = ([0, 1, 2, 3], [0, 2, 1, 3])  # s a b t, then s b a t (undoing a->b), ...
    while True:
        verts = unlucky[k % 2]
        prev_edge = {}
        for x, y in zip(verts, verts[1:]):
            e = next((e for e in g.head[x] if g.to[e] == y and g.cap[e] > 0), None)
            if e is None:
                break
            prev_edge[y] = e
        else:
            flow += augment_along(g, 0, 3, prev_edge)[0]
            count += 1
            k += 1
            continue
        break
    print(f"  always choosing a path through the middle edge: flow {flow} after {count} augmentations of 1")
    g = bad.copy()
    f, log = edmonds_karp(g, 0, 3)
    print(f"  Edmonds-Karp: flow {f} after {len(log)} augmentations")

    print("== 17.6 bipartite matching ==")
    left = ["Ana", "Ben", "Cai", "Dev", "Eli"]
    jobs = {"Ana": ["drill", "map"], "Ben": ["drill"], "Cai": ["map", "cook", "fix"],
            "Dev": ["drill", "map"], "Eli": ["fix", "pilot"]}
    match, phases = hopcroft_karp(left, jobs)
    print("  Hopcroft-Karp:", match, " size", sum(v is not None for v in match.values()), " phases", phases)
    right = sorted({j for js in jobs.values() for j in js})
    n = 2 + len(left) + len(right)
    g = Network(n)
    for i, p in enumerate(left):
        g.add(0, 2 + i, 1)
        for j in jobs[p]:
            g.add(2 + i, 2 + len(left) + right.index(j), 1)
    for k in range(len(right)):
        g.add(2 + len(left) + k, 1, 1)
    print("  as a max flow: matching size", edmonds_karp(g, 0, 1)[0])
    for k in range(1, len(left) + 1):
        for A in itertools.combinations(left, k):
            N = {j for p in A for j in jobs[p]}
            if len(N) < len(A):
                print(f"  Hall violated: {list(A)} can only do {sorted(N)}")
                break
        else:
            continue
        break

    print("== 17.7 assignment: the Hungarian algorithm ==")
    C = [[9, 2, 7, 8], [6, 4, 3, 7], [5, 8, 1, 8], [7, 6, 9, 4]]
    assign, total, dual = hungarian(C)
    brute = min(itertools.permutations(range(4)), key=lambda p: sum(C[i][p[i]] for i in range(4)))
    print("  assignment row->column", assign, " cost", total, " dual value", dual)
    print("  brute force over 24 permutations:", list(brute), sum(C[i][brute[i]] for i in range(4)))

    print("== 17.7 min-cost flow ==")
    mc = [(0, 1, 4, 1), (0, 2, 2, 2), (1, 2, 2, 1), (1, 3, 2, 3), (2, 3, 4, 1)]
    f, cst, log = min_cost_flow(4, mc, 0, 3, 5)
    for b, d, path in log:
        print(f"  send {b} along {path} at cost {d} each")
    print(f"  total flow {f}, total cost {cst}")

    print("== 17.7 stable matching ==")
    P = {"A": ["z", "y", "x", "w"], "B": ["x", "w", "z", "y"],
         "C": ["w", "x", "y", "z"], "D": ["w", "y", "z", "x"]}
    R = {"w": ["D", "C", "A", "B"], "x": ["A", "D", "C", "B"],
         "y": ["B", "C", "A", "D"], "z": ["C", "B", "A", "D"]}
    m = gale_shapley(P, R, trace=True)
    print("  matching:", dict(sorted(m.items())), " blocking pairs:", blocking_pairs(m, P, R))
    m2 = gale_shapley(R, P)
    print("  receivers proposing instead:", dict(sorted((p, r) for r, p in m2.items())))
    stable = [dict(zip(P, q)) for q in itertools.permutations(R)
              if not blocking_pairs(dict(zip(P, q)), P, R)]
    print("  all stable matchings (by brute force):", stable)


if __name__ == "__main__":
    main()
