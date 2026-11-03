# 6. Sorting in linear time, and selection

*Chapter 5 ended with a wall: no algorithm that only compares items can sort $n$ of them in fewer than about
$n\log_2 n$ comparisons. In this chapter you will walk around the wall by doing something a comparison sort may not do:
look inside the keys and use them as addresses. You will build counting sort, radix sort and bucket sort and prove when
each one is linear. Then you will turn to a related question that needs much less than sorting: finding the median, or
the $k$-th smallest item, or the top ten. You will prove that a random pivot finds it in expected linear time, and that
a clever deterministic pivot, the median of medians, guarantees linear time even in the worst case.*

!!! abstract "In this chapter"
    **You will learn:**

    - why the $n\log n$ lower bound does not apply when keys are small integers, and what model of computation changes
    - counting sort, why it is stable, and why it costs $\Theta(n+k)$
    - LSD and MSD radix sort, why LSD needs a stable inner sort, and how to choose the digit size
    - bucket sort and its expected linear time on uniform data, proved with a variance calculation
    - the selection problem, quickselect, and a proof that its expected cost is below $4n$ comparisons
    - the median-of-medians algorithm (Blum, Floyd, Pratt, Rivest, Tarjan 1973) and its worst-case linear bound
    - top-$k$ and partial sorting with heaps, and what libraries offer

    **You need:** [Chapter 5](05-Sorting-by-Comparison.md) (quicksort's partition, the decision-tree lower bound, the
    randomized quicksort analysis), and solving recurrences from [Chapter 3](03-Recursion-and-Induction.md).

    **Levels:** 6.1 to 6.4 and 6.6 are intermediate; 6.5 is advanced.

## 6.1 Beating n log n by not comparing: counting sort

A teacher has 300 exam papers, each marked with a whole-number score from 0 to 100, and wants them in order of score.
Nobody would sort them by comparing pairs. You would lay out 101 piles labelled 0 to 100, drop each paper on its pile,
and pick the piles up in order. One look at each paper, then one look at each pile: about $300+101$ steps, not
$300\log_2 300\approx2500$.

Why does this not contradict the lower bound of [Chapter 5](05-Sorting-by-Comparison.md)? Because dropping a paper on
pile 73 is not a yes/no comparison. It uses the key *as an address*, a 101-way branch in one step. The decision-tree
argument counts binary questions; one memory access indexed by a key answers a question with $k$ possible answers,
worth $\log_2 k$ bits at once. The lower bound is a theorem about a **model of computation** (the comparison model), and
we are now in a different one: the **word RAM**, where keys are integers that fit in a machine word and can be used for
arithmetic and indexing ([Chapter 1](01-What-Is-an-Algorithm.md), 1.5).

### Counting sort

Piles of papers are lists, and lists cost memory management. **Counting sort** does the same thing with one array of
counters. The input is $n$ items whose keys are integers in $0..k-1$.

1. **Count.** `count[v]` = number of items with key $v$.
2. **Prefix sums.** Replace `count[v]` by the number of items with key *less than* $v$. That is exactly the position in
   the output where the first item with key $v$ must go.
3. **Place.** Go through the input from left to right; put each item at position `count[key]` and add 1 to that
   counter.

<figure class="mars-fig" markdown="0">
<svg viewBox="0 0 640 300" role="img" aria-label="Counting sort of 3 1 4 1 5 2 0 4 with keys from 0 to 5. Row 1 is the input. Row 2 is the count of each key: 1 2 1 1 2 1. Row 3 is the starting slot of each key, the prefix sums: 0 1 3 4 5 7. Row 4 is the output 0 1 1 2 3 4 4 5. The first input item 3, the first slot of key 3, which is 4, and output slot 4 are highlighted.">
  <g font-size="13" fill="currentColor" text-anchor="middle">
    <text x="70" y="45" text-anchor="end">input</text>
    <text x="70" y="125" text-anchor="end">count</text>
    <text x="70" y="185" text-anchor="end">first slot</text>
    <text x="70" y="265" text-anchor="end">output</text>
  </g>
  <g stroke="currentColor" font-size="14" fill="currentColor" text-anchor="middle">
    <rect x="90" y="25" width="50" height="30" fill="#eea66f" fill-opacity="0.55"/><text x="115" y="45" stroke="none">3</text>
    <rect x="140" y="25" width="50" height="30" fill="none"/><text x="165" y="45" stroke="none">1</text>
    <rect x="190" y="25" width="50" height="30" fill="none"/><text x="215" y="45" stroke="none">4</text>
    <rect x="240" y="25" width="50" height="30" fill="none"/><text x="265" y="45" stroke="none">1</text>
    <rect x="290" y="25" width="50" height="30" fill="none"/><text x="315" y="45" stroke="none">5</text>
    <rect x="340" y="25" width="50" height="30" fill="none"/><text x="365" y="45" stroke="none">2</text>
    <rect x="390" y="25" width="50" height="30" fill="none"/><text x="415" y="45" stroke="none">0</text>
    <rect x="440" y="25" width="50" height="30" fill="none"/><text x="465" y="45" stroke="none">4</text>
    <rect x="90" y="105" width="50" height="30" fill="#9cc9ea" fill-opacity="0.45"/><text x="115" y="125" stroke="none">1</text>
    <rect x="140" y="105" width="50" height="30" fill="#9cc9ea" fill-opacity="0.45"/><text x="165" y="125" stroke="none">2</text>
    <rect x="190" y="105" width="50" height="30" fill="#9cc9ea" fill-opacity="0.45"/><text x="215" y="125" stroke="none">1</text>
    <rect x="240" y="105" width="50" height="30" fill="#9cc9ea" fill-opacity="0.45"/><text x="265" y="125" stroke="none">1</text>
    <rect x="290" y="105" width="50" height="30" fill="#9cc9ea" fill-opacity="0.45"/><text x="315" y="125" stroke="none">2</text>
    <rect x="340" y="105" width="50" height="30" fill="#9cc9ea" fill-opacity="0.45"/><text x="365" y="125" stroke="none">1</text>
    <rect x="90" y="165" width="50" height="30" fill="#9cc9ea" fill-opacity="0.45"/><text x="115" y="185" stroke="none">0</text>
    <rect x="140" y="165" width="50" height="30" fill="#9cc9ea" fill-opacity="0.45"/><text x="165" y="185" stroke="none">1</text>
    <rect x="190" y="165" width="50" height="30" fill="#9cc9ea" fill-opacity="0.45"/><text x="215" y="185" stroke="none">3</text>
    <rect x="240" y="165" width="50" height="30" fill="#eea66f" fill-opacity="0.55"/><text x="265" y="185" stroke="none">4</text>
    <rect x="290" y="165" width="50" height="30" fill="#9cc9ea" fill-opacity="0.45"/><text x="315" y="185" stroke="none">5</text>
    <rect x="340" y="165" width="50" height="30" fill="#9cc9ea" fill-opacity="0.45"/><text x="365" y="185" stroke="none">7</text>
    <rect x="90" y="245" width="50" height="30" fill="#7ccf9a" fill-opacity="0.45"/><text x="115" y="265" stroke="none">0</text>
    <rect x="140" y="245" width="50" height="30" fill="#7ccf9a" fill-opacity="0.45"/><text x="165" y="265" stroke="none">1</text>
    <rect x="190" y="245" width="50" height="30" fill="#7ccf9a" fill-opacity="0.45"/><text x="215" y="265" stroke="none">1</text>
    <rect x="240" y="245" width="50" height="30" fill="#7ccf9a" fill-opacity="0.45"/><text x="265" y="265" stroke="none">2</text>
    <rect x="290" y="245" width="50" height="30" fill="#eea66f" fill-opacity="0.55"/><text x="315" y="265" stroke="none">3</text>
    <rect x="340" y="245" width="50" height="30" fill="#7ccf9a" fill-opacity="0.45"/><text x="365" y="265" stroke="none">4</text>
    <rect x="390" y="245" width="50" height="30" fill="#7ccf9a" fill-opacity="0.45"/><text x="415" y="265" stroke="none">4</text>
    <rect x="440" y="245" width="50" height="30" fill="#7ccf9a" fill-opacity="0.45"/><text x="465" y="265" stroke="none">5</text>
  </g>
  <g font-size="11" fill="currentColor" text-anchor="middle">
    <text x="115" y="98">key 0</text><text x="165" y="98">1</text><text x="215" y="98">2</text>
    <text x="265" y="98">3</text><text x="315" y="98">4</text><text x="365" y="98">5</text>
    <text x="115" y="290">slot 0</text><text x="165" y="290">1</text><text x="215" y="290">2</text><text x="265" y="290">3</text>
    <text x="315" y="290">4</text><text x="365" y="290">5</text><text x="415" y="290">6</text><text x="465" y="290">7</text>
  </g>
  <g font-size="12" fill="currentColor">
    <text x="520" y="120">1. count keys</text>
    <text x="520" y="180">2. prefix sums</text>
    <text x="520" y="260">3. place items</text>
    <text x="520" y="45">first item: key 3</text>
  </g>
