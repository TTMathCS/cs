"""Chapter 16: shortest paths, built from scratch.

Dijkstra (with a trace), the Mars route from this site's banner, Bellman-Ford
(with a negative cycle), shortest paths in a DAG, Floyd-Warshall, Johnson's
reweighting, A* and bidirectional search on a grid, ALT landmarks, and 0-1 BFS.
Standard library only.
"""
import heapq
import math
import random
from collections import deque

INF = math.inf


def show(x):
    return "inf" if x == INF else f"{x:g}"


# ------------------------------------------------------------- Dijkstra
def dijkstra(adj, s, trace=False):
    dist = {v: INF for v in adj}
    parent = {v: None for v in adj}
    dist[s] = 0
    pq = [(0, s)]
    done = set()
    while pq:
        d, u = heapq.heappop(pq)
        if u in done:                 # stale entry: u was settled earlier
            continue
        done.add(u)
        for v, w in adj[u]:
            if d + w < dist[v]:       # relax the edge u -> v
                dist[v] = d + w
                parent[v] = u
                heapq.heappush(pq, (dist[v], v))
        if trace:
            row = " ".join(f"{v}={show(dist[v])}" for v in adj)
            print(f"  settle {u} at {show(d)}:  {row}")
    return dist, parent


def path_to(parent, v):
    p = []
    while v is not None:
        p.append(v)
        v = parent[v]
    return p[::-1]


# ------------------------------------------------- the banner's Mars route
R_MARS = 3389.5
PLACES = {  # latitude N, longitude E, from the USGS Gazetteer of Planetary Nomenclature
    "Erebus Montes": (35.7, -175.0), "Olympus Mons": (18.65, -133.8),
    "Ascraeus Mons": (11.92, -104.08), "Valles Marineris": (-13.9, -59.2),
    "Elysium Mons": (25.02, 147.21), "Utopia Planitia": (47.97, 134.26),
    "Gale crater": (-5.4, 137.8), "Jezero crater": (18.38, 77.58),
    "Hellas Planitia": (-42.4, 70.5),
}
ROADS = [("Erebus Montes", "Olympus Mons"), ("Erebus Montes", "Elysium Mons"),
         ("Erebus Montes", "Utopia Planitia"), ("Olympus Mons", "Ascraeus Mons"),
         ("Ascraeus Mons", "Valles Marineris"), ("Elysium Mons", "Gale crater"),
         ("Utopia Planitia", "Elysium Mons"), ("Utopia Planitia", "Jezero crater"),
         ("Jezero crater", "Gale crater"), ("Jezero crater", "Hellas Planitia"),
         ("Gale crater", "Hellas Planitia"), ("Olympus Mons", "Gale crater")]


def great_circle(a, b):
    (la1, lo1), (la2, lo2) = PLACES[a], PLACES[b]
    p1, p2, dl = math.radians(la1), math.radians(la2), math.radians(lo2 - lo1)
    c = math.sin(p1) * math.sin(p2) + math.cos(p1) * math.cos(p2) * math.cos(dl)
    return R_MARS * math.acos(max(-1.0, min(1.0, c)))


# ---------------------------------------------------------- Bellman-Ford
def bellman_ford(vertices, edges, s, trace=False):
    dist = {v: INF for v in vertices}
    parent = {v: None for v in vertices}
    dist[s] = 0
    for i in range(1, len(vertices)):
        changed = False
        for u, v, w in edges:
            if dist[u] + w < dist[v]:
                dist[v] = dist[u] + w
                parent[v] = u
                changed = True
        if trace:
            print(f"  round {i}: " + " ".join(f"{v}={show(dist[v])}" for v in vertices))
        if not changed:
            break
    for u, v, w in edges:             # one more round: any change means a negative cycle
        if dist[u] + w < dist[v]:
            x = v
            parent[v] = u
            for _ in range(len(vertices)):  # step back V times to land on the cycle
                x = parent[x]
            cycle, y = [x], parent[x]
            while y != x:
                cycle.append(y)
                y = parent[y]
            return None, cycle[::-1]
    return dist, parent


# ------------------------------------------------------------- DAG paths
def dag_shortest(adj, order, s, longest=False):
    sign = -1 if longest else 1
    dist = {v: INF for v in adj}
    parent = {v: None for v in adj}
    dist[s] = 0
    for u in order:
        if dist[u] == INF:
            continue
        for v, w in adj[u]:
            if dist[u] + sign * w < dist[v]:
                dist[v] = dist[u] + sign * w
                parent[v] = u
    if longest:
        dist = {v: (-d if d != INF else -INF) for v, d in dist.items()}
    return dist, parent


