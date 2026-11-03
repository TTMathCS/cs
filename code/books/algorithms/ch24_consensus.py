# Chapter 24: consensus with crash failures in synchronous rounds (FloodSet).
# Every process floods the set of values it has seen; after f+1 rounds each
# decides the smallest.  The run below shows why f rounds are not enough.
from itertools import combinations, product


def floodset(values, rounds, crashes):
    """values[i]: process i's input.  crashes[r] = (process, receivers): in round r
    that process crashes part-way, so only 'receivers' get its last message."""
    n = len(values)
    seen = [{v} for v in values]
    alive = set(range(n))
    for r in range(1, rounds + 1):
        inbox = [set() for _ in range(n)]
        for i in sorted(alive):
            targets = range(n)
            if r in crashes and crashes[r][0] == i:
                targets = crashes[r][1]
            for j in targets:
                inbox[j] |= seen[i]
        if r in crashes:
            alive.discard(crashes[r][0])
        for j in alive:
            seen[j] |= inbox[j]
    return {i: min(seen[i]) for i in sorted(alive)}


values = [0, 1, 1, 1]                               # only process 0 starts with 0
crashes = {1: (0, [1]),                             # round 1: p0 reaches only p1, then dies
           2: (1, [2])}                             # round 2: p1 reaches only p2, then dies
f = 2
for rounds in (f, f + 1):
    decisions = floodset(values, rounds, crashes)
    agree = len(set(decisions.values())) == 1
    print(f"{rounds} rounds with f = {f} crashes: decisions {decisions} -> "
          f"{'agreement' if agree else 'DISAGREEMENT'}")

# Exhaustive check on 4 processes, f = 1: every crash round and receiver subset.
bad = {1: 0, 2: 0}
for rounds in (1, 2):
    for vals in product([0, 1], repeat=4):
        for crasher in range(4):
            for r in range(1, rounds + 1):
                for size in range(4):
                    for recv in combinations(range(4), size):
                        d = floodset(list(vals), rounds, {r: (crasher, list(recv))})
                        if len(set(d.values())) > 1:
                            bad[rounds] += 1
print("f = 1, all inputs and crash patterns on 4 processes:")
print(f"  1 round : {bad[1]} runs end in disagreement")
print(f"  2 rounds: {bad[2]} runs end in disagreement")
