"""Chapter 7: accuracy on imbalanced data, confusion matrices, precision,
recall, F1, ROC and AUC, precision-recall, regression metrics, calibration
and the Brier score, all from scratch with NumPy."""
import numpy as np

def sigmoid(z):
    return 0.5 * (1 + np.tanh(0.5 * z))

def fit_logistic(X, y, steps=300):
    """Newton's method (Chapter 6) with a tiny ridge term for safety."""
    w = np.zeros(X.shape[1])
    for _ in range(steps):
        p = sigmoid(X @ w)
        g = X.T @ (p - y) / len(y) + 1e-6 * w
        H = X.T @ (X * (p * (1 - p))[:, None]) / len(y) + 1e-6 * np.eye(len(w))
        step = np.linalg.solve(H, g)
        w -= step
        if np.abs(step).max() < 1e-10:
            break
    return w

def confusion(y, yhat):
    tp = int(np.sum((yhat == 1) & (y == 1))); fp = int(np.sum((yhat == 1) & (y == 0)))
    fn = int(np.sum((yhat == 0) & (y == 1))); tn = int(np.sum((yhat == 0) & (y == 0)))
    return tp, fp, fn, tn

def report(name, y, yhat):
    tp, fp, fn, tn = confusion(y, yhat)
    acc = (tp + tn) / len(y)
    prec = tp / (tp + fp) if tp + fp else float("nan")
    rec = tp / (tp + fn)
    f1 = 2 * prec * rec / (prec + rec) if tp else 0.0
    print(f"   {name:24s} TP {tp:3d} FP {fp:3d} FN {fn:3d} TN {tn:4d}  "
          f"acc {acc:.3f} prec {prec:.3f} rec {rec:.3f} F1 {f1:.3f}")

# A rare-event problem: about 5 percent positives, 4 features.
rng = np.random.default_rng(0)
def make(n):
    F = rng.normal(size=(n, 4))
    z = -3.6 + F @ np.array([1.5, -1.0, 0.8, 0.0])
    return np.c_[np.ones(n), F], (rng.uniform(size=n) < sigmoid(z)).astype(int)
Xtr, ytr = make(4000)
Xte, yte = make(2000)
w = fit_logistic(Xtr, ytr)
s = sigmoid(Xte @ w)                           # predicted probabilities on the test set
print(f"1. test set: {len(yte)} examples, {yte.sum()} positive ({yte.mean():.1%})")
report("always 'negative'", yte, np.zeros_like(yte))
report("logistic, threshold 0.5", yte, (s >= 0.5).astype(int))
report("logistic, threshold 0.2", yte, (s >= 0.2).astype(int))
report("logistic, threshold 0.05", yte, (s >= 0.05).astype(int))

# ----------------------------------------------------- 2. ROC and AUC by hand
def roc_points(y, score):
    """Sweep the threshold down through the sorted scores (no ties assumed)."""
    order = np.argsort(-score)
    y = y[order]
    P, N = y.sum(), len(y) - y.sum()
    tpr = np.r_[0, np.cumsum(y) / P]
    fpr = np.r_[0, np.cumsum(1 - y) / N]
    return fpr, tpr

def auc_trapezoid(fpr, tpr):
    return float(np.sum((fpr[1:] - fpr[:-1]) * (tpr[1:] + tpr[:-1]) / 2))

def auc_pairs(y, score):
    """Fraction of (positive, negative) pairs ranked correctly; ties count 1/2."""
    pos, neg = score[y == 1], score[y == 0]
    d = pos[:, None] - neg[None, :]
    return float(np.mean((d > 0) + 0.5 * (d == 0)))

ys = np.array([1, 1, 0, 1, 0, 1, 0, 0, 1, 0])
ss = np.array([0.95, 0.85, 0.80, 0.70, 0.55, 0.45, 0.40, 0.30, 0.20, 0.10])
fpr, tpr = roc_points(ys, ss)
print("\n2. ten scored examples, threshold swept from high to low")
print("   threshold  label  TPR   FPR")
for t, lab, a, b in zip(ss, ys, tpr[1:], fpr[1:]):
    print(f"   {t:.2f}       {lab}      {a:.1f}   {b:.1f}")
