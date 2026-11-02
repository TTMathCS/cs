def merge_sort(a):
    """Returns a new sorted list; a is left unchanged."""
    if len(a) <= 1:                          # 0 or 1 items: already sorted
        return a[:]
    mid = len(a) // 2
    left = merge_sort(a[:mid])               # sort each half ...
    right = merge_sort(a[mid:])
    return merge(left, right)                # ... and merge the two sorted halves


def merge(left, right):
    out = []
    i = j = 0
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:              # <= keeps equal values in order (stable)
            out.append(left[i]); i += 1
        else:
            out.append(right[j]); j += 1
    out.extend(left[i:])                     # one side is used up; copy the rest
    out.extend(right[j:])
    return out


if __name__ == "__main__":
    print(merge_sort([38, 27, 43, 3, 9, 82, 10]))
    print(merge_sort([5, 1, 4, 2, 8, 5]))
    print(merge_sort([1]))
