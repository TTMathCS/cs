"""Chapter 8: splay trees (Sleator and Tarjan, 1985): every access moves the
key to the root by zig, zig-zig and zig-zag steps."""
import random


class Node:
    def __init__(self, key):
        self.key, self.left, self.right, self.parent = key, None, None, None


class SplayTree:
    def __init__(self):
        self.root, self.rotations, self.log = None, 0, []

    def _rotate(self, x):                  # lift x above its parent
        p, g = x.parent, x.parent.parent
        if x is p.left:
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
        self.rotations += 1

    def splay(self, x):
        while x.parent:
            p, g = x.parent, x.parent.parent
            if g is None:
                self.log.append("zig")
                self._rotate(x)
            elif (x is p.left) == (p is g.left):
                self.log.append("zig-zig")
                self._rotate(p)            # parent first, then x
                self._rotate(x)
            else:
                self.log.append("zig-zag")
                self._rotate(x)            # x twice
                self._rotate(x)

    def insert(self, key):
        if self.root is None:
            self.root = Node(key)
            return
        x = self.root
        while True:
            if key == x.key:
                break
            nxt = x.left if key < x.key else x.right
            if nxt is None:
                n = Node(key)
                n.parent = x
                if key < x.key:
                    x.left = n
                else:
                    x.right = n
                x = n
                break
            x = nxt
        self.splay(x)

    def find(self, key):
        x, last = self.root, None
        while x:
            last = x
            if key == x.key:
                break
            x = x.left if key < x.key else x.right
        if last:
            self.splay(last)               # splay the last node touched
        return x is not None

    def depth_of(self, key):
        d, x = 0, self.root
        while x.key != key:
            x, d = (x.left if key < x.key else x.right), d + 1
        return d

    def show(self, x="root"):
        x = self.root if x == "root" else x
        if x is None:
            return "."
        if x.left is None and x.right is None:
            return str(x.key)
        return f"{x.key}({self.show(x.left)},{self.show(x.right)})"


def build_path(n):                         # 1..n as a left path: n at the root
    t = SplayTree()
    prev = None
    for k in range(n, 0, -1):
        node = Node(k)
        if prev is None:
            t.root = node
        else:
            prev.left, node.parent = node, prev
        prev = node
    return t


if __name__ == "__main__":
    t = build_path(7)
    print("start      :", t.show())
    t.log.clear()
    t.find(1)
    print("find 1     :", t.show(), " steps:", ", ".join(t.log))
    t.log.clear()
    t.find(4)
    print("find 4     :", t.show(), " steps:", ", ".join(t.log))

    n = 2000
    t = build_path(n)
    print(f"path of {n}: depth of key 1 before = {t.depth_of(1)}")
    t.find(1)
    print(f"after splaying 1: depth of key 2 = {t.depth_of(2)}, "
          f"of key {n // 2} = {t.depth_of(n // 2)}")

    random.seed(1985)
    n, m = 20000, 100000
    t = SplayTree()
    for k in random.sample(range(n), n):
        t.insert(k)
    t.rotations = 0
    for _ in range(m):
        t.find(random.randrange(n))
    print(f"{m} uniform finds on n = {n}: {t.rotations / m:.1f} rotations per find")
    t.rotations = 0
    hot = random.sample(range(n), 10)
    for _ in range(m):
        t.find(random.choice(hot))
    print(f"{m} finds among 10 hot keys: {t.rotations / m:.1f} rotations per find")
