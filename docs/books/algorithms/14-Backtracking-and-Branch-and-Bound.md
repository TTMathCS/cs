# 14. Backtracking and branch and bound

*Some problems have no known clever recurrence and no safe greedy rule: placing queens on a chessboard, filling a
Sudoku, packing a knapsack with large weights, touring cities. For these the honest method is to search through the
possible solutions. Done naively, that is hopeless, because the number of candidates grows exponentially. In this
chapter you will learn to search systematically, by building solutions one choice at a time and abandoning a partial
solution the moment it cannot succeed (backtracking), or cannot beat the best answer found so far (branch and bound).
You will also split searches in half (meet in the middle) and learn how computer scientists prove that a search
algorithm takes $O(1.38^n)$ instead of $O(2^n)$ time.*

!!! abstract "In this chapter"
    **You will learn:**

    - the state-space tree: how every exhaustive search is a walk through a tree of partial solutions
    - the backtracking template, and how to generate subsets, permutations and combinations with it
    - N-Queens, and Sudoku solved by constraint propagation plus "fewest options first"
    - bounding functions and branch and bound, for the 0/1 knapsack and the travelling salesman
    - meet in the middle: subset sum in $O(2^{n/2})$ instead of $O(2^n)$
    - how to analyse branching algorithms with branching vectors, and how to estimate the size of a search tree

    **You need:** [Chapter 3](03-Recursion-and-Induction.md) (recursion and recurrences),
    [Chapter 12](12-Greedy-Algorithms.md) (the fractional knapsack) and [Chapter 13](13-Dynamic-Programming.md)
    (the knapsack DP and Held-Karp, for comparison).

    **Levels:** 14.1 and 14.2 are beginner; 14.3 to 14.5 are intermediate; 14.6 is advanced.

## 14.1 Exhaustive search, the state-space tree

A lock has three dials, each showing a digit. You have forgotten the code. You can try 000, 001, 002, and so on up to
999: at most a thousand tries, and you are certain to open it. That is **exhaustive search**, or **brute force**: list
every candidate solution and check each one. It is always correct, and it is the baseline against which every cleverer
method is measured.

The trouble is counting. With $n$ yes-or-no decisions there are $2^n$ candidates: about a thousand for $n = 10$, a
million for 20, and $10^{18}$ for 60. With $n$ items to put in order there are $n!$ candidates, which passes $10^{18}$
already at $n = 20$. At a billion candidates per second, $10^{18}$ takes about 30 years.

### The tree of partial solutions

Most candidate solutions are built from a sequence of choices: for each item, take it or not; for each row of a board,
which column; for each step of a tour, which city next. Arrange the choices as a tree:

- the **root** is the empty partial solution, with no choices made;
- each **node** is a partial solution: the choices made so far;
- the **children** of a node are the partial solutions obtained by making one more choice;
- the **leaves** are complete candidates.

This is the **state-space tree** (or **search tree**). Exhaustive search is a walk over the whole tree, usually depth
first: make a choice, go down, and when you reach a leaf or run out of choices, go back up (**backtrack**) to the most
recent node that still has untried choices.

<figure class="mars-fig" markdown="0">
<svg viewBox="0 0 640 271" role="img" aria-label="A binary tree of depth three. From the start node, each level branches into taking or leaving one item: a, then b, then c. The eight leaves are the subsets a b c, a b, a c, a, b c, b, c and the empty set.">
<g stroke="currentColor" stroke-width="1.2">
<line x1="320" y1="41" x2="166" y2="79"/>
<line x1="320" y1="41" x2="474" y2="79"/>
<line x1="166" y1="105" x2="89" y2="143"/>
<line x1="166" y1="105" x2="243" y2="143"/>
<line x1="89" y1="169" x2="50" y2="207"/>
<line x1="89" y1="169" x2="127" y2="207"/>
<line x1="243" y1="169" x2="204" y2="207"/>
<line x1="243" y1="169" x2="281" y2="207"/>
<line x1="474" y1="105" x2="397" y2="143"/>
<line x1="474" y1="105" x2="551" y2="143"/>
<line x1="397" y1="169" x2="359" y2="207"/>
<line x1="397" y1="169" x2="436" y2="207"/>
<line x1="551" y1="169" x2="513" y2="207"/>
<line x1="551" y1="169" x2="590" y2="207"/>
</g>
<rect x="290" y="15" width="60" height="26" rx="5" style="fill:var(--md-default-bg-color)"/>
<rect x="290" y="15" width="60" height="26" rx="5" stroke="currentColor" stroke-width="1.2" fill="#9cc9ea" fill-opacity="0.5"/>
<text x="320" y="33" font-size="13" text-anchor="middle" fill="currentColor" font-family="monospace">start</text>
<rect x="136" y="79" width="60" height="26" rx="5" style="fill:var(--md-default-bg-color)"/>
<rect x="136" y="79" width="60" height="26" rx="5" stroke="currentColor" stroke-width="1.2" fill="#9cc9ea" fill-opacity="0.5"/>
<text x="166" y="97" font-size="13" text-anchor="middle" fill="currentColor" font-family="monospace">+a</text>
<rect x="59" y="143" width="60" height="26" rx="5" style="fill:var(--md-default-bg-color)"/>
<rect x="59" y="143" width="60" height="26" rx="5" stroke="currentColor" stroke-width="1.2" fill="#9cc9ea" fill-opacity="0.5"/>
<text x="89" y="161" font-size="13" text-anchor="middle" fill="currentColor" font-family="monospace">+b</text>
<rect x="20" y="207" width="60" height="26" rx="5" style="fill:var(--md-default-bg-color)"/>
<rect x="20" y="207" width="60" height="26" rx="5" stroke="currentColor" stroke-width="1.2" fill="#7ccf9a" fill-opacity="0.5"/>
<text x="50" y="225" font-size="13" text-anchor="middle" fill="currentColor" font-family="monospace">{a,b,c}</text>
<rect x="97" y="207" width="60" height="26" rx="5" style="fill:var(--md-default-bg-color)"/>
<rect x="97" y="207" width="60" height="26" rx="5" stroke="currentColor" stroke-width="1.2" fill="#7ccf9a" fill-opacity="0.5"/>
<text x="127" y="225" font-size="13" text-anchor="middle" fill="currentColor" font-family="monospace">{a,b}</text>
<rect x="213" y="143" width="60" height="26" rx="5" style="fill:var(--md-default-bg-color)"/>
<rect x="213" y="143" width="60" height="26" rx="5" stroke="currentColor" stroke-width="1.2" fill="#9cc9ea" fill-opacity="0.5"/>
<text x="243" y="161" font-size="13" text-anchor="middle" fill="currentColor" font-family="monospace">−b</text>
<rect x="174" y="207" width="60" height="26" rx="5" style="fill:var(--md-default-bg-color)"/>
<rect x="174" y="207" width="60" height="26" rx="5" stroke="currentColor" stroke-width="1.2" fill="#7ccf9a" fill-opacity="0.5"/>
<text x="204" y="225" font-size="13" text-anchor="middle" fill="currentColor" font-family="monospace">{a,c}</text>
<rect x="251" y="207" width="60" height="26" rx="5" style="fill:var(--md-default-bg-color)"/>
<rect x="251" y="207" width="60" height="26" rx="5" stroke="currentColor" stroke-width="1.2" fill="#7ccf9a" fill-opacity="0.5"/>
<text x="281" y="225" font-size="13" text-anchor="middle" fill="currentColor" font-family="monospace">{a}</text>
<rect x="444" y="79" width="60" height="26" rx="5" style="fill:var(--md-default-bg-color)"/>
<rect x="444" y="79" width="60" height="26" rx="5" stroke="currentColor" stroke-width="1.2" fill="#9cc9ea" fill-opacity="0.5"/>
<text x="474" y="97" font-size="13" text-anchor="middle" fill="currentColor" font-family="monospace">−a</text>
<rect x="367" y="143" width="60" height="26" rx="5" style="fill:var(--md-default-bg-color)"/>
<rect x="367" y="143" width="60" height="26" rx="5" stroke="currentColor" stroke-width="1.2" fill="#9cc9ea" fill-opacity="0.5"/>
<text x="397" y="161" font-size="13" text-anchor="middle" fill="currentColor" font-family="monospace">+b</text>
<rect x="329" y="207" width="60" height="26" rx="5" style="fill:var(--md-default-bg-color)"/>
<rect x="329" y="207" width="60" height="26" rx="5" stroke="currentColor" stroke-width="1.2" fill="#7ccf9a" fill-opacity="0.5"/>
<text x="359" y="225" font-size="13" text-anchor="middle" fill="currentColor" font-family="monospace">{b,c}</text>
<rect x="406" y="207" width="60" height="26" rx="5" style="fill:var(--md-default-bg-color)"/>
<rect x="406" y="207" width="60" height="26" rx="5" stroke="currentColor" stroke-width="1.2" fill="#7ccf9a" fill-opacity="0.5"/>
<text x="436" y="225" font-size="13" text-anchor="middle" fill="currentColor" font-family="monospace">{b}</text>
<rect x="521" y="143" width="60" height="26" rx="5" style="fill:var(--md-default-bg-color)"/>
<rect x="521" y="143" width="60" height="26" rx="5" stroke="currentColor" stroke-width="1.2" fill="#9cc9ea" fill-opacity="0.5"/>
<text x="551" y="161" font-size="13" text-anchor="middle" fill="currentColor" font-family="monospace">−b</text>
<rect x="483" y="207" width="60" height="26" rx="5" style="fill:var(--md-default-bg-color)"/>
<rect x="483" y="207" width="60" height="26" rx="5" stroke="currentColor" stroke-width="1.2" fill="#7ccf9a" fill-opacity="0.5"/>
<text x="513" y="225" font-size="13" text-anchor="middle" fill="currentColor" font-family="monospace">{c}</text>
<rect x="560" y="207" width="60" height="26" rx="5" style="fill:var(--md-default-bg-color)"/>
<rect x="560" y="207" width="60" height="26" rx="5" stroke="currentColor" stroke-width="1.2" fill="#7ccf9a" fill-opacity="0.5"/>
<text x="590" y="225" font-size="13" text-anchor="middle" fill="currentColor" font-family="monospace">{}</text>
<text x="320" y="261" font-size="13" text-anchor="middle" fill="currentColor">left branch takes the item (+), right branch leaves it (−): 8 leaves, 8 subsets</text>
</svg>
<figcaption>Figure 14.1. The state-space tree for choosing a subset of {a, b, c}. Each level decides one item. A depth-first walk visits the leaves from left to right: {a,b,c}, {a,b}, {a,c}, {a}, {b,c}, {b}, {c}, {}.</figcaption>
</figure>

