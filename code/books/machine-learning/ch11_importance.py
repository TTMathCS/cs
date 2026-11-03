"""Chapter 11.7: impurity-based versus permutation feature importance, and two pitfalls:
noise features that a deep tree still uses, and a near-duplicate feature that splits the credit."""
import numpy as np
from ch11_cart import grow, predict
from ch11_gboost import friedman1, boost


def impurity_importance(trees, d):
    imp = np.zeros(d)
    stack = list(trees)
    while stack:
        t = stack.pop()
        if t.feature is not None:
            imp[t.feature] += t.gain
            stack += [t.left, t.right]
    return imp / imp.sum()


def permutation_importance(predict_fn, X, y, rng, repeats=5):
    """Increase in test MSE when one column is shuffled (its link to y is broken)."""
    base = np.mean((y - predict_fn(X)) ** 2)
    out = np.zeros(X.shape[1])
    for j in range(X.shape[1]):
        for _ in range(repeats):
            Xp = X.copy()
            Xp[:, j] = rng.permutation(Xp[:, j])
            out[j] += (np.mean((y - predict_fn(Xp)) ** 2) - base) / repeats
    return out, base


rng = np.random.default_rng(10)
Xtr, ytr = friedman1(500, rng)
Xte, yte = friedman1(1000, rng)
# feature 10: a near-copy of feature 3 (correlation about 0.99)
Xtr = np.column_stack([Xtr, Xtr[:, 3] + rng.normal(0, 0.03, 500)])
Xte = np.column_stack([Xte, Xte[:, 3] + rng.normal(0, 0.03, 1000)])
names = [f"x{j}" for j in range(10)] + ["x3copy"]
true_use = ["yes"] * 5 + ["no"] * 5 + ["copy"]

deep = grow(Xtr, ytr, np.arange(500), "regress")
trees, _ = boost(Xtr, ytr, 200, 0.1, 3)
mean = ytr.mean()


def boosted(X):
    return mean + 0.1 * sum(predict(t, X, "regress") for t in trees)


imp_deep = impurity_importance([deep], 11)
imp_boost = impurity_importance(trees, 11)
perm, base = permutation_importance(boosted, Xte, yte, rng)
perm_deep, base_deep = permutation_importance(lambda X: predict(deep, X, "regress"), Xte, yte, rng)
print(f"Friedman #1 plus a near-copy of x3; test MSE: deep tree {base_deep:.2f}, boosted trees {base:.2f}")
print("feature  used by f?  impurity(deep tree)  impurity(boosting)  permutation(deep)  permutation(boosting)")
for j in range(11):
    print(f"{names[j]:7s}  {true_use[j]:9s}  {imp_deep[j]:18.3f}  {imp_boost[j]:18.3f}  {perm_deep[j]:17.3f}  {perm[j]:20.3f}")
print(f"share of impurity importance on the five unused features: deep tree {imp_deep[5:10].sum():.3f},"
      f" boosting {imp_boost[5:10].sum():.3f}")
