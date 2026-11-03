"""Chapter 6, part 1: sorting without comparing. Counting sort, LSD and MSD radix sort, bucket sort."""
import random


def counting_sort(a, k, key=lambda x: x):
    """Stable sort of a by key(x), an integer in 0..k-1.  Time O(n + k)."""
    count = [0] * k
    for x in a:                      # 1. how many items have each key
        count[key(x)] += 1
    total = 0
    for v in range(k):               # 2. prefix sums: count[v] = first output slot for key v
        count[v], total = total, total + count[v]
    out = [None] * len(a)
    for x in a:                      # 3. place items left to right: equal keys keep their order
        out[count[key(x)]] = x
        count[key(x)] += 1
    return out


def radix_sort_lsd(a, base=10, trace=False):
    """Sort non-negative integers digit by digit, least significant digit first."""
    if not a:
        return []
    biggest, place = max(a), 1
    while place <= biggest:
        a = counting_sort(a, base, key=lambda x: (x // place) % base)
        if trace:
            print(f"  by digit {place:>3d}: {a}")
        place *= base
    return a


def radix_sort_msd(words, pos=0):
    """Sort strings by first character, then recursively each bucket by the next one."""
    if len(words) <= 1:
        return list(words)
    done = [w for w in words if len(w) == pos]          # words that have ended come first
    buckets = {}
    for w in words:
        if len(w) > pos:
            buckets.setdefault(w[pos], []).append(w)
    out = done
    for ch in sorted(buckets):                         # at most 26 (or 256) bucket names
        out += radix_sort_msd(buckets[ch], pos + 1)
    return out


def bucket_sort(xs):
    """Sort floats in [0, 1): n buckets, insertion sort each, concatenate."""
    n = len(xs)
    buckets = [[] for _ in range(n)]
    for x in xs:
        buckets[int(n * x)].append(x)
    out, work = [], 0
    for b in buckets:
        for i in range(1, len(b)):                     # insertion sort
            x, j = b[i], i - 1
            while j >= 0 and b[j] > x:
                b[j + 1] = b[j]; j -= 1
            b[j + 1] = x
        out += b
        work += len(b) ** 2
    return out, work


def main():
    rng = random.Random(6)

    # Counting sort, traced on a small list with keys 0..5, then a stability check.
    a = [3, 1, 4, 1, 5, 2, 0, 4]
    print("counting sort of", a, "->", counting_sort(a, 6))
    cards = [(5, "a"), (2, "b"), (5, "c"), (1, "d"), (2, "e")]
    print("stable:", counting_sort(cards, 6, key=lambda c: c[0]))
    for _ in range(300):
        a = [rng.randrange(20) for _ in range(rng.randrange(50))]
        assert counting_sort(a, 20) == sorted(a)

    # LSD radix sort, traced; then a stability failure if the digit sort is unstable.
    a = [523, 81, 345, 9, 812, 47, 316, 280]
    print("\nLSD radix sort of", a)
    out = radix_sort_lsd(a, trace=True)
    for _ in range(300):
        a = [rng.randrange(10**6) for _ in range(rng.randrange(60))]
        assert radix_sort_lsd(a, base=256) == sorted(a)

    def unstable_digit_sort(a, place):               # same buckets, but each bucket read backwards
        buckets = [[] for _ in range(10)]
        for x in a:
            buckets[(x // place) % 10].append(x)
        return [x for b in buckets for x in reversed(b)]
    a = [523, 81, 345, 9, 812, 47, 316, 280]
    for place in (1, 10, 100):
        a = unstable_digit_sort(a, place)
    print("  with an unstable digit sort:", a)

    # MSD radix sort of words.
    words = ["mars", "moon", "map", "mast", "a", "orbit", "rover", "rock", "ma", "ore"]
    print("\nMSD radix sort:", radix_sort_msd(words))
    assert radix_sort_msd(words) == sorted(words)

    # Bucket sort: the work sum of (bucket size)^2 averages 2n - 1 on uniform data.
    print("\nbucket sort, uniform data: average of sum(bucket size^2) over 200 trials")
    for n in [10, 100, 1000, 10000]:
        total = 0
        for _ in range(200):
            xs = [rng.random() for _ in range(n)]
            out, work = bucket_sort(xs)
            assert out == sorted(xs)
            total += work
        print(f"  n = {n:5d}: {total / 200:9.1f}   (2n - 1 = {2 * n - 1})")
    xs = [rng.random() / 1000 for _ in range(1000)]     # all in [0, 0.001): one bucket
    print(f"  n = 1000, all values below 0.001: {bucket_sort(xs)[1]}")


if __name__ == "__main__":
    main()
