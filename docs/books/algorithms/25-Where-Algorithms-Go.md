# 25. Where algorithms go

*This book has built algorithms from the first idea of a recipe to approximation, streaming and consensus. This
last chapter looks at the edge of what is known: the questions nobody can answer yet, the finer theory that
explains why some quadratic algorithms have never been beaten, the exponent of matrix multiplication creeping down
year by year, the breakthroughs of the last few years on flows and shortest paths, what quantum computers would and
would not change, and how machine learning is starting to shape algorithms. You will run small versions of the key
ideas yourself, so that the frontier is not just a list of names. Everything here is labelled honestly: proved,
conjectured, or simply unknown.*

!!! abstract "In this chapter"
    **You will learn:**

    - what is proved and what is open about P versus NP, and the three barriers that explain why it is so hard
    - fine-grained complexity: the 3SUM, APSP and SETH conjectures, and why edit distance probably needs quadratic
      time
    - how the matrix multiplication exponent fell from 3 to below 2.372, and what limits the current methods
    - the almost-linear-time maximum flow algorithm and near-linear shortest paths with negative weights, in outline
    - Grover's and Shor's quantum algorithms, simulated, and what they do not do
    - learned indexes and algorithms with predictions: consistency and robustness
    - a list of open problems, and how to keep learning

    **You need:** [Chapter 22](22-NP-Completeness.md) (P, NP, reductions), [Chapter 23](23-Approximation-and-Parameterized-Algorithms.md)
    (LP, approximation), [Chapter 24](24-Algorithms-for-Big-Data-and-Many-Processors.md) (online algorithms),
    [Chapter 11](11-Divide-and-Conquer.md) (Strassen, FFT), [Chapter 13](13-Dynamic-Programming.md) (edit distance),
    [Chapter 16](16-Shortest-Paths.md) and [Chapter 17](17-Spanning-Trees-Flows-and-Matching.md) (shortest paths,
    flows). Section 25.5 uses complex numbers ([math.akadian.ca books](https://math.akadian.ca/books/)).

    **Levels:** all sections are advanced or expert, but each starts from a plain question; 25.7 is for everyone.

## 25.1 P versus NP: what is known, and why it is hard

*Level: advanced.*

[Chapter 22](22-NP-Completeness.md) defined **P** (problems solvable in polynomial time) and **NP** (problems
whose yes-answers have certificates checkable in polynomial time), and showed that thousands of natural problems
are **NP-complete**: if any one of them is in P, all of NP is. The question "is P = NP?" was posed in this form by
Stephen Cook (1971) and Leonid Levin (1973), and it is one of the seven Millennium Prize Problems of the Clay
Mathematics Institute (2000), with a prize of one million dollars.

**What is proved.** The known relations between the main classes are:

$$
\mathrm{P} \subseteq \mathrm{NP} \subseteq \mathrm{PSPACE} \subseteq \mathrm{EXPTIME}, \qquad \mathrm{P} \ne \mathrm{EXPTIME} .
$$

Here PSPACE is the class of problems solvable with polynomial memory (and any amount of time), and EXPTIME those
solvable in time $2^{n^{O(1)}}$. The inclusions are easy: a polynomial-time machine uses only polynomial memory,
and a machine with polynomial memory has at most exponentially many configurations, so it halts within exponential
time or loops. The inequality $\mathrm{P} \ne \mathrm{EXPTIME}$ is the **time hierarchy theorem** (Hartmanis and
Stearns, 1965), proved by diagonalization, the argument of the halting problem in
[Chapter 1](01-What-Is-an-Algorithm.md): build a machine that, on input $\langle M \rangle$, runs $M$ on itself for
$2^n$ steps and does the opposite. No machine running in time much less than $2^n$ can agree with it everywhere.
So **at least one** of the three inclusions $\mathrm{P} \subseteq \mathrm{NP} \subseteq \mathrm{PSPACE}
\subseteq \mathrm{EXPTIME}$ is strict, and nobody knows which. It is even open whether $\mathrm{P} \ne
\mathrm{PSPACE}$.

<figure class="mars-fig" markdown="0">
<svg viewBox="0 0 660 300" role="img" aria-label="Known inclusions: P inside NP and co-NP, both inside PSPACE, inside EXPTIME. P is known to differ from EXPTIME; whether P equals NP is open.">
<rect x="20" y="15" width="620" height="270" rx="30" fill="none" stroke="currentColor" stroke-width="1.3"/>
<text x="40" y="42" font-size="14" fill="currentColor">EXPTIME (known: P is not equal to EXPTIME)</text>
<rect x="60" y="55" width="540" height="215" rx="26" fill="#9cc9ea" fill-opacity="0.25" stroke="currentColor" stroke-width="1.2"/>
<text x="80" y="80" font-size="14" fill="currentColor">PSPACE (quantified formulas, many games)</text>
<ellipse cx="270" cy="175" rx="150" ry="75" fill="#eea66f" fill-opacity="0.3" stroke="currentColor" stroke-width="1.2"/>
<ellipse cx="390" cy="175" rx="150" ry="75" fill="#7ccf9a" fill-opacity="0.3" stroke="currentColor" stroke-width="1.2"/>
<ellipse cx="330" cy="175" rx="55" ry="40" fill="#9cc9ea" fill-opacity="0.8" stroke="currentColor" stroke-width="1.2"/>
<text x="330" y="172" font-size="14" text-anchor="middle" fill="currentColor">P</text>
<text x="330" y="190" font-size="11" text-anchor="middle" fill="currentColor">sorting, flows, LP</text>
<text x="185" y="170" font-size="14" text-anchor="middle" fill="currentColor">NP</text>
<text x="185" y="188" font-size="11" text-anchor="middle" fill="currentColor">SAT, TSP (decision)</text>
<text x="475" y="170" font-size="14" text-anchor="middle" fill="currentColor">co-NP</text>
<text x="475" y="188" font-size="11" text-anchor="middle" fill="currentColor">UNSAT, tautology</text>
<text x="330" y="230" font-size="11" text-anchor="middle" fill="currentColor">factoring</text>
</svg>
<figcaption>Figure 25.1. The picture most researchers believe, with P strictly inside NP and co-NP. Only the outer separation, P versus EXPTIME, is proved. Factoring (as a decision problem) is in both NP and co-NP but not known to be in P.</figcaption>
</figure>

**Why it matters either way.** If P = NP with a fast algorithm, then finding a proof of a theorem would be about as
easy as checking one, every optimisation problem of Chapters 13, 14 and 23 would be easy, and most of
[public-key cryptography](https://cryptography.akadian.ca/book/) would fall, since breaking it is an NP search
problem. If $\mathrm{P} \ne \mathrm{NP}$, then hardness is a law of nature that we can build on, and the
approximation and parameterized methods of Chapter 23 are not stopgaps but the right tools. Most researchers believe
$\mathrm{P} \ne \mathrm{NP}$, mostly because decades of effort have found no fast algorithm for any NP-complete
problem, and because a world where creativity is as easy as verification seems implausible. But belief is not
proof.

**Why it is hard: three barriers.** It is unusual in mathematics to have theorems saying *which proof methods
cannot work*. For P versus NP there are three.

*Relativization (Baker, Gill and Solovay, 1975).* An **oracle** $A$ is a black box that answers questions "is
$x \in A$?" in one step. Most proof techniques we know, diagonalization above all, still work if every machine is
given the same oracle: they **relativize**. Baker, Gill and Solovay built an oracle $A$ with
$\mathrm{P}^A = \mathrm{NP}^A$ (take $A$ to be a PSPACE-complete problem: then both classes equal PSPACE) and an
oracle $B$ with $\mathrm{P}^B \ne \mathrm{NP}^B$ (built by diagonalization so that a nondeterministic machine can
find hidden strings that no deterministic polynomial-time machine can). A relativizing proof of
$\mathrm{P} \ne \mathrm{NP}$ would also prove $\mathrm{P}^A \ne \mathrm{NP}^A$, which is false; a relativizing proof
of equality would contradict $B$. So the answer needs a non-relativizing idea.

*Natural proofs (Razborov and Rudich, 1994; journal 1997).* A natural route to $\mathrm{P} \ne \mathrm{NP}$ is to
prove that some NP problem needs Boolean **circuits** of superpolynomial size. All the circuit lower bounds known in
the early 1990s worked the same way: they found a property of Boolean functions that is easy to test (given the
function's truth table), true of many functions, and false for functions with small circuits. Razborov and Rudich
showed that if strong pseudorandom functions exist (which is what cryptography already assumes), then no such
"natural" property can prove superpolynomial lower bounds for general circuits. Informally: a natural proof would
also break cryptography.

*Algebrization (Aaronson and Wigderson, 2008).* Some non-relativizing results, such as IP = PSPACE (Shamir 1992),
use algebra: they extend Boolean formulas to polynomials over larger fields. Aaronson and Wigderson showed that
these techniques also fail to resolve P versus NP, in a precise sense.

**What has been proved instead.** Lower bounds are known for *restricted* models. Circuits of constant depth with
AND, OR and NOT gates (the class AC⁰) cannot compute the parity of $n$ bits in polynomial size (Furst, Saxe and
Sipser 1984; Ajtai 1983; with the sharp bound by Håstad 1986). Monotone circuits (no NOT gates) for detecting a
clique need exponential size (Razborov 1985). Ryan Williams (2011) proved that NEXP, nondeterministic exponential
time, does not have polynomial-size ACC⁰ circuits (constant depth with counting gates), by a new method that turns
a slightly faster *algorithm* for circuit satisfiability into a *lower bound*, a beautiful example of algorithms
and complexity feeding each other. For general circuits, though, the best lower bound for an explicit function is
only a little more than $3n$ gates. The gap between $3n$ and "superpolynomial" shows how far away the problem is.

## 25.2 Fine-grained complexity: 3SUM, SETH, edit distance

*Level: advanced.*

NP-completeness separates polynomial from exponential. Within P it says nothing: an $O(n^2)$ algorithm and an
$O(n^{1.01})$ one are both "efficient". But for a genome of $10^9$ letters the difference between $n^2$ and
$n \log n$ is the difference between centuries and seconds. Edit distance ([Chapter 13](13-Dynamic-Programming.md),
[reference page](../../dp/edit-distance.md)) has had a quadratic algorithm since the 1970s, and despite huge
interest, the best known improvement, by William Masek and Michael Paterson (1980), saves only a logarithmic
factor. Is quadratic the truth? We cannot prove it outright, any more than we can prove $\mathrm{P} \ne
\mathrm{NP}$. **Fine-grained complexity** does the next best thing: it picks a few problems whose running times
have resisted improvement for decades, conjectures their exact exponents, and then proves, by careful reductions,
that many other problems are just as hard.

A **fine-grained reduction** from problem A (best known time $a(n)$) to problem B (best known time $b(n)$) shows:
if B can be solved in time $b(n)^{1-\delta}$ for some $\delta > 0$, then A can be solved in time
$a(n)^{1-\delta'}$ for some $\delta' > 0$. The reduction itself must be cheaper than $a(n)$. Three conjectures carry
most of the field:

1. **The 3SUM conjecture.** Given $n$ integers, are there three that sum to 0? The sort-and-two-pointers algorithm
   takes $O(n^2)$. Conjecture: no $O(n^{2-\delta})$ algorithm exists. (Allan Grønlund and Seth Pettie (2014)
   found an algorithm that saves a small power of $\log n$, which is why the conjecture is stated with $\delta$.)
   Anka Gajentaan and Mark Overmars (1995) showed that many problems of computational geometry, such as deciding
   whether three of $n$ points lie on a line, are "3SUM-hard".
2. **The APSP conjecture.** All-pairs shortest paths with integer weights needs $n^{3-o(1)}$ time. Virginia
   Vassilevska Williams and Ryan Williams (2010) showed that many problems are equivalent to it under
   subcubic reductions, among them finding a triangle of negative total weight and checking a matrix product over
   (min, +).
3. **The Strong Exponential Time Hypothesis (SETH)** (Impagliazzo and Paturi, 2001).
   For every $\varepsilon > 0$ there is a $k$ such that $k$-SAT on $n$ variables cannot be solved in time
   $O(2^{(1-\varepsilon)n})$. In words: for wide clauses, nothing is much better than trying all assignments. (The
   weaker **ETH** says 3-SAT needs $2^{cn}$ time for some $c > 0$.)

Here is the 3SUM algorithm and its cubic rival, counting their basic steps:

```python
--8<-- "books/algorithms/ch25_fine_grained.py"
```

```
3SUM on n distinct odd integers (no solution exists: three odds never sum to 0)
    n   cubic triples checked   quadratic pointer steps
   50                   19600                      1176
  100                  161700                      4851
  200                 1313400                     19701

3-CNF with n=12 variables, m=30 clauses: two lists of 64 vectors of dimension 30; orthogonal pair found: True; brute force says satisfiable: True
3-CNF with n=12 variables, m=70 clauses: two lists of 64 vectors of dimension 70; orthogonal pair found: False; brute force says satisfiable: False
```

The second half of the program builds the bridge from SETH to problems in P.

**Orthogonal Vectors (OV).** Given two lists $L$ and $R$ of $N$ vectors each in $\{0,1\}^d$, is there $u \in L$,
$v \in R$ with $u \cdot v = 0$ (no coordinate where both are 1)? Trying all pairs takes $O(N^2 d)$.

**Theorem (R. Williams, 2005).** If OV can be solved in time $O(N^{2-\delta}\,\mathrm{poly}(d))$ for some
$\delta > 0$, then SETH is false.

*Proof.* Take a CNF formula with $n$ variables and $m$ clauses. Split the variables into two halves. For each of
the $N = 2^{n/2}$ assignments $\alpha$ of the first half, make a vector $u_\alpha \in \{0,1\}^m$ with
$u_\alpha[j] = 0$ if $\alpha$ already satisfies clause $j$ and 1 otherwise; do the same for the second half,
giving vectors $v_\beta$. The full assignment $(\alpha, \beta)$ satisfies the formula exactly when every clause is
satisfied by one of the halves, that is, when no coordinate $j$ has $u_\alpha[j] = v_\beta[j] = 1$: when
$u_\alpha \cdot v_\beta = 0$. So the formula is satisfiable if and only if the OV instance has an orthogonal pair.
Building the lists costs $O(2^{n/2} m n)$. An OV algorithm running in $N^{2-\delta}\mathrm{poly}(m)$ would solve
SAT in $2^{(n/2)(2-\delta)}\mathrm{poly}(m) = 2^{(1-\delta/2)n}\mathrm{poly}(m)$. For $k$-SAT, the
**sparsification lemma** (Impagliazzo, Paturi and Zane, 2001) lets us assume $m = O(n)$, so $\mathrm{poly}(m)$ is
absorbed and every $k$-SAT would be solvable in $O(2^{(1-\delta/3)n})$ time, contradicting SETH. $\square$

The program carries out exactly this split on a 12-variable formula and gets the right answer both times. From OV,
reductions go to many quadratic problems. The best known:

**Theorem (Backurs and Indyk, 2015).** If edit distance between two strings of length $n$ can be computed in time
$O(n^{2-\delta})$ for some $\delta > 0$, then SETH is false.

The proof builds, from each vector, a string "gadget" such that the edit distance of the two long concatenated
strings drops by a fixed amount exactly when some pair of gadgets comes from orthogonal vectors; it is technical
and runs about 20 pages. The same year Amir Abboud, Arturs Backurs and Virginia Vassilevska Williams, and
independently Karl Bringmann and Marvin Künnemann, proved the same for longest common subsequence
([reference page](../../dp/lcs.md)), and Bringmann (2014) for the Fréchet distance between curves. So the
quadratic dynamic programs of Chapter 13 are, under SETH, essentially optimal. The theory does not forbid saving
logarithmic factors (Masek and Paterson's method is consistent with it), nor fast *approximation*: Diptarka
Chakraborty, Debarati Das, Elazar Goldenberg, Michal Koucký and Michael Saks (2018) found a constant-factor
approximation of edit distance in strongly subquadratic time.

Fine-grained complexity has changed how algorithm researchers work: when an improvement resists, one now looks for
a reduction from OV, 3SUM or APSP, which either explains the difficulty or, if the reduction fails, often hints at
the algorithm.

## 25.3 The matrix multiplication exponent

*Level: advanced.*

Multiplying two $n \times n$ matrices by the schoolbook rule takes $n^3$ multiplications. Define the **exponent of
matrix multiplication** $\omega$ as the smallest number such that, for every $\varepsilon > 0$, matrices can be
multiplied with $O(n^{\omega + \varepsilon})$ arithmetic operations. Since the output has $n^2$ entries,
$2 \le \omega \le 3$. Matrix multiplication sits inside many other algorithms (solving linear systems, inverting
matrices, computing determinants, finding triangles in graphs, transitive closure, parsing context-free languages),
so the exponent $\omega$ appears in all their running times.

**Strassen's discovery (1969).** Volker Strassen found that two $2 \times 2$ matrices can be multiplied with **7**
multiplications instead of 8 (the formulas are in [Chapter 11](11-Divide-and-Conquer.md)), using more additions.
Crucially, the formulas never use that multiplication is commutative, so they work when the entries are
themselves matrices. Applied recursively to blocks, $T(n) = 7T(n/2) + O(n^2)$, which by the master theorem is
$O(n^{\log_2 7}) = O(n^{2.8074})$. The program counts the multiplications exactly:

```python
--8<-- "books/algorithms/ch25_matrix.py"
```

```
    n   schoolbook mults   Strassen mults (to 1x1)   ratio   7^k / 8^k
    2                  8                         7   0.875   0.875
    4                 64                        49   0.766   0.766
    8                512                       343   0.670   0.670
   16               4096                      2401   0.586   0.586
   32              32768                     16807   0.513   0.513
   64             262144                    117649   0.449   0.449
exponent log2(7) = 2.8074

  2x2 with  8 products -> exponent log_2(8) = 3.0000   (schoolbook)
  2x2 with  7 products -> exponent log_2(7) = 2.8074   (Strassen 1969)
  3x3 with 23 products -> exponent log_3(23) = 2.8540   (Laderman 1976)
  3x3 with 21 products -> exponent log_3(21) = 2.7712   (hypothetical: 21 products for 3x3)
```

The general principle: if $k \times k$ matrices can be multiplied with $r$ non-commutative multiplications, then
$\omega \le \log_k r$. The smallest such $r$ is the **rank** of the matrix multiplication **tensor**, a
three-dimensional array that records which products of entries go into which output. For $2 \times 2$, rank 7 is
optimal (Winograd 1971). For $3 \times 3$ the best known is 23 (Julian Laderman, 1976), which gives only 2.854,
worse than Strassen; finding 21 or fewer would beat Strassen, and nobody knows whether it is possible (the best
lower bound on the rank is 19, by Markus Bläser, 2003). In 2022 Fawzi and colleagues reported, in *Nature*
("Discovering faster matrix multiplication algorithms with reinforcement learning"), schemes found by a learning
system, including 47 multiplications for $4 \times 4$ matrices in arithmetic modulo 2, against Strassen's
$7^2 = 49$.

**The long descent.** The big improvements did not come from small schemes but from asymptotic ones. Victor Pan
(1978), and Dario Bini, Milvio Capovani, Francesco Romani and Grazia Lotti (1979, with **border rank**, a limit of
approximate schemes), each lowered the exponent slightly. Arnold Schönhage (1981) showed that schemes for several
independent products can be combined (the **asymptotic sum inequality**), reaching 2.522. Strassen's **laser
method** (1986) and Don Coppersmith and Shmuel Winograd's construction (1990) reached 2.376, and then for twenty
years nothing changed. Since 2010 the Coppersmith-Winograd approach has been analysed with more and more powerful
computer-assisted optimisation:

| year | authors | bound on $\omega$ |
|---|---|---|
| 1969 | Strassen | 2.8074 |
| 1981 | Schönhage | 2.522 |
| 1990 | Coppersmith and Winograd | 2.3755 |
| 2010 | Stothers | 2.3737 |
| 2012 | Vassilevska Williams | 2.3729 |
| 2014 | Le Gall | 2.3728639 |
| 2021 | Alman and Vassilevska Williams | 2.3728596 |
| 2023 | Duan, Wu and Zhou | 2.371866 |
| 2024 | Vassilevska Williams, Xu, Xu and Zhou | 2.371552 |
| 2025 | Alman, Duan, Vassilevska Williams, Xu, Xu and Zhou | 2.371339 |

(Years are those of the published papers; several appeared on arXiv a year earlier.)

<figure class="mars-fig" markdown="0">
<svg viewBox="0 0 660 310" role="img" aria-label="Upper bounds on the matrix multiplication exponent omega by year, from 2.81 in 1969 to 2.371 in 2025, with the trivial lower bound 2 below the plotted range.">
<g stroke="currentColor" stroke-width="1.2"><line x1="70" y1="260" x2="640" y2="260"/><line x1="70" y1="260" x2="70" y2="25"/></g>
<g font-size="12" fill="currentColor" text-anchor="end">
<text x="62" y="264.0">2.3</text>
<text x="62" y="231.1">2.4</text>
<text x="62" y="198.3">2.5</text>
<text x="62" y="165.4">2.6</text>
<text x="62" y="132.6">2.7</text>
<text x="62" y="99.7">2.8</text>
<text x="62" y="66.9">2.9</text>
<text x="62" y="34.0">3.0</text>
</g><g stroke="currentColor" stroke-opacity="0.25" stroke-width="1">
<line x1="70" y1="227.1" x2="640" y2="227.1"/>
<line x1="70" y1="194.3" x2="640" y2="194.3"/>
<line x1="70" y1="161.4" x2="640" y2="161.4"/>
<line x1="70" y1="128.6" x2="640" y2="128.6"/>
<line x1="70" y1="95.7" x2="640" y2="95.7"/>
<line x1="70" y1="62.9" x2="640" y2="62.9"/>
<line x1="70" y1="30.0" x2="640" y2="30.0"/>
</g><g font-size="12" fill="currentColor" text-anchor="middle">
<text x="115.2" y="277">1970</text>
<text x="205.5" y="277">1980</text>
<text x="295.8" y="277">1990</text>
<text x="386.1" y="277">2000</text>
<text x="476.5" y="277">2010</text>
<text x="566.8" y="277">2020</text>
</g>
<path d="M 70.0 30.0 L 106.1 30.0 L 106.1 30.0 L 106.1 93.3 L 187.4 93.3 L 187.4 97.0 L 196.5 97.0 L 196.5 102.3 L 214.5 102.3 L 214.5 187.1 L 219.9 187.1 L 219.9 195.6 L 259.7 195.6 L 259.7 201.2 L 295.8 201.2 L 295.8 235.2 L 476.5 235.2 L 476.5 235.8 L 494.5 235.8 L 494.5 236.0 L 512.6 236.0 L 512.6 236.1 L 575.8 236.1 L 575.8 236.1 L 593.9 236.1 L 593.9 236.4 L 602.9 236.4 L 602.9 236.5 L 611.9 236.5 L 611.9 236.6 L 630.0 236.6" fill="none" stroke="#9cc9ea" stroke-width="2.5"/>
<circle cx="106.1" cy="93.3" r="4" fill="#eea66f" stroke="currentColor" stroke-width="1"/>
<circle cx="187.4" cy="97.0" r="4" fill="#eea66f" stroke="currentColor" stroke-width="1"/>
<circle cx="196.5" cy="102.3" r="4" fill="#eea66f" stroke="currentColor" stroke-width="1"/>
<circle cx="214.5" cy="187.1" r="4" fill="#eea66f" stroke="currentColor" stroke-width="1"/>
<circle cx="219.9" cy="195.6" r="4" fill="#eea66f" stroke="currentColor" stroke-width="1"/>
<circle cx="259.7" cy="201.2" r="4" fill="#eea66f" stroke="currentColor" stroke-width="1"/>
<circle cx="295.8" cy="235.2" r="4" fill="#eea66f" stroke="currentColor" stroke-width="1"/>
<circle cx="476.5" cy="235.8" r="4" fill="#eea66f" stroke="currentColor" stroke-width="1"/>
<circle cx="494.5" cy="236.0" r="4" fill="#eea66f" stroke="currentColor" stroke-width="1"/>
<circle cx="512.6" cy="236.1" r="4" fill="#eea66f" stroke="currentColor" stroke-width="1"/>
<circle cx="575.8" cy="236.1" r="4" fill="#eea66f" stroke="currentColor" stroke-width="1"/>
<circle cx="593.9" cy="236.4" r="4" fill="#eea66f" stroke="currentColor" stroke-width="1"/>
<circle cx="602.9" cy="236.5" r="4" fill="#eea66f" stroke="currentColor" stroke-width="1"/>
<circle cx="611.9" cy="236.6" r="4" fill="#eea66f" stroke="currentColor" stroke-width="1"/>
<text x="114.1" y="85.3" font-size="12" fill="currentColor">Strassen 1969: 2.807</text>
<text x="224.5" y="183.1" font-size="12" fill="currentColor">Schönhage 1981: 2.522</text>
<text x="303.8" y="225.2" font-size="12" fill="currentColor">Coppersmith-Winograd 1990: 2.376</text>
<text x="611.9" y="256.6" font-size="12" fill="currentColor" text-anchor="end">2025: 2.371339</text>
<text x="80.0" y="24.0" font-size="12" fill="currentColor">schoolbook: 3</text>
<text x="355" y="300" font-size="12" text-anchor="middle" fill="currentColor">year of publication; the lower bound omega &gt;= 2 lies below this window</text>
</svg>
<figcaption>Figure 25.2. Upper bounds on the matrix multiplication exponent. After the drop to 2.376 in 1990, three decades of work have gained about 0.004. Many researchers conjecture that the exponent is exactly 2.</figcaption>
</figure>

**Limits of the method.** Andris Ambainis, Yuval Filmus and François Le Gall (2015) proved that the laser method
applied to powers of the Coppersmith-Winograd tensor cannot give a bound below about 2.3078, and later work extended
such barriers to wider families of methods. So reaching $\omega = 2$, if it is true, will need a new idea; the
group-theoretic approach of Henry Cohn and Christopher Umans (2003) is one proposed route.

**Theory versus practice.** None of the post-Strassen algorithms is used in practice: their constant factors are
astronomically large, and they beat the schoolbook method only for matrices larger than any computer could hold.
Such methods are sometimes called **galactic algorithms**. Strassen's algorithm itself is used for large matrices
in some libraries, with a cutoff to the ordinary method for small blocks (exercise 5). The fastest practical matrix
code, like NumPy's backends (BLAS libraries such as OpenBLAS), uses the $n^3$ method with careful blocking for the
cache ([Chapter 24](24-Algorithms-for-Big-Data-and-Many-Processors.md)) and vector instructions.

## 25.4 Recent breakthroughs: maximum flow and negative-weight shortest paths

*Level: expert.*

Maximum flow ([Chapter 17](17-Spanning-Trees-Flows-and-Matching.md)) has been studied since Ford and Fulkerson's
1956 paper, through Edmonds-Karp's $O(VE^2)$ (1972), Dinic's blocking flows (1970), push-relabel (Goldberg and
Tarjan, 1988), Goldberg and Rao's $\tilde O(m \min(m^{1/2}, n^{2/3}) \log U)$ (1998) and James Orlin's $O(nm)$
(2013). (The tilde in $\tilde O$ hides logarithmic factors; $U$ is the largest capacity.) In 2022 the problem was
essentially closed:

**Theorem (Chen, Kyng, Liu, Peng, Probst Gutenberg and Sachdeva, FOCS 2022).** Maximum flow, and more generally
minimum-cost flow, on a directed graph with $m$ edges and integer capacities and costs bounded by $U$, can be solved
exactly in $m^{1 + o(1)} \log U$ time (randomized).

Here $m^{1+o(1)}$ means $m$ times a factor that grows more slowly than any power of $m$: "almost linear", not much
more than the time needed to read the graph. How does it work, in outline?

1. **Continuous optimisation.** Write min-cost flow as a linear program (Chapter 23) and solve it with an
   **interior point method**, which moves through the inside of the feasible region along a smooth path instead of
   along edges as simplex does. Their method is guided by a potential function and takes $m^{1+o(1)}$ steps, each
   a small change to the current flow.
2. **Each step is a graph problem.** The improving direction in each step turns out to be approximately a
   **minimum-ratio cycle**: a cycle in the graph minimising (cost of the cycle) / (length of the cycle) under the
   current weights. An approximate answer is good enough.
3. **A dynamic data structure.** The weights change only a little from step to step, so the authors built a data
   structure that maintains approximate minimum-ratio cycles under these changes in $m^{o(1)}$ amortized time per
   step, using a hierarchy of low-stretch spanning trees and decompositions of the graph.

The roots are in **spectral graph theory**: Daniel Spielman and Shang-Hua Teng's nearly-linear-time solvers for
Laplacian linear systems (2004) made "electrical flow" computations fast, which Christiano, Kelner, Mądry, Spielman
and Teng (2011) used for approximate max flow, starting the line of work that ended here. A deterministic version
followed (van den Brand and others, 2023). The algorithm is not practical yet; its importance is that it shows
max flow is, in principle, almost as easy as reading the input, and many problems that reduce to flow (bipartite
matching, Chapter 17's applications, some cuts) inherit the bound.

**Negative-weight shortest paths.** Dijkstra's algorithm ([Chapter 16](16-Shortest-Paths.md),
[reference page](../../graphs/dijkstra.md)) needs non-negative weights. With negative weights the textbook answer is
Bellman-Ford ([reference page](../../graphs/bellman-ford.md)), $O(nm)$ time, and scaling algorithms such as
Goldberg's (1995) gave $O(m\sqrt n \log W)$ for integer weights at least $-W$.

**Theorem (Bernstein, Nanongkai and Wulff-Nilsen, FOCS 2022).** Single-source shortest paths with integer weights
at least $-W$ can be computed in $O(m \log^8 n \log W)$ time (randomized, with high probability), or a negative
cycle reported.

The algorithm is purely combinatorial. Its main ingredients are **scaling** (handle the weights one bit at a
time, so that each phase only has to deal with weights at least $-1$), **potentials** (Johnson's reweighting from
[Chapter 16](16-Shortest-Paths.md): find a function $\phi$ on vertices such that $w(u,v) + \phi(u) - \phi(v) \ge 0$,
after which Dijkstra works), and **low-diameter decompositions** (cut the graph into pieces of small diameter by
removing few edges, solve recursively inside the pieces, then fix the paths that cross between pieces with a few
rounds of Bellman-Ford and Dijkstra combined). Karl Bringmann, Alejandro Cassis and Nick Fischer (2023) reduced the
logarithmic factors to $O(m \log^2 n \log(nW) \log\log n)$.

**Other recent results** worth knowing, each with its paper:

- Integer multiplication in $O(n \log n)$ bit operations (David Harvey and Joris van der Hoeven, *Annals of
  Mathematics*, 2021), the bound Schönhage and Strassen conjectured in 1971.
- Graph isomorphism in quasi-polynomial time $2^{O((\log n)^c)}$ (László Babai, STOC 2016).
- Metric TSP below $\tfrac32$ (Karlin, Klein and Oveis Gharan, STOC 2021; Chapter 23).
- Directed single-source shortest paths with real non-negative weights in $O(m \log^{2/3} n)$ time (Duan, Mao,
  Mao, Shu and Yin, STOC 2025), which beats Dijkstra with Fibonacci heaps on sparse graphs and shows that the
  "sorting barrier" is not a barrier for shortest paths.

## 25.5 Quantum algorithms: Grover and Shor

*Level: advanced.*

A classical bit is 0 or 1. A **qubit** is described by two complex numbers $(\alpha, \beta)$, its **amplitudes**,
with $|\alpha|^2 + |\beta|^2 = 1$; when measured it gives 0 with probability $|\alpha|^2$ and 1 with probability
$|\beta|^2$. A register of $n$ qubits is described by $N = 2^n$ amplitudes, one for each $n$-bit string, whose
squared magnitudes sum to 1. A quantum computation applies **unitary** transformations (linear maps that preserve
the sum of squared magnitudes) built from small gates, and finally measures. The appeal: one gate acting on one
qubit changes all $2^n$ amplitudes at once. The catch: measurement returns only **one** $n$-bit string, at random,
so the art is to make the amplitudes of wrong answers cancel and those of right answers reinforce. Simulating $n$
qubits on a classical computer takes $2^n$ numbers, which is why the programs below stop at small sizes.

**Grover's search (1996).** Given a black box $f : \{0, \dots, N-1\} \to \{0, 1\}$ with exactly one $w$ such that
$f(w) = 1$, find $w$. Classically you must try about $N/2$ inputs on average. Lov Grover's algorithm:

1. Start in the uniform state $|s\rangle$: every amplitude $1/\sqrt N$.
2. Repeat about $\frac{\pi}{4}\sqrt N$ times: (a) the **oracle** flips the sign of the amplitude of $w$; (b) the
   **diffusion** step replaces every amplitude $a_x$ by $2\bar a - a_x$, where $\bar a$ is the mean of all
   amplitudes (a reflection about the mean).
3. Measure.

**Theorem.** After $t$ iterations the probability of measuring $w$ is $\sin^2((2t+1)\theta)$, where
$\sin\theta = 1/\sqrt N$. With $t \approx \frac{\pi}{4}\sqrt N$ it is at least $1 - 1/N$.

*Proof.* All wrong answers always have equal amplitudes (both steps treat them alike), so the state lives in the
plane spanned by $|w\rangle$ and $|s'\rangle$, the uniform state over wrong answers. Write the state as
$\cos\phi\,|s'\rangle + \sin\phi\,|w\rangle$; initially $\sin\phi = 1/\sqrt N$, so $\phi = \theta$. The oracle
maps $\phi$ to $-\phi$: a reflection in the $|s'\rangle$ axis. The diffusion step is a reflection about
$|s\rangle$, which lies at angle $\theta$. Two reflections in lines at angle $\theta$ to each other make a
rotation by $2\theta$. So after $t$ iterations the angle is $(2t + 1)\theta$, and the probability of $w$ is
$\sin^2((2t+1)\theta)$. It reaches about 1 when $(2t + 1)\theta \approx \pi/2$, that is
$t \approx \pi/(4\theta) - 1/2 \approx \frac{\pi}{4}\sqrt N$, since $\theta \approx 1/\sqrt N$. $\square$

<figure class="mars-fig" markdown="0">
<svg viewBox="0 0 660 290" role="img" aria-label="Grover search as rotation: the state starts at angle theta above the wrong-answer axis and each iteration rotates it by 2 theta toward the answer axis; for N = 16 three iterations reach angle 7 theta, just past 90 degrees.">
<path d="M 450 250 A 200 200 0 0 0 190.9 58.9" fill="none" stroke="currentColor" stroke-opacity="0.4" stroke-dasharray="4 4"/>
<line x1="210" y1="250" x2="480" y2="250" stroke="currentColor" stroke-width="1.2"/>
<line x1="250" y1="270" x2="250" y2="30" stroke="currentColor" stroke-width="1.2"/>
<text x="484" y="254" font-size="13" fill="currentColor">wrong answers</text>
<text x="258" y="42" font-size="13" fill="currentColor">the answer</text>
<line x1="250" y1="250" x2="443.6" y2="200.0" stroke="#7ccf9a" stroke-width="3"/>
<circle cx="443.6" cy="200.0" r="4" fill="#7ccf9a" stroke="currentColor"/>
<text x="451.6" y="204.0" font-size="13" fill="currentColor" text-anchor="start">start: θ (P = 0.062)</text>
<line x1="250" y1="250" x2="395.2" y2="112.5" stroke="#9cc9ea" stroke-width="3"/>
<circle cx="395.2" cy="112.5" r="4" fill="#9cc9ea" stroke="currentColor"/>
<text x="403.2" y="116.5" font-size="13" fill="currentColor" text-anchor="start">1 step: 3θ (P = 0.473)</text>
<line x1="250" y1="250" x2="310.5" y2="59.4" stroke="#9cc9ea" stroke-width="3"/>
<circle cx="310.5" cy="59.4" r="4" fill="#9cc9ea" stroke="currentColor"/>
<text x="318.5" y="63.4" font-size="13" fill="currentColor" text-anchor="start">2 steps: 5θ (P = 0.908)</text>
<line x1="250" y1="250" x2="210.7" y2="53.9" stroke="#eea66f" stroke-width="3"/>
<circle cx="210.7" cy="53.9" r="4" fill="#eea66f" stroke="currentColor"/>
<text x="202.7" y="57.9" font-size="13" fill="currentColor" text-anchor="end">3 steps: 7θ (P = 0.961)</text>
<text x="20" y="150" font-size="13" fill="currentColor">N = 16, sin θ = 1/4,</text>
<text x="20" y="168" font-size="13" fill="currentColor">θ ≈ 14.5 degrees.</text>
<text x="20" y="186" font-size="13" fill="currentColor">P = chance of measuring</text>
<text x="20" y="204" font-size="13" fill="currentColor">the answer = sin² of the</text>
<text x="20" y="222" font-size="13" fill="currentColor">angle.</text>
</svg>
<figcaption>Figure 25.3. Grover's algorithm is a rotation in a plane. Each iteration turns the state by twice the small angle θ toward the answer; stop near 90 degrees, because further iterations rotate past it.</figcaption>
</figure>

**Shor's algorithm (1994).** Peter Shor showed that a quantum computer could factor an $n$-bit number in time
polynomial in $n$, and compute discrete logarithms too, breaking RSA and Diffie-Hellman
([cryptography.akadian.ca](https://cryptography.akadian.ca/book/)). The quantum part solves **order finding**:
given $N$ and $a$ with $\gcd(a, N) = 1$, find the smallest $r > 0$ with $a^r \equiv 1 \pmod N$. The rest is
classical number theory ([Chapter 19](19-Number-Theoretic-Algorithms.md)): if $r$ is even and
$a^{r/2} \not\equiv -1 \pmod N$, then $N$ divides $(a^{r/2} - 1)(a^{r/2} + 1)$ but neither factor, so
$\gcd(a^{r/2} - 1, N)$ is a proper factor. For odd $N$ with at least two distinct prime factors, a random $a$
works with probability at least $\tfrac12$ (a theorem from the structure of the multiplicative group; the proof
is in Nielsen and Chuang's book).

To find $r$, the quantum computer prepares a superposition of all $x < Q$ (with $Q$ a power of 2 near $N^2$),
computes $a^x \bmod N$ into a second register, and measures that register. The first register is left in a uniform
superposition over the $x$ with the same value of $a^x$, which form an arithmetic progression with difference $r$.
The **quantum Fourier transform**, the discrete Fourier transform of [Chapter 11](11-Divide-and-Conquer.md) carried
out on amplitudes with only $O(\log^2 Q)$ gates, turns a periodic state into one concentrated near multiples of
$Q/r$. Measuring gives some $k \approx jQ/r$; the continued fraction expansion of $k/Q$ reveals $r$ (or a divisor
of it). The program computes the actual output distribution for $N = 15$, $a = 7$:

```python
--8<-- "books/algorithms/ch25_quantum.py"
```

```
N =    16: best iteration count ~ (pi/4)sqrt(N) =  3, success probability there 0.9613; at twice that 0.0204; classical needs about N/2 = 8 guesses
N =   256: best iteration count ~ (pi/4)sqrt(N) = 13, success probability there 0.9862; at twice that 0.0297; classical needs about N/2 = 128 guesses
N =  1024: best iteration count ~ (pi/4)sqrt(N) = 25, success probability there 0.9995; at twice that 0.0002; classical needs about N/2 = 512 guesses

Shor, N = 15, a = 7: after measuring f(x) = 1, the register holds x in [0, 4, 8, 12, 16]...
  QFT output: nonzero probabilities only at [(0, 0.25), (64, 0.25), (128, 0.25), (192, 0.25)]
  measured k = 64: k/Q = 64/256 ~ 1/4, candidate order r = 4, check 7^4 mod 15 = 1
  measured k = 128: k/Q = 128/256 ~ 1/2, candidate order r = 2, check 7^2 mod 15 = 4
  measured k = 192: k/Q = 192/256 ~ 3/4, candidate order r = 4, check 7^4 mod 15 = 1
  r = 4 is even: gcd(7^2 - 1, 15) = 3, gcd(7^2 + 1, 15) = 5  ->  15 = 3 x 5
```

Here $r = 4$ divides $Q = 256$, so the peaks are exact: measuring $k = 64$ or $192$ reveals $r = 4$, $k = 128$ only
the divisor 2 (the check $7^2 \bmod 15 = 4 \ne 1$ catches it, and one repeats), and $k = 0$ nothing. For general
$r$ the peaks are spread a little, and the continued fraction step still recovers $r$ with good probability.

**What quantum computers do not do.** Three honest limits:

- **No exponential speed-up for brute-force search.** Bennett, Bernstein, Brassard and Vazirani (1997) proved that
  every quantum algorithm needs $\Omega(\sqrt N)$ oracle queries to find a marked item. So Grover is optimal, and
  a quantum computer cannot solve NP-complete problems by searching all $2^n$ certificates faster than about
  $2^{n/2}$. Whether the class BQP (efficient quantum computation) contains NP is unknown and widely doubted.
- **Not every problem has structure to exploit.** Shor's speed-up uses the hidden periodicity of $a^x \bmod N$.
  Factoring is in NP and in co-NP and not believed NP-complete. Known exponential speed-ups are for problems with
  such algebraic structure, and for simulating quantum physics itself, which was Richard Feynman's 1982
  motivation.
- **Hardware.** Running Shor on numbers of cryptographic size needs many error-corrected logical qubits. The
  famous demonstrations so far have factored very small numbers (15, by Vandersypen and colleagues with nuclear
  magnetic resonance, *Nature* 2001). Cryptographers are nonetheless moving to **post-quantum** schemes based on
  problems such as lattices, for which no quantum algorithm is known.

## 25.6 Learned algorithms and data structures

*Level: advanced.*

Worst-case analysis, the method of this whole book, protects against the worst input. Real inputs are rarely the
worst; they have patterns. Can an algorithm **learn** the patterns of its inputs and exploit them, while staying
safe when the patterns fail?

**Learned indexes.** Tim Kraska, Alex Beutel, Ed Chi, Jeffrey Dean and Neoklis Polyzotis ("The Case for Learned
Index Structures", SIGMOD 2018) observed that a sorted array with an index is a model of the **cumulative
distribution function** (CDF) of its keys: the position of key $x$ is $n \cdot F(x)$, where $F(x)$ is the fraction
of keys at most $x$. A B-tree is one way to compute this function; a learned model is another. Their **recursive
model index** uses a small model to choose among many tiny models, each predicting a position; the largest error
each one makes on the stored keys is recorded, so a lookup searches only the window $[\hat p - e, \hat p + e]$
around the prediction $\hat p$. Lookups are always correct; only their speed depends on how well the models fit.

The program builds a two-stage version with straight lines as models, on keys drawn from a skewed (lognormal)
distribution:

```python
--8<-- "books/algorithms/ch25_learned.py"
```

```
92729 distinct lognormal keys; 256 second-stage linear models
  model error: median 2, max 2153 positions
  probes per lookup: learned index 6.0, binary search 17

ski rental with predictions, B = 100
  lambda   worst ratio when prediction is right   worst ratio overall   1+lam   1+1/lam
   1.00                                   1.990                 1.990    2.00      2.00
   0.50                                   1.490                 2.990    1.50      3.00
   0.25                                   1.240                 4.960    1.25      5.00
   0.10                                   1.090                10.900    1.10     11.00
```

Look first at the learned index. Most of the 256 little models predict positions within 2 places,
so a lookup probes about 6 positions instead of binary search's 17; one model, in a region where keys are crowded,
is off by over 2000, and lookups there cost more. Honest caveats: our probe count ignores the cost of evaluating
the models, and careful benchmarks (Marcus and others, "Benchmarking Learned Indexes", VLDB 2020) found learned
indexes competitive with tuned B-trees and hash tables on read-only data, with the gains depending strongly on the
data. Later designs, such as the PGM-index of Paolo Ferragina and Giorgio Vinciguerra (2020), give provable
worst-case bounds by fitting piecewise linear models with a fixed maximum error.

**Algorithms with predictions.** A more general idea, sometimes called *learning-augmented algorithms*: give an
online algorithm (Chapter 24) a **prediction** about the future, from any source, without trusting it blindly. Two
measures replace the competitive ratio:

- **consistency:** the competitive ratio when the prediction is correct;
- **robustness:** the competitive ratio in the worst case, however wrong the prediction.

An ideal algorithm is near 1 when predictions are good and near the classical bound when they are bad.

**Ski rental with a prediction (Purohit, Svitkina and Kumar, NeurIPS 2018).** The prediction $y$ guesses the
number of skiing days. Fix a trust parameter $\lambda \in (0, 1]$. If $y \ge B$ (the prediction says "buy"), buy on
day $\lceil \lambda B \rceil$; otherwise buy on day $\lceil B / \lambda \rceil$.

**Theorem.** This algorithm is $(1 + \lambda)$-consistent and $(1 + 1/\lambda)$-robust.

*Proof.* Let $d$ be the true number of days, so $\mathrm{OPT} = \min(d, B)$. *Case $y \ge B$, buying on day
$t = \lceil \lambda B \rceil$.* If the prediction is right ($d \ge B \ge t$), we pay $t - 1 + B < \lambda B + B$
against $\mathrm{OPT} = B$: ratio below $1 + \lambda$. Whatever $d$ is, the worst case is $d = t$, where we pay
$t - 1 + B$ against $\min(t, B) = t$ (since $t \le B$): ratio $1 + (B-1)/t \le 1 + 1/\lambda$, as
$t \ge \lambda B$. *Case $y < B$, buying on day $t = \lceil B/\lambda \rceil \ge B$.* If the prediction is right
($d < B \le t$), we only rent and pay $d = \mathrm{OPT}$. In the worst case $d \ge t$, we pay $t - 1 + B$ against
$B$: ratio $(t - 1 + B)/B < (B/\lambda + B)/B = 1 + 1/\lambda$. $\square$

With $\lambda = 1$ this is the classical rent-or-buy (ratio 2 both ways). With $\lambda = 0.1$ a good prediction
gives ratio 1.1, and a terrible one costs at most 11. The table above shows the trade-off measured exactly. The same
idea has been applied to caching (Lykouris and Vassilvitskii, ICML 2018, which uses predicted next-request times to
imitate Belady's MIN), scheduling, and data structures; a survey is Mitzenmacher and Vassilvitskii's chapter
"Algorithms with Predictions" in *Beyond the Worst-Case Analysis of Algorithms* (Roughgarden, ed., 2021).

Learning also enters algorithms more directly. Modern SAT and integer-programming solvers (Chapter 23) use learned
rules for branching. Systems trained by reinforcement learning have discovered short sorting routines for small
inputs (Mankowitz and others, "Faster sorting algorithms discovered using deep reinforcement learning", *Nature*
2023) and the matrix multiplication schemes of 25.3. In each case the result is an ordinary algorithm that people
can read and check; the learning helped to search the space of algorithms.

## 25.7 Open problems, and how to keep learning

Here is a list of open problems from across this book, each labelled with its status as of this writing. Some are
famous; some are small enough that a new idea could settle them.

**Open, central and believed very hard:**

1. **P versus NP** (25.1). Believed $\mathrm{P} \ne \mathrm{NP}$; no proof.
2. **NP versus co-NP.** Is there always a short certificate that a formula is *unsatisfiable*? Believed no.
   Proving $\mathrm{NP} \ne \text{co-NP}$ would also prove $\mathrm{P} \ne \mathrm{NP}$, so it is at least as
   hard.
3. **P versus PSPACE.** Even this is unknown.
4. **Derandomization: P versus BPP.** Can every efficient randomized algorithm (Chapter 21) be made deterministic
   with polynomial slowdown? Believed yes, since Impagliazzo and Wigderson (1997) showed that plausible circuit lower
   bounds would imply it; a deterministic polynomial-time test for polynomial identities would be a major step.
   (Primality, a famous example, was derandomized by the AKS algorithm in 2002.)

**Open, about specific algorithms:**

5. **Is $\omega = 2$?** (25.3). Current bound 2.371339; known methods cannot pass about 2.3078 without new ideas.
6. **Linear programming in strongly polynomial time.** LP is in P, but all known polynomial algorithms take time
   depending on the number of bits in the input. Is there one whose number of arithmetic steps is polynomial in the
   number of variables and constraints alone? This is on Steve Smale's 1998 list of problems for the century. A
   related question: does some pivot rule make simplex polynomial (equivalently, a polynomial bound on the diameter
   of polytopes, the **polynomial Hirsch conjecture**)?
7. **Graph isomorphism in P?** Quasi-polynomial since Babai (2016); polynomial unknown.
8. **Factoring classically.** The best algorithm, the number field sieve, is sub-exponential. Its true complexity
   is unknown; it is not believed NP-complete.
9. **Metric TSP approximation.** The ratio is $\tfrac32 - 10^{-36}$; hardness is only $123/122$. The
   Held-Karp LP relaxation is conjectured to have integrality gap $\tfrac43$; an algorithm matching that would
   be a landmark.
10. **The Unique Games Conjecture** (Khot 2002, 23.6). If true, many simple approximation algorithms are optimal.
11. **The dynamic optimality conjecture** (Sleator and Tarjan, 1985). Splay trees (Chapters 8 and 21) are within a
    constant factor of the best binary search tree, even one that knows the access sequence in advance. Open for
    40 years; the best known online trees are $O(\log \log n)$-competitive (Tango trees, Demaine, Harmon, Iacono
    and Pătraşcu, 2004).
12. **Sorting integers in linear time.** On a word RAM, integers can be sorted in $O(n \sqrt{\log\log n})$
    expected time (Han and Thorup, 2002). Is $O(n)$ possible?
13. **The fine-grained conjectures** (25.2): 3SUM, APSP, SETH. Any of them could be false. Refuting SETH, in
    particular, would also give new circuit lower bounds, by results of Ryan Williams.
14. **Single-source shortest paths in linear time** for directed graphs with non-negative real weights, now that
    the $O(m + n \log n)$ "sorting barrier" has been broken (25.4).

**Recently solved (so you can see that problems do fall):** almost-linear max flow (2022), $O(n \log n)$ integer
multiplication (2019 preprint, 2021 paper), metric TSP below $\tfrac32$ (2021), negative-weight shortest paths
in near-linear time (2022), deterministic primality testing (2002), quasi-polynomial graph isomorphism (2016).

**How to keep learning.** You have the foundations. The next steps are:

- **Practise.** Programming contests train the craft of choosing and implementing algorithms quickly: the ICPC
  and IOI, and online judges with weekly contests. The reference pages of this site
  ([sorting](../../sorting/index.md), [graphs](../../graphs/index.md), [dynamic programming](../../dp/index.md),
  [strings](../../strings/index.md)) are a starting set to implement from memory.
- **Courses.** University courses with free lecture notes and videos, such as MIT's 6.006 (Introduction to
  Algorithms) and 6.046 (Design and Analysis of Algorithms) on MIT OpenCourseWare, and Tim Roughgarden's
  *Algorithms Illuminated* book series with its lectures.
- **Books.** For depth: CLRS; Kleinberg and Tardos; Dasgupta, Papadimitriou and Vazirani (*Algorithms*, 2006);
  Jeff Erickson's free *Algorithms* (2019); Arora and Barak for complexity; Williamson and Shmoys for
  approximation; Motwani and Raghavan for randomized algorithms; Nielsen and Chuang for quantum computing; Knuth's
  *The Art of Computer Programming* for everything, in the greatest detail.
- **Papers.** The main conferences are STOC, FOCS, SODA and ICALP; nearly every paper appears first on arXiv in
  the category cs.DS (data structures and algorithms) or cs.CC (computational complexity). Read the introductions
  first: they say what was known, what is new and why it matters, which is exactly the habit this book has tried
  to build.
- **The other books on this shelf.** The [Machine learning book](../machine-learning/index.md) and the
  [Artificial intelligence book](../index.md) take the algorithms of this book, optimisation, search, dynamic
  programming and probability, and build learning and reasoning systems from them; the search and planning that
  let a rover like Perseverance pick its own path across Jezero crater are there too.

## Check yourself

??? question "1. Explain in two sentences why the time hierarchy theorem implies that at least one of P ⊆ NP, NP ⊆ PSPACE, PSPACE ⊆ EXPTIME is a strict inclusion."
    The chain $\mathrm{P} \subseteq \mathrm{NP} \subseteq \mathrm{PSPACE} \subseteq \mathrm{EXPTIME}$ is proved,
    and the hierarchy theorem proves $\mathrm{P} \ne \mathrm{EXPTIME}$. If all three inclusions were equalities,
    P would equal EXPTIME, a contradiction, so at least one is strict, though we do not know which.

??? question "2. Why does a proof that P ≠ NP need to be non-relativizing? What exactly would go wrong with a proof by pure diagonalization?"
    Diagonalization treats machines as black boxes that it simulates and contradicts; the same argument works word
    for word if every machine also has access to an oracle $A$. So a diagonal proof of $\mathrm{P} \ne \mathrm{NP}$
    would also prove $\mathrm{P}^A \ne \mathrm{NP}^A$ for every $A$. But Baker, Gill and Solovay built an oracle
    (any PSPACE-complete language) for which $\mathrm{P}^A = \mathrm{NP}^A$. So such a proof cannot exist.

??? question "3. Write the code: solve 3SUM with a hash set in O(n^2) expected time, and say why this does not contradict the 3SUM conjecture."
    ```python
    def three_sum_hash(a):
        seen = {}
        for i, x in enumerate(a):
            seen.setdefault(x, []).append(i)
        for i in range(len(a)):
            for j in range(i + 1, len(a)):
                need = -(a[i] + a[j])
                for k in seen.get(need, []):
                    if k > j:
                        return a[i], a[j], a[k]
        return None

    print(three_sum_hash([5, -7, 13, 2, -3, 8]))   # (5, -7, 2)
    print(three_sum_hash([1, 3, 5, 7]))            # None
    ```
    It still takes about $n^2/2$ pair checks, so it is quadratic; the conjecture says no algorithm is
    $O(n^{2-\delta})$, and this one is not.

??? question "4. In the SAT-to-OV reduction, a formula has n = 40 variables and m = 200 clauses. How many vectors are there, of what dimension, and what would an O(N^1.9) OV algorithm give for SAT?"
    Each half has 20 variables, so each list has $N = 2^{20} \approx 10^6$ vectors of dimension 200. An
    $O(N^{1.9}\,\mathrm{poly}(d))$ algorithm would decide satisfiability in about
    $(2^{20})^{1.9} = 2^{38}$ steps times $\mathrm{poly}(200)$, instead of $2^{40}$; in general
    $2^{0.95 n}\mathrm{poly}(m)$, which (with sparsification for $k$-SAT) would refute SETH.

??? question "5. Strassen's recursion is faster in theory, but practical codes stop recursing at blocks of size about 64 to 512. Write T(n) for 'recurse with Strassen down to size c, then use the schoolbook method' counting multiplications, and compute it for n = 1024 with c = 1, 64 and 1024."
    With $n = 2^k$ and $c = 2^j$, there are $7^{k-j}$ base blocks, each costing $c^3$:
    $T = 7^{k-j} \cdot 8^{j}$. For $n = 1024$ ($k = 10$): $c = 1$ gives $7^{10} = 282{,}475{,}249$; $c = 64$ gives
    $7^4 \cdot 8^6 = 2401 \cdot 262{,}144 = 629{,}407{,}744$; $c = 1024$ gives $8^{10} = 1{,}073{,}741{,}824$.
    Counting only multiplications, recursing all the way is best; but each Strassen level adds 18 additions of
    half-size blocks and extra memory traffic, so in real code the cutoff wins for small blocks.

??? question "6. Show that if 3 x 3 matrices could be multiplied with 21 multiplications, omega would be below Strassen's bound, while 22 would not suffice."
    The exponent from a $k \times k$ scheme with $r$ products is $\log_k r$. $\log_3 21 = \ln 21 / \ln 3 \approx
    3.0445/1.0986 \approx 2.771 < 2.807$, but $\log_3 22 \approx 3.0910/1.0986 \approx 2.814 > 2.807$. So 21
    products would beat Strassen; 22 would not.

??? question "7. For Grover's algorithm with N = 64, how many iterations should you use, and what is the success probability? What happens if you use twice as many?"
    $\sin\theta = 1/8$, so $\theta \approx 0.1253$ radians. $t = \text{round}(\frac{\pi}{4} \cdot 8) = 6$:
    angle $13\theta \approx 1.629$ radians, probability $\sin^2(1.629) \approx 0.9966$. With 12 iterations the angle
    is $25\theta \approx 3.133$, almost $\pi$, and the probability $\sin^2(3.133) \approx 0.0001$: the state has
    rotated past the answer and back to near the start.

??? question "8. Factor 21 by Shor's classical post-processing: take a = 2, find its order mod 21 by hand, and use it."
    Powers of 2 mod 21: 2, 4, 8, 16, 11, 1. So $r = 6$, which is even. $a^{r/2} = 2^3 = 8$, and
    $8 \not\equiv -1 \pmod{21}$. Then $\gcd(8 - 1, 21) = \gcd(7, 21) = 7$ and $\gcd(8 + 1, 21) = \gcd(9, 21) = 3$:
    $21 = 3 \times 7$.

??? question "9. Why does Grover's algorithm not show that NP-complete problems are easy for quantum computers?"
    Searching all $2^n$ assignments of a SAT formula with Grover takes about $2^{n/2}$ steps: a quadratic speed-up,
    still exponential. Bennett, Bernstein, Brassard and Vazirani proved that no quantum algorithm treating the
    formula as a black box can do better than $\Omega(\sqrt{2^n})$. A polynomial quantum algorithm for SAT would need
    to exploit the structure of formulas, and none is known.

??? question "10. In the ski-rental-with-predictions algorithm, a user picks lambda = 0.2. What are the consistency and robustness? If predictions are right 90 percent of the time, roughly what is the worst expected ratio (assume when wrong the worst case happens)?"
    Consistency $1 + 0.2 = 1.2$, robustness $1 + 1/0.2 = 6$. With right predictions 90 percent of the time and the
    worst case otherwise, the expected ratio is at most about $0.9 \times 1.2 + 0.1 \times 6 = 1.68$, better than the
    deterministic 2 but worse than trusting moderately: with $\lambda = 0.5$, $0.9 \times 1.5 + 0.1 \times 3 = 1.65$.
    (This is a rough guide: the ratio of expectations is not the expectation of ratios, but it shows the trade-off.)

??? question "11. Write the code: a learned index with a single linear model for all keys. Measure its maximum error on keys 0, 10, 20, ... (uniform) and on squares 0, 1, 4, 9, ... and explain the difference."
    ```python
    def fit(keys):
        n = len(keys)
        mx, my = sum(keys) / n, (n - 1) / 2
        a = sum((k - mx) * (i - my) for i, k in enumerate(keys)) / sum((k - mx) ** 2 for k in keys)
        b = my - a * mx
        return max(abs(round(a * k + b) - i) for i, k in enumerate(keys))

    print(fit([10 * i for i in range(1000)]))   # 0
    print(fit([i * i for i in range(1000)]))    # 187
    ```
    Evenly spaced keys have a straight-line CDF, so one line predicts every position exactly. Squares have a CDF
    shaped like a square root, which a single line fits badly (the error here is 187 positions out of 1000); this
    is why learned indexes use many small models, each fitting a nearly straight piece.

## What you learned

- P versus NP is open; what is proved is $\mathrm{P} \ne \mathrm{EXPTIME}$, lower bounds for restricted circuits,
  and three barriers (relativization, natural proofs, algebrization) that rule out the familiar proof methods.
- Fine-grained complexity relates exponents inside P through a few conjectures (3SUM, APSP, SETH); under SETH, edit
  distance and LCS need quadratic time, via orthogonal vectors.
- The matrix multiplication exponent is between 2 and 2.371339; the gains since 1990 are tiny and current methods
  have proven limits; the record-holding algorithms are galactic.
- Max flow and min-cost flow now run in almost-linear time, and shortest paths with negative weights in near-linear
  time, by combining continuous optimisation, graph decompositions and data structures.
- Grover gives a quadratic speed-up for search, which is optimal; Shor factors in polynomial time by finding a
  period with the quantum Fourier transform; neither makes NP-complete problems easy.
- Learned indexes and learning-augmented algorithms use predictions for speed while keeping worst-case guarantees,
  measured by consistency and robustness.
- Many natural problems remain open, and several old ones have fallen in the last few years.

**Next:** this is the last chapter. Return to the [book's contents](index.md) to revisit any part, or continue with
the [Machine learning book](../machine-learning/index.md).

## Further reading

- S. Cook, "The complexity of theorem-proving procedures", STOC 1971; S. Aaronson, "P =? NP", in *Open Problems in
  Mathematics* (Nash and Rassias, eds.), 2016, a long and careful survey.
- T. Baker, J. Gill and R. Solovay, "Relativizations of the P =? NP question", *SIAM Journal on Computing* 4, 1975;
  A. Razborov and S. Rudich, "Natural proofs", *JCSS* 55, 1997; S. Aaronson and A. Wigderson, "Algebrization: a new
  barrier in complexity theory", STOC 2008.
- R. Williams, "Non-uniform ACC circuit lower bounds", CCC 2011 (journal version in *Journal of the ACM*, 2014).
- R. Impagliazzo and R. Paturi, "On the complexity of k-SAT", *JCSS* 62, 2001; R. Williams, "A new algorithm for
  optimal 2-constraint satisfaction and its implications", *Theoretical Computer Science* 348, 2005.
- A. Backurs and P. Indyk, "Edit distance cannot be computed in strongly subquadratic time (unless SETH is false)",
  STOC 2015; V. Vassilevska Williams, "On some fine-grained questions in algorithms and complexity", Proceedings
  of the ICM 2018.
- V. Strassen, "Gaussian elimination is not optimal", *Numerische Mathematik* 13, 1969; D. Coppersmith and
  S. Winograd, "Matrix multiplication via arithmetic progressions", *Journal of Symbolic Computation* 9, 1990;
  J. Alman, R. Duan, V. Vassilevska Williams, Y. Xu, Z. Xu and R. Zhou, "More asymmetry yields faster matrix
  multiplication", SODA 2025.
- L. Chen, R. Kyng, Y. P. Liu, R. Peng, M. Probst Gutenberg and S. Sachdeva, "Maximum flow and minimum-cost flow in
  almost-linear time", FOCS 2022.
- A. Bernstein, D. Nanongkai and C. Wulff-Nilsen, "Negative-weight single-source shortest paths in near-linear
  time", FOCS 2022.
- L. K. Grover, "A fast quantum mechanical algorithm for database search", STOC 1996; P. W. Shor, "Algorithms for
  quantum computation: discrete logarithms and factoring", FOCS 1994; M. A. Nielsen and I. L. Chuang, *Quantum
  Computation and Quantum Information*, 2000.
- T. Kraska, A. Beutel, E. H. Chi, J. Dean and N. Polyzotis, "The case for learned index structures", SIGMOD 2018;
  M. Purohit, Z. Svitkina and R. Kumar, "Improving online algorithms via ML predictions", NeurIPS 2018;
  T. Roughgarden (ed.), *Beyond the Worst-Case Analysis of Algorithms*, 2021.
- On this site: [Chapter 22](22-NP-Completeness.md), [Chapter 23](23-Approximation-and-Parameterized-Algorithms.md),
  [Chapter 24](24-Algorithms-for-Big-Data-and-Many-Processors.md), [edit distance](../../dp/edit-distance.md),
  [Dijkstra](../../graphs/dijkstra.md), [Bellman-Ford](../../graphs/bellman-ford.md);
  [cryptography.akadian.ca/book](https://cryptography.akadian.ca/book/) for what Shor's algorithm means for RSA.
