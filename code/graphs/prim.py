import heapq


def prim(n, edges, start=0):
    """Minimum spanning tree by growing one tree from start: (total weight, edges in the order added)."""
    adj = [[] for _ in range(n)]
    for u, v, w in edges:
        adj[u].append((w, v))
        adj[v].append((w, u))
    in_tree = [False] * n
    pq = [(0, start, -1)]                    # (edge weight, vertex, the tree vertex it hangs from)
    total, chosen = 0, []
    while pq:
        w, v, frm = heapq.heappop(pq)        # the cheapest edge leaving the tree
        if in_tree[v]:
            continue                         # both ends already in the tree: skip
        in_tree[v] = True
        total += w
        if frm != -1:
            chosen.append((frm, v, w))
        for w2, x in adj[v]:
            if not in_tree[x]:
                heapq.heappush(pq, (w2, x, v))
    return total, chosen


if __name__ == "__main__":
    edges = [(0, 1, 4), (0, 7, 8), (1, 2, 8), (1, 7, 11), (2, 3, 7), (2, 8, 2), (2, 5, 4), (3, 4, 9),
             (3, 5, 14), (4, 5, 10), (5, 6, 2), (6, 7, 1), (6, 8, 6), (7, 8, 7)]
    total, chosen = prim(9, edges)
    print(total)
    print(chosen)
