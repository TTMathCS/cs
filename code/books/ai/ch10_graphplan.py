# Chapter 10: GraphPlan (Blum and Furst 1995) from scratch.
# 1. Build the planning graph: proposition levels and action levels (with no-op "persistence" actions) and the
#    mutual-exclusion (mutex) relations between actions and between propositions.
# 2. Read heuristics off the graph: the level at which each goal first appears, max-level, level-sum, set-level.
# 3. Extract a plan by backward search through the graph, remembering failed goal sets ("nogoods").
#    The plan is a sequence of steps; the actions inside one step can run in any order, or at the same time.
from itertools import combinations
from ch10_strips import Action, act, blocks_world, towers


def noop(p):
    return Action(f"keep {p}", frozenset([p]), frozenset([p]), frozenset())


class PlanningGraph:
    def __init__(self, init, acts):
        self.acts = acts
        self.props = [set(init)]            # proposition level 0
        self.pmutex = [set()]               # pairs (frozensets) of mutex propositions, per level
        self.alevels = []                   # action levels
        self.amutex = []

    def expand(self):
        P, PM = self.props[-1], self.pmutex[-1]
        A = [a for a in self.acts if a.pre <= P and not any(frozenset(c) in PM for c in combinations(a.pre, 2))]
        A += [noop(p) for p in sorted(P)]
        AM = set()
        for a, b in combinations(A, 2):
            if (a.delete & (b.add | b.pre)) or (b.delete & (a.add | a.pre)):   # inconsistent effects, interference
                AM.add(frozenset([a, b]))
            elif any(frozenset([p, q]) in PM for p in a.pre for q in b.pre if p != q):  # competing needs
                AM.add(frozenset([a, b]))
        newP = set().union(*[a.add for a in A])
        achievers = {p: [a for a in A if p in a.add] for p in newP}
        newPM = set()
        for p, q in combinations(sorted(newP), 2):
            if all(frozenset([a, b]) in AM for a in achievers[p] for b in achievers[q] if a != b) and \
                    not set(achievers[p]) & set(achievers[q]):
                newPM.add(frozenset([p, q]))
        self.alevels.append(A)
        self.amutex.append(AM)
        self.props.append(newP)
        self.pmutex.append(newPM)

    def leveled_off(self):
        return len(self.props) > 1 and self.props[-1] == self.props[-2] and \
            len(self.pmutex[-1]) == len(self.pmutex[-2])

    def goals_ok(self, goals, k):
        return goals <= self.props[k] and not any(frozenset(c) in self.pmutex[k] for c in combinations(goals, 2))


def graphplan(init, goal, acts, max_levels=30):
    pg = PlanningGraph(init, acts)
    nogoods = set()
    calls = [0]

    def extract(goals, k):
        """Find a set of pairwise non-mutex actions at action level k-1 achieving all goals at level k."""
        if k == 0:
            return []
        if (frozenset(goals), k) in nogoods:
            return None
        A, AM = pg.alevels[k - 1], pg.amutex[k - 1]

        def choose(remaining, chosen):
            calls[0] += 1
            if not remaining:
                pre = frozenset().union(*[a.pre for a in chosen])
                sub = extract(pre, k - 1)
                return None if sub is None else sub + [[a for a in chosen if not a.name.startswith("keep")]]
            g = min(remaining)
            if any(g in a.add for a in chosen):
                return choose(remaining - {g}, chosen)
            # try no-ops first (prefer not to act), then real actions
            options = sorted((a for a in A if g in a.add), key=lambda a: (not a.name.startswith("keep"), a.name))
            for a in options:
                if all(frozenset([a, b]) not in AM for b in chosen):
                    r = choose(remaining - a.add, chosen + [a])
                    if r is not None:
                        return r
            return None

        r = choose(frozenset(goals), [])
        if r is None:
            nogoods.add((frozenset(goals), k))
        return r

    for _ in range(max_levels):
        k = len(pg.props) - 1
        if pg.goals_ok(goal, k):
            plan = extract(goal, k)
            if plan is not None:
                return plan, pg, calls[0]
        if pg.leveled_off() and not pg.goals_ok(goal, k):
            return None, pg, calls[0]
        pg.expand()
    return None, pg, calls[0]


def graph_heuristics(init, goal, acts):
    pg = PlanningGraph(init, acts)
    first = {}
    while True:
        k = len(pg.props) - 1
        for g in goal:
            if g in pg.props[k] and g not in first:
                first[g] = k
        if pg.goals_ok(goal, k):
            set_level = k
            break
        if pg.leveled_off():
            set_level = None
            break
        pg.expand()
    return first, max(first.values()), sum(first.values()), set_level


if __name__ == "__main__":
    acts = blocks_world("ABC")
    init = towers([["A", "C"], ["B"]])
    goal = frozenset({"On(A,B)", "On(B,C)"})
    print("1. The planning graph for the Sussman anomaly")
    plan, pg, calls = graphplan(init, goal, acts)
    print("  level  propositions  prop-mutexes  actions(incl. no-ops)  action-mutexes")
    for k in range(len(pg.props)):
        a = len(pg.alevels[k]) if k < len(pg.alevels) else "-"
        am = len(pg.amutex[k]) if k < len(pg.amutex) else "-"
        print(f"  {k:5d}  {len(pg.props[k]):12d}  {len(pg.pmutex[k]):12d}  {a:>21}  {am:>14}")
    print("  On(A,B) and On(B,C) mutex at levels 0..6:", [frozenset(goal) in pg.pmutex[k] for k in range(7)])
    shrink = all(m in pg.pmutex[k] for k in range(len(pg.props) - 1) for m in pg.pmutex[k + 1] if m <= pg.props[k])
    print("  a pair mutex at level k+1 was already mutex at level k (mutexes only disappear):", shrink)
    print()
    print("2. Heuristics read off the graph")
    first, mx, sm, sl = graph_heuristics(init, goal, acts)
    print(f"  first level: {first}; max-level {mx}, level-sum {sm}, set-level {sl}  (true cost 6)")
    print()
    print(f"3. Extracted plan ({len(plan)} steps, {calls} choice points)")
    for i, step in enumerate(plan, 1):
        print(f"  step {i}: {', '.join(a.name for a in step)}")
    print()

    print("4. Parallel steps: two rovers, each must drive and take a picture")
    links = [("Base", "Rim"), ("Rim", "Delta"), ("Base", "Ridge")]
    links += [(b, a) for a, b in links]
    acts2 = []
    for r in ("R1", "R2"):
        for a, b in links:
            acts2.append(act(f"Drive({r},{a},{b})", [f"At({r},{a})"], [f"At({r},{b})"], [f"At({r},{a})"]))
        for p in ("Base", "Rim", "Delta", "Ridge"):
            acts2.append(act(f"Image({r},{p})", [f"At({r},{p})"], [f"ImageOf({p})"], []))
    init2 = frozenset({"At(R1,Base)", "At(R2,Base)"})
    goal2 = frozenset({"ImageOf(Delta)", "ImageOf(Ridge)", "At(R1,Base)"})
    plan2, pg2, calls2 = graphplan(init2, goal2, acts2)
    for i, step in enumerate(plan2, 1):
        print(f"  step {i}: {', '.join(a.name for a in step)}")
    print(f"  {len(plan2)} steps, {sum(len(s) for s in plan2)} actions")
