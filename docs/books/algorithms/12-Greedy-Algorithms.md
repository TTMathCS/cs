# 12. Greedy algorithms

*Many optimisation problems can be solved by a series of choices, and the tempting way to make them is to take
whatever looks best right now and never look back. Sometimes that gives the best possible answer, and sometimes it
fails badly. In this chapter you will learn to tell the difference: you will see greedy rules fail on coins and
knapsacks, prove them right for scheduling and for Huffman's compression codes with two standard proof methods
(greedy stays ahead, and the exchange argument), and finish with matroids, the structure that explains exactly when
greedy is guaranteed to work.*

!!! abstract "In this chapter"
    **You will learn:**

    - what a greedy algorithm is, and why "locally best" need not be "globally best"
    - which coin systems let the cashier's rule give the fewest coins, and which do not
    - two proof methods, greedy stays ahead and the exchange argument, used on interval scheduling and on lateness
    - Huffman coding: building an optimal prefix code, with a full proof of optimality
    - why the fractional knapsack is greedy-easy and the 0/1 knapsack is not
    - matroids and the theorem that greedy is optimal for every weighting exactly on matroids
    - a first look at minimum spanning trees (the cut property) and at greedy as an approximation for set cover

    **You need:** [Chapter 9](09-Heaps-and-Priority-Queues.md) (priority queues, for Huffman),
    [Chapter 10](10-Union-Find-and-Range-Queries.md) (union-find, for 12.7), and proof by induction and contradiction
    from [Chapter 3](03-Recursion-and-Induction.md). Sorting from [Chapter 5](05-Sorting-by-Comparison.md).

    **Levels:** 12.1 to 12.3 are beginner to intermediate; 12.4, 12.5 and 12.7 are intermediate; 12.6 is advanced.

## 12.1 The greedy idea and when it fails

A cashier owes you 63 cents and has quarters (25), dimes (10), nickels (5) and pennies (1). Without thinking, most
cashiers hand over the largest coin that does not exceed what is still owed, and repeat: 25, 25, 10, then three 1s.
Six coins. Could fewer coins make 63 cents? No, and for these coins the cashier's rule always gives the fewest. But
change the coins and the rule can fail.

A **greedy algorithm** builds a solution piece by piece, and at each step makes the choice that looks best by some
simple local measure, without reconsidering earlier choices. It never backtracks. Greedy algorithms are usually short,
fast and easy to code. The catch is that they are often wrong, and you can only trust one after a proof.

### A coin system that breaks greedy

Take coins of 1, 3 and 4 and the amount 6. Greedy takes 4, then 1 and 1: three coins. But $3 + 3$ uses two. Greedy
went wrong at its very first step: taking the 4 looked best, but it left an amount (2) that the remaining coins
handle badly.

Real coins have done this. Before 1971, Britain's coins included the sixpence (6 pence), the shilling (12), the
florin (24) and the half-crown (30). To make 48 pence, greedy starts with a half-crown and ends with
$30 + 12 + 6$, three coins, while two florins, $24 + 24$, would do. Any coin system is worth checking.

```python
--8<-- "books/algorithms/ch12_scheduling.py"
```

```
coins [25, 10, 5, 1]: greedy optimal below 35, so for every amount
coins [4, 3, 1]: greedy fails first at 6: [4, 1, 1] (3 coins) but 2 suffice
coins [25, 10, 1]: greedy fails first at 30: [25, 1, 1, 1, 1, 1] (6 coins) but 3 suffice
coins [1, 2, 5, 10, 20, 50, 100, 200]: greedy optimal below 300, so for every amount

activities chosen by earliest finish: ['a', 'd', 'h', 'k']

jobs (name, length, deadline): [('j4', 4, 9), ('j1', 3, 6), ('j6', 2, 15), ('j3', 1, 9), ('j5', 3, 14), ('j2', 2, 8)]
earliest deadline first: ['j1', 'j2', 'j4', 'j3', 'j5', 'j6']  max lateness: 1
best of all 720 orders: max lateness 1
shortest job first: ['j3', 'j6', 'j2', 'j1', 'j5', 'j4']  max lateness: 6
```

The program compares greedy with the true optimum, which it computes by dynamic programming
([Chapter 13](13-Dynamic-Programming.md) explains how; the reference page is [coin change](../../dp/coin-change.md)).
Removing the nickel from American coins breaks greedy at 30 cents: $25 + 5 \times 1$ versus $10 + 10 + 10$.

How far must the program test? Dexter Kozen and Shmuel Zaks proved in 1994 that if greedy fails for some amount,
then it already fails for an amount smaller than the sum of the two largest coins. So testing every amount below
$25 + 10 = 35$ settles the question for American coins, and below $200 + 100 = 300$ for the euro cent coins
$1, 2, 5, 10, 20, 50, 100, 200$. A coin system where greedy is always optimal is called **canonical**. David Pearson
gave a polynomial-time test for canonicity in 2005.

### A proof for American coins

Testing up to 35 is a proof, given the theorem. But here is a direct proof, which shows the typical shape of a greedy
argument: show that an optimal solution must look like the greedy one.

**Claim.** For coins 1, 5, 10, 25, greedy gives the fewest coins for every amount.

*Proof.* Take any solution with the fewest coins. It has at most 4 pennies (five could become a nickel, saving 4
coins), at most 1 nickel (two could become a dime), at most 2 dimes (three could become a quarter and a nickel), and
it never has 2 dimes together with a nickel (that makes 25, one quarter). So its pennies, nickels and dimes together are worth at most
$4 + 20 = 24$ cents (two dimes, no nickel, four pennies; or one dime, one nickel, four pennies is only 19). Since
they total less than 25, the number of quarters must be $\lfloor v / 25 \rfloor$, exactly what greedy takes. In the
remainder $r < 25$, the nickels and pennies are worth at most $5 + 4 = 9 < 10$, so the number of dimes is
$\lfloor r / 10 \rfloor$, again greedy's choice; and pennies worth at most $4 < 5$ force the nickel count. So the
optimal solution is the greedy one. $\square$

### Two questions for every greedy algorithm

When greedy works, its correctness rests on two properties, which we will meet over and over:

- **Greedy choice property.** Some optimal solution contains the greedy first choice. So making it does not shut you
  off from the optimum.
- **Optimal substructure.** After the first choice, what remains is a smaller instance of the same problem, and an
  optimal solution to it, combined with the first choice, is optimal for the whole.

If both hold, induction finishes the proof. Dynamic programming ([Chapter 13](13-Dynamic-Programming.md)) needs only
the second; it tries all first choices instead of trusting one. That is why it is slower but works on more
problems.

The two standard ways of proving the greedy choice property are:

- **Greedy stays ahead:** compare greedy's partial solution with any optimal one step by step, and show greedy is
  never behind by some measure.
- **Exchange argument:** take any optimal solution that differs from greedy's, and swap pieces to make it more like
  greedy's without making it worse.

<figure class="play" data-play="greedycoins"><span class="ai-tag">AI-created</span><figcaption><b>Try it.</b> The cashier's rule against the fewest coins, for both coin systems above. Try 6 with coins 4, 3, 1.</figcaption></figure>

## 12.2 Activity selection

One lecture hall, many requests. Each request $i$ asks for the hall from start time $s_i$ to finish time $f_i$. Two
requests are **compatible** if their intervals do not overlap (one may start exactly when another finishes). Accept
as many mutually compatible requests as possible. This is the **activity selection** or **interval scheduling**
problem, and the [activity selection](../../greedy/activity-selection.md) reference page animates it.

### Which greedy rule?

