# Chapter 9: forward chaining and backward chaining over first-order definite clauses.
# Uses unify/substitute from ch09_unify.py (same folder).
# 1. Forward chaining (semi-naive: each round uses at least one fact that is new since the last round) on a
#    family knowledge base, printing the facts each round adds, until a fixed point.
# 2. Forward chaining with a function symbol never reaches a fixed point: Nat(Zero), Nat(x) => Nat(S(x)).
# 3. Backward chaining, depth first and left to right, as Prolog does it: append/3 run "backwards",
#    and a left-recursive rule that loops forever (caught by a depth limit).
from itertools import count
from ch09_unify import is_var, show, show_sub, substitute, term, unify

# ---------------------------------------------------------------- forward chaining
def rule(text):
    """'Parent(x, y) & Parent(y, z) => Grandparent(x, z)' -> ([premises], conclusion)."""
    left, right = text.split("=>")
    return [term(p) for p in left.split("&")], term(right)


def match_all(premises, facts, new, s, used_new):
    """All substitutions that make every premise a known fact; at least one premise must use a new fact."""
    if not premises:
        if used_new:
            yield s
        return
    first, rest = premises[0], premises[1:]
    for f in facts:
        s2 = unify(first, f, s)
        if s2 is not None:
            yield from match_all(rest, facts, new, s2, used_new or f in new)


def forward_chain(facts, rules, max_rounds=50, quiet=False):
    facts = set(facts)
    new = set(facts)
    for rnd in count(1):
        if rnd > max_rounds:
            return facts, rnd - 1, False
        added = set()
        for premises, concl in rules:
            for s in match_all(premises, sorted(facts, key=show), new, {}, False):
                c = substitute(concl, s)
                if c not in facts and c not in added:
                    added.add(c)
        if not added:
            return facts, rnd - 1, True
        if not quiet:
            shown = sorted(show(a) for a in added)
            print(f"  round {rnd}: +{len(added)}  " + ", ".join(shown[:6]) + (" ..." if len(shown) > 6 else ""))
        facts |= added
        new = added


# ---------------------------------------------------------------- backward chaining (a tiny Prolog)
fresh = count()


def rename(clause):
    """Standardize apart: give the clause's variables new names before each use."""
    head, body = clause
    n = next(fresh)
    mapping = {}

    def r(t):
        if is_var(t):
            mapping.setdefault(t, f"{t}_{n}")
            return mapping[t]
        if isinstance(t, tuple):
            return (t[0],) + tuple(r(a) for a in t[1:])
        return t
    return r(head), [r(b) for b in body]


calls = 0


def solve(goals, program, s, depth, limit):
    """Yield every substitution that proves all goals (SLD resolution, depth first, left to right)."""
    global calls
    if not goals:
        yield s
        return
    if depth > limit:
        raise RecursionError(f"depth limit {limit} reached")
    goal, rest = goals[0], goals[1:]
    for clause in program:
        if clause[0][0] != goal[0]:
            continue
        head, body = rename(clause)
        calls += 1
        s2 = unify(goal, head, s)
        if s2 is not None:
            yield from solve(body + rest, program, s2, depth + 1, limit)


def ask(query, program, limit=60, max_answers=10):
    goals = [term(g) for g in query.split("&")]
    qvars = sorted({v for g in goals for v in vars_of(g)})
    answers = []
    for s in solve(goals, program, {}, 0, limit):
        answers.append({v: substitute(v, s) for v in qvars})
        if len(answers) == max_answers:
            break
    return answers


def vars_of(t):
    if is_var(t):
        return {t}
    if isinstance(t, tuple):
        return set().union(*[vars_of(a) for a in t[1:]])
    return set()


def clause(text):
    if ":-" in text:
        h, b = text.split(":-")
        return term(h), [term(g) for g in b.split("&")]
    return term(text), []


def plist(items):
    t = "Nil"
    for x in reversed(items):
        t = ("Cons", x, t)
    return t


def show_list(t):
    out = []
    while isinstance(t, tuple) and t[0] == "Cons":
        out.append(show(t[1]))
        t = t[2]
    return "[" + ", ".join(out) + "]" + ("" if t == "Nil" else f" | {show(t)}")


