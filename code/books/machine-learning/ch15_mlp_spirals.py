"""Chapter 15: an MLP in NumPy, trained from scratch on two interleaved spirals; a picture of its boundary."""
import os
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")   # small matrices: one thread is faster than many
import numpy as np


def spirals(n, noise, rng, turns=4):
    """n points per class on two spirals that wind around each other (turns half-turns each)."""
    t = np.sqrt(rng.uniform(0, 1, n)) * turns * np.pi      # more points far out, where the arms are longer
    arm = np.c_[t * np.cos(t), t * np.sin(t)] / (turns * np.pi)
    X = np.vstack([arm, -arm]) + noise * rng.normal(size=(2 * n, 2))
    return X, np.r_[np.zeros(n), np.ones(n)]


def init(sizes, rng):
    return [(rng.normal(size=(a, b)) * np.sqrt(2.0 / a), np.zeros(b)) for a, b in zip(sizes, sizes[1:])]


def forward(layers, X):
    """Returns the list of activations; ReLU between layers, a raw score (logit) at the end."""
    acts = [X]
    for i, (W, b) in enumerate(layers):
        a = acts[-1] @ W + b
        acts.append(np.maximum(a, 0) if i < len(layers) - 1 else a)
    return acts


def backward(layers, acts, y):
    """Gradients of the mean logistic loss, layer by layer from the top."""
    n = len(y)
    p = 1 / (1 + np.exp(-acts[-1][:, 0]))
    delta = ((p - y) / n)[:, None]                        # dL/d(logit)
    grads = []
    for i in reversed(range(len(layers))):
        W, b = layers[i]
        grads.append((acts[i].T @ delta, delta.sum(0)))
        if i > 0:
            delta = (delta @ W.T) * (acts[i] > 0)         # through W, then through the ReLU
    return grads[::-1]


def loss(layers, X, y):
    s = forward(layers, X)[-1][:, 0]
    return np.mean(np.logaddexp(0, s) - y * s)            # log(1 + e^s) - y s, computed stably


def train(sizes, X, y, steps, lr=0.01, seed=0):
    rng = np.random.default_rng(seed)
    layers = init(sizes, rng)
    m = [(np.zeros_like(W), np.zeros_like(b)) for W, b in layers]
    v = [(np.zeros_like(W), np.zeros_like(b)) for W, b in layers]
    history = []
    for t in range(1, steps + 1):
        grads = backward(layers, forward(layers, X), y)
        for i, ((W, b), (gW, gb)) in enumerate(zip(layers, grads)):   # Adam (Chapter 5)
            mW, mb = m[i]
            vW, vb = v[i]
            mW, mb = 0.9 * mW + 0.1 * gW, 0.9 * mb + 0.1 * gb
            vW, vb = 0.999 * vW + 0.001 * gW ** 2, 0.999 * vb + 0.001 * gb ** 2
            m[i], v[i] = (mW, mb), (vW, vb)
            c1, c2 = 1 - 0.9 ** t, 1 - 0.999 ** t
            W -= lr * (mW / c1) / (np.sqrt(vW / c2) + 1e-8)
            b -= lr * (mb / c1) / (np.sqrt(vb / c2) + 1e-8)
        if t in (1, 100, 250, 500, 1000, 1500):
            history.append((t, loss(layers, X, y)))
    return layers, history


def accuracy(layers, X, y):
    return np.mean((forward(layers, X)[-1][:, 0] > 0) == y)


def ascii_map(layers, size=24):
    xs = np.linspace(-1.2, 1.2, 2 * size)
    ys = np.linspace(1.2, -1.2, size)
    G = np.array([[x, yv] for yv in ys for x in xs])
    s = forward(layers, G)[-1][:, 0].reshape(size, 2 * size)
    return ["  " + "".join("#" if v > 0 else "." for v in row) for row in s]


if __name__ == "__main__":
    rng = np.random.default_rng(1)
    X, y = spirals(200, 0.03, rng)
    Xt, yt = spirals(200, 0.03, rng)
    print("Two spirals: 400 training points, 400 test points")
    for sizes in ([2, 1], [2, 8, 1], [2, 32, 32, 1]):
        layers, hist = train(sizes, X, y, 1500)
        params = sum(W.size + b.size for W, b in layers)
        print(f"  layers {sizes}: {params:5d} parameters, train accuracy {accuracy(layers, X, y):.3f},"
              f" test accuracy {accuracy(layers, Xt, yt):.3f}")
    print("  loss of the 2-32-32-1 network during training:",
          ", ".join(f"step {t}: {l:.4f}" for t, l in hist))
    print("\nIts decision regions on [-1.2, 1.2]^2 ('#' = class 1):")
    print("\n".join(ascii_map(layers)))
