import random


def quicksort(a, lo=0, hi=None):
    """Sorts a[lo..hi] in place (both ends included), smallest first."""
    if hi is None:
        hi = len(a) - 1
    if lo >= hi:
        return a
    p = partition(a, lo, hi)                 # a[p] is now in its final place
    quicksort(a, lo, p - 1)                  # sort what is smaller ...
    quicksort(a, p + 1, hi)                  # ... and what is larger
    return a


def partition(a, lo, hi):
    """Lomuto partition: uses a[hi] as the pivot, returns where the pivot ends up."""
    pivot = a[hi]
    i = lo                                   # a[lo..i-1] holds values < pivot
    for j in range(lo, hi):
        if a[j] < pivot:
            a[i], a[j] = a[j], a[i]
            i += 1
    a[i], a[hi] = a[hi], a[i]                # pivot goes between the two parts
    return i


def quicksort_random(a):
    """The safe version: a random pivot makes the slow O(n^2) case vanishingly unlikely."""
    def go(lo, hi):
        if lo >= hi:
            return
        r = random.randint(lo, hi)
        a[r], a[hi] = a[hi], a[r]            # move a random value into the pivot slot
        p = partition(a, lo, hi)
        go(lo, p - 1)
        go(p + 1, hi)
    go(0, len(a) - 1)
    return a


if __name__ == "__main__":
    print(quicksort([10, 80, 30, 90, 40, 50, 70]))
    print(quicksort([38, 27, 43, 3, 9, 82, 10]))
    print(quicksort_random([5, 1, 4, 2, 8, 5, 5]))
