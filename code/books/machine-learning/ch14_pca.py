"""Chapter 14: PCA two ways (eigenvectors of the covariance, and the SVD), explained variance,
reconstruction error and denoising, from scratch."""
import numpy as np


def pca_eig(X, k):
    """Top-k principal directions from the eigenvectors of the covariance matrix."""
    mu = X.mean(axis=0)
    Xc = X - mu
    S = Xc.T @ Xc / len(X)                       # covariance (dividing by n)
    vals, vecs = np.linalg.eigh(S)               # ascending order
    order = np.argsort(vals)[::-1]
    return mu, vals[order], vecs[:, order[:k]]


def pca_svd(X, k):
    """The same directions from the SVD of the centred data: Xc = U diag(s) V^T."""
    mu = X.mean(axis=0)
    U, s, Vt = np.linalg.svd(X - mu, full_matrices=False)
    return mu, s ** 2 / len(X), Vt[:k].T         # eigenvalues of S are s^2 / n


def fix_signs(V):
    """Eigenvectors are defined up to sign; make the largest entry of each column positive."""
    idx = np.abs(V).argmax(axis=0)
    return V * np.sign(V[idx, np.arange(V.shape[1])])


if __name__ == "__main__":
    print("1. Hand example: five points in the plane")
    P = np.array([[-2, -1], [-1, -1], [0, 0], [1, 1], [2, 1]], float)
    mu, vals, V = pca_eig(P, 2)
    S = (P - mu).T @ (P - mu) / len(P)
    print("  covariance", S.tolist())
    print("  eigenvalues", np.round(vals, 4).tolist(), " first direction", np.round(fix_signs(V)[:, 0], 4).tolist())
    z = (P - mu) @ fix_signs(V)[:, :1]
    print("  scores on PC1", np.round(z.ravel(), 4).tolist())
    print(f"  share of variance on PC1: {vals[0] / vals.sum():.4f}")

    print("\n2. 300 points in 10 dimensions made from 3 hidden factors plus noise")
    rng = np.random.default_rng(0)
    n, p, k_true = 300, 10, 3
    F = rng.normal(size=(n, k_true)) * [3.0, 2.0, 1.0]       # hidden factors with different spreads
    A = np.linalg.qr(rng.normal(size=(p, k_true)))[0]        # orthonormal loading directions
    X = F @ A.T + 0.3 * rng.normal(size=(n, p)) + 5.0
    mu, vals_e, Ve = pca_eig(X, 3)
    _, vals_s, Vs = pca_svd(X, 3)
    print("  eigenvalues from eig:", np.round(vals_e, 3).tolist())
    print("  eigenvalues from SVD:", np.round(vals_s, 3).tolist())
    print("  same directions (max difference after fixing signs):",
          f"{np.abs(fix_signs(Ve) - fix_signs(Vs)).max():.1e}")
    cum = np.cumsum(vals_e) / vals_e.sum()
    print("  cumulative explained variance:", np.round(cum, 3).tolist())

    print("\n3. Reconstruction error with k components equals the sum of the discarded eigenvalues")
    Xc = X - mu
    for k in range(0, 6):
        _, _, Vk = pca_svd(X, k)
        R = Xc @ Vk @ Vk.T if k else np.zeros_like(Xc)
        err = ((Xc - R) ** 2).sum(axis=1).mean()
        print(f"  k = {k}: mean squared error {err:8.4f}   sum of discarded eigenvalues {vals_e[k:].sum():8.4f}")

    print("\n4. Denoising: keep 3 components of a noisy copy and compare with the clean signal")
    clean = F @ A.T
    noisy = clean + 0.3 * rng.normal(size=(n, p))
    mu_n, _, V3 = pca_svd(noisy, 3)
    den = mu_n + (noisy - mu_n) @ V3 @ V3.T
    print(f"  mean squared error noisy vs clean:    {((noisy - clean) ** 2).mean():.4f}")
    print(f"  mean squared error denoised vs clean: {((den - clean) ** 2).mean():.4f}")
