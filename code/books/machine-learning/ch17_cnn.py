"""Chapter 17: a convolutional layer with its backward pass (checked against
finite differences), then a tiny CNN trained from scratch on synthetic bar
images, compared with a fully connected net on positions it never saw, and a
transfer-learning test. NumPy only."""
import numpy as np

rng = np.random.default_rng(17)


# ------------------------------------------------------------ the conv layer
def im2col(x, k, pad):
    """x: (N, C, H, W) -> columns (N, C*k*k, H*W) for a stride-1 'same' conv."""
    N, C, H, W = x.shape
    xp = np.pad(x, ((0, 0), (0, 0), (pad, pad), (pad, pad)))
    cols = np.empty((N, C, k, k, H, W))
    for a in range(k):
        for b in range(k):
            cols[:, :, a, b] = xp[:, :, a:a + H, b:b + W]
    return cols.reshape(N, C * k * k, H * W)


def col2im(cols, shape, k, pad):
    """The adjoint of im2col: scatter-add every column entry back to its pixel."""
    N, C, H, W = shape
    cols = cols.reshape(N, C, k, k, H, W)
    xp = np.zeros((N, C, H + 2 * pad, W + 2 * pad))
    for a in range(k):
        for b in range(k):
            xp[:, :, a:a + H, b:b + W] += cols[:, :, a, b]
    return xp[:, :, pad:pad + H, pad:pad + W]


