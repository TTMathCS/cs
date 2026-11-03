# 7. Constraint satisfaction

*In the searches of Chapters 3 to 6 a state was a black box: a search algorithm could test whether it was a goal and
generate its successors, and nothing else. Many problems have states with an obvious inside: a set of variables, each
with a value, and rules saying which combinations are allowed. Colouring a map, filling a Sudoku, timetabling a school
and placing queens are all like this. This chapter answers the question: what can a search algorithm gain by looking
inside the state? You will formulate problems as constraint satisfaction problems, solve them by backtracking with
heuristics that choose the next variable and value, prune with forward checking and arc consistency (proving that AC-3
terminates and what it costs), solve huge instances with the min-conflicts local search, and use the shape of the
constraint graph to solve tree-structured problems in linear time.*

!!! abstract "In this chapter"
    **You will learn:**

    - what a constraint satisfaction problem (CSP) is: variables, domains, constraints, and the constraint graph
    - how to write map colouring, Sudoku, n-queens and scheduling as CSPs
    - backtracking search with the MRV, degree and least-constraining-value heuristics, and why they are safe
    - constraint propagation: forward checking, arc consistency, and AC-3 with a proof of termination and of its $O(cd^3)$ cost
    - the min-conflicts local search, and why it solves n-queens for huge n in a few dozen steps
    - tree-structured CSPs solved in $O(nd^2)$ time, cutset conditioning, and tree decompositions

    **You need:** [Chapter 3](03-Uninformed-Search.md) (depth-first search) and [Chapter 5](05-Local-Search-and-Optimization.md)
    (local search, 5.2). The Algorithms book's [Chapter 14](../algorithms/14-Backtracking-and-Branch-and-Bound.md)
    (backtracking, Sudoku) and [Chapter 22](../algorithms/22-NP-Completeness.md) (NP-completeness) are the background;
    this chapter does not repeat them.

    **Levels:** 7.1 and 7.2 are beginner to intermediate; 7.3 is intermediate (the proofs are advanced); 7.4 is
    intermediate; 7.5 is advanced.

## 7.1 Variables, domains, constraints: map colouring, Sudoku, scheduling

Colour the map of Australia with three colours so that no two neighbouring regions share a colour. You could search
for it as in Chapter 3: a state is a partly coloured map, an action colours one more region. But that search would not
know what a "region" or a "colour" is, and so it would not notice, after colouring Western Australia and the Northern
Territory differently, that South Australia (which touches both) now has only one colour left. A **constraint
satisfaction problem** makes that structure explicit.

A **CSP** has three parts:

- a set of **variables** $X_1, \dots, X_n$;
- for each variable a **domain** $D_i$, the set of values it may take;
- a set of **constraints**, each naming some variables (its **scope**) and saying which combinations of their values
  are allowed (its **relation**).

An **assignment** gives values to some variables. It is **consistent** if it breaks no constraint, **complete** if
every variable has a value, and a **solution** is a complete, consistent assignment.

**Map colouring.** The variables are the seven regions WA, NT, SA, Q, NSW, V and T. Every domain is {red, green,
blue}. There is one constraint for each pair of neighbours, for example $\text{WA} \ne \text{NT}$; there are nine such
pairs. A constraint between two variables is **binary**, and a binary CSP can be drawn as a **constraint graph**: one
node per variable, one edge per constraint.

<figure class="mars-fig" markdown="0">
<svg viewBox="0 0 520 410" role="img" aria-label="The constraint graph of the map-colouring problem for Australia: nodes WA, NT, SA, Q, NSW, V and T, with an edge between each pair of neighbouring regions. SA touches every mainland region; T has no edges. The nodes are coloured with three colours so that no edge joins two nodes of the same colour.">
<line x1="90" y1="150" x2="220" y2="70" stroke="currentColor" stroke-width="1.5"/>
<line x1="90" y1="150" x2="240" y2="200" stroke="currentColor" stroke-width="1.5"/>
<line x1="220" y1="70" x2="240" y2="200" stroke="currentColor" stroke-width="1.5"/>
<line x1="220" y1="70" x2="380" y2="80" stroke="currentColor" stroke-width="1.5"/>
<line x1="240" y1="200" x2="380" y2="80" stroke="currentColor" stroke-width="1.5"/>
<line x1="240" y1="200" x2="400" y2="210" stroke="currentColor" stroke-width="1.5"/>
<line x1="240" y1="200" x2="330" y2="300" stroke="currentColor" stroke-width="1.5"/>
<line x1="380" y1="80" x2="400" y2="210" stroke="currentColor" stroke-width="1.5"/>
<line x1="400" y1="210" x2="330" y2="300" stroke="currentColor" stroke-width="1.5"/>
<circle cx="90" cy="150" r="27" style="fill:var(--md-default-bg-color)"/>
<circle cx="90" cy="150" r="27" fill="#9cc9ea" fill-opacity="0.85" stroke="currentColor" stroke-width="1.5"/>
<text x="90" y="155" font-size="14" text-anchor="middle" fill="currentColor" font-weight="bold">WA</text>
<circle cx="220" cy="70" r="27" style="fill:var(--md-default-bg-color)"/>
<circle cx="220" cy="70" r="27" fill="#7ccf9a" fill-opacity="0.85" stroke="currentColor" stroke-width="1.5"/>
<text x="220" y="75" font-size="14" text-anchor="middle" fill="currentColor" font-weight="bold">NT</text>
<circle cx="240" cy="200" r="27" style="fill:var(--md-default-bg-color)"/>
<circle cx="240" cy="200" r="27" fill="#eea66f" fill-opacity="0.85" stroke="currentColor" stroke-width="1.5"/>
<text x="240" y="205" font-size="14" text-anchor="middle" fill="currentColor" font-weight="bold">SA</text>
<circle cx="380" cy="80" r="27" style="fill:var(--md-default-bg-color)"/>
<circle cx="380" cy="80" r="27" fill="#9cc9ea" fill-opacity="0.85" stroke="currentColor" stroke-width="1.5"/>
<text x="380" y="85" font-size="14" text-anchor="middle" fill="currentColor" font-weight="bold">Q</text>
<circle cx="400" cy="210" r="27" style="fill:var(--md-default-bg-color)"/>
<circle cx="400" cy="210" r="27" fill="#7ccf9a" fill-opacity="0.85" stroke="currentColor" stroke-width="1.5"/>
<text x="400" y="215" font-size="14" text-anchor="middle" fill="currentColor" font-weight="bold">NSW</text>
<circle cx="330" cy="300" r="27" style="fill:var(--md-default-bg-color)"/>
<circle cx="330" cy="300" r="27" fill="#9cc9ea" fill-opacity="0.85" stroke="currentColor" stroke-width="1.5"/>
<text x="330" y="305" font-size="14" text-anchor="middle" fill="currentColor" font-weight="bold">V</text>
<circle cx="360" cy="375" r="27" style="fill:var(--md-default-bg-color)"/>
<circle cx="360" cy="375" r="27" fill="#eea66f" fill-opacity="0.85" stroke="currentColor" stroke-width="1.5"/>
<text x="360" y="380" font-size="14" text-anchor="middle" fill="currentColor" font-weight="bold">T</text>
<text x="470" y="30" font-size="12" text-anchor="end" fill="currentColor">colours:</text>
<rect x="478" y="40" width="16" height="16" fill="#eea66f" stroke="currentColor"/>
<text x="472" y="53" font-size="12" text-anchor="end" fill="currentColor">colour 1</text>
<rect x="478" y="62" width="16" height="16" fill="#7ccf9a" stroke="currentColor"/>
<text x="472" y="75" font-size="12" text-anchor="end" fill="currentColor">colour 2</text>
<rect x="478" y="84" width="16" height="16" fill="#9cc9ea" stroke="currentColor"/>
<text x="472" y="97" font-size="12" text-anchor="end" fill="currentColor">colour 3</text>
</svg>
<figcaption>Figure 7.1. The constraint graph for colouring Australia: one node per variable, one edge per constraint (neighbouring regions must differ). The colouring shown is the one backtracking with MRV and the degree heuristic finds: SA first, because it touches the most regions. Tasmania (T) has no constraints at all.</figcaption>
</figure>

