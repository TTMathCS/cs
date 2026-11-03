"""Chapter 3: eigenvectors by power iteration, the SVD, and information.

Power iteration finds the direction a symmetric matrix stretches most.
The SVD of a small matrix, a best low-rank approximation, and then entropy,
cross-entropy and KL divergence for small distributions.
"""
import numpy as np


def power_iteration(A, steps, v0):
    v = np.array(v0, dtype=float)
    history = []
    for _ in range(steps):
        v = A @ v
        v = v / np.linalg.norm(v)
        history.append((v.copy(), v @ A @ v))   # Rayleigh quotient estimates the eigenvalue
    return history


def entropy(p):
    p = np.asarray(p, float)
    nz = p > 0
    return float(-(p[nz] * np.log2(p[nz])).sum()) + 0.0   # + 0.0 turns -0.0 into 0.0


def cross_entropy(p, q):
    p, q = np.asarray(p, float), np.asarray(q, float)
    nz = p > 0
    return float(-(p[nz] * np.log2(q[nz])).sum())


def kl(p, q):
    return cross_entropy(p, q) - entropy(p)


if __name__ == "__main__":
    A = np.array([[2.0, 1.0], [1.0, 2.0]])
    print("power iteration on [[2,1],[1,2]] from (1, 0)")
    for t, (v, lam) in enumerate(power_iteration(A, 8, [1, 0]), 1):
        print(f"  step {t}: v = ({v[0]:.4f}, {v[1]:.4f})  estimate {lam:.6f}")
    vals, vecs = np.linalg.eigh(A)
    print("numpy eigh: eigenvalues", vals, " eigenvectors (columns)\n", vecs.round(4))

    # Covariance of correlated data: its top eigenvector is the long axis
    rng = np.random.default_rng(8)
    raw = rng.normal(size=(2000, 2)) * [3.0, 0.5]
    theta = np.radians(30)
    Rot = np.array([[np.cos(theta), -np.sin(theta)], [np.sin(theta), np.cos(theta)]])
    data = raw @ Rot.T
    C = np.cov(data.T)
    vals, vecs = np.linalg.eigh(C)
    top = vecs[:, -1] * np.sign(vecs[0, -1])
    print(f"covariance eigenvalues {vals.round(3)}; top direction {top.round(3)},"
          f" angle {np.degrees(np.arctan2(top[1], top[0])):.1f} deg (built at 30)")

    M = np.array([[3.0, 0.0], [4.0, 5.0]])
    U, s, Vt = np.linalg.svd(M)
    print("\nSVD of [[3,0],[4,5]]: singular values", s.round(4),
          " squares", (s ** 2).round(4), " eig of M^T M", np.linalg.eigvalsh(M.T @ M).round(4))
    print("  U S V^T rebuilds M:", np.allclose(U @ np.diag(s) @ Vt, M))

    # A small table of ratings (5 people x 4 films) with two kinds of taste
    R = np.array([[5, 4, 1, 2], [4, 4, 1, 1], [2, 1, 4, 5], [1, 2, 5, 4], [5, 5, 2, 1]], float)
    U, s, Vt = np.linalg.svd(R, full_matrices=False)
    print("ratings singular values", s.round(3))
    for k in (1, 2):
        Rk = U[:, :k] @ np.diag(s[:k]) @ Vt[:k]
        err = np.sqrt(((R - Rk) ** 2).sum())
        print(f"  rank {k}: error {err:.3f}, sqrt of the dropped s^2 {np.sqrt((s[k:] ** 2).sum()):.3f}")

    print("\nentropy in bits")
    for p in [[0.5, 0.5], [0.9, 0.1], [0.99, 0.01], [1.0, 0.0], [0.25] * 4]:
        print(f"  {str(p):26} H = {entropy(p):.4f}")
    P = [0.5, 0.25, 0.25]
    Q = [1 / 3, 1 / 3, 1 / 3]
    print(f"P = {P}, Q = uniform: H(P) = {entropy(P):.4f}, H(P,Q) = {cross_entropy(P, Q):.4f},"
          f" KL(P||Q) = {kl(P, Q):.4f}, KL(Q||P) = {kl(Q, P):.4f}")
    worst = min(kl(p, q) for p, q in (rng.dirichlet(np.ones(4), size=2) for _ in range(10000)))
    print(f"smallest KL over 10000 random pairs of distributions: {worst:.6f} (never negative)")
