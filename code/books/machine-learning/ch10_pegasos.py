"""Chapter 10.3 and 10.6: hinge loss against other losses, and training a linear SVM in
the primal with Pegasos (stochastic subgradient descent), checked against an exact
solution found by dual coordinate ascent."""
import numpy as np

print("1. Losses as functions of the margin m = y f(x)")
print("      m    0-1   hinge max(0,1-m)   logistic log2(1+e^-m)   squared (1-m)^2")
for m in [-2, -1, 0, 0.5, 1, 2, 3]:
    print(f"  {m:5.1f}    {int(m <= 0)}    {max(0, 1 - m):12.3f}   {np.log2(1 + np.exp(-m)):17.3f}"
          f"   {(1 - m) ** 2:15.3f}")

rng = np.random.default_rng(5)
n = 100
X = np.vstack([rng.normal([1, 1], 1.0, (n // 2, 2)), rng.normal([-1, -1], 1.0, (n // 2, 2))])
y = np.concatenate([np.ones(n // 2), -np.ones(n // 2)])
Xa = np.column_stack([X, np.ones(n)])       # constant feature: the bias is the last weight
lam = 0.01                                  # lambda = 1/(n C) with C = 1


def objective(w):
    return 0.5 * lam * w @ w + np.maximum(0, 1 - y * (Xa @ w)).mean()


def dual_coordinate_ascent(epochs=200):
    """Exact solver for min lam/2 |w|^2 + mean hinge: the dual has box constraints only,
    0 <= a_i <= 1/(lam n), and each coordinate is maximised in closed form."""
    C = 1 / (lam * n)
    a, w = np.zeros(n), np.zeros(3)
    Q = (Xa ** 2).sum(1)
    for _ in range(epochs):
        for i in rng.permutation(n):
            g = y[i] * (w @ Xa[i]) - 1
            new = min(max(a[i] - g / Q[i], 0.0), C)
            w += (new - a[i]) * y[i] * Xa[i]
            a[i] = new
    return w


w_star = dual_coordinate_ascent()
f_star = objective(w_star)
print(f"\n2. Exact optimum (dual coordinate ascent): w = {np.round(w_star, 4)}, objective {f_star:.6f}")


def pegasos(T, seed=0):
    """At step t: pick one example, step size 1/(lam t), subgradient of lam/2|w|^2 + hinge_i."""
    r = np.random.default_rng(seed)
    w, avg = np.zeros(3), np.zeros(3)
    marks, out = {10, 100, 1000, 10000, 100000}, []
    for t in range(1, T + 1):
        i = r.integers(n)
        eta = 1.0 / (lam * t)
        if y[i] * (w @ Xa[i]) < 1:
            w = (1 - eta * lam) * w + eta * y[i] * Xa[i]
        else:
            w = (1 - eta * lam) * w
        norm = np.linalg.norm(w)                 # optional projection onto |w| <= 1/sqrt(lam)
        if norm > 1 / np.sqrt(lam):
            w *= (1 / np.sqrt(lam)) / norm
        avg += (w - avg) / t                     # running average of the iterates
        if t in marks:
            out.append((t, objective(w) - f_star, objective(avg) - f_star))
    return w, out


w, out = pegasos(100000)
print("\n3. Pegasos: objective minus the optimum")
print("        T     last iterate    averaged iterate")
for t, g1, g2 in out:
    print(f"  {t:7d}     {g1:12.6f}    {g2:12.6f}")
print(f"  final w = {np.round(w, 4)}")
acc = (np.sign(Xa @ w) == y).mean()
print(f"  training accuracy {acc:.2f}; support vectors (margin <= 1): {(y * (Xa @ w_star) <= 1 + 1e-6).sum()}")

print("\n4. Hand trace: first three Pegasos steps on the points of 10.2, lam = 0.1, no bias")
P = np.array([[2.0, 0.0], [3.0, 3.0], [0.0, 2.0]])
lab = np.array([-1.0, 1.0, -1.0])
w = np.zeros(2)
for t, i in enumerate([1, 0, 2], start=1):
    eta = 1 / (0.1 * t)
    m = lab[i] * (w @ P[i])
    w = (1 - eta * 0.1) * w + (eta * lab[i] * P[i] if m < 1 else 0)
    print(f"  t = {t}: example {P[i]}, label {lab[i]:+.0f}, margin before {m:.3f}, eta = {eta:.3f}, w = {np.round(w, 4)}")
