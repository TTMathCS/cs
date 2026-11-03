"""Chapter 5: the comparison sorts, built from scratch, each counting its comparisons.

Every sort takes a list `a` and a counter `c` (a one-element list, so the sort can add to it)
and sorts `a` in place. We check each one against Python's sorted() on many random lists,
then compare how many comparisons each needs on random, sorted and reversed input.
"""
import math
import random


def less(x, y, c):
    """The one operation a comparison sort may use: is x < y?  Counted."""
    c[0] += 1
    return x < y


def selection_sort(a, c):
    n = len(a)
    for i in range(n - 1):
        m = i                       # position of the smallest seen so far in a[i..n-1]
        for j in range(i + 1, n):
            if less(a[j], a[m], c):
                m = j
        a[i], a[m] = a[m], a[i]


def insertion_sort(a, c, lo=0, hi=None):
    if hi is None:
        hi = len(a) - 1
    for i in range(lo + 1, hi + 1):
        x = a[i]
        j = i - 1
        while j >= lo and less(x, a[j], c):   # shift bigger values one place right
            a[j + 1] = a[j]
            j -= 1
        a[j + 1] = x


def bubble_sort(a, c):
    n = len(a)
    for end in range(n - 1, 0, -1):
        swapped = False
        for j in range(end):
            if less(a[j + 1], a[j], c):
                a[j], a[j + 1] = a[j + 1], a[j]
                swapped = True
        if not swapped:             # a pass with no swap: already sorted
            return


def merge_sort(a, c):
    if len(a) <= 1:
        return
    mid = len(a) // 2
    left, right = a[:mid], a[mid:]
    merge_sort(left, c)
    merge_sort(right, c)
    i = j = k = 0
    while i < len(left) and j < len(right):
        if less(right[j], left[i], c):        # take from the right only if strictly smaller: stable
            a[k] = right[j]; j += 1
        else:
            a[k] = left[i]; i += 1
        k += 1
    a[k:] = left[i:] + right[j:]


def lomuto_partition(a, lo, hi, c):
    """Pivot a[hi]. Returns p with a[lo..p-1] < pivot <= a[p+1..hi]... and a[p] == pivot."""
    pivot = a[hi]
    i = lo                          # a[lo..i-1] holds values < pivot
    for j in range(lo, hi):
        if less(a[j], pivot, c):
            a[i], a[j] = a[j], a[i]
            i += 1
    a[i], a[hi] = a[hi], a[i]
    return i


def quicksort_lomuto(a, c, rng, lo=0, hi=None):
    if hi is None:
        hi = len(a) - 1
    while lo < hi:
        r = rng.randint(lo, hi)     # random pivot, moved to the end
        a[r], a[hi] = a[hi], a[r]
        p = lomuto_partition(a, lo, hi, c)
        if p - lo < hi - p:         # recurse on the smaller side, loop on the larger:
            quicksort_lomuto(a, c, rng, lo, p - 1)   # the stack stays O(log n) deep
            lo = p + 1
        else:
            quicksort_lomuto(a, c, rng, p + 1, hi)
            hi = p - 1


def hoare_partition(a, lo, hi, c):
    """Pivot a[lo]. Returns j with every value in a[lo..j] <= every value in a[j+1..hi]."""
    pivot = a[lo]
    i, j = lo - 1, hi + 1
    while True:
        i += 1
        while less(a[i], pivot, c):
            i += 1
        j -= 1
        while less(pivot, a[j], c):
            j -= 1
        if i >= j:
            return j
        a[i], a[j] = a[j], a[i]


def quicksort_hoare(a, c, rng, lo=0, hi=None):
    if hi is None:
        hi = len(a) - 1
    if lo < hi:
        r = rng.randint(lo, hi)
        a[r], a[lo] = a[lo], a[r]
        j = hoare_partition(a, lo, hi, c)
        quicksort_hoare(a, c, rng, lo, j)
        quicksort_hoare(a, c, rng, j + 1, hi)


