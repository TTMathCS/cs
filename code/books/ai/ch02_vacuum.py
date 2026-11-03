"""Chapter 2: the two-square vacuum world, and why the performance measure matters.

Squares A and B, each Clean or Dirty. The agent perceives [location, status]
and can do Left, Right, Suck or NoOp. We run agents under three performance
measures:
  M1  +1 for each clean square at each time step
  M2  +1 for each unit of dirt sucked up (and the agent may also Dump dirt)
  M3  M1, minus 1 for each move (Left or Right)
We also check by brute force that the reflex agent is optimal under M1, and
count the size of a table-driven agent. Standard library only.
"""
from itertools import product

LOCS = ("A", "B")


def step(state, action):
    """state = (location, dirtA, dirtB) with dirt as 0/1. Returns (new state, sucked)."""
    loc, da, db = state
    dirt = {"A": da, "B": db}
    sucked = 0
    if action == "Left":
        loc = "A"
    elif action == "Right":
        loc = "B"
    elif action == "Suck" and dirt[loc]:
        dirt[loc] = 0
        sucked = 1
    elif action == "Dump":
        dirt[loc] = 1
    return (loc, dirt["A"], dirt["B"]), sucked


def run(agent_factory, measure, state, T):
    agent = agent_factory()
    score = 0
    for _ in range(T):
        loc, da, db = state
        percept = (loc, "Dirty" if (da if loc == "A" else db) else "Clean")
        action = agent(percept)
        state, sucked = step(state, action)
        clean = (1 - state[1]) + (1 - state[2])
        if measure == "M1":
            score += clean
        elif measure == "M2":
            score += sucked
        elif measure == "M3":
            score += clean - (action in ("Left", "Right"))
    return score


# ------------------------------------------------------------------ agents
def reflex_agent():
    def act(percept):
        loc, status = percept
        if status == "Dirty":
            return "Suck"
        return "Right" if loc == "A" else "Left"
    return act


def dumping_agent():
    """Games measure M2: suck the dirt, dump it back, suck it again..."""
    def act(percept):
        loc, status = percept
        return "Suck" if status == "Dirty" else "Dump"
    return act


def model_based_agent():
    """Remembers which squares it has seen clean; stops moving when both are."""
    known = {}

    def act(percept):
        loc, status = percept
        if status == "Dirty":
            known[loc] = "Clean"            # it will be clean after this Suck
            return "Suck"
        known[loc] = "Clean"
        if all(known.get(x) == "Clean" for x in LOCS):
            return "NoOp"
        return "Right" if loc == "A" else "Left"
    return act


AGENTS = {"reflex": reflex_agent, "dumping": dumping_agent,
          "model-based": model_based_agent}
STARTS = [(loc, da, db) for loc in LOCS for da in (0, 1) for db in (0, 1)]


def best_possible(state, T, measure="M1"):
    """Brute force over every action sequence of length T (no Dump):
    an upper bound for any agent, which also does not know the state."""
    best = None
    for seq in product(("Left", "Right", "Suck", "NoOp"), repeat=T):
        s, score = state, 0
        for a in seq:
            s, _ = step(s, a)
            score += (1 - s[1]) + (1 - s[2])
        best = score if best is None else max(best, score)
    return best


def main():
    T = 1000
    print(f"average score over the 8 starting states, {T} steps:")
    print(f"  {'agent':12} {'M1':>8} {'M2':>8} {'M3':>8}")
    for name, f in AGENTS.items():
        row = [sum(run(f, m, s, T) for s in STARTS) / len(STARTS)
               for m in ("M1", "M2", "M3")]
        print(f"  {name:12} {row[0]:8.2f} {row[1]:8.2f} {row[2]:8.2f}")

    print("\nreflex agent vs best possible action sequence under M1, T = 6:")
    for s in STARTS:
        r, b = run(reflex_agent, "M1", s, 6), best_possible(s, 6)
        print(f"  start {s}: reflex {r:2d}  best {b:2d}")

    print("\nentries in a table-driven agent (4 possible percepts):")
    for T in (1, 2, 5, 10, 20):
        print(f"  lifetime {T:2d} steps: {sum(4 ** t for t in range(1, T + 1)):,}")


if __name__ == "__main__":
    main()
