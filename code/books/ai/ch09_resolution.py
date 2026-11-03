# Chapter 9: resolution theorem proving in first-order logic, from scratch.
# 1. Conversion to clausal form, printed step by step: remove =>, push negation in, rename variables apart,
#    Skolemize, drop the universal quantifiers, distribute OR over AND.
# 2. A resolution prover (given-clause loop with binary resolution and factoring) that prints its proof.
# 3. Why factoring is needed: {P(x), P(y)} and {~P(u), ~P(v)} have no binary-resolution refutation.
# 4. Answer extraction: the proof of "some x is a grandchild of Ada" tells us which x.
# Formulas are tuples: ('all', '?x', F), ('ex', '?x', F), ('=>', A, B), ('&', A, B), ('|', A, B), ('~', A),
# and atoms such as ('Rover', '?x').
from itertools import count
from ch09_unify import is_var, show, substitute, term, unify

CONNECTIVES = {"all", "ex", "=>", "<=>", "&", "|", "~"}


def is_atom(f):
    return f[0] not in CONNECTIVES


def fshow(f):
    op = f[0]
    if is_atom(f):
        return show(f)
    if op == "~":
        return "~" + fshow(f[1])
    if op in ("all", "ex"):
        return ("∀" if op == "all" else "∃") + f[1][1:] + " " + fshow(f[2])
    sym = {"=>": " ⇒ ", "<=>": " ⇔ ", "&": " ∧ ", "|": " ∨ "}[op]
    return "(" + fshow(f[1]) + sym + fshow(f[2]) + ")"


def no_implications(f):
    if is_atom(f):
        return f
    op = f[0]
    if op in ("all", "ex"):
        return (op, f[1], no_implications(f[2]))
    if op == "~":
        return ("~", no_implications(f[1]))
    a, b = no_implications(f[1]), no_implications(f[2])
    if op == "=>":
        return ("|", ("~", a), b)
    if op == "<=>":
        return ("&", ("|", ("~", a), b), ("|", ("~", b), a))
    return (op, a, b)


def negation_in(f):
    if is_atom(f):
        return f
    op = f[0]
    if op in ("all", "ex"):
        return (op, f[1], negation_in(f[2]))
    if op in ("&", "|"):
        return (op, negation_in(f[1]), negation_in(f[2]))
    g = f[1]                                     # f = ~g
    if is_atom(g):
        return f
    if g[0] == "~":
        return negation_in(g[1])
    if g[0] == "&":
        return ("|", negation_in(("~", g[1])), negation_in(("~", g[2])))
    if g[0] == "|":
        return ("&", negation_in(("~", g[1])), negation_in(("~", g[2])))
    if g[0] == "all":
        return ("ex", g[1], negation_in(("~", g[2])))
    return ("all", g[1], negation_in(("~", g[2])))    # ~∃x P  ==  ∀x ~P


fresh = count(1)


def rename_term(t, m):
    if is_var(t):
        return m.get(t, t)
    if isinstance(t, tuple):
        return (t[0],) + tuple(rename_term(a, m) for a in t[1:])
    return t


def standardize(f, m=None):
    """Give every quantifier its own variable name."""
    m = {} if m is None else m
    if is_atom(f):
        return rename_term(f, m)
    op = f[0]
    if op in ("all", "ex"):
        v = f"?{f[1][1:].split('_')[0]}{next(fresh)}"
        return (op, v, standardize(f[2], {**m, f[1]: v}))
    if op == "~":
        return ("~", standardize(f[1], m))
    return (op, standardize(f[1], m), standardize(f[2], m))


skolem_names = count(1)


def skolemize(f, universals=()):
    """Replace each ∃y by a new function of the universally quantified variables around it."""
    if is_atom(f):
        return f
    op = f[0]
    if op == "all":
        return ("all", f[1], skolemize(f[2], universals + (f[1],)))
    if op == "ex":
        k = next(skolem_names)
        sk = (f"F{k}",) + universals if universals else f"C{k}"
        return skolemize(substitute(f[2], {f[1]: sk}), universals)
    if op == "~":
        return f
    return (op, skolemize(f[1], universals), skolemize(f[2], universals))


def drop_universals(f):
    if is_atom(f) or f[0] == "~":
        return f
    if f[0] == "all":
        return drop_universals(f[2])
    return (f[0], drop_universals(f[1]), drop_universals(f[2]))


