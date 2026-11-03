# Chapter 11: a knowledge graph as a data structure.
# 1. A triple store with an index, and conjunctive queries (basic graph patterns, as in SPARQL) by backtracking join.
# 2. RDFS-style inference by forward chaining: subclass and subproperty closure, types from domains and ranges.
# 3. Link prediction with TransE (Bordes et al. 2013) in NumPy: entities and relations become vectors with
#    head + relation ≈ tail, trained on some triples and asked to rank the missing ones.
from collections import defaultdict
import numpy as np

TRIPLES = [
    ("Curiosity", "type", "Rover"), ("Perseverance", "type", "Rover"), ("Ingenuity", "type", "Helicopter"),
    ("Rover", "subClassOf", "Spacecraft"), ("Helicopter", "subClassOf", "Spacecraft"),
    ("Lander", "subClassOf", "Spacecraft"), ("Spacecraft", "subClassOf", "Machine"),
    ("Gale", "type", "Crater"), ("Jezero", "type", "Crater"), ("Crater", "subClassOf", "Landform"),
    ("Curiosity", "landedIn", "Gale"), ("Perseverance", "landedIn", "Jezero"),
    ("Ingenuity", "carriedBy", "Perseverance"),
    ("landedIn", "range", "Landform"), ("landedIn", "domain", "Spacecraft"),
    ("carriedBy", "subPropertyOf", "travelledWith"),
    ("Curiosity", "hasInstrument", "ChemCam"), ("Perseverance", "hasInstrument", "SuperCam"),
    ("ChemCam", "type", "Spectrometer"), ("SuperCam", "type", "Spectrometer"),
    ("Spectrometer", "subClassOf", "Instrument"),
]


class TripleStore:
    def __init__(self, triples):
        self.triples = set()
        self.by_p = defaultdict(set)          # an index on the predicate; real stores index all six orders
        for t in triples:
            self.add(t)

    def add(self, t):
        if t in self.triples:
            return False
        self.triples.add(t)
        self.by_p[t[1]].add(t)
        return True

    def match(self, pattern, binding):
        s, p, o = [binding.get(x, x) for x in pattern]
        pool = self.by_p[p] if not p.startswith("?") else self.triples
        for t in pool:
            b = dict(binding)
            ok = True
            for pat, val in zip((s, p, o), t):
                if pat.startswith("?"):
                    if b.setdefault(pat, val) != val:
                        ok = False
                        break
                elif pat != val:
                    ok = False
                    break
            if ok:
                yield b

    def query(self, patterns, binding=None):
        """All bindings that satisfy every pattern (a join, solved left to right with backtracking)."""
        binding = {} if binding is None else binding
        if not patterns:
            yield binding
            return
        for b in self.match(patterns[0], binding):
            yield from self.query(patterns[1:], b)


RDFS_RULES = [   # (premises, conclusion): forward-chained to a fixed point
    ([("?c", "subClassOf", "?d"), ("?d", "subClassOf", "?e")], ("?c", "subClassOf", "?e")),
    ([("?x", "type", "?c"), ("?c", "subClassOf", "?d")], ("?x", "type", "?d")),
    ([("?p", "subPropertyOf", "?q"), ("?x", "?p", "?y")], ("?x", "?q", "?y")),
    ([("?p", "domain", "?c"), ("?x", "?p", "?y")], ("?x", "type", "?c")),
    ([("?p", "range", "?c"), ("?x", "?p", "?y")], ("?y", "type", "?c")),
]


def rdfs_closure(store):
    rounds = 0
    while True:
        new = []
        for premises, concl in RDFS_RULES:
            for b in store.query(premises):
                new.append(tuple(b.get(x, x) for x in concl))
        added = sum(store.add(t) for t in new)
        rounds += 1
        if not added:
            return rounds


