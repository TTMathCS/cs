"""Chapter 5, part 2: the n log n lower bound, inversions, adaptive sorting and introsort.

Self-contained: it repeats the few helpers it needs from ch05_comparison_sorts.py.
"""
import math
import random


# ---------- 1. The lower bound ceil(log2 n!) against merge sort's worst case ----------
def lower_bound(n):
    return math.ceil(math.lgamma(n + 1) / math.log(2)) if n > 1 else 0


def merge_sort_worst(n):
    """Worst-case comparisons of top-down merge sort: W(n) = W(floor) + W(ceil) + n - 1."""
    if n <= 1:
        return 0
    return merge_sort_worst(n // 2) + merge_sort_worst(n - n // 2) + n - 1


# ---------- 2. Inversions, counted by merge sort in O(n log n) ----------
def count_inversions(a):
    """Return (sorted copy, number of pairs i < j with a[i] > a[j])."""
    if len(a) <= 1:
        return list(a), 0
    mid = len(a) // 2
    left, x = count_inversions(a[:mid])
    right, y = count_inversions(a[mid:])
    out, i, j, cross = [], 0, 0, 0
    while i < len(left) and j < len(right):
        if right[j] < left[i]:
            out.append(right[j]); j += 1
            cross += len(left) - i         # right[j] is smaller than every left value still waiting
        else:
            out.append(left[i]); i += 1
    out += left[i:] + right[j:]
    return out, x + y + cross


def insertion_shifts(a):
    a, shifts = list(a), 0
    for i in range(1, len(a)):
        x, j = a[i], i - 1
        while j >= 0 and x < a[j]:
            a[j + 1] = a[j]; j -= 1; shifts += 1
        a[j + 1] = x
    return shifts


# ---------- 3. Natural merge sort: find the runs, then merge them ----------
def natural_merge_sort(a, c):
    """Split a into maximal non-decreasing runs (reversing strictly decreasing ones),
    then merge neighbouring runs until one is left. c[0] counts comparisons."""
    def lt(x, y):
        c[0] += 1
        return x < y

    runs, i, n = [], 0, len(a)
    while i < n:
        j = i + 1                                   # a[i..j-1] is the run so far
        if j < n and lt(a[j], a[j - 1]):            # strictly decreasing run
            while j + 1 < n and lt(a[j + 1], a[j]):
                j += 1
            j += 1
            runs.append(a[i:j][::-1])               # reversing keeps stability: no equal values
        else:
            j += 1                                  # (a[i+1] < a[i] was already tested false)
            while j < n and not lt(a[j], a[j - 1]):
                j += 1
            runs.append(a[i:j])
        i = j
    nruns = len(runs)
    while len(runs) > 1:
        merged = []
        for k in range(0, len(runs) - 1, 2):
            L, R, out, p, q = runs[k], runs[k + 1], [], 0, 0
            while p < len(L) and q < len(R):
                c[0] += 1
                if R[q] < L[p]:
                    out.append(R[q]); q += 1
                else:
                    out.append(L[p]); p += 1
            merged.append(out + L[p:] + R[q:])
        if len(runs) % 2:
            merged.append(runs[-1])
        runs = merged
    a[:] = runs[0] if runs else []
    return nruns


class Counted:
    """Wraps a value so we can count the comparisons Python's own sort makes."""
    calls = 0
    __slots__ = ("v",)
    def __init__(self, v):
        self.v = v
    def __lt__(self, other):
        Counted.calls += 1
        return self.v < other.v


def python_sort_comparisons(data):
    Counted.calls = 0
    sorted(Counted(v) for v in data)
    return Counted.calls


# ---------- 4. Introsort: quicksort with a depth limit, heapsort as the safety net ----------
def sift_down(a, lo, i, n, c):
    while True:
        big, l, r = i, 2 * i + 1, 2 * i + 2
        if l < n:
            c[0] += 1
            if a[lo + big] < a[lo + l]:
                big = l
        if r < n:
            c[0] += 1
            if a[lo + big] < a[lo + r]:
                big = r
        if big == i:
            return
        a[lo + i], a[lo + big] = a[lo + big], a[lo + i]
        i = big


def heapsort_range(a, lo, hi, c):
    n = hi - lo + 1
    for i in range(n // 2 - 1, -1, -1):
        sift_down(a, lo, i, n, c)
    for end in range(n - 1, 0, -1):
        a[lo], a[lo + end] = a[lo + end], a[lo]
        sift_down(a, lo, 0, end, c)


def partition_first(a, lo, hi, c):
    """Lomuto partition around the FIRST element (a deliberately naive pivot)."""
    a[lo], a[hi] = a[hi], a[lo]
    pivot, i = a[hi], lo
    for j in range(lo, hi):
        c[0] += 1
        if a[j] < pivot:
            a[i], a[j] = a[j], a[i]; i += 1
    a[i], a[hi] = a[hi], a[i]
    return i


def naive_quicksort(a, lo, hi, c):
    while lo < hi:                      # loop on the right part so Python's stack survives
        p = partition_first(a, lo, hi, c)
        naive_quicksort(a, lo, p - 1, c)
        lo = p + 1


def introsort(a, lo, hi, depth, c, stats):
    while lo < hi:
        if depth == 0:
            stats["heapsort calls"] += 1
            heapsort_range(a, lo, hi, c)
            return
        depth -= 1
        p = partition_first(a, lo, hi, c)
        introsort(a, lo, p - 1, depth, c, stats)
        lo = p + 1


# ---------- 5. Lomuto versus Hoare: swaps per partition ----------
def lomuto_swaps(a):
    hi, pivot, i, s = len(a) - 1, a[-1], 0, 0
    for j in range(hi):
        if a[j] < pivot:
            a[i], a[j] = a[j], a[i]; i += 1; s += 1
    a[i], a[hi] = a[hi], a[i]
    return s + 1


def hoare_swaps(a):
    pivot, i, j, s = a[0], -1, len(a), 0
    while True:
        i += 1
        while a[i] < pivot:
            i += 1
        j -= 1
        while pivot < a[j]:
            j -= 1
        if i >= j:
            return s
        a[i], a[j] = a[j], a[i]; s += 1


def main():
    rng = random.Random(5)

    print("n   ceil(log2 n!)  merge sort worst")
    for n in [2, 3, 4, 5, 8, 12, 16, 100, 1000]:
        print(f"{n:<4d}{lower_bound(n):>13d}{merge_sort_worst(n):>18d}")
    n = 10**6
    print(f"n = 10^6: ceil(log2 n!) = {lower_bound(n)}, n log2 n = {n * math.log2(n):.0f}, "
          f"merge sort worst = {merge_sort_worst(n)}")

    print("\ninversions")
    for a in [[2, 4, 1, 3, 5], [5, 4, 3, 2, 1], [1, 2, 3, 4, 5]]:
        print(f"  {a}: {count_inversions(a)[1]}")
    for _ in range(200):
        a = [rng.randint(0, 50) for _ in range(rng.randint(0, 60))]
        assert count_inversions(a)[1] == insertion_shifts(a)
        assert count_inversions(a)[0] == sorted(a)
    big = rng.sample(range(10**5), 10**5)
    print(f"  random permutation of 10^5: {count_inversions(big)[1]} inversions "
          f"(expected n(n-1)/4 = {10**5 * (10**5 - 1) // 4})")

    print("\nadaptive sorting, n = 10000 (comparisons)")
    n = 10000
    nearly = list(range(n))
    for _ in range(10):                       # ten random swaps
        i, j = rng.randrange(n), rng.randrange(n)
        nearly[i], nearly[j] = nearly[j], nearly[i]
    two_runs = list(range(0, n, 2)) + list(range(1, n, 2))
    cases = [("random", rng.sample(range(n), n)), ("sorted", list(range(n))),
             ("reversed", list(range(n, 0, -1))), ("10 swaps", nearly), ("two runs", two_runs)]
    print(f"  {'input':10s}{'runs':>6s}{'natural merge':>15s}{'Python sorted':>15s}")
    for name, d in cases:
        a, c = list(d), [0]
        runs = natural_merge_sort(a, c)
        assert a == sorted(d)
        print(f"  {name:10s}{runs:>6d}{c[0]:>15d}{python_sort_comparisons(d):>15d}")
    print(f"  ceil(log2 n!) = {lower_bound(n)}")

    print("\nintrosort versus naive quicksort (first element as pivot), sorted input")
    for n in [500, 2000]:
        a, c = list(range(n)), [0]
        naive_quicksort(a, 0, n - 1, c)
        b, d, stats = list(range(n)), [0], {"heapsort calls": 0}
        introsort(b, 0, n - 1, 2 * int(math.log2(n)), d, stats)
        assert a == b == list(range(n))
        print(f"  n = {n}: naive {c[0]} comparisons, introsort {d[0]} "
              f"(heapsort took over {stats['heapsort calls']} time)")

    print("\nswaps in one partition of a random array of 1000 (average of 2000 trials)")
    L = H = 0
    for _ in range(2000):
        a = rng.sample(range(1000), 1000)
        L += lomuto_swaps(list(a)); H += hoare_swaps(list(a))
    print(f"  Lomuto {L / 2000:.0f}, Hoare {H / 2000:.0f}")


if __name__ == "__main__":
    main()
