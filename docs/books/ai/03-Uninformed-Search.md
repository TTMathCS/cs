# 3. Searching for solutions

*The goal-based agent of Chapter 2 had to look ahead: "if I do this, then that, will I reach the goal?" When one
action is not enough, the agent must consider sequences of actions, and there are usually far too many to list.
This chapter makes the look-ahead precise. You will learn to state a problem as a state space (the 8-puzzle, routes
between places on Mars, the missionaries and cannibals), see why searching a tree of paths differs from searching a
graph of states, and build one generic search program whose behaviour is set by a single choice: which waiting node
to look at next. From it come breadth-first, uniform-cost and depth-first search; with small changes,
depth-limited, iterative deepening and bidirectional search. For each one you will prove whether it always finds a
solution, whether it finds the best one, and how much time and memory it needs, and then check the proofs against
measurements.*

!!! abstract "In this chapter"
    **You will learn:**

    - how to formulate a problem: states, initial state, actions, transition model, goal test, action costs; and
      why choosing the abstraction is the real work
    - the state spaces of the 8-puzzle (with the parity proof that half its arrangements are unreachable), route
      finding and the missionaries and cannibals
    - search trees versus state-space graphs, the frontier, the reached set, and the separation property
    - breadth-first, uniform-cost, depth-first, depth-limited and iterative deepening search, each with proofs of
      completeness, optimality, time and space
    - bidirectional search and why it costs about $b^{d/2}$ instead of $b^{d}$
    - one generic search program that runs all of them, measured on three problems

    **You need:** [Chapter 2](02-Intelligent-Agents.md) (goal-based agents, atomic states). Graphs, queues and
    stacks as in [Chapter 15 of the Algorithms book](../algorithms/15-Graphs-and-Graph-Search.md) and
    [Chapter 4 of the Algorithms book](../algorithms/04-Lists-Stacks-and-Queues.md); priority queues as in
    [Chapter 9](../algorithms/09-Heaps-and-Priority-Queues.md); $O$-notation and geometric series as in
    [Chapter 2](../algorithms/02-Measuring-Cost.md).

    **Levels:** 3.1 and 3.2 are beginner; 3.3 is beginner to intermediate (the proofs are intermediate); 3.4 is
    intermediate; 3.5 is beginner to intermediate.

## 3.1 Problems as state spaces

A rover at Olympus Mons is told to reach Jezero crater. Its map shows nine places and twelve roads between them.
Which roads should it take? A child sliding tiles in a puzzle wants to put them in order. Three missionaries and
three cannibals must cross a river in a boat that holds two. These look like different problems. They are the same
problem: find a sequence of actions that leads from where you are to where you want to be.

### The parts of a problem

A **search problem** is defined by six things.

1. A set of **states** $S$, the possible situations. States are atomic (Chapter 2, Section 2.5): the search
   algorithm only needs to test them for equality and use them as keys.
2. An **initial state** $s_0 \in S$, where the agent starts.
3. For each state $s$, the set of **actions** $\mathrm{ACTIONS}(s)$ that can be done there.
4. A **transition model** $\mathrm{RESULT}(s, a)$, the state that results from doing $a$ in $s$. (In this chapter
   the environment is fully observable, deterministic and known, so the result is a single, known state.)
