# Chapter 24: streaming algorithms in small memory.
# Misra-Gries heavy hitters, the count-min sketch, and HyperLogLog.
from collections import Counter
import hashlib
import math
import random


def h64(item, seed=0):
    """A 64-bit hash from the standard library (blake2b with a salt)."""
    d = hashlib.blake2b(str(item).encode(), digest_size=8, salt=seed.to_bytes(16, "little"))
    return int.from_bytes(d.digest(), "little")


def misra_gries(stream, k):
    """At most k-1 counters.  Every estimate is low by at most n/k."""
    counters = {}
    for x in stream:
        if x in counters:
            counters[x] += 1
        elif len(counters) < k - 1:
            counters[x] = 1
        else:
            for y in list(counters):                # decrement all; drop zeros
                counters[y] -= 1
                if counters[y] == 0:
                    del counters[y]
    return counters


class CountMin:
    def __init__(self, width, depth):
        self.w, self.d = width, depth
        self.table = [[0] * width for _ in range(depth)]

    def add(self, x):
        for i in range(self.d):
            self.table[i][h64(x, i) % self.w] += 1

    def estimate(self, x):
        return min(self.table[i][h64(x, i) % self.w] for i in range(self.d))


class HyperLogLog:
    def __init__(self, p):
        self.p, self.m = p, 1 << p
        self.reg = [0] * self.m

    def add(self, x):
        h = h64(x)
        j = h & (self.m - 1)                        # low p bits pick a register
        rest = h >> self.p                          # the other 64 - p bits
        rank = (64 - self.p) - rest.bit_length() + 1  # position of the first 1 bit
        self.reg[j] = max(self.reg[j], rank)

    def estimate(self):
        m = self.m
        alpha = 0.7213 / (1 + 1.079 / m)
        raw = alpha * m * m / sum(2.0 ** -r for r in self.reg)
        zeros = self.reg.count(0)
        if raw <= 2.5 * m and zeros:                # small range: linear counting
            return m * math.log(m / zeros)
        return raw


# A skewed stream: item i appears with probability about proportional to 1/i.
rng = random.Random(2007)
N_ITEMS = 1000
weights = [1 / i for i in range(1, N_ITEMS + 1)]
stream = rng.choices(range(1, N_ITEMS + 1), weights, k=50000)
true = Counter(stream)
n = len(stream)

k = 20
mg = misra_gries(stream, k)
print(f"stream of {n} items, {len(true)} distinct")
print(f"Misra-Gries with {k - 1} counters (error at most n/k = {n // k}):")
for x, c in true.most_common(5):
    print(f"  item {x:3d}: true {c:5d}, estimate {mg.get(x, 0):5d}, low by {c - mg.get(x, 0)}")

cm = CountMin(width=272, depth=5)                   # e/width = 0.01, error prob e^-5
for x in stream:
    cm.add(x)
over = [cm.estimate(x) - true[x] for x in true]
print(f"count-min 5 x 272: overestimate at most {max(over)}, mean {sum(over) / len(over):.1f}, "
      f"bound eps*n = {n // 100} (holds for {sum(o <= n // 100 for o in over)}/{len(over)} items)")
print()

print("HyperLogLog (p = 10: 1024 registers of 6 bits = 768 bytes)")
print("  true distinct   estimate   error")
for distinct in (100, 1000, 10000, 100000):
    hll = HyperLogLog(10)
    for i in range(distinct):
        hll.add(f"user{i}")
        hll.add(f"user{i // 2}")                    # repeats do not change anything
    est = hll.estimate()
    print(f"  {distinct:13d}  {est:9.0f}   {100 * (est - distinct) / distinct:+5.1f}%")
print(f"  standard error 1.04/sqrt(m) = {100 * 1.04 / math.sqrt(1024):.1f}%")
