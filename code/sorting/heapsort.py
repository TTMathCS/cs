def heapsort(a):
    """Sorts the list a in place, smallest first, using a max-heap stored in a itself."""
    n = len(a)
    for i in range(n // 2 - 1, -1, -1):      # build the heap: sift down every parent, last first
        sift_down(a, i, n)
    for end in range(n - 1, 0, -1):
        a[0], a[end] = a[end], a[0]          # the largest goes to the back ...
        sift_down(a, 0, end)                 # ... and the heap shrinks by one
    return a


def sift_down(a, i, n):
    """Moves a[i] down until both children are smaller (only a[:n] is the heap)."""
    while True:
        big = i
        left, right = 2 * i + 1, 2 * i + 2
        if left < n and a[left] > a[big]:
            big = left
        if right < n and a[right] > a[big]:
            big = right
        if big == i:
            return
        a[i], a[big] = a[big], a[i]
        i = big


if __name__ == "__main__":
    print(heapsort([4, 10, 3, 5, 1]))
    print(heapsort([38, 27, 43, 3, 9, 82, 10]))
    print(heapsort([7, 7, 1]))
