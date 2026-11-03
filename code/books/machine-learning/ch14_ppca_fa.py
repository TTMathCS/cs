"""Chapter 14: probabilistic PCA (closed form, Tipping and Bishop 1999) and factor analysis (EM)."""
import numpy as np


def gauss_loglik(X, mu, C):
    """Total log-likelihood of the rows of X under N(mu, C)."""
    n, p = X.shape
    sign, logdet = np.linalg.slogdet(C)
    D = X - mu
    quad = np.einsum("ij,ij->", D @ np.linalg.inv(C), D)
    return -0.5 * (n * p * np.log(2 * np.pi) + n * logdet + quad)


def ppca(X, k):
    """Maximum-likelihood PPCA: x = W z + mu + noise, z ~ N(0, I_k), noise ~ N(0, s2 I)."""
    mu = X.mean(0)
    S = (X - mu).T @ (X - mu) / len(X)
    vals, vecs = np.linalg.eigh(S)
    vals, vecs = vals[::-1], vecs[:, ::-1]
    s2 = vals[k:].mean()                          # noise = average discarded variance
    W = vecs[:, :k] * np.sqrt(vals[:k] - s2)      # W = V_k (Lambda_k - s2 I)^(1/2)
    return mu, W, s2


def factor_analysis(X, k, iters=500, seed=0):
    """EM for x = W z + mu + noise with a diagonal noise covariance Psi (one variance per feature)."""
    n, p = X.shape
    mu = X.mean(0)
    Xc = X - mu
    S = Xc.T @ Xc / n
    rng = np.random.default_rng(seed)
    W = rng.normal(size=(p, k))
    psi = np.diag(S).copy()
    for _ in range(iters):
        # E step: posterior of z given x is Gaussian with covariance G and mean G W^T Psi^-1 (x - mu)
        G = np.linalg.inv(np.eye(k) + W.T @ (W / psi[:, None]))
        Ez = Xc @ (W / psi[:, None]) @ G                  # n by k
        Ezz = n * G + Ez.T @ Ez                           # sum over points of E[z z^T]
        # M step
        W = (Xc.T @ Ez) @ np.linalg.inv(Ezz)
        psi = np.diag(S - W @ (Ez.T @ Xc) / n).copy()
        psi = np.maximum(psi, 1e-6)
    return mu, W, psi


if __name__ == "__main__":
    rng = np.random.default_rng(0)
    n, p = 300, 10
    F = rng.normal(size=(n, 3)) * [3.0, 2.0, 1.0]
    A = np.linalg.qr(rng.normal(size=(p, 3)))[0]
    X = F @ A.T + 0.3 * rng.normal(size=(n, p)) + 5.0

    print("1. PPCA on the 10-dimensional data of ch14_pca.py (true noise variance 0.09)")
    print("   k   noise variance   log-likelihood   parameters        BIC")
    for k in range(0, 6):
        mu, W, s2 = ppca(X, k)
        ll = gauss_loglik(X, mu, W @ W.T + s2 * np.eye(p))
        params = p + p * k - k * (k - 1) // 2 + 1
        bic = -2 * ll + params * np.log(n)
        print(f"  {k:2d}   {s2:12.4f}   {ll:14.2f}   {params:5d}   {bic:10.2f}")

    print("\n2. One hidden factor drives features 0-4; feature 5 is pure noise with a large variance")
    z = rng.normal(size=n)
    load = np.array([1.0, 0.9, 0.8, 0.7, 0.6, 0.0])
    noise_sd = np.array([0.3, 0.3, 0.3, 0.3, 0.3, 4.0])
    Y = np.outer(z, load) + rng.normal(size=(n, 6)) * noise_sd
    vals, vecs = np.linalg.eigh(np.cov(Y.T, bias=True))
    pc1 = vecs[:, -1] * np.sign(vecs[np.abs(vecs[:, -1]).argmax(), -1])
    print("  PCA first direction:      ", np.round(pc1, 3).tolist())
    mu, W, psi = factor_analysis(Y, 1)
    w = W[:, 0] * np.sign(W[0, 0])
    print("  factor analysis loadings: ", np.round(w, 3).tolist())
    print("  factor analysis noise var:", np.round(psi, 3).tolist(), " (true", (noise_sd ** 2).tolist(), ")")
