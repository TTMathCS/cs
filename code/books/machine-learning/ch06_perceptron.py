"""Chapter 6: why least squares is a poor classifier, and the perceptron with
a check of Novikoff's mistake bound, from scratch with NumPy."""
import numpy as np

# ------------------------------------- 1. least squares as a classifier
# One feature; class 1 for x >= 5. Fit a line to the 0/1 labels and classify
# by "prediction >= 0.5". Then add far-away, obviously class-1 points.
def ls_threshold(x, y):
    X = np.c_[np.ones_like(x), x]
    b0, b1 = np.linalg.lstsq(X, y, rcond=None)[0]
    return (0.5 - b0) / b1            # where the fitted line crosses 0.5

x = np.arange(10, dtype=float)       # 0..9
y = (x >= 5).astype(float)
t1 = ls_threshold(x, y)
x2 = np.r_[x, 30, 35, 40]
y2 = np.r_[y, 1, 1, 1]
t2 = ls_threshold(x2, y2)
print("1. least squares on 0/1 labels, classify by fitted value >= 0.5")
print(f"   10 points 0..9:             threshold {t1:.3f}, errors {np.sum((x >= t1) != (y == 1))}")
print(f"   plus x = 30, 35, 40 (class 1): threshold {t2:.3f}, errors {np.sum((x2 >= t2) != (y2 == 1))}")

# ------------------------------------------------- 2. a perceptron trace
def perceptron(X, y, max_epochs=1000, trace=False):
    """X has a leading column of ones; y in {-1, +1}. Returns w and mistakes."""
    w = np.zeros(X.shape[1])
    mistakes = 0
    for epoch in range(max_epochs):
        clean = True
        for xi, yi in zip(X, y):
            if yi * (w @ xi) <= 0:                 # wrong side (or on the line)
                w = w + yi * xi
                mistakes += 1
                clean = False
                if trace:
                    print(f"   epoch {epoch + 1}  x={xi[1:]}  y={yi:+d}  ->  w = {w}")
        if clean:
            return w, mistakes, epoch + 1
    return w, mistakes, max_epochs

Xs = np.array([[1, -1, 0], [1, -1, -3], [1, -3, -3], [1, -3, -2], [1, 3, -2]], float)
ys = np.array([-1, 1, -1, -1, 1])
print("\n2. perceptron on five points (first coordinate is the bias input 1)")
w, m, ep = perceptron(Xs, ys, trace=True)
print(f"   converged after {m} mistakes, {ep} epochs; w = {w}")
print(f"   margins y * w.x = {ys * (Xs @ w)}")

# ----------------------------------- 3. Novikoff's bound on random data
rng = np.random.default_rng(0)
print("\n3. mistakes against Novikoff's bound (R / gamma)^2")
print("   gamma_min   n     mistakes   bound")
u = np.array([0.2, 1.0, -1.0]); u /= np.linalg.norm(u)   # a unit separator
for gap in (0.5, 0.2, 0.05):
    P = rng.uniform(-3, 3, size=(4000, 2))
    X = np.c_[np.ones(len(P)), P]
    s = X @ u
    keep = np.abs(s) >= gap                       # throw away points near the line
    X, y = X[keep][:300], np.sign(s[keep][:300]).astype(int)
    gamma = np.min(y * (X @ u))
    R = np.max(np.linalg.norm(X, axis=1))
    w, m, ep = perceptron(X, y)
    print(f"   {gamma:.4f}    {len(y)}     {m:5d}    {(R / gamma) ** 2:9.0f}")

# --------------------------------- 4. non-separable data: no convergence
X = np.c_[np.ones(200), rng.normal(size=(200, 2))]
y = np.where(X[:, 1] + X[:, 2] + rng.normal(size=200) * 0.8 > 0, 1, -1)
w, m, ep = perceptron(X, y, max_epochs=50)
acc = np.mean(np.sign(X @ w) == y)
print(f"\n4. overlapping classes: {m} mistakes in {ep} epochs, still not clean; "
      f"final training accuracy {acc:.3f}")
