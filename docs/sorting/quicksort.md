# Quicksort

*Pick a pivot. Move everything smaller to its left and everything larger to its right. The pivot is now in its
final place; sort the two sides the same way.*

| Time (average) | Time (worst) | Extra space | Stable | In place |
|---|---|---|---|---|
| $O(n \log n)$ | $O(n^2)$, made very unlikely by a random pivot | $O(\log n)$ stack on average | no | yes |

## The idea

Merge sort does its work *after* splitting (the merge). Quicksort does it *before*: it **partitions** the list
around one value, the pivot, so that nothing ever has to be merged. After partitioning, the pivot sits exactly
where it belongs in the sorted list, every value on its left is smaller and every value on its right is at least
as large. Sorting the left part and the right part separately finishes the job.

When the pivot lands near the middle, each split halves the problem and quicksort runs in $O(n \log n)$. When it
lands at an end every time (for example, always picking the last value of a list that is already sorted), each
split peels off just one value and it degrades to $O(n^2)$. Picking the pivot **at random** makes that bad case
astronomically unlikely, whatever the input.

Quicksort was invented by Tony Hoare in 1959. With small refinements it is the fastest general-purpose sort in
practice, because its inner loop is tiny and it walks memory in order.

## How it works (Lomuto partition)

1. If the range has fewer than 2 values, stop.
2. Take the pivot `p = a[hi]` (for the random version, first swap a random value into `a[hi]`).
3. Keep a boundary `i = lo`: everything in `a[lo..i-1]` is less than `p`.
4. For `j` from `lo` to `hi-1`: if `a[j] < p`, swap `a[i]` and `a[j]` and move `i` on.
5. Swap the pivot into `a[i]`. Now `a[i]` is final.
6. Quicksort `a[lo..i-1]` and `a[i+1..hi]`.

## Code

=== "Python"

    ```python
    --8<-- "sorting/quicksort.py"
    ```

=== "Java"

    ```java
    --8<-- "sorting/Quicksort.java"
    ```

=== "C++"

    ```cpp
    --8<-- "sorting/quicksort.cpp"
    ```

Each program prints `[10, 30, 40, 50, 70, 80, 90]`, `[3, 9, 10, 27, 38, 43, 82]` and `[1, 2, 4, 5, 5, 5, 8]`.

## When to use it

- **General sorting in memory, when stability does not matter.** It is the base of C++'s `std::sort`
  (introsort) and Java's `Arrays.sort` for primitive arrays (dual-pivot quicksort).
- **Quickselect**, its one-sided cousin, finds the $k$-th smallest value in $O(n)$ on average.
- Avoid the plain last-value pivot on data that may already be sorted, and avoid quicksort where an attacker
  chooses the input and a worst case matters (use introsort or merge sort).

## Common mistakes

- **A fixed pivot on sorted input:** $O(n^2)$ time and $n$-deep recursion, which can overflow the stack.
- **Many equal values:** Lomuto partition puts all copies of the pivot on one side, so a list of identical
  values takes $O(n^2)$. Use a three-way partition (below) or Hoare's partition.
- **Deep recursion:** recurse into the *smaller* side first and loop on the larger one; the stack then never
  goes deeper than $\log_2 n$.
- Off-by-one errors in the ranges: here `lo` and `hi` are both included.

## Going deeper

Each part below starts closed; open the ones you want.

??? example "Sample walkthrough: partitioning [10, 80, 30, 90, 40, 50, 70]"

    Pivot $p = 70$. `i` marks where the next small value goes.

    | `j` | `a[j]` | `a[j] < 70`? | Action | List | `i` after |
    |---|---|---|---|---|---|
    | 0 | 10 | yes | swap a[0], a[0] | `10 80 30 90 40 50 70` | 1 |
    | 1 | 80 | no | — | `10 80 30 90 40 50 70` | 1 |
    | 2 | 30 | yes | swap a[1], a[2] | `10 30 80 90 40 50 70` | 2 |
    | 3 | 90 | no | — | `10 30 80 90 40 50 70` | 2 |
    | 4 | 40 | yes | swap a[2], a[4] | `10 30 40 90 80 50 70` | 3 |
    | 5 | 50 | yes | swap a[3], a[5] | `10 30 40 50 80 90 70` | 4 |
    | end | | | swap pivot into a[4] | `10 30 40 50 70 90 80` | |

    70 is final at position 4. Next: quicksort `[10, 30, 40, 50]` and `[90, 80]`.

