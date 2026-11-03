"""Chapter 23: a toy model of superposition, from
scratch: 5 features squeezed into 2 hidden dimensions, x' = ReLU(W^T W x + b),
feature i weighted by importance 0.8^i in the loss. Then a sparse
autoencoder that recovers the feature directions from the hidden activations."""
import numpy as np

n_feat, m_hidden = 5, 2
importance = 0.8 ** np.arange(n_feat)

def batch(rng, size, p_active):
    """Each feature is active with probability p_active, with a value in [0, 1]."""
    return rng.random((size, n_feat)) * (rng.random((size, n_feat)) < p_active)

def adam(params, grads, state, lr, t):
    for k in params:
        m, v = state.setdefault(k, (np.zeros_like(params[k]), np.zeros_like(params[k])))
        m = 0.9 * m + 0.1 * grads[k]; v = 0.999 * v + 0.001 * grads[k] ** 2
        state[k] = (m, v)
        params[k] -= lr * (m / (1 - 0.9 ** t)) / (np.sqrt(v / (1 - 0.999 ** t)) + 1e-8)

def train_toy(p_active, seed=0, steps=4000):
    rng = np.random.default_rng(seed)
    P = {"W": 0.3 * rng.normal(size=(m_hidden, n_feat)), "b": np.zeros(n_feat)}
    state = {}
    for t in range(1, steps + 1):
        X = batch(rng, 512, p_active)
        H = X @ P["W"].T                          # hidden activations, (B, 2)
        pre = H @ P["W"] + P["b"]
        out = np.maximum(pre, 0)
        dpre = 2 * importance * (out - X) / len(X) * (pre > 0)
        dH = dpre @ P["W"].T
        grads = {"W": H.T @ dpre + dH.T @ X, "b": dpre.sum(axis=0)}
        adam(P, grads, state, 0.01, t)
    X = batch(rng, 20000, p_active)
    loss = np.mean(np.sum(importance * (np.maximum(X @ P["W"].T @ P["W"] + P["b"], 0) - X) ** 2, axis=1))
    return P, loss

print("1. five features, two hidden dimensions: what does the model keep?")
print("   P(active)   loss    |W_i| for the 5 features           angles of the kept features (degrees)")
for p in [1.0, 0.3, 0.1, 0.03]:
    P, loss = train_toy(p)
    norms = np.linalg.norm(P["W"], axis=0)
    kept = np.flatnonzero(norms > 0.5)
    ang = np.sort(np.degrees(np.arctan2(P["W"][1, kept], P["W"][0, kept])) % 360)
    gaps = np.diff(np.append(ang, ang[0] + 360)) if len(ang) > 1 else np.array([])
    print(f"     {p:5.2f}    {loss:.4f}   {np.array2string(norms, precision=2)}   "
          f"{len(kept)} kept, gaps between them: {np.array2string(gaps, precision=0)}")

# ---------------------------------------------------- 2. sparse autoencoder
P, _ = train_toy(0.03)
rng = np.random.default_rng(1)
X = batch(rng, 30000, 0.03)
X = X[X.sum(axis=1) > 0]                          # keep inputs with something active
Hs = X @ P["W"].T                                 # the 2-D activations we want to explain
true_dirs = P["W"] / np.linalg.norm(P["W"], axis=0)   # (2, 5)

k_dict, lam = 8, 0.001                            # more dictionary features than true ones
Wd = rng.normal(size=(m_hidden, k_dict)); Wd /= np.linalg.norm(Wd, axis=0)
S = {"We": Wd.T.copy(), "be": np.zeros(k_dict), "Wd": Wd}     # encoder starts as decoder transposed
state = {}
for t in range(1, 6001):
    idx = rng.integers(0, len(Hs), size=512)
    h = Hs[idx]
    pre = h @ S["We"].T + S["be"]
    f = np.maximum(pre, 0)                        # sparse code
    rec = f @ S["Wd"].T
    dr = 2 * (rec - h) / len(h)
    df = dr @ S["Wd"] + lam * (f > 0)             # L1 penalty on the (non-negative) codes
    dpre = df * (pre > 0)
    grads = {"Wd": dr.T @ f, "We": dpre.T @ h, "be": dpre.sum(axis=0)}
    adam(S, grads, state, 0.003, t)
    S["Wd"] /= np.linalg.norm(S["Wd"], axis=0, keepdims=True)    # keep decoder columns unit length
f = np.maximum(Hs @ S["We"].T + S["be"], 0)
rec = f @ S["Wd"].T
dec_dirs = S["Wd"] / np.linalg.norm(S["Wd"], axis=0)
cos = true_dirs.T @ dec_dirs                       # (5 true, 5 learned)
print(f"\n2. sparse autoencoder on the 2-D activations ({k_dict} dictionary features, L1 penalty {lam})")
print(f"   reconstruction: fraction of variance unexplained {np.sum((rec - Hs) ** 2) / np.sum((Hs - Hs.mean(0)) ** 2):.4f}")
print(f"   average number of active dictionary features per input: {np.mean((f > 1e-6).sum(axis=1)):.2f}"
      f"   (true active features: {np.mean((X > 0).sum(axis=1)):.2f})")
print(f"   dictionary features that fire on more than 1% of inputs: {np.sum((f > 1e-6).mean(axis=0) > 0.01)} of {k_dict}")
print("   best cosine between each true feature direction and a learned one:",
      np.array2string(cos.max(axis=1), precision=3))
