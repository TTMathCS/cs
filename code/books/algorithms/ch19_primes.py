"""Chapter 19, part 2: Fermat and Miller-Rabin tests, Carmichael numbers,
trial division, Pollard's rho and the Chinese remainder theorem."""
import math
import random

from ch19_arithmetic import inverse, sieve

SMALL_PRIMES = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37]


def fermat_test(n, a):
    """True means 'probably prime' for base a."""
    return pow(a, n - 1, n) == 1


def is_strong_liar(n, a):
    """Miller-Rabin round for odd n > 2 and base a: True if a says 'probably prime'."""
    d, s = n - 1, 0
    while d % 2 == 0:
        d //= 2
        s += 1
    x = pow(a, d, n)
    if x == 1 or x == n - 1:
        return True
    for _ in range(s - 1):
        x = x * x % n
        if x == n - 1:
            return True
    return False


def is_prime(n):
    """Deterministic for n < 2^64 with the first twelve primes as bases."""
    if n < 2:
        return False
    for p in SMALL_PRIMES:
        if n % p == 0:
            return n == p
    return all(is_strong_liar(n, a) for a in SMALL_PRIMES)


def trial_division(n):
    factors, d = [], 2
    while d * d <= n:
        while n % d == 0:
            factors.append(d)
            n //= d
        d += 1 if d == 2 else 2
    if n > 1:
        factors.append(n)
    return factors


def pollard_rho(n, c=1, x0=2):
    """Floyd's cycle finding on x -> x^2 + c mod n. Returns a factor (maybe n)."""
    f = lambda x: (x * x + c) % n
    x = y = x0
    d = 1
    while d == 1:
        x = f(x)          # tortoise: one step
        y = f(f(y))       # hare: two steps
        d = math.gcd(abs(x - y), n)
    return d


def factor(n, rng=random.Random(19)):
    """Full factorization: small primes, then Miller-Rabin and Pollard's rho."""
    if n == 1:
        return []
    for p in SMALL_PRIMES:
        if n % p == 0:
            return [p] + factor(n // p, rng)
    if is_prime(n):
        return [n]
    while True:
        d = pollard_rho(n, c=rng.randrange(1, n), x0=rng.randrange(0, n))
        if d != n:
            return sorted(factor(d, rng) + factor(n // d, rng))


def crt(residues, moduli):
    """Solve x = r_i mod m_i for pairwise coprime m_i; return (x, M)."""
    x, M = 0, 1
    for r, m in zip(residues, moduli):
        # x is right mod M; add a multiple of M to fix it mod m
        t = (r - x) * inverse(M, m) % m
        x, M = x + M * t, M * m
    return x % M, M


def main():
    print("1. Carmichael numbers below 100000, by Korselt's criterion")
    N = 100_000
    flags = sieve(N)
    def korselt(n):     # composite, squarefree, and p - 1 divides n - 1 for each prime p | n
        ps = trial_division(n)
        return len(ps) > 1 and len(set(ps)) == len(ps) and all((n - 1) % (p - 1) == 0 for p in ps)
    carm = [n for n in range(3, N, 2) if not flags[n] and korselt(n)]
    assert all(pow(a, n - 1, n) == 1 for n in carm for a in range(2, 200) if math.gcd(a, n) == 1)
    print("  ", carm)
    print("   561 = ", trial_division(561), " 2^560 mod 561 =", pow(2, 560, 561))

    print("2. Miller-Rabin on 561 with base 2")
    d, s = 560, 0
    while d % 2 == 0:
        d //= 2
        s += 1
    seq = [pow(2, d * 2**j, 561) for j in range(s + 1)]
    print(f"   560 = 2^{s} * {d}; 2^({d}*2^j) mod 561 for j = 0..{s}: {seq}")

    print("3. Share of bases that lie, for some odd composites")
    for n in (91, 561, 1105, 8911, 65):
        units = [a for a in range(1, n) if math.gcd(a, n) == 1]
        fermat = sum(fermat_test(n, a) for a in range(1, n))
        strong = sum(is_strong_liar(n, a) for a in range(1, n))
        print(f"   n={n:5d}: phi(n)={len(units):5d}, Fermat liars {fermat:4d},"
              f" strong liars {strong:4d} = {strong/len(units):.3f} phi(n)")

    print("4. Miller-Rabin with 12 bases agrees with the sieve up to 1000000")
    M = 1_000_000
    flags = sieve(M)
    print("   agree:", all(is_prime(n) == bool(flags[n]) for n in range(M + 1)))
    print("   2^61 - 1 prime?", is_prime(2**61 - 1), "  2^61 + 1 prime?", is_prime(2**61 + 1))

    print("5. Pollard's rho")
    x, y, i = 2, 2, 0
    f = lambda v: (v * v + 1) % 8051
    while True:
        x, y, i = f(x), f(f(y)), i + 1
        g = math.gcd(abs(x - y), 8051)
        print(f"   i={i}: x={x:5d} y={y:5d} gcd={g}")
        if g != 1:
            break
    for n in (8051, 10403, 600851475143, 2**64 + 1, (2**31 - 1) * (2**61 - 1)):
        print(f"   {n} = {' * '.join(map(str, factor(n)))}")

    print("6. Chinese remainder theorem")
    print("   x = 2 mod 3, 3 mod 5, 2 mod 7:", crt([2, 3, 2], [3, 5, 7]))
    print("   x = 1 mod 4, 2 mod 9, 3 mod 25:", crt([1, 2, 3], [4, 9, 25]))


if __name__ == "__main__":
    main()
