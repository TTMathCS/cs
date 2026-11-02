# Depth-first search

*Explore a graph like a maze: keep going forward along unvisited paths; at a dead end, back up to the last place
with an unexplored turning and try it.*

| Time | Extra space | Finds |
|---|---|---|
| $O(V + E)$ | $O(V)$ (the stack) | reachability, components, cycles, and the order used by many other algorithms |

## The idea

Exploring a maze with a ball of string, you follow one corridor as far as it goes. When everything ahead is
explored, you wind the string back to the last junction with an untried corridor. That is depth-first search. The
string is a **stack**: recursion keeps it for you (the call stack), or you keep one yourself.

DFS does not find shortest paths, but the *shape* of its search carries a lot of information. It visits each
vertex once and walks each edge once or twice, and the times at which vertices are **entered** and **finished**
reveal cycles, give [topological orders](topological-sort.md), and find
[strongly connected components](scc.md), bridges and articulation points.

## How it works

`visit(u)`: mark `u` seen; for each neighbour `v` of `u`, if `v` is not seen, `visit(v)`.

To cover a whole graph, call `visit` on each vertex not yet seen; each call explores one connected component.

## Code

Four uses: the recursive order, the same order with an explicit stack, labelling connected components, and
detecting a cycle in an undirected graph.

=== "Python"

    ```python
    --8<-- "graphs/dfs.py"
    ```

=== "Java"

    ```java
    --8<-- "graphs/Dfs.java"
    ```

=== "C++"

    ```cpp
    --8<-- "graphs/dfs.cpp"
    ```

Output: the visiting order `[0, 1, 3, 2, 5, 4]` both ways; `2` components; `True` (the graph has the cycle
0–1–3–2–0) and `False` for a tree.

## When to use it

- **Is $t$ reachable from $s$?** **How many connected parts?** (Either BFS or DFS works.)
- **Cycles:** in an undirected graph, an edge to a seen vertex that is not your parent; in a directed graph, an
  edge back into the current path.
- **[Topological sort](topological-sort.md)**, **[strongly connected components](scc.md)**, bridges and
  articulation points (Tarjan's low-link values).
- **Exploring all possibilities** with [backtracking](../backtracking/index.md): DFS over a tree of choices.
- **Maze generation** (randomized DFS makes long winding corridors).

## Common mistakes

- **Recursion depth:** a path-shaped graph with $10^5$ vertices overflows the default stack in Python and often
  in Java. Use the iterative version or raise the limit.
- **Forgetting the parent check** when looking for cycles in an undirected graph: the edge back to your parent
  is not a cycle.
- **Marking too late** in the iterative version, so vertices are pushed many times (harmless for correctness
  here, because of the `if seen: continue`, but it costs memory).
- **Expecting shortest paths:** DFS paths can be very long.

## Going deeper

Each part below starts closed; open the ones you want.

??? example "Sample walkthrough: DFS from 0"

    Neighbour lists: 0: 1, 2 · 1: 0, 3 · 2: 0, 3, 5 · 3: 1, 2, 4 · 4: 3, 5 · 5: 4, 2.

    ```
    visit 0
      visit 1            (0's first neighbour)
        visit 3          (1's next unseen neighbour)
          visit 2        (3's first unseen neighbour)
            visit 5      (2's next unseen neighbour)
              visit 4    (5's first neighbour)
              4 done: all its neighbours are seen
            5 done, 2 done, back in 3: 4 is seen, 3 done
        1 done
      0 done: 2 is already seen
    ```

    Order of first visits: 0, 1, 3, 2, 5, 4.

??? abstract "The math: edge types and the parenthesis theorem"

    Record for each vertex the time it is **entered**, $d[v]$, and **finished**, $f[v]$, using one clock that
    ticks at each event.

    **Parenthesis theorem.** For any two vertices $u, v$, the intervals $[d[u], f[u]]$ and $[d[v], f[v]]$ are
    either disjoint or one contains the other; and $v$ is a descendant of $u$ in the DFS forest exactly when
    $[d[v], f[v]] \subset [d[u], f[u]]$. (Writing "(u" at entry and "u)" at finish gives balanced brackets.)

    **Edge types** in a directed graph, for an edge $u \to v$ met while exploring $u$:

    | When $v$ is ... | Edge type |
    |---|---|
    | unseen | tree edge |
    | entered but not finished (on the current path) | **back edge**: closes a cycle |
    | finished, and $d[u] < d[v]$ | forward edge |
    | finished, and $d[v] < d[u]$ | cross edge |

    **A directed graph has a cycle if and only if DFS finds a back edge.** In an undirected graph only tree and
    back edges exist.

    **White-path theorem.** $v$ becomes a descendant of $u$ exactly when, at time $d[u]$, there is a path from
    $u$ to $v$ through unvisited vertices only.

    **Time.** Each vertex is visited once and each adjacency list scanned once: $O(V + E)$.

??? tip "Watch it step by step"

    Blue vertices are on the call stack (orange: the current one); green ones are finished.

    <div class="cs-anim" data-anim="dfs"></div>

??? info "Variations and related ideas"

    - **Bridges and articulation points** (Hopcroft and Tarjan): with $\text{low}[v]$, the earliest entry time
      reachable by one back edge from $v$'s subtree, an edge $u$–$v$ is a bridge when $\text{low}[v] > d[u]$.
    - **Iterative deepening DFS:** DFS with a depth limit of 1, 2, 3, ...: finds shortest paths with DFS's small
      memory; used in puzzle solvers (IDA*).
    - **Euler tours** (Hierholzer's algorithm) walk every edge exactly once.
    - **Tree traversals** (pre-order, in-order, post-order) are DFS on a tree.

## See also

- [Breadth-first search](bfs.md)
- [Topological sort](topological-sort.md) and [strongly connected components](scc.md): built on DFS
- [Recursion](../foundations/recursion.md) and [backtracking](../backtracking/index.md)

## References

- R. E. Tarjan, "Depth-first search and linear graph algorithms", *SIAM Journal on Computing* 1(2), 1972.
- T. H. Cormen et al., *Introduction to Algorithms*, 4th ed., §20.3 (depth-first search).
