"""Chapter 9.1: k-nearest neighbours from scratch. Choosing k on a validation
set, three distance metrics, and what happens when one feature is in the wrong units."""
import numpy as np


def make_moons(n, noise, rng):
    """Two interleaving half circles, labels 0 and 1."""
    t = rng.uniform(0, np.pi, n)
    y = rng.integers(0, 2, n)
    x0 = np.where(y == 0, np.cos(t), 1 - np.cos(t))
    x1 = np.where(y == 0, np.sin(t), 0.5 - np.sin(t))
    X = np.column_stack([x0, x1]) + rng.normal(0, noise, (n, 2))
    return X, y


def distances(A, B, metric):
    """All distances between rows of A (m x d) and rows of B (n x d): an m x n matrix."""
    diff = A[:, None, :] - B[None, :, :]
    if metric == "euclidean":
        return np.sqrt((diff ** 2).sum(axis=2))
    if metric == "manhattan":
        return np.abs(diff).sum(axis=2)
    if metric == "chebyshev":
        return np.abs(diff).max(axis=2)
    raise ValueError(metric)


def knn_predict(Xtr, ytr, Xte, k, metric="euclidean"):
    D = distances(Xte, Xtr, metric)
    idx = np.argsort(D, axis=1, kind="stable")[:, :k]   # the k nearest training rows
    votes = ytr[idx].mean(axis=1)                          # fraction voting for class 1
    return (votes > 0.5).astype(int)                       # k odd: never a tie


rng = np.random.default_rng(0)
X, y = make_moons(600, 0.25, rng)
Xtr, ytr = X[:300], y[:300]
Xva, yva = X[300:450], y[300:450]
Xte, yte = X[450:], y[450:]

print("Choosing k on the validation set (Euclidean distance)")
print("   k   train acc   valid acc")
best_k, best_acc = None, -1
for k in [1, 3, 5, 9, 15, 25, 51, 101, 201]:
    tr = (knn_predict(Xtr, ytr, Xtr, k) == ytr).mean()
    va = (knn_predict(Xtr, ytr, Xva, k) == yva).mean()
    print(f"{k:4d}     {tr:.3f}       {va:.3f}")
    if va > best_acc:
        best_k, best_acc = k, va
te = (knn_predict(Xtr, ytr, Xte, best_k) == yte).mean()
print(f"best k = {best_k}; test accuracy with it = {te:.3f}")

print("\nThree metrics, k = 15, validation accuracy")
for m in ["euclidean", "manhattan", "chebyshev"]:
    va = (knn_predict(Xtr, ytr, Xva, 15, m) == yva).mean()
    print(f"  {m:10s} {va:.3f}")

print("\nThe same data with feature 1 measured in millimetres (times 1000)")
print("plus one useless feature of pure noise with large spread")
noise_tr = rng.normal(0, 5, (300, 1))
noise_va = rng.normal(0, 5, (150, 1))
Xtr2 = np.column_stack([Xtr[:, 0] * 1000, Xtr[:, 1], noise_tr])
Xva2 = np.column_stack([Xva[:, 0] * 1000, Xva[:, 1], noise_va])
raw = (knn_predict(Xtr2, ytr, Xva2, 15) == yva).mean()
mu, sd = Xtr2.mean(axis=0), Xtr2.std(axis=0)
std = (knn_predict((Xtr2 - mu) / sd, ytr, (Xva2 - mu) / sd, 15) == yva).mean()
only2 = (knn_predict(((Xtr2 - mu) / sd)[:, :2], ytr, ((Xva2 - mu) / sd)[:, :2], 15) == yva).mean()
print(f"  raw units:                     {raw:.3f}")
print(f"  standardised (all 3 features): {std:.3f}")
print(f"  standardised, noise dropped:   {only2:.3f}")

print("\nHand trace: query (0.5, 0.25) against six training points")
P = np.array([[0.0, 0.0], [1.0, 0.0], [0.5, 1.0], [0.4, 0.3], [0.9, 0.5], [0.2, 0.6]])
lab = np.array([0, 0, 0, 1, 1, 0])
q = np.array([[0.5, 0.25]])
d = distances(q, P, "euclidean")[0]
for i in np.argsort(d, kind="stable"):
    print(f"  point {i} ({P[i,0]:.1f}, {P[i,1]:.1f}) label {lab[i]} distance {d[i]:.4f}")
for k in (1, 3, 5):
    print(f"  k = {k}: predicts {knn_predict(P, lab, q, k)[0]}")
