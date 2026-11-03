# Chapter 6: how much does alpha-beta prune? Uniform trees with random leaf values.
# Leaves of a tree with branching factor b and depth d are numbered 0 .. b^d - 1 in left-to-right order.
import numpy as np


def level_values(leaves, b, d):
    """Minimax value of every node, level by level (root is MAX, levels alternate)."""
    vals = [None] * (d + 1)
    vals[d] = leaves
    for depth in range(d - 1, -1, -1):
        children = vals[depth + 1].reshape(-1, b)
        vals[depth] = children.max(axis=1) if depth % 2 == 0 else children.min(axis=1)
    return vals


def alphabeta(vals, b, d, order, depth=0, idx=0, alpha=-np.inf, beta=np.inf, count=None):
    """Alpha-beta on the implicit tree. order(depth, idx) gives the order in which to try the children.
    count[0] is the number of leaves evaluated."""
    if depth == d:
        count[0] += 1
        return vals[d][idx]
    maximizing = depth % 2 == 0
    v = -np.inf if maximizing else np.inf
    for c in order(depth, idx):
        child = idx * b + c
        w = alphabeta(vals, b, d, order, depth + 1, child, alpha, beta, count)
        if maximizing:
            v = max(v, w)
            if v >= beta:
                return v
            alpha = max(alpha, v)
        else:
            v = min(v, w)
            if v <= alpha:
                return v
            beta = min(beta, v)
    return v


def experiment(b, d, rng, trials=5):
    rows = []
    for _ in range(trials):
        leaves = rng.random(b ** d)
        vals = level_values(leaves, b, d)

        def best(depth, idx):              # oracle: best child first (needs the true values)
            ch = vals[depth + 1][idx * b: idx * b + b]
            return list(np.argsort(-ch) if depth % 2 == 0 else np.argsort(ch))

        def worst(depth, idx):
            return best(depth, idx)[::-1]

        def natural(depth, idx):           # left to right: random order, since the values are random
            return range(b)

        result = {}
        for name, order in (("best", best), ("random", natural), ("worst", worst)):
            count = [0]
            v = alphabeta(vals, b, d, order, count=count)
            assert v == vals[0][0]            # alpha-beta returns the minimax value
            result[name] = count[0]
        rows.append(result)
    return {k: sum(r[k] for r in rows) / trials for k in rows[0]}


def pearl_branching(b):
    """Pearl (1982): alpha-beta's asymptotic branching factor on random trees is x/(1-x),
    where x is the root in (0,1) of x^b + x - 1 = 0."""
    lo, hi = 0.0, 1.0
    for _ in range(60):
        mid = (lo + hi) / 2
        lo, hi = (mid, hi) if mid ** b + mid - 1 < 0 else (lo, mid)
    return lo / (1 - lo)


rng = np.random.default_rng(1975)
print(" b  d   all leaves   worst order  random order   best order   b^ceil(d/2)+b^floor(d/2)-1")
for b, d in ((2, 10), (3, 8), (4, 7), (5, 6), (8, 5), (10, 4)):
    r = experiment(b, d, rng)
    formula = b ** ((d + 1) // 2) + b ** (d // 2) - 1
    print(f"{b:2d} {d:2d}  {b ** d:11d}  {r['worst']:12.0f}  {r['random']:12.1f}  {r['best']:11.0f}  {formula:11d}")

print("\neffective branching factor of random-order alpha-beta, measured on b=4, depth 4 to 8 (one tree each):")
b = 4
prev = None
for d in range(4, 9):
    leaves = rng.random(b ** d)
    vals = level_values(leaves, b, d)
    count = [0]
    alphabeta(vals, b, d, lambda depth, idx: range(b), count=count)
    ratio = "" if prev is None else f"   ratio to depth {d - 1}: {count[0] / prev:.2f}"
    print(f"  depth {d}: {count[0]:6d} leaves{ratio}")
    prev = count[0]
print(f"  Pearl's asymptotic value for b=4: {pearl_branching(4):.3f};  b^(3/4) = {4 ** 0.75:.3f};"
      f"  sqrt(b) = {4 ** 0.5:.3f}")
