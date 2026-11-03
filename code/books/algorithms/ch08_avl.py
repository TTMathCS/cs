"""Chapter 8: AVL trees (Adelson-Velsky and Landis, 1962) from scratch."""
import math
import random


class Node:
    def __init__(self, key):
        self.key, self.left, self.right, self.h = key, None, None, 0


def h(t):
    return -1 if t is None else t.h


def fix(t):                        # recompute a node's height from its children
    t.h = 1 + max(h(t.left), h(t.right))


def rotate_right(y):               #     y          x
    x = y.left                     #    / \        / \
    y.left = x.right               #   x   C  ->  A   y
    x.right = y                    #  / \            / \
    fix(y)                         # A   B          B   C
    fix(x)
    return x


def rotate_left(x):
    y = x.right
    x.right = y.left
    y.left = x
    fix(x)
    fix(y)
    return y


log = []                           # which rotations happened


def rebalance(t):
    fix(t)
    bal = h(t.left) - h(t.right)
    if bal == 2:                   # left side too tall
        if h(t.left.left) < h(t.left.right):
            log.append(f"LR at {t.key}")
            t.left = rotate_left(t.left)
        else:
            log.append(f"LL at {t.key}")
        return rotate_right(t)
    if bal == -2:                  # right side too tall
        if h(t.right.right) < h(t.right.left):
            log.append(f"RL at {t.key}")
            t.right = rotate_right(t.right)
        else:
            log.append(f"RR at {t.key}")
        return rotate_left(t)
    return t


def insert(t, k):
    if t is None:
        return Node(k)
    if k < t.key:
        t.left = insert(t.left, k)
    elif k > t.key:
        t.right = insert(t.right, k)
    else:
        return t
    return rebalance(t)


def delete(t, k):
    if t is None:
        return None
    if k < t.key:
        t.left = delete(t.left, k)
    elif k > t.key:
        t.right = delete(t.right, k)
    else:
        if t.left is None or t.right is None:
            return t.left or t.right
        s = t.right
        while s.left:
            s = s.left
        t.key = s.key
        t.right = delete(t.right, s.key)
    return rebalance(t)


def check(t):
    """Return the height; raise if the AVL rule or the search order fails."""
    if t is None:
        return -1
    a, b = check(t.left), check(t.right)
    assert abs(a - b) <= 1 and t.h == 1 + max(a, b)
    assert t.left is None or t.left.key < t.key
    assert t.right is None or t.right.key > t.key
    return t.h


def show(t):
    if t is None:
        return "."
    if t.left is None and t.right is None:
        return str(t.key)
    return f"{t.key}({show(t.left)},{show(t.right)})"


def fewest_nodes(height):          # N(h) = N(h-1) + N(h-2) + 1
    n = [1, 2]
    while len(n) <= height:
        n.append(n[-1] + n[-2] + 1)
    return n[height]


if __name__ == "__main__":
    root = None
    for k in [10, 20, 30, 25, 28, 5, 3]:
        log.clear()
        root = insert(root, k)
        print(f"insert {k:2}: {show(root):34} {', '.join(log) or '-'}")

    fib = [0, 1]
    while len(fib) < 25:
        fib.append(fib[-1] + fib[-2])
    print("h  N(h)  F(h+3)-1")
    for hh in range(8):
        print(f"{hh}  {fewest_nodes(hh):4}  {fib[hh + 3] - 1:4}")

    random.seed(1962)
    root, keys = None, random.sample(range(10**6), 100000)
    for k in keys:
        root = insert(root, k)
    for k in keys[:50000]:
        root = delete(root, k)
    n = 50000
    print(f"n = {n}: AVL height {check(root)}, log2(n) = {math.log2(n):.1f}, "
          f"bound 1.44*log2(n+2) = {1.4405 * math.log2(n + 2):.1f}")
