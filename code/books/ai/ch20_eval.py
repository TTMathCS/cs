# Chapter 20: the statistics of testing. Confidence intervals for a benchmark score, a paired
# comparison of two models, what "no failures in n tests" proves, contamination, and why searching
# for failures (red-teaming) beats sampling at random.
import math
import numpy as np

rng = np.random.default_rng(0)


def wilson(k, n, z=1.96):
    """95% Wilson score interval for a proportion k/n."""
    p = k / n
    c = (p + z * z / (2 * n)) / (1 + z * z / n)
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / (1 + z * z / n)
    return c - h, c + h


print("1. A model answers 82% of the benchmark correctly. How sure is that number?")
for n in (100, 1000, 10000):
    lo, hi = wilson(round(0.82 * n), n)
    print(f"   n = {n:>5} items: 95% interval {lo:.3f} to {hi:.3f}   (width {hi - lo:.3f})")

z = rng.normal(0, 1.5, 1_000_000)                      # to compute the models' true accuracies
ta, tb = np.mean(1 / (1 + np.exp(-(z + 1.6)))), np.mean(1 / (1 + np.exp(-(z + 1.85))))
print(f"\n2. Models A and B on the same 500 items (true accuracies {ta:.3f} and {tb:.3f})")
skill = rng.normal(0, 1.5, 500)                       # item difficulty shared by both models
a = rng.random(500) < 1 / (1 + np.exp(-(skill + 1.6)))
b = rng.random(500) < 1 / (1 + np.exp(-(skill + 1.85)))
diff = b.mean() - a.mean()
boots = []
for _ in range(5000):
    i = rng.integers(0, 500, 500)                     # resample ITEMS, keeping each item's pair together
    boots.append(b[i].mean() - a[i].mean())
lo, hi = np.percentile(boots, [2.5, 97.5])
n01, n10 = int(np.sum(~a & b)), int(np.sum(a & ~b))
# exact McNemar test: under "no difference" the discordant items split 50/50
k, N = min(n01, n10), n01 + n10
pval = min(1.0, 2 * sum(math.comb(N, j) for j in range(k + 1)) / 2 ** N)
print(f"   measured A {a.mean():.3f}, B {b.mean():.3f}, difference {diff:+.3f}")
print(f"   paired bootstrap 95% interval for B - A: {lo:+.3f} to {hi:+.3f}")
print(f"   items only B got right {n01}, only A got right {n10}; exact McNemar p = {pval:.3f}")

print("\n3. Zero failures in n independent tests: the 95% upper bound on the failure rate")
for n in (300, 3000, 30000):
    exact = 1 - 0.05 ** (1 / n)
    print(f"   n = {n:>5}: exact bound {exact:.2e}, rule of three 3/n = {3 / n:.2e}")
need = math.ceil(math.log(0.05) / math.log(1 - 1e-4))
print(f"   tests needed to show a failure rate below 1 in 10 000: {need}")

print("\n4. Contamination: a model that is right on 60% of NEW questions has memorised part of the test")
for frac in (0.0, 0.1, 0.3, 0.5):
    seen = rng.random(2000) < frac
    right = np.where(seen, True, rng.random(2000) < 0.6)
    fresh = rng.random(2000) < 0.6                    # a fresh set written after the training data
    print(f"   {frac:.0%} of the test leaked: benchmark score {right.mean():.3f}, fresh-set score {fresh.mean():.3f}")

print("\n5. Finding a rare failure in a 10-dimensional input space")
c = np.full(10, 0.6)
def margin(x):                                         # the system fails when the margin is negative
    return np.linalg.norm(x - c, axis=-1) - 0.45
X = rng.uniform(-1, 1, (200000, 10))
fails = margin(X) < 0
first = int(np.argmax(fails)) + 1 if fails.any() else None
print(f"   random testing: {fails.sum()} failures in 200000 queries"
      + (f", first at query {first}" if first else ""))
x = rng.uniform(-1, 1, 10); queries = 1; step = 0.3
while margin(x) >= 0:
    cand = np.clip(x + rng.normal(0, step, 10), -1, 1); queries += 1
    if margin(cand) < margin(x):
        x = cand                                       # keep moves that bring the system nearer to failing
print(f"   local search on the margin: first failure after {queries} queries")