</svg>
<figcaption>Figure 6.1. Counting sort with keys 0 to 5. The prefix sum for key 3 is 1 + 2 + 1 = 4, the number of items with keys 0, 1 or 2, so the first item with key 3 (orange) goes to output slot 4.</figcaption>
</figure>

Trace for $[3,1,4,1,5,2,0,4]$, $k=6$. Counts by key $0..5$: $1,2,1,1,2,1$. Prefix sums (the first slot of each key):
$0,1,3,4,5,7$. Placing left to right:

| item | key's slot before | output so far (slots 0 to 7) |
|---|---|---|
| 3 | 4 | . . . . 3 . . . |
| 1 | 1 | . 1 . . 3 . . . |
| 4 | 5 | . 1 . . 3 4 . . |
| 1 | 2 | . 1 1 . 3 4 . . |
| 5 | 7 | . 1 1 . 3 4 . 5 |
| 2 | 3 | . 1 1 2 3 4 . 5 |
| 0 | 0 | 0 1 1 2 3 4 . 5 |
| 4 | 6 | 0 1 1 2 3 4 4 5 |

**Theorem.** Counting sort outputs the items sorted by key, stably, in $\Theta(n+k)$ time and $\Theta(n+k)$ extra space.

*Proof.* After step 2, `count[v]` $=\#\{\text{items with key}<v\}$. In a sorted output those items fill slots
$0..\text{count}[v]-1$, and the $c_v$ items with key $v$ fill the next $c_v$ slots, ending just before `count[v+1]`.
Step 3 places the items with key $v$ in exactly those slots, one after another, in the order they appear in the input.
So every item lands in a slot reserved for its key (sorted), the slots of each key are filled in input order (stable),
and no slot is used twice (each counter only moves forward through its own range). Steps 1 and 3 each touch each
item once, $\Theta(n)$; step 2 touches each counter once, $\Theta(k)$; the arrays have sizes $n$ and $k$. $\square$

When $k=O(n)$, counting sort is linear. When $k$ is huge (keys are arbitrary 64-bit numbers, $k=2^{64}$) it is
useless: the counter array alone would be larger than any memory. Radix sort fixes that.

**Stability is the point.** Counting sort sorts *records* by an integer key, not just numbers. The program's check sorts
`(5,"a"), (2,"b"), (5,"c"), (1,"d"), (2,"e")` by the number and gets `(1,d) (2,b) (2,e) (5,a) (5,c)`: within each key the
letters keep their input order. Radix sort depends on exactly this. (CLRS places items from right to left, decrementing
the counters; it is equally stable. What breaks stability is mixing the two, filling slots from the left while reading
the input from the right.)

**History.** CLRS credits counting sort, and the idea of using it inside radix sort, to Harold Seward's 1954 MIT
master's thesis. See the reference page [Counting sort](../../sorting/counting-sort.md).

## 6.2 Radix sort, LSD and MSD

Keys up to a million do not fit counting sort comfortably, but each one is only six decimal digits. **Radix sort** sorts
by one digit at a time, with counting sort on that digit ($k=10$ piles).

The surprising part is the order: **least significant digit first** (LSD). Sort by the units digit, then by the tens
digit, then by the hundreds digit, using a *stable* sort each time.

Trace on $[523,81,345,9,812,47,316,280]$ (from the program below; 81 is 081 and 9 is 009):

| pass | sorted by | list after the pass |
|---|---|---|
| 1 | units | 280, 081, 812, 523, 345, 316, 047, 009 |
| 2 | tens | 009, 812, 316, 523, 345, 047, 280, 081 |
| 3 | hundreds | 009, 047, 081, 280, 316, 345, 523, 812 |

Look at pass 2: 812 and 316 both have tens digit 1. Pass 2 leaves them in the order pass 1 put them (812 before 316,
because units 2 < 6). That is right for their last two digits, 12 < 16. Pass 3 then separates them by the hundreds
digit, and once again keeps ties (009, 047, 081 all have hundreds digit 0) in the order of their last two digits.

**Theorem.** If each pass is a stable sort on one digit, then after pass $i$ the list is sorted by the number formed by
the last $i$ digits. So after $d$ passes it is sorted.

*Proof by induction on $i$.* After pass 1 the list is sorted by the last digit. Suppose after pass $i-1$ it is sorted
by the last $i-1$ digits, and take two keys $x,y$ after pass $i$. If their $i$-th digits (from the right) differ, pass
$i$ put them in the order of that digit, which decides the order of their last $i$ digits. If the $i$-th digits are
equal, the order of their last $i$ digits is the order of their last $i-1$ digits; pass $i$ is stable, so it kept them
in the order they had after pass $i-1$, which by induction was that order. $\square$

Remove stability and the proof breaks, and so does the algorithm: the program reads each digit's pile backwards (still
correctly sorted by that digit, but unstable) and ends with `[81, 47, 9, 280, 345, 316, 523, 812]`, which is wrong (both
because 81, 47, 9 and because 345, 316 are reversed).

**Why not most significant digit first, the way you would sort by hand?** With a stable sort, processing the most
significant digit first and the units digit last would let the *last* pass, units, decide the order; $[21,12]$ would end
as $[21,12]$. Most significant first works only if, after sorting by the first digit, each pile is sorted separately,
which is MSD radix sort below.

### Running time and choosing the digit size

With $d$ digits in base $k$, radix sort does $d$ counting sorts: $\Theta(d(n+k))$.

For a machine, the natural "digit" is a group of $r$ bits. A $b$-bit key has $d=\lceil b/r\rceil$ digits in base
$2^r$, so the time is

$$\Theta\Big(\frac br\,(n+2^r)\Big).$$

