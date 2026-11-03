"""Chapter 12.3: MLE, MAP and full Bayes for a coin, with the conjugate beta prior.
Exact posteriors, posterior predictive, credible intervals and sequential updating."""
from math import lgamma, exp, log


def beta_pdf(p, a, b):
    return exp(lgamma(a + b) - lgamma(a) - lgamma(b) + (a - 1) * log(p) + (b - 1) * log(1 - p))


def beta_quantile(q, a, b, steps=200000):
    """Numerical inverse of the beta CDF by the midpoint rule on a fine grid."""
    total, h = 0.0, 1.0 / steps
    for k in range(steps):
        p = (k + 0.5) * h
        total += beta_pdf(p, a, b) * h
        if total >= q:
            return p
    return 1.0


print("Three flips, three heads. Prior Beta(2, 2) (a mild belief that the coin is fair).")
h, n, a, b = 3, 3, 2, 2
print(f"  MLE            h/n                     = {h / n:.4f}")
print(f"  MAP            (h+a-1)/(n+a+b-2)       = {(h + a - 1) / (n + a + b - 2):.4f}")
print(f"  posterior mean (h+a)/(n+a+b)           = {(h + a) / (n + a + b):.4f}")
print(f"  P(next is heads | data) = posterior mean = {(h + a) / (n + a + b):.4f}")
lo, hi = beta_quantile(0.025, h + a, n - h + b), beta_quantile(0.975, h + a, n - h + b)
print(f"  95% central credible interval for p: [{lo:.3f}, {hi:.3f}]")

print("\nHow the estimates move as data arrive (true p = 0.7, same Beta(2,2) prior)")
flips = [1, 1, 0, 1, 1, 1, 0, 1, 0, 1, 1, 1, 0, 1, 1, 0, 1, 1, 1, 0]
print("   n  heads    MLE     MAP   post. mean   95% interval")
heads = 0
for i, f in enumerate(flips, start=1):
    heads += f
    if i in (1, 2, 5, 10, 20):
        A, B = heads + a, i - heads + b
        print(f"  {i:2d}  {heads:5d}  {heads / i:5.3f}  {(A - 1) / (A + B - 2):6.3f}  {A / (A + B):10.3f}"
              f"   [{beta_quantile(0.025, A, B):.3f}, {beta_quantile(0.975, A, B):.3f}]")

print("\nSequential and batch updating give the same posterior:")
A, B = a, b
for f in flips[:10]:
    A, B = A + f, B + 1 - f
print(f"  one flip at a time: Beta({A}, {B});  all ten at once: Beta({a + sum(flips[:10])}, {b + 10 - sum(flips[:10])})")

print("\nLaplace's rule of succession (uniform prior Beta(1,1)): after n successes in n trials,")
for n in [1, 10, 100]:
    print(f"  n = {n:3d}: P(next success) = (n+1)/(n+2) = {(n + 1) / (n + 2):.4f}")

print("\nPosterior density of p after 3 heads in 3 flips, prior Beta(2,2): Beta(5, 2)")
for p in [0.1, 0.3, 0.5, 0.7, 0.8, 0.9, 0.99]:
    print(f"  p = {p:4.2f}: density {beta_pdf(p, 5, 2):.4f}")
