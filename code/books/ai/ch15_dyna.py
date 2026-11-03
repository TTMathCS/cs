# Chapter 15: Dyna-Q (Sutton 1990) from scratch on the Dyna maze (Sutton and Barto, Example 8.1).
# A 6 x 9 maze with walls; reward 1 on reaching the goal, 0 otherwise; gamma = 0.95.
# After every real step, the agent replays n remembered transitions from its learned model.
import random

ROWS, COLS = 6, 9
WALLS = {(1, 2), (2, 2), (3, 2), (4, 5), (0, 7), (1, 7), (2, 7)}
START, GOAL = (2, 0), (0, 8)
MOVES = [(-1, 0), (0, 1), (1, 0), (0, -1)]


def step(s, a):
    r, c = s[0] + MOVES[a][0], s[1] + MOVES[a][1]
    if not (0 <= r < ROWS and 0 <= c < COLS) or (r, c) in WALLS:
        r, c = s
    return (r, c), (1.0 if (r, c) == GOAL else 0.0)


def greedy(q, rng):
    m = max(q)
    return rng.choice([a for a in range(4) if q[a] == m])


def dyna_q(n_planning, episodes, rng, alpha=0.1, eps=0.1, gamma=0.95):
    Q = {(r, c): [0.0] * 4 for r in range(ROWS) for c in range(COLS)}
    model, seen, lengths = {}, [], []
    for _ in range(episodes):
        s, steps = START, 0
        while s != GOAL:
            a = rng.randrange(4) if rng.random() < eps else greedy(Q[s], rng)
            s2, r = step(s, a)
            Q[s][a] += alpha * (r + gamma * (0 if s2 == GOAL else max(Q[s2])) - Q[s][a])   # direct RL
            if (s, a) not in model:
                seen.append((s, a))
            model[(s, a)] = (s2, r)                                                     # model learning
            for _ in range(n_planning):                                                 # planning
                ps, pa = seen[rng.randrange(len(seen))]
                ps2, pr = model[(ps, pa)]
                Q[ps][pa] += alpha * (pr + gamma * (0 if ps2 == GOAL else max(Q[ps2])) - Q[ps][pa])
            s, steps = s2, steps + 1
        lengths.append(steps)
    return lengths


RUNS, EPISODES = 20, 50
print("planning steps n   steps in episode 1    2      3      5     10     20     50   (mean of 20 runs)")
for n in (0, 5, 50):
    total = [0] * EPISODES
    for run in range(RUNS):
        for i, L in enumerate(dyna_q(n, EPISODES, random.Random(run))):
            total[i] += L
    m = [t / RUNS for t in total]
    print(f"{n:16d}   {m[0]:17.0f} {m[1]:6.0f} {m[2]:6.0f} {m[4]:6.0f} {m[9]:6.0f} {m[19]:6.0f} {m[49]:6.0f}")
print("shortest path: 14 steps")
