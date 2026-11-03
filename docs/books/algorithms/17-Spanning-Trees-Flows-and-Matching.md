# 17. Spanning trees, flows and matching

*Three questions about networks that look different and turn out to be close relatives. What is the cheapest set
of cables that connects every building? How much water, traffic or data can a network carry from a source to a
sink? How can people be paired with jobs, or students with schools, as well as possible? This chapter answers all
three from first principles. Minimum spanning trees fall to greedy algorithms backed by two exchange arguments.
Maximum flow falls to the idea of the residual network and is matched exactly by minimum cuts, one of the great
duality theorems of the subject. Matching is a special case of flow, and its weighted and "stable" versions bring in
prices and proposals.*

!!! abstract "In this chapter"
    **You will learn:**

    - what a minimum spanning tree is, and the cut and cycle properties that make greedy algorithms correct for it
    - Kruskal's algorithm with union-find, Prim's with a heap, and Borůvka's, with proofs and running times
    - flow networks, residual graphs and augmenting paths; the Ford-Fulkerson method and its pitfalls
    - the max-flow min-cut theorem, proved, and how to read a minimum cut off the final residual graph
    - Edmonds-Karp in $O(VE^2)$ and Dinic's algorithm in $O(V^2E)$, with the distance argument behind both
    - bipartite matching as flow, Hall's and König's theorems, and Hopcroft-Karp in $O(E\sqrt V)$
    - the assignment problem and the Hungarian algorithm, min-cost flow, and stable matching by Gale-Shapley

    **You need:** [Chapter 15](15-Graphs-and-Graph-Search.md) (BFS, DFS) and [Chapter 16](16-Shortest-Paths.md)
    (Dijkstra, Bellman-Ford, potentials); union-find from [Chapter 10](10-Union-Find-and-Range-Queries.md) and heaps
    from [Chapter 9](09-Heaps-and-Priority-Queues.md); the greedy exchange argument of
    [Chapter 12](12-Greedy-Algorithms.md).

    **Levels:** 17.1 and 17.2 are intermediate; 17.3 to 17.6 are intermediate to advanced; 17.7 is advanced.

## 17.1 Minimum spanning trees: the cut and cycle properties

A new settlement has seven buildings, and engineers know what it would cost to lay a cable between certain pairs.
They want every building connected (directly or through others) at the least total cost. Two observations shape
the answer. A cheapest solution never contains a cycle: on a cycle, one cable can be removed and everything stays
connected, more cheaply. And a connected set of cables with no cycle is a **tree**.

**Definitions.** Let $G = (V, E)$ be a connected undirected graph with a weight $w(e)$ on each edge. A **spanning
tree** is a subset $T \subseteq E$ that connects all the vertices and has no cycle. Its weight is $w(T) =
\sum_{e \in T} w(e)$. A **minimum spanning tree** (MST) is a spanning tree of least weight.

**Fact.** Every spanning tree of a graph with $V$ vertices has exactly $V - 1$ edges. *Proof.* Start with $V$
isolated vertices, $V$ components, and add the tree's edges one at a time. An edge that joins two vertices already
in the same component would close a cycle, so each edge joins two different components and reduces their number by
exactly one. At the end there is one component, so there were $V - 1$ edges. $\square$

