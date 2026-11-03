"""Chapter 21: what classical theory does not explain, on small models.
Random features that fit random labels, double descent, the implicit bias
of gradient descent, and lazy training of wide networks."""
import os
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")   # small matrices: one thread is fastest

import numpy as np

rng = np.random.default_rng(2017)

def relu_features(X, W):
    return np.maximum(X @ W, 0.0) / np.sqrt(W.shape[1])

# ------------------------------------------------- 1. fitting random labels
d, n, n_test, p = 10, 200, 2000, 2000
w_true = rng.normal(size=d)
X, Xt = rng.normal(size=(n, d)), rng.normal(size=(n_test, d))
y, yt = np.sign(X @ w_true), np.sign(Xt @ w_true)
W = rng.normal(size=(d, p))
F, Ft = relu_features(X, W), relu_features(Xt, W)
print(f"1. {p} random ReLU features, {n} training points; minimum-norm interpolation")
print("   labels         train acc   test acc   ||a||")
for name, labels in [("true", y), ("random", rng.choice([-1.0, 1.0], size=n))]:
    a = np.linalg.pinv(F) @ labels
    print(f"   {name:12s}   {np.mean(np.sign(F @ a) == labels):9.3f}   "
          f"{np.mean(np.sign(Ft @ a) == yt):8.3f}   {np.linalg.norm(a):6.1f}")

# ------------------------------------------------------ 2. double descent
# Random Fourier features cos(w.x + b), the kind Belkin et al. (2019) used.
d, n, n_test, noise = 5, 40, 500, 0.1
def target(X):
    return np.sin(2 * X[:, 0]) + 0.5 * np.cos(X[:, 1])
print(f"\n2. double descent: {n} training points, p random Fourier features, minimum-norm least squares")
print("     p    p/n    train MSE   test MSE (median over 20 runs)")
for p in [5, 10, 20, 30, 36, 40, 44, 50, 80, 200, 1000, 3000]:
    tr, te = [], []
    for seed in range(20):
        r = np.random.default_rng(seed)
        X, Xt = r.normal(size=(n, d)), r.normal(size=(n_test, d))
        y = target(X) + noise * r.normal(size=n)
        yt = target(Xt)
        W, b = r.normal(size=(d, p)), r.uniform(0, 2 * np.pi, size=p)
        F, Ft = np.cos(X @ W + b) / np.sqrt(p), np.cos(Xt @ W + b) / np.sqrt(p)
        a = np.linalg.pinv(F) @ y
        tr.append(np.mean((F @ a - y) ** 2)); te.append(np.mean((Ft @ a - yt) ** 2))
    print(f"  {p:5d}  {p / n:5.2f}   {np.median(tr):9.4f}   {np.median(te):9.4f}")

# ------------------------------------------ 3. implicit bias of gradient descent
n, p = 20, 100
A = rng.normal(size=(n, p))
b = rng.normal(size=n)
w_min = np.linalg.pinv(A) @ b
lr = 1.0 / np.linalg.norm(A, 2) ** 2
print(f"\n3. gradient descent on least squares with {n} equations, {p} unknowns (infinitely many exact fits)")
for name, w0 in [("start at 0", np.zeros(p)), ("random start", rng.normal(size=p))]:
    w = w0.copy()
    for _ in range(5000):
        w -= lr * A.T @ (A @ w - b)
    # theory: GD never leaves w0 + rowspace(A), so it ends at w_min + (I - P) w0
    P = np.linalg.pinv(A) @ A
    pred = w_min + (np.eye(p) - P) @ w0
    print(f"   {name:13s} residual {np.linalg.norm(A @ w - b):.1e}  ||w|| = {np.linalg.norm(w):.4f}  "
          f"||w - w_min|| = {np.linalg.norm(w - w_min):.4f}  ||w - predicted|| = {np.linalg.norm(w - pred):.1e}")
print(f"   minimum-norm solution has ||w_min|| = {np.linalg.norm(w_min):.4f}")

# ------------------------------------------------ 4. lazy training of wide nets
# f(x) = (1/sqrt(m)) sum_j a_j relu(w_j . x), trained by gradient descent on 20 points.
n, d = 20, 3
X = rng.normal(size=(n, d)); X /= np.linalg.norm(X, axis=1, keepdims=True)
y = np.sin(3 * X[:, 0]) + X[:, 1]
print("\n4. two-layer ReLU net in NTK scaling, 2000 steps of gradient descent")
print("     width   final train MSE   ||W - W0|| / ||W0||   kernel change ||K - K0|| / ||K0||")
for m in [10, 100, 1000, 10000]:
    r = np.random.default_rng(m)
    W0, a0 = r.normal(size=(d, m)), r.choice([-1.0, 1.0], size=m)
    W, a = W0.copy(), a0.copy()
    def ntk(W, a):
        H = X @ W
        act, der = np.maximum(H, 0), (H > 0).astype(float)
        # gradient features: d f / d a_j and d f / d w_j, stacked
        Ja = act / np.sqrt(m)
        Jw = (der * a)[:, None, :] * X[:, :, None] / np.sqrt(m)     # (n, d, m)
        J = np.concatenate([Ja, Jw.reshape(n, -1)], axis=1)
        return J @ J.T
    K0 = ntk(W, a)
    lr = 0.5
    for _ in range(2000):
        H = X @ W
        act = np.maximum(H, 0)
        f = act @ a / np.sqrt(m)
        g = (f - y) / n                                   # d(MSE/2)/df
        grad_a = act.T @ g / np.sqrt(m)
        grad_W = X.T @ ((g[:, None] * (H > 0)) * a) / np.sqrt(m)
        a -= lr * grad_a; W -= lr * grad_W
    f = np.maximum(X @ W, 0) @ a / np.sqrt(m)
    K = ntk(W, a)
    print(f"  {m:7d}   {np.mean((f - y) ** 2):15.5f}   {np.linalg.norm(W - W0) / np.linalg.norm(W0):19.4f}"
          f"   {np.linalg.norm(K - K0) / np.linalg.norm(K0):19.4f}")
