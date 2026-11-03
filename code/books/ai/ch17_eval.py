# Chapter 17: four evaluation calculations for language models, from scratch.
# 1. self-consistency: majority vote over sampled reasoning chains, computed exactly;
# 2. pass@k: the unbiased estimator versus the naive one;
# 3. contamination: n-gram overlap between a benchmark and a training text;
# 4. noise: how big a gap on a 200-question benchmark means anything.
import math
import re
import numpy as np


def compositions(m, parts):
    """All ways to write m as an ordered sum of `parts` non-negative integers."""
    if parts == 1:
        yield (m,)
        return
    for first in range(m + 1):
        for rest in compositions(m - first, parts - 1):
            yield (first,) + rest


def majority_correct(probs, m):
    """Exact probability that the most common of m sampled answers is answer 0 (ties split evenly)."""
    total = 0.0
    for counts in compositions(m, len(probs)):
        pr = math.factorial(m)
        for c, p in zip(counts, probs):
            pr *= p ** c / math.factorial(c)
        top = max(counts)
        if counts[0] == top:
            total += pr / counts.count(top)
    return total


print("1. self-consistency: P(majority answer is right) after m sampled chains")
cases = {"right 0.4, four wrong answers 0.15 each": [0.4, 0.15, 0.15, 0.15, 0.15],
         "right 0.4, one common wrong answer 0.45": [0.4, 0.45, 0.05, 0.05, 0.05]}
for name, probs in cases.items():
    row = "  ".join(f"m={m}: {majority_correct(probs, m):.3f}" for m in (1, 5, 15, 41))
    print(f"   {name}\n      {row}")


def pass_at_k(n, c, k):
    """Unbiased: 1 - C(n-c, k) / C(n, k), the chance a random k of the n samples include a correct one."""
    return 1.0 if n - c < k else 1.0 - math.comb(n - c, k) / math.comb(n, k)


print("\n2. pass@k with n = 20 samples per problem, true per-sample success p = 0.1, k = 10")
true = 1 - 0.9 ** 10
pmf = [math.comb(20, c) * 0.1 ** c * 0.9 ** (20 - c) for c in range(21)]   # c ~ Binomial(20, 0.1)
unb = sum(w * pass_at_k(20, c, 10) for c, w in enumerate(pmf))           # exact expectations
naive = sum(w * (1 - (1 - c / 20) ** 10) for c, w in enumerate(pmf))
print(f"   true pass@10 = 1 - 0.9^10 = {true:.4f}")
print(f"   expected value of the unbiased estimator {unb:.4f}, of the naive 1-(1-c/n)^k {naive:.4f}")
print(f"   one problem with c = 3 correct out of 20: pass@1 {pass_at_k(20, 3, 1):.4f}, "
      f"pass@5 {pass_at_k(20, 3, 5):.4f}, pass@10 {pass_at_k(20, 3, 10):.4f}")

print("\n3. contamination check: 8-gram overlap between benchmark items and a training text")
train_text = """notes from a forum . a train leaves the station at 3 pm travelling at 60 km per hour
how far has it gone by 5 pm . answer 120 km . other posts follow . if a rover drives 40 metres
every hour for 6 hours how many metres does it drive in total . people discussed it at length ."""
bench = ["A train leaves the station at 3 pm travelling at 60 km per hour. How far has it gone by 5 pm?",
         "If a rover drives 40 metres every hour for 6 hours, how many metres does it drive in total?",
         "A rover moves 40 metres per hour. After six hours, what total distance has it covered?",
         "A tank holds 50 litres and leaks 2 litres per hour. When is it half empty?"]


def toks(s):
    return re.findall(r"[a-z0-9]+", s.lower())


def ngrams(t, n):
    return {tuple(t[i:i + n]) for i in range(len(t) - n + 1)}


train_grams = ngrams(toks(train_text), 8)
for i, b in enumerate(bench, 1):
    g = ngrams(toks(b), 8)
    hit = len(g & train_grams)
    print(f"   item {i}: {hit:2d} of {len(g):2d} 8-grams seen in training -> {'CONTAMINATED' if hit else 'clean'}")

print("\n4. noise: two models, 200 questions each")
n, a, b = 200, 0.72, 0.75
se = math.sqrt(a * (1 - a) / n)
print(f"   accuracy 0.72: standard error {se:.4f}, 95% interval {a - 1.96 * se:.3f} to {a + 1.96 * se:.3f}")
rng = np.random.default_rng(1)
same = rng.binomial(n, 0.735, size=(200000, 2)) / n   # two equally good models (true accuracy 0.735)
print(f"   if both are truly 0.735, P(observed gap >= 0.03) = {np.mean(np.abs(same[:, 0] - same[:, 1]) >= 0.03 - 1e-12):.3f}")
