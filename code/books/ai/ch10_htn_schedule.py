# Chapter 10: hierarchical task networks and scheduling with resources.
# 1. A total-order HTN planner (in the style of SHOP): compound tasks are refined by methods, in order, while the
#    state is tracked; primitive tasks are the STRIPS actions of the rover domain in ch10_strips.py.
# 2. Scheduling: the critical path method (earliest and latest start times, slack), then a power limit that turns
#    the problem into resource-constrained scheduling, solved by a priority-list heuristic.
#    The durations and power numbers are invented for the example.
from collections import deque
from ch10_strips import rover_domain, result, forward, h_add

ACTS, INIT, GOAL = rover_domain()
BY_NAME = {a.name: a for a in ACTS}
LINKS = {}
for a in ACTS:
    if a.name.startswith("Drive("):
        x, y = a.name[6:-1].split(",")
        LINKS.setdefault(x, []).append(y)


def distance(src, dst):
    q, d = deque([src]), {src: 0}
    while q:
        x = q.popleft()
        for y in LINKS[x]:
            if y not in d:
                d[y] = d[x] + 1
                q.append(y)
    return d[dst]


def where(s):
    return next(p[3:-1] for p in s if p.startswith("At("))


# Methods: task name -> function(state, args) returning a list of alternative subtask lists (tried in order).
def m_day(s):
    return [[("Collect", "Ridge"), ("Collect", "Delta"), ("Photograph", "Delta"), ("Photograph", "Fan"),
             ("Downlink", "Delta"), ("Downlink", "Fan"), ("GoTo", "Base")]]


def m_collect(s, p):
    return [[("GoTo", p), ("!Sample", p), ("!Cache", p)]]


def m_photograph(s, p):
    if "CameraOn" in s:
        return [[("GoTo", p), ("!Image", p)]]
    return [[("!CameraOn",), ("GoTo", p), ("!Image", p)]]


def m_downlink(s, p):
    if "AntennaReady" in s:
        return [[("!Send", p)]]
    if "CameraOn" in s:
        return [[("!CameraOff",), ("!DeployAntenna",), ("!Send", p)]]
    return [[("!DeployAntenna",), ("!Send", p)]]


def m_goto(s, p):
    here = where(s)
    if here == p:
        return [[]]
    # expert knowledge in the method: drive to a neighbour that is closer to the destination
    steps = sorted(LINKS[here], key=lambda y: distance(y, p))
    return [[("!Drive", here, y), ("GoTo", p)] for y in steps if distance(y, p) < distance(here, p)]


METHODS = {"Day": m_day, "Collect": m_collect, "Photograph": m_photograph, "Downlink": m_downlink, "GoTo": m_goto}


def primitive(task):
    name, *args = task
    return BY_NAME[f"{name[1:]}({','.join(args)})" if args else name[1:]]


def htn_run(s, tasks, depth=0, tree=None):
    """Refine the task list left to right, tracking the state. Returns (plan, final state) or None.
    The decomposition is recorded in tree; "<end>" markers only restore the indentation of the printout."""
    if tasks and tasks[0][0] == "<end>":
        return htn_run(s, tasks[1:], tasks[0][1], tree)
    if not tasks:
        return [], s
    task, rest = tasks[0], tasks[1:]
    if task[0].startswith("!"):
        a = primitive(task)
        if not a.pre <= s:
            return None
        tree.append("  " * depth + a.name)
        r = htn_run(result(s, a), rest, depth, tree)
        if r is None:
            tree.pop()
            return None
        return [a.name] + r[0], r[1]
    for sub in METHODS[task[0]](s, *task[1:]):
        mark = len(tree)
        tree.append("  " * depth + f"{task[0]}({','.join(task[1:])})")
        r = htn_run(s, list(sub) + [("<end>", depth)] + rest, depth + 1, tree)
        if r is not None:
            return r
        del tree[mark:]
    return None


