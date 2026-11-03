"""Chapter 8: a B-tree with minimum degree t (every node but the root holds
t-1 to 2t-1 keys), insertion by splitting full nodes on the way down."""
import bisect
import math
import random


class BNode:
    def __init__(self, leaf=True):
        self.keys, self.kids, self.leaf = [], [], leaf


class BTree:
    def __init__(self, t):
        self.t, self.root, self.reads = t, BNode(), 0

    def search(self, k, x=None):
        x = x or self.root
        self.reads += 1                    # one node = one disk block read
        i = bisect.bisect_left(x.keys, k)
        if i < len(x.keys) and x.keys[i] == k:
            return True
        return False if x.leaf else self.search(k, x.kids[i])

    def split_child(self, x, i):
        t, y = self.t, x.kids[i]           # y is full: 2t-1 keys
        z = BNode(y.leaf)
        x.keys.insert(i, y.keys[t - 1])    # the middle key moves up
        x.kids.insert(i + 1, z)
        z.keys, y.keys = y.keys[t:], y.keys[:t - 1]
        if not y.leaf:
            z.kids, y.kids = y.kids[t:], y.kids[:t]

    def insert(self, k):
        r = self.root
        if len(r.keys) == 2 * self.t - 1:  # full root: the tree grows a level
            s = BNode(leaf=False)
            s.kids.append(r)
            self.root = s
            self.split_child(s, 0)
        x = self.root
        while not x.leaf:                  # never step into a full node
            i = bisect.bisect_right(x.keys, k)
            if len(x.kids[i].keys) == 2 * self.t - 1:
                self.split_child(x, i)
                if k > x.keys[i]:
                    i += 1
            x = x.kids[i]
        bisect.insort(x.keys, k)

    def height(self):
        h, x = 0, self.root
        while not x.leaf:
            h, x = h + 1, x.kids[0]
        return h

    def show(self, x=None):
        x = x or self.root
        if x.leaf:
            return "[" + " ".join(map(str, x.keys)) + "]"
        parts = [self.show(x.kids[0])]
        for key, kid in zip(x.keys, x.kids[1:]):
            parts += [str(key), self.show(kid)]
        return "{" + " ".join(parts) + "}"


if __name__ == "__main__":
    b = BTree(t=2)                         # a 2-3-4 tree: 1 to 3 keys per node
    for k in [10, 20, 30, 40, 50, 60, 70, 80, 90, 5, 15]:
        b.insert(k)
        print(f"insert {k:2}: {b.show()}")

    random.seed(1970)
    n = 500_000
    b = BTree(t=50)                        # up to 99 keys in a node
    for k in random.sample(range(10 * n), n):
        b.insert(k)
    b.reads = 0
    b.search(-1)                           # a miss walks root to leaf
    bound = math.log((n + 1) / 2, 50)
    print(f"t = 50, n = {n}: height {b.height()}, "
          f"nodes read by a search {b.reads}, bound log_t((n+1)/2) = {bound:.2f}")
    print(f"a balanced binary tree on n keys: height >= {math.ceil(math.log2(n + 1)) - 1}")
