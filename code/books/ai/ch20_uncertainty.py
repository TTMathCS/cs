# Chapter 20: knowing when you don't know. A small network on three overlapping classes:
# calibration (ECE) and temperature scaling (Guo et al. 2017), split conformal prediction sets
# (Vovk et al. 2005), and out-of-distribution detection with two scores.
import os
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
import numpy as np

rng = np.random.default_rng(0)
CENTRES = np.array([[0.0, 0.0], [2.0, 0.0], [1.0, 1.7]])


def data(n):
    y = rng.integers(0, 3, n)
    return CENTRES[y] + rng.normal(0, 0.8, (n, 2)), y


def softmax(z):
    z = z - z.max(1, keepdims=True); e = np.exp(z); return e / e.sum(1, keepdims=True)


Xtr, ytr = data(100); Xval, yval = data(1000); Xte, yte = data(3000)

# a 2-64-3 ReLU network, trained far too long on 100 points with no regularisation
W1 = rng.normal(0, 1, (2, 64)); b1 = np.zeros(64); W2 = rng.normal(0, 0.1, (64, 3)); b2 = np.zeros(3)
def logits(X):
    return np.maximum(X @ W1 + b1, 0) @ W2 + b2
for step in range(20000):
    H = np.maximum(Xtr @ W1 + b1, 0)
    P = softmax(H @ W2 + b2); D = P.copy(); D[np.arange(len(ytr)), ytr] -= 1; D /= len(ytr)
    dH = (D @ W2.T) * (H > 0)
    W2 -= 0.1 * H.T @ D; b2 -= 0.1 * D.sum(0); W1 -= 0.1 * Xtr.T @ dH; b1 -= 0.1 * dH.sum(0)


def nll(P, y): return -np.mean(np.log(P[np.arange(len(y)), y] + 1e-12))


def ece(P, y, bins=10):
    conf, pred = P.max(1), P.argmax(1)
    e = 0.0
    for lo in np.linspace(0, 1, bins, endpoint=False):
        m = (conf > lo) & (conf <= lo + 1 / bins)
        if m.any():
            e += m.mean() * abs(conf[m].mean() - (pred[m] == y[m]).mean())
    return e


Zval, Zte = logits(Xval), logits(Xte)
print(f"train accuracy {np.mean(logits(Xtr).argmax(1) == ytr):.3f}, test accuracy {np.mean(Zte.argmax(1) == yte):.3f}")
Ts = np.arange(0.5, 8.01, 0.05)
T = Ts[np.argmin([nll(softmax(Zval / t), yval) for t in Ts])]
for name, P in (("raw softmax", softmax(Zte)), (f"temperature T = {T:.2f}", softmax(Zte / T))):
    print(f"   {name:<20} mean confidence {P.max(1).mean():.3f}   NLL {nll(P, yte):.3f}   ECE {ece(P, yte):.3f}")

print("\nreliability table for the raw softmax (test set)")
P = softmax(Zte); conf, ok = P.max(1), P.argmax(1) == yte
for lo, hi in ((0.3, 0.6), (0.6, 0.8), (0.8, 0.95), (0.95, 0.99), (0.99, 1.0)):
    m = (conf > lo) & (conf <= hi)
    print(f"   confidence in ({lo:.2f}, {hi:.2f}]: {m.sum():>4} points, mean confidence {conf[m].mean():.3f},"
          f" accuracy {ok[m].mean():.3f}")

# Split conformal prediction: calibrate on the validation set, promise 90% coverage.
alpha = 0.1
Pval, Pte = softmax(Zval / T), softmax(Zte / T)
scores = 1 - Pval[np.arange(len(yval)), yval]                 # nonconformity: 1 - prob of the true class
n = len(scores)
qhat = np.sort(scores)[int(np.ceil((n + 1) * (1 - alpha))) - 1]
sets = (1 - Pte) <= qhat
cover = sets[np.arange(len(yte)), yte]
print(f"\nconformal sets, alpha = {alpha}: threshold {qhat:.3f}, coverage {cover.mean():.3f}, "
      f"mean set size {sets.sum(1).mean():.2f}")
for size in (1, 2, 3):
    m = sets.sum(1) == size
    print(f"   sets of size {size}: {m.mean():.3f} of test points, coverage among them {cover[m].mean():.3f}")

# Out-of-distribution inputs: points from a region the network never saw.
Xood = rng.normal([6.0, -4.0], 0.5, (3000, 2))
def auroc(s_in, s_out):          # probability that a random OOD point scores higher than an in-distribution one
    s = np.r_[s_in, s_out]; r = s.argsort().argsort() + 1
    return (r[len(s_in):].sum() - len(s_out) * (len(s_out) + 1) / 2) / (len(s_in) * len(s_out))
msp_in, msp_out = 1 - softmax(Zte / T).max(1), 1 - softmax(logits(Xood) / T).max(1)
dist = lambda X: np.sqrt(((X[:, None, :] - Xtr[None, :, :]) ** 2).sum(-1)).min(1)
print(f"\nOOD detection (3000 test points vs 3000 points near (6, -4)), AUROC, 1.0 = perfect, 0.5 = chance")
print(f"   score 1 - max softmax:              {auroc(msp_in, msp_out):.3f}"
      f"   (mean max softmax on OOD points {1 - msp_out.mean():.3f})")
print(f"   distance to nearest training point: {auroc(dist(Xte), dist(Xood)):.3f}")
print("\nconfidence far from the data, along the ray t * (1, -1):")
for t in (1, 3, 10, 100, 1000):
    p = softmax(logits(np.array([[t, -t]])) / T)[0]
    print(f"   t = {t:>4}: max softmax {p.max():.6f}")