??? abstract "The math: best, worst and average case"

    **Best case** (pivot always the median): $T(n) = 2T(n/2) + \Theta(n) = \Theta(n \log n)$, as for
    [merge sort](merge-sort.md).

    **Worst case** (pivot always the smallest or largest):

    $$
    T(n) = T(n-1) + \Theta(n) \;\Longrightarrow\; T(n) = \Theta\!\left(\sum_{k=1}^{n} k\right) = \Theta(n^2).
    $$

    **Average case with a random pivot.** Let $z_1 < z_2 < \cdots < z_n$ be the values in sorted order. Two values
    $z_i$ and $z_j$ ($i<j$) are compared **only if** one of them is the first pivot chosen among
    $z_i, z_{i+1}, \ldots, z_j$; otherwise a pivot between them separates them forever. Each of those $j-i+1$
    values is equally likely to be chosen first, so

    $$
    \Pr[z_i \text{ and } z_j \text{ compared}] = \frac{2}{j-i+1}.
    $$

    Adding over all pairs (linearity of expectation),

    $$
    \mathbb{E}[C] = \sum_{i<j} \frac{2}{j-i+1} \le 2n \sum_{k=2}^{n} \frac1k < 2n \ln n \approx 1.39\, n \log_2 n.
    $$

    So random-pivot quicksort makes about 39% more comparisons than the best possible, but each one is cheap. The
    chance of being much slower than this falls off exponentially.

    **Stack depth.** Recursing on the smaller side first bounds the depth by $\log_2 n$, since each nested call
    handles at most half of its parent's range.

??? tip "Watch it step by step"

    Blue is the pivot; `i` marks the end of the small side and `j` the value being checked; green values are final.

    <div class="cs-anim" data-anim="quicksort"></div>

??? info "Variations and related ideas"

    - **Hoare partition** (the original) moves two pointers towards each other and swaps pairs that are on the
      wrong sides. It makes about three times fewer swaps than Lomuto and handles equal values better.
    - **Three-way partition** (Dijkstra's "Dutch national flag"): split into $< p$, $= p$ and $> p$. Lists with
      many repeated values become fast, even linear when there are only a few distinct values.
    - **Median of three:** use the median of the first, middle and last values as the pivot. Cheap and good on
      real data, but specially built inputs can still defeat it.
    - **Introsort** (Musser, 1997): quicksort that switches to [heapsort](heapsort.md) if the recursion gets deeper
      than about $2\log_2 n$, so the worst case is $O(n \log n)$. This is C++'s `std::sort`.
    - **Dual-pivot quicksort** (Yaroslavskiy, 2009) splits into three parts with two pivots; Java has used it for
      primitive arrays since Java 7.
    - **Quickselect** recurses into only the side that contains position $k$: $O(n)$ on average to find the
      $k$-th smallest. The **median of medians** pivot makes it $O(n)$ in the worst case too.

## See also

- [Merge sort](merge-sort.md): guaranteed $O(n \log n)$ and stable, but needs extra memory
- [Heapsort](heapsort.md): the fallback inside introsort
- [Recursion](../foundations/recursion.md)

## References

- C. A. R. Hoare, "Quicksort", *The Computer Journal* 5(1), 1962, pp. 10–16.
- T. H. Cormen et al., *Introduction to Algorithms*, 4th ed., Chapter 7 and §9.2 (randomized select).
- R. Sedgewick, K. Wayne, *Algorithms*, 4th ed., §2.3.
- D. R. Musser, "Introspective Sorting and Selection Algorithms", *Software: Practice and Experience* 27(8), 1997.
