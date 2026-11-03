"""Chapter 22: 3-SAT -> directed Hamiltonian cycle (the 'rows of beads' construction), then
directed -> undirected Hamiltonian cycle, each checked by exhaustive search on small formulas."""
import random
from itertools import product

random.seed(1736)


def satisfiable(formula, n):
    return any(all(any(bits[abs(l) - 1] == (l > 0) for l in c) for c in formula)
               for bits in product((False, True), repeat=n))


def sat_to_directed_ham(formula, n):
    """Row i (variable x_i) is a path of b = 3k + 3 beads, linked both ways. Crossing it left to right means
    x_i = true. Clause j has its own vertex, reached by a detour from beads 3j+2 -> 3j+3 (0-based) of row i."""
    k = len(formula)
    b = 3 * k + 3
    bead = lambda i, p: ("v", i, p)                     # row i in 1..n, position p in 0..b-1
    s, t = ("s",), ("t",)
    out = {}
    add = lambda u, v: out.setdefault(u, []).append(v)
    for i in range(1, n + 1):
        for p in range(b - 1):
            add(bead(i, p), bead(i, p + 1))
            add(bead(i, p + 1), bead(i, p))
    ends = lambda i: (bead(i, 0), bead(i, b - 1))
    for e in ends(1):
        add(s, e)
    for i in range(1, n):
        for u in ends(i):
            for v in ends(i + 1):
                add(u, v)
    for u in ends(n):
        add(u, t)
    add(t, s)
    for j, clause in enumerate(formula):
        c = ("c", j)
        left, right = 3 * j + 2, 3 * j + 3          # beads 0, 1 and 3k+1, 3k+2 stay free of detours
        for lit in clause:
            i = abs(lit)
            if lit > 0:                                 # usable when row i is crossed left to right
                add(bead(i, left), c)
                add(c, bead(i, right))
            else:                                       # usable when crossed right to left
                add(bead(i, right), c)
                add(c, bead(i, left))
    vertices = {s, t} | {bead(i, p) for i in range(1, n + 1) for p in range(b)} | {("c", j) for j in range(k)}
    return vertices, out


def directed_to_undirected(vertices, out):
    """Each vertex v becomes a path v_in - v_mid - v_out; each arc u -> v becomes the edge u_out - v_in."""
    adj = {}
    link = lambda a, b: (adj.setdefault(a, set()).add(b), adj.setdefault(b, set()).add(a))
    # (sets are fine here: this graph is only used to check a given cycle)
    for v in vertices:
        link((v, "in"), (v, "mid"))
        link((v, "mid"), (v, "out"))
    for u, targets in out.items():
        for v in targets:
            link((u, "out"), (v, "in"))
    return adj


def find_ham_cycle(succ, vertices, start):
    """Depth-first search for a cycle through every vertex (directed: succ[v] lists the arcs out of v;
    an undirected graph is the special case where every edge is an arc both ways). Pruning rule: every
    vertex not yet on the path must still be enterable (from an unvisited vertex or the path's end) and
    leavable (to an unvisited vertex or back to the start), and not only through one and the same
    neighbour; otherwise this branch is dead."""
    vertices = list(vertices)
    pred = {v: [] for v in vertices}
    for u in vertices:
        for v in succ.get(u, ()):
            pred[v].append(u)
    on_path = {start}
    path = [start]
    n = len(vertices)

    def alive(end):
        for w in vertices:
            if w in on_path:
                continue
            ins = [u for u in pred[w] if u == end or u not in on_path]
            outs = [x for x in succ.get(w, ()) if x == start or x not in on_path]
            if not ins or not outs or (len(ins) == 1 and outs == ins and n > 2):
                return False                      # w would have to be entered and left through one vertex
        return True

    def extend(v):
        if len(path) == n:
            return start in succ.get(v, ())
        if not alive(v):
            return False
        for w in succ.get(v, ()):
            if w not in on_path:
                on_path.add(w)
                path.append(w)
                if extend(w):
                    return True
                path.pop()
                on_path.remove(w)
        return False

    return path if extend(start) else None


def random_3cnf(n, k):
    return [[v * random.choice((1, -1)) for v in random.sample(range(1, n + 1), 3)] for _ in range(k)]


def is_undirected_cycle(adj, cycle):
    return len(set(cycle)) == len(adj) and all(cycle[i - 1] in adj[cycle[i]] for i in range(len(cycle)))


S = ("s",)
example = [[1, -2, 3], [-1, 2, -3]]
V, A = sat_to_directed_ham(example, 3)
print(f"Example {example}: directed graph with {len(V)} vertices and {sum(map(len, A.values()))} arcs")
cycle = find_ham_cycle(A, sorted(V), S)
print("  formula satisfiable:", satisfiable(example, 3), "  Hamiltonian cycle found:", cycle is not None)
rows = [v for v in cycle if v[0] == "v"]
for i in (1, 2, 3):
    first = next(v for v in rows if v[1] == i)
    print(f"  row {i} entered at bead {first[2]:2}: x{i} = {first[2] == 0}")
print("  clause vertices visited after:", [cycle[cycle.index(("c", j)) - 1] for j in range(2)])
U = directed_to_undirected(V, A)
tripled = [(v, part) for v in cycle for part in ("in", "mid", "out")]
print(f"  undirected version: {len(U)} vertices, {sum(map(len, U.values())) // 2} edges;"
      f" the tripled cycle is a Hamiltonian cycle there: {is_undirected_cycle(U, tripled)}")

unsat = [[a, b, c] for a in (1, -1) for b in (2, -2) for c in (3, -3)]
V, A = sat_to_directed_ham(unsat, 3)
print(f"\nAll 8 clauses on x1, x2, x3 (unsatisfiable): {len(V)} vertices;"
      f" Hamiltonian cycle found: {find_ham_cycle(A, sorted(V), S) is not None}")

print("\nFour variables: all 8 sign patterns on three of them (with none or one removed), plus one random clause:")
agree = sat = 0
tests = []
for trial in range(4):
    a, b, c = random.sample(range(1, 5), 3)
    f = [[sa * a, sb * b, sc * c] for sa in (1, -1) for sb in (1, -1) for sc in (1, -1)]
    if trial % 2:
        f.pop(random.randrange(8))
    f += random_3cnf(4, 1)
    random.shuffle(f)
    tests.append(f)
for f in tests:
    truth = satisfiable(f, 4)
    V, A = sat_to_directed_ham(f, 4)
    agree += (find_ham_cycle(A, sorted(V), S) is not None) == truth
    sat += truth
print(f"  the reduction agreed with brute force on {agree} of {len(tests)} formulas ({sat} satisfiable)")