def conv_forward(x, w, b):
    F, C, k, _ = w.shape
    cols = im2col(x, k, k // 2)                      # (N, Ck^2, HW)
    out = np.einsum("fc,ncp->nfp", w.reshape(F, -1), cols) + b[None, :, None]
    return out.reshape(x.shape[0], F, *x.shape[2:]), cols


def conv_backward(dout, x, w, cols):
    F, C, k, _ = w.shape
    d = dout.reshape(dout.shape[0], F, -1)           # (N, F, HW)
    dw = np.einsum("nfp,ncp->fc", d, cols).reshape(w.shape)
    db = d.sum(axis=(0, 2))
    dcols = np.einsum("fc,nfp->ncp", w.reshape(F, -1), d)
    dx = col2im(dcols, x.shape, k, k // 2)
    return dx, dw, db


# ---------------------------------------------------- 1. gradient check
print("1. gradient check of the conv layer (loss = sum(out * R) for a fixed random R)")
x = rng.normal(size=(2, 3, 5, 5))
w = rng.normal(size=(4, 3, 3, 3))
b = rng.normal(size=4)
R = rng.normal(size=(2, 4, 5, 5))
out, cols = conv_forward(x, w, b)
dx, dw, db = conv_backward(R, x, w, cols)
def numeric(arr, f, h=1e-5):
    g = np.zeros_like(arr)
    for idx in np.ndindex(arr.shape):
        old = arr[idx]
        arr[idx] = old + h; fp = f()
        arr[idx] = old - h; fm = f()
        arr[idx] = old
        g[idx] = (fp - fm) / (2 * h)
    return g
loss = lambda: np.sum(conv_forward(x, w, b)[0] * R)
for name, arr, g in [("dx", x, dx), ("dw", w, dw), ("db", b, db)]:
    num = numeric(arr, loss)
    print(f"   {name}: max relative error {np.abs(num - g).max() / np.abs(num).max():.1e}")


# ------------------------------------------------------------- the data
S = 12                                               # images are 12 x 12


def bar_image(kind, r, c):
    img = np.zeros((S, S))
    for t in range(5):
        if kind == 0:   img[r, c + t] = 1            # horizontal
        elif kind == 1: img[r + t, c] = 1            # vertical
        elif kind == 2: img[r + t, c + t] = 1        # diagonal
        else:           img[r + t, c + 4 - t] = 1    # anti-diagonal
    return img


def make_set(n, kinds, cols_allowed, noise=0.25):
    X, y = [], []
    for _ in range(n):
        k = rng.choice(kinds)
        r = rng.integers(0, S - 4)
        c = rng.choice(cols_allowed)
        X.append(bar_image(k, r, c) + noise * rng.normal(size=(S, S)))
        y.append(kinds.index(k))
    return np.array(X)[:, None], np.array(y)


left, right = list(range(0, 4)), list(range(4, 8))  # bar starts in columns 0-3 or 4-7
Xtr, ytr = make_set(600, [0, 1, 2], left)
Xte_same, yte_same = make_set(300, [0, 1, 2], left)
Xte_moved, yte_moved = make_set(300, [0, 1, 2], right)


# --------------------------------------------------------------- the models
def softmax_xent(z, y):
    z = z - z.max(axis=1, keepdims=True)
    p = np.exp(z); p /= p.sum(axis=1, keepdims=True)
    loss = -np.log(p[np.arange(len(y)), y] + 1e-12).mean()
    g = p.copy(); g[np.arange(len(y)), y] -= 1
    return loss, g / len(y)


class TinyCNN:
    """conv 3x3 (F filters) -> ReLU -> global max pool -> linear -> softmax."""
    def __init__(self, F=8, classes=3):
        self.w = rng.normal(size=(F, 1, 3, 3)) * np.sqrt(2 / 9)   # He init
        self.b = np.zeros(F)
        self.V = rng.normal(size=(F, classes)) * np.sqrt(1 / F)
        self.c = np.zeros(classes)

    def features(self, X):
        a, self.cols = conv_forward(X, self.w, self.b)
        self.h = np.maximum(a, 0)                                 # (N, F, S, S)
        flat = self.h.reshape(len(X), self.h.shape[1], -1)
        self.arg = flat.argmax(axis=2)                            # where each max was
        return flat.max(axis=2)                                   # (N, F)

    def step(self, X, y, lr, train_conv=True):
        f = self.features(X)
        loss, g = softmax_xent(f @ self.V + self.c, y)
        dV, dc = f.T @ g, g.sum(0)
        if train_conv:
            df = g @ self.V.T                                     # (N, F)
            dh = np.zeros(self.h.reshape(len(X), self.h.shape[1], -1).shape)
            n_idx, f_idx = np.indices(self.arg.shape)
            dh[n_idx, f_idx, self.arg] = df                       # max pool routes to argmax
            da = dh.reshape(self.h.shape) * (self.h > 0)          # ReLU gate
            _, dw, db = conv_backward(da, X, self.w, self.cols)
            self.w -= lr * dw; self.b -= lr * db
        self.V -= lr * dV; self.c -= lr * dc
        return loss

    def predict(self, X):
        return (self.features(X) @ self.V + self.c).argmax(1)


class MLP:
    """flatten -> 32 ReLU units -> linear -> softmax (fully connected)."""
    def __init__(self, d=S * S, hid=32, classes=3):
        self.A = rng.normal(size=(d, hid)) * np.sqrt(2 / d); self.a = np.zeros(hid)
        self.B = rng.normal(size=(hid, classes)) * np.sqrt(1 / hid); self.b = np.zeros(classes)

    def step(self, X, y, lr):
        X = X.reshape(len(X), -1)
        h = np.maximum(X @ self.A + self.a, 0)
        loss, g = softmax_xent(h @ self.B + self.b, y)
        dh = (g @ self.B.T) * (h > 0)
        self.B -= lr * h.T @ g; self.b -= lr * g.sum(0)
        self.A -= lr * X.T @ dh; self.a -= lr * dh.sum(0)
        return loss

    def predict(self, X):
        X = X.reshape(len(X), -1)
        return (np.maximum(X @ self.A + self.a, 0) @ self.B + self.b).argmax(1)


def train(model, X, y, epochs, lr, batch=32, **kw):
    for ep in range(epochs):
        order = rng.permutation(len(X))
        losses = [model.step(X[i], y[i], lr, **kw)
                  for i in np.array_split(order, len(X) // batch)]
    return np.mean(losses)


acc = lambda m, X, y: (m.predict(X) == y).mean()
n_cnn = 8 * 9 + 8 + 8 * 3 + 3
n_mlp = 144 * 32 + 32 + 32 * 3 + 3
print()
print("2. horizontal / vertical / diagonal bars, trained with bars in the LEFT half only")
cnn, mlp = TinyCNN(), MLP()
for ep_block in range(3):
    lc = train(cnn, Xtr, ytr, 10, 0.3)
    lm = train(mlp, Xtr, ytr, 10, 0.1)
    print(f"   after {10 * (ep_block + 1):2d} epochs: loss CNN {lc:.3f}  MLP {lm:.3f}")
print(f"   {'':22s}{'CNN':>8s}{'MLP':>8s}")
print(f"   {'parameters':22s}{n_cnn:8d}{n_mlp:8d}")
for name, X, y in [("train", Xtr, ytr), ("test, left half", Xte_same, yte_same),
                   ("test, RIGHT half", Xte_moved, yte_moved)]:
    print(f"   {name:22s}{acc(cnn, X, y):8.3f}{acc(mlp, X, y):8.3f}")

print()
print("3. the learned 3 x 3 filters (rounded), and which class each one votes for")
for f in range(cnn.w.shape[0]):
    rows = [" ".join(f"{v:5.1f}" for v in cnn.w[f, 0, r]) for r in range(3)]
    vote = ["horiz", "vert", "diag"][cnn.V[f].argmax()]
    print(f"   filter {f}: [{rows[0]} | {rows[1]} | {rows[2]}]  -> {vote}")

# --------------------------------------------------- 4. transfer learning
print()
print("4. transfer: a NEW task (anti-diagonal vs diagonal vs horizontal, bars anywhere,")
print("   noisier), few labelled examples; mean test accuracy over 4 runs")
Xbt, ybt = make_set(300, [3, 2, 0], left + right, noise=0.5)
print(f"   {'examples':>10s}{'frozen + new head':>20s}{'fine-tuned':>13s}{'from scratch':>15s}")
for n in (6, 15, 60):
    res = []
    for trial in range(4):
        Xb, yb = make_set(n, [3, 2, 0], left + right, noise=0.5)
        frozen = TinyCNN()
        frozen.w, frozen.b = cnn.w.copy(), cnn.b.copy()        # reuse learned filters
        train(frozen, Xb, yb, 40, 0.3, batch=3, train_conv=False)  # train only the head
        tuned = TinyCNN()
        tuned.w, tuned.b = cnn.w.copy(), cnn.b.copy()          # start from learned filters
        train(tuned, Xb, yb, 40, 0.3, batch=3)                 # then train everything
        scratch = TinyCNN()
        train(scratch, Xb, yb, 40, 0.3, batch=3)               # everything from random
        res.append([acc(m, Xbt, ybt) for m in (frozen, tuned, scratch)])
    r = np.mean(res, axis=0)
    print(f"   {n:10d}{r[0]:20.3f}{r[1]:13.3f}{r[2]:15.3f}")
