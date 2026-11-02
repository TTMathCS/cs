# Edit distance

*How many single-letter changes (insert a letter, delete a letter, replace a letter) turn one word into another?
This number, the Levenshtein distance, is found with a table over the two prefixes.*

| Time | Extra space | Output |
|---|---|---|
| $O(nm)$ for lengths $n$ and $m$ | $O(nm)$, or $O(\min(n, m))$ for the number alone | the distance and the list of edits |

## The idea

`kitten` becomes `sitting` in 3 edits: replace k with s, replace e with i, insert g. No way with 2 exists.

As with the [longest common subsequence](lcs.md), look at the **last letters**. To turn the first $i$ letters of
$a$ into the first $j$ letters of $b$, the last edit was one of:

- **keep** (if $a_i = b_j$) or **replace** $a_i$ by $b_j$: then turn $a_1..a_{i-1}$ into $b_1..b_{j-1}$;
- **delete** $a_i$: then turn $a_1..a_{i-1}$ into $b_1..b_j$;
- **insert** $b_j$ at the end: then turn $a_1..a_i$ into $b_1..b_{j-1}$.

$$D[i][j] = \min\big(D[i-1][j-1] + [a_i \ne b_j],\; D[i-1][j] + 1,\; D[i][j-1] + 1\big)$$

with $D[i][0] = i$ (delete everything) and $D[0][j] = j$ (insert everything). $[a_i \ne b_j]$ is 1 when the letters
differ and 0 when they are equal.

## How it works

1. Fill row 0 with $0, 1, 2, \dots, m$ and column 0 with $0, 1, \dots, n$.
2. Fill the rest row by row with the rule above.
3. $D[n][m]$ is the distance. To list the edits, walk back from the corner, at each cell choosing a neighbour that
   gives its value.

## Code

=== "Python"

    ```python
    --8<-- "dp/edit_distance.py"
    ```

=== "Java"

    ```java
    --8<-- "dp/EditDistance.java"
    ```

=== "C++"

    ```cpp
    --8<-- "dp/edit_distance.cpp"
    ```

Output:

- `kitten sitting 3 replace k with s; replace e with i; insert g`
- `sunday saturday 3 insert a; insert t; replace n with r`
- `mars stars 2 insert s; replace m with t`

## When to use it

- **Spelling correction:** suggest dictionary words at distance 1 or 2 from what was typed.
- **Fuzzy search** and matching of names with typos, OCR errors, or different spellings.
- **Biology:** counting mutations between DNA sequences (with weights, sequence alignment).
- **Comparing versions of short texts,** or measuring how well a speech recognizer did (word error rate is edit
  distance on words).

## Common mistakes

- **Forgetting the first row and column:** they are not zero but $0, 1, 2, \dots$
- **Mixing up which neighbour is insert and which is delete:** up ($D[i-1][j]$) uses up a letter of $a$ (delete);
  left ($D[i][j-1]$) produces a letter of $b$ (insert).
- **Treating swaps as one edit:** plain Levenshtein counts `ab` → `ba` as 2; Damerau–Levenshtein adds
  transposition as one edit.
- **Memory on long strings:** keep only two rows if the edits are not needed.

## Going deeper

Each part below starts closed; open the ones you want.

??? example "Sample walkthrough: kitten → sitting"

    | | ∅ | s | i | t | t | i | n | g |
    |---|---|---|---|---|---|---|---|---|
    | **∅** | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 |
    | **k** | 1 | 1 | 2 | 3 | 4 | 5 | 6 | 7 |
    | **i** | 2 | 2 | 1 | 2 | 3 | 4 | 5 | 6 |
    | **t** | 3 | 3 | 2 | 1 | 2 | 3 | 4 | 5 |
    | **t** | 4 | 4 | 3 | 2 | 1 | 2 | 3 | 4 |
    | **e** | 5 | 5 | 4 | 3 | 2 | 2 | 3 | 4 |
    | **n** | 6 | 6 | 5 | 4 | 3 | 3 | 2 | 3 |

    Two cells explained:

    - Row **k**, column **s**: k ≠ s; replace from $D[0][0] = 0$ gives 1, delete from $D[0][1] = 1$ gives 2,
      insert from $D[1][0] = 1$ gives 2. So 1.
    - Row **e**, column **i** (the second i): e ≠ i; replace from $D[4][4] = 1$ gives **2**.

    Walk back from 3 (row n, column g): insert g (from 2); n = n, keep (from 2); e ≠ i, replace (from 1); t, t, i
    kept along the diagonal; k ≠ s, replace (from 0). Three edits.

??? abstract "The math: it is a true distance, and how fast it can be"

    **Correctness.** Any sequence of edits can be rearranged to work from left to right, so the edits that touch
    the last letters can be taken to be last; the three cases above are all the possibilities for them, and the
    rest must itself be optimal. Hence the minimum over the three cases.

    **A metric.** Edit distance satisfies $D(a, a) = 0$; $D(a, b) > 0$ when $a \ne b$; $D(a, b) = D(b, a)$ (each
    edit has an opposite edit of the same cost); and the triangle inequality $D(a, c) \le D(a, b) + D(b, c)$
    (do the edits one after the other). This is what lets search structures such as BK-trees prune.

    **Bounds.** $|n - m| \le D(a, b) \le \max(n, m)$. With only insertions and deletions allowed,
    $D = n + m - 2\,\text{LCS}(a, b)$.

    **Time.** $(n+1)(m+1)$ cells, $O(1)$ each. Backurs and Indyk (2015) showed that a truly subquadratic algorithm,
    $O(n^{2-\varepsilon})$, would refute the Strong Exponential Time Hypothesis. If the distance $d$ is known to be
    small, only a band of width $2d + 1$ around the diagonal is needed: $O(d \cdot \min(n, m))$ (Ukkonen, 1985).

??? tip "Watch it step by step"

    Orange is the cell the new value came from; green means the letters matched (keep), red means an edit was
    needed. The last frame shows one cheapest path in purple.

    <div class="cs-anim" data-anim="edit-distance"></div>

??? info "Variations and related ideas"

    - **Weighted edits:** different costs for each operation or each pair of letters (for example, keys next to
      each other on a keyboard cost less).
    - **Damerau–Levenshtein:** also allows swapping two neighbouring letters as one edit.
    - **Hamming distance:** for equal lengths, only replacements; just count the differing positions in $O(n)$.
    - **Needleman–Wunsch** (global) and **Smith–Waterman** (local) alignment in biology use the same table with
      scores and gap penalties.

## See also

- [Longest common subsequence](lcs.md)
- [Trie](../data-structures/trie.md): searching a dictionary for close words
- [Dynamic programming](index.md)

## References

- V. I. Levenshtein, "Binary codes capable of correcting deletions, insertions, and reversals", *Soviet Physics
  Doklady* 10(8), 1966.
- R. A. Wagner and M. J. Fischer, "The string-to-string correction problem", *Journal of the ACM* 21(1), 1974.
- E. Ukkonen, "Algorithms for approximate string matching", *Information and Control* 64, 1985.
- A. Backurs and P. Indyk, "Edit distance cannot be computed in strongly subquadratic time (unless SETH is
  false)", *STOC* 2015.
