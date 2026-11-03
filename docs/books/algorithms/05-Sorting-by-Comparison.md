# 5. Sorting by comparison

*A list of a million names is useless until it is in order: you cannot look anything up, find duplicates or merge it
with another list. Sorting is the problem computers have spent more time on than almost any other, and the one where
the ideas of the first four chapters (invariants, recursion, recurrences, amortized thinking) all come together. In
this chapter you will build seven sorting algorithms from scratch, prove each one correct, count exactly how many
comparisons each one makes, and then prove that no algorithm that sorts by comparing can ever beat about $n\log_2 n$
comparisons. You will finish inside the sorts that real libraries use: Timsort in Python, introsort in C++, and
pattern-defeating quicksort.*

!!! abstract "In this chapter"
    **You will learn:**

    - what sorting means precisely, and the two extra properties that matter in practice: stability and sorting in place
    - selection, insertion and bubble sort, with their invariants and their best and worst cases
    - merge sort, the cleanest divide-and-conquer algorithm, and why it always takes $\Theta(n\log n)$ time
    - quicksort with the Lomuto and Hoare partitions, why it can be slow, and a full proof that random pivots make it
      fast on average
    - heapsort: $O(n\log n)$ in the worst case, in place
    - the decision-tree proof that every comparison sort needs $\log_2(n!)\approx n\log_2 n$ comparisons
    - inversions, adaptive sorting, and how Timsort, introsort and pdqsort combine the simple ideas

    **You need:** loop invariants from [Chapter 1](01-What-Is-an-Algorithm.md), Big-O and sums from
    [Chapter 2](02-Measuring-Cost.md), recursion, induction and the master theorem from
    [Chapter 3](03-Recursion-and-Induction.md), and arrays from [Chapter 4](04-Lists-Stacks-and-Queues.md). For 5.4
    you need the idea of an expected value (an average weighted by probability); the
    [probability book](https://math.akadian.ca/books/) explains it, and we recall what we use.

    **Levels:** 5.1 and 5.2 are beginner; 5.3 to 5.6 are intermediate; 5.7 and 5.8 are advanced.

## 5.1 Why sorting matters

Suppose a rover team keeps a log of 200 000 rock samples, each with an identifier, a site and a mass. Questions
arrive all day. Is sample `GALE-41077` in the log? Which two samples have the closest masses? Are there duplicate
identifiers? Which samples appear in both this month's list and last month's? Every one of these questions is slow
on a jumbled list and fast on a sorted one:

- **Lookup.** In a sorted list, binary search ([Chapter 7](07-Searching-and-Hashing.md)) finds an item in about
  $\log_2 n$ steps, 18 for 200 000 items, instead of up to 200 000.
- **Duplicates.** After sorting, equal items sit next to each other, so one pass finds them all.
- **Closest pair of numbers.** After sorting, the closest two values are neighbours, so one pass checks $n-1$ gaps
  instead of $n(n-1)/2$ pairs.
- **Comparing two lists.** Two sorted lists can be walked together, like merging, in one pass.

So a large part of the art of algorithms is: *sort first, then the problem becomes easy.* This is why sorting is in
every standard library, and why it was among the first things anyone programmed on the first stored-program
computers.

### What "sorted" means

We are given a list $a_0,a_1,\dots,a_{n-1}$ of items and a way to compare two items. The output must be a
**permutation** of the input (the same items, each kept exactly as many times as it appeared, rearranged) such that

$$a_0\le a_1\le\cdots\le a_{n-1}.$$

Both parts matter. An "algorithm" that writes $n$ zeros produces a non-decreasing list, but it is not a permutation
of the input. Every correctness proof in this chapter proves both parts.

The items might be numbers, but usually they are **records** (a sample with an identifier, site and mass), and we sort
them by one field, the **key**. The comparison only looks at keys.

A **comparison sort** is an algorithm that learns about the items *only* by asking questions of the form "is
$a_i<a_j$?" It may move items around, copy them and remember answers, but it never looks inside a key (it never asks
"what is the first digit?"). Everything in this chapter is a comparison sort. That is a strength: one program sorts
numbers, strings, dates or rock samples, given only a comparison function. In [Chapter 6](06-Sorting-in-Linear-Time-and-Selection.md)
we break this rule on purpose and go faster.

### Stability

Two records with equal keys are **ties**. A sort is **stable** if tied records come out in the same order they went
in.

Why care? Because people sort in stages. Sort the samples by mass, then sort them by site with a stable sort: within
each site, the samples are still in order of mass. With an unstable sort the second sort would scramble the first.
Spreadsheets, databases and Python's `sorted` all rely on this. (Python's sort is guaranteed stable, and the
documentation says so.)

### In place

A sort is **in place** if it uses only $O(1)$ extra memory besides the input array, or, in the looser sense most books
use, $O(\log n)$ extra for a recursion stack. Merge sort as usually written needs a second array of $n$ items; heapsort
and quicksort do not. When the data barely fits in memory, this matters.

### How we count

We count **comparisons**, because a comparison sort can do nothing useful without one, and because comparing records
(two strings, two dates) is often the expensive part. Moves and swaps are counted when they change the picture. The
program at the end of 5.2 counts every comparison each sort makes, so you can check every claim in this chapter
against real numbers.

## 5.2 Simple sorts: selection, insertion, bubble

Three sorts can be invented by anyone with a hand of playing cards. All three take $\Theta(n^2)$ time in the worst
case, which is too slow for a million items but perfectly fine for twenty, and one of them, insertion sort, lives on
inside every fast library sort. We trace each on the list $[5,2,4,6,1,3]$.

### Selection sort

*Idea:* find the smallest item and put it first; find the smallest of the rest and put it second; and so on.

```python
for i in range(n - 1):
    m = index of the smallest of a[i], ..., a[n-1]
    swap a[i] and a[m]
```

| after pass $i$ | list | sorted prefix |
|---|---|---|
| start | 5 2 4 6 1 3 | |
| 0 | **1** 2 4 6 5 3 | 1 |
| 1 | **1 2** 4 6 5 3 | 1 2 |
| 2 | **1 2 3** 6 5 4 | 1 2 3 |
| 3 | **1 2 3 4** 5 6 | 1 2 3 4 |
| 4 | **1 2 3 4 5** 6 | all |

**Invariant.** Before pass $i$: (a) $a[0..i-1]$ holds the $i$ smallest items in sorted order, and (b) every item in
$a[i..n-1]$ is at least as large as every item in $a[0..i-1]$.

*Proof.* Before pass 0 the prefix is empty, so both parts hold trivially. Suppose they hold before pass $i$. The pass
finds the smallest item $a[m]$ of the rest and swaps it into position $i$. By (b) it is at least every item of the
prefix, so the prefix $a[0..i]$ is still sorted; it is at most every item left in $a[i+1..n-1]$, so (b) holds for
$i+1$; and the prefix now holds the $i+1$ smallest items. Swaps never lose or duplicate an item, so the list is always a
permutation of the input. After pass $n-2$ the prefix holds $n-1$ items in order and the last item is at least all of
them: the list is sorted. $\square$

**Cost.** Pass $i$ compares the current minimum with each of the $n-1-i$ later items, so the total is

$$\sum_{i=0}^{n-2}(n-1-i)=(n-1)+(n-2)+\cdots+1=\frac{n(n-1)}{2}$$

comparisons, *whatever the input*: selection sort cannot notice that a list is already sorted. It does at most $n-1$
swaps, though, which is the fewest of any sort here; if moving an item is very expensive and comparing is cheap, that
can matter.

**Not stable.** The long-distance swap can jump an item over its twin: sorting $[2_a,2_b,1]$ swaps $2_a$ with $1$ to
give $[1,2_b,2_a]$. The program below confirms it on 200 random records.

The reference page [Selection sort](../../sorting/selection-sort.md) has an animation and versions in Java and C++.

### Insertion sort

*Idea:* how most people sort a hand of cards. Keep the cards on the left sorted; take the next card and slide it left
past every bigger card until it fits.

```python
for i in range(1, n):
    x = a[i]
    j = i - 1
    while j >= 0 and x < a[j]:    # shift bigger items one place right
        a[j + 1] = a[j]
        j -= 1
    a[j + 1] = x
```

| $i$ | card $x$ | shifts | list after |
|---|---|---|---|
| 1 | 2 | 1 | **2 5** 4 6 1 3 |
| 2 | 4 | 1 | **2 4 5** 6 1 3 |
| 3 | 6 | 0 | **2 4 5 6** 1 3 |
| 4 | 1 | 4 | **1 2 4 5 6** 3 |
| 5 | 3 | 3 | **1 2 3 4 5 6** |

**Invariant.** Before step $i$, $a[0..i-1]$ contains the items that were originally in positions $0..i-1$, in sorted
order. This is the invariant you proved for "insertion into a sorted list" in [Chapter 1](01-What-Is-an-Algorithm.md),
applied $n-1$ times: inserting $x$ into a sorted list keeps it sorted. After the last step, $i=n$, the whole list is
sorted. $\square$

**Cost.** Step $i$ makes between $1$ and $i$ comparisons. On a list that is already sorted every step makes exactly one
comparison and no shift, so the **best case** is $n-1$ comparisons, linear time. On a reversed list step $i$ shifts all
$i$ earlier items, so the **worst case** is $1+2+\cdots+(n-1)=n(n-1)/2$.

