# Topological sort

*Put the tasks of a project in an order where every task comes after the tasks it depends on. Possible exactly
when the dependencies have no cycle.*

| Time | Extra space | Input | Output |
|---|---|---|---|
| $O(V + E)$ | $O(V)$ | a directed graph | an order of the vertices, or "there is a cycle" |

## The idea

To get dressed, socks come before shoes and the shirt before the tie. To study algorithms you need programming
and data structures first. These "must come before" rules are arrows of a directed graph, and a **topological
order** lists the vertices so that every arrow points forward.

**Kahn's algorithm** (1962) does what you would do by hand. Count, for each task, how many unfinished tasks it
waits for (its **in-degree**). Any task waiting for nothing can go next. Doing it removes its arrows, which may
free other tasks. If at some point tasks remain but none is free, the remaining ones wait on each other in a
**cycle**, and no order exists.

**The DFS method** is just as short: run [depth-first search](dfs.md) and list the vertices in **reverse order of
finishing**. A vertex finishes only after everything it points to has finished, so it ends up in front of all of
them.

## How it works (Kahn)

1. Compute every in-degree; queue every vertex with in-degree 0.
2. While the queue is not empty: take `u`, append it to the order, and for each arrow `u → v` lower `indeg[v]`
   by one; if it reaches 0, queue `v`.
3. If the order has fewer than $V$ vertices, the graph has a cycle.

## Code

The demo orders six courses: 0 maths, 1 programming, 2 data structures, 3 algorithms, 4 databases, 5 machine
learning.

=== "Python"

    ```python
    --8<-- "graphs/topological_sort.py"
    ```

=== "Java"

    ```java
    --8<-- "graphs/TopologicalSort.java"
    ```

=== "C++"

    ```cpp
    --8<-- "graphs/topological_sort.cpp"
    ```

Output: Kahn gives `[0, 1, 2, 3, 4, 5]`, DFS gives `[1, 2, 4, 0, 3, 5]` (a different order that is just as
valid), and the 3-cycle has no order: `None`.

## When to use it

- **Build systems** (make, Bazel, compilers ordering modules), **package managers** installing dependencies
  first, **spreadsheets** recalculating cells in order.
- **Course planning**, project scheduling, and the **critical path** (the longest path in the task graph
  decides the shortest possible project time).
- **Shortest and longest paths in a DAG** in $O(V + E)$: relax edges in topological order.
- **Detecting cycles** in dependencies ("circular import").
- As a first step for [dynamic programming](../dp/index.md) on a DAG: every DP is a walk over its subproblems in
  topological order.

## Common mistakes

- **Not checking for a cycle:** Kahn's algorithm silently returns a short list.
- **Reversing the arrows** by mistake ("A depends on B" means the arrow is B → A when "before" is the direction).
- **In the DFS method, forgetting to reverse** the finishing order.
- **Expecting one answer:** most graphs have many valid orders; if you need a specific one (say the smallest
  number first), use a min-heap instead of the queue in Kahn's algorithm.

## Going deeper

Each part below starts closed; open the ones you want.

??? example "Sample walkthrough: Kahn on the six courses"

    Arrows: maths → algorithms, maths → ML, programming → data structures, data structures → algorithms,
    data structures → databases, algorithms → ML.

    | Take | In-degrees after (0..5) | Newly free | Queue |
    |---|---|---|---|
    | — | `0, 0, 1, 2, 1, 2` | maths, programming | 0, 1 |
    | maths (0) | `-, 0, 1, 1, 1, 1` | — | 1 |
    | programming (1) | `-, -, 0, 1, 1, 1` | data structures | 2 |
    | data structures (2) | `-, -, -, 0, 0, 1` | algorithms, databases | 3, 4 |
    | algorithms (3) | `-, -, -, -, 0, 0` | ML | 4, 5 |
    | databases (4) | | — | 5 |
    | ML (5) | | — | empty |

??? abstract "The math: existence, correctness and counting"

    **A topological order exists if and only if the graph has no directed cycle.** If there is a cycle
    $v_1 \to v_2 \to \cdots \to v_k \to v_1$, each $v_i$ must come before $v_{i+1}$ and $v_k$ before $v_1$:
    impossible. Conversely, a DAG always has a vertex with in-degree 0 (follow arrows backwards; with no cycle
    you must stop), so you can put it first, delete it, and repeat on the smaller DAG.

    **Kahn is correct.** A vertex is output only when all its predecessors have been output, so all arrows point
    forward. If a cycle exists, no vertex on it can ever reach in-degree 0, so fewer than $V$ vertices are output.

    **DFS is correct.** For any arrow $u \to v$ in a DAG, $f[v] < f[u]$: when DFS meets the arrow, $v$ is either
    unseen (it is then finished inside $u$'s call) or already finished; it cannot be on the current path, as that
    would be a cycle. So sorting by decreasing finish time puts $u$ before $v$.

    **Time.** Each vertex is queued once and each arrow decreases one in-degree once: $O(V + E)$.

    **How many orders?** Counting topological orders is #P-complete in general (Brightwell and Winkler, 1991);
    listing them all is a [backtracking](../backtracking/index.md) job.

??? tip "Watch it step by step"

    Numbers are the arrows still coming in. Blue vertices are free to go next; purple is the one just taken;
    removed arrows fade.

    <div class="cs-anim" data-anim="topological-sort"></div>

??? info "Variations and related ideas"

    - **Lexicographically smallest order:** a min-heap in place of the queue, $O(V \log V + E)$.
    - **Parallel scheduling:** process Kahn's queue in rounds; the number of rounds is the length of the longest
      path, the least time with unlimited workers.
    - **Critical path method (CPM)** and **PERT** in project management.
    - **Tarjan's SCC algorithm** outputs the components of any directed graph in reverse topological order.

## See also

- [Depth-first search](dfs.md)
- [Strongly connected components](scc.md): what to do when there *are* cycles
- [Dynamic programming](../dp/index.md): DP is a computation in topological order

## References

- A. B. Kahn, "Topological sorting of large networks", *Communications of the ACM* 5(11), 1962.
- T. H. Cormen et al., *Introduction to Algorithms*, 4th ed., §20.4 (topological sort).
- D. E. Knuth, *The Art of Computer Programming, Vol. 1*, 3rd ed., §2.2.3.
