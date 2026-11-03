"""Chapter 12.6: Gaussian process regression from scratch: prior samples, the posterior
mean and variance by Cholesky, and the length scale chosen by the marginal likelihood."""
import numpy as np


def rbf(a, b, ell, s2=1.0):
    return s2 * np.exp(-0.5 * (a[:, None] - b[None, :]) ** 2 / ell ** 2)


def gp_posterior(x, y, xq, ell, noise2, s2=1.0):
    K = rbf(x, x, ell, s2) + noise2 * np.eye(len(x))
    L = np.linalg.cholesky(K)                              # K = L L^T, O(n^3) once
    alpha = np.linalg.solve(L.T, np.linalg.solve(L, y))    # (K + noise I)^-1 y
    Ks = rbf(x, xq, ell, s2)
    mean = Ks.T @ alpha
    V = np.linalg.solve(L, Ks)
    var = s2 - (V ** 2).sum(0)                             # diag of Kss - Ks^T K^-1 Ks
    logml = -0.5 * y @ alpha - np.log(np.diag(L)).sum() - 0.5 * len(x) * np.log(2 * np.pi)
    return mean, var, logml, -0.5 * y @ alpha, -np.log(np.diag(L)).sum()


rng = np.random.default_rng(13)
print("1. Three functions drawn from the GP prior (RBF kernel, length scale 1), at x = 0, 0.5, ..., 3")
xg = np.arange(0, 3.01, 0.5)
Kg = rbf(xg, xg, 1.0) + 1e-10 * np.eye(len(xg))
Lg = np.linalg.cholesky(Kg)
for k in range(3):
    print("   ", np.round(Lg @ rng.normal(0, 1, len(xg)), 3))
print(f"   prior correlation of f(0) with f(0.5), f(1), f(2), f(3): "
      f"{np.round(rbf(np.array([0.0]), np.array([0.5, 1, 2, 3]), 1.0)[0], 3)}")

print("\n2. Hand example: one noise-free observation f(0) = 2, length scale 1")
m, v, *_ = gp_posterior(np.array([0.0]), np.array([2.0]), np.array([0.0, 1.0, 2.0, 4.0]), 1.0, 1e-12)
for xq, mm, vv in zip([0, 1, 2, 4], m, v):
    print(f"   x = {xq}: posterior mean {mm:.4f}, variance {max(vv, 0):.4f}")

print("\n3. 15 noisy points from f(x) = sin(3x) on [0, 2], noise sd 0.2 (gap between 0.8 and 1.4)")
x = np.concatenate([rng.uniform(0, 0.8, 9), rng.uniform(1.4, 2.0, 6)])
y = np.sin(3 * x) + rng.normal(0, 0.2, len(x))
xq = np.array([-0.5, 0.0, 0.4, 1.1, 1.7, 2.5])
print("   length   log marginal   data fit -y^T K^-1 y / 2   Occam term -log det(K) / 2")
best = None
for ell in [0.05, 0.1, 0.2, 0.3, 0.5, 1.0, 2.0]:
    _, _, lm, fit, comp = gp_posterior(x, y, xq, ell, 0.04)
    print(f"   {ell:6.2f}   {lm:12.3f}   {fit:24.3f}   {comp:27.3f}")
    if best is None or lm > best[0]:
        best = (lm, ell)
ells = np.linspace(0.05, 2.0, 196)
ell_star = ells[np.argmax([gp_posterior(x, y, xq, e, 0.04)[2] for e in ells])]
print(f"   best length scale on a fine grid: {ell_star:.2f}")
m, v, *_ = gp_posterior(x, y, xq, ell_star, 0.04)
print("      x    mean    sd of f   true sin(3x)")
for a, mm, vv in zip(xq, m, v):
    print(f"   {a:5.2f}  {mm:6.3f}   {np.sqrt(max(vv, 0)):7.3f}   {np.sin(3 * a):7.3f}")

K = rbf(x, x, ell_star) + 0.04 * np.eye(len(x))
krr = rbf(x, xq, ell_star).T @ np.linalg.solve(K, y)
print(f"   kernel ridge regression with lambda = noise variance gives the same mean: "
      f"max difference {np.abs(krr - m).max():.1e}")
