"""Chapter 9.2: the curse of dimensionality, measured. Distances concentrate,
neighbourhoods stop being local, and k-NN accuracy collapses when useless dimensions are added."""
import numpy as np

rng = np.random.default_rng(1)

print("1. Distance concentration: 1000 uniform points in the unit cube [0,1]^d,")
print("   distances from one random query point")
print("     d   nearest  farthest  (far-near)/near   mean    sd/mean")
for d in [1, 2, 10, 100, 1000]:
    X = rng.uniform(0, 1, (1000, d))
    q = rng.uniform(0, 1, d)
    dist = np.sqrt(((X - q) ** 2).sum(axis=1))
    lo, hi = dist.min(), dist.max()
    print(f"{d:6d}  {lo:7.3f}  {hi:8.3f}  {((hi - lo) / lo):14.3f}  {dist.mean():7.3f}  {dist.std() / dist.mean():8.3f}")

print("\n2. Edge of the sub-cube that holds a fraction p of uniform data: p ** (1/d)")
print("     d    p=0.01   p=0.1")
for d in [1, 2, 3, 10, 100]:
    print(f"{d:6d}   {0.01 ** (1 / d):6.3f}   {0.1 ** (1 / d):6.3f}")

print("\n3. Fraction of the unit ball's volume within 0.05 of its surface: 1 - 0.95**d")
for d in [2, 10, 50, 100]:
    print(f"   d = {d:3d}: {1 - 0.95 ** d:.3f}")


def knn_acc(Xtr, ytr, Xte, yte, k=5):
    sq = (Xte ** 2).sum(1)[:, None] + (Xtr ** 2).sum(1)[None, :] - 2 * Xte @ Xtr.T
    idx = np.argsort(sq, axis=1)[:, :k]
    pred = (ytr[idx].mean(1) > 0.5).astype(int)
    return (pred == yte).mean()


print("\n4. k-NN (k=5) where only the first 2 features matter (class = which side of a circle);")
print("   the other d-2 features are uniform noise. 500 training points, 500 test points.")
print("     d   test accuracy")
n = 1000
for d in [2, 5, 10, 20, 50, 100, 500]:
    X = rng.uniform(-1, 1, (n, d))
    y = ((X[:, 0] ** 2 + X[:, 1] ** 2) < 0.5).astype(int)
    print(f"{d:6d}   {knn_acc(X[:500], y[:500], X[500:], y[500:]):.3f}")
base = ((rng.uniform(-1, 1, (200000, 2)) ** 2).sum(1) < 0.5).mean()
print(f"   (always guessing the larger class scores about {max(base, 1 - base):.3f})")
