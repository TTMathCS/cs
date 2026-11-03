"""Chapter 23: a graph convolutional network (Kipf and Welling 2017) from
scratch for semi-supervised node classification, compared with an MLP that
ignores the graph; and a check that the GCN is permutation equivariant."""
import numpy as np

rng = np.random.default_rng(2017)
n_per, k = 60, 3                                   # 3 communities of 60 nodes
n = n_per * k
community = np.repeat(np.arange(k), n_per)
p_in, p_out = 0.10, 0.01
prob = np.where(community[:, None] == community[None, :], p_in, p_out)
A = np.triu(rng.random((n, n)) < prob, 1).astype(float)
A = A + A.T
deg = A.sum(axis=1)
print(f"graph: {n} nodes, {int(A.sum() / 2)} edges, mean degree {deg.mean():.1f}, "
      f"{np.mean(community[np.nonzero(np.triu(A))[0]] == community[np.nonzero(np.triu(A))[1]]):.2f} of edges inside a community")

# node features: a weak hint of the community plus a lot of noise
d_in = 16
means = rng.normal(size=(k, d_in))
X = 0.4 * means[community] + rng.normal(size=(n, d_in))

# A_hat = D^-1/2 (A + I) D^-1/2, the GCN propagation matrix
A_tilde = A + np.eye(n)
dinv = 1 / np.sqrt(A_tilde.sum(axis=1))
A_hat = A_tilde * dinv[:, None] * dinv[None, :]

labelled = np.concatenate([np.flatnonzero(community == c)[:3] for c in range(k)])   # 3 labels per class
mask = np.zeros(n, bool); mask[labelled] = True

def softmax(Z):
    Z = Z - Z.max(axis=1, keepdims=True); E = np.exp(Z); return E / E.sum(axis=1, keepdims=True)

def train(prop, hidden=16, steps=300, lr=0.05, wd=5e-3, seed=0):
    """Two layers: Z = prop @ relu(prop @ X @ W1) @ W2. prop = A_hat for a GCN, I for an MLP."""
    r = np.random.default_rng(seed)
    W1 = r.normal(size=(d_in, hidden)) * np.sqrt(2 / d_in)
    W2 = r.normal(size=(hidden, k)) * np.sqrt(1 / hidden)
    Y = np.eye(k)[community]
    for _ in range(steps):
        PX = prop @ X
        H_pre = PX @ W1; H = np.maximum(H_pre, 0)
        Z = prop @ H @ W2
        P = softmax(Z)
        dZ = np.zeros_like(Z); dZ[mask] = (P[mask] - Y[mask]) / mask.sum()   # loss on labelled nodes only
        dW2 = (prop @ H).T @ dZ + wd * W2
        dH = prop.T @ dZ @ W2.T
        dW1 = PX.T @ (dH * (H_pre > 0)) + wd * W1
        W1 -= lr * dW1; W2 -= lr * dW2
    return W1, W2

def predict(prop, W1, W2, Xin=None):
    Xin = X if Xin is None else Xin
    return softmax(prop @ np.maximum(prop @ Xin @ W1, 0) @ W2)

print("\n1. 9 labelled nodes (3 per community); accuracy on the other 171")
for name, prop in [("MLP (ignores edges)", np.eye(n)), ("GCN (uses edges)   ", A_hat)]:
    accs = []
    for seed in range(5):
        W1, W2 = train(prop, seed=seed)
        accs.append(np.mean(predict(prop, W1, W2).argmax(axis=1)[~mask] == community[~mask]))
    print(f"   {name}: mean accuracy {np.mean(accs):.3f} over 5 initialisations (min {min(accs):.3f}, max {max(accs):.3f})")

print("\n2. permutation equivariance: relabel the nodes, the outputs are relabelled the same way")
W1, W2 = train(A_hat)
perm = rng.permutation(n)
Pm = np.eye(n)[perm]                                # permutation matrix
out = predict(A_hat, W1, W2)
out_perm = predict(Pm @ A_hat @ Pm.T, W1, W2, Xin=Pm @ X)
print(f"   max |GCN(P A P^T, P X) - P GCN(A, X)| = {np.abs(out_perm - Pm @ out).max():.2e}")
