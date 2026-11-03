"""Chapter 12.4: Bayesian linear regression. Posterior over weights, predictive mean and
variance, the link to ridge regression, and the evidence choosing a polynomial degree."""
import numpy as np


def posterior(Phi, y, sigma2, tau2):
    """Prior w ~ N(0, tau2 I), noise N(0, sigma2): posterior N(m, S)."""
    d = Phi.shape[1]
    S = np.linalg.inv(Phi.T @ Phi / sigma2 + np.eye(d) / tau2)
    m = S @ Phi.T @ y / sigma2
    return m, S


def log_evidence(Phi, y, sigma2, tau2):
    """log p(y) with y ~ N(0, sigma2 I + tau2 Phi Phi^T), via a Cholesky factor."""
    n = len(y)
    C = sigma2 * np.eye(n) + tau2 * Phi @ Phi.T
    L = np.linalg.cholesky(C)
    z = np.linalg.solve(L, y)
    return -0.5 * z @ z - np.log(np.diag(L)).sum() - 0.5 * n * np.log(2 * np.pi)


print("1. One weight, no intercept: y = w x + noise, prior w ~ N(0, 1), sigma^2 = 1")
x = np.array([[2.0]])
y = np.array([3.0])
m, S = posterior(x, y, 1.0, 1.0)
print(f"   after the point (2, 3): posterior mean {m[0]:.4f}, variance {S[0, 0]:.4f}")
xs = np.array([[2.0], [1.0], [-1.0], [3.0]])
ys = np.array([3.0, 1.0, -2.0, 5.0])
for k in range(1, 5):
    m, S = posterior(xs[:k], ys[:k], 1.0, 1.0)
    print(f"   after {k} points: mean {m[0]:.4f}, sd {np.sqrt(S[0, 0]):.4f}")

rng = np.random.default_rng(12)
n = 12
xtr = np.sort(rng.uniform(-1, 1, n))
ytr = np.sin(3 * xtr) + rng.normal(0, 0.2, n)
sigma2, tau2 = 0.2 ** 2, 1.0


def feats(x, deg):
    return np.vander(x, deg + 1, increasing=True)      # 1, x, x^2, ..., x^deg


print("\n2. Degree-5 polynomial features, 12 points on [-1, 1], noise sd 0.2, prior tau^2 = 1")
Phi = feats(xtr, 5)
m, S = posterior(Phi, ytr, sigma2, tau2)
ridge = np.linalg.solve(Phi.T @ Phi + (sigma2 / tau2) * np.eye(6), Phi.T @ ytr)
print(f"   posterior mean = {np.round(m, 4)}")
print(f"   ridge, lambda = sigma^2/tau^2 = {sigma2 / tau2:.2f}: {np.round(ridge, 4)}")
print("   predictive mean and sd (sd = sqrt(sigma^2 + phi^T S phi))")
print("       x    mean     sd   true f(x)")
for xq in [-1.5, -1.0, -0.5, 0.0, 0.5, 1.0, 1.5]:
    ph = feats(np.array([xq]), 5)[0]
    print(f"   {xq:5.1f}  {ph @ m:6.3f}  {np.sqrt(sigma2 + ph @ S @ ph):5.3f}   {np.sin(3 * xq):6.3f}")

print("\n3. The evidence p(y | degree) for polynomial degrees 0 to 9")
xte = np.linspace(-1, 1, 400)
yte = np.sin(3 * xte) + rng.normal(0, 0.2, 400)
print("   degree   log evidence   train MSE   test MSE (posterior mean)")
for deg in range(10):
    P = feats(xtr, deg)
    m, _ = posterior(P, ytr, sigma2, tau2)
    tr = np.mean((P @ m - ytr) ** 2)
    te = np.mean((feats(xte, deg) @ m - yte) ** 2)
    print(f"   {deg:6d}   {log_evidence(P, ytr, sigma2, tau2):12.3f}   {tr:9.4f}   {te:8.4f}")
