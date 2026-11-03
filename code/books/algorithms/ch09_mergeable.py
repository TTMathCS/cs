"""Chapter 9: mergeable heaps. Leftist heaps (Crane 1972) and binomial heaps
(Vuillemin 1978), both from scratch."""
import random


# ---------- leftist heap ----------
class L:
    def __init__(self, key):
        self.key, self.left, self.right, self.s = key, None, None, 1


def s(t):                                  # null-path length: 0 for empty
    return t.s if t else 0


def lmerge(a, b):
    if a is None:
        return b
    if b is None:
        return a
    if b.key < a.key:
        a, b = b, a                        # a has the smaller root
    a.right = lmerge(a.right, b)           # merge down the right spine
    if s(a.left) < s(a.right):
        a.left, a.right = a.right, a.left  # keep the short side on the right
    a.s = s(a.right) + 1
    return a


def lpush(t, key):
    return lmerge(t, L(key))


def lpop(t):
    return t.key, lmerge(t.left, t.right)


def lshow(t):
    if t is None:
        return "."
    if t.left is None and t.right is None:
        return str(t.key)
    return f"{t.key}({lshow(t.left)},{lshow(t.right)})"


def right_spine(t):
    n = 0
    while t:
        n, t = n + 1, t.right
    return n


# ---------- binomial heap ----------
class B:
    def __init__(self, key):
        self.key, self.kids, self.order = key, [], 0


def link(a, b):                            # two trees of the same order k
    if b.key < a.key:
        a, b = b, a
    a.kids.append(b)                       # the larger root becomes a child
    a.order += 1
    return a


def bmerge(h1, h2):
    """Heaps are lists indexed by order: slot k holds a tree of order k or None.
    Merging is binary addition with carries."""
    out, carry = [], None
    for k in range(max(len(h1), len(h2)) + 1):
        trees = [t for t in (h1[k] if k < len(h1) else None,
                             h2[k] if k < len(h2) else None, carry) if t]
        carry = None
        if len(trees) == 1:
            out.append(trees[0])
        elif len(trees) == 2:
            out.append(None)
            carry = link(*trees)
        elif len(trees) == 3:
            out.append(trees[2])
            carry = link(trees[0], trees[1])
        else:
            out.append(None)
    while out and out[-1] is None:
        out.pop()
    return out


def bpush(h, key):
    return bmerge(h, [B(key)])


def bpop(h):
    k = min((i for i, t in enumerate(h) if t), key=lambda i: h[i].key)
    top = h[k]
    rest = h[:k] + [None] + h[k + 1:]
    return top.key, bmerge(rest, top.kids)  # the children are orders 0..k-1


def bshape(h):
    return " ".join(f"B{t.order}" for t in h if t)


def size(t):
    return 1 + sum(size(c) for c in t.kids)


if __name__ == "__main__":
    a = b = None
    for x in [3, 10, 8, 21, 14, 17]:
        a = lpush(a, x)
    for x in [6, 12, 7, 18, 24, 37, 18, 33]:
        b = lpush(b, x)
    print("leftist A:", lshow(a))
    print("leftist B:", lshow(b))
    m = lmerge(a, b)
    print("merged   :", lshow(m))
    out = []
    while m:
        x, m = lpop(m)
        out.append(x)
    print("pops     :", out)

    h = []
    for x in range(1, 14):                 # 13 = binary 1101
        h = bpush(h, x)
    print("binomial heap of 13 keys:", bshape(h), " sizes:", [size(t) for t in h if t])
    g = []
    for x in range(20, 31):                # 11 = binary 1011
        g = bpush(g, x)
    print("binomial heap of 11 keys:", bshape(g))
    h = bmerge(h, g)
    print("after merging (24 = 11000):", bshape(h))

    random.seed(1978)
    n = 100000
    t, hb, keys = None, [], [random.random() for _ in range(n)]
    for x in keys:
        t = lpush(t, x)
        hb = bpush(hb, x)
    print(f"n = {n}: leftist right spine {right_spine(t)} nodes; "
          f"binomial heap has {sum(1 for x in hb if x)} trees (bits of {n} = {bin(n).count('1')})")
    got = []
    for _ in range(1000):
        x, t = lpop(t)
        y, hb = bpop(hb)
        assert x == y
        got.append(x)
    print("1000 pops agree and are sorted:", got == sorted(keys)[:1000])
