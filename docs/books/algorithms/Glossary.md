# Glossary

*Short definitions of the terms this book uses, from A to Z, each with a link to the chapter that teaches it.*

## A

**A* search**
Dijkstra's algorithm aimed at a target: the next vertex settled is the one with the smallest $d[v] + h(v)$, where $h$ is a heuristic guess of the remaining distance. With a consistent heuristic it is Dijkstra on reweighted edges, so it still finds a shortest path while exploring far less.
See [Chapter 16](16-Shortest-Paths.md#166-a-search-and-bidirectional-search).

**Abstract data type (ADT)**
A description of what a container does, its operations and the rules they obey, without saying how the data is laid out. A stack, a queue, a dictionary and a priority queue are ADTs; arrays, linked lists and heaps are ways to implement them.
See [Chapter 4](04-Lists-Stacks-and-Queues.md#46-abstract-data-types-and-implementations).

**Accounting method**
A way to prove amortized bounds: give each operation a fixed price, let cheap operations store their surplus as credit on the structure, and let expensive operations pay from that credit. If the credit never goes negative, the total price bounds the total actual cost.
See [Chapter 4](04-Lists-Stacks-and-Queues.md#42-dynamic-arrays-and-amortized-analysis).

**Activity selection**
Given time intervals, choose as many as possible that do not overlap; also called interval scheduling. The greedy rule "earliest finish first" is optimal, proved by greedy stays ahead.
See [Chapter 12](12-Greedy-Algorithms.md#122-activity-selection).

**Adaptive sort**
A sort that runs faster on inputs that are already nearly sorted, measured for example by the number of inversions or of runs. Insertion sort and Timsort are adaptive; a sort is optimally adaptive if it meets the lower bound for its measure.
See [Chapter 5](05-Sorting-by-Comparison.md#57-inversions-adaptive-sorting-and-timsort).

**Adjacency list**
A graph representation that keeps, for each vertex, a list of its neighbours. It takes $\Theta(V + E)$ space, which is why graph searches on sparse graphs run in linear time.
See [Chapter 15](15-Graphs-and-Graph-Search.md#151-graphs-the-words-and-the-data-structures).

**Adversary argument**
A lower-bound proof that imagines an opponent answering the algorithm's questions, choosing each answer to keep as many inputs possible as long as it can. In online algorithms the adversary is the one who picks the input sequence knowing the algorithm.
See [Chapter 2](02-Measuring-Cost.md#28-little-o-little-omega-and-lower-bounds) and [Chapter 24](24-Algorithms-for-Big-Data-and-Many-Processors.md#241-online-algorithms-and-competitive-ratio-ski-rental-paging).

**Aho-Corasick automaton**
A trie of all the patterns, with failure links and output links, that finds every occurrence of many patterns in one pass over the text. After $O(M)$ preprocessing for total pattern length $M$, a search costs $O(n + z)$ for $z$ matches.
See [Chapter 18](18-String-Algorithms.md#184-many-patterns-tries-and-aho-corasick).

**Akra-Bazzi theorem**
A generalisation of the master theorem to recurrences with unequal parts, $T(x) = \sum_i a_i T(b_i x) + g(x)$. Find the $p$ with $\sum_i a_i b_i^p = 1$; then $T$ is $x^p$ times a factor given by an integral of $g$.
See [Chapter 3](03-Recursion-and-Induction.md#36-the-master-theorem).

**Algorithm**
A finite, definite, effective procedure that takes an input and produces the right output for every instance of a problem. The word comes from the name of al-Khwarizmi, a scholar in ninth-century Baghdad.
See [Chapter 1](01-What-Is-an-Algorithm.md#11-recipes-for-machines).

**All-pairs shortest paths**
The problem of finding shortest-path distances between every pair of vertices. Floyd-Warshall solves it in $\Theta(V^3)$; Johnson's algorithm runs Dijkstra from every vertex after reweighting.
See [Chapter 16](16-Shortest-Paths.md#165-all-pairs-floyd-warshall-and-johnson).

**Amortized cost**
The total cost of a worst-case sequence of $N$ operations divided by $N$. It is a guarantee about every sequence, with no probability involved: a single operation may be expensive, but the average over the sequence is not.
See [Chapter 4](04-Lists-Stacks-and-Queues.md#42-dynamic-arrays-and-amortized-analysis) and [Chapter 21](21-Randomized-and-Amortized-Analysis.md#216-amortized-analysis-in-depth).

**Approximation ratio**
An algorithm for a minimisation problem is a $\rho$-approximation if its answer is at most $\rho \cdot \mathrm{OPT}$ on every input (for maximisation, at least $\mathrm{OPT}/\rho$). The ratio, also called the performance guarantee, is a worst-case promise proved against a computable bound on $\mathrm{OPT}$.
See [Chapter 23](23-Approximation-and-Parameterized-Algorithms.md#231-approximation-ratio-vertex-cover-2-approximation).

**APX-hard**
A problem that has no polynomial-time approximation scheme unless P = NP, even if it has a constant-ratio approximation. Vertex cover and MAX-3SAT are examples.
See [Chapter 23](23-Approximation-and-Parameterized-Algorithms.md#236-inapproximability-and-the-pcp-theorem).

**Array**
A block of memory cells of equal size holding items in order. The address of `a[i]` is the base address plus $w \cdot i$, so indexing costs $O(1)$, while inserting or deleting in the middle moves $O(n)$ items.
See [Chapter 4](04-Lists-Stacks-and-Queues.md#41-arrays).

**Articulation point**
A vertex of a connected undirected graph whose removal disconnects it. DFS low-links find them all in one pass: a non-root $u$ is one when some child $v$ has $\mathrm{low}[v] \ge \mathrm{disc}[u]$, and the root is one when it has two or more children.
See [Chapter 15](15-Graphs-and-Graph-Search.md#156-bridges-and-articulation-points).

**Augmenting path**
In a flow network, a path from source to sink in the residual graph; pushing its bottleneck capacity along it increases the flow. In a matching, a path that alternates between unmatched and matched edges and starts and ends at unmatched vertices; flipping it adds one edge.
See [Chapter 17](17-Spanning-Trees-Flows-and-Matching.md#173-network-flow-ford-fulkerson-and-residual-graphs) and [Chapter 17](17-Spanning-Trees-Flows-and-Matching.md#176-bipartite-matching).

**Average case**
The average cost of an algorithm over all inputs of size $n$, for a stated probability distribution on the inputs. It differs from expected time, which averages over the algorithm's own random choices on the worst input.
See [Chapter 2](02-Measuring-Cost.md#22-worst-best-and-average-case).

**AVL tree**
A binary search tree in which the heights of the two subtrees of every node differ by at most 1, introduced by Adelson-Velsky and Landis in 1962. Rotations restore the rule after each update, and the height stays below $1.44\log_2(n+1)$.
See [Chapter 8](08-Trees-and-Balanced-Search-Trees.md#83-avl-trees).

## B

**Back edge**
In a depth-first search, an edge from a vertex to one of its ancestors (a grey vertex on the current stack). A directed graph has a cycle exactly when DFS finds a back edge.
See [Chapter 15](15-Graphs-and-Graph-Search.md#153-depth-first-search).

**Backtracking**
A depth-first search of the state-space tree that, at every node, tests whether the partial solution can still be extended to a valid one, and if not prunes (skips) the whole subtree. The test must be safe and should be cheap.
See [Chapter 14](14-Backtracking-and-Branch-and-Bound.md#141-exhaustive-search-the-state-space-tree).

**Base case**
The part of a recursive definition or algorithm that answers small inputs directly, without recursion. In a proof by induction, the base case is the first value checked directly.
See [Chapter 3](03-Recursion-and-Induction.md#31-a-function-that-calls-itself) and [Chapter 3](03-Recursion-and-Induction.md#32-mathematical-induction).

**Bellman-Ford algorithm**
A single-source shortest-path algorithm that relaxes every edge $V - 1$ times, in $O(VE)$ time. It handles negative edge weights, and one more round that still improves some distance reveals a negative cycle.
See [Chapter 16](16-Shortest-Paths.md#163-bellman-ford).

**Big-O notation**
$f(n) = O(g(n))$ means there are constants $c > 0$ and $n_0$ such that $f(n) \le c\,g(n)$ for all $n \ge n_0$: $f$ grows at most as fast as $g$, up to a constant factor. It is an upper bound.
See [Chapter 2](02-Measuring-Cost.md#23-big-o-big-omega-and-big-theta).

**Big-Omega notation**
$f(n) = \Omega(g(n))$ means there are constants $c > 0$ and $n_0$ such that $f(n) \ge c\,g(n)$ for all $n \ge n_0$: $f$ grows at least as fast as $g$. It is a lower bound.
See [Chapter 2](02-Measuring-Cost.md#23-big-o-big-omega-and-big-theta).

**Big-Theta notation**
$f(n) = \Theta(g(n))$ means both $f(n) = O(g(n))$ and $f(n) = \Omega(g(n))$: $f$ grows exactly as fast as $g$, up to constant factors.
See [Chapter 2](02-Measuring-Cost.md#23-big-o-big-omega-and-big-theta).

**Binary heap**
A complete binary tree stored in an array, with the children of position $i$ at $2i + 1$ and $2i + 2$, that satisfies the heap property. Insert and extract-min take $O(\log n)$ by sifting up or down, and build-heap takes $O(n)$.
See [Chapter 9](09-Heaps-and-Priority-Queues.md#92-binary-heaps-in-an-array).

**Binary lifting**
A method for lowest common ancestors that stores, for each node, its $2^k$-th ancestor for every $k$. After $O(n \log n)$ preprocessing it answers each query in $O(\log n)$ by jumping up in powers of two.
See [Chapter 10](10-Union-Find-and-Range-Queries.md#106-sparse-tables-for-range-minimum-rmq-and-lca).

**Binary search**
Searching a sorted list by comparing with the middle item and discarding the half that cannot hold the target. It needs $\lceil \log_2(n+1) \rceil$ probes, which is optimal, and works for any monotone yes/no question over an ordered range.
See [Chapter 7](07-Searching-and-Hashing.md#71-linear-and-binary-search).

**Binary search tree (BST)**
A binary tree with a key in every node such that all keys in a node's left subtree are smaller and all in its right subtree larger (the search-tree property). Search, insert, delete, minimum and successor all cost $O(h)$ for height $h$.
See [Chapter 8](08-Trees-and-Balanced-Search-Trees.md#82-binary-search-trees).

**Binary tree**
A rooted tree in which every node has at most two children, called left and right. A binary tree of height $h$ has at most $2^{h+1} - 1$ nodes.
See [Chapter 8](08-Trees-and-Balanced-Search-Trees.md#81-trees-the-words-and-the-four-walks).

**Bipartite graph**
A graph whose vertices split into two sides so that every edge joins the two sides. A graph is bipartite exactly when it has no odd cycle (König), and BFS finds either a two-colouring or an odd cycle.
See [Chapter 15](15-Graphs-and-Graph-Search.md#157-bipartite-graphs-cycles-and-euler-tours).

**Bloom filter**
A bit array of $m$ bits with $k$ hash functions that answers set membership approximately. It never gives false negatives; its false-positive rate is about $0.6185^{m/n}$ at the best $k = (m/n)\ln 2$.
See [Chapter 7](07-Searching-and-Hashing.md#77-bloom-filters).

**Blossom algorithm**
Edmonds's 1965 algorithm for maximum matching in general (not necessarily bipartite) graphs. It shrinks odd cycles, the blossoms, that defeat the bipartite method, and runs in polynomial time.
See [Chapter 17](17-Spanning-Trees-Flows-and-Matching.md#176-bipartite-matching).

**Borůvka's algorithm**
A minimum-spanning-tree algorithm in which every component, in each round, adds its lightest outgoing edge. The number of components at least halves each round, so there are $O(\log V)$ rounds and $O(E \log V)$ time.
See [Chapter 17](17-Spanning-Trees-Flows-and-Matching.md#172-kruskal-prim-and-boruvka).

**Branch and bound**
Exhaustive search for an optimisation problem that keeps the best solution found so far (the incumbent) and prunes every node whose optimistic bound cannot beat it. Nodes can be explored depth first or best first.
See [Chapter 14](14-Backtracking-and-Branch-and-Bound.md#144-pruning-bounding-functions-branch-and-bound) and [Chapter 23](23-Approximation-and-Parameterized-Algorithms.md#238-heuristics-in-practice-local-search-sat-solvers-and-integer-programming-solvers).

**Breadth-first search (BFS)**
A graph search that explores outwards in rings, using a queue: first the start, then its neighbours, then theirs. It runs in $O(V + E)$ and finds shortest paths by number of edges.
See [Chapter 15](15-Graphs-and-Graph-Search.md#152-breadth-first-search-and-shortest-paths).

**Brent's theorem**
A greedy scheduler runs a computation of work $W$ and span $S$ on $p$ processors in time $T_p \le W/p + S$ (Brent 1974; Graham 1966). It is within a factor 2 of the best possible schedule.
See [Chapter 24](24-Algorithms-for-Big-Data-and-Many-Processors.md#245-parallel-algorithms-work-and-span-brents-theorem-prefix-sums-mapreduce).

**Bridge**
An edge of a connected undirected graph whose removal disconnects it. In a DFS, the tree edge from $u$ to its child $v$ is a bridge exactly when $\mathrm{low}[v] > \mathrm{disc}[u]$.
See [Chapter 15](15-Graphs-and-Graph-Search.md#156-bridges-and-articulation-points).

**B-tree**
A balanced search tree whose nodes hold many keys (between $t - 1$ and $2t - 1$ for minimum degree $t$) and branch many ways, so that a search reads only a few disk blocks. It grows and shrinks only at the root, so all leaves have the same depth.
See [Chapter 8](08-Trees-and-Balanced-Search-Trees.md#85-b-trees-for-disks-and-databases) and [Chapter 24](24-Algorithms-for-Big-Data-and-Many-Processors.md#243-external-memory-the-io-model-external-merge-sort-b-trees-again).

**Bucket sort**
A sort for keys spread over $[0, 1)$: divide the interval into $n$ equal buckets, drop each key into its bucket, sort the buckets and concatenate. It takes expected linear time on uniformly distributed keys, since $E[\sum_i n_i^2] = 2n - 1$.
See [Chapter 6](06-Sorting-in-Linear-Time-and-Selection.md#63-bucket-sort).

**Burrows-Wheeler transform (BWT)**
The last column of the sorted list of all rotations of $T\$$. It groups equal letters into runs, can be inverted with the LF mapping, and is the basis of the FM-index and the bzip2 compressor.
See [Chapter 18](18-String-Algorithms.md#186-suffix-trees-suffix-automata-and-the-burrows-wheeler-transform).

**Bézout's identity**
For integers $a, b$ not both 0 there are integers $x, y$ with $ax + by = \gcd(a, b)$. The extended Euclidean algorithm finds such $x$ and $y$.
See [Chapter 19](19-Number-Theoretic-Algorithms.md#191-gcd-and-extended-euclid).

## C

**Cache-oblivious algorithm**
An algorithm designed for the I/O model that is efficient for every memory size $M$ and block size $B$ without knowing them. Usually it divides and conquers until the problem fits; it is then optimal at every level of the memory hierarchy at once.
See [Chapter 24](24-Algorithms-for-Big-Data-and-Many-Processors.md#244-cache-oblivious-algorithms).

**Certificate**
A piece of evidence that lets an answer be checked quickly, also called a witness. In NP, every yes-instance has a certificate of polynomial length that a polynomial-time verifier accepts; an odd cycle is a certificate that a graph is not bipartite.
See [Chapter 22](22-NP-Completeness.md#222-p-and-np-via-certificates) and [Chapter 15](15-Graphs-and-Graph-Search.md#157-bipartite-graphs-cycles-and-euler-tours).

**Chernoff bound**
A tail bound for a sum of independent 0/1 random variables: the probability that it is far from its mean falls exponentially. It is what makes "with high probability" statements and amplification work.
See [Chapter 21](21-Randomized-and-Amortized-Analysis.md#213-tail-bounds-markov-chebyshev-chernoff).

**Chinese remainder theorem (CRT)**
If $m_1, \ldots, m_k$ are pairwise coprime with product $M$, then any system $x \equiv r_i \pmod{m_i}$ has exactly one solution mod $M$. As an algorithm it solves the congruences one at a time and splits arithmetic mod $M$ into independent small parts.
See [Chapter 19](19-Number-Theoretic-Algorithms.md#196-the-chinese-remainder-theorem-as-an-algorithm).

**Christofides' algorithm**
A $\tfrac32$-approximation for metric TSP (1976): take a minimum spanning tree, add a minimum-weight perfect matching on its odd-degree vertices, find an Euler circuit, and shortcut repeated vertices.
See [Chapter 23](23-Approximation-and-Parameterized-Algorithms.md#232-metric-tsp-mst-doubling-and-christofides).

**Church-Turing thesis**
The claim that anything computable by an algorithm, in the informal sense, can be computed by a Turing machine. It is a thesis, not a theorem, supported by the fact that every proposed model of computation has turned out to be equivalent.
See [Chapter 1](01-What-Is-an-Algorithm.md#18-turing-machines-and-the-limits-of-computation).

**Clique**
A set of vertices every two of which are joined by an edge. Deciding whether a graph has a clique of size $k$ is NP-complete, since cliques in a graph are independent sets in its complement.
See [Chapter 22](22-NP-Completeness.md#225-a-chain-of-reductions-proved).

**Closest pair of points**
The problem of finding the two nearest points among $n$ in the plane. Divide and conquer solves it in $O(n \log n)$: the strip lemma means each point near the dividing line needs comparing with only seven others.
See [Chapter 11](11-Divide-and-Conquer.md#116-closest-pair-of-points-in-on-log-n).

**Comparison sort**
A sorting algorithm that learns about the items only by comparing pairs of keys. Every comparison sort needs $\lceil \log_2 n! \rceil \approx n\log_2 n$ comparisons in the worst case.
See [Chapter 5](05-Sorting-by-Comparison.md#51-why-sorting-matters) and [Chapter 5](05-Sorting-by-Comparison.md#56-the-n-log-n-lower-bound-for-comparison-sorts).

**Competitive ratio**
An online algorithm is $c$-competitive if, on every input sequence, its cost is at most $c$ times that of the best offline algorithm (plus a constant). The smallest such $c$ is its competitive ratio.
See [Chapter 24](24-Algorithms-for-Big-Data-and-Many-Processors.md#241-online-algorithms-and-competitive-ratio-ski-rental-paging).

**Conjunctive normal form (CNF)**
A Boolean formula written as an AND of clauses, each an OR of literals. SAT is usually stated for CNF formulas, and Tseitin's encoding turns any circuit into one of linear size.
See [Chapter 22](22-NP-Completeness.md#222-p-and-np-via-certificates).

**Connected component**
A maximal set of vertices of an undirected graph in which every two are joined by a path. BFS or DFS finds all components in $O(V + E)$.
See [Chapter 15](15-Graphs-and-Graph-Search.md#151-graphs-the-words-and-the-data-structures).

**Co-NP**
The class of decision problems whose no-instances have short certificates checkable in polynomial time, such as "this formula is unsatisfiable". Whether NP = co-NP is open.
See [Chapter 22](22-NP-Completeness.md#226-karps-21-problems-co-np-and-pspace).

**Consensus**
The problem of getting processes in a distributed system to agree on one value: all deciders agree, the value was someone's input, and every correct process decides. With up to $f$ crashes it takes $f + 1$ synchronous rounds; asynchronously it cannot be guaranteed (FLP).
See [Chapter 24](24-Algorithms-for-Big-Data-and-Many-Processors.md#246-distributed-algorithms-briefly-consensus-and-why-it-is-hard).

**Consistent heuristic**
A heuristic for A* with $h(t) = 0$ and $h(u) \le w(u, v) + h(v)$ for every edge: the guess cannot drop by more than the edge it crosses. With a consistent heuristic A* never needs to reopen a vertex. Also called monotone.
See [Chapter 16](16-Shortest-Paths.md#166-a-search-and-bidirectional-search).

**Constraint propagation**
Keeping, for every variable, the set of values still possible and repeatedly applying rules that remove impossible ones. Combined with branching on the variable with the fewest candidates, it solves Sudoku in a handful of nodes.
See [Chapter 14](14-Backtracking-and-Branch-and-Bound.md#143-n-queens-sudoku-with-constraint-propagation).

**Convex hull**
The smallest convex polygon containing a set of points. Gift wrapping finds it in $O(nh)$ for $h$ hull vertices; Graham scan and Andrew's monotone chain in $O(n \log n)$, which is optimal because hulls can be used to sort.
See [Chapter 20](20-Computational-Geometry.md#203-convex-hulls).

**Cook-Levin theorem**
SAT is NP-complete (Cook 1971, Levin 1973). The proof writes "the verifier accepts some certificate" as a formula over the cells of a tableau of the verifier's computation.
See [Chapter 22](22-NP-Completeness.md#224-the-cook-levin-theorem).

**Counting sort**
A stable sort for integer keys in a small range $0, \ldots, k-1$: count how many items have each key, turn the counts into starting positions, and place each item. It takes $\Theta(n + k)$ time and is the engine of radix sort.
See [Chapter 6](06-Sorting-in-Linear-Time-and-Selection.md#61-beating-n-log-n-by-not-comparing-counting-sort).

**Count-min sketch**
A streaming summary of item frequencies: $d$ rows of $w$ counters, one hash function per row, with each item counted in one cell per row and estimated by the minimum over its cells. With $w = \lceil e/\varepsilon \rceil$ and $d = \lceil \ln(1/\delta) \rceil$ the estimate is never too low and exceeds the truth by more than $\varepsilon n$ with probability at most $\delta$.
See [Chapter 24](24-Algorithms-for-Big-Data-and-Many-Processors.md#242-streaming-misra-gries-count-min-sketch-hyperloglog).

**Cuckoo hashing**
A hash table in which every key lives in one of exactly two places, $T_1[h_1(x)]$ or $T_2[h_2(x)]$, so a lookup reads at most two cells (Pagh and Rodler, 2001). An insertion that finds both taken kicks out the occupant, which moves to its other place.
See [Chapter 7](07-Searching-and-Hashing.md#76-perfect-hashing-cuckoo-hashing-and-robin-hood-hashing).

**Cut property**
For any cut of a weighted graph, a lightest edge crossing it belongs to some minimum spanning tree. It is the reason Kruskal's, Prim's and Borůvka's algorithms are correct.
See [Chapter 17](17-Spanning-Trees-Flows-and-Matching.md#171-minimum-spanning-trees-the-cut-and-cycle-properties).

## D

**DAG (directed acyclic graph)**
A directed graph with no directed cycle. Every DAG has a topological order, shortest and longest paths in it take linear time, and every dynamic program is a computation over a DAG of subproblems.
See [Chapter 15](15-Graphs-and-Graph-Search.md#151-graphs-the-words-and-the-data-structures) and [Chapter 13](13-Dynamic-Programming.md#132-the-recipe).

**Decidable problem**
A decision problem for which some Turing machine (equivalently, some program) always halts with the right answer. A problem with no such machine is undecidable.
See [Chapter 1](01-What-Is-an-Algorithm.md#18-turing-machines-and-the-limits-of-computation).

**Decision problem**
A problem whose answer is yes or no for every input. Complexity classes such as P and NP are defined for decision problems; optimisation problems are turned into them by asking "is there a solution of value at most $k$?".
See [Chapter 1](01-What-Is-an-Algorithm.md#18-turing-machines-and-the-limits-of-computation) and [Chapter 22](22-NP-Completeness.md#221-easy-and-hard-problems).

**Decision tree**
A tree that records every comparison an algorithm can make, branching on each outcome, with one leaf for each possible result. A comparison sort's tree needs at least $n!$ leaves, so its height, the worst-case number of comparisons, is at least $\log_2 n!$.
See [Chapter 5](05-Sorting-by-Comparison.md#56-the-n-log-n-lower-bound-for-comparison-sorts) and [Chapter 2](02-Measuring-Cost.md#28-little-o-little-omega-and-lower-bounds).

**Decrease-key**
The priority-queue operation that makes one item's key smaller. In a binary heap it needs a position index to find the item, then a sift-up; Fibonacci heaps do it in $O(1)$ amortized.
See [Chapter 9](09-Heaps-and-Priority-Queues.md#94-decrease-key-and-indexed-heaps) and [Chapter 9](09-Heaps-and-Priority-Queues.md#96-fibonacci-heaps-and-pairing-heaps).

**Delaunay triangulation**
The triangulation of a set of sites obtained by joining two sites whenever their Voronoi cells share an edge. A triangle is Delaunay exactly when its circumcircle contains no other site (the empty-circle property).
See [Chapter 20](20-Computational-Geometry.md#206-voronoi-diagrams-delaunay-triangulations-and-k-d-trees).

**Depth-first search (DFS)**
A graph search that goes as deep as it can along one path before backing up, recording discovery and finish times. It runs in $O(V + E)$ and underlies cycle detection, topological sort, strongly connected components, bridges and articulation points.
See [Chapter 15](15-Graphs-and-Graph-Search.md#153-depth-first-search).

**Dijkstra's algorithm**
A single-source shortest-path algorithm for non-negative edge weights that repeatedly settles the unsettled vertex with the smallest tentative distance and relaxes its edges. It costs $O(V^2)$ with an array, $O((V + E)\log V)$ with a binary heap, and $O(E + V\log V)$ with a Fibonacci heap.
See [Chapter 16](16-Shortest-Paths.md#162-dijkstras-algorithm).

**Dinic's algorithm**
A maximum-flow algorithm that works in phases: BFS builds the level graph of the residual network, and DFS finds a blocking flow in it. There are at most $V - 1$ phases, for $O(V^2 E)$ time.
See [Chapter 17](17-Spanning-Trees-Flows-and-Matching.md#175-edmonds-karp-and-dinic).

**Discrete Fourier transform (DFT)**
The list of values of a polynomial with coefficients $a_0, \ldots, a_{N-1}$ at the $N$ complex $N$-th roots of unity. The fast Fourier transform computes it in $O(N \log N)$, and its inverse is the same algorithm with the conjugate root.
See [Chapter 11](11-Divide-and-Conquer.md#117-the-fast-fourier-transform).

**Divide and conquer**
A design technique with three steps: divide the input into smaller instances of the same problem, conquer each recursively, and combine their answers. Its cost is a recurrence $T(n) = aT(n/b) + f(n)$, solved by a recursion tree or the master theorem.
See [Chapter 11](11-Divide-and-Conquer.md#111-the-pattern-merge-sort-and-binary-search-seen-again).

**Duality (linear programming)**
Every linear program has a dual. Weak duality: every feasible solution of the dual bounds the primal optimum. Strong duality: if the primal has an optimum, the dual optimum has the same value, so the dual solution certifies optimality.
See [Chapter 23](23-Approximation-and-Parameterized-Algorithms.md#235-linear-programming-and-lp-relaxation-with-rounding).

**Dynamic array**
An array that grows when full by moving to a block a constant factor larger, as Python's `list` does. Growing by a factor makes appends cost $O(1)$ amortized; growing by a constant amount would cost $\Theta(n)$ per append.
See [Chapter 4](04-Lists-Stacks-and-Queues.md#42-dynamic-arrays-and-amortized-analysis).

**Dynamic optimality conjecture**
The conjecture of Sleator and Tarjan (1985) that splay trees are dynamically optimal: on every sequence of accesses they cost within a constant factor of the best binary search tree algorithm for that sequence. It is still open.
See [Chapter 8](08-Trees-and-Balanced-Search-Trees.md#87-splay-trees-self-adjusting) and [Chapter 21](21-Randomized-and-Amortized-Analysis.md#216-amortized-analysis-in-depth).

**Dynamic programming (DP)**
Solving a problem whose recursive subproblems overlap by storing each subproblem's answer once, in a memo (top down) or a table filled in a fixed order (bottom up). The recipe is: state, transition, base cases, order; time is states times work per state.
See [Chapter 13](13-Dynamic-Programming.md#131-overlapping-subproblems-fibonacci-three-ways) and [Chapter 13](13-Dynamic-Programming.md#132-the-recipe).

## E

**Edit distance**
The minimum number of single-letter insertions, deletions and substitutions that turn one string into another, also called Levenshtein distance. Dynamic programming over an $(m+1) \times (n+1)$ grid computes it in $O(mn)$, and under SETH nothing is much faster.
See [Chapter 13](13-Dynamic-Programming.md#134-sequences-lcs-edit-distance-alignment) and [Chapter 25](25-Where-Algorithms-Go.md#252-fine-grained-complexity-3sum-seth-edit-distance).

**Edmonds-Karp algorithm**
Ford-Fulkerson that always augments along a shortest path (fewest edges) in the residual graph, found by BFS. It makes at most $VE$ augmentations, so it runs in $O(VE^2)$ whatever the capacities.
See [Chapter 17](17-Spanning-Trees-Flows-and-Matching.md#175-edmonds-karp-and-dinic).

**Entropy**
Shannon's measure of the information in a source emitting symbol $i$ with probability $p_i$: $H = -\sum_i p_i \log_2 p_i$ bits per symbol. No prefix code does better on average, and Huffman's code is within one bit of it.
See [Chapter 12](12-Greedy-Algorithms.md#124-huffman-coding).

**Euclid's algorithm**
The algorithm that computes $\gcd(a, b)$ by repeating $\gcd(a, b) = \gcd(b, a \bmod b)$ until the second number is 0. It takes $O(\log b)$ steps, with consecutive Fibonacci numbers as the worst case (Lamé).
See [Chapter 1](01-What-Is-an-Algorithm.md#17-euclids-algorithm) and [Chapter 19](19-Number-Theoretic-Algorithms.md#191-gcd-and-extended-euclid).

**Euler circuit**
A closed walk that uses every edge of a graph exactly once; an Euler path need not return to its start. A connected multigraph has an Euler circuit exactly when every vertex has even degree, and Hierholzer's algorithm finds one in linear time.
See [Chapter 15](15-Graphs-and-Graph-Search.md#157-bipartite-graphs-cycles-and-euler-tours).

**Exchange argument**
A proof that a greedy algorithm is optimal by transforming an optimal solution, one swap at a time, into the greedy one without making it worse. It proves earliest deadline first, Huffman coding and the cut property.
See [Chapter 12](12-Greedy-Algorithms.md#123-scheduling-to-minimise-lateness) and [Chapter 12](12-Greedy-Algorithms.md#124-huffman-coding).

**Expectation**
The probability-weighted average of the values of a random variable, $E[X] = \sum_x x\,P(X = x)$. Linearity of expectation, $E[X + Y] = E[X] + E[Y]$, holds even for dependent variables.
See [Chapter 21](21-Randomized-and-Amortized-Analysis.md#211-las-vegas-monte-carlo-and-the-tools-of-expectation).

**Exponential search**
Searching a sorted list for an item near the start by probing positions 1, 3, 7, 15, ... until passing it and then binary searching the last gap, in $O(\log i)$ for an item at position $i$. Also called galloping; Timsort uses it when merging.
See [Chapter 7](07-Searching-and-Hashing.md#71-linear-and-binary-search) and [Chapter 5](05-Sorting-by-Comparison.md#57-inversions-adaptive-sorting-and-timsort).

**Exponential time hypothesis (ETH)**
The conjecture (Impagliazzo and Paturi) that 3-SAT on $n$ variables needs $2^{cn}$ time for some $c > 0$. The strong exponential time hypothesis is a sharper version.
See [Chapter 14](14-Backtracking-and-Branch-and-Bound.md#146-exact-exponential-algorithms-measuring-search-trees) and [Chapter 25](25-Where-Algorithms-Go.md#252-fine-grained-complexity-3sum-seth-edit-distance).

**Extended Euclidean algorithm**
Euclid's algorithm with extra bookkeeping that also finds integers $x, y$ with $ax + by = \gcd(a, b)$. When $\gcd(a, m) = 1$ it gives the inverse of $a$ mod $m$.
See [Chapter 19](19-Number-Theoretic-Algorithms.md#191-gcd-and-extended-euclid).

**External merge sort**
Sorting data too big for memory in the I/O model: sort memory-sized runs, then merge them about $M/B$ at a time. It takes $\Theta(\frac NB \log_{M/B} \frac NB)$ block transfers, which is optimal.
See [Chapter 24](24-Algorithms-for-Big-Data-and-Many-Processors.md#243-external-memory-the-io-model-external-merge-sort-b-trees-again).

## F

**Fast exponentiation**
Computing $a^e$ by repeated squaring, using $a^e = (a^{e/2})^2$ for even $e$, in $O(\log e)$ multiplications; also called square-and-multiply. Mod $m$ it computes $a^e \bmod m$ in about $2\log_2 e$ multiplications.
See [Chapter 3](03-Recursion-and-Induction.md#31-a-function-that-calls-itself) and [Chapter 19](19-Number-Theoretic-Algorithms.md#192-modular-arithmetic-fast-powering-and-inverses).

**Fast Fourier transform (FFT)**
A divide-and-conquer algorithm that evaluates a polynomial at the $N$-th roots of unity in $O(N \log N)$, using the halving lemma (Cooley-Tukey). With its inverse it multiplies polynomials and big integers in $O(n \log n)$ arithmetic operations.
See [Chapter 11](11-Divide-and-Conquer.md#117-the-fast-fourier-transform).

**Fenwick tree**
An array $t$ in which $t_i$ stores the sum of the $\mathrm{lowbit}(i)$ elements ending at position $i$, where $\mathrm{lowbit}(i)$ is the lowest 1-bit of $i$ (`i & -i`). Prefix sums and point updates each take $O(\log n)$; also called a binary indexed tree.
See [Chapter 10](10-Union-Find-and-Range-Queries.md#104-fenwick-trees).

**Fermat test**
A probabilistic primality test: pick $a$ and check whether $a^{n-1} \equiv 1 \pmod n$. If not, $a$ is a Fermat witness and $n$ is composite; if so, $n$ may still be composite ($a$ is then a Fermat liar), and Carmichael numbers fool it for every coprime base.
See [Chapter 19](19-Number-Theoretic-Algorithms.md#194-primality-fermat-miller-rabin-and-aks).

**Fermat's little theorem**
If $p$ is prime and $p$ does not divide $a$, then $a^{p-1} \equiv 1 \pmod p$. So mod a prime, $a^{p-2}$ is the inverse of $a$.
See [Chapter 19](19-Number-Theoretic-Algorithms.md#192-modular-arithmetic-fast-powering-and-inverses).

**Fibonacci heap**
A lazy collection of heap-ordered trees with mark bits and cascading cuts (Fredman and Tarjan, 1984). It gives $O(1)$ amortized insert, meld and decrease-key and $O(\log n)$ amortized extract-min, proved with the potential $\Phi = t + 2m$, and so the best bound for Dijkstra's algorithm.
See [Chapter 9](09-Heaps-and-Priority-Queues.md#96-fibonacci-heaps-and-pairing-heaps).

**Fine-grained complexity**
The study of exact exponents of problems inside P, relating them by fine-grained reductions to a few conjectures (3SUM, APSP, SETH). Under SETH, for example, edit distance and LCS need quadratic time.
See [Chapter 25](25-Where-Algorithms-Go.md#252-fine-grained-complexity-3sum-seth-edit-distance).

**Fisher-Yates shuffle**
The algorithm that makes a uniformly random permutation: for each position $i$ from the first to the second-last, swap item $i$ with a uniformly random item among positions $i, \ldots, n-1$. Each of the $n!$ sequences of choices gives a different permutation.
See [Chapter 21](21-Randomized-and-Amortized-Analysis.md#215-reservoir-sampling-and-the-fisher-yates-shuffle).

**Fixed-parameter tractable (FPT)**
A problem with a parameter $k$ is fixed-parameter tractable if it can be solved in time $f(k) \cdot n^{O(1)}$ for some function $f$. Vertex cover is FPT, solvable in $O(2^k m)$ by a bounded search tree.
See [Chapter 23](23-Approximation-and-Parameterized-Algorithms.md#237-fixed-parameter-tractability-vertex-cover-in-o2k-n).

**Flow network**
A directed graph with a source $s$, a sink $t$ and a capacity on each edge. A flow assigns each edge an amount within its capacity, with flow in equal to flow out at every vertex except $s$ and $t$; its value is the net flow leaving $s$.
See [Chapter 17](17-Spanning-Trees-Flows-and-Matching.md#173-network-flow-ford-fulkerson-and-residual-graphs).

**Floyd's cycle finding**
Finding the cycle of a sequence $x_{i+1} = f(x_i)$ with two pointers, a tortoise moving one step and a hare moving two, until they meet. It needs only constant memory and is used in Pollard's rho.
See [Chapter 19](19-Number-Theoretic-Algorithms.md#195-factoring-trial-division-and-pollards-rho).

**Floyd-Warshall algorithm**
An all-pairs shortest-path algorithm that, by dynamic programming, allows intermediate vertices $1, 2, \ldots, k$ in turn. It runs in $\Theta(V^3)$ time and works with negative edges as long as there is no negative cycle.
See [Chapter 16](16-Shortest-Paths.md#165-all-pairs-floyd-warshall-and-johnson).

**FLP theorem**
Fischer, Lynch and Paterson (1985): in an asynchronous message-passing system in which even one process may crash, no deterministic consensus algorithm is guaranteed to terminate. Real protocols keep safety always and gain liveness when the network behaves.
See [Chapter 24](24-Algorithms-for-Big-Data-and-Many-Processors.md#246-distributed-algorithms-briefly-consensus-and-why-it-is-hard).

**Ford-Fulkerson method**
The maximum-flow method that repeatedly finds an augmenting path in the residual graph and pushes its bottleneck capacity along it, until none is left. With integer capacities it ends with an integer maximum flow.
See [Chapter 17](17-Spanning-Trees-Flows-and-Matching.md#173-network-flow-ford-fulkerson-and-residual-graphs).

**Fractional knapsack**
The knapsack problem in which items may be split. Taking items in order of decreasing value per unit weight, splitting only the last, is optimal; the 0/1 version, where items must be taken whole, is NP-hard.
See [Chapter 12](12-Greedy-Algorithms.md#125-fractional-knapsack-vs-01-knapsack).

**Fully polynomial-time approximation scheme (FPTAS)**
An algorithm that, for every $\varepsilon > 0$, finds a solution within a factor $1 + \varepsilon$ of optimal in time polynomial in both $n$ and $1/\varepsilon$. Rounding profits gives one for knapsack; strongly NP-hard problems have none unless P = NP.
See [Chapter 23](23-Approximation-and-Parameterized-Algorithms.md#234-a-knapsack-fptas).

## G

**Gale-Shapley algorithm**
The proposal algorithm for stable matching (1962): each free proposer proposes to the next receiver on its list, who keeps the best offer so far. It ends after at most $n^2$ proposals with a stable matching, the best possible for every proposer.
See [Chapter 17](17-Spanning-Trees-Flows-and-Matching.md#177-assignment-min-cost-flow-and-stable-matching).

**Gift wrapping**
A convex-hull algorithm, also called the Jarvis march: start at an extreme point and repeatedly find the point that makes every other point lie to the left, as if wrapping string around the set. It takes $O(nh)$ time for $h$ hull vertices.
See [Chapter 20](20-Computational-Geometry.md#203-convex-hulls).

**Graham scan**
A convex-hull algorithm (1972): sort the points by angle around the lowest one, then scan them with a stack, popping every point that makes a right turn. It runs in $O(n \log n)$.
See [Chapter 20](20-Computational-Geometry.md#203-convex-hulls).

**Graph**
A set $V$ of vertices and a set $E$ of edges joining pairs of them. Edges are unordered pairs in an undirected graph and ordered pairs in a directed graph, and may carry weights.
See [Chapter 15](15-Graphs-and-Graph-Search.md#151-graphs-the-words-and-the-data-structures).

**Greedy algorithm**
An algorithm that builds a solution piece by piece, at each step making the choice that looks best by some local rule and never revisiting it. It is fast but must be proved correct, and is often wrong.
See [Chapter 12](12-Greedy-Algorithms.md#121-the-greedy-idea-and-when-it-fails).

**Greedy stays ahead**
A proof technique for greedy algorithms: show that after every step the greedy partial solution is at least as good as the first steps of any optimal one. It proves that earliest finish first is optimal for activity selection.
See [Chapter 12](12-Greedy-Algorithms.md#122-activity-selection).

**Grover's algorithm**
A quantum algorithm that finds a marked item among $N$ in about $\frac{\pi}{4}\sqrt N$ iterations, each an oracle call followed by a diffusion step. The quadratic speed-up is optimal, so it does not make NP-complete problems easy.
See [Chapter 25](25-Where-Algorithms-Go.md#255-quantum-algorithms-grover-and-shor).

## H

**Hall's marriage theorem**
A bipartite graph has a matching covering every left vertex if and only if every set $S$ of left vertices has at least $|S|$ neighbours in total.
See [Chapter 17](17-Spanning-Trees-Flows-and-Matching.md#176-bipartite-matching).

**Halting problem**
The problem of deciding, given a program and an input, whether the program eventually stops. Turing proved in 1936, by a diagonal argument, that it is undecidable: no program solves it for all inputs.
See [Chapter 1](01-What-Is-an-Algorithm.md#18-turing-machines-and-the-limits-of-computation).

**Hamiltonian cycle**
A cycle that visits every vertex of a graph exactly once. Deciding whether one exists is NP-complete, although the edge version, an Euler circuit, is easy.
See [Chapter 15](15-Graphs-and-Graph-Search.md#157-bipartite-graphs-cycles-and-euler-tours) and [Chapter 22](22-NP-Completeness.md#225-a-chain-of-reductions-proved).

**Harmonic number**
$H_n = 1 + \frac12 + \frac13 + \cdots + \frac1n$, which lies between $\ln n$ and $\ln n + 1$. It appears in the analysis of quicksort, records in random lists and greedy set cover.
See [Chapter 2](02-Measuring-Cost.md#26-analysing-loops-the-three-sums) and [Chapter 21](21-Randomized-and-Amortized-Analysis.md#211-las-vegas-monte-carlo-and-the-tools-of-expectation).

**Hash table**
An array of $m$ slots together with a hash function that tells each key which slot to use, and a rule for collisions such as chaining or open addressing. It gives expected $O(1)$ insert, lookup and delete when the load factor is bounded.
See [Chapter 7](07-Searching-and-Hashing.md#72-dictionaries-looking-things-up-by-key) and [Chapter 7](07-Searching-and-Hashing.md#73-hash-functions-and-chaining).

**Heapsort**
A sort that builds a max-heap in the array and repeatedly swaps the maximum to the end and sifts down the new root (Williams and Floyd, 1964). It sorts in place in $O(n \log n)$ worst case but is not stable; introsort uses it as a safety net.
See [Chapter 5](05-Sorting-by-Comparison.md#55-heapsort) and [Chapter 9](09-Heaps-and-Priority-Queues.md#93-heapsort-revisited-d-ary-heaps).

**Held-Karp algorithm**
The dynamic program for the travelling salesman problem whose states are (set of cities visited, current city). It runs in $O(2^n n^2)$ time, far better than trying all $(n-1)!$ tours.
See [Chapter 13](13-Dynamic-Programming.md#137-bitmask-dp-travelling-salesman-held-karp).

**Heuristic**
A method that usually finds good answers fast but has no worst-case guarantee on quality, such as local search. In A* search, a heuristic is a guess $h(v)$ of the distance from $v$ to the target.
See [Chapter 23](23-Approximation-and-Parameterized-Algorithms.md#238-heuristics-in-practice-local-search-sat-solvers-and-integer-programming-solvers) and [Chapter 16](16-Shortest-Paths.md#166-a-search-and-bidirectional-search).

**Hopcroft-Karp algorithm**
A bipartite matching algorithm that works in phases: BFS layers the graph by distance from the free left vertices, then DFS finds a maximal set of vertex-disjoint shortest augmenting paths and applies them all. It runs in $O(E\sqrt V)$.
See [Chapter 17](17-Spanning-Trees-Flows-and-Matching.md#176-bipartite-matching).

**Huffman coding**
The greedy algorithm (1952) that builds an optimal prefix code by repeatedly merging the two lightest trees under a new root. The resulting code is within one bit per symbol of the entropy.
See [Chapter 12](12-Greedy-Algorithms.md#124-huffman-coding).

**Hungarian algorithm**
An algorithm for the assignment problem (pairing $n$ workers with $n$ jobs at least total cost) that keeps feasible potentials on both sides and grows a matching of tight edges. The potentials are a certificate that the final assignment is optimal.
See [Chapter 17](17-Spanning-Trees-Flows-and-Matching.md#177-assignment-min-cost-flow-and-stable-matching).

**HyperLogLog**
A streaming algorithm that estimates the number of distinct items within a few percent in under a kilobyte (2007). It hashes each item to one of $m$ registers, keeps in each register the largest position of the first 1-bit seen, and combines the registers with a harmonic mean.
See [Chapter 24](24-Algorithms-for-Big-Data-and-Many-Processors.md#242-streaming-misra-gries-count-min-sketch-hyperloglog).

## I

**In place**
An algorithm is in place if it uses only $O(1)$ memory besides its input (some authors allow $O(\log n)$). Heapsort and insertion sort are in place; merge sort is not.
See [Chapter 2](02-Measuring-Cost.md#27-space-cost) and [Chapter 5](05-Sorting-by-Comparison.md#51-why-sorting-matters).

**Independent set**
A set of vertices of a graph no two of which are joined by an edge. Finding a largest one is NP-hard in general, but a short DP solves it on trees; $S$ is independent exactly when its complement is a vertex cover.
See [Chapter 13](13-Dynamic-Programming.md#136-dp-on-trees-and-dags) and [Chapter 22](22-NP-Completeness.md#223-reductions-np-hard-and-np-complete).

**Indicator variable**
A random variable $I_A$ that is 1 if event $A$ happens and 0 otherwise, so $E[I_A] = P(A)$. Writing a count as a sum of indicators and using linearity of expectation is the main tool for analysing randomized algorithms.
See [Chapter 5](05-Sorting-by-Comparison.md#54-quicksort) and [Chapter 21](21-Randomized-and-Amortized-Analysis.md#211-las-vegas-monte-carlo-and-the-tools-of-expectation).

**Insertion sort**
A sort that takes the items one at a time and shifts each one left into its place among the items already sorted. It does one shift per inversion, so it is $\Theta(n^2)$ in the worst case but linear on nearly sorted data, and fast sorts use it on small parts.
See [Chapter 5](05-Sorting-by-Comparison.md#52-simple-sorts-selection-insertion-bubble).

**Instance**
One particular input of a problem, such as one specific list to sort. An algorithm solves a problem only if it gives the right output on every instance.
See [Chapter 1](01-What-Is-an-Algorithm.md#11-recipes-for-machines) and [Chapter 22](22-NP-Completeness.md#221-easy-and-hard-problems).

**Introsort**
Quicksort that counts its recursion depth and switches to heapsort if the depth exceeds about $2\log_2 n$, with insertion sort on small parts (Musser, 1997). It keeps quicksort's speed with an $O(n \log n)$ worst-case guarantee.
See [Chapter 5](05-Sorting-by-Comparison.md#58-introsort-and-pattern-defeating-quicksort).

**Inverse Ackermann function**
The function $\alpha(m, n)$, which grows so slowly that it never exceeds 4 for any input that could exist. Union-find with union by rank and path compression costs $O(m\,\alpha(m, n))$ for $m$ operations, which is optimal.
See [Chapter 10](10-Union-Find-and-Range-Queries.md#102-union-by-rank-path-compression-and-the-inverse-ackermann-bound).

**Inversion**
A pair of positions $i < j$ whose items are in the wrong order, $a_i > a_j$. A sorted list has none and a reversed list $\binom n2$; merge sort can count them in $O(n \log n)$.
See [Chapter 5](05-Sorting-by-Comparison.md#52-simple-sorts-selection-insertion-bubble) and [Chapter 11](11-Divide-and-Conquer.md#112-counting-inversions).

**I/O model**
A model of computation for data on disk: memory holds $M$ records, the disk moves blocks of $B$ records, and the cost of an algorithm is the number of block transfers. Scanning costs $N/B$, searching a B-tree $\log_B N$, and sorting $\frac NB \log_{M/B} \frac NB$.
See [Chapter 24](24-Algorithms-for-Big-Data-and-Many-Processors.md#243-external-memory-the-io-model-external-merge-sort-b-trees-again) and [Chapter 8](08-Trees-and-Balanced-Search-Trees.md#85-b-trees-for-disks-and-databases).

## J

**Johnson's algorithm**
An all-pairs shortest-path algorithm for sparse graphs with negative edges (1977): run Bellman-Ford once to get a potential $h$, reweight every edge to $w(u, v) + h(u) - h(v) \ge 0$, then run Dijkstra from every vertex.
See [Chapter 16](16-Shortest-Paths.md#165-all-pairs-floyd-warshall-and-johnson).

## K

**Kadane's algorithm**
A linear-time scan for the maximum subarray: keep the best sum of a slice ending at the current position, extend it or start afresh, and remember the best seen. It beats the $O(n \log n)$ divide-and-conquer method.
See [Chapter 11](11-Divide-and-Conquer.md#113-maximum-subarray-divide-and-conquer-vs-kadane).

**Kahn's algorithm**
A topological sort that repeatedly removes a vertex of in-degree 0 and lowers the in-degrees of its successors. If it outputs fewer than $V$ vertices, the graph has a cycle.
See [Chapter 15](15-Graphs-and-Graph-Search.md#154-topological-sort).

**Karatsuba multiplication**
Multiplying two $n$-digit numbers with three half-size products instead of four, by reusing $(a+b)(c+d)$. Its recurrence $T(n) = 3T(n/2) + O(n)$ gives $\Theta(n^{\log_2 3}) \approx n^{1.585}$.
See [Chapter 11](11-Divide-and-Conquer.md#114-karatsuba-multiplication).

**Karger's algorithm**
A randomized minimum-cut algorithm (1993): contract random edges until two vertices remain and output the edges between them. It finds a given minimum cut with probability at least $1/\binom n2$, so about $\binom n2 \ln n$ repetitions almost always succeed.
See [Chapter 21](21-Randomized-and-Amortized-Analysis.md#214-kargers-minimum-cut-and-amplification).

**Karp reduction**
A polynomial-time reduction that maps each instance of $A$ to one instance of $B$ with the same answer; also called a many-one reduction. It is the kind used to prove NP-completeness.
See [Chapter 22](22-NP-Completeness.md#223-reductions-np-hard-and-np-complete).

**k-d tree**
A binary tree that splits $k$-dimensional points alternately by each coordinate (Bentley, 1975). It answers nearest-neighbour queries by pruning subtrees the search ball cannot reach, which is fast in low dimensions.
See [Chapter 20](20-Computational-Geometry.md#206-voronoi-diagrams-delaunay-triangulations-and-k-d-trees).

**Kernelization**
A polynomial-time preprocessing that shrinks an instance with parameter $k$ to an equivalent one whose size depends only on $k$, the kernel. A decidable parameterized problem is FPT exactly when it has a kernel.
See [Chapter 23](23-Approximation-and-Parameterized-Algorithms.md#237-fixed-parameter-tractability-vertex-cover-in-o2k-n).

**KMP algorithm**
The Knuth-Morris-Pratt string-matching algorithm. It uses the prefix function of the pattern to shift past mismatches without re-reading the text, finding all matches in at most $2n$ comparisons after $O(m)$ preprocessing.
See [Chapter 18](18-String-Algorithms.md#182-kmp-the-prefix-function).

**Knapsack problem (0/1)**
Given items with weights and values and a capacity $W$, choose items, each taken whole or not at all, of maximum total value within the capacity. It is NP-hard; dynamic programming solves it in pseudo-polynomial time $O(nW)$, and rounding gives an FPTAS.
See [Chapter 13](13-Dynamic-Programming.md#133-coin-change-01-knapsack-lis) and [Chapter 23](23-Approximation-and-Parameterized-Algorithms.md#234-a-knapsack-fptas).

**König's theorem**
In a bipartite graph, the size of a maximum matching equals the size of a minimum vertex cover (1931). It follows from the max-flow min-cut theorem.
See [Chapter 17](17-Spanning-Trees-Flows-and-Matching.md#176-bipartite-matching).

**Kosaraju's algorithm**
A strongly-connected-components algorithm with two DFS passes: one to compute finish times, then one on the reverse graph in decreasing finish order. Each tree of the second pass is one component.
See [Chapter 15](15-Graphs-and-Graph-Search.md#155-strongly-connected-components).

**Kruskal's algorithm**
A minimum-spanning-tree algorithm that sorts the edges by weight and adds each one that joins two different components, using union-find. It runs in $O(E \log V)$ and is correct by the cut property.
See [Chapter 17](17-Spanning-Trees-Flows-and-Matching.md#172-kruskal-prim-and-boruvka).

## L

**Lamé's theorem**
If Euclid's algorithm on $a > b \ge 1$ takes $k$ division steps, then $b \ge F_{k+1}$ and $a \ge F_{k+2}$, where $F$ are the Fibonacci numbers (1844). So consecutive Fibonacci numbers are the worst case, and the number of steps is $O(\log b)$.
See [Chapter 19](19-Number-Theoretic-Algorithms.md#191-gcd-and-extended-euclid).

**Las Vegas algorithm**
A randomized algorithm that always gives the right answer and whose running time is random, such as randomized quicksort. Checking a Monte Carlo answer turns it into Las Vegas.
See [Chapter 21](21-Randomized-and-Amortized-Analysis.md#211-las-vegas-monte-carlo-and-the-tools-of-expectation).

**LCP array**
For a suffix array, the list of the lengths of the longest common prefix of each suffix with the one just before it in sorted order. With it a suffix array answers distinct substrings and longest repeats.
See [Chapter 18](18-String-Algorithms.md#185-suffix-arrays-and-the-lcp-array).

**Learned index**
An index that replaces a B-tree by a model of the cumulative distribution of the keys, which predicts each key's position, together with the model's largest error, so that a lookup searches only a small window. Lookups are always correct; only their speed depends on the fit.
See [Chapter 25](25-Where-Algorithms-Go.md#256-learned-algorithms-and-data-structures).

**Leftist heap**
A mergeable heap: a heap-ordered binary tree in which every node's left child has null-path length at least its right child's, so the right spine has at most $\log_2(n+1)$ nodes (Crane, 1972). Two leftist heaps merge along their right spines in $O(\log n)$.
See [Chapter 9](09-Heaps-and-Priority-Queues.md#95-mergeable-heaps-leftist-and-binomial-heaps).

**Linear probing**
Open addressing in which a key that finds its slot taken tries the next slots in order. It suffers from primary clustering, about $\frac12(1 + \frac{1}{(1-\alpha)^2})$ probes per miss, but has excellent cache behaviour.
See [Chapter 7](07-Searching-and-Hashing.md#74-open-addressing).

**Linear program (LP)**
The problem of maximising or minimising a linear function of real variables subject to linear inequalities. Its feasible region is a convex polytope, and an optimum, when there is one, is attained at a corner; simplex and interior point methods solve it.
See [Chapter 23](23-Approximation-and-Parameterized-Algorithms.md#235-linear-programming-and-lp-relaxation-with-rounding).

**Linearity of expectation**
$E[aX + bY] = aE[X] + bE[Y]$ for any random variables, independent or not. With indicator variables it reduces most analyses of randomized algorithms to one probability per pair or per position.
See [Chapter 5](05-Sorting-by-Comparison.md#54-quicksort) and [Chapter 21](21-Randomized-and-Amortized-Analysis.md#211-las-vegas-monte-carlo-and-the-tools-of-expectation).

**Linked list**
A sequence stored as nodes anywhere in memory, each holding an item and a reference to the next node. It gives $O(1)$ insertion and deletion next to a node you hold, but $O(n)$ indexing and poor cache locality.
See [Chapter 4](04-Lists-Stacks-and-Queues.md#43-linked-lists).

**Little-o notation**
$f(n) = o(g(n))$ means that for every constant $c > 0$, $f(n) < c\,g(n)$ from some point on: $f$ is negligible compared with $g$. Little-omega, $\omega(g(n))$, means $f$ eventually exceeds every constant multiple of $g$.
See [Chapter 2](02-Measuring-Cost.md#28-little-o-little-omega-and-lower-bounds).

**Load factor**
The ratio $\alpha = n/m$ of stored keys to table slots in a hash table; with chaining it is the average chain length. Keeping it bounded, by doubling the table when it grows, keeps operations $O(1)$ expected.
See [Chapter 7](07-Searching-and-Hashing.md#73-hash-functions-and-chaining) and [Chapter 21](21-Randomized-and-Amortized-Analysis.md#216-amortized-analysis-in-depth).

**Local search**
A heuristic that starts with any solution and repeatedly replaces it by a better one in its neighbourhood (solutions reachable by a small change) until it reaches a local optimum. 2-opt for TSP and WalkSAT are examples; simulated annealing and tabu search help it escape local optima.
See [Chapter 23](23-Approximation-and-Parameterized-Algorithms.md#238-heuristics-in-practice-local-search-sat-solvers-and-integer-programming-solvers).

**Longest common subsequence (LCS)**
The longest sequence that is a subsequence of two given sequences. Dynamic programming over an $(m+1) \times (n+1)$ grid finds it in $O(mn)$, and Hirschberg's method in linear space.
See [Chapter 13](13-Dynamic-Programming.md#134-sequences-lcs-edit-distance-alignment).

**Longest increasing subsequence (LIS)**
The longest subsequence of a list that is strictly increasing. A simple DP takes $O(n^2)$; keeping the smallest possible last element of an increasing subsequence of each length (patience sorting) takes $O(n \log n)$.
See [Chapter 13](13-Dynamic-Programming.md#133-coin-change-01-knapsack-lis).

**Loop invariant**
A statement about a loop's variables that is true before the loop starts (initialization), stays true after each pass (maintenance), and, when the loop stops, gives the result wanted (termination). It proves a loop correct for every input.
See [Chapter 1](01-What-Is-an-Algorithm.md#14-loop-invariants).

**Lower bound**
A proof that no algorithm in a stated model can solve a problem with fewer steps than some amount, such as $\Omega(n \log n)$ comparisons for sorting. Lower bounds are proved by adversary arguments, decision trees or counting.
See [Chapter 1](01-What-Is-an-Algorithm.md#16-counting-steps-by-hand) and [Chapter 2](02-Measuring-Cost.md#28-little-o-little-omega-and-lower-bounds).

**Lowest common ancestor (LCA)**
The deepest node of a rooted tree that is an ancestor of both $u$ and $v$. The Euler tour reduces it to range minimum, and the two problems are equivalent.
See [Chapter 10](10-Union-Find-and-Range-Queries.md#106-sparse-tables-for-range-minimum-rmq-and-lca).

**LRU**
"Least recently used": the paging rule that evicts the page whose last request is oldest. It is $k$-competitive for a cache of $k$ pages, the best possible for a deterministic online algorithm.
See [Chapter 24](24-Algorithms-for-Big-Data-and-Many-Processors.md#241-online-algorithms-and-competitive-ratio-ski-rental-paging).

## M

**MapReduce**
A framework for computing on many machines: a map function runs on every input piece in parallel, the system shuffles the resulting key-value pairs so that equal keys meet, and a reduce function combines each group. It hides machines and failures from the programmer.
See [Chapter 24](24-Algorithms-for-Big-Data-and-Many-Processors.md#245-parallel-algorithms-work-and-span-brents-theorem-prefix-sums-mapreduce).

**Markov's inequality**
For a non-negative random variable $X$ and any $a > 0$, $P(X \ge a) \le E[X]/a$. It needs only the mean, and turns a Las Vegas algorithm into a Monte Carlo one by stopping it after a multiple of its expected time.
See [Chapter 21](21-Randomized-and-Amortized-Analysis.md#213-tail-bounds-markov-chebyshev-chernoff).

**Master theorem**
The rule that solves divide-and-conquer recurrences $T(n) = aT(n/b) + \Theta(n^d)$ by comparing $d$ with the critical exponent $\log_b a$: $\Theta(n^{\log_b a})$ if $d < \log_b a$, $\Theta(n^d \log n)$ if they are equal, $\Theta(n^d)$ if $d > \log_b a$.
See [Chapter 3](03-Recursion-and-Induction.md#36-the-master-theorem).

**Matching**
A set of edges of a graph no two of which share a vertex. It is maximum if no matching has more edges, maximal if no edge can be added, and perfect if it covers every vertex. Bipartite matching is a unit-capacity flow problem.
See [Chapter 17](17-Spanning-Trees-Flows-and-Matching.md#176-bipartite-matching) and [Chapter 23](23-Approximation-and-Parameterized-Algorithms.md#231-approximation-ratio-vertex-cover-2-approximation).

**Mathematical induction**
A proof that a statement $P(n)$ holds for every $n \ge n_0$: prove $P(n_0)$ (the base case), then prove that $P(k)$ implies $P(k+1)$ (the inductive step), where the assumption $P(k)$ is the induction hypothesis. Strong induction lets the step use every smaller case, which matches recursion on $n/2$.
See [Chapter 3](03-Recursion-and-Induction.md#32-mathematical-induction) and [Chapter 3](03-Recursion-and-Induction.md#33-proving-recursive-algorithms-correct).

**Matrix exponentiation**
Computing the $n$-th term of a linear recurrence of order $k$ by raising its $k \times k$ companion matrix to the $n$-th power with square-and-multiply, in $O(k^3 \log n)$ operations.
See [Chapter 19](19-Number-Theoretic-Algorithms.md#197-matrix-exponentiation-and-the-number-theoretic-transform).

**Matrix multiplication exponent**
The smallest $\omega$ such that $n \times n$ matrices can be multiplied in $O(n^{\omega + \varepsilon})$ operations for every $\varepsilon > 0$. Strassen showed $\omega < 2.81$; it is now known to lie between 2 and 2.371339.
See [Chapter 25](25-Where-Algorithms-Go.md#253-the-matrix-multiplication-exponent) and [Chapter 11](11-Divide-and-Conquer.md#115-strassens-matrix-multiplication).

**Matrix-chain multiplication**
Choosing the order in which to multiply a chain of matrices so as to use the fewest scalar multiplications. An interval DP over the best split of each subchain solves it in $O(n^3)$.
See [Chapter 13](13-Dynamic-Programming.md#135-intervals-matrix-chain-multiplication-optimal-bst).

**Matroid**
A pair $(E, \mathcal I)$ where the independent sets $\mathcal I$ include $\emptyset$, are closed under taking subsets, and have the exchange property. The greedy algorithm finds a maximum-weight independent set for every choice of weights exactly when the structure is a matroid (Rado, Edmonds); the forests of a graph form one.
See [Chapter 12](12-Greedy-Algorithms.md#126-matroids-and-the-greedy-theorem).

**Max-flow min-cut theorem**
In every flow network the maximum value of a flow equals the minimum capacity of an s-t cut. The vertices reachable from the source in the final residual graph form a minimum cut, a certificate that the flow is maximum.
See [Chapter 17](17-Spanning-Trees-Flows-and-Matching.md#174-the-max-flow-min-cut-theorem).

**Maximum subarray problem**
Given numbers, some negative, find the contiguous slice with the largest sum. Divide and conquer solves it in $O(n \log n)$, and Kadane's scan in $O(n)$.
See [Chapter 11](11-Divide-and-Conquer.md#113-maximum-subarray-divide-and-conquer-vs-kadane).

**Median of medians**
A deterministic pivot rule for selection: split the items into groups of 5, take each group's median, and recursively find the median of those. The pivot has at least $3n/10 - 6$ items on each side, which makes selection $O(n)$ in the worst case.
See [Chapter 6](06-Sorting-in-Linear-Time-and-Selection.md#65-median-of-medians-worst-case-linear-selection).

**Meet in the middle**
Splitting an exhaustive search into two halves, enumerating each half separately, and matching the halves by sorting or hashing. It solves subset sum in $O(2^{n/2} n)$ time instead of $O(2^n)$.
See [Chapter 14](14-Backtracking-and-Branch-and-Bound.md#145-meet-in-the-middle).

**Memoization**
Keeping a recursive algorithm but storing every answer the first time it is computed, in a table called a memo, and looking it up on later calls. It is the top-down form of dynamic programming.
See [Chapter 13](13-Dynamic-Programming.md#131-overlapping-subproblems-fibonacci-three-ways).

**Menger's theorem**
The largest number of edge-disjoint paths between two vertices equals the smallest number of edges whose removal separates them (1927). It is a special case of the max-flow min-cut theorem.
See [Chapter 17](17-Spanning-Trees-Flows-and-Matching.md#174-the-max-flow-min-cut-theorem).

**Merge sort**
A sort that splits the list into halves, sorts each recursively and merges the two sorted halves. It is stable and takes $\Theta(n \log n)$ on every input, at the price of $\Theta(n)$ extra memory.
See [Chapter 5](05-Sorting-by-Comparison.md#53-merge-sort).

**Miller-Rabin test**
A primality test that writes $n - 1 = 2^s d$ and checks whether $a^d \equiv 1$ or some $a^{2^r d} \equiv -1 \pmod n$. A composite has at most a quarter of the bases as strong liars, so it errs with probability at most $1/4$ per round, and with twelve fixed bases it is exact below $2^{64}$.
See [Chapter 19](19-Number-Theoretic-Algorithms.md#194-primality-fermat-miller-rabin-and-aks).

**Min-cost flow**
The problem of sending a given amount of flow through a network whose edges have capacities and costs per unit, at least total cost. A flow is optimal exactly when its residual graph has no negative-cost cycle; successive shortest paths finds one.
See [Chapter 17](17-Spanning-Trees-Flows-and-Matching.md#177-assignment-min-cost-flow-and-stable-matching).

**Minimum spanning tree (MST)**
A spanning tree of a connected weighted graph with the least total edge weight. Kruskal's, Prim's and Borůvka's greedy algorithms find one in $O(E \log V)$, correct by the cut property.
See [Chapter 17](17-Spanning-Trees-Flows-and-Matching.md#171-minimum-spanning-trees-the-cut-and-cycle-properties) and [Chapter 12](12-Greedy-Algorithms.md#127-minimum-spanning-trees-preview-set-cover-greedy-as-approximation).

**Misra-Gries algorithm**
A streaming algorithm for heavy hitters (1982): keep at most $k - 1$ counters; increment an item's counter, start one if there is room, or else decrement every counter. Each counter undercounts by at most $n/k$, so every item occurring more than $n/k$ times survives.
See [Chapter 24](24-Algorithms-for-Big-Data-and-Many-Processors.md#242-streaming-misra-gries-count-min-sketch-hyperloglog).

**Monte Carlo algorithm**
A randomized algorithm that always runs within a fixed time bound but may give a wrong answer with some small probability, such as the Miller-Rabin test. Repetition makes the error as small as wanted.
See [Chapter 21](21-Randomized-and-Amortized-Analysis.md#211-las-vegas-monte-carlo-and-the-tools-of-expectation).

## N

**Negative cycle**
A cycle whose edge weights sum to less than zero. If one is reachable from the source, going round it again and again makes paths arbitrarily short, so shortest-path distances are undefined; Bellman-Ford detects it.
See [Chapter 16](16-Shortest-Paths.md#161-the-problem-relaxation-and-negative-cycles) and [Chapter 16](16-Shortest-Paths.md#163-bellman-ford).

**NP**
The class of decision problems whose yes-instances have certificates of polynomial length that a polynomial-time verifier can check. The name means nondeterministic polynomial time, not "not polynomial"; $\mathrm{P} \subseteq \mathrm{NP}$.
See [Chapter 22](22-NP-Completeness.md#222-p-and-np-via-certificates).

**NP-complete**
A problem that is in NP and NP-hard: the hardest problems in NP. If any NP-complete problem is in P then P = NP; SAT, 3-SAT, clique, vertex cover, subset sum, Hamiltonian cycle and TSP are examples.
See [Chapter 22](22-NP-Completeness.md#223-reductions-np-hard-and-np-complete) and [Chapter 22](22-NP-Completeness.md#225-a-chain-of-reductions-proved).

**NP-hard**
A problem $B$ such that every problem in NP reduces to it in polynomial time. An NP-hard problem need not be in NP; the halting problem is NP-hard.
See [Chapter 22](22-NP-Completeness.md#223-reductions-np-hard-and-np-complete).

**NP-intermediate problem**
A problem in NP that is neither in P nor NP-complete. Ladner proved that such problems exist if P ≠ NP; graph isomorphism and factoring are candidates.
See [Chapter 22](22-NP-Completeness.md#226-karps-21-problems-co-np-and-pspace).

**Number-theoretic transform (NTT)**
The fast Fourier transform done in arithmetic mod a prime such as $119 \cdot 2^{23} + 1$, using a primitive root of unity mod $p$ in place of complex roots. It multiplies polynomials exactly, with no rounding error, in $O(n \log n)$.
See [Chapter 19](19-Number-Theoretic-Algorithms.md#197-matrix-exponentiation-and-the-number-theoretic-transform) and [Chapter 11](11-Divide-and-Conquer.md#117-the-fast-fourier-transform).

## O

**Online algorithm**
An algorithm that receives its input piece by piece and must make each decision before seeing the rest, without undoing it. It is judged by its competitive ratio against an offline algorithm that sees the whole input first.
See [Chapter 24](24-Algorithms-for-Big-Data-and-Many-Processors.md#241-online-algorithms-and-competitive-ratio-ski-rental-paging).

**Open addressing**
Storing every key in the hash table array itself: a key whose slot is taken tries a sequence of other slots, its probe sequence, and takes the first free one. Deletion needs tombstones, and under uniform hashing a miss costs at most $\frac{1}{1-\alpha}$ probes.
See [Chapter 7](07-Searching-and-Hashing.md#74-open-addressing).

**Optimal substructure**
The property that an optimal solution is built from optimal solutions of subproblems. Dynamic programming, greedy algorithms and divide and conquer all rely on it; Bellman called it the principle of optimality.
See [Chapter 13](13-Dynamic-Programming.md#131-overlapping-subproblems-fibonacci-three-ways).

**Orientation test**
The sign of the cross product $(a - o) \times (b - o)$, which says whether the path $o \to a \to b$ turns left (positive), right (negative) or goes straight (zero, the points are collinear). Computed exactly in integers it is reliable; in floating point it fails on near-collinear points.
See [Chapter 20](20-Computational-Geometry.md#201-points-vectors-and-the-orientation-test).

**Orthogonal Vectors (OV)**
The problem: given two lists of $N$ vectors in $\{0,1\}^d$, is there a pair, one from each list, with dot product 0? Under SETH it needs about $N^2$ time, which is how SETH implies quadratic lower bounds for edit distance and LCS.
See [Chapter 25](25-Where-Algorithms-Go.md#252-fine-grained-complexity-3sum-seth-edit-distance).

**Overlapping subproblems**
The property that a recursive algorithm solves the same subproblems again and again, as the naive Fibonacci recursion does. Storing each answer once turns exponential recursion into polynomial work.
See [Chapter 13](13-Dynamic-Programming.md#131-overlapping-subproblems-fibonacci-three-ways).

## P

**P**
The class of decision problems that can be solved by an algorithm running in polynomial time in the length of the input's encoding, with numbers written in binary. It is the usual formal meaning of "efficiently solvable".
See [Chapter 22](22-NP-Completeness.md#221-easy-and-hard-problems).

**P versus NP**
The open question whether every problem whose yes-answers can be checked quickly can also be solved quickly. Most researchers believe $\mathrm{P} \ne \mathrm{NP}$, but relativization, natural proofs and algebrization rule out the familiar proof methods.
See [Chapter 25](25-Where-Algorithms-Go.md#251-p-versus-np-what-is-known-and-why-it-is-hard) and [Chapter 22](22-NP-Completeness.md#222-p-and-np-via-certificates).

**Paging**
The online problem of managing a cache of $k$ pages: each request is a hit if the page is in the cache and otherwise a miss (page fault), after which some page may have to be evicted. LRU and FIFO are $k$-competitive, and Belady's MIN is the offline optimum.
See [Chapter 24](24-Algorithms-for-Big-Data-and-Many-Processors.md#241-online-algorithms-and-competitive-ratio-ski-rental-paging).

**Pairing heap**
A simple self-adjusting heap (1986): a single heap-ordered tree in which extract-min melds the root's children in two passes. It is usually faster than a Fibonacci heap in practice, though its exact amortized decrease-key cost is still not fully settled.
See [Chapter 9](09-Heaps-and-Priority-Queues.md#96-fibonacci-heaps-and-pairing-heaps).

**Parenthesis theorem**
In a depth-first search, for any two vertices $u$ and $v$ the intervals $[d[u], f[u]]$ and $[d[v], f[v]]$ of discovery and finish times are either disjoint or one contains the other, and the containing vertex is an ancestor.
See [Chapter 15](15-Graphs-and-Graph-Search.md#153-depth-first-search).

**Partition**
The step of quicksort that rearranges a list around a pivot so that smaller items come first, then the pivot, then the rest. Lomuto's and Hoare's are the two classic schemes; three-way partitioning also groups items equal to the pivot.
See [Chapter 5](05-Sorting-by-Comparison.md#54-quicksort) and [Chapter 5](05-Sorting-by-Comparison.md#58-introsort-and-pattern-defeating-quicksort).

**Path compression**
The union-find improvement in which, after a find walks from $x$ to the root, every node on the path is pointed directly at the root. Together with union by rank it makes $m$ operations cost $O(m\,\alpha(m, n))$.
See [Chapter 10](10-Union-Find-and-Range-Queries.md#102-union-by-rank-path-compression-and-the-inverse-ackermann-bound).

**Pattern-defeating quicksort (pdqsort)**
Orson Peters's quicksort variant that adds to introsort detection of patterns: it recognises sorted and nearly sorted parts, breaks up bad pivot patterns by shuffling, and handles many equal keys. Rust's and Go's unstable sorts use it.
See [Chapter 5](05-Sorting-by-Comparison.md#58-introsort-and-pattern-defeating-quicksort).

**Paxos**
Leslie Lamport's consensus protocol (written 1989, published 1998), behind many replicated databases. Like Raft, it never violates agreement and makes progress whenever the network behaves well enough.
See [Chapter 24](24-Algorithms-for-Big-Data-and-Many-Processors.md#246-distributed-algorithms-briefly-consensus-and-why-it-is-hard).

**PCP theorem**
$\mathrm{NP} = \mathrm{PCP}(O(\log n), O(1))$: every NP statement has a proof format that can be checked with high confidence by reading only a constant number of randomly chosen bits. It creates gaps, and so proves that many problems are hard to approximate.
See [Chapter 23](23-Approximation-and-Parameterized-Algorithms.md#236-inapproximability-and-the-pcp-theorem).

**Perfect hashing**
A hash function with no collisions on a given static set. Fredman, Komlós and Szemerédi's two-level scheme uses $O(n)$ space and gives worst-case $O(1)$ lookups.
See [Chapter 7](07-Searching-and-Hashing.md#76-perfect-hashing-cuckoo-hashing-and-robin-hood-hashing).

**Pick's theorem**
For a simple polygon whose vertices have integer coordinates, with $I$ lattice points inside and $B$ on the boundary, the area is $I + B/2 - 1$ (Pick, 1899).
See [Chapter 20](20-Computational-Geometry.md#205-polygon-area-and-point-in-polygon).

**Pollard's rho**
A factoring algorithm that iterates $x \mapsto x^2 + c \bmod n$ and uses Floyd's cycle finding and gcds to detect a repeat mod an unknown prime factor $p$. By the birthday paradox it finds $p$ in about $\sqrt p$ steps.
See [Chapter 19](19-Number-Theoretic-Algorithms.md#195-factoring-trial-division-and-pollards-rho).

**Polynomial time**
An algorithm runs in polynomial time if on instances of size $s$ it takes at most $c\,s^d$ steps for some constants $c$ and $d$. Polynomial versus exponential is the line between practical and hopeless.
See [Chapter 22](22-NP-Completeness.md#221-easy-and-hard-problems) and [Chapter 2](02-Measuring-Cost.md#24-the-growth-ladder).

**Polynomial-time approximation scheme (PTAS)**
An algorithm that, for every fixed $\varepsilon > 0$, gives a $(1 + \varepsilon)$-approximation in time polynomial in $n$, though possibly like $n^{1/\varepsilon}$. Euclidean TSP has one; an FPTAS is also polynomial in $1/\varepsilon$.
See [Chapter 23](23-Approximation-and-Parameterized-Algorithms.md#234-a-knapsack-fptas) and [Chapter 23](23-Approximation-and-Parameterized-Algorithms.md#232-metric-tsp-mst-doubling-and-christofides).

**Polynomial-time reduction**
A polynomial-time algorithm that translates every instance of problem $A$ into an instance of problem $B$ with the same answer, written $A \le_p B$. To prove a new problem hard, reduce a known hard problem to it.
See [Chapter 22](22-NP-Completeness.md#223-reductions-np-hard-and-np-complete).

**Potential method**
A way to prove amortized bounds that stores credit in the whole data structure: choose a potential $\Phi \ge 0$ that starts at 0, and charge each operation its actual cost plus the change in $\Phi$. The potentials telescope, so the total charge bounds the total cost.
See [Chapter 4](04-Lists-Stacks-and-Queues.md#47-the-potential-method-and-a-queue-from-two-stacks) and [Chapter 21](21-Randomized-and-Amortized-Analysis.md#216-amortized-analysis-in-depth).

**Prefix code**
A code in which no codeword is a prefix of another, so that a stream of bits can be decoded without separators. Every binary prefix code is a binary tree, and Huffman coding finds an optimal one.
See [Chapter 12](12-Greedy-Algorithms.md#124-huffman-coding).

**Prefix function**
For each prefix of a pattern, the length of its longest border: the longest proper prefix that is also a suffix. KMP uses it to know how far the pattern can shift after a mismatch.
See [Chapter 18](18-String-Algorithms.md#182-kmp-the-prefix-function).

**Prefix sums**
The array $P$ with $P[i] = a_0 + \cdots + a_{i-1}$, after which any range sum is $P[r] - P[l]$ in $O(1)$. In parallel, prefix sums take $O(n)$ work and $O(\log n)$ span.
See [Chapter 10](10-Union-Find-and-Range-Queries.md#103-prefix-sums-and-difference-arrays) and [Chapter 24](24-Algorithms-for-Big-Data-and-Many-Processors.md#245-parallel-algorithms-work-and-span-brents-theorem-prefix-sums-mapreduce).

**Prime number theorem**
The number of primes up to $n$ is about $n / \ln n$. So primes are common: a random number near $n$ is prime with probability about $1/\ln n$.
See [Chapter 19](19-Number-Theoretic-Algorithms.md#193-sieves-eratosthenes-and-the-linear-sieve).

**Prim's algorithm**
A minimum-spanning-tree algorithm that grows one tree from a start vertex, always adding the lightest edge leaving it, with a priority queue. It is Dijkstra's algorithm with a different key and runs in $O(E \log V)$ with a binary heap.
See [Chapter 17](17-Spanning-Trees-Flows-and-Matching.md#172-kruskal-prim-and-boruvka).

**Priority queue**
An abstract data type that holds items with keys and supports insert, find-min and extract-min, often also decrease-key, delete and meld. Binary heaps, $d$-ary heaps, binomial heaps and Fibonacci heaps implement it.
See [Chapter 9](09-Heaps-and-Priority-Queues.md#91-the-priority-queue-problem).

**Problem**
A description of which output is wanted for each possible input, such as "given two whole numbers, find their greatest common divisor". Each concrete input is an instance.
See [Chapter 1](01-What-Is-an-Algorithm.md#11-recipes-for-machines).

**Pseudo-polynomial time**
Running time polynomial in the numeric values of the input but not in the number of digits needed to write them, such as $O(nW)$ for knapsack. It is exponential in the input size, consistent with knapsack being NP-hard.
See [Chapter 13](13-Dynamic-Programming.md#133-coin-change-01-knapsack-lis) and [Chapter 22](22-NP-Completeness.md#221-easy-and-hard-problems).

**PSPACE**
The class of problems solvable with a polynomial amount of memory and no limit on time. It contains NP and co-NP, and TQBF (true quantified Boolean formulas) is its typical complete problem.
See [Chapter 22](22-NP-Completeness.md#226-karps-21-problems-co-np-and-pspace).

## Q

**Quantum Fourier transform**
The discrete Fourier transform carried out on the amplitudes of a quantum state, using only polynomially many gates in the number of qubits. Shor's algorithm uses it to find periods.
See [Chapter 25](25-Where-Algorithms-Go.md#255-quantum-algorithms-grover-and-shor).

**Queue**
A container in which items join at the back and leave from the front, first in, first out. A circular buffer gives $O(1)$ operations, and two stacks give $O(1)$ amortized; breadth-first search runs on a queue.
See [Chapter 4](04-Lists-Stacks-and-Queues.md#45-queues-and-deques) and [Chapter 4](04-Lists-Stacks-and-Queues.md#47-the-potential-method-and-a-queue-from-two-stacks).

**Quickselect**
The selection algorithm that partitions around a random pivot and recurses only into the side that holds the wanted rank (Hoare's FIND, 1961). It makes fewer than $4n$ expected comparisons, about $3.39n$ for the median.
See [Chapter 6](06-Sorting-in-Linear-Time-and-Selection.md#64-selection-the-k-th-smallest) and [Chapter 21](21-Randomized-and-Amortized-Analysis.md#212-randomized-quicksort-and-quickselect-analysed-fully).

**Quicksort**
A sort that picks a pivot, partitions the list around it and sorts the two sides recursively (Hoare, 1961). It is in place with a tiny inner loop; with random pivots it makes $2(n+1)H_n - 4n \approx 1.39\,n\log_2 n$ expected comparisons on every input, though its worst case is quadratic.
See [Chapter 5](05-Sorting-by-Comparison.md#54-quicksort) and [Chapter 21](21-Randomized-and-Amortized-Analysis.md#212-randomized-quicksort-and-quickselect-analysed-fully).

## R

**Rabin-Karp algorithm**
String matching by hashing: compare the rolling hash of each text window with the pattern's hash, and check the characters only when the hashes agree. With a random base, collisions are rare, so it is fast in expectation and extends easily to many patterns.
See [Chapter 18](18-String-Algorithms.md#183-the-z-algorithm-rabin-karp-and-rolling-hashes).

**Radix sort**
A sort that sorts integer or string keys digit by digit with a stable sort such as counting sort. LSD radix sort goes from the least significant digit and is correct because each pass is stable; it is linear for keys below $n^c$.
See [Chapter 6](06-Sorting-in-Linear-Time-and-Selection.md#62-radix-sort-lsd-and-msd).

**RAM model**
The random-access machine: a model of computation with memory cells holding words of bounded size and unit-cost instructions (arithmetic, comparison, load, store, jump). Random access means reading `a[i]` costs the same for every $i$.
See [Chapter 1](01-What-Is-an-Algorithm.md#15-how-computers-run-code-the-ram-model).

**Randomized algorithm**
An algorithm that may ask for random numbers as it runs, so that its running time or its answer depends on its own coin flips rather than on the input distribution. Las Vegas algorithms are always right; Monte Carlo algorithms are always fast.
See [Chapter 2](02-Measuring-Cost.md#22-worst-best-and-average-case) and [Chapter 21](21-Randomized-and-Amortized-Analysis.md#211-las-vegas-monte-carlo-and-the-tools-of-expectation).

**Range minimum query (RMQ)**
The problem of answering "what is the minimum of $a_l, \ldots, a_{r-1}$?" for many ranges of a fixed array. A sparse table answers each in $O(1)$ after $O(n \log n)$ preprocessing, and RMQ is equivalent to lowest common ancestor.
See [Chapter 10](10-Union-Find-and-Range-Queries.md#106-sparse-tables-for-range-minimum-rmq-and-lca).

**Recurrence**
An equation that gives a function's value at $n$ in terms of its values at smaller arguments, such as $T(n) = 2T(n/2) + n$ for merge sort. Unrolling, recursion trees, substitution and the master theorem solve recurrences.
See [Chapter 3](03-Recursion-and-Induction.md#34-recurrences-writing-tn) and [Chapter 3](03-Recursion-and-Induction.md#35-solving-recurrences).

**Recursion**
A function that calls itself on smaller inputs, with a base case that answers directly and a recursive case built from the answers to smaller inputs. It runs on the call stack, so its depth is its extra space.
See [Chapter 3](03-Recursion-and-Induction.md#31-a-function-that-calls-itself).

**Red-black tree**
A binary search tree whose nodes are coloured red or black so that the root is black, no red node has a red child, and every path from a node down to a NIL leaf has the same number of black nodes. Its height is at most $2\log_2(n+1)$, and an insertion needs at most two rotations.
See [Chapter 8](08-Trees-and-Balanced-Search-Trees.md#84-red-black-trees).

**Reduction**
A way of solving one problem using a solver for another. Reductions prove undecidability (a solver for the new problem would solve the halting problem) and NP-hardness (polynomial-time reductions from a known hard problem).
See [Chapter 1](01-What-Is-an-Algorithm.md#18-turing-machines-and-the-limits-of-computation) and [Chapter 22](22-NP-Completeness.md#223-reductions-np-hard-and-np-complete).

**Relaxation (of an edge)**
The basic step of shortest-path algorithms: if $d[u] + w(u, v) < d[v]$, lower $d[v]$ to $d[u] + w(u, v)$ and make $u$ the parent of $v$. Every algorithm in the shortest-path chapter only relaxes edges, in different orders.
See [Chapter 16](16-Shortest-Paths.md#161-the-problem-relaxation-and-negative-cycles).

**Reservoir sampling**
Keeping a uniform random sample of $k$ items from a stream of unknown length in $O(k)$ memory (Algorithm R): keep the first $k$, then replace a random member with item $t$ with probability $k/t$. After $t$ items each is in the sample with probability exactly $k/t$.
See [Chapter 21](21-Randomized-and-Amortized-Analysis.md#215-reservoir-sampling-and-the-fisher-yates-shuffle).

**Residual graph**
For a flow $f$, the graph with an edge wherever more flow can be sent: forward edges with the unused capacity $c(u, v) - f(u, v)$ and reverse edges that let existing flow be cancelled. Augmenting paths are paths from source to sink in it.
See [Chapter 17](17-Spanning-Trees-Flows-and-Matching.md#173-network-flow-ford-fulkerson-and-residual-graphs).

**Rolling hash**
A hash of a window of text, such as its value as a number in base $b$ mod a prime $p$, that can be updated in $O(1)$ when the window slides by one character. It is the core of Rabin-Karp matching.
See [Chapter 18](18-String-Algorithms.md#183-the-z-algorithm-rabin-karp-and-rolling-hashes).

## S

**Satisfiability (SAT)**
The problem: given a Boolean formula, usually in conjunctive normal form, is there an assignment of true and false to its variables that makes it true? It was the first problem proved NP-complete, by the Cook-Levin theorem.
See [Chapter 22](22-NP-Completeness.md#224-the-cook-levin-theorem) and [Chapter 22](22-NP-Completeness.md#222-p-and-np-via-certificates).

**Segment tree**
A binary tree over an array in which each node stores the combined value of its range, for any associative operation. Queries and point updates take $O(\log n)$, visiting at most four nodes per level, and lazy propagation adds range updates.
See [Chapter 10](10-Union-Find-and-Range-Queries.md#105-segment-trees-and-lazy-propagation).

**Selection problem**
Given $n$ items and a rank $k$, find the item that would be at position $k$ if they were sorted. It is easier than sorting: quickselect takes expected $O(n)$ and median of medians $O(n)$ in the worst case.
See [Chapter 6](06-Sorting-in-Linear-Time-and-Selection.md#64-selection-the-k-th-smallest).

**Selection sort**
A simple sort that repeatedly finds the minimum of the unsorted part and swaps it into place. It always makes $\Theta(n^2)$ comparisons but only $n - 1$ swaps.
See [Chapter 5](05-Sorting-by-Comparison.md#52-simple-sorts-selection-insertion-bubble).

**Separate chaining**
A hash table in which each slot holds a list, its chain, of all the stored pairs whose key hashes there. Under simple uniform hashing each operation takes $\Theta(1 + \alpha)$ expected time for load factor $\alpha$.
See [Chapter 7](07-Searching-and-Hashing.md#73-hash-functions-and-chaining).

**Set cover**
Given a universe of $n$ elements and a family of subsets whose union is the universe, choose as few subsets as possible that still cover everything. It is NP-hard; the greedy algorithm, always taking the set that covers most uncovered elements, is within a factor $H_n \approx \ln n$ of optimal, and that is essentially best possible.
See [Chapter 12](12-Greedy-Algorithms.md#127-minimum-spanning-trees-preview-set-cover-greedy-as-approximation) and [Chapter 23](23-Approximation-and-Parameterized-Algorithms.md#233-set-cover-the-greedy-h_n-bound).

**Shor's algorithm**
A quantum algorithm (1994) that factors an $n$-bit number in polynomial time by finding the period of $a^x \bmod N$ with the quantum Fourier transform. It would break RSA, which is why cryptographers are moving to post-quantum schemes.
See [Chapter 25](25-Where-Algorithms-Go.md#255-quantum-algorithms-grover-and-shor).

**Shortest path**
A path between two vertices of least total weight. Shortest paths have shortest pieces, and the distances satisfy the triangle inequality; with no negative cycle they can always be taken simple, and all of them from one source fit in a shortest-path tree.
See [Chapter 16](16-Shortest-Paths.md#161-the-problem-relaxation-and-negative-cycles).

**Shunting-yard algorithm**
Dijkstra's 1961 algorithm that converts infix expressions to postfix with a stack, on which operators wait until an operator of lower precedence or a closing bracket releases them.
See [Chapter 4](04-Lists-Stacks-and-Queues.md#44-stacks).

**Sieve of Eratosthenes**
The algorithm that lists all primes up to $n$ by crossing off the multiples of each prime in turn; the numbers never crossed off are the primes. It runs in $O(n \log\log n)$ time.
See [Chapter 19](19-Number-Theoretic-Algorithms.md#193-sieves-eratosthenes-and-the-linear-sieve).

**Simplex method**
Dantzig's 1947 method for linear programming: start at a corner of the feasible polytope and repeatedly move along an edge to an adjacent corner with a better value, until none is better. It is fast in practice though exponential in the worst case.
See [Chapter 23](23-Approximation-and-Parameterized-Algorithms.md#235-linear-programming-and-lp-relaxation-with-rounding).

**Skip list**
A sorted linked list with extra levels of express lanes, in which each node is promoted to the next level with probability $\frac12$ (Pugh, 1990). Search, insert and delete take expected $O(\log n)$ with no rebalancing, and it is easy to make concurrent.
See [Chapter 8](08-Trees-and-Balanced-Search-Trees.md#86-treaps-and-skip-lists-randomness-instead-of-rules).

**Sparse table**
A table holding the minimum of every block of length $2^k$ of an array, built in $O(n \log n)$. A range minimum is then the minimum of two overlapping blocks, found in $O(1)$; it works for any idempotent operation.
See [Chapter 10](10-Union-Find-and-Range-Queries.md#106-sparse-tables-for-range-minimum-rmq-and-lca).

**Specification**
A precise statement of what an algorithm must do, made of a precondition (what may be assumed about the input) and a postcondition (what must be true of the output). An algorithm is correct if, on every input meeting the precondition, it stops with an output meeting the postcondition.
See [Chapter 1](01-What-Is-an-Algorithm.md#13-correctness-what-correct-means).

**Splay tree**
A self-adjusting binary search tree that stores no balance information and moves every accessed node to the root by zig, zig-zig and zig-zag rotations (Sleator and Tarjan, 1985). Every operation costs $O(\log n)$ amortized, by the access lemma.
See [Chapter 8](08-Trees-and-Balanced-Search-Trees.md#87-splay-trees-self-adjusting) and [Chapter 21](21-Randomized-and-Amortized-Analysis.md#216-amortized-analysis-in-depth).

**Stable matching**
A perfect matching between two sides with preferences that has no blocking pair. One always exists, and the Gale-Shapley algorithm finds the one best for the proposing side.
See [Chapter 17](17-Spanning-Trees-Flows-and-Matching.md#177-assignment-min-cost-flow-and-stable-matching).

**Stable sort**
A sort that keeps records with equal keys in the order they had in the input. Merge sort, insertion sort and counting sort are stable; quicksort and heapsort are not. Stability is what makes LSD radix sort correct.
See [Chapter 5](05-Sorting-by-Comparison.md#51-why-sorting-matters).

**Stack**
A container in which items are added and removed at one end only, the top, so the last item pushed is the first popped (LIFO). Stacks check brackets, evaluate expressions and run every function call.
See [Chapter 4](04-Lists-Stacks-and-Queues.md#44-stacks).

**State-space tree**
The tree of partial solutions of a search problem: the root makes no choices, each child makes one more choice, and the leaves are complete candidates. Exhaustive search walks all of it, and backtracking prunes it.
See [Chapter 14](14-Backtracking-and-Branch-and-Bound.md#141-exhaustive-search-the-state-space-tree).

**Strassen's algorithm**
Multiplying two $n \times n$ matrices by splitting each into four blocks and using seven block products instead of eight (1969). Its recurrence $T(n) = 7T(n/2) + O(n^2)$ gives $\Theta(n^{\log_2 7}) \approx n^{2.807}$.
See [Chapter 11](11-Divide-and-Conquer.md#115-strassens-matrix-multiplication).

**Streaming model**
A model in which the input is a long sequence of items read once, in order, by an algorithm with memory far smaller than the input. Most streaming problems need both randomness and approximation.
See [Chapter 24](24-Algorithms-for-Big-Data-and-Many-Processors.md#242-streaming-misra-gries-count-min-sketch-hyperloglog).

**Strong exponential time hypothesis (SETH)**
The conjecture (Impagliazzo and Paturi, 2001) that for every $\varepsilon > 0$ there is a $k$ such that $k$-SAT on $n$ variables cannot be solved in time $O(2^{(1-\varepsilon)n})$. It implies, through orthogonal vectors, that edit distance and LCS need quadratic time.
See [Chapter 25](25-Where-Algorithms-Go.md#252-fine-grained-complexity-3sum-seth-edit-distance).

**Strongly connected components**
The maximal sets of vertices of a directed graph in which every vertex can reach every other. Kosaraju's two DFS passes or Tarjan's single pass with low-links find them in $O(V + E)$, and shrinking them gives a DAG.
See [Chapter 15](15-Graphs-and-Graph-Search.md#155-strongly-connected-components).

**Strongly NP-hard**
A problem that stays NP-hard even when every number in the input is bounded by a polynomial in the input size, such as 3-partition and bin packing. Such a problem has no pseudo-polynomial algorithm and no FPTAS unless P = NP.
See [Chapter 22](22-NP-Completeness.md#226-karps-21-problems-co-np-and-pspace) and [Chapter 23](23-Approximation-and-Parameterized-Algorithms.md#234-a-knapsack-fptas).

**Subset sum**
The problem: given positive integers and a target $T$, is there a subset that adds up to exactly $T$? It is NP-complete, yet solvable in pseudo-polynomial time, and meet in the middle solves it in $O^*(2^{n/2})$.
See [Chapter 14](14-Backtracking-and-Branch-and-Bound.md#142-subsets-permutations-combinations) and [Chapter 22](22-NP-Completeness.md#225-a-chain-of-reductions-proved).

**Suffix array**
The list of starting positions of the suffixes of a text in sorted order. Built by prefix doubling in $O(n \log n)$ and paired with the LCP array, it finds a pattern in $O(m \log n)$ and answers questions about repeats and distinct substrings.
See [Chapter 18](18-String-Algorithms.md#185-suffix-arrays-and-the-lcp-array).

**Suffix automaton**
The smallest automaton that accepts exactly the substrings of a text (also called a DAWG). It has at most $2n - 1$ states, is built online in linear time with suffix links, and counts distinct substrings.
See [Chapter 18](18-String-Algorithms.md#186-suffix-trees-suffix-automata-and-the-burrows-wheeler-transform).

**Suffix tree**
The compressed trie of all suffixes of $T\$$, with one leaf per suffix and every chain of one-child nodes merged into a single edge. It has linear size, can be built online in linear time (Ukkonen), and finds a pattern in $O(m)$.
See [Chapter 18](18-String-Algorithms.md#186-suffix-trees-suffix-automata-and-the-burrows-wheeler-transform).

**Sweep line**
A geometric technique that moves a line across the plane, keeping the objects it cuts in order in a balanced search tree and handling events where that order changes. Bentley-Ottmann uses it to report all $k$ crossings of $n$ segments in $O((n + k) \log n)$.
See [Chapter 20](20-Computational-Geometry.md#204-sweep-line-algorithms).

## T

**Tail bound**
An upper bound on the probability that a random variable is far from its mean, such as the Markov, Chebyshev and Chernoff bounds. It turns "fast on average" into "almost always fast".
See [Chapter 21](21-Randomized-and-Amortized-Analysis.md#213-tail-bounds-markov-chebyshev-chernoff).

**Tarjan's algorithm**
A single-pass DFS algorithm for strongly connected components that keeps vertices on a stack and pops a component whenever a vertex's low-link equals its own index. It emits the components in reverse topological order.
See [Chapter 15](15-Graphs-and-Graph-Search.md#155-strongly-connected-components).

**Three-SAT (3-SAT)**
SAT restricted to CNF formulas in which every clause has exactly three literals. It is NP-complete and the usual starting point for reductions, while 2-SAT, with two literals per clause, is in P.
See [Chapter 22](22-NP-Completeness.md#225-a-chain-of-reductions-proved).

**Three-SUM conjecture (3SUM)**
The conjecture that deciding whether three of $n$ integers sum to zero cannot be done in $O(n^{2-\delta})$ time for any $\delta > 0$. Many problems in computational geometry are 3SUM-hard.
See [Chapter 25](25-Where-Algorithms-Go.md#252-fine-grained-complexity-3sum-seth-edit-distance).

**Time hierarchy theorem**
With more time, strictly more problems can be solved (Hartmanis and Stearns, 1965); in particular $\mathrm{P} \ne \mathrm{EXPTIME}$. It is one of the few separations of complexity classes that is proved.
See [Chapter 22](22-NP-Completeness.md#226-karps-21-problems-co-np-and-pspace) and [Chapter 25](25-Where-Algorithms-Go.md#251-p-versus-np-what-is-known-and-why-it-is-hard).

**Timsort**
Python's list sort, written by Tim Peters in 2002: it finds natural runs, extends short ones with binary insertion sort, merges runs with a balanced policy, and gallops when one run keeps winning. It is stable and very fast on partly sorted data.
See [Chapter 5](05-Sorting-by-Comparison.md#57-inversions-adaptive-sorting-and-timsort).

**Topological order**
An ordering of the vertices of a DAG in which every edge goes from an earlier vertex to a later one. DFS gives one by decreasing finish time, and Kahn's algorithm by repeatedly removing a vertex of in-degree 0.
See [Chapter 15](15-Graphs-and-Graph-Search.md#154-topological-sort).

**Towers of Hanoi**
The puzzle of moving $n$ discs of different sizes between three pegs, one at a time, never putting a larger disc on a smaller. The recursive solution takes $2^n - 1$ moves, and an argument about the largest disc proves no solution is shorter.
See [Chapter 3](03-Recursion-and-Induction.md#38-the-towers-of-hanoi).

**Travelling salesman problem (TSP)**
The problem of finding the shortest closed tour that visits every city exactly once. It is NP-hard; Held-Karp solves it exactly in $O(2^n n^2)$, and for metric distances Christofides' algorithm is within a factor $\tfrac32$, while without the triangle inequality no constant ratio is possible unless P = NP.
See [Chapter 13](13-Dynamic-Programming.md#137-bitmask-dp-travelling-salesman-held-karp) and [Chapter 23](23-Approximation-and-Parameterized-Algorithms.md#232-metric-tsp-mst-doubling-and-christofides).

**Treap**
A binary tree that is a binary search tree by key and a heap by random priority (Seidel and Aragon). The random priorities make its shape that of a random BST, so every operation takes expected $O(\log n)$; it also supports fast split and join.
See [Chapter 8](08-Trees-and-Balanced-Search-Trees.md#86-treaps-and-skip-lists-randomness-instead-of-rules).

**Treewidth**
A number measuring how close a graph is to a tree. Dynamic programming over a tree decomposition solves many NP-hard problems in time exponential only in the treewidth, so they become easy on tree-like graphs.
See [Chapter 13](13-Dynamic-Programming.md#136-dp-on-trees-and-dags) and [Chapter 22](22-NP-Completeness.md#227-what-to-do-with-an-np-hard-problem).

**Triangle inequality**
For shortest-path distances, $\delta(s, v) \le \delta(s, u) + w(u, v)$ for every edge $u \to v$. For a metric, $d(u, w) \le d(u, v) + d(v, w)$: going directly is never longer, which is what makes shortcutting work in metric TSP.
See [Chapter 16](16-Shortest-Paths.md#161-the-problem-relaxation-and-negative-cycles) and [Chapter 23](23-Approximation-and-Parameterized-Algorithms.md#232-metric-tsp-mst-doubling-and-christofides).

**Trie**
A rooted tree that stores a set of strings, with each edge labelled by a letter so that each node stands for the string spelled on the path from the root. Looking up a word of length $m$ takes $O(m)$, and the Aho-Corasick automaton is built on one.
See [Chapter 18](18-String-Algorithms.md#184-many-patterns-tries-and-aho-corasick).

**Turing machine**
Turing's 1936 model of computation: an unbounded tape of cells holding symbols from a finite alphabet, a head that reads and writes one cell at a time, a finite set of states, and a transition table saying what to write, where to move and which state to enter.
See [Chapter 1](01-What-Is-an-Algorithm.md#18-turing-machines-and-the-limits-of-computation).

**Two-opt (2-opt)**
A local search for TSP: repeatedly look for two edges of the tour whose replacement by the two other edges joining the same four cities makes the tour shorter, and reverse the segment between them.
See [Chapter 23](23-Approximation-and-Parameterized-Algorithms.md#232-metric-tsp-mst-doubling-and-christofides) and [Chapter 23](23-Approximation-and-Parameterized-Algorithms.md#238-heuristics-in-practice-local-search-sat-solvers-and-integer-programming-solvers).

## U

**Undecidable problem**
A decision problem that no Turing machine (equivalently, no program) solves, always halting with the right answer. The halting problem is the first example.
See [Chapter 1](01-What-Is-an-Algorithm.md#18-turing-machines-and-the-limits-of-computation).

**Uniform hashing**
The idealised model for open addressing in which each key's probe sequence is equally likely to be any of the $m!$ orderings of the slots. Under it an unsuccessful search costs at most $\frac{1}{1-\alpha}$ probes.
See [Chapter 7](07-Searching-and-Hashing.md#74-open-addressing).

**Union by rank**
The union-find rule that, when linking two roots, hangs the tree of smaller rank (an upper bound on its height) under the larger. It keeps every height at most $\log_2 n$; union by size, using node counts, works the same way.
See [Chapter 10](10-Union-Find-and-Range-Queries.md#102-union-by-rank-path-compression-and-the-inverse-ackermann-bound).

**Union-find**
A data structure for disjoint sets with two operations: find, which returns a name for the set containing an element, and union, which merges two sets. Stored as trees of parent pointers with union by rank and path compression, it costs $O(m\,\alpha(m, n))$ for $m$ operations; also called disjoint-set.
See [Chapter 10](10-Union-Find-and-Range-Queries.md#101-connectivity-as-you-add-edges) and [Chapter 10](10-Union-Find-and-Range-Queries.md#102-union-by-rank-path-compression-and-the-inverse-ackermann-bound).

**Unique Games Conjecture**
Khot's 2002 conjecture that a certain constraint satisfaction problem is hard to approximate. If true, many simple approximation algorithms are optimal, among them the 2-approximation for vertex cover.
See [Chapter 23](23-Approximation-and-Parameterized-Algorithms.md#236-inapproximability-and-the-pcp-theorem) and [Chapter 25](25-Where-Algorithms-Go.md#257-open-problems-and-how-to-keep-learning).

**Universal hashing**
Choosing the hash function at random from a family in which any two different keys collide with probability at most $1/m$ (Carter and Wegman, 1979), such as $h(x) = ((ax + b) \bmod p) \bmod m$. It gives expected $O(1 + \alpha)$ per operation on every input, so no fixed set of keys can be a bad case.
See [Chapter 7](07-Searching-and-Hashing.md#75-universal-hashing).

## V

**Vertex cover**
A set of vertices that touches every edge of a graph. Finding a smallest one is NP-complete, but taking both ends of the edges of a maximal matching gives a 2-approximation, and a bounded search tree finds a cover of size $k$ in $O(2^k m)$.
See [Chapter 22](22-NP-Completeness.md#223-reductions-np-hard-and-np-complete), [Chapter 23](23-Approximation-and-Parameterized-Algorithms.md#231-approximation-ratio-vertex-cover-2-approximation) and [Chapter 23](23-Approximation-and-Parameterized-Algorithms.md#237-fixed-parameter-tractability-vertex-cover-in-o2k-n).

**Voronoi diagram**
The division of the plane into cells, one per site, each holding the points closer to that site than to any other. It has linear size, is dual to the Delaunay triangulation, and Fortune's sweep builds it in $O(n \log n)$.
See [Chapter 20](20-Computational-Geometry.md#206-voronoi-diagrams-delaunay-triangulations-and-k-d-trees).

## W

**White-path theorem**
In a depth-first search, $v$ becomes a descendant of $u$ exactly when, at the moment $u$ is discovered, there is a path from $u$ to $v$ through undiscovered (white) vertices only.
See [Chapter 15](15-Graphs-and-Graph-Search.md#153-depth-first-search).

**Word RAM**
The RAM model in which keys are integers that fit in a machine word and can be used as array indices or split into bits. It allows non-comparison sorts such as counting sort and radix sort to beat the $n \log n$ bound.
See [Chapter 6](06-Sorting-in-Linear-Time-and-Selection.md#61-beating-n-log-n-by-not-comparing-counting-sort).

**Work and span**
The two measures of a parallel computation viewed as a DAG of tasks: the work $W$ is the total number of tasks, its time on one processor, and the span $S$ is the length of the longest path, its time on unboundedly many processors. Their ratio $W/S$ is the parallelism.
See [Chapter 24](24-Algorithms-for-Big-Data-and-Many-Processors.md#245-parallel-algorithms-work-and-span-brents-theorem-prefix-sums-mapreduce).

**Worst case**
The largest cost of an algorithm over all inputs of size $n$. It is a guarantee that no input takes longer, and in this book "the running time" means the worst case unless stated otherwise.
See [Chapter 2](02-Measuring-Cost.md#22-worst-best-and-average-case).

## Z

**Z-algorithm**
The linear-time algorithm that computes, for each position of a string, the length of the longest substring starting there that is also a prefix of the string. It reuses the rightmost Z-box found so far to avoid re-reading characters.
See [Chapter 18](18-String-Algorithms.md#183-the-z-algorithm-rabin-karp-and-rolling-hashes).

**Zero-one BFS (0-1 BFS)**
A shortest-path algorithm for graphs whose edge weights are all 0 or 1 that uses a deque instead of a priority queue: a vertex reached by a 0-edge goes to the front, by a 1-edge to the back. It runs in $O(V + E)$.
See [Chapter 16](16-Shortest-Paths.md#167-real-road-maps-landmarks-shortcuts-and-0-1-bfs).
