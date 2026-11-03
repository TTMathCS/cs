# Chapter 20: a shortcut ("Clever Hans") feature and distribution shift.
# The label depends on a weak real signal. In the training data a "watermark" feature agrees with the
# label 95% of the time; in deployment it agrees 50% (no information) or 5% (reversed).
import numpy as np

rng = np.random.default_rng(0)


def make(n, agree):
    y = rng.integers(0, 2, n)
    real = (2 * y - 1) * 1.0 + rng.normal(0, 1.0, n)          # the real signal: class means -1 and +1
    mark = np.where(rng.random(n) < agree, y, 1 - y) + rng.normal(0, 0.1, n)
    return np.column_stack([real, mark]), y


def train_logistic(X, y, steps=3000, lr=0.5):
    Xb = np.column_stack([X, np.ones(len(X))])
    w = np.zeros(Xb.shape[1])
    for _ in range(steps):
        p = 1 / (1 + np.exp(-Xb @ w))
        w -= lr * Xb.T @ (p - y) / len(y)
    return w


def acc(w, X, y):
    return np.mean(((np.column_stack([X, np.ones(len(X))]) @ w) > 0) == y)


Xtr, ytr = make(5000, 0.95)
w_all = train_logistic(Xtr, ytr)
w_real = train_logistic(Xtr[:, :1], ytr)
print("weights (real signal, watermark, bias) when both features are used:", np.round(w_all, 2))
print("                                      test where watermark agrees with label")
print("                             train    95%     50%     5%")
for name, w, cols in (("uses both features", w_all, slice(0, 2)), ("real signal only", w_real, slice(0, 1))):
    row = [acc(w, Xtr[:, cols], ytr)]
    for agree in (0.95, 0.50, 0.05):
        Xte, yte = make(20000, agree)
        row.append(acc(w, Xte[:, cols], yte))
    print(f"   {name:<22} " + "  ".join(f"{a:6.3f}" for a in row))

# Detecting the shift without labels: train a classifier to tell training inputs from deployment inputs.
# If it does better than chance, the input distribution has changed (a "classifier two-sample test").
Xdep, _ = make(5000, 0.05)
Xmix = np.vstack([Xtr, Xdep]); d = np.r_[np.zeros(5000), np.ones(5000)]
idx = rng.permutation(10000); tr, te = idx[:7000], idx[7000:]
print("\ndomain classifier (train vs deployment inputs); held-out accuracy 0.5 means no detectable shift")
w_d = train_logistic(Xmix[tr], d[tr])
print(f"   linear in (real, watermark):             {acc(w_d, Xmix[te], d[te]):.3f}")
# Each feature alone has the same distribution before and after; only their relation changed.
# Give the detector the product feature and it sees the shift clearly.
Xp = np.column_stack([Xmix, Xmix[:, 0] * (Xmix[:, 1] - 0.5)])
w_p = train_logistic(Xp[tr], d[tr])
print(f"   with the product real * (watermark - 0.5): {acc(w_p, Xp[te], d[te]):.3f}")
