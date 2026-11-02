# Dijkstra's algorithm

*Shortest paths from one place to all others when no edge has a negative length. Repeatedly settle the closest
place not yet settled, then see whether going through it shortens the way to its neighbours.*

| Time (binary heap) | Extra space | Needs |
|---|---|---|
| $O((V + E) \log V)$ | $O(V + E)$ | every edge weight $\ge 0$ |

## The idea

Imagine water spreading from the start along every road at the same speed. It reaches places in order of their
true distance. Dijkstra's algorithm simulates this without the water.

Keep a best-known distance for every place: 0 for the start, $\infty$ for the rest. Then repeat:

1. Pick the **unsettled place with the smallest known distance** and **settle** it: its distance is now final.
2. For each road from it, check whether going through it is shorter than the best-known way to the other end
   (**relaxing** the edge): `if dist[u] + w < dist[v]: dist[v] = dist[u] + w`.

Why is the closest unsettled place final? Any other route to it would have to leave the settled region through
some unsettled place that is already at least as far away, and with no negative roads the rest of that route
cannot make it shorter. This is exactly where negative weights break the method.

A **min-heap** finds the closest unsettled place quickly. Instead of updating entries inside the heap, the code
pushes a new entry and skips stale ones when they come out.

The demo uses real places on Mars, with roads as long as the true distances between them, the same network as
the picture on the [home page](../index.md).

## How it works

1. `dist = [∞, ...]`, `dist[src] = 0`; heap = `[(0, src)]`.
2. While the heap is not empty: pop `(d, u)`; if `d > dist[u]`, skip it (stale). Otherwise, for each edge
   `u → v` of weight `w`, if `d + w < dist[v]`, set `dist[v] = d + w`, `parent[v] = u`, and push `(dist[v], v)`.

## Code

=== "Python"

    ```python
    --8<-- "graphs/dijkstra.py"
    ```

=== "Java"

    ```java
    --8<-- "graphs/Dijkstra.java"
    ```

=== "C++"

    ```cpp
    --8<-- "graphs/dijkstra.cpp"
    ```

Output (one line per place):

```
Erebus Montes: 0 km via Erebus Montes
Olympus Mons: 2369 km via Erebus Montes > Olympus Mons
Ascraeus Mons: 4109 km via Erebus Montes > Olympus Mons > Ascraeus Mons
Valles Marineris: 7152 km via Erebus Montes > Olympus Mons > Ascraeus Mons > Valles Marineris
Elysium Mons: 2016 km via Erebus Montes > Elysium Mons
Utopia Planitia: 2305 km via Erebus Montes > Utopia Planitia
Gale crater: 3895 km via Erebus Montes > Elysium Mons > Gale crater
Jezero crater: 5519 km via Erebus Montes > Utopia Planitia > Jezero crater
Hellas Planitia: 8017 km via Erebus Montes > Elysium Mons > Gale crater > Hellas Planitia
```

The direct road from Olympus Mons to Gale crater (5,337 km) is never used: going round by Elysium Mons is shorter.

## When to use it

- **Road maps and navigation** (with refinements such as A* and contraction hierarchies), **network routing**
  (the OSPF protocol runs Dijkstra on every router), flight connections with travel times.
- **Any "cheapest way" problem with non-negative costs:** the fewest coins of energy, the least risk.
- **Grids with different terrain costs**, games' path-finding.
- **Not** with negative weights: use [Bellman-Ford](bellman-ford.md).

## Common mistakes

- **Negative edges:** the answer is silently wrong.
- **Not skipping stale heap entries:** still correct but slower; with `if d > dist[u]: continue` each vertex is
  expanded once.
- **Overflow:** start distances at a large value and use 64-bit sums; `INT_MAX + w` wraps around in Java and C++.
- **Stopping too early:** for one target, you may stop when the *target is popped*, not when it is first reached.
- **Using it for the longest path:** negating weights makes them negative, which Dijkstra cannot handle.

## Going deeper

Each part below starts closed; open the ones you want.

