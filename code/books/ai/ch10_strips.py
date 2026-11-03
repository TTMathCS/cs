# Chapter 10: STRIPS planning by state-space search, with ignore-delete-lists heuristics.
# A state is a frozenset of ground atoms (strings such as "On(A,B)"). An action has preconditions, an add list and
# a delete list (the STRIPS representation of Fikes and Nilsson, 1971).
# 1. The Sussman anomaly: solving one goal at a time fails, in both orders.
# 2. Forward (progression) search: breadth-first, A* with h_max, A* with h_add, greedy best-first with h_FF.
# 3. Backward (regression) search over sets of goals.
# 4. The relaxed heuristics compared with the true distance, and a rover domain.
import heapq
import time
from collections import deque, namedtuple
from itertools import count

Action = namedtuple("Action", "name pre add delete")


def act(name, pre, add, delete):
    return Action(name, frozenset(pre), frozenset(add), frozenset(delete))


def applicable(s, a):
    return a.pre <= s


def result(s, a):
    return (s - a.delete) | a.add


# ---------------------------------------------------------------- domains
def blocks_world(blocks):
    acts = []
    for x in blocks:
        acts.append(act(f"PickUp({x})", [f"Clear({x})", f"OnTable({x})", "HandEmpty"],
                        [f"Holding({x})"], [f"Clear({x})", f"OnTable({x})", "HandEmpty"]))
        acts.append(act(f"PutDown({x})", [f"Holding({x})"],
                        [f"OnTable({x})", f"Clear({x})", "HandEmpty"], [f"Holding({x})"]))
        for y in blocks:
            if x != y:
                acts.append(act(f"Stack({x},{y})", [f"Holding({x})", f"Clear({y})"],
                                [f"On({x},{y})", f"Clear({x})", "HandEmpty"], [f"Holding({x})", f"Clear({y})"]))
                acts.append(act(f"Unstack({x},{y})", [f"On({x},{y})", f"Clear({x})", "HandEmpty"],
                                [f"Holding({x})", f"Clear({y})"], [f"On({x},{y})", f"Clear({x})", "HandEmpty"]))
    return acts


def towers(stacks):
    """stacks: list of lists, bottom first. Returns the atoms describing them."""
    atoms = {"HandEmpty"}
    for st in stacks:
        atoms.add(f"OnTable({st[0]})")
        for lo, hi in zip(st, st[1:]):
            atoms.add(f"On({hi},{lo})")
        atoms.add(f"Clear({st[-1]})")
    return frozenset(atoms)


def rover_domain():
    """A rover, five places, a camera, a sample arm. Goals: images sent, samples cached, rover parked."""
    links = [("Base", "Rim"), ("Rim", "Delta"), ("Delta", "Fan"), ("Rim", "Ridge"), ("Ridge", "Fan")]
    links += [(b, a) for a, b in links]
    places = sorted({p for l in links for p in l})
    acts = []
    for a, b in links:
        acts.append(act(f"Drive({a},{b})", [f"At({a})"], [f"At({b})"], [f"At({a})"]))
    for p in places:
        acts.append(act(f"Image({p})", [f"At({p})", "CameraOn"], [f"ImageOf({p})"], []))
        acts.append(act(f"Sample({p})", [f"At({p})", f"RockAt({p})", "ArmFree"],
                        [f"Holding({p})"], [f"RockAt({p})", "ArmFree"]))
        acts.append(act(f"Cache({p})", [f"Holding({p})"], [f"Cached({p})", "ArmFree"], [f"Holding({p})"]))
        acts.append(act(f"Send({p})", [f"ImageOf({p})", "AntennaReady"], [f"Sent({p})"], []))
    acts.append(act("CameraOn", ["CameraOff"], ["CameraOn"], ["CameraOff"]))
    acts.append(act("CameraOff", ["CameraOn"], ["CameraOff"], ["CameraOn"]))
    acts.append(act("DeployAntenna", ["CameraOff"], ["AntennaReady"], []))
    init = frozenset({"At(Base)", "CameraOff", "ArmFree", "RockAt(Delta)", "RockAt(Ridge)", "RockAt(Fan)"})
    goal = frozenset({"Sent(Fan)", "Sent(Delta)", "Cached(Ridge)", "Cached(Delta)", "At(Base)"})
    return acts, init, goal


