"""Chapter 1: training, validation and test data.

Synthetic two-class data (two overlapping clouds of points, fixed seed).
We fit k-nearest-neighbours, choose k on the validation set, and only then
look at the test set once.  Then we repeat the whole experiment many times
to show why the score used for choosing is too optimistic.
"""
import numpy as np


def make_data(rng, n):
    """n points per class: class 0 around (0, 0), class 1 around (1.5, 1.5)."""
    x0 = rng.normal(0.0, 1.0, size=(n, 2))
    x1 = rng.normal(1.5, 1.0, size=(n, 2))
    X = np.vstack([x0, x1])
    y = np.array([0] * n + [1] * n)
    return X, y


def knn_predict(X_train, y_train, X_query, k):
    # squared distances from every query point to every training point
    d2 = ((X_query[:, None, :] - X_train[None, :, :]) ** 2).sum(axis=2)
    nearest = np.argsort(d2, axis=1, kind="stable")[:, :k]
    votes = y_train[nearest].mean(axis=1)          # fraction voting for class 1
    return (votes > 0.5).astype(int)               # k is odd: no ties


def accuracy(y_true, y_pred):
    return float((y_true == y_pred).mean())


def split(rng, X, y, n_train, n_val):
    order = rng.permutation(len(y))
    tr, va, te = order[:n_train], order[n_train:n_train + n_val], order[n_train + n_val:]
    return (X[tr], y[tr]), (X[va], y[va]), (X[te], y[te])


KS = [1, 3, 5, 9, 15, 25, 51]

if __name__ == "__main__":
    rng = np.random.default_rng(0)
    X, y = make_data(rng, 150)                       # 300 points
    (Xtr, ytr), (Xva, yva), (Xte, yte) = split(rng, X, y, 180, 60)
    print(f"train {len(ytr)}, validation {len(yva)}, test {len(yte)}")
    print("   k   train acc   val acc")
    val_scores = {}
    for k in KS:
        tr_acc = accuracy(ytr, knn_predict(Xtr, ytr, Xtr, k))
        va_acc = accuracy(yva, knn_predict(Xtr, ytr, Xva, k))
        val_scores[k] = va_acc
        print(f"{k:4d}   {tr_acc:9.3f}   {va_acc:7.3f}")
    best_k = max(KS, key=lambda k: (val_scores[k], -k))   # ties: smaller k
    # refit on train + validation, then look at the test set exactly once
    Xfull, yfull = np.vstack([Xtr, Xva]), np.concatenate([ytr, yva])
    test_acc = accuracy(yte, knn_predict(Xfull, yfull, Xte, best_k))
    print(f"chosen k = {best_k}; test accuracy = {test_acc:.3f}")

    # Repeat with fresh data 200 times: the best validation score is biased up.
    best_val, test_of_best = [], []
    for _ in range(200):
        X, y = make_data(rng, 150)
        (Xtr, ytr), (Xva, yva), (Xte, yte) = split(rng, X, y, 180, 60)
        scores = {k: accuracy(yva, knn_predict(Xtr, ytr, Xva, k)) for k in KS}
        k = max(KS, key=lambda k: (scores[k], -k))
        best_val.append(scores[k])
        test_of_best.append(accuracy(yte, knn_predict(Xtr, ytr, Xte, k)))
    print(f"over 200 repeats: mean best validation acc = {np.mean(best_val):.3f},"
          f" mean test acc of that k = {np.mean(test_of_best):.3f}")
