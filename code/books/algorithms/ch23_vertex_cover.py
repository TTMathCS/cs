# Chapter 23: the matching-based 2-approximation for vertex cover,
# checked against an exact answer found by trying every subset.
import itertools
import random


def approx_vertex_cover(edges):
    """Take both ends of every edge that is still uncovered (a maximal matching)."""
    cover = set()
    matching = []
    for u, v in edges:
        if u not in cover and v not in cover:
            matching.append((u, v))
            cover.add(u)
            cover.add(v)
    return cover, matching


def is_cover(edges, cover):
    return all(u in cover or v in cover for u, v in edges)


def exact_vertex_cover(n, edges):
    """Smallest cover, by trying sizes 0, 1, 2, ... (fine for n up to about 20)."""
    for k in range(n + 1):
        for subset in itertools.combinations(range(n), k):
            if is_cover(edges, set(subset)):
                return set(subset)


def random_graph(n, p, rng):
    return [(u, v) for u in range(n) for v in range(u + 1, n) if rng.random() < p]


# The worked example of section 23.1
example = [(0, 1), (0, 2), (1, 3), (2, 3), (3, 4), (4, 5)]
cover, matching = approx_vertex_cover(example)
print("example edges:", example)
print("matching picked:", matching)
print("approx cover:", sorted(cover), "size", len(cover))
best = exact_vertex_cover(6, example)
print("optimal cover:", sorted(best), "size", len(best))
print()

rng = random.Random(23)
print(" n   edges  approx  optimal  ratio")
worst = 0.0
for trial in range(8):
    n = rng.randint(8, 14)
    edges = random_graph(n, 0.3, rng)
    a, _ = approx_vertex_cover(edges)
    o = exact_vertex_cover(n, edges)
    assert is_cover(edges, a)
    ratio = len(a) / len(o) if o else 1.0
    worst = max(worst, ratio)
    print(f"{n:2d}  {len(edges):5d}  {len(a):6d}  {len(o):7d}  {ratio:5.2f}")
print("worst ratio seen:", round(worst, 2), "(the theorem promises at most 2)")
print()

# A tight example: a perfect matching of k edges, nothing else.
k = 5
edges = [(2 * i, 2 * i + 1) for i in range(k)]
a, _ = approx_vertex_cover(edges)
o = exact_vertex_cover(2 * k, edges)
print(f"perfect matching of {k} edges: approx {len(a)}, optimal {len(o)}, ratio {len(a) / len(o):.1f}")
