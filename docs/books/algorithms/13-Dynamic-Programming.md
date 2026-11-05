# 13. Dynamic programming

*Divide and conquer splits a problem into pieces that do not overlap. Many problems split into pieces that do
overlap, and then plain recursion solves the same small piece again and again, often an exponential number of times.
Dynamic programming is the cure: solve each distinct subproblem once, store the answer in a table, and look it up
when it is needed again. In this chapter you will learn the recipe (state, transition, base case, order), use it on
coins, knapsacks, subsequences, edit distance, DNA alignment, matrix chains, search trees, trees and graphs, and the
travelling salesman, and finish with the tricks that make dynamic programs faster and smaller.*

!!! abstract "In this chapter"
    **You will learn:**

    - why naive recursion can be exponential, and how memoisation and tables make it polynomial
    - the four-part recipe for designing a dynamic program, and how to prove one correct
    - coin change, the 0/1 knapsack (and why $O(nW)$ is only "pseudo-polynomial"), and the longest increasing
      subsequence in $O(n \log n)$
    - longest common subsequence, edit distance and sequence alignment, with the tables traced by hand
    - interval problems (matrix chains, optimal search trees), DP on trees and on directed acyclic graphs
    - the Held-Karp $O(2^n n^2)$ algorithm for the travelling salesman
    - speed-ups: Knuth's optimisation, divide-and-conquer optimisation, the convex hull trick, Hirschberg's
      linear-space LCS

    **You need:** [Chapter 3](03-Recursion-and-Induction.md) (recursion and induction),
    [Chapter 11](11-Divide-and-Conquer.md) (divide and conquer) and [Chapter 12](12-Greedy-Algorithms.md) (where greedy
    fails). Binary search from [Chapter 7](07-Searching-and-Hashing.md) for 13.3.

    **Levels:** 13.1 to 13.3 are beginner to intermediate; 13.4 to 13.7 are intermediate; 13.8 is advanced.

## 13.1 Overlapping subproblems: Fibonacci three ways

The Fibonacci numbers are $F_0 = 0$, $F_1 = 1$ and $F_n = F_{n-1} + F_{n-2}$: 0, 1, 1, 2, 3, 5, 8, 13, ... The definition
is already a recursive program. What does it cost to run it as written?

```python
def fib(n):
    return n if n < 2 else fib(n - 1) + fib(n - 2)
```

### Way 1: plain recursion, exponential

Draw the calls for $F_5$ (Figure 13.1). $F_5$ calls $F_4$ and $F_3$; $F_4$ calls $F_3$ again. The same subproblems
appear over and over.

<figure class="mars-fig" markdown="0">
<svg viewBox="0 0 640 338" role="img" aria-label="The call tree of plain recursive Fibonacci for F5. F5 calls F4 and F3; F4 calls F3 and F2; each F3 calls F2 and F1; each F2 calls F1 and F0. F3 appears twice and F2 three times, 15 calls in all.">
<g stroke="currentColor" stroke-width="1.2">
<line x1="80" y1="216" x2="40" y2="278"/>
<line x1="80" y1="216" x2="120" y2="278"/>
<line x1="140" y1="154" x2="80" y2="216"/>
<line x1="140" y1="154" x2="200" y2="216"/>
<line x1="320" y1="154" x2="280" y2="216"/>
<line x1="320" y1="154" x2="360" y2="216"/>
<line x1="230" y1="92" x2="140" y2="154"/>
<line x1="230" y1="92" x2="320" y2="154"/>
<line x1="480" y1="154" x2="440" y2="216"/>
<line x1="480" y1="154" x2="520" y2="216"/>
<line x1="540" y1="92" x2="480" y2="154"/>
<line x1="540" y1="92" x2="600" y2="154"/>
<line x1="385" y1="30" x2="230" y2="92"/>
<line x1="385" y1="30" x2="540" y2="92"/>
</g>
<circle cx="40" cy="278" r="17" style="fill:var(--md-default-bg-color)"/>
<circle cx="40" cy="278" r="17" stroke="currentColor" stroke-width="1.2" fill="none"/>
<text x="40" y="283" font-size="13" text-anchor="middle" fill="currentColor" font-family="monospace">F1</text>
<circle cx="120" cy="278" r="17" style="fill:var(--md-default-bg-color)"/>
<circle cx="120" cy="278" r="17" stroke="currentColor" stroke-width="1.2" fill="none"/>
<text x="120" y="283" font-size="13" text-anchor="middle" fill="currentColor" font-family="monospace">F0</text>
<circle cx="80" cy="216" r="17" style="fill:var(--md-default-bg-color)"/>
<circle cx="80" cy="216" r="17" stroke="currentColor" stroke-width="1.2" fill="#9cc9ea" fill-opacity="0.6"/>
<text x="80" y="221" font-size="13" text-anchor="middle" fill="currentColor" font-family="monospace">F2</text>
<circle cx="200" cy="216" r="17" style="fill:var(--md-default-bg-color)"/>
<circle cx="200" cy="216" r="17" stroke="currentColor" stroke-width="1.2" fill="none"/>
<text x="200" y="221" font-size="13" text-anchor="middle" fill="currentColor" font-family="monospace">F1</text>
<circle cx="140" cy="154" r="17" style="fill:var(--md-default-bg-color)"/>
<circle cx="140" cy="154" r="17" stroke="currentColor" stroke-width="1.2" fill="#eea66f" fill-opacity="0.6"/>
<text x="140" y="159" font-size="13" text-anchor="middle" fill="currentColor" font-family="monospace">F3</text>
<circle cx="280" cy="216" r="17" style="fill:var(--md-default-bg-color)"/>
<circle cx="280" cy="216" r="17" stroke="currentColor" stroke-width="1.2" fill="none"/>
<text x="280" y="221" font-size="13" text-anchor="middle" fill="currentColor" font-family="monospace">F1</text>
<circle cx="360" cy="216" r="17" style="fill:var(--md-default-bg-color)"/>
<circle cx="360" cy="216" r="17" stroke="currentColor" stroke-width="1.2" fill="none"/>
<text x="360" y="221" font-size="13" text-anchor="middle" fill="currentColor" font-family="monospace">F0</text>
<circle cx="320" cy="154" r="17" style="fill:var(--md-default-bg-color)"/>
<circle cx="320" cy="154" r="17" stroke="currentColor" stroke-width="1.2" fill="#9cc9ea" fill-opacity="0.6"/>
<text x="320" y="159" font-size="13" text-anchor="middle" fill="currentColor" font-family="monospace">F2</text>
<circle cx="230" cy="92" r="17" style="fill:var(--md-default-bg-color)"/>
<circle cx="230" cy="92" r="17" stroke="currentColor" stroke-width="1.2" fill="none"/>
<text x="230" y="97" font-size="13" text-anchor="middle" fill="currentColor" font-family="monospace">F4</text>
<circle cx="440" cy="216" r="17" style="fill:var(--md-default-bg-color)"/>
<circle cx="440" cy="216" r="17" stroke="currentColor" stroke-width="1.2" fill="none"/>
<text x="440" y="221" font-size="13" text-anchor="middle" fill="currentColor" font-family="monospace">F1</text>
<circle cx="520" cy="216" r="17" style="fill:var(--md-default-bg-color)"/>
<circle cx="520" cy="216" r="17" stroke="currentColor" stroke-width="1.2" fill="none"/>
<text x="520" y="221" font-size="13" text-anchor="middle" fill="currentColor" font-family="monospace">F0</text>
<circle cx="480" cy="154" r="17" style="fill:var(--md-default-bg-color)"/>
<circle cx="480" cy="154" r="17" stroke="currentColor" stroke-width="1.2" fill="#9cc9ea" fill-opacity="0.6"/>
<text x="480" y="159" font-size="13" text-anchor="middle" fill="currentColor" font-family="monospace">F2</text>
<circle cx="600" cy="154" r="17" style="fill:var(--md-default-bg-color)"/>
<circle cx="600" cy="154" r="17" stroke="currentColor" stroke-width="1.2" fill="none"/>
<text x="600" y="159" font-size="13" text-anchor="middle" fill="currentColor" font-family="monospace">F1</text>
<circle cx="540" cy="92" r="17" style="fill:var(--md-default-bg-color)"/>
<circle cx="540" cy="92" r="17" stroke="currentColor" stroke-width="1.2" fill="#eea66f" fill-opacity="0.6"/>
<text x="540" y="97" font-size="13" text-anchor="middle" fill="currentColor" font-family="monospace">F3</text>
<circle cx="385" cy="30" r="17" style="fill:var(--md-default-bg-color)"/>
<circle cx="385" cy="30" r="17" stroke="currentColor" stroke-width="1.2" fill="none"/>
<text x="385" y="35" font-size="13" text-anchor="middle" fill="currentColor" font-family="monospace">F5</text>
<text x="320" y="323" font-size="13" text-anchor="middle" fill="currentColor">F3 is computed 2 times and F2 3 times: 15 calls for 6 different subproblems</text>
</svg>
<figcaption>Figure 13.1. The calls made by plain recursion for F5. The same subproblem is solved many times: the orange F3 twice and the blue F2 three times. For F30 the tree has over two and a half million nodes but only 31 different labels.</figcaption>
</figure>

**Claim.** Computing $F_n$ this way makes $C(n) = 2F_{n+1} - 1$ calls.

*Proof* by strong induction. $C(0) = C(1) = 1$, and $2F_1 - 1 = 2F_2 - 1 = 1$. For $n \ge 2$, a call makes itself plus
the calls for $n - 1$ and $n - 2$: $C(n) = 1 + C(n-1) + C(n-2) = 1 + (2F_n - 1) + (2F_{n-1} - 1) = 2F_{n+1} - 1$.
$\square$

Since $F_n$ grows like $\varphi^n / \sqrt{5}$ with $\varphi = (1 + \sqrt 5)/2 \approx 1.618$, the work is exponential.
The program counts 242 785 calls for $F_{25}$, which is $2 F_{26} - 1 = 2 \times 121\,393 - 1$. Yet there are only 26
different subproblems, $F_0$ to $F_{25}$. Problems with this feature have **overlapping subproblems**: a recursive
solution revisits the same subproblems many times.

