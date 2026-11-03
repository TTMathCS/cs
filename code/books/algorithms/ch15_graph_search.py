"""Chapter 15: graphs and graph search, built from scratch.

Every algorithm in the chapter on the chapter's own example graphs:
BFS (distances, parents, the queue after each step), DFS (discovery and
finish times, edge classes), topological sort (DFS and Kahn), strongly
connected components (Kosaraju and Tarjan), bridges and articulation
points, bipartite testing, and Euler tours (Hierholzer). Standard library only.
"""
from collections import deque


def undirected(edges):
    """Adjacency lists for an undirected graph, neighbours in sorted order."""
    adj = {}
    for u, v in edges:
        adj.setdefault(u, []).append(v)
        adj.setdefault(v, []).append(u)
    for u in adj:
        adj[u].sort()
    return dict(sorted(adj.items()))


def directed(edges, vertices=()):
    adj = {v: [] for v in vertices}
    for u, v in edges:
        adj.setdefault(u, []).append(v)
        adj.setdefault(v, [])
    return adj


# ---------------------------------------------------------------- BFS
def bfs(adj, s, trace=False):
    dist = {v: None for v in adj}          # None = not yet seen
    parent = {v: None for v in adj}
    dist[s] = 0
    q = deque([s])
    while q:
        u = q.popleft()
        for v in adj[u]:
            if dist[v] is None:
                dist[v] = dist[u] + 1
                parent[v] = u
                q.append(v)
        if trace:
            print(f"  take {u}: queue now {' '.join(q) or '(empty)'}")
    return dist, parent


def path_to(parent, v):
    p = []
    while v is not None:
        p.append(v)
        v = parent[v]
    return p[::-1]


# ---------------------------------------------------------------- DFS
def dfs_classify(adj):
    """Discovery/finish times and the class of every edge (directed graph)."""
    colour = {v: "white" for v in adj}
    d, f, kind = {}, {}, {}
    time = 0

    def visit(u):
        nonlocal time
        time += 1
        d[u] = time
        colour[u] = "grey"
        for v in adj[u]:
            if colour[v] == "white":
                kind[(u, v)] = "tree"
                visit(v)
            elif colour[v] == "grey":
                kind[(u, v)] = "back"
            elif d[u] < d[v]:
                kind[(u, v)] = "forward"
            else:
                kind[(u, v)] = "cross"
        colour[u] = "black"
        time += 1
        f[u] = time

    for u in adj:
        if colour[u] == "white":
            visit(u)
    return d, f, kind


# ------------------------------------------------------ topological sort
def topo_dfs(adj):
    """Vertices in decreasing finish time; raises on a cycle."""
    state, order = {v: 0 for v in adj}, []   # 0 white, 1 grey, 2 black

    def visit(u):
        state[u] = 1
        for v in adj[u]:
            if state[v] == 1:
                raise ValueError(f"cycle through edge {u}->{v}")
            if state[v] == 0:
                visit(v)
        state[u] = 2
        order.append(u)

    for u in adj:
        if state[u] == 0:
            visit(u)
    return order[::-1]


def topo_kahn(adj):
    indeg = {v: 0 for v in adj}
    for u in adj:
        for v in adj[u]:
            indeg[v] += 1
    ready = deque(v for v in adj if indeg[v] == 0)
    order = []
    while ready:
        u = ready.popleft()
        order.append(u)
        for v in adj[u]:
            indeg[v] -= 1
            if indeg[v] == 0:
                ready.append(v)
    if len(order) < len(adj):
        raise ValueError("graph has a cycle")
    return order


# ----------------------------------------------- strongly connected parts
def kosaraju(adj):
    seen, order = set(), []

    def visit(u):                       # first pass: record finish order
        seen.add(u)
        for v in adj[u]:
            if v not in seen:
                visit(v)
        order.append(u)

    for u in adj:
        if u not in seen:
            visit(u)
    radj = {v: [] for v in adj}         # reverse every edge
    for u in adj:
        for v in adj[u]:
            radj[v].append(u)
    comp, comps = {}, []

    def collect(u, c):                  # second pass on the reverse graph
        comp[u] = c
        comps[c].append(u)
        for v in radj[u]:
            if v not in comp:
                collect(v, c)

    for u in reversed(order):           # decreasing finish time
        if u not in comp:
            comps.append([])
            collect(u, len(comps) - 1)
    return comps


