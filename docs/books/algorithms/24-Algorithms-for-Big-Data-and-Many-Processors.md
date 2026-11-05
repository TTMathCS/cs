# 24. Beyond the single machine

*Every algorithm so far assumed one processor that sees the whole input in advance, holds it in a memory where
every access costs the same, and runs alone. Real systems break each of these assumptions. Requests arrive one at a
time and must be answered before the next one comes; data streams past faster than it can be stored; it lives on
disks where reading one byte costs as much as reading thousands; the work is shared among many processors, or
among machines that can crash and whose messages are delayed. In this chapter you will meet the model of cost that
fits each situation, build the classic algorithm for it, and prove what it achieves: competitive ratios, error
bounds in tiny memory, counts of disk transfers, work and span, and the impossibility result at the heart of
distributed computing.*

!!! abstract "In this chapter"
    **You will learn:**

    - online algorithms and competitive analysis: ski rental, and paging with LRU, FIFO and Belady's optimum
    - streaming algorithms that use tiny memory: Misra-Gries, the count-min sketch and HyperLogLog
    - the I/O model: why disks change the cost of sorting and searching; external merge sort and B-trees
    - cache-oblivious algorithms that are fast for every cache size without knowing it
    - parallel algorithms: work, span, Brent's theorem, parallel prefix sums and MapReduce
    - distributed consensus: an algorithm for crash failures, and why the FLP theorem says it cannot be done
      asynchronously

    **You need:** [Chapter 2](02-Measuring-Cost.md) (counting cost), [Chapter 5](05-Sorting-by-Comparison.md)
    (merge sort), [Chapter 7](07-Searching-and-Hashing.md) (hashing), [Chapter 8](08-Trees-and-Balanced-Search-Trees.md)
    (B-trees) and [Chapter 21](21-Randomized-and-Amortized-Analysis.md) (expectation, Markov's inequality, amortized
    analysis).

    **Levels:** 24.1 and 24.2 are intermediate with advanced parts; 24.3 is intermediate; 24.4 is advanced; 24.5 is
    intermediate to advanced; 24.6 is advanced.

## 24.1 Online algorithms and competitive ratio: ski rental, paging

You are on holiday at a ski resort and do not know how many days the snow will last. Renting skis costs 1 a day;
buying them costs $B$. Each morning you must decide: rent again, or buy? If you knew the season would last $d$
days, the answer would be easy: rent if $d < B$, buy on day one otherwise, paying $\min(d, B)$. But you learn $d$
only when the snow melts.

This is an **online problem**: the input arrives piece by piece, and each decision must be made before the rest of
the input is known, and cannot be undone. An **offline** algorithm sees the whole input first. Worst-case running
time is not the issue here; the issue is the *quality of the decisions*. We measure it against the best offline
answer $\mathrm{OPT}$, which knows the future.

An online algorithm is **$c$-competitive** if for every input sequence $\sigma$,

$$
\mathrm{ALG}(\sigma) \le c \cdot \mathrm{OPT}(\sigma) + a ,
$$

for a constant $a$ that does not depend on $\sigma$ (if $a = 0$ it is *strictly* $c$-competitive). The smallest
such $c$ is the **competitive ratio**. Think of a game against an **adversary** who knows your algorithm and
chooses the worst input for it.

**Ski rental.** Any deterministic strategy has the form "rent until day $t - 1$, then buy on day $t$" (if the
season lasts that long). Its cost on a $d$-day season is $d$ if $d < t$, and $(t - 1) + B$ if $d \ge t$.

**Theorem.** Buying on day $t = B$ is $(2 - 1/B)$-competitive, and no deterministic strategy does better.

*Proof.* *Upper bound.* If $d < B$ we rent every day and pay $d = \mathrm{OPT}$. If $d \ge B$ we pay $(B - 1) + B
= 2B - 1$ while $\mathrm{OPT} = B$; the ratio is $2 - 1/B$. *Lower bound.* The adversary ends the season right
after the day you buy, $d = t$. You pay $t - 1 + B$ and $\mathrm{OPT} = \min(t, B)$. If $t \le B$ the ratio is
$1 + (B-1)/t \ge 1 + (B-1)/B = 2 - 1/B$. If $t > B$ it is $(t - 1 + B)/B \ge 2B/B = 2$. Either way at least
$2 - 1/B$. $\square$

The idea is called **rent until you have paid the purchase price, then buy**: by the time you buy, you have already
spent about what OPT would spend, so you can lose at most a factor of 2. It appears in many places: when to stop
spinning on a lock and go to sleep, when to turn off an idle disk, when to stop retrying.

**Randomness helps.** The adversary's trick was to end the season the day after you buy. If you choose the day at
random, the adversary cannot know it. Buying on day $t \in \{1, \dots, B\}$ with probability proportional to
$(1 - 1/B)^{B-t}$ gives an expected ratio of $1/(1 - (1 - 1/B)^B)$, which tends to $e/(e-1) \approx 1.582$ as $B$
grows, and that is optimal for randomized strategies (Karlin, Manasse, McGeoch and Owicki, 1990). The
competitive ratio of a randomized algorithm is measured against an **oblivious adversary**, who fixes the input
in advance without seeing your coin flips.

**Paging.** A computer has a fast memory (a **cache**) with room for $k$ pages and a slow memory holding all pages.
Each request names a page. If it is in the cache, that is a **hit** and costs nothing. Otherwise it is a **miss**
(or **page fault**): the page must be loaded, and if the cache is full some page must be **evicted** to make room.
The goal is to minimise misses. The policies:

- **LRU** (least recently used): evict the page whose last request is oldest.
- **FIFO** (first in, first out): evict the page that was loaded earliest.
- **Belady's MIN** (offline, 1966): evict the page whose *next* request is farthest in the future.

**Theorem (Belady).** MIN makes the fewest misses possible.

*Proof sketch.* An exchange argument, like those of [Chapter 12](12-Greedy-Algorithms.md). Take an optimal
schedule $S$ that makes the same evictions as MIN for the first $i$ requests, and suppose that at request $i + 1$
MIN evicts page $p$ while $S$ evicts a different page $q$. MIN chose $p$ because its next request comes later than
$q$'s. Build a schedule $S'$ that evicts $p$ instead of $q$ and then copies $S$, with $q$ playing the role of $p$ in
its cache. Until the next request of $q$, every request is a hit for $S'$ whenever it is a hit for $S$, because $p$
is not requested in that stretch. At the request for $q$, $S$ misses (or reloaded $q$ earlier, which is also a miss)
while $S'$ hits, and from that point $S'$ can make its cache equal to that of $S$ without any extra miss. So $S'$ is
also optimal and agrees with MIN on $i + 1$ requests; induction on $i$ finishes the proof. (Kleinberg and Tardos,
section 4.3, write out the details.) $\square$

MIN needs the future, so it is a yardstick, not a practical policy. How close can an online policy come?

**Theorem (Sleator and Tarjan 1985).** LRU is $k$-competitive: on every sequence,
$\mathrm{LRU} \le k \cdot \mathrm{OPT} + k$.

*Proof.* Split the request sequence into **phases**: phase 1 starts at the first request, and each phase is as
long as possible while containing at most $k$ distinct pages; the next phase begins with the request that would be
the $(k+1)$-th distinct page. *LRU makes at most $k$ misses per phase:* once a page is requested in a phase, it is
among the $k$ most recently used pages until the phase ends (only $k$ distinct pages occur in the phase), so LRU
does not evict it; each of the at most $k$ distinct pages misses at most once. *OPT makes at least one miss per
phase after the first:* let $p$ be the first request of phase $i$. Look at the window from just after that request
to the first request of phase $i + 1$, inclusive. It contains $k - 1$ distinct pages of phase $i$ other than $p$,
plus the new page that starts phase $i+1$: $k$ distinct pages, none equal to $p$. Just after serving $p$, OPT's
cache holds $p$ and only $k - 1$ other pages, so at least one of those $k$ pages misses inside the window. The
windows of different phases do not overlap. With $P$ phases, $\mathrm{LRU} \le kP$ and
$\mathrm{OPT} \ge P - 1$, so $\mathrm{LRU} \le k(\mathrm{OPT} + 1)$. $\square$

The same proof works for FIFO. And it cannot be improved:

**Theorem.** No deterministic online paging algorithm is better than $k$-competitive.

*Proof.* Use $k + 1$ pages. The adversary always requests the one page that is not in the algorithm's cache, so the
algorithm misses on every request. Now count MIN's misses on the same sequence. When MIN misses, it evicts the
page whose next request is farthest away. Only $k + 1$ pages exist, so before that page comes back, all the other
$k - 1$ pages in MIN's cache are requested first, and those are hits. So MIN misses at most once in every $k$
requests.
Over $n$ requests the algorithm makes $n$ misses and MIN at most about $n/k$. $\square$

Randomization helps here too: the **marking algorithm** (Fiat, Karp, Luby, McGeoch, Sleator and Young, 1991)
marks pages when requested, evicts a uniformly random unmarked page on a miss, and unmarks everything when all
pages are marked. It is $2H_k$-competitive, where $H_k \approx \ln k$, exponentially better than $k$.

