# Chapter 21: an unreliable proposer plus an exact verifier (generate-and-test).
# The proposer imitates a learned model: it suggests whole plans quickly but is often wrong.
# The verifier simulates each plan exactly. We compare: one sample, k samples with verification,
# and verification with feedback (keep the longest valid prefix and ask only for the rest).
import random

GRID = ["S.......",
        "..##....",
        "....#...",
        ".#..#.#.",
        ".#....#.",
        "...##..G"]
R, C = len(GRID), len(GRID[0])
start = next((r, c) for r in range(R) for c in range(C) if GRID[r][c] == "S")
goal = next((r, c) for r in range(R) for c in range(C) if GRID[r][c] == "G")
MOVES = {"U": (-1, 0), "D": (1, 0), "L": (0, -1), "R": (0, 1)}


def free(p):
    return 0 <= p[0] < R and 0 <= p[1] < C and GRID[p[0]][p[1]] != "#"


def verify(plan, pos=start):
    """Exact check. Returns (ok, number of valid steps, position after them)."""
    for i, m in enumerate(plan):
        nxt = (pos[0] + MOVES[m][0], pos[1] + MOVES[m][1])
        if not free(nxt):
            return False, i, pos
        pos = nxt
        if pos == goal:
            return True, i + 1, pos
    return False, len(plan), pos


def propose(rng, pos=start, length=40):
    """A cheap, noisy guesser: usually steps towards the goal, sometimes anywhere. It has no idea of the walls."""
    plan = []
    for _ in range(length):
        if rng.random() < 0.6:
            dr, dc = goal[0] - pos[0], goal[1] - pos[1]
            options = (["D"] if dr > 0 else ["U"] if dr < 0 else []) + (["R"] if dc > 0 else ["L"] if dc < 0 else [])
            m = rng.choice(options or list(MOVES))
        else:
            m = rng.choice("UDLR")
        nxt = (pos[0] + MOVES[m][0], pos[1] + MOVES[m][1])
        plan.append(m)
        if free(nxt):
            pos = nxt
    return "".join(plan)


rng = random.Random(0)
trials = 20000
p = sum(verify(propose(rng))[0] for _ in range(trials)) / trials
print(f"one proposed plan is valid with probability p = {p:.4f} (estimated from {trials} samples)")
print("    k    P(some valid plan among k): measured   formula 1-(1-p)^k")
for k in (1, 10, 100, 1000):
    runs = 500 if k < 1000 else 100
    hit = sum(any(verify(propose(rng))[0] for _ in range(k)) for _ in range(runs)) / runs
    print(f"   {k:>4}                          {hit:6.3f}      {1 - (1 - p) ** k:6.3f}")

# With feedback: the verifier reports where the plan first fails; keep the valid prefix, re-propose from there.
calls, failed = [], 0
for _ in range(500):
    pos, n = start, 0
    while n < 2000:
        plan = propose(rng, pos)
        n += 1
        ok, steps, pos2 = verify(plan, pos)
        if ok:
            break
        if steps > 0:
            pos = pos2                       # keep the progress that was checked
    else:
        failed += 1
    calls.append(n)
calls.sort()
print(f"\nwith feedback (keep the checked prefix), 500 runs: median {calls[250]} proposer calls, "
      f"90th percentile {calls[450]}, runs that gave up after 2000 calls: {failed}")
