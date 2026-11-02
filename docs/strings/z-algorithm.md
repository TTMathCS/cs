# Z-algorithm

*For every position of a string, find how far the string starting there agrees with the start of the whole
string. A "box" of already-known agreement lets most values be copied instead of recomputed, so the whole array
takes linear time.*

| Time | Extra space | Output |
|---|---|---|
| $O(n)$ for a string of length $n$; $O(n + m)$ for matching | $O(n)$ | the Z-array; every match position |

## The idea

The **Z-array** of a string $s$ is

$$z[i] = \text{the length of the longest common prefix of } s \text{ and } s[i..].$$

For `aabxaab`: `z = [7, 1, 0, 0, 3, 1, 0]`. For example $z[4] = 3$ because `aab` at position 4 matches the first
three letters, and then the string ends.

**Pattern matching** comes free: build the Z-array of `pattern + separator + text`, with a separator letter that
appears in neither. Every position in the text part with $z \ge m$ is a match.

To compute it fast, keep the **box** $[l, r)$: the match with the prefix that reaches furthest to the right so
far. The letters $s[l..r)$ are a copy of $s[0..r-l)$. So for a position $i$ inside the box, the answer
$z[i - l]$ (already known, from the copy at the start) tells how far $s[i..]$ agrees, at least up to the box
edge $r$. Only beyond $r$ do letters need to be compared.

## How it works

1. $z[0] = n$; $l = r = 0$.
2. For $i = 1, 2, \dots$:
    - If $i < r$: start with $z[i] = \min(r - i,\; z[i - l])$.
    - Extend $z[i]$ by comparing $s[z[i]]$ with $s[i + z[i]]$ while they are equal.
    - If $i + z[i] > r$, move the box: $l = i$, $r = i + z[i]$.

## Code

=== "Python"

    ```python
    --8<-- "strings/z_algorithm.py"
    ```

=== "Java"

    ```java
    --8<-- "strings/ZAlgorithm.java"
    ```

=== "C++"

    ```cpp
    --8<-- "strings/z_algorithm.cpp"
    ```

Output: `[7, 1, 0, 0, 3, 1, 0]`, `[5, 4, 3, 2, 1]` for `aaaaa`, and `[4, 19]`: the two places `red` appears in
`the red planet has red dust`.

## When to use it

- **Pattern matching** with a short, easy-to-remember algorithm (one function, one loop).
- **Periods and repeats:** $s$ has period $p$ exactly when $z[p] = n - p$ (or $p = n$).
- **Counting distinct substrings, compressing strings, finding the longest prefix that is also a suffix** and many
  other contest-style string problems.
- **Wherever KMP's prefix function is used:** the two arrays can be converted into each other in $O(n)$.

## Common mistakes

- **A separator that occurs in the text or pattern:** matches would run across it. The code uses the zero
  character; with arbitrary bytes, compute the Z-array of the pattern and scan the text separately instead.
- **Forgetting the cap $r - i$:** the copy is only known to agree up to the box edge.
- **Not moving the box** when a longer match is found, which breaks the linear time.
- **The value of $z[0]$:** some books set it to 0, others to $n$; make sure the rest of the code agrees.

## Going deeper

Each part below starts closed; open the ones you want.

??? example "Sample walkthrough: aabxaabxaa"

    | $i$ | inside the box? | start value | compared letters | $z[i]$ | box after |
    |---|---|---|---|---|---|
    | 1 | no | 0 | `a`=`a`, then `b`≠`a` | 1 | [1, 2) |
    | 2 | no | 0 | `b`≠`a` | 0 | [1, 2) |
    | 3 | no | 0 | `x`≠`a` | 0 | [3, 3) (empty) |
    | 4 | no | 0 | `aabxaa` matches, then the string ends | 6 | [4, 10) |
    | 5 | yes, copy of 1 | min(5, z[1] = 1) = 1 | `b`≠`a` | 1 | [4, 10) |
    | 6 | yes, copy of 2 | min(4, 0) = 0 | `b`≠`a` | 0 | [4, 10) |
    | 7 | yes, copy of 3 | min(3, 0) = 0 | `x`≠`a` | 0 | [4, 10) |
    | 8 | yes, copy of 4 | min(2, z[4] = 6) = 2 | none: the string ends | 2 | [4, 10) |
    | 9 | yes, copy of 5 | min(1, 1) = 1 | none: the string ends | 1 | [4, 10) |

    Result: `[10, 1, 0, 0, 6, 1, 0, 0, 2, 1]`. At $i = 8$ the copy said 6, but only 2 letters remain inside the box,
    which is why the value is capped.

??? abstract "The math: correctness and the linear bound"

    **The copy is valid.** By the choice of the box, $s[l..r) = s[0..r-l)$. For $l < i < r$, the letters
    $s[i..r)$ equal $s[i-l..r-l)$. So $s[i..]$ and $s[0..]$ agree for exactly $\min(z[i-l],\, r - i)$ letters
    within the box:

    - if $z[i-l] < r - i$, the disagreement happens inside the box, so $z[i] = z[i-l]$ exactly and no comparison
      will succeed;
    - otherwise $z[i] \ge r - i$, and the comparisons continue from $r$.

    **Linear time.** Every successful comparison at position $i$ looks at the letter $s[i + z[i]]$ with
    $i + z[i] \ge r$, and afterwards the box edge $r$ moves past it. So $r$ grows by one per successful comparison,
    and $r \le n$: at most $n$ successful comparisons in total. Each $i$ makes at most one failed comparison. Total
    $O(n)$.

    **From Z to π.** For each $i$ with $z[i] > 0$, the positions $i, \dots, i + z[i] - 1$ end borders; setting
    $\pi[i + z[i] - 1] \ge z[i]$ and propagating gives the prefix function in $O(n)$.

??? tip "Watch it step by step"

    Blue is the box $[l, r)$, faded blue is the copy at the start, orange letters are being compared, and red is the
    $z$ value being found.

    <div class="cs-anim" data-anim="z-algorithm"></div>

??? info "Variations and related ideas"

    - **Manacher's algorithm** uses the same "box" idea to find all palindromes around every centre in $O(n)$.
    - **Suffix arrays and suffix trees** answer far more questions (any substring, longest repeated substring) in
      $O(n \log n)$ or $O(n)$ to build.
    - **Gusfield's book** presents the Z-algorithm as the "fundamental preprocessing" and builds Boyer–Moore and
      other matchers on top of it.

## See also

- [KMP](kmp.md)
- [Rabin-Karp](rabin-karp.md)
- [Strings](index.md)

## References

- D. Gusfield, *Algorithms on Strings, Trees, and Sequences*, Cambridge University Press, 1997, Chapter 1.
- M. G. Main and R. J. Lorentz, "An O(n log n) algorithm for finding all repetitions in a string", *Journal of
  Algorithms* 5(3), 1984 (an early use of the same preprocessing).
