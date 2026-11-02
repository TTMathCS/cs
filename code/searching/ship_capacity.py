def days_needed(weights, capacity):
    """Loads packages in order onto one ship per day; returns how many days that takes."""
    days, load = 1, 0
    for w in weights:
        if load + w > capacity:              # this package does not fit today: start a new day
            days += 1
            load = 0
        load += w
    return days


def min_capacity(weights, d):
    """The smallest ship capacity that moves every package, in order, within d days."""
    lo, hi = max(weights), sum(weights)      # lo is too small or just right; hi always works
    while lo < hi:
        mid = (lo + hi) // 2
        if days_needed(weights, mid) <= d:   # mid works, so the answer is mid or smaller
            hi = mid
        else:                                # mid fails, so the answer is bigger
            lo = mid + 1
    return lo


def isqrt(n):
    """The largest whole number r with r * r <= n."""
    lo, hi = 0, n
    while lo < hi:
        mid = (lo + hi + 1) // 2             # round up, so lo = mid always makes progress
        if mid * mid <= n:
            lo = mid
        else:
            hi = mid - 1
    return lo


if __name__ == "__main__":
    print(min_capacity([1, 2, 3, 4, 5, 6, 7, 8, 9, 10], 5))
    print(min_capacity([3, 2, 2, 4, 1, 4], 3))
    print(min_capacity([1, 2, 3, 1, 1], 4))
    print(isqrt(0), isqrt(15), isqrt(16), isqrt(1000000007))
