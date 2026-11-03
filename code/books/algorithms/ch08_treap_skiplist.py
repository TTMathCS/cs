"""Chapter 8: treaps and skip lists, balance by coin flips instead of rules."""
import math
import random


# ---------- treap: a BST by key, a heap by random priority ----------
class TNode:
    def __init__(self, key, prio):
        self.key, self.prio, self.left, self.right = key, prio, None, None


def rot_right(y):
    x = y.left
    y.left, x.right = x.right, y
    return x


def rot_left(x):
    y = x.right
    x.right, y.left = y.left, x
    return y


def treap_insert(t, key, prio):
    if t is None:
        return TNode(key, prio)
    if key < t.key:
        t.left = treap_insert(t.left, key, prio)
        if t.left.prio < t.prio:           # smaller priority must be higher up
            t = rot_right(t)
    else:
        t.right = treap_insert(t.right, key, prio)
        if t.right.prio < t.prio:
            t = rot_left(t)
    return t


def depths(t, d=0, out=None):
    out = [] if out is None else out
    if t:
        out.append(d)
        depths(t.left, d + 1, out)
        depths(t.right, d + 1, out)
    return out


def show(t):
    if t is None:
        return "."
    me = f"{t.key}:{t.prio}"
    if t.left is None and t.right is None:
        return me
    return f"{me}({show(t.left)},{show(t.right)})"


# ---------- skip list ----------
class SkipList:
    MAX = 32

    def __init__(self, rng):
        self.head = [None] * self.MAX      # head.next at every level
        self.level, self.rng, self.steps = 1, rng, 0

    def random_level(self):
        lv = 1
        while lv < self.MAX and self.rng.random() < 0.5:
            lv += 1                        # each extra level with probability 1/2
        return lv

    def _path(self, key):
        """For each level, the last node before key (None = the head)."""
        update, x = [None] * self.MAX, None
        for i in reversed(range(self.level)):
            while True:
                nxt = (x[1] if x else self.head)[i]
                if nxt is None or nxt[0] >= key:
                    break
                x = nxt
                self.steps += 1
            update[i] = x
        return update

    def insert(self, key):
        update = self._path(key)
        lv = self.random_level()
        self.level = max(self.level, lv)
        node = [key, [None] * lv]          # [key, forward pointers]
        for i in range(lv):
            prev = update[i][1] if update[i] else self.head
            node[1][i], prev[i] = prev[i], node

    def contains(self, key):
        x = self._path(key)[0]
        nxt = (x[1] if x else self.head)[0]
        return nxt is not None and nxt[0] == key

    def levels(self):
        rows = []
        for i in reversed(range(self.level)):
            row, x = [], self.head[i]
            while x:
                row.append(x[0])
                x = x[1][i]
            rows.append(row)
        return rows


if __name__ == "__main__":
    t = None
    for key, prio in [("D", 9), ("B", 4), ("F", 7), ("A", 6), ("C", 2), ("E", 1)]:
        t = treap_insert(t, key, prio)
        print(f"insert {key}:{prio}  {show(t)}")

    rng = random.Random(1989)
    n = 100000
    t = None
    for k in range(n):                     # sorted keys: no trouble for a treap
        t = treap_insert(t, k, rng.random())
    d = depths(t)
    print(f"treap, n = {n} sorted keys: average depth {sum(d) / n:.1f}, "
          f"max depth {max(d)}, 2 ln n = {2 * math.log(n):.1f}")

    s = SkipList(random.Random(22))
    for k in [30, 10, 50, 20, 40, 60, 70]:
        s.insert(k)
    for i, row in enumerate(s.levels()):
        print(f"level {s.level - i}: {row}")
    s = SkipList(random.Random(1990))
    for k in rng.sample(range(10 * n), n):
        s.insert(k)
    s.steps = 0
    queries = rng.sample(range(10 * n), 1000)
    found = sum(s.contains(q) for q in queries)
    print(f"skip list, n = {n}: {s.level} levels, average forward steps per "
          f"search {s.steps / 1000:.1f}, 2*log2(n) = {2 * math.log2(n):.1f}, found {found}")
