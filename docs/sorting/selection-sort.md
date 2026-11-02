# Selection sort

*Find the smallest value and put it first. Find the smallest of the rest and put it second. Repeat.*

| Time (every case) | Extra space | Swaps | Stable | In place |
|---|---|---|---|---|
| $O(n^2)$ | $O(1)$ | at most $n-1$ | no | yes |

## The idea

Think of sorting a hand of cards face up on a table: scan them all, pick out the lowest card and lay it on the
left. Scan what is left, pick out the lowest again, lay it next. The left part grows by one card at a time and is
always sorted and final.

Selection sort always makes the same number of comparisons, about $n^2/2$, whatever the input looks like. Its one
strength is that it makes very few **writes**: at most one swap per position, $n-1$ in total.

## How it works

1. For `i` from 0 to $n-2$:
    1. Find the position `smallest` of the minimum of `a[i..n-1]`.
    2. Swap `a[i]` and `a[smallest]`. Now `a[0..i]` is sorted and final.

## Code

=== "Python"

    ```python
    --8<-- "sorting/selection_sort.py"
    ```

=== "Java"

    ```java
    --8<-- "sorting/SelectionSort.java"
    ```

=== "C++"

    ```cpp
    --8<-- "sorting/selection_sort.cpp"
    ```

Each program prints `[11, 12, 22, 25, 64]`, `[3, 9, 10, 27, 38, 43, 82]` and `[1, 2]`.

## When to use it

- **When writing is expensive.** On flash memory or EEPROM, where each write wears the chip, $n-1$ swaps beat
  insertion sort's up to $n^2/2$ moves.
- **Tiny lists**, and as a way to learn the "grow a sorted part" idea that [heapsort](heapsort.md) speeds up.
- **Not** for anything large, and not when you need stability.

## Common mistakes

- Swapping every time a smaller value is found, instead of once after the scan: still correct but does many more
  writes, losing the one advantage.
- Expecting it to be stable. The long-distance swap can jump a value over an equal one: sorting
  `[(2,a), (2,b), (1,c)]` by number swaps `(2,a)` to the end, giving `(1,c), (2,b), (2,a)`.

## Going deeper

Each part below starts closed; open the ones you want.

??? example "Sample walkthrough: [64, 25, 12, 22, 11]"

    | Step `i` | Unsorted part | Smallest | Swap | List after |
    |---|---|---|---|---|
    | 0 | `64 25 12 22 11` | 11 at 4 | 64 ↔ 11 | `[11, 25, 12, 22, 64]` |
    | 1 | `25 12 22 64` | 12 at 2 | 25 ↔ 12 | `[11, 12, 25, 22, 64]` |
    | 2 | `25 22 64` | 22 at 3 | 25 ↔ 22 | `[11, 12, 22, 25, 64]` |
    | 3 | `25 64` | 25 at 3 | none needed | `[11, 12, 22, 25, 64]` |

    $4 + 3 + 2 + 1 = 10$ comparisons and 3 real swaps.

??? abstract "The math: why it is correct and how long it takes"

    **Invariant.** Before step $i$, $a[0..i-1]$ holds the $i$ smallest values in sorted order, and every value in
    $a[i..n-1]$ is at least $a[i-1]$. Step $i$ moves the minimum of the rest to position $i$, which keeps both
    statements true for $i+1$. At the end ($i = n-1$) the whole array is sorted.

    **Comparisons** are the same for every input:

    $$
    C(n) = \sum_{i=0}^{n-2} (n-1-i) = \frac{n(n-1)}{2} = \Theta(n^2).
    $$

    **Swaps:** at most $n-1$, one per step: $O(n)$ writes.

    **How often does the "smallest so far" change?** On a random order, while scanning $m$ values the minimum
    changes each time we meet a new record low. The $k$-th value is a record with probability $1/k$, so the
    expected number of changes is the harmonic number $H_m = 1 + \tfrac12 + \cdots + \tfrac1m \approx \ln m$.
    Summed over all steps this is $O(n \log n)$, small next to the $n^2/2$ comparisons.

??? tip "Watch it step by step"

    Blue marks the smallest value found so far, orange the value being compared, green the finished part.

    <div class="cs-anim" data-anim="selection-sort"></div>

??? info "Variations and related ideas"

    - **Heapsort** is selection sort with a faster way to find the maximum: a [heap](../data-structures/binary-heap.md)
      gives it in $O(\log n)$ instead of $O(n)$, so the total drops to $O(n \log n)$.
    - **Double selection sort** finds the minimum and the maximum in the same scan and places both, halving the
      number of passes (not the comparisons).
    - **Stable selection sort:** instead of swapping, shift the block $a[i..s-1]$ one place right and drop the
      minimum in at $i$. Stable, but now up to $n^2/2$ moves.
    - **Partial sort:** stop after $k$ steps to get the $k$ smallest values in order, in $O(kn)$.

## See also

- [Heapsort](heapsort.md): selection sort made fast with a heap
- [Insertion sort](insertion-sort.md): the other simple sort, adaptive and stable
- [Bubble sort](bubble-sort.md)

## References

- D. E. Knuth, *The Art of Computer Programming, Vol. 3*, 2nd ed., §5.2.3 (sorting by selection).
- R. Sedgewick, K. Wayne, *Algorithms*, 4th ed., §2.1.
