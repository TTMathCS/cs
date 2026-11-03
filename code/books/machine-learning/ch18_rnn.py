"""Chapter 18: recurrent networks from scratch. A scalar RNN traced by hand,
backpropagation through time derived and checked, vanishing and exploding
gradients measured, and a vanilla RNN, an LSTM and a GRU trained on a task that
needs memory. NumPy only; a small reverse-mode autodiff (as in Chapter 15, but on
arrays) does the bookkeeping for the gated cells."""
import os
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")   # tiny matrices: threads only add overhead
import numpy as np

rng = np.random.default_rng(18)

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


# ------------------------------------------------------ 1. a scalar RNN by hand
print("1. scalar RNN h_t = tanh(w h_(t-1) + u x_t), w = 0.5, u = 1, h_0 = 0")
w, u, h = 0.5, 1.0, 0.0
for t, x in enumerate([1.0, 0.0, -1.0], start=1):
    pre = w * h + u * x
    h = np.tanh(pre)
    print(f"   t={t}: x={x:+.0f}  w*h+u*x = {pre:+.4f}  h_{t} = {h:+.4f}")


# ------------------------------------ 2. backpropagation through time, by hand
def rnn_forward(X, W, U, b):
    """X: (T, d_in). Returns all hidden states H[0..T] with H[0] = 0."""
    H = [np.zeros(W.shape[0])]
    for x in X:
        H.append(np.tanh(W @ H[-1] + U @ x + b))
    return H


def rnn_bptt(X, W, U, b, dH):
    """dH[t] = dL/dh_t coming from the loss directly (t = 1..T).
    Walk backwards: delta_t = (dH[t] + W^T a_(t+1)) and a_t = delta_t * (1 - h_t^2)."""
    H = rnn_forward(X, W, U, b)
    dW, dU, db = np.zeros_like(W), np.zeros_like(U), np.zeros_like(b)
    carry = np.zeros(W.shape[0])                 # dL/dh_t arriving from step t+1
    for t in range(len(X), 0, -1):
        delta = dH[t] + carry
        a = delta * (1 - H[t] ** 2)              # through tanh
        dW += np.outer(a, H[t - 1]); dU += np.outer(a, X[t - 1]); db += a
        carry = W.T @ a                          # to h_(t-1)
    return dW, dU, db


d, din, Tn = 4, 3, 6
W, U, b = rng.normal(size=(d, d)) * 0.5, rng.normal(size=(d, din)), rng.normal(size=d) * 0.1
X = rng.normal(size=(Tn, din))
R = rng.normal(size=(Tn + 1, d)); R[0] = 0       # loss = sum_t R_t . h_t
loss = lambda: sum(R[t] @ h for t, h in enumerate(rnn_forward(X, W, U, b)))
grads = rnn_bptt(X, W, U, b, R)
print()
print("2. BPTT gradient check, loss = sum_t r_t . h_t over 6 steps")
for name, P, g in [("W", W, grads[0]), ("U", U, grads[1]), ("b", b, grads[2])]:
    num = np.zeros_like(P)
    for idx in np.ndindex(P.shape):
        old = P[idx]
        P[idx] = old + 1e-6; fp = loss()
        P[idx] = old - 1e-6; fm = loss()
        P[idx] = old
        num[idx] = (fp - fm) / 2e-6
    print(f"   d{name}: max |BPTT - numeric| = {np.abs(num - g).max():.1e}")


# ----------------------------------------- 3. vanishing and exploding gradients
print()
print("3. size of dh_t/dh_0 (spectral norm) for a 16-unit RNN, U scaled to spectral radius rho")
d = 16
Q = rng.normal(size=(d, d))
Q /= np.max(np.abs(np.linalg.eigvals(Q)))        # spectral radius 1
steps = [1, 5, 10, 20, 40]
print("   " + " " * 22 + "".join(f"t={t:<9d}" for t in steps))
for act in ("linear", "tanh"):
    for rho in (0.5, 1.0, 1.5):
        Wr = rho * Q
        h, J, out = rng.normal(size=d) * 0.5, np.eye(d), {}
        for t in range(1, 41):
            pre = Wr @ h + 0.5 * rng.normal(size=d)
            h = pre if act == "linear" else np.tanh(pre)
            D = np.ones(d) if act == "linear" else 1 - h ** 2
            J = (D[:, None] * Wr) @ J            # chain rule: dh_t/dh_0
            out[t] = np.linalg.norm(J, 2)
        print(f"   {act:6s} rho={rho:3.1f}         " + "".join(f"{out[t]:<11.2e}" for t in steps))