Making $r$ bigger means fewer passes but more counters. The balance is $2^r\approx n$, that is $r\approx\log_2 n$:
then each pass is $\Theta(n)$ and there are $b/\log_2 n$ passes, for a total of $\Theta(bn/\log n)$.
(Choosing $r$ larger than $\log_2 n$ makes $2^r$ dominate; smaller makes the number of passes grow; CLRS Lemma 8.4 makes
this precise.) So:

- for 32-bit keys and $n=10^6$, $r=16$ gives 2 passes with 65 536 counters each (Exercise 3);
- if the keys are integers below $n^c$ for a constant $c$, then $b=c\log_2 n$ and radix sort is $\Theta(cn)$: **linear**.

Is radix sort then always faster than quicksort? Not in practice. Each pass reads and writes the whole array, and the
writes scatter to $2^r$ different places, which is hard on caches; quicksort works in place on a shrinking part. For
very large arrays of small fixed-size keys (32- or 64-bit integers, floats with a bit trick), well-tuned radix sorts do
win, and graphics processors sort this way. For strings, records and anything with a custom comparison, comparison
sorts are the default. See [Radix sort](../../sorting/radix-sort.md).

### MSD radix sort for strings

Strings have different lengths, and most of the characters of a long string never matter: "ma" and "orbit" are ordered
by their first letters alone. **MSD radix sort** (most significant digit first) splits the items into buckets by their
first character, then sorts each bucket *separately and recursively* by the second character, and so on. Strings that
have ended go before all longer ones in their bucket (the empty suffix is smallest).

```python
def radix_sort_msd(words, pos=0):
    if len(words) <= 1: return list(words)
    done = [w for w in words if len(w) == pos]          # words that have ended come first
    buckets = {}
    for w in words:
        if len(w) > pos: buckets.setdefault(w[pos], []).append(w)
    out = done
    for ch in sorted(buckets): out += radix_sort_msd(buckets[ch], pos + 1)
    return out
```

On `mars moon map mast a orbit rover rock ma ore` the first pass makes buckets `a`, `m`, `o`, `r`; the `m` bucket is
split by its second letter into `a` (`mars map mast ma`) and `o` (`moon`); then `ma` ends, and `map`, `mars`, `mast`
are split by their third letter. The result is `a ma map mars mast moon orbit ore rock rover`.

MSD radix sort examines only the **distinguishing prefix** of each string (the characters needed to tell it from all the
others), so on long keys that differ early it reads far less than the total input. Its weakness is many tiny buckets:
creating 256 buckets to split three strings is waste. Real implementations switch to insertion sort for small buckets,
and McIlroy, Bostic and McIlroy's "Engineering Radix Sort" (1993) shows how to do the bucketing in place (the
"American flag sort"). Bentley and Sedgewick's **three-way radix quicksort** ("Fast Algorithms for Sorting and Searching
Strings", 1997) partitions on one character at a time into less, equal and greater, and recurses on the next character
only in the "equal" part; it is a natural blend of quicksort and MSD radix sort.

**History.** Punched-card sorting machines, which dropped each card into one of ten pockets according to the hole in a
chosen column, were used for sorting by one column per pass, and operators sorted multi-column keys starting from the
least significant column: LSD radix sort, done by machine and by hand long before electronic computers. Knuth's
*TAOCP*, volume 3, section 5.2.5, describes the method and its history.

## 6.3 Bucket sort

Counting sort needs integer keys. Suppose instead the keys are real numbers spread **uniformly** over $[0,1)$: random
measurements, or hash values. **Bucket sort** divides $[0,1)$ into $n$ equal intervals ("buckets"), drops each item
into the bucket $\lfloor n x\rfloor$, sorts each bucket with insertion sort, and concatenates the buckets in order.

<figure class="mars-fig" markdown="0">
<svg viewBox="0 0 640 230" role="img" aria-label="Bucket sort of ten numbers into ten buckets. Input: 0.42 0.07 0.91 0.48 0.15 0.63 0.44 0.86 0.30 0.19. Bucket 0 holds 0.07; bucket 1 holds 0.15 and 0.19; bucket 2 is empty; bucket 3 holds 0.30; bucket 4 holds 0.42, 0.44 and 0.48 after insertion sort; buckets 5 and 7 are empty; bucket 6 holds 0.63; bucket 8 holds 0.86; bucket 9 holds 0.91.">
  <g font-size="13" fill="currentColor" text-anchor="middle" stroke="currentColor">
    <rect x="20" y="15" width="56" height="28" fill="none"/><text x="48" y="34" stroke="none">.42</text>
    <rect x="80" y="15" width="56" height="28" fill="none"/><text x="108" y="34" stroke="none">.07</text>
    <rect x="140" y="15" width="56" height="28" fill="none"/><text x="168" y="34" stroke="none">.91</text>
    <rect x="200" y="15" width="56" height="28" fill="none"/><text x="228" y="34" stroke="none">.48</text>
    <rect x="260" y="15" width="56" height="28" fill="none"/><text x="288" y="34" stroke="none">.15</text>
    <rect x="320" y="15" width="56" height="28" fill="none"/><text x="348" y="34" stroke="none">.63</text>
    <rect x="380" y="15" width="56" height="28" fill="none"/><text x="408" y="34" stroke="none">.44</text>
    <rect x="440" y="15" width="56" height="28" fill="none"/><text x="468" y="34" stroke="none">.86</text>
    <rect x="500" y="15" width="56" height="28" fill="none"/><text x="528" y="34" stroke="none">.30</text>
    <rect x="560" y="15" width="56" height="28" fill="none"/><text x="588" y="34" stroke="none">.19</text>
  </g>
  <g font-size="12" fill="currentColor" text-anchor="middle">
    <text x="48" y="92">0</text><text x="108" y="92">1</text><text x="168" y="92">2</text><text x="228" y="92">3</text>
    <text x="288" y="92">4</text><text x="348" y="92">5</text><text x="408" y="92">6</text><text x="468" y="92">7</text>
    <text x="528" y="92">8</text><text x="588" y="92">9</text>
    <text x="320" y="70">bucket = floor(10 x)</text>
  </g>
  <g stroke="currentColor" fill="none" stroke-width="1">
    <line x1="22" y1="98" x2="618" y2="98"/>
  </g>
  <g font-size="13" fill="currentColor" text-anchor="middle" stroke="currentColor">
    <rect x="20" y="104" width="56" height="28" fill="#9cc9ea" fill-opacity="0.5"/><text x="48" y="123" stroke="none">.07</text>
    <rect x="80" y="104" width="56" height="28" fill="#9cc9ea" fill-opacity="0.5"/><text x="108" y="123" stroke="none">.15</text>
    <rect x="80" y="134" width="56" height="28" fill="#9cc9ea" fill-opacity="0.5"/><text x="108" y="153" stroke="none">.19</text>
    <rect x="200" y="104" width="56" height="28" fill="#9cc9ea" fill-opacity="0.5"/><text x="228" y="123" stroke="none">.30</text>
    <rect x="260" y="104" width="56" height="28" fill="#eea66f" fill-opacity="0.5"/><text x="288" y="123" stroke="none">.42</text>
    <rect x="260" y="134" width="56" height="28" fill="#eea66f" fill-opacity="0.5"/><text x="288" y="153" stroke="none">.44</text>
    <rect x="260" y="164" width="56" height="28" fill="#eea66f" fill-opacity="0.5"/><text x="288" y="183" stroke="none">.48</text>
    <rect x="380" y="104" width="56" height="28" fill="#9cc9ea" fill-opacity="0.5"/><text x="408" y="123" stroke="none">.63</text>
    <rect x="500" y="104" width="56" height="28" fill="#9cc9ea" fill-opacity="0.5"/><text x="528" y="123" stroke="none">.86</text>
    <rect x="560" y="104" width="56" height="28" fill="#9cc9ea" fill-opacity="0.5"/><text x="588" y="123" stroke="none">.91</text>
  </g>
  <text x="320" y="218" font-size="12" fill="currentColor" text-anchor="middle">read the buckets left to right, each sorted: .07 .15 .19 .30 .42 .44 .48 .63 .86 .91</text>
