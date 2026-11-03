# Chapter 5: simulated annealing for the travelling salesman problem, from scratch.
# A move reverses a segment of the tour (a 2-opt move). Worse moves are accepted with
# probability exp(-delta / T); the temperature T falls geometrically.
import math
import random
import numpy as np


def make_cities(n, seed):
    rng = np.random.default_rng(seed)
    pts = rng.random((n, 2))
    d = np.sqrt(((pts[:, None, :] - pts[None, :, :]) ** 2).sum(axis=2))
    return pts, d.tolist()                       # lists are faster than arrays for single lookups


def length(tour, d):
    return sum(d[tour[i - 1]][tour[i]] for i in range(len(tour)))


def two_opt_delta(tour, d, i, j):
    """Change in length if tour[i..j] is reversed (0 < i < j < n)."""
    a, b = tour[i - 1], tour[i]
    c, e = tour[j], tour[(j + 1) % len(tour)]
    return d[a][c] + d[b][e] - d[a][b] - d[c][e]


def hill_climb_2opt(tour, d):
    """Apply improving 2-opt moves (first improvement) until none is left: a local minimum."""
    tour, n, improved = tour[:], len(tour), True
    while improved:
        improved = False
        for i in range(1, n - 1):
            for j in range(i + 1, n):
                if two_opt_delta(tour, d, i, j) < -1e-12:
                    tour[i:j + 1] = reversed(tour[i:j + 1])
                    improved = True
    return tour


def anneal(tour, d, rng, t0, t_end, steps, log_every=0):
    tour, n = tour[:], len(tour)
    cur = length(tour, d)
    best, best_tour = cur, tour[:]
    alpha = (t_end / t0) ** (1.0 / steps)          # geometric cooling: T_k = t0 * alpha^k
    t, accepted_worse, log = t0, 0, []
    for k in range(steps):
        i = rng.randrange(1, n - 1)
        j = rng.randrange(i + 1, n)
        delta = two_opt_delta(tour, d, i, j)
        if delta < 0 or rng.random() < math.exp(-delta / t):
            if delta > 0:
                accepted_worse += 1
            tour[i:j + 1] = reversed(tour[i:j + 1])
            cur += delta
            if cur < best:
                best, best_tour = cur, tour[:]
        if log_every and k % log_every == 0:
            log.append((k, t, cur))
        t *= alpha
    return best_tour, best, accepted_worse, log


def held_karp(d):
    """Exact optimum by dynamic programming over subsets (Algorithms book, chapter 13)."""
    n = len(d)
    INF = float("inf")
    dp = [[INF] * n for _ in range(1 << n)]
    dp[1][0] = 0.0
    for mask in range(1 << n):
        if not mask & 1:
            continue
        for last in range(n):
            v = dp[mask][last]
            if v == INF:
                continue
            for nxt in range(1, n):
                if not mask >> nxt & 1:
                    m2 = mask | 1 << nxt
                    w = v + d[last][nxt]
                    if w < dp[m2][nxt]:
                        dp[m2][nxt] = w
    full = (1 << n) - 1
    return min(dp[full][k] + d[k][0] for k in range(1, n))


rng = random.Random(1983)

print("Metropolis acceptance probability exp(-delta/T) for a move that is worse by delta:")
print("   T     delta=0.01  delta=0.05  delta=0.20")
for t in (1.0, 0.1, 0.03, 0.01, 0.001):
    print(f"{t:6.3f}  " + "  ".join(f"{math.exp(-dl / t):10.4f}" for dl in (0.01, 0.05, 0.20)))
print()

# 1. A 12-city instance small enough to know the true optimum.
_, d12 = make_cities(12, 7)
opt = held_karp(d12)
start = list(range(12))
hc = length(hill_climb_2opt(start, d12), d12)
_, sa, _, _ = anneal(start, d12, rng, 0.5, 0.001, 20000)
print(f"12 cities: optimum {opt:.4f}   2-opt hill climbing {hc:.4f}   annealing {sa:.4f}")

# 2. 60 cities: compare one hill climb, the best of many restarts, and annealing.
_, d = make_cities(60, 11)
n = 60
rand_tour = list(range(n))
rng.shuffle(rand_tour)
print(f"\n60 cities, random tour length {length(rand_tour, d):.3f}")
lengths = []
for r in range(20):
    t = list(range(n))
    rng.shuffle(t)
    lengths.append(length(hill_climb_2opt(t, d), d))
print(f"2-opt hill climbing, 20 random starts: best {min(lengths):.3f}  mean {sum(lengths) / 20:.3f}"
      f"  worst {max(lengths):.3f}")
for steps in (20000, 200000):
    tour, best, worse, log = anneal(rand_tour, d, rng, 1.0, 0.0005, steps, log_every=steps // 8)
    print(f"annealing, {steps:6d} steps: best {best:.3f}   worse moves accepted {worse}")
print("\nprogress of the 200000-step run (step, temperature, current length):")
for k, t, cur in log:
    print(f"  {k:6d}  {t:8.4f}  {cur:7.3f}")
