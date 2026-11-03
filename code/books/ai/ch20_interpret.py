# Chapter 20: interpretability tools from scratch on a small network.
# Integrated gradients (Sundararajan et al. 2017) with its completeness check, a model-randomisation
# sanity check (Adebayo et al. 2018), and linear probes on the hidden layer (with a warning).
import os
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
import numpy as np

rng = np.random.default_rng(0)
n, d = 2000, 5
X = rng.normal(0, 1, (n, d))
y = (X[:, 0] + 2 * X[:, 1] > 0).astype(float)          # only features 0 and 1 matter; 2, 3, 4 are noise

W1 = rng.normal(0, 0.5, (d, 32)); b1 = np.zeros(32); w2 = rng.normal(0, 0.5, 32); b2 = 0.0
def hidden(X, W1=None, b1=None):
    return np.tanh(X @ (W1 if W1 is not None else globals()["W1"]) + (b1 if b1 is not None else globals()["b1"]))
def logit(X): return hidden(X) @ w2 + b2
for step in range(1000):
    H = hidden(X); p = 1 / (1 + np.exp(-(H @ w2 + b2))); g = (p - y) / n
    dH = np.outer(g, w2) * (1 - H ** 2)
    w2 -= 1.0 * H.T @ g; b2 -= 1.0 * g.sum(); W1 -= 1.0 * X.T @ dH; b1 -= 1.0 * dH.sum(0)
print(f"training accuracy {np.mean((logit(X) > 0) == y):.3f}")


def grad_logit(X, W1, b1, w2):
    H = np.tanh(X @ W1 + b1)
    return ((1 - H ** 2) * w2) @ W1.T                    # d logit / d x, one row per input


def integrated_gradients(x, W1, b1, w2, steps=64):
    """x may be one input (shape d) or a batch (shape m, d). Baseline: the zero vector."""
    xs = np.atleast_2d(x)
    alphas = (np.arange(steps) + 0.5) / steps            # midpoint rule along the straight path
    path = (alphas[None, :, None] * xs[:, None, :]).reshape(-1, xs.shape[1])
    g = grad_logit(path, W1, b1, w2).reshape(len(xs), steps, -1).mean(1)
    out = xs * g
    return out[0] if np.ndim(x) == 1 else out


x = np.array([0.8, -0.3, 1.5, -1.0, 0.4])
ig = integrated_gradients(x, W1, b1, w2)
f = lambda z: np.tanh(z @ W1 + b1) @ w2 + b2
print("\none input:", x)
print("   gradient x input    ", np.round(x * grad_logit(x[None], W1, b1, w2)[0], 3))
print("   integrated gradients", np.round(ig, 3))
print(f"   completeness: sum of IG = {ig.sum():.4f},  f(x) - f(0) = {f(x) - f(np.zeros(d)):.4f}")

T = X[:500]
IG = integrated_gradients(T, W1, b1, w2)
print("\nmean |IG| per feature over 500 inputs:", np.round(np.abs(IG).mean(0), 3))

# Sanity check: re-randomise the weights. A faithful explanation must change; an "explanation" that
# only reflects the input (here |x|) does not, so it cannot be telling us about the model.
R1, r2 = rng.normal(0, 0.5, (d, 32)), rng.normal(0, 0.5, 32)
IGr = integrated_gradients(T, R1, b1, r2)
corr = lambda a, b: np.corrcoef(np.abs(a).ravel(), np.abs(b).ravel())[0, 1]
print(f"correlation of |IG| between trained and randomised network:   {corr(IG, IGr):.3f}")
print(f"correlation of the input-only map |x| before and after:          {corr(T, T):.3f}")

# Linear probes: can a concept be read off the hidden layer by logistic regression?
def probe(H, c, steps=800):
    Hb = np.column_stack([H, np.ones(len(H))]); w = np.zeros(Hb.shape[1])
    tr, te = slice(0, 1500), slice(1500, None)
    for _ in range(steps):
        p = 1 / (1 + np.exp(-Hb[tr] @ w)); w -= 0.5 * Hb[tr].T @ (p - c[tr]) / 1500
    return np.mean((Hb[te] @ w > 0) == c[te])
H_trained = hidden(X); H_random = np.tanh(X @ R1 + b1)
print("\nlinear probe accuracy on held-out inputs   trained net   random net")
for name, c in (("x1 > 0 (a feature the model uses)", X[:, 1] > 0),
                ("x3 > 0 (a feature the model ignores)", X[:, 3] > 0),
                ("x0 * x3 > 0 (not linear in the inputs)", X[:, 0] * X[:, 3] > 0)):
    print(f"   {name:<40} {probe(H_trained, c.astype(float)):.3f}        {probe(H_random, c.astype(float)):.3f}")
