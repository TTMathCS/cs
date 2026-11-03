"""Chapter 3: recursive functions, the call stack made visible, and Python's limit."""
import sys


def factorial(n, depth=0, trace=False):
    pad = "    " * depth
    if trace:
        print(f"{pad}call factorial({n})")
    if n == 0:
        result = 1                                   # base case
    else:
        result = n * factorial(n - 1, depth + 1, trace)  # recursive case
    if trace:
        print(f"{pad}factorial({n}) returns {result}")
    return result


def total(a, i=0):
    """Sum of a[i:], by recursion on the length of the rest."""
    if i == len(a):
        return 0
    return a[i] + total(a, i + 1)


def power(x, n):
    """x**n for a whole number n >= 0, by repeated squaring."""
    if n == 0:
        return 1
    half = power(x, n // 2)
    if n % 2 == 0:
        return half * half
    return half * half * x


def power_count(n):
    """Number of calls power(x, n) makes, including the first."""
    return 1 if n == 0 else 1 + power_count(n // 2)


def factorial_loop(n):
    result = 1
    for k in range(2, n + 1):
        result *= k
    return result


def depth_reached(f):
    """Deepest recursion f can reach before RecursionError."""
    n = 1
    while True:
        try:
            f(n)
        except RecursionError:
            return n
        n += 50


if __name__ == "__main__":
    print("The call stack of factorial(3):")
    factorial(3, trace=True)
    print()
    print("total([4, 8, 15, 16, 23, 42]) =", total([4, 8, 15, 16, 23, 42]))
    print("power(3, 13) =", power(3, 13), "  check:", 3**13)
    for n in (13, 1000, 10**6, 10**18):
        print(f"  power(x, {n}) makes {power_count(n)} calls; n.bit_length() + 1 = {n.bit_length() + 1}")
    assert all(power(2, n) == 2**n for n in range(200))
    assert all(factorial(n) == factorial_loop(n) for n in range(100))
    print()
    print("Python's recursion limit:", sys.getrecursionlimit())
    print("factorial fails at about depth", depth_reached(factorial))
    print("factorial_loop(20000) has", factorial_loop(20000).bit_length(), "bits: a loop has no such limit")
