# Chapter 15: Q-learning (Watkins 1989) and SARSA from scratch on the cliff-walking grid
# (Sutton and Barto, Example 6.6). A 4 x 12 grid; start bottom left, goal bottom right; the
# squares between them are a cliff: stepping in costs -100 and sends the agent back to the start.
# Every other step costs -1. Both learners use epsilon-greedy exploration with epsilon = 0.1.
# Plain Python lists are used for the table: for one-number-at-a-time updates they beat NumPy.
import random

ROWS, COLS = 4, 12
START, GOAL = 3 * COLS + 0, 3 * COLS + 11            # a state is row * COLS + column
MOVES = [(-1, 0), (0, 1), (1, 0), (0, -1)]          # up, right, down, left
ARROWS = "^>v<"


def step(s, a):
    r, c = divmod(s, COLS)
    r, c = min(max(r + MOVES[a][0], 0), ROWS - 1), min(max(c + MOVES[a][1], 0), COLS - 1)
    if r == 3 and 1 <= c <= 10:                      # the cliff
        return START, -100.0
    return r * COLS + c, -1.0


def choose(q, eps, rng):
    if rng.random() < eps:
        return rng.randrange(4)
    m = max(q)
    return rng.choice([a for a in range(4) if q[a] == m])   # break ties at random


def learn(method, episodes, rng, alpha=0.1, eps=0.1, gamma=1.0):
    Q = [[0.0] * 4 for _ in range(ROWS * COLS)]
    totals = []
    for _ in range(episodes):
        s, total = START, 0.0
        a = choose(Q[s], eps, rng)
        while s != GOAL:
            s2, r = step(s, a)
            total += r
            a2 = choose(Q[s2], eps, rng)
            if s2 == GOAL:
                target = r                                    # terminal: no future
            elif method == "sarsa":
                target = r + gamma * Q[s2][a2]                # the action it will actually take
            else:
                target = r + gamma * max(Q[s2])               # the best action (off-policy)
            Q[s][a] += alpha * (target - Q[s][a])
            s, a = s2, a2
        totals.append(total)
    return Q, totals


def greedy_path(Q):
    grid = [["." for _ in range(COLS)] for _ in range(ROWS)]
    for c in range(1, 11):
        grid[3][c] = "C"
    grid[3][11] = "G"
    s, seen, n = START, set(), 0
    while s != GOAL and s not in seen:
        seen.add(s)
        a = max(range(4), key=lambda b: Q[s][b])
        grid[s // COLS][s % COLS] = ARROWS[a]
        s, _ = step(s, a)
        n += 1
    return ["".join(row) for row in grid], (n if s == GOAL else None)     # None: the greedy path loops


RUNS, EPISODES = 50, 500
first, lengths = {}, {}
for method in ("sarsa", "q-learning"):
    curves, lengths[method] = [], {}
    for run in range(RUNS):
        Q, totals = learn(method, EPISODES, random.Random(run))
        curves.append(totals)
        n = greedy_path(Q)[1]
        lengths[method][n] = lengths[method].get(n, 0) + 1
        if run == 0:
            first[method] = Q

    def avg(lo, hi):
        return sum(sum(c[lo:hi]) for c in curves) / (RUNS * (hi - lo))
    print(f"{method:10s} reward per episode while learning (average of {RUNS} runs):"
          f" episodes 1-10 {avg(0, 10):7.1f}, 91-100 {avg(90, 100):6.1f}, 401-500 {avg(400, 500):6.1f}")

for method in ("sarsa", "q-learning"):
    rows, n = greedy_path(first[method])
    print(f"\ngreedy path learned by {method} in run 0 (C = cliff, G = goal): {n} steps")
    for row in rows:
        print("   " + row)
    summary = ", ".join(f"{k if k else 'loops'}: {v}" for k, v in sorted(lengths[method].items(), key=lambda kv: kv[0] or 999))
    print(f"   greedy path length over all {RUNS} runs -> {summary}")
