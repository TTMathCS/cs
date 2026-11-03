"""Chapter 14: an exact exponential algorithm for maximum independent set, and branching numbers."""
import itertools
import random


def mis_branching(adj):
    """Size of a maximum independent set. adj: dict vertex -> set of neighbours."""
    calls = 0

    def remove(g, vs):
        return {v: g[v] - vs for v in g if v not in vs}

    def solve(g):
        nonlocal calls
        calls += 1
        if not g:
            return 0
        v = min(g, key=lambda x: len(g[x]))
        if len(g[v]) <= 1:                     # degree 0 or 1: some maximum set contains v
            return 1 + solve(remove(g, {v} | g[v]))
        u = max(g, key=lambda x: len(g[x]))
        if len(g[u]) <= 2:                     # all degrees 2: disjoint cycles, solve directly
            return cycles_mis(g)
        # degree >= 3: either u is out, or u is in and its neighbours are out
        return max(solve(remove(g, {u})), 1 + solve(remove(g, {u} | g[u])))

    def cycles_mis(g):
        seen, total = set(), 0
        for s in g:
            if s in seen:
                continue
            size, stack = 0, [s]
            seen.add(s)
            while stack:
                x = stack.pop()
                size += 1
                for y in g[x]:
                    if y not in seen:
                        seen.add(y)
                        stack.append(y)
            total += size // 2                 # a cycle of length L has MIS floor(L/2)
        return total
    return solve(adj), calls


def mis_brute(adj):
    vs = list(adj)
    for r in range(len(vs), -1, -1):
        for c in itertools.combinations(vs, r):
            if all(b not in adj[a] for a, b in itertools.combinations(c, 2)):
                return r


def branching_number(branches):
    """The c > 1 with sum of c^(-d) = 1 for branches that shrink n by d each (bisection)."""
    lo, hi = 1.0, 2.0
    for _ in range(60):
        mid = (lo + hi) / 2
        if sum(mid ** -d for d in branches) > 1:
            lo = mid
        else:
            hi = mid
    return hi


def queens_children(n, placed):
    r = len(placed)
    return [] if r == n else [placed + [c] for c in range(n)
                              if all(c != pc and abs(c - pc) != r - pr for pr, pc in enumerate(placed))]


def knuth_estimate(n, rng):
    """One random root-to-leaf probe; returns 1 + d1 + d1*d2 + ... (Knuth 1975)."""
    node, product, total = [], 1, 1
    while True:
        kids = queens_children(n, node)
        if not kids:
            return total
        product *= len(kids)
        total += product
        node = rng.choice(kids)


def count_nodes(n, node=None):
    node = node or []
    return 1 + sum(count_nodes(n, k) for k in queens_children(n, node))


def random_graph(n, p, rng):
    adj = {v: set() for v in range(n)}
    for a, b in itertools.combinations(range(n), 2):
        if rng.random() < p:
            adj[a].add(b)
            adj[b].add(a)
    return adj


if __name__ == "__main__":
    for br in ((1, 1), (1, 2), (1, 4), (1, 3), (2, 2, 2)):
        print(f"branching vector {br}: T(n) = O({branching_number(br):.4f}^n)")

    rng = random.Random(2009)
    ok = True
    for _ in range(40):
        g = random_graph(rng.randint(1, 13), rng.choice((0.2, 0.4, 0.6)), rng)
        ok &= mis_branching(g)[0] == mis_brute(g)
    print("\n40 random graphs, branching agrees with brute force:", ok)
    for n in (20, 40, 60):
        g = random_graph(n, 0.15, rng)
        size, calls = mis_branching(g)
        print(f"n = {n}: maximum independent set {size}, {calls} calls (2^n = {2 ** n:.2e},"
              f" 1.3803^n = {1.3803 ** n:.2e})")

    for n in (8, 10):
        probes = [knuth_estimate(n, rng) for _ in range(2000)]
        print(f"\n{n}-queens search tree: Knuth's estimate from 2000 probes {sum(probes) / len(probes):.0f},"
              f" exact count {count_nodes(n)}")