### Backtracking: cut the tree early

Most of the tree is usually useless, and we can tell early. If we are placing queens and the second queen already
attacks the first, no way of placing the remaining queens can fix that: the whole subtree below can be skipped. That
is **backtracking**: a depth-first search of the state-space tree that, at every node, tests whether the partial
solution can still be extended to a valid one, and if not, **prunes** (skips) its subtree.

The general template is short:

```python
def backtrack(partial):
    if is_complete(partial):
        report(partial)
        return
    for choice in choices(partial):
        if is_promising(partial, choice):     # the pruning test
            make(partial, choice)
            backtrack(partial)
            undo(partial, choice)             # restore the state before trying the next choice
```

Three things decide how well it works:

- **What a node is**: which choices, in which order. A good formulation makes invalid partial solutions recognisable
  early.
- **The pruning test**: it must be **safe** (never cut a subtree that contains a solution we want) and should be
  **cheap**, since it runs at every node.
- **The order of choices**: trying likely choices first finds a solution sooner when one solution is enough.

**Correctness** of a backtracking algorithm has two halves. *Completeness:* without pruning, the walk visits every leaf,
because every leaf is reached by a unique sequence of choices and the loop tries every choice at every node; pruning
only removes subtrees with no wanted leaf, by the safety of the test. *Soundness:* everything reported passes the
completeness check. Together they say the algorithm reports exactly the wanted solutions.

**Running time** is (number of nodes visited) × (work per node). Pruning reduces the first factor, sometimes
spectacularly, but usually without a guarantee better than exponential: backtracking is not a way around NP-hardness
([Chapter 22](22-NP-Completeness.md)), only a way to make many real instances feasible.

## 14.2 Subsets, permutations, combinations

Three families of objects appear inside almost every search: subsets (which items?), permutations (in what order?) and
combinations (which $k$ of them?). Generating them is the simplest backtracking, with no pruning at all, and it is
worth writing once by hand. The reference pages [Subsets and permutations](../../backtracking/subsets-permutations.md)
animate them.

```python
--8<-- "books/algorithms/ch14_generate.py"
```

```
subsets of [a, b, c]: [['a', 'b', 'c'], ['a', 'b'], ['a', 'c'], ['a'], ['b', 'c'], ['b'], ['c'], []]
permutations of [1, 2, 3]: [[1, 2, 3], [1, 3, 2], [2, 1, 3], [2, 3, 1], [3, 1, 2], [3, 2, 1]]
combinations C(5, 3): [[1, 2, 3], [1, 2, 4], [1, 2, 5], [1, 3, 4], [1, 3, 5], [1, 4, 5], [2, 3, 4], [2, 3, 5], [2, 4, 5], [3, 4, 5]]
counts: 2^10 = 1024  6! = 720  C(20, 4) = 4845
subset sum 53, pruning False: 58 solutions, 28133 nodes visited
subset sum 53, pruning True : 58 solutions, 1065 nodes visited
one solution: [32, 16, 5]
```

### Subsets

At depth $i$ decide whether item $i$ is in. The recursion `go(i)` takes item $i$, recurses, removes it (the **undo**
step), and recurses again without it. The tree is the complete binary tree of Figure 14.1: $2^n$ leaves and
$2^{n+1} - 1$ nodes in all, so generating all subsets costs $O(2^n \cdot n)$ if each subset is copied out. The undo step
is what makes backtracking cheap in memory: there is one list `chosen`, modified and restored, instead of a new list
for every node.

### Permutations

At depth $k$ choose which unused item goes in position $k$. A boolean array `used` records which items are taken. The
root has $n$ children, each of those $n - 1$, and so on: the tree has $n!$ leaves and
$\sum_{k=0}^{n} n!/(n-k)! \le e \cdot n!$ nodes. (The bound comes from $\sum_k 1/(n-k)! \le \sum_j 1/j! = e$.)

### Combinations and the first pruning

For the $k$-element subsets of $\{1, \dots, n\}$, choose elements in increasing order, so each subset is produced once.
A simple pruning: if we still need `need` more elements, the next one cannot be larger than $n - \text{need} + 1$,
or there would not be enough numbers left. The loop bound `range(start, n - need + 2)` builds that test in, and
every leaf the search reaches is a valid combination: the number of leaves is exactly $\binom{n}{k}$, and no time is
wasted on dead branches.

Python's `itertools` module has `combinations`, `permutations` and `product`, written in C; use them in practice. The
hand-written versions matter when you need to prune *inside* the generation, which `itertools` cannot do.

### Pruning on a real problem: subset sum

**Subset sum** asks: given positive integers and a target $T$, which subsets add up to exactly $T$? Two safe tests
cut the tree:

- if the running total already exceeds $T$, adding more positive numbers cannot help;
- if the running total plus **all** the numbers not yet decided is still below $T$, no choice can reach it.

Sorting the numbers in decreasing order makes the first test bite early. On the program's 14 numbers with target 53,
the unpruned search visits 28 133 nodes and the pruned one 1065, with the same 58 solutions. The second test needs
the sums of the remaining numbers, which the program precomputes as **suffix sums** in $O(n)$.

## 14.3 N-Queens, Sudoku with constraint propagation

### N-Queens

Place $n$ queens on an $n \times n$ chessboard so that no two attack each other: no two in the same row, the same
column or the same diagonal. The puzzle for $n = 8$ was posed in a German chess magazine in 1848, and Gauss
corresponded about it; Franz Nauck published all 92 solutions in 1850. Edsger Dijkstra used it in 1972 as a worked
example of structured programming by backtracking.

**The formulation matters.** Placing 8 queens anywhere on 64 squares gives $\binom{64}{8} \approx 4.4 \times 10^9$
candidates. But two queens in one row attack each other, so each row holds exactly one queen: a candidate is just a list
of 8 column numbers, $8^8 \approx 1.7 \times 10^7$. Columns must also differ, so it is a permutation: $8! = 40\,320$.
Choosing the representation removed most of the search before we started.

**The pruning test.** Place queens row by row. A new queen in row $r$, column $c$ is safe if no earlier queen is in
column $c$ or on either diagonal through $(r, c)$. Squares on one "down-right" diagonal share $r - c$; squares on one
"up-right" diagonal share $r + c$. Keeping three sets (occupied columns, occupied $r - c$ values, occupied $r + c$ values)
makes the test $O(1)$.

