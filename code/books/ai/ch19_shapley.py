# Chapter 19: the Shapley value (Shapley 1953), exact by permutations and by subsets,
# and approximated by sampling permutations. Three small cooperative games.
from itertools import permutations, combinations
from fractions import Fraction as F
from math import factorial
import random


def shapley_permutations(players, v):
    """Average marginal contribution over all n! orders in which the players can arrive."""
    phi = {p: F(0) for p in players}
    orders = list(permutations(players))
    for order in orders:
        before = frozenset()
        for p in order:
            phi[p] += v(before | {p}) - v(before)
            before = before | {p}
    return {p: phi[p] / len(orders) for p in players}


def shapley_subsets(players, v):
    """The same number by the subset formula: weight |S|! (n-|S|-1)! / n! for each S not containing i."""
    n = len(players)
    phi = {}
    for i in players:
        others = [p for p in players if p != i]
        total = F(0)
        for k in range(n):
            w = F(factorial(k) * factorial(n - k - 1), factorial(n))
            for S in combinations(others, k):
                S = frozenset(S)
                total += w * (v(S | {i}) - v(S))
        phi[i] = total
    return phi


def shapley_sampled(players, v, samples, seed=0):
    rng = random.Random(seed)
    phi = {p: 0.0 for p in players}
    for _ in range(samples):
        order = players[:]
        rng.shuffle(order)
        before = frozenset()
        for p in order:
            phi[p] += float(v(before | {p}) - v(before))
            before = before | {p}
    return {p: phi[p] / samples for p in players}


def fmt(d):
    return "  ".join(f"{p}: {str(x):>5}" for p, x in d.items())


# 1. Glove game: L owns a left glove, R1 and R2 each own a right glove; a pair sells for 1.
glove = ["L", "R1", "R2"]
v_glove = lambda S: F(1) if "L" in S and ("R1" in S or "R2" in S) else F(0)
print("Glove game")
print("   by permutations:", fmt(shapley_permutations(glove, v_glove)))
print("   by subsets:     ", fmt(shapley_subsets(glove, v_glove)))
# The core: allocations x >= 0 with x_L + x_R1 + x_R2 = 1 and x(S) >= v(S) for every coalition S.
grid = [(F(a, 12), F(b, 12), F(12 - a - b, 12)) for a in range(13) for b in range(13 - a)]
core = [x for x in grid if x[0] + x[1] >= 1 and x[0] + x[2] >= 1]
print("   core points on a grid of twelfths:", [tuple(str(c) for c in x) for x in core])

# 2. Weighted voting [quota 51; weights 50, 49, 1]: a coalition wins with total weight >= 51.
w = {"A": 50, "B": 49, "C": 1}
v_vote = lambda S: F(1) if sum(w[p] for p in S) >= 51 else F(0)
print("\nWeighted voting, quota 51, weights A=50, B=49, C=1 (Shapley-Shubik power)")
print("   ", fmt(shapley_permutations(list(w), v_vote)))

# 3. Airport game (Littlechild and Owen 1973): a runway long enough for the biggest plane in S
#    costs max over S of c_i; plane types need 1, 2 and 3 units.
need = {"small": 1, "medium": 2, "large": 3}
v_air = lambda S: F(max((need[p] for p in S), default=0))
print("\nAirport cost game, runway costs 1, 2, 3")
phi = shapley_permutations(list(need), v_air)
print("   ", fmt(phi), "   sum =", sum(phi.values()))

# 4. A bigger game where n! is too many: 10 players, v(S) = |S|^2 / 10 plus 1 if S holds both 0 and 9.
players = list(range(10))
v_big = lambda S: F(len(S) ** 2, 10) + (F(1) if 0 in S and 9 in S else F(0))
exact = shapley_subsets(players, v_big)
print("\n10-player game: exact (2^9 subsets per player) vs sampled orders")
print("   exact   ", " ".join(f"{float(exact[p]):.3f}" for p in players))
for m in (100, 1000, 10000):
    est = shapley_sampled(players, v_big, m)
    err = max(abs(est[p] - float(exact[p])) for p in players)
    print(f"   m={m:<5} ", " ".join(f"{est[p]:.3f}" for p in players), f"  max error {err:.3f}")