print(f"   AUC by trapezoids {auc_trapezoid(fpr, tpr):.3f}, by counting pairs {auc_pairs(ys, ss):.3f}")
fpr, tpr = roc_points(yte, s)
print(f"   logistic model on the test set: AUC {auc_trapezoid(fpr, tpr):.4f} "
      f"(pairs {auc_pairs(yte, s):.4f})")

# --------------------------------------------- 3. precision-recall curve
order = np.argsort(-s)
yo = yte[order]
tp_c = np.cumsum(yo)
prec_c = tp_c / np.arange(1, len(yo) + 1)
rec_c = tp_c / yo.sum()
ap = float(np.sum(prec_c[yo == 1]) / yo.sum())       # average precision
print("\n3. precision-recall on the test set")
for r in (0.2, 0.4, 0.6, 0.8, 0.9):
    i = np.argmax(rec_c >= r)
    print(f"   recall {rec_c[i]:.2f}: precision {prec_c[i]:.3f} (top {i + 1} scores flagged)")
print(f"   average precision {ap:.4f}; a random ranking would give about {yte.mean():.4f}")

# ------------------------------------------------- 4. regression metrics
x = rng.uniform(0, 10, size=200)
yr = 2 + 0.5 * x + rng.normal(size=200)
yr[:5] += 15                                          # five gross outliers
def metrics(y, pred):
    e = y - pred
    mse = np.mean(e ** 2)
    return mse, np.sqrt(mse), np.mean(np.abs(e)), 1 - mse / np.var(y)
print("\n4. regression metrics (200 points, five of them outliers)")
print("   predictor                MSE     RMSE    MAE     R^2")
for name, pred in (("true line 2 + 0.5x", 2 + 0.5 * x),
                   ("constant mean", np.full(200, yr.mean())),
                   ("constant median", np.full(200, np.median(yr))),
                   ("line shifted by +3", 5 + 0.5 * x)):
    print("   {:22s} {:7.3f} {:7.3f} {:7.3f} {:7.3f}".format(name, *metrics(yr, pred)))

# --------------------------------------------- 5. calibration and Brier
def reliability(y, p, bins=5):
    edges = np.linspace(0, 1, bins + 1)
    rows, ece = [], 0.0
    for lo, hi in zip(edges[:-1], edges[1:]):
        m = (p >= lo) & (p < hi) if hi < 1 else (p >= lo)
        if m.sum():
            rows.append((lo, hi, int(m.sum()), p[m].mean(), y[m].mean()))
            ece += m.sum() / len(y) * abs(p[m].mean() - y[m].mean())
    return rows, ece

Xc, yc = make(20000)                                  # a big set to see calibration clearly
pc = sigmoid(Xc @ w)
over = sigmoid(3 * (Xc @ w) + 6)                      # same ranking, badly overconfident
print("\n5. calibration on 20000 new examples")
for name, p in (("logistic", pc), ("overconfident", over)):
    rows, ece = reliability(yc, p)
    brier = np.mean((p - yc) ** 2)
    fpr, tpr = roc_points(yc, p)
    print(f"   {name}: Brier {brier:.4f}  ECE {ece:.4f}  AUC {auc_trapezoid(fpr, tpr):.4f}")
    for lo, hi, cnt, mp, fr in rows:
        print(f"      bin [{lo:.1f},{hi:.1f})  n {cnt:5d}  mean predicted {mp:.3f}  observed {fr:.3f}")
print(f"   always predicting the base rate: Brier {np.mean((yc.mean() - yc) ** 2):.4f}")

# Platt scaling: fit a 1-D logistic model on the overconfident scores
# (using the training set, never the test set), then re-evaluate.
z_tr = np.log(sigmoid(3 * (Xtr @ w) + 6)) - np.log1p(-sigmoid(3 * (Xtr @ w) + 6) + 1e-15)
ab = fit_logistic(np.c_[np.ones(len(ytr)), z_tr], ytr)
z_c = np.log(over) - np.log1p(-over + 1e-15)
fixed = sigmoid(ab[0] + ab[1] * z_c)
rows, ece = reliability(yc, fixed)
print(f"   overconfident after Platt scaling (a={ab[0]:.2f}, b={ab[1]:.3f}): "
      f"Brier {np.mean((fixed - yc) ** 2):.4f}  ECE {ece:.4f}")
