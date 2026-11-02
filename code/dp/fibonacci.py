from functools import lru_cache

calls = 0


def fib_naive(n):
    """Straight from the definition: exponential time, because the same values are worked out again and again."""
    global calls
    calls += 1
    return n if n < 2 else fib_naive(n - 1) + fib_naive(n - 2)


@lru_cache(maxsize=None)
def fib_memo(n):
    """Top-down: the same recursion, but each answer is remembered the first time (memoization)."""
    return n if n < 2 else fib_memo(n - 1) + fib_memo(n - 2)


def fib_table(n):
    """Bottom-up: fill a table from the smallest case upwards (tabulation)."""
    f = [0] * (n + 1)
    if n > 0:
        f[1] = 1
    for i in range(2, n + 1):
        f[i] = f[i - 1] + f[i - 2]
    return f[n]


def fib_two(n):
    """Bottom-up with only the last two values kept: O(1) memory."""
    a, b = 0, 1                              # F(i), F(i+1)
    for _ in range(n):
        a, b = b, a + b
    return a


if __name__ == "__main__":
    print(fib_naive(20), calls)
    print(fib_memo(50), fib_table(50), fib_two(50))
    print([fib_two(i) for i in range(11)])
