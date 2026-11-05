# 11. Divide and conquer

*Some problems are hard to attack head-on but easy once they are small. Divide and conquer turns that observation
into a method: cut the problem into smaller copies of itself, solve the copies by the same method, and stitch the
answers together. In this chapter you will see the pattern behind merge sort and binary search, then use it to count
inversions, find the best stretch of a list, multiply numbers with fewer than $n^2$ digit products, multiply matrices
with seven products instead of eight, find the closest two points in a cloud, and finally build the fast Fourier
transform, the algorithm that multiplies polynomials and huge integers in $O(n \log n)$ time.*

!!! abstract "In this chapter"
    **You will learn:**

    - the three steps of divide and conquer, and how to read off a recurrence from them
    - how to count inversions in $O(n \log n)$ by piggybacking on merge sort
    - the maximum subarray problem, solved by divide and conquer and then by Kadane's one-pass scan
    - Karatsuba's trick, which multiplies $n$-digit numbers in $O(n^{1.585})$ steps, with a proof
    - Strassen's seven products and why they give $O(n^{2.81})$ matrix multiplication
    - the closest pair of points in $O(n \log n)$, with a proof of the strip lemma
    - the fast Fourier transform: roots of unity, the butterfly, $O(n \log n)$, and multiplying big numbers

    **You need:** [Chapter 3](03-Recursion-and-Induction.md) (recursion, recurrences, the master theorem) and
    [Chapter 5](05-Sorting-by-Comparison.md) (merge sort). For 11.7, complex numbers at the level of
    [https://math.akadian.ca/books/algebra/](https://math.akadian.ca/books/algebra/).

    **Levels:** 11.1 to 11.3 are beginner to intermediate; 11.4 to 11.6 are intermediate; 11.7 is advanced.

## 11.1 The pattern; merge sort and binary search seen again

Suppose you are handed a shuffled deck of a thousand numbered cards and asked to sort them. Doing it in one go is
daunting. But if someone gave you two sorted piles of five hundred, you could finish in a minute: look at the top
card of each pile, take the smaller, repeat. And each pile of five hundred is the same problem again, only smaller.
Keep halving, and eventually every pile has one card, which is sorted already.

That is **divide and conquer**. Every divide-and-conquer algorithm has three steps:

1. **Divide** the input into smaller instances of the same problem (usually two or more pieces of roughly equal
   size).
2. **Conquer** each piece by calling the algorithm recursively. When a piece is small enough (the **base case**),
   solve it directly.
3. **Combine** the answers of the pieces into an answer for the whole.

The word "recursively" matters. A divide-and-conquer algorithm is a recursive algorithm, so everything from
[Chapter 3](03-Recursion-and-Induction.md) applies: we prove it correct by induction on the size of the input, and
we find its running time by writing a **recurrence**, an equation that gives the cost $T(n)$ on an input of size $n$
in terms of the cost on smaller inputs.

### Reading the recurrence off the three steps

If the divide step makes $a$ pieces, each of size $n/b$, and dividing plus combining costs $f(n)$, then

$$
T(n) = a\,T(n/b) + f(n), \qquad T(\text{small}) = \text{constant}.
$$

The **master theorem** of [Chapter 3](03-Recursion-and-Induction.md) solves this recurrence by comparing $f(n)$ with
$n^{\log_b a}$, the number of leaves in the recursion tree:

- if $f(n)$ is polynomially smaller than $n^{\log_b a}$, the leaves dominate and $T(n) = \Theta(n^{\log_b a})$;
- if $f(n) = \Theta(n^{\log_b a})$, every level of the tree costs the same and $T(n) = \Theta(n^{\log_b a} \log n)$;
- if $f(n)$ is polynomially larger (and a mild regularity condition holds), the root dominates and
  $T(n) = \Theta(f(n))$.

You will see all three in this chapter. Keep one picture in mind: a **recursion tree**, with the whole problem at the
root, its $a$ pieces as children, and so on down to the base cases. The total cost is the sum over all nodes of the
divide-and-combine work done at that node.

### Merge sort

[Merge sort](../../sorting/merge-sort.md), from [Chapter 5](05-Sorting-by-Comparison.md), is the model. Divide: split
the list in half (cost $O(1)$, or $O(n)$ if you copy). Conquer: sort each half. Combine: merge two sorted lists of total
length $n$ in $n - 1$ comparisons at most. So $T(n) = 2T(n/2) + \Theta(n)$. Here $a = b = 2$, so
$n^{\log_b a} = n$, which matches $f(n)$: middle case, $T(n) = \Theta(n \log n)$. In the recursion tree, level $k$
has $2^k$ pieces of size $n/2^k$, so the merging on each level costs about $n$, and there are $\log_2 n$ levels.

### Binary search

[Binary search](../../searching/binary-search.md) is divide and conquer in which only one piece survives. To look for
$x$ in a sorted list, compare it with the middle item; that one comparison tells you which half could contain $x$,
and you throw the other half away. Divide costs $O(1)$, there is one piece of size $n/2$, and combining is free:
$T(n) = T(n/2) + O(1)$. Now $a = 1$, $b = 2$, $n^{\log_2 1} = n^0 = 1$, which matches $f(n) = O(1)$, so
$T(n) = \Theta(\log n)$. Some books call this pattern **decrease and conquer**, because the problem shrinks but does
not split.

### When does dividing help?

Dividing pays off when the combine step is cheaper than solving the problem from scratch, and the pieces do not
overlap. Two warnings:

- **Overlap.** The naive recursion for Fibonacci numbers, $F(n) = F(n-1) + F(n-2)$, divides into two pieces that share
  almost all their work, and it takes exponential time. When pieces overlap, you want
  [dynamic programming](13-Dynamic-Programming.md), not divide and conquer.
- **Imbalance.** If the pieces are very unequal, say sizes $n-1$ and $0$, the recursion has depth $n$ and the savings
  vanish. That is exactly quicksort's worst case.

The art in every algorithm below is in the combine step: finding a way to merge the answers of the halves that is
cheaper than starting again.

## 11.2 Counting inversions

Two friends each rank the same ten films from best to worst. How similar are their tastes? One natural measure:
count the pairs of films that they put in opposite orders. If you number the films by the first friend's ranking,
the second friend's list becomes a sequence of numbers, and the question becomes: how many pairs are out of order?

An **inversion** in a list $a_0, a_1, \dots, a_{n-1}$ is a pair of positions $i < j$ with $a_i > a_j$. A sorted list
has none; a list in reverse order has every pair inverted, which is $\binom{n}{2} = n(n-1)/2$ of them. The number of
inversions is called the **Kendall tau distance** between two rankings, after the statistician Maurice Kendall, who
used it in 1938 to measure rank correlation. Recommendation systems use the same idea to find people whose tastes
match yours.

The obvious algorithm checks every pair, which costs $\Theta(n^2)$. Can we do better without examining every pair?

### Divide: split into halves

Split the list into a left half $L$ and a right half $R$. Every inversion $(i, j)$ is one of three kinds:

- both $i$ and $j$ in $L$ (a **left inversion**);
- both in $R$ (a **right inversion**);
- $i$ in $L$ and $j$ in $R$ (a **cross inversion**).

Recursion counts the first two kinds. The whole difficulty is the third: there can be up to $(n/2)^2$ cross pairs,
so we cannot look at them one at a time.

### Combine: count while merging

Here is the key idea. Whether a cross pair is inverted depends only on the two values, not on where they sit inside
their halves. So we may **sort each half first** without changing the number of cross inversions. Then merge the two
sorted halves as merge sort does. Each time the merge takes an element $r$ from the right half, every element still
waiting in the left half is larger than $r$ (otherwise it would have been taken first) and sits to the left of $r$ in
the original list. So $r$ is inverted with exactly that many left elements, and we add that number to the count.

```python
--8<-- "books/algorithms/ch11_inversions.py"
```

```
array: [3, 8, 2, 5, 1, 9, 4]
sorted: [1, 2, 3, 4, 5, 8, 9]  inversions: 10  brute force: 10

changes: [13, -3, -25, 20, -3, -16, -23, 18, 20, -7, 12, -5, -22, 15, -4, 7]
divide and conquer (sum, start, end): (43, 7, 11)
Kadane              (sum, start, end): (43, 7, 11)

300 random tests against brute force passed: True
inversions in 2000..1 (should be 2000*1999/2 = 1999000): 1999000
```

The program also contains the two maximum-subarray algorithms of 11.3; ignore them for now.

### A trace by hand

Take $a = [3, 8, 2, 5, 1, 9, 4]$. The recursion splits it into $[3, 8, 2]$ and $[5, 1, 9, 4]$, and so on down to
single elements. Figure 11.1 shows the tree with the cross inversions found at each merge.

<figure class="mars-fig" markdown="0">
<svg viewBox="0 0 640 295" role="img" aria-label="Recursion tree of merge-and-count on the list 3 8 2 5 1 9 4. The root splits into 3 8 2 and 5 1 9 4. 3 8 2 splits into 3 and 8 2, which splits into 8 and 2. 5 1 9 4 splits into 5 1 and 9 4, each splitting into single elements. The cross inversions found at each merge are 1 for 8 2, 1 for 3 with 2 8, 1 for 5 1, 1 for 9 4, 1 for 1 5 with 4 9, and 5 at the root, for a total of 10.">
<g stroke="currentColor" stroke-width="1.3" fill="none">
<line x1="320" y1="44" x2="160" y2="82"/>
<line x1="320" y1="44" x2="470" y2="82"/>
<line x1="160" y1="114" x2="80" y2="152"/>
<line x1="160" y1="114" x2="220" y2="152"/>
<line x1="470" y1="114" x2="400" y2="152"/>
<line x1="470" y1="114" x2="540" y2="152"/>
<line x1="220" y1="184" x2="190" y2="222"/>
<line x1="220" y1="184" x2="250" y2="222"/>
<line x1="400" y1="184" x2="370" y2="222"/>
<line x1="400" y1="184" x2="430" y2="222"/>
<line x1="540" y1="184" x2="510" y2="222"/>
<line x1="540" y1="184" x2="570" y2="222"/>
</g>
<g stroke="currentColor" stroke-width="1.3">
<rect x="220" y="12" width="200" height="32" rx="5" fill="#eea66f" fill-opacity="0.35"/>
<rect x="105" y="82" width="110" height="32" rx="5" fill="#9cc9ea" fill-opacity="0.35"/>
<rect x="405" y="82" width="130" height="32" rx="5" fill="#9cc9ea" fill-opacity="0.35"/>
<rect x="60" y="152" width="40" height="32" rx="5" fill="#7ccf9a" fill-opacity="0.35"/>
<rect x="190" y="152" width="60" height="32" rx="5" fill="#7ccf9a" fill-opacity="0.35"/>
<rect x="370" y="152" width="60" height="32" rx="5" fill="#7ccf9a" fill-opacity="0.35"/>
<rect x="510" y="152" width="60" height="32" rx="5" fill="#7ccf9a" fill-opacity="0.35"/>
<rect x="170" y="222" width="40" height="32" rx="5" fill="none"/>
<rect x="230" y="222" width="40" height="32" rx="5" fill="none"/>
<rect x="350" y="222" width="40" height="32" rx="5" fill="none"/>
<rect x="410" y="222" width="40" height="32" rx="5" fill="none"/>
<rect x="490" y="222" width="40" height="32" rx="5" fill="none"/>
<rect x="550" y="222" width="40" height="32" rx="5" fill="none"/>
</g>
<g font-family="monospace" font-size="14" text-anchor="middle" fill="currentColor">
<text x="320" y="33">3 8 2 5 1 9 4</text>
<text x="160" y="103">3 8 2</text>
<text x="470" y="103">5 1 9 4</text>
<text x="80" y="173">3</text>
<text x="220" y="173">8 2</text>
<text x="400" y="173">5 1</text>
<text x="540" y="173">9 4</text>
<text x="190" y="243">8</text>
<text x="250" y="243">2</text>
<text x="370" y="243">5</text>
<text x="430" y="243">1</text>
<text x="510" y="243">9</text>
<text x="570" y="243">4</text>
</g>
<g font-size="13" fill="currentColor">
<text x="428" y="33">+5 cross</text>
<text x="222" y="103">+1</text>
<text x="542" y="103">+1</text>
<text x="256" y="173">+1</text>
<text x="436" y="173">+1</text>
<text x="576" y="173">+1</text>
<text x="320" y="284" text-anchor="middle">total: 1 + 1 + 1 + 1 + 1 + 5 = 10 inversions</text>
</g>
</svg>
<figcaption>Figure 11.1. Merge-and-count on [3, 8, 2, 5, 1, 9, 4]. Each box adds the cross inversions found when its two sorted halves are merged.</figcaption>
</figure>

The last merge is the interesting one. The halves come back sorted as $L = [2, 3, 8]$ and $R = [1, 4, 5, 9]$, carrying
2 and 3 inversions from inside them. The merge goes like this:

| step | compare | take | left still waiting | cross count added | running cross count |
|---|---|---|---|---|---|
| 1 | 2 vs 1 | 1 from $R$ | 2, 3, 8 | 3 | 3 |
| 2 | 2 vs 4 | 2 from $L$ | 3, 8 | 0 | 3 |
| 3 | 3 vs 4 | 3 from $L$ | 8 | 0 | 3 |
| 4 | 8 vs 4 | 4 from $R$ | 8 | 1 | 4 |
| 5 | 8 vs 5 | 5 from $R$ | 8 | 1 | 5 |
| 6 | 8 vs 9 | 8 from $L$ | (none) | 0 | 5 |
| 7 | (left empty) | 9 from $R$ | (none) | 0 | 5 |

Check against the original list: the cross pairs are 1 with each of 3, 8, 2; 4 with 8; 5 with 8. That is five. With
the 2 left and 3 right inversions, the total is 10, which the brute-force count confirms.

### Why it is correct

**Claim.** `count_inversions(a)` returns the sorted list and the number of inversions of $a$.

*Proof* by strong induction on the length $n$ of `a`. For $n \le 1$ there are no pairs, and the function returns 0. For
$n \ge 2$, assume the claim for all shorter lists. By that assumption $x$ and $y$ are the numbers of left and right
inversions, and `left`, `right` are the halves in sorted order. Sorting within a half does not change which
(left value, right value) pairs are inverted, so the cross inversions of $a$ are exactly the pairs (an element of
`left`, an element of `right`) with the left one larger. The merge keeps this invariant: *everything already in
`merged` is at most everything still in `left[i:]` and `right[j:]`*, the usual merge invariant from
[Chapter 5](05-Sorting-by-Comparison.md). When it takes `right[j]`, we know `left[i] > right[j]`, and `left` is
sorted, so all `len(left) - i` elements `left[i:]` exceed `right[j]`; and no element `left[:i]` does, because each of
those was taken earlier, when it was at most the current right element, which is at most `right[j]`. So each right
element adds exactly the number of left elements greater than it, and summing over all right elements counts every
cross inversion exactly once. The merged list is sorted by the merge invariant. $\square$

**Running time.** The work outside the recursive calls is a merge, $\Theta(n)$, so
$T(n) = 2T(n/2) + \Theta(n) = \Theta(n \log n)$, the same as merge sort. We count up to $n(n-1)/2$ inversions while
touching each element only $O(\log n)$ times: the count is added in bulk, `len(left) - i` at a time, rather than one
pair at a time. That is the whole trick.

## 11.3 Maximum subarray (divide and conquer vs Kadane)

A rover logs the change in its battery charge every hour: positive when the solar panels win, negative when driving
or heating drains it. Over which stretch of consecutive hours did the battery gain the most? Or, the version in many
textbooks: given a stock's daily price changes, which buy day and sell day would have made the most money?

Formally, the **maximum subarray problem** asks: given numbers $a_0, \dots, a_{n-1}$ (some negative), find indices
$i < j$ that maximise the sum $a_i + a_{i+1} + \dots + a_{j-1}$ of the **contiguous** slice `a[i:j]`. If every number
were positive the answer would be the whole list, and if every number were negative it would be the single largest
one; the problem is interesting because of the mix.

There are $n(n+1)/2$ slices, so trying them all costs $\Theta(n^2)$ if you keep running sums, or $\Theta(n^3)$ if you
add each slice from scratch.

### Divide and conquer

Split at the middle $m$. The best slice either lies wholly in the left half, wholly in the right half, or **crosses**
the middle, containing both $a_{m-1}$ and $a_m$. Recursion handles the first two. A crossing slice is a suffix of the
left half glued to a prefix of the right half, and the two parts can be chosen independently: the best crossing slice
is the best suffix ending at $m - 1$ plus the best prefix starting at $m$. Each is found by one scan outward from the
middle, in $\Theta(n)$ total. So again $T(n) = 2T(n/2) + \Theta(n) = \Theta(n \log n)$.

The program's example is the classic list of 16 daily price changes from CLRS. The best slice is positions 7 to 10,
$18 + 20 - 7 + 12 = 43$: the crossing case at the top level, since the middle is between positions 7 and 8.

**Correctness** is again induction: every slice is in exactly one of the three classes, the recursive calls are right
by hypothesis, and for the crossing class the sum splits into (left part) + (right part), which are maximised
separately.

### Kadane's algorithm: one pass

Divide and conquer is not always the end of the story. Think about the best slice that **ends** at position $k$; call
its sum $E_k$. Either it is just $a_k$ alone, or it extends the best slice ending at $k - 1$. So

$$
E_k = \max(a_k,\; E_{k-1} + a_k) = a_k + \max(0, E_{k-1}),
$$

and the answer is $\max_k E_k$. In words: carry a running sum; if it ever drops below zero, throw it away and start
afresh at the next element, because a negative prefix can only make any later slice smaller. This is
**Kadane's algorithm**, and it runs in $\Theta(n)$ time and $O(1)$ extra space. It is really a tiny case of
[dynamic programming](13-Dynamic-Programming.md): $E_k$ is a table of subproblem answers, each computed from the one
before.

Trace on $[-2, 1, -3, 4, -1, 2, 1, -5, 4]$:

| $k$ | $a_k$ | $E_k$ (best ending here) | best so far |
|---|---|---|---|
| 0 | -2 | -2 | -2 |
| 1 | 1 | 1 (restart: -2 < 0) | 1 |
| 2 | -3 | -2 | 1 |
| 3 | 4 | 4 (restart) | 4 |
| 4 | -1 | 3 | 4 |
| 5 | 2 | 5 | 5 |
| 6 | 1 | 6 | 6 |
| 7 | -5 | 1 | 6 |
| 8 | 4 | 5 | 6 |

The best slice is $4 - 1 + 2 + 1 = 6$, positions 3 to 6.

**Correctness of the recurrence.** A slice ending at $k$ is either the one-element slice $[a_k]$ or a slice ending at
$k-1$ with $a_k$ appended; the best of the second kind is $E_{k-1} + a_k$ because appending $a_k$ adds the same
amount to every candidate. Taking the larger of the two kinds gives $E_k$. Every slice ends somewhere, so the best
slice overall is $\max_k E_k$. $\square$

**History.** Jon Bentley tells the story in his *Programming Pearls* column (Communications of the ACM, 1984, and the
book of 1986): Ulf Grenander had posed the two-dimensional version for pattern matching in images, the
one-dimensional version was solved in $O(n^2)$, then $O(n \log n)$ by divide and conquer, and then Jay Kadane gave the
linear-time scan.

The lesson is honest: divide and conquer gave a good algorithm, but looking at the problem from another angle gave
a better one. Lower bounds settle such questions. Any correct algorithm must read every element (an unread element
could be a huge positive number), so $\Omega(n)$ is a lower bound, and Kadane meets it.

## 11.4 Karatsuba multiplication

How long does it take to multiply two $n$-digit numbers? The method from school writes down $n$ partial products,
each of $n$ digits, and adds them: $n^2$ digit-by-digit multiplications, plus additions of the same order. For
centuries nobody had a reason to think one could do better.

### The history

In 1960 Andrey Kolmogorov ran a seminar at Moscow State University on the complexity of computation, and he
conjectured that any method of multiplying two $n$-digit numbers needs on the order of $n^2$ elementary operations.
Within about a week, a 23-year-old student in the seminar, Anatoly Karatsuba, found a method that uses about
$n^{1.585}$ and disproved it. Kolmogorov wrote it up, and it appeared in 1962 under the names of Karatsuba and Yuri
Ofman. Karatsuba later described the episode himself in a 1995 article, "The complexity of computations".

### The trick

Write each $n$-digit number in two halves of $m = n/2$ digits:

$$
x = a \cdot 10^m + b, \qquad y = c \cdot 10^m + d.
$$

Then

$$
xy = ac \cdot 10^{2m} + (ad + bc) \cdot 10^m + bd.
$$

That looks like four half-size products, $ac$, $ad$, $bc$ and $bd$, and four half-size products give
$T(n) = 4T(n/2) + O(n)$, which is $\Theta(n^2)$: no gain. Karatsuba's observation is that we do not need $ad$ and
$bc$ separately, only their sum, and

$$
(a + b)(c + d) = ac + ad + bc + bd,
$$

so

$$
ad + bc = (a + b)(c + d) - ac - bd.
$$

Three multiplications, $ac$, $bd$ and $(a+b)(c+d)$, are enough. The extra additions and subtractions cost $O(n)$, and
multiplying by a power of ten is only a shift.

### A trace by hand

Multiply $x = 1234$ by $y = 5678$, with $m = 2$:

| quantity | value |
|---|---|
| $a, b$ | 12, 34 |
| $c, d$ | 56, 78 |
| $ac$ | 672 |
| $bd$ | 2652 |
| $(a+b)(c+d)$ | $46 \times 134 = 6164$ |
| $ad + bc$ | $6164 - 672 - 2652 = 2840$ |
| $xy$ | $672 \cdot 10^4 + 2840 \cdot 10^2 + 2652 = 7\,006\,652$ |

A direct check: $12 \times 78 + 34 \times 56 = 936 + 1904 = 2840$. The three smaller products would themselves be
done by the same method in a real implementation.

```python
--8<-- "books/algorithms/ch11_karatsuba_strassen.py"
```

```
karatsuba(1234, 5678) = 7006652   (check: 7006652)

 digits   recursive calls   n^1.585   schoolbook digit products
      8                49        27           64
     16               187        81          256
     32               517       243         1024
     64              1627       729         4096
    128              4843      2187        16384
    256             14149      6562        65536

Strassen 2x2: [[19, 22], [43, 50]]  ordinary: [[19, 22], [43, 50]]

   n   scalar mults (Strassen)   n^3 (ordinary)
   2                         7                8
   4                        49               64
   8                       343              512
  16                      2401             4096
  32                     16807            32768
```

The count of recursive calls roughly triples each time the number of digits doubles (from 1627 to 4843 to 14149),
while the schoolbook count quadruples. The constant is not exactly 3 because the sums $a + b$ and $c + d$ can carry
into one more digit, and because the split is by decimal length, which is not always a power of two.

### The proof of $O(n^{\log_2 3})$

**Theorem.** If $n$ is a power of two and the base case is a one-digit product, Karatsuba's method uses about
$3^{\log_2 n} = n^{\log_2 3} \approx n^{1.585}$ one-digit multiplications, and $O(n^{\log_2 3})$ operations in all.

*Proof.* Ignore the carry for a moment (assume the half-sums still have $n/2$ digits; handling the extra digit adds
only a lower-order term). Let $M(n)$ be the number of one-digit products. Then $M(1) = 1$ and $M(n) = 3M(n/2)$, so
$M(n) = 3^{\log_2 n}$. Using $a^{\log_b c} = c^{\log_b a}$ (take $\log_b$ of both sides: each is
$\log_b a \cdot \log_b c$), this is $n^{\log_2 3}$.

For the total work, let $T(n) = 3T(n/2) + cn$, where $cn$ covers the additions, subtractions and shifts. In the
recursion tree, level $k$ has $3^k$ nodes, each doing $c\, n/2^k$ work, so level $k$ costs $cn (3/2)^k$. Summing a
geometric series with ratio $3/2 > 1$ over levels $k = 0, \dots, \log_2 n$:

$$
T(n) \le cn \sum_{k=0}^{\log_2 n} \left(\tfrac{3}{2}\right)^k
= cn \cdot \frac{(3/2)^{\log_2 n + 1} - 1}{3/2 - 1}
< 3cn \cdot \frac{3^{\log_2 n}}{n} = 3c\, n^{\log_2 3},
$$

plus the $n^{\log_2 3}$ base cases. The sum is dominated by its last term, the leaves: this is the first case of the
master theorem, with $f(n) = cn$ polynomially smaller than $n^{\log_2 3}$. $\square$

### Further and in practice

Splitting into three parts instead of two, and using five products instead of nine, gives **Toom-Cook**
multiplication (Toom 1963, Cook 1966) in $O(n^{\log_3 5}) \approx O(n^{1.465})$; more parts give exponents ever closer to
1, with growing constants. Section 11.7 goes further, to $O(n \log n)$ for polynomials. In practice, CPython's `int`
switches from schoolbook to Karatsuba multiplication once numbers exceed a cut-off of about 70 machine "digits" of 30
bits; below that, the overhead of recursion outweighs the saving. The GMP library chooses between schoolbook,
several Toom-Cook variants and FFT methods by size.

<figure class="play" data-play="karatsuba"><span class="ai-tag">AI-created</span><figcaption><b>Try it.</b> Digit products needed by schoolbook multiplication and by Karatsuba as the numbers grow.</figcaption></figure>

## 11.5 Strassen's matrix multiplication

Multiplying two $n \times n$ matrices by the definition, $C_{ij} = \sum_k A_{ik} B_{kj}$, takes $n$ multiplications for
each of the $n^2$ entries: $n^3$ in all. Can divide and conquer help?

### Blocks

Cut each matrix into four $n/2 \times n/2$ **blocks**:

$$
A = \begin{pmatrix} A_{11} & A_{12} \\ A_{21} & A_{22} \end{pmatrix}, \quad
B = \begin{pmatrix} B_{11} & B_{12} \\ B_{21} & B_{22} \end{pmatrix}, \quad
C = AB = \begin{pmatrix} C_{11} & C_{12} \\ C_{21} & C_{22} \end{pmatrix}.
$$

Block multiplication works just like multiplying $2 \times 2$ matrices of numbers, for example
$C_{11} = A_{11} B_{11} + A_{12} B_{21}$, as long as we keep the order of each product, because matrices do not
commute. That is eight half-size products and four half-size additions:
$T(n) = 8T(n/2) + \Theta(n^2)$, which solves to $\Theta(n^{\log_2 8}) = \Theta(n^3)$. No gain, just as with four
products in Karatsuba.

### Seven products

In 1969 Volker Strassen published, in a short paper titled "Gaussian elimination is not optimal", seven products that
are enough:

$$
\begin{aligned}
M_1 &= (A_{11} + A_{22})(B_{11} + B_{22}) \\
M_2 &= (A_{21} + A_{22})\,B_{11} \\
M_3 &= A_{11}\,(B_{12} - B_{22}) \\
M_4 &= A_{22}\,(B_{21} - B_{11}) \\
M_5 &= (A_{11} + A_{12})\,B_{22} \\
M_6 &= (A_{21} - A_{11})(B_{11} + B_{12}) \\
M_7 &= (A_{12} - A_{22})(B_{21} + B_{22})
\end{aligned}
$$

and then

$$
\begin{aligned}
C_{11} &= M_1 + M_4 - M_5 + M_7, & C_{12} &= M_3 + M_5, \\
C_{21} &= M_2 + M_4, & C_{22} &= M_1 - M_2 + M_3 + M_6.
\end{aligned}
$$

**Checking one entry.** Expand $C_{12} = M_3 + M_5 = A_{11}B_{12} - A_{11}B_{22} + A_{11}B_{22} + A_{12}B_{22}
= A_{11}B_{12} + A_{12}B_{22}$, which is the right answer. The other three entries expand the same way (exercise 7
asks you for $C_{11}$); each check uses only the distributive law and never swaps the two factors of a product. That
is essential, because when we recurse the "entries" are matrices, which do not commute. Strassen's formulas therefore
work over any **ring**, any number system with addition, subtraction and an associative multiplication.

With the numbers $A = \begin{pmatrix}1&2\\3&4\end{pmatrix}$, $B = \begin{pmatrix}5&6\\7&8\end{pmatrix}$:
$M_1 = 5 \cdot 13 = 65$, $M_2 = 7 \cdot 5 = 35$, $M_3 = 1 \cdot (-2) = -2$, $M_4 = 4 \cdot 2 = 8$,
$M_5 = 3 \cdot 8 = 24$, $M_6 = 2 \cdot 11 = 22$, $M_7 = (-2) \cdot 15 = -30$. Then
$C_{11} = 65 + 8 - 24 - 30 = 19$, $C_{12} = -2 + 24 = 22$, $C_{21} = 35 + 8 = 43$, $C_{22} = 65 - 35 - 2 + 22 = 50$,
matching the program.

### Running time

**Theorem.** For $n$ a power of two, Strassen's algorithm uses $7^{\log_2 n} = n^{\log_2 7} \approx n^{2.807}$ scalar
multiplications and $\Theta(n^{\log_2 7})$ operations in all.

*Proof.* Seven recursive products of half size plus 18 additions or subtractions of $n/2 \times n/2$ blocks:
$T(n) = 7T(n/2) + \Theta(n^2)$. Since $n^{\log_2 7} \approx n^{2.807}$ grows polynomially faster than $n^2$, the master
theorem's first case gives $T(n) = \Theta(n^{\log_2 7})$. Directly: level $k$ of the recursion tree has $7^k$ nodes
each doing $\Theta((n/2^k)^2)$ work, a total of $\Theta(n^2 (7/4)^k)$, a geometric series dominated by the leaves.
For the multiplication count, $M(1) = 1$ and $M(n) = 7M(n/2)$. $\square$

The program's table shows exactly $7^k$ against $8^k$ for $n = 2^k$.

### In practice

Strassen's algorithm has larger constants than the definition (18 block additions per level), uses extra memory for
the temporary sums, and is a little less accurate in floating point, because the subtractions can cancel large
numbers. Real libraries (the BLAS routines underneath NumPy and most scientific code) use the ordinary $n^3$ method,
cut into blocks that fit the processor's caches, and some switch to Strassen for very large matrices. Within
recursive implementations, one stops recursing at a block size of a few dozen to a few hundred and uses the ordinary
method below it.

Strassen's paper started a race. The exponent of matrix multiplication, written $\omega$, is the smallest number such
that $n \times n$ matrices can be multiplied in $O(n^{\omega + \varepsilon})$ operations for every $\varepsilon > 0$. We know
$2 \le \omega$ (you must at least write down the $n^2$ answers) and today $\omega < 2.38$; whether $\omega = 2$ is
open. [Chapter 25](25-Where-Algorithms-Go.md) tells that story. None of the theoretically fastest methods is used in
practice; their constants are astronomically large.

## 11.6 Closest pair of points in O(n log n)

You have the positions of $n$ points in the plane: aircraft on a radar screen, stars in a photograph, sample sites a
rover has visited. Which two are closest together? Air-traffic control asks exactly this question to find the pair of
aircraft most in danger of collision.

Checking all $\binom{n}{2}$ pairs costs $\Theta(n^2)$. In one dimension it is easy to do better: sort the points,
and the closest pair must be neighbours in sorted order, so one scan after sorting finds it in $O(n \log n)$. In two
dimensions there is no single order with that property. Michael Shamos and Dan Hoey showed in 1975 ("Closest-point
problems") that divide and conquer still achieves $O(n \log n)$; the version below is the one in CLRS and Kleinberg
and Tardos.

### The algorithm

Assume all points are distinct. Write $d(p, q)$ for the ordinary distance
$\sqrt{(p_x - q_x)^2 + (p_y - q_y)^2}$.

1. **Divide.** Sort the points by $x$. Draw a vertical line $x = m$ through the median, so that half the points
   ($L$) lie on or left of it and half ($R$) on or right of it.
2. **Conquer.** Recursively find the closest pair within $L$ (distance $\delta_L$) and within $R$ ($\delta_R$). Let
   $\delta = \min(\delta_L, \delta_R)$.
3. **Combine.** The only pairs not yet examined have one point in $L$ and one in $R$. Such a pair can beat $\delta$
   only if both points lie within $\delta$ of the line, in the vertical **strip** $m - \delta < x < m + \delta$:
   a point farther from the line is more than $\delta$ away horizontally from everything on the other side. Take the
   points in the strip, sorted by $y$. For each one, compare it with the next **seven** points in that order, and keep
   the best pair found.

Why seven? That is the strip lemma.

<figure class="mars-fig" markdown="0">
<svg viewBox="0 0 600 340" role="img" aria-label="Points scattered in the plane with a dashed vertical dividing line. A shaded strip of width delta on each side of the line. Above a point p in the strip, a rectangle delta high and two delta wide is divided into eight squares of side delta over two; at most one point lies in each square.">
<rect x="200" y="20" width="200" height="280" fill="#9cc9ea" fill-opacity="0.25"/>
<rect x="200" y="150" width="200" height="100" fill="#eea66f" fill-opacity="0.35" stroke="currentColor" stroke-width="1.5"/>
<g stroke="currentColor" stroke-width="0.8" stroke-dasharray="3 3">
<line x1="250" y1="150" x2="250" y2="250"/>
<line x1="350" y1="150" x2="350" y2="250"/>
<line x1="200" y1="200" x2="400" y2="200"/>
</g>
<line x1="300" y1="20" x2="300" y2="300" stroke="currentColor" stroke-width="1.5" stroke-dasharray="7 5"/>
<g fill="currentColor">
<circle cx="60" cy="80" r="4"/>
<circle cx="80" cy="240" r="4"/>
<circle cx="160" cy="170" r="4"/>
<circle cx="230" cy="60" r="4"/>
<circle cx="330" cy="160" r="4"/>
<circle cx="390" cy="245" r="4"/>
<circle cx="470" cy="90" r="4"/>
<circle cx="520" cy="230" r="4"/>
</g>
<circle cx="260" cy="250" r="5.5" fill="#7ccf9a" stroke="currentColor" stroke-width="1.5"/>
<g font-size="13" fill="currentColor">
<text x="270" y="246">p</text>
<text x="306" y="34">line x = m</text>
<text x="40" y="34">left half L</text>
<text x="480" y="34">right half R</text>
<text x="412" y="205">δ high</text>
</g>
<g stroke="currentColor" stroke-width="1.2">
<line x1="200" y1="285" x2="300" y2="285"/>
<line x1="300" y1="285" x2="400" y2="285"/>
<line x1="200" y1="279" x2="200" y2="291"/>
<line x1="300" y1="279" x2="300" y2="291"/>
<line x1="400" y1="279" x2="400" y2="291"/>
</g>
<g font-size="13" fill="currentColor" text-anchor="middle">
<text x="250" y="279">δ</text>
<text x="350" y="279">δ</text>
<text x="300" y="325">a δ × 2δ box above p, cut into 8 squares of side δ/2: at most one point in each</text>
</g>
</svg>
<figcaption>Figure 11.2. The strip lemma. Any point that could be within δ of p and above it lies in the shaded box; the box has room for only eight points that are at least δ apart within each half.</figcaption>
</figure>

### The strip lemma, proved

**Lemma.** Let $S$ be the points of the strip, sorted by $y$-coordinate. If two points $p, q \in S$ satisfy
$d(p, q) < \delta$, then they are at most 7 positions apart in $S$.

*Proof.* Suppose $q$ comes after $p$ in $S$, so $q_y \ge p_y$. Since $d(p,q) < \delta$, we have
$q_y - p_y < \delta$, and $q$ is in the strip. So $q$ lies in the rectangle $B$ of width $2\delta$ (the strip) and
height $\delta$ whose bottom edge is at height $p_y$. Cut $B$ into eight squares of side $\delta/2$, four on each side
of the line. A square of side $\delta/2$ has diameter $\delta/\sqrt{2} < \delta$, so two points in the same square
are closer than $\delta$. A square lies entirely on one side of the line, so two points in it would both be in $L$
or both in $R$, and their distance is at least $\delta$ by the definition of $\delta$. (Points exactly on the line
are assigned to $L$ or $R$ by the split; give each boundary square to the side whose points it contains. With that
convention each square still contains points of only one half.) So each square holds at most one point, $B$ holds at
most 8 points of $S$, and one of them is $p$ itself. Every point of $S$ between $p$ and $q$ in $y$-order also lies in
$B$. So at most 7 points come after $p$ in $S$ up to and including $q$. $\square$

The constant 7 is generous; more careful packing arguments lower it, but any constant is enough for the running time.
The code also stops the inner loop as soon as the $y$-gap reaches $\delta$, which in practice is after one or two
points.

### Running time

The trick is to avoid sorting the strip by $y$ in every call, which would cost $O(n \log n)$ per call and give
$O(n \log^2 n)$ in total. Instead, sort all the points by $y$ **once** at the start, and in each call split that list
into the $y$-sorted lists of $L$ and $R$ by a linear scan (the code keeps each point's half in a set). The strip is
then filtered from the $y$-sorted list in linear time, still sorted. So the work outside the recursion is $O(n)$:
splitting, filtering and at most $7|S|$ distance computations. Hence $T(n) = 2T(n/2) + O(n) = O(n \log n)$, plus the
initial two sorts, also $O(n \log n)$.

```python
--8<-- "books/algorithms/ch11_closest_pair.py"
```

```
points [(2, 3), (12, 30), (40, 50), (5, 1), (12, 10), (3, 4)]
closest pair (2, 3) (3, 4) at distance 1.4142

      n   distance comparisons   brute force pairs
    100                    148                4950
   1000                   1472              499500
  10000                  15543            49995000
fast answer agrees with brute force for n = 100 and 1000
```

A trace of the small example: sorted by $x$ the points are $(2,3), (3,4), (5,1), (12,10), (12,30), (40,50)$. The line
is at $m = 12$. The left three give $\delta_L = d((2,3),(3,4)) = \sqrt{2} \approx 1.414$; the right three give
$\delta_R = d((12,10),(12,30)) = 20$. So $\delta \approx 1.414$, and the strip $10.59 < x < 13.41$ contains only
$(12, 10)$ and $(12, 30)$, whose $y$-gap of 20 already exceeds $\delta$. Nothing in the strip beats $\delta$, and the
answer is $(2,3), (3,4)$.

The table shows the number of distance computations growing a little faster than $n$, against $n^2/2$ for brute
force: at $n = 10\,000$ about 15 thousand instead of 50 million.

**Lower bound.** In the algebraic decision-tree model, deciding whether $n$ numbers are all distinct needs
$\Omega(n \log n)$ operations (Ben-Or 1983), and the closest pair answers that question (distinct exactly when the
closest distance is positive), so $O(n \log n)$ is optimal in that model. Michael Rabin showed in 1976 that with
randomness and the floor function (bucketing points into a grid) one can do it in expected $O(n)$ time; that model
allows operations the decision-tree model does not. [Chapter 20](20-Computational-Geometry.md) returns to geometry.

## 11.7 The fast Fourier transform

*Level: advanced.*

Karatsuba multiplies numbers in $O(n^{1.585})$. Can we get all the way down to almost linear time? Yes, and the key is
to multiply **polynomials**, then treat a number as a polynomial in its base: $1234 = 4 + 3x + 2x^2 + 1x^3$ at
$x = 10$. Multiply two such polynomials, then carry, and you have the product of the numbers. The tool is the **fast
Fourier transform** (FFT), which Cooley and Tukey published in 1965 and which is among the most widely used
algorithms in science and engineering: it is inside audio and image compression, radio, medical imaging and the
solution of differential equations.

### Two ways to describe a polynomial

A polynomial of degree less than $n$,

$$
A(x) = a_0 + a_1 x + a_2 x^2 + \dots + a_{n-1} x^{n-1},
$$

can be stored by its $n$ **coefficients** $a_0, \dots, a_{n-1}$. Or it can be stored by its **values** at $n$
distinct points $x_0, \dots, x_{n-1}$: the list $A(x_0), \dots, A(x_{n-1})$. The two descriptions carry the same
information, because a polynomial of degree less than $n$ is determined by its values at $n$ distinct points (two such
polynomials that agree at $n$ points differ by a polynomial of degree less than $n$ with $n$ roots, which must be
zero).

Each description is good at something:

| operation | coefficients | values at the same points |
|---|---|---|
| evaluate at one point | $O(n)$ (Horner's rule) | hard |
| add two polynomials | $O(n)$ | $O(n)$ |
| multiply two polynomials | $O(n^2)$ (every $a_i b_j$) | $O(n)$: multiply the values pointwise |

Multiplication in value form is trivial: $(AB)(x_k) = A(x_k)\, B(x_k)$. The product $C = AB$ of two polynomials of
degree less than $n$ has degree less than $2n - 1$, so we need values at $2n - 1$ points (in practice, a power of two
$N \ge 2n - 1$). The plan is:

1. **Evaluate** $A$ and $B$ at $N$ points.
2. **Multiply** the values pointwise: $N$ multiplications.
3. **Interpolate**: recover the coefficients of $C$ from its $N$ values.

Done naively, step 1 costs $O(N^2)$ (each of $N$ evaluations is $O(N)$), and so does step 3. The FFT does both in
$O(N \log N)$ by choosing the points cleverly.

### Roots of unity

The clever points are the complex **$N$-th roots of unity**: the $N$ complex numbers $z$ with $z^N = 1$. They are

$$
\omega_N^k = e^{2\pi i k / N} = \cos\frac{2\pi k}{N} + i \sin\frac{2\pi k}{N}, \qquad k = 0, 1, \dots, N - 1,
$$

evenly spaced around the unit circle, where $\omega_N = e^{2\pi i/N}$ is the **principal** $N$-th root (Euler's
formula $e^{i\theta} = \cos\theta + i\sin\theta$ is the bridge; see the complex-numbers chapter of
[https://math.akadian.ca/books/algebra/](https://math.akadian.ca/books/algebra/)). For $N = 4$ they are $1, i, -1, -i$.
Three facts make them special:

- **Cancellation:** $\omega_{dN}^{dk} = \omega_N^k$, since both equal $e^{2\pi i k/N}$.
- **Halving lemma:** if $N$ is even, the squares of the $N$-th roots of unity are the $(N/2)$-th roots of unity, each
  appearing twice. Indeed $(\omega_N^k)^2 = \omega_N^{2k} = \omega_{N/2}^k$, and $\omega_N^{k + N/2} = -\omega_N^k$
  (because $\omega_N^{N/2} = e^{\pi i} = -1$), so $\omega_N^k$ and $\omega_N^{k+N/2}$ have the same square.
- **Summation lemma:** for an integer $j$ not divisible by $N$, $\sum_{k=0}^{N-1} \omega_N^{jk} = 0$. It is a
  geometric series with ratio $r = \omega_N^j \ne 1$, so it equals $(r^N - 1)/(r - 1) = (1 - 1)/(r - 1) = 0$.

### The recursion

The **discrete Fourier transform** (DFT) of the coefficient list $a = (a_0, \dots, a_{N-1})$ is the list of values
$y_k = A(\omega_N^k)$ for $k = 0, \dots, N - 1$. Split $A$ into its even and odd coefficients:

$$
A(x) = A_{\text{even}}(x^2) + x\, A_{\text{odd}}(x^2),
$$

where $A_{\text{even}}(z) = a_0 + a_2 z + a_4 z^2 + \dots$ and $A_{\text{odd}}(z) = a_1 + a_3 z + a_5 z^2 + \dots$, each of
degree less than $N/2$. We need $A$ at the $N$-th roots of unity, so we need $A_{\text{even}}$ and $A_{\text{odd}}$ at
their squares, and by the halving lemma those are just the $N/2$ values $\omega_{N/2}^k$. So two DFTs of size $N/2$,
$E_k = A_{\text{even}}(\omega_{N/2}^k)$ and $O_k = A_{\text{odd}}(\omega_{N/2}^k)$, give everything:

$$
y_k = E_k + \omega_N^k\, O_k, \qquad y_{k + N/2} = E_k - \omega_N^k\, O_k, \qquad 0 \le k < N/2.
$$

The second line uses $\omega_N^{k+N/2} = -\omega_N^k$ and the fact that $E$ and $O$ repeat with period $N/2$. This pair
of formulas, one sum and one difference sharing the product $\omega_N^k O_k$, is called a **butterfly**, from the
shape it makes when drawn.

**Theorem (Cooley-Tukey).** For $N$ a power of two, the recursion computes the DFT in $\Theta(N \log N)$ arithmetic
operations on complex numbers.

*Proof.* Correctness: by strong induction on $N$, the two recursive calls return $E$ and $O$; the butterfly formulas
were just derived from $A(x) = A_{\text{even}}(x^2) + x A_{\text{odd}}(x^2)$ and the halving lemma. For $N = 1$ the DFT
of $(a_0)$ is $(a_0)$. Time: two half-size calls and $N/2$ butterflies of $O(1)$ each, so
$T(N) = 2T(N/2) + \Theta(N) = \Theta(N \log N)$ by the master theorem's middle case. $\square$

<figure class="mars-fig" markdown="0">
<svg viewBox="0 0 640 270" role="img" aria-label="FFT butterfly diagram for the coefficients 1 2 3 4. Inputs a0 equals 1 and a2 equals 3 enter a size-two FFT giving 4 and minus 2; a1 equals 2 and a3 equals 4 give 6 and minus 2. A second stage of crossing lines combines them into outputs 10, minus 2 plus 2i, minus 2, and minus 2 minus 2i, with the factor minus i on the lower odd line.">
<g font-size="13" fill="currentColor" text-anchor="middle">
<text x="62" y="20">input</text>
<text x="280" y="20">two size-2 DFTs</text>
<text x="545" y="20">output</text>
</g>
<g stroke="currentColor" stroke-width="1.2">
<line x1="100" y1="50" x2="240" y2="50"/>
<line x1="100" y1="50" x2="240" y2="100"/>
<line x1="100" y1="100" x2="240" y2="50"/>
<line x1="100" y1="100" x2="240" y2="100"/>
<line x1="100" y1="150" x2="240" y2="150"/>
<line x1="100" y1="150" x2="240" y2="200"/>
<line x1="100" y1="200" x2="240" y2="150"/>
<line x1="100" y1="200" x2="240" y2="200"/>
</g>
<g stroke="#eea66f" stroke-width="2">
<line x1="320" y1="50" x2="470" y2="50"/>
<line x1="320" y1="50" x2="470" y2="150"/>
<line x1="320" y1="150" x2="470" y2="50"/>
<line x1="320" y1="150" x2="470" y2="150"/>
</g>
<g stroke="#9cc9ea" stroke-width="2">
<line x1="320" y1="100" x2="470" y2="100"/>
<line x1="320" y1="100" x2="470" y2="200"/>
<line x1="320" y1="200" x2="470" y2="100"/>
<line x1="320" y1="200" x2="470" y2="200"/>
</g>
<g font-family="monospace" font-size="14" fill="currentColor">
<text x="95" y="55" text-anchor="end">a0 = 1</text>
<text x="95" y="105" text-anchor="end">a2 = 3</text>
<text x="95" y="155" text-anchor="end">a1 = 2</text>
<text x="95" y="205" text-anchor="end">a3 = 4</text>
<text x="280" y="55" text-anchor="middle">E0 = 4</text>
<text x="280" y="105" text-anchor="middle">E1 = -2</text>
<text x="280" y="155" text-anchor="middle">O0 = 6</text>
<text x="280" y="205" text-anchor="middle">O1 = -2</text>
<text x="478" y="55">y0 = 10</text>
<text x="478" y="105">y1 = -2+2i</text>
<text x="478" y="155">y2 = -2</text>
<text x="478" y="205">y3 = -2-2i</text>
</g>
<g font-size="13" fill="currentColor" text-anchor="middle">
<text x="320" y="232">times w = -i on the O1 line; the lower output of each butterfly takes a minus sign</text>
<text x="320" y="255">y(k) = E(k) + w^k O(k),   y(k + N/2) = E(k) - w^k O(k)</text>
</g>
</svg>
<figcaption>Figure 11.3. The FFT of (1, 2, 3, 4) as butterflies, with the program's sign convention w = e^(-2πi/4) = -i. Each stage halves the problem; there are log2 N stages of N/2 butterflies.</figcaption>
</figure>

### A trace by hand

The program uses the conjugate root $w = e^{-2\pi i/N}$ instead of $\omega_N$, the usual convention in engineering;
everything above holds with $w$ in place of $\omega_N$, because $w$ is also a primitive $N$-th root of unity. Take
$a = (1, 2, 3, 4)$, $N = 4$, $w = -i$.

- Even coefficients $(1, 3)$: their size-2 DFT is $(1 + 3, 1 - 3) = (4, -2)$.
- Odd coefficients $(2, 4)$: $(6, -2)$.
- $k = 0$: $w^0 = 1$, $y_0 = 4 + 6 = 10$, $y_2 = 4 - 6 = -2$.
- $k = 1$: $w^1 = -i$, $w O_1 = (-i)(-2) = 2i$, $y_1 = -2 + 2i$, $y_3 = -2 - 2i$.

Check $y_1$ directly: $A(-i) = 1 + 2(-i) + 3(-i)^2 + 4(-i)^3 = 1 - 2i - 3 + 4i = -2 + 2i$. Correct.

### Going back: the inverse DFT

The DFT is a matrix-vector product $y = V a$, where $V_{kj} = \omega_N^{kj}$ is a **Vandermonde matrix**.

**Theorem.** The inverse of $V$ has entries $(V^{-1})_{jk} = \omega_N^{-jk} / N$.

*Proof.* The $(j, j')$ entry of $V^{-1} V$ with that formula is
$\frac{1}{N} \sum_{k=0}^{N-1} \omega_N^{-jk} \omega_N^{kj'} = \frac{1}{N} \sum_{k=0}^{N-1} \omega_N^{k(j' - j)}$.
If $j = j'$ every term is 1 and the entry is 1. Otherwise $0 < |j' - j| < N$, so $N$ does not divide $j' - j$ and the
summation lemma makes the entry 0. $\square$

So interpolation is just another DFT, run with $\omega_N^{-1}$ in place of $\omega_N$, followed by dividing by $N$. The
same $O(N \log N)$ algorithm does it; in the code, `invert=True` flips the sign of the exponent.

### Multiplying polynomials and big numbers

```python
--8<-- "books/algorithms/ch11_fft.py"
```

```
FFT of [1, 2, 3, 4] = [(10+0j), (-2+2j), (-2+0j), (-2-2j)]
(1 + 2x + 3x^2)(4 + 5x) coefficients: [4, 13, 22, 15]  naive: [4, 13, 22, 15]
1234 * 5678 = 7006652
50 random polynomial products agree with the naive method: True
two 3000-bit numbers (about 900 digits) multiplied by FFT correctly: True
```

**Theorem.** Two polynomials of degree less than $n$ can be multiplied in $O(n \log n)$ arithmetic operations.

*Proof.* Pad both to length $N$, the least power of two at least $2n - 1$, so $N < 4n$. Two forward FFTs, $N$ pointwise
products and one inverse FFT cost $O(N \log N) = O(n \log n)$. Correctness: the product has degree less than $N$, so
its $N$ values determine it, and the pointwise products are exactly its values at the roots of unity. $\square$

For integers, the program writes each number's decimal digits as coefficients, multiplies the polynomials, and then
**carries**: the coefficient $c_k$ may exceed 9, so keep $c_k \bmod 10$ and pass $\lfloor c_k / 10 \rfloor$ up to the next
position.

### Honest caveats

- **Rounding.** The code computes with floating-point complex numbers and rounds the final coefficients to integers.
  That is exact as long as the rounding errors stay below one half, which holds for moderate sizes and small
  coefficients (here, decimal digits). For very large inputs, implementations either split into smaller digits, use
  careful error bounds, or avoid floating point entirely with the **number-theoretic transform**, the same algorithm
  over integers modulo a prime $p$ that has $N$-th roots of unity. [Chapter 19](19-Number-Theoretic-Algorithms.md)
  builds it.
- **Bit complexity.** "$O(n \log n)$ arithmetic operations" counts operations on numbers of growing precision. For
  integer multiplication measured in bit operations, Arnold Schönhage and Volker Strassen gave
  $O(n \log n \log \log n)$ in 1971, and David Harvey and Joris van der Hoeven proved $O(n \log n)$ in "Integer
  multiplication in time $O(n \log n)$" (Annals of Mathematics, 2021). Whether $O(n \log n)$ is optimal is open.
- **In practice.** NumPy has `numpy.fft`, and the FFTW library is a widely used fast implementation. Real FFTs are
  iterative rather than recursive (they reorder the input by reversing the bits of each index, then run the
  butterflies level by level in place) and handle sizes that are not powers of two.

### History

Carl Friedrich Gauss used the same even-odd splitting around 1805 to interpolate the orbits of asteroids, in work
published only after his death; Michael Heideman, Don Johnson and Sidney Burrus traced this in "Gauss and the history
of the fast Fourier transform" (1984). The idea was rediscovered several times before James Cooley and John Tukey's
1965 paper, "An algorithm for the machine calculation of complex Fourier series", made it widely known at the moment
when digital computers could use it.

## Check yourself

??? question "1. Count the inversions of [2, 4, 1, 3, 5] by hand, then by the merge-and-count method."

    By hand: the inverted pairs are (2, 1), (4, 1) and (4, 3), so 3. By merge-and-count: split into [2, 4] and
    [1, 3, 5]. [2, 4] has 0 inversions; [1, 3, 5] has 0 (its pieces [1] and [3, 5] merge with no right element taken
    early). Merging [2, 4] with [1, 3, 5]: take 1 (2 left elements waiting, add 2), take 2, take 3 (1 waiting, add 1),
    take 4, take 5. Cross count 3, total 3.

??? question "2. What is the largest possible number of inversions in a list of n distinct numbers, and which list has it?"

    $\binom{n}{2} = n(n-1)/2$, reached exactly when every pair is inverted, which means the list is in decreasing
    order. The program checks this for $n = 2000$: 1 999 000.

??? question "3. Run Kadane's algorithm by hand on [5, -9, 6, -2, 3]."

    $E$: 5, then $5 - 9 = -4$, then restart at 6 (because $-4 < 0$), then $6 - 2 = 4$, then $4 + 3 = 7$. Best so
    far: 5, 5, 6, 6, 7. The answer is 7, from the slice [6, -2, 3].

??? question "4. Multiply 47 by 86 with Karatsuba's method, showing the three products."

    $a = 4$, $b = 7$, $c = 8$, $d = 6$. $ac = 32$, $bd = 42$, $(a+b)(c+d) = 11 \times 14 = 154$, so
    $ad + bc = 154 - 32 - 42 = 80$. Then $xy = 32 \cdot 100 + 80 \cdot 10 + 42 = 4042$. Check: $47 \times 86 = 4042$.

??? question "5. Solve T(1) = 1, T(n) = 3T(n/2) + n exactly for n a power of two."

    Unroll: $T(n) = n + 3(n/2) + 9(n/4) + \dots + 3^{k-1}(n/2^{k-1}) + 3^k$ with $k = \log_2 n$, which is
    $n \sum_{i=0}^{k-1} (3/2)^i + 3^k = n \cdot 2((3/2)^k - 1) + 3^k = 2 \cdot 3^k - 2n + 3^k = 3 n^{\log_2 3} - 2n$.
    Check: $T(2) = 3 + 2 = 5 = 3 \cdot 3 - 4$, and $T(4) = 15 + 4 = 19 = 3 \cdot 9 - 8$.

??? question "6. Toom-3 splits each number into three parts and multiplies with five products of one-third size. What exponent does it achieve? Why can't one do it with fewer than five?"

    $T(n) = 5T(n/3) + O(n)$ gives $\Theta(n^{\log_3 5}) \approx n^{1.465}$. The product of two polynomials of
    degree 2 (three parts each) has degree 4, so it has five coefficients, and five values determine it: Toom-Cook
    evaluates both at five points and multiplies the values. Fewer than five products cannot determine five unknown
    coefficients in this evaluate-and-interpolate scheme.

??? question "7. Verify Strassen's formula for C11 by expanding M1 + M4 - M5 + M7."

    $M_1 = A_{11}B_{11} + A_{11}B_{22} + A_{22}B_{11} + A_{22}B_{22}$; $M_4 = A_{22}B_{21} - A_{22}B_{11}$;
    $M_5 = A_{11}B_{22} + A_{12}B_{22}$; $M_7 = A_{12}B_{21} + A_{12}B_{22} - A_{22}B_{21} - A_{22}B_{22}$.
    Adding $M_1 + M_4 - M_5 + M_7$, the terms $A_{11}B_{22}$, $A_{22}B_{11}$, $A_{22}B_{22}$, $A_{22}B_{21}$ and
    $A_{12}B_{22}$ all cancel, leaving $A_{11}B_{11} + A_{12}B_{21}$, which is $C_{11}$. No product had its factors
    swapped.

??? question "8. In one dimension, why is it enough to compare each point with the next one in sorted order? What is the 'strip lemma' constant there?"

    If $p < q < r$ on a line, then $|r - p| = |r - q| + |q - p| > |q - p|$, so a pair that is not adjacent in sorted
    order is never strictly the closest. The constant is 1: each point needs comparing only with its successor.

??? question "9. Write code: count the 'significant inversions' of a list, pairs i < j with a[i] > 2 a[j], in O(n log n)."

    Count before merging, with two pointers on the sorted halves; the pointer into the right half only moves
    forward, because the left half is sorted.

    ```python
    import heapq

    def significant_inversions(a):
        if len(a) <= 1:
            return list(a), 0
        mid = len(a) // 2
        left, x = significant_inversions(a[:mid])
        right, y = significant_inversions(a[mid:])
        z = j = 0
        for v in left:                      # left is sorted, so j never moves back
            while j < len(right) and v > 2 * right[j]:
                j += 1
            z += j                          # right[:j] are all < v/2
        return list(heapq.merge(left, right)), x + y + z

    print(significant_inversions([5, 1, 4, 2, 3])[1])   # 2: (5, 1) and (5, 2)
    ```

    The counting pass and the merge are both linear, so $T(n) = 2T(n/2) + O(n) = O(n \log n)$. Checked against a
    brute-force count on 200 random lists.

??? question "10. Compute the DFT of (1, 1, 1, 1) and of (1, 0, 0, 0) without the program. What does this say about the inverse?"

    $(1, 1, 1, 1)$ is $A(x) = 1 + x + x^2 + x^3$. At $x = 1$ it is 4; at any other 4th root of unity it is 0 by the
    summation lemma. So the DFT is $(4, 0, 0, 0)$. $(1, 0, 0, 0)$ is the constant 1, with DFT $(1, 1, 1, 1)$. The two
    are inverse to each other up to the factor $N = 4$: the inverse DFT of $(4, 0, 0, 0)$ is $(1,1,1,1)$ after dividing
    by 4, as the inverse theorem says.

??? question "11. Prove that Kadane's algorithm cannot be beaten asymptotically: every correct algorithm reads all n entries."

    Take $n \ge 2$ and suppose an algorithm, on some input, never reads position $k$, and reports the slice $S$.
    Let $M$ be larger than twice the sum of the absolute values of all the other entries. Change only $a_k$; the
    algorithm reads exactly the same values, so it still reports $S$.

    - If $S$ does not contain $k$, set $a_k = M$. The one-element slice $[a_k]$ has sum $M$, more than any slice
      avoiding $k$ can reach, so $S$ is no longer best.
    - If $S$ contains $k$, set $a_k = -M$. Then the sum of $S$ is less than $-M/2$, while any single other entry is at
      least $-M/2$, so again $S$ is not best.

    Either way some input fools the algorithm. So every correct algorithm reads all $n$ entries, which is $\Omega(n)$
    work, and Kadane's $O(n)$ is optimal.

## What you learned

- Divide and conquer means divide, conquer recursively, combine; the cost is a recurrence
  $T(n) = aT(n/b) + f(n)$, solved by the recursion tree or the master theorem.
- The power is in the combine step: counting inversions while merging, or gluing a best suffix to a best prefix.
- Saving one product per level changes the exponent: four products to three gives Karatsuba's $n^{1.585}$, eight to
  seven gives Strassen's $n^{2.807}$.
- Geometry can make the combine step cheap: the strip lemma limits each point to seven comparisons, giving the
  closest pair in $O(n \log n)$.
- The FFT evaluates a polynomial at the $N$-th roots of unity in $O(N \log N)$ using the halving lemma, its inverse is
  the same algorithm with the conjugate root, and together they multiply polynomials and big integers fast.
- Divide and conquer is not always best: Kadane's scan beats it for maximum subarray, and overlapping pieces call for
  dynamic programming.

**Next:** [Chapter 12](12-Greedy-Algorithms.md), algorithms that build an answer one irrevocable choice at a time, and
how to prove that the choices are safe.

## Further reading

- T. H. Cormen, C. E. Leiserson, R. L. Rivest and C. Stein, *Introduction to Algorithms*, 4th ed., 2022: chapter 4
  (divide and conquer, Strassen, the master theorem) and chapter 30 (polynomials and the FFT).
- J. Kleinberg and É. Tardos, *Algorithm Design*, 2005: chapter 5 (inversions, closest pair, integer multiplication,
  convolutions and the FFT).
- J. Bentley, *Programming Pearls*, 1986 (2nd ed. 2000): column 8, the maximum subarray story.
- A. Karatsuba and Yu. Ofman, "Multiplication of many-digital numbers by automatic computers", *Doklady Akademii Nauk
  SSSR*, 1962; A. A. Karatsuba, "The complexity of computations", *Proceedings of the Steklov Institute of
  Mathematics*, 1995.
- V. Strassen, "Gaussian elimination is not optimal", *Numerische Mathematik* 13, 1969.
- M. I. Shamos and D. Hoey, "Closest-point problems", *16th Annual Symposium on Foundations of Computer Science*, 1975.
- J. W. Cooley and J. W. Tukey, "An algorithm for the machine calculation of complex Fourier series", *Mathematics of
  Computation* 19, 1965; M. T. Heideman, D. H. Johnson and C. S. Burrus, "Gauss and the history of the fast Fourier
  transform", *IEEE ASSP Magazine*, 1984.
- D. Harvey and J. van der Hoeven, "Integer multiplication in time $O(n \log n)$", *Annals of Mathematics* 193, 2021.
- D. E. Knuth, *The Art of Computer Programming*, Vol. 2, *Seminumerical Algorithms*, 3rd ed., 1997: section 4.3.3 on
  fast multiplication.
- On this site: [Merge sort](../../sorting/merge-sort.md), [Binary search](../../searching/binary-search.md),
  [Recursion](../../foundations/recursion.md), [Big-O](../../foundations/big-o.md),
  [Chapter 3](03-Recursion-and-Induction.md), [Chapter 5](05-Sorting-by-Comparison.md),
  [Chapter 19](19-Number-Theoretic-Algorithms.md), [Chapter 20](20-Computational-Geometry.md).
