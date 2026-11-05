# 1. What is an algorithm?

*A computer does exactly what it is told, nothing more and nothing less. So before we can make a computer solve a
problem, we must say, in steps that leave nothing to guess, how the problem is solved. That list of steps is an
algorithm. In this chapter you will see what makes a list of steps an algorithm, write your first ones in pseudocode
and in Python, learn what it means for an algorithm to be correct and how to prove it with a loop invariant, count
the steps it takes, meet the oldest algorithm still in daily use, and finish with the surprising fact that some
problems can be stated perfectly clearly and yet no algorithm can ever solve them.*

!!! abstract "In this chapter"
    **You will learn:**

    - what an algorithm is: input, output, and finite, definite steps
    - how to write an algorithm in pseudocode and in Python
    - what "correct" means, and why testing alone cannot prove it
    - how to prove a loop correct with a loop invariant
    - the RAM model: what one "step" of a computer is, and how to count steps
    - why the difference between $n$ and $n^2$ steps decides what is possible
    - Euclid's algorithm, and (advanced) Turing machines and the halting problem

    **You need:** nothing beyond school arithmetic and the habit of reading a short Python program. If Python is new
    to you, any beginner tutorial covers what we use: variables, `if`, `for`, `while`, lists and functions. The proofs
    use only plain logic; the math books at [math.akadian.ca](https://math.akadian.ca/books/) are there if you want
    more practice with proofs.

    **Levels:** 1.1 to 1.6 are beginner; 1.7 is beginner to intermediate; 1.8 is advanced.

## 1.1 Recipes for machines

What do a cake recipe, the method you learned at school for long division, and the program that steers a rover across
Mars have in common? Each is a list of instructions that, followed faithfully, turns something you start with into
something you want. That is the everyday meaning of an **algorithm**: a precise method for solving a problem.

To make the idea sharp, we name its parts.

- The **input** is what the algorithm is given: the numbers to divide, the list to sort, the map and the goal.
- The **output** is what it must produce: the quotient and remainder, the sorted list, the route.
- The **steps** are the instructions that get from one to the other.

A **problem**, in this book, is a description of which output is wanted for each possible input. "Given two whole
numbers, give their greatest common divisor" is a problem. One particular pair, such as 1071 and 462, is an
**instance** of the problem. An algorithm solves the problem if it gives the right output on *every* instance, not just
on the ones we happened to try.

A recipe is not quite an algorithm, because it leaves things to the cook. "Bake until golden" assumes you know what
golden looks like. "Add salt to taste" assumes you have a taste. A machine has neither. Donald Knuth, in the first
volume of *The Art of Computer Programming* (1968), listed the properties that a method must have to count as an
algorithm. In plain words:

1. **Finiteness.** It must always stop after a finite number of steps. A method that might run forever on some input
   is not an algorithm for that problem.
2. **Definiteness.** Every step must be precisely defined, with exactly one meaning. "Pick a large number" is not
   definite; "pick the number 1000" is.
3. **Input.** It takes zero or more inputs, from a stated set (for example, "two positive whole numbers").
4. **Output.** It produces one or more outputs, which have a stated relation to the inputs.
5. **Effectiveness.** Each step is simple enough that it could, in principle, be done exactly by a person with pencil
   and paper in a finite time. "Add these two digits" is effective. "Decide whether this program contains a bug" is,
   as we shall see in 1.8, not.

Why insist on all this? Because the gap between "a method a clever person could follow" and "a method a machine can
follow" is exactly where most mistakes in programming live. A computer cannot notice that a step is ambiguous and ask
what you meant. It picks one meaning, the one written down, and carries on. The rover example shows why this matters
in a very practical way. A radio signal takes between about 3 and 22 minutes to travel between Earth and Mars,
depending on where the two planets are in their orbits. A driver on Earth cannot steer a rover around a rock in real
time. So Perseverance's AutoNav software decides for itself, from its own camera images, where it is safe to drive. Every
one of those decisions is the output of an algorithm that has to be right with no one watching.

### Where the word comes from

The word "algorithm" comes from a person's name. Muhammad ibn Musa al-Khwarizmi was a scholar who worked in Baghdad in
the early ninth century. One of his books explained how to calculate with the Hindu decimal numerals, the digits 0 to
9 with place value that we use today. Only Latin translations of that book survive, and they begin with the words
"Dixit Algorizmi", "Algorizmi said". Over the following centuries "algorism" came to mean the art of calculating with
decimal numerals, the written methods for adding, multiplying and dividing that children still learn. The spelling
drifted to "algorithm", and in the twentieth century the word took on its modern, general meaning: any precise
procedure, not only arithmetic. (The word "algebra" comes from the title of another of his books.)

So the first algorithms anyone called by that name were the school methods for arithmetic. That is a good place to
start thinking about them: long multiplication is a fixed procedure, it works on numbers of any length, it always
stops, and you can carry it out without understanding *why* it works. Understanding why is what this book is for.

## 1.2 A first problem: find the largest number

Here is a problem simple enough that you can solve it at a glance, which makes it a good place to see what writing an
algorithm involves.

**Problem (maximum).** *Input:* a list of $n$ numbers $a_0,a_1,\dots,a_{n-1}$, with $n\ge1$. *Output:* the largest of
them, that is, a number $m$ that is in the list and satisfies $m\ge a_i$ for every $i$.

Look at the list 3, 41, 7, 41, 12, 5. You see at once that the answer is 41. But "see at once" is not an algorithm; your
eyes and brain did something you cannot easily describe. Suppose instead the numbers are written on cards, face down,
and you may turn over one card at a time. Now you need a method. The natural one is:

- Turn over the first card and remember its number. Call it "the best so far".
- Turn over each remaining card in turn. If its number is bigger than the best so far, forget the old best and
  remember this one instead.
- When no cards are left, the best so far is the answer.

This is an algorithm. It works for any number of cards, it always stops (there are only $n$ cards), and every step is
definite. Written as **pseudocode**, a halfway house between English and a programming language that is meant for
people to read, it looks like this:

```text
FIND-MAX(a[0..n-1]):
    best ← a[0]
    for i ← 1 to n-1:
        if a[i] > best:
            best ← a[i]
    return best
```

The arrow `←` means "becomes": `best ← a[0]` puts the value of the first element into the variable `best`. The
notation `a[0..n-1]` means the elements $a_0$ to $a_{n-1}$, both included. Pseudocode lets us leave out details that do
not matter to the idea, such as how the list was read in. In this book pseudocode is short and very close to Python,
so the Python version is almost a copy:

```python
def find_max(a):
    best = a[0]
    for i in range(1, len(a)):
        if a[i] > best:
            best = a[i]
    return best
```

In Python, `range(1, len(a))` gives the numbers $1,2,\dots,n-1$; the last value $n$ is *not* included. This half-open
habit (start included, end excluded) is used all through Python, and we will meet its consequences for off-by-one
errors again.

Here is the algorithm run by hand on our example. Each row shows the state after the loop body for that $i$.

| $i$ | $a_i$ | is $a_i>$ best? | best afterwards |
|---|---|---|---|
| start | | | 3 |
| 1 | 41 | yes | 41 |
| 2 | 7 | no | 41 |
| 3 | 41 | no (equal is not bigger) | 41 |
| 4 | 12 | no | 41 |
| 5 | 5 | no | 41 |

The answer is 41, as expected. Notice the row for $i=3$: the second 41 is not *bigger* than the best, so nothing
changes. Whether we use $>$ or $\ge$ makes no difference to the value returned, but it would matter if we returned the
*position* of the maximum: with $>$ we get the first position where 41 occurs (position 1), with $\ge$ the last
(position 3). Small choices like this are part of the specification, and a careful algorithm designer writes them down.

<figure class="mars-fig" markdown="0">
<svg viewBox="0 0 640 210" role="img" aria-label="An array of six cells holding 3, 41, 7, 41, 12, 5 with indices 0 to 5. Cells 0 to 2 are shaded green and labelled already seen, best equals 41, the largest of these. Cell 3 is orange, labelled a of i, being compared now. Cells 4 and 5 are blue, labelled not yet seen.">
  <text x="105" y="40" font-size="13" text-anchor="middle" fill="currentColor">0</text>
  <text x="175" y="40" font-size="13" text-anchor="middle" fill="currentColor">1</text>
  <text x="245" y="40" font-size="13" text-anchor="middle" fill="currentColor">2</text>
  <text x="315" y="40" font-size="13" text-anchor="middle" fill="currentColor">3</text>
  <text x="385" y="40" font-size="13" text-anchor="middle" fill="currentColor">4</text>
  <text x="455" y="40" font-size="13" text-anchor="middle" fill="currentColor">5</text>
  <text x="40" y="40" font-size="13" fill="currentColor">index</text>
  <rect x="70" y="50" width="70" height="50" fill="#7ccf9a" fill-opacity="0.45" stroke="currentColor" stroke-width="1.5"/>
  <rect x="140" y="50" width="70" height="50" fill="#7ccf9a" fill-opacity="0.45" stroke="currentColor" stroke-width="1.5"/>
  <rect x="210" y="50" width="70" height="50" fill="#7ccf9a" fill-opacity="0.45" stroke="currentColor" stroke-width="1.5"/>
  <rect x="280" y="50" width="70" height="50" fill="#eea66f" fill-opacity="0.7" stroke="currentColor" stroke-width="2.5"/>
  <rect x="350" y="50" width="70" height="50" fill="#9cc9ea" fill-opacity="0.4" stroke="currentColor" stroke-width="1.5"/>
  <rect x="420" y="50" width="70" height="50" fill="#9cc9ea" fill-opacity="0.4" stroke="currentColor" stroke-width="1.5"/>
  <text x="105" y="81" font-size="18" text-anchor="middle" fill="currentColor">3</text>
  <text x="175" y="81" font-size="18" text-anchor="middle" fill="currentColor">41</text>
  <text x="245" y="81" font-size="18" text-anchor="middle" fill="currentColor">7</text>
  <text x="315" y="81" font-size="18" text-anchor="middle" fill="currentColor">41</text>
  <text x="385" y="81" font-size="18" text-anchor="middle" fill="currentColor">12</text>
  <text x="455" y="81" font-size="18" text-anchor="middle" fill="currentColor">5</text>
  <path d="M 72 112 L 72 120 L 278 120 L 278 112" fill="none" stroke="currentColor" stroke-width="1.5"/>
  <text x="175" y="142" font-size="13" text-anchor="middle" fill="currentColor">already seen: a[0..i-1]</text>
  <text x="175" y="162" font-size="13" text-anchor="middle" fill="currentColor">best = 41 is the largest of these</text>
  <line x1="315" y1="112" x2="315" y2="128" stroke="currentColor" stroke-width="1.5"/>
  <text x="315" y="146" font-size="13" text-anchor="middle" fill="currentColor">a[i], i = 3</text>
  <text x="315" y="166" font-size="13" text-anchor="middle" fill="currentColor">compared now</text>
  <path d="M 352 112 L 352 120 L 488 120 L 488 112" fill="none" stroke="currentColor" stroke-width="1.5"/>
  <text x="420" y="142" font-size="13" text-anchor="middle" fill="currentColor">not yet seen</text>
  <text x="560" y="70" font-size="13" text-anchor="middle" fill="currentColor">best</text>
  <rect x="530" y="78" width="60" height="34" fill="#7ccf9a" fill-opacity="0.45" stroke="currentColor" stroke-width="1.5"/>
  <text x="560" y="101" font-size="16" text-anchor="middle" fill="currentColor">41</text>
  <text x="320" y="196" font-size="13" text-anchor="middle" fill="currentColor">The loop invariant of FIND-MAX: before each pass, best is the largest of the green cells.</text>
</svg>
<figcaption>FIND-MAX in the middle of its run. The green part grows by one cell each pass; the invariant says what
"best" means at every moment.</figcaption>
</figure>

## 1.3 Correctness: what "correct" means

When is FIND-MAX "correct"? The question sounds silly for four lines of code, but it is worth answering properly,
because the same way of answering works for programs of four thousand lines, where the answer is not obvious.

### Specifications

A **specification** says exactly what an algorithm must do. It has two halves.

- The **precondition** states what may be assumed about the input. For FIND-MAX: "$a$ is a list of $n\ge1$ numbers
  that can be compared with each other."
- The **postcondition** states what must be true of the output. For FIND-MAX: "the returned value $m$ is equal to
  some $a_i$, and $m\ge a_j$ for every $j$."

An algorithm is **correct** (with respect to its specification) if, for every input that satisfies the
precondition, it stops and its output satisfies the postcondition. Both parts matter. An algorithm that never stops
on some input is not correct, even if it never gives a wrong answer; this is sometimes split into **partial
correctness** (if it stops, the answer is right) plus **termination** (it always stops).

Notice what the precondition does. FIND-MAX reads `a[0]` on its first line. On an empty list there is no `a[0]`, and
Python raises an `IndexError`. That is not a bug *in the algorithm*: the precondition says $n\ge1$, so the empty list is
an input the algorithm has never promised to handle. Whoever calls FIND-MAX must make sure the precondition holds.
Writing preconditions down turns a vague "it crashes sometimes" into a clear contract between two pieces of code.

### Testing is not proof

The first thing anyone does to check a program is to run it on some examples, and you should always do that. The
program for this chapter runs FIND-MAX, a linear search and a sorted insertion on 2000 random lists and compares the
answers with Python's own built-in functions. But think about what a passing test tells you. It tells you the program
gave the right answer *on those inputs*. It says nothing about the others, and there are infinitely many others.

Here is a mistake that tests can easily miss. A beginner sometimes writes:

```python
def find_max_wrong(a):
    best = 0            # "start with nothing"
    for x in a:
        if x > best:
            best = x
    return best
```

Test it on [3, 41, 7], on [5], on [1, 2, 3, 4]: every answer is right. Test it on a thousand random lists of positive
numbers and every answer is still right. Then someone calls it on the temperatures of a winter night on Mars, all
around $-70$ degrees Celsius, and it returns 0, a temperature that never occurred. The bug is in the first line:
starting from 0 assumes that the maximum is at least 0, which the specification never said.

Edsger Dijkstra put the point in a sentence that has been quoted ever since, in his 1970 *Notes on Structured
Programming*: program testing can be used to show the presence of bugs, but never to show their absence. To show
absence, we need an argument that covers every input at once: a **proof**. That does not make testing useless. Tests
catch the slips we make while writing a proof, and a proof tells us which tests are worth writing (for FIND-MAX: all
negative numbers, the maximum first, the maximum last, ties, a single element). The two work together.

## 1.4 Loop invariants

How do you prove something about a loop, which might run ten times or ten million times? You cannot follow every pass.
Instead you find one statement that is true *every* time the loop is about to test its condition, and that, when the
loop finally stops, says exactly what you wanted. Such a statement is a **loop invariant** ("invariant" means
"unchanging": the values change, but the statement about them stays true).

A proof with a loop invariant has three parts, and it is worth learning them by name.

1. **Initialization.** The invariant is true before the first pass of the loop.
2. **Maintenance.** If the invariant is true before a pass, it is still true before the next pass.
3. **Termination.** When the loop stops, the invariant, together with the reason the loop stopped, gives the
   postcondition. (We also check that the loop does stop.)

If this reminds you of climbing a ladder, it should. Initialization puts you on the first rung; maintenance says that
from any rung you can reach the next. Together they show the invariant holds before every pass, however many there are.
This is the principle of mathematical induction, which we study properly in
[Chapter 3](03-Recursion-and-Induction.md). The idea of attaching such assertions to the points of a program, and
proving them, goes back to Robert Floyd's paper "Assigning Meanings to Programs" (1967) and Tony Hoare's "An Axiomatic
Basis for Computer Programming" (1969).

### Example 1: FIND-MAX

**Invariant.** At the start of the pass with index $i$ (just before the test "is $a_i>$ best?"), the variable `best`
equals the largest of $a_0,\dots,a_{i-1}$.

The picture above shows it: the green cells are $a_0,\dots,a_{i-1}$, and `best` is their maximum.

**Initialization.** Before the first pass, $i=1$ and `best` $=a_0$. The largest of the one number $a_0$ is $a_0$. True.

**Maintenance.** Suppose that before the pass with index $i$, `best` is the largest of $a_0,\dots,a_{i-1}$. Call that
value $M$. The pass compares $a_i$ with $M$. There are two cases.

- If $a_i>M$, then $a_i$ is bigger than every one of $a_0,\dots,a_{i-1}$ (since $M$ is at least all of them), so
  $a_i$ is the largest of $a_0,\dots,a_i$. The pass sets `best` to $a_i$. Correct.
- If $a_i\le M$, then $M$ is still at least every number among $a_0,\dots,a_i$, and it is one of them. The pass leaves
  `best` $=M$. Correct.

Either way, after the pass `best` is the largest of $a_0,\dots,a_i$, which is exactly the invariant for the next
index $i+1$.

**Termination.** The loop runs for $i=1,2,\dots,n-1$ and then stops, so it stops after $n-1$ passes. At that moment
the "next index" is $i=n$, and the invariant says `best` is the largest of $a_0,\dots,a_{n-1}$: the whole list. That is
the postcondition. $\square$

Now see what the proof says about `find_max_wrong`. Its invariant would be "`best` is the largest of $0$ and
$a_0,\dots,a_{i-1}$". That invariant is true and the proof goes through, but at termination it gives "the largest of
0 and the whole list", which is *not* the postcondition when every number is negative. The proof does not just fail;
it tells you exactly where the bug is.

### Example 2: linear search

**Problem (search).** *Input:* a list $a_0,\dots,a_{n-1}$ (here $n\ge0$ is allowed) and a value $x$. *Output:* the
smallest index $i$ with $a_i=x$, or $-1$ if $x$ does not occur.

```text
LINEAR-SEARCH(a[0..n-1], x):
    for i ← 0 to n-1:
        if a[i] = x:
            return i
    return -1
```

**Invariant.** At the start of the pass with index $i$, the value $x$ is not among $a_0,\dots,a_{i-1}$.

**Initialization.** For $i=0$ the range $a_0,\dots,a_{-1}$ is empty, and $x$ is certainly not in an empty range.

**Maintenance.** If the pass with index $i$ finds $a_i=x$, it returns, and there is no next pass to worry about.
Otherwise $a_i\ne x$, and together with the invariant, $x$ is not among $a_0,\dots,a_i$: the invariant for $i+1$.

**Termination.** There are two ways out. If the algorithm returns $i$ from inside the loop, then $a_i=x$ and, by the
invariant, no earlier element equals $x$, so $i$ is the *smallest* such index. If the loop finishes all $n$ passes,
the invariant for $i=n$ says $x$ is not among $a_0,\dots,a_{n-1}$, so returning $-1$ is right. The loop has at most
$n$ passes, so it stops. $\square$

The empty range in the initialization step is not a trick. Getting comfortable with "a statement about nothing is true"
saves you from many special cases, and it is the reason Python's half-open ranges work so neatly: `a[0:0]` is the empty
list, and `a[0:i]` grows to `a[0:n]`, the whole list, in steps of one.

### Example 3: inserting into a sorted list

This one is less obvious, and it is the heart of insertion sort, which we meet in
[Chapter 5](05-Sorting-by-Comparison.md) (and on the [insertion sort](../../sorting/insertion-sort.md) reference page).

**Problem (sorted insert).** *Input:* a list $s_0\le s_1\le\dots\le s_{m-1}$ that is sorted, and a value $x$.
*Output:* the same list with $x$ added, still sorted.

The method: make room by adding a slot at the end, then walk from the right, shifting every element bigger than $x$
one place to the right, until you reach an element that is not bigger than $x$ (or the front of the list). Drop $x$
into the hole.

```python
def insert_sorted(a, x):
    a.append(x)              # make room at the end
    j = len(a) - 1
    while j > 0 and a[j - 1] > x:
        a[j] = a[j - 1]      # shift the bigger item one place right
        j -= 1
    a[j] = x
    return a
```

Trace inserting $x=6$ into [2, 5, 8, 13]. The hole is the position $j$ that $x$ will go into if the loop stops now;
we write it as a dash.

| step | list (dash = hole $j$) | $a_{j-1}$ | $a_{j-1}>6$? |
|---|---|---|---|
| start | 2, 5, 8, 13, — | 13 | yes: shift 13 |
| 1 | 2, 5, 8, —, 13 | 8 | yes: shift 8 |
| 2 | 2, 5, —, 8, 13 | 5 | no: stop |
| end | 2, 5, 6, 8, 13 | | |

**Invariant.** Write $m$ for the length before the insertion, so after `append` the positions are $0..m$. At each
test of the `while` condition, positions $0..j-1$ hold $s_0,\dots,s_{j-1}$ unchanged, and positions $j+1..m$ hold
$s_j,\dots,s_{m-1}$, every one of which is greater than $x$. Position $j$ is the hole.

**Initialization.** At the start $j=m$. Positions $0..m-1$ hold $s_0..s_{m-1}$ unchanged, and the range $m+1..m$ is
empty. True.

**Maintenance.** The body runs only if $j>0$ and $a_{j-1}=s_{j-1}>x$. It copies $s_{j-1}$ into position $j$ and
decreases $j$ by one. Now positions $0..j-1$ (with the new $j$) still hold $s_0..s_{j-1}$, and positions $j+1..m$ hold
$s_j,s_{j+1},\dots,s_{m-1}$ with the new $j$: the old ones, all greater than $x$, plus $s_j$ (old $s_{j-1}$), which we
just checked is greater than $x$. True again.

**Termination.** Each pass decreases $j$ by 1 and the loop requires $j>0$, so there are at most $m$ passes. When it
stops, either $j=0$ or $s_{j-1}\le x$. Writing $x$ into the hole gives the list $s_0,\dots,s_{j-1},x,s_j,\dots,s_{m-1}$.
It is sorted: the part before $x$ was sorted and its last element $s_{j-1}$ is at most $x$ (or there is no part
before); the part after $x$ was sorted and its first element $s_j$ is greater than $x$ (or there is no part after).
It contains exactly the old elements and $x$. $\square$

A side effect of the strict test $a_{j-1}>x$: if the list already contains values equal to $x$, the new $x$ goes
*after* them. That property is called **stability**, and in Chapter 5 we will see why sorting algorithms care.

The chapter's program checks all three invariants while it runs, using Python's `assert` statement, which stops the
program with an error if its condition is false. Asserting an invariant is a cheap way to catch a mistake in your
reasoning, though checking these particular invariants costs far more time than the algorithms themselves, so the
asserts are for learning, not for production.

```python
--8<-- "books/algorithms/ch01_first_algorithms.py"
```

Output:

```
find_max([3, 41, 7, 41, 12, 5]) = 41
linear_search([8, 3, 9, 3], 3) = 1
linear_search([8, 3, 9, 3], 5) = -1
insert_sorted([2, 5, 8, 13], 6) = [2, 5, 6, 8, 13]
2000 random tests passed

        n   find_max        all pairs
       10          9               45
     1000        999           499500
  1000000     999999     499999500000  (formula)

Euclid on 1071 and 462:
       a      b  a mod b
    1071    462      147
     462    147       21
     147     21        0
  gcd = 21
```

The second half of that output, the step counts and Euclid, is the subject of sections 1.6 and 1.7.

## 1.5 How computers run code: the RAM model

To say "this algorithm takes so many steps" we have to agree what a step is. A real computer is enormously
complicated: a processor with several cores, each running many instructions at once, several levels of cache memory,
main memory, a disk. If we had to model all of that, every analysis would be specific to one machine and out of date
in a year. Instead, algorithm designers use a simplified, imaginary computer that is close enough to real ones to
predict which algorithm is faster, yet simple enough to reason about with pencil and paper.

The standard one is the **random-access machine**, or **RAM model** (the theory was set out by Stephen Cook and Robert
Reckhow in 1973; the design of the stored-program computer it imitates goes back to the 1940s). It looks like this.

<figure class="mars-fig" markdown="0">
<svg viewBox="0 0 640 260" role="img" aria-label="The RAM model. On the left a processor box with a few registers and a program counter. On the right a column of numbered memory cells, address 0 to 7 and more, each holding one word. Arrows labelled load and store connect them. Below, the list of unit-cost operations: arithmetic, comparison, load, store, jump.">
  <rect x="30" y="30" width="200" height="150" rx="8" fill="#eea66f" fill-opacity="0.25" stroke="currentColor" stroke-width="1.5"/>
  <text x="130" y="54" font-size="15" text-anchor="middle" fill="currentColor" font-weight="bold">processor</text>
  <rect x="50" y="68" width="160" height="26" fill="none" stroke="currentColor" stroke-width="1.2"/>
  <text x="130" y="86" font-size="13" text-anchor="middle" fill="currentColor">register r1</text>
  <rect x="50" y="100" width="160" height="26" fill="none" stroke="currentColor" stroke-width="1.2"/>
  <text x="130" y="118" font-size="13" text-anchor="middle" fill="currentColor">register r2</text>
  <rect x="50" y="138" width="160" height="26" fill="#7ccf9a" fill-opacity="0.35" stroke="currentColor" stroke-width="1.2"/>
  <text x="130" y="156" font-size="13" text-anchor="middle" fill="currentColor">program counter</text>
  <line x1="230" y1="90" x2="372" y2="90" stroke="currentColor" stroke-width="1.5"/>
  <polygon points="380,90 370,85 370,95" fill="currentColor"/>
  <text x="305" y="82" font-size="13" text-anchor="middle" fill="currentColor">store</text>
  <line x1="380" y1="130" x2="238" y2="130" stroke="currentColor" stroke-width="1.5"/>
  <polygon points="230,130 240,125 240,135" fill="currentColor"/>
  <text x="305" y="150" font-size="13" text-anchor="middle" fill="currentColor">load</text>
  <text x="400" y="24" font-size="12" fill="currentColor">address</text>
  <text x="530" y="24" font-size="12" text-anchor="middle" fill="currentColor">memory (one word per cell)</text>
  <rect x="460" y="30" width="140" height="24" fill="#9cc9ea" fill-opacity="0.35" stroke="currentColor" stroke-width="1"/>
  <rect x="460" y="54" width="140" height="24" fill="#9cc9ea" fill-opacity="0.35" stroke="currentColor" stroke-width="1"/>
  <rect x="460" y="78" width="140" height="24" fill="#9cc9ea" fill-opacity="0.35" stroke="currentColor" stroke-width="1"/>
  <rect x="460" y="102" width="140" height="24" fill="#9cc9ea" fill-opacity="0.35" stroke="currentColor" stroke-width="1"/>
  <rect x="460" y="126" width="140" height="24" fill="#9cc9ea" fill-opacity="0.35" stroke="currentColor" stroke-width="1"/>
  <rect x="460" y="150" width="140" height="24" fill="#9cc9ea" fill-opacity="0.35" stroke="currentColor" stroke-width="1"/>
  <rect x="460" y="174" width="140" height="24" fill="#9cc9ea" fill-opacity="0.35" stroke="currentColor" stroke-width="1"/>
  <rect x="460" y="198" width="140" height="24" fill="#9cc9ea" fill-opacity="0.35" stroke="currentColor" stroke-width="1"/>
  <text x="440" y="47" font-size="12" text-anchor="end" fill="currentColor">0</text>
  <text x="440" y="71" font-size="12" text-anchor="end" fill="currentColor">1</text>
  <text x="440" y="95" font-size="12" text-anchor="end" fill="currentColor">2</text>
  <text x="440" y="119" font-size="12" text-anchor="end" fill="currentColor">3</text>
  <text x="440" y="143" font-size="12" text-anchor="end" fill="currentColor">4</text>
  <text x="440" y="167" font-size="12" text-anchor="end" fill="currentColor">5</text>
  <text x="440" y="191" font-size="12" text-anchor="end" fill="currentColor">6</text>
  <text x="440" y="215" font-size="12" text-anchor="end" fill="currentColor">7</text>
  <text x="530" y="47" font-size="12" text-anchor="middle" fill="currentColor">3</text>
  <text x="530" y="71" font-size="12" text-anchor="middle" fill="currentColor">41</text>
  <text x="530" y="95" font-size="12" text-anchor="middle" fill="currentColor">7</text>
  <text x="530" y="119" font-size="12" text-anchor="middle" fill="currentColor">41</text>
  <text x="530" y="143" font-size="12" text-anchor="middle" fill="currentColor">12</text>
  <text x="530" y="167" font-size="12" text-anchor="middle" fill="currentColor">5</text>
  <text x="530" y="191" font-size="12" text-anchor="middle" fill="currentColor">...</text>
  <text x="530" y="215" font-size="12" text-anchor="middle" fill="currentColor">...</text>
  <text x="530" y="240" font-size="12" text-anchor="middle" fill="currentColor">... as many cells as needed</text>
  <text x="30" y="210" font-size="13" fill="currentColor">one step each: + − × ÷, compare,</text>
  <text x="30" y="230" font-size="13" fill="currentColor">load a cell, store a cell, jump</text>
</svg>
<figcaption>The RAM model: a processor with a few registers, and a memory of numbered cells. Reading or writing any
cell, given its address, costs one step, wherever the cell is.</figcaption>
</figure>

- **Memory** is a long row of **cells**, numbered $0,1,2,\dots$. The number of a cell is its **address**. Each cell
  holds one **word**: a whole number of some fixed size (on today's computers, 64 binary digits).
- The **processor** has a few **registers**, cells inside the processor where arithmetic happens, and a **program
  counter**, which holds the number of the instruction to do next.
- The program is a list of simple instructions, and each one costs **one step**: add, subtract, multiply or divide two
  words; compare two words; **load** a word from a memory cell into a register, given the cell's address; **store** a
  register into a cell; **jump** to another instruction, possibly only if a comparison came out true.

The phrase "random access" means that *any* cell can be read in one step, if you know its address. You do not have to
walk past cells 0 to 999 to reach cell 1000. This single fact is why looking up `a[i]` in a list is fast whatever $i$
is, and it is the basis of almost every data structure in this book. In [Chapter
4](04-Lists-Stacks-and-Queues.md) we see how a list is laid out in memory so that the address of `a[i]` can be computed
from $i$ with one multiplication and one addition.

### What the model leaves out, and why that is fine

The model is a simplification, and it is honest to say where it is wrong.

- **Word size.** If a word could hold a number of any size, one "multiply" could multiply two numbers with a million
  digits each, and the model would be absurdly powerful. So we assume a word is big enough to hold an address into our
  data and numbers of a similar size: for $n$ items, about $\log_2 n$ bits or a constant multiple of that, and no more.
  Arithmetic on bigger numbers must be built out of word operations, and costs more steps. (Python hides this: its
  integers grow as large as needed, and multiplying two huge ones takes much longer than multiplying two small ones.)
- **Memory speed.** In a real machine, reading a cell that was used recently, or one next to it, is far faster than
  reading a cell far away, because of caches. The RAM model says all reads cost the same. Section 2.9 of the next
  chapter shows how large this effect can be, and Chapter 24 introduces models that take it into account.
- **Parallelism.** Real processors do several things at once. The RAM model does one thing at a time. Chapter 24 covers
  models with many processors.

Despite these gaps, the RAM model predicts very well which of two algorithms will be faster on large inputs. That is all
we ask of it.

### What one line of Python costs

A line of Python is not one RAM step. `best = a[i]` involves finding where `a` is, computing the address of element $i$,
loading it, and storing it. The point is that it costs a *fixed* number of steps, the same whether the list has ten
elements or ten million. That is enough for everything we do: when we count "steps", we count operations each of which
costs at most some fixed number of machine instructions. Some Python lines are *not* fixed cost, and you must not count
them as one step:

- `max(a)`, `sum(a)`, `x in a`, `a.index(x)` and `sorted(a)` each look at every element of `a`;
- `a[:i]` makes a copy of $i$ elements, and `a + b` copies both lists;
- `a.insert(0, x)` and `a.pop(0)` shift every element of the list (Chapter 4 explains why).

This is exactly why the asserted invariants in the chapter's program are slow: `max(a[:i])` costs about $i$ steps on
every pass, which turns a loop of $n$ steps into one of about $n^2/2$.

## 1.6 Counting steps by hand

Let us count the steps of FIND-MAX in the RAM model. We do not need the exact machine instructions. We give each line
a cost, the fixed number of steps it takes once, and count how many times each line runs.

| line | cost | times run |
|---|---|---|
| `best ← a[0]` | $c_1$ | $1$ |
| `for i ← 1 to n-1` (set, test and add 1 to $i$) | $c_2$ | $n$ (the test runs once more, when it fails) |
| `if a[i] > best` | $c_3$ | $n-1$ |
| `best ← a[i]` | $c_4$ | between $0$ and $n-1$ |
| `return best` | $c_5$ | $1$ |

The number of times `best ← a[i]` runs depends on the input. If the list is in decreasing order, it never runs; if
the list is in increasing order, it runs every time. Call that number $k$, with $0\le k\le n-1$. The total cost is

$$T(n)=c_1+c_2n+c_3(n-1)+c_4k+c_5.$$

The worst case is $k=n-1$, when

$$T(n)=(c_2+c_3+c_4)\,n+(c_1-c_3-c_4+c_5).$$

That has the form $An+B$ for some constants $A$ and $B$ that depend on the machine but not on $n$. The best case
($k=0$) also has the form $An+B$, with a smaller $A$. So on every input FIND-MAX takes time that grows in proportion
to $n$: double the list and you double the time. We say its running time is **linear** in $n$.

Often we pick one operation that is done the most and count only that. For FIND-MAX the natural choice is the
**comparison** `a[i] > best`, which happens exactly $n-1$ times on every input. Every other line runs at most about
as many times as the comparison, so counting comparisons gives the right picture up to a constant factor.

### Can we do better?

Is $n-1$ comparisons the best possible for finding the maximum? Yes, and the reason is a nice first example of a
**lower bound**, a proof that *no* algorithm can do better.

*Claim.* Any algorithm that finds the maximum of $n$ distinct numbers by comparing them two at a time must make at least
$n-1$ comparisons.

*Proof.* Think of each comparison as a game between two numbers, which the larger one wins. Every number except the
maximum must lose at least one game: if some number $y$ other than the maximum never lost, the algorithm has no evidence
that $y$ is not the largest, and an adversary could quietly make $y$ larger than everything without changing the result
of any comparison the algorithm made (since $y$ only won its games, making it larger keeps them won). The algorithm would
then answer wrongly on that input. Each comparison has exactly one loser, so $n-1$ losers need at least $n-1$
comparisons. $\square$

So FIND-MAX is not just good, it is **optimal** for its problem in this model. Most problems in this book do not have such
clean answers, and finding lower bounds is one of the hardest parts of the subject. Chapter 5 proves the most famous
one: sorting $n$ items by comparisons needs about $n\log_2 n$ of them.

### A first taste of growth

Now compare FIND-MAX with a different algorithm, one that compares every pair of elements, for example to check
whether any two are equal. With $n$ elements there are $n(n-1)/2$ pairs. (Each of the $n$ elements pairs with $n-1$
others; that counts every pair twice, once from each end, so divide by 2.) The chapter's program counts both:

| $n$ | FIND-MAX: $n-1$ | all pairs: $n(n-1)/2$ |
|---|---|---|
| 10 | 9 | 45 |
| 1000 | 999 | 499,500 |
| 1,000,000 | 999,999 | 499,999,500,000 |

At ten items, nobody cares. At a million items, the pairwise algorithm does about half a million times more work.
Suppose a computer does $10^9$ simple steps per second (a fair round number for a modern processor, which can be
faster still). Then $n$ steps and $n^2$ steps take:

| $n$ | $n$ steps | $n^2$ steps |
|---|---|---|
| 10 | 10 nanoseconds | 100 nanoseconds |
| 1000 | 1 microsecond | 1 millisecond |
| $10^6$ | 1 millisecond | 1000 seconds, about 17 minutes |
| $10^9$ | 1 second | $10^9$ seconds, about 32 years |

This table is the most important idea in the chapter after correctness. Machines get faster by constant factors: a
computer ten times faster makes the last row about three years instead of thirty-two. Algorithms differ by factors
that *grow with the input*. No hardware upgrade turns a quadratic algorithm on a billion items into a fast one. Choosing
the right algorithm matters more than any other decision about speed, and the next chapter gives us the language to
talk about it precisely: Big-O notation and its relatives (see also the [Big-O reference
page](../../foundations/big-o.md)).

## 1.7 Euclid's algorithm

The algorithms so far are new; this one is more than two thousand years old. It appears in Book VII of Euclid's
*Elements*, written in Greek around 300 BC, and it is used today inside every secure web connection (see the
[cryptography book](https://cryptography.akadian.ca/book/)). In the second volume of *The Art of Computer Programming*, Knuth
calls it the oldest nontrivial algorithm that has survived to the present day.

**Problem (greatest common divisor).** *Input:* two whole numbers $a\ge0$ and $b\ge0$, not both zero. *Output:* the
largest whole number that divides both, written $\gcd(a,b)$.

For example, the divisors of 12 are 1, 2, 3, 4, 6, 12 and those of 18 are 1, 2, 3, 6, 9, 18, so $\gcd(12,18)=6$.
Listing divisors is fine for small numbers and hopeless for numbers with hundreds of digits. Euclid's method avoids it
entirely.

```text
GCD(a, b):
    while b ≠ 0:
        (a, b) ← (b, a mod b)
    return a
```

Here $a\bmod b$ is the remainder when $a$ is divided by $b$: for example $1071\bmod 462=147$, because
$1071=2\times462+147$. The trace from the program:

| $a$ | $b$ | $a\bmod b$ |
|---|---|---|
| 1071 | 462 | 147 |
| 462 | 147 | 21 |
| 147 | 21 | 0 |
| 21 | 0 | stop |

So $\gcd(1071,462)=21$. Check: $1071=21\times51$ and $462=21\times22$, and 51 and 22 have no common factor. Three
divisions instead of listing hundreds of divisors.

### Why it is correct

The whole algorithm rests on one fact.

**Lemma.** If $b>0$, then $\gcd(a,b)=\gcd(b,\,a\bmod b)$.

*Proof.* Write $a=qb+r$ where $q$ is the quotient and $r=a\bmod b$. We show that the pairs $(a,b)$ and $(b,r)$ have
exactly the same common divisors; then their *greatest* common divisors are equal too.

- If $d$ divides $a$ and $b$, then $d$ divides $a-qb=r$, so $d$ is a common divisor of $b$ and $r$.
- If $d$ divides $b$ and $r$, then $d$ divides $qb+r=a$, so $d$ is a common divisor of $a$ and $b$. $\square$

Now the loop invariant is easy to state. Write $g$ for the gcd of the *original* inputs.

**Invariant.** At each test of `b ≠ 0`, $\gcd(a,b)=g$.

**Initialization.** At the start, $a$ and $b$ are the inputs. **Maintenance.** The body replaces $(a,b)$ with
$(b,a\bmod b)$, which has the same gcd by the lemma (the body only runs when $b\ne0$, as the lemma needs).
**Termination.** Each pass replaces $b$ by $a\bmod b$, which is smaller than $b$. A whole number $\ge0$ cannot decrease
forever, so eventually $b=0$. Then the invariant says $\gcd(a,0)=g$, and $\gcd(a,0)=a$, because every number divides 0,
so the common divisors of $a$ and 0 are just the divisors of $a$, the largest of which is $a$ itself. Returning $a$ is
correct. $\square$

(If $a<b$ at the start, the first pass just swaps them, since $a\bmod b=a$. The algorithm needs no special case.)

### How fast is it?

The termination argument shows only that $b$ goes down by at least one per pass, which would allow about $b$ passes:
for numbers with 300 digits, hopelessly many. In fact it is far faster. Exercise 8 asks you to prove that every two
passes at least halve the first number, so the number of passes is at most about $2\log_2 a$: for 300-digit numbers, at
most about two thousand. Gabriel Lamé proved a sharper bound in 1844, using the Fibonacci numbers; it is often counted
as the first analysis of an algorithm's running time, and Chapter 19 proves it. The [gcd reference
page](../../number-theory/gcd.md) has the code in three languages and an animation.

This contrast, between "it obviously stops" and "it stops *quickly*", is the step from correctness to efficiency that
the next chapter takes.

<figure class="play" data-play="euclidsq"><span class="ai-tag">AI-created</span><figcaption><b>Watch it.</b> Euclid's algorithm as cutting the biggest squares out of a rectangle, starting with the example above, gcd(1071, 462). Type other numbers to try them.</figcaption></figure>

## 1.8 Turing machines and the limits of computation

*Level: advanced.* Everything so far assumed that a problem *has* an algorithm and asked how good it is. In 1936 Alan
Turing asked a deeper question: is there a precise definition of "algorithm" at all, and if so, are there problems that
no algorithm can solve? His answer to both was yes. This section explains his definition, why it is believed to capture
every algorithm, and the most famous problem that no algorithm solves.

### Why a definition was needed

Around 1928 David Hilbert and Wilhelm Ackermann posed the *Entscheidungsproblem* ("decision problem"): find a
mechanical procedure that takes any statement of formal logic and decides whether it is provable. To prove that *no*
such procedure exists, you must be able to talk about *all possible* procedures, so you need an exact definition of
"mechanical procedure". In 1936, Alonzo Church (with his lambda calculus) and Turing (with his machines) each gave one,
and each proved that the Entscheidungsproblem has no solution. Turing's paper was "On Computable Numbers, with an
Application to the Entscheidungsproblem".

### The machine

Turing imagined a person doing a calculation with pencil and paper, and stripped the activity down to its bare parts.
The result is the **Turing machine**:

- a **tape**, divided into cells, unbounded in both directions, each cell holding one symbol from a finite
  **alphabet** (for us: 0, 1 and the blank, written `_`);
- a **head** that sits over one cell at a time and can read and write it;
- a finite set of **states**, one of them the start state and one or more of them halting states;
- a **transition table**: for each state and each symbol read, it says which symbol to write, whether to move the head
  one cell left or right, and which state to go into next.

The machine starts in the start state, with the input written on the tape and the head on its first symbol. It
repeatedly looks up (current state, symbol under head) in the table and does what the table says. If it enters a
halting state it stops, and whatever is on the tape is the output.

<figure class="mars-fig" markdown="0">
<svg viewBox="0 0 640 220" role="img" aria-label="A Turing machine tape with cells holding blank, 1, 0, 1, 1, blank, blank. A head marked carry points at the last 1. Below, the transition table of the increment machine: in state right, on 0 or 1 write it back and move right; on blank move left and go to carry. In state carry, on 1 write 0 and move left; on 0 or blank write 1 and halt.">
  <rect x="80" y="30" width="60" height="44" fill="none" stroke="currentColor" stroke-width="1.2" stroke-dasharray="4 3"/>
  <rect x="140" y="30" width="60" height="44" fill="#9cc9ea" fill-opacity="0.35" stroke="currentColor" stroke-width="1.5"/>
  <rect x="200" y="30" width="60" height="44" fill="#9cc9ea" fill-opacity="0.35" stroke="currentColor" stroke-width="1.5"/>
  <rect x="260" y="30" width="60" height="44" fill="#9cc9ea" fill-opacity="0.35" stroke="currentColor" stroke-width="1.5"/>
  <rect x="320" y="30" width="60" height="44" fill="#eea66f" fill-opacity="0.6" stroke="currentColor" stroke-width="2.5"/>
  <rect x="380" y="30" width="60" height="44" fill="none" stroke="currentColor" stroke-width="1.2" stroke-dasharray="4 3"/>
  <rect x="440" y="30" width="60" height="44" fill="none" stroke="currentColor" stroke-width="1.2" stroke-dasharray="4 3"/>
  <text x="110" y="58" font-size="18" text-anchor="middle" fill="currentColor">_</text>
  <text x="170" y="58" font-size="18" text-anchor="middle" fill="currentColor">1</text>
  <text x="230" y="58" font-size="18" text-anchor="middle" fill="currentColor">0</text>
  <text x="290" y="58" font-size="18" text-anchor="middle" fill="currentColor">1</text>
  <text x="350" y="58" font-size="18" text-anchor="middle" fill="currentColor">1</text>
  <text x="410" y="58" font-size="18" text-anchor="middle" fill="currentColor">_</text>
  <text x="470" y="58" font-size="18" text-anchor="middle" fill="currentColor">_</text>
  <text x="50" y="58" font-size="16" text-anchor="middle" fill="currentColor">...</text>
  <text x="535" y="58" font-size="16" text-anchor="middle" fill="currentColor">...</text>
  <polygon points="350,80 340,98 360,98" fill="#eea66f" stroke="currentColor" stroke-width="1"/>
  <text x="350" y="116" font-size="13" text-anchor="middle" fill="currentColor">head, state "carry"</text>
  <text x="40" y="146" font-size="13" fill="currentColor" font-weight="bold">table</text>
  <text x="40" y="168" font-size="13" fill="currentColor">right, 0 or 1: write same, move R, stay right</text>
  <text x="40" y="188" font-size="13" fill="currentColor">right, _: move L, go to carry</text>
  <text x="360" y="168" font-size="13" fill="currentColor">carry, 1: write 0, move L, stay carry</text>
  <text x="360" y="188" font-size="13" fill="currentColor">carry, 0 or _: write 1, halt</text>
</svg>
<figcaption>The binary increment machine about to add the carry to 1011 (eleven). Its whole "program" is the
six-line table.</figcaption>
</figure>

Here is a small, real machine: it adds 1 to a number written in binary. In state `right` it walks right to the blank
after the last digit, then steps back and enters state `carry`. In state `carry` it does what you do by hand when you
add 1: a 1 becomes 0 and the carry moves left; a 0 (or a blank, if we run off the left end) becomes 1 and we are done.
The program below simulates it, showing the head's cell in brackets.

```python
--8<-- "books/algorithms/ch01_turing_machine.py"
```

Output:

```
Incrementing 1011 (eleven):
  step  0  state right  tape [1]011
  step  1  state right  tape 1[0]11
  step  2  state right  tape 10[1]1
  step  3  state right  tape 101[1]
  step  4  state right  tape 1011[_]
  step  5  state carry  tape 101[1]_
  step  6  state carry  tape 10[1]0_
  step  7  state carry  tape 1[0]00_
  result 1100 after 8 steps

          0 + 1 =         1   (3 steps)
          1 + 1 =        10   (4 steps)
        111 + 1 =      1000   (8 steps)
       1001 + 1 =      1010   (7 steps)
   11111111 + 1 = 100000000   (18 steps)
```

The result 1100 is twelve. Count the steps: a number of $d$ digits that ends in $k$ ones takes $d+1$ steps to walk
right and step back, and then $k+1$ carry steps, so $d+k+2$ steps in all. For 1011 that is $4+2+2=8$.

### The Church-Turing thesis

A Turing machine looks feeble. It has no arithmetic, no memory addresses, one step at a time along a tape. Yet anything
a RAM can compute, a Turing machine can compute too: it can keep the RAM's memory on its tape as a list of
(address, value) pairs and simulate each RAM step by searching the tape. The simulation is slow, but a polynomial
slowdown only, and every other model of computation anyone has proposed (Church's lambda calculus, Gödel's recursive
functions, Post's systems, every programming language) has been shown to compute exactly the same functions.

This led to the **Church-Turing thesis**: *anything that can be computed by an algorithm, in the informal sense of
1.1, can be computed by a Turing machine.* It is called a thesis, not a theorem, because "algorithm in the informal
sense" is not a mathematical object, so the statement cannot be proved. It is a claim that the definition is the right
one, and the evidence for it is overwhelming. Its practical meaning: if you prove that no Turing machine solves a
problem, then no program in any language on any computer ever built will solve it either.

A problem whose answer is yes or no is called a **decision problem**. It is **decidable** if some Turing machine
(equivalently, some program) always halts and gives the right answer; otherwise it is **undecidable**.

### The halting problem

**The halting problem.** *Input:* the text of a program $P$ and an input $x$. *Output:* yes if $P$, run on $x$,
eventually halts; no if it runs forever.

This would be enormously useful. A tool that solved it could warn you about every infinite loop before you ran your
code. Turing proved that no such tool can exist.

**Theorem (Turing, 1936).** The halting problem is undecidable.

*Proof.* Suppose, to get a contradiction, that someone has written a function `halts(P, x)` that always returns, and
returns `True` exactly when program `P` halts on input `x`. Using it, write this program:

```python
def D(P):
    if halts(P, P):     # would P halt if given its own text as input?
        while True:     # then loop forever
            pass
    else:
        return          # otherwise halt at once
```

`D` takes the text of a program and asks what that program does on *its own text*. (Feeding a program its own text is
nothing strange: a program's text is just a string, and a string can be any program's input.) Then it does the
opposite.

Now run `D` on its own text, `D(D)`. Does it halt?

- If `D(D)` halts, then `halts(D, D)` returned `True`, so `D` took the first branch and loops forever. Contradiction.
- If `D(D)` runs forever, then `halts(D, D)` returned `False`, so `D` took the second branch and halted. Contradiction.

Both possibilities are impossible. The only assumption we made was that `halts` exists, so it does not. $\square$

<figure class="mars-fig" markdown="0">
<svg viewBox="0 0 560 300" role="img" aria-label="A table with programs P1 to P5 as rows and the same programs as inputs in columns. Each cell says halts or loops. The diagonal cells are shaded orange. Below, a row for D shows the opposite of each diagonal entry, so D differs from every row at the diagonal position.">
  <text x="70" y="44" font-size="13" text-anchor="middle" fill="currentColor">input →</text>
  <text x="160" y="44" font-size="13" text-anchor="middle" fill="currentColor">P1</text>
  <text x="240" y="44" font-size="13" text-anchor="middle" fill="currentColor">P2</text>
  <text x="320" y="44" font-size="13" text-anchor="middle" fill="currentColor">P3</text>
  <text x="400" y="44" font-size="13" text-anchor="middle" fill="currentColor">P4</text>
  <text x="480" y="44" font-size="13" text-anchor="middle" fill="currentColor">P5</text>
  <g font-size="13" text-anchor="middle" fill="currentColor">
    <text x="70" y="79">P1</text><text x="70" y="115">P2</text><text x="70" y="151">P3</text><text x="70" y="187">P4</text><text x="70" y="223">P5</text>
  </g>
  <rect x="120" y="56" width="80" height="36" fill="#eea66f" fill-opacity="0.6"/>
  <rect x="200" y="92" width="80" height="36" fill="#eea66f" fill-opacity="0.6"/>
  <rect x="280" y="128" width="80" height="36" fill="#eea66f" fill-opacity="0.6"/>
  <rect x="360" y="164" width="80" height="36" fill="#eea66f" fill-opacity="0.6"/>
  <rect x="440" y="200" width="80" height="36" fill="#eea66f" fill-opacity="0.6"/>
  <g stroke="currentColor" stroke-width="1" fill="none">
    <rect x="120" y="56" width="400" height="180"/>
    <line x1="200" y1="56" x2="200" y2="236"/><line x1="280" y1="56" x2="280" y2="236"/>
    <line x1="360" y1="56" x2="360" y2="236"/><line x1="440" y1="56" x2="440" y2="236"/>
    <line x1="120" y1="92" x2="520" y2="92"/><line x1="120" y1="128" x2="520" y2="128"/>
    <line x1="120" y1="164" x2="520" y2="164"/><line x1="120" y1="200" x2="520" y2="200"/>
  </g>
  <g font-size="13" text-anchor="middle" fill="currentColor">
    <text x="160" y="79">halts</text><text x="240" y="79">loops</text><text x="320" y="79">halts</text><text x="400" y="79">halts</text><text x="480" y="79">loops</text>
    <text x="160" y="115">loops</text><text x="240" y="115">loops</text><text x="320" y="115">halts</text><text x="400" y="115">loops</text><text x="480" y="115">halts</text>
    <text x="160" y="151">halts</text><text x="240" y="151">halts</text><text x="320" y="151">halts</text><text x="400" y="151">loops</text><text x="480" y="151">loops</text>
    <text x="160" y="187">loops</text><text x="240" y="187">halts</text><text x="320" y="187">loops</text><text x="400" y="187">loops</text><text x="480" y="187">halts</text>
    <text x="160" y="223">halts</text><text x="240" y="223">loops</text><text x="320" y="223">loops</text><text x="400" y="223">halts</text><text x="480" y="223">halts</text>
  </g>
  <rect x="120" y="250" width="400" height="36" fill="#7ccf9a" fill-opacity="0.4" stroke="currentColor" stroke-width="1.5"/>
  <g stroke="currentColor" stroke-width="1"><line x1="200" y1="250" x2="200" y2="286"/><line x1="280" y1="250" x2="280" y2="286"/><line x1="360" y1="250" x2="360" y2="286"/><line x1="440" y1="250" x2="440" y2="286"/></g>
  <g font-size="13" text-anchor="middle" fill="currentColor">
    <text x="70" y="273" font-weight="bold">D</text>
    <text x="160" y="273">loops</text><text x="240" y="273">halts</text><text x="320" y="273">loops</text><text x="400" y="273">halts</text><text x="480" y="273">loops</text>
  </g>
</svg>
<figcaption>The diagonal argument. Row Pi lists what program Pi does on each program's text. D does the opposite
of the orange diagonal, so D's row differs from row Pi in column Pi: D is none of the listed programs. Yet
if <code>halts</code> existed, D would be a program and must appear somewhere in the list.</figcaption>
</figure>

The figure shows why this is called a **diagonal argument**. List every program as a row, and every program's text as
a column; in each cell write what that row's program does on that column's input. The program $D$ is built to
disagree with the diagonal: on input $P_i$ it does the opposite of what $P_i$ does on $P_i$. So $D$'s behaviour differs
from every row in at least one place, and $D$ cannot be any row. But if `halts` existed, $D$ would be a program, and
every program is a row. The same trick was used by Georg Cantor in 1891 to prove that there are more real numbers than
whole numbers.

### What follows, and what does not

The halting problem is not an isolated curiosity. Once one problem is known to be undecidable, others follow by
**reduction**: show that a solver for the new problem could be used to build a solver for the halting problem. For
example, "does program $P$ ever print the word `hello`?" is undecidable, because a solver for it would solve halting
(take any $P$ and $x$; build a program that runs $P$ on $x$, with its own printing switched off, and prints `hello` when
it finishes). Rice's theorem (Henry Rice, 1953) generalizes this: every nontrivial question about *what a program
computes*, as opposed to how its text looks, is undecidable. Chapter 22 uses reductions in the same way, with time
limits added, to compare the difficulty of problems that *are* decidable.

It is just as important to see what the theorem does *not* say.

- It does not say that we can never tell whether a particular program halts. For FIND-MAX we proved it does. Tools that
  check programs for infinite loops exist and are useful; the theorem says only that no single tool can be right about
  *every* program, so every such tool sometimes answers "I don't know".
- It does not say the question is meaningless. Every program on every input either halts or doesn't. The answer exists;
  no algorithm can compute it in general.
- Running the program and waiting does not solve it. If $P$ halts, you will see it halt, so the "yes" answers can be
  confirmed. But if $P$ has not halted after a billion steps, it may halt after a billion and one. Problems like this,
  where "yes" can be confirmed but "no" cannot be in general, are called **semi-decidable** (or recursively
  enumerable).

There is also a counting reason that most problems are unsolvable. A program is a finite string of characters, so
programs can be listed one after another (all strings of length 1, then length 2, and so on): there are *countably*
many. But the yes-or-no problems about whole numbers correspond to infinite sequences of yes and no, and Cantor's
diagonal argument shows that those cannot be listed: there are *uncountably* many. So almost all problems have no
algorithm at all. The ones we care about in this book are the lucky few that do, and our question will be how fast.

## Check yourself

??? question "1. Trace FIND-MAX on the list 5, 2, 9, 9, 1. Give the value of best after each pass and the number of comparisons."

    Start: best $=5$. $i=1$: $2>5$? no, best $=5$. $i=2$: $9>5$? yes, best $=9$. $i=3$: $9>9$? no, best $=9$.
    $i=4$: $1>9$? no, best $=9$. The answer is 9, after $n-1=4$ comparisons, as for every list of 5 numbers.

??? question "2. Give an input on which find_max_wrong (which starts with best = 0) fails, and say which part of the loop-invariant proof breaks."

    Any list of negative numbers, for example $[-3,-7]$: it returns 0, which is not in the list. Initialization is
    where it goes wrong: before the loop, best $=0$ is not "the largest of $a_0$" (or of any part of the list). The
    invariant that *is* true, "best is the largest of 0 and the elements seen", gives the wrong postcondition at
    termination.

??? question "3. Write the code: a function that returns the position of the largest element (the first position, if there are ties). State its loop invariant."

    ```python
    def argmax(a):
        best_i = 0
        for i in range(1, len(a)):
            if a[i] > a[best_i]:      # strict: keep the first of equal values
                best_i = i
        return best_i
    ```

    Invariant: at the start of the pass with index $i$, $a_{\text{best\_i}}$ is the largest of $a_0,\dots,a_{i-1}$,
    and best_i is the smallest index where that value occurs among them. Maintenance: a strictly larger $a_i$ takes
    over; an equal one does not, so the first position is kept. `argmax([3, 41, 7, 41])` returns 1.

??? question "4. How many comparisons a[i] = x does LINEAR-SEARCH make in the best case and in the worst case, on a list of n elements?"

    Best case: 1, when $x=a_0$. Worst case: $n$, when $x$ is last or not in the list at all. Unlike FIND-MAX, its
    cost depends on the input, which is why the next chapter separates worst, best and average cases.

??? question "5. Compute gcd(252, 198) with Euclid's algorithm, showing the table."

    | $a$ | $b$ | $a\bmod b$ |
    |---|---|---|
    | 252 | 198 | 54 |
    | 198 | 54 | 36 |
    | 54 | 36 | 18 |
    | 36 | 18 | 0 |

    Then $b=0$ with $a=18$, so $\gcd(252,198)=18$. Check: $252=18\times14$, $198=18\times11$.

??? question "6. Trace insert_sorted inserting 4 into [1, 3, 5, 7], with a table of the hole's position."

    After `append`, the list is 1, 3, 5, 7, — with the hole at $j=4$. $a_3=7>4$: shift, hole at 3. $a_2=5>4$: shift,
    hole at 2. $a_1=3>4$? no: stop. Write 4 at position 2: [1, 3, 4, 5, 7]. Two shifts, three comparisons.

??? question "7. Write the code: sum a list with a loop, and prove it correct with a loop invariant."

    ```python
    def total(a):
        s = 0
        for i in range(len(a)):
            s = s + a[i]
        return s
    ```

    Invariant: at the start of the pass with index $i$, $s=a_0+\dots+a_{i-1}$. Initialization: $i=0$, the empty sum
    is 0 and $s=0$. Maintenance: the pass adds $a_i$, so $s=a_0+\dots+a_i$, the invariant for $i+1$. Termination:
    after $n$ passes, the invariant for $i=n$ says $s$ is the sum of the whole list. (Here starting from 0 is right,
    because the empty sum really is 0; compare question 2.)

??? question "8. Prove that if a ≥ b > 0 then a mod b < a/2. Deduce that Euclid's algorithm makes at most about 2 log2 a passes."

    Two cases. If $b\le a/2$, then $a\bmod b<b\le a/2$. If $b>a/2$, then $a$ divided by $b$ has quotient 1 (since
    $2b>a$), so $a\bmod b=a-b<a-a/2=a/2$. Either way the remainder is less than $a/2$.

    In the algorithm, after the first pass we always have $a\ge b$. Two passes turn $(a,b)$ into $(b,r)$ and then into
    $(r,\dots)$ with $r=a\bmod b<a/2$. So every two passes the first number at least halves. A whole number $\ge1$ can
    be halved at most $\log_2 a$ times before reaching 1, so there are at most about $2\log_2 a$ passes (plus one or
    two at the ends). For 300-digit numbers ($a<10^{300}$, so $\log_2 a<997$), that is under about 2000 passes.

??? question "9. A computer does 10^9 steps per second. What is the largest n for which an algorithm of n^2 steps finishes in one second? And one of 2^n steps?"

    $n^2\le10^9$ gives $n\le\sqrt{10^9}\approx31{,}622$. For $2^n\le10^9$: $2^{29}=536{,}870{,}912$ and
    $2^{30}=1{,}073{,}741{,}824$, so $n=29$. A computer a thousand times faster raises the first limit to about a
    million, but the second only to $n=39$, because $2^{10}\approx1000$. Exponential algorithms barely benefit from
    faster machines.

??? question "10. Write a Turing machine table that flips every bit of a binary string (0 to 1 and 1 to 0) and halts at the end."

    One working state `flip` and a halting state `done`:

    | state, read | write | move | next |
    |---|---|---|---|
    | flip, 0 | 1 | R | flip |
    | flip, 1 | 0 | R | flip |
    | flip, _ | _ | L | done |

    In the chapter's simulator, use `run(FLIP, "1011", state="flip")` with these entries in a dict `FLIP`; it returns
    `0100` after 5 steps (one per digit plus one for the blank).

??? question "11. Show that the problem 'does program P halt when given the empty input?' is undecidable, by a reduction from the halting problem."

    Suppose `halts_empty(Q)` decided it. Given any $P$ and $x$, build the text of a program $Q$ that ignores its own
    input and runs $P$ on the fixed input $x$ (the text of $x$ is written into $Q$). Then $Q$ halts on the empty input
    exactly when $P$ halts on $x$. So `halts_empty(Q)` would answer the halting problem for $(P,x)$, which is
    impossible. Building $Q$ from $P$ and $x$ is a simple text operation, so the only impossible part is
    `halts_empty`.

??? question "12. Why does the halting-problem proof not also show that FIND-MAX's termination cannot be proved?"

    The theorem says no *single* algorithm decides halting for *every* program and input. It says nothing against
    proving that one particular program halts on all inputs, and for FIND-MAX we did: the loop runs exactly $n-1$
    times. Most programs people write for real have simple termination arguments like this one (a count that goes up
    to a bound, or a whole number that goes down), which is why practical termination checkers succeed often, while
    still having to answer "unknown" for some programs.

## What you learned

- An algorithm is a finite, definite, effective procedure from input to output; a problem is a rule saying which
  output each input needs, and an algorithm must work on every instance.
- A specification is a precondition plus a postcondition; correct means "always stops, and the output meets the
  postcondition on every valid input".
- Tests can find bugs but never prove their absence; a loop invariant (initialization, maintenance, termination)
  proves a loop correct for every input.
- The RAM model counts unit-cost steps (arithmetic, comparison, load, store, jump) on words of bounded size; random
  access means `a[i]` costs the same for every $i$.
- Counting steps shows that the growth with $n$ matters far more than the speed of the machine: $n^2$ steps on a
  billion items take decades.
- Euclid's algorithm computes gcds by $\gcd(a,b)=\gcd(b,a\bmod b)$, in a number of passes that grows with the number of
  digits, not with the size of the numbers.
- Turing machines define computation precisely, and the halting problem, proved undecidable by a diagonal argument,
  shows that some clearly stated problems have no algorithm at all.

**Next:** [Chapter 2](02-Measuring-Cost.md), the precise language of growth: Big-O, Big-Omega and Big-Theta, worst and
average case, and how to time code honestly.

## Further reading

- D. E. Knuth, *The Art of Computer Programming, Volume 1: Fundamental Algorithms*, 3rd ed., 1997. Section 1.1 is the
  classic discussion of what an algorithm is, starting from Euclid's algorithm.
- T. H. Cormen, C. E. Leiserson, R. L. Rivest and C. Stein, *Introduction to Algorithms*, 4th ed., 2022. Chapters 1
  and 2 (loop invariants, insertion sort, the RAM model).
- R. W. Floyd, "Assigning Meanings to Programs", *Mathematical Aspects of Computer Science*, 1967; C. A. R. Hoare, "An
  Axiomatic Basis for Computer Programming", *Communications of the ACM*, 1969.
- E. W. Dijkstra, *Notes on Structured Programming*, 1970 (later in Dahl, Dijkstra and Hoare, *Structured Programming*,
  1972).
- S. A. Cook and R. A. Reckhow, "Time Bounded Random Access Machines", *Journal of Computer and System Sciences*, 1973.
- A. M. Turing, "On Computable Numbers, with an Application to the Entscheidungsproblem", *Proceedings of the London
  Mathematical Society*, 1936.
- M. Sipser, *Introduction to the Theory of Computation*, 3rd ed., 2012: Turing machines, decidability and reductions
  in full.
- On this site: [Big-O](../../foundations/big-o.md), [Euclid's GCD](../../number-theory/gcd.md),
  [insertion sort](../../sorting/insertion-sort.md), and the [book's contents](index.md). For practice with proofs:
  [math.akadian.ca/books](https://math.akadian.ca/books/).