There is a sharper statement. An **inversion** is a pair of positions $i<j$ whose items are in the wrong order,
$a_i>a_j$. Each shift in insertion sort swaps one adjacent out-of-order pair, which removes *exactly one* inversion and
creates none (the two items passed each other and nothing else moved relative to anything). So

$$\text{number of shifts}=\text{number of inversions in the input},$$

and the number of comparisons is between that and that plus $n-1$. In a random permutation each of the $\binom n2$
pairs is out of order with probability $\tfrac12$, so the average is $n(n-1)/4$ inversions: insertion sort is
quadratic on average too, but four times faster than its worst case, and *very* fast on lists with few inversions. The
program below measures 250 036 comparisons for a random list of 1000 items; $1000\cdot999/4\approx249\,750$.

**Stable**, because an item only moves left past items that are *strictly* bigger; it stops at its equal twin. And it
is **in place**. These three facts (fast on nearly sorted input, stable, tiny code with no recursion) are why every
production sort in 5.7 and 5.8 uses insertion sort for short pieces. See [Insertion sort](../../sorting/insertion-sort.md).

### Bubble sort

*Idea:* walk along the list swapping any neighbouring pair that is out of order. The biggest item "bubbles" to the end
on the first pass; repeat on the rest. Stop early if a pass makes no swap.

| after pass | list |
|---|---|
| 1 | 2 4 5 1 3 **6** |
| 2 | 2 4 1 3 **5 6** |
| 3 | 2 1 3 **4 5 6** |
| 4 | 1 2 **3 4 5 6** |
| 5 | no swaps: stop |

**Invariant.** After pass $k$, the last $k$ positions hold the $k$ largest items in sorted order. (During a pass, the
largest item seen so far is carried along by every swap, so it reaches the end of the unsorted part.)

