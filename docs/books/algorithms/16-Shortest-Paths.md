# 16. Shortest paths

*Breadth-first search finds the route with the fewest edges, but roads have lengths, flights have prices and links
have delays. This chapter finds routes that are shortest by total weight. You will meet the one operation every
shortest-path algorithm is built from, relaxation, and then four algorithms built on it: Dijkstra's, for
non-negative weights; Bellman-Ford, which also handles negative weights and detects negative cycles; a linear-time
method for DAGs; and Floyd-Warshall and Johnson's for all pairs at once. Then you will aim the search at a single
target with A*, and see the ideas (landmarks, shortcuts, two-ended search) behind route planners on real road
maps. Every algorithm is proved correct, and every one runs on this site's own map of Mars.*

!!! abstract "In this chapter"
    **You will learn:**

    - what a shortest path is, why its pieces are shortest paths too, and why negative cycles break the question
    - relaxation and the properties that make every algorithm in the chapter correct
    - Dijkstra's algorithm, its correctness proof, and its cost with an array, a binary heap and a Fibonacci heap
    - Bellman-Ford, its proof, and how it finds negative cycles; shortest paths in DAGs in linear time
    - all-pairs shortest paths by dynamic programming (Floyd-Warshall) and by reweighting (Johnson)
    - A* search with admissible and consistent heuristics, with a proof of optimality, and bidirectional search
    - how road-map routing goes further: landmarks (ALT), contraction hierarchies, and 0-1 BFS

    **You need:** [Chapter 15](15-Graphs-and-Graph-Search.md) (graphs, BFS, DFS, topological order), priority queues
    from [Chapter 9](09-Heaps-and-Priority-Queues.md), and the dynamic-programming recipe of
    [Chapter 13](13-Dynamic-Programming.md) for 16.5.

    **Levels:** 16.1 and 16.2 are beginner to intermediate; 16.3 to 16.6 are intermediate; 16.7 is advanced.

## 16.1 The problem, relaxation and negative cycles

A rover team on Mars wants the shortest drive between two sites, given a network of possible routes with their
lengths. A network engineer wants the path with the least total delay. A traveller wants the cheapest sequence of
flights. Each of these is the same problem on a **weighted directed graph**: every edge $u \to v$ has a **weight**
$w(u, v)$, a real number. (An undirected road is two directed edges, one each way, with the same weight.)

The **weight of a path** $p = v_0, v_1, \dots, v_k$ is the sum of its edge weights,

$$
w(p) = \sum_{i=1}^{k} w(v_{i-1}, v_i),
$$

and the **shortest-path distance** from $s$ to $v$ is the smallest weight of any path from $s$ to $v$:

$$
\delta(s, v) = \min\{\, w(p) : p \text{ is a path from } s \text{ to } v \,\},
$$

with $\delta(s, v) = \infty$ if there is no path. A **shortest path** is a path that achieves this minimum. When
every weight is 1, $\delta$ is the BFS distance of [Chapter 15](15-Graphs-and-Graph-Search.md).

There are a few versions of the problem:

- **single-pair**: from $s$ to one target $t$;
- **single-source**: from $s$ to every vertex (no known algorithm for single-pair is faster in the worst case, so
  most methods solve this);
- **all-pairs**: between every pair of vertices.

### Negative weights and negative cycles

Weights can be negative. A "weight" might be a cost that is sometimes a refund, an energy use where going downhill
recharges a battery, or a logarithm of an exchange rate (exercise 5). Negative edges by themselves are fine. But
if some cycle reachable from $s$ has negative total weight, a **negative cycle**, then walking round it again and
again makes a path as light as you like, and $\delta(s, v) = -\infty$ for every $v$ reachable from that cycle.
There is then no shortest path; the honest answer is to report the cycle. If there is no negative cycle, we can
always take shortest paths to be **simple** (no repeated vertex): a repeated vertex means the path contains a cycle
of weight $\ge 0$, and cutting it out does not make the path heavier. A simple path has at most $V - 1$ edges.
This bound is the heart of Bellman-Ford.

### Optimal substructure

**Lemma 16.1 (pieces of shortest paths are shortest).** If $p = v_0, v_1, \dots, v_k$ is a shortest path from
$v_0$ to $v_k$, then for any $0 \le i \le j \le k$ the piece $v_i, \dots, v_j$ is a shortest path from $v_i$ to
$v_j$.

*Proof.* Split $p$ into three pieces: $v_0 \leadsto v_i$, then $v_i \leadsto v_j$, then $v_j \leadsto v_k$. If
there were a lighter path from $v_i$ to $v_j$, put it in place of the middle piece: the result is a walk from $v_0$
to $v_k$ lighter than $p$, contradicting that $p$ is shortest. $\square$

This is the dynamic-programming property of [Chapter 13](13-Dynamic-Programming.md): an optimal solution is built
from optimal solutions to subproblems. It also means that the shortest paths from $s$ to all vertices can be
stored compactly, as a **shortest-path tree**: each vertex keeps only a **parent** pointer, its predecessor on a
shortest path, exactly as in BFS.

A second basic fact follows directly from the definition.

**Lemma 16.2 (triangle inequality).** For every edge $u \to v$, $\delta(s, v) \le \delta(s, u) + w(u, v)$.

*Proof.* A shortest path to $u$ followed by the edge $u \to v$ is one path to $v$, and $\delta(s, v)$ is at most
the weight of any path. $\square$

### Relaxation

Every algorithm in this chapter keeps an estimate $d[v]$ for each vertex, an upper bound on $\delta(s, v)$. It
starts with $d[s] = 0$ and $d[v] = \infty$ for the rest, and improves the estimates by one operation, **relaxing**
an edge:

```text
RELAX(u, v):
    if d[u] + w(u, v) < d[v]:
        d[v] = d[u] + w(u, v)
        parent[v] = u
```

In words: "is going to $v$ through $u$ better than the best way to $v$ found so far?" The word comes from the image
of the estimate $d[v]$ as a stretched spring that relaxes to a shorter length. The algorithms differ only in **which
edges they relax and in what order**. Four properties of relaxation do all the work in the proofs.

**Lemma 16.3 (properties of relaxation).** Start with $d[s] = 0$, all other $d[v] = \infty$, and apply any
sequence of relaxations.

1. **Upper bound.** Always $d[v] \ge \delta(s, v)$; and once $d[v] = \delta(s, v)$, it never changes again.
2. **No path.** If there is no path from $s$ to $v$, then $d[v] = \infty$ forever.
3. **Convergence.** If $s \leadsto u \to v$ is a shortest path and $d[u] = \delta(s, u)$ at some moment before the
   edge $u \to v$ is relaxed, then $d[v] = \delta(s, v)$ from then on.
4. **Path relaxation.** If $p = v_0, v_1, \dots, v_k$ with $v_0 = s$ is a shortest path, and the edges
   $(v_0, v_1), (v_1, v_2), \dots, (v_{k-1}, v_k)$ are relaxed in that order (any other relaxations may be mixed in
   between), then afterwards $d[v_k] = \delta(s, v_k)$.

*Proof.* (1) By induction on the number of relaxations. At the start the bound holds ($d[s] = 0 = \delta(s,s)$
when there is no negative cycle through $s$, and $\infty$ is above everything). A relaxation that changes $d[v]$
sets it to $d[u] + w(u,v) \ge \delta(s,u) + w(u,v) \ge \delta(s,v)$, by induction and the triangle inequality.
Since $d[v]$ only decreases and can never go below $\delta(s,v)$, once equal it stays equal. (2) follows from (1):
$d[v] \ge \delta(s,v) = \infty$. (3) After relaxing $u \to v$, $d[v] \le d[u] + w(u,v) = \delta(s,u) + w(u,v) =
\delta(s,v)$, the last step because $s \leadsto u \to v$ is shortest. With (1), $d[v] = \delta(s,v)$. (4) By
induction on $i$: $d[v_0] = 0 = \delta(s, v_0)$ from the start; if $d[v_{i-1}]$ is correct before $(v_{i-1}, v_i)$
is relaxed, then by Lemma 16.1 the path to $v_i$ is shortest, and (3) makes $d[v_i]$ correct. $\square$

The path-relaxation property is the whole game: an algorithm is correct as soon as, for every vertex, the edges of
some shortest path to it get relaxed in order. Dijkstra arranges that by settling vertices in order of distance;
Bellman-Ford by relaxing every edge $V - 1$ times; the DAG method by relaxing in topological order.

## 16.2 Dijkstra's algorithm

When no edge weight is negative, there is a beautiful greedy method. Think of BFS's rings again, but now the rings
are by distance instead of by number of edges: imagine water poured at $s$ flowing along every road at the same
speed. It reaches places in the order of their true distance. **Dijkstra's algorithm** simulates the water.

It keeps a set $S$ of **settled** vertices, whose distances are final. Each round it settles the unsettled vertex
with the smallest estimate $d$, and relaxes the edges leaving it.

```text
DIJKSTRA(G, s):          # all weights >= 0
    d[v] = infinity for all v;  d[s] = 0
    S = empty set
    while some vertex outside S has finite d:
        u = the vertex outside S with the smallest d[u]
        add u to S                       # settle u: d[u] is final
        for each edge u -> v:
            RELAX(u, v)
```

### A trace by hand

Take the graph in Figure 16.1, with source $s$.

<figure class="mars-fig" markdown="0">
<svg viewBox="0 0 600 260" role="img" aria-label="A directed weighted graph on s, a, b, c, d, e with Dijkstra's shortest-path tree from s highlighted and final distances 0, 3, 1, 4, 7, 8">
<line x1="64.1" y1="122.5" x2="178.8" y2="61.3" stroke="currentColor" stroke-width="1.3"/>
<polygon points="185.9,57.5 180.1,65.7 175.8,57.8" fill="currentColor"/>
<text x="130.6" y="105.1" font-size="13" text-anchor="middle" fill="currentColor">4</text>
<line x1="64.1" y1="137.5" x2="178.8" y2="198.7" stroke="#eea66f" stroke-width="3"/>
<polygon points="185.9,202.5 175.8,202.2 180.1,194.3" fill="#eea66f"/>
<text x="130.6" y="164.0" font-size="13" text-anchor="middle" fill="currentColor">1</text>
<line x1="214.1" y1="57.5" x2="328.8" y2="118.7" stroke="#eea66f" stroke-width="3"/>
<polygon points="335.9,122.5 325.8,122.2 330.1,114.3" fill="#eea66f"/>
<text x="269.4" y="105.1" font-size="13" text-anchor="middle" fill="currentColor">1</text>
<line x1="200.0" y1="194.0" x2="200.0" y2="74.0" stroke="#eea66f" stroke-width="3"/>
<polygon points="200.0,66.0 204.5,75.0 195.5,75.0" fill="#eea66f"/>
<text x="188.0" y="134.6" font-size="13" text-anchor="middle" fill="currentColor">2</text>
<line x1="214.1" y1="202.5" x2="328.8" y2="141.3" stroke="currentColor" stroke-width="1.3"/>
<polygon points="335.9,137.5 330.1,145.7 325.8,137.8" fill="currentColor"/>
<text x="280.6" y="185.1" font-size="13" text-anchor="middle" fill="currentColor">5</text>
<line x1="216.0" y1="210.0" x2="446.0" y2="210.0" stroke="currentColor" stroke-width="1.3"/>
<polygon points="454.0,210.0 445.0,214.5 445.0,205.5" fill="currentColor"/>
<text x="335.0" y="202.6" font-size="13" text-anchor="middle" fill="currentColor">8</text>
<line x1="363.3" y1="138.9" x2="450.0" y2="196.7" stroke="#eea66f" stroke-width="3"/>
<polygon points="456.7,201.1 446.7,199.9 451.7,192.4" fill="#eea66f"/>
<text x="403.3" y="184.5" font-size="13" text-anchor="middle" fill="currentColor">3</text>
<line x1="365.7" y1="127.0" x2="536.4" y2="94.5" stroke="currentColor" stroke-width="1.3"/>
<polygon points="544.3,93.0 536.3,99.1 534.6,90.3" fill="currentColor"/>
<text x="457.2" y="126.3" font-size="13" text-anchor="middle" fill="currentColor">6</text>
<line x1="479.6" y1="197.2" x2="545.6" y2="109.2" stroke="#eea66f" stroke-width="3"/>
<polygon points="550.4,102.8 548.6,112.7 541.4,107.3" fill="#eea66f"/>
<text x="505.4" y="147.4" font-size="13" text-anchor="middle" fill="currentColor">1</text>
<text x="50" y="106" font-size="12" text-anchor="middle" fill="currentColor" font-family="monospace">d = 0</text>
<text x="200" y="26" font-size="12" text-anchor="middle" fill="currentColor" font-family="monospace">d = 3</text>
<text x="200" y="244" font-size="12" text-anchor="middle" fill="currentColor" font-family="monospace">d = 1</text>
<text x="350" y="106" font-size="12" text-anchor="middle" fill="currentColor" font-family="monospace">d = 4</text>
<text x="470" y="244" font-size="12" text-anchor="middle" fill="currentColor" font-family="monospace">d = 7</text>
<text x="560" y="66" font-size="12" text-anchor="middle" fill="currentColor" font-family="monospace">d = 8</text>
<circle cx="50" cy="130" r="16" fill="#eea66f" fill-opacity="0.55" stroke="currentColor" stroke-width="1.5"/>
<text x="50" y="134.9" font-size="14" text-anchor="middle" fill="currentColor">s</text>
<circle cx="200" cy="50" r="16" fill="#9cc9ea" fill-opacity="0.55" stroke="currentColor" stroke-width="1.5"/>
<text x="200" y="54.9" font-size="14" text-anchor="middle" fill="currentColor">a</text>
<circle cx="200" cy="210" r="16" fill="#9cc9ea" fill-opacity="0.55" stroke="currentColor" stroke-width="1.5"/>
<text x="200" y="214.9" font-size="14" text-anchor="middle" fill="currentColor">b</text>
<circle cx="350" cy="130" r="16" fill="#9cc9ea" fill-opacity="0.55" stroke="currentColor" stroke-width="1.5"/>
<text x="350" y="134.9" font-size="14" text-anchor="middle" fill="currentColor">c</text>
<circle cx="470" cy="210" r="16" fill="#9cc9ea" fill-opacity="0.55" stroke="currentColor" stroke-width="1.5"/>
<text x="470" y="214.9" font-size="14" text-anchor="middle" fill="currentColor">d</text>
<circle cx="560" cy="90" r="16" fill="#9cc9ea" fill-opacity="0.55" stroke="currentColor" stroke-width="1.5"/>
<text x="560" y="94.9" font-size="14" text-anchor="middle" fill="currentColor">e</text>
</svg>
<figcaption>Figure 16.1. The graph used for the Dijkstra trace. Edge numbers are lengths; the thick edges are the parent pointers at the end, the shortest-path tree from s, and the labels are the final distances. The direct edge s→a of length 4 loses to s→b→a of length 3.</figcaption>
</figure>

Each row settles one vertex, then shows all estimates after relaxing its out-edges. Bold marks an improvement.

| Settle | $d[s]$ | $d[a]$ | $d[b]$ | $d[c]$ | $d[d]$ | $d[e]$ |
|---|---|---|---|---|---|---|
| start | 0 | ∞ | ∞ | ∞ | ∞ | ∞ |
| s (0) | 0 | **4** | **1** | ∞ | ∞ | ∞ |
| b (1) | 0 | **3** | 1 | **6** | **9** | ∞ |
| a (3) | 0 | 3 | 1 | **4** | 9 | ∞ |
| c (4) | 0 | 3 | 1 | 4 | **7** | **10** |
| d (7) | 0 | 3 | 1 | 4 | 7 | **8** |
| e (8) | 0 | 3 | 1 | 4 | 7 | 8 |

Notice how $d[a]$ starts at 4 from the direct edge and improves to 3 when $b$ is settled, and $d[c]$ goes 6, then 4.
Following parents back from $e$: e ← d ← c ← a ← b ← s. The shortest path is s, b, a, c, d, e with weight $1 + 2 +
1 + 3 + 1 = 8$. The program prints exactly this trace.

### Why it works

**Theorem 16.4 (Dijkstra is correct).** If all edge weights are non-negative, then when Dijkstra's algorithm settles
a vertex $u$, $d[u] = \delta(s, u)$.

*Proof.* Suppose not, and let $u$ be the first vertex settled with $d[u] \ne \delta(s, u)$; by Lemma 16.3, $d[u] >
\delta(s, u)$. Then $u \ne s$ (s is settled first with $d[s] = 0$), and $u$ is reachable (else $d[u] = \infty =
\delta$; we never settle a vertex with infinite $d$). Take a shortest path $p$ from $s$ to $u$. At the moment just
before $u$ is settled, $p$ starts inside $S$ (at $s$) and ends outside it (at $u$), so it has a first vertex $y$
outside $S$; let $x$ be the vertex before $y$ on $p$, which is in $S$.

- $x$ was settled correctly ($u$ is the first mistake), so $d[x] = \delta(s,x)$, and when $x$ was settled the edge
  $x \to y$ was relaxed. By the convergence property, $d[y] = \delta(s, y)$ now.
- $y$ comes before $u$ on a shortest path, and the rest of the path from $y$ to $u$ has non-negative weight, so
  $\delta(s, y) \le \delta(s, u)$.
- The algorithm chose $u$, not $y$, so $d[u] \le d[y]$.

Putting these together: $d[u] \le d[y] = \delta(s, y) \le \delta(s, u) < d[u]$, a contradiction. $\square$

The proof uses the non-negative weights at one place only: $\delta(s,y) \le \delta(s,u)$. With a negative edge
that step fails, and so does the algorithm. The program's example has edges s→a 2, s→b 3, b→a −2, a→c 1. Dijkstra
settles $a$ at 2 and relaxes a→c, giving $c$ the value 3. Next it settles $b$ (at 3) and discovers that $a$ can be
reached for $3 - 2 = 1$, but $a$ is already settled, so its edge a→c is never relaxed again. Then $c$ is settled at
3, though the true distance is $1 + 1 = 2$. The program
prints `Dijkstra says c = 3`. For negative weights, use Bellman-Ford (16.3) or Johnson's reweighting (16.5).

### Choosing the priority queue

The only data-structure question is how to find "the unsettled vertex with the smallest $d$" quickly. Count the
operations: $V$ times **extract-min**, and up to $E$ times **decrease-key** (a relaxation that lowers some $d[v]$).

| Priority queue | extract-min | decrease-key | Dijkstra total |
|---|---|---|---|
| unsorted array (scan for the minimum) | $O(V)$ | $O(1)$ | $O(V^2 + E) = O(V^2)$ |
| binary heap with decrease-key | $O(\log V)$ | $O(\log V)$ | $O((V + E) \log V)$ |
| binary heap, lazy (push duplicates, skip stale) | $O(\log E)$ | push, $O(\log E)$ | $O((V + E) \log V)$ |
| Fibonacci heap (amortized) | $O(\log V)$ | $O(1)$ | $O(E + V \log V)$ |

A few remarks on this table, each of which matters in practice.

- The plain **array** version is the one Dijkstra published. For a dense graph, where $E$ is close to $V^2$, its
  $O(V^2)$ is optimal (you must read every edge), and it beats a heap.
- A **binary heap** ([Chapter 9](09-Heaps-and-Priority-Queues.md)) is the usual choice for sparse graphs. Python's
  `heapq` has no decrease-key, so the program uses the **lazy** version: every improvement pushes a new pair
  $(d[v], v)$, and when a pair comes out for a vertex that is already settled, it is skipped as stale. The heap holds
  at most $E + 1$ entries, and $\log E \le \log V^2 = 2 \log V$, so the bound is the same. In the trace above the
  program pushes 10 pairs and skips 4 stale ones (exercise 3).
- A **Fibonacci heap** (Fredman and Tarjan, 1984) makes decrease-key $O(1)$ amortized and gives the best bound known
  for general comparison-based heaps, $O(E + V \log V)$. Its constant factors are large, and in practice binary
  heaps, 4-ary heaps or pairing heaps are usually faster; [Chapter 9](09-Heaps-and-Priority-Queues.md) explains
  why.

**Why $V \log V$ seemed to be a barrier.** Dijkstra's algorithm settles vertices in sorted order of distance, so on a
suitable graph it can be used to sort numbers; any comparison-based method that outputs vertices in that order
needs $\Omega(V \log V)$ comparisons ([Chapter 5](05-Sorting-by-Comparison.md)). That lower bound does not apply
to algorithms that find the distances without producing them in order. Thorup (1999) gave a linear-time algorithm
for undirected graphs with integer weights, and in 2025 Duan, Mao, Mao, Shu and Yin gave a deterministic
$O(E \log^{2/3} V)$ algorithm for directed graphs with real non-negative weights, the first to beat Dijkstra with
Fibonacci heaps on sparse graphs in the comparison-addition model. In the other direction, Haeupler, Hladík,
Rozhoň, Tarjan and Tětek (2024) proved that Dijkstra's algorithm with a suitable heap is *universally optimal* for
the task of ordering vertices by distance: on every graph, it is as fast as any algorithm can be on that graph's
worst weights, up to a constant factor.