</svg>
<figcaption>Figure 6.2. Bucket sort with n = 10 buckets. Most buckets get zero, one or two items; the busiest one here (bucket 4) has three, sorted by insertion sort.</figcaption>
</figure>

**Correctness.** If $x<y$ then $\lfloor nx\rfloor\le\lfloor ny\rfloor$, so $x$'s bucket is the same as $y$'s or to the
left of it. Items in different buckets come out in the right order because the buckets are read left to right; items
in the same bucket, because the bucket is sorted. $\square$

**Expected time.** Everything except the insertion sorts is $\Theta(n)$. Insertion sort on a bucket of $n_i$ items costs
$O(n_i^2)$ (at most $n_i(n_i-1)/2$ shifts, plus $n_i$), so the time is $\Theta(n)+O\big(\sum_i n_i^2\big)$. If buckets
were all size 1 that sum would be $n$; but with random data some buckets get two or three and some none. How large is the
sum on average?

**Theorem.** If the $n$ keys are independent and uniform on $[0,1)$, then $E\big[\sum_i n_i^2\big]=2n-1$, so bucket sort
runs in expected $\Theta(n)$ time.

*Proof.* Fix a bucket $i$. Each key falls into it independently with probability $p=1/n$, so $n_i$ counts successes in
$n$ independent trials: it is a **binomial** random variable with $E[n_i]=np=1$ and variance
$\mathrm{Var}[n_i]=np(1-p)=1-\tfrac1n$. Since $\mathrm{Var}[X]=E[X^2]-E[X]^2$,

$$E[n_i^2]=\mathrm{Var}[n_i]+E[n_i]^2=\Big(1-\frac1n\Big)+1=2-\frac1n.$$

Summing over the $n$ buckets with linearity of expectation, $E\big[\sum_i n_i^2\big]=n\big(2-\tfrac1n\big)=2n-1$. $\square$

(If you prefer to avoid variance: write $n_i=\sum_j X_j$ where $X_j=1$ if key $j$ falls in bucket $i$. Then
$n_i^2=\sum_j X_j^2+\sum_{j\ne l}X_jX_l$, whose expectation is $n\cdot\tfrac1n+n(n-1)\cdot\tfrac1{n^2}=2-\tfrac1n$, using
independence for $E[X_jX_l]=\tfrac1{n^2}$.)

The program checks this: over 200 trials the average of $\sum n_i^2$ is 18.9 for $n=10$, 198.2 for $n=100$, 1994.2 for
$n=1000$ and 20 001.6 for $n=10\,000$, each within a fraction of a percent of $2n-1$.

**The catch.** The theorem assumes uniform data. Put all 1000 keys below 0.001 and they all land in bucket 0: the
program reports $\sum n_i^2=1\,000\,000=n^2$, and insertion sort is quadratic. Two remedies: sort each bucket with an
$O(m\log m)$ sort, which caps the worst case at $O(n\log n)$; or, if you know the distribution has a cumulative
distribution function $F$, bucket by $\lfloor nF(x)\rfloor$, which makes any continuous distribution uniform. Bucket sort
is the right idea when the data really is spread out, and also the base of **sample sort** in parallel and distributed
sorting: pick bucket boundaries from a random sample of the data so the buckets come out balanced
([Chapter 24](24-Algorithms-for-Big-Data-and-Many-Processors.md)).

The whole program:

```python
--8<-- "books/algorithms/ch06_linear_sorts.py"
```

Output:

```
counting sort of [3, 1, 4, 1, 5, 2, 0, 4] -> [0, 1, 1, 2, 3, 4, 4, 5]
stable: [(1, 'd'), (2, 'b'), (2, 'e'), (5, 'a'), (5, 'c')]

LSD radix sort of [523, 81, 345, 9, 812, 47, 316, 280]
  by digit   1: [280, 81, 812, 523, 345, 316, 47, 9]
  by digit  10: [9, 812, 316, 523, 345, 47, 280, 81]
  by digit 100: [9, 47, 81, 280, 316, 345, 523, 812]
  with an unstable digit sort: [81, 47, 9, 280, 345, 316, 523, 812]

MSD radix sort: ['a', 'ma', 'map', 'mars', 'mast', 'moon', 'orbit', 'ore', 'rock', 'rover']

bucket sort, uniform data: average of sum(bucket size^2) over 200 trials
  n =    10:      18.9   (2n - 1 = 19)
  n =   100:     198.2   (2n - 1 = 199)
  n =  1000:    1994.2   (2n - 1 = 1999)
  n = 10000:   20001.6   (2n - 1 = 19999)
  n = 1000, all values below 0.001: 1000000
```

*Level: advanced, an aside.* How fast can integers be sorted on a word RAM in the worst case? Radix sort is linear for
keys below $n^c$, but for full 64-bit keys and modest $n$ the answer is subtle. Fredman and Willard's **fusion trees**
(1993) first broke $O(n\log n)$ for arbitrary word-size integers; Han and Thorup (2002) sort in
$O(n\sqrt{\log\log n})$ expected time and linear space. Whether integers can be sorted in $O(n)$ time in general is an
open problem.

## 6.4 Selection: the k-th smallest

Often we do not need everything in order, only one position of the order:

- the **median** of a set of measurements (the middle value, which unlike the mean is not dragged by a few wild
  outliers, such as a faulty sensor reading on a rover);
- the **minimum** or **maximum**;
- the 90th **percentile** of response times;
- the $k$-th best score.

The **selection problem**: given $n$ items and a rank $k$ (here counted from 0), find the item that would be at position
$k$ if the list were sorted. Its rank-$k$ item is the **$k$-th order statistic**.

Sorting solves it in $O(n\log n)$. But the minimum takes only $n-1$ comparisons (scan, keeping the smallest so far), and
that is optimal: each of the $n-1$ items that are not the minimum must lose at least one comparison, or we could not
rule it out, and each comparison has only one loser. Is the median closer to the minimum or to sorting? It turns out
to be linear too, and the proof is two of the nicest ideas in the subject.

### Quickselect

Partition around a pivot exactly as in quicksort. Now the pivot's rank is known: if $p$ items are smaller, the pivot is
the $p$-th smallest. If $k=p$ we are done. If $k<p$, the answer is in the left part; if $k>p$, it is in the right part,
with rank $k-p-1$ there. **Recurse on one side only.** Hoare published this as Algorithm 65, "Find", in 1961, next to
quicksort.

Our program uses a **three-way partition** into less, equal and greater, which handles duplicates cleanly:

```python
def quickselect(a, k, rng):
    while True:
        if len(a) == 1: return a[0]
        pivot = a[rng.randrange(len(a))]
        lo, eq, hi = partition3(a, pivot)
        if k < len(lo):            a = lo
        elif k < len(lo) + len(eq): return pivot
        else:                      k -= len(lo) + len(eq); a = hi
```

