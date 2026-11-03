"""Chapter 7, part 3: perfect hashing (FKS), cuckoo hashing, Bloom filters, and Python's dict probe sequence."""
import hashlib
import math
import random

P = (1 << 61) - 1


def make_hash(m, rng):
    a, b = rng.randrange(1, P), rng.randrange(P)
    return lambda x: ((a * x + b) % P) % m


# ---------- FKS perfect hashing: two levels, O(n) space, worst-case O(1) lookups ----------
def build_fks(keys, rng):
    n = len(keys)
    tries1 = 0
    while True:                                   # level 1: n buckets, retry until sum of squares < 4n
        tries1 += 1
        h = make_hash(n, rng)
        buckets = [[] for _ in range(n)]
        for k in keys:
            buckets[h(k)].append(k)
        if sum(len(b) ** 2 for b in buckets) < 4 * n:
            break
    second, tries2 = [], 0
    for b in buckets:                             # level 2: bucket of size s gets s^2 slots, no collisions
        size = len(b) ** 2
        while True:
            tries2 += 1
            g = make_hash(max(size, 1), rng)
            slots = [None] * size
            ok = True
            for k in b:
                if slots[g(k)] is not None:
                    ok = False
                    break
                slots[g(k)] = k
            if ok:
                second.append((g, slots))
                break
    space = n + sum(len(s) for _, s in second)
    return h, second, tries1, tries2, space


def fks_lookup(table, x):
    h, second = table[0], table[1]
    g, slots = second[h(x)]
    return bool(slots) and slots[g(x)] == x


# ---------- Cuckoo hashing: every key is in one of exactly two places ----------
class Cuckoo:
    def __init__(self, m, rng):
        self.m, self.rng = m, rng
        self.rehashes, self.moves = 0, 0
        self._fresh()
    def _fresh(self):
        self.h = [make_hash(self.m, self.rng), make_hash(self.m, self.rng)]
        self.t = [[None] * self.m, [None] * self.m]
    def contains(self, x):                         # at most two probes, always
        return self.t[0][self.h[0](x)] == x or self.t[1][self.h[1](x)] == x
    def insert(self, x):
        if self.contains(x):
            return
        side = 0
        for _ in range(6 * int(math.log2(self.m)) + 6):     # give up after O(log m) kicks
            i = self.h[side](x)
            x, self.t[side][i] = self.t[side][i], x        # put x in, kick out the old occupant
            if x is None:
                return
            self.moves += 1
            side = 1 - side
        self.rehashes += 1                                   # a cycle (or a very long path): rebuild
        keys = [k for tab in self.t for k in tab if k is not None] + [x]
        self._fresh()
        for k in keys:
            self.insert(k)


# ---------- Bloom filter: k bits per key in an m-bit array ----------
class Bloom:
    def __init__(self, m, k):
        self.m, self.k, self.bits = m, k, bytearray(m)
    def _positions(self, item):
        d = hashlib.sha256(str(item).encode()).digest()
        h1, h2 = int.from_bytes(d[:8], "big"), int.from_bytes(d[8:16], "big") | 1
        return [(h1 + i * h2) % self.m for i in range(self.k)]     # double hashing (Kirsch-Mitzenmacher)
    def add(self, item):
        for p in self._positions(item):
            self.bits[p] = 1
    def __contains__(self, item):
        return all(self.bits[p] for p in self._positions(item))


# ---------- CPython's dict probe sequence (Objects/dictobject.c) ----------
def cpython_probes(h, size, count):
    mask, perturb = size - 1, h
    i = h & mask
    out = [i]
    for _ in range(count - 1):
        perturb >>= 5
        i = (i * 5 + perturb + 1) & mask
        out.append(i)
    return out


def main():
    rng = random.Random(2026)

    keys = rng.sample(range(10**12), 10000)
    table = build_fks(keys, rng)
    assert all(fks_lookup(table, k) for k in keys)
    assert not any(fks_lookup(table, k) for k in rng.sample(range(10**12, 2 * 10**12), 10000))
    print(f"FKS for n = {len(keys)}: level-1 tries {table[2]}, level-2 tries {table[3]} "
          f"for {len(keys)} buckets, total slots {table[4]} ({table[4] / len(keys):.2f} n)")

    for load in [0.25, 0.45]:
        m = 1 << 14
        c = Cuckoo(m, rng)
        ks = rng.sample(range(10**12), int(load * 2 * m))
        for k in ks:
            c.insert(k)
        assert all(c.contains(k) for k in ks)
        print(f"cuckoo, two tables of {m}, load {load:.2f}: {len(ks)} keys, "
              f"{c.moves / len(ks):.3f} kicks per insert, {c.rehashes} rehashes")

    n = 10000
    print(f"\nBloom filter, n = {n} keys, false-positive rate measured on 100000 non-keys")
    print(f"  {'bits/key':>8s} {'k':>3s} {'measured':>10s} {'(1-e^(-kn/m))^k':>16s}")
    for bits_per_key, k in [(8, 3), (8, 6), (10, 7), (16, 11)]:
        m = bits_per_key * n
        bf = Bloom(m, k)
        for i in range(n):
            bf.add(f"key{i}")
        assert all(f"key{i}" in bf for i in range(n))            # never a false negative
        fp = sum(f"other{i}" in bf for i in range(100000)) / 100000
        print(f"  {bits_per_key:8d} {k:3d} {fp:10.5f} {(1 - math.exp(-k * n / m)) ** k:16.5f}")

    print("\nCPython dict probes in a table of 8 slots:")
    for key in [3, 11, 43, 99, 1000003]:
        print(f"  hash {key}: slots {cpython_probes(hash(key), 8, 8)}")
    print("  hash(2**61) =", hash(2**61), "  hash(-1) =", hash(-1), "  hash(-2) =", hash(-2))
    d = {}
    for word in ["olympus", "gale", "jezero", "arsia", "hellas"]:
        d[word] = len(word)
    print("  insertion order kept:", list(d))


if __name__ == "__main__":
    main()
