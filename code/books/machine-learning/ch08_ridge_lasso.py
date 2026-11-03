"""Chapter 8: ridge regression (closed form, SVD shrinkage, Bayesian view),
the lasso by coordinate descent, cross-validated lambda, effective degrees of
freedom and the elastic net, all from scratch with NumPy."""
import numpy as np

rng = np.random.default_rng(0)
n, p = 50, 20
X = rng.normal(size=(n, p))
X = (X - X.mean(0)) / X.std(0)                  # standardised features
w_true = np.zeros(p); w_true[:3] = [3.0, -2.0, 1.5]
SIGMA = 1.0
y = X @ w_true + rng.normal(0, SIGMA, n)
y = y - y.mean()                                # centred: no intercept needed

def ridge(X, y, lam):
    return np.linalg.solve(X.T @ X + lam * np.eye(X.shape[1]), X.T @ y)

def soft(z, t):
    return np.sign(z) * np.maximum(np.abs(z) - t, 0.0)

def lasso(X, y, lam, alpha=1.0, w=None, sweeps=1000, tol=1e-10):
    """Coordinate descent for (1/2n)|y - Xw|^2 + lam*(alpha*|w|_1 + (1-alpha)/2*|w|^2).
    alpha = 1 is the lasso; 0 < alpha < 1 is the elastic net."""
    n, p = X.shape
    w = np.zeros(p) if w is None else w.copy()
    col = (X ** 2).sum(0) / n
    r = y - X @ w
    for _ in range(sweeps):
        biggest = 0.0
        for j in range(p):
            old = w[j]
            rho = X[:, j] @ r / n + col[j] * old          # correlation with partial residual
            w[j] = soft(rho, lam * alpha) / (col[j] + lam * (1 - alpha))
            if w[j] != old:
                r -= X[:, j] * (w[j] - old)
                biggest = max(biggest, abs(w[j] - old))
        if biggest < tol:
            break
    return w

# ------------------------------------------------ 1. ridge and shrinkage
U, d, Vt = np.linalg.svd(X, full_matrices=False)
print("1. ridge: closed form against the SVD formula V diag(d/(d^2+lam)) U^T y")
for lam in (1.0, 10.0, 100.0):
    w1 = ridge(X, y, lam)
    w2 = Vt.T @ ((d / (d ** 2 + lam)) * (U.T @ y))
    f = d ** 2 / (d ** 2 + lam)
    print(f"   lambda {lam:5.0f}: max difference {np.abs(w1 - w2).max():.1e}; "
          f"shrink factors from {f.min():.3f} to {f.max():.3f}; |w| = {np.linalg.norm(w1):.3f}")
print(f"   least squares |w| = {np.linalg.norm(ridge(X, y, 0)):.3f}")

# ---------------------------------------------- 2. the Bayesian view
tau = 0.5                                        # prior w ~ N(0, tau^2 I)
post_prec = X.T @ X / SIGMA ** 2 + np.eye(p) / tau ** 2
post_mean = np.linalg.solve(post_prec, X.T @ y / SIGMA ** 2)
w_r = ridge(X, y, SIGMA ** 2 / tau ** 2)
sd = np.sqrt(np.diag(np.linalg.inv(post_prec)))
print(f"\n2. posterior mean with prior sd {tau} equals ridge with lambda = sigma^2/tau^2 = {SIGMA**2/tau**2:g}:"
      f" max difference {np.abs(post_mean - w_r).max():.1e}")
print("   first five weights: posterior mean +- 2 sd")
for j in range(5):
    print(f"      w{j + 1}: {post_mean[j]:+.3f} +- {2 * sd[j]:.3f}   (true {w_true[j]:+.1f})")

# ------------------------------------------ 3. orthonormal design
Q = np.linalg.qr(rng.normal(size=(n, 4)))[0]     # columns orthonormal: Q^T Q = I
yq = Q @ np.array([2.0, -0.5, 0.2, 1.0]) + rng.normal(0, 0.1, n)
ols = Q.T @ yq
lam = 0.3
print("\n3. orthonormal columns: lasso = soft-threshold(OLS), ridge = OLS / (1 + lam)")
print(f"   OLS          {np.round(ols, 4)}")
print(f"   ridge        {np.round(ridge(Q, yq, lam), 4)}   OLS/(1+lam) {np.round(ols / (1 + lam), 4)}")
# with the (1/2n) scaling, the lasso penalty matching 'lam' on |w|_1 is lam/n
print(f"   lasso        {np.round(lasso(Q, yq, lam / n), 4)}   soft(OLS, lam) {np.round(soft(ols, lam), 4)}")

# ------------------------------------------------ 4. the lasso path
print("\n4. lasso path on the 20-feature problem (true weights 3, -2, 1.5, then 17 zeros)")
print("   lambda   nonzero  w1      w2      w3      largest wrong |w_j|")
w = np.zeros(p)
for lam in (3.0, 2.0, 1.0, 0.5, 0.2, 0.1, 0.05, 0.01):
    w = lasso(X, y, lam, w=w)                    # warm start from the previous lambda
    print(f"   {lam:<6g}   {np.sum(w != 0):4d}    {w[0]:+.3f}  {w[1]:+.3f}  {w[2]:+.3f}   "
          f"{np.abs(w[3:]).max():.3f}")
print(f"   ridge (lambda 10) has {np.sum(np.abs(ridge(X, y, 10)) > 1e-12)} nonzero weights")

