"""Chapter 14: classical MDS, Isomap on a Swiss roll, and t-SNE, from scratch."""
import os
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")   # small matrices: one thread is faster than many
import numpy as np


def sq_dist(X):
    s = (X ** 2).sum(1)
    return np.maximum(s[:, None] + s[None, :] - 2 * X @ X.T, 0.0)


def classical_mds(D, k):
    """Points in k dimensions whose distances match the n by n distance matrix D as well as possible."""
    n = len(D)
    J = np.eye(n) - np.ones((n, n)) / n          # centring matrix
    B = -0.5 * J @ (D ** 2) @ J                  # Gram matrix of centred points
    vals, vecs = np.linalg.eigh(B)
    vals, vecs = vals[::-1][:k], vecs[:, ::-1][:, :k]
    return vecs * np.sqrt(np.maximum(vals, 0))


def isomap(X, k_nn, dim):
    """Geodesic distances along a k-nearest-neighbour graph, then classical MDS."""
    n = len(X)
    D = np.sqrt(sq_dist(X))
    G = np.full((n, n), np.inf)
    nn = np.argsort(D, axis=1)[:, 1:k_nn + 1]
    for i in range(n):
        G[i, nn[i]] = D[i, nn[i]]
    G = np.minimum(G, G.T)                       # make the graph undirected
    np.fill_diagonal(G, 0.0)
    for m in range(n):                           # Floyd-Warshall, one vectorised row at a time
        G = np.minimum(G, G[:, m:m + 1] + G[m:m + 1, :])
    assert np.isfinite(G).all(), "the neighbour graph is not connected"
    return classical_mds(G, dim)


def tsne(X, perplexity=30.0, iters=500, seed=0):
    """t-SNE (van der Maaten and Hinton 2008), exact gradients, for a few hundred points."""
    n = len(X)
    D2 = sq_dist(X)
    P = np.zeros((n, n))
    target = np.log(perplexity)                  # wanted entropy (in nats) of each row
    for i in range(n):                           # binary search for each point's bandwidth
        lo, hi, beta = 0.0, np.inf, 1.0          # beta = 1 / (2 sigma_i^2)
        d = np.delete(D2[i], i)
        for _ in range(60):
            w = np.exp(-(d - d.min()) * beta)
            p = w / w.sum()
            H = -(p * np.log(p + 1e-300)).sum()
            if H > target:                       # too spread out: narrow the Gaussian
                lo = beta
                beta = beta * 2 if hi == np.inf else (beta + hi) / 2
            else:
                hi = beta
                beta = (beta + lo) / 2
        P[i, np.arange(n) != i] = p
    P = (P + P.T) / (2 * n)                      # symmetric joint probabilities
    rng = np.random.default_rng(seed)
    Y = 1e-4 * rng.normal(size=(n, 2))
    V = np.zeros_like(Y)
    for t in range(iters):
        exag = 12.0 if t < 100 else 1.0          # early exaggeration
        num = 1.0 / (1.0 + sq_dist(Y))           # Student-t kernel with one degree of freedom
        np.fill_diagonal(num, 0.0)
        Q = num / num.sum()
        M = (exag * P - Q) * num
        grad = 4 * (np.diag(M.sum(1)) - M) @ Y   # dC/dy_i = 4 sum_j (p_ij - q_ij)(y_i - y_j)/(1+|y_i-y_j|^2)
        V = (0.5 if t < 250 else 0.8) * V - 100.0 * grad
        Y = Y + V
    kl = (P * np.log((P + 1e-12) / (Q + 1e-12))).sum()
    return Y, kl


def knn_kept(X, Y, k=10):
    """Average fraction of each point's k nearest neighbours in X that are also among its k nearest in Y."""
    a = np.argsort(sq_dist(X), 1)[:, 1:k + 1]
    b = np.argsort(sq_dist(Y), 1)[:, 1:k + 1]
    return np.mean([len(set(a[i]) & set(b[i])) / k for i in range(len(X))])


def pca2(X):
    Xc = X - X.mean(0)
    return Xc @ np.linalg.svd(Xc, full_matrices=False)[2][:2].T


if __name__ == "__main__":
    rng = np.random.default_rng(0)

    print("1. Classical MDS from distances alone gives back a configuration with the same distances")
    pts = rng.normal(size=(6, 2))
    D = np.sqrt(sq_dist(pts))
    Z = classical_mds(D, 2)
    print(f"  largest distance error: {np.abs(np.sqrt(sq_dist(Z)) - D).max():.1e}")

    print("\n2. Swiss roll: 500 points on a rolled-up sheet in 3-D; t is the position along the roll")
    t = rng.uniform(1.5 * np.pi, 4.5 * np.pi, 500)
    h = rng.uniform(0, 15, 500)
    X = np.c_[t * np.cos(t), h, t * np.sin(t)]
    for name, Y in (("PCA", pca2(X)), ("Isomap (10 neighbours)", isomap(X, 10, 2))):
        c = max(abs(np.corrcoef(Y[:, j], t)[0, 1]) for j in range(2))
        print(f"  {name:24s} best |correlation| of a coordinate with t: {c:.3f}")

    print("\n3. t-SNE on three clusters in 10-D: a tight one, a medium one and a wide one")
    centres = np.zeros((3, 10))
    centres[1, 0], centres[2, 0] = 20.0, 60.0          # cluster 2 is three times farther from 0 than 1 is
    sds = [0.5, 2.0, 5.0]
    X = np.vstack([c + s * rng.normal(size=(50, 10)) for c, s in zip(centres, sds)])
    lab = np.repeat([0, 1, 2], 50)
    Y, kl = tsne(X, perplexity=20)
    for name, Z in (("input (10-D)", X), ("PCA (2-D)", pca2(X)), ("t-SNE (2-D)", Y)):
        spread = [np.sqrt(((Z[lab == j] - Z[lab == j].mean(0)) ** 2).sum(1).mean()) for j in range(3)]
        m = [Z[lab == j].mean(0) for j in range(3)]
        d01, d02 = np.linalg.norm(m[0] - m[1]), np.linalg.norm(m[0] - m[2])
        print(f"  {name:13s} cluster spreads {np.round(spread, 2).tolist()}  "
              f"ratio of centre distances d(0,2)/d(0,1) = {d02 / d01:.2f}")
    print(f"  10 nearest neighbours kept: PCA {knn_kept(X, pca2(X)):.2f}, t-SNE {knn_kept(X, Y):.2f};"
          f"  final KL(P||Q) = {kl:.3f}")