### Way 2: memoisation (top down)

Keep the recursion, but remember every answer the first time it is computed, in a table called a **memo**. Before
computing $F_k$, look in the memo. Now each $F_k$ is computed once, by two lookups and an addition, so the total work is
$O(n)$. In Python, the decorator `functools.lru_cache` (or `functools.cache`) adds a memo to any function whose
arguments can be dictionary keys.

### Way 3: a table (bottom up)

Or turn the recursion around: compute $F_0, F_1, F_2, \dots$ in increasing order, so that whenever you need $F_{k-1}$
and $F_{k-2}$ they are already known. This uses a simple loop and no recursion at all, and since each value needs only
the previous two, the table shrinks to two variables: $O(n)$ time and $O(1)$ space. The
[Fibonacci reference page](../../dp/fibonacci.md) animates both. ([Chapter 19](19-Number-Theoretic-Algorithms.md) gets
$F_n$ in $O(\log n)$ arithmetic operations by matrix powers.)

```python
--8<-- "books/algorithms/ch13_basics.py"
```

```
fib(10) = 55: naive recursion made 177 calls; memo and table agree: True
fib(20) = 6765: naive recursion made 21891 calls; memo and table agree: True
fib(25) = 75025: naive recursion made 242785 calls; memo and table agree: True
fib(90) by table = 2880067194370816120

min coins for 63 with [1, 5, 10, 21, 25]: (3, [21, 21, 21])
ways to make 100 cents from [1, 5, 10, 25, 50]: 292

knapsack capacity 7: 9 ['B', 'C']
table K[i][w], w = 0..7:
   - [0, 0, 0, 0, 0, 0, 0, 0]
   A [0, 1, 1, 1, 1, 1, 1, 1]
   B [0, 1, 1, 4, 5, 5, 5, 5]
   C [0, 1, 1, 4, 5, 6, 6, 9]
   D [0, 1, 1, 4, 5, 7, 8, 9]

LIS of [3, 1, 4, 1, 5, 9, 2, 6, 5, 3, 5, 8, 9, 7, 9] -> (6, [1, 2, 3, 5, 7, 9])  quadratic DP says length 6
300 random lists: fast LIS length and subsequence check out: True
```

The rest of the program is used in 13.3.

### Bellman and the name

Richard Bellman developed the method at the RAND Corporation in the early 1950s, for multistage decision problems: a
sequence of decisions where each one changes the state in which the next is made. His book *Dynamic Programming*
appeared in 1957. "Programming" then meant planning, as in linear programming, not writing code. In his autobiography,
*Eye of the Hurricane* (1984), Bellman wrote that he picked "dynamic programming" partly because it sounded impressive
and could not be used in a bad sense, at a time when, as he told it, the Secretary of Defense disliked the word
"research". Whatever the motive, the name stuck. Bellman's **principle of optimality** says that an optimal policy has
the property that, whatever the first decision, the remaining decisions form an optimal policy for the state that
results. That is what this book calls **optimal substructure**.

<figure class="play" data-play="fibcalls"><span class="ai-tag">AI-created</span><figcaption>Try it: plain recursion makes 2F<sub>n+1</sub> − 1 calls for F<sub>n</sub>, the claim above; a memo makes n + 1. Move n.</figcaption></figure>

## 13.2 The recipe

Dynamic programming is not one algorithm but a way of designing algorithms. Every dynamic program (DP) has four parts:

1. **State.** What is a subproblem? Choose parameters that describe it: an index $i$, a pair $(i, j)$, a remaining
   capacity $w$, a set of cities $S$. The quantity you want for that state is written like a function, for example
   $\mathrm{OPT}(i, w)$.
2. **Transition.** How is the answer for a state built from answers for smaller states? This is a **recurrence**,
   found by asking: *what is the last (or first) decision, and what are its options?* Each option leads to a smaller
   state.
3. **Base cases.** The smallest states, answered directly.
4. **Order.** An order in which to fill the table so that every state comes after the states it depends on
   (bottom up), or use recursion with a memo (top down) and let the recursion find the order.

Then two more steps: the **answer** is one of the states (or the best of several), and **reconstruction**: to get the
actual solution, not just its value, either store the choice made at each state or retrace the recurrence backwards
from the answer.

### Why it works

**Correctness** is an induction over the order of states: if every state's smaller states hold correct values, the
recurrence gives the correct value for this state. So the whole proof lies in the recurrence: it must consider every
possible last decision (so nothing better is missed) and each option must lead to a genuine subproblem of the same
kind (optimal substructure: an optimal solution's remaining part is optimal for its subproblem, usually proved by
"cut and paste": if it were not, swap in a better one and the whole would improve).

**Running time** is (number of states) × (work per transition), plus the time to reconstruct. A DP with $n^2$ states
and $O(n)$ choices per state takes $O(n^3)$.

### The subproblem graph

Draw one vertex per state and an arrow from each state to the states it uses. Since a state only uses smaller ones,
this **subproblem graph** has no cycles: it is a **directed acyclic graph** (DAG). A bottom-up order is a
**topological order** of this DAG ([Chapter 15](15-Graphs-and-Graph-Search.md)). Every DP is a computation over a DAG,
and many DPs are literally shortest or longest paths in it, as 13.6 shows.

### Top down or bottom up?

| | top down (memo) | bottom up (table) |
|---|---|---|
| code | the recurrence as written, plus a cache | loops in a valid order |
| states solved | only those reachable from the answer | usually all |
| overhead | function calls; Python's recursion limit (about 1000 deep by default) | none |
| saving space | hard | easy: keep only the rows still needed |

Both have the same asymptotic time. Write top down to get a correct program quickly; switch to bottom up for speed,
for deep recursions, or to save memory.

### DP versus divide and conquer versus greedy

All three use optimal substructure. Divide and conquer splits into **disjoint** subproblems, so it needs no table.
Greedy commits to **one** choice per step, which needs a proof that the choice is safe. DP **tries every choice** for
the last decision and keeps the best, which needs no such proof, at the price of solving many subproblems.

## 13.3 Coin change, 0/1 knapsack, LIS

### Coin change: fewest coins

In [Chapter 12](12-Greedy-Algorithms.md) greedy failed for some coin systems. Suppose coins of 1, 5, 10, 21 and 25 and the
amount 63. Greedy takes $25 + 25 + 10 + 1 + 1 + 1$, six coins; but $21 + 21 + 21$ uses three.

- **State:** $\mathrm{best}(v)$ = the fewest coins that make the amount $v$.
- **Transition:** the last coin used is some $c \le v$, and the rest makes $v - c$ with as few coins as possible:

$$
\mathrm{best}(v) = 1 + \min_{c \le v} \mathrm{best}(v - c).
$$

- **Base:** $\mathrm{best}(0) = 0$; an amount no combination reaches gets $\infty$.
- **Order:** $v = 1, 2, \dots, V$.

$V + 1$ states, $k$ coins tried at each: $O(kV)$ time. The program stores the last coin used at each amount to
reconstruct the answer, $21 + 21 + 21$. Its table for $v = 0, \dots, 25$ starts 0, 1, 2, 3, 4, 1, 2, ...: for $v = 20$
it is 2 (two tens), for $v = 21$ it is 1, and for $v = 22$ it is 2 ($21 + 1$).

### Coin change: counting the ways

How many ways can you make a dollar from 1, 5, 10, 25 and 50 cent coins, if the order of the coins does not matter?
Let $\mathrm{ways}_k(v)$ be the number of ways to make $v$ with the first $k$ kinds of coin. Either you use no coin of
kind $k$, or at least one, so $\mathrm{ways}_k(v) = \mathrm{ways}_{k-1}(v) + \mathrm{ways}_k(v - c_k)$. Filling the table
coin by coin in one array (the outer loop over coins in the program) counts each combination exactly once; looping over
amounts on the outside would count $5 + 1$ and $1 + 5$ separately. The answer is 292. The
[coin change](../../dp/coin-change.md) reference page has both versions.

### 0/1 knapsack

The 0/1 knapsack from [Chapter 12](12-Greedy-Algorithms.md): items $1, \dots, n$ with integer weights $w_i$ and values
$v_i$, a capacity $W$; choose items of total weight at most $W$ and maximum value. Greedy fails; DP does not.

- **State:** $K(i, w)$ = the best value using only items $1, \dots, i$ with capacity $w$.
- **Transition:** the last decision is about item $i$. Leave it out, and the best is $K(i-1, w)$. Take it (only if
  $w_i \le w$), and the rest must be the best use of items $1..i-1$ in the capacity left:

$$
K(i, w) = \max\big(K(i-1, w),\; v_i + K(i-1, w - w_i)\big).
$$

- **Base:** $K(0, w) = 0$.
- **Order:** $i = 1, \dots, n$, any order of $w$ within a row.

The program's items are A (weight 1, value 1), B (3, 4), C (4, 5), D (5, 7), with $W = 7$. Its table, one row per item
added, shows how the answer builds up. Look at row C, column 7: leaving C out gives $K(B, 7) = 5$; taking C gives
$5 + K(B, 3) = 5 + 4 = 9$. So 9. In row D, column 7, taking D gives $7 + K(C, 2) = 7 + 1 = 8 < 9$, so D is left out.
To reconstruct, walk back from the corner: a value that differs from the one above it means the item was taken. The
answer is B and C, weight 7, value 9.

*Correctness.* An optimal set for $(i, w)$ either avoids item $i$, and then it is a feasible set for $(i - 1, w)$, or
contains it, and then the rest is feasible for $(i - 1, w - w_i)$; in each case the rest must be optimal for that
subproblem, or swapping in a better one would improve the whole. The recurrence takes the better of the two cases.
$\square$

**Time** $O(nW)$, space $O(nW)$, or $O(W)$ if you keep one row and loop $w$ downwards (so that each item is used at
most once).

### Pseudo-polynomial time

