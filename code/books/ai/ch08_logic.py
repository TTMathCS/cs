# Chapter 8: propositional logic from scratch: sentences, truth tables, entailment,
# conversion to CNF, and resolution, on a small wumpus-world knowledge base.
from itertools import product

# A sentence is a symbol (a string) or a tuple: ("not", s), ("and", s, t, ...), ("or", s, t, ...),
# ("implies", s, t), ("iff", s, t).


def symbols(s):
    if isinstance(s, str):
        return {s}
    return set().union(*(symbols(t) for t in s[1:]))


def holds(s, model):
    """Truth value of sentence s in a model (a dict symbol -> bool)."""
    if isinstance(s, str):
        return model[s]
    op, args = s[0], s[1:]
    if op == "not":
        return not holds(args[0], model)
    if op == "and":
        return all(holds(a, model) for a in args)
    if op == "or":
        return any(holds(a, model) for a in args)
    if op == "implies":
        return (not holds(args[0], model)) or holds(args[1], model)
    if op == "iff":
        return holds(args[0], model) == holds(args[1], model)
    raise ValueError(op)


def tt_entails(kb, alpha):
    """KB |= alpha iff alpha is true in every model of KB. Returns (answer, rows checked, models of KB)."""
    syms = sorted(symbols(kb) | symbols(alpha))
    rows, kb_models = 0, []
    for values in product((False, True), repeat=len(syms)):
        rows += 1
        m = dict(zip(syms, values))
        if holds(kb, m):
            kb_models.append(m)
            if not holds(alpha, m):
                return False, rows, kb_models
    return True, rows, kb_models


# ---- CNF conversion
def eliminate(s):
    """Remove iff and implies."""
    if isinstance(s, str):
        return s
    op, args = s[0], [eliminate(a) for a in s[1:]]
    if op == "iff":
        a, b = args
        return ("and", ("or", ("not", a), b), ("or", ("not", b), a))
    if op == "implies":
        a, b = args
        return ("or", ("not", a), b)
    return (op, *args)


def push_not(s):
    """Move negations inwards (De Morgan) until they sit on symbols: negation normal form."""
    if isinstance(s, str):
        return s
    op = s[0]
    if op == "not":
        a = s[1]
        if isinstance(a, str):
            return s
        if a[0] == "not":
            return push_not(a[1])
        if a[0] == "and":
            return ("or", *(push_not(("not", t)) for t in a[1:]))
        if a[0] == "or":
            return ("and", *(push_not(("not", t)) for t in a[1:]))
    return (op, *(push_not(t) for t in s[1:]))


def to_clauses(s):
    """Distribute or over and. A clause is a frozenset of literals; a literal is 'P' or '-P'."""
    if isinstance(s, str):
        return {frozenset([s])}
    if s[0] == "not":
        return {frozenset(["-" + s[1]])}
    if s[0] == "and":
        return set().union(*(to_clauses(t) for t in s[1:]))
    # "or": every combination of one clause from each disjunct
    parts = [to_clauses(t) for t in s[1:]]
    out = set()
    for combo in product(*parts):
        out.add(frozenset().union(*combo))
    return out


def tautology(c):
    return any(("-" + l) in c for l in c if not l.startswith("-"))


def cnf(s):
    return {c for c in to_clauses(push_not(eliminate(s))) if not tautology(c)}


def negate(lit):
    return lit[1:] if lit.startswith("-") else "-" + lit


def resolve(c1, c2):
    out = []
    for l in c1:
        if negate(l) in c2:
            r = (c1 - {l}) | (c2 - {negate(l)})
            if not tautology(r):
                out.append(frozenset(r))
    return out


def pl_resolution(kb_clauses, alpha):
    """Prove KB |= alpha by refutation: add the clauses of not alpha and look for the empty clause."""
    clauses = set(kb_clauses) | cnf(("not", alpha))
    steps = 0
    while True:
        new = set()
        cl = sorted(clauses, key=lambda c: (len(c), sorted(c)))
        for i in range(len(cl)):
            for j in range(i + 1, len(cl)):
                for r in resolve(cl[i], cl[j]):
                    steps += 1
                    if not r:
                        return True, steps, len(clauses)
                    new.add(r)
        if new <= clauses:
            return False, steps, len(clauses)            # nothing new: not entailed
        clauses |= new


def show(c):
    return "(" + " v ".join(sorted(c, key=lambda l: (l.lstrip("-"), l))) + ")" if c else "()"


# The wumpus world, squares [1,1] [1,2] [2,1]: no pit in [1,1]; a square is breezy iff a neighbour has a pit.
# The agent felt no breeze in [1,1] and a breeze in [2,1].
R1 = ("not", "P11")
R2 = ("iff", "B11", ("or", "P12", "P21"))
R3 = ("iff", "B21", ("or", "P11", "P22", "P31"))
R4 = ("not", "B11")
R5 = "B21"
KB = ("and", R1, R2, R3, R4, R5)

for alpha, name in ((("not", "P12"), "no pit in [1,2]"), (("not", "P22"), "no pit in [2,2]"),
                    (("or", "P22", "P31"), "a pit in [2,2] or [3,1]")):
    ans, rows, models = tt_entails(KB, alpha)
    print(f"KB |= {name:26s}? {str(ans):5s}  (truth-table rows checked: {rows})")
ans, rows, models = tt_entails(KB, "B21")        # B21 is in KB, so this walks the whole table
print(f"the table has {rows} rows over {len(symbols(KB))} symbols; KB is true in {len(models)} of them:")
for m in models:
    print("   ", {k: int(v) for k, v in sorted(m.items())})

print("\nCNF of R2 (B11 <=> P12 v P21):", "  ".join(show(c) for c in sorted(cnf(R2), key=sorted)))
kb_clauses = cnf(KB)
print("KB in CNF:", "  ".join(show(c) for c in sorted(kb_clauses, key=lambda c: (len(c), sorted(c)))))
for alpha, name in ((("not", "P12"), "no pit in [1,2]"), (("not", "P22"), "no pit in [2,2]")):
    ans, steps, size = pl_resolution(kb_clauses, alpha)
    print(f"resolution: KB |= {name}? {ans}  ({steps} resolvents computed, {size} clauses at the end)")
