"""Chapter 22: interpretability from scratch. Coefficients, permutation
importance, exact Shapley values by enumerating coalitions, and gradient
saliency with its saturation problem."""
from itertools import combinations
from math import factorial

import numpy as np

rng = np.random.default_rng(42)


def sigmoid(z):
    return 1.0 / (1.0 + np.exp(-z))


def fit_logreg(X, y, lam=1e-3, steps=100):
    n, d = X.shape
    Xb = np.hstack([X, np.ones((n, 1))]); w = np.zeros(d + 1)
    for _ in range(steps):
        p = sigmoid(Xb @ w)
        g = Xb.T @ (p - y) / n + lam * w
        H = (Xb * (p * (1 - p))[:, None]).T @ Xb / n + lam * np.eye(d + 1)
        w -= np.linalg.solve(H, g)
    return w


# Four features: x1 strong, x2 weak, x3 = a noisy copy of x1, x4 unrelated.
n = 4000
x1 = rng.normal(size=n); x2 = rng.normal(size=n)
x3 = x1 + 0.3 * rng.normal(size=n); x4 = rng.normal(size=n)
X = np.column_stack([x1, x2, x3, x4])
y = (rng.random(n) < sigmoid(2.0 * x1 + 0.5 * x2)).astype(float)
names = ["x1 strong", "x2 weak", "x3 copy of x1", "x4 noise"]
tr, te = np.arange(n) < 3000, np.arange(n) >= 3000
w = fit_logreg(X[tr], y[tr])
logit = lambda Z: Z @ w[:-1] + w[-1]

def log_loss(Z, yy):
    p = np.clip(sigmoid(logit(Z)), 1e-12, 1 - 1e-12)
    return -np.mean(yy * np.log(p) + (1 - yy) * np.log(1 - p))

print("1. coefficients (features all have standard deviation about 1)")
for nm, c in zip(names, w[:-1]):
    print(f"   {nm:14s} {c:+.3f}")

print("\n2. permutation importance on the test set: rise in log loss when one column is shuffled")
base = log_loss(X[te], y[te])
for j, nm in enumerate(names):
    rises = []
    for rep in range(20):
        Z = X[te].copy(); Z[:, j] = rng.permutation(Z[:, j])
        rises.append(log_loss(Z, y[te]) - base)
    print(f"   {nm:14s} {np.mean(rises):+.4f}  (+/- {np.std(rises):.4f})")
# refit without x1: its noisy copy takes over
w234 = fit_logreg(X[tr][:, [1, 2, 3]], y[tr])
Z = X[te][:, [1, 2, 3]]
p = np.clip(sigmoid(Z @ w234[:-1] + w234[-1]), 1e-12, 1 - 1e-12)
ll = -np.mean(y[te] * np.log(p) + (1 - y[te]) * np.log(1 - p))
print(f"   refit without x1: coefficient of x3 becomes {w234[1]:+.3f}; test log loss {ll:.4f} vs {base:.4f}")

print("\n3. exact Shapley values of the model's logit for one person, by all 2^4 coalitions")
background = X[tr][:200]
x0 = np.array([1.5, -1.0, 1.2, 0.8])

def value(S, f):
    """v(S) = average of f when the features in S are set to x0 and the others
    keep their background values (the 'interventional' value function)."""
    Z = background.copy()
    Z[:, list(S)] = x0[list(S)]
    return f(Z).mean()

def shapley(f, d=4):
    phi = np.zeros(d)
    for j in range(d):
        others = [k for k in range(d) if k != j]
        for size in range(d):
            for S in combinations(others, size):
                weight = factorial(size) * factorial(d - size - 1) / factorial(d)
                phi[j] += weight * (value(S + (j,), f) - value(S, f))
    return phi

phi = shapley(logit)
print("   feature        Shapley    w_j (x0_j - mean_j)")
for j, nm in enumerate(names):
    print(f"   {nm:14s} {phi[j]:+.4f}    {w[j] * (x0[j] - background[:, j].mean()):+.4f}")
print(f"   sum of Shapley values {phi.sum():+.4f} = f(x0) - E f(background) = "
      f"{logit(x0[None])[0] - logit(background).mean():+.4f}")
prob = lambda Z: sigmoid(logit(Z))
phip = shapley(prob)
print(f"   on the probability scale: {np.array2string(phip, precision=4, sign='+')}, sum {phip.sum():+.4f}"
      f" = {prob(x0[None])[0] - prob(background).mean():+.4f}")

print("\n4. gradient saliency d P(y=1) / d x = p (1 - p) w, for three people")
for x in [np.array([0.1, 0.0, 0.1, 0.0]), np.array([1.5, -1.0, 1.2, 0.8]), np.array([4.0, 1.0, 4.0, 0.0])]:
    p = prob(x[None])[0]
    grad = p * (1 - p) * w[:-1]
    print(f"   x = {x}, P = {p:.4f}, gradient = {np.array2string(grad, precision=4, sign='+')}")
