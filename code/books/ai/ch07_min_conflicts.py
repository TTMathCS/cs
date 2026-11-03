# Chapter 7: min-conflicts local search for n-queens (Minton, Johnston, Philips and Laird 1992).
# One queen per column; row[c] is its row. Counts of queens per row and per diagonal make the
# number of conflicts of any square a constant-time lookup (and a NumPy vector for a whole column).
import numpy as np


def min_conflicts(n, rng, max_steps=100000, tries=50):
    row = np.empty(n, dtype=np.int64)
    rows = np.zeros(n, dtype=np.int64)
    up = np.zeros(2 * n, dtype=np.int64)          # index r - c + n
    down = np.zeros(2 * n, dtype=np.int64)        # index r + c

    # Greedy start: for each column, try up to `tries` rows not yet used by any queen,
    # and keep the first one with no diagonal conflict (or the best one tried).
    free = list(range(n))                          # rows with no queen yet
    for c in range(n):
        best_i, best_k = 0, None
        for _ in range(min(tries, len(free))):
            i = int(rng.integers(len(free)))
            r = free[i]
            k = up[r - c + n] + down[r + c]
            if best_k is None or k < best_k:
                best_i, best_k = i, k
                if k == 0:
                    break
        r = free[best_i]
        free[best_i] = free[-1]                    # remove row r from the free list in O(1)
        free.pop()
        row[c] = r
        rows[r] += 1
        up[r - c + n] += 1
        down[r + c] += 1

    cols = np.arange(n)
    all_rows = np.arange(n)
    for step in range(max_steps):
        conf = rows[row] + up[row - cols + n] + down[row + cols] - 3   # other queens attacking each queen
        bad = np.flatnonzero(conf)
        if step == 0:
            start_bad = bad.size
        if bad.size == 0:
            return row, step, start_bad
        c = rng.choice(bad)                                       # a random conflicted queen
        r0 = row[c]
        rows[r0] -= 1                                              # lift it off the board
        up[r0 - c + n] -= 1
        down[r0 + c] -= 1
        k = rows + up[all_rows - c + n] + down[all_rows + c]      # conflicts of every square in column c
        best = np.flatnonzero(k == k.min())
        r = rng.choice(best)                                      # least conflicts, ties at random
        row[c] = r
        rows[r] += 1
        up[r - c + n] += 1
        down[r + c] += 1
    return None, max_steps, start_bad


def check(row):
    n = len(row)
    return (len(set(row.tolist())) == n and len(set((row - np.arange(n)).tolist())) == n
            and len(set((row + np.arange(n)).tolist())) == n)


print("       n   conflicted queens after greedy start   repair steps   solved")
for n in (8, 100, 1000, 10000, 100000):
    sol, steps, start_bad = min_conflicts(n, np.random.default_rng(n))
    print(f"{n:8d}   {start_bad:36d}   {steps:12d}   {sol is not None and check(sol)}")

for n in (8, 1000):
    runs = [min_conflicts(n, np.random.default_rng(seed), max_steps=1000) for seed in range(20)]
    ok = sorted(r[1] for r in runs if r[0] is not None)
    print(f"n = {n:4d}, 20 seeds, at most 1000 repairs: solved {len(ok)}/20, repair steps when solved: "
          f"median {ok[len(ok) // 2]}, max {ok[-1]}")
