"""Chapter 19: a tiny character-level transformer (decoder only, like GPT) from
scratch in NumPy: embeddings, positions, causal multi-head self-attention,
layer norm, residuals, MLP. A small reverse-mode autodiff on arrays does the
backward pass, checked against finite differences; then the model is trained
for a few hundred steps on a short text and samples from it."""
import os
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")   # tiny matrices: threads only add overhead
import numpy as np

rng = np.random.default_rng(2017)


# ------------------------------------------------------------- the autodiff
class T:
    def __init__(self, data, parents=(), back=None):
        self.data = np.asarray(data, dtype=float)
        self.grad, self.parents, self.back = None, parents, back

    def __add__(self, o):
        o = o if isinstance(o, T) else T(o)
        return T(self.data + o.data, (self, o), lambda g: (g, g))

    def __mul__(self, o):
        o = o if isinstance(o, T) else T(o)
        return T(self.data * o.data, (self, o), lambda g: (g * o.data, g * self.data))

    def __matmul__(self, W):                       # (..., d) @ (d, k)
        def back(g):
            A = self.data.reshape(-1, self.data.shape[-1])
            return g @ W.data.T, A.T @ g.reshape(-1, g.shape[-1])
        return T(self.data @ W.data, (self, W), back)

    def bmm(self, o):                              # batched (..., n, k) @ (..., k, m)
        sw = lambda a: np.swapaxes(a, -1, -2)
        return T(self.data @ o.data, (self, o), lambda g: (g @ sw(o.data), sw(self.data) @ g))

    def transpose(self, *axes):
        inv = np.argsort(axes)
        return T(self.data.transpose(axes), (self,), lambda g: (g.transpose(inv),))

    def reshape(self, *shape):
        old = self.data.shape
        return T(self.data.reshape(shape), (self,), lambda g: (g.reshape(old),))

    def relu(self):
        m = self.data > 0
        return T(self.data * m, (self,), lambda g: (g * m,))

    def softmax(self):                             # over the last axis
        e = np.exp(self.data - self.data.max(-1, keepdims=True))
        y = e / e.sum(-1, keepdims=True)
        return T(y, (self,), lambda g: (y * (g - (g * y).sum(-1, keepdims=True)),))

    def layernorm(self, gain, bias, eps=1e-5):
        x = self.data
        mu, var = x.mean(-1, keepdims=True), x.var(-1, keepdims=True)
        sd = np.sqrt(var + eps)
        xh = (x - mu) / sd
        def back(g):
            gx = g * gain.data
            dx = (gx - gx.mean(-1, keepdims=True) - xh * (gx * xh).mean(-1, keepdims=True)) / sd
            return dx, (g * xh).reshape(-1, x.shape[-1]).sum(0), g.reshape(-1, x.shape[-1]).sum(0)
        return T(xh * gain.data + bias.data, (self, gain, bias), back)

    def xent(self, y):                             # logits (N, V), labels (N,)
        z = self.data - self.data.max(1, keepdims=True)
        p = np.exp(z); p /= p.sum(1, keepdims=True)
        n = len(y)
        def back(g):
            d = p.copy(); d[np.arange(n), y] -= 1
            return (g * d / n,)
        return T(-np.log(p[np.arange(n), y]).mean(), (self,), back)

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
                while g.ndim > p.data.ndim:
                    g = g.sum(0)
                for ax, size in enumerate(p.data.shape):
                    if size == 1 and g.shape[ax] != 1:
                        g = g.sum(ax, keepdims=True)
                p.grad = g if p.grad is None else p.grad + g


def gather(E, idx):
    def back(g):
        full = np.zeros_like(E.data)
        np.add.at(full, idx, g)
        return (full,)
    return T(E.data[idx], (E,), back)


# ---------------------------------------------------------------- the model
class Transformer:
    def __init__(self, V, ctx, d=48, heads=4, layers=2):
        p = lambda *s, sc=0.02: T(rng.normal(size=s) * sc)
        self.ctx, self.d, self.h = ctx, d, heads
        self.tok, self.pos = p(V, d), p(ctx, d)                 # learned positions (as in GPT)
        self.blocks = []
        for _ in range(layers):
            self.blocks.append(dict(
                g1=T(np.ones(d)), b1=T(np.zeros(d)), Wqkv=p(d, 3 * d), Wo=p(d, d),
                g2=T(np.ones(d)), b2=T(np.zeros(d)), W1=p(d, 4 * d), c1=T(np.zeros(4 * d)),
                W2=p(4 * d, d), c2=T(np.zeros(d))))
        self.gf, self.bf, self.Wout = T(np.ones(d)), T(np.zeros(d)), p(d, V)
        mask = np.tril(np.ones((ctx, ctx), bool))
        self.mask = np.where(mask, 0.0, -1e9)                   # added to scores: -inf above diagonal

    def params(self):
        ps = [self.tok, self.pos, self.gf, self.bf, self.Wout]
        for b in self.blocks:
            ps += list(b.values())
        return ps

    def attention(self, x, b):
        B, n, d = x.data.shape
        h, dk = self.h, d // self.h
        qkv = (x @ b["Wqkv"]).reshape(B, n, 3, h, dk).transpose(2, 0, 3, 1, 4)   # (3, B, h, n, dk)
        Q, K, Vv = self._split(qkv)                             # each (B, h, n, dk)
        S = Q.bmm(K.transpose(0, 1, 3, 2)) * (1 / np.sqrt(dk)) + self.mask[:n, :n]
        A = S.softmax()                                         # (B, h, n, n)
        self.last_attention = A.data
        O = A.bmm(Vv).transpose(0, 2, 1, 3).reshape(B, n, d)   # heads side by side
        return O @ b["Wo"]

    @staticmethod
    def _split(qkv):
        """Split the first axis into three tensors, each sending its gradient back."""
        parts = []
        for i in range(3):
            def back(g, i=i):
                full = np.zeros_like(qkv.data); full[i] = g
                return (full,)
            parts.append(T(qkv.data[i], (qkv,), back))
        return parts

    def __call__(self, idx):
        B, n = idx.shape
        x = gather(self.tok, idx) + gather(self.pos, np.arange(n))
        for b in self.blocks:
            x = x + self.attention(x.layernorm(b["g1"], b["b1"]), b)          # pre-norm residual
            m = x.layernorm(b["g2"], b["b2"])
            x = x + ((m @ b["W1"] + b["c1"]).relu() @ b["W2"] + b["c2"])    # MLP residual
        return x.layernorm(self.gf, self.bf) @ self.Wout                     # (B, n, V) logits

    def loss(self, idx, targets):
        logits = self(idx)
        return logits.reshape(-1, logits.data.shape[-1]).xent(targets.reshape(-1))


