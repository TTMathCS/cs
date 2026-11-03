"""Chapter 10.3-10.6: the soft-margin SVM dual solved by SMO (Platt 1998) from scratch,
with a linear and an RBF kernel; KKT conditions checked; support vectors counted."""
import numpy as np


def linear(A, B):
    return A @ B.T


def rbf(gamma):
    def k(A, B):
        sq = (A ** 2).sum(1)[:, None] + (B ** 2).sum(1)[None, :] - 2 * A @ B.T
        return np.exp(-gamma * np.maximum(sq, 0))
    return k


def smo(X, y, C, kernel, tol=1e-3, max_passes=200):
    """Maximise sum(a) - 1/2 sum_ij a_i a_j y_i y_j K_ij  s.t. 0 <= a_i <= C, sum a_i y_i = 0.
    Each step picks a KKT violator i and a partner j, and solves the two-variable problem exactly."""
    n = len(y)
    K = kernel(X, X)
    a = np.zeros(n)
    E = -y.astype(float)                       # E_i = f(x_i) - y_i, with f = 0 at the start
    rng_smo = np.random.default_rng(0)
    state = {"b": 0.0, "steps": 0}

    def take_step(i, j):
        """Solve the two-variable subproblem in (a_i, a_j) exactly; False if no progress."""
        b = state["b"]
        if y[i] != y[j]:
            L, H = max(0.0, a[j] - a[i]), min(C, C + a[j] - a[i])
        else:
            L, H = max(0.0, a[i] + a[j] - C), min(C, a[i] + a[j])
        eta = K[i, i] + K[j, j] - 2 * K[i, j]
        if L >= H or eta <= 1e-12:
            return False
        aj = np.clip(a[j] + y[j] * (E[i] - E[j]) / eta, L, H)
        if abs(aj - a[j]) < 1e-10:
            return False
        ai = a[i] + y[i] * y[j] * (a[j] - aj)
        di, dj = ai - a[i], aj - a[j]
        b1 = b - E[i] - y[i] * di * K[i, i] - y[j] * dj * K[i, j]
        b2 = b - E[j] - y[i] * di * K[i, j] - y[j] * dj * K[j, j]
        b_new = b1 if 0 < ai < C else b2 if 0 < aj < C else (b1 + b2) / 2
        E[:] += y[i] * di * K[i] + y[j] * dj * K[j] + (b_new - b)
        a[i], a[j] = ai, aj
        state["b"] = b_new
        state["steps"] += 1
        return True

    for _ in range(max_passes):
        changed = 0
        for i in range(n):
            r = y[i] * E[i]                    # = y_i f(x_i) - 1
            if not ((r < -tol and a[i] < C) or (r > tol and a[i] > 0)):
                continue                       # i satisfies KKT within tol
            first = int(np.argmax(np.abs(E - E[i])))   # Platt's heuristic: largest |E_i - E_j|
            for j in [first] + list(rng_smo.permutation(n)):  # fall back to other partners
                if j == i:
                    continue
                if take_step(i, j):
                    break
            else:
                continue
            changed += 1
        if changed == 0:
            break
    free = (a > 1e-8) & (a < C - 1e-8)
    b = state["b"]
    if free.any():                             # b from the KKT equalities y_i f(x_i) = 1 of free points
        b = float(np.mean(y[free] - K[free] @ (a * y)))
    return a, b, state["steps"]


def decision(a, b, X, y, kernel, Xq):
    return kernel(Xq, X) @ (a * y) + b


def kkt_report(a, b, X, y, C, kernel):
    f = decision(a, b, X, y, kernel, X)
    m = y * f
    zero, free, bound = a < 1e-8, (a > 1e-8) & (a < C - 1e-8), a > C - 1e-8
    worst = max(np.max(1 - m[zero], initial=0), np.max(np.abs(m[free] - 1), initial=0),
                np.max(m[bound] - 1, initial=0))
    return zero.sum(), free.sum(), bound.sum(), worst


rng = np.random.default_rng(5)
n = 100
Xp = rng.normal([1, 1], 1.0, (n // 2, 2))
Xn = rng.normal([-1, -1], 1.0, (n // 2, 2))
X = np.vstack([Xp, Xn])
y = np.concatenate([np.ones(n // 2), -np.ones(n // 2)])

print("Linear soft-margin SVM on two overlapping Gaussian clouds (100 points)")
print("      C   steps  |w|    width 2/|w|  a=0  0<a<C  a=C  worst KKT gap  train acc")
for C in [0.01, 0.1, 1, 10]:
    a, b, steps = smo(X, y, C, linear)
    w = (a * y) @ X
    z, fr, bd, gap = kkt_report(a, b, X, y, C, linear)
    acc = (np.sign(X @ w + b) == y).mean()
    print(f"  {C:6g}  {steps:5d}  {np.linalg.norm(w):5.3f}  {2 / np.linalg.norm(w):10.3f}  "
          f"{z:4d}  {fr:5d}  {bd:3d}  {gap:12.4f}  {acc:.2f}")

a, b, _ = smo(X, y, 1.0, linear)
w = (a * y) @ X
primal = 0.5 * w @ w + 1.0 * np.maximum(0, 1 - y * (X @ w + b)).sum()
K = X @ X.T
dual = a.sum() - 0.5 * (a * y) @ K @ (a * y)
print(f"\nC = 1: primal objective {primal:.4f}, dual objective {dual:.4f} (equal at the optimum)")
print(f"w = {np.round(w, 4)}, b = {b:.4f}")

print("\nRBF-kernel SVM on two rings (inner ring class +1, outer ring class -1)")
m = 200
r = np.where(np.arange(m) < m // 2, 1.0, 2.5) + rng.normal(0, 0.25, m)
t = rng.uniform(0, 2 * np.pi, m)
X2 = np.column_stack([r * np.cos(t), r * np.sin(t)])
y2 = np.where(np.arange(m) < m // 2, 1.0, -1.0)
idx = rng.permutation(m)
tr, te = idx[:140], idx[140:]
a, b, _ = smo(X2[tr], y2[tr], 1.0, linear)
acc = (np.sign(decision(a, b, X2[tr], y2[tr], linear, X2[te])) == y2[te]).mean()
print(f"  linear kernel, C = 1:            test acc {acc:.3f}")
print("  gamma     C   support vectors   train acc   test acc")
for g in [0.1, 1, 10, 100]:
    for C in [1, 100]:
        k = rbf(g)
        a, b, _ = smo(X2[tr], y2[tr], C, k)
        ftr = np.sign(decision(a, b, X2[tr], y2[tr], k, X2[tr]))
        fte = np.sign(decision(a, b, X2[tr], y2[tr], k, X2[te]))
        print(f"  {g:5g}  {C:4g}   {int((a > 1e-8).sum()):15d}   {(ftr == y2[tr]).mean():9.3f}   {(fte == y2[te]).mean():.3f}")
