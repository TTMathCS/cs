"""Chapter 4: maximum likelihood, R^2 and residual plots.

1. With Gaussian noise, the least-squares weights maximise the likelihood,
   and the noise variance is estimated by the mean squared residual.
2. Residuals of a straight line fitted to a curve, and of a quadratic.
3. Residuals whose spread grows with x (a funnel).
"""
import numpy as np
from ch04_gradient_descent import make_flats


def fit(X, y):
    return np.linalg.lstsq(X, y, rcond=None)[0]


def gaussian_log_likelihood(X, y, w, sigma2):
    r = y - X @ w
    n = len(y)
    return -0.5 * n * np.log(2 * np.pi * sigma2) - (r @ r) / (2 * sigma2)


def binned(x, r, edges):
    out = []
    for lo, hi in zip(edges[:-1], edges[1:]):
        m = (x >= lo) & (x < hi)
        out.append((lo, hi, r[m].mean(), r[m].std()))
    return out


if __name__ == "__main__":
    F, y = make_flats()
    X = np.column_stack([np.ones(len(y)), F])
    w = fit(X, y)
    r = y - X @ w
    s2 = r @ r / len(y)
    print(f"weights {w.round(3)}; MLE noise sd {np.sqrt(s2):.3f} (data made with sd 15)")
    rng = np.random.default_rng(10)
    others = [float(gaussian_log_likelihood(X, y, w + rng.normal(0, 0.5, 3), s2)) for _ in range(5)]
    print(f"log-likelihood at the least-squares w: {gaussian_log_likelihood(X, y, w, s2):.3f}")
    print("at five nearby w:", [round(v, 3) for v in others])
    sst = ((y - y.mean()) ** 2).sum()
    print(f"R^2 = {1 - (r @ r) / sst:.4f}")

    x = np.sort(rng.uniform(0, 4, 120))
    yc = 1 + 0.5 * x ** 2 + rng.normal(0, 0.4, 120)
    edges = np.linspace(0, 4, 5)
    for name, D in [("line", np.column_stack([np.ones_like(x), x])),
                    ("quadratic", np.column_stack([np.ones_like(x), x, x ** 2]))]:
        res = yc - D @ fit(D, yc)
        r2 = 1 - (res @ res) / ((yc - yc.mean()) ** 2).sum()
        print(f"\n{name}: R^2 = {r2:.4f}; mean residual by range of x:")
        for lo, hi, m, s in binned(x, res, edges):
            print(f"  x in [{lo:.0f}, {hi:.0f}): mean {m:+.3f}")

    yf = 2 + 1.5 * x + rng.normal(0, 0.25 * x + 0.05, 120)
    D = np.column_stack([np.ones_like(x), x])
    res = yf - D @ fit(D, yf)
    print("\nfunnel: residual spread by range of x:")
    for lo, hi, m, s in binned(x, res, edges):
        print(f"  x in [{lo:.0f}, {hi:.0f}): sd {s:.3f}")
