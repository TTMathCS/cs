"""Chapter 2: five kinds of agent in one small grid world.

A rover starts at S and must reach the rock G. '#' is rock wall, '~' is soft
sand: a move into sand fails (the rover stays put) with probability 2/3.
Performance measure: the number of time steps to reach G (fewer is better),
with a limit of 200 steps per run.

  simple reflex   sees its four neighbours and the compass bearing to G
  model-based     the same percepts, plus a memory of how often it visited cells
  goal-based      knows the map; plans the fewest moves with breadth-first search
  utility-based   knows the map and the sand; minimises expected time (Dijkstra)
  learning        knows nothing; learns from reward -1 per step (Q-learning)

Python with NumPy.
"""
import heapq
from collections import deque

import numpy as np

MAP = """\
#############
#S..........#
#.#########.#
#.#.......#.#
#.#.#####.#.#
#.#...#.#.#.#
#.#####.#.#.#
#.......#.#.#
#~#######.#.#
#~~~~~G.....#
#############"""
GRID = [list(r) for r in MAP.split("\n")]
H, W = len(GRID), len(GRID[0])
START = next((r, c) for r in range(H) for c in range(W) if GRID[r][c] == "S")
GOAL = next((r, c) for r in range(H) for c in range(W) if GRID[r][c] == "G")
MOVES = {"N": (-1, 0), "S": (1, 0), "W": (0, -1), "E": (0, 1)}
SLIP = 2 / 3
LIMIT = 200


def free(p):
    return GRID[p[0]][p[1]] != "#"


def neighbours(p):
    for a, (dr, dc) in MOVES.items():
        q = (p[0] + dr, p[1] + dc)
        if free(q):
            yield a, q


def env_step(p, a, rng):
    dr, dc = MOVES[a]
    q = (p[0] + dr, p[1] + dc)
    if not free(q):
        return p                                  # bump into a wall
    if GRID[q[0]][q[1]] == "~" and rng.random() < SLIP:
        return p                                  # wheels slip in sand
    return q


def percept(p):
    """What the reflex agents sense: free directions and the bearing to G."""
    dirs = [a for a, _ in neighbours(p)]
    bearing = []
    if GOAL[0] < p[0]: bearing.append("N")
    if GOAL[0] > p[0]: bearing.append("S")
    if GOAL[1] < p[1]: bearing.append("W")
    if GOAL[1] > p[1]: bearing.append("E")
    return dirs, bearing


# ------------------------------------------------------------- the agents
class SimpleReflex:
    """Rule: if a free direction points toward G, take it; else a random free one."""
    def __init__(self, rng):
        self.rng = rng

    def act(self, p):
        dirs, bearing = percept(p)
        good = [a for a in bearing if a in dirs]
        return self.rng.choice(good if good else dirs)


class ModelBased:
    """Keeps a model: visit counts of cells. Prefers the least-visited free
    neighbour, breaking ties toward G. In this simulation every agent is told
    its cell (a position fix); only the model-based agent remembers it."""
    def __init__(self, rng):
        self.rng = rng
        self.visits = {}

    def act(self, p):
        self.visits[p] = self.visits.get(p, 0) + 1
        dirs, bearing = percept(p)
        def key(a):
            dr, dc = MOVES[a]
            q = (p[0] + dr, p[1] + dc)
            return (self.visits.get(q, 0), a not in bearing, self.rng.random())
        return min(dirs, key=key)


def plan(cost):
    """Dijkstra from START to GOAL with cost(q) for entering cell q."""
    dist, par = {START: 0.0}, {START: None}
    pq = [(0.0, START)]
    while pq:
        d, u = heapq.heappop(pq)
        if u == GOAL:
            break
        if d > dist[u]:
            continue
        for a, q in neighbours(u):
            nd = d + cost(q)
            if nd < dist.get(q, float("inf")):
                dist[q], par[q] = nd, (u, a)
                heapq.heappush(pq, (nd, q))
    acts, v = [], GOAL
    while par[v] is not None:
        v, a = par[v]
        acts.append(a)
    return acts[::-1], dist[GOAL]


