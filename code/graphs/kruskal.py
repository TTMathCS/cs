def kruskal(n, edges):
    """Minimum spanning tree of a connected undirected graph: (total weight, chosen edges)."""
    parent = list(range(n))

    def find(x):                             # union-find with path halving
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x
    total, chosen = 0, []
    for w, u, v in sorted((w, u, v) for u, v, w in edges):   # cheapest edges first
        ru, rv = find(u), find(v)
        if ru != rv:                         # joins two different trees: keep it
            parent[ru] = rv
            total += w
            chosen.append((u, v, w))
            if len(chosen) == n - 1:
                break
        # otherwise it would close a cycle: skip it
    return total, chosen


if __name__ == "__main__":
    edges = [(0, 1, 4), (0, 7, 8), (1, 2, 8), (1, 7, 11), (2, 3, 7), (2, 8, 2), (2, 5, 4), (3, 4, 9),
             (3, 5, 14), (4, 5, 10), (5, 6, 2), (6, 7, 1), (6, 8, 6), (7, 8, 7)]
    total, chosen = kruskal(9, edges)
    print(total)
    print(chosen)
