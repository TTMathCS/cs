# Sliding window

*Look at a stretch of consecutive values, a "window". Move its right edge forward one step at a time, and move
its left edge forward only when the window breaks a rule. Every value enters and leaves once: $O(n)$.*

| Time | Extra space | Needs |
|---|---|---|
| $O(n)$ | $O(1)$, or $O(k)$ for counts of $k$ kinds | a rule that stays true when the window shrinks |

## The idea

**Fixed size.** The largest sum of 3 consecutive values: instead of re-adding 3 values for every position, slide
the window: add the value that enters on the right, subtract the one that leaves on the left. One addition and one
subtraction per step.

**Variable size.** The longest stretch of a word with no repeated letter. Grow the window to the right. When the
new letter is already inside the window, the window is broken; move the left edge just past the earlier copy of
that letter and it is valid again. The longest valid window seen along the way is the answer.

The key fact is that both edges only move **forward**. Each position is added once and removed once, so all the
shrinking together costs at most $n$ steps, even though one shrink can jump far.

## How it works (variable window)

1. `left = 0`, `best = 0`.
2. For `right` from 0 to $n-1$:
    1. Add `a[right]` to the window.
    2. While the window breaks the rule, remove `a[left]` and move `left` on.
    3. Record the window if it is the best so far.

## Code

Three classic problems: the best fixed-size window, the longest substring without repeats, and the shortest
stretch of positive numbers with a sum of at least a target.

=== "Python"

    ```python
    --8<-- "searching/sliding_window.py"
    ```

=== "Java"

    ```java
    --8<-- "searching/SlidingWindow.java"
    ```

=== "C++"

    ```cpp
    --8<-- "searching/sliding_window.cpp"
    ```

Output: `9` (5 + 1 + 3), then `3 1 3 0` ("abc", "b", "wke", the empty string), then `2 0` ([4, 3]; no stretch of
[1, 1, 1] reaches 5).

## When to use it

- "Longest / shortest **contiguous** stretch (subarray, substring) such that ..."
- Moving averages and sums over the last $k$ readings (sensors, stock prices, network traffic).
- At most $k$ distinct values, at most $k$ zeros flipped, an anagram of a pattern inside a text.
- The maximum of every window of size $k$, with a **monotonic deque**, in $O(n)$ total.

## Common mistakes

- **Using it when the rule does not survive shrinking.** With **negative** numbers, "sum $\ge$ target" can become
  true again after removing a value, so the shortest-sum version breaks; use prefix sums with a deque or a sorted
  structure instead.
- **Stale positions:** in the longest-unique version, a letter last seen *before* `left` is not in the window; the
  check `last[ch] >= left` matters.
- **Off-by-one** in the window length: it is `right - left + 1`.
- Recomputing the whole window at every step, which turns $O(n)$ back into $O(nk)$.

## Going deeper

Each part below starts closed; open the ones you want.

??? example "Sample walkthrough: longest unique stretch of \"abcabcbb\""

    | `right` | letter | Repeat inside? | `left` | Window | Best |
    |---|---|---|---|---|---|
    | 0 | a | no | 0 | a | 1 |
    | 1 | b | no | 0 | ab | 2 |
    | 2 | c | no | 0 | abc | 3 |
    | 3 | a | yes, at 0 | 1 | bca | 3 |
    | 4 | b | yes, at 1 | 2 | cab | 3 |
    | 5 | c | yes, at 2 | 3 | abc | 3 |
    | 6 | b | yes, at 4 | 5 | cb | 3 |
    | 7 | b | yes, at 6 | 7 | b | 3 |

??? abstract "The math: why it is linear and why it is right"

    **Amortized cost.** `right` takes $n$ values. `left` never decreases and never passes `right + 1`, so over the
    whole run it moves at most $n$ times. The total work is $O(n + n) = O(n)$, even though a single step of the
    outer loop may move `left` many places.

    **Correctness (shortest stretch with sum $\ge t$, positive values).** For each right end $r$, let $\ell(r)$ be
    the largest left end with $\sum_{k=\ell}^{r} a_k \ge t$. Because the values are positive, sums shrink as the
    left end moves right, so $\ell(r)$ is well defined and, crucially,

    $$
    \ell(r) \le \ell(r+1),
    $$

    since adding $a_{r+1}$ only makes sums bigger. So the left edge never needs to move back, and the algorithm
    finds $\ell(r)$ for every $r$, the shortest valid window ending at $r$. The best of these is the answer.

    **Fixed window sum** by prefix sums: with $P_0 = 0$, $P_i = a_0 + \cdots + a_{i-1}$, the window
    $a[i..i+k-1]$ has sum $P_{i+k} - P_i$, which is the same "add one, drop one" update.

??? tip "Watch it step by step"

    Blue is the window, orange the letter just added; `L` and `R` mark its edges.

    <div class="cs-anim" data-anim="sliding-window"></div>

??? info "Variations and related ideas"

    - **Sliding window maximum** with a deque that keeps candidates in decreasing order: each index is pushed and
      popped at most once, $O(n)$.
    - **Counting subarrays** with at most $k$ distinct values: every right end adds `right - left + 1` windows;
      "exactly $k$" is "at most $k$" minus "at most $k-1$".
    - **Rabin-Karp** slides a *hash* over the text: see [Rabin-Karp](../strings/rabin-karp.md).
    - **Two-dimensional windows** use 2-D prefix sums.

## See also

- [Two pointers](two-pointers.md)
- [Hash table](../data-structures/hash-table.md): the "last seen" map
- [Rabin-Karp](../strings/rabin-karp.md): a rolling hash over a sliding window

## References

- S. Halim, F. Halim, *Competitive Programming 3*, 2013, Chapter 9 (sliding window).
- T. H. Cormen et al., *Introduction to Algorithms*, 4th ed., Chapter 16 (amortized analysis).
