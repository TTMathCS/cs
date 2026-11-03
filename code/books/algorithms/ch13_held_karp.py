"""Chapter 13: travelling salesman by bitmask DP (Held-Karp), checked by brute force."""
from itertools import permutations
import math
import random


def held_karp(dist):
    """C[S][j]: shortest path from city 0 through exactly the cities in S, ending at j (j in S, 0 not in S)."""
    n = len(dist)
    full = 1 << (n - 1)                  # bit j-1 stands for city j, for j = 1..n-1
    INF = math.inf
    C = [[INF] * n for _ in range(full)]
    parent = [[-1] * n for _ in range(full)]
    for j in range(1, n):
        C[1 << (j - 1)][j] = dist[0][j]
    for S in range(1, full):             # every subset is larger than its own subsets
        for j in range(1, n):
            if not S >> (j - 1) & 1 or C[S][j] == INF:
                continue
            for k in range(1, n):        # extend the path ending at j to a new city k
                if S >> (k - 1) & 1:
                    continue
                T = S | 1 << (k - 1)
                if C[S][j] + dist[j][k] < C[T][k]:
                    C[T][k] = C[S][j] + dist[j][k]
                    parent[T][k] = j
    S = full - 1
    best, last = min((C[S][j] + dist[j][0], j) for j in range(1, n))
    tour = []
    while last != -1:                    # walk the parents back to city 0
        tour.append(last)
        S, last = S & ~(1 << (last - 1)), parent[S][last]
    return best, [0] + tour[::-1] + [0]


def brute_force(dist):
    n = len(dist)
    best = math.inf
    for perm in permutations(range(1, n)):
        tour = (0,) + perm + (0,)
        best = min(best, sum(dist[a][b] for a, b in zip(tour, tour[1:])))
    return best


if __name__ == "__main__":
    dist = [[0, 2, 9, 10],
            [1, 0, 6, 4],
            [15, 7, 0, 8],
            [6, 3, 12, 0]]
    print("4 cities (directed distances):", held_karp(dist), " brute force:", brute_force(dist))

    random.seed(1962)
    n = 9
    pts = [(random.randint(0, 100), random.randint(0, 100)) for _ in range(n)]
    d = [[round(math.dist(p, q), 2) for q in pts] for p in pts]
    hk = held_karp(d)
    print(f"{n} random cities: Held-Karp {hk[0]:.2f} tour {hk[1]}, brute force {brute_force(d):.2f}")
    print("work: Held-Karp about 2^(n-1) * n^2 =", 2 ** (n - 1) * n * n,
          " brute force (n-1)! tours =", math.factorial(n - 1))
    for m in (15, 20, 25):
        print(f"n = {m}: 2^(n-1) n^2 = {2 ** (m - 1) * m * m:.2e}, (n-1)! = {math.factorial(m - 1):.2e}")
