# Chapter 14: expected utility, risk attitudes and the value of information, from scratch.
import itertools
import math

# Part 1. Utility of money: a risk-averse agent with logarithmic utility of total wealth.
wealth = 1000.0


def U(x):
    return math.log(wealth + x)


def certainty_equivalent(lottery):
    eu = sum(p * U(x) for p, x in lottery)
    return math.exp(eu) - wealth          # the sure amount with the same utility


lottery = [(0.5, 0.0), (0.5, 1000.0)]
ev = sum(p * x for p, x in lottery)
ce = certainty_equivalent(lottery)
print("Part 1. log utility of wealth, starting wealth 1000")
print(f"coin flip for 0 or 1000: expected value {ev:.2f}, certainty equivalent {ce:.2f},"
      f" risk premium {ev - ce:.2f}")

# St Petersburg: win 2^k with probability 2^-k (k = 1, 2, ...). Expected money is infinite.
st_pete = [(2.0 ** -k, 2.0 ** k) for k in range(1, 200)]
partial_ev = sum(p * x for p, x in st_pete[:40])
print(f"St Petersburg game: expected money after 40 terms {partial_ev:.0f} (and growing without bound);"
      f" certainty equivalent with log utility {certainty_equivalent(st_pete):.2f}")

# Part 2. A decision network: should a rover drill a rock? (a toy model with made-up numbers)
# Chance node Mineral (prior 0.3); decision Drill or Skip; utility in "science points":
# drilling costs 20, a sample containing the mineral is worth 100.
P_M = 0.3
TESTS = {"spectrometer": (0.8, 0.1), "camera": (0.7, 0.2)}   # P(positive | mineral), P(positive | none)


def best_eu(p_mineral):
    eu = {"drill": 100 * p_mineral - 20, "skip": 0.0}
    a = max(eu, key=eu.get)
    return a, eu[a]


def eu_after(tests):
    """Expected utility if we first observe the given tests, then act optimally."""
    total = 0.0
    for outcome in itertools.product([True, False], repeat=len(tests)):
        pm, pn = P_M, 1 - P_M                       # joint P(outcome, mineral) and P(outcome, none)
        for name, pos in zip(tests, outcome):
            tp, fp = TESTS[name]
            pm *= tp if pos else 1 - tp
            pn *= fp if pos else 1 - fp
        p_out = pm + pn
        action, eu = best_eu(pm / p_out)
        total += p_out * eu
        if len(tests) == 1:
            print(f"   {tests[0]} {'positive' if outcome[0] else 'negative'}: P = {p_out:.3f},"
                  f" P(mineral | result) = {pm / p_out:.3f}, best action {action}, EU {eu:.2f}")
    return total


a0, eu0 = best_eu(P_M)
print(f"\nPart 2. no information: best action {a0}, EU {eu0:.2f}")
perfect = P_M * best_eu(1.0)[1] + (1 - P_M) * best_eu(0.0)[1]
print(f"perfect information: EU {perfect:.2f}, value of perfect information {perfect - eu0:.2f}")
vpi = {}
for name in TESTS:
    print(f" observing the {name}:")
    vpi[name] = eu_after([name]) - eu0
    print(f"   value of information {vpi[name]:.2f}")
both = eu_after(list(TESTS)) - eu0
print(f"both tests together: value of information {both:.2f}"
      f" (sum of the two separately {vpi['spectrometer'] + vpi['camera']:.2f})")
