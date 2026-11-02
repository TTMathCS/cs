# Longest increasing subsequence

*From a list of numbers, pick as many as possible, keeping their order, so that each is bigger than the one
before. A simple DP does it in $O(n^2)$; a clever table of "smallest endings" with binary search does it in
$O(n \log n)$.*

| Simple DP | With binary search | Extra space | Output |
|---|---|---|---|
| $O(n^2)$ | $O(n \log n)$ | $O(n)$ | the length and one longest increasing subsequence |

## The idea

In `[10, 9, 2, 5, 3, 7, 101, 18]` the longest increasing subsequence (LIS) has length 4, for example
`2, 3, 7, 18` or `2, 5, 7, 101`.

**The simple DP.** Let `best[i]` be the length of the longest increasing subsequence that **ends at** `a[i]`. It is
1 plus the best `best[j]` over earlier positions `j` with `a[j] < a[i]`. The answer is the largest `best[i]`.

**The fast way.** Read the numbers left to right and keep a list `tails`, where `tails[k]` is the **smallest**
number that can end an increasing subsequence of length $k + 1$ seen so far. A smaller ending is always better,
because it leaves more room for later numbers. Two facts make it fast:

- `tails` is always **sorted**, so the right place for a new number is found by [binary search](../searching/binary-search.md).
- A new number $x$ either **extends** the longest run (it is bigger than every tail) or **replaces** the first tail
  $\ge x$, making that length end lower.

The length of `tails` at the end is the answer.

## How it works

1. For each `x`: find `k`, the first position with `tails[k] >= x`.
2. If `k` is the end of the list, append `x`; otherwise set `tails[k] = x`.
3. To recover the subsequence, remember for each `x` the position of the tail just before it (`tails[k - 1]` at
   that moment), then follow those links back from the last tail.

## Code

=== "Python"

    ```python
    --8<-- "dp/lis.py"
    ```

=== "Java"

    ```java
    --8<-- "dp/Lis.java"
    ```

=== "C++"

    ```cpp
    --8<-- "dp/lis.cpp"
    ```

Output: `4 4 [2, 3, 7, 18]` (both methods give 4) and `6 6 [0, 2, 6, 9, 11, 15]` for a 16-number list.

## When to use it

- **Stacking and nesting:** the most boxes or envelopes that fit inside each other (sort by one side, LIS on the
  other).
- **Scheduling with two orders,** such as building the most bridges between two river banks that do not cross.
- **Measuring how sorted a list is:** $n - \text{LIS}$ is the fewest items to move to make it sorted.
- **Patience sorting** and the analysis of card games; also the **longest common subsequence** of two
  permutations, which becomes an LIS.

## Common mistakes

- **Strictly increasing vs non-decreasing:** for strictly increasing use "first tail $\ge x$" (`bisect_left`,
  `lower_bound`); for non-decreasing use "first tail $> x$" (`bisect_right`, `upper_bound`).
- **Printing `tails` as the answer:** it has the right length but is often **not** a real subsequence. In the
  example it ends as `[2, 3, 7, 18]` by luck; for `[3, 4, 1]` it ends as `[1, 4]`, which is not in order in the list.
- **Forgetting the empty list:** the answer is 0.

## Going deeper

Each part below starts closed; open the ones you want.

??? example "Sample walkthrough: [10, 9, 2, 5, 3, 7, 101, 18]"

    | Read | Where it goes | tails after |
    |---|---|---|
    | 10 | append | [10] |
    | 9 | replaces 10 | [9] |
    | 2 | replaces 9 | [2] |
    | 5 | append | [2, 5] |
    | 3 | replaces 5 | [2, 3] |
    | 7 | append | [2, 3, 7] |
    | 101 | append | [2, 3, 7, 101] |
    | 18 | replaces 101 | [2, 3, 7, 18] |

    Length 4. The links: 18 was placed after the tail 7, 7 after 3, 3 after 2, so following them back gives
    2, 3, 7, 18.

    The simple DP gives `best = [1, 1, 1, 2, 2, 3, 4, 4]`; its largest value is also 4.

??? abstract "The math: why tails stays sorted, and a famous bound"

    **`tails` is sorted.** Suppose $\text{tails}[k] \ge \text{tails}[k+1]$. The increasing run of length $k + 2$
    ending at $\text{tails}[k+1]$ has, one step before its end, a number smaller than $\text{tails}[k+1]$ that ends
    a run of length $k + 1$. That contradicts $\text{tails}[k]$ being the smallest such ending.

    **The update is right.** For a new $x$, the runs it can extend are those ending below $x$; the longest of them
    has length $k$ where $\text{tails}[k-1] < x \le \text{tails}[k]$. So $x$ ends a run of length $k + 1$, and
    since $x \le \text{tails}[k]$ it becomes the new smallest ending for that length. No other entry changes.

    **Time.** $n$ binary searches on a list of at most $n$: $O(n \log n)$, which is optimal for comparison-based
    methods (Fredman, 1975).

    **Erdős–Szekeres theorem (1935).** Every list of $rs + 1$ different numbers has an increasing subsequence of
    length $r + 1$ or a decreasing one of length $s + 1$. *Proof:* label each number with the pair
    (longest increasing run ending there, longest decreasing run ending there). Two different positions always get
    different pairs, because whichever of the two numbers is bigger extends one of the other's runs. If no
    increasing run reached $r + 1$ and no decreasing run reached $s + 1$, there would be only $rs$ possible pairs
    for $rs + 1$ numbers.

    **Random lists.** For a random order of $n$ numbers, the LIS is about $2\sqrt{n}$ (Vershik–Kerov and
    Logan–Shepp, 1977; the fluctuations follow the Tracy–Widom law, Baik–Deift–Johansson, 1999).

??? tip "Watch it step by step"

    Blue marks the numbers currently in `tails`; red is the number just read. The line under the picture shows `tails`.

    <div class="cs-anim" data-anim="lis"></div>

??? info "Variations and related ideas"

    - **Counting the number of longest increasing subsequences:** keep a count next to each `best[i]`, $O(n^2)$, or
      $O(n \log n)$ with a [Fenwick tree](../data-structures/fenwick-tree.md).
    - **Weighted LIS** (maximize the sum, not the length): a Fenwick tree or segment tree over the values.
    - **Longest decreasing subsequence:** run LIS on the negated list.
    - **Mirsky's theorem** (the dual of Dilworth's): the fewest decreasing subsequences that cover the list equals the length of the
      LIS; patience sorting builds both.

## See also

- [Binary search](../searching/binary-search.md)
- [Longest common subsequence](lcs.md)
- [Fenwick tree](../data-structures/fenwick-tree.md)

## References

- M. L. Fredman, "On computing the length of longest increasing subsequences", *Discrete Mathematics* 11(1), 1975.
- P. Erdős and G. Szekeres, "A combinatorial problem in geometry", *Compositio Mathematica* 2, 1935.
- D. Aldous and P. Diaconis, "Longest increasing subsequences: from patience sorting to the
  Baik–Deift–Johansson theorem", *Bulletin of the AMS* 36(4), 1999.
