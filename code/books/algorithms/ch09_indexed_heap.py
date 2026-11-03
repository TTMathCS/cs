"""Chapter 9: an indexed min-heap with decrease-key, and Dijkstra's algorithm
with it and with Python's heapq plus lazy deletion."""
import heapq
import random


class IndexedHeap:
    """Items are 0..n-1, each with a priority. pos[item] = its index in heap."""

    def __init__(self, n):
        self.heap, self.prio, self.pos = [], [None] * n, [-1] * n

    def __contains__(self, item):
        return self.pos[item] != -1

    def _swap(self, i, j):
        h = self.heap
        h[i], h[j] = h[j], h[i]
        self.pos[h[i]], self.pos[h[j]] = i, j

    def _up(self, i):
        while i > 0 and self.prio[self.heap[i]] < self.prio[self.heap[(i - 1) // 2]]:
            self._swap(i, (i - 1) // 2)
            i = (i - 1) // 2

    def _down(self, i):
        n = len(self.heap)
        while True:
            m = i
            for c in (2 * i + 1, 2 * i + 2):
                if c < n and self.prio[self.heap[c]] < self.prio[self.heap[m]]:
                    m = c
            if m == i:
                return
            self._swap(i, m)
            i = m

    def push(self, item, p):
        self.prio[item] = p
        self.pos[item] = len(self.heap)
        self.heap.append(item)
        self._up(self.pos[item])

    def decrease_key(self, item, p):
        assert p <= self.prio[item]
        self.prio[item] = p
        self._up(self.pos[item])           # only up: the key got smaller

    def pop(self):
        top = self.heap[0]
        self._swap(0, len(self.heap) - 1)
        self.heap.pop()
        self.pos[top] = -1
        if self.heap:
            self._down(0)
        return top, self.prio[top]

    def __len__(self):
        return len(self.heap)


def dijkstra_indexed(adj, s):
    dist = [float("inf")] * len(adj)
    dist[s] = 0
    pq, stats = IndexedHeap(len(adj)), {"push": 0, "decrease": 0, "pop": 0}
    pq.push(s, 0)
    stats["push"] += 1
    while pq:
        u, d = pq.pop()
        stats["pop"] += 1
        for v, w in adj[u]:
            if d + w < dist[v]:
                if v in pq:
                    pq.decrease_key(v, d + w)
                    stats["decrease"] += 1
                else:
                    pq.push(v, d + w)
                    stats["push"] += 1
                dist[v] = d + w
    return dist, stats


def dijkstra_lazy(adj, s):
    dist = [float("inf")] * len(adj)
    dist[s] = 0
    pq, stats = [(0, s)], {"push": 1, "stale": 0, "pop": 0, "max size": 1}
    while pq:
        d, u = heapq.heappop(pq)
        stats["pop"] += 1
        if d > dist[u]:                    # an old, outdated entry: skip it
            stats["stale"] += 1
            continue
        for v, w in adj[u]:
            if d + w < dist[v]:
                dist[v] = d + w
                heapq.heappush(pq, (d + w, v))
                stats["push"] += 1
                stats["max size"] = max(stats["max size"], len(pq))
    return dist, stats


if __name__ == "__main__":
    h = IndexedHeap(5)
    for item, p in [(0, 50), (1, 30), (2, 40), (3, 20), (4, 60)]:
        h.push(item, p)
    print("heap of items:", h.heap, " positions:", h.pos)
    h.decrease_key(4, 10)
    print("after decrease_key(4, 10):", h.heap, " positions:", h.pos)
    print("pops:", [h.pop() for _ in range(5)])

    # a small road map: 0 = start
    edges = [(0, 1, 7), (0, 2, 9), (0, 5, 14), (1, 2, 10), (1, 3, 15),
             (2, 3, 11), (2, 5, 2), (3, 4, 6), (4, 5, 9)]
    adj = [[] for _ in range(6)]
    for u, v, w in edges:
        adj[u].append((v, w))
        adj[v].append((u, w))
    print("distances from 0:", dijkstra_indexed(adj, 0)[0])

    random.seed(1959)
    n, m = 20000, 100000
    adj = [[] for _ in range(n)]
    for _ in range(m):
        u, v = random.randrange(n), random.randrange(n)
        w = random.randint(1, 100)
        adj[u].append((v, w))
        adj[v].append((u, w))
    d1, s1 = dijkstra_indexed(adj, 0)
    d2, s2 = dijkstra_lazy(adj, 0)
    print("same distances:", d1 == d2)
    print("indexed heap:", s1)
    print("heapq, lazy  :", s2)