# ---------------------------------------------------------------- TransE
def transe_demo(seed=0, n=12, dim=8, lr=0.02, margin=1.0, epochs=1500):
    """Energy of a triple: ||e_h + r - e_t||^2 (squared distance). Train so that true triples have energy at least
    'margin' below corrupted ones (head or tail replaced by a random entity), by stochastic gradient descent."""
    rng = np.random.default_rng(seed)
    east = [(i + 1, 0, i) for i in range(n - 1)]  # relation 0: P(i+1) eastOf P(i)
    west = [(i, 1, i + 1) for i in range(n - 1)]  # relation 1: P(i) westOf P(i+1)
    test = [west[k] for k in (1, 4, 7, 9)]        # hide four westOf facts
    train = east + [t for t in west if t not in test]
    E = rng.normal(0, 0.5, (n, dim))
    R = rng.normal(0, 0.5, (2, dim))

    def energy(h, r, t):
        d = E[h] + R[r] - E[t]
        return d @ d

    for epoch in range(epochs):
        for idx in rng.permutation(len(train)):
            h, r, t = train[idx]
            if rng.random() < 0.5:
                h2, t2 = int(rng.integers(n)), t      # corrupt the head ...
            else:
                h2, t2 = h, int(rng.integers(n))      # ... or the tail
            if (h2, t2) == (h, t):
                continue
            if margin + energy(h, r, t) - energy(h2, r, t2) > 0:        # the hinge is active: take a gradient step
                gp = 2 * (E[h] + R[r] - E[t])
                gn = 2 * (E[h2] + R[r] - E[t2])
                E[h] -= lr * gp
                E[t] += lr * gp
                E[h2] += lr * gn
                E[t2] -= lr * gn
                R[r] -= lr * (gp - gn)

    def rank(h, r, t):
        scores = [energy(h, r, x) for x in range(n)]
        return 1 + sum(sc < scores[t] for sc in scores)

    ranks = [rank(*t) for t in test]
    train_ranks = [rank(*t) for t in train]
    cos = R[0] @ R[1] / (np.linalg.norm(R[0]) * np.linalg.norm(R[1]))
    return test, ranks, train_ranks, cos, n


if __name__ == "__main__":
    store = TripleStore(TRIPLES)
    print(f"1. A triple store with {len(store.triples)} triples")
    q = [("?r", "type", "Rover"), ("?r", "landedIn", "?c"), ("?r", "hasInstrument", "?i")]
    print("  rovers, where they landed, and their instruments:")
    for b in sorted(store.query(q), key=lambda b: b["?r"]):
        print(f"    {b['?r']:<13} {b['?c']:<7} {b['?i']}")
    print("  machines before inference:", sorted(b["?x"] for b in store.query([("?x", "type", "Machine")])))
    print()
    rounds = rdfs_closure(store)
    print(f"2. RDFS inference: {len(store.triples)} triples after {rounds} rounds")
    print("  machines after inference:", sorted(b["?x"] for b in store.query([("?x", "type", "Machine")])))
    print("  landforms:", sorted(b["?x"] for b in store.query([("?x", "type", "Landform")])))
    print("  travelled with:", sorted((b["?x"], b["?y"]) for b in store.query([("?x", "travelledWith", "?y")])))
    print("  instruments:", sorted(b["?x"] for b in store.query([("?x", "type", "Instrument")])))
    print()
    test, ranks, train_ranks, cos, n = transe_demo()
    print(f"3. TransE on {n} places in a line: eastOf for all neighbours, westOf for some")
    for (h, r, t), rk in zip(test, ranks):
        print(f"  hidden fact P{h} westOf P{t}: true tail ranked {rk} of {n}")
    print(f"  hidden facts: mean rank {np.mean(ranks):.2f}, hits@1 {np.mean([r == 1 for r in ranks]):.2f};"
          f"  training facts: mean rank {np.mean(train_ranks):.2f}")
    other = [np.mean(transe_demo(seed)[1]) for seed in (1, 2, 3)]
    print("  mean rank on the hidden facts with seeds 1, 2, 3:", ", ".join(f"{m:.2f}" for m in other))
    print(f"  cosine(eastOf vector, westOf vector) = {cos:.2f}  (an inverse relation should point the other way)")