??? example "Sample walkthrough: from Erebus Montes"

    | Settle (distance) | Improvements |
    |---|---|
    | Erebus Montes (0) | Olympus 2,369 · Elysium 2,016 · Utopia 2,305 |
    | Elysium Mons (2,016) | Gale 2,016 + 1,879 = 3,895 (Utopia: 2,016 + 1,486 = 3,502, worse than 2,305) |
    | Utopia Planitia (2,305) | Jezero 2,305 + 3,214 = 5,519 |
    | Olympus Mons (2,369) | Ascraeus 4,109 (Gale via Olympus: 7,706, worse) |
    | Gale crater (3,895) | Hellas 3,895 + 4,122 = 8,017 (Jezero via Gale: 7,677, worse) |
    | Ascraeus Mons (4,109) | Valles 7,152 |
    | Jezero crater (5,519) | (Hellas via Jezero: 9,135, worse) |
    | Valles Marineris (7,152) | — |
    | Hellas Planitia (8,017) | — |

??? abstract "The math: correctness and running time"

    Let $\delta(v)$ be the true shortest distance and $S$ the set of settled vertices.

    **Invariant.** For every $v \in S$, $\text{dist}[v] = \delta(v)$; for every $v \notin S$, $\text{dist}[v]$ is
    the shortest path to $v$ whose vertices, apart from $v$, all lie in $S$.

    **Proof that the next settled vertex is correct.** Let $u$ be the unsettled vertex with the smallest
    $\text{dist}$. Take any path $P$ from $s$ to $u$, and let $y$ be the first vertex on it outside $S$. Then

    $$
    \text{len}(P) \;\ge\; \delta_{S}(y) \;=\; \text{dist}[y] \;\ge\; \text{dist}[u],
    $$

    because the part of $P$ after $y$ has length $\ge 0$ (**this is where non-negative weights are used**), the
    part up to $y$ is a path through $S$, and $u$ was chosen with the smallest $\text{dist}$. So no path beats
    $\text{dist}[u]$, and $\text{dist}[u] = \delta(u)$.

    **Running time** with a binary heap: at most $E$ pushes and pops, each $O(\log E) = O(\log V)$ (since
    $E < V^2$), plus $O(V + E)$ for scanning lists:

    $$
    T = O\big((V + E)\log V\big).
    $$

    With a Fibonacci heap (decrease-key in $O(1)$ amortized), $O(E + V \log V)$. With a plain array and no heap,
    $O(V^2)$, which is better for very dense graphs.

    **Great-circle distances** used in the demo: for latitudes $\varphi_1, \varphi_2$ and longitude difference
    $\Delta\lambda$, the central angle is $\theta = \arccos(\sin\varphi_1 \sin\varphi_2 + \cos\varphi_1 \cos\varphi_2 \cos\Delta\lambda)$,
    and the distance is $R\theta$ with Mars's mean radius $R = 3389.5$ km.

??? tip "Watch it step by step"

    Numbers above places are the best-known distances in km. Orange is the place being settled, green the settled
    ones, blue those waiting in the heap; red roads just improved a distance.

    <div class="cs-anim" data-anim="dijkstra"></div>

??? info "Variations and related ideas"

    - **A\* search** adds a guess of the remaining distance (for maps, the straight-line distance) to steer the
      search towards the target; with a guess that never overestimates, it still finds a shortest path, usually
      after exploring far fewer vertices.
    - **Bidirectional Dijkstra** searches from both ends.
    - **Contraction hierarchies** precompute shortcuts so that continental road networks answer queries in
      milliseconds.
    - **Johnson's algorithm** reweights a graph with negative edges (using Bellman-Ford once) so that Dijkstra can
      run from every vertex: all pairs in $O(VE \log V)$.
    - **Widest path / most reliable path:** the same scheme with max-min or products instead of sums.

## See also

- [Breadth-first search](bfs.md): the unweighted case
- [Bellman-Ford](bellman-ford.md): negative weights
- [Binary heap](../data-structures/binary-heap.md)
- [Prim's algorithm](prim.md): almost the same code, a different question

## References

- E. W. Dijkstra, "A note on two problems in connexion with graphs", *Numerische Mathematik* 1, 1959.
- T. H. Cormen et al., *Introduction to Algorithms*, 4th ed., §22.3 (Dijkstra's algorithm).
- P. E. Hart, N. J. Nilsson, B. Raphael, "A formal basis for the heuristic determination of minimum cost paths", *IEEE Transactions on Systems Science and Cybernetics* 4(2), 1968 (A*).
- Place coordinates: USGS Gazetteer of Planetary Nomenclature.
