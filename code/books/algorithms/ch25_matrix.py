# Chapter 25: why the exponent of matrix multiplication drops below 3.
# Strassen's 7-product scheme, checked on random matrices, with exact counts
# of scalar multiplications against the schoolbook n^3.
import math
import random


def add(A, B):
    return [[a + b for a, b in zip(r, s)] for r, s in zip(A, B)]


def sub(A, B):
    return [[a - b for a, b in zip(r, s)] for r, s in zip(A, B)]


def naive(A, B, count):
    n = len(A)
    count[0] += n ** 3
    return [[sum(A[i][k] * B[k][j] for k in range(n)) for j in range(n)] for i in range(n)]


def strassen(A, B, count, cutoff=1):
    n = len(A)
    if n <= cutoff:
        return naive(A, B, count)
    h = n // 2
    q = lambda M, r, c: [row[c * h:(c + 1) * h] for row in M[r * h:(r + 1) * h]]
    A11, A12, A21, A22 = q(A, 0, 0), q(A, 0, 1), q(A, 1, 0), q(A, 1, 1)
    B11, B12, B21, B22 = q(B, 0, 0), q(B, 0, 1), q(B, 1, 0), q(B, 1, 1)
    M1 = strassen(add(A11, A22), add(B11, B22), count, cutoff)
    M2 = strassen(add(A21, A22), B11, count, cutoff)
    M3 = strassen(A11, sub(B12, B22), count, cutoff)
    M4 = strassen(A22, sub(B21, B11), count, cutoff)
    M5 = strassen(add(A11, A12), B22, count, cutoff)
    M6 = strassen(sub(A21, A11), add(B11, B12), count, cutoff)
    M7 = strassen(sub(A12, A22), add(B21, B22), count, cutoff)
    C11 = add(sub(add(M1, M4), M5), M7)
    C12 = add(M3, M5)
    C21 = add(M2, M4)
    C22 = add(sub(add(M1, M3), M2), M6)
    return [r1 + r2 for r1, r2 in zip(C11, C12)] + [r1 + r2 for r1, r2 in zip(C21, C22)]


rng = random.Random(1969)
print("    n   schoolbook mults   Strassen mults (to 1x1)   ratio   7^k / 8^k")
for k in range(1, 7):
    n = 2 ** k
    A = [[rng.randint(-9, 9) for _ in range(n)] for _ in range(n)]
    B = [[rng.randint(-9, 9) for _ in range(n)] for _ in range(n)]
    c1, c2 = [0], [0]
    assert naive(A, B, c1) == strassen(A, B, c2)
    print(f"{n:5d}   {c1[0]:16d}   {c2[0]:23d}   {c2[0] / c1[0]:.3f}   {7 ** k / 8 ** k:.3f}")
print(f"exponent log2(7) = {math.log2(7):.4f}")
print()
# The exponent from a scheme that multiplies k x k matrices with r products:
for k, r, who in [(2, 8, "schoolbook"), (2, 7, "Strassen 1969"), (3, 23, "Laderman 1976"),
                  (3, 21, "hypothetical: 21 products for 3x3")]:
    print(f"  {k}x{k} with {r:2d} products -> exponent log_{k}({r}) = {math.log(r, k):.4f}   ({who})")