<figure class="mars-fig" markdown="0">
<svg viewBox="0 0 640 326" role="img" aria-label="An 8 by 8 chessboard with eight queens, one per row, in columns 1, 5, 8, 6, 3, 7, 2 and 4 from the top row down.">
<rect x="176" y="14" width="34" height="34" fill="none"/>
<rect x="210" y="14" width="34" height="34" fill="#9cc9ea" fill-opacity="0.45"/>
<rect x="244" y="14" width="34" height="34" fill="none"/>
<rect x="278" y="14" width="34" height="34" fill="#9cc9ea" fill-opacity="0.45"/>
<rect x="312" y="14" width="34" height="34" fill="none"/>
<rect x="346" y="14" width="34" height="34" fill="#9cc9ea" fill-opacity="0.45"/>
<rect x="380" y="14" width="34" height="34" fill="none"/>
<rect x="414" y="14" width="34" height="34" fill="#9cc9ea" fill-opacity="0.45"/>
<rect x="176" y="48" width="34" height="34" fill="#9cc9ea" fill-opacity="0.45"/>
<rect x="210" y="48" width="34" height="34" fill="none"/>
<rect x="244" y="48" width="34" height="34" fill="#9cc9ea" fill-opacity="0.45"/>
<rect x="278" y="48" width="34" height="34" fill="none"/>
<rect x="312" y="48" width="34" height="34" fill="#9cc9ea" fill-opacity="0.45"/>
<rect x="346" y="48" width="34" height="34" fill="none"/>
<rect x="380" y="48" width="34" height="34" fill="#9cc9ea" fill-opacity="0.45"/>
<rect x="414" y="48" width="34" height="34" fill="none"/>
<rect x="176" y="82" width="34" height="34" fill="none"/>
<rect x="210" y="82" width="34" height="34" fill="#9cc9ea" fill-opacity="0.45"/>
<rect x="244" y="82" width="34" height="34" fill="none"/>
<rect x="278" y="82" width="34" height="34" fill="#9cc9ea" fill-opacity="0.45"/>
<rect x="312" y="82" width="34" height="34" fill="none"/>
<rect x="346" y="82" width="34" height="34" fill="#9cc9ea" fill-opacity="0.45"/>
<rect x="380" y="82" width="34" height="34" fill="none"/>
<rect x="414" y="82" width="34" height="34" fill="#9cc9ea" fill-opacity="0.45"/>
<rect x="176" y="116" width="34" height="34" fill="#9cc9ea" fill-opacity="0.45"/>
<rect x="210" y="116" width="34" height="34" fill="none"/>
<rect x="244" y="116" width="34" height="34" fill="#9cc9ea" fill-opacity="0.45"/>
<rect x="278" y="116" width="34" height="34" fill="none"/>
<rect x="312" y="116" width="34" height="34" fill="#9cc9ea" fill-opacity="0.45"/>
<rect x="346" y="116" width="34" height="34" fill="none"/>
<rect x="380" y="116" width="34" height="34" fill="#9cc9ea" fill-opacity="0.45"/>
<rect x="414" y="116" width="34" height="34" fill="none"/>
<rect x="176" y="150" width="34" height="34" fill="none"/>
<rect x="210" y="150" width="34" height="34" fill="#9cc9ea" fill-opacity="0.45"/>
<rect x="244" y="150" width="34" height="34" fill="none"/>
<rect x="278" y="150" width="34" height="34" fill="#9cc9ea" fill-opacity="0.45"/>
<rect x="312" y="150" width="34" height="34" fill="none"/>
<rect x="346" y="150" width="34" height="34" fill="#9cc9ea" fill-opacity="0.45"/>
<rect x="380" y="150" width="34" height="34" fill="none"/>
<rect x="414" y="150" width="34" height="34" fill="#9cc9ea" fill-opacity="0.45"/>
<rect x="176" y="184" width="34" height="34" fill="#9cc9ea" fill-opacity="0.45"/>
<rect x="210" y="184" width="34" height="34" fill="none"/>
<rect x="244" y="184" width="34" height="34" fill="#9cc9ea" fill-opacity="0.45"/>
<rect x="278" y="184" width="34" height="34" fill="none"/>
<rect x="312" y="184" width="34" height="34" fill="#9cc9ea" fill-opacity="0.45"/>
<rect x="346" y="184" width="34" height="34" fill="none"/>
<rect x="380" y="184" width="34" height="34" fill="#9cc9ea" fill-opacity="0.45"/>
<rect x="414" y="184" width="34" height="34" fill="none"/>
<rect x="176" y="218" width="34" height="34" fill="none"/>
<rect x="210" y="218" width="34" height="34" fill="#9cc9ea" fill-opacity="0.45"/>
<rect x="244" y="218" width="34" height="34" fill="none"/>
<rect x="278" y="218" width="34" height="34" fill="#9cc9ea" fill-opacity="0.45"/>
<rect x="312" y="218" width="34" height="34" fill="none"/>
<rect x="346" y="218" width="34" height="34" fill="#9cc9ea" fill-opacity="0.45"/>
<rect x="380" y="218" width="34" height="34" fill="none"/>
<rect x="414" y="218" width="34" height="34" fill="#9cc9ea" fill-opacity="0.45"/>
<rect x="176" y="252" width="34" height="34" fill="#9cc9ea" fill-opacity="0.45"/>
<rect x="210" y="252" width="34" height="34" fill="none"/>
<rect x="244" y="252" width="34" height="34" fill="#9cc9ea" fill-opacity="0.45"/>
<rect x="278" y="252" width="34" height="34" fill="none"/>
<rect x="312" y="252" width="34" height="34" fill="#9cc9ea" fill-opacity="0.45"/>
<rect x="346" y="252" width="34" height="34" fill="none"/>
<rect x="380" y="252" width="34" height="34" fill="#9cc9ea" fill-opacity="0.45"/>
<rect x="414" y="252" width="34" height="34" fill="none"/>
<rect x="176" y="14" width="272" height="272" fill="none" stroke="currentColor" stroke-width="1.5"/>
<circle cx="193" cy="31" r="12" fill="#eea66f" stroke="currentColor" stroke-width="1.2"/>
<text x="193" y="36" font-size="13" text-anchor="middle" fill="currentColor" font-weight="bold">Q</text>
<circle cx="329" cy="65" r="12" fill="#eea66f" stroke="currentColor" stroke-width="1.2"/>
<text x="329" y="70" font-size="13" text-anchor="middle" fill="currentColor" font-weight="bold">Q</text>
<circle cx="431" cy="99" r="12" fill="#eea66f" stroke="currentColor" stroke-width="1.2"/>
<text x="431" y="104" font-size="13" text-anchor="middle" fill="currentColor" font-weight="bold">Q</text>
<circle cx="363" cy="133" r="12" fill="#eea66f" stroke="currentColor" stroke-width="1.2"/>
<text x="363" y="138" font-size="13" text-anchor="middle" fill="currentColor" font-weight="bold">Q</text>
<circle cx="261" cy="167" r="12" fill="#eea66f" stroke="currentColor" stroke-width="1.2"/>
<text x="261" y="172" font-size="13" text-anchor="middle" fill="currentColor" font-weight="bold">Q</text>
<circle cx="397" cy="201" r="12" fill="#eea66f" stroke="currentColor" stroke-width="1.2"/>
<text x="397" y="206" font-size="13" text-anchor="middle" fill="currentColor" font-weight="bold">Q</text>
<circle cx="227" cy="235" r="12" fill="#eea66f" stroke="currentColor" stroke-width="1.2"/>
<text x="227" y="240" font-size="13" text-anchor="middle" fill="currentColor" font-weight="bold">Q</text>
<circle cx="295" cy="269" r="12" fill="#eea66f" stroke="currentColor" stroke-width="1.2"/>
<text x="295" y="274" font-size="13" text-anchor="middle" fill="currentColor" font-weight="bold">Q</text>
<text x="166" y="36" font-size="12" text-anchor="end" fill="currentColor">row 1</text>
<text x="166" y="70" font-size="12" text-anchor="end" fill="currentColor">row 2</text>
<text x="166" y="104" font-size="12" text-anchor="end" fill="currentColor">row 3</text>
<text x="166" y="138" font-size="12" text-anchor="end" fill="currentColor">row 4</text>
<text x="166" y="172" font-size="12" text-anchor="end" fill="currentColor">row 5</text>
<text x="166" y="206" font-size="12" text-anchor="end" fill="currentColor">row 6</text>
<text x="166" y="240" font-size="12" text-anchor="end" fill="currentColor">row 7</text>
<text x="166" y="274" font-size="12" text-anchor="end" fill="currentColor">row 8</text>
<text x="193" y="302" font-size="12" text-anchor="middle" fill="currentColor">1</text>
<text x="227" y="302" font-size="12" text-anchor="middle" fill="currentColor">2</text>
<text x="261" y="302" font-size="12" text-anchor="middle" fill="currentColor">3</text>
<text x="295" y="302" font-size="12" text-anchor="middle" fill="currentColor">4</text>
<text x="329" y="302" font-size="12" text-anchor="middle" fill="currentColor">5</text>
<text x="363" y="302" font-size="12" text-anchor="middle" fill="currentColor">6</text>
<text x="397" y="302" font-size="12" text-anchor="middle" fill="currentColor">7</text>
<text x="431" y="302" font-size="12" text-anchor="middle" fill="currentColor">8</text>
<text x="320" y="320" font-size="13" text-anchor="middle" fill="currentColor">columns 1 5 8 6 3 7 2 4: no two queens share a row, column or diagonal</text>
</svg>
<figcaption>Figure 14.2. The first solution of 8-queens found by row-by-row backtracking, trying columns from left to right: the queens stand in columns 1, 5, 8, 6, 3, 7, 2, 4 of rows 1 to 8.</figcaption>
</figure>