Is $O(nW)$ a polynomial-time algorithm? Not in the sense used in complexity theory. The **size** of an input is the
number of bits needed to write it down. The capacity $W$ takes only about $\log_2 W$ bits, so $W = 2^{\log_2 W}$ is
**exponential** in its own size: add 30 bits to $W$ and the table grows a billion-fold. An algorithm polynomial in the
numeric values but not in their bit lengths is called **pseudo-polynomial**. This is consistent with the knapsack
problem being NP-hard ([Chapter 22](22-NP-Completeness.md)): the DP is fast exactly when the weights are small
integers. When the values are small instead, a DP over values works, and rounding the values gives the knapsack
approximation scheme of [Chapter 23](23-Approximation-and-Parameterized-Algorithms.md). The
[knapsack](../../dp/knapsack.md) reference page has the table animated.

### Longest increasing subsequence

A **subsequence** keeps some elements of a list in their original order, not necessarily next to each other. Find the
longest subsequence that is **strictly increasing**. For $3, 1, 4, 1, 5, 9, 2, 6, 5, 3, 5, 8, 9, 7, 9$ (the digits of
$\pi$), one answer is $1, 2, 3, 5, 7, 9$, of length 6.

**The $O(n^2)$ DP.** Let $L(i)$ be the length of the longest increasing subsequence that **ends at** position $i$. Its
second-to-last element is some earlier $a_j < a_i$, and before that comes the best subsequence ending at $j$:
$L(i) = 1 + \max\{L(j) : j < i, a_j < a_i\}$ (or 1 if no such $j$). The answer is $\max_i L(i)$. $n$ states, $O(n)$ each.

**The $O(n \log n)$ algorithm.** Keep an array `tails`, where `tails[k]` is the **smallest possible last element** of an
increasing subsequence of length $k + 1$ seen so far. For each new element $x$, find the first position $k$ with
`tails[k]` $\ge x$ by binary search, and set `tails[k] = x` (appending if $k$ is past the end). The length of `tails` at
the end is the answer.

| $x$ | position $k$ | tails after |
|---|---|---|
| 3 | 0 | 3 |
| 1 | 0 | 1 |
| 4 | 1 | 1, 4 |
| 1 | 0 | 1, 4 |
| 5 | 2 | 1, 4, 5 |
| 9 | 3 | 1, 4, 5, 9 |
| 2 | 1 | 1, 2, 5, 9 |
| 6 | 3 | 1, 2, 5, 6 |
| 5 | 2 | 1, 2, 5, 6 |
| 3 | 2 | 1, 2, 3, 6 |
| 5 | 3 | 1, 2, 3, 5 |
| 8 | 4 | 1, 2, 3, 5, 8 |
| 9 | 5 | 1, 2, 3, 5, 8, 9 |
| 7 | 4 | 1, 2, 3, 5, 7, 9 |
| 9 | 5 | 1, 2, 3, 5, 7, 9 |

Note that `tails` is not itself a subsequence in general (here it happens to be one); it is a summary. To recover an
actual subsequence, the program records, for each element, which element sat in the previous slot when it was placed.

**Lemma.** `tails` is always strictly increasing, and after processing a prefix of the list, for each $k$, `tails[k]` is
the smallest last element of any increasing subsequence of length $k + 1$ in that prefix.

*Proof* by induction over the elements. Suppose it holds before $x$. Any increasing subsequence of length $k + 1$ ending
at $x$ extends one of length $k$ ending below $x$, which exists exactly when $k = 0$ or `tails[k-1]` $< x$. So $x$ can end
subsequences of every length up to $k^* + 1$, where $k^*$ is the first index with `tails[k*]` $\ge x$; it improves only
the slot $k^*$ (for smaller $k$, `tails[k]` $< x$ already, and for larger $k$ it cannot end such a subsequence). Setting
`tails[k*] = x` keeps the array strictly increasing, since `tails[k*-1]` $< x \le$ the old `tails[k*]` $<$
`tails[k*+1]`. $\square$

So the number of slots is the length of the longest increasing subsequence. Each step is a binary search, $O(\log n)$,
for $O(n \log n)$ total. Michael Fredman showed in 1975 that $\Omega(n \log n)$ comparisons are needed in the worst case,
so this is optimal among comparison algorithms. The method is also called **patience sorting**, after a card game in
which cards are dealt onto piles; David Aldous and Persi Diaconis wrote a survey of it in 1999. Reference page:
[LIS](../../dp/lis.md).

## 13.4 Sequences: LCS, edit distance, alignment

### Longest common subsequence

Given two strings $x = x_1 \dots x_m$ and $y = y_1 \dots y_n$, find the longest string that is a subsequence of both. The
`diff` tool that compares two versions of a file is built on this problem (with lines in place of letters).

- **State:** $C(i, j)$ = length of an LCS of the prefixes $x_1 \dots x_i$ and $y_1 \dots y_j$.
- **Transition:** look at the last letters.

$$
C(i, j) =
\begin{cases}
C(i-1, j-1) + 1 & \text{if } x_i = y_j, \\
\max\big(C(i-1, j),\, C(i, j-1)\big) & \text{if } x_i \ne y_j.
\end{cases}
$$

- **Base:** $C(i, 0) = C(0, j) = 0$.
- **Order:** row by row.

**Theorem.** The recurrence is correct.

*Proof.* Let $z_1 \dots z_k$ be an LCS of $x_1..x_i$ and $y_1..y_j$. If $x_i = y_j$, then $z_k = x_i$: otherwise
appending $x_i$ to $z$ would give a longer common subsequence. And $z_1..z_{k-1}$ is a common subsequence of
$x_1..x_{i-1}$ and $y_1..y_{j-1}$, which must be longest (a longer one, with $x_i$ appended, would beat $z$). So
$C(i, j) = C(i-1, j-1) + 1$. If $x_i \ne y_j$, then $z_k$ cannot equal both, so either $z$ does not use $x_i$ (then
$z$ is a common subsequence of $x_1..x_{i-1}$ and $y_1..y_j$) or it does not use $y_j$. Hence
$C(i,j) \le \max(C(i-1,j), C(i,j-1))$, and the reverse inequality is obvious, since a common subsequence of shorter
prefixes is also one of the longer. $\square$

