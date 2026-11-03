# Chapter 11: a tableau reasoner for the description logic ALC, from scratch.
# Concepts: an atomic name 'Rock', 'TOP', 'BOTTOM', ('not', C), ('and', C, D), ('or', C, D),
# ('some', R, C) meaning ∃R.C, and ('all', R, C) meaning ∀R.C.
# A TBox is a list of inclusions C ⊑ D. The reasoner decides whether a concept is satisfiable with respect to the
# TBox; subsumption C ⊑ D is checked as unsatisfiability of C ⊓ ¬D. General (even cyclic) TBoxes are handled by
# adding ¬C ⊔ D to every node and stopping with subset blocking.


def nnf(c):
    """Negation normal form: negation only in front of atomic names."""
    if isinstance(c, str):
        return c
    op = c[0]
    if op == "not":
        d = c[1]
        if isinstance(d, str):
            return {"TOP": "BOTTOM", "BOTTOM": "TOP"}.get(d, ("not", d))
        if d[0] == "not":
            return nnf(d[1])
        if d[0] == "and":
            return ("or", nnf(("not", d[1])), nnf(("not", d[2])))
        if d[0] == "or":
            return ("and", nnf(("not", d[1])), nnf(("not", d[2])))
        if d[0] == "some":
            return ("all", d[1], nnf(("not", d[2])))
        return ("some", d[1], nnf(("not", d[2])))      # ¬∀R.C = ∃R.¬C
    if op in ("and", "or"):
        return (op, nnf(c[1]), nnf(c[2]))
    return (op, c[1], nnf(c[2]))


def show(c):
    if isinstance(c, str):
        return {"TOP": "⊤", "BOTTOM": "⊥"}.get(c, c)
    op = c[0]
    if op == "not":
        return "¬" + show(c[1])
    if op in ("and", "or"):
        return "(" + show(c[1]) + (" ⊓ " if op == "and" else " ⊔ ") + show(c[2]) + ")"
    return ("∃" if op == "some" else "∀") + c[1] + "." + show(c[2])


def AND(*cs):
    out = cs[-1]
    for c in reversed(cs[:-1]):
        out = ("and", c, out)
    return out


class Reasoner:
    """lazy=True treats inclusions with an atomic left side (A ⊑ D) by lazy unfolding: add D to a node only when A is
    in its label. Only the remaining inclusions are added, as ¬C ⊔ D, to every node. lazy=False adds them all."""

    def __init__(self, tbox, lazy=True):
        self.unfold = {}
        general = []
        for c, d in tbox:
            if lazy and isinstance(c, str):
                self.unfold.setdefault(c, []).append(nnf(d))
            else:
                general.append(nnf(("or", ("not", c), d)))      # C ⊑ D  becomes  ¬C ⊔ D, true everywhere
        self.general = general
        self.nodes = 0

    def clash(self, L):
        return "BOTTOM" in L or any(("not", a) in L for a in L if isinstance(a, str))

    def sat(self, L, ancestors):
        """Return a model (a tree of nodes) for the concepts in L, or None if they are unsatisfiable."""
        L = set(L) | set(self.general)
        self.nodes += 1
        while True:                                       # ⊓-rule and unfolding, to a fixed point
            new = {x for c in L if not isinstance(c, str) and c[0] == "and" for x in c[1:]}
            new |= {d for c in L if isinstance(c, str) for d in self.unfold.get(c, [])}
            new -= L
            if not new:
                break
            L |= new
        if self.clash(L):
            return None
        for c in sorted(L, key=show):                      # ⊔-rule: branch, and backtrack if the branch fails
            if not isinstance(c, str) and c[0] == "or" and c[1] not in L and c[2] not in L:
                for d in (c[1], c[2]):
                    m = self.sat(L | {d}, ancestors)
                    if m is not None:
                        return m
                return None
        atoms = sorted(show(x) for x in L if isinstance(x, str) or x[0] == "not")
        if any(L <= A for A in ancestors):                 # blocked: the node can copy an ancestor (a cycle)
            return {"atoms": atoms, "children": [], "blocked": True}
        children = []
        for c in sorted(L, key=show):                      # ∃-rule, with the ∀-rule feeding each new successor
            if not isinstance(c, str) and c[0] == "some":
                r = c[1]
                child = {c[2]} | {d[2] for d in L if not isinstance(d, str) and d[0] == "all" and d[1] == r}
                m = self.sat(child, ancestors + [frozenset(L)])
                if m is None:
                    return None
                children.append((r, m))
        return {"atoms": atoms, "children": children, "blocked": False}

    def satisfiable(self, c):
        self.nodes = 0
        self.last_model = self.sat({nnf(c)}, [])
        return self.last_model is not None

    def subsumes(self, c, d):
        """Does C ⊑ D follow from the TBox?  Yes iff C ⊓ ¬D is unsatisfiable."""
        return not self.satisfiable(("and", c, ("not", d)))


