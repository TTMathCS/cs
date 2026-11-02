def edit_distance(a, b):
    """The fewest single-letter inserts, deletes and replacements that turn a into b (Levenshtein distance).
    Returns the distance and the list of steps."""
    n, m = len(a), len(b)
    D = [[0] * (m + 1) for _ in range(n + 1)]   # D[i][j] = distance from a[:i] to b[:j]
    for i in range(n + 1):
        D[i][0] = i                             # delete all i letters
    for j in range(m + 1):
        D[0][j] = j                             # insert all j letters
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            same = 0 if a[i - 1] == b[j - 1] else 1
            D[i][j] = min(D[i - 1][j] + 1,          # delete a[i-1]
                          D[i][j - 1] + 1,          # insert b[j-1]
                          D[i - 1][j - 1] + same)   # keep or replace
    steps, i, j = [], n, m
    while i > 0 or j > 0:                       # walk back to list the steps
        if i > 0 and j > 0 and D[i][j] == D[i - 1][j - 1] + (a[i - 1] != b[j - 1]):
            if a[i - 1] != b[j - 1]:
                steps.append(f"replace {a[i - 1]} with {b[j - 1]}")
            i -= 1; j -= 1
        elif i > 0 and D[i][j] == D[i - 1][j] + 1:
            steps.append(f"delete {a[i - 1]}"); i -= 1
        else:
            steps.append(f"insert {b[j - 1]}"); j -= 1
    return D[n][m], steps[::-1]


if __name__ == "__main__":
    for a, b in [("kitten", "sitting"), ("sunday", "saturday"), ("mars", "stars")]:
        d, steps = edit_distance(a, b)
        print(a, b, d, "; ".join(steps))
