"""Chapter 20: normalizing flows from scratch. The change-of-variables formula
checked by histogram, an affine coupling layer with its log-determinant checked
against the full Jacobian, and a 1-D flow trained by maximum likelihood on
bimodal data, sampled by inverting it."""
import numpy as np

rng = np.random.default_rng(2015)

# ------------------------------------------- a small reverse-mode autodiff on arrays
class T:
    """An array that remembers how it was made, so backward() can apply the chain rule."""
    def __init__(self, data, parents=(), back=None):
        self.data = np.asarray(data, dtype=float)
        self.grad = None
        self.parents, self.back = parents, back

    @staticmethod
    def lift(x):
        return x if isinstance(x, T) else T(x)

    def __add__(self, o):
        o = T.lift(o)
        return T(self.data + o.data, (self, o), lambda g: (g, g))

    __radd__ = __add__

    def __neg__(self):
        return T(-self.data, (self,), lambda g: (-g,))

    def __sub__(self, o):
        return self + (-T.lift(o))

    def __rsub__(self, o):
        return T.lift(o) + (-self)

    def __mul__(self, o):
        o = T.lift(o)
        return T(self.data * o.data, (self, o), lambda g: (g * o.data, g * self.data))

    __rmul__ = __mul__

    def __matmul__(self, W):   # (..., d) @ (d, k)
        def back(g):
            A = self.data.reshape(-1, self.data.shape[-1])
            return g @ W.data.T, A.T @ g.reshape(-1, g.shape[-1])
        return T(self.data @ W.data, (self, W), back)

    def tanh(self):
        y = np.tanh(self.data)
        return T(y, (self,), lambda g: (g * (1 - y * y),))

    def exp(self):
        y = np.exp(self.data)
        return T(y, (self,), lambda g: (g * y,))

    def log(self):
        x = self.data
        return T(np.log(x), (self,), lambda g: (g / x,))

    def sigmoid(self):
        y = 1 / (1 + np.exp(-self.data))
        return T(y, (self,), lambda g: (g * y * (1 - y),))

    def sum(self, axis):
        shape = self.data.shape
        return T(self.data.sum(axis=axis, keepdims=True), (self,),
                 lambda g: (np.broadcast_to(g, shape),))

    def softmax(self, axis):
        e = np.exp(self.data - self.data.max(axis=axis, keepdims=True))
        y = e / e.sum(axis=axis, keepdims=True)
        return T(y, (self,), lambda g: (y * (g - (g * y).sum(axis=axis, keepdims=True)),))

    def __getitem__(self, idx):
        shape = self.data.shape
        def back(g):
            full = np.zeros(shape)
            full[idx] = g
            return (full,)
        return T(self.data[idx], (self,), back)

    def reshape(self, *shape):
        old = self.data.shape
        return T(self.data.reshape(*shape), (self,), lambda g: (g.reshape(old),))

    def xent(self, y):
        """Mean softmax cross-entropy of logits (N, V) against integer labels y."""
        z = self.data - self.data.max(axis=1, keepdims=True)
        p = np.exp(z); p /= p.sum(axis=1, keepdims=True)
        n = len(y)
        loss = -np.log(p[np.arange(n), y] + 1e-12).mean()
        def back(g):
            d = p.copy(); d[np.arange(n), y] -= 1
            return (g * d / n,)
        return T(loss, (self,), back)

    def backward(self):
        order, seen = [], set()
        def visit(t):
            if id(t) not in seen:
                seen.add(id(t))
                for p in t.parents:
                    visit(p)
                order.append(t)
        visit(self)
        for t in order:
            t.grad = None
        self.grad = np.ones_like(self.data)
        for t in reversed(order):
            if t.back is None or t.grad is None:
                continue
            for p, g in zip(t.parents, t.back(t.grad)):
                while g.ndim > p.data.ndim:           # undo broadcasting
                    g = g.sum(axis=0)
                for ax, n in enumerate(p.data.shape):
                    if n == 1 and g.shape[ax] != 1:
                        g = g.sum(axis=ax, keepdims=True)
                p.grad = g if p.grad is None else p.grad + g


def gather(E, idx):
    """Rows of E picked by integer array idx (an embedding lookup)."""
    def back(g):
        full = np.zeros_like(E.data)
        np.add.at(full, idx, g)
        return (full,)
    return T(E.data[idx], (E,), back)


def stack(ts, axis=1):
    """Stack tensors of equal shape along a new axis (used to collect encoder states)."""
    def back(g):
        return tuple(np.take(g, i, axis=axis) for i in range(len(ts)))
    return T(np.stack([t.data for t in ts], axis=axis), tuple(ts), back)


class Adam:
    def __init__(self, params, lr=0.01, b1=0.9, b2=0.999):
        self.p, self.lr, self.b1, self.b2, self.t = params, lr, b1, b2, 0
        self.m = [np.zeros_like(q.data) for q in params]
        self.v = [np.zeros_like(q.data) for q in params]

    def step(self):
        self.t += 1
        for q, m, v in zip(self.p, self.m, self.v):
            if q.grad is None:
                continue
            m *= self.b1; m += (1 - self.b1) * q.grad
            v *= self.b2; v += (1 - self.b2) * q.grad ** 2
            mh, vh = m / (1 - self.b1 ** self.t), v / (1 - self.b2 ** self.t)
            q.data -= self.lr * mh / (np.sqrt(vh) + 1e-8)


