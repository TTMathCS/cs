"""Chapter 3: problems as state spaces, and one generic search used for all.

Three problems (missionaries and cannibals, routes on a map of Mars, the
8-puzzle), one generic graph search whose behaviour is set by its frontier
(FIFO queue = breadth-first, LIFO stack = depth-first, priority queue =
uniform-cost), plus depth-limited, iterative deepening and bidirectional
search. Every algorithm counts the nodes it generates and expands and the
largest frontier it holds. Chapter 4 imports this file. Standard library only.
"""
import heapq
import math
from collections import deque


# ------------------------------------------------------------ problems
class Problem:
    """A search problem: initial state, actions, transition model, goal test,
    action costs. Subclasses fill these in."""
    def __init__(self, initial, goal=None):
        self.initial, self.goal = initial, goal

    def actions(self, s):
        raise NotImplementedError

    def result(self, s, a):
        raise NotImplementedError

    def is_goal(self, s):
        return s == self.goal

    def action_cost(self, s, a, s2):
        return 1

    def h(self, s):                     # heuristic, used from Chapter 4 on
        return 0


class Missionaries(Problem):
    """State (missionaries on left, cannibals on left, boat on left?).
    Start (3, 3, 1), goal (0, 0, 0). The boat carries one or two people."""
    LOADS = [(1, 0), (2, 0), (0, 1), (0, 2), (1, 1)]

    def __init__(self):
        super().__init__((3, 3, 1), (0, 0, 0))

    @staticmethod
    def safe(m, c):
        return (m == 0 or m >= c) and (3 - m == 0 or 3 - m >= 3 - c)

    def actions(self, s):
        m, c, b = s
        sign = -1 if b else 1           # boat on the left carries people away
        for dm, dc in self.LOADS:
            m2, c2 = m + sign * dm, c + sign * dc
            if 0 <= m2 <= 3 and 0 <= c2 <= 3 and self.safe(m2, c2):
                yield (dm, dc)

    def result(self, s, a):
        m, c, b = s
        sign = -1 if b else 1
        return (m + sign * a[0], c + sign * a[1], 1 - b)


# Places on Mars: latitude N, longitude E (USGS Gazetteer of Planetary
# Nomenclature), and the roads of this site's map, as in Chapter 16 of the
# Algorithms book. A road's length is the great-circle distance in km.
R_MARS = 3389.5
PLACES = {
    "Erebus Montes": (35.7, -175.0), "Olympus Mons": (18.65, -133.8),
    "Ascraeus Mons": (11.92, -104.08), "Valles Marineris": (-13.9, -59.2),
    "Elysium Mons": (25.02, 147.21), "Utopia Planitia": (47.97, 134.26),
    "Gale crater": (-5.4, 137.8), "Jezero crater": (18.38, 77.58),
    "Hellas Planitia": (-42.4, 70.5),
}
ROADS = [("Erebus Montes", "Olympus Mons"), ("Erebus Montes", "Elysium Mons"),
         ("Erebus Montes", "Utopia Planitia"), ("Olympus Mons", "Ascraeus Mons"),
         ("Ascraeus Mons", "Valles Marineris"), ("Elysium Mons", "Gale crater"),
         ("Utopia Planitia", "Elysium Mons"), ("Utopia Planitia", "Jezero crater"),
         ("Jezero crater", "Gale crater"), ("Jezero crater", "Hellas Planitia"),
         ("Gale crater", "Hellas Planitia"), ("Olympus Mons", "Gale crater")]


def great_circle(a, b):
    (la1, lo1), (la2, lo2) = PLACES[a], PLACES[b]
    p1, p2, dl = math.radians(la1), math.radians(la2), math.radians(lo2 - lo1)
    c = math.sin(p1) * math.sin(p2) + math.cos(p1) * math.cos(p2) * math.cos(dl)
    return R_MARS * math.acos(max(-1.0, min(1.0, c)))


class Route(Problem):
    """Drive between places; an action is 'go to a neighbouring place'."""
    def __init__(self, start, goal):
        super().__init__(start, goal)
        self.adj = {p: [] for p in PLACES}
        for a, b in ROADS:
            self.adj[a].append(b)
            self.adj[b].append(a)
        for p in self.adj:
            self.adj[p].sort()

    def actions(self, s):
        return self.adj[s]

    def result(self, s, a):
        return a

    def action_cost(self, s, a, s2):
        return great_circle(s, s2)

    def h(self, s):                     # straight-line (great-circle) distance
        return great_circle(s, self.goal)


