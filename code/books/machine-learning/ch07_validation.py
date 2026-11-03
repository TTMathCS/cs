"""Chapter 7: k-fold and leave-one-out cross-validation, the wrong way to
cross-validate, nested cross-validation, confidence intervals, the bootstrap,
McNemar's test and multiple comparisons, from scratch with NumPy."""
import math
import numpy as np

rng = np.random.default_rng(0)

def knn_predict(Xtr, ytr, Xte, k):
    d = ((Xte[:, None, :] - Xtr[None, :, :]) ** 2).sum(-1)
    idx = np.argsort(d, axis=1)[:, :k]
    return (ytr[idx].mean(1) > 0.5).astype(int)    # majority vote (k odd)

def folds(n, k, r):
    return np.array_split(r.permutation(n), k)

def cv_accuracy(X, y, k_nn, n_folds, r):
    accs = []
    for f in folds(len(y), n_folds, r):
        tr = np.setdiff1d(np.arange(len(y)), f)
        accs.append(np.mean(knn_predict(X[tr], y[tr], X[f], k_nn) == y[f]))
    return np.mean(accs), np.std(accs)

# Two noisy overlapping classes in 2-D.
def make(n):
    y = rng.integers(0, 2, size=n)
    X = rng.normal(size=(n, 2)) + y[:, None] * np.array([1.2, 1.2])
    return X, y
X, y = make(200)
Xbig, ybig = make(5000)                            # stands in for "the future"

print("1. choosing k for k-NN: 5-fold CV on 200 points vs accuracy on 5000 new points")
print("   k    CV mean  fold sd   true accuracy")
for k_nn in (1, 3, 7, 15, 31, 61):
    m, sd = cv_accuracy(X, y, k_nn, 5, np.random.default_rng(1))
    true = np.mean(knn_predict(X, y, Xbig, k_nn) == ybig)
    print(f"   {k_nn:2d}   {m:.3f}    {sd:.3f}     {true:.3f}")

# ------------------------------- 2. leave-one-out for least squares, two ways
n = 30
A = np.c_[np.ones(n), rng.uniform(-1, 1, size=(n, 2))]
b = A @ np.array([1.0, 2.0, -1.0]) + rng.normal(size=n) * 0.3
brute = []
for i in range(n):
    keep = np.arange(n) != i
    wi = np.linalg.lstsq(A[keep], b[keep], rcond=None)[0]
    brute.append(b[i] - A[i] @ wi)
H = A @ np.linalg.solve(A.T @ A, A.T)              # the hat matrix
resid = b - H @ b
short = resid / (1 - np.diag(H))
print("\n2. leave-one-out residuals for least squares (30 points)")
print(f"   refit 30 times:   LOO MSE {np.mean(np.square(brute)):.6f}")
print(f"   one fit, e/(1-h): LOO MSE {np.mean(short ** 2):.6f}   "
      f"max difference {np.max(np.abs(np.array(brute) - short)):.1e}")
print(f"   training MSE {np.mean(resid ** 2):.6f} (optimistic)")

# ---------------------------------- 3. the wrong way to cross-validate
# 50 examples, 5000 features of pure noise, labels are coin flips.
# Any honest estimate of accuracy must be about 0.5.
n, p = 50, 5000
Xn = rng.normal(size=(n, p))
yn = np.repeat([0, 1], 25); rng.shuffle(yn)

def top_features(X, y, m):
    c = np.abs((X - X.mean(0)).T @ (y - y.mean()))
    return np.argsort(-c)[:m]

def centroid_predict(Xtr, ytr, Xte):
    m0, m1 = Xtr[ytr == 0].mean(0), Xtr[ytr == 1].mean(0)
    return (((Xte - m1) ** 2).sum(1) < ((Xte - m0) ** 2).sum(1)).astype(int)

def cv_select(select_inside, r):
    if not select_inside:
        cols = top_features(Xn, yn, 20)              # chosen using ALL labels: leak
    accs = []
    for f in folds(n, 5, r):
        tr = np.setdiff1d(np.arange(n), f)
        if select_inside:
            cols = top_features(Xn[tr], yn[tr], 20)  # chosen on the training fold only
        pred = centroid_predict(Xn[tr][:, cols], yn[tr], Xn[f][:, cols])
        accs.append(np.mean(pred == yn[f]))
    return np.mean(accs)
print("\n3. noise features, coin-flip labels: pick 20 best features, nearest centroid")
print(f"   selection before CV (wrong): CV accuracy {cv_select(False, np.random.default_rng(2)):.3f}")
print(f"   selection inside each fold:  CV accuracy {cv_select(True, np.random.default_rng(2)):.3f}")

