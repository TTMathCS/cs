def selection_sort(a):
    """Sorts the list a in place, smallest first."""
    n = len(a)
    for i in range(n - 1):
        smallest = i                         # find the smallest value in a[i:]
        for j in range(i + 1, n):
            if a[j] < a[smallest]:
                smallest = j
        a[i], a[smallest] = a[smallest], a[i]  # put it at position i: a[:i+1] is now final
    return a


if __name__ == "__main__":
    print(selection_sort([64, 25, 12, 22, 11]))
    print(selection_sort([38, 27, 43, 3, 9, 82, 10]))
    print(selection_sort([2, 1]))