# ---------------------------------------------------------------- relaxed heuristics (delete lists ignored)
def h_costs(s, acts, goal, combine):
    """Cost of each atom when deletes are ignored; combine = max (h_max) or sum (h_add)."""
    cost = {p: 0 for p in s}
    changed = True
    while changed:
        changed = False
        for a in acts:
            if all(p in cost for p in a.pre):
                c = 1 + (combine(cost[p] for p in a.pre) if a.pre else 0)
                for q in a.add:
                    if c < cost.get(q, float("inf")):
                        cost[q] = c
                        changed = True
    if not all(g in cost for g in goal):
        return float("inf")
    return combine(cost[g] for g in goal) if goal else 0


def h_max(s, acts, goal):
    return h_costs(s, acts, goal, max)


def h_add(s, acts, goal):
    return h_costs(s, acts, goal, sum)


def h_ff(s, acts, goal):
    """Hoffmann and Nebel's FF heuristic: build the relaxed planning graph, extract a relaxed plan, count it."""
    level = {p: 0 for p in s}
    achiever = {}
    layer = 0
    while not all(g in level for g in goal):
        layer += 1
        new = {}
        for a in acts:
            if all(level.get(p, layer) < layer for p in a.pre):
                for q in a.add:
                    if q not in level and q not in new:
                        new[q] = a
        if not new:
            return float("inf")
        for q, a in new.items():
            level[q] = layer
            achiever[q] = a
    plan, agenda = set(), [g for g in goal if level[g] > 0]
    done = set()
    while agenda:
        g = agenda.pop()
        if g in done:
            continue
        done.add(g)
        a = achiever[g]
        if a.name not in plan:
            plan.add(a.name)
            agenda.extend(p for p in a.pre if level[p] > 0)
    return len(plan)


def h_zero(s, acts, goal):
    return 0


# ---------------------------------------------------------------- forward search
def forward(init, goal, acts, h=h_zero, weight=1.0, greedy=False, limit=10**6):
    """A* (or greedy best-first) in the space of states; h_zero gives uniform-cost = breadth-first here."""
    tie = count()
    frontier = [(h(init, acts, goal), next(tie), init, 0, None)]
    parent = {init: None}
    best_g = {init: 0}
    expanded = 0
    while frontier:
        f, _, s, g, _ = heapq.heappop(frontier)
        if g > best_g[s]:
            continue
        if goal <= s:
            plan = []
            while parent[s] is not None:
                s, a = parent[s]
                plan.append(a)
            return plan[::-1], expanded
        expanded += 1
        if expanded > limit:
            return None, expanded
        for a in acts:
            if applicable(s, a):
                t = result(s, a)
                if g + 1 < best_g.get(t, float("inf")):
                    best_g[t] = g + 1
                    parent[t] = (s, a.name)
                    hv = h(t, acts, goal)
                    if hv < float("inf"):
                        key = hv if greedy else g + 1 + weight * hv
                        heapq.heappush(frontier, (key, next(tie), t, g + 1, None))
    return None, expanded


# ---------------------------------------------------------------- backward search
def regress(g, a):
    """The goal set that must hold before a, so that g holds after it; None if a is not relevant or would undo g."""
    if not (a.add & g) or (a.delete & g):
        return None
    return (g - a.add) | a.pre


def consistent(g):
    """A cheap check that rules out impossible goal sets (a hand holding two blocks, a rover in two places...)."""
    held = [p for p in g if p.startswith("Holding(")]
    at = [p for p in g if p.startswith("At(")]
    if len(held) > 1 or len(at) > 1 or (held and "HandEmpty" in g):
        return False
    for p in g:
        if p.startswith("On("):
            x, y = p[3:-1].split(",")
            if f"Clear({y})" in g or f"OnTable({x})" in g or f"Holding({x})" in g or f"Holding({y})" in g:
                return False
    return True


