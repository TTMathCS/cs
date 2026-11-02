# Floyd-Warshall

*Shortest distances between every pair of vertices, in three nested loops. Step $k$ asks, for every pair: is it
shorter to go through vertex $k$?*

| Time | Extra space | Handles | Detects |
|---|---|---|---|
| $O(V^3)$ | $O(V^2)$ | negative weights | negative cycles (a negative number on the diagonal) |

## The idea

Start with a table `d[i][j]` of direct edge weights ($\infty$ where there is no edge, 0 from a vertex to itself).
Now allow paths to pass through vertex 0: for every pair $(i, j)$, going $i \to 0 \to j$ might be shorter. Then
allow vertex 1 as well, then 2, and so on. After allowing all $V$ vertices, the table holds every shortest
distance.

The whole algorithm is

```
for k in range(n):
    for i in range(n):
        for j in range(n):
            d[i][j] = min(d[i][j], d[i][k] + d[k][j])
```

and the order of the loops matters: $k$ must be outermost.

## Code

=== "Python"

    ```python
    --8<-- "graphs/floyd_warshall.py"
    ```

=== "Java"

    ```java
    --8<-- "graphs/FloydWarshall.java"
    ```

=== "C++"

    ```cpp
    --8<-- "graphs/floyd_warshall.cpp"
    ```

Output: the full distance table

```
[0, 3, 5, 6]
[5, 0, 2, 3]
[3, 6, 0, 1]
[2, 5, 7, 0]
```

and `False`: no negative cycle.

## When to use it

- **All-pairs distances on small graphs** (up to a few hundred vertices): a distance table between all the
  stations of a transit network, all cities on a map.
- **Transitive closure:** who can reach whom, with `or` and `and` in place of `min` and `+` (Warshall's
  algorithm).
- **Dense graphs with negative weights** where running Bellman-Ford from every vertex would cost $O(V^2E)$.
- For large sparse graphs, run [Dijkstra](dijkstra.md) from every vertex instead: $O(VE\log V)$.

## Common mistakes

- **Wrong loop order:** with `k` inside, the answer is wrong. `k` is always the outer loop.
- **Overflow of $\infty + \infty$:** use $\infty$ = half the largest integer (as the code does), or skip when
  `d[i][k]` is $\infty$.
- **Forgetting the zeros on the diagonal.**
- **Rebuilding paths:** keep a `next[i][j]` table, updated together with `d`, if you need the routes and not
  just their lengths.

## Going deeper

Each part below starts closed; open the ones you want.

??? example "Sample walkthrough: the table after each k"

    Edges: 0→1 (3), 0→3 (7), 1→0 (8), 1→2 (2), 2→0 (5), 2→3 (1), 3→0 (2).

    | After $k$ | Improvements |
    |---|---|
    | 0 | 1→3 via 0: 8 + 7 = 15; 2→1 via 0: 5 + 3 = 8; 3→1 via 0: 2 + 3 = 5 |
    | 1 | 0→2 via 1: 3 + 2 = 5; 3→2 via 1: 5 + 2 = 7 |
    | 2 | 0→3 via 2: 5 + 1 = 6; 1→0 via 2: 2 + 5 = 7; 1→3 via 2: 2 + 1 = 3 |
    | 3 | 1→0 via 3: 3 + 2 = 5; 2→0 via 3: 1 + 2 = 3; 2→1 via 3: 1 + 5 = 6 |

??? abstract "The math: the recurrence behind the loops"

    Number the vertices $0..n-1$ and let $d^{(k)}_{ij}$ be the length of the shortest path from $i$ to $j$ whose
    **intermediate** vertices all lie in $\{0, \ldots, k-1\}$. Then $d^{(0)}_{ij}$ is the direct edge weight, and

    $$
    d^{(k+1)}_{ij} = \min\!\left(d^{(k)}_{ij},\; d^{(k)}_{ik} + d^{(k)}_{kj}\right),
    $$

    because a shortest such path either avoids $k$, or passes through $k$ exactly once (with no negative cycle,
    repeating $k$ never helps) and splits into two paths that use only $\{0, \ldots, k-1\}$ inside.
    $d^{(n)}_{ij}$ is the answer. This is [dynamic programming](../dp/index.md) over $k$.

    **Why one table is enough.** In round $k$, the entries $d_{ik}$ and $d_{kj}$ do not change (going through $k$
    to reach $k$ adds $d_{kk} = 0$), so updating in place reads the same values as using a fresh table.

    **Negative cycles.** If vertex $i$ lies on a negative cycle, then after the algorithm $d_{ii} < 0$.

    **Time and space:** $n^3$ updates and an $n \times n$ table: $\Theta(V^3)$ time, $\Theta(V^2)$ space. For
    $V = 400$ that is 64 million cheap steps, well under a second.

??? tip "Watch it step by step"

    For each $k$, row $k$ and column $k$ (orange) combine to improve other entries (red).

    <div class="cs-anim" data-anim="floyd-warshall"></div>

??? info "Variations and related ideas"

    - **Warshall's transitive closure:** `reach[i][j] |= reach[i][k] && reach[k][j]`.
    - **Minimax and maximin paths** (the widest bottleneck): replace $(\min, +)$ by $(\min, \max)$ or
      $(\max, \min)$.
    - **Matrix multiplication view:** shortest paths are powers of the weight matrix in the $(\min, +)$ algebra;
      repeated squaring gives $O(V^3 \log V)$.
    - **Counting walks:** in ordinary algebra, $(A^k)_{ij}$ counts walks of length $k$.

## See also

- [Dijkstra](dijkstra.md) and [Bellman-Ford](bellman-ford.md): single-source shortest paths
- [Dynamic programming](../dp/index.md): Floyd-Warshall is a DP

## References

- R. W. Floyd, "Algorithm 97: Shortest path", *Communications of the ACM* 5(6), 1962.
- S. Warshall, "A theorem on Boolean matrices", *Journal of the ACM* 9(1), 1962.
- T. H. Cormen et al., *Introduction to Algorithms*, 4th ed., §23.2 (the Floyd-Warshall algorithm).
