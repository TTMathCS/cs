"""Chapter 22: a reproducible pipeline, a leak that fools cross-validation,
and distribution shift: detecting it, and correcting covariate and label shift."""
import hashlib

import numpy as np


def sigmoid(z):
    return 1.0 / (1.0 + np.exp(-np.clip(z, -30, 30)))


def fit_logreg(X, y, w_sample=None, lam=1e-3, steps=300):
    """Logistic regression (labels 0/1) by Newton's method, optional sample weights."""
    n, d = X.shape
    Xb = np.hstack([X, np.ones((n, 1))])
    s = np.ones(n) if w_sample is None else w_sample
    w = np.zeros(d + 1)
    for _ in range(steps):
        p = sigmoid(Xb @ w)
        g = Xb.T @ (s * (p - y)) / n + lam * w
        H = (Xb * (s * p * (1 - p))[:, None]).T @ Xb / n + lam * np.eye(d + 1)
        step = np.linalg.solve(H, g)
        w -= step
        if np.abs(step).max() < 1e-10:
            break
    return w


def predict_proba(w, X):
    return sigmoid(X @ w[:-1] + w[-1])


def auc(scores, labels):
    """Probability that a random positive outranks a random negative (ties count 1/2)."""
    order = np.argsort(scores)
    ranks = np.empty(len(scores)); ranks[order] = np.arange(1, len(scores) + 1)
    for v in np.unique(scores):                       # average ranks of ties
        tie = scores == v
        if tie.sum() > 1: ranks[tie] = ranks[tie].mean()
    npos = labels.sum(); nneg = len(labels) - npos
    return (ranks[labels == 1].sum() - npos * (npos + 1) / 2) / (npos * nneg)


def fingerprint(*arrays):
    h = hashlib.sha256()
    for a in arrays:
        h.update(np.ascontiguousarray(a).tobytes())
    return h.hexdigest()[:16]


class Pipeline:
    """Standardise, then logistic regression. fit() learns the scaler from the
    training rows only, and the whole thing is a pure function of (data, seed)."""
    def fit(self, X, y):
        self.mu, self.sd = X.mean(axis=0), X.std(axis=0) + 1e-12
        self.w = fit_logreg((X - self.mu) / self.sd, y)
        return self
    def predict_proba(self, X):
        return predict_proba(self.w, (X - self.mu) / self.sd)


def make_data(seed, n=500):
    r = np.random.default_rng(seed)
    X = r.normal(size=(n, 3))
    y = (r.random(n) < sigmoid(2 * X[:, 0] - X[:, 1])).astype(float)
    return X, y

# ------------------------------------------------------- 1. reproducibility
print("1. reproducibility: same data + same seed -> same model, bit for bit")
for seed in [0, 0, 1]:
    X, y = make_data(seed)
    model = Pipeline().fit(X, y)
    print(f"   seed {seed}: data {fingerprint(X, y)}  model {fingerprint(model.w)}")

# ------------------------------------------- 2. a leak that fools cross-validation
rng = np.random.default_rng(22)
n, p, k = 100, 2000, 20
X = rng.normal(size=(n, p))
y = rng.integers(0, 2, size=n).astype(float)          # labels are pure noise
folds = np.arange(n) % 5

def top_features(X, y, k):
    c = np.abs((X - X.mean(0)).T @ (y - y.mean()))
    return np.argsort(c)[-k:]

def cv_accuracy(select_inside):
    acc = []
    chosen_all = top_features(X, y, k)
    for f in range(5):
        tr, te = folds != f, folds == f
        cols = top_features(X[tr], y[tr], k) if select_inside else chosen_all
        model = Pipeline().fit(X[tr][:, cols], y[tr])
        acc.append(np.mean((model.predict_proba(X[te][:, cols]) > 0.5) == y[te]))
    return np.mean(acc)

print(f"\n2. {p} noise features, random labels, n = {n}; keep the {k} most correlated features")
print(f"   selection on ALL data, then 5-fold CV:   accuracy {cv_accuracy(False):.3f}   (a leak)")
print(f"   selection inside each training fold:     accuracy {cv_accuracy(True):.3f}   (honest)")

# ------------------------------------------------------- 3. covariate shift
def f_true(x):
    return np.sin(1.5 * x)

r = np.random.default_rng(5)
x_tr = r.normal(0.0, 1.0, 400); y_tr = f_true(x_tr) + 0.1 * r.normal(size=400)
x_te = r.normal(1.5, 0.6, 400); y_te = f_true(x_te) + 0.1 * r.normal(size=400)

