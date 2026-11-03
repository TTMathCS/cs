"""Chapter 21: a splay tree, with every access checked against the access lemma."""
import random
from math import log2

random.seed(1985)


class Node:
    __slots__ = ("key", "left", "right", "parent", "size")

    def __init__(self, key):
        self.key, self.left, self.right, self.parent, self.size = key, None, None, None, 1


def size(t):
    return t.size if t else 0


def fix(t):
    t.size = 1 + size(t.left) + size(t.right)


class SplayTree:
    def __init__(self):
        self.root = None
        self.rotations = 0

    def rotate(self, x):
        """Rotate x above its parent, keeping the in-order sequence."""
        p, g = x.parent, x.parent.parent
        if p.left is x:
            p.left, x.right = x.right, p
            if p.left:
                p.left.parent = p
        else:
            p.right, x.left = x.left, p
            if p.right:
                p.right.parent = p
        p.parent, x.parent = x, g
        if g is None:
            self.root = x
        elif g.left is p:
            g.left = x
        else:
            g.right = x
        fix(p)
        fix(x)
        self.rotations += 1

    def splay(self, x):
        while x.parent:
            p, g = x.parent, x.parent.parent
            if g is None:                                   # zig
                self.rotate(x)
            elif (g.left is p) == (p.left is x):            # zig-zig: rotate the parent first
                self.rotate(p)
                self.rotate(x)
            else:                                           # zig-zag
                self.rotate(x)
                self.rotate(x)

    def insert(self, key):
        if self.root is None:
            self.root = Node(key)
            return
        t = self.root
        while True:
            t.size += 1
            nxt = t.left if key < t.key else t.right
            if nxt is None:
                x = Node(key)
                x.parent = t
                if key < t.key:
                    t.left = x
                else:
                    t.right = x
                break
            t = nxt
        self.splay(x)

    def find(self, key):
        t = self.root
        while t.key != key:
            t = t.left if key < t.key else t.right
        self.splay(t)
        return t


def run(name, n, accesses):
    """Splay each key; check  actual rotations + change in Phi  <=  3 (r(root) - r(x)) + 1.
    Phi = sum over all nodes of r(v) = log2(size of v's subtree). Splaying x changes the subtree
    of a node only if the node lies on the path from the root to x, so only those terms change."""
    tree = SplayTree()
    for k in range(1, n + 1):           # increasing keys: each new key becomes the root, the tree is a path
        tree.insert(k)
    worst_slack, total_actual, total_bound = float("inf"), 0, 0.0
    for key in accesses:
        path, t = [], tree.root
        while True:
            path.append(t)
            if t.key == key:
                break
            t = t.left if key < t.key else t.right
        phi_before = sum(log2(v.size) for v in path)
        bound = 3 * (log2(n) - log2(t.size)) + 1           # the access lemma, r(root) = log2 n
        before = tree.rotations
        tree.find(key)
        actual = tree.rotations - before
        amortized = actual + sum(log2(v.size) for v in path) - phi_before
        worst_slack = min(worst_slack, bound - amortized)
        total_actual += actual
        total_bound += bound
    m = len(accesses)
    print(f"  {name:<27} m = {m:4}, rotations {total_actual:6}, per access {total_actual / m:6.2f};"
          f" lemma's smallest slack {worst_slack:.3f}")


n = 1000
print(f"Splay tree on keys 1..{n}, built as a path by inserting 1, 2, ..., n; 3 log2 n + 1 = {3 * log2(n) + 1:.2f}")
run("access 1, 2, ..., n in order", n, list(range(1, n + 1)))
run("uniform random keys", n, [random.randint(1, n) for _ in range(5000)])
run("one key over and over", n, [1] + [500] * 4999)
run("90% of accesses to 10 keys", n, [random.randint(1, 10) if random.random() < 0.9
                                       else random.randint(1, n) for _ in range(5000)])