def backward(init, goal, acts, limit=10**6):
    """Breadth-first search from the goal: nodes are sets of atoms (descriptions of many states)."""
    frontier = deque([goal])
    parent = {goal: None}
    expanded = 0
    while frontier:
        g = frontier.popleft()
        if g <= init:
            plan = []
            while parent[g] is not None:
                g, a = parent[g]
                plan.append(a)
            return plan, expanded
        expanded += 1
        if expanded > limit:
            return None, expanded
        for a in acts:
            r = regress(g, a)
            if r is not None and consistent(r) and r not in parent:
                parent[r] = (g, a.name)
                frontier.append(r)
    return None, expanded


def one_goal_at_a_time(init, goals, acts):
    """Solve each goal separately with BFS, in order, without protecting the earlier ones."""
    s, plan = init, []
    for g in goals:
        p, _ = forward(s, frozenset([g]), acts)
        for name in p:
            a = next(x for x in acts if x.name == name)
            s = result(s, a)
        plan += p
    return plan, all(g in s for g in goals)


if __name__ == "__main__":
    print("1. The Sussman anomaly: C on A; A and B on the table.  Goal: On(A,B) and On(B,C).")
    acts = blocks_world("ABC")
    init = towers([["A", "C"], ["B"]])
    goals = ["On(A,B)", "On(B,C)"]
    for order in (goals, goals[::-1]):
        plan, ok = one_goal_at_a_time(init, order, acts)
        print(f"  goals in order {order}: {len(plan)} actions, all goals true at the end: {ok}")
    plan, n = forward(init, frozenset(goals), acts)
    print(f"  planning for both goals together: {len(plan)} actions: {', '.join(plan)}")
    print()

    print("2. Forward and backward search")
    problems = [
        ("Sussman (3 blocks)", acts, init, frozenset(goals)),
        ("reverse a tower of 5", blocks_world("ABCDE"), towers([list("ABCDE")]),
         frozenset({"On(D,E)", "On(C,D)", "On(B,C)", "On(A,B)"})),
        ("6 blocks, two towers", blocks_world("ABCDEF"), towers([list("ABC"), list("DEF")]),
         frozenset({"On(A,F)", "On(F,B)", "On(B,E)", "On(E,C)", "On(C,D)"})),
    ]
    r_acts, r_init, r_goal = rover_domain()
    problems.append(("rover day", r_acts, r_init, r_goal))
    methods = [("forward BFS", lambda i, g, a: forward(i, g, a)),
               ("A* h_max", lambda i, g, a: forward(i, g, a, h_max)),
               ("A* h_add", lambda i, g, a: forward(i, g, a, h_add)),
               ("greedy h_FF", lambda i, g, a: forward(i, g, a, h_ff, greedy=True)),
               ("backward BFS", lambda i, g, a: backward(i, g, a))]
    print(f"  {'problem':<22} {'method':<13} {'length':>6} {'expanded':>9} {'seconds':>8}")
    optimal = {}
    for name, a, i, g in problems:
        for mname, m in methods:
            t0 = time.time()
            plan, n = m(i, g, a)
            if mname == "forward BFS":
                optimal[name] = plan            # unit action costs: breadth-first plans are optimal
            print(f"  {name:<22} {mname:<13} {len(plan) if plan else '-':>6} {n:>9} {time.time() - t0:8.2f}")
    print()

    print("3. Heuristic values at the start, against the true optimal plan length h*")
    print(f"  {'problem':<22} {'h_max':>5} {'h_add':>5} {'h_FF':>5} {'h*':>4}")
    for name, a, i, g in problems:
        print(f"  {name:<22} {h_max(i, a, g):>5} {h_add(i, a, g):>5} {h_ff(i, a, g):>5} {len(optimal[name]):>4}")
    print()
    plan = optimal["rover day"]
    print("  an optimal rover plan:")
    for k in range(0, len(plan), 6):
        print("   ", ", ".join(plan[k:k + 6]))
