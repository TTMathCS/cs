# Segment tree

*A tree over an array where every node stores an answer (minimum, sum, maximum, ...) for one range. Any range
breaks into $O(\log n)$ whole nodes, so range questions and single changes are both $O(\log n)$.*

| Point update | Range query | Build | Space |
|---|---|---|---|
| $O(\log n)$ | $O(\log n)$ | $O(n)$ | $\le 4n$ nodes |

## The idea

The root of a segment tree covers the whole array, positions $0..n-1$. Each node's range is split in half
between its two children, down to the leaves, which hold single positions. Each node stores the answer for its
range, here the **minimum**: the root stores the minimum of everything, its children the minimums of the two
halves, and so on.

- **Query $\min(a[l..r])$:** start at the root. A node whose range lies entirely inside $[l, r]$ answers with its
  stored value at once; a node entirely outside answers "infinity"; a node that overlaps partly asks its two
  children. At most four nodes per level are visited.
- **Update $a[i] = v$:** change the leaf, then recompute the minimum in each ancestor on the way back up.

Anything that combines like minimum does (an **associative** operation: sum, max, gcd, product, "count of
zeros") works the same way. With **lazy propagation**, whole ranges can be updated in $O(\log n)$ too.

## How it works

- Node 1 covers $[0, n-1]$; node $k$ covering $[lo, hi]$ has children $2k$ covering $[lo, mid]$ and $2k+1$
  covering $[mid+1, hi]$, where $mid = \lfloor (lo + hi)/2 \rfloor$.
- `build`: leaves take $a[lo]$; inner nodes take the min of their children.
- `query(l, r)`: no overlap → $+\infty$; full cover → stored value; else min of the children's answers.
- `update(i, v)`: recurse to the leaf for $i$, set it, recompute on the way back.

## Code

=== "Python"

    ```python
    --8<-- "data-structures/segment_tree.py"
    ```

=== "Java"

    ```java
    --8<-- "data-structures/SegmentTree.java"
    ```

=== "C++"

    ```cpp
    --8<-- "data-structures/segment_tree.cpp"
    ```

Output for $a = [5, 8, 6, 3, 2, 7, 2, 6]$: `2 5 3 7` (the minimums of $[0,7]$, $[0,2]$, $[1,3]$, $[5,5]$); after
$a[4] = 9$, `3 7`; after $a[3] = 10$, `5 2`.

## When to use it

- **Range minimum / maximum / sum queries on changing data:** game leaderboards over time windows, stock
  prices, scheduling with capacities.
- **Range updates** ("add 5 to every value in $[l, r]$") with lazy propagation.
- **Computational geometry:** area of a union of rectangles, sweep-line counting.
- For **sums only**, a [Fenwick tree](fenwick-tree.md) is shorter. For a **static** array (no updates), a
  sparse table answers range minimum in $O(1)$ after $O(n \log n)$ preparation.

## Common mistakes

- **Array too small:** with this layout, node numbers can reach almost $4n$; allocate `4 * n`.
- **Wrong "no answer" value:** $+\infty$ for min, $-\infty$ for max, 0 for sum. Using 0 for min is a classic bug.
- **Forgetting to recompute** a parent after updating a child.
- **Inclusive versus exclusive** range ends; this page uses inclusive $[l, r]$.

## Going deeper

Each part below starts closed; open the ones you want.

??? example "Sample walkthrough: min of a[1..6] in [5, 8, 6, 3, 2, 7, 2, 6]"

    ```
                     [0..7] 2
               /                  \
         [0..3] 3              [4..7] 2
          /     \               /     \
     [0..1] 5  [2..3] 3    [4..5] 2  [6..7] 2
      /  \      /  \        /  \      /  \
     5    8    6    3      2    7    2    6
    ```

    $[1, 6]$ is covered by the whole nodes **[1]** (leaf 8), **[2..3]** (3), **[4..5]** (2) and **[6]** (leaf 2):
    $\min(8, 3, 2, 2) = 2$. Every other node visited only passes the question down.

??? abstract "The math: why a query touches O(log n) nodes"

    **Height.** Ranges halve at each level, so the tree has height $\lceil \log_2 n \rceil$.

    **At most 4 nodes per level.** At any level, the nodes visited that only *partly* overlap $[l, r]$ can be only
    the ones containing $l$ or $r$: at most 2. Only they recurse, so at most $2 \times 2 = 4$ nodes are visited on
    the next level. A query visits at most $4 \lceil \log_2 n \rceil$ nodes and uses at most
    $2\lceil \log_2 n \rceil$ whole nodes in its answer.

    **Space.** With $h = \lceil \log_2 n \rceil$, node numbers stay below $2^{h+1} < 4n$.

    **Why associativity matters.** A query combines whole-node answers in an order fixed by the tree, so the
    operation $\oplus$ must satisfy $(x \oplus y) \oplus z = x \oplus (y \oplus z)$. Minimum, sum, product of
    matrices and gcd all qualify; average does not (store sum and count instead).

    **Lazy propagation.** For "add $d$ to $[l, r]$", a fully covered node adds $d$ to its stored minimum and
    remembers a pending $+d$ for its children, pushed down only when a later operation needs them. Each update
    still touches $O(\log n)$ nodes.

??? tip "Watch it step by step"

    Small labels show each node's range; the number inside is its stored minimum.

    <div class="cs-anim" data-anim="segment-tree"></div>

??? info "Variations and related ideas"

    - **Iterative (bottom-up) segment tree:** leaves at $n..2n-1$, parents at $i/2$; about half the code and
      faster.
    - **Lazy propagation** for range assignments and range additions.
    - **Persistent segment trees** keep every old version by copying only the $O(\log n)$ changed nodes;
      they answer "$k$-th smallest in a subarray".
    - **Merge sort tree:** each node stores its range sorted; counts values $\le x$ in a range in $O(\log^2 n)$.
    - **Sparse table:** static range minimum in $O(1)$ per query.

## See also

- [Fenwick tree](fenwick-tree.md): simpler, for sums
- [Binary heap](binary-heap.md): the same array-as-tree numbering
- [Recursion](../foundations/recursion.md)

## References

- M. de Berg, O. Cheong, M. van Kreveld, M. Overmars, *Computational Geometry*, 3rd ed., §10.3 (segment trees).
- S. Halim, F. Halim, *Competitive Programming 3*, 2013, Chapter 2 (segment tree).