**A trace for $n = 4$.** Columns numbered 1 to 4. A node lists the columns chosen so far.

| step | partial placement | event |
|---|---|---|
| 1 | 1 | row 1, column 1 |
| 2 | 1 3 | row 2: columns 1, 2 attacked; 3 is safe |
| 3 | 1 3 ? | row 3: every column attacked; backtrack |
| 4 | 1 4 | row 2, column 4 |
| 5 | 1 4 2 | row 3, column 2 |
| 6 | 1 4 2 ? | row 4: every column attacked; backtrack twice |
| 7 | 2 | row 1, column 2 |
| 8 | 2 4 | row 2: only column 4 is safe |
| 9 | 2 4 1 | row 3: column 1 |
| 10 | 2 4 1 3 | row 4: column 3; **solution** |
| 11 | 3, 3 1, 3 1 4, 3 1 4 2 | the mirror image; **solution** |
| 12 | 4, 4 1, 4 1 3, 4 2 | dead ends |

<figure class="mars-fig" markdown="0">
<svg viewBox="0 0 640 335" role="img" aria-label="The 4-queens backtracking tree with 17 nodes. From start, the first queen goes in column 1, 2, 3 or 4. Under 1: 1 3 is a dead end, 1 4 leads to the dead end 1 4 2. Under 2: 2 4, 2 4 1 and the solution 2 4 1 3. Under 3: 3 1, 3 1 4 and the solution 3 1 4 2. Under 4: 4 1 leads to the dead end 4 1 3, and 4 2 is a dead end.">
<g stroke="currentColor" stroke-width="1.2">
<line x1="320" y1="41" x2="104" y2="79"/>
<line x1="320" y1="41" x2="266" y2="79"/>
<line x1="320" y1="41" x2="374" y2="79"/>
<line x1="320" y1="41" x2="536" y2="79"/>
<line x1="104" y1="105" x2="50" y2="143"/>
<line x1="104" y1="105" x2="158" y2="143"/>
<line x1="158" y1="169" x2="158" y2="207"/>
<line x1="266" y1="105" x2="266" y2="143"/>
<line x1="266" y1="169" x2="266" y2="207"/>
<line x1="266" y1="233" x2="266" y2="271"/>
<line x1="374" y1="105" x2="374" y2="143"/>
<line x1="374" y1="169" x2="374" y2="207"/>
<line x1="374" y1="233" x2="374" y2="271"/>
<line x1="536" y1="105" x2="482" y2="143"/>
<line x1="536" y1="105" x2="590" y2="143"/>
<line x1="482" y1="169" x2="482" y2="207"/>
</g>
<rect x="288" y="15" width="64" height="26" rx="5" style="fill:var(--md-default-bg-color)"/>
<rect x="288" y="15" width="64" height="26" rx="5" stroke="currentColor" stroke-width="1.2" fill="#9cc9ea" fill-opacity="0.5"/>
<text x="320" y="33" font-size="13" text-anchor="middle" fill="currentColor" font-family="monospace">start</text>
<rect x="72" y="79" width="64" height="26" rx="5" style="fill:var(--md-default-bg-color)"/>
<rect x="72" y="79" width="64" height="26" rx="5" stroke="currentColor" stroke-width="1.2" fill="#9cc9ea" fill-opacity="0.5"/>
<text x="104" y="97" font-size="13" text-anchor="middle" fill="currentColor" font-family="monospace">1</text>
<rect x="18" y="143" width="64" height="26" rx="5" style="fill:var(--md-default-bg-color)"/>
<rect x="18" y="143" width="64" height="26" rx="5" stroke="currentColor" stroke-width="1.2" fill="#eea66f" fill-opacity="0.5"/>
<text x="50" y="161" font-size="13" text-anchor="middle" fill="currentColor" font-family="monospace">1 3</text>
<rect x="126" y="143" width="64" height="26" rx="5" style="fill:var(--md-default-bg-color)"/>
<rect x="126" y="143" width="64" height="26" rx="5" stroke="currentColor" stroke-width="1.2" fill="#9cc9ea" fill-opacity="0.5"/>
<text x="158" y="161" font-size="13" text-anchor="middle" fill="currentColor" font-family="monospace">1 4</text>
<rect x="126" y="207" width="64" height="26" rx="5" style="fill:var(--md-default-bg-color)"/>
<rect x="126" y="207" width="64" height="26" rx="5" stroke="currentColor" stroke-width="1.2" fill="#eea66f" fill-opacity="0.5"/>
<text x="158" y="225" font-size="13" text-anchor="middle" fill="currentColor" font-family="monospace">1 4 2</text>
<rect x="234" y="79" width="64" height="26" rx="5" style="fill:var(--md-default-bg-color)"/>
<rect x="234" y="79" width="64" height="26" rx="5" stroke="currentColor" stroke-width="1.2" fill="#9cc9ea" fill-opacity="0.5"/>
<text x="266" y="97" font-size="13" text-anchor="middle" fill="currentColor" font-family="monospace">2</text>
<rect x="234" y="143" width="64" height="26" rx="5" style="fill:var(--md-default-bg-color)"/>
<rect x="234" y="143" width="64" height="26" rx="5" stroke="currentColor" stroke-width="1.2" fill="#9cc9ea" fill-opacity="0.5"/>
<text x="266" y="161" font-size="13" text-anchor="middle" fill="currentColor" font-family="monospace">2 4</text>
<rect x="234" y="207" width="64" height="26" rx="5" style="fill:var(--md-default-bg-color)"/>
<rect x="234" y="207" width="64" height="26" rx="5" stroke="currentColor" stroke-width="1.2" fill="#9cc9ea" fill-opacity="0.5"/>
<text x="266" y="225" font-size="13" text-anchor="middle" fill="currentColor" font-family="monospace">2 4 1</text>
<rect x="234" y="271" width="64" height="26" rx="5" style="fill:var(--md-default-bg-color)"/>
<rect x="234" y="271" width="64" height="26" rx="5" stroke="currentColor" stroke-width="1.2" fill="#7ccf9a" fill-opacity="0.5"/>
<text x="266" y="289" font-size="13" text-anchor="middle" fill="currentColor" font-family="monospace">2 4 1 3</text>
<rect x="342" y="79" width="64" height="26" rx="5" style="fill:var(--md-default-bg-color)"/>
<rect x="342" y="79" width="64" height="26" rx="5" stroke="currentColor" stroke-width="1.2" fill="#9cc9ea" fill-opacity="0.5"/>
<text x="374" y="97" font-size="13" text-anchor="middle" fill="currentColor" font-family="monospace">3</text>
<rect x="342" y="143" width="64" height="26" rx="5" style="fill:var(--md-default-bg-color)"/>
<rect x="342" y="143" width="64" height="26" rx="5" stroke="currentColor" stroke-width="1.2" fill="#9cc9ea" fill-opacity="0.5"/>
<text x="374" y="161" font-size="13" text-anchor="middle" fill="currentColor" font-family="monospace">3 1</text>
<rect x="342" y="207" width="64" height="26" rx="5" style="fill:var(--md-default-bg-color)"/>
<rect x="342" y="207" width="64" height="26" rx="5" stroke="currentColor" stroke-width="1.2" fill="#9cc9ea" fill-opacity="0.5"/>
<text x="374" y="225" font-size="13" text-anchor="middle" fill="currentColor" font-family="monospace">3 1 4</text>
<rect x="342" y="271" width="64" height="26" rx="5" style="fill:var(--md-default-bg-color)"/>
<rect x="342" y="271" width="64" height="26" rx="5" stroke="currentColor" stroke-width="1.2" fill="#7ccf9a" fill-opacity="0.5"/>
<text x="374" y="289" font-size="13" text-anchor="middle" fill="currentColor" font-family="monospace">3 1 4 2</text>
<rect x="504" y="79" width="64" height="26" rx="5" style="fill:var(--md-default-bg-color)"/>
<rect x="504" y="79" width="64" height="26" rx="5" stroke="currentColor" stroke-width="1.2" fill="#9cc9ea" fill-opacity="0.5"/>
<text x="536" y="97" font-size="13" text-anchor="middle" fill="currentColor" font-family="monospace">4</text>
<rect x="450" y="143" width="64" height="26" rx="5" style="fill:var(--md-default-bg-color)"/>
<rect x="450" y="143" width="64" height="26" rx="5" stroke="currentColor" stroke-width="1.2" fill="#9cc9ea" fill-opacity="0.5"/>
<text x="482" y="161" font-size="13" text-anchor="middle" fill="currentColor" font-family="monospace">4 1</text>
<rect x="450" y="207" width="64" height="26" rx="5" style="fill:var(--md-default-bg-color)"/>
<rect x="450" y="207" width="64" height="26" rx="5" stroke="currentColor" stroke-width="1.2" fill="#eea66f" fill-opacity="0.5"/>
<text x="482" y="225" font-size="13" text-anchor="middle" fill="currentColor" font-family="monospace">4 1 3</text>
<rect x="558" y="143" width="64" height="26" rx="5" style="fill:var(--md-default-bg-color)"/>
<rect x="558" y="143" width="64" height="26" rx="5" stroke="currentColor" stroke-width="1.2" fill="#eea66f" fill-opacity="0.5"/>
<text x="590" y="161" font-size="13" text-anchor="middle" fill="currentColor" font-family="monospace">4 2</text>
<text x="320" y="325" font-size="13" text-anchor="middle" fill="currentColor">columns of the queens in rows 1, 2, ...; orange: dead end, green: solution</text>
</svg>
<figcaption>Figure 14.3. The whole backtracking tree for 4-queens: 17 nodes, against 341 nodes in the full tree of all 4^0 + 4^1 + ... + 4^4 placements with one queen per row. Each dead end (orange) cuts off a subtree; the two green leaves are the solutions.</figcaption>
</figure>

