"""Chapter 13: agglomerative clustering, DBSCAN and spectral clustering from scratch."""
import os
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")   # small matrices: one thread is faster than many
import numpy as np


def pairwise(X):
    return np.sqrt(((X[:, None, :] - X[None, :, :]) ** 2).sum(axis=2))


def agglomerative(X, linkage):
    """Merge the two closest clusters until one is left. Returns the list of merges (a, b, height)."""
    D = pairwise(X)
    clusters = {i: [i] for i in range(len(X))}
    merges, nxt = [], len(X)
    while len(clusters) > 1:
        best = None
        keys = sorted(clusters)
        for ai, a in enumerate(keys):
            for b in keys[ai + 1:]:
                block = D[np.ix_(clusters[a], clusters[b])]
                h = {"single": block.min(), "complete": block.max(), "average": block.mean()}[linkage]
                if best is None or h < best[2] - 1e-12:
                    best = (a, b, h)
        a, b, h = best
        clusters[nxt] = clusters.pop(a) + clusters.pop(b)
        merges.append((a, b, round(float(h), 3), sorted(clusters[nxt])))
        nxt += 1
    return merges


def cut(X, linkage, k):
    """Labels after stopping when k clusters remain. Uses the Lance-Williams update, so each merge
    costs one pass over a distance matrix instead of recomputing every block."""
    n = len(X)
    D = pairwise(X)
    np.fill_diagonal(D, np.inf)
    size = np.ones(n)
    alive = np.ones(n, bool)
    owner = np.arange(n)                   # owner[i] = representative of point i's cluster
    for _ in range(n - k):
        i, j = np.unravel_index(np.argmin(D), D.shape)
        if linkage == "single":
            new = np.minimum(D[i], D[j])
        elif linkage == "complete":
            new = np.maximum(D[i], D[j])
        else:                              # average: weighted by cluster sizes
            new = (size[i] * D[i] + size[j] * D[j]) / (size[i] + size[j])
        D[i], D[:, i] = new, new
        D[i, i] = np.inf
        D[j], D[:, j] = np.inf, np.inf     # cluster j is gone
        size[i] += size[j]
        alive[j] = False
        owner[owner == j] = i
    _, lab = np.unique(owner, return_inverse=True)
    return lab


def dbscan(X, eps, min_pts):
    """Label -1 is noise. A core point has at least min_pts points (itself included) within eps."""
    D = pairwise(X)
    nbrs = [np.flatnonzero(D[i] <= eps) for i in range(len(X))]
    core = np.array([len(nb) >= min_pts for nb in nbrs])
    lab = np.full(len(X), -1)
    c = 0
    for i in range(len(X)):
        if lab[i] != -1 or not core[i]:
            continue
        lab[i] = c
        stack = [i]
        while stack:                       # grow the cluster through core points
            p = stack.pop()
            for q in nbrs[p]:
                if lab[q] == -1:
                    lab[q] = c
                    if core[q]:
                        stack.append(q)
        c += 1
    return lab, core


def kmeans(X, k, rng, runs=10):
    best = None
    for _ in range(runs):
        C = X[rng.choice(len(X), k, replace=False)]
        for _ in range(100):
            lab = ((X[:, None] - C[None]) ** 2).sum(2).argmin(1)
            newC = np.array([X[lab == j].mean(0) if (lab == j).any() else C[j] for j in range(k)])
            if np.allclose(newC, C):
                break
            C = newC
        J = ((X - C[lab]) ** 2).sum()
        if best is None or J < best[0]:
            best = (J, lab)
    return best[1]


def spectral(X, k, sigma, rng):
    """Normalized spectral clustering (Ng, Jordan and Weiss 2001)."""
    W = np.exp(-pairwise(X) ** 2 / (2 * sigma ** 2))
    np.fill_diagonal(W, 0.0)
    d = W.sum(1)
    Lsym = np.eye(len(X)) - W / np.sqrt(d[:, None] * d[None, :])
    vals, vecs = np.linalg.eigh(Lsym)                     # ascending eigenvalues
    U = vecs[:, :k]
    U = U / np.linalg.norm(U, axis=1, keepdims=True)      # each row onto the unit sphere
    return kmeans(U, k, rng), vals[:k + 2]


def two_rings(rng, n=100):
    """n points on a ring of radius 1 and 3n on a ring of radius 3: the same density on both."""
    t = rng.uniform(0, 2 * np.pi, 4 * n)
    r = np.r_[np.full(n, 1.0), np.full(3 * n, 3.0)] + rng.normal(scale=0.12, size=4 * n)
    return np.c_[r * np.cos(t), r * np.sin(t)], np.r_[np.zeros(n, int), np.ones(3 * n, int)]


def agree(lab, truth):
    return max((lab == truth).mean(), (lab == 1 - truth).mean())


if __name__ == "__main__":
    pts = np.array([[0, 0], [1, 0], [0, 1.5], [5, 0], [5, 1], [9, 0.5]], float)
    print("1. Six points, the merge order (cluster ids 6, 7, ... are new clusters)")
    for link in ("single", "complete", "average"):
        print(f"  {link}:")
        for a, b, h, members in agglomerative(pts, link):
            print(f"    merge {a} + {b} at height {h:6.3f} -> {members}")

    rng = np.random.default_rng(0)
    X, truth = two_rings(rng)
    print("\n2. Two rings (100 + 300 points): agreement with the true rings")
    print(f"  k-means, k = 2:              {agree(kmeans(X, 2, rng), truth):.3f}")
    print(f"  complete linkage, 2 clusters: {agree(cut(X, 'complete', 2), truth):.3f}")
    print(f"  single linkage, 2 clusters:   {agree(cut(X, 'single', 2), truth):.3f}")
    lab, core = dbscan(X, eps=0.5, min_pts=5)
    print(f"  DBSCAN eps 0.5, minPts 5:     clusters {lab.max() + 1}, noise {np.sum(lab == -1)}, "
          f"core {core.sum()}, agreement {agree(np.where(lab < 0, 0, lab), truth):.3f}")
    lab, vals = spectral(X, 2, sigma=0.3, rng=rng)
    print(f"  spectral, sigma 0.3:          {agree(lab, truth):.3f};  smallest eigenvalues {(np.round(vals, 4) + 0.0).tolist()}")

    print("\n3. DBSCAN finds noise: the rings plus 20 scattered points")
    Xn = np.vstack([X, rng.uniform(-4, 4, size=(20, 2))])
    lab, core = dbscan(Xn, eps=0.5, min_pts=5)
    print(f"  clusters {lab.max() + 1}, points labelled noise {np.sum(lab == -1)}")