The graph already tells us things. Tasmania is not connected to anything, so it can be coloured separately: the
problem splits into **independent subproblems**. And SA is connected to every other mainland region, so it is the place
to start.

**Sudoku.** The 81 cells are the variables; the domain of an empty cell is {1, ..., 9} and the domain of a clue is the
single given digit. The constraints say that the nine cells of each row, each column and each 3 × 3 box are all
different. That can be written as 27 constraints $\text{Alldiff}(\dots)$ on nine variables each, an example of a
**global constraint** (one with a scope of any size), or as $\binom{9}{2} = 36$ binary $\ne$ constraints per unit. Each
cell has 20 **peers** (cells sharing a row, column or box), so the binary version has $81 \cdot 20 / 2 = 810$
constraints. The programs below use the binary form.

**n-queens.** One variable per column, $Q_c$, with domain $\{0, \dots, n-1\}$, the row of its queen, and a binary
constraint for each pair of columns: $Q_a \ne Q_b$ and $|Q_a - Q_b| \ne |a - b|$.

**Scheduling.** A rover must do four things in one sol: drive to a rock (D, 3 hours), image it (I, 1 hour), drill (R, 2
hours) and send the data home (S, 1 hour). Variables are the start times, with domains $\{0, 1, \dots, 10\}$ (hours
after dawn). **Precedence constraints** say what must come first: $D + 3 \le I$, $D + 3 \le R$, $I + 1 \le S$,
$R + 2 \le S$. A **resource constraint** might say that imaging and drilling cannot overlap because they share a
power budget: $I + 1 \le R$ or $R + 2 \le I$. A **unary** constraint restricts one variable, for example "the
uplink is only available after hour 6": $S \ge 6$. NASA's MAPGEN tool, used to plan the daily activities of the Mars
Exploration Rovers, was built on a constraint-based planner of this general kind (Bresina, Jónsson, Morris and Rajan,
2005), with people making the final choices.

