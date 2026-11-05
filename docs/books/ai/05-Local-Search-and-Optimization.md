# 5. Local search and optimization

*The searches of Chapters 3 and 4 return a path: the sequence of actions that leads from the start to a goal. Many
problems do not care about the path at all. When you place eight queens on a board, schedule exams into rooms, or lay
out a tour of sixty cities, only the final arrangement matters, and the number of arrangements is far too large to
store a frontier of them. This chapter answers the question: how do you search a huge space when all you keep is one
state (or a few), and all you can do is change it a little and see whether it got better? You will build hill
climbing, simulated annealing, local beam search and a genetic algorithm from scratch, prove what can be proved about
each (when they stop, why random restarts work, why annealing samples the right distribution), move to continuous
spaces where the gradient tells you which way is up, and finally drop two assumptions of classical search: that
actions have one outcome, and that the agent can see the state.*

!!! abstract "In this chapter"
    **You will learn:**

    - the complete-state formulation, objective functions and the state-space landscape
    - hill climbing and its traps (local maxima, plateaus, ridges), and why random restarts work, with the expected cost
    - simulated annealing: the Metropolis rule, why it samples the Boltzmann distribution, and a from-scratch TSP solver
    - local beam search and genetic algorithms, built and measured on 8-queens
    - local search in continuous spaces: gradients, step sizes, Newton's method, and their link to machine learning
    - AND-OR search for actions with several outcomes, conditional plans, and search over belief states

    **You need:** [Chapter 3](03-Uninformed-Search.md) (states, actions, search trees) and
    [Chapter 4](04-Heuristic-Search.md) (heuristics). A little probability (expected value of a geometric random
    variable; [Probability](https://math.akadian.ca/books/probability/)) for 5.2 and 5.3, and derivatives
    ([Calculus](https://math.akadian.ca/books/calculus/)) for 5.5.

    **Levels:** 5.1 and 5.2 are beginner; 5.3 and 5.4 are intermediate (the proofs in 5.3 are advanced);
    5.5 is intermediate; 5.6 is advanced.

## 5.1 When the path doesn't matter: n-queens, scheduling

Put eight queens on a chessboard so that no two attack each other. A queen attacks along its row, its column and both
diagonals. In [Chapter 3](03-Uninformed-Search.md) we would treat this as a path problem: start with an empty board and
add queens one at a time. But nobody cares in which order the queens were placed. The answer is the final board.

Problems like this are everywhere:

- **Scheduling.** Assign 300 exams to 20 time slots so that no student has two exams at once and as few as possible
  have two on the same day. The answer is the timetable.
- **Layout.** Place the components of a chip, or the rooms of a building, to keep wires or corridors short.
- **Tours.** Visit 60 cities and return home along the shortest closed route (the travelling salesman problem, TSP).
- **Fitting.** Choose the numbers inside a model so that it fits data well; this is all of machine learning.

For these we use a different formulation. In the **complete-state formulation**, every state is a full candidate
answer: all eight queens on the board, every exam in some slot, a complete tour. A state may be bad (queens attacking,
students clashing, a long tour), but it is complete. An **objective function** scores each state. We either maximise
it (a "value", higher is better) or minimise it (a "cost", lower is better); the two are the same problem with the sign
flipped, and this chapter uses whichever reads more naturally. A **neighbour** of a state is any state reached by one
small change, and the set of all of them is its **neighbourhood**.

For $n$-queens, the usual choice is:

- **state:** one queen in each column, so a state is a list `queen[0..n-1]`, where `queen[c]` is the row of the queen
  in column `c`;
- **neighbour:** move one queen to another row of its own column, so each state has $n(n-1)$ neighbours (56 for
  $n = 8$);
- **cost:** $h$ = the number of pairs of queens that attack each other (same row or same diagonal; columns cannot
  clash by construction). A solution has $h = 0$, and the worst possible is $\binom{n}{2} = 28$ for $n = 8$.

There are $8^8 = 16\,777\,216$ such states. That is not huge for a computer, but $n = 100$ gives $100^{100}$, and
local search does not care: it never lists the states.

**Local search** means: keep one current state (or a few), look only at its neighbours, move to one of them, repeat.
It has two great strengths. It uses a constant amount of memory (one state, not a frontier of millions), and it can
find good answers in spaces so large or so continuous that systematic search is hopeless. It has one great weakness:
it usually cannot prove that a better answer does not exist, and some versions cannot even tell you that no answer
exists at all.

A helpful picture is the **state-space landscape**. Lay the states out along the ground, with neighbours next to each
other, and let the height of the ground at each state be its objective value. Maximising means climbing to the highest
peak; minimising means finding the lowest valley. The **global maximum** is the highest point anywhere; a **local
maximum** is a point higher than all its neighbours but not the highest overall.

<figure class="mars-fig" markdown="0">
<svg viewBox="0 0 640 260" role="img" aria-label="A one-dimensional state-space landscape: a curve over the states with a local maximum, a shoulder, the global maximum and a flat local maximum. An arrow shows a hill climber stuck on the local maximum.">
<line x1="40" y1="220" x2="615" y2="220" stroke="currentColor" stroke-width="1.2"/>
<line x1="40" y1="220" x2="40" y2="20" stroke="currentColor" stroke-width="1.2"/>
<polyline points="40,200 80,160 130,110 160,135 190,165 220,150 250,140 320,140 360,100 420,40 455,95 480,150 510,130 530,120 580,120 600,150 610,170" fill="none" stroke="#eea66f" stroke-width="3"/>
<text x="130" y="98" font-size="13" text-anchor="middle" fill="currentColor">local maximum</text>
<text x="285" y="128" font-size="13" text-anchor="middle" fill="currentColor">shoulder</text>
<text x="420" y="28" font-size="13" text-anchor="middle" fill="currentColor">global maximum</text>
<text x="555" y="108" font-size="13" text-anchor="middle" fill="currentColor">flat local maximum</text>
<circle cx="130" cy="110" r="5" fill="#7ccf9a" stroke="currentColor"/>
<circle cx="420" cy="40" r="5" fill="#7ccf9a" stroke="currentColor"/>
<circle cx="80" cy="160" r="6" fill="#9cc9ea" stroke="currentColor"/>
<text x="80" y="185" font-size="12" text-anchor="middle" fill="currentColor">current state</text>
<line x1="88" y1="151" x2="118" y2="121" stroke="currentColor" stroke-width="1.3"/>
<polygon points="123,116 114,120 119,125" fill="currentColor"/>
<text x="327" y="245" font-size="13" text-anchor="middle" fill="currentColor">state space</text>
<text x="24" y="120" font-size="13" text-anchor="middle" fill="currentColor" transform="rotate(-90 24 120)">objective</text>
</svg>
<figcaption>Figure 5.1. A state-space landscape in one dimension. Hill climbing from the blue state goes uphill and stops at the local maximum: every neighbour is lower, although the global maximum is higher. On the shoulder and on the flat local maximum every neighbour has the same value, so a climber has no direction.</figcaption>
</figure>

The picture is honest about one thing and misleading about another. It is honest that local search sees only the
ground near its feet. It is misleading because real landscapes have not one dimension but thousands, and each state
has many neighbours, so "being stuck" is rarer than the picture suggests, and plateaus are far more common.

**A note on scheduling.** For exam timetabling, a state assigns every exam a slot; a neighbour moves one exam to another
slot or swaps two exams; the cost counts clashes, with a large weight for a student with two exams at once (a **hard
constraint**, which must hold) and a small weight for two exams on one day (a **soft constraint**, which we would like
to hold). Everything in this chapter applies unchanged. [Chapter 7](07-Constraint-Satisfaction.md) returns to such
problems with methods that exploit their structure, and its min-conflicts algorithm is hill climbing specialised to
constraints.

## 5.2 Hill climbing and its traps; random restarts

The simplest local search is the one you would invent yourself. Look at all the neighbours, move to the best one, and
stop when no neighbour is better. Climbing a hill in thick fog, you feel the ground around you and step uphill.

```python
def hill_climb(state):
    while True:
        best = the neighbour of state with the best objective
        if best is not better than state:
            return state             # a peak: no neighbour is higher
        state = best
```

This is **steepest-ascent hill climbing** (for a cost to minimise we should call it steepest descent, but the name
"hill climbing" is used for both). It keeps no search tree and never looks back.

### A trace by hand on 4-queens

Take $n = 4$ and number rows 0 to 3 from the bottom. A state is written as the four rows, column by column.

| step | state | h | best neighbour value | moves reaching it |
|---|---|---|---|---|
| 0 | [1, 1, 1, 1] | 6 | 4 | 8 moves, e.g. column 0 to row 0 |
| 1 | [0, 1, 1, 1] | 4 | 2 | column 1 to row 2, column 1 to row 3, column 2 to row 3 |
| 2 | [0, 2, 1, 1] | 2 | 1 | column 2 to row 3 |
| 3 | [0, 2, 3, 1] | 1 | 1 | column 1 to row 0 (no improvement) |

At step 3 the best neighbour has the same value as the current state, so plain hill climbing stops with $h = 1$.
Check the final board: the queens at (column 1, row 2) and (column 2, row 3) are on one diagonal; no other pair attacks.
The two solutions of 4-queens are [1, 3, 0, 2] and [2, 0, 3, 1], and [0, 2, 3, 1] is not one move from either. We are
stuck on a **local minimum** of $h$: a state from which every single move makes things no better.

### When does it stop, and how long does each step take?

**Claim.** On $n$-queens, steepest-ascent hill climbing that moves only to strictly better neighbours stops after at
most $\binom{n}{2}$ moves.

*Proof.* $h$ is a whole number between 0 and $\binom{n}{2}$. Every move decreases it by at least 1. A decreasing
sequence of whole numbers that starts at most at $\binom{n}{2}$ and never goes below 0 has at most $\binom{n}{2}$
steps. $\square$

The same argument works for any problem with a finite set of objective values: plain hill climbing always stops,
because it can never revisit a state (each move strictly improves). It does not say the stopping point is a solution.

The cost of one step is the number of neighbours times the cost of scoring each. With $n(n-1)$ neighbours and a naive
$O(n^2)$ count of attacking pairs, a step costs $O(n^4)$. The program below is smarter: moving the queen of column $c$
changes $h$ only through the pairs that involve that queen, so
$h_{\text{new}} = h - a_{\text{old}} + a_{\text{new}}$, where $a_{\text{old}}$ and $a_{\text{new}}$ count the
queens attacking the old and the new square, each in $O(n)$; that is $O(n^3)$ per step. Keeping counts of queens per
row and per diagonal brings it down to $O(n^2)$, one constant-time update per neighbour.

### The traps

Figure 5.1 shows the three things that stop a hill climber:

- **Local maxima** (local minima, for a cost): every neighbour is worse. The 4-queens trace ended on one.
- **Plateaus**: a flat region where all neighbours have the same value. A **flat local maximum** has no way up at all;
  a **shoulder** is a flat region from which progress is possible further along. On a plateau the climber has no
  information about direction.
- **Ridges**: a sequence of local maxima that rises, but in a direction that no single move follows. Picture a narrow
  ridge running diagonally across a grid where each move goes north, south, east or west: every single step falls off
  the ridge, so every point on it looks like a peak, even though walking along it diagonally would keep climbing.

Here is a real 8-queens state, with the value of every possible move written in its square:

<figure class="mars-fig" markdown="0">
<svg viewBox="0 0 312 320" role="img" aria-label="An 8 by 8 board with one queen in each column. Each empty square shows the number of attacking pairs if that column's queen moved there. The current board has 17 attacking pairs; the best moves give 12.">
<rect x="20" y="248" width="34" height="34" fill="#9cc9ea" fill-opacity="0.35" stroke="currentColor" stroke-width="0.6"/>
<text x="37.0" y="270" font-size="13" text-anchor="middle" fill="currentColor">18</text>
<rect x="20" y="214" width="34" height="34" fill="none" stroke="currentColor" stroke-width="0.6"/>
<text x="37.0" y="236" font-size="13" text-anchor="middle" fill="currentColor">14</text>
<rect x="20" y="180" width="34" height="34" fill="#9cc9ea" fill-opacity="0.35" stroke="currentColor" stroke-width="0.6"/>
<text x="37.0" y="202" font-size="13" text-anchor="middle" fill="currentColor">14</text>
<rect x="20" y="146" width="34" height="34" fill="none" stroke="currentColor" stroke-width="0.6"/>
<text x="37.0" y="168" font-size="13" text-anchor="middle" fill="currentColor">15</text>
<rect x="20" y="112" width="34" height="34" fill="#9cc9ea" fill-opacity="0.35" stroke="currentColor" stroke-width="0.6"/>
<circle cx="37.0" cy="129.0" r="11" fill="#eea66f" stroke="currentColor" stroke-width="1.2"/>
<text x="37.0" y="134.0" font-size="13" text-anchor="middle" fill="currentColor" font-weight="bold">Q</text>
<rect x="20" y="78" width="34" height="34" fill="none" stroke="currentColor" stroke-width="0.6"/>
<text x="37.0" y="100" font-size="13" text-anchor="middle" fill="currentColor">17</text>
<rect x="20" y="44" width="34" height="34" fill="#9cc9ea" fill-opacity="0.35" stroke="currentColor" stroke-width="0.6"/>
<text x="37.0" y="66" font-size="13" text-anchor="middle" fill="currentColor">18</text>
<rect x="20" y="10" width="34" height="34" fill="none" stroke="currentColor" stroke-width="0.6"/>
<text x="37.0" y="32" font-size="13" text-anchor="middle" fill="currentColor">14</text>
<rect x="54" y="248" width="34" height="34" fill="none" stroke="currentColor" stroke-width="0.6"/>
<rect x="57" y="251" width="28" height="28" rx="4" fill="#7ccf9a" fill-opacity="0.7"/>
<text x="71.0" y="270" font-size="13" text-anchor="middle" fill="currentColor">12</text>
<rect x="54" y="214" width="34" height="34" fill="#9cc9ea" fill-opacity="0.35" stroke="currentColor" stroke-width="0.6"/>
<text x="71.0" y="236" font-size="13" text-anchor="middle" fill="currentColor">16</text>
<rect x="54" y="180" width="34" height="34" fill="none" stroke="currentColor" stroke-width="0.6"/>
<rect x="57" y="183" width="28" height="28" rx="4" fill="#7ccf9a" fill-opacity="0.7"/>
<text x="71.0" y="202" font-size="13" text-anchor="middle" fill="currentColor">12</text>
<rect x="54" y="146" width="34" height="34" fill="#9cc9ea" fill-opacity="0.35" stroke="currentColor" stroke-width="0.6"/>
<text x="71.0" y="168" font-size="13" text-anchor="middle" fill="currentColor">14</text>
<rect x="54" y="112" width="34" height="34" fill="none" stroke="currentColor" stroke-width="0.6"/>
<text x="71.0" y="134" font-size="13" text-anchor="middle" fill="currentColor">14</text>
<rect x="54" y="78" width="34" height="34" fill="#9cc9ea" fill-opacity="0.35" stroke="currentColor" stroke-width="0.6"/>
<circle cx="71.0" cy="95.0" r="11" fill="#eea66f" stroke="currentColor" stroke-width="1.2"/>
<text x="71.0" y="100.0" font-size="13" text-anchor="middle" fill="currentColor" font-weight="bold">Q</text>
<rect x="54" y="44" width="34" height="34" fill="none" stroke="currentColor" stroke-width="0.6"/>
<text x="71.0" y="66" font-size="13" text-anchor="middle" fill="currentColor">14</text>
<rect x="54" y="10" width="34" height="34" fill="#9cc9ea" fill-opacity="0.35" stroke="currentColor" stroke-width="0.6"/>
<text x="71.0" y="32" font-size="13" text-anchor="middle" fill="currentColor">14</text>
<rect x="88" y="248" width="34" height="34" fill="#9cc9ea" fill-opacity="0.35" stroke="currentColor" stroke-width="0.6"/>
<text x="105.0" y="270" font-size="13" text-anchor="middle" fill="currentColor">14</text>
<rect x="88" y="214" width="34" height="34" fill="none" stroke="currentColor" stroke-width="0.6"/>
<text x="105.0" y="236" font-size="13" text-anchor="middle" fill="currentColor">13</text>
<rect x="88" y="180" width="34" height="34" fill="#9cc9ea" fill-opacity="0.35" stroke="currentColor" stroke-width="0.6"/>
<text x="105.0" y="202" font-size="13" text-anchor="middle" fill="currentColor">18</text>
<rect x="88" y="146" width="34" height="34" fill="none" stroke="currentColor" stroke-width="0.6"/>
<text x="105.0" y="168" font-size="13" text-anchor="middle" fill="currentColor">14</text>
<rect x="88" y="112" width="34" height="34" fill="#9cc9ea" fill-opacity="0.35" stroke="currentColor" stroke-width="0.6"/>
<text x="105.0" y="134" font-size="13" text-anchor="middle" fill="currentColor">17</text>
<rect x="88" y="78" width="34" height="34" fill="none" stroke="currentColor" stroke-width="0.6"/>
<text x="105.0" y="100" font-size="13" text-anchor="middle" fill="currentColor">16</text>
<rect x="88" y="44" width="34" height="34" fill="#9cc9ea" fill-opacity="0.35" stroke="currentColor" stroke-width="0.6"/>
<circle cx="105.0" cy="61.0" r="11" fill="#eea66f" stroke="currentColor" stroke-width="1.2"/>
<text x="105.0" y="66.0" font-size="13" text-anchor="middle" fill="currentColor" font-weight="bold">Q</text>
<rect x="88" y="10" width="34" height="34" fill="none" stroke="currentColor" stroke-width="0.6"/>
<text x="105.0" y="32" font-size="13" text-anchor="middle" fill="currentColor">13</text>
<rect x="122" y="248" width="34" height="34" fill="none" stroke="currentColor" stroke-width="0.6"/>
<text x="139.0" y="270" font-size="13" text-anchor="middle" fill="currentColor">13</text>
<rect x="122" y="214" width="34" height="34" fill="#9cc9ea" fill-opacity="0.35" stroke="currentColor" stroke-width="0.6"/>
<text x="139.0" y="236" font-size="13" text-anchor="middle" fill="currentColor">15</text>
<rect x="122" y="180" width="34" height="34" fill="none" stroke="currentColor" stroke-width="0.6"/>
<text x="139.0" y="202" font-size="13" text-anchor="middle" fill="currentColor">13</text>
<rect x="122" y="146" width="34" height="34" fill="#9cc9ea" fill-opacity="0.35" stroke="currentColor" stroke-width="0.6"/>
<circle cx="139.0" cy="163.0" r="11" fill="#eea66f" stroke="currentColor" stroke-width="1.2"/>
<text x="139.0" y="168.0" font-size="13" text-anchor="middle" fill="currentColor" font-weight="bold">Q</text>
<rect x="122" y="112" width="34" height="34" fill="none" stroke="currentColor" stroke-width="0.6"/>
<text x="139.0" y="134" font-size="13" text-anchor="middle" fill="currentColor">15</text>
<rect x="122" y="78" width="34" height="34" fill="#9cc9ea" fill-opacity="0.35" stroke="currentColor" stroke-width="0.6"/>
<text x="139.0" y="100" font-size="13" text-anchor="middle" fill="currentColor">18</text>
<rect x="122" y="44" width="34" height="34" fill="none" stroke="currentColor" stroke-width="0.6"/>
<text x="139.0" y="66" font-size="13" text-anchor="middle" fill="currentColor">15</text>
<rect x="122" y="10" width="34" height="34" fill="#9cc9ea" fill-opacity="0.35" stroke="currentColor" stroke-width="0.6"/>
<text x="139.0" y="32" font-size="13" text-anchor="middle" fill="currentColor">17</text>
<rect x="156" y="248" width="34" height="34" fill="#9cc9ea" fill-opacity="0.35" stroke="currentColor" stroke-width="0.6"/>
<text x="173.0" y="270" font-size="13" text-anchor="middle" fill="currentColor">13</text>
<rect x="156" y="214" width="34" height="34" fill="none" stroke="currentColor" stroke-width="0.6"/>
<rect x="159" y="217" width="28" height="28" rx="4" fill="#7ccf9a" fill-opacity="0.7"/>
<text x="173.0" y="236" font-size="13" text-anchor="middle" fill="currentColor">12</text>
<rect x="156" y="180" width="34" height="34" fill="#9cc9ea" fill-opacity="0.35" stroke="currentColor" stroke-width="0.6"/>
<text x="173.0" y="202" font-size="13" text-anchor="middle" fill="currentColor">15</text>
<rect x="156" y="146" width="34" height="34" fill="none" stroke="currentColor" stroke-width="0.6"/>
<text x="173.0" y="168" font-size="13" text-anchor="middle" fill="currentColor">13</text>
<rect x="156" y="112" width="34" height="34" fill="#9cc9ea" fill-opacity="0.35" stroke="currentColor" stroke-width="0.6"/>
<circle cx="173.0" cy="129.0" r="11" fill="#eea66f" stroke="currentColor" stroke-width="1.2"/>
<text x="173.0" y="134.0" font-size="13" text-anchor="middle" fill="currentColor" font-weight="bold">Q</text>
<rect x="156" y="78" width="34" height="34" fill="none" stroke="currentColor" stroke-width="0.6"/>
<text x="173.0" y="100" font-size="13" text-anchor="middle" fill="currentColor">15</text>
<rect x="156" y="44" width="34" height="34" fill="#9cc9ea" fill-opacity="0.35" stroke="currentColor" stroke-width="0.6"/>
<text x="173.0" y="66" font-size="13" text-anchor="middle" fill="currentColor">15</text>
<rect x="156" y="10" width="34" height="34" fill="none" stroke="currentColor" stroke-width="0.6"/>
<rect x="159" y="13" width="28" height="28" rx="4" fill="#7ccf9a" fill-opacity="0.7"/>
<text x="173.0" y="32" font-size="13" text-anchor="middle" fill="currentColor">12</text>
<rect x="190" y="248" width="34" height="34" fill="none" stroke="currentColor" stroke-width="0.6"/>
<rect x="193" y="251" width="28" height="28" rx="4" fill="#7ccf9a" fill-opacity="0.7"/>
<text x="207.0" y="270" font-size="13" text-anchor="middle" fill="currentColor">12</text>
<rect x="190" y="214" width="34" height="34" fill="#9cc9ea" fill-opacity="0.35" stroke="currentColor" stroke-width="0.6"/>
<text x="207.0" y="236" font-size="13" text-anchor="middle" fill="currentColor">14</text>
<rect x="190" y="180" width="34" height="34" fill="none" stroke="currentColor" stroke-width="0.6"/>
<rect x="193" y="183" width="28" height="28" rx="4" fill="#7ccf9a" fill-opacity="0.7"/>
<text x="207.0" y="202" font-size="13" text-anchor="middle" fill="currentColor">12</text>
<rect x="190" y="146" width="34" height="34" fill="#9cc9ea" fill-opacity="0.35" stroke="currentColor" stroke-width="0.6"/>
<text x="207.0" y="168" font-size="13" text-anchor="middle" fill="currentColor">16</text>
<rect x="190" y="112" width="34" height="34" fill="none" stroke="currentColor" stroke-width="0.6"/>
<text x="207.0" y="134" font-size="13" text-anchor="middle" fill="currentColor">14</text>
<rect x="190" y="78" width="34" height="34" fill="#9cc9ea" fill-opacity="0.35" stroke="currentColor" stroke-width="0.6"/>
<circle cx="207.0" cy="95.0" r="11" fill="#eea66f" stroke="currentColor" stroke-width="1.2"/>
<text x="207.0" y="100.0" font-size="13" text-anchor="middle" fill="currentColor" font-weight="bold">Q</text>
<rect x="190" y="44" width="34" height="34" fill="none" stroke="currentColor" stroke-width="0.6"/>
<text x="207.0" y="66" font-size="13" text-anchor="middle" fill="currentColor">14</text>
<rect x="190" y="10" width="34" height="34" fill="#9cc9ea" fill-opacity="0.35" stroke="currentColor" stroke-width="0.6"/>
<text x="207.0" y="32" font-size="13" text-anchor="middle" fill="currentColor">14</text>
<rect x="224" y="248" width="34" height="34" fill="#9cc9ea" fill-opacity="0.35" stroke="currentColor" stroke-width="0.6"/>
<text x="241.0" y="270" font-size="13" text-anchor="middle" fill="currentColor">14</text>
<rect x="224" y="214" width="34" height="34" fill="none" stroke="currentColor" stroke-width="0.6"/>
<rect x="227" y="217" width="28" height="28" rx="4" fill="#7ccf9a" fill-opacity="0.7"/>
<text x="241.0" y="236" font-size="13" text-anchor="middle" fill="currentColor">12</text>
<rect x="224" y="180" width="34" height="34" fill="#9cc9ea" fill-opacity="0.35" stroke="currentColor" stroke-width="0.6"/>
<text x="241.0" y="202" font-size="13" text-anchor="middle" fill="currentColor">14</text>
<rect x="224" y="146" width="34" height="34" fill="none" stroke="currentColor" stroke-width="0.6"/>
<text x="241.0" y="168" font-size="13" text-anchor="middle" fill="currentColor">13</text>
<rect x="224" y="112" width="34" height="34" fill="#9cc9ea" fill-opacity="0.35" stroke="currentColor" stroke-width="0.6"/>
<text x="241.0" y="134" font-size="13" text-anchor="middle" fill="currentColor">16</text>
<rect x="224" y="78" width="34" height="34" fill="none" stroke="currentColor" stroke-width="0.6"/>
<text x="241.0" y="100" font-size="13" text-anchor="middle" fill="currentColor">15</text>
<rect x="224" y="44" width="34" height="34" fill="#9cc9ea" fill-opacity="0.35" stroke="currentColor" stroke-width="0.6"/>
<circle cx="241.0" cy="61.0" r="11" fill="#eea66f" stroke="currentColor" stroke-width="1.2"/>
<text x="241.0" y="66.0" font-size="13" text-anchor="middle" fill="currentColor" font-weight="bold">Q</text>
<rect x="224" y="10" width="34" height="34" fill="none" stroke="currentColor" stroke-width="0.6"/>
<rect x="227" y="13" width="28" height="28" rx="4" fill="#7ccf9a" fill-opacity="0.7"/>
<text x="241.0" y="32" font-size="13" text-anchor="middle" fill="currentColor">12</text>
<rect x="258" y="248" width="34" height="34" fill="none" stroke="currentColor" stroke-width="0.6"/>
<text x="275.0" y="270" font-size="13" text-anchor="middle" fill="currentColor">14</text>
<rect x="258" y="214" width="34" height="34" fill="#9cc9ea" fill-opacity="0.35" stroke="currentColor" stroke-width="0.6"/>
<text x="275.0" y="236" font-size="13" text-anchor="middle" fill="currentColor">16</text>
<rect x="258" y="180" width="34" height="34" fill="none" stroke="currentColor" stroke-width="0.6"/>
<text x="275.0" y="202" font-size="13" text-anchor="middle" fill="currentColor">14</text>
<rect x="258" y="146" width="34" height="34" fill="#9cc9ea" fill-opacity="0.35" stroke="currentColor" stroke-width="0.6"/>
<text x="275.0" y="168" font-size="13" text-anchor="middle" fill="currentColor">16</text>
<rect x="258" y="112" width="34" height="34" fill="none" stroke="currentColor" stroke-width="0.6"/>
<text x="275.0" y="134" font-size="13" text-anchor="middle" fill="currentColor">16</text>
<rect x="258" y="78" width="34" height="34" fill="#9cc9ea" fill-opacity="0.35" stroke="currentColor" stroke-width="0.6"/>
<circle cx="275.0" cy="95.0" r="11" fill="#eea66f" stroke="currentColor" stroke-width="1.2"/>
<text x="275.0" y="100.0" font-size="13" text-anchor="middle" fill="currentColor" font-weight="bold">Q</text>
<rect x="258" y="44" width="34" height="34" fill="none" stroke="currentColor" stroke-width="0.6"/>
<text x="275.0" y="66" font-size="13" text-anchor="middle" fill="currentColor">16</text>
<rect x="258" y="10" width="34" height="34" fill="#9cc9ea" fill-opacity="0.35" stroke="currentColor" stroke-width="0.6"/>
<text x="275.0" y="32" font-size="13" text-anchor="middle" fill="currentColor">18</text>
<text x="37.0" y="300" font-size="12" text-anchor="middle" fill="currentColor">0</text>
<text x="71.0" y="300" font-size="12" text-anchor="middle" fill="currentColor">1</text>
<text x="105.0" y="300" font-size="12" text-anchor="middle" fill="currentColor">2</text>
<text x="139.0" y="300" font-size="12" text-anchor="middle" fill="currentColor">3</text>
<text x="173.0" y="300" font-size="12" text-anchor="middle" fill="currentColor">4</text>
<text x="207.0" y="300" font-size="12" text-anchor="middle" fill="currentColor">5</text>
<text x="241.0" y="300" font-size="12" text-anchor="middle" fill="currentColor">6</text>
<text x="275.0" y="300" font-size="12" text-anchor="middle" fill="currentColor">7</text>
<text x="12" y="270" font-size="12" text-anchor="middle" fill="currentColor">0</text>
<text x="12" y="236" font-size="12" text-anchor="middle" fill="currentColor">1</text>
<text x="12" y="202" font-size="12" text-anchor="middle" fill="currentColor">2</text>
<text x="12" y="168" font-size="12" text-anchor="middle" fill="currentColor">3</text>
<text x="12" y="134" font-size="12" text-anchor="middle" fill="currentColor">4</text>
<text x="12" y="100" font-size="12" text-anchor="middle" fill="currentColor">5</text>
<text x="12" y="66" font-size="12" text-anchor="middle" fill="currentColor">6</text>
<text x="12" y="32" font-size="12" text-anchor="middle" fill="currentColor">7</text>
<text x="156" y="318" font-size="12" text-anchor="middle" fill="currentColor">column (row numbers at the left, 0 at the bottom)</text>
</svg>
<figcaption>Figure 5.2. The board [4, 5, 6, 3, 4, 5, 6, 5] has h = 17 attacking pairs. The number in each empty square is h after moving that column's queen there. The best moves (green) give h = 12; steepest-ascent hill climbing picks one of them at random.</figcaption>
</figure>

### Sideways moves and random restarts

Two cheap fixes help enormously.

**Sideways moves.** When the best neighbour is equal, not better, move to it anyway, hoping the plateau is a shoulder.
Because a flat local maximum would trap the climber forever, cap the number of consecutive sideways moves (100 below).
With the cap, the termination proof still works: between two strict improvements there are at most 100 sideways moves,
so there are at most $101 \binom{n}{2}$ moves in total.

**Random restarts.** If a run gets stuck, start again from a new random state. "If at first you don't succeed, try,
try again." This turns any hill climber with a positive success probability into one that succeeds with probability
1, and we can say exactly how long it takes.

**Theorem.** Suppose each run, from an independent random start, succeeds with probability $p > 0$, a successful run
takes $s$ steps on average and a failed run $f$ steps on average. Then random-restart hill climbing needs $1/p$ runs on
average, and its expected total number of steps is

$$
s + \frac{1 - p}{p} f.
$$

*Proof.* The number of runs $N$ until the first success is a geometric random variable: $\Pr[N = k] = (1-p)^{k-1} p$.
Its mean satisfies $\mathbb{E}[N] = 1 + (1 - p)\,\mathbb{E}[N]$ (one run always happens; with probability $1 - p$ it fails
and we are back where we started), so $\mathbb{E}[N] = 1/p$. Exactly one run succeeds, and $N - 1$ fail, with
$\mathbb{E}[N - 1] = (1 - p)/p$. Each failed run costs $f$ steps on average, independently of how many failures there
were, so by linearity of expectation (Wald's identity) the failures cost $\frac{1-p}{p} f$ steps in expectation, and the
final success adds $s$. $\square$

The probability that $k$ independent runs all fail is $(1 - p)^k$, which falls exponentially. With $p = 0.14$, 31 runs
fail together with probability below 1 percent (Exercise 3).

### The code, and what it measures

```python
--8<-- "books/ai/ch05_hill_climbing.py"
```

```
example board [4, 5, 6, 3, 4, 5, 6, 5] h = 17
best neighbour h = 12 reached by 8 moves, e.g. [(1, 0), (1, 2), (4, 1), (4, 7)]

 n  sideways  runs  solved   success  steps(success)  steps(failure)  expected steps with restarts
 8         0  1000     142     0.142             4.2             3.0        22.3
 8       100  1000     933     0.933            19.2            58.6        23.4
16         0   150       6     0.040             8.7             6.6       167.7
16       100   150     146     0.973            34.9            86.5        37.2

restarts needed (8-queens, no sideways), 10 tries: [1, 10, 6, 8, 6, 5, 2, 4, 9, 7]  mean 5.8
```

Read the table row by row.

- **Plain hill climbing on 8-queens** succeeds in about 14 percent of runs. It is fast either way, about 4 moves when it
  succeeds and 3 when it gets stuck, because $h$ drops quickly and then hits a local minimum.
- **With up to 100 sideways moves**, success jumps to about 93 percent, at the price of more steps per run (about 19 for
  a success, 59 for a failure, since a failing run spends its 100 allowed sideways moves wandering before it gives up).
- **The expected cost with restarts** is the formula above: $4.2 + \frac{0.858}{0.142} \cdot 3.0 \approx 22.3$ steps for
  plain hill climbing and $19.2 + \frac{0.067}{0.933} \cdot 58.6 \approx 23.4$ with sideways moves. Both solve 8-queens
  in a couple of dozen moves, out of 16.7 million states.
- **On 16-queens** plain hill climbing almost never succeeds (about 4 percent), but sideways moves raise it to about 97
  percent. Plateaus, not true local minima, are the main obstacle in $n$-queens, and they become more common as $n$
  grows.

These numbers are close to the ones Russell and Norvig report for 8-queens in their textbook (about 14 percent and 94
percent), which is a useful check that the program is right.

### Variants

- **Stochastic hill climbing** chooses at random among the uphill moves, with more chance for steeper ones. It climbs
  more slowly but sometimes finds better peaks.
- **First-choice hill climbing** generates random neighbours one at a time and takes the first that is better. This is
  the right choice when a state has thousands of neighbours (Exercise 8 codes it).
- **Tabu search** (Fred Glover, 1986) keeps a short list of recent moves and forbids undoing them, so the search can
  walk across plateaus and out of shallow valleys without cycling.

A hill climber that never moves downhill is **incomplete**: it can get stuck on a local maximum. A purely random walk
(move to a random neighbour, regardless of value) is complete in the sense that on a finite connected space it
eventually visits every state, but it is absurdly slow. The next two sections mix the two.

## 5.3 Simulated annealing on the travelling salesman problem

*Level: intermediate (the proofs are advanced).*

How do you get out of a local minimum? You have to go uphill (worse) for a while. But if you accept worse moves too
freely, you never settle. **Simulated annealing** accepts worse moves with a probability that depends on how much worse
they are and on a "temperature" that falls over time: at first the search wanders almost freely, later it only goes
downhill.

The name comes from metallurgy. To make a strong metal or a perfect crystal you heat it until its atoms move freely,
then cool it slowly. At each temperature the atoms jiggle into lower-energy arrangements, and slow cooling lets them
reach a nearly perfect, minimum-energy crystal. Cooling too fast (**quenching**) freezes the atoms into a disordered,
higher-energy state: a local minimum.

### The algorithm

Call the cost $E(s)$, the **energy**. Choose a starting temperature $T_0$ and a **schedule** that lowers $T$ over time.

1. Pick a random neighbour $s'$ of the current state $s$.
2. Let $\Delta = E(s') - E(s)$.
3. If $\Delta \le 0$ (not worse), move to $s'$.
4. Otherwise move to $s'$ with probability $e^{-\Delta / T}$, and stay at $s$ otherwise.
5. Lower $T$ a little and repeat.

The rule in steps 3 and 4 is the **Metropolis criterion**, from the 1953 paper by Nicholas Metropolis, Arianna and
Marshall Rosenbluth, and Augusta and Edward Teller, who used it to simulate atoms in a liquid on one of the first
computers. Scott Kirkpatrick, C. Daniel Gelatt and Mario Vecchi, physicists at IBM, saw in 1983 that the same rule,
with a falling temperature, is an optimisation method, and applied it to chip layout and the TSP; Vlado Černý published
the same idea independently in 1985.

Two features of $e^{-\Delta/T}$ do all the work. A move that is only a little worse (small $\Delta$) is accepted more
often than a much worse one. And as $T$ falls, every worse move becomes less likely; at $T$ near 0 the algorithm is a
stochastic hill climber. The first table printed by the program below shows the numbers.

### Why the Metropolis rule? The Boltzmann distribution

*Level: advanced.*

Hold the temperature fixed. Then simulated annealing is a **Markov chain**: a random walk over states in which the next
state depends only on the current one. Assume the neighbour proposal is **symmetric**: the chance $q(s, s')$ of
proposing $s'$ from $s$ equals the chance $q(s', s)$ of proposing $s$ from $s'$. (For the TSP below, reversing the
segment between positions $i$ and $j$ is undone by reversing the same segment again, and we choose $(i, j)$ with the
same probability in both tours, so the proposal is symmetric.)

**Theorem.** With a symmetric proposal, the Metropolis chain at temperature $T$ has the **Boltzmann distribution**

$$
\pi_T(s) = \frac{e^{-E(s)/T}}{Z_T}, \qquad Z_T = \sum_{u} e^{-E(u)/T}
$$

as a stationary distribution. If the chain is irreducible (every state can reach every other) and aperiodic, it
converges to $\pi_T$ from any start.

*Proof.* A distribution $\pi$ is stationary if the chain, started in $\pi$, is still in $\pi$ after one step. A
sufficient condition is **detailed balance**: for every pair of states, the flow from $s$ to $s'$ equals the flow back,
$\pi(s) P(s, s') = \pi(s') P(s', s)$, where $P(s, s') = q(s, s') A(s, s')$ and $A$ is the acceptance probability.
(Summing detailed balance over $s$ gives $\sum_s \pi(s) P(s, s') = \pi(s') \sum_s P(s', s) = \pi(s')$, which is
stationarity.) Take $s \ne s'$ and suppose, without loss of generality, $E(s') \ge E(s)$. Then $A(s, s') = e^{-(E(s') - E(s))/T}$
 and $A(s', s) = 1$, so

$$
\pi_T(s)\, q\, e^{-(E(s') - E(s))/T} = \frac{q}{Z_T} e^{-E(s')/T} = \pi_T(s')\, q \cdot 1,
$$

where $q = q(s, s') = q(s', s)$. Detailed balance holds. Convergence from any start is the basic convergence theorem for
finite irreducible aperiodic Markov chains. $\square$

Now look at what $\pi_T$ says. For any state $s$ and a global minimum $s^*$,

$$
\frac{\pi_T(s)}{\pi_T(s^*)} = e^{-(E(s) - E(s^*))/T},
$$

which tends to 0 as $T \to 0$ whenever $E(s) > E(s^*)$. **At low temperature, the Boltzmann distribution puts almost all
its probability on the global minima.** That is the whole justification of annealing: if at each temperature we let the
chain settle into $\pi_T$, and lower $T$ slowly, we end in a global minimum with probability close to 1.

How slowly is "slowly"? Stuart Geman and Donald Geman (1984) proved convergence for schedules of the form
$T_k = c / \log(1 + k)$ with $c$ large enough, and Bruce Hajek (1988) found the exact condition: such a schedule
converges in probability to the global minima if and only if $c$ is at least the depth of the deepest local minimum
that is not global (the height you must climb to escape it). This is a real theorem, and it is useless in practice: a
logarithmic schedule cools so slowly that it can take longer than listing every state. Practical schedules are
geometric, $T_k = T_0 \alpha^k$ with $\alpha$ slightly below 1, and come with no guarantee. Simulated annealing is a
heuristic justified by a limit theorem, not an algorithm with a proof of speed.

### From scratch on the TSP

A tour is a permutation of the cities. The neighbourhood is **2-opt**: pick positions $i < j$ and reverse the segment
`tour[i..j]`. This removes two edges, $(a, b)$ before the segment and $(c, e)$ after it, and adds $(a, c)$ and $(b, e)$.
So the change in length is computed in constant time:

$$
\Delta = d(a, c) + d(b, e) - d(a, b) - d(c, e).
$$

Reversing a segment never breaks the tour, and every tour can reach every other by 2-opt moves (any permutation is a
product of reversals), so the chain is irreducible. The program also runs plain 2-opt hill climbing (keep applying
improving 2-opt moves until none is left), and, on 12 cities, the exact Held-Karp dynamic programme of the
[Algorithms book, 13.7](../algorithms/13-Dynamic-Programming.md#137-bitmask-dp-travelling-salesman-held-karp) for the
true optimum.

```python
--8<-- "books/ai/ch05_annealing.py"
```

```
Metropolis acceptance probability exp(-delta/T) for a move that is worse by delta:
   T     delta=0.01  delta=0.05  delta=0.20
 1.000      0.9900      0.9512      0.8187
 0.100      0.9048      0.6065      0.1353
 0.030      0.7165      0.1889      0.0013
 0.010      0.3679      0.0067      0.0000
 0.001      0.0000      0.0000      0.0000

12 cities: optimum 3.5597   2-opt hill climbing 3.6112   annealing 3.5597

60 cities, random tour length 33.816
2-opt hill climbing, 20 random starts: best 6.487  mean 6.789  worst 7.133
annealing,  20000 steps: best 7.106   worse moves accepted 1660
annealing, 200000 steps: best 6.450   worse moves accepted 15950

progress of the 200000-step run (step, temperature, current length):
       0    1.0000   33.477
   25000    0.3867   25.336
   50000    0.1495   11.119
   75000    0.0578    8.571
  100000    0.0224    6.551
  125000    0.0086    6.462
  150000    0.0033    6.460
  175000    0.0013    6.450
```

What the output shows:

- **The acceptance table.** At $T = 1$ almost everything is accepted; the walk is nearly random. At $T = 0.03$ a move
  that is worse by 0.05 is still taken about one time in five, but a move worse by 0.2 almost never. At $T = 0.001$ the
  search is a pure descent. The useful range of temperatures is where the typical $\Delta$ of a bad move is comparable
  to $T$; for cities in a unit square, a 2-opt move changes the length by a few hundredths to a few tenths.
- **On 12 cities** annealing finds the exact optimum (3.5597, confirmed by Held-Karp), while one 2-opt hill climb from
  the identity tour stops 1.4 percent above it.
- **On 60 cities** a random tour has length 33.8. Twenty 2-opt hill climbs from random starts end between 6.49 and 7.13:
  each stops in a different local minimum. Annealing with 20 000 steps cools too fast and ends at 7.11, worse than a
  typical hill climb. With 200 000 steps it reaches 6.450, slightly better than the best of the twenty restarts. More time, slower cooling, better answer: that is the usual pattern, with no
  guarantee.

<figure class="mars-fig" markdown="0">
<svg viewBox="0 0 640 290" role="img" aria-label="Plot of the current tour length during simulated annealing on 60 cities: it starts near 33, wanders down noisily while the temperature is high, falls quickly between steps 30000 and 90000, and settles at 6.45. A dashed line marks the best 2-opt hill-climbing result, 6.49.">
<line x1="70" y1="220" x2="610" y2="220" stroke="currentColor" stroke-width="1.2"/>
<line x1="70" y1="220" x2="70" y2="20" stroke="currentColor" stroke-width="1.2"/>
<line x1="65" y1="220.0" x2="70" y2="220.0" stroke="currentColor"/>
<text x="61" y="224.0" font-size="12" text-anchor="end" fill="currentColor">0</text>
<line x1="65" y1="162.9" x2="70" y2="162.9" stroke="currentColor"/>
<text x="61" y="166.9" font-size="12" text-anchor="end" fill="currentColor">10</text>
<line x1="65" y1="105.7" x2="70" y2="105.7" stroke="currentColor"/>
<text x="61" y="109.7" font-size="12" text-anchor="end" fill="currentColor">20</text>
<line x1="65" y1="48.6" x2="70" y2="48.6" stroke="currentColor"/>
<text x="61" y="52.6" font-size="12" text-anchor="end" fill="currentColor">30</text>
<line x1="70.0" y1="220" x2="70.0" y2="225" stroke="currentColor"/>
<text x="70.0" y="240" font-size="12" text-anchor="middle" fill="currentColor">0</text>
<line x1="205.0" y1="220" x2="205.0" y2="225" stroke="currentColor"/>
<text x="205.0" y="240" font-size="12" text-anchor="middle" fill="currentColor">50000</text>
<line x1="340.0" y1="220" x2="340.0" y2="225" stroke="currentColor"/>
<text x="340.0" y="240" font-size="12" text-anchor="middle" fill="currentColor">100000</text>
<line x1="475.0" y1="220" x2="475.0" y2="225" stroke="currentColor"/>
<text x="475.0" y="240" font-size="12" text-anchor="middle" fill="currentColor">150000</text>
<line x1="610.0" y1="220" x2="610.0" y2="225" stroke="currentColor"/>
<text x="610.0" y="240" font-size="12" text-anchor="middle" fill="currentColor">200000</text>
<line x1="70" y1="182.9" x2="610" y2="182.9" stroke="#7ccf9a" stroke-width="2" stroke-dasharray="6 4"/>
<text x="610" y="174.9" font-size="12" text-anchor="end" fill="currentColor">best of 20 hill climbs: 6.487</text>
<polyline points="70.0,28.7 80.8,38.3 91.6,66.9 102.4,71.4 113.2,61.7 124.0,77.5 134.8,83.6 145.6,68.8 156.4,75.0 167.2,99.4 178.0,128.3 188.8,111.2 199.6,141.0 210.4,131.7 221.2,143.3 232.0,153.7 242.8,162.9 253.6,153.8 264.4,166.0 275.2,170.9 286.0,174.6 296.8,174.8 307.6,176.2 318.4,181.8 329.2,182.1 340.0,182.6 350.8,182.1 361.6,182.0 372.4,182.3 383.2,183.1 394.0,182.9 404.8,183.1 415.6,183.1 426.4,183.1 437.2,183.1 448.0,183.1 458.8,183.1 469.6,183.1 480.4,183.1 491.2,183.1 502.0,183.1 512.8,183.1 523.6,183.1 534.4,183.1 545.2,183.1 556.0,183.1 566.8,183.1 577.6,183.1 588.4,183.1 599.2,183.1" fill="none" stroke="#eea66f" stroke-width="2.5"/>
<text x="340.0" y="262" font-size="13" text-anchor="middle" fill="currentColor">step (temperature falls from 1.0 to 0.0005)</text>
<text x="20" y="120.0" font-size="13" text-anchor="middle" fill="currentColor" transform="rotate(-90 20 120.0)">tour length</text>
</svg>
<figcaption>Figure 5.3. The current tour length during the 200 000-step annealing run on 60 cities, sampled every 4000 steps. While the temperature is high the tour gets worse as often as better; the length falls fast in the middle range of temperatures and freezes at 6.450, a little below the best of 20 hill climbs.</figcaption>
</figure>

The progress log (Figure 5.3) shows the three phases every annealing run has: a hot phase where the length barely
improves because almost every move is accepted, a middle phase where the length falls fast (the useful temperatures),
and a cold phase where the tour is frozen and only tiny improvements remain.

**Choosing the parameters.** A common recipe: set $T_0$ so that early on most worse moves (say 80 percent) are
accepted; set the final temperature so that almost none are; choose the number of steps by the time you have; and
always keep the best state seen, since the current state at the end may be slightly worse than an earlier one.

<figure class="play" data-play="anneal"><span class="ai-tag">AI-created</span><figcaption><b>Watch it.</b> Simulated annealing against plain hill climbing on a tour of 25 made-up sites: heat lets it accept worse tours early on and escape traps.</figcaption></figure>

## 5.4 Local beam search; genetic algorithms

*Level: intermediate.*

Hill climbing and annealing keep one state. What if we keep $k$?

### Local beam search

**Local beam search** starts with $k$ random states. At each step it generates all successors of all $k$ states and
keeps the best $k$ of the whole pool. If any is a goal, it stops.

This is not the same as $k$ independent hill climbs. In independent climbs, each run ignores the others. In beam
search, the states share information: if one state has many good successors and the others have none, the next beam is
all children of the good one. Effort flows to where progress is being made. The danger is the same as its strength: the
$k$ states can quickly crowd into one small region, and the beam becomes an expensive single hill climb.

**Stochastic beam search** fixes this by choosing the $k$ successors at random, with probability increasing with their
value, instead of always the best $k$. The program weights a successor of fitness $f$ by $2^f$. Diversity survives,
because weaker successors are sometimes kept.

### Genetic algorithms

A **genetic algorithm** (GA) is a stochastic beam search in which successors are made by combining two parents rather
than changing one. The words come from biology:

- the **population** is the current set of states, usually written as strings (here the 8 digits of the rows, 1 to 8);
- the **fitness function** is the objective, higher is better (here the number of non-attacking pairs, 28 for a
  solution);
- **selection** picks parents, fitter ones more often;
- **crossover** makes a child by taking a prefix of one parent and the rest from the other, at a random **crossover
  point**;
- **mutation** changes a random position of the child with some small probability;
- **elitism** copies the best few states unchanged into the next generation, so the best fitness never goes down.

Crossover is the new idea. It can join a good left half and a good right half that were found separately. Here is one
crossover, traced by hand. The parents are 15863722 and 63184257; cut after position 3:

| | columns 1-3 | columns 4-8 | fitness |
|---|---|---|---|
| parent x | 1 5 8 | 6 3 7 2 2 | 26 |
| parent y | 6 3 1 | 8 4 2 5 7 | 25 |
| child | 1 5 8 | 8 4 2 5 7 | 24 |

The child is worse than both parents here. That is typical: crossover of two unrelated states is close to a random
jump. Crossover helps when the population has already converged somewhat, so that parents share structure and the
pieces being swapped are each good in context. Cutting after position 7 instead gives the child 15863727 with fitness
27, better than both parents (Exercise 6).

Two selection rules are common. **Fitness-proportional** ("roulette wheel") selection picks a parent with probability
proportional to its fitness. **Tournament selection** picks a few states at random (three here) and takes the best.
The difference matters: on 8-queens, fitness values are 20 to 28, so roulette gives a state of fitness 28 barely more
chance than one of fitness 22. The **selection pressure**, how strongly fitness drives reproduction, is weak. Tournament
selection depends only on the ranking, not on the size of the numbers, and the pressure is stronger.

```python
--8<-- "books/ai/ch05_genetic.py"
```

```
parents 15863722 26 and 63184257 25
child (cut after 3) 15884257 24

local beam search on 8-queens, 50 runs each
  k= 1 plain       solved  11/50   mean steps when solved   4.5
  k= 5 plain       solved  27/50   mean steps when solved   3.4
  k=20 plain       solved  31/50   mean steps when solved   2.8
  k=10 stochastic  solved  45/50   mean steps when solved  16.5

genetic algorithm, roulette   selection, 20 runs: solved 12/20 within 300 generations; median  51, fastest   8, slowest 242
genetic algorithm, tournament selection, 20 runs: solved 20/20 within 300 generations; median  19, fastest   1, slowest  45

one tournament run (seed 3): solution 73168524 at generation 23
 gen  best  mean
   0    25   20.0
   3    27   22.2
   6    27   22.7
   9    27   23.0
  12    27   23.2
  15    27   24.1
  18    27   24.5
  21    27   24.6
  23    28   24.8
```

What it shows:

- A beam of size 1 is plain hill climbing: about one success in five here. Plain beams of 5 and 20 help, but they also
  get stuck (all $k$ states on the same plateau). The stochastic beam, which keeps weaker states too, succeeds in 45 of
  50 runs, in more steps.
- The GA solves most runs. With tournament selection it is faster and more reliable than with roulette selection, as the
  selection-pressure argument predicts.
- In the traced run the best fitness reaches 27 (one attacking pair) after a few generations and then waits for the
  last improvement, while the mean fitness climbs as the population converges. This "long wait for the last bit" is
  common in GAs.

For 8-queens a GA is a sledgehammer: random-restart hill climbing with sideways moves solves it in about 23 moves.
Genetic algorithms earn their keep where a good representation lets crossover combine partial solutions that really are
independent, and where the objective is a black box: you can evaluate it but know nothing else about it.

### What theory says, honestly

John Holland's *Adaptation in Natural and Artificial Systems* (1975) set out genetic algorithms and their first
analysis, the **schema theorem**. A **schema** is a pattern such as `1 5 * * * * * 7`, with fixed positions and wildcards.
The theorem says, roughly, that in one generation the expected number of strings matching a schema grows in proportion
to how much fitter than average the schema's strings are, minus losses from crossover cutting the schema apart (likely
when its fixed positions are far apart) and from mutation. So short, fit patterns spread. It is a statement about
expected counts over one generation; it does not prove that a GA finds the optimum or how fast. The convergence
theory of evolutionary algorithms is much more recent and still incomplete.

GAs and their relatives (**evolution strategies** for real-valued vectors, **genetic programming** for evolving
programs) have real successes. A well-documented one: a team at NASA Ames evolved the shape of an X-band antenna for the
three small satellites of the Space Technology 5 mission, launched in 2006 (Hornby, Globus, Linden and Lohn, 2006).

## 5.5 Continuous spaces: gradient methods

Many problems have states that are vectors of real numbers. Then "neighbours" are infinitely many, and we need a
different way to decide where to step.

**The example.** Twelve rover sites lie on a 10 km by 10 km map. We want to place $k = 3$ relay stations
$x_1, x_2, x_3$ (points in the plane) to keep the sites close to a station. Our cost is

$$
C(x_1, \dots, x_k) = \sum_{i=1}^{12} \min_j \lVert s_i - x_j \rVert^2,
$$

the sum over sites $s_i$ of the squared distance to the nearest station. The state is six real numbers.

### The gradient

If you are standing on a smooth hillside, the direction of steepest ascent is the **gradient**: the vector of partial
derivatives $\nabla C = (\partial C / \partial z_1, \dots, \partial C / \partial z_6)$, where the $z$'s are the six
coordinates. Moving a small step against the gradient decreases $C$ fastest. **Gradient descent** repeats

$$
x \leftarrow x - \alpha \nabla C(x),
$$

where $\alpha > 0$ is the **step size** (in machine learning, the **learning rate**).

For our cost, fix for a moment which station is nearest to each site. Let $S_j$ be the set of sites whose nearest
station is $x_j$, with $n_j$ sites and mean $m_j$. Then $C = \sum_j \sum_{i \in S_j} \lVert s_i - x_j\rVert^2$, and
differentiating with respect to $x_j$,

$$
\nabla_{x_j} C = \sum_{i \in S_j} 2 (x_j - s_i) = 2 n_j (x_j - m_j).
$$

Each station is pulled towards the mean of its sites. Where the assignment changes (a site equally close to two
stations) $C$ has a crease and no derivative, but those points are rare and gradient descent steps past them.

When you cannot differentiate by hand, you can estimate the gradient: change one coordinate by a tiny $\pm h$ and
measure, $\partial C / \partial z \approx (C(z + h) - C(z - h)) / 2h$. This **empirical gradient** costs two
evaluations of $C$ per coordinate. The program checks the analytic gradient against it; they agree to four decimals.

### Step size: a proof of when gradient descent converges

With the assignment fixed, one step for station $j$ is

$$
x_j \leftarrow x_j - 2\alpha n_j (x_j - m_j), \quad\text{so}\quad x_j - m_j \leftarrow (1 - 2\alpha n_j)(x_j - m_j).
$$

The distance to the target is multiplied by $1 - 2\alpha n_j$ every step. If $0 < \alpha < 1/n_j$ this factor has
absolute value below 1, and the station converges to $m_j$ geometrically; if $\alpha > 1/n_j$ it overshoots by more
than it gains and diverges. If $\alpha = 1/(2 n_j)$, the factor is 0 and the station jumps to $m_j$ in one step. So the
right step size depends on the curvature ($2 n_j$ here), and too small is slow while too large is unstable. These are
exactly the issues of [Machine learning, Chapter 5](../machine-learning/05-Optimization.md), which proves the general
rate for smooth convex functions
([5.2](../machine-learning/05-Optimization.md#52-how-fast-gradient-descent-converges)).

### Newton's method

The jump with $\alpha = 1/(2 n_j)$ is no accident. **Newton's method** approximates the function near $x$ by a
quadratic (using the second derivative, or in many dimensions the **Hessian** matrix $H$ of second derivatives) and
jumps to the minimum of that quadratic:

$$
x \leftarrow x - H^{-1} \nabla C(x).
$$

For one station's cost $n_j \lVert x_j - m_j\rVert^2$ the Hessian is $2 n_j I$, and the Newton step is exactly "move to
the mean of your sites". Alternating "assign each site to its nearest station" with "move each station to the mean of
its sites" is the **k-means algorithm** (Lloyd's algorithm) of [Machine learning, Chapter 13](../machine-learning/13-Clustering.md).
In one dimension, Newton's method for minimising $f$ solves $f'(x) = 0$ by $x \leftarrow x - f'(x)/f''(x)$. Near a
minimum with $f'' > 0$ it converges **quadratically**: the number of correct digits roughly doubles each step, which you
can see in the last two lines of the output. The price is computing and inverting the Hessian, $O(d^3)$ in $d$
dimensions, which is why large machine-learning models use first-order methods.

```python
--8<-- "books/ai/ch05_continuous.py"
```

```
start cost 175.36
analytic gradient : [[0.0, 0.0], [-24.8294, 40.0758], [15.8186, -15.3039]]
empirical gradient: [[0.0, 0.0], [-24.8294, 40.0758], [15.8186, -15.3039]]

gradient descent, alpha = 0.05
  step   0: cost  175.360
  step   1: cost   89.306
  step   2: cost   79.663
  step   5: cost   75.811
  step  10: cost   75.629
  step  50: cost   75.628
  step 200: cost   75.628
  stations end at [[1.0, 9.0], [3.55, 5.5], [7.02, 2.91]]

step size matters (cost after 5 and 50 steps from the same start):
  alpha 0.005:  125.928   76.155
  alpha 0.020:   82.391   75.628
  alpha 0.050:   75.811   75.628
  Newton steps (jump to the mean of the nearest sites): [175.36, 75.628, 75.628, 75.628, 75.628]

random restarts: 10 random starts, 200 steps each
  final costs: [19.14, 19.14, 22.54, 22.54, 22.54, 22.54, 54.19, 60.85, 60.85, 60.85]

Newton's method on f(x) = x^4 - 3x^2 + x, from x = -2 and from x = 2
  -2.000000  -1.547619  -1.347929  -1.303083  -1.300845  -1.300840   f = -3.5139
  2.000000  1.500000  1.238095  1.144277  1.131153  1.130901   f = -1.0702
```

Everything from 5.2 reappears in continuous form:

- From the chosen start, the first station, at (1, 9), is nearest to no site. Its gradient is exactly zero, so it never
  moves: a **dead station**, stuck forever on a perfectly flat region of the landscape. The other two share all twelve
  sites, and descent converges to cost 75.63, a local minimum.
- With step size 0.05, descent is close to the minimum in 5 steps; with 0.005 it is still far after 5 steps and not
  quite there after 50. Newton's jump gets there in one step.
- **Random restarts** again: ten random starts end at four different local minima, from 19.14 (one station per group of
  sites, the best found) to 60.85. Two of the ten find the best.
- Newton's method on $f(x) = x^4 - 3x^2 + x$ finds the global minimum $x \approx -1.3008$ from $x = -2$ and a merely local
  minimum $x \approx 1.1309$ from $x = 2$. Newton's method is a fast local method, not a global one.

### Convexity, constraints, and the rest of optimisation

A function is **convex** if the straight line between any two points of its graph lies on or above the graph. For a
convex function every local minimum is a global minimum, so local search is all you need; the proof and the conditions
are in [Machine learning, 5.1](../machine-learning/05-Optimization.md#51-loss-landscapes-and-convexity). Our relay
cost is not convex (it has several local minima), and neither are the losses of neural networks.

Many problems also have **constraints**: stations must lie inside the map, budgets must not be exceeded. If the
objective and the constraints are linear, the problem is a **linear program**, solved exactly by the simplex method or
interior-point methods ([Algorithms book, 23.5](../algorithms/23-Approximation-and-Parameterized-Algorithms.md#235-linear-programming-and-lp-relaxation-with-rounding)).
For convex objectives with convex constraints there are efficient general methods (**convex optimisation**). For
everything else, the tools of this chapter, gradient steps plus restarts, plus annealing-like noise, are what people
actually use.

**In practice.** `scipy.optimize` provides `minimize` (gradient, quasi-Newton and Newton methods) and `dual_annealing`;
PyTorch and JAX compute gradients automatically and provide SGD and Adam; OR-Tools and many TSP codes use local search
with 2-opt and Lin-Kernighan moves; DEAP is a Python library for evolutionary algorithms.

## 5.6 Search with nondeterministic actions and partial observation: AND-OR search, belief states

*Level: advanced.*

Every search so far assumed two things about the world: an action has exactly one outcome, and the agent knows the
state it is in. Real agents have neither luxury. A Mars rover told to drive one metre forward on loose sand may slip
and travel less; the two Mars Exploration Rovers used visual odometry, tracking features between stereo images, to
measure how far they had really moved on slopes, because wheel counts alone were not trustworthy there (Maimone, Cheng
and Matthies, 2007). And with radio signals taking between 3 and 22 minutes each way, the rover cannot wait for Earth
to tell it where it ended up.

### Nondeterministic actions: the erratic vacuum world

The **vacuum world** of [Chapter 2](02-Intelligent-Agents.md) has two squares, L and R, each clean or dirty, and a robot
in one of them. Write a state as `L:Dc`: the robot is on L, L is dirty (D), R is clean (c). There are 8 states. The
actions are Left, Right and Suck. In the **erratic** vacuum world, Suck misbehaves:

- on a dirty square it cleans that square, and **sometimes** cleans the other square too;
- on a clean square it **sometimes** deposits dirt on it.

So an action now has a **set** of possible results. The transition model is a function $\text{Results}(s, a)$ that
returns a set. A solution can no longer be a fixed sequence of actions; it must say what to do in each case. Such a
solution is a **conditional plan** (or **contingency plan**), a small program with if-then branches:

```
Suck; if state is L:cD then [Right; Suck]
```

### AND-OR search trees

The search tree has two kinds of nodes.

- **OR nodes** are states, where the agent chooses an action. A solution needs **one** action that works.
- **AND nodes** are the outcome sets of an action, where the world chooses. A solution needs a sub-plan for **every**
  outcome.

A **solution** to an AND-OR search problem is a subtree that (1) has a goal state at every leaf, (2) picks one action
at each OR node, and (3) includes every outcome at each AND node. The algorithm is a pair of mutually recursive
depth-first functions:

```python
def or_search(state, path):
    if is_goal(state):
        return []                                  # the empty plan
    if state in path:
        return None                                # a loop on this branch: fail
    for action in actions(state):
        plan = and_search(results(state, action), path + [state])
        if plan is not None:
            return [action, plan]
    return None

def and_search(states, path):
    plans = {}
    for s in states:
        plan = or_search(s, path)
        if plan is None:
            return None                            # one bad outcome sinks the action
        plans[s] = plan
    return plans                                   # "if state is s then plans[s]"
```

**Claim (soundness).** If `or_search(s, [])` returns a plan, executing the plan from $s$ reaches a goal whatever outcomes
the world chooses.

*Proof*, by induction on the depth of the returned plan. The empty plan is returned only at a goal. Otherwise the plan
is `[a, plans]`, where `plans` has an entry for every $s' \in \text{Results}(s, a)$ (that is what `and_search` checks), and
each entry is a plan returned by `or_search(s', ...)`, of smaller depth, which by induction reaches a goal from $s'$.
Whatever outcome $s'$ occurs after $a$, the agent follows `plans[s']` and reaches a goal. $\square$

**Claim (termination and completeness).** On a finite state space, the search always stops; and if some acyclic
conditional plan exists, it finds one.

*Proof sketch.* The `path` argument holds the states on the current branch, and a state already on the branch is
rejected, so no branch is longer than the number of states: the recursion is finite. For completeness: if an acyclic
plan exists from $s$, then some action $a$ has an acyclic plan from every outcome, none of which needs to revisit $s$
or anything on the path (a plan that revisits a state on its own branch could be shortened by starting from the later
visit). The loop over actions tries $a$, and by induction on the number of states not yet on the path every recursive
call succeeds. $\square$

The search is depth first, so its memory is linear in the depth, and its time can be exponential, as for any tree
search ([Chapter 3](03-Uninformed-Search.md)). Breadth-first and heuristic versions exist; the best-known heuristic
one is AO*, developed in the 1970s; Nilsson's 1971 book describes AND-OR graphs for problem reduction.

<figure class="mars-fig" markdown="0">
<svg viewBox="0 0 640 300" role="img" aria-label="AND-OR tree of the plan for the erratic vacuum world. From state L:DD the action Suck leads to an AND node with two outcomes, L:cc which is a goal, and L:cD. From L:cD the action Right leads to R:cD, and Suck leads to R:cc, a goal.">
<rect x="280" y="16" width="80" height="28" rx="5" fill="#9cc9ea" fill-opacity="0.5" stroke="currentColor" stroke-width="1.2"/>
<text x="320" y="35" font-size="13" text-anchor="middle" fill="currentColor" font-family="monospace">L:DD</text>
<line x1="320" y1="44" x2="320" y2="90" stroke="currentColor" stroke-width="1.3"/>
<text x="330" y="72" font-size="13" text-anchor="start" fill="#eea66f" font-weight="bold">Suck</text>
<circle cx="320" cy="96" r="6" fill="none" stroke="currentColor" stroke-width="1.3"/>
<line x1="315" y1="101" x2="200" y2="146" stroke="currentColor" stroke-width="1.3"/>
<line x1="325" y1="101" x2="440" y2="146" stroke="currentColor" stroke-width="1.3"/>
<path d="M 290 113 Q 320 128 350 113" fill="none" stroke="currentColor" stroke-width="1.3"/>
<text x="470" y="100" font-size="12" fill="currentColor">AND node: every</text>
<text x="470" y="116" font-size="12" fill="currentColor">outcome needs a plan</text>
<rect x="160" y="146" width="80" height="28" rx="5" fill="#7ccf9a" fill-opacity="0.5" stroke="currentColor" stroke-width="1.2"/>
<text x="200" y="165" font-size="13" text-anchor="middle" fill="currentColor" font-family="monospace">L:cc</text>
<text x="200" y="195" font-size="12" text-anchor="middle" fill="currentColor">goal: stop</text>
<rect x="400" y="146" width="80" height="28" rx="5" fill="#9cc9ea" fill-opacity="0.5" stroke="currentColor" stroke-width="1.2"/>
<text x="440" y="165" font-size="13" text-anchor="middle" fill="currentColor" font-family="monospace">L:cD</text>
<line x1="440" y1="174" x2="440" y2="214" stroke="currentColor" stroke-width="1.3"/>
<text x="450" y="200" font-size="13" text-anchor="start" fill="#eea66f" font-weight="bold">Right</text>
<rect x="400" y="214" width="80" height="28" rx="5" fill="#9cc9ea" fill-opacity="0.5" stroke="currentColor" stroke-width="1.2"/>
<text x="440" y="233" font-size="13" text-anchor="middle" fill="currentColor" font-family="monospace">R:cD</text>
<line x1="480" y1="228" x2="540" y2="228" stroke="currentColor" stroke-width="1.3"/>
<text x="490" y="220" font-size="13" text-anchor="start" fill="#eea66f" font-weight="bold">Suck</text>
<rect x="540" y="214" width="80" height="28" rx="5" fill="#7ccf9a" fill-opacity="0.5" stroke="currentColor" stroke-width="1.2"/>
<text x="580" y="233" font-size="13" text-anchor="middle" fill="currentColor" font-family="monospace">R:cc</text>
<text x="580" y="264" font-size="12" text-anchor="middle" fill="currentColor">goal: stop</text>
<text x="40" y="250" font-size="12" fill="currentColor">boxes: OR nodes (we choose an action)</text>
<text x="40" y="270" font-size="12" fill="currentColor">circle with arc: AND node (nature chooses)</text>
</svg>
<figcaption>Figure 5.4. The conditional plan found by AND-OR search in the erratic vacuum world, drawn as a tree. At the box nodes the agent chooses an action; at the AND node the world chooses the outcome, so the plan must cover both. Read as a program: Suck; if the state is L:cD then Right, Suck.</figcaption>
</figure>

### Cyclic plans

Suppose instead that movement is **slippery**: Right sometimes leaves the robot where it was. Then from `L:cD` there
is no acyclic plan, since the world can keep refusing to move the robot. But "keep trying Right until you are on R" works,
provided each attempt has some chance of success. Such a **cyclic plan** contains a loop (`while state is L:cD do
Right`). AND-OR search finds cyclic plans if, instead of failing when a state repeats on the path, it labels the state
and lets the plan jump back to it; the plan is accepted if every leaf is a goal and a goal is reachable from every
point of the plan. Whether a cyclic plan is a solution depends on what we assume about the world: it terminates with
probability 1 only if each attempt has a fixed positive chance, not if the world is an adversary that can make the
robot slip forever.

### Sensorless search: belief states

Now take the ordinary, deterministic vacuum world but give the robot no sensors at all. It does not know where it is
or which squares are dirty. Can it still guarantee a clean house?

The trick is to search in the space of **belief states**: sets of physical states the agent might be in. Initially
the belief state is all 8 states. An action $a$ maps a belief state $b$ to

$$
b' = \bigcup_{s \in b} \text{Results}(s, a),
$$

the set of everywhere the agent could now be (for deterministic actions, $\{\text{Result}(s, a) : s \in b\}$). A belief
state is a goal if **every** state in it is a goal. With these definitions, a sensorless problem is an ordinary,
deterministic, fully observed search problem over belief states, and any algorithm from Chapters 3 and 4 solves it.
With $N$ physical states there are $2^N - 1$ non-empty belief states, which sounds terrible, but usually only a tiny
fraction is reachable.

One fact makes pruning possible. **If a plan works for a belief state $b$, it works for every subset of $b$**, because
it works for each state of $b$ individually. So if we have already found that belief state $b$ is solvable, any
generated subset is too; and if a superset was already put on the frontier, a subset can be preferred.

### Partial observation: predict and update

Between no sensors and full observation lies the common case: the agent senses some things. With a **local** sensor,
the vacuum robot perceives its own square and whether that square is dirty. Then each step of the agent has three
parts, which [Chapter 13](13-Reasoning-over-Time.md) develops into filtering:

1. **Predict:** after action $a$, the belief state becomes $\hat b = \bigcup_{s \in b} \text{Results}(s, a)$.
2. **Possible percepts:** the percepts the agent might receive are those of the states in $\hat b$.
3. **Update:** after receiving percept $o$, keep only the states consistent with it: $b_o = \{s \in \hat b : \text{Percept}(s) = o\}$.

For planning, the possible percepts are like the outcomes of a nondeterministic action: each needs its own sub-plan. So
**planning under partial observation is AND-OR search over belief states**, with the agent choosing actions and the
percept playing the role of the world's choice.

```python
--8<-- "books/ai/ch05_and_or.py"
```

```
erratic vacuum world, conditional plan from L:DD (7 OR-nodes expanded):
  Suck
  if state is L:cc:
    (goal)
  if state is L:cD:
    Right
    Suck
    (goal)
executed, lucky nature  : ['Suck->L:cc']
executed, unlucky nature: ['Suck->L:cD', 'Right->R:cD', 'Suck->R:cc']
plans found and verified for 8 of 8 start states

sensorless plan from total ignorance: ['Left', 'Suck', 'Right', 'Suck'] (12 belief states generated)
  after Left : ['L:DD', 'L:Dc', 'L:cD', 'L:cc']
  after Suck : ['L:cD', 'L:cc']
  after Right: ['R:cD', 'R:cc']
  after Suck : ['R:cc']
  belief states reachable from total ignorance: 12 of 255 non-empty sets

local sensing, ordinary world
  start percept ('L', True): belief ['L:DD', 'L:Dc']
  Suck  percept ('L', False): belief ['L:cD', 'L:cc']
  Right percept ('R', False): belief ['R:cc']
```

Read the output:

- AND-OR search returns the plan of Figure 5.4 from `L:DD`. If the erratic Suck happens to clean both squares, the robot
  is done after one action; otherwise it moves Right and sucks. The program verifies, by following every branch, that
  the plan found from each of the 8 start states reaches the goal under every outcome.
- The sensorless robot, knowing nothing, still has a plan that is guaranteed to work: Left, Suck, Right, Suck. After
  Left it knows it is on L; after Suck it knows L is clean; and so on. Only 12 of the 255 possible belief states can be
  reached at all, and breadth-first search over belief states finds a shortest plan (Exercise 10 checks that none of
  length 3 exists).
- With the local sensor, the belief state shrinks with each percept. After Suck the percept says "L clean", which the
  robot already knew; the move Right and the percept "R clean" then pin down the state exactly.

Belief states are the link between search and probability. Replace "the set of states I might be in" by "a probability
for each state" and you get the belief states of hidden Markov models and partially observable Markov decision
processes ([Chapter 14](14-Making-Decisions.md), 14.6).

### A short history thread

Hill climbing is older than computers; it is the natural method of anyone tuning a dial. Its use on hard combinatorial
problems took off with the 2-opt move for the TSP (Croes, 1958) and the variable-depth moves of Shen Lin and Brian
Kernighan (1973), still at the core of the best TSP heuristics. The Metropolis rule (1953) came from statistical
physics, and Kirkpatrick, Gelatt and Vecchi made it an optimiser in 1983. Holland's book on genetic algorithms
appeared in 1975, and David Goldberg's 1989 textbook spread them widely. Local search for satisfiability (GSAT, Selman,
Levesque and Mitchell, 1992) and min-conflicts for constraints (Minton and colleagues, 1992) showed in the early 1990s
that very simple local search could beat systematic search on large random and real instances; both return in
Chapters 7 and 8. AND-OR graphs were studied in the 1960s and 1970s for problem reduction and game playing (Nilsson,
1971), and searching in belief space was developed for planning with incomplete information in the 1990s and 2000s (for example
Genesereth and Nourbakhsh, 1993; Bonet and Geffner, 2000).

## Check yourself

??? question "1. In the complete-state formulation of 8-queens (one queen per column), how many states are there, how many neighbours does each state have, and what are the smallest and largest possible values of h?"

    Each of the 8 columns holds its queen in one of 8 rows: $8^8 = 16\,777\,216$ states. A neighbour moves one queen to
    one of the 7 other rows of its column: $8 \cdot 7 = 56$ neighbours. $h$ ranges from 0 (a solution; there are 92) to
    $\binom{8}{2} = 28$ (all queens in one row, where every pair attacks).

??? question "2. Prove that steepest-ascent hill climbing with at most 100 consecutive sideways moves stops on n-queens. Why is the cap needed?"

    Between two strict improvements there are at most 100 sideways moves (the counter resets only on an improvement),
    and there are at most $\binom{n}{2}$ strict improvements because $h$ is a whole number that starts at most at
    $\binom{n}{2}$ and stays at least 0. So the run has at most $101\binom{n}{2}$ moves. Without the cap, a climber on a
    flat local minimum could move sideways forever (for example back and forth between two equal states), so the
    argument, and the algorithm, would fail.

??? question "3. Each hill-climbing run solves 8-queens with probability p = 0.14. How many independent runs do you need so that the chance that all fail is below 1 percent? What is the expected number of runs?"

    All $k$ runs fail with probability $0.86^k$. We need $0.86^k < 0.01$, that is $k > \ln 0.01 / \ln 0.86 = (-4.605)/(-0.1508) \approx 30.5$, so 31 runs. The expected number of runs is $1/p = 1/0.14 \approx 7.1$. The gap
    between 7 (average) and 31 (99 percent sure) is typical of geometric distributions: the average is small, the tail
    is long.

??? question "4. In simulated annealing, at T = 0.03, what is the probability of accepting a move that is worse by 0.05? At what temperature is a move that is worse by 0.1 accepted with probability one half?"

    $e^{-0.05/0.03} = e^{-1.667} \approx 0.189$, as in the program's table. For the second, solve $e^{-0.1/T} = 1/2$:
    $0.1/T = \ln 2$, so $T = 0.1/\ln 2 \approx 0.144$.

??? question "5. Write code: run the Metropolis rule at fixed temperature T = 1 on three states with energies 0, 1, 2 arranged in a ring (each proposes one of the other two with probability 1/2), and compare the fraction of time in each state with the Boltzmann distribution."

    ```python
    import math, random

    E = [0.0, 1.0, 2.0]
    T = 1.0
    rng = random.Random(0)
    s, counts = 0, [0, 0, 0]
    for _ in range(300000):
        t = (s + rng.choice((-1, 1))) % 3          # symmetric proposal: a neighbour on a ring
        if E[t] <= E[s] or rng.random() < math.exp(-(E[t] - E[s]) / T):
            s = t
        counts[s] += 1
    Z = sum(math.exp(-e / T) for e in E)
    print([round(c / 300000, 3) for c in counts], [round(math.exp(-e / T) / Z, 3) for e in E])
    ```

    It prints `[0.668, 0.243, 0.089] [0.665, 0.245, 0.09]`. The time fractions match $e^{-E/T}/Z$ to within sampling
    noise, as the detailed-balance theorem of 5.3 predicts. With $T = 0.2$ the chain would spend over 99 percent of its
    time in the minimum.

??? question "6. Cross the parents 15863722 (fitness 26) and 63184257 (fitness 25) at every cut point 1 to 7, taking the prefix from the first parent. Which child is best?"

    The children and fitness values (non-attacking pairs) are: cut 1: 13184257, 24; cut 2: 15184257, 23; cut 3:
    15884257, 24; cut 4: 15864257, 26; cut 5: 15863257, 25; cut 6: 15863757, 25; cut 7: 15863727, 27. The best is the
    cut after position 7, which keeps almost all of the fitter parent and replaces its last queen (row 2, which clashed
    with the queen in column 7 on row 2) by the other parent's last queen (row 7). Only one cut beats both parents:
    crossover is a gamble.

??? question "7. In the relay-station example, a station has n_j = 4 sites. For which step sizes does gradient descent (with the assignment fixed) converge to the mean of its sites? Which step size reaches it in one step?"

    The error is multiplied by $1 - 2\alpha n_j = 1 - 8\alpha$ each step. Convergence needs $|1 - 8\alpha| < 1$, so
    $0 < \alpha < 0.25$. At $\alpha = 1/8 = 0.125$ the factor is 0 and the station reaches the mean in one step (the
    Newton step). For $\alpha$ between 0.125 and 0.25 the error changes sign each step but still shrinks; above 0.25 it
    grows.

??? question "8. Write code: first-choice hill climbing for 8-queens (try random neighbours, take the first strictly better one; give up after 1000 failed tries). What fraction of runs succeed?"

    ```python
    import random

    def conflicts(q):
        n = len(q)
        return sum(1 for a in range(n) for b in range(a + 1, n)
                   if q[a] == q[b] or abs(q[a] - q[b]) == b - a)

    def first_choice(n, rng, max_tries=1000):
        """Try random neighbours; take the first one that is strictly better."""
        q = [rng.randrange(n) for _ in range(n)]
        h = conflicts(q)
        while h > 0:
            for _ in range(max_tries):
                c, r = rng.randrange(n), rng.randrange(n)
                if r == q[c]:
                    continue
                old = q[c]
                q[c] = r
                h2 = conflicts(q)
                if h2 < h:
                    h = h2
                    break
                q[c] = old
            else:
                return False               # no better neighbour found: assume a local minimum
        return True

    rng = random.Random(1)
    print(sum(first_choice(8, rng) for _ in range(1000)) / 1000)
    ```

    It prints 0.119: about 12 percent, a little below steepest ascent's 14 percent. That is expected, since it takes any
    improving move rather than the best one, and it has the same traps. Its advantage is speed per step when there are
    very many neighbours, since it usually evaluates only a few.

??? question "9. In the slippery vacuum world, Right sometimes leaves the robot where it was. Why does the AND-OR search of 5.6 find no plan from L:cD? What plan does work, and under what assumption?"

    From `L:cD`, Right has outcomes {`R:cD`, `L:cD`}. The second outcome is the state itself, which is on the path, so
    `or_search` returns failure for it, and the AND node fails. Left and Suck do not help either: Left leaves the robot on L, and Suck on the
    clean L does nothing in this world. The working plan is cyclic: `while state is L:cD
    do Right; Suck`. It reaches the goal with probability 1 if every attempt to move has some fixed positive chance of
    success, independently of earlier attempts; it is not guaranteed if the world can choose the outcome adversarially
    forever.

??? question "10. Show that the sensorless vacuum world has no plan of length 3, and find all plans of length 4."

    A short program checks all $3^k$ action sequences against all 8 start states:

    ```python
    from itertools import product
    STATES = [(l, a, b) for l in "LR" for a in (True, False) for b in (True, False)]
    def res(s, act):
        l, a, b = s
        if act == "Left": return ("L", a, b)
        if act == "Right": return ("R", a, b)
        return ("L", False, b) if l == "L" else ("R", a, False)
    def works(plan):
        for s in STATES:
            for act in plan:
                s = res(s, act)
            if s[1] or s[2]:
                return False
        return True
    for k in (1, 2, 3, 4):
        print(k, [p for p in product(["Left", "Right", "Suck"], repeat=k) if works(p)])
    ```

    Lengths 1 to 3 have no plan; length 4 has exactly two: Left, Suck, Right, Suck and Right, Suck, Left, Suck. The
    reason: each square must be sucked at a moment when the robot is certainly on it. Before the first move the robot's
    square is unknown, so a Suck then is not guaranteed to clean either particular square. So the plan needs a move, a
    Suck, a move to the other square and a Suck: at least four actions.

??? question "11. Prove that if a sensorless plan reaches the goal from belief state b, it reaches the goal from every non-empty subset of b. How can a search use this?"

    A sensorless plan is a fixed sequence of actions. It solves $b$ exactly when, for every $s \in b$, executing it from
    $s$ ends in a goal (for every outcome, if actions are nondeterministic). Every state of a subset $b' \subseteq b$ is
    a state of $b$, so the same condition holds for $b'$. Uses: once $b$ is known to be solvable, every subset is
    solvable with the same plan; and when a search generates a belief state that is a superset of one already on the
    frontier, it can be discarded, since the subset is at least as easy.

??? question "12. Write code: simulated annealing for 8-queens with energy h, random single-queen moves, T0 = 2 and geometric cooling by 0.999 per step, at most 20 000 steps. How often does it solve the problem?"

    ```python
    import math, random

    def conflicts(q):
        n = len(q)
        return sum(1 for a in range(n) for b in range(a + 1, n)
                   if q[a] == q[b] or abs(q[a] - q[b]) == b - a)

    def anneal_queens(n, rng, t0=2.0, alpha=0.999, steps=20000):
        q = [rng.randrange(n) for _ in range(n)]
        h, t = conflicts(q), t0
        for step in range(steps):
            if h == 0:
                return step
            c, r = rng.randrange(n), rng.randrange(n)
            old = q[c]
            q[c] = r
            h2 = conflicts(q)
            if h2 <= h or rng.random() < math.exp(-(h2 - h) / t):
                h = h2
            else:
                q[c] = old
            t *= alpha
        return None

    rng = random.Random(3)
    results = [anneal_queens(8, rng) for _ in range(100)]
    solved = [s for s in results if s is not None]
    print(len(solved), "of 100 solved; median steps", sorted(solved)[len(solved) // 2])
    ```

    It prints `100 of 100 solved; median steps 1722`. Every run succeeds without restarts, but each takes many more
    (cheap) steps than a hill climb, since most of the early steps are spent wandering while the temperature is high.

## What you learned

- When only the final state matters, local search keeps one complete state (or a few) and improves it by small
  changes, in constant memory, over spaces far too large to search systematically.
- Hill climbing stops because each move strictly improves a bounded objective; it gets stuck on local optima, plateaus
  and ridges. Sideways moves and random restarts fix most of this, and restarts cost $s + \frac{1-p}{p} f$ steps on
  average.
- Simulated annealing accepts a worse move with probability $e^{-\Delta/T}$. At fixed $T$ it samples the Boltzmann
  distribution (detailed balance), which concentrates on global optima as $T \to 0$; a logarithmic schedule provably
  converges but is impractically slow, so real schedules are geometric heuristics.
- Local beam search shares effort among $k$ states; genetic algorithms add crossover, and their behaviour depends on
  selection pressure and representation. The schema theorem describes one generation, not convergence.
- In continuous spaces, the gradient gives the direction; the step size must match the curvature; Newton's method uses
  the curvature directly; local minima and dead regions remain, and restarts still help.
- With nondeterministic actions a solution is a conditional plan, found by AND-OR search; with partial observation the
  agent searches over belief states, predicting with actions and updating with percepts.

**Next:** [Chapter 6](06-Games-and-Adversarial-Search.md), where the "world" choosing outcomes becomes an opponent
choosing moves: minimax, alpha-beta and Monte Carlo tree search.

## Further reading

- S. Russell and P. Norvig, *Artificial Intelligence: A Modern Approach*, 4th ed., 2020: chapter 4 (search in complex
  environments: local search, continuous spaces, nondeterministic actions, partial observation).
- N. Metropolis, A. W. Rosenbluth, M. N. Rosenbluth, A. H. Teller and E. Teller, "Equation of state calculations by fast
  computing machines", *Journal of Chemical Physics* 21, 1953.
- S. Kirkpatrick, C. D. Gelatt and M. P. Vecchi, "Optimization by simulated annealing", *Science* 220, 1983;
  V. Černý, "Thermodynamical approach to the traveling salesman problem: an efficient simulation algorithm", *Journal of
  Optimization Theory and Applications* 45, 1985.
- S. Geman and D. Geman, "Stochastic relaxation, Gibbs distributions, and the Bayesian restoration of images", *IEEE
  Transactions on Pattern Analysis and Machine Intelligence* 6, 1984; B. Hajek, "Cooling schedules for optimal
  annealing", *Mathematics of Operations Research* 13, 1988.
- J. H. Holland, *Adaptation in Natural and Artificial Systems*, 1975; D. E. Goldberg, *Genetic Algorithms in Search,
  Optimization, and Machine Learning*, 1989.
- G. S. Hornby, A. Globus, D. S. Linden and J. D. Lohn, "Automated antenna design with evolutionary algorithms", AIAA
  Space 2006 conference.
- G. A. Croes, "A method for solving traveling-salesman problems", *Operations Research* 6, 1958; S. Lin and B. W.
  Kernighan, "An effective heuristic algorithm for the traveling-salesman problem", *Operations Research* 21, 1973.
- F. Glover, "Future paths for integer programming and links to artificial intelligence", *Computers and Operations
  Research* 13, 1986 (the paper that named tabu search).
- N. J. Nilsson, *Problem-Solving Methods in Artificial Intelligence*, 1971 (AND-OR graphs); B. Bonet and H. Geffner,
  "Planning with incomplete information as heuristic search in belief space", AIPS 2000.
- M. Maimone, Y. Cheng and L. Matthies, "Two years of visual odometry on the Mars Exploration Rovers", *Journal of
  Field Robotics* 24, 2007.
- On this site: [N-Queens](../../backtracking/n-queens.md) (the backtracking solution), the Algorithms book's
  [Chapter 14](../algorithms/14-Backtracking-and-Branch-and-Bound.md) (systematic search for the same problems) and
  [23.8](../algorithms/23-Approximation-and-Parameterized-Algorithms.md#238-heuristics-in-practice-local-search-sat-solvers-and-integer-programming-solvers)
  (local search, SAT and integer programming in practice), [Machine learning, Chapter 5](../machine-learning/05-Optimization.md)
  (gradient methods in depth), and [Probability](https://math.akadian.ca/books/probability/) for Markov chains.
