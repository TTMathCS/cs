"""Chapter 4: greedy best-first search and A*, with the generic search of Chapter 3.

Both are graph_search with a priority queue: greedy orders the frontier by
h(n), A* by f(n) = g(n) + h(n). We run them on the Mars road map (h = great-
circle distance to the goal) and on the 8-puzzle with two heuristics:
  h1 = number of misplaced tiles,  h2 = sum of Manhattan distances.
We also check, over every state of the 8-puzzle, that h1 <= h2 <= true cost,
and that both are consistent. Standard library only.
"""
from ch03_search import (EightPuzzle, Priority, Route, Stats, graph_search,
                         path_actions, path_states, uniform_cost)
from ch03_space import bfs_layers


def greedy(problem, h=None):
    h = h or problem.h
    st = Stats("greedy")
    return graph_search(problem, Priority(lambda n: h(n.state)), st), st


def astar(problem, h=None):
    """Priority (f, -g): among nodes with equal f, prefer the deeper one,
    which is usually closer to a goal."""
    h = h or problem.h
    st = Stats("A*")
    key = lambda n: (n.path_cost + h(n.state), -n.path_cost)
    return graph_search(problem, Priority(key), st), st


GOAL_POS = {t: divmod(i, 3) for i, t in enumerate(EightPuzzle.GOAL)}


def h1(s):
    """Misplaced tiles (the blank is not a tile)."""
    return sum(1 for i, t in enumerate(s) if t and t != EightPuzzle.GOAL[i])


def h2(s):
    """Sum over tiles of the Manhattan distance to the tile's goal square."""
    total = 0
    for i, t in enumerate(s):
        if t:
            r, c = divmod(i, 3)
            gr, gc = GOAL_POS[t]
            total += abs(r - gr) + abs(c - gc)
    return total


def trace_astar_route():
    p = Route("Olympus Mons", "Jezero crater")
    print("A* on the Mars map, Olympus Mons to Jezero crater (km):")
    import heapq
    g = {p.initial: 0.0}
    pq = [(p.h(p.initial), p.initial)]
    done = set()
    while pq:
        f, u = heapq.heappop(pq)
        if u in done or f > g[u] + p.h(u) + 1e-9:
            continue
        done.add(u)
        if p.is_goal(u):
            print(f"  expand {u:16} g={g[u]:5.0f} f={f:5.0f}  goal")
            break
        for v in p.actions(u):
            nv = g[u] + p.action_cost(u, v, v)
            if v not in done and nv < g.get(v, float("inf")):
                g[v] = nv
                heapq.heappush(pq, (nv + p.h(v), v))
        front = sorted((g[v] + p.h(v), v) for v in g if v not in done)
        print(f"  expand {u:16} g={g[u]:5.0f} f={f:5.0f}  frontier: "
              + ", ".join(f"{v} {fv:.0f}" for fv, v in front))


def main():
    trace_astar_route()
    p = Route("Olympus Mons", "Jezero crater")
    for name, fn in [("UCS", uniform_cost), ("greedy", greedy), ("A*", astar)]:
        node, st = fn(p)
        print(f"  {name:7} {' > '.join(path_states(node))}: {node.path_cost:.0f} km,"
              f" expanded {st.expanded}")

    start = (7, 2, 4, 5, 0, 6, 8, 3, 1)
    p = EightPuzzle(start)
    print(f"\n8-puzzle from {start}: h1 = {h1(start)}, h2 = {h2(start)}")
    print(f"  {'algorithm':12} {'moves':>6} {'generated':>10} {'expanded':>9}")
    runs = [("UCS", lambda: uniform_cost(p)), ("greedy h2", lambda: greedy(p, h2)),
            ("A* h1", lambda: astar(p, h1)), ("A* h2", lambda: astar(p, h2))]
    for name, fn in runs:
        node, st = fn()
        print(f"  {name:12} {len(path_actions(node)):>6} {st.generated:>10}"
              f" {st.expanded:>9}")

    dist = bfs_layers(EightPuzzle.GOAL)          # true cost of every state
    H1 = {s: h1(s) for s in dist}
    H2 = {s: h2(s) for s in dist}
    adm = all(H1[s] <= H2[s] <= d for s, d in dist.items())
    q = EightPuzzle(EightPuzzle.GOAL)
    cons = all(abs(H[s] - H[q.result(s, a)]) <= 1
               for s in dist for a in q.actions(s) for H in (H1, H2))
    n_exact = sum(H2[s] == d for s, d in dist.items())
    n = len(dist)
    print(f"\nover all {n} states: h1 <= h2 <= h* everywhere: {adm};"
          f" both consistent: {cons}")
    print(f"  mean h1 {sum(H1.values()) / n:.2f}, mean h2 {sum(H2.values()) / n:.2f},"
          f" mean true cost {sum(dist.values()) / n:.2f};"
          f" h2 exact on {n_exact} states")


if __name__ == "__main__":
    main()