# ---------------------------------------- 5. choosing lambda by 5-fold CV
X_te = rng.normal(size=(5000, p)); X_te = (X_te - X.mean(0))
y_te = X_te @ w_true + rng.normal(0, SIGMA, 5000)
folds = np.array_split(rng.permutation(n), 5)
def cv_error(method, lam):
    err = 0.0
    for f in folds:
        tr = np.setdiff1d(np.arange(n), f)
        w = method(X[tr], y[tr], lam)
        err += np.sum((X[f] @ w - y[f]) ** 2)
    return err / n
lams_l = [1.0, 0.5, 0.3, 0.2, 0.1, 0.05, 0.02, 0.01]
lams_r = [100, 30, 10, 3, 1, 0.3, 0.1]
bl = min(lams_l, key=lambda l: cv_error(lasso, l))
br = min(lams_r, key=lambda l: cv_error(ridge, l))
print("\n5. lambda chosen by 5-fold CV, then refit on all 50 points; test MSE on 5000 points")
for name, w in (("least squares", ridge(X, y, 0)), (f"ridge  (lambda {br:g})", ridge(X, y, br)),
                (f"lasso  (lambda {bl:g})", lasso(X, y, bl))):
    print(f"   {name:22s} test MSE {np.mean((X_te @ w - y_te) ** 2):.4f}   nonzero {np.sum(np.abs(w) > 1e-12)}")
print(f"   noise floor sigma^2 = {SIGMA ** 2:.4f}")

# The same comparison averaged over 10 fresh data sets of only 30 points,
# where least squares (20 weights from 30 points) has much more variance.
r = np.random.default_rng(11)
avg = {"least squares": [], "ridge, CV lambda": [], "lasso, CV lambda": []}
for rep in range(10):
    Xr = r.normal(size=(30, p)); yr = Xr @ w_true + r.normal(0, SIGMA, 30)
    Xt = r.normal(size=(2000, p)); yt = Xt @ w_true + r.normal(0, SIGMA, 2000)
    fo = np.array_split(r.permutation(30), 5)
    def cv30(method, lam):
        return sum(np.sum((Xr[f] @ method(Xr[np.setdiff1d(np.arange(30), f)],
                                          yr[np.setdiff1d(np.arange(30), f)], lam) - yr[f]) ** 2)
                   for f in fo)
    bl30 = min([0.5, 0.2, 0.1, 0.05, 0.02], key=lambda l: cv30(lasso, l))
    br30 = min([30, 10, 3, 1, 0.3], key=lambda l: cv30(ridge, l))
    for name, w in (("least squares", ridge(Xr, yr, 0)), ("ridge, CV lambda", ridge(Xr, yr, br30)),
                    ("lasso, CV lambda", lasso(Xr, yr, bl30))):
        avg[name].append(np.mean((Xt @ w - yt) ** 2))
print("   averaged over 10 data sets of 30 points:")
for name, v in avg.items():
    print(f"   {name:22s} mean test MSE {np.mean(v):.4f}")

# --------------------------- 6. effective degrees of freedom, by simulation
# df = sum_i Cov(yhat_i, y_i) / sigma^2, estimated over 2000 noise draws.
mean_y = X @ w_true
draws = 2000
r = np.random.default_rng(3)
Ys = mean_y + r.normal(0, SIGMA, (draws, n))
print("\n6. effective degrees of freedom")
for lam in (1.0, 10.0, 100.0):
    H = X @ np.linalg.solve(X.T @ X + lam * np.eye(p), X.T)
    preds = Ys @ H.T
    cov = np.mean(np.sum((preds - preds.mean(0)) * (Ys - mean_y), 1)) / SIGMA ** 2
    print(f"   ridge lambda {lam:5g}: formula sum d^2/(d^2+lam) = {np.sum(d ** 2 / (d ** 2 + lam)):6.3f}, "
          f"simulated {cov:6.3f}")
for lam in (0.5, 0.1):
    preds = np.empty((400, n)); nz = []
    for k in range(400):
        wk = lasso(X, Ys[k], lam)
        preds[k] = X @ wk; nz.append(np.sum(wk != 0))
    cov = np.mean(np.sum((preds - preds.mean(0)) * (Ys[:400] - mean_y), 1)) / SIGMA ** 2
    print(f"   lasso lambda {lam:5g}: average number of nonzeros {np.mean(nz):6.3f}, simulated {cov:6.3f}")

# ------------------------------------- 7. correlated features: elastic net
z = rng.normal(size=n)
Xc = np.c_[z + 0.01 * rng.normal(size=n), z + 0.01 * rng.normal(size=n), rng.normal(size=(n, 3))]
Xc = (Xc - Xc.mean(0)) / Xc.std(0)
yc = 2 * z + rng.normal(0, 0.5, n); yc -= yc.mean()
print(f"\n7. two nearly identical features (correlation {np.corrcoef(Xc[:, 0], Xc[:, 1])[0, 1]:.4f}), "
      "true signal 2 z")
print(f"   lasso       (lambda 0.1)            {np.round(lasso(Xc, yc, 0.1), 3)}")
print(f"   elastic net (lambda 0.1, alpha 0.5) {np.round(lasso(Xc, yc, 0.1, alpha=0.5), 3)}")
print(f"   ridge       (lambda 5)              {np.round(ridge(Xc, yc, 5.0), 3)}")
