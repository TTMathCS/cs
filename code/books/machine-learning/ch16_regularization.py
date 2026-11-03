"""Chapter 16: regularising a network that is too big for its data: weight decay, dropout, augmentation."""
import os
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")   # small matrices: one thread is faster than many
import numpy as np
from ch16_nn import Linear, ReLU, Dropout, Sequential, AdamW, softmax_cross_entropy
from ch15_mlp_spirals import spirals


def make_net(rng, p_drop):
    return Sequential(Linear(2, 64, rng), ReLU(), Dropout(p_drop, rng),
                      Linear(64, 64, rng), ReLU(), Dropout(p_drop, rng),
                      Linear(64, 2, rng))


def run(X, y, Xt, yt, weight_decay=0.0, p_drop=0.0, jitter=0.0, steps=1000, seed=0):
    rng = np.random.default_rng(seed)
    net = make_net(rng, p_drop)
    opt = AdamW(net.params, lr=3e-3, weight_decay=weight_decay)
    for _ in range(steps):
        Xb = X + jitter * rng.normal(size=X.shape)     # augmentation: a slightly moved copy each step
        loss, g = softmax_cross_entropy(net.forward(Xb), y)
        net.backward(g)
        opt.step(net.grads)
    acc = lambda A, b: (net.forward(A, train=False).argmax(1) == b).mean()
    return acc(X, y), acc(Xt, yt), np.sqrt(sum((p ** 2).sum() for p in net.params if p.ndim == 2))


if __name__ == "__main__":
    rng = np.random.default_rng(7)
    X, y = spirals(40, 0.08, rng, turns=3)              # only 80 noisy training points
    Xt, yt = spirals(1000, 0.08, rng, turns=3)          # 2000 test points from the same spirals
    y, yt = y.astype(int), yt.astype(int)
    print("2-64-64-2 network (4482 parameters), 80 training points, 2000 test points, 1000 steps of Adam")
    print("averages over 2 random initialisations")
    print("                               train acc   test acc   weight norm")
    for name, kw in (("no regularisation", {}),
                     ("weight decay 0.1", {"weight_decay": 0.1}),
                     ("dropout p = 0.3", {"p_drop": 0.3}),
                     ("augmentation (jitter 0.05)", {"jitter": 0.05}),
                     ("all three", {"weight_decay": 0.1, "p_drop": 0.3, "jitter": 0.05})):
        tr, te, wn = np.mean([run(X, y, Xt, yt, seed=s, **kw) for s in (0, 1)], axis=0)
        print(f"  {name:28s} {tr:9.3f}   {te:8.3f}   {wn:11.2f}")
