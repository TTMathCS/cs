# Greedy algorithms

A **greedy** algorithm builds its answer one piece at a time and always takes the choice that looks best **right
now**, never going back. It is usually simple and fast. The hard part is knowing when it is *right*: for many
problems the locally best choice leads to a worse total (see [coin change](../dp/coin-change.md) with coins 1, 3
and 4).

| Page | Problem | Greedy rule | Time |
|---|---|---|---|
| [Activity selection](activity-selection.md) | the most non-overlapping meetings in one room | earliest finish first | $O(n \log n)$ |
| [Huffman coding](huffman.md) | the shortest prefix code for given letter counts | join the two rarest | $O(n \log n)$ |

Greedy algorithms elsewhere on this site: [Dijkstra](../graphs/dijkstra.md) (closest unfinished vertex next),
[Kruskal](../graphs/kruskal.md) and [Prim](../graphs/prim.md) (cheapest safe edge next), and the fractional
[knapsack](../dp/knapsack.md) (best value per kilogram first).

## How to prove a greedy algorithm right

Two standard arguments:

1. **Exchange argument.** Take any optimal answer that differs from the greedy one. Swap one of its pieces for
   the greedy choice and show the answer does not get worse. Repeating turns it into the greedy answer, so the
   greedy answer is optimal too.
2. **Greedy stays ahead.** Show by induction that after each step, the greedy partial answer is at least as good
   as any other answer's first $k$ steps (for example, it finishes no later).

## Greedy or dynamic programming?

Both need **optimal substructure** (the best whole is built from best parts). Greedy also needs the
**greedy-choice property**: one choice can be fixed now without looking at the subproblems. When it is not clear
that one choice is always safe, try a small counterexample by hand; if greedy fails, use
[dynamic programming](../dp/index.md).
