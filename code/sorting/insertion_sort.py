def insertion_sort(a):
    """Sorts the list a in place, smallest first."""
    for i in range(1, len(a)):
        key = a[i]                           # a[:i] is sorted; insert a[i] into it
        j = i - 1
        while j >= 0 and a[j] > key:         # shift bigger values one place right
            a[j + 1] = a[j]
            j -= 1
        a[j + 1] = key                       # drop the key into the gap
    return a


if __name__ == "__main__":
    print(insertion_sort([12, 11, 13, 5, 6]))
    print(insertion_sort([38, 27, 43, 3, 9, 82, 10]))
    print(insertion_sort([]))