Trace: find rank 3 (the fourth smallest) of $[7,2,9,4,3,8,6,5]$, with pivots $6$, $3$, $4$:

| round | list | pivot | less / equal / greater | $k$ | goes to |
|---|---|---|---|---|---|
| 1 | 7 2 9 4 3 8 6 5 | 6 | [2 4 3 5] [6] [7 9 8] | 3 | less (3 < 4) |
| 2 | 2 4 3 5 | 3 | [2] [3] [4 5] | 3 | greater, $k=3-2=1$ |
| 3 | 4 5 | 4 | [] [4] [5] | 1 | greater, $k=0$ |
| 4 | 5 | | | 0 | answer 5 |

That cost $7+3+1=11$ comparisons; sorting the list would need at least $\lceil\log_2 8!\rceil=16$.

**Correctness.** Invariant: the answer (the rank-$k$ item of the original list) is the rank-$k$ item of the current
list. It holds at the start. If $k$ is less than the number of smaller items, the rank-$k$ item is one of them and keeps
rank $k$ among them; if $k$ falls among the equal items, the answer is the pivot; otherwise it is in the greater part,
and the $|lo|+|eq|$ items removed are all smaller than it, so its rank drops by that much. The list shrinks every round
(the pivot is removed), so the loop ends. $\square$

**Worst case.** As with quicksort, terrible pivots (always the largest, when we want the smallest) peel off one item per
round: $(n-1)+(n-2)+\cdots=\Theta(n^2)$.

**Expected cost.** With random pivots, each round throws away a random-sized chunk, and on average a large one.

**Theorem.** For $n$ distinct items and any rank $k$, randomized quickselect makes fewer than $4n$ comparisons in
expectation.

*Proof.* Use the same idea as for quicksort in [Chapter 5](05-Sorting-by-Comparison.md), 5.4. Call the items
$z_1<\cdots<z_n$ in sorted order, and let the target be $z_k$ (now counting from 1). Two items $z_i,z_j$ ($i<j$) are
compared at most once, and only if one of them is a pivot while both are still in the current list.

When are $z_i$ and $z_j$ compared? Consider the block of all items between $\min(i,k)$ and $\max(j,k)$ in sorted order:
it contains $z_i$, $z_j$ and the target. As long as no pivot has been chosen from this block, the whole block stays in
the current list (a pivot outside the block is smaller or larger than all of it, and the target, being in the block,
is on the same side as all of it). The first pivot chosen from the block decides: if it is $z_i$ or $z_j$, they are
compared; if it is anything else in the block, then either it separates $z_i$ from $z_j$, or it separates them both from
the target and they are thrown away together, or it is the target and the algorithm stops. The first pivot from the block
is uniform over the block, so

$$P(z_i,z_j\text{ compared})=\frac{2}{\max(j,k)-\min(i,k)+1}.$$

Summing over pairs, split into three kinds:

1. *Both at or above the target*, $k\le i<j$: the probability is $\frac2{j-k+1}$. For a fixed $j$ there are $j-k$ such
   $i$, contributing $\frac{2(j-k)}{j-k+1}<2$. Summing over $j=k+1..n$ gives less than $2(n-k)$.
2. *Both at or below*, $i<j\le k$: by the same count, less than $2(k-1)$.
3. *On opposite sides*, $i<k<j$: the probability is $\frac2{j-i+1}$. For a gap $d=j-i$, at most $d-1$ such pairs straddle
   $k$, contributing at most $\frac{2(d-1)}{d+1}<2$; with $d$ from 2 to $n-1$ that is less than $2(n-2)$.

The total is less than $2(n-k)+2(k-1)+2(n-2)<4n$. $\square$

The exact value is known. Knuth (*TAOCP* volume 3, 5.3.3) gives the expected number of comparisons for rank $k$ (from 1)
as

$$2\big[(n+1)H_n-(n+3-k)H_{n+1-k}-(k+2)H_k+n+3\big],$$

which for the median is about $2(1+\ln2)\,n\approx3.39\,n$, and for the minimum about $2n$. The second program computes
the exact expectation from the recurrence "partition cost plus the average over the $n$ pivot ranks", with exact
fractions, and checks that it equals this formula for every $n\le12$ and every $k$; for example $\tfrac83$ for the median
of 3 (Exercise 6) and $\tfrac{23}6$ for the minimum of 4. On random lists of 1000 to 100 000 items it measures about 3.5
comparisons per item when finding the median.

Compare with the $\approx1.39\,n\log_2 n$ of quicksort: by recursing on one side only, the total work becomes a
shrinking geometric series instead of $\log n$ full levels.

## 6.5 Median of medians: worst-case linear selection

*Level: advanced.*

Random pivots make bad luck unlikely, but not impossible. Can a *deterministic* algorithm find the median in $O(n)$
time on every input? In 1973 Manuel Blum, Robert Floyd, Vaughan Pratt, Ronald Rivest and Robert Tarjan showed that it
can ("Time Bounds for Selection", *Journal of Computer and System Sciences*). The idea is to spend a little work
finding a pivot that is *guaranteed* to be near the middle.

**SELECT$(a,k)$:**

1. Divide the $n$ items into groups of 5 (the last group may be smaller).
2. Find the median of each group by brute force (sorting 5 items takes at most 7 comparisons; insertion sort, as in our
   code, at most 10).
3. **Recursively** call SELECT on the $\lceil n/5\rceil$ group medians to find *their* median, $x$.
4. Partition the items around $x$ into less, equal and greater.
5. If $k$ falls in the equal part, return $x$; otherwise recurse into the less or greater part, as in quickselect.

### Why the pivot is good

