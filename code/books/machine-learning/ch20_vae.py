"""Chapter 20: sampling basics, the reparameterisation trick against the score-
function estimator, and a variational autoencoder trained from scratch on 2-D
data (a noisy ring), with the ELBO split into reconstruction and KL."""
import os
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
import numpy as np

rng = np.random.default_rng(2013)

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


# ------------------------------------------------- 1. sampling by inverse CDF
print("1. sampling an exponential distribution (rate 2) by the inverse CDF, x = -ln(1 - u) / 2")
u = rng.uniform(size=100_000)
x = -np.log(1 - u) / 2
print(f"   sample mean {x.mean():.4f} (exact 0.5), variance {x.var():.4f} (exact 0.25)")

# ------------------------------- 2. two ways to differentiate an expectation
print()
print("2. gradient of E[z^2] over z ~ N(mu, 1) with respect to mu, at mu = 1 (exact: 2 mu = 2)")
mu, n = 1.0, 100_000
eps = rng.normal(size=n)
z = mu + eps
reparam = 2 * z                       # d/dmu of (mu + eps)^2
score = z ** 2 * (z - mu)             # f(z) * d/dmu log N(z; mu, 1)
print(f"   reparameterisation: mean {reparam.mean():.3f}, std per sample {reparam.std():.2f}")
print(f"   score function    : mean {score.mean():.3f}, std per sample {score.std():.2f}")

# ------------------------------------------------------------ 3. the VAE
def ring(n):
    a = rng.uniform(0, 2 * np.pi, n)
    r = 2 + 0.1 * rng.normal(size=n)
    return np.stack([r * np.cos(a), r * np.sin(a)], 1)


def param(*shape):
    return T(rng.normal(size=shape) / np.sqrt(shape[0]))


H, Z, SX = 64, 2, 0.1                 # hidden units, latent size, decoder noise std
enc = dict(W1=param(2, H), b1=T(np.zeros(H)), Wm=param(H, Z), bm=T(np.zeros(Z)),
           Wv=param(H, Z), bv=T(np.zeros(Z)))
dec = dict(W1=param(Z, H), b1=T(np.zeros(H)), W2=param(H, H), b2=T(np.zeros(H)),
           W3=param(H, 2), b3=T(np.zeros(2)))


def decode(z):
    h = (z @ dec["W1"] + dec["b1"]).tanh()
    h = (h @ dec["W2"] + dec["b2"]).tanh()
    return h @ dec["W3"] + dec["b3"]


def elbo_terms(x):
    """Returns (negative ELBO per point, reconstruction term, KL term) as tensors."""
    xt = T(x)
    h = (xt @ enc["W1"] + enc["b1"]).tanh()
    m, logvar = h @ enc["Wm"] + enc["bm"], h @ enc["Wv"] + enc["bv"]
    e = T(rng.normal(size=m.data.shape))
    z = m + (logvar * 0.5).exp() * e          # the reparameterisation trick
    diff = decode(z) - xt
    n = len(x)
    rec = (diff * diff).sum(1).sum(0) * (1 / (2 * SX ** 2 * n))   # -log p(x|z) up to a constant
    kl = (m * m + logvar.exp() - logvar - 1).sum(1).sum(0) * (0.5 / n)
    return rec + kl, rec, kl


params = list(enc.values()) + list(dec.values())
opt = Adam(params, 0.003)
data = ring(2000)
print()
print(f"3. VAE on a noisy ring (radius 2, noise 0.1): latent size {Z}, decoder noise {SX}")
print("   (negative ELBO = reconstruction + KL, per point, in nats, up to a constant)")
for step in range(1, 3001):
    xb = data[rng.integers(0, len(data), 128)]
    loss, rec, kl = elbo_terms(xb)
    loss.backward()
    opt.step()
    if step in (1, 250, 1000, 3000):
        print(f"   step {step:4d}: -ELBO {loss.data.item():8.2f} = reconstruction {rec.data.item():8.2f}"
              f" + KL {kl.data.item():5.2f}")

samples = decode(T(rng.normal(size=(5000, Z)))).data      # z from the prior, then decode
radius = np.linalg.norm(samples, axis=1)
angle = np.arctan2(samples[:, 1], samples[:, 0])
print()
print("4. 5000 new points: z ~ N(0, I), x = decoder mean")
print(f"   radius: mean {radius.mean():.3f}, std {radius.std():.3f}   (data: 2.000, 0.100)")
print(f"   share of points with 1.7 < radius < 2.3: {np.mean(np.abs(radius - 2) < 0.3):.3f}")
counts = np.histogram(angle, bins=8, range=(-np.pi, np.pi))[0]
print(f"   points in each eighth of the circle: {counts.tolist()}")
