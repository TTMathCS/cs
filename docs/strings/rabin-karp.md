# Rabin-Karp

*Turn the pattern and every window of the text into a number (a hash). Different numbers mean "certainly not a
match", so letters are compared only where the numbers agree. Each window's number is updated from the previous
one in constant time.*

| Expected time | Worst time | Extra space | Output |
|---|---|---|---|
| $O(n + m)$ | $O(nm)$ (only if hashes keep colliding) | $O(1)$ | every position where the pattern starts |

## The idea

Read a string as a number written in base $B$ (here $B = 256$, one "digit" per byte), and keep only its remainder
modulo a prime $q$:

$$h(c_0 c_1 \dots c_{m-1}) = \left(c_0 B^{m-1} + c_1 B^{m-2} + \dots + c_{m-1}\right) \bmod q.$$

Comparing two numbers is one step, while comparing two strings is up to $m$ steps. If the hashes differ, the
strings differ. If they are equal, the strings are *probably* equal; check the letters to be sure.

The key is the **rolling hash**: moving the window one place right removes the first letter and adds a new last
one, exactly like shifting a decimal number:

$$h_{s+1} = \big((h_s - t_s B^{m-1}) \cdot B + t_{s+m}\big) \bmod q.$$

So all $n - m + 1$ window hashes cost $O(n)$ together.

## How it works

1. Compute `high` $= B^{m-1} \bmod q$, the hash of the pattern, and the hash of the first window.
2. For each window start `s`: if the hashes are equal, compare the letters (a real match, or a **false alarm**).
   Then roll the hash to the next window.

## Code

=== "Python"

    ```python
    --8<-- "strings/rabin_karp.py"
    ```

=== "Java"

    ```java
    --8<-- "strings/RabinKarp.java"
    ```

=== "C++"

    ```cpp
    --8<-- "strings/rabin_karp.cpp"
    ```

Output: `[15, 37] 0`, the two places `mars` appears, with no false alarms when $q = 1{,}000{,}000{,}007$; then
`[15, 37] 3`: the same answer with $q = 13$, but three windows had the right hash and the wrong letters; then
`[0, 7] 0` for `abra` in `abracadabra`.

## When to use it

- **Many patterns of the same length:** put all their hashes in a [hash table](../data-structures/hash-table.md)
  and check each window against all of them in $O(1)$.
- **Plagiarism and duplicate detection:** hash every run of $k$ words in two documents and count the shared hashes
  (the idea behind "shingling" and the MOSS tool).
- **Two-dimensional matching:** hash rows, then hash the column of row hashes.
- **Comparing substrings quickly:** with prefix hashes, any two substrings can be compared in $O(1)$; used with
  [binary search](../searching/binary-search.md) for the longest repeated substring.

## Common mistakes

- **Trusting equal hashes** without checking the letters (unless a tiny chance of error is acceptable).
- **Negative numbers:** in Java and C++, `%` of a negative number is negative; add $q$ before taking the remainder.
- **Overflow:** $h \cdot B$ must fit in the integer type. With $q \approx 10^9$ and $B = 256$, 64-bit integers
  are enough; with larger $q$ use 128-bit multiplication or a different scheme.
- **A small or non-prime modulus**, or a fixed base an attacker knows: they can craft texts with many false
  alarms. Pick the base at random.

## Going deeper

Each part below starts closed; open the ones you want.

??? example "Sample walkthrough: mars in \"stars on mars\", q = 13"

    With $B = 256$ and $q = 13$, $h(\texttt{mars}) = 7$. The ten windows:

    | Start | Window | Hash | Result |
    |---|---|---|---|
    | 0 | `star` | 7 | equal hash, letters differ: **false alarm** |
    | 1 | `tars` | 1 | skip |
    | 2 | `ars␣` | 11 | skip |
    | 3 | `rs␣o` | 0 | skip |
    | 4 | `s␣on` | 7 | **false alarm** |
    | 5 | `␣on␣` | 9 | skip |
    | 6 | `on␣m` | 6 | skip |
    | 7 | `n␣ma` | 10 | skip |
    | 8 | `␣mar` | 7 | **false alarm** |
    | 9 | `mars` | 7 | **match** |

    With only 13 possible hash values, about one window in 13 collides by chance; here it was 3 in 9. With
    $q \approx 10^9$ a false alarm is about a one-in-a-billion event per window.

??? abstract "The math: how likely is a false alarm?"

    Two different strings $x \ne y$ of length $m$ have equal hashes exactly when $q$ divides the difference
    $D = \text{val}(x) - \text{val}(y)$, a nonzero number below $B^m$.

    **Random prime.** $D$ has at most $\log_2 D < m \log_2 B$ prime factors. If $q$ is chosen at random among the
    primes up to some bound $Q$ (there are about $Q / \ln Q$ of them), the chance that $q$ is one of $D$'s factors is
    at most $\frac{m \log_2 B \cdot \ln Q}{Q}$, which is tiny for $Q$ much larger than $nm$.

    **Random base, fixed prime.** The hash is the polynomial $\sum c_i X^{m-1-i}$ evaluated at $X = B$. Two
    different strings give two different polynomials of degree below $m$; their difference has at most $m - 1$
    roots modulo the prime $q$. So for a random $B$, $\Pr[\text{collision}] \le \frac{m-1}{q}$.

    **Expected time.** Over $n - m + 1$ windows, the expected number of false alarms is at most
    $n \cdot \frac{m}{q}$, each costing $O(m)$ to check; with $q > nm$ that is $O(m)$ extra in expectation. Plus
    $O(m)$ per real match. Total $O(n + m + m \cdot \#\text{matches})$.

    **Worst case.** If every window collides (for example, $q$ chosen badly and an adversarial text), every
    window is checked: $O(nm)$.

??? tip "Watch it step by step"

    Blue is the current window; red means equal hashes but different letters (a false alarm); purple is a real match.

    <div class="cs-anim" data-anim="rabin-karp"></div>

??? info "Variations and related ideas"

    - **Double hashing:** two hashes with different moduli; a false alarm needs both to collide.
    - **Mersenne prime $2^{61} - 1$:** fast remainder with shifts, and a very low collision rate.
    - **Rolling hashes in backups and sync tools** (rsync, content-defined chunking): find where two files agree
      even after insertions.
    - **Karp and Rabin's original paper** used fingerprints as a randomized algorithm with a provable error bound.

## See also

- [Hash table](../data-structures/hash-table.md)
- [KMP](kmp.md): no randomness, guaranteed linear time
- [Fast exponentiation](../number-theory/fast-power.md): computing $B^{m-1} \bmod q$

## References

- R. M. Karp and M. O. Rabin, "Efficient randomized pattern-matching algorithms", *IBM Journal of Research and
  Development* 31(2), 1987.
- T. H. Cormen et al., *Introduction to Algorithms*, 4th ed., Section 32.2 (the Rabin-Karp algorithm).
