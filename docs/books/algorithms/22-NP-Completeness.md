# 22. P, NP and NP-completeness

*For most problems in this book we found an algorithm whose running time is a small polynomial in the input size:
sorting in $O(n\log n)$, shortest paths in $O(m\log n)$, maximum flow in polynomial time. For some problems we never
did. Finding a shortest route through all of a set of cities, packing a knapsack exactly, satisfying a logical
formula: Chapters 13 and 14 solved them only in exponential time. Is that our fault, or the problems'? Nobody knows.
But we know something almost as useful: thousands of these problems are **equally hard**, in a precise sense, so a
fast algorithm for any one of them would give a fast algorithm for all. This chapter defines the classes P and NP,
builds the tool that compares problems (the polynomial-time reduction), explains the Cook-Levin theorem that started
the theory, proves a chain of reductions by hand and in code, and ends with what to do when your problem turns out
to be NP-hard.*

!!! abstract "In this chapter"
    **You will learn:**

    - what a decision problem is, how input size is measured, and why "polynomial time" is the line between easy and hard
    - the classes P and NP, defined by certificates and verifiers, and why P is inside NP
    - polynomial-time reductions, NP-hardness and NP-completeness, and the direction a reduction must go
    - the idea of the Cook-Levin theorem: why every problem in NP reduces to satisfiability
    - full proofs of SAT to 3-SAT, 3-SAT to independent set, vertex cover and clique, 3-SAT to subset sum, and 3-SAT to Hamiltonian cycle
    - Karp's 21 problems, co-NP and PSPACE, and the honest state of P versus NP
    - the practical options when a problem is NP-hard

    **You need:** [Chapter 2](02-Measuring-Cost.md) (big-O and growth), [Chapter 13](13-Dynamic-Programming.md)
    (knapsack and Held-Karp), [Chapter 14](14-Backtracking-and-Branch-and-Bound.md) (exhaustive search),
    [Chapter 15](15-Graphs-and-Graph-Search.md) (graphs), and the Turing machines of
    [Chapter 1](01-What-Is-an-Algorithm.md), 1.8, for 22.4.

    **Levels:** 22.1 to 22.3 are intermediate; 22.4 and 22.5 are advanced; 22.6 is advanced to expert; 22.7 is
    intermediate.

## 22.1 Easy and hard problems

Look at these pairs. In each, the two problems sound almost the same.

| easy (polynomial algorithm known) | hard (no polynomial algorithm known) |
|---|---|
| shortest simple path between two vertices (Chapter 16) | longest simple path between two vertices |
| a tour using every **edge** once: Euler tour (Chapter 15) | a tour visiting every **vertex** once: Hamiltonian cycle |
| minimum spanning tree (Chapter 17) | cheapest tree connecting a chosen subset of vertices (Steiner tree) |
| 2-SAT: formulas with two literals per clause | 3-SAT: three literals per clause |
| maximum matching in a graph (Chapter 17) | maximum independent set in a graph |
| is $n$ prime? (in P since 2002) | what are the prime factors of $n$? (status unknown) |

Euler showed in 1736 that a connected graph has a closed walk using every edge exactly once if and only if every
vertex has even degree, which is checked in linear time. For the vertex version, the **Hamiltonian cycle** problem
(named after William Rowan Hamilton, who invented a puzzle based on it in 1857), nobody has found anything fundamentally
better than trying exponentially many possibilities. Why should one letter, "edge" against "vertex", make such a
difference? The theory of NP-completeness does not answer that question, but it explains why the hard column all
stands or falls together.

### Decision problems

To compare problems we first put them in one shape. A **decision problem** is a question with a yes-or-no answer
about an input. Each concrete input is an **instance**. For example:

- HAMILTONIAN CYCLE: given a graph $G$, does $G$ have a cycle through every vertex exactly once?
- SUBSET SUM: given positive integers $a_1, \dots, a_n$ and a target $T$, is there a subset adding up to exactly $T$?
- CLIQUE: given a graph $G$ and a number $k$, does $G$ contain $k$ vertices that are all joined to each other?

