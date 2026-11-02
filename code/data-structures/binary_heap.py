class MinHeap:
    """A min-heap in a list: a[0] is the smallest; the children of i are 2i+1 and 2i+2."""
    def __init__(self):
        self.a = []

    def push(self, x):
        a = self.a
        a.append(x)                          # put it at the bottom ...
        i = len(a) - 1
        while i > 0:                         # ... and sift it up while it beats its parent
            parent = (i - 1) // 2
            if a[parent] <= a[i]:
                break
            a[parent], a[i] = a[i], a[parent]
            i = parent

    def pop(self):
        a = self.a
        top = a[0]
        last = a.pop()
        if a:
            a[0] = last                      # move the last value to the root ...
            i, n = 0, len(a)
            while True:                      # ... and sift it down below smaller children
                small, l, r = i, 2 * i + 1, 2 * i + 2
                if l < n and a[l] < a[small]:
                    small = l
                if r < n and a[r] < a[small]:
                    small = r
                if small == i:
                    break
                a[i], a[small] = a[small], a[i]
                i = small
        return top

    def peek(self):
        return self.a[0]

    def __len__(self):
        return len(self.a)


if __name__ == "__main__":
    h = MinHeap()
    for x in [5, 3, 8, 1, 9, 2, 7]:
        h.push(x)
    print(h.a)                               # the heap as stored
    print([h.pop() for _ in range(len(h))])  # comes out sorted
    # the 3 largest of a stream, keeping only 3 values in memory
    top = MinHeap()
    for x in [12, 3, 45, 7, 33, 21, 9, 40]:
        top.push(x)
        if len(top) > 3:
            top.pop()                        # drop the smallest of the 4
    print(sorted(top.a, reverse=True))
