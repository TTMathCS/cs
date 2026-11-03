# Chapter 11: events, time and change.
# 1. Situation calculus with successor-state axioms (Reiter 1991): a fluent's truth in do(a, s) is defined from s,
#    so queries are answered by regression back to the initial situation S0. No frame axioms are written.
# 2. A discrete event calculus: a narrative of events at time points; a fluent holds if an earlier event initiated
#    it and nothing has terminated it since ("clipped") - the commonsense law of inertia.
# 3. Allen's interval algebra (1983): the 13 relations between two intervals, the composition table computed by
#    brute force, and path consistency on a small network.
from itertools import product

# ---------------------------------------------------------------- 1. situation calculus
INIT = {("At", "Base"), ("ArmStowed",)}


def holds(f, s):
    """Successor-state axioms. A situation is 'S0' or ('do', action, situation)."""
    if s == "S0":
        return f in INIT
    _, a, prev = s
    kind = f[0]
    if kind == "At":           # At(p, do(a,s)) <=> a = Drive(q,p) or (At(p,s) and a is not Drive(p,q) for any q)
        return (a[0] == "Drive" and a[2] == f[1]) or (holds(f, prev) and not (a[0] == "Drive" and a[1] == f[1]))
    if kind == "ArmStowed":    # ArmStowed(do(a,s)) <=> a = Stow or (ArmStowed(s) and a != Unstow)
        return a[0] == "Stow" or (holds(f, prev) and a[0] != "Unstow")
    if kind == "Sampled":      # Sampled(p, do(a,s)) <=> (a = Drill and At(p,s) and not ArmStowed(s)) or Sampled(p,s)
        return (a[0] == "Drill" and holds(("At", f[1]), prev) and not holds(("ArmStowed",), prev)) or holds(f, prev)
    raise ValueError(f)


def poss(a, s):
    """Precondition axioms: when is an action possible?"""
    if a[0] == "Drive":
        return holds(("At", a[1]), s) and holds(("ArmStowed",), s)    # never drive with the arm out
    if a[0] == "Drill":
        return not holds(("ArmStowed",), s)
    return True


def do_all(actions):
    s = "S0"
    for a in actions:
        if not poss(a, s):
            return s, a
        s = ("do", a, s)
    return s, None


def term_str(t):
    return t[0] + (f"({','.join(t[1:])})" if len(t) > 1 else "")


def sit_str(s):
    return "S0" if s == "S0" else f"do({term_str(s[1])}, {sit_str(s[2])})"


# ---------------------------------------------------------------- 2. event calculus
NARRATIVE = [(1, "HeaterOn"), (4, "DriveStart"), (6, "HeaterOff"), (9, "DriveStop"), (10, "SunSet"),
             (12, "HeaterOn"), (15, "SunRise")]
INITIATES = {"HeaterOn": ["Heating"], "DriveStart": ["Moving"], "SunRise": ["Daylight"], "SunSet": []}
TERMINATES = {"HeaterOff": ["Heating"], "DriveStop": ["Moving"], "SunSet": ["Daylight"]}
INITIALLY = {"Daylight"}


def clipped(t1, f, t2):
    return any(t1 < t < t2 and f in TERMINATES.get(e, []) for t, e in NARRATIVE)


def holds_at(f, t):
    if f in INITIALLY and not clipped(-1, f, t):
        return True
    return any(t1 < t and f in INITIATES.get(e, []) and not clipped(t1, f, t) for t1, e in NARRATIVE)


# ---------------------------------------------------------------- 3. Allen's interval algebra
RELS = ["before", "meets", "overlaps", "starts", "during", "finishes", "equals",
        "finished-by", "contains", "started-by", "overlapped-by", "met-by", "after"]


def relation(a, b):
    (a1, a2), (b1, b2) = a, b
    if a2 < b1: return "before"
    if a2 == b1: return "meets"
    if b2 < a1: return "after"
    if b2 == a1: return "met-by"
    if a1 == b1 and a2 == b2: return "equals"
    if a1 == b1: return "starts" if a2 < b2 else "started-by"
    if a2 == b2: return "finishes" if a1 > b1 else "finished-by"
    if b1 < a1 and a2 < b2: return "during"
    if a1 < b1 and b2 < a2: return "contains"
    return "overlaps" if a1 < b1 else "overlapped-by"


