"""Chapter 20: a denoising diffusion model (Ho et al. 2020) from scratch on 2-D
toy data: the forward noising process checked against its closed form, a small
MLP trained to predict the noise, and ancestral sampling back from pure noise."""
import os
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
import numpy as np

rng = np.random.default_rng(2020)

# --------------------------------------------------------------- the data
MODES = 2.0 * np.stack([np.cos(np.arange(8) * np.pi / 4), np.sin(np.arange(8) * np.pi / 4)], 1)


def data(n):
    return MODES[rng.integers(0, 8, n)] + 0.1 * rng.normal(size=(n, 2))


def quality(x):
    d = np.linalg.norm(x[:, None, :] - MODES[None], axis=2)
    near = d.min(1) < 0.3
    return near.mean(), np.bincount(d.argmin(1)[near], minlength=8)


# ---------------------------------------------------- 1. the forward process
Tn = 100
beta = np.linspace(1e-4, 0.1, Tn)                # noise added at each step
alpha = 1 - beta
abar = np.cumprod(alpha)                         # alpha-bar_t = product of alphas up to t
print(f"1. forward process: {Tn} steps, beta from {beta[0]} to {beta[-1]}; alpha-bar_T = {abar[-1]:.4f}")
x0 = data(20000)
x = x0.copy()
for t in range(Tn):                              # step by step: x_t = sqrt(a_t) x_(t-1) + sqrt(b_t) noise
    x = np.sqrt(alpha[t]) * x + np.sqrt(beta[t]) * rng.normal(size=x.shape)
    if t + 1 in (10, 50, 100):
        pred_sd = np.sqrt(abar[t] * x0.var(0).mean() + (1 - abar[t]))
        print(f"   t = {t + 1:3d}: std of x_t simulated {x.std(0).mean():.4f}, closed form {pred_sd:.4f};"
              f" corr(x_t, x_0) {np.corrcoef(x[:, 0], x0[:, 0])[0, 1]:.3f}")

# --------------------------------------------------------- the noise model
def time_features(t):
    f = np.exp(np.linspace(0, np.log(50), 8))[None, :] * (t[:, None] / Tn)
    return np.concatenate([np.sin(f), np.cos(f)], 1)            # (n, 16)


H = 64
P = {"W1": rng.normal(size=(18, H)) * np.sqrt(2 / 18), "b1": np.zeros(H),
     "W2": rng.normal(size=(H, H)) * np.sqrt(2 / H), "b2": np.zeros(H),
     "W3": rng.normal(size=(H, 2)) * np.sqrt(1 / H), "b3": np.zeros(2)}


def forward(xt, t):
    inp = np.concatenate([xt, time_features(t)], 1)
    h1 = np.maximum(inp @ P["W1"] + P["b1"], 0)
    h2 = np.maximum(h1 @ P["W2"] + P["b2"], 0)
    return h2 @ P["W3"] + P["b3"], (inp, h1, h2)


def backward(g, cache):                          # plain backprop through the MLP
    inp, h1, h2 = cache
    grads = {"W3": h2.T @ g, "b3": g.sum(0)}
    g2 = (g @ P["W3"].T) * (h2 > 0)
    grads.update(W2=h1.T @ g2, b2=g2.sum(0))
    g1 = (g2 @ P["W2"].T) * (h1 > 0)
    grads.update(W1=inp.T @ g1, b1=g1.sum(0))
    return grads


# -------------------------------------------------------------- 2. training
m = {k: np.zeros_like(v) for k, v in P.items()}; v2 = {k: np.zeros_like(v) for k, v in P.items()}
print()
print("2. train eps_theta(x_t, t) to predict the noise: loss = mean |eps - eps_theta|^2")
for step in range(1, 4001):
    x0 = data(256)
    t = rng.integers(0, Tn, 256)
    eps = rng.normal(size=x0.shape)
    xt = np.sqrt(abar[t])[:, None] * x0 + np.sqrt(1 - abar[t])[:, None] * eps   # jump straight to x_t
    pred, cache = forward(xt, t)
    loss = np.mean(np.sum((pred - eps) ** 2, 1))
    grads = backward(2 * (pred - eps) / len(x0), cache)
    lr = 2e-3 if step < 3000 else 5e-4
    for k in P:                                  # Adam
        m[k] = 0.9 * m[k] + 0.1 * grads[k]; v2[k] = 0.999 * v2[k] + 0.001 * grads[k] ** 2
        P[k] -= lr * (m[k] / (1 - 0.9 ** step)) / (np.sqrt(v2[k] / (1 - 0.999 ** step)) + 1e-8)
    if step in (1, 1000, 2000, 4000):
        print(f"   step {step:4d}: loss {loss:.3f}   (predicting 0 would give 2.0)")

# -------------------------------------------------------------- 3. sampling
def sample(n):
    x = rng.normal(size=(n, 2))                  # start from pure noise, x_T ~ N(0, I)
    for t in range(Tn - 1, -1, -1):
        eps_hat, _ = forward(x, np.full(n, t))
        mean = (x - beta[t] / np.sqrt(1 - abar[t]) * eps_hat) / np.sqrt(alpha[t])
        x = mean + (np.sqrt(beta[t]) * rng.normal(size=x.shape) if t > 0 else 0)
    return x


print()
print("3. ancestral sampling from x_T ~ N(0, I) back to x_0")
for name, xs in [("pure noise N(0, I)", rng.normal(size=(2000, 2))),
                 ("diffusion samples", sample(2000)), ("real data", data(2000))]:
    frac, per_mode = quality(xs)
    print(f"   {name:19s}: within 0.3 of a mode {frac:.3f}; per mode {per_mode.tolist()}")
