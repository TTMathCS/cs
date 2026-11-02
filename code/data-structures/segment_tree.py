INF = float("inf")


class SegmentTree:
    """Range minimum over a[lo..hi] and point updates, both O(log n). Node 1 covers the whole array."""
    def __init__(self, a):
        self.n = len(a)
        self.t = [0] * (4 * self.n)
        self._build(1, 0, self.n - 1, a)

    def _build(self, node, lo, hi, a):
        if lo == hi:
            self.t[node] = a[lo]             # a leaf holds one value
            return
        mid = (lo + hi) // 2
        self._build(2 * node, lo, mid, a)
        self._build(2 * node + 1, mid + 1, hi, a)
        self.t[node] = min(self.t[2 * node], self.t[2 * node + 1])

    def update(self, i, value, node=1, lo=0, hi=None):
        """a[i] = value."""
        if hi is None:
            hi = self.n - 1
        if lo == hi:
            self.t[node] = value
            return
        mid = (lo + hi) // 2
        if i <= mid:
            self.update(i, value, 2 * node, lo, mid)
        else:
            self.update(i, value, 2 * node + 1, mid + 1, hi)
        self.t[node] = min(self.t[2 * node], self.t[2 * node + 1])   # repair on the way back up

    def query(self, l, r, node=1, lo=0, hi=None):
        """min(a[l..r]), both ends included."""
        if hi is None:
            hi = self.n - 1
        if r < lo or hi < l:                 # no overlap
            return INF
        if l <= lo and hi <= r:              # this node's range is inside [l, r]: use it whole
            return self.t[node]
        mid = (lo + hi) // 2
        return min(self.query(l, r, 2 * node, lo, mid), self.query(l, r, 2 * node + 1, mid + 1, hi))


if __name__ == "__main__":
    a = [5, 8, 6, 3, 2, 7, 2, 6]
    st = SegmentTree(a)
    print(st.query(0, 7), st.query(0, 2), st.query(1, 3), st.query(5, 5))
    st.update(4, 9)                          # a[4]: 2 -> 9
    print(st.query(3, 5), st.query(4, 5))
    st.update(3, 10)
    print(st.query(0, 4), st.t[1])
