"""Chapter 2: splitting well, and three kinds of leakage shown by numbers.

1. stratified vs random splits on imbalanced labels
2. by time: a random split lets the model peek at the future
3. by group: several records per patient
4. selecting features on all the data before cross-validation
All data is synthetic with fixed seeds.
"""
import numpy as np


def stratified_split(y, test_frac, rng):
    test = []
    for c in np.unique(y):
        idx = rng.permutation(np.flatnonzero(y == c))
        test.extend(idx[:round(test_frac * len(idx))])
    test = np.array(sorted(test))
    train = np.setdiff1d(np.arange(len(y)), test)
    return train, test


def nn1_predict(Xtr, ytr, Xte):
    d2 = ((Xte[:, None, :] - Xtr[None, :, :]) ** 2).sum(axis=2)
    return ytr[d2.argmin(axis=1)]


def correlations(X, y):
    Xc, yc = X - X.mean(axis=0), y - y.mean()
    return (Xc * yc[:, None]).sum(axis=0) / np.sqrt((Xc ** 2).sum(axis=0) * (yc ** 2).sum())


def kfold_indices(n, k, rng):
    return np.array_split(rng.permutation(n), k)


if __name__ == "__main__":
    rng = np.random.default_rng(3)

    # 1. Stratification: 200 examples, 10% positive, 20% test set.
    y = np.array([1] * 20 + [0] * 180)
    rand_counts = [y[rng.permutation(200)[:40]].sum() for _ in range(1000)]
    strat_counts = [y[stratified_split(y, 0.2, rng)[1]].sum() for _ in range(1000)]
    print("positives in a 40-example test set (should be 4):")
    print(f"  random:     min {min(rand_counts)}, max {max(rand_counts)},"
          f" fraction of splits with exactly 4: {np.mean(np.array(rand_counts) == 4):.2f}")
    print(f"  stratified: min {min(strat_counts)}, max {max(strat_counts)}")

    # 2. Time: a random walk; predict each day's value from the nearest day.
    days = np.arange(500, dtype=float)
    value = np.cumsum(rng.normal(0, 1, 500))
    X = days[:, None]
    perm = rng.permutation(500)
    tr, te = perm[:400], perm[400:]
    err_random = np.mean(np.abs(nn1_predict(X[tr], value[tr], X[te]) - value[te]))
    tr, te = np.arange(400), np.arange(400, 500)
    err_time = np.mean(np.abs(nn1_predict(X[tr], value[tr], X[te]) - value[te]))
    print(f"\nrandom walk, mean absolute error: random split {err_random:.2f},"
          f" split by time {err_time:.2f}")

    # 3. Groups: 60 patients, 5 scans each.  The label is per patient and only
    #    weakly related to the features; each patient has a personal signature.
    n_pat, per = 60, 5
    label = rng.integers(0, 2, n_pat)
    signature = rng.normal(0, 1, (n_pat, 10)) + 0.3 * label[:, None]
    Xs = np.repeat(signature, per, axis=0) + rng.normal(0, 0.1, (n_pat * per, 10))
    ys = np.repeat(label, per)
    group = np.repeat(np.arange(n_pat), per)
    perm = rng.permutation(n_pat * per)
    tr, te = perm[:240], perm[240:]
    acc_rows = np.mean(nn1_predict(Xs[tr], ys[tr], Xs[te]) == ys[te])
    test_pat = rng.permutation(n_pat)[:12]
    te = np.flatnonzero(np.isin(group, test_pat))
    tr = np.flatnonzero(~np.isin(group, test_pat))
    acc_groups = np.mean(nn1_predict(Xs[tr], ys[tr], Xs[te]) == ys[te])
    print(f"patients, 1-NN accuracy: random rows {acc_rows:.2f}, whole patients held out {acc_groups:.2f}")

    # 4. Feature selection outside the folds: pure noise, labels are coin flips.
    n, p, keep = 50, 5000, 20
    Xn = rng.normal(0, 1, (n, p))
    yn = rng.integers(0, 2, n)
    folds = kfold_indices(n, 5, rng)
    top_all = np.argsort(-np.abs(correlations(Xn, yn)))[:keep]
    wrong, right = [], []
    for f in folds:
        trn = np.setdiff1d(np.arange(n), f)
        wrong.append(np.mean(nn1_predict(Xn[trn][:, top_all], yn[trn], Xn[f][:, top_all]) == yn[f]))
        top_tr = np.argsort(-np.abs(correlations(Xn[trn], yn[trn])))[:keep]
        right.append(np.mean(nn1_predict(Xn[trn][:, top_tr], yn[trn], Xn[f][:, top_tr]) == yn[f]))
    print(f"noise features, 5-fold CV accuracy: select on all data {np.mean(wrong):.2f},"
          f" select inside each fold {np.mean(right):.2f}")
