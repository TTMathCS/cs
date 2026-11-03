# Chapter 8: DPLL (Davis, Logemann, Loveland 1962) and WalkSAT (Selman, Kautz, Cohen 1994), from scratch.
# A formula is a list of clauses; a clause is a list of non-zero integers (DIMACS style): 3 means x3, -3 means not x3.
import random
from itertools import combinations


def simplify(clauses, lit):
    """Set literal lit true: drop satisfied clauses, delete the opposite literal elsewhere."""
    out = []
    for c in clauses:
        if lit in c:
            continue
        if -lit in c:
            c = [l for l in c if l != -lit]
        out.append(c)
    return out


def dpll(clauses, assignment, stats, use_pure=True):
    # unit propagation
    while True:
        if any(len(c) == 0 for c in clauses):
            stats["conflicts"] += 1
            return None
        units = [c[0] for c in clauses if len(c) == 1]
        if not units:
            break
        stats["propagations"] += 1
        assignment = assignment | {units[0]}
        clauses = simplify(clauses, units[0])
    if not clauses:
        return assignment
    # pure literals: a symbol that appears with one sign only can be set to make it true
    if use_pure:
        lits = {l for c in clauses for l in c}
        pure = [l for l in lits if -l not in lits]
        if pure:
            for l in pure:
                clauses = simplify(clauses, l)
            return dpll(clauses, assignment | set(pure), stats, use_pure)
    # branch on the variable occurring most often (ties: smallest number)
    counts = {}
    for c in clauses:
        for l in c:
            counts[abs(l)] = counts.get(abs(l), 0) + 1
    v = min(counts, key=lambda x: (-counts[x], x))
    for lit in (v, -v):
        stats["decisions"] += 1
        r = dpll(simplify(clauses, lit), assignment | {lit}, stats, use_pure)
        if r is not None:
            return r
    return None


def solve(clauses, **kw):
    stats = {"decisions": 0, "propagations": 0, "conflicts": 0}
    return dpll(clauses, frozenset(), stats, **kw), stats


def walksat(clauses, n, rng, p=0.5, max_flips=100000):
    x = [False] + [rng.random() < 0.5 for _ in range(n)]
    occurs = {}
    for i, c in enumerate(clauses):
        for l in c:
            occurs.setdefault(-l, []).append(i)          # clauses that become false-ish if l is made false
    true_count = [sum(1 for l in c if x[abs(l)] == (l > 0)) for c in clauses]
    unsat = {i for i, k in enumerate(true_count) if k == 0}
    for flip in range(max_flips):
        if not unsat:
            return x, flip
        c = clauses[rng.choice(sorted(unsat))]
        if rng.random() < p:
            v = abs(rng.choice(c))                       # random walk
        else:                                            # greedy: the flip that breaks fewest clauses
            def breaks(v):
                lit_now_true = v if x[v] else -v
                return sum(1 for i in occurs.get(-lit_now_true, []) if true_count[i] == 1)
            v = min(sorted({abs(l) for l in c}), key=breaks)
        lit_before = v if x[v] else -v                   # this literal is true now and becomes false
        x[v] = not x[v]
        for i in occurs.get(-lit_before, []):           # clauses containing lit_before lose a true literal
            true_count[i] -= 1
            if true_count[i] == 0:
                unsat.add(i)
        for i in occurs.get(lit_before, []):            # clauses containing -lit_before gain one
            true_count[i] += 1
            unsat.discard(i)
    return None, max_flips


def check(clauses, model):
    return all(any((l > 0) == (abs(l) in model) for l in c) for c in clauses)


# ---- encodings
def queens_sat(n):
    var = lambda r, c: r * n + c + 1                     # x_{r,c}: a queen on row r, column c
    cl = []
    for c in range(n):
        cl.append([var(r, c) for r in range(n)])         # at least one queen per column
    squares = [(r, c) for r in range(n) for c in range(n)]
    for (r1, c1), (r2, c2) in combinations(squares, 2):  # at most one per row, column, diagonal
        if r1 == r2 or c1 == c2 or abs(r1 - r2) == abs(c1 - c2):
            cl.append([-var(r1, c1), -var(r2, c2)])
    return cl


def pigeonhole(holes):
    """holes + 1 pigeons in `holes` holes, at most one per hole: unsatisfiable."""
    p = holes + 1
    var = lambda i, j: i * holes + j + 1
    cl = [[var(i, j) for j in range(holes)] for i in range(p)]
    for j in range(holes):
        for i1, i2 in combinations(range(p), 2):
            cl.append([-var(i1, j), -var(i2, j)])
    return cl


q8 = queens_sat(8)
model, st = solve(q8)
pos = sorted(l for l in model if l > 0)
print(f"8-queens as SAT: {len(q8)} clauses over 64 variables; DPLL: {st}")
print("  queens at (row, column):", [((v - 1) // 8, (v - 1) % 8) for v in pos], " valid:", check(q8, set(pos)))
rng = random.Random(1994)
x, flips = walksat(q8, 64, rng)
print(f"  WalkSAT found a solution after {flips} flips: {check(q8, {v for v in range(1, 65) if x[v]})}")

print("\npigeonhole: n + 1 pigeons, n holes (unsatisfiable); DPLL work grows exponentially")
for h in range(3, 9):
    cl = pigeonhole(h)
    model, st = solve(cl)
    print(f"  holes {h}: {len(cl):4d} clauses, satisfiable {model is not None}, decisions {st['decisions']:6d},"
          f" conflicts {st['conflicts']:6d}")

# Entailment by SAT: KB |= alpha iff KB and not alpha is unsatisfiable (wumpus KB of ch08_logic.py)
# symbols: 1 B11, 2 B21, 3 P11, 4 P12, 5 P21, 6 P22, 7 P31
kb = [[-1], [-3], [2], [2, -3], [1, -4], [1, -5], [2, -6], [2, -7], [-1, 4, 5], [-2, 3, 6, 7]]
print()
for lits, name in (([4], "P12"), ([6], "P22")):
    model, st = solve(kb + [lits])
    print(f"KB and {name}: satisfiable {model is not None}  -> KB entails not {name}: {model is None}")
