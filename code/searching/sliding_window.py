def max_sum_window(a, k):
    """The largest sum of k consecutive values of a."""
    window = sum(a[:k])
    best = window
    for i in range(k, len(a)):
        window += a[i] - a[i - k]            # slide right: add the new value, drop the old one
        best = max(best, window)
    return best


def longest_unique(s):
    """The length of the longest stretch of s with no repeated character."""
    last = {}                                # where each character was last seen
    left = best = 0                          # the window is s[left..right]
    for right, ch in enumerate(s):
        if ch in last and last[ch] >= left:  # ch repeats inside the window: shrink past it
            left = last[ch] + 1
        last[ch] = right
        best = max(best, right - left + 1)
    return best


def shortest_with_sum(a, target):
    """The length of the shortest stretch of positive values with sum >= target (0 if none)."""
    left = total = 0
    best = len(a) + 1
    for right in range(len(a)):
        total += a[right]                    # grow on the right ...
        while total >= target:               # ... and shrink from the left while it still works
            best = min(best, right - left + 1)
            total -= a[left]
            left += 1
    return 0 if best > len(a) else best


if __name__ == "__main__":
    print(max_sum_window([2, 1, 5, 1, 3, 2], 3))
    print(longest_unique("abcabcbb"), longest_unique("bbbbb"), longest_unique("pwwkew"), longest_unique(""))
    print(shortest_with_sum([2, 3, 1, 2, 4, 3], 7), shortest_with_sum([1, 1, 1], 5))
