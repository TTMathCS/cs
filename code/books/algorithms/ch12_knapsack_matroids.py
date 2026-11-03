"""Chapter 12: fractional vs 0/1 knapsack, greedy on matroids, greedy set cover."""
from itertools import combinations


def fractional_knapsack(items, capacity):
    """items: (name, weight, value). Take by value per unit weight; split the last one."""
    total, taken = 0.0, []
    for name, w, v in sorted(items, key=lambda it: it[2] / it[1], reverse=True):
        if capacity <= 0:
            break
        part = min(w, capacity)
        taken.append((name, part / w))
        total += v * part / w
        capacity -= part
    return total, taken


def greedy_01_by_ratio(items, capacity):
    total, taken = 0, []
    for name, w, v in sorted(items, key=lambda it: it[2] / it[1], reverse=True):
        if w <= capacity:
            taken.append(name)
            total += v
            capacity -= w
    return total, taken


def best_01(items, capacity):
    best = (0, ())
    for r in range(len(items) + 1):
        for sub in combinations(items, r):
            if sum(it[1] for it in sub) <= capacity:
                best = max(best, (sum(it[2] for it in sub), tuple(it[0] for it in sub)))
    return best


def matroid_greedy(elements, weight, independent):
    """Generic greedy: heaviest first, keep an element if the set stays independent."""
    chosen = []
    for e in sorted(elements, key=weight, reverse=True):
        if independent(chosen + [e]):
            chosen.append(e)
    return chosen


def is_forest(edges):
    """Independence test of the graphic matroid: no cycle (tiny union-find)."""
    parent = {}

    def find(x):
        parent.setdefault(x, x)
        while parent[x] != x:
            x = parent[x]
        return x
    for u, v, _ in edges:
        ru, rv = find(u), find(v)
        if ru == rv:
            return False
        parent[ru] = rv
    return True


def is_matching(edges):
    ends = [x for u, v, _ in edges for x in (u, v)]
    return len(ends) == len(set(ends))


def best_subset(elements, weight, independent):
    best = (0, [])
    for r in range(len(elements) + 1):
        for sub in combinations(elements, r):
            if independent(list(sub)):
                best = max(best, (sum(map(weight, sub)), list(sub)), key=lambda t: t[0])
    return best


def greedy_set_cover(universe, sets):
    uncovered, chosen = set(universe), []
    while uncovered:
        name = max(sets, key=lambda s: len(sets[s] & uncovered))
        chosen.append(name)
        uncovered -= sets[name]
    return chosen


if __name__ == "__main__":
    items = [("gold", 10, 60), ("silver", 20, 100), ("bronze", 30, 120)]
    print("fractional knapsack, capacity 50:", fractional_knapsack(items, 50))
    print("0/1 greedy by ratio:              ", greedy_01_by_ratio(items, 50))
    print("0/1 true optimum:                 ", best_01(items, 50))

    edges = [("A", "B", 7), ("A", "C", 5), ("B", "C", 8), ("B", "D", 9),
             ("C", "D", 7), ("C", "E", 5), ("D", "E", 15)]
    w = lambda e: e[2]
    g = matroid_greedy(edges, w, is_forest)
    print("\nforests (a matroid): greedy", sum(map(w, g)), g)
    print("                     best  ", best_subset(edges, w, is_forest)[0])
    path = [("P", "Q", 2), ("Q", "R", 3), ("R", "S", 2)]
    g = matroid_greedy(path, w, is_matching)
    print("matchings (not a matroid): greedy", sum(map(w, g)), g)
    print("                           best  ", best_subset(path, w, is_matching))

    universe = range(1, 13)
    sets = {"S1": {1, 2, 3, 4, 5, 6}, "S2": {5, 6, 8, 9}, "S3": {1, 4, 7, 10},
            "S4": {2, 5, 7, 8, 11}, "S5": {3, 6, 9, 12}, "S6": {10, 11}}
    print("\ngreedy set cover:", greedy_set_cover(universe, sets))
    small = min((c for r in range(1, 7) for c in combinations(sets, r)
                 if set().union(*(sets[s] for s in c)) >= set(universe)), key=len)
    print("smallest cover:  ", list(small))
