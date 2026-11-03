# Chapter 25: (1) a learned index in the spirit of Kraska et al. 2018: a two-stage
# piecewise-linear model predicts a key's position, a bounded search fixes the error.
# (2) ski rental with a prediction (Purohit, Svitkina and Kumar 2018).
import bisect
import math
import random

rng = random.Random(2018)
keys = sorted({int(rng.lognormvariate(10, 1.5)) for _ in range(200000)})
n = len(keys)


def fit_line(xs, ys):
    """Least squares y = a x + b (stdlib only)."""
    m = len(xs)
    mx, my = sum(xs) / m, sum(ys) / m
    var = sum((x - mx) ** 2 for x in xs)
    a = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / var if var else 0.0
    return a, my - a * mx


# Stage 1: one line over all keys picks one of S second-stage models.
S = 256
a0, b0 = fit_line(keys, [i * S / n for i in range(n)])
route = lambda k: min(S - 1, max(0, int(a0 * k + b0)))
buckets = [[] for _ in range(S)]
for i, k in enumerate(keys):
    buckets[route(k)].append(i)
# Stage 2: a line per bucket, and the largest error it makes on its own keys.
models = []
for idx in buckets:
    if not idx:
        models.append((0.0, 0.0, 0))
        continue
    xs = [keys[i] for i in idx]
    a, b = fit_line(xs, idx) if len(idx) > 1 else (0.0, float(idx[0]))
    err = max(abs(int(round(a * x + b)) - i) for x, i in zip(xs, idx))
    models.append((a, b, err))


def learned_lookup(k):
    a, b, err = models[route(k)]
    guess = int(round(a * k + b))
    lo, hi = max(0, guess - err), min(n, guess + err + 1)
    probes = 0
    while lo < hi:                                  # binary search in the window only
        probes += 1
        mid = (lo + hi) // 2
        if keys[mid] < k:
            lo = mid + 1
        else:
            hi = mid
    return lo, probes


queries = rng.sample(keys, 2000)
total_learned = 0
for q in queries:
    pos, probes = learned_lookup(q)
    assert keys[pos] == q and pos == bisect.bisect_left(keys, q)
    total_learned += probes
errs = sorted(e for _, _, e in models)
print(f"{n} distinct lognormal keys; {S} second-stage linear models")
print(f"  model error: median {errs[S // 2]}, max {errs[-1]} positions")
print(f"  probes per lookup: learned index {total_learned / len(queries):.1f}, "
      f"binary search {math.ceil(math.log2(n + 1))}")
print()


# Ski rental with a prediction y of the number of days (buy price B).
def with_prediction(days, y, B, lam):
    t = math.ceil(lam * B) if y >= B else math.ceil(B / lam)   # buy on day t
    return days if days < t else (t - 1) + B


B = 100
print(f"ski rental with predictions, B = {B}")
print("  lambda   worst ratio when prediction is right   worst ratio overall   1+lam   1+1/lam")
for lam in (1.0, 0.5, 0.25, 0.1):
    right = max(with_prediction(d, d, B, lam) / min(d, B) for d in range(1, 400))
    overall = max(with_prediction(d, y, B, lam) / min(d, B)
                  for d in range(1, 400) for y in (0, 10 * B))
    print(f"  {lam:5.2f}   {right:37.3f}   {overall:19.3f}   {1 + lam:5.2f}   {1 + 1 / lam:7.2f}")