def sift_down(a, i, n, c, lo=0):
    """Max-heap a[lo..lo+n-1], children of i (relative) at 2i+1, 2i+2."""
    while True:
        big = i
        l, r = 2 * i + 1, 2 * i + 2
        if l < n and less(a[lo + big], a[lo + l], c):
            big = l
        if r < n and less(a[lo + big], a[lo + r], c):
            big = r
        if big == i:
            return
        a[lo + i], a[lo + big] = a[lo + big], a[lo + i]
        i = big


def heapsort(a, c, lo=0, hi=None):
    if hi is None:
        hi = len(a) - 1
    n = hi - lo + 1
    for i in range(n // 2 - 1, -1, -1):      # build a max-heap bottom up
        sift_down(a, i, n, c, lo)
    for end in range(n - 1, 0, -1):          # move the max to the end, shrink the heap
        a[lo], a[lo + end] = a[lo + end], a[lo]
        sift_down(a, 0, end, c, lo)


def run(sort, data, rng):
    a, c = list(data), [0]
    if sort in (quicksort_lomuto, quicksort_hoare):
        sort(a, c, rng)
    else:
        sort(a, c)
    return a, c[0]


SORTS = [("selection", selection_sort), ("insertion", insertion_sort),
         ("bubble", bubble_sort), ("merge", merge_sort),
         ("quick (Lomuto)", quicksort_lomuto), ("quick (Hoare)", quicksort_hoare),
         ("heapsort", heapsort)]


def main():
    rng = random.Random(2026)

    # 1. Correctness: every sort agrees with sorted() on 300 random lists, duplicates included.
    for name, sort in SORTS:
        for trial in range(300):
            n = rng.randint(0, 40)
            data = [rng.randint(0, 9) for _ in range(n)]
            assert run(sort, data, rng)[0] == sorted(data), name
    print("all 7 sorts agree with sorted() on 300 random lists each")

    # 2. Stability: sort (key, original position) pairs by key only.
    class Item:
        def __init__(self, key, pos):
            self.key, self.pos = key, pos
        def __lt__(self, other):
            return self.key < other.key
    data = [Item(rng.randint(0, 4), i) for i in range(200)]
    print("\nstable?")
    for name, sort in SORTS:
        out = run(sort, data, rng)[0]
        ok = all(out[i].key < out[i + 1].key or out[i].pos < out[i + 1].pos
                 for i in range(len(out) - 1))
        print(f"  {name:15s} {'yes' if ok else 'no'}")

    # 3. Comparisons for n = 1000.
    n = 1000
    rand = rng.sample(range(n), n)
    inputs = [("random", rand), ("sorted", list(range(n))), ("reversed", list(range(n, 0, -1)))]
    print(f"\ncomparisons for n = {n}:")
    print(f"  {'sort':15s}" + "".join(f"{lab:>10s}" for lab, _ in inputs))
    for name, sort in SORTS:
        row = [run(sort, d, rng)[1] for _, d in inputs]
        print(f"  {name:15s}" + "".join(f"{x:10d}" for x in row))
    lb = math.ceil(math.lgamma(n + 1) / math.log(2))
    print(f"  lower bound ceil(log2 {n}!) = {lb}")

    # 4. Randomized quicksort: average over 200 runs versus the exact expectation 2(n+1)H_n - 4n.
    H = sum(1 / k for k in range(1, n + 1))
    avg = sum(run(quicksort_lomuto, rand, rng)[1] for _ in range(200)) / 200
    print(f"\nrandom-pivot quicksort, n = {n}: average {avg:.0f} comparisons over 200 runs; "
          f"2(n+1)H_n - 4n = {2 * (n + 1) * H - 4 * n:.0f}; "
          f"1.386 n log2 n = {2 * math.log(2) * n * math.log2(n):.0f}")


if __name__ == "__main__":
    main()