def tarjan(adj):
    index, low, on_stack, stack, comps = {}, {}, set(), [], []
    counter = 0

    def visit(u):
        nonlocal counter
        index[u] = low[u] = counter
        counter += 1
        stack.append(u)
        on_stack.add(u)
        for v in adj[u]:
            if v not in index:
                visit(v)
                low[u] = min(low[u], low[v])
            elif v in on_stack:
                low[u] = min(low[u], index[v])
        if low[u] == index[u]:          # u is the root of a component
            comp = []
            while True:
                w = stack.pop()
                on_stack.discard(w)
                comp.append(w)
                if w == u:
                    break
            comps.append(comp)

    for u in adj:
        if u not in index:
            visit(u)
    return comps, index, low


# ------------------------------------------- bridges and articulation points
def bridges_and_cuts(adj):
    disc, low, bridges, cuts = {}, {}, [], set()
    t = 0

    def visit(u, parent):
        nonlocal t
        disc[u] = low[u] = t
        t += 1
        children = 0
        for v in adj[u]:
            if v not in disc:
                children += 1
                visit(v, u)
                low[u] = min(low[u], low[v])
                if low[v] > disc[u]:
                    bridges.append((u, v))
                if parent is not None and low[v] >= disc[u]:
                    cuts.add(u)
            elif v != parent:
                low[u] = min(low[u], disc[v])
        if parent is None and children >= 2:
            cuts.add(u)

    for u in adj:
        if u not in disc:
            visit(u, None)
    return bridges, sorted(cuts), disc, low


# ---------------------------------------------------------------- bipartite
def two_colour(adj):
    """Return (True, colouring) or (False, an odd cycle)."""
    colour, parent = {}, {}
    for s in adj:
        if s in colour:
            continue
        colour[s], parent[s] = 0, None
        q = deque([s])
        while q:
            u = q.popleft()
            for v in adj[u]:
                if v not in colour:
                    colour[v], parent[v] = 1 - colour[u], u
                    q.append(v)
                elif colour[v] == colour[u]:      # odd cycle found
                    pu, pv = path_to(parent, u), path_to(parent, v)
                    i = 0
                    while i < min(len(pu), len(pv)) and pu[i] == pv[i]:
                        i += 1
                    return False, pu[i - 1:] + pv[i:][::-1]
    return True, colour


# --------------------------------------------------------------- Euler tours
def hierholzer(edges, start):
    """Euler circuit of an undirected multigraph given as a list of edges."""
    adj = {}
    for i, (u, v) in enumerate(edges):
        adj.setdefault(u, []).append((v, i))
        adj.setdefault(v, []).append((u, i))
    used = [False] * len(edges)
    stack, tour = [start], []
    while stack:
        u = stack[-1]
        while adj[u] and used[adj[u][-1][1]]:
            adj[u].pop()                        # drop edges already walked
        if adj[u]:
            v, i = adj[u].pop()
            used[i] = True
            stack.append(v)
        else:
            tour.append(stack.pop())
    return tour[::-1]


