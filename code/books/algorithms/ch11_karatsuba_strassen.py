"""Chapter 11: Karatsuba multiplication and Strassen's matrix multiplication."""
import random

calls = 0


def karatsuba(x, y):
    """Multiply non-negative integers with three half-size products."""
    global calls
    calls += 1
    if x < 10 or y < 10:
        return x * y                       # one-digit base case
    m = max(len(str(x)), len(str(y))) // 2
    p = 10 ** m
    a, b = divmod(x, p)                    # x = a*10^m + b
    c, d = divmod(y, p)                    # y = c*10^m + d
    ac = karatsuba(a, c)
    bd = karatsuba(b, d)
    mid = karatsuba(a + b, c + d) - ac - bd    # = ad + bc
    return ac * p * p + mid * p + bd


def school_digit_products(n):
    return n * n


def mat_mul(A, B):
    n, m, k = len(A), len(B), len(B[0])
    return [[sum(A[i][t] * B[t][j] for t in range(m)) for j in range(k)] for i in range(n)]


def add(A, B):
    return [[a + b for a, b in zip(r, s)] for r, s in zip(A, B)]


def sub(A, B):
    return [[a - b for a, b in zip(r, s)] for r, s in zip(A, B)]


mults = 0


def strassen(A, B):
    """Multiply n x n matrices, n a power of two, with 7 recursive products."""
    global mults
    n = len(A)
    if n == 1:
        mults += 1
        return [[A[0][0] * B[0][0]]]
    h = n // 2
    def quarter(M, r, c):
        return [row[c:c + h] for row in M[r:r + h]]
    A11, A12, A21, A22 = (quarter(A, 0, 0), quarter(A, 0, h),
                          quarter(A, h, 0), quarter(A, h, h))
    B11, B12, B21, B22 = (quarter(B, 0, 0), quarter(B, 0, h),
                          quarter(B, h, 0), quarter(B, h, h))
    M1 = strassen(add(A11, A22), add(B11, B22))
    M2 = strassen(add(A21, A22), B11)
    M3 = strassen(A11, sub(B12, B22))
    M4 = strassen(A22, sub(B21, B11))
    M5 = strassen(add(A11, A12), B22)
    M6 = strassen(sub(A21, A11), add(B11, B12))
    M7 = strassen(sub(A12, A22), add(B21, B22))
    C11 = add(sub(add(M1, M4), M5), M7)
    C12 = add(M3, M5)
    C21 = add(M2, M4)
    C22 = add(add(sub(M1, M2), M3), M6)
    top = [r1 + r2 for r1, r2 in zip(C11, C12)]
    bottom = [r1 + r2 for r1, r2 in zip(C21, C22)]
    return top + bottom


if __name__ == "__main__":
    x, y = 1234, 5678
    print(f"karatsuba({x}, {y}) = {karatsuba(x, y)}   (check: {x * y})")

    random.seed(1960)
    print("\n digits   recursive calls   n^1.585   schoolbook digit products")
    for digits in (8, 16, 32, 64, 128, 256):
        x = random.randrange(10 ** (digits - 1), 10 ** digits)
        y = random.randrange(10 ** (digits - 1), 10 ** digits)
        calls = 0
        assert karatsuba(x, y) == x * y
        print(f"{digits:7d} {calls:17d} {digits ** 1.585:9.0f} {school_digit_products(digits):12d}")

    A = [[1, 2], [3, 4]]
    B = [[5, 6], [7, 8]]
    print("\nStrassen 2x2:", strassen(A, B), " ordinary:", mat_mul(A, B))
    print("\n   n   scalar mults (Strassen)   n^3 (ordinary)")
    for n in (2, 4, 8, 16, 32):
        A = [[random.randint(-9, 9) for _ in range(n)] for _ in range(n)]
        B = [[random.randint(-9, 9) for _ in range(n)] for _ in range(n)]
        mults = 0
        assert strassen(A, B) == mat_mul(A, B)
        print(f"{n:4d} {mults:25d} {n ** 3:16d}")
