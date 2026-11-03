"""Chapter 19, part 3: matrix exponentiation and the number-theoretic transform."""
import random

MOD = 998_244_353          # = 119 * 2^23 + 1, a prime; 3 is a primitive root
ROOT = 3


def mat_mult(A, B, mod):
    n, m, p = len(A), len(B), len(B[0])
    return [[sum(A[i][k] * B[k][j] for k in range(m)) % mod for j in range(p)]
            for i in range(n)]


def mat_pow(M, e, mod):
    n = len(M)
    R = [[int(i == j) for j in range(n)] for i in range(n)]
    while e:
        if e & 1:
            R = mat_mult(R, M, mod)
        M = mat_mult(M, M, mod)
        e >>= 1
    return R


def fib_mod(n, mod):
    """F(n) mod `mod` from [[1,1],[1,0]]^n = [[F(n+1),F(n)],[F(n),F(n-1)]]."""
    return mat_pow([[1, 1], [1, 0]], n, mod)[0][1]


def fib_doubling(n, mod):
    """Fast doubling: F(2k) = F(k)(2F(k+1) - F(k)), F(2k+1) = F(k)^2 + F(k+1)^2."""
    if n == 0:
        return 0, 1
    a, b = fib_doubling(n >> 1, mod)
    c = a * (2 * b - a) % mod
    d = (a * a + b * b) % mod
    return (d, (c + d) % mod) if n & 1 else (c, d)


def ntt(a, invert=False):
    """In-place iterative Cooley-Tukey transform over Z_MOD; len(a) a power of 2."""
    n = len(a)
    j = 0
    for i in range(1, n):            # bit-reversal permutation
        bit = n >> 1
        while j & bit:
            j ^= bit
            bit >>= 1
        j |= bit
        if i < j:
            a[i], a[j] = a[j], a[i]
    length = 2
    while length <= n:
        w = pow(ROOT, (MOD - 1) // length, MOD)   # a primitive length-th root of unity
        if invert:
            w = pow(w, MOD - 2, MOD)
        for start in range(0, n, length):
            wk = 1
            half = length // 2
            for k in range(start, start + half):
                u, v = a[k], a[k + half] * wk % MOD
                a[k], a[k + half] = (u + v) % MOD, (u - v) % MOD
                wk = wk * w % MOD
        length <<= 1
    if invert:
        n_inv = pow(n, MOD - 2, MOD)
        for i in range(n):
            a[i] = a[i] * n_inv % MOD


def multiply(p, q):
    """Coefficients of p*q mod MOD in O(n log n)."""
    size = 1
    while size < len(p) + len(q) - 1:
        size <<= 1
    fa, fb = p + [0] * (size - len(p)), q + [0] * (size - len(q))
    ntt(fa)
    ntt(fb)
    prod = [x * y % MOD for x, y in zip(fa, fb)]
    ntt(prod, invert=True)
    return prod[:len(p) + len(q) - 1]


def naive_multiply(p, q):
    r = [0] * (len(p) + len(q) - 1)
    for i, x in enumerate(p):
        for j, y in enumerate(q):
            r[i + j] = (r[i + j] + x * y) % MOD
    return r


def big_multiply(x, y):
    """Multiply big integers through their decimal digits and one NTT."""
    a = [int(c) for c in reversed(str(x))]
    b = [int(c) for c in reversed(str(y))]
    c = multiply(a, b)               # each entry < 81 * len, far below MOD
    carry, digits = 0, []
    for v in c:
        carry += v
        digits.append(carry % 10)
        carry //= 10
    while carry:
        digits.append(carry % 10)
        carry //= 10
    return int("".join(map(str, reversed(digits))))


def main():
    print("1. Fibonacci by matrix powers")
    print("   [[1,1],[1,0]]^10 =", mat_pow([[1, 1], [1, 0]], 10, 10**9))
    exact = [0, 1]
    for _ in range(300):
        exact.append(exact[-1] + exact[-2])
    print("   F(300) mod 10^9+7 matches the exact value:",
          fib_mod(300, 10**9 + 7) == exact[300] % (10**9 + 7))
    n = 10**18
    print(f"   F(10^18) mod 10^9+7 = {fib_mod(n, 10**9 + 7)}"
          f" (fast doubling: {fib_doubling(n, 10**9 + 7)[0]})")

    print("2. Number-theoretic transform")
    print("   MOD - 1 =", MOD - 1, "= 119 * 2^23:", MOD - 1 == 119 * 2**23)
    w8 = pow(ROOT, (MOD - 1) // 8, MOD)
    print("   order of w8 = 3^((MOD-1)/8):", [pow(w8, k, MOD) == 1 for k in range(1, 9)].index(True) + 1)
    print("   (1 + 2x + 3x^2)(4 + 5x) =", multiply([1, 2, 3], [4, 5]))
    rng = random.Random(19)
    p = [rng.randrange(MOD) for _ in range(300)]
    q = [rng.randrange(MOD) for _ in range(200)]
    print("   random 300 x 200 product equals the naive one:", multiply(p, q) == naive_multiply(p, q))
    x = rng.getrandbits(3000)
    y = rng.getrandbits(3000)
    print("   3000-bit integers multiplied via NTT equal x*y:", big_multiply(x, y) == x * y)


if __name__ == "__main__":
    main()
