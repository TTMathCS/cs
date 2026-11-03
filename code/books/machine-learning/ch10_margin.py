"""Chapter 10.1-10.2: the geometry of the margin, and the hard-margin SVM on a tiny
data set solved exactly by trying every possible set of support vectors."""
import itertools
import numpy as np


def signed_distance(w, b, x):
    """Signed distance from point x to the hyperplane w.x + b = 0."""
    return (w @ x + b) / np.linalg.norm(w)


print("1. Distance from a point to a line")
w, b = np.array([3.0, 4.0]), -10.0
for x in [np.array([0.0, 0.0]), np.array([2.0, 1.0]), np.array([4.0, 3.0])]:
    print(f"   x = {x}: w.x + b = {w @ x + b:6.1f}, distance = {signed_distance(w, b, x):5.2f}")
print("   scaling (w, b) by 7 changes w.x + b but not the distance:",
      f"{signed_distance(7 * w, 7 * b, np.array([4.0, 3.0])):.2f}")

X = np.array([[0, 0], [2, 0], [0, 2], [3, 3], [4, 4], [5, 2]], dtype=float)
y = np.array([-1, -1, -1, 1, 1, 1], dtype=float)


def hard_margin_exact(X, y):
    """Try each candidate support set S: solve  w = sum_{i in S} a_i y_i x_i,
    y_i (w.x_i + b) = 1 for i in S, sum a_i y_i = 0.  Keep the feasible solution
    (all a_i >= 0, all margins >= 1) with the smallest |w|. Exponential: tiny data only."""
    n, d = X.shape
    best = None
    for size in range(2, n + 1):
        for S in itertools.combinations(range(n), size):
            S = list(S)
            G = (X[S] @ X[S].T) * np.outer(y[S], y[S])
            A = np.zeros((size + 1, size + 1))
            A[:size, :size] = G
            A[:size, size] = y[S]           # y_i (sum_j a_j y_j x_j.x_i + b) = 1
            A[size, :size] = y[S]           # sum a_j y_j = 0
            rhs = np.concatenate([np.ones(size), [0.0]])
            sol, *_ = np.linalg.lstsq(A, rhs, rcond=None)
            if not np.allclose(A @ sol, rhs):
                continue
            a, b0 = sol[:size], sol[size]
            if (a < -1e-9).any():
                continue
            w0 = (a * y[S]) @ X[S]
            if (y * (X @ w0 + b0) < 1 - 1e-9).any():
                continue
            if best is None or w0 @ w0 < best[0] @ best[0] - 1e-12:
                alpha = np.zeros(n)
                alpha[S] = a
                best = (w0, b0, alpha)
    return best


w, b, alpha = hard_margin_exact(X, y)
print("\n2. Hard-margin SVM on six points")
print(f"   w = {w}, b = {b:.4f}")
print(f"   |w| = {np.linalg.norm(w):.4f}; margin 1/|w| = {1 / np.linalg.norm(w):.4f}; "
      f"width 2/|w| = {2 / np.linalg.norm(w):.4f}")
print("   point     label  y(w.x+b)  alpha")
for xi, yi, ai in zip(X, y, alpha):
    print(f"   {str(xi):9s} {yi:+.0f}    {yi * (w @ xi + b):7.3f}  {ai:.4f}")
print(f"   sum alpha_i y_i = {alpha @ y:.2e};  sum alpha_i y_i x_i = {(alpha * y) @ X}")
print(f"   dual objective sum(alpha) - |w|^2/2 = {alpha.sum() - 0.5 * w @ w:.4f}; "
      f"primal |w|^2/2 = {0.5 * w @ w:.4f}")

print("\n3. Any other separating line has a smaller margin, e.g. w = (1, 2), b = -5.5:")
w2, b2 = np.array([1.0, 2.0]), -5.5
m = (y * (X @ w2 + b2)).min() / np.linalg.norm(w2)
print(f"   smallest distance from a point to it = {m:.4f}  (< {1 / np.linalg.norm(w):.4f})")