Several rules suggest themselves. Sort the requests somehow and accept each one that is compatible with those
accepted so far. But sorted by what?

- **Earliest start first** fails: one long request $[0, 10)$ that starts first blocks $[1, 2)$ and $[3, 4)$. Greedy
  gets 1, the optimum is 2.
- **Shortest first** fails: $[0, 5)$, $[4, 7)$, $[6, 11)$. The shortest, $[4, 7)$, overlaps both others. Greedy gets
  1, the optimum 2.
- **Fewest conflicts first** sounds clever, but Kleinberg and Tardos draw a small example where it fails too.
- **Earliest finish first** works. The intuition: the request that finishes first leaves the hall free as early as
  possible for everything else.

### Trace

The program's example is the one in CLRS, eleven requests, listed by finish time in Figure 12.1.

<figure class="mars-fig" markdown="0">
<svg viewBox="0 0 640 315" role="img" aria-label="Eleven activities drawn as horizontal bars on a time line from 0 to 16, sorted by finish time: a from 1 to 4, b 3 to 5, c 0 to 6, d 5 to 7, e 3 to 9, f 5 to 9, g 6 to 10, h 8 to 11, i 8 to 12, j 2 to 14, k 12 to 16. The bars a, d, h and k are highlighted as the greedy choice.">
<g stroke="currentColor" stroke-width="1">
<rect x="94" y="14" width="102" height="14" fill="#7ccf9a"/>
<rect x="162" y="38" width="68" height="14" fill="#9cc9ea" fill-opacity="0.5"/>
<rect x="60" y="62" width="204" height="14" fill="#9cc9ea" fill-opacity="0.5"/>
<rect x="230" y="86" width="68" height="14" fill="#7ccf9a"/>
<rect x="162" y="110" width="204" height="14" fill="#9cc9ea" fill-opacity="0.5"/>
<rect x="230" y="134" width="136" height="14" fill="#9cc9ea" fill-opacity="0.5"/>
<rect x="264" y="158" width="136" height="14" fill="#9cc9ea" fill-opacity="0.5"/>
<rect x="332" y="182" width="102" height="14" fill="#7ccf9a"/>
<rect x="332" y="206" width="136" height="14" fill="#9cc9ea" fill-opacity="0.5"/>
<rect x="128" y="230" width="408" height="14" fill="#9cc9ea" fill-opacity="0.5"/>
<rect x="468" y="254" width="136" height="14" fill="#7ccf9a"/>
</g>
<g font-size="13" fill="currentColor" text-anchor="end" font-family="monospace">
<text x="48" y="26">a</text>
<text x="48" y="50">b</text>
<text x="48" y="74">c</text>
<text x="48" y="98">d</text>
<text x="48" y="122">e</text>
<text x="48" y="146">f</text>
<text x="48" y="170">g</text>
<text x="48" y="194">h</text>
<text x="48" y="218">i</text>
<text x="48" y="242">j</text>
<text x="48" y="266">k</text>
</g>
<line x1="60" y1="284" x2="604" y2="284" stroke="currentColor" stroke-width="1.2"/>
<g stroke="currentColor" stroke-width="1">
<line x1="60" y1="280" x2="60" y2="288"/>
<line x1="128" y1="280" x2="128" y2="288"/>
<line x1="196" y1="280" x2="196" y2="288"/>
<line x1="264" y1="280" x2="264" y2="288"/>
<line x1="332" y1="280" x2="332" y2="288"/>
<line x1="400" y1="280" x2="400" y2="288"/>
<line x1="468" y1="280" x2="468" y2="288"/>
<line x1="536" y1="280" x2="536" y2="288"/>
<line x1="604" y1="280" x2="604" y2="288"/>
</g>
<g font-size="12" fill="currentColor" text-anchor="middle">
<text x="60" y="303">0</text>
<text x="128" y="303">2</text>
<text x="196" y="303">4</text>
<text x="264" y="303">6</text>
<text x="332" y="303">8</text>
<text x="400" y="303">10</text>
<text x="468" y="303">12</text>
<text x="536" y="303">14</text>
<text x="604" y="303">16</text>
</g>
</svg>
<figcaption>Figure 12.1. Eleven requests sorted by finish time. Earliest finish first accepts the green ones, a, d, h and k: each is the first to finish among those that start after the last accepted one ends.</figcaption>
</figure>

| request | start | finish | last accepted finish | compatible? | accepted so far |
|---|---|---|---|---|---|
| a | 1 | 4 | none | yes | a |
| b | 3 | 5 | 4 | no (3 < 4) | a |
| c | 0 | 6 | 4 | no | a |
| d | 5 | 7 | 4 | yes | a, d |
| e | 3 | 9 | 7 | no | a, d |
| f | 5 | 9 | 7 | no | a, d |
| g | 6 | 10 | 7 | no | a, d |
| h | 8 | 11 | 7 | yes | a, d, h |
| i | 8 | 12 | 11 | no | a, d, h |
| j | 2 | 14 | 11 | no | a, d, h |
| k | 12 | 16 | 11 | yes | a, d, h, k |

Four requests. Other sets of four exist (for example b, d, h, k), but none of five, as the proof will show.

### Proof 1: greedy stays ahead

Let greedy accept $g_1, g_2, \dots, g_k$ in order, and let $o_1, o_2, \dots, o_m$ be any optimal compatible set,
sorted by finish time. Since the $o$'s are compatible and sorted, each starts after the previous one finishes. Write
$f(x)$ for the finish time of request $x$.

**Lemma (greedy stays ahead).** For every $r \le \min(k, m)$, $f(g_r) \le f(o_r)$.

*Proof* by induction on $r$. For $r = 1$, greedy picks the request with the earliest finish of all, so
$f(g_1) \le f(o_1)$. Suppose $f(g_{r-1}) \le f(o_{r-1})$. Request $o_r$ starts after $o_{r-1}$ finishes, so
$s(o_r) \ge f(o_{r-1}) \ge f(g_{r-1})$: when greedy chose its $r$-th request, $o_r$ was compatible with everything
greedy had accepted, and so was available. Greedy picked the available request with the earliest finish, so
$f(g_r) \le f(o_r)$. $\square$

**Theorem.** Earliest finish first accepts an optimal number of requests: $k = m$.

*Proof.* Suppose $k < m$. By the lemma, $f(g_k) \le f(o_k)$, and $o_{k+1}$ starts after $f(o_k)$, hence after
$f(g_k)$. So $o_{k+1}$ was compatible with all of greedy's choices, and greedy, which only stops when nothing
compatible remains, would have accepted something more. Contradiction. $\square$

