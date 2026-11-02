import sys


def kosaraju(n, edges):
    """Strongly connected components: groups where every vertex can reach every other.
    Returns a component number for each vertex, numbered in topological order of the components."""
    sys.setrecursionlimit(10000)
    adj = [[] for _ in range(n)]
    radj = [[] for _ in range(n)]            # the same graph with every arrow reversed
    for u, v in edges:
        adj[u].append(v)
        radj[v].append(u)
    seen = [False] * n
    order = []

    def dfs1(u):                             # pass 1: record finishing order
        seen[u] = True
        for v in adj[u]:
            if not seen[v]:
                dfs1(v)
        order.append(u)
    for u in range(n):
        if not seen[u]:
            dfs1(u)
    comp = [-1] * n

    def dfs2(u, c):                          # pass 2: on the reversed graph, latest finisher first
        comp[u] = c
        for v in radj[u]:
            if comp[v] == -1:
                dfs2(v, c)
    c = 0
    for u in reversed(order):
        if comp[u] == -1:
            dfs2(u, c)
            c += 1
    return c, comp


if __name__ == "__main__":
    edges = [(0, 1), (1, 2), (2, 0), (2, 3), (3, 4), (4, 5), (5, 3), (6, 5), (6, 7), (7, 6)]
    count, comp = kosaraju(8, edges)
    print(count, comp)
    groups = [[v for v in range(8) if comp[v] == c] for c in range(count)]
    print(groups)
