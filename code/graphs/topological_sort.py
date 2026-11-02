from collections import deque


def kahn(n, edges):
    """Topological order of a directed graph (Kahn's algorithm), or None if it has a cycle."""
    adj = [[] for _ in range(n)]
    indeg = [0] * n                          # how many arrows point into each vertex
    for u, v in edges:
        adj[u].append(v)
        indeg[v] += 1
    q = deque(v for v in range(n) if indeg[v] == 0)   # nothing has to come before these
    order = []
    while q:
        u = q.popleft()
        order.append(u)
        for v in adj[u]:                     # "remove" u: its arrows no longer count
            indeg[v] -= 1
            if indeg[v] == 0:
                q.append(v)
    return order if len(order) == n else None  # leftovers lie on a cycle


def dfs_topo(n, edges):
    """Topological order by depth-first search: a vertex is finished after everything it points to."""
    adj = [[] for _ in range(n)]
    for u, v in edges:
        adj[u].append(v)
    state = [0] * n                          # 0 = new, 1 = on the current path, 2 = finished
    finished = []

    def visit(u):
        state[u] = 1
        for v in adj[u]:
            if state[v] == 1:
                raise ValueError("cycle")    # an arrow back into the current path
            if state[v] == 0:
                visit(v)
        state[u] = 2
        finished.append(u)
    for u in range(n):
        if state[u] == 0:
            visit(u)
    return finished[::-1]                    # reverse finishing order


if __name__ == "__main__":
    # 0 maths, 1 programming, 2 data structures, 3 algorithms, 4 databases, 5 machine learning
    edges = [(0, 3), (1, 2), (2, 3), (2, 4), (3, 5), (0, 5)]
    print(kahn(6, edges))
    print(dfs_topo(6, edges))
    print(kahn(3, [(0, 1), (1, 2), (2, 0)]))
