# Heapsort

*Arrange the list into a max-heap, so the largest value is always on top. Swap the top to the end, repair the
heap, and repeat.*

| Time (every case) | Extra space | Stable | In place |
|---|---|---|---|
| $O(n \log n)$ | $O(1)$ | no | yes |

## The idea

[Selection sort](selection-sort.md) spends $O(n)$ finding the largest remaining value, $n$ times. Heapsort finds
it in $O(1)$ and repairs things in $O(\log n)$, by keeping the unsorted part as a **max-heap**: a binary tree in
which every parent is at least as large as its children, so the root is the maximum.

The trick is that the heap needs no pointers. It lives inside the array itself: the children of position $i$ are
positions $2i+1$ and $2i+2$, and the parent of $i$ is $\lfloor (i-1)/2 \rfloor$. See
[binary heap](../data-structures/binary-heap.md) for the data structure on its own.

Heapsort is the only common sort that is $O(n \log n)$ in the worst case **and** needs no extra memory. In
practice it is slower than quicksort because it jumps around the array, which caches dislike.

## How it works

1. **Build the heap.** For every parent position `i` from $\lfloor n/2 \rfloor - 1$ down to 0, *sift down*
   `a[i]`: while it is smaller than its larger child, swap them.
2. **Sort.** For `end` from $n-1$ down to 1:
    1. Swap `a[0]` (the maximum) with `a[end]`. Position `end` is now final.
    2. Sift down `a[0]` within `a[0..end-1]`.

## Code

=== "Python"

    ```python
    --8<-- "sorting/heapsort.py"
    ```

=== "Java"

    ```java
    --8<-- "sorting/Heapsort.java"
    ```

=== "C++"

    ```cpp
    --8<-- "sorting/heapsort.cpp"
    ```

Each program prints `[1, 3, 4, 5, 10]`, `[3, 9, 10, 27, 38, 43, 82]` and `[1, 7, 7]`.

## When to use it

- **A hard $O(n \log n)$ guarantee with $O(1)$ extra memory**, for example in embedded systems or the Linux
  kernel's `sort()`.
- **As a safety net:** introsort switches from quicksort to heapsort when quicksort goes badly.
- **Partial sorting:** build the heap in $O(n)$, then pop only $k$ values: the $k$ largest in $O(n + k \log n)$.

## Common mistakes

- Building the heap by sifting down from position 0 upwards: the order matters, it must go from the last parent
  *down* to 0.
- Sifting down over the whole array instead of only `a[0..end-1]`: it pulls sorted values back into the heap.
- Comparing only with the left child, or swapping with the smaller child (that builds a broken heap).

## Going deeper

Each part below starts closed; open the ones you want.

??? example "Sample walkthrough: [4, 10, 3, 5, 1]"

    **Build:** the last parent is position 1 (value 10, children 5 and 1): it stays. Position 0 (value 4,
    children 10 and 3): swap with 10 → `[10, 4, 3, 5, 1]`; 4 now has children 5 and 1: swap with 5 →
    `[10, 5, 3, 4, 1]`. That is a max-heap.

    **Sort** (final values in bold):

    | Swap top to end | Sift down | Array |
    |---|---|---|
    | 10 ↔ 1 | 1 ↓ 5 ↓ 4 | `5 4 3 1` **10** |
    | 5 ↔ 1 | 1 ↓ 4 | `4 1 3` **5 10** |
    | 4 ↔ 3 | 3 stays | `3 1` **4 5 10** |
    | 3 ↔ 1 | — | `1` **3 4 5 10** |

??? abstract "The math: why building the heap is O(n)"

    **Sift down** costs at most the height of the node, because it moves one level per swap. A heap of $n$ values
    has height $\lfloor \log_2 n \rfloor$.

    **Building the heap** seems to cost $n \log n$, but most nodes are near the bottom. At most
    $\lceil n / 2^{h+1} \rceil$ nodes have height $h$, so the total work is

    $$
    \sum_{h=0}^{\lfloor \log_2 n \rfloor} \left\lceil \frac{n}{2^{h+1}} \right\rceil O(h)
    \;=\; O\!\left(n \sum_{h=0}^{\infty} \frac{h}{2^{h}}\right) \;=\; O(2n) \;=\; O(n),
    $$

    using $\sum_{h \ge 0} h x^h = \frac{x}{(1-x)^2}$ at $x = \tfrac12$, which equals 2.

    **Sorting phase:** $n-1$ sift-downs from the root, each $O(\log n)$: $O(n \log n)$ in total. That bound is
    tight: heapsort takes $\Theta(n \log n)$ even on sorted input.

    **Comparisons.** Each level of a sift-down costs 2 comparisons, so about $2n\log_2 n$ in the worst case.
    **Bottom-up heapsort** first walks the larger children all the way down (1 comparison per level), then climbs
    back to find the spot, cutting this to about $n \log_2 n$.

??? tip "Watch it step by step"

    The array is the heap: position $i$ has children $2i+1$ and $2i+2$. Blue is the value being sifted, orange its
    children, red a swap, green the sorted tail.

    <div class="cs-anim" data-anim="heapsort"></div>

??? info "Variations and related ideas"

    - **Priority queues:** the same heap, with insert and remove-max, is the engine of
      [Dijkstra](../graphs/dijkstra.md), [Prim](../graphs/prim.md), [Huffman coding](../greedy/huffman.md) and
      event simulations.
    - **$d$-ary heaps** give each node $d$ children: a shallower tree, cheaper inserts, dearer removals.
    - **Smoothsort** (Dijkstra, 1981) uses a forest of Leonardo heaps and runs in $O(n)$ on sorted input while
      staying $O(n \log n)$ in the worst case.
    - **Tournament sort** keeps a tree of "winners", like a knockout tournament.

## See also

- [Binary heap](../data-structures/binary-heap.md): the data structure
- [Selection sort](selection-sort.md): the slow version of the same idea
- [Quicksort](quicksort.md): faster on average; introsort combines the two

## References

- J. W. J. Williams, "Algorithm 232: Heapsort", *Communications of the ACM* 7(6), 1964.
- R. W. Floyd, "Algorithm 245: Treesort 3", *Communications of the ACM* 7(12), 1964 (the $O(n)$ heap build).
- T. H. Cormen et al., *Introduction to Algorithms*, 4th ed., Chapter 6.
