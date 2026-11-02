def min_coins(coins, amount):
    """The fewest coins that add up to amount (any coin may be used many times), and which coins; -1 if impossible."""
    INF = float("inf")
    best = [0] + [INF] * amount              # best[x] = fewest coins for the amount x
    last = [0] * (amount + 1)                # last[x] = the coin used last in that best way
    for x in range(1, amount + 1):
        for c in coins:
            if c <= x and best[x - c] + 1 < best[x]:
                best[x] = best[x - c] + 1
                last[x] = c
    if best[amount] == INF:
        return -1, []
    used, x = [], amount
    while x > 0:                             # walk back through the choices
        used.append(last[x])
        x -= last[x]
    return best[amount], used


def count_ways(coins, amount):
    """How many different sets of coins add up to amount (order does not matter)."""
    ways = [1] + [0] * amount                # one way to make 0: no coins
    for c in coins:                          # coins in the outer loop, so each set is counted once
        for x in range(c, amount + 1):
            ways[x] += ways[x - c]
    return ways[amount]


if __name__ == "__main__":
    print(*min_coins([1, 3, 4], 6))
    print(*min_coins([1, 5, 10, 25], 63))
    print(*min_coins([2], 3))
    print(count_ways([1, 2, 5], 5), count_ways([1, 5, 10, 25], 100))
