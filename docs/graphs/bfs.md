# Breadth-first search

*Explore a graph in rings: first the start, then everything one edge away, then everything two edges away, and
so on. A queue keeps the order, and the first time you reach a vertex is by a shortest path.*

| Time | Extra space | Finds |
|---|---|---|
| $O(V + E)$ | $O(V)$ | fewest-edges distances and paths from one start; everything reachable |

## The idea

Drop a stone in a pond: the ripple reaches nearby points first and far points later. BFS spreads through a graph
the same way. It keeps a **queue** of vertices that have been reached but not yet explored. It takes the oldest
one, looks at its neighbours, and every neighbour not seen before gets distance one more than the current vertex
and joins the back of the queue.

Because vertices leave the queue in order of distance (all distance-1 vertices before any distance-2 vertex),
the first time BFS reaches a vertex, it has found a path with the **fewest possible edges**. Remembering who
discovered each vertex (its *parent*) lets you rebuild that path backwards.

## How it works

1. `dist[start] = 0`, every other distance $-1$ (unseen); put `start` in the queue.
2. While the queue is not empty: take `u` from the front; for each neighbour `v` with `dist[v] = -1`, set
   `dist[v] = dist[u] + 1`, `parent[v] = u`, and add `v` to the back.

## Code

=== "Python"

    ```python
    --8<-- "graphs/bfs.py"
    ```

=== "Java"

    ```java
    --8<-- "graphs/Bfs.java"
    ```

=== "C++"

    ```cpp
    --8<-- "graphs/bfs.cpp"
    ```

Output: the distances `[0, 1, 1, 2, 3, 2, -1, -1]`, the paths `[0, 1, 3, 4]` and `[0, 2, 5]`, and `[6, 7]`, the
vertices that cannot be reached.

## When to use it

- **Shortest paths when every step costs the same:** mazes and grids, the fewest moves to solve a puzzle (each
  state is a vertex), degrees of separation in a social network, the fewest flights.
- **Connected components** and flood fill (the paint bucket).
- **Testing whether a graph is bipartite** (two-colourable): colour by distance parity.
- **Level-by-level work** on trees, web crawling by distance.
- **Not** for weighted edges: use [Dijkstra](dijkstra.md).

## Common mistakes

- **Marking a vertex as seen when it leaves the queue** instead of when it enters: the same vertex can be queued
  many times, and with weights in mind that is wrong anyway; mark on entry.
- **Using a list with `pop(0)`** in Python as the queue: $O(V^2)$. Use `collections.deque`.
- **Using it on weighted graphs:** fewest edges is not least total weight.
- **Grids:** forgetting to check the bounds or walls before queuing a neighbour.

## Going deeper

Each part below starts closed; open the ones you want.

??? example "Sample walkthrough: BFS from 0"

    Edges: 0–1, 0–2, 1–3, 2–3, 3–4, 4–5, 2–5, 6–7.

    | Take from queue | New neighbours (distance) | Queue after |
    |---|---|---|
    | — | start 0 (0) | 0 |
    | 0 | 1 (1), 2 (1) | 1, 2 |
    | 1 | 3 (2) | 2, 3 |
    | 2 | 5 (2) (3 already seen) | 3, 5 |
    | 3 | 4 (3) | 5, 4 |
    | 5 | none (4 already seen) | 4 |
    | 4 | none | empty |

    The path to 4 is read backwards from the parents: 4 ← 3 ← 1 ← 0.

??? abstract "The math: why BFS finds shortest paths"

    Let $\delta(v)$ be the true fewest-edges distance from the start $s$.

    **Claim 1: the queue is sorted by distance and spans at most two levels.** At any time, if the queue holds
    $v_1, \ldots, v_r$ (front to back), then $d[v_1] \le d[v_2] \le \cdots \le d[v_r] \le d[v_1] + 1$. Taking $v_1$
    and adding neighbours with distance $d[v_1] + 1$ at the back keeps this true.

    **Claim 2: $d[v] = \delta(v)$ for every reached $v$.** Suppose not, and let $v$ be a vertex with the smallest
    $\delta(v)$ for which $d[v] > \delta(v)$ (BFS never underestimates, since every $d$ comes from a real path).
    Let $u$ be the vertex before $v$ on a shortest path, so $\delta(u) = \delta(v) - 1$ and $d[u] = \delta(u)$.
    When $u$ was taken from the queue, $v$ was either unseen (then $d[v] = d[u] + 1 = \delta(v)$, a
    contradiction) or already seen with, by claim 1, $d[v] \le d[u] + 1 = \delta(v)$, a contradiction too.

    **Time.** Each vertex enters the queue at most once, and each adjacency list is scanned once when its vertex
    leaves: $\sum_v (1 + \deg v) = V + 2E$ for an undirected graph, so $O(V + E)$.

??? tip "Watch it step by step"

    Numbers above vertices are distances. Blue vertices wait in the queue; orange is being explored; purple edges
    form the shortest-path tree.

    <div class="cs-anim" data-anim="bfs"></div>

??? info "Variations and related ideas"

    - **Multi-source BFS:** put several starts in the queue at distance 0 (distance to the nearest fire exit, the
      nearest shop).
    - **0-1 BFS:** for weights 0 and 1, push 0-edges to the front of a deque and 1-edges to the back: $O(V + E)$.
    - **Bidirectional BFS:** search from both ends and meet in the middle; for branching factor $b$ and distance
      $d$, about $2b^{d/2}$ vertices instead of $b^d$.
    - **BFS on implicit graphs:** the states of a Rubik's cube or a sliding puzzle are generated on the fly.

## See also

- [Depth-first search](dfs.md): the other way to explore
- [Dijkstra's algorithm](dijkstra.md): BFS for weighted edges, with a heap instead of a queue
- [Stack and queue](../data-structures/stack-queue.md)

## References

- E. F. Moore, "The shortest path through a maze", *Proceedings of the International Symposium on the Theory of Switching*, Harvard, 1959.
- T. H. Cormen et al., *Introduction to Algorithms*, 4th ed., §20.2 (breadth-first search).
