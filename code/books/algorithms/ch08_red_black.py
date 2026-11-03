"""Chapter 8: red-black tree insertion (the classic five rules), from scratch."""
import math
import random

RED, BLACK = "R", "B"


class Node:
    def __init__(self, key, color, nil=None):
        self.key, self.color = key, color
        self.left = self.right = self.parent = nil


class RedBlackTree:
    def __init__(self):
        self.nil = Node(None, BLACK)   # one shared black leaf (rule 3)
        self.root = self.nil
        self.log = []

    def rotate_left(self, x):
        y = x.right
        x.right = y.left
        if y.left is not self.nil:
            y.left.parent = x
        y.parent = x.parent
        if x.parent is self.nil:
            self.root = y
        elif x is x.parent.left:
            x.parent.left = y
        else:
            x.parent.right = y
        y.left, x.parent = x, y

    def rotate_right(self, x):
        y = x.left
        x.left = y.right
        if y.right is not self.nil:
            y.right.parent = x
        y.parent = x.parent
        if x.parent is self.nil:
            self.root = y
        elif x is x.parent.right:
            x.parent.right = y
        else:
            x.parent.left = y
        y.right, x.parent = x, y

    def insert(self, key):
        z = Node(key, RED, self.nil)       # new nodes start red
        y, x = self.nil, self.root
        while x is not self.nil:           # ordinary BST descent
            y = x
            x = x.left if key < x.key else x.right
        z.parent = y
        if y is self.nil:
            self.root = z
        elif key < y.key:
            y.left = z
        else:
            y.right = z
        self.fixup(z)

    def fixup(self, z):
        while z.parent.color == RED:       # rule 4 broken: red under red
            p, g = z.parent, z.parent.parent
            left = p is g.left
            uncle = g.right if left else g.left
            if uncle.color == RED:         # case 1: recolour, move up
                self.log.append(f"case 1 at {z.key}")
                p.color = uncle.color = BLACK
                g.color = RED
                z = g
                continue
            if z is (p.right if left else p.left):   # case 2: a bend
                self.log.append(f"case 2 at {z.key}")
                z = p
                (self.rotate_left if left else self.rotate_right)(z)
                p = z.parent
            self.log.append(f"case 3 at {z.key}")    # case 3: a line
            p.color, g.color = BLACK, RED
            (self.rotate_right if left else self.rotate_left)(g)
        if self.root.color == RED:
            self.log.append("root made black")
        self.root.color = BLACK            # rule 2

    def check(self, x=None):
        """Black-height of x; asserts rules 2, 4, 5 and the search order."""
        x = self.root if x is None else x
        if x is self.nil:
            return 1
        if x is self.root:
            assert x.color == BLACK
        for c in (x.left, x.right):
            if x.color == RED:
                assert c.color == BLACK
        if x.left is not self.nil:
            assert x.left.key < x.key
        if x.right is not self.nil:
            assert x.right.key > x.key
        a, b = self.check(x.left), self.check(x.right)
        assert a == b
        return a + (x.color == BLACK)

    def height(self, x=None):
        x = self.root if x is None else x
        if x is self.nil:
            return 0                       # counting nodes on the longest path
        return 1 + max(self.height(x.left), self.height(x.right))

    def show(self, x=None):
        x = self.root if x is None else x
        if x is self.nil:
            return "."
        me = f"{x.key}{x.color}"
        if x.left is self.nil and x.right is self.nil:
            return me
        return f"{me}({self.show(x.left)},{self.show(x.right)})"


if __name__ == "__main__":
    t = RedBlackTree()
    for k in [10, 20, 30, 15, 25, 5, 1]:
        t.log.clear()
        t.insert(k)
        t.check()
        print(f"insert {k:2}: {t.show():40} {', '.join(t.log) or '-'}")

    random.seed(1978)
    for n in [1000, 100000]:
        t = RedBlackTree()
        for k in random.sample(range(10 * n), n):
            t.insert(k)
        bh = t.check()
        print(f"n = {n:6}: height {t.height():2}, black-height {bh - 1}, "
              f"2*log2(n+1) = {2 * math.log2(n + 1):.1f}")
    t = RedBlackTree()
    for k in range(100000):                # sorted input: the worst for a plain BST
        t.insert(k)
    t.check()
    print(f"sorted n = 100000: height {t.height()}")