The reference page [Dijkstra's algorithm](../../graphs/dijkstra.md) has the algorithm in Java and C++ and an
animation on the same Mars map as below.

### The Mars route on this site's banner

The banner on this site's home page is a correct answer, not a drawing of one. It shows nine real places on Mars,
placed by their latitude and longitude from the USGS Gazetteer of Planetary Nomenclature, and twelve roads, each as
long as the **great-circle distance** between its ends: the length of the shortest arc on the surface of a sphere of
Mars's mean radius, 3389.5 km. For two points at latitudes $\varphi_1, \varphi_2$ and longitude difference
$\Delta\lambda$, the central angle $\theta$ between them satisfies

$$
\cos\theta = \sin\varphi_1 \sin\varphi_2 + \cos\varphi_1 \cos\varphi_2 \cos\Delta\lambda,
$$

and the distance is $R\theta$ with $R = 3389.5$ km. The program computes all twelve lengths this way, builds the
graph, and runs the same Dijkstra function from Erebus Montes.

<figure class="mars-fig" markdown="0">
<svg viewBox="0 0 640 330" role="img" aria-label="Nine places on Mars joined by twelve roads with great-circle lengths in kilometres; the shortest route from Erebus Montes to Gale crater, through Elysium Mons, 3895 km, is highlighted">
<line x1="321.7" y1="85.9" x2="375.8" y2="120.7" stroke="currentColor" stroke-width="1.2"/>
<text x="342.3" y="117.3" font-size="11" text-anchor="middle" fill="currentColor">2,369</text>
<line x1="307.7" y1="84.8" x2="260.3" y2="105.6" stroke="#eea66f" stroke-width="3.5"/>
<text x="288.0" y="108.2" font-size="11" text-anchor="middle" fill="currentColor">2,016</text>
<line x1="307.5" y1="78.8" x2="239.3" y2="53.1" stroke="currentColor" stroke-width="1.2"/>
<text x="269.2" y="81.0" font-size="11" text-anchor="middle" fill="currentColor">2,305</text>
<line x1="390.1" y1="127.7" x2="423.8" y2="139.6" stroke="currentColor" stroke-width="1.2"/>
<text x="403.0" y="148.8" font-size="11" text-anchor="middle" fill="currentColor">1,740</text>
<line x1="437.3" y1="147.6" x2="499.0" y2="202.8" stroke="currentColor" stroke-width="1.2"/>
<text x="476.1" y="170.1" font-size="11" text-anchor="middle" fill="currentColor">3,043</text>
<line x1="251.5" y1="116.7" x2="239.2" y2="178.6" stroke="#eea66f" stroke-width="3.5"/>
<text x="233.5" y="149.1" font-size="11" text-anchor="middle" fill="currentColor">1,879</text>
<line x1="234.5" y1="57.8" x2="250.3" y2="101.3" stroke="currentColor" stroke-width="1.2"/>
<text x="231.1" y="87.5" font-size="11" text-anchor="middle" fill="currentColor">1,486</text>
<line x1="225.6" y1="55.3" x2="145.0" y2="120.7" stroke="currentColor" stroke-width="1.2"/>
<text x="192.9" y="101.2" font-size="11" text-anchor="middle" fill="currentColor">3,214</text>
<line x1="145.6" y1="130.0" x2="230.8" y2="182.2" stroke="currentColor" stroke-width="1.2"/>
<text x="181.9" y="170.2" font-size="11" text-anchor="middle" fill="currentColor">3,782</text>
<line x1="138.2" y1="133.7" x2="127.8" y2="272.8" stroke="currentColor" stroke-width="1.2"/>
<text x="121.1" y="206.2" font-size="11" text-anchor="middle" fill="currentColor">3,616</text>
<line x1="231.5" y1="191.6" x2="133.3" y2="275.6" stroke="currentColor" stroke-width="1.2"/>
<text x="190.2" y="246.6" font-size="11" text-anchor="middle" fill="currentColor">4,122</text>
<line x1="375.2" y1="128.2" x2="245.0" y2="183.3" stroke="currentColor" stroke-width="1.2"/>
<text x="314.0" y="168.8" font-size="11" text-anchor="middle" fill="currentColor">5,337</text>
<text x="327" y="72" font-size="12" text-anchor="start" fill="currentColor" font-weight="bold">Erebus Montes</text>
<text x="391" y="115" font-size="12" text-anchor="start" fill="currentColor" font-weight="bold">Olympus Mons</text>
<text x="443" y="146" font-size="12" text-anchor="start" fill="currentColor" font-weight="bold">Ascraeus Mons</text>
<text x="493" y="212" font-size="12" text-anchor="end" fill="currentColor" font-weight="bold">Valles Marineris</text>
<text x="247" y="131" font-size="12" text-anchor="end" fill="currentColor" font-weight="bold">Elysium Mons</text>
<text x="232" y="36" font-size="12" text-anchor="middle" fill="currentColor" font-weight="bold">Utopia Planitia</text>
<text x="248" y="204" font-size="12" text-anchor="start" fill="currentColor" font-weight="bold">Gale crater</text>
<text x="127" y="130" font-size="12" text-anchor="end" fill="currentColor" font-weight="bold">Jezero crater</text>
<text x="139" y="285" font-size="12" text-anchor="start" fill="currentColor" font-weight="bold">Hellas Planitia</text>
<text x="320" y="320" font-size="13" text-anchor="middle" fill="currentColor">shortest route Erebus Montes → Elysium Mons → Gale crater: 3,895 km</text>
<circle cx="315" cy="81.5816" r="8" fill="#eea66f" fill-opacity="0.55" stroke="currentColor" stroke-width="1.5"/>
<text x="315" y="86.5" font-size="14" text-anchor="middle" fill="currentColor"></text>
<circle cx="382.568" cy="125.077" r="8" fill="#9cc9ea" fill-opacity="0.55" stroke="currentColor" stroke-width="1.5"/>
<text x="382.568" y="130.0" font-size="14" text-anchor="middle" fill="currentColor"></text>
<circle cx="431.309" cy="142.245" r="8" fill="#9cc9ea" fill-opacity="0.55" stroke="currentColor" stroke-width="1.5"/>
<text x="431.309" y="147.1" font-size="14" text-anchor="middle" fill="currentColor"></text>
<circle cx="504.912" cy="208.112" r="8" fill="#9cc9ea" fill-opacity="0.55" stroke="currentColor" stroke-width="1.5"/>
<text x="504.912" y="213.0" font-size="14" text-anchor="middle" fill="currentColor"></text>
<circle cx="253.024" cy="108.827" r="8" fill="#eea66f" fill-opacity="0.55" stroke="currentColor" stroke-width="1.5"/>
<text x="253.024" y="113.7" font-size="14" text-anchor="middle" fill="currentColor"></text>
<circle cx="231.786" cy="50.2806" r="8" fill="#9cc9ea" fill-opacity="0.55" stroke="currentColor" stroke-width="1.5"/>
<text x="231.786" y="55.2" font-size="14" text-anchor="middle" fill="currentColor"></text>
<circle cx="237.592" cy="186.429" r="8" fill="#eea66f" fill-opacity="0.55" stroke="currentColor" stroke-width="1.5"/>
<text x="237.592" y="191.3" font-size="14" text-anchor="middle" fill="currentColor"></text>
<circle cx="138.831" cy="125.765" r="8" fill="#9cc9ea" fill-opacity="0.55" stroke="currentColor" stroke-width="1.5"/>
<text x="138.831" y="130.7" font-size="14" text-anchor="middle" fill="currentColor"></text>
<circle cx="127.22" cy="280.816" r="8" fill="#9cc9ea" fill-opacity="0.55" stroke="currentColor" stroke-width="1.5"/>
<text x="127.22" y="285.7" font-size="14" text-anchor="middle" fill="currentColor"></text>
</svg>
<figcaption>Figure 16.2. The network on this site's home-page banner, redrawn: real places on Mars (USGS coordinates, longitude 60° to 310° east from left to right) and roads as long as the great-circle distance on a sphere of radius 3389.5 km. Dijkstra's algorithm from Erebus Montes picks the orange route to Gale crater.</figcaption>
</figure>

The output lists every place with its distance and route; the line that the banner draws is

```
  Gale crater         3895 km  via Erebus Montes > Elysium Mons > Gale crater
```

Notice two things the algorithm teaches. First, the direct road from Olympus Mons to Gale crater is long (5337 km),
so even though Olympus Mons is close to Erebus Montes, the route through it costs $2369 + 5337 = 7706$ km. Second,
Elysium Mons is reached directly in 2016 km, and the road onward to Gale is only 1879 km: the greedy "closest
unsettled first" rule settles Elysium Mons (2016) before Utopia Planitia (2305) and Olympus Mons (2369), and Gale
crater is then settled at $2016 + 1879 = 3895$ km before any longer route could matter.

### A short history

Edsger Dijkstra later recalled designing the algorithm in 1956 at the Mathematical Centre in Amsterdam, in about
twenty minutes and without pencil and paper, as a demonstration for the new ARMAC computer, on a simplified road
map of the Netherlands. He published it in 1959 in a three-page paper, "A note on two problems in connexion with
graphs", whose other problem was the minimum spanning tree ([Chapter 17](17-Spanning-Trees-Flows-and-Matching.md)).
Similar methods were found independently around the same time by others, including Leyzorek and co-authors (1957)
and Dantzig. Dijkstra received the Turing Award in 1972, chiefly for his work on programming languages and
structured programming.

## 16.3 Bellman-Ford

Dijkstra's proof needed non-negative weights. What if some are negative? We can no longer settle a vertex for
good, because a negative edge found later might improve it. A blunter method works instead: **relax every edge, $V
- 1$ times over.**

```text
BELLMAN-FORD(G, s):
    d[v] = infinity for all v;  d[s] = 0
    repeat V - 1 times:
        for each edge (u, v):  RELAX(u, v)
    for each edge (u, v):
        if d[u] + w(u, v) < d[v]:  report "negative cycle reachable from s"
```

**Theorem 16.5.** If no negative cycle is reachable from $s$, then after the $V - 1$ rounds $d[v] = \delta(s, v)$
for every $v$, and the final check reports nothing. If a negative cycle is reachable from $s$, the final check
reports it. The running time is $O(VE)$.

*Proof.* *No negative cycle.* Every reachable $v$ has a simple shortest path $s = v_0, v_1, \dots, v_k = v$ with $k
\le V - 1$ edges. Round 1 relaxes every edge, in particular $(v_0, v_1)$; round 2 relaxes $(v_1, v_2)$; ...; round
$k$ relaxes $(v_{k-1}, v_k)$. So these edges are relaxed in path order (with others in between), and by the
path-relaxation property $d[v] = \delta(s, v)$ after round $k \le V - 1$. Unreachable vertices keep $\infty$. Then
every edge satisfies $d[v] = \delta(s,v) \le \delta(s,u) + w(u,v) = d[u] + w(u,v)$ by the triangle inequality, so the
check passes.

*A negative cycle.* Let $c = v_0, v_1, \dots, v_k = v_0$ be a reachable cycle with $\sum_{i=1}^k w(v_{i-1}, v_i) <
0$. After the rounds all $d[v_i]$ are finite (they are reachable, and each round extends known paths by one edge).
Suppose the check passed on every edge of $c$: $d[v_i] \le d[v_{i-1}] + w(v_{i-1}, v_i)$ for each $i$. Summing over
the cycle, each $d[v_i]$ appears once on each side, and they cancel:

$$
\sum_{i=1}^{k} d[v_i] \le \sum_{i=1}^{k} d[v_{i-1}] + \sum_{i=1}^{k} w(v_{i-1}, v_i)
\quad\Longrightarrow\quad 0 \le \sum_{i=1}^{k} w(v_{i-1}, v_i),
$$

contradicting the negative cycle. So some edge on $c$ fails the check.

*Time.* $V - 1$ rounds of $E$ relaxations plus one more pass: $O(VE)$. $\square$

### A trace

Figure 16.3 shows a graph with two negative edges. The program relaxes the edges in the fixed order c→d, b→c, a→b,
s→a, s→b, a→c, b→d, c→a: a deliberately unhelpful order, so that you can see several rounds do the work.

<figure class="mars-fig" markdown="0">
<svg viewBox="0 0 560 260" role="img" aria-label="A directed graph on s, a, b, c, d with negative edges b to c of minus 2 and c to a of minus 1; the cycle a, b, c has total weight zero">
<line x1="403.3" y1="138.9" x2="490.0" y2="196.7" stroke="currentColor" stroke-width="1.3"/>
<polygon points="496.7,201.1 486.7,199.9 491.7,192.4" fill="currentColor"/>
<text x="456.7" y="164.6" font-size="13" text-anchor="middle" fill="currentColor">2</text>
<line x1="234.5" y1="203.2" x2="368.3" y2="140.2" stroke="#7ccf9a" stroke-width="2.5"/>
<polygon points="375.5,136.8 369.3,144.7 365.5,136.6" fill="#7ccf9a"/>
<text x="310.1" y="185.4" font-size="13" text-anchor="middle" fill="#7ccf9a">-2</text>
<line x1="220.0" y1="66.0" x2="220.0" y2="186.0" stroke="currentColor" stroke-width="1.3"/>
<polygon points="220.0,194.0 215.5,185.0 224.5,185.0" fill="currentColor"/>
<text x="208.0" y="134.6" font-size="13" text-anchor="middle" fill="currentColor">3</text>
<line x1="74.3" y1="122.8" x2="198.5" y2="60.7" stroke="currentColor" stroke-width="1.3"/>
<polygon points="205.7,57.2 199.7,65.2 195.6,57.2" fill="currentColor"/>
<text x="145.4" y="105.3" font-size="13" text-anchor="middle" fill="currentColor">6</text>
<line x1="74.3" y1="137.2" x2="198.5" y2="199.3" stroke="currentColor" stroke-width="1.3"/>
<polygon points="205.7,202.8 195.6,202.8 199.7,194.8" fill="currentColor"/>
<text x="145.4" y="163.8" font-size="13" text-anchor="middle" fill="currentColor">7</text>
<path d="M 232.7 59.7 Q 296.5 108.1 366.6 124.5" fill="none" stroke="currentColor" stroke-width="1.3"/>
<polygon points="374.4,126.4 364.6,128.7 366.7,119.9" fill="currentColor"/>
<text x="295.6" y="114.5" font-size="13" text-anchor="middle" fill="currentColor">5</text>
<line x1="236.0" y1="210.0" x2="486.0" y2="210.0" stroke="currentColor" stroke-width="1.3"/>
<polygon points="494.0,210.0 485.0,214.5 485.0,205.5" fill="currentColor"/>
<text x="365.0" y="202.6" font-size="13" text-anchor="middle" fill="currentColor">4</text>
<path d="M 377.3 120.3 Q 313.5 71.9 243.4 55.5" fill="none" stroke="#7ccf9a" stroke-width="2.5"/>
<polygon points="235.6,53.6 245.4,51.3 243.3,60.1" fill="#7ccf9a"/>
<text x="314.4" y="74.6" font-size="13" text-anchor="middle" fill="#7ccf9a">-1</text>
<circle cx="60" cy="130" r="16" fill="#eea66f" fill-opacity="0.55" stroke="currentColor" stroke-width="1.5"/>
<text x="60" y="134.9" font-size="14" text-anchor="middle" fill="currentColor">s</text>
<circle cx="220" cy="50" r="16" fill="#9cc9ea" fill-opacity="0.55" stroke="currentColor" stroke-width="1.5"/>
<text x="220" y="54.9" font-size="14" text-anchor="middle" fill="currentColor">a</text>
<circle cx="220" cy="210" r="16" fill="#9cc9ea" fill-opacity="0.55" stroke="currentColor" stroke-width="1.5"/>
<text x="220" y="214.9" font-size="14" text-anchor="middle" fill="currentColor">b</text>
<circle cx="390" cy="130" r="16" fill="#9cc9ea" fill-opacity="0.55" stroke="currentColor" stroke-width="1.5"/>
<text x="390" y="134.9" font-size="14" text-anchor="middle" fill="currentColor">c</text>
<circle cx="510" cy="210" r="16" fill="#9cc9ea" fill-opacity="0.55" stroke="currentColor" stroke-width="1.5"/>
<text x="510" y="214.9" font-size="14" text-anchor="middle" fill="currentColor">d</text>
</svg>
<figcaption>Figure 16.3. The Bellman-Ford example. The green edges are negative. The cycle a → b → c → a weighs 3 − 2 − 1 = 0, so shortest paths still exist; change c → a to −2 and the cycle weighs −1, and no shortest path to a, b, c or d exists any more.</figcaption>
</figure>

| After round | $d[s]$ | $d[a]$ | $d[b]$ | $d[c]$ | $d[d]$ |
|---|---|---|---|---|---|
| 0 | 0 | ∞ | ∞ | ∞ | ∞ |
| 1 | 0 | 6 | 7 | 11 | 11 |
| 2 | 0 | 4 | 7 | 5 | 11 |
| 3 | 0 | 4 | 7 | 5 | 7 |
| 4 | 0 | 4 | 7 | 5 | 7 |

In round 1, c→d and b→c come before anything reaches b or c, so they do nothing; s→a sets $a = 6$, s→b sets $b =
7$, a→c sets $c = 11$ and b→d sets $d = 11$. In round 2, b→c lowers $c$ to $7 - 2 = 5$, and c→a then lowers $a$ to $5 -
1 = 4$; but c→d was already relaxed this round, before $c$ improved. Round 3 fixes $d = 5 + 2 = 7$. Round 4 changes
nothing, so the program stops early (an optimisation every implementation should have: if a full round changes
nothing, no later round will). The distances are $a = 4$ (by s, b, c, a), $b = 7$, $c = 5$, $d = 7$ (by s, b, c, d).

The cycle a → b → c → a weighs $3 - 2 - 1 = 0$: not negative, so shortest paths exist. Change c→a to −2 and the cycle
weighs −1. Then the final check fails, and the program walks back along parent pointers to print the cycle: c → a →
b → c.

**Finding the cycle.** When the check fails on edge $u \to v$, set $\mathrm{parent}[v] = u$ and walk back $V$
steps along parent pointers from $v$; then keep walking until you return to where you landed, and the vertices
passed form a negative cycle. One half of why is easy to prove: **any cycle formed by parent pointers has negative
weight.** Whenever $\mathrm{parent}[x] = p$ is set, $d[x] = d[p] + w(p, x)$, and afterwards $d[p]$ can only
decrease, so $d[x] \ge d[p] + w(p, x)$ holds for every parent edge from then on. Go round a cycle of parent edges
and look at the edge whose pointer was set last: just before that, it held with strict inequality ($d[x] > d[p] +
w(p,x)$, which is why the relaxation happened), and the others held with $\ge$. Summing round the cycle, the $d$
values cancel and leave $0 > \sum w$. The other half, that walking back $V$ steps from $v$ always reaches such a
cycle, is standard but longer; see Cherkassky and Goldberg (1999) for the analysis of negative-cycle detection.

**History.** The method has many fathers. Alfonso Shimbel described it in 1955; Lester Ford Jr. gave it in a 1956
RAND report on network flows; Richard Bellman published it in 1958 in "On a routing problem"; and Edward F. Moore
gave it in 1959 (his maze paper, the same one that described BFS). It is sometimes called Bellman-Ford-Moore.

**Speed-ups in practice.** Only vertices whose $d$ changed in the last round can cause changes in the next. Keeping
such vertices in a FIFO queue gives a variant (sometimes called SPFA) that is often much faster on real graphs,
though its worst case is still $O(VE)$. The routing protocol RIP, used on early networks, is a distributed
Bellman-Ford: each router relaxes using its neighbours' distance tables.

### Uses of negative weights

- **Difference constraints.** A system of inequalities $x_j - x_i \le b_{ij}$ (schedules where task $j$ starts at
  most $b_{ij}$ after task $i$) has a solution iff the graph with an edge $i \to j$ of weight $b_{ij}$, plus a source
  joined to every vertex by weight 0, has no negative cycle; and then $x_v = \delta(s, v)$ is a solution, because
  the triangle inequality is exactly the constraint. This is how some schedulers and timing-analysis tools work.
- **Arbitrage.** If exchange rates multiply round a cycle to more than 1, you can make money from nothing. Taking
  $w = -\log(\text{rate})$ turns "product $> 1$" into "sum $< 0$": arbitrage is a negative cycle (exercise 5).

<figure class="play" data-play="negedge"><span class="ai-tag">AI-created</span><figcaption>Try it: one edge of −4. Dijkstra settles a node too early and keeps the wrong distance; Bellman-Ford relaxes every edge again and finds the true one. Small made-up graph.</figcaption></figure>

## 16.4 Shortest paths in a DAG

If the graph has no directed cycle, there is a much faster way, and it even allows negative weights. Relax the
edges in **topological order** ([Chapter 15](15-Graphs-and-Graph-Search.md)): take the vertices in that order, and
relax every edge leaving each.

```text
DAG-SHORTEST(G, s):
    d[v] = infinity for all v;  d[s] = 0
    for u in topological order:
        for each edge u -> v:  RELAX(u, v)
```

**Theorem 16.6.** In a DAG, DAG-SHORTEST computes $d[v] = \delta(s, v)$ for every $v$ in $O(V + E)$ time, for any
real weights.

*Proof.* A DAG has no cycles, so no negative cycles, and every shortest path $s = v_0, \dots, v_k$ visits its
vertices in topological order. Each vertex's out-edges are relaxed when it is reached in that order, so the path
edges are relaxed in path order, and the path-relaxation property finishes. Time: a topological sort is $O(V + E)$
and each edge is relaxed once. $\square$

**Longest paths and critical paths.** In a general graph, finding the longest simple path is NP-hard
([Chapter 22](22-NP-Completeness.md)): it would solve the Hamiltonian path problem. In a DAG it is easy. Negate every
weight and find shortest paths, or equivalently replace min by max in the relaxation. This is the **critical-path
method** for project scheduling: if each edge is a task with a duration, the longest path from start to finish is
the shortest possible length of the whole project, and the tasks on it are the ones whose delay delays everything.

The program's DAG has edges r→s 5, r→t 3, s→t 2, s→x 6, t→x 7, t→y 4, t→z 2, x→y −1, x→z 1, y→z −2, with
topological order r, s, t, x, y, z. From $s$: $t = 2$, $x = 6$, $y = 5$ (via $x$, using the negative edge),
$z = 3$ (via $x$ and $y$). The longest paths from $r$: $s = 5$, $t = 7$ (r, s, t beats r, t), $x = 14$, $y = 13$, $z
= 15$, along the critical path r, s, t, x, z.

## 16.5 All pairs: Floyd-Warshall and Johnson

Sometimes you want the whole table: the distance from every place to every other, for a road atlas or for a
program that will answer many queries. One option is to run a single-source algorithm from every vertex: $V$ runs
of Dijkstra cost $O(VE \log V)$ with a binary heap, which is good for sparse graphs with non-negative weights; $V$
runs of Bellman-Ford cost $O(V^2 E)$, which can be $O(V^4)$. Two better methods follow.

### Floyd-Warshall: dynamic programming over intermediate vertices

Number the vertices $1, \dots, n$. The clever choice of subproblem is to restrict which vertices a path may pass
*through*. Let

$$
D^{(k)}[i][j] = \text{the weight of a shortest path from } i \text{ to } j \text{ whose intermediate vertices all lie in } \{1, \dots, k\}.
$$

For $k = 0$ no intermediate vertex is allowed, so $D^{(0)}[i][j]$ is $w(i,j)$ if there is an edge, 0 if $i = j$, and
$\infty$ otherwise. For $D^{(k)}$, look at a shortest path from $i$ to $j$ with intermediates in $\{1, \dots, k\}$.
Either it does not pass through $k$, and then its intermediates are in $\{1, \dots, k-1\}$; or it does, exactly
once (it is simple, with no negative cycles), and splits into $i \leadsto k$ and $k \leadsto j$, each with
intermediates in $\{1, \dots, k-1\}$ and each shortest by Lemma 16.1. So

$$
D^{(k)}[i][j] = \min\big( D^{(k-1)}[i][j],\ D^{(k-1)}[i][k] + D^{(k-1)}[k][j] \big),
$$

and $D^{(n)}$ is the answer, since then every vertex may be used. That gives three nested loops:

```text
for k = 1..n:
    for i = 1..n:
        for j = 1..n:
            D[i][j] = min(D[i][j], D[i][k] + D[k][j])
```

**Theorem 16.7.** With no negative cycle, Floyd-Warshall computes all distances in $\Theta(V^3)$ time and
$\Theta(V^2)$ space, updating a single matrix in place.

*Proof.* The recurrence is proved above; the induction on $k$ gives correctness of $D^{(k)}$ for all $k$. Updating
in place is safe because during round $k$ the entries $D[i][k]$ and $D[k][j]$ do not change: $D^{(k)}[i][k] =
\min(D^{(k-1)}[i][k], D^{(k-1)}[i][k] + D^{(k-1)}[k][k])$ and $D^{(k-1)}[k][k] = 0$ without negative cycles.
Overwriting an entry with a smaller value that is still the weight of a real path never breaks the upper-bound
property. The three loops do $n^3$ constant-time steps. $\square$

**A trace.** The program uses four vertices 0 to 3 and edges 0→1 3, 0→2 8, 1→3 1, 2→1 4, 3→0 2, 3→2 −5. The
matrices after each round $k$ (rows are sources, columns targets):

| | start | after $k = 0$ | after $k = 1$ | after $k = 2$ | after $k = 3$ |
|---|---|---|---|---|---|
| row 0 | 0 3 8 ∞ | 0 3 8 ∞ | 0 3 8 **4** | 0 3 8 4 | 0 3 **−1** 4 |
| row 1 | ∞ 0 ∞ 1 | ∞ 0 ∞ 1 | ∞ 0 ∞ 1 | ∞ 0 ∞ 1 | **3** 0 **−4** 1 |
| row 2 | ∞ 4 0 ∞ | ∞ 4 0 ∞ | ∞ 4 0 **5** | ∞ 4 0 5 | **7** 4 0 5 |
| row 3 | 2 ∞ −5 0 | 2 **5** −5 0 | 2 5 −5 0 | 2 **−1** −5 0 | 2 −1 −5 0 |

(Here the vertices are numbered from 0, so "after $k = 0$" allows vertex 0 as an intermediate.) Read one entry:
row 1, column 2 is $-4$, by the path 1 → 3 → 2 of weight $1 - 5$. It appears only when vertex 3 is allowed. Row 3,
column 1 becomes 5 when vertex 0 is allowed (3 → 0 → 1, $2 + 3$) and then −1 when vertex 2 is allowed
(3 → 2 → 1, $-5 + 4$).

**Negative cycles and paths.** If there is a negative cycle, some diagonal entry $D[i][i]$ ends negative, which is
the standard test (exercise 6). To recover paths, keep a second table $\mathrm{next}[i][j]$, the first step on the
best path from $i$ to $j$, and update it with each improvement (exercise 9).

Robert Floyd published the algorithm in 1962 as "Algorithm 97: Shortest path"; Stephen Warshall published the same
loop structure for transitive closure (which vertices can reach which) the same year, and Bernard Roy had given it
in 1959. The reference page [Floyd-Warshall](../../graphs/floyd-warshall.md) animates it.

### Johnson's algorithm: reweighting

For a sparse graph with negative edges, $V^3$ is wasteful: we would like $V$ runs of Dijkstra, $O(VE \log V)$. The
obstacle is the negative edges. Adding a constant to every edge does not help, because it penalises paths with many
edges (exercise 2). Donald Johnson's 1977 idea is subtler: give every vertex a **potential** $h(v)$ and change the
weights to

$$
\hat w(u, v) = w(u, v) + h(u) - h(v).
$$

**Lemma 16.8 (reweighting preserves shortest paths).** For any path $p = v_0, \dots, v_k$,
$\hat w(p) = w(p) + h(v_0) - h(v_k)$.

*Proof.* The sum telescopes: $\sum_{i=1}^{k} \big(w(v_{i-1}, v_i) + h(v_{i-1}) - h(v_i)\big) = w(p) + h(v_0) -
h(v_k)$. $\square$

Every path from $u$ to $v$ changes by the same amount $h(u) - h(v)$, so the shortest ones stay shortest, and every
cycle keeps its weight (the change is $h(v_0) - h(v_0) = 0$). Now choose $h$ to make every $\hat w \ge 0$. Add a new
vertex $q$ with an edge of weight 0 to every vertex, run Bellman-Ford from $q$ (which also detects negative
cycles), and set $h(v) = \delta(q, v)$. By the triangle inequality, $h(v) \le h(u) + w(u, v)$ for every edge, which
says exactly $\hat w(u, v) \ge 0$.

So Johnson's algorithm is: one Bellman-Ford, $O(VE)$; reweight; $V$ runs of Dijkstra, $O(VE \log V)$; and finally
undo the shift, $\delta(u,v) = \hat\delta(u,v) - h(u) + h(v)$. Total $O(VE \log V)$, or $O(VE + V^2 \log V)$ with
Fibonacci heaps.

On the Floyd-Warshall example the program finds $h = (0, -1, -5, 0)$ and new weights 0→1 4, 0→2 13, 1→3 0, 2→1 0,
3→0 2, 3→2 0, all non-negative, and its final table equals the Floyd-Warshall one.

## 16.6 A* search and bidirectional search

Dijkstra's water spreads in all directions. If you want only the route from Erebus Montes to Gale crater, most of
that work is wasted on places in the wrong direction. **A\*** (read "A star") aims the search.

Suppose that for every vertex $v$ we have a guess $h(v)$ of the remaining distance to the target $t$, a
**heuristic**. A\* is Dijkstra's algorithm in which the vertex chosen next is the one with the smallest

$$
f(v) = d[v] + h(v),
$$

the known distance so far plus the guessed distance still to go. It stops when it settles $t$. With $h = 0$ it is
exactly Dijkstra.

**Definitions.** A heuristic is **admissible** if it never overestimates: $h(v) \le \delta(v, t)$ for all $v$. It is
**consistent** (or monotone) if $h(t) = 0$ and, for every edge, $h(u) \le w(u, v) + h(v)$: the guess cannot drop by
more than the edge you walk. Consistent implies admissible (sum the inequality along a shortest path from $v$ to
$t$). On a map, the straight-line distance to the target is consistent, by the triangle inequality of geometry: no
road is shorter than the straight line between its ends. On a grid where you move one step up, down, left or
right, the **Manhattan distance** $|r - r_t| + |c - c_t|$ is consistent.

**Theorem 16.9 (A\* is Dijkstra on reweighted edges).** With a consistent heuristic $h$, A\* settles vertices in
exactly the order Dijkstra's algorithm would on the reweighted graph $\hat w(u,v) = w(u, v) - h(u) + h(v)$, and it
returns a shortest path to $t$.

*Proof.* This is Johnson's reweighting with potential $-h$. By consistency $\hat w(u,v) \ge 0$, so Dijkstra is
correct on $\hat w$. By Lemma 16.8, a path $p$ from $s$ to $v$ has $\hat w(p) = w(p) - h(s) + h(v)$, so
Dijkstra's estimate on $\hat w$ is $\hat d[v] = d[v] + h(v) - h(s) = f(v) - h(s)$. Choosing the smallest $\hat
d$ is choosing the smallest $f$, since $h(s)$ is a constant. When $t$ is settled, $\hat d[t] = \hat\delta(s,t) =
\delta(s,t) - h(s) + h(t)$ and $h(t) = 0$, so $d[t] = \delta(s,t)$. $\square$

This is the cleanest way to see A\*: it is not a new algorithm, it is Dijkstra on a tilted map, tilted so that
"downhill" points at the target. The better the guess, the steeper the tilt and the fewer vertices settled. With
the perfect guess $h(v) = \delta(v, t)$, every edge on a shortest path to $t$ has $\hat w = 0$, and A\* walks
straight there.

**Admissible but not consistent.** Hart, Nilsson and Raphael proved that A\* with an admissible heuristic also finds
an optimal path, provided it is allowed to **reopen** a vertex whose $d$ improves after it was settled. The
argument: until $t$ is settled, some vertex $y$ on an optimal path is in the queue with $d[y] = \delta(s,y)$ (the
first unsettled vertex on that path, as in Dijkstra's proof), and $f(y) = \delta(s,y) + h(y) \le \delta(s,y) +
\delta(y,t) = \delta(s,t)$. So no non-optimal $t$ entry, with $f = d[t] > \delta(s,t)$, can come out of the queue
before $y$; repeating the argument, $t$ comes out with its optimal value. Without consistency, a vertex may be
settled several times, and the running time can grow; with consistency each vertex is settled once.

**On the grid.** The program builds a 60 × 60 grid in which each cell is a wall with probability 1/4 (fixed seed
7), and searches from the top-left corner to the bottom-right corner, each step costing 1.

```
  free cells 2663; BFS distance 118
  Dijkstra (h = 0):      cost 118, settled 2627
  A* (Manhattan):        cost 118, settled 840
  bidirectional Dijkstra: cost 118, settled 2041
  A* with ALT (4 landmarks): cost 118, settled 466
```

All four agree that the shortest route has 118 steps (the BFS check confirms it). Dijkstra settles 2627 of the 2663
open cells, almost everything, because the goal is in the far corner. A\* with the Manhattan guess settles 840.
Figure 16.4 shows where each search spent its effort.

<figure class="mars-fig" markdown="0">
<svg viewBox="0 0 620 240" role="img" aria-label="Three 60 by 60 grids with walls; cells settled by Dijkstra, by A star with the Manhattan heuristic and by A star with landmarks are shaded; the shortest path is drawn in orange">
<text x="110" y="20" font-size="13" text-anchor="middle" fill="currentColor">Dijkstra: 2627 settled</text>
<rect x="20" y="30" width="180" height="180" fill="none" stroke="currentColor" stroke-width="1"/>
<rect x="23" y="30" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="29" y="30" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="38" y="30" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="44" y="30" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="50" y="30" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="62" y="30" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="83" y="30" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="92" y="30" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="104" y="30" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="119" y="30" width="9" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="152" y="30" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="173" y="30" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="182" y="30" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="188" y="30" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="26" y="30" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="32" y="30" width="6" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="41" y="30" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="47" y="30" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="56" y="30" width="6" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="68" y="30" width="15" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="86" y="30" width="6" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="107" y="30" width="12" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="128" y="30" width="24" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="155" y="30" width="18" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="176" y="30" width="6" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="191" y="30" width="9" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="20" y="30" width="3" height="3" fill="#eea66f" fill-opacity="1"/>
<rect x="50" y="33" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="74" y="33" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="80" y="33" width="9" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="92" y="33" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="104" y="33" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="137" y="33" width="12" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="158" y="33" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="185" y="33" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="47" y="33" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="53" y="33" width="21" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="77" y="33" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="89" y="33" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="107" y="33" width="30" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="149" y="33" width="9" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="161" y="33" width="24" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="188" y="33" width="12" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="20" y="33" width="27" height="3" fill="#eea66f" fill-opacity="1"/>
<rect x="26" y="36" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="32" y="36" width="12" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="47" y="36" width="12" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="62" y="36" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="71" y="36" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="83" y="36" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="98" y="36" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="113" y="36" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="125" y="36" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="131" y="36" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="152" y="36" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="167" y="36" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="188" y="36" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="197" y="36" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="20" y="36" width="6" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="29" y="36" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="59" y="36" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="65" y="36" width="6" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="74" y="36" width="9" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="86" y="36" width="12" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="104" y="36" width="9" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="119" y="36" width="6" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="128" y="36" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="134" y="36" width="18" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="155" y="36" width="12" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="170" y="36" width="18" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="191" y="36" width="6" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="44" y="36" width="3" height="3" fill="#eea66f" fill-opacity="1"/>
<rect x="20" y="39" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="50" y="39" width="12" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="80" y="39" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="98" y="39" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="125" y="39" width="9" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="140" y="39" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="158" y="39" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="185" y="39" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="194" y="39" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="23" y="39" width="21" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="62" y="39" width="18" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="83" y="39" width="15" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="101" y="39" width="24" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="134" y="39" width="6" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="143" y="39" width="15" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="164" y="39" width="21" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="188" y="39" width="6" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="197" y="39" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="44" y="39" width="6" height="3" fill="#eea66f" fill-opacity="1"/>
<rect x="26" y="42" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="59" y="42" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="65" y="42" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="74" y="42" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="98" y="42" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="104" y="42" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="173" y="42" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="182" y="42" width="9" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="20" y="42" width="6" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="29" y="42" width="18" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="56" y="42" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="62" y="42" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="71" y="42" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="77" y="42" width="21" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="101" y="42" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="107" y="42" width="66" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="179" y="42" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="191" y="42" width="9" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="47" y="42" width="9" height="3" fill="#eea66f" fill-opacity="1"/>
<rect x="20" y="45" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="29" y="45" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="38" y="45" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="56" y="45" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="68" y="45" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="77" y="45" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="86" y="45" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="98" y="45" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="110" y="45" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="116" y="45" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="125" y="45" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="140" y="45" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="152" y="45" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="164" y="45" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="176" y="45" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="182" y="45" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="23" y="45" width="6" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="32" y="45" width="6" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="41" y="45" width="12" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="59" y="45" width="9" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="71" y="45" width="6" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="80" y="45" width="6" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="89" y="45" width="9" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="101" y="45" width="9" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="113" y="45" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="119" y="45" width="6" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="128" y="45" width="12" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="143" y="45" width="9" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="158" y="45" width="6" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="167" y="45" width="9" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="179" y="45" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="185" y="45" width="15" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="53" y="45" width="3" height="3" fill="#eea66f" fill-opacity="1"/>
<rect x="23" y="48" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="29" y="48" width="15" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="59" y="48" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="65" y="48" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="71" y="48" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="80" y="48" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="89" y="48" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="134" y="48" width="9" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="149" y="48" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="167" y="48" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="176" y="48" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="194" y="48" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="26" y="48" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="44" y="48" width="9" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="56" y="48" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="62" y="48" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="68" y="48" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="74" y="48" width="6" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="83" y="48" width="6" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="92" y="48" width="42" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="143" y="48" width="6" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="155" y="48" width="12" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="170" y="48" width="6" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="179" y="48" width="15" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="197" y="48" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="53" y="48" width="3" height="3" fill="#eea66f" fill-opacity="1"/>
<rect x="26" y="51" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="38" y="51" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="44" y="51" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="50" y="51" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="56" y="51" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="65" y="51" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="95" y="51" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="104" y="51" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="122" y="51" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="152" y="51" width="9" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="164" y="51" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="185" y="51" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="29" y="51" width="9" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="47" y="51" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="62" y="51" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="68" y="51" width="27" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="98" y="51" width="6" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="107" y="51" width="15" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="125" y="51" width="27" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="161" y="51" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="167" y="51" width="18" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="188" y="51" width="12" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="53" y="51" width="3" height="3" fill="#eea66f" fill-opacity="1"/>
<rect x="23" y="54" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="32" y="54" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="41" y="54" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="71" y="54" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="89" y="54" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="119" y="54" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="125" y="54" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="134" y="54" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="152" y="54" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="158" y="54" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="164" y="54" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="173" y="54" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="188" y="54" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="197" y="54" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="26" y="54" width="6" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="35" y="54" width="6" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="44" y="54" width="9" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="77" y="54" width="12" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="95" y="54" width="24" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="122" y="54" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="128" y="54" width="6" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="137" y="54" width="15" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="155" y="54" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="161" y="54" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="167" y="54" width="6" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="176" y="54" width="12" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="191" y="54" width="6" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="53" y="54" width="18" height="3" fill="#eea66f" fill-opacity="1"/>
<rect x="20" y="57" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="32" y="57" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="44" y="57" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="53" y="57" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="89" y="57" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="104" y="57" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="113" y="57" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="143" y="57" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="161" y="57" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="167" y="57" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="23" y="57" width="9" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="35" y="57" width="9" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="47" y="57" width="6" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="56" y="57" width="12" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="95" y="57" width="9" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="107" y="57" width="6" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="116" y="57" width="27" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="146" y="57" width="15" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="164" y="57" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="170" y="57" width="30" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="68" y="57" width="21" height="3" fill="#eea66f" fill-opacity="1"/>
<rect x="20" y="60" width="9" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="35" y="60" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="47" y="60" width="9" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="59" y="60" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="92" y="60" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="101" y="60" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="113" y="60" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="119" y="60" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="137" y="60" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="155" y="60" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="173" y="60" width="9" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="29" y="60" width="6" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="38" y="60" width="9" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="56" y="60" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="65" y="60" width="21" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="95" y="60" width="6" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="104" y="60" width="9" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="116" y="60" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="122" y="60" width="15" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="143" y="60" width="12" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="158" y="60" width="15" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="182" y="60" width="18" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="86" y="60" width="6" height="3" fill="#eea66f" fill-opacity="1"/>
<rect x="26" y="63" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="32" y="63" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="44" y="63" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="56" y="63" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="71" y="63" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="77" y="63" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="98" y="63" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="113" y="63" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="134" y="63" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="149" y="63" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="161" y="63" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="173" y="63" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="191" y="63" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="20" y="63" width="6" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="29" y="63" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="35" y="63" width="9" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="47" y="63" width="9" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="62" y="63" width="9" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="74" y="63" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="80" y="63" width="9" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="92" y="63" width="6" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="104" y="63" width="9" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="116" y="63" width="18" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="140" y="63" width="9" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="152" y="63" width="9" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="164" y="63" width="9" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="179" y="63" width="12" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="197" y="63" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="89" y="63" width="3" height="3" fill="#eea66f" fill-opacity="1"/>
<rect x="26" y="66" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="32" y="66" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="38" y="66" width="9" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="68" y="66" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="77" y="66" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="92" y="66" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="107" y="66" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="113" y="66" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="128" y="66" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="140" y="66" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="149" y="66" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="161" y="66" width="9" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="20" y="66" width="6" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="29" y="66" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="35" y="66" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="47" y="66" width="21" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="71" y="66" width="6" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="80" y="66" width="9" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="98" y="66" width="9" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="110" y="66" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="116" y="66" width="12" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="131" y="66" width="9" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="143" y="66" width="6" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="152" y="66" width="9" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="170" y="66" width="30" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="89" y="66" width="3" height="3" fill="#eea66f" fill-opacity="1"/>
<rect x="26" y="69" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="41" y="69" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="71" y="69" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="101" y="69" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="110" y="69" width="9" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="137" y="69" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="152" y="69" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="173" y="69" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="191" y="69" width="9" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="20" y="69" width="6" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="29" y="69" width="12" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="47" y="69" width="24" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="74" y="69" width="15" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="119" y="69" width="18" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="143" y="69" width="9" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="155" y="69" width="18" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="176" y="69" width="15" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="89" y="69" width="12" height="3" fill="#eea66f" fill-opacity="1"/>
<rect x="20" y="72" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="41" y="72" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="53" y="72" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="68" y="72" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="74" y="72" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="107" y="72" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="116" y="72" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="122" y="72" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="137" y="72" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="149" y="72" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="155" y="72" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="164" y="72" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="179" y="72" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="23" y="72" width="18" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="44" y="72" width="9" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="56" y="72" width="12" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="80" y="72" width="18" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="110" y="72" width="6" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="119" y="72" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="128" y="72" width="9" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="143" y="72" width="6" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="152" y="72" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="158" y="72" width="6" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="170" y="72" width="9" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="185" y="72" width="15" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="98" y="72" width="9" height="3" fill="#eea66f" fill-opacity="1"/>
<rect x="41" y="75" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="47" y="75" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="71" y="75" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="86" y="75" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="98" y="75" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="110" y="75" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="122" y="75" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="137" y="75" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="155" y="75" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="161" y="75" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="173" y="75" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="188" y="75" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="20" y="75" width="21" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="44" y="75" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="53" y="75" width="18" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="77" y="75" width="9" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="89" y="75" width="9" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="101" y="75" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="113" y="75" width="9" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="128" y="75" width="9" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="140" y="75" width="15" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="158" y="75" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="164" y="75" width="9" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="179" y="75" width="9" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="194" y="75" width="6" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="104" y="75" width="6" height="3" fill="#eea66f" fill-opacity="1"/>
<rect x="20" y="78" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="29" y="78" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="35" y="78" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="68" y="78" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="77" y="78" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="89" y="78" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="95" y="78" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="104" y="78" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="113" y="78" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="119" y="78" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="131" y="78" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="143" y="78" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="158" y="78" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="173" y="78" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="182" y="78" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="191" y="78" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="23" y="78" width="6" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="32" y="78" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="38" y="78" width="30" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="71" y="78" width="6" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="80" y="78" width="9" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="92" y="78" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="101" y="78" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="116" y="78" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="122" y="78" width="9" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="134" y="78" width="9" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="146" y="78" width="12" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="161" y="78" width="12" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="176" y="78" width="6" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="185" y="78" width="6" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="194" y="78" width="6" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="107" y="78" width="6" height="3" fill="#eea66f" fill-opacity="1"/>
<rect x="23" y="81" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="32" y="81" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="44" y="81" width="9" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="62" y="81" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="68" y="81" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="92" y="81" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="125" y="81" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="131" y="81" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="155" y="81" width="9" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="176" y="81" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="185" y="81" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="194" y="81" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="26" y="81" width="6" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="35" y="81" width="9" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="53" y="81" width="9" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="65" y="81" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="71" y="81" width="21" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="95" y="81" width="15" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="116" y="81" width="9" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="128" y="81" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="134" y="81" width="21" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="164" y="81" width="12" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="197" y="81" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="110" y="81" width="6" height="3" fill="#eea66f" fill-opacity="1"/>
<rect x="20" y="84" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="29" y="84" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="38" y="84" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="44" y="84" width="9" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="68" y="84" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="92" y="84" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="98" y="84" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="107" y="84" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="116" y="84" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="125" y="84" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="143" y="84" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="152" y="84" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="164" y="84" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="182" y="84" width="12" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="23" y="84" width="6" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="32" y="84" width="6" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="41" y="84" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="53" y="84" width="15" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="71" y="84" width="21" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="95" y="84" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="101" y="84" width="6" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="119" y="84" width="6" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="131" y="84" width="12" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="146" y="84" width="6" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="167" y="84" width="15" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="194" y="84" width="6" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="113" y="84" width="3" height="3" fill="#eea66f" fill-opacity="1"/>
<rect x="53" y="87" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="59" y="87" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="65" y="87" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="86" y="87" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="128" y="87" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="134" y="87" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="140" y="87" width="9" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="155" y="87" width="9" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="176" y="87" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="194" y="87" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="20" y="87" width="33" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="56" y="87" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="62" y="87" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="68" y="87" width="18" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="89" y="87" width="24" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="116" y="87" width="12" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="131" y="87" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="137" y="87" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="149" y="87" width="6" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="164" y="87" width="12" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="179" y="87" width="15" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="197" y="87" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="113" y="87" width="3" height="3" fill="#eea66f" fill-opacity="1"/>
<rect x="26" y="90" width="12" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="56" y="90" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="65" y="90" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="74" y="90" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="104" y="90" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="125" y="90" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="131" y="90" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="137" y="90" width="9" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="152" y="90" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="164" y="90" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="185" y="90" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="194" y="90" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="20" y="90" width="6" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="38" y="90" width="18" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="62" y="90" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="68" y="90" width="6" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="77" y="90" width="27" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="107" y="90" width="6" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="116" y="90" width="9" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="128" y="90" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="146" y="90" width="6" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="155" y="90" width="9" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="167" y="90" width="18" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="188" y="90" width="6" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="197" y="90" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="113" y="90" width="3" height="3" fill="#eea66f" fill-opacity="1"/>
<rect x="20" y="93" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="47" y="93" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="53" y="93" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="74" y="93" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="98" y="93" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="110" y="93" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="122" y="93" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="131" y="93" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="146" y="93" width="9" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="161" y="93" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="167" y="93" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="176" y="93" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="182" y="93" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="23" y="93" width="24" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="50" y="93" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="59" y="93" width="15" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="77" y="93" width="21" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="101" y="93" width="9" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="116" y="93" width="6" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="125" y="93" width="6" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="137" y="93" width="9" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="155" y="93" width="6" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="164" y="93" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="170" y="93" width="6" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="179" y="93" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="185" y="93" width="15" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="113" y="93" width="3" height="3" fill="#eea66f" fill-opacity="1"/>
<rect x="20" y="96" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="26" y="96" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="35" y="96" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="56" y="96" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="83" y="96" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="116" y="96" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="152" y="96" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="170" y="96" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="176" y="96" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="188" y="96" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="23" y="96" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="32" y="96" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="38" y="96" width="18" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="59" y="96" width="24" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="86" y="96" width="27" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="119" y="96" width="33" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="155" y="96" width="15" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="173" y="96" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="179" y="96" width="9" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="191" y="96" width="9" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="113" y="96" width="3" height="3" fill="#eea66f" fill-opacity="1"/>
<rect x="38" y="99" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="50" y="99" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="59" y="99" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="68" y="99" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="86" y="99" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="98" y="99" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="107" y="99" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="128" y="99" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="155" y="99" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="179" y="99" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="191" y="99" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="20" y="99" width="18" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="41" y="99" width="9" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="53" y="99" width="6" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="62" y="99" width="6" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="71" y="99" width="15" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="89" y="99" width="9" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="101" y="99" width="6" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="116" y="99" width="12" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="131" y="99" width="24" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="158" y="99" width="21" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="185" y="99" width="6" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="194" y="99" width="6" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="113" y="99" width="3" height="3" fill="#eea66f" fill-opacity="1"/>
<rect x="38" y="102" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="50" y="102" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="59" y="102" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="74" y="102" width="9" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="89" y="102" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="98" y="102" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="122" y="102" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="146" y="102" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="155" y="102" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="161" y="102" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="176" y="102" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="20" y="102" width="18" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="41" y="102" width="9" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="53" y="102" width="6" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="65" y="102" width="9" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="83" y="102" width="6" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="92" y="102" width="6" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="101" y="102" width="12" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="116" y="102" width="6" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="125" y="102" width="21" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="152" y="102" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="158" y="102" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="164" y="102" width="12" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="179" y="102" width="21" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="113" y="102" width="3" height="3" fill="#eea66f" fill-opacity="1"/>
<rect x="23" y="105" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="32" y="105" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="59" y="105" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="86" y="105" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="146" y="105" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="158" y="105" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="164" y="105" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="20" y="105" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="26" y="105" width="6" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="35" y="105" width="24" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="62" y="105" width="24" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="89" y="105" width="24" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="116" y="105" width="30" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="149" y="105" width="9" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="161" y="105" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="170" y="105" width="30" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="113" y="105" width="3" height="3" fill="#eea66f" fill-opacity="1"/>
<rect x="23" y="108" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="35" y="108" width="9" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="86" y="108" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="92" y="108" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="110" y="108" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="131" y="108" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="137" y="108" width="12" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="152" y="108" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="158" y="108" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="164" y="108" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="173" y="108" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="179" y="108" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="197" y="108" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="20" y="108" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="26" y="108" width="9" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="44" y="108" width="42" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="89" y="108" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="98" y="108" width="12" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="116" y="108" width="15" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="134" y="108" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="149" y="108" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="155" y="108" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="161" y="108" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="170" y="108" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="176" y="108" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="185" y="108" width="12" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="113" y="108" width="3" height="3" fill="#eea66f" fill-opacity="1"/>
<rect x="41" y="111" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="53" y="111" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="62" y="111" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="71" y="111" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="86" y="111" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="122" y="111" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="176" y="111" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="194" y="111" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="20" y="111" width="21" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="47" y="111" width="6" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="56" y="111" width="6" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="65" y="111" width="6" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="74" y="111" width="12" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="89" y="111" width="24" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="116" y="111" width="6" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="125" y="111" width="51" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="179" y="111" width="15" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="197" y="111" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="113" y="111" width="3" height="3" fill="#eea66f" fill-opacity="1"/>
<rect x="47" y="114" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="56" y="114" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="65" y="114" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="77" y="114" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="92" y="114" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="101" y="114" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="122" y="114" width="9" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="146" y="114" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="158" y="114" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="167" y="114" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="179" y="114" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="20" y="114" width="27" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="50" y="114" width="6" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="59" y="114" width="6" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="68" y="114" width="9" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="80" y="114" width="12" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="95" y="114" width="6" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="104" y="114" width="9" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="116" y="114" width="6" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="131" y="114" width="15" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="152" y="114" width="6" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="161" y="114" width="6" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="170" y="114" width="9" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="185" y="114" width="15" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="113" y="114" width="3" height="3" fill="#eea66f" fill-opacity="1"/>
<rect x="41" y="117" width="15" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="71" y="117" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="80" y="117" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="107" y="117" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="116" y="117" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="137" y="117" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="152" y="117" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="176" y="117" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="185" y="117" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="191" y="117" width="9" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="20" y="117" width="21" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="56" y="117" width="15" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="74" y="117" width="6" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="83" y="117" width="24" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="110" y="117" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="122" y="117" width="15" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="140" y="117" width="12" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="158" y="117" width="18" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="179" y="117" width="6" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="188" y="117" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="113" y="117" width="3" height="3" fill="#eea66f" fill-opacity="1"/>
<rect x="23" y="120" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="29" y="120" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="38" y="120" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="50" y="120" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="56" y="120" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="83" y="120" width="9" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="98" y="120" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="110" y="120" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="122" y="120" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="134" y="120" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="140" y="120" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="149" y="120" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="161" y="120" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="176" y="120" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="185" y="120" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="197" y="120" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="20" y="120" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="26" y="120" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="35" y="120" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="41" y="120" width="9" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="59" y="120" width="24" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="92" y="120" width="6" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="101" y="120" width="9" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="125" y="120" width="9" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="137" y="120" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="143" y="120" width="6" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="152" y="120" width="9" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="164" y="120" width="12" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="179" y="120" width="6" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="188" y="120" width="9" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="113" y="120" width="9" height="3" fill="#eea66f" fill-opacity="1"/>
<rect x="26" y="123" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="38" y="123" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="47" y="123" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="53" y="123" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="65" y="123" width="9" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="83" y="123" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="98" y="123" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="113" y="123" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="131" y="123" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="146" y="123" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="155" y="123" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="164" y="123" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="176" y="123" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="20" y="123" width="6" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="32" y="123" width="6" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="41" y="123" width="6" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="59" y="123" width="6" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="74" y="123" width="9" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="86" y="123" width="12" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="104" y="123" width="9" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="116" y="123" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="128" y="123" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="134" y="123" width="12" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="149" y="123" width="6" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="158" y="123" width="6" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="167" y="123" width="9" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="179" y="123" width="21" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="119" y="123" width="9" height="3" fill="#eea66f" fill-opacity="1"/>
<rect x="20" y="126" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="41" y="126" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="47" y="126" width="9" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="62" y="126" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="71" y="126" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="89" y="126" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="98" y="126" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="113" y="126" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="119" y="126" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="128" y="126" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="137" y="126" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="170" y="126" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="194" y="126" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="23" y="126" width="18" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="44" y="126" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="56" y="126" width="6" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="68" y="126" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="77" y="126" width="12" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="92" y="126" width="6" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="104" y="126" width="9" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="116" y="126" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="122" y="126" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="131" y="126" width="6" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="140" y="126" width="30" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="173" y="126" width="21" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="197" y="126" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="125" y="126" width="3" height="3" fill="#eea66f" fill-opacity="1"/>
<rect x="26" y="129" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="41" y="129" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="50" y="129" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="77" y="129" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="122" y="129" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="143" y="129" width="9" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="161" y="129" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="182" y="129" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="20" y="129" width="6" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="29" y="129" width="12" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="44" y="129" width="6" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="56" y="129" width="21" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="80" y="129" width="42" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="152" y="129" width="9" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="167" y="129" width="15" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="185" y="129" width="15" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="125" y="129" width="18" height="3" fill="#eea66f" fill-opacity="1"/>
<rect x="23" y="132" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="38" y="132" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="47" y="132" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="68" y="132" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="80" y="132" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="92" y="132" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="104" y="132" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="149" y="132" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="155" y="132" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="20" y="132" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="29" y="132" width="9" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="41" y="132" width="6" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="50" y="132" width="18" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="74" y="132" width="6" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="83" y="132" width="9" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="98" y="132" width="6" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="107" y="132" width="33" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="152" y="132" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="158" y="132" width="42" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="140" y="132" width="9" height="3" fill="#eea66f" fill-opacity="1"/>
<rect x="44" y="135" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="50" y="135" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="59" y="135" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="77" y="135" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="86" y="135" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="140" y="135" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="182" y="135" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="197" y="135" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="20" y="135" width="24" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="47" y="135" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="53" y="135" width="6" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="62" y="135" width="15" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="80" y="135" width="6" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="92" y="135" width="48" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="143" y="135" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="152" y="135" width="30" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="185" y="135" width="12" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="146" y="135" width="6" height="3" fill="#eea66f" fill-opacity="1"/>
<rect x="38" y="138" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="50" y="138" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="71" y="138" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="86" y="138" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="101" y="138" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="128" y="138" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="137" y="138" width="9" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="158" y="138" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="176" y="138" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="182" y="138" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="20" y="138" width="18" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="41" y="138" width="9" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="56" y="138" width="15" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="74" y="138" width="12" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="89" y="138" width="12" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="104" y="138" width="24" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="134" y="138" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="146" y="138" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="152" y="138" width="6" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="164" y="138" width="12" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="179" y="138" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="185" y="138" width="15" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="149" y="138" width="3" height="3" fill="#eea66f" fill-opacity="1"/>
<rect x="20" y="141" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="38" y="141" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="74" y="141" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="83" y="141" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="98" y="141" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="107" y="141" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="119" y="141" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="131" y="141" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="143" y="141" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="152" y="141" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="164" y="141" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="170" y="141" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="179" y="141" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="191" y="141" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="23" y="141" width="15" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="44" y="141" width="30" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="77" y="141" width="6" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="86" y="141" width="12" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="104" y="141" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="110" y="141" width="9" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="122" y="141" width="9" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="158" y="141" width="6" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="167" y="141" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="173" y="141" width="6" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="182" y="141" width="9" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="194" y="141" width="6" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="149" y="141" width="3" height="3" fill="#eea66f" fill-opacity="1"/>
<rect x="26" y="144" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="35" y="144" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="41" y="144" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="59" y="144" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="65" y="144" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="71" y="144" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="101" y="144" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="116" y="144" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="131" y="144" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="137" y="144" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="164" y="144" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="170" y="144" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="191" y="144" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="20" y="144" width="6" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="29" y="144" width="6" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="44" y="144" width="15" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="62" y="144" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="68" y="144" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="74" y="144" width="27" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="107" y="144" width="9" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="119" y="144" width="12" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="134" y="144" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="143" y="144" width="6" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="161" y="144" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="167" y="144" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="173" y="144" width="18" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="194" y="144" width="6" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="149" y="144" width="12" height="3" fill="#eea66f" fill-opacity="1"/>
<rect x="23" y="147" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="38" y="147" width="12" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="56" y="147" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="65" y="147" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="89" y="147" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="101" y="147" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="110" y="147" width="9" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="122" y="147" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="131" y="147" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="149" y="147" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="176" y="147" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="191" y="147" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="197" y="147" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="20" y="147" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="29" y="147" width="9" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="50" y="147" width="6" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="59" y="147" width="6" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="68" y="147" width="21" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="92" y="147" width="9" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="104" y="147" width="6" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="119" y="147" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="125" y="147" width="6" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="134" y="147" width="15" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="152" y="147" width="6" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="161" y="147" width="15" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="179" y="147" width="12" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="194" y="147" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="158" y="147" width="3" height="3" fill="#eea66f" fill-opacity="1"/>
<rect x="41" y="150" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="53" y="150" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="59" y="150" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="68" y="150" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="92" y="150" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="110" y="150" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="128" y="150" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="137" y="150" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="146" y="150" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="155" y="150" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="167" y="150" width="9" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="182" y="150" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="194" y="150" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="20" y="150" width="21" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="47" y="150" width="6" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="62" y="150" width="6" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="74" y="150" width="18" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="95" y="150" width="15" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="113" y="150" width="15" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="131" y="150" width="6" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="143" y="150" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="149" y="150" width="6" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="161" y="150" width="6" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="176" y="150" width="6" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="185" y="150" width="9" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="197" y="150" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="158" y="150" width="3" height="3" fill="#eea66f" fill-opacity="1"/>
<rect x="23" y="153" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="29" y="153" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="50" y="153" width="9" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="68" y="153" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="80" y="153" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="95" y="153" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="116" y="153" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="146" y="153" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="155" y="153" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="161" y="153" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="170" y="153" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="179" y="153" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="185" y="153" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="20" y="153" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="26" y="153" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="32" y="153" width="18" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="59" y="153" width="9" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="71" y="153" width="9" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="83" y="153" width="12" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="98" y="153" width="18" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="122" y="153" width="24" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="149" y="153" width="6" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="164" y="153" width="6" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="176" y="153" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="188" y="153" width="12" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="158" y="153" width="3" height="3" fill="#eea66f" fill-opacity="1"/>
<rect x="47" y="156" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="62" y="156" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="95" y="156" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="128" y="156" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="140" y="156" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="164" y="156" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="176" y="156" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="185" y="156" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="20" y="156" width="27" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="50" y="156" width="12" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="68" y="156" width="27" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="98" y="156" width="30" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="134" y="156" width="6" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="143" y="156" width="15" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="170" y="156" width="6" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="188" y="156" width="12" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="158" y="156" width="6" height="3" fill="#eea66f" fill-opacity="1"/>
<rect x="20" y="159" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="26" y="159" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="35" y="159" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="41" y="159" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="59" y="159" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="68" y="159" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="77" y="159" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="89" y="159" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="95" y="159" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="104" y="159" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="110" y="159" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="140" y="159" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="158" y="159" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="173" y="159" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="179" y="159" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="188" y="159" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="23" y="159" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="29" y="159" width="6" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="38" y="159" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="44" y="159" width="15" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="62" y="159" width="6" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="71" y="159" width="6" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="80" y="159" width="9" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="92" y="159" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="101" y="159" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="107" y="159" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="113" y="159" width="27" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="143" y="159" width="15" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="191" y="159" width="9" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="161" y="159" width="12" height="3" fill="#eea66f" fill-opacity="1"/>
<rect x="20" y="162" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="32" y="162" width="9" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="44" y="162" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="59" y="162" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="77" y="162" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="83" y="162" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="95" y="162" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="113" y="162" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="128" y="162" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="134" y="162" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="143" y="162" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="164" y="162" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="173" y="162" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="182" y="162" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="23" y="162" width="9" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="41" y="162" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="47" y="162" width="12" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="62" y="162" width="15" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="80" y="162" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="86" y="162" width="9" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="101" y="162" width="12" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="116" y="162" width="12" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="131" y="162" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="137" y="162" width="6" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="149" y="162" width="15" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="167" y="162" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="188" y="162" width="12" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="170" y="162" width="3" height="3" fill="#eea66f" fill-opacity="1"/>
<rect x="35" y="165" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="98" y="165" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="116" y="165" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="125" y="165" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="146" y="165" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="176" y="165" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="20" y="165" width="15" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="38" y="165" width="60" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="101" y="165" width="15" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="122" y="165" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="131" y="165" width="15" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="152" y="165" width="18" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="173" y="165" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="182" y="165" width="18" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="170" y="165" width="3" height="3" fill="#eea66f" fill-opacity="1"/>
<rect x="20" y="168" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="35" y="168" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="47" y="168" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="53" y="168" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="65" y="168" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="77" y="168" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="89" y="168" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="107" y="168" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="128" y="168" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="134" y="168" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="155" y="168" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="167" y="168" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="179" y="168" width="9" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="191" y="168" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="23" y="168" width="12" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="41" y="168" width="6" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="50" y="168" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="56" y="168" width="9" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="68" y="168" width="9" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="80" y="168" width="9" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="95" y="168" width="12" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="110" y="168" width="18" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="131" y="168" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="137" y="168" width="18" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="158" y="168" width="9" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="173" y="168" width="6" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="188" y="168" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="194" y="168" width="6" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="170" y="168" width="3" height="3" fill="#eea66f" fill-opacity="1"/>
<rect x="74" y="171" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="95" y="171" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="101" y="171" width="12" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="119" y="171" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="128" y="171" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="140" y="171" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="149" y="171" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="176" y="171" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="182" y="171" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="194" y="171" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="20" y="171" width="54" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="80" y="171" width="15" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="98" y="171" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="113" y="171" width="6" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="122" y="171" width="6" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="134" y="171" width="6" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="146" y="171" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="152" y="171" width="18" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="173" y="171" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="179" y="171" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="185" y="171" width="9" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="197" y="171" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="170" y="171" width="3" height="3" fill="#eea66f" fill-opacity="1"/>
<rect x="32" y="174" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="44" y="174" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="62" y="174" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="68" y="174" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="98" y="174" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="116" y="174" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="131" y="174" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="143" y="174" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="152" y="174" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="158" y="174" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="164" y="174" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="173" y="174" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="191" y="174" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="20" y="174" width="12" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="35" y="174" width="9" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="50" y="174" width="12" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="65" y="174" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="71" y="174" width="27" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="101" y="174" width="15" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="119" y="174" width="12" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="134" y="174" width="9" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="149" y="174" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="155" y="174" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="161" y="174" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="176" y="174" width="15" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="197" y="174" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="170" y="174" width="3" height="3" fill="#eea66f" fill-opacity="1"/>
<rect x="23" y="177" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="29" y="177" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="35" y="177" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="50" y="177" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="56" y="177" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="62" y="177" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="68" y="177" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="77" y="177" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="92" y="177" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="107" y="177" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="113" y="177" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="131" y="177" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="179" y="177" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="185" y="177" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="20" y="177" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="26" y="177" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="32" y="177" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="41" y="177" width="9" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="53" y="177" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="59" y="177" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="65" y="177" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="71" y="177" width="6" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="80" y="177" width="12" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="95" y="177" width="12" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="110" y="177" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="119" y="177" width="12" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="134" y="177" width="36" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="182" y="177" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="188" y="177" width="12" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="170" y="177" width="9" height="3" fill="#eea66f" fill-opacity="1"/>
<rect x="23" y="180" width="9" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="41" y="180" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="62" y="180" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="80" y="180" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="116" y="180" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="140" y="180" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="161" y="180" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="185" y="180" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="197" y="180" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="20" y="180" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="32" y="180" width="9" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="44" y="180" width="18" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="65" y="180" width="15" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="83" y="180" width="33" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="119" y="180" width="21" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="146" y="180" width="15" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="167" y="180" width="9" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="188" y="180" width="9" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="176" y="180" width="9" height="3" fill="#eea66f" fill-opacity="1"/>
<rect x="20" y="183" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="26" y="183" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="41" y="183" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="65" y="183" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="77" y="183" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="89" y="183" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="98" y="183" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="113" y="183" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="119" y="183" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="128" y="183" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="143" y="183" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="179" y="183" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="197" y="183" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="23" y="183" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="29" y="183" width="12" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="44" y="183" width="21" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="68" y="183" width="9" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="80" y="183" width="9" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="95" y="183" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="104" y="183" width="9" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="116" y="183" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="122" y="183" width="6" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="131" y="183" width="12" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="146" y="183" width="33" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="188" y="183" width="9" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="182" y="183" width="6" height="3" fill="#eea66f" fill-opacity="1"/>
<rect x="38" y="186" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="83" y="186" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="98" y="186" width="9" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="110" y="186" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="122" y="186" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="134" y="186" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="155" y="186" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="164" y="186" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="194" y="186" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="20" y="186" width="18" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="41" y="186" width="42" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="86" y="186" width="12" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="107" y="186" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="116" y="186" width="6" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="125" y="186" width="9" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="137" y="186" width="18" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="158" y="186" width="6" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="167" y="186" width="18" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="188" y="186" width="6" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="197" y="186" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="185" y="186" width="3" height="3" fill="#eea66f" fill-opacity="1"/>
<rect x="32" y="189" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="59" y="189" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="68" y="189" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="116" y="189" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="125" y="189" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="131" y="189" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="137" y="189" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="161" y="189" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="167" y="189" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="173" y="189" width="9" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="20" y="189" width="12" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="38" y="189" width="21" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="62" y="189" width="6" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="71" y="189" width="45" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="119" y="189" width="6" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="128" y="189" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="134" y="189" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="140" y="189" width="21" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="164" y="189" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="170" y="189" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="182" y="189" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="188" y="189" width="12" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="185" y="189" width="3" height="3" fill="#eea66f" fill-opacity="1"/>
<rect x="23" y="192" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="32" y="192" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="41" y="192" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="53" y="192" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="65" y="192" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="77" y="192" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="86" y="192" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="92" y="192" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="107" y="192" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="113" y="192" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="143" y="192" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="158" y="192" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="173" y="192" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="179" y="192" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="197" y="192" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="20" y="192" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="29" y="192" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="35" y="192" width="6" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="44" y="192" width="9" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="56" y="192" width="9" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="68" y="192" width="9" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="80" y="192" width="6" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="89" y="192" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="95" y="192" width="12" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="110" y="192" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="116" y="192" width="27" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="146" y="192" width="12" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="164" y="192" width="9" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="176" y="192" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="182" y="192" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="188" y="192" width="9" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="185" y="192" width="3" height="3" fill="#eea66f" fill-opacity="1"/>
<rect x="26" y="195" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="32" y="195" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="41" y="195" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="47" y="195" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="62" y="195" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="68" y="195" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="74" y="195" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="89" y="195" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="110" y="195" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="119" y="195" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="128" y="195" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="134" y="195" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="146" y="195" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="152" y="195" width="9" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="170" y="195" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="188" y="195" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="194" y="195" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="20" y="195" width="6" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="29" y="195" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="35" y="195" width="6" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="44" y="195" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="50" y="195" width="12" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="71" y="195" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="77" y="195" width="12" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="95" y="195" width="15" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="116" y="195" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="122" y="195" width="6" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="131" y="195" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="137" y="195" width="9" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="149" y="195" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="161" y="195" width="9" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="173" y="195" width="12" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="191" y="195" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="197" y="195" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="185" y="195" width="3" height="3" fill="#eea66f" fill-opacity="1"/>
<rect x="20" y="198" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="35" y="198" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="41" y="198" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="53" y="198" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="65" y="198" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="89" y="198" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="101" y="198" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="113" y="198" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="119" y="198" width="9" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="158" y="198" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="170" y="198" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="179" y="198" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="191" y="198" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="23" y="198" width="12" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="38" y="198" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="44" y="198" width="9" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="59" y="198" width="6" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="68" y="198" width="21" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="92" y="198" width="9" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="107" y="198" width="6" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="116" y="198" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="128" y="198" width="30" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="161" y="198" width="9" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="173" y="198" width="6" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="182" y="198" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="194" y="198" width="6" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="185" y="198" width="6" height="3" fill="#eea66f" fill-opacity="1"/>
<rect x="59" y="201" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="74" y="201" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="83" y="201" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="119" y="201" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="140" y="201" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="146" y="201" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="167" y="201" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="182" y="201" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="20" y="201" width="39" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="62" y="201" width="12" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="80" y="201" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="86" y="201" width="33" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="122" y="201" width="18" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="143" y="201" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="152" y="201" width="15" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="170" y="201" width="12" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="185" y="201" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="197" y="201" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="188" y="201" width="9" height="3" fill="#eea66f" fill-opacity="1"/>
<rect x="20" y="204" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="26" y="204" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="32" y="204" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="44" y="204" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="71" y="204" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="77" y="204" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="83" y="204" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="104" y="204" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="128" y="204" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="170" y="204" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="197" y="204" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="23" y="204" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="29" y="204" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="35" y="204" width="9" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="47" y="204" width="24" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="74" y="204" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="80" y="204" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="89" y="204" width="15" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="107" y="204" width="21" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="131" y="204" width="39" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="173" y="204" width="21" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="194" y="204" width="3" height="3" fill="#eea66f" fill-opacity="1"/>
<rect x="23" y="207" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="32" y="207" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="41" y="207" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="95" y="207" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="110" y="207" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="119" y="207" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="125" y="207" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="131" y="207" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="146" y="207" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="155" y="207" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="164" y="207" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="182" y="207" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="26" y="207" width="6" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="35" y="207" width="6" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="44" y="207" width="51" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="98" y="207" width="12" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="113" y="207" width="6" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="122" y="207" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="134" y="207" width="12" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="149" y="207" width="6" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="158" y="207" width="6" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="167" y="207" width="15" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="185" y="207" width="9" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="194" y="207" width="6" height="3" fill="#eea66f" fill-opacity="1"/>
<text x="310" y="20" font-size="13" text-anchor="middle" fill="currentColor">A*, Manhattan: 840 settled</text>
<rect x="220" y="30" width="180" height="180" fill="none" stroke="currentColor" stroke-width="1"/>
<rect x="223" y="30" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="229" y="30" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="238" y="30" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="244" y="30" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="250" y="30" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="262" y="30" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="283" y="30" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="292" y="30" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="304" y="30" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="319" y="30" width="9" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="352" y="30" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="373" y="30" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="382" y="30" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="388" y="30" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="220" y="30" width="3" height="3" fill="#eea66f" fill-opacity="1"/>
<rect x="250" y="33" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="274" y="33" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="280" y="33" width="9" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="292" y="33" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="304" y="33" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="337" y="33" width="12" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="358" y="33" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="385" y="33" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="247" y="33" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="220" y="33" width="27" height="3" fill="#eea66f" fill-opacity="1"/>
<rect x="226" y="36" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="232" y="36" width="12" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="247" y="36" width="12" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="262" y="36" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="271" y="36" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="283" y="36" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="298" y="36" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="313" y="36" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="325" y="36" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="331" y="36" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="352" y="36" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="367" y="36" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="388" y="36" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="397" y="36" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="220" y="36" width="6" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="229" y="36" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="244" y="36" width="3" height="3" fill="#eea66f" fill-opacity="1"/>
<rect x="220" y="39" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="250" y="39" width="12" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="280" y="39" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="298" y="39" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="325" y="39" width="9" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="340" y="39" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="358" y="39" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="385" y="39" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="394" y="39" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="223" y="39" width="21" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="244" y="39" width="6" height="3" fill="#eea66f" fill-opacity="1"/>
<rect x="226" y="42" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="259" y="42" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="265" y="42" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="274" y="42" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="298" y="42" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="304" y="42" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="373" y="42" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="382" y="42" width="9" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="223" y="42" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="229" y="42" width="18" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="256" y="42" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="247" y="42" width="9" height="3" fill="#eea66f" fill-opacity="1"/>
<rect x="220" y="45" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="229" y="45" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="238" y="45" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="256" y="45" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="268" y="45" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="277" y="45" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="286" y="45" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="298" y="45" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="310" y="45" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="316" y="45" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="325" y="45" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="340" y="45" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="352" y="45" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="364" y="45" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="376" y="45" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="382" y="45" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="223" y="45" width="6" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="232" y="45" width="6" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="241" y="45" width="12" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="253" y="45" width="3" height="3" fill="#eea66f" fill-opacity="1"/>
<rect x="223" y="48" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="229" y="48" width="15" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="259" y="48" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="265" y="48" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="271" y="48" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="280" y="48" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="289" y="48" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="334" y="48" width="9" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="349" y="48" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="367" y="48" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="376" y="48" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="394" y="48" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="226" y="48" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="244" y="48" width="9" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="256" y="48" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="253" y="48" width="3" height="3" fill="#eea66f" fill-opacity="1"/>
<rect x="226" y="51" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="238" y="51" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="244" y="51" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="250" y="51" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="256" y="51" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="265" y="51" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="295" y="51" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="304" y="51" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="322" y="51" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="352" y="51" width="9" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="364" y="51" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="385" y="51" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="247" y="51" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="253" y="51" width="3" height="3" fill="#eea66f" fill-opacity="1"/>
<rect x="223" y="54" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="232" y="54" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="241" y="54" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="271" y="54" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="289" y="54" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="319" y="54" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="325" y="54" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="334" y="54" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="352" y="54" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="358" y="54" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="364" y="54" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="373" y="54" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="388" y="54" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="397" y="54" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="247" y="54" width="6" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="253" y="54" width="18" height="3" fill="#eea66f" fill-opacity="1"/>
<rect x="220" y="57" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="232" y="57" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="244" y="57" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="253" y="57" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="289" y="57" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="304" y="57" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="313" y="57" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="343" y="57" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="361" y="57" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="367" y="57" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="247" y="57" width="6" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="256" y="57" width="12" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="268" y="57" width="21" height="3" fill="#eea66f" fill-opacity="1"/>
<rect x="220" y="60" width="9" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="235" y="60" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="247" y="60" width="9" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="259" y="60" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="292" y="60" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="301" y="60" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="313" y="60" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="319" y="60" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="337" y="60" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="355" y="60" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="373" y="60" width="9" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="256" y="60" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="265" y="60" width="21" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="286" y="60" width="6" height="3" fill="#eea66f" fill-opacity="1"/>
<rect x="226" y="63" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="232" y="63" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="244" y="63" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="256" y="63" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="271" y="63" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="277" y="63" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="298" y="63" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="313" y="63" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="334" y="63" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="349" y="63" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="361" y="63" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="373" y="63" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="391" y="63" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="265" y="63" width="6" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="274" y="63" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="280" y="63" width="9" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="292" y="63" width="6" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="289" y="63" width="3" height="3" fill="#eea66f" fill-opacity="1"/>
<rect x="226" y="66" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="232" y="66" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="238" y="66" width="9" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="268" y="66" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="277" y="66" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="292" y="66" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="307" y="66" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="313" y="66" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="328" y="66" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="340" y="66" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="349" y="66" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="361" y="66" width="9" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="265" y="66" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="274" y="66" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="280" y="66" width="9" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="289" y="66" width="3" height="3" fill="#eea66f" fill-opacity="1"/>
<rect x="226" y="69" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="241" y="69" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="271" y="69" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="301" y="69" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="310" y="69" width="9" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="337" y="69" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="352" y="69" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="373" y="69" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="391" y="69" width="9" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="265" y="69" width="6" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="274" y="69" width="15" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="289" y="69" width="12" height="3" fill="#eea66f" fill-opacity="1"/>
<rect x="220" y="72" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="241" y="72" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="253" y="72" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="268" y="72" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="274" y="72" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="307" y="72" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="316" y="72" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="322" y="72" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="337" y="72" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="349" y="72" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="355" y="72" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="364" y="72" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="379" y="72" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="265" y="72" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="280" y="72" width="18" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="298" y="72" width="9" height="3" fill="#eea66f" fill-opacity="1"/>
<rect x="241" y="75" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="247" y="75" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="271" y="75" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="286" y="75" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="298" y="75" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="310" y="75" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="322" y="75" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="337" y="75" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="355" y="75" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="361" y="75" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="373" y="75" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="388" y="75" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="265" y="75" width="6" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="280" y="75" width="6" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="289" y="75" width="9" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="301" y="75" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="304" y="75" width="6" height="3" fill="#eea66f" fill-opacity="1"/>
<rect x="220" y="78" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="229" y="78" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="235" y="78" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="268" y="78" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="277" y="78" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="289" y="78" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="295" y="78" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="304" y="78" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="313" y="78" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="319" y="78" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="331" y="78" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="343" y="78" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="358" y="78" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="373" y="78" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="382" y="78" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="391" y="78" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="265" y="78" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="280" y="78" width="9" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="292" y="78" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="301" y="78" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="307" y="78" width="6" height="3" fill="#eea66f" fill-opacity="1"/>
<rect x="223" y="81" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="232" y="81" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="244" y="81" width="9" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="262" y="81" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="268" y="81" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="292" y="81" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="325" y="81" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="331" y="81" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="355" y="81" width="9" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="376" y="81" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="385" y="81" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="394" y="81" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="265" y="81" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="280" y="81" width="12" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="301" y="81" width="9" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="316" y="81" width="9" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="310" y="81" width="6" height="3" fill="#eea66f" fill-opacity="1"/>
<rect x="220" y="84" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="229" y="84" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="238" y="84" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="244" y="84" width="9" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="268" y="84" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="292" y="84" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="298" y="84" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="307" y="84" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="316" y="84" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="325" y="84" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="343" y="84" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="352" y="84" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="364" y="84" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="382" y="84" width="12" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="265" y="84" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="280" y="84" width="12" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="301" y="84" width="6" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="319" y="84" width="6" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="313" y="84" width="3" height="3" fill="#eea66f" fill-opacity="1"/>
<rect x="253" y="87" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="259" y="87" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="265" y="87" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="286" y="87" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="328" y="87" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="334" y="87" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="340" y="87" width="9" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="355" y="87" width="9" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="376" y="87" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="394" y="87" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="280" y="87" width="6" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="289" y="87" width="24" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="316" y="87" width="12" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="313" y="87" width="3" height="3" fill="#eea66f" fill-opacity="1"/>
<rect x="226" y="90" width="12" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="256" y="90" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="265" y="90" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="274" y="90" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="304" y="90" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="325" y="90" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="331" y="90" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="337" y="90" width="9" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="352" y="90" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="364" y="90" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="385" y="90" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="394" y="90" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="280" y="90" width="24" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="307" y="90" width="6" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="316" y="90" width="9" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="313" y="90" width="3" height="3" fill="#eea66f" fill-opacity="1"/>
<rect x="220" y="93" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="247" y="93" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="253" y="93" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="274" y="93" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="298" y="93" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="310" y="93" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="322" y="93" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="331" y="93" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="346" y="93" width="9" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="361" y="93" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="367" y="93" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="376" y="93" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="382" y="93" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="280" y="93" width="18" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="301" y="93" width="9" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="316" y="93" width="6" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="313" y="93" width="3" height="3" fill="#eea66f" fill-opacity="1"/>
<rect x="220" y="96" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="226" y="96" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="235" y="96" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="256" y="96" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="283" y="96" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="316" y="96" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="352" y="96" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="370" y="96" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="376" y="96" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="388" y="96" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="280" y="96" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="286" y="96" width="27" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="319" y="96" width="33" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="313" y="96" width="3" height="3" fill="#eea66f" fill-opacity="1"/>
<rect x="238" y="99" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="250" y="99" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="259" y="99" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="268" y="99" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="286" y="99" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="298" y="99" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="307" y="99" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="328" y="99" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="355" y="99" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="379" y="99" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="391" y="99" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="280" y="99" width="6" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="289" y="99" width="9" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="301" y="99" width="6" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="316" y="99" width="12" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="331" y="99" width="24" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="313" y="99" width="3" height="3" fill="#eea66f" fill-opacity="1"/>
<rect x="238" y="102" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="250" y="102" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="259" y="102" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="274" y="102" width="9" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="289" y="102" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="298" y="102" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="322" y="102" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="346" y="102" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="355" y="102" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="361" y="102" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="376" y="102" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="283" y="102" width="6" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="292" y="102" width="6" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="301" y="102" width="12" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="316" y="102" width="6" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="325" y="102" width="21" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="352" y="102" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="313" y="102" width="3" height="3" fill="#eea66f" fill-opacity="1"/>
<rect x="223" y="105" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="232" y="105" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="259" y="105" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="286" y="105" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="346" y="105" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="358" y="105" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="364" y="105" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="283" y="105" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="292" y="105" width="21" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="316" y="105" width="30" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="352" y="105" width="6" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="313" y="105" width="3" height="3" fill="#eea66f" fill-opacity="1"/>
<rect x="223" y="108" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="235" y="108" width="9" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="286" y="108" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="292" y="108" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="310" y="108" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="331" y="108" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="337" y="108" width="12" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="352" y="108" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="358" y="108" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="364" y="108" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="373" y="108" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="379" y="108" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="397" y="108" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="283" y="108" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="298" y="108" width="12" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="316" y="108" width="15" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="334" y="108" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="355" y="108" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="313" y="108" width="3" height="3" fill="#eea66f" fill-opacity="1"/>
<rect x="241" y="111" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="253" y="111" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="262" y="111" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="271" y="111" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="286" y="111" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="322" y="111" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="376" y="111" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="394" y="111" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="283" y="111" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="298" y="111" width="15" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="316" y="111" width="6" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="325" y="111" width="51" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="313" y="111" width="3" height="3" fill="#eea66f" fill-opacity="1"/>
<rect x="247" y="114" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="256" y="114" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="265" y="114" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="277" y="114" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="292" y="114" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="301" y="114" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="322" y="114" width="9" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="346" y="114" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="358" y="114" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="367" y="114" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="379" y="114" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="283" y="114" width="9" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="298" y="114" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="304" y="114" width="9" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="316" y="114" width="6" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="331" y="114" width="15" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="352" y="114" width="6" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="361" y="114" width="6" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="370" y="114" width="9" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="313" y="114" width="3" height="3" fill="#eea66f" fill-opacity="1"/>
<rect x="241" y="117" width="15" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="271" y="117" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="280" y="117" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="307" y="117" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="316" y="117" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="337" y="117" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="352" y="117" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="376" y="117" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="385" y="117" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="391" y="117" width="9" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="283" y="117" width="24" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="310" y="117" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="331" y="117" width="6" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="340" y="117" width="12" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="361" y="117" width="15" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="313" y="117" width="3" height="3" fill="#eea66f" fill-opacity="1"/>
<rect x="223" y="120" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="229" y="120" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="238" y="120" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="250" y="120" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="256" y="120" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="283" y="120" width="9" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="298" y="120" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="310" y="120" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="322" y="120" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="334" y="120" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="340" y="120" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="349" y="120" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="361" y="120" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="376" y="120" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="385" y="120" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="397" y="120" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="292" y="120" width="6" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="301" y="120" width="9" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="331" y="120" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="343" y="120" width="6" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="364" y="120" width="12" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="313" y="120" width="9" height="3" fill="#eea66f" fill-opacity="1"/>
<rect x="226" y="123" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="238" y="123" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="247" y="123" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="253" y="123" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="265" y="123" width="9" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="283" y="123" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="298" y="123" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="313" y="123" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="331" y="123" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="346" y="123" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="355" y="123" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="364" y="123" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="376" y="123" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="292" y="123" width="6" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="304" y="123" width="9" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="316" y="123" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="328" y="123" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="343" y="123" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="367" y="123" width="9" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="319" y="123" width="9" height="3" fill="#eea66f" fill-opacity="1"/>
<rect x="220" y="126" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="241" y="126" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="247" y="126" width="9" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="262" y="126" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="271" y="126" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="289" y="126" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="298" y="126" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="313" y="126" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="319" y="126" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="328" y="126" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="337" y="126" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="370" y="126" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="394" y="126" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="292" y="126" width="6" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="304" y="126" width="9" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="316" y="126" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="322" y="126" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="343" y="126" width="27" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="373" y="126" width="21" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="325" y="126" width="3" height="3" fill="#eea66f" fill-opacity="1"/>
<rect x="226" y="129" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="241" y="129" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="250" y="129" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="277" y="129" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="322" y="129" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="343" y="129" width="9" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="361" y="129" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="382" y="129" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="292" y="129" width="30" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="352" y="129" width="9" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="367" y="129" width="15" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="385" y="129" width="15" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="325" y="129" width="18" height="3" fill="#eea66f" fill-opacity="1"/>
<rect x="223" y="132" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="238" y="132" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="247" y="132" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="268" y="132" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="280" y="132" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="292" y="132" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="304" y="132" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="349" y="132" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="355" y="132" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="298" y="132" width="6" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="307" y="132" width="33" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="352" y="132" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="358" y="132" width="42" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="340" y="132" width="9" height="3" fill="#eea66f" fill-opacity="1"/>
<rect x="244" y="135" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="250" y="135" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="259" y="135" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="277" y="135" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="286" y="135" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="340" y="135" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="382" y="135" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="397" y="135" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="298" y="135" width="42" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="343" y="135" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="352" y="135" width="30" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="385" y="135" width="12" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="346" y="135" width="6" height="3" fill="#eea66f" fill-opacity="1"/>
<rect x="238" y="138" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="250" y="138" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="271" y="138" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="286" y="138" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="301" y="138" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="328" y="138" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="337" y="138" width="9" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="358" y="138" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="376" y="138" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="382" y="138" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="298" y="138" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="304" y="138" width="24" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="334" y="138" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="346" y="138" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="352" y="138" width="6" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="364" y="138" width="12" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="379" y="138" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="385" y="138" width="15" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="349" y="138" width="3" height="3" fill="#eea66f" fill-opacity="1"/>
<rect x="220" y="141" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="238" y="141" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="274" y="141" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="283" y="141" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="298" y="141" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="307" y="141" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="319" y="141" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="331" y="141" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="343" y="141" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="352" y="141" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="364" y="141" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="370" y="141" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="379" y="141" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="391" y="141" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="304" y="141" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="310" y="141" width="9" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="322" y="141" width="9" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="367" y="141" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="373" y="141" width="6" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="385" y="141" width="6" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="394" y="141" width="6" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="349" y="141" width="3" height="3" fill="#eea66f" fill-opacity="1"/>
<rect x="226" y="144" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="235" y="144" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="241" y="144" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="259" y="144" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="265" y="144" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="271" y="144" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="301" y="144" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="316" y="144" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="331" y="144" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="337" y="144" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="364" y="144" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="370" y="144" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="391" y="144" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="310" y="144" width="6" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="322" y="144" width="9" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="361" y="144" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="367" y="144" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="373" y="144" width="18" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="394" y="144" width="6" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="349" y="144" width="12" height="3" fill="#eea66f" fill-opacity="1"/>
<rect x="223" y="147" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="238" y="147" width="12" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="256" y="147" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="265" y="147" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="289" y="147" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="301" y="147" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="310" y="147" width="9" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="322" y="147" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="331" y="147" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="349" y="147" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="376" y="147" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="391" y="147" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="397" y="147" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="325" y="147" width="6" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="352" y="147" width="6" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="361" y="147" width="15" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="379" y="147" width="12" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="394" y="147" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="358" y="147" width="3" height="3" fill="#eea66f" fill-opacity="1"/>
<rect x="241" y="150" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="253" y="150" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="259" y="150" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="268" y="150" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="292" y="150" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="310" y="150" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="328" y="150" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="337" y="150" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="346" y="150" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="355" y="150" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="367" y="150" width="9" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="382" y="150" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="394" y="150" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="325" y="150" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="352" y="150" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="361" y="150" width="6" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="379" y="150" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="385" y="150" width="9" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="358" y="150" width="3" height="3" fill="#eea66f" fill-opacity="1"/>
<rect x="223" y="153" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="229" y="153" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="250" y="153" width="9" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="268" y="153" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="280" y="153" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="295" y="153" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="316" y="153" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="346" y="153" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="355" y="153" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="361" y="153" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="370" y="153" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="379" y="153" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="385" y="153" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="325" y="153" width="21" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="352" y="153" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="364" y="153" width="6" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="388" y="153" width="12" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="358" y="153" width="3" height="3" fill="#eea66f" fill-opacity="1"/>
<rect x="247" y="156" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="262" y="156" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="295" y="156" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="328" y="156" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="340" y="156" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="364" y="156" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="376" y="156" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="385" y="156" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="325" y="156" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="334" y="156" width="6" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="343" y="156" width="15" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="388" y="156" width="12" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="358" y="156" width="6" height="3" fill="#eea66f" fill-opacity="1"/>
<rect x="220" y="159" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="226" y="159" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="235" y="159" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="241" y="159" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="259" y="159" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="268" y="159" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="277" y="159" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="289" y="159" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="295" y="159" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="304" y="159" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="310" y="159" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="340" y="159" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="358" y="159" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="373" y="159" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="379" y="159" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="388" y="159" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="325" y="159" width="15" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="343" y="159" width="15" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="391" y="159" width="9" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="361" y="159" width="12" height="3" fill="#eea66f" fill-opacity="1"/>
<rect x="220" y="162" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="232" y="162" width="9" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="244" y="162" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="259" y="162" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="277" y="162" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="283" y="162" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="295" y="162" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="313" y="162" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="328" y="162" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="334" y="162" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="343" y="162" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="364" y="162" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="373" y="162" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="382" y="162" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="325" y="162" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="331" y="162" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="337" y="162" width="6" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="349" y="162" width="15" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="367" y="162" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="391" y="162" width="9" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="370" y="162" width="3" height="3" fill="#eea66f" fill-opacity="1"/>
<rect x="235" y="165" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="298" y="165" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="316" y="165" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="325" y="165" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="346" y="165" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="376" y="165" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="331" y="165" width="15" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="352" y="165" width="18" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="373" y="165" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="391" y="165" width="9" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="370" y="165" width="3" height="3" fill="#eea66f" fill-opacity="1"/>
<rect x="220" y="168" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="235" y="168" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="247" y="168" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="253" y="168" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="265" y="168" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="277" y="168" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="289" y="168" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="307" y="168" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="328" y="168" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="334" y="168" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="355" y="168" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="367" y="168" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="379" y="168" width="9" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="391" y="168" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="331" y="168" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="337" y="168" width="18" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="358" y="168" width="9" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="373" y="168" width="6" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="394" y="168" width="6" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="370" y="168" width="3" height="3" fill="#eea66f" fill-opacity="1"/>
<rect x="274" y="171" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="295" y="171" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="301" y="171" width="12" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="319" y="171" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="328" y="171" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="340" y="171" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="349" y="171" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="376" y="171" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="382" y="171" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="394" y="171" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="337" y="171" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="346" y="171" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="352" y="171" width="18" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="373" y="171" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="397" y="171" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="370" y="171" width="3" height="3" fill="#eea66f" fill-opacity="1"/>
<rect x="232" y="174" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="244" y="174" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="262" y="174" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="268" y="174" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="298" y="174" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="316" y="174" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="331" y="174" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="343" y="174" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="352" y="174" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="358" y="174" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="364" y="174" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="373" y="174" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="391" y="174" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="337" y="174" width="6" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="355" y="174" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="361" y="174" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="397" y="174" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="370" y="174" width="3" height="3" fill="#eea66f" fill-opacity="1"/>
<rect x="223" y="177" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="229" y="177" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="235" y="177" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="250" y="177" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="256" y="177" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="262" y="177" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="268" y="177" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="277" y="177" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="292" y="177" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="307" y="177" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="313" y="177" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="331" y="177" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="379" y="177" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="385" y="177" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="337" y="177" width="33" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="397" y="177" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="370" y="177" width="9" height="3" fill="#eea66f" fill-opacity="1"/>
<rect x="223" y="180" width="9" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="241" y="180" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="262" y="180" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="280" y="180" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="316" y="180" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="340" y="180" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="361" y="180" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="385" y="180" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="397" y="180" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="337" y="180" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="346" y="180" width="15" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="367" y="180" width="9" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="376" y="180" width="9" height="3" fill="#eea66f" fill-opacity="1"/>
<rect x="220" y="183" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="226" y="183" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="241" y="183" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="265" y="183" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="277" y="183" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="289" y="183" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="298" y="183" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="313" y="183" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="319" y="183" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="328" y="183" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="343" y="183" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="379" y="183" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="397" y="183" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="337" y="183" width="6" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="346" y="183" width="33" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="388" y="183" width="9" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="382" y="183" width="6" height="3" fill="#eea66f" fill-opacity="1"/>
<rect x="238" y="186" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="283" y="186" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="298" y="186" width="9" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="310" y="186" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="322" y="186" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="334" y="186" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="355" y="186" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="364" y="186" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="394" y="186" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="337" y="186" width="18" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="358" y="186" width="6" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="367" y="186" width="18" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="388" y="186" width="6" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="385" y="186" width="3" height="3" fill="#eea66f" fill-opacity="1"/>
<rect x="232" y="189" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="259" y="189" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="268" y="189" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="316" y="189" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="325" y="189" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="331" y="189" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="337" y="189" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="361" y="189" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="367" y="189" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="373" y="189" width="9" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="340" y="189" width="21" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="370" y="189" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="382" y="189" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="388" y="189" width="12" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="385" y="189" width="3" height="3" fill="#eea66f" fill-opacity="1"/>
<rect x="223" y="192" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="232" y="192" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="241" y="192" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="253" y="192" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="265" y="192" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="277" y="192" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="286" y="192" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="292" y="192" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="307" y="192" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="313" y="192" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="343" y="192" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="358" y="192" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="373" y="192" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="379" y="192" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="397" y="192" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="340" y="192" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="346" y="192" width="12" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="370" y="192" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="382" y="192" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="388" y="192" width="9" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="385" y="192" width="3" height="3" fill="#eea66f" fill-opacity="1"/>
<rect x="226" y="195" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="232" y="195" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="241" y="195" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="247" y="195" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="262" y="195" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="268" y="195" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="274" y="195" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="289" y="195" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="310" y="195" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="319" y="195" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="328" y="195" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="334" y="195" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="346" y="195" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="352" y="195" width="9" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="370" y="195" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="388" y="195" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="394" y="195" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="340" y="195" width="6" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="349" y="195" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="382" y="195" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="391" y="195" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="385" y="195" width="3" height="3" fill="#eea66f" fill-opacity="1"/>
<rect x="220" y="198" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="235" y="198" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="241" y="198" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="253" y="198" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="265" y="198" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="289" y="198" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="301" y="198" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="313" y="198" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="319" y="198" width="9" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="358" y="198" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="370" y="198" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="379" y="198" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="391" y="198" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="340" y="198" width="18" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="382" y="198" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="385" y="198" width="6" height="3" fill="#eea66f" fill-opacity="1"/>
<rect x="259" y="201" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="274" y="201" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="283" y="201" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="319" y="201" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="340" y="201" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="346" y="201" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="367" y="201" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="382" y="201" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="343" y="201" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="352" y="201" width="15" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="385" y="201" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="397" y="201" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="388" y="201" width="9" height="3" fill="#eea66f" fill-opacity="1"/>
<rect x="220" y="204" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="226" y="204" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="232" y="204" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="244" y="204" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="271" y="204" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="277" y="204" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="283" y="204" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="304" y="204" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="328" y="204" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="370" y="204" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="397" y="204" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="343" y="204" width="27" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="385" y="204" width="9" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="394" y="204" width="3" height="3" fill="#eea66f" fill-opacity="1"/>
<rect x="223" y="207" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="232" y="207" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="241" y="207" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="295" y="207" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="310" y="207" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="319" y="207" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="325" y="207" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="331" y="207" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="346" y="207" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="355" y="207" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="364" y="207" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="382" y="207" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="343" y="207" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="349" y="207" width="6" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="358" y="207" width="6" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="367" y="207" width="15" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="385" y="207" width="9" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="394" y="207" width="6" height="3" fill="#eea66f" fill-opacity="1"/>
<text x="510" y="20" font-size="13" text-anchor="middle" fill="currentColor">A*, landmarks (ALT): 466 settled</text>
<rect x="420" y="30" width="180" height="180" fill="none" stroke="currentColor" stroke-width="1"/>
<rect x="423" y="30" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="429" y="30" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="438" y="30" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="444" y="30" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="450" y="30" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="462" y="30" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="483" y="30" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="492" y="30" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="504" y="30" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="519" y="30" width="9" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="552" y="30" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="573" y="30" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="582" y="30" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="588" y="30" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="420" y="30" width="3" height="3" fill="#eea66f" fill-opacity="1"/>
<rect x="450" y="33" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="474" y="33" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="480" y="33" width="9" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="492" y="33" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="504" y="33" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="537" y="33" width="12" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="558" y="33" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="585" y="33" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="420" y="33" width="27" height="3" fill="#eea66f" fill-opacity="1"/>
<rect x="426" y="36" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="432" y="36" width="12" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="447" y="36" width="12" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="462" y="36" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="471" y="36" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="483" y="36" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="498" y="36" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="513" y="36" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="525" y="36" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="531" y="36" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="552" y="36" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="567" y="36" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="588" y="36" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="597" y="36" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="420" y="36" width="6" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="429" y="36" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="444" y="36" width="3" height="3" fill="#eea66f" fill-opacity="1"/>
<rect x="420" y="39" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="450" y="39" width="12" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="480" y="39" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="498" y="39" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="525" y="39" width="9" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="540" y="39" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="558" y="39" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="585" y="39" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="594" y="39" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="423" y="39" width="21" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="444" y="39" width="6" height="3" fill="#eea66f" fill-opacity="1"/>
<rect x="426" y="42" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="459" y="42" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="465" y="42" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="474" y="42" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="498" y="42" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="504" y="42" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="573" y="42" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="582" y="42" width="9" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="429" y="42" width="18" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="447" y="42" width="9" height="3" fill="#eea66f" fill-opacity="1"/>
<rect x="420" y="45" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="429" y="45" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="438" y="45" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="456" y="45" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="468" y="45" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="477" y="45" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="486" y="45" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="498" y="45" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="510" y="45" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="516" y="45" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="525" y="45" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="540" y="45" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="552" y="45" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="564" y="45" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="576" y="45" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="582" y="45" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="441" y="45" width="12" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="453" y="45" width="3" height="3" fill="#eea66f" fill-opacity="1"/>
<rect x="423" y="48" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="429" y="48" width="15" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="459" y="48" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="465" y="48" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="471" y="48" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="480" y="48" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="489" y="48" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="534" y="48" width="9" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="549" y="48" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="567" y="48" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="576" y="48" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="594" y="48" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="444" y="48" width="9" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="453" y="48" width="3" height="3" fill="#eea66f" fill-opacity="1"/>
<rect x="426" y="51" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="438" y="51" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="444" y="51" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="450" y="51" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="456" y="51" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="465" y="51" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="495" y="51" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="504" y="51" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="522" y="51" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="552" y="51" width="9" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="564" y="51" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="585" y="51" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="447" y="51" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="453" y="51" width="3" height="3" fill="#eea66f" fill-opacity="1"/>
<rect x="423" y="54" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="432" y="54" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="441" y="54" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="471" y="54" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="489" y="54" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="519" y="54" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="525" y="54" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="534" y="54" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="552" y="54" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="558" y="54" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="564" y="54" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="573" y="54" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="588" y="54" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="597" y="54" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="447" y="54" width="6" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="453" y="54" width="18" height="3" fill="#eea66f" fill-opacity="1"/>
<rect x="420" y="57" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="432" y="57" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="444" y="57" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="453" y="57" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="489" y="57" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="504" y="57" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="513" y="57" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="543" y="57" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="561" y="57" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="567" y="57" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="456" y="57" width="12" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="468" y="57" width="21" height="3" fill="#eea66f" fill-opacity="1"/>
<rect x="420" y="60" width="9" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="435" y="60" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="447" y="60" width="9" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="459" y="60" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="492" y="60" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="501" y="60" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="513" y="60" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="519" y="60" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="537" y="60" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="555" y="60" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="573" y="60" width="9" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="465" y="60" width="21" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="486" y="60" width="6" height="3" fill="#eea66f" fill-opacity="1"/>
<rect x="426" y="63" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="432" y="63" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="444" y="63" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="456" y="63" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="471" y="63" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="477" y="63" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="498" y="63" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="513" y="63" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="534" y="63" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="549" y="63" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="561" y="63" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="573" y="63" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="591" y="63" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="474" y="63" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="480" y="63" width="9" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="489" y="63" width="3" height="3" fill="#eea66f" fill-opacity="1"/>
<rect x="426" y="66" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="432" y="66" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="438" y="66" width="9" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="468" y="66" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="477" y="66" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="492" y="66" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="507" y="66" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="513" y="66" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="528" y="66" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="540" y="66" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="549" y="66" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="561" y="66" width="9" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="474" y="66" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="480" y="66" width="9" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="489" y="66" width="3" height="3" fill="#eea66f" fill-opacity="1"/>
<rect x="426" y="69" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="441" y="69" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="471" y="69" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="501" y="69" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="510" y="69" width="9" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="537" y="69" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="552" y="69" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="573" y="69" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="591" y="69" width="9" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="474" y="69" width="15" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="489" y="69" width="12" height="3" fill="#eea66f" fill-opacity="1"/>
<rect x="420" y="72" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="441" y="72" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="453" y="72" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="468" y="72" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="474" y="72" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="507" y="72" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="516" y="72" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="522" y="72" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="537" y="72" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="549" y="72" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="555" y="72" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="564" y="72" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="579" y="72" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="480" y="72" width="18" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="498" y="72" width="9" height="3" fill="#eea66f" fill-opacity="1"/>
<rect x="441" y="75" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="447" y="75" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="471" y="75" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="486" y="75" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="498" y="75" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="510" y="75" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="522" y="75" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="537" y="75" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="555" y="75" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="561" y="75" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="573" y="75" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="588" y="75" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="480" y="75" width="6" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="501" y="75" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="504" y="75" width="6" height="3" fill="#eea66f" fill-opacity="1"/>
<rect x="420" y="78" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="429" y="78" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="435" y="78" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="468" y="78" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="477" y="78" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="489" y="78" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="495" y="78" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="504" y="78" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="513" y="78" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="519" y="78" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="531" y="78" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="543" y="78" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="558" y="78" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="573" y="78" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="582" y="78" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="591" y="78" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="480" y="78" width="9" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="501" y="78" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="507" y="78" width="6" height="3" fill="#eea66f" fill-opacity="1"/>
<rect x="423" y="81" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="432" y="81" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="444" y="81" width="9" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="462" y="81" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="468" y="81" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="492" y="81" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="525" y="81" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="531" y="81" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="555" y="81" width="9" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="576" y="81" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="585" y="81" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="594" y="81" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="480" y="81" width="12" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="501" y="81" width="9" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="510" y="81" width="6" height="3" fill="#eea66f" fill-opacity="1"/>
<rect x="420" y="84" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="429" y="84" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="438" y="84" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="444" y="84" width="9" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="468" y="84" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="492" y="84" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="498" y="84" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="507" y="84" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="516" y="84" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="525" y="84" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="543" y="84" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="552" y="84" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="564" y="84" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="582" y="84" width="12" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="480" y="84" width="12" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="501" y="84" width="6" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="513" y="84" width="3" height="3" fill="#eea66f" fill-opacity="1"/>
<rect x="453" y="87" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="459" y="87" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="465" y="87" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="486" y="87" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="528" y="87" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="534" y="87" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="540" y="87" width="9" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="555" y="87" width="9" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="576" y="87" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="594" y="87" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="480" y="87" width="6" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="489" y="87" width="24" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="513" y="87" width="3" height="3" fill="#eea66f" fill-opacity="1"/>
<rect x="426" y="90" width="12" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="456" y="90" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="465" y="90" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="474" y="90" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="504" y="90" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="525" y="90" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="531" y="90" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="537" y="90" width="9" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="552" y="90" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="564" y="90" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="585" y="90" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="594" y="90" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="480" y="90" width="24" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="507" y="90" width="6" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="513" y="90" width="3" height="3" fill="#eea66f" fill-opacity="1"/>
<rect x="420" y="93" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="447" y="93" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="453" y="93" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="474" y="93" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="498" y="93" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="510" y="93" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="522" y="93" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="531" y="93" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="546" y="93" width="9" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="561" y="93" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="567" y="93" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="576" y="93" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="582" y="93" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="480" y="93" width="18" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="501" y="93" width="9" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="513" y="93" width="3" height="3" fill="#eea66f" fill-opacity="1"/>
<rect x="420" y="96" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="426" y="96" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="435" y="96" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="456" y="96" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="483" y="96" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="516" y="96" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="552" y="96" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="570" y="96" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="576" y="96" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="588" y="96" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="480" y="96" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="486" y="96" width="27" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="513" y="96" width="3" height="3" fill="#eea66f" fill-opacity="1"/>
<rect x="438" y="99" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="450" y="99" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="459" y="99" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="468" y="99" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="486" y="99" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="498" y="99" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="507" y="99" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="528" y="99" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="555" y="99" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="579" y="99" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="591" y="99" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="480" y="99" width="6" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="489" y="99" width="9" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="501" y="99" width="6" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="513" y="99" width="3" height="3" fill="#eea66f" fill-opacity="1"/>
<rect x="438" y="102" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="450" y="102" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="459" y="102" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="474" y="102" width="9" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="489" y="102" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="498" y="102" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="522" y="102" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="546" y="102" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="555" y="102" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="561" y="102" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="576" y="102" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="483" y="102" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="492" y="102" width="6" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="501" y="102" width="12" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="513" y="102" width="3" height="3" fill="#eea66f" fill-opacity="1"/>
<rect x="423" y="105" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="432" y="105" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="459" y="105" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="486" y="105" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="546" y="105" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="558" y="105" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="564" y="105" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="483" y="105" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="492" y="105" width="21" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="513" y="105" width="3" height="3" fill="#eea66f" fill-opacity="1"/>
<rect x="423" y="108" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="435" y="108" width="9" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="486" y="108" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="492" y="108" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="510" y="108" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="531" y="108" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="537" y="108" width="12" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="552" y="108" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="558" y="108" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="564" y="108" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="573" y="108" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="579" y="108" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="597" y="108" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="483" y="108" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="498" y="108" width="12" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="513" y="108" width="3" height="3" fill="#eea66f" fill-opacity="1"/>
<rect x="441" y="111" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="453" y="111" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="462" y="111" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="471" y="111" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="486" y="111" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="522" y="111" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="576" y="111" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="594" y="111" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="483" y="111" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="498" y="111" width="15" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="513" y="111" width="3" height="3" fill="#eea66f" fill-opacity="1"/>
<rect x="447" y="114" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="456" y="114" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="465" y="114" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="477" y="114" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="492" y="114" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="501" y="114" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="522" y="114" width="9" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="546" y="114" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="558" y="114" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="567" y="114" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="579" y="114" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="483" y="114" width="9" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="498" y="114" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="504" y="114" width="9" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="513" y="114" width="3" height="3" fill="#eea66f" fill-opacity="1"/>
<rect x="441" y="117" width="15" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="471" y="117" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="480" y="117" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="507" y="117" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="516" y="117" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="537" y="117" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="552" y="117" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="576" y="117" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="585" y="117" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="591" y="117" width="9" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="483" y="117" width="24" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="510" y="117" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="513" y="117" width="3" height="3" fill="#eea66f" fill-opacity="1"/>
<rect x="423" y="120" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="429" y="120" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="438" y="120" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="450" y="120" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="456" y="120" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="483" y="120" width="9" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="498" y="120" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="510" y="120" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="522" y="120" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="534" y="120" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="540" y="120" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="549" y="120" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="561" y="120" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="576" y="120" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="585" y="120" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="597" y="120" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="492" y="120" width="6" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="501" y="120" width="9" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="513" y="120" width="9" height="3" fill="#eea66f" fill-opacity="1"/>
<rect x="426" y="123" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="438" y="123" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="447" y="123" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="453" y="123" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="465" y="123" width="9" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="483" y="123" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="498" y="123" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="513" y="123" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="531" y="123" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="546" y="123" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="555" y="123" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="564" y="123" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="576" y="123" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="492" y="123" width="6" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="504" y="123" width="9" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="516" y="123" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="519" y="123" width="9" height="3" fill="#eea66f" fill-opacity="1"/>
<rect x="420" y="126" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="441" y="126" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="447" y="126" width="9" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="462" y="126" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="471" y="126" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="489" y="126" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="498" y="126" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="513" y="126" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="519" y="126" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="528" y="126" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="537" y="126" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="570" y="126" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="594" y="126" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="492" y="126" width="6" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="504" y="126" width="9" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="516" y="126" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="522" y="126" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="525" y="126" width="3" height="3" fill="#eea66f" fill-opacity="1"/>
<rect x="426" y="129" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="441" y="129" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="450" y="129" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="477" y="129" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="522" y="129" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="543" y="129" width="9" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="561" y="129" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="582" y="129" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="492" y="129" width="30" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="525" y="129" width="18" height="3" fill="#eea66f" fill-opacity="1"/>
<rect x="423" y="132" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="438" y="132" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="447" y="132" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="468" y="132" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="480" y="132" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="492" y="132" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="504" y="132" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="549" y="132" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="555" y="132" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="498" y="132" width="6" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="507" y="132" width="33" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="540" y="132" width="9" height="3" fill="#eea66f" fill-opacity="1"/>
<rect x="444" y="135" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="450" y="135" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="459" y="135" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="477" y="135" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="486" y="135" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="540" y="135" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="582" y="135" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="597" y="135" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="498" y="135" width="30" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="543" y="135" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="546" y="135" width="6" height="3" fill="#eea66f" fill-opacity="1"/>
<rect x="438" y="138" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="450" y="138" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="471" y="138" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="486" y="138" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="501" y="138" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="528" y="138" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="537" y="138" width="9" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="558" y="138" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="576" y="138" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="582" y="138" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="504" y="138" width="24" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="546" y="138" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="549" y="138" width="3" height="3" fill="#eea66f" fill-opacity="1"/>
<rect x="420" y="141" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="438" y="141" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="474" y="141" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="483" y="141" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="498" y="141" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="507" y="141" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="519" y="141" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="531" y="141" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="543" y="141" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="552" y="141" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="564" y="141" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="570" y="141" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="579" y="141" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="591" y="141" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="522" y="141" width="6" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="549" y="141" width="3" height="3" fill="#eea66f" fill-opacity="1"/>
<rect x="426" y="144" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="435" y="144" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="441" y="144" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="459" y="144" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="465" y="144" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="471" y="144" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="501" y="144" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="516" y="144" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="531" y="144" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="537" y="144" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="564" y="144" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="570" y="144" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="591" y="144" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="522" y="144" width="6" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="549" y="144" width="12" height="3" fill="#eea66f" fill-opacity="1"/>
<rect x="423" y="147" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="438" y="147" width="12" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="456" y="147" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="465" y="147" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="489" y="147" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="501" y="147" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="510" y="147" width="9" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="522" y="147" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="531" y="147" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="549" y="147" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="576" y="147" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="591" y="147" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="597" y="147" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="525" y="147" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="552" y="147" width="6" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="558" y="147" width="3" height="3" fill="#eea66f" fill-opacity="1"/>
<rect x="441" y="150" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="453" y="150" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="459" y="150" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="468" y="150" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="492" y="150" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="510" y="150" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="528" y="150" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="537" y="150" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="546" y="150" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="555" y="150" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="567" y="150" width="9" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="582" y="150" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="594" y="150" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="525" y="150" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="552" y="150" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="558" y="150" width="3" height="3" fill="#eea66f" fill-opacity="1"/>
<rect x="423" y="153" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="429" y="153" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="450" y="153" width="9" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="468" y="153" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="480" y="153" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="495" y="153" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="516" y="153" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="546" y="153" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="555" y="153" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="561" y="153" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="570" y="153" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="579" y="153" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="585" y="153" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="525" y="153" width="21" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="552" y="153" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="558" y="153" width="3" height="3" fill="#eea66f" fill-opacity="1"/>
<rect x="447" y="156" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="462" y="156" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="495" y="156" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="528" y="156" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="540" y="156" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="564" y="156" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="576" y="156" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="585" y="156" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="525" y="156" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="534" y="156" width="6" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="543" y="156" width="15" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="558" y="156" width="6" height="3" fill="#eea66f" fill-opacity="1"/>
<rect x="420" y="159" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="426" y="159" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="435" y="159" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="441" y="159" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="459" y="159" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="468" y="159" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="477" y="159" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="489" y="159" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="495" y="159" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="504" y="159" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="510" y="159" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="540" y="159" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="558" y="159" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="573" y="159" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="579" y="159" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="588" y="159" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="525" y="159" width="15" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="543" y="159" width="15" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="561" y="159" width="12" height="3" fill="#eea66f" fill-opacity="1"/>
<rect x="420" y="162" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="432" y="162" width="9" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="444" y="162" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="459" y="162" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="477" y="162" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="483" y="162" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="495" y="162" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="513" y="162" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="528" y="162" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="534" y="162" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="543" y="162" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="564" y="162" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="573" y="162" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="582" y="162" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="531" y="162" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="537" y="162" width="6" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="549" y="162" width="15" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="567" y="162" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="570" y="162" width="3" height="3" fill="#eea66f" fill-opacity="1"/>
<rect x="435" y="165" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="498" y="165" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="516" y="165" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="525" y="165" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="546" y="165" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="576" y="165" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="531" y="165" width="15" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="552" y="165" width="18" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="570" y="165" width="3" height="3" fill="#eea66f" fill-opacity="1"/>
<rect x="420" y="168" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="435" y="168" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="447" y="168" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="453" y="168" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="465" y="168" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="477" y="168" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="489" y="168" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="507" y="168" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="528" y="168" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="534" y="168" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="555" y="168" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="567" y="168" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="579" y="168" width="9" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="591" y="168" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="537" y="168" width="18" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="558" y="168" width="9" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="570" y="168" width="3" height="3" fill="#eea66f" fill-opacity="1"/>
<rect x="474" y="171" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="495" y="171" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="501" y="171" width="12" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="519" y="171" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="528" y="171" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="540" y="171" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="549" y="171" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="576" y="171" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="582" y="171" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="594" y="171" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="537" y="171" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="552" y="171" width="18" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="570" y="171" width="3" height="3" fill="#eea66f" fill-opacity="1"/>
<rect x="432" y="174" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="444" y="174" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="462" y="174" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="468" y="174" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="498" y="174" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="516" y="174" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="531" y="174" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="543" y="174" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="552" y="174" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="558" y="174" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="564" y="174" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="573" y="174" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="591" y="174" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="537" y="174" width="6" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="555" y="174" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="561" y="174" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="570" y="174" width="3" height="3" fill="#eea66f" fill-opacity="1"/>
<rect x="423" y="177" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="429" y="177" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="435" y="177" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="450" y="177" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="456" y="177" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="462" y="177" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="468" y="177" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="477" y="177" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="492" y="177" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="507" y="177" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="513" y="177" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="531" y="177" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="579" y="177" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="585" y="177" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="537" y="177" width="33" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="570" y="177" width="9" height="3" fill="#eea66f" fill-opacity="1"/>
<rect x="423" y="180" width="9" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="441" y="180" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="462" y="180" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="480" y="180" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="516" y="180" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="540" y="180" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="561" y="180" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="585" y="180" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="597" y="180" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="546" y="180" width="15" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="567" y="180" width="9" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="576" y="180" width="9" height="3" fill="#eea66f" fill-opacity="1"/>
<rect x="420" y="183" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="426" y="183" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="441" y="183" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="465" y="183" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="477" y="183" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="489" y="183" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="498" y="183" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="513" y="183" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="519" y="183" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="528" y="183" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="543" y="183" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="579" y="183" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="597" y="183" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="546" y="183" width="33" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="582" y="183" width="6" height="3" fill="#eea66f" fill-opacity="1"/>
<rect x="438" y="186" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="483" y="186" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="498" y="186" width="9" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="510" y="186" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="522" y="186" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="534" y="186" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="555" y="186" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="564" y="186" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="594" y="186" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="567" y="186" width="18" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="585" y="186" width="3" height="3" fill="#eea66f" fill-opacity="1"/>
<rect x="432" y="189" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="459" y="189" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="468" y="189" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="516" y="189" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="525" y="189" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="531" y="189" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="537" y="189" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="561" y="189" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="567" y="189" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="573" y="189" width="9" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="582" y="189" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="585" y="189" width="3" height="3" fill="#eea66f" fill-opacity="1"/>
<rect x="423" y="192" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="432" y="192" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="441" y="192" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="453" y="192" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="465" y="192" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="477" y="192" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="486" y="192" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="492" y="192" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="507" y="192" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="513" y="192" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="543" y="192" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="558" y="192" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="573" y="192" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="579" y="192" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="597" y="192" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="582" y="192" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="585" y="192" width="3" height="3" fill="#eea66f" fill-opacity="1"/>
<rect x="426" y="195" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="432" y="195" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="441" y="195" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="447" y="195" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="462" y="195" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="468" y="195" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="474" y="195" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="489" y="195" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="510" y="195" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="519" y="195" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="528" y="195" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="534" y="195" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="546" y="195" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="552" y="195" width="9" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="570" y="195" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="588" y="195" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="594" y="195" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="582" y="195" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="585" y="195" width="3" height="3" fill="#eea66f" fill-opacity="1"/>
<rect x="420" y="198" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="435" y="198" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="441" y="198" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="453" y="198" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="465" y="198" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="489" y="198" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="501" y="198" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="513" y="198" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="519" y="198" width="9" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="558" y="198" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="570" y="198" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="579" y="198" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="591" y="198" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="582" y="198" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="585" y="198" width="6" height="3" fill="#eea66f" fill-opacity="1"/>
<rect x="459" y="201" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="474" y="201" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="483" y="201" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="519" y="201" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="540" y="201" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="546" y="201" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="567" y="201" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="582" y="201" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="585" y="201" width="3" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="588" y="201" width="9" height="3" fill="#eea66f" fill-opacity="1"/>
<rect x="420" y="204" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="426" y="204" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="432" y="204" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="444" y="204" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="471" y="204" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="477" y="204" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="483" y="204" width="6" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="504" y="204" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="528" y="204" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="570" y="204" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="597" y="204" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="585" y="204" width="9" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="594" y="204" width="3" height="3" fill="#eea66f" fill-opacity="1"/>
<rect x="423" y="207" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="432" y="207" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="441" y="207" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="495" y="207" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="510" y="207" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="519" y="207" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="525" y="207" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="531" y="207" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="546" y="207" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="555" y="207" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="564" y="207" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="582" y="207" width="3" height="3" fill="currentColor" fill-opacity="0.55"/>
<rect x="585" y="207" width="9" height="3" fill="#9cc9ea" fill-opacity="0.7"/>
<rect x="594" y="207" width="6" height="3" fill="#eea66f" fill-opacity="1"/>
<text x="310" y="232" font-size="12" text-anchor="middle" fill="currentColor">grey: walls   blue: settled before reaching the far corner   orange: a shortest path (118 steps)</text>
</svg>
<figcaption>Figure 16.4. The program's 60 × 60 grid, start at the top left, goal at the bottom right. Dijkstra settles almost every open cell before reaching the goal. A* with the Manhattan distance as its guess settles fewer, and A* with landmark distances fewer still. All three find a path of the same length, 118.</figcaption>
</figure>

On the Mars map, the straight great-circle distance to Gale crater is an admissible heuristic (every road is a
great-circle arc, at least as long as the direct arc between its ends). From Erebus Montes, Dijkstra settles
Erebus Montes, Elysium Mons, Utopia Planitia, Olympus Mons and then Gale crater; A\* with the great-circle guess
settles only Erebus Montes, Elysium Mons and Gale crater.

### Bidirectional search

Another way to save work: search forwards from $s$ and backwards from $t$ (along reversed edges) at the same time,
and stop when the two meet. On a map, two discs of radius $r/2$ have about half the area of one disc of radius $r$.

The subtle point is the stopping rule. It is **not** correct to stop when some vertex has been settled by both
searches (exercise 10). The correct rule: keep $\mu$, the weight of the best $s$–$t$ path seen so far (updated
whenever an edge relaxed by one search reaches a vertex labelled by the other), and stop when the smallest keys
in the two queues add up to at least $\mu$. *Why this is safe.* Let $f$ and $b$ be the smallest keys in the forward and backward queues, so every vertex
$x$ with $\delta(s, x) < f$ is settled forwards and every $y$ with $\delta(y, t) < b$ is settled backwards.
Suppose some path $P$ had weight $w(P) < \mu$, while $f + b \ge \mu$. Let $x$ be the last vertex of $P$ with
$\delta(s,x) < f$ (there is one: $s$), and $y$ the next vertex; then $\delta(s, y) \ge f$, so $\delta(y,t) \le
w(P) - \delta(s,y) < b$, and $y$ is settled backwards. Whichever of the two settlements came second relaxed the edge
$x \to y$ (forwards, or reversed) and saw the other end already labelled with its true distance, so it set $\mu \le
\delta(s,x) + w(x,y) + \delta(y,t) = w(P)$. That contradicts $w(P) < \mu$. In
the grid run, bidirectional Dijkstra settled 2041 cells against 2627; the saving is modest here because walls force
long detours, and much larger on open maps.

Ira Pohl studied bidirectional heuristic search in 1971. Combining bidirectional search with A\* needs care with
the two heuristics, and is one of the ingredients of the route planners in the next section.

### History, and the rovers

A\* came from the Shakey robot project at the Stanford Research Institute: Peter Hart, Nils Nilsson and Bertram
Raphael published "A Formal Basis for the Heuristic Determination of Minimum Cost Paths" in 1968, with the proof of
optimality for admissible heuristics. It has been a workhorse of robotics, games and AI search ever since; the
[AI book](../ai/index.md) uses it for problem solving in state spaces.

On Mars, a command from Earth takes 3 to 22 minutes to arrive, so rovers must plan parts of their drives
themselves. In the mid-2000s, JPL engineers integrated Field D\*, an incremental descendant of A\* that replans
quickly as the rover's map changes, into the flight software of the rovers Spirit and Opportunity (Carsten and
co-authors, 2007). Perseverance's AutoNav likewise builds terrain maps from its cameras as it drives and chooses its
path on board.

## 16.7 Real road maps: landmarks, shortcuts and 0-1 BFS

*Level: advanced.*

A road map of a continent has tens of millions of junctions. Plain Dijkstra would explore a large part of it for
every query. Route planners answer queries far faster by doing work in advance, **preprocessing**, and storing extra
information that every later query uses. Two of the best-known ideas fit naturally with this chapter.

### ALT: A\*, landmarks and the triangle inequality

The straight-line guess is weak on roads that wind around lakes and mountains. Goldberg and Harrelson (2005) found
a better guess that is still consistent. Pick a few **landmarks** $L$ and precompute $\delta(L, v)$ and $\delta(v,
L)$ for every vertex $v$ (one Dijkstra each way per landmark). By the triangle inequality,

$$
\delta(v, t) \ge \delta(L, t) - \delta(L, v) \quad\text{and}\quad \delta(v, t) \ge \delta(v, L) - \delta(t, L),
$$

because $\delta(L, t) \le \delta(L, v) + \delta(v, t)$ and $\delta(v, L) \le \delta(v, t) + \delta(t, L)$. So
$h(v) = \max$ over landmarks of these two bounds is admissible; it is also consistent, because each bound changes
by at most $w(u,v)$ along an edge (again by the triangle inequality), and a maximum of consistent functions is
consistent. A landmark "behind" the target (so that the shortest way from the landmark to $t$ passes near $v$)
makes the bound nearly exact. The name ALT stands for A\*, Landmarks and Triangle inequality.

The program uses the four corners of the grid as landmarks, with BFS tables from each. A\* with this guess settled
466 cells against 840 with Manhattan distance and 2627 with Dijkstra, and found the same 118-step path. The price
is the memory for the tables: one distance per vertex per landmark.

### Contraction hierarchies

The second idea comes from how people drive: you leave the side streets for a main road, take the motorway, and
leave it only near the end. **Contraction hierarchies** (Geisberger, Sanders, Schultes and Delling, 2008) make that
precise.

*Preprocessing.* Put the vertices in an order of "importance" (the rank), least important first. **Contract** them
one by one: remove vertex $v$, and for every pair of neighbours $u, w$ such that the path $u \to v \to w$ was the
only shortest path between them, add a **shortcut** edge $u \to w$ with weight $w(u,v) + w(v,w)$. (A small local
Dijkstra search, the "witness search", checks whether there is another path as short that avoids $v$; if so, no
shortcut is needed.) Distances among the remaining vertices are unchanged after each step. At the end, keep the
original edges plus all shortcuts.

*Query.* Run Dijkstra forwards from $s$ using only edges that go **up** in rank, and backwards from $t$ using only
edges that go up in rank; the answer is the minimum over vertices $x$ reached by both of $d_s(x) + d_t(x)$.

<figure class="mars-fig" markdown="0">
<svg viewBox="0 0 600 200" role="img" aria-label="Contraction of a vertex v with neighbours u and w: the path u, v, w of length 3 plus 4 is replaced by a shortcut u to w of length 7 when no shorter detour exists">
<line x1="75.8" y1="101.4" x2="154.2" y2="58.6" stroke="currentColor" stroke-width="1.5"/>
<text x="120.7" y="95.1" font-size="13" text-anchor="middle" fill="currentColor">3</text>
<line x1="185.8" y1="58.6" x2="264.2" y2="101.4" stroke="currentColor" stroke-width="1.5"/>
<text x="219.3" y="95.1" font-size="13" text-anchor="middle" fill="currentColor">4</text>
<line x1="78.0" y1="110.0" x2="262.0" y2="110.0" stroke="currentColor" stroke-width="1.5" stroke-dasharray="5 4"/>
<text x="170.0" y="114.2" font-size="12" text-anchor="middle" fill="currentColor"></text>
<text x="170" y="128" font-size="12" text-anchor="middle" fill="currentColor">shortcut 7</text>
<text x="170" y="170" font-size="12" text-anchor="middle" fill="currentColor">contract v (low rank)</text>
<text x="386" y="154" font-size="11" text-anchor="start" fill="currentColor">rank 1</text>
<text x="456" y="99" font-size="11" text-anchor="start" fill="currentColor">rank 3</text>
<text x="526" y="44" font-size="11" text-anchor="start" fill="currentColor">rank 5</text>
<text x="534" y="154" font-size="11" text-anchor="end" fill="currentColor">rank 2</text>
<line x1="374.2" y1="138.9" x2="409.6" y2="111.1" stroke="#eea66f" stroke-width="2.5"/>
<polygon points="415.8,106.1 411.5,115.2 406.0,108.1" fill="#eea66f"/>
<line x1="444.2" y1="83.9" x2="479.6" y2="56.1" stroke="#eea66f" stroke-width="2.5"/>
<polygon points="485.8,51.1 481.5,60.2 476.0,53.1" fill="#eea66f"/>
<line x1="551.4" y1="134.2" x2="512.5" y2="62.8" stroke="#7ccf9a" stroke-width="2.5"/>
<polygon points="508.6,55.8 516.9,61.5 509.0,65.9" fill="#7ccf9a"/>
<text x="480" y="190" font-size="12" text-anchor="middle" fill="currentColor">query: both searches only climb</text>
<circle cx="60" cy="110" r="18" fill="#9cc9ea" fill-opacity="0.55" stroke="currentColor" stroke-width="1.5"/>
<text x="60" y="114.9" font-size="14" text-anchor="middle" fill="currentColor">u</text>
<circle cx="170" cy="50" r="18" fill="#eea66f" fill-opacity="0.55" stroke="currentColor" stroke-width="1.5"/>
<text x="170" y="54.9" font-size="14" text-anchor="middle" fill="currentColor">v</text>
<circle cx="280" cy="110" r="18" fill="#9cc9ea" fill-opacity="0.55" stroke="currentColor" stroke-width="1.5"/>
<text x="280" y="114.9" font-size="14" text-anchor="middle" fill="currentColor">w</text>
<circle cx="360" cy="150" r="18" fill="#9cc9ea" fill-opacity="0.55" stroke="currentColor" stroke-width="1.5"/>
<text x="360" y="154.9" font-size="14" text-anchor="middle" fill="currentColor">s</text>
<circle cx="430" cy="95" r="18" fill="#9cc9ea" fill-opacity="0.55" stroke="currentColor" stroke-width="1.5"/>
<text x="430" y="99.9" font-size="14" text-anchor="middle" fill="currentColor">q</text>
<circle cx="500" cy="40" r="18" fill="#eea66f" fill-opacity="0.55" stroke="currentColor" stroke-width="1.5"/>
<text x="500" y="44.9" font-size="14" text-anchor="middle" fill="currentColor">r</text>
<circle cx="560" cy="150" r="18" fill="#9cc9ea" fill-opacity="0.55" stroke="currentColor" stroke-width="1.5"/>
<text x="560" y="154.9" font-size="14" text-anchor="middle" fill="currentColor">t</text>
</svg>
<figcaption>Figure 16.5. Contraction hierarchies in two pictures. Left: removing an unimportant vertex v adds a shortcut u–w that keeps every shortest distance the same. Right: at query time the forward search from s and the backward search from t only follow edges to higher-ranked vertices, and they meet at the top of the route.</figcaption>
</figure>

**Why the query is correct (sketch).** Take a shortest path from $s$ to $t$ in the graph with shortcuts, and look at
its highest-ranked vertex $x$. Consider any vertex $v$ on the path that has neighbours on both sides ranked above
it, and pick the lowest-ranked one: when $v$ was contracted, its two path neighbours were still present, and either
a shortcut between them was added or a witness path as short exists among higher-ranked vertices. Replace and
repeat. Each step removes a "valley" and the rank strictly increases, so it ends with a shortest path that goes
only up from $s$ to $x$ and only down from $x$ to $t$, which is exactly what the two upward searches find. The
detailed proof, and the heuristics for choosing the order (for example, contracting first the vertices whose removal
adds the fewest shortcuts), are in the 2008 paper. On road networks the upward searches visit only a few hundred
vertices, and the authors report query times orders of magnitude faster than Dijkstra's algorithm. Many production
routing engines use contraction hierarchies or close relatives.

### 0-1 BFS

A last special case is common in puzzles and grids: every edge weight is 0 or 1 (a free move, or a move that costs
one unit, such as breaking through a wall or changing a train line). Dijkstra works, but a heap is unnecessary.
Use a **double-ended queue**: when relaxing an edge of weight 0, put the vertex at the *front*; of weight 1, at the
*back*.

**Why it works.** By the same induction as Lemma 15.1, the deque always holds vertices whose labels are $D$ at the
front part and $D + 1$ at the back part, for some $D$, in non-decreasing order: a 0-edge adds a vertex with label
$D$ at the front, a 1-edge adds $D + 1$ at the back. So vertices come out in non-decreasing order of label, exactly
as Dijkstra's heap would deliver them, and the correctness proof of Dijkstra applies. Each vertex can be added
once per improvement, at most once per incoming edge, so the time is $O(V + E)$. The program's example agrees with
Dijkstra on every vertex.

More generally, for integer weights at most $C$, **Dial's algorithm** (1969) keeps an array of $C + 1$ buckets
indexed by distance and runs in $O(V C + E)$; radix heaps improve this further.

### Shortest paths and the frontier

Shortest paths with negative weights were long stuck near Bellman-Ford's $O(VE)$ for general graphs. In 2022,
Bernstein, Nanongkai and Wulff-Nilsen gave a near-linear-time algorithm for integer weights, and the same year the
almost-linear-time max-flow algorithm of Chen and co-authors also solves negative-weight shortest paths;
[Chapter 25](25-Where-Algorithms-Go.md) returns to both.

## Check yourself

??? question "1. Run Dijkstra on the graph of Figure 16.1 starting from b. Which vertices are reachable, and what are their distances?"

    From $b$ the edges lead to $a$ (2), $c$ (5) and $d$ (8); $s$ has no incoming edges, so it is unreachable and
    stays at ∞. Settle b (0): a = 2, c = 5, d = 8. Settle a (2): c = 3. Settle c (3): d = 6, e = 9. Settle d (6):
    e = 7. Settle e (7). Distances: a 2, c 3, d 6, e 7, s ∞. The program's `dijkstra(G, "b", trace=True)` prints
    the same rows.

??? question "2. A student suggests handling negative weights by adding a large constant to every edge so that all become non-negative, then running Dijkstra. Show that this can change the answer."

    A path with $k$ edges gets heavier by $k$ times the constant, so paths with many edges are penalised more than
    paths with few. Example: $s \to t$ directly with weight 5, and $s \to a \to t$ with weights 2 and 2. The
    shortest path is $s, a, t$ with weight 4. Add 2 to every edge: the direct edge becomes 7 and the two-edge path
    becomes $4 + 4 = 8$, so the "shortest" path changes to the direct edge. Johnson's reweighting avoids this,
    because $h(u) - h(v)$ telescopes along any path to the same total.

??? question "3. In the lazy-heap version of Dijkstra on Figure 16.1, how many pairs are pushed onto the heap, and how many popped pairs are skipped as stale?"

    Pushes: the start $(0, s)$; from $s$: $(4, a)$, $(1, b)$; from $b$: $(3, a)$, $(6, c)$, $(9, d)$; from $a$:
    $(4, c)$; from $c$: $(7, d)$, $(10, e)$; from $d$: $(8, e)$. That is 10 pushes. Every pair is eventually popped,
    and 6 of the pops settle a vertex, so 4 are stale: $(4, a)$, $(6, c)$, $(9, d)$ and $(10, e)$. Each stale pair
    was pushed before a better path to the same vertex was found.

??? question "4. Order the edges of the graph in Figure 16.3 so that Bellman-Ford has the right distances after one round."

    Relax the edges of the shortest-path tree in the order of the paths: s→b, b→c, c→a, c→d, then the rest (a→b,
    s→a, a→c, b→d) in any order. After s→b, $b = 7$; after b→c, $c = 5$; after c→a, $a = 4$; after c→d, $d = 7$. The
    remaining edges cannot improve anything, and round 2 confirms that nothing changes. This is the path-relaxation
    property: one round suffices whenever the order relaxes each shortest path's edges in sequence. Bellman-Ford's
    $V - 1$ rounds are what you pay for not knowing such an order in advance.

??? question "5. Write code to detect arbitrage. With rates USD→EUR 0.9, EUR→USD 1.1, EUR→GBP 0.9, GBP→EUR 1.1, GBP→USD 1.25, USD→GBP 0.78, is there an arbitrage cycle?"

    Use $w = -\log(\text{rate})$; a cycle whose rates multiply to more than 1 has negative total weight. Start
    every vertex at 0 (as if a new source were joined to all), run $V - 1$ rounds, and look for an edge that still
    improves.

    ```python
    import math

    def arbitrage(rates):
        names = sorted({a for a, b in rates} | {b for a, b in rates})
        edges = [(a, b, -math.log(r)) for (a, b), r in rates.items()]
        dist = {v: 0.0 for v in names}
        parent = {v: None for v in names}
        for _ in range(len(names) - 1):
            for a, b, w in edges:
                if dist[a] + w < dist[b] - 1e-12:
                    dist[b], parent[b] = dist[a] + w, a
        for a, b, w in edges:
            if dist[a] + w < dist[b] - 1e-12:     # still improving: negative cycle
                parent[b] = a
                x = b
                for _ in range(len(names)):
                    x = parent[x]
                cyc, y = [x], parent[x]
                while y != x:
                    cyc.append(y)
                    y = parent[y]
                cyc.reverse()
                return cyc + cyc[:1]
        return None
    ```

    It returns `['GBP', 'USD', 'EUR', 'GBP']`: $1.25 \times 0.9 \times 0.9 = 1.0125$, so converting round this
    cycle gains 1.25 percent. (The reverse cycle multiplies to $0.78 \times 1.1 \times 1.1 = 0.9438$, a loss.) The
    tiny tolerance `1e-12` stops rounding errors in the logarithms from inventing cycles.

??? question "6. Change the edge 3→0 in the Floyd-Warshall example from weight 2 to weight −5. What does Floyd-Warshall show, and why?"

    The cycle 0 → 1 → 3 → 0 now weighs $3 + 1 - 5 = -1$. Running the same code gives the diagonal $D[0][0] = -1$,
    $D[1][1] = -1$, $D[2][2] = 0$, $D[3][3] = -2$: negative entries on the diagonal, which is the test for a
    negative cycle. A diagonal entry $D[i][i] < 0$ means the algorithm found a closed walk from $i$ to $i$ of negative
    weight. (Once a negative cycle exists, the other entries are no longer meaningful distances, and the in-place
    updates can even double-count the cycle, as $D[3][3] = -2$ shows.)

??? question "7. Prove that Dijkstra's algorithm, with non-negative weights, settles vertices in non-decreasing order of distance."

    Let $u$ be settled just before $u'$. When $u$ was chosen, $d[u] \le d[u']$. Settling $u$ then relaxes $u$'s
    edges, which may lower $d[u']$, but only to $d[u] + w(u, u') \ge d[u]$ since $w \ge 0$. So when $u'$ is chosen,
    $d[u'] \ge d[u]$, and both values are the true distances by Theorem 16.4. By induction over consecutive pairs
    the whole settling order is non-decreasing. With a negative edge the second step fails, which is the failure in
    the program's example.

??? question "8. Show that the great-circle distance to the target is a consistent heuristic for the Mars road map, and say what A* does on it."

    Every road is a great-circle arc, whose length is the great-circle distance between its ends. Great-circle
    distance obeys the triangle inequality on the sphere: $g(u, t) \le g(u, v) + g(v, t)$, and $g(u, v) = w(u, v)$
    for a road. So $h(u) \le w(u, v) + h(v)$ with $h(t) = 0$: consistent. From Erebus Montes to Gale crater,
    Dijkstra settles Erebus Montes, Elysium Mons, Utopia Planitia, Olympus Mons, Gale crater; A* settles only Erebus
    Montes, Elysium Mons and Gale crater, and both report 3895 km.

??? question "9. Write Floyd-Warshall with path reconstruction. What is the shortest path from 1 to 2 in the example, and from 2 to 0?"

    Keep `nxt[i][j]`, the first vertex after $i$ on the best known path to $j$. When going through $k$ improves
    $D[i][j]$, the first step becomes the first step towards $k$.

    ```python
    import math

    def floyd_paths(n, edges):
        INF = math.inf
        D = [[0 if i == j else INF for j in range(n)] for i in range(n)]
        nxt = [[j if i == j else None for j in range(n)] for i in range(n)]
        for u, v, w in edges:
            if w < D[u][v]:
                D[u][v], nxt[u][v] = w, v
        for k in range(n):
            for i in range(n):
                for j in range(n):
                    if D[i][k] + D[k][j] < D[i][j]:
                        D[i][j] = D[i][k] + D[k][j]
                        nxt[i][j] = nxt[i][k]
        return D, nxt

    def walk(nxt, i, j):
        if nxt[i][j] is None:
            return None
        p = [i]
        while i != j:
            i = nxt[i][j]
            p.append(i)
        return p
    ```

    On the example: from 1 to 2, distance −4 by the path [1, 3, 2]; from 2 to 0, distance 7 by [2, 1, 3, 0] (weights
    $4 + 1 + 2$). Storing `nxt` costs another $V^2$ entries but no extra time.

??? question "10. Give a graph where stopping bidirectional Dijkstra as soon as some vertex is settled by both searches gives a wrong answer."

    Undirected graph: $s$–$u$ 4, $u$–$t$ 4, and $s$–$a$ 3, $a$–$b$ 1.5, $b$–$t$ 3. The true distance is 7.5 by $s,
    a, b, t$. Forward search settles $s$ (0), then $a$ (3); backward search settles $t$ (0), then $b$ (3). Next the
    forward queue holds $u$ at 4 and $b$ at 4.5, so it settles $u$ at 4; the backward queue holds $u$ at 4 and $a$
    at 4.5, so it settles $u$ too. Now $u$ is settled by both, with total $4 + 4 = 8$, but the answer is 7.5. The
    correct rule keeps $\mu$, which was lowered to 7.5 when the forward search relaxed $a$–$b$ and found $b$ already
    labelled by the backward search, and stops only when the two queue tops add up to at least $\mu$ ($4 + 4 \ge
    7.5$, so it stops with the right answer).

## What you learned

- A shortest path's pieces are shortest paths; distances obey the triangle inequality; negative cycles make
  distances undefined, and without them shortest paths can be taken simple.
- Every algorithm here only relaxes edges; it is correct once each shortest path's edges are relaxed in order.
- Dijkstra settles the closest unsettled vertex, is correct for non-negative weights, and costs $O(V^2)$ with an
  array, $O((V + E)\log V)$ with a binary heap, $O(E + V \log V)$ with a Fibonacci heap; it draws the banner's
  Mars route of 3895 km.
- Bellman-Ford relaxes every edge $V - 1$ times, handles negative weights in $O(VE)$, and finds negative cycles; in a
  DAG, one pass in topological order suffices, even for longest paths.
- Floyd-Warshall computes all pairs in $\Theta(V^3)$ by dynamic programming over allowed intermediate vertices;
  Johnson reweights with potentials so that $V$ runs of Dijkstra work despite negative edges.
- A\* is Dijkstra on edges tilted by a consistent heuristic, and stays optimal; landmarks give strong heuristics, and
  contraction hierarchies, bidirectional search and 0-1 BFS make real route planning fast.

**Next:** [Chapter 17](17-Spanning-Trees-Flows-and-Matching.md), the cheapest way to connect everything, how much
can flow through a network, and how to pair things up.

## Further reading

- T. H. Cormen, C. E. Leiserson, R. L. Rivest and C. Stein, *Introduction to Algorithms*, 4th ed., MIT Press, 2022,
  Chapters 22 and 23 (single-source and all-pairs shortest paths).
- J. Kleinberg and É. Tardos, *Algorithm Design*, Addison-Wesley, 2005, Sections 4.4 and 6.8-6.10.
- R. Sedgewick and K. Wayne, *Algorithms*, 4th ed., Addison-Wesley, 2011, Section 4.4.
- E. W. Dijkstra, "A note on two problems in connexion with graphs", *Numerische Mathematik* 1, 1959.
- R. Bellman, "On a routing problem", *Quarterly of Applied Mathematics* 16, 1958.
- R. W. Floyd, "Algorithm 97: Shortest path", *Communications of the ACM* 5(6), 1962; S. Warshall, "A theorem on
  Boolean matrices", *Journal of the ACM* 9(1), 1962.
- D. B. Johnson, "Efficient algorithms for shortest paths in sparse networks", *Journal of the ACM* 24(1), 1977.
- P. E. Hart, N. J. Nilsson and B. Raphael, "A formal basis for the heuristic determination of minimum cost paths",
  *IEEE Transactions on Systems Science and Cybernetics* 4(2), 1968.
- M. L. Fredman and R. E. Tarjan, "Fibonacci heaps and their uses in improved network optimization algorithms",
  *Journal of the ACM* 34(3), 1987.
- A. V. Goldberg and C. Harrelson, "Computing the shortest path: A\* search meets graph theory", SODA 2005.
- R. Geisberger, P. Sanders, D. Schultes and D. Delling, "Contraction hierarchies: faster and simpler hierarchical
  routing in road networks", WEA 2008.
- M. Thorup, "Undirected single-source shortest paths with positive integer weights in linear time", *Journal of the
  ACM* 46(3), 1999.
- R. Duan, J. Mao, X. Mao, X. Shu and L. Yin, "Breaking the sorting barrier for directed single-source shortest
  paths", STOC 2025.
- B. Haeupler, R. Hladík, V. Rozhoň, R. Tarjan and J. Tětek, "Universal optimality of Dijkstra via beyond-worst-case
  heaps", FOCS 2024.
- J. Carsten, A. Rankin, D. Ferguson and A. Stentz, "Global path planning on board the Mars Exploration Rovers",
  IEEE Aerospace Conference, 2007.
- P. L. Frana, "An interview with Edsger W. Dijkstra", *Communications of the ACM* 53(8), 2010.
- On this site: [Dijkstra's algorithm](../../graphs/dijkstra.md), [Bellman-Ford](../../graphs/bellman-ford.md),
  [Floyd-Warshall](../../graphs/floyd-warshall.md), [Breadth-first search](../../graphs/bfs.md),
  [Binary heap](../../data-structures/binary-heap.md), and the [AI book](../ai/index.md) for A\* in problem solving.
