# Binary search on the answer

*When you cannot compute the best value directly but can easily **test** a guess ("is capacity 15 enough?"), and
every value above a good guess is also good, binary-search the smallest good guess.*

| Time | Extra space | Needs |
|---|---|---|
| $O(\log R)$ tests, $R$ = size of the range of possible answers | $O(1)$ | a monotone test: no, no, ..., no, yes, yes, ..., yes |

## The idea

A ship must carry packages weighing 1, 2, ..., 10 tonnes, **in this order**, within 5 days, sailing once a day.
What is the smallest ship capacity that makes it?

Computing that capacity directly is awkward. But *checking* one is easy: load packages in order until the next
would overflow, then start a new day, and count the days. And the checks are **monotone**: if capacity 15 works,
16 works too. So the answers to "does capacity $c$ work?" look like

$$
\underbrace{\text{no, no, \ldots, no}}_{c \,<\, c^*},\ \underbrace{\text{yes, yes, \ldots, yes}}_{c \,\ge\, c^*}
$$

and finding the first "yes", $c^*$, is exactly a [binary search](binary-search.md), over numbers instead of over a
list. We never even build the list of candidates.

## How it works

1. Find a range `[lo, hi]` that surely contains the answer: here `lo` = the heaviest package (it must fit),
   `hi` = the total weight (everything in one day).
2. While `lo < hi`:
    1. `mid = (lo + hi) // 2`.
    2. If `test(mid)` passes, the answer is `mid` or smaller: `hi = mid`.
    3. Otherwise it is bigger: `lo = mid + 1`.
3. `lo` is the smallest value that passes.

## Code

The second example, the integer square root, searches for the **last** "yes" (the largest $r$ with $r^2 \le n$),
so it rounds `mid` up.

=== "Python"

    ```python
    --8<-- "searching/ship_capacity.py"
    ```

=== "Java"

    ```java
    --8<-- "searching/ShipCapacity.java"
    ```

=== "C++"

    ```cpp
    --8<-- "searching/ship_capacity.cpp"
    ```

Output: `15`, `6`, `3`, then `0 3 4 31622` for the square roots of 0, 15, 16 and 1,000,000,007.

## When to use it

Look for the words **"minimum maximum"** or **"maximum minimum"**, or "the smallest $x$ such that ...":

- the smallest capacity, speed or time that finishes a job by a deadline,
- splitting an array into $k$ parts so that the largest part sum is as small as possible,
- placing $k$ items as far apart as possible (the largest smallest gap),
- the $k$-th smallest value in a sorted matrix or among pairwise sums,
- roots of increasing functions, integer square and cube roots.

## Common mistakes

- **A test that is not monotone:** the method silently returns a wrong answer. Always ask "if $x$ works, does
  every larger $x$ work?"
- **A range that misses the answer:** `lo` must not exceed it and `hi` must surely work.
- **Rounding:** searching for the first "yes" uses `mid` rounded down with `hi = mid`; searching for the last
  "yes" needs `mid` rounded **up** with `lo = mid`, or the loop never ends.
- **Overflow** in `mid * mid` or in sums; use 64-bit integers.

## Going deeper

Each part below starts closed; open the ones you want.

??? example "Sample walkthrough: weights 1..10, 5 days"

    | `lo` | `hi` | `mid` | Days with capacity `mid` | Works? |
    |---|---|---|---|---|
    | 10 | 55 | 32 | 1+..+7 = 28 · 8+9+10 = 27: **2** | yes: `hi = 32` |
    | 10 | 32 | 21 | 1..6 = 21 · 7+8 = 15 · 9+10 = 19: **3** | yes: `hi = 21` |
    | 10 | 21 | 15 | 1..5 · 6+7 · 8 · 9 · 10: **5** | yes: `hi = 15` |
    | 10 | 15 | 12 | 1..4 · 5+6 · 7 · 8 · 9 · 10: **6** | no: `lo = 13` |
    | 13 | 15 | 14 | 1..4 · 5+6 · 7 · 8 · 9 · 10: **6** | no: `lo = 15` |

    `lo = hi = 15`. Six tests instead of trying all 46 capacities from 10 to 55.

??? abstract "The math: why it works and what it costs"

    **Monotone predicate.** Let $P(c)$ be "capacity $c$ ships everything in at most $d$ days". If $c \le c'$, the
    greedy loading with $c'$ never starts a new day earlier than with $c$ (by induction on the packages, the
    $c'$-ship is always at least as far along), so $\text{days}(c') \le \text{days}(c)$, and $P(c) \Rightarrow P(c')$.

    **Greedy loading is optimal for a fixed capacity.** Packing each day as full as possible never hurts: any
    valid plan can be changed, day by day, into the greedy one without using more days. So
    $\text{days}(c)$ is the true minimum number of days for capacity $c$.

    **Invariant of the search.** $P(hi)$ is true, and $P(c)$ is false for every $c < lo$. Each step keeps it and
    shrinks $hi - lo$ by about half, so after $\lceil \log_2 (hi - lo + 1) \rceil$ steps $lo = hi = c^*$.

    **Cost.** Each test here is $O(n)$, so the total is

    $$
    O\!\left(n \log \textstyle\sum_i w_i\right).
    $$

    **Integer square root.** $P(r) = (r^2 \le n)$ is true then false; we want the last true value, so `mid` rounds
    up. Bounding `hi` by $\lfloor\sqrt{2^{63}-1}\rfloor = 3{,}037{,}000{,}499$ keeps `mid * mid` inside 64 bits.

??? tip "Watch it step by step"

    Each guess colours the packages by the day they sail; the info line shows each day's load.

    <div class="cs-anim" data-anim="ship-capacity"></div>

??? info "Variations and related ideas"

    - **Real-valued answers:** for "the smallest speed to arrive on time", run a fixed number of halvings.
    - **Parametric search** is the general theory: turn an optimization problem into a sequence of decision
      problems.
    - **The bisection method** for roots of continuous functions is the same idea, guaranteed by the intermediate
      value theorem.
    - **Parallel binary search** answers many such questions at once by sharing the tests.

## See also

- [Binary search](binary-search.md)
- [Greedy algorithms](../greedy/index.md): the greedy loading used as the test

## References

- S. Halim, F. Halim, *Competitive Programming 3*, 2013, Chapter 3 ("binary search the answer").
- N. Megiddo, "Applying parallel computation algorithms in the design of serial algorithms", *Journal of the ACM* 30(4), 1983 (parametric search).
