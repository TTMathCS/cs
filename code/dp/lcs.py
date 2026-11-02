def lcs(a, b):
    """The longest common subsequence of a and b: the longest string whose letters appear in both, in order
    (not necessarily next to each other). Returns its length and one such string."""
    n, m = len(a), len(b)
    L = [[0] * (m + 1) for _ in range(n + 1)]   # L[i][j] = LCS length of a[:i] and b[:j]
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            if a[i - 1] == b[j - 1]:
                L[i][j] = L[i - 1][j - 1] + 1   # last letters match: use them
            else:
                L[i][j] = max(L[i - 1][j], L[i][j - 1])   # drop the last letter of a, or of b
    out, i, j = [], n, m
    while i > 0 and j > 0:                      # walk back from the corner
        if a[i - 1] == b[j - 1]:
            out.append(a[i - 1]); i -= 1; j -= 1
        elif L[i - 1][j] >= L[i][j - 1]:
            i -= 1
        else:
            j -= 1
    return L[n][m], "".join(reversed(out))


if __name__ == "__main__":
    print(*lcs("ABCBDAB", "BDCABA"))
    print(*lcs("AGGTAB", "GXTXAYB"))
    print(*lcs("OLYMPUS", "ELYSIUM"))
