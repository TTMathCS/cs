# Subsets and permutations

*Generate every subset and every ordering of a list by deciding one item at a time and undoing each decision
afterwards. The same pattern, with a check that cuts off hopeless branches, finds the subsets with a given sum.*

| Subsets | Permutations | Subset sum (with pruning) | Extra space |
|---|---|---|---|
| $O(n \cdot 2^n)$ | $O(n \cdot n!)$ | at most $O(2^n)$, often far less | $O(n)$ besides the output |

## The idea

**Subsets.** Each item is either **out** or **in**: two choices per item, $2^n$ subsets. Picture a tree: the root
has decided nothing; each level decides one item; each of the $2^n$ leaves is one subset. A recursive function
walks this tree: decide item $i$ (first "out", then "in"), recurse to item $i + 1$, and when all items are
decided, record the subset.

**Permutations.** Fill position 1 with any of the $n$ items, position 2 with any of the $n - 1$ left, and so on:
$n!$ orderings. A `used` list says which items are still free.

**Subset sum.** Look for the subsets that add up to a target. With positive numbers, once the running total is
above the target, nothing deeper can work, so return at once: **pruning**.

## How it works

- **Subsets:** `go(i)`: if `i == n`, record `chosen`. Otherwise `go(i + 1)`; append `items[i]`; `go(i + 1)`; pop.
- **Permutations:** `go()`: if `chosen` is full, record it. Otherwise for each unused item: mark it, append, `go()`,
  pop, unmark.
- **Subset sum:** like subsets, carrying the running total, and returning when it equals the target (record) or
  passes it (prune).

## Code

=== "Python"

    ```python
    --8<-- "backtracking/subsets_permutations.py"
    ```

=== "Java"

    ```java
    --8<-- "backtracking/SubsetsPermutations.java"
    ```

=== "C++"

    ```cpp
    --8<-- "backtracking/subsets_permutations.cpp"
    ```

Output: the 8 subsets of `[1, 2, 3]`, starting with the empty one; the 6 permutations in dictionary order; and
`[[3, 4, 2], [4, 5]]`, the two subsets of `[3, 34, 4, 12, 5, 2]` that add up to 9.

## When to use it

- **Trying every combination** when $n$ is small (up to about 20–25 for subsets, 10–11 for permutations).
- **Brute-force checks** of a cleverer algorithm on small inputs: generate all cases and compare.
- **Puzzles and planning:** choosing a team, ordering stops on a route (the travelling salesman for a few
  cities), assigning tasks.
- **With pruning,** much larger inputs can still be searched when the rules cut most branches.

## Common mistakes

- **Recording the shared list itself** instead of a copy: every recorded answer then changes as the search
  continues, and they all end up empty.
- **Forgetting to undo** (`pop`, `used[i] = False`): later branches see a wrong state.
- **Pruning on a sum with negative numbers:** the total can come back down, so "too big" does not mean hopeless.
- **Duplicates in the input:** `[1, 1, 2]` would give repeated subsets and permutations; sort and skip an item equal
  to the previous one at the same level.

## Going deeper

Each part below starts closed; open the ones you want.

??? example "Sample walkthrough: subsets of [1, 2, 3] and the sum 9"

    The order the subsets come out (0 = out, 1 = in, for items 1, 2, 3):

    | Decisions | Subset |
    |---|---|
    | 0 0 0 | {} |
    | 0 0 1 | {3} |
    | 0 1 0 | {2} |
    | 0 1 1 | {2, 3} |
    | 1 0 0 | {1} |
    | 1 0 1 | {1, 3} |
    | 1 1 0 | {1, 2} |
    | 1 1 1 | {1, 2, 3} |

    The decisions count from 0 to 7 in binary: subsets of $n$ items and $n$-bit numbers are the same thing.

    **Subset sum 9 from [3, 34, 4, 12, 5, 2]:** take 3; take 34 → 37 > 9, prune; skip 34; take 4 → 7; take 12 → 19,
    prune; skip 12; take 5 → 12, prune; skip 5; take 2 → **9, found [3, 4, 2]**. Later, skipping 3: ... take 4,
    skip 12, take 5 → **9, found [4, 5]**.

??? abstract "The math: counting, and the cost of listing"

    **Counting.** Each item has 2 choices independently, so there are $2^n$ subsets; $\sum_k \binom{n}{k} = 2^n$
    groups them by size. Orderings: $n$ choices for the first position, $n - 1$ for the second, ..., so
    $n! = n(n-1)\cdots 1$.

    **Tree size.** The subset tree has $2^{n+1} - 1$ nodes. The permutation tree has
    $\sum_{k=0}^{n} \frac{n!}{(n-k)!} = n! \sum_{j=0}^{n} \frac{1}{j!} < e \cdot n!$ nodes.

    **Time.** Each answer costs $O(n)$ to copy, so listing all subsets is $\Theta(n \, 2^n)$ and all permutations
    $\Theta(n \cdot n!)$. No algorithm can list them faster than the size of its output.

    **How fast these grow.** $2^{30} \approx 10^9$; $10! = 3{,}628{,}800$; $13! \approx 6.2 \times 10^9$;
    $20! \approx 2.4 \times 10^{18}$. **Stirling's formula:** $n! \approx \sqrt{2\pi n}\,(n/e)^n$.

    **Subset sum is NP-complete**, so no polynomial algorithm is known; with small numbers, the
    [knapsack](../dp/knapsack.md)-style DP solves it in $O(n \cdot \text{target})$.

??? tip "Watch it step by step"

    The tree of decisions for {1, 2, 3}: a left branch leaves the item out, a right branch (+k) puts it in. Red is
    where the search is, green has been visited, purple are the subsets found.

    <div class="cs-anim" data-anim="subsets"></div>

??? info "Variations and related ideas"

    - **Bitmasks:** loop `mask` from 0 to $2^n - 1$; bit $i$ says whether item $i$ is in. Short and fast for
      $n \le 20$ or so.
    - **Next permutation:** step from one ordering to the next in dictionary order without recursion
      (`std::next_permutation` in C++).
    - **Combinations** (subsets of exactly $k$ items): stop going deeper once $k$ are chosen, or when too few items
      remain.
    - **Gray code:** list subsets so that consecutive ones differ by one item.
    - **Heap's algorithm:** each permutation from the previous by a single swap.
    - **Meet in the middle:** for subset sum with $n \approx 40$, list the $2^{20}$ sums of each half and match them.

## See also

- [N-Queens](n-queens.md)
- [Recursion](../foundations/recursion.md)
- [0/1 knapsack](../dp/knapsack.md)

## References

- D. E. Knuth, *The Art of Computer Programming*, Vol. 4A, *Combinatorial Algorithms, Part 1*, Section 7.2.1
  (generating all possibilities).
- S. S. Skiena, *The Algorithm Design Manual*, 3rd ed., Springer, 2020, Chapter 9 (combinatorial search).