<figure class="mars-fig" markdown="0">
<svg viewBox="0 0 398 442" role="img" aria-label="The LCS table for ABCBDAB down the side and BDCABA across the top, with values from 0 to 4. The traceback path from the bottom right corner to the top left is shaded, with the four matched cells, spelling B C B A, highlighted.">
<text x="136" y="28" font-size="14" text-anchor="middle" fill="currentColor" font-family="monospace" font-weight="bold">B</text>
<text x="180" y="28" font-size="14" text-anchor="middle" fill="currentColor" font-family="monospace" font-weight="bold">D</text>
<text x="224" y="28" font-size="14" text-anchor="middle" fill="currentColor" font-family="monospace" font-weight="bold">C</text>
<text x="268" y="28" font-size="14" text-anchor="middle" fill="currentColor" font-family="monospace" font-weight="bold">A</text>
<text x="312" y="28" font-size="14" text-anchor="middle" fill="currentColor" font-family="monospace" font-weight="bold">B</text>
<text x="356" y="28" font-size="14" text-anchor="middle" fill="currentColor" font-family="monospace" font-weight="bold">A</text>
<text x="56" y="111" font-size="14" text-anchor="middle" fill="currentColor" font-family="monospace" font-weight="bold">A</text>
<text x="56" y="155" font-size="14" text-anchor="middle" fill="currentColor" font-family="monospace" font-weight="bold">B</text>
<text x="56" y="199" font-size="14" text-anchor="middle" fill="currentColor" font-family="monospace" font-weight="bold">C</text>
<text x="56" y="243" font-size="14" text-anchor="middle" fill="currentColor" font-family="monospace" font-weight="bold">B</text>
<text x="56" y="287" font-size="14" text-anchor="middle" fill="currentColor" font-family="monospace" font-weight="bold">D</text>
<text x="56" y="331" font-size="14" text-anchor="middle" fill="currentColor" font-family="monospace" font-weight="bold">A</text>
<text x="56" y="375" font-size="14" text-anchor="middle" fill="currentColor" font-family="monospace" font-weight="bold">B</text>
<rect x="70" y="40" width="44" height="44" stroke="currentColor" stroke-width="0.8" fill="none"/>
<text x="92" y="67" font-size="14" text-anchor="middle" fill="currentColor" font-family="monospace">0</text>
<rect x="114" y="40" width="44" height="44" stroke="currentColor" stroke-width="0.8" fill="none"/>
<text x="136" y="67" font-size="14" text-anchor="middle" fill="currentColor" font-family="monospace">0</text>
<rect x="158" y="40" width="44" height="44" stroke="currentColor" stroke-width="0.8" fill="none"/>
<text x="180" y="67" font-size="14" text-anchor="middle" fill="currentColor" font-family="monospace">0</text>
<rect x="202" y="40" width="44" height="44" stroke="currentColor" stroke-width="0.8" fill="none"/>
<text x="224" y="67" font-size="14" text-anchor="middle" fill="currentColor" font-family="monospace">0</text>
<rect x="246" y="40" width="44" height="44" stroke="currentColor" stroke-width="0.8" fill="none"/>
<text x="268" y="67" font-size="14" text-anchor="middle" fill="currentColor" font-family="monospace">0</text>
<rect x="290" y="40" width="44" height="44" stroke="currentColor" stroke-width="0.8" fill="none"/>
<text x="312" y="67" font-size="14" text-anchor="middle" fill="currentColor" font-family="monospace">0</text>
<rect x="334" y="40" width="44" height="44" stroke="currentColor" stroke-width="0.8" fill="none"/>
<text x="356" y="67" font-size="14" text-anchor="middle" fill="currentColor" font-family="monospace">0</text>
<rect x="70" y="84" width="44" height="44" stroke="currentColor" stroke-width="0.8" fill="none"/>
<text x="92" y="111" font-size="14" text-anchor="middle" fill="currentColor" font-family="monospace">0</text>
<rect x="114" y="84" width="44" height="44" stroke="currentColor" stroke-width="0.8" fill="none"/>
<text x="136" y="111" font-size="14" text-anchor="middle" fill="currentColor" font-family="monospace">0</text>
<rect x="158" y="84" width="44" height="44" stroke="currentColor" stroke-width="0.8" fill="none"/>
<text x="180" y="111" font-size="14" text-anchor="middle" fill="currentColor" font-family="monospace">0</text>
<rect x="202" y="84" width="44" height="44" stroke="currentColor" stroke-width="0.8" fill="none"/>
<text x="224" y="111" font-size="14" text-anchor="middle" fill="currentColor" font-family="monospace">0</text>
<rect x="246" y="84" width="44" height="44" stroke="currentColor" stroke-width="0.8" fill="none"/>
<text x="268" y="111" font-size="14" text-anchor="middle" fill="currentColor" font-family="monospace">1</text>
<rect x="290" y="84" width="44" height="44" stroke="currentColor" stroke-width="0.8" fill="none"/>
<text x="312" y="111" font-size="14" text-anchor="middle" fill="currentColor" font-family="monospace">1</text>
<rect x="334" y="84" width="44" height="44" stroke="currentColor" stroke-width="0.8" fill="none"/>
<text x="356" y="111" font-size="14" text-anchor="middle" fill="currentColor" font-family="monospace">1</text>
<rect x="70" y="128" width="44" height="44" stroke="currentColor" stroke-width="0.8" fill="none"/>
<text x="92" y="155" font-size="14" text-anchor="middle" fill="currentColor" font-family="monospace">0</text>
<rect x="114" y="128" width="44" height="44" stroke="currentColor" stroke-width="0.8" fill="#7ccf9a" fill-opacity="0.7"/>
<text x="136" y="155" font-size="14" text-anchor="middle" fill="currentColor" font-family="monospace">1</text>
<rect x="158" y="128" width="44" height="44" stroke="currentColor" stroke-width="0.8" fill="#9cc9ea" fill-opacity="0.5"/>
<text x="180" y="155" font-size="14" text-anchor="middle" fill="currentColor" font-family="monospace">1</text>
<rect x="202" y="128" width="44" height="44" stroke="currentColor" stroke-width="0.8" fill="none"/>
<text x="224" y="155" font-size="14" text-anchor="middle" fill="currentColor" font-family="monospace">1</text>
<rect x="246" y="128" width="44" height="44" stroke="currentColor" stroke-width="0.8" fill="none"/>
<text x="268" y="155" font-size="14" text-anchor="middle" fill="currentColor" font-family="monospace">1</text>
<rect x="290" y="128" width="44" height="44" stroke="currentColor" stroke-width="0.8" fill="none"/>
<text x="312" y="155" font-size="14" text-anchor="middle" fill="currentColor" font-family="monospace">2</text>
<rect x="334" y="128" width="44" height="44" stroke="currentColor" stroke-width="0.8" fill="none"/>
<text x="356" y="155" font-size="14" text-anchor="middle" fill="currentColor" font-family="monospace">2</text>
<rect x="70" y="172" width="44" height="44" stroke="currentColor" stroke-width="0.8" fill="none"/>
<text x="92" y="199" font-size="14" text-anchor="middle" fill="currentColor" font-family="monospace">0</text>
<rect x="114" y="172" width="44" height="44" stroke="currentColor" stroke-width="0.8" fill="none"/>
<text x="136" y="199" font-size="14" text-anchor="middle" fill="currentColor" font-family="monospace">1</text>
<rect x="158" y="172" width="44" height="44" stroke="currentColor" stroke-width="0.8" fill="none"/>
<text x="180" y="199" font-size="14" text-anchor="middle" fill="currentColor" font-family="monospace">1</text>
<rect x="202" y="172" width="44" height="44" stroke="currentColor" stroke-width="0.8" fill="#7ccf9a" fill-opacity="0.7"/>
<text x="224" y="199" font-size="14" text-anchor="middle" fill="currentColor" font-family="monospace">2</text>
<rect x="246" y="172" width="44" height="44" stroke="currentColor" stroke-width="0.8" fill="#9cc9ea" fill-opacity="0.5"/>
<text x="268" y="199" font-size="14" text-anchor="middle" fill="currentColor" font-family="monospace">2</text>
<rect x="290" y="172" width="44" height="44" stroke="currentColor" stroke-width="0.8" fill="none"/>
<text x="312" y="199" font-size="14" text-anchor="middle" fill="currentColor" font-family="monospace">2</text>
<rect x="334" y="172" width="44" height="44" stroke="currentColor" stroke-width="0.8" fill="none"/>
<text x="356" y="199" font-size="14" text-anchor="middle" fill="currentColor" font-family="monospace">2</text>
<rect x="70" y="216" width="44" height="44" stroke="currentColor" stroke-width="0.8" fill="none"/>
<text x="92" y="243" font-size="14" text-anchor="middle" fill="currentColor" font-family="monospace">0</text>
<rect x="114" y="216" width="44" height="44" stroke="currentColor" stroke-width="0.8" fill="none"/>
<text x="136" y="243" font-size="14" text-anchor="middle" fill="currentColor" font-family="monospace">1</text>
<rect x="158" y="216" width="44" height="44" stroke="currentColor" stroke-width="0.8" fill="none"/>
<text x="180" y="243" font-size="14" text-anchor="middle" fill="currentColor" font-family="monospace">1</text>
<rect x="202" y="216" width="44" height="44" stroke="currentColor" stroke-width="0.8" fill="none"/>
<text x="224" y="243" font-size="14" text-anchor="middle" fill="currentColor" font-family="monospace">2</text>
<rect x="246" y="216" width="44" height="44" stroke="currentColor" stroke-width="0.8" fill="none"/>
<text x="268" y="243" font-size="14" text-anchor="middle" fill="currentColor" font-family="monospace">2</text>
<rect x="290" y="216" width="44" height="44" stroke="currentColor" stroke-width="0.8" fill="#7ccf9a" fill-opacity="0.7"/>
<text x="312" y="243" font-size="14" text-anchor="middle" fill="currentColor" font-family="monospace">3</text>
<rect x="334" y="216" width="44" height="44" stroke="currentColor" stroke-width="0.8" fill="none"/>
<text x="356" y="243" font-size="14" text-anchor="middle" fill="currentColor" font-family="monospace">3</text>
<rect x="70" y="260" width="44" height="44" stroke="currentColor" stroke-width="0.8" fill="none"/>
<text x="92" y="287" font-size="14" text-anchor="middle" fill="currentColor" font-family="monospace">0</text>
<rect x="114" y="260" width="44" height="44" stroke="currentColor" stroke-width="0.8" fill="none"/>
<text x="136" y="287" font-size="14" text-anchor="middle" fill="currentColor" font-family="monospace">1</text>
<rect x="158" y="260" width="44" height="44" stroke="currentColor" stroke-width="0.8" fill="none"/>
<text x="180" y="287" font-size="14" text-anchor="middle" fill="currentColor" font-family="monospace">2</text>
<rect x="202" y="260" width="44" height="44" stroke="currentColor" stroke-width="0.8" fill="none"/>
<text x="224" y="287" font-size="14" text-anchor="middle" fill="currentColor" font-family="monospace">2</text>
<rect x="246" y="260" width="44" height="44" stroke="currentColor" stroke-width="0.8" fill="none"/>
<text x="268" y="287" font-size="14" text-anchor="middle" fill="currentColor" font-family="monospace">2</text>
<rect x="290" y="260" width="44" height="44" stroke="currentColor" stroke-width="0.8" fill="#9cc9ea" fill-opacity="0.5"/>
<text x="312" y="287" font-size="14" text-anchor="middle" fill="currentColor" font-family="monospace">3</text>
<rect x="334" y="260" width="44" height="44" stroke="currentColor" stroke-width="0.8" fill="none"/>
<text x="356" y="287" font-size="14" text-anchor="middle" fill="currentColor" font-family="monospace">3</text>
<rect x="70" y="304" width="44" height="44" stroke="currentColor" stroke-width="0.8" fill="none"/>
<text x="92" y="331" font-size="14" text-anchor="middle" fill="currentColor" font-family="monospace">0</text>
<rect x="114" y="304" width="44" height="44" stroke="currentColor" stroke-width="0.8" fill="none"/>
<text x="136" y="331" font-size="14" text-anchor="middle" fill="currentColor" font-family="monospace">1</text>
<rect x="158" y="304" width="44" height="44" stroke="currentColor" stroke-width="0.8" fill="none"/>
<text x="180" y="331" font-size="14" text-anchor="middle" fill="currentColor" font-family="monospace">2</text>
<rect x="202" y="304" width="44" height="44" stroke="currentColor" stroke-width="0.8" fill="none"/>
<text x="224" y="331" font-size="14" text-anchor="middle" fill="currentColor" font-family="monospace">2</text>
<rect x="246" y="304" width="44" height="44" stroke="currentColor" stroke-width="0.8" fill="none"/>
<text x="268" y="331" font-size="14" text-anchor="middle" fill="currentColor" font-family="monospace">3</text>
<rect x="290" y="304" width="44" height="44" stroke="currentColor" stroke-width="0.8" fill="none"/>
<text x="312" y="331" font-size="14" text-anchor="middle" fill="currentColor" font-family="monospace">3</text>
<rect x="334" y="304" width="44" height="44" stroke="currentColor" stroke-width="0.8" fill="#7ccf9a" fill-opacity="0.7"/>
<text x="356" y="331" font-size="14" text-anchor="middle" fill="currentColor" font-family="monospace">4</text>
<rect x="70" y="348" width="44" height="44" stroke="currentColor" stroke-width="0.8" fill="none"/>
<text x="92" y="375" font-size="14" text-anchor="middle" fill="currentColor" font-family="monospace">0</text>
<rect x="114" y="348" width="44" height="44" stroke="currentColor" stroke-width="0.8" fill="none"/>
<text x="136" y="375" font-size="14" text-anchor="middle" fill="currentColor" font-family="monospace">1</text>
<rect x="158" y="348" width="44" height="44" stroke="currentColor" stroke-width="0.8" fill="none"/>
<text x="180" y="375" font-size="14" text-anchor="middle" fill="currentColor" font-family="monospace">2</text>
<rect x="202" y="348" width="44" height="44" stroke="currentColor" stroke-width="0.8" fill="none"/>
<text x="224" y="375" font-size="14" text-anchor="middle" fill="currentColor" font-family="monospace">2</text>
<rect x="246" y="348" width="44" height="44" stroke="currentColor" stroke-width="0.8" fill="none"/>
<text x="268" y="375" font-size="14" text-anchor="middle" fill="currentColor" font-family="monospace">3</text>
<rect x="290" y="348" width="44" height="44" stroke="currentColor" stroke-width="0.8" fill="none"/>
<text x="312" y="375" font-size="14" text-anchor="middle" fill="currentColor" font-family="monospace">4</text>
<rect x="334" y="348" width="44" height="44" stroke="currentColor" stroke-width="0.8" fill="#9cc9ea" fill-opacity="0.5"/>
<text x="356" y="375" font-size="14" text-anchor="middle" fill="currentColor" font-family="monospace">4</text>
<text x="199" y="427" font-size="13" text-anchor="middle" fill="currentColor">green: matches B, C, B, A on the way back from the corner</text>
</svg>
<figcaption>Figure 13.2. The LCS table for ABCBDAB (rows) and BDCABA (columns), the example in CLRS. Tracing back from the bottom-right corner, a diagonal step (green) is a matched letter and a step up or left (blue) skips one; the matches spell BCBA.</figcaption>
</figure>

