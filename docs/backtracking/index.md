# Backtracking

**Backtracking** searches through all possible answers by building them one choice at a time. After each
choice it goes deeper; when a partial answer can no longer lead anywhere, it **undoes the last choice** and tries
the next option. It is a depth-first search over a tree of decisions.

| Page | Problem | Number of answers | Pruning |
|---|---|---|---|
| [Subsets and permutations](subsets-permutations.md) | list every subset, every ordering; subsets with a given sum | $2^n$, $n!$ | stop when a sum is too big |
| [N-Queens](n-queens.md) | place $n$ queens so none attacks another | 92 for $n = 8$ | skip attacked squares |

## The template

```text
solve(partial):
    if partial is a complete answer: record it; return
    for each option for the next choice:
        if the option is allowed (does not break a rule):
            make the choice          # change the state
            solve(partial + option)
            undo the choice          # put the state back exactly as it was
```

The "undo" step is what gives backtracking its name: one shared state is changed and changed back, instead of
copying it at every step.

## Why prune?

Without rules, the tree is enormous: 8 queens on 64 squares can be placed in 4,426,165,368 ways. Putting one
queen per row cuts that to $8^8 \approx 16.8$ million, and skipping attacked squares as soon as they appear cuts the
search to just **2,057** partial boards. Good pruning, checking rules as early as possible, is the difference
between seconds and centuries.

Backtracking is the right tool when the answers must be **listed**, or when no cleverer method (such as
[dynamic programming](../dp/index.md)) is known. Sudoku, crosswords, mazes, scheduling with many rules, and
puzzle solvers are all classic examples.
