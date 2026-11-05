# 23. Approximation and parameterized algorithms

*Chapter 22 ended with bad news: vertex cover, the travelling salesman, set cover and knapsack are NP-hard, so
unless P = NP no algorithm solves every instance exactly in polynomial time. Yet delivery companies route trucks,
chip makers place components and schedulers fill timetables every day. They do it by giving up one of three
things: exactness (take an answer that is provably close to the best), generality (exploit the fact that some
number in the input is small), or the guarantee (use a heuristic that is usually excellent). In this chapter you
will build each kind from scratch, prove how close the approximations come, see the theorem that says some
problems cannot even be approximated, and meet the solvers that industry actually runs.*

!!! abstract "In this chapter"
    **You will learn:**

    - what an approximation ratio is, and how a lower bound on the optimum makes a proof possible
    - a 2-approximation for vertex cover, and 2 and 1.5 for the metric travelling salesman (Christofides)
    - why greedy set cover is within a factor $H_n \approx \ln n$ of optimal, and why that is close to the best possible
    - how rounding profits turns the knapsack dynamic program into an FPTAS
    - linear programming: the simplex method built by hand, duality, and LP relaxation with rounding
    - what the PCP theorem says about the limits of approximation
    - fixed-parameter algorithms and kernels: vertex cover in $O(2^k m)$
    - how local search, SAT solvers and integer programming solvers attack NP-hard problems in practice

    **You need:** [Chapter 22](22-NP-Completeness.md) (NP-hardness, reductions),
    [Chapter 12](12-Greedy-Algorithms.md) (greedy and exchange arguments),
    [Chapter 13](13-Dynamic-Programming.md) (knapsack, Held-Karp),
    [Chapter 17](17-Spanning-Trees-Flows-and-Matching.md) (minimum spanning trees, matchings) and
    [Chapter 15](15-Graphs-and-Graph-Search.md) (Euler tours). A little linear algebra helps for 23.5
    ([math.akadian.ca books](https://math.akadian.ca/books/)).

    **Levels:** 23.1 to 23.4 are intermediate; 23.5 is intermediate to advanced; 23.6 and 23.7 are advanced;
    23.8 is intermediate.

## 23.1 Approximation ratio; vertex cover 2-approximation

Suppose a museum has corridors that meet at junctions, and you must place guards at junctions so that every
corridor has a guard at one of its ends. Guards cost money, so you want as few as possible. In graph words: given a
graph $G = (V, E)$, a **vertex cover** is a set $C \subseteq V$ such that every edge has at least one end in $C$.
Finding the smallest vertex cover is NP-hard ([Chapter 22](22-NP-Completeness.md) reduced independent set to it).

What can we promise instead? An algorithm for a minimisation problem is a **$\rho$-approximation** (read "rho")
if it runs in polynomial time and, on every input, returns a solution whose cost is at most $\rho$ times the cost of
the best solution, written $\mathrm{OPT}$:

$$
\mathrm{ALG}(I) \le \rho \cdot \mathrm{OPT}(I) \quad \text{for every input } I .
$$

For a maximisation problem the promise is $\mathrm{ALG}(I) \ge \rho \cdot \mathrm{OPT}(I)$ with $\rho \le 1$
(some books write $1/\rho$ instead, so that the ratio is always at least 1). The number $\rho$ is the
**approximation ratio** or **performance guarantee**. It is a worst-case promise: like a running time bound, it must
hold for every input, including ones built by an enemy.

Here is the puzzle every approximation proof must solve. We cannot compute $\mathrm{OPT}$; that is the whole
problem. So how can we compare our answer with it? The trick is always the same: find a quantity that is **easy to
compute** and that is **provably at most $\mathrm{OPT}$** (a *lower bound* for a minimisation problem). Then show
that our answer is at most $\rho$ times that quantity.

For vertex cover the lower bound is a matching. A **matching** is a set of edges no two of which share an end.

**Lemma.** If $M$ is any matching in $G$, then every vertex cover has at least $|M|$ vertices.

*Proof.* Each edge of $M$ needs one of its ends in the cover. The edges of $M$ have no ends in common, so no single
vertex can serve two of them. Hence the cover contains at least $|M|$ different vertices. $\square$

A matching is **maximal** if no edge can be added to it, that is, every edge of $G$ shares an end with some edge of
$M$. (Maximal is weaker than *maximum*, which means largest possible. A maximal matching is found greedily in one
pass; a maximum one needs the machinery of [Chapter 17](17-Spanning-Trees-Flows-and-Matching.md).)

**Algorithm (matching cover).** Go through the edges in any order. If neither end of the edge is in $C$ yet, add
both ends to $C$.

**Theorem.** The matching cover is a vertex cover with $|C| \le 2\,\mathrm{OPT}$, found in $O(|V| + |E|)$ time.

*Proof.* *It is a cover:* when the algorithm looks at an edge, either one of its ends is already in $C$, or it adds
both. Either way the edge ends up covered, and $C$ only grows. *It is small:* the edges for which we added both ends
form a matching $M$, because we only took an edge when both its ends were still unused. So $|C| = 2|M|$, and by the
lemma $|M| \le \mathrm{OPT}$. Hence $|C| = 2|M| \le 2\,\mathrm{OPT}$. *Time:* one pass over the edges with a
set (or boolean array) for $C$. $\square$

Let us trace it on a small graph with six junctions. The edges are $01, 02, 13, 23, 34, 45$.

| edge looked at | ends already in $C$? | action | $C$ after |
|---|---|---|---|
| 01 | neither | take 0 and 1 | {0, 1} |
| 02 | 0 | skip | {0, 1} |
| 13 | 1 | skip | {0, 1} |
| 23 | neither | take 2 and 3 | {0, 1, 2, 3} |
| 34 | 3 | skip | {0, 1, 2, 3} |
| 45 | neither | take 4 and 5 | {0, 1, 2, 3, 4, 5} |

The matching is $\{01, 23, 45\}$, so $\mathrm{OPT} \ge 3$, and the algorithm returns all six vertices. The best
cover is $\{0, 3, 4\}$ of size 3: on this graph the algorithm is exactly a factor 2 off, the worst the theorem
allows. Figure 23.1 shows both.

<figure class="mars-fig" markdown="0">
<svg viewBox="0 0 660 230" role="img" aria-label="Two copies of the same six-vertex graph. Left: the matching edges 01, 23 and 45 are thick and all six vertices are in the cover. Right: the optimal cover 0, 3, 4 is shaded green.">
<text x="165" y="24" font-size="14" text-anchor="middle" fill="currentColor">matching cover: 6 vertices</text>
<text x="495" y="24" font-size="14" text-anchor="middle" fill="currentColor">optimal cover: 3 vertices</text>
<g stroke="currentColor" stroke-width="1.5">
<line x1="40" y1="70" x2="130" y2="70" stroke="#eea66f" stroke-width="6"/>
<line x1="40" y1="70" x2="40" y2="160"/>
<line x1="130" y1="70" x2="130" y2="160"/>
<line x1="40" y1="160" x2="130" y2="160" stroke="#eea66f" stroke-width="6"/>
<line x1="130" y1="160" x2="210" y2="160"/>
<line x1="210" y1="160" x2="290" y2="160" stroke="#eea66f" stroke-width="6"/>
<line x1="370" y1="70" x2="460" y2="70"/>
<line x1="370" y1="70" x2="370" y2="160"/>
<line x1="460" y1="70" x2="460" y2="160"/>
<line x1="370" y1="160" x2="460" y2="160"/>
<line x1="460" y1="160" x2="540" y2="160"/>
<line x1="540" y1="160" x2="620" y2="160"/>
</g>
<g stroke="currentColor" stroke-width="1.5">
<circle cx="40" cy="70" r="16" fill="#9cc9ea"/>
<circle cx="130" cy="70" r="16" fill="#9cc9ea"/>
<circle cx="40" cy="160" r="16" fill="#9cc9ea"/>
<circle cx="130" cy="160" r="16" fill="#9cc9ea"/>
<circle cx="210" cy="160" r="16" fill="#9cc9ea"/>
<circle cx="290" cy="160" r="16" fill="#9cc9ea"/>
<circle cx="370" cy="70" r="16" fill="#7ccf9a"/>
<circle cx="460" cy="70" r="16" fill="none"/>
<circle cx="370" cy="160" r="16" fill="none"/>
<circle cx="460" cy="160" r="16" fill="#7ccf9a"/>
<circle cx="540" cy="160" r="16" fill="#7ccf9a"/>
<circle cx="620" cy="160" r="16" fill="none"/>
</g>
<g font-size="14" text-anchor="middle" fill="currentColor">
<text x="40" y="75">0</text><text x="130" y="75">1</text><text x="40" y="165">2</text>
<text x="130" y="165">3</text><text x="210" y="165">4</text><text x="290" y="165">5</text>
<text x="370" y="75">0</text><text x="460" y="75">1</text><text x="370" y="165">2</text>
<text x="460" y="165">3</text><text x="540" y="165">4</text><text x="620" y="165">5</text>
</g>
<text x="165" y="210" font-size="12" text-anchor="middle" fill="currentColor">thick edges: the matching M, so OPT is at least 3</text>
<text x="495" y="210" font-size="12" text-anchor="middle" fill="currentColor">green: {0, 3, 4} touches every edge</text>
</svg>
<figcaption>Figure 23.1. The matching cover takes both ends of each matching edge. The matching proves that no cover can have fewer than 3 vertices, so 6 is at most twice the optimum.</figcaption>
</figure>

The program below runs the algorithm, checks it against the exact answer found by trying every subset, and ends
with the simplest tight example: a graph that is itself a perfect matching of $k$ edges, where the algorithm takes
$2k$ vertices and $k$ suffice.

```python
--8<-- "books/algorithms/ch23_vertex_cover.py"
```

```
example edges: [(0, 1), (0, 2), (1, 3), (2, 3), (3, 4), (4, 5)]
matching picked: [(0, 1), (2, 3), (4, 5)]
approx cover: [0, 1, 2, 3, 4, 5] size 6
optimal cover: [0, 3, 4] size 3

 n   edges  approx  optimal  ratio
14     28      12        8   1.50
10     15       8        5   1.60
11     17       8        5   1.60
 8     12       6        5   1.20
13     19      12        6   2.00
13     20      10        7   1.43
14     24      14        8   1.75
10     15      10        5   2.00
worst ratio seen: 2.0 (the theorem promises at most 2)

perfect matching of 5 edges: approx 10, optimal 5, ratio 2.0
```

Two lessons hide in this small result. First, the analysis is **tight**: there are inputs where the ratio really is
2, so no cleverer proof can show the same algorithm does better. Second, the obvious greedy idea, "repeatedly take
the vertex that covers the most uncovered edges", sounds better but is worse: on specially built bipartite graphs
its ratio grows like $\ln n$ (exercise 4 hints at the construction). Intuition about "smart" choices is not a
proof; the dumb-looking matching cover has the better guarantee.

**A little history.** Ronald Graham's 1966 analysis of list scheduling, which showed that a simple rule for
assigning jobs to $m$ machines finishes within a factor $2 - 1/m$ of the best possible, is usually named as the
first approximation guarantee. The idea became a field after David Johnson's 1974 paper "Approximation algorithms
for combinatorial problems", written just after Cook's and Karp's NP-completeness results: once exact answers were
believed out of reach, the natural question became how close one could get. The matching cover for vertex cover is usually
credited to Fănică Gavril and Mihalis Yannakakis.

<figure class="play" data-play="vcover"><span class="ai-tag">AI-created</span><figcaption>Try it: the 2-approximation on a small made-up graph. Each uncovered edge puts both its ends in the cover.</figcaption></figure>

## 23.2 Metric TSP: MST doubling and Christofides

The **travelling salesman problem** (TSP) asks for the shortest closed tour that visits each of $n$ cities exactly
once. A Mars rover with a list of rock targets for the day faces a small version: in which order should it drive
to them? For a dozen targets the exact Held-Karp algorithm of [Chapter 13](13-Dynamic-Programming.md) is fine; for
thousands it is not.

Without any assumption on the distances, TSP cannot be approximated at all (we prove this in 23.6). So we assume
the distances are a **metric**: $d(u, v) \ge 0$, $d(u, v) = d(v, u)$, and the **triangle inequality**
$d(u, w) \le d(u, v) + d(v, w)$ holds: going straight is never longer than a detour. Driving distances and
straight-line distances on a map both satisfy it. The triangle inequality gives us the key tool, **shortcutting**:
if a walk visits $u$, then some cities already seen, then $w$, we may jump from $u$ straight to $w$ without making
the walk longer.

**The lower bound.** Delete any one edge from an optimal tour. What is left is a path through all cities, which is
a spanning tree. So the minimum spanning tree $T$ ([Chapter 17](17-Spanning-Trees-Flows-and-Matching.md),
[Prim](../../graphs/prim.md), [Kruskal](../../graphs/kruskal.md)) satisfies

$$
w(T) \le \mathrm{OPT} .
$$

**The double-tree algorithm.** Compute $T$. Walk around it, going down every edge and back up again, as if tracing
the outline of the tree with a pencil: this closed walk uses every tree edge twice and has length $2w(T)$. Now list
the cities in the order the walk first meets them (this is a preorder traversal of $T$) and visit them in that
order, skipping repeats. By the triangle inequality each skip is no longer than the part of the walk it replaces, so

$$
\mathrm{ALG} \le 2 w(T) \le 2\,\mathrm{OPT} .
$$

Prim's algorithm on a complete graph takes $O(n^2)$ time and the walk $O(n)$, so the whole algorithm is $O(n^2)$.

<figure class="mars-fig" markdown="0">
<svg viewBox="0 0 660 250" role="img" aria-label="A spanning tree with root A, children B and C, B's children D and E, and C's child F. A dashed tour A, B, D, E, C, F, A follows tree edges where it can and takes shortcuts D to E, E to C and F to A.">
<g stroke="#9cc9ea" stroke-width="9" stroke-linecap="round">
<line x1="330" y1="45" x2="200" y2="115"/>
<line x1="330" y1="45" x2="460" y2="115"/>
<line x1="200" y1="115" x2="130" y2="195"/>
<line x1="200" y1="115" x2="270" y2="195"/>
<line x1="460" y1="115" x2="460" y2="195"/>
</g>
<g stroke="#eea66f" stroke-width="2.5" stroke-dasharray="7 5" fill="none">
<line x1="330" y1="45" x2="200" y2="115"/>
<line x1="200" y1="115" x2="130" y2="195"/>
<line x1="130" y1="195" x2="270" y2="195"/>
<line x1="270" y1="195" x2="460" y2="115"/>
<line x1="460" y1="115" x2="460" y2="195"/>
<path d="M 460 195 Q 600 120 330 45"/>
</g>
<g stroke="currentColor" stroke-width="1.5">
<circle cx="330" cy="45" r="17" fill="#7ccf9a"/>
<circle cx="200" cy="115" r="17" fill="#7ccf9a"/>
<circle cx="460" cy="115" r="17" fill="#7ccf9a"/>
<circle cx="130" cy="195" r="17" fill="#7ccf9a"/>
<circle cx="270" cy="195" r="17" fill="#7ccf9a"/>
<circle cx="460" cy="195" r="17" fill="#7ccf9a"/>
</g>
<g font-size="14" text-anchor="middle" fill="currentColor">
<text x="330" y="50">A</text><text x="200" y="120">B</text><text x="460" y="120">C</text>
<text x="130" y="200">D</text><text x="270" y="200">E</text><text x="460" y="200">F</text>
</g>
<text x="20" y="232" font-size="12" fill="currentColor">wide blue: tree T; walk around it: A B D B E B A C F C A (length 2w(T))</text>
<text x="20" y="248" font-size="12" fill="currentColor">dashed orange: shortcut tour A B D E C F A; D-E, E-C and F-A replace longer pieces of the walk</text>
</svg>
<figcaption>Figure 23.2. The double-tree algorithm. The full walk around the tree costs twice the tree; skipping cities already seen can only shorten it, by the triangle inequality.</figcaption>
</figure>

A tiny check by hand: four cities at the corners of a 4 by 3 rectangle, $(0,0), (4,0), (4,3), (0,3)$. The MST
takes the two sides of length 3 and one side of length 4, total 10. The preorder from city 0 is $0, 1, 2, 3$, a
tour of length $4 + 3 + 4 + 3 = 14$, which here is optimal; the bound promised at most 20.

**Christofides' improvement.** The walk around the tree uses every edge twice because we needed a closed walk using
every tree edge, and a graph has a closed walk using each edge exactly once (an **Euler circuit**,
[Chapter 15](15-Graphs-and-Graph-Search.md)) exactly when it is connected and every vertex has even degree.
Doubling all edges makes all degrees even, but that is wasteful: only the vertices of **odd** degree in $T$ need
fixing. Nicos Christofides' 1976 algorithm (found independently by Anatoliy Serdyukov, published 1978) fixes only
those:

1. Compute the MST $T$.
2. Let $O$ be the set of vertices with odd degree in $T$. ($|O|$ is even, since the degrees of any graph add up to
   twice the number of edges.)
3. Find a minimum-weight **perfect matching** $M$ on $O$: pair up the vertices of $O$ so that the total length of the
   pairs is as small as possible.
4. $T \cup M$ (keeping both copies if an edge is in both) has all degrees even. Find an Euler circuit of it.
5. Shortcut the circuit to a tour.

**Theorem (Christofides 1976).** For metric TSP the tour has length at most $\tfrac{3}{2}\,\mathrm{OPT}$.

*Proof.* We already know $w(T) \le \mathrm{OPT}$. We show $w(M) \le \tfrac12 \mathrm{OPT}$. Take an optimal tour
and shortcut it so that it visits only the vertices of $O$, in the same cyclic order; by the triangle inequality the
result, a cycle through the $|O|$ odd vertices, has length at most $\mathrm{OPT}$. Its edges, taken alternately,
form two perfect matchings of $O$ (this works because $|O|$ is even). Their lengths add up to at most
$\mathrm{OPT}$, so the shorter one has length at most $\tfrac12\mathrm{OPT}$, and the minimum perfect matching $M$
is no longer than that. Every vertex of $T \cup M$ has even degree (odd vertices got exactly one matching edge), and
$T \cup M$ is connected because $T$ is, so an Euler circuit exists and has length
$w(T) + w(M) \le \tfrac32\mathrm{OPT}$. Shortcutting does not increase it. $\square$

Minimum-weight perfect matching in a general graph is polynomial (Edmonds' blossom algorithm, 1965), in
$O(n^3)$ time with the standard implementations, so Christofides runs in $O(n^3)$. In our program the odd vertices
are few, so a bitmask dynamic program over subsets finds the matching exactly; that keeps the code short.

The program also runs **2-opt**, a local search we meet in 23.8: repeatedly look for two edges $ab$ and $ce$ of
the tour whose replacement by $ac$ and $be$ (reversing the stretch between them) makes the tour shorter. It has no
useful worst-case guarantee, but on small random instances it often lands on the optimum.

```python
--8<-- "books/algorithms/ch23_tsp.py"
```

```
  n   optimal  double-tree  christofides   2-opt(from DT)  odd
 12     296.5   369.2 (1.25)   312.4 (1.05)    296.5 (1.00)    4
 12     325.8   331.6 (1.02)   336.4 (1.03)    325.8 (1.00)    4
 12     325.4   412.4 (1.27)   344.1 (1.06)    325.4 (1.00)    6
 12     269.0   282.1 (1.05)   287.3 (1.07)    269.0 (1.00)    4
 12     269.9   353.8 (1.31)   308.8 (1.14)    269.9 (1.00)    8
 12     318.4   409.4 (1.29)   322.5 (1.01)    318.4 (1.00)    4

rectangle 4 x 3: MST edges [(0, 3), (0, 1), (1, 2)] weight 10.0
double-tree tour [0, 1, 2, 3] length 14.0
optimal length 14.0
```

Notice three honest things in this table. The guarantees hold (all double-tree ratios are below 2 and all
Christofides ratios below 1.5), but on random points both algorithms do far better than their guarantees, which
are about the worst case. Christofides is not always better than double-tree on a given instance (row 2), only in
the worst case. And the guarantee-free local search beats both here, which is why practical TSP codes use local
search, with approximation algorithms as starting points or as safety nets.

For 45 years nobody improved $\tfrac32$ for general metric TSP. In 2021 Anna Karlin, Nathan Klein and Shayan Oveis
Gharan gave a randomized algorithm with ratio $\tfrac32 - \varepsilon$ for a tiny fixed $\varepsilon$ (their paper
gives $\varepsilon > 10^{-36}$). The improvement is minute, but it broke a barrier many thought might be the truth.
For points in the plane with straight-line distances, Sanjeev Arora (1998) and Joseph Mitchell (1999) independently
found a **PTAS** (defined in 23.4): ratio $1 + \varepsilon$ for any fixed $\varepsilon > 0$.

## 23.3 Set cover: the greedy $H_n$ bound

A space agency wants to photograph twelve regions of a planet and has six candidate satellite passes; each pass sees
some of the regions. Which passes should it schedule so that every region is seen, using as few passes as
possible? This is **set cover**: given a universe $U$ of $n$ elements and a family of subsets
$S_1, \dots, S_m$ whose union is $U$, choose as few subsets as possible whose union is still $U$. It is NP-hard, and
it is the most general of the covering problems: vertex cover is the special case where the elements are edges and
each vertex is the set of edges touching it.

**Greedy.** Repeatedly choose the set that covers the most elements not yet covered.

The proof uses a bookkeeping trick. Each time greedy picks a set that covers $t$ new elements, charge each of those
elements a **price** of $1/t$. The prices of the elements covered in one step add up to 1, so the total price of
all elements equals the number of sets greedy chose.

Here is the example the program runs. The sets are $A = \{1,\dots,6\}$, $B = \{5,6,8,9\}$, $C = \{1,4,7,10\}$,
$D = \{2,5,7,8,11\}$, $E = \{3,6,9,12\}$ and $F = \{10,11\}$.

| step | new elements each set would cover | greedy picks | new elements | each pays |
|---|---|---|---|---|
| 1 | A 6, B 4, C 4, D 5, E 4, F 2 | A | 1, 2, 3, 4, 5, 6 | 1/6 |
| 2 | B 2, C 2, D 3, E 2, F 2 | D | 7, 8, 11 | 1/3 |
| 3 | B 1, C 1, E 2, F 1 | E | 9, 12 | 1/2 |
| 4 | C 1, F 1 | F (a tie) | 10 | 1 |

Greedy uses 4 sets; the optimum is 3 ($C$, $D$, $E$). The prices add up to $6 \cdot \tfrac16 + 3 \cdot \tfrac13 +
2 \cdot \tfrac12 + 1 = 4$.

**Theorem (Johnson 1974, Lovász 1975; Chvátal 1979 for weighted sets).** Greedy uses at most
$H_n \cdot \mathrm{OPT}$ sets, where $H_n = 1 + \tfrac12 + \tfrac13 + \dots + \tfrac1n \le 1 + \ln n$ is the
$n$-th harmonic number.

*Proof.* Number the elements $e_1, e_2, \dots, e_n$ in the order greedy covers them (elements covered in the same
step in any order). Consider the moment just before $e_k$ is covered. At least $n - k + 1$ elements are still
uncovered (namely $e_k, \dots, e_n$). The optimal solution covers all of them with $\mathrm{OPT}$ sets, so by the
pigeonhole principle one of those sets contains at least $(n-k+1)/\mathrm{OPT}$ uncovered elements. Greedy picks the
set with the *most* uncovered elements, so the set it picks covers $t \ge (n-k+1)/\mathrm{OPT}$ new elements, and
$e_k$ pays

$$
\mathrm{price}(e_k) = \frac1t \le \frac{\mathrm{OPT}}{n-k+1} .
$$

Adding over all elements,

$$
\text{sets chosen} = \sum_{k=1}^{n} \mathrm{price}(e_k) \le \mathrm{OPT} \left( \frac1n + \frac1{n-1} + \dots + \frac11 \right) = H_n \cdot \mathrm{OPT} . \qquad \square
$$

In the example, $H_{12} \approx 3.10$, so the theorem allows up to $3 \times 3.10 = 9.3$ sets; greedy used 4. Is
the logarithm real or an artifact of the proof? It is real. Build a universe of two rows, each split into blocks of
sizes $1, 2, 4, \dots, 2^{k-1}$. Let the sets be the two rows $R_0, R_1$ (so $\mathrm{OPT} = 2$), and for each $i$
the set $S_i$ made of block $i$ of both rows, which has $2^{i+1}$ elements. At the start $S_{k-1}$ has $2^k$
elements and each row has $2^k - 1$, so greedy takes $S_{k-1}$; the same happens one level down at every step, and
greedy ends with all $k$ blocks. With $n = 2^{k+1} - 2$ elements greedy uses $k \approx \log_2 n$ sets against 2:

```python
--8<-- "books/algorithms/ch23_set_cover.py"
```

```
greedy picks: ['A', 'D', 'E', 'F']
  element  1 pays 1/6
  element  2 pays 1/6
  element  3 pays 1/6
  element  4 pays 1/6
  element  5 pays 1/6
  element  6 pays 1/6
  element  7 pays 1/3
  element  8 pays 1/3
  element  9 pays 1/2
  element 10 pays 1
  element 11 pays 1/3
  element 12 pays 1/2
total price = 4 = number of sets 4
optimal: ['C', 'D', 'E']

k=2: n=  6  greedy uses 2 sets ['S1', 'S0'], optimum 2, H_n = 2.45
k=3: n= 14  greedy uses 3 sets ['S2', 'S1', 'S0'], optimum 2, H_n = 3.25
k=4: n= 30  greedy uses 4 sets ['S3', 'S2', 'S1', 'S0'], optimum 2, H_n = 3.99
k=5: n= 62  greedy uses 5 sets ['S4', 'S3', 'S2', 'S1', 'S0'], optimum 2, H_n = 4.71
k=6: n=126  greedy uses 6 sets ['S5', 'S4', 'S3', 'S2', 'S1', 'S0'], optimum 2, H_n = 5.42
```

Strangely, this simple greedy is essentially the best anyone can do. Uriel Feige (1998) showed that a ratio of
$(1 - \varepsilon)\ln n$ for any $\varepsilon > 0$ would put NP inside quasi-polynomial time, and Irit Dinur and
David Steurer (2014) showed it is NP-hard. Section 23.6 explains where such results come from.

The same price argument works when sets have costs: pick the set with the smallest cost per newly covered element,
and charge each new element that cost per element. The bound is again $H_n \cdot \mathrm{OPT}$ (Chvátal 1979).

## 23.4 A knapsack FPTAS

In the 0/1 knapsack problem ([Chapter 13](13-Dynamic-Programming.md), [reference page](../../dp/knapsack.md)) we
have $n$ items with profits $p_i$ and weights $w_i$, and a capacity $W$; we want the most profitable set of items
of total weight at most $W$. The dynamic program over capacities runs in $O(nW)$ time. That is
**pseudo-polynomial**: polynomial in the *value* $W$, but exponential in the number of digits needed to write $W$
down. Knapsack is NP-hard, but only because numbers can be huge.

There is a second dynamic program that turns the problem around. Let

$$
\mathrm{best}[q] = \text{the least weight of a set of items whose profit is exactly } q .
$$

Start with $\mathrm{best}[0] = 0$ and all other entries infinite; for each item $(p, w)$ in turn, for $q$ from the
top down, set $\mathrm{best}[q] = \min(\mathrm{best}[q], \mathrm{best}[q-p] + w)$. The answer is the largest $q$
with $\mathrm{best}[q] \le W$. The table has $\sum p_i + 1$ entries, so this takes $O(n \sum p_i)$ time: fast if the
*profits* are small numbers, whatever the weights.

The idea of Oscar Ibarra and Chul Kim (1975): **make the profits small by rounding them**. Choose a scale $K$, and
replace each profit by $p_i' = \lfloor p_i / K \rfloor$. Solve the rounded problem exactly with the profit DP. The
answer is optimal for the wrong profits; we show it is nearly optimal for the right ones.

**Algorithm (FPTAS for knapsack).** Given $\varepsilon > 0$: discard items heavier than $W$; let $P$ be the
largest remaining profit and $K = \varepsilon P / n$; round $p_i' = \lfloor p_i / K \rfloor$; run the profit DP on
the rounded profits; return the set $S$ it finds.

**Theorem.** $p(S) \ge (1 - \varepsilon)\,\mathrm{OPT}$, and the running time is $O(n^3 / \varepsilon)$.

*Proof.* Let $O$ be an optimal set. Rounding down loses less than $K$ per item, so for any set $X$,
$K p'(X) \le p(X) < K p'(X) + K|X|$, where $p'(X)$ is the rounded profit. Since $S$ is optimal for the rounded
profits, $p'(S) \ge p'(O)$. Therefore

$$
p(S) \ge K\,p'(S) \ge K\,p'(O) > p(O) - K|O| \ge \mathrm{OPT} - nK = \mathrm{OPT} - \varepsilon P .
$$

Every item fits alone, so the single most profitable item is a valid solution and $P \le \mathrm{OPT}$. Hence
$p(S) \ge \mathrm{OPT} - \varepsilon\,\mathrm{OPT}$. For the time: each $p_i' \le P/K = n/\varepsilon$, so
$\sum p_i' \le n^2/\varepsilon$, and the DP costs $O(n \cdot n^2/\varepsilon)$. $\square$

This is the strongest kind of approximation there is short of an exact answer. A **polynomial-time approximation
scheme** (PTAS) is a family of algorithms, one for each $\varepsilon > 0$, each running in polynomial time in $n$
and achieving ratio $1 + \varepsilon$ (or $1 - \varepsilon$ when maximising); the time may grow badly with
$1/\varepsilon$, as in $n^{1/\varepsilon}$. A **fully polynomial** scheme (FPTAS) runs in time polynomial in both
$n$ and $1/\varepsilon$, as ours does.

Trace the three-item example the program starts with: profits 60, 100, 120, weights 10, 20, 30, capacity 50. With
$\varepsilon = 0.5$: $P = 120$, $K = 0.5 \cdot 120 / 3 = 20$, rounded profits $3, 5, 6$. The rounded problem's best
is items 2 and 3 (rounded profit 11, weight 50), real profit 220, which is the true optimum.

```python
--8<-- "books/algorithms/ch23_knapsack_fptas.py"
```

```
items (profit, weight): [(60, 10), (100, 20), (120, 30)] capacity 50
exact: (220, [1, 2])
eps=0.5: K=20.0, scaled profits [3, 5, 6], value 220, items [1, 2]
eps=0.1: K=4.0, scaled profits [15, 25, 30], value 220, items [1, 2]

30 correlated items, capacity 838: optimum 84879, exact profit table would have 169038 cells
  eps    value    ratio   bound   table size
 0.90    84251  0.9926  0.10       549
 0.50    84445  0.9949  0.50       993
 0.20    84749  0.9985  0.80      2508
 0.10    84832  0.9994  0.90      5030
 0.05    84874  0.9999  0.95     10075
 0.01    84879  1.0000  0.99     50420
```

The second experiment uses "correlated" items, whose profit is nearly proportional to weight; such instances are
known to be hard for knapsack codes because every item looks about equally good. The table size grows like
$1/\varepsilon$, as the proof says, and the value stays far above the guarantee.

**Why not an FPTAS for everything?** A problem is **strongly NP-hard** if it stays NP-hard even when every number
in the input is at most a polynomial in $n$. Bin packing, TSP and 3-partition are examples. Such problems have no
FPTAS unless P = NP. The argument: if all numbers are at most $n^c$, the optimum of an integer-valued problem is at
most some polynomial $Q(n)$; run the FPTAS with $\varepsilon = 1/(Q(n)+1)$; an error smaller than 1 in an integer
value is no error, so the scheme solves the problem exactly in time polynomial in $n$ and $Q(n)$.

## 23.5 Linear programming and LP relaxation with rounding

*Level: intermediate to advanced.*

So far each algorithm had its own clever lower bound. Linear programming gives a lower bound almost for free, for
a huge range of problems.

A **linear program** (LP) asks to maximise (or minimise) a linear function of real variables subject to linear
inequalities. In **standard form**:

$$
\text{maximise } c^{\mathsf T} x \quad \text{subject to } A x \le b,\ x \ge 0 ,
$$

where $x$ is a column of $n$ unknowns, $c$ a column of $n$ given weights, $A$ a given $m \times n$ matrix and $b$ a
column of $m$ bounds. Each inequality cuts space in half by a flat wall (a **half-space**); the points satisfying
all of them form a convex polygon in two dimensions, a convex **polytope** in general, called the **feasible
region**. The objective is a direction; we want the point of the region farthest in that direction.

A concrete one: maximise $3x_1 + 2x_2$ subject to $x_1 + x_2 \le 4$, $x_1 + 3x_2 \le 6$, $x_1 \le 3$,
$x_1, x_2 \ge 0$. Figure 23.3 draws it. The region is the quadrilateral with corners $(0,0)$, $(3,0)$, $(3,1)$,
$(0,2)$.

<figure class="mars-fig" markdown="0">
<svg viewBox="0 0 660 300" role="img" aria-label="The feasible region of a two-variable LP, a quadrilateral with corners (0,0), (3,0), (3,1), (0,2), with the three constraint lines, the simplex path along the bottom edge then up, and a dashed level line of the objective through the optimum (3,1).">
<polygon points="60,260 240,260 240,200 60,140" fill="#9cc9ea" fill-opacity="0.45"/>
<g stroke="currentColor" stroke-width="1.2">
<line x1="60" y1="260" x2="380" y2="260"/>
<line x1="60" y1="260" x2="60" y2="15"/>
</g>
<g font-size="12" fill="currentColor" text-anchor="middle">
<text x="120" y="277">1</text><text x="180" y="277">2</text><text x="240" y="277">3</text><text x="300" y="277">4</text><text x="360" y="277">5</text>
<text x="48" y="204">1</text><text x="48" y="144">2</text><text x="48" y="84">3</text><text x="48" y="24">4</text>
<text x="385" y="277">x1</text><text x="60" y="12">x2</text>
</g>
<g stroke-width="1.5" fill="none">
<line x1="60" y1="20" x2="300" y2="260" stroke="currentColor"/>
<line x1="60" y1="140" x2="360" y2="240" stroke="currentColor" stroke-dasharray="2 3"/>
<line x1="240" y1="20" x2="240" y2="260" stroke="currentColor" stroke-dasharray="8 4"/>
<line x1="120" y1="20" x2="280" y2="260" stroke="#eea66f" stroke-dasharray="6 4" stroke-width="2"/>
</g>
<g stroke="#7ccf9a" stroke-width="4" fill="none">
<line x1="64" y1="260" x2="234" y2="260"/>
<line x1="240" y1="256" x2="240" y2="206"/>
</g>
<g stroke="currentColor" stroke-width="1.5">
<circle cx="60" cy="260" r="5" fill="#7ccf9a"/>
<circle cx="240" cy="260" r="5" fill="#7ccf9a"/>
<circle cx="240" cy="200" r="7" fill="#eea66f"/>
<circle cx="60" cy="140" r="4" fill="none"/>
</g>
<g font-size="13" fill="currentColor">
<text x="250" y="195">(3, 1): value 11</text>
<text x="232" y="250" text-anchor="end">(3, 0): value 9</text>
<text x="420" y="60">solid: x1 + x2 = 4</text>
<text x="420" y="84">dotted: x1 + 3x2 = 6</text>
<text x="420" y="108">long dashes: x1 = 3</text>
<text x="420" y="132" fill="#eea66f">orange: 3x1 + 2x2 = 11</text>
<text x="420" y="156">green: the simplex path</text>
<text x="420" y="180">blue: feasible region</text>
</g>
</svg>
<figcaption>Figure 23.3. A linear program in two variables. The best point is a corner of the region; the simplex method walks from corner to corner along edges, never getting worse.</figcaption>
</figure>

**Why corners.** If a point in the middle of an edge were the best, moving along the edge one way or the other
would not make the objective worse (a linear function along a line goes up one way and down the other, or is
flat), so one end of the edge is at least as good. Repeating the argument in higher dimensions shows: if an LP has
an optimum, some corner (a **vertex** of the polytope) attains it. There are finitely many corners, at most
$\binom{n+m}{m}$, so in principle we could try them all. That is exponential; we want a smarter walk.

**The simplex method** (George Dantzig, 1947) starts at a corner and repeatedly moves along an edge to a
neighbouring corner with a better objective value, until no neighbour is better. Because the region is convex and
the objective linear, a corner with no better neighbour is a global optimum (a local optimum of a linear function
over a convex set is global; this is the theorem that makes simplex work, and it follows from convexity:
if a better point existed, the segment toward it would leave the corner along a direction that improves the
objective, and such a direction can be written as a combination of edge directions, one of which must improve).

To compute with corners we add one **slack variable** per inequality: $s_1 = 4 - x_1 - x_2$,
$s_2 = 6 - x_1 - 3x_2$, $s_3 = 3 - x_1$, all required to be $\ge 0$. A corner is where $n$ of the $n + m$ variables
are zero; the other $m$ are the **basis**, written in terms of the zero ones. We start at the origin: $x_1 = x_2 = 0$
and the slacks are the basis. Written out (this form is called a **dictionary**):

$$
\begin{aligned}
z &= 0 + 3x_1 + 2x_2 \\
s_1 &= 4 - x_1 - x_2 \\
s_2 &= 6 - x_1 - 3x_2 \\
s_3 &= 3 - x_1
\end{aligned}
$$

*Step 1.* The objective row has a positive coefficient on $x_1$, so increasing $x_1$ helps. How far can it grow?
$s_1 \ge 0$ allows 4, $s_2$ allows 6, $s_3$ allows 3. The tightest is $s_3$ (this is the **ratio test**), so $x_1$
**enters** the basis and $s_3$ **leaves**: $x_1 = 3 - s_3$. Substitute everywhere:

$$
\begin{aligned}
z &= 9 + 2x_2 - 3s_3 \\
s_1 &= 1 - x_2 + s_3 \\
s_2 &= 3 - 3x_2 + s_3 \\
x_1 &= 3 - s_3
\end{aligned}
$$

We are at the corner $(3, 0)$ with value 9.

*Step 2.* $x_2$ still has a positive coefficient. $s_1$ allows $x_2 \le 1$, $s_2$ allows $x_2 \le 1$: a tie. (Three
of the walls meet at $(3,1)$; such a corner is called **degenerate**.) **Bland's rule** (1977) breaks ties by
choosing the variable with the smallest index, which provably prevents the method from cycling forever on degenerate
corners. So $s_1$ leaves: $x_2 = 1 - s_1 + s_3$, and

$$
\begin{aligned}
z &= 11 - 2s_1 - s_3 \\
x_2 &= 1 - s_1 + s_3 \\
s_2 &= 0 + 3s_1 - 2s_3 \\
x_1 &= 3 - s_3
\end{aligned}
$$

Every coefficient in the $z$ row is now negative or zero, so any feasible move (increasing a nonbasic variable from
0) can only lower $z$. The corner $(3, 1)$ with value 11 is optimal.

**Duality.** Look at the final $z$ row: $z = 11 - 2s_1 - 0 s_2 - 1 s_3$. Those numbers $y = (2, 0, 1)$ are a
*certificate* that 11 is optimal. Multiply the three constraints by $2$, $0$ and $1$ and add:

$$
2(x_1 + x_2) + 0(x_1 + 3x_2) + 1(x_1) = 3x_1 + 2x_2 \le 2 \cdot 4 + 0 \cdot 6 + 1 \cdot 3 = 11 .
$$

The combination reproduces the objective exactly, so *no* feasible point can do better than 11. In general, for
any $y \ge 0$ with $A^{\mathsf T} y \ge c$, and any feasible $x$,

$$
c^{\mathsf T} x \le (A^{\mathsf T} y)^{\mathsf T} x = y^{\mathsf T} (A x) \le y^{\mathsf T} b .
$$

This is **weak duality**: every feasible solution of the **dual** LP, "minimise $b^{\mathsf T} y$ subject to
$A^{\mathsf T} y \ge c$, $y \ge 0$", bounds the primal from above. The proof is the two-line calculation just
written. **Strong duality** says more: if the primal has an optimum, the dual optimum has the same value. The
simplex method proves it constructively: when it stops, the $z$ row has the form
$z = v - \sum_j \bar c_j (\text{nonbasic variables})$ with all $\bar c_j \ge 0$, and reading off
$y_i = \bar c_{s_i}$ for the slacks gives a dual solution with $b^{\mathsf T}y = v$ (checking $A^{\mathsf T}y \ge c$
is a page of algebra, in CLRS chapter 29). The idea of duality goes back to John von Neumann's remarks to Dantzig
in 1947.

The program implements exactly these steps in exact fractions (Python's `fractions` module), and prints the corners
it visits:

```python
--8<-- "books/algorithms/ch23_simplex.py"
```

```
LP: maximise 3x1 + 2x2 with x1 + x2 <= 4, x1 + 3x2 <= 6, x1 <= 3
  step 0: basis ['s1', 's2', 's3'], x = ['0', '0'], value 0
  step 1: basis ['s1', 's2', 'x1'], x = ['3', '0'], value 9
  step 2: basis ['x2', 's2', 'x1'], x = ['3', '1'], value 11
  optimum 11 at x = ['3', '1'] ; dual y = ['2', '0', '1']
  dual objective 4y1 + 6y2 + 3y3 = 11

triangle: LP optimum 3/2
   fractional cover x = ['1/2', '1/2', '1/2']
   fractional matching y = ['1/2', '1/2', '1/2']
   rounded cover (x >= 1/2): [0, 1, 2] size 3 valid True
section 23.1 example: LP optimum 3
   fractional cover x = ['0', '1', '1', '0', '1', '0']
   fractional matching y = ['0', '1', '1', '0', '0', '1']
   rounded cover (x >= 1/2): [1, 2, 4] size 3 valid True
5-cycle: LP optimum 5/2
   fractional cover x = ['1/2', '1/2', '1/2', '1/2', '1/2']
   fractional matching y = ['1/2', '1/2', '1/2', '1/2', '1/2']
   rounded cover (x >= 1/2): [0, 1, 2, 3, 4] size 5 valid True
```

**How fast is simplex?** In practice, very fast: the number of steps is typically a small multiple of $m$. In the
worst case, exponential: Victor Klee and George Minty (1972) built a squashed cube in $n$ dimensions on which the
usual pivot rule visits all $2^n$ corners. Whether *some* pivot rule always takes polynomially many steps is open
(it is tied to the polynomial Hirsch conjecture on polytope diameters). The first polynomial-time LP algorithm was
Leonid Khachiyan's ellipsoid method (1979); Narendra Karmarkar's interior-point method (1984) was the first that was
also fast in practice. Daniel Spielman and Shang-Hua Teng (2004) explained simplex's good behaviour with **smoothed
analysis**: if the input numbers are perturbed by a little random noise, the expected number of steps is
polynomial. So LP is in P, and the bad examples are fragile.

**LP relaxation and rounding.** Write vertex cover as an *integer* program: a variable $x_v \in \{0, 1\}$ for each
vertex ($1$ means "in the cover"):

$$
\text{minimise } \sum_{v} x_v \quad \text{subject to } x_u + x_v \ge 1 \text{ for every edge } uv,\ x_v \in \{0, 1\} .
$$

This is exactly vertex cover, so it is NP-hard. **Relax** it: allow any real $0 \le x_v \le 1$. Now it is an LP,
solvable in polynomial time, and since every true cover is a feasible point of the relaxation,

$$
\mathrm{LP} \le \mathrm{OPT} .
$$

The LP is our lower bound. To get a real cover, **round**: put $v$ in the cover when $x_v \ge \tfrac12$.

**Theorem.** LP rounding gives a vertex cover of size at most $2\,\mathrm{OPT}$.

*Proof.* For each edge, $x_u + x_v \ge 1$, so at least one of them is $\ge \tfrac12$ and is taken: the result is a
cover. Each taken vertex has $x_v \ge \tfrac12$, so the number taken is at most $\sum_v 2x_v = 2\,\mathrm{LP} \le
2\,\mathrm{OPT}$. $\square$

The program solves the relaxation in a neat way: the dual of the vertex cover LP is the **fractional matching** LP
(maximise $\sum_e y_e$ with $\sum_{e \ni v} y_e \le 1$ at each vertex), which is in standard form, so our simplex
solves it and the final $z$ row hands us the optimal fractional cover. On the triangle the LP says $\tfrac32$ (all
$x_v = \tfrac12$) while every real cover needs 2. The ratio between the integer optimum and the LP optimum, in the
worst case, is the **integrality gap**; it limits what any rounding of this LP can prove. For vertex cover it tends
to 2: on the complete graph $K_n$ the LP is $n/2$ (all halves) and the optimum is $n - 1$.

The same pattern, *write an integer program, relax, solve the LP, round*, gives approximation algorithms for
weighted vertex cover (where greedy matching does not apply but the rounding proof above works unchanged), for
weighted set cover (ratio $f$, the most sets any element is in), for facility location and for scheduling. More
sophisticated relaxations, **semidefinite programs**, gave Michel Goemans and David Williamson's 1995 algorithm for
maximum cut with ratio about 0.878.

## 23.6 Inapproximability and the PCP theorem

*Level: advanced.*

Can every NP-hard problem be approximated to some constant? No, and for some problems we can prove it with tools
from [Chapter 22](22-NP-Completeness.md) alone.

**Theorem.** If P ≠ NP, then for no constant $\rho \ge 1$ is there a polynomial-time $\rho$-approximation for TSP
with arbitrary (non-metric) distances.

*Proof.* Suppose such an algorithm $\mathcal A$ exists. We use it to decide the NP-complete Hamiltonian cycle
problem. Given a graph $G$ on $n$ vertices, build a TSP instance on the same vertices: distance 1 if $uv$ is an
edge of $G$, and distance $\rho n + 1$ otherwise. If $G$ has a Hamiltonian cycle, that cycle is a tour of length
$n$, so $\mathrm{OPT} = n$ and $\mathcal A$ returns a tour of length at most $\rho n$. If $G$ has none, every tour
uses at least one non-edge, so every tour, including the one $\mathcal A$ returns, has length at least
$(n - 1) + \rho n + 1 > \rho n$. So "$\mathcal A$'s tour has length at most $\rho n$" decides whether $G$ has a
Hamiltonian cycle, in polynomial time, which would give P = NP. $\square$

The trick is a **gap**: the reduction makes yes-instances and no-instances differ not just in their answers but by
a big factor in their optimum. An approximation algorithm cannot help noticing a big gap. For most problems, though,
the usual NP-completeness reductions create no gap at all: a satisfiable formula and one where all but one clause
can be satisfied look almost the same. Creating gaps is what the PCP theorem does.

**Probabilistically checkable proofs.** Recall from Chapter 22 that a language is in NP when there is a
polynomial-time *verifier* that reads a proposed certificate and accepts exactly when the input is a yes-instance
(for some certificate). Now limit the verifier: it may toss $r(n)$ random coins and then read only $q(n)$ bits of
the certificate, at positions chosen from the coins. It must accept a correct proof of a yes-instance always, and
for a no-instance it must reject every claimed proof with probability at least $\tfrac12$. The class of languages
with such verifiers is $\mathrm{PCP}(r(n), q(n))$.

**The PCP theorem (Arora and Safra; Arora, Lund, Motwani, Sudan and Szegedy; conference papers 1992, journal 1998).**

$$
\mathrm{NP} = \mathrm{PCP}(O(\log n),\, O(1)) .
$$

In words: every NP statement has a proof format that can be checked, with high confidence, by reading a *constant*
number of its bits chosen at random. It is as if you could grade a whole mathematical proof by looking at three
randomly chosen words of it. The proof is long (a graduate course); Irit Dinur found a different, combinatorial
proof in 2007 ("The PCP theorem by gap amplification"), and Arora and Barak's textbook presents it.

**Why it gives hardness of approximation.** Let $L$ be NP-complete and fix its PCP verifier with $c \log n$ coins
and $q$ queries. For each of the $2^{c \log n} = n^c$ coin outcomes, the verifier's decision is a function of $q$
proof bits; write it as a small formula in those bits (a 3-CNF with at most some constant $Q$ clauses, since $q$ is
a constant). Put all these $n^c$ little formulas together: a polynomial-size 3-SAT instance $\phi$. If $x \in L$,
the correct proof satisfies every clause. If $x \notin L$, every assignment (every claimed proof) makes at least
half of the coin outcomes reject, so at least a fraction $\tfrac{1}{2Q}$ of all clauses is false. Distinguishing
"all clauses satisfiable" from "at most a $1 - \tfrac{1}{2Q}$ fraction satisfiable" is therefore NP-hard, and so
there is a constant $\varepsilon > 0$ such that **MAX-3SAT has no polynomial-time $(1-\varepsilon)$-approximation
unless P = NP**. The converse also holds: such a gap result implies the PCP theorem. They are two faces of one fact.

**The map of what is known.** Gap-preserving reductions from MAX-3SAT then spread hardness to many problems. A
selection of results, each from the named paper and each assuming P ≠ NP unless stated:

| problem | best ratio known in polynomial time | hardness |
|---|---|---|
| MAX-3SAT | 7/8 (random assignment, derandomized) | $7/8 + \varepsilon$ is NP-hard (Håstad 2001) |
| vertex cover | 2 (23.1) | 1.3606 NP-hard (Dinur and Safra 2005); $\sqrt2 - \varepsilon$ NP-hard (Khot, Minzer and Safra, 2018); $2 - \varepsilon$ under the Unique Games Conjecture (Khot and Regev 2008) |
| set cover | $H_n \approx \ln n$ (23.3) | $(1-\varepsilon)\ln n$ NP-hard (Dinur and Steurer 2014) |
| maximum clique | barely better than the trivial factor $n$ | $n^{1-\varepsilon}$ NP-hard (Håstad 1999, Zuckerman 2007) |
| metric TSP | $3/2 - 10^{-36}$ (Karlin, Klein, Oveis Gharan 2021) | $123/122$ NP-hard (Karpinski, Lampis and Schmied 2015) |
| knapsack | FPTAS (23.4) | none beyond exactness |

Johan Håstad's 7/8 is remarkable because it matches a trivial algorithm: a random assignment satisfies each
3-literal clause with probability $7/8$, and he proved that doing even slightly better is NP-hard. The **Unique
Games Conjecture** (Subhash Khot, 2002) is a still-unproved statement about a particular kind of constraint problem;
if it is true, the simple LP and semidefinite algorithms are exactly optimal for vertex cover, maximum cut (the
Goemans-Williamson 0.878) and many others. Whether it is true is one of the central open problems of the area.
The gap for metric TSP, between $123/122 \approx 1.008$ and about 1.5, is embarrassingly wide.

So approximability sorts NP-hard problems into classes: those with an FPTAS (knapsack), a PTAS but no FPTAS
(Euclidean TSP), a constant ratio but no PTAS (**APX-hard** problems such as vertex cover and MAX-3SAT), a
logarithmic ratio (set cover), or essentially nothing (clique, general TSP). NP-completeness made all these problems
look the same; approximation shows they are very different.

## 23.7 Fixed-parameter tractability: vertex cover in $O(2^k n)$

*Level: advanced.*

The museum from 23.1 has 3,000 junctions but its budget allows only 12 guards. Is there a cover with at most 12
vertices? Trying all $\binom{3000}{12} \approx 10^{33}$ subsets is hopeless. But the number 12 is small, and a
smarter search can exploit that.

The idea of **parameterized complexity** (Rodney Downey and Michael Fellows, around 1990; their book appeared in
1999) is to measure running time in two quantities: the input size $n$ and a **parameter** $k$, some number that is
small in the instances we care about (the size of the solution, the width of a tree decomposition, the number of
distinct values). A problem is **fixed-parameter tractable** (FPT) if it can be solved in time

$$
f(k) \cdot n^{O(1)}
$$

for some computable function $f$, however fast-growing, that depends only on $k$. The point is that the exponent of
$n$ does not depend on $k$. Contrast $O(n^k)$, the cost of trying all $k$-subsets: that is polynomial for each
fixed $k$ (the class called **XP**), but $n^{12}$ for $n = 3000$ is useless, while $2^{12} \cdot 3000$ is nothing.

**A bounded search tree.** Pick any edge $uv$. Every vertex cover contains $u$ or $v$. So branch: either put $u$ in
the cover, delete it and all its edges, and look for a cover of size $k-1$ in what is left; or do the same with
$v$. If no edges remain we have succeeded; if edges remain but $k = 0$, this branch fails.

**Theorem.** This decides whether a cover of size at most $k$ exists in $O(2^k \cdot m)$ time, where $m$ is the
number of edges.

*Proof.* *Correct:* by induction on $k$. If a cover $C$ with $|C| \le k$ exists, it contains $u$ or $v$; say $u$.
Then $C \setminus \{u\}$ covers the graph with $u$ deleted and has size at most $k - 1$, so by induction the $u$
branch succeeds. Conversely, any cover found by a branch, plus the vertex chosen, covers the whole graph. *Time:*
each call makes at most two recursive calls with $k$ reduced by 1, so the search tree has depth at most $k$ and at
most $2^{k+1} - 1$ nodes. Each node does $O(m)$ work to delete a vertex's edges. $\square$

Figure 23.4 shows the search tree for a path $a$-$b$-$c$-$d$ with $k = 2$.

<figure class="mars-fig" markdown="0">
<svg viewBox="0 0 660 260" role="img" aria-label="A bounded search tree for vertex cover on the path a-b-c-d with k equal to 2. The root branches on edge ab into take a and take b; each child branches again; leaves show success or failure.">
<g stroke="currentColor" stroke-width="1.4">
<line x1="330" y1="66" x2="175" y2="112"/>
<line x1="330" y1="66" x2="495" y2="112"/>
<line x1="175" y1="156" x2="85" y2="196"/>
<line x1="175" y1="156" x2="245" y2="196"/>
<line x1="495" y1="156" x2="415" y2="196"/>
<line x1="495" y1="156" x2="575" y2="196"/>
</g>
<g stroke="currentColor" stroke-width="1.3">
<rect x="250" y="22" width="160" height="44" rx="6" fill="#9cc9ea"/>
<rect x="100" y="112" width="150" height="44" rx="6" fill="#9cc9ea"/>
<rect x="420" y="112" width="150" height="44" rx="6" fill="#9cc9ea"/>
<rect x="15" y="196" width="140" height="44" rx="6" fill="#eea66f"/>
<rect x="175" y="196" width="140" height="44" rx="6" fill="#7ccf9a"/>
<rect x="345" y="196" width="140" height="44" rx="6" fill="#7ccf9a"/>
<rect x="505" y="196" width="140" height="44" rx="6" fill="#7ccf9a"/>
</g>
<g font-size="12" text-anchor="middle" fill="currentColor">
<text x="330" y="40">edges ab, bc, cd</text><text x="330" y="58">k = 2, branch on ab</text>
<text x="175" y="130">take a: edges bc, cd</text><text x="175" y="148">k = 1, branch on bc</text>
<text x="495" y="130">take b: edge cd</text><text x="495" y="148">k = 1, branch on cd</text>
<text x="85" y="214">take b: edge cd left</text><text x="85" y="232">k = 0: fail</text>
<text x="245" y="214">take c: no edges</text><text x="245" y="232">cover {a, c}</text>
<text x="415" y="214">take c: no edges</text><text x="415" y="232">cover {b, c}</text>
<text x="575" y="214">take d: no edges</text><text x="575" y="232">cover {b, d}</text>
</g>
</svg>
<figcaption>Figure 23.4. The search tree branches on the two ends of an uncovered edge. Its depth is at most k, so it has at most 2 to the power k leaves, however large the graph. (A real search stops at the first success.)</figcaption>
</figure>

**Kernels.** A second, complementary idea: shrink the input first. A **kernelization** is a polynomial-time
procedure that turns an instance $(G, k)$ into an equivalent instance $(G', k')$ with $k' \le k$ and size bounded by
a function of $k$ alone. Samuel Buss's rules for vertex cover (published with Judy Goldsmith in 1993):

1. If a vertex $v$ has degree more than $k$, it must be in every cover of size at most $k$ (otherwise all of its
   more than $k$ neighbours would be needed). Take it, delete it, and decrease $k$ by 1. Repeat.
2. Delete isolated vertices.
3. Now every vertex has degree at most $k$, so $k$ vertices cover at most $k^2$ edges. If more than $k^2$ edges
   remain, answer no.

What survives has at most $k^2$ edges, and at most $k + k^2$ vertices: each of the at most $k$ cover vertices
has at most $k$ neighbours, and every surviving vertex is a cover vertex or a neighbour of one. Running the search tree on the kernel costs
$O(2^k k^2)$, so the whole algorithm runs in $O(n + m + 2^k k^2)$.

**Theorem.** A decidable parameterized problem is FPT if and only if it has a kernel.

*Proof.* If there is a kernel, compute it in polynomial time and then solve the kernel by any algorithm at all; its
size depends only on $k$, so this costs $f(k)$. Conversely, suppose an algorithm runs in time $f(k) n^c$. Given an
instance, if $n \ge f(k)$, then running the algorithm takes at most $n^{c+1}$ steps, which is polynomial, so solve
it and output a trivial yes- or no-instance of constant size. Otherwise $n < f(k)$, and the instance itself is a
kernel. $\square$

The program runs the search tree on graphs where we hid a cover of size $k$, and applies Buss's rules:

```python
--8<-- "books/algorithms/ch23_fpt.py"
```

```
   n    m   k   search-tree nodes   2^(k+1)-1   C(n,k)
  100  150   6             32         127   1.19e+09
  300  400   8            137         511   1.48e+15
 1000 1500  10           1743        2047   2.63e+23
 3000 4000  12           4344        8191   1.09e+33

kernel (dense planted): 1500 edges, k=10 -> forced 10, left 0 edges on 0 vertices, k'=0; search 1 nodes, cover 10
kernel (sparse planted): 40 edges, k=10 -> forced 0, left 40 edges on 46 vertices, k'=10; search 19 nodes, cover 10
kernel (matching of 15 edges): 15 edges, k=3 -> answer is NO at once

cover of size 10? True  (589 search-tree nodes, 2^(k+1)-1 = 2047)
cover of size 9? False  (1023 search-tree nodes, 2^(k+1)-1 = 1023)
```

The node counts never exceed $2^{k+1} - 1$, while trying all $k$-subsets would face up to $10^{33}$ candidates. On
the dense graph, rule 1 alone finds the whole cover: the ten hidden cover vertices are the only ones of high degree.
Proving "no" is the expensive case: the search for a cover of size 9 had to explore the full tree of
$2^{10} - 1 = 1023$ nodes. (The count is $2^{10} - 1$ rather than $2^{k+1} - 1$ because a call with $k = 0$ and
edges left stops without branching.)

**Better and worse.** Smarter branching (for instance on a vertex of degree 3 or more: take it, or take all its
neighbours) shrinks the base of the exponent; the best known running time for vertex cover is
$O(1.2738^k + kn)$ (Jianer Chen, Iyad Kanj and Ge Xia, 2010). A kernel with at most $2k$ vertices follows from the LP
relaxation of 23.5: George Nemhauser and Leslie Trotter showed in 1975 that the LP has an optimum with all values in
$\{0, \tfrac12, 1\}$ and that the vertices at 1 can be taken and those at 0 discarded. On the other side, some
problems seem not to be FPT: $k$-clique has an obvious $O(n^k)$ algorithm but is complete for the class W[1],
which is believed to be strictly larger than FPT, so no $f(k) n^{O(1)}$ algorithm is expected. And under the
Exponential Time Hypothesis (Chapter 25) vertex cover has no $2^{o(k)} n^{O(1)}$ algorithm, so the exponential in
$k$ is the right shape.

FPT is the theory behind a practical observation: many hard problems are easy on real data because some hidden
parameter is small. Treewidth, which measures how close a graph is to a tree, is the most famous: Courcelle's
theorem (1990) says that every graph property expressible in a certain logic (monadic second-order logic) can be
decided in time $f(\text{treewidth}) \cdot n$.

## 23.8 Heuristics in practice: local search, SAT solvers and integer programming solvers

The algorithms so far come with proofs. The tools that solve the biggest real instances often come without them.
A **heuristic** is a method that usually finds good answers fast but has no worst-case guarantee on quality,
running time, or both. Three families matter most.

**Local search.** Start with any solution and repeatedly replace it by a better one in its **neighbourhood**, the
set of solutions reachable by a small change, until no neighbour is better: a **local optimum**. For TSP the classic
neighbourhood is **2-opt** (G. A. Croes, 1958): remove two edges and reconnect the two paths the other way. Shen Lin
and Brian Kernighan's 1973 heuristic chains many such moves and is still the core of the best TSP heuristics. We saw
2-opt reach the exact optimum on all six random 12-city instances in 23.2. To escape poor local optima, **simulated
annealing** (Kirkpatrick, Gelatt and Vecchi, 1983) sometimes accepts a worse neighbour, with a probability that
shrinks over time, and **tabu search** forbids undoing recent moves.

**SAT solvers.** Many hard problems (hardware verification, scheduling, puzzles, planning) are translated into SAT
and handed to a solver. The basic algorithm is **DPLL** (Davis and Putnam 1960; Davis, Logemann and Loveland 1962):
backtracking search ([Chapter 14](14-Backtracking-and-Branch-and-Bound.md)) over variable assignments, plus **unit
propagation**: if every literal of a clause but one is false, the last one is forced. Modern solvers add
**conflict-driven clause learning** (CDCL; GRASP by Marques-Silva and Sakallah, 1996): when a branch fails, analyse
which choices caused the conflict, add a new clause forbidding that combination, and jump back past irrelevant
choices. With efficient data structures (the "watched literals" of the Chaff solver, Moskewicz and others, 2001)
CDCL solvers handle many industrial formulas with millions of clauses. Local search works on SAT too: **WalkSAT**
(Selman, Kautz and Cohen, 1994) flips a variable in an unsatisfied clause, sometimes at random, sometimes greedily.

Here is a small DPLL with unit propagation and a WalkSAT, run on random 3-SAT formulas with 40 variables and
different ratios of clauses to variables:

```python
--8<-- "books/algorithms/ch23_sat.py"
```

```
 ratio  clauses  DPLL result  decisions  conflicts   WalkSAT flips
 3.00      120          SAT          8          1   62
 4.00      160          SAT         58         28   1364
 4.26      170          SAT         64         29   177
 5.00      200        UNSAT         64         33   (cannot prove UNSAT)
 6.00      240        UNSAT         28         15   (cannot prove UNSAT)
```

Two things are visible even at this small size. Formulas with few clauses are easy and almost always satisfiable;
formulas with many clauses are almost always unsatisfiable, and a contradiction is found quickly; the hardest are
near the transition between them. Experiments (Mitchell, Selman and Levesque, 1992, and many since) put that
transition for random 3-SAT near a ratio of about 4.27 clauses per variable; its exact location for 3-SAT is not
proved. Second, local search can find a satisfying assignment but can never prove that none exists: for that you
need a complete search like DPLL or CDCL.

**Integer programming solvers.** An integer linear program (ILP) is an LP whose variables must be integers; it can
express almost every combinatorial problem in this book. Solvers combine the ideas of this chapter: solve the LP
relaxation for a bound (23.5), **branch** on a variable with a fractional value ($x \le 2$ or $x \ge 3$), and prune
any branch whose LP bound is worse than the best integer solution found so far (**branch and bound**, Ailsa Land and
Alison Doig, 1960, the method of [Chapter 14](14-Backtracking-and-Branch-and-Bound.md)). They also add **cutting
planes**, inequalities that all integer solutions satisfy but the current fractional optimum violates (Ralph Gomory,
1958), which tighten the relaxation. Heuristics inside the solver find good integer solutions early, so the pruning
works. The Concorde TSP solver of Applegate, Bixby, Chvátal and Cook used LP relaxations with problem-specific
cutting planes to solve, with a proof of optimality, an instance of 85,900 cities, as its authors report in their 2006 book.

**Choosing in practice.** For a problem you must solve:

1. Check whether your instances have a small parameter or special structure (planar, bounded treewidth, small
   numbers): an exact algorithm may be fast.
2. If you need proof of optimality on moderate sizes, model it as SAT or ILP and use a solver.
3. If you need a good answer fast on large sizes, use local search started from an approximation algorithm, and use
   the approximation's lower bound (an MST, an LP value) to tell you how far from optimal you might be.

**In practice.** Python programmers reach for OR-Tools (Google's routing, LP and constraint solvers), PuLP or
Pyomo to write LP and ILP models for solvers such as HiGHS, CBC, Gurobi or CPLEX, `scipy.optimize.linprog` for LPs,
and PySAT, MiniSat or CaDiCaL for SAT. NetworkX has `approximation.min_weighted_vertex_cover` (an LP-style
2-approximation) and Christofides for TSP.

## Check yourself

??? question "1. Run the matching cover on the star with centre 0 and leaves 1, 2, 3, 4, 5 (edges 01 to 05). What does it return, what is the optimum, and what does the lemma's lower bound say?"
    The first edge 01 is taken, so $C = \{0, 1\}$; every later edge touches 0 and is skipped. The algorithm returns
    2 vertices. The optimum is 1 (just the centre). The matching has one edge, so the lemma says $\mathrm{OPT} \ge 1$,
    and indeed $2 \le 2 \cdot 1$. The ratio 2 is reached again.

??? question "2. Why does the double-tree algorithm need the triangle inequality? Give a four-city example where shortcutting makes a walk longer."
    Shortcutting replaces a path $u \to \dots \to w$ by the direct edge $uw$, and only the triangle inequality
    guarantees $d(u, w)$ is no longer than the path. Without it, take cities $a, b, c, d$ with every distance 1
    except $d(b, c) = 100$. The MST could be the star at $a$ (edges $ab, ac, ad$, weight 3). The walk around it is
    $a\,b\,a\,c\,a\,d\,a$ of length 6, but the preorder tour $a\,b\,c\,d\,a$ uses $bc$ and has length
    $1 + 100 + 1 + 1 = 103$, while the tour $a\,b\,d\,c\,a$ has length 4. (Section 23.6 proves that without the
    triangle inequality no constant ratio is possible at all.)

??? question "3. In Christofides, why does the set O of odd-degree vertices always have an even number of elements?"
    Each edge adds 1 to the degree of each of its two ends, so the sum of all degrees is $2|E|$, an even number. The
    vertices of even degree contribute an even amount, so the odd-degree vertices must contribute an even amount,
    which needs an even number of odd terms.

??? question "4. Show that the greedy rule 'take the vertex of highest degree' can be worse than factor 2 for vertex cover."
    Build a bipartite graph with $n$ top vertices $t_0, \dots, t_{n-1}$. For each $j = 2, 3, \dots, n$ add
    $\lfloor n/j \rfloor$ bottom vertices; the $g$-th of them is joined to the $j$ top vertices
    $t_{gj}, \dots, t_{gj+j-1}$. A top vertex gets at most one edge from each $j$, so its degree is at most $n - 1$,
    while the bottom vertex for $j = n$ has degree $n$. Greedy takes it first. In general, once all bottom vertices
    with $j' > j$ are gone, a top vertex has degree at most $j - 1$ (one edge for each of $2, \dots, j$) while a bottom
    vertex of group $j$ still has degree $j$, so greedy always prefers a bottom vertex, with no ties, and ends up
    taking all $\sum_{j=2}^{n} \lfloor n/j \rfloor$ of them. For $n = 6$ that is $3 + 2 + 1 + 1 + 1 = 8$; for $n = 12$
    it is 23; for $n = 20$ it is 46 (checked by running greedy). The $n$ top vertices are a cover, so
    $\mathrm{OPT} \le n$ and the ratio is at least $46/20 = 2.3$ for $n = 20$. The sum is about $n(\ln n - 0.85)$,
    so the ratio grows like $\ln n$.

??? question "5. Write the code: the weighted set cover greedy (pick the set with least cost per new element) and run it on universe {1,...,6}, sets A={1,2,3} cost 3, B={4,5,6} cost 3, C={1,2,3,4,5,6} cost 7."
    ```python
    def weighted_greedy(universe, sets, cost):
        left, chosen, total = set(universe), [], 0
        while left:
            name = min((s for s in sets if sets[s] & left),
                       key=lambda s: cost[s] / len(sets[s] & left))
            chosen.append(name)
            total += cost[name]
            left -= sets[name]
        return chosen, total

    sets = {"A": {1, 2, 3}, "B": {4, 5, 6}, "C": {1, 2, 3, 4, 5, 6}}
    cost = {"A": 3, "B": 3, "C": 7}
    print(weighted_greedy(range(1, 7), sets, cost))   # (['A', 'B'], 6)
    ```
    First step: A and B cost 1 per element, C costs $7/6 \approx 1.17$, so A (the first of the tie) is chosen.
    Then B covers 3 new elements at 1 each, C covers the same 3 at $7/3$, so B. Total 6, which is optimal.

??? question "6. In the knapsack FPTAS, why must items heavier than W be discarded before computing P?"
    The proof uses $P \le \mathrm{OPT}$, which holds because the single most profitable item is itself a feasible
    solution. If an item heavier than $W$ were allowed to define $P$, it could have a huge profit that no feasible
    solution reaches; then $K = \varepsilon P/n$ would be huge, all real items would round to profit 0, and the
    error $nK = \varepsilon P$ could exceed the optimum itself.

??? question "7. Trace the FPTAS by hand on profits 7, 9, 11, weights 3, 4, 5, capacity 8, with eps = 0.6."
    All items fit. $P = 11$, $n = 3$, $K = 0.6 \cdot 11 / 3 = 2.2$. Rounded profits: $\lfloor 7/2.2 \rfloor = 3$,
    $\lfloor 9/2.2 \rfloor = 4$, $\lfloor 11/2.2 \rfloor = 5$. Feasible pairs: items 1 and 2 (weight 7, rounded 7),
    items 1 and 3 (weight 8, rounded 8); items 2 and 3 weigh 9, too heavy. The rounded DP picks items 1 and 3, real
    profit 18. That is also the true optimum (the other pair gives 16). The guarantee was only
    $(1 - 0.6) \cdot 18 = 7.2$.

??? question "8. Write the dual of: maximise x1 + x2 subject to 2x1 + x2 <= 4, x1 + 2x2 <= 4, x >= 0. Find both optima and check they agree."
    Dual: minimise $4y_1 + 4y_2$ subject to $2y_1 + y_2 \ge 1$, $y_1 + 2y_2 \ge 1$, $y \ge 0$. Primal corners:
    $(0,0)$ value 0, $(2,0)$ value 2, $(0,2)$ value 2, and the intersection of the two lines $(4/3, 4/3)$ with
    value $8/3$, which is the optimum. Dual: by symmetry try $y_1 = y_2 = 1/3$: both constraints give exactly 1, and
    the value is $8/3$. Weak duality says no primal point exceeds $8/3$, and here the two meet, so both are optimal.

??? question "9. On an even cycle with 2r vertices, show that all values 1/2 is an optimal solution of the vertex cover LP, and say what rounding at 1/2 gives. What does this show about the rounding analysis?"
    All $x_v = \tfrac12$ is feasible (each edge gets $\tfrac12 + \tfrac12 = 1$) with value $r$. Every other vertex
    is a real cover of size $r$, so $\mathrm{OPT} \le r$, and $r$ alternate edges form a matching, so
    $\mathrm{LP} \ge r$ by weak duality. Hence $\mathrm{LP} = \mathrm{OPT} = r$ and all halves is optimal.
    Rounding at $\tfrac12$ takes all $2r$ vertices, twice the optimum. So the factor 2 can be lost in the rounding
    step even when the relaxation itself is exact; a different optimal LP solution (alternating 0 and 1) would have
    rounded perfectly.

??? question "10. Write the code: decide by a bounded search tree whether a graph has an independent set of size k. Why is this FPT for graphs of maximum degree d, but not in general?"
    An **independent set** is a set of vertices with no edge between any two. Pick any vertex $v$. If an
    independent set $S$ contains no vertex of $N[v]$ ($v$ and its neighbours), then $S \cup \{v\}$ is still
    independent, so if a set of size $k$ exists, one exists that contains a vertex of $N[v]$. Branch on the at most
    $d + 1$ choices, deleting the chosen vertex and its neighbours and looking for $k - 1$ more: at most $(d+1)^k$
    leaves, each costing polynomial time. That is FPT when $d$ is a constant.
    ```python
    def has_independent_set(adj, alive, k):
        if k == 0:
            return True
        if not alive:
            return False
        v = min(alive, key=lambda u: len(adj[u] & alive))
        for pick in [v] + sorted(adj[v] & alive):
            rest = alive - {pick} - adj[pick]
            if has_independent_set(adj, rest, k - 1):
                return True
        return False

    cycle6 = {i: {(i - 1) % 6, (i + 1) % 6} for i in range(6)}
    print(has_independent_set(cycle6, set(range(6)), 3))   # True
    print(has_independent_set(cycle6, set(range(6)), 4))   # False
    ```
    In general graphs the branching factor can be about $n$, giving up to $n^k$ leaves: XP, not FPT. Independent
    set parameterized by $k$ is W[1]-hard (it is clique in the complement graph), so no FPT algorithm is expected.

??? question "11. Improve the search tree for vertex cover: if every vertex has degree at most 2 solve directly; otherwise branch on a vertex v of degree at least 3. What recurrence do you get, and what is its growth rate?"
    If all degrees are at most 2, the graph is a union of paths and cycles, and the minimum cover is read off:
    $\lfloor \ell/2 \rfloor$ for a path on $\ell$ vertices, $\lceil \ell/2 \rceil$ for a cycle on $\ell$
    vertices. Otherwise let $v$ have degree $d \ge 3$. Either $v$ is in the cover (recurse with $k - 1$) or it is
    not, and then all its neighbours must be (recurse with $k - d \le k - 3$). The number of leaves satisfies
    $L(k) \le L(k-1) + L(k-3)$, which grows like $x^k$ for the largest root of $x^3 = x^2 + 1$, about $1.4656$. So
    the search takes $O(1.4656^k \cdot m)$ time instead of $O(2^k m)$.

??? question "10. Write the code: a bounded-search-tree algorithm that decides whether a graph has an independent set of size k... and explain why this does NOT give an FPT algorithm for independent set in general, though it does for graphs of maximum degree d."
    In a graph of maximum degree $d$, pick a vertex $v$ of smallest degree: some maximum independent set contains
    $v$ or one of its at most $d$ neighbours (if an independent set avoids all of $N[v]$, swap any... more
    precisely, if it contains no vertex of $N[v]$ we can add $v$). Branch on these $d+1$ choices, deleting the chosen
    vertex and its neighbours, with $k - 1$: a tree of at most $(d+1)^k$ leaves.
    ```python
    def has_independent_set(adj, alive, k):
        if k == 0:
            return True
        if not alive:
            return False
        v = min(alive, key=lambda u: len(adj[u] & alive))
        for pick in [v] + sorted(adj[v] & alive):
            rest = alive - {pick} - adj[pick]
            if has_independent_set(adj, rest, k - 1):
                return True
        return False

    cycle6 = {i: {(i - 1) % 6, (i + 1) % 6} for i in range(6)}
    print(has_independent_set(cycle6, set(range(6)), 3))   # True
    print(has_independent_set(cycle6, set(range(6)), 4))   # False
    ```
    In general graphs the branching factor is the degree, which can be about $n$, so the tree has up to $n^k$
    leaves: that is XP, not FPT. Independent set parameterized by $k$ is W[1]-hard (it is clique on the complement
    graph), so no FPT algorithm is expected.

??? question "11. Prove that the bounded search tree can be improved to about 1.62^k: if every vertex has degree at most 2 the problem is easy; otherwise branch on a vertex v of degree at least 3."
    If all degrees are at most 2, the graph is a union of paths and cycles, and the minimum cover is computed
    directly ($\lfloor \ell/2 \rfloor$ for a path with $\ell$ vertices, $\lceil \ell/2 \rceil$ for a cycle). Otherwise
    let $v$ have degree $d \ge 3$. Either $v$ is in the cover (recurse with $k - 1$) or it is not, and then all its
    neighbours must be (recurse with $k - d \le k - 3$). The number of leaves $L(k)$ satisfies
    $L(k) \le L(k-1) + L(k-3)$, whose growth rate is the largest root of $x^3 = x^2 + 1$, about $1.4656$. (Branching
    on degree at least 2 instead gives $L(k-1) + L(k-2)$, the Fibonacci rate $1.618$, which is where the "1.62" in
    the question comes from; degree 3 is better still.)

## What you learned

- An approximation guarantee compares with $\mathrm{OPT}$ through a lower bound you can compute: a matching, a
  spanning tree, an LP optimum.
- Vertex cover has a 2-approximation by maximal matching, and the bound is tight for that algorithm.
- Metric TSP: doubling the MST gives 2, Christofides' matching on odd vertices gives 1.5; without the triangle
  inequality no constant ratio is possible unless P = NP.
- Greedy set cover is within $H_n \approx \ln n$ of optimal, by the price argument, and that is essentially best
  possible.
- Rounding profits turns knapsack's pseudo-polynomial DP into an FPTAS; strongly NP-hard problems have none.
- Linear programs are solved by walking corners (simplex) and certified by duality; relaxing an integer program to
  an LP and rounding is a general recipe.
- The PCP theorem makes gaps, and gaps give hardness of approximation; problems differ greatly in how well they can
  be approximated.
- Fixed-parameter algorithms such as the $O(2^k m)$ search tree and kernels make NP-hard problems easy when a
  parameter is small; SAT and ILP solvers and local search do the heavy lifting in practice.

**Next:** [Chapter 24](24-Algorithms-for-Big-Data-and-Many-Processors.md), algorithms for data that arrives
online, streams past, lives on disk or is shared among many processors.

## Further reading

- D. S. Johnson, "Approximation algorithms for combinatorial problems", *Journal of Computer and System Sciences*
  9, 1974.
- N. Christofides, "Worst-case analysis of a new heuristic for the travelling salesman problem", report 388,
  Graduate School of Industrial Administration, Carnegie Mellon University, 1976.
- V. Chvátal, "A greedy heuristic for the set-covering problem", *Mathematics of Operations Research* 4, 1979.
- O. H. Ibarra and C. E. Kim, "Fast approximation algorithms for the knapsack and sum of subset problems",
  *Journal of the ACM* 22, 1975.
- S. Arora, C. Lund, R. Motwani, M. Sudan and M. Szegedy, "Proof verification and the hardness of approximation
  problems", *Journal of the ACM* 45, 1998; S. Arora and S. Safra, "Probabilistic checking of proofs", same
  volume; I. Dinur, "The PCP theorem by gap amplification", *Journal of the ACM* 54, 2007.
- J. Håstad, "Some optimal inapproximability results", *Journal of the ACM* 48, 2001.
- A. R. Karlin, N. Klein and S. Oveis Gharan, "A (slightly) improved approximation algorithm for metric TSP",
  STOC 2021.
- V. V. Vazirani, *Approximation Algorithms*, 2001; D. P. Williamson and D. B. Shmoys, *The Design of
  Approximation Algorithms*, 2011.
- M. Cygan, F. V. Fomin, Ł. Kowalik, D. Lokshtanov, D. Marx, M. Pilipczuk, M. Pilipczuk and S. Saurabh,
  *Parameterized Algorithms*, 2015; R. G. Downey and M. R. Fellows, *Parameterized Complexity*, 1999.
- V. Chvátal, *Linear Programming*, 1983; CLRS (Cormen, Leiserson, Rivest, Stein, *Introduction to Algorithms*,
  4th ed. 2022), chapters 29 and 35; Kleinberg and Tardos (*Algorithm Design*, 2005), chapters 10 and 11.
- S. Arora and B. Barak, *Computational Complexity: A Modern Approach*, 2009 (PCP theorem).
- D. L. Applegate, R. E. Bixby, V. Chvátal and W. J. Cook, *The Traveling Salesman Problem: A Computational
  Study*, 2006.
- A. Biere, M. Heule, H. van Maaren and T. Walsh (eds.), *Handbook of Satisfiability*, 2009.
- On this site: [Prim](../../graphs/prim.md), [Kruskal](../../graphs/kruskal.md),
  [knapsack](../../dp/knapsack.md), [Chapter 22](22-NP-Completeness.md),
  [Chapter 14](14-Backtracking-and-Branch-and-Bound.md); the
  [Machine learning book](../machine-learning/index.md) uses the same LP and local-search ideas for optimisation.
