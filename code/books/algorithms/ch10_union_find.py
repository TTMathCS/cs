"""Chapter 10: union-find (disjoint sets) four ways, with step counters."""
import math
import random


class QuickFind:                       # id[x] = name of x's set
    def __init__(self, n):
        self.id, self.steps = list(range(n)), 0

    def find(self, x):
        self.steps += 1
        return self.id[x]

    def union(self, a, b):
        ra, rb = self.find(a), self.find(b)
        if ra != rb:
            for i in range(len(self.id)):      # rename every member of rb's set
                self.steps += 1
                if self.id[i] == rb:
                    self.id[i] = ra


class QuickUnion:                      # parent pointers, no balancing
    def __init__(self, n):
        self.parent, self.steps = list(range(n)), 0

    def find(self, x):
        while self.parent[x] != x:
            self.steps += 1
            x = self.parent[x]
        return x

    def union(self, a, b):
        ra, rb = self.find(a), self.find(b)
        if ra != rb:
            self.parent[rb] = ra


class UnionFind:                       # union by rank + path compression
    def __init__(self, n, by_rank=True, compress=True):
        self.parent, self.rank = list(range(n)), [0] * n
        self.by_rank, self.compress, self.steps = by_rank, compress, 0
        self.count = n                 # number of sets

    def find(self, x):
        root = x
        while self.parent[root] != root:
            self.steps += 1
            root = self.parent[root]
        if self.compress:
            while self.parent[x] != root:      # second pass: point at the root
                self.parent[x], x = root, self.parent[x]
        return root

    def union(self, a, b):
        ra, rb = self.find(a), self.find(b)
        if ra == rb:
            return False
        if self.by_rank:
            if self.rank[ra] < self.rank[rb]:
                ra, rb = rb, ra                # ra is the taller tree
            if self.rank[ra] == self.rank[rb]:
                self.rank[ra] += 1
        self.parent[rb] = ra
        self.count -= 1
        return True


def log_star(n):
    k = 0
    while n > 1:
        n, k = math.log2(n), k + 1
    return k


if __name__ == "__main__":
    uf = UnionFind(10)
    for a, b in [(4, 3), (3, 8), (6, 5), (9, 4), (2, 1), (8, 9), (5, 0), (7, 2), (6, 1)]:
        merged = uf.union(a, b)
        print(f"union({a},{b}) {'merged ' if merged else 'already '}  parent = {uf.parent}"
              f"  sets = {uf.count}")
    print("connected(0, 7):", uf.find(0) == uf.find(7), "  connected(0, 4):", uf.find(0) == uf.find(4))

    # the worst case for quick-union: union(0,1), union(0,2), ... builds a path
    n = 2000
    pairs = [(i, 0) for i in range(1, n)]      # parent[0] = i: the root climbs each time
    for name, s in [("quick-find", QuickFind(n)), ("quick-union", QuickUnion(n)),
                    ("by rank only", UnionFind(n, compress=False)),
                    ("compress only", UnionFind(n, by_rank=False)),
                    ("rank + compress", UnionFind(n))]:
        for a, b in pairs:
            s.union(a, b)
        for _ in range(n):
            s.find(0)
        print(f"{name:16} {n - 1} unions + {n} finds of 0: {s.steps:8} steps")

    # the worst case for union by rank alone: always join two equal trees
    n = 2 ** 11
    uf = UnionFind(n, compress=False)
    step = 1
    while step < n:
        for i in range(0, n, 2 * step):
            uf.union(i, i + step)
        step *= 2
    uf.steps = 0
    uf.find(n - 1)
    print(f"by rank only, n = {n} joined in equal pairs: find({n - 1}) takes "
          f"{uf.steps} steps = log2 n")

    random.seed(1975)
    n = 200000
    uf = UnionFind(n)
    for _ in range(n):
        uf.union(random.randrange(n), random.randrange(n))
    print(f"n = {n}, {n} random unions: {uf.count} sets left, max rank {max(uf.rank)}, "
          f"log2 n = {math.log2(n):.1f}")
    ranks = [uf.rank.count(r) for r in range(max(uf.rank) + 1)]
    print("nodes of rank r:", ranks, " bound n/2^r:", [n >> r for r in range(len(ranks))])
    print("log* of 2, 16, 65536, 10**80:", [log_star(x) for x in (2, 16, 65536, 10**80)])
