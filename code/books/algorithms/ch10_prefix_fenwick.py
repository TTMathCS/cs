"""Chapter 10: prefix sums, difference arrays and the Fenwick tree
(binary indexed tree, Fenwick 1994), from scratch."""
import random


def prefix_sums(a):
    p = [0]
    for x in a:
        p.append(p[-1] + x)            # p[i] = a[0] + ... + a[i-1]
    return p


def range_sum(p, l, r):                # a[l] + ... + a[r-1], half-open
    return p[r] - p[l]


def apply_range_adds(n, updates):
    d = [0] * (n + 1)                  # difference array
    for l, r, v in updates:            # add v to a[l..r-1]
        d[l] += v
        d[r] -= v
    out, run = [], 0
    for i in range(n):
        run += d[i]
        out.append(run)
    return out


def prefix_sums_2d(g):
    R, C = len(g), len(g[0])
    P = [[0] * (C + 1) for _ in range(R + 1)]
    for i in range(R):
        for j in range(C):
            P[i + 1][j + 1] = g[i][j] + P[i][j + 1] + P[i + 1][j] - P[i][j]
    return P


def rect_sum(P, r1, c1, r2, c2):       # rows r1..r2-1, columns c1..c2-1
    return P[r2][c2] - P[r1][c2] - P[r2][c1] + P[r1][c1]


class Fenwick:
    """1-based. t[i] holds the sum of a(i - lowbit(i), i], lowbit(i) = i & -i."""

    def __init__(self, n):
        self.n, self.t = n, [0] * (n + 1)

    @classmethod
    def build(cls, a):                 # O(n): push each node into its parent once
        f = cls(len(a))
        for i, x in enumerate(a, 1):
            f.t[i] += x
            j = i + (i & -i)
            if j <= f.n:
                f.t[j] += f.t[i]
        return f

    def add(self, i, v):               # a[i] += v
        while i <= self.n:
            self.t[i] += v
            i += i & -i                # climb to the next node that covers i

    def prefix(self, i):               # a[1] + ... + a[i]
        s = 0
        while i > 0:
            s += self.t[i]
            i -= i & -i                # drop the lowest 1-bit
        return s

    def range_sum(self, l, r):         # a[l] + ... + a[r], 1-based, inclusive
        return self.prefix(r) - self.prefix(l - 1)


if __name__ == "__main__":
    a = [3, 1, 4, 1, 5, 9, 2, 6]
    p = prefix_sums(a)
    print("a          :", a)
    print("prefix sums:", p)
    print("sum a[2..5] =", range_sum(p, 2, 6))
    print("difference array, add 10 to a[1..3] and 5 to a[2..6] on zeros:",
          apply_range_adds(8, [(1, 4, 10), (2, 7, 5)]))
    g = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
    P = prefix_sums_2d(g)
    print("2D: sum of the bottom-right 2x2 block =", rect_sum(P, 1, 1, 3, 3))

    print(" i  binary  lowbit  t[i] covers")
    for i in range(1, 9):
        lb = i & -i
        print(f"{i:2}  {i:04b}    {lb:2}     a[{i - lb + 1}..{i}]")
    f = Fenwick.build(a)
    print("tree t[1..8]:", f.t[1:])
    i, path = 7, []
    while i > 0:
        path.append(i)
        i -= i & -i
    print("prefix(7) reads t at", path, "=", f.prefix(7))
    i, path = 3, []
    while i <= 8:
        path.append(i)
        i += i & -i
    print("add(3, ...) writes t at", path)

    random.seed(1994)
    n = 100000
    a = [random.randint(-50, 50) for _ in range(n)]
    f, ok = Fenwick.build(a), True
    for _ in range(20000):
        if random.random() < 0.5:
            i, v = random.randrange(n), random.randint(-50, 50)
            a[i] += v
            f.add(i + 1, v)
        else:
            l = random.randrange(n)
            r = random.randrange(l, min(n, l + 50))
            ok &= f.range_sum(l + 1, r + 1) == sum(a[l:r + 1])
    print(f"20000 random adds and range sums on n = {n} agree with brute force:", ok)
