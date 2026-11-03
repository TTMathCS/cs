"""Chapter 11: counting inversions and maximum subarray, two ways each."""
import random


def count_inversions(a):
    """Return (sorted copy of a, number of inversions) by merge-and-count."""
    if len(a) <= 1:
        return list(a), 0
    mid = len(a) // 2
    left, x = count_inversions(a[:mid])
    right, y = count_inversions(a[mid:])
    merged, z = [], 0
    i = j = 0
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            merged.append(left[i])
            i += 1
        else:                      # right[j] is smaller than every left[i:]
            merged.append(right[j])
            z += len(left) - i     # so it forms an inversion with each of them
            j += 1
    merged += left[i:] + right[j:]
    return merged, x + y + z


def brute_inversions(a):
    return sum(1 for i in range(len(a)) for j in range(i + 1, len(a)) if a[i] > a[j])


def max_subarray_dc(a, lo=0, hi=None):
    """Best sum of a non-empty contiguous slice of a[lo:hi], with its ends."""
    if hi is None:
        hi = len(a)
    if hi - lo == 1:
        return a[lo], lo, hi
    mid = (lo + hi) // 2
    best_left = max_subarray_dc(a, lo, mid)
    best_right = max_subarray_dc(a, mid, hi)
    # best slice that crosses the middle: best suffix of the left half
    # plus best prefix of the right half
    s, best_s, i_best = 0, float("-inf"), mid
    for i in range(mid - 1, lo - 1, -1):
        s += a[i]
        if s > best_s:
            best_s, i_best = s, i
    s, best_p, j_best = 0, float("-inf"), mid
    for j in range(mid, hi):
        s += a[j]
        if s > best_p:
            best_p, j_best = s, j + 1
    crossing = (best_s + best_p, i_best, j_best)
    return max(best_left, best_right, crossing, key=lambda t: t[0])


def kadane(a):
    """Best sum of a non-empty contiguous slice, in one pass."""
    best = cur = a[0]
    start = best_l = 0
    best_r = 1
    for i in range(1, len(a)):
        if cur < 0:                # a negative prefix never helps: restart here
            cur, start = a[i], i
        else:
            cur += a[i]
        if cur > best:
            best, best_l, best_r = cur, start, i + 1
    return best, best_l, best_r


if __name__ == "__main__":
    a = [3, 8, 2, 5, 1, 9, 4]
    s, inv = count_inversions(a)
    print("array:", a)
    print("sorted:", s, " inversions:", inv, " brute force:", brute_inversions(a))

    prices_change = [13, -3, -25, 20, -3, -16, -23, 18, 20, -7, 12, -5, -22, 15, -4, 7]
    print("\nchanges:", prices_change)
    print("divide and conquer (sum, start, end):", max_subarray_dc(prices_change))
    print("Kadane              (sum, start, end):", kadane(prices_change))

    random.seed(11)
    ok = True
    for _ in range(300):
        n = random.randint(1, 40)
        b = [random.randint(-20, 20) for _ in range(n)]
        if count_inversions(b)[1] != brute_inversions(b):
            ok = False
        brute = max(sum(b[i:j]) for i in range(n) for j in range(i + 1, n + 1))
        if max_subarray_dc(b)[0] != brute or kadane(b)[0] != brute:
            ok = False
    print("\n300 random tests against brute force passed:", ok)
    big = list(range(2000, 0, -1))
    print("inversions in 2000..1 (should be 2000*1999/2 = 1999000):", count_inversions(big)[1])
