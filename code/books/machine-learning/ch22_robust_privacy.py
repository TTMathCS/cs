"""Chapter 22: adversarial examples with FGSM on logistic regression, and
adversarial training; then privacy: randomized response, the Laplace
mechanism, and federated averaging."""
import os
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")   # small matrices: one thread is fastest

import numpy as np


def sigmoid(z):
    return 1.0 / (1.0 + np.exp(-np.clip(z, -30, 30)))


def train_logreg(X, y, lr=0.5, steps=300, lam=1e-3, attack_eps=0.0):
    """Gradient descent on the logistic loss, labels y in {-1, +1}.
    With attack_eps > 0, every step trains on the FGSM versions of the data,
    x - eps * y * sign(w). For a linear model we never need to build them:
    their scores are y(w.x + b) - eps * ||w||_1, and the gradient picks up
    an extra -eps * sign(w) * sum(g * y)."""
    n, d = X.shape
    w, b = np.zeros(d), 0.0
    for _ in range(steps):
        m = y * (X @ w + b) - attack_eps * np.abs(w).sum()
        g = -y * sigmoid(-m)                          # d loss / d score
        grad_w = X.T @ g / n - attack_eps * np.sign(w) * np.sum(g * y) / n
        w -= lr * (grad_w + lam * w)
        b -= lr * g.mean()
    return w, b


def fgsm(X, y, w, eps):
    """Fast gradient sign method: x + eps * sign(grad_x loss). For logistic
    loss the input gradient is -y * sigmoid(-y(w.x+b)) * w, whose sign is -y sign(w)."""
    return X - eps * y[:, None] * np.sign(w)[None, :]


def acc(X, y, w, b):
    return np.mean(np.sign(X @ w + b) == y)

rng = np.random.default_rng(2014)
print("1. FGSM on logistic regression: d weak features, each shifted by +/- 0.1 between classes")
print("        d   clean acc   acc at eps=0.02   eps=0.05   eps=0.10   eps * ||w||_1 at 0.05")
for d in [10, 100, 1000]:
    n = 2000
    y = rng.choice([-1.0, 1.0], size=n)
    X = rng.normal(size=(n, d)) + 0.1 * y[:, None]
    yt = rng.choice([-1.0, 1.0], size=n)
    Xt = rng.normal(size=(n, d)) + 0.1 * yt[:, None]
    w, b = train_logreg(X, y)
    accs = [acc(fgsm(Xt, yt, w, e), yt, w, b) for e in (0.02, 0.05, 0.10)]
    print(f"   {d:6d}   {acc(Xt, yt, w, b):9.3f}   {accs[0]:15.3f}   {accs[1]:8.3f}   {accs[2]:8.3f}"
          f"   {0.05 * np.abs(w).sum():8.2f}")

print("\n2. one robust feature (2y + noise) plus 1000 weak ones (0.1y + noise); train with and without attacks")
def make(n):
    y = rng.choice([-1.0, 1.0], size=n)
    X = np.hstack([2 * y[:, None] + rng.normal(size=(n, 1)),
                   0.1 * y[:, None] + rng.normal(size=(n, 1000))])
    return X, y
X, y = make(2000); Xt, yt = make(2000)
w, b = train_logreg(X, y)
wa, ba = train_logreg(X, y, attack_eps=0.1)
print("   training        acc at eps = 0     0.05     0.10     0.20    weight on robust   ||w_weak||_1")
for name, (ww, bb) in [("standard   ", (w, b)), ("adversarial", (wa, ba))]:
    accs = "   ".join(f"{acc(fgsm(Xt, yt, ww, e), yt, ww, bb):.3f}" for e in (0.0, 0.05, 0.10, 0.20))
    print(f"   {name}          {accs}   {ww[0]:12.2f}   {np.abs(ww[1:]).sum():12.1f}")

# ------------------------------------------------------------- privacy
print("\n3. randomized response: each person tells the truth with probability 3/4, else flips")
true_share = 0.30
for n in [1000, 10000, 100000]:
    errs = []
    for rep in range(200):
        truth = rng.random(n) < true_share
        honest = rng.random(n) < 0.75
        answer = np.where(honest, truth, ~truth)
        est = (answer.mean() - 0.25) / 0.5            # invert P(yes) = 0.25 + 0.5 * share
        errs.append(est - true_share)
    print(f"   n = {n:6d}: estimate error  mean {np.mean(errs):+.4f}   std {np.std(errs):.4f}"
          f"   (epsilon = ln 3 = {np.log(3):.3f})")

print("\n4. Laplace mechanism for the mean of n values clipped to [0, 1]: noise scale 1 / (n eps)")
vals = rng.random(10000) ** 2                          # some private numbers in [0, 1]
for eps in [0.1, 1.0, 10.0]:
    for n in [100, 10000]:
        sample = vals[:n]
        noisy = sample.mean() + rng.laplace(scale=1.0 / (n * eps), size=2000)
        print(f"   eps = {eps:5.1f}, n = {n:6d}: true mean {sample.mean():.4f}, "
              f"typical error {np.mean(np.abs(noisy - sample.mean())):.5f}")

print("\n5. federated averaging: 5 clients, each holding a skewed slice of the data")
d = 5
w_star = np.array([1.0, -2.0, 0.5, 0.0, 1.5])
clients = []
for c in range(5):
    Xc = rng.normal(size=(400, d)) + 1.5 * np.eye(d)[c]     # each client sees a shifted region
    yc = np.where(rng.random(400) < sigmoid(Xc @ w_star), 1.0, -1.0)
    clients.append((Xc, yc))
Xall = np.vstack([c[0] for c in clients]); yall = np.concatenate([c[1] for c in clients])
w_central = np.zeros(d)                                    # Newton's method on the pooled data
for _ in range(30):
    pr = sigmoid(yall * (Xall @ w_central))
    grad = -Xall.T @ (yall * (1 - pr)) / len(yall)
    hess = (Xall * (pr * (1 - pr))[:, None]).T @ Xall / len(yall)
    w_central -= np.linalg.solve(hess, grad)

def local_steps(w, Xc, yc, steps, lr=0.5):
    w = w.copy()
    for _ in range(steps):
        g = -yc * sigmoid(-yc * (Xc @ w))
        w -= lr * Xc.T @ g / len(yc)
    return w

def loss(w):
    return np.mean(np.log1p(np.exp(-yall * (Xall @ w))))

print(f"   central training on pooled data: loss {loss(w_central):.4f}")
print("   rounds   FedAvg (5 local steps)   one step per round")
w_fed, w_sgd = np.zeros(d), np.zeros(d)
for rnd in range(1, 51):
    w_fed = np.mean([local_steps(w_fed, Xc, yc, 5) for Xc, yc in clients], axis=0)
    w_sgd = np.mean([local_steps(w_sgd, Xc, yc, 1) for Xc, yc in clients], axis=0)
    if rnd in (1, 5, 10, 50):
        print(f"   {rnd:6d}   {loss(w_fed):22.4f}   {loss(w_sgd):18.4f}")
print(f"   distance of FedAvg weights from central weights: {np.linalg.norm(w_fed - w_central):.4f}")