class EightPuzzle(Problem):
    """State: tuple of 9 tiles read row by row, 0 for the blank. An action
    names the direction the blank moves."""
    GOAL = (1, 2, 3, 4, 5, 6, 7, 8, 0)
    DELTA = {"U": -3, "D": 3, "L": -1, "R": 1}

    def __init__(self, initial, goal=GOAL):
        super().__init__(tuple(initial), tuple(goal))

    def actions(self, s):
        i = s.index(0)
        r, c = divmod(i, 3)
        if r > 0: yield "U"
        if r < 2: yield "D"
        if c > 0: yield "L"
        if c < 2: yield "R"

    def result(self, s, a):
        i = s.index(0)
        j = i + self.DELTA[a]
        t = list(s)
        t[i], t[j] = t[j], t[i]
        return tuple(t)


def solvable(s, goal=EightPuzzle.GOAL):
    """Same inversion parity as the goal (Section 3.1)."""
    def inv(t):
        x = [v for v in t if v]
        return sum(x[i] > x[j] for i in range(8) for j in range(i + 1, 8))
    return inv(s) % 2 == inv(goal) % 2


# --------------------------------------------------------------- nodes
class Node:
    __slots__ = ("state", "parent", "action", "path_cost", "depth")

    def __init__(self, state, parent=None, action=None, path_cost=0.0):
        self.state, self.parent, self.action = state, parent, action
        self.path_cost = path_cost
        self.depth = 0 if parent is None else parent.depth + 1

    def __lt__(self, other):            # ties in the priority queue
        return self.depth < other.depth


def expand(problem, node):
    s = node.state
    for a in problem.actions(s):
        s2 = problem.result(s, a)
        yield Node(s2, node, a, node.path_cost + problem.action_cost(s, a, s2))


def path_actions(node):
    out = []
    while node is not None and node.parent is not None:
        out.append(node.action)
        node = node.parent
    return out[::-1]


def path_states(node):
    out = []
    while node is not None:
        out.append(node.state)
        node = node.parent
    return out[::-1]


class Stats:
    def __init__(self, name):
        self.name, self.generated, self.expanded, self.max_frontier = name, 0, 0, 0

    def __repr__(self):
        return (f"{self.name}: generated {self.generated}, expanded {self.expanded},"
                f" max frontier {self.max_frontier}")


# ---------------------------------------------------- frontiers and search
class FIFO:                             # breadth-first
    reopen = False
    def __init__(self): self.q = deque()
    def add(self, n): self.q.append(n)
    def pop(self): return self.q.popleft()
    def __len__(self): return len(self.q)


class LIFO(FIFO):                       # depth-first
    def pop(self): return self.q.pop()


class Priority:                         # uniform-cost (f = g), A* (f = g + h), ...
    reopen = True
    def __init__(self, f): self.f, self.h = f, []
    def add(self, n): heapq.heappush(self.h, (self.f(n), n))
    def pop(self): return heapq.heappop(self.h)[1]
    def __len__(self): return len(self.h)


def graph_search(problem, frontier, stats, early_goal=False):
    """The one generic search. The frontier decides the order of expansion.
    reached maps each state to the best node found for it so far."""
    node = Node(problem.initial)
    if problem.is_goal(node.state):
        return node
    frontier.add(node)
    reached = {node.state: node}
    while len(frontier):
        stats.max_frontier = max(stats.max_frontier, len(frontier))
        node = frontier.pop()
        if reached[node.state] is not node:
            continue                    # stale entry: a cheaper path was found
        if not early_goal and problem.is_goal(node.state):
            return node
        stats.expanded += 1
        for child in expand(problem, node):
            stats.generated += 1
            s = child.state
            old = reached.get(s)
            if old is None or (frontier.reopen and child.path_cost < old.path_cost):
                if early_goal and problem.is_goal(s):
                    return child
                reached[s] = child
                frontier.add(child)
    return None


def breadth_first(problem):
    st = Stats("BFS")
    return graph_search(problem, FIFO(), st, early_goal=True), st


def uniform_cost(problem):
    st = Stats("UCS")
    return graph_search(problem, Priority(lambda n: n.path_cost), st), st


def depth_first(problem):
    st = Stats("DFS")
    return graph_search(problem, LIFO(), st), st


CUTOFF = "cutoff"