# -------------------------------------------- 1. change of variables in 1-D
print("1. z ~ Uniform(0, 1), x = z^2: the formula says p(x) = p(z) |dz/dx| = 1 / (2 sqrt x)")
x = rng.uniform(size=200_000) ** 2
hist, edges = np.histogram(x, bins=[0.01, 0.05, 0.2, 0.5, 0.9])
for lo, hi, h in zip(edges, edges[1:], hist):
    exact = np.sqrt(hi) - np.sqrt(lo)                    # integral of 1/(2 sqrt x) from lo to hi
    print(f"   P({lo:4.2f} < x < {hi:4.2f}): sampled {h / len(x):.4f}, formula {exact:.4f}")

# -------------------------------------------- 2. an affine coupling layer
print()
print("2. affine coupling in 4-D: y1 = x1, y2 = x2 * exp(s(x1)) + t(x1)")
W1, W2 = rng.normal(size=(2, 8)), rng.normal(size=(8, 4))


def coupling(x):
    h = np.tanh(x[:2] @ W1) @ W2                          # any network of x1 at all
    s, t = h[:2], h[2:]
    return np.concatenate([x[:2], x[2:] * np.exp(s) + t]), s.sum()


def inverse(y):
    h = np.tanh(y[:2] @ W1) @ W2                          # y1 = x1, so s and t are known
    s, t = h[:2], h[2:]
    return np.concatenate([y[:2], (y[2:] - t) * np.exp(-s)])


x0 = rng.normal(size=4)
y0, logdet = coupling(x0)
J = np.zeros((4, 4))
for j in range(4):
    e = np.zeros(4); e[j] = 1e-6
    J[:, j] = (coupling(x0 + e)[0] - coupling(x0 - e)[0]) / 2e-6
print(f"   inverse(coupling(x)) == x? {np.allclose(inverse(y0), x0)}")
print(f"   log|det J| from the full 4x4 Jacobian {np.log(abs(np.linalg.det(J))):.6f}; sum of s {logdet:.6f}")

# --------------------------------------------- 3. a 1-D flow trained by MLE
def data(n):
    side = rng.choice([-2.0, 2.0], n)
    return side + 0.5 * rng.normal(size=n)


def true_logp(x):
    return np.log(0.5 * np.exp(-0.5 * ((x + 2) / 0.5) ** 2) + 0.5 * np.exp(-0.5 * ((x - 2) / 0.5) ** 2)) \
        - np.log(0.5 * np.sqrt(2 * np.pi))


K = 6                                                     # number of tanh layers
alpha = T(rng.normal(size=K) * 0.1); beta = T(rng.normal(size=K) * 0.1)
shift = T(rng.normal(size=K)); a_out = T(np.zeros(1)); b_out = T(np.zeros(1))


def g_and_logdet(x):
    """z = g(x) built from layers u -> u + w tanh(s u + t) with s = e^beta > 0 and
    w s = e^alpha - 0.99 > -1, so each layer is increasing: its derivative
    1 + w s (1 - tanh^2) is at least 0.01. Then z = e^a u + b."""
    u, logdet = T(x), 0
    ws, s = alpha.exp() - 0.99, beta.exp()
    for k in range(K):
        th = (u * s[k] + shift[k]).tanh()
        logdet = logdet + (1 + ws[k] * (1 - th * th)).log()
        u = u + ws[k] * th * (-beta[k]).exp()           # w = (w s) / s
    return u * a_out.exp() + b_out, logdet + a_out


def nll(x):
    z, logdet = g_and_logdet(x)
    logp = (z * z) * -0.5 - 0.5 * np.log(2 * np.pi) + logdet  # log N(z) + log|dz/dx|
    return logp.sum(0) * (-1 / len(x))


opt = Adam([alpha, beta, shift, a_out, b_out], 0.03)
train, test = data(2000), data(5000)
print()
print(f"3. a {K}-layer flow on data 0.5 N(-2, 0.5^2) + 0.5 N(2, 0.5^2)")
for step in range(1, 1501):
    loss = nll(train[rng.integers(0, len(train), 256)])
    loss.backward(); opt.step()
    if step in (1, 100, 500, 1500):
        print(f"   step {step:4d}: train negative log-likelihood {loss.data.item():.4f}")
mu, sd = train.mean(), train.std()
gauss_nll = 0.5 * np.log(2 * np.pi * sd ** 2) + np.mean((test - mu) ** 2) / (2 * sd ** 2)
print(f"   test NLL: flow {nll(test).data.item():.4f}, best single Gaussian {gauss_nll:.4f}, "
      f"true density {-true_logp(test).mean():.4f}")
for xv in (-2.0, 0.0, 2.0):
    z, ld = g_and_logdet(np.array([xv]))
    p = np.exp(-0.5 * z.data[0] ** 2 + ld.data[0]) / np.sqrt(2 * np.pi)
    print(f"   density at x = {xv:4.1f}: flow {p:.4f}, true {np.exp(true_logp(xv)):.4f}")

# sampling: z ~ N(0, 1), then solve g(x) = z by bisection (g is increasing)
zs = rng.normal(size=4000)
lo, hi = np.full_like(zs, -20.0), np.full_like(zs, 20.0)
for _ in range(60):
    mid = (lo + hi) / 2
    above = g_and_logdet(mid)[0].data > zs
    hi, lo = np.where(above, mid, hi), np.where(above, lo, mid)
xs = (lo + hi) / 2
print(f"   4000 samples by inverting g: share below 0 {np.mean(xs < 0):.3f}, "
      f"mean |x| {np.abs(xs).mean():.3f} (data 2.0), std of |x| {np.abs(xs).std():.3f} (data about 0.5)")
