# 10. Automated planning

*A rover must drive to a delta, drill a rock, take pictures, send them home and park before dark. The search
algorithms of Chapters 3 and 4 could find that sequence of actions, if someone wrote a successor function and a
heuristic by hand for this one problem. Planning asks for more: a single language in which any such problem can be
written down, and general algorithms that read the description and find a plan, with heuristics computed automatically
from the description itself. In this chapter you will learn the STRIPS and PDDL languages, plan forwards and backwards,
derive heuristics by ignoring delete lists, build a partial-order planner and GraphPlan from scratch, decompose tasks
hierarchically, schedule activities under a power limit, and see how planners have flown on real spacecraft.*

!!! abstract "In this chapter"
    **You will learn:**

    - how STRIPS and PDDL describe states, actions and goals, and why a factored description beats a hand-written
      successor function
    - forward (progression) and backward (regression) state-space planning, with the Sussman anomaly as a warning
    - domain-independent heuristics from the delete relaxation: $h_{\max}$ (admissible, proved), $h_{\mathrm{add}}$ and
      $h_{\mathrm{FF}}$, measured against the true cost
    - partial-order planning with causal links and threats, and GraphPlan with mutexes, both built from scratch
    - hierarchical task networks, the critical path method, and scheduling with a resource limit
    - what the Remote Agent on Deep Space 1 (1999) and Mars rover activity planners did, and why autonomy is needed
      when light takes about 3 to 22 minutes each way

    **You need:** [Chapter 3](03-Uninformed-Search.md) (search, BFS) and [Chapter 4](04-Heuristic-Search.md) (A*,
    admissibility); propositional and first-order atoms from [Chapter 8](08-Propositional-Logic-and-SAT.md) and
    [Chapter 9](09-First-Order-Logic.md). Topological order and longest paths in a DAG from the Algorithms book
    ([Chapter 15](../algorithms/15-Graphs-and-Graph-Search.md), [Chapter 13](../algorithms/13-Dynamic-Programming.md))
    help in 10.5.

    **Levels:** 10.1 and 10.2 are beginner; 10.3 is intermediate (with an advanced proof); 10.4 and 10.5 are
    intermediate; 10.6 is beginner, with facts only.

## 10.1 Planning vs search; STRIPS (Fikes and Nilsson 1971), PDDL

### What planning adds to search

In [Chapter 3](03-Uninformed-Search.md) a problem was a black box: a start state, a function `actions(s)`, a function
`result(s, a)`, a goal test. The search algorithm never looked inside a state. That is an **atomic** representation
([Chapter 2](02-Intelligent-Agents.md)), and it has two costs. Someone must write the functions by hand for each new
problem. And the search cannot reason about *why* a state is good, so the heuristic must be written by hand too.

**Automated planning** uses a **factored** representation: a state is a set of facts, and an action is described by
which facts it needs and which it changes. Because the planner can read those descriptions, it can do things a black-box
search cannot: work backwards from the goal, notice that two goals are independent, notice that one action undoes
another's work, and compute a heuristic automatically by solving a simplified version of the problem. A planner is a
general problem solver for any problem written in its language; the problem is input data, not code.

### STRIPS

The classic language is **STRIPS**, from the Stanford Research Institute Problem Solver of Richard Fikes and Nils Nilsson
(1971). It was written to plan for Shakey, a mobile robot at SRI that pushed boxes between rooms, the first robot to
reason about its own actions.

A STRIPS problem has:

- **States:** a state is a set of ground atoms (facts with no variables), such as `At(Base)`, `On(C,A)`. Any atom not
  in the set is false (the closed-world assumption of [Chapter 9](09-First-Order-Logic.md)).
- **An initial state** and **a goal**: the goal is a set of atoms that must all be true. A state *satisfies* the goal
  when it contains it. Many states may satisfy one goal.
- **Action schemas**, each with a name and parameters, a **precondition** (atoms that must hold before), an **add
  list** (atoms made true) and a **delete list** (atoms made false).

Here is the four-operator **blocks world**, the most studied planning domain. A robot hand moves blocks between a table
and stacks; it holds at most one block.

| action | precondition | add list | delete list |
|---|---|---|---|
| PickUp(x) | Clear(x), OnTable(x), HandEmpty | Holding(x) | Clear(x), OnTable(x), HandEmpty |
| PutDown(x) | Holding(x) | OnTable(x), Clear(x), HandEmpty | Holding(x) |
| Stack(x, y) | Holding(x), Clear(y) | On(x, y), Clear(x), HandEmpty | Holding(x), Clear(y) |
| Unstack(x, y) | On(x, y), Clear(x), HandEmpty | Holding(x), Clear(y) | On(x, y), Clear(x), HandEmpty |

An action $a$ is **applicable** in state $s$ when $\mathrm{pre}(a) \subseteq s$, and then the next state is

$$
\mathrm{result}(s, a) = \big(s \setminus \mathrm{del}(a)\big) \cup \mathrm{add}(a).
$$