Optimization problems ("find the largest clique", "find the shortest tour") have decision versions ("is there a
clique of size at least $k$?", "is there a tour of length at most $L$?"). Little is lost. If you can answer the
decision question, you can find the optimum value by **binary search** on $k$ or $L$, which costs only a logarithmic
number of questions, and usually you can then find an optimal solution itself (22.2 shows how for SAT). Conversely,
solving the optimization problem answers the decision question at once. So "the decision version is hard" means
"the optimization version is hard".

### Input size and polynomial time

The running time of an algorithm is measured as a function of the **size** of the instance: the number of bits
needed to write it down in a reasonable **encoding**. A graph with $n$ vertices and $m$ edges takes about
$(n + m)\log n$ bits as an adjacency list; a list of $n$ integers each below $2^b$ takes about $nb$ bits. An
algorithm runs in **polynomial time** if on instances of size $s$ it takes at most $c\,s^d$ steps for some constants
$c$ and $d$.

**Definition.** **P** is the class of decision problems that can be solved by an algorithm running in polynomial
time.

The encoding matters in one important way: **numbers must be written in binary** (or any base at least 2), not in
unary. The knapsack DP of [Chapter 13](13-Dynamic-Programming.md) runs in $O(nW)$ time, where $W$ is the capacity.
That looks polynomial, but $W$ takes only $\log_2 W$ bits to write, so $nW$ can be exponential in the input size:
with 100 items and $W = 2^{60}$ the input is a few thousand bits and the table has $100 \cdot 2^{60}$ cells. An
algorithm that is polynomial in the input's *numeric values* rather than its *length* is called
**pseudo-polynomial**. Other reasonable encodings (adjacency matrix against list, decimal against binary) change the
size only polynomially, so they do not change membership in P.

### Why polynomial?

Why draw the line at polynomials, when an $n^{100}$ algorithm is useless and a $1.0001^n$ one is fine for every
practical $n$? Three honest reasons.

1. **Closure.** Polynomials are closed under addition, multiplication and composition. A polynomial-time algorithm
   that calls a polynomial-time subroutine polynomially many times is still polynomial. So P does not depend on
   details: the machine model (a RAM, a Turing machine) and the encoding change running times only polynomially.
2. **Experience.** Problems that were shown to be in P have, again and again, soon had algorithms with small
   exponents. Exponential algorithms, by contrast, usually reflect brute force over a search space, and brute force
   doubles its cost every time the input grows by a constant.
3. **Scaling.** With a polynomial algorithm, a computer twice as fast solves larger instances by a constant
   *factor*; with a $2^n$ algorithm only by a constant *amount* (one more item).

The idea that "efficient" should mean "polynomial" was argued in 1965 by Alan Cobham ("The Intrinsic Computational
Difficulty of Functions") and by Jack Edmonds ("Paths, Trees, and Flowers", which gave a polynomial algorithm for
maximum matching in general graphs and called such algorithms "good"). It is now called the Cobham-Edmonds thesis.
It is a convention, not a theorem, and both its authors said so.

## 22.2 P and NP via certificates

What do the hard problems have in common? Not that they are hard to *solve*, but that they are easy to *check*.
If someone hands you a cycle and claims it is Hamiltonian, you can check the claim in linear time: is every vertex
on it exactly once, and is every consecutive pair an edge? If someone hands you a subset and claims it adds up to
$T$, you add it up. If they hand you an assignment of true and false to the variables of a formula, you evaluate
the formula. Finding the cycle, subset or assignment may take exponential time; recognising one is easy.

**Definition.** A decision problem $A$ is in **NP** if there is a polynomial-time algorithm $V$, the **verifier**,
and a polynomial $p$ such that for every instance $x$:

- if $x$ is a yes-instance, there is a string $c$ with $|c| \le p(|x|)$ such that $V(x, c)$ accepts;
- if $x$ is a no-instance, $V(x, c)$ rejects for every $c$.

The string $c$ is a **certificate** (or witness, or proof) for $x$. Read the definition as a game: a prover with
unlimited time tries to convince a verifier with polynomial time that the answer is yes. For yes-instances some
short certificate convinces the verifier; for no-instances nothing fools it. The asymmetry matters: NP is about
convincing someone that the answer is **yes**.

Examples, with their certificates:

| problem | certificate | verification |
|---|---|---|
| SAT: is a Boolean formula satisfiable? | an assignment of true/false to the variables | evaluate every clause: linear time |
| HAMILTONIAN CYCLE | the cycle, as an order of the vertices | $n$ adjacency checks |
| SUBSET SUM | the subset | one addition per number |
| CLIQUE | the $k$ vertices | $\binom{k}{2}$ adjacency checks |
| 3-COLOURING: can the vertices get 3 colours with every edge two-coloured? | the colouring | one check per edge |
| COMPOSITE: is $n$ not prime? | a factor $d$ with $1 < d < n$ | one division |

A **Boolean formula** is built from variables $x_1, \dots, x_n$ that are true or false using AND ($\wedge$), OR
($\vee$) and NOT ($\neg$). A **literal** is a variable or its negation. A **clause** is an OR of literals, and a
formula in **conjunctive normal form (CNF)** is an AND of clauses, such as
$(x_1 \vee \neg x_2 \vee x_3) \wedge (\neg x_1 \vee x_2) \wedge (\neg x_1 \vee \neg x_4)$. SAT asks whether some
assignment makes the formula true; from now on "SAT" means CNF satisfiability.

**The name.** NP stands for **nondeterministic polynomial time**. The original definition used a
*nondeterministic* Turing machine, which at each step may branch into several possible next steps and accepts if
*some* branch accepts. The two definitions are equivalent: a nondeterministic machine can guess a certificate one
bit per step and then run the verifier; conversely, the sequence of choices of an accepting branch is a
certificate, checked by re-running that branch. "NP" does **not** mean "not polynomial".

**Theorem.** $\mathrm{P} \subseteq \mathrm{NP} \subseteq \mathrm{EXP}$, where EXP is the class of problems solvable
in time $2^{p(n)}$ for some polynomial $p$.

*Proof.* If $A \in \mathrm{P}$, let the verifier ignore the certificate and solve the instance itself: certificates
are not needed. If $A \in \mathrm{NP}$ with verifier $V$ and bound $p$, try every string $c$ of length at most
$p(|x|)$ (there are fewer than $2^{p(|x|)+1}$) and run $V(x, c)$ on each, accepting if any is accepted; this takes
$2^{p(|x|)+1}$ times a polynomial, which is within $2^{q(|x|)}$ for a polynomial $q$. $\square$

The famous question is whether the first inclusion is an equality: **is P = NP?** If it were, every problem whose
solutions can be checked quickly could also be solved quickly. Most researchers believe $\mathrm{P} \ne \mathrm{NP}$,
but there is no proof either way. It is one of the seven Millennium Prize Problems announced by the Clay Mathematics
Institute in 2000. Remarkably, the question was put, in different words, in a 1956 letter from Kurt Gödel to John von
Neumann that was found decades later: Gödel asked how fast the time to find proofs of a given length must grow, and
noted what it would mean if it grew only linearly or quadratically.

### Code: verifiers, and search from decision

The program below writes the verifiers from the table, then shows a gap between checking and finding: it hides a
Hamiltonian cycle in a 9-vertex graph, checks the certificate with 9 lookups, and lets brute force search for it.

It also proves by example a useful fact: **for SAT, search is no harder than decision.** Suppose a box answers "is
this formula satisfiable?". Ask it about $F$; if yes, set $x_1$ to true, simplify, and ask again. If the answer is
still yes keep $x_1$ true, otherwise $x_1$ must be false in every satisfying assignment that agrees with the choices
so far. Repeat for $x_2, \dots, x_n$: at most $n+1$ questions find a satisfying assignment. This property, called
**self-reducibility**, holds for all the NP-complete problems of this chapter, which is why the theory can work with
decision problems only.

```python
--8<-- "books/algorithms/ch22_verifiers.py"
```

```
Verifying is fast, finding may not be:
  formula [[1, -2, 3], [-1, 2], [2, 3, -4], [-3, 4], [-1, -4]]
  certificate {1: False, 2: False, 3: True, 4: True} -> verifier says True
  a wrong certificate {1: True, 2: True, 3: True, 4: True} -> False

  Hamiltonian cycle, n = 9, m = 11: the certificate checks in 9 edge lookups (True); brute force tried 11108 of 40320 orders
  subset sum [267, 493, 869, 961, 1000, 1153, 1246, 1598, 1766, 1922], target 5842: certificate [869, 961, 1000, 1246, 1766], verified True
  clique {0,1,2} in a triangle plus a tail: True

Search from decision: find a satisfying assignment with at most n + 1 calls to a yes/no oracle
  found {1: True, 2: True, 3: False, 4: False}, valid True, oracle calls 4
  [[1, 2], [1, -2], [-1, 2], [-1, -2]]: None after 1 call
```

The formula is written as a list of clauses, each a list of integers: `3` means $x_3$ and `-3` means $\neg x_3$
(the format used by real SAT solvers). With 9 vertices brute force needed 11,108 orders; with 30 vertices the
number of orders is $29! \approx 8.8 \times 10^{30}$, while the certificate still checks in 30 lookups.

## 22.3 Reductions, NP-hard and NP-complete

How do you compare the difficulty of two problems without knowing how hard either one is? You show that one can
be **translated** into the other.

**Definition.** A **polynomial-time reduction** from problem $A$ to problem $B$, written $A \le_p B$, is an
algorithm $f$ running in polynomial time that turns every instance $x$ of $A$ into an instance $f(x)$ of $B$ such that

$$
x \text{ is a yes-instance of } A \iff f(x) \text{ is a yes-instance of } B .
$$

Read $A \le_p B$ as "$A$ is no harder than $B$": a fast algorithm for $B$ gives one for $A$ (translate, then solve).
Both directions of the "if and only if" must be proved, every time. These are called **Karp reductions** or
**many-one reductions**. A weaker kind, **Cook reductions** (or Turing reductions), allows solving $A$ with
polynomially many calls to an algorithm for $B$, as in the self-reduction above; for NP-completeness the stricter
Karp form is standard.

**A first example.** An **independent set** in a graph is a set of vertices no two of which are joined by an edge.
A **vertex cover** is a set of vertices that touches every edge.

**Lemma.** $S$ is an independent set of $G = (V, E)$ if and only if $V \setminus S$ is a vertex cover.

*Proof.* $S$ is independent $\iff$ no edge has both ends in $S$ $\iff$ every edge has an end outside $S$ $\iff$
$V \setminus S$ covers every edge. $\square$

So "does $G$ have an independent set of size $k$?" has the same answer as "does $G$ have a vertex cover of size
$n - k$?". The map $(G, k) \mapsto (G, n-k)$ is a reduction INDEPENDENT SET $\le_p$ VERTEX COVER, and the same map is
also a reduction back. Similarly $S$ is independent in $G$ if and only if $S$ is a clique in the **complement graph**
$\bar G$ (same vertices, an edge exactly where $G$ has none), so $(G, k) \mapsto (\bar G, k)$ reduces INDEPENDENT SET
to CLIQUE and back; building $\bar G$ takes $O(n^2)$ time.

**Lemma (transitivity).** If $A \le_p B$ and $B \le_p C$ then $A \le_p C$.

*Proof.* Compose the two maps: $x \mapsto g(f(x))$. If $f$ runs in time $p(n)$, its output has size at most $p(n)$,
so $g$ runs in time $q(p(n))$, a polynomial. The equivalences chain. $\square$

**Definitions.** A problem $B$ is **NP-hard** if $A \le_p B$ for *every* $A \in \mathrm{NP}$. It is
**NP-complete** if it is NP-hard and also in NP. The NP-complete problems are the hardest problems in NP.

**Theorem.** Let $B$ be NP-complete.

1. If $B \in \mathrm{P}$, then $\mathrm{P} = \mathrm{NP}$.
2. If $B \le_p C$ and $C \in \mathrm{NP}$, then $C$ is NP-complete.

*Proof.* (1) Any $A \in \mathrm{NP}$ reduces to $B$; translate in polynomial time, then run $B$'s polynomial
algorithm. (2) Any $A \in \mathrm{NP}$ has $A \le_p B \le_p C$, so $A \le_p C$ by transitivity; and $C$ is in NP by
assumption. $\square$

Part 2 is how almost every NP-completeness proof goes: to show a new problem $C$ is NP-complete, (a) show $C \in$ NP
by giving a certificate, and (b) reduce a **known** NP-complete problem **to** $C$. The direction is the most common
mistake. Reducing $C$ to SAT (writing $C$ as a formula) shows only that $C$ is no harder than SAT, which is true of
everything in NP, including sorting. To show $C$ is hard you must show that SAT, or another hard problem, can be
disguised as an instance of $C$.

<figure class="mars-fig" markdown="0">
<svg viewBox="0 0 640 330" role="img" aria-label="The classes as most researchers believe them to be: a large PSPACE box contains NP and co-NP as two overlapping ovals. P sits in their intersection. NP-complete problems form a band at the far edge of NP, co-NP-complete problems at the far edge of co-NP. NP-hard extends beyond NP.">
  <rect x="10" y="10" width="620" height="290" rx="14" fill="none" stroke="currentColor" stroke-width="1.4"/>
  <text x="30" y="36" font-size="14" fill="currentColor">PSPACE (games, quantified formulas)</text>
  <ellipse cx="250" cy="170" rx="190" ry="105" fill="#9cc9ea" fill-opacity="0.25" stroke="currentColor" stroke-width="1.4"/>
  <ellipse cx="390" cy="170" rx="190" ry="105" fill="#7ccf9a" fill-opacity="0.2" stroke="currentColor" stroke-width="1.4"/>
  <ellipse cx="320" cy="170" rx="55" ry="40" fill="#eea66f" fill-opacity="0.55" stroke="currentColor" stroke-width="1.4"/>
  <g font-size="13" text-anchor="middle" fill="currentColor">
    <text x="320" y="166">P</text>
    <text x="320" y="184" font-size="11">sorting, paths, flow</text>
    <text x="165" y="110">NP</text>
    <text x="475" y="110">co-NP</text>
    <text x="320" y="226" font-size="11">factoring (decision)?</text>
    <text x="320" y="240" font-size="11">graph isomorphism?</text>
    <text x="125" y="165" font-size="12">NP-complete:</text>
    <text x="125" y="181" font-size="11">SAT, clique,</text>
    <text x="125" y="195" font-size="11">Ham. cycle</text>
    <text x="515" y="165" font-size="12">co-NP-complete:</text>
    <text x="515" y="181" font-size="11">tautology,</text>
    <text x="515" y="195" font-size="11">no Ham. cycle</text>
  </g>
  <path d="M 95 120 Q 68 170 95 220" fill="none" stroke="#eea66f" stroke-width="5"/>
  <path d="M 545 120 Q 572 170 545 220" fill="none" stroke="#eea66f" stroke-width="5"/>
  <text x="320" y="322" font-size="12" text-anchor="middle" fill="currentColor">drawn assuming P ≠ NP ≠ co-NP; if P = NP, the three inner regions collapse into one</text>
</svg>
<figcaption>Figure 22.1. The classes of this chapter as most researchers believe them to be. None of the inclusions drawn as strict has been proved strict. Problems marked "?" are in NP and co-NP but not known to be in P or NP-complete.</figcaption>
</figure>

Note that NP-hard problems need not be in NP at all. The **halting problem** of [Chapter 1](01-What-Is-an-Algorithm.md)
is NP-hard (any NP problem reduces to it: map $x$ to a program that tries every certificate for $x$, halts if one is accepted,
and otherwise loops forever)
but it is not even decidable.

## 22.4 The Cook-Levin theorem

*Level: advanced.* Part 2 of the theorem above needs a *first* NP-complete problem to start the chain. That is what
Stephen Cook proved in 1971, in "The Complexity of Theorem-Proving Procedures" (STOC 1971), and Leonid Levin proved
independently in the Soviet Union in "Universal Sequential Search Problems" (1973, in Russian, *Problemy Peredachi
Informatsii*).

**Theorem (Cook 1971, Levin 1973).** SAT is NP-complete.

SAT is in NP (the assignment is the certificate). The content of the theorem is that **every** problem in NP
reduces to SAT, including problems nobody has thought of yet. So the proof cannot use anything about a particular
problem. It uses only the definition: a problem $A$ in NP has a polynomial-time verifier $V$. Given an instance $x$,
we must build, in polynomial time, a formula $F_x$ that is satisfiable exactly when some certificate $c$ makes
$V(x, c)$ accept. The idea fits in one sentence:

> **Make the certificate's bits into Boolean variables, and write "the verifier, run on $x$ and these bits,
> accepts" as a formula.**

### Step 1: a computation is a table

Run $V$ on $(x, c)$ as a Turing machine (Chapter 1, 1.8). It halts within $T = p(|x|)$ steps for a polynomial $p$,
so it uses at most $T$ tape cells. Write the whole computation as a **tableau**: a $T \times T$ grid whose row $t$ is
the machine's configuration at time $t$, that is, the tape contents, with the head position and the machine's state
recorded in the cell under the head. Row 0 holds $x$, then the certificate cells, then blanks.

### Step 2: the table is described by variables

Introduce a Boolean variable $y_{t,i,\sigma}$ for each time $t$, cell $i$ and symbol $\sigma$ (a symbol is a tape
letter, or a letter combined with a state when the head is there), meaning "at time $t$, cell $i$ holds $\sigma$".
There are $O(T^2)$ variables, since the set of symbols is a fixed finite set that depends only on $V$.

### Step 3: the rules are clauses

Four groups of clauses say that the variables describe an accepting computation.

1. **Each cell holds exactly one symbol:** for each $(t, i)$, one clause "some $\sigma$" and, for each pair
   $\sigma \ne \tau$, a clause $\neg y_{t,i,\sigma} \vee \neg y_{t,i,\tau}$.
2. **The first row is the start:** unit clauses fixing the cells of $x$, the start state and the blanks. The
   certificate cells are **left free**: they may hold 0 or 1. This is where the existential "there is a $c$" goes.
3. **Each row follows from the one above by the machine's rules.** The key fact: a Turing machine changes only the
   cell under its head and moves one step, so whether row $t+1$ is correct can be checked by looking at every
   $2 \times 3$ **window** (cells $i-1$, $i$, $i+1$ in rows $t$ and $t+1$). The legal windows form a finite list
   that depends only on $V$'s transition table. For each window position, a constant-size CNF says "this window is
   one of the legal ones".
4. **The machine accepts:** a clause saying some cell of the last row holds the accepting state.

### Step 4: count and check

There are $O(T^2)$ cells and windows, each contributing a constant number of clauses of constant size, so $F_x$ has
size $O(T^2) = O(p(|x|)^2)$ and can be written out in polynomial time. If some certificate makes $V$ accept, setting
the variables from the real computation satisfies every clause. If an assignment satisfies every clause, groups 1
and 3 force the rows to be a legal computation of $V$ (by induction on $t$), group 2 forces it to start on $x$ and
*some* certificate (read it off the free cells), and group 4 forces it to accept. So $F_x$ is satisfiable if and
only if $x$ is a yes-instance. $\square$

That is the proof's skeleton. The full details (the window lemma, the exact encoding of states) take a few pages;
they are written out in Sipser's *Introduction to the Theory of Computation* (section 7.4) and in CLRS, which goes
through circuits instead: every polynomial-time verifier can be turned into a polynomial-size **Boolean circuit**,
so CIRCUIT-SAT is NP-complete, and then CIRCUIT-SAT reduces to SAT gate by gate.

### The idea in miniature

The gate-by-gate step is short enough to code. A circuit is a network of AND, OR and NOT gates. Give every gate
output its own new variable $g$ and write three or two clauses saying "$g$ equals this gate applied to its inputs":

$$
g \leftrightarrow (a \wedge b): \ (\neg g \vee a)(\neg g \vee b)(g \vee \neg a \vee \neg b), \qquad g \leftrightarrow (a \vee b): \ (g \vee \neg a)(g \vee \neg b)(\neg g \vee a \vee b), \qquad g \leftrightarrow \neg a: \ (g \vee a)(\neg g \vee \neg a).
$$

Add the unit clause "the output is true". The CNF is satisfiable exactly when some input makes the circuit output
true, and its size is linear in the circuit's. This is **Tseitin's encoding** (G. S. Tseitin, 1968), used by every
modern tool that hands problems to SAT solvers. The program checks it on all inputs of a small circuit, then encodes
"this graph is 3-colourable" the same way, with variables for the certificate (vertex $v$ gets colour $c$) and
clauses for the verifier's checks, and solves both with a small DPLL solver (Davis, Putnam, Logemann and Loveland,
1960-62: set forced literals, otherwise branch).

