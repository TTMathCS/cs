# Chapter 24: cache misses of matrix transpose, counted on a simulated cache
# (M words, lines of B words, least-recently-used replacement).
# Naive row-by-row versus a cache-oblivious divide-and-conquer that never looks at M or B.
from collections import OrderedDict


class Cache:
    def __init__(self, M, B):
        self.lines, self.B = M // B, B
        self.store, self.misses = OrderedDict(), 0

    def touch(self, address):
        line = address // self.B
        if line in self.store:
            self.store.move_to_end(line)
        else:
            self.misses += 1
            if len(self.store) == self.lines:
                self.store.popitem(last=False)
            self.store[line] = True


def naive_transpose(n, cache):
    A, T = 0, n * n                                 # A at address 0, its transpose after it
    for i in range(n):
        for j in range(n):
            cache.touch(A + i * n + j)              # read A[i][j]: along a row
            cache.touch(T + j * n + i)              # write T[j][i]: down a column


def recursive_transpose(n, cache, r0=0, c0=0, rows=None, cols=None):
    rows = n if rows is None else rows
    cols = n if cols is None else cols
    if rows * cols <= 16:                           # tiny base case
        for i in range(r0, r0 + rows):
            for j in range(c0, c0 + cols):
                cache.touch(i * n + j)
                cache.touch(n * n + j * n + i)
    elif rows >= cols:                              # split the longer side in half
        h = rows // 2
        recursive_transpose(n, cache, r0, c0, h, cols)
        recursive_transpose(n, cache, r0 + h, c0, rows - h, cols)
    else:
        h = cols // 2
        recursive_transpose(n, cache, r0, c0, rows, h)
        recursive_transpose(n, cache, r0, c0 + h, rows, cols - h)


print("matrix transpose, n x n doubles; misses counted in cache lines")
print("    n      M     B   naive misses   recursive misses   lower bound 2n^2/B")
for n, M, B in [(64, 1024, 8), (128, 1024, 8), (128, 4096, 16), (256, 4096, 16), (256, 8192, 64)]:
    c1, c2 = Cache(M, B), Cache(M, B)
    naive_transpose(n, c1)
    recursive_transpose(n, c2)
    print(f"{n:5d} {M:6d} {B:5d}   {c1.misses:12d}   {c2.misses:16d}   {2 * n * n // B:12d}")
