# Chapter 11: categories, inheritance, frames and semantic networks.
# 1. A small taxonomy (an ontology fragment): subclass closure, disjointness checks, a partition test, part-of.
# 2. Frames with slots and default values, inherited along is-a links; a more specific frame overrides a more
#    general one (inferential distance), and conflicts that no specificity can settle are reported (the Nixon diamond).

# ---------------------------------------------------------------- 1. a taxonomy
SUBCLASS = {             # class: its direct superclasses
    "Thing": [],
    "PhysicalObject": ["Thing"],
    "Rock": ["PhysicalObject"],
    "IgneousRock": ["Rock"],
    "SedimentaryRock": ["Rock"],
    "MetamorphicRock": ["Rock"],
    "Basalt": ["IgneousRock"],
    "Granite": ["IgneousRock"],
    "Mudstone": ["SedimentaryRock"],
    "Sandstone": ["SedimentaryRock"],
    "Machine": ["PhysicalObject"],
    "Rover": ["Machine"],
    "Instrument": ["Machine"],
}
DISJOINT = [{"IgneousRock", "SedimentaryRock", "MetamorphicRock"}, {"Rock", "Machine"}]
PARTITIONS = {"Rock": ["IgneousRock", "SedimentaryRock", "MetamorphicRock"]}   # disjoint and exhaustive
MEMBER = {"Rock42": ["Mudstone"], "Rock7": ["Basalt"], "Odd1": ["Basalt", "Sandstone"], "Percy": ["Rover"],
          "SuperCam": ["Instrument"]}
PART_OF = {("SuperCam", "Mast"), ("Mast", "Percy"), ("Wheel3", "Percy"), ("Drill", "Arm"), ("Arm", "Percy")}


def superclasses(c):
    """All classes above c, including c (the reflexive-transitive closure of SUBCLASS)."""
    out, stack = [], [c]
    while stack:
        x = stack.pop()
        if x not in out:
            out.append(x)
            stack.extend(SUBCLASS[x])
    return out


def types_of(obj):
    return sorted({s for c in MEMBER[obj] for s in superclasses(c)})


def disjointness_violations(obj):
    t = set(types_of(obj))
    return [sorted(d & t) for d in DISJOINT if len(d & t) > 1]


def parts(whole):
    """Transitive part-of: everything that is part of whole, directly or through other parts."""
    found, changed = set(), True
    while changed:
        changed = False
        for p, w in PART_OF:
            if (w == whole or w in found) and p not in found:
                found.add(p)
                changed = True
    return sorted(found)


# ---------------------------------------------------------------- 2. frames with defaults
FRAMES = {
    "Bird":       {"is_a": [], "flies": True, "legs": 2, "covering": "feathers"},
    "Penguin":    {"is_a": ["Bird"], "flies": False, "swims": True},
    "Emperor":    {"is_a": ["Penguin"], "height_cm": 115},
    "Opus":       {"is_a": ["Emperor"], "legs": 1},          # this one lost a leg: an exception for one individual
    "Tweety":     {"is_a": ["Bird"]},
    "Quaker":     {"is_a": [], "pacifist": True},
    "Republican": {"is_a": [], "pacifist": False},
    "Nixon":      {"is_a": ["Quaker", "Republican"]},
}


def ancestors(f):
    out, stack = [], [f]
    while stack:
        x = stack.pop()
        if x not in out:
            out.append(x)
            stack.extend(FRAMES[x]["is_a"])
    return out


def lookup(f, slot):
    """Inherit slot values; a frame overrides every frame above it. Returns (value, source) or a conflict."""
    holders = [a for a in ancestors(f) if slot in FRAMES[a]]
    # keep only the most specific holders: drop any holder that is an ancestor of another holder
    best = [h for h in holders if not any(h != k and h in ancestors(k) for k in holders)]
    values = {FRAMES[h][slot] for h in best}
    if not best:
        return None, "unknown"
    if len(values) == 1:
        return values.pop(), "+".join(sorted(best))
    return "CONFLICT", ", ".join(f"{h} says {FRAMES[h][slot]}" for h in sorted(best))


if __name__ == "__main__":
    print("1. A taxonomy")
    for obj in MEMBER:
        v = disjointness_violations(obj)
        print(f"  {obj:<8} types: {', '.join(types_of(obj))}" + (f"   <- violates disjointness {v}" if v else ""))
    print("  Mudstone is a subclass of Rock:", "Rock" in superclasses("Mudstone"),
          "| Basalt is a subclass of SedimentaryRock:", "SedimentaryRock" in superclasses("Basalt"))
    leaves = [c for c in SUBCLASS if "Rock" in superclasses(c) and not any(c in v for v in SUBCLASS.values())]
    for whole, pieces in PARTITIONS.items():
        covered = all(any(p in superclasses(l) for p in pieces) for l in leaves)
        print(f"  partition of {whole} into {pieces}: every leaf rock class is covered: {covered}")
    print("  parts of Percy:", parts("Percy"))
    print()

    print("2. Frames and default inheritance")
    for f in ["Tweety", "Opus", "Nixon"]:
        for slot in ["flies", "legs", "swims", "covering", "pacifist"]:
            v, src = lookup(f, slot)
            if v is not None:
                print(f"  {f:<6} {slot:<9} = {str(v):<9} from {src}")
