"""Chapter 4: weighted A* and anytime search on the 15-puzzle.

Weighted A* orders the frontier by f = g + w*h with w >= 1. With an admissible
h, the solution it returns costs at most w times the optimum (Section 4.5).
Anytime weighted A* (in the style of Hansen and Zhou 2007) keeps going after
the first solution: it prunes every node whose g + h is no better than the best
solution so far, reports each improvement, and when the frontier is empty the
last solution is proved optimal. Standard library only.
"""
import heapq
import random


class Puzzle:
    """The n x n sliding-tile puzzle; the blank (0) moves."""
    def __init__(self, n, start):
        self.n = n
        self.start = tuple(start)
        self.goal = tuple(list(range(1, n * n)) + [0])
        self.pos = {t: divmod(i, n) for i, t in enumerate(self.goal)}
        self.neigh = {}
        for i in range(n * n):
            r, c = divmod(i, n)
            self.neigh[i] = [(r + dr) * n + c + dc for dr, dc in
                             ((-1, 0), (1, 0), (0, -1), (0, 1))
                             if 0 <= r + dr < n and 0 <= c + dc < n]

    def h(self, s):
        """Manhattan distance."""
        n, total = self.n, 0
        for i, t in enumerate(s):
            if t:
                r, c = divmod(i, n)
                gr, gc = self.pos[t]
                total += abs(r - gr) + abs(c - gc)
        return total

    def successors(self, s):
        b = s.index(0)
        for j in self.neigh[b]:
            t = list(s)
            t[b], t[j] = t[j], t[b]
            yield tuple(t)


def scramble(n, moves, seed):
    p = Puzzle(n, list(range(1, n * n)) + [0])
    rng = random.Random(seed)
    s, prev = p.goal, None
    for _ in range(moves):
        nxt = [t for t in p.successors(s) if t != prev]
        prev, s = s, rng.choice(nxt)
    return s


def weighted_astar(p, w, incumbent=float("inf"), report=None):
    """Graph search on f = g + w*h. If report is given, continue after each
    solution (anytime mode), pruning nodes with g + h >= the best cost."""
    g = {p.start: 0}
    pq = [(w * p.h(p.start), 0, p.start)]
    expanded = 0
    best = incumbent
    while pq:
        f, neg_g, s = heapq.heappop(pq)       # ties: deeper node first
        gs = -neg_g
        if gs > g[s] or gs + p.h(s) >= best:
            continue                      # stale, or cannot beat the incumbent
        if s == p.goal:
            best = gs
            if report is None:
                return best, expanded
            report(best, expanded)
            continue
        expanded += 1
        for t in p.successors(s):
            gt = gs + 1
            if gt < g.get(t, float("inf")) and gt + p.h(t) < best:
                g[t] = gt
                heapq.heappush(pq, (gt + w * p.h(t), -gt, t))
    return best, expanded


def main():
    start = scramble(4, 50, seed=3)
    p = Puzzle(4, start)
    print(f"15-puzzle start {start}, Manhattan h = {p.h(start)}")
    print(f"  {'w':>4} {'cost':>5} {'bound w*C*':>11} {'expanded':>9}")
    opt = None
    for w in (1, 1.25, 1.5, 2, 3, 5):
        cost, exp = weighted_astar(p, w)
        opt = cost if w == 1 else opt
        print(f"  {w:>4} {cost:>5} {w * opt:>11.1f} {exp:>9}")

    print("\nanytime weighted A* with w = 2:")
    best, total = weighted_astar(p, 2, report=lambda c, e: print(
        f"  solution of cost {c} after {e} expansions"))
    print(f"  frontier empty after {total} expansions: cost {best} is optimal"
          f" (A* found {opt})")


if __name__ == "__main__":
    main()
