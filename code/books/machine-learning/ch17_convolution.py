"""Chapter 17: convolution from scratch. Filters and edges, stride and padding,
pooling, receptive fields, and translation equivariance, checked numerically."""
import numpy as np


def conv2d(x, w, stride=1, pad=0):
    """Cross-correlation of a 2-D image x with a 2-D filter w (what deep-learning
    libraries call 'convolution'). out[i, j] = sum_{a,b} w[a, b] x[i*s + a, j*s + b]."""
    if pad:
        x = np.pad(x, pad)
    k = w.shape[0]
    H = (x.shape[0] - k) // stride + 1
    W = (x.shape[1] - k) // stride + 1
    out = np.zeros((H, W))
    for i in range(H):
        for j in range(W):
            patch = x[i * stride:i * stride + k, j * stride:j * stride + k]
            out[i, j] = np.sum(patch * w)
    return out


def pool2d(x, size=2, mode="max"):
    H, W = x.shape[0] // size, x.shape[1] // size
    blocks = x[:H * size, :W * size].reshape(H, size, W, size)
    return blocks.max(axis=(1, 3)) if mode == "max" else blocks.mean(axis=(1, 3))


def show(name, a):
    print(name)
    for row in a:
        print("   " + " ".join(f"{v:4.0f}" for v in row))


# ----------------------------------------------------- 1. why not fully connected
print("1. parameters of one layer on a 224 x 224 colour image")
inputs = 224 * 224 * 3
print(f"   fully connected to 1000 units: {inputs * 1000 + 1000:,} weights")
print(f"   64 filters of 3 x 3 x 3      : {64 * 3 * 3 * 3 + 64:,} weights")

# ------------------------------------------------------ 2. a filter finds edges
img = np.array([[0, 0, 0, 9, 9, 9]] * 6, dtype=float)      # dark left, bright right
vert = np.array([[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]], float)  # Sobel, x direction
horz = vert.T                                               # Sobel, y direction
print()
show("2. image (6 x 6)", img)
show("   Sobel-x response (4 x 4)", conv2d(img, vert))
show("   Sobel-y response (4 x 4)", conv2d(img, horz))

# ------------------------------------------------ 3. stride, padding, sizes
print()
print("3. output size floor((n + 2p - k) / s) + 1, checked")
for n, k, s, p in [(6, 3, 1, 0), (6, 3, 1, 1), (7, 3, 2, 0), (7, 3, 2, 1), (224, 7, 2, 3)]:
    out = conv2d(np.ones((n, n)), np.ones((k, k)), stride=s, pad=p).shape[0]
    print(f"   n={n:3d} k={k} s={s} p={p}: formula {(n + 2 * p - k) // s + 1:3d}, code {out:3d}")

# ------------------------------------------------------------- 4. pooling
x = np.array([[1, 3, 2, 0], [4, 6, 1, 1], [0, 2, 5, 7], [1, 1, 8, 3]], float)
print()
show("4. a 4 x 4 feature map", x)
show("   2 x 2 max pooling", pool2d(x, 2, "max"))
print("   2 x 2 average pooling")
for row in pool2d(x, 2, "mean"):
    print("   " + " ".join(f"{v:4.2f}" for v in row))

# -------------------------------------------------------- 5. receptive fields
print()
print("5. receptive field of one unit after a stack of layers (kernel k, stride s)")
layers = [("conv3", 3, 1), ("conv3", 3, 1), ("pool2", 2, 2), ("conv3", 3, 1),
          ("conv3", 3, 1), ("pool2", 2, 2), ("conv3", 3, 1)]
r, jump = 1, 1
for name, k, s in layers:
    r += (k - 1) * jump        # each new layer widens the field by (k-1) input steps
    jump *= s                  # distance in input pixels between neighbouring units
    print(f"   after {name}: receptive field {r:2d} x {r:2d}, jump {jump}")
# check the first two rows by brute force: which inputs change one output?
probe = np.zeros((9, 9))
probe[4, 4] = 1.0
two = conv2d(conv2d(probe, np.ones((3, 3))), np.ones((3, 3)))
print(f"   brute force: one input pixel reaches {np.count_nonzero(two)} outputs "
      f"after two 3x3 convs (a 5 x 5 block)")

# ------------------------------------------------------ 6. equivariance
rng = np.random.default_rng(0)
x = np.zeros((12, 12))
x[3:6, 2:5] = rng.uniform(1, 2, (3, 3))                   # a small blob
w = rng.normal(size=(3, 3))
shift = lambda a, d: np.roll(a, d, axis=1)                # move right by d pixels
lhs = conv2d(shift(x, 3), w)                              # shift then convolve
rhs = shift(conv2d(x, w), 3)                              # convolve then shift
print()
print("6. translation equivariance: conv(shift(x)) == shift(conv(x))?",
      np.allclose(lhs, rhs))
feat = lambda a: pool2d(np.maximum(conv2d(a, np.ones((3, 3)) / 9), 0), 2)
p0 = feat(x)
for d in (1, 2, 3):
    pd = feat(shift(x, d))
    print(f"   shift {d}: pooled max {p0.max():.3f} -> {pd.max():.3f}; pooled map unchanged? "
          f"{str(np.allclose(p0, pd)):5s} equals pooled map moved {d // 2}? "
          f"{np.allclose(shift(p0, d // 2), pd)}")