```python
--8<-- "books/algorithms/ch13_sequences.py"
```

```
LCS of ABCBDAB and BDCABA: 4 BCBA
table (rows ABCBDAB, columns BDCABA):
   [0, 0, 0, 0, 0, 0, 0]
   [0, 0, 0, 0, 1, 1, 1]
   [0, 1, 1, 1, 1, 2, 2]
   [0, 1, 1, 2, 2, 2, 2]
   [0, 1, 1, 2, 2, 3, 3]
   [0, 1, 2, 2, 2, 3, 3]
   [0, 1, 2, 2, 3, 3, 4]
   [0, 1, 2, 2, 3, 4, 4]

edit distance kitten -> sitting: 3 ['substitute k->s', 'substitute e->i', 'insert g']
edit distance sunday -> saturday: 3 ['insert a', 'insert t', 'substitute n->r']

alignment score 0:
  GCA-TGCG
  G-ATTACA
```

The table has $(m+1)(n+1)$ entries, each $O(1)$: time and space $O(mn)$. To compute only the length, two rows suffice;
to get the subsequence itself in linear space, see Hirschberg in 13.8. Reference page: [LCS](../../dp/lcs.md).

### Edit distance

How many single-letter edits turn one word into another? An **edit** is inserting a letter, deleting one, or
substituting one letter for another. The minimum number is the **edit distance**, or **Levenshtein distance**, after
Vladimir Levenshtein, who defined it in 1965 in work on error-correcting codes. Spell checkers use it to suggest the
dictionary words closest to a typo.

Let $D(i, j)$ be the edit distance between $s_1..s_i$ and $t_1..t_j$. Consider the last letters in an optimal
sequence of edits, lined up as an **alignment**: either $s_i$ is deleted, or $t_j$ is inserted, or $s_i$ is turned into
$t_j$ (free if they are equal):

$$
D(i, j) = \min
\begin{cases}
D(i-1, j) + 1 & \text{delete } s_i, \\
D(i, j-1) + 1 & \text{insert } t_j, \\
D(i-1, j-1) + [s_i \ne t_j] & \text{match or substitute},
\end{cases}
$$

where $[s_i \ne t_j]$ is 1 if the letters differ and 0 if not. The base cases are $D(i, 0) = i$ (delete everything) and
$D(0, j) = j$ (insert everything). The table for kitten and sitting, rows k-i-t-t-e-n, columns s-i-t-t-i-n-g:

| | | s | i | t | t | i | n | g |
|---|---|---|---|---|---|---|---|---|
| | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 |
| **k** | 1 | 1 | 2 | 3 | 4 | 5 | 6 | 7 |
| **i** | 2 | 2 | 1 | 2 | 3 | 4 | 5 | 6 |
| **t** | 3 | 3 | 2 | 1 | 2 | 3 | 4 | 5 |
| **t** | 4 | 4 | 3 | 2 | 1 | 2 | 3 | 4 |
| **e** | 5 | 5 | 4 | 3 | 2 | 2 | 3 | 4 |
| **n** | 6 | 6 | 5 | 4 | 3 | 3 | 2 | 3 |

The corner is 3: substitute k by s, substitute e by i, insert g. Correctness follows the LCS argument: in an optimal
alignment the last column is one of the three cases, and the rest is an optimal alignment of the shorter prefixes. The
same table algorithm was published several times; Robert Wagner and Michael Fischer's 1974 paper "The string-to-string
correction problem" is the usual reference. Reference page: [edit distance](../../dp/edit-distance.md).

Is $O(mn)$ the best possible? Arturs Backurs and Piotr Indyk showed in 2015 that a truly subquadratic algorithm
(time $O(n^{2 - \varepsilon})$) would refute the Strong Exponential Time Hypothesis, a widely believed conjecture.
[Chapter 25](25-Where-Algorithms-Go.md) explains what that means.

### Sequence alignment in biology

When biologists compare two DNA or protein sequences, they want to line them up so that related positions sit in the
same column, allowing gaps where one sequence gained or lost letters during evolution. Each column gets a score: a
reward for a match, a penalty for a mismatch, and a penalty for a gap. The best **global alignment** maximises the
total score, by the same recurrence with $\max$ in place of $\min$:

$$
S(i, j) = \max\big(S(i-1, j-1) + \sigma(a_i, b_j),\; S(i-1, j) + g,\; S(i, j-1) + g\big),
$$

where $\sigma$ is the match or mismatch score and $g < 0$ is the gap score. This is the algorithm of Saul Needleman
and Christian Wunsch (1970). With match $+1$, mismatch $-1$ and gap $-1$, the program aligns GCATGCG with GATTACA:

```
GCA-TGCG
G-ATTACA
```

for a score of 0 (four matches, two mismatches, two gaps). Real tools use substitution scores measured from related
proteins (such as the BLOSUM matrices) and **affine** gap penalties, where opening a gap costs more than extending it,
which needs three tables instead of one (Gotoh, 1982). Temple Smith and Michael Waterman's 1981 variant finds the best
**local** alignment, the most similar pair of substrings, by also allowing a score to restart at 0. For searching huge
databases, heuristics such as BLAST (Altschul and others, 1990) first look for short exact matches and run the DP only
around them.

## 13.5 Intervals: matrix-chain multiplication, optimal BST

Some problems are about a sequence that must be split recursively, and the natural subproblem is a **contiguous
interval** $i..j$. The transition chooses where to split, and the order is by interval length.

### Matrix-chain multiplication

Multiplying a $p \times q$ matrix by a $q \times r$ matrix takes $pqr$ scalar multiplications. Matrix multiplication is
associative, so a product $A_1 A_2 \cdots A_n$ can be bracketed in many ways, all giving the same result, but at very
different costs. With $A_1$ of shape $10 \times 100$, $A_2$ of $100 \times 5$, $A_3$ of $5 \times 50$:

- $(A_1 A_2) A_3$ costs $10 \cdot 100 \cdot 5 + 10 \cdot 5 \cdot 50 = 5000 + 2500 = 7500$;
- $A_1 (A_2 A_3)$ costs $100 \cdot 5 \cdot 50 + 10 \cdot 100 \cdot 50 = 25\,000 + 50\,000 = 75\,000$.

Ten times more. How many bracketings are there? For $n$ matrices it is the Catalan number $C_{n-1}$, which grows like
$4^n / n^{3/2}$, so trying them all is hopeless for long chains.

Let matrix $A_i$ have shape $p_{i-1} \times p_i$, and let $m(i, j)$ be the cheapest cost of computing
$A_i \cdots A_j$. The last multiplication in the best bracketing splits the chain at some $k$ with $i \le k < j$: it
multiplies $(A_i \cdots A_k)$, a $p_{i-1} \times p_k$ matrix, by $(A_{k+1} \cdots A_j)$, a $p_k \times p_j$ one. So

$$
m(i, j) = \min_{i \le k < j} \Big( m(i, k) + m(k+1, j) + p_{i-1} p_k p_j \Big), \qquad m(i, i) = 0.
$$

Both pieces are shorter intervals, so filling the table by increasing length $j - i$ works. There are $O(n^2)$
intervals and $O(n)$ splits each: $O(n^3)$ time, $O(n^2)$ space. Store the best $k$ for each interval to print the
bracketing.

```python
--8<-- "books/algorithms/ch13_intervals_trees.py"
```

```
matrix chain 30x35, 35x15, 15x5, 5x10, 10x20, 20x25: (15125, '((A1(A2A3))((A4A5)A6))')
left to right ((((A1A2)A3)A4)A5)A6 would cost 40500

optimal BST expected cost 2.75, root key k2

longest path in the DAG: (15, [0, 1, 2, 3, 5])
tree independent set: best with root 21  without root 15  answer 21
```

For CLRS's six-matrix example (shapes $30 \times 35$, $35 \times 15$, $15 \times 5$, $5 \times 10$, $10 \times 20$,
$20 \times 25$) the best order costs 15 125 against 40 500 for multiplying left to right. The optimal bracketing
$((A_1 (A_2 A_3))((A_4 A_5) A_6))$ first multiplies around the small dimension 5.

### Optimal binary search trees

A dictionary of words will be searched many times, and we know how often each word (and each kind of miss) will be
looked up. Which [binary search tree](../../data-structures/bst.md) on these keys minimises the expected number of nodes
visited? Balanced is not always best: a very common key should be near the root even if that unbalances the tree.

In CLRS's formulation, keys $k_1 < \dots < k_n$ are searched with probabilities $p_1, \dots, p_n$, and searches that fall
between keys (the "dummy keys" $d_0, \dots, d_n$, leaves of the tree) with probabilities $q_0, \dots, q_n$. The expected
cost is $\sum_i (\mathrm{depth}(k_i) + 1) p_i + \sum_i (\mathrm{depth}(d_i) + 1) q_i$. Let $e(i, j)$ be the least
expected cost of a tree on keys $k_i..k_j$ (and the dummies between them), and $w(i, j)$ the total probability of
those keys and dummies. Choosing the root $k_r$ splits into left keys $k_i..k_{r-1}$ and right keys $k_{r+1}..k_j$,
and every node goes one level deeper, which adds $w(i, j)$:

$$
e(i, j) = \min_{i \le r \le j} \big( e(i, r-1) + e(r+1, j) \big) + w(i, j), \qquad e(i, i-1) = q_{i-1}.
$$

This is an interval DP again, $O(n^3)$. On CLRS's five-key example ($p = 0.15, 0.10, 0.05, 0.10, 0.20$ and
$q = 0.05, 0.10, 0.05, 0.05, 0.05, 0.10$) the program finds expected cost 2.75 with root $k_2$, matching the book. Donald
Knuth gave this DP in 1971, together with a trick that brings it down to $O(n^2)$ (13.8).

## 13.6 DP on trees and DAGs

### Longest path in a DAG

On a general graph, finding the longest simple path is NP-hard: it includes the question of whether a path through
every vertex exists ([Chapter 22](22-NP-Completeness.md)). On a **directed acyclic graph** it is easy. Number the
vertices in topological order, so every edge goes from a smaller to a larger number. Let $\mathrm{best}(v)$ be the
length of the longest path ending at $v$:

$$
\mathrm{best}(v) = \max\Big(0,\; \max_{(u, v) \in E} \big(\mathrm{best}(u) + w(u, v)\big)\Big).
$$

All edges into $v$ come from earlier vertices, so processing vertices in topological order makes the recurrence valid.
Each edge is looked at once: $O(V + E)$ time after a topological sort
([Chapter 15](15-Graphs-and-Graph-Search.md), [topological sort](../../graphs/topological-sort.md)). Replace max by
min and you have shortest paths in a DAG, even with negative weights ([Chapter 16](16-Shortest-Paths.md)).

<figure class="mars-fig" markdown="0">
<svg viewBox="0 0 640 300" role="img" aria-label="A directed acyclic graph with vertices 0 to 5 in a row. Edges: 0 to 1 weight 5, 0 to 2 weight 3, 1 to 2 weight 2, 1 to 3 weight 6, 2 to 3 weight 7, 2 to 4 weight 4, 2 to 5 weight 2, 3 to 4 weight minus 1, 3 to 5 weight 1, 4 to 5 weight minus 2. The longest path 0, 1, 2, 3, 5 of length 15 is highlighted.">
<defs><marker id="arr13" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="currentColor"/></marker></defs>
<line x1="78" y1="150" x2="145" y2="150" stroke="#eea66f" stroke-width="3" marker-end="url(#arr13)"/>
<path d="M60,132 Q164.0,42 268,132" fill="none" stroke="currentColor" stroke-width="1.3" marker-end="url(#arr13)"/>
<path d="M164,168 Q268.0,258 372,168" fill="none" stroke="currentColor" stroke-width="1.3" marker-end="url(#arr13)"/>
<line x1="182" y1="150" x2="249" y2="150" stroke="#eea66f" stroke-width="3" marker-end="url(#arr13)"/>
<path d="M268,132 Q372.0,42 476,132" fill="none" stroke="currentColor" stroke-width="1.3" marker-end="url(#arr13)"/>
<path d="M268,168 Q424.0,308 580,168" fill="none" stroke="currentColor" stroke-width="1.3" marker-end="url(#arr13)"/>
<line x1="286" y1="150" x2="353" y2="150" stroke="#eea66f" stroke-width="3" marker-end="url(#arr13)"/>
<path d="M372,132 Q476.0,42 580,132" fill="none" stroke="#eea66f" stroke-width="3" marker-end="url(#arr13)"/>
<line x1="390" y1="150" x2="457" y2="150" stroke="currentColor" stroke-width="1.3" marker-end="url(#arr13)"/>
<line x1="494" y1="150" x2="561" y2="150" stroke="currentColor" stroke-width="1.3" marker-end="url(#arr13)"/>
<circle cx="60" cy="150" r="18" style="fill:var(--md-default-bg-color)"/>
<circle cx="60" cy="150" r="18" stroke="currentColor" stroke-width="1.3" fill="#9cc9ea" fill-opacity="0.5"/>
<text x="60" y="155" font-size="14" text-anchor="middle" fill="currentColor" font-family="monospace">0</text>
<circle cx="164" cy="150" r="18" style="fill:var(--md-default-bg-color)"/>
<circle cx="164" cy="150" r="18" stroke="currentColor" stroke-width="1.3" fill="#9cc9ea" fill-opacity="0.5"/>
<text x="164" y="155" font-size="14" text-anchor="middle" fill="currentColor" font-family="monospace">1</text>
<circle cx="268" cy="150" r="18" style="fill:var(--md-default-bg-color)"/>
<circle cx="268" cy="150" r="18" stroke="currentColor" stroke-width="1.3" fill="#9cc9ea" fill-opacity="0.5"/>
<text x="268" y="155" font-size="14" text-anchor="middle" fill="currentColor" font-family="monospace">2</text>
<circle cx="372" cy="150" r="18" style="fill:var(--md-default-bg-color)"/>
<circle cx="372" cy="150" r="18" stroke="currentColor" stroke-width="1.3" fill="#9cc9ea" fill-opacity="0.5"/>
<text x="372" y="155" font-size="14" text-anchor="middle" fill="currentColor" font-family="monospace">3</text>
<circle cx="476" cy="150" r="18" style="fill:var(--md-default-bg-color)"/>
<circle cx="476" cy="150" r="18" stroke="currentColor" stroke-width="1.3" fill="#9cc9ea" fill-opacity="0.5"/>
<text x="476" y="155" font-size="14" text-anchor="middle" fill="currentColor" font-family="monospace">4</text>
<circle cx="580" cy="150" r="18" style="fill:var(--md-default-bg-color)"/>
<circle cx="580" cy="150" r="18" stroke="currentColor" stroke-width="1.3" fill="#9cc9ea" fill-opacity="0.5"/>
<text x="580" y="155" font-size="14" text-anchor="middle" fill="currentColor" font-family="monospace">5</text>
<text x="112" y="142" font-size="13" text-anchor="middle" fill="currentColor">5</text>
<text x="164" y="81" font-size="13" text-anchor="middle" fill="currentColor">3</text>
<text x="268" y="229" font-size="13" text-anchor="middle" fill="currentColor">6</text>
<text x="216" y="142" font-size="13" text-anchor="middle" fill="currentColor">2</text>
<text x="372" y="81" font-size="13" text-anchor="middle" fill="currentColor">4</text>
<text x="424" y="254" font-size="13" text-anchor="middle" fill="currentColor">2</text>
<text x="320" y="142" font-size="13" text-anchor="middle" fill="currentColor">7</text>
<text x="476" y="81" font-size="13" text-anchor="middle" fill="currentColor">1</text>
<text x="424" y="142" font-size="13" text-anchor="middle" fill="currentColor">-1</text>
<text x="528" y="142" font-size="13" text-anchor="middle" fill="currentColor">-2</text>
<text x="320" y="292" font-size="13" text-anchor="middle" fill="currentColor">longest path 0 → 1 → 2 → 3 → 5, length 5 + 2 + 7 + 1 = 15</text>
</svg>
<figcaption>Figure 13.3. A weighted DAG with vertices in topological order. The longest path (orange) is 0, 1, 2, 3, 5 with length 15; the DP finds it by computing best(v) for v = 0, 1, ..., 5 in turn.</figcaption>
</figure>

The values for Figure 13.3 are: best(0) = 0; best(1) = 5; best(2) = max(0 + 3, 5 + 2) = 7; best(3) = max(5 + 6, 7 + 7) = 14;
best(4) = max(7 + 4, 14 - 1) = 13; best(5) = max(7 + 2, 14 + 1, 13 - 2) = 15.

This picture explains every DP in the chapter. In the knapsack, each state $(i, w)$ is a vertex, with an edge of weight
0 to $(i+1, w)$ and an edge of weight $v_{i+1}$ to $(i + 1, w + w_{i+1})$; the best knapsack is the longest path. In the
edit-distance grid, the answer is the shortest path from the top-left corner to the bottom-right, with horizontal and
vertical steps costing 1 and diagonal steps costing 0 or 1. Designing a DP is choosing a DAG.

### Independent set on a tree

An **independent set** in a graph is a set of vertices no two of which are joined by an edge. Finding a heaviest one is
NP-hard in general graphs, but on a **tree** it is a short DP. Root the tree. For each vertex $v$ compute two numbers:

- $\mathrm{take}(v)$: the heaviest independent set in $v$'s subtree that contains $v$. Then no child may be in it:
  $\mathrm{take}(v) = w(v) + \sum_{c} \mathrm{skip}(c)$.
- $\mathrm{skip}(v)$: the heaviest one not containing $v$. Then each child is free:
  $\mathrm{skip}(v) = \sum_{c} \max(\mathrm{take}(c), \mathrm{skip}(c))$.

The answer is $\max(\mathrm{take}(\text{root}), \mathrm{skip}(\text{root}))$, computed by one post-order traversal (children
before parents): $O(n)$. Correctness: the subtrees of different children share no edges, so their choices are
independent once $v$'s status is fixed. In the program's tree (root r weight 6 with children a, b; a has children c, d;
b has child e; e has children f, g; weights a 4, b 3, c 5, d 2, e 8, f 1, g 1), the answer is 21 = r + c + d + e.

The trick generalises: on a tree, keep a few numbers per vertex describing the "interface" between the vertex and its
parent. On graphs that are tree-like (small **treewidth**), the same idea solves many NP-hard problems in time
exponential only in the treewidth ([Chapter 23](23-Approximation-and-Parameterized-Algorithms.md)).

## 13.7 Bitmask DP: travelling salesman (Held-Karp)

A rover must visit $n$ science targets and return to the lander, and the driving distance between every pair is
known. In what order should it visit them to drive the least? This is the **travelling salesman problem** (TSP), one of
the most studied NP-hard problems. Trying all $(n-1)!$ orders is hopeless beyond about a dozen targets.

In 1962, Richard Bellman and, independently, Michael Held and Richard Karp gave a DP that runs in $O(2^n n^2)$. Still
exponential, but $2^n$ is far smaller than $n!$: at $n = 20$ it is about $2 \times 10^8$ steps against $1.2 \times 10^{17}$
orders.

### The state

