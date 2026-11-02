# N-Queens

*Place $n$ chess queens on an $n \times n$ board so that no two attack each other (no two share a row, a column
or a diagonal). Backtracking places one queen per row and steps back as soon as a row has no safe square.*

| Time | Extra space | Output |
|---|---|---|
| exponential, but heavily pruned (2,057 partial boards for $n = 8$) | $O(n)$ | the number of solutions and the first one |

## The idea

A queen attacks along its row, its column and both diagonals. Since no two queens may share a row, there is
exactly **one queen per row**. So: place a queen in row 0, then find a safe column in row 1, then in row 2, and
so on. If some row has no safe column, the earlier choices were wrong: **back up** to the previous row and move
its queen to the next column.

To check "is this square safe?" in $O(1)$, keep three lists of flags:

- `cols[c]`: column $c$ has a queen;
- `diag1[r + c]`: the "/" diagonal through $(r, c)$ has a queen (along it, $r + c$ is constant);
- `diag2[r - c + n]`: the "\\" diagonal has a queen (along it, $r - c$ is constant; $+n$ keeps the index positive).

## How it works

1. `go(r)`: if $r = n$, all queens are placed: count the solution.
2. Otherwise, for each column $c$: if column $c$ and both diagonals are free, mark them, record the queen,
   call `go(r + 1)`, then clear the marks.

## Code

=== "Python"

    ```python
    --8<-- "backtracking/n_queens.py"
    ```

=== "Java"

    ```java
    --8<-- "backtracking/NQueens.java"
    ```

=== "C++"

    ```cpp
    --8<-- "backtracking/n_queens.cpp"
    ```

Output: the number of solutions for $n = 1$ to 10, `[1, 0, 0, 2, 10, 4, 40, 92, 352, 724]`; the first solution
for 8 queens, `[0, 4, 7, 5, 2, 6, 1, 3]` (row 0 has its queen in column 0, row 1 in column 4, ...); and the first
6-queens board:

```text
.Q....
...Q..
.....Q
Q.....
..Q...
....Q.
```

## When to use it

- **Constraint puzzles:** Sudoku, crosswords, map colouring, timetables and seating plans have the same shape:
  fill slots one by one, check the rules at once, back up on a dead end.
- **As a benchmark:** N-Queens is the standard example for testing search and pruning ideas.
- **When you need one solution for large $n$:** backtracking finds one quickly up to a few dozen; for huge
  $n$ there are direct formulas or local search (see Variations).

## Common mistakes

- **Checking the whole board for every square:** $O(n)$ or $O(n^2)$ per check instead of $O(1)$ with the flag lists.
- **Wrong diagonal index:** $r - c$ can be negative; shift it by $n$.
- **Forgetting to clear the flags** after the recursive call.
- **Expecting solutions for $n = 2$ and 3:** there are none.

## Going deeper

Each part below starts closed; open the ones you want.

??? example "Sample walkthrough: 4 queens"

    Columns are numbered 0–3.

    1. Row 0: queen in column 0.
    2. Row 1: columns 0 and 1 are attacked; column 2 is safe. Row 2: every column is attacked, so back up.
    3. Row 1: column 3. Row 2: column 0 attacked, column 1 safe. Row 3: every column attacked, so back up.
    4. Row 2: columns 2 and 3 attacked. Row 1 has no columns left, so back up to row 0.
    5. Row 0: column 1. Row 1: column 3. Row 2: column 0. Row 3: column 2. **Solution `[1, 3, 0, 2]`**:

    ```text
    .Q..
    ...Q
    Q...
    ..Q.
    ```

    The other 4-queens solution is its mirror image, `[2, 0, 3, 1]`.

??? abstract "The math: how much pruning helps, and how many solutions there are"

    **Search space.**

    | Approach | Boards looked at for $n = 8$ |
    |---|---|
    | any 8 of the 64 squares | $\binom{64}{8} = 4{,}426{,}165{,}368$ |
    | one queen per row | $8^8 = 16{,}777{,}216$ |
    | one per row and column (permutations) | $8! = 40{,}320$ |
    | backtracking with early checks (this code) | **2,057** partial boards (nodes of the search tree) |

    **Number of solutions** $Q(n)$: 1, 0, 0, 2, 10, 4, 40, 92, 352, 724, ... (OEIS A000170). The 92 solutions for
    $n = 8$ come in groups related by rotating and reflecting the board; there are 12 essentially different ones.
    No simple formula is known; $Q(27)$ was computed in 2016 with a large distributed search. Simkin (2021) showed
    that $Q(n) = \left((1 + o(1))\, n e^{-\alpha}\right)^n$ with $\alpha \approx 1.944$.

    **A solution always exists for $n \ge 4$**, and one can be written down directly (constructions going back to
    the 19th century), so finding *one* solution is easy even for huge $n$. Counting all of them is the hard part.

??? tip "Watch it step by step"

    Green: queens placed. Faded blue: squares attacked by them in later rows. Red ✕: the square just tried and
    found attacked. Purple: the finished solution.

    <div class="cs-anim" data-anim="n-queens"></div>

??? info "Variations and related ideas"

    - **Bitmasks:** keep the three flag lists as bits of three integers; the free columns of a row are
      `~(cols | d1 | d2) & ((1 << n) - 1)`; this is the fastest known way to count solutions.
    - **Symmetry:** only try the first queen in the left half of row 0 and double the count (care with the middle
      column when $n$ is odd).
    - **Min-conflicts local search:** start with any placement and move queens to reduce attacks; solves a million
      queens in seconds.
    - **Exact cover:** N-Queens, Sudoku and pentomino puzzles can all be phrased as exact cover and solved with
      Knuth's Algorithm X ("dancing links").

## See also

- [Subsets and permutations](subsets-permutations.md)
- [Depth-first search](../graphs/dfs.md): backtracking is a DFS of the decision tree
- [Backtracking](index.md)

## References

- N. Wirth, *Algorithms + Data Structures = Programs*, Prentice-Hall, 1976, Section 3.5 (the eight queens problem).
- J. Bell and B. Stevens, "A survey of known results and research areas for n-queens", *Discrete Mathematics*
  309(1), 2009.
- M. Simkin, "The number of n-queens configurations", *Advances in Mathematics* 427, 2023.
- D. E. Knuth, "Dancing links", in *Millennial Perspectives in Computer Science*, 2000.
