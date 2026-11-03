"""Chapter 14: branch and bound for 0/1 knapsack and for the travelling salesman."""
import heapq
import itertools
import math
import random


def knapsack_bb(items, W, use_bound=True):
    """Depth-first branch and bound; items sorted by value density, bound = fractional knapsack."""
    items = sorted(items, key=lambda it: it[1] / it[0], reverse=True)   # (weight, value)
    n = len(items)
    best = [0]
    nodes = [0]

    def bound(i, weight, value):
        """Upper bound: fill the remaining room greedily, allowing a fraction of one item."""
        room = W - weight
        for w, v in items[i:]:
            if w <= room:
                room -= w
                value += v
            else:
                return value + v * room / w
        return value

    def go(i, weight, value):
        nodes[0] += 1
        best[0] = max(best[0], value)
        if i == n:
            return
        if use_bound and bound(i, weight, value) <= best[0]:
            return                               # this subtree cannot beat the incumbent
        w, v = items[i]
        if weight + w <= W:
            go(i + 1, weight + w, value + v)     # take item i first: finds good solutions early
        go(i + 1, weight, value)                 # then leave it
    go(0, 0, 0)
    return best[0], nodes[0]


def knapsack_dp(items, W):
    K = [0] * (W + 1)
    for w, v in items:
        for c in range(W, w - 1, -1):
            K[c] = max(K[c], K[c - w] + v)
    return K[W]


def tsp_bb(d):
    """Best-first branch and bound. Lower bound: cost so far plus, for every city still to be
    left (the current one and the unvisited ones), its cheapest edge to a city it could go to."""
    n = len(d)
    best_cost, best_tour = math.inf, None
    tick = itertools.count()
    heap = [(0, next(tick), 0, (0,))]
    nodes = 0
    while heap:
        lb, _, cost, path = heapq.heappop(heap)
        if lb >= best_cost:
            continue                              # pruned: cannot beat the best tour found
        nodes += 1
        last = path[-1]
        if len(path) == n:
            total = cost + d[last][0]
            if total < best_cost:
                best_cost, best_tour = total, path + (0,)
            continue
        rest = [c for c in range(n) if c not in path]
        for nxt in rest:
            new_cost = cost + d[last][nxt]
            left = [c for c in rest if c != nxt]
            # every city in `left` and nxt itself still needs one outgoing edge
            est = new_cost
            for c in left + [nxt]:
                targets = [t for t in left if t != c] + [0]
                est += min(d[c][t] for t in targets) if targets else 0
            if est < best_cost:
                heapq.heappush(heap, (est, next(tick), new_cost, path + (nxt,)))
    return best_cost, best_tour, nodes


def tsp_brute(d):
    n = len(d)
    return min(sum(d[a][b] for a, b in zip((0,) + p, p + (0,)))
               for p in itertools.permutations(range(1, n)))


if __name__ == "__main__":
    random.seed(14)
    items = [(random.randint(10, 60), random.randint(10, 90)) for _ in range(30)]
    W = sum(w for w, _ in items) // 2
    v_bb, n_bb = knapsack_bb(items, W, use_bound=True)
    print(f"knapsack, 30 items, capacity {W}: branch and bound {v_bb} in {n_bb} nodes;"
          f" DP says {knapsack_dp(items, W)}; the full tree has {2 ** 31 - 1} nodes")
    small = items[:18]
    W2 = sum(w for w, _ in small) // 2
    for flag in (False, True):
        v, nodes = knapsack_bb(small, W2, use_bound=flag)
        print(f"  18 items, bounding {flag!s:5}: value {v}, {nodes} nodes")

    for n in (8, 10):
        pts = [(random.randint(0, 100), random.randint(0, 100)) for _ in range(n)]
        d = [[round(math.dist(p, q)) for q in pts] for p in pts]
        cost, tour, nodes = tsp_bb(d)
        print(f"TSP {n} cities: branch and bound {cost} via {tour}, {nodes} nodes expanded;"
              f" brute force {tsp_brute(d)} over {math.factorial(n - 1)} tours")
