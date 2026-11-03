"""Chapter 11.3: bagging and random forests from scratch, with out-of-bag error.
Uses the tree code of ch11_cart.py."""
import numpy as np
from ch11_cart import grow, predict, make_data


def forest(X, y, n_trees, max_features, rng):
    """Each tree: a bootstrap sample (n draws with replacement) and, at every split,
    a random subset of max_features features (None = all of them = plain bagging)."""
    n = len(y)
    trees, inbag = [], []
    for _ in range(n_trees):
        idx = rng.integers(0, n, n)
        trees.append(grow(X, y, idx, "classify", max_features=max_features, rng=rng))
        mask = np.zeros(n, bool)
        mask[idx] = True
        inbag.append(mask)
    return trees, np.array(inbag)


def vote(trees, X):
    return np.mean([predict(t, X, "classify") for t in trees], axis=0)   # fraction voting 1


rng = np.random.default_rng(7)
# the 2 informative features of make_data, plus 4 noisy copies of each: 10 features in all
Xtr2, ytr = make_data(400, rng)
Xte2, yte = make_data(2000, rng)
Xtr = np.column_stack([Xtr2] + [Xtr2 + rng.normal(0, 0.1, (400, 2)) for _ in range(4)])
Xte = np.column_stack([Xte2] + [Xte2 + rng.normal(0, 0.1, (2000, 2)) for _ in range(4)])

single = grow(Xtr, ytr, np.arange(400), "classify")
print(f"One full tree: test accuracy {np.mean(predict(single, Xte, 'classify') == yte):.3f}")
print(f"Probability a given point is left out of a bootstrap sample: (1 - 1/400)^400 = {(1 - 1 / 400) ** 400:.4f}"
      f"  (1/e = {np.exp(-1):.4f})")

for name, mf in [("bagging (all 10 features per split)", None), ("random forest (3 of 10 per split)", 3)]:
    trees, inbag = forest(Xtr, ytr, 100, mf, rng)
    P = np.array([predict(t, Xtr, "classify") for t in trees])            # trees x points
    T = np.array([predict(t, Xte, "classify") for t in trees])
    print(f"\n{name}")
    print("  trees   OOB acc   test acc")
    for k in [1, 5, 10, 25, 50, 100]:
        out = ~inbag[:k]                                   # trees that did not see each point
        cnt = out.sum(0)
        ok = cnt > 0
        oob_vote = (P[:k] * out).sum(0)[ok] / cnt[ok]
        oob = np.mean((oob_vote > 0.5) == ytr[ok])
        test = np.mean((T[:k].mean(0) > 0.5) == yte)
        print(f"  {k:5d}   {oob:7.3f}   {test:7.3f}")
    # correlation between two trees' errors on the test set
    E = (T != yte).astype(float)
    C = np.corrcoef(E)
    print(f"  mean correlation between trees' test errors: {C[np.triu_indices(len(trees), 1)].mean():.3f}")
    print(f"  mean accuracy of a single tree: {np.mean(T == yte):.3f}")
