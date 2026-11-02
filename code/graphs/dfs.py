def dfs_order(adj, start):
    """The order in which depth-first search first visits the vertices reachable from start."""
    seen = [False] * len(adj)
    order = []

    def visit(u):
        seen[u] = True
        order.append(u)
        for v in adj[u]:
            if not seen[v]:
                visit(v)                     # go as deep as possible before trying u's next neighbour
    visit(start)
    return order


def dfs_iterative(adj, start):
    """The same order without recursion, using an explicit stack (safe for huge graphs)."""
    seen = [False] * len(adj)
    order = []
    stack = [start]
    while stack:
        u = stack.pop()
        if seen[u]:
            continue
        seen[u] = True
        order.append(u)
        for v in reversed(adj[u]):           # reversed, so the first neighbour is popped first
            if not seen[v]:
                stack.append(v)
    return order


def components(adj):
    """Labels each vertex with the number of its connected component."""
    comp = [-1] * len(adj)
    count = 0
    for s in range(len(adj)):
        if comp[s] == -1:                    # a new component starts here
            stack = [s]
            comp[s] = count
            while stack:
                u = stack.pop()
                for v in adj[u]:
                    if comp[v] == -1:
                        comp[v] = count
                        stack.append(v)
            count += 1
    return count, comp


def has_cycle(adj):
    """Undirected graph: is there a cycle? (An edge to an already-seen vertex other than our parent.)"""
    seen = [False] * len(adj)
    for s in range(len(adj)):
        if seen[s]:
            continue
        stack = [(s, -1)]
        seen[s] = True
        while stack:
            u, parent = stack.pop()
            for v in adj[u]:
                if not seen[v]:
                    seen[v] = True
                    stack.append((v, u))
                elif v != parent:
                    return True
    return False


def build(n, edges):
    adj = [[] for _ in range(n)]
    for u, v in edges:
        adj[u].append(v)
        adj[v].append(u)
    return adj


if __name__ == "__main__":
    adj = build(8, [(0, 1), (0, 2), (1, 3), (2, 3), (3, 4), (4, 5), (2, 5), (6, 7)])
    print(dfs_order(adj, 0), dfs_iterative(adj, 0))
    print(components(adj))
    tree = build(5, [(0, 1), (0, 2), (2, 3), (2, 4)])
    print(has_cycle(adj), has_cycle(tree))
