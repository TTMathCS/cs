# Two pointers

*Keep two positions in the array and move them, never backwards, according to a simple rule. Each step rules out
a whole row of possibilities, so a problem that looks like $O(n^2)$ pairs takes $O(n)$.*

| Time | Extra space | Usually needs |
|---|---|---|
| $O(n)$ (after sorting, $O(n \log n)$) | $O(1)$ | sorted data, or a "read" and a "write" position |

## The idea

In a **sorted** list, find two values that add up to 15. Checking every pair takes $n(n-1)/2$ checks. Instead,
put one finger on the smallest value and one on the largest, and add them:

- **Too small?** The left value plus even the *largest* value is not enough, so the left value cannot be part of
  any answer. Move the left finger right.
- **Too big?** The right value plus even the *smallest* value is too much. Move the right finger left.
- **Equal?** Done.

Each step throws away one value for good, so after at most $n-1$ steps the fingers meet.

The same "two positions moving one way" pattern appears in two more shapes:

- **Read and write pointers**, both moving left to right: filter or de-duplicate an array in place.
- **Fast and slow pointers**: in a linked list, one moving twice as fast finds the middle, or detects a cycle.

## How it works (pair with a given sum)

1. `i = 0`, `j = n - 1`.
2. While `i < j`: let `s = a[i] + a[j]`.
    - `s == target`: return `(i, j)`.
    - `s < target`: `i += 1`.
    - `s > target`: `j -= 1`.
3. No pair.

## Code

Three classic uses: a pair with a given sum, removing duplicates in place, and the "container with most water"
(two walls at positions $i < j$ hold $(j-i)\cdot\min(h_i, h_j)$).

=== "Python"

    ```python
    --8<-- "searching/two_pointers.py"
    ```

=== "Java"

    ```java
    --8<-- "searching/TwoPointers.java"
    ```

=== "C++"

    ```cpp
    --8<-- "searching/two_pointers.cpp"
    ```

Output: `(2, 4)` (4 + 11), `None` (no pair adds to 10), `4 [1, 2, 3, 4]` and `49`.

## When to use it

- Pairs or triples in a sorted array with a given sum (**3-sum** fixes one value and runs two pointers on the
  rest: $O(n^2)$ instead of $O(n^3)$).
- **Merging** two sorted lists (the merge step of [merge sort](../sorting/merge-sort.md)).
- **Partitioning** in place: [quicksort](../sorting/quicksort.md), moving zeros to the end, the Dutch national
  flag.
- **Palindromes**: compare from both ends towards the middle.
- Linked lists: middle node, cycle detection (Floyd's tortoise and hare), the $k$-th node from the end.

## Common mistakes

- **Unsorted input** for the pair-sum version: the rule "too small, move left pointer" is only safe when sorted.
- **Moving the wrong pointer** in the water problem: moving the *taller* wall can never help, because the
  shorter one still limits the height and the width shrinks.
- **Loop condition** `i <= j` when a value must not pair with itself.
- Forgetting to skip equal values in 3-sum, which reports the same triple many times.

## Going deeper

Each part below starts closed; open the ones you want.

??? example "Sample walkthrough: sum 15 in [1, 2, 4, 7, 11, 15]"

    | `i` | `j` | `a[i] + a[j]` | Move |
    |---|---|---|---|
    | 0 | 5 | 1 + 15 = 16 | too big: `j = 4` |
    | 0 | 4 | 1 + 11 = 12 | too small: `i = 1` |
    | 1 | 4 | 2 + 11 = 13 | too small: `i = 2` |
    | 2 | 4 | 4 + 11 = 15 | found `(2, 4)` |

??? abstract "The math: why no pair is ever missed"

    Picture all pairs $(i, j)$ with $i < j$ as the upper triangle of an $n \times n$ grid. The algorithm walks a
    path from the corner $(0, n-1)$.

    **Claim.** When the algorithm moves $i$ up because $a_i + a_j < t$, no pair $(i, j')$ with $j' \le j$ can be
    an answer, since $a_i + a_{j'} \le a_i + a_j < t$. Pairs $(i, j')$ with $j' > j$ were already ruled out
    earlier (when $j$ moved past them, they were too big). So the whole row $i$ is eliminated. Symmetrically,
    moving $j$ eliminates the whole column $j$.

    Each step eliminates one row or one column and there are $n$ of each, so the algorithm makes at most $n - 1$
    steps and every pair is either checked or provably not an answer: time $\Theta(n)$, space $O(1)$.

    **Container with most water.** If $h_i < h_j$, every container $(i, j')$ with $j' < j$ has width less than
    $j - i$ and height at most $h_i$, so its area is less than $(j-i)\,h_i$, which we already measured. So
    moving $i$ loses nothing.

    **Floyd's cycle detection.** If a list has a tail of length $\mu$ and a cycle of length $\lambda$, the fast
    pointer (2 steps) and the slow one (1 step) meet within $\mu + \lambda$ steps, since inside the cycle the gap
    between them shrinks by 1 each step.

??? tip "Watch it step by step"

    <div class="cs-anim" data-anim="two-pointers"></div>

??? info "Variations and related ideas"

    - **$k$-sum:** sort, fix $k-2$ values by loops, two pointers on the rest: $O(n^{k-1})$.
    - **Pair counting:** count pairs with $a_i + a_j \le t$ by adding $j - i$ whenever the sum fits.
    - **Merging intervals, intersecting sorted lists:** one pointer per list.
    - **Sliding window** is two pointers moving in the same direction with a condition on the stretch between
      them: see [Sliding window](sliding-window.md).

## See also

- [Sliding window](sliding-window.md)
- [Binary search](binary-search.md): the other way to use sorted order
- [Merge sort](../sorting/merge-sort.md): merging is a two-pointer walk

## References

- S. Halim, F. Halim, *Competitive Programming 3*, 2013, Chapter 3 and Chapter 9 (two pointers).
- D. E. Knuth, *The Art of Computer Programming, Vol. 2*, 3rd ed., §3.1, exercise 6 (Floyd's cycle-finding).
