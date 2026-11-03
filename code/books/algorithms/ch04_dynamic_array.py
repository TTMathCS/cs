"""Chapter 4: a dynamic array built on fixed-size blocks, with its copying cost counted.

A "block" is a Python list made once with a fixed length and never resized,
standing in for the contiguous memory a real array gets from the system.
"""
import sys


class DynamicArray:
    def __init__(self, grow):
        self.grow = grow            # function: old capacity -> new capacity
        self.cap = 1
        self.n = 0
        self.block = [None] * self.cap
        self.copies = 0             # element copies made while resizing

    def append(self, x):
        if self.n == self.cap:      # full: get a bigger block and copy everything
            new_cap = self.grow(self.cap)
            new_block = [None] * new_cap
            for i in range(self.n):
                new_block[i] = self.block[i]
            self.copies += self.n
            self.block, self.cap = new_block, new_cap
        self.block[self.n] = x
        self.n += 1

    def __getitem__(self, i):
        if not 0 <= i < self.n:
            raise IndexError(i)
        return self.block[i]

    def insert(self, i, x):
        """Insert at position i by shifting a[i:] one place right: O(n - i)."""
        self.append(None)
        for j in range(self.n - 1, i, -1):
            self.block[j] = self.block[j - 1]
        self.block[i] = x


if __name__ == "__main__":
    print("Appending n items: element copies made by resizing")
    rules = [
        ("double (x2)", lambda c: 2 * c),
        ("x1.5", lambda c: max(c + 1, c * 3 // 2)),
        ("add 100", lambda c: c + 100),
    ]
    print(f"{'n':>9}" + "".join(f"{name:>16}" for name, _ in rules))
    for n in (1_000, 10_000, 100_000):
        row = f"{n:>9}"
        for name, grow in rules:
            d = DynamicArray(grow)
            for k in range(n):
                d.append(k)
            assert all(d[k] == k for k in range(0, n, 997))
            row += f"{d.copies:>10} ({d.copies / n:4.1f})"
        print(row)
    print("  (in brackets: copies per append)")

    print()
    d = DynamicArray(lambda c: 2 * c)
    for x in [10, 20, 30, 40]:
        d.append(x)
    d.insert(1, 15)
    print("insert(1, 15) into [10, 20, 30, 40] ->", [d[i] for i in range(d.n)])

    print()
    print("CPython's own list: capacity changes seen through sys.getsizeof")
    a, last, seen = [], sys.getsizeof([]), []
    ptr = 8                                    # bytes per element reference (64-bit)
    for k in range(1, 200):
        a.append(k)
        size = sys.getsizeof(a)
        if size != last:
            seen.append((len(a), (size - sys.getsizeof([])) // ptr))
            last = size
    print("  length at resize -> new capacity:", ", ".join(f"{n}->{c}" for n, c in seen))