The key question: what do we need to know about a partial tour to finish it optimally? Not the order in which the
cities were visited, only **which** cities have been visited and **where we are now**. So:

- **State:** $C(S, j)$ = the length of the shortest path that starts at city 0, visits exactly the cities in the set $S$
  (with $0 \notin S$), and ends at city $j \in S$.
- **Transition:** the city before $j$ is some $k \in S \setminus \{j\}$:

$$
C(S, j) = \min_{k \in S,\, k \ne j} \Big( C(S \setminus \{j\}, k) + d(k, j) \Big).
$$

- **Base:** $C(\{j\}, j) = d(0, j)$.
- **Answer:** $\min_j \big(C(\{1, \dots, n-1\}, j) + d(j, 0)\big)$, closing the tour.

**Bitmasks.** A subset of $\{1, \dots, n-1\}$ is stored as an integer whose bit $j - 1$ is 1 when city $j$ is in the set.
Then "$j \in S$" is `S >> (j-1) & 1`, adding $j$ is `S | 1 << (j-1)`, and, the reason the order works, every proper
subset of $S$ is a **smaller integer** than $S$. So looping $S = 1, 2, 3, \dots$ in numeric order fills every state after
its subproblems. (The program writes the same recurrence "forward": from each state it pushes to the states one city
larger.)

**Time and space.** There are $2^{n-1}$ sets and up to $n - 1$ endpoints: $O(2^n n)$ states, each taking $O(n)$ to
evaluate, so $O(2^n n^2)$ time and $O(2^n n)$ space. Correctness: the shortest path through $S$ ending at $j$ is a
shortest path through $S \setminus \{j\}$ ending at its own last city $k$, followed by the edge $(k, j)$; any shorter path
through $S \setminus \{j\}$ to $k$ could be substituted.

```python
--8<-- "books/algorithms/ch13_held_karp.py"
```

```
4 cities (directed distances): (21, [0, 2, 3, 1, 0])  brute force: 21
9 random cities: Held-Karp 296.89 tour [0, 4, 5, 1, 6, 3, 7, 8, 2, 0], brute force 296.89
work: Held-Karp about 2^(n-1) * n^2 = 20736  brute force (n-1)! tours = 40320
n = 15: 2^(n-1) n^2 = 3.69e+06, (n-1)! = 8.72e+10
n = 20: 2^(n-1) n^2 = 2.10e+08, (n-1)! = 1.22e+17
n = 25: 2^(n-1) n^2 = 1.05e+10, (n-1)! = 6.20e+23
```

The four-city example has **directed** distances (the distance from $i$ to $j$ need not equal the distance back), which
the DP handles without change. The best tour, $0 \to 2 \to 3 \to 1 \to 0$, has length $9 + 8 + 3 + 1 = 21$.

How good is $O(2^n n^2)$? For the general TSP with arbitrary distances, no algorithm with running time $O(c^n)$ for a
constant $c < 2$ is known: improving on Held-Karp is an open problem. In practice, exact TSP solvers such as Concorde
(Applegate, Bixby, Chvátal and Cook) use linear programming and branch and cut
([Chapter 14](14-Backtracking-and-Branch-and-Bound.md), [Chapter 23](23-Approximation-and-Parameterized-Algorithms.md))
and solve instances with thousands of cities, though without a worst-case guarantee.

Bitmask DP applies whenever the state must remember a set drawn from a small universe: assigning $n$ jobs to $n$
workers, covering a board with dominoes row by row, or choosing a subset of sensors.

## 13.8 Speed-ups

*Level: advanced.*

A DP's time is (states) × (work per state). Speed-ups either avoid trying every option for each state, by proving that
the best option moves monotonically, or reduce the space. Each of the four below is checked against the plain DP in the
program.

```python
--8<-- "books/algorithms/ch13_speedups.py"
```

```
Hirschberg LCS length 188 | full-table length 188 | common subsequence of both: True
optimal BST, 120 keys: plain cost 15372 in 295120 inner steps; Knuth cost 15372 in 14168 steps
partition 200 numbers into 6 groups: plain 775553  divide and conquer 775553
stops on a route, first 400: plain 1225104774  hull 1225104774 | hull on all 2000: 6337489893
100 random tests of all four speed-ups against the plain DP passed: True
```

### Knuth's optimisation

In the optimal BST recurrence, let $\mathrm{root}(i, j)$ be the index of a best root for keys $i..j$. Knuth proved in
1971 that roots can be chosen to be **monotone**:

$$
\mathrm{root}(i, j-1) \le \mathrm{root}(i, j) \le \mathrm{root}(i+1, j).
$$

Intuitively, adding a key on the right can only pull the best root to the right, and removing a key on the left can
only push it to the right as well. So when computing $e(i, j)$, try only roots in that range.

**Theorem.** With this restriction, the DP takes $O(n^2)$ time.

*Proof.* For a fixed length $\ell = j - i$, the work over all intervals of that length is
$\sum_i \big(\mathrm{root}(i+1, i+\ell) - \mathrm{root}(i, i+\ell-1) + 1\big)$. The sum **telescopes**: consecutive terms
cancel, leaving $\mathrm{root}(n - \ell + 1, n) - \mathrm{root}(1, \ell) + (n - \ell + 1) \le 2n$. Summing over $n$
lengths gives $O(n^2)$. $\square$

The monotonicity itself takes more work to prove; F. Frances Yao (1980) gave a general condition, the **quadrangle
inequality**, $w(a, c) + w(b, d) \le w(a, d) + w(b, c)$ for $a \le b \le c \le d$ (together with monotonicity of $w$
on nested intervals), under which any recurrence of the form $e(i, j) = \min_k (e(i, k) + e(k, j)) + w(i, j)$ has
monotone optimal splits. The program's 120-key tree needs 295 120 inner steps the plain way and 14 168 with Knuth's
range, for the same cost.

### Divide-and-conquer optimisation

Many DPs have layers of the form $\mathrm{dp}_t(i) = \min_{j < i} \big( \mathrm{dp}_{t-1}(j) + \mathrm{cost}(j, i) \big)$:
for example, splitting a list into $t$ contiguous groups, where $\mathrm{cost}(j, i)$ is the cost of a group made of items
$j+1..i$. Done directly, each layer takes $O(n^2)$. Suppose the best $j$ for $i$, call it $\mathrm{opt}(i)$, is
non-decreasing in $i$ (which holds when the cost satisfies the quadrangle inequality, as the square of a group's sum
does). Then compute $\mathrm{opt}$ for the middle $i$ by scanning all candidates, and recurse: the left half of the
$i$'s only needs candidates up to $\mathrm{opt}(\text{mid})$, the right half only from it. Each level of this recursion
scans $O(n)$ candidates in total and there are $O(\log n)$ levels, so each layer costs $O(n \log n)$ instead of $O(n^2)$.

### The convex hull trick

Consider a rover driving along a straight route with possible stops at positions $x_0 < x_1 < \dots < x_{n-1}$. It must
start at the first and end at the last. Each stop costs a fixed $C$, and a leg of length $L$ costs $L^2$ (long legs
drain the battery disproportionately; it is a toy model). The cheapest plan satisfies

$$
\mathrm{dp}(i) = \min_{j < i} \big( \mathrm{dp}(j) + (x_i - x_j)^2 \big) + C.
$$

Expand the square: $\mathrm{dp}(j) + x_j^2 - 2 x_j x_i + x_i^2$. For fixed $j$, the part that depends on both $i$ and
$j$ is the **line** $y = m_j t + b_j$ with slope $m_j = -2x_j$ and intercept $b_j = \mathrm{dp}(j) + x_j^2$, evaluated at
$t = x_i$. So $\mathrm{dp}(i) = x_i^2 + C + \min_j (m_j x_i + b_j)$: the lowest of a set of lines at one point. The
lower envelope of a set of lines is convex, a "hull". Because the slopes arrive in decreasing order and the query points
$x_i$ increase, a deque of the lines on the envelope does it: pop lines from the back that the new line makes useless
(the `bad` test compares two intersection points, with integers only), and pop lines from the front that are no longer
the minimum at the current query. Each line is pushed and popped at most once, so the whole DP takes $O(n)$ after
sorting, instead of $O(n^2)$. When slopes or queries come in no particular order, a binary search on the envelope or a
**Li Chao tree** gives $O(n \log n)$.

### Hirschberg's linear-space LCS

The LCS table needs $O(mn)$ space, which for two sequences of a million letters is a trillion entries. The length alone
needs only two rows. Can we get the subsequence itself in linear space? Daniel Hirschberg showed how in 1975.

Split $x$ in the middle, $x = x_{\text{top}} x_{\text{bottom}}$. Compute, with two rows each:

- the last row of the LCS table of $x_{\text{top}}$ against every prefix of $y$: $L(k)$, the LCS length of $x_{\text{top}}$
  and $y_1..y_k$;
- the same for the reversed $x_{\text{bottom}}$ against the reversed $y$: $R(k)$, the LCS length of $x_{\text{bottom}}$
  and $y_{k+1}..y_n$.

An optimal alignment crosses the middle row somewhere, at a column $k$ that maximises $L(k) + R(k)$. Then the LCS is
the LCS of $(x_{\text{top}}, y_1..y_k)$ followed by the LCS of $(x_{\text{bottom}}, y_{k+1}..y_n)$, two independent,
smaller problems: recurse.

**Theorem.** Hirschberg's algorithm finds an LCS in $O(mn)$ time and $O(m + n)$ space.

*Proof.* Correctness: every common subsequence splits at some column $k$ into a common subsequence of the top half with
$y_1..y_k$ and one of the bottom half with the rest, so the best total over $k$ is the LCS length, and the two recursive
calls achieve their parts. Time: the top-level call does about $mn$ work (two half tables of $mn/2$ each). Its two
children work on $x$-halves of length $m/2$ and $y$-pieces of lengths $k$ and $n - k$, so together about
$(m/2) k + (m/2)(n - k) = mn/2$. Each level halves the total: $mn(1 + 1/2 + 1/4 + \dots) \le 2mn$. Space: only two rows
are alive at a time, plus the recursion stack of depth $O(\log m)$ and the output. $\square$

The same idea, "find the middle of the optimal path, then recurse", works for edit distance and alignment, and is
how bioinformatics tools align long sequences (Myers and Miller, 1988).