if __name__ == "__main__":
    print("1. Forward chaining on a family tree")
    people = [("Ada", "Ben"), ("Ada", "Cleo"), ("Ben", "Dan"), ("Cleo", "Eve"), ("Dan", "Finn")]
    facts = {("Parent", a, b) for a, b in people}
    rules = [rule("Parent(x, y) => Ancestor(x, y)"),
             rule("Parent(x, y) & Ancestor(y, z) => Ancestor(x, z)"),
             rule("Parent(x, y) & Parent(y, z) => Grandparent(x, z)"),
             rule("Parent(p, x) & Parent(p, y) & Different(x, y) => Sibling(x, y)")]
    names = sorted({p for pair in people for p in pair})
    facts |= {("Different", a, b) for a in names for b in names if a != b}
    start = len(facts)
    kb, rounds, fixed = forward_chain(facts, rules)
    print(f"  fixed point after {rounds} rounds: {start} facts -> {len(kb)} facts")
    anc = sorted(show(f) for f in kb if f[0] == "Ancestor" and f[1] == "Ada")
    print("  ", ", ".join(anc))
    print()

    print("2. A function symbol: no fixed point")
    kb, rounds, fixed = forward_chain({("Nat", "Zero")}, [rule("Nat(x) => Nat(S(x))")], max_rounds=5)
    print(f"  stopped by the round limit: fixed point reached = {fixed}; {len(kb)} facts")
    print(f"  Nat(S(S(Zero))) proved: {term('Nat(S(S(Zero)))') in kb};  Nat(Banana) proved: {('Nat', 'Banana') in kb}")
    print()

    print("3. Backward chaining (a tiny Prolog)")
    append = [clause("Append(Nil, l, l)"),
              clause("Append(Cons(h, t), l, Cons(h, r)) :- Append(t, l, r)")]
    q = ("Append", "?x", "?y", plist(["1", "2", "3"]))
    sols = [{"?x": substitute("?x", s), "?y": substitute("?y", s)} for s in solve([q], append, {}, 0, 60)]
    print("  ?- Append(x, y, [1, 2, 3]).")
    for a in sols:
        print(f"     x = {show_list(a['?x']):<10} y = {show_list(a['?y'])}")
    q = ("Append", plist(["1", "2"]), plist(["3"]), "?z")
    z = substitute("?z", next(solve([q], append, {}, 0, 60)))
    print(f"  ?- Append([1, 2], [3], z).   z = {show_list(z)}")
    print()

    links = [("Gale", "Elysium"), ("Elysium", "Jezero"), ("Jezero", "Isidis"), ("Isidis", "Elysium")]
    facts_l = [((("Link",) + l), []) for l in links]
    right = facts_l + [clause("Path(x, y) :- Link(x, y)"), clause("Path(x, z) :- Link(x, y) & Path(y, z)")]
    left = facts_l + [clause("Path(x, y) :- Link(x, y)"), clause("Path(x, z) :- Path(x, y) & Link(y, z)")]
    for name, prog in [("right-recursive", right), ("left-recursive", left)]:
        calls = 0
        got = []
        try:
            for s in solve([term("Path(Gale, w)")], prog, {}, 0, 40):
                got.append(show(substitute("?w", s)))
                if len(got) == 6:
                    break
            print(f"  {name}: first answers {got} ({calls} clause tries)")
        except RecursionError as e:
            print(f"  {name}: answers {got}, then {e} ({calls} clause tries)")
    calls = 0
    try:
        got = [show(substitute("?w", s)) for s in solve([term("Path(Jezero, Gale)")], left, {}, 0, 40)]
        print("  left-recursive, Path(Jezero, Gale):", got)
    except RecursionError as e:
        print(f"  left-recursive, Path(Jezero, Gale): no answer, {e} ({calls} clause tries)")
    calls = 0
    try:
        got = list(solve([term("Path(Jezero, Gale)")], right, {}, 0, 40))
        print("  right-recursive, Path(Jezero, Gale):", got)
    except RecursionError as e:
        print(f"  right-recursive, Path(Jezero, Gale): no answer, {e} ({calls} clause tries)")
    print("  forward chaining on the same links reaches a fixed point:")
    kb, rounds, fixed = forward_chain({("Link",) + l for l in links},
                                      [rule("Link(x, y) => Path(x, y)"),
                                       rule("Link(x, y) & Path(y, z) => Path(x, z)")], quiet=True)
    paths = sorted(show(f) for f in kb if f[0] == "Path" and f[1] == "Gale")
    print(f"  {rounds} rounds, fixed point {fixed}; from Gale: {', '.join(paths)}")
    print(f"  Path(Jezero, Gale) in the fixed point: {('Path', 'Jezero', 'Gale') in kb}")