<figure class="mars-fig" markdown="0">
<svg viewBox="0 0 640 215" role="img" aria-label="Greedy stays ahead. Top row: greedy's choices g1, g2, g3. Bottom row: an optimal schedule o1, o2, o3, o4. Dashed lines show each greedy request finishing no later than the optimal request with the same index. o4 starts after o3 finishes, hence after g3, so greedy could have taken it.">
<g font-size="13" fill="currentColor">
<text x="20" y="62">greedy</text>
<text x="20" y="142">optimal</text>
</g>
<g stroke="currentColor" stroke-width="1.2">
<rect x="90" y="45" width="90" height="26" rx="4" fill="#7ccf9a"/>
<rect x="200" y="45" width="90" height="26" rx="4" fill="#7ccf9a"/>
<rect x="310" y="45" width="100" height="26" rx="4" fill="#7ccf9a"/>
<rect x="80" y="125" width="130" height="26" rx="4" fill="#9cc9ea"/>
<rect x="225" y="125" width="105" height="26" rx="4" fill="#9cc9ea"/>
<rect x="340" y="125" width="120" height="26" rx="4" fill="#9cc9ea"/>
<rect x="480" y="125" width="110" height="26" rx="4" fill="#eea66f"/>
</g>
<g font-size="13" fill="currentColor" text-anchor="middle" font-family="monospace">
<text x="135" y="63">g1</text>
<text x="245" y="63">g2</text>
<text x="360" y="63">g3</text>
<text x="145" y="143">o1</text>
<text x="277" y="143">o2</text>
<text x="400" y="143">o3</text>
<text x="535" y="143">o4</text>
</g>
<g stroke="currentColor" stroke-width="1" stroke-dasharray="4 3">
<line x1="180" y1="30" x2="180" y2="165"/>
<line x1="290" y1="30" x2="290" y2="165"/>
<line x1="410" y1="30" x2="410" y2="165"/>
<line x1="210" y1="110" x2="210" y2="165"/>
<line x1="330" y1="110" x2="330" y2="165"/>
<line x1="460" y1="110" x2="460" y2="165"/>
</g>
<g font-size="12" fill="currentColor" text-anchor="middle">
<text x="180" y="24">f(g1)</text>
<text x="290" y="24">f(g2)</text>
<text x="410" y="24">f(g3)</text>
<text x="215" y="180">f(o1)</text>
<text x="335" y="180">f(o2)</text>
<text x="465" y="180">f(o3)</text>
<text x="320" y="205">if o4 existed, it would start after f(o3) ≥ f(g3), so greedy could take it</text>
</g>
</svg>
<figcaption>Figure 12.2. Greedy stays ahead: the r-th greedy request finishes no later than the r-th request of any optimal schedule, so an optimal schedule can never fit in an extra request after greedy stops.</figcaption>
</figure>

### Proof 2: the exchange argument

The same theorem can be proved by exchanging. Let $O$ be an optimal set, sorted by finish time, and suppose its first
request $o_1$ is not $g_1$. Replace $o_1$ by $g_1$. Since $f(g_1) \le f(o_1)$, and every other request of $O$ starts
after $f(o_1)$, they all start after $f(g_1)$ too: the new set is still compatible and has the same size, so it is
also optimal. So **some optimal solution contains the greedy choice $g_1$** (the greedy choice property). Remove
$g_1$ and every request that overlaps it: what is left is a smaller instance of the same problem (optimal
substructure), on which greedy makes the same choices it made before, and induction on the number of requests
finishes the proof.

**Running time.** Sorting by finish time costs $O(n \log n)$; the scan is $O(n)$. If the requests come already
sorted, the whole algorithm is linear.

### A cousin: interval partitioning

Now suppose you must accept **every** request and want the fewest halls. Sort by **start** time, and put each request
in any hall that is free at its start, opening a new hall only when none is. Keep the halls' finish times in a
min-heap so that "is any hall free?" is one look at the top. The number of halls opened equals the **depth**, the
largest number of requests that overlap at one moment, and no schedule can use fewer than the depth, so this is
optimal. Exercise 8 asks you to write it.

## 12.3 Scheduling to minimise lateness

One machine (or one antenna, or one person) has $n$ jobs to do. Job $i$ takes $t_i$ units of time and has a deadline
$d_i$. The machine does one job at a time, starting at time 0. If job $i$ finishes at time $c_i$, its **lateness** is
$\ell_i = \max(0, c_i - d_i)$. Find an order that makes the **maximum lateness** $L = \max_i \ell_i$ as small as
possible.

There is no choosing here, only ordering: every job is done. The greedy rule that works is perhaps the most natural
one of all, and also the one people use with homework: **earliest deadline first** (EDF). It ignores the lengths
completely.

### Trace

The program's six jobs come from Kleinberg and Tardos, given here in a scrambled order:

| job | length $t$ | deadline $d$ | EDF start | finish $c$ | lateness |
|---|---|---|---|---|---|
| j1 | 3 | 6 | 0 | 3 | 0 |
| j2 | 2 | 8 | 3 | 5 | 0 |
| j4 | 4 | 9 | 5 | 9 | 0 |
| j3 | 1 | 9 | 9 | 10 | 1 |
| j5 | 3 | 14 | 10 | 13 | 0 |
| j6 | 2 | 15 | 13 | 15 | 0 |

Maximum lateness 1, and the program confirms by trying all $6! = 720$ orders that nothing does better. Shortest job
first, which sounds sensible, gets 6: it leaves the long job j4, deadline 9, to the very end.

### Proof by exchanging inversions

Call a pair of jobs an **inversion** of a schedule if the job with the later deadline is done first, the same idea
as in [Chapter 11](11-Divide-and-Conquer.md). EDF schedules have no inversions and no **idle time** (gaps when the
machine waits).

**Lemma 1.** All schedules with no inversions and no idle time have the same maximum lateness.

*Proof.* They can differ only in the order of jobs with equal deadlines, which are done one after another in a
block. The last job of the block finishes at the same time whichever order is used, and it has the largest lateness
within the block, since all share one deadline. $\square$

**Lemma 2.** Some optimal schedule has no idle time. (Removing a gap moves later jobs earlier, which cannot increase
any lateness.)

**Lemma 3.** If a schedule with no idle time has an inversion, it has an inversion between two **adjacent** jobs.

*Proof.* If no two adjacent jobs were inverted, the deadlines would be non-decreasing along the schedule, and then no
pair at all is inverted. $\square$

**Lemma 4.** Swapping an adjacent inverted pair does not increase the maximum lateness, and it reduces the number of
inversions by exactly one.

*Proof.* Let $i$ be done immediately before $j$, with $d_i > d_j$. Swapping them changes only their own finish
times; every other job finishes when it did. Let $c$ be the time at which the second of the two finishes, before and
after the swap (they occupy the same block of time). Before the swap, $j$ finished at $c$, with lateness
$\max(0, c - d_j)$. After the swap, $j$ finishes earlier, so its lateness does not rise; and $i$ finishes at $c$ with
lateness $\max(0, c - d_i) \le \max(0, c - d_j)$ since $d_i > d_j$. So neither new lateness exceeds the old lateness
of $j$, and the maximum does not increase. The relative order of every other pair is unchanged, so exactly one
inversion disappears. $\square$

**Theorem.** Earliest deadline first minimises the maximum lateness.

*Proof.* Take an optimal schedule with no idle time (Lemma 2). While it has an inversion, swap an adjacent inverted
pair (Lemma 3); by Lemma 4 it stays optimal, and since the number of inversions drops each time, this stops, with an
optimal schedule having no inversions and no idle time. By Lemma 1 its maximum lateness equals that of the EDF
schedule. So EDF is optimal. $\square$

This is the exchange argument in its purest form: transform any optimal solution into the greedy one, one harmless
swap at a time. EDF is used for real-time scheduling on computers, where tasks with deadlines share one processor;
Liu and Layland analysed it in 1973 in "Scheduling algorithms for multiprogramming in a hard-real-time environment".

## 12.4 Huffman coding

A text file stores each character in a fixed number of bits, for example 8 in ASCII. But in English, "e" is far more
common than "z". Could we give common characters **shorter** codes and rare ones longer, and so use fewer bits in
total? Morse code does this: "E" is a single dot. The question is how to choose the codes so that the total is as
small as possible, and so that the bit stream can still be split back into characters.

### Prefix codes are trees

If codes have different lengths, how do you know where one ends? Use a **prefix code**: no codeword is a prefix of
another. Then decoding is unambiguous: read bits until they spell a codeword; that must be the character, because no
longer codeword starts the same way.

