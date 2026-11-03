"""Chapter 13: longest common subsequence, edit distance, global alignment."""


def lcs(x, y):
    m, n = len(x), len(y)
    C = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if x[i - 1] == y[j - 1]:
                C[i][j] = C[i - 1][j - 1] + 1
            else:
                C[i][j] = max(C[i - 1][j], C[i][j - 1])
    out, i, j = [], m, n                 # trace back from the corner
    while i and j:
        if x[i - 1] == y[j - 1]:
            out.append(x[i - 1])
            i, j = i - 1, j - 1
        elif C[i - 1][j] >= C[i][j - 1]:
            i -= 1
        else:
            j -= 1
    return C[m][n], "".join(reversed(out)), C


def edit_distance(s, t):
    """Levenshtein distance with the list of operations that achieves it."""
    m, n = len(s), len(t)
    D = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(m + 1):
        D[i][0] = i
    for j in range(n + 1):
        D[0][j] = j
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            D[i][j] = min(D[i - 1][j] + 1,                          # delete s[i-1]
                          D[i][j - 1] + 1,                          # insert t[j-1]
                          D[i - 1][j - 1] + (s[i - 1] != t[j - 1]))  # match or substitute
    ops, i, j = [], m, n
    while i or j:
        if i and j and D[i][j] == D[i - 1][j - 1] + (s[i - 1] != t[j - 1]):
            if s[i - 1] != t[j - 1]:
                ops.append(f"substitute {s[i - 1]}->{t[j - 1]}")
            i, j = i - 1, j - 1
        elif i and D[i][j] == D[i - 1][j] + 1:
            ops.append(f"delete {s[i - 1]}")
            i -= 1
        else:
            ops.append(f"insert {t[j - 1]}")
            j -= 1
    return D[m][n], ops[::-1], D


def align(a, b, match=1, mismatch=-1, gap=-1):
    """Needleman-Wunsch global alignment: maximise the score."""
    m, n = len(a), len(b)
    S = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(m + 1):
        S[i][0] = i * gap
    for j in range(n + 1):
        S[0][j] = j * gap
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            diag = S[i - 1][j - 1] + (match if a[i - 1] == b[j - 1] else mismatch)
            S[i][j] = max(diag, S[i - 1][j] + gap, S[i][j - 1] + gap)
    top, bottom, i, j = [], [], m, n
    while i or j:
        if i and j and S[i][j] == S[i - 1][j - 1] + (match if a[i - 1] == b[j - 1] else mismatch):
            top.append(a[i - 1]); bottom.append(b[j - 1]); i, j = i - 1, j - 1
        elif i and S[i][j] == S[i - 1][j] + gap:
            top.append(a[i - 1]); bottom.append("-"); i -= 1
        else:
            top.append("-"); bottom.append(b[j - 1]); j -= 1
    return S[m][n], "".join(reversed(top)), "".join(reversed(bottom))


if __name__ == "__main__":
    length, common, C = lcs("ABCBDAB", "BDCABA")
    print("LCS of ABCBDAB and BDCABA:", length, common)
    print("table (rows ABCBDAB, columns BDCABA):")
    for row in C:
        print("  ", row)

    d, ops, D = edit_distance("kitten", "sitting")
    print("\nedit distance kitten -> sitting:", d, ops)
    d, ops, D = edit_distance("sunday", "saturday")
    print("edit distance sunday -> saturday:", d, ops)

    score, top, bottom = align("GCATGCG", "GATTACA")
    print(f"\nalignment score {score}:\n  {top}\n  {bottom}")
