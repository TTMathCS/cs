"""Chapter 9: in-place heapsort (Williams 1964, Floyd 1964) and d-ary heaps."""
import random


def sift_down(a, i, n, d, count):
    """Max-heap sift down in a[0:n] with d children per node."""
    while True:
        first = d * i + 1
        if first >= n:
            return
        m = first                          # the largest child
        for c in range(first + 1, min(first + d, n)):
            count[0] += 1
            if a[c] > a[m]:
                m = c
        count[0] += 1
        if a[m] <= a[i]:
            return
        a[i], a[m] = a[m], a[i]
        i = m


def heapsort(a, d=2, trace=False):
    n, count = len(a), [0]
    for i in reversed(range((n - 2) // d + 1)):    # build a max-heap
        sift_down(a, i, n, d, count)
    if trace:
        print("max-heap   :", a)
    for end in range(n - 1, 0, -1):
        a[0], a[end] = a[end], a[0]        # the largest goes to its final place
        sift_down(a, 0, end, d, count)
        if trace:
            print(f"after {n - end} out:", a[:end], "|", a[end:])
    return count[0]


def sift_up(a, i, d, count):               # min-heap, for the push test
    while i > 0:
        p = (i - 1) // d
        count[0] += 1
        if a[p] <= a[i]:
            return
        a[i], a[p] = a[p], a[i]
        i = p


def pop_min(a, d, count):
    top, last = a[0], a.pop()
    if a:
        a[0] = last
        i, n = 0, len(a)
        while True:
            first = d * i + 1
            if first >= n:
                break
            m = first
            for c in range(first + 1, min(first + d, n)):
                count[0] += 1
                if a[c] < a[m]:
                    m = c
            count[0] += 1
            if a[m] >= a[i]:
                break
            a[i], a[m] = a[m], a[i]
            i = m
    return top


if __name__ == "__main__":
    a = [4, 10, 3, 5, 1, 8]
    heapsort(a, trace=True)
    print("sorted     :", a)

    random.seed(1964)
    n = 50000
    data = [random.random() for _ in range(n)]
    for d in [2, 3, 4]:
        a = data[:]
        c = heapsort(a, d)
        assert a == sorted(data)
        print(f"heapsort d = {d}: {c / n:.1f} comparisons per item")

    print("d   push comparisons   pop comparisons   (per operation, n = 50000)")
    keys = [random.random() for _ in range(n)]
    for d in [2, 4, 8, 16]:
        h, cu, cd = [], [0], [0]
        for k in sorted(keys, reverse=True):   # decreasing: every push climbs
            h.append(k)
            sift_up(h, len(h) - 1, d, cu)
        out = [pop_min(h, d, cd) for _ in range(n)]
        assert out == sorted(keys)
        print(f"{d:2}  {cu[0] / n:17.2f}  {cd[0] / n:16.2f}")
