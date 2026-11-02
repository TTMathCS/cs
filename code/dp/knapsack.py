def knapsack(weights, values, cap):
    """0/1 knapsack: the most value that fits in a bag of capacity cap, each item taken at most once.
    Returns the best value and the items (by number) that give it."""
    n = len(weights)
    # best[i][c] = the most value using only the first i items with capacity c
    best = [[0] * (cap + 1) for _ in range(n + 1)]
    for i in range(1, n + 1):
        w, v = weights[i - 1], values[i - 1]
        for c in range(cap + 1):
            best[i][c] = best[i - 1][c]                          # leave item i-1 out ...
            if w <= c and best[i - 1][c - w] + v > best[i][c]:   # ... or take it, if it fits and is better
                best[i][c] = best[i - 1][c - w] + v
    items, c = [], cap
    for i in range(n, 0, -1):                # walk back: a changed value means item i-1 was taken
        if best[i][c] != best[i - 1][c]:
            items.append(i - 1)
            c -= weights[i - 1]
    return best[n][cap], sorted(items)


def knapsack_1d(weights, values, cap):
    """The same answer with one row: go through capacities from high to low so each item is used once."""
    best = [0] * (cap + 1)
    for w, v in zip(weights, values):
        for c in range(cap, w - 1, -1):
            best[c] = max(best[c], best[c - w] + v)
    return best[cap]


if __name__ == "__main__":
    print(*knapsack([1, 3, 4, 5], [1, 4, 5, 7], 7))
    print(*knapsack([10, 20, 30], [60, 100, 120], 50))
    print(knapsack_1d([1, 3, 4, 5], [1, 4, 5, 7], 7), knapsack_1d([10, 20, 30], [60, 100, 120], 50))