<figure class="mars-fig" markdown="0">
<svg viewBox="0 0 680 300" role="img" aria-label="Thirty-five items drawn as seven columns of five circles. Each column is a group of five sorted from small at the top to large at the bottom, so its median is in the middle row. The columns are drawn in order of their medians from left to right. The median of medians x is the middle circle of the middle column. The top-left block of circles, columns one to four and rows one to three, is shaded blue: all are at most x. The bottom-right block, columns four to seven and rows three to five, is shaded orange: all are at least x.">
  <rect x="35" y="20" width="250" height="130" rx="10" fill="#9cc9ea" fill-opacity="0.35" stroke="none"/>
  <rect x="245" y="110" width="250" height="130" rx="10" fill="#eea66f" fill-opacity="0.35" stroke="none"/>
  <g stroke="currentColor" stroke-width="1.2" fill="none">
    <circle cx="60" cy="40" r="11"/><circle cx="60" cy="85" r="11"/><circle cx="60" cy="130" r="11"/><circle cx="60" cy="175" r="11"/><circle cx="60" cy="220" r="11"/>
    <circle cx="130" cy="40" r="11"/><circle cx="130" cy="85" r="11"/><circle cx="130" cy="130" r="11"/><circle cx="130" cy="175" r="11"/><circle cx="130" cy="220" r="11"/>
    <circle cx="200" cy="40" r="11"/><circle cx="200" cy="85" r="11"/><circle cx="200" cy="130" r="11"/><circle cx="200" cy="175" r="11"/><circle cx="200" cy="220" r="11"/>
    <circle cx="270" cy="40" r="11"/><circle cx="270" cy="85" r="11"/><circle cx="270" cy="175" r="11"/><circle cx="270" cy="220" r="11"/>
    <circle cx="340" cy="40" r="11"/><circle cx="340" cy="85" r="11"/><circle cx="340" cy="130" r="11"/><circle cx="340" cy="175" r="11"/><circle cx="340" cy="220" r="11"/>
    <circle cx="410" cy="40" r="11"/><circle cx="410" cy="85" r="11"/><circle cx="410" cy="130" r="11"/><circle cx="410" cy="175" r="11"/><circle cx="410" cy="220" r="11"/>
    <circle cx="480" cy="40" r="11"/><circle cx="480" cy="85" r="11"/><circle cx="480" cy="130" r="11"/><circle cx="480" cy="175" r="11"/><circle cx="480" cy="220" r="11"/>
  </g>
  <circle cx="270" cy="130" r="13" fill="#7ccf9a" stroke="currentColor" stroke-width="1.5"/>
  <text x="270" y="135" font-size="13" text-anchor="middle" fill="currentColor">x</text>
  <g stroke="currentColor" stroke-width="1" stroke-dasharray="3 3">
    <line x1="60" y1="130" x2="480" y2="130" stroke-opacity="0.6"/>
  </g>
  <g font-size="12" fill="currentColor">
    <text x="515" y="44">small</text>
    <text x="515" y="134">group medians</text>
    <text x="515" y="224">large</text>
    <text x="515" y="64">each column:</text>
    <text x="515" y="80">5 items, sorted</text>
    <text x="270" y="265" text-anchor="middle">columns in order of their medians</text>
    <text x="270" y="285" text-anchor="middle">blue: all at most x        orange: all at least x</text>
  </g>
</svg>
<figcaption>Figure 6.3. Why the median of medians x is a good pivot. Imagine each group of 5 sorted and the groups ordered by their medians (the algorithm never actually does this; it is a way to see the proof). Everything in the orange block is at least x, about 3/10 of all items; by symmetry so is everything in the blue block at most x.</figcaption>
</figure>

**Lemma.** With $g=\lceil n/5\rceil$ groups, at least $\frac{3n}{10}-6$ items are $\ge x$, and at least $\frac{3n}{10}-6$
are $\le x$. So after partitioning around $x$, the less part and the greater part each have at most $\frac{7n}{10}+6$
items.

*Proof.* $x$ is the median of the $g$ group medians, so at least $\lceil g/2\rceil$ of the group medians are $\ge x$
(including $x$'s own). In each of those groups, the median and the two items above it in that group are $\ge$ the
median $\ge x$: three items per group. To keep the count simple, do not count two of these groups: the last group
(which may have fewer than 5 items) and $x$'s own group. So the number of items $\ge x$ is at least

$$3\Big(\Big\lceil\frac g2\Big\rceil-2\Big)\ge3\Big(\frac n{10}-2\Big)=\frac{3n}{10}-6.$$

The same argument with "$\le$" gives the other half. The less part contains no item $\ge x$, so it has at most
$n-(\tfrac{3n}{10}-6)=\tfrac{7n}{10}+6$ items, and likewise the greater part. $\square$

### The linear bound

**Theorem.** SELECT runs in $O(n)$ time in the worst case.

*Proof.* Let $T(n)$ be the worst-case time on $n$ items. Steps 1, 2 and 4 take at most $an$ time for some constant $a$
(constant work per group of 5, and one pass to partition). Step 3 is a recursive call on $\lceil n/5\rceil$ items. Step
5 recurses on at most $\tfrac{7n}{10}+6$ items, by the lemma. So for $n$ above some threshold,

$$T(n)\le T\big(\lceil n/5\rceil\big)+T\big(\tfrac{7n}{10}+6\big)+an.$$

We prove $T(n)\le cn$ by strong induction, for a suitable constant $c$. For $n<140$ it holds if $c$ is at least the
largest of $T(n)/n$ over those finitely many $n$. For $n\ge140$, using the induction hypothesis on the two smaller
calls (and $\lceil n/5\rceil\le n/5+1$),

$$\begin{aligned}
T(n)&\le c\Big(\frac n5+1\Big)+c\Big(\frac{7n}{10}+6\Big)+an\\
&=cn-\Big(\frac{cn}{10}-7c-an\Big).
\end{aligned}$$

This is at most $cn$ when $\frac{cn}{10}-7c\ge an$, that is $c\ge\frac{10an}{n-70}$. For $n\ge140$ the right side is at
most $20a$, so $c=\max(20a,\ \max_{n<140}T(n)/n)$ works. $\square$

**The intuition** is the recursion tree. A call on $n$ items makes two calls, on about $n/5$ and $7n/10$ items, whose
sizes add up to $9n/10$. So the total size at each level of the tree shrinks by a factor of $9/10$, and the work is a
geometric series:

$$an\Big(1+\frac9{10}+\Big(\frac9{10}\Big)^2+\cdots\Big)=10an.$$

The general principle: if $T(n)\le T(\alpha n)+T(\beta n)+O(n)$ with $\alpha+\beta<1$, then $T(n)=O(n)$. The two
fractions must add up to *less than* 1.

**Why groups of 5?** With groups of 3, the same count gives at least $2(\lceil g/2\rceil-2)\approx n/3$ items on each
side, so the recursion is $T(n)\le T(n/3)+T(2n/3)+O(n)$. Now $\tfrac13+\tfrac23=1$: every level of the recursion tree
costs about the same, and there are $\Theta(\log n)$ levels, so the bound is only $O(n\log n)$. Groups of 7 work (the
fractions are $\tfrac17$ and $\tfrac57$), and so does any larger odd size; 5 is the smallest that works. (Chen and Dumitrescu,
"Select with Groups of 3 or 4", 2015, show that a modified grouping makes 3 and 4 work too.)

**In practice** median of medians is slower than quickselect. The program measures about 7 to 8 comparisons per item on
random data, against quickselect's 3.5, and about 5.8 per item on sorted data (where quickselect with a fixed pivot
would take quadratic time). Its job in real libraries is the same as heapsort's in introsort: a guarantee. **Introselect**
(Musser, 1997) runs quickselect and switches to median of medians if the parts are not shrinking fast enough. Floyd
and Rivest's algorithm SELECT ("Expected Time Bounds for Selection", 1975) goes the other way: it picks *two* pivots
from a small random sample, chosen to bracket the target closely, and finds the $k$-th item with
$n+\min(k,n-k)+o(n)$ expected comparisons, about $1.5n$ for the median, which is known to be optimal for the expected
number up to the lower-order term.

**How many comparisons does the median really need?** A lower-bound argument like the one for the minimum (each item
must be shown to be on the correct side) gives about $1.5n$; Bent and John (1985) raised it to $2n$, and Dor and Zwick
proved a lower bound slightly above $2n$ (2001) and gave an algorithm using about $2.95n$ comparisons in the worst case
("Selecting the Median", 1999). The exact constant is still unknown.

The full selection program:

```python
--8<-- "books/algorithms/ch06_selection.py"
```

Output:

```
quickselect and median of medians agree with sorted(a)[k] on 500 random lists
exact expectation = Knuth's formula for all n <= 12, every k
  n = 3, median: 8/3   n = 4, smallest: 23/6

comparisons / n  (median, random distinct data)
        n  quickselect avg  2(1+ln2)  median of medians
     1000            3.458     3.386              7.040
    10000            3.534     3.386              8.005
   100000            3.481     3.386              8.244
  median of medians on sorted input, n = 100000: 5.826 comparisons per item

top 5 of 100000: [999974, 999964, 999948, 999941, 999933]
```

