"""Chapter 7, part 2: hash tables from scratch.  Chaining, open addressing (linear probing and
double hashing) with tombstones, measured probe counts against the theory, and universal hashing."""
import math
import random

P = (1 << 61) - 1                      # a prime larger than every key we use


class UniversalHash:
    """h(x) = ((a x + b) mod p) mod m, with a, b random (Carter and Wegman)."""
    def __init__(self, m, rng):
        self.m, self.a, self.b = m, rng.randrange(1, P), rng.randrange(P)
    def __call__(self, x):
        return ((self.a * x + self.b) % P) % self.m


class ChainedTable:
    def __init__(self, rng, m=8):
        self.rng, self.n = rng, 0
        self._new(m)
    def _new(self, m):
        self.m, self.h = m, UniversalHash(m, self.rng)
        self.buckets = [[] for _ in range(m)]
    def put(self, key, value):
        b = self.buckets[self.h(key)]
        for i, (k, _) in enumerate(b):
            if k == key:
                b[i] = (key, value)
                return
        b.append((key, value))
        self.n += 1
        if self.n > self.m:            # load factor above 1: double and rehash with a new function
            old = [kv for b in self.buckets for kv in b]
            self._new(2 * self.m)
            for k, v in old:
                self.buckets[self.h(k)].append((k, v))
    def get(self, key):
        for k, v in self.buckets[self.h(key)]:
            if k == key:
                return v
        raise KeyError(key)


EMPTY, TOMB = object(), object()


