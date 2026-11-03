"""Chapter 14: autoencoders preview. A linear autoencoder trained by gradient descent finds the PCA subspace;
a small non-linear one compresses a circle to one number better than PCA can."""
import numpy as np


def make_data(seed=0):
    rng = np.random.default_rng(seed)               # the same data as ch14_pca.py
    F = rng.normal(size=(300, 3)) * [3.0, 2.0, 1.0]
    A = np.linalg.qr(rng.normal(size=(10, 3)))[0]
    return F @ A.T + 0.3 * rng.normal(size=(300, 10)) + 5.0


def linear_autoencoder(X, k, steps=3000, lr=0.01, seed=1):
    """Encoder z = E x, decoder x_hat = D z, loss = mean squared reconstruction error."""
    rng = np.random.default_rng(seed)
    Xc = X - X.mean(0)
    n, p = Xc.shape
    E = 0.1 * rng.normal(size=(k, p))
    D = 0.1 * rng.normal(size=(p, k))
    for s in range(steps):
        Z = Xc @ E.T                                  # n by k codes
        R = Z @ D.T - Xc                              # residuals
        gD = 2 * R.T @ Z / n                          # gradient of mean ||R_i||^2 with respect to D
        gE = 2 * (R @ D).T @ Xc / n                   # ... and with respect to E
        D -= lr * gD
        E -= lr * gE
    return E, D, (R ** 2).sum(1).mean()


def adam_step(params, grads, state, lr, t, b1=0.9, b2=0.999):
    for key in params:
        m, v = state.setdefault(key, (np.zeros_like(params[key]), np.zeros_like(params[key])))
        m = b1 * m + (1 - b1) * grads[key]
        v = b2 * v + (1 - b2) * grads[key] ** 2
        state[key] = (m, v)
        params[key] -= lr * (m / (1 - b1 ** t)) / (np.sqrt(v / (1 - b2 ** t)) + 1e-8)


def circle_autoencoder(X, hidden=32, steps=4000, lr=0.01, seed=2):
    """2 -> hidden (tanh) -> 1 -> hidden (tanh) -> 2, trained with Adam; gradients by the chain rule."""
    rng = np.random.default_rng(seed)
    p = {"W1": rng.normal(size=(2, hidden)), "b1": np.zeros(hidden),
         "W2": rng.normal(size=(hidden, 1)) / np.sqrt(hidden), "b2": np.zeros(1),
         "W3": rng.normal(size=(1, hidden)), "b3": np.zeros(hidden),
         "W4": rng.normal(size=(hidden, 2)) / np.sqrt(hidden), "b4": np.zeros(2)}
    state, n = {}, len(X)
    for t in range(1, steps + 1):
        H1 = np.tanh(X @ p["W1"] + p["b1"])
        Z = H1 @ p["W2"] + p["b2"]                    # the one-number code
        H2 = np.tanh(Z @ p["W3"] + p["b3"])
        Xh = H2 @ p["W4"] + p["b4"]
        dXh = 2 * (Xh - X) / n                        # backward pass, layer by layer
        g = {"W4": H2.T @ dXh, "b4": dXh.sum(0)}
        dA2 = (dXh @ p["W4"].T) * (1 - H2 ** 2)
        g["W3"], g["b3"] = Z.T @ dA2, dA2.sum(0)
        dZ = dA2 @ p["W3"].T
        g["W2"], g["b2"] = H1.T @ dZ, dZ.sum(0)
        dA1 = (dZ @ p["W2"].T) * (1 - H1 ** 2)
        g["W1"], g["b1"] = X.T @ dA1, dA1.sum(0)
        adam_step(p, g, state, lr, t)
    return ((Xh - X) ** 2).sum(1).mean()


if __name__ == "__main__":
    X = make_data()
    Xc = X - X.mean(0)
    V = np.linalg.svd(Xc, full_matrices=False)[2][:3].T
    pca_err = ((Xc - Xc @ V @ V.T) ** 2).sum(1).mean()
    E, D, ae_err = linear_autoencoder(X, 3)
    Q = np.linalg.qr(D)[0]                             # orthonormal basis of the decoder's column space
    cosines = np.linalg.svd(V.T @ Q)[1]                # cosines of the principal angles between subspaces
    print("1. Linear autoencoder 10 -> 3 -> 10 on the data of ch14_pca.py")
    print(f"  reconstruction error: autoencoder {ae_err:.4f}, PCA with 3 components {pca_err:.4f}")
    print("  cosines of the angles between its subspace and the PCA subspace:", np.round(cosines, 4).tolist())
    print("  is the decoder orthonormal like PCA?  D^T D =", (np.round(D.T @ D, 2) + 0.0).tolist())

    rng = np.random.default_rng(5)
    a = rng.uniform(0, 2 * np.pi, 200)
    C = np.c_[np.cos(a), np.sin(a)] + 0.02 * rng.normal(size=(200, 2))
    Cc = C - C.mean(0)
    v = np.linalg.svd(Cc, full_matrices=False)[2][:1].T
    print("\n2. 200 points on a circle, squeezed through one number")
    print(f"  PCA with 1 component: error {((Cc - Cc @ v @ v.T) ** 2).sum(1).mean():.4f}")
    print(f"  non-linear autoencoder 2-32-1-32-2: error {circle_autoencoder(C):.4f}")