```python
--8<-- "books/algorithms/ch24_online.py"
```

```
ski rental, B = 10: worst-case ratio of 'buy on day t'
  t =  1: 10.000
  t =  5: 2.800
  t = 10: 1.900
  t = 11: 2.000
  t = 15: 2.400
  t = 20: 2.900
  best deterministic: t = B gives 2 - 1/B = 1.900
  randomized: worst expected ratio 1.535 (limit e/(e-1) = 1.582)

paging with k = 4 frames      LRU  FIFO  marking  OPT
  cyclic over k+1 pages (100)   100   100       56   28
  walk with locality (2000)     263   334      334  257
```

The cyclic sequence over $k + 1 = 5$ pages is LRU's nightmare: the page it just evicted is always the next one
requested, so every request misses, while MIN misses 28 times. The randomized marking algorithm sits between them.
On a request sequence with **locality of reference**, where recent pages tend to be requested again, LRU is within
a few percent of the optimum. That gap between the worst case ($k$ times worse) and typical behaviour is a
well-known weakness of competitive analysis; refinements such as the **access graph** model (Borodin, Irani,
Raghavan and Schieber, 1995) and resource augmentation (compare LRU with $k$ pages against OPT with fewer) explain
why LRU is so good in practice.

<figure class="play" data-play="skirental"><span class="ai-tag">AI-created</span><figcaption><b>Try it.</b> Ski rental: compare always renting, buying at once, the break-even rule and someone who knows the future.</figcaption></figure>

## 24.2 Streaming: Misra-Gries, count-min sketch, HyperLogLog

A network router sees billions of packets a day and wants to know which addresses send the most. A website wants
the number of distinct visitors this month. The data passes once, in order, and there is not enough memory to keep
it. The **streaming model**: the input is a sequence $x_1, x_2, \dots, x_n$ of items from a universe of size $u$,
read once from left to right, and the algorithm may use memory far smaller than $n$ or $u$, ideally
$O(\log n)$ or polynomial in $\log n$ and in $1/\varepsilon$ for an accuracy $\varepsilon$.

**Exact answers are impossible in small memory.** Take the number of distinct items. Suppose an algorithm reads a
stream that is some subset $S$ of $\{1, \dots, u\}$ and then, for any $x$, it can be fed $x$ and asked for the new
count. The count goes up by one exactly when $x \notin S$, so the algorithm's memory state determines $S$ entirely.
There are $2^u$ subsets, so the memory needs at least $u$ bits. Alon, Matias and Szegedy (1996) showed that
approximate *deterministic* algorithms and exact randomized ones are also stuck with linear memory: small-memory
streaming needs both **randomness** and **approximation**. Their paper founded the field (and received the 2005
Gödel Prize).

**Heavy hitters: Misra-Gries (1982).** Find every item that occurs more than $n/k$ times. Keep at most $k - 1$
counters, each attached to an item. For each arriving $x$:

- if $x$ has a counter, add 1 to it;
- else if fewer than $k - 1$ counters are in use, start a counter for $x$ at 1;
- else decrease **every** counter by 1, and delete those that reach 0 ($x$ itself is not stored).

**Theorem.** For every item $x$, if $f_x$ is its true count and $\hat f_x$ its counter (0 if none), then
$f_x - n/k \le \hat f_x \le f_x$. So every item with $f_x > n/k$ still has a counter at the end.

*Proof.* Counters only grow when $x$ really arrives, so $\hat f_x \le f_x$. Every time $x$ arrives and is not
counted, or a counter of $x$ is decreased, a "decrement step" happens. Each decrement step removes 1 from $k - 1$
counters and also throws away the arriving item: $k$ units of count vanish. Only $n$ units ever entered, so there
are at most $n/k$ decrement steps, and each lowers $x$'s estimate by at most 1. $\square$

Memory: $k - 1$ pairs (item, count), that is $O(k(\log u + \log n))$ bits, independent of $n$. A second pass
over the data (if possible) can count the candidates exactly.

**Frequency of any item: the count-min sketch (Cormode and Muthukrishnan, 2005).** Keep a table of $d$ rows and $w$
columns of counters, and $d$ hash functions $h_1, \dots, h_d$, each mapping items to $\{0, \dots, w - 1\}$. To add
$x$, increase $T[i][h_i(x)]$ in every row $i$. To estimate $f_x$, return $\min_i T[i][h_i(x)]$.

<figure class="mars-fig" markdown="0">
<svg viewBox="0 0 660 230" role="img" aria-label="A count-min sketch with 3 rows and 8 columns. Item x hashes to one cell in each row; the estimate is the minimum of the three cells, 7, 9 and 12, which is 7.">
<g font-size="13" fill="currentColor">
<text x="30" y="58">h1</text><text x="30" y="108">h2</text><text x="30" y="158">h3</text>
</g>
<g stroke="currentColor" stroke-width="1">
<rect x="70" y="35" width="50" height="36" fill="none"/><rect x="120" y="35" width="50" height="36" fill="none"/>
<rect x="170" y="35" width="50" height="36" fill="none"/><rect x="220" y="35" width="50" height="36" fill="#eea66f"/>
<rect x="270" y="35" width="50" height="36" fill="none"/><rect x="320" y="35" width="50" height="36" fill="none"/>
<rect x="370" y="35" width="50" height="36" fill="none"/><rect x="420" y="35" width="50" height="36" fill="none"/>
<rect x="70" y="85" width="50" height="36" fill="none"/><rect x="120" y="85" width="50" height="36" fill="none"/>
<rect x="170" y="85" width="50" height="36" fill="none"/><rect x="220" y="85" width="50" height="36" fill="none"/>
<rect x="270" y="85" width="50" height="36" fill="none"/><rect x="320" y="85" width="50" height="36" fill="none"/>
<rect x="370" y="85" width="50" height="36" fill="#9cc9ea"/><rect x="420" y="85" width="50" height="36" fill="none"/>
<rect x="70" y="135" width="50" height="36" fill="none"/><rect x="120" y="135" width="50" height="36" fill="#9cc9ea"/>
<rect x="170" y="135" width="50" height="36" fill="none"/><rect x="220" y="135" width="50" height="36" fill="none"/>
<rect x="270" y="135" width="50" height="36" fill="none"/><rect x="320" y="135" width="50" height="36" fill="none"/>
<rect x="370" y="135" width="50" height="36" fill="none"/><rect x="420" y="135" width="50" height="36" fill="none"/>
</g>
<g font-size="13" text-anchor="middle" fill="currentColor">
<text x="95" y="58">3</text><text x="145" y="58">0</text><text x="195" y="58">5</text><text x="245" y="58">7</text>
<text x="295" y="58">2</text><text x="345" y="58">4</text><text x="395" y="58">1</text><text x="445" y="58">6</text>
<text x="95" y="108">2</text><text x="145" y="108">6</text><text x="195" y="108">1</text><text x="245" y="108">3</text>
<text x="295" y="108">0</text><text x="345" y="108">5</text><text x="395" y="108">9</text><text x="445" y="108">2</text>
<text x="95" y="158">4</text><text x="145" y="158">12</text><text x="195" y="158">0</text><text x="245" y="158">3</text>
<text x="295" y="158">6</text><text x="345" y="158">1</text><text x="395" y="158">2</text><text x="445" y="158">0</text>
</g>
<g font-size="13" fill="currentColor">
<text x="495" y="58">x lands here: 7</text>
<text x="495" y="108">x lands here: 9</text>
<text x="495" y="158">x lands here: 12</text>
</g>
<text x="270" y="205" font-size="13" text-anchor="middle" fill="currentColor">estimate of x = min(7, 9, 12) = 7; collisions only ever add, so the minimum is the least spoiled</text>
</svg>
<figcaption>Figure 24.1. A count-min sketch. Each row is a small hash table without collision handling; every count is too high, never too low, and taking the minimum over independent rows makes a large error unlikely.</figcaption>
</figure>

**Theorem.** With $w = \lceil e/\varepsilon \rceil$ and $d = \lceil \ln(1/\delta) \rceil$, and hash functions drawn
from a pairwise independent family ([Chapter 7](07-Searching-and-Hashing.md)), the estimate satisfies
$f_x \le \hat f_x$ always, and $\hat f_x \le f_x + \varepsilon n$ with probability at least $1 - \delta$.

*Proof.* Every arrival of $x$ adds to all its cells, so each cell is at least $f_x$. In row $i$ the excess
$Z_i = T[i][h_i(x)] - f_x$ is the total count of the *other* items that hash to the same cell. Each other item $y$
collides with $x$ with probability $1/w$, so $\mathbb E[Z_i] \le \sum_{y \ne x} f_y / w \le n/w = \varepsilon n/e$.
By Markov's inequality ([Chapter 21](21-Randomized-and-Amortized-Analysis.md)),
$\Pr[Z_i > \varepsilon n] \le 1/e$. The rows use independent hash functions, so the probability that *every* row
exceeds the bound is at most $e^{-d} \le \delta$, and the minimum is within $\varepsilon n$ otherwise. $\square$

