"""Chapter 23: contrastive self-supervised learning from scratch.
A linear encoder trained with the InfoNCE loss on pairs of augmented views,
compared with PCA and raw inputs by a linear probe that sees few labels."""
import numpy as np

rng = np.random.default_rng(2020)
d_content, d_style, k_classes = 4, 28, 4
d = d_content + d_style
centers = rng.normal(size=(k_classes, d_content)) * 1.5
Q, _ = np.linalg.qr(rng.normal(size=(d, d)))          # mix content and style coordinates

def sample(n):
    c = rng.integers(0, k_classes, size=n)
    content = centers[c] + 0.4 * rng.normal(size=(n, d_content))
    style = 3.0 * rng.normal(size=(n, d_style))       # large, label-free variation
    return np.hstack([content, style]) @ Q.T, c, content

def augment(x):
    """A new 'view': same content, fresh style (and a little noise)."""
    n = len(x)
    raw = x @ Q
    raw[:, d_content:] = 3.0 * rng.normal(size=(n, d_style))
    raw[:, :d_content] += 0.1 * rng.normal(size=(n, d_content))
    return raw @ Q.T

def info_nce_grad(W, X1, X2, tau=0.2):
    """InfoNCE loss and gradient for z = W x, normalised; positives on the diagonal."""
    Z1, Z2 = X1 @ W.T, X2 @ W.T
    n1, n2 = np.linalg.norm(Z1, axis=1, keepdims=True), np.linalg.norm(Z2, axis=1, keepdims=True)
    U1, U2 = Z1 / n1, Z2 / n2
    S = U1 @ U2.T / tau
    S -= S.max(axis=1, keepdims=True)
    P = np.exp(S); P /= P.sum(axis=1, keepdims=True)
    B = len(X1)
    loss = -np.mean(np.log(P[np.arange(B), np.arange(B)]))
    G = (P - np.eye(B)) / B                            # d loss / d S
    dU1, dU2 = G @ U2 / tau, G.T @ U1 / tau
    dZ1 = (dU1 - np.sum(dU1 * U1, axis=1, keepdims=True) * U1) / n1
    dZ2 = (dU2 - np.sum(dU2 * U2, axis=1, keepdims=True) * U2) / n2
    return loss, dZ1.T @ X1 + dZ2.T @ X2

def probe_accuracy(E_train, c_train, E_test, c_test):
    """Linear probe: nearest class mean in the embedding (a linear classifier)."""
    means = np.array([E_train[c_train == j].mean(axis=0) for j in range(k_classes)])
    dist = ((E_test[:, None, :] - means[None]) ** 2).sum(axis=2)
    return np.mean(dist.argmin(axis=1) == c_test)

# unlabeled pool for self-supervised training
X_pool, _, _ = sample(20000)
k_embed = 4
W = 0.1 * rng.normal(size=(k_embed, d))
W_random = W.copy()
m, v = np.zeros_like(W), np.zeros_like(W)
print("1. training a linear encoder with InfoNCE (batch 256, temperature 0.2, Adam)")
for step in range(1, 601):
    idx = rng.integers(0, len(X_pool), size=256)
    x = X_pool[idx]
    loss, g = info_nce_grad(W, augment(x), augment(x))
    m = 0.9 * m + 0.1 * g; v = 0.999 * v + 0.001 * g * g
    W -= 0.01 * (m / (1 - 0.9 ** step)) / (np.sqrt(v / (1 - 0.999 ** step)) + 1e-8)
    if step in (1, 50, 200, 600):
        print(f"   step {step:4d}: loss {loss:.3f}   (chance level ln 256 = {np.log(256):.3f})")

# where does the encoder look? fraction of its rows' energy in the content coordinates
Wr = W @ Q
print(f"   share of encoder weight on the 4 content directions: {np.sum(Wr[:, :d_content] ** 2) / np.sum(Wr ** 2):.3f}"
      f"   (random encoder: {np.sum((W_random @ Q)[:, :d_content] ** 2) / np.sum((W_random @ Q) ** 2):.3f})")

print("\n2. linear probe with only 5 labelled examples per class (20 labels), test on 4000")
X_big, c_big, C_big = sample(400)
pick = np.concatenate([np.flatnonzero(c_big == j)[:5] for j in range(k_classes)])
X_lab, c_lab = X_big[pick], c_big[pick]
X_te, c_te, C_te = sample(4000)
Xc = X_pool - X_pool.mean(axis=0)
_, _, Vt = np.linalg.svd(Xc[:5000], full_matrices=False)
P_pca = Vt[:4]
norm = lambda E: E / np.linalg.norm(E, axis=1, keepdims=True)
results = [
    ("raw input (32 numbers)", X_lab, X_te),
    ("PCA, top 4 directions", X_lab @ P_pca.T, X_te @ P_pca.T),
    ("random linear encoder", norm(X_lab @ W_random.T), norm(X_te @ W_random.T)),
    ("contrastive encoder", norm(X_lab @ W.T), norm(X_te @ W.T)),
    ("oracle: true content", C_big[pick], C_te),
]
for name, Etr, Ete in results:
    print(f"   {name:24s} accuracy {probe_accuracy(Etr, c_lab, Ete, c_te):.3f}")
