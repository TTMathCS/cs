"""Chapter 8: tree traversals and a plain binary search tree, from scratch."""
from collections import deque
import random


class Node:
    def __init__(self, key):
        self.key = key
        self.left = None
        self.right = None


# ---------- traversals ----------
def preorder(t, out):
    if t:
        out.append(t.key)          # visit, then left, then right
        preorder(t.left, out)
        preorder(t.right, out)
    return out


def inorder(t, out):
    if t:
        inorder(t.left, out)       # left, visit, right
        out.append(t.key)
        inorder(t.right, out)
    return out


def postorder(t, out):
    if t:
        postorder(t.left, out)     # left, right, then visit
        postorder(t.right, out)
        out.append(t.key)
    return out


def level_order(t):
    out, q = [], deque([t] if t else [])
    while q:                       # a queue: nearest the root first
        x = q.popleft()
        out.append(x.key)
        if x.left:
            q.append(x.left)
        if x.right:
            q.append(x.right)
    return out


def height(t):                     # empty tree -1, one node 0
    h, level = -1, [t] if t else []
    while level:                   # level by level, so no deep recursion
        h += 1
        level = [c for x in level for c in (x.left, x.right) if c]
    return h


# ---------- binary search tree ----------
def search(t, k):
    while t is not None and t.key != k:
        t = t.left if k < t.key else t.right
    return t


def insert(t, k):
    if t is None:
        return Node(k)
    if k < t.key:
        t.left = insert(t.left, k)
    elif k > t.key:
        t.right = insert(t.right, k)
    return t                       # equal keys: already there


def insert_loop(t, k):
    """The same insertion without recursion (a path of 1000 nodes would
    overflow Python's call stack)."""
    if t is None:
        return Node(k)
    x = t
    while True:
        if k == x.key:
            return t
        side = "left" if k < x.key else "right"
        child = getattr(x, side)
        if child is None:
            setattr(x, side, Node(k))
            return t
        x = child


def delete(t, k):
    if t is None:
        return None
    if k < t.key:
        t.left = delete(t.left, k)
    elif k > t.key:
        t.right = delete(t.right, k)
    else:
        if t.left is None:         # zero or one child: splice out
            return t.right
        if t.right is None:
            return t.left
        s = t.right                # two children: successor = min of right
        while s.left:
            s = s.left
        t.key = s.key
        t.right = delete(t.right, s.key)
    return t


def is_bst(t, lo=float("-inf"), hi=float("inf")):
    return t is None or (lo < t.key < hi and is_bst(t.left, lo, t.key)
                         and is_bst(t.right, t.key, hi))


def show(t):
    """One line: key(left,right), '.' for an empty child."""
    if t is None:
        return "."
    if t.left is None and t.right is None:
        return str(t.key)
    return f"{t.key}({show(t.left)},{show(t.right)})"


if __name__ == "__main__":
    keys = [8, 3, 10, 1, 6, 14, 4, 7, 13]
    root = None
    for k in keys:
        root = insert(root, k)
    print("tree      :", show(root))
    print("preorder  :", preorder(root, []))
    print("inorder   :", inorder(root, []))
    print("postorder :", postorder(root, []))
    print("level     :", level_order(root))
    print("height    :", height(root))
    print("search 7  :", search(root, 7) is not None, "| search 5:", search(root, 5) is not None)

    for k in [4, 10, 3]:           # a leaf, one child, two children
        root = delete(root, k)
        print(f"delete {k:2} :", show(root), "| still a BST:", is_bst(root))

    # Sorted input makes a path; random input stays shallow.
    n = 1000
    path = None
    for k in range(n):
        path = insert_loop(path, k)
    rnd = None
    random.seed(8)
    for k in random.sample(range(n), n):
        rnd = insert_loop(rnd, k)
    print(f"n = {n}: height after sorted inserts = {height(path)}, "
          f"after random inserts = {height(rnd)}")
