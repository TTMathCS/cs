def radix_sort(a):
    """Returns a sorted copy of a list of non-negative whole numbers (LSD radix sort, base 10)."""
    out = a[:]
    biggest = max(out, default=0)
    place = 1
    while biggest // place > 0:              # one pass per digit, ones first
        out = sort_by_digit(out, place)
        place *= 10
    return out


def sort_by_digit(a, place):
    """A stable counting sort on one decimal digit."""
    count = [0] * 10
    for x in a:
        count[(x // place) % 10] += 1
    for d in range(1, 10):
        count[d] += count[d - 1]
    out = [0] * len(a)
    for x in reversed(a):                    # from the back keeps it stable, which radix sort needs
        d = (x // place) % 10
        count[d] -= 1
        out[count[d]] = x
    return out


if __name__ == "__main__":
    print(radix_sort([170, 45, 75, 90, 802, 24, 2, 66]))
    print(radix_sort([329, 457, 657, 839, 436, 720, 355]))
    print(radix_sort([5, 0, 5]))
