"""Chapter 19: scaled dot-product attention from scratch. Why divide by sqrt(d),
multi-head attention, sinusoidal positions, causal masks, permutation
equivariance, and the online (tiled) softmax behind FlashAttention."""
import numpy as np

rng = np.random.default_rng(19)


def softmax(z, axis=-1):
    z = z - z.max(axis=axis, keepdims=True)
    e = np.exp(z)
    return e / e.sum(axis=axis, keepdims=True)


def attention(Q, K, V, mask=None):
    """softmax(Q K^T / sqrt(d_k)) V. Q: (n, d_k), K: (m, d_k), V: (m, d_v)."""
    scores = Q @ K.T / np.sqrt(Q.shape[-1])
    if mask is not None:
        scores = np.where(mask, scores, -np.inf)
    A = softmax(scores)
    return A @ V, A


# ------------------------------------------------------------ 1. a tiny example
print("1. three tokens, d_k = 2, by hand")
Q = np.array([[1.0, 0.0], [0.0, 1.0], [1.0, 1.0]])
K = np.array([[1.0, 0.0], [0.0, 1.0], [1.0, 1.0]])
V = np.array([[1.0, 0.0], [0.0, 2.0], [3.0, 3.0]])
out, A = attention(Q, K, V)
print("   scores Q K^T / sqrt 2 =\n" + "\n".join("      " + " ".join(f"{v:6.3f}" for v in r)
                                           for r in Q @ K.T / np.sqrt(2)))
print("   weights (rows sum to 1) =\n" + "\n".join("      " + " ".join(f"{v:6.3f}" for v in r) for r in A))
print("   output =\n" + "\n".join("      " + " ".join(f"{v:6.3f}" for v in r) for r in out))

# ----------------------------------------------------- 2. why divide by sqrt(d)
print()
print("2. random q, k with unit-variance entries, 16 keys: what the softmax sees")
print(f"   {'d':>5s}{'var(q.k)':>10s}{'max weight':>12s}{'(scaled)':>10s}{'grad size':>11s}{'(scaled)':>10s}")
for d in (4, 64, 512):
    q = rng.normal(size=(2000, d)); k = rng.normal(size=(2000, 16, d))
    s = np.einsum("nd,nkd->nk", q, k)
    rows = []
    for scale in (1.0, np.sqrt(d)):
        a = softmax(s / scale)
        # size of the softmax Jacobian, diag(a) - a a^T, averaged over rows
        J = np.einsum("nk,kl->nkl", a, np.eye(16)) - np.einsum("nk,nl->nkl", a, a)
        rows.append((a.max(1).mean(), np.linalg.norm(J, axis=(1, 2)).mean()))
    print(f"   {d:5d}{s.var():10.1f}{rows[0][0]:12.3f}{rows[1][0]:10.3f}{rows[0][1]:11.4f}{rows[1][1]:10.4f}")

# -------------------------------------------------------------- 3. multi-head
print()
print("3. multi-head attention: h heads of size d/h cost about the same as one of size d")
n, d, h = 6, 8, 2
X = rng.normal(size=(n, d))
Wq, Wk, Wv, Wo = (rng.normal(size=(d, d)) / np.sqrt(d) for _ in range(4))


def multi_head(X, h, mask=None):
    dk = d // h
    Q, K, V = X @ Wq, X @ Wk, X @ Wv
    heads, maps = [], []
    for i in range(h):
        sl = slice(i * dk, (i + 1) * dk)          # each head uses its own slice
        o, a = attention(Q[:, sl], K[:, sl], V[:, sl], mask)
        heads.append(o); maps.append(a)
    return np.concatenate(heads, axis=1) @ Wo, maps


Y, maps = multi_head(X, h)
print(f"   input {X.shape}, output {Y.shape}, {h} attention maps of shape {maps[0].shape}")
print(f"   weights: 4 d^2 = {4 * d * d} whatever h is")
print(f"   head 0 row 0: {np.round(maps[0][0], 3)}")
print(f"   head 1 row 0: {np.round(maps[1][0], 3)}   (different heads look at different places)")