# -------------------------------------------------------- Floyd-Warshall
def floyd_warshall(n, edges, trace=False):
    D = [[0 if i == j else INF for j in range(n)] for i in range(n)]
    for u, v, w in edges:
        D[u][v] = min(D[u][v], w)
    for k in range(n):
        for i in range(n):
            for j in range(n):
                if D[i][k] + D[k][j] < D[i][j]:
                    D[i][j] = D[i][k] + D[k][j]
        if trace:
            print(f"  after k={k}: " + "  ".join(" ".join(f"{show(x):>3}" for x in row) for row in D))
    return D


# ------------------------------------------------------------- Johnson
def johnson(n, edges):
    q = n                                          # new vertex joined to all by 0
    h, _ = bellman_ford(list(range(n + 1)), edges + [(q, v, 0) for v in range(n)], q)
    if h is None:
        raise ValueError("negative cycle")
    adj = {v: [] for v in range(n)}
    for u, v, w in edges:
        adj[u].append((v, w + h[u] - h[v]))        # reweighted, never negative
    D = []
    for s in range(n):
        d, _ = dijkstra(adj, s)
        D.append([d[t] - h[s] + h[t] if d[t] != INF else INF for t in range(n)])
    return D, h, adj


# ------------------------------------------------------ grids, A*, ALT
def make_grid(n, wall_prob, seed):
    rng = random.Random(seed)
    g = [[rng.random() < wall_prob for _ in range(n)] for _ in range(n)]
    g[0][0] = g[n - 1][n - 1] = False
    return g


def grid_neighbours(g, cell):
    r, c = cell
    n = len(g)
    for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        rr, cc = r + dr, c + dc
        if 0 <= rr < n and 0 <= cc < n and not g[rr][cc]:
            yield (rr, cc), 1


def astar(g, s, t, h):
    """A* with a consistent heuristic h; returns (cost, vertices settled)."""
    dist = {s: 0}
    pq = [(h(s), 0, s)]
    done = set()
    while pq:
        f, d, u = heapq.heappop(pq)
        if u in done:
            continue
        done.add(u)
        if u == t:
            return d, len(done)
        for v, w in grid_neighbours(g, u):
            nd = d + w
            if nd < dist.get(v, INF):
                dist[v] = nd
                heapq.heappush(pq, (nd + h(v), nd, v))
    return INF, len(done)


def bfs_all(g, s):
    dist = {s: 0}
    q = deque([s])
    while q:
        u = q.popleft()
        for v, _ in grid_neighbours(g, u):
            if v not in dist:
                dist[v] = dist[u] + 1
                q.append(v)
    return dist


def bidirectional(g, s, t):
    """Bidirectional Dijkstra on an undirected graph; returns (cost, settled)."""
    dist = [{s: 0}, {t: 0}]
    pq = [[(0, s)], [(0, t)]]
    done = [set(), set()]
    best = INF
    while pq[0] and pq[1]:
        if pq[0][0][0] + pq[1][0][0] >= best:      # stopping rule
            break
        side = 0 if pq[0][0][0] <= pq[1][0][0] else 1
        d, u = heapq.heappop(pq[side])
        if u in done[side]:
            continue
        done[side].add(u)
        for v, w in grid_neighbours(g, u):
            nd = d + w
            if nd < dist[side].get(v, INF):
                dist[side][v] = nd
                heapq.heappush(pq[side], (nd, v))
            if v in dist[1 - side]:
                best = min(best, nd + dist[1 - side][v])
    return best, len(done[0]) + len(done[1])


# ---------------------------------------------------------------- 0-1 BFS
def zero_one_bfs(adj, s):
    dist = {v: INF for v in adj}
    dist[s] = 0
    dq = deque([s])
    while dq:
        u = dq.popleft()
        for v, w in adj[u]:
            if dist[u] + w < dist[v]:
                dist[v] = dist[u] + w
                if w == 0:
                    dq.appendleft(v)       # same distance: front
                else:
                    dq.append(v)           # one more: back
    return dist


