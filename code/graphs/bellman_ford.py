INF = float("inf")


def bellman_ford(n, edges, src):
    """Shortest distances from src even with negative edge weights.
    Returns (dist, None) or (None, a vertex on a negative cycle) if some distance can drop forever."""
    dist = [INF] * n
    dist[src] = 0
    for _ in range(n - 1):                   # a shortest path uses at most n-1 edges
        changed = False
        for u, v, w in edges:
            if dist[u] != INF and dist[u] + w < dist[v]:
                dist[v] = dist[u] + w        # relax every edge, again and again
                changed = True
        if not changed:
            break                            # nothing improved: we are done early
    for u, v, w in edges:                    # one more round: any improvement means a negative cycle
        if dist[u] != INF and dist[u] + w < dist[v]:
            return None, v
    return dist, None


def show(dist):
    return "[" + ", ".join("inf" if d == INF else str(d) for d in dist) + "]"


if __name__ == "__main__":
    edges = [(0, 1, 6), (0, 2, 7), (1, 2, 8), (1, 3, 5), (1, 4, -4), (2, 3, -3), (2, 4, 9), (3, 1, -2),
             (4, 0, 2), (4, 3, 7)]
    dist, _ = bellman_ford(5, edges, 0)
    print(show(dist))
    dist, _ = bellman_ford(6, edges, 0)      # vertex 5 has no edges: unreachable
    print(show(dist))
    bad = [(0, 1, 1), (1, 2, -1), (2, 1, -1), (2, 3, 1)]
    print(bellman_ford(4, bad, 0)[1] is not None)
