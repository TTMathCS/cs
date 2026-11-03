"""Chapter 23: scaling laws. Measure power laws on a small model family
ourselves, then use the parametric law fitted by Hoffmann et al. (2022)
to find compute-optimal model and data sizes."""
import os
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")   # small matrices: one thread is fastest

import numpy as np

rng = np.random.default_rng(2020)
d = 4
def target(X):
    return np.sin(X @ np.array([1.0, 0.7, -0.5, 0.3])) + 0.5 * np.cos(2 * X[:, 0] - X[:, 2])

W_all = rng.normal(size=(d, 4000)); b_all = rng.uniform(0, 2 * np.pi, 4000)
def features(X, p):
    return np.cos(X @ W_all[:, :p] + b_all[:p]) * np.sqrt(2.0 / p)

def test_mse(n, p, lam=1e-4, seed=0):
    r = np.random.default_rng(seed)
    X, Xt = r.normal(size=(n, d)), r.normal(size=(2000, d))
    y = target(X) + 0.1 * r.normal(size=n)
    F, Ft = features(X, p), features(Xt, p)
    a = np.linalg.solve(F.T @ F + lam * n * np.eye(p), F.T @ y)
    return np.mean((Ft @ a - target(Xt)) ** 2)

def fit_power_law(x, L):
    """Fit L = E + A x^-alpha: grid over E, straight line in log-log for the rest."""
    best = None
    for E in np.linspace(0, 0.99 * L.min(), 200):
        k, c = np.polyfit(np.log(x), np.log(L - E), 1)
        res = np.sum((np.log(L - E) - (k * np.log(x) + c)) ** 2)
        if best is None or res < best[0]:
            best = (res, E, np.exp(c), -k)
    return best[1:]

print("1. our own scaling curves: ridge regression on p random Fourier features")
ns = np.array([100, 200, 400, 800, 1600, 3200])
Ln = np.array([np.mean([test_mse(n, 800, seed=s) for s in range(3)]) for n in ns])
E, A, alpha = fit_power_law(ns, Ln)
print("   data scaling (p = 800):        n = " + "  ".join(f"{n:6d}" for n in ns))
print("                              test MSE = " + "  ".join(f"{v:6.4f}" for v in Ln))
print(f"   fit: L(n) = {E:.4f} + {A:.2f} n^-{alpha:.2f}")
ps = np.array([25, 50, 100, 200, 400, 800])
Lp = np.array([np.mean([test_mse(4000, p, seed=s) for s in range(3)]) for p in ps])
E, A, alpha = fit_power_law(ps, Lp)
print("   model scaling (n = 4000):      p = " + "  ".join(f"{p:6d}" for p in ps))
print("                              test MSE = " + "  ".join(f"{v:6.4f}" for v in Lp))
print(f"   fit: L(p) = {E:.4f} + {A:.2f} p^-{alpha:.2f}")

print("\n2. compute-optimal sizes from the Chinchilla fit L(N, D) = E + A/N^a + B/D^b")
E, A, B, a, b = 1.69, 406.4, 410.7, 0.34, 0.28     # Hoffmann et al. 2022, equation 10
G = (a * A / (b * B)) ** (1 / (a + b))
print(f"   with C = 6 N D: N_opt = G (C/6)^{b / (a + b):.3f}, D_opt = (C/6)^{a / (a + b):.3f} / G,  G = {G:.3f}")
print("      compute C (FLOP)    N_opt (params)   D_opt (tokens)   tokens/param   predicted loss")
for C in [1e21, 1e22, 1e23, 5.76e23, 1e24, 1e25]:
    N = G * (C / 6) ** (b / (a + b)); D = C / (6 * N)
    L = E + A / N ** a + B / D ** b
    print(f"      {C:12.3g}      {N:14.3g}   {D:14.3g}   {D / N:12.1f}   {L:14.3f}")
C = 5.76e23
for N in [70e9, 280e9]:
    D = C / (6 * N)
    print(f"   at C = 5.76e23 the law gives N = {N:.3g}, D = {D:.3g}: loss {E + A / N ** a + B / D ** b:.3f}")
