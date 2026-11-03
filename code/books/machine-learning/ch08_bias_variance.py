"""Chapter 8: underfitting and overfitting with polynomials, the bias-variance
decomposition measured by simulation, ridge validation curves, early
stopping and noise augmentation, from scratch with NumPy."""
import numpy as np

def truth(x):
    return np.sin(np.pi * x)

SIGMA = 0.3                                     # noise standard deviation

def poly(x, degree):
    return np.vander(x, degree + 1, increasing=True)    # columns 1, x, x^2, ...

def fit(x, y, degree, lam=0.0):
    X = poly(x, degree)
    A = X.T @ X + lam * np.diag(np.r_[0, np.ones(degree)])   # do not penalise the intercept
    return np.linalg.lstsq(A, X.T @ y, rcond=None)[0]

rng = np.random.default_rng(0)
n = 20
x_tr = np.sort(rng.uniform(-1, 1, n))
y_tr = truth(x_tr) + rng.normal(0, SIGMA, n)
x_te = rng.uniform(-1, 1, 2000)
y_te = truth(x_te) + rng.normal(0, SIGMA, 2000)

# ------------------------------------------- 1. under- and overfitting
print(f"1. polynomial fits to {n} noisy points of sin(pi x), noise sd {SIGMA}")
print("   degree  train MSE  test MSE   largest |coefficient|")
for d in (0, 1, 3, 5, 9, 12, 14):
    w = fit(x_tr, y_tr, d)
    tr = np.mean((poly(x_tr, d) @ w - y_tr) ** 2)
    te = np.mean((poly(x_te, d) @ w - y_te) ** 2)
    print(f"   {d:4d}    {tr:9.4f}  {te:10.4f}   {np.abs(w).max():12.1f}")
print(f"   noise floor (best possible test MSE) = sigma^2 = {SIGMA ** 2:.4f}")

# ------------------------------- 2. the bias-variance decomposition
# Draw 2000 training sets of size n, fit each, and look at predictions on
# a fixed grid of test inputs.
grid = np.linspace(-0.95, 0.95, 200)
def decompose(degree, lam=0.0, sets=2000, seed=1):
    r = np.random.default_rng(seed)
    preds = np.empty((sets, len(grid)))
    sq_err = 0.0
    for s in range(sets):
        x = r.uniform(-1, 1, n)
        y = truth(x) + r.normal(0, SIGMA, n)
        preds[s] = poly(grid, degree) @ fit(x, y, degree, lam)
        y_new = truth(grid) + r.normal(0, SIGMA, len(grid))
        sq_err += np.mean((preds[s] - y_new) ** 2)
    mean_pred = preds.mean(0)
    bias2 = np.mean((mean_pred - truth(grid)) ** 2)
    var = np.mean(preds.var(0))
    return bias2, var, sq_err / sets

print(f"\n2. bias-variance by simulation (2000 training sets of {n} points)")
print("   model           bias^2     variance   bias^2+var+sigma^2   measured test MSE")
for d, lam in ((1, 0), (3, 0), (5, 0), (7, 0), (9, 0), (9, 1e-3), (9, 1e-1)):
    b2, v, mse = decompose(d, lam)
    name = f"degree {d}" + (f", ridge {lam:g}" if lam else "")
    print(f"   {name:16s} {b2:8.4f}  {v:10.4f}   {b2 + v + SIGMA ** 2:12.4f}       {mse:10.4f}")

# ---------------------------------------- 3. a validation curve for ridge
x_va = rng.uniform(-1, 1, 15)
y_va = truth(x_va) + rng.normal(0, SIGMA, 15)
print("\n3. degree 12 with ridge penalty lambda: validation curve")
print("   lambda     train MSE  validation MSE  test MSE")
best = None
for lam in (0, 1e-6, 1e-4, 1e-3, 1e-2, 1e-1, 1, 10):
    w = fit(x_tr, y_tr, 12, lam)
    tr = np.mean((poly(x_tr, 12) @ w - y_tr) ** 2)
    va = np.mean((poly(x_va, 12) @ w - y_va) ** 2)
    te = np.mean((poly(x_te, 12) @ w - y_te) ** 2)
    if best is None or va < best[1]:
        best = (lam, va)
    print(f"   {lam:<8g}   {tr:9.4f}  {va:12.4f}   {te:9.4f}")
print(f"   chosen by validation: lambda = {best[0]:g}")

# ------------------------------------------------- 4. early stopping
# Gradient descent on degree-12 features (scaled to unit variance) from w = 0.
X = poly(x_tr, 12)[:, 1:]
mu, sd = X.mean(0), X.std(0)
Z = np.c_[np.ones(n), (X - mu) / sd]
Zva = np.c_[np.ones(15), (poly(x_va, 12)[:, 1:] - mu) / sd]
Zte = np.c_[np.ones(2000), (poly(x_te, 12)[:, 1:] - mu) / sd]
L = np.linalg.eigvalsh(2 * Z.T @ Z / n).max()
w = np.zeros(13)
print("\n4. early stopping: gradient descent on degree-12 features, step 1/L")
print("   step      train MSE  validation MSE  test MSE   |w|")
best = (None, np.inf)
for t in range(1, 100001):
    w -= (2 * Z.T @ (Z @ w - y_tr) / n) / L
    va = np.mean((Zva @ w - y_va) ** 2)
    if va < best[1]:
        best = (t, va, np.mean((Zte @ w - y_te) ** 2))
    if t in (10, 100, 1000, 3000, 10000, 100000):
        print(f"   {t:6d}    {np.mean((Z @ w - y_tr) ** 2):9.4f}  {va:12.4f}   "
              f"{np.mean((Zte @ w - y_te) ** 2):9.4f}  {np.linalg.norm(w):7.2f}")
print(f"   best validation at step {best[0]}: validation {best[1]:.4f}, test {best[2]:.4f}")

# ------------------------------------------ 5. augmentation with input noise
# Copy each training point 200 times with its input jittered (sd 0.1), fit
# degree 12 by plain least squares: the noise acts like a penalty.
r = np.random.default_rng(5)
xa = np.repeat(x_tr, 200) + r.normal(0, 0.1, n * 200)
ya = np.repeat(y_tr, 200)
w_aug = fit(xa, ya, 12)
print("\n5. degree 12 with input-noise augmentation (200 jittered copies, sd 0.1)")
print(f"   test MSE without augmentation {np.mean((poly(x_te, 12) @ fit(x_tr, y_tr, 12) - y_te) ** 2):.4f}, "
      f"with {np.mean((poly(x_te, 12) @ w_aug - y_te) ** 2):.4f}")
