"""Chapter 21: Karger's random contraction algorithm for the global minimum cut."""
import random
from itertools import combinations
from math import comb, log, ceil

random.seed(1993)


def contract(n, edges):
    """One run: contract uniformly random edges until two super-vertices remain.
    Shuffling the edge list and skipping edges whose ends are already merged picks each next edge
    uniformly among the edges that are still present (self-loops removed)."""
    parent = list(range(n))

    def find(v):
        while parent[v] != v:
            parent[v] = parent[parent[v]]
            v = parent[v]
        return v

    order = edges[:]
    random.shuffle(order)
    groups = n
    for u, v in order:
        if groups == 2:
            break
        ru, rv = find(u), find(v)
        if ru != rv:
            parent[ru] = rv
            groups -= 1
    side = frozenset(v for v in range(n) if find(v) == find(0))
    cut = sum(1 for u, v in edges if (u in side) != (v in side))
    return cut, side


def brute_force_min_cut(n, edges):
    """Try every split of the vertices (vertex 0 always on side A): 2^(n-1) - 1 cuts."""
    best, count = None, 0
    for mask in range(2 ** (n - 1) - 1):           # the all-ones mask would put every vertex on side A
        side = {0} | {v for v in range(1, n) if mask >> (v - 1) & 1}
        cut = sum(1 for u, v in edges if (u in side) != (v in side))
        if best is None or cut < best:
            best, count = cut, 1
        elif cut == best:
            count += 1
    return best, count


# Two four-vertex cliques {0,1,2,3} and {4,5,6,7} joined by the edges 3-4 and 2-5
G = [e for e in combinations(range(4), 2)] + [(a + 4, b + 4) for a, b in combinations(range(4), 2)]
G += [(3, 4), (2, 5)]
n = 8
print(f"Two cliques joined by two edges: n = {n}, m = {len(G)}")
print("  brute force (min cut, number of minimum cuts):", brute_force_min_cut(n, G))
trials, wins = 20000, 0
for _ in range(trials):
    cut, _ = contract(n, G)
    wins += cut == 2
print(f"  one contraction run finds it with frequency {wins / trials:.4f};"
      f" Karger's guarantee is at least 1/C(n,2) = {1 / comb(n, 2):.4f}")

print("\nCycle graph C_n: any two edges form a minimum cut, so it has exactly C(n,2) minimum cuts")
for n in (5, 6, 8):
    cycle = [(i, (i + 1) % n) for i in range(n)]
    best, count = brute_force_min_cut(n, cycle)
    trials, hits = 40000, 0
    for _ in range(trials):
        cut, side = contract(n, cycle)
        hits += side in (frozenset([0]), frozenset(range(1, n)))   # one particular cut: vertex 0 alone
    print(f"  n = {n}: min cut {best}, {count} minimum cuts (C(n,2) = {comb(n, 2)});"
          f" the cut 'vertex 0 alone' is found with frequency {hits / trials:.4f}, 1/C(n,2) = {1 / comb(n, 2):.4f}")

print("\nRandom graphs, repeated runs: C(n,2) ln n repetitions, failure at most 1/n")
for trial in range(5):
    n = 12
    E = [e for e in combinations(range(n), 2) if random.random() < 0.35]
    best, _ = brute_force_min_cut(n, E)
    reps = ceil(comb(n, 2) * log(n))
    found = min(contract(n, E)[0] for _ in range(reps))
    print(f"  graph {trial}: m = {len(E):2}, true min cut {best}, best of {reps} runs {found}")
