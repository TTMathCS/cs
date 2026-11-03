# Chapter 5: search when actions are nondeterministic or the state is not observed.
# The vacuum world has two squares, L and R. A state is (robot square, L dirty?, R dirty?).
# 1. AND-OR search in the ERRATIC vacuum world returns a conditional plan.
# 2. Sensorless (no percepts) search over BELIEF STATES (sets of states) in the ordinary world.
# 3. Predict and update with a local dirt sensor.
from collections import deque
from itertools import product

STATES = [(loc, dl, dr) for loc in "LR" for dl in (True, False) for dr in (True, False)]
ACTIONS = ["Suck", "Left", "Right"]


def name(s):
    loc, dl, dr = s
    return f"{loc}:{'D' if dl else 'c'}{'D' if dr else 'c'}"   # e.g. L:DD = robot on L, both dirty


def is_goal(s):
    return not s[1] and not s[2]


def erratic(s, a):
    """Set of possible results. Suck on a dirty square cleans it and SOMETIMES the other one too;
    Suck on a clean square SOMETIMES drops dirt on it."""
    loc, dl, dr = s
    if a == "Left":
        return {("L", dl, dr)}
    if a == "Right":
        return {("R", dl, dr)}
    here_dirty = dl if loc == "L" else dr
    if here_dirty:
        cleaned = ("L", False, dr) if loc == "L" else ("R", dl, False)
        return {cleaned, (loc, False, False)}
    dirtied = ("L", True, dr) if loc == "L" else ("R", dl, True)
    return {s, dirtied}


def ordinary(s, a):
    loc, dl, dr = s
    if a == "Left":
        return ("L", dl, dr)
    if a == "Right":
        return ("R", dl, dr)
    return ("L", False, dr) if loc == "L" else ("R", dl, False)


calls = 0


def or_search(s, path):
    """Return a conditional plan from state s, or None. path holds the states on the current branch."""
    global calls
    calls += 1
    if is_goal(s):
        return []
    if s in path:
        return None                                  # a cycle: give up on this branch
    for a in ACTIONS:
        plan = and_search(erratic(s, a), path + [s])
        if plan is not None:
            return [a, plan]
    return None


def and_search(states, path):
    """Every possible outcome needs its own sub-plan."""
    plans = {}
    for s in sorted(states):
        p = or_search(s, path)
        if p is None:
            return None
        plans[s] = p
    return plans


def show(plan, indent=0):
    """Print a plan [action, {state: subplan}] as nested if-then text."""
    pad = "  " * indent
    if plan == []:
        print(pad + "(goal)")
        return
    action, branches = plan
    print(pad + action)
    if len(branches) == 1:
        show(next(iter(branches.values())), indent)
        return
    for s, sub in branches.items():
        print(pad + f"if state is {name(s)}:")
        show(sub, indent + 1)


def run(plan, s, outcome_choice):
    """Execute a conditional plan; nature picks outcomes with outcome_choice."""
    steps = []
    while plan:
        action, branches = plan
        s = outcome_choice(sorted(erratic(s, action)))
        steps.append(f"{action}->{name(s)}")
        plan = branches[s]
    return steps


start = ("L", True, True)
plan = or_search(start, [])
print("erratic vacuum world, conditional plan from", name(start), f"({calls} OR-nodes expanded):")
show(plan, 1)
print("executed, lucky nature  :", run(plan, start, lambda outs: outs[0]))
print("executed, unlucky nature:", run(plan, start, lambda outs: outs[-1]))

# Check: the plan reaches the goal for EVERY sequence of outcomes, from every state.
ok = 0
for s in STATES:
    p = or_search(s, [])
    stack = [(s, p)]
    good = p is not None
    while stack and good:
        st, pl = stack.pop()
        if pl == []:
            good = good and is_goal(st)
            continue
        a, br = pl
        for o in erratic(st, a):
            stack.append((o, br[o]))
    ok += good
print(f"plans found and verified for {ok} of {len(STATES)} start states")

# 2. Sensorless search: BFS over belief states with the ordinary (deterministic) actions.
start_belief = frozenset(STATES)
frontier, seen = deque([(start_belief, [])]), {start_belief}
while frontier:
    b, acts = frontier.popleft()
    if all(is_goal(s) for s in b):
        break
    for a in ACTIONS:
        nb = frozenset(ordinary(s, a) for s in b)
        if nb not in seen:
            seen.add(nb)
            frontier.append((nb, acts + [a]))
print("\nsensorless plan from total ignorance:", acts, f"({len(seen)} belief states generated)")
b = start_belief
for a in acts:
    b = frozenset(ordinary(s, a) for s in b)
    print(f"  after {a:5s}: {sorted(name(s) for s in b)}")

# how many belief states are reachable at all from total ignorance?
reach, todo = {start_belief}, [start_belief]
while todo:
    b = todo.pop()
    for a in ACTIONS:
        nb = frozenset(ordinary(s, a) for s in b)
        if nb not in reach:
            reach.add(nb)
            todo.append(nb)
print(f"  belief states reachable from total ignorance: {len(reach)} of {2 ** len(STATES) - 1} non-empty sets")

# 3. Local sensing: the robot sees its square and whether that square is dirty.
def percept(s):
    loc, dl, dr = s
    return loc, (dl if loc == "L" else dr)


b = frozenset(STATES)
print("\nlocal sensing, ordinary world")
for a, real in (("start", ("L", True, False)), ("Suck", None), ("Right", None)):
    if a != "start":
        b = frozenset(ordinary(s, a) for s in b)                  # predict
        real = ordinary(real_state, a)
    real_state = real
    p = percept(real_state)
    b = frozenset(s for s in b if percept(s) == p)                # update with the percept
    print(f"  {a:5s} percept {p}: belief {sorted(name(s) for s in b)}")