def depth_limited(problem, limit, st):
    """Tree-like depth-first search to depth `limit`, checking for cycles only
    along the current path. Memory: the current path and its siblings.
    Returns a goal node, CUTOFF (the limit was hit somewhere) or None."""
    on_path = set()

    def rec(node):
        if problem.is_goal(node.state):
            return node
        if node.depth == limit:
            return CUTOFF
        st.expanded += 1
        on_path.add(node.state)
        cut = False
        for child in expand(problem, node):
            st.generated += 1
            if child.state in on_path:
                continue
            r = rec(child)
            if r is CUTOFF:
                cut = True
            elif r is not None:
                on_path.discard(node.state)
                return r
        on_path.discard(node.state)
        return CUTOFF if cut else None

    st.max_frontier = max(st.max_frontier, limit)   # recursion depth
    return rec(Node(problem.initial))


def iterative_deepening(problem, max_depth=50):
    st = Stats("IDS")
    for limit in range(max_depth + 1):
        r = depth_limited(problem, limit, st)
        if r is not CUTOFF:
            return r, st
    return None, st


def bidirectional_bfs(problem, backward):
    """Breadth-first from both ends, one whole layer at a time, always growing
    the smaller frontier. `backward` is a problem whose actions undo the
    forward ones (for the puzzles and the map, the same moves). When a layer
    touches the other side, every meeting state in that layer is compared, so
    the path returned has the fewest moves."""
    st = Stats("bidirectional BFS")
    start, goal = Node(problem.initial), Node(problem.goal)
    if start.state == goal.state:
        return [start.state], st
    reach = [{start.state: start}, {goal.state: goal}]
    front = [[start], [goal]]
    probs = [problem, backward]
    while front[0] and front[1]:
        st.max_frontier = max(st.max_frontier, len(front[0]) + len(front[1]))
        i = 0 if len(front[0]) <= len(front[1]) else 1
        best, new = None, []
        for node in front[i]:
            st.expanded += 1
            for child in expand(probs[i], node):
                st.generated += 1
                s = child.state
                if s in reach[i]:
                    continue
                reach[i][s] = child
                new.append(child)
                if s in reach[1 - i]:
                    d = child.depth + reach[1 - i][s].depth
                    if best is None or d < best[0]:
                        best = (d, s)
        if best is not None:
            s = best[1]
            fwd = path_states(reach[0][s])
            bwd = path_states(reach[1][s])[::-1]
            return fwd + bwd[1:], st
        front[i] = new
    return None, st


# ----------------------------------------------------------------- demos
def show_missionaries():
    p = Missionaries()
    node, st = breadth_first(p)
    print("Missionaries and cannibals, breadth-first:")
    print(f"  {len(path_actions(node))} crossings; {st}")
    for s, a in zip(path_states(node), path_actions(node) + [None]):
        m, c, b = s
        left = "M" * m + "C" * c
        right = "M" * (3 - m) + "C" * (3 - c)
        boat = "boat left " if b else "boat right"
        move = f"  -> carry {'M' * a[0] + 'C' * a[1]}" if a else ""
        print(f"    {left:>6} | {boat} | {right:<6}{move}")


def show_routes():
    start, goal = "Olympus Mons", "Jezero crater"
    p = Route(start, goal)
    print(f"\nRoutes from {start} to {goal}:")
    for name, fn in [("BFS", breadth_first), ("UCS", uniform_cost),
                     ("DFS", depth_first)]:
        node, st = fn(p)
        print(f"  {name}: {' > '.join(path_states(node))}")
        print(f"       {len(path_actions(node))} roads, {node.path_cost:.0f} km;"
              f" generated {st.generated}, expanded {st.expanded}")


def show_puzzle():
    start = (7, 2, 4, 5, 0, 6, 8, 3, 1)
    p = EightPuzzle(start)
    print(f"\n8-puzzle from {start} (solvable: {solvable(start)}):")
    results = []
    for name, fn in [("BFS", breadth_first), ("UCS", uniform_cost),
                     ("IDS", iterative_deepening)]:
        node, st = fn(p)
        results.append((name, len(path_actions(node)), st))
    states, st = bidirectional_bfs(p, p.__class__(p.goal, p.initial))
    results.append(("bidirectional", len(states) - 1, st))
    node, st = depth_first(p)
    results.append(("DFS (graph)", len(path_actions(node)), st))
    print(f"  {'algorithm':14} {'moves':>6} {'generated':>10} {'expanded':>9}"
          f" {'max frontier':>13}")
    for name, moves, st in results:
        print(f"  {name:14} {moves:>6} {st.generated:>10} {st.expanded:>9}"
              f" {st.max_frontier:>13}")


if __name__ == "__main__":
    show_missionaries()
    show_routes()
    show_puzzle()