# ----------------------------------------------- 4. permutation equivariance
P = rng.permutation(n)
Yp, _ = multi_head(X[P], h)
print()
print("4. without positions, attention ignores order: f(X permuted) == f(X) permuted?",
      np.allclose(Yp, Y[P]))

# ------------------------------------------------------- 5. sinusoidal positions
def sinusoid(n, d):
    pos = np.arange(n)[:, None]
    i = np.arange(d // 2)[None, :]
    angle = pos / 10000 ** (2 * i / d)
    pe = np.zeros((n, d))
    pe[:, 0::2], pe[:, 1::2] = np.sin(angle), np.cos(angle)
    return pe


pe = sinusoid(50, 16)
k = 7
# PE(pos + k) = R_k PE(pos) for a fixed block-rotation matrix R_k
R = np.zeros((16, 16))
for i in range(8):
    w = k / 10000 ** (2 * i / 16)
    c, s = np.cos(w), np.sin(w)
    R[2 * i:2 * i + 2, 2 * i:2 * i + 2] = [[c, s], [-s, c]]
print()
print("5. sinusoidal positions, d = 16")
print(f"   PE(0)[:4] = {np.round(pe[0, :4], 3)},  PE(1)[:4] = {np.round(pe[1, :4], 3)}")
print(f"   one rotation R_7 maps every PE(pos) to PE(pos + 7)? {np.allclose(pe[:-k] @ R.T, pe[k:])}")
dots = pe @ pe[20]
print(f"   PE(20) . PE(20 + j) for j = 0, 1, 2, 5, 10, 20: "
      + ", ".join(f"{dots[20 + j]:.2f}" for j in (0, 1, 2, 5, 10, 20)))

# ------------------------------------------------------------ 6. causal mask
mask = np.tril(np.ones((n, n), bool))            # position t may see 0..t only
Y1, m1 = multi_head(X, h, mask)
X2 = X.copy(); X2[4:] = rng.normal(size=(2, d))  # change the last two tokens
Y2, _ = multi_head(X2, h, mask)
print()
print("6. causal mask: outputs 0..3 unchanged when tokens 4, 5 change?", np.allclose(Y1[:4], Y2[:4]),
      "| output 5 changed?", not np.allclose(Y1[5], Y2[5]))
print("   head 0 weights with the mask:")
for r in m1[0]:
    print("      " + " ".join(f"{v:5.2f}" for v in r))

# ------------------------------------------------- 7. online softmax (tiles)
def attention_tiled(Q, K, V, block):
    """Exact attention reading K, V one block at a time, never storing the n x m
    score matrix: keep a running max m, running sum l and running output o."""
    n, dk = Q.shape
    m = np.full(n, -np.inf); l = np.zeros(n); o = np.zeros((n, V.shape[1]))
    for s in range(0, K.shape[0], block):
        S = Q @ K[s:s + block].T / np.sqrt(dk)      # scores for this block only
        m_new = np.maximum(m, S.max(1))
        scale = np.exp(m - m_new)                   # rescale what we had so far
        P = np.exp(S - m_new[:, None])
        l = l * scale + P.sum(1)
        o = o * scale[:, None] + P @ V[s:s + block]
        m = m_new
    return o / l[:, None]


Q, K, V = rng.normal(size=(64, 16)), rng.normal(size=(256, 16)), rng.normal(size=(256, 16))
ref, _ = attention(Q, K, V)
print()
print("7. tiled attention with an online softmax equals the usual one:")
for b in (1, 32, 100, 256):
    print(f"   block {b:3d}: max difference {np.abs(attention_tiled(Q, K, V, b) - ref).max():.1e}")
print("   memory for the score matrix, 16-bit numbers, one head:")
for n in (1024, 8192, 65536):
    print(f"   n = {n:6d}: {n * n * 2 / 2**20:10.0f} MiB")
