"""Chapter 16: a small layer library in NumPy. Every layer has forward and backward; run this file to
check every backward pass against finite differences."""
import numpy as np


class Linear:
    def __init__(self, n_in, n_out, rng, init="he"):
        std = {"he": np.sqrt(2.0 / n_in), "xavier": np.sqrt(2.0 / (n_in + n_out))}.get(init, init)
        self.W = rng.normal(size=(n_in, n_out)) * std     # init may also be a plain number (the std)
        self.b = np.zeros(n_out)
        self.params = [self.W, self.b]

    def forward(self, x, train=True):
        self.x = x
        return x @ self.W + self.b

    def backward(self, g):
        self.grads = [self.x.T @ g, g.sum(0)]
        return g @ self.W.T


class ReLU:
    params = []
    def forward(self, x, train=True):
        self.mask = x > 0
        return x * self.mask
    def backward(self, g):
        self.grads = []
        return g * self.mask


class Tanh:
    params = []
    def forward(self, x, train=True):
        self.y = np.tanh(x)
        return self.y
    def backward(self, g):
        self.grads = []
        return g * (1 - self.y ** 2)


class Sigmoid:
    params = []
    def forward(self, x, train=True):
        self.y = 0.5 * (1 + np.tanh(0.5 * x))
        return self.y
    def backward(self, g):
        self.grads = []
        return g * self.y * (1 - self.y)


class BatchNorm:
    """Normalise each feature over the batch, then scale by gamma and shift by beta (Ioffe and Szegedy 2015)."""
    def __init__(self, n, momentum=0.9, eps=1e-5):
        self.gamma, self.beta = np.ones(n), np.zeros(n)
        self.params = [self.gamma, self.beta]
        self.run_mean, self.run_var = np.zeros(n), np.ones(n)
        self.momentum, self.eps = momentum, eps

    def forward(self, x, train=True):
        if train:
            mu, var = x.mean(0), x.var(0)
            self.run_mean = self.momentum * self.run_mean + (1 - self.momentum) * mu
            self.run_var = self.momentum * self.run_var + (1 - self.momentum) * var
        else:                                   # at test time use the running averages
            mu, var = self.run_mean, self.run_var
        self.inv = 1.0 / np.sqrt(var + self.eps)
        self.xhat = (x - mu) * self.inv
        return self.gamma * self.xhat + self.beta

    def backward(self, g):
        n = len(g)
        self.grads = [(g * self.xhat).sum(0), g.sum(0)]
        gx = g * self.gamma
        # the batch mean and variance depend on every row, which gives the two correction terms
        return self.inv / n * (n * gx - gx.sum(0) - self.xhat * (gx * self.xhat).sum(0))


class LayerNorm:
    """Normalise each example over its features (Ba, Kiros and Hinton 2016)."""
    def __init__(self, n, eps=1e-5):
        self.gamma, self.beta = np.ones(n), np.zeros(n)
        self.params = [self.gamma, self.beta]
        self.eps = eps

    def forward(self, x, train=True):
        mu, var = x.mean(1, keepdims=True), x.var(1, keepdims=True)
        self.inv = 1.0 / np.sqrt(var + self.eps)
        self.xhat = (x - mu) * self.inv
        return self.gamma * self.xhat + self.beta

    def backward(self, g):
        d = g.shape[1]
        self.grads = [(g * self.xhat).sum(0), g.sum(0)]
        gx = g * self.gamma
        return self.inv / d * (d * gx - gx.sum(1, keepdims=True) - self.xhat * (gx * self.xhat).sum(1, keepdims=True))


class Dropout:
    """Inverted dropout: in training, zero each unit with probability p and scale the rest by 1/(1-p)."""
    params = []
    def __init__(self, p, rng):
        self.p, self.rng = p, rng
    def forward(self, x, train=True):
        if not train or self.p == 0:
            self.mask = np.ones_like(x)
            return x
        self.mask = (self.rng.random(x.shape) >= self.p) / (1 - self.p)
        return x * self.mask
    def backward(self, g):
        self.grads = []
        return g * self.mask


class Sequential:
    def __init__(self, *layers):
        self.layers = list(layers)
        self.params = [p for l in self.layers for p in l.params]
    def forward(self, x, train=True):
        for l in self.layers:
            x = l.forward(x, train)
        return x
    def backward(self, g):
        for l in reversed(self.layers):
            g = l.backward(g)
        self.grads = [q for l in self.layers for q in l.grads]
        return g


