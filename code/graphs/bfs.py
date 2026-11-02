from collections import deque


def bfs(adj, start):
    """Fewest-edges distance from start to every vertex (-1 if unreachable), and each vertex's parent."""
    dist = [-1] * len(adj)
    parent = [-1] * len(adj)
    dist[start] = 0
    q = deque([start])
    while q:
        u = q.popleft()                      # the oldest vertex in the queue: nearest first
        for v in adj[u]:
            if dist[v] == -1:                # first time we reach v: this is the shortest way
                dist[v] = dist[u] + 1
                parent[v] = u
                q.append(v)
    return dist, parent


def path(parent, target):
    """Walks the parents back from target and reverses: the shortest path from the start."""
    out = []
    while target != -1:
        out.append(target)
        target = parent[target]
    return out[::-1]


def build(n, edges):
    adj = [[] for _ in range(n)]
    for u, v in edges:                       # undirected: store both directions
        adj[u].append(v)
        adj[v].append(u)
    return adj


if __name__ == "__main__":
    adj = build(8, [(0, 1), (0, 2), (1, 3), (2, 3), (3, 4), (4, 5), (2, 5), (6, 7)])
    dist, parent = bfs(adj, 0)
    print(dist)
    print(path(parent, 4), path(parent, 5))
    print([v for v in range(8) if dist[v] == -1])   # not reachable from 0
