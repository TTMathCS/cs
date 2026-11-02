def bubble_sort(a):
    """Sorts the list a in place, smallest first."""
    n = len(a)
    for end in range(n - 1, 0, -1):          # after each pass, a[end] is in its final place
        swapped = False
        for i in range(end):
            if a[i] > a[i + 1]:              # neighbours in the wrong order: swap them
                a[i], a[i + 1] = a[i + 1], a[i]
                swapped = True
        if not swapped:                      # a whole pass with no swap: already sorted
            break
    return a


if __name__ == "__main__":
    print(bubble_sort([5, 1, 4, 2, 8]))
    print(bubble_sort([38, 27, 43, 3, 9, 82, 10]))
    print(bubble_sort([1, 2, 3]))
