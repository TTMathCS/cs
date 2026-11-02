def pair_with_sum(a, target):
    """In the sorted list a, finds positions i < j with a[i] + a[j] == target, or None."""
    i, j = 0, len(a) - 1
    while i < j:
        s = a[i] + a[j]
        if s == target:
            return (i, j)
        if s < target:
            i += 1                           # need a bigger sum: move the left pointer right
        else:
            j -= 1                           # need a smaller sum: move the right pointer left
    return None


def remove_duplicates(a):
    """Removes repeats from the sorted list a in place; returns the new length."""
    if not a:
        return 0
    write = 1                                # a[:write] holds the distinct values so far
    for read in range(1, len(a)):
        if a[read] != a[write - 1]:
            a[write] = a[read]
            write += 1
    del a[write:]
    return write


def max_water(h):
    """Two walls of heights h[i], h[j] hold (j - i) * min(h[i], h[j]) water; returns the most."""
    i, j, best = 0, len(h) - 1, 0
    while i < j:
        best = max(best, (j - i) * min(h[i], h[j]))
        if h[i] < h[j]:                      # the shorter wall limits us: only moving it can help
            i += 1
        else:
            j -= 1
    return best


if __name__ == "__main__":
    print(pair_with_sum([1, 2, 4, 7, 11, 15], 15))
    print(pair_with_sum([1, 2, 4, 7, 11, 15], 10))
    a = [1, 1, 2, 3, 3, 3, 4]
    print(remove_duplicates(a), a)
    print(max_water([1, 8, 6, 2, 5, 4, 8, 3, 7]))
