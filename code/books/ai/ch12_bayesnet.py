# Chapter 12: a Bayesian network, exact inference and d-separation, from scratch (NumPy).
# The network (numbers invented for the example):
#   Storm -> Low (solar power low), Storm -> Dark (images dark), Storm -> Slow (drive fell short),
#   Fault (wheel motor fault) -> Slow, Slow -> Alert (ground team gets a short-drive alert).
# 1. The joint distribution as a product of conditional probability tables; size comparison.
# 2. Inference by enumeration and by variable elimination (factor product and summing out), with the same answers,
#    including "explaining away".
# 3. d-separation by a reachability ("Bayes ball") algorithm, checked against numerical independence for every
#    pair of variables and every conditioning set.
from itertools import combinations, product
import numpy as np

VARS = ["Storm", "Fault", "Low", "Dark", "Slow", "Alert"]
PARENTS = {"Storm": [], "Fault": [], "Low": ["Storm"], "Dark": ["Storm"], "Slow": ["Storm", "Fault"],
           "Alert": ["Slow"]}
# P(X = 1 | parents), indexed by the tuple of parent values
CPT = {"Storm": {(): 0.1}, "Fault": {(): 0.05},
       "Low": {(1,): 0.8, (0,): 0.1}, "Dark": {(1,): 0.7, (0,): 0.05},
       "Slow": {(1, 1): 0.95, (1, 0): 0.6, (0, 1): 0.7, (0, 0): 0.05},
       "Alert": {(1,): 0.9, (0,): 0.02}}


def p_local(x, val, assign):
    p1 = CPT[x][tuple(assign[u] for u in PARENTS[x])]
    return p1 if val else 1 - p1


def joint(assign):
    """The chain rule for Bayesian networks: P(x1..xn) = product of P(xi | parents(xi))."""
    out = 1.0
    for x in VARS:
        out *= p_local(x, assign[x], assign)
    return out


# ---------------------------------------------------------------- enumeration
def enumerate_ask(q, evidence):
    """P(q | evidence) by summing the full joint over all hidden variables: O(2^n) terms."""
    hidden = [v for v in VARS if v != q and v not in evidence]
    dist = np.zeros(2)
    for qv in (0, 1):
        for vals in product((0, 1), repeat=len(hidden)):
            a = dict(evidence, **dict(zip(hidden, vals)), **{q: qv})
            dist[qv] += joint(a)
    return dist / dist.sum()


# ---------------------------------------------------------------- variable elimination
class Factor:
    def __init__(self, vars_, table):
        self.vars, self.table = list(vars_), np.asarray(table, dtype=float)

    def __mul__(self, other):
        allv = self.vars + [v for v in other.vars if v not in self.vars]
        letters = {v: chr(97 + i) for i, v in enumerate(allv)}
        spec = "".join(letters[v] for v in self.vars) + "," + "".join(letters[v] for v in other.vars) + "->" + \
            "".join(letters[v] for v in allv)
        return Factor(allv, np.einsum(spec, self.table, other.table))

    def sum_out(self, v):
        i = self.vars.index(v)
        return Factor(self.vars[:i] + self.vars[i + 1:], self.table.sum(axis=i))

    def restrict(self, evidence):
        idx = tuple(evidence.get(v, slice(None)) for v in self.vars)
        return Factor([v for v in self.vars if v not in evidence], self.table[idx])


def cpt_factor(x):
    vs = PARENTS[x] + [x]
    t = np.zeros((2,) * len(vs))
    for vals in product((0, 1), repeat=len(vs)):
        a = dict(zip(vs, vals))
        t[vals] = p_local(x, a[x], a)
    return Factor(vs, t)


def eliminate(q, evidence, order=None, log=None):
    factors = [cpt_factor(x).restrict(evidence) for x in VARS]
    hidden = order or [v for v in VARS if v != q and v not in evidence]
    largest = max(len(f.vars) for f in factors)
    for h in hidden:
        involved = [f for f in factors if h in f.vars]
        rest = [f for f in factors if h not in f.vars]
        prod = involved[0]
        for f in involved[1:]:
            prod = prod * f
        largest = max(largest, len(prod.vars))
        new = prod.sum_out(h)
        if log is not None:
            log.append(f"    eliminate {h:<6}: multiply {len(involved)} factor(s) over {prod.vars}, "
                       f"sum out -> factor over {new.vars}")
        factors = rest + [new]
    result = factors[0]
    for f in factors[1:]:
        result = result * f
    t = result.table
    return t / t.sum(), largest


# ---------------------------------------------------------------- d-separation
def children(x):
    return [c for c in VARS if x in PARENTS[c]]