```python
--8<-- "books/algorithms/ch22_cook_levin.py"
```

```
Circuit out = (x1 AND x2) OR (NOT x3), as 8 clauses: [[-4, 1], [-4, 2], [4, -1, -2], [5, 3], [-5, -3], [6, -4], [6, -5], [-6, 4, 5]]
  inputs  circuit  CNF with out forced true is satisfiable
  000     1        True
  001     0        False
  010     1        True
  011     0        False
  100     1        True
  101     0        False
  110     1        True
  111     1        True

Petersen graph: 30 variables, 85 clauses; satisfiable
  colours: [0, 1, 0, 1, 2, 1, 0, 2, 2, 1]  proper: True

complete graph K4: 12 variables, 34 clauses; unsatisfiable
```

The 3-colouring encoding has 85 clauses for the Petersen graph: 10 "some colour" clauses, $10 \times 3$ "at most one
colour" clauses and $15 \times 3$ "ends differ" clauses. It is a reduction 3-COLOURING $\le_p$ SAT, which (by the
warning in 22.3) says nothing about 3-colouring being hard. Showing that 3-colouring *is* NP-complete needs a
reduction in the other direction, from 3-SAT (Exercise 11).

## 22.5 A chain of reductions, proved

*Level: advanced.* With SAT known to be NP-complete, each new problem needs only one reduction from a problem
already on the list. Here is the chain this section builds; every arrow is a polynomial-time reduction, proved
below, so every problem in the picture is NP-complete (each is in NP by the certificates of 22.2).

<figure class="mars-fig" markdown="0">
<svg viewBox="0 0 660 300" role="img" aria-label="A tree of reductions. Every problem in NP reduces to circuit SAT and SAT by Cook-Levin. SAT reduces to 3-SAT. 3-SAT reduces to independent set, to subset sum and to directed Hamiltonian cycle. Independent set reduces to vertex cover and clique. Directed Hamiltonian cycle reduces to undirected Hamiltonian cycle, which reduces to the travelling salesman problem.">
  <defs>
    <marker id="ar22" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
      <path d="M 0 0 L 10 5 L 0 10 z" fill="currentColor"/>
    </marker>
  </defs>
  <g stroke="currentColor" stroke-width="1.4" fill="none" marker-end="url(#ar22)">
    <line x1="330" y1="46" x2="330" y2="72"/>
    <line x1="330" y1="106" x2="330" y2="132"/>
    <line x1="300" y1="166" x2="140" y2="196"/>
    <line x1="330" y1="166" x2="330" y2="196"/>
    <line x1="360" y1="166" x2="520" y2="196"/>
    <line x1="110" y1="230" x2="70" y2="256"/>
    <line x1="140" y1="230" x2="190" y2="256"/>
    <line x1="520" y1="230" x2="520" y2="256"/>
    <line x1="580" y1="273" x2="590" y2="273"/>
  </g>
  <g font-size="13" text-anchor="middle" fill="currentColor">
    <rect x="200" y="14" width="260" height="32" rx="6" fill="#eea66f" fill-opacity="0.35" stroke="currentColor"/>
    <text x="330" y="35">every problem in NP</text>
    <rect x="230" y="74" width="200" height="32" rx="6" fill="#eea66f" fill-opacity="0.6" stroke="currentColor"/>
    <text x="330" y="95">SAT (Cook-Levin, 22.4)</text>
    <rect x="270" y="134" width="120" height="32" rx="6" fill="#9cc9ea" fill-opacity="0.5" stroke="currentColor"/>
    <text x="330" y="155">3-SAT</text>
    <rect x="60" y="198" width="140" height="32" rx="6" fill="#9cc9ea" fill-opacity="0.5" stroke="currentColor"/>
    <text x="130" y="219">independent set</text>
    <rect x="270" y="198" width="120" height="32" rx="6" fill="#9cc9ea" fill-opacity="0.5" stroke="currentColor"/>
    <text x="330" y="219">subset sum</text>
    <rect x="430" y="198" width="180" height="32" rx="6" fill="#9cc9ea" fill-opacity="0.5" stroke="currentColor"/>
    <text x="520" y="219">directed Ham. cycle</text>
    <rect x="10" y="258" width="120" height="32" rx="6" fill="#7ccf9a" fill-opacity="0.5" stroke="currentColor"/>
    <text x="70" y="279">vertex cover</text>
    <rect x="150" y="258" width="90" height="32" rx="6" fill="#7ccf9a" fill-opacity="0.5" stroke="currentColor"/>
    <text x="195" y="279">clique</text>
    <rect x="420" y="258" width="160" height="32" rx="6" fill="#7ccf9a" fill-opacity="0.5" stroke="currentColor"/>
    <text x="500" y="279">undirected Ham.</text>
    <rect x="592" y="258" width="58" height="32" rx="6" fill="#7ccf9a" fill-opacity="0.5" stroke="currentColor"/>
    <text x="621" y="279">TSP</text>
  </g>
