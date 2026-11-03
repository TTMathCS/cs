"""Chapter 6, part 2: selection.  Quickselect, median of medians, and top-k with a heap.

select(a, k) returns the k-th smallest item of a, counting from k = 0.
Every comparison goes through less() so we can count them.
"""
import heapq
import math
import random
from fractions import Fraction

C = [0]                                  # global comparison counter


def less(x, y):
    C[0] += 1
    return x < y


def partition3(a, pivot):
    """Split a into items < pivot, == pivot, > pivot.  Counted as one comparison per item
    (a three-way comparison), the model in which partitioning m items costs m - 1."""
    lo, eq, hi = [], [], []
    for x in a:
        if x is pivot:
            eq.append(x)
            continue
        C[0] += 1
        (lo if x < pivot else hi if pivot < x else eq).append(x)
    return lo, eq, hi


def quickselect(a, k, rng):
    while True:
        if len(a) == 1:
            return a[0]
        pivot = a[rng.randrange(len(a))]
        lo, eq, hi = partition3(a, pivot)
        if k < len(lo):
            a = lo
        elif k < len(lo) + len(eq):
            return pivot
        else:
            k -= len(lo) + len(eq)
            a = hi


def median_of_5(g):
    """Median of a group of at most 5 by insertion sort (at most 10 comparisons)."""
    g = list(g)
    for i in range(1, len(g)):
        x, j = g[i], i - 1
        while j >= 0 and less(x, g[j]):
            g[j + 1] = g[j]; j -= 1
        g[j + 1] = x
    return g[(len(g) - 1) // 2]


def mom_select(a, k):
    """Blum-Floyd-Pratt-Rivest-Tarjan selection: worst case O(n)."""
    if len(a) <= 5:
        return sorted(a)[k]  # tiny base case; its comparisons are not counted (at most 7)
    medians = [median_of_5(a[i:i + 5]) for i in range(0, len(a), 5)]
    pivot = mom_select(medians, (len(medians) - 1) // 2)
    lo, eq, hi = partition3(a, pivot)
    if k < len(lo):
        return mom_select(lo, k)
    if k < len(lo) + len(eq):
        return pivot
    return mom_select(hi, k - len(lo) - len(eq))


def expected_exact(n, k):
    """Exact expected comparisons of quickselect for rank k (0-based) among n distinct items,
    from the recurrence E(n,k) = n - 1 + (1/n) * sum over pivot ranks."""
    E = {}
    for m in range(1, n + 1):
        for j in range(m):
            if m == 1:
                E[m, j] = Fraction(0)
                continue
            s = Fraction(0)
            for p in range(m):          # pivot has rank p in this part
                if j < p:
                    s += E[p, j]
                elif j > p:
                    s += E[m - 1 - p, j - p - 1]
            E[m, j] = (m - 1) + s / m
    return E[n, k]


def knuth_formula(n, k):
    """2[(n+1)H_n - (n+3-k)H_{n+1-k} - (k+2)H_k + n + 3], k counted from 1."""
    H = lambda m: sum(Fraction(1, i) for i in range(1, m + 1))
    return 2 * ((n + 1) * H(n) - (n + 3 - k) * H(n + 1 - k) - (k + 2) * H(k) + n + 3)


def top_k_heap(xs, k):
    """The k largest items, using a min-heap of size k: O(n log k)."""
    h = []
    for x in xs:
        if len(h) < k:
            heapq.heappush(h, x)
        elif x > h[0]:
            heapq.heapreplace(h, x)     # drop the smallest of the k kept so far
    return sorted(h, reverse=True)


def main():
    rng = random.Random(7)

    # 1. Both selection algorithms agree with sorting, duplicates included.
    for _ in range(500):
        a = [rng.randrange(30) for _ in range(rng.randrange(1, 80))]
        k = rng.randrange(len(a))
        assert quickselect(list(a), k, rng) == sorted(a)[k] == mom_select(list(a), k)
    print("quickselect and median of medians agree with sorted(a)[k] on 500 random lists")

    # 2. The exact expectation, from the recurrence, matches Knuth's closed form.
    for n in range(1, 13):
        for k in range(n):
            assert expected_exact(n, k) == knuth_formula(n, k + 1)
    print("exact expectation = Knuth's formula for all n <= 12, every k")
    print("  n = 3, median:", expected_exact(3, 1), "  n = 4, smallest:", expected_exact(4, 0))

    # 3. Comparisons per item.
    print("\ncomparisons / n  (median, random distinct data)")
    print(f"  {'n':>7s} {'quickselect avg':>16s} {'2(1+ln2)':>9s} {'median of medians':>18s}")
    for n in [1000, 10000, 100000]:
        a = rng.sample(range(10 * n), n)
        tot = 0
        trials = 20 if n < 100000 else 5
        for _ in range(trials):
            C[0] = 0
            quickselect(a, n // 2, rng)
            tot += C[0]
        C[0] = 0
        m = mom_select(a, n // 2)
        assert m == sorted(a)[n // 2]
        print(f"  {n:7d} {tot / trials / n:16.3f} {2 * (1 + math.log(2)):9.3f} {C[0] / n:18.3f}")

    # 4. Median of medians on sorted input, where a fixed-pivot quickselect would be quadratic.
    n = 100000
    C[0] = 0
    mom_select(list(range(n)), n // 2)
    print(f"  median of medians on sorted input, n = {n}: {C[0] / n:.3f} comparisons per item")

    # 5. Top-k.
    xs = [rng.randrange(10**6) for _ in range(100000)]
    assert top_k_heap(xs, 10) == sorted(xs, reverse=True)[:10] == heapq.nlargest(10, xs)
    print("\ntop 5 of 100000:", top_k_heap(xs, 5))


if __name__ == "__main__":
    main()
