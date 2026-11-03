# Chapter 19: a small Axelrod-style round-robin tournament of the repeated prisoner's dilemma.
# Payoffs T=5, R=3, P=1, S=0 as in Axelrod's tournaments; 200 rounds per match.
import random

PAY = {("C", "C"): (3, 3), ("C", "D"): (0, 5), ("D", "C"): (5, 0), ("D", "D"): (1, 1)}


def all_c(me, other, rng): return "C"
def all_d(me, other, rng): return "D"
def rand(me, other, rng): return rng.choice("CD")
def tit_for_tat(me, other, rng): return other[-1] if other else "C"
def grim(me, other, rng): return "D" if "D" in other else "C"
def tit_for_two_tats(me, other, rng): return "D" if other[-2:] == ["D", "D"] else "C"


def alternator(me, other, rng):
    """Defect, cooperate, defect, ...: never two defections in a row."""
    return "D" if len(me) % 2 == 0 else "C"


def pavlov(me, other, rng):
    """Win-stay, lose-shift: repeat my move after payoff 3 or 5, switch after 0 or 1."""
    if not me:
        return "C"
    return me[-1] if other[-1] == "C" else ("D" if me[-1] == "C" else "C")


def joss(me, other, rng):
    """Tit for tat that sneaks in a defection 10% of the time."""
    m = tit_for_tat(me, other, rng)
    return "D" if m == "C" and rng.random() < 0.1 else m


STRATS = {"ALL-C": all_c, "ALL-D": all_d, "RANDOM": rand, "TIT-FOR-TAT": tit_for_tat,
          "GRIM": grim, "TF2T": tit_for_two_tats, "PAVLOV": pavlov, "JOSS": joss,
          "ALTERNATOR": alternator}


def match(f, g, rng, rounds=200, noise=0.0):
    a, b, sa, sb = [], [], 0, 0
    for _ in range(rounds):
        x, y = f(a, b, rng), g(b, a, rng)
        if rng.random() < noise: x = "C" if x == "D" else "D"   # a slip of the hand
        if rng.random() < noise: y = "C" if y == "D" else "D"
        pa, pb = PAY[(x, y)]
        sa += pa; sb += pb
        a.append(x); b.append(y)
    return sa, sb


def tournament(noise, repeats=5, seed=1):
    rng = random.Random(seed)
    names = list(STRATS)
    table = {(p, q): 0.0 for p in names for q in names}
    for _ in range(repeats):
        for i, p in enumerate(names):
            for q in names[i:]:                       # every pair once, and each against itself
                sp, sq = match(STRATS[p], STRATS[q], rng, noise=noise)
                table[(p, q)] += sp / repeats
                if p != q:
                    table[(q, p)] += sq / repeats
    return names, table


for noise in (0.0, 0.05):
    names, table = tournament(noise)
    total = {p: sum(table[(p, q)] for q in names) / len(names) for p in names}
    print(f"Round robin, noise {noise:.0%}: average score per 200-round match")
    for p in sorted(names, key=lambda s: -total[s]):
        print(f"   {p:<12} {total[p]:7.1f}")
    print()

# Ecological run: each generation, a strategy's share grows in proportion to its average score
# against the current population (Axelrod's "ecological" analysis). No noise.
names, table = tournament(0.0)
share = {p: 1 / len(names) for p in names}
print("Ecological simulation (population shares):")
print("   gen  " + " ".join(f"{p[:7]:>7}" for p in names))
for gen in range(0, 101):
    if gen in (0, 5, 10, 20, 50, 100):
        print(f"   {gen:>3}  " + " ".join(f"{share[p]:7.3f}" for p in names))
    fit = {p: sum(share[q] * table[(p, q)] for q in names) for p in names}
    mean = sum(share[p] * fit[p] for p in names)
    share = {p: share[p] * fit[p] / mean for p in names}

print("\nThree matches traced (first 12 rounds):")
for p, q in (("TIT-FOR-TAT", "JOSS"), ("PAVLOV", "ALL-D"), ("TF2T", "ALTERNATOR")):
    rng = random.Random(7)
    a, b = [], []
    for _ in range(12):
        x, y = STRATS[p](a, b, rng), STRATS[q](b, a, rng)
        a.append(x); b.append(y)
    print(f"   {p:<12} {''.join(a)}\n   {q:<12} {''.join(b)}\n")
