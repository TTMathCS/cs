"""Chapter 5: gradient descent, its O(1/k) rate, stochastic and mini-batch
gradient descent, and momentum, all from scratch with NumPy."""
import numpy as np

# ---------------------------------------------------------------- 1. convexity
def is_convex_on_samples(f, dim, trials=2000, seed=0):
    """Test f(t x + (1-t) y) <= t f(x) + (1-t) f(y) on random points.
    A failure proves f is not convex; passing is only evidence."""
    rng = np.random.default_rng(seed)
    for _ in range(trials):
        x, y = rng.normal(size=dim) * 3, rng.normal(size=dim) * 3
        t = rng.uniform()
        if f(t * x + (1 - t) * y) > t * f(x) + (1 - t) * f(y) + 1e-12:
            return False
    return True

print("1. convexity test on random chords")
tests = {
    "x^2 + y^2": lambda v: v @ v,
    "|x| + |y|": lambda v: np.abs(v).sum(),
    "log(1+e^x)": lambda v: np.log1p(np.exp(v[0])),
    "sin(x)": lambda v: np.sin(v[0]),
    "x^2 - y^2": lambda v: v[0] ** 2 - v[1] ** 2,
}
for name, f in tests.items():
    print(f"   {name:12s} convex? {is_convex_on_samples(f, 2)}")

# ------------------------------------------------- 2. GD and the O(1/k) bound
# Logistic-regression loss on overlapping (non-separable) data: convex and
# L-smooth with L = lambda_max(X^T X) / (4 n), and it has a minimiser.
rng = np.random.default_rng(1)
n, d = 200, 3
X = np.c_[np.ones(n), rng.normal(size=(n, d - 1))]
y = (X @ np.array([0.5, 2.0, -1.0]) + rng.normal(size=n) * 1.5 > 0).astype(float)

def loss(w):
    z = X @ w
    return np.mean(np.logaddexp(0, z) - y * z)

def grad(w):
    p = 1 / (1 + np.exp(-(X @ w)))
    return X.T @ (p - y) / n

L = np.linalg.eigvalsh(X.T @ X / (4 * n)).max()
w_star = np.zeros(d)                      # find w* to machine precision with Newton
for _ in range(30):
    p = 1 / (1 + np.exp(-(X @ w_star)))
    H = X.T @ (X * (p * (1 - p))[:, None]) / n
    w_star -= np.linalg.solve(H, grad(w_star))
f_star = loss(w_star)

w = np.zeros(d)
R2 = np.sum((w - w_star) ** 2)
print(f"\n2. gradient descent with step 1/L on logistic loss, L = {L:.4f}")
print("     k    f(w_k)-f*    bound L*R^2/(2k)   ratio")
for k in range(1, 1001):
    w = w - grad(w) / L
    if k in (1, 2, 5, 10, 50, 100, 1000):
        gap = loss(w) - f_star
        bound = L * R2 / (2 * k)
        print(f"  {k:4d}   {gap:.3e}     {bound:.3e}        {gap / bound:.4f}")

# For each k, the 1-D quadratic f(x) = lam x^2 / 2 with lam = L / (2k+1) makes
# gradient descent lose a fixed fraction of the bound: no single faster rate
# can hold for every L-smooth convex function.
print("\n   worst 1-D quadratic for each k (L = 1, R = 1)")
print("     k    f(x_k)-f*    bound      ratio")
for k in (1, 10, 100, 1000):
    lam = 1.0 / (2 * k + 1)
    x = 1.0
    for _ in range(k):
        x -= lam * x                       # step 1/L = 1
    gap, bound = lam * x * x / 2, 1 / (2 * k)
    print(f"  {k:4d}   {gap:.3e}   {bound:.3e}   {gap / bound:.4f}")

# ------------------------------------------- 3. full, stochastic, mini-batch
rng = np.random.default_rng(2)
n, d = 1000, 5
A = rng.normal(size=(n, d))
w_true = rng.normal(size=d)
b = A @ w_true + rng.normal(size=n) * 0.5
w_ls = np.linalg.lstsq(A, b, rcond=None)[0]
mse = lambda w: np.mean((A @ w - b) ** 2)
best = mse(w_ls)

def run(batch, lr, epochs, decay=False, seed=3):
    r = np.random.default_rng(seed)
    w = np.zeros(d)
    out, t = [], 0
    for _ in range(epochs):
        order = r.permutation(n)
        for s in range(0, n, batch):
            idx = order[s:s + batch]
            g = 2 * A[idx].T @ (A[idx] @ w - b[idx]) / len(idx)
            t += 1
            w -= (lr / (1 + 0.01 * t) if decay else lr) * g
        out.append(mse(w) - best)
    return out, t

print(f"\n3. excess training MSE after each epoch (best MSE = {best:.4f})")
runs = {
    "full batch, lr 0.1": run(n, 0.1, 5),
    "batch 1, lr 0.01": run(1, 0.01, 5),
    "batch 1, lr 0.01 decaying": run(1, 0.01, 5, decay=True),
    "batch 32, lr 0.05": run(32, 0.05, 5),
}
print("   method                      updates  ep1       ep2       ep3       ep5")
for name, (h, t) in runs.items():
    print(f"   {name:27s} {t:6d}  " + "  ".join(f"{h[e]:.2e}" for e in (0, 1, 2, 4)))

# -------------------------------------------- 4. momentum and Nesterov
# f(x) = 1/2 x^T Q x with eigenvalues mu = 1 and L = 100 (condition number 100).
Q = np.diag([1.0, 100.0])
fq = lambda x: 0.5 * x @ Q @ x
gq = lambda x: Q @ x
mu, Lq = 1.0, 100.0
kappa = Lq / mu

def iterations(method, tol=1e-8, max_it=20000):
    x = np.array([1.0, 1.0]); v = np.zeros(2); x_prev = x.copy()
    for k in range(1, max_it + 1):
        if method == "gd":
            x = x - gq(x) / Lq
        elif method == "heavy ball":
            a = 4 / (np.sqrt(Lq) + np.sqrt(mu)) ** 2
            beta = ((np.sqrt(kappa) - 1) / (np.sqrt(kappa) + 1)) ** 2
            x, x_prev = x - a * gq(x) + beta * (x - x_prev), x
        elif method == "nesterov":
            beta = (np.sqrt(kappa) - 1) / (np.sqrt(kappa) + 1)
            yk = x + beta * (x - x_prev)
            x, x_prev = yk - gq(yk) / Lq, x
        if fq(x) < tol:
            return k
    return max_it

print(f"\n4. steps to reach f < 1e-8 on a quadratic with condition number {kappa:.0f}")
for m in ("gd", "heavy ball", "nesterov"):
    print(f"   {m:11s} {iterations(m):5d}")
print(f"   predicted rates per step: gd {1 - 1 / kappa:.4f}, "
      f"heavy ball {(np.sqrt(kappa) - 1) / (np.sqrt(kappa) + 1):.4f}, "
      f"nesterov {1 - 1 / np.sqrt(kappa):.4f}")
