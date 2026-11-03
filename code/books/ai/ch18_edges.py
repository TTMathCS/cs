# Chapter 18: seeing from scratch. Image gradients with Sobel filters, edges by thresholding,
# and Harris corners from the structure tensor, on a small synthetic image of a "rock".
import numpy as np

rng = np.random.default_rng(0)
H, W = 24, 24
img = np.full((H, W), 0.2)
img[7:17, 6:18] = 0.9                            # a bright rectangle: rows 7..16, columns 6..17
img += rng.normal(0, 0.03, img.shape)            # a little sensor noise


def correlate(a, k):
    """Slide kernel k over image a (no padding): out[i, j] = sum k * patch."""
    kh, kw = k.shape
    out = np.zeros((a.shape[0] - kh + 1, a.shape[1] - kw + 1))
    for di in range(kh):
        for dj in range(kw):
            out += k[di, dj] * a[di:di + out.shape[0], dj:dj + out.shape[1]]
    return out


SOBEL_X = np.array([[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]]) / 8.0   # smoothing (1 2 1) times derivative (-1 0 1)
SOBEL_Y = SOBEL_X.T
gx, gy = correlate(img, SOBEL_X), correlate(img, SOBEL_Y)       # each output pixel sits at input (i+1, j+1)
mag = np.hypot(gx, gy)

print("1. Sobel gradient at a few pixels (row, col in the original image)")
for (r, c) in [(12, 6), (12, 17), (7, 12), (12, 12), (3, 3)]:
    print(f"   ({r:2d},{c:2d}): gx {gx[r - 1, c - 1]:+.3f}  gy {gy[r - 1, c - 1]:+.3f}  magnitude {mag[r - 1, c - 1]:.3f}")

edges = mag > 0.5 * mag.max()
print(f"\n2. edge map, threshold half the largest magnitude ({0.5 * mag.max():.3f}); # = edge")
for row in edges[2:18]:
    print("   " + "".join("#" if e else "." for e in row))
print(f"   {edges.sum()} edge pixels")

# Harris: structure tensor M = sum over a window of [Ix^2, IxIy; IxIy, Iy^2]; R = det M - k (trace M)^2
box = np.ones((3, 3))
Sxx, Syy, Sxy = correlate(gx * gx, box), correlate(gy * gy, box), correlate(gx * gy, box)
R = Sxx * Syy - Sxy ** 2 - 0.05 * (Sxx + Syy) ** 2               # pixel (i, j) of R is image pixel (i+2, j+2)
peaks = []
for i in range(1, R.shape[0] - 1):
    for j in range(1, R.shape[1] - 1):
        if R[i, j] == R[i - 1:i + 2, j - 1:j + 2].max() and R[i, j] > 0.1 * R.max():
            peaks.append((R[i, j], i + 2, j + 2))
print("\n3. Harris corners (local maxima of R above 10% of the largest)")
for v, r, c in sorted(peaks, reverse=True):
    print(f"   corner at row {r:2d}, col {c:2d}   R = {v:.5f}")


def eig2(a, b, c):
    """Eigenvalues of the symmetric 2x2 matrix [[a, b], [b, c]]."""
    m, d = (a + c) / 2, np.sqrt(((a - c) / 2) ** 2 + b ** 2)
    return m + d, m - d


print("\n4. eigenvalues of the structure tensor: what kind of place is it?")
for name, (r, c) in [("flat background", (4, 4)), ("middle of left edge", (12, 6)), ("top-left corner", (7, 6))]:
    i, j = r - 2, c - 2
    l1, l2 = eig2(Sxx[i, j], Sxy[i, j], Syy[i, j])
    print(f"   {name:20s} lambda1 {l1:.4f}  lambda2 {l2:.4f}")
