"""Chapter 16: a 12-hidden-layer network on the two spirals of Chapter 15. Plain with Xavier initialisation
(the signal vanishes), plain with He initialisation, batch normalisation, and residual blocks."""
import os
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")   # small matrices: one thread is faster than many
import numpy as np
from ch16_nn import Linear, ReLU, BatchNorm, LayerNorm, Residual, Sequential, AdamW, softmax_cross_entropy
from ch15_mlp_spirals import spirals


def build(kind, depth, width, init, rng):
    layers = [Linear(2, width, rng, init), ReLU()]
    for _ in range(depth - 1):
        if kind == "plain":
            layers += [Linear(width, width, rng, init), ReLU()]
        elif kind == "batchnorm":
            layers += [Linear(width, width, rng, init), BatchNorm(width), ReLU()]
        elif kind == "residual":    # pre-norm block x + W2 relu(W1 LN(x)), W2 small at the start
            layers += [Residual(Sequential(LayerNorm(width), Linear(width, width, rng, init), ReLU(),
                                           Linear(width, width, rng, 0.02)))]   # branch output starts small
    layers.append(Linear(width, 2, rng, init))
    return Sequential(*layers)


def train(kind, init, X, y, Xt, yt, depth=12, width=32, steps=400, lr=3e-3, batch=64, seed=0):
    rng = np.random.default_rng(seed)
    net = build(kind, depth, width, init, rng)
    opt = AdamW(net.params, lr)
    curve = []
    for t in range(steps + 1):
        if t % 100 == 0:
            curve.append(softmax_cross_entropy(net.forward(X, train=False), y)[0])
        if t == steps:
            break
        idx = rng.choice(len(X), batch, replace=False)
        loss, g = softmax_cross_entropy(net.forward(X[idx]), y[idx])
        net.backward(g)
        opt.step(net.grads)
    acc = (net.forward(Xt, train=False).argmax(1) == yt).mean()
    return curve, acc


if __name__ == "__main__":
    rng = np.random.default_rng(1)
    X, y = spirals(200, 0.03, rng)
    Xt, yt = spirals(200, 0.03, rng)
    y, yt = y.astype(int), yt.astype(int)
    print("12 hidden layers of width 32, Adam, learning rate 0.003, batches of 64, 400 steps")
    print("training loss at step 0, 100, ..., 400, then test accuracy")
    for kind, init in (("plain", "xavier"), ("plain", "he"), ("batchnorm", "xavier"), ("residual", "xavier")):
        curve, acc = train(kind, init, X, y, Xt, yt)
        print(f"  {kind:9s} {init:6s}: " + " ".join(f"{c:.3f}" for c in curve) + f"   test accuracy {acc:.3f}")