## Check yourself

??? question "1. How many calls does plain recursion make for F(30)? Use the formula from 13.1."

    $C(30) = 2F_{31} - 1 = 2 \times 1\,346\,269 - 1 = 2\,692\,537$. With a memo, 31 distinct values are computed (and
    each looked up at most twice), so about 60 calls.

??? question "2. You can climb a staircase 1 or 2 steps at a time. In how many ways can you climb n steps? Write the DP."

    Let $W(n)$ be the number of ways. The last step was 1 or 2, so $W(n) = W(n-1) + W(n-2)$, with $W(0) = W(1) = 1$.
    So $W(n) = F_{n+1}$: 1, 2, 3, 5, 8, 13, 21 for $n = 1, \dots, 7$.

    ```python
    def climb(n):
        a, b = 1, 1               # W(0), W(1)
        for _ in range(n):
            a, b = b, a + b
        return a
    ```

??? question "3. Fill the 0/1 knapsack table for capacity 5 and items (weight, value) (2, 3), (3, 4), (4, 5), (5, 6)."

    Rows after each item, for $w = 0..5$: item 1: 0 0 3 3 3 3; item 2: 0 0 3 4 4 7; item 3: 0 0 3 4 5 7;
    item 4: 0 0 3 4 5 7. The answer is 7, items 1 and 2 (weight 5). In row 2, column 5, taking item 2 gives
    $4 + K(1, 2) = 4 + 3 = 7$.

??? question "4. Why is the O(nW) knapsack algorithm not a polynomial-time algorithm? Would it become one if all weights were at most n^2?"

    The input writes $W$ in about $\log_2 W$ bits, and $nW$ is exponential in that. If every weight is at most $n^2$,
    then only capacities up to $n \cdot n^2$ matter, so $W$ can be capped at $n^3$ and the time is $O(n^4)$, which is
    polynomial. Pseudo-polynomial algorithms are polynomial exactly on inputs whose numbers are polynomially bounded.

??? question "5. Find an LCS of AGGTAB and GXTXAYB."

    Length 4: GTAB. (Check: G, T, A, B appear in that order in both.) Running `lcs("AGGTAB", "GXTXAYB")` from the
    chapter's program gives `(4, 'GTAB')`.

??? question "6. What is the edit distance between intention and execution? Which edits?"

    5. Both end in "tion", and the first five letters "inten" and "execu" differ in every position, so five
    substitutions (i to e, n to x, t to e, e to c, n to u) do it. No cheaper sequence exists, which the table confirms.

??? question "7. Find the best bracketing of A1 (10 x 100), A2 (100 x 5), A3 (5 x 50) with the matrix-chain DP."

    $m(1,2) = 10 \cdot 100 \cdot 5 = 5000$, $m(2,3) = 100 \cdot 5 \cdot 50 = 25\,000$.
    $m(1,3) = \min(m(1,1) + m(2,3) + 10 \cdot 100 \cdot 50,\; m(1,2) + m(3,3) + 10 \cdot 5 \cdot 50) =
    \min(75\,000, 7500) = 7500$, split after $A_2$: $(A_1 A_2) A_3$.

??? question "8. Write code: the longest palindromic subsequence of a string, as an interval DP."

    Let $L(i, j)$ be the answer for $s_i..s_j$. If $s_i = s_j$, both ends can be the outside letters of a palindrome:
    $L(i,j) = L(i+1, j-1) + 2$. Otherwise one end is unused: $\max(L(i+1, j), L(i, j-1))$. Fill by decreasing $i$.

    ```python
    def longest_palindromic_subsequence(s):
        n = len(s)
        if n == 0:
            return 0
        L = [[0] * n for _ in range(n)]
        for i in range(n - 1, -1, -1):
            L[i][i] = 1
            for j in range(i + 1, n):
                if s[i] == s[j]:
                    L[i][j] = L[i + 1][j - 1] + 2
                else:
                    L[i][j] = max(L[i + 1][j], L[i][j - 1])
        return L[0][n - 1]

    print(longest_palindromic_subsequence("character"))   # 5, for example "carac"
    ```

    $O(n^2)$ time and space. (Checked against brute force over all subsequences for 100 random strings.) It also equals
    the LCS of $s$ and its reverse.

??? question "9. Write code: a minimum vertex cover of a tree (fewest vertices touching every edge)."

    For each vertex keep $\mathrm{in}(v)$ (cover contains $v$) and $\mathrm{out}(v)$ (it does not, so every child must be
    in): $\mathrm{in}(v) = 1 + \sum_c \min(\mathrm{in}(c), \mathrm{out}(c))$, $\mathrm{out}(v) = \sum_c \mathrm{in}(c)$.

    ```python
    def tree_vertex_cover(children, root):
        def solve(v):
            take, skip = 1, 0
            for c in children.get(v, []):
                t, s = solve(c)
                take += min(t, s)
                skip += t           # v not in the cover: the edge (v, c) needs c
            return take, skip
        return min(solve(root))

    tree = {"r": ["a", "b"], "a": ["c", "d"], "b": ["e"], "e": ["f", "g"]}
    print(tree_vertex_cover(tree, "r"))   # 3, for example {a, b, e}
    ```

??? question "10. In Held-Karp, why must the state include the last city j, not just the set S?"

    To extend a partial path by city $k$ you add $d(j, k)$, which depends on where the path ends. Two paths through the
    same set but ending at different cities cannot be compared: the shorter one might end far from every remaining
    city. Keeping the endpoint is exactly the information the future needs, no more.

??? question "11. Prove that in the LIS algorithm the array tails stays strictly increasing, using only the update rule."

    Before the update, assume `tails` is strictly increasing. The new element $x$ goes to the first index $k$ with
    `tails[k]` $\ge x$. Then `tails[k-1]` $< x$ (by the choice of $k$), and $x \le$ old `tails[k]` $<$ `tails[k+1]`.
    So after setting `tails[k] = x` we still have `tails[k-1]` $< x <$ `tails[k+1]`. If $k$ was the end, $x$ is larger
    than every entry and is appended.

??? question "12. Show that Hirschberg's algorithm needs only O(log m) recursion depth and explain why its time is at most about 2mn."

    Each call halves the length of $x$, so the depth is $\lceil \log_2 m \rceil$. At recursion depth $d$ the $x$-pieces
    have length $m/2^d$ and the $y$-pieces partition $y$, so the total table work at that depth is
    $\sum (m/2^d) n_i = mn/2^d$. Summing over $d$ gives at most $mn(1 + 1/2 + 1/4 + \dots) = 2mn$.

## What you learned

- When recursive subproblems overlap, store each answer once: a memo (top down) or a table (bottom up) turns
  exponential recursion into polynomial work.
- The recipe: state, transition (consider every option for the last decision), base cases, order; correctness is
  induction over the order, time is states times work per state.
- Coin change and knapsack are DPs over amounts; $O(nW)$ is pseudo-polynomial, consistent with NP-hardness. LIS takes
  $O(n \log n)$ with the `tails` array.
- Sequence DPs (LCS, edit distance, Needleman-Wunsch) fill an $(m+1) \times (n+1)$ grid; interval DPs (matrix chains,
  optimal BSTs) fill by interval length.
- Every DP is a path problem on a DAG of subproblems; on trees, keep a few numbers per vertex; on sets, use bitmasks
  (Held-Karp, $O(2^n n^2)$).
- Monotone optimal choices (Knuth, divide and conquer), lower envelopes of lines (convex hull trick) and
  middle-splitting (Hirschberg) make DPs faster or smaller.

**Next:** [Chapter 14](14-Backtracking-and-Branch-and-Bound.md), searching the whole space of solutions when no
polynomial recurrence exists, and pruning that search hard.

## Further reading

- R. Bellman, *Dynamic Programming*, Princeton University Press, 1957; R. Bellman, *Eye of the Hurricane: An
  Autobiography*, 1984.
- T. H. Cormen, C. E. Leiserson, R. L. Rivest and C. Stein, *Introduction to Algorithms*, 4th ed., 2022: chapter 14
  (rod cutting, matrix chains, LCS, optimal BSTs).
- J. Kleinberg and É. Tardos, *Algorithm Design*, 2005: chapter 6 (weighted interval scheduling, segmented least
  squares, knapsack, sequence alignment, Hirschberg's method, shortest paths).
- S. Dasgupta, C. Papadimitriou and U. Vazirani, *Algorithms*, 2006: chapter 6, which presents every DP as a DAG.
- M. Held and R. M. Karp, "A dynamic programming approach to sequencing problems", *Journal of SIAM* 10, 1962;
  R. Bellman, "Dynamic programming treatment of the travelling salesman problem", *Journal of the ACM* 9, 1962.
- D. E. Knuth, "Optimum binary search trees", *Acta Informatica* 1, 1971; F. F. Yao, "Efficient dynamic programming
  using quadrangle inequalities", *STOC* 1980.
- D. S. Hirschberg, "A linear space algorithm for computing maximal common subsequences", *Communications of the ACM*
  18, 1975.
- S. B. Needleman and C. D. Wunsch, "A general method applicable to the search for similarities in the amino acid
  sequence of two proteins", *Journal of Molecular Biology* 48, 1970; T. F. Smith and M. S. Waterman, "Identification of
  common molecular subsequences", *Journal of Molecular Biology* 147, 1981.
- R. A. Wagner and M. J. Fischer, "The string-to-string correction problem", *Journal of the ACM* 21, 1974.
- A. Backurs and P. Indyk, "Edit distance cannot be computed in strongly subquadratic time (unless SETH is false)",
  *STOC* 2015.
- On this site: [Fibonacci](../../dp/fibonacci.md), [Coin change](../../dp/coin-change.md),
  [Knapsack](../../dp/knapsack.md), [LIS](../../dp/lis.md), [LCS](../../dp/lcs.md),
  [Edit distance](../../dp/edit-distance.md), [Topological sort](../../graphs/topological-sort.md),
  [Floyd-Warshall](../../graphs/floyd-warshall.md) (a DP over intermediate vertices),
  [Chapter 12](12-Greedy-Algorithms.md), [Chapter 16](16-Shortest-Paths.md).
