# 4. Heuristic search

*Uninformed search has no sense of direction. On the Mars map of Chapter 3, uniform-cost search from Olympus Mons
expanded Valles Marineris, a place in the wrong direction, just because it was cheap to reach. People do not search
like that: they use rough estimates, "Jezero is that way, about 8000 km", to decide what to try first. This chapter
makes such estimates, called heuristics, precise. You will meet greedy best-first search and A\*, and prove exactly
when A\* is guaranteed to find the best solution. You will learn how to invent good heuristics by relaxing a
problem, and how to measure them, building pattern databases for the 8-puzzle. When memory runs out, IDA\* and
RBFS keep the guarantees in linear space; when time runs out, weighted A\* and anytime search trade a little quality
for a lot of speed. The chapter ends by planning a rover's route across a synthetic, Mars-like terrain.*

!!! abstract "In this chapter"
    **You will learn:**

    - what a heuristic function is, and greedy best-first search, with why it is fast but neither optimal nor (as a
      tree search) complete
    - A\*: admissible and consistent heuristics, proofs that A\* is optimal (tree search with an admissible
      heuristic, graph search with a consistent one), contours, and why A\* expands every node with $f < C^{*}$
    - how to design heuristics: relaxed problems, dominance, the effective branching factor, Manhattan distance and
      additive pattern databases for the 8-puzzle
    - memory-bounded search: IDA\* (Korf 1985) and RBFS (Korf 1993), with their guarantees and costs
    - weighted A\*, with the proof that its solutions cost at most $w$ times the optimum, and anytime search
    - path planning on a cost grid, and what real rover planners add

    **You need:** [Chapter 3](03-Uninformed-Search.md) (problem formulation, the generic search, uniform-cost
    search). [Section 16.6 of the Algorithms book](../algorithms/16-Shortest-Paths.md#166-a-search-and-bidirectional-search)
    proves A\* by reweighting edges; this chapter gives the other classic proofs and links there rather than
    repeating that one.

    **Levels:** 4.1 is beginner; 4.2 is intermediate; 4.3 is intermediate; 4.4 and 4.5 are advanced; 4.6 is
    intermediate.

## 4.1 Heuristics; greedy best-first search

How far is Jezero crater from Olympus Mons? We do not know the length of the best route until we have found it.
But we do know something for free: no road can be shorter than the great-circle distance between its ends, the
"straight line" on the sphere. From Olympus Mons that distance is 7798 km.

A **heuristic function** $h(n)$ is an estimate of the cost of the cheapest path from the state at node $n$ to a goal
state. It depends only on the state, and it must be cheap to compute. By convention $h(n) = 0$ when $n$ is a goal.
The word comes from the Greek for "find" or "discover" (the same root as "eureka", "I have found it"); in AI it means a
rule of thumb that usually helps and comes with no guarantee by itself.

For the Mars map we use $h_{\text{SLD}}$, the straight-line (great-circle) distance to Jezero crater:

| Place | $h_{\text{SLD}}$ to Jezero (km) |
|---|---|
| Olympus Mons | 7798 |
| Ascraeus Mons | 8853 |
| Valles Marineris | 8184 |
| Erebus Montes | 5483 |
| Elysium Mons | 3808 |
| Gale crater | 3782 |
| Hellas Planitia | 3616 |
| Utopia Planitia | 3214 |
| Jezero crater | 0 |

Utopia Planitia's estimate (3214) equals the length of its road to Jezero, because every road on this map is a
great-circle arc. That will matter in 4.2.

### Greedy best-first search

The most direct use of $h$: always expand the node that *looks* closest to the goal. **Greedy best-first search** is
the generic search of Chapter 3 with the frontier ordered by $h(n)$.

From Olympus Mons, the neighbours are Ascraeus Mons ($h = 8853$), Erebus Montes ($h = 5483$) and Gale crater
($h = 3782$). Greedy picks Gale crater, the one that looks closest. From Gale, Jezero crater has $h = 0$, so it is
picked next: done, after expanding only 2 nodes. The route Olympus Mons, Gale crater, Jezero crater is 9119 km
long. But Chapter 3 showed that a route of 7888 km exists. Greedy search found the route that *started* closest to
the goal, not the best one: Gale is close to Jezero in a straight line, but the road from Olympus to Gale is very
long (5337 km).

On the 8-puzzle with the Manhattan heuristic (defined in 4.3), greedy best-first search finds a solution of 62 moves
for our 20-move instance, expanding 645 nodes, against 60 473 for uniform-cost search. That is the typical trade:
fast, but with poor solutions.

**Theorem 4.1 (greedy best-first search).** Greedy best-first search is not cost-optimal. As a tree search it is
not complete, even in a finite state space; as a graph search it is complete in finite state spaces. Its worst-case
time and space are $O(b^{m})$, where $m$ is the maximum depth.

*Proof.* Non-optimality: the Mars example. Incompleteness of the tree version: take a start $A$ with two
neighbours, a dead end $B$ that lies toward the goal and so looks close ($h(B) = 2$), and $C$ ($h(C) = 4$), from
which a road leads on to the goal; let $h(A) = 3$. Tree search expands $A$, then $B$ (smallest $h$), whose only
child is $A$ again ($h = 3 < 4$), then $A$, then $B$, forever, while $C$ waits (exercise 2 spells this out).
Completeness of the graph version: it expands each state at most once, so in a finite space it stops; by the
separation property of Chapter 3 (Theorem 3.2), stopping without a goal means none is reachable. The time and space
bound is the size of the whole tree to depth $m$. $\square$

A good heuristic can make greedy search very fast in practice; a bad one can make it explore everything. Its flaw is
structural: it ignores the cost already paid, $g(n)$.

## 4.2 A\* search: admissibility, consistency and optimality

*Level: intermediate.*

The fix is to add the cost so far to the estimate of the cost to go. **A\* search** (pronounced "A star") orders the
frontier by

$$
f(n) = g(n) + h(n),
$$

where $g(n)$ is the cost of the path from the start to $n$ and $h(n)$ is the estimated cost from $n$ to a goal. So
$f(n)$ is the estimated cost of the cheapest solution *through* $n$. With $h = 0$, A\* is uniform-cost search; with
$g$ ignored, it is greedy search.

### A trace on the Mars map

From Olympus Mons to Jezero crater, with $f = g + h_{\text{SLD}}$ (all in km). The program `ch04_astar.py` prints
this trace:

```
A* on the Mars map, Olympus Mons to Jezero crater (km):
  expand Olympus Mons     g=    0 f= 7798  frontier: Erebus Montes 7852, Gale crater 9119, Ascraeus Mons 10593
  expand Erebus Montes    g= 2369 f= 7852  frontier: Utopia Planitia 7888, Elysium Mons 8192, Gale crater 9119, Ascraeus Mons 10593
  expand Utopia Planitia  g= 4674 f= 7888  frontier: Jezero crater 7888, Elysium Mons 8192, Gale crater 9119, Ascraeus Mons 10593
  expand Jezero crater    g= 7888 f= 7888  goal
```

Check the first line by hand. Erebus Montes: $g = 2369$ (the road from Olympus), $h = 5483$, $f = 7852$. Gale crater:
$g = 5337$, $h = 3782$, $f = 9119$. Ascraeus Mons: $1740 + 8853 = 10\,593$. Greedy picked Gale (smallest $h$); A\*
picks Erebus (smallest $f$), because the long road to Gale has already used most of the budget. From Erebus, Utopia
Planitia gets $g = 2369 + 2305 = 4674$ and $f = 4674 + 3214 = 7888$. Expanding Utopia generates Jezero with
$g = 4674 + 3214 = 7888$, $f = 7888$, the smallest on the frontier, so it is expanded next, and it is the goal.

A\* expanded 3 nodes before the goal, where uniform-cost search expanded 7, and found the same optimal route of
7888 km. It never looked at Valles Marineris or Ascraeus Mons beyond generating Ascraeus: their $f$ values exceed
the cost of the solution.

### Admissible heuristics, and why A\* tree search is optimal

A heuristic is **admissible** if it never overestimates:

$$
h(n) \le h^{*}(n) \quad \text{for every node } n,
$$

where $h^{*}(n)$ is the true cost of the cheapest path from $n$ to a goal. An admissible heuristic is optimistic. The
straight-line distance is admissible: no road is shorter than the straight line between its ends, so no route is
shorter than the straight line from its start to its end.

**Theorem 4.2 (A\* tree search is optimal).** If $h$ is admissible, every action costs at least $\varepsilon > 0$, and
the branching factor is finite, then A\* as a tree search (with the goal test on expansion) returns an optimal
solution.

*Proof.* Let $C^{*}$ be the optimal solution cost. Suppose, for contradiction, that A\* is about to expand a goal node
$G_2$ with $g(G_2) > C^{*}$. Since $h(G_2) = 0$, $f(G_2) = g(G_2) > C^{*}$. Take an optimal solution path. Its
start node was put on the frontier at the beginning, and every time a node on the path is expanded its successor on
the path is generated; since the goal at the end of the path has not been expanded, some node $n$ of the path is on
the frontier now (the deepest one generated so far). For that node, $g(n)$ is the cost of the optimal path up to $n$,
so

$$
f(n) = g(n) + h(n) \le g(n) + h^{*}(n) = C^{*} < f(G_2),
$$

using admissibility and the fact that the rest of the optimal path from $n$ costs exactly $h^{*}(n)$. So $n$ has a
smaller $f$ than $G_2$ and would be expanded first: a contradiction. Hence the first goal expanded has cost
$C^{*}$. Finally, A\* does expand some goal: every node with $f \le C^{*}$ has depth at most $C^{*}/\varepsilon$
(each action costs at least $\varepsilon$ and $h \ge 0$), so with a finite branching factor there are finitely many
of them, and while the optimal goal is unexpanded some node of the optimal path with $f \le C^{*}$ is waiting. $\square$

### Consistent heuristics, and graph search

Graph search discards a node when its state has already been reached, unless the new path is cheaper; if a cheaper
path to an *expanded* state turns up, the state must be **reopened** and expanded again. With an admissible heuristic
that can happen. A stronger condition rules it out.

A heuristic is **consistent** (or **monotone**) if for every node $n$, every action $a$ and the resulting
successor $n'$,

$$
h(n) \le c(n, a, n') + h(n'),
$$

and $h(G) = 0$ for goals. This is a triangle inequality: the estimate from $n$ is no more than the cost of one step
plus the estimate from where the step leads. On the Mars map it holds because roads are great-circle arcs and
spherical distance obeys the triangle inequality.

**Lemma 4.3.** Every consistent heuristic is admissible.

*Proof.* Let $n = n_0, n_1, \dots, n_k$ be a cheapest path from $n$ to a goal $n_k$, with step costs
$c_1, \dots, c_k$. Applying consistency $k$ times,
$h(n_0) \le c_1 + h(n_1) \le c_1 + c_2 + h(n_2) \le \dots \le c_1 + \dots + c_k + h(n_k) = h^{*}(n) + 0$. $\square$

The converse is false. Exercise 3 gives an admissible heuristic that is not consistent, on which graph-search A\*
without reopening returns a suboptimal path. Admissible heuristics that occur in practice are, however, almost always
consistent; the misplaced-tiles and Manhattan heuristics below are, and the program checks this on all 181 440 states
of the 8-puzzle.

**Lemma 4.4 (f never decreases along a path).** If $h$ is consistent, then along any path, $f$ values are
non-decreasing: for a node $n$ and its successor $n'$, $f(n') \ge f(n)$.

