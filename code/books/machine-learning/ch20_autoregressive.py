"""Chapter 20: autoregressive models as generative models. Character n-gram
models of orders 0 to 4 with add-k smoothing: exact log-likelihood by the chain
rule, bits per character on held-out text, and samples."""
import numpy as np
from collections import defaultdict

rng = np.random.default_rng(1948)
train = ("a rover on mars cannot wait for advice from home. a radio signal takes between four and "
         "twenty four minutes to cross the gap, so the rover must look, think and drive by itself. "
         "it takes pictures of the ground ahead, builds a map of rocks and slopes, and plans a path "
         "that keeps its wheels safe. then it drives a short way, stops, looks again and plans again. "
         "at the end of the day it sends its pictures home, and the team on earth chooses where it "
         "should go next. the rover sleeps through the cold night and wakes when the sun returns. "
         "a good plan is short and safe. a bad plan ends in sand. the rover would rather stop than "
         "guess, because nobody can come to help it if it gets stuck. ")
test = ("the rover looks at the rocks ahead and plans a safe path. it drives a short way and stops. "
        "then it sends a picture home and waits for the sun. ")
chars = sorted(set(train + test))
V = len(chars)


def fit(text, n):
    """Counts of next character after each context of n - 1 characters."""
    counts = defaultdict(lambda: np.zeros(V))
    pad = "~" * (n - 1) + text
    for i in range(n - 1, len(pad)):
        counts[pad[i - n + 1:i]][chars.index(pad[i])] += 1
    return counts


def probs(counts, ctx, k=0.1):
    c = counts.get(ctx, np.zeros(V))
    return (c + k) / (c.sum() + k * V)             # add-k smoothing: no probability is ever zero


def log2_likelihood(counts, text, n):
    pad = "~" * (n - 1) + text
    return sum(np.log2(probs(counts, pad[i - n + 1:i])[chars.index(pad[i])])
               for i in range(n - 1, len(pad)))


print(f"training text {len(train)} characters, held-out text {len(test)}, alphabet {V}")
print()
print("1. the chain rule, exactly: log2 p('the') under the order-3 model is a sum of three terms")
c3 = fit(train, 3)
total = 0.0
for i, ch in enumerate("the"):
    ctx = ("~~" + "the")[i:i + 2]
    lp = np.log2(probs(c3, ctx)[chars.index(ch)])
    total += lp
    print(f"   log2 p({ch!r} | {ctx!r}) = {lp:7.3f}")
print(f"   total {total:.3f} = log2_likelihood {log2_likelihood(c3, 'the', 3):.3f}")

print()
print("2. bits per character (lower is better; uniform guessing = log2 V =", f"{np.log2(V):.2f})")
print(f"   {'order n':>8s}{'train':>8s}{'held-out':>10s}")
for n in range(1, 6):
    c = fit(train, n)
    print(f"   {n:8d}{-log2_likelihood(c, train, n) / len(train):8.3f}"
          f"{-log2_likelihood(c, test, n) / len(test):10.3f}")

print()
print("3. samples after the prompt 'the rover ': draw each next character from")
print("   p(x_t | previous n - 1 characters), with very light smoothing (k = 0.001)")
for n in (1, 2, 3, 5):
    c = fit(train, n)
    out = "the rover "
    for _ in range(70):
        ctx = out[len(out) - n + 1:] if n > 1 else ""
        out += chars[rng.choice(V, p=probs(c, ctx, k=0.001))]
    print(f"   n = {n}: {out!r}")