</svg>
<figcaption>Figure 22.2. The reductions proved in this section. An arrow from A to B means A ≤p B: a fast algorithm for B would solve A. Hardness flows down the arrows.</figcaption>
</figure>

### SAT to 3-SAT

**3-SAT** is SAT restricted to formulas in which every clause has exactly three literals. It is the usual starting
point for reductions because its instances are so uniform.

**The construction.** Replace each clause $C$ of the formula by clauses of exactly three literals, using new
variables that appear nowhere else:

- $C = (\ell)$ becomes $(\ell \vee y \vee z)(\ell \vee y \vee \neg z)(\ell \vee \neg y \vee z)(\ell \vee \neg y \vee \neg z)$.
- $C = (\ell_1 \vee \ell_2)$ becomes $(\ell_1 \vee \ell_2 \vee y)(\ell_1 \vee \ell_2 \vee \neg y)$.
- A clause of three literals is kept.
- $C = (\ell_1 \vee \ell_2 \vee \dots \vee \ell_L)$ with $L \ge 4$ becomes the **chain**
  $(\ell_1 \vee \ell_2 \vee y_1)(\neg y_1 \vee \ell_3 \vee y_2)(\neg y_2 \vee \ell_4 \vee y_3)\cdots(\neg y_{L-3} \vee \ell_{L-1} \vee \ell_L)$.

**Claim.** Each group of new clauses is satisfiable together with a given assignment of the old variables if and
only if that assignment satisfies $C$. Since the new variables of different clauses are different, the whole new
formula is satisfiable if and only if the old one is.

*Proof.* For the short clauses: whatever $y$ and $z$ are, one of the padding clauses has all its new literals false,
so the group holds exactly when $\ell$ (or $\ell_1 \vee \ell_2$) is true. For the chain, read $y_i$ as "a true
literal is still to come after position $i+1$".

($\Rightarrow$) If $C$ is true, pick a true literal $\ell_r$. Set $y_i$ true for $i \le r-2$ and false for
$i \ge r-1$. The clause containing $\ell_r$ is satisfied by it; every clause to its left contains a positive $y_i$
with $i \le r-2$, which is true; every clause to its right contains a $\neg y_i$ with $i \ge r-1$, which is true.

($\Leftarrow$) If every $\ell_i$ is false, the first clause forces $y_1$ true, then the second forces $y_2$ true,
and so on: all $y_i$ are true, and the last clause $(\neg y_{L-3} \vee \ell_{L-1} \vee \ell_L)$ is false. So no
setting of the $y$'s works. $\square$

A clause of length $L$ becomes at most $\max(4, L-2)$ clauses, so the new formula is linear in the size of the old
one. Example: $(x_1 \vee \neg x_2 \vee x_3 \vee x_4 \vee \neg x_5)$ becomes
$(x_1 \vee \neg x_2 \vee y_1)(\neg y_1 \vee x_3 \vee y_2)(\neg y_2 \vee x_4 \vee \neg x_5)$.

Why stop at three? Because **2-SAT is in P**: a clause $(a \vee b)$ is the pair of implications
$\neg a \Rightarrow b$ and $\neg b \Rightarrow a$; the formula is unsatisfiable exactly when some variable $x$ and
$\neg x$ lie in the same strongly connected component of this implication graph, which
[Chapter 15](15-Graphs-and-Graph-Search.md) finds in linear time (Aspvall, Plass and Tarjan, 1979). The chain trick
cannot produce clauses of two literals, since each link needs a literal from the old clause plus two connectors.

### 3-SAT to independent set

**The construction.** Given a 3-CNF formula with $k$ clauses, build a graph with one vertex for each literal
occurrence ($3k$ vertices). Join the three vertices of each clause into a **triangle**. Join every vertex labelled
$x_i$ to every vertex labelled $\neg x_i$ (a **conflict edge**). Ask for an independent set of size $k$.

**Claim.** The formula is satisfiable if and only if the graph has an independent set of size $k$.

*Proof.* ($\Rightarrow$) Take a satisfying assignment and choose one true literal in each clause: $k$ vertices.
No two are in the same triangle (one per clause), and no conflict edge joins two of them, because $x_i$ and
$\neg x_i$ are never both true. So they are independent.

($\Leftarrow$) An independent set contains at most one vertex of each triangle, so one of size $k$ contains exactly
one per clause. It has no conflict edge, so it never contains both $x_i$ and $\neg x_i$. Make the chosen literals
true (any variable not mentioned can be set either way); this is a consistent assignment, and every clause has a
true literal. $\square$

The graph has $3k$ vertices and $O(k^2)$ edges, built in polynomial time. A worked example with
$F = (x_1 \vee x_2 \vee x_3)(\neg x_1 \vee \neg x_2 \vee x_3)(x_1 \vee \neg x_2 \vee \neg x_3)$:

<figure class="mars-fig" markdown="0">
<svg viewBox="0 0 640 290" role="img" aria-label="Three triangles, one per clause. Clause 1 has x1, x2, x3; clause 2 has not x1, not x2, x3; clause 3 has x1, not x2, not x3. Dashed conflict edges join x1 with not x1, x2 with not x2, x3 with not x3. The highlighted independent set is x1 in clause 1, not x2 in clause 2 and x1 in clause 3.">
  <g stroke="currentColor" stroke-width="1.6" fill="none">
    <polygon points="120,60 70,150 170,150"/>
    <polygon points="320,60 270,150 370,150"/>
    <polygon points="520,60 470,150 570,150"/>
  </g>
  <g stroke="currentColor" stroke-width="1.2" fill="none" stroke-dasharray="5 4">
    <line x1="138" y1="60" x2="302" y2="60"/>
    <line x1="338" y1="60" x2="502" y2="60"/>
    <path d="M 70 168 Q 170 235 270 168"/>
    <path d="M 70 168 Q 270 330 470 168"/>
    <path d="M 170 168 Q 370 300 570 168"/>
    <path d="M 370 168 Q 470 215 570 168"/>
  </g>
  <g font-size="12" text-anchor="middle" fill="currentColor">
    <circle cx="120" cy="60" r="18" fill="#eea66f" stroke="currentColor"/><text x="120" y="64">x1</text>
    <circle cx="70" cy="150" r="18" fill="#9cc9ea" stroke="currentColor"/><text x="70" y="154">x2</text>
    <circle cx="170" cy="150" r="18" fill="#9cc9ea" stroke="currentColor"/><text x="170" y="154">x3</text>
    <circle cx="320" cy="60" r="18" fill="#9cc9ea" stroke="currentColor"/><text x="320" y="64">¬x1</text>
    <circle cx="270" cy="150" r="18" fill="#eea66f" stroke="currentColor"/><text x="270" y="154">¬x2</text>
    <circle cx="370" cy="150" r="18" fill="#9cc9ea" stroke="currentColor"/><text x="370" y="154">x3</text>
    <circle cx="520" cy="60" r="18" fill="#eea66f" stroke="currentColor"/><text x="520" y="64">x1</text>
    <circle cx="470" cy="150" r="18" fill="#9cc9ea" stroke="currentColor"/><text x="470" y="154">¬x2</text>
    <circle cx="570" cy="150" r="18" fill="#9cc9ea" stroke="currentColor"/><text x="570" y="154">¬x3</text>
    <text x="120" y="28">clause 1</text><text x="320" y="28">clause 2</text><text x="520" y="28">clause 3</text>
    <text x="320" y="280">solid: triangle edges; dashed: conflict edges; orange: an independent set of size 3</text>
  </g>
</svg>
<figcaption>Figure 22.3. The 3-SAT to independent set gadget for a three-clause formula. The orange set corresponds to x1 = true, x2 = false (x3 is free); it picks one true literal per clause and never both x and ¬x.</figcaption>
</figure>

Combined with 22.3, **vertex cover** (via $(G, k) \mapsto (G, n-k)$) and **clique** (via the complement graph) are
NP-complete too.