**Cost.** Like insertion sort, every swap fixes exactly one inversion, so it does exactly as many swaps as insertion
sort does shifts. But it pays for them with more comparisons: up to $n(n-1)/2$, and on random input close to that
(499 422 for 1000 items, twice insertion sort's count). With the early exit, a sorted list takes one pass of $n-1$
comparisons. Bubble sort is stable and in place.

Knuth's verdict in *The Art of Computer Programming*, volume 3, is that bubble sort seems to have nothing to recommend
it except a catchy name and some interesting theoretical problems it leads to. We include it because it is the sort everybody invents first, and because it shows that
"swaps adjacent out-of-order pairs" alone forces $\Omega(n^2)$ work: a reversed list has $n(n-1)/2$ inversions, and
each adjacent swap removes only one. **Any algorithm that only swaps neighbours is quadratic in the worst case.** To go
faster, items must jump far. Merge sort, quicksort and heapsort all do. See [Bubble sort](../../sorting/bubble-sort.md).

### The whole family in one program

Here are all seven sorts of this chapter, each written with a counted comparison `less(x, y, c)` so we can see what
they really do. The program checks every one against Python's `sorted` on 300 random lists, tests stability, and
counts comparisons on random, sorted and reversed lists of 1000 items. The later sections explain the rows.

```python
--8<-- "books/algorithms/ch05_comparison_sorts.py"
```

Output:

```
all 7 sorts agree with sorted() on 300 random lists each

stable?
  selection       no
  insertion       yes
  bubble          yes
  merge           yes
  quick (Lomuto)  no
  quick (Hoare)   no
  heapsort        no

comparisons for n = 1000:
  sort               random    sorted  reversed
  selection          499500    499500    499500
  insertion          250036       999    499500
  bubble             499422       999    499500
  merge                8730      4932      5044
  quick (Lomuto)      10334     10870     10545
  quick (Hoare)       14593     14660     14053
  heapsort            16874     17583     15965
  lower bound ceil(log2 1000!) = 8530

random-pivot quicksort, n = 1000: average 11024 comparisons over 200 runs; 2(n+1)H_n - 4n = 10986; 1.386 n log2 n = 13816
```

Look at the gap: the simple sorts need about half a million comparisons for 1000 items, the fast ones about ten
thousand. For a million items the gap is about a factor of 25 000. The last line of the table, $8530$, is a number no
comparison sort can beat on its worst input; 5.6 proves it.

## 5.3 Merge sort

How can we sort faster than $n^2$? The simple sorts work one item at a time. **Divide and conquer** works with halves:
split the problem into smaller problems of the same kind, solve them recursively, and combine the answers. For sorting:

1. If the list has 0 or 1 items, it is already sorted.
2. Otherwise split it into a left half and a right half.
3. Sort each half (recursively).
4. **Merge** the two sorted halves into one sorted list.

All the work is in step 4, and merging is easy. Put the two sorted piles face up; the smallest item overall is on top of
one of them. Take the smaller of the two tops, put it on the output pile, and repeat. When one pile runs out, put the
rest of the other on the end.

### A trace

Sort $[38,27,43,3,9,82,10,15]$. The splits go down to single items; then merges come back up.

<figure class="mars-fig" markdown="0">
<svg viewBox="0 0 680 270" role="img" aria-label="Merge sort of eight numbers drawn from the bottom up. Bottom row: eight single items 38, 27, 43, 3, 9, 82, 10, 15. Above them four merged pairs: 27 38, 3 43, 9 82, 10 15. Above those two merged fours: 3 27 38 43 and 9 10 15 82. At the top the sorted list 3 9 10 15 27 38 43 82. On the right each row is labelled with its merge work, 8 items per level, and three merge levels in all.">
  <g font-size="13" fill="currentColor" text-anchor="middle">
    <rect x="166" y="20" width="240" height="30" rx="4" fill="#7ccf9a" fill-opacity="0.45" stroke="currentColor"/>
    <text x="181" y="40">3</text><text x="211" y="40">9</text><text x="241" y="40">10</text><text x="271" y="40">15</text>
    <text x="301" y="40">27</text><text x="331" y="40">38</text><text x="361" y="40">43</text><text x="391" y="40">82</text>
    <rect x="94" y="85" width="120" height="30" rx="4" fill="#9cc9ea" fill-opacity="0.45" stroke="currentColor"/>
    <text x="109" y="105">3</text><text x="139" y="105">27</text><text x="169" y="105">38</text><text x="199" y="105">43</text>
    <rect x="358" y="85" width="120" height="30" rx="4" fill="#9cc9ea" fill-opacity="0.45" stroke="currentColor"/>
    <text x="373" y="105">9</text><text x="403" y="105">10</text><text x="433" y="105">15</text><text x="463" y="105">82</text>
    <rect x="58" y="150" width="60" height="30" rx="4" fill="#eea66f" fill-opacity="0.45" stroke="currentColor"/>
    <text x="73" y="170">27</text><text x="103" y="170">38</text>
    <rect x="190" y="150" width="60" height="30" rx="4" fill="#eea66f" fill-opacity="0.45" stroke="currentColor"/>
    <text x="205" y="170">3</text><text x="235" y="170">43</text>
    <rect x="322" y="150" width="60" height="30" rx="4" fill="#eea66f" fill-opacity="0.45" stroke="currentColor"/>
    <text x="337" y="170">9</text><text x="367" y="170">82</text>
    <rect x="454" y="150" width="60" height="30" rx="4" fill="#eea66f" fill-opacity="0.45" stroke="currentColor"/>
    <text x="469" y="170">10</text><text x="499" y="170">15</text>
    <rect x="40" y="215" width="30" height="30" rx="4" fill="none" stroke="currentColor"/><text x="55" y="235">38</text>
    <rect x="106" y="215" width="30" height="30" rx="4" fill="none" stroke="currentColor"/><text x="121" y="235">27</text>
    <rect x="172" y="215" width="30" height="30" rx="4" fill="none" stroke="currentColor"/><text x="187" y="235">43</text>
    <rect x="238" y="215" width="30" height="30" rx="4" fill="none" stroke="currentColor"/><text x="253" y="235">3</text>
    <rect x="304" y="215" width="30" height="30" rx="4" fill="none" stroke="currentColor"/><text x="319" y="235">9</text>
    <rect x="370" y="215" width="30" height="30" rx="4" fill="none" stroke="currentColor"/><text x="385" y="235">82</text>
    <rect x="436" y="215" width="30" height="30" rx="4" fill="none" stroke="currentColor"/><text x="451" y="235">10</text>
    <rect x="502" y="215" width="30" height="30" rx="4" fill="none" stroke="currentColor"/><text x="517" y="235">15</text>
  </g>
  <g stroke="currentColor" stroke-width="1.2" fill="none">
    <line x1="55" y1="215" x2="80" y2="180"/><line x1="121" y1="215" x2="96" y2="180"/>
    <line x1="187" y1="215" x2="212" y2="180"/><line x1="253" y1="215" x2="228" y2="180"/>
    <line x1="319" y1="215" x2="344" y2="180"/><line x1="385" y1="215" x2="360" y2="180"/>
    <line x1="451" y1="215" x2="476" y2="180"/><line x1="517" y1="215" x2="492" y2="180"/>
    <line x1="88" y1="150" x2="140" y2="115"/><line x1="220" y1="150" x2="168" y2="115"/>
    <line x1="352" y1="150" x2="404" y2="115"/><line x1="484" y1="150" x2="432" y2="115"/>
    <line x1="154" y1="85" x2="270" y2="50"/><line x1="418" y1="85" x2="302" y2="50"/>
  </g>
  <g font-size="12" fill="currentColor">
    <text x="560" y="40">merge work 8</text>
    <text x="560" y="105">merge work 8</text>
    <text x="560" y="170">merge work 8</text>
    <text x="560" y="235">single items</text>
    <text x="340" y="264" text-anchor="middle">log2 8 = 3 levels of merging, each touching all 8 items: 24 steps in all</text>
  </g>
</svg>
<figcaption>Figure 5.1. Merge sort from the bottom up. Each level of merging copies every item once, and halving 8 items reaches single items after 3 levels, so the total work is 8 × 3.</figcaption>
</figure>

The comparisons made by each merge (counted by running the code):

| merge | result | comparisons |
|---|---|---|
| [38] + [27] | [27, 38] | 1 |
| [43] + [3] | [3, 43] | 1 |
| [27, 38] + [3, 43] | [3, 27, 38, 43] | 3 |
| [9] + [82] | [9, 82] | 1 |
| [10] + [15] | [10, 15] | 1 |
| [9, 82] + [10, 15] | [9, 10, 15, 82] | 3 |
| [3, 27, 38, 43] + [9, 10, 15, 82] | [3, 9, 10, 15, 27, 38, 43, 82] | 7 |

Total: 17 comparisons. That is the worst case for 8 items: every merge here made the maximum possible number.

### Merging is correct and takes linear time

**Lemma (merge).** If $L$ (length $p$) and $R$ (length $q$) are sorted, the merge outputs all $p+q$ items in sorted
order, using at most $p+q-1$ comparisons.

*Proof.* Invariant: before each step, the output holds the smallest items taken so far in sorted order, and every item
in the output is $\le$ every item still waiting in $L$ and $R$. Initially the output is empty. At each step the
smallest waiting item overall is the front of $L$ or the front of $R$ (each list is sorted, so its front is its
smallest), and the merge takes the smaller of those two fronts. So it appends the smallest waiting item, which is
$\ge$ everything already output (by the invariant): the invariant is kept. When one list is empty the rest of the other
is sorted and $\ge$ the output, so appending it finishes correctly. Each comparison outputs one item, and the last
item is always output without a comparison, so at most $p+q-1$ comparisons are made. $\square$

The merge in our code takes from the right list only when its front is *strictly* smaller; on a tie it takes from the
left. Equal items from the left half (which came earlier in the input) therefore come out first, and **merge sort is
stable**. Change `<` to `<=` and it is not.

### Correctness of merge sort

*Proof by strong induction on $n$* ([Chapter 3](03-Recursion-and-Induction.md)). Lists of length 0 or 1 are sorted.
For $n\ge2$, the halves have lengths $\lfloor n/2\rfloor$ and $\lceil n/2\rceil$, both smaller than $n$, so by induction
the recursive calls sort them; by the merge lemma the merge produces a sorted permutation of the whole list. $\square$

### Running time

Let $T(n)$ be the time on a list of length $n$. The split costs $O(n)$ (copying, in Python) or $O(1)$ (index
arithmetic), the two recursive calls cost $T(\lfloor n/2\rfloor)+T(\lceil n/2\rceil)$, and the merge costs $\Theta(n)$.
So

$$T(n)=T(\lfloor n/2\rfloor)+T(\lceil n/2\rceil)+\Theta(n),\qquad T(1)=\Theta(1).$$

For $n$ a power of 2 and the merge costing exactly $cn$, unroll it ([Chapter 3](03-Recursion-and-Induction.md), 3.5):

$$\begin{aligned}
T(n)&=2T(n/2)+cn\\
&=4T(n/4)+cn+cn\\
&=8T(n/8)+3cn\\
&\;\;\vdots\\
&=2^kT(n/2^k)+kcn.
\end{aligned}$$

With $k=\log_2 n$ this is $nT(1)+cn\log_2 n=\Theta(n\log n)$. The picture is Figure 5.1: $\log_2 n$ levels, each doing
$cn$ work. The master theorem (case 2, with $a=b=2$ and $f(n)=\Theta(n)$) gives the same for every $n$.

The exact worst-case comparison count $W(n)$ satisfies $W(n)=W(\lfloor n/2\rfloor)+W(\lceil n/2\rceil)+n-1$, whose
solution is

$$W(n)=n\lceil\log_2 n\rceil-2^{\lceil\log_2 n\rceil}+1.$$

For $n=8$: $8\cdot3-8+1=17$, as in the trace. For $n=1000$: $1000\cdot10-1024+1=8977$. (Exercise 9 asks you to check the
formula by induction.)

Crucially, $\Theta(n\log n)$ holds for *every* input: the splits are always even, whatever the data. On a sorted list
the merges stop early (each merge of two halves of size $m$ needs only $m$ comparisons, because the left half runs out
first), which is why the table shows 4932 instead of 8730, but the copying still costs $n\log_2 n$.

**Space.** The merge needs somewhere to put its output: $\Theta(n)$ extra memory. In-place merging in linear time is
possible but complicated and slow in practice, so merge sort is the standard example of a fast sort that is *not* in
place. It shines where data is read in order anyway: linked lists (no extra array needed) and files too big for memory
(external merge sort, [Chapter 24](24-Algorithms-for-Big-Data-and-Many-Processors.md)).

**History.** John von Neumann described merge sort in 1945 as a test program for the EDVAC design, one of the first
programs written for a stored-program computer. The reference page [Merge sort](../../sorting/merge-sort.md) has an
animation and Java and C++ versions that use one scratch array.

## 5.4 Quicksort

Merge sort does its work *after* the recursive calls (in the merge). Quicksort does it *before*: it arranges the list so
that, once the two parts are sorted, nothing remains to be done.

1. Pick an item, the **pivot**.
2. **Partition**: rearrange the list so that items smaller than the pivot come first, then the pivot, then the rest.
3. Sort the part before the pivot and the part after it (recursively). Done: no merge needed.

Tony Hoare invented quicksort around 1959-1960 and published it in 1961 (as Algorithm 64 in *Communications of the
ACM*) and in a full paper, "Quicksort", in *The Computer Journal* in 1962. It is in place, it has an extremely tight
inner loop, and it is still the basis of most unstable library sorts.

### The Lomuto partition

The easiest partition to prove correct is usually credited to Nico Lomuto and was made popular by Jon Bentley's
*Programming Pearls*. Use the last item $a[hi]$ as the pivot $x$. Sweep $j$ from left to right, keeping a boundary $i$:

<figure class="mars-fig" markdown="0">
<svg viewBox="0 0 640 150" role="img" aria-label="The Lomuto partition invariant. An array from lo to hi is split into four regions: from lo to i minus 1 the items less than the pivot, from i to j minus 1 the items at least the pivot, from j to hi minus 1 items not yet examined, and the pivot at position hi.">
  <rect x="30" y="50" width="160" height="40" fill="#7ccf9a" fill-opacity="0.5" stroke="currentColor"/>
  <rect x="190" y="50" width="160" height="40" fill="#eea66f" fill-opacity="0.5" stroke="currentColor"/>
  <rect x="350" y="50" width="200" height="40" fill="none" stroke="currentColor" stroke-dasharray="5 4"/>
  <rect x="550" y="50" width="50" height="40" fill="#9cc9ea" fill-opacity="0.6" stroke="currentColor"/>
  <g font-size="13" fill="currentColor" text-anchor="middle">
    <text x="110" y="75">less than x</text>
    <text x="270" y="75">at least x</text>
    <text x="450" y="75">not yet examined</text>
    <text x="575" y="75">x</text>
    <text x="38" y="35">lo</text>
    <text x="198" y="35">i</text>
    <text x="358" y="35">j</text>
    <text x="575" y="35">hi</text>
    <text x="320" y="125">each step looks at a[j]: if a[j] &lt; x, swap it with a[i] and move i right</text>
  </g>
  <g stroke="currentColor" stroke-width="1.2">
    <line x1="38" y1="40" x2="38" y2="50"/><line x1="198" y1="40" x2="198" y2="50"/>
    <line x1="358" y1="40" x2="358" y2="50"/><line x1="575" y1="40" x2="575" y2="50"/>
  </g>
</svg>
<figcaption>Figure 5.2. The Lomuto invariant. The green part grows when the next item is small; the orange part grows when it is not. At the end the pivot is swapped to position i, between them.</figcaption>
</figure>

**Invariant.** Before looking at $a[j]$: every item in $a[lo..i-1]$ is $<x$, every item in $a[i..j-1]$ is $\ge x$.

At $a[j]$: if $a[j]\ge x$, just move $j$ on; the orange region grows. If $a[j]<x$, swap $a[j]$ with $a[i]$ (the first
orange item, or $a[j]$ itself if there is none) and move both $i$ and $j$; the green region grows and the orange one
shifts right by one. Either way the invariant holds again. At the end ($j=hi$), swap the pivot $a[hi]$ with $a[i]$.
Now $a[lo..i-1]<x=a[i]\le a[i+1..hi]$: partitioned. It makes exactly $hi-lo$ comparisons.

Trace on $[7,2,9,4,3,8,6,5]$ with pivot $x=5$:

| $j$ | $a[j]$ | action | $i$ after | array after |
|---|---|---|---|---|
| 0 | 7 | $\ge5$: skip | 0 | 7 2 9 4 3 8 6 5 |
| 1 | 2 | $<5$: swap $a[0],a[1]$ | 1 | 2 7 9 4 3 8 6 5 |
| 2 | 9 | skip | 1 | 2 7 9 4 3 8 6 5 |
| 3 | 4 | swap $a[1],a[3]$ | 2 | 2 4 9 7 3 8 6 5 |
| 4 | 3 | swap $a[2],a[4]$ | 3 | 2 4 3 7 9 8 6 5 |
| 5 | 8 | skip | 3 | 2 4 3 7 9 8 6 5 |
| 6 | 6 | skip | 3 | 2 4 3 7 9 8 6 5 |
| end | | swap pivot into $a[3]$ | | 2 4 3 **5** 9 8 6 7 |

The pivot 5 is now in its final place, index 3; quicksort recurses on $[2,4,3]$ and $[9,8,6,7]$.

### The Hoare partition

Hoare's own partition uses two fingers that start at the two ends and move toward each other. The left finger $i$
moves right past items smaller than the pivot; the right finger $j$ moves left past items larger than it; when both
stop, the two items are each on the wrong side, so swap them and continue. When the fingers cross, stop.

```python
pivot = a[lo]
i, j = lo - 1, hi + 1
while True:
    i += 1
    while a[i] < pivot: i += 1
    j -= 1
    while pivot < a[j]: j -= 1
    if i >= j: return j
    a[i], a[j] = a[j], a[i]
```

Trace on $[5,2,9,4,3,8,6,7]$ with pivot $a[0]=5$: $i$ stops at once at 5 (not $<5$); $j$ moves left past 7, 6, 8 and
stops at 3. Swap: $[3,2,9,4,5,8,6,7]$. Now $i$ moves past 2 and stops at 9 (index 2); $j$ stops at 4 (index 3). Swap:
$[3,2,4,9,5,8,6,7]$. Then $i$ stops at 9 (index 3), $j$ stops at 4 (index 2); they have crossed, return $j=2$. The
parts are $a[0..2]=[3,2,4]$ and $a[3..7]=[9,5,8,6,7]$: everything on the left is $\le5$, everything on the right is
$\ge5$.

Two differences from Lomuto are worth knowing:

1. The pivot does *not* end in its final place, and the split is $[lo..j]$ and $[j+1..hi]$, both of which may contain
   pivot-equal items. (Recursing on $[lo..j-1]$, as with Lomuto, is a classic bug.)
2. It does far fewer swaps. On a random array Lomuto swaps every small item, about $n/2$ swaps; Hoare swaps only items
   that are on the wrong side, about $n/6$. The second program in 5.7 measures 497 against 167 for $n=1000$. It
   makes a few more comparisons (both fingers compare with the pivot at the crossing point), which is the extra in
   the table's Hoare row, but swaps are what cost time on real hardware.

Hoare's partition also behaves well when there are many equal keys: both fingers stop at items equal to the pivot and
swap them, so equal items are spread evenly between the two sides. Lomuto puts all of them on one side, and on a list of
$n$ equal items it degrades to $n^2/2$ comparisons. (Exercise 5.)

*Why does Hoare's loop never run off the ends of the array?* On the first round $i$ stops at the pivot itself, at
$lo$. After a swap, the item now at $a[i]$ is $\le$ pivot and the item at $a[j]$ is $\ge$ pivot, so on the next round
the $j$ loop must stop by position $i$ at the latest, and the $i$ loop by position $j$. The full proof that the returned
$j$ satisfies $lo\le j<hi$ (so both parts are strictly smaller and the recursion ends) is CLRS problem 7-1.

### Correctness of quicksort

By strong induction on the length. After the partition, everything in the left part is $\le$ everything in the right
part (and, for Lomuto, the pivot sits between them). Both parts are shorter than the whole, so by induction the
recursive calls sort them, and a sorted left part followed by a sorted right part, with every left item $\le$ every
right item, is a sorted list. Partitioning only swaps, so the result is a permutation. $\square$

### The worst case

Quicksort's time depends on how evenly the pivot splits the list. If a partition of $m$ items leaves parts of sizes $k$
and $m-1-k$,

$$T(m)=T(k)+T(m-1-k)+\Theta(m).$$

**Worst case.** If the pivot is always the smallest or largest item, one part is empty and the other has $m-1$ items:
$T(n)=T(n-1)+\Theta(n)$, so $T(n)=\Theta(n+(n-1)+\cdots+1)=\Theta(n^2)$. With "last item as pivot", this happens on an
*already sorted list*, the most common input in real life! The second program shows a first-item-pivot quicksort
making $1\,999\,000=2000\cdot1999/2$ comparisons on a sorted list of 2000.

**Best case.** A perfect median pivot gives $T(n)=2T(n/2)+\Theta(n)=\Theta(n\log n)$, like merge sort. Even a lopsided
but constant-ratio split, say always 1 to 9, gives $T(n)=T(n/10)+T(9n/10)+cn$: the recursion tree has depth
$\log_{10/9}n$ and every level costs at most $cn$, so $T(n)=O(n\log n)$. Only *systematically* bad pivots hurt.

### Random pivots

The fix is to choose the pivot **uniformly at random** from the current part. Then no input is bad: for every input,
the *expected* number of comparisons (averaged over the algorithm's own coin flips, not over inputs) is about
$1.39\,n\log_2 n$. This is a much stronger promise than "fast on average over random inputs", because an adversary who
knows our code still cannot pick a bad list.

**Theorem.** Randomized quicksort (Lomuto partition, uniformly random pivot) on $n$ distinct items makes, in
expectation,

$$E[C_n]=2(n+1)H_n-4n$$

comparisons, where $H_n=1+\tfrac12+\cdots+\tfrac1n$ is the $n$-th harmonic number. Since $H_n=\ln n+O(1)$, this is
$2n\ln n+O(n)\approx1.386\,n\log_2 n$.

*Proof.* Name the items by their rank: $z_1<z_2<\cdots<z_n$ in sorted order. Two observations:

1. Two items are compared only when one of them is the current pivot, and the pivot is then set aside for good. So
   each pair is compared **at most once**.
2. Consider $z_i$ and $z_j$ with $i<j$, and the block $Z_{ij}=\{z_i,z_{i+1},\dots,z_j\}$. Until some item of this
   block is chosen as a pivot, all of the block stays together in the same part (a pivot outside the block is either
   smaller or larger than all of it). Look at the *first* pivot chosen from the block. If it is $z_i$ or $z_j$, the two
   are compared (the pivot is compared with everything in its part). If it is some $z_k$ strictly between, then $z_i$
   goes left and $z_j$ goes right, and they are never compared.

Because each pivot is uniform over its part, and the whole block is in that part, the first pivot from the block is
equally likely to be any of its $j-i+1$ items. So

$$P(z_i\text{ and }z_j\text{ are compared})=\frac{2}{j-i+1}.$$

Let $X_{ij}$ be the **indicator variable** of that event: $1$ if they are compared, $0$ if not. Its expectation is the
probability, and the total number of comparisons is $C_n=\sum_{i<j}X_{ij}$. By **linearity of expectation** (the
expectation of a sum is the sum of expectations, always, even for dependent variables),

$$E[C_n]=\sum_{i=1}^{n-1}\sum_{j=i+1}^{n}\frac{2}{j-i+1}.$$

Group the pairs by their gap $d=j-i$: there are $n-d$ pairs with gap $d$. Writing $k=d+1$,

$$\begin{aligned}
E[C_n]&=\sum_{k=2}^{n}(n+1-k)\frac{2}{k}=2(n+1)\sum_{k=2}^{n}\frac1k-2\sum_{k=2}^{n}1\\
&=2(n+1)(H_n-1)-2(n-1)=2(n+1)H_n-4n.\qquad\square
\end{aligned}$$

Check it on small cases. $n=2$: $2\cdot3\cdot\tfrac32-8=1$, and indeed one comparison sorts two items. $n=3$: the formula
gives $\tfrac83$. By hand: the first partition costs 2; with probability $\tfrac13$ the pivot is the middle item and
we are done; with probability $\tfrac23$ it is an end item and one more comparison sorts the remaining pair. So
$E=\tfrac13\cdot2+\tfrac23\cdot3=\tfrac83$. For $n=1000$ the formula gives 10 986; the program averaged 11 024 over 200
runs.

The same analysis shows the *probability* of doing much worse than this is tiny: the chance of more than, say, $c\,n\ln n$ comparisons for a constant $c$ well above 2 shrinks like a power of $n$. That needs tail bounds, which
[Chapter 21](21-Randomized-and-Amortized-Analysis.md) proves.

**Space.** The recursion is the only extra memory. If we always recurse on the *smaller* part and loop on the larger
(as `quicksort_lomuto` above does), each recursive call is on at most half the items, so the stack is at most
$\log_2 n$ deep even in the worst case. Every serious implementation uses this trick.

**Why is quicksort fast in practice, if it does about 39% more comparisons than merge sort?** Its inner loop is a
comparison with one fixed pivot held in a register and a pointer increment; it reads memory in order (good for caches,
[Chapter 2](02-Measuring-Cost.md), 2.9); it needs no extra array and no copying. Merge sort moves every item at every
level. For numbers in arrays, the constant factors favour quicksort. For records with expensive comparisons (Python
objects), they favour merge-based sorts, which is one reason Python uses Timsort (5.7). See [Quicksort](../../sorting/quicksort.md).

## 5.5 Heapsort

Merge sort is $O(n\log n)$ always but not in place. Quicksort is in place but only $O(n\log n)$ in expectation. Can we
have both? **Heapsort** (J. W. J. Williams, 1964, with an improvement by Robert Floyd the same year) does: $O(n\log n)$
in the worst case, $O(1)$ extra memory.

It is selection sort with a better way to find the maximum. Selection sort spends $n-1-i$ comparisons finding each
minimum by scanning. Heapsort keeps the unsorted part arranged as a **binary max-heap**, a structure in which the maximum
is always at the front and can be removed in $O(\log n)$ time.

**The heap in an array.** Think of the array positions as the nodes of a binary tree, filled level by level: position
0 is the root, and the children of position $i$ are $2i+1$ and $2i+2$ (so the parent of $i$ is $\lfloor(i-1)/2\rfloor$).
A **max-heap** is an array in which every item is $\ge$ its children. Then the root, $a[0]$, is the maximum. No pointers
are stored; the tree is pure index arithmetic. The tree has height $\lfloor\log_2 n\rfloor$ because each level doubles
in size.

**Sift down.** If the root is the only item out of place (both of its subtrees are heaps), swap it with its larger child,
and repeat from there, until it is $\ge$ both children or is a leaf. Each step costs 2 comparisons and moves one level
down, so sift-down costs at most $2\lfloor\log_2 n\rfloor$ comparisons. Why it restores the heap: after the swap the
larger child is the new parent and it is $\ge$ the other child and $\ge$ the old root, so this node is fine; only the
subtree where the old root landed might be wrong, and it is handled by the next step.

**Heapsort.**

1. **Build a heap**: sift down every non-leaf position, from the last ($\lfloor n/2\rfloor-1$) back to 0. When we sift
   position $i$, both its subtrees are already heaps, so sift-down applies.
2. **Repeat** for $end=n-1$ down to 1: swap $a[0]$ (the maximum of the heap) with $a[end]$, so it lands in its final
   place; the heap is now $a[0..end-1]$ with only the root wrong; sift it down.

Trace on $[4,10,3,5,1,8,7]$:

| step | array | note |
|---|---|---|
| sift 2 | 4 10 **8** 5 1 **3** 7 | 3 swapped with its larger child 8 |
| sift 1 | 4 10 8 5 1 3 7 | 10 is already $\ge$ 5 and 1 |
| sift 0 | **10 5** 8 **4** 1 3 7 | 4 goes down twice: heap built |
| out 10 | 8 5 7 4 1 3 \| 10 | |
| out 8 | 7 5 3 4 1 \| 8 10 | |
| out 7 | 5 4 3 1 \| 7 8 10 | |
| out 5 | 4 1 3 \| 5 7 8 10 | |
| out 4 | 3 1 \| 4 5 7 8 10 | |
| out 3 | 1 \| 3 4 5 7 8 10 | sorted |

**Correctness.** Invariant of phase 2: $a[0..end]$ is a max-heap, and $a[end+1..n-1]$ holds the $n-1-end$ largest
items in sorted order. Swapping the root (the largest of the heap, which is $\le$ everything to its right) into
position $end$ extends the sorted tail by one; sift-down repairs the heap. $\square$

**Cost.** Building costs at most $n/2$ sift-downs of $O(\log n)$ each, and phase 2 costs $n-1$ sift-downs: $O(n\log n)$
in total, in every case. (In fact the building phase is only $O(n)$, because most nodes are near the bottom and sift
only a little way; [Chapter 9](09-Heaps-and-Priority-Queues.md) proves it.) The table shows heapsort making about
twice merge sort's comparisons, $2n\log_2 n$ against $n\log_2 n$, because each sift step makes two comparisons.

**Not stable**, and in practice slower than quicksort, because it jumps around the array (from $i$ to $2i+1$), which
defeats the cache. Its real job in modern libraries is as a guaranteed fallback (5.8). The data structure is the star of
[Chapter 9](09-Heaps-and-Priority-Queues.md); the reference pages are [Binary heap](../../data-structures/binary-heap.md)
and [Heapsort](../../sorting/heapsort.md).

## 5.6 The n log n lower bound for comparison sorts

Merge sort and heapsort both take about $n\log_2 n$ comparisons. Is there a cleverer comparison sort that takes, say,
$n\log_2\log_2 n$? No, and the proof is one of the most beautiful in the subject, because it is about *every possible
algorithm at once*, including ones nobody has invented.

### Decision trees

Fix $n$. Any comparison sort, run on inputs of size $n$, can be drawn as a **decision tree**. Each internal node is a
comparison "$a_i:a_j$?". The algorithm starts at the root, asks that question, and goes to the left child if the
answer is $a_i\le a_j$ and to the right child otherwise; the next question it asks may depend on all answers so far,
which is exactly what the tree records. A **leaf** is where the algorithm stops; at that point it has decided how to
rearrange the input, so a leaf is labelled with a permutation. The moves and copies the algorithm makes between
comparisons are not drawn: they cannot affect which comparison comes next unless a comparison is made.

Here is insertion sort's tree for three items $a_1,a_2,a_3$:

<figure class="mars-fig" markdown="0">
<svg viewBox="0 0 700 290" role="img" aria-label="The decision tree of insertion sort on three items. The root compares a1 with a2. If a1 is at most a2 it compares a2 with a3: at most gives the order 1 2 3, otherwise it compares a1 with a3, giving 1 3 2 or 3 1 2. If a1 is greater than a2 it compares a1 with a3: at most gives 2 1 3, otherwise it compares a2 with a3, giving 2 3 1 or 3 2 1. Six leaves, height 3.">
  <g stroke="currentColor" stroke-width="1.3" fill="none">
    <line x1="340" y1="45" x2="170" y2="100"/><line x1="340" y1="45" x2="510" y2="100"/>
    <line x1="170" y1="130" x2="80" y2="185"/><line x1="170" y1="130" x2="260" y2="185"/>
    <line x1="510" y1="130" x2="420" y2="185"/><line x1="510" y1="130" x2="600" y2="185"/>
    <line x1="260" y1="215" x2="210" y2="245"/><line x1="260" y1="215" x2="310" y2="245"/>
    <line x1="600" y1="215" x2="550" y2="245"/><line x1="600" y1="215" x2="650" y2="245"/>
  </g>
  <g font-size="13" fill="currentColor" text-anchor="middle">
    <ellipse cx="340" cy="30" rx="42" ry="15" fill="#9cc9ea" fill-opacity="0.55" stroke="currentColor"/>
    <text x="340" y="35">a1 : a2</text>
    <ellipse cx="170" cy="115" rx="42" ry="15" fill="#9cc9ea" fill-opacity="0.55" stroke="currentColor"/>
    <text x="170" y="120">a2 : a3</text>
    <ellipse cx="510" cy="115" rx="42" ry="15" fill="#9cc9ea" fill-opacity="0.55" stroke="currentColor"/>
    <text x="510" y="120">a1 : a3</text>
    <ellipse cx="260" cy="200" rx="42" ry="15" fill="#9cc9ea" fill-opacity="0.55" stroke="currentColor"/>
    <text x="260" y="205">a1 : a3</text>
    <ellipse cx="600" cy="200" rx="42" ry="15" fill="#9cc9ea" fill-opacity="0.55" stroke="currentColor"/>
    <text x="600" y="205">a2 : a3</text>
    <rect x="48" y="185" width="64" height="28" rx="4" fill="#7ccf9a" fill-opacity="0.5" stroke="currentColor"/>
    <text x="80" y="204">1 2 3</text>
    <rect x="388" y="185" width="64" height="28" rx="4" fill="#7ccf9a" fill-opacity="0.5" stroke="currentColor"/>
    <text x="420" y="204">2 1 3</text>
    <rect x="178" y="245" width="64" height="28" rx="4" fill="#7ccf9a" fill-opacity="0.5" stroke="currentColor"/>
    <text x="210" y="264">1 3 2</text>
    <rect x="278" y="245" width="64" height="28" rx="4" fill="#7ccf9a" fill-opacity="0.5" stroke="currentColor"/>
    <text x="310" y="264">3 1 2</text>
    <rect x="518" y="245" width="64" height="28" rx="4" fill="#7ccf9a" fill-opacity="0.5" stroke="currentColor"/>
    <text x="550" y="264">2 3 1</text>
    <rect x="618" y="245" width="64" height="28" rx="4" fill="#7ccf9a" fill-opacity="0.5" stroke="currentColor"/>
    <text x="650" y="264">3 2 1</text>
  </g>
  <g font-size="12" fill="currentColor" text-anchor="middle">
    <text x="240" y="66">≤</text><text x="440" y="66">&gt;</text>
    <text x="113" y="155">≤</text><text x="227" y="155">&gt;</text>
    <text x="453" y="155">≤</text><text x="567" y="155">&gt;</text>
    <text x="225" y="232">≤</text><text x="297" y="232">&gt;</text>
    <text x="565" y="232">≤</text><text x="637" y="232">&gt;</text>
  </g>
</svg>
<figcaption>Figure 5.3. Insertion sort's decision tree for three items. A leaf "3 1 2" means the sorted order is a3, a1, a2. There are 3! = 6 leaves, so some path must have length at least log2 6 ≈ 2.58, that is 3.</figcaption>
</figure>

The **worst-case number of comparisons** of the algorithm is the length of the longest root-to-leaf path: the
**height** $h$ of the tree.

**Theorem.** Every comparison sort makes at least $\lceil\log_2(n!)\rceil$ comparisons on some input of size $n$. So its
worst case is $\Omega(n\log n)$.

*Proof.* Consider the $n!$ inputs that are the permutations of $1,2,\dots,n$. Two different permutations need different
rearrangements to sort them, so they must reach *different* leaves (if two reached the same leaf, the algorithm would
apply the same rearrangement to both and at least one would come out unsorted). So the tree has at least $n!$ leaves.
A binary tree of height $h$ has at most $2^h$ leaves (each level at most doubles the count). Hence

$$2^h\ge n!,\qquad h\ge\log_2(n!).$$

Since $h$ is a whole number, $h\ge\lceil\log_2 n!\rceil$. Finally, $\log_2(n!)=\Omega(n\log n)$: the largest $n/2$ factors of
$n!$ are each at least $n/2$, so

$$\log_2(n!)\ge\log_2\Big(\big(\tfrac n2\big)^{n/2}\Big)=\frac n2\log_2\frac n2=\Omega(n\log n).\qquad\square$$

**How good is the bound?** Stirling's formula, $n!\approx\sqrt{2\pi n}\,(n/e)^n$, gives the precise size:

$$\log_2(n!)=n\log_2 n-n\log_2 e+O(\log n)\approx n\log_2 n-1.443\,n.$$

So the bound is not just "some constant times $n\log n$"; it has leading constant 1. Merge sort's worst case is
$n\log_2 n-n+1$ when $n$ is a power of two: it matches the bound to within about $0.44\,n$ comparisons. Here are both,
computed by the second program of this chapter:

| $n$ | $\lceil\log_2 n!\rceil$ | merge sort worst case |
|---|---|---|
| 2 | 1 | 1 |
| 3 | 3 | 3 |
| 4 | 5 | 5 |
| 5 | 7 | 8 |
| 8 | 16 | 17 |
| 12 | 29 | 33 |
| 100 | 525 | 573 |
| 1000 | 8530 | 8977 |
| $10^6$ | 18 488 885 | 18 951 425 |

For small $n$ people have found the exact optimum. Five items can be sorted with 7 comparisons, matching the bound
(merge sort needs 8). The Ford-Johnson "merge insertion" algorithm (1959) matches the bound up to $n=11$; for $n=12$
the bound says 29 but Mark Wells proved in 1965, by computer search, that 30 are needed. So the information-theoretic
bound is not always exact. Knuth's *TAOCP* volume 3, section 5.3.1, tells this story with all the details.

**The average case is no better.** The bound above is for the worst input. A stronger version says the *average* depth
of the $n!$ leaves is also at least $\log_2(n!)$, so even averaged over random inputs no comparison sort beats
$n\log_2 n-1.443n$ by more than lower-order terms. *Sketch:* among binary trees with $N$ leaves, the average leaf depth is
smallest when all leaves sit on at most two adjacent levels (if a leaf is two or more levels above another, moving a
pair of deep sibling leaves up to hang under the shallow leaf reduces the total depth), and for such trees the average
depth is at least $\log_2 N$. CLRS problem 8-1 does it in full.

**What the bound does not say.** It says nothing about algorithms that look inside keys. If keys are small integers, we
can use them as array indices and sort in linear time, which is [Chapter 6](06-Sorting-in-Linear-Time-and-Selection.md).
And it counts comparisons only; it does not say that an $n\log n$ sort is fast in seconds (that is 5.7 and 5.8). The
same argument proves lower bounds for other problems: finding an item in a sorted list needs $\lceil\log_2(n+1)\rceil$
comparisons (there are $n+1$ possible answers), and merging two sorted lists of length $n$ needs at least
$\log_2\binom{2n}{n}\approx2n-\tfrac12\log_2 n$ (Exercise 10).

The idea of the proof, counting how many outcomes must be told apart and dividing by how many each question can split,
is information theory: each yes/no answer gives at most one **bit** of information, and the output needs
$\log_2(n!)$ bits to describe.

## 5.7 Inversions, adaptive sorting and Timsort

*Level: advanced.*

Real data is rarely random. Log files are almost in time order; a list sorted yesterday has had a few items appended;
a table is sorted by one column and needs sorting by a related one. A sort that is fast on such input is called
**adaptive**. The lower bound of 5.6 is about the *worst* input; on easy inputs we can do better.

### Measuring presortedness

How "nearly sorted" is a list? There are several measures:

- **Inversions**, $\mathrm{Inv}$: the number of out-of-order pairs, from $0$ (sorted) to $\binom n2$ (reversed).
  Insertion sort runs in $\Theta(n+\mathrm{Inv})$ time (5.2).
- **Runs**, $\mathrm{Runs}$: the number of maximal non-decreasing stretches. A sorted list has 1, a random one about
  $n/2$. Merging the runs pairwise takes $O(n\log\mathrm{Runs})$ time.
- Others: how far items are from their final positions, the number of items you must remove to leave a sorted list.

For each measure there is a matching lower bound, by the same counting as 5.6: if few permutations have measure at most
$m$, few comparisons are needed to tell them apart. For example, there are at most $\mathrm{Runs}^n$ ways to fill $n$
items into $\mathrm{Runs}$ sorted runs, so about $n\log_2\mathrm{Runs}$ comparisons are necessary and, by merging
runs, sufficient. A sort is **optimally adaptive** for a measure if it meets that bound. (Estivill-Castro and Wood's
survey "A Survey of Adaptive Sorting Algorithms", 1992, collects the measures and algorithms.)

### Counting inversions in $O(n\log n)$

Counting inversions by checking all pairs takes $\Theta(n^2)$. Merge sort can count them on the way, a classic
divide-and-conquer idea that [Chapter 11](11-Divide-and-Conquer.md) uses again. Every inversion $(i,j)$ is of one of
three kinds: both in the left half, both in the right half, or *split* ($i$ left, $j$ right). The first two are counted
recursively. For the split ones: during the merge, when the front of the right list $R[q]$ is output before the
remaining left items $L[p..]$, it is smaller than every one of them, and each forms a split inversion with it. So add
`len(left) - p` at that moment. The merge does the counting for free; the time is still $O(n\log n)$.

### Natural merge sort and Python's sorted

The second program below finds the runs of a list (reversing strictly decreasing runs, which is safe for stability
because they contain no equal items), then merges neighbouring runs until one is left. It also counts the comparisons
Python's own `sorted` makes, by wrapping each value in an object whose `<` counts its calls.

```python
--8<-- "books/algorithms/ch05_lower_bound_and_runs.py"
```

Output:

```
n   ceil(log2 n!)  merge sort worst
2               1                 1
3               3                 3
4               5                 5
5               7                 8
8              16                17
12             29                33
16             45                49
100           525               573
1000         8530              8977
n = 10^6: ceil(log2 n!) = 18488885, n log2 n = 19931569, merge sort worst = 18951425

inversions
  [2, 4, 1, 3, 5]: 3
  [5, 4, 3, 2, 1]: 10
  [1, 2, 3, 4, 5]: 0
  random permutation of 10^5: 2504618515 inversions (expected n(n-1)/4 = 2499975000)

adaptive sorting, n = 10000 (comparisons)
  input       runs  natural merge  Python sorted
  random      4116         133193         120169
  sorted         1           9999           9999
  reversed       1           9999           9999
  10 swaps      21          49165          11025
  two runs       2          19998          19999
  ceil(log2 n!) = 118459

introsort versus naive quicksort (first element as pivot), sorted input
  n = 500: naive 124750 comparisons, introsort 15340 (heapsort took over 1 time)
  n = 2000: naive 1999000 comparisons, introsort 78644 (heapsort took over 1 time)

swaps in one partition of a random array of 1000 (average of 2000 trials)
  Lomuto 497, Hoare 167
```

Read the adaptive table row by row. On sorted and reversed lists both sorts find one run and stop after $n-1$
comparisons: linear time, far below the $118\,459$ that a random list must cost. On "two runs" (the even numbers then
the odd numbers) both need about $2n$: $n$ to find the runs and $n$ to merge them. The interesting row is "10 swaps":
ten random exchanges break the list into 21 runs. Our natural merge sort needs 49 165 comparisons, because it merges
the runs blindly in pairs, and some runs are huge and some are one item long. Python needs only 11 025. On random data
Python is also about 10% better than our merge, and within 2% of the lower bound. How?

### Timsort

Python's list sort is **Timsort**, written by Tim Peters for Python 2.3 in 2002 and described in his notes
`listsort.txt` in the CPython source. It is a natural merge sort with four engineering ideas:

1. **Find runs, and make short ones longer.** It scans for a run (non-decreasing, or strictly decreasing and then
   reversed). If the run is shorter than a minimum length `minrun` (chosen between 32 and 64 so that $n/\text{minrun}$
   is close to a power of 2), it extends the run to `minrun` items with **binary insertion sort**: insertion sort that
   finds each item's place by binary search, so it makes $O(\log\text{minrun})$ comparisons per item even though it
   still shifts. So random data becomes $n/\text{minrun}$ sorted runs very cheaply, and merging those is balanced.
2. **Merge runs with balance rules.** Runs go on a stack. Timsort merges neighbouring runs when their lengths break
   rules like "each run is longer than the next two above it combined", so that merges are always between runs of
   similar size (like the levels of merge sort) and the stack stays $O(\log n)$ deep. Merging similar sizes is what
   makes the total $O(n\log\mathrm{Runs})$ instead of the blind pairing's waste.
3. **Galloping.** When one run keeps winning during a merge (as when a run of 5000 items is merged with a run of 3), the
   merge switches to **exponential search**: compare with the item 1, 3, 7, 15, ... places ahead, then binary search in
   the last gap ([Chapter 7](07-Searching-and-Hashing.md)). A block of $k$ items that all go to the output together is
   then found with about $2\log_2 k$ comparisons instead of $k$. This is what saves the "10 swaps" row.
4. **Merge in a temporary copy of the smaller run only**, which halves the extra memory compared with plain merge sort.

Timsort is stable, $O(n\log n)$ in the worst case and $O(n)$ on already ordered data. Java has used it for sorting
objects since Java 7 (2011). Two later chapters of its story are worth knowing because they show how hard
"obviously correct" engineering is:

- In 2015 de Gouw, Rot, de Boer, Bubel and Hähnle, while trying to *formally verify* Java's Timsort with the KeY proof
  system, found that the merge rules as implemented did not always keep the run-length invariant, so on specially built
  inputs of huge length the fixed-size run stack could overflow. Their paper "OpenJDK's java.utils.Collection.sort() is
  broken: The good, the bad and the worst case" (CAV 2015) gave a corrected merge rule, which CPython adopted; Java's
maintainers enlarged the stack instead.
- In 2018 Munro and Wild proposed **powersort**, a merge policy that provably chooses merges within a small additive
  amount of the optimal cost for the given run lengths ("Nearly-Optimal Mergesorts", ESA 2018). CPython 3.11 replaced
  Timsort's original merge rules with powersort's; the run detection and galloping are unchanged.

## 5.8 Introsort and pattern-defeating quicksort

*Level: advanced.*

For sorting plain numbers (or anything where stability is not needed), the standard libraries of C++, Rust and Go use
quicksort variants hardened against its weak points. Here are the weak points and the defences.

**1. Bad pivots, by accident or by attack.** A fixed pivot rule (first item, last item, or the median of first, middle
and last, "median of three") can always be defeated by some input. Douglas McIlroy's paper "A Killer Adversary for
Quicksort" (1999) shows how to construct such an input *on the fly* against any quicksort that picks pivots
deterministically: the adversary decides the values of items only when they are first compared, always making the pivot
look small. This is not academic: a web service that sorts data sent by users can be slowed to a crawl. Random pivots
help, but libraries often avoid randomness (it makes results harder to reproduce and needs a generator).

**Introsort** (David Musser, "Introspective Sorting and Selection Algorithms", 1997) solves it with a guarantee instead
of luck: run quicksort, but count the recursion depth; if it exceeds $2\lfloor\log_2 n\rfloor$, the pivots have been
bad, so finish that part with heapsort. Then:

**Theorem.** Introsort makes $O(n\log n)$ comparisons in the worst case.

*Proof.* Cut the recursion tree at depth $2\lfloor\log_2 n\rfloor$. Above the cut, the parts at any one depth are
disjoint pieces of the array, so partitioning all of them at that depth costs $O(n)$; with $O(\log n)$ depths that is
$O(n\log n)$. At the cut, each remaining part of size $m_i$ is heapsorted in $O(m_i\log m_i)\le O(m_i\log n)$, and the
$m_i$ add up to at most $n$, giving $O(n\log n)$. $\square$

When pivots are good, which with median-of-three is nearly always, the heapsort fallback never triggers and introsort
runs at quicksort speed. The program above uses the worst possible pivot rule (first item) on a sorted list: plain
quicksort needs $1\,999\,000$ comparisons for 2000 items, introsort hits the depth limit, calls heapsort once on the
remaining part, and finishes in $78\,644$.

**2. Small parts.** Recursion has overhead. Below about 16 items, insertion sort is faster than quicksort (fewer
instructions per item, no calls, and the data is in cache). So introsort stops recursing on small parts and runs
insertion sort, either on each small part or once over the whole nearly sorted array at the end (each item is then
within 16 places of its final position, so there are at most $16n$ inversions and insertion sort is linear). The GNU
C++ library's `std::sort` is introsort with median-of-three pivots and a final insertion sort.

**3. Many equal keys.** With many duplicates, two-way partitions waste effort. **Three-way partitioning** (Dijkstra's
"Dutch national flag" problem) splits into $<x$, $=x$ and $>x$ and never recurses on the middle. Bentley and McIlroy's
"Engineering a Sort Function" (1993) gives an efficient version and is still the best short read on building a library
sort.

**4. Patterns.** Orson Peters's **pattern-defeating quicksort** (pdqsort; paper on arXiv, 2021) combines introsort with
ideas that make it adaptive on common patterns:

- If a partition did no swaps at all, the part may already be sorted; try a *bounded* insertion sort that gives up after
  a few moves. Sorted and nearly sorted inputs then finish in linear time.
- If a partition was very unbalanced, shuffle a few items around the boundaries to break the pattern before continuing
  (and count bad partitions; too many trigger heapsort, as in introsort).
- Partition with all items equal to the pivot of the *previous* level grouped together, so many equal keys cost linear
  time, like three-way partitioning.
- A **branchless** partition (BlockQuicksort, Edelkamp and Weiß, 2016) that first records, for a block of items, which
  ones belong on the wrong side, then swaps them, so the processor never mispredicts a branch on a comparison.

Go's `sort` package switched to pdqsort in Go 1.19 (2022), and Rust's `sort_unstable` was built on it. Java sorts arrays
of primitive numbers with Vladimir Yaroslavskiy's **dual-pivot quicksort** (from Java 7), which partitions around two
pivots into three parts. Wild and Nebel ("Average Case Analysis of Java 7's Dual Pivot Quicksort", ESA 2012) showed
that it makes about 5% fewer comparisons than classic quicksort but more swaps, so neither count alone explains why it
is faster; later work points to its reading memory fewer times.

**The lesson of 5.7 and 5.8.** None of these libraries invented a new idea that beats the lower bound. They combine the
simple pieces of this chapter, each where it is best: insertion sort for tiny parts, quicksort or merging for the bulk,
heapsort as insurance, and runs and galloping to exploit order that is already there. *Insideout*, you now know every
piece of them.

**In practice.** In Python call `sorted(xs)` or `xs.sort()`, with `key=` for records; it is stable, adaptive and well
tested, and the only reason to write your own sort is to learn, as here, or to exploit special structure in the keys
([Chapter 6](06-Sorting-in-Linear-Time-and-Selection.md)).

## Check yourself

??? question "1. Trace insertion sort on [3, 1, 2]. How many comparisons and shifts does it make, and how many inversions does the list have?"

    $i=1$: $x=1$ is compared with 3, which is bigger, so 3 shifts right; $j$ falls off the left end. List $[1,3,2]$:
    1 comparison, 1 shift. $i=2$: $x=2$ is compared with 3 (bigger, shift) and then with 1 (not bigger, stop). List
    $[1,2,3]$: 2 comparisons, 1 shift. Total 3 comparisons and 2 shifts. The inversions are $(3,1)$ and $(3,2)$: 2, equal
    to the number of shifts, as 5.2 proved.

??? question "2. Which of the seven sorts are stable? Give a three-item example that shows selection sort is not, and say how to make it stable."

    Stable: insertion, bubble, merge (with "take from the right only when strictly smaller"). Not stable: selection,
    both quicksorts, heapsort. Selection sort on $[2_a,2_b,1]$ swaps $2_a$ with $1$, giving $[1,2_b,2_a]$. To make it
    stable, instead of swapping the minimum into place, *remove* it and shift the items between one place right
    (like insertion sort's shift). That keeps the relative order of the others but costs $O(n)$ moves per pass instead
    of one swap.

??? question "3. Count the inversions of [3, 1, 4, 1, 5, 9, 2, 6]."

    Go through each item and count later items smaller than it: 3 has 1, 1, 2 (3); the first 1 has none; 4 has 1, 2
    (2); the second 1 has none; 5 has 2 (1); 9 has 2, 6 (2); 2 and 6 have none. Total $3+2+1+2=8$. (Equal items do not
    form an inversion, since the condition is strict: $a_i>a_j$.) Checked with `count_inversions`.

??? question "4. How many comparisons does merge sort make on an already sorted list of 8 items? Why is that the best case?"

    Each merge of two halves of length $m$ outputs the whole left half first (its items are all smaller), taking $m$
    comparisons, then copies the right half free. Four merges of $1+1$ cost 1 each, two merges of $2+2$ cost 2 each,
    one merge of $4+4$ costs 4: $4+4+4=12=\tfrac n2\log_2 n$. Our merge outputs one item per comparison and keeps
    comparing until one list is empty, so merging lists of lengths $p\le q$ costs it at least $p$ comparisons; the
    sorted input achieves exactly $p$ in every merge, so 12 is this merge sort's best case.

??? question "5. What does Lomuto quicksort do on a list of n equal items? And Hoare's?"

    Lomuto's test `a[j] < pivot` is false for every item, so $i$ never moves; the pivot is swapped to position $lo$ and
    the right part has $n-1$ items. Every level peels off one item: $(n-1)+(n-2)+\cdots=n(n-1)/2$ comparisons,
    quadratic, *even with random pivots*. Hoare's fingers both stop at every item (none is strictly less or greater
    than the pivot) and swap, meeting in the middle, so the split is even and the total is $O(n\log n)$. A three-way
    partition (5.8) makes it linear.

??? question "6. Prove that any comparison sort must make at least n - 1 comparisons, even on its best input."

    Draw a graph whose vertices are the $n$ items, with an edge for each pair compared. If the graph is not connected,
    split the items into two nonempty groups $A$ and $B$ with no comparison between them. Make two new inputs: one by
    adding a huge constant to every key in $B$ (all of $B$ now sorts after $A$), one by subtracting it (all of $B$ sorts
    before $A$). Inside each group the order is unchanged and no comparison crosses the groups, so every comparison
    gets the same answer on both inputs, and the algorithm outputs the same arrangement for both. Their correct sorted
    orders differ, so it is wrong on one of them. A connected graph
    on $n$ vertices has at least $n-1$ edges. So at least $n-1$ comparisons are needed, and insertion sort on a sorted
    list shows it is achievable.

??? question "7. For n = 5, compute the decision-tree lower bound and merge sort's worst case. Is there a gap?"

    $5!=120$ and $2^6=64<120\le128=2^7$, so $\lceil\log_2 120\rceil=7$. Merge sort's worst case:
    $W(5)=W(2)+W(3)+4=1+3+4=8$. The gap is 1. (A cleverer algorithm does sort 5 items with 7 comparisons, so for
    $n=5$ the bound is exact.)

??? question "8. Write a bottom-up merge sort: no recursion, merge runs of width 1, then 2, then 4, and so on."

    ```python
    def merge_sort_bottom_up(a):
        n, width = len(a), 1
        src, dst = list(a), [None] * len(a)
        while width < n:
            for lo in range(0, n, 2 * width):
                mid, hi = min(lo + width, n), min(lo + 2 * width, n)
                i, j, k = lo, mid, lo
                while i < mid and j < hi:
                    if src[j] < src[i]:
                        dst[k] = src[j]; j += 1
                    else:
                        dst[k] = src[i]; i += 1
                    k += 1
                dst[k:hi] = src[i:mid] + src[j:hi]
            src, dst = dst, src          # swap roles instead of copying back
            width *= 2
        return src

    assert merge_sort_bottom_up([5, 2, 4, 6, 1, 3]) == [1, 2, 3, 4, 5, 6]
    ```

    After the pass with width $w$, every block $src[k\cdot2w..(k+1)\cdot2w-1]$ is sorted (merge lemma); after
    $\lceil\log_2 n\rceil$ passes one block covers everything. Each pass costs $O(n)$, so the total is $O(n\log n)$, with
    no recursion stack at all.

??? question "9. Prove by induction that W(n) = n⌈log₂ n⌉ − 2^⌈log₂ n⌉ + 1 solves W(n) = W(⌊n/2⌋) + W(⌈n/2⌉) + n − 1, W(1) = 0."

    Write $f(x,c)=xc-2^c+1$. First a small observation: if $x=2^j$ then $f(x,j)=f(x,j+1)$ (both equal $xj-x+1$), so
    $W(x)=f(x,c)$ for *any* $c$ with $2^{c-1}\le x\le2^c$, not only for $c=\lceil\log_2 x\rceil$. Now let $n\ge2$,
    $k=\lceil\log_2 n\rceil$, so $2^{k-1}<n\le2^k$. The halves $\lfloor n/2\rfloor$ and $\lceil n/2\rceil$ both lie in
    $[2^{k-2},2^{k-1}]$ (because $n>2^{k-1}$ forces $\lfloor n/2\rfloor\ge2^{k-2}$, and $n\le2^k$ forces
    $\lceil n/2\rceil\le2^{k-1}$). By strong induction and the observation, with $c=k-1$ for both halves:
    $W(n)=\lfloor\tfrac n2\rfloor(k-1)+\lceil\tfrac n2\rceil(k-1)-2\cdot2^{k-1}+2+n-1=n(k-1)-2^k+n+1=nk-2^k+1$.
    The base case: $W(1)=1\cdot0-1+1=0$. $\square$ (The program's table, computed from the recurrence, agrees:
    $W(1000)=8977=10000-1024+1$.)

??? question "10. Use the decision-tree argument to show that merging two sorted lists of length n each needs at least about 2n comparisons in the worst case."

    The output is determined by which $n$ of the $2n$ output positions are taken by items of the first list: there
    are $\binom{2n}{n}$ possible outcomes, each needing its own leaf, so at least $\lceil\log_2\binom{2n}{n}\rceil$
    comparisons are needed. Since $\binom{2n}{n}\ge\frac{4^n}{2n+1}$ (it is the largest of the $2n+1$ terms that sum to
    $4^n$), this is at least $2n-\log_2(2n+1)$. For $n=8$: $\binom{16}{8}=12\,870$ and $\log_2 12\,870\approx13.65$, so 14
    are needed; the merge uses at most $2n-1=15$. A sharper argument (an adversary that keeps the two lists perfectly
    interleaved) shows $2n-1$ is exactly optimal.

??? question "11. Show that the expected comparisons of randomized quicksort for n = 4 are 29/6, both from the formula and by conditioning on the first pivot."

    Formula: $2\cdot5\cdot H_4-16$ with $H_4=\tfrac{25}{12}$: $\tfrac{250}{12}-16=\tfrac{58}{12}=\tfrac{29}{6}\approx4.83$.
    Conditioning: the first partition costs 3. With probability $\tfrac12$ the pivot is an end item, leaving a part of
    size 3 (expected $\tfrac83$ more); with probability $\tfrac12$ it is the second or third, leaving parts of sizes 1
    and 2 (1 more). $E=3+\tfrac12\cdot\tfrac83+\tfrac12\cdot1=3+\tfrac43+\tfrac12=\tfrac{29}{6}$. Both agree.

## What you learned

- Sorting is a permutation of the input into non-decreasing order; stability (ties keep their order) and working in
  place are the properties that decide which sort a library uses.
- Selection, insertion and bubble sort are $\Theta(n^2)$ in the worst case; insertion sort does exactly one shift per
  inversion, so it is linear on nearly sorted data and is used inside every fast sort.
- Merge sort is stable and $\Theta(n\log n)$ on every input, at the price of $\Theta(n)$ extra memory.
- Quicksort is in place with a tiny inner loop; random pivots give $2(n+1)H_n-4n\approx1.39\,n\log_2 n$ expected
  comparisons on every input, proved with indicator variables and linearity of expectation.
- Heapsort is in place and $O(n\log n)$ in the worst case, and serves as the safety net in introsort.
- Every comparison sort needs $\lceil\log_2 n!\rceil\approx n\log_2 n-1.44n$ comparisons in the worst case and on
  average, by counting the leaves of a decision tree.
- Timsort (runs, balanced merging, galloping), introsort (depth limit) and pdqsort (pattern breaking) combine the simple
  sorts to be fast on the inputs people really have.

**Next:** [Chapter 6](06-Sorting-in-Linear-Time-and-Selection.md) breaks the $n\log n$ barrier by looking inside the
keys, and finds the median in linear time.

## Further reading

- T. H. Cormen, C. E. Leiserson, R. L. Rivest and C. Stein, *Introduction to Algorithms*, 4th ed., 2022: chapters 2
  (insertion and merge sort), 6 (heapsort), 7 (quicksort) and 8.1 (the lower bound).
- D. E. Knuth, *The Art of Computer Programming*, Vol. 3: *Sorting and Searching*, 2nd ed., 1998: chapter 5, including
  minimum-comparison sorting (5.3.1).
- R. Sedgewick and K. Wayne, *Algorithms*, 4th ed., 2011: chapter 2.
- J. Kleinberg and É. Tardos, *Algorithm Design*, 2005: chapter 5 (merge sort, counting inversions) and 13.5
  (randomized quicksort).
- C. A. R. Hoare, "Quicksort", *The Computer Journal* 5(1), 1962.
- J. W. J. Williams, "Algorithm 232: Heapsort", *Communications of the ACM* 7(6), 1964; R. W. Floyd, "Algorithm 245:
  Treesort 3", *Communications of the ACM* 7(12), 1964.
- J. L. Bentley and M. D. McIlroy, "Engineering a Sort Function", *Software: Practice and Experience* 23(11), 1993.
- D. R. Musser, "Introspective Sorting and Selection Algorithms", *Software: Practice and Experience* 27(8), 1997.
- M. D. McIlroy, "A Killer Adversary for Quicksort", *Software: Practice and Experience* 29(4), 1999.
- T. Peters, `listsort.txt` in the CPython source (2002 onwards), the design notes of Timsort.
- S. de Gouw, J. Rot, F. S. de Boer, R. Bubel and R. Hähnle, "OpenJDK's java.utils.Collection.sort() is broken: The
  good, the bad and the worst case", CAV 2015.
- J. I. Munro and S. Wild, "Nearly-Optimal Mergesorts: Fast, Practical Sorting Methods That Optimally Adapt to Existing
  Runs", ESA 2018.
- O. R. L. Peters, "Pattern-defeating Quicksort", arXiv:2106.05123, 2021.
- V. Estivill-Castro and D. Wood, "A Survey of Adaptive Sorting Algorithms", *ACM Computing Surveys* 24(4), 1992.
- Reference pages on this site: [Selection sort](../../sorting/selection-sort.md),
  [Insertion sort](../../sorting/insertion-sort.md), [Bubble sort](../../sorting/bubble-sort.md),
  [Merge sort](../../sorting/merge-sort.md), [Quicksort](../../sorting/quicksort.md),
  [Heapsort](../../sorting/heapsort.md), [Binary heap](../../data-structures/binary-heap.md),
  [Big-O](../../foundations/big-o.md), [Recursion](../../foundations/recursion.md).
- The other books: [Machine learning](../machine-learning/index.md), where sorting by a learned score is everywhere,
  and the [math books](https://math.akadian.ca/books/) for induction, sums and probability.
