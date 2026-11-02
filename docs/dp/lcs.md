# Longest common subsequence

*Find the longest string whose letters appear, in the same order, in both of two strings (they need not be next
to each other). A table over the two prefixes does it; it is the heart of `diff` and of DNA comparison.*

| Time | Extra space | Output |
|---|---|---|
| $O(nm)$ for lengths $n$ and $m$ | $O(nm)$, or $O(\min(n, m))$ for the length alone | the length and one longest common subsequence |

## The idea

A **subsequence** keeps some letters of a string, in order, and drops the rest: `ACE` is a subsequence of
`ABCDE`. The **longest common subsequence** (LCS) of `ABCBDAB` and `BDCABA` has length 4, for example `BCBA`.

Look at the **last letters**:

- If they are **equal**, they can be matched together, and the rest is the LCS of the two shorter strings, plus 1.
- If they **differ**, at least one of them is not in the LCS: drop the last letter of the first string, or of the
  second, and take the better.

Let $L[i][j]$ be the LCS length of the first $i$ letters of $a$ and the first $j$ letters of $b$:

$$L[i][j] = \begin{cases} L[i-1][j-1] + 1 & \text{if } a_i = b_j \\ \max(L[i-1][j],\; L[i][j-1]) & \text{otherwise} \end{cases}$$

with $L[0][j] = L[i][0] = 0$.

## How it works

1. Make an $(n+1) \times (m+1)$ table with a zero row and a zero column.
2. Fill it row by row with the rule above.
3. $L[n][m]$ is the length. To get the letters, walk back from the corner: on a match, take the letter and go
   diagonally; otherwise go to the bigger of up and left.

## Code

=== "Python"

    ```python
    --8<-- "dp/lcs.py"
    ```

=== "Java"

    ```java
    --8<-- "dp/Lcs.java"
    ```

=== "C++"

    ```cpp
    --8<-- "dp/lcs.cpp"
    ```

Output: `4 BCBA`, `4 GTAB` and `3 LYM`. There can be several longest common subsequences
(`BCAB` and `BDAB` also have length 4); which one is printed depends on how ties are broken in the walk back.

## When to use it

- **`diff` and version control:** the lines two files have in common, in order, are an LCS of their lines;
  everything else is shown as added or removed.
- **Biology:** comparing DNA or protein sequences (with scores, this becomes sequence alignment).
- **Plagiarism and similarity checks**, spelling suggestions, merging two edited copies of a document.

## Common mistakes

- **Confusing subsequence with substring:** a substring must be contiguous. The longest common *substring* uses
  $L[i][j] = L[i-1][j-1] + 1$ on a match and **0** otherwise, and the answer is the largest cell anywhere.
- **Off-by-one:** row $i$ is about letter $a_{i-1}$ in 0-based code.
- **Running out of memory** on long strings: $10^5 \times 10^5$ cells is 10 billion. For the length alone keep two
  rows; for the letters too, use Hirschberg's method.

## Going deeper

Each part below starts closed; open the ones you want.

??? example "Sample walkthrough: ABCBDAB and BDCABA"

    | | ∅ | B | D | C | A | B | A |
    |---|---|---|---|---|---|---|---|
    | **∅** | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
    | **A** | 0 | 0 | 0 | 0 | 1 | 1 | 1 |
    | **B** | 0 | 1 | 1 | 1 | 1 | 2 | 2 |
    | **C** | 0 | 1 | 1 | 2 | 2 | 2 | 2 |
    | **B** | 0 | 1 | 1 | 2 | 2 | 3 | 3 |
    | **D** | 0 | 1 | 2 | 2 | 2 | 3 | 3 |
    | **A** | 0 | 1 | 2 | 2 | 3 | 3 | 4 |
    | **B** | 0 | 1 | 2 | 2 | 3 | 4 | 4 |

    Walk back from the bottom-right 4: B ≠ A, and up (4) ≥ left (4), so go up; A = A, match **A**, go diagonally to
    row D, column B (3); D ≠ B, up (3) ≥ left (2), go up; B = B, match **B** (2); C ≠ A, up (1) < left (2), go
    left; C = C, match **C** (1); B ≠ D, up (0) < left (1), go left; B = B, match **B**. Read backwards: **BCBA**.

??? abstract "The math: why the rule is right, and the limits"

    **Optimal substructure.** Let $Z = z_1 \dots z_k$ be an LCS of $a_1 \dots a_i$ and $b_1 \dots b_j$.

    - If $a_i = b_j$, then $z_k = a_i$ (otherwise appending it would give a longer common subsequence), and
      $z_1 \dots z_{k-1}$ is an LCS of the two strings without their last letters.
    - If $a_i \ne b_j$, then $z_k$ is not $a_i$ or not $b_j$ (or neither), so $Z$ is a common subsequence of one
      of the shortened pairs; hence $k = \max(L[i-1][j], L[i][j-1])$.

    **Time and space.** $nm$ cells of $O(1)$ work each. **Hirschberg** (1975) recovers an LCS in $O(nm)$ time and
    only $O(n + m)$ space by divide and conquer: find where an optimal path crosses the middle row using a forward
    pass and a backward pass, then solve the two halves.

    **No much faster algorithm is likely.** Abboud, Backurs and Vassilevska Williams (2015) showed that an
    $O(n^{2 - \varepsilon})$ algorithm for LCS would break the Strong Exponential Time Hypothesis. The best known
    improvement is the "Four Russians" trick, $O(n^2 / \log n)$ (Masek and Paterson, 1980).

    **Link with edit distance.** If only insertions and deletions are allowed, the edit distance is
    $n + m - 2\,\text{LCS}$.

??? tip "Watch it step by step"

    Green is a match (diagonal + 1); red takes the larger of the two orange neighbours. The last frame shows the
    walk back, with the matched letters in green.

    <div class="cs-anim" data-anim="lcs"></div>

??? info "Variations and related ideas"

    - **Longest common substring:** the contiguous version (see Common mistakes), or $O(n + m)$ with a suffix
      automaton.
    - **Shortest common supersequence:** the shortest string containing both as subsequences has length
      $n + m - \text{LCS}$.
    - **Hunt–Szymanski:** fast when few pairs of letters match, $O((r + n) \log n)$ for $r$ matching pairs.
    - **Myers' diff algorithm** (1986): $O((n + m)D)$, where $D$ is the size of the difference; it is what `git diff`
      uses by default.
    - **Sequence alignment** (Needleman–Wunsch, Smith–Waterman): the same table with scores for matches,
      mismatches and gaps.

## See also

- [Edit distance](edit-distance.md)
- [Longest increasing subsequence](lis.md): LCS of a list and its sorted copy
- [KMP](../strings/kmp.md): finding one string inside another

## References

- D. S. Hirschberg, "A linear space algorithm for computing maximal common subsequences", *Communications of the
  ACM* 18(6), 1975.
- E. W. Myers, "An O(ND) difference algorithm and its variations", *Algorithmica* 1, 1986.
- A. Abboud, A. Backurs and V. Vassilevska Williams, "Tight hardness results for LCS and other sequence similarity
  measures", *FOCS* 2015.
- T. H. Cormen et al., *Introduction to Algorithms*, 4th ed., Section 14.4 (longest common subsequence).