The sketch uses $O(\frac1\varepsilon \log \frac1\delta)$ counters regardless of the number of distinct items.
Sketches can also be **added**: the sketch of two streams merged is the cell-by-cell sum of their sketches, which
is what makes them useful when many machines each see part of the data.

**Distinct items: HyperLogLog (Flajolet, Fusy, Gandouet and Meunier, 2007).** The idea goes back to Philippe
Flajolet and Nigel Martin (1985). Hash each item to a random-looking string of bits. Half of all hash values start
with a 1, a quarter with 01, an eighth with 001: the chance that the first 1 bit is at position $r$ or later is
$2^{-(r-1)}$. If the largest such position seen so far is $R$, then about $2^R$ distinct items have probably gone
by. Repeats hash to the same value and change nothing, so this counts *distinct* items. One such estimate is very
noisy (it can only be a power of 2). HyperLogLog uses the first $p$ bits of the hash to send each item to one of
$m = 2^p$ **registers**, keeps in each register the largest position $R_j$ seen, and combines them with a
harmonic mean:

$$
E = \alpha_m \, m^2 \Big/ \sum_{j=1}^{m} 2^{-R_j} ,
$$

where $\alpha_m \approx 0.7213/(1 + 1.079/m)$ corrects a bias. The harmonic mean is used because it is little
affected by the occasional register with an unluckily large value. The paper proves a relative standard error of
about $1.04/\sqrt m$. Each register holds a number below 64, so 6 bits suffice: with $m = 1024$ registers, 768
bytes estimate counts in the billions to within a few percent. For small counts, many registers are still 0, and
the algorithm switches to **linear counting**, $m \ln(m / \text{zeros})$.

```python
--8<-- "books/algorithms/ch24_streaming.py"
```

```
stream of 50000 items, 1000 distinct
Misra-Gries with 19 counters (error at most n/k = 2500):
  item   1: true  6783, estimate  4572, low by 2211
  item   2: true  3341, estimate  1130, low by 2211
  item   3: true  2251, estimate    69, low by 2182
  item   4: true  1677, estimate     0, low by 1677
  item   5: true  1259, estimate     1, low by 1258
count-min 5 x 272: overestimate at most 161, mean 25.7, bound eps*n = 500 (holds for 1000/1000 items)

HyperLogLog (p = 10: 1024 registers of 6 bits = 768 bytes)
  true distinct   estimate   error
            100         96    -3.6%
           1000       1048    +4.8%
          10000      10188    +1.9%
         100000      98425    -1.6%
  standard error 1.04/sqrt(m) = 3.2%
```

Read the Misra-Gries rows honestly: the guarantee holds (every error is below 2500), but with only 19 counters on
a stream whose top item has 13.6 percent of the traffic, the estimates are rough; only the top item is clearly
identified. More counters shrink the error in proportion. The count-min overestimates stay well below their bound.
HyperLogLog's errors match its standard error of about 3 percent.

**In practice.** HyperLogLog is built into Redis (`PFADD`, `PFCOUNT`) and many databases' approximate
`COUNT(DISTINCT)`; count-min and its relatives run inside network monitoring tools. Python's
`collections.Counter` is the exact, memory-hungry version.

## 24.3 External memory: the I/O model, external merge sort, B-trees again

A database holds a billion records on disk, and memory holds only a few million. Reading a random record from a
spinning disk takes milliseconds, millions of times slower than a memory access, but once the disk head is in
place, the next few thousand bytes come almost free. Solid-state drives narrow the gap but keep the shape: data
moves in **blocks**. Counting comparisons is now the wrong measure; we must count block transfers.

**The I/O model (Aggarwal and Vitter, 1988).** There is a memory of $M$ records and an unbounded disk divided into
blocks of $B$ records. Computation in memory is free. An **I/O** moves one block between disk and memory. The input
of $N$ records starts on disk, in $N/B$ blocks. We count I/Os. (Typically $1 \ll B \ll M \ll N$.)

<figure class="mars-fig" markdown="0">
<svg viewBox="0 0 660 220" role="img" aria-label="The I/O model: a CPU attached to a memory of M records divided into blocks, and a disk of many blocks of B records. One I/O moves one whole block between disk and memory.">
<rect x="30" y="40" width="90" height="60" rx="6" fill="#7ccf9a" stroke="currentColor" stroke-width="1.3"/>
<text x="75" y="75" font-size="14" text-anchor="middle" fill="currentColor">CPU</text>
<line x1="120" y1="70" x2="170" y2="70" stroke="currentColor" stroke-width="1.5"/>
<text x="145" y="60" font-size="11" text-anchor="middle" fill="currentColor">free</text>
<rect x="170" y="30" width="200" height="80" rx="6" fill="none" stroke="currentColor" stroke-width="1.3"/>
<g fill="#9cc9ea" stroke="currentColor" stroke-width="1">
<rect x="180" y="45" width="40" height="22"/><rect x="225" y="45" width="40" height="22"/>
<rect x="270" y="45" width="40" height="22"/><rect x="315" y="45" width="40" height="22"/>
<rect x="180" y="75" width="40" height="22"/><rect x="225" y="75" width="40" height="22"/>
<rect x="270" y="75" width="40" height="22"/><rect x="315" y="75" width="40" height="22"/>
</g>
<text x="270" y="128" font-size="13" text-anchor="middle" fill="currentColor">memory: M records = M/B blocks</text>
<line x1="295" y1="150" x2="295" y2="117" stroke="#eea66f" stroke-width="2.5"/>
<polygon points="295,111 290,121 300,121" fill="#eea66f"/>
<text x="305" y="148" font-size="12" fill="currentColor">one I/O = one block of B records</text>
<g fill="none" stroke="currentColor" stroke-width="1">
<rect x="30" y="160" width="40" height="22"/><rect x="75" y="160" width="40" height="22"/>
<rect x="120" y="160" width="40" height="22"/><rect x="165" y="160" width="40" height="22"/>
<rect x="210" y="160" width="40" height="22"/><rect x="255" y="160" width="40" height="22" fill="#eea66f"/>
<rect x="300" y="160" width="40" height="22"/><rect x="345" y="160" width="40" height="22"/>
<rect x="390" y="160" width="40" height="22"/><rect x="435" y="160" width="40" height="22"/>
<rect x="480" y="160" width="40" height="22"/><rect x="525" y="160" width="40" height="22"/>
<rect x="570" y="160" width="40" height="22"/>
</g>
<text x="625" y="176" font-size="13" fill="currentColor">...</text>
<text x="330" y="205" font-size="13" text-anchor="middle" fill="currentColor">disk: N records = N/B blocks, unbounded</text>
</svg>
<figcaption>Figure 24.2. The I/O model of Aggarwal and Vitter. Only block transfers between disk and memory are counted; work inside memory is free.</figcaption>
</figure>

Three basic costs:

- **Scanning** $N$ records takes $\lceil N/B \rceil$ I/Os, not $N$.
- **Searching** a sorted file by binary search takes about $\log_2(N/B)$ I/Os: the first steps each jump to a new
  block. A **B-tree** ([Chapter 8](08-Trees-and-Balanced-Search-Trees.md)) with nodes of one block each has
  fan-out about $B$ and height $\log_B N$, and the theory shows this is optimal for comparison-based search.
- **Sorting** takes $\Theta\big(\frac NB \log_{M/B} \frac NB\big)$ I/Os, proved optimal by Aggarwal and Vitter. This
  is the "sorting bound" that many external algorithms meet.

**External merge sort.** *Pass 0:* read $M$ records at a time, sort them in memory, write them back as a sorted
**run**: $N/M$ runs, costing $2N/B$ I/Os (everything read once, written once). *Merge passes:* with one block of
memory for each input run and one for output, we can merge $M/B - 1$ runs at once. Each merge pass reads and writes
everything once ($2N/B$ I/Os) and divides the number of runs by $M/B - 1$. So the number of merge passes is
$\lceil \log_{M/B-1}(N/M) \rceil$ and the total is

$$
\frac{2N}{B}\left(1 + \left\lceil \log_{M/B - 1} \frac{N}{M} \right\rceil\right) \text{ I/Os.}
$$

Compare ordinary merge sort, which merges two runs at a time: it makes $\log_2(N/M)$ passes. With $M/B = 100$,
a 100-way merge cuts the passes by a factor of $\log_2 100 \approx 6.6$, and on disk each pass is minutes or hours.
The program simulates a disk that counts block reads and writes:

```python
--8<-- "books/algorithms/ch24_external.py"
```

```
      N      M     B   runs  merge passes   I/Os   formula 2(N/B)(1 + passes)
   10000   1000   100     10        2         600         600
  100000   1000   100    100        3        8000        8000
  100000  10000   100     10        1        4000        4000
 1000000  10000  1000    100        3        8000        8000

height needed to index N keys
         N   binary tree   B-tree, B = 100   B-tree, B = 1000
  1e+03          10                2                 1
  1e+06          20                3                 2
  1e+09          30                5                 3
  1e+12          40                6                 4
```

