# Binary search tree

*A tree where everything in a node's left branch is smaller than it and everything in its right branch is larger.
Searching is a walk from the root: go left or right at each node, like [binary search](../searching/binary-search.md),
but the data can change.*

| Search / insert / delete | Worst case (unbalanced) | In-order walk | Extra space |
|---|---|---|---|
| $O(h)$; $O(\log n)$ when balanced | $O(n)$ (a tree that is a line) | $O(n)$, in sorted order | one node per key |

## The idea

A sorted array gives $O(\log n)$ search but $O(n)$ insertion (everything must shift). A linked list gives $O(1)$
insertion but $O(n)$ search. A **binary search tree** (BST) gets the best of both, provided it stays bushy.

Each node holds a key and up to two children. The **BST rule**: every key in the left subtree is smaller, every
key in the right subtree is larger. So:

- **Search:** at each node, stop if equal; go left if the key is smaller, right if larger.
- **Insert:** search for the key; where the search falls off the tree, hang a new node.
- **Delete:** a leaf just goes; a node with one child is replaced by that child; a node with **two** children
  takes the key of its **successor** (the smallest key in its right subtree), which is then deleted from there.
- **In-order walk** (left subtree, node, right subtree) lists the keys in sorted order.

Everything costs $O(h)$ where $h$ is the height. Random insertions keep $h$ around $2\ln n$, but inserting keys
**in sorted order** builds a line with $h = n$. **Self-balancing** trees (AVL, red-black) fix this by rotating
nodes after each change, guaranteeing $h = O(\log n)$. Java's `TreeMap` and C++'s `std::map` are red-black trees.

## How it works

- `insert(node, k)`: empty → new node; `k < node.key` → insert left; `k > node.key` → insert right.
- `delete(node, k)`: find it; 0 or 1 child → return the other child; 2 children → copy the successor's key in and
  delete the successor from the right subtree.

## Code

=== "Python"

    ```python
    --8<-- "data-structures/bst.py"
    ```

=== "Java"

    ```java
    --8<-- "data-structures/Bst.java"
    ```

=== "C++"

    ```cpp
    --8<-- "data-structures/bst.cpp"
    ```

Output: the in-order walk `[20, 30, 35, 40, 50, 60, 70, 80]` with height 4; `True False` for 60 and 65; three
deletions (a leaf, a node with two children, then the root, whose place 60 takes); and a height of **7** when
1..7 are inserted in order: the tree has become a list.

## When to use it

- **Ordered data that changes:** a leaderboard, an order book, a calendar of events.
- **Queries a hash table cannot answer:** the smallest key $\ge x$ (`ceiling`, `lower_bound`), the keys in a
  range, the $k$-th smallest (with subtree sizes stored).
- In practice, use the library's balanced tree (`TreeMap`, `std::map`, `std::set`; in Python, the
  `sortedcontainers` package or `bisect` on a list for small data).

## Common mistakes

- **Sorted input into a plain BST:** the tree degenerates into a list, and everything becomes $O(n)$.
- **Forgetting to return the (possibly new) root** from `insert` and `delete`, so the change is lost.
- **Duplicates:** decide whether they are ignored (as here), counted, or always sent one way.
- **Recursion depth** on a degenerate tree of $10^5$ nodes overflows the stack.

## Going deeper

Each part below starts closed; open the ones you want.

??? example "Sample walkthrough: insert 50, 30, 70, 20, 40, 60, 80, 35, then delete 30"

    ```
              50
            /    \
          30      70
         /  \    /  \
       20   40  60   80
           /
         35
    ```

    **Delete 30** (two children): its successor is the smallest key in its right subtree, 35. Copy 35 into
    30's node, then delete the old 35 (a leaf):

    ```
              50
            /    \
          35      70
         /  \    /  \
       20   40  60   80
    ```

??? abstract "The math: height, and why random trees are shallow"

    **Height bounds.** A binary tree of height $h$ holds at most $2^h - 1$ nodes, so $h \ge \lceil \log_2(n+1) \rceil$.
    A chain has $h = n$. So $\log_2 n \lesssim h \le n$.

    **Random insertion order.** If the $n$ keys arrive in a uniformly random order, the expected depth of a node
    is $2 \ln n + O(1) \approx 1.39 \log_2 n$, and the expected height is about $4.311 \ln n$ (Devroye, 1986).
    The proof mirrors [quicksort](../sorting/quicksort.md): keys $i < j$ are in an ancestor relationship exactly
    when one of them is inserted first among the keys $i, \ldots, j$, which happens with probability
    $\frac{2}{j - i + 1}$, so the total depth is

    $$
    \mathbb{E}\Big[\sum_{\text{nodes}} \text{depth}\Big] = \sum_{i<j} \frac{2}{j-i+1} \approx 2n \ln n.
    $$

    **AVL trees** keep the heights of every node's two subtrees within 1 of each other. The fewest nodes in an
    AVL tree of height $h$ satisfies $N(h) = N(h-1) + N(h-2) + 1$, a Fibonacci recurrence, so
    $N(h) \ge \varphi^{h} / \sqrt5 - 1$ and

    $$
    h < 1.4405 \log_2 (n + 2).
    $$

    **Red-black trees** colour nodes so that no red node has a red child and every root-to-leaf path has the same
    number of black nodes; this gives $h \le 2 \log_2(n + 1)$.

??? tip "Watch it step by step"

    Orange nodes are compared on the way down; blue is the new node.

    <div class="cs-anim" data-anim="bst"></div>

??? info "Variations and related ideas"

    - **AVL trees** (Adelson-Velsky and Landis, 1962) and **red-black trees** (Bayer 1972; Guibas and Sedgewick
      1978): rotations keep them balanced.
    - **Treaps** give each node a random priority and keep them in heap order: balanced with high probability.
    - **Splay trees** move every accessed node to the root: $O(\log n)$ amortized, and fast for repeated access.
    - **B-trees** have many keys per node, so a lookup reads few disk blocks; every database index and file
      system uses them.
    - **Order statistics:** store subtree sizes to find the $k$-th smallest key, or a key's rank, in $O(h)$.

## See also

- [Binary search](../searching/binary-search.md): the same idea on a static array
- [Hash table](hash-table.md): faster for exact look-ups, but unordered
- [Binary heap](binary-heap.md): a weaker order that is cheaper to keep

## References

- T. H. Cormen et al., *Introduction to Algorithms*, 4th ed., Chapter 12 (binary search trees) and Chapter 13 (red-black trees).
- G. M. Adelson-Velsky, E. M. Landis, "An algorithm for the organization of information", *Soviet Mathematics Doklady* 3, 1962.
- L. Devroye, "A note on the height of binary search trees", *Journal of the ACM* 33(3), 1986.
