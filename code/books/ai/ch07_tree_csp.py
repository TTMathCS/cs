# Chapter 7: tree-structured CSPs in O(n d^2), and cutset conditioning.
import itertools
import random
from collections import deque


def tree_solve(nodes, edges, domains, allowed, root=None, count_checks=None):
    """nodes: list; edges: list of (u, v) forming a forest; allowed[(u, v)] = set of (a, b) pairs.
    Returns an assignment or None. Directed arc consistency from the leaves up, then assign from the root down."""
    adj = {x: [] for x in nodes}
    for u, v in edges:
        adj[u].append(v)
        adj[v].append(u)

    def ok(u, a, v, b):
        if count_checks is not None:
            count_checks[0] += 1
        return (a, b) in allowed[(u, v)] if (u, v) in allowed else (b, a) in allowed[(v, u)]

    dom = {x: list(domains[x]) for x in nodes}
    parent, order, seen = {}, [], set()
    for r in ([root] if root is not None else []) + nodes:     # every tree of the forest gets a root
        if r in seen:
            continue
        seen.add(r)
        parent[r] = None
        q = deque([r])
        while q:                                                # breadth-first: parents come before children
            x = q.popleft()
            order.append(x)
            for y in adj[x]:
                if y not in seen:
                    seen.add(y)
                    parent[y] = x
                    q.append(y)
    # backward pass: make each arc parent -> child consistent, children first
    for x in reversed(order):
        p = parent[x]
        if p is None:
            continue
        dom[p] = [a for a in dom[p] if any(ok(p, a, x, b) for b in dom[x])]
        if not dom[p]:
            return None
    # forward pass: any value left for the parent has a support in each child, so no backtracking
    value = {}
    for x in order:
        p = parent[x]
        choices = dom[x] if p is None else [b for b in dom[x] if ok(p, value[p], x, b)]
        value[x] = choices[0]
    return value


def brute_force(nodes, edges, domains, allowed):
    for vals in itertools.product(*(domains[x] for x in nodes)):
        a = dict(zip(nodes, vals))
        if all((a[u], a[v]) in allowed[(u, v)] for u, v in edges):
            return a
    return None


def random_tree_csp(n, d, density, rng):
    nodes = list(range(n))
    edges = [(rng.randrange(i), i) for i in range(1, n)]           # node i hangs below a random earlier node
    allowed = {e: {(a, b) for a in range(d) for b in range(d) if rng.random() < density} for e in edges}
    return nodes, edges, {x: list(range(d)) for x in nodes}, allowed


rng = random.Random(1982)
agree = solvable = 0
for trial in range(200):
    nodes, edges, doms, allowed = random_tree_csp(8, 3, 0.45, rng)
    t = tree_solve(nodes, edges, doms, allowed)
    b = brute_force(nodes, edges, doms, allowed)
    if t is not None:
        assert all((t[u], t[v]) in allowed[(u, v)] for u, v in edges)
    agree += (t is None) == (b is None)
    solvable += b is not None
print(f"200 random tree CSPs (8 variables, 3 values; {solvable} solvable): tree solver and brute force agree"
      f" in {agree}")

print("\nconstraint checks of the tree solver (d = 5, every pair allowed with probability 0.6):")
print("       n    checks   checks / (n d^2)   solved")
for n in (10, 100, 1000, 10000, 100000):
    nodes, edges, doms, allowed = random_tree_csp(n, 5, 0.6, rng)
    checks = [0]
    sol = tree_solve(nodes, edges, doms, allowed, count_checks=checks)
    print(f"{n:8d}  {checks[0]:8d}   {checks[0] / (n * 25):16.3f}   {sol is not None}")

# Cutset conditioning on the map of Australia: removing SA leaves a forest.
nbrs = {"WA": ["NT", "SA"], "NT": ["WA", "SA", "Q"], "SA": ["WA", "NT", "Q", "NSW", "V"],
        "Q": ["NT", "SA", "NSW"], "NSW": ["Q", "SA", "V"], "V": ["SA", "NSW"], "T": []}
colours = ["red", "green", "blue"]
diff = {(a, b) for a in colours for b in colours if a != b}
print("\ncutset conditioning on Australia with cutset {SA}:")
for c in colours:
    rest = [x for x in nbrs if x != "SA"]
    edges = sorted({tuple(sorted((u, v))) for u in rest for v in nbrs[u] if v != "SA"})
    doms = {x: [k for k in colours if not ("SA" in nbrs[x] and k == c)] for x in rest}   # neighbours of SA lose c
    sol = tree_solve(rest, edges, doms, {e: diff for e in edges})
    print(f"  SA = {c:5s}: remaining forest {edges}; solution {sol}")
