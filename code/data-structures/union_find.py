class UnionFind:
    """Disjoint sets: which group is each item in? Union by size and path compression."""
    def __init__(self, n):
        self.parent = list(range(n))         # each item starts as its own group's leader
        self.size = [1] * n
        self.groups = n

    def find(self, x):
        root = x
        while self.parent[root] != root:     # walk up to the leader
            root = self.parent[root]
        while self.parent[x] != root:        # path compression: point everything on the way at it
            self.parent[x], x = root, self.parent[x]
        return root

    def union(self, a, b):
        """Joins the groups of a and b; returns False if they were already together."""
        ra, rb = self.find(a), self.find(b)
        if ra == rb:
            return False
        if self.size[ra] < self.size[rb]:    # hang the smaller tree under the bigger one
            ra, rb = rb, ra
        self.parent[rb] = ra
        self.size[ra] += self.size[rb]
        self.groups -= 1
        return True

    def connected(self, a, b):
        return self.find(a) == self.find(b)


if __name__ == "__main__":
    uf = UnionFind(10)
    for a, b in [(0, 1), (2, 3), (1, 3), (5, 6), (7, 8), (8, 9), (3, 0)]:
        print(f"union({a}, {b}) -> {uf.union(a, b)}")
    print(uf.connected(0, 2), uf.connected(4, 5), uf.connected(7, 9))
    print("groups:", uf.groups, "size of 0's group:", uf.size[uf.find(0)])
