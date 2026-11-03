"""Chapter 1: a tiny rule-based expert system with certainty factors.

Expert systems of the 1970s and 1980s (MYCIN, PROSPECTOR, XCON) stored an
expert's knowledge as IF-THEN rules and chained them forwards. MYCIN attached a
certainty factor (CF) between -1 and 1 to each rule and combined evidence with
a fixed formula. This toy identifies a rock from a few observations; the rules
are simplified textbook geology, written for the demonstration only.
Standard library only.
"""

# (conditions, conclusion, CF of the rule)
RULES = [
    ({"colour=dark", "grain=fine"}, "type=volcanic", 0.7),
    ({"vesicles=yes"}, "type=volcanic", 0.6),
    ({"colour=light", "grain=coarse"}, "type=plutonic", 0.7),
    ({"layers=yes", "grains_visible=yes"}, "type=sedimentary", 0.8),
    ({"type=volcanic", "colour=dark"}, "rock=basalt", 0.8),
    ({"type=plutonic", "colour=light"}, "rock=granite", 0.8),
    ({"type=sedimentary", "grain=medium"}, "rock=sandstone", 0.7),
    ({"type=sedimentary", "grain=fine"}, "rock=mudstone", 0.6),
]


def combine(a, b):
    """MYCIN's rule for two certainty factors about the same conclusion."""
    if a >= 0 and b >= 0:
        return a + b * (1 - a)
    if a <= 0 and b <= 0:
        return a + b * (1 + a)
    return (a + b) / (1 - min(abs(a), abs(b)))


def infer(facts, trace=False):
    """Forward chaining: fire every rule whose conditions are all known with
    CF > 0.2, until nothing changes. A rule's conclusion gets
    CF(rule) * min(CF of its conditions); evidence from several rules is
    combined with combine()."""
    cf = dict(facts)
    fired = set()
    changed = True
    while changed:
        changed = False
        for i, (conds, concl, rcf) in enumerate(RULES):
            if i in fired or not all(cf.get(c, 0) > 0.2 for c in conds):
                continue
            fired.add(i)
            new = rcf * min(cf[c] for c in conds)
            old = cf.get(concl)
            cf[concl] = new if old is None else combine(old, new)
            changed = True
            if trace:
                print(f"    rule {i + 1} fires: {concl} gets {new:.3f}"
                      f" -> now {cf[concl]:.3f}")
    return {k: v for k, v in cf.items() if k.startswith("rock=")}


def main():
    print("combine(0.56, 0.42) =", round(combine(0.56, 0.42), 4))
    cases = {
        "dark, fine-grained, with gas holes": {
            "colour=dark": 1.0, "grain=fine": 0.8, "vesicles=yes": 0.7},
        "light, coarse-grained": {"colour=light": 1.0, "grain=coarse": 0.9},
        "layered, sand grains visible, medium grain": {
            "layers=yes": 0.9, "grains_visible=yes": 1.0, "grain=medium": 0.8},
        "glassy and green (no rule mentions it)": {
            "colour=green": 1.0, "lustre=glassy": 1.0},
    }
    for name, facts in cases.items():
        print(f"\ncase: {name}")
        result = infer(facts, trace=True)
        if result:
            for k, v in sorted(result.items(), key=lambda kv: -kv[1]):
                print(f"  conclusion {k} with CF {v:.3f}")
        else:
            print("  no conclusion: the rules do not cover this case")


if __name__ == "__main__":
    main()
