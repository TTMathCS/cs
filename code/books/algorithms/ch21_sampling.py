"""Chapter 21: the Fisher-Yates shuffle, a broken shuffle, and reservoir sampling."""
import random
from itertools import product
from collections import Counter

random.seed(2021)


def fisher_yates(a, choices):
    """Shuffle a in place. choices[i] plays the role of random.randint(i, n-1)."""
    n = len(a)
    for i in range(n - 1):
        j = choices[i]
        a[i], a[j] = a[j], a[i]
    return a


def naive_shuffle(a, choices):
    """The common mistake: swap every position with ANY position, j in 0..n-1."""
    for i in range(len(a)):
        j = choices[i]
        a[i], a[j] = a[j], a[i]
    return a


n = 3
print("All equally likely choice sequences for n = 3, and the permutation each one makes")
fy = Counter()
for choices in product(*[range(i, n) for i in range(n - 1)]):        # j0 in 0..2, j1 in 1..2
    fy["".join(fisher_yates(list("ABC"), choices))] += 1
naive = Counter()
for choices in product(range(n), repeat=n):                             # 3^3 = 27 sequences
    naive["".join(naive_shuffle(list("ABC"), choices))] += 1
print(f"  Fisher-Yates ({sum(fy.values())} sequences):", dict(sorted(fy.items())))
print(f"  naive        ({sum(naive.values())} sequences):", dict(sorted(naive.items())))


def reservoir(stream, k):
    """Algorithm R: keep a uniform sample of k items from a stream of unknown length."""
    sample = []
    for t, item in enumerate(stream, start=1):
        if t <= k:
            sample.append(item)
        else:
            j = random.randint(1, t)            # uniform in 1..t
            if j <= k:
                sample[j - 1] = item            # the new item replaces a uniformly random one
    return sample


print("\nReservoir sampling k = 3 from a stream of 10 items, 200000 runs")
runs, k, N = 200000, 3, 10
hits, sets = Counter(), Counter()
for _ in range(runs):
    s = reservoir(range(N), k)
    hits.update(s)
    sets[frozenset(s)] += 1
print("  frequency each item is kept (should be k/N = 0.3):")
print("   ", " ".join(f"{hits[i] / runs:.3f}" for i in range(N)))
expected = runs / 120                            # C(10, 3) = 120 possible samples
print(f"  {len(sets)} different samples seen (C(10,3) = 120); counts range"
      f" {min(sets.values())} to {max(sets.values())}, expected {expected:.0f} each")

print("\nLibrary versions: random.shuffle is Fisher-Yates, random.sample draws without replacement")
deck = list(range(10))
random.shuffle(deck)
print("  random.shuffle:", deck, "  random.sample:", random.sample(range(100), 5))
