"""Chapter 10: segment trees. A range-minimum tree with point updates, and a
range-add / range-sum tree with lazy propagation."""
import random


class MinSegTree:
    """Node 1 is the root covering [0, n); node v has children 2v and 2v+1."""

    def __init__(self, a):
        self.n = len(a)
        self.t = [0] * (4 * self.n)
        self.visited = 0
        self._build(1, 0, self.n, a)

    def _build(self, v, lo, hi, a):
        if hi - lo == 1:
            self.t[v] = a[lo]
            return
        mid = (lo + hi) // 2
        self._build(2 * v, lo, mid, a)
        self._build(2 * v + 1, mid, hi, a)
        self.t[v] = min(self.t[2 * v], self.t[2 * v + 1])

    def query(self, l, r, v=1, lo=0, hi=None):     # min of a[l:r]
        hi = self.n if hi is None else hi
        self.visited += 1
        if r <= lo or hi <= l:
            return float("inf")                    # no overlap
        if l <= lo and hi <= r:
            return self.t[v]                       # node inside the query
        mid = (lo + hi) // 2
        return min(self.query(l, r, 2 * v, lo, mid),
                   self.query(l, r, 2 * v + 1, mid, hi))

    def update(self, i, x, v=1, lo=0, hi=None):    # a[i] = x
        hi = self.n if hi is None else hi
        if hi - lo == 1:
            self.t[v] = x
            return
        mid = (lo + hi) // 2
        if i < mid:
            self.update(i, x, 2 * v, lo, mid)
        else:
            self.update(i, x, 2 * v + 1, mid, hi)
        self.t[v] = min(self.t[2 * v], self.t[2 * v + 1])


class LazySumTree:
    """Range add and range sum. lazy[v] = an add not yet passed to v's children."""

    def __init__(self, a):
        self.n = len(a)
        self.s = [0] * (4 * self.n)
        self.lazy = [0] * (4 * self.n)
        self._build(1, 0, self.n, a)

    def _build(self, v, lo, hi, a):
        if hi - lo == 1:
            self.s[v] = a[lo]
            return
        mid = (lo + hi) // 2
        self._build(2 * v, lo, mid, a)
        self._build(2 * v + 1, mid, hi, a)
        self.s[v] = self.s[2 * v] + self.s[2 * v + 1]

    def _apply(self, v, lo, hi, x):    # add x to every element under v, lazily
        self.s[v] += x * (hi - lo)
        self.lazy[v] += x

    def _push(self, v, lo, mid, hi):   # pass the pending add down one level
        if self.lazy[v]:
            self._apply(2 * v, lo, mid, self.lazy[v])
            self._apply(2 * v + 1, mid, hi, self.lazy[v])
            self.lazy[v] = 0

    def add(self, l, r, x, v=1, lo=0, hi=None):    # a[l:r] += x
        hi = self.n if hi is None else hi
        if r <= lo or hi <= l:
            return
        if l <= lo and hi <= r:
            self._apply(v, lo, hi, x)
            return
        mid = (lo + hi) // 2
        self._push(v, lo, mid, hi)
        self.add(l, r, x, 2 * v, lo, mid)
        self.add(l, r, x, 2 * v + 1, mid, hi)
        self.s[v] = self.s[2 * v] + self.s[2 * v + 1]

    def sum(self, l, r, v=1, lo=0, hi=None):       # a[l] + ... + a[r-1]
        hi = self.n if hi is None else hi
        if r <= lo or hi <= l:
            return 0
        if l <= lo and hi <= r:
            return self.s[v]
        mid = (lo + hi) // 2
        self._push(v, lo, mid, hi)
        return self.sum(l, r, 2 * v, lo, mid) + self.sum(l, r, 2 * v + 1, mid, hi)


if __name__ == "__main__":
    a = [5, 8, 6, 3, 2, 7, 2, 6]
    st = MinSegTree(a)
    print("a =", a)
    print("tree nodes 1..15:", st.t[1:16])
    st.visited = 0
    print("min a[1:6] =", st.query(1, 6), " nodes visited:", st.visited)
    st.update(4, 9)
    print("after a[4] = 9: min a[1:6] =", st.query(1, 6), " root =", st.t[1])

    lz = LazySumTree([0] * 8)
    lz.add(2, 7, 10)
    print("after adding 10 to a[2:7]: sum a[0:8] =", lz.sum(0, 8),
          " sum a[5:8] =", lz.sum(5, 8), " pending adds:", [x for x in lz.lazy[1:16]])

    random.seed(1977)
    n = 50000
    a = [random.randint(0, 1000) for _ in range(n)]
    st, lz, ok, worst = MinSegTree(a), LazySumTree(a), True, 0
    b = a[:]
    for _ in range(3000):
        l = random.randrange(n)
        r = random.randrange(l + 1, min(n, l + 200) + 1)
        op = random.random()
        if op < 0.3:
            i, x = random.randrange(n), random.randint(0, 1000)
            a[i] = x
            st.update(i, x)
        elif op < 0.6:
            st.visited = 0
            ok &= st.query(l, r) == min(a[l:r])
            worst = max(worst, st.visited)
        elif op < 0.8:
            x = random.randint(-5, 5)
            lz.add(l, r, x)
            for i in range(l, r):
                b[i] += x
        else:
            ok &= lz.sum(l, r) == sum(b[l:r])
    print(f"n = {n}: 3000 random operations agree with brute force: {ok}; "
          f"most nodes visited by one min query: {worst} (4 log2 n is about 62)")
