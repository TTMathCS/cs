# 7. Searching and hashing

*Most programs spend their lives looking things up: is this user logged in, what is the price of this item, have we
seen this web page before, which waypoint has this name? This chapter answers the question "how fast can we find
something?" twice. First for sorted data, with binary search, the simplest algorithm that almost everyone gets wrong the
first time; you will prove it correct with an invariant and see the exact bugs it invites. Then for data in no order at
all, with hash tables, which find a key in expected constant time. You will build chaining and open addressing from
scratch, prove their costs, see why a fixed hash function can be attacked and how random ("universal") hashing defends
against it, meet perfect hashing, cuckoo hashing and Bloom filters, and finish inside Python's own `dict`.*

!!! abstract "In this chapter"
    **You will learn:**

    - linear and binary search, a binary search written from an invariant, the classic off-by-one bugs, and
      exponential search
    - binary search on the answer: searching a space of possible answers instead of an array
    - the dictionary problem, and why direct addressing and hashing solve it
    - hash tables with chaining, the load factor, and a proof of expected $O(1+\alpha)$ time under simple uniform hashing
    - open addressing (linear probing, quadratic probing, double hashing), deletion with tombstones, and the probe
      formulas, measured
    - universal hashing (Carter and Wegman 1979) with a proof of its collision bound; perfect, cuckoo and Robin Hood
      hashing
    - Bloom filters with their false-positive rate derived, and how Python's `dict` really works

    **You need:** loop invariants from [Chapter 1](01-What-Is-an-Algorithm.md), dynamic arrays and amortized doubling
    from [Chapter 4](04-Lists-Stacks-and-Queues.md), and sorting from [Chapter 5](05-Sorting-by-Comparison.md). For
    7.3 to 7.7 you need expectation and linearity of expectation, as used in [Chapter 5](05-Sorting-by-Comparison.md),
    5.4, and [Chapter 6](06-Sorting-in-Linear-Time-and-Selection.md), 6.3.

    **Levels:** 7.1 and 7.2 are beginner; 7.3, 7.4, 7.7 and 7.8 are intermediate; 7.5 and 7.6 are advanced.

## 7.1 Linear and binary search

### Linear search

The most basic search: look at every item in turn until you find the one you want.

```python
def linear_search(a, x):
    for i, v in enumerate(a):
        if v == x:
            return i
    return -1
```

It works on any list, sorted or not, and it costs up to $n$ comparisons. If $x$ is absent, all $n$ are needed, and
that is optimal for an unordered list: if an algorithm skipped some position, an adversary could hide $x$ exactly
there. You proved its loop invariant ("$x$ is not in $a[0..i-1]$") in [Chapter 1](01-What-Is-an-Algorithm.md).

### Binary search

If the list is **sorted**, we can do enormously better. Look at the middle item. If it is smaller than $x$, then $x$
cannot be in the left half (everything there is even smaller), so throw the left half away. Otherwise throw the right
half away. Each comparison halves the part that remains, so after about $\log_2 n$ comparisons one candidate is left.
For a million items that is 20 comparisons instead of a million. A phone book (when there were phone books) was
searched this way by everyone.

The idea is easy. The details are famously not. Jon Bentley reported in *Programming Pearls* that when he asked
professional programmers to write binary search, most of their programs had bugs, and Knuth notes in *TAOCP* volume 3
that although the first binary search was published in 1946, the first version correct for every $n$ appeared only
around 1960. So let us write it from an invariant, which is the reliable way.

We solve a slightly more useful problem. **Lower bound:** given a sorted list $a$ and a value $x$, find the first index
$i$ with $a[i]\ge x$ (or $n$ if there is none). That one index answers every question: $x$ is present exactly when
$i<n$ and $a[i]=x$; it is the place where $x$ should be inserted to keep the list sorted; and the number of items
smaller than $x$ is $i$.

```python
def lower_bound(a, x):
    lo, hi = 0, len(a)
    # Invariant: every item in a[:lo] is < x, and every item in a[hi:] is >= x.
    while lo < hi:
        mid = (lo + hi) // 2
        if a[mid] < x:
            lo = mid + 1      # a[mid] < x, so everything up to mid is < x
        else:
            hi = mid          # a[mid] >= x, so everything from mid on is >= x
    return lo
```

<figure class="mars-fig" markdown="0">
<svg viewBox="0 0 640 230" role="img" aria-label="Binary search for 42 in the sorted array 3 8 15 21 30 42 57. Row 1: lo is 0, hi is 7, mid is 3 holding 21, which is less than 42, so lo becomes 4. Row 2: lo 4, hi 7, mid 5 holding 42, not less than 42, so hi becomes 5. Row 3: lo 4, hi 5, mid 4 holding 30, less than 42, so lo becomes 5. Row 4: lo equals hi equals 5, the answer, holding 42. Cells to the left of lo are known to be less than 42 and shaded blue; cells from hi on are known to be at least 42 and shaded orange.">
  <g font-size="13" fill="currentColor" text-anchor="middle" stroke="currentColor">
    <rect x="60" y="20" width="50" height="30" fill="none"/><text x="85" y="40" stroke="none">3</text>
    <rect x="110" y="20" width="50" height="30" fill="none"/><text x="135" y="40" stroke="none">8</text>
    <rect x="160" y="20" width="50" height="30" fill="none"/><text x="185" y="40" stroke="none">15</text>
    <rect x="210" y="20" width="50" height="30" fill="#7ccf9a" fill-opacity="0.6"/><text x="235" y="40" stroke="none">21</text>
    <rect x="260" y="20" width="50" height="30" fill="none"/><text x="285" y="40" stroke="none">30</text>
    <rect x="310" y="20" width="50" height="30" fill="none"/><text x="335" y="40" stroke="none">42</text>
    <rect x="360" y="20" width="50" height="30" fill="none"/><text x="385" y="40" stroke="none">57</text>
    <rect x="60" y="70" width="50" height="30" fill="#9cc9ea" fill-opacity="0.5"/><text x="85" y="90" stroke="none">3</text>
    <rect x="110" y="70" width="50" height="30" fill="#9cc9ea" fill-opacity="0.5"/><text x="135" y="90" stroke="none">8</text>
    <rect x="160" y="70" width="50" height="30" fill="#9cc9ea" fill-opacity="0.5"/><text x="185" y="90" stroke="none">15</text>
    <rect x="210" y="70" width="50" height="30" fill="#9cc9ea" fill-opacity="0.5"/><text x="235" y="90" stroke="none">21</text>
    <rect x="260" y="70" width="50" height="30" fill="none"/><text x="285" y="90" stroke="none">30</text>
    <rect x="310" y="70" width="50" height="30" fill="#7ccf9a" fill-opacity="0.6"/><text x="335" y="90" stroke="none">42</text>
    <rect x="360" y="70" width="50" height="30" fill="none"/><text x="385" y="90" stroke="none">57</text>
    <rect x="60" y="120" width="50" height="30" fill="#9cc9ea" fill-opacity="0.5"/><text x="85" y="140" stroke="none">3</text>
    <rect x="110" y="120" width="50" height="30" fill="#9cc9ea" fill-opacity="0.5"/><text x="135" y="140" stroke="none">8</text>
    <rect x="160" y="120" width="50" height="30" fill="#9cc9ea" fill-opacity="0.5"/><text x="185" y="140" stroke="none">15</text>
    <rect x="210" y="120" width="50" height="30" fill="#9cc9ea" fill-opacity="0.5"/><text x="235" y="140" stroke="none">21</text>
    <rect x="260" y="120" width="50" height="30" fill="#7ccf9a" fill-opacity="0.6"/><text x="285" y="140" stroke="none">30</text>
    <rect x="310" y="120" width="50" height="30" fill="#eea66f" fill-opacity="0.5"/><text x="335" y="140" stroke="none">42</text>
    <rect x="360" y="120" width="50" height="30" fill="#eea66f" fill-opacity="0.5"/><text x="385" y="140" stroke="none">57</text>
    <rect x="60" y="170" width="50" height="30" fill="#9cc9ea" fill-opacity="0.5"/><text x="85" y="190" stroke="none">3</text>
    <rect x="110" y="170" width="50" height="30" fill="#9cc9ea" fill-opacity="0.5"/><text x="135" y="190" stroke="none">8</text>
    <rect x="160" y="170" width="50" height="30" fill="#9cc9ea" fill-opacity="0.5"/><text x="185" y="190" stroke="none">15</text>
    <rect x="210" y="170" width="50" height="30" fill="#9cc9ea" fill-opacity="0.5"/><text x="235" y="190" stroke="none">21</text>
    <rect x="260" y="170" width="50" height="30" fill="#9cc9ea" fill-opacity="0.5"/><text x="285" y="190" stroke="none">30</text>
    <rect x="310" y="170" width="50" height="30" fill="#eea66f" fill-opacity="0.5"/><text x="335" y="190" stroke="none">42</text>
    <rect x="360" y="170" width="50" height="30" fill="#eea66f" fill-opacity="0.5"/><text x="385" y="190" stroke="none">57</text>
  </g>
  <g font-size="12" fill="currentColor">
    <text x="430" y="40">lo 0, hi 7, mid 3: 21 &lt; 42</text>
    <text x="430" y="90">lo 4, hi 7, mid 5: 42 ≥ 42</text>
    <text x="430" y="140">lo 4, hi 5, mid 4: 30 &lt; 42</text>
    <text x="430" y="190">lo = hi = 5: answer</text>
    <text x="235" y="222" text-anchor="middle">blue: known &lt; 42      orange: known ≥ 42      green: the probe</text>
  </g>
</svg>
<figcaption>Figure 7.1. Lower-bound binary search for 42. Each row shows the state before a probe. The blue part (left of lo) and the orange part (from hi on) only grow; the search ends when they meet.</figcaption>
</figure>

**Theorem.** If $a$ is sorted, `lower_bound` returns the first index $i$ with $a[i]\ge x$ (or $n$), after at most
$\lceil\log_2(n+1)\rceil$ probes.

*Proof of correctness.* *Initially* $a[:0]$ and $a[n:]$ are empty, so the invariant holds. *Maintenance:* $lo\le mid<hi$ because $mid$ is the floor of the average of $lo<hi$. If $a[mid]<x$ then, since $a$ is sorted, every item in
$a[lo..mid]$ is $\le a[mid]<x$; together with the invariant, all of $a[:mid+1]$ is $<x$, so setting $lo=mid+1$ keeps it.
If $a[mid]\ge x$, every item in $a[mid..]$ is $\ge x$, so setting $hi=mid$ keeps it. *Termination:* the gap $hi-lo$
shrinks by at least 1 every round (because $lo\le mid<hi$, both updates make it strictly smaller), so the loop ends,
with $lo=hi$. Then the invariant says $a[:lo]<x\le a[lo:]$: $lo$ is exactly the first index whose item is $\ge x$.

