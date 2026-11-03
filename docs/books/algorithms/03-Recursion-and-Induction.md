# 3. Recursion and induction

*Many problems contain smaller copies of themselves. To sort a list, you can sort its two halves and merge them; to move
a tower of discs, you can move a smaller tower out of the way. A function that solves a problem by calling itself on
smaller copies is **recursive**, and the proof technique that matches it exactly is **mathematical induction**. In this
chapter you will write recursive functions and watch the computer run them on its call stack, prove them correct by
induction, describe their cost with recurrence equations, and solve those equations by unrolling, recursion trees,
substitution and the master theorem. The chapter ends with the Towers of Hanoi, where we prove not only that the
recursive solution works, but that nothing can do better.*

!!! abstract "In this chapter"
    **You will learn:**

    - how a recursive function works: base case, recursive case, and the call stack that runs it
    - ordinary and strong induction, and how to use them to prove recursive algorithms correct
    - how to write a recurrence $T(n)$ for the cost of a recursive algorithm
    - three ways to solve a recurrence: unrolling, recursion trees and substitution
    - the master theorem, with its proof for exact powers, and where Akra-Bazzi takes over
    - when to prefer a loop, what a tail call is, and why Python stops at depth 1000
    - the Towers of Hanoi: $2^n-1$ moves, and a proof that no solution is shorter

    **You need:** [Chapter 1](01-What-Is-an-Algorithm.md) (loop invariants) and [Chapter 2](02-Measuring-Cost.md)
    ($O$, $\Theta$, geometric sums). Proof by induction is taught from the start here; for more practice see the
    [math books](https://math.akadian.ca/books/).

    **Levels:** 3.1 to 3.4 are beginner; 3.5, 3.7 and 3.8 are intermediate; 3.6 is intermediate to advanced.

## 3.1 A function that calls itself

What is $5!$, "five factorial"? It is $5\times4\times3\times2\times1=120$. Here is a different way to say the same
thing: $5!=5\times4!$. And $4!=4\times3!$, and so on down to $1!=1\times0!$, where by convention $0!=1$ (the product of no
numbers is 1, as the sum of no numbers is 0). That description of factorial refers to factorial itself, on a smaller
number:

$$n!=\begin{cases}1&\text{if }n=0,\\ n\times(n-1)!&\text{if }n\ge1.\end{cases}$$

Such a definition is called **recursive**. It is not circular, because each use of "factorial" on the right is for a
*smaller* number, and the smallest case is answered directly. Python lets us write it exactly as stated:

```python
def factorial(n):
    if n == 0:
        return 1                    # base case
    return n * factorial(n - 1)     # recursive case
```

Every recursive function has the same two parts.

1. A **base case**: an input small enough to answer without recursion ($n=0$).
2. A **recursive case**: the answer is built from the answers to one or more **smaller** inputs ($n-1$).

"Smaller" is essential. If the recursive call were `factorial(n)` or `factorial(n + 1)`, the function would call itself
forever (in practice, until the computer runs out of the memory it sets aside for calls, as 3.7 shows).

Two more examples in the same style. The sum of a list is its first element plus the sum of the rest; the sum of the
empty list is 0.

```python
def total(a, i=0):          # sum of a[i:]
    if i == len(a):
        return 0
    return a[i] + total(a, i + 1)
```

And a power $x^n$: since $x^n=x\cdot x^{n-1}$, we could recurse on $n-1$, making $n$ calls. Better: $x^n=(x^{n/2})^2$ when
$n$ is even, and $x\cdot(x^{\lfloor n/2\rfloor})^2$ when $n$ is odd. That recurses on $\lfloor n/2\rfloor$, so the problem
halves at each call. This is **fast exponentiation** by repeated squaring (see the [fast power reference
page](../../number-theory/fast-power.md)).

```python
def power(x, n):
    if n == 0:
        return 1
    half = power(x, n // 2)
    if n % 2 == 0:
        return half * half
    return half * half * x
```

Trace `power(3, 13)`: it calls `power(3, 6)`, which calls `power(3, 3)`, then `power(3, 1)`, then `power(3, 0)`. Then the
answers come back up:

| call | $n$ | half (answer from below) | even? | returns |
|---|---|---|---|---|
| 5th | 0 | | | 1 |
| 4th | 1 | 1 | no | $1\cdot1\cdot3=3$ |
| 3rd | 3 | 3 | no | $3\cdot3\cdot3=27$ |
| 2nd | 6 | 27 | yes | $27\cdot27=729$ |
| 1st | 13 | 729 | no | $729\cdot729\cdot3=1{,}594{,}323$ |

Five calls instead of thirteen multiplications. For $n=10^{18}$ it is 61 calls instead of a billion billion.

### The call stack

How does the computer keep track of all these unfinished calls? Each time a function is called, the computer sets aside a
small block of memory, a **stack frame**, holding that call's own variables (its `n`, its `half`) and the place in the
caller's code to return to. The frames are kept on a **stack**: a pile where the newest item is on top and is the first to
be removed (Chapter 4 builds stacks from scratch). A call **pushes** a new frame on top; a `return` **pops** it off and
hands the value to the frame below, which carries on where it left off.

<figure class="mars-fig" markdown="0">
<svg viewBox="0 0 640 290" role="img" aria-label="The call stack of factorial of 3 at its deepest point. Four frames are stacked: factorial 3 at the bottom, then factorial 2, factorial 1, and factorial 0 on top in orange. Each lower frame waits for the one above. On the right, return values flow down: factorial 0 returns 1, factorial 1 returns 1 times 1 equals 1, factorial 2 returns 2 times 1 equals 2, factorial 3 returns 3 times 2 equals 6.">
  <text x="180" y="40" font-size="13" text-anchor="middle" fill="currentColor">top of the stack (newest call)</text>
  <rect x="60" y="52" width="240" height="46" rx="4" fill="#eea66f" fill-opacity="0.6" stroke="currentColor" stroke-width="1.5"/>
  <text x="180" y="72" font-size="14" text-anchor="middle" fill="currentColor">factorial(0)</text>
  <text x="180" y="90" font-size="12" text-anchor="middle" fill="currentColor">n = 0: base case</text>
  <rect x="60" y="102" width="240" height="46" rx="4" fill="#9cc9ea" fill-opacity="0.4" stroke="currentColor" stroke-width="1.5"/>
  <text x="180" y="122" font-size="14" text-anchor="middle" fill="currentColor">factorial(1)</text>
  <text x="180" y="140" font-size="12" text-anchor="middle" fill="currentColor">n = 1: waiting for factorial(0)</text>
  <rect x="60" y="152" width="240" height="46" rx="4" fill="#9cc9ea" fill-opacity="0.4" stroke="currentColor" stroke-width="1.5"/>
  <text x="180" y="172" font-size="14" text-anchor="middle" fill="currentColor">factorial(2)</text>
  <text x="180" y="190" font-size="12" text-anchor="middle" fill="currentColor">n = 2: waiting for factorial(1)</text>
  <rect x="60" y="202" width="240" height="46" rx="4" fill="#9cc9ea" fill-opacity="0.4" stroke="currentColor" stroke-width="1.5"/>
  <text x="180" y="222" font-size="14" text-anchor="middle" fill="currentColor">factorial(3)</text>
  <text x="180" y="240" font-size="12" text-anchor="middle" fill="currentColor">n = 3: waiting for factorial(2)</text>
  <text x="180" y="272" font-size="13" text-anchor="middle" fill="currentColor">bottom (the first call)</text>
  <line x1="320" y1="75" x2="360" y2="75" stroke="#7ccf9a" stroke-width="2.5"/>
  <text x="370" y="80" font-size="13" fill="currentColor">returns 1</text>
  <line x1="320" y1="125" x2="360" y2="125" stroke="#7ccf9a" stroke-width="2.5"/>
  <text x="370" y="130" font-size="13" fill="currentColor">returns 1 × 1 = 1</text>
  <line x1="320" y1="175" x2="360" y2="175" stroke="#7ccf9a" stroke-width="2.5"/>
  <text x="370" y="180" font-size="13" fill="currentColor">returns 2 × 1 = 2</text>
  <line x1="320" y1="225" x2="360" y2="225" stroke="#7ccf9a" stroke-width="2.5"/>
  <text x="370" y="230" font-size="13" fill="currentColor">returns 3 × 2 = 6</text>
  <line x1="590" y1="70" x2="590" y2="222" stroke="currentColor" stroke-width="1.5"/>
  <polygon points="590,232 585,220 595,220" fill="currentColor"/>
  <text x="600" y="150" font-size="12" fill="currentColor" transform="rotate(90 600 150)" text-anchor="middle">answers flow down</text>
</svg>
<figcaption>The call stack of factorial(3) at its deepest moment. Each frame waits for the frame above it; when the base
case returns, the frames pop off one by one, each finishing its multiplication.</figcaption>
</figure>

The chapter's first program makes the stack visible by indenting each call one step deeper than its caller:

```python
--8<-- "books/algorithms/ch03_recursion.py"
```

Output:

```
The call stack of factorial(3):
call factorial(3)
    call factorial(2)
        call factorial(1)
            call factorial(0)
            factorial(0) returns 1
        factorial(1) returns 1
    factorial(2) returns 2
factorial(3) returns 6

total([4, 8, 15, 16, 23, 42]) = 108
power(3, 13) = 1594323   check: 1594323
  power(x, 13) makes 5 calls; n.bit_length() + 1 = 5
  power(x, 1000) makes 11 calls; n.bit_length() + 1 = 11
  power(x, 1000000) makes 21 calls; n.bit_length() + 1 = 21
  power(x, 1000000000000000000) makes 61 calls; n.bit_length() + 1 = 61

Python's recursion limit: 1000
factorial fails at about depth 1001
factorial_loop(20000) has 256909 bits: a loop has no such limit
```

Notice the shape: calls go down and to the right, returns come back up and to the left, and each call returns only after
every call it made has returned. The **depth** of the recursion, the largest number of frames on the stack at once, is
the extra memory it uses: $n+1$ frames for `factorial(n)`, so $\Theta(n)$ space, but only about $\lg n$ frames for
`power`. The last lines of the output, about the recursion limit, are explained in 3.7.

## 3.2 Mathematical induction

How can we be sure `factorial` is right for *every* $n$, not just the ones we ran? We need to prove infinitely many
statements, one for each $n$, and the tool for that is **mathematical induction**.

**The principle of induction.** Let $P(n)$ be a statement about a whole number $n$. Suppose

1. **(base case)** $P(n_0)$ is true, and
2. **(inductive step)** for every $k\ge n_0$, if $P(k)$ is true then $P(k+1)$ is true.

Then $P(n)$ is true for every $n\ge n_0$.

*Why it is valid.* Suppose some $P(n)$ with $n\ge n_0$ were false. Among all the false ones, take the smallest, $m$. It is
not $n_0$, since the base case holds, so $m>n_0$, and $P(m-1)$ is true because $m$ was the smallest false one. But then
the inductive step, applied to $k=m-1$, says $P(m)$ is true. Contradiction. (This argument uses the fact that every
non-empty set of whole numbers has a smallest element, which is really an equivalent form of the same principle.)

The assumption "$P(k)$ is true" inside the inductive step is called the **induction hypothesis**. It is not assuming
what we want to prove: we prove the *implication* "if $P(k)$ then $P(k+1)$", for every $k$, and the base case gets the
chain started. Chapter 1's loop invariants were exactly this: initialization is the base case, maintenance is the
inductive step.

**Example 1.** For every $n\ge1$, $1+2+\dots+n=\dfrac{n(n+1)}{2}$.

*Proof.* Let $P(n)$ be the statement. *Base case:* for $n=1$ the left side is 1 and the right side is $\frac{1\cdot2}{2}=1$.
*Inductive step:* assume $P(k)$, that is $1+\dots+k=\frac{k(k+1)}{2}$. Then

$$1+\dots+k+(k+1)=\frac{k(k+1)}{2}+(k+1)=\frac{k(k+1)+2(k+1)}{2}=\frac{(k+1)(k+2)}{2},$$

which is $P(k+1)$. $\square$

(Chapter 2 proved the same formula by pairing terms. Induction is the general method; it works even when no clever trick
is in sight, but it needs you to know the answer in advance. Chapter 2's methods *find* answers; induction *checks* them.)

**Example 2.** For every $n\ge0$, $2^n\ge n+1$.

*Proof.* Base case $n=0$: $2^0=1\ge1$. Inductive step: assume $2^k\ge k+1$. Then $2^{k+1}=2\cdot2^k\ge2(k+1)=2k+2\ge k+2$.
$\square$

**Example 3 (a geometric sum).** For every $n\ge0$, $1+2+4+\dots+2^n=2^{n+1}-1$.

*Proof.* Base: $1=2^1-1$. Step: if $1+\dots+2^k=2^{k+1}-1$, then adding $2^{k+1}$ gives $2\cdot2^{k+1}-1=2^{k+2}-1$. $\square$

### Strong induction

Sometimes $P(k+1)$ does not follow from $P(k)$ alone but from some earlier case, such as $P(\lfloor(k+1)/2\rfloor)$. Then we
use a stronger hypothesis.

**The principle of strong induction.** Suppose $P(n_0)$ is true, and for every $k\ge n_0$, if $P(n_0),P(n_0+1),\dots,P(k)$
are *all* true then $P(k+1)$ is true. Then $P(n)$ is true for every $n\ge n_0$.

It is valid for the same reason: the smallest false case would have all earlier cases true, and the step would make it
true. Strong induction is no stronger as logic (you can always turn it into ordinary induction on the statement "$P$
holds for everything up to $k$"), but it is much more convenient, and it is the natural partner of algorithms that recurse
on inputs much smaller than $n-1$.

**Example 4.** Every whole number $n\ge2$ is a product of primes (a prime counts as a product of one prime).

*Proof by strong induction.* Base: 2 is prime. Step: let $k+1\ge3$ and assume every number from 2 to $k$ is a product of
primes. If $k+1$ is prime, done. Otherwise $k+1=ab$ with $2\le a,b\le k$. By the hypothesis, $a$ and $b$ are products of
primes, so $k+1=ab$ is too. $\square$

Ordinary induction would not work here: knowing that $k$ is a product of primes says nothing useful about $k+1$. The
divisors $a$ and $b$ can be anywhere below $k$, and strong induction lets us use whichever we need.

**Example 5 (a Fibonacci bound).** The Fibonacci numbers are $F_0=0$, $F_1=1$ and $F_n=F_{n-1}+F_{n-2}$ for $n\ge2$. Then
$F_n<2^n$ for every $n\ge0$.

*Proof.* Two base cases: $F_0=0<1$ and $F_1=1<2$. Step for $k+1\ge2$: assume the claim for every number up to $k$. Then
$F_{k+1}=F_k+F_{k-1}<2^k+2^{k-1}<2^k+2^k=2^{k+1}$. $\square$

The step uses *two* earlier cases, so we needed two base cases: the step from $k+1=2$ uses $F_1$ and $F_0$, which no
earlier step could provide. Forgetting a base case is the most common mistake in induction proofs, and Exercise 4 shows how
it can "prove" something false.

## 3.3 Proving recursive algorithms correct

A recursive algorithm and an induction proof have the same shape: the base case of the algorithm matches the base case of
the proof, and the recursive call matches the induction hypothesis. When you write `factorial(n - 1)` inside
`factorial(n)`, you are *trusting* that the call on the smaller input works, and induction is what entitles you to that
trust. This is sometimes called the "leap of faith" of recursion, but there is nothing faithful about it: it is a proof.

**Claim.** For every $n\ge0$, `factorial(n)` returns $n!$.

*Proof by induction on $n$.* Base: `factorial(0)` returns 1, which is $0!$. Step: assume `factorial(k)` returns $k!$.
Then `factorial(k + 1)` returns `(k + 1) * factorial(k)`, which by the hypothesis is $(k+1)\cdot k!=(k+1)!$. And the
recursion stops, because each call is on a smaller non-negative number and the base case catches 0. $\square$

**Claim.** For every $n\ge0$ and every $x$, `power(x, n)` returns $x^n$.

*Proof by strong induction on $n$.* Base: `power(x, 0)` returns $1=x^0$. Step: let $n\ge1$ and assume `power(x, m)` returns
$x^m$ for every $m<n$. The call computes `half = power(x, n // 2)`; since $\lfloor n/2\rfloor<n$, the hypothesis gives
half $=x^{\lfloor n/2\rfloor}$.

- If $n$ is even, $n=2\lfloor n/2\rfloor$, so half $\cdot$ half $=x^{2\lfloor n/2\rfloor}=x^n$.
- If $n$ is odd, $n=2\lfloor n/2\rfloor+1$, so half $\cdot$ half $\cdot x=x^{2\lfloor n/2\rfloor+1}=x^n$. $\square$

Ordinary induction from $n-1$ to $n$ would not help: `power(x, n)` never calls `power(x, n - 1)`. Strong induction fits
because the algorithm's recursive call is on $\lfloor n/2\rfloor$.

### A recursive maximum

Recursion often makes correctness proofs *easier* than loops do, because the induction is right there in the code.
Here is FIND-MAX from Chapter 1, done by splitting the list in half:

```python
def rmax(a, lo, hi):            # largest of a[lo:hi], with hi - lo >= 1
    if hi - lo == 1:
        return a[lo]
    mid = (lo + hi) // 2
    return max(rmax(a, lo, mid), rmax(a, mid, hi))
```

*Claim.* For every range of length $m=hi-lo\ge1$, `rmax` returns the largest of $a_{lo},\dots,a_{hi-1}$.

*Proof by strong induction on $m$.* Base $m=1$: the one element is the largest. Step $m\ge2$: then
$lo<mid<hi$ (because $mid=\lfloor(lo+hi)/2\rfloor$ and $hi-lo\ge2$), so both halves are non-empty and shorter than $m$. By
the hypothesis the two calls return the largest of each half, and the largest of the whole range is the larger of those
two. $\square$

The detail "$lo<mid<hi$" is not pedantry. If a half could be empty, the recursion would call `rmax` on a range of length
0 (violating its precondition), or on the same range again (recursing forever). Checking that every recursive call is
*strictly smaller* and still satisfies the precondition is the termination half of the proof. Binary search, merge sort
and quicksort all need exactly this check, and Chapter 5 and Chapter 7 return to it.

## 3.4 Recurrences: writing T(n)

How long does a recursive algorithm take? For a loop we added up the passes. For recursion, the cost of a call is the
work it does itself plus the cost of the calls it makes, and *those* costs are values of the same function on smaller
inputs. So the cost satisfies an equation that refers to itself: a **recurrence**.

**factorial.** Let $T(n)$ be the number of steps for `factorial(n)`. The call does a constant amount of work $c$ (the
test, the multiplication, the return) plus one call on $n-1$:

$$T(0)=c_0,\qquad T(n)=T(n-1)+c\quad(n\ge1).$$

**power.** One call on $\lfloor n/2\rfloor$ plus constant work:

$$T(0)=c_0,\qquad T(n)=T(\lfloor n/2\rfloor)+c\quad(n\ge1).$$

**rmax.** Two calls on halves plus constant work:

$$T(1)=c_0,\qquad T(m)=T(\lfloor m/2\rfloor)+T(\lceil m/2\rceil)+c.$$

**merge sort** (Chapter 5; [reference page](../../sorting/merge-sort.md)). Sort each half recursively, then merge the two
sorted halves in linear time:

$$T(1)=c_0,\qquad T(n)=T(\lfloor n/2\rfloor)+T(\lceil n/2\rceil)+cn.$$

The recipe for writing a recurrence:

1. Let $T(n)$ be the worst-case cost on inputs of size $n$.
2. For the base case, the cost is a constant.
3. For the recursive case, add the cost of each recursive call (as $T$ of its size) and the cost of the work done outside
   the calls (splitting the input, combining the answers).

Three simplifications are standard and harmless, and we use them from now on.

- **Constants.** We write $T(n)=2T(n/2)+n$ instead of $\dots+cn$: a constant factor in the non-recursive work changes the
  answer only by a constant factor.
- **Base cases.** We often leave out the base case and assume $T(n)$ is a constant for small $n$. Changing the constant
  changes the answer by at most a constant factor for the recurrences in this book.
- **Floors and ceilings.** We often drop them and solve for $n$ a power of 2 (or of $b$). The answer is almost always the
  same $\Theta$; the chapter's program checks one case, the merge sort recurrence with exact floors and ceilings, and
  finds $T(n)/(n\lg n)$ within 0.1% of 1 at $n=1000$ and $n=10^6$. CLRS (Chapter 4 of the 4th edition) discusses when the
  simplification is safe.

## 3.5 Solving recurrences

*Level: intermediate.* A recurrence describes $T(n)$, but not in a form we can read. "Solving" it means finding a
**closed form**, an expression without $T$ on the right, or at least its $\Theta$. Three methods, in order of how much
you need to guess.

### Method 1: unrolling

Substitute the recurrence into itself until a pattern appears, then sum.

**factorial.** $T(n)=T(n-1)+c=T(n-2)+2c=T(n-3)+3c=\dots=T(0)+nc$. So $T(n)=c_0+cn=\Theta(n)$.

**power.** With $n=2^k$: $T(n)=T(n/2)+c=T(n/4)+2c=\dots=T(1)+kc=T(0)+(k+1)c$. Since $k=\lg n$, $T(n)=\Theta(\log n)$. The
program counts the calls exactly: `power(x, n)` makes $\lfloor\lg n\rfloor+2$ calls for $n\ge1$ (which Python writes as
`n.bit_length() + 1`), for instance 61 calls for $n=10^{18}$.

**A sum recurrence.** $T(n)=T(n-1)+n$ with $T(0)=0$ unrolls to $n+(n-1)+\dots+1=\frac{n(n+1)}{2}=\Theta(n^2)$. This is the
cost of an algorithm that does linear work and then recurses on one fewer item, which is how insertion sort and selection
sort behave.

### Method 2: recursion trees

For algorithms that make several calls, draw the calls as a tree: the original call at the top (the **root**), the calls
it makes below it, their calls below them, down to the base cases (the **leaves**). Write in each node the work done in
that call *outside* its own recursive calls. The total cost is the sum over all nodes, and it is usually easiest to add
**level by level**.

<figure class="mars-fig" markdown="0">
<svg viewBox="0 0 720 300" role="img" aria-label="Recursion tree for T of n equals 2 T of n over 2 plus n. The root does n work. Two children each do n over 2. Four grandchildren each do n over 4. The tree continues down to n leaves of cost 1. On the right, each level totals n, and there are lg n plus 1 levels, for a total of n lg n plus n.">
  <rect x="270" y="20" width="70" height="30" rx="5" fill="#eea66f" fill-opacity="0.5" stroke="currentColor" stroke-width="1.2"/>
  <text x="305" y="40" font-size="14" text-anchor="middle" fill="currentColor">n</text>
  <line x1="290" y1="50" x2="175" y2="88" stroke="currentColor" stroke-width="1.2"/>
  <line x1="320" y1="50" x2="435" y2="88" stroke="currentColor" stroke-width="1.2"/>
  <rect x="140" y="88" width="70" height="30" rx="5" fill="#9cc9ea" fill-opacity="0.45" stroke="currentColor" stroke-width="1.2"/>
  <text x="175" y="108" font-size="14" text-anchor="middle" fill="currentColor">n/2</text>
  <rect x="400" y="88" width="70" height="30" rx="5" fill="#9cc9ea" fill-opacity="0.45" stroke="currentColor" stroke-width="1.2"/>
  <text x="435" y="108" font-size="14" text-anchor="middle" fill="currentColor">n/2</text>
  <line x1="160" y1="118" x2="105" y2="156" stroke="currentColor" stroke-width="1.2"/>
  <line x1="190" y1="118" x2="245" y2="156" stroke="currentColor" stroke-width="1.2"/>
  <line x1="420" y1="118" x2="365" y2="156" stroke="currentColor" stroke-width="1.2"/>
  <line x1="450" y1="118" x2="505" y2="156" stroke="currentColor" stroke-width="1.2"/>
  <rect x="75" y="156" width="60" height="30" rx="5" fill="#7ccf9a" fill-opacity="0.45" stroke="currentColor" stroke-width="1.2"/>
  <text x="105" y="176" font-size="14" text-anchor="middle" fill="currentColor">n/4</text>
  <rect x="215" y="156" width="60" height="30" rx="5" fill="#7ccf9a" fill-opacity="0.45" stroke="currentColor" stroke-width="1.2"/>
  <text x="245" y="176" font-size="14" text-anchor="middle" fill="currentColor">n/4</text>
  <rect x="335" y="156" width="60" height="30" rx="5" fill="#7ccf9a" fill-opacity="0.45" stroke="currentColor" stroke-width="1.2"/>
  <text x="365" y="176" font-size="14" text-anchor="middle" fill="currentColor">n/4</text>
  <rect x="475" y="156" width="60" height="30" rx="5" fill="#7ccf9a" fill-opacity="0.45" stroke="currentColor" stroke-width="1.2"/>
  <text x="505" y="176" font-size="14" text-anchor="middle" fill="currentColor">n/4</text>
  <text x="305" y="220" font-size="16" text-anchor="middle" fill="currentColor">⋮</text>
  <g fill="none" stroke="currentColor" stroke-width="1.2">
    <rect x="60" y="240" width="28" height="24" rx="3"/><rect x="96" y="240" width="28" height="24" rx="3"/>
    <rect x="132" y="240" width="28" height="24" rx="3"/><rect x="450" y="240" width="28" height="24" rx="3"/>
    <rect x="486" y="240" width="28" height="24" rx="3"/><rect x="522" y="240" width="28" height="24" rx="3"/>
  </g>
  <g font-size="12" text-anchor="middle" fill="currentColor">
    <text x="74" y="257">1</text><text x="110" y="257">1</text><text x="146" y="257">1</text>
    <text x="464" y="257">1</text><text x="500" y="257">1</text><text x="536" y="257">1</text>
  </g>
  <text x="305" y="257" font-size="13" text-anchor="middle" fill="currentColor">. . .  n leaves  . . .</text>
  <g font-size="13" fill="currentColor">
    <text x="565" y="40">level 0: n</text>
    <text x="565" y="108">level 1: 2 · n/2 = n</text>
    <text x="565" y="176">level 2: 4 · n/4 = n</text>
    <text x="565" y="257">leaves: n · 1 = n</text>
  </g>
  <text x="340" y="290" font-size="13" text-anchor="middle" fill="currentColor">lg n + 1 levels, n each: T(n) = n lg n + n</text>
</svg>
<figcaption>The recursion tree of T(n) = 2T(n/2) + n, for n a power of 2. Level j has 2^j nodes, each doing n/2^j
work, so every level costs n. There are lg n levels above the leaves, plus the leaf level.</figcaption>
</figure>

**Merge sort: $T(n)=2T(n/2)+n$, $T(1)=1$, with $n=2^k$.** Level $j$ (the root is level 0) has $2^j$ calls, each on a
problem of size $n/2^j$, each doing $n/2^j$ work. So each level costs $2^j\cdot n/2^j=n$. The sizes reach 1 at level $k=\lg
n$, where there are $n$ leaves costing 1 each. Total: $k$ levels of $n$, plus $n$ for the leaves:

$$T(n)=n\lg n+n=\Theta(n\log n).$$

The program confirms it exactly: for $n=2^{20}$, $T(n)=22{,}020{,}096=2^{20}\cdot20+2^{20}$.

**$T(n)=2T(n/2)+1$** (the cost of `rmax`). Level $j$ has $2^j$ nodes, each costing 1, so the levels cost $1,2,4,\dots,n/2$
and the leaves $n$. That is a geometric sum, dominated by its largest term: $T(n)=1+2+\dots+n=2n-1=\Theta(n)$. The leaves
dominate.

**$T(n)=2T(n/2)+n^2$.** Level $j$ costs $2^j(n/2^j)^2=n^2/2^j$: the levels cost $n^2,n^2/2,n^2/4,\dots$, a decreasing
geometric sum, at most $2n^2$. So $T(n)=\Theta(n^2)$. The root dominates.

These three examples show the only three things that can happen when the problem shrinks by a constant factor: the level
costs are **equal** (multiply one level by the number of levels), **increasing** geometrically (the leaves dominate), or
**decreasing** geometrically (the root dominates). The master theorem in 3.6 is exactly this observation, made precise.

**An unbalanced tree: $T(n)=T(n/3)+T(2n/3)+n$.** The root costs $n$; its children cost $n/3$ and $2n/3$, together $n$;
the next level again totals $n$ (the sizes $n/9$, $2n/9$, $2n/9$, $4n/9$ add up to $n$), and so on. But the branches end at
different depths: the leftmost path (always $n/3$) ends after $\log_3 n$ levels, the rightmost (always $2n/3$) after
$\log_{3/2}n$ levels. Every full level costs exactly $n$ and the deeper levels cost at most $n$, so
$T(n)\le n(\log_{3/2}n+1)=O(n\log n)$, and the first $\log_3 n$ levels are full, so $T(n)\ge n\log_3 n=\Omega(n\log n)$.
Hence $\Theta(n\log n)$. A quicksort that always splits a third against two thirds is still $\Theta(n\log n)$.

### Method 3: substitution (guess and prove)

Recursion trees are good for finding the answer, but adding up "level by level" with dots in the middle is not quite a
proof. The **substitution method** is: guess the form of the answer, then prove it by induction, finding the constants
as you go.

**Example.** Prove that $T(n)=2T(n/2)+n$, $T(1)=1$, satisfies $T(n)\le2n\lg n$ for all powers of two $n\ge2$.

*Proof by induction.* Base $n=2$: $T(2)=2T(1)+2=4$, and $2\cdot2\cdot\lg2=4$. Step: assume $T(n/2)\le2\cdot\frac n2\lg\frac n2$.
Then

$$T(n)=2T(n/2)+n\le2n\lg\frac n2+n=2n(\lg n-1)+n=2n\lg n-n\le2n\lg n.$$

$\square$

We could not start at $n=1$, because $2\cdot1\cdot\lg1=0<T(1)$. That is fine: Big-O only needs the bound from some $n_0$
on. Choosing the base case and the constant together is the usual small puzzle of this method.

**A trap.** Here is a wrong "proof" that $T(n)=2T(n/2)+n$ is $O(n)$. "Assume $T(n/2)\le c\cdot n/2$. Then
$T(n)\le2c\cdot n/2+n=cn+n=O(n)$." The error: the induction hypothesis was the *exact* inequality $T(m)\le cm$, so the
step must prove exactly $T(n)\le cn$, with the *same* $c$. It proved $T(n)\le(c+1)n$, and the constant grows by 1 at every
level, which over $\lg n$ levels is $c+\lg n$: not a constant at all. In substitution proofs, never write $O$ inside the
induction; work with explicit constants.

**Strengthening the hypothesis.** Sometimes the right guess fails for a silly reason. For $T(n)=2T(n/2)+1$, guess
$T(n)\le cn$: the step gives $T(n)\le2c\frac n2+1=cn+1$, which is not $\le cn$. The fix is counter-intuitive: prove
something *stronger*, $T(n)\le cn-1$. Now the step gives $T(n)\le2\left(c\frac n2-1\right)+1=cn-1$. It works, because the
stronger hypothesis gives more to work with in the step. (With $c=2$ and $T(1)=1$ the base case $1\le2-1$ holds too, and
in fact $T(n)=2n-1$ exactly.)

## 3.6 The master theorem

*Level: intermediate to advanced.* Most divide-and-conquer algorithms split a problem of size $n$ into $a$ subproblems of
size $n/b$ and do $f(n)$ work to split and combine. Their recurrences all have the form

$$T(n)=a\,T(n/b)+f(n),$$

with constants $a\ge1$ and $b>1$. The **master theorem** solves all the common cases at once. The key quantity is the
**critical exponent** $\log_b a$. Here is why: the recursion tree has $\log_b n$ levels, and level $j$ has $a^j$ nodes, so
the leaf level has $a^{\log_b n}$ nodes. And

$$a^{\log_b n}=n^{\log_b a},$$

because taking $\log_b$ of both sides gives $\log_b n\cdot\log_b a$ on each side. So the leaves alone cost
$\Theta(n^{\log_b a})$, and the question is how $f(n)$, the root's cost, compares with that.

### The version with polynomial f

**Theorem (master theorem, polynomial form).** Let $a\ge1$, $b>1$, $d\ge0$ be constants and let
$T(n)=aT(n/b)+\Theta(n^d)$ for $n>1$, with $T(1)=\Theta(1)$. Then

1. if $d<\log_b a$, then $T(n)=\Theta(n^{\log_b a})$ (the leaves dominate);
2. if $d=\log_b a$, then $T(n)=\Theta(n^d\log n)$ (all levels are equal);
3. if $d>\log_b a$, then $T(n)=\Theta(n^d)$ (the root dominates).

*Proof for $n$ an exact power of $b$.* Write $n=b^k$, so $k=\log_b n$, and suppose for the upper bound that the
non-recursive work is at most $cn^d$ and $T(1)\le c$ (the lower bound is the same argument with $\ge$ and another
constant). Unrolling the recurrence $k$ times, or reading off the recursion tree, gives

$$T(n)=a^kT(1)+\sum_{j=0}^{k-1}a^j\,f\!\left(\frac n{b^j}\right).$$

Level $j$ has $a^j$ nodes, each with a problem of size $n/b^j$. With $f(m)=cm^d$, level $j$ costs

$$a^j\cdot c\left(\frac{n}{b^j}\right)^d=cn^d\left(\frac{a}{b^d}\right)^j.$$

So the level costs form a geometric sequence with ratio $r=a/b^d$, and the leaves cost $a^kT(1)=\Theta(n^{\log_b a})$.
Notice that $r<1$, $r=1$ and $r>1$ correspond exactly to $d>\log_b a$, $d=\log_b a$ and $d<\log_b a$, because $a/b^d<1$
means $a<b^d$, that is $\log_b a<d$.

- **Case 3, $r<1$.** The geometric sum is at most $\frac{1}{1-r}$ times its first term (Chapter 2, 2.6), so the levels
  total at most $\frac{c}{1-r}n^d$. The leaves cost $\Theta(n^{\log_b a})$, which is $O(n^d)$ since $\log_b a<d$. And the
  root alone costs $cn^d$. So $T(n)=\Theta(n^d)$.
- **Case 2, $r=1$.** Every level costs exactly $cn^d$, and there are $k=\log_b n$ levels, so the levels total
  $cn^d\log_b n$. The leaves cost $\Theta(n^{\log_b a})=\Theta(n^d)$, which is smaller. So $T(n)=\Theta(n^d\log n)$.
- **Case 1, $r>1$.** The geometric sum is at most $\frac{r}{r-1}$ times its *last* term, $cn^dr^{k-1}$. Now
  $n^dr^k=b^{kd}\cdot\frac{a^k}{b^{kd}}=a^k=n^{\log_b a}$, so the levels total $O(n^{\log_b a})$, and the leaves cost
  $\Theta(n^{\log_b a})$ too. So $T(n)=\Theta(n^{\log_b a})$. $\square$

That is the whole proof: the master theorem is "a geometric sum is dominated by its largest term", applied to the levels
of a recursion tree.

### Examples

The chapter's second program computes several recurrences exactly for powers of 2 and compares them with closed forms
found by the methods above, then classifies more with the theorem.

```python
--8<-- "books/algorithms/ch03_recurrences.py"
```

Output:

```
T(n) = T(n/2) + 1      (binary search)
   n = 2^4   T(n) =               5   closed form =               5.0
   n = 2^10  T(n) =              11   closed form =              11.0
   n = 2^20  T(n) =              21   closed form =              21.0
T(n) = 2T(n/2) + n     (merge sort)
   n = 2^4   T(n) =              80   closed form =              80.0
   n = 2^10  T(n) =          11,264   closed form =          11,264.0
   n = 2^20  T(n) =      22,020,096   closed form =      22,020,096.0
T(n) = 2T(n/2) + 1     (tree sum)
   n = 2^4   T(n) =              31   closed form =              31.0
   n = 2^10  T(n) =           2,047   closed form =           2,047.0
   n = 2^20  T(n) =       2,097,151   closed form =       2,097,151.0
T(n) = 4T(n/2) + n
   n = 2^4   T(n) =             496   closed form =             496.0
   n = 2^10  T(n) =       2,096,128   closed form =       2,096,128.0
   n = 2^20  T(n) = 2,199,022,206,976   closed form = 2,199,022,206,976.0
T(n) = 3T(n/2) + n     (Karatsuba)
   n = 2^4   T(n) =             211   closed form =             211.0
   n = 2^10  T(n) =         175,099   closed form =         175,099.0
   n = 2^20  T(n) =  10,458,256,051   closed form =  10,458,256,051.0
T(n) = 2T(n/2) + n^2
   n = 2^4   T(n) =             496   closed form =             496.0
   n = 2^10  T(n) =       2,096,128   closed form =       2,096,128.0
   n = 2^20  T(n) = 2,199,022,206,976   closed form = 2,199,022,206,976.0

  a=1 b=2 d=0:  Theta(log n)        case 2: d = log_b a
  a=2 b=2 d=1:  Theta(n log n)      case 2: d = log_b a
  a=2 b=2 d=0:  Theta(n)            case 1: d < log_b a = 1.000
  a=4 b=2 d=1:  Theta(n^2)          case 1: d < log_b a = 2.000
  a=3 b=2 d=1:  Theta(n^1.585)      case 1: d < log_b a = 1.585
  a=2 b=2 d=2:  Theta(n^2)          case 3: d > log_b a = 1.000
  a=7 b=2 d=2:  Theta(n^2.807)      case 1: d < log_b a = 2.807
  a=9 b=3 d=2:  Theta(n^2 log n)    case 2: d = log_b a

Not an exact power: T(n) = T(floor(n/2)) + T(ceil(n/2)) + n, T(1) = 0
   n =     1000:  T(n) =      9,976   n lg n =        9,966   ratio 1.0010
   n =  1000000:  T(n) = 19,951,424   n lg n =   19,931,569   ratio 1.0010
```

Read the examples.

- **Binary search**, $T(n)=T(n/2)+1$: $a=1$, $b=2$, $d=0$, and $\log_2 1=0=d$. Case 2: $\Theta(\log n)$. Exactly
  $\lg n+1$.
- **Merge sort**, $2T(n/2)+n$: $\log_2 2=1=d$. Case 2: $\Theta(n\log n)$.
- **Tree sum**, $2T(n/2)+1$: $d=0<1$. Case 1: $\Theta(n)$.
- **$4T(n/2)+n$** (four half-size subproblems, as in naive divide-and-conquer multiplication of $n$-digit numbers):
  $\log_2 4=2>1$. Case 1: $\Theta(n^2)$; exactly $2n^2-n$.
- **Karatsuba**, $3T(n/2)+n$ (Chapter 11): three half-size multiplications instead of four. $\log_2 3\approx1.585>1$.
  Case 1: $\Theta(n^{\log_2 3})=\Theta(n^{1.585})$; exactly $3n^{\lg3}-2n$. Saving one subproblem out of four changes
  the exponent.
- **$2T(n/2)+n^2$**: $d=2>1$. Case 3: $\Theta(n^2)$. Curiously, with $T(1)=1$ it gives exactly the same numbers as
  $4T(n/2)+n$, namely $2n^2-n$: the same total, reached in opposite ways. In $4T(n/2)+n$ the level costs are
  $n,2n,4n,\dots$ and the leaves dominate; in $2T(n/2)+n^2$ they are $n^2,n^2/2,n^2/4,\dots$ and the root dominates.
- **Strassen**, $7T(n/2)+n^2$ (Chapter 11): $\log_2 7\approx2.807>2$. Case 1: $\Theta(n^{2.807})$, beating the
  $\Theta(n^3)$ of the school method for multiplying matrices.
- **$9T(n/3)+n^2$**: $\log_3 9=2=d$. Case 2: $\Theta(n^2\log n)$.

The closed forms in the program were found by solving each recurrence exactly. For example, for $3T(n/2)+n$ with $T(1)=1$,
try $T(n)=An^{\lg3}+Bn$: substituting, $An^{\lg 3}+Bn=3A(n/2)^{\lg3}+3B\frac n2+n=An^{\lg3}+\frac32Bn+n$ (since
$3/2^{\lg3}=1$), so $B=\frac32B+1$, giving $B=-2$; then $T(1)=A+B=1$ gives $A=3$.

### The general version, and its gaps

The polynomial form covers almost every recurrence in this book. The general statement allows any $f$.

**Theorem (master theorem, general form, as in CLRS, 4th ed.).** Let $a\ge1$, $b>1$, and $T(n)=aT(n/b)+f(n)$.

1. If $f(n)=O(n^{\log_b a-\varepsilon})$ for some constant $\varepsilon>0$, then $T(n)=\Theta(n^{\log_b a})$.
2. If $f(n)=\Theta(n^{\log_b a}\log^k n)$ for a constant $k\ge0$, then $T(n)=\Theta(n^{\log_b a}\log^{k+1}n)$.
3. If $f(n)=\Omega(n^{\log_b a+\varepsilon})$ for some $\varepsilon>0$, and $af(n/b)\le cf(n)$ for some constant $c<1$
   and all large $n$ (the **regularity condition**), then $T(n)=\Theta(f(n))$.

The proof follows the same plan as ours (sum the levels of the recursion tree), with more care to bound sums of a general
$f$ and to handle floors and ceilings; it is in CLRS, Chapter 4. The $\varepsilon$ in cases 1 and 3 means $f$ must be
*polynomially* smaller or larger than $n^{\log_b a}$, not just smaller or larger. That leaves gaps. For example,
$T(n)=2T(n/2)+n/\lg n$ has $f(n)=n/\lg n$, which is smaller than $n^{\log_2 2}=n$ but only by a log factor, so neither case
1 nor case 2 applies. Summing the levels directly, level $j$ costs $2^j\cdot\frac{n/2^j}{\lg(n/2^j)}=\frac{n}{\lg n-j}$, so
the total is $n\left(\frac1{\lg n}+\frac1{\lg n-1}+\dots+\frac11\right)=nH_{\lg n}=\Theta(n\log\log n)$ (Exercise 9).

### Akra-Bazzi

What about recurrences with unequal parts, such as $T(n)=T(n/3)+T(2n/3)+n$? Mohamad Akra and Louay Bazzi proved a much more
general theorem in 1998. For $T(x)=\sum_{i=1}^k a_iT(b_ix)+g(x)$ with constants $a_i>0$ and $0<b_i<1$ (and a mild growth
condition on $g$), find the number $p$ with $\sum_i a_ib_i^p=1$. Then

$$T(x)=\Theta\left(x^p\left(1+\int_1^x\frac{g(u)}{u^{p+1}}\,du\right)\right).$$

For $T(n)=T(n/3)+T(2n/3)+n$: $\frac13+\frac23=1$, so $p=1$, and $\int_1^n\frac{u}{u^2}du=\ln n$, giving
$\Theta(n\log n)$, as our recursion tree found. Akra-Bazzi includes the master theorem as a special case ($k=1$,
$a_1=a$, $b_1=1/b$, so $p=\log_b a$). We will not need it often, but it is good to know that the unbalanced recurrences of
quickselect and median-of-medians (Chapter 6) have a general theory.

## 3.7 Recursion versus iteration

*Level: intermediate.* Any recursive function can be rewritten with loops, and any loop can be written as a recursion.
Which should you use?

### When each is natural

Recursion is natural when the problem's structure is recursive: trees (a tree is a root with smaller trees below it),
divide and conquer (sort the halves, then merge), and searching through choices (try this option, then solve the rest;
Chapter 14). Writing these with loops means managing the stack yourself, which hides the idea.

Iteration is natural when the recursion is a straight line, as in `factorial` and `total`: each call makes one call on
the next smaller input. Then a loop does the same job without the frames, and in Python it is faster and has no depth
limit:

```python
def factorial_loop(n):
    result = 1
    for k in range(2, n + 1):
        result *= k
    return result
```

### Python's recursion limit

Each frame takes memory, and the stack has a fixed size. To avoid crashing the whole interpreter when a recursion runs
away, CPython (the standard Python) counts frames and raises `RecursionError` when there are more than a set limit, by
default 1000. The chapter's program shows it: `factorial` fails at a depth a little above 1000, while `factorial_loop`
computes $20000!$, a number of 256,909 bits, without trouble. You can raise the limit with `sys.setrecursionlimit`, but
only so far before the real stack overflows and the interpreter crashes outright. The practical rules in Python are:

- recursion whose depth is $O(\log n)$ (binary search, fast power, merge sort, balanced trees) is always fine;
- recursion whose depth can be $\Theta(n)$ (walking a linked list, a tree that may be unbalanced, depth-first search on a
  long path) should be written with a loop and, if needed, an explicit stack.

Java and C++ have no counter, but their stacks are limited too (often a few megabytes by default), and a very deep
recursion fails there with a stack overflow.

### Tail calls

A call is a **tail call** if it is the very last thing the function does, so that its result is returned unchanged. In

```python
def factorial_acc(n, acc=1):
    if n == 0:
        return acc
    return factorial_acc(n - 1, acc * n)    # a tail call
```

the recursive call is a tail call: after it returns, there is nothing left to do. Compare `return n * factorial(n - 1)`,
where the multiplication still has to happen afterwards, so the frame must be kept. When a call is in tail position, the
current frame is no longer needed, and a compiler can *reuse* it instead of pushing a new one. That turns the recursion
into a loop, using $O(1)$ stack space. This is **tail-call elimination**. The language Scheme requires it, and so deep
tail recursion is the normal way to write loops there; many compilers for C and other languages do it as an optimization.

CPython does not eliminate tail calls; its designer has explained this as a deliberate choice, partly so that every call
appears in error tracebacks. So in Python, `factorial_acc(5000)` fails just like `factorial(5000)`, and the
accumulator style is a stepping stone to writing the loop yourself.

### Turning recursion into a loop with a stack

When the recursion is not a straight line, for instance when a function makes two calls, you can still remove it by
keeping your own stack of "work still to do". For the recursive maximum:

```python
def rmax_stack(a):
    best = a[0]
    stack = [(0, len(a))]            # ranges still to examine
    while stack:
        lo, hi = stack.pop()
        if hi - lo == 1:
            best = max(best, a[lo])
        else:
            mid = (lo + hi) // 2
            stack.append((lo, mid))
            stack.append((mid, hi))
    return best
```

This is exactly what the computer does with its call stack, written out by hand. It is longer and less clear than the
recursive version, which is why we write recursion when the depth is safe and fall back on this when it is not. Chapter 4
shows the stack itself, and Chapter 15 uses the same transformation for depth-first search.

## 3.8 The Towers of Hanoi

*Level: intermediate.* Three pegs, A, B and C. On peg A sit $n$ discs of different sizes, largest at the bottom. Move the
whole tower to peg C, one disc at a time, never putting a larger disc on a smaller one. The French mathematician Édouard
Lucas published the puzzle in 1883, under the playful pen name "N. Claus de Siam" (an anagram of "Lucas d'Amiens"). It
was sold with a story about priests moving 64 golden discs, at the end of which the world would end; the story came with
the puzzle as part of its presentation, and there is no evidence of an older legend.

### The recursive solution

Think about the largest disc, disc $n$. It cannot move until every other disc is off it, and it can only go to C if C is
empty. So at the moment it moves, the other $n-1$ discs must all be on B. That suggests the whole algorithm:

1. Move the top $n-1$ discs from A to B (using C as the spare peg).
2. Move disc $n$ from A to C.
3. Move the $n-1$ discs from B to C (using A as the spare).

<figure class="mars-fig" markdown="0">
<svg viewBox="0 0 640 300" role="img" aria-label="Three pegs labelled A, B and C on a base. Peg A holds a large orange disc n with a blue block of n minus 1 smaller discs on top. A curved arrow from A to B is labelled step 1, n minus 1 discs from A to B. A curved arrow under the base from A to C is labelled step 2, disc n from A to C. A curved arrow from B to C is labelled step 3, n minus 1 discs from B to C.">
  <line x1="60" y1="200" x2="580" y2="200" stroke="currentColor" stroke-width="3"/>
  <line x1="140" y1="95" x2="140" y2="200" stroke="currentColor" stroke-width="3"/>
  <line x1="320" y1="95" x2="320" y2="200" stroke="currentColor" stroke-width="3"/>
  <line x1="500" y1="95" x2="500" y2="200" stroke="currentColor" stroke-width="3"/>
  <rect x="80" y="178" width="120" height="20" rx="4" fill="#eea66f" stroke="currentColor" stroke-width="1.2"/>
  <text x="140" y="193" font-size="13" text-anchor="middle" fill="currentColor">disc n</text>
  <rect x="100" y="120" width="80" height="56" rx="4" fill="#9cc9ea" fill-opacity="0.7" stroke="currentColor" stroke-width="1.2"/>
  <text x="140" y="146" font-size="13" text-anchor="middle" fill="currentColor">n − 1</text>
  <text x="140" y="162" font-size="13" text-anchor="middle" fill="currentColor">discs</text>
  <text x="140" y="218" font-size="14" text-anchor="middle" fill="currentColor" font-weight="bold">A</text>
  <text x="320" y="218" font-size="14" text-anchor="middle" fill="currentColor" font-weight="bold">B</text>
  <text x="500" y="218" font-size="14" text-anchor="middle" fill="currentColor" font-weight="bold">C</text>
  <path d="M 144 108 Q 230 30 316 100" fill="none" stroke="#7ccf9a" stroke-width="2.5"/>
  <polygon points="316.0,100.0 304.3,96.9 310.6,89.2" fill="#7ccf9a"/>
  <path d="M 324 100 Q 410 30 504 100" fill="none" stroke="#7ccf9a" stroke-width="2.5"/>
  <polygon points="504.0,100.0 492.2,97.4 498.2,89.4" fill="#7ccf9a"/>
  <path d="M 140 222 Q 320 290 500 222" fill="none" stroke="#eea66f" stroke-width="2.5"/>
  <polygon points="500.0,222.0 491.5,230.6 487.9,221.2" fill="#eea66f"/>
  <text x="210" y="40" font-size="13" text-anchor="middle" fill="currentColor">1. n − 1 discs A → B</text>
  <text x="440" y="40" font-size="13" text-anchor="middle" fill="currentColor">3. n − 1 discs B → C</text>
  <text x="320" y="285" font-size="13" text-anchor="middle" fill="currentColor">2. disc n A → C</text>
</svg>
<figcaption>The Towers of Hanoi in three steps. Steps 1 and 3 are the same puzzle with n − 1 discs (solved by
recursion); step 2 is a single move of the largest disc, which ignores everything above it.</figcaption>
</figure>

Steps 1 and 3 are the same puzzle with $n-1$ discs, so we solve them by recursion. They are legal because disc $n$ is
larger than all the others: while it sits at the bottom of a peg, any disc may be put on it, so it never gets in the way.
The base case is $n=0$: nothing to do.

```python
--8<-- "books/algorithms/ch03_hanoi.py"
```

Output:

```
Moves for 3 discs:
  1. disc 1: A -> C
  2. disc 2: A -> B
  3. disc 1: C -> B
  4. disc 3: A -> C
  5. disc 1: B -> A
  6. disc 2: B -> C
  7. disc 1: A -> C

  n  moves made   2^n - 1  BFS minimum
  1           1         1            1
  2           3         3            3
  3           7         7            7
  4          15        15           15
  5          31        31           31
  6          63        63           63
  7         127       127          127
  8         255       255          255
  9         511       511          511
 10        1023      1023         1023
all moves legal; every tower ends on C
```

The program checks each solution by actually playing it on three lists (asserting that every move takes a top disc and
never puts it on a smaller one), and, independently, it finds the true minimum number of moves by **breadth-first
search** over all $3^n$ positions: starting from the initial position, it finds every position reachable in 1 move, then
in 2, and so on, until it reaches the goal. (Chapter 15 proves that breadth-first search finds shortest paths.) For every
$n$ up to 10, the recursive solution uses exactly the minimum. Now we prove both facts for every $n$.

### The number of moves

Let $M(n)$ be the number of moves the algorithm makes. Steps 1 and 3 take $M(n-1)$ each, and step 2 one move:

$$M(0)=0,\qquad M(n)=2M(n-1)+1.$$

**Claim.** $M(n)=2^n-1$.

*Proof by induction.* Base: $M(0)=0=2^0-1$. Step: if $M(k)=2^k-1$, then $M(k+1)=2(2^k-1)+1=2^{k+1}-1$. $\square$

(Unrolling finds the formula: $M(n)=1+2+4+\dots+2^{n-1}$, the geometric sum.) The algorithm is also correct by induction
on $n$: if the recursive calls correctly move $n-1$ discs between any two pegs without breaking the rule, then the three
steps move $n$ discs, as argued above. For 64 discs, $2^{64}-1=18{,}446{,}744{,}073{,}709{,}551{,}615$ moves: at one move
a second, about 585 billion years.

Other patterns are visible in the output. Disc 1, the smallest, moves on every odd-numbered move. Disc $k$ moves
$2^{n-k}$ times in all, and the largest disc moves exactly once, at move $2^{n-1}$, the middle of the solution.

### No solution is shorter

The program's search confirmed the minimum for $n\le10$. A proof covers every $n$.

**Theorem.** Every solution of the $n$-disc puzzle uses at least $2^n-1$ moves.

*Proof.* Let $L(n)$ be the least number of moves in any solution, for any choice of start and target peg (by symmetry, it
is the same for every pair). We show $L(n)\ge2L(n-1)+1$; with $L(0)=0$, induction then gives $L(n)\ge2^n-1$ exactly as for
$M$.

Take any solution for $n\ge1$ discs. Disc $n$ must move at least once, since it starts on A and ends on C. Look at its
**first** move, from A to some peg X. At that moment disc $n$ is the only disc on A (nothing may be on top of it), and X
is empty (nothing smaller may be underneath it). So all $n-1$ smaller discs are on the third peg. They started on A, so
before this move the solution must already have moved the $(n-1)$-disc tower from A to the third peg: at least $L(n-1)$
moves, since only discs $1,\dots,n-1$ moved before this point.

Now look at disc $n$'s **last** move, onto C. At that moment all $n-1$ smaller discs are on the peg that is neither its
source nor C. After that move, they must all get onto C, on top of disc $n$, which does not move again: another tower
move of $n-1$ discs, at least $L(n-1)$ moves.

These two groups of moves are different (one comes before disc $n$'s first move, the other after its last move), and
disc $n$ moves at least once in between. So any solution uses at least $L(n-1)+1+L(n-1)$ moves. $\square$

So the recursive algorithm is optimal: $L(n)=M(n)=2^n-1$. This is a rare situation in which we know an algorithm's cost
*and* a matching lower bound, by an argument that fits on half a page. It also shows that some problems simply need
exponential time, not because we lack a clever idea but because the answer itself is exponentially long: any algorithm
must at least output $2^n-1$ moves.

## Check yourself

??? question "1. Write the code: a recursive function that counts the digits of a whole number n ≥ 0, and prove it correct."

    ```python
    def digits(n):
        if n < 10:
            return 1
        return 1 + digits(n // 10)

    print(digits(0), digits(7), digits(10), digits(2026))   # 1 1 2 4
    ```

    Proof by strong induction on $n$. Base: if $n<10$, $n$ has one digit. Step: if $n\ge10$, removing the last digit gives
    $\lfloor n/10\rfloor$, which is smaller than $n$ and has one digit fewer; by the hypothesis `digits(n // 10)` counts its
    digits, so adding 1 is right. Each call divides by 10, so there are $\Theta(\log n)$ calls.

??? question "2. Prove by induction that 1 + 3 + 5 + ... + (2n − 1) = n² for every n ≥ 1."

    Base $n=1$: $1=1^2$. Step: if $1+3+\dots+(2k-1)=k^2$, then adding the next odd number $2(k+1)-1=2k+1$ gives
    $k^2+2k+1=(k+1)^2$. $\square$

??? question "3. Prove by induction that n! ≥ 2^(n−1) for every n ≥ 1."

    Base $n=1$: $1!=1=2^0$. Step: if $k!\ge2^{k-1}$, then $(k+1)!=(k+1)\,k!\ge2\cdot2^{k-1}=2^k$, since $k+1\ge2$. $\square$

??? question "4. What is wrong with this proof that all horses are the same colour? 'For n horses, base case n = 1 is clear. Step: given k + 1 horses, the first k are the same colour by hypothesis, and so are the last k; the two groups overlap, so all k + 1 are the same colour.'"

    The step fails for $k=1$, going from 1 horse to 2: the first horse and the last horse are groups of one that do *not*
    overlap. The step is correct for every $k\ge2$, but the chain breaks at its first link, so nothing follows. Always check
    that the inductive step works for the smallest $k$ it is used for.

??? question "5. Solve T(n) = T(n − 1) + n, T(0) = 0, and say which algorithms behave like this."

    Unrolling: $T(n)=n+(n-1)+\dots+1+0=\frac{n(n+1)}{2}=\Theta(n^2)$. Any algorithm that does linear work to remove one item
    and recurses on the rest: selection sort (find the minimum, recurse on the remainder), and quicksort when every pivot
    is the smallest element (its worst case, Chapter 5).

??? question "6. Use the master theorem on: (a) T(n) = 8T(n/2) + n², (b) T(n) = T(n/2) + n, (c) T(n) = 16T(n/4) + n², (d) T(n) = 2T(n/4) + √n."

    (a) $\log_2 8=3>2$: case 1, $\Theta(n^3)$. (b) $\log_2 1=0<1$: case 3, $\Theta(n)$; the levels cost $n,n/2,n/4,\dots$,
    under $2n$. (c) $\log_4 16=2=d$: case 2, $\Theta(n^2\log n)$. (d) $\log_4 2=\frac12=d$: case 2, $\Theta(\sqrt n\log n)$.

??? question "7. Write the code: power(x, n) without recursion, using the binary digits of n, and say how many multiplications it makes."

    ```python
    def power_loop(x, n):
        result = 1
        while n > 0:
            if n % 2 == 1:         # this binary digit of n is 1
                result *= x
            x *= x                 # x, x^2, x^4, x^8, ...
            n //= 2
        return result

    print(power_loop(3, 13))       # 1594323
    ```

    Invariant: (result) $\cdot$ (current $x$)$^{\text{current }n}$ equals the original $x^n$. Each pass halves $n$, so there
    are $\lfloor\lg n\rfloor+1$ passes, each with at most two multiplications: $O(\log n)$. Because $13=1101_2$, the result
    picks up $x^1$, $x^4$ and $x^8$: $x^{13}$.

??? question "8. How many calls does the naive recursive Fibonacci function make? def fib(n): return n if n < 2 else fib(n-1) + fib(n-2)"

    Let $C(n)$ be the number of calls for `fib(n)`. Then $C(0)=C(1)=1$ and $C(n)=1+C(n-1)+C(n-2)$. By induction,
    $C(n)=2F_{n+1}-1$: true for $n=0,1$ ($2\cdot1-1=1$), and $1+(2F_n-1)+(2F_{n-1}-1)=2F_{n+1}-1$. Checked by running it for
    $n\le10$: $C(10)=177=2\cdot89-1$. Since $F_n$ grows like $1.618^n$, the calls grow exponentially, even though only
    $n+1$ different values are ever computed. Chapter 13 fixes this by remembering answers (see also the
    [Fibonacci reference page](../../dp/fibonacci.md)).

??? question "9. Solve T(n) = 2T(n/2) + n/lg n for n a power of 2 (T(1) = 0), and explain why the master theorem does not apply."

    Level $j$ (for $j=0,\dots,\lg n-1$) has $2^j$ nodes of size $n/2^j$, each costing $\frac{n/2^j}{\lg n-j}$, so the level
    costs $\frac{n}{\lg n-j}$. Summing, $T(n)=n\left(\frac1{\lg n}+\dots+\frac11\right)=nH_{\lg n}=\Theta(n\log\log n)$, since
    $H_m=\Theta(\log m)$ (Chapter 2). Checked in Python: for $n=2^{20}$ both $T(n)$ and $nH_{20}$ are $3{,}772{,}503.46$. The
    master theorem's case 1 needs $f(n)=O(n^{1-\varepsilon})$, polynomially smaller than $n$; $n/\lg n$ is smaller only by a
    log factor, and it is not $\Theta(n\log^k n)$ for any $k\ge0$ either, so no case fits.

??? question "10. In the n-disc Hanoi solution, at which move does the largest disc move, and how many times does disc k move?"

    The largest disc moves once, at move $M(n-1)+1=2^{n-1}$ (for 4 discs, move 8). Disc $k$ moves once in each solution of
    the $k$-disc subproblem, and the $k$-disc subproblem is solved $2^{n-k}$ times (each level of recursion above it doubles
    the count), so disc $k$ moves $2^{n-k}$ times. Check: $\sum_{k=1}^n2^{n-k}=2^n-1$. For $n=4$ the program's moves give
    disc 1: 8, disc 2: 4, disc 3: 2, disc 4: 1.

??? question "11. Prove that T(n) = T(n/3) + T(2n/3) + n is Ω(n log n) and O(n log n) using the recursion tree, without Akra-Bazzi."

    Every level of the tree that is complete costs exactly $n$, because the sizes at each level add up to $n$ (each node
    of size $m$ has children of sizes $m/3$ and $2m/3$, adding to $m$). Lower bound: the shortest root-to-leaf path keeps
    taking the $n/3$ branch and has length $\log_3 n$, so the first $\log_3 n$ levels are complete: $T(n)\ge n\log_3 n$.
    Upper bound: the longest path keeps taking the $2n/3$ branch and has length $\log_{3/2}n$, and every level costs at most
    $n$: $T(n)\le n(\log_{3/2}n+1)$. Both are $\Theta(n\log n)$ by the change-of-base rule.

??? question "12. Prove that the recursive maximum rmax makes exactly n − 1 comparisons on a list of n elements, for every n ≥ 1."

    Let $C(m)$ be the comparisons (calls to `max` on two values) for a range of length $m$. $C(1)=0$, and
    $C(m)=C(\lfloor m/2\rfloor)+C(\lceil m/2\rceil)+1$. Claim $C(m)=m-1$, by strong induction: base $C(1)=0$; step
    $C(m)=(\lfloor m/2\rfloor-1)+(\lceil m/2\rceil-1)+1=m-1$, since the two halves add up to $m$. This matches the lower
    bound of $n-1$ comparisons from Chapter 1: splitting does not save comparisons, it only rearranges them.

## What you learned

- A recursive function has a base case and a recursive case on strictly smaller inputs; the computer runs it on a call
  stack, one frame per active call, so the recursion depth is its extra space.
- Induction (base case plus inductive step) proves statements for every $n$; strong induction allows the step to use any
  smaller case, which matches recursion on $n/2$.
- A recursive algorithm is proved correct by induction on the input size: the recursive call is the induction hypothesis,
  and termination needs every call to be strictly smaller and valid.
- A recursive algorithm's cost satisfies a recurrence; unrolling, recursion trees and substitution (with explicit
  constants) solve recurrences.
- The master theorem for $T(n)=aT(n/b)+\Theta(n^d)$ compares $d$ with $\log_b a$; its proof is a geometric sum over the levels
  of the recursion tree. Akra-Bazzi handles unequal splits.
- Straight-line recursion is better as a loop in Python (limit about 1000 frames, no tail-call elimination); deep
  branching recursion can use an explicit stack.
- The Towers of Hanoi need exactly $2^n-1$ moves: the recursion achieves it, and an argument about the largest disc proves
  no solution is shorter.

**Next:** [Chapter 4](04-Lists-Stacks-and-Queues.md), how data sits in memory: arrays, growing arrays and amortized cost,
linked lists, stacks and queues.

## Further reading

- T. H. Cormen, C. E. Leiserson, R. L. Rivest and C. Stein, *Introduction to Algorithms*, 4th ed., 2022. Chapter 4
  (divide and conquer, recurrences, the master theorem and its full proof, Akra-Bazzi).
- J. Kleinberg and É. Tardos, *Algorithm Design*, 2005. Chapter 5 (divide and conquer and recurrences).
- J. L. Bentley, D. Haken and J. B. Saxe, "A General Method for Solving Divide-and-Conquer Recurrences", *SIGACT News*,
  1980 (the origin of the master method).
- M. Akra and L. Bazzi, "On the Solution of Linear Recurrence Equations", *Computational Optimization and Applications*,
  1998.
- R. L. Graham, D. E. Knuth and O. Patashnik, *Concrete Mathematics*, 2nd ed., 1994. Chapter 1 starts with the Tower of
  Hanoi; induction and recurrences throughout.
- H. Abelson and G. J. Sussman, *Structure and Interpretation of Computer Programs*, 2nd ed., 1996: recursion, iteration
  and tail calls.
- On this site: [Recursion reference page](../../foundations/recursion.md), [fast power](../../number-theory/fast-power.md),
  [merge sort](../../sorting/merge-sort.md), [Fibonacci](../../dp/fibonacci.md), [Chapter 2](02-Measuring-Cost.md).
