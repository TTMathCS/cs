"""Chapter 21: Markov, Chebyshev and Chernoff against the exact tail, and amplification by majority vote."""
from math import comb, exp, log, ceil


def binomial_tail_at_least(n, p, t):
    """Exact P[X >= t] for X ~ Binomial(n, p)."""
    return sum(comb(n, i) * p**i * (1 - p)**(n - i) for i in range(t, n + 1))


n, p = 100, 0.5
mu, var = n * p, n * p * (1 - p)
print(f"X = number of heads in {n} fair coin flips: mean {mu}, variance {var}")
print(f"{'t':>4} {'exact P[X>=t]':>15} {'Markov':>9} {'Chebyshev':>10} {'Chernoff':>11}")
for t in (60, 70, 75, 90):
    delta = t / mu - 1
    markov = mu / t
    chebyshev = var / (t - mu) ** 2          # bounds P[|X - mu| >= t - mu], so also the one-sided tail
    chernoff = exp(-delta**2 * mu / (2 + delta))
    print(f"{t:>4} {binomial_tail_at_least(n, p, t):15.3e} {markov:9.3f} {min(1, chebyshev):10.4f} {chernoff:11.3e}")

print("\nAmplifying a Monte Carlo test that is wrong with probability 1/3, by a majority of k runs")
print(f"{'k':>4} {'exact error':>13} {'Chernoff bound':>15}")
for k in (1, 5, 11, 31, 101):
    wrong_majority = binomial_tail_at_least(k, 1 / 3, k // 2 + 1)   # more than half the runs wrong
    mu_k = k / 3
    delta = (k / 2) / mu_k - 1                                         # = 1/2
    bound = exp(-delta**2 * mu_k / (2 + delta))
    print(f"{k:>4} {wrong_majority:13.3e} {min(1, bound):15.3e}")

print("\nOne-sided error: repeat a test that succeeds with probability q, until it has succeeded once")
for q, target in ((0.5, 1e-9), (0.01, 1e-6), (2 / (50 * 49), 1 / 50)):
    runs = ceil(log(1 / target) / q)                # (1 - q)^runs <= e^(-q runs) <= target
    print(f"  q = {q:.6f}: {runs:6} runs give failure <= {(1 - q) ** runs:.2e} (target {target:.0e})")
