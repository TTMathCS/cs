class Fenwick:
    """Prefix sums with updates, both in O(log n). Positions are 1..n inside the tree."""
    def __init__(self, n):
        self.n = n
        self.t = [0] * (n + 1)               # t[i] holds the sum of the last lowbit(i) values up to i

    def add(self, i, delta):
        """a[i] += delta, for i in 0..n-1."""
        i += 1
        while i <= self.n:
            self.t[i] += delta
            i += i & -i                      # jump to the next range that covers position i

    def prefix(self, i):
        """a[0] + ... + a[i-1]."""
        s = 0
        while i > 0:
            s += self.t[i]
            i -= i & -i                      # drop the lowest set bit: the ranges tile [1, i]
        return s

    def range_sum(self, lo, hi):
        """a[lo] + ... + a[hi - 1]."""
        return self.prefix(hi) - self.prefix(lo)


if __name__ == "__main__":
    a = [5, 2, 9, -3, 5, 20, 10, -7]
    f = Fenwick(len(a))
    for i, x in enumerate(a):
        f.add(i, x)
    print([f.prefix(i) for i in range(len(a) + 1)])
    print(f.range_sum(2, 6))                 # 9 - 3 + 5 + 20
    f.add(3, 10)                             # a[3] becomes 7
    print(f.range_sum(2, 6), f.prefix(8))
    print(f.t[1:])
