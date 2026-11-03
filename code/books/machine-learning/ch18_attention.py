"""Chapter 18: sequence to sequence from scratch, with and without attention
(Bahdanau, Cho and Bengio 2014), on a toy task: reverse a sequence of symbols.
A small reverse-mode autodiff on NumPy arrays does the backpropagation."""
import os
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")   # tiny matrices: threads only add overhead
import numpy as np

rng = np.random.default_rng(14)

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


# ----------------------------------------------------------------- the task
SYM, L, BOS = 8, 12, 8                   # symbols 0..7, length 12, start token 8


def batch(n):
    src = rng.integers(0, SYM, (n, L))
    return src, src[:, ::-1].copy()      # target: the source reversed


def param(*shape):
    return T(rng.normal(size=shape) / np.sqrt(shape[0]))


class Seq2Seq:
    def __init__(self, attention, d=32, e=16, da=32):
        self.att, self.d = attention, d
        self.E = param(SYM + 1, e)                                   # embeddings
        self.eWx, self.eWh, self.eb = param(e, d), param(d, d), T(np.zeros(d))
        self.dWy, self.dWs, self.db = param(e, d), param(d, d), T(np.zeros(d))
        self.Wo, self.bo = param(d, SYM), T(np.zeros(SYM))
        if attention:
            self.Wa, self.Ua, self.va = param(d, da), param(d, da), param(da, 1)
            self.dWc, self.Wco = param(d, d), param(d, SYM)

    def params(self):
        return [v for v in vars(self).values() if isinstance(v, T)]

    def encode(self, src):
        h, states = T(np.zeros((len(src), self.d))), []
        X = gather(self.E, src) @ self.eWx + self.eb                 # all steps at once
        for t in range(L):
            h = (X[:, t] + h @ self.eWh).tanh()
            states.append(h)
        return h, stack(states)                                      # (n, d), (n, L, d)

    def attend(self, s, H, HU):
        """Bahdanau's additive score e_i = v . tanh(W s + U h_i), softmax over i."""
        n = H.data.shape[0]
        e = (HU + (s @ self.Wa).reshape(n, 1, -1)).tanh() @ self.va  # (n, L, 1)
        a = e.softmax(axis=1)
        ctx = (a * H).sum(axis=1).reshape(n, self.d)                 # weighted average
        return ctx, a

    def step(self, y_in, s, H, HU):
        """One decoder step. y_in = embedding of the previous output times dWy.
        Returns logits, new state, attention weights."""
        if self.att:
            ctx, a = self.attend(s, H, HU)
            s = (y_in + s @ self.dWs + ctx @ self.dWc + self.db).tanh()
            return s @ self.Wo + ctx @ self.Wco + self.bo, s, a
        s = (y_in + s @ self.dWs + self.db).tanh()
        return s @ self.Wo + self.bo, s, None

    def loss(self, src, tgt):
        s, H = self.encode(src)
        HU = H @ self.Ua if self.att else None
        prev = np.concatenate([np.full((len(src), 1), BOS), tgt[:, :-1]], axis=1)
        Y = gather(self.E, prev) @ self.dWy        # teacher forcing: true previous symbols
        total = 0
        for t in range(L):
            logits, s, _ = self.step(Y[:, t], s, H, HU)
            total = total + logits.xent(tgt[:, t])
        return total * (1 / L)

    def decode(self, src):
        s, H = self.encode(src)
        HU = H @ self.Ua if self.att else None
        prev, out, weights = np.full(len(src), BOS), [], []
        for t in range(L):
            logits, s, a = self.step(gather(self.E, prev) @ self.dWy, s, H, HU)
            prev = logits.data.argmax(1)                             # greedy
            out.append(prev)
            if a is not None:
                weights.append(a.data[0, :, 0])
        return np.array(out).T, np.array(weights)


def train(model, steps):
    opt = Adam(model.params(), 0.01)
    for s in range(1, steps + 1):
        src, tgt = batch(64)
        loss = model.loss(src, tgt)
        loss.backward()
        opt.step()
        if s % 100 == 0:
            print(f"   step {s:4d}: loss {float(loss.data):.3f}")


test_src, test_tgt = batch(500)
for att in (False, True):
    print(f"{'with' if att else 'without'} attention: reverse sequences of {L} symbols")
    model = Seq2Seq(att)
    train(model, 300)
    pred, w = model.decode(test_src)
    print(f"   test: symbols right {(pred == test_tgt).mean():.3f}, "
          f"whole sequences right {(pred == test_tgt).all(1).mean():.3f}")
    print()
print("attention weights for the first test sequence", test_src[0])
print("(row = output step, column = input position; each row sums to 1)")
for t, row in enumerate(w):
    print(f"   out {t} ({pred[0, t]}): " + " ".join(f"{v:4.2f}" for v in row))