def ks_statistic(a, b):
    """Largest gap between the two empirical CDFs."""
    grid = np.sort(np.concatenate([a, b]))
    Fa = np.searchsorted(np.sort(a), grid, side="right") / len(a)
    Fb = np.searchsorted(np.sort(b), grid, side="right") / len(b)
    return np.abs(Fa - Fb).max()

def permutation_p(a, b, stat, reps=500, seed=0):
    r = np.random.default_rng(seed)
    obs, pooled, hits = stat(a, b), np.concatenate([a, b]), 0
    for _ in range(reps):
        r.shuffle(pooled)
        hits += stat(pooled[:len(a)], pooled[len(a):]) >= obs
    return obs, (hits + 1) / (reps + 1)

print("\n3. covariate shift: train x ~ N(0, 1), deployment x ~ N(1.5, 0.6^2), same rule y = sin(1.5 x) + noise")
D, pval = permutation_p(x_tr, x_te, ks_statistic)
print(f"   Kolmogorov-Smirnov statistic {D:.3f}, permutation p-value {pval:.4f}")
D0, pval0 = permutation_p(x_tr[:200], x_tr[200:], ks_statistic)
print(f"   (two halves of the training set: statistic {D0:.3f}, p-value {pval0:.4f})")
# domain classifier: can a model tell training rows from deployment rows?
Z = np.concatenate([x_tr, x_te])[:, None]; Z = np.hstack([Z, Z ** 2])
dom = np.concatenate([np.zeros(400), np.ones(400)])
half = np.arange(800) % 2 == 0
wd = fit_logreg(Z[half], dom[half])
print(f"   domain classifier AUC on held-out rows: {auc(predict_proba(wd, Z[~half]), dom[~half]):.3f}"
      "  (0.5 = no shift)")
# importance weights w(x) = p_te(x) / p_tr(x) = odds from the domain classifier
Ztr = np.hstack([x_tr[:, None], x_tr[:, None] ** 2])
wd_all = fit_logreg(Z, dom)
pt = predict_proba(wd_all, Ztr)
iw = pt / (1 - pt); iw /= iw.mean()
def poly(x, deg=3):
    return np.vstack([x ** j for j in range(deg + 1)]).T
def wls(x, y, s):
    A = poly(x) * np.sqrt(s)[:, None]
    return np.linalg.lstsq(A, y * np.sqrt(s), rcond=None)[0]
for name, s in [("ordinary least squares", np.ones(400)), ("importance-weighted   ", iw)]:
    c = wls(x_tr, y_tr, s)
    print(f"   cubic fit, {name}: train MSE {np.mean((poly(x_tr) @ c - y_tr) ** 2):.4f}"
          f"   deployment MSE {np.mean((poly(x_te) @ c - y_te) ** 2):.4f}")
print(f"   effective sample size of the weights: {iw.sum() ** 2 / (iw ** 2).sum():.0f} of 400")

# --------------------------------------------------------- 4. label shift
# Class-conditional x | y fixed; the share of positives drops from 0.5 to 0.1.
def sample(n, prior, r):
    y = (r.random(n) < prior).astype(float)
    x = r.normal(loc=np.where(y == 1, 1.0, -1.0), scale=1.0)
    return x[:, None], y
r = np.random.default_rng(9)
Xa, ya = sample(4000, 0.5, r)          # training
Xv, yv = sample(4000, 0.5, r)          # validation, same distribution
Xd, yd = sample(4000, 0.1, r)          # deployment, unlabeled in real life
w = fit_logreg(Xa, ya)
pv = predict_proba(w, Xv) > 0.5
tpr, fpr = pv[yv == 1].mean(), pv[yv == 0].mean()
pos_rate = (predict_proba(w, Xd) > 0.5).mean()
prior_hat = (pos_rate - fpr) / (tpr - fpr)
print("\n4. label shift: training prior 0.5, deployment prior 0.1")
print(f"   validation TPR {tpr:.3f}, FPR {fpr:.3f}; deployment predicted-positive rate {pos_rate:.3f}")
print(f"   estimated deployment prior (rate - FPR) / (TPR - FPR) = {prior_hat:.3f}")
p_old = predict_proba(w, Xd)
odds = p_old / (1 - p_old) * (prior_hat / (1 - prior_hat)) / (0.5 / 0.5)
p_new = odds / (1 + odds)
for name, pr in [("unadjusted", p_old), ("prior-adjusted", p_new)]:
    acc = np.mean((pr > 0.5) == yd)
    ll = -np.mean(yd * np.log(pr) + (1 - yd) * np.log(1 - pr))
    print(f"   {name:15s} accuracy {acc:.3f}   log loss {ll:.3f}   mean predicted P(y=1) {pr.mean():.3f}")