5. A **goal test**: a set of goal states, or a function $\mathrm{IS\text{-}GOAL}(s)$ that says whether $s$ is one.
6. An **action cost** $c(s, a, s') > 0$, the cost of doing $a$ in $s$ to reach $s'$: kilometres, minutes, fuel, or
   just 1 per step.

The states and the transitions together form the **state space**, a directed graph whose vertices are states and
whose edges are actions. A **path** is a sequence of states joined by actions; its cost is the sum of its action
costs. A **solution** is a path from the initial state to a goal state, and an **optimal solution** is one of
lowest cost among all solutions. The **depth** of a solution is its number of actions.

### Abstraction

A real rover driving from Olympus Mons to Jezero crater passes through billions of physical situations: wheel
angles, dust on the cameras, the exact position to the millimetre. The road map throws almost all of that away.
That is **abstraction**: removing detail from a representation. An abstraction is *valid* if every abstract
solution can be expanded into a real one (every road on the map can actually be driven), and *useful* if carrying
out each abstract action is easier than the original problem (driving one road is something the rover's local
navigation can do on its own, as Chapter 2 described). Choosing a good abstraction is often most of the work; the
search algorithms then run on whatever we give them.

### Example 1: routes on Mars

The state is the place where the rover is. The initial state is Olympus Mons; the goal is Jezero crater. The actions
in a place are "drive to a neighbouring place by its road"; the result is that place; the cost of an action is the
road's length. On this site's map of Mars (the same map as in
[Chapter 16 of the Algorithms book](../algorithms/16-Shortest-Paths.md)), the places are real (their latitudes
and longitudes come from the USGS Gazetteer of Planetary Nomenclature), and each road's length is the great-circle
distance between its ends on a sphere of radius 3389.5 km. The roads themselves are invented for the example.

<figure class="mars-fig" markdown="0">
<svg viewBox="0 0 600 280" role="img" aria-label="A map of nine places on Mars joined by twelve roads with their lengths in kilometres. Jezero crater and Hellas Planitia are on the left, Utopia Planitia, Elysium Mons and Gale crater in the middle left, Erebus Montes in the middle, Olympus Mons, Ascraeus Mons and Valles Marineris on the right.">
  <g stroke="currentColor" stroke-width="1.5" stroke-opacity="0.7">
    <line x1="330" y1="60" x2="410" y2="125"/>
    <line x1="330" y1="60" x2="235" y2="110"/>
    <line x1="330" y1="60" x2="190" y2="40"/>
    <line x1="410" y1="125" x2="490" y2="150"/>
    <line x1="490" y1="150" x2="555" y2="215"/>
    <line x1="235" y1="110" x2="195" y2="190"/>
    <line x1="190" y1="40" x2="235" y2="110"/>
    <line x1="190" y1="40" x2="70" y2="110"/>
    <line x1="70" y1="110" x2="195" y2="190"/>
    <line x1="70" y1="110" x2="60" y2="240"/>
    <line x1="195" y1="190" x2="60" y2="240"/>
    <line x1="410" y1="125" x2="195" y2="190"/>
  </g>
  <g font-size="11" fill="currentColor" text-anchor="middle">
    <text x="384" y="84">2369</text>
    <text x="294" y="98">2016</text>
    <text x="262" y="42">2305</text>
    <text x="455" y="155">1740</text>
    <text x="538" y="178">3043</text>
    <text x="230" y="158">1879</text>
    <text x="226" y="70">1486</text>
    <text x="122" y="66">3214</text>
    <text x="122" y="164">3782</text>
    <text x="46" y="178">3616</text>
    <text x="132" y="230">4122</text>
    <text x="318" y="172">5337</text>
  </g>
  <g stroke="currentColor">
    <circle cx="330" cy="60" r="6" fill="#9cc9ea"/>
    <circle cx="410" cy="125" r="6" fill="#eea66f"/>
    <circle cx="490" cy="150" r="6" fill="#9cc9ea"/>
    <circle cx="555" cy="215" r="6" fill="#9cc9ea"/>
    <circle cx="235" cy="110" r="6" fill="#9cc9ea"/>
    <circle cx="190" cy="40" r="6" fill="#9cc9ea"/>
    <circle cx="195" cy="190" r="6" fill="#9cc9ea"/>
    <circle cx="70" cy="110" r="6" fill="#7ccf9a"/>
    <circle cx="60" cy="240" r="6" fill="#9cc9ea"/>
  </g>
  <g font-size="12" fill="currentColor">
    <text x="342" y="52">Erebus Montes</text>
    <text x="418" y="118">Olympus Mons</text>
    <text x="498" y="143">Ascraeus Mons</text>
    <text x="590" y="240" text-anchor="end">Valles Marineris</text>
    <text x="245" y="122">Elysium Mons</text>
    <text x="200" y="26" text-anchor="middle">Utopia Planitia</text>
    <text x="205" y="208">Gale crater</text>
    <text x="10" y="94">Jezero crater</text>
    <text x="70" y="262">Hellas Planitia</text>
  </g>
</svg>
<figcaption>Figure 3.1. The road map of Mars used in this chapter and the next (schematic positions; lengths are
great-circle distances in km). Orange: the start, Olympus Mons; green: the goal, Jezero crater.</figcaption>
</figure>

### Example 2: the 8-puzzle

The 8-puzzle is a 3 × 3 board with eight numbered tiles and one blank. A tile next to the blank can slide into it.
The goal is a given arrangement; we use tiles 1 to 8 in reading order with the blank last.

- **States:** the arrangement of the nine squares, written as a tuple read row by row with 0 for the blank, such as
  `(7, 2, 4, 5, 0, 6, 8, 3, 1)`.
- **Actions:** it is simplest to think of the *blank* moving Up, Down, Left or Right; only moves that stay on the
  board are allowed, so a state has 2, 3 or 4 actions.
- **Transition model:** swap the blank with the tile in that direction.
- **Goal test:** the state equals `(1, 2, 3, 4, 5, 6, 7, 8, 0)`. **Action cost:** 1 per move.

<figure class="mars-fig" markdown="0">
<svg viewBox="0 0 520 190" role="img" aria-label="Two 3 by 3 boards. Left, the start state: 7 2 4 / 5 blank 6 / 8 3 1. Right, the goal state: 1 2 3 / 4 5 6 / 7 8 blank. An arrow between them is labelled 20 moves at least.">
  <g stroke="currentColor" stroke-width="1.5" font-size="22" text-anchor="middle" fill="currentColor">
    <rect x="40" y="20" width="150" height="150" fill="none"/>
    <rect x="330" y="20" width="150" height="150" fill="none"/>
  </g>
  <g fill="#9cc9ea" fill-opacity="0.45" stroke="currentColor">
    <rect x="40" y="20" width="50" height="50"/><rect x="90" y="20" width="50" height="50"/><rect x="140" y="20" width="50" height="50"/>
    <rect x="40" y="70" width="50" height="50"/><rect x="140" y="70" width="50" height="50"/>
    <rect x="40" y="120" width="50" height="50"/><rect x="90" y="120" width="50" height="50"/><rect x="140" y="120" width="50" height="50"/>
    <rect x="330" y="20" width="50" height="50"/><rect x="380" y="20" width="50" height="50"/><rect x="430" y="20" width="50" height="50"/>
    <rect x="330" y="70" width="50" height="50"/><rect x="380" y="70" width="50" height="50"/><rect x="430" y="70" width="50" height="50"/>
    <rect x="330" y="120" width="50" height="50"/><rect x="380" y="120" width="50" height="50"/>
  </g>
  <g font-size="22" text-anchor="middle" fill="currentColor">
    <text x="65" y="53">7</text><text x="115" y="53">2</text><text x="165" y="53">4</text>
    <text x="65" y="103">5</text><text x="165" y="103">6</text>
    <text x="65" y="153">8</text><text x="115" y="153">3</text><text x="165" y="153">1</text>
    <text x="355" y="53">1</text><text x="405" y="53">2</text><text x="455" y="53">3</text>
    <text x="355" y="103">4</text><text x="405" y="103">5</text><text x="455" y="103">6</text>
    <text x="355" y="153">7</text><text x="405" y="153">8</text>
  </g>
  <line x1="205" y1="95" x2="308" y2="95" stroke="currentColor" stroke-width="2"/>
  <polygon points="316,95 306,90 306,100" fill="currentColor"/>
  <text x="260" y="85" font-size="12" text-anchor="middle" fill="currentColor">at least 20</text>
  <text x="260" y="115" font-size="12" text-anchor="middle" fill="currentColor">moves</text>
  <text x="115" y="186" font-size="13" text-anchor="middle" fill="currentColor">start</text>
  <text x="405" y="186" font-size="13" text-anchor="middle" fill="currentColor">goal</text>
</svg>
<figcaption>Figure 3.2. The 8-puzzle instance used in this chapter. The fewest moves from start to goal is 20, as
every optimal algorithm below confirms.</figcaption>
</figure>

**How many states?** There are $9! = 362\,880$ ways to place nine items in nine squares. But not all of them can be
reached from a given start. Here is why, and it is a beautiful small proof.

Read the eight tiles in reading order, ignoring the blank. An **inversion** is a pair of tiles where the larger
comes first. For the start state, the tile order is 7, 2, 4, 5, 6, 8, 3, 1, and the inversions are 7 before each of
2, 4, 5, 6, 3, 1 (six), 2 before 1 (one), 4 before 3 and 1 (two), 5 before 3 and 1 (two), 6 before 3 and 1 (two),
8 before 3 and 1 (two), 3 before 1 (one): $6 + 1 + 2 + 2 + 2 + 2 + 1 = 16$. The goal has 0.

**Theorem 3.1 (parity invariant).** Every move of the 8-puzzle leaves the number of inversions even if it was even
and odd if it was odd. Hence a state with an odd number of inversions can never reach the goal.

*Proof.* A left or right move swaps the blank with a neighbour in the same row, which does not change the order of
the tiles read row by row, so the inversion count is unchanged. An up or down move takes a tile from one row to the
next, jumping in reading order over exactly the two tiles that lie between its old and new positions (there are
three squares per row, so it moves two places in the sequence of tiles). Moving one tile past two others changes
its relative order with each of them, and each change adds or removes one inversion, so the count changes by $-2$,
$0$ or $+2$. In every case the parity is unchanged. The goal has 0 inversions (even), so only states with an even
count can reach it. $\square$

The start state has 16 inversions, an even number, so it may be solvable. The theorem shows that *at most* half of
the $9!$ arrangements are reachable. That *exactly* half are, $9!/2 = 181\,440$, needs a converse argument (one
shows that the moves can produce any even permutation of the tiles); for the 8-puzzle we can simply check it by
computer. The program `ch03_space.py` in Section 3.5 runs breadth-first search from the goal over the whole
reachable space, finds 181 440 states, and confirms that a state is reachable exactly when its inversion count is
even. It also finds that the farthest states need 31 moves. The 15-puzzle (4 × 4) has $16!/2 \approx 10^{13}$
reachable states, and the 24-puzzle about $10^{25}$, which is where blind search gives up and Chapter 4 begins.

### Example 3: missionaries and cannibals

Three missionaries and three cannibals are on the left bank of a river with a boat that carries one or two people.
If cannibals ever outnumber missionaries on a bank where there are missionaries, the missionaries are eaten. How can
all six cross?

The abstraction that makes this easy: the identities of the people do not matter, and neither does anything that
happens mid-river. The state is the triple $(m, c, b)$: missionaries on the left bank, cannibals on the left bank,
and whether the boat is on the left (1) or right (0). The initial state is $(3, 3, 1)$ and the goal $(0, 0, 0)$. An
action is a boat load, one of $(1,0), (2,0), (0,1), (0,2), (1,1)$, carried from the boat's bank to the other,
allowed only if both banks are safe afterwards. Of the $4 \times 4 \times 2 = 32$ triples, the program finds that
16 are reachable from the start. Saul Amarel used this puzzle in 1968 to show how much the choice of representation
affects how hard a problem is to solve.

## 3.2 Tree search and graph search; the frontier and the reached set

How does an algorithm explore a state space it cannot see all at once? It grows a **search tree**. The root is the
initial state. **Expanding** a node means applying every action to its state and creating a child node for each
result. Each node records four things: its **state**, its **parent** node, the **action** that produced it, and the
**path cost** $g(n)$ from the root. Following parents back from a node gives the path to it.

The nodes that have been generated but not yet expanded form the **frontier** (also called the open list). Every
search algorithm in this chapter has the same loop: take a node from the frontier; if its state is a goal, return
it; otherwise expand it and add its children to the frontier. They differ only in *which* node they take next.

### The tree is not the graph

A **state** is a situation in the world; a **node** is a bookkeeping record for one *path* to that situation. The
same state can appear in many nodes. In the 8-puzzle, moving the blank Up and then Down returns to the start; the
search tree would happily contain the start state at depth 0, 2, 4, ..., an infinite tree over a finite graph. On
the Mars map, Gale crater can be reached from Olympus Mons directly or via Elysium Mons. Paths that reach a state
already reached are **redundant**, and a path that returns to a state already on it is a **cycle** (a special case).

There are three ways to handle them.

1. **Tree search.** Ignore the problem. Simple, uses little memory, but can waste exponential time on redundant
   paths and may loop forever on cycles.
2. **Graph search.** Keep a table of every state **reached** so far (in older texts, the explored set plus the
   frontier), and do not add a child whose state has already been reached, unless (for cost-based search) the new
   path is cheaper. Each state is then expanded at most once, at the price of memory proportional to the number of
   states reached.
3. **Tree-like search with cycle checking.** Check only whether the child's state already appears on the path back
   to the root. This removes cycles but not other redundant paths, and needs memory only for the current path. It is
   the choice for depth-first methods (3.3), where memory is the point.

<figure class="mars-fig" markdown="0">
<svg viewBox="0 0 600 260" role="img" aria-label="A search on a grid. Expanded states form a filled region around the start; the frontier is a ring of states around it; unreached states lie outside. Any path from the start to an unreached state, drawn as an arrow, must cross the frontier ring.">
  <rect x="20" y="20" width="560" height="220" rx="8" fill="none" stroke="currentColor" stroke-opacity="0.4"/>
  <ellipse cx="230" cy="130" rx="170" ry="95" fill="#eea66f" fill-opacity="0.3" stroke="currentColor" stroke-dasharray="6 4"/>
  <ellipse cx="230" cy="130" rx="125" ry="65" fill="#9cc9ea" fill-opacity="0.5" stroke="currentColor"/>
  <circle cx="200" cy="130" r="7" fill="currentColor"/>
  <text x="200" y="155" font-size="12" text-anchor="middle" fill="currentColor">start</text>
  <text x="250" y="110" font-size="13" text-anchor="middle" fill="currentColor">expanded</text>
  <text x="230" y="52" font-size="13" text-anchor="middle" fill="currentColor">frontier</text>
  <text x="500" y="60" font-size="13" text-anchor="middle" fill="currentColor">unreached</text>
  <circle cx="500" cy="170" r="7" fill="#7ccf9a" stroke="currentColor"/>
  <text x="500" y="195" font-size="12" text-anchor="middle" fill="currentColor">goal</text>
  <path d="M 207 128 Q 300 105 385 128 T 490 170" fill="none" stroke="currentColor" stroke-width="2"/>
  <circle cx="385" cy="128" r="5" fill="#eea66f" stroke="currentColor"/>
  <text x="392" y="118" font-size="11" fill="currentColor">crosses the frontier</text>
</svg>
<figcaption>Figure 3.3. The separation property. The frontier (dashed ring) separates the states already expanded
from the states not yet reached: every path from the start to an unreached state passes through a frontier
state.</figcaption>
</figure>

**Theorem 3.2 (separation property).** In graph search, at the start of every iteration of the loop, every path
from the initial state to a state that has not been reached passes through some state on the frontier.

*Proof.* Take any path from the initial state to a state $u$ that has not been reached. The initial state has
been reached and $u$ has not, so walking along the path there is a *last* reached state $x$, followed by an
unreached state $y$. If $x$ had already been expanded, the edge $x \to y$ would have generated $y$, and graph search
adds every generated child whose state has not been reached, so $y$ would be reached. Hence $x$ is reached but not
yet expanded, which is exactly what it means to be on the frontier. $\square$

The argument is worth remembering in one line: along any path from the start to an unreached state, the last
reached state has not been expanded, so it is on the frontier. Consequence: an
algorithm that empties its frontier has reached every state reachable from the start, so if it reports failure,
there really is no solution.

### Measuring a search algorithm

We judge search algorithms on four criteria.

- **Completeness:** is it guaranteed to find a solution when one exists, and to report failure when none does?
- **Cost optimality:** does it find a solution with the lowest path cost?
- **Time complexity:** how long does it take? We count nodes generated (or expanded), which is proportional to time.
- **Space complexity:** how much memory does it need? We count nodes stored at once.

For graphs given explicitly, as in the Algorithms book, time is measured as $O(V + E)$. In AI the graph is usually
*implicit* (given by the initial state, actions and transition model) and may be infinite, so we use three numbers:
the **branching factor** $b$ (the maximum number of successors of any node), the **depth** $d$ of the shallowest
solution, and the **maximum depth** $m$ of any path (possibly $\infty$). For cost-based search we also use $C^{*}$,
the cost of an optimal solution, and $\varepsilon > 0$, a lower bound on every action cost.

## 3.3 Uninformed search strategies

*Level: beginner to intermediate; the proofs are intermediate.*

**Uninformed** (or **blind**) search uses no information about how close a state is to the goal. It can only
generate successors and recognise a goal when it sees one. (Chapter 4 adds such information.) There are five
classic strategies.

<figure class="mars-fig" markdown="0">
<svg viewBox="0 0 600 250" role="img" aria-label="A complete binary tree of depth 3 with nodes A to O. A is the root; B and C its children; D, E, F, G at depth 2; H to O at depth 3. The goal node M is highlighted.">
  <g stroke="currentColor" stroke-width="1.3" stroke-opacity="0.7">
    <line x1="300" y1="30" x2="150" y2="90"/><line x1="300" y1="30" x2="450" y2="90"/>
    <line x1="150" y1="90" x2="75" y2="150"/><line x1="150" y1="90" x2="225" y2="150"/>
    <line x1="450" y1="90" x2="375" y2="150"/><line x1="450" y1="90" x2="525" y2="150"/>
    <line x1="75" y1="150" x2="38" y2="210"/><line x1="75" y1="150" x2="112" y2="210"/>
    <line x1="225" y1="150" x2="188" y2="210"/><line x1="225" y1="150" x2="262" y2="210"/>
    <line x1="375" y1="150" x2="338" y2="210"/><line x1="375" y1="150" x2="412" y2="210"/>
    <line x1="525" y1="150" x2="488" y2="210"/><line x1="525" y1="150" x2="562" y2="210"/>
  </g>
  <g stroke="currentColor" fill="#9cc9ea">
    <circle cx="300" cy="30" r="14"/><circle cx="150" cy="90" r="14"/><circle cx="450" cy="90" r="14"/>
    <circle cx="75" cy="150" r="14"/><circle cx="225" cy="150" r="14"/><circle cx="375" cy="150" r="14"/><circle cx="525" cy="150" r="14"/>
    <circle cx="38" cy="210" r="14"/><circle cx="112" cy="210" r="14"/><circle cx="188" cy="210" r="14"/><circle cx="262" cy="210" r="14"/>
    <circle cx="338" cy="210" r="14"/><circle cx="412" cy="210" r="14" fill="#7ccf9a"/><circle cx="488" cy="210" r="14"/><circle cx="562" cy="210" r="14"/>
  </g>
  <g font-size="13" text-anchor="middle" fill="currentColor">
    <text x="300" y="35">A</text><text x="150" y="95">B</text><text x="450" y="95">C</text>
    <text x="75" y="155">D</text><text x="225" y="155">E</text><text x="375" y="155">F</text><text x="525" y="155">G</text>
    <text x="38" y="215">H</text><text x="112" y="215">I</text><text x="188" y="215">J</text><text x="262" y="215">K</text>
    <text x="338" y="215">L</text><text x="412" y="215">M</text><text x="488" y="215">N</text><text x="562" y="215">O</text>
    <text x="412" y="243">goal</text>
  </g>
</svg>
<figcaption>Figure 3.4. A complete binary tree ($b = 2$) of depth 3, children generated left to right. The goal is
M. The table below lists the order in which each strategy expands nodes until it reaches M.</figcaption>
</figure>

| Strategy | Order of nodes taken from the frontier, until M | Nodes |
|---|---|---|
| breadth-first | A B C D E F G H I J K L M | 13 |
| depth-first | A B D H I E J K C F L M | 12 |
| iterative deepening | limit 0: A; limit 1: A B C; limit 2: A B D E C F G; limit 3: A B D H I E J K C F L M | 23 |

Keep this table in mind while reading the proofs: breadth-first goes layer by layer; depth-first goes down the left
side first; iterative deepening repeats depth-first with growing limits, revisiting the top of the tree each time.

### Breadth-first search

**Breadth-first search** (BFS) expands the shallowest node first: the frontier is a **FIFO queue** (first in,
first out), so the root is expanded, then all its children, then all their children, and so on. Because a node at
depth $k$ is always generated after every node at depth $k - 1$ has been, BFS can apply the goal test when a node is
*generated* rather than when it is expanded (an **early goal test**): the first goal node generated is already a
shallowest one. For graph search, a child is discarded if its state has been reached before.

**Theorem 3.3 (breadth-first search).** Suppose the branching factor $b$ is finite. Then BFS (graph search with
an early goal test) is complete; it returns a solution with the fewest actions; and it generates $O(b^{d})$ nodes and
stores $O(b^{d})$ nodes, where $d$ is the depth of the shallowest solution.

*Proof.* First, the frontier is always ordered by depth with at most two consecutive depths present: every node
added is a child of the node just removed, so if the queue holds depths $k$ and $k+1$, removals of depth-$k$ nodes
add depth-$(k+1)$ nodes at the back. (This is Lemma 15.1 of the
[Algorithms book](../algorithms/15-Graphs-and-Graph-Search.md#152-breadth-first-search-and-shortest-paths).) Hence nodes are generated in
non-decreasing order of depth.

*Shallowest solution.* Let the shallowest goal be at depth $d$ and $s_0, s_1, \dots, s_d$ a path to it. By
induction on $k$, some state at distance exactly $k$ from $s_0$ is generated, and every state at distance $k$ is
reached with a node of depth $k$ (the graph version of Theorem 15.2 of the Algorithms book). Since nodes are
generated in order of depth, every node generated before the first goal has depth at most $d$, and the first goal
generated has depth exactly $d$: none at depth below $d$ exists, and the goal at depth $d$ will be generated by the
time the depth-$(d-1)$ layer has been expanded.

*Completeness.* With a finite $b$, each layer is finite, so the layers up to depth $d$ are generated in finite
time, even if the state space is infinite. If there is no solution and the state space is finite, graph search
eventually empties the frontier and reports failure, which by the separation property (Theorem 3.2) is correct.

*Cost.* At most $b$ nodes at depth 1, $b^2$ at depth 2, ..., $b^{d}$ at depth $d$ are generated, so in total at most

$$
1 + b + b^2 + \dots + b^{d} = \frac{b^{d+1} - 1}{b - 1} = O(b^{d})
$$

for fixed $b \ge 2$. Graph search keeps every reached node in its table and the frontier holds the whole deepest
layer, so the memory is also $O(b^{d})$. $\square$

BFS is optimal when every action has the same cost, because then fewest actions means lowest cost. It is not
optimal with varied costs: on the Mars map, BFS finds Olympus Mons, Gale crater, Jezero crater, 2 roads and 9119
km, while a 3-road route of 7888 km exists (the program's output in 3.5).

The real problem is memory. The program `ch03_space.py` prints what BFS costs for $b = 10$ if a computer generates
a million nodes a second and each node takes a kilobyte:

```
breadth-first search with b = 10, 1 million nodes per second, 1 kilobyte per node:
  depth  2:                    111 nodes, 0.000111 seconds,    111 kB
  depth  4:                 11,111 nodes,   0.0111 seconds,   11.1 MB
  depth  6:              1,111,111 nodes,     1.11 seconds,   1.11 GB
  depth  8:            111,111,111 nodes,      111 seconds,    111 GB
  depth 10:         11,111,111,111 nodes,       3.09 hours,   11.1 TB
  depth 12:      1,111,111,111,111 nodes,        309 hours,   1.11 PB
  depth 14:    111,111,111,111,111 nodes,       3.52 years,    111 PB
  depth 16: 11,111,111,111,111,111 nodes,        352 years,   11.1 EB
```

Depth 8 takes two minutes but 111 gigabytes; depth 12 takes under two weeks but a petabyte. Memory runs out long
before patience. Two lessons: memory is a worse problem than time for BFS, and exponential-complexity search
problems cannot be solved by uninformed methods for any but the smallest instances.

### Uniform-cost search

When actions have different costs, expand the node with the **lowest path cost** $g(n)$ first: the frontier is a
**priority queue** ordered by $g$. This is **uniform-cost search** (UCS). On an explicit graph it is Dijkstra's
algorithm ([Chapter 16 of the Algorithms book](../algorithms/16-Shortest-Paths.md#162-dijkstras-algorithm)); the AI
version differs only in that the graph is implicit, the search stops at the goal, and a cheaper path to a state on
the frontier is handled by adding a new node and skipping the old one when it comes out ("lazy deletion").

The goal test must be applied when a node is *expanded*, not when it is generated. Example: $S \to G$ costs 10,
while $S \to A$ and $A \to G$ cost 1 each. Expanding $S$ generates $G$ with cost 10 and $A$ with cost 1. An early
goal test would return the cost-10 path. With the late test, $A$ (cost 1) is expanded first, generating $G$ with
cost 2, which comes out of the queue before the cost-10 copy.

A hand trace on the Mars map, from Olympus Mons to Jezero crater. Each row shows the node expanded (with its $g$)
and then the frontier, cheapest first.

| Step | Expand (g, km) | Frontier after expanding |
|---|---|---|
| 1 | Olympus Mons 0 | Ascraeus 1740, Erebus 2369, Gale 5337 |
| 2 | Ascraeus Mons 1740 | Erebus 2369, Valles 4782, Gale 5337 |
| 3 | Erebus Montes 2369 | Elysium 4385, Utopia 4674, Valles 4782, Gale 5337 |
| 4 | Elysium Mons 4385 | Utopia 4674, Valles 4782, Gale 5337 (via Elysium would be 6264: no change) |
| 5 | Utopia Planitia 4674 | Valles 4782, Gale 5337, Jezero 7888 |
| 6 | Valles Marineris 4782 | Gale 5337, Jezero 7888 |
| 7 | Gale crater 5337 | Jezero 7888 (via Gale would be 9119: no change), Hellas 9459 |
| 8 | Jezero crater 7888 | goal: return Olympus, Erebus, Utopia, Jezero |

Notice step 7: Jezero crater was on the frontier with $g = 7888$ when the direct road through Gale offered 9119;
the cheaper entry stays. Notice also that UCS expanded Valles Marineris, which is in the wrong direction, simply
because it was cheap to reach. Uninformed search has no sense of direction; Chapter 4 gives it one.

**Theorem 3.4 (uniform-cost search).** Suppose every action cost is at least some $\varepsilon > 0$ and $b$ is
finite. Then UCS (graph search, late goal test) is complete and cost-optimal, and it generates
$O(b^{1 + \lfloor C^{*}/\varepsilon \rfloor})$ nodes, where $C^{*}$ is the optimal solution cost.

*Proof.* *Optimality.* With non-negative costs, the values $g$ of the nodes expanded never decrease: a child has
$g$ at least that of its parent, and the queue always gives the smallest. The proof that the first time a state is
expanded its $g$ is the optimal cost to reach it is exactly the proof of Dijkstra's algorithm (Theorem 16.4 of the
Algorithms book), which uses the separation property: if a cheaper path to state $s$ existed, its first unexpanded
state would be on the frontier with a smaller $g$, and would have been taken first. The goal is tested on
expansion, so the solution returned is optimal.

*Completeness.* Every node with $g < C^{*}$ has at most $\lfloor C^{*}/\varepsilon \rfloor$ actions on its path,
because each costs at least $\varepsilon$. With a finite $b$ there are finitely many such paths, so after finitely
many expansions every node with $g < C^{*}$ has been expanded and the optimal goal node is taken. (The condition
$\varepsilon > 0$ matters: with zero-cost actions, an infinite sequence of zero-cost moves could keep UCS busy
forever.)

*Cost.* All nodes expanded have $g \le C^{*}$, hence depth at most $\lfloor C^{*}/\varepsilon \rfloor$; the nodes
generated are their children, one level deeper. So at most
$1 + b + \dots + b^{1 + \lfloor C^{*}/\varepsilon \rfloor}$ nodes are generated. $\square$

The bound can be much worse than BFS's $b^{d}$: when many actions are cheap and a few are expensive, UCS may explore
long chains of cheap actions before trying an expensive one that leads to the goal. When all costs are equal,
$C^{*}/\varepsilon = d$ and the bound is $b^{d+1}$: UCS then does what BFS does, plus the last layer that BFS's
early goal test avoids. In the 8-puzzle run below it generates 161 168 nodes against BFS's 106 576.

### Depth-first search

**Depth-first search** (DFS) expands the *deepest* node first: the frontier is a **LIFO stack** (last in, first
out). It goes down one branch until it reaches a node with no successors, then backs up to the most recent node
with unexplored children. It is usually written as tree-like search, often recursively, with checking for cycles
on the current path only.

**Theorem 3.5 (depth-first search).** (a) As graph search in a finite state space, DFS is complete. (b) As
tree-like search with cycle checking, it is complete in finite state spaces but not in infinite ones. (c) It is not
cost-optimal. (d) Tree-like DFS takes $O(b^{m})$ time and $O(bm)$ space, where $m$ is the maximum depth.

*Proof.* (a) Graph search expands each state at most once, so in a finite space it stops; when it stops without a
goal, the separation property says no goal is reachable. (b) With cycle checking, every path in the tree is
**simple** (no repeated state), and a finite space has finitely many simple paths, so the search ends; it explores
every simple path from the start unless it finds a goal first, and every reachable goal lies at the end of some
simple path. In an infinite space, DFS can follow an infinite path that never reaches a goal (for instance, always
"drive one more metre east" in an unbounded plane) and never return. (c) Figure 3.4 shows it: DFS reaches the
left subtree first, so if the tree had a goal at depth 3 on the left and another at depth 1 on the right, it would
return the deeper one. On the 8-puzzle below, graph-search DFS finds a solution of 66 056 moves where 20 suffice.
(d) The tree has at most $1 + b + \dots + b^{m} = O(b^{m})$ nodes. At any moment, tree-like DFS stores only the
current path from the root (at most $m$ nodes) and, for each node on it, its not-yet-explored siblings (at most
$b - 1$ each): $O(bm)$ nodes. $\square$

That last line is DFS's great virtue. With $b = 10$ and $m = 16$, BFS would need 11 exabytes; tree-like DFS needs
about 160 nodes, a few hundred kilobytes. Its vices are incompleteness and non-optimality. If $m$ is much larger
than $d$, its time $O(b^{m})$ is also far worse than BFS's. The next two strategies keep the virtue and remove the
vices.

### Depth-limited search

**Depth-limited search** (DLS) is DFS that treats nodes at depth $\ell$ as if they had no successors. It returns
one of three results: a solution; **failure**, meaning there is no solution at all; or **cutoff**, meaning there was
no solution within depth $\ell$ but the limit was hit somewhere, so a deeper solution might exist. Telling failure
from cutoff matters for the next algorithm.

DLS takes $O(b^{\ell})$ time and $O(b\ell)$ space. It is complete if $\ell \ge d$ and incomplete otherwise; it is
not optimal if $\ell > d$. Sometimes a good limit is known: on a map with 9 places, no simple path has more than 8
roads, so $\ell = 8$ is safe. The **diameter** of the state space (the greatest distance between two states) is
the best such limit: 31 for the 8-puzzle, as the program shows. Usually it is not known.

### Iterative deepening search

**Iterative deepening search** (IDS) runs DLS with limit 0, then 1, then 2, and so on, until a run does not return
cutoff. That looks wasteful: the top of the tree is searched again and again. It is not, and here is the proof.

**Theorem 3.6 (iterative deepening).** With finite $b$ and unit action costs, IDS is complete and returns a
solution with the fewest actions. It generates

$$
N_{\text{IDS}} = d\,b + (d-1)\,b^2 + \dots + 2\,b^{d-1} + 1\,b^{d}
$$

nodes in the worst case, which is $O(b^{d})$, and stores $O(bd)$ nodes. As $d$ grows, $N_{\text{IDS}}$ divided by the
number of nodes of one breadth-first pass, $N_{\text{BFS}} = b + b^2 + \dots + b^{d}$, tends to $b/(b - 1)$.

*Proof.* *Correctness.* DLS with limit $\ell$ searches every simple path of length at most $\ell$ (cycle checking
removes only paths that repeat a state, and a shortest solution never does). So it finds a goal if and only if one
lies within depth $\ell$. The runs with limits $0, 1, \dots, d - 1$ find no goal and return cutoff (the tree goes
deeper, since a goal exists at depth $d$); the run with limit $d$ finds a goal, at depth exactly $d$ because nothing
shallower exists. So IDS returns a solution with $d$ actions, the minimum. It never stops early with failure,
because failure is returned only when the whole tree is shallower than the limit.

*Time.* In the run with limit $\ell$, the nodes at depth $i \le \ell$ are generated once. A node at depth $i$ is
generated in the runs with limits $i, i+1, \dots, d$, that is $d + 1 - i$ times, and there are at most $b^{i}$ of
them; this gives the formula. To compare it with $b^{d}$, put $j = d - i$:

$$
N_{\text{IDS}} = \sum_{i=1}^{d} (d + 1 - i)\, b^{i} = b^{d} \sum_{j=0}^{d-1} (j + 1)\, b^{-j} < b^{d} \sum_{j=0}^{\infty} (j+1) x^{j} = \frac{b^{d}}{(1 - x)^{2}}, \quad x = \frac{1}{b},
$$

using the series $\sum_{j \ge 0} (j+1) x^{j} = 1/(1-x)^2$ for $|x| < 1$ (differentiate the geometric series). So
$N_{\text{IDS}} < b^{d} \cdot b^2/(b-1)^2 = O(b^{d})$. Meanwhile $N_{\text{BFS}} = b^{d} \sum_{j=0}^{d-1} b^{-j}$,
which tends to $b^{d} \cdot b/(b-1)$. The ratio of the two limits is $\frac{b^2/(b-1)^2}{b/(b-1)} = \frac{b}{b-1}$.

*Space.* Each run is a DLS, using $O(b\ell) \le O(bd)$ memory, and nothing is kept between runs. $\square$

For $b = 10$ and $d = 5$: $N_{\text{IDS}} = 50 + 400 + 3000 + 20\,000 + 100\,000 = 123\,450$, against
$N_{\text{BFS}} = 111\,110$, only 11 percent more. The program confirms the ratios for several $b$ and $d$:

```
nodes generated: IDS against BFS (complete tree, branching b, depth d)
  b =  2, d = 10: IDS          4,072  BFS          2,046  ratio 1.990  (b/(b-1) = 2.000)
  b =  3, d =  8: IDS         14,748  BFS          9,840  ratio 1.499  (b/(b-1) = 1.500)
  b = 10, d =  5: IDS        123,450  BFS        111,110  ratio 1.111  (b/(b-1) = 1.111)
  b = 10, d = 10: IDS 12,345,679,000  BFS 11,111,111,110  ratio 1.111  (b/(b-1) = 1.111)
```

The reason is that in an exponentially growing tree, almost all nodes are in the bottom layer; repeating the
smaller layers above costs little. IDS is the preferred uninformed method when the search space is larger than
memory and the depth of the solution is not known.

One honest caveat, visible in the 8-puzzle measurements of 3.5. The ratio $b/(b-1)$ compares IDS with a breadth-first
*tree* search. Graph-search BFS is smarter: it never expands a state twice. In a state space with many redundant
paths, the tree of simple paths can be far bigger than the graph of states, and then IDS loses to graph-search BFS
by much more than $b/(b-1)$. That is the price of its tiny memory.

### Summary of the strategies

| Criterion | BFS | Uniform-cost | DFS | Depth-limited | Iterative deepening | Bidirectional (BFS) |
|---|---|---|---|---|---|---|
| Complete? | yes (1) | yes (1, 2) | no (3) | no | yes (1) | yes (1, 4) |
| Cost-optimal? | yes (5) | yes | no | no | yes (5) | yes (4, 5) |
| Time | $O(b^{d})$ | $O(b^{1+\lfloor C^*/\varepsilon\rfloor})$ | $O(b^{m})$ | $O(b^{\ell})$ | $O(b^{d})$ | $O(b^{d/2})$ |
| Space | $O(b^{d})$ | $O(b^{1+\lfloor C^*/\varepsilon\rfloor})$ | $O(bm)$ | $O(b\ell)$ | $O(bd)$ | $O(b^{d/2})$ |

Notes: (1) if $b$ is finite and the state space either has a solution or is finite; (2) if every action cost is at
least $\varepsilon > 0$; (3) complete in finite spaces as graph search, or with cycle checking; (4) if both
directions are breadth-first or uniform-cost; (5) if all action costs are equal.

<figure class="play" data-play="bfsdfs"><span class="ai-tag">AI-created</span><figcaption>Try it: the same maze searched breadth-first and depth-first. Watch the order each one visits the squares.</figcaption></figure>

## 3.4 Bidirectional search

*Level: intermediate.*

If BFS from the start must reach depth $d$, two breadth-first searches, one forward from the start and one backward
from the goal, each need only reach depth about $d/2$ before they meet. The saving is enormous: $2 b^{d/2}$ is much
smaller than $b^{d}$. With $b = 10$ and $d = 10$, that is $2 \times 10^{5}$ nodes against $10^{10}$.

<figure class="mars-fig" markdown="0">
<svg viewBox="0 0 600 240" role="img" aria-label="Left: one large circle of radius d around the start reaching the goal. Right: two small circles of radius d over 2, one around the start and one around the goal, touching in the middle.">
  <circle cx="130" cy="110" r="95" fill="#9cc9ea" fill-opacity="0.35" stroke="currentColor"/>
  <circle cx="130" cy="110" r="5" fill="currentColor"/>
  <circle cx="225" cy="110" r="5" fill="#7ccf9a" stroke="currentColor"/>
  <text x="120" y="102" font-size="12" text-anchor="middle" fill="currentColor">start</text>
  <text x="225" y="130" font-size="12" text-anchor="middle" fill="currentColor">goal</text>
  <line x1="130" y1="110" x2="222" y2="110" stroke="currentColor" stroke-dasharray="4 3"/>
  <text x="178" y="124" font-size="12" text-anchor="middle" fill="currentColor">d</text>
  <text x="130" y="230" font-size="12" text-anchor="middle" fill="currentColor">one search: about b^d nodes</text>
  <circle cx="395" cy="110" r="48" fill="#9cc9ea" fill-opacity="0.35" stroke="currentColor"/>
  <circle cx="490" cy="110" r="48" fill="#7ccf9a" fill-opacity="0.35" stroke="currentColor"/>
  <circle cx="395" cy="110" r="5" fill="currentColor"/>
  <circle cx="490" cy="110" r="5" fill="#7ccf9a" stroke="currentColor"/>
  <text x="395" y="102" font-size="12" text-anchor="middle" fill="currentColor">start</text>
  <text x="490" y="102" font-size="12" text-anchor="middle" fill="currentColor">goal</text>
  <text x="442" y="52" font-size="11" text-anchor="middle" fill="currentColor">they meet</text>
  <line x1="442" y1="56" x2="442" y2="104" stroke="currentColor" stroke-opacity="0.6"/>
  <text x="442" y="230" font-size="12" text-anchor="middle" fill="currentColor">two searches: about 2 b^(d/2) nodes</text>
</svg>
<figcaption>Figure 3.5. Why bidirectional search pays. In a space where the number of states within distance $r$
grows like $b^{r}$, two searches of radius $d/2$ touch far sooner than one search of radius $d$ reaches the
goal.</figcaption>
</figure>

Three things are needed. First, a **single, known goal state** (or a small set), to start the backward search
from; "checkmate" describes a huge set of positions and is hard to search backward from. Second, the ability to
compute **predecessors**: the states from which an action leads to a given state. In the 8-puzzle and on an
undirected map, every action can be undone, so predecessors are just successors. Third, a correct **stopping rule**,
which is where people go wrong.

Our version expands one *whole layer* at a time, on whichever side has the smaller frontier, and stops after the
first layer in which a newly generated state has already been reached by the other side.

**Theorem 3.7 (layered bidirectional BFS).** With unit costs and reversible actions, layered bidirectional BFS
returns a path with the fewest actions. If both sides grow to radius about $d/2$, it generates $O(b^{d/2})$ nodes.

*Proof.* Suppose that before a layer is expanded, the forward search has reached exactly the states within
distance $r_f$ of the start, with their correct distances, and the backward search those within distance $r_b$ of
the goal (each side is a BFS, so Theorem 3.3 gives this), and no state has been reached by both. Let $d$ be the
length of a shortest solution. Then $d > r_f + r_b$: otherwise the state at distance $\min(r_f, d)$ from the start
along a shortest path would be within $r_f$ of the start and within $d - \min(r_f, d) \le r_b$ of the goal, so
reached by both.

Now say the forward side expands its layer (the backward case is symmetric). Every state it generates newly is at
distance exactly $r_f + 1$ from the start. If such a state $s$ was reached by the backward search, the path through
$s$ has length $(r_f + 1) + \delta_b(s) \le r_f + 1 + r_b \le d$, where $\delta_b(s) \le r_b$ is its distance to
the goal; as no solution is shorter than $d$, its length is exactly $d$. So any meeting found in this layer gives an
optimal path, and taking the best of them is safe. Conversely, if $d = r_f + 1 + r_b'$ for some $r_b' \le r_b$, the
state at distance $r_f + 1$ along a shortest path is generated in this layer and has been reached backwards, so
the meeting is found as soon as it is possible. For the cost: each side generates the states within its radius, and
the two radii add up to about $d$; balancing them (always growing the smaller frontier) keeps each near $d/2$, for
$O(b^{d/2})$ nodes per side. $\square$

**The trap.** It is tempting to stop the moment *any* state is reached by both sides, in the middle of a layer, and
return the path through it. With unit costs and whole layers, as above, this is safe. With varied costs it is not:
the first state settled by both searches need not lie on a shortest path. The correct rule for uniform-cost
bidirectional search keeps the best meeting cost $\mu$ seen so far and stops only when the two smallest frontier
keys add up to at least $\mu$. It is proved in
[Section 16.6 of the Algorithms book](../algorithms/16-Shortest-Paths.md#166-a-search-and-bidirectional-search),
and is not repeated here.

On the 8-puzzle instance, layered bidirectional BFS generated 2670 nodes, against 106 576 for BFS, a factor of 40.
Bidirectional search was first studied by Ira Pohl, whose 1971 paper also raised the question of how to combine it
with heuristics, a question that took decades to settle well.

## 3.5 Code: one generic search for all

How much code do six algorithms need? Very little, if it is organised around the one idea of this chapter: the
order of the frontier. The program below has three parts.

1. **Problems.** A `Problem` class with `actions`, `result`, `is_goal` and `action_cost`; subclasses for the
   missionaries and cannibals, routes on the Mars map and the 8-puzzle. (There is also a method `h`, returning 0,
   for Chapter 4.)
2. **One generic graph search**, `graph_search(problem, frontier, ...)`. It keeps the `reached` table and the
   loop of 3.2; it skips stale entries (nodes whose state has since been reached more cheaply). Pass a FIFO queue and
   it is BFS; a LIFO stack, DFS; a priority queue on $g$, uniform-cost search; and in Chapter 4, a priority queue on
   $g + h$, A\*.
3. **The depth-first family and bidirectional search,** written separately because they keep different memory:
   `depth_limited` keeps only the current path, `iterative_deepening` calls it with growing limits, and
   `bidirectional_bfs` keeps two reached tables.

Every algorithm counts nodes generated, nodes expanded and the largest frontier, so the theorems of 3.3 can be
checked against reality. (For depth-limited search, the "frontier" column reports the deepest recursion, the length
of the current path.)

```python
--8<-- "books/ai/ch03_search.py"
```

Output:

```
Missionaries and cannibals, breadth-first:
  11 crossings; BFS: generated 28, expanded 13, max frontier 3
    MMMCCC | boat left  |         -> carry CC
      MMMC | boat right | CC      -> carry C
     MMMCC | boat left  | C       -> carry CC
       MMM | boat right | CCC     -> carry C
      MMMC | boat left  | CC      -> carry MM
        MC | boat right | MMCC    -> carry MC
      MMCC | boat left  | MC      -> carry MM
        CC | boat right | MMMC    -> carry C
       CCC | boat left  | MMM     -> carry CC
         C | boat right | MMMCC   -> carry M
        MC | boat left  | MMCC    -> carry MC
           | boat right | MMMCCC

Routes from Olympus Mons to Jezero crater:
  BFS: Olympus Mons > Gale crater > Jezero crater
       2 roads, 9119 km; generated 11, expanded 4
  UCS: Olympus Mons > Erebus Montes > Utopia Planitia > Jezero crater
       3 roads, 7888 km; generated 19, expanded 7
  DFS: Olympus Mons > Gale crater > Jezero crater
       2 roads, 9119 km; generated 7, expanded 2

8-puzzle from (7, 2, 4, 5, 0, 6, 8, 3, 1) (solvable: True):
  algorithm       moves  generated  expanded  max frontier
  BFS                20     106576     39278         16130
  UCS                20     161168     60473         19384
  IDS                20     800221    292708            20
  bidirectional      20       2670       957           486
  DFS (graph)     66056     269224     99899         42912
```

Read the results against the theory.

- **Missionaries and cannibals.** BFS finds the classic 11-crossing solution after expanding 13 nodes; the space is
  tiny (16 reachable states), so any complete method works. The key moment is the fifth crossing: after four crossings that
  shuttle cannibals, two of them wait on the far bank, and now two missionaries go over together.
- **Routes.** BFS minimises the number of roads (2) and gets 9119 km; UCS minimises kilometres and gets 7888 km by
  a route with one more road, after the 7 expansions traced by hand in 3.3. DFS happens to find the same route as
  BFS here, by luck of the order in which neighbours are listed (alphabetical); exercise 4 asks you to change the
  order.
- **8-puzzle, optimal methods.** BFS, UCS and IDS all find 20 moves, as Theorems 3.3, 3.4 and 3.6 promise. UCS
  generates about 50 percent more nodes than BFS because of the late goal test (it expands the depth-20 layer up to
  the goal). IDS keeps at most 20 nodes on its path, against BFS's frontier of 16 130 plus its table of every
  reached state, but generates 7.5 times as many nodes. The overhead has two parts. Its tree's layers grew by a
  factor of about 1.8 per level (instrumenting the runs, the limit-18 and limit-19 iterations expanded 51 765 and
  93 333 nodes), so the repetition factor $b/(b-1)$ is about 2.25; the rest is redundancy, many different simple
  paths leading to the same state, which graph search never repeats.
- **Bidirectional BFS** generates 2670 nodes, 40 times fewer than BFS.
- **DFS as graph search** finds a solution of 66 056 moves. It is complete (it found one) and spectacularly
  non-optimal: it expanded more than half of the reachable states (99 899 of 181 440) before stumbling on the goal.

The second program measures the whole 8-puzzle space, and prints the tables quoted in 3.3:

```python
--8<-- "books/ai/ch03_space.py"
```

Output:

```
8-puzzle: 181440 states reachable from the goal; 9! = 362880
  states at each distance from the goal:
     0:     1   1:     2   2:     4   3:     8   4:    16   5:    20   6:    39   7:    62
     8:   116   9:   152  10:   286  11:   396  12:   748  13:  1024  14:  1893  15:  2512
    16:  4485  17:  5638  18:  9529  19: 10878  20: 16993  21: 17110  22: 23952  23: 20224
    24: 24047  25: 15578  26: 14560  27:  6274  28:  3910  29:   760  30:   221  31:     2
  the farthest states (31 moves): [(8, 6, 7, 2, 5, 4, 3, 0, 1), (6, 4, 7, 8, 5, 0, 3, 2, 1)]
  reachable exactly when the inversion parity matches the goal: True

breadth-first search with b = 10, 1 million nodes per second, 1 kilobyte per node:
  depth  2:                    111 nodes, 0.000111 seconds,    111 kB
  depth  4:                 11,111 nodes,   0.0111 seconds,   11.1 MB
  depth  6:              1,111,111 nodes,     1.11 seconds,   1.11 GB
  depth  8:            111,111,111 nodes,      111 seconds,    111 GB
  depth 10:         11,111,111,111 nodes,       3.09 hours,   11.1 TB
  depth 12:      1,111,111,111,111 nodes,        309 hours,   1.11 PB
  depth 14:    111,111,111,111,111 nodes,       3.52 years,    111 PB
  depth 16: 11,111,111,111,111,111 nodes,        352 years,   11.1 EB

nodes generated: IDS against BFS (complete tree, branching b, depth d)
  b =  2, d = 10: IDS          4,072  BFS          2,046  ratio 1.990  (b/(b-1) = 2.000)
  b =  3, d =  8: IDS         14,748  BFS          9,840  ratio 1.499  (b/(b-1) = 1.500)
  b = 10, d =  5: IDS        123,450  BFS        111,110  ratio 1.111  (b/(b-1) = 1.111)
  b = 10, d = 10: IDS 12,345,679,000  BFS 11,111,111,110  ratio 1.111  (b/(b-1) = 1.111)
```

The layer counts tell a story of their own. Up to depth 4 they double ($1, 2, 4, 8, 16$): every move from the goal
leads somewhere new. Then growth slows to a factor of about 1.5 per layer, because paths start to meet each other;
the counts peak at depths 22 to 24 and fall off to the two farthest states at depth 31. Our start state is one of the
16 993 states at depth 20. A random solvable state is most likely to be 22 to 24 moves
from the goal.

### A short history

Search as a method of problem solving goes back to the first AI programs: Newell and Simon's Logic Theorist and GPS
(Chapter 1) searched spaces of proof steps and problem states. Breadth-first search for shortest paths in mazes was
described by E. F. Moore in 1959, and Dijkstra's algorithm, of which uniform-cost search is the implicit-graph form,
by Edsger Dijkstra the same year. The formulation of problems as states, operators and goals, and the influence of
representation on difficulty, were studied by Saul Amarel in the 1960s, notably with the missionaries and cannibals.
Iterative deepening was used in game-playing programs in the 1970s (the chess program CHESS 4.5 of Slate and Atkin,
1977) and was analysed for single-agent search by Richard Korf in 1985, who proved it asymptotically optimal among
brute-force tree searches in time, space and solution length. Ira Pohl studied bidirectional search around 1970.
The 15-puzzle was a popular craze around 1880; W. W. Johnson and W. E. Story proved in 1879 that half of its
arrangements cannot be solved, the argument of Theorem 3.1. Ratner and Warmuth showed in 1986 that finding
shortest solutions of the general $n \times n$ puzzle is NP-hard, so no polynomial-time method is expected
([Chapter 22 of the Algorithms book](../algorithms/22-NP-Completeness.md)).

## Check yourself

??? question "1. Formulate the 'jugs' problem as a search problem: with a 4-litre jug and a 3-litre jug and a tap, measure exactly 2 litres. Give the states, actions and goal, and find a solution by hand."

    States: $(x, y)$, the litres in the 4-litre and 3-litre jugs, $0 \le x \le 4$, $0 \le y \le 3$ (20 states).
    Initial state $(0, 0)$. Actions: fill either jug, empty either jug, pour one into the other until the source
    is empty or the target is full. Goal: $x = 2$ or $y = 2$. A solution: fill the 3 $(0,3)$; pour into the 4
    $(3,0)$; fill the 3 $(3,3)$; pour into the 4 until full $(4,2)$. Four actions, and the 3-litre jug holds 2.
    BFS would confirm that no shorter solution exists (exercise 9 runs it).

??? question "2. Count the inversions of the 8-puzzle state (8, 1, 3, 4, 0, 2, 7, 6, 5). Is it solvable (with the goal of this chapter)?"

    Tiles in order: 8, 1, 3, 4, 2, 7, 6, 5. Inversions: 8 before all seven others (7); 1 before none (0); 3
    before 2 (1); 4 before 2 (1); 2 before none (0); 7 before 6 and 5 (2); 6 before 5 (1). Total
    $7 + 1 + 1 + 2 + 1 = 12$, even. So it is solvable: by the program's check, the even-parity states are exactly the reachable
    ones. The function `solvable((8, 1, 3, 4, 0, 2, 7, 6, 5))` returns True.

??? question "3. In the 15-puzzle (4 × 4), an up or down move jumps a tile over three others, not two. Does Theorem 3.1's invariant still hold? What is the correct invariant?"

    Moving a tile past three others changes the inversion count by an odd amount ($\pm 1$ or $\pm 3$), so the
    parity of inversions alone is *not* invariant. But each vertical move also changes the blank's row by one. So
    the parity of (inversions + row of the blank) is invariant: horizontal moves change neither; vertical moves
    change both by odd amounts, keeping the sum's parity. A state is solvable exactly when this sum has the same
    parity as in the goal. This is the form in which Johnson and Story's 1879 result is usually stated.

??? question "4. In the route program the neighbours of each place are sorted alphabetically. If instead they were sorted in reverse, what route would graph-search DFS find from Olympus Mons to Jezero crater? Is it optimal?"

    The stack pops the child pushed last. With alphabetical order, Olympus Mons pushes Ascraeus, Erebus, Gale;
    Gale is popped first and pushes Elysium, Hellas, Jezero; Jezero is popped next: 2 roads, 9119 km. With
    reversed order, Olympus pushes Gale, Erebus, Ascraeus. Ascraeus is popped and pushes Valles Marineris, a dead
    end. Then Erebus is popped and pushes Utopia and Elysium (Olympus is already reached). Elysium is popped, but
    its neighbours Utopia, Gale and Erebus are all reached already, so it adds nothing. Utopia is popped and pushes
    Jezero, which is popped and is the goal. Route: Olympus Mons, Erebus Montes, Utopia Planitia, Jezero crater,
    7888 km. That happens to be optimal, but only by luck: DFS makes no attempt to minimise cost, and the order of
    a list decided the answer. Running `depth_first` after `self.adj[p].sort(reverse=True)` prints this route.

??? question "5. Prove that uniform-cost search is not complete if zero-cost actions are allowed, even with a finite branching factor."

    Take an infinite chain of states $s_0, s_1, s_2, \dots$ with $s_i \to s_{i+1}$ of cost 0, and a single action
    $s_0 \to G$ of cost 1. UCS expands $s_0$ ($g = 0$), generating $s_1$ ($g = 0$) and $G$ ($g = 1$). Then it
    always prefers the next chain state with $g = 0$ to $G$ with $g = 1$, and expands $s_1, s_2, \dots$ forever.
    The branching factor is 2, but there are infinitely many nodes with $g < C^{*} = 1$, which is exactly what the
    condition $\varepsilon > 0$ rules out.

??? question "6. For $b = 3$ and $d = 4$, compute the number of nodes IDS generates and the number BFS generates (without the root), and check the ratio against $b/(b-1)$."

    $N_{\text{IDS}} = 4 \cdot 3 + 3 \cdot 9 + 2 \cdot 27 + 1 \cdot 81 = 12 + 27 + 54 + 81 = 174$.
    $N_{\text{BFS}} = 3 + 9 + 27 + 81 = 120$. Ratio $174/120 = 1.45$, below the limit $3/2 = 1.5$, which is
    approached as $d$ grows (the program shows 1.499 for $d = 8$).

??? question "7. Why can BFS use an early goal test but uniform-cost search cannot? Give the property that makes it safe for BFS."

    BFS generates nodes in non-decreasing order of depth, and with unit costs depth equals path cost. So when a
    goal node is generated at depth $d$, every node that will be generated later has depth at least $d$ (in fact
    at least the current depth), and no cheaper goal can appear. UCS generates nodes in no particular order of
    cost: a child generated now can be much more expensive than nodes generated later, as in the example $S \to G$
    (10) versus $S \to A \to G$ (1 + 1). What UCS has instead is that it *expands* nodes in non-decreasing order
    of $g$, so the goal test must wait until expansion.

??? question "8. Trace layered bidirectional BFS, as coded in `bidirectional_bfs`, on the path graph 1 - 2 - 3 - 4 - 5 - 6 from 1 to 6. Where do the searches meet? What does this say about tie-breaking?"

    Both frontiers start with one state, {1} and {6}. The code grows the forward side when the sizes are equal, and
    on a path every layer has one state, so the sizes are always equal: the forward side generates 2, then 3, 4, 5
    and finally 6, which the backward side has reached. The path 1, 2, 3, 4, 5, 6 (5 moves) is correct, as Theorem
    3.7 promises, but the backward search never grew: it was plain BFS, with 5 expansions. With alternation on
    ties (forward generates 2, backward 5, forward 3, backward 4), the backward layer {4} would meet the forward
    side after 4 expansions, about $d/2$ on each side. The lesson: the correctness of the layered rule does not
    depend on which side grows, but the $b^{d/2}$ saving does. On bushy spaces such as the 8-puzzle the frontiers
    rarely tie, so "grow the smaller" balances them by itself.

??? question "9. Write code: solve the jugs problem of exercise 1 with the chapter's generic search, by BFS and by DFS."

    ```python
    from ch03_search import Problem, breadth_first, depth_first, path_states

    class Jugs(Problem):
        CAP = (4, 3)

        def __init__(self):
            super().__init__((0, 0))

        def is_goal(self, s):
            return 2 in s

        def actions(self, s):
            return ["fill0", "fill1", "empty0", "empty1", "pour01", "pour10"]

        def result(self, s, a):
            x = list(s)
            if a.startswith("fill"):
                i = int(a[-1]); x[i] = self.CAP[i]
            elif a.startswith("empty"):
                x[int(a[-1])] = 0
            else:
                i, j = int(a[-2]), int(a[-1])
                t = min(x[i], self.CAP[j] - x[j])
                x[i] -= t; x[j] += t
            return tuple(x)

    for fn in (breadth_first, depth_first):
        node, st = fn(Jugs())
        print(fn.__name__, path_states(node), st)
    ```

    Output:

    ```
    breadth_first [(0, 0), (0, 3), (3, 0), (3, 3), (4, 2)] BFS: generated 48, expanded 8, max frontier 3
    depth_first [(0, 0), (0, 3), (3, 0), (3, 3), (4, 2)] DFS: generated 24, expanded 4, max frontier 3
    ```

    BFS finds the 4-action solution of exercise 1 and, by Theorem 3.3, no shorter one exists. DFS finds the same
    solution with fewer nodes, because the last action in the list, "pour10", happens to lead straight down a good
    branch; with another order of actions it could find a longer one. Note that `is_goal` is overridden: here the
    goal is a *set* of states, not one state.

??? question "10. A state space has $b = 10$ and a solution at depth $d = 12$. Roughly how many nodes would BFS, IDS and bidirectional BFS generate? Which would you choose with 16 GB of memory and 1 kilobyte per node?"

    BFS: about $b^{d} = 10^{12}$ nodes (more precisely $1.11 \times 10^{12}$); memory about a petabyte, impossible.
    IDS: about $b/(b-1)$ times that, $1.2 \times 10^{12}$ nodes, but memory only $bd = 120$ nodes. At a million
    nodes a second that is about two weeks of computing. Bidirectional BFS: about $2 \times 10^{6}$ nodes, which
    needs about 2 GB and takes seconds. With 16 GB, bidirectional search is the clear choice, provided the goal
    state is known and predecessors can be computed; otherwise IDS is the only option that fits in memory, and a
    heuristic (Chapter 4) is badly needed.

??? question "11. The program's DFS solution for the 8-puzzle has 66 056 moves, but the state space has only 181 440 states and diameter 31. Explain why DFS's path is so long, and why it is still a valid solution."

    Graph-search DFS always extends the most recently generated node, and never revisits a state. So it builds
    one long path that winds through the state space, backing up only when every neighbour of the current state
    has already been reached. Each state on its final path is distinct, so the path is a simple path through
    66 057 distinct states, about a third of the space. It is valid because every step is a legal move and it
    ends at the goal; it is just very far from the 20-move optimum. The diameter (31) bounds the *shortest* path
    between any two states, not the paths DFS happens to build.

## What you learned

- A search problem has states, an initial state, actions, a transition model, a goal test and action costs; a good
  abstraction keeps only what the solution needs.
- Search grows a tree of nodes (paths) over the graph of states; graph search keeps a reached table so each state
  is expanded once; the frontier separates expanded states from unreached ones.
- BFS (FIFO) is complete and finds the fewest actions in $O(b^{d})$ time and space; uniform-cost search (priority
  on $g$) is optimal for any positive costs in $O(b^{1+\lfloor C^*/\varepsilon\rfloor})$; DFS (LIFO) needs only
  $O(bm)$ memory but is neither complete in infinite spaces nor optimal.
- Iterative deepening combines DFS's memory with BFS's guarantees, at a cost of only about $b/(b-1)$ times BFS's
  nodes on a tree; bidirectional search cuts the cost to about $b^{d/2}$ when the goal is known and actions can be
  reversed, with a careful stopping rule.
- The 8-puzzle has $9!/2 = 181\,440$ reachable states (a parity invariant forbids the rest) and diameter 31; on our
  20-move instance BFS generated 106 576 nodes, IDS 800 221, bidirectional BFS 2670.
- One generic search loop, with the frontier as a parameter, implements all of these.

**Next:** [Chapter 4](04-Heuristic-Search.md) gives search a sense of direction: heuristic estimates of the
distance to the goal, greedy best-first search and A\*, with the proof that A\* is optimal.

## Further reading

- S. Russell and P. Norvig, *Artificial Intelligence: A Modern Approach*, 4th ed., Pearson, 2020, Chapter 3
  (problem formulation, uninformed search, the 8-puzzle, the comparison of strategies).
- R. E. Korf, "Depth-first iterative-deepening: an optimal admissible tree search", *Artificial Intelligence* 27(1),
  1985.
- E. F. Moore, "The shortest path through a maze", *Proceedings of the International Symposium on the Theory of
  Switching*, Harvard University Press, 1959.
- E. W. Dijkstra, "A note on two problems in connexion with graphs", *Numerische Mathematik* 1, 1959.
- I. Pohl, "Bi-directional search", *Machine Intelligence* 6, 1971.
- S. Amarel, "On representations of problems of reasoning about actions", *Machine Intelligence* 3, 1968.
- W. W. Johnson and W. E. Story, "Notes on the '15' puzzle", *American Journal of Mathematics* 2(4), 1879.
- D. Ratner and M. Warmuth, "Finding a shortest solution for the N × N extension of the 15-puzzle is
  intractable", AAAI 1986.
- J. Pearl, *Heuristics: Intelligent Search Strategies for Computer Problem Solving*, Addison-Wesley, 1984.
- T. H. Cormen, C. E. Leiserson, R. L. Rivest and C. Stein, *Introduction to Algorithms*, 4th ed., MIT Press, 2022,
  Chapters 20 and 22 (graph search and shortest paths on explicit graphs).
- On this site: [Breadth-first search](../../graphs/bfs.md), [Depth-first search](../../graphs/dfs.md),
  [Dijkstra's algorithm](../../graphs/dijkstra.md), [Stacks and queues](../../data-structures/stack-queue.md),
  [Binary heap](../../data-structures/binary-heap.md), and Chapters
  [15](../algorithms/15-Graphs-and-Graph-Search.md) and [16](../algorithms/16-Shortest-Paths.md) of the Algorithms
  book.
