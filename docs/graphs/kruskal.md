# Kruskal's algorithm

*To connect every town with the least total length of road: sort all possible roads from shortest to longest, and
build each one unless its two towns are already connected.*

| Time | Extra space | Input | Output |
|---|---|---|---|
| $O(E \log E)$ (the sort) | $O(V + E)$ | a connected, undirected, weighted graph | a minimum spanning tree |

## The idea

A **spanning tree** connects all $V$ vertices using exactly $V - 1$ edges and no cycle. A **minimum spanning
tree** (MST) is one with the smallest total weight: the cheapest way to wire up a network, lay pipes between
habitats, or connect points with cable.

Kruskal's rule is the simplest greedy idea possible: go through the edges from cheapest to most expensive, and
**keep an edge unless it would close a cycle**. To test "would it close a cycle?" quickly, ask whether its two
ends are already in the same group, using [union-find](../data-structures/union-find.md): keeping an edge merges
two groups.

It is not obvious that greed works here, but it does, thanks to the **cut property** (below): the cheapest edge
crossing any division of the vertices into two sides is always safe to take.

## How it works

1. Sort the edges by weight.
2. Start with every vertex in its own group.
3. For each edge $(u, v, w)$ in order: if `find(u) != find(v)`, keep the edge and `union(u, v)`; otherwise skip
   it. Stop after $V - 1$ edges.

## Code

The demo graph is the 9-vertex example used in many textbooks.

=== "Python"

    ```python
    --8<-- "graphs/kruskal.py"
    ```

=== "Java"

    ```java
    --8<-- "graphs/Kruskal.java"
    ```

=== "C++"

    ```cpp
    --8<-- "graphs/kruskal.cpp"
    ```

Output: total weight `37`, and the 8 edges in the order they were chosen:
`(6, 7, 1), (2, 8, 2), (5, 6, 2), (0, 1, 4), (2, 5, 4), (2, 3, 7), (0, 7, 8), (3, 4, 9)`.

## When to use it

- **Designing networks** (electric grids, water pipes, roads, computer networks) at the least total cost.
- **Clustering:** stop Kruskal when $k$ groups remain; the result is the clustering into $k$ groups with the
  largest possible gap between groups (single-linkage clustering).
- **Approximations:** the MST gives a tour at most twice the optimum for the travelling salesman problem with
  triangle-inequality distances.
- When the edges are **already sorted**, or the graph is sparse. For dense graphs, [Prim](prim.md) with an array
  is $O(V^2)$.

## Common mistakes

- **Testing for a cycle with a fresh DFS each time:** correct but $O(VE)$. Use union-find.
- **A disconnected graph:** there is no spanning tree; Kruskal returns a spanning **forest** with fewer than
  $V - 1$ edges. Check the count.
- **Directed graphs:** the MST is defined for undirected graphs; the directed version (arborescence) needs the
  Chu–Liu/Edmonds algorithm.
- **Mixing up MST and shortest paths:** the MST does not give the shortest route between two vertices.

## Going deeper

Each part below starts closed; open the ones you want.

??? example "Sample walkthrough: the 14 edges in order"

    | Edge (weight) | Same group already? | Action | Total |
    |---|---|---|---|
    | 6–7 (1) | no | keep | 1 |
    | 2–8 (2) | no | keep | 3 |
    | 5–6 (2) | no | keep | 5 |
    | 0–1 (4) | no | keep | 9 |
    | 2–5 (4) | no | keep | 13 |
    | 6–8 (6) | yes (8–2–5–6) | skip | 13 |
    | 2–3 (7) | no | keep | 20 |
    | 7–8 (7) | yes | skip | 20 |
    | 0–7 (8) | no | keep | 28 |
    | 1–2 (8) | yes | skip | 28 |
    | 3–4 (9) | no | keep: 8 edges, done | 37 |

    The two edges of weight 8 tie; picking 1–2 instead of 0–7 would give a different tree with the same total.

??? abstract "The math: the cut property"

    A **cut** splits the vertices into two non-empty sides $S$ and $V \setminus S$; an edge **crosses** the cut if
    its ends are on different sides.

    **Cut property.** Let $A$ be a set of edges contained in some MST, and let $e$ be a lightest edge crossing a
    cut that no edge of $A$ crosses. Then $A \cup \{e\}$ is also contained in some MST.

    **Proof (exchange argument).** Let $T$ be an MST containing $A$. If $e \in T$ we are done. Otherwise adding
    $e$ to $T$ creates a cycle, which must cross the cut a second time at some edge $e'$ (not in $A$). Since $e$
    is lightest, $w(e) \le w(e')$, and

    $$
    T' = T - e' + e
    $$

    is a spanning tree with $w(T') \le w(T)$, so it is also an MST, and it contains $A \cup \{e\}$.

    **Kruskal is correct.** When Kruskal keeps edge $(u, v)$, take $S$ = the group of $u$. No kept edge crosses
    this cut, and every lighter edge crossing it would have been kept already, so $(u, v)$ is a lightest edge
    crossing it: the cut property applies at every step.

    **Time.** Sorting is $O(E \log E) = O(E \log V)$ (since $E < V^2$); the $E$ union-find operations cost
    $O(E\,\alpha(V))$.

    **Uniqueness.** If all weights are different, the MST is unique.

??? tip "Watch it step by step"

    Purple edges are kept; red ones are rejected because they would close a cycle.

    <div class="cs-anim" data-anim="kruskal"></div>

??? info "Variations and related ideas"

    - **Prim's algorithm** grows one tree instead of merging a forest: [Prim](prim.md).
    - **Borůvka's algorithm** (1926, the oldest): every group adds its cheapest outgoing edge at once; at most
      $\log_2 V$ rounds, and easy to run in parallel.
    - **Maximum spanning tree:** sort in decreasing order.
    - **Second-best MST**, **minimum bottleneck spanning tree** (every MST is one), and **Steiner trees**
      (connect only some vertices; NP-hard).

## See also

- [Union-find](../data-structures/union-find.md)
- [Prim's algorithm](prim.md)
- [Greedy algorithms](../greedy/index.md): exchange arguments

## References

- J. B. Kruskal, "On the shortest spanning subtree of a graph and the traveling salesman problem", *Proceedings of the AMS* 7(1), 1956.
- T. H. Cormen et al., *Introduction to Algorithms*, 4th ed., Chapter 21 (minimum spanning trees).