Some more words. Domains can be **finite** (colours, digits) or **infinite** (integers, real numbers). With infinite
domains, constraints must be written as formulas rather than tables; linear constraints over reals are **linear
programming** ([the Algorithms book, 23.5](../algorithms/23-Approximation-and-Parameterized-Algorithms.md#235-linear-programming-and-lp-relaxation-with-rounding)),
which is solvable in polynomial time, while over integers they are NP-hard. Constraints that must hold are **hard**;
**preferences** ("I would rather not teach on Friday") turn the CSP into a **constraint optimisation problem**. This
chapter treats finite domains and hard constraints.

**How hard is it?** Deciding whether a CSP with finite domains has a solution is NP-complete: graph 3-colouring is the
special case of map colouring, and it is one of the classic NP-complete problems ([the Algorithms book, Chapter
22](../algorithms/22-NP-Completeness.md)). So we should not expect a polynomial algorithm for every CSP. What we can do
is make search far faster in practice, and find special structures (7.5) that are easy.

## 7.2 Backtracking search with MRV, degree and least-constraining-value heuristics

A CSP has a property that general search problems lack: the order in which you assign the variables does not matter
for what the solution is. The assignment {WA = red, then NT = green} is the same as {NT = green, then WA = red}. So at
each node of the search tree it is enough to choose values for **one** variable. This is **backtracking search**: a
depth-first search that, at each node, picks an unassigned variable, tries each of its values that is consistent with
the assignment so far, recurses, and undoes the choice if the recursion fails.

```python
def backtrack(assignment):
    if assignment is complete:
        return assignment
    var = select_unassigned_variable(assignment)
    for value in order_domain_values(var, assignment):
        if value is consistent with assignment:
            assignment[var] = value
            inferences = infer(var, value)          # optional: forward checking, MAC (7.3)
            if no domain became empty:
                result = backtrack(assignment)
                if result is not None:
                    return result
            del assignment[var]                      # and undo the inferences
    return None
```

The Algorithms book's [Chapter 14](../algorithms/14-Backtracking-and-Branch-and-Bound.md) introduces backtracking on
n-queens and Sudoku. What a CSP adds is that the algorithm can be **generic**: the same code solves every CSP, and the
heuristics below work without knowing anything about the particular problem.

**Correctness.** Without the heuristics, backtracking over a fixed variable order visits every consistent partial
assignment that extends to a solution, because every solution is reached by its unique sequence of values in that
order, and the consistency test only prunes partial assignments that already break a constraint (no extension of
those can be a solution). So backtracking is **complete** (if a solution exists it finds one) and **sound** (it returns
only solutions, since the last step checks every constraint on the full assignment). The choice of which variable to
branch on can change from node to node without harming this: at each node, branching on any one unassigned variable
over all its values covers every extension. The order of the values changes only which solution is found first.
**Every heuristic below is therefore safe: it can change the running time, never the answer.**

The running time is exponential in the worst case: with $n$ variables and domains of size $d$ the tree has up to $d^n$
leaves. The heuristics attack the constant in that exponent.

### Which variable next? MRV and degree

The **minimum-remaining-values** (MRV) heuristic picks the variable with the fewest legal values left. It is also
called **most constrained variable** or **fail-first**: if some variable is about to have no values, MRV picks it at
once and the failure is detected before more work is wasted. If a variable has zero legal values left, MRV picks it
and fails immediately; if it has one, MRV makes the forced choice at once.

MRV needs to know the legal values of each variable, which it gets from forward checking (7.3). At the very start all
domains have the same size and MRV cannot choose. The **degree heuristic** breaks ties by picking the variable involved
in the most constraints with unassigned variables. For Australia, SA has degree 5, so it goes first.

### Which value first? Least constraining value

Once a variable is chosen, the **least-constraining-value** (LCV) heuristic tries first the value that rules out the
fewest choices for the neighbouring variables. The logic is the opposite of MRV: for the variable we want to fail fast
(a variable must be assigned eventually, so if it is going to fail, better now), but for the value we want to succeed
(only one value needs to work, so try the one most likely to). If we wanted every solution, value order would not
matter, since every value is tried anyway.

### A trace on Australia

Backtracking with MRV, degree as tie-breaker, and forward checking (each assignment removes the value from its
neighbours' domains):

| step | choose | why | domains after (r, g, b) |
|---|---|---|---|
| 1 | SA = r | all domains equal; SA has the highest degree (5) | WA gb, NT gb, Q gb, NSW gb, V gb, T rgb |
| 2 | NT = g | ties at 2 values; NT, Q and NSW tie at degree 2; NT is first in the list | WA b, Q b, NSW gb, V gb, T rgb |
| 3 | Q = b | WA and Q have 1 value; Q has the higher degree | WA b, NSW g, V gb, T rgb |
| 4 | NSW = g | 1 value | WA b, V b, T rgb |
| 5 | WA = b | 1 value | V b, T rgb |
| 6 | V = b | 1 value | T rgb |
| 7 | T = r | the only one left | |

Seven assignments and no backtracking. After the first two choices, every remaining mainland region is forced.

### Measured

The program implements a small generic CSP solver and runs it with and without the heuristics.

```python
--8<-- "books/ai/ch07_csp.py"
```

```
Australia, plain backtracking:       ({'WA': 'red', 'NT': 'green', 'SA': 'blue', 'Q': 'red', 'NSW': 'green', 'V': 'red', 'T': 'red'}, 7)
Australia, MRV + degree + fc:        ({'SA': 'red', 'NT': 'green', 'Q': 'blue', 'NSW': 'green', 'WA': 'blue', 'V': 'blue', 'T': 'red'}, 7)

n-queens: number of assignments until the first solution
                                n=8     n=12     n=16     n=24     n=32
plain                           113      261    10052        -        -
forward checking                 88      193     7560        -        -
MRV + fc                         75      153       44       43       89
MRV + degree + LCV + fc          39       32      332      256       35
MRV + MAC                        20       51       21       30       46

Sudoku, an easy puzzle, 32 clues (every cell counts as an assignment; 81 means no backtracking)
  MRV + fc   assignments 81
  MRV + MAC  assignments 81

Sudoku, a hard puzzle, 17 clues (every cell counts as an assignment; 81 means no backtracking)
  MRV + fc   assignments 498
  MRV + MAC  assignments 291
   4 1 7 3 6 9 8 2 5
   6 3 2 1 5 8 9 4 7
   9 5 8 7 2 4 3 1 6
   8 2 5 4 3 7 1 6 9
   7 9 1 5 8 6 4 3 2
   3 4 6 9 1 2 7 5 8
   2 8 9 6 4 3 5 7 1
   5 7 3 2 9 1 6 8 4
   1 6 4 8 7 5 2 9 3
```

What the numbers show:

- On n-queens, plain backtracking needs 10 052 assignments for $n = 16$; forward checking alone cuts that only by a
  quarter. Adding MRV brings it to a few dozen for every size up to 32. Fail-first is the big win.
- More heuristics are not always better on a given instance: MRV + degree + LCV is better than MRV alone at $n = 8$,
  12 and 32 and worse at 16 and 24. Heuristics are statistically good, not guaranteed. For n-queens the degree
  heuristic does nothing (every column constrains every other), so the difference comes from LCV and tie-breaking.
- MAC (7.3) gives the smallest trees at most sizes, at a higher cost per node.
- On the easy Sudoku, 81 assignments means each cell was assigned exactly once: forward checking plus MRV never had
  to guess. The hard 17-clue puzzle needs real search: 498 assignments with forward checking, 291 with MAC.

## 7.3 Constraint propagation: forward checking, arc consistency AC-3

*Level: intermediate (the proofs are advanced).*

Search makes choices; **inference** draws consequences. In a CSP the consequences of a choice can be computed by
**constraint propagation**: removing from the domains the values that can no longer be part of a solution.

### Forward checking

The simplest propagation: whenever a variable $X$ is assigned a value $v$, delete from the domain of each unassigned
neighbour $Y$ every value that conflicts with $X = v$. If some domain becomes empty, the current branch is dead and
backtracking can start at once. That is what the trace above did. Forward checking (Robert Haralick and Gordon
Elliott, 1980, who also proposed the fail-first principle) looks only one step ahead: it does not notice that two
unassigned neighbours now have the same single value. In the trace after step 2, WA and Q are each left with only
blue; they are not neighbours, so that is fine, but if they were, forward checking would not see the contradiction
until one of them was assigned.

### Arc consistency

An **arc** is a directed pair $(X, Y)$ of variables with a constraint between them. The arc is **consistent** if for
every value $a$ in $D_X$ there is some value $b$ in $D_Y$ such that $(a, b)$ satisfies the constraint; $b$ is called a
**support** for $a$. A CSP is **arc consistent** if every arc is. Making an arc consistent is simple: delete the values
of $X$ without support. That operation is called **revise**:

```python
def revise(X, Y):
    removed = False
    for a in list(D[X]):
        if no b in D[Y] satisfies the constraint with a:
            D[X].remove(a)
            removed = True
    return removed
```

Revising one arc can break another: if a value disappears from $D_X$, some value of a neighbour $Z$ may have lost its
only support, so the arc $(Z, X)$ must be checked again. **AC-3** (Alan Mackworth, 1977) keeps a queue of arcs to
check:

```python
def ac3():
    queue = all arcs (X, Y)
    while queue:
        (X, Y) = queue.pop()
        if revise(X, Y):
            if D[X] is empty:
                return False                     # no solution
            for each neighbour Z of X other than Y:
                queue.add((Z, X))
    return True
```

### A trace

Take three variables with domains {1, 2, 3} and the constraints $X < Y$ and $Y < Z$. The initial queue holds the four
arcs $(X, Y), (Y, X), (Y, Z), (Z, Y)$.

<figure class="mars-fig" markdown="0">
<svg viewBox="0 0 640 260" role="img" aria-label="A table showing the domains of X, Y and Z after each step of AC-3 on the constraints X less than Y less than Z: starting from 1 2 3 each, they shrink until X is 1, Y is 2 and Z is 3.">
<text x="20" y="28" font-size="13" text-anchor="start" fill="currentColor" font-weight="bold">step</text>
<text x="200" y="28" font-size="13" text-anchor="middle" fill="currentColor" font-weight="bold">X</text>
<text x="280" y="28" font-size="13" text-anchor="middle" fill="currentColor" font-weight="bold">Y</text>
<text x="360" y="28" font-size="13" text-anchor="middle" fill="currentColor" font-weight="bold">Z</text>
<text x="410" y="28" font-size="13" text-anchor="start" fill="currentColor" font-weight="bold">reason</text>
<line x1="15" y1="38" x2="625" y2="38" stroke="currentColor" stroke-width="1"/>
<text x="20" y="64" font-size="13" text-anchor="start" fill="currentColor" font-family="monospace">start</text>
<rect x="170" y="47" width="60" height="24" rx="4" fill="#9cc9ea" fill-opacity="0.3" stroke="currentColor" stroke-width="0.8"/>
<text x="200" y="64" font-size="13" text-anchor="middle" fill="currentColor" font-family="monospace">1 2 3</text>
<rect x="250" y="47" width="60" height="24" rx="4" fill="#9cc9ea" fill-opacity="0.3" stroke="currentColor" stroke-width="0.8"/>
<text x="280" y="64" font-size="13" text-anchor="middle" fill="currentColor" font-family="monospace">1 2 3</text>
<rect x="330" y="47" width="60" height="24" rx="4" fill="#9cc9ea" fill-opacity="0.3" stroke="currentColor" stroke-width="0.8"/>
<text x="360" y="64" font-size="13" text-anchor="middle" fill="currentColor" font-family="monospace">1 2 3</text>
<text x="410" y="64" font-size="12" text-anchor="start" fill="currentColor"></text>
<text x="20" y="98" font-size="13" text-anchor="start" fill="currentColor" font-family="monospace">revise(X, Y)</text>
<rect x="170" y="81" width="60" height="24" rx="4" fill="#eea66f" fill-opacity="0.75" stroke="currentColor" stroke-width="0.8"/>
<text x="200" y="98" font-size="13" text-anchor="middle" fill="currentColor" font-family="monospace">1 2</text>
<rect x="250" y="81" width="60" height="24" rx="4" fill="#9cc9ea" fill-opacity="0.3" stroke="currentColor" stroke-width="0.8"/>
<text x="280" y="98" font-size="13" text-anchor="middle" fill="currentColor" font-family="monospace">1 2 3</text>
<rect x="330" y="81" width="60" height="24" rx="4" fill="#9cc9ea" fill-opacity="0.3" stroke="currentColor" stroke-width="0.8"/>
<text x="360" y="98" font-size="13" text-anchor="middle" fill="currentColor" font-family="monospace">1 2 3</text>
<text x="410" y="98" font-size="12" text-anchor="start" fill="currentColor">X = 3 has no larger Y</text>
<text x="20" y="132" font-size="13" text-anchor="start" fill="currentColor" font-family="monospace">revise(Y, X)</text>
<rect x="170" y="115" width="60" height="24" rx="4" fill="#9cc9ea" fill-opacity="0.3" stroke="currentColor" stroke-width="0.8"/>
<text x="200" y="132" font-size="13" text-anchor="middle" fill="currentColor" font-family="monospace">1 2</text>
<rect x="250" y="115" width="60" height="24" rx="4" fill="#eea66f" fill-opacity="0.75" stroke="currentColor" stroke-width="0.8"/>
<text x="280" y="132" font-size="13" text-anchor="middle" fill="currentColor" font-family="monospace">2 3</text>
<rect x="330" y="115" width="60" height="24" rx="4" fill="#9cc9ea" fill-opacity="0.3" stroke="currentColor" stroke-width="0.8"/>
<text x="360" y="132" font-size="13" text-anchor="middle" fill="currentColor" font-family="monospace">1 2 3</text>
<text x="410" y="132" font-size="12" text-anchor="start" fill="currentColor">Y = 1 has no smaller X</text>
<text x="20" y="166" font-size="13" text-anchor="start" fill="currentColor" font-family="monospace">revise(Y, Z)</text>
<rect x="170" y="149" width="60" height="24" rx="4" fill="#9cc9ea" fill-opacity="0.3" stroke="currentColor" stroke-width="0.8"/>
<text x="200" y="166" font-size="13" text-anchor="middle" fill="currentColor" font-family="monospace">1 2</text>
<rect x="250" y="149" width="60" height="24" rx="4" fill="#eea66f" fill-opacity="0.75" stroke="currentColor" stroke-width="0.8"/>
<text x="280" y="166" font-size="13" text-anchor="middle" fill="currentColor" font-family="monospace">2</text>
<rect x="330" y="149" width="60" height="24" rx="4" fill="#9cc9ea" fill-opacity="0.3" stroke="currentColor" stroke-width="0.8"/>
<text x="360" y="166" font-size="13" text-anchor="middle" fill="currentColor" font-family="monospace">1 2 3</text>
<text x="410" y="166" font-size="12" text-anchor="start" fill="currentColor">Y = 3 has no larger Z</text>
<text x="20" y="200" font-size="13" text-anchor="start" fill="currentColor" font-family="monospace">revise(Z, Y)</text>
<rect x="170" y="183" width="60" height="24" rx="4" fill="#9cc9ea" fill-opacity="0.3" stroke="currentColor" stroke-width="0.8"/>
<text x="200" y="200" font-size="13" text-anchor="middle" fill="currentColor" font-family="monospace">1 2</text>
<rect x="250" y="183" width="60" height="24" rx="4" fill="#9cc9ea" fill-opacity="0.3" stroke="currentColor" stroke-width="0.8"/>
<text x="280" y="200" font-size="13" text-anchor="middle" fill="currentColor" font-family="monospace">2</text>
<rect x="330" y="183" width="60" height="24" rx="4" fill="#eea66f" fill-opacity="0.75" stroke="currentColor" stroke-width="0.8"/>
<text x="360" y="200" font-size="13" text-anchor="middle" fill="currentColor" font-family="monospace">3</text>
<text x="410" y="200" font-size="12" text-anchor="start" fill="currentColor">Z = 1, 2 have no smaller Y</text>
<text x="20" y="234" font-size="13" text-anchor="start" fill="currentColor" font-family="monospace">revise(X, Y)</text>
<rect x="170" y="217" width="60" height="24" rx="4" fill="#eea66f" fill-opacity="0.75" stroke="currentColor" stroke-width="0.8"/>
<text x="200" y="234" font-size="13" text-anchor="middle" fill="currentColor" font-family="monospace">1</text>
<rect x="250" y="217" width="60" height="24" rx="4" fill="#9cc9ea" fill-opacity="0.3" stroke="currentColor" stroke-width="0.8"/>
<text x="280" y="234" font-size="13" text-anchor="middle" fill="currentColor" font-family="monospace">2</text>
<rect x="330" y="217" width="60" height="24" rx="4" fill="#9cc9ea" fill-opacity="0.3" stroke="currentColor" stroke-width="0.8"/>
<text x="360" y="234" font-size="13" text-anchor="middle" fill="currentColor" font-family="monospace">3</text>
<text x="410" y="234" font-size="12" text-anchor="start" fill="currentColor">re-queued because Y shrank</text>
</svg>
<figcaption>Figure 7.2. AC-3 on X &lt; Y &lt; Z with domains {1, 2, 3}. Each row is one call of revise that removed something (orange: the domain that just shrank). When Y shrinks, the arc (X, Y) goes back on the queue, and its second revision removes 2 from X. Propagation alone solves this problem.</figcaption>
</figure>

AC-3 alone solves this problem. Usually it does not: it only shrinks the domains, and search must finish the job.

### Correctness, termination and cost

**Claim (soundness).** AC-3 never removes a value that belongs to some solution.

*Proof.* A value $a$ is removed from $D_X$ only when no value $b$ in the current $D_Y$ supports it. Suppose a solution
had $X = a$ and $Y = b'$. Then $b'$ supports $a$, so $b'$ must already have been removed from $D_Y$. Take the first
value of any solution that AC-3 removes; at that moment all values of that solution are still present, including its
value for $Y$, which supports it. Contradiction. $\square$

So if AC-3 empties a domain, the CSP has no solution; and after AC-3 the CSP has exactly the same solutions as before.

**Claim (termination and result).** AC-3 stops, and when it returns True the CSP is arc consistent.

*Proof.* An arc $(Z, X)$ is added to the queue only when a value has just been deleted from $D_X$. Each domain starts
with at most $d$ values and never grows, so values can be deleted at most $nd$ times in total, and only finitely many
arcs are ever added: the loop ends. When it ends, every arc is consistent: each arc was revised at least once (all
were in the initial queue), and after its last revision $(X, Y)$, the only thing that could make it inconsistent again
is a deletion from $D_Y$, which would have put $(X, Y)$ back on the queue. $\square$

**Claim (cost).** With $c$ binary constraints (so $2c$ arcs) and domains of size at most $d$, AC-3 takes $O(cd^3)$
time.

*Proof.* Arc $(Z, X)$ is re-added only after a deletion from $D_X$, which happens at most $d$ times, so each arc is
revised at most $d + 1$ times (once from the initial queue, then once per deletion). There are $2c$ arcs, so there are
$O(cd)$ revisions, and each revision compares up to $d \times d$ pairs of values: $O(cd^3)$ in total. $\square$

AC-4 (Mohr and Henderson, 1986) reaches the optimal $O(cd^2)$ by keeping, for every value, a count of its supports, and
later algorithms (AC-6, AC-2001) do it with less memory. In practice AC-3 with a good queue order is often competitive.

**What arc consistency does not do.** Three regions, mutually adjacent, with two colours each: every value of every
variable has a support on every arc (red is supported by green and vice versa), so the CSP is arc consistent, yet it
has no solution. Arc consistency looks at constraints one at a time; it cannot see that three of them together are
impossible. **Path consistency** looks at triples (for every consistent pair of values for $X, Y$ there must be a
value of each third variable $Z$ compatible with both), and in general **$k$-consistency** looks at $k$ variables
together. Strong $n$-consistency would solve any CSP without backtracking, but enforcing it costs exponential time in
general: there is no free lunch. A practical middle ground is special-purpose propagation for global constraints: for
$\text{Alldiff}$ on $m$ variables, if the union of their domains has fewer than $m$ values, there is no solution, and
Jean-Charles Régin's 1994 algorithm removes exactly the values that cannot appear in any all-different assignment,
using bipartite matching ([the Algorithms book, Chapter 17](../algorithms/17-Spanning-Trees-Flows-and-Matching.md)).

### Maintaining arc consistency (MAC)

Forward checking is the first step of AC-3. **MAC** does all of it during search: after assigning $X$, run AC-3
starting with the arcs $(Y, X)$ for the unassigned neighbours $Y$ of $X$. MAC detects every failure that forward
checking does, and more; the cost per node is higher, and the trees are smaller (the table in 7.2).

```python
--8<-- "books/ai/ch07_ac3.py"
```

```
X < Y < Z, domains {1,2,3}:
  revise(X,Y): remove [3] -> X = [1, 2]
  revise(Y,X): remove [1] -> Y = [2, 3]
  revise(Y,Z): remove [3] -> Y = [2]
  revise(Z,Y): remove [1, 2] -> Z = [3]
  revise(X,Y): remove [2] -> X = [1]
  (True, 5, 6) {'X': [1], 'Y': [2], 'Z': [3]}

triangle with 2 colours: AC-3 says consistent = True removed 0 values; domains {'A': ['green', 'red'], 'B': ['green', 'red'], 'C': ['green', 'red']}

Sudoku easy: 1620 arcs, 3591 revise calls, values 473 -> 81, cells decided 81/81

Sudoku hard: 1620 arcs, 2274 revise calls, values 593 -> 318, cells decided 17/81
  domain sizes after AC-3:
   1 4 5 3 4 4 1 4 1
   5 1 7 5 5 7 5 4 6
   4 5 6 1 6 7 5 5 6
   4 1 6 4 5 4 5 1 5
   4 5 6 3 1 5 1 5 5
   5 6 6 4 1 6 5 5 5
   3 2 3 1 3 1 4 1 5
   1 4 5 1 3 5 4 5 6
   1 4 1 3 3 4 5 5 5
```

- The trace matches Figure 7.2.
- The two-coloured triangle is arc consistent with nothing removed, as argued above.
- AC-3 solves the easy Sudoku outright: 473 candidate values shrink to 81, one per cell. This is the way human solvers
  start ("this cell's row already has a 3, so it is not 3"). On the hard puzzle AC-3 decides nothing beyond the 17
  clues (the 17 decided cells are the clues), though it removes 275 candidate values; search must do the rest.

## 7.4 Local search for CSPs: min-conflicts

*Level: intermediate.*

Local search ([Chapter 5](05-Local-Search-and-Optimization.md)) suits CSPs well when they are large and have many
solutions. Use the complete-state formulation: every variable has a value, some constraints are broken. The
**min-conflicts** heuristic repeatedly picks a variable that is in conflict, at random, and gives it the value that
breaks the fewest constraints, with ties broken at random:

```python
def min_conflicts(csp, max_steps):
    current = a complete assignment (greedy or random)
    for step in range(max_steps):
        if current is a solution:
            return current
        var = a random variable that is in some broken constraint
        current[var] = the value of var that minimises the number of broken constraints
    return failure
```

This is hill climbing (5.2) on the number of broken constraints, restricted to moves of conflicted variables. Steve
Minton, Mark Johnston, Andrew Philips and Philip Laird (1992) showed that it is remarkably effective. They found that,
from a greedy initial assignment, the number of repair steps for n-queens stays roughly constant as $n$ grows, and
solved problems with a million queens; they had developed it for scheduling observations of the Hubble Space Telescope.

### From scratch, with counts

To evaluate a move quickly, keep three arrays: how many queens are on each row, on each "up" diagonal ($r - c$
constant) and on each "down" diagonal ($r + c$ constant). The number of queens attacking square $(r, c)$ is then the sum
of three counts, and NumPy computes it for all $n$ rows of a column in one vector operation. The greedy start puts each
queen, column by column, on a randomly chosen unused row, trying up to 50 rows and keeping the first one with no
diagonal conflict.

```python
--8<-- "books/ai/ch07_min_conflicts.py"
```

```
       n   conflicted queens after greedy start   repair steps   solved
       8                                      3              5   True
     100                                     14             36   True
    1000                                     16             92   True
   10000                                     29             39   True
  100000                                     30             68   True
n =    8, 20 seeds, at most 1000 repairs: solved 17/20, repair steps when solved: median 44, max 921
n = 1000, 20 seeds, at most 1000 repairs: solved 20/20, repair steps when solved: median 68, max 174
```

- For $n = 100\,000$ the greedy start leaves only 30 conflicted queens, and 68 repairs remove them. The number of
  repairs barely grows with $n$: between 36 and 92 for $n$ from 100 to 100 000. Each repair costs $O(n)$ (one vector
  over the column), so the whole search is roughly linear in $n$. A million queens works the same way; in pure Python
  the greedy start alone would then take longer than the 10-second limit of the programs in this book, which is why
  the table stops at 100 000.
- Small boards are harder, not easier: on 8-queens 3 of 20 runs did not finish within 1000 repairs. With few
  solutions and few rows per column, min-conflicts can cycle on a plateau. Real implementations add restarts, random
  moves or a **tabu** list of recently changed variables.

Why does it work so well on n-queens? The solutions are dense: for large $n$ there are enormously many of them, spread
all over the space, so from almost anywhere a solution is a few moves away. Min-conflicts is poor near a **phase
transition**, where solutions are rare; for random 3-SAT that is near about 4.27 clauses per variable, as the
Algorithms book shows in [23.8](../algorithms/23-Approximation-and-Parameterized-Algorithms.md#238-heuristics-in-practice-local-search-sat-solvers-and-integer-programming-solvers).
A real advantage of local search is **online repair**: when a schedule is disrupted (a dust storm cancels a drive, an
observation runs long), min-conflicts starts from the old schedule and changes only what must change, instead of
building a new schedule from scratch that might move everything.

## 7.5 Structure: tree-structured CSPs solved in linear time, cutset conditioning

*Level: advanced.*

Sometimes the constraint graph's shape makes a CSP easy. The simplest case is **independence**: if the graph splits
into connected components, solve each separately. A problem with $n$ variables split into pieces of $k$ variables
costs $O((n/k) d^k)$ instead of $O(d^n)$: for $n = 80$, $d = 2$, $k = 20$ that is four pieces of a million each instead
of $2^{80}$.

### Tree-structured CSPs

A constraint graph is a **tree** if any two variables are connected by exactly one path. Then:

**Theorem.** A binary CSP whose constraint graph is a tree can be solved in $O(nd^2)$ time.

*The algorithm.*

1. Pick any variable as the root and list the variables in an order where each variable comes after its parent (for
   example breadth-first). Call them $X_1, \dots, X_n$; each $X_j$ with $j > 1$ has exactly one parent $X_{p(j)}$
   earlier in the list.
2. **Backward pass.** For $j = n$ down to 2: revise the arc $(X_{p(j)}, X_j)$, removing from the parent's domain every
   value with no support in the child. If a domain becomes empty, report failure.
3. **Forward pass.** For $j = 1$ to $n$: give $X_j$ any value in its domain consistent with the value already chosen
   for its parent.

<figure class="mars-fig" markdown="0">
<svg viewBox="0 0 640 380" role="img" aria-label="Top: a tree-shaped constraint graph with six variables A to F. Right: the same variables in an order where each variable after the first has exactly one parent earlier in the order: A, B, C, D, E, F. Arcs point from parent to child. The backward pass goes right to left making each parent arc consistent with its child; the forward pass assigns left to right.">
<line x1="180" y1="40" x2="280" y2="110" stroke="currentColor" stroke-width="1.5"/>
<line x1="180" y1="180" x2="280" y2="110" stroke="currentColor" stroke-width="1.5"/>
<line x1="280" y1="110" x2="380" y2="40" stroke="currentColor" stroke-width="1.5"/>
<line x1="280" y1="110" x2="380" y2="180" stroke="currentColor" stroke-width="1.5"/>
<line x1="380" y1="40" x2="480" y2="110" stroke="currentColor" stroke-width="1.5"/>
<circle cx="180" cy="40" r="20" style="fill:var(--md-default-bg-color)"/>
<circle cx="180" cy="40" r="20" fill="#9cc9ea" fill-opacity="0.6" stroke="currentColor" stroke-width="1.3"/>
<text x="180" y="45" font-size="14" text-anchor="middle" fill="currentColor" font-weight="bold">A</text>
<circle cx="280" cy="110" r="20" style="fill:var(--md-default-bg-color)"/>
<circle cx="280" cy="110" r="20" fill="#9cc9ea" fill-opacity="0.6" stroke="currentColor" stroke-width="1.3"/>
<text x="280" y="115" font-size="14" text-anchor="middle" fill="currentColor" font-weight="bold">B</text>
<circle cx="180" cy="180" r="20" style="fill:var(--md-default-bg-color)"/>
<circle cx="180" cy="180" r="20" fill="#9cc9ea" fill-opacity="0.6" stroke="currentColor" stroke-width="1.3"/>
<text x="180" y="185" font-size="14" text-anchor="middle" fill="currentColor" font-weight="bold">C</text>
<circle cx="380" cy="40" r="20" style="fill:var(--md-default-bg-color)"/>
<circle cx="380" cy="40" r="20" fill="#9cc9ea" fill-opacity="0.6" stroke="currentColor" stroke-width="1.3"/>
<text x="380" y="45" font-size="14" text-anchor="middle" fill="currentColor" font-weight="bold">D</text>
<circle cx="380" cy="180" r="20" style="fill:var(--md-default-bg-color)"/>
<circle cx="380" cy="180" r="20" fill="#9cc9ea" fill-opacity="0.6" stroke="currentColor" stroke-width="1.3"/>
<text x="380" y="185" font-size="14" text-anchor="middle" fill="currentColor" font-weight="bold">E</text>
<circle cx="480" cy="110" r="20" style="fill:var(--md-default-bg-color)"/>
<circle cx="480" cy="110" r="20" fill="#9cc9ea" fill-opacity="0.6" stroke="currentColor" stroke-width="1.3"/>
<text x="480" y="115" font-size="14" text-anchor="middle" fill="currentColor" font-weight="bold">F</text>
<path d="M 90 302 C 90 268 185 268 185 300" fill="none" stroke="#eea66f" stroke-width="2"/>
<polygon points="185,301 181,292 189,292" fill="#eea66f"/>
<path d="M 185 302 C 185 268 280 268 280 300" fill="none" stroke="#eea66f" stroke-width="2"/>
<polygon points="280,301 276,292 284,292" fill="#eea66f"/>
<path d="M 185 302 C 185 252 375 252 375 300" fill="none" stroke="#eea66f" stroke-width="2"/>
<polygon points="375,301 371,292 379,292" fill="#eea66f"/>
<path d="M 185 302 C 185 236 470 236 470 300" fill="none" stroke="#eea66f" stroke-width="2"/>
<polygon points="470,301 466,292 474,292" fill="#eea66f"/>
<path d="M 375 302 C 375 252 565 252 565 300" fill="none" stroke="#eea66f" stroke-width="2"/>
<polygon points="565,301 561,292 569,292" fill="#eea66f"/>
<circle cx="90" cy="320" r="18" style="fill:var(--md-default-bg-color)"/>
<circle cx="90" cy="320" r="18" fill="#7ccf9a" fill-opacity="0.6" stroke="currentColor" stroke-width="1.3"/>
<text x="90" y="325" font-size="14" text-anchor="middle" fill="currentColor" font-weight="bold">A</text>
<circle cx="185" cy="320" r="18" style="fill:var(--md-default-bg-color)"/>
<circle cx="185" cy="320" r="18" fill="#7ccf9a" fill-opacity="0.6" stroke="currentColor" stroke-width="1.3"/>
<text x="185" y="325" font-size="14" text-anchor="middle" fill="currentColor" font-weight="bold">B</text>
<circle cx="280" cy="320" r="18" style="fill:var(--md-default-bg-color)"/>
<circle cx="280" cy="320" r="18" fill="#7ccf9a" fill-opacity="0.6" stroke="currentColor" stroke-width="1.3"/>
<text x="280" y="325" font-size="14" text-anchor="middle" fill="currentColor" font-weight="bold">C</text>
<circle cx="375" cy="320" r="18" style="fill:var(--md-default-bg-color)"/>
<circle cx="375" cy="320" r="18" fill="#7ccf9a" fill-opacity="0.6" stroke="currentColor" stroke-width="1.3"/>
<text x="375" y="325" font-size="14" text-anchor="middle" fill="currentColor" font-weight="bold">D</text>
<circle cx="470" cy="320" r="18" style="fill:var(--md-default-bg-color)"/>
<circle cx="470" cy="320" r="18" fill="#7ccf9a" fill-opacity="0.6" stroke="currentColor" stroke-width="1.3"/>
<text x="470" y="325" font-size="14" text-anchor="middle" fill="currentColor" font-weight="bold">E</text>
<circle cx="565" cy="320" r="18" style="fill:var(--md-default-bg-color)"/>
<circle cx="565" cy="320" r="18" fill="#7ccf9a" fill-opacity="0.6" stroke="currentColor" stroke-width="1.3"/>
<text x="565" y="325" font-size="14" text-anchor="middle" fill="currentColor" font-weight="bold">F</text>
<text x="320" y="368" font-size="12" text-anchor="middle" fill="currentColor">backward pass: right to left, revise(parent, child); forward pass: left to right, assign</text>
</svg>
<figcaption>Figure 7.3. A tree-structured CSP (top) and a topological order of it (bottom), in which every variable has its parent, and only its parent, earlier in the order. Making each arc from parent to child consistent, from the last variable back to the first, and then assigning from first to last, never needs to backtrack.</figcaption>
</figure>

*Proof.* Cost: each of the $n - 1$ revisions compares at most $d^2$ pairs, and the forward pass looks at each variable
once with at most $d$ checks, so $O(nd^2)$.

Correctness. After the backward pass, every arc from a parent to a child is consistent, and stays so: when the arc
$(X_{p(j)}, X_j)$ is revised, the child $X_j$ will never lose another value, because all of $X_j$'s own children come
later in the order and were revised before it, and revisions only remove values from parents. (This is called
**directed arc consistency**.) In the forward pass, $X_1$ takes any value left in its domain. When we reach $X_j$, its
parent has a value that survived the revision of the arc $(X_{p(j)}, X_j)$, so it has a support in $D_{X_j}$; choose
it. $X_j$'s only constraint with an earlier variable is the one with its parent (in a tree, any other edge to an
earlier variable would make a cycle), so this choice is consistent with everything assigned so far. By induction the
forward pass never gets stuck and produces a solution. If the backward pass empties a domain, by the soundness of
revise (7.3) there is no solution. $\square$

So tree CSPs need no search at all. Eugene Freuder (1982) gave this result and the more general one behind it: if the
graph has width 1 (a tree), arc consistency suffices for backtrack-free search; in general, enough consistency relative
to the graph's width guarantees backtrack-free search. The same "pass messages up the tree, then down" pattern reappears
in exact inference for Bayesian networks ([Chapter 12](12-Probabilistic-Reasoning.md)) and in counting solutions
(Exercise 9).

### Cutset conditioning

Most graphs are not trees, but many are trees after deleting a few nodes. Australia is a tree (in fact a path plus an
isolated node) once SA is removed. **Cutset conditioning**:

1. Choose a set $S$ of variables (a **cycle cutset**) whose removal leaves a tree (or forest).
2. For each consistent assignment to the variables of $S$: remove from the domains of the remaining variables every
   value inconsistent with it, and solve the remaining tree CSP in $O((n - c)d^2)$.
3. If any of these tree problems has a solution, together with the assignment of $S$ it is a solution.

With $|S| = c$, the cost is $O(d^c (n - c) d^2)$: exponential only in the cutset size. Finding the smallest cycle cutset
is NP-hard, but approximations work well. The program checks the tree solver against brute force and measures its
linear cost, then runs cutset conditioning on Australia.

```python
--8<-- "books/ai/ch07_tree_csp.py"
```

```
200 random tree CSPs (8 variables, 3 values; 152 solvable): tree solver and brute force agree in 200

constraint checks of the tree solver (d = 5, every pair allowed with probability 0.6):
       n    checks   checks / (n d^2)   solved
      10       126              0.504   True
     100      1312              0.525   True
    1000     13051              0.522   True
   10000    130848              0.523   True
  100000   1309022              0.524   True

cutset conditioning on Australia with cutset {SA}:
  SA = red  : remaining forest [('NSW', 'Q'), ('NSW', 'V'), ('NT', 'Q'), ('NT', 'WA')]; solution {'WA': 'green', 'NT': 'blue', 'Q': 'green', 'NSW': 'blue', 'V': 'green', 'T': 'red'}
  SA = green: remaining forest [('NSW', 'Q'), ('NSW', 'V'), ('NT', 'Q'), ('NT', 'WA')]; solution {'WA': 'red', 'NT': 'blue', 'Q': 'red', 'NSW': 'blue', 'V': 'red', 'T': 'red'}
  SA = blue : remaining forest [('NSW', 'Q'), ('NSW', 'V'), ('NT', 'Q'), ('NT', 'WA')]; solution {'WA': 'red', 'NT': 'green', 'Q': 'red', 'NSW': 'green', 'V': 'red', 'T': 'red'}
```

- The tree solver agrees with brute force on all 200 random problems, including the 48 with no solution.
- The number of constraint checks divided by $n d^2$ stays at about 0.52 from $n = 10$ to $n = 100\,000$: the cost is
  linear in $n$, as proved.
- With SA fixed, the remaining forest (the path WA, NT, Q, NSW, V and the isolated T) is solved directly for each of SA's
  three colours, with no backtracking.

### Tree decompositions and treewidth

The other general approach groups variables instead of deleting them. A **tree decomposition** covers the constraint
graph with overlapping subsets of variables (the "bags") arranged in a tree, such that every constraint lies inside some
bag and the bags containing any one variable form a connected subtree. Solve each bag's subproblem completely (all its
solutions), then treat each bag as one big variable whose values are those solutions, with constraints that
neighbouring bags agree on their shared variables. That is a tree CSP. If the largest bag has $w + 1$ variables, the cost
is $O(n d^{w+1})$ for a fixed decomposition; the smallest possible $w$ is the graph's **treewidth**. A CSP whose graph has
bounded treewidth is solvable in polynomial time, which is one of the main results of the structural theory of CSPs.
Finding the treewidth exactly is NP-hard, but good decompositions are found by heuristics in practice.

**Values have structure too.** In map colouring the colours are interchangeable: any solution with the three colours
permuted is another solution, so there are $3! = 6$ copies of everything. Adding a **symmetry-breaking constraint**
(for example $\text{NT} < \text{SA} < \text{WA}$ in some order of the colours) removes the copies and can shrink the search by
the same factor.

**In practice.** Constraint programming systems such as Google OR-Tools CP-SAT, Gecode, Choco and MiniZinc (a modelling
language for many solvers) implement everything in this chapter, with many specialised global constraints; in Python,
`python-constraint` is a small library and OR-Tools has Python bindings.

### A short history thread

Constraint propagation entered AI with David Waltz's 1975 program for labelling the lines in drawings of polyhedra,
which pruned the possible labels of each junction against its neighbours, and Ugo Montanari's 1974 paper on networks of
constraints in picture processing. Alan Mackworth's 1977 paper defined node, arc and path consistency and gave AC-3.
Backtracking itself was analysed by Solomon Golomb and Leonard Baumert in 1965, and Haralick and Elliott's 1980 paper
introduced forward checking and the fail-first principle. Freuder (1982) related consistency to the graph's structure.
The local-search view came from Minton and colleagues (1992) and, for satisfiability, from GSAT and WalkSAT
([Chapter 8](08-Propositional-Logic-and-SAT.md)). Today constraint programming and SAT solving have largely merged:
the strongest constraint solvers learn clauses from conflicts exactly as SAT solvers do (8.6).

## Check yourself

??? question "1. How many solutions does the Australia map-colouring CSP have with three colours? Argue without a computer, then check with one."

    SA can take any of the 3 colours. Every mainland region touches SA, so WA, NT, Q, NSW and V must use the other two
    colours; they form a path WA, NT, Q, NSW, V, which alternates, so once WA is chosen (2 ways) the rest is forced. T
    is free: 3 ways. Total $3 \cdot 2 \cdot 3 = 18$.

    ```python
    nbrs = {"WA": ["NT", "SA"], "NT": ["WA", "SA", "Q"], "SA": ["WA", "NT", "Q", "NSW", "V"],
            "Q": ["NT", "SA", "NSW"], "NSW": ["Q", "SA", "V"], "V": ["SA", "NSW"], "T": []}
    order = ["SA", "NT", "Q", "NSW", "WA", "V", "T"]

    def count(i, colour):
        if i == len(order):
            return 1
        v, total = order[i], 0
        for c in range(3):
            if all(colour.get(n) != c for n in nbrs[v]):
                colour[v] = c
                total += count(i + 1, colour)
                del colour[v]
        return total

    print(count(0, {}))     # 18
    ```

??? question "2. Write the rover schedule of 7.1 (D 3 h, I 1 h, R 2 h, S 1 h; D before I and R; I and R before S; I and R do not overlap; S at hour 6 or later) and find the earliest finishing schedule by hand."

    D starts at 0 and ends at 3. I and R both need $\ge 3$ and must not overlap. Option 1: I at 3 to 4, R at 4 to 6,
    then S at $\max(6, 6) = 6$, finishing at 7. Option 2: R at 3 to 5, I at 5 to 6, S at 6, finishing at 7. Both
    finish at hour 7, and no schedule can finish earlier: S cannot start before 6 (the unary constraint) and lasts 1
    hour. Arc consistency on the precedence constraints alone would already reduce the domains to $D \in \{0, \dots, 5\}$,
    $S \in \{6, \dots, 10\}$, and so on; the "or" constraint is the one that needs search.

??? question "3. Do forward checking by hand on 4-queens after placing the first queen in row 0 of column 0. What do the domains of the other columns become, and which is chosen next by MRV?"

    Column 0, row 0 attacks row 0 in every column and the diagonal squares (1, 1), (2, 2), (3, 3) (column, row). So
    $D_1 = \{2, 3\}$, $D_2 = \{1, 3\}$, $D_3 = \{1, 2\}$. All have two values; MRV ties, and the degree heuristic also ties
    (every column constrains every other), so the first in order, column 1, is chosen. If it takes row 2, forward
    checking removes 1 and 3 from $D_2$ (row 3 is its diagonal), leaving $D_2$ empty: backtrack at once. If it takes
    row 3, $D_2$ loses 3 and is left with {1}, and $D_3$ loses 1 (its diagonal) and is left with {2}; then column 2 = 1
    removes 2 (a diagonal) from $D_3$ and empties it.
    So row 0 in column 0 leads to no solution, found after only four assignments.

??? question "4. Prove that AC-3 revises each arc at most d + 1 times, and give its cost for Sudoku in the binary form."

    An arc $(Z, X)$ enters the queue at the start and afterwards only when a value is deleted from $D_X$ (and it is not
    already queued). $D_X$ has at most $d$ values, so it can lose values at most $d$ times, and the arc is revised at
    most $1 + d$ times. For Sudoku: $c = 810$ constraints, $1620$ arcs, $d = 9$, so at most $1620 \cdot 10 = 16\,200$
    revisions, each comparing at most $81$ pairs. The program used 3591 revisions on the easy puzzle, well within the
    bound.

??? question "5. Show that the two-coloured triangle is arc consistent but not path consistent."

    Arcs: for $A$ = red, $B$ = green is a support; for $A$ = green, $B$ = red; the same for every arc. So it is arc
    consistent. Path consistency requires, for each consistent pair, a compatible value of the third variable. The pair
    $A$ = red, $B$ = green is consistent with $A \ne B$, but $C$ must differ from both, and only red and green exist.
    So the pair is removed; the same happens to every pair, and the empty relations prove that there is no solution.

??? question "6. Why does MRV choose the variable most likely to fail, while LCV chooses the value least likely to fail? Isn't that inconsistent?"

    Every variable must eventually get a value, so the search will have to face the hardest variable anyway; facing it
    early means that if it fails, the failure costs only a small subtree. For values the situation is different: we need
    only one value of the chosen variable to work, so we try the most promising first and may never have to try the
    others. If all solutions are wanted (or if the problem has none), value ordering makes no difference at all, while
    variable ordering still does.

??? question "7. In the backward pass of the tree algorithm, why must the arcs be revised from the last variable back to the first, and not in the forward order?"

    Revising $(X_{p(j)}, X_j)$ removes values from the parent only. If we went forwards, after revising
    $(X_{p(j)}, X_j)$ a later revision $(X_j, X_k)$ for a child $X_k$ of $X_j$ could remove values from $X_j$, and some
    parent value might then lose its only support in $X_j$: the arc we had made consistent would no longer be. Going
    backwards, all revisions that can shrink $X_j$ (those with $X_j$ as the parent) happen before $X_j$ itself is used
    as the child of a revision, so each arc stays consistent once revised.

??? question "8. A CSP has 100 variables with domains of size 10, and a cycle cutset of 5 variables. Compare the cost of cutset conditioning with brute force."

    Cutset conditioning: $d^c = 10^5$ assignments of the cutset, each followed by a tree solve of about $(n - c)d^2 = 95 \cdot 100 = 9500$
    checks: about $9.5 \times 10^8$ checks. Brute force: $10^{100}$ complete assignments. Even
    backtracking would face $10^{100}$ leaves in the worst case. Structure turns the impossible into a second's work.

??? question "9. Write code: count the solutions of a tree-structured CSP in O(nd^2) time, and check it on a path of 5 variables with 3 colours (neighbours different) and on Australia without SA."

    For each node and value, compute the number of ways to complete its subtree: the product, over the children, of
    the sum of the children's counts over compatible values. This is the backward pass with sums and products instead
    of "is there a support".

    ```python
    def count_tree(children, root, d, ok):
        """Number of solutions of a tree CSP: for each node and value, the number of ways to finish its subtree."""
        def ways(x):
            sub = [ways(c) for c in children.get(x, [])]
            return [prod(sum(w[b] for b in range(d) if ok(a, b)) for w in sub) for a in range(d)]
        return sum(ways(root))

    def prod(xs):
        p = 1
        for x in xs:
            p *= x
        return p

    # a path of 5 nodes with 3 colours, neighbours different: 3 * 2^4 = 48
    path = {0: [1], 1: [2], 2: [3], 3: [4]}
    print(count_tree(path, 0, 3, lambda a, b: a != b))
    # Australia without SA: the path WA-NT-Q-NSW-V, each with the 2 colours SA does not use
    print(count_tree({"WA": ["NT"], "NT": ["Q"], "Q": ["NSW"], "NSW": ["V"]}, "WA", 2, lambda a, b: a != b))
    ```

    It prints 48 and 2. Multiplying by 3 (SA) and 3 (T) gives $3 \cdot 2 \cdot 3 = 18$ solutions of Australia, as in
    Exercise 1: cutset conditioning counts solutions too, by summing over the cutset assignments.

??? question "10. Min-conflicts solved 100 000-queens in 68 repairs but failed 3 of 20 times on 8-queens within 1000 repairs. Explain, and suggest a fix."

    For large $n$ the solutions are extremely dense and the greedy start is already almost a solution, so a few dozen
    local repairs suffice. For small $n$ there are few solutions (92 for $n = 8$, out of $8^8$ assignments) and the
    landscape has plateaus and small local minima where every move of a conflicted queen keeps the number of conflicts
    the same or raises it; the random tie-breaking can then cycle among a few states. Fixes: restart after a fixed number
    of steps (5.2), occasionally move a random queen to a random row (a random walk step), or forbid changing the same
    queen again for a few steps (a tabu list).

??? question "11. Explain why deciding whether a finite-domain CSP has a solution is in NP and is NP-hard."

    In NP: a solution is a certificate; checking it means evaluating every constraint on it, which takes time polynomial
    in the size of the CSP (for constraints given as tables of allowed tuples or as efficiently computable relations).
    NP-hard: graph 3-colouring is NP-complete ([the Algorithms book, Chapter 22](../algorithms/22-NP-Completeness.md)),
    and it is a CSP: one variable per vertex, domain {1, 2, 3}, a $\ne$ constraint per edge. So a polynomial algorithm
    for all CSPs would give one for 3-colouring, hence P = NP. SAT is also a CSP (Boolean variables, one constraint per
    clause), the subject of [Chapter 8](08-Propositional-Logic-and-SAT.md).

## What you learned

- A CSP has variables, domains and constraints; its constraint graph shows which variables interact. Map colouring,
  Sudoku, n-queens and scheduling are all CSPs, and the general problem is NP-complete.
- Backtracking assigns one variable per level; MRV (fail-first), the degree heuristic and least-constraining-value
  change the running time but never the answer, and MRV is the big win.
- Forward checking and arc consistency remove values that cannot be in any solution; AC-3 is sound, terminates and
  costs $O(cd^3)$; MAC runs it inside search. Arc consistency does not detect every inconsistency (the triangle).
- Min-conflicts is hill climbing on broken constraints; it solves n-queens with a roughly constant number of repairs
  for huge $n$, and repairs schedules online.
- Tree-structured CSPs are solved without search in $O(nd^2)$ by directed arc consistency and a forward pass; cutset
  conditioning costs $O(d^c (n-c) d^2)$, and tree decompositions make bounded-treewidth CSPs polynomial.

**Next:** [Chapter 8](08-Propositional-Logic-and-SAT.md), where the variables become true/false propositions, the
constraints become logical clauses, and the solvers become SAT solvers that learn from their own failures.

## Further reading

- S. Russell and P. Norvig, *Artificial Intelligence: A Modern Approach*, 4th ed., 2020: chapter 6 (constraint
  satisfaction problems).
- R. Dechter, *Constraint Processing*, 2003; F. Rossi, P. van Beek and T. Walsh (eds.), *Handbook of Constraint
  Programming*, 2006.
- A. K. Mackworth, "Consistency in networks of relations", *Artificial Intelligence* 8, 1977; R. Mohr and T. C.
  Henderson, "Arc and path consistency revisited", *Artificial Intelligence* 28, 1986.
- R. M. Haralick and G. L. Elliott, "Increasing tree search efficiency for constraint satisfaction problems",
  *Artificial Intelligence* 14, 1980; S. W. Golomb and L. D. Baumert, "Backtrack programming", *Journal of the ACM* 12,
  1965.
- E. C. Freuder, "A sufficient condition for backtrack-free search", *Journal of the ACM* 29, 1982.
- S. Minton, M. D. Johnston, A. B. Philips and P. Laird, "Minimizing conflicts: a heuristic repair method for constraint
  satisfaction and scheduling problems", *Artificial Intelligence* 58, 1992.
- D. Waltz, "Understanding line drawings of scenes with shadows", in P. H. Winston (ed.), *The Psychology of Computer
  Vision*, 1975; U. Montanari, "Networks of constraints: fundamental properties and applications to picture
  processing", *Information Sciences* 7, 1974.
- J.-C. Régin, "A filtering algorithm for constraints of difference in CSPs", AAAI 1994.
- J. Bresina, A. Jónsson, P. Morris and K. Rajan, "Activity planning for the Mars Exploration Rovers", ICAPS 2005.
- On this site: the Algorithms book's [Chapter 14](../algorithms/14-Backtracking-and-Branch-and-Bound.md) (backtracking,
  n-queens and Sudoku), [Chapter 22](../algorithms/22-NP-Completeness.md) (why CSPs are hard) and
  [23.8](../algorithms/23-Approximation-and-Parameterized-Algorithms.md#238-heuristics-in-practice-local-search-sat-solvers-and-integer-programming-solvers);
  the reference page [N-Queens](../../backtracking/n-queens.md); and [Chapter 5](05-Local-Search-and-Optimization.md)
  of this book for local search.