# ----------------------------------------------------- 4. nested CV
# Random labels again, so the true accuracy of every k is 0.5.
Xr = rng.normal(size=(80, 2))
yr = rng.integers(0, 2, size=80)
grid = (1, 3, 5, 7, 9, 11, 15, 21, 31)
best_plain = []
nested = []
for rep in range(20):
    r = np.random.default_rng(100 + rep)
    scores = [cv_accuracy(Xr, yr, k, 5, np.random.default_rng(rep))[0] for k in grid]
    best_plain.append(max(scores))                  # report the best CV score: optimistic
    outer = []
    for f in folds(80, 5, r):                       # nested: choose k inside, score outside
        tr = np.setdiff1d(np.arange(80), f)
        inner = [cv_accuracy(Xr[tr], yr[tr], k, 4, np.random.default_rng(rep))[0] for k in grid]
        kb = grid[int(np.argmax(inner))]
        outer.append(np.mean(knn_predict(Xr[tr], yr[tr], Xr[f], kb) == yr[f]))
    nested.append(np.mean(outer))
print("\n4. random labels, k chosen from 9 values; average over 20 repetitions")
print(f"   best plain 5-fold CV score: {np.mean(best_plain):.3f}")
print(f"   nested CV estimate:         {np.mean(nested):.3f}   (truth 0.500)")

# ----------------------------------------- 5. intervals and the bootstrap
def wilson(k, n, z=1.96):
    ph = k / n
    centre = (ph + z * z / (2 * n)) / (1 + z * z / n)
    half = z * math.sqrt(ph * (1 - ph) / n + z * z / (4 * n * n)) / (1 + z * z / n)
    return centre - half, centre + half

print("\n5. 95% intervals for an accuracy")
for k, m in ((85, 100), (850, 1000), (99, 100)):
    ph = k / m
    se = math.sqrt(ph * (1 - ph) / m)
    lo, hi = wilson(k, m)
    print(f"   {k}/{m}: normal [{ph - 1.96 * se:.3f}, {ph + 1.96 * se:.3f}]   Wilson [{lo:.3f}, {hi:.3f}]")

# Two classifiers on the same 500 test examples (simulated correctness flags).
m = 500
truth_a, truth_b = 0.86, 0.82
u = rng.uniform(size=m)
correct_a = u < truth_a                              # shared u: errors are correlated
correct_b = np.where(rng.uniform(size=m) < 0.7, u < truth_b, rng.uniform(size=m) < truth_b)
acc_a, acc_b = correct_a.mean(), correct_b.mean()
boot = []
r = np.random.default_rng(7)
for _ in range(10000):
    i = r.integers(0, m, size=m)
    boot.append(correct_a[i].mean() - correct_b[i].mean())
lo, hi = np.percentile(boot, [2.5, 97.5])
n01 = int(np.sum(correct_a & ~correct_b)); n10 = int(np.sum(~correct_a & correct_b))
chi2 = (abs(n01 - n10) - 1) ** 2 / (n01 + n10)
pval = math.erfc(math.sqrt(chi2 / 2))                # chi-square, 1 degree of freedom
print("\n6. comparing two classifiers on the same 500 examples")
print(f"   accuracy A {acc_a:.3f}, B {acc_b:.3f}, difference {acc_a - acc_b:+.3f}")
print(f"   paired bootstrap 95% interval for the difference: [{lo:+.3f}, {hi:+.3f}]")
print(f"   McNemar: A right & B wrong {n01}, A wrong & B right {n10}, "
      f"chi2 {chi2:.2f}, p = {pval:.4f}")

# ------------------------------------------------ 7. multiple comparisons
m, models = 200, 100
yt = rng.integers(0, 2, size=m)
accs = np.array([np.mean(rng.integers(0, 2, size=m) == yt) for _ in range(models)])
best = accs.max()
k = int(round(best * m))
# one-sided p-value of the best model as if it had been the only one tried
p_single = sum(math.comb(m, j) for j in range(k, m + 1)) / 2 ** m
print(f"\n7. {models} coin-flip 'models' scored on the same {m} test labels")
print(f"   best accuracy {best:.3f}; its p-value if it were the only model: {p_single:.4f}")
print(f"   Bonferroni-adjusted p-value: {min(1, p_single * models):.3f}")
print(f"   models with p < 0.05 before adjustment: "
      f"{sum(sum(math.comb(m, j) for j in range(int(round(a * m)), m + 1)) / 2 ** m < 0.05 for a in accs)}")
