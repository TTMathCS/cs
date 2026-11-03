# Chapter 7: a small constraint-satisfaction library and backtracking search with
# MRV, degree and least-constraining-value heuristics, forward checking and MAC (AC-3 inside search).
from collections import deque


class CSP:
    """Binary CSP: variables, a domain per variable, and for each constrained pair a test ok(x, a, y, b)."""

    def __init__(self, variables, domains, neighbours, ok):
        self.variables = list(variables)
        self.domains = {v: list(domains[v]) for v in self.variables}
        self.neighbours = neighbours
        self.ok = ok


def consistent(csp, var, value, assignment):
    return all(csp.ok(var, value, n, assignment[n]) for n in csp.neighbours[var] if n in assignment)


def revise(csp, domains, x, y):
    """Remove values of x that have no supporting value in y. Return True if something was removed."""
    removed = False
    for a in domains[x][:]:
        if not any(csp.ok(x, a, y, b) for b in domains[y]):
            domains[x].remove(a)
            removed = True
    return removed


def ac3(csp, domains, queue=None, stats=None):
    """Make every arc (x, y) consistent. Returns False if some domain becomes empty."""
    if queue is None:
        queue = deque((x, y) for x in csp.variables for y in csp.neighbours[x])
    while queue:
        x, y = queue.popleft()
        if stats is not None:
            stats["revisions"] += 1
        if revise(csp, domains, x, y):
            if not domains[x]:
                return False
            for z in csp.neighbours[x]:
                if z != y:
                    queue.append((z, x))
    return True


def solve(csp, mrv=False, degree=False, lcv=False, inference=None):
    """Backtracking search. inference: None, 'fc' (forward checking) or 'mac'. Returns (solution, assignments)."""
    stats = {"assignments": 0}

    def select(assignment, domains):
        unassigned = [v for v in csp.variables if v not in assignment]
        if not mrv:
            return unassigned[0]
        def key(v):
            unassigned_nbrs = sum(1 for n in csp.neighbours[v] if n not in assignment)
            return (len(domains[v]), -unassigned_nbrs if degree else 0)
        return min(unassigned, key=key)

    def order(var, assignment, domains):
        if not lcv:
            return list(domains[var])
        def ruled_out(value):          # how many neighbour values this choice removes
            return sum(1 for n in csp.neighbours[var] if n not in assignment
                       for b in domains[n] if not csp.ok(var, value, n, b))
        return sorted(domains[var], key=ruled_out)

    def backtrack(assignment, domains):
        if len(assignment) == len(csp.variables):
            return dict(assignment)
        var = select(assignment, domains)
        for value in order(var, assignment, domains):
            if not consistent(csp, var, value, assignment):
                continue
            stats["assignments"] += 1
            assignment[var] = value
            new = {v: list(d) for v, d in domains.items()}
            new[var] = [value]
            ok = True
            if inference == "fc":
                for n in csp.neighbours[var]:
                    if n not in assignment:
                        new[n] = [b for b in new[n] if csp.ok(var, value, n, b)]
                        if not new[n]:
                            ok = False
                            break
            elif inference == "mac":
                ok = ac3(csp, new, deque((n, var) for n in csp.neighbours[var] if n not in assignment))
            if ok:
                result = backtrack(assignment, new)
                if result is not None:
                    return result
            del assignment[var]
        return None

    return backtrack({}, csp.domains), stats["assignments"]


def different(x, a, y, b):
    return a != b


# ---- map colouring: the states and territories of Australia
nbrs = {"WA": ["NT", "SA"], "NT": ["WA", "SA", "Q"], "SA": ["WA", "NT", "Q", "NSW", "V"],
        "Q": ["NT", "SA", "NSW"], "NSW": ["Q", "SA", "V"], "V": ["SA", "NSW"], "T": []}
australia = CSP(nbrs, {v: ["red", "green", "blue"] for v in nbrs}, nbrs, different)
print("Australia, plain backtracking:      ", solve(australia))
print("Australia, MRV + degree + fc:       ", solve(australia, mrv=True, degree=True, inference="fc"))


# ---- n-queens: variable = column, value = row
def queens(n):
    cols = list(range(n))
    nb = {c: [d for d in cols if d != c] for c in cols}
    return CSP(cols, {c: list(range(n)) for c in cols}, nb,
               lambda x, a, y, b: a != b and abs(a - b) != abs(x - y))


print("\nn-queens: number of assignments until the first solution")
configs = [("plain", {}), ("forward checking", {"inference": "fc"}),
           ("MRV + fc", {"mrv": True, "inference": "fc"}),
           ("MRV + degree + LCV + fc", {"mrv": True, "degree": True, "lcv": True, "inference": "fc"}),
           ("MRV + MAC", {"mrv": True, "inference": "mac"})]
SIZES = (8, 12, 16, 24, 32)
print(f"{'':26s}" + "".join(f"{'n=' + str(n):>9s}" for n in SIZES))
for name, kw in configs:
    row = []
    for n in SIZES:
        if name in ("plain", "forward checking") and n > 16:
            row.append("-")
            continue
        sol, count = solve(queens(n), **kw)
        assert all(sol[a] != sol[b] and abs(sol[a] - sol[b]) != b - a for a in range(n) for b in range(a + 1, n))
        row.append(str(count))
    print(f"{name:26s}" + "".join(f"{r:>9s}" for r in row))


# ---- Sudoku: 81 variables, values 1-9, all-different on rows, columns and boxes (as binary constraints)
def sudoku(grid):
    cells = [(r, c) for r in range(9) for c in range(9)]
    def peers(rc):
        r, c = rc
        ps = {(r, k) for k in range(9)} | {(k, c) for k in range(9)}
        ps |= {(3 * (r // 3) + i, 3 * (c // 3) + j) for i in range(3) for j in range(3)}
        ps.discard(rc)
        return sorted(ps)
    nb = {rc: peers(rc) for rc in cells}
    doms = {}
    for r, c in cells:
        ch = grid[9 * r + c]
        doms[(r, c)] = [int(ch)] if ch in "123456789" else list(range(1, 10))
    return CSP(cells, doms, nb, different)


easy = ("..3.2.6.." "9..3.5..1" "..18.64.." "..81.29.." "7.......8"
        "..67.82.." "..26.95.." "8..2.3..9" "..5.1.3..")
hard = ("4.....8.5" ".3......." "...7....." ".2.....6." "....8.4.."
        "....1...." "...6.3.7." "5..2....." "1.4......")
for label, puzzle in (("an easy puzzle, 32 clues", easy), ("a hard puzzle, 17 clues", hard)):
    print(f"\nSudoku, {label} (every cell counts as an assignment; 81 means no backtracking)")
    for name, kw in (("MRV + fc", {"mrv": True, "inference": "fc"}), ("MRV + MAC", {"mrv": True, "inference": "mac"})):
        sol, count = solve(sudoku(puzzle), **kw)
        print(f"  {name:10s} assignments {count}")
for r in range(9):
    print("   " + " ".join(str(sol[(r, c)]) for c in range(9)))
