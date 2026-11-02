# Graphs

A **graph** is a set of things (vertices, or nodes) and links between them (edges). Roads between towns,
friendships, web pages and their links, tasks and what they depend on, the moves of a puzzle: all graphs. Edges
can be **directed** (one-way) or **undirected**, and **weighted** (a length or cost) or not.

## Storing a graph

| Way | Memory | Is $u$–$v$ an edge? | List $u$'s neighbours | Best for |
|---|---|---|---|---|
| **Adjacency list:** for each vertex, a list of its neighbours | $O(V + E)$ | $O(\deg u)$ | $O(\deg u)$ | almost everything; used on this site |
| **Adjacency matrix:** a $V \times V$ table of 0/1 or weights | $O(V^2)$ | $O(1)$ | $O(V)$ | dense graphs, [Floyd-Warshall](floyd-warshall.md) |
| **Edge list:** just the list of $(u, v, w)$ | $O(E)$ | $O(E)$ | $O(E)$ | [Kruskal](kruskal.md), [Bellman-Ford](bellman-ford.md) |

$V$ is the number of vertices and $E$ the number of edges. A simple graph has at most $V(V-1)/2$ undirected edges.

## The algorithms on this site

| Algorithm | Answers | Time | Notes |
|---|---|---|---|
| [Breadth-first search](bfs.md) | fewest edges from a start; connected parts | $O(V + E)$ | uses a queue |
| [Depth-first search](dfs.md) | reachability, components, cycles; the base of many others | $O(V + E)$ | uses a stack or recursion |
| [Topological sort](topological-sort.md) | an order that respects all arrows (tasks, courses) | $O(V + E)$ | directed graphs without cycles |
| [Dijkstra](dijkstra.md) | shortest paths from one start, weights $\ge 0$ | $O((V + E)\log V)$ | uses a heap |
| [Bellman-Ford](bellman-ford.md) | shortest paths with negative weights; finds negative cycles | $O(VE)$ | |
| [Floyd-Warshall](floyd-warshall.md) | shortest paths between **all** pairs | $O(V^3)$ | three nested loops |
| [Kruskal](kruskal.md) | minimum spanning tree | $O(E \log E)$ | sort edges + union-find |
| [Prim](prim.md) | minimum spanning tree | $O(E \log V)$ | grow one tree with a heap |
| [Strongly connected components](scc.md) | groups where everyone reaches everyone (directed) | $O(V + E)$ | two DFS passes |

## Which shortest-path algorithm?

- **No weights** (every edge costs 1): [BFS](bfs.md).
- **Weights 0 or 1 only:** BFS with a deque (0-1 BFS).
- **Non-negative weights, one start:** [Dijkstra](dijkstra.md).
- **Negative weights, one start:** [Bellman-Ford](bellman-ford.md).
- **All pairs, a few hundred vertices:** [Floyd-Warshall](floyd-warshall.md).
- **A directed graph with no cycles:** relax edges in [topological order](topological-sort.md), $O(V + E)$, even
  with negative weights.