def print_model(m, depth=0, via=None):
    pad = "  " + "    " * depth
    head = f"--{via}--> " if via else ""
    print(pad + head + (", ".join(m["atoms"]) or "(no atoms)") + ("   [blocked]" if m["blocked"] else ""))
    for r, child in m["children"]:
        print_model(child, depth + 1, r)


if __name__ == "__main__":
    tbox = [
        ("Mudstone", "SedimentaryRock"),
        ("Basalt", "IgneousRock"),
        ("SedimentaryRock", "Rock"),
        ("IgneousRock", "Rock"),
        (("and", "IgneousRock", "SedimentaryRock"), "BOTTOM"),          # disjoint classes
        ("LakeDeposit", AND("Rock", ("some", "formedIn", "Lake"))),     # LakeDeposit ≡ Rock ⊓ ∃formedIn.Lake
        (AND("Rock", ("some", "formedIn", "Lake")), "LakeDeposit"),
        ("Lake", ("some", "contains", "Water")),
        ("Site", ("some", "linkedTo", "Site")),                          # cyclic: every site links to a site
    ]
    R, naive = Reasoner(tbox), Reasoner(tbox, lazy=False)
    print("1. Subsumption and satisfiability with respect to the TBox (tableau nodes: lazy unfolding / naive)")
    queries = [
        ("subsumes", AND("Mudstone", ("some", "formedIn", "Lake")), "LakeDeposit"),
        ("subsumes", "LakeDeposit", ("some", "formedIn", ("some", "contains", "Water"))),
        ("subsumes", "LakeDeposit", "SedimentaryRock"),
        ("subsumes", AND(("all", "r", "A"), ("some", "r", "B")), ("some", "r", AND("A", "B"))),
        ("subsumes", ("some", "r", AND("A", "B")), AND(("some", "r", "A"), ("some", "r", "B"))),
        ("subsumes", AND(("some", "r", "A"), ("some", "r", "B")), ("some", "r", AND("A", "B"))),
        ("sat", AND("Basalt", "Mudstone"), None),
        ("sat", AND(("some", "r", "A"), ("all", "r", ("not", "A"))), None),
        ("sat", AND("Basalt", ("or", "Mudstone", ("some", "formedIn", "Lake"))), None),
        ("sat", "Site", None),
    ]
    for kind, c, d in queries:
        if kind == "subsumes":
            ans, ans2 = R.subsumes(c, d), naive.subsumes(c, d)
            text = f"{show(c)} ⊑ {show(d)} ?"
        else:
            ans, ans2 = R.satisfiable(c), naive.satisfiable(c)
            text = f"{show(c)} satisfiable?"
        assert ans == ans2
        print(f"  {text:<52} {'yes' if ans else 'no ':<4} ({R.nodes} / {naive.nodes} nodes)")
    print()
    print("2. The model found for Basalt ⊓ (Mudstone ⊔ ∃formedIn.Lake)")
    R.satisfiable(AND("Basalt", ("or", "Mudstone", ("some", "formedIn", "Lake"))))
    print_model(R.last_model)
    print()
    print("3. A counter-model: LakeDeposit ⊓ ¬SedimentaryRock is satisfiable, so LakeDeposit ⋢ SedimentaryRock")
    R.satisfiable(AND("LakeDeposit", ("not", "SedimentaryRock")))
    print_model(R.last_model)
    print()
    print("4. Blocking: Site is satisfiable although Site ⊑ ∃linkedTo.Site asks for an endless chain")
    R.satisfiable("Site")
    print_model(R.last_model)
