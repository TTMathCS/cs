# Insertion sort

*Keep the left part sorted. Take the next value and slide it left into its place, like sorting playing cards in
your hand.*

| Time (worst / average) | Time (best) | Extra space | Stable | In place | Online |
|---|---|---|---|---|---|
| $O(n^2)$ | $O(n)$ on sorted input | $O(1)$ | yes | yes | yes |

## The idea

Pick up cards one at a time. Your hand is always sorted. Each new card is slid in from the right, moving past
every card bigger than it, until it meets one that is not bigger.

On a list: the first value alone is sorted. Take the second, shift it left past bigger values, and drop it into
the gap. Now the first two are sorted. Keep going. The work for each value equals how far it has to travel, so a
list that is **nearly sorted** is sorted almost in a single pass.

That is why insertion sort is used inside the fastest real sorts: Timsort (Python, Java) and introsort (C++)
hand small pieces, of up to about 16 to 64 values, to insertion sort.

## How it works

1. For `i` from 1 to $n-1$:
    1. Save `key = a[i]`.
    2. Walk `j` left from `i - 1` while `a[j] > key`, copying `a[j]` one place right.
    3. Put `key` at `a[j+1]`. Now `a[0..i]` is sorted.

## Code

=== "Python"

    ```python
    --8<-- "sorting/insertion_sort.py"
    ```

=== "Java"

    ```java
    --8<-- "sorting/InsertionSort.java"
    ```

=== "C++"

    ```cpp
    --8<-- "sorting/insertion_sort.cpp"
    ```

Each program prints `[5, 6, 11, 12, 13]`, `[3, 9, 10, 27, 38, 43, 82]` and `[]`.

## When to use it

- **Small lists** (up to a few dozen values): less overhead than any $O(n \log n)$ sort.
- **Nearly sorted data:** each value moves only a few places, so it runs in close to $O(n)$.
- **Data arriving one value at a time** (it is *online*): you can keep a list sorted as values come in.
- **As the finishing step** of merge sort or quicksort, once the pieces are small.

## Common mistakes

- Using `a[j] >= key`: equal values then jump over each other and the sort stops being stable.
- Swapping at every step instead of shifting and writing the key once: correct, but about three times the writes.
- Starting `i` at 0, or letting `j` go below 0 (check `j >= 0` *before* reading `a[j]`).

## Going deeper

Each part below starts closed; open the ones you want.

??? example "Sample walkthrough: [12, 11, 13, 5, 6]"

    The sorted part is in bold.

    | `i` | key | Shifts | List after |
    |---|---|---|---|
    | 1 | 11 | 12 → right | **11 12** 13 5 6 |
    | 2 | 13 | none (12 < 13) | **11 12 13** 5 6 |
    | 3 | 5 | 13, 12, 11 → right | **5 11 12 13** 6 |
    | 4 | 6 | 13, 12, 11 → right | **5 6 11 12 13** |

    7 shifts in all, which is exactly the number of inversions in `[12, 11, 13, 5, 6]`.

??? abstract "The math: why it is correct and how long it takes"

    **Invariant.** Before step $i$, $a[0..i-1]$ holds the original first $i$ values in sorted order. Step $i$
    shifts every value greater than the key one place right and writes the key into the gap, which leaves
    $a[0..i]$ sorted. Because only values strictly greater than the key move past it, equal values keep their
    order: the sort is stable.

    **Running time equals inversions.** Each shift fixes exactly one inversion (a pair $i<j$ with $a_i>a_j$), so
    with $I$ inversions the running time is $\Theta(n + I)$. Since

    $$
    0 \le I \le \binom{n}{2} = \frac{n(n-1)}{2}, \qquad \mathbb{E}[I] = \frac{n(n-1)}{4} \text{ for a random order},
    $$

    the best case is $\Theta(n)$, and the worst (reversed input) and average cases are $\Theta(n^2)$.

    **Comparisons.** Each step makes one more comparison than it makes shifts (the one that stops it), except
    when the key goes all the way to the front: between $n-1$ and $\frac{n(n-1)}{2}$ comparisons.

    **Binary insertion** finds the place with [binary search](../searching/binary-search.md) in
    $\lceil \log_2(i+1) \rceil$ comparisons, $\sum_i \log_2 i \approx n \log_2 n$ in total, but the shifting is still
    $\Theta(n^2)$ moves.

??? tip "Watch it step by step"

    Blue is the value being inserted, red a value shifting right, green the sorted part.

    <div class="cs-anim" data-anim="insertion-sort"></div>

??? info "Variations and related ideas"

    - **Shellsort** (D. Shell, 1959) runs insertion sort on values a *gap* apart, with shrinking gaps such as
      $701, 301, 132, 57, 23, 10, 4, 1$. Far-apart inversions are fixed cheaply early, and the final gap-1 pass
      meets an almost sorted list. No tight bound is known for the best gap sequences; good ones run in about
      $O(n^{4/3})$ or better in practice.
    - **Timsort** finds runs that are already sorted, extends short ones with binary insertion sort, and merges
      them. It is the standard sort of Python and of Java for objects.
    - **Library sort** leaves gaps in the array so that inserting needs few shifts: $O(n \log n)$ with high
      probability.

## See also

- [Bubble sort](bubble-sort.md) and [selection sort](selection-sort.md): the other simple sorts
- [Merge sort](merge-sort.md): the $O(n \log n)$ partner in Timsort
- [Binary search](../searching/binary-search.md)

## References

- D. E. Knuth, *The Art of Computer Programming, Vol. 3*, 2nd ed., §5.2.1 (sorting by insertion, Shellsort).
- T. H. Cormen et al., *Introduction to Algorithms*, 4th ed., §2.1–2.2.
- T. Peters, ["listsort.txt"](https://github.com/python/cpython/blob/main/Objects/listsort.txt), the description of Timsort in CPython.
