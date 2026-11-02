def prefix_function(p):
    """pi[i] = the length of the longest proper prefix of p[:i+1] that is also a suffix of it."""
    pi = [0] * len(p)
    k = 0                                    # the length of the current matching prefix
    for i in range(1, len(p)):
        while k > 0 and p[i] != p[k]:        # mismatch: fall back to the next shorter border
            k = pi[k - 1]
        if p[i] == p[k]:
            k += 1
        pi[i] = k
    return pi


def kmp_search(text, p):
    """Every position where p starts in text (Knuth-Morris-Pratt), in O(len(text) + len(p))."""
    if not p:
        return list(range(len(text) + 1))
    pi = prefix_function(p)
    found, k = [], 0                         # k = how many letters of p match right now
    for i, ch in enumerate(text):
        while k > 0 and ch != p[k]:          # never move back in text: shift p using pi instead
            k = pi[k - 1]
        if ch == p[k]:
            k += 1
        if k == len(p):                      # a full match ends at i
            found.append(i - len(p) + 1)
            k = pi[k - 1]                    # keep going, to find overlapping matches too
    return found


if __name__ == "__main__":
    print(prefix_function("ABABCABAB"))
    print(kmp_search("ABABDABACDABABCABAB", "ABABCABAB"))
    print(kmp_search("AAAAA", "AA"), kmp_search("olympus mons", "mars"))