(Quickselect's averages are a little above $3.386$ because the formula's leading term ignores lower-order terms, and
because 20 runs is a small sample. Median of medians makes fewer comparisons on sorted input because every group of 5 is
already sorted, so insertion sort needs only 4 comparisons per group.)

## 6.6 Order statistics in practice: top-k and partial sorts

A search engine has a million matching pages and shows the best ten. A leaderboard shows the top 100 of ten million
players. A rover picks the five most interesting targets in a camera frame of thousands of candidate rocks (this is
roughly what the AEGIS software on Curiosity does: it detects candidate targets in a navigation-camera image, ranks them
by properties the science team chose, and points the ChemCam laser at the best, without waiting for a command from
Earth, where a round trip takes between about 8 and 48 minutes). None of these needs a full sort. There are three good
methods for "the $k$ largest of $n$".

**1. A min-heap of size $k$.** Scan the items. Keep the best $k$ seen so far in a min-heap, so the *weakest* of them is
at the top. For each new item, if it beats the weakest, replace the weakest with it and sift down.

```python
def top_k_heap(xs, k):
    h = []
    for x in xs:
        if len(h) < k:     heapq.heappush(h, x)
        elif x > h[0]:     heapq.heapreplace(h, x)   # drop the smallest of the k kept so far
    return sorted(h, reverse=True)
```

*Correctness:* invariant: after reading a prefix of the input, the heap holds the $k$ largest items of that prefix. A
new item belongs in the top $k$ of the longer prefix exactly when it beats the current $k$-th largest, which is the
heap's minimum $h[0]$. *Cost:* $O(n\log k)$ time in the worst case and only $O(k)$ memory. It works on a **stream**
that is too big to store, read once, which neither sorting nor quickselect can do. On random input it is even better:
the $i$-th item enters the heap only if it is among the top $k$ of the first $i$, with probability $k/i$, so the
expected number of heap updates is about $k\ln(n/k)$, and the expected time is $O(n+k\log k\log(n/k))$.

**2. Quickselect, then sort the winners.** Select the item of rank $n-k$; after a three-way partition, everything in the
greater part (plus enough of the equal part) is the top $k$. Sort those: $O(n+k\log k)$ expected time, $O(n)$ memory.

**3. Partial heapsort.** Build a max-heap of all $n$ items in $O(n)$ ([Chapter 9](09-Heaps-and-Priority-Queues.md)) and
pop $k$ times: $O(n+k\log n)$, and the output comes sorted.

For $k$ much smaller than $n$, all three are close to linear; the heap method wins when memory or one-pass access
matters. When $k$ is close to $n$, just sort.

**In practice.**

- Python: `heapq.nlargest(k, xs)` and `heapq.nsmallest(k, xs)` implement method 1 (with shortcuts to `max`, `min` or
  plain sorting in edge cases); `statistics.median` sorts.
- C++: `std::nth_element` (usually introselect) rearranges so that position $k$ holds the right item with smaller items
  before it and larger after; `std::partial_sort` sorts the first $k$ positions with a heap.
- NumPy: `numpy.partition` and `numpy.argpartition` select in linear time (introselect).
- Databases: query engines commonly execute `ORDER BY score DESC LIMIT 10` with a top-$k$ heap instead of a full sort.

Selection is also a building block. Quicksort with the exact median as pivot (found by SELECT) is $O(n\log n)$ in the
worst case, though slower in practice than introsort. Weighted medians solve one-dimensional facility location: the point
on a line that minimizes the total distance to $n$ sites is a median of the sites (Exercise 9). And Chapter 11 uses
linear-time selection inside other divide-and-conquer algorithms.

## Check yourself

??? question "1. Run counting sort by hand on [2, 0, 2, 1, 0] with k = 3. Give the counts, the first slots and the output."

    Counts for keys 0, 1, 2: $2,1,2$. Prefix sums (first slots): $0,2,3$. Placing left to right: 2 goes to slot 3,
    0 to slot 0, the second 2 to slot 4, 1 to slot 2, the second 0 to slot 1. Output: $[0,0,1,2,2]$, and the two 0s
    (and the two 2s) are in their input order.

??? question "2. In step 3 of counting sort, what goes wrong if you read the input from right to left but still fill each key's slots from left to right?"

    Items with the same key are then placed in reverse input order: the last one in the input takes the first slot.
    The output is still sorted by key, but **not stable**. Inside radix sort this gives wrong answers, as the program's
    "unstable digit sort" shows. (Reading right to left *and* filling from the right, decrementing the counters, as in
    CLRS, is stable again.)

??? question "3. You must radix sort a million 32-bit keys. Compare digit sizes r = 8, 16 and 32 by the cost model (b/r)(n + 2^r)."

    $r=8$: 4 passes of $10^6+256$, about $4.0\times10^6$. $r=16$: 2 passes of $10^6+65\,536$, about $2.13\times10^6$.
    $r=32$: 1 pass of $10^6+2^{32}\approx4.3\times10^9$, hopeless. So $r=16$ is best in this model; in practice $r=8$
    or $r=11$ often wins because 256 or 2048 counters fit in the fastest cache while 65 536 do not.

??? question "4. Show by an example that processing digits from most significant to least significant, with a stable sort on each digit, does not sort."

    Take $[21,12]$. Sort stably by the tens digit: $[12,21]$. Then stably by the units digit: $21$ has units 1 and $12$
    has units 2, so the result is $[21,12]$, which is wrong. The last pass decides the order, so the last pass must use
    the most important digit.

??? question "5. Sort n integers in the range 0 to n³ − 1 in O(n) time."

    Write each key in base $n$: since $n^3-1<n^3$ it has at most 3 base-$n$ digits, $x=d_2n^2+d_1n+d_0$. Run LSD radix
    sort with counting sort on each digit ($k=n$): 3 passes of $\Theta(n+n)$, so $\Theta(n)$ in total. In code, the
    digit of pass $i$ is `(x // n**i) % n`.

??? question "6. Compute the expected number of comparisons of randomized quickselect for the median of 3 distinct items by hand."

    The first partition compares the pivot with the 2 others: 2 comparisons. With probability $\tfrac13$ the pivot is
    the median itself: done. With probability $\tfrac23$ it is the smallest or largest; the median is then in a part
    of 2 items, where one more partition (1 comparison) finds it. Expected total
    $2+\tfrac23\cdot1=\tfrac83$, which is what the program's exact computation prints and what Knuth's formula gives
    for $n=3$, $k=2$: $2[4\cdot\tfrac{11}6-4\cdot\tfrac32-4\cdot\tfrac32+6]=2[\tfrac{22}3-6]=\tfrac83$.

??? question "7. Find both the minimum and the maximum of n items with about 3n/2 comparisons instead of 2n − 2."

    Take the items in pairs. Compare the two items of a pair (1 comparison); compare the smaller with the current
    minimum and the larger with the current maximum (2 more). That is 3 comparisons per 2 items. Starting from the
    first pair (1 comparison gives the initial minimum and maximum), the total for even $n$ is
    $1+3(n-2)/2=\tfrac{3n}2-2$, and for odd $n$ (start with the first item as both) $3(n-1)/2$; in both cases
    $\lceil3n/2\rceil-2$. For $n=8$: 10 comparisons, against 14 for two separate scans. (This is optimal; CLRS 9.1
    gives the adversary argument.)

