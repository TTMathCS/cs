# Strongly connected components

*In a one-way (directed) graph, split the vertices into groups where every vertex can reach every other vertex of
its group. Kosaraju's algorithm does it with two depth-first searches.*

| Time | Extra space | Works on | Output |
|---|---|---|---|
| $O(V + E)$ | $O(V + E)$ | directed graphs | a component number for each vertex |

## The idea

In a directed graph, $u$ reaching $v$ does not mean $v$ reaches $u$. Two vertices are **strongly connected** when
each can reach the other. That splits the graph into **strongly connected components** (SCCs): inside one, you can
go from anywhere to anywhere; between two, you can travel at most one way.

Shrink every component to a single dot and the result has **no cycles**: it is a DAG, the "condensation". That is
why SCCs are so useful: any directed graph becomes a [topological order](topological-sort.md) of tight clusters.

Kosaraju's trick uses this:

1. A [depth-first search](dfs.md) records the order in which vertices **finish**. The vertex that finishes last
   lies in a "source" component, one that no other component points into.
2. **Reverse every arrow.** Now that source component has become a sink: from its vertices, the reversed search
   cannot leak into any other component. So a DFS on the reversed graph, started at the latest finisher, visits
   exactly one component. Mark it, then start again from the latest finisher not yet marked.

## How it works

1. Build the adjacency lists `adj` and the reversed lists `radj`.
2. **Pass 1:** DFS over the whole graph on `adj`; append each vertex to `order` when its search finishes.
3. **Pass 2:** for `u` in `order` from last to first: if `u` has no component yet, DFS from `u` on `radj`,
   giving every vertex it reaches the next component number.

## Code

=== "Python"

    ```python
    --8<-- "graphs/scc.py"
    ```

=== "Java"

    ```java
    --8<-- "graphs/Scc.java"
    ```

=== "C++"

    ```cpp
    --8<-- "graphs/scc.cpp"
    ```

Output: `3 [1, 1, 1, 2, 2, 2, 0, 0]` and then the groups `[[6, 7], [0, 1, 2], [3, 4, 5]]`. Three components:
the cycle 0 → 1 → 2 → 0, the cycle 3 → 4 → 5 → 3, and the pair 6 ⇄ 7. The numbers come out in topological order
of the condensation: component 0 ({6, 7}) points into component 2, and component 1 ({0, 1, 2}) points into
component 2 as well.

## When to use it

- **Finding cycles of dependencies:** in a build system or a spreadsheet, every component with more than one
  vertex is a set of things that all depend on each other.
- **2-SAT:** a set of either/or rules can be satisfied exactly when no variable shares a component with its own
  opposite; the solution is read off the component numbers.
- **Simplifying a directed graph** before another algorithm: work on the condensation DAG, which is smaller and
  has no cycles.
- **Web and social graphs:** the "giant" strongly connected core of the web was found this way.

## Common mistakes

- **Running the second pass on the original graph** instead of the reversed one: it then leaks across components.
- **Taking vertices in the wrong order in pass 2:** it must be the *reverse* of the finishing order, not the order
  vertices were first visited.
- **Deep recursion:** a long chain of vertices overflows the call stack; raise the limit (as the Python code does)
  or write the DFS with an explicit stack.
- **Confusing weak and strong connectivity:** ignoring arrow directions gives weakly connected components, which is
  a plain [BFS](bfs.md) or [union-find](../data-structures/union-find.md) job.

## Going deeper

Each part below starts closed; open the ones you want.

??? example "Sample walkthrough: the 8-vertex example"

    Edges: 0→1, 1→2, 2→0, 2→3, 3→4, 4→5, 5→3, 6→5, 6→7, 7→6.

    **Pass 1** starts at 0 and goes 0 → 1 → 2 → 3 → 4 → 5. Vertex 5's only arrow leads back to 3 (already seen), so 5
    finishes first, then 4, 3, 2, 1, 0. Vertex 6 was never reached, so a new search starts there: 6 → 7, and 7
    finishes, then 6.

    Finishing order: `[5, 4, 3, 2, 1, 0, 7, 6]`.

    **Pass 2** walks that list backwards on the reversed graph:

    | Start (latest free finisher) | Reversed arrows followed | Component |
    |---|---|---|
    | 6 | 6 → 7 (from 7→6); 7 → 6 already marked | 0: {6, 7} |
    | 7 | already marked | |
    | 0 | 0 → 2 (from 2→0), 2 → 1 (from 1→2), 1 → 0 marked | 1: {0, 1, 2} |
    | 1, 2 | already marked | |
    | 3 | 3 → 2 is marked (another component), 3 → 5 (from 5→3), 5 → 4, 5 → 6 marked | 2: {3, 4, 5} |

    Notice how in pass 2 the arrow 3 → 2 and the arrow 5 → 6 are blocked only because those vertices are already
    marked: the reversed search from a sink never needs them.

??? abstract "The math: why the latest finisher works"

    Let $C$ and $C'$ be two different components with an edge from $C$ to $C'$. Write $f(C)$ for the latest
    finishing time of any vertex in $C$.

    **Lemma.** $f(C) > f(C')$.

    *Proof.* If the first search to enter $C \cup C'$ enters at $x \in C$, then all of $C$ and $C'$ is reachable
    from $x$, so all of it finishes before $x$ does, and $f(C) = $ the finish of $x$ $> f(C')$. If instead it
    enters at $y \in C'$, it cannot reach $C$ (otherwise $C$ and $C'$ would be one component), so all of $C'$
    finishes before $C$ is even discovered. Either way $f(C) > f(C')$. $\square$

    So the vertex finishing last overall lies in a component with no incoming edge from another component. In the
    reversed graph its component has **no outgoing edge** to an unmarked component, so the pass-2 search from it
    visits exactly that component. Remove it and repeat: by the lemma the next latest finisher is again in a
    component with no unmarked component pointing into it. Induction on the number of components finishes the
    proof.

    **Time.** Each pass is one DFS, $O(V + E)$; reversing the edges is $O(V + E)$ too. Total $\Theta(V + E)$.

??? tip "Watch it step by step"

    Pass 1 colours vertices green as they finish. Pass 2 colours each component its own colour, edges inside it
    included.

    <div class="cs-anim" data-anim="scc"></div>

??? info "Variations and related ideas"

    - **Tarjan's algorithm** (1972) finds the components with **one** DFS, using the discovery time and a
      "low-link" value for each vertex plus a stack; it gives the components in reverse topological order.
    - **Path-based (Gabow's) algorithm:** one DFS with two stacks, also $O(V + E)$.
    - **Bridges and articulation points** in undirected graphs use the same low-link idea as Tarjan.
    - **Condensation:** after numbering components, add an edge $c(u) \to c(v)$ for every $u \to v$ with
      $c(u) \ne c(v)$; the result is a DAG.

## See also

- [Depth-first search](dfs.md)
- [Topological sort](topological-sort.md)
- [Union-find](../data-structures/union-find.md): connectivity when arrows do not matter

## References

- M. Sharir, "A strong-connectivity algorithm and its applications in data flow analysis", *Computers & Mathematics
  with Applications* 7(1), 1981 (the two-pass method credited to Kosaraju, who did not publish it).
- R. E. Tarjan, "Depth-first search and linear graph algorithms", *SIAM Journal on Computing* 1(2), 1972.
- T. H. Cormen et al., *Introduction to Algorithms*, 4th ed., Chapter 20 (elementary graph algorithms).