The number of spanning trees can be huge (Cayley's formula: the complete graph on $n$ vertices has $n^{n-2}$), so
trying them all is hopeless. Two properties make greedy algorithms work instead. They use one more word: a **cut**
$(S, V \setminus S)$ is a split of the vertices into two non-empty sides, and an edge **crosses** the cut if its
ends lie on different sides.

<figure class="mars-fig" markdown="0">
<svg viewBox="0 0 640 330" role="img" aria-label="A weighted graph on seven vertices A to G with its minimum spanning tree of weight 39 highlighted, and a cut separating A, B and D from the rest">
<path d="M 30 30 L 228 10 L 245 58 L 150 215 L 75 215 L 25 120 Z" stroke-linejoin="round" fill="#7ccf9a" fill-opacity="0.15" stroke="currentColor" stroke-dasharray="5 4" stroke-opacity="0.7"/>
<line x1="76.6" y1="66.4" x2="183.4" y2="43.6" stroke="#eea66f" stroke-width="4"/>
<text x="127.5" y="47.8" font-size="13" text-anchor="middle" fill="currentColor">7</text>
<line x1="67.0" y1="85.5" x2="103.0" y2="164.5" stroke="#eea66f" stroke-width="4"/>
<text x="95.9" y="124.6" font-size="13" text-anchor="middle" fill="currentColor">5</text>
<line x1="216.6" y1="43.6" x2="323.4" y2="66.4" stroke="currentColor" stroke-width="1.3"/>
<text x="272.5" y="47.8" font-size="13" text-anchor="middle" fill="currentColor">8</text>
<line x1="190.8" y1="54.3" x2="119.2" y2="165.7" stroke="currentColor" stroke-width="1.3"/>
<text x="165.1" y="121.0" font-size="13" text-anchor="middle" fill="currentColor">9</text>
<line x1="206.7" y1="55.6" x2="253.3" y2="164.4" stroke="#eea66f" stroke-width="4"/>
<text x="219.0" y="119.3" font-size="13" text-anchor="middle" fill="currentColor">7</text>
<line x1="330.0" y1="83.7" x2="270.0" y2="166.3" stroke="#eea66f" stroke-width="4"/>
<text x="309.7" y="136.6" font-size="13" text-anchor="middle" fill="currentColor">5</text>
<line x1="127.0" y1="180.0" x2="243.0" y2="180.0" stroke="currentColor" stroke-width="1.3"/>
<text x="185.0" y="172.6" font-size="13" text-anchor="middle" fill="currentColor">15</text>
<line x1="117.0" y1="195.5" x2="153.0" y2="274.5" stroke="#eea66f" stroke-width="4"/>
<text x="124.1" y="244.5" font-size="13" text-anchor="middle" fill="currentColor">6</text>
<line x1="248.6" y1="192.6" x2="171.4" y2="277.4" stroke="currentColor" stroke-width="1.3"/>
<text x="218.9" y="247.6" font-size="13" text-anchor="middle" fill="currentColor">8</text>
<line x1="269.1" y1="194.3" x2="320.9" y2="275.7" stroke="#eea66f" stroke-width="4"/>
<text x="305.1" y="233.1" font-size="13" text-anchor="middle" fill="currentColor">9</text>
<line x1="177.0" y1="290.0" x2="313.0" y2="290.0" stroke="currentColor" stroke-width="1.3"/>
<text x="245.0" y="306.6" font-size="13" text-anchor="middle" fill="currentColor">11</text>
<text x="420" y="40" font-size="13" text-anchor="start" fill="currentColor">MST weight 5+5+6+7+7+9 = 39</text>
<text x="420" y="70" font-size="12" text-anchor="start" fill="currentColor">thick: tree edges</text>
<text x="420" y="120" font-size="12" text-anchor="start" fill="currentColor">shaded side S = {A, B, D}</text>
<text x="420" y="142" font-size="12" text-anchor="start" fill="currentColor">edges crossing the cut:</text>
<text x="420" y="164" font-size="12" text-anchor="start" fill="currentColor">B–C 8, B–E 7, D–E 15, D–F 6</text>
<text x="420" y="192" font-size="12" text-anchor="start" fill="currentColor">lightest crossing edge: D–F 6,</text>
<text x="420" y="212" font-size="12" text-anchor="start" fill="currentColor">so it is in every MST</text>
<text x="420" y="250" font-size="12" text-anchor="start" fill="currentColor">cycle B, C, E: heaviest edge</text>
<text x="420" y="270" font-size="12" text-anchor="start" fill="currentColor">B–C 8 is in no MST</text>
<circle cx="60" cy="70" r="17" fill="#9cc9ea" fill-opacity="0.55" stroke="currentColor" stroke-width="1.5"/>
<text x="60" y="74.9" font-size="14" text-anchor="middle" fill="currentColor">A</text>
<circle cx="200" cy="40" r="17" fill="#9cc9ea" fill-opacity="0.55" stroke="currentColor" stroke-width="1.5"/>
<text x="200" y="44.9" font-size="14" text-anchor="middle" fill="currentColor">B</text>
<circle cx="340" cy="70" r="17" fill="#9cc9ea" fill-opacity="0.55" stroke="currentColor" stroke-width="1.5"/>
<text x="340" y="74.9" font-size="14" text-anchor="middle" fill="currentColor">C</text>
<circle cx="110" cy="180" r="17" fill="#9cc9ea" fill-opacity="0.55" stroke="currentColor" stroke-width="1.5"/>
<text x="110" y="184.9" font-size="14" text-anchor="middle" fill="currentColor">D</text>
<circle cx="260" cy="180" r="17" fill="#9cc9ea" fill-opacity="0.55" stroke="currentColor" stroke-width="1.5"/>
<text x="260" y="184.9" font-size="14" text-anchor="middle" fill="currentColor">E</text>
<circle cx="160" cy="290" r="17" fill="#9cc9ea" fill-opacity="0.55" stroke="currentColor" stroke-width="1.5"/>
<text x="160" y="294.9" font-size="14" text-anchor="middle" fill="currentColor">F</text>
<circle cx="330" cy="290" r="17" fill="#9cc9ea" fill-opacity="0.55" stroke="currentColor" stroke-width="1.5"/>
<text x="330" y="294.9" font-size="14" text-anchor="middle" fill="currentColor">G</text>
</svg>
<figcaption>Figure 17.1. The chapter's MST example. The six thick edges form its minimum spanning tree, of weight 39. The shaded region is one side of a cut: the lightest edge leaving it, D–F of weight 6, must be in the tree (the cut property), and the heaviest edge on any cycle, such as B–C on the cycle B, C, E, cannot be (the cycle property).</figcaption>
</figure>

**Theorem 17.1 (cut property).** For any cut, a lightest edge crossing it belongs to some MST. If it is the only
lightest crossing edge, it belongs to every MST.

*Proof.* Let $e = \{u, v\}$ be a lightest edge crossing the cut $(S, V \setminus S)$, with $u \in S$. Take any MST
$T$. If $e \in T$, done. Otherwise, adding $e$ to $T$ creates exactly one cycle (the path in $T$ from $u$ to $v$,
plus $e$). That path starts in $S$ and ends outside it, so it contains some other edge $e'$ crossing the cut. Swap:
$T' = T - e' + e$. It still has $V - 1$ edges and is still connected (any route that used $e'$ can go round the
cycle instead), so it is a spanning tree, and $w(T') = w(T) - w(e') + w(e) \le w(T)$ because $e$ is a lightest
crossing edge. So $T'$ is an MST containing $e$. If $e$ is strictly lighter than every other crossing edge, then
$w(T') < w(T)$ whenever $e \notin T$, contradicting that $T$ is minimum; so every MST contains $e$. $\square$

**Theorem 17.2 (cycle property).** If an edge $e$ is strictly the heaviest edge on some cycle, then no MST contains
it.

*Proof.* Suppose an MST $T$ contains $e = \{u, v\}$. Removing $e$ splits $T$ into two pieces, one containing $u$
and one containing $v$: a cut. The rest of the cycle is a path from $u$ to $v$ avoiding $e$, so it has an edge $e'$
crossing that cut, and $w(e') < w(e)$. Then $T - e + e'$ is a spanning tree lighter than $T$: a contradiction.
$\square$

In Figure 17.1, take $S = \{A, B, D\}$. The crossing edges are B–C 8, B–E 7, D–E 15 and D–F 6, so D–F is in every
MST. On the cycle B, C, E the weights are 8, 5 and 7, so B–C 8 is in none.

**Corollary (uniqueness).** If all edge weights are different, the MST is unique. (Every MST edge is the unique
lightest edge across the cut that removing it creates; exercise 2 does it carefully.) With ties there can be several
MSTs, all of the same weight. The example graph has ties (two 5s, two 7s, two 8s, two 9s) but still a single MST,
as a brute-force check over all 6-edge subsets confirms (exercise 1).

**The generic algorithm.** Start with no edges. Repeatedly find a cut that no chosen edge crosses, and add a lightest
edge crossing it. By the cut property (applied with care to the MST that contains the edges chosen so far, the same
swap argument), every chosen edge keeps us inside some MST, and after $V - 1$ steps we have one. Kruskal, Prim and
Borůvka are three ways of choosing the cuts.

## 17.2 Kruskal, Prim and Borůvka

### Kruskal's algorithm

Sort the edges from lightest to heaviest. Take each one in turn and keep it unless it would close a cycle with the
edges already kept.

```text
KRUSKAL(G):
    T = empty;  make each vertex its own set
    for each edge {u, v} in increasing order of weight:
        if find(u) != find(v):        # different trees: no cycle
            add {u, v} to T;  union(u, v)
```

**Correctness.** When Kruskal keeps $\{u, v\}$, let $S$ be the tree (component of kept edges) containing $u$. No
kept edge crosses the cut $(S, V \setminus S)$, and every lighter edge crossing it was already considered and
skipped or kept; a skipped edge joins two vertices of one component, so it does not cross this cut, and a kept edge
would have merged its two sides. So $\{u, v\}$ is a lightest edge crossing the cut, and the cut property says it is
safe. An edge that is skipped closes a cycle in which it is the heaviest edge (all the others were considered
earlier), so the cycle property (with ties handled by the same exchange) says nothing is lost.

**Running time.** Sorting costs $O(E \log E) = O(E \log V)$ (since $E \le V^2$). The cycle test needs to know
whether $u$ and $v$ are in the same tree as edges are added, which is exactly the union-find structure of
[Chapter 10](10-Union-Find-and-Range-Queries.md): with union by size and path compression, $2E$ finds and $V - 1$
unions take $O(E\,\alpha(V))$, where $\alpha$ is the inverse Ackermann function, at most 4 for any input that fits
in our universe. So the sort dominates, and Kruskal runs in $O(E \log V)$. If the edges come already sorted, or
with small integer weights that can be sorted in linear time ([Chapter 6](06-Sorting-in-Linear-Time-and-Selection.md)),
it is almost linear.

**Trace on Figure 17.1.** The program prints:

| Edge | Weight | Decision | Trees after |
|---|---|---|---|
| A–D | 5 | take | {A,D} |
| C–E | 5 | take | {A,D} {C,E} |
| D–F | 6 | take | {A,D,F} {C,E} |
| A–B | 7 | take | {A,B,D,F} {C,E} |
| B–E | 7 | take | {A,B,C,D,E,F} |
| B–C | 8 | skip: B and C already joined | |
| E–F | 8 | skip | |
| B–D | 9 | skip | |
| E–G | 9 | take | all seven |
| F–G | 11 | skip | |
| D–E | 15 | skip | |

Six edges, weight $5 + 5 + 6 + 7 + 7 + 9 = 39$. (An implementation may stop as soon as it has $V - 1$ edges.)

Joseph Kruskal published the algorithm in 1956, in a two-page note in the *Proceedings of the American Mathematical
Society* whose main subject was the travelling salesman problem.

### Prim's algorithm

Prim's algorithm grows a single tree from a root. At each step it takes the lightest edge leaving the tree.

```text
PRIM(G, r):
    tree = {r}
    while tree has fewer than V vertices:
        add the lightest edge {u, v} with u in tree and v not in tree
        add v to tree
```

**Correctness** is the cut property with $S$ = the current tree, every time. **Implementation** is Dijkstra's
algorithm with a different key: keep, for each vertex outside the tree, the weight of the lightest edge joining it
to the tree, and pick the smallest. With a binary heap this costs $O(E \log V)$; with a plain array and a scan for
the minimum, $O(V^2)$, which is better for dense graphs; with a Fibonacci heap, $O(E + V \log V)$. The program uses
the lazy heap of [Chapter 16](16-Shortest-Paths.md): push every edge leaving a newly added vertex, and skip edges
whose far end has joined the tree in the meantime.

From A it adds A–D 5, D–F 6, A–B 7, B–E 7, E–C 5 and E–G 9: the same six edges, in a different order. Notice E–C 5
comes late, because C cannot be reached cheaply until E is in the tree. The reference pages
[Kruskal's algorithm](../../graphs/kruskal.md) and [Prim's algorithm](../../graphs/prim.md) animate both.

The method was first published by Vojtěch Jarník in 1930, in Czech, and rediscovered by Robert Prim in 1957 and by
Dijkstra in his 1959 paper; it is also called Jarník's or the Prim-Jarník algorithm.

### Borůvka's algorithm

The oldest MST algorithm works on all components at once. In each round, every component picks the lightest edge
leaving it, and all those edges are added together.

```text
BORUVKA(G):
    T = empty;  every vertex is a component
    while there is more than one component:
        for each component C:  cheapest[C] = lightest edge leaving C
        add all the cheapest edges to T, merging components
```

**Correctness.** Each chosen edge is a lightest edge across the cut (C, rest), so each is safe on its own. Adding
them *together* is also safe provided ties are broken consistently: compare edges by the pair (weight, a fixed
label such as their end-points), so that all weights are effectively distinct. Then each chosen edge is the unique
lightest across its cut, so it is in the unique MST under that order, and a set of edges of one tree has no cycle.
Without a consistent tie-break, two components joined by two equal edges could pick different ones and make a
cycle. The program breaks ties by comparing the triple (weight, u, v).

**Running time.** Every component gets merged with at least one other in each round, so the number of components at
least halves, and there are at most $\log_2 V$ rounds. Each round scans all edges in $O(E)$ with union-find. Total
$O(E \log V)$. On the example, round 1 adds A–D 5, C–E 5, D–F 6, A–B 7 and E–G 9 (five edges, leaving two
components, {A, B, D, F} and {C, E, G}), and round 2 adds B–E 7.

Borůvka's algorithm is the natural one for parallel computers, since every component works independently, and it is
an ingredient of the fastest known MST algorithms.

### History and the frontier

Otakar Borůvka published his algorithm in 1926 to design an efficient electrical network for the region of
Moravia; it is the earliest of all. Jarník's paper of 1930 was a direct reply to it. Kruskal (1956) and Prim (1957)
followed, and Graham and Hell's 1985 article "On the history of the minimum spanning tree
problem" tells the story in full.

How fast can an MST be found? Karger, Klein and Tarjan (1995) gave a randomized algorithm with expected time
$O(V + E)$. The best deterministic bound is Chazelle's (2000), $O(E\,\alpha(E, V))$. Pettie and Ramachandran (2002)
gave a deterministic algorithm that is provably optimal, but nobody knows what its running time is as a function of
$V$ and $E$: it is somewhere between linear and Chazelle's bound. Whether a deterministic linear-time MST algorithm
exists is an open problem.

## 17.3 Network flow: Ford-Fulkerson and residual graphs

Now a different question. Water flows from a reservoir $s$ to a city $t$ through pipes, each with a maximum rate.
How much can arrive per second? The same question asks how many trains can run from one city to another, how much
data can cross a network, or (as 17.6 will show) how many people can be given jobs.

**Definitions.** A **flow network** is a directed graph with a **source** $s$, a **sink** $t$, and a **capacity**
$c(u, v) \ge 0$ on each edge. A **flow** assigns a number $f(u, v)$ to each edge such that

- **capacity:** $0 \le f(u, v) \le c(u, v)$ for every edge;
- **conservation:** at every vertex other than $s$ and $t$, flow in equals flow out:
  $\sum_{u} f(u, v) = \sum_{w} f(v, w)$.

The **value** of the flow, $|f|$, is the net flow leaving the source: $\sum_v f(s, v) - \sum_v f(v, s)$. The
**maximum flow problem** asks for a flow of largest value.

Figure 17.2 shows the chapter's network, with a maximum flow of value 15 already filled in.

<figure class="mars-fig" markdown="0">
<svg viewBox="0 0 560 300" role="img" aria-label="A flow network from s to t with flow over capacity on each edge, total flow 15, and a dashed minimum cut crossing s to b, a to b and a to c">
<line x1="63.5" y1="141.3" x2="169.8" y2="73.0" stroke="#eea66f" stroke-width="3.4000000000000004"/>
<polygon points="176.5,68.7 171.4,77.3 166.5,69.7" fill="#eea66f"/>
<text x="112.4" y="97.4" font-size="12" text-anchor="middle" fill="currentColor">7/10</text>
<line x1="63.5" y1="158.7" x2="169.8" y2="227.0" stroke="#eea66f" stroke-width="3.7"/>
<polygon points="176.5,231.3 166.5,230.3 171.4,222.7" fill="#eea66f"/>
<text x="112.4" y="211.0" font-size="12" text-anchor="middle" fill="currentColor">8/8</text>
<line x1="190.0" y1="76.0" x2="190.0" y2="216.0" stroke="#eea66f" stroke-width="1.9"/>
<polygon points="190.0,224.0 185.5,215.0 194.5,215.0" fill="#eea66f"/>
<text x="170.0" y="154.2" font-size="12" text-anchor="middle" fill="currentColor">2/2</text>
<line x1="206.0" y1="60.0" x2="326.0" y2="60.0" stroke="#eea66f" stroke-width="2.8"/>
<polygon points="334.0,60.0 325.0,64.5 325.0,55.5" fill="#eea66f"/>
<text x="270.0" y="76.2" font-size="12" text-anchor="middle" fill="currentColor">5/5</text>
<line x1="206.0" y1="240.0" x2="326.0" y2="240.0" stroke="#eea66f" stroke-width="4.3"/>
<polygon points="334.0,240.0 325.0,244.5 325.0,235.5" fill="#eea66f"/>
<text x="270.0" y="256.2" font-size="12" text-anchor="middle" fill="currentColor">10/10</text>
<line x1="339.4" y1="72.0" x2="205.9" y2="222.1" stroke="currentColor" stroke-width="1.3"/>
<polygon points="200.6,228.0 203.2,218.3 210.0,224.3" fill="currentColor"/>
<text x="307.5" y="139.2" font-size="12" text-anchor="middle" fill="currentColor">0/7</text>
<line x1="363.5" y1="68.7" x2="469.8" y2="137.0" stroke="#eea66f" stroke-width="2.8"/>
<polygon points="476.5,141.3 466.5,140.3 471.4,132.7" fill="#eea66f"/>
<text x="427.6" y="97.4" font-size="12" text-anchor="middle" fill="currentColor">5/7</text>
<line x1="350.0" y1="224.0" x2="350.0" y2="84.0" stroke="currentColor" stroke-width="1.3"/>
<polygon points="350.0,76.0 354.5,85.0 345.5,85.0" fill="currentColor"/>
<text x="330.0" y="154.2" font-size="12" text-anchor="middle" fill="currentColor">0/6</text>
<line x1="363.5" y1="231.3" x2="469.8" y2="163.0" stroke="#eea66f" stroke-width="4.3"/>
<polygon points="476.5,158.7 471.4,167.3 466.5,159.7" fill="#eea66f"/>
<text x="427.6" y="211.0" font-size="12" text-anchor="middle" fill="currentColor">10/10</text>
<polyline points="270,12 230,150 80,272" fill="none" stroke="#7ccf9a" stroke-width="2.5" stroke-dasharray="7 5"/>
<text x="120" y="290" font-size="12" text-anchor="middle" fill="currentColor">min cut: 8 + 2 + 5 = 15</text>
<circle cx="50" cy="150" r="16" fill="#eea66f" fill-opacity="0.55" stroke="currentColor" stroke-width="1.5"/>
<text x="50" y="154.9" font-size="14" text-anchor="middle" fill="currentColor">s</text>
<circle cx="190" cy="60" r="16" fill="#9cc9ea" fill-opacity="0.55" stroke="currentColor" stroke-width="1.5"/>
<text x="190" y="64.9" font-size="14" text-anchor="middle" fill="currentColor">a</text>
<circle cx="190" cy="240" r="16" fill="#9cc9ea" fill-opacity="0.55" stroke="currentColor" stroke-width="1.5"/>
<text x="190" y="244.9" font-size="14" text-anchor="middle" fill="currentColor">b</text>
<circle cx="350" cy="60" r="16" fill="#9cc9ea" fill-opacity="0.55" stroke="currentColor" stroke-width="1.5"/>
<text x="350" y="64.9" font-size="14" text-anchor="middle" fill="currentColor">c</text>
<circle cx="350" cy="240" r="16" fill="#9cc9ea" fill-opacity="0.55" stroke="currentColor" stroke-width="1.5"/>
<text x="350" y="244.9" font-size="14" text-anchor="middle" fill="currentColor">d</text>
<circle cx="490" cy="150" r="16" fill="#eea66f" fill-opacity="0.55" stroke="currentColor" stroke-width="1.5"/>
<text x="490" y="154.9" font-size="14" text-anchor="middle" fill="currentColor">t</text>
</svg>
<figcaption>Figure 17.2. The flow network of 17.3 to 17.5 with a maximum flow; each label is flow/capacity, and orange edges carry flow. The green dashed line is a minimum cut: S = {s, a} on its left. Every edge crossing it from S to the other side is full, and its capacities add up to 15, the value of the flow.</figcaption>
</figure>

### A first idea, and why it fails

A natural greedy method: find any path from $s$ to $t$ with spare capacity on every edge, push as much as fits,
and repeat until no such path exists. It can get stuck too early. In the network with edges s→a, s→b, a→b, a→t,
b→t, each of capacity 1, the path s, a, b, t carries 1 unit, and after that every path is blocked (s→a and b→t are
full). Yet the maximum flow is 2: s, a, t and s, b, t. The first path made a bad choice, sending flow along a→b, and
the greedy method cannot take it back.

### The residual graph

The fix is to allow **undoing**. Sending flow back against an edge that carries flow is the same as cancelling some
of it. Given a flow $f$, the **residual capacity** is

$$
c_f(u, v) =
\begin{cases}
c(u, v) - f(u, v) & \text{for an edge } u \to v \text{ (spare room)},\\
f(v, u) & \text{for the reverse of an edge } v \to u \text{ (flow that can be cancelled)},
\end{cases}
$$

and the **residual graph** $G_f$ has an edge wherever the residual capacity is positive. An **augmenting path** is
a path from $s$ to $t$ in $G_f$; its **bottleneck** $b$ is the smallest residual capacity on it. **Augmenting**
pushes $b$ along it: add $b$ to the flow on forward edges and subtract $b$ on reverse ones.

**Lemma 17.3.** Augmenting along an augmenting path gives a valid flow whose value is larger by $b > 0$.

*Proof.* Capacities: a forward edge gains at most its spare room, and a reverse edge cancels at most the flow its
real edge carried, so every flow stays between 0 and the capacity. Conservation: a residual edge from $x$ to $y$,
whether it adds flow to a real edge $x \to y$ or cancels flow on a real edge $y \to x$, moves $b$ units of *net*
flow from $x$ to $y$. At an inner vertex of the path, the entering residual edge brings $b$ more net flow in and the
leaving one takes $b$ more net flow out, so the balance is unchanged. The path leaves $s$ and never returns, so the
net flow out of $s$ grows by $b$. $\square$

In the stuck example, the residual graph after s, a, b, t contains the reverse edge b→a, so s, b, a, t is an
augmenting path. Pushing 1 along it cancels the flow on a→b and leaves s→a→t and s→b→t: value 2.

### The Ford-Fulkerson method

```text
FORD-FULKERSON(G, s, t):
    f = 0 on every edge
    while the residual graph G_f has a path from s to t:
        augment along it
```

Lester Ford Jr. and Delbert Fulkerson published the method in 1956. It is called a *method* rather than an algorithm
because it does not say which augmenting path to choose; 17.5 shows that the choice matters enormously.

**In code.** The program stores the residual graph directly: every edge is created together with its reverse, of
capacity 0, at the neighbouring index, so edge `e` and edge `e ^ 1` are partners (the `^` is bitwise exclusive or,
which flips the last bit: 0 ↔ 1, 2 ↔ 3, and so on). Pushing $b$ along `e` does `cap[e] -= b` and `cap[e ^ 1] += b`.
The flow on an original edge is the capacity its reverse has gained.

With depth-first search choosing the path (and neighbours tried in the order the edges were added), the program
finds five augmenting paths:

```
   push  2 along s a b d c t
   push  5 along s a c b d t
   push  3 along s b d c t
   push  2 along s b c t
   push  3 along s b c d t
```

The second path uses c→b, a real edge. The fourth, s, b, c, t, goes from $b$ to $c$, against the edge c→b: it
cancels 2 of the 5 units the second path sent along c→b. The fifth cancels the 3 units on d→c. The total is $2 + 5
+ 3 + 2 + 3 = 15$, the same as Edmonds-Karp's three paths in 17.5. Different paths, different final flows on some
edges, the same maximum value.

**Integrality.** If all capacities are integers, every bottleneck is a positive integer, the flow stays integral
throughout, and each augmentation adds at least 1. So Ford-Fulkerson stops after at most $|f^*|$ augmentations,
where $f^*$ is a maximum flow, and each takes $O(E)$ with BFS or DFS: total $O(E\,|f^*|)$. Two consequences: **an
integer network always has an integer maximum flow** (the integrality theorem), which is what makes flows useful for
matching and other combinatorial problems; and the running time depends on the *size of the numbers*, not just the
graph, which 17.5 exploits. With irrational capacities the method may fail to stop, and its flow value can even
converge to something less than the maximum; Ford and Fulkerson gave such an example themselves, and Zwick (1995)
found the smallest ones.

## 17.4 The max-flow min-cut theorem

How do we know that 15 is the maximum in Figure 17.2? We need a certificate, a short reason no flow can do better.
Cuts provide it.

**Definitions.** An **s-t cut** $(S, T)$ splits the vertices into $S \ni s$ and $T = V \setminus S \ni t$. Its
**capacity** is the total capacity of the edges going from $S$ to $T$:

$$
c(S, T) = \sum_{u \in S,\ v \in T} c(u, v).
$$

Edges from $T$ back to $S$ do not count. The **net flow across the cut** is the flow on edges from $S$ to $T$ minus
the flow on edges from $T$ to $S$.

**Lemma 17.4 (flow across any cut).** For every flow $f$ and every s-t cut $(S, T)$, the net flow across the cut
equals $|f|$, and therefore $|f| \le c(S, T)$.

*Proof.* Add up, over all vertices $v \in S$, (flow out of $v$) minus (flow into $v$). For $v = s$ this is $|f|$;
for every other $v \in S$ it is 0 by conservation. So the total is $|f|$. Now count the same sum edge by edge. An
edge with both ends in $S$ is counted once as "out" and once as "in", contributing 0. An edge from $S$ to $T$
contributes its flow; an edge from $T$ to $S$ contributes minus its flow; edges inside $T$ do not appear. So $|f|$
equals the net flow across the cut. Finally, the net flow is at most the flow on $S \to T$ edges, which is at most
their capacities: $|f| \le c(S, T)$. $\square$

So every cut gives an upper bound on every flow. The remarkable fact is that the best upper bound is always reached.

**Theorem 17.5 (max-flow min-cut).** For a flow $f$ in a network, the following are equivalent:

1. $f$ is a maximum flow;
2. the residual graph $G_f$ has no augmenting path;
3. $|f| = c(S, T)$ for some s-t cut $(S, T)$.

So the maximum value of a flow equals the minimum capacity of a cut.

*Proof.* (1 ⇒ 2) If there were an augmenting path, Lemma 17.3 would give a larger flow.

(2 ⇒ 3) Suppose $G_f$ has no path from $s$ to $t$. Let $S$ be the set of vertices reachable from $s$ in $G_f$, and
$T$ the rest; $t \in T$, so this is an s-t cut. Take any edge $u \to v$ with $u \in S$, $v \in T$: if it had spare
room, $v$ would be reachable, so $f(u, v) = c(u, v)$, full. Take any edge $v \to u$ with $v \in T$, $u \in S$: if
it carried flow, its reverse would be a residual edge from $u$ to $v$, making $v$ reachable, so $f(v, u) = 0$. The
net flow across the cut is therefore exactly $c(S, T)$, and by Lemma 17.4 it is also $|f|$.

(3 ⇒ 1) By Lemma 17.4, every flow $g$ has $|g| \le c(S, T) = |f|$. $\square$

The proof is also an algorithm for the cut. When Ford-Fulkerson stops, search the residual graph from $s$; the
reachable vertices form the $S$ side of a minimum cut. The program does this after Dinic's algorithm and prints

```
  min cut S = {'a', 's'}  edges [('s', 'b', 8), ('a', 'b', 2), ('a', 'c', 5)]  capacity 15
```

Three full edges, $8 + 2 + 5 = 15$, the green line in Figure 17.2. Now nobody needs to trust the algorithm: anyone
can check that the flow is valid and has value 15, and that the cut has capacity 15. Lemma 17.4 does the rest.

**Uses of minimum cuts.** The theorem is used as often for its cuts as for its flows. In **image segmentation**, the
pixels are vertices, a source stands for "foreground" and a sink for "background", and a minimum cut separates the
picture along boundaries that are cheap to cut. In **project selection**, a minimum cut chooses the most profitable
set of projects whose prerequisites are also chosen. **Menger's theorem** (1927), that the largest number of
edge-disjoint paths from $s$ to $t$ equals the smallest number of edges whose removal separates them, is max-flow
min-cut with all capacities 1.

**History.** In 1955 T. E. Harris and F. S. Ross wrote a then-classified RAND report on the capacity of the Soviet
and Eastern European railway network, framed as finding a bottleneck: a minimum cut. Ford and Fulkerson, also at
RAND, proved the theorem in 1956; Elias, Feinstein and Shannon proved it independently the same year for
communication networks. Alexander Schrijver's article "On the history of the transportation and maximum flow
problems" (2002) tells the story, including the declassification of the Harris-Ross report in 1999.

## 17.5 Edmonds-Karp and Dinic

Figure 17.4 shows why the choice of augmenting path matters.

<figure class="mars-fig" markdown="0">
<svg viewBox="0 0 640 200" role="img" aria-label="Four vertices s, a, b, t; edges s to a, s to b, a to t, b to t of capacity 1000 and a middle edge a to b of capacity 1">
<line x1="204.1" y1="92.4" x2="298.9" y2="41.4" stroke="currentColor" stroke-width="1.3"/>
<polygon points="305.9,37.6 300.1,45.8 295.9,37.9" fill="currentColor"/>
<text x="248.4" y="56.9" font-size="12" text-anchor="middle" fill="currentColor">1000</text>
<line x1="204.1" y1="107.6" x2="298.9" y2="158.6" stroke="currentColor" stroke-width="1.3"/>
<polygon points="305.9,162.4 295.9,162.1 300.1,154.2" fill="currentColor"/>
<text x="248.4" y="151.5" font-size="12" text-anchor="middle" fill="currentColor">1000</text>
<line x1="334.1" y1="37.6" x2="428.9" y2="88.6" stroke="currentColor" stroke-width="1.3"/>
<polygon points="435.9,92.4 425.9,92.1 430.1,84.2" fill="currentColor"/>
<text x="391.6" y="56.9" font-size="12" text-anchor="middle" fill="currentColor">1000</text>
<line x1="334.1" y1="162.4" x2="428.9" y2="111.4" stroke="currentColor" stroke-width="1.3"/>
<polygon points="435.9,107.6 430.1,115.8 425.9,107.9" fill="currentColor"/>
<text x="391.6" y="151.5" font-size="12" text-anchor="middle" fill="currentColor">1000</text>
<line x1="320.0" y1="46.0" x2="320.0" y2="146.0" stroke="#7ccf9a" stroke-width="2.5"/>
<polygon points="320.0,154.0 315.5,145.0 324.5,145.0" fill="#7ccf9a"/>
<text x="332.0" y="104.2" font-size="12" text-anchor="middle" fill="currentColor">1</text>
<circle cx="190" cy="100" r="16" fill="#eea66f" fill-opacity="0.55" stroke="currentColor" stroke-width="1.5"/>
<text x="190" y="104.9" font-size="14" text-anchor="middle" fill="currentColor">s</text>
<circle cx="320" cy="30" r="16" fill="#9cc9ea" fill-opacity="0.55" stroke="currentColor" stroke-width="1.5"/>
<text x="320" y="34.9" font-size="14" text-anchor="middle" fill="currentColor">a</text>
<circle cx="320" cy="170" r="16" fill="#9cc9ea" fill-opacity="0.55" stroke="currentColor" stroke-width="1.5"/>
<text x="320" y="174.9" font-size="14" text-anchor="middle" fill="currentColor">b</text>
<circle cx="450" cy="100" r="16" fill="#eea66f" fill-opacity="0.55" stroke="currentColor" stroke-width="1.5"/>
<text x="450" y="104.9" font-size="14" text-anchor="middle" fill="currentColor">t</text>
</svg>
<figcaption>Figure 17.4. A trap for Ford-Fulkerson. Paths that use the middle edge a→b (and then its reverse) carry 1 unit each, so an unlucky choice needs 2000 augmentations; two shortest paths, s→a→t and s→b→t, finish in 2.</figcaption>
</figure>

The maximum flow is 2000: s→a→t and s→b→t, 1000 each. But an augmenting path through the middle edge, s, a, b, t,
has bottleneck 1. After it, the residual graph has the reverse edge b→a, and s, b, a, t also has bottleneck 1 and
cancels the middle flow. Alternating forever between these two, each step adds 1. The program does exactly that
and reports `flow 2000 after 2000 augmentations of 1`. With capacities $10^9$ it would take two billion. The
running time $O(E\,|f^*|)$ is exponential in the number of digits of the capacities.

### Edmonds-Karp: shortest augmenting paths

Jack Edmonds and Richard Karp (1972), and independently Yefim Dinitz (1970), noticed that a simple rule fixes this:
**always augment along a shortest path (fewest edges) in the residual graph**, found by BFS. On Figure 17.4 that
takes two augmentations. On Figure 17.2 the program prints

```
   push  5 along s a c t
   push  8 along s b d t
   push  2 along s a b d t
```

three paths of lengths 3, 3 and 4.

**Theorem 17.6.** Edmonds-Karp performs at most $VE$ augmentations, so it runs in $O(VE^2)$ time, whatever the
capacities.

The proof needs one lemma. Write $\delta_f(s, v)$ for the BFS distance from $s$ to $v$ in the residual graph $G_f$.

**Lemma 17.7 (distances never shrink).** If Edmonds-Karp augments flow $f$ to $f'$, then $\delta_{f'}(s, v) \ge
\delta_f(s, v)$ for every $v$.

*Proof.* Suppose not, and among the vertices whose distance decreased pick $v$ with the smallest new distance
$\delta_{f'}(s, v)$. Let $u$ be the vertex before $v$ on a shortest path in $G_{f'}$, so $\delta_{f'}(s, u) =
\delta_{f'}(s, v) - 1$, and by the choice of $v$, $\delta_{f'}(s, u) \ge \delta_f(s, u)$. Was the edge $u \to v$
in $G_f$? If yes, $\delta_f(s, v) \le \delta_f(s, u) + 1 \le \delta_{f'}(s, u) + 1 = \delta_{f'}(s, v)$,
contradicting that $v$'s distance decreased. If no, the edge $u \to v$ appeared in the residual graph because the
augmentation pushed flow along $v \to u$, which lay on a shortest path in $G_f$; so $\delta_f(s, u) =
\delta_f(s, v) + 1$. Then $\delta_f(s, v) = \delta_f(s, u) - 1 \le \delta_{f'}(s, u) - 1 = \delta_{f'}(s, v) - 2$,
again a contradiction. $\square$

*Proof of Theorem 17.6.* Call a residual edge **critical** on an augmenting path if its residual capacity equals
the bottleneck; every augmentation has at least one, and it disappears from the residual graph afterwards. Suppose
$u \to v$ is critical when the flow is $f$. Since the path is shortest, $\delta_f(s, v) = \delta_f(s, u) + 1$.
For $u \to v$ to be critical again, it must first reappear, which requires a later augmentation, at flow $f'$, to
push along $v \to u$, so $\delta_{f'}(s, u) = \delta_{f'}(s, v) + 1 \ge \delta_f(s, v) + 1 = \delta_f(s, u) + 2$,
using the lemma. So between two times it is critical, $u$'s distance grows by at least 2. Distances are at most $V
- 1$ (or $u$ becomes unreachable), so each of the at most $2E$ possible residual edges is critical at most
$V/2$ times. Every augmentation has a critical edge, so there are at most $2E \cdot V/2 = VE$ augmentations, and each
costs $O(E)$ for the BFS: $O(VE^2)$. $\square$

### Dinic's algorithm: blocking flows in the level graph

Edmonds-Karp spends a BFS for every single path. Yefim Dinitz's 1970 algorithm (usually spelled Dinic in the West)
does one BFS and then finds *many* shortest paths at once.

- **Phase.** Run BFS from $s$ in the residual graph to get levels $\ell(v) = \delta_f(s, v)$. The **level graph**
  keeps only residual edges that go from level $i$ to level $i + 1$. Every shortest augmenting path lies in it.
- **Blocking flow.** In the level graph, push flow along paths from $s$ to $t$, by DFS, until every $s$–$t$ path in
  the level graph has a full edge. Edges found to lead to dead ends are skipped for the rest of the phase (the
  pointer `it[u]` in the code moves past them), so each edge is abandoned at most once per phase.

**Theorem 17.8.** Dinic's algorithm runs at most $V - 1$ phases, each in $O(VE)$, for $O(V^2 E)$ in total. With
unit capacities it runs in $O(E \min(\sqrt E, V^{2/3}))$, and on unit-capacity bipartite matching networks in
$O(E \sqrt V)$.

*Proof sketch.* After a blocking flow, every shortest path of the old length has a full edge, and new residual
edges only go backwards in level (from level $i+1$ to $i$), so every augmenting path in the new residual graph is
strictly longer: $\delta(s, t)$ increases each phase, and it is at most $V - 1$. Within a phase, each DFS either
reaches $t$ (and saturates at least one edge, which then leaves the level graph) or retreats from a dead end
(advancing a pointer). A path has at most $V$ edges, so each of the at most $E$ saturating pushes costs $O(V)$, and
pointer advances total $O(E)$: $O(VE)$ per phase. The unit-capacity bounds come from counting phases more cleverly:
after $\sqrt E$ phases the remaining flow is at most $\sqrt E$ (Even and Tarjan, 1975). $\square$

On Figure 17.2 the program prints `phases (distance to t, flow added): [(3, 13), (4, 2)]`. The first phase, with
$t$ at level 3, pushes 13 along paths of length 3 (s, a, c, t and s, b, d, t carry 5 and 8). The second, with $t$
at level 4, pushes the last 2 along s, a, b, d, t. Then $t$ is unreachable and the algorithm stops.

**Beyond.** The push-relabel method of Goldberg and Tarjan (1988) works locally, pushing excess flow from vertex to
vertex, and with good heuristics is among the fastest in practice, in $O(V^3)$ with the simplest (first-in, first-out) rule. In 2022 Chen,
Kyng, Liu, Peng, Probst Gutenberg and Sachdeva gave an algorithm for maximum flow, and even minimum-cost flow, in
almost-linear time $E^{1 + o(1)}$, using continuous optimisation rather than augmenting paths;
[Chapter 25](25-Where-Algorithms-Go.md) returns to it. In practice, a well-implemented Dinic or push-relabel is the
usual choice; libraries such as NetworkX in Python and the LEMON and OR-Tools libraries in C++ provide them.

## 17.6 Bipartite matching

Five people and five jobs; each person can do certain jobs (Figure 17.3). Give as many people as possible a job,
with no job given twice.

<figure class="mars-fig" markdown="0">
<svg viewBox="0 0 440 300" role="img" aria-label="A bipartite graph of five people and five jobs with a maximum matching of size four highlighted, and the source and sink of the flow version">
<line x1="28.4" y1="138.8" x2="96.2" y2="48.4" stroke="currentColor" stroke-width="0.8" stroke-dasharray="3 3"/>
<line x1="31.6" y1="142.2" x2="90.9" y2="102.8" stroke="currentColor" stroke-width="0.8" stroke-dasharray="3 3"/>
<line x1="34.0" y1="150.0" x2="87.0" y2="150.0" stroke="currentColor" stroke-width="0.8" stroke-dasharray="3 3"/>
<line x1="31.6" y1="157.8" x2="90.9" y2="197.2" stroke="currentColor" stroke-width="0.8" stroke-dasharray="3 3"/>
<line x1="28.4" y1="161.2" x2="96.2" y2="251.6" stroke="currentColor" stroke-width="0.8" stroke-dasharray="3 3"/>
<line x1="343.8" y1="48.4" x2="411.6" y2="138.8" stroke="currentColor" stroke-width="0.8" stroke-dasharray="3 3"/>
<line x1="349.1" y1="102.8" x2="408.4" y2="142.2" stroke="currentColor" stroke-width="0.8" stroke-dasharray="3 3"/>
<line x1="353.0" y1="150.0" x2="406.0" y2="150.0" stroke="currentColor" stroke-width="0.8" stroke-dasharray="3 3"/>
<line x1="349.1" y1="197.2" x2="408.4" y2="157.8" stroke="currentColor" stroke-width="0.8" stroke-dasharray="3 3"/>
<line x1="343.8" y1="251.6" x2="411.6" y2="161.2" stroke="currentColor" stroke-width="0.8" stroke-dasharray="3 3"/>
<line x1="132.2" y1="36.1" x2="307.8" y2="83.9" stroke="#eea66f" stroke-width="4"/>
<line x1="127.8" y1="44.6" x2="312.2" y2="195.4" stroke="currentColor" stroke-width="1.2"/>
<line x1="133.0" y1="90.0" x2="307.0" y2="90.0" stroke="currentColor" stroke-width="1.2"/>
<line x1="132.2" y1="156.1" x2="307.8" y2="203.9" stroke="currentColor" stroke-width="1.2"/>
<line x1="130.2" y1="139.0" x2="309.8" y2="41.0" stroke="#eea66f" stroke-width="4"/>
<line x1="133.0" y1="150.0" x2="307.0" y2="150.0" stroke="currentColor" stroke-width="1.2"/>
<line x1="130.2" y1="199.0" x2="309.8" y2="101.0" stroke="currentColor" stroke-width="1.2"/>
<line x1="133.0" y1="210.0" x2="307.0" y2="210.0" stroke="#eea66f" stroke-width="4"/>
<line x1="130.2" y1="259.0" x2="309.8" y2="161.0" stroke="#eea66f" stroke-width="4"/>
<line x1="133.0" y1="270.0" x2="307.0" y2="270.0" stroke="currentColor" stroke-width="1.2"/>
<circle cx="110" cy="30" r="23" fill="#9cc9ea" fill-opacity="0.55" stroke="currentColor" stroke-width="1.5"/>
<text x="110" y="33.9" font-size="11" text-anchor="middle" fill="currentColor">Ana</text>
<circle cx="110" cy="90" r="23" fill="#9cc9ea" fill-opacity="0.55" stroke="currentColor" stroke-width="1.5"/>
<text x="110" y="93.8" font-size="11" text-anchor="middle" fill="currentColor">Ben</text>
<circle cx="110" cy="150" r="23" fill="#9cc9ea" fill-opacity="0.55" stroke="currentColor" stroke-width="1.5"/>
<text x="110" y="153.8" font-size="11" text-anchor="middle" fill="currentColor">Cai</text>
<circle cx="110" cy="210" r="23" fill="#9cc9ea" fill-opacity="0.55" stroke="currentColor" stroke-width="1.5"/>
<text x="110" y="213.8" font-size="11" text-anchor="middle" fill="currentColor">Dev</text>
<circle cx="110" cy="270" r="23" fill="#9cc9ea" fill-opacity="0.55" stroke="currentColor" stroke-width="1.5"/>
<text x="110" y="273.9" font-size="11" text-anchor="middle" fill="currentColor">Eli</text>
<circle cx="330" cy="30" r="23" fill="#9cc9ea" fill-opacity="0.55" stroke="currentColor" stroke-width="1.5"/>
<text x="330" y="33.9" font-size="11" text-anchor="middle" fill="currentColor">cook</text>
<circle cx="330" cy="90" r="23" fill="#9cc9ea" fill-opacity="0.55" stroke="currentColor" stroke-width="1.5"/>
<text x="330" y="93.8" font-size="11" text-anchor="middle" fill="currentColor">drill</text>
<circle cx="330" cy="150" r="23" fill="#9cc9ea" fill-opacity="0.55" stroke="currentColor" stroke-width="1.5"/>
<text x="330" y="153.8" font-size="11" text-anchor="middle" fill="currentColor">fix</text>
<circle cx="330" cy="210" r="23" fill="#9cc9ea" fill-opacity="0.55" stroke="currentColor" stroke-width="1.5"/>
<text x="330" y="213.8" font-size="11" text-anchor="middle" fill="currentColor">map</text>
<circle cx="330" cy="270" r="23" fill="#9cc9ea" fill-opacity="0.55" stroke="currentColor" stroke-width="1.5"/>
<text x="330" y="273.9" font-size="11" text-anchor="middle" fill="currentColor">pilot</text>
<circle cx="20" cy="150" r="14" fill="#eea66f" fill-opacity="0.55" stroke="currentColor" stroke-width="1.5"/>
<text x="20" y="154.2" font-size="12" text-anchor="middle" fill="currentColor">s</text>
<circle cx="420" cy="150" r="14" fill="#eea66f" fill-opacity="0.55" stroke="currentColor" stroke-width="1.5"/>
<text x="420" y="154.2" font-size="12" text-anchor="middle" fill="currentColor">t</text>
</svg>
<figcaption>Figure 17.3. Five people and the jobs each can do. The thick edges are a maximum matching of size 4; Ben is left out, because Ana, Ben and Dev can between them do only drill and map. The dashed edges from s and to t, each of capacity 1, turn the problem into a maximum flow.</figcaption>
</figure>

**Definitions.** A **matching** in a graph is a set of edges with no vertex in common. It is **maximum** if no
matching has more edges, and **perfect** if it covers every vertex. A graph is **bipartite** if its vertices split
into a left side $L$ and a right side $R$ with every edge between them
([Chapter 15](15-Graphs-and-Graph-Search.md)). Matching problems are everywhere: workers and shifts, students and
projects, organ donors and recipients, taxis and riders.

### Matching as flow

Add a source $s$ with an edge of capacity 1 to every left vertex, a sink $t$ with an edge of capacity 1 from every
right vertex, and direct every original edge from left to right with capacity 1 (or anything $\ge 1$).

**Theorem 17.9.** The maximum matching size equals the maximum flow value in this network.

*Proof.* A matching $M$ gives a flow of value $|M|$: send 1 unit along $s \to u \to v \to t$ for each matched pair
$(u, v)$; capacities hold because each vertex is in at most one pair. Conversely, by integrality there is an integer
maximum flow; each edge carries 0 or 1. Each left vertex receives at most 1 unit from $s$, so it sends 1 unit along
at most one edge; each right vertex sends at most 1 unit to $t$, so it receives along at most one. The edges
carrying flow form a matching of size $|f|$. $\square$

The program builds this network and finds flow 4. Ford-Fulkerson's bound gives $O(VE)$ time here, since $|f^*| \le
V$. Its augmenting paths, read in the original graph, alternate between unmatched and matched edges, starting and
ending at unmatched vertices: they are **augmenting paths** in the matching sense.

**Berge's lemma (1957).** A matching $M$ is maximum if and only if there is no augmenting path for it. *Proof.* An
augmenting path $P$ has one more unmatched edge than matched ones, so swapping them ($M \oplus P$, the symmetric
difference) gives a matching one larger. Conversely, if $M'$ is larger than $M$, look at $M \oplus M'$: every vertex
touches at most one edge of each, so it splits into paths and cycles alternating between the two; cycles have equal
numbers of each, so some path has more edges of $M'$ than of $M$, and that path is augmenting for $M$. $\square$

### Hall's theorem: when can everyone be matched?

In Figure 17.3, Ana, Ben and Dev can between them do only drill and map. Three people, two jobs: at least one of
them must go without, so no matching covers all five people. Philip Hall proved in 1935 that this kind of
obstacle is the only one. For a set $A$ of left vertices, let $N(A)$ be the set of right vertices adjacent to some
vertex of $A$.

**Theorem 17.10 (Hall's marriage theorem).** A bipartite graph has a matching covering every left vertex if and
only if $|N(A)| \ge |A|$ for every subset $A \subseteq L$.

*Proof.* (Only if.) The vertices of $A$ are matched to $|A|$ different vertices, all in $N(A)$.

(If, via max-flow min-cut.) Use the flow network above but give the left-to-right edges capacity $\infty$ (a large
number). We show every s-t cut has capacity at least $|L|$; then the maximum flow, hence the maximum matching, is
$|L|$. Take a cut $(S, T)$ and let $A = L \cap S$. If some $v \in N(A)$ lies in $T$, an infinite edge crosses the
cut and we are done. Otherwise $N(A) \subseteq S$, and the cut contains the edges $s \to u$ for $u \in L \setminus
A$ (capacity $|L| - |A|$) and the edges $v \to t$ for $v \in N(A)$ (capacity $|N(A)| \ge |A|$). Total at least
$|L|$. $\square$

The program searches all subsets of people and prints the first violation it finds, `['Ana', 'Ben', 'Dev'] can only
do ['drill', 'map']`. Hall's condition is a certificate for "no": a small set that cannot be satisfied, checkable by
hand.

**König's theorem (1931).** In a bipartite graph, the size of a maximum matching equals the size of a minimum
**vertex cover** (a set of vertices touching every edge). This is max-flow min-cut again: from a minimum cut $(S,
T)$ the vertices $(L \cap T) \cup (R \cap S)$ form a cover of the same size. In Figure 17.3, {drill, map, Cai, Eli}
covers every edge, so no matching can have more than 4 (exercise 7). For general graphs the minimum vertex cover is
NP-hard ([Chapter 22](22-NP-Completeness.md)): bipartiteness is what makes it easy.

### Hopcroft-Karp: many augmenting paths at once

The augmenting-path method finds one path per search, $O(VE)$ in all. John Hopcroft and Richard Karp (1973) did for
matching what Dinic did for flow.

- **Phase.** BFS from all free left vertices at once, through alternating paths (unmatched edges left to right,
  matched edges right to left), until free right vertices are reached. This gives the length $k$ of the shortest
  augmenting paths and a layering.
- Then DFS finds a **maximal set of vertex-disjoint shortest augmenting paths** in the layers, and all are applied.

**Theorem 17.11.** Hopcroft-Karp runs in $O(E\sqrt V)$ time.

*Proof sketch.* Each phase costs $O(E)$. As in Dinic's algorithm, the shortest augmenting path length strictly
increases from phase to phase. After $\sqrt V$ phases, every augmenting path has more than $\sqrt V$ edges. Let $M$
be the current matching and $M^*$ a maximum one. The symmetric difference $M \oplus M^*$ contains $|M^*| - |M|$
vertex-disjoint augmenting paths for $M$ (Berge's argument), each with more than $\sqrt V$ vertices, so there are
fewer than $\sqrt V$ of them. Each later phase adds at least one edge to the matching, so at most $\sqrt V$ more
phases remain. Total $O(\sqrt V)$ phases of $O(E)$. $\square$

On the example the program finds a matching of size 4 in 2 phases: Ana–drill, Cai–cook, Dev–map, Eli–fix, with Ben
unmatched. It is one of several maximum matchings (the simpler method of exercise 8 finds Ben–drill, Ana–map instead).

**General graphs.** Without bipartiteness, an odd cycle can hide an augmenting path from a search. Jack Edmonds's
**blossom algorithm** (1965) shrinks such odd cycles and finds maximum matchings in polynomial time in any graph. His
paper, "Paths, trees, and flowers", is also where he argued that "efficient" should mean "polynomial time", the idea
behind the class P of [Chapter 22](22-NP-Completeness.md).

## 17.7 Assignment, min-cost flow and stable matching

*Level: advanced.*

### The assignment problem and the Hungarian algorithm

Now every pair has a cost: worker $i$ doing job $j$ costs $C[i][j]$. With $n$ workers and $n$ jobs, find a perfect
matching of least total cost. There are $n!$ assignments; the program's $4 \times 4$ example has 24, and brute force
finds the best, but at $n = 20$ there are about $2.4 \times 10^{18}$.

$$
C = \begin{pmatrix} 9 & 2 & 7 & 8 \\ 6 & 4 & 3 & 7 \\ 5 & 8 & 1 & 8 \\ 7 & 6 & 9 & 4 \end{pmatrix}
$$

The key idea is **prices**, or **potentials**. Give each worker a number $u_i$ and each job a number $v_j$ with

$$
u_i + v_j \le C[i][j] \quad \text{for every } i, j.
$$

Call such $(u, v)$ **feasible**, and call an edge $(i, j)$ **tight** if $u_i + v_j = C[i][j]$.

**Lemma 17.12 (the certificate).** For any feasible $(u, v)$ and any perfect matching $M$, $\mathrm{cost}(M) \ge
\sum_i u_i + \sum_j v_j$. If $M$ uses only tight edges, equality holds and $M$ is optimal.

*Proof.* Each worker and each job appears in exactly one pair of $M$, so $\mathrm{cost}(M) = \sum_{(i,j) \in M}
C[i][j] \ge \sum_{(i,j) \in M} (u_i + v_j) = \sum_i u_i + \sum_j v_j$, with equality exactly when every pair is
tight. Since the right-hand side does not depend on $M$, a tight perfect matching reaches the lower bound that every
matching obeys. $\square$

This is linear-programming duality ([Chapter 23](23-Approximation-and-Parameterized-Algorithms.md)) in miniature:
the potentials are the dual variables. The **Hungarian algorithm** keeps $(u, v)$ feasible and grows a matching of
tight edges. When it cannot extend the matching using tight edges, it searches from a free worker through tight
edges, and raises the potentials of the workers it reached and lowers those of the jobs it reached by the largest
amount $\Delta$ that keeps feasibility. That makes at least one new edge tight, and the search goes on. When a free
job is reached, the alternating path of tight edges is flipped and the matching grows by one.

Each search is like one run of Dijkstra's algorithm on reduced costs $C[i][j] - u_i - v_j \ge 0$ (the same
reweighting as Johnson's, Chapter 16), and there are $n$ searches; the program's implementation runs in $O(n^3)$.
On the example it finds potentials $u = (4, 6, 4, 4)$ and $v = (0, -2, -3, 0)$, whose reduced costs are

| | job 0 | job 1 | job 2 | job 3 |
|---|---|---|---|---|
| worker 0 | 5 | **0** | 6 | 4 |
| worker 1 | **0** | 0 | 0 | 1 |
| worker 2 | 1 | 6 | **0** | 4 |
| worker 3 | 3 | 4 | 8 | **0** |

All reduced costs are $\ge 0$ (feasible), and the bold zeros are a perfect matching of tight edges: worker 0 → job
1, worker 1 → job 0, worker 2 → job 2, worker 3 → job 3, with cost $2 + 6 + 1 + 4 = 13$. The potentials add up to
$18 - 5 = 13$ as well, so by Lemma 17.12 no assignment costs less, and the brute-force check over all 24 agrees.

**History.** Harold Kuhn published the method in 1955 and named it the Hungarian method because it rests on ideas of
two Hungarian mathematicians, Dénes König and Jenő Egerváry (1931). James Munkres showed in 1957 that it runs in
polynomial time; the $O(n^3)$ version came later (Edmonds and Karp, 1972; Tomizawa, 1971). In 2006 it was found
that Carl Gustav Jacobi had described an equivalent method in work published after his death in 1890. SciPy's
`scipy.optimize.linear_sum_assignment` solves the same problem.

### Min-cost flow

The assignment problem is one case of a general one: send a required amount of flow from $s$ to $t$, where each
edge has a capacity and a **cost per unit**, at least total cost. Costs on reverse residual edges are negative
(cancelling flow refunds its cost).

**Theorem 17.13 (optimality).** A flow of a given value has minimum cost if and only if its residual graph has no
negative-cost cycle.

*Proof sketch.* If there is a negative cycle, pushing flow round it keeps the value and lowers the cost. Conversely,
the difference between two flows of the same value decomposes into cycles in the residual graph of the first; if
the other flow were cheaper, one of those cycles would have negative cost. $\square$

The **successive shortest paths** algorithm keeps the residual graph free of negative cycles from the start (it
begins with the zero flow, and assumes the costs have no negative cycle) and repeatedly augments along a cheapest
path from $s$ to $t$. Each augmentation along a shortest path preserves the property, by an argument like Lemma
17.7. The program finds shortest paths with Bellman-Ford; production codes use Dijkstra with Johnson's potentials.
On its example (vertices 0 to 3, edges 0→1 capacity 4 cost 1, 0→2 2/2, 1→2 2/1, 1→3 2/3, 2→3 4/1, and 5 units
required), it sends

```
  send 2 along [0, 2, 3] at cost 3 each
  send 2 along [0, 1, 2, 3] at cost 3 each
  send 1 along [0, 1, 3] at cost 4 each
  total flow 5, total cost 16
```

and a brute-force search over all integer flows of value 5 confirms that 16 is the minimum. The number of
augmentations depends on the amount of flow, so this is pseudo-polynomial; polynomial algorithms exist (Orlin's 1993
strongly polynomial algorithm, and the 2022 almost-linear one).

### Stable matching: Gale and Shapley

The last problem has no costs, only **preferences**. There are $n$ proposers (say, applicants) and $n$ receivers
(say, programmes), each with a strict ranking of the other side. A perfect matching is **unstable** if some
proposer $p$ and receiver $r$ who are not matched to each other both prefer each other to their own partners: they
would both walk away, a **blocking pair**. A matching with no blocking pair is **stable**. Does one always exist?

David Gale and Lloyd Shapley answered yes in 1962, with an algorithm.

```text
GALE-SHAPLEY:
    everyone starts free
    while some proposer p is free and has not proposed to everyone:
        r = the highest receiver on p's list not yet proposed to
        if r is free:              r holds p
        elif r prefers p to its current partner p':
                                   r holds p and frees p'
        else:                      r rejects p
```

**Trace.** The program's preferences (best first):

| Proposer | Ranking | Receiver | Ranking |
|---|---|---|---|
| A | z y x w | w | D C A B |
| B | x w z y | x | A D C B |
| C | w x y z | y | B C A D |
| D | w y z x | z | C B A D |

| Step | Proposal | Result |
|---|---|---|
| 1 | A → z | z holds A |
| 2 | B → x | x holds B |
| 3 | C → w | w holds C |
| 4 | D → w | w prefers D: holds D, frees C |
| 5 | C → x | x prefers C to B: holds C, frees B |
| 6 | B → w | w prefers D: rejects B |
| 7 | B → z | z prefers B to A: holds B, frees A |
| 8 | A → y | y holds A |

The result is A–y, B–z, C–x, D–w, and the program checks every pair and finds no blocking pair.

**Theorem 17.14 (Gale and Shapley, 1962).** The algorithm ends after at most $n^2$ proposals with a perfect, stable
matching. Moreover, every proposer gets the best partner it has in *any* stable matching.

*Proof.* *Termination.* Each proposer proposes to each receiver at most once: at most $n^2$ proposals.

*Two monotone facts.* A receiver, once proposed to, always holds someone from then on, and only ever trades up. A
proposer's partners only get worse, since it proposes down its list.

*Perfect.* Suppose proposer $p$ is still free at the end. Then $p$ has proposed to all $n$ receivers, and each of
them now holds someone. That is $n$ receivers held by $n$ proposers other than $p$, but there are only $n - 1$ of
those. Contradiction.

*Stable.* Suppose $p$ and $r$ prefer each other to their partners $r'$ and $p'$. Since $p$ prefers $r$ to $r'$, $p$
proposed to $r$ before $r'$. At that moment, or later, $r$ rejected or dropped $p$ for someone it prefers, and $r$
only trades up, so it ends with $p'$ whom it likes better than $p$. That contradicts $r$ preferring $p$ to $p'$.

*Proposer-optimal.* Call $r$ a **valid** partner of $p$ if some stable matching pairs them. Suppose some proposer is
rejected by a valid partner, and look at the first time it happens in the run: $r$ rejects (or drops) $p$ for $p''$,
though some stable matching $M$ pairs $p$ with $r$. Then $r$ prefers $p''$ to $p$. In $M$, $p''$ is paired with
some $r''$. Up to this moment no proposer has been rejected by a valid partner, so $p''$ has not yet been rejected by
$r''$, which is valid for it; since $p''$ proposes in order of preference and has reached $r$, it prefers $r$ to
$r''$. So in $M$, $p''$ and $r$ prefer each other to their partners: $M$ is not stable. Contradiction. So no
proposer is ever rejected by a valid partner, and each ends with its best valid partner. $\square$

The flip side, by a similar argument, is that every receiver gets its *worst* valid partner. Whoever proposes has the
advantage. The program shows it: with the receivers proposing, the result is A–x, B–y, C–z, D–w, and a brute-force
search over all 24 matchings finds exactly three stable ones, with the proposer-proposing and receiver-proposing
results at the two extremes. With A–w, B–x, C–y, D–z there are five blocking pairs (exercise 10).

**In the world.** Since the 1950s the American medical residency match (the National Resident Matching Program) has
used algorithms of this kind; Alvin Roth showed that its original procedure was equivalent to Gale-Shapley, and in
1999 Roth and Elliott Peranson redesigned it, letting applicants propose and allowing for couples. School choice in
New York City and Boston was redesigned with stable-matching ideas in the 2000s. Roth and Shapley received the 2012
Nobel Memorial Prize in Economic Sciences for the theory of stable allocations and its practice (Gale had died in
2008).

## Check yourself

??? question "1. Is the minimum spanning tree of Figure 17.1 unique, even though several weights are tied?"

    Yes. A brute-force check over all $\binom{11}{6} = 462$ six-edge subsets finds exactly one spanning tree of
    weight 39. Reasoning: the tied pairs never compete for the same cut. Both 5s are taken (they are the two
    lightest edges and do not form a cycle). Of the 7s, A–B and B–E are both needed; they are taken before any 8 and
    do not form a cycle with the earlier edges. Of the 8s, B–C and E–F both close cycles of lighter edges, so both
    are rejected. Of the 9s, B–D closes a cycle and E–G is the only edge to G lighter than 11. Every decision was
    forced, so the tree is unique.

??? question "2. Prove that if all edge weights are different, the MST is unique."

    Suppose $T_1 \ne T_2$ are both MSTs. Let $e$ be the lightest edge in one but not the other, say $e \in T_1
    \setminus T_2$. Adding $e$ to $T_2$ makes a cycle, which must contain an edge $e' \notin T_1$ (otherwise $T_1$
    would contain the whole cycle). Since $e'$ is in $T_2$ but not $T_1$, and $e$ is the lightest edge in the
    difference, $w(e) < w(e')$ (weights are distinct). Then $T_2 + e - e'$ is a spanning tree lighter than $T_2$,
    contradicting minimality.

??? question "3. Show that an MST also minimises the heaviest edge: no spanning tree has a smaller maximum edge weight."

    Let $T$ be an MST with heaviest edge $e$ of weight $W$, and suppose some spanning tree $T'$ has every edge
    lighter than $W$. Remove $e$ from $T$: it splits into two pieces, a cut. $T'$ is connected, so it has an edge
    $e'$ crossing this cut, with $w(e') < W = w(e)$. Then $T - e + e'$ is a spanning tree lighter than $T$, a
    contradiction. So an MST is also a **minimum bottleneck spanning tree**. (The converse is false: a bottleneck
    tree need not be an MST.) This is why, to find the route between two places whose worst road is as good as
    possible, you can use the path in the MST.

??? question "4. Run Prim's algorithm on Figure 17.1 starting from G. In what order are the edges added?"

    From G the edges are E–G 9 and F–G 11; take G–E 9. Now the cheapest edge leaving {G, E} is E–C 5; then from
    {G, E, C}: B–E 7 (B–C 8, E–F 8, F–G 11, D–E 15 are heavier); then A–B 7; then A–D 5; then D–F 6. Order: G–E 9,
    E–C 5, E–B 7, B–A 7, A–D 5, D–F 6, total 39, the same tree. The program's `prim(V, E, "G", trace=True)` prints
    this order.

??? question "5. In Figure 17.2, raise the capacity of s → b from 8 to 10. What is the new maximum flow? Explain with a cut."

    Still 15. The program finds paths s, a, c, t carrying 5 and s, b, d, t carrying 10. The cut $S = \{s, a, b\}$
    has outgoing edges a→c (5) and b→d (10), capacity 15, so no flow can exceed 15. Raising an edge helps only if it
    lies in *every* minimum cut; s→b was in the cut $\{s, a\}$ but not in $\{s, a, b\}$, which has the same capacity
    15. After the change the old cut has capacity 17 and the new one is the unique minimum.

??? question "6. Why does Ford-Fulkerson need reverse residual edges? Give the smallest example you can where pushing only along real edges gets stuck."

    Edges s→a, s→b, a→b, a→t, b→t, all capacity 1. If the first path chosen is s, a, b, t, then s→a and b→t are full,
    and there is no path left that uses only edges with spare room: from s only s→b remains, and from b, b→t is full.
    The flow is stuck at 1 though the maximum is 2. With residual edges, the reverse edge b→a (capacity 1, the flow
    on a→b) gives the path s, b, a, t, which cancels the flow on a→b and reaches 2. Without cancellation, greedy path
    choice can be arbitrarily far from optimal on larger versions of this example.

??? question "7. Find a vertex cover of size 4 for Figure 17.3, and explain why it proves the matching of size 4 is maximum."

    {drill, map, Cai, Eli}. Check each person's edges: Ana (drill, map), Ben (drill) and Dev (drill, map) are covered
    by drill and map; all of Cai's and Eli's edges are covered by Cai and Eli. In any matching, each edge has an end
    in the cover and no two edges share a vertex, so a matching has at most as many edges as the cover has vertices:
    at most 4. Since a matching of size 4 exists, both are optimal, as König's theorem promises.

??? question "8. Write the simple augmenting-path algorithm for bipartite matching (often called Kuhn's algorithm) and run it on Figure 17.3."

    For each left vertex, try to find an augmenting path by DFS: a job that is free, or whose current holder can be
    moved to another job recursively.

    ```python
    def kuhn(left, adj):
        match_r = {}                          # job -> person

        def try_kuhn(u, seen):
            for v in adj[u]:
                if v in seen:
                    continue
                seen.add(v)
                if v not in match_r or try_kuhn(match_r[v], seen):
                    match_r[v] = u            # flip the path: u takes v
                    return True
            return False

        size = sum(try_kuhn(u, set()) for u in left)
        return size, {u: v for v, u in match_r.items()}
    ```

    It returns size 4 with Ana–map, Ben–drill, Cai–cook, Eli–fix. The run: Ana takes drill. Ben wants drill, held
    by Ana; Ana can move to map, which is free, so Ana–map and Ben–drill. Cai tries map: Ana holds it and cannot
    move (drill is held by Ben, who has no other job), so Cai takes cook, which is free. Dev tries drill and map;
    neither holder can move, so Dev stays unmatched. Eli takes fix. This is a different maximum matching from
    Hopcroft-Karp's, of the same size. Each of the $V$ searches costs $O(E)$, so the total is $O(VE)$.

??? question "9. Why does the Gale-Shapley algorithm make at most $n^2$ proposals, and why can't a receiver end up unmatched?"

    Each proposer goes down its own list and never proposes twice to the same receiver, so there are at most $n$
    proposals per proposer, $n^2$ in all. A receiver that has received one proposal holds someone from then on
    (it only trades up). If some receiver $r$ were unmatched at the end, nobody would ever have proposed to it;
    then some proposer is also unmatched (the numbers are equal), and that proposer would have proposed to every
    receiver, including $r$. Contradiction. (A sharper count shows at most $n^2 - n + 1$ proposals.)

??? question "10. With the preferences of 17.7, list the blocking pairs of the matching A–w, B–x, C–y, D–z."

    Check each proposer against every receiver it prefers to its own partner. A has w, its last choice, and prefers
    z, y, x: z ranks A above D (its partner), so (A, z) blocks; y ranks A below B, no; x ranks A first, above B, so
    (A, x) blocks. B has x, its first choice, so B is in no blocking pair. C has y and prefers w
    and x: w ranks C above A, blocks; x ranks C above B, blocks. D has z and prefers w and y: w ranks D first, blocks;
    y ranks D last, no. Blocking pairs: (A, z), (A, x), (C, w), (C, x), (D, w), five in all, which is what the
    program's `blocking_pairs` returns.

## What you learned

- An MST connects all vertices at least cost; the cut property (lightest crossing edge is safe) and the cycle
  property (heaviest cycle edge is never needed) are proved by swapping one edge.
- Kruskal sorts edges and uses union-find, Prim grows one tree with a heap, Borůvka merges all components in
  $O(\log V)$ rounds; each runs in $O(E \log V)$.
- A flow obeys capacities and conservation; the residual graph lets flow be cancelled, and Ford-Fulkerson augments
  until no residual path is left, with integer flows for integer capacities.
- Every cut bounds every flow, and the maximum flow equals the minimum cut; the vertices reachable in the final
  residual graph form a minimum cut, a checkable certificate.
- Choosing shortest augmenting paths (Edmonds-Karp, $O(VE^2)$) or blocking flows in level graphs (Dinic,
  $O(V^2E)$) makes the time independent of the capacities.
- Bipartite matching is unit-capacity flow; Hall's condition and König's vertex covers certify the answer, and
  Hopcroft-Karp finds it in $O(E\sqrt V)$.
- Potentials certify optimal assignments (Hungarian algorithm), min-cost flows are optimal when no residual cycle
  is negative, and Gale-Shapley always finds a stable matching that favours the proposing side.

**Next:** [Chapter 18](18-String-Algorithms.md), searching for patterns in text, from the naive method to KMP,
suffix arrays and the Burrows-Wheeler transform.

## Further reading

- T. H. Cormen, C. E. Leiserson, R. L. Rivest and C. Stein, *Introduction to Algorithms*, 4th ed., MIT Press, 2022,
  Chapters 21 (minimum spanning trees), 24 (maximum flow) and 25 (matchings in bipartite graphs).
- J. Kleinberg and É. Tardos, *Algorithm Design*, Addison-Wesley, 2005, Chapter 1 (stable matching), Section 4.5
  (MSTs) and Chapter 7 (network flow and its many applications).
- R. Sedgewick and K. Wayne, *Algorithms*, 4th ed., Addison-Wesley, 2011, Sections 4.3 and 6.4.
- R. K. Ahuja, T. L. Magnanti and J. B. Orlin, *Network Flows: Theory, Algorithms, and Applications*, Prentice Hall,
  1993.
- O. Borůvka, "O jistém problému minimálním" (On a certain minimal problem), *Práce Moravské přírodovědecké
  společnosti* 3, 1926; R. L. Graham and P. Hell, "On the history of the minimum spanning tree problem", *Annals of
  the History of Computing* 7(1), 1985.
- J. B. Kruskal, "On the shortest spanning subtree of a graph and the traveling salesman problem", *Proceedings of
  the AMS* 7(1), 1956; R. C. Prim, "Shortest connection networks and some generalizations", *Bell System Technical
  Journal* 36(6), 1957.
- L. R. Ford Jr. and D. R. Fulkerson, "Maximal flow through a network", *Canadian Journal of Mathematics* 8, 1956.
- J. Edmonds and R. M. Karp, "Theoretical improvements in algorithmic efficiency for network flow problems",
  *Journal of the ACM* 19(2), 1972; E. A. Dinic, "Algorithm for solution of a problem of maximum flow in a network
  with power estimation", *Soviet Mathematics Doklady* 11, 1970.
- J. E. Hopcroft and R. M. Karp, "An $n^{5/2}$ algorithm for maximum matchings in bipartite graphs", *SIAM Journal
  on Computing* 2(4), 1973.
- P. Hall, "On representatives of subsets", *Journal of the London Mathematical Society* 10, 1935.
- H. W. Kuhn, "The Hungarian method for the assignment problem", *Naval Research Logistics Quarterly* 2, 1955.
- D. Gale and L. S. Shapley, "College admissions and the stability of marriage", *American Mathematical Monthly*
  69(1), 1962.
- A. Schrijver, "On the history of the transportation and maximum flow problems", *Mathematical Programming* 91,
  2002.
- On this site: [Kruskal's algorithm](../../graphs/kruskal.md), [Prim's algorithm](../../graphs/prim.md),
  [Union-find](../../data-structures/union-find.md), [Binary heap](../../data-structures/binary-heap.md), and
  [Chapter 23](23-Approximation-and-Parameterized-Algorithms.md) for linear programming and duality.
