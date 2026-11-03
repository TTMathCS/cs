# Chapter 23: metric TSP.  Double-tree (factor 2), Christofides (factor 1.5),
# the exact answer by Held-Karp dynamic programming, and 2-opt local search.
import itertools
import math
import random


def dist_matrix(points):
    return [[math.dist(p, q) for q in points] for p in points]


def tour_length(tour, d):
    return sum(d[tour[i]][tour[(i + 1) % len(tour)]] for i in range(len(tour)))


def mst_prim(d):
    """Prim's algorithm on a complete graph, O(n^2). Returns a list of edges."""
    n = len(d)
    in_tree = [False] * n
    best = [math.inf] * n
    parent = [-1] * n
    best[0] = 0
    edges = []
    for _ in range(n):
        u = min((v for v in range(n) if not in_tree[v]), key=lambda v: best[v])
        in_tree[u] = True
        if parent[u] >= 0:
            edges.append((parent[u], u))
        for v in range(n):
            if not in_tree[v] and d[u][v] < best[v]:
                best[v], parent[v] = d[u][v], u
    return edges


def double_tree(d):
    """Walk the MST in preorder; skipping repeated cities is the shortcut."""
    adj = {v: [] for v in range(len(d))}
    for u, v in mst_prim(d):
        adj[u].append(v)
        adj[v].append(u)
    tour, seen, stack = [], set(), [0]
    while stack:
        u = stack.pop()
        if u in seen:
            continue
        seen.add(u)
        tour.append(u)
        stack.extend(sorted(adj[u], reverse=True))
    return tour


def min_perfect_matching(vertices, d):
    """Exact minimum-weight perfect matching by bitmask DP (few odd vertices)."""
    m = len(vertices)
    memo = {0: (0.0, [])}

    def solve(mask):
        if mask in memo:
            return memo[mask]
        i = (mask & -mask).bit_length() - 1      # lowest vertex still unmatched
        best = (math.inf, [])
        rest = mask & ~(1 << i)
        j_mask = rest
        while j_mask:
            j = (j_mask & -j_mask).bit_length() - 1
            j_mask &= j_mask - 1
            cost, pairs = solve(rest & ~(1 << j))
            cost += d[vertices[i]][vertices[j]]
            if cost < best[0]:
                best = (cost, pairs + [(vertices[i], vertices[j])])
        memo[mask] = best
        return best

    return solve((1 << m) - 1)[1]


def euler_circuit(n, multiedges):
    """Hierholzer's algorithm on a connected multigraph with all degrees even."""
    adj = {v: [] for v in range(n)}
    for idx, (u, v) in enumerate(multiedges):
        adj[u].append((v, idx))
        adj[v].append((u, idx))
    used = [False] * len(multiedges)
    stack, circuit = [0], []
    while stack:
        u = stack[-1]
        while adj[u] and used[adj[u][-1][1]]:
            adj[u].pop()
        if adj[u]:
            v, idx = adj[u].pop()
            used[idx] = True
            stack.append(v)
        else:
            circuit.append(stack.pop())
    return circuit


def christofides(d):
    n = len(d)
    tree = mst_prim(d)
    degree = [0] * n
    for u, v in tree:
        degree[u] += 1
        degree[v] += 1
    odd = [v for v in range(n) if degree[v] % 2 == 1]
    matching = min_perfect_matching(odd, d)
    circuit = euler_circuit(n, tree + matching)
    tour, seen = [], set()
    for v in circuit:                      # shortcut repeated cities
        if v not in seen:
            seen.add(v)
            tour.append(v)
    return tour, len(odd)


def held_karp(d):
    """Exact TSP in O(2^n n^2) (chapter 13)."""
    n = len(d)
    INF = math.inf
    dp = [[INF] * n for _ in range(1 << n)]
    dp[1][0] = 0.0
    for mask in range(1 << n):
        if not mask & 1:
            continue
        for last in range(n):
            cur = dp[mask][last]
            if cur == INF:
                continue
            for nxt in range(n):
                if mask & (1 << nxt):
                    continue
                new = mask | (1 << nxt)
                if cur + d[last][nxt] < dp[new][nxt]:
                    dp[new][nxt] = cur + d[last][nxt]
    full = (1 << n) - 1
    return min(dp[full][v] + d[v][0] for v in range(1, n))


def two_opt(tour, d):
    """Reverse a segment whenever that shortens the tour; stop at a local optimum."""
    tour = tour[:]
    n = len(tour)
    improved, moves = True, 0
    while improved:
        improved = False
        for i in range(n - 1):
            for j in range(i + 2, n if i > 0 else n - 1):
                a, b = tour[i], tour[i + 1]
                c, e = tour[j], tour[(j + 1) % n]
                delta = d[a][c] + d[b][e] - d[a][b] - d[c][e]
                if delta < -1e-12:
                    tour[i + 1:j + 1] = reversed(tour[i + 1:j + 1])
                    improved, moves = True, moves + 1
    return tour, moves


rng = random.Random(2023)
print("  n   optimal  double-tree  christofides   2-opt(from DT)  odd")
for trial in range(6):
    n = 12
    pts = [(rng.uniform(0, 100), rng.uniform(0, 100)) for _ in range(n)]
    d = dist_matrix(pts)
    opt = held_karp(d)
    dt = tour_length(double_tree(d), d)
    ch_tour, odd = christofides(d)
    ch = tour_length(ch_tour, d)
    t2, _ = two_opt(double_tree(d), d)
    lo = tour_length(t2, d)
    mst = sum(d[u][v] for u, v in mst_prim(d))
    assert mst <= opt + 1e-9 and dt <= 2 * opt + 1e-9 and ch <= 1.5 * opt + 1e-9
    print(f"{n:3d}  {opt:8.1f}  {dt:6.1f} ({dt/opt:.2f})  {ch:6.1f} ({ch/opt:.2f})"
          f"   {lo:6.1f} ({lo/opt:.2f})    {odd}")

# The four-city example traced by hand in section 23.2
pts = [(0, 0), (4, 0), (4, 3), (0, 3)]
d = dist_matrix(pts)
print()
print("rectangle 4 x 3: MST edges", mst_prim(d),
      "weight", sum(d[u][v] for u, v in mst_prim(d)))
print("double-tree tour", double_tree(d), "length", tour_length(double_tree(d), d))
print("optimal length", held_karp(d))