def distribute(f):
    """Return a list of clauses; a clause is a list of literals (sign, atom)."""
    if is_atom(f):
        return [[(True, f)]]
    if f[0] == "~":
        return [[(False, f[1])]]
    if f[0] == "&":
        return distribute(f[1]) + distribute(f[2])
    return [a + b for a in distribute(f[1]) for b in distribute(f[2])]   # (A1∧A2) ∨ (B1∧B2) -> 4 clauses


def to_clauses(f, verbose=False):
    steps = [("start", f)]
    f = no_implications(f); steps.append(("remove ⇒ and ⇔", f))
    f = negation_in(f); steps.append(("push ~ inward", f))
    f = standardize(f); steps.append(("rename variables apart", f))
    f = skolemize(f); steps.append(("Skolemize", f))
    f = drop_universals(f); steps.append(("drop ∀", f))
    clauses = distribute(f)
    if verbose:
        for name, g in steps:
            print(f"  {name:<24} {fshow(g)}")
        print(f"  {'distribute ∨ over ∧':<24} " + "   ".join(cshow(c) for c in clauses))
    return clauses


def lshow(lit):
    return ("" if lit[0] else "~") + show(lit[1])


def cshow(c):
    return "{" + ", ".join(lshow(l) for l in c) + "}" if c else "{} (empty clause)"


# ---------------------------------------------------------------- the prover
def vars_in(t, acc):
    if is_var(t):
        acc.append(t)
    elif isinstance(t, tuple):
        for a in t[1:]:
            vars_in(a, acc)
    return acc


def blank(t):
    if is_var(t):
        return "_"
    if isinstance(t, tuple):
        return (t[0],) + tuple(blank(a) for a in t[1:])
    return t


def canonical(lits):
    """Sort literals and rename variables in order of first appearance, so variants look the same."""
    lits = sorted(dict.fromkeys(lits), key=lambda l: (l[0], show(blank(l[1]))))   # stable: ties keep input order
    order = []
    for _, a in lits:
        for v in vars_in(a, []):
            if v not in order:
                order.append(v)
    m = {v: f"?v{i}" for i, v in enumerate(order)}
    out = []
    for s, a in lits:
        lit = (s, rename_term(a, m))
        if lit not in out:
            out.append(lit)
    return tuple(out)


def apart(c, tag):
    vs = sorted({v for _, a in c for v in vars_in(a, [])})
    m = {v: f"{v}'{tag}" for v in vs}
    return tuple((s, rename_term(a, m)) for s, a in c)


def tautology(c):
    return any((not s, a) in c for s, a in c)


def resolvents(c1, c2):
    c2 = apart(c2, "r")
    for i, (s1, a1) in enumerate(c1):
        for j, (s2, a2) in enumerate(c2):
            if s1 != s2 and a1[0] == a2[0]:
                th = unify(a1, a2)
                if th is not None:
                    rest = [l for k, l in enumerate(c1) if k != i] + [l for k, l in enumerate(c2) if k != j]
                    yield canonical([(s, substitute(a, th)) for s, a in rest])


def factors(c):
    for i in range(len(c)):
        for j in range(i + 1, len(c)):
            if c[i][0] == c[j][0]:
                th = unify(c[i][1], c[j][1])
                if th is not None:
                    yield canonical([(s, substitute(a, th)) for s, a in c])


def prove(clauses, factoring=True, max_clauses=2000, answer=False, quiet=False):
    """Given-clause loop. Returns (proof list or None, number of clauses kept, saturated?)."""
    why = {}
    unprocessed = []
    for c in clauses:
        c = canonical(c)
        if c not in why:
            why[c] = ("input",)
            unprocessed.append(c)
    processed = []

    def is_goal(c):
        return len(c) == 0 or (answer and all(a[0] == "Answer" for _, a in c))

    while unprocessed:
        unprocessed.sort(key=len)                 # smallest clause first: the "unit preference" idea
        given = unprocessed.pop(0)
        if is_goal(given):
            return trace_proof(given, why), len(why), False
        processed.append(given)
        new = []
        for other in processed:
            for r in resolvents(given, other):
                new.append((r, ("resolve", given, other)))
        if factoring:
            for r in factors(given):
                new.append((r, ("factor", given)))
        for r, reason in new:
            if r not in why and not tautology(r):
                why[r] = reason
                unprocessed.append(r)
                if is_goal(r):
                    return trace_proof(r, why), len(why), False
        if len(why) > max_clauses:
            return None, len(why), False
    return None, len(why), True


