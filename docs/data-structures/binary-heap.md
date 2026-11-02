# Binary heap

*A tree kept "roughly sorted": every parent is smaller than its children, so the smallest value is always on
top. Adding a value or taking the smallest costs only $O(\log n)$, and the whole tree lives in a plain array.*

| Push | Pop smallest | Peek smallest | Build from $n$ values | Extra space |
|---|---|---|---|---|
| $O(\log n)$ | $O(\log n)$ | $O(1)$ | $O(n)$ | none beyond the array |

## The idea

A hospital's emergency room does not serve patients in arrival order; it serves the most urgent first. That is
a **priority queue**, and the binary heap is the standard way to build one.

A **min-heap** is a binary tree with two rules:

1. **Shape:** every level is full except perhaps the last, which fills from the left. So a heap of $n$ values
   has height $\lfloor \log_2 n \rfloor$.
2. **Order:** every parent is $\le$ its children. So the root is the minimum. (Siblings are in no particular
   order: a heap is much less sorted than a sorted list, which is why it is cheaper to maintain.)

Because of the shape rule, the tree fits in an array with no pointers: the root is at 0, and the node at $i$ has
children at $2i+1$ and $2i+2$ and its parent at $\lfloor (i-1)/2 \rfloor$.

- **Push:** put the new value at the end (the next free leaf) and **sift it up**: swap it with its parent while
  it is smaller.
- **Pop:** take the root, move the last value to the root, and **sift it down**: swap it with its smaller child
  while it is larger.

Each sift walks one path between the root and a leaf: $O(\log n)$.

## How it works

- `push(x)`: `a.append(x)`; `i = len(a)-1`; while `i > 0` and `a[parent(i)] > a[i]`: swap, `i = parent(i)`.
- `pop()`: save `a[0]`; `a[0] = a.pop()`; sift down from 0; return the saved value.

## Code

=== "Python"

    ```python
    --8<-- "data-structures/binary_heap.py"
    ```

=== "Java"

    ```java
    --8<-- "data-structures/BinaryHeap.java"
    ```

=== "C++"

    ```cpp
    --8<-- "data-structures/binary_heap.cpp"
    ```

Output: the heap as stored, `[1, 3, 2, 5, 9, 8, 7]` (not sorted, but every parent is smaller than its children);
then the pops in order `[1, 2, 3, 5, 7, 8, 9]`; then `[45, 40, 33]`, the three largest of a stream, found while
keeping only 3 values in memory.

## When to use it

- **Repeatedly taking the smallest (or largest):** [Dijkstra](../graphs/dijkstra.md), [Prim](../graphs/prim.md),
  [Huffman coding](../greedy/huffman.md), event simulations, operating-system schedulers.
- **Top $k$ of a stream:** keep a min-heap of size $k$; $O(n \log k)$ time, $O(k)$ memory.
- **Merging $k$ sorted lists:** heap of the current front of each list, $O(n \log k)$.
- **Running median:** a max-heap for the lower half and a min-heap for the upper half.
- **Sorting:** [heapsort](../sorting/heapsort.md).

In the libraries: Python's `heapq` (a min-heap on a list), Java's `PriorityQueue` (min-heap), C++'s
`std::priority_queue` (a **max**-heap by default; use `greater<int>` for a min-heap).

## Common mistakes

- **Expecting the array to be sorted.** Only the root is guaranteed; use pops to get sorted order.
- **Changing a value inside the heap** without sifting it: the order rule breaks silently. Libraries do not
  support "decrease key"; the usual trick is to push the new value and skip stale entries when they are popped
  (as in [Dijkstra](../graphs/dijkstra.md)).
- **Max versus min:** C++ is max by default; Python and Java are min. For a max-heap in Python, push $-x$.
- **Off-by-one in the index formulas** when switching between 0-based and 1-based arrays.

## Going deeper

Each part below starts closed; open the ones you want.

??? example "Sample walkthrough: push 5, 3, 8, 1, 9, 2, 7"

    | Push | Array after the push | Sift up |
    |---|---|---|
    | 5 | `[5]` | — |
    | 3 | `[3, 5]` | 3 < 5: swap |
    | 8 | `[3, 5, 8]` | 8 > 3: stays |
    | 1 | `[1, 3, 8, 5]` | 1 < 5, then 1 < 3: two swaps |
    | 9 | `[1, 3, 8, 5, 9]` | 9 > 3: stays |
    | 2 | `[1, 3, 2, 5, 9, 8]` | 2 < 8: swap; 2 > 1: stop |
    | 7 | `[1, 3, 2, 5, 9, 8, 7]` | 7 > 2: stays |

    **Pop:** remove 1, move 7 to the root: `[7, 3, 2, 5, 9, 8]`. Children 3 and 2; the smaller is 2: swap →
    `[2, 3, 7, 5, 9, 8]`. 7's child is 8: stop. The new minimum is 2.

??? abstract "The math: height, costs and building in O(n)"

    **Height.** A heap with height $h$ has between $2^h$ and $2^{h+1} - 1$ nodes, so
    $h = \lfloor \log_2 n \rfloor$. Sift-up and sift-down move at most $h$ levels: $O(\log n)$.

    **Index formulas.** Level $d$ holds positions $2^d - 1$ to $2^{d+1} - 2$. The node at position $i$, the
    $k$-th on its level ($k = i - 2^d + 1$), has its children at the $2k$-th and $(2k+1)$-th places of level
    $d+1$, which are positions $2^{d+1} - 1 + 2k = 2i + 1$ and $2i + 2$.

    **Building a heap from $n$ values** by sifting down every parent from the last one to the root costs

    $$
    \sum_{h=0}^{\lfloor \log_2 n\rfloor} \left\lceil \frac{n}{2^{h+1}} \right\rceil \cdot O(h) = O\!\left(n \sum_{h\ge 0} \frac{h}{2^{h}}\right) = O(n),
    $$

    because few nodes are high up. Pushing the $n$ values one by one costs $O(n \log n)$ in the worst case.

    **Lower bound.** A heap cannot do both push and pop in $o(\log n)$ with comparisons only, or we could
    sort faster than $\Omega(n \log n)$ (push all, pop all).

??? tip "Watch it step by step"

    The tree and, below it, the same heap as an array.

    <div class="cs-anim" data-anim="binary-heap"></div>

??? info "Variations and related ideas"

    - **$d$-ary heap:** $d$ children per node; height $\log_d n$. Cheaper push and decrease-key, dearer pop; with
      $d \approx E/V$ it speeds up Dijkstra on dense graphs.
    - **Indexed heap:** also stores each item's position, so "decrease key" works in $O(\log n)$.
    - **Fibonacci heap:** decrease-key in $O(1)$ amortized, giving Dijkstra $O(E + V \log V)$ in theory; rarely
      faster in practice.
    - **Pairing heaps, leftist and skew heaps, binomial heaps:** heaps that can also be **merged** quickly.

## See also

- [Heapsort](../sorting/heapsort.md): sorting with a heap, in place
- [Dijkstra's algorithm](../graphs/dijkstra.md) and [Huffman coding](../greedy/huffman.md): heaps at work
- [Binary search tree](bst.md): fully ordered, but more work to keep balanced

## References

- J. W. J. Williams, "Algorithm 232: Heapsort", *Communications of the ACM* 7(6), 1964.
- T. H. Cormen et al., *Introduction to Algorithms*, 4th ed., Chapter 6 (heapsort, priority queues).
- R. Sedgewick, K. Wayne, *Algorithms*, 4th ed., §2.4 (priority queues).