# ------------------------------------------------- the task: remember a symbol
def make_batch(n, T):
    """The first input is a symbol 0/1/2/3; then T-1 steps of random noise symbols 4..7.
    The answer, asked for at the last step, is the first symbol."""
    first = rng.integers(0, 4, n)
    seq = rng.integers(4, 8, (n, T))
    seq[:, 0] = first
    return np.eye(8)[seq], first                 # one-hot (n, T, 8)


def param(*shape, scale=None):
    scale = scale if scale is not None else 1 / np.sqrt(shape[0])
    return T(rng.normal(size=shape) * scale)


class VanillaRNN:
    def __init__(self, d=16):
        self.d, self.Wx, self.Wh, self.b = d, param(8, d), param(d, d), T(np.zeros(d))
    def run(self, X):
        h = T(np.zeros((X.shape[0], self.d)))
        self.inputs = []
        for t in range(X.shape[1]):
            x = T(X[:, t]); self.inputs.append(x)
            h = (x @ self.Wx + h @ self.Wh + self.b).tanh()
        return h
    def params(self):
        return [self.Wx, self.Wh, self.b]


class LSTM:
    """Four gates computed by one matrix product, then sliced: input i, forget f,
    output o, candidate n."""
    def __init__(self, d=16, forget_bias=3.0):
        self.d, self.Wx, self.Wh = d, param(8, 4 * d), param(d, 4 * d)
        b = np.zeros(4 * d); b[d:2 * d] = forget_bias      # start by remembering
        self.b = T(b)
    def run(self, X):
        d, n = self.d, X.shape[0]
        h, c = T(np.zeros((n, d))), T(np.zeros((n, d)))
        self.inputs = []
        for t in range(X.shape[1]):
            x = T(X[:, t]); self.inputs.append(x)
            g = x @ self.Wx + h @ self.Wh + self.b
            i, f, o = g[:, :d].sigmoid(), g[:, d:2 * d].sigmoid(), g[:, 2 * d:3 * d].sigmoid()
            c = f * c + i * g[:, 3 * d:].tanh()   # the cell: forget some, write some
            h = o * c.tanh()                      # the output: read some
        return h
    def params(self):
        return [self.Wx, self.Wh, self.b]


class GRU:
    """Update gate z, reset gate r, candidate n; h = (1 - z) n + z h_old."""
    def __init__(self, d=16, keep_bias=3.0):
        self.d, self.Wx, self.Wzr, self.Wn = d, param(8, 3 * d), param(d, 2 * d), param(d, d)
        b = np.zeros(3 * d); b[:d] = keep_bias          # start by keeping the old state
        self.b = T(b)
    def run(self, X):
        d = self.d
        h = T(np.zeros((X.shape[0], d)))
        self.inputs = []
        for t in range(X.shape[1]):
            xt = T(X[:, t]); self.inputs.append(xt)
            x = xt @ self.Wx + self.b
            zr = (x[:, :2 * d] + h @ self.Wzr).sigmoid()
            z, r = zr[:, :d], zr[:, d:]
            cand = (x[:, 2 * d:] + (r * h) @ self.Wn).tanh()
            h = (1 - z) * cand + z * h            # interpolate: keep old or take new
        return h
    def params(self):
        return [self.Wx, self.Wzr, self.Wn, self.b]


def head(cell):
    return param(cell.d, 4), T(np.zeros(4))


print()
print("4. at initialisation: size of the gradient of the loss with respect to the FIRST input")
print("   (median over 9 random initialisations)")
print(f"   {'T':>4s}{'vanilla RNN':>14s}{'LSTM':>11s}{'GRU':>11s}")
for T_len in (5, 20, 80):
    row = []
    for Cls in (VanillaRNN, LSTM, GRU):
        norms = []
        for rep in range(9):
            cell = Cls(); V, c = head(cell)
            X, y = make_batch(32, T_len)
            (cell.run(X) @ V + c).xent(y).backward()
            norms.append(np.linalg.norm(cell.inputs[0].grad))
        row.append(np.median(norms))
    print(f"   {T_len:4d}" + "".join(f"{g:{w}.1e}" for g, w in zip(row, (14, 11, 11))))


def train(cell, T_len, steps, lr=0.01):
    V, c = head(cell)
    opt = Adam(cell.params() + [V, c], lr)
    for s in range(steps):
        X, y = make_batch(32, T_len)
        loss = (cell.run(X) @ V + c).xent(y)
        loss.backward()
        opt.step()
    X, y = make_batch(300, T_len)
    return ((cell.run(X) @ V + c).data.argmax(1) == y).mean()


print()
print("5. trained 250 steps (Adam, batch 32), T = 60: test accuracy (4 classes, chance 0.25)")
for Cls in (VanillaRNN, GRU):
    print(f"   {Cls.__name__:12s}{train(Cls(), 60, 250):.3f}")