Every binary prefix code is a **binary tree**: start at the root, go left for 0 and right for 1, and put each
character at a leaf. The path to a leaf spells its codeword, and because characters are only at leaves, no codeword
is a prefix of another. Conversely, every such tree gives a prefix code.

If character $c$ appears $f(c)$ times (its **frequency** or **weight**) and its leaf is at depth $d_T(c)$, the total
length of the encoded text is

$$
B(T) = \sum_{c} f(c)\, d_T(c),
$$

the **cost** of the tree. We want a tree of minimum cost: an **optimal prefix code**.

### Huffman's algorithm

David Huffman's 1952 algorithm builds the tree from the bottom up:

1. Make each character a one-node tree with its weight.
2. Repeat until one tree is left: take the **two lightest** trees, join them under a new root whose weight is the
   sum of theirs.

A min-priority queue ([Chapter 9](09-Heaps-and-Priority-Queues.md),
[binary heap](../../data-structures/binary-heap.md)) holds the trees. The [Huffman](../../greedy/huffman.md) reference
page animates it.

```python
--8<-- "books/algorithms/ch12_huffman.py"
```

```
merges (lighter, heavier): [(5, 9), (12, 13), (14, 16), (25, 30), (45, 55)]
  a: weight 45  code 0
  b: weight 13  code 101
  c: weight 12  code 100
  d: weight 16  code 111
  e: weight  9  code 1101
  f: weight  5  code 1100
total bits for 100 symbols: 224  (fixed 3-bit code: 300)

'abracadabra alakazam': 55 bits, 2.750 bits per symbol, entropy 2.695
decodes back correctly: True
Huffman cost equals exhaustive optimum on the 6-symbol example: True
```

### Trace

The weights are CLRS's: a 45, b 13, c 12, d 16, e 9, f 5 (say, thousands of occurrences in a file of 100 thousand
characters).

| step | queue before (weights) | merge | new tree |
|---|---|---|---|
| 1 | 5, 9, 12, 13, 16, 45 | f 5 + e 9 | 14 |
| 2 | 12, 13, 14, 16, 45 | c 12 + b 13 | 25 |
| 3 | 14, 16, 25, 45 | (f e) 14 + d 16 | 30 |
| 4 | 25, 30, 45 | 25 + 30 | 55 |
| 5 | 45, 55 | a 45 + 55 | 100 |

<figure class="mars-fig" markdown="0">
<svg viewBox="0 0 640 350" role="img" aria-label="The Huffman tree for weights a 45, b 13, c 12, d 16, e 9, f 5. The root 100 has a 45 on the 0 side and an internal node 55 on the 1 side. 55 has children 25 and 30. 25 has leaves c 12 and b 13. 30 has an internal node 14 and leaf d 16. 14 has leaves f 5 and e 9. Codewords: a 0, c 100, b 101, d 111, f 1100, e 1101.">
<g stroke="currentColor" stroke-width="1.3">
<line x1="320" y1="30" x2="160" y2="100"/>
<line x1="320" y1="30" x2="460" y2="100"/>
<line x1="460" y1="100" x2="350" y2="170"/>
<line x1="460" y1="100" x2="560" y2="170"/>
<line x1="350" y1="170" x2="290" y2="240"/>
<line x1="350" y1="170" x2="400" y2="240"/>
<line x1="560" y1="170" x2="510" y2="240"/>
<line x1="560" y1="170" x2="600" y2="240"/>
<line x1="510" y1="240" x2="460" y2="305"/>
<line x1="510" y1="240" x2="560" y2="305"/>
</g>
<g>
<circle cx="320" cy="30" r="18" style="fill:var(--md-default-bg-color)"/>
<circle cx="460" cy="100" r="18" style="fill:var(--md-default-bg-color)"/>
<circle cx="350" cy="170" r="18" style="fill:var(--md-default-bg-color)"/>
<circle cx="560" cy="170" r="18" style="fill:var(--md-default-bg-color)"/>
<circle cx="510" cy="240" r="18" style="fill:var(--md-default-bg-color)"/>
<rect x="132" y="85" width="56" height="30" rx="5" style="fill:var(--md-default-bg-color)"/>
<rect x="262" y="225" width="56" height="30" rx="5" style="fill:var(--md-default-bg-color)"/>
<rect x="372" y="225" width="56" height="30" rx="5" style="fill:var(--md-default-bg-color)"/>
<rect x="572" y="225" width="56" height="30" rx="5" style="fill:var(--md-default-bg-color)"/>
<rect x="432" y="290" width="56" height="30" rx="5" style="fill:var(--md-default-bg-color)"/>
<rect x="532" y="290" width="56" height="30" rx="5" style="fill:var(--md-default-bg-color)"/>
</g>
<g stroke="currentColor" stroke-width="1.3">
<circle cx="320" cy="30" r="18" fill="#9cc9ea" fill-opacity="0.45"/>
<circle cx="460" cy="100" r="18" fill="#9cc9ea" fill-opacity="0.45"/>
<circle cx="350" cy="170" r="18" fill="#9cc9ea" fill-opacity="0.45"/>
<circle cx="560" cy="170" r="18" fill="#9cc9ea" fill-opacity="0.45"/>
<circle cx="510" cy="240" r="18" fill="#9cc9ea" fill-opacity="0.45"/>
<rect x="132" y="85" width="56" height="30" rx="5" fill="#7ccf9a" fill-opacity="0.5"/>
<rect x="262" y="225" width="56" height="30" rx="5" fill="#7ccf9a" fill-opacity="0.5"/>
<rect x="372" y="225" width="56" height="30" rx="5" fill="#7ccf9a" fill-opacity="0.5"/>
<rect x="572" y="225" width="56" height="30" rx="5" fill="#7ccf9a" fill-opacity="0.5"/>
<rect x="432" y="290" width="56" height="30" rx="5" fill="#7ccf9a" fill-opacity="0.5"/>
<rect x="532" y="290" width="56" height="30" rx="5" fill="#7ccf9a" fill-opacity="0.5"/>
</g>
<g font-size="13" fill="currentColor" text-anchor="middle" font-family="monospace">
<text x="320" y="35">100</text>
<text x="460" y="105">55</text>
<text x="350" y="175">25</text>
<text x="560" y="175">30</text>
<text x="510" y="245">14</text>
<text x="160" y="105">a:45</text>
<text x="290" y="245">c:12</text>
<text x="400" y="245">b:13</text>
<text x="600" y="245">d:16</text>
<text x="460" y="310">f:5</text>
<text x="560" y="310">e:9</text>
</g>
<g font-size="12" fill="currentColor" text-anchor="middle">
<text x="232" y="58">0</text>
<text x="398" y="58">1</text>
<text x="396" y="130">0</text>
<text x="520" y="130">1</text>
<text x="311" y="200">0</text>
<text x="388" y="200">1</text>
<text x="524" y="203">0</text>
<text x="592" y="203">1</text>
<text x="474" y="276">0</text>
<text x="546" y="276">1</text>
</g>
<g font-size="12" fill="currentColor" text-anchor="middle" font-family="monospace">
<text x="160" y="132">0</text>
<text x="290" y="272">100</text>
<text x="400" y="272">101</text>
<text x="600" y="272">111</text>
<text x="460" y="337">1100</text>
<text x="560" y="337">1101</text>
</g>
</svg>
<figcaption>Figure 12.3. The Huffman tree for the weights of the trace. Leaves (green) carry the characters, internal nodes (blue) the merged weights; reading 0 for left and 1 for right gives each codeword, printed under its leaf.</figcaption>
</figure>

