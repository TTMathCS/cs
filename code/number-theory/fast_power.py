def power(a, n):
    """a to the power n with O(log n) multiplications (square and multiply)."""
    result = 1
    while n > 0:
        if n & 1:                            # this binary digit of n is 1: include the current square
            result *= a
        a *= a                               # a, a^2, a^4, a^8, ...
        n >>= 1
    return result


def power_mod(a, n, m):
    """a^n mod m, keeping every number below m."""
    result, a = 1 % m, a % m
    while n > 0:
        if n & 1:
            result = result * a % m
        a = a * a % m
        n >>= 1
    return result


def mat_mult(X, Y):
    return [[X[0][0] * Y[0][0] + X[0][1] * Y[1][0], X[0][0] * Y[0][1] + X[0][1] * Y[1][1]],
            [X[1][0] * Y[0][0] + X[1][1] * Y[1][0], X[1][0] * Y[0][1] + X[1][1] * Y[1][1]]]


def fib(n):
    """The nth Fibonacci number from the matrix [[1, 1], [1, 0]] to the power n."""
    result, M = [[1, 0], [0, 1]], [[1, 1], [1, 0]]
    while n > 0:
        if n & 1:
            result = mat_mult(result, M)
        M = mat_mult(M, M)
        n >>= 1
    return result[0][1]


if __name__ == "__main__":
    print(power(2, 10), power(3, 13), power(7, 0))
    MOD = 1_000_000_007
    print(power_mod(2, 1_000_000, MOD), power_mod(3, MOD - 2, MOD) * 3 % MOD)
    print(power_mod(5, 117, 19), fib(10), fib(90))
