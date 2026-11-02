# 0/1 knapsack

*A bag holds at most a certain weight. Each item has a weight and a value, and you either take it or leave it.
Which items give the most value? A table over (items, capacity) answers it.*

| Time | Extra space | Output |
|---|---|---|
| $O(nW)$ for $n$ items and capacity $W$ | $O(nW)$, or $O(W)$ for the value alone | the best value and the items |

## The idea

Trying every subset means $2^n$ choices: for 100 items, about $10^{30}$ of them. Taking items
by best value per kilogram (greedy) fails too: with a bag of 50 and items (10 kg, 60), (20 kg, 100),
(30 kg, 120), greedy takes the first two for 160, while the last two give 220.

DP looks at **one item at a time**. For item $i$ and every capacity $c$, there are only two cases:

- **leave it:** the best is what the earlier items could do with capacity $c$;
- **take it** (if it fits): its value plus the best the earlier items could do with $c - w_i$.

$$\text{best}[i][c] = \max\big(\text{best}[i-1][c],\; \text{best}[i-1][c - w_i] + v_i\big)$$

The table has a row per item and a column per capacity; the answer is in the bottom-right corner.

## How it works

1. Row 0 (no items) is all zeros.
2. For each item `i` and each capacity `c` from 0 to `W`, apply the rule above.
3. To find the items, start at `best[n][W]` and go up row by row: if the value changes from the row above,
   item `i` was taken, so subtract its weight from `c`.
4. **Saving memory:** if only the value is needed, one row is enough, provided `c` goes from **high to low**, so
   each item is counted once (going upwards would let an item be taken again and again: that is
   [coin change](coin-change.md)).

## Code

=== "Python"

    ```python
    --8<-- "dp/knapsack.py"
    ```

=== "Java"

    ```java
    --8<-- "dp/Knapsack.java"
    ```

=== "C++"

    ```cpp
    --8<-- "dp/knapsack.cpp"
    ```

Output: `9 [1, 2]` (items 1 and 2, weights 3 + 4 = 7, values 4 + 5), `220 [1, 2]` for the greedy-trap example,
and `9 220` from the one-row version.

## When to use it

- **Choosing under a budget:** projects with costs and benefits, files to fit on a disk, cargo for a rocket with a
  mass limit.
- **Subset sum:** "can some of these numbers add up to exactly $T$?" is knapsack with value = weight.
- **Splitting into two equal halves** (the partition problem): subset sum with $T$ = half the total.
- **When $W$ is small.** If capacities are huge (say $10^{12}$), the table is too big; then use the
  value-indexed version, meet-in-the-middle, or branch and bound.

## Common mistakes

- **Going upwards in the one-row version:** items get reused.
- **Using greedy by value per weight:** right only for the *fractional* knapsack, where items can be cut.
- **Not handling items heavier than the bag:** the "take" option must check $w_i \le c$.
- **Off-by-one between item numbers and rows:** row $i$ is about item $i - 1$ when items are numbered from 0.

## Going deeper

Each part below starts closed; open the ones you want.

??? example "Sample walkthrough: capacity 7, items (weight, value) = (1, 1), (3, 4), (4, 5), (5, 7)"

    | | cap 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 |
    |---|---|---|---|---|---|---|---|---|
    | no items | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
    | + item 0 (1, 1) | 0 | 1 | 1 | 1 | 1 | 1 | 1 | 1 |
    | + item 1 (3, 4) | 0 | 1 | 1 | 4 | 5 | 5 | 5 | 5 |
    | + item 2 (4, 5) | 0 | 1 | 1 | 4 | 5 | 6 | 6 | **9** |
    | + item 3 (5, 7) | 0 | 1 | 1 | 4 | 5 | 7 | 8 | **9** |

    Two cells explained:

    - Row "item 2", capacity 7: leave it → 5 (from above); take it → best[1][3] + 5 = 4 + 5 = **9**.
    - Row "item 3", capacity 7: leave it → 9; take it → best[2][2] + 7 = 1 + 7 = 8. Keep 9.

    Walking back from 9: the row for item 3 did not change it (9 above), so item 3 is out; item 2 changed it
    (5 → 9), so it is in, leaving capacity 3; item 1 changed best at capacity 3 (1 → 4): in, leaving 0. Items 1 and 2.

??? abstract "The math: correctness, pseudo-polynomial time, and NP-hardness"

    **Correctness.** Let $S$ be a best set of items among the first $i$, within capacity $c$. If item $i$ is not in
    $S$, then $S$ is a best set among the first $i - 1$ with capacity $c$. If it is, then $S$ without item $i$
    must be a best set among the first $i - 1$ with capacity $c - w_i$ (otherwise a better one could replace it).
    So the maximum of the two cases is exactly $\text{best}[i][c]$.

    **Time.** $(n + 1)(W + 1)$ cells, each $O(1)$: $O(nW)$.

    **Pseudo-polynomial.** The input size is about $n \log W$ bits, but the time grows with $W$ itself, which is
    exponential in $\log W$. Knapsack (as a yes/no question "can value $\ge V$ fit?") is **NP-complete**, one of
    Karp's 21 problems (1972), so no algorithm polynomial in $n \log W$ is known.

    **Approximation (FPTAS).** Round each value down to a multiple of $\varepsilon v_{\max} / n$ and run the
    value-indexed DP (`minweight[value]`). This gives a value at least $(1 - \varepsilon)$ times the best in
    $O(n^3 / \varepsilon)$ time.

    **Fractional knapsack.** If items can be cut, sorting by $v_i / w_i$ and filling greedily is optimal, in
    $O(n \log n)$.

??? tip "Watch it step by step"

    Red is the cell being filled; orange is the cell it uses; faded is the option that lost. The purple cells at
    the end show the walk back.

    <div class="cs-anim" data-anim="knapsack"></div>

??? info "Variations and related ideas"

    - **Unbounded knapsack:** unlimited copies of each item; loop capacities upwards.
    - **Bounded knapsack:** at most $k_i$ copies; split each item into pieces of 1, 2, 4, ... copies (binary
      splitting) and run 0/1 knapsack.
    - **Multiple constraints** (weight and volume): one more table dimension.
    - **Meet in the middle:** for $n \le 40$ with huge weights, list all subsets of each half ($2^{20}$ each) and
      combine with sorting and binary search.

## See also

- [Coin change](coin-change.md)
- [Greedy algorithms](../greedy/index.md): the fractional version
- [Binary search](../searching/binary-search.md): used in meet in the middle

## References

- R. M. Karp, "Reducibility among combinatorial problems", in *Complexity of Computer Computations*, 1972.
- H. Kellerer, U. Pferschy and D. Pisinger, *Knapsack Problems*, Springer, 2004.
- T. H. Cormen et al., *Introduction to Algorithms*, 4th ed., Chapter 14 (dynamic programming) and Chapter 15 (greedy).
