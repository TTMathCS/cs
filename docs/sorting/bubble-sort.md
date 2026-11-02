# Bubble sort

*Walk along the list, swap any two neighbours that are in the wrong order, and repeat. The big values "bubble"
to the end one pass at a time.*

| Time (worst / average) | Time (best) | Extra space | Stable | In place |
|---|---|---|---|---|
| $O(n^2)$ | $O(n)$ with the early stop | $O(1)$ | yes | yes |

## The idea

Look at the first two values. If the left one is bigger, swap them. Move one step right and do the same with the
next pair, all the way to the end. After this first **pass** the largest value has been carried to the last
position, like a bubble rising to the top of a glass, and it never moves again.

Do another pass over everything except the last value, and the second largest settles in the second-to-last
position. After $n-1$ passes every value is home.

One small improvement makes a big difference on lists that are already nearly sorted: if a whole pass makes no
swap at all, every neighbour pair is in order, so the list is sorted and we can stop.

## How it works

1. For `end` from the last position down to 1:
    1. Walk `i` from 0 to `end - 1` and swap `a[i]` and `a[i+1]` whenever `a[i] > a[i+1]`.
    2. Now `a[end]` holds the largest value of `a[0..end]`: it is final.
    3. If no swap happened in this pass, stop.

## Code

=== "Python"

    ```python
    --8<-- "sorting/bubble_sort.py"
    ```

=== "Java"

    ```java
    --8<-- "sorting/BubbleSort.java"
    ```

=== "C++"

    ```cpp
    --8<-- "sorting/bubble_sort.cpp"
    ```

Each program prints `[1, 2, 4, 5, 8]`, `[3, 9, 10, 27, 38, 43, 82]` and `[1, 2, 3]`.

## When to use it

- **Teaching and tiny lists.** It is the easiest sort to understand and to get right.
- **Checking a list is sorted, cheaply.** One pass with no swaps proves it, in $O(n)$.
- **Almost never in real programs.** [Insertion sort](insertion-sort.md) is just as simple and usually about twice
  as fast; for anything big, use your language's built-in sort ([merge sort](merge-sort.md) and
  [quicksort](quicksort.md) ideas inside).

## Common mistakes

- Running the inner loop to `n - 1` every time instead of `end`: still correct, but it re-checks values that are
  already final.
- Forgetting the `swapped` flag, which loses the fast $O(n)$ case on sorted input.
- Comparing with `>=` instead of `>`: equal values then swap, and the sort is no longer **stable**.

## Going deeper

Each part below starts closed; open the ones you want.

??? example "Sample walkthrough: [5, 1, 4, 2, 8]"

    The comparisons in each pass; a swap is marked **swap**.

    | Pass | Comparisons | List after the pass | Final from here on |
    |---|---|---|---|
    | 1 | 5 > 1 **swap**, 5 > 4 **swap**, 5 > 2 **swap**, 5 < 8 | `[1, 4, 2, 5, 8]` | 8 |
    | 2 | 1 < 4, 4 > 2 **swap**, 4 < 5 | `[1, 2, 4, 5, 8]` | 5, 8 |
    | 3 | 1 < 2, 2 < 4 | `[1, 2, 4, 5, 8]` | no swap: stop |

    Three passes and 9 comparisons instead of the full $4 + 3 + 2 + 1 = 10$, because pass 3 made no swap.

??? abstract "The math: why it is correct and how long it takes"

    **Invariant.** After pass $p$ (counting from 1), the last $p$ positions hold the $p$ largest values in sorted
    order. Proof: during a pass, the running maximum of $a[0..i]$ is always at position $i$, because every
    comparison moves the larger of the pair to the right. So at the end of the pass the maximum of the unsorted
    part sits at position `end`.

    **Comparisons.** Without the early stop, pass $p$ makes $n - p$ comparisons:

    $$
    \sum_{p=1}^{n-1} (n-p) = \frac{n(n-1)}{2} = \Theta(n^2).
    $$

    **Swaps count inversions.** An *inversion* is a pair $i < j$ with $a_i > a_j$. Each swap of neighbours fixes
    exactly one inversion and creates none, so the number of swaps equals the number of inversions $I$, which is
    between $0$ (sorted) and $\binom{n}{2}$ (reversed). For a random order each of the $\binom{n}{2}$ pairs is
    inverted with probability $\tfrac12$, so on average

    $$
    \mathbb{E}[I] = \frac{1}{2}\binom{n}{2} = \frac{n(n-1)}{4}.
    $$

    **Best case.** On sorted input the first pass makes $n-1$ comparisons, no swaps, and stops: $\Theta(n)$.

    **Space.** Only `i`, `end` and `swapped`: $O(1)$ extra memory.

??? tip "Watch it step by step"

    Orange bars are being compared, red bars were just swapped, green bars are in their final place.

    <div class="cs-anim" data-anim="bubble-sort"></div>

??? info "Variations and related ideas"

    - **Cocktail shaker sort** passes left-to-right then right-to-left, so small values near the end ("turtles")
      also move quickly.
    - **Comb sort** compares values a *gap* apart and shrinks the gap by about 1.3 each pass; it fixes far-apart
      inversions early and runs much faster in practice.
    - **Odd–even transposition sort** compares all odd pairs at once, then all even pairs: a parallel bubble sort
      that needs $n$ rounds on $n$ processors.
    - Any sort that only swaps *neighbours* needs at least $I$ swaps, so it is $\Theta(n^2)$ on average. Faster
      sorts must move values over long distances.

## See also

- [Insertion sort](insertion-sort.md): also $O(n^2)$, but faster and just as simple
- [Selection sort](selection-sort.md): the fewest swaps of the simple sorts
- [Big-O and running time](../foundations/big-o.md): what $O(n^2)$ means

## References

- D. E. Knuth, *The Art of Computer Programming, Vol. 3: Sorting and Searching*, 2nd ed., §5.2.2 (exchange sorts).
- T. H. Cormen, C. E. Leiserson, R. L. Rivest, C. Stein, *Introduction to Algorithms*, 4th ed., Problem 2-2.
- O. Astrachan, ["Bubble Sort: An Archaeological Algorithmic Analysis"](https://users.cs.duke.edu/~ola/papers/bubble.pdf), SIGCSE 2003.
