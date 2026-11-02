# Knuth-Morris-Pratt (KMP)

*Search for a pattern without ever moving backwards in the text. When a mismatch happens, a small table of the
pattern's own repeats says how far the pattern can safely slide.*

| Time | Extra space | Output |
|---|---|---|
| $O(n + m)$, worst case | $O(m)$ for the table | every position where the pattern starts |

## The idea

Searching for `ABABCABAB`, suppose the first four letters `ABAB` matched and then the fifth failed. The naive
method shifts the pattern by one and starts again from scratch, re-reading text it has already seen.

KMP notices that the matched part `ABAB` **ends with** `AB`, which is also how the pattern **starts**. So after
the mismatch, slide the pattern so that its first `AB` sits under the text's last `AB`, and carry on comparing
from there. No text letter is read twice in a row of successes, and the text pointer never goes back.

How far to slide depends only on the pattern, so it is worked out once, in the **prefix function**:

$$\pi[i] = \text{length of the longest proper prefix of } P[0..i] \text{ that is also a suffix of it.}$$

For `ABABCABAB`: $\pi = [0, 0, 1, 2, 0, 1, 2, 3, 4]$.

## How it works

1. **Build $\pi$.** Keep `k`, the length of the current border. For each new letter `P[i]`: while `k > 0` and
   `P[i] ≠ P[k]`, fall back to `k = π[k-1]`. If `P[i] = P[k]`, increase `k`. Set `π[i] = k`.
2. **Search.** The same loop on the text: `k` is how many pattern letters currently match. On a mismatch fall back
   with $\pi$; on a match increase `k`; when `k = m`, report a match at `i - m + 1` and set `k = π[m-1]` to keep
   looking for overlapping matches.

## Code

=== "Python"

    ```python
    --8<-- "strings/kmp.py"
    ```

=== "Java"

    ```java
    --8<-- "strings/Kmp.java"
    ```

=== "C++"

    ```cpp
    --8<-- "strings/kmp.cpp"
    ```

Output: the prefix function `[0, 0, 1, 2, 0, 1, 2, 3, 4]`; a match at `[10]`; then `[0, 1, 2, 3]` (overlapping
matches of `AA` in `AAAAA`) and `[]` (`mars` does not appear in `olympus mons`).

## When to use it

- **Searching a stream** (a file read once, network packets): the text pointer never goes back, so nothing needs
  to be buffered.
- **Guaranteed time:** no bad cases, unlike the naive method or hashing.
- **The prefix function on its own** answers other questions: the shortest period of a string is
  $m - \pi[m-1]$; counting how often each prefix occurs; building an automaton for the pattern.

## Common mistakes

- **Moving the text pointer back** after a mismatch: that is the naive method again.
- **Using `if` instead of `while`** when falling back: one step back may not be enough.
- **Forgetting `k = π[m-1]` after a match:** the next search step would read past the end of the pattern, or miss
  overlapping matches.
- **Off-by-one in $\pi$:** it uses *proper* prefixes, so $\pi[0] = 0$ always.

## Going deeper

Each part below starts closed; open the ones you want.

??? example "Sample walkthrough: ABABCABAB in ABABDABACDABABCABAB"

    | Text position | What happens | k after |
    |---|---|---|
    | 0–3 | `A B A B` match | 4 |
    | 4 | `D` ≠ `C`: fall back to π[3] = 2; `D` ≠ `A`: fall back to π[1] = 0; `D` ≠ `A` | 0 |
    | 5–7 | `A B A` match | 3 |
    | 8 | `C` ≠ `B`: fall back to π[2] = 1; `C` ≠ `B`: to π[0] = 0; `C` ≠ `A` | 0 |
    | 9 | `D` ≠ `A` | 0 |
    | 10–18 | all nine letters match | 9 → **match at 10** |

    23 letter comparisons in all, against up to $11 \times 9 = 99$ for the naive method on this text.

    **Building π for ABABCABAB:** `B` vs `A` no (0); `A` = `A` (1); `B` = `B` (2); `C` vs `A` after falling back
    from 2 → 0: no (0); then `A B A B` grow it again to 1, 2, 3, 4.

??? abstract "The math: why the fall-back is safe, and the linear bound"

    **Borders of borders.** If $b$ is the longest border of $s$, then the borders of $s$ are exactly $b$ and the
    borders of $b$. So the borders of $P[0..i]$, from longest to shortest, are
    $\pi[i], \pi[\pi[i]-1], \dots$, down to 0. Falling back with $k \leftarrow \pi[k-1]$ visits them in that order.

    **Nothing is skipped.** After a mismatch with $k$ letters matched, any match of $P$ that starts inside those $k$
    letters must line up a prefix of $P$ with a suffix of the matched part, which is a border. Trying the borders
    from longest to shortest therefore never jumps over a possible match.

    **Linear time (amortized).** In the search, $k$ goes up by at most 1 per text letter, so at most $n$ times in
    total. Each fall-back makes $k$ strictly smaller, and $k \ge 0$, so there are at most $n$ fall-backs. Total
    comparisons: at most $2n$. The same argument gives $2m$ for building $\pi$.

    **Period.** $P$ has period $p$ exactly when it has a border of length $m - p$, so its shortest period is
    $m - \pi[m-1]$.

??? tip "Watch it step by step"

    Green letters are already matched, orange is the pair being compared, red a mismatch. Notice how the pattern
    jumps forward but the text column never moves left.

    <div class="cs-anim" data-anim="kmp"></div>

??? info "Variations and related ideas"

    - **KMP automaton:** precompute, for every state $k$ and letter $c$, the next state; then the search is one
      table look-up per letter.
    - **Aho–Corasick:** KMP for many patterns at once, on a [trie](../data-structures/trie.md) with failure links;
      used in virus scanners and `grep -F`.
    - **Boyer–Moore:** compares from the **end** of the pattern and can skip large parts of the text; often faster
      in practice on natural language.
    - **The [Z-algorithm](z-algorithm.md)** computes closely related information and can replace $\pi$ in most uses.

## See also

- [Rabin-Karp](rabin-karp.md)
- [Z-algorithm](z-algorithm.md)
- [Trie](../data-structures/trie.md)

## References

- D. E. Knuth, J. H. Morris and V. R. Pratt, "Fast pattern matching in strings", *SIAM Journal on Computing* 6(2), 1977.
- T. H. Cormen et al., *Introduction to Algorithms*, 4th ed., Chapter 32 (string matching).
- D. Gusfield, *Algorithms on Strings, Trees, and Sequences*, Cambridge University Press, 1997.
