"""Chapter 4: many features, the design matrix, and polynomial features.

Part 1: price from area and rooms (two features plus an intercept).
Part 2: a curve, fitted by a straight line and by polynomials, using
synthetic data from y = sin(2 pi x) + noise with a fixed seed.
"""
import numpy as np
from ch04_line_fit import AREA, PRICE

ROOMS = np.array([2, 3, 1, 4, 3, 3, 2, 2.5, 2, 3])   # flat 9: filled in with the median


def design(*cols):
    """Design matrix: a column of ones, then the given feature columns."""
    return np.column_stack([np.ones(len(cols[0]))] + list(cols))


def least_squares(X, y):
    return np.linalg.solve(X.T @ X, X.T @ y)


def poly_design(x, degree):
    return np.column_stack([x ** k for k in range(degree + 1)])


if __name__ == "__main__":
    X = design(AREA, ROOMS)
    w = least_squares(X, PRICE)
    print(f"price = {w[0]:.2f} + {w[1]:.3f} area {'+' if w[2] >= 0 else '-'} {abs(w[2]):.2f} rooms")
    r = PRICE - X @ w
    print("X^T r =", (X.T @ r).round(8) + 0.0, "(the residual is orthogonal to every column)")
    print("rooms alone: price = {:.2f} + {:.2f} rooms".format(*least_squares(design(ROOMS), PRICE)))
    print(f"correlation of area and rooms: {np.corrcoef(AREA, ROOMS)[0, 1]:.3f}")

    rng = np.random.default_rng(9)
    x = np.sort(rng.uniform(0, 1, 15))
    y = np.sin(2 * np.pi * x) + rng.normal(0, 0.2, 15)
    x_new = np.linspace(0, 1, 200)
    y_new = np.sin(2 * np.pi * x_new)              # the noise-free truth
    print("\ndegree  train RMSE  RMSE vs truth on a fine grid")
    for d in [0, 1, 3, 5, 9, 14]:
        P = poly_design(x, d)
        wd = np.linalg.lstsq(P, y, rcond=None)[0]
        train = np.sqrt(np.mean((P @ wd - y) ** 2))
        truth = np.sqrt(np.mean((poly_design(x_new, d) @ wd - y_new) ** 2))
        print(f"{d:6d}  {train:10.4f}  {truth:12.4f}")
