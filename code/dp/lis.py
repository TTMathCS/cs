from bisect import bisect_left


def lis_slow(a):
    """O(n^2): best[i] = the length of the longest increasing subsequence that ends at a[i]."""
    best = [1] * len(a)
    for i in range(len(a)):
        for j in range(i):
            if a[j] < a[i] and best[j] + 1 > best[i]:
                best[i] = best[j] + 1
    return max(best, default=0)


def lis_fast(a):
    """O(n log n): tails[k] = the smallest value that can end an increasing subsequence of length k+1.
    Returns the length and one longest increasing subsequence."""
    tails, tail_at = [], []                  # tail_at[k] = the position in a of tails[k]
    prev = [-1] * len(a)                     # prev[i] = the position before a[i] in its subsequence
    for i, x in enumerate(a):
        k = bisect_left(tails, x)            # the first tail >= x (binary search)
        if k == len(tails):
            tails.append(x); tail_at.append(i)   # x extends the longest so far
        else:
            tails[k] = x; tail_at[k] = i         # x is a smaller ending for length k+1
        prev[i] = tail_at[k - 1] if k > 0 else -1
    out, i = [], tail_at[-1] if tail_at else -1
    while i != -1:
        out.append(a[i]); i = prev[i]
    return len(tails), out[::-1]


if __name__ == "__main__":
    a = [10, 9, 2, 5, 3, 7, 101, 18]
    print(lis_slow(a), *lis_fast(a))
    b = [0, 8, 4, 12, 2, 10, 6, 14, 1, 9, 5, 13, 3, 11, 7, 15]
    print(lis_slow(b), *lis_fast(b))
