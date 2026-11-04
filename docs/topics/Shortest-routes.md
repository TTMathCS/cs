# Find the shortest route guide

*Maps, computer networks, game characters, delivery vans: anything with places and the roads between them. Four parts: stop at the one you need.*

[In one minute](#in-one-minute) · [Do it](#do-it) · [Expert](#expert) · [Now and next](#now-and-next)

## In one minute

Draw dots for places and lines for the roads between them, and write each road's length on its line. Computer scientists call this a **graph**.

To find the shortest way from home to school, imagine pouring water at home. It spreads along every road at the same speed, so it reaches each place in order of distance. The first time water reaches school, it came along the shortest route. **Dijkstra's algorithm** (1956) does exactly this, without the water: it always takes the closest place not yet reached next.

If every road is equally long, it is even simpler: visit places in rings, one step away, then two, then three (**breadth-first search**). A map app does the same thing at enormous scale, with tricks so it answers in milliseconds.

## Do it

**With a library** (Python, `pip install networkx`)

```python
import networkx as nx

G = nx.Graph()                                         # nx.DiGraph() for one-way roads
G.add_weighted_edges_from([("A", "B", 4), ("A", "C", 1), ("C", "B", 2), ("B", "D", 5)])
nx.shortest_path(G, "A", "D", weight="weight")         # ['A', 'C', 'B', 'D']
nx.shortest_path_length(G, "A", "D", weight="weight")  # 8
nx.shortest_path(G, "A", "D")                          # ['A', 'B', 'D']: fewest roads, ignoring length
nx.astar_path(G, "A", "D", heuristic=h, weight="weight")   # with a distance estimate h(u, v)
```

**Yourself**: Dijkstra in a dozen lines, with a heap

```python
import heapq

def dijkstra(graph, start):                            # graph: {place: [(neighbour, length), ...]}
    dist = {start: 0}
    heap = [(0, start)]
    while heap:
        d, u = heapq.heappop(heap)
        if d > dist[u]:
            continue                                   # an old, longer entry: skip it
        for v, w in graph[u]:
            if d + w < dist.get(v, float("inf")):
                dist[v] = d + w
                heapq.heappush(heap, (d + w, v))
    return dist
```

The same in Java and C++, with a step-by-step animation: [Dijkstra](../graphs/dijkstra.md).

**Real road maps:** OpenStreetMap data with a routing engine (OSRM, GraphHopper, Valhalla), or a library such as OSMnx for Python.

## Expert

### Which algorithm when

| Situation | Algorithm | Time | Notes |
|---|---|---|---|
| Every edge the same length | [Breadth-first search](../graphs/bfs.md) | $O(V + E)$ | also 0/1 weights with a deque |
| Lengths $\ge 0$, one start | [Dijkstra](../graphs/dijkstra.md) | $O((V + E) \log V)$ with a binary heap | the default |
| One start, one goal, a good distance estimate | A* (Hart, Nilsson and Raphael, 1968) | often far less than Dijkstra | estimate must never overstate the true distance |
| Some lengths negative | [Bellman-Ford](../graphs/bellman-ford.md) | $O(VE)$ | also detects negative cycles |
| Every pair, small graph | [Floyd-Warshall](../graphs/floyd-warshall.md) | $O(V^3)$ | a few lines; up to a few thousand places |
| No cycles (a schedule, a build) | [Topological order](../graphs/topological-sort.md), then one pass | $O(V + E)$ | longest paths too |
| Road networks, millions of queries | contraction hierarchies, hub labels, customizable route planning | microseconds to milliseconds per query | hours of preprocessing once |
| Connect every place as cheaply as possible (not a route) | [Kruskal](../graphs/kruskal.md), [Prim](../graphs/prim.md) | $O(E \log V)$ | a spanning tree, a different problem |

### Implementations

| Tool | Where |
|---|---|
| **NetworkX** | Python, easy, small to medium graphs |
| **igraph**, **graph-tool** | Python and R, large graphs (C / C++ cores) |
| **Boost Graph Library** | C++ |
| **JGraphT** | Java |
| **OSRM**, **GraphHopper**, **Valhalla** | open-source road routing on OpenStreetMap (contraction hierarchies, multi-level Dijkstra) |
| **pgRouting** | shortest paths inside PostgreSQL |
| **Neo4j** graph algorithms | graph databases |
| Game engines (Unity NavMesh, Unreal) | A* over navigation meshes |
| OSPF and IS-IS routers | the internet's own Dijkstra, run on every link change |

### Common mistakes

| Mistake | What happens |
|---|---|
| **Dijkstra with negative edges** | It settles a place too early and gives a wrong answer, with no error. Use Bellman-Ford, or reweight (Johnson's algorithm). |
| **An A* estimate that overstates** | A* returns a path quickly, but not the shortest one. Straight-line distance is safe on maps; "number of steps times the longest road" is not. |
| **Marking places visited when pushed, not when popped** | The first route found to a place is not always the shortest; Dijkstra must finalize on pop. |
| **Using Dijkstra when every edge is equal** | Correct, but a plain queue (BFS) is simpler and faster. |
| **"Infinity" as a large int that overflows** | `INT_MAX + w` wraps to a negative number and wins every comparison. Use a wider type or check before adding. |
| **Directed vs undirected mixed up** | A one-way street added as two-way gives routes that drive the wrong way. |
| **Floyd-Warshall on a big graph** | $V^3$ is a trillion steps at 10,000 places. Run Dijkstra from each source instead, or only from those you need. |

### Best practices

- Model first: what is a place, what is a road, what does "length" mean (time, distance, cost)?
- Use a library for anything real; write Dijkstra yourself once, to understand it.
- For many queries on a fixed map, preprocess (contraction hierarchies) instead of searching from scratch.
- Test on a tiny graph whose answers you know, including unreachable places and ties.

### Learn it properly

- [Algorithms book, chapter 15](../books/algorithms/15-Graphs-and-Graph-Search.md) and [chapter 16](../books/algorithms/16-Shortest-Paths.md): proofs, the cost of each method, and the speed-up techniques
- [AI book, chapter 4](../books/ai/04-Heuristic-Search.md): A* and how to design good estimates
- The [Graphs](../graphs/index.md) pages: each algorithm with code in three languages and an animation on a map of Mars

## Now and next

*Last checked: 4 November 2026.*

- **Dijkstra is "universally optimal".** Haeupler and others (2024) proved that Dijkstra with a suitable heap is as fast as any algorithm can be on every graph, not only the worst one.
- **The sorting barrier fell.** Duan and others (2025) found a shortest-path algorithm for directed graphs with non-negative lengths in $O(m \log^{2/3} n)$ time, the first to beat Dijkstra's $O(m + n \log n)$ on sparse graphs.
- **Negative lengths in near-linear time.** Bernstein, Nanongkai and Wulff-Nilsen (2022) gave an almost-linear algorithm where Bellman-Ford takes $O(VE)$.
- **Routing at scale** keeps moving toward live traffic: routes recomputed as road speeds change, which favours methods that re-weight quickly (customizable route planning).