??? question "8. Explain why median of medians with groups of 3 only gives O(n log n), but groups of 7 give O(n)."

    With groups of 3, at least about $2\cdot\tfrac{n}{6}=\tfrac n3$ items lie on each side of the pivot, so the larger
    part may have $\tfrac{2n}3$ items, and the recursion is $T(n)\le T(\tfrac n3)+T(\tfrac{2n}3)+cn$. The two
    subproblem sizes add up to $n$, so every level of the recursion tree costs $cn$ and there are
    $\Theta(\log n)$ levels: $\Theta(n\log n)$ for this bound. With groups of 7, at least $4\cdot\tfrac n{14}=\tfrac{2n}7$
    items lie on each side, the recursion is $T(n)\le T(\tfrac n7)+T(\tfrac{5n}7)+cn$, and $\tfrac17+\tfrac57=\tfrac67<1$,
    so the level costs shrink geometrically and $T(n)\le7cn$.

??? question "9. Show that the point m on a line minimizing the total distance Σ|x_i − m| to n sites is a median of the sites, and write the code."

    Move $m$ a little to the right. Every site to the left of $m$ gets farther by that amount and every site to the
    right gets closer. So the total decreases while more sites are to the right than to the left, and increases when
    more are to the left. It is minimal where the counts balance: at a median (for even $n$, anywhere between the two
    middle sites).

    ```python
    import random
    def best_meeting_point(xs):
        return quickselect(list(xs), (len(xs) - 1) // 2, random.Random(1))  # from ch06_selection.py

    xs = [2, 9, 4, 1, 15]
    m = best_meeting_point(xs)                       # 4
    print(m, sum(abs(x - m) for x in xs))            # 4 21
    ```

    The total at $m=4$ is $2+5+0+3+11=21$; at $m=5$ (the mean is $6.2$) it would be $3+4+1+4+10=22$.

??? question "10. Find the second smallest of n items with n + ⌈log₂ n⌉ − 2 comparisons."

    Run a **knockout tournament**: pair the items, the smaller of each pair goes on, and so on, $n-1$ comparisons in
    all; the winner is the minimum. The second smallest lost only to the minimum (it beat everyone else it met), so it
    is among the items that lost *directly* to the minimum. The minimum played one match per round, at most
    $\lceil\log_2 n\rceil$ matches. Find the smallest of those at most $\lceil\log_2 n\rceil$ items with
    $\lceil\log_2 n\rceil-1$ comparisons. Total $n+\lceil\log_2 n\rceil-2$; for $n=8$, $8+3-2=9$. Kislitsyn proved in
    1964 that this is optimal.

??? question "11. Write a function that returns the k smallest items of a list in sorted order in O(n + k log k) expected time."

    ```python
    import random
    def k_smallest(xs, k, rng=random.Random(0)):
        if k <= 0: return []
        a, out = list(xs), []
        while True:                          # quickselect, but keep everything known to be small
            pivot = a[rng.randrange(len(a))]
            lo = [x for x in a if x < pivot]
            eq = [x for x in a if x == pivot]
            hi = [x for x in a if x > pivot]
            if k <= len(lo):
                a = lo
            elif k <= len(lo) + len(eq):
                return sorted(out + lo) + eq[:k - len(lo)]
            else:
                out += lo + eq; k -= len(lo) + len(eq); a = hi

    xs = [7, 2, 9, 4, 3, 8, 6, 5]
    assert k_smallest(xs, 3) == [2, 3, 4]
    ```

    Each round costs $O(|a|)$ and the sizes shrink like quickselect's, so the selection is $O(n)$ expected; the items
    collected in `out` and `lo` are at most $k$ in total, and sorting them costs $O(k\log k)$.

## What you learned

- The $n\log n$ lower bound is about the comparison model. Using keys as array indices (the word RAM) answers
  many-way questions in one step, and sorting can be linear.
- Counting sort is stable and $\Theta(n+k)$; it is the right tool for keys in a small range and the engine of radix
  sort.
- LSD radix sort is correct *because* each pass is stable; with $r\approx\log_2 n$-bit digits it sorts $b$-bit keys in
  $\Theta(bn/\log n)$, linear for keys below $n^c$. MSD radix sort suits strings.
- Bucket sort is expected linear on uniform data, since $E[\sum n_i^2]=2n-1$, but quadratic on clustered data unless
  the buckets are sorted with an $O(m\log m)$ sort.
- Selection is easier than sorting: quickselect makes fewer than $4n$ expected comparisons (about $3.39n$ for the
  median), proved with the same indicator-variable method as quicksort.
- The median of medians guarantees a pivot with at least $3n/10-6$ items on each side, giving
  $T(n)\le T(n/5)+T(7n/10+6)+O(n)=O(n)$ in the worst case.
- For the top $k$, a size-$k$ heap gives $O(n\log k)$ time and $O(k)$ memory on a stream; libraries provide
  `heapq.nlargest`, `nth_element`, `numpy.partition`.

**Next:** [Chapter 7](07-Searching-and-Hashing.md) turns from ordering to finding: binary search, and hash tables that
look up a key in expected constant time.

## Further reading

- T. H. Cormen, C. E. Leiserson, R. L. Rivest and C. Stein, *Introduction to Algorithms*, 4th ed., 2022: chapter 8
  (linear-time sorting) and chapter 9 (medians and order statistics).
- D. E. Knuth, *The Art of Computer Programming*, Vol. 3: *Sorting and Searching*, 2nd ed., 1998: 5.2.5 (radix sorting)
  and 5.3.3 (minimum-comparison selection).
- J. Kleinberg and É. Tardos, *Algorithm Design*, 2005: 13.5 (median finding and quicksort).
- R. Sedgewick and K. Wayne, *Algorithms*, 4th ed., 2011: 5.1 (string sorts: LSD, MSD, three-way radix quicksort).
- C. A. R. Hoare, "Algorithm 65: Find", *Communications of the ACM* 4(7), 1961.
- M. Blum, R. W. Floyd, V. Pratt, R. L. Rivest and R. E. Tarjan, "Time Bounds for Selection", *Journal of Computer and
  System Sciences* 7(4), 1973.
- R. W. Floyd and R. L. Rivest, "Expected Time Bounds for Selection", *Communications of the ACM* 18(3), 1975.
- D. Dor and U. Zwick, "Selecting the Median", *SIAM Journal on Computing* 28(5), 1999.
- K. Chen and A. Dumitrescu, "Select with Groups of 3 or 4", WADS 2015.
- P. M. McIlroy, K. Bostic and M. D. McIlroy, "Engineering Radix Sort", *Computing Systems* 6(1), 1993.
- J. L. Bentley and R. Sedgewick, "Fast Algorithms for Sorting and Searching Strings", SODA 1997.
- Y. Han and M. Thorup, "Integer Sorting in $O(n\sqrt{\log\log n})$ Expected Time and Linear Space", FOCS 2002.
- Reference pages on this site: [Counting sort](../../sorting/counting-sort.md),
  [Radix sort](../../sorting/radix-sort.md), [Quicksort](../../sorting/quicksort.md),
  [Binary heap](../../data-structures/binary-heap.md).
- The [probability material in the math books](https://math.akadian.ca/books/) for binomial variables, variance and
  linearity of expectation.