def d_separated(x, y, z):
    """Is x independent of y given the set z, by the graph alone? Search for an active trail from x
    (Koller and Friedman's reachability algorithm). A node is visited 'up' (arrived from a child) or 'down'."""
    z = set(z)
    anc = set()                                    # z and its ancestors: a collider is active if it is in here
    stack = list(z)
    while stack:
        v = stack.pop()
        if v not in anc:
            anc.add(v)
            stack.extend(PARENTS[v])
    visited, stack = set(), [(x, "up")]
    while stack:
        v, d = stack.pop()
        if (v, d) in visited:
            continue
        visited.add((v, d))
        if v not in z and v == y:
            return False                           # an active trail reaches y
        if d == "up" and v not in z:               # came from a child: may go up to parents or down to children
            stack += [(p, "up") for p in PARENTS[v]] + [(c, "down") for c in children(v)]
        elif d == "down":                          # came from a parent
            if v not in z:                         # chain: keep going down
                stack += [(c, "down") for c in children(v)]
            if v in anc:                           # collider with an observed descendant: go back up
                stack += [(p, "up") for p in PARENTS[v]]
    return True


def numerically_independent(x, y, z, tol=1e-12):
    for zv in product((0, 1), repeat=len(z)):
        ev = dict(zip(z, zv))
        pz = sum(joint(dict(ev, **dict(zip(o, ov)))) for o in [[v for v in VARS if v not in ev]]
                 for ov in product((0, 1), repeat=len(o)))
        if pz == 0:
            continue
        for xv, yv in product((0, 1), repeat=2):
            def p(extra):
                e = dict(ev, **extra)
                others = [v for v in VARS if v not in e]
                return sum(joint(dict(e, **dict(zip(others, ov)))) for ov in product((0, 1), repeat=len(others)))
            if abs(p({x: xv, y: yv}) / pz - p({x: xv}) / pz * p({y: yv}) / pz) > tol:
                return False
    return True


if __name__ == "__main__":
    n_params = sum(len(CPT[x]) for x in VARS)
    print(f"1. {len(VARS)} binary variables: the full joint needs {2 ** len(VARS) - 1} numbers, the network {n_params}")
    total = sum(joint(dict(zip(VARS, v))) for v in product((0, 1), repeat=len(VARS)))
    print(f"  the product of the CPTs sums to {total:.6f} over all {2 ** len(VARS)} assignments")
    print()

    print("2. Queries (enumeration = variable elimination)")
    queries = [("Storm", {}), ("Fault", {}), ("Fault", {"Alert": 1}), ("Fault", {"Alert": 1, "Low": 1}),
               ("Fault", {"Alert": 1, "Low": 0}), ("Storm", {"Alert": 1}), ("Storm", {"Alert": 1, "Dark": 1}),
               ("Slow", {"Low": 1})]
    for q, ev in queries:
        e = enumerate_ask(q, ev)
        v, _ = eliminate(q, ev)
        assert np.allclose(e, v)
        evs = ", ".join(f"{k}={val}" for k, val in ev.items()) or "nothing"
        label = f"P({q}=1 | {evs})"
        print(f"  {label:<34} = {v[1]:.4f}")
    log = []
    eliminate("Fault", {"Alert": 1}, log=log)
    print("  variable elimination for P(Fault | Alert=1), hidden variables in network order:")
    print("\n".join(log))
    for order in (["Storm", "Low", "Dark", "Slow"], ["Low", "Dark", "Slow", "Storm"]):
        _, largest = eliminate("Fault", {"Alert": 1}, order=order)
        print(f"  order {order}: largest factor has {largest} variables")
    print()

    print("3. d-separation checked against the numbers")
    agree = total_tests = 0
    examples = []
    for x, y in combinations(VARS, 2):
        others = [v for v in VARS if v not in (x, y)]
        for k in range(len(others) + 1):
            for z in combinations(others, k):
                g = d_separated(x, y, z)
                nmr = numerically_independent(x, y, list(z))
                total_tests += 1
                agree += g == nmr
                if (x, y, z) in [("Low", "Dark", ()), ("Low", "Dark", ("Storm",)), ("Storm", "Fault", ()),
                                 ("Storm", "Fault", ("Slow",)), ("Storm", "Fault", ("Alert",)),
                                 ("Fault", "Low", ("Alert",)), ("Fault", "Low", ("Storm", "Alert"))]:
                    examples.append(f"  {x} ⊥ {y} | {{{', '.join(z)}}}: graph says {g}, numbers say {nmr}")
    print("\n".join(examples))
    print(f"  graph and numbers agree on {agree} of {total_tests} (pair, conditioning set) tests")
