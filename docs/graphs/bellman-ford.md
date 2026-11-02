# Bellman-Ford

*Shortest paths from one start even when some edges have negative weights. Relax every edge, $V-1$ times. If a
further round still improves something, there is a negative cycle and "shortest" makes no sense.*

| Time | Extra space | Handles | Detects |
|---|---|---|---|
| $O(VE)$ | $O(V)$ | negative weights | negative cycles reachable from the start |

## The idea

Negative weights appear naturally: a refund, an energy gain going downhill, a currency exchange rate turned into
a logarithm. [Dijkstra](dijkstra.md) settles vertices for good and so cannot cope with them.

Bellman-Ford never settles anything. It just **relaxes every edge** (`dist[v] = min(dist[v], dist[u] + w)`),
round after round. After round 1, every shortest path that uses at most 1 edge is correct; after round 2, every
one with at most 2 edges; and so on. A shortest path never repeats a vertex (if there is no negative cycle), so it
has at most $V-1$ edges, and $V-1$ rounds are enough.

If round $V$ would still lower some distance, the only explanation is a **negative cycle**: going round it again
and again lowers the cost forever. Bellman-Ford reports it instead of a wrong answer.

## How it works

1. `dist[src] = 0`, all others $\infty$.
2. Repeat $V-1$ times: for every edge `(u, v, w)`, if `dist[u] + w < dist[v]`, lower `dist[v]`. Stop early if a
   round changes nothing.
3. One more pass over the edges: if any distance can still be lowered, a negative cycle is reachable.

## Code

=== "Python"

    ```python
    --8<-- "graphs/bellman_ford.py"
    ```

=== "Java"

    ```java
    --8<-- "graphs/BellmanFord.java"
    ```

=== "C++"

    ```cpp
    --8<-- "graphs/bellman_ford.cpp"
    ```

Output: `[0, 2, 7, 4, -2]`, the same with `inf` for an extra unreachable vertex, and `True`: the graph with the
cycle 1 → 2 → 1 of total weight $-2$ has a negative cycle.

## When to use it

- **Graphs with negative weights** and few vertices or edges.
- **Detecting negative cycles:** **currency arbitrage** (with weights $-\log(\text{rate})$, a negative cycle is a
  sequence of trades that makes money), inconsistent constraints.
- **Difference constraints** $x_v - x_u \le w$: a system is solvable exactly when its constraint graph has no
  negative cycle, and Bellman-Ford finds a solution.
- **Distance-vector routing** (RIP): each router relaxes its neighbours' tables, a distributed Bellman-Ford.
- For non-negative weights, [Dijkstra](dijkstra.md) is much faster.

## Common mistakes

- **Relaxing from $\infty$:** `INF + (-4)` is not $\infty$; check `dist[u] != INF` first (and in Java and C++,
  avoid overflow).
- **Only $V-2$ rounds**, or forgetting the final check.
- **Undirected graphs with a negative edge:** the edge is itself a negative cycle ($u \to v \to u$).
- **Negative cycles that cannot be reached** from the start do not affect its distances and are not reported.

## Going deeper

Each part below starts closed; open the ones you want.

??? example "Sample walkthrough: the demo graph from vertex 0"

    Edges in the order relaxed: 0→1 (6), 0→2 (7), 1→2 (8), 1→3 (5), 1→4 (−4), 2→3 (−3), 2→4 (9), 3→1 (−2),
    4→0 (2), 4→3 (7).

    | Round | Changes, in order | Distances after (0..4) |
    |---|---|---|
    | 1 | d1 = 6, d2 = 7, d3 = 11, d4 = 2, d3 = 7 − 3 = 4, d1 = 4 − 2 = 2 | 0, 2, 7, 4, 2 |
    | 2 | d4 = 2 − 4 = −2 | 0, 2, 7, 4, −2 |
    | 3 | none: stop early | 0, 2, 7, 4, −2 |

    The order of edges matters for speed (round 1 already did a lot) but not for the final answer.

??? abstract "The math: why V − 1 rounds are enough"

    **Lemma.** After round $k$, $\text{dist}[v] \le$ the length of the shortest path from $s$ to $v$ that uses at
    most $k$ edges. Proof by induction on $k$: such a path is a path of at most $k-1$ edges to some $u$, then the
    edge $u \to v$; after round $k-1$, $\text{dist}[u]$ is at most the first part, and round $k$ relaxes $u \to v$.

    Also $\text{dist}[v]$ is always the length of *some* real path, so it never drops below $\delta(v)$.

    **No negative cycle reachable:** a shortest path can drop any cycle (of weight $\ge 0$) without getting
    longer, so some shortest path is simple and has at most $V-1$ edges. After $V-1$ rounds,
    $\text{dist}[v] = \delta(v)$, and no edge can be relaxed any more.

    **A negative cycle $v_0 \to v_1 \to \cdots \to v_k = v_0$ reachable:** suppose no edge could be relaxed, so
    $\text{dist}[v_i] \le \text{dist}[v_{i-1}] + w(v_{i-1}, v_i)$ for every $i$. Adding these $k$ inequalities, the
    distances cancel (each appears once on each side) and

    $$
    0 \;\le\; \sum_{i=1}^{k} w(v_{i-1}, v_i) \;<\; 0,
    $$

    a contradiction. So round $V$ always finds something to relax.

    **Time:** $V-1$ rounds of $E$ relaxations: $O(VE)$. The **SPFA** variant only re-relaxes edges out of
    vertices whose distance just changed; often much faster, but still $O(VE)$ in the worst case.

??? tip "Watch it step by step"

    Each frame is one full round over the edges; red edges and vertices changed in that round.

    <div class="cs-anim" data-anim="bellman-ford"></div>

??? info "Variations and related ideas"

    - **Finding the negative cycle itself:** take a vertex relaxed in round $V$, follow parents $V$ times to land
      inside the cycle, then walk the parents round it.
    - **Shortest paths with at most $k$ edges** (cheapest flight with at most $k$ stops): run exactly $k$
      rounds, relaxing from a copy of the previous round's distances.
    - **Johnson's algorithm** uses one Bellman-Ford run to reweight edges so that they are all non-negative, then
      runs Dijkstra from every vertex.

## See also

- [Dijkstra's algorithm](dijkstra.md): faster, non-negative weights only
- [Floyd-Warshall](floyd-warshall.md): all pairs, negative weights allowed

## References

- R. Bellman, "On a routing problem", *Quarterly of Applied Mathematics* 16, 1958.
- L. R. Ford Jr., *Network Flow Theory*, RAND Corporation paper P-923, 1956.
- T. H. Cormen et al., *Introduction to Algorithms*, 4th ed., §22.1 (the Bellman-Ford algorithm); the demo graph is the one in their Bellman-Ford example.
