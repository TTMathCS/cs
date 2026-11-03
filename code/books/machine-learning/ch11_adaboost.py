"""Chapter 11.4: AdaBoost (Freund and Schapire 1997) with decision stumps, from scratch.
Checks the training-error bound prod 2 sqrt(eps (1 - eps)) and the exponential loss."""
import numpy as np


def best_stump(X, y, w):
    """Weighted stump: predict s if x_f > t else -s. Returns (error, f, t, s)."""
    best = (np.inf, 0, 0.0, 1)
    for f in range(X.shape[1]):
        order = np.argsort(X[:, f], kind="stable")
        xs, ys, ws = X[order, f], y[order], w[order]
        # error of 'predict +1 to the right of the cut' = weight of +1 on the left + weight of -1 on the right
        pos_left = np.concatenate([[0], np.cumsum(ws * (ys == 1))])
        neg_left = np.concatenate([[0], np.cumsum(ws * (ys == -1))])
        err = pos_left + (neg_left[-1] - neg_left)
        cuts = np.concatenate([[xs[0] - 1], (xs[:-1] + xs[1:]) / 2, [xs[-1] + 1]])
        valid = np.concatenate([[True], xs[1:] > xs[:-1], [True]])
        for e, s in [(err, 1), (1 - err, -1)]:
            e = np.where(valid, e, np.inf)
            k = int(np.argmin(e))
            if e[k] < best[0]:
                best = (e[k], f, cuts[k], s)
    return best


def stump_predict(X, f, t, s):
    return np.where(X[:, f] > t, s, -s)


def adaboost(X, y, rounds, verbose_rounds=0):
    n = len(y)
    w = np.full(n, 1 / n)
    model, bound = [], 1.0
    for m in range(rounds):
        eps, f, t, s = best_stump(X, y, w)
        alpha = 0.5 * np.log((1 - eps) / eps)
        h = stump_predict(X, f, t, s)
        if m < verbose_rounds:
            print(f"  round {m + 1}: stump x{f} > {t:.3f} -> {s:+d}, weighted error {eps:.4f}, alpha {alpha:.4f}")
        w = w * np.exp(-alpha * y * h)
        Z = w.sum()
        bound *= Z                                   # Z = 2 sqrt(eps (1 - eps))
        w /= Z
        model.append((alpha, f, t, s))
    return model


def score(model, X, upto=None):
    return sum(a * stump_predict(X, f, t, s) for a, f, t, s in model[:upto])


print("Hand example: six points on a line, labels + + - - + +")
x = np.array([[1.0], [2.0], [3.0], [4.0], [5.0], [6.0]])
yy = np.array([1, 1, -1, -1, 1, 1])
small = adaboost(x, yy, 3, verbose_rounds=3)
print(f"  combined sign after 3 rounds: {np.sign(score(small, x)).astype(int)}  (true {yy})")

rng = np.random.default_rng(8)


def make(n):
    """Class +1 inside a circle of radius sqrt(2 ln 2) around the origin in 2-D, Gaussian inputs:
    about half the points in each class. A single stump cannot do this."""
    X = rng.normal(0, 1, (n, 2))
    y = np.where((X ** 2).sum(1) < 2 * np.log(2), 1, -1)
    flip = rng.random(n) < 0.05
    return X, np.where(flip, -y, y)


Xtr, ytr = make(500)
Xte, yte = make(5000)
model = adaboost(Xtr, ytr, 400)
print("\nCircle data, 500 training points, 5% label noise")
print("  rounds  train err  bound prod Z  exp loss  test err")
for M in [1, 2, 5, 10, 25, 50, 100, 200, 400]:
    F = score(model, Xtr, M)
    eps_list = []
    w = np.full(500, 1 / 500)
    bound = 1.0
    for a, f, t, s in model[:M]:
        h = stump_predict(Xtr, f, t, s)
        e = w[h != ytr].sum()
        bound *= 2 * np.sqrt(e * (1 - e))
        w = w * np.exp(-a * ytr * h)
        w /= w.sum()
    print(f"  {M:6d}  {np.mean(np.sign(F) != ytr):9.3f}  {bound:12.4f}  {np.mean(np.exp(-ytr * F)):8.4f}"
          f"  {np.mean(np.sign(score(model, Xte, M)) != yte):8.3f}")
