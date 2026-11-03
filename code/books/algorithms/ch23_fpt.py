# Chapter 23: vertex cover parameterized by k.
# Bounded search tree O(2^k * m), Buss's kernel, and a comparison with
# trying all C(n, k) subsets.
import math
import random


def vc_branch(edges, k, counter):
    """Is there a cover of size <= k?  Branch on the two ends of any edge."""
    counter[0] += 1
    if not edges:
        return set()
    if k == 0:
        return None
    u, v = edges[0]
    for pick in (u, v):                             # one of them must be in the cover
        rest = [e for e in edges if pick not in e]
        sub = vc_branch(rest, k - 1, counter)
        if sub is not None:
            return sub | {pick}
    return None


def buss_kernel(edges, k):
    """Rule 1: a vertex of degree > k must be in every cover of size <= k.
    Rule 2: afterwards, a yes-instance has at most k^2 edges.
    Returns (forced vertices, remaining edges, remaining k) or None for 'no'."""
    forced = set()
    edges = list(edges)
    while True:
        deg = {}
        for u, v in edges:
            deg[u] = deg.get(u, 0) + 1
            deg[v] = deg.get(v, 0) + 1
        high = [x for x in deg if deg[x] > k]
        if not high:
            break
        x = high[0]
        forced.add(x)
        edges = [e for e in edges if x not in e]
        k -= 1
        if k < 0:
            return None
    if len(edges) > k * k:
        return None
    return forced, edges, k


def planted_instance(n, k, extra, rng):
    """A graph on n vertices that has a cover of size k (the first k vertices)."""
    cover = list(range(k))
    edges = set()
    while len(edges) < extra:
        u = rng.choice(cover)
        v = rng.randrange(n)
        if u != v and (v, u) not in edges:
            edges.add((u, v) if rng.random() < 0.5 else (v, u))
    edges = list(edges)
    rng.shuffle(edges)                              # hide the planted cover
    return edges


rng = random.Random(7)
print("   n    m   k   search-tree nodes   2^(k+1)-1   C(n,k)")
for n, k, m in [(100, 6, 150), (300, 8, 400), (1000, 10, 1500), (3000, 12, 4000)]:
    edges = planted_instance(n, k, m, rng)
    counter = [0]
    cover = vc_branch(edges, k, counter)
    assert cover is not None and all(u in cover or v in cover for u, v in edges)
    print(f"{n:5d} {m:4d} {k:3d}   {counter[0]:12d}   {2 ** (k + 1) - 1:9d}   {math.comb(n, k):.2e}")
print()

# Buss's kernel: a few busy vertices plus a sparse part
for title, edges, k in [
    ("dense planted", planted_instance(1000, 10, 1500, rng), 10),
    ("sparse planted", planted_instance(1000, 10, 40, rng), 10),
    ("matching of 15 edges", [(2 * i, 2 * i + 1) for i in range(15)], 3),
]:
    res = buss_kernel(edges, k)
    if res is None:
        print(f"kernel ({title}): {len(edges)} edges, k={k} -> answer is NO at once")
        continue
    forced, left, k_left = res
    verts = {x for e in left for x in e}
    counter = [0]
    sub = vc_branch(left, k_left, counter)
    print(f"kernel ({title}): {len(edges)} edges, k={k} -> forced {len(forced)}, "
          f"left {len(left)} edges on {len(verts)} vertices, k'={k_left}; "
          f"search {counter[0]} nodes, cover {len(forced | sub)}")
print()
edges = planted_instance(1000, 10, 1500, rng)
for k in (10, 9):
    counter = [0]
    found = vc_branch(edges, k, counter) is not None
    print(f"cover of size {k}? {found}  ({counter[0]} search-tree nodes, 2^(k+1)-1 = {2 ** (k + 1) - 1})")
