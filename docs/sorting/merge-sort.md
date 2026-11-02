# Merge sort

*Split the list in half, sort each half, then merge the two sorted halves into one. Divide and conquer at its
cleanest.*

| Time (every case) | Extra space | Stable | In place |
|---|---|---|---|
| $O(n \log n)$ | $O(n)$ | yes | no |

## The idea

Two sorted piles are easy to combine: look at the top card of each, take the smaller, repeat. That is a
**merge**, and it takes one step per card.

Merge sort turns sorting into merging. A list of one value is already sorted. Split any longer list into two
halves, sort each half the same way (this is [recursion](../foundations/recursion.md)), and merge the results.
The list is halved about $\log_2 n$ times, and each level of halving does $n$ steps of merging in total, so the
whole sort takes about $n \log_2 n$ steps, **always**, whatever the input.

Merge sort was described by John von Neumann in 1945, one of the first programs written for a stored-program
computer.

## How it works

1. If the list has 0 or 1 values, it is sorted: stop.
2. Split it at the middle, `mid = n // 2`.
3. Merge sort the left half and the right half.
4. Merge: keep a finger at the start of each half; repeatedly copy the smaller of the two values under the
   fingers (the left one if they are equal) and move that finger on. When one half runs out, copy the rest of
   the other.

## Code

The Python version returns a new list, which reads most clearly. The Java and C++ versions sort in place with one
scratch array allocated once, which is how it is done when speed matters.

=== "Python"

    ```python
    --8<-- "sorting/merge_sort.py"
    ```

=== "Java"

    ```java
    --8<-- "sorting/MergeSort.java"
    ```

=== "C++"

    ```cpp
    --8<-- "sorting/merge_sort.cpp"
    ```

Each program prints `[3, 9, 10, 27, 38, 43, 82]`, `[1, 2, 4, 5, 5, 8]` and `[1]`.

## When to use it

- **You need a guarantee:** $O(n \log n)$ in the worst case, no bad inputs.
- **You need stability**, for example sorting records by several fields one after another.
- **Linked lists:** merging needs no random access, and on a list it needs no extra array at all.
- **Data too big for memory (external sorting):** sort chunks that fit, write them to disk, then merge the sorted
  files in a few sequential passes. Databases do exactly this.
- **Parallel sorting:** the two halves are independent.

## Common mistakes

- `mid = (lo + hi) / 2` can overflow in Java and C++ when `lo + hi` exceeds $2^{31}-1$; use `lo + (hi - lo) / 2`
  for huge arrays.
- Using `<` instead of `<=` in the merge takes from the right half on ties, which breaks stability.
- Allocating a new scratch array inside every merge call: correct, but slow. Allocate once.
- Off-by-one errors in the split: decide whether ranges are half-open `[lo, hi)` (as here) and stick to it.

## Going deeper

Each part below starts closed; open the ones you want.

??? example "Sample walkthrough: [38, 27, 43, 3, 9, 82, 10]"

    Splitting goes down, merging comes back up.

    | Level | Pieces |
    |---|---|
    | split | `[38 27 43]` `[3 9 82 10]` |
    | split | `[38]` `[27 43]` · `[3 9]` `[82 10]` |
    | split | `[38]` `[27]` `[43]` · `[3]` `[9]` `[82]` `[10]` |
    | merge | `[38]` `[27 43]` · `[3 9]` `[10 82]` |
    | merge | `[27 38 43]` · `[3 9 10 82]` |
    | merge | `[3 9 10 27 38 43 82]` |

    The last merge, step by step: compare 27 and 3 → take **3**; 27 vs 9 → **9**; 27 vs 10 → **10**; 27 vs 82 →
    **27**; 38 vs 82 → **38**; 43 vs 82 → **43**; left is empty → copy **82**. Six comparisons for seven values.

??? abstract "The math: the recurrence and its solution"

    **Recurrence.** Sorting $n$ values means sorting two halves and merging in at most $n-1$ comparisons:

    $$
    T(n) = T\!\left(\lfloor n/2 \rfloor\right) + T\!\left(\lceil n/2 \rceil\right) + \Theta(n), \qquad T(1) = \Theta(1).
    $$

    **Recursion tree.** At depth $d$ there are $2^d$ pieces of size $n/2^d$, so each level costs $cn$ in total.
    There are $\log_2 n$ levels, so

    $$
    T(n) = \sum_{d=0}^{\log_2 n - 1} 2^d \cdot c\,\frac{n}{2^d} = c\,n\log_2 n = \Theta(n \log n).
    $$

    The **master theorem** gives the same: $a = 2$ subproblems, each of size $n/b$ with $b = 2$, and merge cost
    $f(n) = \Theta(n) = \Theta(n^{\log_b a})$, which is case 2, so $T(n) = \Theta(n^{\log_b a} \log n) = \Theta(n \log n)$.

    **Exact comparisons.** In the worst case merge sort makes
    $n\lceil \log_2 n\rceil - 2^{\lceil \log_2 n\rceil} + 1$ comparisons, which is at most $n\log_2 n - 0.91n$.
    The lower bound on the [sorting overview](index.md) is $\log_2 n! \approx n\log_2 n - 1.44n$, so merge sort is
    within about $0.53n$ comparisons of the best any comparison sort can do.

    **Correctness of merge.** Invariant: the output holds the smallest $k$ values of the two halves, in order,
    and the fingers point at the smallest values not yet taken. Taking the smaller of the two keeps it true.

    **Space.** The scratch array is $n$ values; the recursion stack is $\log_2 n$ frames deep: $O(n)$ in all.

??? tip "Watch it step by step"

    Blue marks the piece being split; green the piece just merged. Grey values are outside the current piece.

    <div class="cs-anim" data-anim="merge-sort"></div>

??? info "Variations and related ideas"

    - **Bottom-up merge sort** has no recursion: merge pieces of size 1 into 2, then 2 into 4, and so on.
    - **Natural merge sort** starts from the runs already sorted in the input, so sorted input costs $O(n)$.
      Timsort is a refined version of this.
    - **$k$-way merge** merges $k$ sorted lists at once with a [heap](../data-structures/binary-heap.md), in
      $O(n \log k)$; it is the heart of external sorting.
    - **Counting inversions** in $O(n \log n)$: during the merge, each time a value is taken from the right half,
      it was smaller than every value still waiting in the left half.
    - **In-place merging** is possible in $O(n \log n)$ total without the scratch array, but it is complicated and
      slower in practice.

## See also

- [Quicksort](quicksort.md): the other divide-and-conquer sort, splitting first and doing no merge
- [Recursion](../foundations/recursion.md) and the master theorem
- [Insertion sort](insertion-sort.md): the partner inside Timsort

## References

- T. H. Cormen et al., *Introduction to Algorithms*, 4th ed., §2.3 and §4.5 (the master theorem).
- D. E. Knuth, *The Art of Computer Programming, Vol. 3*, 2nd ed., §5.2.4 (sorting by merging) and §5.4 (external sorting).
- R. Sedgewick, K. Wayne, *Algorithms*, 4th ed., §2.2.
