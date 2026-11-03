"""Chapter 4: memory-bounded heuristic search: IDA* and RBFS against A*.

IDA* (Korf 1985) is iterative deepening on f = g + h instead of depth.
RBFS (Korf 1993) is a recursive best-first search that keeps only the current
path and, for each node on it, the best f-value of its siblings; when it backs
up it remembers the best f-value of the subtree it forgets.
Both use memory linear in the depth. Heuristic: Manhattan distance.
Standard library only.
"""
import math

from ch03_search import EightPuzzle
from ch04_astar import astar, h2


def ida_star(problem, h):
    stats = {"generated": 0, "expanded": 0, "iterations": 0, "max_depth": 0}
    path = [problem.initial]
    on_path = {problem.initial}

    def search(g, bound):
        s = path[-1]
        f = g + h(s)
        if f > bound:
            return f                       # smallest f that exceeded the bound
        if problem.is_goal(s):
            return "FOUND"
        stats["expanded"] += 1
        stats["max_depth"] = max(stats["max_depth"], len(path))
        smallest = math.inf
        for a in problem.actions(s):
            t = problem.result(s, a)
            stats["generated"] += 1
            if t in on_path:
                continue
            path.append(t)
            on_path.add(t)
            r = search(g + problem.action_cost(s, a, t), bound)
            if r == "FOUND":
                return r
            smallest = min(smallest, r)
            path.pop()
            on_path.discard(t)
        return smallest

    bound = h(problem.initial)
    bounds = []
    while True:
        stats["iterations"] += 1
        bounds.append(bound)
        r = search(0, bound)
        if r == "FOUND":
            return len(path) - 1, stats, bounds
        if r == math.inf:
            return None, stats, bounds
        bound = r


def rbfs(problem, h):
    stats = {"generated": 0, "expanded": 0, "max_depth": 0}

    def recurse(s, g, f_s, f_limit, depth, on_path):
        """Returns (solution length or None, backed-up f value)."""
        if problem.is_goal(s):
            return depth, f_s
        stats["expanded"] += 1
        stats["max_depth"] = max(stats["max_depth"], depth + 1)
        succ = []
        for a in problem.actions(s):
            t = problem.result(s, a)
            stats["generated"] += 1
            if t in on_path:
                continue
            gt = g + problem.action_cost(s, a, t)
            # a child's f is at least its parent's backed-up f (keeps f monotone)
            succ.append([max(gt + h(t), f_s), gt, t])
        if not succ:
            return None, math.inf
        while True:
            succ.sort(key=lambda x: x[0])
            best = succ[0]
            if best[0] > f_limit:
                return None, best[0]
            alt = succ[1][0] if len(succ) > 1 else math.inf
            on_path.add(best[2])
            result, best[0] = recurse(best[2], best[1], best[0],
                                      min(f_limit, alt), depth + 1, on_path)
            on_path.discard(best[2])
            if result is not None:
                return result, best[0]

    s0 = problem.initial
    length, _ = recurse(s0, 0, h(s0), math.inf, 0, {s0})
    return length, stats


def main():
    for start in [(7, 2, 4, 5, 0, 6, 8, 3, 1), (8, 6, 7, 2, 5, 4, 3, 0, 1)]:
        p = EightPuzzle(start)
        print(f"8-puzzle from {start}, h2 = {h2(start)}")
        node, st = astar(p, h2)
        print(f"  A*:    {node.depth} moves, generated {st.generated:7d},"
              f" expanded {st.expanded:7d}, max frontier {st.max_frontier}")
        length, st, bounds = ida_star(p, h2)
        print(f"  IDA*:  {length} moves, generated {st['generated']:7d},"
              f" expanded {st['expanded']:7d}, deepest path {st['max_depth']},"
              f" {st['iterations']} iterations, bounds {bounds}")
        length, st = rbfs(p, h2)
        print(f"  RBFS:  {length} moves, generated {st['generated']:7d},"
              f" expanded {st['expanded']:7d}, deepest path {st['max_depth']}")


if __name__ == "__main__":
    main()
