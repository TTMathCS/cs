"""Chapter 22: the Cook-Levin idea in miniature. A verifier's certificate becomes Boolean variables and
its checks become clauses. Two examples: a logic circuit (Tseitin's encoding) and graph 3-colouring."""
from itertools import product, combinations


def dpll(clauses, assignment=None):
    """A small SAT solver: unit propagation, then branch on a variable (Davis, Putnam, Logemann, Loveland)."""
    assignment = dict(assignment or {})
    while True:
        simplified, unit = [], None
        for c in clauses:
            if any(assignment.get(abs(l)) == (l > 0) for l in c):
                continue                                   # clause already true
            rest = [l for l in c if abs(l) not in assignment]
            if not rest:
                return None                                # clause false: dead end
            if len(rest) == 1:
                unit = rest[0]
            simplified.append(rest)
        if not simplified:
            return assignment
        if unit is None:
            break
        assignment[abs(unit)] = unit > 0                   # a unit clause forces its literal
        clauses = simplified
    v = abs(simplified[0][0])
    for value in (True, False):
        result = dpll(simplified, {**assignment, v: value})
        if result is not None:
            return result
    return None


# 1. Circuit: out = (x1 AND x2) OR (NOT x3). Variables: x1, x2, x3 = 1, 2, 3; gate g = 4, h = 5, out = 6.
def AND(g, a, b):          # g <-> (a and b)
    return [[-g, a], [-g, b], [g, -a, -b]]


def OR(g, a, b):           # g <-> (a or b)
    return [[g, -a], [g, -b], [-g, a, b]]


def NOT(g, a):             # g <-> not a
    return [[g, a], [-g, -a]]


circuit = AND(4, 1, 2) + NOT(5, 3) + OR(6, 4, 5)
print("Circuit out = (x1 AND x2) OR (NOT x3), as", len(circuit), "clauses:", circuit)
print("  inputs  circuit  CNF with out forced true is satisfiable")
for bits in product((False, True), repeat=3):
    x1, x2, x3 = bits
    direct = (x1 and x2) or (not x3)
    fixed = {1: x1, 2: x2, 3: x3}
    cnf = dpll(circuit + [[6]], fixed) is not None
    print(f"  {''.join('1' if b else '0' for b in bits)}     {int(direct)}        {cnf}")


# 2. Graph 3-colouring. Variable var(v, c) means "vertex v has colour c".
def colouring_cnf(n, edges, colours=3):
    var = lambda v, c: v * colours + c + 1
    cnf = [[var(v, c) for c in range(colours)] for v in range(n)]                       # some colour
    cnf += [[-var(v, a), -var(v, b)] for v in range(n) for a, b in combinations(range(colours), 2)]  # one only
    cnf += [[-var(u, c), -var(v, c)] for u, v in edges for c in range(colours)]         # ends differ
    return cnf, var


petersen = [(i, (i + 1) % 5) for i in range(5)] + [(i, i + 5) for i in range(5)] + \
           [(5 + i, 5 + (i + 2) % 5) for i in range(5)]
k4 = list(combinations(range(4), 2))
for name, n, edges in (("Petersen graph", 10, petersen), ("complete graph K4", 4, k4)):
    cnf, var = colouring_cnf(n, edges)
    a = dpll(cnf)
    print(f"\n{name}: {n * 3} variables, {len(cnf)} clauses;", "satisfiable" if a else "unsatisfiable")
    if a:
        colour = [next(c for c in range(3) if a.get(var(v, c))) for v in range(n)]
        print("  colours:", colour, " proper:", all(colour[u] != colour[v] for u, v in edges))
