def counting_sort(a, k):
    """Returns a sorted copy of a, whose values are whole numbers from 0 to k. Stable."""
    count = [0] * (k + 1)
    for x in a:                              # 1. count each value
        count[x] += 1
    for v in range(1, k + 1):                # 2. running totals: count[v] = how many values are <= v
        count[v] += count[v - 1]
    out = [0] * len(a)
    for x in reversed(a):                    # 3. place from the back, so equal values keep their order
        count[x] -= 1
        out[count[x]] = x
    return out


if __name__ == "__main__":
    print(counting_sort([2, 5, 3, 0, 2, 3, 0, 3], 5))
    print(counting_sort([4, 1, 3, 4, 3], 4))
    print(counting_sort([0], 0))
