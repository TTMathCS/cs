# Chapter 11: default reasoning with stable models (answer sets), from scratch.
# A normal logic program has rules  head :- b1, ..., bn, not c1, ..., not cm.
# A set of atoms M is a STABLE MODEL (Gelfond and Lifschitz 1988) if M is the least model of the reduct P^M:
# delete every rule with some "not c" where c is in M, then delete the remaining "not" literals.
# We find all stable models of small ground programs by trying every subset of the atoms (fine for a dozen atoms).
from itertools import combinations


def ground(rules, constants):
    """Rules use the variable X; replace it by every constant."""
    out = []
    for head, pos, neg in rules:
        texts = [head] + pos + neg
        cs = constants if any("X" in t for t in texts) else [None]
        for c in cs:
            sub = (lambda t: t.replace("X", c)) if c else (lambda t: t)
            out.append((sub(head), [sub(p) for p in pos], [sub(n) for n in neg]))
    return out


def least_model(definite):
    m, changed = set(), True
    while changed:
        changed = False
        for head, pos in definite:
            if head not in m and all(p in m for p in pos):
                m.add(head)
                changed = True
    return m


def reduct(program, m):
    return [(h, pos) for h, pos, neg in program if not any(n in m for n in neg)]


def stable_models(program):
    atoms = sorted({h for h, _, _ in program} | {a for _, p, n in program for a in p + n})
    heads = sorted({h for h, _, _ in program})             # a stable model only contains atoms that are heads
    models = []
    for k in range(len(heads) + 1):
        for cand in combinations(heads, k):
            m = set(cand)
            if least_model(reduct(program, m)) == m:
                models.append(sorted(m))
    return models


def parse(text):
    """'Flies(X) :- Bird(X), not Ab(X)'"""
    if ":-" not in text:
        return (text.strip(), [], [])
    h, body = text.split(":-")
    pos, neg = [], []
    for lit in body.split(","):
        lit = lit.strip()
        (neg if lit.startswith("not ") else pos).append(lit[4:] if lit.startswith("not ") else lit)
    return (h.strip(), pos, neg)


def report(name, rules, constants, query=None):
    prog = ground([parse(r) for r in rules], constants)
    models = stable_models(prog)
    print(f"  {name}: {len(models)} stable model(s)")
    for m in models:
        print("    {" + ", ".join(m) + "}")
    if query and models:
        cred = any(query in m for m in models)
        skep = all(query in m for m in models)
        print(f"    {query}: credulously {'yes' if cred else 'no'}, skeptically {'yes' if skep else 'no'}")


if __name__ == "__main__":
    birds = ["Flies(X) :- Bird(X), not Ab(X)",        # a default: birds fly unless known to be abnormal
             "Ab(X) :- Penguin(X)",
             "Bird(X) :- Penguin(X)",
             "Bird(Tweety)"]
    print("1. Birds fly by default")
    report("Tweety is a bird", birds, ["Tweety", "Opus"], "Flies(Tweety)")
    report("... and we learn that Tweety is a penguin", birds + ["Penguin(Tweety)"], ["Tweety", "Opus"],
           "Flies(Tweety)")
    print("  adding a fact removed a conclusion: the reasoning is non-monotonic")
    print()
    print("2. The Nixon diamond: two conflicting defaults")
    nixon = ["Pacifist(X) :- Quaker(X), not NonPacifist(X)",
             "NonPacifist(X) :- Republican(X), not Pacifist(X)",
             "Quaker(Nixon)", "Republican(Nixon)"]
    report("Nixon", nixon, ["Nixon"], "Pacifist(Nixon)")
    print()
    print("3. Programs with no stable model, and negation as failure")
    report("p :- not p", ["P :- not P"], [])
    report("closed world: a timetable", ["Train(Ten)", "Train(Noon)", "NoTrain(X) :- not Train(X)"],
           ["Ten", "Noon", "Three"], "NoTrain(Three)")
    print()
    print("4. Choosing: each site is visited or skipped, at least one rock site must be visited")
    choice = ["Visit(X) :- Site(X), not Skip(X)", "Skip(X) :- Site(X), not Visit(X)",
              "Site(Delta)", "Site(Ridge)", "Rock(Delta)", "Rock(Ridge)",
              "Good :- Visit(X), Rock(X)", "Bad :- not Good, not Bad"]   # the last rule kills models without Good
    prog = ground([parse(r) for r in choice], ["Delta", "Ridge"])
    for m in stable_models(prog):
        print("    visit: " + ", ".join(a[6:-1] for a in m if a.startswith("Visit(")))
