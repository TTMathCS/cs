"""Chapter 12: greedy coin change, activity selection, minimising lateness."""
from itertools import permutations


def greedy_coins(amount, coins):
    """Always take the largest coin that fits."""
    used = []
    for c in sorted(coins, reverse=True):
        while amount >= c:
            amount -= c
            used.append(c)
    return used if amount == 0 else None


def fewest_coins(amount, coins):
    """The true optimum, by dynamic programming (chapter 13)."""
    best = [0] + [None] * amount
    for v in range(1, amount + 1):
        options = [best[v - c] for c in coins if c <= v and best[v - c] is not None]
        best[v] = min(options) + 1 if options else None
    return best[amount]


def first_counterexample(coins):
    # Kozen and Zaks (1994): if greedy ever fails, it fails below the sum of the two largest coins
    big = sorted(coins)
    limit = big[-1] + big[-2]
    for v in range(1, limit):
        g = greedy_coins(v, coins)
        if g is not None and len(g) != fewest_coins(v, coins):
            return v, g
    return None


def select_activities(acts):
    """Earliest finish time first. acts: list of (name, start, finish)."""
    chosen, last_finish = [], float("-inf")
    for name, s, f in sorted(acts, key=lambda a: a[2]):
        if s >= last_finish:           # compatible with everything chosen so far
            chosen.append(name)
            last_finish = f
    return chosen


def max_lateness(order):
    t, worst = 0, 0
    for name, length, deadline in order:
        t += length
        worst = max(worst, t - deadline)
    return worst


def earliest_deadline_first(jobs):
    return sorted(jobs, key=lambda j: j[2])


if __name__ == "__main__":
    for coins in ([25, 10, 5, 1], [4, 3, 1], [25, 10, 1], [1, 2, 5, 10, 20, 50, 100, 200]):
        bad = first_counterexample(coins)
        if bad:
            v, g = bad
            print(f"coins {coins}: greedy fails first at {v}: {g} ({len(g)} coins) "
                  f"but {fewest_coins(v, coins)} suffice")
        else:
            big = sorted(coins)
            print(f"coins {coins}: greedy optimal below {big[-1] + big[-2]}, so for every amount")

    acts = [("a", 1, 4), ("b", 3, 5), ("c", 0, 6), ("d", 5, 7), ("e", 3, 9), ("f", 5, 9),
            ("g", 6, 10), ("h", 8, 11), ("i", 8, 12), ("j", 2, 14), ("k", 12, 16)]
    print("\nactivities chosen by earliest finish:", select_activities(acts))

    jobs = [("j4", 4, 9), ("j1", 3, 6), ("j6", 2, 15), ("j3", 1, 9), ("j5", 3, 14), ("j2", 2, 8)]
    edf = earliest_deadline_first(jobs)
    print("\njobs (name, length, deadline):", jobs)
    print("earliest deadline first:", [j[0] for j in edf], " max lateness:", max_lateness(edf))
    best = min(permutations(jobs), key=max_lateness)
    print("best of all 720 orders: max lateness", max_lateness(best))
    shortest = sorted(jobs, key=lambda j: j[1])
    print("shortest job first:", [j[0] for j in shortest], " max lateness:", max_lateness(shortest))