The cost is $45 \cdot 1 + (12 + 13 + 16) \cdot 3 + (5 + 9) \cdot 4 = 45 + 123 + 56 = 224$ bits per hundred characters,
against 300 for a fixed 3-bit code: a saving of about 25 percent. A useful fact: the cost also equals the sum of the
weights of all internal nodes, $14 + 25 + 30 + 55 + 100 = 224$, because each internal node's weight is counted once for
every leaf below it, once per level.

### Why Huffman's algorithm is optimal

**Lemma 1 (full trees).** An optimal tree is **full**: every internal node has two children.

*Proof.* If a node had one child, delete it and move its subtree up a level. Every leaf below it gets shorter, and
the cost drops (or stays equal, if all those weights are zero). $\square$

**Lemma 2 (greedy choice).** Let $x$ and $y$ be two characters of smallest weight. There is an optimal tree in which
$x$ and $y$ are sibling leaves at the greatest depth.

*Proof.* Take an optimal tree $T$. It is full, so a deepest leaf has a sibling, which is also a leaf (anything below
it would be deeper); call these deepest siblings $a$ and $b$, with $f(a) \le f(b)$, and say $f(x) \le f(y)$. Since $x$
and $y$ are the lightest, $f(x) \le f(a)$ and $f(y) \le f(b)$. Swap $x$ with $a$. The cost changes by

