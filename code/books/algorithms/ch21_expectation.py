"""Chapter 21: expectations by indicator variables, checked by simulation."""
import random
from fractions import Fraction
from math import comb

random.seed(7)
trials = 20000

print("Left-to-right maxima ('new record' moments) of a random permutation: E = H_n")
for n in (5, 10, 100):
    total = 0
    for _ in range(trials):
        best, records = -1, 0
        for x in random.sample(range(n), n):
            if x > best:
                best, records = x, records + 1
        total += records
    h = sum(Fraction(1, i) for i in range(1, n + 1))
    print(f"  n = {n:3}: H_n = {float(h):.4f}   measured {total / trials:.4f}")

print("\nFixed points of a random permutation: E = 1 for every n")
for n in (3, 10, 1000):
    total = sum(sum(1 for i, x in enumerate(random.sample(range(n), n)) if i == x) for _ in range(trials // 10))
    print(f"  n = {n:4}: measured {total / (trials // 10):.4f}")

print("\nPairs of people sharing a birthday, k people and 365 days: E = C(k,2)/365")
for k in (10, 23, 28, 50):
    total = 0
    for _ in range(trials // 4):
        days = [random.randrange(365) for _ in range(k)]
        total += sum(1 for i in range(k) for j in range(i + 1, k) if days[i] == days[j])
    print(f"  k = {k:2}: predicted {comb(k, 2) / 365:.4f}   measured {total / (trials // 4):.4f}")

print("\nFlips of a coin with P(head) = p until the first head: E = 1/p")
for p in (0.5, 0.1):
    total = 0
    for _ in range(trials):
        flips = 1
        while random.random() >= p:
            flips += 1
        total += flips
    print(f"  p = {p}: predicted {1 / p:.1f}   measured {total / trials:.3f}")
