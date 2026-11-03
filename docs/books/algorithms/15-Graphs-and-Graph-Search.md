# 15. Graphs and graph search

*Roads between towns, links between web pages, prerequisites between courses, moves between positions in a
puzzle: a huge number of problems are really about things joined to other things. This chapter gives that shape a
name, a graph, and builds the two ways of walking through one: breadth-first search, which explores in rings and
finds shortest routes, and depth-first search, which goes as deep as it can and then backs up. From those two walks
you will build, and prove correct, a whole toolbox: shortest paths when every step costs the same, ordering tasks
that depend on each other, finding the tightly knit parts of a network, finding the single links whose failure cuts
it in two, two-colouring, and Euler's walk over every bridge exactly once.*

!!! abstract "In this chapter"
    **You will learn:**

    - the words of graph theory (vertex, edge, degree, path, cycle, connected, directed, weighted) and the two
      standard ways to store a graph, with their costs
    - breadth-first search, and a proof that it finds shortest paths in an unweighted graph in $O(V + E)$ time
    - depth-first search: discovery and finish times, the four kinds of edge, the parenthesis and white-path theorems
    - topological sorting two ways (by finish times and by Kahn's in-degree method), with proofs
    - strongly connected components by Kosaraju's two passes and by Tarjan's single pass with low-links
    - bridges and articulation points from the same low-link idea
    - two-colouring and odd cycles, and Euler tours: Euler's 1736 theorem and Hierholzer's linear-time algorithm

    **You need:** queues and stacks from [Chapter 4](04-Lists-Stacks-and-Queues.md), recursion and induction from
    [Chapter 3](03-Recursion-and-Induction.md), and $O$-notation from [Chapter 2](02-Measuring-Cost.md).

    **Levels:** 15.1 and 15.2 are beginner; 15.3, 15.4 and 15.7 are intermediate; 15.5 and 15.6 are advanced.

## 15.1 Graphs: the words and the data structures

Here is a question you could ask about any map. Given a list of towns and a list of roads, each road joining two
towns, can you drive from town A to town H? If so, what is the route with the fewest roads? The towns and roads
could just as well be computers and cables, people and friendships, or the squares of a maze and the openings
between them. The question only cares about **which things are joined to which**. That is exactly what a graph
records.

**Definition.** A **graph** $G = (V, E)$ is a set $V$ of **vertices** (also called nodes) and a set $E$ of
**edges**. In an **undirected** graph each edge is an unordered pair $\{u, v\}$ of vertices: the road goes both
ways. In a **directed** graph (a **digraph**) each edge is an ordered pair $(u, v)$, written $u \to v$: a one-way
street, a link from page $u$ to page $v$, "course $u$ must come before course $v$". We write $n = |V|$ for the
number of vertices and $m = |E|$ for the number of edges; running times are usually written with $V$ and $E$
themselves, as in $O(V + E)$, meaning $O(|V| + |E|)$.

A few more words, each of which you will need:

- Two vertices joined by an edge are **adjacent**, or **neighbours**. The edge is **incident** to both.
- The **degree** of a vertex in an undirected graph is the number of edges touching it. In a directed graph a vertex
  has an **out-degree** (edges leaving) and an **in-degree** (edges arriving).
- A **path** is a sequence of vertices $v_0, v_1, \dots, v_k$ in which each consecutive pair is joined by an edge;
  its **length** is the number of edges, $k$. A path is **simple** if no vertex repeats.
- A **cycle** is a path of length at least 1 (at least 3 in an undirected simple graph) that starts and ends at the
  same vertex and otherwise does not repeat vertices.
- An undirected graph is **connected** if there is a path between every pair of vertices. Its maximal connected
  pieces are its **connected components**.
- A **weighted** graph gives each edge a number $w(u, v)$: a length, a cost, a time, a capacity. This chapter's
  graphs are unweighted (or, equivalently, every edge has weight 1); [Chapter 16](16-Shortest-Paths.md) handles
  weights.
- A **simple** graph has no edge from a vertex to itself (a **loop**) and at most one edge between any two
  vertices. A **multigraph** allows several **parallel** edges, which we will need for Euler's bridges in 15.7.
- A **tree** is a connected undirected graph with no cycle. A **DAG** is a directed acyclic graph: a directed graph
  with no directed cycle.

One fact is worth proving at once because it is used again and again.

**Handshake lemma.** In any undirected graph, the degrees add up to twice the number of edges:

$$
\sum_{v \in V} \deg(v) = 2|E|.
$$

*Proof.* Each edge $\{u, v\}$ adds exactly 1 to the degree of $u$ and 1 to the degree of $v$, so it adds exactly 2
to the sum. Summing over all edges gives $2|E|$. (A loop, if allowed, adds 2 to the degree of its one vertex, so
the lemma still holds.) $\square$

A consequence: the number of vertices of odd degree is always even, since the sum must be even. Euler will need
that in 15.7.

### Storing a graph

A computer needs the graph as data. There are two standard choices, shown in Figure 15.1 for the graph we will use
throughout 15.1 and 15.2.

<figure class="mars-fig" markdown="0">
<svg viewBox="0 0 700 250" role="img" aria-label="An undirected graph with eight vertices A to H and ten edges, its adjacency list and its adjacency matrix">
<line x1="52.1" y1="119.6" x2="97.9" y2="80.4" stroke="currentColor" stroke-width="1.5"/>
<line x1="52.1" y1="140.4" x2="97.9" y2="179.6" stroke="currentColor" stroke-width="1.5"/>
<line x1="125.5" y1="66.1" x2="174.5" y2="53.9" stroke="currentColor" stroke-width="1.5"/>
<line x1="121.3" y1="81.3" x2="178.7" y2="138.7" stroke="currentColor" stroke-width="1.5"/>
<line x1="124.3" y1="182.8" x2="175.7" y2="157.2" stroke="currentColor" stroke-width="1.5"/>
<line x1="204.3" y1="57.2" x2="255.7" y2="82.8" stroke="currentColor" stroke-width="1.5"/>
<line x1="202.8" y1="140.4" x2="257.2" y2="99.6" stroke="currentColor" stroke-width="1.5"/>
<line x1="203.6" y1="158.5" x2="256.4" y2="191.5" stroke="currentColor" stroke-width="1.5"/>
<line x1="282.1" y1="100.4" x2="327.9" y2="139.6" stroke="currentColor" stroke-width="1.5"/>
<line x1="283.0" y1="190.7" x2="327.0" y2="159.3" stroke="currentColor" stroke-width="1.5"/>
<text x="440" y="22" font-size="13" text-anchor="middle" fill="currentColor" font-weight="bold">adjacency list</text>
<text x="395" y="48" font-size="13" text-anchor="start" fill="currentColor" font-family="monospace">A: B C</text>
<text x="395" y="72" font-size="13" text-anchor="start" fill="currentColor" font-family="monospace">B: A D E</text>
<text x="395" y="96" font-size="13" text-anchor="start" fill="currentColor" font-family="monospace">C: A E</text>
<text x="395" y="120" font-size="13" text-anchor="start" fill="currentColor" font-family="monospace">D: B F</text>
<text x="395" y="144" font-size="13" text-anchor="start" fill="currentColor" font-family="monospace">E: B C F G</text>
<text x="395" y="168" font-size="13" text-anchor="start" fill="currentColor" font-family="monospace">F: D E H</text>
<text x="395" y="192" font-size="13" text-anchor="start" fill="currentColor" font-family="monospace">G: E H</text>
<text x="395" y="216" font-size="13" text-anchor="start" fill="currentColor" font-family="monospace">H: F G</text>
<text x="605" y="22" font-size="13" text-anchor="middle" fill="currentColor" font-weight="bold">adjacency matrix</text>
<text x="546" y="44" font-size="11" text-anchor="middle" fill="currentColor" font-family="monospace">A</text>
<text x="562" y="44" font-size="11" text-anchor="middle" fill="currentColor" font-family="monospace">B</text>
<text x="578" y="44" font-size="11" text-anchor="middle" fill="currentColor" font-family="monospace">C</text>
<text x="594" y="44" font-size="11" text-anchor="middle" fill="currentColor" font-family="monospace">D</text>
<text x="610" y="44" font-size="11" text-anchor="middle" fill="currentColor" font-family="monospace">E</text>
<text x="626" y="44" font-size="11" text-anchor="middle" fill="currentColor" font-family="monospace">F</text>
<text x="642" y="44" font-size="11" text-anchor="middle" fill="currentColor" font-family="monospace">G</text>
<text x="658" y="44" font-size="11" text-anchor="middle" fill="currentColor" font-family="monospace">H</text>
<text x="526" y="64" font-size="11" text-anchor="middle" fill="currentColor" font-family="monospace">A</text>
<text x="546" y="64" font-size="11" text-anchor="middle" fill="currentColor" font-family="monospace">·</text>
<text x="562" y="64" font-size="11" text-anchor="middle" fill="#eea66f" font-family="monospace">1</text>
<text x="578" y="64" font-size="11" text-anchor="middle" fill="#eea66f" font-family="monospace">1</text>
<text x="594" y="64" font-size="11" text-anchor="middle" fill="currentColor" font-family="monospace">·</text>
<text x="610" y="64" font-size="11" text-anchor="middle" fill="currentColor" font-family="monospace">·</text>
<text x="626" y="64" font-size="11" text-anchor="middle" fill="currentColor" font-family="monospace">·</text>
<text x="642" y="64" font-size="11" text-anchor="middle" fill="currentColor" font-family="monospace">·</text>
<text x="658" y="64" font-size="11" text-anchor="middle" fill="currentColor" font-family="monospace">·</text>
<text x="526" y="86" font-size="11" text-anchor="middle" fill="currentColor" font-family="monospace">B</text>
<text x="546" y="86" font-size="11" text-anchor="middle" fill="#eea66f" font-family="monospace">1</text>
<text x="562" y="86" font-size="11" text-anchor="middle" fill="currentColor" font-family="monospace">·</text>
<text x="578" y="86" font-size="11" text-anchor="middle" fill="currentColor" font-family="monospace">·</text>
<text x="594" y="86" font-size="11" text-anchor="middle" fill="#eea66f" font-family="monospace">1</text>
<text x="610" y="86" font-size="11" text-anchor="middle" fill="#eea66f" font-family="monospace">1</text>
<text x="626" y="86" font-size="11" text-anchor="middle" fill="currentColor" font-family="monospace">·</text>
<text x="642" y="86" font-size="11" text-anchor="middle" fill="currentColor" font-family="monospace">·</text>
<text x="658" y="86" font-size="11" text-anchor="middle" fill="currentColor" font-family="monospace">·</text>
<text x="526" y="108" font-size="11" text-anchor="middle" fill="currentColor" font-family="monospace">C</text>
<text x="546" y="108" font-size="11" text-anchor="middle" fill="#eea66f" font-family="monospace">1</text>
<text x="562" y="108" font-size="11" text-anchor="middle" fill="currentColor" font-family="monospace">·</text>
<text x="578" y="108" font-size="11" text-anchor="middle" fill="currentColor" font-family="monospace">·</text>
<text x="594" y="108" font-size="11" text-anchor="middle" fill="currentColor" font-family="monospace">·</text>
<text x="610" y="108" font-size="11" text-anchor="middle" fill="#eea66f" font-family="monospace">1</text>
<text x="626" y="108" font-size="11" text-anchor="middle" fill="currentColor" font-family="monospace">·</text>
<text x="642" y="108" font-size="11" text-anchor="middle" fill="currentColor" font-family="monospace">·</text>
<text x="658" y="108" font-size="11" text-anchor="middle" fill="currentColor" font-family="monospace">·</text>
<text x="526" y="130" font-size="11" text-anchor="middle" fill="currentColor" font-family="monospace">D</text>
<text x="546" y="130" font-size="11" text-anchor="middle" fill="currentColor" font-family="monospace">·</text>
<text x="562" y="130" font-size="11" text-anchor="middle" fill="#eea66f" font-family="monospace">1</text>
<text x="578" y="130" font-size="11" text-anchor="middle" fill="currentColor" font-family="monospace">·</text>
<text x="594" y="130" font-size="11" text-anchor="middle" fill="currentColor" font-family="monospace">·</text>
<text x="610" y="130" font-size="11" text-anchor="middle" fill="currentColor" font-family="monospace">·</text>
<text x="626" y="130" font-size="11" text-anchor="middle" fill="#eea66f" font-family="monospace">1</text>
<text x="642" y="130" font-size="11" text-anchor="middle" fill="currentColor" font-family="monospace">·</text>
<text x="658" y="130" font-size="11" text-anchor="middle" fill="currentColor" font-family="monospace">·</text>
<text x="526" y="152" font-size="11" text-anchor="middle" fill="currentColor" font-family="monospace">E</text>
<text x="546" y="152" font-size="11" text-anchor="middle" fill="currentColor" font-family="monospace">·</text>
<text x="562" y="152" font-size="11" text-anchor="middle" fill="#eea66f" font-family="monospace">1</text>
<text x="578" y="152" font-size="11" text-anchor="middle" fill="#eea66f" font-family="monospace">1</text>
<text x="594" y="152" font-size="11" text-anchor="middle" fill="currentColor" font-family="monospace">·</text>
<text x="610" y="152" font-size="11" text-anchor="middle" fill="currentColor" font-family="monospace">·</text>
<text x="626" y="152" font-size="11" text-anchor="middle" fill="#eea66f" font-family="monospace">1</text>
<text x="642" y="152" font-size="11" text-anchor="middle" fill="#eea66f" font-family="monospace">1</text>
<text x="658" y="152" font-size="11" text-anchor="middle" fill="currentColor" font-family="monospace">·</text>
<text x="526" y="174" font-size="11" text-anchor="middle" fill="currentColor" font-family="monospace">F</text>
<text x="546" y="174" font-size="11" text-anchor="middle" fill="currentColor" font-family="monospace">·</text>
<text x="562" y="174" font-size="11" text-anchor="middle" fill="currentColor" font-family="monospace">·</text>
<text x="578" y="174" font-size="11" text-anchor="middle" fill="currentColor" font-family="monospace">·</text>
<text x="594" y="174" font-size="11" text-anchor="middle" fill="#eea66f" font-family="monospace">1</text>
<text x="610" y="174" font-size="11" text-anchor="middle" fill="#eea66f" font-family="monospace">1</text>
<text x="626" y="174" font-size="11" text-anchor="middle" fill="currentColor" font-family="monospace">·</text>
<text x="642" y="174" font-size="11" text-anchor="middle" fill="currentColor" font-family="monospace">·</text>
<text x="658" y="174" font-size="11" text-anchor="middle" fill="#eea66f" font-family="monospace">1</text>
<text x="526" y="196" font-size="11" text-anchor="middle" fill="currentColor" font-family="monospace">G</text>
<text x="546" y="196" font-size="11" text-anchor="middle" fill="currentColor" font-family="monospace">·</text>
<text x="562" y="196" font-size="11" text-anchor="middle" fill="currentColor" font-family="monospace">·</text>
<text x="578" y="196" font-size="11" text-anchor="middle" fill="currentColor" font-family="monospace">·</text>
<text x="594" y="196" font-size="11" text-anchor="middle" fill="currentColor" font-family="monospace">·</text>
<text x="610" y="196" font-size="11" text-anchor="middle" fill="#eea66f" font-family="monospace">1</text>
<text x="626" y="196" font-size="11" text-anchor="middle" fill="currentColor" font-family="monospace">·</text>
<text x="642" y="196" font-size="11" text-anchor="middle" fill="currentColor" font-family="monospace">·</text>
<text x="658" y="196" font-size="11" text-anchor="middle" fill="#eea66f" font-family="monospace">1</text>
<text x="526" y="218" font-size="11" text-anchor="middle" fill="currentColor" font-family="monospace">H</text>
<text x="546" y="218" font-size="11" text-anchor="middle" fill="currentColor" font-family="monospace">·</text>
<text x="562" y="218" font-size="11" text-anchor="middle" fill="currentColor" font-family="monospace">·</text>
<text x="578" y="218" font-size="11" text-anchor="middle" fill="currentColor" font-family="monospace">·</text>
<text x="594" y="218" font-size="11" text-anchor="middle" fill="currentColor" font-family="monospace">·</text>
<text x="610" y="218" font-size="11" text-anchor="middle" fill="currentColor" font-family="monospace">·</text>
<text x="626" y="218" font-size="11" text-anchor="middle" fill="#eea66f" font-family="monospace">1</text>
<text x="642" y="218" font-size="11" text-anchor="middle" fill="#eea66f" font-family="monospace">1</text>
<text x="658" y="218" font-size="11" text-anchor="middle" fill="currentColor" font-family="monospace">·</text>
<circle cx="40" cy="130" r="16" fill="#9cc9ea" fill-opacity="0.55" stroke="currentColor" stroke-width="1.5"/>
<text x="40" y="134.9" font-size="14" text-anchor="middle" fill="currentColor">A</text>
<circle cx="110" cy="70" r="16" fill="#9cc9ea" fill-opacity="0.55" stroke="currentColor" stroke-width="1.5"/>
<text x="110" y="74.9" font-size="14" text-anchor="middle" fill="currentColor">B</text>
<circle cx="110" cy="190" r="16" fill="#9cc9ea" fill-opacity="0.55" stroke="currentColor" stroke-width="1.5"/>
<text x="110" y="194.9" font-size="14" text-anchor="middle" fill="currentColor">C</text>
<circle cx="190" cy="50" r="16" fill="#9cc9ea" fill-opacity="0.55" stroke="currentColor" stroke-width="1.5"/>
<text x="190" y="54.9" font-size="14" text-anchor="middle" fill="currentColor">D</text>
<circle cx="190" cy="150" r="16" fill="#9cc9ea" fill-opacity="0.55" stroke="currentColor" stroke-width="1.5"/>
<text x="190" y="154.9" font-size="14" text-anchor="middle" fill="currentColor">E</text>
<circle cx="270" cy="90" r="16" fill="#9cc9ea" fill-opacity="0.55" stroke="currentColor" stroke-width="1.5"/>
<text x="270" y="94.9" font-size="14" text-anchor="middle" fill="currentColor">F</text>
<circle cx="270" cy="200" r="16" fill="#9cc9ea" fill-opacity="0.55" stroke="currentColor" stroke-width="1.5"/>
<text x="270" y="204.9" font-size="14" text-anchor="middle" fill="currentColor">G</text>
<circle cx="340" cy="150" r="16" fill="#9cc9ea" fill-opacity="0.55" stroke="currentColor" stroke-width="1.5"/>
<text x="340" y="154.9" font-size="14" text-anchor="middle" fill="currentColor">H</text>
</svg>
<figcaption>Figure 15.1. The chapter's first graph three ways: as a drawing, as an adjacency list (each vertex with the list of its neighbours) and as an adjacency matrix (row u, column v holds 1 when u and v are joined). The list uses space for 8 vertices and 20 list entries; the matrix always uses 8 × 8 = 64 cells.</figcaption>
</figure>

An **adjacency matrix** is an $n \times n$ table $M$ with $M[u][v] = 1$ if $u \to v$ is an edge (or $\{u,v\}$ for
undirected graphs, which makes the matrix symmetric) and 0 otherwise; for weighted graphs store the weight
instead. It answers "is there an edge from $u$ to $v$?" in $O(1)$ time, but it always takes $\Theta(V^2)$ space,
and listing the neighbours of $u$ takes $\Theta(V)$ time, however few there are.

An **adjacency list** keeps, for each vertex, a list of its neighbours. It takes $\Theta(V + E)$ space: one list
head per vertex and, by the handshake lemma, $2|E|$ entries in an undirected graph ($|E|$ in a directed one).
Listing the neighbours of $u$ takes $O(\deg u)$ time, which is as fast as anyone could hope. Asking whether one
particular edge exists takes $O(\deg u)$ by scanning, or $O(1)$ expected if each list is a hash set
([Chapter 7](07-Searching-and-Hashing.md)).

| Operation | Adjacency matrix | Adjacency list |
|---|---|---|
| Space | $\Theta(V^2)$ | $\Theta(V + E)$ |
| Is $u$–$v$ an edge? | $O(1)$ | $O(\deg u)$ |
| List the neighbours of $u$ | $\Theta(V)$ | $O(\deg u)$ |
| Visit every edge once | $\Theta(V^2)$ | $\Theta(V + E)$ |

Which is better depends on how many edges there are. A graph with $V$ vertices has at most $V(V-1)/2$ undirected
edges. A graph with close to that many is **dense**; one with $E = O(V)$, or at least far fewer than $V^2$, is
**sparse**. Real graphs are nearly always sparse. A road network has a few roads at each junction; a social network
with a billion people does not give each person a billion friends. For a sparse graph with a million vertices the
matrix needs $10^{12}$ cells, which no laptop holds, while the list needs a few million entries. **So the algorithms
in this chapter all use adjacency lists**, and their running times come out as $O(V + E)$, which is linear in the
size of the input. You cannot do better if you have to look at every edge.

In Python, an adjacency list is simply a dictionary from each vertex to a list of its neighbours. The program for
this chapter builds the graph of Figure 15.1 that way and prints both forms; its output starts like this:

```
  A: B C
  B: A D E
  ...
  edges: 10  degree sum: 20
```

The degree sum is 20, twice the 10 edges, as the handshake lemma says it must be.

**A remark on order.** An adjacency list stores the neighbours in some order, and a search will visit them in that
order. The answers that matter (distances, components, whether a cycle exists) never depend on it, but the exact
trace does. In this chapter neighbours are kept in alphabetical or numerical order so that you can follow every
trace by hand.

## 15.2 Breadth-first search and shortest paths

Back to the question: what is the route from A to H in Figure 15.1 with the fewest edges? You could list every path
and pick the shortest, but even small graphs can have exponentially many paths. Here is a much better idea.
Everything one edge from A is at distance 1. Everything one edge from a distance-1 vertex, that has not already been
found, is at distance 2. And so on, outwards in rings. That idea is **breadth-first search** (BFS).

The **distance** $\delta(s, v)$ from $s$ to $v$ is the number of edges on a shortest path from $s$ to $v$, or
$\infty$ if there is no path at all.

To process vertices ring by ring, BFS uses a **queue** (first in, first out; [Chapter 4](04-Lists-Stacks-and-Queues.md)).
A vertex joins the back of the queue when it is first seen and is explored when it reaches the front.

```text
BFS(G, s):
    dist[v] = None and parent[v] = None for every v
    dist[s] = 0
    queue = [s]
    while queue is not empty:
        u = take from the front of queue
        for each neighbour v of u:
            if dist[v] is None:          # first time we see v
                dist[v] = dist[u] + 1
                parent[v] = u
                add v to the back of queue
```

The **parent** of $v$ is the vertex from which $v$ was first seen. Following parents back from any vertex to $s$
traces a path; the parent edges together form the **BFS tree**.

### A trace by hand

Run BFS from A on the graph of Figure 15.1. Each row shows the vertex taken from the queue, the new vertices it
discovers, and the queue afterwards.

| Step | Take | Newly found (distance) | Queue after |
|---|---|---|---|
| 0 | | A (0) | A |
| 1 | A | B (1), C (1) | B C |
| 2 | B | D (2), E (2); A already seen | C D E |
| 3 | C | none (A, E already seen) | D E |
| 4 | D | F (3) | E F |
| 5 | E | G (3) | F G |
| 6 | F | H (4) | G H |
| 7 | G | none | H |
| 8 | H | none | empty |

The parents are B←A, C←A, D←B, E←B, F←D, G←E, H←F. Walking back from H: H, F, D, B, A, so the shortest route is
A, B, D, F, H with 4 edges. Figure 15.2 draws the result.

<figure class="mars-fig" markdown="0">
<svg viewBox="0 0 560 250" role="img" aria-label="Breadth-first search from A: vertices arranged in columns by distance 0 to 4, tree edges thick, other edges dashed">
<line x1="64.6" y1="103.4" x2="145.4" y2="66.6" stroke="#eea66f" stroke-width="3.5"/>
<line x1="64.6" y1="116.6" x2="145.4" y2="153.4" stroke="#eea66f" stroke-width="3.5"/>
<line x1="176.0" y1="60.0" x2="254.0" y2="60.0" stroke="#eea66f" stroke-width="3.5"/>
<line x1="171.8" y1="70.8" x2="258.2" y2="149.2" stroke="#eea66f" stroke-width="3.5"/>
<line x1="176.0" y1="160.0" x2="254.0" y2="160.0" stroke="currentColor" stroke-width="1.5" stroke-dasharray="5 4"/>
<line x1="286.0" y1="60.0" x2="364.0" y2="60.0" stroke="#eea66f" stroke-width="3.5"/>
<line x1="281.8" y1="149.2" x2="368.2" y2="70.8" stroke="currentColor" stroke-width="1.5" stroke-dasharray="5 4"/>
<line x1="286.0" y1="160.0" x2="364.0" y2="160.0" stroke="#eea66f" stroke-width="3.5"/>
<line x1="394.6" y1="66.6" x2="475.4" y2="103.4" stroke="#eea66f" stroke-width="3.5"/>
<line x1="394.6" y1="153.4" x2="475.4" y2="116.6" stroke="currentColor" stroke-width="1.5" stroke-dasharray="5 4"/>
<text x="50" y="215" font-size="12" text-anchor="middle" fill="currentColor">distance 0</text>
<text x="160" y="215" font-size="12" text-anchor="middle" fill="currentColor">distance 1</text>
<text x="270" y="215" font-size="12" text-anchor="middle" fill="currentColor">distance 2</text>
<text x="380" y="215" font-size="12" text-anchor="middle" fill="currentColor">distance 3</text>
<text x="490" y="215" font-size="12" text-anchor="middle" fill="currentColor">distance 4</text>
<line x1="20" y1="195" x2="540" y2="195" stroke="currentColor" stroke-opacity="0.4"/>
<text x="280" y="240" font-size="12" text-anchor="middle" fill="currentColor">thick: BFS tree (parent pointers)     dashed: edges BFS saw but did not use</text>
<circle cx="50" cy="110" r="16" fill="#eea66f" fill-opacity="0.55" stroke="currentColor" stroke-width="1.5"/>
<text x="50" y="114.9" font-size="14" text-anchor="middle" fill="currentColor">A</text>
<circle cx="160" cy="60" r="16" fill="#9cc9ea" fill-opacity="0.55" stroke="currentColor" stroke-width="1.5"/>
<text x="160" y="64.9" font-size="14" text-anchor="middle" fill="currentColor">B</text>
<circle cx="160" cy="160" r="16" fill="#9cc9ea" fill-opacity="0.55" stroke="currentColor" stroke-width="1.5"/>
<text x="160" y="164.9" font-size="14" text-anchor="middle" fill="currentColor">C</text>
<circle cx="270" cy="60" r="16" fill="#9cc9ea" fill-opacity="0.55" stroke="currentColor" stroke-width="1.5"/>
<text x="270" y="64.9" font-size="14" text-anchor="middle" fill="currentColor">D</text>
<circle cx="270" cy="160" r="16" fill="#9cc9ea" fill-opacity="0.55" stroke="currentColor" stroke-width="1.5"/>
<text x="270" y="164.9" font-size="14" text-anchor="middle" fill="currentColor">E</text>
<circle cx="380" cy="60" r="16" fill="#9cc9ea" fill-opacity="0.55" stroke="currentColor" stroke-width="1.5"/>
<text x="380" y="64.9" font-size="14" text-anchor="middle" fill="currentColor">F</text>
<circle cx="380" cy="160" r="16" fill="#9cc9ea" fill-opacity="0.55" stroke="currentColor" stroke-width="1.5"/>
<text x="380" y="164.9" font-size="14" text-anchor="middle" fill="currentColor">G</text>
<circle cx="490" cy="110" r="16" fill="#9cc9ea" fill-opacity="0.55" stroke="currentColor" stroke-width="1.5"/>
<text x="490" y="114.9" font-size="14" text-anchor="middle" fill="currentColor">H</text>
</svg>
<figcaption>Figure 15.2. BFS from A sorts the vertices into layers by distance. Every thick edge is a parent pointer; following them back from H gives the shortest path A, B, D, F, H. No edge skips a layer: an edge joins vertices whose distances differ by at most 1.</figcaption>
</figure>

### Why BFS is correct

It is not obvious that "first seen" means "seen by a shortest path". A vertex could, in principle, be found early by
a long path and only later be reachable by a short one. The proof that this cannot happen rests on one property of
the queue.

**Lemma 15.1 (the queue holds at most two neighbouring layers).** At every moment during BFS, if the queue holds
$u_1, u_2, \dots, u_r$ from front to back, then $\mathrm{dist}[u_1] \le \mathrm{dist}[u_2] \le \dots \le
\mathrm{dist}[u_r] \le \mathrm{dist}[u_1] + 1$.

*Proof.* By induction on the number of queue operations. At the start the queue holds only $s$, and the claim is
true. Two things change the queue. *Taking* $u_1$ from the front: the rest is still sorted, and the new front
$u_2$ has $\mathrm{dist}[u_2] \ge \mathrm{dist}[u_1]$, so the bound $\mathrm{dist}[u_r] \le \mathrm{dist}[u_1] + 1
\le \mathrm{dist}[u_2] + 1$ still holds. *Adding* $v$ at the back while exploring $u$: the vertex $u$ was just taken
from the front, so every vertex still in the queue has distance between $\mathrm{dist}[u]$ and $\mathrm{dist}[u]+1$
by the induction hypothesis applied just before $u$ was taken. The new $v$ gets $\mathrm{dist}[u] + 1$, which is at
least every value in the queue and at most the new front plus 1. $\square$

So vertices leave the queue in non-decreasing order of the labels `dist`. Now the theorem.

**Theorem 15.2 (BFS finds shortest paths).** When BFS from $s$ finishes, every vertex $v$ reachable from $s$ has
$\mathrm{dist}[v] = \delta(s, v)$, and following parent pointers from $v$ gives a shortest path. Vertices not
reachable keep the label None.

*Proof.* First, $\mathrm{dist}[v] \ge \delta(s, v)$ whenever it is set: by induction, $\mathrm{dist}[v] =
\mathrm{dist}[u] + 1$ and parent $u$ was itself reached by a path of $\mathrm{dist}[u]$ edges, so there is a path
of $\mathrm{dist}[v]$ edges to $v$, and the shortest path is no longer than that. In the same way, BFS only ever
labels vertices it reaches along edges from $s$, so an unreachable vertex is never labelled.

Now suppose, for a contradiction, that some reachable vertex ends with the wrong label, and among all such vertices
pick $v$ with the smallest true distance $\delta(s, v) = k$. Then $v \neq s$, so $k \ge 1$. Let $u$ be the
vertex just before $v$ on a shortest path from $s$; then $\delta(s, u) = k - 1$, and by the choice of $v$, $u$ has
the right label $\mathrm{dist}[u] = k - 1$. Since $u$ is labelled, it entered the queue and was eventually taken
out and explored. Look at the moment BFS explores $u$ and examines the edge to $v$.

- If $v$ is unlabelled at that moment, BFS sets $\mathrm{dist}[v] = k$, which is correct. Contradiction.
- If $v$ is already labelled, it was labelled by some vertex $u'$ taken from the queue no later than $u$. By
  Lemma 15.1, $\mathrm{dist}[u'] \le \mathrm{dist}[u] = k - 1$, so $\mathrm{dist}[v] = \mathrm{dist}[u'] + 1 \le
  k$. Combined with $\mathrm{dist}[v] \ge \delta(s,v) = k$, the label is exactly $k$. Contradiction.

So every reachable vertex is labelled correctly. The parent of $v$ has label one less, so walking up the parents
reaches $s$ in exactly $\mathrm{dist}[v]$ steps: a shortest path. $\square$

A useful corollary, visible in Figure 15.2: in an undirected graph, the two ends of any edge have BFS distances that
differ by at most 1. (If $\{u,v\}$ is an edge, $\delta(s,v) \le \delta(s,u) + 1$ by going through $u$, and the same
the other way round.) For a directed edge $u \to v$, only $\delta(s,v) \le \delta(s,u) + 1$ holds; the edge can go
back to a much closer vertex.

### Running time

**Theorem 15.3.** BFS runs in $O(V + E)$ time with an adjacency list.

*Proof.* Each vertex enters the queue at most once, because it is added only when its label is None and is labelled
at the same moment. So there are at most $V$ queue operations of each kind, each $O(1)$. Each vertex $u$ is
explored at most once, and exploring it scans its list in $O(1 + \deg u)$ time. The total over all vertices is
$O(V + \sum_u \deg u) = O(V + E)$ by the handshake lemma (or $O(V+E)$ directly for out-degrees in a digraph).
Setting up the arrays costs $O(V)$. $\square$

The full program is below, with the output for every section of this chapter. Its `bfs` function is the pseudocode
above, using `collections.deque` as the queue; a Python list with `pop(0)` would make each removal cost $O(n)$ and
the whole search quadratic.

```python
--8<-- "books/algorithms/ch15_graph_search.py"
```

```
== 15.1 adjacency list and matrix ==
  A: B C
  B: A D E
  C: A E
  D: B F
  E: B C F G
  F: D E H
  G: E H
  H: F G
     A B C D E F G H
  A  0 1 1 0 0 0 0 0
  B  1 0 0 1 1 0 0 0
  C  1 0 0 0 1 0 0 0
  D  0 1 0 0 0 1 0 0
  E  0 1 1 0 0 1 1 0
  F  0 0 0 1 1 0 0 1
  G  0 0 0 0 1 0 0 1
  H  0 0 0 0 0 1 1 0
  edges: 10  degree sum: 20
== 15.2 BFS from A ==
  take A: queue now B C
  take B: queue now C D E
  take C: queue now D E
  take D: queue now E F
  take E: queue now F G
  take F: queue now G H
  take G: queue now H
  take H: queue now (empty)
  dist   {'A': 0, 'B': 1, 'C': 1, 'D': 2, 'E': 2, 'F': 3, 'G': 3, 'H': 4}
  parent {'A': None, 'B': 'A', 'C': 'A', 'D': 'B', 'E': 'B', 'F': 'D', 'G': 'E', 'H': 'F'}
  path to H: A B D F H
== 15.3 DFS edge classes ==
  a: d= 1 f=10
  b: d= 2 f= 5
  c: d= 3 f= 4
  d: d= 6 f= 9
  e: d= 7 f= 8
  a->b: tree
  b->c: tree
  c->a: back
  a->c: forward
  a->d: tree
  d->c: cross
  d->e: tree
== 15.4 topological sort ==
  DFS : discrete intro data systems algos compilers theory
  Kahn: intro discrete data algos systems theory compilers
  cycle x->y->z->x: graph has a cycle
== 15.5 strongly connected components ==
  Kosaraju: [[1, 3, 2], [4, 6, 5], [7, 8]]
  Tarjan:   [[8, 7], [6, 5, 4], [3, 2, 1]]
  index {1: 0, 2: 1, 3: 2, 4: 3, 5: 4, 6: 5, 7: 6, 8: 7}
  low   {1: 0, 2: 0, 3: 0, 4: 3, 5: 3, 6: 3, 7: 6, 8: 6}
== 15.6 bridges and articulation points ==
  disc {'A': 0, 'B': 1, 'C': 2, 'D': 3, 'E': 4, 'F': 5, 'G': 6}
  low  {'A': 0, 'B': 0, 'C': 0, 'D': 3, 'E': 3, 'F': 3, 'G': 6}
  bridges: [('F', 'G'), ('C', 'D')]  articulation points: ['C', 'D', 'F']
== 15.7 bipartite, odd cycles, Euler tours ==
  cube bipartite: True sides: [0, 3, 5, 6] [1, 2, 4, 7]
  pentagon+tail: (False, [0, 1, 2, 3, 4])
  Konigsberg degrees: {'N': 3, 'I': 5, 'S': 3, 'E': 3} odd: 4
  envelope degrees: {1: 4, 2: 4, 3: 3, 4: 3, 5: 2}
  odd vertices: [3, 4] -> an Euler path must run between them
  circuit with extra edge: [3, 4, 2, 5, 1, 3, 4, 1, 2, 3]
  Euler path: [4, 2, 5, 1, 3, 4, 1, 2, 3] uses 8 edges
  Euler circuit of two triangles at 0: [0, 4, 3, 0, 2, 1, 0]
```

The reference page [Breadth-first search](../../graphs/bfs.md) has the same algorithm in Java and C++ and an
animation.

**Where BFS is used.** Any problem where every move costs the same: the fewest moves to solve a sliding puzzle
(each position is a vertex), the fewest steps across a grid map with obstacles, the fewest hops between two
computers, degrees of separation in a social network. Running BFS from every unseen vertex in turn also finds the
**connected components** of an undirected graph in $O(V + E)$ total: each BFS labels exactly one component. A
**multi-source BFS** starts with several vertices in the queue at distance 0 and finds, for every vertex, the
distance to the nearest source; it is how you compute "distance to the nearest charging station" on a grid in one
pass.

## 15.3 Depth-first search

*Level: intermediate.*

Picture exploring a cave system with a ball of string. You go down the first unexplored passage you see, then the
first unexplored passage from there, and so on, as deep as you can. When you reach a dead end, or every passage
leads somewhere you have already been, you follow the string back one junction and try the next passage there.
That is **depth-first search** (DFS). It is the oldest systematic search: a nineteenth-century French
engineer, Charles Pierre Trémaux, described essentially this method for escaping mazes, and Édouard Lucas
published it in 1882.

BFS answers "how far?". DFS answers structural questions: is there a cycle? In what order can these tasks be done?
Which parts of the network hang together? It does so through two timestamps that it records for each vertex.

```text
DFS(G):
    colour[v] = white for every v;  time = 0
    for each vertex u:
        if colour[u] == white: VISIT(u)

VISIT(u):
    time += 1;  d[u] = time;  colour[u] = grey     # discovered
    for each neighbour v of u:
        if colour[v] == white:
            parent[v] = u
            VISIT(v)
    colour[u] = black;  time += 1;  f[u] = time    # finished
```

The colours mean: **white**, not yet discovered; **grey**, discovered but not finished (it is on the current
recursion stack, the "string"); **black**, finished, with every neighbour fully explored. The **discovery time**
$d[u]$ is when $u$ turns grey, and the **finish time** $f[u]$ when it turns black. Times run from 1 to $2V$, each
value used once. Every vertex is visited exactly once and each adjacency list is scanned once, so, just as for BFS,
**DFS runs in $O(V + E)$ time**.

The parent edges form the **DFS forest**: one tree for each call of VISIT from the outer loop.

### The four kinds of edge

Every edge $u \to v$ of a directed graph lands in exactly one of four classes, decided by the colour of $v$ at the
moment DFS looks at the edge from $u$:

- **tree edge**: $v$ is white, and DFS goes to it through this edge;
- **back edge**: $v$ is grey, so $v$ is an ancestor of $u$ in the DFS tree (it is on the current stack);
- **forward edge**: $v$ is black and $d[u] < d[v]$, so $v$ is a descendant of $u$ found earlier by another route;
- **cross edge**: $v$ is black and $d[v] < d[u]$, so $v$ is in a branch that was finished before $u$ began.

Here is a trace on a small directed graph with edges a→b, a→c, a→d, b→c, c→a, d→c, d→e (neighbours in that order).

| Time | Event | Edge examined | Class |
|---|---|---|---|
| 1 | discover a | a→b, b white | tree |
| 2 | discover b | b→c, c white | tree |
| 3 | discover c | c→a, a grey | back |
| 4 | finish c | | |
| 5 | finish b | a→c, c black, $d[a]=1<d[c]=3$ | forward |
| 6 | discover d (from a) | d→c, c black, $d[c]=3<d[d]=6$ | cross |
| 7 | discover e | d→e was tree | tree |
| 8 | finish e | | |
| 9 | finish d | | |
| 10 | finish a | | |

The program prints the same times and classes. Figure 15.3 draws them, together with each vertex's interval
$[d, f]$.

<figure class="mars-fig" markdown="0">
<svg viewBox="0 0 760 300" role="img" aria-label="Depth-first search of a five-vertex directed graph with discovery and finish times, its tree, back, forward and cross edges, and the nested time intervals">
<line x1="188.0" y1="55.5" x2="98.1" y2="134.2" stroke="#eea66f" stroke-width="3.5"/>
<polygon points="92.0,139.5 95.9,130.2 101.8,136.9" fill="#eea66f"/>
<text x="149.2" y="112.2" font-size="12" text-anchor="middle" fill="currentColor">tree</text>
<line x1="92.0" y1="160.5" x2="181.9" y2="239.2" stroke="#eea66f" stroke-width="3.5"/>
<polygon points="188.0,244.5 178.2,241.9 184.1,235.2" fill="#eea66f"/>
<text x="149.2" y="196.2" font-size="12" text-anchor="middle" fill="currentColor">tree</text>
<line x1="212.0" y1="55.5" x2="301.9" y2="134.2" stroke="#eea66f" stroke-width="3.5"/>
<polygon points="308.0,139.5 298.2,136.9 304.1,130.2" fill="#eea66f"/>
<text x="250.8" y="112.2" font-size="12" text-anchor="middle" fill="currentColor">tree</text>
<line x1="336.0" y1="150.0" x2="416.0" y2="150.0" stroke="#eea66f" stroke-width="3.5"/>
<polygon points="424.0,150.0 415.0,154.5 415.0,145.5" fill="#eea66f"/>
<text x="380.0" y="142.2" font-size="12" text-anchor="middle" fill="currentColor">tree</text>
<line x1="200.0" y1="61.0" x2="200.0" y2="231.0" stroke="#9cc9ea" stroke-width="2"/>
<polygon points="200.0,239.0 195.5,230.0 204.5,230.0" fill="#9cc9ea"/>
<text x="232.0" y="154.2" font-size="12" text-anchor="middle" fill="currentColor">forward</text>
<path d="M 193.8 240.2 Q 156.0 150.0 190.7 67.1" fill="none" stroke="#7ccf9a" stroke-width="2" stroke-dasharray="6 4"/>
<polygon points="193.8,59.8 194.5,69.8 186.2,66.3" fill="#7ccf9a"/>
<text x="158.0" y="154.2" font-size="12" text-anchor="middle" fill="currentColor">back</text>
<line x1="308.0" y1="160.5" x2="218.1" y2="239.2" stroke="currentColor" stroke-width="1.5" stroke-dasharray="2 3"/>
<polygon points="212.0,244.5 215.9,235.2 221.8,241.9" fill="currentColor"/>
<text x="250.8" y="196.2" font-size="12" text-anchor="middle" fill="currentColor">cross</text>
<text x="228" y="43" font-size="12" text-anchor="start" fill="currentColor" font-family="monospace">1/10</text>
<text x="56" y="154" font-size="12" text-anchor="end" fill="currentColor" font-family="monospace">2/5</text>
<text x="226" y="263" font-size="12" text-anchor="start" fill="currentColor" font-family="monospace">3/4</text>
<text x="320" y="124" font-size="12" text-anchor="middle" fill="currentColor" font-family="monospace">6/9</text>
<text x="440" y="124" font-size="12" text-anchor="middle" fill="currentColor" font-family="monospace">7/8</text>
<text x="608" y="22" font-size="12" text-anchor="middle" fill="currentColor">time</text>
<text x="500" y="42" font-size="11" text-anchor="middle" fill="currentColor" font-family="monospace">1</text>
<text x="524" y="42" font-size="11" text-anchor="middle" fill="currentColor" font-family="monospace">2</text>
<text x="548" y="42" font-size="11" text-anchor="middle" fill="currentColor" font-family="monospace">3</text>
<text x="572" y="42" font-size="11" text-anchor="middle" fill="currentColor" font-family="monospace">4</text>
<text x="596" y="42" font-size="11" text-anchor="middle" fill="currentColor" font-family="monospace">5</text>
<text x="620" y="42" font-size="11" text-anchor="middle" fill="currentColor" font-family="monospace">6</text>
<text x="644" y="42" font-size="11" text-anchor="middle" fill="currentColor" font-family="monospace">7</text>
<text x="668" y="42" font-size="11" text-anchor="middle" fill="currentColor" font-family="monospace">8</text>
<text x="692" y="42" font-size="11" text-anchor="middle" fill="currentColor" font-family="monospace">9</text>
<text x="716" y="42" font-size="11" text-anchor="middle" fill="currentColor" font-family="monospace">10</text>
<rect x="492" y="57" width="232" height="18" rx="9" fill="#9cc9ea" fill-opacity="0.45" stroke="currentColor" stroke-width="1"/>
<text x="484" y="70" font-size="12" text-anchor="end" fill="currentColor">a</text>
<rect x="516" y="87" width="88" height="18" rx="9" fill="#9cc9ea" fill-opacity="0.45" stroke="currentColor" stroke-width="1"/>
<text x="508" y="100" font-size="12" text-anchor="end" fill="currentColor">b</text>
<rect x="540" y="117" width="40" height="18" rx="9" fill="#9cc9ea" fill-opacity="0.45" stroke="currentColor" stroke-width="1"/>
<text x="532" y="130" font-size="12" text-anchor="end" fill="currentColor">c</text>
<rect x="612" y="147" width="88" height="18" rx="9" fill="#9cc9ea" fill-opacity="0.45" stroke="currentColor" stroke-width="1"/>
<text x="604" y="160" font-size="12" text-anchor="end" fill="currentColor">d</text>
<rect x="636" y="177" width="40" height="18" rx="9" fill="#9cc9ea" fill-opacity="0.45" stroke="currentColor" stroke-width="1"/>
<text x="628" y="190" font-size="12" text-anchor="end" fill="currentColor">e</text>
<text x="610" y="236" font-size="11" text-anchor="middle" fill="currentColor" font-family="monospace">( a ( b ( c c ) b ) ( d ( e e ) d ) a )</text>
<text x="610" y="262" font-size="12" text-anchor="middle" fill="currentColor">intervals nest or are apart,</text>
<text x="610" y="280" font-size="12" text-anchor="middle" fill="currentColor">never partly overlap</text>
<circle cx="200" cy="45" r="16" fill="#9cc9ea" fill-opacity="0.55" stroke="currentColor" stroke-width="1.5"/>
<text x="200" y="49.9" font-size="14" text-anchor="middle" fill="currentColor">a</text>
<circle cx="80" cy="150" r="16" fill="#9cc9ea" fill-opacity="0.55" stroke="currentColor" stroke-width="1.5"/>
<text x="80" y="154.9" font-size="14" text-anchor="middle" fill="currentColor">b</text>
<circle cx="200" cy="255" r="16" fill="#9cc9ea" fill-opacity="0.55" stroke="currentColor" stroke-width="1.5"/>
<text x="200" y="259.9" font-size="14" text-anchor="middle" fill="currentColor">c</text>
<circle cx="320" cy="150" r="16" fill="#9cc9ea" fill-opacity="0.55" stroke="currentColor" stroke-width="1.5"/>
<text x="320" y="154.9" font-size="14" text-anchor="middle" fill="currentColor">d</text>
<circle cx="440" cy="150" r="16" fill="#9cc9ea" fill-opacity="0.55" stroke="currentColor" stroke-width="1.5"/>
<text x="440" y="154.9" font-size="14" text-anchor="middle" fill="currentColor">e</text>
</svg>
<figcaption>Figure 15.3. Depth-first search from a. Each vertex carries discovery/finish times. Thick edges form the DFS tree; c→a goes back to an ancestor, a→c jumps forward to a descendant, d→c crosses to a vertex already finished in another branch. On the right, each vertex's interval [d, f]: they nest like brackets.</figcaption>
</figure>

### The parenthesis theorem

Write "(u" when $u$ is discovered and "u)" when it finishes. The trace above reads ( a ( b ( c c ) b ) ( d ( e e )
d ) a ): a correctly nested expression, as if the brackets were typed by a careful person. That always happens.

**Theorem 15.4 (parenthesis theorem).** For any two vertices $u$ and $v$, exactly one of these holds:

1. the intervals $[d[u], f[u]]$ and $[d[v], f[v]]$ are disjoint, and neither vertex is a descendant of the other in
   the DFS forest;
2. $[d[v], f[v]]$ lies strictly inside $[d[u], f[u]]$, and $v$ is a descendant of $u$;
3. the same with $u$ and $v$ swapped.

*Proof.* Suppose $d[u] < d[v]$ (the other case is symmetric). Either $d[v] < f[u]$ or $d[v] > f[u]$.

If $d[v] < f[u]$, then $v$ was discovered while $u$ was grey, that is, while VISIT(u) was still running. Every call
made during VISIT(u) is a call made, directly or indirectly, from it, so $v$ is a descendant of $u$. A recursive call
that starts inside another call also ends inside it, so VISIT(v) returns before VISIT(u) does: $f[v] < f[u]$. The
interval of $v$ is inside that of $u$: case 2.

If $d[v] > f[u]$, then $d[u] < f[u] < d[v] < f[v]$: the intervals are disjoint. Neither vertex was discovered while
the other was grey, so neither is a descendant of the other: case 1. $\square$

**Corollary.** $v$ is a proper descendant of $u$ exactly when $d[u] < d[v] < f[v] < f[u]$.

### The white-path theorem

Which vertices end up below $u$ in the DFS forest? The answer is clean.

**Theorem 15.5 (white-path theorem).** $v$ becomes a descendant of $u$ if and only if, at the moment $d[u]$ when $u$
is discovered, there is a path from $u$ to $v$ consisting entirely of white vertices.

*Proof.* ($\Rightarrow$) If $v$ is a descendant, the tree path from $u$ to $v$ consists of vertices discovered after
$u$ (by the corollary), so they were all white at time $d[u]$.

($\Leftarrow$) Suppose there is a white path $u = w_0, w_1, \dots, w_k = v$ at time $d[u]$, but $v$ does not become
a descendant. Let $w_i$ be the first vertex on the path that does not become a descendant; $i \ge 1$, and
$w_{i-1}$ is a descendant (or $u$ itself), so $f[w_{i-1}] \le f[u]$. Since $w_i$ is white at time $d[u]$, $d[u] <
d[w_i]$. And $w_i$ must be discovered before $w_{i-1}$ finishes, because VISIT($w_{i-1}$) examines the edge to
$w_i$ and would visit it if it were still white. So $d[u] < d[w_i] < f[w_{i-1}] \le f[u]$: $w_i$ is discovered while
$u$ is grey, and by the parenthesis theorem it is a descendant of $u$. Contradiction. $\square$

### Undirected graphs

In an undirected graph each edge is seen twice, once from each end. If we classify each edge the first time DFS
examines it, only two classes appear.

**Theorem 15.6.** In a DFS of an undirected graph, every edge is a tree edge or a back edge.

*Proof.* Take an edge $\{u, v\}$ and suppose $d[u] < d[v]$. Then $v$ is white when $u$ is discovered, and the edge
itself is a white path, so $v$ becomes a descendant of $u$ (white-path theorem) and finishes before $u$. If DFS
first examines the edge from $u$, $v$ is still white at that moment (otherwise DFS would have examined it from $v$
first, since VISIT(v) scans all of $v$'s edges and finishes before $u$ goes on), so it is a tree edge. If it first
examines it from $v$, then $u$ is grey, so it is a back edge. Forward and cross edges never occur. $\square$

This is why, in an undirected graph, "DFS met a vertex that is already visited and is not my parent" means "there
is a cycle".

### Detecting cycles in directed graphs

**Theorem 15.7.** A directed graph has a cycle if and only if a DFS finds a back edge.

*Proof.* ($\Leftarrow$) A back edge $u \to v$ goes to an ancestor $v$, and the tree path from $v$ down to $u$
closes into a cycle with it.

($\Rightarrow$) Let the graph have a cycle, and let $v$ be the first vertex of the cycle that DFS discovers; let
$u$ be the vertex before $v$ on the cycle. At time $d[v]$ the rest of the cycle is white, so there is a white path
from $v$ to $u$, and $u$ becomes a descendant of $v$. When DFS examines $u \to v$, $v$ is still grey (it is an
ancestor of $u$ that has not finished), so $u \to v$ is a back edge. $\square$

This is why the colouring needs three states, not two. With only "visited" and "not visited", reaching a visited
vertex could be a back edge (a cycle) or a harmless forward or cross edge (exercise 5).

**Recursion depth.** In Python, VISIT recursing through a path of 100 000 vertices exceeds the default recursion
limit of 1000. Chapter 3 discussed the limit; for large graphs, write DFS with an explicit stack of (vertex,
iterator over its neighbours) pairs. Exercise 11 does this.

## 15.4 Topological sort

A student must take Intro and Discrete Mathematics before Data Structures, Data Structures before Algorithms and
Systems, Algorithms before Theory and Compilers, Systems before Compilers, and Discrete before Theory. In what order
can the courses be taken, one at a time? Draw each "must come before" as a directed edge. A **topological order**
of a directed graph is a listing of all its vertices in which every edge $u \to v$ has $u$ before $v$. Build
systems order compilation steps this way, spreadsheets order cell updates this way, and package managers order
installations this way.

If the graph has a cycle, there is no topological order: the vertices of the cycle would each have to come before
the next, all the way round to themselves. The converse is the interesting part: every DAG has one, and it can be
found in linear time. There are two classic ways.

### By finish times

**Theorem 15.8.** In a DAG, listing the vertices in decreasing order of DFS finish time gives a topological order.

*Proof.* Take any edge $u \to v$. We show $f[v] < f[u]$. When DFS examines this edge from $u$, $u$ is grey. The
vertex $v$ cannot be grey, because then the edge would be a back edge and, by Theorem 15.7, the graph would have a
cycle. If $v$ is white, it becomes a descendant of $u$ and finishes first: $f[v] < f[u]$. If $v$ is black, it
has already finished, while $u$ has not: again $f[v] < f[u]$. $\square$

So the algorithm is: run DFS; each time a vertex finishes, append it to a list; reverse the list at the end. The
program's `topo_dfs` does exactly that and raises an error if it meets a grey vertex, which proves a cycle. On the
course graph it prints

```
  DFS : discrete intro data systems algos compilers theory
```

You can check every edge: discrete is before data and theory, intro before data, data before algos and systems, and
so on. The time is that of DFS, $O(V + E)$.

### Kahn's algorithm

The second method is the one a person would use. Something must be first: a course with no prerequisites. Take one,
cross it off, and repeat with what remains. The **in-degree** of a vertex counts the edges arriving at it, its
unmet prerequisites.

```text
KAHN(G):
    compute indeg[v] for every v
    ready = queue of all v with indeg[v] == 0
    order = []
    while ready is not empty:
        u = take from ready;  append u to order
        for each edge u -> v:
            indeg[v] -= 1
            if indeg[v] == 0: add v to ready
    if order has fewer than V vertices: report a cycle
```

Arthur Kahn published it in 1962 for scheduling large networks of jobs. Here is the trace on the course graph. The
starting in-degrees are intro 0, discrete 0, data 2, algos 1, systems 1, theory 2, compilers 2.

| Take | In-degrees that drop | Becomes ready | Ready queue after |
|---|---|---|---|
| | | intro, discrete | intro discrete |
| intro | data 2→1 | | discrete |
| discrete | data 1→0, theory 2→1 | data | data |
| data | algos 1→0, systems 1→0 | algos, systems | algos systems |
| algos | theory 1→0, compilers 2→1 | theory | systems theory |
| systems | compilers 1→0 | compilers | theory compilers |
| theory | | | compilers |
| compilers | | | empty |

The order is intro, discrete, data, algos, systems, theory, compilers, which is a different topological order from
the DFS one. Both are right: the course graph has exactly 10 topological orders (exercise 7).

**Theorem 15.9.** Kahn's algorithm outputs a topological order if the graph is a DAG, and outputs fewer than $V$
vertices if the graph has a cycle. It runs in $O(V + E)$ time.

*Proof.* *Order.* A vertex $v$ is added to `ready` only when $\mathrm{indeg}[v]$ reaches 0, which happens only after
every $u$ with an edge $u \to v$ has been taken and appended. So every edge points forward in `order`.

*Completeness on a DAG.* Every DAG with at least one vertex has a vertex of in-degree 0: otherwise, walk backwards
along incoming edges from any vertex; after $V$ steps some vertex repeats, which gives a cycle. Removing the taken
vertices leaves a DAG on the rest, and the counters `indeg` are exactly the in-degrees in that remaining graph. So
while vertices remain, one of them has counter 0 and is in `ready`; the loop stops only when all $V$ have been
output.

*Cycles.* No vertex of a cycle can ever be output: the first one to be output would need its predecessor on the
cycle to be output before it. So at most $V - 1$ vertices come out, and the check reports the cycle.

*Time.* Computing the in-degrees scans every edge once; each vertex enters and leaves `ready` once; each edge is
decremented once. $O(V + E)$. $\square$

Kahn's method has two practical advantages. It needs no recursion. And the `ready` set at each moment is the set of
jobs that could run *right now*, in parallel: the layers it peels off are the stages of a parallel schedule. The
reference page [Topological sort](../../graphs/topological-sort.md) has both methods in three languages.

**Longest paths in a DAG.** A topological order also lets you solve problems that are hard in general graphs. The
longest path in a DAG (the **critical path** of a project: the chain of tasks that decides how long the whole
project takes) is a dynamic program over the topological order, $O(V + E)$; see
[Chapter 13](13-Dynamic-Programming.md), and shortest paths in DAGs come back in
[Chapter 16](16-Shortest-Paths.md).

## 15.5 Strongly connected components

*Level: advanced.*

In a directed graph, "connected" splits into two ideas. Two vertices $u$ and $v$ are **strongly connected** if
there is a path from $u$ to $v$ *and* a path from $v$ to $u$. This relation is an equivalence (it is reflexive,
symmetric, and transitive by joining paths), so it divides the vertices into classes, the **strongly connected
components** (SCCs). Inside a component every vertex can reach every other. In a web graph a component is a group
of pages that all link round to each other; in a program's call graph it is a group of mutually recursive
functions; in a road map with one-way streets, a component you can leave but never re-enter is a trap.

<figure class="mars-fig" markdown="0">
<svg viewBox="0 0 600 320" role="img" aria-label="A directed graph of eight vertices with three strongly connected components shaded, and below it the condensation, a path of three component nodes">
<rect x="30" y="40" width="160" height="150" rx="14" fill="#7ccf9a" fill-opacity="0.18" stroke="currentColor" stroke-opacity="0.5" stroke-dasharray="4 3"/>
<rect x="230" y="40" width="160" height="150" rx="14" fill="#7ccf9a" fill-opacity="0.18" stroke="currentColor" stroke-opacity="0.5" stroke-dasharray="4 3"/>
<rect x="430" y="120" width="150" height="70" rx="14" fill="#7ccf9a" fill-opacity="0.18" stroke="currentColor" stroke-opacity="0.5" stroke-dasharray="4 3"/>
<line x1="76.0" y1="70.0" x2="136.0" y2="70.0" stroke="currentColor" stroke-width="1.5"/>
<polygon points="144.0,70.0 135.0,74.5 135.0,65.5" fill="currentColor"/>
<line x1="152.2" y1="84.0" x2="121.7" y2="139.0" stroke="currentColor" stroke-width="1.5"/>
<polygon points="117.8,146.0 118.2,136.0 126.1,140.3" fill="currentColor"/>
<line x1="102.2" y1="146.0" x2="71.7" y2="91.0" stroke="currentColor" stroke-width="1.5"/>
<polygon points="67.8,84.0 76.1,89.7 68.2,94.0" fill="currentColor"/>
<line x1="126.0" y1="160.0" x2="236.0" y2="160.0" stroke="currentColor" stroke-width="1.5"/>
<polygon points="244.0,160.0 235.0,164.5 235.0,155.5" fill="currentColor"/>
<line x1="267.8" y1="146.0" x2="298.3" y2="91.0" stroke="currentColor" stroke-width="1.5"/>
<polygon points="302.2,84.0 301.8,94.0 293.9,89.7" fill="currentColor"/>
<line x1="317.8" y1="84.0" x2="348.3" y2="139.0" stroke="currentColor" stroke-width="1.5"/>
<polygon points="352.2,146.0 343.9,140.3 351.8,136.0" fill="currentColor"/>
<line x1="344.0" y1="160.0" x2="284.0" y2="160.0" stroke="currentColor" stroke-width="1.5"/>
<polygon points="276.0,160.0 285.0,155.5 285.0,164.5" fill="currentColor"/>
<line x1="376.0" y1="160.0" x2="436.0" y2="160.0" stroke="currentColor" stroke-width="1.5"/>
<polygon points="444.0,160.0 435.0,164.5 435.0,155.5" fill="currentColor"/>
<line x1="176.0" y1="70.0" x2="286.0" y2="70.0" stroke="currentColor" stroke-width="1.5"/>
<polygon points="294.0,70.0 285.0,74.5 285.0,65.5" fill="currentColor"/>
<path d="M 474.1 167.5 Q 505.0 184.0 528.8 171.3" fill="none" stroke="currentColor" stroke-width="1.5"/>
<polygon points="535.9,167.5 530.1,175.7 525.8,167.8" fill="currentColor"/>
<path d="M 535.9 152.5 Q 505.0 136.0 481.2 148.7" fill="none" stroke="currentColor" stroke-width="1.5"/>
<polygon points="474.1,152.5 479.9,144.3 484.2,152.2" fill="currentColor"/>
<text x="110" y="30" font-size="12" text-anchor="middle" fill="currentColor">{1, 2, 3}</text>
<text x="310" y="30" font-size="12" text-anchor="middle" fill="currentColor">{4, 5, 6}</text>
<text x="505" y="112" font-size="12" text-anchor="middle" fill="currentColor">{7, 8}</text>
<rect x="70" y="250" width="100" height="36" rx="8" fill="#eea66f" fill-opacity="0.45" stroke="currentColor" stroke-width="1.3"/>
<text x="120" y="273" font-size="13" text-anchor="middle" fill="currentColor">{1,2,3}</text>
<rect x="250" y="250" width="100" height="36" rx="8" fill="#eea66f" fill-opacity="0.45" stroke="currentColor" stroke-width="1.3"/>
<text x="300" y="273" font-size="13" text-anchor="middle" fill="currentColor">{4,5,6}</text>
<rect x="430" y="250" width="100" height="36" rx="8" fill="#eea66f" fill-opacity="0.45" stroke="currentColor" stroke-width="1.3"/>
<text x="480" y="273" font-size="13" text-anchor="middle" fill="currentColor">{7,8}</text>
<line x1="170" y1="268" x2="241" y2="268" stroke="currentColor" stroke-width="1.5"/><polygon points="250,268 241,263.5 241,272.5" fill="currentColor"/>
<line x1="350" y1="268" x2="421" y2="268" stroke="currentColor" stroke-width="1.5"/><polygon points="430,268 421,263.5 421,272.5" fill="currentColor"/>
<text x="300" y="310" font-size="12" text-anchor="middle" fill="currentColor">the condensation: one node per component, always a DAG</text>
<circle cx="60" cy="70" r="16" fill="#9cc9ea" fill-opacity="0.55" stroke="currentColor" stroke-width="1.5"/>
<text x="60" y="74.9" font-size="14" text-anchor="middle" fill="currentColor">1</text>
<circle cx="160" cy="70" r="16" fill="#9cc9ea" fill-opacity="0.55" stroke="currentColor" stroke-width="1.5"/>
<text x="160" y="74.9" font-size="14" text-anchor="middle" fill="currentColor">2</text>
<circle cx="110" cy="160" r="16" fill="#9cc9ea" fill-opacity="0.55" stroke="currentColor" stroke-width="1.5"/>
<text x="110" y="164.9" font-size="14" text-anchor="middle" fill="currentColor">3</text>
<circle cx="260" cy="160" r="16" fill="#9cc9ea" fill-opacity="0.55" stroke="currentColor" stroke-width="1.5"/>
<text x="260" y="164.9" font-size="14" text-anchor="middle" fill="currentColor">4</text>
<circle cx="310" cy="70" r="16" fill="#9cc9ea" fill-opacity="0.55" stroke="currentColor" stroke-width="1.5"/>
<text x="310" y="74.9" font-size="14" text-anchor="middle" fill="currentColor">5</text>
<circle cx="360" cy="160" r="16" fill="#9cc9ea" fill-opacity="0.55" stroke="currentColor" stroke-width="1.5"/>
<text x="360" y="164.9" font-size="14" text-anchor="middle" fill="currentColor">6</text>
<circle cx="460" cy="160" r="16" fill="#9cc9ea" fill-opacity="0.55" stroke="currentColor" stroke-width="1.5"/>
<text x="460" y="164.9" font-size="14" text-anchor="middle" fill="currentColor">7</text>
<circle cx="550" cy="160" r="16" fill="#9cc9ea" fill-opacity="0.55" stroke="currentColor" stroke-width="1.5"/>
<text x="550" y="164.9" font-size="14" text-anchor="middle" fill="currentColor">8</text>
</svg>
<figcaption>Figure 15.4. Strongly connected components. Inside each shaded region every vertex can reach every other; between regions the edges all point one way. Shrinking each component to a single node gives the condensation, which has no cycles.</figcaption>
</figure>

Figure 15.4 shows our example, with edges 1→2, 2→3, 3→1, 3→4, 4→5, 5→6, 6→4, 6→7, 7→8, 8→7 and 2→5. It has three
components: {1, 2, 3}, {4, 5, 6} and {7, 8}.

**The condensation.** Shrink each component to a single vertex, keeping an edge from component $C$ to component $C'$
whenever some edge goes from $C$ to $C'$. The result, the **condensation**, is always a DAG: if it had a cycle, all
the components on it could reach each other, so they would be one component. So every directed graph is "a DAG of
strongly connected pieces". The two algorithms below find the pieces in linear time.

### Kosaraju's algorithm: two passes

The idea is surprising the first time you see it. Run DFS once to get finish times. Then reverse every edge and run
DFS again, starting each new tree at the remaining vertex with the *latest* finish time. Each tree of the second
pass is exactly one component.

The algorithm is usually credited to S. Rao Kosaraju (an unpublished 1978 lecture) and was published by Micha
Sharir in 1981.

**Trace.** First pass from 1: 1→2→3, 3→1 is grey, 3→4→5→6, 6→4 grey, 6→7→8, 8→7 grey. Vertices finish in the order
8, 7, 6, 5, 4, 3, then 2 (whose edge 2→5 now leads to a black vertex), then 1. In the **reverse graph** the edges
are 2→1, 3→2, 1→3, 4→3, 5→4, 6→5, 4→6, 7→6, 8→7, 7→8, 5→2. Second pass, in decreasing finish time:

- start at 1: reverse edges lead 1→3→2→1; the tree is {1, 3, 2}. From 2, the reverse edge 2→1 goes back inside.
- next unvisited in finish order: 4. Reverse edges 4→3 (taken), 4→6→5→4, and 5→2 (taken); the tree is {4, 6, 5}.
- next: 7. Reverse edges 7→6 (taken), 7→8; the tree is {7, 8}.

The program prints `[[1, 3, 2], [4, 6, 5], [7, 8]]`.

**Why it works.** Extend finish times to components: $f(C)$ is the largest finish time of any vertex in $C$.

**Lemma 15.10.** If there is an edge from component $C$ to a different component $C'$, then $f(C) > f(C')$.

*Proof.* Let $x$ be the first vertex of $C \cup C'$ that the first DFS discovers.

If $x \in C$: at time $d[x]$ every other vertex of $C$ and $C'$ is white, and there are white paths from $x$ to all
of them (through $C$, across the edge, through $C'$). By the white-path theorem all of them become descendants of
$x$ and finish before $x$, so $f(C) = f[x] > f(C')$.

If $x \in C'$: at time $d[x]$ all of $C'$ is white and reachable, so all of $C'$ finishes before $x$ finishes, at
$f[x] = f(C')$. No vertex of $C$ is reachable from $x$ (otherwise, with the edge from $C$ to $C'$, the two would be
one component), so none of $C$ is discovered while $x$ is grey; they are all still white at $f[x]$ and finish
later. So $f(C) > f(C')$. $\square$

**Theorem 15.11.** The trees of Kosaraju's second pass are exactly the strongly connected components.

*Proof.* Reversing every edge keeps the same components (a path from $u$ to $v$ reversed is a path from $v$ to $u$)
but reverses the edges of the condensation. The second pass starts at the vertex with the largest finish time,
which lies in the component $C$ with largest $f(C)$. By the lemma, no edge of the original graph enters $C$ from
another component (that component would have a larger $f$), so in the reverse graph no edge leaves $C$. The second
DFS from that vertex therefore visits all of $C$ (it is strongly connected) and nothing else. Remove $C$ and
repeat the argument on what remains: the next start is in the component with the largest $f$ among those left, and
every reverse edge leaving it goes to a component already visited. By induction each tree is one component.
$\square$

The cost is two DFS runs and building the reverse graph: $O(V + E)$.

### Tarjan's algorithm: one pass with low-links

Robert Tarjan's 1972 paper "Depth-first search and linear graph algorithms" did it in a single DFS, and its main
idea, the **low-link**, also gives bridges and articulation points (15.6).

Give each vertex an **index**, the order in which DFS discovers it (0, 1, 2, ...). Push each vertex on a separate
stack when it is discovered. Define $\mathrm{low}[u]$ as the smallest index reachable from $u$ by going down tree
edges and then taking at most one edge to a vertex that is still on the stack. If, when $u$ finishes, $\mathrm{low}[u]
= \mathrm{index}[u]$, then $u$ is the first-discovered vertex of its component, its **root**, and the component is
exactly $u$ and everything above it on the stack. Pop them off.

```text
VISIT(u):
    index[u] = low[u] = counter;  counter += 1
    push u on stack
    for each edge u -> v:
        if v has no index:  VISIT(v);  low[u] = min(low[u], low[v])
        elif v is on stack: low[u] = min(low[u], index[v])
    if low[u] == index[u]:
        pop vertices down to and including u: they form one component
```

**Trace on Figure 15.4.** Indices follow the discovery order 1, 2, 3, 4, 5, 6, 7, 8 → 0 to 7.

| Event | Stack (bottom to top) | low updates |
|---|---|---|
| visit 1, 2, 3 | 1 2 3 | |
| 3→1, 1 on stack | 1 2 3 | low[3] = 0 |
| visit 4, 5, 6 | 1 2 3 4 5 6 | |
| 6→4, on stack | | low[6] = 3 |
| visit 7, 8; 8→7 on stack | 1 2 3 4 5 6 7 8 | low[8] = 6 |
| finish 8 (low 6 ≠ 7); finish 7 | | low[7] = 6 = index[7]: pop 8, 7 |
| finish 6, 5 | 1 2 3 4 5 6 | low[5] = 3 |
| finish 4 | | low[4] = 3 = index[4]: pop 6, 5, 4 |
| finish 3; at 2, edge 2→5: 5 not on stack, ignored | 1 2 3 | low[2] = 0 |
| finish 1 | | low[1] = 0 = index[1]: pop 3, 2, 1 |

The output is `[[8, 7], [6, 5, 4], [3, 2, 1]]` with the low values `{1: 0, 2: 0, 3: 0, 4: 3, 5: 3, 6: 3, 7: 6, 8: 6}`,
as printed. Notice that Tarjan's algorithm emits the components in *reverse* topological order of the
condensation: sinks first.

The test "is $v$ on the stack?" matters. The edge 2→5 leads to 5, which has an index but was already popped as part
of a finished component; using its index would wrongly pull 2's low value down to 4 and merge components.

**Why it works (sketch of the proof).** Call the first-discovered vertex of a component its **root**. By the
white-path theorem, when the root is discovered every other vertex of its component is white and reachable, so the
whole component lies in the root's DFS subtree. We show that $u$ is a root exactly when $\mathrm{low}[u] =
\mathrm{index}[u]$.

Suppose $u$ is not a root; its root $r$ is a proper ancestor of $u$. A path from $u$ back to $r$ must leave $u$'s
subtree; let $x \to y$ be the first edge on it that does, with $x$ inside. In a directed DFS an edge leaving a
subtree goes to a vertex discovered earlier, so $\mathrm{index}[y] < \mathrm{index}[u]$. And $y$ is in the same
component as $r$ (it lies on the cycle $r \to u \to y \to r$), which has not been popped yet because $r$ is still
running; so $y$ is on the stack and $\mathrm{low}[u] \le \mathrm{index}[y] < \mathrm{index}[u]$.

Conversely, suppose some edge from $u$'s subtree reaches a vertex $w$ on the stack with $\mathrm{index}[w] <
\mathrm{index}[u]$. The root $r$ of $w$'s component has not finished (it would have popped $w$), so $r$ is grey and
therefore an ancestor of the current vertex, and $\mathrm{index}[r] \le \mathrm{index}[w] < \mathrm{index}[u]$
makes it a proper ancestor of $u$. Then $r$ reaches $u$ down the tree, $u$ reaches $w$, and $w$ reaches $r$: $u$ is
in $r$'s component and is not a root.

When a root $u$ finishes, the vertices above it on the stack are the vertices of its subtree not already popped
with an earlier root, and those are exactly its component. Full proofs are in Tarjan's 1972 paper and in Sedgewick
and Wayne, Section 4.2. Time: one DFS plus $O(1)$ stack work per vertex, $O(V + E)$.

The reference page [Strongly connected components](../../graphs/scc.md) has an animation of the two-pass method.

**A use: 2-satisfiability.** Given clauses like "$x$ or not $y$", each with two literals, is there an assignment
making them all true? Build a graph on the $2n$ literals with edges $\lnot a \to b$ and $\lnot b \to a$ for each clause
$(a \lor b)$. The formula is satisfiable if and only if no variable is in the same SCC as its negation, and the
SCC order gives an assignment (Aspvall, Plass and Tarjan, 1979). Compare 3-satisfiability, which is NP-complete
([Chapter 22](22-NP-Completeness.md)).

## 15.6 Bridges and articulation points

*Level: advanced.*

A network engineer asks: which single cable, if cut, splits the network? Which single router, if it fails? In an
undirected connected graph, a **bridge** is an edge whose removal disconnects the graph, and an **articulation
point** (cut vertex) is a vertex whose removal, together with its edges, disconnects it. A graph with no articulation
point is **biconnected**: it survives any one vertex failure.

The slow way removes each edge in turn and runs BFS: $O(E(V + E))$. DFS with low-links does it in one pass.

In an undirected DFS, number the vertices by discovery time $\mathrm{disc}[u]$ and define

$$
\mathrm{low}[u] = \min\big(\mathrm{disc}[u],\ \min\{\mathrm{disc}[w] : \text{some back edge goes from the subtree of } u \text{ to } w\}\big),
$$

the earliest vertex that the subtree of $u$ can reach with one back edge. It is computed bottom-up while DFS returns:
for a tree child $v$, $\mathrm{low}[u] \leftarrow \min(\mathrm{low}[u], \mathrm{low}[v])$; for a back edge to $w$
(other than the edge to the parent), $\mathrm{low}[u] \leftarrow \min(\mathrm{low}[u], \mathrm{disc}[w])$.

**Theorem 15.12.** Let $v$ be a child of $u$ in the DFS tree.

1. The tree edge $\{u, v\}$ is a bridge if and only if $\mathrm{low}[v] > \mathrm{disc}[u]$.
2. A non-root vertex $u$ is an articulation point if and only if it has a child $v$ with $\mathrm{low}[v] \ge
   \mathrm{disc}[u]$.
3. The root is an articulation point if and only if it has at least two children in the DFS tree.

*Proof.* By Theorem 15.6, all non-tree edges are back edges, joining a vertex to one of its ancestors. A back edge
is never a bridge, because it lies on a cycle with the tree path it spans.

(1) Remove the tree edge $\{u, v\}$. The subtree of $v$ stays connected to the rest exactly when some edge, other
than $\{u,v\}$, joins the subtree of $v$ to a vertex outside it. Any such edge is a back edge to a proper ancestor of
$v$, which is $u$ or above, with discovery time at most $\mathrm{disc}[u]$. So the subtree stays connected iff
$\mathrm{low}[v] \le \mathrm{disc}[u]$, and $\{u,v\}$ is a bridge iff $\mathrm{low}[v] > \mathrm{disc}[u]$.

(2) Remove a non-root $u$. The rest of the graph falls into the part containing the root, and the subtrees of $u$'s
children. The subtree of child $v$ stays attached to the root's part iff it has a back edge to a proper ancestor of
$u$, which means $\mathrm{low}[v] < \mathrm{disc}[u]$. (Back edges from one child's subtree to another's do not
exist: they would be cross edges.) So $u$ cuts the graph iff some child has $\mathrm{low}[v] \ge \mathrm{disc}[u]$.

(3) If the root has one child, removing it leaves that child's subtree, which is connected. If it has two or more,
there are no edges between their subtrees (again, they would be cross edges), so removing the root separates them.
$\square$

<figure class="mars-fig" markdown="0">
<svg viewBox="0 0 560 175" role="img" aria-label="Two triangles A B C and D E F joined by the edge C D, with a pendant edge F G; the bridges C D and F G are thick and the articulation points C, D and F are orange">
<line x1="50.0" y1="56.0" x2="50.0" y2="119.0" stroke="currentColor" stroke-width="1.5"/>
<line x1="64.2" y1="127.6" x2="125.8" y2="95.4" stroke="currentColor" stroke-width="1.5"/>
<line x1="125.9" y1="80.5" x2="64.1" y2="47.5" stroke="currentColor" stroke-width="1.5"/>
<line x1="274.1" y1="80.5" x2="335.9" y2="47.5" stroke="currentColor" stroke-width="1.5"/>
<line x1="350.0" y1="56.0" x2="350.0" y2="119.0" stroke="currentColor" stroke-width="1.5"/>
<line x1="335.8" y1="127.6" x2="274.2" y2="95.4" stroke="currentColor" stroke-width="1.5"/>
<line x1="156.0" y1="88.0" x2="244.0" y2="88.0" stroke="#eea66f" stroke-width="4"/>
<text x="200.0" y="78.2" font-size="12" text-anchor="middle" fill="currentColor">bridge</text>
<line x1="366.0" y1="135.0" x2="454.0" y2="135.0" stroke="#eea66f" stroke-width="4"/>
<text x="410.0" y="125.2" font-size="12" text-anchor="middle" fill="currentColor">bridge</text>
<text x="50" y="16" font-size="11" text-anchor="middle" fill="currentColor" font-family="monospace">0, 0</text>
<text x="50" y="167" font-size="11" text-anchor="middle" fill="currentColor" font-family="monospace">1, 0</text>
<text x="140" y="64" font-size="11" text-anchor="middle" fill="currentColor" font-family="monospace">2, 0</text>
<text x="260" y="64" font-size="11" text-anchor="middle" fill="currentColor" font-family="monospace">3, 3</text>
<text x="350" y="16" font-size="11" text-anchor="middle" fill="currentColor" font-family="monospace">4, 3</text>
<text x="350" y="167" font-size="11" text-anchor="middle" fill="currentColor" font-family="monospace">5, 3</text>
<text x="470" y="167" font-size="11" text-anchor="middle" fill="currentColor" font-family="monospace">6, 6</text>
<circle cx="50" cy="40" r="16" fill="#9cc9ea" fill-opacity="0.55" stroke="currentColor" stroke-width="1.5"/>
<text x="50" y="44.9" font-size="14" text-anchor="middle" fill="currentColor">A</text>
<circle cx="50" cy="135" r="16" fill="#9cc9ea" fill-opacity="0.55" stroke="currentColor" stroke-width="1.5"/>
<text x="50" y="139.9" font-size="14" text-anchor="middle" fill="currentColor">B</text>
<circle cx="140" cy="88" r="16" fill="#eea66f" fill-opacity="0.55" stroke="currentColor" stroke-width="1.5"/>
<text x="140" y="92.9" font-size="14" text-anchor="middle" fill="currentColor">C</text>
<circle cx="260" cy="88" r="16" fill="#eea66f" fill-opacity="0.55" stroke="currentColor" stroke-width="1.5"/>
<text x="260" y="92.9" font-size="14" text-anchor="middle" fill="currentColor">D</text>
<circle cx="350" cy="40" r="16" fill="#9cc9ea" fill-opacity="0.55" stroke="currentColor" stroke-width="1.5"/>
<text x="350" y="44.9" font-size="14" text-anchor="middle" fill="currentColor">E</text>
<circle cx="350" cy="135" r="16" fill="#eea66f" fill-opacity="0.55" stroke="currentColor" stroke-width="1.5"/>
<text x="350" y="139.9" font-size="14" text-anchor="middle" fill="currentColor">F</text>
<circle cx="470" cy="135" r="16" fill="#9cc9ea" fill-opacity="0.55" stroke="currentColor" stroke-width="1.5"/>
<text x="470" y="139.9" font-size="14" text-anchor="middle" fill="currentColor">G</text>
</svg>
<figcaption>Figure 15.6. Bridges and articulation points. The small numbers are disc, low for a DFS from A. An edge u–v to a child v is a bridge exactly when low[v] > disc[u]; a non-root u is an articulation point exactly when some child has low[v] ≥ disc[u].</figcaption>
</figure>

**Trace (Figure 15.6).** Edges: triangle A, B, C; edge C–D; triangle D, E, F; edge F–G. DFS from A visits A, B, C,
D, E, F, G with disc 0 to 6. Back edges: C–A gives low[C] = 0; F–D gives low[F] = 3. Passing low values up: low[G]
= 6, low[F] = 3, low[E] = 3, low[D] = 3, low[C] = 0, low[B] = 0, low[A] = 0.

- Edge F–G: low[G] = 6 > disc[F] = 5, a bridge. Edge C–D: low[D] = 3 > disc[C] = 2, a bridge. Every other tree edge
  has low[child] ≤ disc[parent].
- F: child G has low 6 ≥ 5, an articulation point. D: child E has low 3 ≥ 3, an articulation point. C: child D has
  low 3 ≥ 2, an articulation point. B: child C has low 0 < 1, not one. A is the root with one child, not one.

The program agrees: bridges `[('F', 'G'), ('C', 'D')]`, articulation points `['C', 'D', 'F']`.

**A trap with parallel edges.** The code skips the edge back to the parent by comparing vertices (`v != parent`). In
a multigraph with two parallel edges between $u$ and $v$, the second copy is a genuine back edge and the pair is not a
bridge, but the vertex test would ignore it. For multigraphs, skip the parent *edge* by its id instead.

This low-link technique, from the same 1972 Tarjan paper (with Hopcroft, who worked with him on biconnected
components and planarity), runs in $O(V + E)$.

## 15.7 Bipartite graphs, cycles and Euler tours

### Two-colouring

Can you split a class into two teams so that no two rivals are on the same team? Can a set of exams be fitted into
two time slots so that no student has two exams at once? Each is the question whether a graph is **bipartite**: its
vertices can be split into two sides with every edge going between the sides. Equivalently, the vertices can be
coloured with two colours so that every edge joins different colours.

**Theorem 15.13 (König, 1936).** A graph is bipartite if and only if it has no cycle of odd length.

*Proof.* ($\Rightarrow$) Walking along a cycle in a two-coloured graph, the colours alternate, so you are back to
the starting colour only after an even number of steps.

($\Leftarrow$) It suffices to treat a connected graph (do each component separately). Pick a vertex $s$ and colour
each vertex by the parity of its BFS distance $\delta(s, v)$. Suppose some edge $\{u, v\}$ joins two vertices of the
same parity. The BFS tree paths from $s$ to $u$ and from $s$ to $v$ part company at some last common vertex $z$.
The cycle $z \to \dots \to u \to v \to \dots \to z$ has length $(\delta(s,u) - \delta(s,z)) + 1 + (\delta(s,v) -
\delta(s,z))$, and since $\delta(s,u)$ and $\delta(s,v)$ have the same parity, this is odd. So if there is no odd
cycle, the parity colouring is proper. $\square$

The proof is an algorithm: BFS, colour by parity, check every edge. When an edge fails, the two tree paths give an
odd cycle as a **certificate** that the graph is not bipartite, which is far more convincing than a bare "no". The
program's `two_colour` does this. On the cube graph (8 corners of a cube, 12 edges) it prints the two sides [0, 3,
5, 6] and [1, 2, 4, 7]; on a pentagon with a tail it returns the odd cycle [0, 1, 2, 3, 4]. Time $O(V + E)$.

Bipartite graphs are where the matching algorithms of [Chapter 17](17-Spanning-Trees-Flows-and-Matching.md) live.
Testing for three colours is a different story: 3-colourability is NP-complete ([Chapter 22](22-NP-Completeness.md)).

### Finding any cycle

To summarise cycle detection, which comes up constantly:

- **Undirected:** a DFS (or BFS) that meets an already-visited vertex other than the parent has found a cycle.
  Without any cycle the graph is a forest and $E = V - C$, where $C$ is the number of components.
- **Directed:** a DFS that meets a *grey* vertex has found a cycle (Theorem 15.7); equivalently Kahn's algorithm
  fails to output every vertex.

### Euler tours and the bridges of Königsberg

The city of Königsberg in Prussia (today Kaliningrad) stood on both banks of the river Pregel and on an island, with
seven bridges joining the four land masses. People asked whether one could walk through the city crossing every
bridge exactly once. In a paper dated 1736 for the Academy in St Petersburg (and published in 1741), Leonhard
Euler showed that it cannot be done and, more importantly, gave the rule for any arrangement of land and bridges.
His paper is usually counted as the beginning of graph theory.

<figure class="mars-fig" markdown="0">
<svg viewBox="0 0 640 300" role="img" aria-label="Left: the seven bridges of Königsberg as a multigraph with four land masses of degrees 3, 5, 3 and 3. Right: the envelope graph with an Euler path numbered 1 to 8">
<path d="M 156.1 47.9 Q 107.7 75.5 94.0 129.5" fill="none" stroke="currentColor" stroke-width="1.5"/>
<path d="M 166.0 55.5 Q 152.3 109.5 103.9 137.1" fill="none" stroke="currentColor" stroke-width="1.5"/>
<path d="M 166.0 234.5 Q 152.3 180.5 103.9 152.9" fill="none" stroke="currentColor" stroke-width="1.5"/>
<path d="M 156.1 242.1 Q 107.7 214.5 94.0 160.5" fill="none" stroke="currentColor" stroke-width="1.5"/>
<line x1="181.6" y1="51.0" x2="268.4" y2="134.0" stroke="currentColor" stroke-width="1.5"/>
<line x1="181.6" y1="239.0" x2="268.4" y2="156.0" stroke="currentColor" stroke-width="1.5"/>
<line x1="106.0" y1="145.0" x2="264.0" y2="145.0" stroke="currentColor" stroke-width="1.5"/>
<text x="170" y="16" font-size="12" text-anchor="middle" fill="currentColor">north bank, degree 3</text>
<text x="170" y="288" font-size="12" text-anchor="middle" fill="currentColor">south bank, degree 3</text>
<text x="60" y="150" font-size="12" text-anchor="end" fill="currentColor">5</text>
<text x="305" y="150" font-size="12" text-anchor="start" fill="currentColor">3</text>
<text x="48" y="128" font-size="12" text-anchor="end" fill="currentColor">island</text>
<text x="305" y="128" font-size="12" text-anchor="start" fill="currentColor">east</text>
<line x1="451.7" y1="249.1" x2="568.3" y2="140.9" stroke="currentColor" stroke-width="1.5"/>
<text x="488.7" y="238.4" font-size="13" text-anchor="middle" fill="#eea66f">1</text>
<line x1="569.5" y1="118.0" x2="520.5" y2="62.0" stroke="currentColor" stroke-width="1.5"/>
<text x="536.0" y="102.5" font-size="13" text-anchor="middle" fill="#eea66f">2</text>
<line x1="499.5" y1="62.0" x2="450.5" y2="118.0" stroke="currentColor" stroke-width="1.5"/>
<text x="484.0" y="102.5" font-size="13" text-anchor="middle" fill="#eea66f">3</text>
<line x1="451.7" y1="140.9" x2="568.3" y2="249.1" stroke="currentColor" stroke-width="1.5"/>
<text x="469.7" y="181.2" font-size="13" text-anchor="middle" fill="#eea66f">4</text>
<line x1="564.0" y1="260.0" x2="456.0" y2="260.0" stroke="currentColor" stroke-width="1.5"/>
<text x="510.0" y="278.6" font-size="13" text-anchor="middle" fill="#eea66f">5</text>
<line x1="440.0" y1="244.0" x2="440.0" y2="146.0" stroke="currentColor" stroke-width="1.5"/>
<text x="454.0" y="199.6" font-size="13" text-anchor="middle" fill="#eea66f">6</text>
<line x1="456.0" y1="130.0" x2="564.0" y2="130.0" stroke="currentColor" stroke-width="1.5"/>
<text x="510.0" y="122.5" font-size="13" text-anchor="middle" fill="#eea66f">7</text>
<line x1="580.0" y1="146.0" x2="580.0" y2="244.0" stroke="currentColor" stroke-width="1.5"/>
<text x="594.0" y="199.6" font-size="13" text-anchor="middle" fill="#eea66f">8</text>
<text x="510" y="292" font-size="12" text-anchor="middle" fill="currentColor">odd vertices: 3 and 4 (orange)</text>
<circle cx="170" cy="40" r="16" fill="#9cc9ea" fill-opacity="0.55" stroke="currentColor" stroke-width="1.5"/>
<text x="170" y="44.9" font-size="14" text-anchor="middle" fill="currentColor">N</text>
<circle cx="170" cy="250" r="16" fill="#9cc9ea" fill-opacity="0.55" stroke="currentColor" stroke-width="1.5"/>
<text x="170" y="254.9" font-size="14" text-anchor="middle" fill="currentColor">S</text>
<circle cx="90" cy="145" r="16" fill="#9cc9ea" fill-opacity="0.55" stroke="currentColor" stroke-width="1.5"/>
<text x="90" y="149.9" font-size="14" text-anchor="middle" fill="currentColor">I</text>
<circle cx="280" cy="145" r="16" fill="#9cc9ea" fill-opacity="0.55" stroke="currentColor" stroke-width="1.5"/>
<text x="280" y="149.9" font-size="14" text-anchor="middle" fill="currentColor">E</text>
<circle cx="440" cy="130" r="16" fill="#9cc9ea" fill-opacity="0.55" stroke="currentColor" stroke-width="1.5"/>
<text x="440" y="134.9" font-size="14" text-anchor="middle" fill="currentColor">1</text>
<circle cx="580" cy="130" r="16" fill="#9cc9ea" fill-opacity="0.55" stroke="currentColor" stroke-width="1.5"/>
<text x="580" y="134.9" font-size="14" text-anchor="middle" fill="currentColor">2</text>
<circle cx="580" cy="260" r="16" fill="#eea66f" fill-opacity="0.55" stroke="currentColor" stroke-width="1.5"/>
<text x="580" y="264.9" font-size="14" text-anchor="middle" fill="currentColor">3</text>
<circle cx="440" cy="260" r="16" fill="#eea66f" fill-opacity="0.55" stroke="currentColor" stroke-width="1.5"/>
<text x="440" y="264.9" font-size="14" text-anchor="middle" fill="currentColor">4</text>
<circle cx="510" cy="50" r="16" fill="#9cc9ea" fill-opacity="0.55" stroke="currentColor" stroke-width="1.5"/>
<text x="510" y="54.9" font-size="14" text-anchor="middle" fill="currentColor">5</text>
</svg>
<figcaption>Figure 15.5. Left: Euler's 1736 problem as a graph. Each land mass is a vertex and each bridge an edge; all four degrees are odd, so no walk crosses every bridge once. Right: the envelope has exactly two odd vertices, 3 and 4, and the numbers give the Euler path 4, 2, 5, 1, 3, 4, 1, 2, 3 found by the code.</figcaption>
</figure>

An **Euler path** is a walk that uses every edge exactly once; an **Euler circuit** is one that ends where it
began. (A walk may repeat vertices but, here, not edges.)

**Theorem 15.14 (Euler; Hierholzer).** A connected multigraph (ignoring vertices of degree 0) has an Euler circuit if
and only if every vertex has even degree. It has an Euler path that is not a circuit if and only if exactly two
vertices have odd degree, and then the path runs from one to the other.

*Proof.* (Necessity.) Each time a closed walk passes through a vertex it enters by one edge and leaves by another,
using two of its edges; the start vertex is left at the beginning and entered at the end, also a pair. So every
degree is even. For an open path the two ends each have one unpaired edge, so exactly they are odd.

(Sufficiency, for circuits, by strong induction on the number of edges.) Suppose every degree is even. Start
anywhere and walk along unused edges, never reusing one, until you are stuck. You can only get stuck at the start
vertex: whenever you enter any other vertex you have used an odd number of its edges, and its degree is even, so an
unused edge remains to leave by. So the walk is a closed circuit $C$. If $C$ uses every edge, done. Otherwise remove
the edges of $C$. Every vertex loses an even number of edges, so all degrees in what remains are still even, and each
connected piece of the remainder has fewer edges and, by induction, an Euler circuit. Each piece touches $C$ at some
vertex (the original graph is connected). Splice each piece's circuit into $C$ at such a vertex: you get one circuit
using every edge.

(Paths.) If exactly two vertices $a$ and $b$ are odd, add an extra edge $a$–$b$. Now all degrees are even and there
is an Euler circuit; removing the extra edge from it leaves an Euler path from $a$ to $b$. $\square$

Königsberg's four land masses have degrees 3, 5, 3 and 3 (Figure 15.5, left): four odd vertices, so there is no
walk over every bridge once, open or closed. The program prints those degrees. Euler's paper did not draw a graph:
he reasoned with the land areas and bridges directly, and the theorem's proof of sufficiency was given only in 1873,
in a posthumous paper by Carl Hierholzer.

**Hierholzer's algorithm.** The sufficiency proof is an algorithm, and with a stack it runs in $O(E)$:

```text
stack = [start];  tour = []
while stack:
    u = top of stack
    if u has an unused edge u-v:  mark it used;  push v
    else:                         pop u and append it to tour
reverse tour
```

Walking forward pushes the current circuit; getting stuck pops vertices into the tour, and whenever a popped-back
vertex still has unused edges, a new sub-circuit starts there and is spliced in automatically. Each edge is pushed
once and each vertex pop is $O(1)$, plus the work of skipping used edges, which is $O(1)$ per edge if you delete
them from the lists as you go (the program pops them off the end of each list). Total $O(V + E)$.

The **envelope** puzzle (draw this house shape without lifting the pen or retracing a line) has degrees 4, 4, 3, 3,
2: exactly two odd vertices, 3 and 4. The program adds a dummy edge 3–4, finds the circuit 3, 4, 2, 5, 1, 3, 4, 1,
2, 3 and cuts it at one of the two 3–4 edges, giving the Euler path 4, 2, 5, 1, 3, 4, 1, 2, 3 that is numbered in
Figure 15.5. On two triangles sharing vertex 0 it finds the circuit 0, 4, 3, 0, 2, 1, 0: the second triangle was
spliced in when the walk returned to 0.

Euler circuits look like a puzzle, but they are used to assemble DNA: in the de Bruijn graph method, the short reads
of a genome become edges, and a reconstruction of the sequence is an Euler path (Pevzner, Tang and Waterman, 2001).
The opposite question, a **Hamiltonian cycle** visiting every *vertex* once, looks almost the same and is
NP-complete ([Chapter 22](22-NP-Completeness.md)). A one-word change in the question moves it from linear time to
one of the hardest problems we know.

### A short history

Euler's Königsberg paper (1736) started the subject. Kirchhoff used spanning trees of circuit graphs in 1847, and
Cayley counted trees in the 1850s to 1880s for chemistry. The word "graph" in this sense is due to J. J. Sylvester
in 1878. Maze-solving by what is in effect DFS goes back to Trémaux in the nineteenth century; an early
computer-age statement of BFS for shortest paths in a maze is E. F. Moore's 1959 paper "The shortest path through a
maze", and C. Y. Lee used it in 1961 to route wires on circuit boards. Kahn's topological sort appeared in 1962. The
modern view of DFS as a tool with timestamps and edge classes, and the linear-time algorithms for strong components
and biconnected components, are due to Hopcroft and Tarjan in papers from 1972 and 1973; they received the Turing
Award in 1986 for their work on the design and analysis of algorithms and data structures.

### A Mars aside

Rovers on Mars meet BFS in its most literal form. A rover's planner sees the ground ahead as a grid of cells marked
safe or hazardous, and the simplest question, "which cells can I reach, and by how few steps?", is a BFS from the
rover's cell. Because a command from Earth takes 4 to 24 minutes to arrive, rovers such as Perseverance plan many of
their own drives with on-board navigation software instead of waiting for each step to be approved. Real planners
weigh slopes and rocks with costs, which is a weighted problem: that is the next chapter.

## Check yourself

??? question "1. Can a graph have vertex degrees 3, 3, 2, 2, 1? Why or why not?"

    No. The degrees add to $3 + 3 + 2 + 2 + 1 = 11$, which is odd, but by the handshake lemma the sum of degrees is
    $2|E|$, always even. Equivalently, the number of odd-degree vertices (here three: 3, 3, 1) must be even.

??? question "2. A road map has one million junctions and 2.5 million roads. Compare the memory of an adjacency matrix and an adjacency list."

    The matrix has $10^6 \times 10^6 = 10^{12}$ cells; even at one bit per cell that is $1.25 \times 10^{11}$
    bytes, about 125 gigabytes, and almost all of them are 0. The list has $10^6$ heads and $2 \times 2.5 \times 10^6
    = 5 \times 10^6$ entries (each road appears in two lists), a few tens of megabytes. With roughly 5 neighbours
    per vertex, scanning all neighbours costs 5 steps with the list and $10^6$ with a matrix row.

??? question "3. Run BFS on the graph of Figure 15.1 starting from E. Give the queue after each step and the final distances."

    E's neighbours are B, C, F, G (in order).

    | Take | New (distance) | Queue after |
    |---|---|---|
    | E | B, C, F, G (1) | B C F G |
    | B | A, D (2) | C F G A D |
    | C | none | F G A D |
    | F | H (2) | G A D H |
    | G | none | A D H |
    | A, D, H | none | empty |

    Distances: E 0; B, C, F, G 1; A, D, H 2. Parents: B, C, F, G ← E; A ← B, D ← B, H ← F.

??? question "4. Write code that counts the shortest paths from s to every vertex of an unweighted graph. How many shortest paths go from A to H in Figure 15.1?"

    In BFS, $v$ lies on a shortest path through $u$ exactly when $\mathrm{dist}[v] = \mathrm{dist}[u] + 1$, so the
    number of shortest paths to $v$ is the sum over such $u$. Because BFS takes $u$ only after all vertices of the
    previous layer, `ways[u]` is final when it is used.

    ```python
    from collections import deque

    def count_shortest(adj, s):
        dist, ways = {s: 0}, {s: 1}
        q = deque([s])
        while q:
            u = q.popleft()
            for v in adj[u]:
                if v not in dist:                 # first time: one layer further
                    dist[v], ways[v] = dist[u] + 1, 0
                    q.append(v)
                if dist[v] == dist[u] + 1:        # u is a parent on some shortest path
                    ways[v] += ways[u]
        return dist, ways
    ```

    On Figure 15.1 from A it gives `{'A': 1, 'B': 1, 'C': 1, 'D': 1, 'E': 2, 'F': 3, 'G': 2, 'H': 5}`. There are 5
    shortest paths from A to H, all of length 4: A B D F H, A B E F H, A C E F H, A B E G H, A C E G H.

??? question "5. In a directed graph, why is it wrong to report a cycle whenever DFS meets an already-visited vertex? Give a small example."

    Take edges a→b, a→c, b→c. DFS from a visits b, then c (from b), finishes c and b, and then examines a→c and
    finds c already visited. But there is no cycle: a→c is a forward edge. Only an edge to a *grey* vertex (one
    still on the recursion stack) is a back edge and proves a cycle (Theorem 15.7). That is why the cycle test needs
    three states: white, grey, black. In an undirected graph two states plus the parent check suffice, because
    forward and cross edges cannot occur (Theorem 15.6).

??? question "6. Prove that every vertex reachable from s is reached by BFS, and that BFS from every vertex in turn finds the connected components of an undirected graph."

    Suppose $v$ is reachable from $s$ but never labelled; take such a $v$ closest to $s$ along some path $s = v_0,
    \dots, v_k = v$. Then $v_{k-1}$ is labelled, so it enters the queue and is explored, and the edge to $v$ makes
    BFS label $v$ if it is not labelled yet. Contradiction. Conversely BFS only labels vertices it reaches along
    edges. So one BFS labels exactly the vertices reachable from $s$, which in an undirected graph is $s$'s
    component. Starting a new BFS at each still-unlabelled vertex labels one new component each time. Every vertex
    and edge is handled by exactly one of these searches, so the total time is $O(V + E)$.

??? question "7. How many topological orders does the course graph of 15.4 have?"

    Ten. The graph has 7 vertices, so a brute-force check of all $7! = 5040$ orderings is instant:

    ```python
    import itertools
    C = {'intro': ['data'], 'discrete': ['data', 'theory'], 'data': ['algos', 'systems'],
         'algos': ['theory', 'compilers'], 'systems': ['compilers'], 'theory': [], 'compilers': []}
    count = 0
    for p in itertools.permutations(C):
        pos = {v: i for i, v in enumerate(p)}
        count += all(pos[u] < pos[v] for u in C for v in C[u])
    print(count)   # 10
    ```

    By hand: intro and discrete come first in either order (2 ways), then data. After data, the remaining four
    vertices algos, systems, theory, compilers must respect algos→theory, algos→compilers, systems→compilers. If
    algos is next: the orders of {systems, theory, compilers} with systems before compilers number 3. If systems is
    next: algos must come next, then theory and compilers in either order: 2. That is 5, times 2 is 10. Counting
    topological orders in general is #P-complete (Brightwell and Winkler, 1991), so this kind of brute force is only
    for tiny graphs.

??? question "8. Add the edge 8 → 1 to the graph of Figure 15.4. How many strongly connected components are there now? State a general rule."

    One. The condensation was the path {1,2,3} → {4,5,6} → {7,8}; the new edge goes from the last component back to
    the first, so every vertex can now reach every other (the program's `kosaraju` returns a single component of all
    8 vertices). In general, adding an edge from component $C'$ to component $C$ merges into one component $C$,
    $C'$ and every component that lies on some path from $C$ to $C'$ in the condensation; if there is no path from
    $C$ to $C'$, nothing merges.

??? question "9. Prove that an edge of an undirected graph is a bridge if and only if it lies on no cycle."

    If $\{u, v\}$ lies on a cycle, removing it leaves the rest of the cycle as a path from $u$ to $v$, so any walk
    that used the edge can detour round the cycle: the graph stays connected and the edge is not a bridge.
    Conversely, if removing $\{u,v\}$ leaves $u$ and $v$ still connected by some path $P$, then $P$ plus the edge is a
    cycle containing it. So if the edge is on no cycle, $u$ and $v$ are disconnected after removal, and it is a
    bridge. (This is exactly why the low-link test asks whether the subtree below the edge has a back edge going
    above it: a back edge closes a cycle.)

??? question "10. Which complete graphs $K_n$ (every pair of $n$ vertices joined) have an Euler circuit? Which have an Euler path but no circuit?"

    Every vertex of $K_n$ has degree $n - 1$. An Euler circuit needs all degrees even, so $n$ must be odd: $K_3,
    K_5, K_7, \dots$ (and trivially $K_1$). For an Euler path that is not a circuit you need exactly two odd
    vertices, but in $K_n$ either all $n$ vertices are odd or none are; with $n$ even all are odd, which is two odd
    vertices only when $n = 2$ (a single edge). So $K_2$ has an Euler path, and $K_4, K_6, \dots$ have neither.

??? question "11. Write DFS-based topological sort without recursion, so it works on a chain of 200 000 vertices."

    Keep a stack of pairs (vertex, iterator over its remaining neighbours). Advancing an iterator replaces the
    recursive loop; when it runs out, the vertex finishes.

    ```python
    def topo_iterative(adj):
        state, order = {v: 0 for v in adj}, []      # 0 white, 1 grey, 2 black
        for s in adj:
            if state[s]:
                continue
            state[s] = 1
            stack = [(s, iter(adj[s]))]
            while stack:
                u, it = stack[-1]
                for v in it:
                    if state[v] == 1:
                        raise ValueError("cycle")
                    if state[v] == 0:
                        state[v] = 1
                        stack.append((v, iter(adj[v])))
                        break
                else:                                # all neighbours done: u finishes
                    state[u] = 2
                    order.append(u)
                    stack.pop()
        return order[::-1]
    ```

    On the chain 0 → 1 → ... → 199999 it returns the 200 000 vertices from 0 to 199999 without hitting the
    recursion limit, and on the course graph it returns the same order as the recursive version, discrete intro data
    systems algos compilers theory. Each neighbour is drawn from an iterator once, so it is still $O(V + E)$.

## What you learned

- A graph is vertices and edges, directed or undirected; store sparse graphs as adjacency lists, in $\Theta(V + E)$
  space, so that searches run in time linear in the graph's size.
- BFS explores in rings with a queue and finds shortest paths by edge count in $O(V + E)$; the proof rests on the
  queue holding at most two consecutive distances.
- DFS records discovery and finish times; the intervals nest (parenthesis theorem), descendants are exactly the
  vertices reachable by white paths, and each edge is a tree, back, forward or cross edge.
- A directed graph has a cycle exactly when DFS finds a back edge; a DAG is topologically sorted by decreasing
  finish time or by Kahn's in-degree peeling.
- Strongly connected components come from Kosaraju's two passes or Tarjan's low-links, and they shrink every digraph
  to a DAG.
- Low-links in an undirected DFS find bridges (low[v] > disc[u]) and articulation points (low[v] ≥ disc[u]) in one
  pass.
- A graph is bipartite exactly when it has no odd cycle, and BFS parity finds either a two-colouring or an odd cycle;
  an Euler circuit exists exactly when every degree is even, and Hierholzer finds it in linear time.

**Next:** [Chapter 16](16-Shortest-Paths.md), shortest paths when the edges have lengths: Dijkstra, Bellman-Ford,
Floyd-Warshall and A*.

## Further reading

- T. H. Cormen, C. E. Leiserson, R. L. Rivest and C. Stein, *Introduction to Algorithms*, 4th ed., MIT Press, 2022,
  Chapter 20 (elementary graph algorithms: BFS, DFS, topological sort, strongly connected components).
- J. Kleinberg and É. Tardos, *Algorithm Design*, Addison-Wesley, 2005, Chapter 3 (graphs, bipartiteness, DAGs).
- R. Sedgewick and K. Wayne, *Algorithms*, 4th ed., Addison-Wesley, 2011, Chapter 4.1-4.2 (undirected and directed
  graphs, Kosaraju-Sharir and Tarjan).
- R. Tarjan, "Depth-first search and linear graph algorithms", *SIAM Journal on Computing* 1(2), 1972.
- J. Hopcroft and R. Tarjan, "Algorithm 447: Efficient algorithms for graph manipulation", *Communications of the
  ACM* 16(6), 1973.
- M. Sharir, "A strong-connectivity algorithm and its applications in data flow analysis", *Computers and
  Mathematics with Applications* 7(1), 1981.
- A. B. Kahn, "Topological sorting of large networks", *Communications of the ACM* 5(11), 1962.
- E. F. Moore, "The shortest path through a maze", *Proceedings of the International Symposium on the Theory of
  Switching*, Harvard University Press, 1959.
- L. Euler, "Solutio problematis ad geometriam situs pertinentis", *Commentarii Academiae Scientiarum Petropolitanae*
  8, 1741 (presented 1736); an English translation is in N. Biggs, E. K. Lloyd and R. J. Wilson, *Graph Theory
  1736-1936*, Oxford University Press, 1976.
- B. Aspvall, M. Plass and R. Tarjan, "A linear-time algorithm for testing the truth of certain quantified boolean
  formulas", *Information Processing Letters* 8(3), 1979 (2-SAT by strong components).
- On this site: [Breadth-first search](../../graphs/bfs.md), [Depth-first search](../../graphs/dfs.md),
  [Topological sort](../../graphs/topological-sort.md), [Strongly connected components](../../graphs/scc.md), and
  the [Graphs](../../graphs/index.md) overview.
- The graph theory behind this chapter, proved from the beginning: https://math.akadian.ca/books/.