def main():
    print("== 16.2 Dijkstra, traced ==")
    G = {"s": [("a", 4), ("b", 1)], "a": [("c", 1)], "b": [("a", 2), ("c", 5), ("d", 8)],
         "c": [("d", 3), ("e", 6)], "d": [("e", 1)], "e": []}
    dist, parent = dijkstra(G, "s", trace=True)
    print("  path to e:", " ".join(path_to(parent, "e")), "length", dist["e"])

    print("== 16.2 Dijkstra fails with a negative edge ==")
    N = {"s": [("a", 2), ("b", 3)], "a": [("c", 1)], "b": [("a", -2)], "c": []}
    print("  Dijkstra says c =", dijkstra(N, "s")[0]["c"], " but s->b->a->c costs 3 - 2 + 1 = 2")

    print("== 16.2 the Mars route on the banner ==")
    M = {p: [] for p in PLACES}
    for a, b in ROADS:
        d = great_circle(a, b)
        M[a].append((b, d))
        M[b].append((a, d))
    dist, parent = dijkstra(M, "Erebus Montes")
    for p in PLACES:
        print(f"  {p:17} {dist[p]:6.0f} km  via {' > '.join(path_to(parent, p))}")

    print("== 16.3 Bellman-Ford ==")
    V = ["s", "a", "b", "c", "d"]
    E = [("c", "d", 2), ("b", "c", -2), ("a", "b", 3), ("s", "a", 6), ("s", "b", 7),
         ("a", "c", 5), ("b", "d", 4), ("c", "a", -1)]
    dist, parent = bellman_ford(V, E, "s", trace=True)
    print("  final:", {v: dist[v] for v in V}, " path to d:", " ".join(path_to(parent, "d")))
    E2 = E[:-1] + [("c", "a", -2)]
    dist, cycle = bellman_ford(V, E2, "s")
    print("  with c->a = -2: negative cycle", " -> ".join(cycle + cycle[:1]))

    print("== 16.4 DAG shortest and longest paths ==")
    D = {"r": [("s", 5), ("t", 3)], "s": [("t", 2), ("x", 6)], "t": [("x", 7), ("y", 4), ("z", 2)],
         "x": [("y", -1), ("z", 1)], "y": [("z", -2)], "z": []}
    order = ["r", "s", "t", "x", "y", "z"]
    sd, _ = dag_shortest(D, order, "s")
    print("  shortest from s:", {v: show(x) for v, x in sd.items()})
    ld, lp = dag_shortest(D, order, "r", longest=True)
    print("  longest from r: ", {v: show(x) for v, x in ld.items()},
          " critical path:", " ".join(path_to(lp, "z")))

    print("== 16.5 Floyd-Warshall ==")
    FE = [(0, 1, 3), (0, 2, 8), (1, 3, 1), (2, 1, 4), (3, 0, 2), (3, 2, -5)]
    Dfw = floyd_warshall(4, FE, trace=True)
    for row in Dfw:
        print("   ", " ".join(f"{show(x):>3}" for x in row))
    print("== 16.5 Johnson ==")
    Dj, h, adj = johnson(4, FE)
    print("  h =", [h[v] for v in range(4)])
    print("  reweighted:", [(u, v, w) for u in adj for v, w in adj[u]])
    print("  same as Floyd-Warshall:", Dj == Dfw)

    print("== 16.6 A*, Dijkstra and bidirectional search on a 60 x 60 grid ==")
    n = 60
    g = make_grid(n, 0.25, seed=7)
    s, t = (0, 0), (n - 1, n - 1)
    zero = lambda v: 0
    manhattan = lambda v: abs(v[0] - t[0]) + abs(v[1] - t[1])
    c0, k0 = astar(g, s, t, zero)
    c1, k1 = astar(g, s, t, manhattan)
    c2, k2 = bidirectional(g, s, t)
    free = sum(not x for row in g for x in row)
    print(f"  free cells {free}; BFS distance {bfs_all(g, s)[t]}")
    print(f"  Dijkstra (h = 0):      cost {c0}, settled {k0}")
    print(f"  A* (Manhattan):        cost {c1}, settled {k1}")
    print(f"  bidirectional Dijkstra: cost {c2}, settled {k2}")
    marks = [(0, n - 1), (n - 1, 0), (0, 0), (n - 1, n - 1)]
    tables = [bfs_all(g, L) for L in marks]

    def alt(v):
        best = 0
        for T in tables:
            if v in T and t in T:
                best = max(best, T[t] - T[v], T[v] - T[t])
        return best
    c3, k3 = astar(g, s, t, alt)
    print(f"  A* with ALT (4 landmarks): cost {c3}, settled {k3}")

    print("== 16.7 0-1 BFS ==")
    Z = {0: [(1, 0), (2, 1)], 1: [(3, 1)], 2: [(3, 0)], 3: [(4, 1), (5, 0)], 4: [], 5: [(4, 0)]}
    print("  dist:", zero_one_bfs(Z, 0))
    print("  Dijkstra agrees:", dijkstra(Z, 0)[0] == zero_one_bfs(Z, 0))


if __name__ == "__main__":
    main()
