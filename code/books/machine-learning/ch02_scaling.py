"""Chapter 2: scaling features, and why gradient descent cares.

Synthetic flats: area (tens of square metres) and rooms (a few), price made
from them plus noise.  We fit the same straight-line model by gradient
descent on the raw features and on standardised features, and count steps.
"""
import numpy as np


def standardise(X, mean=None, sd=None):
    mean = X.mean(axis=0) if mean is None else mean
    sd = X.std(axis=0) if sd is None else sd
    return (X - mean) / sd, mean, sd


def min_max(X, lo=None, hi=None):
    lo = X.min(axis=0) if lo is None else lo
    hi = X.max(axis=0) if hi is None else hi
    return (X - lo) / (hi - lo), lo, hi


def gradient_descent(A, y, tol=1e-6, max_steps=200_000):
    """Minimise mean squared error ||A w - y||^2 / n with the safe step 1/L."""
    n = len(y)
    H = 2 * A.T @ A / n                       # the loss's curvature (Hessian)
    eig = np.linalg.eigvalsh(H)
    step = 1.0 / eig[-1]                      # L = largest eigenvalue
    w_best = np.linalg.lstsq(A, y, rcond=None)[0]
    best = np.mean((A @ w_best - y) ** 2)
    w = np.zeros(A.shape[1])
    for t in range(1, max_steps + 1):
        w -= step * (2 * A.T @ (A @ w - y) / n)
        if np.mean((A @ w - y) ** 2) - best < tol * best:
            return t, eig[-1] / eig[0]
    return None, eig[-1] / eig[0]


if __name__ == "__main__":
    rng = np.random.default_rng(2)
    n = 200
    area = rng.normal(70, 20, n).clip(25, None)
    rooms = np.round(area / 25 + rng.normal(0, 0.6, n)).clip(1, None)
    price = 30 + 2.8 * area + 12 * rooms + rng.normal(0, 15, n)   # thousands
    X = np.column_stack([area, rooms])
    print("raw feature means", X.mean(axis=0).round(2), "sds", X.std(axis=0).round(2))

    Z, mu, sd = standardise(X)
    print("standardised means", Z.mean(axis=0).round(12) + 0.0, "sds", Z.std(axis=0).round(12))
    M, lo, hi = min_max(X)
    print("min-max ranges", M.min(axis=0), M.max(axis=0))

    ones = np.ones((n, 1))
    for name, F in [("raw", X), ("min-max", M), ("standardised", Z)]:
        steps, kappa = gradient_descent(np.hstack([ones, F]), price)
        print(f"{name:13} condition number {kappa:12.1f}   steps to converge: {steps}")

    # The same scaling must be reused on new data: never recompute it there.
    new = np.array([[85.0, 3.0]])
    print("new flat standardised with the training mean and sd:", standardise(new, mu, sd)[0].round(3))
