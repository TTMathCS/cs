# 2. Measuring cost

*Chapter 1 showed that an algorithm taking $n^2$ steps on a billion items runs for decades, while one taking $n$ steps
finishes in a second. To compare algorithms we need a way to talk about growth that ignores what does not matter (the
speed of the machine, the language, small inputs) and keeps what does (how the cost rises with the input). This
chapter builds that language from its definitions: worst, best and average case; Big-O, Big-Omega and Big-Theta, with
the constants that make them precise; the ladder of common growth rates; the rules and the sums you need to analyse
loops; space as well as time; little-o and lower bounds; and finally how to time real Python code without fooling
yourself.*

!!! abstract "In this chapter"
    **You will learn:**

    - why we count operations instead of measuring seconds
    - the difference between worst, best and average case, and how to compute an average
    - the definitions of $O$, $\Omega$ and $\Theta$ with constants $c$ and $n_0$, and how to prove statements with them
    - the growth ladder $1,\log n,n,n\log n,n^2,2^n,n!$ and what each rung means in practice
    - the arithmetic, geometric and harmonic sums, derived, and how they analyse loops
    - how to measure memory use, and (advanced) little-o, limits and lower bounds
    - how to time Python code honestly with `timeit`, and why constants and caches still matter

    **You need:** [Chapter 1](01-What-Is-an-Algorithm.md) (the RAM model, counting steps). Logarithms and exponents
    are explained as we go; if they are rusty, the [math books](https://math.akadian.ca/books/) have a full
    treatment.

    **Levels:** 2.1 to 2.4 are beginner; 2.5 to 2.7 and 2.9 are intermediate; 2.8 is advanced.

## 2.1 Why wall-clock time misleads

You have written two programs that solve the same problem and want to know which is faster. The obvious method is to run
both and look at a clock. Why not stop there?

Because the number you get depends on far more than the algorithm:

- **The machine.** A laptop from ten years ago and one from this year can differ by a factor of ten.
- **The language and its implementation.** The same algorithm in Python and in C often differs by a factor of ten or more,
  because Python does much more work per line (Section 2.9 measures one example).
- **What else is running.** Other programs, the operating system, even the temperature of the processor (modern chips
  slow down when hot) change the time from one run to the next.
- **The input.** One input of size $n$ may be much harder than another of the same size (linear search finds the first
  element at once, and an absent one only after looking at everything).
- **The size you tried.** Most important of all: a time measured at $n=1000$ says little about $n=10^6$. An algorithm
  that wins on small inputs can lose badly on large ones.

A clock reading is a fact about one program, on one machine, on one input. We want a fact about the *algorithm* that
stays true when the machine changes. The answer, already used in Chapter 1, is to **count operations** in the RAM model
and express the count as a function of the input size $n$. Write $T(n)$ for the number of steps on an input of size $n$.
The machine changes $T(n)$ only by a constant factor (each step takes a fixed number of nanoseconds, more on an old
machine, fewer on a new one). How $T(n)$ *grows* with $n$ does not depend on the machine at all.

### What "input size" means

The size $n$ is whatever measure of the input makes the count easy to state.

- For a list, $n$ is the number of elements.
- For a graph (Chapter 15), there are two sizes: the number of points $V$ and of connections $E$; costs are written in
  both, such as $V+E$.
- For a number, the honest size is its number of *digits* (or bits), not its value. Euclid's algorithm on $a$ and $b$
  takes at most about $2\log_2 a$ passes (Exercise 8 of Chapter 1): that is proportional to the number of bits of $a$,
  so it is fast. An algorithm that tries every divisor up to $a$ takes about $a$ steps: that is exponential in the
  number of bits, so it is hopeless for 300-digit numbers, even though "$a$ steps" sounds linear. Confusing these two
  measures is a classic mistake, and it comes back in Chapter 13 (pseudo-polynomial algorithms).

## 2.2 Worst, best and average case

The cost of linear search depends on where $x$ is. For a fixed size $n$, the different inputs give different counts,
and we need to summarise them by one number. There are three standard ways.

- The **worst-case** cost $T_{\text{worst}}(n)$ is the largest cost over all inputs of size $n$.
- The **best-case** cost $T_{\text{best}}(n)$ is the smallest cost over all inputs of size $n$.
- The **average-case** cost $T_{\text{avg}}(n)$ is the average cost over inputs of size $n$, *for a stated probability
  distribution* of the inputs.

For linear search on $n$ distinct items, counting comparisons `a[i] == x`:

- best case: $x=a_0$, one comparison;
- worst case: $x$ is the last element or absent, $n$ comparisons.

### Computing an average

The average case needs an assumption about which inputs are likely. Suppose $x$ is in the list, and it is equally
likely to be at each of the $n$ positions. If $x$ is at position $i$ (counting from 0), the search makes $i+1$
comparisons. Each position has probability $1/n$, so the average is

$$T_{\text{avg}}(n)=\sum_{i=0}^{n-1}\frac{1}{n}(i+1)=\frac{1}{n}(1+2+\dots+n)=\frac{1}{n}\cdot\frac{n(n+1)}{2}=\frac{n+1}{2}.$$

(The sum $1+2+\dots+n=n(n+1)/2$ is derived in 2.6.) The chapter's program checks this by running 20,000 searches for
random elements of a shuffled list of 1000: the measured average is 499.2 against the formula's 500.5, as close as
random sampling allows.

What if $x$ is absent half the time? Then the average is $\tfrac12\cdot\frac{n+1}{2}+\tfrac12\cdot n=\frac{3n+1}{4}$.
The answer changes with the assumption, which is the weakness of average-case analysis: the result is only as good as
the distribution. Real inputs are often far from uniformly random (data arrives nearly sorted; users search for the same
few things again and again).

### Which one to use

In this book, "the running time" means the **worst case** unless we say otherwise. There are good reasons.

1. It is a **guarantee**. No input of size $n$ will take longer. For a rover deciding where to drive, or a server that
   must answer within a deadline, a guarantee is what matters.
2. For many algorithms the worst case happens often (searching for something absent is common).
3. It needs no assumption about the inputs.

The average case is still very useful when the assumption is reasonable, and it explains why some algorithms with a bad
worst case are used everywhere (quicksort, Chapter 5; hash tables, Chapter 7). The best case is mostly useful as a
warning: an algorithm that is fast on its best input tells you almost nothing.

A different idea, which we will use from Chapter 5 on, is a **randomized algorithm**: one that makes random choices
itself. Its **expected** running time is an average over its own coin flips, for the *worst* input. That gives a
guarantee with no assumption about the inputs, and it is a different thing from the average case above, even though
both are averages.

## 2.3 Big-O, Big-Omega and Big-Theta

Chapter 1 found that FIND-MAX takes $T(n)=An+B$ steps, with constants $A$ and $B$ that depend on the machine. The
pairwise algorithm took about $Cn^2$. Two facts made the comparison easy: we did not care about the constants, and we did
not care about small $n$. Asymptotic notation makes exactly those two kinds of carelessness precise.

### Big-O: an upper bound

**Definition.** Let $f$ and $g$ be functions from the positive whole numbers to the non-negative real numbers. We say
$f(n)=O(g(n))$, read "$f$ is big-O of $g$", if there are constants $c>0$ and $n_0\ge1$ such that

$$f(n)\le c\cdot g(n)\quad\text{for every }n\ge n_0.$$

In words: from some point on, $f$ is at most a constant multiple of $g$. The constant $c$ is what lets us ignore the
machine; the starting point $n_0$ is what lets us ignore small inputs.

<figure class="mars-fig" markdown="0">
<svg viewBox="0 0 640 300" role="img" aria-label="A plot of three curves against n from 0 to 20. f of n equals n squared plus 10 n starts above 2 n squared but crosses it at n equals 10 and stays below afterwards. g of n equals n squared is drawn dashed. A vertical dotted line marks n0 equals 10.">
  <line x1="60" y1="260" x2="580" y2="260" stroke="currentColor" stroke-width="1.5"/>
  <line x1="60" y1="260" x2="60" y2="30" stroke="currentColor" stroke-width="1.5"/>
  <text x="585" y="264" font-size="13" fill="currentColor">n</text>
  <text x="60" y="278" font-size="12" text-anchor="middle" fill="currentColor">0</text>
  <text x="185" y="278" font-size="12" text-anchor="middle" fill="currentColor">5</text>
  <text x="310" y="278" font-size="12" text-anchor="middle" fill="currentColor">10</text>
  <text x="435" y="278" font-size="12" text-anchor="middle" fill="currentColor">15</text>
  <text x="560" y="278" font-size="12" text-anchor="middle" fill="currentColor">20</text>
  <text x="52" y="264" font-size="12" text-anchor="end" fill="currentColor">0</text>
  <text x="52" y="157" font-size="12" text-anchor="end" fill="currentColor">400</text>
  <text x="52" y="44" font-size="12" text-anchor="end" fill="currentColor">800</text>
  <line x1="310" y1="260" x2="310" y2="40" stroke="currentColor" stroke-width="1" stroke-dasharray="2 4"/>
  <text x="314" y="292" font-size="13" fill="currentColor">n0 = 10</text>
  <polyline fill="none" stroke="#eea66f" stroke-width="3" points="60.0,260.0 85.0,257.0 110.0,253.4 135.0,249.3 160.0,244.6 185.0,239.4 210.0,233.6 235.0,227.3 260.0,220.4 285.0,213.0 310.0,205.0 335.0,196.5 360.0,187.4 385.0,177.8 410.0,167.6 435.0,156.9 460.0,145.6 485.0,133.8 510.0,121.4 535.0,108.5 560.0,95.0"/>
  <polyline fill="none" stroke="#9cc9ea" stroke-width="3" points="60.0,260.0 85.0,259.4 110.0,257.8 135.0,255.1 160.0,251.2 185.0,246.2 210.0,240.2 235.0,233.1 260.0,224.8 285.0,215.4 310.0,205.0 335.0,193.4 360.0,180.8 385.0,167.1 410.0,152.2 435.0,136.2 460.0,119.2 485.0,101.0 510.0,81.8 535.0,61.4 560.0,40.0"/>
  <polyline fill="none" stroke="currentColor" stroke-width="1.5" stroke-dasharray="6 4" points="60.0,260.0 110.0,258.9 160.0,255.6 210.0,250.1 260.0,242.4 310.0,232.5 360.0,220.4 410.0,206.1 460.0,189.6 510.0,170.9 560.0,150.0"/>
  <circle cx="310" cy="205" r="4" fill="currentColor"/>
  <text x="470" y="62" font-size="13" text-anchor="end" fill="currentColor">c·g(n) = 2n²</text>
  <text x="565" y="112" font-size="13" fill="currentColor">f(n)</text>
  <text x="565" y="154" font-size="13" fill="currentColor">g(n) = n²</text>
  <text x="80" y="60" font-size="13" fill="currentColor">f(n) = n² + 10n is O(n²):</text>
  <text x="80" y="80" font-size="13" fill="currentColor">below 2n² for every n ≥ 10</text>
</svg>
<figcaption>Big-O pictured. The orange curve is f(n) = n² + 10n. It starts above 2n² (blue) but crosses it at
n = 10 and never comes back, so c = 2 and n0 = 10 witness f(n) = O(n²). The dashed curve is n² itself; f is never
below it, which is the Big-Omega half.</figcaption>
</figure>

Two remarks before examples. First, the "$=$" in $f(n)=O(g(n))$ is a traditional abuse of notation: it means "$f$
belongs to the set of functions that grow at most like $g$", and it is one-way. We write $n=O(n^2)$, but never
$O(n^2)=n$. Second, Big-O is only an upper bound. It is true that $n=O(n^2)$, and true that $n=O(2^n)$, though neither is
a useful thing to say about FIND-MAX.

**Example 1.** $f(n)=n^2+10n$ is $O(n^2)$.

*Proof.* We need $c$ and $n_0$ with $n^2+10n\le cn^2$ for $n\ge n_0$. Take $c=2$: the inequality becomes $10n\le n^2$,
that is $n\ge10$. So $c=2$, $n_0=10$ work. Or take $c=11$: since $10n\le10n^2$ for every $n\ge1$, we get
$n^2+10n\le11n^2$ for all $n\ge1$, so $c=11$, $n_0=1$ also work. $\square$

The example shows that the constants are not unique; any pair that works proves the claim. A smaller $c$ usually needs a
larger $n_0$. The figure shows the first pair.

**Example 2.** $3n^2+5n+2=O(n^2)$.

*Proof.* For $n\ge1$ we have $n\le n^2$ and $1\le n^2$, so $3n^2+5n+2\le3n^2+5n^2+2n^2=10n^2$. Take $c=10$, $n_0=1$.
$\square$

The trick, "replace every lower power by the highest power, which is bigger when $n\ge1$", proves that every polynomial
is $O$ of its highest power. We state that as a rule in 2.5.

**Example 3.** $n^2$ is *not* $O(n)$.

*Proof.* Suppose it were: there are $c$ and $n_0$ with $n^2\le cn$ for all $n\ge n_0$. Dividing by $n$ gives $n\le c$ for
all $n\ge n_0$. That fails for any whole number $n$ larger than both $c$ and $n_0$. Contradiction. $\square$

To prove that a Big-O statement is *false*, you show that no constants can work, which is usually a proof by
contradiction like this one.

### Big-Omega: a lower bound

**Definition.** $f(n)=\Omega(g(n))$, "$f$ is big-Omega of $g$", if there are constants $c>0$ and $n_0\ge1$ with

$$f(n)\ge c\cdot g(n)\quad\text{for every }n\ge n_0.$$

It is the mirror image of Big-O: from some point on, $f$ is at least a constant multiple of $g$. Equivalently,
$f=\Omega(g)$ exactly when $g=O(f)$.

**Example 4.** $3n^2+5n+2=\Omega(n^2)$: for all $n\ge1$, $3n^2+5n+2\ge3n^2$, so $c=3$, $n_0=1$.

**Example 5.** $\frac{n^2}{2}-3n=\Omega(n^2)$.

*Proof.* Here a term is subtracted, so we need room. We want $\frac{n^2}{2}-3n\ge\frac{n^2}{4}$, which rearranges to
$\frac{n^2}{4}\ge3n$, that is $n\ge12$. So $c=\frac14$, $n_0=12$. $\square$

### Big-Theta: the exact rate

**Definition.** $f(n)=\Theta(g(n))$, "$f$ is big-Theta of $g$", if $f(n)=O(g(n))$ and $f(n)=\Omega(g(n))$. In other
words, there are constants $c_1,c_2>0$ and $n_0$ with

$$c_1\,g(n)\le f(n)\le c_2\,g(n)\quad\text{for every }n\ge n_0.$$

$\Theta$ says that $f$ and $g$ grow at the same rate, up to constant factors. From examples 2 and 4,
$3n^2+5n+2=\Theta(n^2)$ (with $c_1=3$, $c_2=10$, $n_0=1$). From Chapter 1, FIND-MAX takes $\Theta(n)$ time on every
input, and the pairwise algorithm takes $\Theta(n^2)$.

When people say "this algorithm is $O(n\log n)$", they usually mean $\Theta$ for the worst case, and say $O$ out of
habit. In this book we try to say $\Theta$ when we mean "exactly this rate" and $O$ when we mean "at most". A careful
statement of an algorithm's cost often has the form: "its worst-case running time is $\Theta(n^2)$; its best case is
$\Theta(n)$". Then "the running time is $O(n^2)$" is true of every input, and "the running time is $\Omega(n)$" is true
of every input, but neither $\Theta(n^2)$ nor $\Theta(n)$ describes all inputs.

### A short history

The $O$ symbol comes from number theory, not computing. Paul Bachmann used it in 1894, and Edmund Landau made it
popular in the early twentieth century, which is why it is sometimes called Landau notation; the letter stands for
"Ordnung", German for "order". Knuth's 1976 article "Big Omicron and Big Omega and Big Theta" proposed the uses of
$\Omega$ and $\Theta$ described here, and they have been standard in computer science since.

## 2.4 The growth ladder

A handful of functions describe the running times of nearly every algorithm in this book. Here they are in increasing
order, each one eventually much bigger than the one before.

| growth | name | where it comes from | example |
|---|---|---|---|
| $1$ | constant | a fixed number of steps | read `a[i]`; push onto a stack |
| $\log n$ | logarithmic | halve the problem each step | binary search |
| $n$ | linear | look at each item once | FIND-MAX, linear search |
| $n\log n$ | linearithmic | split in halves, linear work per level | merge sort |
| $n^2$ | quadratic | look at every pair | insertion sort, all pairs |
| $n^3$ | cubic | every triple | naive matrix multiplication |
| $2^n$ | exponential | every subset | try every subset of $n$ items |
| $n!$ | factorial | every ordering | try every route through $n$ places |

### What a logarithm is

The **logarithm** $\log_2 n$ is the power you must raise 2 to in order to get $n$: $\log_2 8=3$ because $2^3=8$. The
useful way to think of it for algorithms: $\log_2 n$ is roughly **how many times you can halve $n$ before reaching 1**.
Halve 1024 and you get 512, 256, 128, 64, 32, 16, 8, 4, 2, 1: ten halvings, and $\log_2 1024=10$. That is why any
algorithm that throws away half of the remaining problem at each step, such as binary search, takes about $\log_2 n$
steps. And it is why logarithms grow so slowly: $\log_2$ of a million is about 20, of a billion about 30. We write
$\lg n$ for $\log_2 n$; when the base does not matter (2.5 shows that in Big-O it never does) we just write $\log n$.

### The numbers

The chapter's program prints the ladder for a few sizes. For values too large to print, it gives the number of digits.

```
        n   lg n      n lg n                n^2               2^n                n!
       10    3.3          33                100             1,024         3,628,800
       20    4.3          86                400         1,048,576       about 10^18
       50    5.6         282              2,500       about 10^15       about 10^64
      100    6.6         664             10,000       about 10^30      about 10^157
    1,000   10.0       9,966          1,000,000      about 10^301     about 10^2567
1,000,000   19.9  19,931,569  1,000,000,000,000   about 10^301029  about 10^5565708
```

Read the rows at a speed of $10^9$ steps per second. At $n=10^6$, an $n\lg n$ algorithm needs 0.02 seconds and an $n^2$
one about 17 minutes. At $n=100$, $2^n$ steps would take about $10^{21}$ seconds, tens of trillions of years; for
comparison, the age of the universe is under $10^{18}$ seconds. An exponential algorithm is fine for $n=20$ (a million
steps) and useless for $n=100$. This is the line between the **polynomial** rungs ($n^k$ for a fixed $k$), which we call
efficient, and the exponential ones, which we do not. Chapter 22 makes that line the centre of the theory of P and NP.

<figure class="mars-fig" markdown="0">
<svg viewBox="0 0 640 310" role="img" aria-label="Plot of growth functions for n from 1 to 20 with the vertical axis from 0 to 100. n factorial and 2 to the n shoot off the top before n equals 6 and n equals 8. n squared leaves the top at n equals 10. n log n reaches about 86 at n equals 20. n reaches 20, and log n stays below 5.">
  <line x1="60" y1="270" x2="580" y2="270" stroke="currentColor" stroke-width="1.5"/>
  <line x1="60" y1="270" x2="60" y2="30" stroke="currentColor" stroke-width="1.5"/>
  <text x="590" y="274" font-size="13" fill="currentColor">n</text>
  <text x="60" y="288" font-size="12" text-anchor="middle" fill="currentColor">1</text>
  <text x="191.6" y="288" font-size="12" text-anchor="middle" fill="currentColor">6</text>
  <text x="323.2" y="288" font-size="12" text-anchor="middle" fill="currentColor">11</text>
  <text x="454.7" y="288" font-size="12" text-anchor="middle" fill="currentColor">16</text>
  <text x="560" y="288" font-size="12" text-anchor="middle" fill="currentColor">20</text>
  <text x="52" y="274" font-size="12" text-anchor="end" fill="currentColor">0</text>
  <text x="52" y="159" font-size="12" text-anchor="end" fill="currentColor">50</text>
  <text x="52" y="44" font-size="12" text-anchor="end" fill="currentColor">100</text>
  <line x1="60" y1="40" x2="580" y2="40" stroke="currentColor" stroke-width="0.8" stroke-dasharray="2 4"/>
  <polyline fill="none" stroke="currentColor" stroke-width="2" points="60.0,270.0 86.3,267.7 112.6,266.4 138.9,265.4 165.3,264.7 191.6,264.1 217.9,263.5 244.2,263.1 270.5,262.7 296.8,262.4 323.2,262.0 349.5,261.8 375.8,261.5 402.1,261.2 428.4,261.0 454.7,260.8 481.1,260.6 507.4,260.4 533.7,260.2 560.0,260.1"/>
  <polyline fill="none" stroke="#7ccf9a" stroke-width="2.5" points="60.0,267.7 560.0,224.0"/>
  <polyline fill="none" stroke="#9cc9ea" stroke-width="2.5" points="60.0,270.0 86.3,265.4 112.6,259.1 138.9,251.6 165.3,243.3 191.6,234.3 217.9,224.8 244.2,214.8 270.5,204.4 296.8,193.6 323.2,182.5 349.5,171.1 375.8,159.4 402.1,147.4 428.4,135.2 454.7,122.8 481.1,110.2 507.4,97.4 533.7,84.4 560.0,71.2"/>
  <polyline fill="none" stroke="#eea66f" stroke-width="2.5" points="60.0,267.7 81.1,262.5 102.1,254.5 123.2,243.4 144.2,229.4 165.3,212.5 186.3,192.6 207.4,169.8 228.4,144.1 249.5,115.3 270.5,83.7 291.6,49.1 296.8,40.0"/>
  <polyline fill="none" stroke="#eea66f" stroke-width="2.5" stroke-dasharray="7 4" points="60.0,265.4 81.1,262.0 102.1,256.1 123.2,245.7 144.2,227.7 165.3,196.4 175.8,172.9 186.3,141.9 196.8,100.9 207.4,46.9 208.5,40.0"/>
  <polyline fill="none" stroke="currentColor" stroke-width="2" stroke-dasharray="3 3" points="60.0,267.7 81.1,266.1 102.1,261.5 112.6,256.2 123.2,246.7 133.7,229.0 144.2,195.1 154.7,128.4 160.0,73.1 162.4,40.0"/>
  <text x="140" y="34" font-size="13" text-anchor="middle" fill="currentColor">n!</text>
  <text x="214" y="34" font-size="13" text-anchor="middle" fill="currentColor">2ⁿ</text>
  <text x="300" y="34" font-size="13" text-anchor="middle" fill="currentColor">n²</text>
  <text x="566" y="74" font-size="13" fill="currentColor">n lg n</text>
  <text x="566" y="228" font-size="13" fill="currentColor">n</text>
  <text x="566" y="262" font-size="13" fill="currentColor">lg n</text>
</svg>
<figcaption>The growth ladder for n from 1 to 20, cut off at 100 steps. Even at these tiny sizes the order is
clear: n! and 2ⁿ leave the picture first, then n²; n lg n bends upward slowly; lg n is almost flat.</figcaption>
</figure>

Two habits help when reading such tables. First, *double the input and see what happens to the cost*: for $\lg n$ it
goes up by 1; for $n$ it doubles; for $n\lg n$ it slightly more than doubles; for $n^2$ it multiplies by 4; for $n^3$ by
8; for $2^n$ it *squares*. Second, *ask what a faster machine buys you*: with a machine 1000 times faster, in the same
time an $n$ algorithm handles inputs 1000 times bigger, an $n^2$ algorithm about 32 times bigger ($\sqrt{1000}$), and a
$2^n$ algorithm inputs bigger by only about 10 items ($2^{10}\approx1000$).

<figure class="play" data-play="growth"><span class="ai-tag">AI-created</span><figcaption>Try it: move n and see how long lg n, n, n lg n, n² and 2ⁿ steps take at 10⁹ steps a second, the speed this page uses.</figcaption></figure>

## 2.5 Rules for working with growth rates

*Level: intermediate.* Proving every Big-O fact from the definition gets tedious. A few rules, each proved once from the
definition, do almost all the work.

**Rule 1 (constant factors).** For any constant $k>0$, $k\cdot f(n)=\Theta(f(n))$.

*Proof.* $k f(n)\le k\cdot f(n)$ and $kf(n)\ge k\cdot f(n)$ for all $n$; take $c_1=c_2=k$, $n_0=1$. $\square$

**Rule 2 (sums).** If $f_1=O(g_1)$ and $f_2=O(g_2)$, then $f_1+f_2=O(\max(g_1,g_2))$. In particular, if $f_2=O(f_1)$ then
$f_1+f_2=\Theta(f_1)$: in a sum, the fastest-growing term wins.

*Proof.* We have $f_1(n)\le c_1g_1(n)$ for $n\ge n_1$ and $f_2(n)\le c_2g_2(n)$ for $n\ge n_2$. For
$n\ge\max(n_1,n_2)$, both hold, so $f_1(n)+f_2(n)\le c_1g_1(n)+c_2g_2(n)\le(c_1+c_2)\max(g_1(n),g_2(n))$. $\square$

This rule is what lets us analyse a program as a sequence of parts: a $\Theta(n)$ loop followed by a $\Theta(n^2)$
loop is $\Theta(n^2)$ in all.

**Rule 3 (products).** If $f_1=O(g_1)$ and $f_2=O(g_2)$, then $f_1f_2=O(g_1g_2)$.

*Proof.* For $n$ beyond both starting points, $f_1(n)f_2(n)\le c_1g_1(n)\cdot c_2g_2(n)=(c_1c_2)\,g_1(n)g_2(n)$, using
that all the values are non-negative. $\square$

This rule is for nested loops: a loop of $O(n)$ passes whose body costs $O(\log n)$ costs $O(n\log n)$.

**Rule 4 (transitivity).** If $f=O(g)$ and $g=O(h)$ then $f=O(h)$; the same for $\Omega$ and $\Theta$.

*Proof.* $f(n)\le c_1g(n)\le c_1c_2h(n)$ once $n$ is past both starting points. $\square$

**Rule 5 (polynomials).** If $p(n)=a_dn^d+a_{d-1}n^{d-1}+\dots+a_0$ with $a_d>0$, then $p(n)=\Theta(n^d)$.

*Proof.* Upper bound: for $n\ge1$, each $|a_i|n^i\le|a_i|n^d$, so $p(n)\le(|a_d|+\dots+|a_0|)\,n^d$. Lower bound: let
$A=|a_{d-1}|+\dots+|a_0|$. For $n\ge1$, the lower terms total at least $-An^{d-1}$, so
$p(n)\ge a_dn^d-An^{d-1}=n^{d-1}(a_dn-A)$. When $n\ge2A/a_d$ we have $a_dn-A\ge a_dn/2$, so $p(n)\ge\frac{a_d}{2}n^d$.
$\square$

**Rule 6 (logarithms of any base).** For any bases $a,b>1$, $\log_a n=\Theta(\log_b n)$.

*Proof.* The change-of-base formula says $\log_a n=\dfrac{\log_b n}{\log_b a}$. (If $a^x=n$, take $\log_b$ of both sides:
$x\log_b a=\log_b n$.) So $\log_a n$ is $\log_b n$ times the constant $1/\log_b a$, and Rule 1 applies. $\square$

That is why we write $O(\log n)$ without a base: changing the base only changes the constant. (In an *exponent* the base
matters: $2^{\log_2 n}=n$ but $2^{\log_4 n}=\sqrt n$.)

**Rule 7 (the ladder is strict).** For constants $k\ge1$ and $\varepsilon>0$: $\log n=O(n^\varepsilon)$ but not the
reverse; $n^k=O(2^n)$ but not the reverse; $2^n=O(n!)$ but not the reverse. Logs grow slower than any power, powers
slower than exponentials. We prove these with limits in 2.8.

**A worked fact: $\log(n!)=\Theta(n\log n)$.** This comes up in Chapter 5 (the sorting lower bound), and it is a good
example of bounding something you cannot compute exactly.

*Proof.* Upper: $n!=1\cdot2\cdots n\le n\cdot n\cdots n=n^n$, so $\log(n!)\le n\log n$. Lower: at least half of the
factors $1,\dots,n$ are at least $n/2$ (the ones from $\lceil n/2\rceil$ up), so $n!\ge(n/2)^{n/2}$ and
$\log(n!)\ge\frac n2\log\frac n2=\frac n2(\log n-\log 2)$. For $n\ge4$, $\log 2\le\frac12\log n$, so
$\log(n!)\ge\frac n4\log n$. $\square$

## 2.6 Analysing loops: the three sums

*Level: intermediate.* Analysing an algorithm usually means counting how many times its innermost line runs. For loops,
that count is a **sum**, and three sums cover nearly every case. The chapter's program counts five typical loops and
compares them with the formulas derived here.

```python
--8<-- "books/algorithms/ch02_counting.py"
```

Output:

```
Loop counts against their formulas
     n  single    nested  n(n-1)/2  doubling floor(lg n)+1  harmonic     n*H_n
    10      10       100        45         4             4        33      29.3
   100     100     10000      4950         7             7       573     518.7
  1000    1000   1000000    499500        10            10      8053    7485.5

Linear search on n = 1000 distinct items
  best case  : 1 comparison
  worst case : 1000 comparisons (x absent)
  average over 20000 random present x: 499.2   formula (n+1)/2 = 500.5

The growth ladder (number of steps)
        n   lg n      n lg n                n^2               2^n                n!
       10    3.3          33                100             1,024         3,628,800
       20    4.3          86                400         1,048,576       about 10^18
       50    5.6         282              2,500       about 10^15       about 10^64
      100    6.6         664             10,000       about 10^30      about 10^157
    1,000   10.0       9,966          1,000,000      about 10^301     about 10^2567
1,000,000   19.9  19,931,569  1,000,000,000,000   about 10^301029  about 10^5565708
```

### Sequential and nested loops

A single loop `for i in range(n)` with a constant-cost body runs $n$ times: $\Theta(n)$. Two nested loops, each over
`range(n)`, run the inner body $n\cdot n=n^2$ times: $\Theta(n^2)$. Those are Rule 3. The interesting cases are loops whose
bounds depend on each other.

### The arithmetic sum

In the "triangle" loop the inner loop runs over $j=i+1,\dots,n-1$, which is $n-1-i$ passes. Adding over $i=0,\dots,n-1$:

$$(n-1)+(n-2)+\dots+1+0=\sum_{k=0}^{n-1}k.$$

**Claim.** $1+2+\dots+m=\dfrac{m(m+1)}{2}$.

*Proof.* Write the sum $S$ forwards and backwards and add the two lines term by term:

$$\begin{aligned}S&=1+2+\dots+m\\ S&=m+(m-1)+\dots+1\\ 2S&=(m+1)+(m+1)+\dots+(m+1)=m(m+1).\end{aligned}$$

Each column adds to $m+1$, and there are $m$ columns. $\square$

So the triangle loop runs $\frac{(n-1)n}{2}$ times, which is $\Theta(n^2)$: half the nested loop, but the same rate. The
program confirms 45, 4950 and 499,500. A useful general fact: $\sum_{k=1}^m k^d=\Theta(m^{d+1})$ for each fixed $d$. (Upper
bound: each of the $m$ terms is at most $m^d$. Lower bound: the last $m/2$ terms are each at least $(m/2)^d$, so the sum
is at least $(m/2)^{d+1}$.)

The story that the young Carl Friedrich Gauss found this trick at school is often told, but the details vary from
version to version and are not well documented, so treat it as a story.

### The geometric sum

In the "doubling" loop, $i$ takes the values $1,2,4,8,\dots$ as long as $i\le n$. The number of passes is the number of
powers of 2 that are at most $n$, which is $\lfloor\lg n\rfloor+1$. (The **floor** $\lfloor x\rfloor$ is $x$ rounded
down to a whole number.) So the loop runs $\Theta(\log n)$ times: for $n=1000$, ten passes ($1,2,\dots,512$).

Geometric growth also appears in the *total* work of many algorithms, and then we need the sum of the powers.

**Claim.** For $r\ne1$, $1+r+r^2+\dots+r^m=\dfrac{r^{m+1}-1}{r-1}$.

*Proof.* Call the sum $S$. Then $rS=r+r^2+\dots+r^{m+1}$. Subtract: $rS-S=r^{m+1}-1$, since everything else cancels.
Divide by $r-1$. $\square$

Two consequences are used again and again.

- If $r>1$, the sum is less than $\frac{r}{r-1}$ times its **largest** term $r^m$. For $r=2$: $1+2+4+\dots+2^m=2^{m+1}-1$,
  less than twice the last term. A doubling process costs, in total, about as much as its last step. Chapter 4 uses this
  to show that a growing array costs $O(1)$ per insertion on average.
- If $0<r<1$, the sum is less than $\frac{1}{1-r}$, a constant, however large $m$ is. For $r=\frac12$:
  $1+\frac12+\frac14+\dots<2$. A process whose steps shrink geometrically costs about as much as its **first** step.
  Chapter 3 uses this in the master theorem.

### The harmonic sum

In the "harmonic" loop, for each $i$ from 1 to $n$ the inner loop steps through $0,i,2i,\dots$ below $n$, which is
$\lceil n/i\rceil$ passes (the **ceiling** $\lceil x\rceil$ rounds up). So the total is about

$$\frac n1+\frac n2+\frac n3+\dots+\frac nn=n\left(1+\frac12+\dots+\frac1n\right)=n\,H_n,$$

where $H_n=\sum_{k=1}^n\frac1k$ is the $n$-th **harmonic number**. (The rounding up adds less than 1 per value of $i$,
so less than $n$ in all, which is why the program's counts are a little above $nH_n$.) How big is $H_n$?

**Claim.** $\ln(n+1)\le H_n\le1+\ln n$, where $\ln$ is the natural logarithm. So $H_n=\Theta(\log n)$.

*Proof.* Compare the sum with the area under the curve $y=1/x$. The area from $x=1$ to $x=m$ is $\ln m$. On the interval
from $k$ to $k+1$, the curve lies below $1/k$ and above $1/(k+1)$, because $1/x$ decreases.

- A rectangle of height $\frac1k$ on $[k,k+1]$ lies above the curve, so $\frac1k\ge\int_k^{k+1}\frac{dx}{x}$. Adding for
  $k=1,\dots,n$: $H_n\ge\int_1^{n+1}\frac{dx}{x}=\ln(n+1)$.
- A rectangle of height $\frac1k$ on $[k-1,k]$ lies below the curve, so $\frac1k\le\int_{k-1}^k\frac{dx}{x}$. Adding for
  $k=2,\dots,n$ and keeping the first term: $H_n\le1+\int_1^n\frac{dx}{x}=1+\ln n$. $\square$

<figure class="mars-fig" markdown="0">
<svg viewBox="0 0 620 290" role="img" aria-label="Bars of width 1 and heights 1, one half, one third and so on up to one eighth, standing on the intervals from 1 to 9. The curve y equals 1 over x passes through the top left corner of each bar and stays below the bars, so the total area of the bars is more than the area under the curve.">
  <line x1="60" y1="250" x2="580" y2="250" stroke="currentColor" stroke-width="1.5"/>
  <line x1="60" y1="250" x2="60" y2="50" stroke="currentColor" stroke-width="1.5"/>
  <text x="590" y="254" font-size="13" fill="currentColor">x</text>
  <rect x="60" y="70" width="60" height="180" fill="#9cc9ea" fill-opacity="0.45" stroke="currentColor" stroke-width="1"/>
  <rect x="120" y="160" width="60" height="90" fill="#9cc9ea" fill-opacity="0.45" stroke="currentColor" stroke-width="1"/>
  <rect x="180" y="190" width="60" height="60" fill="#9cc9ea" fill-opacity="0.45" stroke="currentColor" stroke-width="1"/>
  <rect x="240" y="205" width="60" height="45" fill="#9cc9ea" fill-opacity="0.45" stroke="currentColor" stroke-width="1"/>
  <rect x="300" y="214" width="60" height="36" fill="#9cc9ea" fill-opacity="0.45" stroke="currentColor" stroke-width="1"/>
  <rect x="360" y="220" width="60" height="30" fill="#9cc9ea" fill-opacity="0.45" stroke="currentColor" stroke-width="1"/>
  <rect x="420" y="224.3" width="60" height="25.7" fill="#9cc9ea" fill-opacity="0.45" stroke="currentColor" stroke-width="1"/>
  <rect x="480" y="227.5" width="60" height="22.5" fill="#9cc9ea" fill-opacity="0.45" stroke="currentColor" stroke-width="1"/>
  <polyline fill="none" stroke="#eea66f" stroke-width="3" points="60.0,70.0 72.0,100.0 84.0,121.4 96.0,137.5 108.0,150.0 120.0,160.0 132.0,168.2 144.0,175.0 156.0,180.8 168.0,185.7 180.0,190.0 192.0,193.8 204.0,197.1 216.0,200.0 228.0,202.6 240.0,205.0 252.0,207.1 264.0,209.1 276.0,210.9 288.0,212.5 300.0,214.0 312.0,215.4 324.0,216.7 336.0,217.9 348.0,219.0 360.0,220.0 372.0,221.0 384.0,221.9 396.0,222.7 408.0,223.5 420.0,224.3 432.0,225.0 444.0,225.7 456.0,226.3 468.0,226.9 480.0,227.5 492.0,228.0 504.0,228.6 516.0,229.1 528.0,229.5 540.0,230.0"/>
  <text x="60" y="268" font-size="12" text-anchor="middle" fill="currentColor">1</text>
  <text x="120" y="268" font-size="12" text-anchor="middle" fill="currentColor">2</text>
  <text x="180" y="268" font-size="12" text-anchor="middle" fill="currentColor">3</text>
  <text x="240" y="268" font-size="12" text-anchor="middle" fill="currentColor">4</text>
  <text x="300" y="268" font-size="12" text-anchor="middle" fill="currentColor">5</text>
  <text x="360" y="268" font-size="12" text-anchor="middle" fill="currentColor">6</text>
  <text x="420" y="268" font-size="12" text-anchor="middle" fill="currentColor">7</text>
  <text x="480" y="268" font-size="12" text-anchor="middle" fill="currentColor">8</text>
  <text x="540" y="268" font-size="12" text-anchor="middle" fill="currentColor">9</text>
  <text x="90" y="64" font-size="12" text-anchor="middle" fill="currentColor">1</text>
  <text x="150" y="154" font-size="12" text-anchor="middle" fill="currentColor">1/2</text>
  <text x="210" y="184" font-size="12" text-anchor="middle" fill="currentColor">1/3</text>
  <text x="270" y="199" font-size="12" text-anchor="middle" fill="currentColor">1/4</text>
  <text x="300" y="90" font-size="13" fill="currentColor">bars: 1 + 1/2 + ... + 1/8 = H₈ ≈ 2.72</text>
  <text x="300" y="112" font-size="13" fill="currentColor">area under y = 1/x from 1 to 9: ln 9 ≈ 2.20</text>
  <text x="300" y="134" font-size="13" fill="currentColor">bars lie above the curve, so H₈ ≥ ln 9</text>
</svg>
<figcaption>Why the harmonic number grows like a logarithm. Each bar has width 1 and height 1/k, and the curve 1/x
(orange) stays under the bars, so H_n is at least ln(n+1). Shifting every bar one place left puts it under the curve,
which gives H_n at most 1 + ln n.</figcaption>
</figure>

So the harmonic loop costs $\Theta(n\log n)$, which is not obvious from looking at it: the inner loops get shorter so fast
that the total is far below $n^2$. The harmonic sum turns up in quicksort's analysis (Chapter 5), in the coupon
collector problem, and in the sieve of Eratosthenes (Chapter 19, where a sum over primes only gives $n\log\log n$).

### A recipe for loops

1. Find the line that runs the most (the innermost body), and check that every other line runs at most a constant times
   as often.
2. Write its count as a sum, with one $\sum$ per loop, inner bounds in terms of outer variables.
3. Evaluate the sum with the three formulas, or bound it above and below if an exact value is messy.
4. Simplify with the rules of 2.5.

Be careful with lines that are not constant cost (1.5): `if x in a` inside a loop over `a` is a nested loop in disguise.

## 2.7 Space cost

*Level: intermediate.* Time is not the only resource. An algorithm also needs **memory**, and memory can run out first:
a phone has far less of it than a server, and a rover's flight computer far less than a phone. The **space cost** $S(n)$
of an algorithm is the amount of memory it uses, in words, as a function of the input size.

We usually count only the **auxiliary space**: memory used *beyond* the input itself. That way an algorithm that reads a
list of $n$ items and uses three extra variables has auxiliary space $\Theta(1)$, even though the list takes $n$ words.

- FIND-MAX uses $\Theta(1)$ extra space: `best` and `i`.
- Making a sorted copy with `sorted(a)` uses $\Theta(n)$ extra space: the new list.
- An algorithm that builds a table of every pair uses $\Theta(n^2)$ space; for $n=10^5$ that is $10^{10}$ words, 80
  gigabytes, which does not fit in most computers.

An algorithm is called **in place** if it uses $O(1)$ auxiliary space (some authors allow $O(\log n)$). Reversing a list
by swapping its ends inward is in place:

```python
def reverse_in_place(a):
    i, j = 0, len(a) - 1
    while i < j:
        a[i], a[j] = a[j], a[i]
        i, j = i + 1, j - 1
```

`a[::-1]` gives the same result but builds a new list, $\Theta(n)$ extra space.

Three things are easy to overlook when counting space:

1. **The call stack.** A recursive function uses one stack frame per active call (Chapter 3 draws it). A recursion $n$
   deep uses $\Theta(n)$ space even if each call has only two variables.
2. **Hidden copies.** In Python, `a[1:]`, `a + b`, `list(x)` and string concatenation all build new objects.
3. **Real sizes.** In the RAM model a word holds one number. In Python, every integer is an object of about 28 bytes and a
   list holds 8-byte references to them, so a list of a million small integers takes tens of megabytes.

Time and space trade against each other. Storing answers you have computed (Chapter 13's dynamic programming) spends
space to save time; recomputing them saves space and spends time. A basic fact connects them: an algorithm that runs for
$T$ steps can touch at most $T$ memory cells (one per step at most), so its space cannot be larger than its time, if we
count only the cells it actually uses.

## 2.8 Little-o, little-omega, and lower bounds

*Level: advanced.* Big-O allows equality of rates: $2n=O(n)$. Sometimes we want to say "strictly slower". And so far all
our bounds are for particular algorithms; we also want to say something about *every possible* algorithm for a problem.
This section does both.

### Little-o and little-omega

**Definition.** $f(n)=o(g(n))$, "$f$ is little-o of $g$", if for **every** constant $c>0$ there is an $n_0$ such that
$f(n)<c\cdot g(n)$ for all $n\ge n_0$. Similarly, $f(n)=\omega(g(n))$ if for every $c>0$ there is an $n_0$ with
$f(n)>c\cdot g(n)$ for all $n\ge n_0$.

Compare with Big-O: there, *some* constant works; here, *every* constant works, however small. So $f=o(g)$ means $f$
becomes negligible compared to $g$. When $g(n)>0$ for large $n$, this is the same as a limit:

$$f(n)=o(g(n))\iff\lim_{n\to\infty}\frac{f(n)}{g(n)}=0,\qquad f(n)=\omega(g(n))\iff\lim_{n\to\infty}\frac{f(n)}{g(n)}=\infty.$$

Limits also give a quick test for $\Theta$:

**Limit rule.** If $\lim_{n\to\infty}f(n)/g(n)=L$ with $0<L<\infty$, then $f=\Theta(g)$.

*Proof.* By the definition of a limit, there is an $n_0$ beyond which $f(n)/g(n)$ lies between $L/2$ and $2L$. So
$\frac L2g(n)\le f(n)\le2L\,g(n)$ for $n\ge n_0$. $\square$

(The rule does not work backwards: the limit may not exist even when $f=\Theta(g)$. For example $f(n)=(2+(-1)^n)\,n$
alternates between $n$ and $3n$; it is $\Theta(n)$, but $f(n)/n$ has no limit.)

Now we can prove Rule 7 of 2.5.

**Claim.** For every fixed $k$, $n^k=o(2^n)$.

*Proof.* Let $u_n=n^k/2^n$. The ratio of consecutive terms is
$\frac{u_{n+1}}{u_n}=\frac12\left(1+\frac1n\right)^k$. As $n$ grows, $(1+\frac1n)^k\to1$, so for large enough $n$, say
$n\ge N$, the ratio is at most $\frac34$. Then $u_{N+m}\le u_N\left(\frac34\right)^m$, which tends to 0 as $m$ grows.
$\square$

**Claim.** For every fixed $\varepsilon>0$, $\log_2 n=o(n^\varepsilon)$.

*Proof.* Put $n=2^m$. Then $\frac{\log_2 n}{n^\varepsilon}=\frac{m}{2^{\varepsilon m}}=\frac{m}{(2^\varepsilon)^m}$. Since
$2^\varepsilon>1$, the same ratio argument as above shows this tends to 0 as $m\to\infty$ (and the ratio is monotone
enough between powers of 2 for the conclusion to hold for all $n$). $\square$

**Claim.** $2^n=o(n!)$. *Proof.* $\frac{2^n}{n!}=\frac21\cdot\frac22\cdot\frac23\cdots\frac2n\le2\cdot\left(\frac23\right)^{n-2}$
for $n\ge2$, since every factor from the third on is at most $\frac23$. This tends to 0. $\square$

So even $\log n$ to the hundredth power is eventually smaller than $n^{0.01}$, and $n^{100}$ is eventually smaller than
$1.01^n$. "Eventually" can be very late, which is why practical comparisons also need constants (2.9).

### Lower bounds: what no algorithm can do

An upper bound is a statement about *one* algorithm: "merge sort takes at most $cn\log n$ steps". A **lower bound for a
problem** is a statement about *all* algorithms: "every algorithm that solves this problem, in this model, takes at
least $f(n)$ steps on some input of size $n$, in the worst case". Proving one requires a precise **model of
computation**, a list of the operations an algorithm may use, because a lower bound in one model can be beaten in a more
powerful one (Chapter 6 sorts faster than the comparison lower bound by using operations that comparison sorts are not
allowed).

When a problem's lower bound matches an algorithm's upper bound, the algorithm is **asymptotically optimal**, and the
problem's complexity is settled. Three examples, in increasing order of difficulty.

**1. Reading the input.** If the correct output can depend on every part of the input, an algorithm must look at every
part, so it needs $\Omega(n)$ steps. This **trivial lower bound** already shows FIND-MAX is optimal up to constants;
Chapter 1 proved the sharper bound $n-1$ comparisons.

**2. Search in an unsorted list needs $n$ comparisons.** *Model:* the algorithm may compare $x$ with list elements, asking
"is $a_i=x$?", in any order it likes, chosen adaptively. *Claim:* in the worst case it must ask about all $n$ positions.
*Proof by adversary.* An **adversary** argument imagines an opponent who answers the algorithm's questions, choosing the
answers to make the algorithm work as hard as possible, but always consistently with *some* input. Here the adversary
answers "no" to every question. Suppose the algorithm stops after asking about fewer than $n$ positions; some position $j$
was never asked about. If the algorithm answers "absent", the adversary reveals an input with $a_j=x$; if it answers any
position, the adversary reveals an input with $x$ absent. Both inputs agree with every "no" given, so the algorithm's
answer is wrong on one of them. $\square$

**3. Search in a sorted list needs $\lceil\lg(n+1)\rceil$ comparisons.** *Model:* the list holds $n$ distinct numbers in
increasing order; each comparison compares $x$ with some $a_i$ (any $i$, chosen adaptively) and has three outcomes,
$x<a_i$, $x=a_i$ or $x>a_i$. *Proof by decision tree.* Draw the algorithm as a **decision tree**: the first comparison
at the root, its possible outcomes as branches, the next comparison on each branch, and so on. An "$=$" outcome ends the
search, so only the "$<$" and "$>$" branches continue: the comparisons form a binary tree. Now, the algorithm can only
answer "$x$ is at position $i$" after it has seen $x=a_i$ (otherwise an adversary could change $x$ slightly, keeping
every answer the same, and make that answer wrong). So for each of the $n$ positions some node of the tree compares with
$a_i$, and the tree has at least $n$ nodes. A binary tree whose longest root-to-node path has $h$ nodes has at most
$1+2+4+\dots+2^{h-1}=2^h-1$ nodes (each level at most doubles; the sum is the geometric sum of 2.6). So $2^h-1\ge n$,
that is $h\ge\lg(n+1)$, and since $h$ is a whole number, $h\ge\lceil\lg(n+1)\rceil$. Following the longest path takes $h$
comparisons, which is the worst case. $\square$

Binary search ([reference page](../../searching/binary-search.md); Chapter 7) matches this bound, so it is optimal. The
same decision-tree argument, with $n!$ leaves for the $n!$ possible orders, gives the famous $\Omega(n\log n)$ lower bound
for comparison sorting in Chapter 5; and our worked fact $\log(n!)=\Theta(n\log n)$ from 2.5 is exactly what it needs.

Lower bounds beyond these simple models are among the hardest open problems in computer science. For problems in NP
(Chapter 22), nobody has proved a lower bound much above linear time on a general RAM, and Chapter 25 explains why such proofs
are so hard to find.

## 2.9 Measuring for real

*Level: intermediate.* Asymptotic analysis tells you which algorithm wins for large $n$. It does not tell you how large
"large" is, nor which of two $\Theta(n)$ algorithms is faster. For that you have to measure, and measuring well takes some
care.

### Timing honestly

Python's standard library has a module for exactly this, `timeit`. It runs a statement many times in a loop with
garbage collection switched off, and measures with the most precise clock available. The rules the chapter's program
follows are the ones to follow in general.

1. **Time many runs, not one.** A single run of a fast statement is shorter than the clock's resolution and the noise.
   Run it enough times that the whole batch takes a noticeable fraction of a second, and divide.
2. **Repeat the batch and take the minimum.** Other programs and the operating system can only make a run *slower*, never
   faster, so the minimum is the best estimate of the code's own cost. (Report the spread too if you care about variation.)
3. **Time only what you mean to time.** Build the input outside the timed statement. Never time `print`.
4. **Try several sizes.** One size tells you a cost; several sizes tell you a growth rate. A **doubling experiment** runs
   at $n,2n,4n,\dots$ and looks at the ratio of successive times: a ratio near 2 suggests $\Theta(n)$, near 4 suggests
   $\Theta(n^2)$, a ratio slightly above 2 suggests $\Theta(n\log n)$.
5. **Check the answer.** A fast wrong program is not a result.

```python
--8<-- "books/algorithms/ch02_timing.py"
```

One run's output (times will differ on your machine, and from run to run on the same one):

```
1. Same O(n) work, different constants: summing a list
  n=  10000: Python loop    260.9 us   built-in sum    97.5 us   ratio  2.7
  n= 100000: Python loop   2712.1 us   built-in sum  1207.3 us   ratio  2.2

2. Different growth: membership test in a list (O(n)) vs a set (O(1) expected)
  n=   1000: list      6.83 us   set  0.051 us
  n=  10000: list    119.90 us   set  0.048 us
  n= 100000: list    749.15 us   set  0.039 us

3. Same operation count, different memory order: summing via an index list
  in order   34.9 ms   shuffled order  546.9 ms   ratio 15.7
```

("us" is microseconds, millionths of a second.) Read the three experiments.

**1. Constants matter.** Both ways of summing do $\Theta(n)$ work; both times grow about tenfold when $n$ grows tenfold.
But the built-in `sum`, written in C inside the Python interpreter, is two to three times faster than the Python loop,
because each pass of the Python loop does much more work: it looks up the variable, checks the types, creates a new
integer object for the running total. The Big-O is the same; the constant is not. When two algorithms have the same
growth rate, the constant is the whole story.

**2. Growth matters more.** `x in a` on a list is a linear search: its time grows roughly in proportion to $n$ (the
measurements are noisy, as small timings on a shared machine are, but the trend over a factor of 100 in $n$ is clear).
`x in s` on a set uses a hash table (Chapter 7) and takes about the same tiny time at every size. At $n=100{,}000$ the
set is more than ten thousand times faster. No constant-factor tuning of a linear search can catch up with that.

**3. Memory order matters.** Both statements do exactly the same operations: a million lookups `a[i]` and a million
additions. The only difference is the order of the indices. In order, they take about 35 milliseconds; shuffled, about
fifteen times longer. The RAM model, in which every memory access costs one step, cannot explain this. Real memory can.

### Caches

A modern processor can do an addition far faster than it can fetch a value from main memory. To hide this gap, it keeps
small, fast copies of recently used memory in **caches**: typically a tiny, very fast level-1 cache, a larger level-2,
often a level-3 shared between cores, and then the large, slow main memory. Reading from main memory is commonly around
a hundred times slower than reading from level 1. When the processor fetches a value, it brings in a whole **cache line**
(commonly 64 bytes) around it, betting that neighbouring values will be needed soon, and it watches for regular access
patterns so it can fetch ahead.

Going through memory in order wins both bets: each fetched line serves several accesses, and the pattern is predictable.
Jumping around at random loses both: almost every access is a **cache miss** that waits on main memory. In experiment 3,
the list holds references to a million float objects scattered through tens of megabytes, far more than the caches hold,
so the shuffled order misses nearly every time.

The lessons for algorithm design:

- Asymptotic analysis comes first: no cache trick saves a quadratic algorithm on a big input.
- Among algorithms with the same growth rate, the one that touches memory in order often wins by a large factor. This is
  why arrays usually beat linked lists in practice (Chapter 4), and why B-trees beat binary trees on disk (Chapter 8).
- When memory behaviour dominates, use a model that counts it: the external-memory and cache-oblivious models of Chapter 24
  count blocks moved between levels, not instructions.

### Why the RAM model is still the right start

After all these caveats, why not just measure? Because measurements answer "how fast is this program on these inputs on
this machine", and analysis answers "how will it behave on inputs a thousand times larger, on any machine". You need both:
analysis to choose the algorithm and to know it will scale, measurement to choose among equally good algorithms and to
find the slow line in a real program. Knuth's often quoted remark, from his 1974 paper "Structured Programming with go to
Statements", that premature optimization is the root of all evil, is about the second kind of decision: measure before you
tune constants. It was never advice to ignore the growth rate.

## Check yourself

??? question "1. Prove that 5n + 20 = Θ(n), giving explicit constants."

    Upper: for $n\ge1$, $20\le20n$, so $5n+20\le25n$: $c_2=25$, $n_0=1$. Or for $n\ge20$, $20\le n$, so
    $5n+20\le6n$: $c_2=6$, $n_0=20$. Lower: $5n+20\ge5n$ for all $n$: $c_1=5$. So $5n\le5n+20\le25n$ for all
    $n\ge1$.

??? question "2. Is 2^(n+1) = O(2^n)? Is 2^(2n) = O(2^n)?"

    $2^{n+1}=2\cdot2^n$, so yes, with $c=2$. But $2^{2n}=4^n$, and $4^n/2^n=2^n$ is unbounded, so no constant $c$ can
    satisfy $4^n\le c\cdot2^n$ for all large $n$: no. A constant added in the exponent is a constant factor; a constant
    *multiplied* in the exponent changes the rate.

??? question "3. Put these in increasing order of growth: n/lg n, (lg n)^2, n^1.5, sqrt(n), 2^n, n lg n, n!, n."

    $(\lg n)^2$, $\sqrt n$, $n/\lg n$, $n$, $n\lg n$, $n^{1.5}$, $2^n$, $n!$. Reasons: any power of $\lg n$ is $o(n^\varepsilon)$
    (2.8), so $(\lg n)^2=o(\sqrt n)$; $\sqrt n=o(n/\lg n)$ because their ratio $\sqrt n/\lg n\to\infty$; dividing or
    multiplying $n$ by $\lg n$ gives the next two; $n\lg n=o(n^{1.5})$ because $\lg n=o(n^{0.5})$; then polynomial before
    exponential before factorial.

??? question "4. How many times does the inner line run? for i in range(n): j = 1; while j < i: j *= 2; (count one per doubling)."

    For a given $i\ge2$, $j$ runs $1,2,4,\dots$ while $j<i$, so the body runs $\lceil\lg i\rceil$ times ($0$ times for
    $i=0,1$). The total is $\sum_{i=2}^{n-1}\lceil\lg i\rceil$, which is at most $n\lg n$ and at least the last half of the
    terms, each at least $\lg(n/2)$, so it is $\Theta(n\log n)$. For $n=16$ the exact count is 45 (and $n\lg n=64$); for
    $n=1024$ it is 9207 (and $n\lg n=10240$), both checked by running it.

??? question "5. Write the code: count how many times the innermost line of three nested loops over i < j < k runs, and find the formula."

    ```python
    def triples(n):
        c = 0
        for i in range(n):
            for j in range(i + 1, n):
                for k in range(j + 1, n):
                    c += 1
        return c

    print(triples(10))   # 120
    ```

    Each run corresponds to one set $\{i,j,k\}$ of three different indices, listed in increasing order, so the count is
    the number of 3-element subsets, $\binom{n}{3}=\frac{n(n-1)(n-2)}{6}=\Theta(n^3)$. For $n=10$: $\frac{10\cdot9\cdot8}{6}=120$.

??? question "6. Show that 1 + 2 + 4 + ... + 2^k = 2^(k+1) − 1, and explain what it says about a doubling process."

    It is the geometric sum with $r=2$, $m=k$: $\frac{2^{k+1}-1}{2-1}=2^{k+1}-1$. Directly: call it $S$; then
    $2S-S=2^{k+1}-1$. It says that all the steps of a doubling process together cost less than twice the last step, so
    the total is $\Theta$ of the last step.

??? question "7. In linear search over n distinct items, x is present with probability p (at a uniformly random position) and absent otherwise. What is the average number of comparisons?"

    Present: $(n+1)/2$ on average; absent: $n$. So the average is $p\cdot\frac{n+1}{2}+(1-p)\,n$. For $p=1$ it is
    $\frac{n+1}{2}$, for $p=\frac12$ it is $\frac{3n+1}{4}$, for $p=0$ it is $n$. Every choice gives $\Theta(n)$, but the
    constant depends on the assumption.

??? question "8. Write the code: reverse a list in place, and state its time and auxiliary space."

    ```python
    def reverse_in_place(a):
        i, j = 0, len(a) - 1
        while i < j:
            a[i], a[j] = a[j], a[i]
            i, j = i + 1, j - 1
        return a

    print(reverse_in_place([1, 2, 3, 4, 5]))   # [5, 4, 3, 2, 1]
    ```

    Each pass swaps two elements and moves $i$ and $j$ one step closer, so there are $\lfloor n/2\rfloor$ passes:
    $\Theta(n)$ time. It uses only $i$, $j$ and the temporary values of a swap: $\Theta(1)$ auxiliary space, so it is
    in place. Invariant: the first $i$ and last $i$ positions already hold their final values.

??? question "9. Prove that n^100 = o(1.01^n)."

    The ratio of consecutive terms of $u_n=n^{100}/1.01^n$ is $\frac{(1+1/n)^{100}}{1.01}$. As $n\to\infty$ the top tends
    to 1, so for large $n$ the ratio is below some $q<1$ (for example, once $(1+1/n)^{100}<1.005$, the ratio is below
    $1.005/1.01<1$). From then on $u_n$ shrinks at least geometrically, so it tends to 0. How late is "eventually"? The
    terms keep growing until about $n=10{,}000$, and $n^{100}$ first drops below $1.01^n$ only at $n=117{,}309$ (found by
    comparing $100\ln n$ with $n\ln1.01$ in Python).

??? question "10. A doubling experiment gives times 0.50 s, 2.1 s and 8.3 s for n = 10^4, 2·10^4, 4·10^4. What growth rate does this suggest, and how long would n = 10^6 take?"

    The ratios are about 4.2 and 4.0, suggesting $\Theta(n^2)$. Going from $4\cdot10^4$ to $10^6$ multiplies $n$ by 25, so the
    time by about $25^2=625$: about $8.3\times625\approx5200$ seconds, roughly an hour and a half. (A sign to find a better
    algorithm before running it.)

??? question "11. Prove that any algorithm that decides whether an unsorted list of n numbers contains a 0, using only questions of the form 'is a[i] = 0?', must ask n questions in the worst case."

    Adversary: answer "no" to every question. If the algorithm stops after fewer than $n$ questions, some position $j$ was
    never asked. If it answers "no 0", the adversary reveals an input with $a_j=0$; if it answers "there is a 0", the
    adversary reveals an input with no 0 at all. Both inputs agree with every answer given, so the algorithm is wrong on one
    of them. Hence it must ask all $n$.

??? question "12. Why is it misleading to call 'try every divisor d from 2 to N−1' a linear-time test for whether N is prime?"

    The input is the number $N$, written with $b\approx\lg N$ bits. The algorithm takes about $N=2^b$ divisions: linear in
    the *value*, but exponential in the *size* of the input. For a 600-bit number that is about $2^{600}$ divisions, hopeless.
    Fast primality tests (Chapter 19) take a number of steps polynomial in $b$.

## What you learned

- We measure an algorithm by counting operations as a function $T(n)$ of the input size, because the machine changes
  only constant factors; input size for a number means its number of digits.
- Worst case is a guarantee; average case needs an assumed distribution of inputs; best case says little.
- $O$, $\Omega$ and $\Theta$ are defined by constants $c$ and $n_0$: "at most", "at least" and "exactly" a constant times
  $g(n)$ from some point on.
- The growth ladder $1,\log n,n,n\log n,n^2,2^n,n!$: each rung eventually dwarfs the one before, and polynomial versus
  exponential is the line between practical and hopeless.
- Sums, products, polynomials and logarithms of any base follow simple rules; the arithmetic, geometric and harmonic sums
  analyse almost every loop.
- Little-o means "negligible compared to"; lower bounds hold for every algorithm in a stated model, proved by adversaries
  or decision trees.
- Real timings need `timeit`, many runs, the minimum of repeats and several sizes; constant factors and cache behaviour
  can still change running time tenfold.

**Next:** [Chapter 3](03-Recursion-and-Induction.md), functions that call themselves, proofs by induction, and the
recurrences and master theorem that measure recursive algorithms.

## Further reading

- T. H. Cormen, C. E. Leiserson, R. L. Rivest and C. Stein, *Introduction to Algorithms*, 4th ed., 2022. Chapter 3
  (characterizing running times) and Appendix A (summations).
- D. E. Knuth, "Big Omicron and Big Omega and Big Theta", *SIGACT News*, 1976.
- D. E. Knuth, "Structured Programming with go to Statements", *Computing Surveys*, 1974.
- R. L. Graham, D. E. Knuth and O. Patashnik, *Concrete Mathematics*, 2nd ed., 1994: sums, harmonic numbers and
  asymptotics in depth.
- R. Sedgewick and K. Wayne, *Algorithms*, 4th ed., 2011. Section 1.4 (analysis of algorithms, doubling experiments).
- J. Kleinberg and É. Tardos, *Algorithm Design*, 2005. Chapter 2 (basics of algorithm analysis).
- U. Drepper, "What Every Programmer Should Know About Memory", 2007: caches explained in detail.
- On this site: [Big-O reference page](../../foundations/big-o.md), [binary search](../../searching/binary-search.md),
  [Chapter 1](01-What-Is-an-Algorithm.md).
