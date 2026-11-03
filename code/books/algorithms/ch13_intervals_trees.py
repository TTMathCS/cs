"""Chapter 13: matrix-chain order, optimal BST, longest path in a DAG, independent set in a tree."""
from functools import lru_cache


def matrix_chain(p):
    """Matrix i has shape p[i-1] x p[i], i = 1..n. m[i][j] = fewest scalar mults for A_i..A_j."""
    n = len(p) - 1
    m = [[0] * (n + 1) for _ in range(n + 1)]
    split = [[0] * (n + 1) for _ in range(n + 1)]
    for length in range(2, n + 1):               # solve short chains before long ones
        for i in range(1, n - length + 2):
            j = i + length - 1
            m[i][j] = float("inf")
            for k in range(i, j):
                cost = m[i][k] + m[k + 1][j] + p[i - 1] * p[k] * p[j]
                if cost < m[i][j]:
                    m[i][j], split[i][j] = cost, k

    def paren(i, j):
        return f"A{i}" if i == j else "(" + paren(i, split[i][j]) + paren(split[i][j] + 1, j) + ")"
    return m[1][n], paren(1, n)


def optimal_bst(p, q):
    """CLRS form: keys k1..kn searched with prob p[1..n], misses d0..dn with prob q[0..n]."""
    n = len(p) - 1
    e = [[0.0] * (n + 1) for _ in range(n + 2)]
    w = [[0.0] * (n + 1) for _ in range(n + 2)]
    root = [[0] * (n + 1) for _ in range(n + 1)]
    for i in range(1, n + 2):
        e[i][i - 1] = w[i][i - 1] = q[i - 1]
    for length in range(1, n + 1):
        for i in range(1, n - length + 2):
            j = i + length - 1
            w[i][j] = w[i][j - 1] + p[j] + q[j]
            e[i][j] = float("inf")
            for r in range(i, j + 1):
                t = e[i][r - 1] + e[r + 1][j] + w[i][j]
                if t < e[i][j]:
                    e[i][j], root[i][j] = t, r
    return e[1][n], root


def longest_path_dag(n, edges):
    """Vertices 0..n-1 already in topological order; edges (u, v, weight) with u < v."""
    best = [0] * n
    pred = [None] * n
    for u, v, wt in sorted(edges):               # sorted by u: process vertices in order
        if best[u] + wt > best[v]:
            best[v], pred[v] = best[u] + wt, u
    end = max(range(n), key=lambda v: best[v])
    path = [end]
    while pred[path[-1]] is not None:
        path.append(pred[path[-1]])
    return best[end], path[::-1]


def tree_independent_set(children, weight, root):
    """Max weight set of vertices, no two adjacent. Returns (with root, without root)."""
    def solve(v):
        take, skip = weight[v], 0
        for c in children.get(v, []):
            c_take, c_skip = solve(c)
            take += c_skip                     # v taken: children must be left out
            skip += max(c_take, c_skip)        # v skipped: each child free to choose
        return take, skip
    return solve(root)


if __name__ == "__main__":
    print("matrix chain 30x35, 35x15, 15x5, 5x10, 10x20, 20x25:",
          matrix_chain([30, 35, 15, 5, 10, 20, 25]))
    print("left to right ((((A1A2)A3)A4)A5)A6 would cost",
          30*35*15 + 30*15*5 + 30*5*10 + 30*10*20 + 30*20*25)

    p = [0, 0.15, 0.10, 0.05, 0.10, 0.20]
    q = [0.05, 0.10, 0.05, 0.05, 0.05, 0.10]
    cost, root = optimal_bst(p, q)
    print(f"\noptimal BST expected cost {cost:.2f}, root key k{root[1][5]}")

    edges = [(0, 1, 5), (0, 2, 3), (1, 3, 6), (1, 2, 2), (2, 4, 4), (2, 5, 2),
             (2, 3, 7), (3, 5, 1), (3, 4, -1), (4, 5, -2)]
    print("\nlongest path in the DAG:", longest_path_dag(6, edges))

    children = {"r": ["a", "b"], "a": ["c", "d"], "b": ["e"], "e": ["f", "g"]}
    weight = {"r": 6, "a": 4, "b": 3, "c": 5, "d": 2, "e": 8, "f": 1, "g": 1}
    take, skip = tree_independent_set(children, weight, "r")
    print("tree independent set: best with root", take, " without root", skip,
          " answer", max(take, skip))
