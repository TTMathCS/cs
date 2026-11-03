"""Chapter 13: Gaussian mixtures fitted by EM, from scratch; the log-likelihood never goes down."""
import numpy as np


def log_gauss(X, mu, S):
    """log N(x | mu, S) for every row x of X."""
    d = X.shape[1]
    L = np.linalg.cholesky(S)                      # S = L L^T
    z = np.linalg.solve(L, (X - mu).T)             # z = L^{-1}(x - mu)
    return -0.5 * (z ** 2).sum(axis=0) - np.log(np.diag(L)).sum() - 0.5 * d * np.log(2 * np.pi)


def logsumexp(A, axis):
    m = A.max(axis=axis, keepdims=True)
    return (m + np.log(np.exp(A - m).sum(axis=axis, keepdims=True))).squeeze(axis)


def em_gmm(X, pis, mus, Ss, iters=200, tol=1e-8, verbose=False):
    n, d = X.shape
    k = len(pis)
    pis, mus, Ss = np.array(pis, float), np.array(mus, float), np.array(Ss, float)
    lls = []
    for it in range(iters):
        # E step: responsibilities r[i, j] = P(z_i = j | x_i, current parameters)
        logp = np.stack([np.log(pis[j]) + log_gauss(X, mus[j], Ss[j]) for j in range(k)], axis=1)
        ll = logsumexp(logp, axis=1)               # log p(x_i) under the current parameters
        lls.append(ll.sum())
        r = np.exp(logp - ll[:, None])
        # M step: weighted maximum likelihood
        Nk = r.sum(axis=0)
        pis = Nk / n
        mus = (r.T @ X) / Nk[:, None]
        for j in range(k):
            D = X - mus[j]
            Ss[j] = (r[:, j, None] * D).T @ D / Nk[j] + 1e-6 * np.eye(d)
        if verbose:
            print(f"  iter {it}: log-lik {lls[-1]:9.4f}  pi {np.round(pis, 3).tolist()}  "
                  f"mu {np.round(mus.ravel(), 3).tolist()}  var {np.round(Ss.ravel(), 3).tolist()}")
        if it > 0 and abs(lls[-1] - lls[-2]) < tol:
            break
    return pis, mus, Ss, r, lls


def agreement(labels, truth, k):
    """Best fraction of matching labels over all relabellings (k is small, so try all permutations)."""
    from itertools import permutations
    return max((np.array(p)[labels] == truth).mean() for p in permutations(range(k)))


if __name__ == "__main__":
    print("1. One dimension, 8 points, two components, deliberately poor start")
    x = np.array([-2.1, -1.7, -1.3, -0.9, 1.2, 1.6, 2.0, 2.5])[:, None]
    pis, mus, Ss, r, lls = em_gmm(x, [0.5, 0.5], [[-0.5], [0.5]], [[[1.0]], [[1.0]]], iters=6, verbose=True)
    print("  log-likelihood never decreased:", all(b >= a - 1e-12 for a, b in zip(lls, lls[1:])))

    print("\n2. Two long thin clusters in the plane (300 points). k-means against a GMM with full covariances")
    rng = np.random.default_rng(3)
    A = rng.normal(size=(150, 2)) * [3.0, 0.3] + [0.0, 0.0]
    B = rng.normal(size=(150, 2)) * [3.0, 0.3] + [0.0, 1.6]
    X = np.vstack([A, B])
    truth = np.repeat([0, 1], 150)

    C = X[[0, 150]].copy() + [[-2.0, 0.0], [2.0, 0.0]]   # same start for both methods
    for _ in range(100):
        lab = ((X[:, None, :] - C[None]) ** 2).sum(2).argmin(1)
        C = np.array([X[lab == j].mean(0) for j in range(2)])
    print(f"  k-means agreement with the true groups: {agreement(lab, truth, 2):.3f}")

    pis, mus, Ss, r, lls = em_gmm(X, [0.5, 0.5], C, [np.eye(2), np.eye(2)])
    lab = r.argmax(1)
    print(f"  GMM (EM) agreement with the true groups: {agreement(lab, truth, 2):.3f}  after {len(lls)} iterations")
    print("  fitted covariances:", [np.round(S, 2).tolist() for S in Ss])
    steps = np.diff(lls)
    print(f"  smallest change in log-likelihood between iterations: {steps.min():.2e} (never negative)")