*Proof of the bound.* If the gap is $g=hi-lo$, the next gap is at most $\lfloor g/2\rfloor$: with $mid=lo+\lfloor g/2\rfloor$, the left choice leaves $\lfloor g/2\rfloor$ and the right choice leaves $g-\lfloor g/2\rfloor-1\le\lfloor g/2\rfloor$. Starting from $g=n$, after $t$ probes the gap is at most $\lfloor n/2^t\rfloor$, which is 0 once
$2^t>n$, that is, after $\lfloor\log_2 n\rfloor+1=\lceil\log_2(n+1)\rceil$ probes. $\square$

For $n=10^6$ that is 20, which the program confirms.

**It is optimal.** The decision-tree argument of [Chapter 5](05-Sorting-by-Comparison.md), 5.6, applies: the answer
is one of $n+1$ positions, each comparison has two outcomes, so some input needs $\lceil\log_2(n+1)\rceil$ comparisons.

### The classic bugs

Every bug in a binary search is a broken invariant or a broken termination argument. The usual ones:

- **`lo = mid` instead of `lo = mid + 1`.** When $hi=lo+1$, $mid=lo$, and if $a[mid]<x$ nothing changes: an infinite
  loop. The program shows the version with `hi = len(a) - 1` and `lo = mid` getting stuck at $lo=5$, $hi=6$ when
  searching for 57 in $[3,8,15,21,30,42,57]$. The termination proof above is exactly what rules this out.
- **Mixing conventions.** Half-open ranges $[lo,hi)$ use `while lo < hi` and `hi = mid`; closed ranges $[lo,hi]$ use
  `while lo <= hi`, `hi = mid - 1` and `lo = mid + 1`. Each is correct alone; a mixture usually is not. Choose one
  invariant and derive every line from it.
- **Overflow of `lo + hi`.** In languages with fixed-size integers, $(lo+hi)/2$ overflows when both are above half the
  largest integer. Joshua Bloch described in 2006 how this bug had sat for years in the binary search of the Java
  library (and in the one in *Programming Pearls*): it only showed up on arrays of over a billion items. The fix is
  `lo + (hi - lo) / 2`. Python's integers do not overflow, so the Python code here is safe.
- **Returning "found" too early.** A version that stops when $a[mid]=x$ returns *some* occurrence of $x$, not the first;
  for counting duplicates, or for "insert here", you want the lower bound (and the matching **upper bound**, the first
  index with $a[i]>x$; the number of copies of $x$ is the difference, Exercise 3).

Python's standard library has these two as `bisect.bisect_left` (lower bound) and `bisect.bisect_right` (upper bound);
the program checks our version against `bisect_left` on 2000 random queries.

### Exponential search

