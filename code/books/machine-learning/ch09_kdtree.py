"""Chapter 9.3: a k-d tree in d dimensions with exact nearest-neighbour search,
how many points it really looks at as d grows, and random-hyperplane hashing
(an approximate method) for comparison."""
import numpy as np


class Node:
    __slots__ = ("idx", "axis", "left", "right")

    def __init__(self, idx, axis, left, right):
        self.idx, self.axis, self.left, self.right = idx, axis, left, right


def build(X, ids, depth=0):
    """Split at the median of coordinate depth mod d. O(n log^2 n) as written."""
    if len(ids) == 0:
        return None
    axis = depth % X.shape[1]
    ids = ids[np.argsort(X[ids, axis], kind="stable")]
    mid = len(ids) // 2
    return Node(ids[mid], axis, build(X, ids[:mid], depth + 1), build(X, ids[mid + 1:], depth + 1))


def nearest(node, X, q, best, count):
    """best = [squared distance, index]; count[0] = points whose distance we computed."""
    if node is None:
        return
    count[0] += 1
    p = X[node.idx]
    d2 = float(((p - q) ** 2).sum())
    if d2 < best[0]:
        best[0], best[1] = d2, node.idx
    diff = q[node.axis] - p[node.axis]
    near, far = (node.left, node.right) if diff < 0 else (node.right, node.left)
    nearest(near, X, q, best, count)
    if diff * diff < best[0]:          # the ball around q crosses the splitting plane
        nearest(far, X, q, best, count)


def kd_query(root, X, q):
    best, count = [np.inf, -1], [0]
    nearest(root, X, q, best, count)
    return best[1], count[0]


rng = np.random.default_rng(2)
n = 10000
print(f"Exact nearest neighbour with a k-d tree, n = {n} uniform points, 50 queries")
print("    d   mean points examined   fraction of n   all answers correct")
for d in [2, 4, 8, 12, 16]:
    X = rng.uniform(0, 1, (n, d))
    root = build(X, np.arange(n))
    Q = rng.uniform(0, 1, (50, d))
    seen, ok = [], True
    for q in Q:
        i, c = kd_query(root, X, q)
        seen.append(c)
        ok &= (i == np.argmin(((X - q) ** 2).sum(1)))
    m = np.mean(seen)
    print(f"{d:5d}   {m:20.1f}   {m / n:13.4f}   {ok}")

print("\nHand-sized tree: 7 points in 2-D")
P = np.array([[2, 3], [5, 4], [9, 6], [4, 7], [8, 1], [7, 2], [6, 8]], dtype=float)
root = build(P, np.arange(7))


def show(node, depth=0):
    if node is None:
        return
    print("    " * depth + f"{tuple(int(v) for v in P[node.idx])} split on {'xy'[node.axis]}")
    show(node.left, depth + 1)
    show(node.right, depth + 1)


show(root)
i, c = kd_query(root, P, np.array([9.0, 2.0]))
print(f"query (9, 2): nearest {tuple(int(v) for v in P[i])}, examined {c} of 7 points")

print("\nApproximate search by random-hyperplane hashing (d = 32, n = 10000)")
print("Each table hashes a point to the signs of b random projections; a query")
print("compares only against points in the same bucket of some table.")
d = 32
X = rng.normal(0, 1, (n, d))
Q = X[:200] + rng.normal(0, 0.3, (200, d))     # queries near some data points
truth = np.array([np.argmin(((X - q) ** 2).sum(1)) for q in Q])
print("  bits  tables   mean candidates   recall of the true nearest")
for b, L in [(8, 1), (8, 4), (12, 4), (12, 16)]:
    tables = []
    for _ in range(L):
        R = rng.normal(0, 1, (d, b))
        keys = (X @ R > 0) @ (1 << np.arange(b))
        buckets = {}
        for j, key in enumerate(keys):
            buckets.setdefault(int(key), []).append(j)
        tables.append((R, buckets))
    found, cand = 0, 0
    for q, t in zip(Q, truth):
        C = set()
        for R, buckets in tables:
            C.update(buckets.get(int((q @ R > 0) @ (1 << np.arange(b))), []))
        C = np.fromiter(C, int)
        cand += len(C)
        if len(C) and C[np.argmin(((X[C] - q) ** 2).sum(1))] == t:
            found += 1
    print(f"  {b:4d}  {L:6d}   {cand / len(Q):15.1f}   {found / len(Q):.3f}")