$$
\begin{aligned}
B(T') - B(T) &= f(x) d(a) + f(a) d(x) - f(x) d(x) - f(a) d(a) \\
&= -\big(f(a) - f(x)\big)\big(d(a) - d(x)\big) \le 0,
\end{aligned}
$$

because $f(a) \ge f(x)$ and $d(a) \ge d(x)$ ($a$ is deepest). Swapping $y$ with $b$ likewise does not increase the
cost. The new tree is still optimal, and $x$, $y$ are deepest siblings. (If $x$ or $y$ was already one of $a$, $b$,
the same argument with one swap fewer works.) $\square$

The proof is an exchange argument with a picture: moving a heavier character up and a lighter one down never hurts.

**Lemma 3 (optimal substructure).** Replace $x$ and $y$ by a single new character $z$ with $f(z) = f(x) + f(y)$, giving
an alphabet $C'$. If $T'$ is an optimal tree for $C'$, then replacing the leaf $z$ in $T'$ by an internal node with
children $x$ and $y$ gives an optimal tree $T$ for the original alphabet $C$.

*Proof.* The depths of $x$ and $y$ in $T$ are $d_{T'}(z) + 1$, and everything else is unchanged, so

$$
B(T) = B(T') - f(z)\, d_{T'}(z) + \big(f(x) + f(y)\big)\big(d_{T'}(z) + 1\big) = B(T') + f(x) + f(y).
$$

Now suppose some tree $U$ for $C$ were cheaper than $T$. By Lemma 2 we may take $U$ with $x$, $y$ deepest siblings.
Merge them into $z$ to get a tree $U'$ for $C'$ with $B(U') = B(U) - f(x) - f(y) < B(T) - f(x) - f(y) = B(T')$,
contradicting the optimality of $T'$. $\square$

**Theorem (Huffman 1952).** Huffman's algorithm produces an optimal prefix code.

*Proof* by induction on the number of characters $n$. For $n = 2$, the tree with two leaves at depth 1 is optimal.
For $n > 2$, the algorithm first merges the two lightest characters $x$ and $y$, then runs on $C'$, producing (by
the induction hypothesis) an optimal tree for $C'$; Lemma 3 says that expanding $z$ back into $x$ and $y$ is optimal
for $C$, and that is exactly the tree the algorithm outputs. $\square$

The program double-checks the theorem on the six-character example by trying every possible merge order, not just
the two lightest, and finding nothing better than 224.

**Running time.** With a binary heap, $n - 1$ merges each cost $O(\log n)$: $O(n \log n)$ in total. If the weights
arrive sorted, two ordinary queues (one for the original leaves, one for merged trees, whose weights come out in
non-decreasing order) give $O(n)$.

### How good is "optimal"? Entropy

Claude Shannon's 1948 paper "A Mathematical Theory of Communication" defined the **entropy** of a source that emits
symbol $c$ with probability $p_c$:

$$
H = -\sum_c p_c \log_2 p_c \quad \text{bits per symbol}.
$$

His source coding theorem says no uniquely decodable code can average fewer than $H$ bits per symbol, and Huffman's
code averages less than $H + 1$. For "abracadabra alakazam" the program finds 2.750 bits per symbol against an entropy
of 2.695. The gap of up to one bit per symbol is the price of whole-bit codewords; **arithmetic coding** and
asymmetric numeral systems avoid it by coding many symbols together. (The proofs use the Kraft inequality,
$\sum_c 2^{-d(c)} \le 1$, which every prefix code satisfies; we state the theorem here without proof.)

### History and in practice

Huffman was a graduate student at MIT in Robert Fano's information theory course in 1951. As Huffman later told it,
students could write a term paper instead of taking the final exam, and the paper topic was to find the most
efficient binary code. Shannon and Fano had a top-down method (split the symbols into two groups of nearly equal
weight, recursively) that is good but not always optimal. Huffman, about to give up, found the bottom-up method and
proved it optimal. It was published as "A Method for the Construction of Minimum-Redundancy Codes" in the
*Proceedings of the IRE* in 1952.

Huffman codes are inside the DEFLATE format used by zip, gzip and PNG (after a dictionary step called LZ77) and in
baseline JPEG images. Python's `zlib` module implements DEFLATE.

## 12.5 Fractional knapsack vs 0/1 knapsack

A rover's sample bay can carry 50 grams. Three materials are available: 10 grams of a sample worth 60 points of
science value, 20 grams worth 100, and 30 grams worth 120. (The numbers are CLRS's.) What should go in?

That depends on a detail. If the samples are powders you can scoop any fraction of, this is the **fractional
knapsack** problem. If each must be taken whole or left, it is the **0/1 knapsack** problem. They look almost the
same; one is greedy-easy and the other is NP-hard.

```python
--8<-- "books/algorithms/ch12_knapsack_matroids.py"
```

```
fractional knapsack, capacity 50: (240.0, [('gold', 1.0), ('silver', 1.0), ('bronze', 0.6666666666666666)])
0/1 greedy by ratio:               (160, ['gold', 'silver'])
0/1 true optimum:                  (220, ('silver', 'bronze'))

forests (a matroid): greedy 39 [('D', 'E', 15), ('B', 'D', 9), ('B', 'C', 8), ('A', 'B', 7)]
                     best   39
matchings (not a matroid): greedy 3 [('Q', 'R', 3)]
                           best   (4, [('P', 'Q', 2), ('R', 'S', 2)])

greedy set cover: ['S1', 'S4', 'S5', 'S3']
smallest cover:   ['S3', 'S4', 'S5']
```

### Fractional: greedy by density

The **density** (value per gram) of the three items is 6, 5 and 4. Greedy fills the bay with the densest item first:
all 10 grams of the first (60), all 20 grams of the second (100), and 20 of the 30 grams of the third (two thirds of
120, which is 80). Total 240.

**Theorem.** Taking items in order of decreasing density, splitting only the last, is optimal for fractional
knapsack.

*Proof* (exchange). Number the items by decreasing density $v_1/w_1 \ge v_2/w_2 \ge \dots$. Let $x_i \in [0, 1]$ be
the fraction of item $i$ in an optimal solution, and let greedy's fractions be $g_i$. If they differ, let $i$ be the
first index with $x_i \ne g_i$. Greedy takes as much of item $i$ as fits, so $x_i < g_i$, and the optimum uses the
missing $(g_i - x_i) w_i$ grams on later items $j > i$ (or leaves them empty, which is no better). Move that much
weight from later items to item $i$: each gram moved changes the value by $v_i/w_i - v_j/w_j \ge 0$. The new solution
is no worse and agrees with greedy on one more index. Repeating gives greedy's solution with value at least the
optimum. $\square$

Sorting costs $O(n \log n)$. (It can even be done in $O(n)$ by finding the "critical" density with a linear-time
selection algorithm, [Chapter 6](06-Sorting-in-Linear-Time-and-Selection.md).)

### 0/1: greedy fails

Now the items must be whole. Greedy by density takes the 10-gram and 20-gram items (160) and then cannot fit the
30-gram item. But the 20-gram and 30-gram items together weigh exactly 50 and are worth 220. Greedy's mistake was the
same as with the coins: its first choice was good locally, but it left 20 grams of space that nothing else could use.

No simple greedy rule works for the 0/1 knapsack: it is NP-hard ([Chapter 22](22-NP-Completeness.md)), so no
polynomial-time algorithm is known for it at all. It can be solved in $O(nW)$ time by dynamic programming, where $W$ is
the capacity ([Chapter 13](13-Dynamic-Programming.md), and the [knapsack](../../dp/knapsack.md) reference page), and by
branch and bound ([Chapter 14](14-Backtracking-and-Branch-and-Bound.md)).

Greedy by density can even be arbitrarily bad: with capacity $W$, an item of weight 1 and value 2 (density 2) and an
item of weight $W$ and value $W$ (density 1), greedy takes the small item and then nothing fits, value 2 against $W$.
But a small repair helps: **take the better of greedy's answer and the single most valuable item**. That is at least
half the optimum. *Why:* let item $k$ be the first one greedy cannot fit. Items $1, \dots, k-1$ plus all of item $k$
are worth at least the fractional optimum (they overfill the bag with the densest items), which is at least the 0/1
optimum. So greedy's value plus $v_k$ is at least OPT, and the larger of the two is at least OPT/2. Better
approximations are in [Chapter 23](23-Approximation-and-Parameterized-Algorithms.md).

## 12.6 Matroids and the greedy theorem

*Level: advanced.*

We now have greedy successes (activity selection, Huffman, fractional knapsack) and failures (coins, 0/1 knapsack).
Is there a pattern that tells us in advance when greedy works? For one broad class of problems, yes, and the answer
is a single structural property.

### The generic greedy algorithm

Many problems have this form: there is a finite set $E$ of elements, each with a weight $w(e) > 0$; some subsets of
$E$ are **independent** (allowed); find an independent set of maximum total weight. The generic greedy algorithm is:

1. Sort the elements by decreasing weight.
2. Start with $S = \emptyset$. For each element $e$ in that order, if $S \cup \{e\}$ is independent, add $e$ to $S$.

Examples: $E$ = the edges of a graph, independent = forms no cycle (a **forest**); $E$ = the edges, independent =
no two edges share an endpoint (a **matching**); $E$ = vectors, independent = linearly independent.

### Matroids

A **matroid** is a pair $(E, \mathcal{I})$, where $\mathcal{I}$ is a family of subsets of $E$ called independent,
such that:

- **(M1)** $\emptyset$ is independent;
- **(M2) hereditary:** every subset of an independent set is independent;
- **(M3) exchange:** if $A$ and $B$ are independent and $|A| < |B|$, then some $b \in B \setminus A$ can be added to
  $A$ keeping it independent.

The word was coined by Hassler Whitney in 1935, in "On the abstract properties of linear dependence", as an
abstraction of linear independence ("matrix-oid"). The key examples:

- **Uniform matroid:** independent = at most $k$ elements. Exchange is obvious.
- **Linear matroid:** vectors, independent = linearly independent. Exchange is the Steinitz exchange lemma of linear
  algebra: if $|A| < |B|$, the span of $A$ cannot contain all of $B$ (dimensions), so some $b$ is outside it.
- **Graphic matroid:** edges of a graph, independent = forests. *Exchange:* a forest with $|A|$ edges on $n$ vertices
  has $n - |A|$ connected components (each edge joins two components into one). $B$ has fewer components, so some
  edge of $B$ joins two different components of $A$; adding it to $A$ makes no cycle.

Matchings are **not** a matroid. On the path $P - Q - R - S$, $A = \{QR\}$ and $B = \{PQ, RS\}$ are matchings with
$|A| < |B|$, but adding either edge of $B$ to $A$ creates a shared endpoint. And greedy fails there: with weights
$PQ = 2$, $QR = 3$, $RS = 2$ it takes $QR$ (3) and stops, while $\{PQ, RS\}$ weighs 4. The program shows exactly this.

A first consequence of the exchange property: **all maximal independent sets have the same size**. (If $A$ and $B$ are
maximal and $|A| < |B|$, exchange extends $A$, so it was not maximal.) Maximal independent sets are called **bases**;
in the graphic matroid of a connected graph they are the spanning trees, all with $n - 1$ edges.

### The theorem

**Theorem (Rado 1957, Edmonds 1971).** Let $(E, \mathcal{I})$ satisfy (M1) and (M2). Then the generic greedy algorithm
finds a maximum-weight independent set **for every choice of positive weights** if and only if (M3) holds, that is,
if and only if $(E, \mathcal{I})$ is a matroid.

*Proof that matroids make greedy optimal.* Let greedy choose $g_1, g_2, \dots, g_k$, in the order chosen, so
$w(g_1) \ge w(g_2) \ge \dots$. Greedy's set is a basis: an element it rejected could not be added to its set at that
time, and by (M2) cannot be added to the larger final set either. Let $O = \{o_1, \dots, o_m\}$ be a maximum-weight
independent set with $w(o_1) \ge w(o_2) \ge \dots$; extending $O$ to a basis only adds positive weight, so we may take
$O$ to be a basis, and then $m = k$.

We show $w(g_j) \ge w(o_j)$ for every $j$, which gives $w(G) \ge w(O)$. Suppose not, and let $j$ be the first index
with $w(g_j) < w(o_j)$. Apply exchange to $A = \{g_1, \dots, g_{j-1}\}$ and $B = \{o_1, \dots, o_j\}$: there is some
$o_i \in B \setminus A$ with $A \cup \{o_i\}$ independent, and $w(o_i) \ge w(o_j) > w(g_j)$. So greedy examined $o_i$
before $g_j$. At that moment greedy's set was a subset of $A$, and adding $o_i$ to it gives a subset of
$A \cup \{o_i\}$, which is independent by (M2). So greedy would have taken $o_i$, putting it in $A$; but
$o_i \notin A$. Contradiction. $\square$

*Proof that greedy's success forces exchange.* Suppose (M3) fails: there are independent $A$, $B$ with $|A| < |B|$
and no $b \in B \setminus A$ such that $A \cup \{b\}$ is independent. By (M2) we may shrink $B$ to exactly
$|A| + 1$ elements, keeping the failure. Let $p = |A|$ and define weights: $p + 2$ on the elements of $A$, $p + 1$
on the elements of $B \setminus A$, and a tiny $\varepsilon > 0$ elsewhere. Greedy first takes all of $A$ (they are
the heaviest, and $A$ is independent, so by (M2) each prefix is too). Then it cannot add any element of
$B \setminus A$. So its total is at most $p(p + 2) + \varepsilon |E|$. But $B$ alone weighs at least
$(p + 1)(p + 1) = p^2 + 2p + 1$. For $\varepsilon < 1/|E|$, greedy loses. $\square$

So for a hereditary family, **greedy works for all weights exactly when the family is a matroid.** That is a
remarkable converse: if you suspect greedy and can find two independent sets violating exchange, you can build
weights that defeat it.

### Using the theorem

- **Maximum spanning forest.** The graphic matroid plus the theorem says: sort edges by decreasing weight, keep each
  edge that makes no cycle. That is Kruskal's algorithm with the sort order reversed. The program finds weight 39 on a five-vertex
  graph, and brute force over all edge subsets agrees.
- **Minimum spanning tree.** All bases have the same size $n - 1$, so minimising the total weight of a basis is the
  same as maximising $\sum (C - w(e))$ for a large constant $C$. That turns into greedy by **increasing** weight:
  exactly Kruskal's algorithm (12.7).
- **Scheduling unit jobs with deadlines and penalties.** Jobs of unit length, each with a deadline and a penalty for
  missing it: the sets of jobs that can all meet their deadlines form a matroid, so greedy by decreasing penalty is
  optimal (CLRS, 3rd edition, section 16.5, works this example).

Not every greedy algorithm is a matroid in disguise: Huffman coding and activity selection are not. There are
generalisations (**greedoids**, introduced by Bernhard Korte and László Lovász in 1981) that cover more cases, but no
single theory explains every greedy success. Edmonds's work also showed that the intersection of two matroids (for
example, bipartite matchings) is still solvable in polynomial time, though not by plain greedy.

## 12.7 Minimum spanning trees preview; set cover greedy as approximation

### The cut property

Several research stations on a plain must be connected by cables, and each possible cable has a cost. Connect them
all as cheaply as possible. Since a cycle would contain a removable cable, the answer is a **spanning tree** (a set of
edges connecting all vertices with no cycle) of minimum total weight: a **minimum spanning tree** (MST).

A **cut** of a graph is a split of its vertices into two non-empty groups $S$ and $V \setminus S$; an edge **crosses**
the cut if it has one end in each group.

**Cut property.** Assume all edge weights are distinct. For any cut, the lightest edge crossing it belongs to every
minimum spanning tree.

*Proof* (exchange). Let $e$ be the lightest edge crossing the cut $(S, V \setminus S)$, and suppose a minimum spanning
tree $T$ does not contain $e = \{u, v\}$. $T$ has a path from $u$ to $v$; since $u \in S$ and $v \notin S$, the path
crosses the cut at some edge $e'$. Swap: $T' = T - e' + e$. Removing $e'$ splits $T$ into two pieces, one containing
$u$ and one containing $v$, and $e$ reconnects them, so $T'$ is a spanning tree. Its weight is
$w(T) - w(e') + w(e) < w(T)$ because $e$ is lighter. That contradicts the minimality of $T$. $\square$

Every MST algorithm is a way of choosing cuts:

- **Kruskal** (1956) sorts edges by increasing weight and adds each edge that joins two different components, using
  union-find ([Chapter 10](10-Union-Find-and-Range-Queries.md)). The edge joins component $C$ to another; it is the
  lightest edge crossing the cut ($C$, rest), since any lighter crossing edge would have been examined and added
  earlier. Reference page: [Kruskal](../../graphs/kruskal.md).
- **Prim** grows one tree from a start vertex, always adding the lightest edge leaving it: the cut is (tree, rest).
  Reference page: [Prim](../../graphs/prim.md).

Both are greedy, both are justified by the cut property, and both run in $O(m \log n)$ on a graph with $m$ edges.
[Chapter 17](17-Spanning-Trees-Flows-and-Matching.md) proves them in full, handles equal weights, and adds
Borůvka's algorithm. [Dijkstra's shortest-path algorithm](../../graphs/dijkstra.md) is greedy in the same spirit
([Chapter 16](16-Shortest-Paths.md)).

### Greedy when the optimum is out of reach: set cover

Some problems are so hard that no fast algorithm is expected to find the optimum (they are NP-hard,
[Chapter 22](22-NP-Completeness.md)). Greedy can still give answers that are **provably close**. The classic example
is **set cover**: given a universe $U$ of $n$ elements and a family of subsets whose union is $U$, choose as few
subsets as possible that together cover $U$. Think of placing as few relay antennas as possible, where each candidate
site covers some set of locations.

The greedy rule: repeatedly choose the subset that covers the most still-uncovered elements.

In the program's example the universe is $\{1, \dots, 12\}$:

| step | uncovered before | new elements covered by each set | choice |
|---|---|---|---|
| 1 | 1 to 12 | S1: 6, S2: 4, S3: 4, S4: 5, S5: 4, S6: 2 | S1 |
| 2 | 7, 8, 9, 10, 11, 12 | S2: 2, S3: 2, S4: 3, S5: 2, S6: 2 | S4 |
| 3 | 9, 10, 12 | S2: 1, S3: 1, S5: 2, S6: 1 | S5 |
| 4 | 10 | S3: 1, S6: 1 | S3 |

Greedy uses 4 sets. The optimum is 3: $S_3 \cup S_4 \cup S_5$ is exactly $\{1, \dots, 12\}$. Greedy's first choice,
the big set $S_1$, was a trap: every one of its elements is also covered by $S_3$, $S_4$ or $S_5$.

**Theorem (Johnson 1974, Lovász 1975, Chvátal 1979).** Greedy set cover uses at most $H_n \cdot \mathrm{OPT}$ sets, where
$H_n = 1 + \tfrac12 + \dots + \tfrac1n \le 1 + \ln n$ is the $n$-th harmonic number.

*Idea of the proof.* Whenever $k$ elements remain uncovered, the optimal cover's OPT sets cover them, so one of those
sets covers at least $k / \mathrm{OPT}$ of them, and greedy's choice covers at least as many. So each greedy step
shrinks the uncovered count by a factor of at least $1 - 1/\mathrm{OPT}$, and after about $\mathrm{OPT} \ln n$ steps
nothing is left. The full proof, which charges each element a price, is in
[Chapter 23](23-Approximation-and-Parameterized-Algorithms.md), along with the fact that doing much better than
$\ln n$ is believed impossible in polynomial time.

So greedy has two lives: an exact algorithm when the structure is right (matroids, exchange arguments), and an
approximation algorithm, with a guarantee, when the problem is too hard to solve exactly.

## Check yourself

??? question "1. For coins 1, 7 and 10, find the smallest amount where greedy is not optimal."

    14: greedy gives $10 + 1 + 1 + 1 + 1$ (five coins), but $7 + 7$ uses two. Checking smaller amounts (the program's
    `first_counterexample([1, 7, 10])` does this) shows greedy is optimal below 14, and by Kozen and Zaks we only had
    to search below $10 + 7 = 17$.

??? question "2. Find three intervals for which 'shortest request first' accepts fewer requests than the optimum."

    $[0, 5)$, $[4, 7)$, $[6, 11)$. The shortest, $[4, 7)$, is accepted first and overlaps both others, so greedy
    accepts 1. The optimum accepts $[0, 5)$ and $[6, 11)$, which is 2.

??? question "3. Show that 'latest start first' is also optimal for activity selection."

    Reverse time: replace each interval $[s, f)$ by $[-f, -s)$. Compatibility is unchanged, and "latest start" becomes
    "earliest finish" in the reversed problem, which we proved optimal. So the number of requests accepted is the
    same as the optimum.

??? question "4. Build a Huffman code for weights A 1, B 1, C 2, D 3, E 5. What is its cost? What shape is the tree?"

    Merges: $1 + 1 = 2$; $2 + 2 = 4$; $3 + 4 = 7$; $5 + 7 = 12$. Codes: E 0, D 10, C 110, A 1110, B 1111. Cost
    $5 \cdot 1 + 3 \cdot 2 + 2 \cdot 3 + 1 \cdot 4 + 1 \cdot 4 = 25$, which is also $2 + 4 + 7 + 12 = 25$ (sum of internal
    weights). The tree is a single long spine: Fibonacci-like weights make each merged tree the lightest again, so
    the code has maximum depth $n - 1$.

??? question "5. Prove that in an optimal prefix code, if f(x) > f(y) then the codeword of x is no longer than that of y."

    If $d(x) > d(y)$, swap the two leaves. The cost changes by
    $f(x) d(y) + f(y) d(x) - f(x) d(x) - f(y) d(y) = -(f(x) - f(y))(d(x) - d(y)) < 0$, so the tree was not optimal.

??? question "6. Capacity 10; items (weight, value): p (5, 30), q (4, 28), r (6, 30), s (3, 9). Solve the fractional knapsack, then the 0/1 knapsack."

    Densities: q 7, p 6, r 5, s 3. Fractional: all of q (4, 28), all of p (9 grams, 58), then 1 gram of r, which is
    $30/6 = 5$. Total 63. For 0/1, greedy by density takes q and p (58) and nothing else fits; the optimum is also 58
    (q and r, 10 grams, or q and p). Here greedy happens to tie, but the fractional value 63 shows that splitting
    helps.

??? question "7. Is 'every subset of at most k elements' a matroid? What does the greedy theorem say about it?"

    Yes, the uniform matroid: subsets of small sets are small (M2), and if $|A| < |B| \le k$, any element of
    $B \setminus A$ can be added to $A$ without exceeding $k$ (M3). The theorem says greedy finds the maximum-weight
    set of at most $k$ elements: it takes the $k$ heaviest, which is obviously right, a sanity check on the
    theorem.

??? question "8. Write code: interval partitioning. Given intervals, use the fewest rooms so that no room has two overlapping intervals."

    Sort by start; keep a min-heap of the rooms' finish times. If the earliest-finishing room is free when the next
    interval starts, reuse it; otherwise open a room.

    ```python
    import heapq

    def rooms_needed(intervals):
        finish_times = []                     # one entry per open room
        for start, finish in sorted(intervals):
            if finish_times and finish_times[0] <= start:
                heapq.heapreplace(finish_times, finish)   # reuse the room that frees first
            else:
                heapq.heappush(finish_times, finish)      # open a new room
        return len(finish_times)

    print(rooms_needed([(9, 10.5), (9, 12.5), (9, 10.5), (11, 12.5), (11, 14),
                        (13, 14.5), (13, 14.5), (14, 16.5), (15, 16.5), (15, 16.5)]))   # 3
    ```

    Optimal because a new room is opened only when every room is busy at that start time, so at that moment the
    number of overlapping intervals equals the number of rooms; no schedule can use fewer rooms than the maximum
    overlap. Time $O(n \log n)$. (Checked against the maximum overlap on 300 random inputs.)

??? question "9. Show that 'smallest slack first' (slack = d - t) fails for minimising maximum lateness."

    Job 1: $t = 1$, $d = 2$ (slack 1). Job 2: $t = 10$, $d = 10$ (slack 0). Slack-first runs job 2 first, finishing at
    10, then job 1 at 11, lateness 9. Earliest deadline first runs job 1 (finishes at 1) then job 2 (finishes at 11,
    lateness 1). Maximum lateness 9 against 1.

??? question "10. Prove the exchange property for forests directly from the component count."

    A forest with $k$ edges on $n$ vertices has exactly $n - k$ components: start with $n$ isolated vertices, and each
    edge, joining two different trees, reduces the count by one. If $|A| < |B|$, then $B$ has fewer components than
    $A$. If every edge of $B$ had both ends in the same component of $A$, each component of $B$ would sit inside one
    component of $A$, so $B$ would have at least as many components as $A$. So some edge of $B$ joins two components
    of $A$, and adding it to $A$ creates no cycle.

??? question "11. A greedy for 0/1 knapsack sorts by value alone. Give an example where it does badly, and explain why taking the better of 'density greedy' and 'best single item' is never worse than half the optimum."

    Capacity 10; one item of weight 10 and value 11, and ten items of weight 1 and value 10 each. By value, greedy
    takes the big item: 11. The optimum takes the ten small ones: 100. For the half bound: let $k$ be the first item,
    in density order, that density greedy cannot fit. Items $1..k$ together are worth at least the fractional
    optimum, which is at least the 0/1 optimum OPT. Greedy has items $1..k-1$ (at least), and the best single item is
    worth at least $v_k$, so their sum is at least OPT and the larger is at least OPT/2.

## What you learned

- A greedy algorithm makes the locally best choice and never revisits it; it must be proved, and often it is wrong
  (coins 1, 3, 4; 0/1 knapsack; matchings).
- Two proof tools: **greedy stays ahead** (activity selection) and the **exchange argument** (lateness, Huffman,
  fractional knapsack, the cut property).
- Earliest finish first maximises compatible intervals; earliest deadline first minimises maximum lateness.
- Huffman's bottom-up merging of the two lightest trees gives an optimal prefix code, within one bit per symbol of
  Shannon's entropy.
- Greedy is optimal for every weighting exactly on matroids (Rado, Edmonds); forests form a matroid, which is why
  Kruskal works.
- When a problem is NP-hard, greedy can still give a guarantee: set cover within a factor $H_n \approx \ln n$.

**Next:** [Chapter 13](13-Dynamic-Programming.md), dynamic programming, which handles the problems greedy cannot by
trying every first choice and remembering the answers.

## Further reading

- J. Kleinberg and É. Tardos, *Algorithm Design*, 2005: chapter 4 (greedy stays ahead, exchange arguments, interval
  scheduling and partitioning, lateness, Huffman, MSTs).
- T. H. Cormen, C. E. Leiserson, R. L. Rivest and C. Stein, *Introduction to Algorithms*, 4th ed., 2022: chapter 15
  (greedy algorithms, Huffman codes); matroids are in the 3rd edition (2009), section 16.4.
- D. A. Huffman, "A Method for the Construction of Minimum-Redundancy Codes", *Proceedings of the IRE* 40(9), 1952.
- C. E. Shannon, "A Mathematical Theory of Communication", *Bell System Technical Journal*, 1948.
- R. Rado, "A note on independence functions", *Proceedings of the London Mathematical Society*, 1957; J. Edmonds,
  "Matroids and the greedy algorithm", *Mathematical Programming* 1, 1971; H. Whitney, "On the abstract properties of
  linear dependence", *American Journal of Mathematics*, 1935.
- D. Kozen and S. Zaks, "Optimal bounds for the change-making problem", *Theoretical Computer Science* 123, 1994;
  D. Pearson, "A polynomial-time algorithm for the change-making problem", *Operations Research Letters* 33, 2005.
- C. L. Liu and J. W. Layland, "Scheduling algorithms for multiprogramming in a hard-real-time environment",
  *Journal of the ACM* 20, 1973.
- V. Chvátal, "A greedy heuristic for the set-covering problem", *Mathematics of Operations Research* 4, 1979.
- J. Oxley, *Matroid Theory*, 2nd ed., 2011, for the full theory.
- On this site: [Activity selection](../../greedy/activity-selection.md), [Huffman coding](../../greedy/huffman.md),
  [Kruskal](../../graphs/kruskal.md), [Prim](../../graphs/prim.md), [Knapsack](../../dp/knapsack.md),
  [Coin change](../../dp/coin-change.md), [Chapter 11](11-Divide-and-Conquer.md), [Chapter 17](17-Spanning-Trees-Flows-and-Matching.md),
  [Chapter 23](23-Approximation-and-Parameterized-Algorithms.md).
