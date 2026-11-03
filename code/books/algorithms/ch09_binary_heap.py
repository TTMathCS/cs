"""Chapter 9: a binary min-heap in a Python list, from scratch, with a
comparison counter to check that build-heap is linear."""
import heapq
import math
import random


class MinHeap:
    def __init__(self, items=()):
        self.a = list(items)
        self.comparisons = 0
        for i in reversed(range(len(self.a) // 2)):   # build-heap: bottom up
            self._down(i)

    def _less(self, i, j):
        self.comparisons += 1
        return self.a[i] < self.a[j]

    def _up(self, i):                  # sift up: swap with parent while smaller
        while i > 0:
            p = (i - 1) // 2
            if not self._less(i, p):
                break
            self.a[i], self.a[p] = self.a[p], self.a[i]
            i = p

    def _down(self, i):                # sift down: swap with the smaller child
        n = len(self.a)
        while True:
            l, r, m = 2 * i + 1, 2 * i + 2, i
            if l < n and self._less(l, m):
                m = l
            if r < n and self._less(r, m):
                m = r
            if m == i:
                return
            self.a[i], self.a[m] = self.a[m], self.a[i]
            i = m

    def push(self, x):
        self.a.append(x)
        self._up(len(self.a) - 1)

    def peek(self):
        return self.a[0]

    def pop(self):
        a = self.a
        top, last = a[0], a.pop()
        if a:
            a[0] = last                # move the last leaf to the root ...
            self._down(0)              # ... and let it sink
        return top

    def __len__(self):
        return len(self.a)


def is_heap(a):
    return all(a[(i - 1) // 2] <= a[i] for i in range(1, len(a)))


if __name__ == "__main__":
    h = MinHeap()
    for x in [5, 3, 8, 1, 9, 2]:
        h.push(x)
        print(f"push {x}: {h.a}")
    while h:
        x = h.pop()
        print(f"pop -> {x}: {h.a}")

    a = [9, 4, 7, 1, 8, 2, 6, 3, 5]
    print("build-heap of", a, "->", MinHeap(a).a)

    random.seed(1964)
    print("     n   build: comparisons  per n   n pushes: comparisons  per n")
    for n in [1000, 10000, 100000]:
        data = [random.random() for _ in range(n)]
        b = MinHeap(data)
        p = MinHeap()
        for x in data:
            p.push(x)
        assert is_heap(b.a) and is_heap(p.a)
        print(f"{n:6}   {b.comparisons:18}  {b.comparisons / n:5.2f}"
              f"   {p.comparisons:20}  {p.comparisons / n:5.2f}")
    data = list(range(100000, 0, -1))  # decreasing: every push climbs to the root
    p = MinHeap()
    for x in data:
        p.push(x)
    print(f"n pushes of decreasing keys, n = 100000: {p.comparisons / 100000:.2f} "
          f"comparisons per push, log2 n = {math.log2(100000):.2f}")

    ours, data = MinHeap(data), data[:]
    heapq.heapify(data)
    same = all(ours.pop() == heapq.heappop(data) for _ in range(len(data)))
    print("pops agree with heapq:", same)