```python
--8<-- "books/algorithms/ch14_queens_sudoku.py"
```

```
 n  solutions  search nodes   bitmask count
 1          1             2               1
 2          0             3               0
 3          0             6               0
 4          2            17               2
 5         10            54              10
 6          4           153               4
 7         40           552              40
 8         92          2057              92
 9        352          8394             352
10        724         35539             724
first 8-queens solution (column of the queen in each row): [0, 4, 7, 5, 2, 6, 1, 3]
puzzle 1, plain backtracking: 4209 search nodes, valid solution: True
puzzle 1, propagation + fewest options: 1 search nodes, valid solution: True
5 3 4 6 7 8 9 1 2
6 7 2 1 9 5 3 4 8
1 9 8 3 4 2 5 6 7
8 5 9 7 6 1 4 2 3
4 2 6 8 5 3 7 9 1
7 1 3 9 2 4 8 5 6
9 6 1 5 3 7 2 8 4
2 8 7 4 1 9 6 3 5
3 4 5 2 8 6 1 7 9
puzzle 2, plain backtracking: gave up after 1000000 search nodes
puzzle 2, propagation + fewest options: 16 search nodes, valid solution: True
```

The table shows the counts: 92 solutions for $n = 8$, found in 2057 nodes instead of the 40 320 leaves of the
permutation tree. The number of solutions is known exactly only up to $n = 27$ (computed in 2016 by a large
distributed search); no formula is known.

The **bitmask** version keeps the three constraint sets as integers: bit $c$ of `cols` says column $c$ is taken, and
the diagonal masks shift by one position per row, because a diagonal moves one column per row. The free squares of the
current row are `full & ~(cols | d1 | d2)`, and `free & -free` isolates the lowest one (two's-complement arithmetic;
compare the lowbit of Fenwick trees in [Chapter 10](10-Union-Find-and-Range-Queries.md)). It explores the same tree, but
each node costs a few machine operations. Reference page: [N-Queens](../../backtracking/n-queens.md).

### Sudoku: propagate before you search

A Sudoku grid has 81 cells in 9 rows, 9 columns and 9 boxes of $3 \times 3$ (together, 27 **units**). Fill the empty
cells with digits 1 to 9 so that every unit contains each digit once. The **peers** of a cell are the 20 other cells
sharing a unit with it.

**Plain backtracking** fills the empty cells in reading order, trying each digit not already used by a peer. On the
program's first puzzle (the example in Wikipedia's article on Sudoku, 30 givens) it needs 4209 nodes; on the second, a
sparse puzzle with 17 givens (the fewest possible for a unique solution, as Gary McGuire, Bastian Tugemann and Gilles
Civario proved by an exhaustive computer search published in 2014), it gives up after a million nodes.

**Constraint propagation** keeps, for every cell, the set of digits still possible (its **candidates**), and applies
two rules whenever a candidate is removed:

1. if a cell has only one candidate left, remove that digit from all its peers;
2. if a digit has only one possible place left in some unit, put it there.

Each rule may trigger the other, in a cascade. If any cell runs out of candidates, or any digit runs out of places, the
current state is a contradiction. Propagation alone solves the first puzzle without any search (1 node). When it gets
stuck, **search** with a good order: pick the cell with the **fewest candidates** (the **minimum remaining values**
heuristic), try each candidate on a copy of the state, and propagate again. The second puzzle then needs 16 nodes.

Why does "fewest options first" help so much? A cell with 2 candidates splits the search into 2 branches; one with 9
candidates splits it into 9. Choosing the narrowest branching point first keeps the tree thin near the root, where every
extra branch multiplies all the work below it. And a cell with 1 candidate is free: it is a forced move.

These two ideas, propagate constraints and branch on the most constrained variable, are the heart of **constraint
programming** and of modern SAT solvers ([Chapter 23](23-Approximation-and-Parameterized-Algorithms.md)), where
propagation is called **unit propagation**. Sudoku is also an **exact cover** problem, for which Donald Knuth's
"Dancing Links" (2000) gives an elegant backtracking data structure.

## 14.4 Pruning: bounding functions; branch and bound

Backtracking prunes nodes that cannot lead to *any* valid solution. In an **optimisation** problem almost every node
can lead to some valid solution; the question is whether it can lead to a **better** one than the best found so far.

### The idea

**Branch and bound** keeps:

- the **incumbent**: the best complete solution found so far, with its value;
- a **bounding function**: for each node, an **optimistic bound**, a value that no solution in its subtree can beat.
  For a maximisation problem it is an upper bound; for minimisation, a lower bound.

At each node, if the optimistic bound is no better than the incumbent, prune the subtree: nothing in it can improve on
what we have. The bound must be **valid** (truly optimistic) for the pruning to be safe, and **tight** (close to the
truth) for it to prune much. Usually it comes from a **relaxation**: the same problem with some constraint dropped, so
it is easier to solve and its optimum can only be better.

There are two common orders of exploration:

- **depth first**: little memory, and it reaches complete solutions (and so a good incumbent) quickly;
- **best first**: always expand the node with the most promising bound, from a priority queue. It expands the fewest
  nodes among strategies using the same bound, but it may need a lot of memory.

The method was introduced by Ailsa Land and Alison Doig in 1960 for integer linear programming, and named "branch and
bound" in 1963 by Little, Murty, Sweeney and Karel in a paper on the travelling salesman problem.

### 0/1 knapsack

