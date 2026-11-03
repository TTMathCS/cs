# Chapter 23: greedy set cover, with the "price" bookkeeping of the H_n proof,
# and an instance on which greedy really is about log2(n)/2 times optimal.
from fractions import Fraction
import itertools


def greedy_set_cover(universe, sets):
    uncovered = set(universe)
    chosen, price = [], {}
    while uncovered:
        name = max(sets, key=lambda s: (len(sets[s] & uncovered), s))
        new = sets[name] & uncovered
        if not new:
            raise ValueError("the sets do not cover the universe")
        for x in new:                       # each new element pays 1/|new|
            price[x] = Fraction(1, len(new))
        chosen.append(name)
        uncovered -= new
    return chosen, price


def exact_set_cover(universe, sets):
    names = sorted(sets)
    for k in range(1, len(names) + 1):
        for combo in itertools.combinations(names, k):
            if set().union(*(sets[c] for c in combo)) >= set(universe):
                return list(combo)


def harmonic(n):
    return sum(Fraction(1, i) for i in range(1, n + 1))


# The worked example of section 23.3
U = range(1, 13)
S = {
    "A": {1, 2, 3, 4, 5, 6},
    "B": {5, 6, 8, 9},
    "C": {1, 4, 7, 10},
    "D": {2, 5, 7, 8, 11},
    "E": {3, 6, 9, 12},
    "F": {10, 11},
}
chosen, price = greedy_set_cover(U, S)
print("greedy picks:", chosen)
for x in sorted(price):
    print(f"  element {x:2d} pays {price[x]}")
print("total price =", sum(price.values()), "= number of sets", len(chosen))
print("optimal:", exact_set_cover(U, S))
print()

# The bad family: two rows R0, R1 cover everything (optimum 2), but block S_i
# with 2^(i+1) elements always looks a little bigger to greedy than what is left of a row.
for k in range(2, 7):
    rows = [set(), set()]
    sets = {}
    start = 0
    for i in range(k):
        size = 2 ** i                       # block i has 2^i elements in each row
        block = set()
        for r in range(2):
            elems = set(range(start, start + size))
            start += size
            rows[r] |= elems
            block |= elems
        sets[f"S{i}"] = block
    universe = rows[0] | rows[1]
    sets["R0"], sets["R1"] = rows[0], rows[1]
    greedy, _ = greedy_set_cover(universe, sets)
    n = len(universe)
    print(f"k={k}: n={n:3d}  greedy uses {len(greedy)} sets {greedy}, optimum 2, "
          f"H_n = {float(harmonic(n)):.2f}")
