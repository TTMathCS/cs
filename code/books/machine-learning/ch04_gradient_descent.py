"""Chapter 4: linear regression by gradient descent, from scratch.

Synthetic data: 200 flats, price from area and rooms plus noise (the data
of ch02_scaling.py).  Features are standardised; we run gradient descent
with several learning rates and compare with the exact solution.
"""
import numpy as np


def make_flats(seed=2, n=200):
    rng = np.random.default_rng(seed)
    area = rng.normal(70, 20, n).clip(25, None)
    rooms = np.round(area / 25 + rng.normal(0, 0.6, n)).clip(1, None)
    price = 30 + 2.8 * area + 12 * rooms + rng.normal(0, 15, n)
    return np.column_stack([area, rooms]), price


def mse(X, y, w):
    return np.mean((X @ w - y) ** 2)


def gradient_descent(X, y, lr, steps):
    w = np.zeros(X.shape[1])
    losses = [mse(X, y, w)]
    for _ in range(steps):
        grad = 2 * X.T @ (X @ w - y) / len(y)
        w = w - lr * grad
        losses.append(mse(X, y, w))
    return w, losses


if __name__ == "__main__":
    F, y = make_flats()
    mu, sd = F.mean(axis=0), F.std(axis=0)
    X = np.column_stack([np.ones(len(y)), (F - mu) / sd])
    w_exact = np.linalg.lstsq(X, y, rcond=None)[0]
    best = mse(X, y, w_exact)
    H = 2 * X.T @ X / len(y)
    lam = np.linalg.eigvalsh(H)
    print(f"exact solution {w_exact.round(3)}, best MSE {best:.3f}")
    print(f"eigenvalues of the Hessian {lam.round(3)}; 2 / largest = {2 / lam[-1]:.3f}")

    print("\n  lr    loss after 0, 1, 2, 5, 10, 20, 50 steps")
    curves = {}
    for lr in [0.01, 0.1, 0.5, 0.56, 0.6]:
        w, losses = gradient_descent(X, y, lr, 50)
        curves[lr] = losses
        print(f"{lr:5.2f} " + " ".join(f"{losses[t]:9.4g}" for t in [0, 1, 2, 5, 10, 20, 50]))
    w, _ = gradient_descent(X, y, 0.5, 200)
    print("\nlr 0.5 after 200 steps:", w.round(3), " exact:", w_exact.round(3))

    # back to the original units: price = b0 + b1 area + b2 rooms
    b1, b2 = w_exact[1:] / sd
    b0 = w_exact[0] - b1 * mu[0] - b2 * mu[1]
    print(f"in original units: price = {b0:.2f} + {b1:.3f} area + {b2:.2f} rooms"
          f"  (data made with 30 + 2.8 area + 12 rooms)")

    # the gap to the optimum shrinks by |1 - lr * lambda| per step in each eigen-direction
    lr = 0.1
    w, losses = gradient_descent(X, y, lr, 60)
    gaps = np.array(losses) - best
    print(f"\nlr 0.1: gap ratio over the last 10 steps per step {(gaps[60] / gaps[50]) ** 0.1:.4f},"
          f" predicted (1 - lr * smallest eigenvalue)^2 = {(1 - lr * lam[0]) ** 2:.4f}")
