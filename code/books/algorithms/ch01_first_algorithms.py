"""Chapter 1: first algorithms, with their loop invariants checked as they run.

find_max, linear_search and insert_sorted each assert their invariant on
every pass of the loop, so a wrong step stops the program at once.
Then we count steps and run Euclid's algorithm with a trace.
"""
import random


def find_max(a):
    """Return the largest number in the non-empty list a."""
    best = a[0]
    for i in range(1, len(a)):
        # invariant: best is the largest of a[0..i-1]
        assert best == max(a[:i])
        if a[i] > best:
            best = a[i]
    return best


def linear_search(a, x):
    """Return the first index i with a[i] == x, or -1 if x is not in a."""
    for i in range(len(a)):
        # invariant: x is not among a[0..i-1]
        assert x not in a[:i]
        if a[i] == x:
            return i
    return -1


def insert_sorted(a, x):
    """a is sorted; put x into it so that it stays sorted (in place)."""
    a.append(x)                  # make room at the end
    j = len(a) - 1
    while j > 0 and a[j - 1] > x:
        # invariant: a[j+1..] are all > x and sorted; a[j] is the hole for x
        a[j] = a[j - 1]          # shift the bigger item one place right
        j -= 1
    a[j] = x
    return a


def find_max_counted(a):
    """find_max again, without the checks, counting comparisons a[i] > best."""
    best, comparisons = a[0], 0
    for i in range(1, len(a)):
        comparisons += 1
        if a[i] > best:
            best = a[i]
    return best, comparisons


def all_pairs_counted(a):
    """Compare every item with every other one: n(n-1)/2 comparisons."""
    comparisons = 0
    for i in range(len(a)):
        for j in range(i + 1, len(a)):
            comparisons += 1
    return comparisons


def gcd_trace(a, b):
    """Euclid's algorithm; print each step."""
    print(f"  {'a':>6} {'b':>6} {'a mod b':>8}")
    while b != 0:
        print(f"  {a:>6} {b:>6} {a % b:>8}")
        a, b = b, a % b
    print(f"  gcd = {a}")
    return a


if __name__ == "__main__":
    print("find_max([3, 41, 7, 41, 12, 5]) =", find_max([3, 41, 7, 41, 12, 5]))
    print("linear_search([8, 3, 9, 3], 3) =", linear_search([8, 3, 9, 3], 3))
    print("linear_search([8, 3, 9, 3], 5) =", linear_search([8, 3, 9, 3], 5))
    print("insert_sorted([2, 5, 8, 13], 6) =", insert_sorted([2, 5, 8, 13], 6))

    # Testing: compare with Python's own answers on many random lists.
    rng = random.Random(1)
    for trial in range(2000):
        n = rng.randint(1, 12)
        a = [rng.randint(-20, 20) for _ in range(n)]
        x = rng.randint(-20, 20)
        assert find_max(a) == max(a)
        assert linear_search(a, x) == (a.index(x) if x in a else -1)
        s = sorted(a)
        assert insert_sorted(s[:], x) == sorted(s + [x])
    print("2000 random tests passed")

    print()
    print(f"{'n':>9} {'find_max':>10} {'all pairs':>16}")
    for n in (10, 1000):
        a = [rng.random() for _ in range(n)]
        print(f"{n:>9} {find_max_counted(a)[1]:>10} {all_pairs_counted(a):>16}")
    n = 10**6
    a = [rng.random() for _ in range(n)]
    # all pairs for a million items would take hours in Python: use the formula
    print(f"{n:>9} {find_max_counted(a)[1]:>10} {n * (n - 1) // 2:>16}  (formula)")

    print()
    print("Euclid on 1071 and 462:")
    gcd_trace(1071, 462)