Check one row by hand: $N = 10^5$, $M = 10^3$, $B = 100$. Pass 0 makes 100 runs. The fan-in is $M/B - 1 = 9$:
the first merge pass leaves $\lceil 100/9 \rceil = 12$ runs, the second 2, the third 1, so 3 merge passes. Each
pass moves $2N/B = 2000$ blocks: $2000 \times 4 = 8000$ I/Os. Notice also the last row: with bigger blocks
($B = 1000$) the same memory holds only 10 blocks, the fan-in drops to 9, and we need more passes, but each pass is
10 times cheaper.

**B-trees again.** The second table is why every database index is a B-tree or a relative. A trillion keys need a
binary tree 40 levels deep (40 random disk reads per lookup), but a B-tree with nodes of 1000 keys only 4 levels,
and the top two or three levels stay in memory. Modern write-heavy stores use **log-structured merge trees**
(O'Neil, Cheng, Gawlick and O'Neil, 1996), which buffer writes in memory and merge sorted files on disk, the
external merge sort idea applied continuously.

## 24.4 Cache-oblivious algorithms

*Level: advanced.*

The I/O model has two levels; a real computer has many: registers, three levels of cache, main memory, SSD. Each
has its own $M$ and $B$, and they differ from machine to machine. An algorithm tuned for one $(M, B)$ is wrong for
the others. Matteo Frigo, Charles Leiserson, Harald Prokop and Sridhar Ramachandran (1999) asked: can an algorithm
be efficient for **every** $M$ and $B$ at once, **without knowing** them?

