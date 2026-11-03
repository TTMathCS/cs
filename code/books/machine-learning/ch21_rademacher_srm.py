"""Chapter 21: empirical Rademacher complexity measured by Monte Carlo,
compared with Massart's lemma and the B R / sqrt(m) bound for linear classes;
then structural risk minimisation over unions of k intervals."""
from math import e, exp, log, sqrt

import numpy as np

rng = np.random.default_rng(7)

# ------------------------------------------- 1. Rademacher for thresholds
def rademacher_thresholds(x, draws=4000):
    """E_sigma sup_t (1/m) sum sigma_i h_t(x_i), h_t(x) = +1 if x >= t else -1.
    Sorting x lets us evaluate all m+1 thresholds with one cumulative sum."""
    m = len(x)
    order = np.argsort(x)
    sig = rng.choice([-1.0, 1.0], size=(draws, m))[:, order]
    # threshold before position c: points c..m-1 get +1, points 0..c-1 get -1
    total = sig.sum(axis=1, keepdims=True)
    left = np.concatenate([np.zeros((draws, 1)), np.cumsum(sig, axis=1)], axis=1)
    corr = (total - left) - left                      # shape (draws, m+1)
    return corr.max(axis=1).mean() / m

print("1. thresholds on the line: Monte Carlo Rademacher vs Massart sqrt(2 ln(m+1) / m)")
print("     m   measured   Massart")
for m in [10, 40, 160, 640]:
    r = rademacher_thresholds(rng.random(m))
    print(f"  {m:5d}   {r:.4f}    {sqrt(2 * log(m + 1) / m):.4f}")

# ----------------------------------------- 2. Rademacher for linear classes
print("\n2. linear functions w.x with ||w|| <= B = 1 on points with ||x|| <= R = 1 in 10-D")
print("   exact sup is (B/m) ||sum sigma_i x_i||; bound is B R / sqrt(m)")
print("     m   measured   bound")
for m in [10, 40, 160, 640]:
    X = rng.normal(size=(m, 10))
    X /= np.maximum(1.0, np.linalg.norm(X, axis=1, keepdims=True))   # put them in the unit ball
    sig = rng.choice([-1.0, 1.0], size=(4000, m))
    r = np.linalg.norm(sig @ X, axis=1).mean() / m
    print(f"  {m:5d}   {r:.4f}    {1 / sqrt(m):.4f}")

# ------------------------------------ 3. structural risk minimisation
# Target: union of 3 intervals on [0,1]; labels flipped with probability 0.1.
TARGET = [(0.10, 0.25), (0.40, 0.55), (0.70, 0.90)]
def target(x):
    return np.any([(a <= x) & (x <= b) for a, b in TARGET], axis=0)

def erm_k_intervals(x, y, k):
    """Fewest training mistakes using at most k intervals labelled 1 (dynamic
    programming over the sorted points). Returns (mistakes, cut points)."""
    order = np.argsort(x)
    xs, ys = x[order], y[order].astype(int)
    m = len(xs)
    INF = 10 ** 9
    # best[j][s]: mistakes so far having opened j intervals, s = 1 if inside one
    best = np.full((k + 1, 2), INF); best[0, 0] = 0
    back = np.zeros((m, k + 1, 2, 2), dtype=int)       # (prev j, prev s)
    for i in range(m):
        new = np.full((k + 1, 2), INF)
        for j in range(k + 1):
            for s in (0, 1):
                if best[j, s] >= INF: continue
                for s2 in (0, 1):
                    j2 = j + (1 if (s2 == 1 and s == 0) else 0)
                    if j2 > k: continue
                    cost = best[j, s] + (s2 != ys[i])
                    if cost < new[j2, s2]:
                        new[j2, s2] = cost
                        back[i, j2, s2] = (j, s)
        best = new
    j, s = np.unravel_index(np.argmin(best), best.shape)
    mistakes = int(best[j, s])
    labels = np.zeros(m, dtype=int)
    for i in range(m - 1, -1, -1):
        labels[i] = s
        j, s = back[i, j, s]
    # turn the labels into intervals with endpoints halfway between points
    ivals, start = [], None
    for i in range(m):
        if labels[i] and start is None:
            start = xs[i] if i == 0 else (xs[i - 1] + xs[i]) / 2
        if not labels[i] and start is not None:
            ivals.append((start, (xs[i - 1] + xs[i]) / 2)); start = None
    if start is not None:
        ivals.append((start, 1.0))
    return mistakes, ivals

def predict(ivals, x):
    if not ivals: return np.zeros_like(x, dtype=bool)
    return np.any([(a <= x) & (x <= b) for a, b in ivals], axis=0)

m, delta = 300, 0.05
x = rng.random(m)
y = target(x) ^ (rng.random(m) < 0.1)
xt = rng.random(200_000)
yt = target(xt) ^ (rng.random(200_000) < 0.1)
print(f"\n3. SRM over H_k = unions of k intervals (VC dimension 2k); m = {m}, 10% label noise")
print("   penalty(k) = sqrt(2 d ln(e m / d) / m) + sqrt(ln(1 / (delta w_k)) / (2 m)), d = 2k, w_k = 2^-k")
print("    k   train err   penalty   bound    test err")
rows = []
for k in range(1, 11):
    mis, iv = erm_k_intervals(x, y, k)
    d = 2 * k
    pen = sqrt(2 * d * log(e * m / d) / m) + sqrt(log(1 / (delta * 2.0 ** -k)) / (2 * m))
    test = np.mean(predict(iv, xt) != yt)
    rows.append((k, mis / m, pen, mis / m + pen, test))
    print(f"  {k:3d}   {mis / m:9.4f}   {pen:7.4f}   {mis / m + pen:6.4f}   {test:8.4f}")
k_srm = min(rows, key=lambda r: r[3])[0]
k_erm = min(rows, key=lambda r: (r[1], r[0]))[0]
print(f"   SRM picks k = {k_srm}; plain ERM over all k reaches its lowest training error at k = {k_erm}")
mis, iv = erm_k_intervals(x, y, m)
print(f"   with no limit on k: {len(iv)} intervals, train err {mis / m:.4f}, "
      f"test err {np.mean(predict(iv, xt) != yt):.4f}")
