"""Chapter 7, part 1: linear search, binary search (and its classic bugs), exponential search,
and binary search on the answer."""
import bisect
import math
import random


def linear_search(a, x):
    for i, v in enumerate(a):
        if v == x:
            return i
    return -1


def lower_bound(a, x):
    """First index i with a[i] >= x (len(a) if none).  Invariant: a[:lo] < x <= a[hi:]."""
    lo, hi, probes = 0, len(a), 0
    while lo < hi:
        mid = (lo + hi) // 2
        probes += 1
        if a[mid] < x:
            lo = mid + 1          # a[mid] < x, so everything up to mid is < x
        else:
            hi = mid              # a[mid] >= x, so everything from mid on is >= x
    return lo, probes


def binary_search(a, x):
    i, probes = lower_bound(a, x)
    return (i if i < len(a) and a[i] == x else -1), probes


def buggy_search(a, x, max_steps=100):
    """A common wrong version: 'lo = mid' instead of 'lo = mid + 1'."""
    lo, hi, steps = 0, len(a) - 1, 0
    while lo < hi:
        steps += 1
        if steps > max_steps:
            return f"stuck: lo = {lo}, hi = {hi} forever"
        mid = (lo + hi) // 2
        if a[mid] < x:
            lo = mid              # BUG: when hi = lo + 1, mid = lo and nothing changes
        else:
            hi = mid
    return lo


def exponential_search(a, x):
    """Find lower_bound when the answer is near the start: probe 1, 2, 4, 8, ... then binary search."""
    if not a or a[0] >= x:
        return 0, 1
    bound, probes = 1, 1
    while bound < len(a) and a[bound] < x:
        bound *= 2
        probes += 1
    lo, hi = bound // 2 + 1, min(bound, len(a))   # a[bound // 2] < x <= a[hi] (or hi = len)
    while lo < hi:
        mid = (lo + hi) // 2
        probes += 1
        if a[mid] < x:
            lo = mid + 1
        else:
            hi = mid
    return lo, probes


def isqrt(n):
    """Largest r with r*r <= n, by binary search on the answer."""
    lo, hi = 0, n + 1                 # invariant: lo*lo <= n < hi*hi
    while hi - lo > 1:
        mid = (lo + hi) // 2
        if mid * mid <= n:
            lo = mid
        else:
            hi = mid
    return lo


def sols_needed(legs, limit):
    """Greedy: how many sols to drive the legs in order if a rover drives at most `limit` metres per sol."""
    sols, today = 1, 0
    for d in legs:
        if today + d > limit:
            sols, today = sols + 1, 0
        today += d
    return sols


def min_daily_limit(legs, days):
    """Smallest daily limit that finishes within `days` sols.  sols_needed is monotone in the limit."""
    lo, hi = max(legs), sum(legs)      # lo might work; hi certainly works
    while lo < hi:
        mid = (lo + hi) // 2
        if sols_needed(legs, mid) <= days:
            hi = mid
        else:
            lo = mid + 1
    return lo


def main():
    rng = random.Random(7)
    a = sorted(rng.sample(range(1000), 100))

    for _ in range(2000):
        x = rng.randrange(-5, 1005)
        assert lower_bound(a, x)[0] == bisect.bisect_left(a, x)
        assert exponential_search(a, x)[0] == bisect.bisect_left(a, x)
        assert (binary_search(a, x)[0] >= 0) == (x in a)
    print("lower_bound and exponential_search agree with bisect.bisect_left on 2000 queries")

    small = [3, 8, 15, 21, 30, 42, 57]
    print("\nbinary search trace in", small, "for 42:")
    lo, hi = 0, len(small)
    while lo < hi:
        mid = (lo + hi) // 2
        go = "right" if small[mid] < 42 else "left"
        print(f"  lo={lo} hi={hi} mid={mid} a[mid]={small[mid]:2d} -> {go}")
        if small[mid] < 42:
            lo = mid + 1
        else:
            hi = mid
    print(f"  stop: lo = hi = {lo}, a[{lo}] = {small[lo]}")

    print("\nthe 'lo = mid' bug, searching", small, "for 57:", buggy_search(small, 57))

    n = 10**6
    big = list(range(0, 2 * n, 2))
    worst = max(binary_search(big, x)[1] for x in [0, 1, 2 * n - 2, 2 * n, 777777, 777778])
    print(f"\nbinary search in {n} items: at most {worst} probes; ceil(log2(n+1)) = {math.ceil(math.log2(n + 1))}")
    print("linear search for the last item:", linear_search(big, 2 * n - 2) + 1, "probes")
    for target_index in [3, 100, 10000, 900000]:
        x = big[target_index]
        print(f"  item at index {target_index:6d}: binary {binary_search(big, x)[1]:2d} probes, "
              f"exponential {exponential_search(big, x)[1]:2d} probes")

    print("\nbinary search on the answer")
    for m in [0, 1, 15, 16, 10**12 + 7]:
        assert isqrt(m) ** 2 <= m < (isqrt(m) + 1) ** 2
    print("  isqrt(10**12 + 7) =", isqrt(10**12 + 7))
    legs = [400, 250, 600, 150, 300, 500, 200, 350]     # metres between waypoints, in order
    for days in [1, 2, 3, 4, 8]:
        L = min_daily_limit(legs, days)
        assert sols_needed(legs, L) <= days and (L == max(legs) or sols_needed(legs, L - 1) > days)
        print(f"  {days} sols: drive at most {L} m per sol")


if __name__ == "__main__":
    main()
