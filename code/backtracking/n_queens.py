def n_queens(n):
    """Place n queens on an n x n board so that none attacks another. One queen per row: try each column,
    skip columns and diagonals already under attack, and back up when a row has no safe square.
    Returns the number of solutions and the first one found (queen's column in each row)."""
    cols, diag1, diag2 = [False] * n, [False] * (2 * n), [False] * (2 * n)
    place, first, count = [0] * n, [], 0

    def go(r):
        nonlocal count, first
        if r == n:
            count += 1
            if not first:
                first = list(place)
            return
        for c in range(n):
            if cols[c] or diag1[r + c] or diag2[r - c + n]:   # attacked: prune this branch
                continue
            cols[c] = diag1[r + c] = diag2[r - c + n] = True
            place[r] = c
            go(r + 1)
            cols[c] = diag1[r + c] = diag2[r - c + n] = False   # undo, try the next column
    go(0)
    return count, first


if __name__ == "__main__":
    print([n_queens(n)[0] for n in range(1, 11)])
    print(n_queens(8)[1])
    for c in n_queens(6)[1]:
        print("".join("Q" if k == c else "." for k in range(6)))