*Proof.* $f(n') = g(n') + h(n') = g(n) + c(n, a, n') + h(n') \ge g(n) + h(n) = f(n)$, by consistency. $\square$

**Theorem 4.5 (A\* graph search is optimal with a consistent heuristic).** If $h$ is consistent (and action costs
and branching factor are as in Theorem 4.2), then whenever graph-search A\* expands a node, the path to it is a
cheapest path to its state. Hence no state ever needs to be reopened, each state is expanded at most once, and the
first goal expanded is optimal.

*Proof.* By induction on the number of expansions, we show that every node expanded so far had the optimal $g$
for its state. Suppose this holds so far and A\* now selects node $n$ with state $s$, but $g(n) > g^{*}(s)$, the
cheapest cost of reaching $s$. Take a cheapest path $P$ from the start to $s$. The start state has been expanded and
$s$ has not, so $P$ has a first state $s''$ that has not been expanded. Its predecessor on $P$ was expanded, with its
optimal $g$ by the induction hypothesis, and that expansion generated $s''$ with cost $g^{*}(s'')$ (a prefix of a
cheapest path is a cheapest path); so $s''$ is on the frontier with a node $n''$ of cost $g(n'') = g^{*}(s'')$. By
Lemma 4.4 applied to the rest of $P$, from $s''$ to $s$,

$$
f(n'') = g^{*}(s'') + h(s'') \le g^{*}(s) + h(s) < g(n) + h(s) = f(n).
$$

So $n''$ has a smaller $f$ than $n$ and would have been selected first: a contradiction. Hence $g(n) = g^{*}(s)$
whenever $n$ is expanded, no expanded state is ever found again more cheaply, and no reopening is needed. For a
goal, $h = 0$ and $f = g$; the first goal expanded has the smallest $f$ of all frontier nodes, and every other goal
node expanded later has an $f$ at least as large, so the first goal returned is optimal. $\square$

[Theorem 16.9 of the Algorithms book](../algorithms/16-Shortest-Paths.md#166-a-search-and-bidirectional-search) gives
a different, very clean proof: with a consistent $h$, A\* is exactly Dijkstra's algorithm on the edge costs
$c(u, v) - h(u) + h(v)$, which are non-negative precisely because $h$ is consistent. Both proofs say the same thing:
consistency makes $f$ behave like a distance.

### Contours, and which nodes A\* expands

Lemma 4.4 gives a picture. Since A\* expands nodes in order of non-decreasing $f$, we can draw **contours** in the
state space: the set of states with $f \le 7900$, with $f \le 8500$, and so on. Uniform-cost search ($h = 0$) has
round contours centred on the start; a good heuristic stretches them toward the goal. The better the heuristic, the
more narrowly the contours hug the optimal path.

<figure class="mars-fig" markdown="0">
<svg viewBox="0 0 600 265" role="img" aria-label="Two panels. Left, uniform-cost search: circular contours of equal g around the start, the goal far to the right inside the largest circle. Right, A star: contours of equal f stretched into ellipses from the start toward the goal, enclosing far less area.">
  <text x="150" y="22" font-size="13" text-anchor="middle" fill="currentColor">uniform-cost search (h = 0)</text>
  <circle cx="115" cy="135" r="30" fill="#9cc9ea" fill-opacity="0.5" stroke="currentColor"/>
  <circle cx="115" cy="135" r="60" fill="none" stroke="currentColor" stroke-dasharray="4 3"/>
  <circle cx="115" cy="135" r="95" fill="none" stroke="currentColor" stroke-dasharray="4 3"/>
  <circle cx="115" cy="135" r="5" fill="currentColor"/>
  <circle cx="210" cy="135" r="6" fill="#7ccf9a" stroke="currentColor"/>
  <text x="115" y="155" font-size="11" text-anchor="middle" fill="currentColor">start</text>
  <text x="222" y="158" font-size="11" text-anchor="middle" fill="currentColor">goal</text>
  <text x="275" y="118" font-size="11" text-anchor="middle" fill="currentColor">g = C*</text>
  <line x1="207" y1="112" x2="255" y2="114" stroke="currentColor" stroke-opacity="0.5"/>
  <text x="450" y="22" font-size="13" text-anchor="middle" fill="currentColor">A* (f = g + h)</text>
  <ellipse cx="400" cy="135" rx="45" ry="22" fill="#eea66f" fill-opacity="0.45" stroke="currentColor"/>
  <ellipse cx="420" cy="135" rx="78" ry="36" fill="none" stroke="currentColor" stroke-dasharray="4 3"/>
  <ellipse cx="438" cy="135" rx="105" ry="48" fill="none" stroke="currentColor" stroke-dasharray="4 3"/>
  <circle cx="345" cy="135" r="5" fill="currentColor"/>
  <circle cx="537" cy="135" r="6" fill="#7ccf9a" stroke="currentColor"/>
  <text x="345" y="160" font-size="11" text-anchor="middle" fill="currentColor">start</text>
  <text x="547" y="160" font-size="11" text-anchor="middle" fill="currentColor">goal</text>
  <text x="450" y="210" font-size="11" text-anchor="middle" fill="currentColor">outer contour: f = C*</text>
  <text x="300" y="256" font-size="12" text-anchor="middle" fill="currentColor">each dashed curve joins states of equal g (left) or equal f (right)</text>
</svg>
<figcaption>Figure 4.1. Contours. Uniform-cost search expands everything inside the circle $g = C^{*}$; A\* with a
consistent heuristic expands everything inside the contour $f = C^{*}$, which a good heuristic stretches toward the
goal. The shaded regions are the states expanded early in each search.</figcaption>
</figure>

**Theorem 4.6 (which nodes A\* expands).** With a consistent heuristic, graph-search A\* expands every node with
$f(n) < C^{*}$ (it *must*), may expand some with $f(n) = C^{*}$ (depending on tie-breaking), and expands no node with
$f(n) > C^{*}$.

*Proof.* A\* expands nodes in non-decreasing order of $f$ (Lemma 4.4 and the priority queue) and stops when it
expands the goal, whose $f$ is $C^{*}$ (Theorem 4.5). So every node expanded has $f \le C^{*}$. Conversely, a
reachable state $s$ with $f < C^{*}$ along its cheapest path: by the separation property, until $s$ is expanded,
some state on the cheapest path to it sits on the frontier with $f < C^{*}$ (by Lemma 4.4, $f$ along that path is at
most $f$ at $s$), so the goal, with $f = C^{*}$, cannot be taken first. $\square$

Two consequences. First, A\* **prunes**: whole subtrees with $f > C^{*}$ (Valles Marineris on our map) are never
expanded, without being examined. Second, A\* is **optimally efficient** in a precise sense, proved by Dechter and
Pearl (1985): among algorithms that extend search paths from the start and use the same consistent heuristic, none
can be guaranteed to find an optimal solution while expanding fewer nodes than those with $f < C^{*}$, since any
such node, left unexamined, might hide a cheaper solution. The full statement has conditions on tie-breaking and on
what the competing algorithms may do; the idea is that A\* does the unavoidable work and almost nothing else.

That does not make A\* cheap. The number of nodes with $f < C^{*}$ can still be exponential in the solution length.
For tree search on idealised problems (a uniform tree with one goal), the analysis summarised by Pearl (1984) shows
the number of nodes expanded grows subexponentially only if the heuristic's error $|h(n) - h^{*}(n)|$ grows no faster
than the logarithm of $h^{*}(n)$; for heuristics with a constant *relative* error, which is typical, growth stays
exponential, though with a much smaller base than blind search. The effective branching factor of 4.3 measures that
base.

### A\* on the 8-puzzle

```python
--8<-- "books/ai/ch04_astar.py"
```

Output:

```
A* on the Mars map, Olympus Mons to Jezero crater (km):
  expand Olympus Mons     g=    0 f= 7798  frontier: Erebus Montes 7852, Gale crater 9119, Ascraeus Mons 10593
  expand Erebus Montes    g= 2369 f= 7852  frontier: Utopia Planitia 7888, Elysium Mons 8192, Gale crater 9119, Ascraeus Mons 10593
  expand Utopia Planitia  g= 4674 f= 7888  frontier: Jezero crater 7888, Elysium Mons 8192, Gale crater 9119, Ascraeus Mons 10593
  expand Jezero crater    g= 7888 f= 7888  goal
  UCS     Olympus Mons > Erebus Montes > Utopia Planitia > Jezero crater: 7888 km, expanded 7
  greedy  Olympus Mons > Gale crater > Jezero crater: 9119 km, expanded 2
  A*      Olympus Mons > Erebus Montes > Utopia Planitia > Jezero crater: 7888 km, expanded 3

8-puzzle from (7, 2, 4, 5, 0, 6, 8, 3, 1): h1 = 6, h2 = 14
  algorithm     moves  generated  expanded
  UCS              20     161168     60473
  greedy h2        62       1781       645
  A* h1            20       6325      2336
  A* h2            20        245        91

over all 181440 states: h1 <= h2 <= h* everywhere: True; both consistent: True
  mean h1 7.11, mean h2 14.00, mean true cost 21.97; h2 exact on 2351 states
```

The A\* in the program breaks ties between equal $f$ values in favour of the larger $g$, the deeper node. Among
nodes with the same estimate of total cost, the deeper one has less of that estimate left as guesswork, and on the
8-puzzle the last $f$-layer is large, so tie-breaking matters (try changing it: exercise 9). The results show the
heuristics at work. Uniform-cost search generated 161 168 nodes; A\* with the misplaced-tiles heuristic $h_1$
generated 6325, and with the Manhattan heuristic $h_2$ only 245, all finding the optimal 20 moves. The last two
lines check, over every reachable state, that $h_1 \le h_2 \le h^{*}$ and that both heuristics are consistent. On
average $h_2$ is 14.00 while the true distance is 21.97: even the better heuristic sees only about two thirds of the
true cost.

## 4.3 Designing heuristics

*Level: intermediate.*

Where do good heuristics come from? The 8-puzzle shows the method.

### Two heuristics for the 8-puzzle

- $h_1$ = the number of **misplaced tiles** (not counting the blank). For our start state `(7, 2, 4, 5, 0, 6, 8, 3,
  1)`, only tiles 2 and 6 are in their goal squares, so $h_1 = 6$. It is admissible: each misplaced tile needs at
  least one move.
- $h_2$ = the sum of the **Manhattan distances** of the tiles from their goal squares: the number of rows plus the
  number of columns each tile is away from home. (The name is from the street grid of Manhattan, where you travel
  along blocks, never diagonally.) For the start state: tile 7 is at row 0, column 0 and belongs at row 2, column 0:
  distance 2. Tile 2: 0. Tile 4 (row 0, col 2; goal row 1, col 0): $1 + 2 = 3$. Tile 5 (1, 0; goal 1, 1): 1. Tile 6: 0.
  Tile 8 (2, 0; goal 2, 1): 1. Tile 3 (2, 1; goal 0, 2): $2 + 1 = 3$. Tile 1 (2, 2; goal 0, 0): $2 + 2 = 4$. Total
  $2 + 0 + 3 + 1 + 0 + 1 + 3 + 4 = 14$. It is admissible: each move moves one tile one square, reducing that tile's
  distance by at most one.

Both are consistent: a move changes $h_1$ by at most 1 (one tile moves) and $h_2$ by exactly 1 (one tile moves one
square closer or farther), while the move costs 1.

### Relaxed problems

Here is the deeper reason both work. The 8-puzzle's rule is: *a tile can move from square A to square B if A is
adjacent to B and B is blank.* Remove conditions and you get easier problems:

1. a tile can move from A to B if A is adjacent to B (ignore "B is blank");
2. a tile can move from A to B if B is blank (ignore adjacency);
3. a tile can move from A to B (ignore both).

In (3), each misplaced tile needs exactly one move, and the optimal solution cost is $h_1$. In (1), each tile
moves independently along the grid, and the optimal cost is $h_2$. Problem (2) gives a heuristic proposed by
Gaschnig (1979), which exercise 8 builds. A problem with fewer restrictions on the actions is called a **relaxed
problem**.

**Theorem 4.7 (relaxation gives consistent heuristics).** If $h$ is the exact optimal cost in a relaxed problem,
whose state space has the same states and *at least* the same actions with the same costs, then $h$ is admissible
and consistent for the original problem.

*Proof.* The relaxed state-space graph contains every edge of the original (and maybe more). *Admissible:* an
optimal solution of the original problem from $n$ is also a solution of the relaxed problem, so the relaxed optimum
is no larger: $h(n) \le h^{*}(n)$. *Consistent:* $h$ is the true distance-to-goal in the relaxed graph, and true
distances obey the triangle inequality: for an original action $n \to n'$, which is also a relaxed action, going
from $n$ by that action and then optimally from $n'$ is one relaxed path to the goal, so
$h(n) \le c(n, a, n') + h(n')$. $\square$

Relaxed problems must also be easy to solve, or the heuristic costs more than it saves. Problem (1) is easy because
it breaks into eight independent single-tile problems. Programs have been written that generate heuristics
automatically from formal problem descriptions by trying relaxations; the planners of Chapter 10 use exactly this
idea ("ignore the delete lists").

### Dominance

If two admissible heuristics satisfy $h_2(n) \ge h_1(n)$ for every $n$, we say $h_2$ **dominates** $h_1$.

**Theorem 4.8.** If $h_1$ and $h_2$ are consistent and $h_2$ dominates $h_1$, then every node that A\* with $h_2$
must expand is also expanded by A\* with $h_1$. (A\* with $h_2$ never does more work, apart from ties on
$f = C^{*}$.)

*Proof.* By Theorem 4.6, A\* with $h_2$ must expand exactly the nodes with $g(n) + h_2(n) < C^{*}$ (with $g$ the
optimal cost to $n$'s state). For such a node, $g(n) + h_1(n) \le g(n) + h_2(n) < C^{*}$, so A\* with $h_1$ must
expand it too. $\square$

So higher is better, as long as it stays admissible, and as long as it is not too expensive to compute. Given
several admissible heuristics and none dominating, take their **maximum**, $h(n) = \max(h_a(n), h_b(n), \dots)$: it
is admissible (each part is at most $h^{*}$), consistent if each part is (exercise 4), and dominates every part.

### The effective branching factor

How to compare heuristics with one number? If A\* generates $N$ nodes for a solution at depth $d$, the **effective
branching factor** $b^{*}$ is the branching factor a uniform tree of depth $d$ would need to have $N + 1$ nodes:

$$
N + 1 = 1 + b^{*} + (b^{*})^{2} + \dots + (b^{*})^{d}.
$$

For example, 52 nodes at depth 5 gives $b^{*} \approx 1.92$ (solve numerically; the program uses bisection). A
good heuristic has $b^{*}$ close to 1, so that large problems stay affordable; and $b^{*}$ tends to be fairly
constant across problem sizes for a given heuristic, which makes it a useful summary.

### Pattern databases

Can we do better than Manhattan distance? Its weakness is that it treats tiles as independent: two tiles in each
other's way, in the same row, each count only their own distance, though one must step aside. A **pattern database**
(Culberson and Schaeffer, 1996 and 1998) captures interactions within a group of tiles exactly.

Choose a **pattern**, a subset of the tiles, say $\{1, 2, 3, 4\}$. Ignore the identities of the other tiles (treat
them as indistinguishable "don't care" tiles). The abstract state is the positions of the pattern tiles and of the
blank: $9 \times 8 \times 7 \times 6 \times 5 = 15\,120$ abstract states. Compute, once, the exact cost of solving
every abstract state by a breadth-first search backward from the abstract goal, and store it in a table. During
search, look up the current state's abstract state. That value is an exact solution cost of a relaxed problem (the
other tiles are interchangeable), so by Theorem 4.7 it is admissible and consistent.

Can we add the values of two databases, for $\{1,2,3,4\}$ and $\{5,6,7,8\}$? Not in general: both counts include
moves of the "don't care" tiles, so a move could be counted twice. The fix (Korf and Felner, 2002) is to count, in
each database, *only the moves of that database's own tiles*: moving the blank past a "don't care" tile costs 0 in
the abstract problem. Every real move moves exactly one tile, which belongs to exactly one pattern, so the sum of
the two values never exceeds the number of real moves: an **additive** (disjoint) pattern database. Each table is
built by a **0-1 BFS** (a breadth-first search in which zero-cost edges are put at the front of the deque, as in
[Section 16.7 of the Algorithms book](../algorithms/16-Shortest-Paths.md#167-real-road-maps-landmarks-shortcuts-and-0-1-bfs)).
The additive database also dominates Manhattan distance, because each pattern's value is at least the sum of its
tiles' Manhattan distances (each counted move moves one of its tiles one square).

```python
--8<-- "books/ai/ch04_heuristics.py"
```

Output:

```
pattern databases: 15120 and 15120 entries
h2 <= pdb <= true cost on all 181440 states: True
mean values: h1 7.11, h2 14.00, pdb 19.13, true 21.97

mean nodes generated (and effective branching factor), 10 states per depth
    d              BFS            A* h1            A* h2           A* pdb
    4        35 (2.09)        12 (1.50)        12 (1.49)        12 (1.49)
    8       375 (1.91)        44 (1.38)        27 (1.27)        24 (1.24)
   12      2606 (1.80)       188 (1.39)        60 (1.23)        37 (1.16)
   16                -      1193 (1.45)       229 (1.28)        56 (1.14)
   20                -      6841 (1.47)       652 (1.28)       111 (1.15)
   24                -                -      1596 (1.28)       159 (1.13)
   28                -                -      6763 (1.30)       364 (1.15)
```

<figure class="mars-fig" markdown="0">
<svg viewBox="0 0 600 270" role="img" aria-label="Nodes generated against solution depth, log scale, for breadth-first search and A star with misplaced tiles, Manhattan distance and the additive pattern database. Breadth-first rises steepest, then misplaced tiles, then Manhattan; the pattern database curve is the flattest.">
  <line x1="70" y1="220" x2="565" y2="220" stroke="currentColor" stroke-width="1.5"/>
  <line x1="70" y1="25" x2="70" y2="220" stroke="currentColor" stroke-width="1.5"/>
  <g font-size="11" fill="currentColor" text-anchor="end">
    <text x="62" y="224">10</text><text x="62" y="161">100</text><text x="62" y="97">1000</text><text x="62" y="34">10000</text>
  </g>
  <g stroke="currentColor" stroke-opacity="0.25">
    <line x1="70" y1="157" x2="565" y2="157"/><line x1="70" y1="93" x2="565" y2="93"/><line x1="70" y1="30" x2="565" y2="30"/>
  </g>
  <g font-size="11" fill="currentColor" text-anchor="middle">
    <text x="70" y="236">4</text><text x="152" y="236">8</text><text x="233" y="236">12</text><text x="315" y="236">16</text>
    <text x="397" y="236">20</text><text x="478" y="236">24</text><text x="560" y="236">28</text>
    <text x="315" y="258">solution depth d</text>
  </g>
  <text x="18" y="125" font-size="12" text-anchor="middle" fill="currentColor" transform="rotate(-90 18 125)">nodes generated</text>
  <polyline points="70,186 152,120 233,67" fill="none" stroke="currentColor" stroke-width="2" stroke-dasharray="5 3"/>
  <polyline points="70,215 152,179 233,139 315,88 397,40" fill="none" stroke="#eea66f" stroke-width="2.5"/>
  <polyline points="70,215 152,193 233,171 315,134 397,105 478,80 560,41" fill="none" stroke="#9cc9ea" stroke-width="2.5"/>
  <polyline points="70,215 152,196 233,184 315,173 397,154 478,144 560,121" fill="none" stroke="#7ccf9a" stroke-width="2.5"/>
  <g font-size="11" fill="currentColor">
    <text x="240" y="62">BFS</text>
    <text x="404" y="44">A* h1</text>
    <text x="500" y="72">A* h2</text>
    <text x="500" y="128">A* pdb</text>
  </g>
</svg>
<figcaption>Figure 4.2. Mean nodes generated by depth on the 8-puzzle (log scale), from the table above. A straight
line on this scale is exponential growth; its slope is $\log b^{*}$. Better heuristics give flatter lines.</figcaption>
</figure>

Read the table across a row. At depth 12, BFS generated 2606 nodes, A\* with $h_1$ 188, with $h_2$ 60, with the
pattern database 37. Down a column, the effective branching factor of each method is roughly constant: about 1.8 to
2.1 for BFS, 1.4 to 1.5 for $h_1$, about 1.28 for $h_2$, about 1.15 for the pattern database. At depth 28 the
pattern database generates about 18 times fewer nodes than Manhattan distance. The cost is the tables: 2 × 15 120
entries, built once, in well under a second. For the 15-puzzle and 24-puzzle, where blind search is hopeless,
additive pattern databases are what made optimal solving practical (Korf and Felner, 2002), and the 24-puzzle was
first solved optimally in the 1990s with heuristic search (Korf and Taylor, 1996).

**Learning heuristics.** Another source of heuristics is experience: solve many instances, record features of
states (Manhattan distance, number of tiles in conflict, ...) together with their true costs, and fit a function that
predicts cost from features, for example by linear regression
([Chapter 4 of the Machine learning book](../machine-learning/04-Linear-Regression.md)). A learned heuristic is
usually not admissible, so A\* with it loses the optimality guarantee, though it may search far faster. AlphaGo's
value network (Chapter 6) is a learned evaluation in this spirit.

## 4.4 Memory-bounded search: IDA\* and RBFS

*Level: advanced.*

A\* keeps every node it generates. On large problems memory runs out long before time does, exactly as for BFS in
Chapter 3. Two algorithms keep A\*'s guarantees using memory proportional to the depth.

### IDA\*

**Iterative-deepening A\*** (IDA\*; Korf, 1985) is iterative deepening with $f$ in place of depth. Each iteration is a
depth-first search that cuts off any node whose $f = g + h$ exceeds the current **bound**. The first bound is
$h(\text{start})$. When an iteration fails, the next bound is the smallest $f$ value that exceeded the old bound.

```text
IDA*(problem):
    bound = h(start)
    loop:
        t = DFS(start, g = 0, bound)          # returns FOUND, or the smallest f > bound seen
        if t == FOUND: return the path
        if t == infinity: return failure
        bound = t

DFS(node, g, bound):
    f = g + h(node)
    if f > bound: return f
    if node is a goal: return FOUND
    min = infinity
    for each child not already on the path:
        t = DFS(child, g + cost, bound)
        if t == FOUND: return FOUND
        min = min(min, t)
    return min
```

**Theorem 4.9 (IDA\*).** With an admissible heuristic, positive action costs bounded below by $\varepsilon$ and a
finite branching factor, IDA\* returns an optimal solution, using memory $O(bd)$ where $d$ is the solution's depth.

*Proof.* *Invariant:* the bound never exceeds $C^{*}$. It starts at
$h(\text{start}) \le h^{*}(\text{start}) = C^{*}$. Suppose an iteration with bound $B \le C^{*}$ fails, i.e. finds no goal with $g \le B$. Along the optimal
path, the nodes have $f \le C^{*}$ (admissibility, as in Theorem 4.2). If all of them had $f \le B$, the iteration
would have followed the whole path and found the goal; so some node on it has $B < f \le C^{*}$, and the next bound,
the smallest $f$ above $B$ that was seen, is at most $C^{*}$. *Termination:* each new bound is strictly larger than
the old one and is the $f$ value of some path with $f \le C^{*}$; with costs at least $\varepsilon$ there are
finitely many such paths, so finitely many bounds. *Optimality:* when an iteration with bound $B \le C^{*}$ finds a
goal, that goal has $g = f \le B \le C^{*}$, so it is optimal. *Memory:* each iteration is a depth-first search
keeping only the current path and the siblings along it. $\square$

On the 8-puzzle with Manhattan distance, the bounds rise by 2 each time: 14, 16, 18, 20 for our 20-move instance. Each
move changes $g$ by 1 and $h_2$ by exactly $\pm 1$, so $f$ changes by 0 or 2, and all $f$ values along a search
have the same parity (exercise 6). The number of iterations is the number of distinct $f$ values between
$h(\text{start})$ and $C^{*}$. That is IDA\*'s weakness when costs are real numbers, as on the Mars map: every path
may have a different $f$, each iteration may admit only one new node, and the repetition becomes ruinous. Fixes
increase the bound by more than the minimum and accept a bounded loss of optimality.

### RBFS

**Recursive best-first search** (RBFS; Korf, 1993) imitates best-first order more closely, still in linear space.
It is a recursive search that, at each node, explores the child with the lowest $f$, but only as long as that
child's $f$ stays below the best alternative available elsewhere: the lowest $f$ among the siblings of the nodes on
the current path. If the current subtree's best $f$ grows beyond that limit, RBFS returns, and on the way back it
**backs up** the best $f$ value found in the abandoned subtree into the subtree's root. That value is remembered, so
if the search later comes back to this subtree, it knows how promising it is. The program's `rbfs` function is about
thirty lines; the key line updates a child's stored value with what came back from the recursion.

RBFS with an admissible heuristic is optimal (the backed-up values remain lower bounds on the cost of solutions in
each subtree, so it behaves like A\* with a lower-bound ordering), and it uses $O(bd)$ memory. Its cost is
**re-expansion**: each time it switches to a different subtree it forgets the old one and may have to regenerate
it, many times. Like IDA\*, it cannot use extra memory when there is some. Algorithms such as SMA\* (simplified
memory-bounded A\*; Russell, 1992) use all available memory and drop the worst nodes only when it is full.

```python
--8<-- "books/ai/ch04_memory.py"
```

Output:

```
8-puzzle from (7, 2, 4, 5, 0, 6, 8, 3, 1), h2 = 14
  A*:    20 moves, generated     245, expanded      91, max frontier 64
  IDA*:  20 moves, generated     696, expanded     269, deepest path 20, 4 iterations, bounds [14, 16, 18, 20]
  RBFS:  20 moves, generated     791, expanded     300, deepest path 20
8-puzzle from (8, 6, 7, 2, 5, 4, 3, 0, 1), h2 = 21
  A*:    31 moves, generated   17853, expanded    6784, max frontier 3568
  IDA*:  31 moves, generated   36978, expanded   14195, deepest path 31, 6 iterations, bounds [21, 23, 25, 27, 29, 31]
  RBFS:  31 moves, generated   36410, expanded   13965, deepest path 31
```

All three find the optimal 20 and 31 moves (the second instance is one of the two farthest states of the 8-puzzle,
from Chapter 3). IDA\* and RBFS generate about two to three times as many nodes as A\*, because they repeat work, but
their memory is the current path, at most 31 nodes, against A\*'s frontier of 3568 plus a table of every state
reached. On the 15-puzzle (about $10^{13}$ states), IDA\* with Manhattan distance was the first method to solve
random instances optimally (Korf, 1985), precisely because it needs no memory to speak of.

## 4.5 Weighted A\* and anytime search

*Level: advanced.*

Sometimes an optimal solution is not worth the wait. A rover with a few minutes of planning time would rather drive
a route 10 percent longer than sit still. **Weighted A\*** (Pohl, 1970) inflates the heuristic:

$$
f_w(n) = g(n) + w \cdot h(n), \qquad w \ge 1.
$$

With $w = 1$ it is A\*; as $w \to \infty$ it approaches greedy search. A larger $w$ makes the search more eager to
dive toward the goal, usually expanding far fewer nodes, and its solutions are provably not too bad.

**Theorem 4.10 (weighted A\* is $w$-admissible).** If $h$ is admissible and $w \ge 1$, then weighted A\* (with
reopening of states, or with a consistent $h$) returns a solution of cost at most $w \cdot C^{*}$.

*Proof.* Suppose weighted A\* is about to expand a goal node $G_2$ with cost $g(G_2)$. As in Theorem 4.2, some node
$n$ of an optimal path is on the frontier, with $g(n)$ equal to the optimal cost of reaching it (with reopening, a
cheaper path to a state is always put back on the frontier, so the deepest generated node of the optimal path carries
its optimal $g$). Then

$$
f_w(n) = g(n) + w\,h(n) \le g(n) + w\,h^{*}(n) \le w\,\big(g(n) + h^{*}(n)\big) = w\,C^{*},
$$

using admissibility and $w \ge 1$. $G_2$ is chosen before $n$, so $f_w(G_2) \le f_w(n)$, and $f_w(G_2) = g(G_2)$
because $h(G_2) = 0$. Hence $g(G_2) \le w\,C^{*}$. $\square$

The bound is a guarantee, not a prediction: in practice weighted A\*'s solutions are usually much closer to
optimal than $w$ times. Here is the 15-puzzle (a 4 × 4 board with $16!/2 \approx 10^{13}$ reachable states), on an
instance scrambled by 50 random moves.

### Anytime search

An **anytime algorithm** returns a valid answer quickly and improves it the longer it runs. Weighted A\* gives one
directly (in the style of Hansen and Zhou, 2007): run weighted A\*, but when it finds a solution of cost $U$, do not
stop. Keep expanding, while **pruning** every node with $g(n) + h(n) \ge U$: with an admissible $h$, such a node
cannot lead to a solution cheaper than $U$. Each new goal reached is cheaper than the last, and $U$ falls. When the
frontier is empty, no node that could beat $U$ remains, so the last solution is optimal: the algorithm has not only
found the optimum but proved it. A related method, ARA\* (Likhachev, Gordon and Thrun, 2003), lowers $w$ step by
step and reuses earlier search effort, and is used in robot motion planning.

```python
--8<-- "books/ai/ch04_weighted.py"
```

Output:

```
15-puzzle start (6, 2, 5, 3, 13, 9, 11, 10, 1, 8, 15, 4, 14, 12, 7, 0), Manhattan h = 28
     w  cost  bound w*C*  expanded
     1    40        40.0     25405
  1.25    40        50.0      3851
   1.5    46        60.0     11481
     2    48        80.0     12623
     3    60       120.0      2445
     5    68       200.0      6322

anytime weighted A* with w = 2:
  solution of cost 48 after 12623 expansions
  solution of cost 42 after 12679 expansions
  solution of cost 40 after 47432 expansions
  frontier empty after 62138 expansions: cost 40 is optimal (A* found 40)
```

Every solution respects its bound $w C^{*}$, and every one is far better than the bound: with $w = 5$ the bound
allows 200 moves, and the solution has 68. The number of expansions is *not* monotone in $w$: $w = 1.25$ found an
optimal solution with 3851 expansions, but $w = 1.5$ and $w = 2$ needed more. A larger weight usually helps, but an
inflated heuristic can also lure the search deep into a region that turns out to be a dead end. That is the honest
state of the art: weighted A\* is a heuristic about heuristics, with a worst-case guarantee on quality but none on
speed.

The anytime run shows the trade-off over time: a 48-move solution after 12 623 expansions, a 42-move one almost at
once afterwards, and the optimal 40 after 47 432. Proving that 40 is optimal took until 62 138 expansions, more than
plain A\* (25 405), because the weighted ordering explores nodes A\* would never touch before the pruning bound
becomes tight. If you need the optimum and its proof, run A\*; if you may be interrupted, run the anytime search.

## 4.6 Path planning on a Mars-like terrain grid

*Level: intermediate.*

Back to the rover. A planner on board sees the terrain ahead as a grid of cells, each with an elevation estimated
from stereo images (Chapter 2, Section 2.6, and Chapter 18). Steep cells and rocks are dangerous; gentle slopes are
safe but cost more energy and time than flat ground. Planning a drive is then a shortest-path problem on a grid with
costs, exactly what A\* is for.

Our terrain is made up, generated from a fixed random seed: a 60 × 60 grid of 1 m cells with low hills, three
craters with raised rims, and rocks scattered over 4 percent of the cells. This is a teaching model, not real Mars
data, and the cost rule is invented for the example. The rover can move to any of the 8 neighbouring cells. A move
costs its length (1 m, or $\sqrt{2}$ m diagonally) times a **slope penalty** $1 + \theta/20°$, where $\theta$ is the
slope of the cell entered; cells steeper than 20 degrees, and rocks, cannot be entered.

The heuristic is the **octile distance**, the length of the shortest 8-connected path on an empty, flat grid: with
$\Delta r$ and $\Delta c$ the row and column differences,
$h = \Delta r + \Delta c + (\sqrt{2} - 2)\min(\Delta r, \Delta c)$ (move diagonally while both differences remain, then straight). Every real move costs at least its flat
length, so this is the exact cost of a relaxed problem (no slopes, no obstacles), hence admissible and consistent by
Theorem 4.7.

```python
--8<-- "books/ai/ch04_terrain.py"
```

Output:

```
terrain 60 x 60: height -5.4 to 1.4 m, 18.1% too steep, 4.0% rocks
start (54, 3), goal (4, 56): straight-line 72.9 m, octile h = 73.7
  planner                   cost  cells  expanded
  Dijkstra (h = 0)          98.8     68      2639
  A* (octile)               98.8     68      1739
  weighted A*, w = 2       109.4     71       133
  greedy best-first        113.1     71        73

A* route (every second row; # blocked, o route, . expanded):
                                                              
                                  #    #......#........       
                       ...................ooooooooooooooooG   
          #         ...#................oo.#######......      
          #      .....................oo## ####### ###        
              ......................oo.# ########### #      # 
        #   ......................oo..# ############# #       
      #  #..........#...........oo....######     ###### ...   
       .......................oo......######     ######....   
     .................#....ooo.........###############......  
    ....................ooo##########...## ##########.......  
   #....#........#....oo.###############..#########..#......  
  ...................oo## ############# ##...#.....#........# 
  ..#...........#..oo.##########    #### ##................   
  ........#......oo..## ######        ### ##...............  #
  ....#........oo#.#.########         ### ##..............    
  ........#.#oo.......# #####         ### ##............#     
  .........oo.### #############     #### ##............       
  ........o.############  ############# ##..#........         
  ......oo.#######  #### ###############............          
  ....oo...######    #####..##########........#...            
  ...o...#.#######  ######.......................  #          
  ...o......#############.................#....               
  ...o........### #####......................                 
  ...o......................................  #            #  
  ...o......................#.............           #        
  ...o.............................#.....                 #   
  ...S...........................#....                    # # 
  .....#......#.#..................  #       #    #           
  ..............................                              
```

<figure class="mars-fig" markdown="0">
<svg viewBox="0 0 600 340" role="img" aria-label="Two copies of the 60 by 60 terrain grid. Blocked cells (steep slopes, crater rims and rocks) are dark. Left: cells expanded by A star with the octile heuristic, a large shaded region, and the optimal route in orange from the bottom left to the top right. Right: cells expanded by weighted A star with w equal to 2, a thin shaded band around its route.">
<text x="155" y="20" font-size="12" text-anchor="middle" fill="currentColor">A*: cost 98.8, 1739 expanded</text>
<text x="455" y="20" font-size="12" text-anchor="middle" fill="currentColor">weighted A* (w = 2): cost 109.4, 133 expanded</text>
<rect x="20" y="30" width="270" height="270" fill="none" stroke="currentColor"/>
<rect x="213.5" y="34.5" width="27" height="4.5" fill="#9cc9ea" fill-opacity="0.6"/>
<rect x="191" y="39" width="27" height="4.5" fill="#9cc9ea" fill-opacity="0.6"/>
<rect x="222.5" y="39" width="36" height="4.5" fill="#9cc9ea" fill-opacity="0.6"/>
<rect x="141.5" y="43.5" width="54" height="4.5" fill="#9cc9ea" fill-opacity="0.6"/>
<rect x="200" y="43.5" width="45" height="4.5" fill="#9cc9ea" fill-opacity="0.6"/>
<rect x="249.5" y="43.5" width="9" height="4.5" fill="#9cc9ea" fill-opacity="0.6"/>
<rect x="114.5" y="48" width="126" height="4.5" fill="#9cc9ea" fill-opacity="0.6"/>
<rect x="245" y="48" width="27" height="4.5" fill="#9cc9ea" fill-opacity="0.6"/>
<rect x="110" y="52.5" width="81" height="4.5" fill="#9cc9ea" fill-opacity="0.6"/>
<rect x="195.5" y="52.5" width="63" height="4.5" fill="#9cc9ea" fill-opacity="0.6"/>
<rect x="101" y="57" width="13.5" height="4.5" fill="#9cc9ea" fill-opacity="0.6"/>
<rect x="119" y="57" width="85.5" height="4.5" fill="#9cc9ea" fill-opacity="0.6"/>
<rect x="236" y="57" width="27" height="4.5" fill="#9cc9ea" fill-opacity="0.6"/>
<rect x="96.5" y="61.5" width="99" height="4.5" fill="#9cc9ea" fill-opacity="0.6"/>
<rect x="245" y="61.5" width="4.5" height="4.5" fill="#9cc9ea" fill-opacity="0.6"/>
<rect x="87.5" y="66" width="94.5" height="4.5" fill="#9cc9ea" fill-opacity="0.6"/>
<rect x="186.5" y="66" width="4.5" height="4.5" fill="#9cc9ea" fill-opacity="0.6"/>
<rect x="83" y="70.5" width="49.5" height="4.5" fill="#9cc9ea" fill-opacity="0.6"/>
<rect x="137" y="70.5" width="13.5" height="4.5" fill="#9cc9ea" fill-opacity="0.6"/>
<rect x="155" y="70.5" width="31.5" height="4.5" fill="#9cc9ea" fill-opacity="0.6"/>
<rect x="74" y="75" width="112.5" height="4.5" fill="#9cc9ea" fill-opacity="0.6"/>
<rect x="69.5" y="79.5" width="67.5" height="4.5" fill="#9cc9ea" fill-opacity="0.6"/>
<rect x="141.5" y="79.5" width="40.5" height="4.5" fill="#9cc9ea" fill-opacity="0.6"/>
<rect x="65" y="84" width="117" height="4.5" fill="#9cc9ea" fill-opacity="0.6"/>
<rect x="56" y="88.5" width="126" height="4.5" fill="#9cc9ea" fill-opacity="0.6"/>
<rect x="263" y="88.5" width="9" height="4.5" fill="#9cc9ea" fill-opacity="0.6"/>
<rect x="56" y="93" width="45" height="4.5" fill="#9cc9ea" fill-opacity="0.6"/>
<rect x="105.5" y="93" width="76.5" height="4.5" fill="#9cc9ea" fill-opacity="0.6"/>
<rect x="263" y="93" width="13.5" height="4.5" fill="#9cc9ea" fill-opacity="0.6"/>
<rect x="47" y="97.5" width="58.5" height="4.5" fill="#9cc9ea" fill-opacity="0.6"/>
<rect x="110" y="97.5" width="49.5" height="4.5" fill="#9cc9ea" fill-opacity="0.6"/>
<rect x="164" y="97.5" width="18" height="4.5" fill="#9cc9ea" fill-opacity="0.6"/>
<rect x="263" y="97.5" width="13.5" height="4.5" fill="#9cc9ea" fill-opacity="0.6"/>
<rect x="42.5" y="102" width="103.5" height="4.5" fill="#9cc9ea" fill-opacity="0.6"/>
<rect x="150.5" y="102" width="31.5" height="4.5" fill="#9cc9ea" fill-opacity="0.6"/>
<rect x="258.5" y="102" width="18" height="4.5" fill="#9cc9ea" fill-opacity="0.6"/>
<rect x="38" y="106.5" width="63" height="4.5" fill="#9cc9ea" fill-opacity="0.6"/>
<rect x="105.5" y="106.5" width="63" height="4.5" fill="#9cc9ea" fill-opacity="0.6"/>
<rect x="173" y="106.5" width="9" height="4.5" fill="#9cc9ea" fill-opacity="0.6"/>
<rect x="258.5" y="106.5" width="22.5" height="4.5" fill="#9cc9ea" fill-opacity="0.6"/>
<rect x="33.5" y="111" width="76.5" height="4.5" fill="#9cc9ea" fill-opacity="0.6"/>
<rect x="114.5" y="111" width="72" height="4.5" fill="#9cc9ea" fill-opacity="0.6"/>
<rect x="254" y="111" width="27" height="4.5" fill="#9cc9ea" fill-opacity="0.6"/>
<rect x="33.5" y="115.5" width="13.5" height="4.5" fill="#9cc9ea" fill-opacity="0.6"/>
<rect x="51.5" y="115.5" width="99" height="4.5" fill="#9cc9ea" fill-opacity="0.6"/>
<rect x="168.5" y="115.5" width="18" height="4.5" fill="#9cc9ea" fill-opacity="0.6"/>
<rect x="254" y="115.5" width="27" height="4.5" fill="#9cc9ea" fill-opacity="0.6"/>
<rect x="29" y="120" width="103.5" height="4.5" fill="#9cc9ea" fill-opacity="0.6"/>
<rect x="177.5" y="120" width="13.5" height="4.5" fill="#9cc9ea" fill-opacity="0.6"/>
<rect x="249.5" y="120" width="31.5" height="4.5" fill="#9cc9ea" fill-opacity="0.6"/>
<rect x="29" y="124.5" width="99" height="4.5" fill="#9cc9ea" fill-opacity="0.6"/>
<rect x="186.5" y="124.5" width="9" height="4.5" fill="#9cc9ea" fill-opacity="0.6"/>
<rect x="249.5" y="124.5" width="13.5" height="4.5" fill="#9cc9ea" fill-opacity="0.6"/>
<rect x="267.5" y="124.5" width="13.5" height="4.5" fill="#9cc9ea" fill-opacity="0.6"/>
<rect x="29" y="129" width="18" height="4.5" fill="#9cc9ea" fill-opacity="0.6"/>
<rect x="51.5" y="129" width="36" height="4.5" fill="#9cc9ea" fill-opacity="0.6"/>
<rect x="92" y="129" width="18" height="4.5" fill="#9cc9ea" fill-opacity="0.6"/>
<rect x="114.5" y="129" width="9" height="4.5" fill="#9cc9ea" fill-opacity="0.6"/>
<rect x="191" y="129" width="9" height="4.5" fill="#9cc9ea" fill-opacity="0.6"/>
<rect x="240.5" y="129" width="9" height="4.5" fill="#9cc9ea" fill-opacity="0.6"/>
<rect x="254" y="129" width="27" height="4.5" fill="#9cc9ea" fill-opacity="0.6"/>
<rect x="20" y="133.5" width="45" height="4.5" fill="#9cc9ea" fill-opacity="0.6"/>
<rect x="69.5" y="133.5" width="49.5" height="4.5" fill="#9cc9ea" fill-opacity="0.6"/>
<rect x="204.5" y="133.5" width="9" height="4.5" fill="#9cc9ea" fill-opacity="0.6"/>
<rect x="227" y="133.5" width="36" height="4.5" fill="#9cc9ea" fill-opacity="0.6"/>
<rect x="267.5" y="133.5" width="13.5" height="4.5" fill="#9cc9ea" fill-opacity="0.6"/>
<rect x="20" y="138" width="94.5" height="4.5" fill="#9cc9ea" fill-opacity="0.6"/>
<rect x="200" y="138" width="13.5" height="4.5" fill="#9cc9ea" fill-opacity="0.6"/>
<rect x="218" y="138" width="22.5" height="4.5" fill="#9cc9ea" fill-opacity="0.6"/>
<rect x="245" y="138" width="36" height="4.5" fill="#9cc9ea" fill-opacity="0.6"/>
<rect x="20" y="142.5" width="94.5" height="4.5" fill="#9cc9ea" fill-opacity="0.6"/>
<rect x="204.5" y="142.5" width="76.5" height="4.5" fill="#9cc9ea" fill-opacity="0.6"/>
<rect x="20" y="147" width="9" height="4.5" fill="#9cc9ea" fill-opacity="0.6"/>
<rect x="33.5" y="147" width="49.5" height="4.5" fill="#9cc9ea" fill-opacity="0.6"/>
<rect x="87.5" y="147" width="22.5" height="4.5" fill="#9cc9ea" fill-opacity="0.6"/>
<rect x="204.5" y="147" width="72" height="4.5" fill="#9cc9ea" fill-opacity="0.6"/>
<rect x="20" y="151.5" width="27" height="4.5" fill="#9cc9ea" fill-opacity="0.6"/>
<rect x="51.5" y="151.5" width="58.5" height="4.5" fill="#9cc9ea" fill-opacity="0.6"/>
<rect x="204.5" y="151.5" width="49.5" height="4.5" fill="#9cc9ea" fill-opacity="0.6"/>
<rect x="258.5" y="151.5" width="18" height="4.5" fill="#9cc9ea" fill-opacity="0.6"/>
<rect x="20" y="156" width="36" height="4.5" fill="#9cc9ea" fill-opacity="0.6"/>
<rect x="60.5" y="156" width="45" height="4.5" fill="#9cc9ea" fill-opacity="0.6"/>
<rect x="209" y="156" width="67.5" height="4.5" fill="#9cc9ea" fill-opacity="0.6"/>
<rect x="20" y="160.5" width="18" height="4.5" fill="#9cc9ea" fill-opacity="0.6"/>
<rect x="42.5" y="160.5" width="63" height="4.5" fill="#9cc9ea" fill-opacity="0.6"/>
<rect x="209" y="160.5" width="54" height="4.5" fill="#9cc9ea" fill-opacity="0.6"/>
<rect x="267.5" y="160.5" width="4.5" height="4.5" fill="#9cc9ea" fill-opacity="0.6"/>
<rect x="20" y="165" width="18" height="4.5" fill="#9cc9ea" fill-opacity="0.6"/>
<rect x="42.5" y="165" width="45" height="4.5" fill="#9cc9ea" fill-opacity="0.6"/>
<rect x="92" y="165" width="4.5" height="4.5" fill="#9cc9ea" fill-opacity="0.6"/>
<rect x="101" y="165" width="4.5" height="4.5" fill="#9cc9ea" fill-opacity="0.6"/>
<rect x="209" y="165" width="63" height="4.5" fill="#9cc9ea" fill-opacity="0.6"/>
<rect x="20" y="169.5" width="72" height="4.5" fill="#9cc9ea" fill-opacity="0.6"/>
<rect x="101" y="169.5" width="4.5" height="4.5" fill="#9cc9ea" fill-opacity="0.6"/>
<rect x="209" y="169.5" width="58.5" height="4.5" fill="#9cc9ea" fill-opacity="0.6"/>
<rect x="20" y="174" width="36" height="4.5" fill="#9cc9ea" fill-opacity="0.6"/>
<rect x="60.5" y="174" width="4.5" height="4.5" fill="#9cc9ea" fill-opacity="0.6"/>
<rect x="69.5" y="174" width="40.5" height="4.5" fill="#9cc9ea" fill-opacity="0.6"/>
<rect x="209" y="174" width="54" height="4.5" fill="#9cc9ea" fill-opacity="0.6"/>
<rect x="20" y="178.5" width="13.5" height="4.5" fill="#9cc9ea" fill-opacity="0.6"/>
<rect x="38" y="178.5" width="13.5" height="4.5" fill="#9cc9ea" fill-opacity="0.6"/>
<rect x="56" y="178.5" width="22.5" height="4.5" fill="#9cc9ea" fill-opacity="0.6"/>
<rect x="204.5" y="178.5" width="40.5" height="4.5" fill="#9cc9ea" fill-opacity="0.6"/>
<rect x="249.5" y="178.5" width="9" height="4.5" fill="#9cc9ea" fill-opacity="0.6"/>
<rect x="20" y="183" width="54" height="4.5" fill="#9cc9ea" fill-opacity="0.6"/>
<rect x="204.5" y="183" width="54" height="4.5" fill="#9cc9ea" fill-opacity="0.6"/>
<rect x="20" y="187.5" width="49.5" height="4.5" fill="#9cc9ea" fill-opacity="0.6"/>
<rect x="209" y="187.5" width="45" height="4.5" fill="#9cc9ea" fill-opacity="0.6"/>
<rect x="20" y="192" width="45" height="4.5" fill="#9cc9ea" fill-opacity="0.6"/>
<rect x="200" y="192" width="9" height="4.5" fill="#9cc9ea" fill-opacity="0.6"/>
<rect x="213.5" y="192" width="36" height="4.5" fill="#9cc9ea" fill-opacity="0.6"/>
<rect x="20" y="196.5" width="40.5" height="4.5" fill="#9cc9ea" fill-opacity="0.6"/>
<rect x="195.5" y="196.5" width="49.5" height="4.5" fill="#9cc9ea" fill-opacity="0.6"/>
<rect x="20" y="201" width="40.5" height="4.5" fill="#9cc9ea" fill-opacity="0.6"/>
<rect x="191" y="201" width="54" height="4.5" fill="#9cc9ea" fill-opacity="0.6"/>
<rect x="29" y="205.5" width="31.5" height="4.5" fill="#9cc9ea" fill-opacity="0.6"/>
<rect x="186.5" y="205.5" width="54" height="4.5" fill="#9cc9ea" fill-opacity="0.6"/>
<rect x="20" y="210" width="40.5" height="4.5" fill="#9cc9ea" fill-opacity="0.6"/>
<rect x="128" y="210" width="9" height="4.5" fill="#9cc9ea" fill-opacity="0.6"/>
<rect x="182" y="210" width="36" height="4.5" fill="#9cc9ea" fill-opacity="0.6"/>
<rect x="222.5" y="210" width="13.5" height="4.5" fill="#9cc9ea" fill-opacity="0.6"/>
<rect x="20" y="214.5" width="40.5" height="4.5" fill="#9cc9ea" fill-opacity="0.6"/>
<rect x="128" y="214.5" width="18" height="4.5" fill="#9cc9ea" fill-opacity="0.6"/>
<rect x="168.5" y="214.5" width="31.5" height="4.5" fill="#9cc9ea" fill-opacity="0.6"/>
<rect x="204.5" y="214.5" width="4.5" height="4.5" fill="#9cc9ea" fill-opacity="0.6"/>
<rect x="213.5" y="214.5" width="18" height="4.5" fill="#9cc9ea" fill-opacity="0.6"/>
<rect x="20" y="219" width="31.5" height="4.5" fill="#9cc9ea" fill-opacity="0.6"/>
<rect x="56" y="219" width="4.5" height="4.5" fill="#9cc9ea" fill-opacity="0.6"/>
<rect x="128" y="219" width="103.5" height="4.5" fill="#9cc9ea" fill-opacity="0.6"/>
<rect x="20" y="223.5" width="40.5" height="4.5" fill="#9cc9ea" fill-opacity="0.6"/>
<rect x="128" y="223.5" width="36" height="4.5" fill="#9cc9ea" fill-opacity="0.6"/>
<rect x="168.5" y="223.5" width="27" height="4.5" fill="#9cc9ea" fill-opacity="0.6"/>
<rect x="200" y="223.5" width="27" height="4.5" fill="#9cc9ea" fill-opacity="0.6"/>
<rect x="20" y="228" width="45" height="4.5" fill="#9cc9ea" fill-opacity="0.6"/>
<rect x="123.5" y="228" width="76.5" height="4.5" fill="#9cc9ea" fill-opacity="0.6"/>
<rect x="204.5" y="228" width="18" height="4.5" fill="#9cc9ea" fill-opacity="0.6"/>
<rect x="20" y="232.5" width="49.5" height="4.5" fill="#9cc9ea" fill-opacity="0.6"/>
<rect x="119" y="232.5" width="99" height="4.5" fill="#9cc9ea" fill-opacity="0.6"/>
<rect x="20" y="237" width="54" height="4.5" fill="#9cc9ea" fill-opacity="0.6"/>
<rect x="114.5" y="237" width="99" height="4.5" fill="#9cc9ea" fill-opacity="0.6"/>
<rect x="20" y="241.5" width="4.5" height="4.5" fill="#9cc9ea" fill-opacity="0.6"/>
<rect x="29" y="241.5" width="9" height="4.5" fill="#9cc9ea" fill-opacity="0.6"/>
<rect x="47" y="241.5" width="27" height="4.5" fill="#9cc9ea" fill-opacity="0.6"/>
<rect x="110" y="241.5" width="49.5" height="4.5" fill="#9cc9ea" fill-opacity="0.6"/>
<rect x="164" y="241.5" width="9" height="4.5" fill="#9cc9ea" fill-opacity="0.6"/>
<rect x="177.5" y="241.5" width="36" height="4.5" fill="#9cc9ea" fill-opacity="0.6"/>
<rect x="20" y="246" width="189" height="4.5" fill="#9cc9ea" fill-opacity="0.6"/>
<rect x="20" y="250.5" width="184.5" height="4.5" fill="#9cc9ea" fill-opacity="0.6"/>
<rect x="20" y="255" width="117" height="4.5" fill="#9cc9ea" fill-opacity="0.6"/>
<rect x="141.5" y="255" width="58.5" height="4.5" fill="#9cc9ea" fill-opacity="0.6"/>
<rect x="20" y="259.5" width="175.5" height="4.5" fill="#9cc9ea" fill-opacity="0.6"/>
<rect x="20" y="264" width="148.5" height="4.5" fill="#9cc9ea" fill-opacity="0.6"/>
<rect x="173" y="264" width="22.5" height="4.5" fill="#9cc9ea" fill-opacity="0.6"/>
<rect x="20" y="268.5" width="99" height="4.5" fill="#9cc9ea" fill-opacity="0.6"/>
<rect x="123.5" y="268.5" width="67.5" height="4.5" fill="#9cc9ea" fill-opacity="0.6"/>
<rect x="20" y="273" width="139.5" height="4.5" fill="#9cc9ea" fill-opacity="0.6"/>
<rect x="164" y="273" width="18" height="4.5" fill="#9cc9ea" fill-opacity="0.6"/>
<rect x="20" y="277.5" width="22.5" height="4.5" fill="#9cc9ea" fill-opacity="0.6"/>
<rect x="47" y="277.5" width="130.5" height="4.5" fill="#9cc9ea" fill-opacity="0.6"/>
<rect x="20" y="282" width="22.5" height="4.5" fill="#9cc9ea" fill-opacity="0.6"/>
<rect x="47" y="282" width="27" height="4.5" fill="#9cc9ea" fill-opacity="0.6"/>
<rect x="78.5" y="282" width="4.5" height="4.5" fill="#9cc9ea" fill-opacity="0.6"/>
<rect x="87.5" y="282" width="81" height="4.5" fill="#9cc9ea" fill-opacity="0.6"/>
<rect x="24.5" y="286.5" width="58.5" height="4.5" fill="#9cc9ea" fill-opacity="0.6"/>
<rect x="87.5" y="286.5" width="76.5" height="4.5" fill="#9cc9ea" fill-opacity="0.6"/>
<rect x="20" y="291" width="135" height="4.5" fill="#9cc9ea" fill-opacity="0.6"/>
<rect x="20" y="295.5" width="31.5" height="4.5" fill="#9cc9ea" fill-opacity="0.6"/>
<rect x="56" y="295.5" width="72" height="4.5" fill="#9cc9ea" fill-opacity="0.6"/>
<rect x="132.5" y="295.5" width="18" height="4.5" fill="#9cc9ea" fill-opacity="0.6"/>
<rect x="164" y="34.5" width="4.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="164" y="39" width="4.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="186.5" y="39" width="4.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="218" y="39" width="4.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="195.5" y="43.5" width="4.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="245" y="43.5" width="4.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="267.5" y="43.5" width="4.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="240.5" y="48" width="4.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="69.5" y="52.5" width="4.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="191" y="52.5" width="4.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="258.5" y="52.5" width="4.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="56" y="57" width="4.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="114.5" y="57" width="4.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="204.5" y="57" width="31.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="92" y="61.5" width="4.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="195.5" y="61.5" width="13.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="213.5" y="61.5" width="13.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="231.5" y="61.5" width="13.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="56" y="66" width="4.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="182" y="66" width="4.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="191" y="66" width="9" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="204.5" y="66" width="31.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="240.5" y="66" width="13.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="132.5" y="70.5" width="4.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="150.5" y="70.5" width="4.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="186.5" y="70.5" width="9" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="200" y="70.5" width="40.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="245" y="70.5" width="9" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="186.5" y="75" width="4.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="195.5" y="75" width="49.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="249.5" y="75" width="4.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="281" y="75" width="4.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="33.5" y="79.5" width="4.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="137" y="79.5" width="4.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="182" y="79.5" width="76.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="47" y="84" width="4.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="182" y="84" width="4.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="191" y="84" width="58.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="254" y="84" width="4.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="182" y="88.5" width="4.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="191" y="88.5" width="18" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="231.5" y="88.5" width="18" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="254" y="88.5" width="4.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="38" y="93" width="4.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="51.5" y="93" width="4.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="101" y="93" width="4.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="182" y="93" width="27" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="231.5" y="93" width="27" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="105.5" y="97.5" width="4.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="159.5" y="97.5" width="4.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="182" y="97.5" width="4.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="191" y="97.5" width="18" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="231.5" y="97.5" width="18" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="254" y="97.5" width="9" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="146" y="102" width="4.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="182" y="102" width="27" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="231.5" y="102" width="27" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="101" y="106.5" width="4.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="168.5" y="106.5" width="4.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="182" y="106.5" width="31.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="231.5" y="106.5" width="27" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="110" y="111" width="4.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="186.5" y="111" width="67.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="47" y="115.5" width="4.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="150.5" y="115.5" width="18" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="186.5" y="115.5" width="9" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="200" y="115.5" width="40.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="245" y="115.5" width="9" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="132.5" y="120" width="45" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="191" y="120" width="9" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="204.5" y="120" width="45" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="128" y="124.5" width="18" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="155" y="124.5" width="4.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="168.5" y="124.5" width="18" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="195.5" y="124.5" width="18" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="227" y="124.5" width="22.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="263" y="124.5" width="4.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="24.5" y="129" width="4.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="47" y="129" width="4.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="87.5" y="129" width="4.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="110" y="129" width="4.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="123.5" y="129" width="67.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="200" y="129" width="40.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="249.5" y="129" width="4.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="65" y="133.5" width="4.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="119" y="133.5" width="9" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="132.5" y="133.5" width="49.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="186.5" y="133.5" width="9" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="200" y="133.5" width="4.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="213.5" y="133.5" width="13.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="263" y="133.5" width="4.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="114.5" y="138" width="9" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="128" y="138" width="58.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="191" y="138" width="9" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="213.5" y="138" width="4.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="240.5" y="138" width="4.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="281" y="138" width="4.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="114.5" y="142.5" width="90" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="29" y="147" width="4.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="83" y="147" width="4.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="110" y="147" width="45" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="173" y="147" width="18" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="195.5" y="147" width="9" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="47" y="151.5" width="4.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="110" y="151.5" width="36" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="177.5" y="151.5" width="27" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="254" y="151.5" width="4.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="56" y="156" width="4.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="105.5" y="156" width="9" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="119" y="156" width="27" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="182" y="156" width="13.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="200" y="156" width="9" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="285.5" y="156" width="4.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="38" y="160.5" width="4.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="105.5" y="160.5" width="9" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="119" y="160.5" width="22.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="182" y="160.5" width="13.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="200" y="160.5" width="9" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="263" y="160.5" width="4.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="38" y="165" width="4.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="87.5" y="165" width="4.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="96.5" y="165" width="4.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="105.5" y="165" width="36" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="182" y="165" width="13.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="200" y="165" width="9" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="92" y="169.5" width="9" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="105.5" y="169.5" width="9" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="119" y="169.5" width="22.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="182" y="169.5" width="13.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="200" y="169.5" width="9" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="56" y="174" width="4.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="65" y="174" width="4.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="110" y="174" width="4.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="119" y="174" width="22.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="182" y="174" width="13.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="200" y="174" width="9" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="263" y="174" width="4.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="33.5" y="178.5" width="4.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="51.5" y="178.5" width="4.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="78.5" y="178.5" width="67.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="177.5" y="178.5" width="27" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="245" y="178.5" width="4.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="74" y="183" width="13.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="92" y="183" width="58.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="173" y="183" width="18" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="195.5" y="183" width="9" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="69.5" y="187.5" width="45" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="123.5" y="187.5" width="85.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="65" y="192" width="54" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="128" y="192" width="58.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="191" y="192" width="9" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="209" y="192" width="4.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="60.5" y="196.5" width="67.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="132.5" y="196.5" width="49.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="186.5" y="196.5" width="9" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="60.5" y="201" width="31.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="101" y="201" width="18" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="123.5" y="201" width="67.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="20" y="205.5" width="9" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="60.5" y="205.5" width="27" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="105.5" y="205.5" width="13.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="123.5" y="205.5" width="22.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="150.5" y="205.5" width="4.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="168.5" y="205.5" width="18" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="267.5" y="205.5" width="4.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="60.5" y="210" width="27" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="105.5" y="210" width="22.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="137" y="210" width="45" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="218" y="210" width="4.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="60.5" y="214.5" width="27" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="105.5" y="214.5" width="13.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="123.5" y="214.5" width="4.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="146" y="214.5" width="22.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="200" y="214.5" width="4.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="209" y="214.5" width="4.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="51.5" y="219" width="4.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="60.5" y="219" width="31.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="101" y="219" width="27" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="240.5" y="219" width="4.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="60.5" y="223.5" width="67.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="164" y="223.5" width="4.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="195.5" y="223.5" width="4.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="65" y="228" width="58.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="200" y="228" width="4.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="69.5" y="232.5" width="49.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="218" y="232.5" width="4.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="245" y="232.5" width="4.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="74" y="237" width="13.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="92" y="237" width="22.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="24.5" y="241.5" width="4.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="38" y="241.5" width="9" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="74" y="241.5" width="36" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="159.5" y="241.5" width="4.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="173" y="241.5" width="4.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="218" y="246" width="4.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="276.5" y="246" width="4.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="137" y="255" width="4.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="249.5" y="255" width="4.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="168.5" y="264" width="4.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="272" y="264" width="4.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="119" y="268.5" width="4.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="159.5" y="273" width="4.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="272" y="273" width="4.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="281" y="273" width="4.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="42.5" y="277.5" width="4.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="191" y="277.5" width="4.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="213.5" y="277.5" width="4.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="42.5" y="282" width="4.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="74" y="282" width="4.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="83" y="282" width="4.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="177.5" y="282" width="4.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="213.5" y="282" width="4.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="236" y="282" width="4.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="20" y="286.5" width="4.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="83" y="286.5" width="4.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="51.5" y="295.5" width="4.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="128" y="295.5" width="4.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="159.5" y="295.5" width="4.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="173" y="295.5" width="4.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="285.5" y="295.5" width="4.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<polyline points="35.75,275.25 35.75,270.75 35.75,266.25 35.75,261.75 35.75,257.25 35.75,252.75 35.75,248.25 35.75,243.75 35.75,239.25 35.75,234.75 35.75,230.25 35.75,225.75 35.75,221.25 40.25,216.75 44.75,212.25 49.25,207.75 53.75,203.25 58.25,198.75 58.25,194.25 62.75,189.75 67.25,185.25 71.75,180.75 76.25,176.25 80.75,171.75 85.25,167.25 89.75,162.75 94.25,158.25 98.75,153.75 103.25,149.25 107.75,144.75 112.25,140.25 112.25,135.75 116.75,131.25 121.25,126.75 125.75,122.25 130.25,122.25 134.75,117.75 139.25,113.25 143.75,113.25 148.25,108.75 152.75,104.25 157.25,99.75 161.75,95.25 166.25,90.75 170.75,86.25 175.25,81.75 179.75,77.25 184.25,72.75 188.75,68.25 193.25,63.75 197.75,59.25 202.25,54.75 206.75,54.75 211.25,50.25 215.75,50.25 220.25,50.25 224.75,50.25 229.25,50.25 233.75,54.75 238.25,54.75 242.75,54.75 247.25,50.25 251.75,50.25 256.25,50.25 260.75,50.25 265.25,50.25 269.75,50.25 274.25,50.25" fill="none" stroke="#eea66f" stroke-width="2.5"/>
<rect x="320" y="30" width="270" height="270" fill="none" stroke="currentColor"/>
<rect x="572" y="52.5" width="4.5" height="4.5" fill="#9cc9ea" fill-opacity="0.6"/>
<rect x="572" y="57" width="4.5" height="4.5" fill="#9cc9ea" fill-opacity="0.6"/>
<rect x="572" y="61.5" width="4.5" height="4.5" fill="#9cc9ea" fill-opacity="0.6"/>
<rect x="572" y="66" width="4.5" height="4.5" fill="#9cc9ea" fill-opacity="0.6"/>
<rect x="572" y="70.5" width="4.5" height="4.5" fill="#9cc9ea" fill-opacity="0.6"/>
<rect x="572" y="75" width="4.5" height="4.5" fill="#9cc9ea" fill-opacity="0.6"/>
<rect x="572" y="79.5" width="4.5" height="4.5" fill="#9cc9ea" fill-opacity="0.6"/>
<rect x="572" y="84" width="4.5" height="4.5" fill="#9cc9ea" fill-opacity="0.6"/>
<rect x="572" y="88.5" width="4.5" height="4.5" fill="#9cc9ea" fill-opacity="0.6"/>
<rect x="572" y="93" width="4.5" height="4.5" fill="#9cc9ea" fill-opacity="0.6"/>
<rect x="572" y="97.5" width="4.5" height="4.5" fill="#9cc9ea" fill-opacity="0.6"/>
<rect x="572" y="102" width="4.5" height="4.5" fill="#9cc9ea" fill-opacity="0.6"/>
<rect x="572" y="106.5" width="4.5" height="4.5" fill="#9cc9ea" fill-opacity="0.6"/>
<rect x="572" y="111" width="4.5" height="4.5" fill="#9cc9ea" fill-opacity="0.6"/>
<rect x="572" y="115.5" width="4.5" height="4.5" fill="#9cc9ea" fill-opacity="0.6"/>
<rect x="572" y="120" width="4.5" height="4.5" fill="#9cc9ea" fill-opacity="0.6"/>
<rect x="567.5" y="124.5" width="4.5" height="4.5" fill="#9cc9ea" fill-opacity="0.6"/>
<rect x="563" y="129" width="4.5" height="4.5" fill="#9cc9ea" fill-opacity="0.6"/>
<rect x="558.5" y="133.5" width="4.5" height="4.5" fill="#9cc9ea" fill-opacity="0.6"/>
<rect x="558.5" y="138" width="4.5" height="4.5" fill="#9cc9ea" fill-opacity="0.6"/>
<rect x="554" y="142.5" width="4.5" height="4.5" fill="#9cc9ea" fill-opacity="0.6"/>
<rect x="549.5" y="147" width="4.5" height="4.5" fill="#9cc9ea" fill-opacity="0.6"/>
<rect x="545" y="151.5" width="4.5" height="4.5" fill="#9cc9ea" fill-opacity="0.6"/>
<rect x="540.5" y="156" width="4.5" height="4.5" fill="#9cc9ea" fill-opacity="0.6"/>
<rect x="536" y="160.5" width="4.5" height="4.5" fill="#9cc9ea" fill-opacity="0.6"/>
<rect x="531.5" y="165" width="4.5" height="4.5" fill="#9cc9ea" fill-opacity="0.6"/>
<rect x="527" y="169.5" width="4.5" height="4.5" fill="#9cc9ea" fill-opacity="0.6"/>
<rect x="522.5" y="174" width="4.5" height="4.5" fill="#9cc9ea" fill-opacity="0.6"/>
<rect x="518" y="178.5" width="4.5" height="4.5" fill="#9cc9ea" fill-opacity="0.6"/>
<rect x="513.5" y="183" width="4.5" height="4.5" fill="#9cc9ea" fill-opacity="0.6"/>
<rect x="509" y="187.5" width="4.5" height="4.5" fill="#9cc9ea" fill-opacity="0.6"/>
<rect x="500" y="192" width="9" height="4.5" fill="#9cc9ea" fill-opacity="0.6"/>
<rect x="495.5" y="196.5" width="4.5" height="4.5" fill="#9cc9ea" fill-opacity="0.6"/>
<rect x="491" y="201" width="4.5" height="4.5" fill="#9cc9ea" fill-opacity="0.6"/>
<rect x="486.5" y="205.5" width="4.5" height="4.5" fill="#9cc9ea" fill-opacity="0.6"/>
<rect x="428" y="210" width="9" height="4.5" fill="#9cc9ea" fill-opacity="0.6"/>
<rect x="482" y="210" width="4.5" height="4.5" fill="#9cc9ea" fill-opacity="0.6"/>
<rect x="428" y="214.5" width="18" height="4.5" fill="#9cc9ea" fill-opacity="0.6"/>
<rect x="468.5" y="214.5" width="13.5" height="4.5" fill="#9cc9ea" fill-opacity="0.6"/>
<rect x="428" y="219" width="49.5" height="4.5" fill="#9cc9ea" fill-opacity="0.6"/>
<rect x="428" y="223.5" width="36" height="4.5" fill="#9cc9ea" fill-opacity="0.6"/>
<rect x="360.5" y="228" width="4.5" height="4.5" fill="#9cc9ea" fill-opacity="0.6"/>
<rect x="423.5" y="228" width="27" height="4.5" fill="#9cc9ea" fill-opacity="0.6"/>
<rect x="356" y="232.5" width="13.5" height="4.5" fill="#9cc9ea" fill-opacity="0.6"/>
<rect x="419" y="232.5" width="18" height="4.5" fill="#9cc9ea" fill-opacity="0.6"/>
<rect x="356" y="237" width="18" height="4.5" fill="#9cc9ea" fill-opacity="0.6"/>
<rect x="414.5" y="237" width="18" height="4.5" fill="#9cc9ea" fill-opacity="0.6"/>
<rect x="356" y="241.5" width="18" height="4.5" fill="#9cc9ea" fill-opacity="0.6"/>
<rect x="410" y="241.5" width="18" height="4.5" fill="#9cc9ea" fill-opacity="0.6"/>
<rect x="356" y="246" width="58.5" height="4.5" fill="#9cc9ea" fill-opacity="0.6"/>
<rect x="356" y="250.5" width="49.5" height="4.5" fill="#9cc9ea" fill-opacity="0.6"/>
<rect x="351.5" y="255" width="36" height="4.5" fill="#9cc9ea" fill-opacity="0.6"/>
<rect x="347" y="259.5" width="4.5" height="4.5" fill="#9cc9ea" fill-opacity="0.6"/>
<rect x="360.5" y="259.5" width="9" height="4.5" fill="#9cc9ea" fill-opacity="0.6"/>
<rect x="342.5" y="264" width="4.5" height="4.5" fill="#9cc9ea" fill-opacity="0.6"/>
<rect x="338" y="268.5" width="4.5" height="4.5" fill="#9cc9ea" fill-opacity="0.6"/>
<rect x="333.5" y="273" width="4.5" height="4.5" fill="#9cc9ea" fill-opacity="0.6"/>
<rect x="464" y="34.5" width="4.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="464" y="39" width="4.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="486.5" y="39" width="4.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="518" y="39" width="4.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="495.5" y="43.5" width="4.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="545" y="43.5" width="4.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="567.5" y="43.5" width="4.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="540.5" y="48" width="4.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="369.5" y="52.5" width="4.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="491" y="52.5" width="4.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="558.5" y="52.5" width="4.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="356" y="57" width="4.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="414.5" y="57" width="4.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="504.5" y="57" width="31.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="392" y="61.5" width="4.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="495.5" y="61.5" width="13.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="513.5" y="61.5" width="13.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="531.5" y="61.5" width="13.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="356" y="66" width="4.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="482" y="66" width="4.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="491" y="66" width="9" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="504.5" y="66" width="31.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="540.5" y="66" width="13.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="432.5" y="70.5" width="4.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="450.5" y="70.5" width="4.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="486.5" y="70.5" width="9" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="500" y="70.5" width="40.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="545" y="70.5" width="9" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="486.5" y="75" width="4.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="495.5" y="75" width="49.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="549.5" y="75" width="4.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="581" y="75" width="4.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="333.5" y="79.5" width="4.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="437" y="79.5" width="4.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="482" y="79.5" width="76.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="347" y="84" width="4.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="482" y="84" width="4.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="491" y="84" width="58.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="554" y="84" width="4.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="482" y="88.5" width="4.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="491" y="88.5" width="18" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="531.5" y="88.5" width="18" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="554" y="88.5" width="4.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="338" y="93" width="4.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="351.5" y="93" width="4.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="401" y="93" width="4.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="482" y="93" width="27" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="531.5" y="93" width="27" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="405.5" y="97.5" width="4.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="459.5" y="97.5" width="4.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="482" y="97.5" width="4.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="491" y="97.5" width="18" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="531.5" y="97.5" width="18" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="554" y="97.5" width="9" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="446" y="102" width="4.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="482" y="102" width="27" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="531.5" y="102" width="27" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="401" y="106.5" width="4.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="468.5" y="106.5" width="4.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="482" y="106.5" width="31.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="531.5" y="106.5" width="27" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="410" y="111" width="4.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="486.5" y="111" width="67.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="347" y="115.5" width="4.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="450.5" y="115.5" width="18" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="486.5" y="115.5" width="9" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="500" y="115.5" width="40.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="545" y="115.5" width="9" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="432.5" y="120" width="45" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="491" y="120" width="9" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="504.5" y="120" width="45" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="428" y="124.5" width="18" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="455" y="124.5" width="4.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="468.5" y="124.5" width="18" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="495.5" y="124.5" width="18" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="527" y="124.5" width="22.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="563" y="124.5" width="4.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="324.5" y="129" width="4.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="347" y="129" width="4.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="387.5" y="129" width="4.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="410" y="129" width="4.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="423.5" y="129" width="67.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="500" y="129" width="40.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="549.5" y="129" width="4.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="365" y="133.5" width="4.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="419" y="133.5" width="9" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="432.5" y="133.5" width="49.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="486.5" y="133.5" width="9" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="500" y="133.5" width="4.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="513.5" y="133.5" width="13.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="563" y="133.5" width="4.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="414.5" y="138" width="9" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="428" y="138" width="58.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="491" y="138" width="9" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="513.5" y="138" width="4.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="540.5" y="138" width="4.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="581" y="138" width="4.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="414.5" y="142.5" width="90" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="329" y="147" width="4.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="383" y="147" width="4.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="410" y="147" width="45" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="473" y="147" width="18" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="495.5" y="147" width="9" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="347" y="151.5" width="4.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="410" y="151.5" width="36" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="477.5" y="151.5" width="27" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="554" y="151.5" width="4.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="356" y="156" width="4.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="405.5" y="156" width="9" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="419" y="156" width="27" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="482" y="156" width="13.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="500" y="156" width="9" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="585.5" y="156" width="4.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="338" y="160.5" width="4.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="405.5" y="160.5" width="9" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="419" y="160.5" width="22.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="482" y="160.5" width="13.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="500" y="160.5" width="9" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="563" y="160.5" width="4.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="338" y="165" width="4.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="387.5" y="165" width="4.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="396.5" y="165" width="4.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="405.5" y="165" width="36" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="482" y="165" width="13.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="500" y="165" width="9" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="392" y="169.5" width="9" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="405.5" y="169.5" width="9" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="419" y="169.5" width="22.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="482" y="169.5" width="13.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="500" y="169.5" width="9" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="356" y="174" width="4.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="365" y="174" width="4.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="410" y="174" width="4.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="419" y="174" width="22.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="482" y="174" width="13.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="500" y="174" width="9" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="563" y="174" width="4.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="333.5" y="178.5" width="4.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="351.5" y="178.5" width="4.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="378.5" y="178.5" width="67.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="477.5" y="178.5" width="27" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="545" y="178.5" width="4.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="374" y="183" width="13.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="392" y="183" width="58.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="473" y="183" width="18" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="495.5" y="183" width="9" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="369.5" y="187.5" width="45" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="423.5" y="187.5" width="85.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="365" y="192" width="54" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="428" y="192" width="58.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="491" y="192" width="9" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="509" y="192" width="4.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="360.5" y="196.5" width="67.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="432.5" y="196.5" width="49.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="486.5" y="196.5" width="9" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="360.5" y="201" width="31.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="401" y="201" width="18" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="423.5" y="201" width="67.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="320" y="205.5" width="9" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="360.5" y="205.5" width="27" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="405.5" y="205.5" width="13.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="423.5" y="205.5" width="22.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="450.5" y="205.5" width="4.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="468.5" y="205.5" width="18" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="567.5" y="205.5" width="4.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="360.5" y="210" width="27" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="405.5" y="210" width="22.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="437" y="210" width="45" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="518" y="210" width="4.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="360.5" y="214.5" width="27" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="405.5" y="214.5" width="13.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="423.5" y="214.5" width="4.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="446" y="214.5" width="22.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="500" y="214.5" width="4.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="509" y="214.5" width="4.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="351.5" y="219" width="4.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="360.5" y="219" width="31.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="401" y="219" width="27" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="540.5" y="219" width="4.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="360.5" y="223.5" width="67.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="464" y="223.5" width="4.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="495.5" y="223.5" width="4.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="365" y="228" width="58.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="500" y="228" width="4.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="369.5" y="232.5" width="49.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="518" y="232.5" width="4.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="545" y="232.5" width="4.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="374" y="237" width="13.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="392" y="237" width="22.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="324.5" y="241.5" width="4.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="338" y="241.5" width="9" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="374" y="241.5" width="36" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="459.5" y="241.5" width="4.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="473" y="241.5" width="4.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="518" y="246" width="4.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="576.5" y="246" width="4.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="437" y="255" width="4.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="549.5" y="255" width="4.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="468.5" y="264" width="4.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="572" y="264" width="4.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="419" y="268.5" width="4.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="459.5" y="273" width="4.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="572" y="273" width="4.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="581" y="273" width="4.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="342.5" y="277.5" width="4.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="491" y="277.5" width="4.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="513.5" y="277.5" width="4.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="342.5" y="282" width="4.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="374" y="282" width="4.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="383" y="282" width="4.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="477.5" y="282" width="4.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="513.5" y="282" width="4.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="536" y="282" width="4.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="320" y="286.5" width="4.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="383" y="286.5" width="4.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="351.5" y="295.5" width="4.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="428" y="295.5" width="4.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="459.5" y="295.5" width="4.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="473" y="295.5" width="4.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<rect x="585.5" y="295.5" width="4.5" height="4.5" fill="currentColor" fill-opacity="0.55"/>
<polyline points="335.75,275.25 340.25,270.75 344.75,266.25 349.25,261.75 353.75,257.25 358.25,252.75 362.75,248.25 367.25,248.25 371.75,252.75 376.25,252.75 380.75,252.75 385.25,252.75 389.75,252.75 394.25,252.75 398.75,248.25 403.25,248.25 407.75,248.25 412.25,243.75 416.75,239.25 421.25,234.75 425.75,230.25 430.25,225.75 434.75,221.25 439.25,221.25 443.75,221.25 448.25,221.25 452.75,221.25 457.25,221.25 461.75,221.25 466.25,221.25 470.75,221.25 475.25,221.25 479.75,216.75 484.25,212.25 488.75,207.75 493.25,203.25 497.75,198.75 502.25,194.25 506.75,194.25 511.25,189.75 515.75,185.25 520.25,180.75 524.75,176.25 529.25,171.75 533.75,167.25 538.25,162.75 542.75,158.25 547.25,153.75 551.75,149.25 556.25,144.75 560.75,140.25 560.75,135.75 565.25,131.25 569.75,126.75 574.25,122.25 574.25,117.75 574.25,113.25 574.25,108.75 574.25,104.25 574.25,99.75 574.25,95.25 574.25,90.75 574.25,86.25 574.25,81.75 574.25,77.25 574.25,72.75 574.25,68.25 574.25,63.75 574.25,59.25 574.25,54.75 574.25,50.25" fill="none" stroke="#eea66f" stroke-width="2.5"/>
<text x="300" y="332" font-size="12" text-anchor="middle" fill="currentColor">dark: too steep or rock; blue: expanded; orange: route from S (bottom left) to G (top right)</text>
</svg>
<figcaption>Figure 4.3. Planning on the synthetic terrain. A\* (left) proves its route optimal but expands two thirds
of the free cells, because the octile heuristic ignores slopes; weighted A\* (right) expands 13 times fewer cells
for a route 11 percent costlier.</figcaption>
</figure>

What the numbers say:

- **Dijkstra** (A\* with $h = 0$) expanded 2639 cells, almost every reachable one, and found the optimal cost 98.8.
- **A\*** found the same cost, as Theorem 4.5 guarantees, with 1739 expansions. The saving is real but modest,
  because the heuristic is weak here: at the start it estimates 73.7 against a true 98.8, three quarters of the
  cost, and the missing quarter is exactly the slope penalty it cannot see. The quality of a heuristic, not the
  algorithm, decides how much A\* saves.
- **Weighted A\*** with $w = 2$ expanded only 133 cells, for a route of cost 109.4, 11 percent worse than optimal and
  well inside the guarantee $2 \times 98.8$.
- **Greedy best-first** expanded 73 cells and drove an expensive route (cost 113.1) over steeper ground.

The text map (every second row) shows the A\* route swinging west and north of the straight line, around the
large central crater and north of the crater near the goal. The route hugs the edges of the obstacles: shortest paths on grids like to graze obstacles, which is one reason
real planners inflate obstacles by the rover's radius plus a safety margin.

### What real rover planners do

The toy shows the core of the problem; real systems differ in several honest ways. The terrain map is built on the
fly from stereo images and is uncertain, so cells carry a confidence as well as a cost. The rover is not a point,
so it plans over its footprint and wheel placements, and the cost includes tilt and the risk of high-centring on a
rock. The map changes as the rover drives and sees more, so the planner must **replan** quickly; incremental
descendants of A\* such as D\* Lite and Field D\* reuse earlier search effort instead of starting over, and Field D\*
also allows paths that cut across cells at any angle rather than in 8 directions. Carsten and colleagues (2007)
describe how Field D\* was integrated into the flight software of the Mars Exploration Rovers Spirit and
Opportunity, where it was used for global path planning combined with the rovers' local hazard evaluation.
Perseverance's enhanced AutoNav also builds and searches terrain cost maps on board (Verma and colleagues, 2023).
Chapter 18 returns to motion planning with continuous configuration spaces.

### A short history

The A\* algorithm was published in 1968 by Peter Hart, Nils Nilsson and Bertram Raphael at the Stanford Research
Institute, for the Shakey robot, together with the proof that it is optimal with an admissible heuristic; a
correction to one of the proofs followed in 1972. Ira Pohl introduced weighted heuristic search in 1970 and studied
how heuristic error affects search cost. Judea Pearl's 1984 book *Heuristics* gathered the theory, and Dechter and
Pearl (1985) made the sense in which A\* is optimally efficient precise. Richard Korf introduced IDA\* in 1985, used
it to solve random instances of the 15-puzzle optimally, and introduced RBFS in 1993. Culberson and Schaeffer
introduced pattern databases in the mid-1990s, and Korf and Felner (2002) made them additive. Hansen and Zhou (2007)
analysed anytime weighted A\*.

## Check yourself

??? question "1. Trace A\* from Valles Marineris to Jezero crater on the Mars map ($h$ = great-circle distance to Jezero). Which route does it find, and how does greedy best-first search do?"

    The straight-line distances to Jezero are given in 4.1; Valles Marineris has $h = 8184$. Expand Valles
    ($f = 8184$): its only neighbour, Ascraeus, gets $g = 3043$, $f = 3043 + 8853 = 11\,896$. Expand Ascraeus:
    Olympus gets $g = 4782$, $f = 4782 + 7798 = 12\,580$ (the program, with unrounded values, prints 12 581).
    Expand Olympus: Erebus gets $g = 7151$, $f = 7151 + 5483 = 12\,634$; Gale gets $g = 10\,119$, $f = 13\,901$.
    Expand Erebus: Utopia $g = 9456$, $f = 9456 + 3214 = 12\,670$; Elysium $g = 9167$, $f = 12\,975$. Expand Utopia:
    Jezero $g = 12\,670$, $f = 12\,670$. Expand Jezero: goal. Route Valles, Ascraeus, Olympus, Erebus, Utopia,
    Jezero, 12 670 km, 5 expansions before the goal. Greedy follows the smallest $h$: Valles, Ascraeus, Olympus,
    then Gale ($h = 3782$ beats Erebus's 5483), then Jezero: 13 901 km, 9.7 percent longer.

??? question "2. Give a small road map on which greedy best-first tree search (no reached set) never terminates, even though a solution exists."

    Places $A$ (start), $B$, $C$, and goal $G$, with roads $A$–$B$, $A$–$C$ and $C$–$G$ (each two-way). Let the
    straight-line estimates be $h(A) = 3$, $h(B) = 2$, $h(C) = 4$ (possible if $B$ lies toward $G$ but has no road
    onward: a dead end). Tree search from $A$ expands $A$; its children are $B$ ($h = 2$) and $C$ ($h = 4$); it
    expands $B$, whose only child is $A$ ($h = 3$), which now beats $C$; expanding $A$ again generates $B$ again
    ($h = 2$), and so on: $A, B, A, B, \dots$ forever, while $C$ waits with $h = 4$. Graph search would mark $A$ and
    $B$ as reached, then expand $C$ and find $G$. (In Theorem 4.1's proof the same loop appears.)

??? question "3. Show with the graph S–A (1), S–B (1), A–C (1), B–C (2), C–G (3) and heuristic h(S) = 0, h(A) = 4, h(B) = 1, h(C) = 0, h(G) = 0 that h is admissible but not consistent, and that graph-search A\* without reopening returns a suboptimal path."

    True costs to $G$: $h^{*}(C) = 3$, $h^{*}(A) = 4$, $h^{*}(B) = 5$, $h^{*}(S) = 5$. Every $h \le h^{*}$, so $h$ is
    admissible. But $h(A) = 4 > c(A, C) + h(C) = 1 + 0$, so it is not consistent. A\*: expand $S$ ($f = 0$),
    generating $A$ ($f = 1 + 4 = 5$) and $B$ ($f = 1 + 1 = 2$). Expand $B$: $C$ gets $g = 3$, $f = 3$. Expand $C$
    ($f = 3$): $G$ gets $g = 6$, $f = 6$. Expand $A$ ($f = 5$): it offers $C$ with $g = 2$, but $C$ has been
    expanded; without reopening, the better path is discarded. Expand $G$: return cost 6. The optimum is 5 (S, A,
    C, G). With reopening, $C$ goes back on the frontier with $g = 2$, $f = 2$, is expanded again, and $G$ is reached
    with $g = 5$, the optimum. (A short program confirms both runs: the expansion orders are S, B, C, A, G with cost
    6, and S, B, C, A, C, G with cost 5.)

??? question "4. Prove that the maximum of two consistent heuristics is consistent."

    Let $h = \max(h_a, h_b)$. For an action $n \to n'$ of cost $c$: $h_a(n) \le c + h_a(n') \le c + h(n')$ and
    $h_b(n) \le c + h_b(n') \le c + h(n')$. So $h(n) = \max(h_a(n), h_b(n)) \le c + h(n')$. At a goal both parts are
    0, so $h = 0$. Hence $h$ is consistent, and by Lemma 4.3 admissible.

??? question "5. Prove that $h_1 \le h_2$ on every 8-puzzle state, and find a state where they are equal and not zero."

    Each misplaced tile is at least one square from its goal, so it contributes at least 1 to $h_2$ and exactly 1
    to $h_1$; correctly placed tiles contribute 0 to both. Summing, $h_1 \le h_2$. They are equal exactly when every
    misplaced tile is one square from home. Example: `(1, 2, 3, 4, 5, 6, 7, 0, 8)`, one move from the goal, has
    $h_1 = h_2 = 1$.

??? question "6. Why do the IDA\* bounds on the 8-puzzle with Manhattan distance go up in steps of 2? Would the same happen with $h_1$?"

    A move adds 1 to $g$ and moves one tile one square, so it changes $h_2$ by exactly $+1$ or $-1$. Hence
    $f = g + h_2$ changes by 0 or 2, and every $f$ value met in a search has the same parity as $h_2(\text{start})$. Bounds
    are $f$ values, so they rise by at least 2. (It also follows that $h_2(\text{start})$ and the solution length
    have the same parity: $h_2 = 14$ and 20 for our instance; 21 and 31 for the other.) With $h_1$, a move may leave
    $h_1$ unchanged (a tile moves from one wrong square to another), so $f$ can rise by 1, and bounds can rise by 1.

??? question "7. Weighted A\* with $w = 1.5$ found a 15-puzzle solution of 46 moves. Without knowing $C^{*}$, what does Theorem 4.10 let you conclude? Combine it with the Manhattan value $h = 28$ at the start."

    The solution costs at most $1.5\,C^{*}$, so $C^{*} \ge 46/1.5 \approx 30.7$, i.e. $C^{*} \ge 31$. Admissibility
    of Manhattan distance gives $C^{*} \ge 28$, a weaker bound. So the optimum lies between 31 and 46 (and, by the
    parity argument of exercise 6, it is even, since $h = 28$ is even: between 32 and 46). The true optimum, found
    by A\*, is 40. This is how weighted A\* is used in practice: it gives a solution together with a certificate of
    how far from optimal it can be.

??? question "8. Write code: Gaschnig's heuristic for the 8-puzzle, the exact cost of the relaxed problem in which a tile can jump into the blank from anywhere. Check that it is admissible, compare it with $h_1$ and $h_2$, and run A\* with it."

    ```python
    from ch03_search import EightPuzzle
    from ch03_space import bfs_layers
    from ch04_astar import astar, h1, h2

    GOAL = EightPuzzle.GOAL

    def h_gaschnig(s):
        """Relaxation: a tile may jump into the blank from anywhere.
        Count the swaps needed, done greedily."""
        s, swaps = list(s), 0
        while tuple(s) != GOAL:
            b = s.index(0)
            if GOAL[b] != 0:                 # put the right tile into the blank's square
                j = s.index(GOAL[b])
            else:                            # blank is home: move it to any misplaced tile
                j = next(i for i in range(9) if s[i] != GOAL[i])
            s[b], s[j] = s[j], s[b]
            swaps += 1
        return swaps

    dist = bfs_layers(GOAL)
    print("h1 <= hG <= h* everywhere:", all(h1(s) <= h_gaschnig(s) <= d for s, d in dist.items()))
    print("hG <= h2 everywhere:", all(h_gaschnig(s) <= h2(s) for s in dist),
          "| hG > h2 somewhere:", any(h_gaschnig(s) > h2(s) for s in dist))
    n = len(dist)
    print("mean hG:", round(sum(map(h_gaschnig, dist)) / n, 2))
    node, st = astar(EightPuzzle((7, 2, 4, 5, 0, 6, 8, 3, 1)), h_gaschnig)
    print("A* with hG on the chapter's instance:", node.depth, "moves,", st.generated, "generated")
    ```

    Output:

    ```
    h1 <= hG <= h* everywhere: True
    hG <= h2 everywhere: False | hG > h2 somewhere: True
    mean hG: 8.05
    A* with hG on the chapter's instance: 20 moves, 3465 generated
    ```

    Gaschnig's heuristic dominates $h_1$ (each misplaced tile needs a swap, and sometimes the blank needs extra swaps
    to reach a tile), is admissible (checked against the true cost of every state), and is neither above nor below
    $h_2$ everywhere: on some states it is larger. On average it is much weaker (8.05 against 14.00), and A\* with it
    generates 3465 nodes against 245 with $h_2$. Since neither dominates, $\max(h_G, h_2)$ would be at least as good
    as both (exercise 4).

??? question "9. In `ch04_astar.py`, change A\*'s tie-breaking to prefer the *shallower* node among equal $f$ values (priority $(f, g)$ instead of $(f, -g)$). Predict and then measure the effect on the 8-puzzle instance."

    With a consistent heuristic, A\* must expand every node with $f < C^{*} = 20$, whatever the tie-breaking, but
    among the nodes with $f = 20$ it can stop as soon as it reaches the goal. Preferring deeper nodes heads for the
    goal through the last layer; preferring shallower ones expands much of that layer first. So the number of nodes
    with $f < 20$ stays the same and the total grows. Measured: with $h_2$, preferring shallow nodes generated 747
    nodes and expanded 282, against 245 and 91 with the deeper-first rule; with $h_1$, 9900 and 3666 against 6325
    and 2336. The solution length is 20 either way, as Theorem 4.5 guarantees.

??? question "10. On the terrain grid, would the straight-line (Euclidean) distance be a better or worse heuristic than the octile distance? Is it admissible?"

    It is admissible: every path is at least as long as the straight line between its ends, and every move costs at
    least its length. It is consistent, by the triangle inequality. But it is never larger than the octile distance
    (the octile distance is the shortest path using the 8 allowed directions, which is at least the straight line),
    so the octile distance dominates it, and by Theorem 4.8 A\* with Euclidean distance expands at least as many
    cells (apart from ties). Octile is the better choice on an 8-connected grid; Euclidean is the right one for
    planners such as Field D\* that allow any direction.

??? question "11. Explain why a perfect heuristic, $h = h^{*}$, makes A\* expand only nodes on an optimal path (with ties broken toward larger $g$), and why this does not make search trivial in practice."

    With $h = h^{*}$, every node on an optimal path has $f = g + h^{*} = C^{*}$, and every node off all optimal paths
    has $f > C^{*}$ (the best solution through it is worse). So no node has $f < C^{*}$, and A\* expands only nodes
    with $f = C^{*}$. Breaking ties toward larger $g$ means it always extends the deepest such node, a successor of
    the last one expanded, so it walks straight down one optimal path. But computing $h^{*}$ exactly is as hard as
    solving the problem from every state: for the terrain we would have to run Dijkstra from the goal over the whole
    map first. Heuristic design is a trade-off between accuracy and the cost of computing $h$; pattern databases pay
    that cost once, ahead of time, for a relaxed problem small enough to solve completely.

## What you learned

- A heuristic $h(n)$ estimates the cost from $n$ to a goal. Greedy best-first search (order by $h$) is fast but not
  optimal, and as a tree search not complete.
- A\* orders by $f = g + h$. With an admissible $h$ (never overestimates), tree-search A\* is optimal; with a
  consistent $h$ (a triangle inequality), graph-search A\* expands states in non-decreasing $f$, each once, with its
  optimal cost. It must expand every node with $f < C^{*}$ and none with $f > C^{*}$.
- Exact costs of relaxed problems are admissible and consistent heuristics; higher (dominating) heuristics never
  make A\* do more work; the effective branching factor summarises a heuristic. On the 8-puzzle, misplaced tiles,
  Manhattan distance and an additive pattern database give $b^{*}$ of about 1.45, 1.28 and 1.15.
- IDA\* and RBFS keep A\*'s optimality in $O(bd)$ memory, at the cost of repeated work; IDA\* suffers when $f$
  takes many distinct values.
- Weighted A\* ($f = g + w h$) returns solutions within $w$ times optimal, usually much faster; anytime versions
  improve the solution and finally prove it optimal.
- On a terrain cost grid, A\* found the optimal route with a third fewer expansions than Dijkstra, and weighted A\*
  with 20 times fewer; a heuristic that ignores most of the cost saves little, whatever the algorithm.

**Next:** [Chapter 5](05-Local-Search-and-Optimization.md) drops the path altogether: when only the final state
matters, as in scheduling or the n-queens puzzle, local search improves one candidate at a time.

## Further reading

- S. Russell and P. Norvig, *Artificial Intelligence: A Modern Approach*, 4th ed., Pearson, 2020, Sections 3.5 and
  3.6 (informed search, heuristic functions).
- P. E. Hart, N. J. Nilsson and B. Raphael, "A formal basis for the heuristic determination of minimum cost
  paths", *IEEE Transactions on Systems Science and Cybernetics* 4(2), 1968; and "Correction to 'A formal basis
  for the heuristic determination of minimum cost paths'", *SIGART Newsletter* 37, 1972.
- I. Pohl, "Heuristic search viewed as path finding in a graph", *Artificial Intelligence* 1(3-4), 1970.
- J. Pearl, *Heuristics: Intelligent Search Strategies for Computer Problem Solving*, Addison-Wesley, 1984.
- R. Dechter and J. Pearl, "Generalized best-first search strategies and the optimality of A\*", *Journal of the
  ACM* 32(3), 1985.
- R. E. Korf, "Depth-first iterative-deepening: an optimal admissible tree search", *Artificial Intelligence*
  27(1), 1985.
- R. E. Korf, "Linear-space best-first search", *Artificial Intelligence* 62(1), 1993.
- J. Gaschnig, *Performance Measurement and Analysis of Certain Search Algorithms*, PhD thesis, Carnegie Mellon
  University, 1979.
- J. C. Culberson and J. Schaeffer, "Pattern databases", *Computational Intelligence* 14(3), 1998.
- R. E. Korf and A. Felner, "Disjoint pattern database heuristics", *Artificial Intelligence* 134(1-2), 2002.
- R. E. Korf and L. A. Taylor, "Finding optimal solutions to the twenty-four puzzle", AAAI 1996.
- S. Russell, "Efficient memory-bounded search methods", ECAI 1992.
- M. Likhachev, G. Gordon and S. Thrun, "ARA\*: anytime A\* with provable bounds on sub-optimality", NeurIPS 2003.
- E. A. Hansen and R. Zhou, "Anytime heuristic search", *Journal of Artificial Intelligence Research* 28, 2007.
- S. Koenig and M. Likhachev, "D\* Lite", AAAI 2002; D. Ferguson and A. Stentz, "Using interpolation to improve
  path planning: the Field D\* algorithm", *Journal of Field Robotics* 23(2), 2006.
- J. Carsten, A. Rankin, D. Ferguson and A. Stentz, "Global path planning on board the Mars Exploration Rovers",
  IEEE Aerospace Conference, 2007.
- On this site: [Dijkstra's algorithm](../../graphs/dijkstra.md), [Binary heap](../../data-structures/binary-heap.md),
  [Section 16.6 of the Algorithms book](../algorithms/16-Shortest-Paths.md#166-a-search-and-bidirectional-search)
  (A\* as Dijkstra on reweighted edges, landmarks, bidirectional A\*), and
  [Chapter 14 of the Algorithms book](../algorithms/14-Backtracking-and-Branch-and-Bound.md) (branch and bound, a
  close relative of A\*'s pruning).
