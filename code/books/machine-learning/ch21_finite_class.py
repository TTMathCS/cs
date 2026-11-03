"""Chapter 21: Hoeffding's inequality and the finite-class PAC bounds,
checked by simulation on threshold classifiers over [0, 1]."""
from math import ceil, exp, log, sqrt

import numpy as np

rng = np.random.default_rng(21)

# ------------------------------------------------------------ 1. Hoeffding
print("1. Hoeffding: P(|mean - p| >= eps) for m coin flips")
print("    p     m    eps   simulated   bound 2exp(-2 m eps^2)")
for p, m, eps in [(0.5, 100, 0.1), (0.1, 100, 0.1), (0.5, 400, 0.05), (0.5, 400, 0.1)]:
    means = (rng.random((50_000, m)) < p).mean(axis=1)
    freq = np.mean(np.abs(means - p) >= eps - 1e-12)
    print(f"  {p:4.1f} {m:5d} {eps:5.2f}   {freq:9.5f}   {2 * exp(-2 * m * eps * eps):9.5f}")

# ------------------------------------- 2. realizable case, finite class
# H = { h_k(x) = 1[x >= k/100] : k = 0..100 }, |H| = 101; target k* = 37.
# x ~ Uniform[0, 1]; the true error of h_k is |k - 37| / 100.
H_SIZE, KSTAR = 101, 37
eps, delta = 0.05, 0.05
m_bound = ceil((log(H_SIZE) + log(1 / delta)) / eps)
print(f"\n2. realizable: |H| = {H_SIZE}, eps = {eps}, delta = {delta}")
print(f"   bound says m >= (ln|H| + ln(1/delta)) / eps = {m_bound}")
print("   m    P(worst consistent h has error > eps)")
trials = 20_000
for m in [20, 40, 60, 80, 100, m_bound]:
    x = rng.random((trials, m))
    k = np.floor(x * 100).astype(int)            # point x lies in [k/100, (k+1)/100)
    left = np.where(x < KSTAR / 100, k, -1).max(axis=1)      # last cell left of target
    right = np.where(x >= KSTAR / 100, k, 100).min(axis=1)   # first cell right of it
    # consistent thresholds: kmin = left + 1 ... kmax = right (h_k labels x as 1 iff k <= 100 x)
    worst = np.maximum(KSTAR - (left + 1), right - KSTAR) / 100
    print(f"  {m:4d}   {np.mean(worst > eps):.4f}")

# ------------------------------------------- 3. agnostic case, finite class
# Same class, but each label is flipped with probability 0.1.
# True error of h_k: 0.1 + 0.8 |k - 37| / 100; the best in H has error 0.1.
print("\n3. agnostic: labels flipped with probability 0.1, ERM over the same 101 thresholds")
print("    m    mean sup|L_S - L|   95th pct   bound sqrt(ln(2|H|/delta)/(2m))   mean excess risk")
grid = np.arange(H_SIZE) / 100
true_err = 0.1 + 0.8 * np.abs(np.arange(H_SIZE) - KSTAR) / 100
for m in [100, 400, 1600]:
    trials = 1000
    x = rng.random((trials, m))
    y = (x >= KSTAR / 100) ^ (rng.random((trials, m)) < 0.1)
    train = np.empty((trials, H_SIZE))
    for j, t in enumerate(grid):
        train[:, j] = np.mean((x >= t) != y, axis=1)
    sup_gap = np.abs(train - true_err).max(axis=1)
    erm = train.argmin(axis=1)
    excess = true_err[erm] - 0.1
    bound = sqrt(log(2 * H_SIZE / delta) / (2 * m))
    print(f"  {m:5d}   {sup_gap.mean():.4f}            {np.quantile(sup_gap, 0.95):.4f}     "
          f"{bound:.4f}                            {excess.mean():.4f}")

# ------------------------------------------------------- 4. sample sizes
print("\n4. samples needed for eps = 0.05, delta = 0.05")
print("        |H|        realizable   agnostic")
for size, name in [(10, "10"), (1e3, "1e3"), (1e6, "1e6"), (2.0 ** 64, "2^64")]:
    real = ceil((log(size) + log(1 / delta)) / eps)
    agn = ceil(log(2 * size / delta) / (2 * eps * eps))
    print(f"  {name:>10s}   {real:10d}   {agn:8d}")