class GoalBased:
    """Plans the path with the fewest moves (all moves cost 1: this is BFS)."""
    def __init__(self, rng):
        self.path, _ = plan(lambda q: 1.0)
        self.cells = self._cells(self.path)

    @staticmethod
    def _cells(path):
        p, out = START, {}
        for a in path:
            dr, dc = MOVES[a]
            q = (p[0] + dr, p[1] + dc)
            out[p] = a
            p = q
        return out

    def act(self, p):
        return self.cells[p]                     # after a slip, repeat the move


class UtilityBased(GoalBased):
    """Expected time to enter a sand cell is 1 / (1 - SLIP) = 3 steps."""
    def __init__(self, rng):
        self.path, self.expected = plan(
            lambda q: 1 / (1 - SLIP) if GRID[q[0]][q[1]] == "~" else 1.0)
        self.cells = self._cells(self.path)


def run(agent, rng):
    p, t = START, 0
    while p != GOAL and t < LIMIT:
        p = env_step(p, agent.act(p), rng)
        t += 1
    return t, p == GOAL


def q_learning(rng, episodes=300, alpha=0.5, gamma=1.0, eps=0.1):
    acts = list(MOVES)
    Q = np.zeros((H, W, 4))
    steps = []
    for _ in range(episodes):
        p, t = START, 0
        while p != GOAL and t < LIMIT:
            if rng.random() < eps:
                i = int(rng.integers(4))
            else:
                row = Q[p[0], p[1]]
                i = int(rng.choice(np.flatnonzero(row == row.max())))
            q = env_step(p, acts[i], rng)
            target = -1 + (0 if q == GOAL else gamma * Q[q[0], q[1]].max())
            Q[p[0], p[1], i] += alpha * (target - Q[p[0], p[1], i])
            p, t = q, t + 1
        steps.append(t)
    return Q, steps


class Greedy:
    def __init__(self, Q):
        self.Q = Q

    def act(self, p):
        return list(MOVES)[int(np.argmax(self.Q[p[0], p[1]]))]


def main():
    print(MAP)
    rng = np.random.default_rng(2)
    g, u = GoalBased(rng), UtilityBased(rng)
    def sand(path):
        cells = list(GoalBased._cells(path))[1:] + [GOAL]   # cells entered
        return sum(GRID[r][c] == "~" for r, c in cells)
    print(f"\ngoal-based plan:    {len(g.path)} moves, {sand(g.path)} into sand,"
          f" route {''.join(g.path)}")
    print(f"utility-based plan: {len(u.path)} moves, expected {u.expected:.1f} steps,"
          f" route {''.join(u.path)}")

    print(f"\n{'agent':15} {'reached G':>10} {'mean steps':>11}  (500 runs each)")
    for name, cls in [("simple reflex", SimpleReflex), ("model-based", ModelBased),
                      ("goal-based", GoalBased), ("utility-based", UtilityBased)]:
        res = [run(cls(rng), rng) for _ in range(500)]
        ok = sum(r[1] for r in res)
        mean = sum(r[0] for r in res) / len(res)
        print(f"{name:15} {ok:>9}/500 {mean:11.1f}")

    Q, steps = q_learning(rng)
    for a, b in [(0, 10), (40, 50), (290, 300)]:
        print(f"learning agent, episodes {a + 1:3d}-{b:3d}: mean steps "
              f"{sum(steps[a:b]) / (b - a):6.1f}")
    res = [run(Greedy(Q), rng) for _ in range(500)]
    print(f"{'learned policy':15} {sum(r[1] for r in res):>9}/500 "
          f"{sum(r[0] for r in res) / 500:11.1f}")


if __name__ == "__main__":
    main()
