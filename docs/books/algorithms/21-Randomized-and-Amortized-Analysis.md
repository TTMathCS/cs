# 21. Randomized and amortized analysis

*Some of the best algorithms in this book flip coins, and some of the best data structures are allowed to be slow
now and then. Neither is fast on every single step, yet both are fast in a sense you can prove: randomized quicksort
is fast on average over its own coin flips, whatever the input, and a splay tree is fast on average over any long
run of operations, whatever the operations. This chapter makes both kinds of "on average" exact. You will learn the
small toolkit of probability that analysing algorithms needs (expectation, indicator variables, tail bounds), use it
to analyse quicksort, quickselect, Karger's minimum-cut algorithm, shuffling and sampling, and then go back to
amortized analysis and prove the bound for splay trees that Chapter 8 could only state.*

!!! abstract "In this chapter"
    **You will learn:**

    - the difference between Las Vegas and Monte Carlo algorithms, and how to turn one kind into the other
    - expectation, its linearity, and the indicator-variable trick that analyses almost every randomized algorithm
    - the exact expected number of comparisons of randomized quicksort, and a linear bound for quickselect
    - the Markov, Chebyshev and Chernoff tail bounds, and how they make "usually fast" into "almost always fast"
    - Karger's contraction algorithm for minimum cuts, and amplification by repetition
    - the Fisher-Yates shuffle and reservoir sampling, each proved exactly uniform
    - the potential method in depth: the access lemma for splay trees and a dynamic table that also shrinks

    **You need:** [Chapter 4](04-Lists-Stacks-and-Queues.md) (dynamic arrays and the aggregate, accounting and
    potential methods), [Chapter 5](05-Sorting-by-Comparison.md) (quicksort),
    [Chapter 6](06-Sorting-in-Linear-Time-and-Selection.md) (quickselect),
    [Chapter 8](08-Trees-and-Balanced-Search-Trees.md) (binary search trees, rotations, splay trees) and
    [Chapter 10](10-Union-Find-and-Range-Queries.md) (union-find, used inside Karger's algorithm). Basic counting
    and probability help; [https://math.akadian.ca/books/](https://math.akadian.ca/books/) has the background.

    **Levels:** 21.1 and 21.5 are intermediate; 21.2 to 21.4 are advanced; 21.6 is advanced to expert.

## 21.1 Las Vegas, Monte Carlo, and the tools of expectation

Why would an algorithm ever want to flip a coin? Think about quicksort with the last element as pivot. On a list
that is already sorted it makes $n(n-1)/2$ comparisons, and sorted inputs are common in real life. Whatever fixed
rule you choose for the pivot, somebody can build an input that hits the bad case every time. If the algorithm
chooses the pivot **at random**, no input is bad any more: the bad behaviour now depends on the algorithm's own
luck, not on the input, and we can calculate how unlikely bad luck is.

A **randomized algorithm** is an algorithm that may, at any step, ask for a random number (for example "give me an
integer between 1 and $n$, each equally likely") and use it to decide what to do. Its running time, and sometimes
its answer, become **random variables**: quantities that depend on the random choices. There are two kinds.

- A **Las Vegas** algorithm always gives the right answer; only its running time is random. Randomized quicksort
  is Las Vegas: it always sorts, and the coin flips decide only how many comparisons it makes.
- A **Monte Carlo** algorithm runs within a fixed time bound, but may give a wrong answer with some (small)
  probability. The Miller-Rabin primality test of [Chapter 19](19-Number-Theoretic-Algorithms.md) is Monte Carlo:
  it may call a composite number "probably prime". So is one run of Karger's minimum-cut algorithm (21.4).

The names are jokes about casinos. "Monte Carlo" for random sampling goes back to the Los Alamos physicists of the
1940s, and Nicholas Metropolis and Stanislaw Ulam's paper "The Monte Carlo Method" (1949) made it standard. The name
"Las Vegas" is usually credited to László Babai (1979), who needed a word for randomized algorithms that never lie.
Michael Rabin's survey "Probabilistic Algorithms" (1976) is often taken as the moment randomized algorithms became a
field of their own.

You can turn one kind into the other.

- **Las Vegas to Monte Carlo.** Suppose a Las Vegas algorithm has expected running time $T$. Stop it after $2T$
  steps and answer "don't know" if it has not finished. By Markov's inequality (21.3) the probability it had not
  finished is at most $1/2$. Now it always runs in time $2T$, but may fail.
- **Monte Carlo to Las Vegas.** If a wrong answer can be *checked* quickly, repeat the Monte Carlo algorithm until
  the check passes. If each run succeeds with probability $q$, the expected number of runs is $1/q$ (shown below).

Notice where the randomness lives. In **average-case analysis** (as for plain quicksort on a random input) the
input is random and the algorithm is fixed; the conclusion is only as good as the assumption about inputs. In a
**randomized algorithm** the input is fixed, as bad as an adversary likes, and the algorithm is random. Every bound
in this chapter holds for *every* input.

### Probability in six lines

We need only finite (or countable) probability. A **sample space** is the set of all outcomes of the random choices
(for one die, $\{1,2,3,4,5,6\}$), each outcome $\omega$ with a probability $P(\omega) \ge 0$, all summing to 1. An
**event** is a set of outcomes; its probability is the sum of theirs. A **random variable** $X$ is a number computed
from the outcome. Its **expectation** (mean) is the probability-weighted average of its values:

$$
E[X] = \sum_{\omega} P(\omega)\, X(\omega) = \sum_{x} x \cdot P(X = x).
$$

Two events $A$ and $B$ are **independent** when $P(A \cap B) = P(A)\,P(B)$: knowing one happened tells you nothing
about the other. Separate coin flips are independent; that is all we assume about the random-number source.

### Linearity of expectation

**Theorem (linearity).** For any random variables $X$ and $Y$ and any numbers $a$, $b$:
$E[aX + bY] = a\,E[X] + b\,E[Y]$. *No independence is needed.*

*Proof.* Expand the definition and split the sum:

$$
E[aX+bY] = \sum_\omega P(\omega)\,(aX(\omega) + bY(\omega)) = a\sum_\omega P(\omega)X(\omega) + b\sum_\omega P(\omega)Y(\omega) = aE[X] + bE[Y].
$$

That is the whole proof, and it is the most used fact in this chapter. It says that to find the expected *total*
of many things, you can find the expected value of each thing separately and add, even when the things depend on
each other in complicated ways.

### Indicator variables

An **indicator variable** $I_A$ of an event $A$ is 1 if $A$ happens and 0 otherwise. Its expectation is the
probability of the event:

$$
E[I_A] = 1 \cdot P(A) + 0 \cdot P(\text{not } A) = P(A).
$$

The trick: to find the expected number of times something happens, write the count as a sum of indicators, one per
place it could happen, and use linearity. Each indicator only needs one probability.

**Example 1: new records.** Shuffle the numbers $1, \dots, n$ into a random order and read them left to right. Call
position $i$ a **record** if its value is larger than everything before it. (This is the "hiring problem" of CLRS:
interview candidates in random order and hire each one who beats everyone so far.) How many records do you expect?

Let $I_i$ indicate "position $i$ is a record". Among the first $i$ values, each is equally likely to be the largest,
so $P(I_i = 1) = 1/i$. By linearity,

$$
E[\text{records}] = \sum_{i=1}^{n} \frac{1}{i} = H_n \approx \ln n + 0.577,
$$

the $n$-th **harmonic number** ([Chapter 2](02-Measuring-Cost.md) showed $H_n$ is between $\ln n$ and
$\ln n + 1$). The records are *not* independent of each other, and we never needed them to be.

**Example 2: fixed points.** In a random permutation of $n$ items, how many items stay in their own place? Let
$I_i$ indicate "item $i$ is at position $i$"; its probability is $1/n$. So the expected number of fixed points is
$n \cdot (1/n) = 1$, for every $n$. Computing the full distribution is much harder; the expectation takes one line.

**Example 3: birthday pairs.** Put $k$ people in a room, each with a birthday uniform over 365 days, independently.
For each of the $\binom{k}{2}$ pairs, the indicator "this pair shares a birthday" has probability $1/365$. So the
expected number of sharing pairs is $\binom{k}{2}/365$. For $k = 28$ that is $378/365 > 1$. The same count tells you
how many collisions to expect when you put $k$ keys into a hash table with $m$ slots: $\binom{k}{2}/m$ (see
[Chapter 7](07-Searching-and-Hashing.md)).

**Example 4: waiting for a success.** Flip a coin that lands heads with probability $p$ until the first head. Let
$N$ be the number of flips. Then $N \ge i$ exactly when the first $i-1$ flips are tails, which has probability
$(1-p)^{i-1}$. Since $N = \sum_{i \ge 1} I_{N \ge i}$ (a number $N$ is the count of $i$ from 1 to $N$),

$$
E[N] = \sum_{i=1}^{\infty} P(N \ge i) = \sum_{i=1}^{\infty} (1-p)^{i-1} = \frac{1}{1-(1-p)} = \frac{1}{p}.
$$

This is the "repeat until success" cost used above: a test that succeeds with probability $q$ is expected to need
$1/q$ tries. A random variable like $N$ is called **geometric**.

The program checks all four by simulation.

```python
--8<-- "books/algorithms/ch21_expectation.py"
```

```
Left-to-right maxima ('new record' moments) of a random permutation: E = H_n
  n =   5: H_n = 2.2833   measured 2.2853
  n =  10: H_n = 2.9290   measured 2.9272
  n = 100: H_n = 5.1874   measured 5.1768

Fixed points of a random permutation: E = 1 for every n
  n =    3: measured 0.9830
  n =   10: measured 0.9840
  n = 1000: measured 1.0025

Pairs of people sharing a birthday, k people and 365 days: E = C(k,2)/365
  k = 10: predicted 0.1233   measured 0.1228
  k = 23: predicted 0.6932   measured 0.6914
  k = 28: predicted 1.0356   measured 1.0362
  k = 50: predicted 3.3562   measured 3.4156

Flips of a coin with P(head) = p until the first head: E = 1/p
  p = 0.5: predicted 2.0   measured 2.014
  p = 0.1: predicted 10.0   measured 9.971
```

A word on the random numbers themselves. Python's `random` module is a **pseudorandom** generator (the Mersenne
Twister): a deterministic program whose output passes statistical tests. The analyses in this chapter assume truly
independent uniform choices; for algorithms (not for cryptography) good pseudorandom generators behave
indistinguishably in practice. The fixed seeds in the programs make every run print the same numbers.

## 21.2 Randomized quicksort and quickselect, analysed fully

*Level: advanced.* [Chapter 5](05-Sorting-by-Comparison.md) proved that randomized quicksort makes $O(n \log n)$
comparisons on average. Now we find the exact number. The [quicksort reference page](../../sorting/quicksort.md)
has the code in three languages and an animation.

Here is the algorithm we analyse. Assume the $n$ keys are distinct (ties only make things easier with three-way
partitioning). To sort a list: if it has at most one element, stop; otherwise pick a pivot uniformly at random from
the list, compare every other element with it once to split the list into "smaller" and "larger", and sort the two
parts the same way. A list of length $\ell$ costs $\ell - 1$ comparisons to split.

### The recurrence

Let $C(n)$ be the expected number of comparisons on $n$ keys. The pivot's **rank** (its position in sorted order)
is uniform from 1 to $n$. If the rank is $k$, the parts have $k-1$ and $n-k$ elements. So

$$
C(n) = (n - 1) + \frac{1}{n}\sum_{k=1}^{n} \big(C(k-1) + C(n-k)\big) = (n-1) + \frac{2}{n}\sum_{j=0}^{n-1} C(j),
$$

with $C(0) = C(1) = 0$. By hand: $C(2) = 1 + \tfrac{2}{2}(0 + 0) = 1$. For $C(3)$, the pivot is the middle key with
probability $1/3$ (cost 2, then two parts of size 1) or an extreme key with probability $2/3$ (cost 2, then one part
of size 2, costing 1 more): $C(3) = \tfrac13 \cdot 2 + \tfrac23 \cdot 3 = \tfrac83$, which is what the recurrence
gives: $2 + \tfrac23(0 + 0 + 1) = \tfrac83$. Solving the recurrence in general is possible (multiply by $n$, subtract
the same equation for $n-1$), but indicator variables give the answer more directly and explain it.

### The indicator proof

Name the keys in sorted order $z_1 < z_2 < \dots < z_n$. Two keys are compared at most once, because every
comparison involves the current pivot, and a pivot is never looked at again after its partition. So the number of
comparisons is

$$
X = \sum_{1 \le i < j \le n} X_{ij}, \qquad X_{ij} = \text{indicator that } z_i \text{ and } z_j \text{ are compared}.
$$

**Lemma.** $P(z_i \text{ and } z_j \text{ are compared}) = \dfrac{2}{j - i + 1}$.

*Proof.* Look at the block $Z_{ij} = \{z_i, z_{i+1}, \dots, z_j\}$, which has $j - i + 1$ keys. As long as no pivot
has been chosen from $Z_{ij}$, all of $Z_{ij}$ stays together in the same sublist: a pivot smaller than $z_i$ or
larger than $z_j$ sends the whole block to the same side. Consider the first moment a pivot is chosen from inside
$Z_{ij}$. At that moment the whole block is in the sublist being split, and the pivot is uniform over that sublist,
so given that it lands in $Z_{ij}$ it is uniform over $Z_{ij}$.

- If that first pivot is $z_i$ or $z_j$, the two are compared (every element of the sublist meets the pivot).
- If it is some $z_k$ strictly between them, $z_i$ goes to the "smaller" side and $z_j$ to the "larger" side, and
  they are never in the same sublist again, so they are never compared.

So they are compared with probability $2/(j-i+1)$. $\square$

<figure class="mars-fig" markdown="0">
<svg viewBox="0 0 640 175" role="img" aria-label="Ten sorted keys z1 to z10 in a row. The block z3 to z7 is shaded. z3 and z7 are highlighted. If the first pivot chosen from the block is z3 or z7 they are compared; if it is z4, z5 or z6 they are separated and never compared.">
  <g font-size="13" text-anchor="middle" fill="currentColor">
    <rect x="20" y="30" width="50" height="36" rx="4" fill="none" stroke="currentColor" stroke-width="1.2"/>
    <text x="45" y="53">z1</text>
    <rect x="80" y="30" width="50" height="36" rx="4" fill="none" stroke="currentColor" stroke-width="1.2"/>
    <text x="105" y="53">z2</text>
    <rect x="140" y="30" width="50" height="36" rx="4" fill="#eea66f" fill-opacity="0.75" stroke="currentColor" stroke-width="1.2"/>
    <text x="165" y="53">z3</text>
    <rect x="200" y="30" width="50" height="36" rx="4" fill="#9cc9ea" fill-opacity="0.6" stroke="currentColor" stroke-width="1.2"/>
    <text x="225" y="53">z4</text>
    <rect x="260" y="30" width="50" height="36" rx="4" fill="#9cc9ea" fill-opacity="0.6" stroke="currentColor" stroke-width="1.2"/>
    <text x="285" y="53">z5</text>
    <rect x="320" y="30" width="50" height="36" rx="4" fill="#9cc9ea" fill-opacity="0.6" stroke="currentColor" stroke-width="1.2"/>
    <text x="345" y="53">z6</text>
    <rect x="380" y="30" width="50" height="36" rx="4" fill="#eea66f" fill-opacity="0.75" stroke="currentColor" stroke-width="1.2"/>
    <text x="405" y="53">z7</text>
    <rect x="440" y="30" width="50" height="36" rx="4" fill="none" stroke="currentColor" stroke-width="1.2"/>
    <text x="465" y="53">z8</text>
    <rect x="500" y="30" width="50" height="36" rx="4" fill="none" stroke="currentColor" stroke-width="1.2"/>
    <text x="525" y="53">z9</text>
    <rect x="560" y="30" width="50" height="36" rx="4" fill="none" stroke="currentColor" stroke-width="1.2"/>
    <text x="585" y="53">z10</text>
  </g>
  <path d="M 140 76 L 140 86 L 430 86 L 430 76" fill="none" stroke="currentColor" stroke-width="1.3"/>
  <text x="285" y="104" font-size="13" text-anchor="middle" fill="currentColor">block Z(3,7): 5 keys; pivots outside it never split it</text>
  <rect x="40" y="120" width="12" height="12" fill="#eea66f" fill-opacity="0.75" stroke="currentColor"/>
  <text x="60" y="131" font-size="13" fill="currentColor">first pivot from the block is z3 or z7: compared (2 chances in 5)</text>
  <rect x="40" y="145" width="12" height="12" fill="#9cc9ea" fill-opacity="0.6" stroke="currentColor"/>
  <text x="60" y="156" font-size="13" fill="currentColor">first pivot is z4, z5 or z6: z3 and z7 go to different sides, never compared</text>
</svg>
<figcaption>Figure 21.1. Why z3 and z7 are compared with probability 2/5. Only the first pivot drawn from their block matters.</figcaption>
</figure>

Now add up. Group the pairs by their distance $d = j - i$; there are $n - d$ pairs at distance $d$:

$$
\begin{aligned}
E[X] &= \sum_{i<j} \frac{2}{j-i+1} = \sum_{d=1}^{n-1} (n-d)\,\frac{2}{d+1} = \sum_{k=2}^{n} \frac{2(n+1-k)}{k} \\
&= 2(n+1)\sum_{k=2}^{n}\frac{1}{k} - 2(n-1) = 2(n+1)(H_n - 1) - 2(n-1) = 2(n+1)H_n - 4n .
\end{aligned}
$$

**Theorem.** Randomized quicksort on $n$ distinct keys makes exactly $2(n+1)H_n - 4n$ comparisons in expectation,
for every input order. Since $H_n = \ln n + O(1)$, this is $2n\ln n + O(n) \approx 1.386\, n \log_2 n$.

Check against the hand values: $n = 2$ gives $2 \cdot 3 \cdot \tfrac32 - 8 = 1$, and $n = 3$ gives
$2 \cdot 4 \cdot \tfrac{11}{6} - 12 = \tfrac83$. The constant $1.386$ is worth remembering: a random pivot costs about
39% more comparisons than the information-theoretic lower bound $\log_2 n! \approx n\log_2 n$ of Chapter 5. Choosing
the pivot as the median of three random keys lowers the constant (to about $1.188$, a classical result of the
analysis of quicksort variants; see Sedgewick's thesis and Knuth, TAOCP volume 3).

The lemma also explains *where* the comparisons go: neighbours $z_i, z_{i+1}$ are always compared (they must be,
or the algorithm could not know their order), while keys far apart in sorted order are rarely compared.

### Quickselect

[Chapter 6](06-Sorting-in-Linear-Time-and-Selection.md) introduced **quickselect** (Hoare's FIND, 1961): to find the
$k$-th smallest key, partition around a random pivot of rank $p$; if $p = k$ you are done, otherwise continue only in
the side that contains rank $k$. Let $T(n)$ be the largest expected number of comparisons over all $k$. If the pivot
has rank $p$, the side we keep has at most $\max(p - 1, n - p)$ keys, so

$$
T(n) \le (n - 1) + \frac{1}{n} \sum_{p=1}^{n} T\big(\max(p-1,\, n-p)\big).
$$

**Theorem.** $T(n) \le 4n$ for all $n \ge 1$.

*Proof by strong induction.* For $n = 1$ there is no comparison. Assume $T(m) \le 4m$ for all $m < n$. As $p$ runs
from 1 to $n$, the value $\max(p-1, n-p)$ takes each value from $\lceil n/2 \rceil$ to $n-1$ at most twice, so

$$
\sum_{p=1}^{n} \max(p-1, n-p) \le 2\sum_{m=\lfloor n/2 \rfloor}^{n-1} m \le \frac{3n^2}{4}.
$$

(For even $n$ the middle sum is exactly $2\big(\tfrac{3n^2}{8} - \tfrac{n}{4}\big) = \tfrac{3n^2}{4} - \tfrac{n}{2}$;
the odd case is similar.) Therefore $T(n) \le (n-1) + \frac{1}{n}\cdot 4 \cdot \frac{3n^2}{4} = 4n - 1 \le 4n$.
$\square$

So quickselect is linear in expectation, again for every input. The true constant is smaller. The program below
computes the exact expectation $Q(n, k)$ by its recurrence (pivot rank $p$ below $k$ leaves $Q(n-p, k-p)$, above $k$
leaves $Q(p-1, k)$). The worst rank is the median, where $Q(n, n/2)/n$ creeps up towards $2 + 2\ln 2 \approx 3.386$,
a result of Knuth (1971) for large $n$; for the minimum ($k = 1$) it is exactly $2n - 2H_n$, which matches the program's
last column. An indicator proof like quicksort's works here too: $z_i$ and $z_j$ are compared exactly when the first
pivot drawn from the block spanning $z_i$, $z_j$ *and* $z_k$ is $z_i$ or $z_j$ (Exercise 4).

```python
--8<-- "books/algorithms/ch21_quicksort_select.py"
```

```
Randomized quicksort: average comparisons against the exact expectation 2(n+1)H_n - 4n
  n =    2: exact      1.00   measured      1.00   deepest recursion seen 1
  n =    3: exact      2.67   measured      2.66   deepest recursion seen 2
  n =   10: exact     24.44   measured     24.40   deepest recursion seen 9
  n =  100: exact    647.85   measured    644.44   deepest recursion seen 19
  n = 1000: exact  10985.91   measured  10975.65   deepest recursion seen 27
  exact values as fractions: C(2) = 1  C(3) = 8/3  C(4) = 29/6

The pair (z_i, z_j) is compared with probability 2/(j - i + 1); n = 10, 100000 runs:
  z1, z2: predicted 1.0000   measured 1.0000
  z3, z4: predicted 1.0000   measured 1.0000
  z1, z3: predicted 0.6667   measured 0.6679
  z2, z7: predicted 0.3333   measured 0.3340
  z1, z10: predicted 0.2000   measured 0.1989

Randomized quickselect: exact expected comparisons, worst rank, against the bound 4n
  n =  10: worst rank k =   5, exact    19.27 = 1.927 n,  measured    19.28,  minimum (k = 1)   14.14
  n = 100: worst rank k =  50, exact   306.94 = 3.069 n,  measured   303.16,  minimum (k = 1)  189.63
  n = 200: worst rank k = 100, exact   640.10 = 3.201 n,  measured   634.14,  minimum (k = 1)  388.24
```

The "deepest recursion" column counts nested calls, including the calls on empty sublists. For $n = 1000$ the worst
of 300 runs went 27 levels deep, while $\log_2 1000 \approx 10$. The expectation says nothing about how often a run
is much worse than average. That is the job of the next section.

## 21.3 Tail bounds: Markov, Chebyshev, Chernoff

*Level: advanced.* An expectation is an average. A user who waits for one run of quicksort wants something
stronger: "the probability that this run takes more than twice the average is tiny". A **tail bound** is an upper
bound on the probability that a random variable is far from its mean. There are three standard ones, each using a
little more information about the variable and giving a much stronger answer.

### Markov's inequality

**Theorem (Markov).** If $X \ge 0$ and $a > 0$, then $P(X \ge a) \le E[X]/a$.

*Proof.* The indicator $I_{X \ge a}$ satisfies $a \cdot I_{X \ge a} \le X$ for every outcome (if $X \ge a$ the left
side is $a \le X$; otherwise it is $0 \le X$). Take expectations: $a\,P(X \ge a) \le E[X]$. $\square$

It needs only the mean and non-negativity, and it is weak: it says randomized quicksort exceeds ten times its
expected comparisons with probability at most $1/10$. But it is the seed of the other two. It is also what makes
the Las Vegas to Monte Carlo conversion of 21.1 work: $P(\text{time} \ge 2T) \le 1/2$.

### Chebyshev's inequality

The **variance** of $X$ is $\operatorname{Var}[X] = E[(X - \mu)^2]$, where $\mu = E[X]$: the average squared distance
from the mean. Its square root is the **standard deviation**. For a sum of *independent* variables the variances add
(the cross terms $E[(X_i - \mu_i)(X_j - \mu_j)]$ are zero when $X_i$ and $X_j$ are independent). A single coin that
lands 1 with probability $p$ has variance $p(1-p)$, so the number of heads in $n$ flips has variance $np(1-p)$.

**Theorem (Chebyshev).** For any $t > 0$, $P(|X - \mu| \ge t) \le \operatorname{Var}[X]/t^2$.

*Proof.* Apply Markov to the non-negative variable $(X - \mu)^2$ and the threshold $t^2$:
$P(|X-\mu| \ge t) = P((X-\mu)^2 \ge t^2) \le E[(X-\mu)^2]/t^2$. $\square$

### Chernoff bounds

For a sum of many independent 0/1 variables, the probability of being far from the mean falls *exponentially*.
That is what makes randomized algorithms reliable.

**Theorem (Chernoff bound).** Let $X = X_1 + \dots + X_n$ where the $X_i$ are independent, each $X_i \in \{0, 1\}$
with $P(X_i = 1) = p_i$, and let $\mu = E[X] = \sum p_i$. Then for every $\delta > 0$,

$$
P\big(X \ge (1+\delta)\mu\big) \le \left(\frac{e^{\delta}}{(1+\delta)^{1+\delta}}\right)^{\mu} \le \exp\!\left(-\frac{\delta^2 \mu}{2+\delta}\right),
$$

and for $0 < \delta < 1$,

$$
P\big(X \le (1-\delta)\mu\big) \le \exp\!\left(-\frac{\delta^2 \mu}{2}\right).
$$

*Proof of the upper tail.* The idea is to apply Markov not to $X$ but to $e^{tX}$ for a well-chosen $t > 0$, which
turns a sum into a product. For each $i$, $E[e^{tX_i}] = 1 - p_i + p_i e^t = 1 + p_i(e^t - 1) \le \exp(p_i(e^t-1))$,
using $1 + y \le e^y$. By independence the expectation of the product is the product of the expectations, so
$E[e^{tX}] = \prod_i E[e^{tX_i}] \le \exp(\mu(e^t - 1))$. Markov gives

$$
P\big(X \ge (1+\delta)\mu\big) = P\big(e^{tX} \ge e^{t(1+\delta)\mu}\big) \le \frac{\exp(\mu(e^t-1))}{e^{t(1+\delta)\mu}} .
$$

Choose $t = \ln(1+\delta)$, which makes the right side as small as possible; it becomes
$\big(e^{\delta}/(1+\delta)^{1+\delta}\big)^{\mu}$. For the simpler form we need
$(1+\delta)\ln(1+\delta) - \delta \ge \delta^2/(2+\delta)$. Let $f(\delta) = \ln(1+\delta) - 2\delta/(2+\delta)$.
Then $f(0) = 0$ and $f'(\delta) = \frac{1}{1+\delta} - \frac{4}{(2+\delta)^2} = \frac{\delta^2}{(1+\delta)(2+\delta)^2} \ge 0$,
so $\ln(1+\delta) \ge 2\delta/(2+\delta)$, and multiplying by $1+\delta$ and subtracting $\delta$ gives the
inequality. The lower tail is proved the same way with $t = \ln(1 - \delta) < 0$ and the inequality
$(1-\delta)\ln(1-\delta) \ge -\delta + \delta^2/2$. $\square$

The bound is named after Herman Chernoff, whose 1952 paper in the *Annals of Mathematical Statistics* used this
moment-generating-function method; closely related bounds are due to Hoeffding (1963) and Bernstein.

### The three side by side

Flip a fair coin 100 times; $X$ = number of heads, $\mu = 50$, variance $25$. How likely are at least 75 heads?

- Markov: $P(X \ge 75) \le 50/75 \approx 0.667$.
- Chebyshev: $P(X \ge 75) \le P(|X - 50| \ge 25) \le 25/625 = 0.04$.
- Chernoff with $\delta = 1/2$: $\exp(-0.25 \cdot 50/2.5) = e^{-5} \approx 0.0067$.
- The exact answer: about $2.8 \times 10^{-7}$.

```python
--8<-- "books/algorithms/ch21_tail_bounds.py"
```

```
X = number of heads in 100 fair coin flips: mean 50.0, variance 25.0
   t   exact P[X>=t]    Markov  Chebyshev    Chernoff
  60       2.844e-02     0.833     0.2500   4.029e-01
  70       3.925e-05     0.714     0.0625   3.567e-02
  75       2.818e-07     0.667     0.0400   6.738e-03
  90       1.532e-17     0.556     0.0156   1.088e-05

Amplifying a Monte Carlo test that is wrong with probability 1/3, by a majority of k runs
   k   exact error  Chernoff bound
   1     3.333e-01       9.672e-01
   5     2.099e-01       8.465e-01
  11     1.221e-01       6.930e-01
  31     2.702e-02       3.558e-01
 101     2.724e-04       3.450e-02

One-sided error: repeat a test that succeeds with probability q, until it has succeeded once
  q = 0.500000:     42 runs give failure <= 2.27e-13 (target 1e-09)
  q = 0.010000:   1382 runs give failure <= 9.29e-07 (target 1e-06)
  q = 0.000816:   4793 runs give failure <= 2.00e-02 (target 2e-02)
```

<figure class="mars-fig" markdown="0">
<svg viewBox="0 0 640 230" role="img" aria-label="Bar chart on a logarithmic scale of four bounds on the probability of at least 75 heads in 100 fair flips: Markov 0.67, Chebyshev 0.04, Chernoff 0.0067, exact 2.8 times ten to the minus 7.">
  <g font-size="12" fill="currentColor" text-anchor="middle">
    <line x1="100" y1="170" x2="580" y2="170" stroke="currentColor" stroke-width="1"/>
    <line x1="100" y1="165" x2="100" y2="175" stroke="currentColor"/><text x="100" y="190">1e-8</text>
    <line x1="160" y1="165" x2="160" y2="175" stroke="currentColor"/><text x="160" y="190">1e-7</text>
    <line x1="220" y1="165" x2="220" y2="175" stroke="currentColor"/><text x="220" y="190">1e-6</text>
    <line x1="280" y1="165" x2="280" y2="175" stroke="currentColor"/><text x="280" y="190">1e-5</text>
    <line x1="340" y1="165" x2="340" y2="175" stroke="currentColor"/><text x="340" y="190">1e-4</text>
    <line x1="400" y1="165" x2="400" y2="175" stroke="currentColor"/><text x="400" y="190">1e-3</text>
    <line x1="460" y1="165" x2="460" y2="175" stroke="currentColor"/><text x="460" y="190">0.01</text>
    <line x1="520" y1="165" x2="520" y2="175" stroke="currentColor"/><text x="520" y="190">0.1</text>
    <line x1="580" y1="165" x2="580" y2="175" stroke="currentColor"/><text x="580" y="190">1</text>
    <text x="340" y="215">bound on P(at least 75 heads in 100 flips), log scale</text>
  </g>
  <g font-size="13" fill="currentColor">
    <text x="90" y="34" text-anchor="end">Markov</text>
    <rect x="100" y="20" width="469" height="22" fill="#9cc9ea" fill-opacity="0.7" stroke="currentColor" stroke-width="0.8"/>
    <text x="90" y="70" text-anchor="end">Chebyshev</text>
    <rect x="100" y="56" width="396" height="22" fill="#9cc9ea" fill-opacity="0.7" stroke="currentColor" stroke-width="0.8"/>
    <text x="502" y="71">0.04</text>
    <text x="90" y="106" text-anchor="end">Chernoff</text>
    <rect x="100" y="92" width="350" height="22" fill="#7ccf9a" fill-opacity="0.75" stroke="currentColor" stroke-width="0.8"/>
    <text x="456" y="107">0.0067</text>
    <text x="90" y="142" text-anchor="end">exact</text>
    <rect x="100" y="128" width="87" height="22" fill="#eea66f" fill-opacity="0.8" stroke="currentColor" stroke-width="0.8"/>
    <text x="193" y="143">2.8e-7</text>
    <text x="575" y="35">0.67</text>
  </g>
</svg>
<figcaption>Figure 21.2. Each bound uses more about the variable: Markov only the mean, Chebyshev the variance, Chernoff independence. Even Chernoff is far above the truth here, but it falls exponentially, which is what algorithms need.</figcaption>
</figure>

Two honest remarks about the table. First, for small deviations ($t = 60$, $70$) Chebyshev beats this simple form of
Chernoff; the exponential bound wins only once the deviation is several standard deviations. Second, bounds are
not estimates: their job is to be *provably* above the truth, and in proofs they are used where the exact value is
impossible to compute.

### Using Chernoff: amplifying a Monte Carlo algorithm

Suppose a Monte Carlo algorithm answers a yes/no question correctly with probability $2/3$ (any constant above
$1/2$ will do). Run it $k$ times independently and output the majority answer. The majority is wrong only if at
least $k/2$ runs are wrong. The number of wrong runs has mean $\mu = k/3$, and $k/2 = (1 + \tfrac12)\mu$, so
Chernoff with $\delta = 1/2$ gives

$$
P(\text{majority wrong}) \le \exp\!\left(-\frac{(1/2)^2 (k/3)}{2.5}\right) = e^{-k/30} .
$$

The error falls exponentially in the number of runs: to get error below $10^{-9}$, about $k = 30 \ln 10^9 \approx 622$
runs suffice by this crude bound (the exact binomial needs far fewer, as the table shows). This is
**amplification**. For **one-sided** errors (the algorithm can only be wrong in one direction, like Karger's or
Miller-Rabin's) it is even simpler: one correct answer is enough, and after $r$ runs the failure probability is
$(1-q)^r \le e^{-qr}$.

### Using Chernoff: quicksort is fast with high probability

Here is a typical argument, which shows that randomized quicksort makes $O(n \log n)$ comparisons not just on
average but with probability at least $1 - 1/n^2$. Follow a single key $x$ down the recursion. Call a level
**good** for $x$ if the pivot chosen for $x$'s sublist has rank in the middle half of that sublist; then both parts
have at most $3/4$ of its size, so $x$'s sublist shrinks by a factor $3/4$. Each level is good with probability at
least $1/2$, whatever happened before. After $\log_{4/3} n$ good levels the sublist has size 1, so the depth of $x$
is more than $L = 8\log_{4/3} n$ only if fewer than $\log_{4/3} n = L/8$ of the first $L$ levels are good. The
number of good levels behaves at least as well as a sum of $L$ independent fair coins (the formal word is
*stochastically dominates*; the Chernoff bound still applies), with mean $L/2$, and $L/8 = (1 - \tfrac34)(L/2)$, so

$$
P(\text{depth of } x > L) \le \exp\!\left(-\frac{(3/4)^2 (L/2)}{2}\right) = \exp\!\left(-\frac{9 L}{64}\right) = n^{-\frac{9 \cdot 8}{64 \ln(4/3)}} \le n^{-3.9}.
$$

By the **union bound** ($P(A_1 \cup \dots \cup A_n) \le \sum P(A_i)$), the probability that *any* of the $n$ keys is
deeper than $L$ is at most $n \cdot n^{-3.9} < n^{-2}$. Each key is compared once per level it sits at, so with that
probability the total number of comparisons is at most $nL = O(n \log n)$. The constants are crude ($L \approx 19 \log_2 n$, while the measured depth for $n = 1000$ was 27), but the shape is what matters: the probability of
quadratic behaviour is not merely small, it vanishes faster than any power you like as $n$ grows, if you take the
constant 8 larger.

## 21.4 Karger's minimum cut and amplification

*Level: advanced.* Here is a problem where randomness gives a strikingly simple algorithm. A **cut** of a connected
undirected graph $G = (V, E)$ is a split of the vertices into two non-empty sets $S$ and $V \setminus S$; its **size**
is the number of edges with one end on each side. A **global minimum cut** is a cut of smallest size: the fewest
edges whose removal disconnects the graph. It measures how robust a network is: a communication network with
minimum cut 1 has a single link whose failure splits it.

[Chapter 17](17-Spanning-Trees-Flows-and-Matching.md) finds a minimum cut *between two given vertices* $s$ and $t$ by
max flow. A global minimum cut could be found by running max flow from one fixed vertex $s$ to each of the other
$n-1$ vertices. In 1993 David Karger, then a graduate student at Stanford, published a far simpler idea in
"Global Min-cuts in RNC, and Other Ramifications of a Simple Min-cut Algorithm".

### The contraction algorithm

To **contract** an edge $\{u, v\}$, merge $u$ and $v$ into one new vertex, keep every edge that went from $u$ or $v$
to anything else (so the graph becomes a **multigraph**, with parallel edges allowed), and delete the edges between
$u$ and $v$ (which would now be self-loops). The algorithm:

1. While more than two vertices remain, pick an edge uniformly at random among the remaining edges and contract it.
2. The two remaining super-vertices are two groups of original vertices: output that cut.

Every cut of a contracted graph is a cut of the original graph (split the super-vertices back into their members),
with exactly the same edges crossing it. So the algorithm always outputs *a* cut; the question is whether it is a
minimum one.

<figure class="mars-fig" markdown="0">
<svg viewBox="0 0 660 230" role="img" aria-label="Three panels of contraction. Left: five vertices a b c d e with edges ab, ac, bc, cd, ce, de; edge cd is highlighted. Middle: c and d merged into cd; edges ab, a-cd, b-cd and two parallel edges cd-e; edge ab highlighted. Right: ab and cd joined by two parallel edges, cd and e joined by two parallel edges.">
  <g stroke="currentColor" stroke-width="1.6" fill="none">
    <line x1="30" y1="60" x2="30" y2="160"/>
    <line x1="30" y1="60" x2="100" y2="110"/>
    <line x1="30" y1="160" x2="100" y2="110"/>
    <line x1="100" y1="110" x2="170" y2="60" stroke="#eea66f" stroke-width="4"/>
    <line x1="100" y1="110" x2="170" y2="160"/>
    <line x1="170" y1="60" x2="170" y2="160"/>
    <line x1="250" y1="60" x2="250" y2="160" stroke="#eea66f" stroke-width="4"/>
    <line x1="250" y1="60" x2="330" y2="100"/>
    <line x1="250" y1="160" x2="330" y2="100"/>
    <path d="M 330 100 Q 380 112 400 160"/>
    <path d="M 330 100 Q 342 152 400 160"/>
    <path d="M 480 110 Q 520 70 560 80"/>
    <path d="M 480 110 Q 530 118 560 80"/>
    <path d="M 560 80 Q 610 95 615 160"/>
    <path d="M 560 80 Q 560 148 615 160"/>
  </g>
  <g font-size="14" text-anchor="middle" fill="currentColor">
    <circle cx="30" cy="60" r="15" fill="#9cc9ea" stroke="currentColor"/><text x="30" y="65">a</text>
    <circle cx="30" cy="160" r="15" fill="#9cc9ea" stroke="currentColor"/><text x="30" y="165">b</text>
    <circle cx="100" cy="110" r="15" fill="#9cc9ea" stroke="currentColor"/><text x="100" y="115">c</text>
    <circle cx="170" cy="60" r="15" fill="#9cc9ea" stroke="currentColor"/><text x="170" y="65">d</text>
    <circle cx="170" cy="160" r="15" fill="#9cc9ea" stroke="currentColor"/><text x="170" y="165">e</text>
    <circle cx="250" cy="60" r="15" fill="#9cc9ea" stroke="currentColor"/><text x="250" y="65">a</text>
    <circle cx="250" cy="160" r="15" fill="#9cc9ea" stroke="currentColor"/><text x="250" y="165">b</text>
    <circle cx="330" cy="100" r="18" fill="#7ccf9a" stroke="currentColor"/><text x="330" y="105">cd</text>
    <circle cx="400" cy="160" r="15" fill="#9cc9ea" stroke="currentColor"/><text x="400" y="165">e</text>
    <circle cx="480" cy="110" r="18" fill="#7ccf9a" stroke="currentColor"/><text x="480" y="115">ab</text>
    <circle cx="560" cy="80" r="18" fill="#7ccf9a" stroke="currentColor"/><text x="560" y="85">cd</text>
    <circle cx="615" cy="160" r="15" fill="#9cc9ea" stroke="currentColor"/><text x="615" y="165">e</text>
    <text x="100" y="205">contract c–d</text>
    <text x="325" y="205">contract a–b</text>
    <text x="550" y="205">3 vertices, 4 edges left</text>
  </g>
</svg>
<figcaption>Figure 21.3. Contraction keeps parallel edges and drops self-loops. One more contraction leaves two super-vertices; either choice here gives a cut of size 2, which is a minimum cut of this graph.</figcaption>
</figure>

### Why it succeeds with probability at least 2/(n(n-1))

**Theorem (Karger 1993).** Fix any minimum cut $C$ (a set of $k$ edges). The contraction algorithm outputs exactly
$C$ with probability at least $\dfrac{2}{n(n-1)} = 1\big/\tbinom{n}{2}$.

*Proof.* The algorithm outputs $C$ if and only if it never contracts an edge of $C$: contracting an edge of $C$
puts its two ends, which are on opposite sides of $C$, into one super-vertex; and if no edge of $C$ is ever
contracted, each side of $C$ is only ever merged with itself, so the final two groups are exactly the two sides.

Two facts. First, every vertex has degree at least $k$, because the edges at a single vertex form a cut. So a graph
with $n$ vertices has at least $nk/2$ edges (the degrees sum to twice the number of edges). Second, the same holds
after contractions: as long as no edge of $C$ has been contracted, the minimum cut of the contracted graph is still
$k$ (it cannot go down, since its cuts are cuts of $G$, and $C$ is still one of them), so a contracted graph with
$r$ vertices has at least $rk/2$ edges.

When $r$ vertices remain, the random edge lies in $C$ with probability at most $k/(rk/2) = 2/r$. The steps happen
with $r = n, n-1, \dots, 3$, so

$$
P(C \text{ survives}) \ge \prod_{r=3}^{n}\left(1 - \frac{2}{r}\right) = \prod_{r=3}^{n}\frac{r-2}{r} = \frac{1 \cdot 2 \cdot 3 \cdots (n-2)}{3 \cdot 4 \cdots n} = \frac{2}{n(n-1)} .
$$

The middle product telescopes: every factor from 3 to $n-2$ appears once on top and once below. $\square$

**A corollary for free.** The events "the algorithm outputs $C$" for different minimum cuts $C$ are disjoint, and
each has probability at least $1/\binom{n}{2}$. Probabilities of disjoint events add to at most 1, so **every graph
has at most $\binom{n}{2}$ minimum cuts.** The cycle on $n$ vertices shows this is tight: removing any two of its $n$
edges disconnects it, so it has exactly $\binom{n}{2}$ minimum cuts of size 2, and by symmetry contraction finds each
with probability exactly $1/\binom{n}{2}$. A purely combinatorial proof of this count is not obvious; here it falls
out of a probability argument.

### Amplification

A success probability of about $2/n^2$ looks hopeless, but the error is one-sided: a run either finds a minimum cut
or finds a bigger cut, and we keep the smallest cut seen. Run it $R = \binom{n}{2}\ln n$ times independently. The
probability that every run misses $C$ is at most

$$
\left(1 - \frac{1}{\binom{n}{2}}\right)^{\binom{n}{2}\ln n} \le e^{-\ln n} = \frac{1}{n},
$$

using $1 - y \le e^{-y}$. With $c$ times as many runs the failure drops to $n^{-c}$.

### Implementation and running time

Picking a random remaining edge, contracting, picking again: this is the same as **shuffling the edge list once and
walking through it, skipping any edge whose ends are already in the same group**. (After the shuffle, the next
non-skipped edge is uniform among the edges between different groups, which are exactly the edges still present.)
Walking a shuffled edge list and merging groups is Kruskal's algorithm with random weights, and the groups are kept
with [union-find](../../data-structures/union-find.md) ([Chapter 10](10-Union-Find-and-Range-Queries.md)). One run
costs $O(m\,\alpha(n))$, almost linear, and the whole amplified algorithm $O(n^2 m \log n)$ time.

A hand trace on Figure 21.3's graph (edges ab, ac, bc, cd, ce, de) with the shuffled order de, ce, ab, bc, cd, ac:

| step | edge | action | groups |
|---|---|---|---|
| 0 | | | {a} {b} {c} {d} {e} |
| 1 | de | merge | {a} {b} {c} {d,e} |
| 2 | ce | merge | {a} {b} {c,d,e} |
| 3 | ab | merge, 2 groups left: stop | {a,b} {c,d,e} |

The cut $\{a,b\} \mid \{c,d,e\}$ is crossed by ac and bc: size 2, a minimum cut.

```python
--8<-- "books/algorithms/ch21_karger.py"
```

```
Two cliques joined by two edges: n = 8, m = 14
  brute force (min cut, number of minimum cuts): (2, 1)
  one contraction run finds it with frequency 0.2150; Karger's guarantee is at least 1/C(n,2) = 0.0357

Cycle graph C_n: any two edges form a minimum cut, so it has exactly C(n,2) minimum cuts
  n = 5: min cut 2, 10 minimum cuts (C(n,2) = 10); the cut 'vertex 0 alone' is found with frequency 0.1021, 1/C(n,2) = 0.1000
  n = 6: min cut 2, 15 minimum cuts (C(n,2) = 15); the cut 'vertex 0 alone' is found with frequency 0.0691, 1/C(n,2) = 0.0667
  n = 8: min cut 2, 28 minimum cuts (C(n,2) = 28); the cut 'vertex 0 alone' is found with frequency 0.0360, 1/C(n,2) = 0.0357

Random graphs, repeated runs: C(n,2) ln n repetitions, failure at most 1/n
  graph 0: m = 25, true min cut 2, best of 165 runs 2
  graph 1: m = 23, true min cut 1, best of 165 runs 1
  graph 2: m = 22, true min cut 1, best of 165 runs 1
  graph 3: m = 28, true min cut 1, best of 165 runs 1
  graph 4: m = 26, true min cut 2, best of 165 runs 2
```

On the two cliques the single run succeeds about 21% of the time, six times the guarantee: the guarantee is a worst
case, met with equality by the cycle.

**Faster versions.** The failure probability is concentrated at the *end* of a run: the first contractions are very
unlikely to hit $C$ (probability $2/n$), the last ones quite likely ($2/3$). David Karger and Clifford Stein ("A New
Approach to the Minimum Cut Problem", *Journal of the ACM*, 1996) contract only down to about $n/\sqrt2$ vertices,
then recurse *twice* on copies of that smaller graph and keep the better answer. This succeeds with probability
$\Omega(1/\log n)$ per run and gives total time $O(n^2 \log^3 n)$. Karger later gave a near-linear-time randomized
algorithm ("Minimum Cuts in Near-Linear Time", *Journal of the ACM*, 2000). A clean deterministic algorithm with
time $O(nm + n^2 \log n)$ is due to Mechthild Stoer and Frank Wagner (*Journal of the ACM*, 1997).

## 21.5 Reservoir sampling and the Fisher-Yates shuffle

Two everyday tasks: put a list in a uniformly random order (shuffle a deck, randomize the order of survey
questions, pick a random pivot order), and pick a uniform random sample of $k$ items from a stream too long to
store, whose length you do not even know in advance (a log file, packets on a network link, telemetry arriving from
a spacecraft). Both have tiny, exact algorithms, and both are easy to get subtly wrong.

### Fisher-Yates

"Uniformly random" means each of the $n!$ orders has probability exactly $1/n!$. The **Fisher-Yates shuffle**:

```python
for i in range(n - 1):
    j = random.randint(i, n - 1)     # uniform among the positions not yet fixed
    a[i], a[j] = a[j], a[i]
```

It is named after the statisticians Ronald Fisher and Frank Yates, who described a pencil-and-paper version in their
book *Statistical Tables for Biological, Agricultural and Medical Research* (1938). Richard Durstenfeld gave the
in-place computer version as "Algorithm 235: Random permutation" (*Communications of the ACM*, 1964), and Knuth's
TAOCP volume 2 presents it as Algorithm P. Python's `random.shuffle` is this algorithm, run from the right end.

**Theorem.** Fisher-Yates produces every permutation with probability exactly $1/n!$.

*Proof.* The random choices are a sequence $(j_0, j_1, \dots, j_{n-2})$ with $j_i \in \{i, \dots, n-1\}$: there are
$n (n-1) \cdots 2 = n!$ sequences, all equally likely. We show that different sequences give different
permutations; then the $n!$ sequences give all $n!$ permutations, one each. Invariant: after step $i$, positions
$0..i$ are final, and positions $i+1..n-1$ hold the remaining elements. At step $i$, the element placed in position
$i$ is the one that was at position $j_i$, and the elements in positions $i..n-1$ are all different, so two sequences
that first differ at step $i$ put different elements in position $i$, and that position is never touched again. So
the map from sequences to permutations is one-to-one, hence onto, and each permutation has probability $1/n!$.
$\square$

A hand trace on ABCD with choices $j_0 = 2$, $j_1 = 3$, $j_2 = 2$:

| step $i$ | $j_i$ | swap | list after |
|---|---|---|---|
| 0 | 2 | positions 0 and 2 | C B A D |
| 1 | 3 | positions 1 and 3 | C D A B |
| 2 | 2 | position 2 with itself | C D A B |

**The classic mistake.** Swapping position $i$ with *any* position, `j = random.randint(0, n - 1)`, looks just as
random. It is not. It makes $n^n$ equally likely choice sequences, and for $n \ge 3$ the number $n!$ does not divide
$n^n$ (the factor $n - 1$ of $n!$ shares no prime with $n$), so the $n!$ permutations cannot all receive the same
number of sequences. For $n = 3$ the program below lists all 27 sequences: three permutations come out 5 times, three
come out 4 times.

### Reservoir sampling

We see items $x_1, x_2, \dots$ one at a time, we have room for only $k$ of them, and at any moment we want the $k$
items in memory to be a uniform random sample of the items seen so far. **Algorithm R**:

1. Keep the first $k$ items.
2. When item $t > k$ arrives, pick $j$ uniform in $1..t$. If $j \le k$, replace the $j$-th kept item by $x_t$;
   otherwise ignore $x_t$.

Knuth (TAOCP volume 2, section 3.4.2) credits Algorithm R to Alan G. Waterman. Jeffrey Vitter's paper "Random
Sampling with a Reservoir" (*ACM Transactions on Mathematical Software*, 1985) analysed it and gave faster versions
that compute how many items to skip instead of drawing a number for every item.

**Theorem.** After $t \ge k$ items, each of $x_1, \dots, x_t$ is in the reservoir with probability exactly $k/t$.

*Proof by induction on $t$.* For $t = k$ every item is kept: probability $1 = k/k$. Suppose it holds after $t - 1$
items. Item $x_t$ enters with probability $P(j \le k) = k/t$. An earlier item $x_s$ is in the reservoir after $t-1$
items with probability $k/(t-1)$, and is then thrown out only if $x_t$ enters *and* lands in its slot, which has
probability $(k/t)(1/k) = 1/t$. The new draw is independent of the past, so

$$
P(x_s \text{ kept after } t) = \frac{k}{t-1}\cdot\left(1 - \frac{1}{t}\right) = \frac{k}{t-1}\cdot\frac{t-1}{t} = \frac{k}{t}. \qquad \square
$$

The same induction shows more: every one of the $\binom{t}{k}$ possible $k$-sets is equally likely (Exercise 7).
Equal inclusion probabilities alone would not be enough for that, since a scheme that keeps either $\{1,2\}$ or
$\{3,4\}$ gives each of four items probability $1/2$ but is far from a uniform sample.

A trace with $k = 2$ on the stream a, b, c, d, e and draws $j = 1$ (for c, $t = 3$), $j = 4$ (for d), $j = 2$ (for e):

| $t$ | item | $j$ | reservoir |
|---|---|---|---|
| 1 | a | | a |
| 2 | b | | a b |
| 3 | c | 1 of 3 | c b |
| 4 | d | 4 of 4 | c b (d ignored) |
| 5 | e | 2 of 5 | c e |

```python
--8<-- "books/algorithms/ch21_sampling.py"
```

```
All equally likely choice sequences for n = 3, and the permutation each one makes
  Fisher-Yates (6 sequences): {'ABC': 1, 'ACB': 1, 'BAC': 1, 'BCA': 1, 'CAB': 1, 'CBA': 1}
  naive        (27 sequences): {'ABC': 4, 'ACB': 5, 'BAC': 5, 'BCA': 5, 'CAB': 4, 'CBA': 4}

Reservoir sampling k = 3 from a stream of 10 items, 200000 runs
  frequency each item is kept (should be k/N = 0.3):
    0.300 0.299 0.300 0.299 0.301 0.300 0.300 0.300 0.300 0.301
  120 different samples seen (C(10,3) = 120); counts range 1566 to 1779, expected 1667 each

Library versions: random.shuffle is Fisher-Yates, random.sample draws without replacement
  random.shuffle: [5, 3, 6, 4, 0, 9, 7, 2, 1, 8]   random.sample: [90, 35, 89, 20, 48]
```

The spread 1566 to 1779 around 1667 is what chance predicts: each count has standard deviation about
$\sqrt{1667} \approx 41$, and among 120 counts the extremes are typically two to three standard deviations out.

## 21.6 Amortized analysis in depth

*Level: advanced; the splay-tree proofs are expert.* Randomized analysis averages over coin flips. **Amortized
analysis** averages over a *sequence of operations*, with no randomness at all: it proves that any sequence of $m$
operations costs at most $m$ times some bound, even if a single operation can be expensive. Chapter 4 met its three
methods on the dynamic array. Here we use the strongest one, the potential method, on two harder structures.

### The potential method, precisely

Let $D_0$ be the starting state of a data structure and $D_i$ its state after the $i$-th operation, which really
costs $c_i$. Choose a **potential function** $\Phi$ that maps each state to a real number. The **amortized cost** of
operation $i$ is defined as

$$
\hat c_i = c_i + \Phi(D_i) - \Phi(D_{i-1}),
$$

the real cost plus the change in potential. Summing over $m$ operations, the potential terms telescope:

$$
\sum_{i=1}^{m} \hat c_i = \sum_{i=1}^{m} c_i + \Phi(D_m) - \Phi(D_0).
$$

So if $\Phi(D_m) \ge \Phi(D_0)$ for every possible sequence (usually: $\Phi \ge 0$ always and $\Phi(D_0) = 0$), the
total real cost is at most the total amortized cost. Think of $\Phi$ as money saved in the structure: cheap
operations pay a little extra into it (their potential goes up), and an expensive operation is paid for by the
potential it releases. The whole art is choosing $\Phi$. Robert Tarjan's paper "Amortized Computational Complexity"
(*SIAM Journal on Algebraic and Discrete Methods*, 1985) set out the method in this form.

### A dynamic table that also shrinks

A dynamic array (Python's `list`, Chapter 4) doubles its capacity when full, which makes appends amortized $O(1)$.
If elements are also deleted, we may want to give memory back by shrinking. Write $\mathit{num}$ for the number of
elements, $\mathit{size}$ for the capacity, and $\alpha = \mathit{num}/\mathit{size}$ for the **load factor**. Count
the real cost as 1 per insert or delete, plus 1 per element copied when the table is resized.

**The natural rule fails.** "Double when full, halve when less than half full" can cost $\Theta(n)$ *per operation*.
Start with a full table of size $n$ (a power of two) and repeat: insert, delete, delete, insert. The first insert
doubles (copy $n$), the two deletes bring $\mathit{num}$ to $n-1 < n = \mathit{size}/2$, so the table halves (copy
$n-1$), and the last insert fills it again. Every four operations copy about $2n$ elements.

**The fix: shrink later.** Double when an insert finds the table full; halve when a delete makes the table less than
**a quarter** full. After either resize the table is exactly half full, so it takes many cheap operations to reach
the next resize, and those operations pay for it. The potential that proves this (it is the one in CLRS) is

$$
\Phi = \begin{cases} 2\,\mathit{num} - \mathit{size} & \text{if } \alpha \ge 1/2, \\ \mathit{size}/2 - \mathit{num} & \text{if } \alpha < 1/2. \end{cases}
$$

It is 0 when the table is exactly half full, grows as the table moves away from half full in either direction, and
equals $\mathit{num}$ at both trigger points: when the table is full ($2\,\mathit{num} - \mathit{size} = \mathit{num}$)
and when it is a quarter full ($\mathit{size}/2 - \mathit{num} = \mathit{num}$). That is exactly the money needed to
copy $\mathit{num}$ elements.

**Theorem.** With this rule every insert has amortized cost at most 3 and every delete at most 2, so any sequence
of $m$ operations starting from an empty table costs at most $3m$.

*Proof.* $\Phi \ge 0$ always, and $\Phi = 0$ for the empty table. Check every case (sizes are powers of two).

| operation | case | real cost | change in $\Phi$ | amortized |
|---|---|---|---|---|
| insert | $\alpha \ge 1/2$, not full | 1 | $+2$ | 3 |
| insert | full, $\mathit{num} = \mathit{size} = s$: doubles | $1 + s$ | from $s$ to $2(s+1) - 2s = 2$ | 3 |
| insert | $\alpha < 1/2$ before and after | 1 | $-1$ | 0 |
| insert | $\mathit{num} = \mathit{size}/2 - 1$ before | 1 | from 1 to 0 | 0 |
| delete | $\alpha \ge 1/2$ before and after | 1 | $-2$ | $-1$ |
| delete | $\mathit{num} = \mathit{size}/2$ before | 1 | from 0 to 1 | 2 |
| delete | $\alpha < 1/2$, no shrink | 1 | $+1$ | 2 |
| delete | $\mathit{num} = \mathit{size}/4$ before: halves | $1 + (\mathit{size}/4 - 1)$ | from $\mathit{size}/4$ to 1 | 1 |

In the last row, after the delete there are $\mathit{size}/4 - 1$ elements in a table of size $\mathit{size}/2$, so
$\Phi = \mathit{size}/4 - (\mathit{size}/4 - 1) = 1$. Every amortized cost is at most 3. $\square$

The program runs the bad sequence against both rules, then runs 200,000 random operations and checks every
amortized cost against the theorem.

```python
--8<-- "books/algorithms/ch21_dynamic_table.py"
```

```
halve below 1/2 full: average cost per operation over 4000 operations after the fill   512.75
halve below 1/4 full: average cost per operation over 4000 operations after the fill     1.26

Potential check for the 1/4 rule: amortized = actual + change in Phi, over random operations
  largest amortized insert 3, largest amortized delete 2.0  (final size 2048, num 1202, Phi 356)
```

The 1/4 rule is not magic: any shrink threshold strictly below the growth threshold divided by the growth factor
works, with a different constant. Real libraries differ. CPython's `list` grows to about $1.125$ times the needed length (plus
a small constant) rather than doubling, and gives memory back only when the length falls below half the capacity;
the gap between the two triggers is what prevents thrashing.

### Splay trees and the access lemma

[Chapter 8](08-Trees-and-Balanced-Search-Trees.md) introduced the **splay tree** (Daniel Sleator and Robert Tarjan,
"Self-Adjusting Binary Search Trees", *Journal of the ACM*, 1985): an ordinary [binary search
tree](../../data-structures/bst.md) with no balance information at all, which after every access moves the accessed
node $x$ to the root by a sequence of rotations called **splaying**. While $x$ is not the root, let $y$ be its parent
and $z$ its grandparent:

- **zig**: $y$ is the root. Rotate $x$ above $y$.
- **zig-zig**: $x$ and $y$ are both left children (or both right children). Rotate $y$ above $z$, then $x$ above $y$.
- **zig-zag**: one is a left child and the other a right child. Rotate $x$ above $y$, then $x$ above $z$.

Rotations keep the in-order sequence of keys, so the tree stays a search tree. The order of the two rotations in a
zig-zig (the parent first) is what makes splaying different from simply rotating $x$ up step by step, and it is the
reason the analysis below works: plain rotate-to-root has sequences costing $\Theta(n)$ per access.

<figure class="mars-fig" markdown="0">
<svg viewBox="0 0 660 400" role="img" aria-label="Top: zig-zig. z with left child y with left child x, subtrees A B under x, C under y, D under z, becomes x at the root with A on the left and y on the right, y with B and z, z with C and D. Bottom: zig-zag. z with left child y, y with right child x, becomes x at the root with children y and z, holding A B and C D.">
  <g stroke="currentColor" stroke-width="1.4" fill="none">
    <line x1="170" y1="40" x2="120" y2="85"/><line x1="170" y1="40" x2="210" y2="80"/>
    <line x1="120" y1="85" x2="75" y2="130"/><line x1="120" y1="85" x2="155" y2="120"/>
    <line x1="75" y1="130" x2="50" y2="165"/><line x1="75" y1="130" x2="100" y2="165"/>
    <line x1="450" y1="40" x2="405" y2="80"/><line x1="450" y1="40" x2="500" y2="85"/>
    <line x1="500" y1="85" x2="465" y2="120"/><line x1="500" y1="85" x2="545" y2="130"/>
    <line x1="545" y1="130" x2="520" y2="165"/><line x1="545" y1="130" x2="570" y2="165"/>
    <line x1="170" y1="240" x2="115" y2="285"/><line x1="170" y1="240" x2="215" y2="280"/>
    <line x1="115" y1="285" x2="80" y2="320"/><line x1="115" y1="285" x2="150" y2="330"/>
    <line x1="150" y1="330" x2="125" y2="365"/><line x1="150" y1="330" x2="175" y2="365"/>
    <line x1="450" y1="240" x2="400" y2="290"/><line x1="450" y1="240" x2="500" y2="290"/>
    <line x1="400" y1="290" x2="375" y2="325"/><line x1="400" y1="290" x2="425" y2="325"/>
    <line x1="500" y1="290" x2="475" y2="325"/><line x1="500" y1="290" x2="525" y2="325"/>
  </g>
  <g stroke="currentColor" stroke-width="1" fill="#9cc9ea" fill-opacity="0.45">
    <polygon points="50,165 35,191 65,191"/><polygon points="100,165 85,191 115,191"/>
    <polygon points="155,120 140,146 170,146"/><polygon points="210,80 195,106 225,106"/>
    <polygon points="405,80 390,106 420,106"/><polygon points="465,120 450,146 480,146"/>
    <polygon points="520,165 505,191 535,191"/><polygon points="570,165 555,191 585,191"/>
    <polygon points="80,320 65,346 95,346"/><polygon points="125,365 110,391 140,391"/>
    <polygon points="175,365 160,391 190,391"/><polygon points="215,280 200,306 230,306"/>
    <polygon points="375,325 360,351 390,351"/><polygon points="425,325 410,351 440,351"/>
    <polygon points="475,325 460,351 490,351"/><polygon points="525,325 510,351 540,351"/>
  </g>
  <g font-size="12" text-anchor="middle" fill="currentColor">
    <text x="50" y="186">A</text><text x="100" y="186">B</text><text x="155" y="141">C</text><text x="210" y="101">D</text>
    <text x="405" y="101">A</text><text x="465" y="141">B</text><text x="520" y="186">C</text><text x="570" y="186">D</text>
    <text x="80" y="341">A</text><text x="125" y="386">B</text><text x="175" y="386">C</text><text x="215" y="301">D</text>
    <text x="375" y="346">A</text><text x="425" y="346">B</text><text x="475" y="346">C</text><text x="525" y="346">D</text>
  </g>
  <g font-size="14" text-anchor="middle" fill="currentColor">
    <circle cx="170" cy="40" r="15" fill="#9cc9ea" stroke="currentColor"/><text x="170" y="45">z</text>
    <circle cx="120" cy="85" r="15" fill="#9cc9ea" stroke="currentColor"/><text x="120" y="90">y</text>
    <circle cx="75" cy="130" r="15" fill="#eea66f" stroke="currentColor"/><text x="75" y="135">x</text>
    <circle cx="450" cy="40" r="15" fill="#eea66f" stroke="currentColor"/><text x="450" y="45">x</text>
    <circle cx="500" cy="85" r="15" fill="#9cc9ea" stroke="currentColor"/><text x="500" y="90">y</text>
    <circle cx="545" cy="130" r="15" fill="#9cc9ea" stroke="currentColor"/><text x="545" y="135">z</text>
    <circle cx="170" cy="240" r="15" fill="#9cc9ea" stroke="currentColor"/><text x="170" y="245">z</text>
    <circle cx="115" cy="285" r="15" fill="#9cc9ea" stroke="currentColor"/><text x="115" y="290">y</text>
    <circle cx="150" cy="330" r="15" fill="#eea66f" stroke="currentColor"/><text x="150" y="335">x</text>
    <circle cx="450" cy="240" r="15" fill="#eea66f" stroke="currentColor"/><text x="450" y="245">x</text>
    <circle cx="400" cy="290" r="15" fill="#9cc9ea" stroke="currentColor"/><text x="400" y="295">y</text>
    <circle cx="500" cy="290" r="15" fill="#9cc9ea" stroke="currentColor"/><text x="500" y="295">z</text>
    <text x="310" y="100">zig-zig</text><text x="310" y="300">zig-zag</text>
  </g>
  <g stroke="#7ccf9a" stroke-width="3" fill="#7ccf9a">
    <line x1="270" y1="110" x2="340" y2="110"/><polygon points="350,110 338,103 338,117"/>
    <line x1="270" y1="310" x2="340" y2="310"/><polygon points="350,310 338,303 338,317"/>
  </g>
</svg>
<figcaption>Figure 21.4. The two double steps of splaying (the mirror images are the same). In-order, the keys read A x B y C z D before and after, so the tree remains a search tree.</figcaption>
</figure>

**The potential.** For a node $v$ let $s(v)$ be the number of nodes in its subtree and $r(v) = \log_2 s(v)$ its
**rank**. The potential of the tree is the sum of all ranks, $\Phi = \sum_v r(v)$. A path of $n$ nodes has potential
$\log_2 n!$, about $n\log_2 n$; a perfectly balanced tree has potential $O(n)$. So potential measures, roughly, how
unbalanced the tree is. Measure the real cost of a splay as its number of rotations (a zig costs 1, the double steps
cost 2); the search that found $x$ costs the same as the rotations, up to a constant.

**Lemma (a fact about logarithms).** If $a, b > 0$ and $a + b \le c$, then $\log_2 a + \log_2 b \le 2\log_2 c - 2$.

*Proof.* $ab \le \big(\tfrac{a+b}{2}\big)^2 \le c^2/4$, since $(a-b)^2 \ge 0$ gives $4ab \le (a+b)^2$. Take
$\log_2$ of both ends. $\square$

**Access lemma (Sleator and Tarjan 1985).** Splaying a node $x$ in a tree with root $t$ has amortized cost at most
$3\,(r(t) - r(x)) + 1$.

*Proof.* Write $r$ and $s$ for ranks and sizes before one step, and $r'$, $s'$ after. Only the nodes $x$, $y$ (and
$z$) change their subtrees, so only their ranks enter the change in potential. We show that each step has amortized
cost at most $3(r'(x) - r(x))$, plus 1 for a zig. Since after one step's $r'(x)$ is the next step's $r(x)$, the
bounds telescope to $3(r_{\text{final}}(x) - r(x)) + 1 = 3(r(t) - r(x)) + 1$, the final $x$ being the root. There is
at most one zig, so the $+1$ appears at most once.

*Zig.* Cost 1. Afterwards $x$ has $y$'s old subtree, so $r'(x) = r(y)$, and $y$ is now below $x$, so
$r'(y) \le r'(x)$. Amortized cost
$= 1 + r'(x) + r'(y) - r(x) - r(y) = 1 + r'(y) - r(x) \le 1 + r'(x) - r(x) \le 1 + 3(r'(x) - r(x))$, because
$r'(x) \ge r(x)$.

*Zig-zig.* Cost 2. Again $r'(x) = r(z)$, so the amortized cost is

$$
2 + r'(y) + r'(z) - r(x) - r(y) \le 2 + r'(x) + r'(z) - 2r(x),
$$

using $r'(y) \le r'(x)$ ($y$ is below $x$ afterwards) and $r(y) \ge r(x)$ ($x$ was below $y$ before). Now look at the
picture: $x$'s old subtree (x, A, B) and $z$'s new subtree (z, C, D) are disjoint, and both lie inside $x$'s new
subtree, so $s(x) + s'(z) \le s'(x)$. By the lemma, $r(x) + r'(z) \le 2r'(x) - 2$, that is,
$r'(z) \le 2r'(x) - r(x) - 2$. Substituting, the amortized cost is at most $3r'(x) - 3r(x)$.

*Zig-zag.* Cost 2. Again $r'(x) = r(z)$ and $r(y) \ge r(x)$, so the amortized cost is at most
$2 + r'(y) + r'(z) - 2r(x)$. Afterwards $y$ and $z$ are the two children of $x$, with disjoint subtrees inside
$x$'s, so $s'(y) + s'(z) \le s'(x)$ and the lemma gives $r'(y) + r'(z) \le 2r'(x) - 2$. The amortized cost is at
most $2r'(x) - 2r(x) \le 3(r'(x) - r(x))$. $\square$

The "$-2$" from the lemma is the whole trick: it pays for the 2 rotations of a double step. That is why splaying
takes two steps at a time.

**Balance theorem.** Any sequence of $m$ accesses in an $n$-node splay tree costs $O((m + n)\log n)$ in total.

*Proof.* Each access has amortized cost at most $3\log_2 n + 1$, since $r(t) = \log_2 n$ and $r(x) \ge 0$. The
potential starts at most $\sum_v \log_2 n = n\log_2 n$ and never drops below 0, so the real total is at most
$m(3\log_2 n + 1) + n\log_2 n$. $\square$

Insertion and deletion (search, then splay, then a few pointer changes) also cost $O(\log n)$ amortized; the
insertion of a new leaf raises the ranks of its ancestors, but by at most $\log_2(n+1)$ in total: along the path
each subtree size $s_i$ becomes $s_i + 1 \le s_{i+1}$, so the increases telescope (Sleator and Tarjan give the
details).

**A hand trace.** Insert 1, 2, 3, 4, 5 in increasing order: each new key is splayed to the root and the old tree
hangs on its left, so the tree is a left path 5, 4, 3, 2, 1, with sizes 5, 4, 3, 2, 1 and potential
$\log_2(5 \cdot 4 \cdot 3 \cdot 2 \cdot 1) = \log_2 120 \approx 6.907$. Now access 1.

| step | case | tree after (in-order with parentheses) | $\Phi$ after |
|---|---|---|---|
| start | | (((((1) 2) 3) 4) 5) | 6.907 |
| 1 | zig-zig on 1, 2, 3 | ((1 (2 (3))) 4) 5 | 6.907 |
| 2 | zig-zig on 1, 4, 5 | 1 ((2 (3)) 4 (5)) | 5.322 |

After step 1 the sizes of nodes 5, 4, 1, 2, 3 are 5, 4, 3, 2, 1, the same multiset as before, so the potential has
not moved yet; after step 2 they are 5, 4, 2, 1, 1 for nodes 1, 4, 2, 3, 5, giving $\log_2 40 \approx 5.322$. Real
cost 4 rotations; the potential fell by $\log_2 120 - \log_2 40 = \log_2 3 \approx 1.585$; amortized cost
$4 - 1.585 = 2.415$, below the lemma's $3\log_2 5 + 1 \approx 7.97$. The depth of the tree went from 4 to 3. In
general splaying roughly halves the depth of every node on the access path, which is the intuition behind the
lemma: a long path costs a lot once, and leaves a much flatter tree behind.

The program builds a 1000-key path the same way, runs four access patterns, and checks the access lemma on every
single access by recomputing the ranks along the path.

```python
--8<-- "books/algorithms/ch21_splay.py"
```

```
Splay tree on keys 1..1000, built as a path by inserting 1, 2, ..., n; 3 log2 n + 1 = 30.90
  access 1, 2, ..., n in order m = 1000, rotations   4374, per access   4.37; lemma's smallest slack 2.755
  uniform random keys         m = 5000, rotations  58466, per access  11.69; lemma's smallest slack 0.397
  one key over and over       m = 5000, rotations   1250, per access   0.25; lemma's smallest slack 1.000
  90% of accesses to 10 keys  m = 5000, rotations  20824, per access   4.16; lemma's smallest slack 0.010

The in-order run is a known case: Tarjan proved in 1985 (the **sequential access theorem**) that accessing all $n$
keys of a splay tree in order costs $O(n)$ in total, whatever the starting tree; here it was 4374 rotations for
1000 keys, under 5 per access. The skewed pattern costs about a third of the uniform one, because recently used
keys stay near the root. Splay trees satisfy several such theorems (static optimality, the working-set theorem),
all proved in the 1985 paper with the same potential and different weights in place of subtree sizes.

**An open problem.** Sleator and Tarjan conjectured that splay trees are **dynamically optimal**: on every access
sequence, they cost at most a constant factor more than the best possible binary search tree algorithm that may
rotate however it likes, even one that knows the future. Despite partial results (for example Tango trees by
Demaine, Harmon, Iacono and Pătraşcu, 2004, are $O(\log\log n)$-competitive), the **dynamic optimality conjecture**
is still open.

## Check yourself

??? question "1. You throw $n$ balls into $n$ bins, each ball into a uniformly random bin, independently. What is the expected number of empty bins? Evaluate it for $n = 10$."

    Let $I_b$ indicate "bin $b$ is empty". Each ball misses bin $b$ with probability $1 - 1/n$, independently, so
    $P(I_b = 1) = (1 - 1/n)^n$. By linearity the expected number of empty bins is $n(1 - 1/n)^n$, which tends to
    $n/e \approx 0.368n$. For $n = 10$: $10 \cdot 0.9^{10} \approx 3.487$.

??? question "2. Compute $C(4)$, the expected number of comparisons of randomized quicksort on 4 keys, from the recurrence and from the closed form."

    Recurrence: $C(4) = 3 + \tfrac{2}{4}\big(C(0) + C(1) + C(2) + C(3)\big) = 3 + \tfrac12\big(0 + 0 + 1 + \tfrac83\big)
    = 3 + \tfrac{11}{6} = \tfrac{29}{6}$. Closed form: $2 \cdot 5 \cdot H_4 - 16 = 10 \cdot \tfrac{25}{12} - 16 =
    \tfrac{125}{6} - \tfrac{96}{6} = \tfrac{29}{6} \approx 4.83$. The program prints the same fraction.

??? question "3. A Las Vegas algorithm has expected running time $T$. You run it, and if it has not finished after $2T$ steps you restart it with fresh random bits. Show that the probability of not having finished after $r$ restarts is at most $2^{-r}$, and that the expected total time is at most $4T$."

    Each attempt of $2T$ steps fails with probability at most $1/2$ by Markov, and attempts use independent random
    bits, so $r$ failures in a row have probability at most $2^{-r}$. The number of attempts is geometric with
    success probability at least $1/2$, so its expectation is at most 2 (21.1, Example 4), and each attempt costs at
    most $2T$: total expected time at most $4T$.

??? question "4. In quickselect for rank $k$, show that $z_i$ and $z_j$ ($i < j$) are compared with probability $2/(\max(j,k) - \min(i,k) + 1)$. Sum these for $n = 10$, $k = 5$ and compare with the program."

    Let $B$ be the block of keys from $z_{\min(i,k)}$ to $z_{\max(j,k)}$: it contains $z_i$, $z_j$ and $z_k$. While no
    pivot has been drawn from $B$, the whole block stays in the current sublist (a pivot outside it sends all of $B$
    the same way, and the side containing $z_k$ is kept). The first pivot from $B$ is uniform over $B$. If it is $z_i$
    or $z_j$, they are compared. If it is anything else in $B$, either it separates $z_i$ from $z_j$ (if between
    them), or it separates both from $z_k$ (if it lies between $z_k$ and the pair, so the pair's side is thrown
    away), or it is $z_k$ itself and the algorithm stops; in every case they are never compared. Summing
    $2/(\max(j,k) - \min(i,k) + 1)$ over the 45 pairs for $n = 10$, $k = 5$ gives exactly $24281/1260 \approx
    19.27$, the program's exact value.

    ```python
    from fractions import Fraction
    n, k = 10, 5
    print(sum(Fraction(2, max(j, k) - min(i, k) + 1) for i in range(1, n + 1) for j in range(i + 1, n + 1)))
    # 24281/1260
    ```

??? question "5. For 1000 fair coin flips, bound $P(X \ge 600)$ with Chebyshev and with the Chernoff bound, and compare with the exact value $1.36 \times 10^{-10}$."

    $\mu = 500$, variance $250$. Chebyshev: $250/100^2 = 0.025$. Chernoff with $\delta = 0.2$:
    $\exp(-0.04 \cdot 500/2.2) = e^{-9.09} \approx 1.1 \times 10^{-4}$. Both are true upper bounds; Chernoff is
    about 200 times sharper here, and still a million times above the truth.

??? question "6. Run Karger's contraction algorithm on a tree with $n$ vertices. What is its success probability, and how many minimum cuts are there? Does this contradict anything?"

    A tree has minimum cut 1 (remove any edge). Contraction never creates parallel edges in a tree, so after $n - 2$
    contractions exactly one original edge is left between the two super-vertices: the output is always a minimum
    cut, so the probability of finding *some* minimum cut is 1. There are $n - 1$ minimum cuts, one per edge, and
    each is found with probability $1/(n-1)$ by symmetry of the random order (the surviving edge is the last of
    the $n-1$ edges in the shuffled order). That is at least $1/\binom{n}{2}$ and the count $n - 1 \le \binom{n}{2}$,
    so there is no contradiction.

??? question "7. Prove that reservoir sampling makes every $k$-subset of the first $t$ items equally likely, with probability $1/\binom{t}{k}$."

    Induction on $t$; for $t = k$ the only subset is kept. Take a $k$-set $S$ of items from $1..t$. If $x_t \notin S$,
    the reservoir equals $S$ after step $t$ exactly when it was $S$ before and $x_t$ was rejected:
    $\frac{1}{\binom{t-1}{k}} \cdot \frac{t-k}{t}$. If $x_t \in S$, the reservoir equals $S$ when, before step $t$,
    it was $S \setminus \{x_t\}$ plus some other item $y$ (there are $t - k$ choices of $y$, each with probability
    $1/\binom{t-1}{k}$), and $x_t$ entered and replaced exactly $y$ (probability $\frac{k}{t} \cdot \frac1k = \frac1t$):
    total $\frac{t-k}{t\binom{t-1}{k}}$. Both cases give $\frac{t-k}{t\binom{t-1}{k}}$, and
    $\binom{t}{k} = \frac{t}{t-k}\binom{t-1}{k}$, so the probability is $1/\binom{t}{k}$.

??? question "8. Write the code: Sattolo's algorithm (1986) changes one character of Fisher-Yates so that it produces a uniformly random *cyclic* permutation (a single cycle through all $n$ elements). Write it and check by enumeration for $n = 4$."

    Choose $j$ from $i+1$ to $n-1$ instead of from $i$: there are $(n-1)!$ choice sequences, and there are exactly
    $(n-1)!$ cyclic permutations; an argument like the one for Fisher-Yates shows each appears once.

    ```python
    from itertools import product
    def sattolo(a, choices):
        for i, j in enumerate(choices):      # j in i+1..n-1
            a[i], a[j] = a[j], a[i]
        return "".join(a)
    n = 4
    seen = [sattolo(list("ABCD"), c) for c in product(*[range(i + 1, n) for i in range(n - 1)])]
    print(sorted(seen))
    # ['BCDA', 'BDAC', 'CADB', 'CDBA', 'DABC', 'DCAB']
    ```

    Six distinct results, $3! = 6$. Read each as the map sending position $i$ to the original position of the letter
    now at $i$: BCDA is $0 \to 1 \to 2 \to 3 \to 0$, BDAC is $0 \to 1 \to 3 \to 2 \to 0$, and so on; each of
    the six is a single 4-cycle, and there are exactly $3! = 6$ such cycles.

??? question "9. Continue the splay trace of 21.6: from the tree 1 ((2 (3)) 4 (5)), access 3. Which steps happen, what is the real cost, and what is the amortized cost?"

    3 is the right child of 2, which is the left child of 4: a **zig-zag** (2 rotations) makes 3 the parent of 2
    and 4, as the right child of the root 1. Then 3's parent is the root: a **zig** (1 rotation). The result is
    ((1 (2)) 3 (4 (5))), real cost 3. Sizes: 3 has 5, 1 has 2, 4 has 2, 2 and 5 have 1, so
    $\Phi = \log_2 20 \approx 4.322$, down from $5.322$: amortized cost $3 - 1 = 2$. The lemma allowed
    $3(\log_2 5 - \log_2 1) + 1 \approx 7.97$.

??? question "10. Why does the dynamic table potential use $2\,\mathit{num} - \mathit{size}$ and not simply $\mathit{num}$? What goes wrong with $\Phi = \mathit{num}$ when there are no deletions?"

    With $\Phi = \mathit{num}$ a doubling (from $s$ to $2s$, copying $s$) does not lower the potential at all: it
    goes from $s$ to $s + 1$. The copy cost $s$ is then charged in full to that one insert, and the bound is not
    $O(1)$. The potential must *drop* by about $s$ at the moment of doubling. $2\,\mathit{num} - \mathit{size}$ is
    $s$ just before (full table) and 2 just after, releasing $s - 2$ to pay for the copy, while each ordinary insert
    adds 2 to it: one unit for its own future copy and one for an element that was copied last time.

??? question "11. (Hard) Show that a graph with minimum cut $k$ has at most $\binom{n}{2\alpha} 2^{2\alpha - 1}$ cuts of size at most $\alpha k$, for any $\alpha \ge 1$ with $2\alpha$ an integer."

    Fix such a cut $C$ with $|C| \le \alpha k$. Contract random edges until $r = 2\alpha$ vertices remain. While $j$
    vertices remain, there are at least $jk/2$ edges, so the next edge lies in $C$ with probability at most
    $\alpha k/(jk/2) = 2\alpha/j = r/j$. So $C$ survives with probability at least
    $\prod_{j=r+1}^{n}\frac{j-r}{j} = \frac{(n-r)!\,r!}{n!} = 1/\binom{n}{r}$. Then output a uniformly random cut of
    the $r$-vertex graph; there are $2^{r-1} - 1$ of them, so $C$ is output with probability at least
    $1/\big(\binom{n}{r}2^{r-1}\big)$. These events are disjoint for different cuts, so there are at most
    $\binom{n}{2\alpha}2^{2\alpha-1} = O(n^{2\alpha})$ such cuts. (Karger used this count to build sparse
    "skeleton" graphs that preserve all cuts approximately.)

## What you learned

- Las Vegas algorithms are always right and fast on average; Monte Carlo algorithms are always fast and usually
  right; Markov's inequality and checking turn one into the other.
- Linearity of expectation needs no independence; writing a count as a sum of indicators reduces most analyses to
  one probability per pair or per position.
- Randomized quicksort makes exactly $2(n+1)H_n - 4n \approx 1.386\,n\log_2 n$ comparisons in expectation, because
  $z_i$ and $z_j$ meet with probability $2/(j-i+1)$; quickselect is at most $4n$.
- Markov uses the mean, Chebyshev the variance, Chernoff independence; Chernoff's exponential tails make
  "with high probability" statements and amplification by repetition work.
- Karger's contraction algorithm finds a fixed minimum cut with probability at least $1/\binom{n}{2}$, so repeating
  it $\binom{n}{2}\ln n$ times fails with probability at most $1/n$, and every graph has at most $\binom{n}{2}$
  minimum cuts.
- Fisher-Yates is uniform because its $n!$ choice sequences map one-to-one onto permutations; reservoir sampling
  keeps each item with probability $k/t$, and every $k$-set with equal probability.
- The potential method proves amortized bounds: a dynamic table that halves at a quarter full costs at most 3 per
  operation, and the access lemma gives splay trees $O(\log n)$ amortized per operation.

**Next:** [Chapter 22](22-NP-Completeness.md), the problems for which nobody knows any fast algorithm, randomized or
not, and the theory of reductions that explains why they are all equally hard.

## Further reading

- R. Motwani and P. Raghavan, *Randomized Algorithms*, 1995. The standard textbook; quicksort, min cut, Chernoff
  bounds and much more.
- M. Mitzenmacher and E. Upfal, *Probability and Computing*, 2nd ed., 2017. A gentler route through the same
  probability, with many algorithmic examples.
- T. Cormen, C. Leiserson, R. Rivest and C. Stein, *Introduction to Algorithms*, 4th ed., 2022: chapter 5
  (probabilistic analysis, the hiring problem), chapter 7 (quicksort), chapter 9 (selection) and chapter 16
  (amortized analysis, dynamic tables).
- J. Kleinberg and É. Tardos, *Algorithm Design*, 2005, chapter 13 (randomized algorithms, including Karger's
  algorithm and Chernoff bounds).
- D. Knuth, *The Art of Computer Programming*, volume 2 (*Seminumerical Algorithms*, 3rd ed. 1997), section 3.4.2 on
  shuffling and sampling, and volume 3 (*Sorting and Searching*, 2nd ed. 1998) on quicksort's analysis.
- M. O. Rabin, "Probabilistic Algorithms", in J. F. Traub (ed.), *Algorithms and Complexity: New Directions and
  Recent Results*, 1976.
- H. Chernoff, "A Measure of Asymptotic Efficiency for Tests of a Hypothesis Based on the Sum of Observations",
  *Annals of Mathematical Statistics*, 1952.
- D. Karger, "Global Min-cuts in RNC, and Other Ramifications of a Simple Min-cut Algorithm", SODA 1993; D. Karger
  and C. Stein, "A New Approach to the Minimum Cut Problem", *Journal of the ACM*, 1996.
- J. S. Vitter, "Random Sampling with a Reservoir", *ACM Transactions on Mathematical Software*, 1985.
- R. Durstenfeld, "Algorithm 235: Random Permutation", *Communications of the ACM*, 1964.
- R. E. Tarjan, "Amortized Computational Complexity", *SIAM Journal on Algebraic and Discrete Methods*, 1985.
- D. D. Sleator and R. E. Tarjan, "Self-Adjusting Binary Search Trees", *Journal of the ACM*, 1985.
- On this site: the reference pages [Quicksort](../../sorting/quicksort.md), [Union-find](../../data-structures/union-find.md),
  [Binary search tree](../../data-structures/bst.md), [Hash table](../../data-structures/hash-table.md) and
  [Big-O](../../foundations/big-o.md); [Chapter 8](08-Trees-and-Balanced-Search-Trees.md) for splay trees,
  [Chapter 23](23-Approximation-and-Parameterized-Algorithms.md) for randomized rounding, and
  [Chapter 24](24-Algorithms-for-Big-Data-and-Many-Processors.md) for sketches built on hashing and sampling. The
  [Machine learning](../machine-learning/index.md) book uses the same tail bounds for generalization.
