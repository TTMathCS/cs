"""Chapter 16: practical checks and tools. The loss at initialisation, overfitting one batch, a learning-rate
range test, warmup with cosine decay, and gradient clipping."""
import os
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")   # small matrices: one thread is faster than many
import numpy as np
from ch16_nn import Linear, ReLU, Sequential, AdamW, softmax_cross_entropy, clip_grad_norm
from ch15_mlp_spirals import spirals


def mlp(rng, sizes, init="he", last_std=None):
    layers = []
    for i, (a, b) in enumerate(zip(sizes, sizes[1:])):
        std = last_std if (last_std is not None and i == len(sizes) - 2) else init
        layers += [Linear(a, b, rng, std), ReLU()]
    return Sequential(*layers[:-1])                     # no ReLU after the last layer


def warmup_cosine(t, total, peak, warmup):
    if t < warmup:
        return peak * (t + 1) / warmup
    return 0.5 * peak * (1 + np.cos(np.pi * (t - warmup) / (total - warmup)))


if __name__ == "__main__":
    rng = np.random.default_rng(0)
    X = rng.normal(size=(512, 20))
    y = rng.integers(0, 3, 512)

    print("1. Loss at initialisation, 3 classes (it should be close to ln 3 = %.4f)" % np.log(3))
    for name, last in (("last layer std 0.01", 0.01), ("last layer He", None), ("last layer std 10", 10.0)):
        net = mlp(np.random.default_rng(1), [20, 64, 64, 3], last_std=last)
        print(f"  {name:20s}: {softmax_cross_entropy(net.forward(X), y)[0]:.4f}")

    print("\n2. Overfit one batch: 8 examples with random labels must reach loss near 0")
    net = mlp(np.random.default_rng(2), [20, 64, 64, 3])
    opt = AdamW(net.params, lr=1e-2)
    for t in range(1, 201):
        loss, g = softmax_cross_entropy(net.forward(X[:8]), y[:8])
        net.backward(g)
        opt.step(net.grads)
        if t in (1, 25, 50, 100, 200):
            print(f"  step {t:3d}: loss {loss:.5f}")

    print("\n3. Learning-rate range test on the spirals: raise the rate from 1e-5 to 10 over 300 steps")
    Xs, ys = spirals(200, 0.03, np.random.default_rng(1))
    ys = ys.astype(int)
    net = mlp(np.random.default_rng(3), [2, 64, 64, 2])
    opt = AdamW(net.params)
    r = np.random.default_rng(4)
    smooth, rows = None, []
    for t in range(300):
        opt.lr = 1e-5 * (1e6) ** (t / 299)
        idx = r.choice(len(Xs), 64, replace=False)
        loss, g = softmax_cross_entropy(net.forward(Xs[idx]), ys[idx])
        smooth = loss if smooth is None else 0.9 * smooth + 0.1 * loss   # smoothed, as in practice
        rows.append((opt.lr, smooth))
        net.backward(g)
        opt.step(net.grads)
    for lr, s in rows[::25] + [rows[-1]]:
        print(f"  learning rate {lr:9.2e}: smoothed loss {s:.4f}")

    print("\n4. Warmup for 100 steps to 0.003, then cosine decay to 0 at step 1000")
    print("  " + "  ".join(f"t={t}: {warmup_cosine(t, 1000, 3e-3, 100):.2e}" for t in (0, 50, 99, 100, 300, 550, 800, 999)))

    print("\n5. Gradient clipping: a badly initialised 10-layer ReLU net (std 0.5), plain gradient descent, rate 0.01")
    Xc, yc = Xs, ys
    for clip in (None, 1.0):
        net = mlp(np.random.default_rng(5), [2] + [32] * 10 + [2], init=0.5)
        out = []
        with np.errstate(all="ignore"):
            for t in range(1, 201):
                loss, g = softmax_cross_entropy(net.forward(Xc), yc)
                net.backward(g)
                norm = clip_grad_norm(net.grads, clip) if clip else np.sqrt(sum((q ** 2).sum() for q in net.grads))
                for p, q in zip(net.params, net.grads):
                    p -= 0.01 * q
                if t in (1, 2, 3, 5, 50, 200):
                    out.append(f"step {t}: loss {loss:.3g}, grad norm {norm:.2g}")
        print(f"  {'no clipping' if clip is None else 'clip at 1.0'}: " + "; ".join(out))
