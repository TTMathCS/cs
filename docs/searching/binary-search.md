# Binary search

*Look at the middle of a sorted list. If it is too small, the answer is in the right half; if too big, in the
left half. Each look halves what is left.*

| Time | Extra space | Needs |
|---|---|---|
| $O(\log n)$: at most $\lfloor \log_2 n \rfloor + 1$ looks | $O(1)$ | the list to be sorted |

## The idea

To find a word in a paper dictionary you do not start at "A". You open it in the middle, see that you are at "M",
and know your word is in the first half. Open the middle of that half, and so on. A dictionary of a million words
needs only about 20 such steps, because $2^{20} \approx 10^6$.

Binary search keeps two markers, `lo` and `hi`, and a promise: *if the target is in the list at all, it is between
`lo` and `hi`*. Comparing the middle value with the target lets us move one marker past the middle, which keeps the
promise and halves the range. When the range is empty, the target is not there.

The most useful form in practice is **lower bound**: the first position whose value is $\ge$ the target. It
answers "where would this go?", "how many values are less than $x$?" and, used twice, "how many copies of $x$?"
(as the demo shows).

## How it works

1. `lo = 0`, `hi = n - 1`.
2. While `lo <= hi`:
    1. `mid = lo + (hi - lo) // 2`.
    2. If `a[mid] == target`, return `mid`.
    3. If `a[mid] < target`, set `lo = mid + 1`; otherwise set `hi = mid - 1`.
3. Return "not found".

## Code

=== "Python"

    ```python
    --8<-- "searching/binary_search.py"
    ```

=== "Java"

    ```java
    --8<-- "searching/BinarySearch.java"
    ```

=== "C++"

    ```cpp
    --8<-- "searching/binary_search.cpp"
    ```

Output: `5 0 9 -1` (23 is at 5, 2 at 0, 91 at 9, 7 is missing), then `1 4 0 6` for the lower bounds, then `3`
copies of 3.

The libraries have it built in: Python's `bisect.bisect_left` (lower bound) and `bisect_right`, Java's
`Arrays.binarySearch` and `Collections.binarySearch`, C++'s `std::lower_bound`, `std::upper_bound` and
`std::binary_search`.

## When to use it

- **Looking up values in sorted data** many times.
- **Insertion points:** where to insert to keep a list sorted; counting values in a range $[x, y)$ as
  `lower_bound(y) - lower_bound(x)`.
- **Any yes/no question whose answer flips once** as a number grows: see
  [binary search on the answer](binary-search-answer.md).
- **Debugging:** `git bisect` binary-searches the history for the commit that broke something.

## Common mistakes

Binary search is famous for being easy to get *almost* right. Jon Bentley found that about 90% of professional
programmers he tested could not write a correct one, and the version in Java's own library had an overflow bug for
nine years (below).

- **Overflow:** `(lo + hi) / 2` overflows when `lo + hi` passes $2^{31}-1$. Use `lo + (hi - lo) / 2`.
- **Infinite loops:** with `lo < hi` and `lo = mid`, the middle must be rounded **up**, or the loop can get stuck
  when `hi = lo + 1`.
- **Mixing conventions:** decide whether `hi` is included (`[lo, hi]`, loop while `lo <= hi`) or excluded
  (`[lo, hi)`, loop while `lo < hi`), and keep every update consistent with that choice.
- **Unsorted input:** the answer is then meaningless, with no error.

## Going deeper

Each part below starts closed; open the ones you want.

??? example "Sample walkthrough: find 23 in [2, 5, 8, 12, 16, 23, 38, 56, 72, 91]"

    | Look | `lo` | `hi` | `mid` | `a[mid]` | Decision |
    |---|---|---|---|---|---|
    | 1 | 0 | 9 | 4 | 16 | 16 < 23: `lo = 5` |
    | 2 | 5 | 9 | 7 | 56 | 56 > 23: `hi = 6` |
    | 3 | 5 | 6 | 5 | 23 | found at 5 |

    Three looks. Searching for 7 instead: mid 4 (16, go left), mid 1 (5, go right), mid 2 (8, go left), and then
    `lo = 2 > hi = 1`: not found after 3 looks.

??? abstract "The math: correctness and the number of steps"

    **Invariant.** If the target is in the array, its position is in $[lo, hi]$. It holds at the start
    ($[0, n-1]$). If $a[mid] < t$, then every $a[k]$ with $k \le mid$ is $\le a[mid] < t$ (the array is sorted),
    so $t$ can only be at $k \ge mid+1$; symmetrically for $a[mid] > t$. When $lo > hi$ the range is empty, so the
    target is absent.

    **Termination and steps.** Let $m = hi - lo + 1$ be the size of the range. After one step the new size is at
    most $\lfloor m/2 \rfloor$. Starting from $n$, after $k$ steps the size is at most $\lfloor n / 2^k \rfloor$,
    which reaches 0 once $2^k > n$. So the loop runs at most

    $$
    \lfloor \log_2 n \rfloor + 1 \text{ times}, \qquad \text{for example } \lfloor \log_2 10^9 \rfloor + 1 = 30.
    $$

    **Optimal.** A search that only compares the target with list values must tell apart $n+1$ outcomes (each
    position, or absent). Each comparison has at most three results ($<$, $=$, $>$), so $c$ comparisons tell apart
    at most $3^c$ outcomes, and $c \ge \log_3(n+1) = \Omega(\log n)$. Binary search meets this bound up to a constant.

    **Recurrence form:** $T(n) = T(n/2) + O(1)$, which the master theorem solves as $T(n) = \Theta(\log n)$.

??? tip "Watch it step by step"

    `lo`, `mid` and `hi` are marked under the boxes; greyed values have been ruled out.

    <div class="cs-anim" data-anim="binary-search"></div>

??? info "Variations and related ideas"

    - **Upper bound:** the first position with $a[i] > t$; change `a[mid] < target` to `a[mid] <= target`.
    - **Searching a rotated sorted array** (like `[15, 18, 2, 3, 6, 12]`): one half around `mid` is always sorted;
      check whether the target lies inside it.
    - **Exponential (galloping) search** for an unbounded or very long list: check positions 1, 2, 4, 8, ... until
      you pass the target, then binary search the last gap. $O(\log i)$ where $i$ is the target's position.
    - **Interpolation search** guesses the position from the values, like opening a dictionary near "T" for
      "tiger": $O(\log \log n)$ on evenly spread data, $O(n)$ in the worst case.
    - **Binary search on real numbers:** loop a fixed number of times (say 100) instead of comparing to an epsilon.
    - **Ternary search** finds the peak of a function that rises then falls.

## See also

- [Binary search on the answer](binary-search-answer.md): the same idea applied to a yes/no test
- [Binary search tree](../data-structures/bst.md): binary search as a data structure that allows inserts
- [Sorting](../sorting/index.md): binary search needs sorted data

## References

- J. Bentley, *Programming Pearls*, 2nd ed., Column 4, "Writing Correct Programs".
- J. Bloch, ["Extra, Extra – Read All About It: Nearly All Binary Searches and Mergesorts are Broken"](https://research.google/blog/extra-extra-read-all-about-it-nearly-all-binary-searches-and-mergesorts-are-broken/), Google Research blog, 2006.
- D. E. Knuth, *The Art of Computer Programming, Vol. 3*, 2nd ed., §6.2.1.
