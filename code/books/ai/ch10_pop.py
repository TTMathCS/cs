# Chapter 10: partial-order planning (plan-space search) from scratch.
# A partial plan has steps, ordering constraints a < b, causal links a --p--> b ("a achieves p for b"), and open
# preconditions. The planner repairs one flaw at a time: an open precondition (link it to an old or a new step) or a
# threat (a step that deletes p and might fall inside a link a --p--> b: order it before a or after b).
# 1. Shoes and socks: the plan stays partially ordered, and we count its linearizations.
# 2. The Sussman anomaly: interleaving the two goals comes out by itself.
import heapq
from itertools import count
from ch10_strips import Action, act, blocks_world, towers, result


def before(order, a, b):
    """Is a < b implied by the ordering constraints? (depth-first search on the order graph)"""
    stack, seen = [a], {a}
    while stack:
        x = stack.pop()
        for (u, v) in order:
            if u == x and v not in seen:
                if v == b:
                    return True
                seen.add(v)
                stack.append(v)
    return False


def add_order(order, a, b):
    if a == b or before(order, b, a):
        return None                                      # would create a cycle
    return order | {(a, b)}


def threats(steps, order, links):
    for (a, p, b) in links:
        for c, s in steps.items():
            if c not in (a, b) and p in s.delete and not before(order, c, a) and not before(order, b, c):
                yield (c, (a, p, b))


def resolve(plan):
    """Yield every way of resolving all threats in plan (promotion or demotion)."""
    steps, order, links, agenda = plan
    t = next(threats(steps, order, links), None)
    if t is None:
        yield plan
        return
    c, (a, p, b) = t
    for o in (add_order(order, c, a), add_order(order, b, c)):   # demotion, promotion
        if o is not None:
            yield from resolve((steps, o, links, agenda))


def pop(init, goal, library, limit=200000):
    START, FINISH = 0, 1
    steps = {START: Action("Start", frozenset(), frozenset(init), frozenset()),
             FINISH: Action("Finish", frozenset(goal), frozenset(), frozenset())}
    plan0 = (steps, frozenset({(START, FINISH)}), frozenset(), tuple(sorted((g, FINISH) for g in goal)))
    tie = count()
    frontier = [(len(goal), next(tie), plan0)]
    explored = 0
    while frontier:
        _, _, plan = heapq.heappop(frontier)
        steps, order, links, agenda = plan
        if not agenda:
            return plan, explored
        explored += 1
        if explored > limit:
            return None, explored
        # pick the open precondition with the fewest ways to achieve it
        def options(item):
            p, b = item
            old = [s for s, a in steps.items() if p in a.add and s != b and not before(order, b, s)]
            new = [a for a in library if p in a.add]
            return old, new
        item = min(agenda, key=lambda it: sum(map(len, options(it))))
        p, b = item
        rest = tuple(x for x in agenda if x != item)
        old, new = options(item)
        children = []
        for s in old:
            o = add_order(order, s, b)
            if o is not None:
                children.append((steps, o, links | {(s, p, b)}, rest))
        for a in new:
            sid = max(steps) + 1
            st = dict(steps)
            st[sid] = a
            o = add_order(add_order(order, START, sid) | {(sid, FINISH)}, sid, b)
            if o is not None:
                children.append((st, o, links | {(sid, p, b)}, rest + tuple((q, sid) for q in sorted(a.pre))))
        for child in children:
            for fixed in resolve(child):
                cost = len(fixed[0]) - 2 + len(fixed[3])     # steps so far + open preconditions
                heapq.heappush(frontier, (cost, next(tie), fixed))
    return None, explored


def linearizations(steps, order):
    """All total orders consistent with the partial order (fine for small plans)."""
    ids = [s for s in steps if s not in (0, 1)]
    out = []

    def go(prefix, left):
        if not left:
            out.append(prefix)
            return
        for s in sorted(left):
            if not any(before(order, t, s) for t in left if t != s):
                go(prefix + [s], left - {s})
    go([], set(ids))
    return out


def show(plan):
    steps, order, links, _ = plan
    names = {s: a.name for s, a in steps.items()}
    print("  steps:", ", ".join(f"{s}:{names[s]}" for s in sorted(steps) if s > 1))
    inner = {(a, b) for (a, b) in order if a != 0 and b != 1}
    # show only the covering pairs: a < b with no step c in between (the transitive reduction)
    direct = sorted((a, b) for (a, b) in inner
                    if not any(before(order, a, c) and before(order, c, b) for c in steps if c not in (0, 1, a, b))
                    and before(order, a, b))
    print("  orderings (covering pairs only; Start < every step < Finish):",
          ", ".join(f"{names[a]} < {names[b]}" for a, b in direct) or "none")
    print("  causal links:")
    for (a, p, b) in sorted(links, key=lambda l: (l[2], l[0], l[1])):
        print(f"    {names[a]} --{p}--> {names[b]}")


if __name__ == "__main__":
    print("1. Shoes and socks")
    lib = [act("RightSock", [], ["RightSockOn"], []), act("LeftSock", [], ["LeftSockOn"], []),
           act("RightShoe", ["RightSockOn"], ["RightShoeOn"], []), act("LeftShoe", ["LeftSockOn"], ["LeftShoeOn"], [])]
    plan, n = pop([], ["RightShoeOn", "LeftShoeOn"], lib)
    show(plan)
    lins = linearizations(plan[0], plan[1])
    print(f"  {len(lins)} total orders fit this one partial plan, e.g.",
          " / ".join(", ".join(plan[0][s].name for s in l) for l in lins[:2]))
    print(f"  ({n} partial plans explored)")
    print()

    print("2. The Sussman anomaly")
    acts = blocks_world("ABC")
    init = towers([["A", "C"], ["B"]])
    goal = ["On(A,B)", "On(B,C)"]
    plan, n = pop(init, goal, acts)
    show(plan)
    lins = linearizations(plan[0], plan[1])
    for l in lins:
        s = init
        for sid in l:
            assert plan[0][sid].pre <= s
            s = result(s, plan[0][sid])
        assert all(g in s for g in goal)
    print(f"  {len(lins)} linearization(s), all checked by simulation:")
    for l in lins:
        print("   ", ", ".join(plan[0][s].name for s in l))
    print(f"  ({n} partial plans explored)")
