# Fenwick tree

*An array of partial sums, each covering a block whose length is a power of two read off the binary digits of
its index. Changing one value and summing a prefix both touch only $\log_2 n$ blocks.*

| Add to one value | Prefix sum | Range sum | Build | Space |
|---|---|---|---|---|
| $O(\log n)$ | $O(\log n)$ | $O(\log n)$ | $O(n \log n)$, or $O(n)$ | $n + 1$ numbers |

Also called a **binary indexed tree** (BIT). Peter Fenwick described it in 1994.

## The idea

You keep running totals of a list of numbers that keeps changing: points in a game per round, sales per day.

- Storing the plain list makes a change $O(1)$ but a sum $O(n)$.
- Storing all prefix sums makes a sum $O(1)$ but a change $O(n)$ (every later prefix shifts).

A Fenwick tree sits in between. Using positions $1..n$, cell $t[i]$ stores the sum of a block that **ends at
$i$** and whose length is $i$'s **lowest set bit**, written $\text{lowbit}(i) = i \,\&\, (-i)$:

| $i$ | binary | lowbit | $t[i]$ covers |
|---|---|---|---|
| 1 | 0001 | 1 | 1 |
| 2 | 0010 | 2 | 1..2 |
| 3 | 0011 | 1 | 3 |
| 4 | 0100 | 4 | 1..4 |
| 6 | 0110 | 2 | 5..6 |
| 7 | 0111 | 1 | 7 |
| 8 | 1000 | 8 | 1..8 |

- **Prefix sum of $1..i$:** add $t[i]$, then drop $i$'s lowest bit and repeat until $i = 0$. For $i = 7$
  (`111`): $t[7] + t[6] + t[4]$, the blocks 7, 5..6 and 1..4.
- **Add to position $i$:** add to $t[i]$, then **add** $i$'s lowest bit and repeat while $i \le n$. Those are
  exactly the blocks that contain $i$.

Both loops run once per binary digit: $O(\log n)$. The whole structure is a dozen lines of code.

## Code

=== "Python"

    ```python
    --8<-- "data-structures/fenwick_tree.py"
    ```

=== "Java"

    ```java
    --8<-- "data-structures/FenwickTree.java"
    ```

=== "C++"

    ```cpp
    --8<-- "data-structures/fenwick_tree.cpp"
    ```

Output: all prefix sums of `[5, 2, 9, -3, 5, 20, 10, -7]`; the range sum of positions 2..5, `31`; after adding
10 to position 3, `41 51`; and the stored array `t`.

## When to use it

- **Prefix and range sums with point updates**, when that is all you need: shorter and faster than a
  [segment tree](segment-tree.md).
- **Counting inversions** in $O(n \log n)$: walk the array, and for each value ask how many larger values were
  already seen.
- **Ranking:** how many values so far are $\le x$; the $k$-th smallest with a binary-lifting walk.
- **Range update with point query:** store differences, so adding to $a[l..r]$ becomes two point adds.
- It does **not** directly support range minimum or maximum with arbitrary updates; use a segment tree.

## Common mistakes

- **0-based indices:** the tree is 1-based; `lowbit(0) = 0`, so a loop on index 0 never ends. Shift by one, as
  the code does.
- **Setting instead of adding:** to set $a[i] = v$, add $v - a[i]$ and keep a copy of $a$.
- **Overflow** of big sums in 32-bit integers.
- **Range sum** is `prefix(r) - prefix(l)`, not `prefix(r) - prefix(l - 1)`, with the half-open convention used
  here.

## Going deeper

Each part below starts closed; open the ones you want.

??? example "Sample walkthrough: prefix(7) and add(position 3, +10)"

    With $a = [5, 2, 9, -3, 5, 20, 10, -7]$ (positions 1..8 inside the tree):

    $t = [5, 7, 9, 13, 5, 25, 10, 41]$, for example $t[6] = a_5 + a_6 = 5 + 20 = 25$ and
    $t[4] = 5 + 2 + 9 - 3 = 13$.

    **prefix(7):** $7 = 111_2 \to t[7] = 10$; drop the low bit, $6 = 110_2 \to t[6] = 25$; drop it, $4 = 100_2 \to t[4] = 13$;
    drop it, 0: stop. Sum $10 + 25 + 13 = 48$, which is $5 + 2 + 9 - 3 + 5 + 20 + 10$.

    **add(+10 at 0-based index 3, so $i = 4$):** $t[4] \mathrel{+}= 10$; $4 + 4 = 8$: $t[8] \mathrel{+}= 10$; $8 + 8 = 16 > 8$:
    stop. Only two cells change.

??? abstract "The math: why the blocks tile and cover correctly"

    **Two's complement.** $-i$ is $\lnot i + 1$, so $i \,\&\, (-i)$ keeps only the lowest set bit of $i$.

    **Prefix query.** Write $i = 2^{k_1} + 2^{k_2} + \cdots + 2^{k_r}$ with $k_1 > k_2 > \cdots > k_r$. The query
    visits $i$, then $i - 2^{k_r}$, and so on, and $t$ at each visited index covers the block of length
    $2^{k_j}$ ending there. These blocks are consecutive and together cover $[1, i]$:

    $$
    \sum_{j=1}^{i} a_j = \sum_{s=1}^{r} t\!\left[2^{k_1} + \cdots + 2^{k_s}\right],
    $$

    with $r \le \lfloor \log_2 i \rfloor + 1$ terms.

    **Update.** Position $p$ lies in block $t[j]$ exactly when $j - \text{lowbit}(j) < p \le j$. Starting at
    $j = p$ and repeatedly adding the lowest bit visits exactly those $j$: each step clears a run of low bits and
    sets the next higher one, so the block length at least doubles, and at most $\lfloor\log_2 n\rfloor + 1$
    blocks are visited.

    **Inversions in $O(n \log n)$.** For each $a_i$ (values compressed to $1..n$), add $i -
    \text{prefix}(a_i)$ (the number of earlier values greater than $a_i$), then `add(a_i, 1)`.

??? tip "Watch it step by step"

    Row 2 shows the block each cell covers. Each new value updates the cells red; the last frame sums a prefix.

    <div class="cs-anim" data-anim="fenwick-tree"></div>

??? info "Variations and related ideas"

    - **$O(n)$ build:** for each $i$, add $t[i]$ into $t[i + \text{lowbit}(i)]$.
    - **Two Fenwick trees** support range update *and* range sum.
    - **2-D Fenwick tree:** sums over rectangles in $O(\log^2 n)$.
    - **Binary lifting** finds the smallest $i$ with prefix sum $\ge s$ in $O(\log n)$ (all values non-negative).

## See also

- [Segment tree](segment-tree.md): more general (min, max, lazy ranges), a little more code
- [Counting sort](../sorting/counting-sort.md): prefix sums as positions

## References

- P. M. Fenwick, "A new data structure for cumulative frequency tables", *Software: Practice and Experience* 24(3), 1994.
- S. Halim, F. Halim, *Competitive Programming 3*, 2013, Chapter 2 (Fenwick tree).
