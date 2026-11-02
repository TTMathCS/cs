# Prim's algorithm

*Grow a minimum spanning tree from one vertex: again and again, add the cheapest edge that connects the tree to a
vertex outside it.*

| Time (binary heap) | Time (array, dense graphs) | Extra space | Output |
|---|---|---|---|
| $O(E \log V)$ | $O(V^2)$ | $O(V + E)$ | a minimum spanning tree |

## The idea

[Kruskal](kruskal.md) builds many little trees and merges them. Prim builds **one** tree and lets it grow, like a
crystal. At each step the tree is one side of a cut, the rest of the graph the other side, and the cheapest edge
across that cut is always safe to add (the cut property on the [Kruskal page](kruskal.md)).

To find the cheapest edge leaving the tree quickly, keep the candidate edges in a
[min-heap](../data-structures/binary-heap.md). When a vertex joins the tree, push all its edges to vertices still
outside. Popped edges whose far end is already inside are skipped.

The code is almost the same as [Dijkstra's](dijkstra.md). The difference is the number used as the key: Dijkstra
uses the **total distance from the start**, Prim only the **weight of the last edge**.

## How it works

1. Push `(0, start, -1)`.
2. While the heap is not empty: pop the cheapest `(w, v, from)`; if `v` is in the tree, skip it. Otherwise add
   `v` (and the edge `from–v`) to the tree, and push `(weight, x, v)` for every edge to an `x` not in the tree.

## Code

=== "Python"

    ```python
    --8<-- "graphs/prim.py"
    ```

=== "Java"

    ```java
    --8<-- "graphs/Prim.java"
    ```

=== "C++"

    ```cpp
    --8<-- "graphs/prim.cpp"
    ```

Output: total weight `37`, the same as Kruskal, with the edges in the order the tree grew:
`(0, 1, 4), (1, 2, 8), (2, 8, 2), (2, 5, 4), (5, 6, 2), (6, 7, 1), (2, 3, 7), (3, 4, 9)`. The tree differs from
Kruskal's in one edge (1–2 instead of 0–7, both weight 8): two different minimum spanning trees with equal total.

## When to use it

- **Dense graphs** (many edges per vertex): with an adjacency matrix and a plain array of best edges, Prim is
  $O(V^2)$ with no heap and no sorting, which beats Kruskal's $O(E \log E)$ when $E \approx V^2$.
- **Points in the plane** where every pair is an edge: the $O(V^2)$ version needs no edge list at all.
- **When you want the tree to grow from a chosen place**, for example a network built outwards from a power
  station.

## Common mistakes

- **Using the distance from the start as the key** (that is Dijkstra) instead of the edge weight.
- **Not skipping vertices already in the tree** when they are popped again.
- **Disconnected graphs:** only the start's component is spanned; check that all $V$ vertices joined.

## Going deeper

Each part below starts closed; open the ones you want.

??? example "Sample walkthrough: from vertex 0"

    | Tree so far | Cheapest edge leaving it | Add | Total |
    |---|---|---|---|
    | {0} | 0–1 (4) | 1 | 4 |
    | {0, 1} | 1–2 (8) or 0–7 (8): tie, the heap picks 1–2 | 2 | 12 |
    | {0, 1, 2} | 2–8 (2) | 8 | 14 |
    | {0, 1, 2, 8} | 2–5 (4) | 5 | 18 |
    | {.., 5} | 5–6 (2) | 6 | 20 |
    | {.., 6} | 6–7 (1) | 7 | 21 |
    | {.., 7} | 2–3 (7) | 3 | 28 |
    | {.., 3} | 3–4 (9) | 4 | 37 |

??? abstract "The math: correctness and running time"

    **Correctness.** Let $S$ be the vertices in the tree. Prim adds a lightest edge crossing the cut
    $(S, V \setminus S)$, and no tree edge crosses that cut, so by the **cut property** (proved on the
    [Kruskal page](kruskal.md)) the tree stays inside some minimum spanning tree at every step. After $V-1$
    additions it *is* one.

    **Time with a binary heap.** Every edge is pushed at most twice (once from each end) and popped at most
    twice: $O(E)$ heap operations of $O(\log E) = O(\log V)$ each, so $O(E \log V)$.

    **Time with an array.** Keep `best[x]` = the lightest edge from the tree to $x$. Each step scans all $V$
    entries for the minimum and updates the new vertex's neighbours: $V$ steps of $O(V)$, so $O(V^2)$, which is
    optimal for dense graphs since the input itself has size $\Theta(V^2)$.

    **With a Fibonacci heap:** $O(E + V \log V)$.

    **Cycle property** (the mirror image): the heaviest edge on any cycle, if strictly heaviest, is in no MST.

??? tip "Watch it step by step"

    Green vertices are in the tree; blue edges wait in the heap; purple edges are in the tree.

    <div class="cs-anim" data-anim="prim"></div>

??? info "Variations and related ideas"

    - **Jarník** described the algorithm in 1930, Prim in 1957 and Dijkstra in 1959, so it is also called the
      Jarník or Prim–Jarník algorithm.
    - **Euclidean MST:** for points in the plane, the MST is a subgraph of the Delaunay triangulation, so it can
      be found in $O(n \log n)$.
    - **MST-based maze generation:** Prim on a grid with random weights draws a maze.

## See also

- [Kruskal's algorithm](kruskal.md)
- [Dijkstra's algorithm](dijkstra.md): the same skeleton for shortest paths
- [Binary heap](../data-structures/binary-heap.md)

## References

- R. C. Prim, "Shortest connection networks and some generalizations", *Bell System Technical Journal* 36(6), 1957.
- V. Jarník, "O jistém problému minimálním", *Práce Moravské Přírodovědecké Společnosti* 6, 1930.
- T. H. Cormen et al., *Introduction to Algorithms*, 4th ed., Chapter 21 (minimum spanning trees).