def trace_proof(goal, why):
    seen, order = set(), []

    def visit(c):
        if c in seen:
            return
        seen.add(c)
        for p in why[c][1:]:
            visit(p)
        order.append(c)
    visit(goal)
    num = {c: i + 1 for i, c in enumerate(order)}
    lines = []
    for c in order:
        r = why[c]
        how = "given" if r[0] == "input" else (f"resolve {num[r[1]]}, {num[r[2]]}" if r[0] == "resolve"
                                              else f"factor {num[r[1]]}")
        lines.append(f"  {num[c]:2d}. {cshow(c):<44} {how}")
    return lines


def F(text):
    """Small formula parser: 'all x (Rover(x) => ex y (Camera(y) & Has(x, y)))'. Binary ops need parentheses."""
    toks = text.replace("(", " ( ").replace(")", " ) ").replace(",", " , ").split()
    pos = 0

    def atom():
        nonlocal pos
        depth, start = 0, pos
        while True:
            t = toks[pos]; pos += 1
            depth += t == "("
            depth -= t == ")"
            if depth == 0 and (pos >= len(toks) or toks[pos] != "("):
                break
        return term("".join(toks[start:pos]))

    def unit():
        nonlocal pos
        t = toks[pos]
        if t in ("all", "ex"):
            pos += 2
            return (t, "?" + toks[pos - 1], unit())
        if t == "~":
            pos += 1
            return ("~", unit())
        if t == "(":
            pos += 1
            a = unit()
            if toks[pos] == ")":
                pos += 1
                return a
            op = toks[pos]; pos += 1
            b = unit()
            pos += 1                                   # ')'
            return (op, a, b)
        return atom()

    return unit()


if __name__ == "__main__":
    print("1. Clausal form, step by step")
    f1 = F("all x (Rover(x) => ex y (Camera(y) & Has(x, y)))")
    to_clauses(f1, verbose=True)
    print()
    skolem_names = count(1)
    f2 = F("~ all x (ex y Link(x, y) => all z Visits(z, x))")
    to_clauses(f2, verbose=True)
    print()

    print("2. Proofs by refutation")
    problems = {
        "a rover with a camera can see": (
            ["all x (Rover(x) => ex y (Camera(y) & Has(x, y)))",
             "all x all y ((Camera(y) & Has(x, y)) => CanSee(x))",
             "Rover(Percy)"],
            "CanSee(Percy)"),
        "two links make a two-step route": (
            ["all x ex y Link(x, y)",
             "all x all y all z ((Link(x, y) & Link(y, z)) => Link2(x, z))"],
            "all x ex z Link2(x, z)"),
    }
    for name, (kb, goal) in problems.items():
        skolem_names = count(1)                  # fresh Skolem names for each problem
        clauses = []
        for s in kb:
            clauses += to_clauses(F(s))
        clauses += to_clauses(("~", F(goal)))
        proof, kept, sat = prove(clauses)
        print(f"  {name}: prove {goal}   ({kept} clauses generated)")
        print("\n".join(proof))
        print()

    print("3. Factoring")
    cl = [[(True, term("P(x)")), (True, term("P(y)"))], [(False, term("P(u)")), (False, term("P(v)"))]]
    for fac in (False, True):
        proof, kept, sat = prove(cl, factoring=fac)
        if proof is None:
            print(f"  factoring={fac}: no proof; saturated={sat} with {kept} distinct clauses")
        else:
            print(f"  factoring={fac}: proof found")
            print("\n".join(proof))
    print()

    print("4. Answer extraction: who is a grandchild of Ada?")
    kb = ["Parent(Ada, Ben)", "Parent(Ben, Dan)", "Parent(Ada, Cleo)", "Parent(Cleo, Eve)",
          "all x all y all z ((Parent(x, y) & Parent(y, z)) => Grandparent(x, z))"]
    clauses = []
    for s in kb:
        clauses += to_clauses(F(s))
    clauses.append([(False, term("Grandparent(Ada, w)")), (True, term("Answer(w)"))])
    proof, kept, sat = prove(clauses, answer=True)
    print("\n".join(proof))
