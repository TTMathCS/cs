"""Chapter 9.5-9.6: the kernel trick checked by hand, Gram matrices that are
(and are not) positive semidefinite, and kernel ridge regression from scratch."""
import numpy as np

print("1. The kernel trick: k(x, z) = (x.z + 1)^2 equals phi(x).phi(z) for an explicit phi")
x, z = np.array([1.0, 2.0]), np.array([3.0, -1.0])


def phi(v):
    a, b = v
    r2 = np.sqrt(2)
    return np.array([1, r2 * a, r2 * b, a * a, b * b, r2 * a * b])


print(f"   (x.z + 1)^2      = {(x @ z + 1) ** 2:.4f}")
print(f"   phi(x).phi(z)    = {phi(x) @ phi(z):.4f}")
print(f"   phi(x) = {np.round(phi(x), 4)}")
for p, d in [(2, 2), (3, 10), (5, 100)]:
    from math import comb
    print(f"   degree {p} in d = {d}: explicit features = C(d+p, p) = {comb(d + p, p)}, kernel cost ~ d = {d}")


def rbf(A, B, gamma):
    sq = (A ** 2).sum(1)[:, None] + (B ** 2).sum(1)[None, :] - 2 * A @ B.T
    return np.exp(-gamma * np.maximum(sq, 0))


print("\n2. Is the Gram matrix positive semidefinite? smallest eigenvalue on 40 random points")
rng = np.random.default_rng(4)
P = rng.normal(0, 1, (40, 3))
cands = {
    "linear x.z": P @ P.T,
    "polynomial (x.z+1)^3": (P @ P.T + 1) ** 3,
    "RBF exp(-|x-z|^2)": rbf(P, P, 1.0),
    "Laplacian exp(-|x-z|)": np.exp(-np.sqrt(np.maximum(
        (P ** 2).sum(1)[:, None] + (P ** 2).sum(1)[None, :] - 2 * P @ P.T, 0))),
    "tanh(x.z - 1) (not a kernel)": np.tanh(P @ P.T - 1),
    "-|x-z|^2 (not a kernel)": -np.maximum((P ** 2).sum(1)[:, None] + (P ** 2).sum(1)[None, :] - 2 * P @ P.T, 0),
}
for name, K in cands.items():
    lam = np.linalg.eigvalsh(K).min()
    print(f"   {name:30s} {lam: .3e}")


def krr_fit(X, y, kernel, lam):
    K = kernel(X, X)
    return np.linalg.solve(K + lam * np.eye(len(X)), y)


def krr_predict(alpha, X, Xq, kernel):
    return kernel(Xq, X) @ alpha


print("\n3. Kernel ridge regression on y = sin(2x) + noise, 80 training points")
x = np.sort(rng.uniform(0, 3, 80))[:, None]
y = np.sin(2 * x[:, 0]) + rng.normal(0, 0.3, 80)
xv = rng.uniform(0, 3, 200)[:, None]
yv = np.sin(2 * xv[:, 0]) + rng.normal(0, 0.3, 200)
xt = np.linspace(0, 3, 301)[:, None]
print("   gamma   lambda   valid MSE   error vs true curve")
best = None
for g in [0.1, 1, 10, 100]:
    for lam in [1e-3, 1e-1, 1, 10]:
        kern = lambda A, B, g=g: rbf(A, B, g)
        a = krr_fit(x, y, kern, lam)
        mse = ((krr_predict(a, x, xv, kern) - yv) ** 2).mean()
        te = ((krr_predict(a, x, xt, kern) - np.sin(2 * xt[:, 0])) ** 2).mean()
        print(f"   {g:5g}   {lam:6g}   {mse:9.4f}   {te:.4f}")
        if best is None or mse < best[0]:
            best = (mse, g, lam)
print(f"   best on validation: gamma = {best[1]}, lambda = {best[2]}")
Xl = np.column_stack([np.ones(80), x[:, 0]])
w = np.linalg.solve(Xl.T @ Xl + 0.1 * np.eye(2), Xl.T @ y)
lin = ((np.column_stack([np.ones(200), xv[:, 0]]) @ w - yv) ** 2).mean()
print(f"   plain linear ridge on the same data: valid MSE {lin:.4f}")

print("\n4. Kernel ridge with a linear kernel = ordinary ridge (primal and dual agree)")
X = rng.normal(0, 1, (30, 4))
t = X @ np.array([1.0, -2.0, 0.5, 0.0]) + rng.normal(0, 0.1, 30)
lam = 0.7
w_primal = np.linalg.solve(X.T @ X + lam * np.eye(4), X.T @ t)
alpha = np.linalg.solve(X @ X.T + lam * np.eye(30), t)
w_dual = X.T @ alpha
print(f"   primal w = {np.round(w_primal, 6)}")
print(f"   X^T alpha = {np.round(w_dual, 6)}")
print(f"   largest difference {np.abs(w_primal - w_dual).max():.2e}")

print("\n5. Hand example: three points, RBF kernel gamma = 1, lambda = 0.1")
xs = np.array([[0.0], [1.0], [2.0]])
ys = np.array([0.0, 1.0, 0.0])
K = rbf(xs, xs, 1.0)
print("   K =\n", np.round(K, 4))
a = np.linalg.solve(K + 0.1 * np.eye(3), ys)
print(f"   alpha = {np.round(a, 4)}")
print(f"   prediction at 1.0 = {krr_predict(a, xs, np.array([[1.0]]), lambda A, B: rbf(A, B, 1.0))[0]:.4f}")
print(f"   prediction at 0.5 = {krr_predict(a, xs, np.array([[0.5]]), lambda A, B: rbf(A, B, 1.0))[0]:.4f}")
