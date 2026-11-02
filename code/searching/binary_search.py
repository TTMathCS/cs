def binary_search(a, target):
    """Returns an index of target in the sorted list a, or -1 if it is not there."""
    lo, hi = 0, len(a) - 1                   # the target, if present, is in a[lo..hi]
    while lo <= hi:
        mid = lo + (hi - lo) // 2
        if a[mid] == target:
            return mid
        if a[mid] < target:
            lo = mid + 1                     # everything up to mid is too small
        else:
            hi = mid - 1                     # everything from mid on is too big
    return -1


def lower_bound(a, target):
    """Returns the first index i with a[i] >= target (len(a) if there is none)."""
    lo, hi = 0, len(a)                       # the answer is in [lo, hi]
    while lo < hi:
        mid = lo + (hi - lo) // 2
        if a[mid] < target:
            lo = mid + 1
        else:
            hi = mid
    return lo


if __name__ == "__main__":
    a = [2, 5, 8, 12, 16, 23, 38, 56, 72, 91]
    print(binary_search(a, 23), binary_search(a, 2), binary_search(a, 91), binary_search(a, 7))
    b = [1, 3, 3, 3, 7, 9]
    print(lower_bound(b, 3), lower_bound(b, 4), lower_bound(b, 0), lower_bound(b, 10))
    print(lower_bound(b, 4) - lower_bound(b, 3))   # how many 3s
