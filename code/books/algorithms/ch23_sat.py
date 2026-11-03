# Chapter 23: two ways real tools attack an NP-complete problem.
# DPLL (Davis, Putnam, Logemann, Loveland): backtracking + unit propagation.
# WalkSAT (Selman, Kautz, Cohen): local search that flips variables.
import random


def random_3sat(n, m, rng):
    clauses = []
    for _ in range(m):
        vs = rng.sample(range(1, n + 1), 3)
        clauses.append([v if rng.random() < 0.5 else -v for v in vs])
    return clauses


def dpll(clauses, assignment, stats):
    # Unit propagation: a clause with one unset literal and no true literal forces it.
    assignment = dict(assignment)
    while True:
        unit = None
        for c in clauses:
            if any(assignment.get(abs(l)) == (l > 0) for l in c):
                continue                            # clause already true
            free = [l for l in c if abs(l) not in assignment]
            if not free:
                stats["conflicts"] += 1
                return None                         # clause false: back up
            if len(free) == 1:
                unit = free[0]
                break
        if unit is None:
            break
        assignment[abs(unit)] = unit > 0
        stats["propagations"] += 1
    # Pick an unset variable that appears most often in unsatisfied clauses.
    counts = {}
    for c in clauses:
        if any(assignment.get(abs(l)) == (l > 0) for l in c):
            continue
        for l in c:
            if abs(l) not in assignment:
                counts[abs(l)] = counts.get(abs(l), 0) + 1
    if not counts:
        return assignment                           # every clause true
    var = max(counts, key=counts.get)
    for value in (True, False):
        stats["decisions"] += 1
        assignment[var] = value
        result = dpll(clauses, assignment, stats)
        if result is not None:
            return result
        del assignment[var]
    return None


def walksat(clauses, n, rng, p=0.5, max_flips=100000):
    x = {v: rng.random() < 0.5 for v in range(1, n + 1)}
    sat = lambda c: any(x[abs(l)] == (l > 0) for l in c)
    for flip in range(max_flips):
        unsat = [c for c in clauses if not sat(c)]
        if not unsat:
            return x, flip
        c = rng.choice(unsat)
        if rng.random() < p:
            v = abs(rng.choice(c))                  # random walk step
        else:                                       # greedy step: fewest new breaks
            def breaks(v):
                x[v] = not x[v]
                b = sum(1 for d in clauses if not sat(d))
                x[v] = not x[v]
                return b
            v = min((abs(l) for l in c), key=breaks)
        x[v] = not x[v]
    return None, max_flips


def check(clauses, x):
    return all(any(x.get(abs(l), False) == (l > 0) for l in c) for c in clauses)


rng = random.Random(1962)
n = 40
print(" ratio  clauses  DPLL result  decisions  conflicts   WalkSAT flips")
for ratio in (3.0, 4.0, 4.26, 5.0, 6.0):
    m = int(ratio * n)
    clauses = random_3sat(n, m, rng)
    stats = {"decisions": 0, "conflicts": 0, "propagations": 0}
    res = dpll(clauses, {}, stats)
    verdict = "SAT" if res is not None else "UNSAT"
    if res is not None:
        assert check(clauses, res)
        _, flips = walksat(clauses, n, random.Random(1), max_flips=5000)
        walk = str(flips)
    else:
        walk = "(cannot prove UNSAT)"
    print(f"{ratio:5.2f}  {m:7d}  {verdict:>11}  {stats['decisions']:9d}  {stats['conflicts']:9d}   {walk}")
