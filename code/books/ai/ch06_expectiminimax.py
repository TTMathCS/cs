# Chapter 6: games with chance. Expectiminimax on a small tree, and a dice game solved exactly.
from functools import lru_cache
from itertools import product

# 1. A tiny tree: MAX chooses move A or B; then a coin with P(heads) = 0.9 decides the leaf value.
tree = {"A": [(0.9, 2), (0.1, 3)], "B": [(0.9, 1), (0.1, 40)]}


def decide(transform):
    exp = {m: sum(p * transform(v) for p, v in outs) for m, outs in tree.items()}
    return max(exp, key=exp.get), exp


for name, f in (("values as given", lambda v: v), ("values squared", lambda v: v * v),
                ("values replaced by rank", lambda v: {1: 1, 2: 2, 3: 3, 40: 4}[v])):
    best, exp = decide(f)
    print(f"{name:24s} expected A = {exp['A']:7.2f}  B = {exp['B']:7.2f}  -> choose {best}")

# 2. A dice game. Players alternate. On your turn choose to roll 1, 2 or 3 dice. If any die shows 1,
#    you score 1 point; otherwise you score the sum. First to reach TARGET points wins.
TARGET = 20


def outcome_distribution(k):
    dist = {}
    for faces in product(range(1, 7), repeat=k):
        pts = 1 if 1 in faces else sum(faces)
        dist[pts] = dist.get(pts, 0) + 1 / 6 ** k
    return dist


DIST = {k: outcome_distribution(k) for k in (1, 2, 3)}


@lru_cache(maxsize=None)
def win_prob(me, opp):
    """Probability that the player about to move wins, with best play by both (expectimax in negamax form)."""
    return max(chance_value(me, opp, k) for k in (1, 2, 3))


def chance_value(me, opp, k):
    total = 0.0
    for pts, p in DIST[k].items():
        total += p * (1.0 if me + pts >= TARGET else 1.0 - win_prob(opp, me + pts))
    return total


def best_dice(me, opp):
    vals = [chance_value(me, opp, k) for k in (1, 2, 3)]
    if max(vals) - min(vals) < 1e-12:
        return "*"                                   # all three choices are equally good
    return str(1 + vals.index(max(vals)))


for k in (1, 2, 3):
    mean = sum(pts * p for pts, p in DIST[k].items())
    print(f"\nroll {k} dice: P(score only 1) = {DIST[k][1]:.3f}, expected points {mean:.3f}", end="")
print("\n")
print(f"first to {TARGET}: P(first player wins) with best play by both = {win_prob(0, 0):.4f}")
print("best number of dice (rows: my score, columns: opponent's score; * = all equal)")
print("      " + "".join(f"{o:3d}" for o in range(0, TARGET, 2)))
for me in range(0, TARGET, 2):
    print(f"  {me:3d} " + "".join(f"{best_dice(me, o):>3s}" for o in range(0, TARGET, 2)))


@lru_cache(maxsize=None)
def win_vs_fixed(me, opp, my_turn, fixed):
    """P(the optimal player wins) when the opponent always rolls `fixed` dice. me = optimal player's score."""
    if my_turn:
        return max(sum(p * (1.0 if me + pts >= TARGET else win_vs_fixed(me + pts, opp, False, fixed))
                       for pts, p in DIST[k].items()) for k in (1, 2, 3))
    return sum(p * (0.0 if opp + pts >= TARGET else win_vs_fixed(me, opp + pts, True, fixed))
               for pts, p in DIST[fixed].items())


for fixed in (1, 2, 3):
    print(f"optimal player moving first vs 'always {fixed} dice': wins with probability "
          f"{win_vs_fixed(0, 0, True, fixed):.4f}")
