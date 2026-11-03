# Chapter 21: checking a proof is easy, finding one is hard.
# A tiny proof checker for propositional logic in Hilbert style (implication only):
#   A1: A -> (B -> A)      A2: (A -> (B -> C)) -> ((A -> B) -> (A -> C))      rule: modus ponens
# This is the kind of kernel that proof assistants such as Lean, Coq (Rocq) and Isabelle trust:
# small, simple, and checking every step.
import itertools
import time


def imp(a, b):
    return ("->", a, b)


def show(f):
    return f if isinstance(f, str) else f"({show(f[1])} -> {show(f[2])})"


def match(pat, f, env):
    """Does formula f fit the schema pat (metavariables are 'A', 'B', 'C')? Extends env consistently."""
    if pat in ("A", "B", "C"):
        if pat in env:
            return env[pat] == f
        env[pat] = f
        return True
    if isinstance(pat, str) or isinstance(f, str):
        return pat == f
    return match(pat[1], f[1], env) and match(pat[2], f[2], env)


AXIOMS = {"A1": imp("A", imp("B", "A")),
          "A2": imp(imp("A", imp("B", "C")), imp(imp("A", "B"), imp("A", "C")))}


def check(proof, goal):
    """proof: list of (formula, justification); justification is 'A1', 'A2' or ('MP', i, j) meaning
    line i is X and line j is X -> formula (lines numbered from 1). Returns (ok, message)."""
    for n, (f, why) in enumerate(proof, 1):
        if why in AXIOMS:
            if not match(AXIOMS[why], f, {}):
                return False, f"line {n} is not an instance of {why}"
        else:
            _, i, j = why
            if not (i < n and j < n):
                return False, f"line {n} cites a later line"
            if proof[j - 1][0] != imp(proof[i - 1][0], f):
                return False, f"line {n}: line {j} is not (line {i}) -> (line {n})"
    if proof[-1][0] != goal:
        return False, "the last line is not the goal"
    return True, "proof accepted"


p = "p"
pp = imp(p, p)
proof = [(imp(imp(p, imp(pp, p)), imp(imp(p, pp), pp)), "A2"),
         (imp(p, imp(pp, p)), "A1"),
         (imp(imp(p, pp), pp), ("MP", 2, 1)),
         (imp(p, pp), "A1"),
         (pp, ("MP", 4, 3))]
print("A proof of p -> p:")
for n, (f, why) in enumerate(proof, 1):
    print(f"   {n}. {show(f):<48} {why if isinstance(why, str) else 'MP from %d and %d' % why[1:]}")
t = time.perf_counter()
print("   checker:", check(proof, pp)[1], f"({(time.perf_counter() - t) * 1e6:.0f} microseconds)")

bad = proof[:2] + [(imp(imp(p, pp), pp), ("MP", 1, 2))] + proof[3:]
print("Same proof with lines 1 and 2 swapped in the citation of line 3:", check(bad, pp)[1])
bad2 = [(imp(p, imp(p, p)), "A1"), (pp, "A2")]
print("A 'proof' that calls p -> p an instance of A2:", check(bad2, pp)[1])

# Blind search: instantiate the axioms with every formula up to a given size, close under modus
# ponens round by round, and count the theorems produced before the goal appears.
def formulas(size, atoms):
    if size == 1:
        return list(atoms)
    return [imp(a, b) for k in range(1, size - 1)
            for a in formulas(k, atoms) for b in formulas(size - 1 - k, atoms)]


def blind_search(goal, atoms, sizes, max_rounds=3, cap=300000):
    terms = [f for s in sizes for f in formulas(s, atoms)]
    known = {imp(A, imp(B, A)) for A, B in itertools.product(terms, repeat=2)}
    known |= {imp(imp(A, imp(B, C)), imp(imp(A, B), imp(A, C))) for A, B, C in itertools.product(terms, repeat=3)}
    print(f"   {len(terms)} building blocks, {len(known)} axiom instances")
    for r in range(1, max_rounds + 1):
        if goal in known:
            break
        known |= {f[2] for f in known if not isinstance(f, str) and f[1] in known}
        print(f"   after round {r} of modus ponens: {len(known)} theorems; goal found: {goal in known}")
        if len(known) > cap:
            print("   stopped: too many theorems")
            break
    return goal in known


t = time.perf_counter()
print("\nBlind search for p -> p (building blocks: formulas in p of size 1, 3, 5):")
blind_search(pp, "p", (1, 3, 5))
q, r = "q", "r"
syll = imp(imp(p, q), imp(imp(q, r), imp(p, r)))
print(f"Blind search for {show(syll)} (building blocks: formulas in p, q, r of size 1 and 3):")
blind_search(syll, "pqr", (1, 3))
print("The same with building blocks of size 1, 3 and 5:")
blind_search(syll, "pqr", (1, 3, 5), max_rounds=4, cap=2000000)
print(f"({time.perf_counter() - t:.1f} s)")