**The ideal-cache model.** Analyse an algorithm in the I/O model, but the algorithm is written without any mention
of $M$ or $B$; the cache is fully associative (any block can go anywhere) and the replacement is optimal (Belady's
MIN). These sound unrealistic, but they can be justified: LRU with twice the cache size is within a factor 2 of
MIN (Sleator and Tarjan's resource-augmentation result), and full associativity can be simulated by hashing. The
payoff: an algorithm that is optimal in this model for all $M$ and $B$ is optimal **simultaneously at every level**
of a multilevel memory, since each level is a pair $(M, B)$ for the analysis.

The design principle is **divide and conquer until the problem fits**. A recursive algorithm keeps halving the
problem; at some depth, which depends on $M$ but which the algorithm never needs to know, the subproblems fit in
cache, and from then on they cost only the I/Os needed to load them once.

**Example: transposing a matrix.** Store an $n \times n$ matrix $A$ row by row, and write its transpose $T$. The
naive loop reads $A$ along rows (good: consecutive addresses, one miss per $B$ entries) and writes $T$ down columns
(bad: each write is in a different row of $T$, so a different cache line). If the cache cannot hold $n$ lines, each
line of $T$ is evicted before it is used again, and the writes miss almost every time: about $n^2$ misses.

The cache-oblivious version splits the larger dimension of the current submatrix in half and transposes each half
recursively, down to a tiny base case. **Claim:** with a "tall cache" $M \ge c B^2$, it makes $O(n^2/B)$ misses,
which is optimal (you must at least read and write $2n^2$ entries, $B$ at a time).

*Proof sketch.* Follow the recursion to the first level where the current submatrix has both sides at most
$s = \sqrt{M}/2$ (sides at that level are between $s/2$ and $s$ since we halve the longer side). The submatrix of $A$
and the matching submatrix of $T$ each occupy at most $s$ rows, touching at most $s(s/B + 2)$ lines each. With the
tall-cache assumption $s \ge B$, that is $O(s^2/B)$ lines, and both together fit in the cache, so this subproblem
costs $O(s^2/B)$ misses. There are about $n^2/s^2$ such subproblems: $O(n^2/B)$ in total. $\square$

```python
--8<-- "books/algorithms/ch24_cache.py"
```

```
matrix transpose, n x n doubles; misses counted in cache lines
    n      M     B   naive misses   recursive misses   lower bound 2n^2/B
   64   1024     8           1024               1024           1024
  128   1024     8          18432               4096           4096
  128   4096    16           2048               2048           2048
  256   4096    16          69632               8192           8192
  256   8192    64          66560               2048           2048
```

The simulation uses LRU, not the ideal cache, and the recursive transpose still meets the lower bound $2n^2/B$
exactly in every row, without the code ever mentioning $M$ or $B$. The naive loop is optimal only when the cache
holds at least $n$ lines (first and third rows: 128 lines for $n = 64$; 256 lines for $n = 128$), and is about 32
times worse otherwise. Other cache-oblivious classics are recursive matrix multiplication, the **van Emde Boas
layout** of a search tree (store the top half of the tree, then each bottom subtree, recursively), which gives
$O(\log_B N)$ search like a B-tree, and **funnelsort**, which sorts with the optimal I/O bound of 24.3.

## 24.5 Parallel algorithms: work and span, Brent's theorem, prefix sums, MapReduce

*Level: intermediate to advanced.*

A laptop has 8 or 16 cores; a graphics processor has thousands of simple ones; a data centre has thousands of
machines. How do we describe an algorithm for $p$ processors, and how fast can it be?

**The work-span model.** Describe the computation as a **directed acyclic graph** (DAG) of unit-time tasks, with an
edge $u \to v$ when $v$ needs $u$'s result. Two numbers characterise it:

- the **work** $W$ (also $T_1$): the total number of tasks, the time on one processor;
- the **span** $S$ (also $T_\infty$, the **depth** or **critical path**): the number of tasks on the longest path,
  the time with unlimited processors.

Two lower bounds hold for any schedule on $p$ processors: $T_p \ge W/p$ (only $p$ tasks per step) and
$T_p \ge S$ (the tasks on the longest path must run one after another). The ratio $W/S$ is the **parallelism**:
using more processors than that cannot help much.

In code, parallelism is often written as **fork-join**: `spawn` a recursive call to run in parallel with the rest,
then `sync` to wait for it. For a parallel sum by divide and conquer, $W(n) = 2W(n/2) + O(1) = O(n)$ and
$S(n) = S(n/2) + O(1) = O(\log n)$: the two halves run at the same time, so the span counts only one of them. This
is the [master theorem](03-Recursion-and-Induction.md) applied twice.

**Theorem (Brent 1974; greedy scheduling, Graham 1966).** A **greedy** scheduler, which at each step runs any $p$
ready tasks if at least $p$ are ready and all of them otherwise, finishes in

$$
T_p \le \frac{W}{p} + S .
$$

*Proof.* Call a step **complete** if it runs $p$ tasks and **incomplete** otherwise. Each complete step does $p$
units of the total work $W$, so there are at most $W/p$ of them. In an incomplete step every ready task runs. In
particular every task with no unfinished predecessors runs, including the first unfinished task on every longest
remaining path; so the length of the longest path of unfinished tasks drops by one. It starts at $S$, so there are
at most $S$ incomplete steps. $\square$

Since $\max(W/p, S) \le T_p^{\text{opt}}$ and $W/p + S \le 2\max(W/p, S)$, greedy scheduling is within a factor 2
of the best schedule, and it is nearly perfect when $p \ll W/S$. The practical lesson: **design for low span**, and
let a scheduler (Cilk's work-stealing scheduler, by Blumofe and Leiserson, 1999, achieves expected
$W/p + O(S)$) map tasks to processors.

**Parallel prefix sums.** Given $x_0, \dots, x_{n-1}$, compute every prefix sum $y_i = x_0 + \dots + x_{i-1}$ (the
*exclusive* scan). The loop $y_{i+1} = y_i + x_i$ has span $n$: every step needs the previous one. It looks
inherently sequential, but it is not, because addition is associative. Guy Blelloch's work-efficient scan (1990)
runs in two sweeps over an implicit balanced binary tree:

- **Up-sweep:** for $d = 1, 2, 4, \dots$, in parallel for each $i \equiv 2d - 1 \pmod{2d}$, set
  $a[i] \mathrel{+}= a[i - d]$. Afterwards $a[i]$ holds the sum of a block ending at $i$, and $a[n-1]$ the total.
- **Down-sweep:** set $a[n-1] = 0$; for $d = n/2, \dots, 2, 1$, in parallel for the same $i$, set
  $(a[i-d], a[i]) \leftarrow (a[i], a[i] + a[i-d])$.

Figure 24.3 traces it on eight numbers.

<figure class="mars-fig" markdown="0">
<svg viewBox="0 0 660 280" role="img" aria-label="Blelloch exclusive scan of 3 1 7 0 4 1 6 3: the array after each up-sweep and down-sweep step, ending with 0 3 4 11 11 15 16 22. Changed cells are shaded.">
<text x="215" y="20" font-size="12" text-anchor="middle" fill="currentColor">a[0]</text>
<text x="271" y="20" font-size="12" text-anchor="middle" fill="currentColor">a[1]</text>
<text x="327" y="20" font-size="12" text-anchor="middle" fill="currentColor">a[2]</text>
<text x="383" y="20" font-size="12" text-anchor="middle" fill="currentColor">a[3]</text>
<text x="439" y="20" font-size="12" text-anchor="middle" fill="currentColor">a[4]</text>
<text x="495" y="20" font-size="12" text-anchor="middle" fill="currentColor">a[5]</text>
<text x="551" y="20" font-size="12" text-anchor="middle" fill="currentColor">a[6]</text>
<text x="607" y="20" font-size="12" text-anchor="middle" fill="currentColor">a[7]</text>
<text x="175" y="48" font-size="13" text-anchor="end" fill="currentColor">input</text>
<rect x="190" y="30" width="50" height="24" rx="3" fill="none" stroke="currentColor" stroke-width="1"/>
<text x="215" y="47" font-size="13" text-anchor="middle" fill="currentColor">3</text>
<rect x="246" y="30" width="50" height="24" rx="3" fill="none" stroke="currentColor" stroke-width="1"/>
<text x="271" y="47" font-size="13" text-anchor="middle" fill="currentColor">1</text>
<rect x="302" y="30" width="50" height="24" rx="3" fill="none" stroke="currentColor" stroke-width="1"/>
<text x="327" y="47" font-size="13" text-anchor="middle" fill="currentColor">7</text>
<rect x="358" y="30" width="50" height="24" rx="3" fill="none" stroke="currentColor" stroke-width="1"/>
<text x="383" y="47" font-size="13" text-anchor="middle" fill="currentColor">0</text>
<rect x="414" y="30" width="50" height="24" rx="3" fill="none" stroke="currentColor" stroke-width="1"/>
<text x="439" y="47" font-size="13" text-anchor="middle" fill="currentColor">4</text>
<rect x="470" y="30" width="50" height="24" rx="3" fill="none" stroke="currentColor" stroke-width="1"/>
<text x="495" y="47" font-size="13" text-anchor="middle" fill="currentColor">1</text>
<rect x="526" y="30" width="50" height="24" rx="3" fill="none" stroke="currentColor" stroke-width="1"/>
<text x="551" y="47" font-size="13" text-anchor="middle" fill="currentColor">6</text>
<rect x="582" y="30" width="50" height="24" rx="3" fill="none" stroke="currentColor" stroke-width="1"/>
<text x="607" y="47" font-size="13" text-anchor="middle" fill="currentColor">3</text>
<text x="175" y="78" font-size="13" text-anchor="end" fill="currentColor">up-sweep, d = 1</text>
<rect x="190" y="60" width="50" height="24" rx="3" fill="none" stroke="currentColor" stroke-width="1"/>
<text x="215" y="77" font-size="13" text-anchor="middle" fill="currentColor">3</text>
<rect x="246" y="60" width="50" height="24" rx="3" fill="#eea66f" stroke="currentColor" stroke-width="1"/>
<text x="271" y="77" font-size="13" text-anchor="middle" fill="currentColor">4</text>
<rect x="302" y="60" width="50" height="24" rx="3" fill="none" stroke="currentColor" stroke-width="1"/>
<text x="327" y="77" font-size="13" text-anchor="middle" fill="currentColor">7</text>
<rect x="358" y="60" width="50" height="24" rx="3" fill="#eea66f" stroke="currentColor" stroke-width="1"/>
<text x="383" y="77" font-size="13" text-anchor="middle" fill="currentColor">7</text>
<rect x="414" y="60" width="50" height="24" rx="3" fill="none" stroke="currentColor" stroke-width="1"/>
<text x="439" y="77" font-size="13" text-anchor="middle" fill="currentColor">4</text>
<rect x="470" y="60" width="50" height="24" rx="3" fill="#eea66f" stroke="currentColor" stroke-width="1"/>
<text x="495" y="77" font-size="13" text-anchor="middle" fill="currentColor">5</text>
<rect x="526" y="60" width="50" height="24" rx="3" fill="none" stroke="currentColor" stroke-width="1"/>
<text x="551" y="77" font-size="13" text-anchor="middle" fill="currentColor">6</text>
<rect x="582" y="60" width="50" height="24" rx="3" fill="#eea66f" stroke="currentColor" stroke-width="1"/>
<text x="607" y="77" font-size="13" text-anchor="middle" fill="currentColor">9</text>
<text x="175" y="108" font-size="13" text-anchor="end" fill="currentColor">up-sweep, d = 2</text>
<rect x="190" y="90" width="50" height="24" rx="3" fill="none" stroke="currentColor" stroke-width="1"/>
<text x="215" y="107" font-size="13" text-anchor="middle" fill="currentColor">3</text>
<rect x="246" y="90" width="50" height="24" rx="3" fill="none" stroke="currentColor" stroke-width="1"/>
<text x="271" y="107" font-size="13" text-anchor="middle" fill="currentColor">4</text>
<rect x="302" y="90" width="50" height="24" rx="3" fill="none" stroke="currentColor" stroke-width="1"/>
<text x="327" y="107" font-size="13" text-anchor="middle" fill="currentColor">7</text>
<rect x="358" y="90" width="50" height="24" rx="3" fill="#eea66f" stroke="currentColor" stroke-width="1"/>
<text x="383" y="107" font-size="13" text-anchor="middle" fill="currentColor">11</text>
<rect x="414" y="90" width="50" height="24" rx="3" fill="none" stroke="currentColor" stroke-width="1"/>
<text x="439" y="107" font-size="13" text-anchor="middle" fill="currentColor">4</text>
<rect x="470" y="90" width="50" height="24" rx="3" fill="none" stroke="currentColor" stroke-width="1"/>
<text x="495" y="107" font-size="13" text-anchor="middle" fill="currentColor">5</text>
<rect x="526" y="90" width="50" height="24" rx="3" fill="none" stroke="currentColor" stroke-width="1"/>
<text x="551" y="107" font-size="13" text-anchor="middle" fill="currentColor">6</text>
<rect x="582" y="90" width="50" height="24" rx="3" fill="#eea66f" stroke="currentColor" stroke-width="1"/>
<text x="607" y="107" font-size="13" text-anchor="middle" fill="currentColor">14</text>
<text x="175" y="138" font-size="13" text-anchor="end" fill="currentColor">up-sweep, d = 4</text>
<rect x="190" y="120" width="50" height="24" rx="3" fill="none" stroke="currentColor" stroke-width="1"/>
<text x="215" y="137" font-size="13" text-anchor="middle" fill="currentColor">3</text>
<rect x="246" y="120" width="50" height="24" rx="3" fill="none" stroke="currentColor" stroke-width="1"/>
<text x="271" y="137" font-size="13" text-anchor="middle" fill="currentColor">4</text>
<rect x="302" y="120" width="50" height="24" rx="3" fill="none" stroke="currentColor" stroke-width="1"/>
<text x="327" y="137" font-size="13" text-anchor="middle" fill="currentColor">7</text>
<rect x="358" y="120" width="50" height="24" rx="3" fill="none" stroke="currentColor" stroke-width="1"/>
<text x="383" y="137" font-size="13" text-anchor="middle" fill="currentColor">11</text>
<rect x="414" y="120" width="50" height="24" rx="3" fill="none" stroke="currentColor" stroke-width="1"/>
<text x="439" y="137" font-size="13" text-anchor="middle" fill="currentColor">4</text>
<rect x="470" y="120" width="50" height="24" rx="3" fill="none" stroke="currentColor" stroke-width="1"/>
<text x="495" y="137" font-size="13" text-anchor="middle" fill="currentColor">5</text>
<rect x="526" y="120" width="50" height="24" rx="3" fill="none" stroke="currentColor" stroke-width="1"/>
<text x="551" y="137" font-size="13" text-anchor="middle" fill="currentColor">6</text>
<rect x="582" y="120" width="50" height="24" rx="3" fill="#eea66f" stroke="currentColor" stroke-width="1"/>
<text x="607" y="137" font-size="13" text-anchor="middle" fill="currentColor">25</text>
<text x="175" y="168" font-size="13" text-anchor="end" fill="currentColor">clear last</text>
<rect x="190" y="150" width="50" height="24" rx="3" fill="none" stroke="currentColor" stroke-width="1"/>
<text x="215" y="167" font-size="13" text-anchor="middle" fill="currentColor">3</text>
<rect x="246" y="150" width="50" height="24" rx="3" fill="none" stroke="currentColor" stroke-width="1"/>
<text x="271" y="167" font-size="13" text-anchor="middle" fill="currentColor">4</text>
<rect x="302" y="150" width="50" height="24" rx="3" fill="none" stroke="currentColor" stroke-width="1"/>
<text x="327" y="167" font-size="13" text-anchor="middle" fill="currentColor">7</text>
<rect x="358" y="150" width="50" height="24" rx="3" fill="none" stroke="currentColor" stroke-width="1"/>
<text x="383" y="167" font-size="13" text-anchor="middle" fill="currentColor">11</text>
<rect x="414" y="150" width="50" height="24" rx="3" fill="none" stroke="currentColor" stroke-width="1"/>
<text x="439" y="167" font-size="13" text-anchor="middle" fill="currentColor">4</text>
<rect x="470" y="150" width="50" height="24" rx="3" fill="none" stroke="currentColor" stroke-width="1"/>
<text x="495" y="167" font-size="13" text-anchor="middle" fill="currentColor">5</text>
<rect x="526" y="150" width="50" height="24" rx="3" fill="none" stroke="currentColor" stroke-width="1"/>
<text x="551" y="167" font-size="13" text-anchor="middle" fill="currentColor">6</text>
<rect x="582" y="150" width="50" height="24" rx="3" fill="#7ccf9a" stroke="currentColor" stroke-width="1"/>
<text x="607" y="167" font-size="13" text-anchor="middle" fill="currentColor">0</text>
<text x="175" y="198" font-size="13" text-anchor="end" fill="currentColor">down-sweep, d = 4</text>
<rect x="190" y="180" width="50" height="24" rx="3" fill="none" stroke="currentColor" stroke-width="1"/>
<text x="215" y="197" font-size="13" text-anchor="middle" fill="currentColor">3</text>
<rect x="246" y="180" width="50" height="24" rx="3" fill="none" stroke="currentColor" stroke-width="1"/>
<text x="271" y="197" font-size="13" text-anchor="middle" fill="currentColor">4</text>
<rect x="302" y="180" width="50" height="24" rx="3" fill="none" stroke="currentColor" stroke-width="1"/>
<text x="327" y="197" font-size="13" text-anchor="middle" fill="currentColor">7</text>
<rect x="358" y="180" width="50" height="24" rx="3" fill="#9cc9ea" stroke="currentColor" stroke-width="1"/>
<text x="383" y="197" font-size="13" text-anchor="middle" fill="currentColor">0</text>
<rect x="414" y="180" width="50" height="24" rx="3" fill="none" stroke="currentColor" stroke-width="1"/>
<text x="439" y="197" font-size="13" text-anchor="middle" fill="currentColor">4</text>
<rect x="470" y="180" width="50" height="24" rx="3" fill="none" stroke="currentColor" stroke-width="1"/>
<text x="495" y="197" font-size="13" text-anchor="middle" fill="currentColor">5</text>
<rect x="526" y="180" width="50" height="24" rx="3" fill="none" stroke="currentColor" stroke-width="1"/>
<text x="551" y="197" font-size="13" text-anchor="middle" fill="currentColor">6</text>
<rect x="582" y="180" width="50" height="24" rx="3" fill="#9cc9ea" stroke="currentColor" stroke-width="1"/>
<text x="607" y="197" font-size="13" text-anchor="middle" fill="currentColor">11</text>
<text x="175" y="228" font-size="13" text-anchor="end" fill="currentColor">down-sweep, d = 2</text>
<rect x="190" y="210" width="50" height="24" rx="3" fill="none" stroke="currentColor" stroke-width="1"/>
<text x="215" y="227" font-size="13" text-anchor="middle" fill="currentColor">3</text>
<rect x="246" y="210" width="50" height="24" rx="3" fill="#9cc9ea" stroke="currentColor" stroke-width="1"/>
<text x="271" y="227" font-size="13" text-anchor="middle" fill="currentColor">0</text>
<rect x="302" y="210" width="50" height="24" rx="3" fill="none" stroke="currentColor" stroke-width="1"/>
<text x="327" y="227" font-size="13" text-anchor="middle" fill="currentColor">7</text>
<rect x="358" y="210" width="50" height="24" rx="3" fill="#9cc9ea" stroke="currentColor" stroke-width="1"/>
<text x="383" y="227" font-size="13" text-anchor="middle" fill="currentColor">4</text>
<rect x="414" y="210" width="50" height="24" rx="3" fill="none" stroke="currentColor" stroke-width="1"/>
<text x="439" y="227" font-size="13" text-anchor="middle" fill="currentColor">4</text>
<rect x="470" y="210" width="50" height="24" rx="3" fill="#9cc9ea" stroke="currentColor" stroke-width="1"/>
<text x="495" y="227" font-size="13" text-anchor="middle" fill="currentColor">11</text>
<rect x="526" y="210" width="50" height="24" rx="3" fill="none" stroke="currentColor" stroke-width="1"/>
<text x="551" y="227" font-size="13" text-anchor="middle" fill="currentColor">6</text>
<rect x="582" y="210" width="50" height="24" rx="3" fill="#9cc9ea" stroke="currentColor" stroke-width="1"/>
<text x="607" y="227" font-size="13" text-anchor="middle" fill="currentColor">16</text>
<text x="175" y="258" font-size="13" text-anchor="end" fill="currentColor">down-sweep, d = 1</text>
<rect x="190" y="240" width="50" height="24" rx="3" fill="#9cc9ea" stroke="currentColor" stroke-width="1"/>
<text x="215" y="257" font-size="13" text-anchor="middle" fill="currentColor">0</text>
<rect x="246" y="240" width="50" height="24" rx="3" fill="#9cc9ea" stroke="currentColor" stroke-width="1"/>
<text x="271" y="257" font-size="13" text-anchor="middle" fill="currentColor">3</text>
<rect x="302" y="240" width="50" height="24" rx="3" fill="#9cc9ea" stroke="currentColor" stroke-width="1"/>
<text x="327" y="257" font-size="13" text-anchor="middle" fill="currentColor">4</text>
<rect x="358" y="240" width="50" height="24" rx="3" fill="#9cc9ea" stroke="currentColor" stroke-width="1"/>
<text x="383" y="257" font-size="13" text-anchor="middle" fill="currentColor">11</text>
<rect x="414" y="240" width="50" height="24" rx="3" fill="#9cc9ea" stroke="currentColor" stroke-width="1"/>
<text x="439" y="257" font-size="13" text-anchor="middle" fill="currentColor">11</text>
<rect x="470" y="240" width="50" height="24" rx="3" fill="#9cc9ea" stroke="currentColor" stroke-width="1"/>
<text x="495" y="257" font-size="13" text-anchor="middle" fill="currentColor">15</text>
<rect x="526" y="240" width="50" height="24" rx="3" fill="#9cc9ea" stroke="currentColor" stroke-width="1"/>
<text x="551" y="257" font-size="13" text-anchor="middle" fill="currentColor">16</text>
<rect x="582" y="240" width="50" height="24" rx="3" fill="#9cc9ea" stroke="currentColor" stroke-width="1"/>
<text x="607" y="257" font-size="13" text-anchor="middle" fill="currentColor">22</text>
</svg>
<figcaption>Figure 24.3. Blelloch's scan of 3, 1, 7, 0, 4, 1, 6, 3. Orange: cells changed by the up-sweep, which builds sums of blocks of 2, 4 and 8. Green: the total is replaced by 0. Blue: cells changed by the down-sweep, which hands each left child the sum of everything before it. The last row is the exclusive prefix sum.</figcaption>
</figure>

**Why it is correct.** Think of the up-sweep as computing, at each internal node of the tree, the sum of its left
subtree (stored at the left child's last cell) and of the whole subtree. The down-sweep maintains the invariant:
*the value arriving at a node is the sum of all elements before that node's subtree.* The root gets 0. A node passes
its incoming value to its left child unchanged (nothing new comes before the left subtree), and to its right child
the incoming value plus the left subtree's sum (everything before the right subtree). The swap-and-add step does
exactly this. At the leaves, "the sum of everything before this leaf" is the exclusive prefix sum. **Cost:** each
sweep does $n - 1$ additions in $\log_2 n$ rounds, so $W = O(n)$ and $S = O(\log n)$. The simpler scan of Hillis
and Steele (1986) has span $\log n$ too but does $n \log n$ work.

Prefix sums are a building block of parallel algorithms the way loops are of sequential ones: parallel radix sort
(each processor finds where its keys go), stream compaction (keep the items satisfying a test, in order), the
carry-lookahead adder in every processor (carries are a prefix computation), and recurrences such as
$y_i = a_i y_{i-1} + b_i$ (by scanning with composition of linear maps, which is associative).

```python
--8<-- "books/algorithms/ch24_parallel.py"
```

```
Blelloch scan: work W, span S, and greedy time T_p on p processors
  n=   16: W=   31, S=  9;  T_1=31 (bound 40), T_4=11 (bound 17), T_16=9 (bound 11), T_64=9 (bound 9)
  n=  256: W=  511, S= 17;  T_1=511 (bound 528), T_4=131 (bound 145), T_16=39 (bound 49), T_64=19 (bound 25)
  n= 1024: W= 2047, S= 21;  T_1=2047 (bound 2068), T_4=515 (bound 533), T_16=135 (bound 149), T_64=43 (bound 53)

reducer 0: [('dust', 2), ('over', 1), ('planet', 2), ('rover', 2)]
reducer 1: [('drives', 1), ('on', 2), ('red', 3), ('storm', 2), ('the', 3)]
```

The task graph has $W = 2n - 1$ tasks ($n - 1$ in each sweep, plus clearing the last cell) and span
$S = 2\log_2 n + 1$. Every greedy time is within Brent's bound, and with $p \ll W/S$ processors the time is close to
$W/p$.

**Amdahl's law.** If a fraction $f$ of a program's work can be parallelised and the rest cannot, then with $p$
processors the speed-up is at most

$$
\frac{1}{(1 - f) + f/p} < \frac{1}{1 - f} .
$$

With $f = 0.95$, no number of processors gives more than 20 times. (Gene Amdahl made the argument in 1967; John
Gustafson replied in 1988 that in practice bigger machines are used for bigger problems, where $f$ grows.) In the
work-span model this is the statement $T_p \ge S$.

**MapReduce (Dean and Ghemawat, 2004).** At the scale of thousands of machines, the hard part is not the
arithmetic but the failures, the network and the programming. MapReduce asks the programmer for two functions only:

- `map(record)` returns a list of (key, value) pairs;
- `reduce(key, list of values)` returns the result for that key.

The system runs the map function on every input piece in parallel, **shuffles** the pairs so that all pairs with
the same key reach the same reducer (by hashing the key, as in our program), runs the reducers in parallel, and
re-runs any task whose machine fails, which is safe because map and reduce have no side effects. Word counting,
building an inverted index for search, and computing link statistics fit this shape. Iterative algorithms fit
badly, since each round writes everything to disk; that led to systems such as Spark (Zaharia and others, 2012)
that keep data in memory between rounds. Theorists model these systems as the **massively parallel computation**
(MPC) model: machines with memory $n^{\delta}$ for some $\delta < 1$, communicating in synchronous rounds, where the
cost is the number of rounds.

## 24.6 Distributed algorithms briefly: consensus, and why it is hard

*Level: advanced.*

In parallel computing the processors cooperate under one scheduler and share memory or a fast network. In a
**distributed system** the computers are independent: they communicate only by messages, messages are delayed,
and computers fail. A database replicated on five machines must still agree on the order of the updates if two of
them crash. A team on Mars and a control centre on Earth, separated by a one-way light time of 3 to 22 minutes,
cannot run a protocol that waits for an answer at every step; that delay is one reason Mars rovers such as
Perseverance drive with onboard autonomy (AutoNav) instead of being steered from Earth.

**Consensus.** Each of $n$ processes starts with an input value. Each process that does not fail must eventually
**decide** a value, subject to:

- **agreement:** no two processes decide differently;
- **validity:** the decided value is some process's input;
- **termination:** every non-faulty process eventually decides.

Consensus is the core of replication: if replicas agree, one decision at a time, on the next operation in a log,
they stay identical (the **state machine** approach, Lamport 1978 and Schneider 1990).

**Synchronous rounds with crashes.** Suppose computation proceeds in rounds: in each round every live process sends
messages, all messages sent are delivered before the round ends, and then each process computes. Up to $f$
processes may **crash**: stop forever, possibly in the middle of sending, so that only some processes receive their
last message. The **FloodSet** algorithm: each process keeps the set $W$ of values it has seen, starting with its
input; in each of $f + 1$ rounds it sends $W$ to everyone and adds whatever it receives; at the end it decides
$\min W$.

**Theorem.** FloodSet solves consensus with up to $f$ crashes in $f + 1$ rounds.

*Proof.* Validity and termination are clear. For agreement it is enough to show that all live processes end with
the same set $W$. Among $f + 1$ rounds at most $f$ contain a crash, so some round $r$ has none. In round $r$ every
live process sends its set to every other, so after round $r$ all live processes have the same set (the union of
their sets). From then on they all receive the same messages, so their sets stay equal. $\square$

Why not $f$ rounds? The program builds the bad run for $n = 4$, $f = 2$: only process 0 has input 0. In round 1
process 0 crashes after sending only to process 1. In round 2 process 1 crashes after sending only to process 2. At
the end of round 2, process 2 has seen 0 and process 3 has not: they decide differently. A third round, in which
nobody can crash any more, repairs it. The program then tries every input and crash pattern for $f = 1$ on 4
processes:

```python
--8<-- "books/algorithms/ch24_consensus.py"
```

```
2 rounds with f = 2 crashes: decisions {2: 0, 3: 1} -> DISAGREEMENT
3 rounds with f = 2 crashes: decisions {2: 0, 3: 0} -> agreement
f = 1, all inputs and crash patterns on 4 processes:
  1 round : 48 runs end in disagreement
  2 rounds: 0 runs end in disagreement
```

The simulation shows that FloodSet itself fails with $f$ rounds. A much stronger statement is true: **every**
algorithm needs $f + 1$ rounds in the worst case when $f < n - 1$ processes may crash. The bound comes from
Fischer and Lynch (1982), proved for a harder failure model, with the crash version in Lynch's textbook
(*Distributed Algorithms*, 1996). For **Byzantine** failures, where faulty processes may send arbitrary, even
malicious, messages, Lamport, Shostak and Pease (1982) showed that consensus is possible if and only if
$n \ge 3f + 1$ (without digital signatures); their "Byzantine generals" paper named the problem.

**Asynchrony and the FLP theorem.** Now drop the rounds: messages arrive eventually but with no bound on the delay,
and processes run at arbitrary speeds. A slow process and a crashed one then look the same from outside.

**Theorem (Fischer, Lynch and Paterson, 1985).** In an asynchronous message-passing system in which even one
process may crash, no deterministic algorithm solves consensus: for every algorithm there is a run in which no
process ever decides.

*Proof idea.* Call a global state of the system **bivalent** if both decisions 0 and 1 are still reachable from it,
and **univalent** otherwise. (1) Some initial state is bivalent: line up the input vectors from all zeros to all ones,
changing one process at a time; the decision must switch somewhere, between two states differing in one process's
input; if that process crashes at the start, nobody can tell the two states apart, so one of them must be bivalent.
(2) From any bivalent state, and for any message $m$ waiting to be delivered, there is a way to deliver some other
messages first and then $m$ that reaches another bivalent state. If not, delivering $m$ after any delay would give
a univalent state, and one finds two neighbouring cases, one leading to decision 0 and one to decision 1, that differ
only in the order of two steps. If those steps are at different processes they commute, which is a contradiction;
if they are at the same process $P$, let $P$ stop taking steps: the others must still decide (one crash is allowed),
and they cannot tell the two cases apart, another contradiction. (3) Repeating (2) forever, delivering every message eventually,
gives a run that is fair to all processes yet stays bivalent forever: no one decides. $\square$

FLP does not say consensus is impossible in practice. It says that **safety** (agreement) and **liveness**
(termination) cannot both be *guaranteed* when timing is unbounded. Practical systems choose to keep agreement
always and to terminate when the network behaves:

- **partial synchrony** (Dwork, Lynch and Stockmeyer, 1988): delays are bounded after some unknown time; algorithms
  decide once that time comes;
- **randomization** (Ben-Or, 1983): processes flip coins, and decision happens with probability 1;
- **failure detectors** (Chandra and Toueg, 1996): add an oracle that eventually suspects crashed processes.

Leslie Lamport's **Paxos** (written in 1989, published as "The Part-Time Parliament" in 1998) and Diego Ongaro and
John Ousterhout's **Raft** (2014) are the consensus algorithms behind many replicated databases and configuration
stores (etcd, ZooKeeper's ZAB is a close relative). They never let replicas disagree, and they make progress
whenever a majority can talk to one leader with bounded delay. Between Earth and Mars, with round trips of 8 to
48 minutes, such a protocol would still be safe but each decision would take an hour, which is why designs for
interplanetary systems lean on local autonomy and delay-tolerant networking rather than on tight agreement.

## Check yourself

??? question "1. In ski rental with B = 4, what is the worst-case ratio of 'buy on day 2', and which season length achieves it?"
    Buying on day 2 costs 1 (rent day 1) + 4 = 5 for any season of 2 or more days. OPT is $\min(d, 4)$. The worst
    case is $d = 2$: $5/2 = 2.5$. (For $d = 1$ the cost is 1 = OPT.) The best deterministic choice, buy on day 4,
    has ratio $2 - 1/4 = 1.75$.

??? question "2. Run LRU and Belady's MIN by hand with k = 2 frames on the requests a b c a b c. Count misses."
    LRU: a miss {a}; b miss {a,b}; c miss, evict a {b,c}; a miss, evict b {c,a}; b miss, evict c {a,b}; c miss,
    evict a {b,c}: 6 misses. MIN: a, b miss {a,b}; c miss: next uses are a at 4, b at 5, so evict b {a,c}; a hit;
    b miss: next uses c at 6, a never, evict a {c,b}; c hit. 4 misses. (The cold misses a, b, c are unavoidable.)

??? question "3. Show that LRU is k-competitive but that this is not 'k times slower in practice': give a sequence on which LRU and OPT make the same number of misses."
    Any sequence using at most $k$ distinct pages: both make exactly one miss per distinct page (the cold misses)
    and then only hits. More generally, the phase argument shows LRU is bad only when each phase brings $k$ new
    pages that push out pages needed soon, as in a loop over $k + 1$ pages.

??? question "4. Run Misra-Gries with k = 3 (two counters) on the stream a b a c a b d a. Which items survive, and does the bound hold?"
    a: {a:1}. b: {a:1, b:1}. a: {a:2, b:1}. c: no room, decrement all: {a:1} (b reaches 0). a: {a:2}. b:
    {a:2, b:1}. d: decrement: {a:1}. a: {a:2}. The answer is a with estimate 2; its true count is 4, and $n/k =
    8/3 \approx 2.67$, so the estimate is within the bound ($4 - 2.67 \le 2 \le 4$). a occurs more than $n/k$ times
    and indeed survives; no other item occurs more than 2.67 times.

??? question "5. Write the code: a Misra-Gries summary for two streams computed separately, then merged. (Merge rule: add the counters, then subtract the k-th largest count from all and drop the non-positive ones.)"
    ```python
    from collections import Counter

    def mg(stream, k):
        c = {}
        for x in stream:
            if x in c:
                c[x] += 1
            elif len(c) < k - 1:
                c[x] = 1
            else:
                for y in list(c):
                    c[y] -= 1
                    if c[y] == 0:
                        del c[y]
        return c

    def merge(c1, c2, k):
        c = Counter(c1) + Counter(c2)
        if len(c) >= k:
            kth = sorted(c.values(), reverse=True)[k - 1]
            c = {x: v - kth for x, v in c.items() if v > kth}
        return dict(c)

    s1, s2 = "aabacada", "bbcbbdbe"
    print(mg(s1, 3), mg(s2, 3), merge(mg(s1, 3), mg(s2, 3), 3))
    # {'a': 4, 'd': 1} {'b': 4, 'e': 1} {'a': 3, 'b': 3}
    ```
    Subtracting the $k$-th largest count removes at least $k$ times that amount of total count, so the same proof
    shows the merged error stays at most $(n_1 + n_2)/k$ (Agarwal, Cormode, Huang, Phillips, Wei and Yi, 2012,
    "Mergeable summaries").

??? question "6. A count-min sketch should estimate frequencies within 0.1 percent of the stream length, failing with probability at most 1 in a million. How many counters does it need?"
    $\varepsilon = 0.001$ gives $w = \lceil e / 0.001 \rceil = 2719$. $\delta = 10^{-6}$ gives
    $d = \lceil \ln 10^6 \rceil = \lceil 13.8 \rceil = 14$. Total $2719 \times 14 = 38{,}066$ counters, whatever
    the length of the stream or the number of distinct items.

??? question "7. Why does HyperLogLog ignore repeated items, while count-min counts them?"
    HyperLogLog's registers store a maximum over hash values. A repeated item has the same hash, so it produces the
    same register and the same rank, and a maximum does not change when the same value is offered twice. Count-min
    adds 1 for every arrival, so it counts occurrences. That is the difference between estimating the number of
    distinct items ($F_0$) and frequencies.

??? question "8. External merge sort: N = 10^9 records, M = 10^7, B = 10^4. How many merge passes and I/Os? How many passes would a 2-way merge need?"
    Pass 0 makes $N/M = 100$ runs. The fan-in is $M/B - 1 = 999$, so one merge pass suffices. I/Os:
    $2(N/B)(1 + 1) = 2 \cdot 10^5 \cdot 2 = 4 \cdot 10^5$. A 2-way merge needs $\lceil \log_2 100 \rceil = 7$
    merge passes, so $2 \cdot 10^5 \cdot 8 = 1.6 \cdot 10^6$ I/Os, four times more.

??? question "9. A parallel algorithm has work n log n and span log^2 n. For n = 2^20, what does Brent's theorem give on 64 processors, and roughly how many processors can be used before the span dominates?"
    $W = 2^{20} \cdot 20 \approx 2.1 \times 10^7$ and $S = 400$. Brent: $T_{64} \le W/64 + S \approx 327{,}680 + 400$,
    essentially perfect speed-up. The parallelism is $W/S \approx 52{,}000$: beyond tens of thousands of
    processors the $S$ term takes over.

??? question "10. Write the code: an inclusive prefix sum computed by the Hillis-Steele method, and count its additions."
    In round $d = 1, 2, 4, \dots$, every $i \ge d$ adds the value $d$ places to its left (all reads first, then all
    writes).
    ```python
    def hillis_steele(x):
        a, d, adds = x[:], 1, 0
        while d < len(a):
            a = [a[i] + (a[i - d] if i >= d else 0) for i in range(len(a))]
            adds += len(a) - d
            d *= 2
        return a, adds

    print(hillis_steele([3, 1, 7, 0, 4, 1, 6, 3]))
    # ([3, 4, 11, 11, 15, 16, 22, 25], 17)
    ```
    It has span $\log_2 n$ (3 rounds for 8 numbers) but does $\sum_d (n - d) \approx n \log_2 n - n$ additions (17
    here, against 7 for a sequential loop): faster when processors are plentiful, wasteful otherwise.

??? question "11. In the FloodSet proof, where exactly is the assumption 'at most f crashes' used, and what happens with f + 1 crashes?"
    It guarantees that among $f + 1$ rounds at least one has no crash, which is the round in which all live
    processes equalise their sets. With $f + 1$ crashes, the adversary can crash one process per round in a chain,
    as in the program's run, and the last link in the chain reaches only some processes; then the survivors can
    disagree. The algorithm would need $f + 2$ rounds.

??? question "12. Why does the FLP theorem not contradict the fact that Paxos and Raft are used in real systems every day?"
    FLP shows that every deterministic asynchronous protocol has *some* run, under some schedule of delays, in which
    it never decides. Paxos and Raft never violate agreement in any run; what they give up is guaranteed
    termination: under a bad schedule (for example leaders repeatedly timing out each other) they can stall. They
    decide whenever the network is well-behaved for long enough, which real networks usually are. That matches
    FLP's limit exactly: safety always, liveness only under extra timing assumptions.

## What you learned

- Online algorithms are judged by the competitive ratio against an offline optimum: ski rental's rent-then-buy is
  $(2 - 1/B)$-competitive, LRU is $k$-competitive, and both bounds are best possible for deterministic algorithms;
  randomization improves them to about $e/(e-1)$ and $2H_k$.
- Streaming algorithms need both randomness and approximation: Misra-Gries finds heavy hitters with $k$ counters,
  count-min estimates frequencies within $\varepsilon n$, HyperLogLog counts distinct items within a few percent
  in under a kilobyte.
- In the I/O model only block transfers count: scanning costs $N/B$, searching $\log_B N$ (B-trees), sorting
  $\frac NB \log_{M/B} \frac NB$ (multiway external merge sort).
- Cache-oblivious algorithms, recursive by design, are optimal at every level of the memory hierarchy without
  knowing its sizes.
- Parallel algorithms are measured by work and span; a greedy scheduler achieves $T_p \le W/p + S$; prefix sums
  run in $O(n)$ work and $O(\log n)$ span; MapReduce hides machines and failures behind map, shuffle and reduce.
- Consensus with $f$ crashes needs $f + 1$ synchronous rounds; asynchronously it cannot be guaranteed (FLP), so
  real protocols such as Paxos and Raft keep safety always and liveness when the network allows.

**Next:** [Chapter 25](25-Where-Algorithms-Go.md), the open problems and recent breakthroughs at the frontier of
algorithms.

## Further reading

- A. Borodin and R. El-Yaniv, *Online Computation and Competitive Analysis*, 1998.
- D. D. Sleator and R. E. Tarjan, "Amortized efficiency of list update and paging rules", *Communications of the
  ACM* 28, 1985; L. A. Belady, "A study of replacement algorithms for a virtual-storage computer", *IBM Systems
  Journal* 5, 1966.
- J. Misra and D. Gries, "Finding repeated elements", *Science of Computer Programming* 2, 1982.
- N. Alon, Y. Matias and M. Szegedy, "The space complexity of approximating the frequency moments", STOC 1996.
- G. Cormode and S. Muthukrishnan, "An improved data stream summary: the count-min sketch and its applications",
  *Journal of Algorithms* 55, 2005.
- P. Flajolet, É. Fusy, O. Gandouet and F. Meunier, "HyperLogLog: the analysis of a near-optimal cardinality
  estimation algorithm", AofA 2007; P. Flajolet and G. N. Martin, "Probabilistic counting algorithms for data base
  applications", *JCSS* 31, 1985.
- A. Aggarwal and J. S. Vitter, "The input/output complexity of sorting and related problems", *Communications of
  the ACM* 31, 1988; J. S. Vitter, *Algorithms and Data Structures for External Memory*, 2008.
- M. Frigo, C. E. Leiserson, H. Prokop and S. Ramachandran, "Cache-oblivious algorithms", FOCS 1999.
- R. P. Brent, "The parallel evaluation of general arithmetic expressions", *Journal of the ACM* 21, 1974;
  G. E. Blelloch, "Prefix sums and their applications", 1990; CLRS chapter 26 (parallel algorithms).
- J. Dean and S. Ghemawat, "MapReduce: simplified data processing on large clusters", OSDI 2004.
- M. J. Fischer, N. A. Lynch and M. S. Paterson, "Impossibility of distributed consensus with one faulty process",
  *Journal of the ACM* 32, 1985; N. A. Lynch, *Distributed Algorithms*, 1996.
- L. Lamport, R. Shostak and M. Pease, "The Byzantine generals problem", *ACM TOPLAS* 4, 1982; L. Lamport, "The
  part-time parliament", *ACM TOCS* 16, 1998; D. Ongaro and J. Ousterhout, "In search of an understandable
  consensus algorithm", USENIX ATC 2014.
- On this site: [merge sort](../../sorting/merge-sort.md), [hash tables](../../data-structures/hash-table.md),
  [Chapter 21](21-Randomized-and-Amortized-Analysis.md), [Chapter 8](08-Trees-and-Balanced-Search-Trees.md).
