"""Chapter 4: solving least squares with QR and the SVD, and why not invert X^T X.

A polynomial design matrix on [0, 1] is badly conditioned.  We make exact
data y = X w_true (no noise at all) and see how many digits each method
recovers.  Householder QR and back substitution are written from scratch.
"""
import numpy as np


def householder_qr(A):
    """Return Q (n x m, orthonormal columns) and R (m x m, upper triangular)."""
    A = A.astype(float).copy()
    n, m = A.shape
    Q = np.eye(n)
    for k in range(m):
        x = A[k:, k]
        v = x.copy()
        v[0] += np.copysign(np.linalg.norm(x), x[0])   # reflect x onto a multiple of e1
        v /= np.linalg.norm(v)
        A[k:, k:] -= 2 * np.outer(v, v @ A[k:, k:])
        Q[:, k:] -= 2 * np.outer(Q[:, k:] @ v, v)
    return Q[:, :m], np.triu(A[:m, :m])


def back_substitution(R, b):
    m = len(b)
    w = np.zeros(m)
    for i in range(m - 1, -1, -1):
        w[i] = (b[i] - R[i, i + 1:] @ w[i + 1:]) / R[i, i]
    return w


def solve_qr(X, y):
    Q, R = householder_qr(X)
    return back_substitution(R, Q.T @ y)


def solve_svd(X, y, rtol=1e-12):
    U, s, Vt = np.linalg.svd(X, full_matrices=False)
    keep = s > rtol * s[0]                       # drop (near-)zero singular values
    return Vt[keep].T @ ((U[:, keep].T @ y) / s[keep])


def solve_normal(X, y):
    return np.linalg.solve(X.T @ X, X.T @ y)


def solve_inverse(X, y):
    return np.linalg.inv(X.T @ X) @ (X.T @ y)


if __name__ == "__main__":
    # A small hand-checkable QR
    X = np.array([[1.0, 1.0], [1.0, 2.0], [1.0, 3.0]])
    Q, R = householder_qr(X)
    print("Q^T Q =", ((Q.T @ Q).round(12) + 0.0).tolist())
    print("R =", R.round(4).tolist(), " Q R = X:", np.allclose(Q @ R, X))
    y = np.array([1.0, 2.0, 2.0])
    print("QR solution", solve_qr(X, y).round(4), " normal equations", solve_normal(X, y).round(4))

    x = np.linspace(0, 1, 50)
    print("\ndegree  cond(X)   cond(X^T X)   relative error of w: normal  inverse   QR       SVD")
    for d in [3, 6, 9, 12]:
        X = np.column_stack([x ** k for k in range(d + 1)])
        w_true = np.ones(d + 1)
        y = X @ w_true
        errs = [np.linalg.norm(f(X, y) - w_true) / np.linalg.norm(w_true)
                for f in (solve_normal, solve_inverse, solve_qr, solve_svd)]
        print(f"{d:6d} {np.linalg.cond(X):9.2e} {np.linalg.cond(X.T @ X):12.2e}      "
              + "  ".join(f"{e:8.1e}" for e in errs))

    # Rank deficient: the same area in square metres and in tens of square metres
    area = np.array([52.0, 75, 40, 98, 63])
    price = np.array([210.0, 255, 140, 390, 240])
    X = np.column_stack([np.ones(5), area, area / 10])
    print("\nduplicate column: rank", np.linalg.matrix_rank(X), "of", X.shape[1])
    print(f"cond(X^T X) = {np.linalg.cond(X.T @ X):.2e}")
    try:
        wn = solve_normal(X, price)
        print("normal equations:", wn.round(4), " w1 + w2/10 =", round(wn[1] + wn[2] / 10, 4))
    except np.linalg.LinAlgError as e:
        print("normal equations fail:", e)
    w = solve_svd(X, price)
    print("SVD minimum-norm solution", w.round(4), " predictions", (X @ w).round(2))
    print("single-column fit slope", np.polyfit(area, price, 1)[0].round(4),
          "= w1 + w2/10 =", round(w[1] + w[2] / 10, 4))
