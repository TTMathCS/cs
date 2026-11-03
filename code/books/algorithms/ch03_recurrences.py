"""Chapter 3: compute recurrences exactly and compare with their closed forms,
and a small master-theorem helper for T(n) = a T(n/b) + n^d.
"""
import math
from functools import lru_cache


def make_T(a, b, f, base=1):
    """T(1) = base, T(n) = a*T(n // b) + f(n)."""
    @lru_cache(maxsize=None)
    def T(n):
        if n <= 1:
            return base
        return a * T(n // b) + f(n)
    return T


def pw(e):
    """n^e written nicely."""
    if abs(e - round(e)) < 1e-12:
        e = round(e)
        return "1" if e == 0 else "n" if e == 1 else f"n^{e}"
    return f"n^{e:.3f}"


def master(a, b, d):
    """Growth of T(n) = a T(n/b) + Theta(n^d), by the master theorem."""
    crit = math.log(a, b)                     # the critical exponent log_b a
    if abs(d - crit) < 1e-12:
        core = "log n" if d == 0 else f"{pw(d)} log n"
        return f"Theta({core})".ljust(20) + "case 2: d = log_b a"
    if d < crit:
        return f"Theta({pw(crit)})".ljust(20) + f"case 1: d < log_b a = {crit:.3f}"
    return f"Theta({pw(d)})".ljust(20) + f"case 3: d > log_b a = {crit:.3f}"


if __name__ == "__main__":
    cases = [
        ("T(n) = T(n/2) + 1      (binary search)", 1, 2, lambda n: 1, lambda n: math.log2(n) + 1),
        ("T(n) = 2T(n/2) + n     (merge sort)", 2, 2, lambda n: n, lambda n: n * math.log2(n) + n),
        ("T(n) = 2T(n/2) + 1     (tree sum)", 2, 2, lambda n: 1, lambda n: 2 * n - 1),
        ("T(n) = 4T(n/2) + n", 4, 2, lambda n: n, lambda n: 2 * n * n - n),
        ("T(n) = 3T(n/2) + n     (Karatsuba)", 3, 2, lambda n: n, lambda n: 3 * n**math.log2(3) - 2 * n),
        ("T(n) = 2T(n/2) + n^2", 2, 2, lambda n: n * n, lambda n: 2 * n * n - n),
    ]
    for name, a, b, f, closed in cases:
        T = make_T(a, b, f)
        print(name)
        for k in (4, 10, 20):
            n = 2**k
            print(f"   n = 2^{k:<2}  T(n) = {T(n):>15,}   closed form = {closed(n):>17,.1f}")
            assert abs(T(n) - closed(n)) < 1e-6 * T(n)
    print()
    for a, b, d in [(1, 2, 0), (2, 2, 1), (2, 2, 0), (4, 2, 1), (3, 2, 1), (2, 2, 2), (7, 2, 2), (9, 3, 2)]:
        print(f"  a={a} b={b} d={d}:  {master(a, b, d)}")

    print()
    print("Not an exact power: T(n) = T(floor(n/2)) + T(ceil(n/2)) + n, T(1) = 0")

    @lru_cache(maxsize=None)
    def M(n):
        return 0 if n <= 1 else M(n // 2) + M((n + 1) // 2) + n
    for n in (1000, 10**6):
        print(f"   n = {n:>8}:  T(n) = {M(n):>10,}   n lg n = {n * math.log2(n):>12,.0f}"
              f"   ratio {M(n) / (n * math.log2(n)):.4f}")
