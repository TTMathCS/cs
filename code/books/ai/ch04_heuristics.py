"""Chapter 4: how good is a heuristic? Effective branching factors on the 8-puzzle.

Heuristics compared, all admissible:
  h1  misplaced tiles             h2  Manhattan distance
  pdb additive pattern database: tiles {1,2,3,4} and {5,6,7,8}, each table
      built by a 0-1 breadth-first search that counts only moves of its own
      tiles, so the two values can be added.
For random solvable states at known depths (true costs from a full BFS), A*
with each heuristic is run, and the effective branching factor b* is solved
from N + 1 = 1 + b* + b*^2 + ... + b*^d. Standard library only.
"""
import random
from collections import deque

from ch03_search import EightPuzzle, breadth_first
from ch03_space import bfs_layers
from ch04_astar import astar, h1, h2

GOAL = EightPuzzle.GOAL
NEIGH = {i: [j for j in (i - 3, i + 3, i - 1, i + 1)
             if 0 <= j < 9 and (abs(j - i) == 3 or j // 3 == i // 3)] for i in range(9)}


def build_pdb(pattern):
    """Abstract state: (positions of the pattern tiles in order, blank position).
    Cost: 1 when the blank swaps with a pattern tile, 0 otherwise."""
    start = (tuple(GOAL.index(t) for t in pattern), GOAL.index(0))
    dist = {start: 0}
    dq = deque([start])
    while dq:
        s = dq.popleft()
        pos, blank = s
        for j in NEIGH[blank]:
            if j in pos:
                k = pos.index(j)
                t = (pos[:k] + (blank,) + pos[k + 1:], j)
                c = 1
            else:
                t, c = (pos, j), 0
            nd = dist[s] + c
            if nd < dist.get(t, 1 << 30):
                dist[t] = nd
                if c == 0:
                    dq.appendleft(t)                 # 0-1 BFS: cost-0 edges first
                else:
                    dq.append(t)
    return dist


PATTERNS = [(1, 2, 3, 4), (5, 6, 7, 8)]
PDBS = [build_pdb(p) for p in PATTERNS]


def h_pdb(s):
    blank = s.index(0)
    return sum(db[(tuple(s.index(t) for t in pat), blank)]
               for pat, db in zip(PATTERNS, PDBS))


def effective_b(n, d):
    """Solve n + 1 = 1 + b + ... + b^d for b by bisection."""
    lo, hi = 1.0, float(n + 1)
    for _ in range(100):
        mid = (lo + hi) / 2
        total = sum(mid ** i for i in range(d + 1))
        lo, hi = (mid, hi) if total < n + 1 else (lo, mid)
    return lo


def main():
    dist = bfs_layers(GOAL)
    print(f"pattern databases: {len(PDBS[0])} and {len(PDBS[1])} entries")
    ok = all(h2(s) <= h_pdb(s) <= d for s, d in dist.items())
    print(f"h2 <= pdb <= true cost on all {len(dist)} states: {ok}")
    n = len(dist)
    print(f"mean values: h1 {sum(map(h1, dist)) / n:.2f}, h2 {sum(map(h2, dist)) / n:.2f},"
          f" pdb {sum(map(h_pdb, dist)) / n:.2f}, true {sum(dist.values()) / n:.2f}")

    rng = random.Random(1)
    by_depth = {}
    for s, d in dist.items():
        by_depth.setdefault(d, []).append(s)
    for d in by_depth:
        by_depth[d].sort()
    print("\nmean nodes generated (and effective branching factor), 10 states per depth")
    print(f"  {'d':>3} {'BFS':>16} {'A* h1':>16} {'A* h2':>16} {'A* pdb':>16}")
    for d in (4, 8, 12, 16, 20, 24, 28):
        states = rng.sample(by_depth[d], 10)
        cols = []
        for name, h in [("BFS", None), ("h1", h1), ("h2", h2), ("pdb", h_pdb)]:
            if (name == "BFS" and d > 12) or (name == "h1" and d > 20):
                cols.append(f"{'-':>16}")
                continue
            total = 0
            for s in states:
                p = EightPuzzle(s)
                node, st = breadth_first(p) if h is None else astar(p, h)
                assert node.depth == d
                total += st.generated
            mean = total / len(states)
            cols.append(f"{mean:9.0f} ({effective_b(mean, d):.2f})")
        print(f"  {d:>3} " + " ".join(cols))


if __name__ == "__main__":
    main()