# ------------------------------------------------------------------ the text
text = ("the rover woke at dawn and read the sky. the rover saw a rock and drove to the rock. "
        "the rock was red and the sand was red. the rover took a picture of the rock and sent it home. "
        "home was far away, and the signal took many minutes to arrive, so the rover had to plan alone. "
        "it chose a safe path between the rocks, it drove slowly, and it stopped before the sand. "
        "at night the rover slept and the sky was dark. at dawn the rover woke and read the sky again. ")
chars = sorted(set(text))
stoi = {c: i for i, c in enumerate(chars)}
data = np.array([stoi[c] for c in text])
V, ctx = len(chars), 32
print(f"text: {len(text)} characters, vocabulary {V}, context {ctx}")

# ------------------------------------------------------- 1. gradient check
small = Transformer(V, 8, d=8, heads=2, layers=1)
for p in small.params():                       # larger weights, so the check is not trivial
    p.data += rng.normal(size=p.data.shape) * 0.3
xb = data[None, :8]; yb = data[None, 1:9]
L = small.loss(xb, yb); L.backward()
print()
print("1. gradient check on a tiny model (d = 8, 2 heads, 1 block):")
for name, P in [("token embedding", small.tok), ("W_qkv", small.blocks[0]["Wqkv"]),
                ("layer-norm gain", small.blocks[0]["g2"]), ("output W", small.Wout)]:
    worst = 0.0
    for _ in range(5):
        idx = tuple(rng.integers(0, s) for s in P.data.shape)
        if name == "token embedding":
            idx = (int(xb[0, 0]), idx[1])      # a row that is actually used
        old = P.data[idx]
        P.data[idx] = old + 1e-5; fp = small.loss(xb, yb).data
        P.data[idx] = old - 1e-5; fm = small.loss(xb, yb).data
        P.data[idx] = old
        num = (fp - fm) / 2e-5
        worst = max(worst, abs(num - P.grad[idx]) / max(1e-8, abs(num) + abs(P.grad[idx])))
    print(f"   {name:16s}: worst relative error over 5 entries {worst:.1e}")

# ------------------------------------------------- 2. causality of the model
x1 = data[None, :ctx].copy(); x2 = x1.copy(); x2[0, 20:] = stoi["z"] if "z" in stoi else 0
model = Transformer(V, ctx)
same = np.allclose(model(x1).data[0, :20], model(x2).data[0, :20])
print()
print(f"2. changing characters 20.. leaves the predictions at positions 0..19 unchanged? {same}")

# ----------------------------------------------------------------- 3. train
class Adam:
    def __init__(self, ps, lr):
        self.ps, self.lr, self.t = ps, lr, 0
        self.m = [np.zeros_like(p.data) for p in ps]; self.v = [np.zeros_like(p.data) for p in ps]
    def step(self):
        self.t += 1
        for p, m, v in zip(self.ps, self.m, self.v):
            m[:] = 0.9 * m + 0.1 * p.grad; v[:] = 0.999 * v + 0.001 * p.grad ** 2
            p.data -= self.lr * (m / (1 - 0.9 ** self.t)) / (np.sqrt(v / (1 - 0.999 ** self.t)) + 1e-8)


n_params = sum(p.data.size for p in model.params())
print()
print(f"3. training a 2-block, 4-head, d = 48 model ({n_params:,} parameters), Adam, batch 16")
opt = Adam(model.params(), 3e-3)
print(f"   loss before training {float(model.loss(data[None, :ctx], data[None, 1:ctx + 1]).data):.3f}"
      f" (uniform guessing: ln {V} = {np.log(V):.3f})")
for step in range(1, 251):
    starts = rng.integers(0, len(data) - ctx - 1, 16)
    xb = np.stack([data[s:s + ctx] for s in starts]); yb = np.stack([data[s + 1:s + ctx + 1] for s in starts])
    L = model.loss(xb, yb); L.backward(); opt.step()
    if step % 50 == 0:
        print(f"   step {step:3d}: loss {float(L.data):.3f}")

# ---------------------------------------------------------------- 4. sample
def generate(prompt, n, temperature=0.5):
    idx = [stoi[c] for c in prompt]
    for _ in range(n):
        logits = model(np.array([idx[-ctx:]])).data[0, -1] / temperature
        p = np.exp(logits - logits.max()); p /= p.sum()
        idx.append(rng.choice(V, p=p))
    return "".join(chars[i] for i in idx)


print()
print("4. samples (temperature 0.5):")
for prompt in ("the rover ", "at night "):
    print("   " + repr(generate(prompt, 60)))