### 3-SAT to subset sum

This reduction turns logic into arithmetic, and shows why numbers must be written in binary.

**The construction.** Let the formula have variables $x_1, \dots, x_n$ and clauses $C_1, \dots, C_k$, and assume no
clause contains both $x_i$ and $\neg x_i$ (such a clause is always true and can be dropped). Write numbers in
decimal with $n + k$ digits: one digit for each variable, then one for each clause.

- For each variable $x_i$, two numbers $v_i$ and $v'_i$. Both have a 1 in digit $x_i$. In addition, $v_i$ has a 1
  in digit $C_j$ for every clause containing $x_i$, and $v'_i$ has a 1 in digit $C_j$ for every clause containing
  $\neg x_i$. All other digits are 0.
- For each clause $C_j$, two **slack** numbers $s_j$ and $s'_j$, with 1 and 2 respectively in digit $C_j$, 0
  elsewhere.
- The target $T$ has 1 in every variable digit and 4 in every clause digit.

**Claim.** The formula is satisfiable if and only if some subset of these $2n + 2k$ numbers adds up to $T$.

*Proof.* First, **no carries**: in any digit, the numbers that have a nonzero entry there add to at most 6 (a
clause digit gets at most 3 from its literals and $1 + 2$ from its slacks; a variable digit gets 2). So a subset
sums to $T$ exactly when it matches $T$ digit by digit.

($\Rightarrow$) Given a satisfying assignment, take $v_i$ if $x_i$ is true and $v'_i$ if it is false. Every variable
digit is now 1. Each clause digit $C_j$ is the number of true literals in $C_j$, between 1 and 3. Add slacks to
reach 4: $s'_j$ and $s_j$ if it is 1, $s'_j$ if it is 2, $s_j$ if it is 3.

($\Leftarrow$) If a subset sums to $T$, each variable digit equals 1, so the subset contains exactly one of $v_i$,
$v'_i$: set $x_i$ true if it contains $v_i$. In digit $C_j$ the slacks contribute at most 3, so at least 1 comes
from the chosen $v$'s, which means some literal of $C_j$ is true. $\square$

The numbers have $n + k$ digits each, so the instance has size polynomial in the formula. Their *values* are
around $10^{n+k}$, which is why the $O(nT)$ dynamic program of Chapter 13 does not contradict the theorem: it is
pseudo-polynomial, exponential in the number of digits.

**Worked example**, with the formula of Figure 22.3 (digits $x_1 x_2 x_3 \mid C_1 C_2 C_3$):

| number | $x_1$ | $x_2$ | $x_3$ | $C_1$ | $C_2$ | $C_3$ | value |
|---|---|---|---|---|---|---|---|
| $v_1$ | 1 | 0 | 0 | 1 | 0 | 1 | 100101 |
| $v'_1$ | 1 | 0 | 0 | 0 | 1 | 0 | 100010 |
| $v_2$ | 0 | 1 | 0 | 1 | 0 | 0 | 010100 |
| $v'_2$ | 0 | 1 | 0 | 0 | 1 | 1 | 010011 |
| $v_3$ | 0 | 0 | 1 | 1 | 1 | 0 | 001110 |
| $v'_3$ | 0 | 0 | 1 | 0 | 0 | 1 | 001001 |
| slacks | | | | 1, 2 | 1, 2 | 1, 2 | 000100, 000200, ... |
| target $T$ | 1 | 1 | 1 | 4 | 4 | 4 | 111444 |

The assignment $x_1$ = true, $x_2$ = false, $x_3$ = true picks $v_1 + v'_2 + v_3 = 100101 + 010011 + 001110 = 111222$: each clause has exactly two true literals. Adding $s'_1 + s'_2 + s'_3 = 000222$ gives $111444 = T$.

### 3-SAT to Hamiltonian cycle

The last reduction builds a graph whose Hamiltonian cycles *are* truth assignments. This is the construction of
Kleinberg and Tardos (*Algorithm Design*, section 8.5); Karp's 1972 paper reached Hamiltonian cycle by a different
route, through vertex cover.

**The construction (directed).** Let the formula have variables $x_1, \dots, x_n$ and clauses $C_1, \dots, C_k$.

1. For each variable $x_i$ make a **row** of $b = 3k + 3$ vertices ("beads") $v_{i,0}, \dots, v_{i,b-1}$, with arcs
   in both directions between neighbouring beads. Crossing row $i$ left to right will mean $x_i$ = true; right to
   left, false.
2. Add a start vertex $s$ and an end vertex $t$. Add arcs from $s$ to both ends of row 1; from both ends of row $i$
   to both ends of row $i+1$; from both ends of row $n$ to $t$; and from $t$ back to $s$.
3. For each clause $C_j$ add one vertex $c_j$. Clause $j$ owns the pair of beads $(3j+2, 3j+3)$ in every row, for
   $j = 0, \dots, k-1$ (counting clauses from 0), so beads $0, 1$ at the left end, $3k+1, 3k+2$ at the right end and
   one bead between consecutive pairs touch no clause. If $x_i$ appears in $C_j$, add arcs
   $v_{i,3j+2} \to c_j \to v_{i,3j+3}$: a detour usable when crossing row $i$ left to right. If $\neg x_i$ appears in
   $C_j$, add $v_{i,3j+3} \to c_j \to v_{i,3j+2}$: usable when crossing right to left.

The graph has $n(3k+3) + k + 2$ vertices.

<figure class="mars-fig" markdown="0">
<svg viewBox="0 0 660 330" role="img" aria-label="Three rows of twelve beads, linked both ways. Arrows lead from s to both ends of row 1, from the ends of each row to both ends of the next, and from row 3 to t, with an arc from t back to s. A clause vertex C1 between rows 1 and 2 has a detour from row 1 going left to right and a detour from row 2 going right to left. Row 1 is labelled crossed left to right, x1 true; row 2 right to left, x2 false.">
  <defs>
    <marker id="ah22" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 0 L 10 5 L 0 10 z" fill="currentColor"/>
    </marker>
    <marker id="ao22" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 0 L 10 5 L 0 10 z" fill="#eea66f"/>
    </marker>
  </defs>
  <g stroke="currentColor" stroke-width="1.2" fill="none">
    <line x1="60" y1="80" x2="588" y2="80"/>
    <line x1="60" y1="160" x2="588" y2="160"/>
    <line x1="60" y1="240" x2="588" y2="240"/>
  </g>
  <g stroke="currentColor" stroke-width="1" fill="none" stroke-dasharray="4 4" marker-end="url(#ah22)">
    <line x1="322" y1="32" x2="66" y2="74"/>
    <line x1="338" y1="32" x2="582" y2="74"/>
    <line x1="60" y1="88" x2="60" y2="151"/>
    <line x1="588" y1="88" x2="588" y2="151"/>
    <line x1="66" y1="86" x2="580" y2="155"/>
    <line x1="582" y1="86" x2="68" y2="155"/>
    <line x1="60" y1="168" x2="60" y2="231"/>
    <line x1="588" y1="168" x2="588" y2="231"/>
    <line x1="66" y1="166" x2="580" y2="235"/>
    <line x1="582" y1="166" x2="68" y2="235"/>
    <line x1="66" y1="246" x2="320" y2="294"/>
    <line x1="582" y1="246" x2="340" y2="294"/>
    <path d="M 345 302 Q 900 165 345 26"/>
  </g>
  <g fill="#9cc9ea" stroke="currentColor" stroke-width="1">
    <circle cx="60" cy="80" r="7"/><circle cx="108" cy="80" r="7"/><circle cx="156" cy="80" r="7"/><circle cx="204" cy="80" r="7"/>
    <circle cx="252" cy="80" r="7"/><circle cx="300" cy="80" r="7"/><circle cx="348" cy="80" r="7"/><circle cx="396" cy="80" r="7"/>
    <circle cx="444" cy="80" r="7"/><circle cx="492" cy="80" r="7"/><circle cx="540" cy="80" r="7"/><circle cx="588" cy="80" r="7"/>
    <circle cx="60" cy="160" r="7"/><circle cx="108" cy="160" r="7"/><circle cx="156" cy="160" r="7"/><circle cx="204" cy="160" r="7"/>
    <circle cx="252" cy="160" r="7"/><circle cx="300" cy="160" r="7"/><circle cx="348" cy="160" r="7"/><circle cx="396" cy="160" r="7"/>
    <circle cx="444" cy="160" r="7"/><circle cx="492" cy="160" r="7"/><circle cx="540" cy="160" r="7"/><circle cx="588" cy="160" r="7"/>
    <circle cx="60" cy="240" r="7"/><circle cx="108" cy="240" r="7"/><circle cx="156" cy="240" r="7"/><circle cx="204" cy="240" r="7"/>
    <circle cx="252" cy="240" r="7"/><circle cx="300" cy="240" r="7"/><circle cx="348" cy="240" r="7"/><circle cx="396" cy="240" r="7"/>
    <circle cx="444" cy="240" r="7"/><circle cx="492" cy="240" r="7"/><circle cx="540" cy="240" r="7"/><circle cx="588" cy="240" r="7"/>
  </g>
  <g stroke="#eea66f" stroke-width="2.2" fill="none" marker-end="url(#ao22)">
    <line x1="160" y1="86" x2="172" y2="108"/>
    <line x1="188" y1="108" x2="200" y2="87"/>
    <line x1="200" y1="154" x2="188" y2="132"/>
    <line x1="172" y1="132" x2="160" y2="153"/>
  </g>
  <circle cx="180" cy="120" r="13" fill="#7ccf9a" stroke="currentColor"/>
  <g font-size="12" text-anchor="middle" fill="currentColor">
    <circle cx="330" cy="25" r="12" fill="#eea66f" fill-opacity="0.6" stroke="currentColor"/><text x="330" y="29">s</text>
    <circle cx="330" cy="302" r="12" fill="#eea66f" fill-opacity="0.6" stroke="currentColor"/><text x="330" y="306">t</text>
    <text x="180" y="124" font-size="11">C1</text>
    <text x="25" y="84">x1</text><text x="25" y="164">x2</text><text x="25" y="244">x3</text>
    <text x="420" y="66">x1 = true: cross left to right</text>
    <text x="420" y="146">x2 = false: cross right to left</text>
  </g>