The **relaxation** of the 0/1 knapsack is the fractional knapsack ([Chapter 12](12-Greedy-Algorithms.md)): allow
fractions of items. It is solved greedily, by density, and its value is at least the 0/1 optimum, because every 0/1
solution is also a fractional one. So the bound at a node is: the value already taken, plus the fractional knapsack's
value on the remaining items and the remaining capacity.

A small example by hand, capacity 16, items sorted by density:

| item | weight | value | density |
|---|---|---|---|
| 1 | 2 | 40 | 20 |
| 2 | 5 | 30 | 6 |
| 3 | 10 | 50 | 5 |
| 4 | 5 | 10 | 2 |

Depth-first, trying "take" before "leave":

| node (+ take, − leave) | weight | value | bound | incumbent after | action |
|---|---|---|---|---|---|
| root | 0 | 0 | 40 + 30 + 9/10 of 50 = 115 | 0 | branch |
| +1 | 2 | 40 | 115 | 40 | branch |
| +1 +2 | 7 | 70 | 115 | 70 | item 3 does not fit; leave it |
| +1 +2 −3 | 7 | 70 | 70 + 10 = 80 | 70 | branch |
| +1 +2 −3 +4 | 12 | 80 | 80 | 80 | leaf |
| +1 +2 −3 −4 | 7 | 70 | 70 | 80 | leaf |
| +1 −2 | 2 | 40 | 40 + 50 + 4/5 of 10 = 98 | 80 | branch |
| +1 −2 +3 | 12 | 90 | 98 | 90 | item 4 does not fit; leave it |
| +1 −2 +3 −4 | 12 | 90 | 90 | 90 | leaf |
| +1 −2 −3 | 2 | 40 | 40 + 10 = 50 | 90 | **prune** (50 ≤ 90) |
| −1 | 0 | 0 | 30 + 50 + 1/5 of 10 = 82 | 90 | **prune** (82 ≤ 90) |

Eleven nodes instead of the 31 of the full tree, and the answer is 90 (items 1 and 3). The pruning of "−1" is typical:
a large subtree, half the tree, discarded by one cheap calculation.

```python
--8<-- "books/algorithms/ch14_branch_bound.py"
```

```
knapsack, 30 items, capacity 529: branch and bound 1138 in 76 nodes; DP says 1138; the full tree has 2147483647 nodes
  18 items, bounding False: value 664, 310311 nodes
  18 items, bounding True : value 664, 29 nodes
TSP 8 cities: branch and bound 183 via (0, 5, 7, 4, 6, 1, 3, 2, 0), 137 nodes expanded; brute force 183 over 5040 tours
TSP 10 cities: branch and bound 225 via (0, 2, 4, 9, 1, 5, 3, 7, 6, 8, 0), 1701 nodes expanded; brute force 225 over 362880 tours
```

On 18 random items, the search without bounding visits 310 311 nodes and with bounding 29; on 30 items, 76 nodes out
of a tree of over two billion, and the answer matches the dynamic program of [Chapter 13](13-Dynamic-Programming.md).
Such dramatic numbers are typical of random knapsack instances, whose fractional bound is very tight, but not
guaranteed: there are instances on which branch and bound with this bound explores exponentially many nodes. Real
integer-programming solvers combine branch and bound with linear-programming relaxations and **cutting planes**
("branch and cut").

### Travelling salesman

For the TSP (minimise the length of a tour visiting every city once and returning), a node is a partial path from
city 0. Its lower bound must not exceed the length of any completion. The program uses a simple one:

$$
\text{bound} = \text{length so far} + \sum_{c \text{ still to leave}} \min_{t \text{ allowed}} d(c, t),
$$

where the cities "still to leave" are the current endpoint and every unvisited city, and the allowed targets of $c$
are the unvisited cities other than $c$, or city 0 at the very end.

*Why it is valid:* any completion of the path leaves each of those cities exactly once, along some edge to an allowed
target, and each such edge is at least the cheapest allowed edge from that city. Summing gives a lower bound. $\square$

The program runs best first: a priority queue keyed by the bound, so the most promising partial tour is extended
first, and any node whose bound is not below the incumbent is discarded. For 10 random cities it expands 1701 nodes
instead of checking 362 880 tours. Much stronger bounds exist: the **1-tree bound** of Held and Karp (1970, 1971), a
minimum spanning tree plus two edges at one city, adjusted with Lagrange multipliers, and the linear-programming
relaxations used by the Concorde solver, which has solved instances with tens of thousands of cities to proven
optimality. Branch and bound with a good bound beats the $O(2^n n^2)$ Held-Karp DP of
[Chapter 13](13-Dynamic-Programming.md) on most real instances, though not in the worst case.

## 14.5 Meet in the middle

Subset sum again: $n$ numbers, is there a subset adding to $T$? The numbers are now large (say, up to $10^{10}$), so the
$O(nT)$ dynamic program is useless, and backtracking's pruning is weak when the numbers are similar in size. Plain
enumeration costs $2^n$. Can we do better than $2^n$?

Yes, by a simple and surprisingly general trick. **Split the numbers into two halves** $A$ and $B$ of $n/2$ each. Any
subset is a subset of $A$ plus a subset of $B$, so the question becomes: is there a sum $s$ of a subset of $A$ and a sum
$s'$ of a subset of $B$ with $s + s' = T$?

1. List all $2^{n/2}$ subset sums of $A$, and all $2^{n/2}$ subset sums of $B$.
2. Sort the list for $B$.
3. For each sum $s$ from $A$, binary search the sorted list for $T - s$.

**A hand example.** Numbers $3, 34, 4, 12, 5, 2$ and target 9. $A = \{3, 34, 4\}$ has sums
$0, 3, 34, 37, 4, 7, 38, 41$; $B = \{12, 5, 2\}$ has sums, sorted, $0, 2, 5, 7, 12, 14, 17, 19$. For $s = 0$ we need 9,
not there; $s = 3$ needs 6, no; $s = 34$ needs $-25$, no; $s = 37$ needs $-28$, no; $s = 4$ needs 5: **found**, $4 + 5 = 9$.

**Theorem.** Meet in the middle decides subset sum in $O(2^{n/2} \cdot n)$ time and $O(2^{n/2})$ space.

*Proof.* Correctness: the subsets of the whole set correspond exactly to the pairs (subset of $A$, subset of $B$), with
sums adding, so a subset with sum $T$ exists exactly when some $s$ from $A$ has $T - s$ in $B$'s list. Time: the two
lists have $2^{n/2}$ entries each and are built by doubling (each number doubles the list); sorting takes
$O(2^{n/2} \log 2^{n/2}) = O(2^{n/2} \cdot n)$; the $2^{n/2}$ binary searches cost the same. $\square$

```python
--8<-- "books/algorithms/ch14_meet_middle.py"
```

```
22 numbers, target 52397555
enumerate all 2^22 sums: True  sums built: 4194304
meet in the middle:      True  sums built: 4096

40 numbers, capacity 68182460971: best subset sum 68182460971, gap 0
two lists of 2^20 = 1048576 sums instead of 2^40 = 1099511627776 subsets
checks against full enumeration (closest sum, 50 random yes/no instances): True
```

$2^{n/2} = (\sqrt 2)^n \approx 1.414^n$, so the exponent is halved: 40 numbers need about two million list entries
instead of a trillion subsets. The same program also solves the optimisation version (the largest subset sum not
exceeding a capacity, which is a knapsack whose values equal its weights) by searching for the largest $s'$ at most
$T - s$.

The price is memory: $2^{n/2}$ sums must be stored. Richard Schroeppel and Adi Shamir showed in 1981 how to keep the
time at about $2^{n/2}$ while using only about $2^{n/4}$ space, by generating the sums of each half in sorted order on
the fly from quarters. Ellis Horowitz and Sartaj Sahni had introduced the two-list method for knapsack in 1974.

