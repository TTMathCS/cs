"""Chapter 12.1 and 12.5: Gaussian discriminant analysis (LDA and QDA) from scratch, and a
generative-versus-discriminative race: LDA against logistic regression as the data grow."""
import numpy as np


def fit_gda(X, y, shared):
    classes = np.unique(y)
    pri = np.array([np.mean(y == c) for c in classes])
    mu = np.array([X[y == c].mean(0) for c in classes])
    covs = [np.cov(X[y == c].T, bias=True) for c in classes]
    if shared:   # pooled covariance: weighted average of the class covariances
        pooled = sum(np.mean(y == c) * S for c, S in zip(classes, covs))
        covs = [pooled] * len(classes)
    return classes, pri, mu, covs


def gda_log_post(model, X):
    classes, pri, mu, covs = model
    out = []
    for p, m, S in zip(pri, mu, covs):
        D = X - m
        Si = np.linalg.inv(S)
        out.append(np.log(p) - 0.5 * np.log(np.linalg.det(S)) - 0.5 * np.einsum("ij,jk,ik->i", D, Si, D))
    return np.array(out).T          # up to a shared constant


def gda_predict(model, X):
    return model[0][np.argmax(gda_log_post(model, X), axis=1)]


def logistic_newton(X, y, iters=25, l2=1e-6):
    """Logistic regression fitted by Newton's method (IRLS), tiny ridge for stability."""
    A = np.column_stack([np.ones(len(X)), X])
    w = np.zeros(A.shape[1])
    for _ in range(iters):
        p = 1 / (1 + np.exp(-np.clip(A @ w, -30, 30)))
        g = A.T @ (p - y) + l2 * w
        H = A.T @ (A * (p * (1 - p))[:, None]) + l2 * np.eye(len(w))
        w -= np.linalg.solve(H, g)
    return w


rng = np.random.default_rng(12)
mu0, mu1 = np.array([0.0, 0.0]), np.array([1.5, 1.0])
Sig = np.array([[1.0, 0.6], [0.6, 1.5]])

print("1. LDA on two Gaussian classes with a shared covariance (200 points each)")
X = np.vstack([rng.multivariate_normal(mu0, Sig, 200), rng.multivariate_normal(mu1, Sig, 200)])
y = np.repeat([0, 1], 200)
classes, pri, mu, covs = fit_gda(X, y, shared=True)
Si = np.linalg.inv(covs[0])
w = Si @ (mu[1] - mu[0])
b = -0.5 * (mu[1] @ Si @ mu[1] - mu[0] @ Si @ mu[0]) + np.log(pri[1] / pri[0])
print(f"   estimated means {np.round(mu[0], 3)}, {np.round(mu[1], 3)}")
print(f"   pooled covariance {np.round(covs[0], 3).tolist()}")
print(f"   log P(1|x)/P(0|x) = w.x + b with w = {np.round(w, 4)}, b = {b:.4f}")
wl = logistic_newton(X, y)
print(f"   logistic regression on the same data: w = {np.round(wl[1:], 4)}, b = {wl[0]:.4f}")
wt = np.linalg.inv(Sig) @ (mu1 - mu0)
print(f"   true w = Sigma^-1 (mu1 - mu0) = {np.round(wt, 4)}, true b = {-0.5 * (mu1 @ np.linalg.inv(Sig) @ mu1):.4f}")

print("\n2. QDA when the covariances differ (class 1 much wider)")
Xq = np.vstack([rng.multivariate_normal([0, 0], [[0.3, 0], [0, 0.3]], 300),
                rng.multivariate_normal([0.5, 0], [[3, 0], [0, 3]], 300)])
yq = np.repeat([0, 1], 300)
Xqt = np.vstack([rng.multivariate_normal([0, 0], [[0.3, 0], [0, 0.3]], 3000),
                 rng.multivariate_normal([0.5, 0], [[3, 0], [0, 3]], 3000)])
yqt = np.repeat([0, 1], 3000)
for name, shared in [("LDA", True), ("QDA", False)]:
    acc = np.mean(gda_predict(fit_gda(Xq, yq, shared), Xqt) == yqt)
    print(f"   {name}: test accuracy {acc:.3f}")

print("\n3. Generative against discriminative in 10 dimensions, 20 repeats, test accuracy")


def fit_nb(X, y):
    """Gaussian naive Bayes with a shared diagonal covariance: LDA that assumes independent features."""
    m0, m1 = X[y == 0].mean(0), X[y == 1].mean(0)
    v = 0.5 * (X[y == 0].var(0) + X[y == 1].var(0))
    return (m1 - m0) / v, -0.5 * ((m1 ** 2 - m0 ** 2) / v).sum()


d = 10


def world_a(y):
    """Independent features, each shifted by 0.35 in class 1: naive Bayes' assumption is true."""
    return rng.normal(0, 1, (len(y), d)) + 0.35 * y[:, None]


def world_b(y):
    """One shared noise z in every feature; only feature 0 carries the class. Independence is false,
    and the other nine features are useful only to cancel z, which naive Bayes cannot do."""
    z = rng.normal(0, 1, (len(y), 1))
    return np.column_stack([z + 0.6 * y[:, None] + 0.5 * rng.normal(0, 1, (len(y), 1)),
                            z + 0.5 * rng.normal(0, 1, (len(y), d - 1))])


yt = np.repeat([0, 1], 5000)
for name, world in [("A: features independent", world_a), ("B: features share noise", world_b)]:
    Xt = world(yt)
    print(f"   world {name}")
    print("     per class n   naive Bayes    LDA   logistic")
    for n in [5, 10, 20, 50, 200, 1000]:
        res = np.zeros(3)
        for _ in range(20):
            ya = np.repeat([0, 1], n)
            Xa = world(ya)
            wn, bn = fit_nb(Xa, ya)
            res[0] += np.mean(((Xt @ wn + bn) > 0) == yt) / 20
            if n > d // 2:   # LDA needs an invertible pooled covariance: more points than dimensions
                res[1] += np.mean(gda_predict(fit_gda(Xa, ya, True), Xt) == yt) / 20
            wl = logistic_newton(Xa, ya)
            res[2] += np.mean(((Xt @ wl[1:] + wl[0]) > 0) == yt) / 20
        lda = f"{res[1]:.3f}" if n > d // 2 else "  -  "
        print(f"     {n:11d}   {res[0]:11.3f}  {lda}   {res[2]:.3f}")
from math import erf, sqrt
print("   In world B naive Bayes tends to the accuracy of feature 0 alone,"
      f" Phi(0.3 / sqrt(1.25)) = {0.5 * (1 + erf(0.3 / sqrt(1.25) / sqrt(2))):.3f};")
Sig_b = np.ones((d, d)) + 0.25 * np.eye(d)            # within-class covariance of world B
delta = np.zeros(d)
delta[0] = 0.6
maha = sqrt(delta @ np.linalg.solve(Sig_b, delta))
print(f"   the Bayes classifier (linear here) scores Phi(Delta/2) = {0.5 * (1 + erf(maha / 2 / sqrt(2))):.3f},"
      " where Delta is the Mahalanobis distance between the class means;")
print("   one test set of 10000 points measures accuracy to about +-0.005.")
