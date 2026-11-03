"""Chapter 2: count the operations of typical loops and compare with the formulas.

Each function returns how many times its innermost line runs.
"""
import math
import random


def single(n):                  # for i in 0..n-1
    return sum(1 for i in range(n))


def nested(n):                  # for i, for j: every ordered pair
    c = 0
    for i in range(n):
        for j in range(n):
            c += 1
    return c


def triangle(n):                # for i, for j > i: every unordered pair
    c = 0
    for i in range(n):
        for j in range(i + 1, n):
            c += 1
    return c


def doubling(n):                # i = 1, 2, 4, 8, ... while i <= n
    c, i = 0, 1
    while i <= n:
        c += 1
        i *= 2
    return c


def harmonic(n):                # for i = 1..n, for j in steps of i
    c = 0
    for i in range(1, n + 1):
        for j in range(0, n, i):
            c += 1
    return c


def linear_search_comparisons(a, x):
    for i, v in enumerate(a):
        if v == x:
            return i + 1        # comparisons made
    return len(a)


if __name__ == "__main__":
    print("Loop counts against their formulas")
    print(f"{'n':>6} {'single':>7} {'nested':>9} {'n(n-1)/2':>9} {'doubling':>9} "
          f"{'floor(lg n)+1':>13} {'harmonic':>9} {'n*H_n':>9}")
    for n in (10, 100, 1000):
        H = sum(1 / k for k in range(1, n + 1))
        print(f"{n:>6} {single(n):>7} {nested(n):>9} {triangle(n):>9} {doubling(n):>9} "
              f"{math.floor(math.log2(n)) + 1:>13} {harmonic(n):>9} {n * H:>9.1f}")
        assert single(n) == n and nested(n) == n * n
        assert triangle(n) == n * (n - 1) // 2
        assert doubling(n) == n.bit_length() == math.floor(math.log2(n)) + 1
        assert harmonic(n) <= n * H + n

    print()
    print("Linear search on n = 1000 distinct items")
    rng = random.Random(2)
    n = 1000
    a = list(range(n))
    rng.shuffle(a)
    trials = 20000
    total = sum(linear_search_comparisons(a, rng.randrange(n)) for _ in range(trials))
    print(f"  best case  : {linear_search_comparisons(a, a[0])} comparison")
    print(f"  worst case : {linear_search_comparisons(a, -1)} comparisons (x absent)")
    print(f"  average over {trials} random present x: {total / trials:.1f}"
          f"   formula (n+1)/2 = {(n + 1) / 2}")

    print()
    print("The growth ladder (number of steps)")
    print(f"{'n':>9} {'lg n':>6} {'n lg n':>11} {'n^2':>18} {'2^n':>17} {'n!':>17}")

    def big(x):
        return f"{x:,}" if x < 10**12 else f"about 10^{len(str(x)) - 1}"
    for n in (10, 20, 50, 100, 1000, 10**6):
        lg = math.log2(n)
        two = big(2**n) if n <= 1000 else "about 10^301029"
        fact = big(math.factorial(n)) if n <= 1000 else "about 10^5565708"
        print(f"{n:>9,} {lg:>6.1f} {n * lg:>11,.0f} {n * n:>18,} {two:>17} {fact:>17}")
    # the last row's exponents, computed without building the huge numbers:
    assert math.floor(10**6 * math.log10(2)) == 301029
    assert math.floor(math.lgamma(10**6 + 1) / math.log(10)) == 5565708
