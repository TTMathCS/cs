def sieve(n):
    """Sieve of Eratosthenes: is_prime[k] for every k from 0 to n."""
    is_prime = [True] * (n + 1)
    is_prime[0] = False
    if n >= 1:
        is_prime[1] = False
    p = 2
    while p * p <= n:
        if is_prime[p]:
            for k in range(p * p, n + 1, p):  # smaller multiples were crossed out by smaller primes
                is_prime[k] = False
        p += 1
    return is_prime


def smallest_factors(n):
    """spf[k] = the smallest prime that divides k (for k >= 2): factor any k <= n in O(log k) steps."""
    spf = list(range(n + 1))
    p = 2
    while p * p <= n:
        if spf[p] == p:                      # p is prime
            for k in range(p * p, n + 1, p):
                if spf[k] == k:
                    spf[k] = p
        p += 1
    return spf


def factorize(k, spf):
    out = []
    while k > 1:
        out.append(spf[k])
        k //= spf[k]
    return out


if __name__ == "__main__":
    is_p = sieve(50)
    print([k for k in range(51) if is_p[k]])
    print(sum(sieve(1_000_000)))
    spf = smallest_factors(10_000)
    print(factorize(360, spf), factorize(9973, spf), factorize(2024, spf))