What if the list is huge, or has no known end (a sorted stream, a function), and the answer is probably near the
start? **Exponential search** (also called galloping or doubling search; Bentley and Yao, "An almost optimal algorithm
for unbounded searching", 1976) probes positions 1, 2, 4, 8, ... until it passes $x$, then binary searches in the last
gap. If the answer is at position $i$, the doubling takes about $\log_2 i$ probes and the binary search another
$\log_2 i$, about $2\log_2 i$ in all, *independent of $n$*. The program measures 4 probes for the item at index 3 of a
million-item list (binary search: 20), but 40 for an item at index 900 000. This is exactly the galloping mode of
Timsort's merge ([Chapter 5](05-Sorting-by-Comparison.md), 5.7): when one run keeps winning, the merge searches ahead
in it exponentially.

### Binary search on the answer

Binary search does not need an array. It needs a **monotone yes/no question** over an ordered range: a predicate
$P(v)$ that is false for small $v$ and true from some point on. Then binary search finds the first $v$ with $P(v)$ true,
with the same invariant ("$P$ is false below $lo$ and true from $hi$ on").

Example: a rover must drive a fixed route of legs of $400,250,600,150,300,500,200,350$ metres, in order, and must stop
only at waypoints at the end of a sol. What is the smallest daily driving limit $L$ that finishes the route in $D$ sols?
For a given $L$, a greedy scan answers "how many sols does $L$ need?": drive legs until the next one would pass $L$, then
start a new sol. The answer is monotone, because a bigger limit never needs more sols. So binary search over $L$ from
$\max(\text{legs})=600$ (anything smaller cannot drive the longest leg) to $\text{sum}=2750$ (one sol) finds the
smallest $L$ with $\text{sols}(L)\le D$. The program prints 2750 m for 1 sol, 1400 m for 2, 1050 m for 3, 800 m for 4 and
600 m for 8. Each answer costs $O(\log(\text{sum})\cdot n)$ time.

The same pattern computes the integer square root (the largest $r$ with $r^2\le n$; the program's `isqrt`), finds the
minimum capacity of a ship that delivers packages in $D$ days (the reference page
[Binary search on the answer](../../searching/binary-search-answer.md) works it through), and, with real numbers and a
fixed number of halvings, solves equations by **bisection**. See also [Binary search](../../searching/binary-search.md)
and, for sorted arrays scanned from both ends, [Two pointers](../../searching/two-pointers.md).

The whole program:

```python
--8<-- "books/algorithms/ch07_binary_search.py"
```

Output:

```
lower_bound and exponential_search agree with bisect.bisect_left on 2000 queries

binary search trace in [3, 8, 15, 21, 30, 42, 57] for 42:
  lo=0 hi=7 mid=3 a[mid]=21 -> right
  lo=4 hi=7 mid=5 a[mid]=42 -> left
  lo=4 hi=5 mid=4 a[mid]=30 -> right
  stop: lo = hi = 5, a[5] = 42

the 'lo = mid' bug, searching [3, 8, 15, 21, 30, 42, 57] for 57: stuck: lo = 5, hi = 6 forever

binary search in 1000000 items: at most 20 probes; ceil(log2(n+1)) = 20
linear search for the last item: 1000000 probes
  item at index      3: binary 20 probes, exponential  4 probes
  item at index    100: binary 20 probes, exponential 14 probes
  item at index  10000: binary 20 probes, exponential 28 probes
  item at index 900000: binary 20 probes, exponential 40 probes

binary search on the answer
  isqrt(10**12 + 7) = 1000000
  1 sols: drive at most 2750 m per sol
  2 sols: drive at most 1400 m per sol
  3 sols: drive at most 1050 m per sol
  4 sols: drive at most 800 m per sol
  8 sols: drive at most 600 m per sol
```

## 7.2 Dictionaries: looking things up by key

A **dictionary** (also called a map, symbol table or associative array) stores pairs (key, value) and supports three
operations:

- **insert**$(k,v)$: store value $v$ under key $k$ (replacing any old value);
- **lookup**$(k)$: return the value stored under $k$, or report that there is none;
- **delete**$(k)$: remove the pair with key $k$.

Keys might be identifiers, names, coordinates, or whole strings of text. This is an **abstract data type**
([Chapter 4](04-Lists-Stacks-and-Queues.md), 4.6): the operations are fixed, the implementation is our choice. Here are
the options so far, for $n$ stored keys:

| implementation | lookup | insert | delete | keeps keys in order? |
|---|---|---|---|---|
| unsorted list | $O(n)$ | $O(1)$ | $O(n)$ | no |
| sorted array + binary search | $O(\log n)$ | $O(n)$ | $O(n)$ | yes |
| balanced search tree ([Chapter 8](08-Trees-and-Balanced-Search-Trees.md)) | $O(\log n)$ | $O(\log n)$ | $O(\log n)$ | yes |
| direct-address table | $O(1)$ | $O(1)$ | $O(1)$ | yes, but memory $\Theta(U)$ |
| hash table | $O(1)$ expected | $O(1)$ expected (amortized) | $O(1)$ expected | no |

**Direct addressing** is the ideal case. If the keys are integers from a small **universe** $U=\{0,1,\dots,u-1\}$, keep
an array `T` of size $u$ and store the value of key $k$ in `T[k]`. Every operation is one array access. It is counting
sort's trick ([Chapter 6](06-Sorting-in-Linear-Time-and-Selection.md)) applied to lookups.

The problem is the size of $U$. Keys that are 64-bit numbers have $u=2^{64}$; keys that are strings of up to 20
letters have more than $26^{20}$. But we only ever store a few: a few thousand waypoint names, a few million users.
**Hashing** keeps direct addressing's speed with memory proportional to $n$ instead of $u$: a **hash function**
$h:U\to\{0,\dots,m-1\}$ maps each key to a slot of a table of size $m\approx n$, and we store $k$ in slot $h(k)$.

Since $u>m$, some keys must share a slot (by the pigeonhole principle): a **collision**. A hash table is a hash
function plus a rule for collisions. The two rules are chaining (7.3) and open addressing (7.4).

## 7.3 Hash functions and chaining

### Chaining

In **separate chaining**, slot $j$ holds a list (a **chain**) of all stored pairs whose key hashes to $j$. To look up
$k$, compute $h(k)$ and walk that chain comparing keys. To insert, look up first; if absent, add the pair to the chain.
To delete, remove it from the chain.

Example: $m=10$, $h(k)=k\bmod10$ (the last digit), inserting $23,47,13,90,33,58,7$. Slot 3 gets the chain $23,13,33$;
slot 7 gets $47,7$; slot 0 gets $90$; slot 8 gets $58$. Looking up 33 checks three keys; looking up 63 (absent) checks
three keys and fails.

<figure class="mars-fig" markdown="0">
<svg viewBox="0 0 640 300" role="img" aria-label="Two hash tables of 10 slots holding the keys 23, 47, 13, 90, 33, 58, 7 with h of k equal to k mod 10. Left, chaining: slot 0 holds 90, slot 3 a chain 23 then 13 then 33, slot 7 a chain 47 then 7, slot 8 holds 58. Right, linear probing: slot 0 holds 90, slot 3 holds 23, slot 4 holds 13, slot 5 holds 33, slot 7 holds 47, slot 8 holds 58, slot 9 holds 7; slots 1, 2 and 6 are empty. Curved arrows show 33 probing slots 3, 4, 5 and 7 probing 7, 8, 9.">
  <g font-size="13" fill="currentColor" text-anchor="middle">
    <text x="150" y="18">chaining</text>
    <text x="480" y="18">linear probing</text>
  </g>
  <g font-size="12" fill="currentColor" text-anchor="end">
    <text x="42" y="47">0</text><text x="42" y="73">1</text><text x="42" y="99">2</text><text x="42" y="125">3</text>
    <text x="42" y="151">4</text><text x="42" y="177">5</text><text x="42" y="203">6</text><text x="42" y="229">7</text>
    <text x="42" y="255">8</text><text x="42" y="281">9</text>
    <text x="402" y="47">0</text><text x="402" y="73">1</text><text x="402" y="99">2</text><text x="402" y="125">3</text>
    <text x="402" y="151">4</text><text x="402" y="177">5</text><text x="402" y="203">6</text><text x="402" y="229">7</text>
    <text x="402" y="255">8</text><text x="402" y="281">9</text>
  </g>
  <g stroke="currentColor" fill="none">
    <rect x="50" y="30" width="36" height="260"/>
    <line x1="50" y1="56" x2="86" y2="56"/><line x1="50" y1="82" x2="86" y2="82"/><line x1="50" y1="108" x2="86" y2="108"/>
    <line x1="50" y1="134" x2="86" y2="134"/><line x1="50" y1="160" x2="86" y2="160"/><line x1="50" y1="186" x2="86" y2="186"/>
    <line x1="50" y1="212" x2="86" y2="212"/><line x1="50" y1="238" x2="86" y2="238"/><line x1="50" y1="264" x2="86" y2="264"/>
    <rect x="410" y="30" width="60" height="260"/>
    <line x1="410" y1="56" x2="470" y2="56"/><line x1="410" y1="82" x2="470" y2="82"/><line x1="410" y1="108" x2="470" y2="108"/>
    <line x1="410" y1="134" x2="470" y2="134"/><line x1="410" y1="160" x2="470" y2="160"/><line x1="410" y1="186" x2="470" y2="186"/>
    <line x1="410" y1="212" x2="470" y2="212"/><line x1="410" y1="238" x2="470" y2="238"/><line x1="410" y1="264" x2="470" y2="264"/>
  </g>
  <g stroke="currentColor" stroke-width="1.2">
    <line x1="68" y1="43" x2="110" y2="43"/>
    <line x1="68" y1="121" x2="110" y2="121"/><line x1="150" y1="121" x2="170" y2="121"/><line x1="210" y1="121" x2="230" y2="121"/>
    <line x1="68" y1="225" x2="110" y2="225"/><line x1="150" y1="225" x2="170" y2="225"/>
    <line x1="68" y1="251" x2="110" y2="251"/>
  </g>
  <g font-size="13" fill="currentColor" text-anchor="middle" stroke="currentColor">
    <rect x="110" y="32" width="40" height="22" fill="#9cc9ea" fill-opacity="0.55"/><text x="130" y="48" stroke="none">90</text>
    <rect x="110" y="110" width="40" height="22" fill="#eea66f" fill-opacity="0.55"/><text x="130" y="126" stroke="none">23</text>
    <rect x="170" y="110" width="40" height="22" fill="#eea66f" fill-opacity="0.55"/><text x="190" y="126" stroke="none">13</text>
    <rect x="230" y="110" width="40" height="22" fill="#eea66f" fill-opacity="0.55"/><text x="250" y="126" stroke="none">33</text>
    <rect x="110" y="214" width="40" height="22" fill="#7ccf9a" fill-opacity="0.55"/><text x="130" y="230" stroke="none">47</text>
    <rect x="170" y="214" width="40" height="22" fill="#7ccf9a" fill-opacity="0.55"/><text x="190" y="230" stroke="none">7</text>
    <rect x="110" y="240" width="40" height="22" fill="#9cc9ea" fill-opacity="0.55"/><text x="130" y="256" stroke="none">58</text>
  </g>
  <g font-size="13" fill="currentColor" text-anchor="middle">
    <text x="440" y="48">90</text><text x="440" y="126">23</text><text x="440" y="152">13</text><text x="440" y="178">33</text>
    <text x="440" y="230">47</text><text x="440" y="256">58</text><text x="440" y="282">7</text>
  </g>
  <g fill="none" stroke-width="1.6">
    <path d="M 472 121 C 500 125, 500 143, 474 147" stroke="#eea66f"/>
    <path d="M 472 147 C 500 151, 500 169, 474 173" stroke="#eea66f"/>
    <path d="M 472 225 C 520 229, 520 247, 474 251" stroke="#7ccf9a"/>
    <path d="M 472 251 C 520 255, 520 273, 474 277" stroke="#7ccf9a"/>
  </g>
  <g font-size="12" fill="currentColor">
    <text x="525" y="152">33: slots 3, 4, 5</text>
    <text x="530" y="256">7: slots 7, 8, 9</text>
  </g>
</svg>
<figcaption>Figure 7.2. The same seven keys with h(k) = k mod 10. Chaining (left) keeps colliding keys in a list per slot. Linear probing (right) stores every key in the table itself, moving on to the next free slot, so keys that collided at slot 3 spill into slots 4 and 5.</figcaption>
</figure>

### The load factor and simple uniform hashing

With $n$ keys in $m$ slots, the **load factor** is $\alpha=n/m$, the average chain length. The worst case of chaining is
terrible: if all keys hash to one slot, lookups cost $\Theta(n)$, no better than a list. The average case depends on how
well $h$ spreads the keys, which is not something we can prove about a fixed $h$ and arbitrary keys. So we first
analyse an idealized model:

**Simple uniform hashing (SUHA):** each key is equally likely to hash to any of the $m$ slots, independently of where
other keys go.

**Theorem.** Under simple uniform hashing, in a table with chaining and load factor $\alpha$:

1. an unsuccessful lookup examines $\alpha$ keys on average, so costs $\Theta(1+\alpha)$;
2. a successful lookup of a key chosen uniformly among the $n$ stored ones examines $1+\frac\alpha2-\frac{\alpha}{2n}$
   keys on average, also $\Theta(1+\alpha)$.

*Proof.* (1) The key $k$ we look for is not in the table; it hashes to some slot $j$, and we examine the whole chain of
$j$. Each of the $n$ stored keys is in that chain with probability $1/m$, so by linearity of expectation the chain's
expected length is $n/m=\alpha$. Add $O(1)$ for computing $h(k)$.

(2) Number the stored keys $k_1,\dots,k_n$ in the order they were inserted, and assume new keys are added at the *end*
of their chain. Looking up $k_i$ examines $k_i$ itself plus every key in its chain inserted *before* it. For $j<i$, let
$X_{ij}=1$ if $h(k_j)=h(k_i)$; under SUHA, $E[X_{ij}]=1/m$. The expected number of keys examined, averaged over $i$, is

$$\frac1n\sum_{i=1}^{n}\Big(1+\sum_{j<i}E[X_{ij}]\Big)=1+\frac1{nm}\sum_{i=1}^{n}(i-1)=1+\frac{n-1}{2m}=1+\frac\alpha2-\frac\alpha{2n}.\qquad\square$$

(Adding new keys at the *front* of the chain, which is the usual choice because it is $O(1)$ without a tail pointer,
gives the same average by symmetry: the key then examines the keys inserted *after* it.)

**So keep $\alpha$ bounded.** If the table grows, by doubling $m$ and **rehashing** every key into the new table whenever
$\alpha$ passes a constant (the program uses 1; Java's `HashMap` uses 0.75), then $\alpha$ stays below that constant and
every operation is $O(1)$ in expectation. A rehash costs $\Theta(n)$, but it happens only after the number of keys has
doubled, so by the same aggregate argument as the dynamic array of [Chapter 4](04-Lists-Stacks-and-Queues.md), 4.2,
insertions cost $O(1)$ amortized. The program builds such a table and checks it against Python's `dict` after 20 000
random operations: 4911 keys in 8192 buckets, load 0.60, longest chain 2.

### What makes a good hash function?

SUHA is an idealization. Real hash functions are fixed formulas, and the goal is that *real* keys, which are far from
random (consecutive ID numbers, names that share prefixes, memory addresses that are all multiples of 16), still spread
evenly. Classic designs for integer keys:

- **Division method:** $h(k)=k\bmod m$. Fast. Bad if $m$ is a power of 2, because $k\bmod2^p$ is just the lowest $p$ bits
  of $k$, and keys that agree in their low bits (all addresses aligned to 16) collide (Exercise 8). A prime $m$ not close
  to a power of 2 is the traditional choice.
- **Multiplication method:** $h(k)=\lfloor m\cdot\mathrm{frac}(kA)\rfloor$ for a constant $0<A<1$, where $\mathrm{frac}$
  is the fractional part. Knuth suggests $A=(\sqrt5-1)/2\approx0.618$. With $m=2^p$ and $w$-bit words it is computed as
  "multiply by a $w$-bit constant and keep the top $p$ bits of the low word", which is very fast; with a random odd
  constant this is the **multiply-shift** scheme of Dietzfelbinger, Hagerup, Katajainen and Penttonen (1997), which comes
  with a proven collision bound of $2/m$ (a near-universal family, 7.5).
- **Strings:** treat the characters as digits of a number in base $B$ and reduce: $h(s)=(s_0B^{L-1}+s_1B^{L-2}+\cdots+s_{L-1})\bmod M$, computed left to right by Horner's rule, $h\leftarrow(hB+s_i)\bmod M$. Java's `String.hashCode` is this with
  $B=31$ and $M=2^{32}$ (the reference page [Hash table](../../data-structures/hash-table.md) implements it). The same
  polynomial, updated as a window slides along a text, is the rolling hash of Rabin-Karp string matching
  ([Chapter 18](18-String-Algorithms.md)).

Two different requirements are often confused. A hash function for tables needs to be **fast and spread keys evenly**.
A **cryptographic** hash function (SHA-256) must also make it infeasible to find collisions or invert it, and is much
slower; the [cryptography book](https://cryptography.akadian.ca/book/) builds them. Hash tables need the first kind,
plus, as 7.5 shows, a secret random ingredient when keys may come from an adversary.

### Collisions come early: the birthday paradox

How full can a table be before the first collision? With $m$ slots and keys placed uniformly at random, the probability
that $n$ keys all land in different slots is

$$\Big(1-\frac1m\Big)\Big(1-\frac2m\Big)\cdots\Big(1-\frac{n-1}m\Big)\le e^{-(1+2+\cdots+(n-1))/m}=e^{-n(n-1)/(2m)},$$

using $1-x\le e^{-x}$. This drops below $\tfrac12$ once $n(n-1)>2m\ln2$, around $n\approx1.18\sqrt m$. With 365 "slots"
that is 23 people, the famous birthday paradox. The expected number of keys up to and including the first collision is
about $\sqrt{\pi m/2}$; for $m=10^6$ slots that is 1253, and the program measured 1233 on average over 2000 trials. So
collisions are not a sign of a bad hash function. They are certain once $n$ is much bigger than $\sqrt m$, and a hash
table must handle them gracefully.

## 7.4 Open addressing

Chaining needs a list per slot: extra pointers, extra memory allocations, and the chain nodes scattered in memory.
**Open addressing** stores every key in the table array itself. When the slot $h(k)$ is taken, the key tries a
sequence of other slots, its **probe sequence** $h(k,0),h(k,1),h(k,2),\dots$, and takes the first free one. Lookups
follow the same sequence until they find the key or an empty slot (which proves the key is absent, since an insertion
would have stopped there). The load factor must stay below 1, since every key needs its own slot.

Three standard probe sequences:

- **Linear probing:** $h(k,i)=(h(k)+i)\bmod m$. Try the next slot, then the next.
- **Quadratic probing:** $h(k,i)=(h(k)+c_1i+c_2i^2)\bmod m$. A common choice for $m$ a power of 2 is the triangular
  numbers $i(i+1)/2$, which visit every slot (Exercise 6).
- **Double hashing:** $h(k,i)=(h_1(k)+i\,h_2(k))\bmod m$, with a second hash function $h_2$ whose values are coprime to
  $m$ (for $m$ a power of 2, make $h_2(k)$ odd; for $m$ prime, any value in $1..m-1$). Each key then gets its own step
  size.

**Linear probing, traced.** Insert $23,47,13,90,33,58,7$ into $m=10$ slots with $h(k)=k\bmod10$ (Figure 7.2, right).
23 goes to slot 3, 47 to 7. 13 wants 3 (taken), takes 4. 90 takes 0. 33 wants 3, finds 3 and 4 taken, takes 5. 58 takes 8.
7 wants 7, finds 7 and 8 taken, takes 9. Final table: slot 0: 90, 3: 23, 4: 13, 5: 33, 7: 47, 8: 58, 9: 7.

A successful lookup costs 1 probe for 23, 47, 90, 58; 2 for 13; 3 for 33 and 7: on average $12/7\approx1.71$. An
unsuccessful lookup for a key hashing to slot 3 walks 3, 4, 5 and stops at the empty slot 6: 4 probes. For a key hashing
to 7 it walks 7, 8, 9, 0 and stops at 1: 5 probes. Averaged over the 10 possible home slots, an unsuccessful lookup costs
2.6 probes (Exercise 5).

**Clustering.** Linear probing's weakness is visible here: occupied slots form runs (**clusters**), and a cluster grows
faster the longer it is, because any key that hashes anywhere into it lands at its end. This is **primary clustering**.
Quadratic probing avoids it, but keys with the *same* home slot still follow the same sequence (**secondary
clustering**). Double hashing avoids both, because two keys that collide at the first probe usually have different step
sizes. With $m=11$, $h_1(k)=k\bmod11$ and $h_2(k)=1+(k\bmod10)$, inserting $23,47,13,90$: 23 goes to slot 1, 47 to 3, 13 to
2; then 90 has $h_1=2$ (taken) and step $h_2=1$, so it probes 3 (taken) and settles in 4.

### How many probes? The analysis

The idealized model for open addressing is **uniform hashing**: each key's probe sequence is equally likely to be any of
the $m!$ orderings of the slots. (Double hashing comes close to it; linear probing does not.)

**Theorem.** Under uniform hashing with load factor $\alpha=n/m<1$:

1. an unsuccessful lookup (and an insertion) makes at most $\frac1{1-\alpha}$ probes in expectation;
2. a successful lookup makes at most $\frac1\alpha\ln\frac1{1-\alpha}$ probes in expectation.

*Proof.* (1) The first probe hits an occupied slot with probability $\frac nm=\alpha$. Given that, the second probe is to
a different slot, uniform among the remaining $m-1$, of which $n-1$ are occupied: probability $\frac{n-1}{m-1}\le\alpha$.
In general, the probability that the first $i-1$ probes all hit occupied slots is

$$\frac nm\cdot\frac{n-1}{m-1}\cdots\frac{n-i+2}{m-i+2}\le\alpha^{i-1}.$$

The number of probes $X$ is at least $i$ exactly when the first $i-1$ probes all hit occupied slots. For a random
variable taking values $1,2,3,\dots$, $E[X]=\sum_{i\ge1}P(X\ge i)$, so

$$E[X]\le\sum_{i\ge1}\alpha^{i-1}=1+\alpha+\alpha^2+\cdots=\frac1{1-\alpha}.$$

(2) A successful lookup of a key follows the same probe sequence as when that key was inserted. If it was the
$(i+1)$-th key inserted, the table then held $i$ keys, so by (1) its insertion took at most $\frac1{1-i/m}=\frac m{m-i}$
probes. Averaging over the $n$ keys,

$$\frac1n\sum_{i=0}^{n-1}\frac m{m-i}=\frac mn\sum_{j=m-n+1}^{m}\frac1j\le\frac1\alpha\int_{m-n}^{m}\frac{dx}x=\frac1\alpha\ln\frac m{m-n}=\frac1\alpha\ln\frac1{1-\alpha}.$$

The inequality bounds a decreasing sum by an integral. $\square$

At $\alpha=\tfrac12$: at most 2 probes for a miss and 1.39 for a hit. At $\alpha=0.9$: 10 and 2.56. Hits stay cheap;
misses get expensive as the table fills.

**Linear probing** is not uniform hashing, and its clusters cost more. In 1962 Donald Knuth worked out its exact
behaviour, assuming a truly random hash function: about $\frac12\big(1+\frac1{1-\alpha}\big)$ probes for a hit and
$\frac12\big(1+\frac1{(1-\alpha)^2}\big)$ for a miss (*TAOCP* volume 3, 6.4). The miss cost grows like the *square* of
$\frac1{1-\alpha}$: at $\alpha=0.9$, about 50 probes. The program builds tables of 65 536 slots and measures:

```
open addressing, m = 65536: average slots examined (measured / formula)
  alpha         linear hit        linear miss         double hit        double miss
   0.50      1.50 /   1.50      2.58 /   2.50      1.38 /   1.39      2.00 /   2.00
   0.75      2.50 /   2.50      8.86 /   8.50      1.82 /   1.85      3.97 /   4.00
   0.90      5.12 /   5.50     40.97 /  50.50      2.53 /   2.56      9.85 /  10.00
```

Double hashing matches the uniform-hashing formulas almost exactly. Linear probing matches Knuth's formulas at
$\alpha=0.5$ and $0.75$; at $0.9$ the measured miss cost (41) is below the formula (50.5) because the formula is the
limit for very large tables and the cost at high load has a very large spread: a few huge clusters dominate, and 5000
random misses sample them unevenly.

**So why does anyone use linear probing?** Because on real hardware a probe to the *next* slot is almost free: it is
usually in the same cache line, already loaded. Two or three extra probes in one cache line beat one extra probe that
misses the cache. At moderate load ($\alpha\le0.7$ or so), linear probing is often the fastest table there is. Its
theory also caught up: Pagh, Pagh and Ružić (2007) proved that linear probing has constant expected cost with any
5-wise independent hash family, and Pătraşcu and Thorup (2011) showed that simple **tabulation hashing** (XOR together
random table entries indexed by the bytes of the key) suffices.

### Deletion and tombstones

Deleting from open addressing is subtle. In the linear probing example, delete 13 (in slot 4) by simply emptying the
slot. Now look up 33: start at slot 3 (23, not it), go to slot 4: empty, so report "absent". Wrong! 33 is in slot 5, but
the hole cut its probe sequence.

The fix is a **tombstone**: mark the slot as "deleted" instead of "empty". Lookups treat a tombstone as occupied (keep
probing past it); insertions may reuse it (after checking the key is not further along the sequence). The program builds
exactly this case with three keys hashing to one slot: after deleting the first, the third is still found with a
tombstone and lost without one.

Tombstones have a cost: they keep probe sequences long even when few live keys remain. A table with many deletions must
be rebuilt (rehashed) from time to time, counting tombstones toward the load factor. With linear probing there is an
alternative: after emptying a slot, scan forward through the cluster and move back any key that can legally fill the hole
(Knuth's Algorithm R in *TAOCP* 6.4), which leaves no tombstones at all.

## 7.5 Universal hashing

*Level: advanced.*

Every fixed hash function has a bad set of keys: since $u>m$, by pigeonhole at least $u/m$ keys share some slot, and an
adversary who knows $h$ can insert only those. The program shows it with $h(x)=x\bmod1024$ and 2000 keys that are
multiples of 1024: every key lands in slot 0, a chain of 2000.

This is not a theoretical worry. In 2003 Crosby and Wallach ("Denial of Service via Algorithmic Complexity Attacks",
USENIX Security) showed that sending specially chosen inputs to programs that store them in hash tables could slow those
programs to a crawl; in 2011 the same idea against the hash tables that web frameworks use for request parameters forced
many languages, Python among them, to change how they hash strings.

The defence is the same as for quicksort's pivot ([Chapter 5](05-Sorting-by-Comparison.md), 5.4): **choose randomly,
at run time, from a family of functions**, so that no fixed set of keys is bad for most choices. The adversary may know
the family but not which member we picked.

**Definition (Carter and Wegman, 1979).** A family $\mathcal H$ of functions $U\to\{0,\dots,m-1\}$ is **universal** if
for every pair of distinct keys $x\ne y$,

$$P_{h\in\mathcal H}\big[h(x)=h(y)\big]\le\frac1m,$$

where $h$ is chosen uniformly from $\mathcal H$. That is, any two keys collide no more often than they would under a truly
random function.

That is all we need for chaining. Fix a key $k$ and the set $S$ of $n$ stored keys. The number of keys of $S$ (other
than $k$) in $k$'s chain is $\sum_{y\in S,y\ne k}X_y$, where $X_y=1$ if $h(y)=h(k)$. By linearity of expectation and
universality its expectation is at most $n/m=\alpha$. So:

**Theorem.** With $h$ drawn from a universal family, for *every* set of stored keys and every key $k$, the expected
length of the chain $k$ is in (or would be in) is at most $1+\alpha$. Every operation costs $O(1+\alpha)$ in
expectation, for every input.

Note what changed: no assumption about the keys. The probability is over our random choice of $h$ only.

### A universal family

Choose a prime $p$ larger than every key, so keys are in $\{0,\dots,p-1\}$. For $a\in\{1,\dots,p-1\}$ and
$b\in\{0,\dots,p-1\}$ define

$$h_{a,b}(x)=\big((ax+b)\bmod p\big)\bmod m.$$

**Theorem (Carter and Wegman).** The family $\mathcal H_{p,m}=\{h_{a,b}\}$, of $p(p-1)$ functions, is universal.

*Proof.* Fix distinct keys $x\ne y$. Let $r=(ax+b)\bmod p$ and $s=(ay+b)\bmod p$.

*Step 1: $r\ne s$.* $r-s\equiv a(x-y)\pmod p$. Since $p$ is prime and neither $a$ nor $x-y$ is divisible by $p$, their
product is not either, so $r\ne s$. Thus *before* the final "mod $m$", distinct keys never collide.

*Step 2: $(a,b)\mapsto(r,s)$ is a bijection* from the $p(p-1)$ pairs with $a\ne0$ onto the $p(p-1)$ pairs with $r\ne s$.
Given $(r,s)$ with $r\ne s$ we can solve for $(a,b)$ uniquely: $a=(r-s)(x-y)^{-1}\bmod p$ (the inverse exists because $p$
is prime) and $b=(r-ax)\bmod p$; and $a\ne0$ because $r\ne s$. So choosing $(a,b)$ uniformly makes $(r,s)$ uniform over
all pairs of distinct values.

*Step 3: count collisions after mod $m$.* $x$ and $y$ collide exactly when $r\equiv s\pmod m$. For a fixed $r$, the values
$s\ne r$ in $\{0,\dots,p-1\}$ with $s\equiv r\pmod m$ number at most $\lceil p/m\rceil-1\le\frac{p+m-1}m-1=\frac{p-1}m$.
So, for each $r$, at most $\frac{p-1}m$ of the $p-1$ equally likely values of $s$ cause a collision, and

$$P[h_{a,b}(x)=h_{a,b}(y)]\le\frac{(p-1)/m}{p-1}=\frac1m.\qquad\square$$

The program checks this exhaustively for $p=37$, $m=6$: over all $36\cdot37=1332$ choices of $(a,b)$, the worst pair of
keys collides for 192 of them, a fraction $0.1441\le\tfrac16=0.1667$. And with a randomly chosen $h_{a,b}$ the 2000
multiples of 1024 that broke $x\bmod1024$ spread out with a longest chain of 4.

**History and variants.** J. Lawrence Carter and Mark Wegman introduced universal hashing in "Universal Classes of Hash
Functions" (*Journal of Computer and System Sciences*, 1979). A stronger property, **$k$-wise independence** (any $k$
distinct keys hash to independent uniform values), is what some analyses need (the linear probing result above uses
$k=5$); a random polynomial of degree $k-1$ modulo a prime gives it. In practice, languages defend their tables with a
fast keyed hash: Python has hashed `str` and `bytes` with **SipHash** (Aumasson and Bernstein, 2012), with a random key
chosen at start-up, since Python 3.4 (PEP 456). You can see the randomness: `hash("mars")` differs between runs unless
the environment variable `PYTHONHASHSEED` fixes it.

## 7.6 Perfect hashing, cuckoo hashing and Robin Hood hashing

*Level: advanced.*

Universal hashing gives *expected* $O(1)$. Can we guarantee $O(1)$ in the worst case for lookups? For a fixed set of keys
known in advance (a **static** dictionary: the reserved words of a language, the names of all Mars craters in a
gazetteer), yes.

### Perfect hashing (FKS)

A hash function is **perfect** for a set $S$ if it has no collisions on $S$. Fredman, Komlós and Szemerédi ("Storing a
Sparse Table with $O(1)$ Worst Case Access Time", *Journal of the ACM*, 1984) showed how to build one in expected $O(n)$
time and $O(n)$ space, with two levels of universal hashing.

**Lemma.** If $n$ keys are hashed into $m=n^2$ slots by a function from a universal family, the probability of any
collision is less than $\tfrac12$.

*Proof.* There are $\binom n2$ pairs, each colliding with probability at most $\frac1{n^2}$. The expected number of
colliding pairs is at most $\binom n2\frac1{n^2}<\frac12$, and by Markov's inequality (a nonnegative integer variable
with expectation below $\tfrac12$ is 0 with probability above $\tfrac12$) there is no collision with probability more
than $\tfrac12$. $\square$

So $n^2$ space makes perfection easy: try random functions until one is collision-free, two tries on average. But $n^2$
is too much. The FKS trick is to use it only on small groups:

1. **Level 1:** hash the $n$ keys into $m=n$ buckets with a universal $h$. Let $n_i$ be the size of bucket $i$. Retry
   until $\sum_in_i^2<4n$.
2. **Level 2:** for each bucket $i$, choose a universal $g_i$ into $n_i^2$ slots, retrying until it has no collisions on
   that bucket (the lemma: fewer than 2 tries on average).

A lookup computes $i=h(x)$, then $g_i(x)$, and compares one key: **two hash evaluations and one comparison, always.**
The space is $n+\sum_in_i^2<5n$ slots.

**Theorem.** With $h$ universal into $n$ buckets, $E\big[\sum_in_i^2\big]<2n$. So the retry condition in step 1 holds
with probability more than $\tfrac12$ (by Markov's inequality), and the expected construction time is $O(n)$.

*Proof.* $n_i^2$ counts ordered pairs $(x,y)$ of keys in bucket $i$, including $x=y$. Summing over buckets,
$\sum_in_i^2=n+2C$, where $C$ is the number of unordered colliding pairs. By universality $E[C]\le\binom n2\frac1n=\frac{n-1}2$,
so $E\big[\sum_in_i^2\big]\le n+(n-1)<2n$. $\square$

This is the same $2n-1$ as bucket sort's in [Chapter 6](06-Sorting-in-Linear-Time-and-Selection.md), 6.3, and for the
same reason. The program builds an FKS table for 10 000 random keys: one try at level 1, 10 995 tries in total for the
10 000 level-2 tables (most buckets have 0 or 1 keys and succeed at once), and $29\,994\approx3.00\,n$ slots in all;
every key is found and 10 000 non-keys are rejected.

Dietzfelbinger, Karlin, Mehlhorn, Meyer auf der Heide, Rohnert and Tarjan extended this to a *dynamic* dictionary with
worst-case $O(1)$ lookups and amortized expected $O(1)$ updates ("Dynamic Perfect Hashing", 1994).

### Cuckoo hashing

**Cuckoo hashing** (Pagh and Rodler, ESA 2001; journal version 2004) gets worst-case $O(1)$ lookups for a dynamic table
with a simpler rule: every key lives in one of exactly **two** possible places, $T_1[h_1(x)]$ or $T_2[h_2(x)]$. A lookup
checks both, never more.

To insert $x$: put it in $T_1[h_1(x)]$. If that slot was occupied by $y$, kick $y$ out and move it to its *other* place,
$T_2[h_2(y)]$; if that was occupied by $z$, kick $z$ out to its other place; and so on, like the cuckoo chick that pushes
the other eggs out of the nest. If this goes on too long (more than $O(\log n)$ kicks, which signals a cycle), pick new
hash functions and rebuild.

Picture a graph whose vertices are the $2m$ slots, with one edge per key joining its two possible slots. A set of keys
can be placed exactly when every connected component has at most as many edges as vertices (at most one cycle). Pagh and
Rodler proved that if each table has $m\ge(1+\varepsilon)n$ slots (total load below $\tfrac12$) and the hash functions
are sufficiently random, insertion takes expected amortized $O(1)$ time, counting the occasional rebuild. The proof
analyses random graphs and is too long for here; see their paper. The program inserts 14 745 keys
into two tables of 16 384 (load 0.45): 0.586 kicks per insertion on average and no rebuilds. Variants with more than two
choices or buckets of several slots work at loads above 90%.

### Robin Hood hashing

Linear probing's cost is the *variance*: some keys sit far from their home slot. **Robin Hood hashing** (Celis, Larson
and Munro, FOCS 1985) changes only the insertion rule. As a new key probes, compare its distance from its home slot with
the distance of the key occupying the slot. If the occupant is *closer* to home ("richer"), the newcomer takes the slot
and the occupant continues probing instead: take from the rich, give to the poor. The average probe count is unchanged,
but the spread is much smaller, and an unsuccessful lookup can stop early as soon as it meets a key closer to home than
it is. Rust's standard `HashMap` used Robin Hood hashing until 2019, when it switched to a port of Google's SwissTable
design (open addressing with groups of slots checked in parallel using small per-slot fingerprints).

## 7.7 Bloom filters

A web crawler has visited a billion pages. Before fetching a URL it wants to know "have I seen this one?" A hash set of a
billion URLs would need tens of gigabytes. A **Bloom filter** (Burton Bloom, "Space/Time Trade-offs in Hash Coding with
Allowable Errors", *Communications of the ACM*, 1970) answers the question in about 10 bits per URL, at the price of
sometimes saying "yes, seen it" when the answer is no. It never says no wrongly.

**The structure.** An array of $m$ bits, all 0, and $k$ hash functions $h_1,\dots,h_k$ into $\{0,\dots,m-1\}$.

- **Add** $x$: set bits $h_1(x),\dots,h_k(x)$ to 1.
- **Query** $x$: answer "maybe present" if all $k$ of those bits are 1, and "definitely absent" if any is 0.

If $x$ was added, its bits are all 1, so a query never gives a **false negative**. But the $k$ bits of a new item $y$
might all have been set by *other* items: a **false positive**.

<figure class="mars-fig" markdown="0">
<svg viewBox="0 0 640 210" role="img" aria-label="A Bloom filter of 16 bits with k equal to 3 hash functions. Item A sets bits 1, 6 and 11. Item B sets bits 4, 9 and 14. A query for item C checks bits 6, 9 and 12; bit 12 is 0, so C is definitely absent. A query for item D checks bits 1, 9 and 14, all set by A and B, so D is a false positive.">
  <g font-size="13" fill="currentColor" text-anchor="middle">
    <text x="150" y="25">add A</text><text x="420" y="25">add B</text>
    <text x="210" y="190">query C: bit 12 is 0, absent</text>
    <text x="470" y="190">query D: all 1, false positive</text>
  </g>
  <g stroke="currentColor" stroke-width="1" font-size="12" fill="currentColor" text-anchor="middle">
    <rect x="40" y="80" width="35" height="32" fill="none"/><text x="57" y="101" stroke="none">0</text>
    <rect x="75" y="80" width="35" height="32" fill="#9cc9ea" fill-opacity="0.6"/><text x="92" y="101" stroke="none">1</text>
    <rect x="110" y="80" width="35" height="32" fill="none"/><text x="127" y="101" stroke="none">0</text>
    <rect x="145" y="80" width="35" height="32" fill="none"/><text x="162" y="101" stroke="none">0</text>
    <rect x="180" y="80" width="35" height="32" fill="#eea66f" fill-opacity="0.6"/><text x="197" y="101" stroke="none">1</text>
    <rect x="215" y="80" width="35" height="32" fill="none"/><text x="232" y="101" stroke="none">0</text>
    <rect x="250" y="80" width="35" height="32" fill="#9cc9ea" fill-opacity="0.6"/><text x="267" y="101" stroke="none">1</text>
    <rect x="285" y="80" width="35" height="32" fill="none"/><text x="302" y="101" stroke="none">0</text>
    <rect x="320" y="80" width="35" height="32" fill="none"/><text x="337" y="101" stroke="none">0</text>
    <rect x="355" y="80" width="35" height="32" fill="#eea66f" fill-opacity="0.6"/><text x="372" y="101" stroke="none">1</text>
    <rect x="390" y="80" width="35" height="32" fill="none"/><text x="407" y="101" stroke="none">0</text>
    <rect x="425" y="80" width="35" height="32" fill="#9cc9ea" fill-opacity="0.6"/><text x="442" y="101" stroke="none">1</text>
    <rect x="460" y="80" width="35" height="32" fill="none"/><text x="477" y="101" stroke="none">0</text>
    <rect x="495" y="80" width="35" height="32" fill="none"/><text x="512" y="101" stroke="none">0</text>
    <rect x="530" y="80" width="35" height="32" fill="#eea66f" fill-opacity="0.6"/><text x="547" y="101" stroke="none">1</text>
    <rect x="565" y="80" width="35" height="32" fill="none"/><text x="582" y="101" stroke="none">0</text>
  </g>
  <g font-size="10" fill="currentColor" text-anchor="middle">
    <text x="57" y="126">0</text><text x="92" y="126">1</text><text x="127" y="126">2</text><text x="162" y="126">3</text>
    <text x="197" y="126">4</text><text x="232" y="126">5</text><text x="267" y="126">6</text><text x="302" y="126">7</text>
    <text x="337" y="126">8</text><text x="372" y="126">9</text><text x="407" y="126">10</text><text x="442" y="126">11</text>
    <text x="477" y="126">12</text><text x="512" y="126">13</text><text x="547" y="126">14</text><text x="582" y="126">15</text>
  </g>
  <g fill="none" stroke-width="1.4">
    <line x1="150" y1="32" x2="92" y2="78" stroke="#9cc9ea"/><line x1="150" y1="32" x2="267" y2="78" stroke="#9cc9ea"/>
    <line x1="150" y1="32" x2="442" y2="78" stroke="#9cc9ea"/>
    <line x1="420" y1="32" x2="197" y2="78" stroke="#eea66f"/><line x1="420" y1="32" x2="372" y2="78" stroke="#eea66f"/>
    <line x1="420" y1="32" x2="547" y2="78" stroke="#eea66f"/>
    <line x1="210" y1="175" x2="267" y2="132" stroke="currentColor" stroke-dasharray="3 3"/>
    <line x1="210" y1="175" x2="372" y2="132" stroke="currentColor" stroke-dasharray="3 3"/>
    <line x1="210" y1="175" x2="477" y2="132" stroke="currentColor" stroke-dasharray="3 3"/>
    <line x1="470" y1="175" x2="92" y2="132" stroke="#7ccf9a"/>
    <line x1="470" y1="175" x2="372" y2="132" stroke="#7ccf9a"/>
    <line x1="470" y1="175" x2="547" y2="132" stroke="#7ccf9a"/>
  </g>
</svg>
<figcaption>Figure 7.3. A Bloom filter with m = 16 bits and k = 3. A query is "absent" as soon as one of its bits is 0 (C, bit 12). D was never added, but its three bits were set by A and B: a false positive.</figcaption>
</figure>

### The false-positive rate

Assume the hash functions behave like independent uniform random functions. After inserting $n$ items, a particular bit
has been missed by all $kn$ bit-settings with probability

$$\Big(1-\frac1m\Big)^{kn}\approx e^{-kn/m}.$$

So the fraction of bits that are 1 is about $1-e^{-kn/m}$. A query for an item not in the set checks $k$ bits; treating
them as independent (an approximation, discussed below), all are 1 with probability

$$\varepsilon\approx\big(1-e^{-kn/m}\big)^k.$$

**The best $k$.** More hash functions check more bits (good) but fill the array faster (bad). Write $p=e^{-kn/m}$, so
$k=-\frac mn\ln p$ and $\ln\varepsilon=k\ln(1-p)=-\frac mn\ln p\,\ln(1-p)$. The product $\ln p\ln(1-p)$ is symmetric in
$p\leftrightarrow1-p$ and is largest at $p=\tfrac12$, so the optimum is $p=\tfrac12$: **half the bits set**, at

$$k=\frac mn\ln2\approx0.693\,\frac mn,\qquad\varepsilon=2^{-k}=\Big(\frac12\Big)^{(m/n)\ln2}\approx0.6185^{m/n}.$$

Turned around: for a target rate $\varepsilon$, the filter needs $m/n=\log_2(1/\varepsilon)/\ln2\approx1.44\log_2(1/\varepsilon)$
bits per item, *independent of how big the items are*. For $\varepsilon=1\%$: 9.6 bits per item and $k=7$; a billion URLs
fit in about 1.2 GB.

The program builds filters for 10 000 keys (using two 64-bit halves of SHA-256 and the double-hashing trick
$h_i=h_1+i\,h_2$, which Kirsch and Mitzenmacher proved loses nothing asymptotically, "Less Hashing, Same Performance",
2006) and measures on 100 000 non-keys:

```
  bits/key   k   measured  (1-e^(-kn/m))^k
         8   3    0.02972          0.03058
         8   6    0.02094          0.02158
        10   7    0.00798          0.00819
        16  11    0.00047          0.00046
```

With 8 bits per key, $k=6$ (close to $8\ln2=5.5$) beats $k=3$, and 10 bits per key with $k=7$ give 0.8%.

**Honest small print.** The bits checked by one query are not exactly independent, so the formula is an approximation;
Bose, Guo, Kranakis, Maheshwari, Morin, Morrison, Smid and Tang ("On the False-Positive Rate of Bloom Filters", 2008)
showed that it slightly underestimates the true rate, though the error vanishes as $m$ grows. And there is a limit to how
small such a structure can be: any data structure that answers membership with false-positive rate $\varepsilon$ and no
false negatives needs at least $\log_2(1/\varepsilon)$ bits per item (Carter, Floyd, Gill, Markowsky and Wegman, 1978), so
Bloom filters use about 44% more space than the minimum.

**Uses and relatives.** Databases built on log-structured merge trees keep a Bloom filter per file on disk and skip
files whose filter says "absent", saving a disk read for most missing keys. Web caches and network routers use them to
summarize sets cheaply. A plain Bloom filter cannot delete (clearing a bit might erase another item); a **counting Bloom
filter** (Fan, Cao, Almeida and Broder, 2000) stores small counters instead of bits. **Cuckoo filters** (Fan, Andersen,
Kaminsky and Mitzenmacher, 2014) store short fingerprints in a cuckoo hash table, support deletion and are often smaller
at low error rates. Sketches that *count* rather than test membership, such as count-min and HyperLogLog, are in
[Chapter 24](24-Algorithms-for-Big-Data-and-Many-Processors.md).

## 7.8 How Python's dict really works

Python's `dict` is perhaps the most heavily used data structure in the language: every module's global variables,
every object's attributes and every keyword argument live in one. Its design (in `Objects/dictobject.c` in the CPython
source, with comments that are worth reading) uses most of this chapter.

**1. Hashing.** `hash(x)` calls the object's `__hash__`. For integers it is the value reduced modulo the prime
$2^{61}-1$ on 64-bit builds (so `hash(2**61) == 1`, which the program prints), with one oddity: $-1$ is reserved as an
error code at the C level, so `hash(-1) == -2` (and so is `hash(-2)`). Equal numbers must hash equally, so
`hash(1) == hash(1.0) == hash(True)`, and `{1: "a", 1.0: "b"}` is a dictionary with one key (Exercise 12). For `str` and
`bytes`, the hash is SipHash with a random per-process key (7.5). The hash of a string is cached in the string object, so
it is computed once.

**2. Open addressing with perturbation.** The table size is a power of 2, $2^p$ (at least 8). The first probe is the
low $p$ bits of the hash, `i = h & mask`. Low bits alone would be weak (keys that differ only in high bits would follow
identical probe sequences), so CPython mixes the high bits in gradually:

```python
perturb = h
i = h & mask
while slot i is occupied by a different key:
    perturb >>= 5
    i = (5 * i + 1 + perturb) & mask
```

While `perturb` is nonzero, its higher bits steer the sequence; once they are shifted away, `perturb` is 0 and the
recurrence $i\leftarrow(5i+1)\bmod2^p$ is a full-period linear congruential generator, which visits every slot. So every
probe sequence eventually reaches every slot. The program prints the sequences in a table of 8 slots: keys 3 and 11 have
the same low bits and no bits above bit 4, so they follow the identical sequence 3, 0, 1, 6, 7, 4, 5, 2; key 43
($=101011_2$) starts at the same slot but goes to 1 next; key 99 tries slot 3 twice before moving on. Deleted entries
become tombstones (called "dummy" entries in the source).

**3. Load factor 2/3.** The table is resized when it would become more than two-thirds full, to keep probe sequences
short (7.4: at $\alpha=\tfrac23$, uniform hashing predicts about 3 probes for a miss). The new size is chosen from the
number of live entries, so a table that had many deletions shrinks or is cleaned of tombstones on resize.

**4. The compact layout (Python 3.6) and insertion order (3.7).** Until Python 3.5 the hash table was an array of
(hash, key, value) entries, mostly empty (at most two-thirds full). Raymond Hettinger proposed in 2012 to split it in
two:

- an **entries** array holding (hash, key, value) in *insertion order*, densely packed;
- a sparse **indices** array of small integers (one byte each for small tables), the actual hash table, whose slots hold
  positions in the entries array or "empty".

<figure class="mars-fig" markdown="0">
<svg viewBox="0 0 640 250" role="img" aria-label="CPython's compact dict holding keys 3, 43 and 8 inserted in that order. The indices array has 8 one-byte slots: slot 0 holds 2, slot 1 holds 1, slot 3 holds 0, the rest are empty. The entries array holds, in insertion order, entry 0 with hash 3, key 3, value a; entry 1 with hash 43, key 43, value b; entry 2 with hash 8, key 8, value c. Arrows go from index slots to entries.">
  <g font-size="13" fill="currentColor" text-anchor="middle">
    <text x="190" y="22">indices (the hash table, 1 byte per slot)</text>
    <text x="490" y="22">entries (insertion order)</text>
  </g>
  <g stroke="currentColor" font-size="13" fill="currentColor" text-anchor="middle">
    <rect x="40" y="40" width="300" height="30" fill="none"/>
    <line x1="77.5" y1="40" x2="77.5" y2="70"/><line x1="115" y1="40" x2="115" y2="70"/><line x1="152.5" y1="40" x2="152.5" y2="70"/>
    <line x1="190" y1="40" x2="190" y2="70"/><line x1="227.5" y1="40" x2="227.5" y2="70"/><line x1="265" y1="40" x2="265" y2="70"/>
    <line x1="302.5" y1="40" x2="302.5" y2="70"/>
    <rect x="40" y="40" width="37.5" height="30" fill="#7ccf9a" fill-opacity="0.5"/><text x="59" y="60" stroke="none">2</text>
    <rect x="77.5" y="40" width="37.5" height="30" fill="#eea66f" fill-opacity="0.5"/><text x="96" y="60" stroke="none">1</text>
    <text x="134" y="60" stroke="none">–</text>
    <rect x="152.5" y="40" width="37.5" height="30" fill="#9cc9ea" fill-opacity="0.5"/><text x="171" y="60" stroke="none">0</text>
    <text x="209" y="60" stroke="none">–</text><text x="246" y="60" stroke="none">–</text><text x="284" y="60" stroke="none">–</text>
    <text x="321" y="60" stroke="none">–</text>
  </g>
  <g font-size="10" fill="currentColor" text-anchor="middle">
    <text x="59" y="84">0</text><text x="96" y="84">1</text><text x="134" y="84">2</text><text x="171" y="84">3</text>
    <text x="209" y="84">4</text><text x="246" y="84">5</text><text x="284" y="84">6</text><text x="321" y="84">7</text>
  </g>
  <g stroke="currentColor" font-size="13" fill="currentColor" text-anchor="middle">
    <rect x="400" y="120" width="210" height="30" fill="#9cc9ea" fill-opacity="0.5"/><text x="505" y="140" stroke="none">0: hash 3, key 3, "a"</text>
    <rect x="400" y="155" width="210" height="30" fill="#eea66f" fill-opacity="0.5"/><text x="505" y="175" stroke="none">1: hash 43, key 43, "b"</text>
    <rect x="400" y="190" width="210" height="30" fill="#7ccf9a" fill-opacity="0.5"/><text x="505" y="210" stroke="none">2: hash 8, key 8, "c"</text>
  </g>
  <g fill="none" stroke="currentColor" stroke-width="1.2">
    <path d="M 171 70 C 180 120, 300 135, 398 135"/>
    <path d="M 96 70 C 110 150, 300 170, 398 170"/>
    <path d="M 59 70 C 60 190, 300 205, 398 205"/>
  </g>
  <text x="200" y="240" font-size="12" fill="currentColor" text-anchor="middle">43 wanted slot 3 (taken by 3), probed 1; 8 took slot 0</text>
</svg>
<figcaption>Figure 7.4. The compact dict {3: "a", 43: "b", 8: "c"}. Probing happens in the small indices array; the entries stay packed in insertion order, so iterating over the dict walks the entries array directly.</figcaption>
</figure>

The benefits: less memory (the sparse part is one byte per slot instead of three 8-byte words), faster iteration (no
empty slots to skip), and, as a side effect, **iteration in insertion order**. PyPy shipped this design first; CPython
adopted it in 3.6, where the ordering was called an implementation detail, and Python 3.7 made insertion order part of
the language definition. The program's dictionary of crater and volcano names comes back in exactly the order inserted.

**5. What this means for you.** Keys must be **hashable**: their hash must never change while they are in a dict, which
is why lists (mutable) cannot be keys and tuples of immutable values can. If you define `__eq__` on a class you must
define a matching `__hash__` (equal objects, equal hashes), or Python makes instances unhashable. And all the guarantees
are expected-time guarantees: lookups are $O(1)$ on average, with SipHash and random seeds making it very hard to force
the bad case on purpose.

The full program for 7.6 to 7.8:

```python
--8<-- "books/algorithms/ch07_advanced_hashing.py"
```

Output:

```
FKS for n = 10000: level-1 tries 1, level-2 tries 10995 for 10000 buckets, total slots 29994 (3.00 n)
cuckoo, two tables of 16384, load 0.25: 8192 keys, 0.237 kicks per insert, 0 rehashes
cuckoo, two tables of 16384, load 0.45: 14745 keys, 0.586 kicks per insert, 0 rehashes

Bloom filter, n = 10000 keys, false-positive rate measured on 100000 non-keys
  bits/key   k   measured  (1-e^(-kn/m))^k
         8   3    0.02972          0.03058
         8   6    0.02094          0.02158
        10   7    0.00798          0.00819
        16  11    0.00047          0.00046

CPython dict probes in a table of 8 slots:
  hash 3: slots [3, 0, 1, 6, 7, 4, 5, 2]
  hash 11: slots [3, 0, 1, 6, 7, 4, 5, 2]
  hash 43: slots [3, 1, 6, 7, 4, 5, 2, 3]
  hash 99: slots [3, 3, 0, 1, 6, 7, 4, 5]
  hash 1000003: slots [3, 2, 3, 6, 7, 4, 5, 2]
  hash(2**61) = 1   hash(-1) = -2   hash(-2) = -2
  insertion order kept: ['olympus', 'gale', 'jezero', 'arsia', 'hellas']
```

And the program for 7.3 to 7.5, the hash tables built from scratch:

```python
--8<-- "books/algorithms/ch07_hash_tables.py"
```

Output:

```
chained table: 4911 keys, 8192 buckets, load 0.60, longest chain 2, empty buckets 4092

open addressing, m = 65536: average slots examined (measured / formula)
  alpha         linear hit        linear miss         double hit        double miss
   0.50      1.50 /   1.50      2.58 /   2.50      1.38 /   1.39      2.00 /   2.00
   0.75      2.50 /   2.50      8.86 /   8.50      1.82 /   1.85      3.97 /   4.00
   0.90      5.12 /   5.50     40.97 /  50.50      2.53 /   2.56      9.85 /  10.00

delete with tombstone: later key 52 still found? True
delete with plain EMPTY: later key 52 still found? False

2000 keys that are multiples of 1024: longest chain with h(x) = x mod m: 2000, with a random universal h: 4

p = 37, m = 6: worst pair collides for 192 of 1332 choices of (a, b) = 0.1441 <= 1/m = 0.1667

first collision in 1000000 slots: after 1233 keys on average (sqrt(pi m / 2) = 1253)
```

(The longest chain in the first line is only 2 although a random function would give about 5 or 6 for 4911 keys in
8192 buckets: the keys there are the consecutive integers $0..4999$, and $((ax+b)\bmod p)\bmod m$ spreads an arithmetic
progression more evenly than random. Universality only promises "no worse than random" for pairs.)

**In practice.** Use the built-in `dict` and `set`; `collections.Counter` and `defaultdict` for counting and grouping.
Write your own hash table only to learn, or for a special structure: a static perfect-hash table generated at build time
(the GNU `gperf` tool does this for keyword tables), a Bloom filter in front of slow storage, or a lock-free table in a
concurrent program.

## Check yourself

??? question "1. Trace lower_bound on [3, 8, 15, 21, 30, 42, 57] for x = 10. What does it return, and what does that tell you?"

    $lo=0,hi=7$: $mid=3$, $a[3]=21\ge10$, so $hi=3$. $mid=1$, $a[1]=8<10$, so $lo=2$. $mid=2$, $a[2]=15\ge10$, so $hi=2$.
    Stop with $lo=hi=2$. So 10 is absent ($a[2]=15\ne10$), it would be inserted at index 2, and exactly 2 items are
    smaller than 10. Three probes; $\lceil\log_2 8\rceil=3$.

??? question "2. This version is meant to find x in a sorted list. Find the bug: lo, hi = 0, len(a); while lo <= hi: mid = (lo + hi) // 2; if a[mid] == x: return mid; elif a[mid] < x: lo = mid + 1; else: hi = mid - 1."

    It mixes conventions: `hi = len(a)` is a half-open end, but `while lo <= hi` and `hi = mid - 1` belong to the closed
    convention. When $x$ is larger than every item, $lo$ climbs to $len(a)$ while $hi=len(a)$, the loop runs once more
    and reads `a[len(a)]`: an index error. Fix: start with `hi = len(a) - 1`.

??? question "3. Write a function that counts how many times x occurs in a sorted list, in O(log n) time."

    ```python
    def upper_bound(a, x):              # first index with a[i] > x
        lo, hi = 0, len(a)
        while lo < hi:
            mid = (lo + hi) // 2
            if a[mid] <= x:
                lo = mid + 1
            else:
                hi = mid
        return lo

    def count(a, x):
        return upper_bound(a, x) - lower_bound(a, x)[0]   # lower_bound from ch07_binary_search.py

    assert count([1, 2, 2, 2, 5, 7], 2) == 3 and count([1, 2, 2, 2, 5, 7], 3) == 0
    ```

    The only change from `lower_bound` is `<=` in place of `<`, and the invariant becomes $a[:lo]\le x<a[hi:]$. The two
    searches cost $2\lceil\log_2(n+1)\rceil$ probes. In Python: `bisect_right(a, x) - bisect_left(a, x)`.

??? question "4. Insert 15, 22, 8, 36, 3, 50 into a chained table with m = 7 and h(k) = k mod 7. Which chains form, and what is wrong with this choice?"

    $15\bmod7=1$, $22\bmod7=1$, $8\bmod7=1$, $36\bmod7=1$, $3\bmod7=3$, $50\bmod7=1$. Slot 1 holds a chain of five keys
    and slot 3 holds one key. Nothing is wrong with $m=7$ in general; these keys happen to be $\equiv1\pmod7$, exactly the
    kind of pattern a fixed hash function cannot defend against. A random universal function would spread them (with
    expected chain length at most $1+\alpha$ for every key).

??? question "5. In the linear probing table of 7.4 (slots 0: 90, 3: 23, 4: 13, 5: 33, 7: 47, 8: 58, 9: 7), compute the average cost of a successful lookup and of an unsuccessful lookup whose home slot is uniform."

    Successful: 1 probe each for 23, 47, 90, 58; 2 for 13; 3 for 33 and for 7. Total 12, average $12/7\approx1.71$.
    Unsuccessful, by home slot 0 to 9: 0 → 0, 1: 2 probes; 1: 1; 2: 1; 3 → 3, 4, 5, 6: 4; 4: 3; 5: 2; 6: 1; 7 → 7, 8, 9,
    0, 1: 5; 8: 4; 9: 3. Total 26, average 2.6. Compare Knuth's formulas at $\alpha=0.7$: 2.17 and 6.06; this table is
    small and lucky.

??? question "6. Show that for m = 2^p the quadratic probe sequence h + i(i+1)/2 (mod m), i = 0, 1, ..., m − 1, visits every slot."

    It suffices to show the offsets $t_i=i(i+1)/2$ are distinct mod $m$ for $0\le i<j<m$. Suppose
    $t_j-t_i=\frac{(j-i)(j+i+1)}2\equiv0\pmod{2^p}$, so $(j-i)(j+i+1)\equiv0\pmod{2^{p+1}}$. The two factors $j-i$ and
    $j+i+1$ have different parity (their sum $2j+1$ is odd), so one of them is odd and the other must be divisible by
    $2^{p+1}$. But $1\le j-i<2^p$ and $2\le j+i+1<2^{p+1}$, so neither can be. Contradiction; so the $m$ offsets are
    distinct and cover all $m$ slots.

??? question "7. Under uniform hashing at load α = 0.8, how many probes do an insertion and a successful lookup take, at most, in expectation? What about linear probing?"

    Uniform hashing: insertion (an unsuccessful search) at most $1/(1-0.8)=5$; successful at most
    $\frac1{0.8}\ln5\approx2.01$. Linear probing (Knuth): miss $\tfrac12(1+25)=13$, hit $\tfrac12(1+5)=3$. The difference
    at high load is why linear probing tables are kept below about 70% full.

??? question "8. A program stores objects in a hash table keyed by their memory address, with m = 1024 and h(k) = k mod m. Addresses are multiples of 16. What load does each used slot carry?"

    $k\bmod1024$ for $k$ a multiple of 16 is itself a multiple of 16, so only $1024/16=64$ of the 1024 slots can ever be
    used. The real load factor on those slots is 16 times the nominal one. Fixes: drop the low 4 bits first (`k >> 4`),
    use a prime $m$, or better a multiplicative or universal hash that mixes all bits.

??? question "9. Design a Bloom filter for 1 million items with a false-positive rate of 1%. How many bits, how many hash functions, and what rate do you get if you have 2 million items instead?"

    $m/n=1.44\log_2(100)\approx9.59$, so $m\approx9.59\times10^6$ bits, about 1.2 MB, and $k=(m/n)\ln2\approx6.6$, so 7.
    With $n=2\times10^6$ and the same $m$ and $k$: $kn/m\approx7\cdot2/9.59=1.46$, so
    $\varepsilon\approx(1-e^{-1.46})^7\approx(0.768)^7\approx0.157$: 16%. Bloom filters must be sized for the final
    number of items; overfilling them ruins them quickly.

??? question "10. How many pairs of keys are expected to collide when 1000 keys are hashed uniformly into 1000 slots? And into a million slots?"

    Each of the $\binom{1000}2=499\,500$ pairs collides with probability $1/m$. For $m=1000$: $499.5$ colliding pairs
    expected. For $m=10^6$: $0.4995$. So even with a thousand times more slots than keys, the probability of at least
    one collision is about $1-e^{-0.4995}\approx39\%$ (the birthday bound of 7.3).

??? question "11. Write an O(n) expected-time function that decides whether two numbers in a list add up to a target."

    ```python
    def has_pair_with_sum(xs, target):
        seen = set()
        for x in xs:
            if target - x in seen:      # one expected O(1) hash lookup
                return True
            seen.add(x)
        return False

    assert has_pair_with_sum([8, 3, 11, 5, 2], 13)       # 8 + 5 (also 11 + 2)
    assert not has_pair_with_sum([8, 3, 11, 5, 2], 4)
    ```

    Invariant: before processing $x$, `seen` holds all earlier items, so the test asks exactly "is there an earlier
    partner for $x$?". Every pair is examined when its second item arrives. $n$ insertions and $n$ lookups, each
    expected $O(1)$. Without hashing, sorting plus two pointers ([Two pointers](../../searching/two-pointers.md))
    takes $O(n\log n)$.

??? question "12. What does Python print for d = {1: 'a', True: 'b', 1.0: 'c'}; print(d), and why?"

    `{1: 'c'}`. The three keys are equal (`1 == True == 1.0`) and so have equal hashes, which Python requires. The dict
    sees one key: the first insertion stores the key object `1`; the later ones find an equal key and only replace the
    value. The key keeps its first spelling, `1`, and the value is the last one, `'c'`.

## What you learned

- Binary search finds a position in a sorted list with $\lceil\log_2(n+1)\rceil$ probes, which is optimal; writing it
  from the invariant $a[:lo]<x\le a[hi:]$ avoids the classic off-by-one and infinite-loop bugs.
- Binary search works on any monotone yes/no question (binary search on the answer), and exponential search finds items
  near the start in $O(\log i)$.
- Hashing gives dictionaries direct addressing's speed with $\Theta(n)$ memory: chaining costs $\Theta(1+\alpha)$
  expected per operation under simple uniform hashing, and doubling keeps $\alpha$ bounded with $O(1)$ amortized
  inserts.
- Open addressing stores keys in the array; uniform hashing costs at most $\frac1{1-\alpha}$ probes per miss, linear
  probing about $\frac12\big(1+\frac1{(1-\alpha)^2}\big)$ but with excellent cache behaviour; deletion needs tombstones.
- A fixed hash function can be attacked; a universal family such as $((ax+b)\bmod p)\bmod m$ guarantees collision
  probability at most $1/m$ for every pair of keys, and so expected $O(1+\alpha)$ for every input.
- FKS perfect hashing and cuckoo hashing give worst-case $O(1)$ lookups; Robin Hood hashing reduces the variance of
  probe lengths.
- A Bloom filter answers membership with no false negatives and false-positive rate about $0.6185^{m/n}$ at the best
  $k=(m/n)\ln2$; Python's `dict` is a compact, insertion-ordered open-addressing table with perturbed probing and load
  at most $2/3$.

**Next:** [Chapter 8](08-Trees-and-Balanced-Search-Trees.md) builds dictionaries that also keep their keys in order,
with balanced search trees that guarantee $O(\log n)$ for every operation.

## Further reading

- T. H. Cormen, C. E. Leiserson, R. L. Rivest and C. Stein, *Introduction to Algorithms*, 4th ed., 2022: chapter 11
  (hash tables).
- D. E. Knuth, *The Art of Computer Programming*, Vol. 3: *Sorting and Searching*, 2nd ed., 1998: 6.2.1 (binary search
  and its history) and 6.4 (hashing, including the analysis of linear probing).
- R. Sedgewick and K. Wayne, *Algorithms*, 4th ed., 2011: 3.1 (symbol tables, binary search) and 3.4 (hash tables).
- J. Kleinberg and É. Tardos, *Algorithm Design*, 2005: 13.6 (hashing and universal hashing).
- J. Bentley, *Programming Pearls*, 2nd ed., 2000: column 4, "Writing correct programs", on binary search.
- J. L. Bentley and A. C. Yao, "An Almost Optimal Algorithm for Unbounded Searching", *Information Processing Letters*
  5(3), 1976.
- J. L. Carter and M. N. Wegman, "Universal Classes of Hash Functions", *Journal of Computer and System Sciences* 18(2),
  1979.
- M. L. Fredman, J. Komlós and E. Szemerédi, "Storing a Sparse Table with $O(1)$ Worst Case Access Time", *Journal of the
  ACM* 31(3), 1984.
- R. Pagh and F. F. Rodler, "Cuckoo Hashing", *Journal of Algorithms* 51(2), 2004 (ESA 2001).
- P. Celis, P.-Å. Larson and J. I. Munro, "Robin Hood Hashing", FOCS 1985.
- B. H. Bloom, "Space/Time Trade-offs in Hash Coding with Allowable Errors", *Communications of the ACM* 13(7), 1970.
- A. Kirsch and M. Mitzenmacher, "Less Hashing, Same Performance: Building a Better Bloom Filter", ESA 2006.
- A. Pagh, R. Pagh and M. Ružić, "Linear Probing with Constant Independence", STOC 2007; M. Pătraşcu and M. Thorup,
  "The Power of Simple Tabulation Hashing", STOC 2011.
- S. A. Crosby and D. S. Wallach, "Denial of Service via Algorithmic Complexity Attacks", USENIX Security 2003.
- J.-P. Aumasson and D. J. Bernstein, "SipHash: a Fast Short-Input PRF", INDOCRYPT 2012; PEP 456, "Secure and
  interchangeable hash algorithm".
- M. Mitzenmacher and E. Upfal, *Probability and Computing*, 2nd ed., 2017: balls and bins, the birthday paradox and
  Bloom filters.
- Reference pages on this site: [Binary search](../../searching/binary-search.md),
  [Binary search on the answer](../../searching/binary-search-answer.md),
  [Two pointers](../../searching/two-pointers.md), [Hash table](../../data-structures/hash-table.md).
- The [cryptography book](https://cryptography.akadian.ca/book/) for cryptographic hash functions, and the
  [math books](https://math.akadian.ca/books/) for primes and modular inverses (used in 7.5).