def main():
    print("== 15.1 adjacency list and matrix ==")
    G = undirected([("A", "B"), ("A", "C"), ("B", "D"), ("B", "E"), ("C", "E"),
                    ("D", "F"), ("E", "F"), ("E", "G"), ("F", "H"), ("G", "H")])
    names = list(G)
    for u in names:
        print(f"  {u}: {' '.join(G[u])}")
    print("     " + " ".join(names))
    for u in names:
        print(f"  {u}  " + " ".join("1" if v in G[u] else "0" for v in names))
    print("  edges:", sum(len(a) for a in G.values()) // 2,
          " degree sum:", sum(len(a) for a in G.values()))

    print("== 15.2 BFS from A ==")
    dist, parent = bfs(G, "A", trace=True)
    print("  dist  ", dist)
    print("  parent", parent)
    print("  path to H:", " ".join(path_to(parent, "H")))

    print("== 15.3 DFS edge classes ==")
    D = directed([("a", "b"), ("a", "c"), ("a", "d"), ("b", "c"), ("c", "a"),
                  ("d", "c"), ("d", "e")])
    d, f, kind = dfs_classify(D)
    for v in D:
        print(f"  {v}: d={d[v]:2} f={f[v]:2}")
    for e, k in kind.items():
        print(f"  {e[0]}->{e[1]}: {k}")

    print("== 15.4 topological sort ==")
    C = directed([("intro", "data"), ("discrete", "data"), ("discrete", "theory"),
                  ("data", "algos"), ("algos", "theory"), ("algos", "compilers"),
                  ("data", "systems"), ("systems", "compilers")])
    print("  DFS :", " ".join(topo_dfs(C)))
    print("  Kahn:", " ".join(topo_kahn(C)))
    try:
        topo_kahn(directed([("x", "y"), ("y", "z"), ("z", "x")]))
    except ValueError as err:
        print("  cycle x->y->z->x:", err)

    print("== 15.5 strongly connected components ==")
    S = directed([(1, 2), (2, 3), (3, 1), (3, 4), (4, 5), (5, 6), (6, 4),
                  (6, 7), (7, 8), (8, 7), (2, 5)])
    print("  Kosaraju:", kosaraju(S))
    comps, index, low = tarjan(S)
    print("  Tarjan:  ", comps)
    print("  index", index)
    print("  low  ", low)

    print("== 15.6 bridges and articulation points ==")
    B = undirected([("A", "B"), ("B", "C"), ("C", "A"), ("C", "D"), ("D", "E"),
                    ("E", "F"), ("F", "D"), ("F", "G")])
    br, cuts, disc, low = bridges_and_cuts(B)
    print("  disc", disc)
    print("  low ", low)
    print("  bridges:", br, " articulation points:", cuts)

    print("== 15.7 bipartite, odd cycles, Euler tours ==")
    cube = undirected([(0, 1), (1, 3), (3, 2), (2, 0), (4, 5), (5, 7), (7, 6),
                       (6, 4), (0, 4), (1, 5), (2, 6), (3, 7)])
    ok, col = two_colour(cube)
    print("  cube bipartite:", ok, "sides:",
          [v for v in col if col[v] == 0], [v for v in col if col[v] == 1])
    pent = undirected([(0, 1), (1, 2), (2, 3), (3, 4), (4, 0), (0, 5)])
    print("  pentagon+tail:", two_colour(pent))
    kb = [("N", "I"), ("N", "I"), ("S", "I"), ("S", "I"), ("N", "E"), ("S", "E"),
          ("I", "E")]
    deg = {}
    for u, v in kb:
        deg[u] = deg.get(u, 0) + 1
        deg[v] = deg.get(v, 0) + 1
    print("  Konigsberg degrees:", deg, "odd:", sum(x % 2 for x in deg.values()))
    house = [(1, 2), (2, 3), (3, 4), (4, 1), (1, 5), (5, 2), (1, 3), (2, 4)]
    hdeg = {}
    for u, v in house:
        hdeg[u] = hdeg.get(u, 0) + 1
        hdeg[v] = hdeg.get(v, 0) + 1
    print("  envelope degrees:", dict(sorted(hdeg.items())))
    odd = [v for v in sorted(hdeg) if hdeg[v] % 2]
    print("  odd vertices:", odd, "-> an Euler path must run between them")
    # add a dummy edge between the two odd vertices, find a circuit, cut it there
    tour = hierholzer(house + [(odd[0], odd[1])], odd[0])
    print("  circuit with extra edge:", tour)
    for i in range(len(tour) - 1):
        if {tour[i], tour[i + 1]} == set(odd):
            path = tour[i + 1:] + tour[1:i + 1]
            break
    print("  Euler path:", path, "uses", len(path) - 1, "edges")
    print("  Euler circuit of two triangles at 0:",
          hierholzer([(0, 1), (1, 2), (2, 0), (0, 3), (3, 4), (4, 0)], 0))


if __name__ == "__main__":
    main()
