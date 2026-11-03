# Chapter 20: learning a reward from pairwise preferences (the Bradley-Terry model used by
# Christiano et al. 2017), and what happens when we optimise hard against the learned reward.
import numpy as np

rng = np.random.default_rng(0)
np.set_printoptions(suppress=True)
d = 4


def true_reward(X):
    """What the person actually wants: more of feature 0 is good, but only up to a point,
    plus a little of feature 1. Features 2 and 3 do not matter."""
    return X[:, 0] - 0.25 * X[:, 0] ** 2 + 0.5 * X[:, 1]


# 1. Preferences are collected on ordinary outputs, drawn from N(0, 0.5^2) per feature.
m = 2000
A, B = rng.normal(0, 0.5, (m, d)), rng.normal(0, 0.5, (m, d))
p_true = 1 / (1 + np.exp(-(true_reward(A) - true_reward(B))))   # Bradley-Terry: P(A preferred)
pref = (rng.random(m) < p_true).astype(float)                    # noisy human choices

# 2. Fit a linear reward r(x) = w . x by logistic regression on the differences A - B.
D = A - B
w = np.zeros(d)
for _ in range(3000):
    p = 1 / (1 + np.exp(-D @ w))
    w -= 0.5 * D.T @ (p - pref) / m
print("learned reward weights:", np.round(w, 3), "  (true slope at 0: 1.0, 0.5, 0, 0)")
At, Bt = rng.normal(0, 0.5, (20000, d)), rng.normal(0, 0.5, (20000, d))
agree = np.mean(((At - Bt) @ w > 0) == (true_reward(At) > true_reward(Bt)))
print(f"on fresh pairs from the same distribution the learned reward agrees with the truth {agree:.3f} of the time")

# 3. Optimise against the learned reward by best-of-n: draw n candidates from the base distribution
#    N(0, 1) and keep the one the learned reward likes best. KL(best-of-n || base) = log n - (n-1)/n.
print("\nbest-of-n against the learned reward (averages over 400 repetitions)")
print("        n    KL (nats)   learned reward   true reward of the chosen output")
for n in (1, 4, 16, 64, 256, 1024, 4096, 16384):
    lr, tr = [], []
    for _ in range(400):
        C = rng.normal(0, 1, (n, d))
        k = np.argmax(C @ w)
        lr.append(C[k] @ w); tr.append(true_reward(C[k:k + 1])[0])
    print(f"   {n:>6}    {np.log(n) - (n - 1) / n:6.2f}       {np.mean(lr):7.3f}          {np.mean(tr):7.3f}")
print("\nthe part of the true reward that depends on feature 0, x - x^2/4, is largest (1.0) at x = 2;")
print("the learned linear reward keeps asking for more of feature 0 for ever.")
