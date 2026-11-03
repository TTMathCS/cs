# Chapter 12: probability as degree of belief, full joint distributions and Bayes' rule.
# 1. A full joint distribution over three yes/no variables (typed in as a table), and every basic operation on it:
#    marginalising, conditioning, normalising, checking independence.
# 2. Bayes' rule on a medical test, with probabilities and with natural frequencies.
# 3. Two tests: conditionally independent evidence multiplies likelihood ratios (naive Bayes).
from itertools import product
import numpy as np

# Storm (dust storm today), Low (solar power low), Dark (navigation images dark). Numbers invented for the example.
NAMES = ["Storm", "Low", "Dark"]
JOINT = np.zeros((2, 2, 2))
p_storm = 0.1
p_low = {1: 0.8, 0: 0.1}       # P(Low | Storm)
p_dark = {1: 0.7, 0: 0.05}     # P(Dark | Storm)
for s, l, d in product((0, 1), repeat=3):
    JOINT[s, l, d] = (p_storm if s else 1 - p_storm) * (p_low[s] if l else 1 - p_low[s]) * \
                     (p_dark[s] if d else 1 - p_dark[s])


def prob(joint, **fixed):
    """P(variables = values) by summing the matching entries of the joint table."""
    idx = tuple(fixed.get(n, slice(None)) for n in NAMES)
    return joint[idx].sum()


def cond(joint, query, **evidence):
    """P(query | evidence) = P(query, evidence) / P(evidence)."""
    return prob(joint, **query, **evidence) / prob(joint, **evidence)


if __name__ == "__main__":
    print("1. The full joint distribution P(Storm, Low, Dark)")
    print("  Storm Low Dark   P")
    for s, l, d in product((1, 0), repeat=3):
        print(f"    {s}    {l}    {d}   {JOINT[s, l, d]:.4f}")
    print(f"  total {JOINT.sum():.4f}")
    print(f"  P(Low) = {prob(JOINT, Low=1):.4f}   (marginalise: sum over Storm and Dark)")
    print(f"  P(Storm | Low) = {cond(JOINT, {'Storm': 1}, Low=1):.4f}")
    print(f"  P(Storm | Low, Dark) = {cond(JOINT, {'Storm': 1}, Low=1, Dark=1):.4f}")
    un = np.array([prob(JOINT, Storm=v, Low=1, Dark=1) for v in (1, 0)])
    print(f"  normalising: unnormalised {un.round(5)} -> {(un / un.sum()).round(4)}")
    print(f"  Low and Dark independent?  P(Low,Dark) = {prob(JOINT, Low=1, Dark=1):.4f}"
          f" vs P(Low)P(Dark) = {prob(JOINT, Low=1) * prob(JOINT, Dark=1):.4f}")
    lhs = cond(JOINT, {"Low": 1, "Dark": 1}, Storm=1)
    rhs = cond(JOINT, {"Low": 1}, Storm=1) * cond(JOINT, {"Dark": 1}, Storm=1)
    print(f"  ... but given Storm: P(Low,Dark|Storm) = {lhs:.4f} = P(Low|Storm)P(Dark|Storm) = {rhs:.4f}")
    print()

    print("2. Bayes' rule: a test for a condition with prevalence 1 in 100")
    prior, sens, spec = 0.01, 0.90, 0.95
    p_pos = sens * prior + (1 - spec) * (1 - prior)
    post = sens * prior / p_pos
    print(f"  P(+) = {sens}*{prior} + {1 - spec:.2f}*{1 - prior} = {p_pos:.4f}")
    print(f"  P(condition | +) = {sens * prior:.4f} / {p_pos:.4f} = {post:.4f}")
    n = 10000
    sick, healthy = round(n * prior), round(n * (1 - prior))
    tp, fp = round(sick * sens), round(healthy * (1 - spec))
    print(f"  natural frequencies: of {n} people, {sick} have it and {tp} of them test positive;")
    print(f"  of the {healthy} who do not, {fp} test positive. So {tp} / ({tp} + {fp}) = {tp / (tp + fp):.4f}")
    print()

    print("3. Two positive results from conditionally independent tests")
    lr = sens / (1 - spec)
    odds = prior / (1 - prior)
    for k in range(4):
        o = odds * lr ** k
        print(f"  {k} positive test(s): odds {o:.4f}, probability {o / (1 + o):.4f}")
    rng = np.random.default_rng(1)
    m = 1_000_000
    has = rng.random(m) < prior
    t1 = np.where(has, rng.random(m) < sens, rng.random(m) < 1 - spec)
    t2 = np.where(has, rng.random(m) < sens, rng.random(m) < 1 - spec)
    print(f"  simulation of {m:,} people: P(condition | both positive) = {has[t1 & t2].mean():.4f}")
