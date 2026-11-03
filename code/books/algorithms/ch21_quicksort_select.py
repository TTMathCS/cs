"""Chapter 21: randomized quicksort and quickselect, measured and compared with the exact expectations."""
import random
from fractions import Fraction

random.seed(21)


def quicksort(a, stats, depth=0):
    """Sort a list of distinct numbers with a random pivot; count comparisons and recursion depth."""
    stats["depth"] = max(stats["depth"], depth)
    if len(a) <= 1:
        return a
    pivot = random.choice(a)
    stats["comparisons"] += len(a) - 1          # every other element is compared with the pivot once
    left = [x for x in a if x < pivot]
    right = [x for x in a if x > pivot]
    return quicksort(left, stats, depth + 1) + [pivot] + quicksort(right, stats, depth + 1)


def quickselect(a, k, stats):
    """Return the k-th smallest (k = 1 is the minimum) of distinct numbers; count comparisons."""
    while True:
        if len(a) == 1:
            return a[0]
        pivot = random.choice(a)
        stats["comparisons"] += len(a) - 1
        left = [x for x in a if x < pivot]
        if k <= len(left):
            a = left
        elif k == len(left) + 1:
            return pivot
        else:
            k -= len(left) + 1
            a = [x for x in a if x > pivot]


def harmonic(n):
    return sum(Fraction(1, i) for i in range(1, n + 1))


def exact_quicksort(n_max):
    """C(n) = (n - 1) + (2/n) * (C(0) + ... + C(n - 1)), solved exactly with fractions."""
    c, prefix = [Fraction(0)], Fraction(0)
    for n in range(1, n_max + 1):
        prefix += c[-1]
        c.append(n - 1 + Fraction(2, n) * prefix)
    return c


def exact_quickselect(n_max):
    """Q[n][k] = expected comparisons to find rank k among n, with a uniformly random pivot."""
    q = [[0.0] * (n_max + 2) for _ in range(n_max + 1)]
    for n in range(2, n_max + 1):
        for k in range(1, n + 1):
            total = 0.0
            for p in range(1, n + 1):          # p = rank of the pivot
                if p > k:
                    total += q[p - 1][k]
                elif p < k:
                    total += q[n - p][k - p]
            q[n][k] = (n - 1) + total / n
    return q


print("Randomized quicksort: average comparisons against the exact expectation 2(n+1)H_n - 4n")
c = exact_quicksort(1000)
for n in (2, 3, 10, 100, 1000):
    closed = 2 * (n + 1) * harmonic(n) - 4 * n
    assert closed == c[n]
    trials = 2000 if n <= 100 else 300
    total = depth = 0
    for _ in range(trials):
        stats = {"comparisons": 0, "depth": 0}
        data = random.sample(range(10 * n), n)
        assert quicksort(data, stats) == sorted(data)
        total += stats["comparisons"]
        depth = max(depth, stats["depth"])
    print(f"  n = {n:4}: exact {float(closed):9.2f}   measured {total / trials:9.2f}"
          f"   deepest recursion seen {depth}")
print("  exact values as fractions: C(2) =", c[2], " C(3) =", c[3], " C(4) =", c[4])

print("\nThe pair (z_i, z_j) is compared with probability 2/(j - i + 1); n = 10, 100000 runs:")
counts = {}
for _ in range(100000):
    def qs(lo_hi):
        if len(lo_hi) <= 1:
            return
        p = random.choice(lo_hi)
        for x in lo_hi:
            if x != p:
                pair = (min(x, p), max(x, p))
                counts[pair] = counts.get(pair, 0) + 1
        qs([x for x in lo_hi if x < p])
        qs([x for x in lo_hi if x > p])
    qs(list(range(1, 11)))
for i, j in ((1, 2), (3, 4), (1, 3), (2, 7), (1, 10)):
    print(f"  z{i}, z{j}: predicted {2 / (j - i + 1):.4f}   measured {counts.get((i, j), 0) / 100000:.4f}")

print("\nRandomized quickselect: exact expected comparisons, worst rank, against the bound 4n")
q = exact_quickselect(200)
for n in (10, 100, 200):
    worst_k = max(range(1, n + 1), key=lambda k: q[n][k])
    trials = 3000
    total = 0
    for _ in range(trials):
        stats = {"comparisons": 0}
        data = random.sample(range(10 * n), n)
        assert quickselect(data, worst_k, stats) == sorted(data)[worst_k - 1]
        total += stats["comparisons"]
    print(f"  n = {n:3}: worst rank k = {worst_k:3}, exact {q[n][worst_k]:8.2f} = {q[n][worst_k] / n:.3f} n,"
          f"  measured {total / trials:8.2f},  minimum (k = 1) {q[n][1]:7.2f}")
