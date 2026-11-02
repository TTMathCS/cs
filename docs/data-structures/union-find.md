# Union-find

*Keep track of which items belong to the same group while groups merge. Each group is a little tree; its root is
the group's leader. Two items are together exactly when they have the same leader.*

| Union | Find (the leader) | Space |
|---|---|---|
| $O(\alpha(n))$ amortized | $O(\alpha(n))$ amortized | $O(n)$ |

$\alpha(n)$ is the inverse Ackermann function, which is at most 4 for any $n$ that fits in the universe: in
practice, constant time.

## The idea

Islands appear on a map one bridge at a time. After each new bridge, can you get from island 3 to island 7?
Re-exploring the whole map after every bridge is slow. **Union-find** (also called a *disjoint-set union*)
answers instantly.

Every item points to a **parent**; a leader points to itself. To **find** an item's leader, follow parents up to
the root. To **union** two groups, find both leaders and make one point to the other.

Two small tricks make the trees almost flat:

- **Union by size:** always hang the smaller tree under the larger one. Then any item's depth is at most
  $\log_2 n$, because each time it gets deeper its group at least doubles.
- **Path compression:** after a find, point every item on the path directly at the leader. Later finds on them
  take one step.

Together they give the astonishing $O(\alpha(n))$ bound, proved by Tarjan in 1975.

## How it works

- `find(x)`: walk up to the root; then walk the path again setting each parent to the root.
- `union(a, b)`: `ra, rb = find(a), find(b)`; if equal, nothing to do; otherwise attach the smaller-size root
  under the larger and add the sizes.

## Code

=== "Python"

    ```python
    --8<-- "data-structures/union_find.py"
    ```

=== "Java"

    ```java
    --8<-- "data-structures/UnionFind.java"
    ```

=== "C++"

    ```cpp
    --8<-- "data-structures/union_find.cpp"
    ```

Output: six unions succeed and `union(3, 0)` returns `False` (0 and 3 were already joined through 1); then
`True False True`; then `groups: 4` ({0,1,2,3}, {4}, {5,6}, {7,8,9}) and the size 4 of 0's group.

## When to use it

- **[Kruskal's minimum spanning tree](../graphs/kruskal.md):** add the cheapest edge that joins two different
  groups.
- **Connected components** of a graph whose edges arrive over time; counting islands; network connectivity.
- **Cycle detection** in an undirected graph: an edge inside one group closes a cycle.
- **Grouping equal things:** accounts that share an email, pixels of one colour region, variables that must be
  equal (type inference, unification).
- It **cannot** split groups apart again; for deletions you need other structures.

## Common mistakes

- **Comparing items instead of leaders:** `parent[a] == parent[b]` is wrong; use `find(a) == find(b)`.
- **Forgetting union by size or rank:** with only path compression it is still fast in practice
  ($O(\log n)$ amortized), but with neither, a chain can make every find $O(n)$.
- **Recursive find on a deep chain** can overflow the stack before compression flattens it; the loop version
  here is safe.
- **Updating the size of the wrong root** after the swap.

## Going deeper

Each part below starts closed; open the ones you want.

??? example "Sample walkthrough: the demo's unions on 10 items"

    | Operation | Leaders found | Result (parent changes) | Groups |
    |---|---|---|---|
    | union(0, 1) | 0, 1 | 1 → 0 | 9 |
    | union(2, 3) | 2, 3 | 3 → 2 | 8 |
    | union(1, 3) | 0, 2 (sizes 2, 2) | 2 → 0 | 7 |
    | union(5, 6) | 5, 6 | 6 → 5 | 6 |
    | union(7, 8) | 7, 8 | 8 → 7 | 5 |
    | union(8, 9) | 7, 9 (sizes 2, 1) | 9 → 7 | 4 |
    | union(3, 0) | 0, 0 | already together: **False** | 4 |

    Finding 3's leader in the last step walks 3 → 2 → 0, then compression sets 3's parent to 0 directly.

??? abstract "The math: why the trees stay shallow"

    **Union by size alone gives depth $\le \log_2 n$.** An item's depth grows by 1 only when its root is hung
    under another root whose tree is at least as big, so the size of the item's group at least doubles. A group
    can double at most $\log_2 n$ times.

    **With path compression too,** any sequence of $m$ finds and unions on $n$ items costs
    $O(m\,\alpha(n))$ (Tarjan, 1975), and this is optimal for this kind of structure (Fredman and Saks, 1989).
    Here $\alpha$ is the inverse of the very fast-growing Ackermann function $A$:

    $$
    \alpha(n) = \min\{k : A(k, k) \ge n\}, \qquad A(4, 4) \gg 2^{2^{2^{65536}}},
    $$

    so $\alpha(n) \le 4$ for every $n$ we could ever store.

    **A simpler bound** with path compression and union by rank is $O(m \log^* n)$, where $\log^* n$ is the
    number of times you must take $\log_2$ to get down to 1: $\log^* 2^{65536} = 5$.

??? tip "Watch it step by step"

    Arrows point from an item to its parent. Blue is the new group's leader, red the root that was hung under it.

    <div class="cs-anim" data-anim="union-find"></div>

??? info "Variations and related ideas"

    - **Union by rank** (an upper bound on height) instead of size: the same guarantees.
    - **Path halving / splitting:** point every node to its grandparent while walking up; one pass, same bound.
    - **Weighted union-find** stores, on each edge, an offset to the parent: it answers "how much heavier is $a$
      than $b$?" or checks parity constraints (is this graph bipartite?).
    - **Offline dynamic connectivity** handles deletions by processing queries in a clever order.

## See also

- [Kruskal's algorithm](../graphs/kruskal.md): the classic use
- [Breadth-first search](../graphs/bfs.md): components of a fixed graph in one pass

## References

- R. E. Tarjan, "Efficiency of a good but not linear set union algorithm", *Journal of the ACM* 22(2), 1975.
- B. A. Galler, M. J. Fischer, "An improved equivalence algorithm", *Communications of the ACM* 7(5), 1964.
- T. H. Cormen et al., *Introduction to Algorithms*, 4th ed., Chapter 19 (data structures for disjoint sets).
