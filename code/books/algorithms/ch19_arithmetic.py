"""Chapter 19, part 1: Euclid, extended Euclid, fast powers, inverses, sieves."""
import time


def gcd_steps(a, b):
    """Euclid's algorithm; returns the gcd and the number of division steps."""
    steps = 0
    while b:
        a, b = b, a % b
        steps += 1
    return a, steps


def ext_gcd(a, b):
    """Return (g, x, y) with a*x + b*y = g = gcd(a, b), iteratively.
    Invariant: a0*x0 + b0*y0 = r0 and a0*x1 + b0*y1 = r1."""
    r0, r1 = a, b
    x0, x1, y0, y1 = 1, 0, 0, 1
    while r1:
        q = r0 // r1
        r0, r1 = r1, r0 - q * r1
        x0, x1 = x1, x0 - q * x1
        y0, y1 = y1, y0 - q * y1
    return r0, x0, y0


def inverse(a, m):
    g, x, _ = ext_gcd(a % m, m)
    if g != 1:
        raise ValueError(f"{a} has no inverse mod {m}")
    return x % m


def power_mod(base, exp, mod):
    """Right-to-left square and multiply: about log2(exp) squarings."""
    result, base = 1 % mod, base % mod
    while exp > 0:
        if exp & 1:
            result = result * base % mod
        base = base * base % mod
        exp >>= 1
    return result


def sieve(n):
    """Eratosthenes: is_prime[k] for 0 <= k <= n, crossing off from p*p."""
    is_prime = bytearray([1]) * (n + 1)
    is_prime[0:2] = b"\x00\x00"
    p = 2
    while p * p <= n:
        if is_prime[p]:
            is_prime[p * p::p] = bytes(len(range(p * p, n + 1, p)))
        p += 1
    return is_prime


def linear_sieve(n):
    """Each composite is crossed off once, by its least prime factor.
    Returns the primes and lp[k] = least prime factor of k."""
    lp = [0] * (n + 1)
    primes = []
    for i in range(2, n + 1):
        if lp[i] == 0:
            lp[i] = i
            primes.append(i)
        for p in primes:
            if p > lp[i] or i * p > n:
                break
            lp[i * p] = p
    return primes, lp


def main():
    print("1. Euclid on consecutive Fibonacci numbers (the worst case)")
    fib = [0, 1]
    while len(fib) < 40:
        fib.append(fib[-1] + fib[-2])
    for k in (5, 10, 20, 30):
        g, steps = gcd_steps(fib[k + 2], fib[k + 1])
        print(f"   gcd(F{k+2}={fib[k+2]}, F{k+1}={fib[k+1]}) = {g} in {steps} steps")
    worst = max(gcd_steps(a, b)[1] for a in range(1, 1000) for b in range(1, a + 1))
    print("   most steps for any 1 <= b <= a < 1000:", worst)

    print("2. Extended Euclid")
    for a, b in ((240, 46), (3120, 17), (99, 78)):
        g, x, y = ext_gcd(a, b)
        print(f"   {a}*({x}) + {b}*({y}) = {g}")
    print("   inverse of 17 mod 3120 =", inverse(17, 3120), " Python's pow:", pow(17, -1, 3120))

    print("3. Fast powers")
    print("   3^200 mod 13 =", power_mod(3, 200, 13), " 7^560 mod 561 =", power_mod(7, 560, 561))
    big = power_mod(2, 10**18, 10**9 + 7)
    print("   2^(10^18) mod (10^9+7) =", big, " same as pow():", big == pow(2, 10**18, 10**9 + 7))

    print("4. Sieves")
    n = 2_000_000
    t = time.perf_counter()
    flags = sieve(n)
    t1 = time.perf_counter() - t
    t = time.perf_counter()
    primes, lp = linear_sieve(n)
    t2 = time.perf_counter() - t
    print(f"   primes up to {n}: {sum(flags)} (Eratosthenes) and {len(primes)} (linear)")
    print(f"   times: slice-based Eratosthenes {t1:.2f}s, pure-Python linear sieve {t2:.2f}s")
    x, f = 360360, []
    while x > 1:
        f.append(lp[x])
        x //= lp[x]
    print("   360360 factored with the lp table:", f)
    crossings = sum(len(range(p * p, n + 1, p)) for p in range(2, int(n**0.5) + 1) if flags[p])
    print(f"   Eratosthenes crossings: {crossings} = {crossings / n:.3f} n;"
          f" linear sieve: {n + 1 - 2 - len(primes)} (one per composite)")


if __name__ == "__main__":
    main()
