# Chapter 21: learning from little data and learning without forgetting.
# (1) Few-shot regression: a new task with 3 examples, with and without a prior learned from 50 earlier
#     related tasks (hierarchical Bayes in its simplest form: "learning to learn").
# (2) Catastrophic forgetting: a small network learns task A, then task B; accuracy on A collapses.
#     Two remedies: rehearsal (replay a few stored A examples) and EWC (Kirkpatrick et al. 2017).
import os
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
import numpy as np

rng = np.random.default_rng(0)

# ---------- (1) few-shot learning with a learned prior ----------
d = 8
w_family = rng.normal(0, 1, d)                        # tasks in this family share most of their weights
def new_task():
    return w_family + rng.normal(0, 0.2, d)
earlier = []
for _ in range(50):                                   # 50 earlier tasks, 40 examples each, fitted by least squares
    w = new_task(); X = rng.normal(0, 1, (40, d)); y = X @ w + rng.normal(0, 0.3, 40)
    earlier.append(np.linalg.lstsq(X, y, rcond=None)[0])
earlier = np.array(earlier)
mu, tau2 = earlier.mean(0), max(earlier.var(0).mean(), 1e-3)   # learned prior: N(mu, tau2 I)
errs = {"no prior (least norm)": [], "ridge towards 0": [], "learned prior": []}
for _ in range(500):
    w = new_task(); X = rng.normal(0, 1, (3, d)); y = X @ w + rng.normal(0, 0.3, 3)
    Xt = rng.normal(0, 1, (500, d)); yt = Xt @ w
    lam = 0.3 ** 2 / tau2
    fits = {"no prior (least norm)": np.linalg.pinv(X) @ y,
            "ridge towards 0": np.linalg.solve(X.T @ X + lam * np.eye(d), X.T @ y),
            "learned prior": mu + np.linalg.solve(X.T @ X + lam * np.eye(d), X.T @ (y - X @ mu))}
    for k, wh in fits.items():
        errs[k].append(np.mean((Xt @ wh - yt) ** 2))
print("(1) a new task, only 3 examples for 8 unknown weights: mean squared test error over 500 tasks")
for k, v in errs.items():
    print(f"   {k:<24} {np.mean(v):7.3f}")

# ---------- (2) continual learning ----------
D_IN, H = 22, 64                                      # 20 features plus 2 bits saying which task it is
wA, wB = rng.normal(0, 1, 20), rng.normal(0, 1, 20)    # two different rules
def task(n, which):
    X = rng.normal(0, 1, (n, 20))
    w = wA if which == "A" else wB
    flag = np.tile([1.0, 0.0] if which == "A" else [0.0, 1.0], (n, 1))
    return np.column_stack([X, flag]), (X @ w > 0).astype(int)
XA, yA = task(3000, "A"); XB, yB = task(3000, "B")
XAt, yAt = task(2000, "A"); XBt, yBt = task(2000, "B")


def init():
    r = np.random.default_rng(1)
    return [r.normal(0, np.sqrt(2 / D_IN), (D_IN, H)), np.zeros(H), r.normal(0, np.sqrt(1 / H), (H, 2)), np.zeros(2)]


def forward(p, X):
    h = np.maximum(X @ p[0] + p[1], 0)
    z = h @ p[2] + p[3]; z -= z.max(1, keepdims=True); P = np.exp(z); P /= P.sum(1, keepdims=True)
    return h, P


def grad(p, X, y):
    h, P = forward(p, X)
    G = P.copy(); G[np.arange(len(y)), y] -= 1; G /= len(y)
    dh = (G @ p[2].T) * (h > 0)
    return [X.T @ dh, dh.sum(0), h.T @ G, G.sum(0)]


def train(p, X, y, epochs=20, anchor=None, fisher=None, lam=0.0, replay=None):
    r = np.random.default_rng(2)
    for _ in range(epochs):
        for idx in np.array_split(r.permutation(len(X)), 30):
            Xb, yb = X[idx], y[idx]
            if replay is not None:                    # mix in a few stored examples of the old task
                j = r.integers(0, len(replay[0]), 20)
                Xb, yb = np.vstack([Xb, replay[0][j]]), np.r_[yb, replay[1][j]]
            g = grad(p, Xb, yb)
            if fisher is not None:                    # EWC: pull important weights back to their old values
                g = [gi + lam * F * (pi - ai) for gi, F, pi, ai in zip(g, fisher, p, anchor)]
            p = [pi - 0.1 * gi for pi, gi in zip(p, g)]
    return p


acc = lambda p, X, y: np.mean(forward(p, X)[1].argmax(1) == y)
pA = train(init(), XA, yA)
# diagonal Fisher information on task A: average squared gradient of the log-likelihood per example
fisher = [np.zeros_like(q) for q in pA]
for i in range(0, 600):
    g = grad(pA, XA[i:i + 1], yA[i:i + 1])
    fisher = [F + gi ** 2 / 600 for F, gi in zip(fisher, g)]
print("\n(2) task A, then task B (a different rule; an input bit says which task); test accuracy")
print("   method                         on A after A   on A after B   on B after B")
runs = {"plain sequential training": train(pA, XB, yB),
        "rehearsal (100 stored A items)": train(pA, XB, yB, replay=(XA[:100], yA[:100])),
        "EWC, lambda 20": train(pA, XB, yB, anchor=pA, fisher=fisher, lam=20.0),
        "EWC, lambda 200": train(pA, XB, yB, anchor=pA, fisher=fisher, lam=200.0)}
for k, p in runs.items():
    print(f"   {k:<30}    {acc(pA, XAt, yAt):.3f}          {acc(p, XAt, yAt):.3f}          {acc(p, XBt, yBt):.3f}")
pJ = train(init(), np.vstack([XA, XB]), np.r_[yA, yB])
print(f"   {'both tasks together (reference)':<30}      -            {acc(pJ, XAt, yAt):.3f}          {acc(pJ, XBt, yBt):.3f}")