class Residual:
    """y = x + F(x): the gradient reaches x directly, plus through F (He et al. 2016)."""
    def __init__(self, block):
        self.block = block
        self.params = block.params
    def forward(self, x, train=True):
        return x + self.block.forward(x, train)
    def backward(self, g):
        gx = g + self.block.backward(g)
        self.grads = self.block.grads
        return gx


def softmax_cross_entropy(scores, y):
    """Mean cross-entropy of integer labels y, and its gradient with respect to the scores (p - onehot)/n."""
    s = scores - scores.max(1, keepdims=True)
    logp = s - np.log(np.exp(s).sum(1, keepdims=True))
    n = len(y)
    g = np.exp(logp)
    g[np.arange(n), y] -= 1
    return -logp[np.arange(n), y].mean(), g / n


class AdamW:
    """Adam (Kingma and Ba 2014) with decoupled weight decay (Loshchilov and Hutter 2019)."""
    def __init__(self, params, lr=1e-3, weight_decay=0.0, b1=0.9, b2=0.999, eps=1e-8):
        self.params, self.lr, self.wd = params, lr, weight_decay
        self.b1, self.b2, self.eps, self.t = b1, b2, eps, 0
        self.m = [np.zeros_like(p) for p in params]
        self.v = [np.zeros_like(p) for p in params]
    def step(self, grads):
        self.t += 1
        for p, g, m, v in zip(self.params, grads, self.m, self.v):
            m *= self.b1; m += (1 - self.b1) * g
            v *= self.b2; v += (1 - self.b2) * g * g
            mh, vh = m / (1 - self.b1 ** self.t), v / (1 - self.b2 ** self.t)
            if self.wd and p.ndim == 2:            # decay weight matrices, not biases or norm parameters
                p -= self.lr * self.wd * p
            p -= self.lr * mh / (np.sqrt(vh) + self.eps)


def clip_grad_norm(grads, max_norm):
    """Scale all gradients together so that their combined length is at most max_norm."""
    total = np.sqrt(sum((g ** 2).sum() for g in grads))
    if total > max_norm:
        for g in grads:
            g *= max_norm / total
    return total


def grad_check(layer, x, rng, h=1e-6):
    """Compare backward() with central differences of a random linear function of the output."""
    r = rng.normal(size=layer.forward(x).shape)
    f = lambda: (layer.forward(x) * r).sum()
    f()
    gx = layer.backward(r)
    worst = 0.0
    for arr, g in [(x, gx)] + list(zip(layer.params, layer.grads)):
        for idx in np.ndindex(arr.shape):
            old = arr[idx]
            arr[idx] = old + h; up = f()
            arr[idx] = old - h; down = f()
            arr[idx] = old
            worst = max(worst, abs((up - down) / (2 * h) - g[idx]))
    return worst


if __name__ == "__main__":
    rng = np.random.default_rng(0)
    x = rng.normal(size=(6, 4))
    tests = {
        "Linear": Linear(4, 3, rng),
        "ReLU": ReLU(),
        "Tanh": Tanh(),
        "Sigmoid": Sigmoid(),
        "BatchNorm": BatchNorm(4),
        "LayerNorm": LayerNorm(4),
        "Residual(Linear-Tanh-Linear)": Residual(Sequential(Linear(4, 5, rng), Tanh(), Linear(5, 4, rng))),
    }
    print("Largest difference between backward() and finite differences:")
    for name, layer in tests.items():
        print(f"  {name:30s} {grad_check(layer, x.copy(), rng):.1e}")
    scores = rng.normal(size=(5, 3))
    y = np.array([0, 2, 1, 1, 0])
    L, g = softmax_cross_entropy(scores, y)
    num = np.zeros_like(scores)
    for idx in np.ndindex(scores.shape):
        s2 = scores.copy(); s2[idx] += 1e-6; up = softmax_cross_entropy(s2, y)[0]
        s2[idx] -= 2e-6; down = softmax_cross_entropy(s2, y)[0]
        num[idx] = (up - down) / 2e-6
    print(f"  {'softmax cross-entropy':30s} {np.abs(num - g).max():.1e}")
