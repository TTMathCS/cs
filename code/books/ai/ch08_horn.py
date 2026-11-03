# Chapter 8: forward and backward chaining on definite clauses (Horn clauses with exactly one positive literal).
from collections import deque

# A rover's knowledge base. Each rule is (premises, conclusion); facts have no premises.
RULES = [
    (["Sunny"], "SolarOK"),
    (["SolarOK", "BatteryOK"], "PowerOK"),
    (["PowerOK", "LinkUp"], "CanSend"),
    (["PowerOK", "AtRock"], "CanDrill"),
    (["CanDrill", "ArmOK"], "SampleTaken"),
    (["SampleTaken", "CanSend"], "MissionDone"),
    (["CanSend"], "LinkUp"),                   # a circular rule: true but useless on its own
]
FACTS = ["Sunny", "BatteryOK", "AtRock", "ArmOK"]


def forward_chaining(rules, facts, query):
    """The linear-time algorithm: count[i] = premises of rule i not yet known; fire a rule when it reaches 0."""
    count = [len(p) for p, _ in rules]
    uses = {}                                    # symbol -> rules in which it is a premise
    for i, (prem, _) in enumerate(rules):
        for p in prem:
            uses.setdefault(p, []).append(i)
    inferred, agenda, order, work = set(), deque(facts), [], 0
    while agenda:
        p = agenda.popleft()
        if p in inferred:
            continue
        inferred.add(p)
        order.append(p)
        if p == query:
            return True, order, work
        for i in uses.get(p, []):
            work += 1
            count[i] -= 1
            if count[i] == 0:
                agenda.append(rules[i][1])
    return False, order, work


def backward_chaining(rules, facts, query):
    """Depth-first: to prove q, find a rule concluding q and prove its premises. Goals on the current path are
    not tried again (that would loop), and proved or failed goals are remembered."""
    known, failed, trace = set(facts), set(), []

    def prove(q, path, depth):
        trace.append("  " * depth + q)
        if q in known:
            return True
        if q in failed or q in path:
            return False
        for prem, concl in rules:
            if concl == q and all(prove(p, path | {q}, depth + 1) for p in prem):
                known.add(q)
                return True
        if not path:
            failed.add(q)
        return False

    return prove(query, frozenset(), 0), trace


for q in ("SampleTaken", "MissionDone"):
    ok, order, work = forward_chaining(RULES, FACTS, q)
    print(f"forward chaining, query {q}: {ok}; symbols inferred in order: {order}; premise counts updated: {work}")
print()
for q in ("SampleTaken", "MissionDone"):
    ok, trace = backward_chaining(RULES, FACTS, q)
    print(f"backward chaining, query {q}: {ok}; goals tried:")
    print("\n".join(trace))
