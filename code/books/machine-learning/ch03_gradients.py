"""Chapter 3: derivatives, gradients, the chain rule, and checking a gradient.

We differentiate by hand, then check the answer with finite differences.
The same check is used in every later chapter that derives a gradient.
"""
import numpy as np


def f(x):
    return x ** 3 - 2 * x


def f_prime(x):
    return 3 * x ** 2 - 2


def forward_diff(g, x, h):
    return (g(x + h) - g(x)) / h


def central_diff(g, x, h):
    return (g(x + h) - g(x - h)) / (2 * h)


def numerical_gradient(F, w, h=1e-5):
    """Central differences, one coordinate at a time."""
    grad = np.zeros_like(w)
    for j in range(len(w)):
        e = np.zeros_like(w)
        e[j] = h
        grad[j] = (F(w + e) - F(w - e)) / (2 * h)
    return grad


if __name__ == "__main__":
    x = 1.5
    print(f"f(x) = x^3 - 2x at x = {x}: exact derivative {f_prime(x)}")
    print("      h    forward error    central error")
    for h in [1e-1, 1e-2, 1e-3, 1e-4, 1e-6, 1e-8, 1e-10]:
        ef = abs(forward_diff(f, x, h) - f_prime(x))
        ec = abs(central_diff(f, x, h) - f_prime(x))
        print(f"  {h:6.0e}    {ef:13.3e}    {ec:13.3e}")

    # A two-variable function and its gradient
    def g(w):
        return w[0] ** 2 + 3 * w[0] * w[1] + 2 * w[1] ** 2

    def g_grad(w):
        return np.array([2 * w[0] + 3 * w[1], 3 * w[0] + 4 * w[1]])

    w = np.array([1.0, -2.0])
    print("\ng(w) = w1^2 + 3 w1 w2 + 2 w2^2 at", w)
    print("  by hand:", g_grad(w), "  numerical:", numerical_gradient(g, w).round(8))

    # Chain rule: L(w) = mean((X w - y)^2); dL/dw = (2/n) X^T (X w - y)
    rng = np.random.default_rng(6)
    X = rng.normal(size=(5, 3))
    y = rng.normal(size=5)
    wv = rng.normal(size=3)

    def mse(w):
        return np.mean((X @ w - y) ** 2)

    def mse_grad(w):
        return 2 * X.T @ (X @ w - y) / len(y)

    a, b = mse_grad(wv), numerical_gradient(mse, wv)
    rel = np.linalg.norm(a - b) / np.linalg.norm(a + b)
    print("\nmean squared error gradient")
    print("  by hand:  ", a.round(6))
    print("  numerical:", b.round(6))
    print(f"  relative difference {rel:.1e}")

    # A deliberate bug: forgetting the factor 2 is caught at once
    buggy = X.T @ (X @ wv - y) / len(y)
    print(f"  buggy gradient's relative difference {np.linalg.norm(buggy - b) / np.linalg.norm(buggy + b):.2f}")
