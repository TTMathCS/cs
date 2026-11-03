# Chapter 20: adversarial examples on a small network, from scratch.
# A 2-32-32-2 ReLU network learns two interleaved half-moons; we attack it with the fast gradient
# sign method (FGSM) and projected gradient descent (PGD) in the L-infinity ball of radius eps,
# then train it adversarially (Madry et al. 2018) and attack again.
import os
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
import numpy as np


def moons(n, rng, noise=0.12):
    t = rng.random(n) * np.pi
    y = rng.integers(0, 2, n)
    x = np.where(y[:, None] == 0, np.column_stack([np.cos(t), np.sin(t)]),
                 np.column_stack([1 - np.cos(t), 0.5 - np.sin(t)]))
    return x + rng.normal(0, noise, (n, 2)), y


def init(rng, sizes=(2, 32, 32, 2)):
    return [(rng.normal(0, np.sqrt(2 / a), (a, b)), np.zeros(b)) for a, b in zip(sizes, sizes[1:])]


def forward(params, X):
    acts = [X]
    for k, (W, b) in enumerate(params):
        z = acts[-1] @ W + b
        acts.append(np.maximum(z, 0) if k < len(params) - 1 else z)
    return acts


def grads(params, X, y):
    """Cross-entropy loss; returns parameter gradients and the gradient with respect to the input."""
    acts = forward(params, X)
    z = acts[-1] - acts[-1].max(1, keepdims=True)
    p = np.exp(z); p /= p.sum(1, keepdims=True)
    d = p.copy(); d[np.arange(len(y)), y] -= 1; d /= len(y)
    gp = []
    for k in range(len(params) - 1, -1, -1):
        W, b = params[k]
        gp.append((acts[k].T @ d, d.sum(0)))
        d = d @ W.T
        if k > 0:
            d = d * (acts[k] > 0)
    return gp[::-1], d * len(y)          # input gradient per example (undo the 1/n)


def predict(params, X):
    return forward(params, X)[-1].argmax(1)


def pgd(params, X, y, eps, steps=20):
    """Projected gradient ascent on the loss inside the box |delta|_inf <= eps. steps=1 is FGSM."""
    alpha = eps if steps == 1 else 2.5 * eps / steps
    Xa = X.copy()
    for _ in range(steps):
        _, gx = grads(params, Xa, y)
        Xa = np.clip(Xa + alpha * np.sign(gx), X - eps, X + eps)
    return Xa


def train(seed=0, adversarial_eps=0.0, epochs=150):
    rng = np.random.default_rng(seed)
    X, y = moons(1000, rng)
    params = init(rng)
    m = [(np.zeros_like(W), np.zeros_like(b)) for W, b in params]
    for ep in range(epochs):
        for idx in np.array_split(rng.permutation(len(X)), 10):
            Xb, yb = X[idx], y[idx]
            if adversarial_eps > 0:                   # train on the worst case found by PGD
                Xb = pgd(params, Xb, yb, adversarial_eps, steps=7)
            g, _ = grads(params, Xb, yb)
            m = [(0.9 * mW + gW, 0.9 * mb + gb) for (mW, mb), (gW, gb) in zip(m, g)]
            params = [(W - 0.05 * mW, b - 0.05 * mb) for (W, b), (mW, mb) in zip(params, m)]
    return params


if __name__ == "__main__":
    rng = np.random.default_rng(42)
    Xte, yte = moons(1000, rng)
    for label, eps_train in (("standard training", 0.0), ("adversarial training, eps 0.1", 0.1)):
        params = train(adversarial_eps=eps_train)
        print(f"{label}: clean test accuracy {np.mean(predict(params, Xte) == yte):.3f}")
        print("    eps    FGSM acc   PGD-20 acc")
        for eps in (0.02, 0.05, 0.1, 0.15, 0.2):
            a1 = np.mean(predict(params, pgd(params, Xte, yte, eps, steps=1)) == yte)
            a20 = np.mean(predict(params, pgd(params, Xte, yte, eps, steps=20)) == yte)
            print(f"   {eps:4.2f}     {a1:.3f}      {a20:.3f}")
        print()
    params = train()
    flipped = np.nonzero(predict(params, pgd(params, Xte, yte, 0.1)) != yte)[0]
    k = int(flipped[0])                                  # the first test point that PGD manages to flip
    x0, y0 = Xte[k:k + 1], yte[k:k + 1]
    xa = pgd(params, x0, y0, 0.1)
    print(f"test point {k}:", np.round(x0[0], 3), "label", y0[0], "predicted", predict(params, x0)[0])
    print("after PGD, eps 0.1:", np.round(xa[0], 3), "predicted", predict(params, xa)[0],
          " change", np.round(xa[0] - x0[0], 3))