</svg>
<figcaption>Figure 22.4. The Hamiltonian-cycle gadget with three variables and k = 3 (12 beads per row; links between beads go both ways). Only clause C1 = (x1 ∨ ¬x2 ∨ ...) is drawn: its detour from row 1 runs left to right, its detour from row 2 right to left, and its third literal adds a detour into row 3 in the same way.</figcaption>
</figure>

**Claim.** The formula is satisfiable if and only if the graph has a Hamiltonian cycle.

*Proof.* ($\Rightarrow$) Given a satisfying assignment, go from $s$ through rows $1, \dots, n$ in order, crossing
row $i$ left to right if $x_i$ is true and right to left if false, then to $t$ and back to $s$. This visits every
bead once. For each clause $C_j$ choose one true literal, say in row $i$, and on the way through row $i$ take the
detour through $c_j$ between beads $3j+2$ and $3j+3$; it points the right way precisely because the literal is
true. Each $c_j$ is visited once.

($\Leftarrow$) Take a Hamiltonian cycle. The key claim is: **if the cycle enters $c_j$ from a bead of row $i$, it
leaves $c_j$ to the neighbouring bead of the same row.** Suppose it enters from $v_{i,3j+2}$ (the case of a
positive literal; the negative case is the mirror image) but leaves to some other vertex. Recall that we excluded
clauses containing both $x_i$ and $\neg x_i$, so the only clause arcs at these two beads are
$v_{i,3j+2} \to c_j \to v_{i,3j+3}$. Where did the cycle come from just before $v_{i,3j+2}$? Its only possible
predecessors are its two neighbours in the row.

- *From $v_{i,3j+3}$.* Then look at the bead $v_{i,3j+1}$ on the other side. It touches no clause vertex (it is a
  free bead), so its only neighbours are $v_{i,3j}$ and $v_{i,3j+2}$; but $v_{i,3j+2}$ already has its predecessor
  and its successor on the cycle. So $v_{i,3j+1}$ would have to be entered from $v_{i,3j}$ and left to $v_{i,3j}$,
  which a cycle through more than two vertices cannot do.
- *From $v_{i,3j+1}$.* Then look at $v_{i,3j+3}$. It is not entered from $v_{i,3j+2}$ (whose successor is $c_j$)
  or from $c_j$ (by assumption), so it is entered from $v_{i,3j+4}$. It must leave to $v_{i,3j+2}$ (which already
  has a predecessor) or to $v_{i,3j+4}$ (where it just came from). Both are impossible.

Either way we have a contradiction, which proves the claim.

So every visit to a clause vertex is a short detour that returns to the same row. Remove the detours: what remains
is a Hamiltonian cycle of the graph without clause vertices, and in that graph, once the cycle enters a row at one
end, it must run through the whole row to the other end (a bead in the middle has only its two neighbours), then go
on to the next row. Read off $x_i$ = true if row $i$ is crossed left to right. Each $c_j$ was visited by a detour
from some row, in the direction that row was crossed, so the corresponding literal is true. $\square$

The free beads matter: the first case of the proof needs a bead next to every clause pair that has no way out of
the row. While testing this chapter's program, a first version put clause 0's pair at beads 1 and 2, so the only
bead to its left was the end bead 0, which *does* have arcs to the next row. The search then found a Hamiltonian
cycle for an *unsatisfiable* formula: it entered row 3 at bead 0, jumped at once to row 4, and came back into row 3
later through a clause vertex at bead 1. With two free beads at each end the escape is impossible, which is why the
construction uses $3k + 3$ beads.

**Directed to undirected.** Replace each vertex $v$ by a path of three vertices $v_{\text{in}} - v_{\text{mid}} - v_{\text{out}}$, and each arc $u \to v$ by the edge $u_{\text{out}} - v_{\text{in}}$. A Hamiltonian cycle must pass
through each middle vertex, which has degree 2, so it traverses every triple as in, mid, out (or the reverse
throughout, by symmetry), and the directed cycle can be read off. So UNDIRECTED HAMILTONIAN CYCLE is NP-complete.

**And the travelling salesman.** The decision version of the **travelling salesman problem** (TSP) asks: given
distances between $n$ cities and a budget $L$, is there a tour visiting every city once of total length at most $L$?
Reduce from Hamiltonian cycle: give distance 1 to pairs joined by an edge and 2 to all other pairs, and set $L = n$.
A tour of length $n$ uses only distance-1 pairs, so it is a Hamiltonian cycle, and conversely. Planning the order in
which a rover visits a list of sampling sites, or in which a telescope observes a list of targets, is a problem of
this kind, so exact optimal answers for large lists are out of reach, and Chapter 23's approximations are used
instead.

### Code: every reduction, checked

The first program implements SAT to 3-SAT, 3-SAT to independent set, independent set to vertex cover and to clique,
and 3-SAT to subset sum, prints the worked examples above, and checks on 200 random formulas (half of them built to
be unsatisfiable or nearly so) that every reduction preserves the answer. The checkers are exhaustive searches
written independently of the reductions (branching for independent sets, vertex covers and cliques; meet in the
middle for subset sum, as in [Chapter 14](14-Backtracking-and-Branch-and-Bound.md)).

```python
--8<-- "books/algorithms/ch22_reductions.py"
```

```
A worked example: (x1 or x2 or x3) and (not x1 or not x2 or x3) and (x1 or not x2 or not x3)
  independent set instance: 9 vertices, 15 edges, k = 3; answer True
  subset sum numbers: ['100101', '100010', '010100', '010011', '001110', '001001', '000100', '000200', '000010', '000020', '000001', '000002']
  target: 111444

SAT -> 3-SAT on a formula with clauses of length 1, 2 and 5:
   [[1], [-1, 2], [-2, 3, -4, 5, 1]] -> [[1, 6, 7], [1, 6, -7], [1, -6, 7], [1, -6, -7], [-1, 2, 8], [-1, 2, -8], [-2, 3, 9], [-9, -4, 10], [-10, 5, 1]] (10 variables)

Random checks: the answer is preserved by every reduction
  SAT->3SAT        agreed on 200 of 200 instances
  3SAT->IS         agreed on 200 of 200 instances
  IS->VC           agreed on 200 of 200 instances
  IS->Clique       agreed on 200 of 200 instances
  3SAT->SubsetSum  agreed on 200 of 200 instances
  satisfiable: 160 of the 200 general formulas, 102 of the 200 3-CNF formulas
```

The second program builds the Hamiltonian-cycle graph, searches it by depth-first search with pruning (a vertex not
yet on the path must still have a way in and a different way out), reads the assignment off the cycle it finds,
converts the cycle to the undirected graph, and checks unsatisfiable formulas too.

```python
--8<-- "books/algorithms/ch22_hamiltonian.py"
```

```
Example [[1, -2, 3], [-1, 2, -3]]: directed graph with 31 vertices and 73 arcs
  formula satisfiable: True   Hamiltonian cycle found: True
  row 1 entered at bead  0: x1 = True
  row 2 entered at bead  0: x2 = True
  row 3 entered at bead  0: x3 = True
  clause vertices visited after: [('v', 3, 2), ('v', 2, 5)]
  undirected version: 93 vertices, 135 edges; the tripled cycle is a Hamiltonian cycle there: True

All 8 clauses on x1, x2, x3 (unsatisfiable): 91 vertices; Hamiltonian cycle found: False

Four variables: all 8 sign patterns on three of them (with none or one removed), plus one random clause:
  the reduction agreed with brute force on 4 of 4 formulas (1 satisfiable)
```

With all variables true, clause 0 $(x_1 \vee \neg x_2 \vee x_3)$ is served by a detour from row 3 at bead 2, and
clause 1 $(\neg x_1 \vee x_2 \vee \neg x_3)$ by a detour from row 2 at bead $3 \cdot 1 + 2 = 5$, exactly as the
proof says.

## 22.6 Karp's 21 problems, co-NP and PSPACE

*Level: advanced to expert.*

### Karp's list

Cook's paper showed satisfiability NP-complete, together with a few related problems. A year later Richard Karp's paper "Reducibility Among
Combinatorial Problems" (in *Complexity of Computer Computations*, edited by Miller and Thatcher, 1972) showed that
21 well-known problems from operations research, graph theory and logic are all NP-complete, by a tree of
reductions starting from SAT. That paper is what made the theory matter to everyone: suddenly the problems that
whole communities had failed to solve efficiently were all the same problem. In Karp's own names, the 21 are:

| | | |
|---|---|---|
| satisfiability | 0-1 integer programming | clique |
| set packing | node cover | set covering |
| feedback node set | feedback arc set | directed Hamilton circuit |
| undirected Hamilton circuit | satisfiability with at most 3 literals per clause | chromatic number |
| clique cover | exact cover | hitting set |
| Steiner tree | 3-dimensional matching | knapsack |
| job sequencing | partition | max cut |

("Node cover" is vertex cover; Karp's "knapsack" is essentially subset sum.) Michael Garey and David Johnson's
book *Computers and Intractability: A Guide to the Theory of NP-Completeness* (1979) collected some 300 more, and the
list has grown into the thousands. The name "NP-complete" itself was settled by a poll among researchers that Knuth
reported in 1974 ("A Terminological Proposal", *SIGACT News*).

Two subtleties are worth knowing. **Strong NP-completeness**: subset sum and knapsack are NP-complete only because
their numbers can be huge; with numbers bounded by a polynomial in $n$ the DP solves them. Problems such as TSP,
3-partition or bin packing stay NP-complete even when all numbers are small; they are **strongly NP-complete**, and
no pseudo-polynomial algorithm exists for them unless P = NP. **NP-intermediate problems**: Richard Ladner proved in
1975 that if $\mathrm{P} \ne \mathrm{NP}$, there are problems in NP that are neither in P nor NP-complete. Natural
candidates are factoring (in its decision form) and graph isomorphism, for which László Babai announced a
quasi-polynomial algorithm, time $2^{O((\log n)^c)}$, in 2015.

### co-NP

NP is about short proofs of **yes**. **co-NP** is the class of problems whose **no**-instances have short proofs;
equivalently, problems whose complement is in NP. Examples: UNSAT (is this formula unsatisfiable?), TAUTOLOGY (is
this formula true under every assignment?), "this graph has no Hamiltonian cycle". No one knows a short certificate
that a formula is unsatisfiable; proofs found by SAT solvers can be exponentially long.

- P is closed under complement (flip the answer), so $\mathrm{P} \subseteq \mathrm{NP} \cap \mathrm{co\text{-}NP}$.
- If $\mathrm{NP} \ne \mathrm{co\text{-}NP}$ then $\mathrm{P} \ne \mathrm{NP}$ (Exercise 12).
- If any NP-complete problem were in co-NP, then $\mathrm{NP} = \mathrm{co\text{-}NP}$.

So a problem in $\mathrm{NP} \cap \mathrm{co\text{-}NP}$ is unlikely to be NP-complete. PRIMES was an example
(Pratt's 1975 certificates showed it is in NP) long before the AKS algorithm of Agrawal, Kayal and Saxena (2002,
published 2004) put it in P; factoring's decision version ("does $n$ have a factor below $m$?") is in
$\mathrm{NP} \cap \mathrm{co\text{-}NP}$ and believed not to be in P, which is what RSA relies on
([https://cryptography.akadian.ca/book/](https://cryptography.akadian.ca/book/)).

### PSPACE

**PSPACE** is the class of problems solvable with a polynomial amount of memory, with no limit on time. It contains
NP: try every certificate one after another, reusing the same space. The typical complete problem is **TQBF**, true
quantified Boolean formulas, such as $\forall x_1 \exists x_2 \forall x_3 \dots \varphi$, shown PSPACE-complete by
Stockmeyer and Meyer (1973). SAT is the special case with only $\exists$. Quantifiers alternating like this are the
moves of a two-player game ("for every move of mine, you have a reply"), and many generalized games (such as
generalized geography, or determining the winner of Hex on an $n \times n$ board) are PSPACE-complete. Savitch's
theorem (1970) shows that nondeterminism adds nothing for space: $\mathrm{NPSPACE} = \mathrm{PSPACE}$.

The known picture is

$$
\mathrm{P} \subseteq \mathrm{NP} \subseteq \mathrm{PSPACE} \subseteq \mathrm{EXP}, \qquad \mathrm{P} \ne \mathrm{EXP}.
$$

The last fact is the **time hierarchy theorem** (Hartmanis and Stearns, 1965): with more time, strictly more
problems can be solved, proved by a diagonal argument like the halting problem's. So at least one of the three
inclusions is strict, and nobody knows which. [Chapter 25](25-Where-Algorithms-Go.md) explains why proving
$\mathrm{P} \ne \mathrm{NP}$ is so hard.

## 22.7 What to do with an NP-hard problem

Suppose your problem turns out to be NP-hard: a delivery-route planner, a timetable, a chip layout, the order in
which a lander's instruments should run within a power budget. NP-hardness is a statement about the **worst case**,
for **exact** answers, as the input grows **without bound**. Each of those three words opens a way out.

1. **Check that your instances are really general.** Many NP-hard problems are easy on special inputs.
   Independent set is NP-hard on general graphs but linear on trees ([Chapter 13](13-Dynamic-Programming.md), 13.6)
   and polynomial on bipartite graphs (by matching, Chapter 17); 2-SAT is linear; graph colouring with 2 colours is
   bipartiteness testing. Bounded **treewidth** makes many problems linear for fixed width.
2. **Solve exactly, but cleverly.** Exponential is not all the same: $1.2^n$ is far better than $2^n$, and $2^n$
   far better than $n!$. Held-Karp solves TSP in $O(2^n n^2)$ instead of $n!$ (Chapter 13); branch and bound and
   meet in the middle ([Chapter 14](14-Backtracking-and-Branch-and-Bound.md)) push the practical limit further.
3. **Approximate.** Find a solution provably within a factor of the optimum in polynomial time: a vertex cover at
   most twice the minimum, a metric TSP tour at most 1.5 times the shortest.
   [Chapter 23](23-Approximation-and-Parameterized-Algorithms.md) builds these, and shows that for some problems
   even approximation is NP-hard.
4. **Parameterize.** If some parameter $k$ of the instance is small (the size of the cover you look for, the
   treewidth), an algorithm running in $f(k) \cdot n^{O(1)}$ time, such as vertex cover in $O(2^k n)$, is fast
   whatever $n$ is. This is **fixed-parameter tractability**, also in Chapter 23.
5. **Use a solver.** Modern SAT solvers (conflict-driven clause learning, which grew out of the DPLL procedure of
   22.4) and integer programming solvers routinely solve industrial instances with millions of variables, because
   real instances have structure that worst-case instances lack. Encoding your problem into SAT or an integer
   program, as the colouring example of 22.4 did, is often the fastest route to a working system.
6. **Use heuristics.** Local search, simulated annealing and genetic algorithms give good solutions without
   guarantees. Measure them honestly on realistic data.

And one way out that does not work: hoping for a clever polynomial algorithm. If you find one for an NP-complete
problem, you have proved P = NP. That is possible, but it is not the way to bet.

## Check yourself

??? question "1. Is the Euler tour problem in NP? Is it in P? What about the Hamiltonian cycle problem, and the problem \"does this graph have *no* Hamiltonian cycle?\""

    Euler tour is in P (connected, and every degree even, checked in linear time), hence in NP. Hamiltonian cycle is
    in NP (certificate: the cycle) and NP-complete (22.5). "No Hamiltonian cycle" is in co-NP; it is not known to
    be in NP, because no short certificate of non-existence is known, and it is in NP only if
    $\mathrm{NP} = \mathrm{co\text{-}NP}$.

??? question "2. A friend writes Sudoku as a SAT formula and concludes that Sudoku is NP-hard. What is wrong? What would show it?"

    Encoding Sudoku into SAT is a reduction from Sudoku *to* SAT. It shows Sudoku is no harder than SAT, which holds
    for every problem in NP. To show hardness (for generalized $n^2 \times n^2$ Sudoku) one must reduce a known
    NP-complete problem *to* Sudoku. Such a reduction exists: Yato and Seta (2003) showed that completing
    generalized Sudoku is NP-complete, via Latin-square completion.

??? question "3. Apply the SAT to 3-SAT construction to the single clause $(x_1 \vee \neg x_2 \vee x_3 \vee x_4 \vee \neg x_5)$. Then check that $x_4$ = true and every other old literal false extends to the new clauses."

    $(x_1 \vee \neg x_2 \vee y_1)(\neg y_1 \vee x_3 \vee y_2)(\neg y_2 \vee x_4 \vee \neg x_5)$. Here $\ell_r = x_4$
    is literal number $r = 4$, so set $y_i$ true for $i \le 2$: $y_1$ and $y_2$ are true. Clause 1 holds by $y_1$,
    clause 2 by $y_2$, clause 3 by $x_4$.

??? question "4. Why can't the chain trick reduce 3-SAT to 2-SAT, and what goes wrong if you try?"

    A clause of two literals has room for only one old literal plus one connector, so a chain cannot pass a
    "still to come" signal along: from $(\ell_1 \vee y_1)(\neg y_1 \vee \ell_2)$ you get only the implications
    $\neg\ell_1 \Rightarrow y_1 \Rightarrow \ell_2$, which say "$\ell_1$ or $\ell_2$", and there is no way to add a
    third literal. Indeed 2-SAT is in P (implication graph and strongly connected components), so a reduction
    from 3-SAT would prove P = NP.

??? question "5. Build the independent-set instance for $(x_1 \vee x_2 \vee \neg x_3)(\neg x_1 \vee x_2 \vee x_3)$. How many vertices and edges, and which independent sets of size 2 are there?"

    Six vertices: $a_1 = x_1, a_2 = x_2, a_3 = \neg x_3$ and $b_1 = \neg x_1, b_2 = x_2, b_3 = x_3$. Triangle edges:
    6. Conflict edges: $a_1 b_1$ and $a_3 b_3$: 2. Total 8 edges. The size-2 independent sets take one vertex per
    clause and avoid $a_1 b_1$ and $a_3 b_3$: $\{a_1, b_2\}$, $\{a_1, b_3\}$, $\{a_2, b_1\}$, $\{a_2, b_2\}$,
    $\{a_2, b_3\}$, $\{a_3, b_1\}$, $\{a_3, b_2\}$: 7 of the 9 pairs. Each gives satisfying assignments, for
    example $\{a_2, b_2\}$ means $x_2$ = true.

??? question "6. In the subset-sum reduction, why are the slack numbers 1 and 2 and the clause target 4, rather than, say, target 1 and no slacks?"

    The clause digit must accept any number of true literals from 1 to 3 and reject 0. With slacks 1 and 2, the
    reachable totals from slacks are 0, 1, 2, 3, so the target 4 is reachable exactly when the literals contribute
    1, 2 or 3. With target 1 and no slacks, a clause with two true literals would give digit 2 and the reduction
    would wrongly reject many satisfying assignments.

??? question "7. Show that the decision version of TSP is in NP, and give the reduction from Hamiltonian cycle with an example."

    Certificate: the tour; check it visits every city once and add up its length. Reduction: distance 1 for edges,
    2 for non-edges, budget $L = n$. For the 4-cycle 0-1-2-3-0 the distances are 1 on its four edges and 2 on the
    diagonals 0-2 and 1-3; the tour 0, 1, 2, 3 has length 4 = $L$. If the graph has no Hamiltonian cycle, every tour
    uses some non-edge and has length at least $n + 1$.

??? question "8. Write the code: a verifier for 3-colouring, and the reduction CLIQUE to INDEPENDENT SET. Test the reduction on a triangle with a pendant vertex."

    ```python
    from itertools import combinations
    def verify_3col(n, edges, colour):
        return len(colour) == n and all(c in (0, 1, 2) for c in colour) and all(colour[u] != colour[v] for u, v in edges)

    def clique_to_is(n, edges, k):                    # S is a clique in G  <=>  S is independent in the complement
        E = {frozenset(e) for e in edges}
        return n, [(u, v) for u, v in combinations(range(n), 2) if frozenset((u, v)) not in E], k

    def has_is(n, edges, k):
        E = {frozenset(e) for e in edges}
        return any(all(frozenset(p) not in E for p in combinations(S, 2)) for S in combinations(range(n), k))

    G = [(0, 1), (1, 2), (0, 2), (2, 3)]
    print(verify_3col(4, G, [0, 1, 2, 0]), has_is(*clique_to_is(4, G, 3)), has_is(*clique_to_is(4, G, 4)))
    # True True False
    ```

    The triangle $\{0, 1, 2\}$ is a clique of size 3, so the complement has an independent set of size 3; there is
    no clique of size 4.

??? question "9. The 0/1 knapsack DP runs in $O(nW)$. Knapsack is NP-complete. Why is this not a proof that P = NP?"

    The input size is about $n \log W$ bits, not $W$. The running time $nW = n \cdot 2^{\log_2 W}$ is exponential in
    the length of $W$'s binary representation. The DP is pseudo-polynomial: polynomial only when the numbers are
    small. The subset-sum reduction from 3-SAT produces numbers with $n + k$ decimal digits, where the DP is
    exponential.

??? question "10. Show that if P = NP, then for every NP problem with a self-reduction like SAT's, an actual solution (not just yes or no) can be found in polynomial time. Do it for CLIQUE."

    Given $(G, k)$, ask the polynomial decider whether $G$ has a $k$-clique. If yes, go through the vertices: delete
    $v$ and ask again; if the answer is still yes, leave $v$ deleted, otherwise put it back (it is needed). After
    one pass, the remaining graph has a $k$-clique but no vertex can be removed, so it has exactly $k$ vertices,
    which form the clique. That is $n + 1$ calls to a polynomial algorithm on graphs no larger than $G$.

??? question "11. (Hard) Outline why 3-COLOURING is NP-complete, by reducing 3-SAT to it."

    It is in NP (the colouring). Reduction: make a triangle on three special vertices TRUE, FALSE, BASE. For each
    variable, a triangle on $x_i$, $\neg x_i$ and BASE: so $x_i$ and $\neg x_i$ get the colours of TRUE and FALSE
    in some order, which is a truth assignment. For each clause $(a \vee b \vee c)$ attach a small "OR gadget" of a
    few new vertices connected to $a$, $b$, $c$, TRUE and FALSE, built so that it can be 3-coloured exactly when at
    least one of $a, b, c$ has the colour of TRUE. Checking the gadget's two properties is a finite case analysis;
    the full construction is in Kleinberg and Tardos, section 8.7. The graph has $O(n + k)$ vertices.

??? question "12. Prove: if $\mathrm{P} = \mathrm{NP}$ then $\mathrm{NP} = \mathrm{co\text{-}NP}$. Conclude that $\mathrm{NP} \ne \mathrm{co\text{-}NP}$ would imply $\mathrm{P} \ne \mathrm{NP}$."

    Suppose P = NP. If $A \in \mathrm{co\text{-}NP}$, its complement $\bar A$ is in NP = P. P is closed under
    complement, so $A = \overline{\bar A} \in \mathrm{P} = \mathrm{NP}$. So co-NP $\subseteq$ NP; symmetrically
    NP $\subseteq$ co-NP. The second statement is the contrapositive.

## What you learned

- A decision problem asks yes or no; input size is the length of its encoding, with numbers in binary, and
  "efficient" means polynomial in that length (P).
- NP is the class of problems whose yes-answers have short certificates checkable in polynomial time;
  $\mathrm{P} \subseteq \mathrm{NP} \subseteq \mathrm{PSPACE} \subseteq \mathrm{EXP}$, and whether P = NP is open.
- A polynomial-time reduction $A \le_p B$ translates instances and preserves answers in both directions; to prove
  a new problem hard, reduce a known hard problem *to* it.
- Cook and Levin showed SAT is NP-complete by writing "the verifier accepts some certificate" as a formula over
  the cells of its computation table.
- SAT, 3-SAT, independent set, vertex cover, clique, subset sum, Hamiltonian cycle and TSP are all NP-complete,
  each by a gadget proved correct in both directions.
- Karp's 21 problems made the theory central; co-NP is about short proofs of "no", PSPACE about polynomial memory,
  and graph isomorphism and factoring are candidates for the space between P and NP-complete.
- NP-hard means hard in the worst case for exact answers; special structure, clever exponential search,
  approximation, parameters, solvers and heuristics are the ways forward.

**Next:** [Chapter 23](23-Approximation-and-Parameterized-Algorithms.md), algorithms that give provably good answers
to NP-hard problems in polynomial time, or exact answers when a parameter is small.

## Further reading

- S. A. Cook, "The Complexity of Theorem-Proving Procedures", *Proceedings of the 3rd ACM Symposium on Theory of
  Computing*, 1971.
- L. A. Levin, "Universal Sequential Search Problems", *Problemy Peredachi Informatsii*, 1973 (English translation
  in *Problems of Information Transmission*).
- R. M. Karp, "Reducibility Among Combinatorial Problems", in R. E. Miller and J. W. Thatcher (eds.), *Complexity of
  Computer Computations*, 1972.
- M. R. Garey and D. S. Johnson, *Computers and Intractability: A Guide to the Theory of NP-Completeness*, 1979.
- J. Kleinberg and É. Tardos, *Algorithm Design*, 2005, chapters 8 and 9 (the Hamiltonian-cycle and 3-colouring
  reductions used here, and PSPACE).
- T. Cormen, C. Leiserson, R. Rivest and C. Stein, *Introduction to Algorithms*, 4th ed., 2022, chapter 34.
- M. Sipser, *Introduction to the Theory of Computation*, 3rd ed., 2012, chapters 7 and 8 (Cook-Levin in full,
  PSPACE, Savitch's theorem).
- S. Arora and B. Barak, *Computational Complexity: A Modern Approach*, 2009.
- J. Edmonds, "Paths, Trees, and Flowers", *Canadian Journal of Mathematics*, 1965; A. Cobham, "The Intrinsic
  Computational Difficulty of Functions", 1965.
- R. E. Ladner, "On the Structure of Polynomial Time Reducibility", *Journal of the ACM*, 1975.
- M. Agrawal, N. Kayal and N. Saxena, "PRIMES is in P", *Annals of Mathematics*, 2004.
- L. Stockmeyer and A. Meyer, "Word Problems Requiring Exponential Time", STOC 1973.
- On this site: [Chapter 13](13-Dynamic-Programming.md) (knapsack, Held-Karp),
  [Chapter 14](14-Backtracking-and-Branch-and-Bound.md) (exhaustive search),
  [Chapter 21](21-Randomized-and-Amortized-Analysis.md) (randomized algorithms),
  [Chapter 25](25-Where-Algorithms-Go.md) (why P versus NP is hard to settle); the reference pages
  [Knapsack](../../dp/knapsack.md), [Subsets and permutations](../../backtracking/subsets-permutations.md) and
  [Strongly connected components](../../graphs/scc.md); the [Artificial intelligence](../index.md) book for search
  and SAT-based planning; and [https://cryptography.akadian.ca/book/](https://cryptography.akadian.ca/book/) for
  cryptography built on problems believed hard.
