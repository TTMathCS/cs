# Chapter 19: social choice. Four voting rules on one profile of 21 voters,
# a Condorcet cycle, and how often cycles happen when voters rank at random.
from itertools import permutations, product
import math
import random

PROFILE = [("ABCD", 7), ("DCBA", 6), ("BCDA", 5), ("CDAB", 3)]   # (ranking best first, number of voters)
CANDS = "ABCD"


def plurality(P):
    s = {c: 0 for c in CANDS}
    for r, k in P:
        s[r[0]] += k
    return s


def borda(P):
    s = {c: 0 for c in CANDS}
    for r, k in P:
        for pos, c in enumerate(r):
            s[c] += k * (len(r) - 1 - pos)
    return s


def instant_runoff(P):
    left, rounds = set(CANDS), []
    while len(left) > 1:
        s = {c: 0 for c in sorted(left)}
        for r, k in P:
            s[next(c for c in r if c in left)] += k
        loser = min(s, key=s.get)
        rounds.append((dict(s), loser))
        left.remove(loser)
    return left.pop(), rounds


def pairwise(P, a, b):
    return sum(k for r, k in P if r.index(a) < r.index(b))


def condorcet_winner(P, cands):
    n = sum(k for _, k in P)
    for a in cands:
        if all(2 * pairwise(P, a, b) > n for b in cands if b != a):
            return a
    return None


print("Profile:", ", ".join(f"{k} x {'>'.join(r)}" for r, k in PROFILE))
s = plurality(PROFILE)
print("plurality scores", s, "-> winner", max(s, key=s.get))
s = borda(PROFILE)
print("Borda scores    ", s, "-> winner", max(s, key=s.get))
w, rounds = instant_runoff(PROFILE)
for sc, lo in rounds:
    print("instant runoff round", sc, "eliminate", lo)
print("instant runoff winner", w)
print("pairwise majorities (row beats column by this many of 21):")
print("      " + "   ".join(CANDS))
for a in CANDS:
    print("   " + a + "  " + "  ".join(f"{pairwise(PROFILE, a, b):>2}" if a != b else " -" for b in CANDS))
print("Condorcet winner:", condorcet_winner(PROFILE, CANDS))

cyc = [("ABC", 1), ("BCA", 1), ("CAB", 1)]
print("\nThree voters A>B>C, B>C>A, C>A>B: A beats B", pairwise(cyc, "A", "B"), "to 1, B beats C",
      pairwise(cyc, "B", "C"), "to 1, C beats A", pairwise(cyc, "C", "A"), "to 1; Condorcet winner:",
      condorcet_winner(cyc, "ABC"))

# Impartial culture: every voter picks one of the 6 rankings of A, B, C uniformly at random.
orders = ["".join(p) for p in permutations("ABC")]
cycles = 0
for prof in product(orders, repeat=3):
    if condorcet_winner([(r, 1) for r in prof], "ABC") is None:
        cycles += 1
print(f"\nn=3 voters, all 216 profiles enumerated: no Condorcet winner in {cycles} = {cycles / 216:.4f}")
rng = random.Random(0)
for n in (11, 101, 1001):
    trials, none = 20000 if n < 1001 else 4000, 0
    for _ in range(trials):
        counts = {r: 0 for r in orders}
        for _ in range(n):
            counts[rng.choice(orders)] += 1
        if condorcet_winner(list(counts.items()), "ABC") is None:
            none += 1
    print(f"n={n:<5} voters, {trials} random profiles: no Condorcet winner in {none / trials:.4f}")
print(f"limit as n grows (Guilbaud 1952): 1/4 - 3/(2 pi) arcsin(1/3) = {0.25 - 3 / (2 * math.pi) * math.asin(1 / 3):.4f}")
