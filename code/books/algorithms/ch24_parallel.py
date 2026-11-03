# Chapter 24: parallel algorithms in the work-span model.
# Blelloch's prefix sum as a DAG of tasks, a greedy scheduler that checks
# Brent's bound T_p <= W/p + S, and a word count in the MapReduce style.
from collections import defaultdict
import random


def scan_dag(n):
    """Exclusive prefix sum of n = 2^d numbers (Blelloch 1990), as a task graph.
    Returns tasks {name: list of tasks it waits for} and the computed result."""
    x = list(range(1, n + 1))
    a = x[:]
    deps, last = {}, {i: None for i in range(n)}      # last task that wrote a[i]

    def task(name, cells):
        deps[name] = sorted({last[c] for c in cells if last[c] is not None})
        for c in cells:
            last[c] = name

    d, step = 1, 0
    while d < n:                                    # up-sweep: build partial sums
        for i in range(2 * d - 1, n, 2 * d):
            a[i] += a[i - d]
            task(("up", d, i), [i - d, i])
        d *= 2
    a[n - 1] = 0
    task(("clear",), [n - 1])
    d = n // 2
    while d >= 1:                                   # down-sweep: push sums down
        for i in range(2 * d - 1, n, 2 * d):
            a[i - d], a[i] = a[i], a[i] + a[i - d]
            task(("down", d, i), [i - d, i])
        d //= 2
    expected = [sum(x[:i]) for i in range(n)]
    assert a == expected
    return deps


def work_and_span(deps):
    depth = {}
    for t in deps:                                  # tasks were created in a valid order
        depth[t] = 1 + max((depth[u] for u in deps[t]), default=0)
    return len(deps), max(depth.values())


def greedy_schedule(deps, p):
    """Each step, run up to p tasks whose inputs are ready."""
    done, steps, remaining = set(), 0, dict(deps)
    while remaining:
        ready = [t for t, ds in remaining.items() if all(u in done for u in ds)]
        for t in ready[:p]:
            del remaining[t]
        done.update(ready[:p])
        steps += 1
    return steps


print("Blelloch scan: work W, span S, and greedy time T_p on p processors")
for n in (16, 256, 1024):
    deps = scan_dag(n)
    W, S = work_and_span(deps)
    row = []
    for p in (1, 4, 16, 64):
        Tp = greedy_schedule(deps, p)
        assert Tp <= W / p + S
        row.append(f"T_{p}={Tp} (bound {W / p + S:.0f})")
    print(f"  n={n:5d}: W={W:5d}, S={S:3d};  " + ", ".join(row))
print()

# MapReduce word count, simulated: map -> shuffle by hash(key) % R -> reduce
docs = [
    "red planet red dust",
    "dust storm on the red planet",
    "the rover drives on",
    "storm over the rover",
]


def map_fn(doc):
    return [(word, 1) for word in doc.split()]


def reduce_fn(word, counts):
    return word, sum(counts)


R = 2
partitions = [defaultdict(list) for _ in range(R)]
for doc in docs:                                    # each doc could be a different machine
    for key, value in map_fn(doc):
        partitions[sum(map(ord, key)) % R][key].append(value)   # a fixed, simple hash
for r in range(R):
    result = sorted(reduce_fn(w, c) for w, c in partitions[r].items())
    print(f"reducer {r}: {result}")