Meet in the middle works whenever a solution splits into two independent halves that must "agree" on a value that
can be looked up: bidirectional search in graphs ([Chapter 16](16-Shortest-Paths.md)) meets in the middle of a path, and
in cryptography it is why encrypting twice with two keys does not double the key length (the attack on double DES;
see [https://cryptography.akadian.ca/book/](https://cryptography.akadian.ca/book/)).

## 14.6 Exact exponential algorithms; measuring search trees

*Level: advanced.*

For an NP-hard problem we do not expect a polynomial algorithm ([Chapter 22](22-NP-Completeness.md)). But exponential is
not all the same: $2^n$ and $1.2^n$ are both exponential, yet at $n = 100$ the first is about $10^{30}$ and the second
about $8 \times 10^7$. The field of **exact exponential algorithms** asks: what is the smallest base $c$ for which a
problem can be solved in $O^*(c^n)$ time? (The notation $O^*$ hides polynomial factors.)

### Branching algorithms and branching vectors

Take **maximum independent set**: the largest set of vertices in a graph, no two adjacent. Brute force tries $2^n$
subsets. A **branching algorithm** instead picks a vertex $v$ and branches on two cases:

- $v$ is **not** in the set: recurse on the graph without $v$ (one vertex fewer);
- $v$ **is** in the set: then none of its neighbours is, so recurse on the graph without $v$ and its neighbours
  ($1 + \deg v$ vertices fewer).

Add simple **reduction rules** that need no branching:

- if $v$ has degree 0 or 1, some maximum independent set contains $v$ (if a maximum set contains $v$'s neighbour $u$
  instead, swap $u$ for $v$), so take $v$ and delete it and its neighbour;
- if every vertex has degree exactly 2, the graph is a union of cycles, and a cycle of length $L$ has a maximum
  independent set of size $\lfloor L/2 \rfloor$.

So we branch only on a vertex of degree at least 3. If $T(n)$ bounds the number of leaves of the search tree for graphs
with $n$ vertices, then

$$
T(n) \le T(n - 1) + T(n - 4).
$$

The pair $(1, 4)$, the amounts by which the branches shrink the problem, is the **branching vector**.

**Lemma.** If $T(n) \le \sum_{i=1}^{k} T(n - d_i)$ with all $d_i \ge 1$, then $T(n) = O(c^n)$, where $c$ is the unique
real root greater than 1 of $\sum_i c^{-d_i} = 1$ (equivalently, of $x^{d} = \sum_i x^{d - d_i}$ with $d = \max d_i$).

*Proof.* Show $T(n) \le A c^n$ by strong induction, for a constant $A$ large enough to cover the base cases:
$T(n) \le \sum_i A c^{n - d_i} = A c^n \sum_i c^{-d_i} = A c^n$. The function $f(x) = \sum_i x^{-d_i}$ decreases from $k$
at $x = 1$ toward 0, so if $k \ge 2$ there is exactly one root above 1. $\square$

For $(1, 4)$ the equation is $x^4 = x^3 + 1$, with root $c \approx 1.3803$. The program computes several:

| branching vector | equation | base $c$ |
|---|---|---|
| (1, 1) | $x = 2$ | 2 (plain enumeration) |
| (1, 2) | $x^2 = x + 1$ | 1.6180 (the golden ratio) |
| (1, 3) | $x^3 = x^2 + 1$ | 1.4656 |
| (1, 4) | $x^4 = x^3 + 1$ | 1.3803 |
| (2, 2, 2) | $x^2 = 3$ | 1.7321 |

So this simple algorithm runs in $O^*(1.3803^n)$. Each node does polynomial work (finding degrees, deleting vertices),
and the number of nodes is at most a constant times the number of leaves, since each internal node has at least two
children or is a reduction step that shrinks $n$.

```python
--8<-- "books/algorithms/ch14_exact.py"
```

```
branching vector (1, 1): T(n) = O(2.0000^n)
branching vector (1, 2): T(n) = O(1.6180^n)
branching vector (1, 4): T(n) = O(1.3803^n)
branching vector (1, 3): T(n) = O(1.4656^n)
branching vector (2, 2, 2): T(n) = O(1.7321^n)

40 random graphs, branching agrees with brute force: True
n = 20: maximum independent set 12, 13 calls (2^n = 1.05e+06, 1.3803^n = 6.30e+02)
n = 40: maximum independent set 15, 349 calls (2^n = 1.10e+12, 1.3803^n = 3.97e+05)
n = 60: maximum independent set 18, 6959 calls (2^n = 1.15e+18, 1.3803^n = 2.50e+08)

8-queens search tree: Knuth's estimate from 2000 probes 2042, exact count 2057

10-queens search tree: Knuth's estimate from 2000 probes 36672, exact count 35539
```

On sparse random graphs the real search trees are tiny, far below the $1.3803^n$ worst case (the reduction rules do most
of the work). Worst-case bounds are statements about the hardest graphs, not typical ones.

### Better bounds and the frontier

Robert Tarjan and Anthony Trojanowski gave an $O(2^{n/3}) \approx O(1.26^n)$ algorithm for independent set in 1977 by a
long case analysis. Fedor Fomin, Fabrizio Grandoni and Dieter Kratsch introduced **measure and conquer** (2009): measure
the size of an instance not by $n$ but by a weighted count in which low-degree vertices count less, which proves much
better bounds for simple algorithms; their independent-set algorithm runs in $O(1.2210^n)$. Mingyu Xiao and Hiroshi
Nagamochi reached $O(1.1996^n)$ (2017). Other landmarks: Uwe Schöning's 1999 randomised algorithm for 3-SAT in
$O^*((4/3)^n)$; inclusion-exclusion algorithms for Hamiltonian path in $O^*(2^n)$ time and polynomial space; and Andreas
Björklund's $O^*(1.657^n)$ for Hamiltonicity in undirected graphs (2010). The **exponential time hypothesis** of Russell
Impagliazzo and Ramamohan Paturi (2001) conjectures that 3-SAT has no $2^{o(n)}$ algorithm at all; many lower bounds for
other problems are proved assuming it ([Chapter 25](25-Where-Algorithms-Go.md)).

### Measuring a search tree before you run it

How long will a backtracking search take? Running it to find out may take a week. Donald Knuth gave a beautifully
simple estimator in 1975 ("Estimating the efficiency of backtrack programs"): walk **one random path** from the root,
at each node choosing a child uniformly at random, and note the number of children $d_1, d_2, \dots$ at the nodes
passed. The estimate is

$$
X = 1 + d_1 + d_1 d_2 + d_1 d_2 d_3 + \cdots.
$$

**Theorem.** $X$ is an unbiased estimate of the number of nodes in the tree: $\mathbb{E}[X]$ equals the node count.

*Proof.* A node $u$ at depth $k$ is reached by the random walk with probability $1/(d_1 d_2 \cdots d_k)$, where the
$d_i$ are the child counts along the path to $u$. When it is reached, the walk adds $d_1 \cdots d_k$ for depth $k$. Write
$X = \sum_{k} \sum_{u \text{ at depth } k} [u \text{ on the walk}] \cdot d_1(u) \cdots d_k(u)$, where each term is the
contribution of depth $k$ (exactly one node per depth is on the walk, while the walk lasts). Taking expectations, each
node contributes $\Pr[u \text{ on the walk}] \cdot d_1(u) \cdots d_k(u) = 1$. So $\mathbb{E}[X]$ is the number of
nodes. $\square$

Averaging many probes reduces the variance. The program estimates 2042 for the 8-queens tree (exact 2057) and 36 672 for
10-queens (exact 35 539) from 2000 probes each. The variance can be huge when the tree is very unbalanced, so the
estimate is a guide, not a promise; Knuth also described ways to reduce it, and the idea is still used to predict the
running time of SAT and integer-programming solvers.

## Check yourself

??? question "1. How many nodes does the state-space tree of all subsets of n items have? How many for permutations of 3 items?"

    Subsets: a complete binary tree of depth $n$, with $1 + 2 + 4 + \dots + 2^n = 2^{n+1} - 1$ nodes. Permutations of 3:
    $1 + 3 + 3 \cdot 2 + 3 \cdot 2 \cdot 1 = 16$ nodes, with 6 leaves.

??? question "2. Find both solutions of 4-queens by hand and explain why they are mirror images."

    2 4 1 3 and 3 1 4 2 (column of the queen in rows 1 to 4). Reflecting the board left to right sends column $c$ to
    $5 - c$, which maps 2 4 1 3 to 3 1 4 2; reflection preserves rows, columns and diagonals, so it maps solutions to
    solutions.

??? question "3. Write code: generate all strings of n pairs of balanced brackets by backtracking. How many are there for n = 1, ..., 8?"

    Add "(" while fewer than $n$ have been opened; add ")" only while it would not close more than were opened. Those
    two tests prune every invalid prefix, so every leaf is valid.

    ```python
    def brackets(n):
        out = []
        def go(s, opened, closed):
            if len(s) == 2 * n:
                out.append(s)
                return
            if opened < n:
                go(s + "(", opened + 1, closed)
            if closed < opened:
                go(s + ")", opened, closed + 1)
        go("", 0, 0)
        return out

    print(brackets(3))   # ['((()))', '(()())', '(())()', '()(())', '()()()']
    ```

    The counts are 1, 2, 5, 14, 42, 132, 429, 1430: the Catalan numbers, the same numbers that count the bracketings
    of a matrix chain in [Chapter 13](13-Dynamic-Programming.md).

??? question "4. Write code: decide whether a graph can be coloured with k colours so that adjacent vertices differ. Try the Petersen graph with 2 and 3 colours."

    Colour vertices in order; try each colour not used by an already-coloured neighbour; backtrack on failure.

    ```python
    def colour(adj, k):
        n = len(adj)
        col = [None] * n
        def go(v):
            if v == n:
                return True
            for c in range(k):
                if all(col[u] != c for u in adj[v]):
                    col[v] = c
                    if go(v + 1):
                        return True
            col[v] = None
            return False
        return list(col) if go(0) else None

    # Petersen graph: outer 5-cycle, inner pentagram, five spokes
    edges = ([(i, (i + 1) % 5) for i in range(5)] + [(5 + i, 5 + (i + 2) % 5) for i in range(5)]
             + [(i, i + 5) for i in range(5)])
    adj = [[] for _ in range(10)]
    for a, b in edges:
        adj[a].append(b)
        adj[b].append(a)
    print(colour(adj, 2), colour(adj, 3))   # None [0, 1, 0, 1, 2, 1, 0, 2, 2, 1]
    ```

    Two colours fail (the outer 5-cycle is an odd cycle); three succeed.

??? question "5. In the knapsack branch and bound, why try 'take the item' before 'leave it'? Would the answer change if you reversed the order?"

    The answer would not change: pruning is safe in any order, so the optimum is always found. But taking dense items
    first builds a good incumbent early (in the trace, value 80 after five nodes), and a good incumbent prunes more of
    the rest of the tree. Leaving items first would start with the empty knapsack as incumbent and prune almost
    nothing at first.

??? question "6. Prove that the fractional knapsack bound is valid for 0/1 knapsack at every node."

    At a node, every completion chooses some 0/1 subset of the remaining items that fits the remaining capacity. That
    subset is also a feasible fractional solution of the remaining problem, so its value is at most the fractional
    optimum, which greedy by density computes exactly ([Chapter 12](12-Greedy-Algorithms.md)). Adding the value
    already taken gives an upper bound for every completion.

??? question "7. Solve the subset-sum instance 3, 34, 4, 12, 5, 2 with target 30 by meet in the middle."

    $A = \{3, 34, 4\}$: sums $0, 3, 34, 37, 4, 7, 38, 41$. $B$ sorted: $0, 2, 5, 7, 12, 14, 17, 19$. Needed values
    $30 - s$: 30, 27, $-4$, $-7$, 26, 23, $-8$, $-11$. None is in $B$'s list, so no subset sums to 30. (Check: without 34 the
    total is $3 + 4 + 12 + 5 + 2 = 26 < 30$, and 34 alone overshoots.)

??? question "8. Show that the branching vector (1, 2) gives base equal to the golden ratio, and name an algorithm with that vector."

    The equation $c^{-1} + c^{-2} = 1$ becomes $c^2 = c + 1$, whose root above 1 is $(1 + \sqrt 5)/2 \approx 1.618$.
    Example: counting the independent sets of a path by branching on its first vertex: leave it out (path shrinks by 1)
    or take it (it and its neighbour go, shrinking by 2). The counts are Fibonacci numbers, which grow like $1.618^n$.

??? question "9. Vertex cover with budget k: does a graph have k vertices touching every edge? Branch on an edge (u, v): one of u, v must be in the cover. Bound the search tree."

    Each branch puts one vertex in the cover and decreases $k$ by 1, and a branch with $k = 0$ and edges left fails.
    So the tree has depth at most $k$ and at most $2^k$ leaves, and each node costs $O(n + m)$: total $O(2^k (n + m))$.
    The exponential part depends only on $k$, not on $n$; this is the starting point of fixed-parameter algorithms in
    [Chapter 23](23-Approximation-and-Parameterized-Algorithms.md).

??? question "10. Why is the TSP bound of 14.4 valid even though the cheapest edges of different cities may point to the same city?"

    The bound does not claim that the cheapest edges form a tour. It only uses that each city still to be left is left
    exactly once in any completion, along some allowed edge, which costs at least that city's cheapest allowed edge.
    Summing these per-city lower bounds gives a lower bound on the sum of the actual edges. Collisions make the bound
    weaker (less tight), never invalid.

??? question "11. In Knuth's estimator, what is the estimate from a single probe on a tree where the root has 4 children, the chosen child has 3, the next 2, and then a leaf?"

    $X = 1 + 4 + 4 \cdot 3 + 4 \cdot 3 \cdot 2 = 1 + 4 + 12 + 24 = 41$. If every node at each depth had the same number of
    children, this would be the exact node count; differences between subtrees are what make single probes noisy.

## What you learned

- Every exhaustive search is a walk through a state-space tree of partial solutions; backtracking prunes subtrees
  that cannot contain a solution, using a safe and cheap test.
- The formulation decides the size of the tree (one queen per row turns $4.4 \times 10^9$ placements into $8!$).
- Constraint propagation plus "branch on the fewest options" solves Sudoku in a handful of nodes; the same ideas run
  SAT and constraint solvers.
- Branch and bound prunes nodes whose optimistic bound cannot beat the incumbent; bounds come from relaxations, such
  as the fractional knapsack.
- Meet in the middle halves the exponent: subset sum in $O^*(2^{n/2})$ time and space.
- Branching vectors turn a recursive search into a bound $O^*(c^n)$, and Knuth's random probes estimate a tree's size
  before you search it.

**Next:** [Chapter 15](15-Graphs-and-Graph-Search.md), graphs and the two basic ways of searching them, breadth first
and depth first.

## Further reading

- J. Kleinberg and É. Tardos, *Algorithm Design*, 2005: chapter 10 (extending the limits of tractability: small vertex
  covers, trees) and chapter 8 on NP-hard problems.
- D. E. Knuth, *The Art of Computer Programming*, Vol. 4A (*Combinatorial Algorithms, Part 1*), 2011, on generating
  subsets, permutations and combinations; Vol. 4B (*Part 2*), 2022, on backtracking and dancing links.
- D. E. Knuth, "Estimating the efficiency of backtrack programs", *Mathematics of Computation* 29, 1975; D. E. Knuth,
  "Dancing links", in *Millennial Perspectives in Computer Science*, 2000.
- A. H. Land and A. G. Doig, "An automatic method of solving discrete programming problems", *Econometrica* 28, 1960;
  J. D. C. Little, K. G. Murty, D. W. Sweeney and C. Karel, "An algorithm for the traveling salesman problem",
  *Operations Research* 11, 1963.
- E. Horowitz and S. Sahni, "Computing partitions with applications to the knapsack problem", *Journal of the ACM* 21,
  1974; R. Schroeppel and A. Shamir, "A $T = O(2^{n/2})$, $S = O(2^{n/4})$ algorithm for certain NP-complete problems",
  *SIAM Journal on Computing* 10, 1981.
- F. V. Fomin and D. Kratsch, *Exact Exponential Algorithms*, Springer, 2010; F. V. Fomin, F. Grandoni and D. Kratsch,
  "A measure & conquer approach for the analysis of exact algorithms", *Journal of the ACM* 56, 2009.
- D. Applegate, R. Bixby, V. Chvátal and W. Cook, *The Traveling Salesman Problem: A Computational Study*, 2006.
- S. Russell and P. Norvig, *Artificial Intelligence: A Modern Approach*, 4th ed., 2020: chapter 6 (constraint
  satisfaction problems: propagation, backtracking, variable ordering).
- G. McGuire, B. Tugemann and G. Civario, "There is no 16-clue Sudoku: solving the Sudoku minimum number of clues
  problem via hitting set enumeration", *Experimental Mathematics* 23, 2014.
- On this site: [Backtracking](../../backtracking/index.md), [N-Queens](../../backtracking/n-queens.md),
  [Subsets and permutations](../../backtracking/subsets-permutations.md), [Knapsack](../../dp/knapsack.md),
  [Chapter 13](13-Dynamic-Programming.md), [Chapter 22](22-NP-Completeness.md),
  [Chapter 23](23-Approximation-and-Parameterized-Algorithms.md), and the AI book's search chapters
  ([Artificial intelligence](../ai/index.md)).
