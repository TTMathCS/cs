INF = float("inf")


def floyd_warshall(d):
    """All-pairs shortest distances. d[i][j] is the edge weight (INF if none, 0 on the diagonal).
    Changes d in place."""
    n = len(d)
    for k in range(n):                       # allow k as a stop in the middle of paths
        for i in range(n):
            for j in range(n):
                if d[i][k] + d[k][j] < d[i][j]:
                    d[i][j] = d[i][k] + d[k][j]
    return d


if __name__ == "__main__":
    d = [[0, 3, INF, 7],
         [8, 0, 2, INF],
         [5, INF, 0, 1],
         [2, INF, INF, 0]]
    for row in floyd_warshall(d):
        print(row)
    print(any(d[i][i] < 0 for i in range(len(d))))   # a negative diagonal would mean a negative cycle
