# Dynamic programming

**Dynamic programming** (DP) solves a problem by solving smaller versions of the same problem, **remembering each
answer**, and building the big answer from the small ones. It works when two things are true:

1. **Optimal substructure:** the best answer to the whole is made of best answers to parts.
2. **Overlapping subproblems:** the same parts come up again and again, so remembering them saves work.

A plain recursion that recomputes the same parts can take exponential time; with a table it takes about
(number of different parts) × (work per part).

| Page | Problem | Table | Time |
|---|---|---|---|
| [Fibonacci and the DP idea](fibonacci.md) | the $n$th Fibonacci number; memoization vs tabulation | 1D, $n$ | $O(n)$ |
| [Coin change](coin-change.md) | fewest coins for an amount; number of ways | 1D, amount $A$ | $O(kA)$ |
| [0/1 knapsack](knapsack.md) | most value in a bag of limited weight | 2D, items × capacity | $O(nW)$ |
| [Longest common subsequence](lcs.md) | the longest string inside both of two strings | 2D, $n \times m$ | $O(nm)$ |
| [Longest increasing subsequence](lis.md) | the longest rising run, not necessarily adjacent | 1D | $O(n \log n)$ |
| [Edit distance](edit-distance.md) | fewest letter edits from one word to another | 2D, $n \times m$ | $O(nm)$ |

## How to design a DP

1. **Say what one table entry means, in words.** For example: "`best[x]` = the fewest coins that make $x$".
   Most mistakes come from a vague meaning.
2. **Write the rule** (the *recurrence*) that gets an entry from smaller ones, by asking "what was the last
   choice?".
3. **Find the starting values** (the *base cases*), such as `best[0] = 0`.
4. **Choose an order** so every entry is filled after the ones it needs.
5. **Read off the answer**, and if you need the choices too, walk back through the table.

## Top-down or bottom-up?

- **Top-down (memoization):** write the recursion, and keep a dictionary of answers already found. Easy to write;
  only the needed entries are computed; deep recursion can overflow the stack.
- **Bottom-up (tabulation):** fill a table in a loop from the smallest case up. No recursion, often faster, and
  it is easy to keep only the last row or two to save memory.

The name was chosen by Richard Bellman in the 1950s; "programming" meant planning, as in a schedule, not writing code.