Everything not mentioned stays as it was. This is the **STRIPS assumption**, and it is how STRIPS sidesteps the
**frame problem**: in logic, describing an action requires saying not only what changes but also everything that does
not change (moving block A does not change the colour of block B, the position of block C, ...), and writing those
"frame axioms" by hand is hopeless. [Chapter 11](11-Knowledge-Representation.md#113-events-time-and-change-situation-calculus-event-calculus-briefly)
looks at the logical solutions; STRIPS simply builds persistence into the update rule.

A **plan** is a sequence of actions $a_1, \ldots, a_n$, each applicable in the state left by the previous ones, such
that the final state satisfies the goal. An **optimal** plan has the fewest actions (or least total cost, when actions
have costs).

<figure class="mars-fig" markdown="0">
<svg viewBox="0 0 640 200" role="img" aria-label="The Sussman anomaly. Left, the initial state: block C on block A, and block B alone on the table. Right, the goal: A on B on C, a single tower.">
<line x1="30" y1="160" x2="290" y2="160" stroke="currentColor" stroke-width="2"/>
<rect x="70" y="110" width="50" height="50" fill="#9cc9ea" fill-opacity="0.6" stroke="currentColor"/>
<text x="95" y="141" font-size="16" text-anchor="middle" fill="currentColor">A</text>
<rect x="70" y="60" width="50" height="50" fill="#eea66f" fill-opacity="0.6" stroke="currentColor"/>
<text x="95" y="91" font-size="16" text-anchor="middle" fill="currentColor">C</text>
<rect x="190" y="110" width="50" height="50" fill="#7ccf9a" fill-opacity="0.6" stroke="currentColor"/>
<text x="215" y="141" font-size="16" text-anchor="middle" fill="currentColor">B</text>
<text x="160" y="186" font-size="13" text-anchor="middle" fill="currentColor">initial state</text>
<line x1="350" y1="160" x2="610" y2="160" stroke="currentColor" stroke-width="2"/>
<rect x="455" y="110" width="50" height="50" fill="#eea66f" fill-opacity="0.6" stroke="currentColor"/>
<text x="480" y="141" font-size="16" text-anchor="middle" fill="currentColor">C</text>
<rect x="455" y="60" width="50" height="50" fill="#7ccf9a" fill-opacity="0.6" stroke="currentColor"/>
<text x="480" y="91" font-size="16" text-anchor="middle" fill="currentColor">B</text>
<rect x="455" y="10" width="50" height="50" fill="#9cc9ea" fill-opacity="0.6" stroke="currentColor"/>
<text x="480" y="41" font-size="16" text-anchor="middle" fill="currentColor">A</text>
<text x="480" y="186" font-size="13" text-anchor="middle" fill="currentColor">goal: On(A,B) and On(B,C)</text>
<text x="320" y="100" font-size="22" text-anchor="middle" fill="currentColor">→</text>
</svg>
<figcaption>Figure 10.1. The Sussman anomaly (Gerald Sussman, 1973). Either goal alone is easy; achieving them one after
the other, in either order, undoes the first. A correct plan must interleave the work for the two goals.</figcaption>
</figure>

### PDDL

STRIPS has descendants. ADL (Edwin Pednault, 1989) added conditional effects, negative preconditions and typed
variables. In 1998 Drew McDermott and colleagues defined **PDDL**, the Planning Domain Definition Language, for the
first International Planning Competition (held at the AIPS-98 conference), and it became the common language of the
field. A PDDL task comes in two files: a **domain** (types, predicates, action schemas) and a **problem** (objects,
initial state, goal). The blocks-world `Stack` action looks like this:

```text
(define (domain blocks)
  (:predicates (on ?x ?y) (ontable ?x) (clear ?x) (handempty) (holding ?x))
  (:action stack
    :parameters (?x ?y)
    :precondition (and (holding ?x) (clear ?y))
    :effect (and (on ?x ?y) (clear ?x) (handempty)
                 (not (holding ?x)) (not (clear ?y)))))

(define (problem sussman) (:domain blocks)
  (:objects a b c)
  (:init (on c a) (ontable a) (ontable b) (clear c) (clear b) (handempty))
  (:goal (and (on a b) (on b c))))
```

Later versions of PDDL added numeric fluents (quantities such as battery charge), durative actions with start and end
times (PDDL 2.1, Fox and Long, 2003), derived predicates and preferences. Because every planner reads the same files,
domains written for one planner can be run by any other, and a planner's strength can be measured on hundreds of
problems it has never seen.

### Grounding, and how hard planning is

Planners first **ground** the schemas: replace the parameters by every combination of objects, keeping the ground
actions whose static preconditions can hold. The blocks world with three blocks has 3 PickUp, 3 PutDown, 6 Stack and
6 Unstack ground actions. Our code works on ground actions throughout; a schema with $k$ parameters over $n$ objects
gives up to $n^k$ of them, which is why real planners ground carefully.

How hard is planning? Tom Bylander (1994) proved that deciding whether a STRIPS problem has a plan at all is
**PSPACE-complete**. The state is a set of $m$ atoms, so there are $2^m$ states, and plans can be exponentially long
(Towers of Hanoi with $n$ discs needs $2^n - 1$ moves), so planning is in general harder than NP-complete problems such
as SAT ([Algorithms, Chapter 22](../algorithms/22-NP-Completeness.md)). Specific domains are easier: blocks world plan
*existence* is trivial (put everything on the table, then build), and a plan at most twice the optimal length is easy,
but finding an *optimal* blocks-world plan is NP-hard (Gupta and Nau, 1992). Planning is hard in the worst case and
very often easy in practice, which is exactly the situation where good heuristics pay.

## 10.2 Forward (progression) and backward (regression) state-space planning

### Forward search

The most direct planner is a search in the space of states, exactly as in [Chapter 3](03-Uninformed-Search.md), with
the successor function computed from the action descriptions: in state $s$, every ground action with
$\mathrm{pre}(a) \subseteq s$ is applicable, and leads to $\mathrm{result}(s, a)$. This is **progression** (forward)
planning. With breadth-first search and unit action costs it returns optimal plans, and with A* and an admissible
heuristic too.

Its weakness is **irrelevant actions**. In a state of the rover domain below, the rover can drive in any direction,
switch the camera on and off, and photograph whatever it is next to; most of those actions have nothing to do with the
goal. Without a heuristic, forward search tries them all.

### Backward search

**Regression** (backward) planning starts from the goal and asks: what must be true *before* an action, so that the
goal is true *after* it? The nodes of this search are not states but **goal descriptions**: sets of atoms, each
standing for all the states that contain it.

An action $a$ is **relevant** to a goal $g$ if it adds at least one atom of $g$ and deletes none. Then the regression of
$g$ through $a$ is

$$
\mathrm{regress}(g, a) = \big(g \setminus \mathrm{add}(a)\big) \cup \mathrm{pre}(a).
$$

In words: the atoms that $a$ provides no longer need to hold beforehand, but $a$'s precondition does, and the
remaining goals must already hold (since $a$ will not delete them). The search succeeds when it reaches a goal
description contained in the initial state.

*Why this is right.* Suppose a state $s$ contains $\mathrm{regress}(g, a)$. Then $a$ is applicable in $s$ (its
precondition is included). Each atom of $g$ is either added by $a$, or it is in $g \setminus \mathrm{add}(a)$, hence in
$s$, and $a$ does not delete it, so it survives into $\mathrm{result}(s, a)$. So $\mathrm{result}(s, a)$ satisfies
$g$. Conversely, if $a$ is applicable in $s$ and $\mathrm{result}(s, a) \supseteq g$ (and $a$ deletes no atom of $g$),
then $s$ must contain $\mathrm{pre}(a)$ and every atom of $g$ that $a$ does not add. So $\mathrm{regress}(g, a)$ is the
**weakest precondition**: exactly the set of states from which $a$ reaches $g$. By induction on the length of the plan,
backward search finds exactly the plans that forward search finds. $\square$

Regressing $\{\mathit{On}(A,B), \mathit{HandEmpty}\}$ through $\mathit{Stack}(A,B)$ gives $\{\mathit{Holding}(A),
\mathit{Clear}(B)\}$; through $\mathit{PutDown}(C)$ it gives $\{\mathit{On}(A,B), \mathit{Holding}(C)\}$; and
$\mathit{Unstack}(C,A)$ is not relevant, because it deletes $\mathit{HandEmpty}$ (Exercise 2).

Backward search only considers relevant actions, so its branching factor is often smaller. Its weakness is that goal
descriptions can be **impossible**: regression happily produces $\{\mathit{Holding}(A), \mathit{Holding}(B)\}$ or
$\{\mathit{At}(Rim), \mathit{At}(Fan)\}$, sets that no state contains, and then searches backwards from them in vain.
Our program prunes these with a hand-written consistency check (one block in the hand, one place for the rover). Real
planners compute such **mutex** facts automatically, for instance from the planning graph of 10.4. Because good
heuristics are easier to compute for states than for sets of states, most modern planners search forwards.

### One goal at a time fails: the Sussman anomaly

An obvious idea is to split a conjunctive goal and solve each part separately, one after the other. Early planners did
this, and Figure 10.1 shows the problem that defeated them. The program solves each goal with breadth-first search, in
order, without protecting the goals already achieved:

```
1. The Sussman anomaly: C on A; A and B on the table.  Goal: On(A,B) and On(B,C).
  goals in order ['On(A,B)', 'On(B,C)']: 8 actions, all goals true at the end: False
  goals in order ['On(B,C)', 'On(A,B)']: 8 actions, all goals true at the end: False
  planning for both goals together: 6 actions: Unstack(C,A), PutDown(C), PickUp(B), Stack(B,C), PickUp(A), Stack(A,B)
```

Achieve $\mathit{On}(A,B)$ first (move C off A, stack A on B) and to put B on C you must take A off B again. Achieve
$\mathit{On}(B,C)$ first (stack B on C) and to free A you must take C, and therefore B, off it. Each order *clobbers*
the goal achieved first. The correct 6-step plan interleaves the two: clear A (a step toward goal 1), build B on C
(goal 2), then A on B (goal 1). Gerald Sussman described the problem in his 1973 MIT thesis on the HACKER program, and
it pushed planning toward methods that treat goals together, as all the planners in this chapter do.

### The program on four problems

The program `ch10_strips.py` (listed in [10.3](#the-strips-planning-program)) runs breadth-first forward search,
A* with two relaxed heuristics, greedy best-first search, and breadth-first backward search on four problems: the
Sussman anomaly; reversing a tower of five blocks; rearranging six blocks from two towers into one; and a **rover day**.
In the rover domain the rover starts at its base; there are five places linked as in Figure 10.2; it can drive along a
link, sample a rock where there is one and cache the sample tube, photograph its location if the camera is on, and send
a picture once its antenna is deployed, which needs the camera off (a stand-in for a power constraint). The goal is to
cache samples from Ridge and Delta, send pictures of Delta and Fan, and be parked at Base.

<figure class="mars-fig" markdown="0">
<svg viewBox="0 0 640 210" role="img" aria-label="The rover domain map. Base links to Rim. Rim links to Delta and to Ridge. Delta links to Fan, and Ridge links to Fan. Rocks to sample lie at Delta, Ridge and Fan.">
<line x1="80" y1="105" x2="230" y2="105" stroke="currentColor" stroke-width="2"/>
<line x1="230" y1="105" x2="390" y2="45" stroke="currentColor" stroke-width="2"/>
<line x1="230" y1="105" x2="390" y2="165" stroke="currentColor" stroke-width="2"/>
<line x1="390" y1="45" x2="550" y2="105" stroke="currentColor" stroke-width="2"/>
<line x1="390" y1="165" x2="550" y2="105" stroke="currentColor" stroke-width="2"/>
<circle cx="80" cy="105" r="28" fill="#7ccf9a" fill-opacity="0.5" stroke="currentColor"/>
<text x="80" y="110" font-size="13" text-anchor="middle" fill="currentColor">Base</text>
<circle cx="230" cy="105" r="28" fill="#9cc9ea" fill-opacity="0.5" stroke="currentColor"/>
<text x="230" y="110" font-size="13" text-anchor="middle" fill="currentColor">Rim</text>
<circle cx="390" cy="45" r="28" fill="#eea66f" fill-opacity="0.5" stroke="currentColor"/>
<text x="390" y="50" font-size="13" text-anchor="middle" fill="currentColor">Delta</text>
<circle cx="390" cy="165" r="28" fill="#eea66f" fill-opacity="0.5" stroke="currentColor"/>
<text x="390" y="170" font-size="13" text-anchor="middle" fill="currentColor">Ridge</text>
<circle cx="550" cy="105" r="28" fill="#eea66f" fill-opacity="0.5" stroke="currentColor"/>
<text x="550" y="110" font-size="13" text-anchor="middle" fill="currentColor">Fan</text>
<text x="390" y="12" font-size="12" text-anchor="middle" fill="currentColor">rock; sample and photograph</text>
<text x="390" y="207" font-size="12" text-anchor="middle" fill="currentColor">rock; sample</text>
<text x="600" y="150" font-size="12" text-anchor="middle" fill="currentColor">photograph</text>
</svg>
<figcaption>Figure 10.2. The rover domain's map (orange: places with rocks). The goal needs a visit to Ridge, Delta and
Fan and a return to Base; the planner must also order camera, antenna, sampling and caching actions around the
drives.</figcaption>
</figure>

```
2. Forward and backward search
  problem                method        length  expanded  seconds
  Sussman (3 blocks)     forward BFS        6        21     0.00
  Sussman (3 blocks)     A* h_max           6        11     0.00
  Sussman (3 blocks)     A* h_add           6        11     0.00
  Sussman (3 blocks)     greedy h_FF        6        10     0.00
  Sussman (3 blocks)     backward BFS       6        14     0.00
  reverse a tower of 5   forward BFS       10       184     0.00
  reverse a tower of 5   A* h_max          10        27     0.01
  reverse a tower of 5   A* h_add          10        10     0.00
  reverse a tower of 5   greedy h_FF       10        10     0.00
  reverse a tower of 5   backward BFS      10       401     0.02
  6 blocks, two towers   forward BFS       14      5425     0.07
  6 blocks, two towers   A* h_max          14      1196     0.70
  6 blocks, two towers   A* h_add          16       158     0.15
  6 blocks, two towers   greedy h_FF       18        35     0.01
  6 blocks, two towers   backward BFS      14      6205     0.49
  rover day              forward BFS       16     31828     0.55
  rover day              A* h_max          16     14195     2.69
  rover day              A* h_add          16        45     0.01
  rover day              greedy h_FF       18        19     0.00
  rover day              backward BFS      16     15562     0.38
```

(The seconds are from one run on an ordinary laptop; they will differ on yours, but the "expanded" counts will not.)
The table tells the story of the next section. Blind search, forwards or backwards, expands thousands of nodes on the
larger problems. The heuristics cut that by one to three orders of magnitude. The admissible $h_{\max}$ keeps plans
optimal but prunes least; the inadmissible $h_{\mathrm{add}}$ and $h_{\mathrm{FF}}$ prune enormously, and the plans they
find are sometimes a little longer (16 and 18 instead of 14). On this rover problem backward search expands about half
as many nodes as forward search, because it ignores irrelevant actions; on the two larger block problems it does worse, because it
wastes time on goal sets that are only nearly consistent.

## 10.3 Planning heuristics: ignore-delete-lists relaxation

*Level: intermediate; the admissibility proof is advanced.*

### Relaxation

[Chapter 4](04-Heuristic-Search.md) showed that good heuristics come from **relaxed problems**: drop some constraints,
solve the easier problem exactly, and use its cost as an estimate. Manhattan distance for the 8-puzzle is the cost of a
relaxed puzzle in which tiles may move through each other. Because a planner can read the action descriptions, it can
relax *any* problem automatically, and the most successful relaxation in planning is simple: **ignore the delete
lists**.

In the **delete relaxation**, $\mathrm{result}^+(s, a) = s \cup \mathrm{add}(a)$. Facts, once true, stay true. The
hand can hold two blocks at once; the rover is in every place it has ever visited. Two consequences:

1. Any real plan is also a relaxed plan (deleting nothing never makes a precondition false that was true). So the
   optimal relaxed cost $h^+(s)$ is at most the true cost $h^*(s)$: **$h^+$ is admissible**.
2. In the relaxation, states only grow, so no action ever needs to be applied twice, and a relaxed plan can be found
   greedily in polynomial time.

But *optimal* relaxed planning is still NP-hard (Bylander 1994): finding the *fewest* actions that together produce the
goals is a set-cover-like problem ([Algorithms, Chapter 23](../algorithms/23-Approximation-and-Parameterized-Algorithms.md#233-set-cover-the-greedy-h_n-bound)).
So planners estimate $h^+$ itself. Three estimates, all computed by the program:

### h_max and h_add

Give every atom a cost: 0 if it is true in the current state $s$; otherwise the cheapest way to achieve it, computed by
a fixed-point iteration like the Bellman-Ford algorithm ([Algorithms, Chapter 16](../algorithms/16-Shortest-Paths.md)):

$$
\mathrm{cost}(p) = \min_{a \,:\, p \in \mathrm{add}(a)} \Big(1 + \mathrm{combine}_{q \in \mathrm{pre}(a)} \mathrm{cost}(q)\Big).
$$

With $\mathrm{combine} = \max$ this is $h_{\max}$ (Bonet and Geffner, 2001): an action's precondition costs as much as
its most expensive atom. With $\mathrm{combine} = \sum$ it is $h_{\mathrm{add}}$: the atoms are assumed to need
separate work. The heuristic value of the state is the same combination over the goal atoms.

Worked by hand on the Sussman anomaly (the state of Figure 10.1, left):

| atom | how it is reached (relaxed) | cost under max | cost under sum |
|---|---|---|---|
| Clear(A) | Unstack(C,A): pre all true | 1 | 1 |
| Holding(B) | PickUp(B): pre all true | 1 | 1 |
| Holding(A) | PickUp(A): needs Clear(A) | 1 + 1 = 2 | 1 + 1 = 2 |
| On(B,C) | Stack(B,C): needs Holding(B), Clear(C) | 1 + max(1, 0) = 2 | 1 + (1 + 0) = 2 |
| On(A,B) | Stack(A,B): needs Holding(A), Clear(B) | 1 + max(2, 0) = 3 | 1 + (2 + 0) = 3 |
| goal | On(A,B) and On(B,C) | max(3, 2) = 3 | 3 + 2 = 5 |

The true cost is 6. $h_{\max} = 3$ is a safe underestimate; $h_{\mathrm{add}} = 5$ is closer here.

**Theorem.** $h_{\max}$ is admissible: $h_{\max}(s) \le h^+(s) \le h^*(s)$.

*Proof.* The second inequality is consequence 1 above. For the first, take an optimal relaxed plan $a_1, \ldots, a_k$
from $s$, with $k = h^+(s)$. Claim: every atom $p$ that is true after the first $i$ actions of this plan (in the
relaxed sense) has $\mathrm{cost}(p) \le i$. By induction on $i$: for $i = 0$, the true atoms are those of $s$, with
cost 0. If $p$ first becomes true at action $a_i$, every precondition $q$ of $a_i$ was true after $i - 1$ actions, so
$\mathrm{cost}(q) \le i - 1$ by induction, and the fixed point gives $\mathrm{cost}(p) \le 1 + \max_q \mathrm{cost}(q)
\le i$. After $k$ actions all goal atoms are true, so each has cost at most $k$, and $h_{\max}(s) = \max_g
\mathrm{cost}(g) \le k$. $\square$

$h_{\mathrm{add}}$ is *not* admissible, because it counts shared work twice. Reversing a tower of five needs 10 actions,
but $h_{\mathrm{add}}$ says 24 at the start: each of the four goals $\mathit{On}(D,E), \ldots$ is charged for clearing
the same blocks. On the other hand, $h_{\max}$ is often far too low (4 for a 14-step problem), because it only looks at
the single hardest goal.

### h_FF: count a real relaxed plan

The **FF** planner of Jörg Hoffmann and Bernhard Nebel (2001) combined the strengths of both. Build the **relaxed
planning graph**: layer 0 is the atoms of $s$; layer $i$ adds every atom produced by an action whose preconditions are
all in earlier layers; stop when all goals are present. Then extract a relaxed plan backwards: for each goal atom pick
the action that first achieved it, add that action's preconditions as new subgoals, and repeat. The heuristic is the
number of distinct actions picked. Shared subgoals are counted once, so it is far closer to $h^+$ than $h_{\mathrm{add}}$,
and it comes with a concrete relaxed plan that can be used to suggest which actions to try first ("helpful actions").
It is still not admissible: the extraction is greedy, not optimal.

```
3. Heuristic values at the start, against the true optimal plan length h*
  problem                h_max h_add  h_FF   h*
  Sussman (3 blocks)         3     5     5    6
  reverse a tower of 5       6    24     9   10
  6 blocks, two towers       4    18    10   14
  rover day                  5    21    14   16
```

$h_{\mathrm{FF}}$ is the closest of the three on every problem, and it never overshoots here, though it can in general.
FF used it in a greedy search ("enforced hill climbing") and won the 2000 planning competition; its successors,
such as Fast Downward (Malte Helmert, 2006) and LAMA (Silvia Richter and Matthias Westphal, 2010), combine it with
other heuristics, especially **landmarks** (facts that every plan must make true at some point, such as
$\mathit{Holding}(A)$ in the Sussman anomaly) and **abstractions** (pattern databases, as in
[Chapter 4](04-Heuristic-Search.md), computed automatically from the factored description).

The other classic relaxation, **ignore preconditions**, makes every action applicable everywhere; its cost is the number
of goal atoms not yet true, roughly, when each action achieves one goal. It is admissible only with care (one action
can achieve several goals) and much weaker than the delete relaxation.

Exercise 8 shows that weighting the heuristic, as in [Chapter 4](04-Heuristic-Search.md)'s weighted A*, trades plan
quality for speed in a controlled way.

### The STRIPS planning program

```python
--8<-- "books/ai/ch10_strips.py"
```

```
1. The Sussman anomaly: C on A; A and B on the table.  Goal: On(A,B) and On(B,C).
  goals in order ['On(A,B)', 'On(B,C)']: 8 actions, all goals true at the end: False
  goals in order ['On(B,C)', 'On(A,B)']: 8 actions, all goals true at the end: False
  planning for both goals together: 6 actions: Unstack(C,A), PutDown(C), PickUp(B), Stack(B,C), PickUp(A), Stack(A,B)

2. Forward and backward search
  problem                method        length  expanded  seconds
  Sussman (3 blocks)     forward BFS        6        21     0.00
  Sussman (3 blocks)     A* h_max           6        11     0.00
  Sussman (3 blocks)     A* h_add           6        11     0.00
  Sussman (3 blocks)     greedy h_FF        6        10     0.00
  Sussman (3 blocks)     backward BFS       6        14     0.00
  reverse a tower of 5   forward BFS       10       184     0.00
  reverse a tower of 5   A* h_max          10        27     0.01
  reverse a tower of 5   A* h_add          10        10     0.00
  reverse a tower of 5   greedy h_FF       10        10     0.00
  reverse a tower of 5   backward BFS      10       401     0.02
  6 blocks, two towers   forward BFS       14      5425     0.07
  6 blocks, two towers   A* h_max          14      1196     0.70
  6 blocks, two towers   A* h_add          16       158     0.15
  6 blocks, two towers   greedy h_FF       18        35     0.01
  6 blocks, two towers   backward BFS      14      6205     0.49
  rover day              forward BFS       16     31828     0.55
  rover day              A* h_max          16     14195     2.69
  rover day              A* h_add          16        45     0.01
  rover day              greedy h_FF       18        19     0.00
  rover day              backward BFS      16     15562     0.38

3. Heuristic values at the start, against the true optimal plan length h*
  problem                h_max h_add  h_FF   h*
  Sussman (3 blocks)         3     5     5    6
  reverse a tower of 5       6    24     9   10
  6 blocks, two towers       4    18    10   14
  rover day                  5    21    14   16

  an optimal rover plan:
    Drive(Base,Rim), Drive(Rim,Delta), Sample(Delta), Cache(Delta), DeployAntenna, CameraOn
    Image(Delta), Drive(Delta,Fan), Send(Delta), Image(Fan), Drive(Fan,Ridge), Send(Fan)
    Sample(Ridge), Drive(Ridge,Rim), Drive(Rim,Base), Cache(Ridge)
```

## 10.4 Partial-order planning; GraphPlan (Blum and Furst 1995)

*Level: intermediate.*

### Searching in the space of plans

The planners so far commit to a total order from the first step: the plan is built strictly forwards or strictly
backwards. But many plans have parts that do not depend on each other. To put on shoes you need socks first, but
whether the left foot or the right foot goes first does not matter. A **partial-order plan** records only the orderings
that matter and leaves the rest open, a principle called **least commitment**.

Partial-order planning (POP) searches in the space of *plans* rather than states. A partial plan has:

- **steps**, each an instance of an action, plus two special steps: *Start*, whose add list is the initial state, and
  *Finish*, whose precondition is the goal;
- **ordering constraints** $a \prec b$ ("$a$ before $b$"), which must stay free of cycles;
- **causal links** $a \xrightarrow{p} b$: step $a$ achieves $p$, which $b$ needs, and $p$ must stay true from $a$ to $b$;
- **open preconditions**: preconditions of steps that no causal link supplies yet.

The empty plan has only *Start* $\prec$ *Finish* and every goal atom open. The planner repeatedly picks a **flaw** and
repairs it:

1. An **open precondition** $p$ of step $b$: choose a step $a$ that adds $p$, either one already in the plan (that can
   be ordered before $b$) or a new step from the action library; add $a \xrightarrow{p} b$ and $a \prec b$; a new step's
   preconditions become open.
2. A **threat**: a step $c$ that deletes $p$ and could be ordered between $a$ and $b$ of a link $a \xrightarrow{p} b$.
   Resolve it by **demotion** ($c \prec a$) or **promotion** ($b \prec c$), whichever keeps the order acyclic.

When no flaws remain, the plan is a **solution**.

**Theorem (soundness).** If a partial plan has no open preconditions and no threats, then *every* total order of its
steps consistent with the ordering constraints (every **linearization**) is a valid plan.

*Proof.* Take any linearization and any step $b$ with precondition $p$. There is a causal link $a \xrightarrow{p} b$
with $a \prec b$, so $p$ is true right after $a$ (it is in $a$'s add list, or $a$ is *Start* and $p$ is initial). Any
step $c$ that deletes $p$ is not between $a$ and $b$ in this linearization, because the absence of threats means it is
ordered before $a$ or after $b$. So $p$ is still true when $b$ executes. This holds for every precondition of every step,
including *Finish*, whose preconditions are the goal. $\square$

The planner is complete too, if it explores the choices systematically (McAllester and Rosenblitt's SNLP, 1991, proved
this for its version), because every plan can be justified by causal links.

### The program on shoes and socks, and on Sussman

```
1. Shoes and socks
  steps: 2:LeftShoe, 3:RightShoe, 4:LeftSock, 5:RightSock
  orderings (covering pairs only; Start < every step < Finish): LeftSock < LeftShoe, RightSock < RightShoe
  causal links:
    LeftShoe --LeftShoeOn--> Finish
    RightShoe --RightShoeOn--> Finish
    LeftSock --LeftSockOn--> LeftShoe
    RightSock --RightSockOn--> RightShoe
  6 total orders fit this one partial plan, e.g. LeftSock, LeftShoe, RightSock, RightShoe / LeftSock, RightSock, LeftShoe, RightShoe
  (4 partial plans explored)
```

One partial plan stands for six total orders: the number of ways to interleave two chains of length two,
$\binom{4}{2} = 6$. An executor can pick any of them at run time, for instance whichever foot is nearer. On the Sussman
anomaly, the same planner discovers the interleaving on its own:

```
2. The Sussman anomaly
  steps: 2:Stack(A,B), 3:Stack(B,C), 4:PickUp(A), 5:PickUp(B), 6:Unstack(C,A), 7:PutDown(C)
  orderings (covering pairs only; Start < every step < Finish): Stack(B,C) < PickUp(A), PickUp(A) < Stack(A,B), PickUp(B) < Stack(B,C), Unstack(C,A) < PutDown(C), PutDown(C) < PickUp(B)
  ...
  1 linearization(s), all checked by simulation:
    Unstack(C,A), PutDown(C), PickUp(B), Stack(B,C), PickUp(A), Stack(A,B)
  (41 partial plans explored)
```

Trace the key decisions. The planner adds $\mathit{Stack}(A,B)$ and $\mathit{Stack}(B,C)$ for the two goals.
$\mathit{Stack}(A,B)$ needs $\mathit{Clear}(B)$, and the planner supplies it from $\mathit{Stack}(B,C)$, which adds
$\mathit{Clear}(B)$ (B is clear once it sits on C): that causal link is the ordering "B on C before A on B".
$\mathit{Stack}(A,B)$ also deletes $\mathit{Clear}(B)$, which $\mathit{PickUp}(B)$ needs from *Start*, so it
threatens that link and is promoted after $\mathit{PickUp}(B)$. $\mathit{Unstack}(C,A)$ is added to clear A; since the hand can hold only one block, the $\mathit{HandEmpty}$ links
force $\mathit{PutDown}(C)$ before $\mathit{PickUp}(B)$, and so on. Here the constraints leave only one linearization,
the optimal plan. Exactly the threat mechanism that fails in goal-at-a-time planning ("achieving one goal clobbers
another") is here detected and repaired.

Partial-order planning was the dominant approach from the mid-1970s to the late 1990s: Earl Sacerdoti's NOAH (1975),
Austin Tate's NONLIN (1977), McAllester and Rosenblitt's SNLP (1991) and Penberthy and Weld's UCPOP (1992). Around 2000
it lost ground to forward search with the heuristics of 10.3, which were far easier to compute for states than for
partial plans. It remains attractive where flexibility matters: when actions have durations and run in parallel, and
when a human must read the plan and see which steps depend on which.

### GraphPlan

In 1995 Avrim Blum and Merrick Furst published GraphPlan ("Fast planning through planning graph analysis", IJCAI 1995;
journal version 1997), which was orders of magnitude faster than the partial-order planners of its day. Its central
object is the **planning graph**, a layered structure that over-approximates what can be reached in $k$ steps.

- **Level 0** is the set of atoms of the initial state.
- **Action level $k$** contains every action whose preconditions are all in proposition level $k$ and pairwise not
  mutex, plus a **no-op** ("persistence") action for each atom, which keeps it true.
- **Proposition level $k+1$** is the union of the add lists of action level $k$.
- **Mutex** (mutual exclusion) links mark pairs that cannot both happen at that level. Two actions at a level are mutex
  if (a) one deletes an effect of the other (*inconsistent effects*), (b) one deletes a precondition of the other
  (*interference*), or (c) some precondition of one is mutex with some precondition of the other (*competing needs*).
  Two atoms are mutex if every way of achieving one is mutex with every way of achieving the other.

<figure class="mars-fig" markdown="0">
<svg viewBox="0 0 640 300" role="img" aria-label="The first layers of the planning graph for the Sussman anomaly. Proposition level 0 has six atoms. Action level 0 has Unstack(C,A) and PickUp(B), which are mutex, plus no-ops. Proposition level 1 adds Holding(C), Clear(A) and Holding(B); Holding(C) and Holding(B) are mutex.">
<text x="110" y="14" font-size="13" text-anchor="middle" fill="currentColor" font-weight="bold">level 0</text>
<text x="320" y="14" font-size="13" text-anchor="middle" fill="currentColor" font-weight="bold">actions 0</text>
<text x="530" y="14" font-size="13" text-anchor="middle" fill="currentColor" font-weight="bold">level 1</text>
<text x="145" y="34" font-size="12" text-anchor="end" fill="currentColor">On(C,A)</text>
<text x="145" y="64" font-size="12" text-anchor="end" fill="currentColor">Clear(C)</text>
<text x="145" y="94" font-size="12" text-anchor="end" fill="currentColor">Clear(B)</text>
<text x="145" y="124" font-size="12" text-anchor="end" fill="currentColor">HandEmpty</text>
<text x="145" y="154" font-size="12" text-anchor="end" fill="currentColor">OnTable(A)</text>
<text x="145" y="184" font-size="12" text-anchor="end" fill="currentColor">OnTable(B)</text>
<line x1="150" y1="30" x2="490" y2="30" stroke="currentColor" stroke-opacity="0.4" stroke-dasharray="3 4"/>
<line x1="150" y1="60" x2="490" y2="60" stroke="currentColor" stroke-opacity="0.4" stroke-dasharray="3 4"/>
<line x1="150" y1="90" x2="490" y2="90" stroke="currentColor" stroke-opacity="0.4" stroke-dasharray="3 4"/>
<line x1="150" y1="120" x2="490" y2="120" stroke="currentColor" stroke-opacity="0.4" stroke-dasharray="3 4"/>
<line x1="150" y1="150" x2="490" y2="150" stroke="currentColor" stroke-opacity="0.4" stroke-dasharray="3 4"/>
<line x1="150" y1="180" x2="490" y2="180" stroke="currentColor" stroke-opacity="0.4" stroke-dasharray="3 4"/>
<text x="495" y="34" font-size="12" fill="currentColor">On(C,A)</text>
<text x="495" y="64" font-size="12" fill="currentColor">Clear(C)</text>
<text x="495" y="94" font-size="12" fill="currentColor">Clear(B)</text>
<text x="495" y="124" font-size="12" fill="currentColor">HandEmpty</text>
<text x="495" y="154" font-size="12" fill="currentColor">OnTable(A)</text>
<text x="495" y="184" font-size="12" fill="currentColor">OnTable(B)</text>
<text x="495" y="214" font-size="12" fill="currentColor" font-weight="bold">Holding(C)</text>
<text x="495" y="244" font-size="12" fill="currentColor" font-weight="bold">Clear(A)</text>
<text x="495" y="274" font-size="12" fill="currentColor" font-weight="bold">Holding(B)</text>
<rect x="262" y="212" width="116" height="26" rx="6" fill="#9cc9ea" fill-opacity="0.5" stroke="currentColor"/>
<text x="320" y="229" font-size="12" text-anchor="middle" fill="currentColor">Unstack(C,A)</text>
<rect x="262" y="252" width="116" height="26" rx="6" fill="#9cc9ea" fill-opacity="0.5" stroke="currentColor"/>
<text x="320" y="269" font-size="12" text-anchor="middle" fill="currentColor">PickUp(B)</text>
<line x1="150" y1="30" x2="262" y2="222" stroke="currentColor"/>
<line x1="150" y1="60" x2="262" y2="225" stroke="currentColor"/>
<line x1="150" y1="120" x2="262" y2="228" stroke="currentColor"/>
<line x1="150" y1="90" x2="262" y2="261" stroke="currentColor"/>
<line x1="150" y1="120" x2="262" y2="265" stroke="currentColor"/>
<line x1="150" y1="180" x2="262" y2="269" stroke="currentColor"/>
<line x1="378" y1="222" x2="490" y2="210" stroke="currentColor"/>
<line x1="378" y1="228" x2="490" y2="240" stroke="currentColor"/>
<line x1="378" y1="265" x2="490" y2="270" stroke="currentColor"/>
<path d="M262,232 Q236,248 262,262" fill="none" stroke="#eea66f" stroke-width="2.5"/>
<text x="222" y="252" font-size="11" text-anchor="end" fill="currentColor">mutex</text>
<path d="M568,210 Q600,240 568,270" fill="none" stroke="#eea66f" stroke-width="2.5"/>
<text x="596" y="244" font-size="11" fill="currentColor">mutex</text>
</svg>
<figcaption>Figure 10.3. The first layers of the planning graph for the Sussman anomaly. Dashed lines are no-ops.
Unstack(C,A) and PickUp(B) are mutex (each deletes HandEmpty, which the other needs), and therefore so are their only
effects Holding(C) and Holding(B): the hand cannot hold both after one step.</figcaption>
</figure>

**Facts about the planning graph.**

1. *Polynomial size.* With $m$ ground atoms and $n$ ground actions, each level has at most $m$ atoms and $n + m$
   actions, and at most quadratically many mutex pairs, so building $k$ levels costs time polynomial in $k$, $m$ and
   $n$. Compare the $2^m$ states of the state space.
2. *Monotonicity.* Atoms and actions only appear as levels grow (no-ops carry everything forward), and mutexes only
   disappear: if two atoms are not mutex at level $k$, they are not mutex at any later level. The program checks this
   on Sussman (the last line of its first block below).
3. *Leveling off.* Since levels grow and mutex sets shrink, and both are finite, the graph eventually stops changing.
   If the goals are not all present and pairwise non-mutex by then, the problem has no solution.
4. *Admissible estimates.* If a set of atoms can be made true after $k$ steps (with parallel steps of non-mutex
   actions), the atoms appear, pairwise non-mutex, at level $k$. Read the other way: the first level at which an atom
   appears is a lower bound on the number of parallel steps to achieve it.

From fact 4 come planning-graph heuristics. The **max-level** heuristic (the largest first-appearance level among the
goals) is admissible. **Level-sum** adds the levels; like $h_{\mathrm{add}}$ it is not admissible. **Set-level** is the
first level at which all goals appear and are pairwise non-mutex; it is admissible and dominates max-level.

```
1. The planning graph for the Sussman anomaly
  level  propositions  prop-mutexes  actions(incl. no-ops)  action-mutexes
      0             6             0                      8               7
      1             9            11                     16              74
      2            12            24                     23             174
      3            13            29                     28             273
      4            16            53                     34             422
      5            16            49                     34             410
      6            16            45                      -               -
  On(A,B) and On(B,C) mutex at levels 0..6: [False, False, False, False, True, True, False]
  a pair mutex at level k+1 was already mutex at level k (mutexes only disappear): True

2. Heuristics read off the graph
  first level: {'On(B,C)': 2, 'On(A,B)': 4}; max-level 4, level-sum 6, set-level 6  (true cost 6)
```

At levels 0 to 3 the two goals are not both present at all, so "not mutex" there means nothing. They first coexist at
level 4, but as a mutex pair; only at level 6 do they become compatible. The set-level heuristic, 6, equals the true
cost on this problem. (The absolute number of mutexes grows at first because the number of atoms grows; each
particular pair, once non-mutex, stays non-mutex.)

**Plan extraction.** GraphPlan expands the graph until all goals appear without mutexes at the last level $k$, then
searches backwards: choose a set of pairwise non-mutex actions at action level $k-1$ that achieves all goals (no-ops
included), make their preconditions the goals at level $k-1$, and recurse to level 0. A failure for a goal set at a
level is stored as a **nogood**, so it is never retried. If extraction fails, add a level and try again; GraphPlan's
termination test compares nogoods across levels once the graph has leveled off.

```
3. Extracted plan (6 steps, 33 choice points)
  step 1: Unstack(C,A)
  ...
  step 6: Stack(A,B)

4. Parallel steps: two rovers, each must drive and take a picture
  step 1: Drive(R1,Base,Ridge), Drive(R2,Base,Rim)
  step 2: Drive(R2,Rim,Delta), Image(R1,Ridge)
  step 3: Drive(R1,Ridge,Base), Image(R2,Delta)
  3 steps, 6 actions
```

The second problem shows what GraphPlan's steps mean: actions within a step are non-mutex, so they can run in any
order or simultaneously. Two rovers do six actions in three steps. GraphPlan finds plans with the fewest *steps*, which
for parallel actions is the natural measure of time. It does not minimise the number of actions.

**SATPlan.** Henry Kautz and Bart Selman (1992, 1996) took a different route to the same structure: encode "there is
a plan of $k$ steps" as a propositional formula (one variable per atom per time step, one per action per time step,
with clauses for preconditions, effects, frame axioms and mutexes), and hand it to a SAT solver
([Chapter 8](08-Propositional-Logic-and-SAT.md)); increase $k$ until it is satisfiable. With the CDCL solvers of the
2000s, SAT-based planning became one of the strongest approaches for optimal parallel plans.

### The partial-order planning and GraphPlan programs

```python
--8<-- "books/ai/ch10_pop.py"
```

```
1. Shoes and socks
  steps: 2:LeftShoe, 3:RightShoe, 4:LeftSock, 5:RightSock
  orderings (covering pairs only; Start < every step < Finish): LeftSock < LeftShoe, RightSock < RightShoe
  causal links:
    LeftShoe --LeftShoeOn--> Finish
    RightShoe --RightShoeOn--> Finish
    LeftSock --LeftSockOn--> LeftShoe
    RightSock --RightSockOn--> RightShoe
  6 total orders fit this one partial plan, e.g. LeftSock, LeftShoe, RightSock, RightShoe / LeftSock, RightSock, LeftShoe, RightShoe
  (4 partial plans explored)

2. The Sussman anomaly
  steps: 2:Stack(A,B), 3:Stack(B,C), 4:PickUp(A), 5:PickUp(B), 6:Unstack(C,A), 7:PutDown(C)
  orderings (covering pairs only; Start < every step < Finish): Stack(B,C) < PickUp(A), PickUp(A) < Stack(A,B), PickUp(B) < Stack(B,C), Unstack(C,A) < PutDown(C), PutDown(C) < PickUp(B)
  causal links:
    Stack(A,B) --On(A,B)--> Finish
    Stack(B,C) --On(B,C)--> Finish
    Stack(B,C) --Clear(B)--> Stack(A,B)
    PickUp(A) --Holding(A)--> Stack(A,B)
    PickUp(B) --Holding(B)--> Stack(B,C)
    PutDown(C) --Clear(C)--> Stack(B,C)
    Start --OnTable(A)--> PickUp(A)
    Stack(B,C) --HandEmpty--> PickUp(A)
    Unstack(C,A) --Clear(A)--> PickUp(A)
    Start --Clear(B)--> PickUp(B)
    Start --OnTable(B)--> PickUp(B)
    PutDown(C) --HandEmpty--> PickUp(B)
    Start --Clear(C)--> Unstack(C,A)
    Start --HandEmpty--> Unstack(C,A)
    Start --On(C,A)--> Unstack(C,A)
    Unstack(C,A) --Holding(C)--> PutDown(C)
  1 linearization(s), all checked by simulation:
    Unstack(C,A), PutDown(C), PickUp(B), Stack(B,C), PickUp(A), Stack(A,B)
  (41 partial plans explored)
```

```python
--8<-- "books/ai/ch10_graphplan.py"
```

```
1. The planning graph for the Sussman anomaly
  level  propositions  prop-mutexes  actions(incl. no-ops)  action-mutexes
      0             6             0                      8               7
      1             9            11                     16              74
      2            12            24                     23             174
      3            13            29                     28             273
      4            16            53                     34             422
      5            16            49                     34             410
      6            16            45                      -               -
  On(A,B) and On(B,C) mutex at levels 0..6: [False, False, False, False, True, True, False]
  a pair mutex at level k+1 was already mutex at level k (mutexes only disappear): True

2. Heuristics read off the graph
  first level: {'On(B,C)': 2, 'On(A,B)': 4}; max-level 4, level-sum 6, set-level 6  (true cost 6)

3. Extracted plan (6 steps, 33 choice points)
  step 1: Unstack(C,A)
  step 2: PutDown(C)
  step 3: PickUp(B)
  step 4: Stack(B,C)
  step 5: PickUp(A)
  step 6: Stack(A,B)

4. Parallel steps: two rovers, each must drive and take a picture
  step 1: Drive(R1,Base,Ridge), Drive(R2,Base,Rim)
  step 2: Drive(R2,Rim,Delta), Image(R1,Ridge)
  step 3: Drive(R1,Ridge,Base), Image(R2,Delta)
  3 steps, 6 actions
```

## 10.5 Hierarchical task networks; scheduling with resources

*Level: intermediate.*

### Planning the way people describe work

Ask a mission planner how a rover spends a day and you will not hear a list of 16 primitive actions. You will hear
"collect a sample at Ridge, then one at Delta, photograph both, downlink, drive home", and each of those, if you ask,
breaks into smaller steps: "collecting a sample means driving there, drilling, sealing the tube". **Hierarchical task
network (HTN) planning** works exactly this way.

An HTN problem has:

- **primitive tasks**, which are ordinary actions with preconditions and effects;
- **compound tasks** (also called *high-level actions*), such as $\mathit{Collect}(p)$, which cannot be executed
  directly;
- **methods**: each method says how to carry out a compound task, as a list (or partial order) of subtasks, and may
  have a precondition saying when it applies. A task may have several methods;
- an initial **task network** (here, the single task $\mathit{Day}$) instead of, or as well as, a goal.

A **solution** is a sequence of primitive actions obtained by repeatedly replacing compound tasks by the subtasks of one
of their methods, that is executable from the initial state. The planner's search is over *which method* to use for
each task, not over arbitrary actions.

Our planner is in the style of SHOP (Dana Nau and colleagues, 1999; SHOP2, 2003): **total-order, forward
decomposition**. It refines tasks left to right while simulating the state, so each method's precondition can be
tested against the actual state at that point. The rover methods are short Python functions: $\mathit{Photograph}(p)$
switches the camera on only if it is off; $\mathit{Downlink}(p)$ deploys the antenna only if needed (switching the
camera off first); $\mathit{GoTo}(p)$ drives to a neighbour that is closer to $p$ and recurses, which is route-finding
knowledge built into the method.

```
1. HTN planning: decompose Day into primitive actions
  Day()
    Collect(Ridge)
      GoTo(Ridge)
        Drive(Base,Rim)
        GoTo(Ridge)
          Drive(Rim,Ridge)
          GoTo(Ridge)
      Sample(Ridge)
      Cache(Ridge)
    Collect(Delta)
      ...
    Photograph(Delta)
      CameraOn
      GoTo(Delta)
      Image(Delta)
    ...
    Downlink(Delta)
      CameraOff
      DeployAntenna
      Send(Delta)
    Downlink(Fan)
      Send(Fan)
    GoTo(Base)
      ...
  19 primitive actions; goal reached: True
  (an optimal plan from search has 16 actions)
```

(The full tree is in the program output at the end of this section.) The HTN planner did almost no search: each task had
one applicable method, or the method's ordering of alternatives was right first time. The price is plan quality and
generality. The plan has 19 actions instead of 16, because the task list fixed the order "collect, then photograph",
which makes the rover visit Delta and Fan in a poor order; a search planner found the better interleaving. And the
planner can only produce plans that the methods allow. That is the trade HTN makes deliberately: methods encode the
expert's **recipes**, which rule out absurd plans and make planning fast and predictable, and they let the planner use
knowledge, such as operating procedures and safety rules, that is hard to state as goals. Many deployed planners are
hierarchical for this reason, from Sacerdoti's NOAH (1975) and Tate's O-Plan to David Wilkins's SIPE (1988) and SHOP2.

How expressive are HTNs? More than STRIPS: Kutluhan Erol, James Hendler and Dana Nau (1994) showed that HTN planning
with partially ordered, recursive methods can encode context-free grammars and is **undecidable** in general, whereas
STRIPS planning is decidable (PSPACE). With total ordering, as in SHOP, or bounded recursion, it becomes decidable
again.

### Scheduling: when the actions are known

Planning chooses *which* actions; **scheduling** decides *when* each one happens, given durations, ordering
constraints and limited **resources** (power, memory, an instrument that can do one thing at a time). Real systems
interleave the two, but the scheduling part alone already needs algorithms.

Take ten activities for a rover sol, with invented durations and power draws, and predecessors: drive after warm-up,
unstow the arm after the drive, abrade the rock after unstowing, and so on.

**The critical path method (CPM).** (Developed in the late 1950s by James Kelley and Morgan Walker for plant
construction; the US Navy's PERT is its cousin.) If resources are unlimited, each activity should start as soon as its
predecessors finish. Define the **earliest start**

$$
\mathrm{ES}(j) = \max_{i \,\in\, \mathrm{pred}(j)} \big(\mathrm{ES}(i) + d_i\big), \qquad \mathrm{ES}(j) = 0 \text{ if } j \text{ has no predecessors},
$$

computed in topological order ([Algorithms, Chapter 15](../algorithms/15-Graphs-and-Graph-Search.md#154-topological-sort)).
The **makespan** (total length) is $T = \max_j (\mathrm{ES}(j) + d_j)$. Working backwards, the **latest start** that
does not delay the makespan is

$$
\mathrm{LS}(j) = \min_{k \,\in\, \mathrm{succ}(j)} \mathrm{LS}(k) - d_j, \qquad \mathrm{LS}(j) = T - d_j \text{ if } j \text{ has no successors}.
$$

The **slack** $\mathrm{LS}(j) - \mathrm{ES}(j)$ says how long $j$ can slip; activities with zero slack form the
**critical path**.

*Why it is right.* $\mathrm{ES}(j)$ is the length of the longest path (summing durations) from a source to $j$ in the
precedence DAG; by induction in topological order, no schedule can start $j$ earlier (each predecessor must finish), and
starting every job at $\mathrm{ES}$ respects every constraint. So $T$ is the optimal makespan, equal to the longest
path, which is a dynamic program over a DAG ([Algorithms, Chapter 13](../algorithms/13-Dynamic-Programming.md#136-dp-on-trees-and-dags)),
computed in time linear in the number of activities plus constraints. The latest starts are the same computation on the
reversed DAG. $\square$

```
2. Critical path method (no resource limits)
  job               dur watts earliest latest slack
  Warm up            30    40        0      0     0  critical
  Drive to Delta     90   120       30     30     0  critical
  Panorama           40    30       30    185   155
  Arm unstow         15    50      120    120     0  critical
  Abrade rock        30   110      135    135     0  critical
  Spectrometer       60    40      165    165     0  critical
  Drill core         50   130      165    180    15
  Close-up image     20    30      165    205    40
  Seal tube          25    60      215    230    15
  Downlink           30    70      225    225     0  critical
  makespan 255 minutes
  peak power if every job starts as early as possible: 200 W
```

The critical path is warm-up, drive, unstow, abrade, spectrometer, downlink: $30 + 90 + 15 + 30 + 60 + 30 = 255$
minutes. The panorama can slip by up to 155 minutes without delaying anything.

**Adding a resource.** Now suppose the rover can supply at most 160 W at once. Starting everything early draws 200 W
(drill, spectrometer and close-up imaging together), so some activities must move. This is the
**resource-constrained project scheduling problem**, and it is NP-hard (Blazewicz, Lenstra and Rinnooy Kan, 1983).
A standard heuristic is **list scheduling** (the *serial schedule-generation scheme*): sort the activities by a
priority, here least slack first; take them one by one, always one whose predecessors are already scheduled, and start
it at the earliest time when its predecessors are done and the power stays under the cap for its whole duration.

```
3. With a power cap (resource-constrained scheduling, priority = least slack first)
  cap 250 W: makespan 255 min, peak 200 W, delayed: none
  cap 200 W: makespan 255 min, peak 200 W, delayed: none
  cap 160 W: makespan 305 min, peak 150 W, delayed: Drill core, Seal tube, Downlink
  cap 130 W: makespan 305 min, peak 130 W, delayed: Panorama, Drill core, Seal tube, Downlink
```

<figure class="mars-fig" markdown="0">
<svg viewBox="0 0 660 286" role="img" aria-label="A Gantt chart of the ten rover activities under a 160 watt cap. Critical-path activities are orange, others blue. Drill core, seal tube and downlink are pushed later than their earliest starts, shown as dashed outlines. The schedule ends at 305 minutes instead of 255.">
<text x="142" y="35" font-size="12" text-anchor="end" fill="currentColor">Warm up</text>
<rect x="150.0" y="23" width="45.0" height="16" fill="#eea66f" fill-opacity="0.7" stroke="currentColor"/>
<text x="199.0" y="35" font-size="11" fill="currentColor">40 W</text>
<text x="142" y="57" font-size="12" text-anchor="end" fill="currentColor">Drive to Delta</text>
<rect x="195.0" y="45" width="135.0" height="16" fill="#eea66f" fill-opacity="0.7" stroke="currentColor"/>
<text x="334.0" y="57" font-size="11" fill="currentColor">120 W</text>
<text x="142" y="79" font-size="12" text-anchor="end" fill="currentColor">Panorama</text>
<rect x="195.0" y="67" width="60.0" height="16" fill="#9cc9ea" fill-opacity="0.7" stroke="currentColor"/>
<text x="259.0" y="79" font-size="11" fill="currentColor">30 W</text>
<text x="142" y="101" font-size="12" text-anchor="end" fill="currentColor">Arm unstow</text>
<rect x="330.0" y="89" width="22.5" height="16" fill="#eea66f" fill-opacity="0.7" stroke="currentColor"/>
<text x="356.5" y="101" font-size="11" fill="currentColor">50 W</text>
<text x="142" y="123" font-size="12" text-anchor="end" fill="currentColor">Abrade rock</text>
<rect x="352.5" y="111" width="45.0" height="16" fill="#eea66f" fill-opacity="0.7" stroke="currentColor"/>
<text x="401.5" y="123" font-size="11" fill="currentColor">110 W</text>
<text x="142" y="145" font-size="12" text-anchor="end" fill="currentColor">Spectrometer</text>
<rect x="397.5" y="133" width="90.0" height="16" fill="#eea66f" fill-opacity="0.7" stroke="currentColor"/>
<text x="491.5" y="145" font-size="11" fill="currentColor">40 W</text>
<text x="142" y="167" font-size="12" text-anchor="end" fill="currentColor">Drill core</text>
<rect x="397.5" y="155" width="75.0" height="16" fill="none" stroke="currentColor" stroke-dasharray="3 3"/>
<rect x="487.5" y="155" width="75.0" height="16" fill="#9cc9ea" fill-opacity="0.7" stroke="currentColor"/>
<text x="566.5" y="167" font-size="11" fill="currentColor">130 W</text>
<text x="142" y="189" font-size="12" text-anchor="end" fill="currentColor">Close-up image</text>
<rect x="397.5" y="177" width="30.0" height="16" fill="#9cc9ea" fill-opacity="0.7" stroke="currentColor"/>
<text x="431.5" y="189" font-size="11" fill="currentColor">30 W</text>
<text x="142" y="211" font-size="12" text-anchor="end" fill="currentColor">Seal tube</text>
<rect x="472.5" y="199" width="37.5" height="16" fill="none" stroke="currentColor" stroke-dasharray="3 3"/>
<rect x="562.5" y="199" width="37.5" height="16" fill="#9cc9ea" fill-opacity="0.7" stroke="currentColor"/>
<text x="604.0" y="211" font-size="11" fill="currentColor">60 W</text>
<text x="142" y="233" font-size="12" text-anchor="end" fill="currentColor">Downlink</text>
<rect x="487.5" y="221" width="45.0" height="16" fill="none" stroke="currentColor" stroke-dasharray="3 3"/>
<rect x="562.5" y="221" width="45.0" height="16" fill="#eea66f" fill-opacity="0.7" stroke="currentColor"/>
<text x="611.5" y="233" font-size="11" fill="currentColor">70 W</text>
<line x1="150" y1="246" x2="615.0" y2="246" stroke="currentColor"/>
<line x1="150.0" y1="246" x2="150.0" y2="251" stroke="currentColor"/>
<text x="150.0" y="264" font-size="11" text-anchor="middle" fill="currentColor">0</text>
<line x1="225.0" y1="246" x2="225.0" y2="251" stroke="currentColor"/>
<text x="225.0" y="264" font-size="11" text-anchor="middle" fill="currentColor">50</text>
<line x1="300.0" y1="246" x2="300.0" y2="251" stroke="currentColor"/>
<text x="300.0" y="264" font-size="11" text-anchor="middle" fill="currentColor">100</text>
<line x1="375.0" y1="246" x2="375.0" y2="251" stroke="currentColor"/>
<text x="375.0" y="264" font-size="11" text-anchor="middle" fill="currentColor">150</text>
<line x1="450.0" y1="246" x2="450.0" y2="251" stroke="currentColor"/>
<text x="450.0" y="264" font-size="11" text-anchor="middle" fill="currentColor">200</text>
<line x1="525.0" y1="246" x2="525.0" y2="251" stroke="currentColor"/>
<text x="525.0" y="264" font-size="11" text-anchor="middle" fill="currentColor">250</text>
<line x1="600.0" y1="246" x2="600.0" y2="251" stroke="currentColor"/>
<text x="600.0" y="264" font-size="11" text-anchor="middle" fill="currentColor">300</text>
<text x="382.5" y="280" font-size="12" text-anchor="middle" fill="currentColor">minutes</text>
<line x1="532.5" y1="14" x2="532.5" y2="246" stroke="#7ccf9a" stroke-width="2" stroke-dasharray="5 3"/>
<line x1="607.5" y1="14" x2="607.5" y2="246" stroke="#7ccf9a" stroke-width="2" stroke-dasharray="5 3"/>
</svg>
<figcaption>Figure 10.4. The schedule under a 160 W cap. Orange bars are on the unconstrained critical path; dashed
outlines show where a delayed activity would start without the cap; green dashed lines mark the makespans without the
cap (255 minutes) and with it (305 minutes). The 130 W drill cannot run beside the spectrometer or the downlink.</figcaption>
</figure>

Is 305 minutes the best possible under 160 W? Here we can prove it. Nothing can start before the abrasion ends at 165.
After that, the drill (130 W) cannot overlap the spectrometer (40 W, total 170) or the downlink (70 W, total 200), and
the downlink must follow the spectrometer. So the drill, the spectrometer and the downlink run one after another:
$165 + 50 + 60 + 30 = 305$. The heuristic happened to find an optimal schedule. In general it does not, and real
schedulers use constraint propagation ([Chapter 7](07-Constraint-Satisfaction.md)), local search
([Chapter 5](05-Local-Search-and-Optimization.md)) or integer programming. At 130 W the panorama (30 W) can no longer
run beside the drive (120 W), so it moves too, but into the slack, and the makespan does not change.

Real activity planners for spacecraft add more kinds of constraints: **time windows** (a downlink only while an orbiter
is overhead), **state constraints** (the arm must be stowed while driving), and **consumable** resources (battery
energy, which drains and recharges, rather than power, which is a rate). The resulting problems are solved by
combinations of everything in this chapter.

### The HTN and scheduling program

```python
--8<-- "books/ai/ch10_htn_schedule.py"
```

```
1. HTN planning: decompose Day into primitive actions
  Day()
    Collect(Ridge)
      GoTo(Ridge)
        Drive(Base,Rim)
        GoTo(Ridge)
          Drive(Rim,Ridge)
          GoTo(Ridge)
      Sample(Ridge)
      Cache(Ridge)
    Collect(Delta)
      GoTo(Delta)
        Drive(Ridge,Fan)
        GoTo(Delta)
          Drive(Fan,Delta)
          GoTo(Delta)
      Sample(Delta)
      Cache(Delta)
    Photograph(Delta)
      CameraOn
      GoTo(Delta)
      Image(Delta)
    Photograph(Fan)
      GoTo(Fan)
        Drive(Delta,Fan)
        GoTo(Fan)
      Image(Fan)
    Downlink(Delta)
      CameraOff
      DeployAntenna
      Send(Delta)
    Downlink(Fan)
      Send(Fan)
    GoTo(Base)
      Drive(Fan,Delta)
      GoTo(Base)
        Drive(Delta,Rim)
        GoTo(Base)
          Drive(Rim,Base)
          GoTo(Base)
  19 primitive actions; goal reached: True
  (an optimal plan from search has 16 actions)

2. Critical path method (no resource limits)
  job               dur watts earliest latest slack
  Warm up            30    40        0      0     0  critical
  Drive to Delta     90   120       30     30     0  critical
  Panorama           40    30       30    185   155
  Arm unstow         15    50      120    120     0  critical
  Abrade rock        30   110      135    135     0  critical
  Spectrometer       60    40      165    165     0  critical
  Drill core         50   130      165    180    15
  Close-up image     20    30      165    205    40
  Seal tube          25    60      215    230    15
  Downlink           30    70      225    225     0  critical
  makespan 255 minutes
  peak power if every job starts as early as possible: 200 W

3. With a power cap (resource-constrained scheduling, priority = least slack first)
  cap 250 W: makespan 255 min, peak 200 W, delayed: none
  cap 200 W: makespan 255 min, peak 200 W, delayed: none
  cap 160 W: makespan 305 min, peak 150 W, delayed: Drill core, Seal tube, Downlink
  cap 130 W: makespan 305 min, peak 130 W, delayed: Panorama, Drill core, Seal tube, Downlink
```

## 10.6 Planning in the real world: spacecraft autonomy and rover activity planning

### Why spacecraft plan for themselves

A radio signal takes about 3 to 22 minutes to travel between Earth and Mars, depending on where the two planets are in
their orbits, so a question and its answer take between about 6 and 44 minutes, and the rover is out of contact for
much of each day. Nobody can drive a Mars rover with a joystick. The usual pattern is that ground teams plan the
activities for the next sol (a Mars day) while the rover sleeps, send the plan up as a command sequence, and receive
the results the next day. Everything that cannot wait that long, from avoiding a rock to choosing a target for a laser,
must be decided on board ([Chapter 2](02-Intelligent-Agents.md#26-autonomy-with-long-delays-why-a-mars-rover-must-decide-for-itself)).

Planning in this world differs from the textbook problem in four ways:

- **Time and resources are central.** Activities have durations, overlap, and draw power and data volume; a plan is a
  schedule as much as a sequence (10.5).
- **Execution is uncertain.** A drive may end short of the target, an instrument may take longer, a fault may occur.
  The planner must be paired with an **executive** that monitors execution and repairs or replans
  ([Chapter 5](05-Local-Search-and-Optimization.md#56-search-with-nondeterministic-actions-and-partial-observation-and-or-search-belief-states)
  discusses plans with branches for different outcomes).
- **Safety constraints are hard.** Some states (instrument too cold, battery too low) must never occur, whatever the
  plan gains.
- **Humans stay in charge.** Ground teams want to understand and approve plans, so the planner's output must be
  readable and its constraints explicit, which favours hierarchical and constraint-based planners.

### Remote Agent on Deep Space 1 (1999)

Deep Space 1 was a NASA technology-demonstration spacecraft launched in 1998. In May 1999, during the **Remote Agent
Experiment**, software developed at NASA Ames Research Center and JPL controlled the spacecraft for several days from
high-level goals rather than from a fixed command sequence. NASA described it as the first time an artificial
intelligence system had controlled a spacecraft without human supervision. Remote Agent had three parts (Muscettola,
Nayak, Pell and Williams, "Remote Agent: to boldly go where no AI system has gone before", *Artificial Intelligence*
103, 1998):

- a **planner/scheduler** that built a temporal plan on board from the goals, using constraint-based temporal
  planning in the spirit of 10.4 and 10.5;
- a **smart executive** that carried out the plan, decomposing its activities into commands, hierarchically as in
  an HTN, and reacting to events;
- **mode identification and recovery** (the Livingstone system), which used a model of the spacecraft's components and
  logical reasoning to diagnose faults from sensor readings and choose repairs.

During the experiment, simulated faults were injected and handled. One run stopped when the executive deadlocked, a
concurrency bug in the flight software; the team diagnosed it from the ground and the experiment went on to complete its
objectives. Both the success and the bug were instructive: the first showed that onboard planning and diagnosis could
work in flight, and the second fed directly into research on verifying autonomy software (see
[Chapter 20](20-Safe-and-Reliable-AI.md) on formal methods).

### Activity planning for the Mars rovers

For the Mars Exploration Rovers Spirit and Opportunity (landed January 2004), the tactical planning of each sol's
activities was done on the ground with **MAPGEN** (Mixed-initiative Activity Plan GENerator), built on the EUROPA
constraint-based planner from NASA Ames (Bresina, Jónsson, Morris and Rajan, "Activity planning for the Mars
Exploration Rovers", ICAPS 2005). It was *mixed-initiative*: the planner proposed schedules satisfying the constraints
(power, data, thermal, ordering), and human planners edited them, with the system checking every change. That division
of labour, with people choosing the science and the program guaranteeing the constraints, is typical of deployed
planning.

JPL's ASPEN and CASPER planners took the next step on board an Earth-orbiting spacecraft: from 2003 the **Autonomous
Sciencecraft Experiment** on Earth Observing-1 used CASPER to replan observations on board when its own image analysis
detected events such as floods or volcanic activity (Chien et al., 2005). On Mars, the AEGIS software lets
Opportunity (from 2010), Curiosity (from 2016) and Perseverance choose rock targets for their instruments on board,
without waiting for the ground (Estlin et al., 2012; Francis et al., 2017), and Perseverance's AutoNav plans its own
driving paths through rock fields. For Perseverance, JPL also developed a flight-software scheduler meant to adjust the
timing of a sol's activities on board as conditions change. These systems make local decisions within a plan written
on Earth; the overall day is still planned by people with ground tools.

### What the field looks like now

The planning research community runs the International Planning Competition, with tracks for optimal, satisficing
(any good plan), temporal, probabilistic and learning planners; PDDL is its language and Fast Downward one of the most
used code bases. Planning also meets the rest of this book: plans with uncertain outcomes become Markov decision
processes ([Chapter 14](14-Making-Decisions.md)); planners with learned models are part of model-based reinforcement
learning ([Chapter 15](15-Reinforcement-Learning.md)); and whether large language models can plan reliably is an active
and contested research question ([Chapter 17](17-Large-Language-Models.md)). A practical point: if you need a planner
today, you write your domain in PDDL and run an existing planner (such as Fast Downward); you write your own only to
learn how they work, which is what this chapter did.

## Check yourself

??? question "1. Apply Unstack(C,A) to the initial state of the Sussman anomaly. Which actions are applicable in the initial state?"

    Initial state: $\{\mathit{On}(C,A), \mathit{OnTable}(A), \mathit{OnTable}(B), \mathit{Clear}(C), \mathit{Clear}(B),
    \mathit{HandEmpty}\}$. Unstack(C,A) deletes $\mathit{On}(C,A)$, $\mathit{Clear}(C)$, $\mathit{HandEmpty}$ and adds
    $\mathit{Holding}(C)$, $\mathit{Clear}(A)$, giving $\{\mathit{Clear}(A), \mathit{Clear}(B), \mathit{Holding}(C),
    \mathit{OnTable}(A), \mathit{OnTable}(B)\}$. Applicable initially: only $\mathit{PickUp}(B)$ and
    $\mathit{Unstack}(C,A)$ (the hand is empty and only B and C are clear; A is under C).

??? question "2. Regress the goal {On(A,B), HandEmpty} through Stack(A,B), PutDown(C), Unstack(C,A) and PickUp(A)."

    Stack(A,B) adds both goal atoms and deletes neither: regression $= (\{\ldots\} \setminus \mathrm{add}) \cup
    \mathrm{pre} = \{\mathit{Holding}(A), \mathit{Clear}(B)\}$. PutDown(C) adds $\mathit{HandEmpty}$ and deletes
    neither goal atom: $\{\mathit{On}(A,B), \mathit{Holding}(C)\}$. Unstack(C,A) is not relevant: it deletes
    $\mathit{HandEmpty}$ (and adds neither goal). PickUp(A) is not relevant: it adds neither goal and deletes
    $\mathit{HandEmpty}$. The program's `regress` gives the same answers.

??? question "3. Compute h_FF by hand for the Sussman anomaly and list the relaxed plan. Why is it below the true cost 6?"

    Relaxed planning graph: layer 1 adds $\mathit{Holding}(C)$, $\mathit{Clear}(A)$ (Unstack(C,A)) and
    $\mathit{Holding}(B)$ (PickUp(B)). Layer 2 adds $\mathit{Holding}(A)$ (PickUp(A), now that A is clear) and
    $\mathit{On}(B,C)$ (Stack(B,C)). Layer 3 adds $\mathit{On}(A,B)$ (Stack(A,B)). Extract backwards: Stack(A,B) needs
    Holding(A) from PickUp(A), which needs Clear(A) from Unstack(C,A); Stack(B,C) needs Holding(B) from PickUp(B). The
    relaxed plan is {Unstack(C,A), PickUp(A), Stack(A,B), PickUp(B), Stack(B,C)}: 5 actions. It misses PutDown(C):
    in the relaxation the hand "holds" C and B and A at once, because deletes (of HandEmpty and Holding) are ignored.

??? question "4. Prove that h_add is not admissible with the program's numbers, and explain where the overcount comes from."

    Reversing a tower of five blocks costs 10 actions, but $h_{\mathrm{add}} = 24$ at the start, so it overestimates and
    is not admissible. Each goal $\mathit{On}(D,E)$, $\mathit{On}(C,D)$, $\mathit{On}(B,C)$, $\mathit{On}(A,B)$ is
    costed separately, and each of their costs includes unstacking the same blocks from the original tower; the shared
    work is counted once per goal. $h_{\mathrm{FF}}$ counts each action in its relaxed plan once, which is why it
    gives 9.

??? question "5. In the partial-order plan for the Sussman anomaly, which causal links could Unstack(C,A) threaten, and why is none of them threatened in the final plan?"

    Unstack(C,A) deletes $\mathit{On}(C,A)$, $\mathit{Clear}(C)$ and $\mathit{HandEmpty}$. Links carrying those atoms:
    Start $\to$ Unstack(C,A) for all three (its own preconditions, so no threat: a step does not threaten links into
    itself); PutDown(C) $\xrightarrow{\mathit{HandEmpty}}$ PickUp(B); Stack(B,C) $\xrightarrow{\mathit{HandEmpty}}$
    PickUp(A); and Start $\xrightarrow{\mathit{HandEmpty}}$ Unstack(C,A). Since Unstack(C,A) $\prec$ PutDown(C) $\prec$
    PickUp(B) $\prec$ Stack(B,C), Unstack(C,A) is ordered before the producer of each of the other two links, so it
    cannot fall inside them: they were resolved by demotion.

??? question "6. Why are Holding(B) and OnTable(B) mutex at level 1 of the Sussman planning graph, but Clear(A) and Clear(B) not?"

    At level 1, $\mathit{Holding}(B)$ has one achiever, PickUp(B), and $\mathit{OnTable}(B)$ has one, its no-op. PickUp(B)
    deletes $\mathit{OnTable}(B)$, which is the no-op's precondition and effect (interference and inconsistent effects),
    so the two achievers are mutex, and so are the atoms. $\mathit{Clear}(A)$ is achieved by Unstack(C,A) and
    $\mathit{Clear}(B)$ by its no-op; Unstack(C,A) does not delete $\mathit{Clear}(B)$, and their preconditions are not
    mutex at level 0 (nothing is), so they are compatible. The program's list of the 11 level-1 mutex pairs contains the
    first pair and not the second.

??? question "7. A partial-order plan consists of three independent chains, each of two ordered steps. How many linearizations does it have?"

    Choose the positions of the steps of each chain among 6 slots; inside a chain the order is fixed. That is the
    multinomial $\frac{6!}{2!\,2!\,2!} = 90$. For two chains (shoes and socks) it is $\binom{4}{2} = 6$, matching the
    program.

??? question "8. Write the code: run weighted A* with h_max on the six-block problem with weights 1, 1.5, 2 and 3, and report plan length and nodes expanded. What does the weight guarantee?"

    ```python
    from ch10_strips import blocks_world, towers, forward, h_max

    acts = blocks_world("ABCDEF")
    init = towers([list("ABC"), list("DEF")])
    goal = frozenset({"On(A,F)", "On(F,B)", "On(B,E)", "On(E,C)", "On(C,D)"})
    for w in [1, 1.5, 2, 3]:
        plan, n = forward(init, goal, acts, h_max, weight=w)
        print(w, len(plan), n)
    ```

    Output: `1 14 1196`, `1.5 14 762`, `2 14 756`, `3 14 381`. With an admissible $h$, weighted A* with weight $w$
    returns a plan of cost at most $w$ times the optimum ([Chapter 4](04-Heuristic-Search.md)); here it even stays
    optimal while expanding a third as many nodes. (With the inadmissible $h_{\mathrm{add}}$ there is no such
    guarantee, and the plans get longer as $w$ grows.)

??? question "9. Write the code: count the states reachable in the blocks world with 3, 4 and 5 blocks, starting from all blocks on the table."

    ```python
    from collections import deque
    from ch10_strips import blocks_world, towers, result

    for n in [3, 4, 5]:
        names = "ABCDE"[:n]
        acts = blocks_world(names)
        start = towers([[b] for b in names])
        seen, queue = {start}, deque([start])
        while queue:
            s = queue.popleft()
            for a in acts:
                if a.pre <= s:
                    t = result(s, a)
                    if t not in seen:
                        seen.add(t)
                        queue.append(t)
        print(n, len(seen), sum(1 for s in seen if "HandEmpty" in s))
    ```

    It prints `3 22 13`, `4 125 73`, `5 866 501`. The counts with the hand empty (13, 73, 501) are the numbers of ways
    to arrange $n$ labelled blocks into towers; the extra states have one block in the hand. The growth (roughly a
    factor of 7 per block here, and faster later) is why blind search fails beyond a few blocks.

??? question "10. In the CPM table, the panorama has slack 155. What happens to the makespan if the panorama takes 200 minutes instead of 40?"

    Its earliest finish becomes $30 + 200 = 230$, later than the spectrometer's finish (225) and the close-up's (185), so
    the downlink's earliest start becomes 230 and the makespan $230 + 30 = 260$: five minutes later. The slack of 155
    minutes allowed a delay of 155 minutes; a lengthening of 160 minutes uses it up and 5 more, and the panorama joins
    the critical path. (Checked with `cpm` on the modified table.)

??? question "11. (Advanced) Show that a STRIPS problem can need a plan of exponential length, and explain why plan existence is nevertheless in PSPACE."

    Towers of Hanoi with $n$ discs is a STRIPS problem with $O(n^2)$ atoms (which disc is on which disc or peg, which
    are clear) and needs $2^n - 1$ moves ([Algorithms, Chapter 3](../algorithms/03-Recursion-and-Induction.md)), so
    no algorithm can even write down its plan in polynomial time. Deciding whether a plan exists does not require
    writing it down: a nondeterministic algorithm guesses one action at a time, keeping only the current state ($m$
    bits) and a step counter up to $2^m$ ($m$ bits), so it uses polynomial space; by Savitch's theorem, nondeterministic
    polynomial space equals deterministic polynomial space. Bylander (1994) showed the problem is also PSPACE-hard.

??? question "12. (Advanced) Prove that in a planning graph, if two atoms p and q are not mutex at level k, they are not mutex at level k+1."

    Both $p$ and $q$ are present at level $k$, so their no-op actions are in action level $k$, and they achieve $p$ and
    $q$ at level $k+1$. The two no-ops are not mutex: they delete nothing, so there are no inconsistent effects or
    interference, and their preconditions ($p$ and $q$) are not mutex at level $k$, so there are no competing needs.
    Two atoms are mutex only if *every* pair of their achievers is mutex; here one pair is not, so $p$ and $q$ are not
    mutex at level $k+1$. A similar argument shows actions present at a level stay present, which together give the
    leveling-off property.

## What you learned

- Planning uses factored descriptions of actions (STRIPS, PDDL: preconditions, add and delete lists) so that one
  planner solves any problem written in the language, with heuristics derived from the description itself.
- Forward search applies applicable actions; backward search regresses goals through relevant actions, and
  $\mathrm{regress}(g, a) = (g \setminus \mathrm{add}(a)) \cup \mathrm{pre}(a)$ is the weakest precondition. Solving
  goals one at a time fails (the Sussman anomaly).
- Ignoring delete lists gives a relaxation whose optimum $h^+$ is admissible but NP-hard; $h_{\max}$ is admissible,
  $h_{\mathrm{add}}$ and $h_{\mathrm{FF}}$ are not but guide search far better, which is how modern planners work.
- Partial-order planning keeps only necessary orderings, protects causal links from threats, and every linearization
  of a flawless plan is valid; GraphPlan's polynomial-size planning graph with mutexes gives admissible estimates and
  parallel plans.
- HTN planning refines tasks with expert methods (fast, predictable, more expressive than STRIPS); scheduling assigns
  times, CPM finds the critical path as a longest path in a DAG, and resource limits make it NP-hard.
- Real spacecraft pair planners with executives and diagnosis (Remote Agent, 1999); Mars rover activity planning is
  mixed-initiative on the ground (MAPGEN), with onboard autonomy for targeting and driving (AEGIS, AutoNav).

**Next:** [Chapter 11](11-Knowledge-Representation.md) asks how to organise what an agent knows: categories and
inheritance, frames and description logics, events and time, defaults, and the knowledge graphs of today.

## Further reading

- S. Russell and P. Norvig, *Artificial Intelligence: A Modern Approach*, 4th ed., 2020: chapter 11 (automated
  planning).
- M. Ghallab, D. Nau and P. Traverso, *Automated Planning: Theory and Practice*, 2004, and *Automated Planning and
  Acting*, 2016 (the standard graduate texts).
- R. E. Fikes and N. J. Nilsson, "STRIPS: a new approach to the application of theorem proving to problem solving",
  *Artificial Intelligence* 2, 1971.
- D. McDermott et al., "PDDL: the Planning Domain Definition Language", technical report, 1998; M. Fox and D. Long,
  "PDDL2.1: an extension to PDDL for expressing temporal planning domains", *Journal of Artificial Intelligence
  Research* 20, 2003.
- T. Bylander, "The computational complexity of propositional STRIPS planning", *Artificial Intelligence* 69, 1994.
- G. J. Sussman, *A Computer Model of Skill Acquisition*, 1975 (from his 1973 thesis).
- B. Bonet and H. Geffner, "Planning as heuristic search", *Artificial Intelligence* 129, 2001; J. Hoffmann and
  B. Nebel, "The FF planning system: fast plan generation through heuristic search", *Journal of Artificial
  Intelligence Research* 14, 2001; M. Helmert, "The Fast Downward planning system", *Journal of Artificial
  Intelligence Research* 26, 2006.
- D. McAllester and D. Rosenblitt, "Systematic nonlinear planning", AAAI 1991; J. S. Penberthy and D. S. Weld,
  "UCPOP: a sound, complete, partial order planner for ADL", KR 1992.
- A. L. Blum and M. L. Furst, "Fast planning through planning graph analysis", *Artificial Intelligence* 90, 1997
  (IJCAI 1995); H. Kautz and B. Selman, "Pushing the envelope: planning, propositional logic, and stochastic search",
  AAAI 1996.
- E. D. Sacerdoti, "The nonlinear nature of plans", IJCAI 1975; K. Erol, J. Hendler and D. S. Nau, "HTN planning:
  complexity and expressivity", AAAI 1994; D. Nau et al., "SHOP2: an HTN planning system", *Journal of Artificial
  Intelligence Research* 20, 2003.
- J. E. Kelley and M. R. Walker, "Critical-path planning and scheduling", Eastern Joint Computer Conference, 1959;
  J. Blazewicz, J. K. Lenstra and A. H. G. Rinnooy Kan, "Scheduling subject to resource constraints: classification
  and complexity", *Discrete Applied Mathematics* 5, 1983.
- N. Muscettola, P. P. Nayak, B. Pell and B. C. Williams, "Remote Agent: to boldly go where no AI system has gone
  before", *Artificial Intelligence* 103, 1998.
- J. Bresina, A. Jónsson, P. Morris and K. Rajan, "Activity planning for the Mars Exploration Rovers", ICAPS 2005;
  S. Chien et al., "Using autonomy flight software to improve science return on Earth Observing One", *Journal of
  Aerospace Computing, Information, and Communication* 2, 2005.
- T. Estlin et al., "AEGIS automated science targeting for the MER Opportunity rover", *ACM Transactions on Intelligent
  Systems and Technology* 3, 2012; R. Francis et al., "AEGIS autonomous targeting for ChemCam on Mars Science
  Laboratory: deployment and results of initial science team use", *Science Robotics* 2, 2017.
- On this site: the Algorithms book's [Chapter 15](../algorithms/15-Graphs-and-Graph-Search.md) (topological sort,
  BFS), [Chapter 13](../algorithms/13-Dynamic-Programming.md) (longest paths in DAGs) and
  [Chapter 22](../algorithms/22-NP-Completeness.md) (NP-completeness, PSPACE); the reference pages for
  [BFS](../../graphs/bfs.md), [Dijkstra's algorithm](../../graphs/dijkstra.md) and
  [topological sort](../../graphs/topological-sort.md); this book's [Chapter 4](04-Heuristic-Search.md) (A*) and
  [Chapter 7](07-Constraint-Satisfaction.md) (constraint satisfaction, which schedulers use).
