"""Chapter 13: Fibonacci three ways, coin change, 0/1 knapsack, longest increasing subsequence."""
from bisect import bisect_left
from functools import lru_cache
import random

calls = 0


def fib_naive(n):
    global calls
    calls += 1
    return n if n < 2 else fib_naive(n - 1) + fib_naive(n - 2)


@lru_cache(maxsize=None)
def fib_memo(n):                      # top-down: recursion plus a memo table
    return n if n < 2 else fib_memo(n - 1) + fib_memo(n - 2)


def fib_table(n):                     # bottom-up: fill the table in order, keep two entries
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a


def min_coins(amount, coins):
    """best[v] = fewest coins making v; also remember the last coin used."""
    INF = float("inf")
    best = [0] + [INF] * amount
    last = [None] * (amount + 1)
    for v in range(1, amount + 1):
        for c in coins:
            if c <= v and best[v - c] + 1 < best[v]:
                best[v], last[v] = best[v - c] + 1, c
    used, v = [], amount
    while v > 0 and last[v] is not None:
        used.append(last[v])
        v -= last[v]
    return best[amount], used


def count_ways(amount, coins):
    """Number of multisets of coins summing to amount (order does not matter)."""
    ways = [1] + [0] * amount
    for c in coins:                   # coin loop outside: each combination counted once
        for v in range(c, amount + 1):
            ways[v] += ways[v - c]
    return ways[amount]


def knapsack(items, W):
    """items: (name, weight, value). K[i][w] = best value using the first i items, capacity w."""
    n = len(items)
    K = [[0] * (W + 1) for _ in range(n + 1)]
    for i in range(1, n + 1):
        _, wt, val = items[i - 1]
        for w in range(W + 1):
            K[i][w] = K[i - 1][w]                         # skip item i
            if wt <= w:
                K[i][w] = max(K[i][w], K[i - 1][w - wt] + val)   # or take it
    chosen, w = [], W
    for i in range(n, 0, -1):                             # walk back to see which items
        if K[i][w] != K[i - 1][w]:
            chosen.append(items[i - 1][0])
            w -= items[i - 1][1]
    return K[n][W], chosen[::-1], K


def lis_quadratic(a):
    L = [1] * len(a)
    for i in range(len(a)):
        for j in range(i):
            if a[j] < a[i]:
                L[i] = max(L[i], L[j] + 1)
    return max(L, default=0)


def lis_fast(a):
    """tails[k] = smallest possible last element of an increasing subsequence of length k+1."""
    tails, tails_idx, prev = [], [], [None] * len(a)
    for i, x in enumerate(a):
        k = bisect_left(tails, x)
        if k == len(tails):
            tails.append(x)
            tails_idx.append(i)
        else:
            tails[k] = x
            tails_idx[k] = i
        prev[i] = tails_idx[k - 1] if k > 0 else None
    seq, i = [], tails_idx[-1] if tails_idx else None
    while i is not None:
        seq.append(a[i])
        i = prev[i]
    return len(tails), seq[::-1]


if __name__ == "__main__":
    for n in (10, 20, 25):
        calls = 0
        v = fib_naive(n)
        print(f"fib({n}) = {v}: naive recursion made {calls} calls; memo and table agree:",
              fib_memo(n) == fib_table(n) == v)
    print("fib(90) by table =", fib_table(90))

    print("\nmin coins for 63 with [1, 5, 10, 21, 25]:", min_coins(63, [1, 5, 10, 21, 25]))
    print("ways to make 100 cents from [1, 5, 10, 25, 50]:", count_ways(100, [1, 5, 10, 25, 50]))

    items = [("A", 1, 1), ("B", 3, 4), ("C", 4, 5), ("D", 5, 7)]
    best, chosen, K = knapsack(items, 7)
    print("\nknapsack capacity 7:", best, chosen)
    print("table K[i][w], w = 0..7:")
    for i, row in enumerate(K):
        print("  ", "-" if i == 0 else items[i - 1][0], row)

    a = [3, 1, 4, 1, 5, 9, 2, 6, 5, 3, 5, 8, 9, 7, 9]
    print("\nLIS of", a, "->", lis_fast(a), " quadratic DP says length", lis_quadratic(a))
    random.seed(13)
    def is_subsequence(seq, b):
        it = iter(b)
        return all(x in it for x in seq)
    ok = True
    for _ in range(300):
        b = [random.randint(0, 30) for _ in range(random.randint(0, 40))]
        length, seq = lis_fast(b)
        ok &= (length == lis_quadratic(b) == len(seq) and is_subsequence(seq, b)
               and all(x < y for x, y in zip(seq, seq[1:])))
    print("300 random lists: fast LIS length and subsequence check out:", ok)
