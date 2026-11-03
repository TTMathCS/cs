"""Chapter 11.5: gradient boosting for regression from scratch (Friedman 2001),
with small regression trees from ch11_cart.py, on Friedman's benchmark function #1."""
import numpy as np
from ch11_cart import grow, predict


def friedman1(n, rng, noise=1.0):
    """y = 10 sin(pi x0 x1) + 20 (x2 - 0.5)^2 + 10 x3 + 5 x4 + noise; x5..x9 are unused."""
    X = rng.uniform(0, 1, (n, 10))
    f = 10 * np.sin(np.pi * X[:, 0] * X[:, 1]) + 20 * (X[:, 2] - 0.5) ** 2 + 10 * X[:, 3] + 5 * X[:, 4]
    return X, f + rng.normal(0, noise, n)


def boost(X, y, rounds, lr, depth, Xte=None, yte=None, marks=()):
    """Squared loss: the negative gradient is the residual y - F, so each tree fits residuals."""
    F = np.full(len(y), y.mean())
    Fte = np.full(len(Xte), y.mean()) if Xte is not None else None
    trees, log = [], []
    for m in range(1, rounds + 1):
        r = y - F                                       # pseudo-residuals
        t = grow(X, r, np.arange(len(y)), "regress", max_depth=depth)
        F += lr * predict(t, X, "regress")
        trees.append(t)
        if Xte is not None:
            Fte += lr * predict(t, Xte, "regress")
            if m in marks:
                log.append((m, np.mean((y - F) ** 2), np.mean((yte - Fte) ** 2)))
    return trees, log


if __name__ == "__main__":
    print("Hand example: stumps with learning rate 1 on four points")
    x = np.array([[1.0], [2.0], [3.0], [4.0]])
    y = np.array([1.0, 3.0, 2.0, 6.0])
    F = np.full(4, y.mean())
    print(f"  start: F = mean = {y.mean():.2f}")
    for m in range(1, 4):
        r = y - F
        t = grow(x, r, np.arange(4), "regress", max_depth=1)
        step = predict(t, x, "regress")
        F = F + step
        print(f"  round {m}: residuals {np.round(r, 3)}, split x <= {t.threshold:.1f}, "
              f"step {np.round(step, 3)}, F = {np.round(F, 3)}, SSE {np.sum((y - F) ** 2):.3f}")

    rng = np.random.default_rng(9)
    Xtr, ytr = friedman1(500, rng)
    Xte, yte = friedman1(2000, rng)
    print(f"\nFriedman #1, 500 training points, noise variance 1")
    print(f"  predicting the mean:      test MSE {np.mean((yte - ytr.mean()) ** 2):.3f}")
    for md in [3, 6, 50]:
        t = grow(Xtr, ytr, np.arange(500), "regress", max_depth=md)
        print(f"  one tree, depth {md:2d}:      test MSE {np.mean((yte - predict(t, Xte, 'regress')) ** 2):.3f}")
    Xa = np.column_stack([np.ones(500), Xtr])
    w = np.linalg.lstsq(Xa, ytr, rcond=None)[0]
    print(f"  linear regression:        test MSE {np.mean((yte - np.column_stack([np.ones(2000), Xte]) @ w) ** 2):.3f}")

    marks = (1, 10, 50, 100, 200, 400)
    for lr, depth in [(1.0, 3), (0.1, 1), (0.1, 3)]:
        _, log = boost(Xtr, ytr, 400, lr, depth, Xte, yte, marks)
        print(f"\nBoosting, learning rate {lr}, trees of depth {depth}")
        print("  trees   train MSE   test MSE")
        for m, tr, te in log:
            print(f"  {m:5d}   {tr:9.3f}   {te:8.3f}")