class OpenTable:
    """Open addressing with a fixed number of slots m (no resizing, so we can study the load factor).
    probe='linear': h(k), h(k)+1, ...;  probe='double': h1(k) + i*h2(k), h2 odd, m a power of 2."""
    def __init__(self, m, probe, rng):
        self.m, self.probe = m, probe
        self.keys, self.vals = [EMPTY] * m, [None] * m
        self.h1, self.h2 = UniversalHash(m, rng), UniversalHash(m // 2, rng)
    def _slots(self, key):
        i = self.h1(key)
        step = 1 if self.probe == "linear" else 2 * self.h2(key) + 1
        for _ in range(self.m):
            yield i
            i = (i + step) % self.m
    def put(self, key, value):
        first_tomb = None
        for i in self._slots(key):
            k = self.keys[i]
            if k is EMPTY:
                j = i if first_tomb is None else first_tomb
                self.keys[j], self.vals[j] = key, value
                return
            if k is TOMB:
                if first_tomb is None:
                    first_tomb = i         # reuse it, but keep looking: the key may be further on
            elif k == key:
                self.vals[i] = value
                return
        if first_tomb is None:
            raise RuntimeError("table full")
        self.keys[first_tomb], self.vals[first_tomb] = key, value
    def probes(self, key):
        """(found?, number of slots examined)."""
        for count, i in enumerate(self._slots(key), 1):
            k = self.keys[i]
            if k is EMPTY:
                return False, count
            if k is not TOMB and k == key:
                return True, count
        return False, self.m
    def get(self, key):
        for i in self._slots(key):
            k = self.keys[i]
            if k is EMPTY:
                break
            if k is not TOMB and k == key:
                return self.vals[i]
        raise KeyError(key)
    def delete(self, key, tombstone=True):
        for i in self._slots(key):
            k = self.keys[i]
            if k is EMPTY:
                raise KeyError(key)
            if k is not TOMB and k == key:
                self.keys[i] = TOMB if tombstone else EMPTY
                self.vals[i] = None
                return
        raise KeyError(key)


def main():
    rng = random.Random(77)

    # 1. A chained table works like a dict.
    t, d = ChainedTable(rng), {}
    for _ in range(20000):
        k, v = rng.randrange(5000), rng.random()
        t.put(k, v); d[k] = v
    assert all(t.get(k) == d[k] for k in d)
    lengths = [len(b) for b in t.buckets]
    print(f"chained table: {t.n} keys, {t.m} buckets, load {t.n / t.m:.2f}, "
          f"longest chain {max(lengths)}, empty buckets {lengths.count(0)}")

    # 2. Probe counts in open addressing, against the formulas.
    m = 1 << 16
    print(f"\nopen addressing, m = {m}: average slots examined (measured / formula)")
    print(f"  {'alpha':>5s}  {'linear hit':>17s}  {'linear miss':>17s}  {'double hit':>17s}  {'double miss':>17s}")
    for alpha in [0.5, 0.75, 0.9]:
        row = []
        for probe in ["linear", "double"]:
            tab = OpenTable(m, probe, rng)
            keys = rng.sample(range(10**12), int(alpha * m))
            for k in keys:
                tab.put(k, 1)
            hit = sum(tab.probes(k)[1] for k in rng.sample(keys, 5000)) / 5000
            others = [rng.randrange(10**12, 2 * 10**12) for _ in range(5000)]
            miss = sum(tab.probes(k)[1] for k in others) / 5000
            if probe == "linear":           # Knuth (1962)
                fh, fm = (1 + 1 / (1 - alpha)) / 2, (1 + 1 / (1 - alpha) ** 2) / 2
            else:                           # uniform hashing
                fh, fm = math.log(1 / (1 - alpha)) / alpha, 1 / (1 - alpha)
            row += [f"{hit:6.2f} / {fh:6.2f}", f"{miss:6.2f} / {fm:6.2f}"]
        print(f"  {alpha:5.2f}  " + "  ".join(f"{c:>17s}" for c in row))

    # 3. Deletion: tombstones keep later keys reachable; emptying the slot loses them.
    for tomb in (True, False):
        tab = OpenTable(16, "linear", random.Random(1))
        keys = [k for k in range(10**6) if tab.h1(k) == 5][:3]     # three keys that all hash to slot 5
        for k in keys:
            tab.put(k, str(k))
        tab.delete(keys[0], tombstone=tomb)
        try:
            found = tab.get(keys[2]) == str(keys[2])
        except KeyError:
            found = False
        print(f"\ndelete with {'tombstone' if tomb else 'plain EMPTY'}: "
              f"later key {keys[2]} still found? {found}", end="")
    print()

    # 4. A fixed hash function can be attacked; a random one from a universal family cannot.
    m = 1024
    evil = [m * i for i in range(2000)]                 # all equal to 0 mod m
    fixed = [0] * m
    for x in evil:
        fixed[x % m] += 1
    h = UniversalHash(m, rng)
    univ = [0] * m
    for x in evil:
        univ[h(x)] += 1
    print(f"\n2000 keys that are multiples of {m}: longest chain with h(x) = x mod m: {max(fixed)}, "
          f"with a random universal h: {max(univ)}")

    # 5. The universal property checked exhaustively for a small prime.
    p, m = 37, 6
    worst = 0
    for x in range(p):
        for y in range(x + 1, p):
            coll = sum(1 for a in range(1, p) for b in range(p) if ((a * x + b) % p) % m == ((a * y + b) % p) % m)
            worst = max(worst, coll)
    total = (p - 1) * p
    print(f"\np = {p}, m = {m}: worst pair collides for {worst} of {total} choices of (a, b) "
          f"= {worst / total:.4f} <= 1/m = {1 / m:.4f}")

    # 6. The birthday paradox: the first collision among random hashes into m slots.
    m, trials, total = 10**6, 2000, 0
    for _ in range(trials):
        seen = set()
        while True:
            v = rng.randrange(m)
            if v in seen:
                break
            seen.add(v)
        total += len(seen) + 1
    print(f"\nfirst collision in {m} slots: after {total / trials:.0f} keys on average "
          f"(sqrt(pi m / 2) = {math.sqrt(math.pi * m / 2):.0f})")


if __name__ == "__main__":
    main()
