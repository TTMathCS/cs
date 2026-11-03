# Chapter 9: unification (Robinson 1965) from scratch.
# A term is a variable (a string that starts with '?', like '?x'), a constant (any other string, like 'John'),
# or a compound term: a tuple whose first item is the function or predicate name, e.g. ('Knows', 'John', '?x').
# 1. unify() returns the most general unifier (a dict) or None, with an optional step-by-step trace.
# 2. A table of examples, including the occurs check.
# 3. Composition of substitutions, and a check that the result really makes the two sides equal.
# 4. Why the printed unifier can be exponentially long, and why shared terms keep the work small.


def is_var(t):
    return isinstance(t, str) and t.startswith("?")


def show(t):
    """Print a term the way the chapter writes it: Knows(John, x)."""
    if is_var(t):
        return t[1:]
    if isinstance(t, str):
        return t
    return f"{t[0]}({', '.join(show(a) for a in t[1:])})"


def show_sub(s):
    if s is None:
        return "fail"
    return "{" + ", ".join(f"{k[1:]}/{show(v)}" for k, v in s.items()) + "}"


def walk(t, s):
    """Follow variable bindings until reaching a non-variable or an unbound variable."""
    while is_var(t) and t in s:
        t = s[t]
    return t


def substitute(t, s):
    """Apply substitution s to term t completely (following chains of bindings)."""
    t = walk(t, s)
    if isinstance(t, tuple):
        return (t[0],) + tuple(substitute(a, s) for a in t[1:])
    return t


def occurs(v, t, s, seen=None):
    """Does variable v occur in t (after following s)? 'seen' remembers variables already searched,
    so shared subterms are searched once: without it this check alone can take exponential time."""
    seen = set() if seen is None else seen
    if is_var(t):
        if t == v:
            return True
        if t in seen or t not in s:
            return False
        seen.add(t)
        return occurs(v, s[t], s, seen)
    if isinstance(t, tuple):
        return any(occurs(v, a, s, seen) for a in t[1:])
    return False


def unify(x, y, s=None, trace=None, occurs_check=True):
    """Most general unifier of x and y extending s, or None. Iterative, with a stack of pairs to solve."""
    s = {} if s is None else dict(s)
    stack = [(x, y)]
    while stack:
        a, b = stack.pop()
        a, b = walk(a, s), walk(b, s)
        if trace is not None:
            trace.append(f"  solve {show(a)} = {show(b)}")
        if a == b:
            continue
        if is_var(a) or is_var(b):
            v, t = (a, b) if is_var(a) else (b, a)
            if occurs_check and occurs(v, t, s):
                if trace is not None:
                    trace.append(f"  occurs check: {show(v)} appears inside {show(substitute(t, s))} -> fail")
                return None
            s[v] = t
            if trace is not None:
                trace.append(f"  bind {show(v)} -> {show(t)}")
            continue
        if isinstance(a, tuple) and isinstance(b, tuple) and a[0] == b[0] and len(a) == len(b):
            for p, q in reversed(list(zip(a[1:], b[1:]))):   # reversed so the leftmost pair is solved first
                stack.append((p, q))
            continue
        if trace is not None:
            trace.append(f"  clash: {show(a)} vs {show(b)} -> fail")
        return None
    return s


def resolved(s):
    """Write the unifier in solved form: every right side fully substituted."""
    return None if s is None else {k: substitute(v, s) for k, v in s.items()}


def term(text):
    """Tiny parser: 'Knows(John, x)'. Lower-case names are variables, others are constants or functions."""
    text = text.replace(" ", "")
    pos = 0

    def parse():
        nonlocal pos
        start = pos
        while pos < len(text) and (text[pos].isalnum() or text[pos] == "_"):
            pos += 1
        name = text[start:pos]
        if pos < len(text) and text[pos] == "(":
            pos += 1
            args = [parse()]
            while text[pos] == ",":
                pos += 1
                args.append(parse())
            pos += 1                                       # the ')'
            return (name,) + tuple(args)
        return "?" + name if name[0].islower() else name

    return parse()


if __name__ == "__main__":
    print("1. A traced unification")
    a, b = term("Knows(John, x, Mother(x))"), term("Knows(y, Jane, z)")
    tr = []
    s = unify(a, b, trace=tr)
    print(f"unify {show(a)} with {show(b)}")
    print("\n".join(tr))
    print("result", show_sub(resolved(s)))
    print()

    print("2. Examples")
    examples = [
        ("Knows(John, x)", "Knows(John, Jane)"),
        ("Knows(John, x)", "Knows(y, Bill)"),
        ("Knows(John, x)", "Knows(y, Mother(y))"),
        ("Knows(John, x)", "Knows(x, Elizabeth)"),
        ("Knows(John, x)", "Knows(z, Elizabeth)"),
        ("P(x, x)", "P(f(y), f(A))"),
        ("P(x, f(x))", "P(y, y)"),
        ("P(f(x), g(y))", "P(f(g(z)), z)"),
        ("Q(x, y, z)", "Q(y, z, A)"),
        ("Q(A, B)", "Q(x, x)"),
    ]
    for p, q in examples:
        s = resolved(unify(term(p), term(q)))
        print(f"  {p:<22} {q:<22} {show_sub(s)}")
    print()

    print("3. Check: applying each unifier makes both sides identical")
    ok = 0
    for p, q in examples:
        s = unify(term(p), term(q))
        if s is not None:
            assert substitute(term(p), s) == substitute(term(q), s)
            ok += 1
    print(f"  {ok} unifiers checked")
    no_oc = unify(term("P(x, f(x))"), term("P(y, y)"), occurs_check=False)
    print("  without the occurs check, P(x, f(x)) = P(y, y) 'succeeds' with", show_sub(no_oc),
          "(a cyclic binding: y = f(y))")
    # Most general: any other unifier is an instance of the MGU.
    other = {"?y": "John", "?x": ("Mother", "John"), "?z": "John"}
    p, q = term("Knows(y, x)"), term("Knows(z, Mother(y))")
    mgu = unify(p, q)
    print(f"  MGU of {show(p)} and {show(q)}: {show_sub(resolved(mgu))}")
    print(f"  another unifier {show_sub(other)} = MGU followed by {{z/John}}:",
          all(substitute(substitute(v, mgu), {"?z": "John"}) == substitute(v, other)
              for v in ["?x", "?y", "?z"]))
    print()

    print("4. Exponential output, small work")
    print("  n  pairs solved  printed size of x_n")
    for n in [2, 4, 8, 16, 24]:
        left = ("P",) + tuple(f"?x{i}" for i in range(1, n + 1))
        right = ("P",) + tuple(("f", f"?x{i-1}", f"?x{i-1}") for i in range(1, n + 1))
        tr = []
        s = unify(left, right, trace=tr)
        solved = sum(1 for line in tr if line.startswith("  solve"))

        def size(t):    # number of symbols when written out in full, computed without building the term
            memo = {}

            def sz(u):
                u = walk(u, s)
                if isinstance(u, tuple):
                    key = id(u)
                    if key not in memo:
                        memo[key] = 1 + sum(sz(a) for a in u[1:])
                    return memo[key]
                return 1
            return sz(t)
        print(f"  {n:2d}  {solved:12d}  {size(f'?x{n}'):>12,d}")