def intervals(n):
    return [(x, y) for x in range(n) for y in range(n) if x < y]


def composition_table(n=7):
    """For r1, r2: which relations can hold between A and C when A r1 B and B r2 C? (by enumerating endpoints)"""
    table = {}
    iv = intervals(n)
    for a, b, c in product(iv, iv, iv):
        table.setdefault((relation(a, b), relation(b, c)), set()).add(relation(a, c))
    return table


INVERSE = dict(zip(RELS, reversed(RELS)))


def path_consistency(net, names, table):
    """Allen's algorithm: tighten every constraint (i,k) with the composition of (i,j) and (j,k) until stable."""
    changed = True
    while changed:
        changed = False
        for i, j, k in product(names, repeat=3):
            if len({i, j, k}) < 3:
                continue
            comp = set().union(*[table[(r1, r2)] for r1 in net[i, j] for r2 in net[j, k]])
            new = net[i, k] & comp
            if new != net[i, k]:
                net[i, k] = new
                net[k, i] = {INVERSE[r] for r in new}
                changed = True
                if not new:
                    return False
    return True


if __name__ == "__main__":
    print("1. Situation calculus")
    plan = [("Drive", "Base", "Rim"), ("Unstow",), ("Drill",), ("Stow",), ("Drive", "Rim", "Delta")]
    s, refused = do_all(plan)
    print("  situation:", sit_str(s))
    for f in [("At", "Delta"), ("At", "Rim"), ("At", "Base"), ("Sampled", "Rim"), ("Sampled", "Delta"), ("ArmStowed",)]:
        print(f"  {term_str(f)} holds: {holds(f, s)}")
    s2, refused = do_all([("Drive", "Base", "Rim"), ("Unstow",), ("Drive", "Rim", "Delta")])
    print("  driving with the arm unstowed is refused by the precondition axiom:", term_str(refused), "in",
          sit_str(s2))
    print()

    print("2. Event calculus: which fluents hold at each time")
    fluents = ["Daylight", "Heating", "Moving"]
    print("   t  " + "  ".join(f"{f:<8}" for f in fluents) + "  events")
    for t in range(0, 17):
        ev = ", ".join(e for tt, e in NARRATIVE if tt == t)
        print(f"  {t:2d}  " + "  ".join(f"{'yes' if holds_at(f, t) else '.':<8}" for f in fluents) + f"  {ev}")
    print()

    print("3. Allen's interval algebra")
    table = composition_table()
    print(f"  composition table: {len(table)} entries (13 x 13)")
    for r1, r2 in [("before", "before"), ("meets", "meets"), ("during", "before"), ("overlaps", "overlaps"),
                   ("before", "after"), ("during", "contains")]:
        out = table[(r1, r2)]
        print(f"  {r1} ∘ {r2} = {sorted(out, key=RELS.index) if len(out) < 13 else 'any of the 13'}")
    # A network: Drive (D), Heating (H), Imaging (I), Downlink (L)
    names = ["D", "H", "I", "L"]
    ALL = set(RELS)
    net = {(i, j): set(ALL) for i in names for j in names if i != j}

    def constrain(i, j, rels):
        net[i, j] = set(rels)
        net[j, i] = {INVERSE[r] for r in rels}
    constrain("H", "D", ["overlaps", "meets"])         # heating starts before the drive and ends during it or as it starts
    constrain("I", "D", ["after", "met-by"])           # imaging after the drive
    constrain("L", "I", ["after", "met-by"])           # downlink after imaging
    ok = path_consistency(net, names, table)
    print("  network: H {overlaps, meets} D;  I {after, met-by} D;  L {after, met-by} I")
    print(f"  path consistent: {ok};  derived H-to-L: {sorted(net['H', 'L'], key=RELS.index)}")
    constrain("L", "H", ["during"])                    # now demand the downlink happen during the heating
    print("  adding L during H: path consistent =", path_consistency(net, names, table))