# ---------------------------------------------------------------- scheduling
JOBS = {   # name: (duration in minutes, power in watts, predecessors)
    "Warm up":        (30, 40, []),
    "Drive to Delta": (90, 120, ["Warm up"]),
    "Panorama":       (40, 30, ["Warm up"]),
    "Arm unstow":     (15, 50, ["Drive to Delta"]),
    "Abrade rock":    (30, 110, ["Arm unstow"]),
    "Spectrometer":   (60, 40, ["Abrade rock"]),
    "Drill core":     (50, 130, ["Abrade rock"]),
    "Close-up image": (20, 30, ["Abrade rock"]),
    "Seal tube":      (25, 60, ["Drill core"]),
    "Downlink":       (30, 70, ["Panorama", "Spectrometer", "Close-up image"]),
}


def cpm(jobs):
    order, seen = [], set()

    def visit(j):
        if j not in seen:
            seen.add(j)
            for p in jobs[j][2]:
                visit(p)
            order.append(j)
    for j in jobs:
        visit(j)
    es = {}
    for j in order:
        es[j] = max((es[p] + jobs[p][0] for p in jobs[j][2]), default=0)
    makespan = max(es[j] + jobs[j][0] for j in jobs)
    ls = {}
    for j in reversed(order):
        succ = [k for k in jobs if j in jobs[k][2]]
        ls[j] = min((ls[k] for k in succ), default=makespan) - jobs[j][0]
    return es, ls, makespan, order


def list_schedule(jobs, power_cap, priority):
    """Serial schedule generation: take jobs in priority order (predecessors first) and start each at the earliest
    minute when its predecessors are done and the power in use stays under the cap for its whole duration."""
    start, usage = {}, {}
    pending = sorted(jobs, key=priority)
    while pending:
        j = next(x for x in pending if all(p in start for p in jobs[x][2]))
        d, w, preds = jobs[j]
        t = max((start[p] + jobs[p][0] for p in preds), default=0)
        while any(usage.get(m, 0) + w > power_cap for m in range(t, t + d)):
            t += 1
        start[j] = t
        for m in range(t, t + d):
            usage[m] = usage.get(m, 0) + w
        pending.remove(j)
    return start, max(start[j] + jobs[j][0] for j in jobs), max(usage.values())


if __name__ == "__main__":
    print("1. HTN planning: decompose Day into primitive actions")
    tree = []
    plan, final = htn_run(INIT, [("Day",)], 0, tree)
    for line in tree:
        print("  " + line)
    print(f"  {len(plan)} primitive actions; goal reached: {GOAL <= final}")
    best, _ = forward(INIT, GOAL, ACTS, h_add)
    print(f"  (an optimal plan from search has {len(best)} actions)")
    print()

    print("2. Critical path method (no resource limits)")
    es, ls, makespan, order = cpm(JOBS)
    print(f"  {'job':<16} {'dur':>4} {'watts':>5} {'earliest':>8} {'latest':>6} {'slack':>5}")
    for j in order:
        d, w, _ = JOBS[j]
        print(f"  {j:<16} {d:4d} {w:5d} {es[j]:8d} {ls[j]:6d} {ls[j] - es[j]:5d}{'  critical' if ls[j] == es[j] else ''}")
    print(f"  makespan {makespan} minutes")
    _, _, peak = list_schedule(JOBS, 10**9, lambda j: es[j])
    print(f"  peak power if every job starts as early as possible: {peak} W")
    print()

    print("3. With a power cap (resource-constrained scheduling, priority = least slack first)")
    for cap in (250, 200, 160, 130):
        start, span, peak = list_schedule(JOBS, cap, lambda j: (ls[j] - es[j], es[j]))
        moved = [j for j in JOBS if start[j] != es[j]]
        print(f"  cap {cap:3d} W: makespan {span:3d} min, peak {peak:3d} W, delayed: {', '.join(moved) or 'none'}")
