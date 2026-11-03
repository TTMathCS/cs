# 8. Propositional logic and SAT solvers

*An agent that only searches knows nothing except the problem it was given. An agent that reasons can be told facts,
combine them and conclude things nobody told it: there is no pit here, the rock is reachable, the drill is safe to use.
This chapter answers the questions: how can knowledge be written down so that a machine can reason with it, what does
it mean for a conclusion to follow, and how can a program decide that quickly? You will define propositional logic
exactly, check entailment with truth tables, prove things by resolution (with a sketch of why resolution is sound and
complete), reason in linear time with Horn clauses, and build the DPLL and WalkSAT satisfiability solvers from scratch.
Finally you will build a conflict-driven clause-learning solver, the design behind the SAT solvers that check chips and
software today, and see exactly where its speed comes from.*

!!! abstract "In this chapter"
    **You will learn:**

    - what a knowledge-based agent is, using the wumpus world as the running example
    - the syntax and semantics of propositional logic: models, entailment, validity, satisfiability, truth tables
    - conversion to conjunctive normal form, and resolution, with a sketch of its soundness and completeness
    - Horn clauses, and forward and backward chaining, with a proof that forward chaining runs in linear time
    - DPLL (1962) and WalkSAT, from scratch, and why unsatisfiable problems like the pigeonhole principle are hard
    - CDCL: implication graphs, first-UIP clause learning, backjumping, watched literals, VSIDS and restarts

    **You need:** [Chapter 7](07-Constraint-Satisfaction.md) (backtracking, propagation, local search for CSPs). The
    Algorithms book's [Chapter 22](../algorithms/22-NP-Completeness.md) (SAT and the Cook-Levin theorem) is the
    background for 8.5 and 8.6. The [Logic](https://math.akadian.ca/books/logic/) book on math.akadian.ca covers the
    same logic from the mathematical side.

    **Levels:** 8.1 and 8.2 are beginner; 8.3 and 8.4 are intermediate; 8.5 is intermediate; 8.6 is advanced.

## 8.1 Knowledge-based agents; the wumpus world

The agents of the earlier chapters had their knowledge built in: a transition model, a heuristic, a set of
constraints. A **knowledge-based agent** keeps a **knowledge base** (KB): a set of **sentences** in a formal
**knowledge representation language**, each stating something the agent believes about the world. It interacts with
the KB through two operations:

- **Tell**: add a sentence (a percept, a rule, a fact learned).
- **Ask**: query whether some sentence follows from the KB. The answer is computed by **inference**.

```python
def kb_agent(percept, t):
    tell(KB, sentence describing percept at time t)
    action = ask(KB, "what action should I do at time t?")
    tell(KB, sentence saying that action was done at time t)
    return action
```

The point of this design is that the agent can be built **declaratively**: you tell it what is true and what it
wants, and inference works out what to do, instead of programming each behaviour. A new fact (a new map of the terrain,
a broken wheel) changes behaviour without changing code.

### The wumpus world

The standard teaching example, adapted by Russell and Norvig from Gregory Yob's 1973 computer game *Hunt the Wumpus*,
is a 4 × 4 grid of rooms. Somewhere there is gold, a wumpus (a monster that eats anyone entering its room) and some
bottomless pits. The agent starts in the bottom-left room [1,1], facing right. It cannot see the hazards, but it
perceives:

- a **stench** in the room with the wumpus and in the rooms next to it (not diagonally);
- a **breeze** in the rooms next to a pit;
- a **glitter** in the room with the gold.

The environment is deterministic, discrete, static and single-agent, but **partially observable**: the agent learns
about the hazards only through these local percepts, and it must **reason** to stay alive.

Here is the reasoning we want to automate. In [1,1] the agent feels no breeze. So neither neighbour, [1,2] nor [2,1],
has a pit: both are safe. It moves to [2,1] and feels a breeze. So [2,2] or [3,1] (the neighbours of [2,1] other than
[1,1], which is known to be safe) holds a pit. It does not know which. A careful agent goes back and tries [1,2].

<figure class="mars-fig" markdown="0">
<svg viewBox="0 0 560 360" role="img" aria-label="A 4 by 4 wumpus-world grid. The agent started in square 1,1, felt no breeze there and moved to 2,1, where it felt a breeze. Squares 1,1, 2,1 and 1,2 are marked OK. Squares 2,2 and 3,1 are marked P question mark: one of them may hold a pit.">
<rect x="40" y="260" width="80" height="80" fill="#7ccf9a" fill-opacity="0.45" stroke="currentColor" stroke-width="1.2"/>
<text x="80" y="305" font-size="18" text-anchor="middle" fill="currentColor" font-weight="bold">OK</text>
<text x="46" y="275" font-size="11" text-anchor="start" fill="currentColor">[1,1]</text>
<rect x="40" y="180" width="80" height="80" fill="#7ccf9a" fill-opacity="0.45" stroke="currentColor" stroke-width="1.2"/>
<text x="80" y="225" font-size="18" text-anchor="middle" fill="currentColor" font-weight="bold">OK</text>
<text x="46" y="195" font-size="11" text-anchor="start" fill="currentColor">[1,2]</text>
<rect x="40" y="100" width="80" height="80" fill="none" stroke="currentColor" stroke-width="1.2"/>
<text x="46" y="115" font-size="11" text-anchor="start" fill="currentColor">[1,3]</text>
<rect x="40" y="20" width="80" height="80" fill="none" stroke="currentColor" stroke-width="1.2"/>
<text x="46" y="35" font-size="11" text-anchor="start" fill="currentColor">[1,4]</text>
<rect x="120" y="260" width="80" height="80" fill="#eea66f" fill-opacity="0.45" stroke="currentColor" stroke-width="1.2"/>
<text x="160" y="305" font-size="18" text-anchor="middle" fill="currentColor" font-weight="bold">B</text>
<text x="126" y="275" font-size="11" text-anchor="start" fill="currentColor">[2,1]</text>
<rect x="120" y="180" width="80" height="80" fill="#9cc9ea" fill-opacity="0.45" stroke="currentColor" stroke-width="1.2"/>
<text x="160" y="225" font-size="18" text-anchor="middle" fill="currentColor" font-weight="bold">P?</text>
<text x="126" y="195" font-size="11" text-anchor="start" fill="currentColor">[2,2]</text>
<rect x="120" y="100" width="80" height="80" fill="none" stroke="currentColor" stroke-width="1.2"/>
<text x="126" y="115" font-size="11" text-anchor="start" fill="currentColor">[2,3]</text>
<rect x="120" y="20" width="80" height="80" fill="none" stroke="currentColor" stroke-width="1.2"/>
<text x="126" y="35" font-size="11" text-anchor="start" fill="currentColor">[2,4]</text>
<rect x="200" y="260" width="80" height="80" fill="#9cc9ea" fill-opacity="0.45" stroke="currentColor" stroke-width="1.2"/>
<text x="240" y="305" font-size="18" text-anchor="middle" fill="currentColor" font-weight="bold">P?</text>
<text x="206" y="275" font-size="11" text-anchor="start" fill="currentColor">[3,1]</text>
<rect x="200" y="180" width="80" height="80" fill="none" stroke="currentColor" stroke-width="1.2"/>
<text x="206" y="195" font-size="11" text-anchor="start" fill="currentColor">[3,2]</text>
<rect x="200" y="100" width="80" height="80" fill="none" stroke="currentColor" stroke-width="1.2"/>
<text x="206" y="115" font-size="11" text-anchor="start" fill="currentColor">[3,3]</text>
<rect x="200" y="20" width="80" height="80" fill="none" stroke="currentColor" stroke-width="1.2"/>
<text x="206" y="35" font-size="11" text-anchor="start" fill="currentColor">[3,4]</text>
<rect x="280" y="260" width="80" height="80" fill="none" stroke="currentColor" stroke-width="1.2"/>
<text x="286" y="275" font-size="11" text-anchor="start" fill="currentColor">[4,1]</text>
<rect x="280" y="180" width="80" height="80" fill="none" stroke="currentColor" stroke-width="1.2"/>
<text x="286" y="195" font-size="11" text-anchor="start" fill="currentColor">[4,2]</text>
<rect x="280" y="100" width="80" height="80" fill="none" stroke="currentColor" stroke-width="1.2"/>
<text x="286" y="115" font-size="11" text-anchor="start" fill="currentColor">[4,3]</text>
<rect x="280" y="20" width="80" height="80" fill="none" stroke="currentColor" stroke-width="1.2"/>
<text x="286" y="35" font-size="11" text-anchor="start" fill="currentColor">[4,4]</text>
<path d="M 80 322 L 160 322" stroke="currentColor" stroke-width="1.5" stroke-dasharray="4 3"/>
<polygon points="160,322 152,317 152,327" fill="currentColor"/>
<text x="106" y="276" font-size="13" text-anchor="middle" fill="currentColor" font-weight="bold">A</text>
<rect x="380" y="40" width="30" height="26" fill="#7ccf9a" fill-opacity="0.45" stroke="currentColor"/>
<text x="395" y="58" font-size="12" text-anchor="middle" fill="currentColor" font-weight="bold">OK</text>
<text x="420" y="58" font-size="12" text-anchor="start" fill="currentColor">no pit, no wumpus</text>
<rect x="380" y="80" width="30" height="26" fill="#eea66f" fill-opacity="0.45" stroke="currentColor"/>
<text x="395" y="98" font-size="12" text-anchor="middle" fill="currentColor" font-weight="bold">B</text>
<text x="420" y="98" font-size="12" text-anchor="start" fill="currentColor">breeze felt here</text>
<rect x="380" y="120" width="30" height="26" fill="#9cc9ea" fill-opacity="0.45" stroke="currentColor"/>
<text x="395" y="138" font-size="12" text-anchor="middle" fill="currentColor" font-weight="bold">P?</text>
<text x="420" y="138" font-size="12" text-anchor="start" fill="currentColor">pit possible</text>
<text x="380" y="200" font-size="12" text-anchor="start" fill="currentColor">the agent (A) went from</text>
<text x="380" y="218" font-size="12" text-anchor="start" fill="currentColor">[1,1] to [2,1]</text>
<text x="380" y="250" font-size="12" text-anchor="start" fill="currentColor">KB entails: no pit in [1,2];</text>
<text x="380" y="268" font-size="12" text-anchor="start" fill="currentColor">a pit in [2,2] or [3,1]</text>
<text x="380" y="300" font-size="12" text-anchor="start" fill="currentColor">KB does not entail which</text>
</svg>
<figcaption>Figure 8.1. The wumpus world after two moves. No breeze in [1,1] means no pit in [1,2] or [2,1]; the breeze in [2,1] means a pit in [2,2] or [3,1] (not [1,1], which is safe). The knowledge base entails the first conclusion and the disjunction, but neither "pit in [2,2]" nor its negation.</figcaption>
</figure>

To mechanise that, we need a language in which "no breeze in [1,1]" and "a room is breezy exactly when a neighbour has
a pit" are sentences, a precise meaning for "follows", and an algorithm.

## 8.2 Syntax and semantics; entailment; truth tables

### Syntax

The **atomic sentences** of propositional logic are **proposition symbols** such as $P_{1,2}$ ("there is a pit in
[1,2]") or $B_{2,1}$ ("there is a breeze in [2,1]"), plus the constants True and False. **Complex sentences** are
built with five **connectives**:

| connective | name | read as |
|---|---|---|
| $\neg A$ | negation | not $A$ |
| $A \wedge B$ | conjunction | $A$ and $B$ |
| $A \vee B$ | disjunction | $A$ or $B$ (or both) |
| $A \Rightarrow B$ | implication | if $A$ then $B$ |
| $A \Leftrightarrow B$ | biconditional | $A$ if and only if $B$ |

A **literal** is a symbol or its negation ($P$, $\neg P$). In $A \Rightarrow B$, $A$ is the **premise** and $B$ the
**conclusion**.

### Semantics

A **model** fixes the truth value of every symbol: it is one possible world, as far as the language can tell. With $n$
symbols there are $2^n$ models. The truth value of a complex sentence in a model is computed from its parts by the
**truth tables** of the connectives:

| $A$ | $B$ | $\neg A$ | $A \wedge B$ | $A \vee B$ | $A \Rightarrow B$ | $A \Leftrightarrow B$ |
|---|---|---|---|---|---|---|
| false | false | true | false | false | true | true |
| false | true | true | false | true | true | false |
| true | false | false | false | true | false | false |
| true | true | false | true | true | true | true |

The row that surprises beginners is "$A \Rightarrow B$ is true when $A$ is false". Implication in logic says only
"it is not the case that $A$ is true and $B$ false"; it claims no causal connection. "If the Moon is made of cheese then
5 is prime" is true.

If sentence $\alpha$ is true in model $m$, we say $m$ **satisfies** $\alpha$, or $m$ is a model **of** $\alpha$. Write
$M(\alpha)$ for the set of all models of $\alpha$.

### Entailment

The central idea: $\alpha$ **entails** $\beta$, written $\alpha \models \beta$, if $\beta$ is true in every model in
which $\alpha$ is true:

$$
\alpha \models \beta \quad\text{if and only if}\quad M(\alpha) \subseteq M(\beta).
$$

Entailment is what "follows" means. Note the direction: the stronger sentence (true in fewer worlds) entails the
weaker one. $P \wedge Q \models P$, because every world where both hold is a world where $P$ holds.

Three related notions:

- $\alpha$ is **valid** (a **tautology**) if it is true in every model, for example $P \vee \neg P$;
- $\alpha$ is **satisfiable** if it is true in at least one model;
- $\alpha$ is **unsatisfiable** if it is true in none, for example $P \wedge \neg P$.

They are tied together by two facts that are used everywhere:

**Theorem (deduction).** $\alpha \models \beta$ if and only if $\alpha \Rightarrow \beta$ is valid.

**Theorem (refutation).** $\alpha \models \beta$ if and only if $\alpha \wedge \neg\beta$ is unsatisfiable.

*Proof of both.* $\alpha \models \beta$ says there is no model where $\alpha$ is true and $\beta$ false. "$\alpha$ true
and $\beta$ false" is exactly when $\alpha \Rightarrow \beta$ is false, and exactly when $\alpha \wedge \neg\beta$ is
true. So "no such model" means "$\alpha \Rightarrow \beta$ is never false" (valid) and "$\alpha \wedge \neg \beta$ is never
true" (unsatisfiable). $\square$

The refutation theorem is the bridge to SAT: **to prove that the KB entails $\beta$, show that KB $\wedge \neg\beta$ has no
satisfying assignment.** A SAT solver, which looks for satisfying assignments, is therefore a theorem prover.

### The wumpus KB

With only the rooms [1,1], [1,2], [2,1], [2,2] and [3,1] in play, the agent knows:

- $R_1$: $\neg P_{1,1}$ (the start is safe);
- $R_2$: $B_{1,1} \Leftrightarrow (P_{1,2} \vee P_{2,1})$ (a room is breezy exactly when a neighbour has a pit);
- $R_3$: $B_{2,1} \Leftrightarrow (P_{1,1} \vee P_{2,2} \vee P_{3,1})$;
- $R_4$: $\neg B_{1,1}$ (percept: no breeze in [1,1]);
- $R_5$: $B_{2,1}$ (percept: breeze in [2,1]).

The KB is $R_1 \wedge R_2 \wedge R_3 \wedge R_4 \wedge R_5$, over seven symbols.

### Model checking with a truth table

The most direct inference algorithm enumerates all $2^n$ models and checks that $\beta$ is true in every model of KB.
It is **sound** (it answers "entailed" only when it is, since it checks the definition) and **complete** (it always
answers, since the number of models is finite). Its time is $O(2^n)$ and its memory $O(n)$.

```python
--8<-- "books/ai/ch08_logic.py"
```

```
KB |= no pit in [1,2]           ? True   (truth-table rows checked: 128)
KB |= no pit in [2,2]           ? False  (truth-table rows checked: 35)
KB |= a pit in [2,2] or [3,1]   ? True   (truth-table rows checked: 128)
the table has 128 rows over 7 symbols; KB is true in 3 of them:
    {'B11': 0, 'B21': 1, 'P11': 0, 'P12': 0, 'P21': 0, 'P22': 0, 'P31': 1}
    {'B11': 0, 'B21': 1, 'P11': 0, 'P12': 0, 'P21': 0, 'P22': 1, 'P31': 0}
    {'B11': 0, 'B21': 1, 'P11': 0, 'P12': 0, 'P21': 0, 'P22': 1, 'P31': 1}

CNF of R2 (B11 <=> P12 v P21): (-B11 v P12 v P21)  (B11 v -P12)  (B11 v -P21)
KB in CNF: (-B11)  (-P11)  (B21)  (B21 v -P11)  (B11 v -P12)  (B11 v -P21)  (B21 v -P22)  (B21 v -P31)  (-B11 v P12 v P21)  (-B21 v P11 v P22 v P31)
resolution: KB |= no pit in [1,2]? True  (6 resolvents computed, 16 clauses at the end)
resolution: KB |= no pit in [2,2]? False  (127 resolvents computed, 29 clauses at the end)
```

The first part of the output confirms the reasoning of 8.1 mechanically. The KB is true in exactly 3 of the 128 models;
in all three $P_{1,2}$ is false, so the KB entails "no pit in [1,2]". In all three $P_{2,2} \vee P_{3,1}$ is true. But
$P_{2,2}$ is false in one model and true in two, so neither "pit in [2,2]" nor "no pit in [2,2]" is entailed. The
search for a counterexample to "no pit in [2,2]" stopped at row 35, the first model of the KB in which $P_{2,2}$ is
true. (The second half of the output, CNF and resolution, is explained in 8.3.)

Is there an algorithm for entailment that is always much faster than $2^n$? Entailment is the complement of
satisfiability: KB $\models \beta$ is co-NP-complete, so a polynomial algorithm for it would imply P = NP
([the Algorithms book, 22.6](../algorithms/22-NP-Completeness.md#226-karps-21-problems-co-np-and-pspace)). The rest of
the chapter is about doing much better than truth tables in practice.

## 8.3 Inference: resolution, soundness and completeness; CNF conversion

*Level: intermediate.*

Model checking reasons about worlds. **Theorem proving** reasons about sentences: it applies **inference rules**, each
producing a new sentence from old ones, until the goal appears. A **proof** is a sequence of such steps. An inference
procedure is **sound** if everything it derives is entailed, and **complete** if it can derive everything that is
entailed.

Two familiar rules:

- **Modus ponens:** from $A \Rightarrow B$ and $A$, infer $B$.
- **And-elimination:** from $A \wedge B$, infer $A$.

Both are sound: you can check with a truth table that in every model of the premises the conclusion is true. A
**logical equivalence** $\alpha \equiv \beta$ ($\alpha$ and $\beta$ have the same models) can be used as a rule in both
directions. The ones we need:

| equivalence | name |
|---|---|
| $A \Leftrightarrow B \equiv (A \Rightarrow B) \wedge (B \Rightarrow A)$ | biconditional elimination |
| $A \Rightarrow B \equiv \neg A \vee B$ | implication elimination |
| $\neg(A \wedge B) \equiv \neg A \vee \neg B$, $\neg(A \vee B) \equiv \neg A \wedge \neg B$ | De Morgan |
| $\neg\neg A \equiv A$ | double negation |
| $A \vee (B \wedge C) \equiv (A \vee B) \wedge (A \vee C)$ | distributivity of $\vee$ over $\wedge$ |

### Conjunctive normal form

A **clause** is a disjunction of literals, such as $\neg B_{1,1} \vee P_{1,2} \vee P_{2,1}$. A sentence is in
**conjunctive normal form** (CNF) if it is a conjunction of clauses. **Every sentence is equivalent to one in CNF**,
by four steps, each an equivalence from the table:

1. eliminate $\Leftrightarrow$ (biconditional elimination);
2. eliminate $\Rightarrow$ (implication elimination);
3. move $\neg$ inwards until it applies only to symbols (De Morgan, double negation): **negation normal form**;
4. distribute $\vee$ over $\wedge$ until no $\wedge$ is inside an $\vee$.

For $R_2$, $B_{1,1} \Leftrightarrow (P_{1,2} \vee P_{2,1})$:

1. $(B_{1,1} \Rightarrow (P_{1,2} \vee P_{2,1})) \wedge ((P_{1,2} \vee P_{2,1}) \Rightarrow B_{1,1})$
2. $(\neg B_{1,1} \vee P_{1,2} \vee P_{2,1}) \wedge (\neg(P_{1,2} \vee P_{2,1}) \vee B_{1,1})$
3. $(\neg B_{1,1} \vee P_{1,2} \vee P_{2,1}) \wedge ((\neg P_{1,2} \wedge \neg P_{2,1}) \vee B_{1,1})$
4. $(\neg B_{1,1} \vee P_{1,2} \vee P_{2,1}) \wedge (\neg P_{1,2} \vee B_{1,1}) \wedge (\neg P_{2,1} \vee B_{1,1})$

which is what the program printed. Step 4 can blow up: $(A_1 \wedge B_1) \vee \dots \vee (A_k \wedge B_k)$ has a CNF of
$2^k$ clauses. **Tseitin's transformation** (Grigori Tseitin, 1968) avoids this by introducing a new symbol for each
subformula: the result is not equivalent but **equisatisfiable** (satisfiable exactly when the original is), and only
linearly larger. Every practical SAT tool uses it, and it is how the Cook-Levin reduction ends in CNF
([the Algorithms book, 22.4](../algorithms/22-NP-Completeness.md#224-the-cook-levin-theorem)).

### The resolution rule

**Resolution** takes two clauses that contain a complementary pair of literals, $\ell$ in one and $\neg\ell$ in the
other, and produces the clause of all the other literals:

$$
\frac{\ell_1 \vee \dots \vee \ell_k \vee \ell \qquad m_1 \vee \dots \vee m_j \vee \neg\ell}{\ell_1 \vee \dots \vee \ell_k \vee m_1 \vee \dots \vee m_j}.
$$

The result is the **resolvent**; duplicate literals are merged (**factoring**). Resolving $\ell$ with $\neg\ell$ gives
the **empty clause**, written $()$ or $\square$, a disjunction of nothing, which is false in every model.

**Soundness of the rule.** In any model of both premises, $\ell$ is either true or false. If $\ell$ is true, $\neg\ell$ is
false, so for the second premise to hold some $m_i$ is true. If $\ell$ is false, some $\ell_i$ is true. Either way the
resolvent is true. $\square$

**Resolution refutation**: to show KB $\models \beta$, convert KB $\wedge \neg\beta$ to CNF, and repeatedly add
resolvents of pairs of clauses. If the empty clause appears, KB $\wedge \neg\beta$ is unsatisfiable, so KB $\models \beta$.
If no new clause can be added, it is not entailed.

**A proof by hand.** To show KB $\models \neg P_{1,2}$, add the clause $P_{1,2}$ (the negation of the goal).

| step | clause | from |
|---|---|---|
| 1 | $B_{1,1} \vee \neg P_{1,2}$ | part of $R_2$ in CNF |
| 2 | $P_{1,2}$ | negated goal |
| 3 | $B_{1,1}$ | resolve 1 and 2 on $P_{1,2}$ |
| 4 | $\neg B_{1,1}$ | $R_4$ |
| 5 | $()$ | resolve 3 and 4 on $B_{1,1}$ |

Two resolution steps. The program, which computes all resolvents level by level, needed 6 resolvents; to show that
$\neg P_{2,2}$ is **not** entailed it had to saturate: 127 resolvents until nothing new appeared.

### Completeness of resolution (sketch)

**Ground resolution theorem.** If a set $S$ of clauses is unsatisfiable, then the **resolution closure** $RC(S)$ (all
clauses derivable from $S$ by repeated resolution) contains the empty clause.

*Proof sketch.* Prove the contrapositive: if $RC(S)$ does not contain the empty clause, then $S$ is satisfiable. Order
the symbols $P_1, \dots, P_k$ and build a model one symbol at a time (tautologies, clauses containing both $P$ and
$\neg P$, are true in every model and can be ignored). For $i = 1, \dots, k$: set $P_i$ to false if some clause of
$RC(S)$ contains $\neg P_i$ and all its other literals are already false under the values of $P_1, \dots, P_{i-1}$
(that clause needs $\neg P_i$); otherwise set $P_i$ to true. Suppose some clause of $RC(S)$ ends up false, and let $i$
be the first step at which a clause $C$ of $RC(S)$ becomes false. Then $C$ contains $P_i$ or $\neg P_i$, and all its
other literals are false. If $C$ contained $\neg P_i$, it would be false because $P_i$ was set true; but $C$ is
exactly a clause that makes the rule set $P_i$ false. So $C$ contains $P_i$, and $P_i$ was set false because of some
clause $C'$ that contains $\neg P_i$ with all its other literals false. The resolvent of $C$ and $C'$ on $P_i$ is in
$RC(S)$ and uses only $P_1, \dots, P_{i-1}$, all of its literals false. If it is empty, that contradicts the
assumption that the empty clause is not in $RC(S)$; if not, it was already false at an earlier step, which contradicts
the choice of $i$. So no clause of $RC(S)$, and in particular none of $S$, is ever falsified: the model satisfies $S$. $\square$

The full proof is in Russell and Norvig (section 7.5) and in logic textbooks. Since there are only finitely many
clauses over $k$ symbols ($3^k$), the closure is finite, so resolution refutation always terminates: **resolution is
sound and refutation-complete** for propositional logic. It is not fast: there are unsatisfiable formulas, such as the
pigeonhole formulas of 8.5, whose shortest resolution refutations have exponential length (Armin Haken, 1985).

## 8.4 Horn clauses, forward and backward chaining

*Level: intermediate.*

Full resolution is complete but expensive. Many real knowledge bases use only rules of the form "if these things are
all true, then that is true". A **definite clause** is a clause with exactly one positive literal, such as
$\neg A \vee \neg B \vee C$, which is the same as $A \wedge B \Rightarrow C$. A **fact** is a definite clause with no
negative literals, such as $C$. A **Horn clause** has at most one positive literal; a clause with none, such as
$\neg A \vee \neg B$, is a **goal clause** (it says $A \wedge B$ is false). Horn clauses are named after the logician
Alfred Horn, who studied them in 1951.

Horn clauses are much easier than general clauses: entailment of a symbol from definite clauses can be decided in
time **linear** in the size of the KB.

### Forward chaining

**Forward chaining** starts from the known facts and fires every rule whose premises are all known, adding its
conclusion, until the query appears or nothing new can be added. To make it linear, keep for each rule a **count** of
its premises not yet known, and an **agenda** of symbols known but not yet processed.

```python
def forward_chaining(rules, facts, q):
    count = {rule: number of premises of rule}
    inferred = set()
    agenda = queue of facts
    while agenda:
        p = agenda.pop()
        if p == q: return True
        if p not in inferred:
            inferred.add(p)
            for each rule with p in its premises:
                count[rule] -= 1
                if count[rule] == 0:
                    agenda.push(conclusion of rule)
    return False
```

**Theorem.** For a KB of definite clauses, forward chaining is sound and complete for atomic queries, and runs in time
linear in the total size of the KB.

*Proof.* Soundness: every added symbol is the conclusion of a rule whose premises are all already derived, so it is
entailed (by repeated modus ponens). Completeness: when the algorithm stops with nothing on the agenda, let $m$ be the
model that makes every inferred symbol true and every other symbol false. Every definite clause is true in $m$: if its
premises were all true in $m$, they were all inferred, so its count reached 0 and its conclusion was inferred too.
So $m$ is a model of the KB. If $q$ was not inferred, $q$ is false in $m$, so the KB does not entail $q$. Hence every
entailed atomic query is inferred. Time: each symbol is processed once, and processing it decrements the count of each
rule in which it is a premise, once; the total work is the number of premise occurrences, which is the size of the KB.
$\square$

The same argument gives a linear-time test of satisfiability for any set of Horn clauses (William Dowling and Jean
Gallier, 1984): run forward chaining from the facts; the set is unsatisfiable exactly when all premises of some goal
clause get inferred.

### Backward chaining

**Backward chaining** works from the query: to prove $q$, either $q$ is a known fact, or find a rule 
$p_1 \wedge \dots \wedge p_k \Rightarrow q$ and prove each $p_i$ the same way. It is depth-first search in an AND-OR tree, exactly like
5.6: choosing a rule is an OR node, proving all its premises is an AND node. A goal already on the current path must
not be tried again (that would loop), and goals already proved or refuted are remembered. Backward chaining is
**goal-directed**: it touches only the rules relevant to the question, which in a large KB is often a tiny fraction,
while forward chaining derives everything it can. Logic programming (Prolog, [Chapter 9](09-First-Order-Logic.md))
is backward chaining.

```python
--8<-- "books/ai/ch08_horn.py"
```

```
forward chaining, query SampleTaken: True; symbols inferred in order: ['Sunny', 'BatteryOK', 'AtRock', 'ArmOK', 'SolarOK', 'PowerOK', 'CanDrill', 'SampleTaken']; premise counts updated: 8
forward chaining, query MissionDone: False; symbols inferred in order: ['Sunny', 'BatteryOK', 'AtRock', 'ArmOK', 'SolarOK', 'PowerOK', 'CanDrill', 'SampleTaken']; premise counts updated: 9

backward chaining, query SampleTaken: True; goals tried:
SampleTaken
  CanDrill
    PowerOK
      SolarOK
        Sunny
      BatteryOK
    AtRock
  ArmOK
backward chaining, query MissionDone: False; goals tried:
MissionDone
  SampleTaken
    CanDrill
      PowerOK
        SolarOK
          Sunny
        BatteryOK
      AtRock
    ArmOK
  CanSend
    PowerOK
    LinkUp
      CanSend
```

The rover's KB derives SampleTaken in both directions. Forward chaining derived SolarOK, PowerOK, CanDrill and
SampleTaken from the four facts and never needed the link. MissionDone is not entailed: it needs CanSend, which needs
LinkUp, and the only rule concluding LinkUp needs CanSend again. Backward chaining shows this as a loop on its path
(CanSend, LinkUp, CanSend) and gives up on that branch; forward chaining simply never fires the rules, because their
counts never reach zero. The circular rule $\text{CanSend} \Rightarrow \text{LinkUp}$ is true, but no amount of
reasoning can bootstrap from it: a fact (a received carrier signal, say) must be told.

## 8.5 DPLL from scratch; WalkSAT

*Level: intermediate.*

Back to general clauses. The **satisfiability problem** (SAT) asks whether a CNF formula has a satisfying model. By the
refutation theorem, entailment reduces to it; so do planning ([Chapter 10](10-Planning.md)), hardware and software
verification, scheduling, and every CSP of [Chapter 7](07-Constraint-Satisfaction.md). SAT was the first problem shown
NP-complete (Stephen Cook, 1971; Leonid Levin independently), and the Algorithms book proves this in
[Chapter 22](../algorithms/22-NP-Completeness.md).

### DPLL

Martin Davis and Hilary Putnam (1960) gave a procedure based on resolution; Davis, George Logemann and Donald Loveland
(1962) replaced its memory-hungry elimination step by backtracking. The result, **DPLL**, is backtracking search over
truth assignments (7.2) with three improvements, each of which shrinks the search without losing completeness:

1. **Early termination.** A clause is true as soon as one literal is true, and the formula is false as soon as one
   clause has all literals false; the search need not wait for a complete assignment. In the code, setting a literal
   true deletes the clauses it satisfies and removes its negation from the others; an empty clause means failure.
2. **Unit propagation.** A **unit clause** has one literal left: that literal must be made true. Setting it may create
   further unit clauses: a chain of forced assignments. This is forward checking for SAT, and it is where most of the
   inference happens. (On Horn clauses, unit propagation is exactly forward chaining.)
3. **Pure literals.** If a symbol appears only positively (or only negatively) in the remaining clauses, setting it to
   make those literals true cannot hurt: any solution can be changed to agree with it.

When nothing is forced, DPLL **branches**: choose an unassigned variable (here the most frequent one, a simple
version of MRV) and try true, then false.

**Correctness** follows from that of backtracking (7.2): unit propagation and pure literals only make assignments that
are forced (unit) or harmless (pure), so no solution is lost. The pure-literal claim needs a one-line proof: if $\ell$ is
pure and $m$ satisfies the remaining clauses, change $m$ to make $\ell$ true; clauses containing $\ell$ become true, and no
clause contains $\neg \ell$, so nothing becomes false.

```python
--8<-- "books/ai/ch08_dpll.py"
```

```
8-queens as SAT: 736 clauses over 64 variables; DPLL: {'decisions': 9, 'propagations': 95, 'conflicts': 3}
  queens at (row, column): [(0, 4), (1, 6), (2, 1), (3, 3), (4, 7), (5, 0), (6, 2), (7, 5)]  valid: True
  WalkSAT found a solution after 60 flips: True

pigeonhole: n + 1 pigeons, n holes (unsatisfiable); DPLL work grows exponentially
  holes 3:   22 clauses, satisfiable False, decisions     10, conflicts      6
  holes 4:   45 clauses, satisfiable False, decisions     46, conflicts     24
  holes 5:   81 clauses, satisfiable False, decisions    238, conflicts    120
  holes 6:  133 clauses, satisfiable False, decisions   1438, conflicts    720
  holes 7:  204 clauses, satisfiable False, decisions  10078, conflicts   5040
  holes 8:  297 clauses, satisfiable False, decisions  80638, conflicts  40320

KB and P12: satisfiable False  -> KB entails not P12: True
KB and P22: satisfiable True  -> KB entails not P22: False
```

- **8-queens as SAT** uses 64 variables $x_{r,c}$ ("a queen on row $r$, column $c$"), one "at least one queen" clause
  per column and a binary clause $\neg x \vee \neg y$ for every pair of attacking squares: 736 clauses. DPLL solves it
  with 9 decisions; 95 rounds of unit propagation do most of the work. WalkSAT (below) also finds a solution.
- **The pigeonhole principle.** $n + 1$ pigeons cannot sit in $n$ holes with at most one per hole. The CNF says each
  pigeon is in some hole and no two pigeons share one. It is unsatisfiable, obviously to us, but the number of
  conflicts DPLL needs to prove it is exactly $n!$ here (6, 24, 120, 720, 5040, 40 320), and the decisions grow at
  the same rate. Haken's 1985 theorem says no resolution proof can be short, and DPLL's search tree is a resolution
  proof in disguise, so no branching order could rescue it. Humans see the counting argument; resolution cannot
  count.
- **Entailment by SAT.** KB $\wedge P_{1,2}$ is unsatisfiable, so KB $\models \neg P_{1,2}$; KB $\wedge P_{2,2}$ is
  satisfiable, so "no pit in [2,2]" is not entailed. The same answers as the truth table, by search instead of
  enumeration.

### WalkSAT

Local search (Chapter 5) works for SAT too. Bart Selman, Hector Levesque and David Mitchell's GSAT (1992) flipped the
variable that most increased the number of satisfied clauses. **WalkSAT** (Selman, Henry Kautz and Bram Cohen, 1994) is
more careful: pick a random unsatisfied clause; with probability $p$, flip a random variable in it (a **random walk**
step); otherwise flip the variable in it that **breaks** the fewest currently satisfied clauses (a greedy step). The
random walk lets it escape local minima, and choosing within an unsatisfied clause guarantees that each flip fixes at
least that clause.

The program keeps, for each clause, the number of its true literals, so a flip updates only the clauses that contain
the flipped variable: a flip costs time proportional to the variable's occurrences, not to the formula.

WalkSAT is **incomplete**: it can find a model, but if none exists it runs until its flip limit and reports nothing. It
can never prove unsatisfiability, so it cannot prove entailment. On large satisfiable random formulas it is often much
faster than complete search, and on random 3-SAT the hardest instances, for both kinds of solver, lie near the
satisfiability threshold of about 4.27 clauses per variable, as measured in the Algorithms book's
[23.8](../algorithms/23-Approximation-and-Parameterized-Algorithms.md#238-heuristics-in-practice-local-search-sat-solvers-and-integer-programming-solvers),
which runs both on that problem.

## 8.6 CDCL: clause learning, watched literals; why modern SAT solvers handle millions of variables

*Level: advanced.*

DPLL backtracks **chronologically**: when a branch fails, it undoes the most recent decision, even if that decision had
nothing to do with the failure, and it forgets why the branch failed, so the same failure can happen again in another
part of the tree. **Conflict-driven clause learning** (CDCL), introduced in the GRASP solver of João Marques-Silva and
Karem Sakallah (1996) and made fast by the Chaff solver of Matthew Moskewicz and colleagues (2001), fixes both. It is the
algorithm inside nearly every competitive SAT solver today.

### Decision levels and the implication graph

CDCL is iterative, not recursive. It keeps a **trail**: the list of assigned literals in order. Each assignment has a
**decision level**: the number of decisions made up to and including the one it depends on. A literal is either a
**decision** (it starts a new level) or **implied** by unit propagation, and then it records its **reason**: the clause
that became unit. The reasons define the **implication graph**: an arrow from each false literal of the reason clause to
the implied literal. A **conflict** is a clause all of whose literals are false.

Consider this formula with eight variables:

$$
\begin{aligned}
&c_1: \neg x_1 \vee x_2 \qquad c_2: \neg x_1 \vee x_3 \qquad c_3: \neg x_2 \vee \neg x_3 \vee x_4\\
&c_4: \neg x_4 \vee \neg x_7 \vee x_5 \qquad c_5: \neg x_4 \vee x_6 \qquad c_6: \neg x_5 \vee \neg x_6
\end{aligned}
$$

Suppose the solver decides $x_7$ = true (level 1), then $x_8$ = true (level 2; $x_8$ appears in no clause), then
$x_1$ = true (level 3). Unit propagation at level 3: $c_1$ gives $x_2$, $c_2$ gives $x_3$, $c_3$ gives $x_4$, $c_4$ gives
$x_5$ (using $x_7$ from level 1), $c_5$ gives $x_6$, and now $c_6$ has both literals false: a conflict.

<figure class="mars-fig" markdown="0">
<svg viewBox="0 0 640 300" role="img" aria-label="The implication graph of the CDCL example. Decisions x7 at level 1, x8 at level 2, x1 at level 3. x1 implies x2 and x3, which imply x4. x4 and x7 imply x5. x4 implies x6. x5 and x6 together conflict. A dashed cut separates x4 and x7 from the rest; the learned clause is not x4 or not x7.">
<line x1="93.7" y1="134.2" x2="154.5" y2="106.6" stroke="currentColor" stroke-width="1.3"/>
<polygon points="154.5,106.6 148.0,114.0 144.7,106.7" fill="currentColor"/>
<line x1="93.7" y1="155.8" x2="154.5" y2="183.4" stroke="currentColor" stroke-width="1.3"/>
<polygon points="154.5,183.4 144.7,183.3 148.0,176.0" fill="currentColor"/>
<line x1="203.7" y1="105.8" x2="264.5" y2="133.4" stroke="currentColor" stroke-width="1.3"/>
<polygon points="264.5,133.4 254.7,133.3 258.0,126.0" fill="currentColor"/>
<line x1="203.7" y1="184.2" x2="264.5" y2="156.6" stroke="currentColor" stroke-width="1.3"/>
<polygon points="264.5,156.6 258.0,164.0 254.7,156.7" fill="currentColor"/>
<line x1="313.9" y1="155.1" x2="394.2" y2="189.1" stroke="currentColor" stroke-width="1.3"/>
<polygon points="394.2,189.1 384.4,189.3 387.5,181.9" fill="currentColor"/>
<line x1="95.9" y1="227.8" x2="392.1" y2="202.4" stroke="currentColor" stroke-width="1.3"/>
<polygon points="392.1,202.4 383.5,207.1 382.8,199.2" fill="currentColor"/>
<line x1="313.9" y1="134.9" x2="394.2" y2="100.9" stroke="currentColor" stroke-width="1.3"/>
<polygon points="394.2,100.9 387.5,108.1 384.4,100.7" fill="currentColor"/>
<line x1="444.2" y1="190.5" x2="533.9" y2="155.2" stroke="currentColor" stroke-width="1.3"/>
<polygon points="533.9,155.2 527.0,162.3 524.1,154.8" fill="currentColor"/>
<line x1="444.2" y1="99.5" x2="533.9" y2="134.8" stroke="currentColor" stroke-width="1.3"/>
<polygon points="533.9,134.8 524.1,135.2 527.0,127.7" fill="currentColor"/>
<circle cx="70" cy="230" r="25" style="fill:var(--md-default-bg-color)"/>
<circle cx="70" cy="230" r="25" fill="#7ccf9a" fill-opacity="0.6" stroke="currentColor" stroke-width="1.3"/>
<text x="70" y="235" font-size="12" text-anchor="middle" fill="currentColor" font-family="monospace">x7@1</text>
<circle cx="70" cy="60" r="25" style="fill:var(--md-default-bg-color)"/>
<circle cx="70" cy="60" r="25" fill="#7ccf9a" fill-opacity="0.6" stroke="currentColor" stroke-width="1.3"/>
<text x="70" y="65" font-size="12" text-anchor="middle" fill="currentColor" font-family="monospace">x8@2</text>
<circle cx="70" cy="145" r="25" style="fill:var(--md-default-bg-color)"/>
<circle cx="70" cy="145" r="25" fill="#7ccf9a" fill-opacity="0.6" stroke="currentColor" stroke-width="1.3"/>
<text x="70" y="150" font-size="12" text-anchor="middle" fill="currentColor" font-family="monospace">x1@3</text>
<circle cx="180" cy="95" r="25" style="fill:var(--md-default-bg-color)"/>
<circle cx="180" cy="95" r="25" fill="#9cc9ea" fill-opacity="0.6" stroke="currentColor" stroke-width="1.3"/>
<text x="180" y="100" font-size="12" text-anchor="middle" fill="currentColor" font-family="monospace">x2@3</text>
<circle cx="180" cy="195" r="25" style="fill:var(--md-default-bg-color)"/>
<circle cx="180" cy="195" r="25" fill="#9cc9ea" fill-opacity="0.6" stroke="currentColor" stroke-width="1.3"/>
<text x="180" y="200" font-size="12" text-anchor="middle" fill="currentColor" font-family="monospace">x3@3</text>
<circle cx="290" cy="145" r="25" style="fill:var(--md-default-bg-color)"/>
<circle cx="290" cy="145" r="25" fill="#9cc9ea" fill-opacity="0.6" stroke="currentColor" stroke-width="1.3"/>
<text x="290" y="150" font-size="12" text-anchor="middle" fill="currentColor" font-family="monospace">x4@3</text>
<circle cx="420" cy="200" r="25" style="fill:var(--md-default-bg-color)"/>
<circle cx="420" cy="200" r="25" fill="#9cc9ea" fill-opacity="0.6" stroke="currentColor" stroke-width="1.3"/>
<text x="420" y="205" font-size="12" text-anchor="middle" fill="currentColor" font-family="monospace">x5@3</text>
<circle cx="420" cy="90" r="25" style="fill:var(--md-default-bg-color)"/>
<circle cx="420" cy="90" r="25" fill="#9cc9ea" fill-opacity="0.6" stroke="currentColor" stroke-width="1.3"/>
<text x="420" y="95" font-size="12" text-anchor="middle" fill="currentColor" font-family="monospace">x6@3</text>
<rect x="526" y="127" width="68" height="36" rx="6" fill="#eea66f" fill-opacity="0.7" stroke="currentColor" stroke-width="1.3"/>
<text x="560" y="150" font-size="13" text-anchor="middle" fill="currentColor" font-weight="bold">conflict</text>
<path d="M 352 20 C 362 120 352 170 300 270" fill="none" stroke="#eea66f" stroke-width="2.5" stroke-dasharray="7 5"/>
<text x="340" y="290" font-size="12" text-anchor="start" fill="currentColor">cut: learned clause (¬x4 ∨ ¬x7)</text>
<text x="130" y="30" font-size="12" text-anchor="start" fill="currentColor">green: decisions; value@level</text>
</svg>
<figcaption>Figure 8.2. The implication graph when CDCL hits the conflict in the example of 8.6. Each node is an assignment with its decision level; arrows show which clause forced it. x4 is the first unique implication point: every path from the level-3 decision x1 to the conflict passes through it. Cutting just after x4 gives the learned clause (¬x4 ∨ ¬x7), whose literals are at levels 3 and 1, so the solver jumps back to level 1, skipping level 2 entirely.</figcaption>
</figure>

### Learning a clause: the first UIP

Any **cut** of the implication graph that separates the decisions from the conflict gives a clause that is entailed by
the formula: the assignments on the decision side of the cut, with arrows crossing it, together imply the conflict, so
at least one of them must be false. The cut just after the decisions gives $\neg x_1 \vee \neg x_7$ (the **decision
cut**). The cut that CDCL solvers use goes through the **first unique implication point** (first UIP): the
current-level node closest to the conflict through which every path from the current decision to the conflict passes.
Here that is $x_4$, so the learned clause is

$$
\neg x_4 \vee \neg x_7 .
$$

The program's `analyze` finds it by resolution: start from the conflict clause $c_6 = \neg x_5 \vee \neg x_6$; resolve
with the reason of the latest current-level literal on the trail, $c_5$ for $x_6$, to get $\neg x_4 \vee \neg x_5$; resolve
with the reason of $x_5$, $c_4$, to get $\neg x_4 \vee \neg x_7$. Now exactly one current-level literal ($\neg x_4$) is left:
stop. **The learned clause is a resolvent of clauses of the formula, so it is entailed by the formula, and adding it
loses no solutions.** That is the soundness of clause learning in one sentence, and it is also why CDCL is a
resolution prover: the learned clauses are the steps of a resolution refutation, and the final empty clause ends it.

### Backjumping

The learned clause has one literal at the current level (3) and the others at lower levels (here 1). Undo the trail
back to the **second-highest** level in the clause, level 1, not just to level 2. At level 1, with $x_7$ true, the
learned clause is unit and forces $\neg x_4$ at once. The decision $x_8$ at level 2 was irrelevant to the conflict, and
it is simply thrown away: this is **non-chronological backtracking**, or **backjumping**. The learned clause is
**asserting**: after the jump it immediately propagates, so the solver never repeats the same mistake. A 1-UIP clause
always has exactly one current-level literal, so it is always asserting.

### Two watched literals

Profiles of SAT solvers show that unit propagation takes most of the time, so it must be cheap. A clause can become unit
or false only when all but one of its literals are false. So it suffices to **watch two literals** per clause that are
not false: as long as both are non-false, the clause is neither unit nor conflicting, and nothing needs to be looked at.
When a watched literal becomes false, the solver looks for another non-false literal in the clause to watch instead;
only if there is none is the clause unit (the other watch is forced) or conflicting. Two properties make this fast:

- assigning a literal touches only the clauses watching its negation, not every clause containing it;
- **backtracking costs nothing**: unassigning literals cannot make a watched literal false, so the watches stay valid
  and need no update.

This scheme came from the Chaff solver. In the program, `propagate` keeps the false watch in position 1 of the clause
and the other in position 0.

### Heuristics that matter

- **VSIDS** (variable state independent decaying sum, also from Chaff): each variable has an activity score, bumped
  every time it appears in a conflict analysis; scores decay over time (in the code, the bump increment grows by a factor
  $1/0.95$ per conflict, which is equivalent). The solver decides the most active unassigned variable: it focuses on the
  variables involved in recent conflicts, the hard core of the problem.
- **Phase saving**: when a variable is unassigned by backjumping, remember its last value and reuse it the next time
  it is decided, so that work on independent subproblems is not lost.
- **Restarts**: every so often, undo all decisions but keep the learned clauses and the activities. With learned
  clauses and new activities the solver starts in a better place; restarts also counter the heavy-tailed run times of
  randomised search (Carla Gomes, Selman and Kautz, 1998). The program restarts after 100 conflicts, then at gaps
  growing by 1.5 times.
- **Clause deletion**: real solvers learn millions of clauses and must forget the less useful ones; the program
  keeps them all, which is fine at this size.

### Measured

```python
--8<-- "books/ai/ch08_cdcl.py"
```

```
random 3-SAT at 4.26 clauses per variable (3 formulas per size)
   n   result   DPLL decisions   CDCL decisions  conflicts  learned  longest backjump
  50   UNSAT               176               73         66       65                 4
  50   UNSAT               204              107         97       96                 3
  50   UNSAT               144               72         63       62                 7
  75   UNSAT               252              154        136      135                 4
  75   UNSAT               468              188        154      153                 3
  75   SAT                 510              294        244      244                 3
 100   UNSAT              1678              633        524      523                 7
 100   SAT                1494              366        275      275                 6
 100   SAT                 547              524        407      407                 6

pigeonhole (unsatisfiable): CDCL conflicts
  holes 4: unsatisfiable True, conflicts 28
  holes 5: unsatisfiable True, conflicts 145
  holes 6: unsatisfiable True, conflicts 824
  holes 7: unsatisfiable True, conflicts 4265

irrelevant variables plus a small unsatisfiable core
   k   DPLL decisions   CDCL decisions   CDCL conflicts   longest backjump
  10              542               42               28                  7
  20             4850               47               28                 12
  30            52942               51               28                 16
```

What the program shows, honestly:

- **On random 3-SAT at the threshold**, with 50 to 100 variables, CDCL needs fewer decisions than DPLL, typically by a
  factor of 1 to 4. Random formulas have no structure to exploit, so learning helps only moderately; at this size
  both are fast. Every model was checked, and both solvers agreed on every answer.
- **On the pigeonhole formulas** CDCL is also exponential (28, 145, 824, 4265 conflicts): it is a resolution prover, and
  Haken's lower bound applies to it too.
- **On a formula with a hidden unsatisfiable core** (a 5-pigeon, 4-hole core plus $k$ irrelevant variables in easily
  satisfied clauses, numbered first so that both solvers tend to decide them first), the difference is dramatic. DPLL's
  decisions grow by about a factor of 10 for every 10 irrelevant variables (542, 4850, 52 942): every time the core
  fails, it backtracks only to the most recent irrelevant decision and tries the core again. CDCL learns clauses about
  the core only, backjumps over the irrelevant decisions (by up to 16 levels in one jump), and needs 28 conflicts
  whatever $k$ is.

The last experiment is a caricature of real industrial formulas: a chip-verification formula may have millions of
variables, but the reason a particular property holds usually involves a small, tightly connected part of them. CDCL
finds that part, learns about it, and ignores the rest. That, plus watched literals making each propagation cheap, is
why modern solvers (MiniSat by Niklas Eén and Niklas Sörensson, 2003, and its many successors such as Glucose, CaDiCaL
and Kissat) handle many industrial instances with millions of variables and clauses. It is not a contradiction of
NP-completeness: there are small formulas (pigeonhole, and random formulas near the threshold with a few hundred
variables) that defeat all of them. SAT solving is fast on the formulas people actually need, for reasons that are
understood only in part; explaining it precisely is an active research area.

Solvers have also settled real mathematical questions. Marijn Heule, Oliver Kullmann and Victor Marek used a SAT solver
in 2016 to show that the numbers 1 to 7825 cannot be split into two parts with no part containing a Pythagorean triple
$a^2 + b^2 = c^2$, while 1 to 7824 can, producing a machine-checkable proof of about 200 terabytes.

**In practice.** Use an existing solver: PySAT gives Python access to MiniSat, Glucose, CaDiCaL and others; most
solvers read the DIMACS CNF format used by the programs here (integers for literals). Problems are often written in a
higher-level language and compiled to SAT, or solved by **SMT** solvers such as Z3 and cvc5, which extend CDCL with
arithmetic, arrays and other theories. The spacecraft software of [Chapter 10](10-Planning.md) used propositional models
too: the Livingstone diagnosis system of NASA's Remote Agent experiment on Deep Space 1 (1999) represented the
spacecraft's components in propositional logic and searched for the most likely failure that explained the sensor
readings.

### A short history thread

George Boole's algebra of logic (1847, 1854) turned reasoning into calculation; truth tables were set out in the early
1920s by Emil Post and by Ludwig Wittgenstein. Davis and Putnam's procedure (1960) and the DPLL version (1962) were among
the first theorem provers on computers; John Alan Robinson's 1965 resolution principle made resolution the basis of
automated reasoning ([Chapter 9](09-First-Order-Logic.md)). Cook's 1971 theorem made SAT the canonical hard problem, and
for two decades SAT solving was seen as hopeless in general. The 1990s changed that: local search (GSAT, WalkSAT) and
the observation of the phase transition, then GRASP's clause learning (1996), Chaff's watched literals and VSIDS (2001)
and MiniSat's clean design (2003). Annual SAT competitions since the early 2000s have driven steady improvement, and SAT
and SMT solvers are now standard tools in hardware and software verification.

## Check yourself

??? question "1. Use a truth table to show that (P ⇒ Q) ⇔ (¬Q ⇒ ¬P) is valid, and that P ⇒ Q does not entail Q ⇒ P."

    | P | Q | P ⇒ Q | ¬Q ⇒ ¬P | Q ⇒ P |
    |---|---|---|---|---|
    | F | F | T | T | T |
    | F | T | T | T | F |
    | T | F | F | F | T |
    | T | T | T | T | T |

    The columns for $P \Rightarrow Q$ and its **contrapositive** $\neg Q \Rightarrow \neg P$ are identical, so the
    biconditional is true in every row: valid. In row 2, $P \Rightarrow Q$ is true and its **converse** $Q \Rightarrow P$
    is false, so the entailment fails. (The program's `tt_entails` confirms both.)

??? question "2. Show by resolution that (P ∨ Q) ∧ (¬P ∨ R) entails Q ∨ R."

    Resolving $P \vee Q$ with $\neg P \vee R$ on $P$ gives $Q \vee R$ directly. As a refutation: add $\neg(Q \vee R)$,
    which in CNF is the two clauses $\neg Q$ and $\neg R$. From $Q \vee R$ and $\neg Q$ get $R$; with $\neg R$ get the
    empty clause. The rule used, "from $A \vee B$ and $\neg A \vee C$ infer $B \vee C$", is resolution itself.

??? question "3. Convert (A ⇔ B) ⇒ C to CNF by hand."

    Eliminate $\Rightarrow$: $\neg(A \Leftrightarrow B) \vee C$. Eliminate $\Leftrightarrow$ inside:
    $\neg((\neg A \vee B) \wedge (\neg B \vee A)) \vee C$. Push $\neg$ in: $((A \wedge \neg B) \vee (B \wedge \neg A)) \vee C$.
    Distribute: $(A \vee B \vee C) \wedge (A \vee \neg A \vee C) \wedge (\neg B \vee B \vee C) \wedge (\neg B \vee \neg A \vee C)$.
    The middle two are tautologies and can be dropped: $(A \vee B \vee C) \wedge (\neg A \vee \neg B \vee C)$. The program's
    `cnf` returns exactly these two clauses.

??? question "4. Prove by resolution that the wumpus KB entails P22 ∨ P31."

    Negate the goal: $\neg P_{2,2}$ and $\neg P_{3,1}$. From $R_3$ in CNF take $\neg B_{2,1} \vee P_{1,1} \vee P_{2,2} \vee P_{3,1}$.
    Resolve with $B_{2,1}$ ($R_5$): $P_{1,1} \vee P_{2,2} \vee P_{3,1}$. Resolve with $\neg P_{1,1}$ ($R_1$): $P_{2,2} \vee P_{3,1}$.
    Resolve with $\neg P_{2,2}$: $P_{3,1}$. Resolve with $\neg P_{3,1}$: the empty clause. Four steps.

??? question "5. Which of these are Horn clauses, and which are definite: ¬A ∨ ¬B ∨ C; A ∨ B; ¬A ∨ ¬B; D. Why is A ∨ B outside the fast fragment?"

    $\neg A \vee \neg B \vee C$ (one positive literal): definite, the rule $A \wedge B \Rightarrow C$. $\neg A \vee \neg B$
    (no positive literal): Horn, a goal clause. $D$: definite, a fact. $A \vee B$ has two positive literals: not Horn. It
    says "one of them, but I do not know which", and reasoning with such disjunctions needs case analysis, which is where
    the exponential cost of general SAT comes from. (Another tractable class is **2-SAT**, clauses of at most two literals,
    solvable in linear time with strongly connected components; see [SCC](../../graphs/scc.md).)

??? question "6. In the forward-chaining proof of completeness, why does the constructed model make every definite clause true?"

    A definite clause $p_1 \wedge \dots \wedge p_k \Rightarrow q$ is false in a model only if all $p_i$ are true and $q$ is
    false. In the constructed model, the true symbols are exactly the inferred ones. If all $p_i$ were inferred, each
    one, when processed, decremented this rule's count, so the count reached 0 and $q$ was put on the agenda and later
    inferred, so $q$ is true. Hence no clause is false. For a fact ($k = 0$), $q$ was on the initial agenda.

??? question "7. Write code: count the models of a CNF formula (#SAT) by DPLL-style splitting, and check it on the wumpus KB."

    ```python
    from itertools import product

    def count_models(clauses, variables):
        """#SAT by DPLL-style splitting: a variable that no clause mentions doubles the count."""
        if any(len(c) == 0 for c in clauses):
            return 0
        if not clauses:
            return 2 ** len(variables)
        v = abs(clauses[0][0])
        rest = [u for u in variables if u != v]
        total = 0
        for lit in (v, -v):
            reduced = [[l for l in c if l != -lit] for c in clauses if lit not in c]
            total += count_models(reduced, rest)
        return total

    # the wumpus KB in clause form (1 B11, 2 B21, 3 P11, 4 P12, 5 P21, 6 P22, 7 P31)
    kb = [[-1], [-3], [2], [2, -3], [1, -4], [1, -5], [2, -6], [2, -7], [-1, 4, 5], [-2, 3, 6, 7]]
    print(count_models(kb, list(range(1, 8))))
    brute = sum(all(any((l > 0) == x[abs(l) - 1] for l in c) for c in kb) for x in product((False, True), repeat=7))
    print(brute)
    ```

    Both print 3, the number of models found by the truth table in 8.2. Counting cannot stop at the first model, so
    #SAT is harder than SAT (it is #P-complete); model counting is the basis of exact probabilistic inference
    ([Chapter 12](12-Probabilistic-Reasoning.md)).

??? question "8. Why do watched literals need no work when the solver backtracks?"

    A watched literal is moved only when it becomes false. Backtracking only unassigns variables, which turns false or
    true literals into unassigned ones; it never makes a non-false literal false. So after backtracking, both watches of
    every clause are still non-false (or the clause is in the same state as when its watches were last valid), and the
    invariant "if a clause is unit or false, one of its watches is false" still holds. Counter-based schemes, by contrast,
    must update a counter in every clause containing each unassigned variable.

??? question "9. In the CDCL example of 8.6, what clause does the decision cut give, and why is the first-UIP clause better?"

    The decision cut separates the decisions $x_7, x_8, x_1$ from everything else; only $x_1$ and $x_7$ have arrows
    crossing it, so the clause is $\neg x_1 \vee \neg x_7$. Both clauses are entailed and both are asserting. The 1-UIP
    clause $\neg x_4 \vee \neg x_7$ is closer to the conflict: it rules out every way of reaching $x_4$ with $x_7$ true, not
    only through $x_1$ (if another decision later implies $x_4$, the decision clause would not stop it, the 1-UIP clause
    would). Experiments since the Chaff paper found first-UIP learning the most effective scheme in practice.

??? question "10. Explain why DPLL needs exactly n! conflicts on the pigeonhole formula in the program, at least in outline, and why no clever branching order can make it polynomial."

    Branching on the most frequent variables places pigeons one at a time; unit propagation then forbids the chosen hole
    to the other pigeons. Every way of placing the first $n$ pigeons into distinct holes leaves the last pigeon with no
    hole, a conflict, and the program's run visits essentially all $n!$ such placements (the counts 6, 24, ..., 40 320
    match $3!, \dots, 8!$). The general reason is Haken's theorem: every resolution refutation of the pigeonhole formula
    with $n + 1$ pigeons has size exponential in $n$, and the search tree of a DPLL run that proves unsatisfiability can be
    turned into a resolution refutation of about the same size. So any DPLL (and any CDCL) run is exponential, whatever
    the order. Stronger proof systems (with counting, or extended resolution) have short proofs.

??? question "11. A WalkSAT run on a formula stops after a million flips without finding a model. What can you conclude?"

    Nothing definite. The formula may be unsatisfiable, or satisfiable with models that are hard to reach by local
    moves. WalkSAT is incomplete: it can prove satisfiability (by exhibiting a model, which is checked in linear time) but
    never unsatisfiability. To prove that no model exists you need a complete method: DPLL, CDCL, or a resolution proof,
    which modern solvers can output (for example in the DRAT format) so that a small, independent program can check it.

??? question "12. Write the clauses saying that exactly one of x1, x2, x3 is true, and count them for n variables."

    "At least one": $x_1 \vee x_2 \vee x_3$. "At most one": for every pair, $\neg x_i \vee \neg x_j$: $\neg x_1 \vee \neg x_2$,
    $\neg x_1 \vee \neg x_3$, $\neg x_2 \vee \neg x_3$. For $n$ variables that is $1 + \binom{n}{2}$ clauses, quadratic. The
    8-queens encoding used the at-most-one part for every row, column and diagonal. Encodings with $O(n)$ extra variables
    and $O(n)$ clauses exist (for example the sequential counter of Carsten Sinz, 2005) and matter for large problems.

## What you learned

- A knowledge-based agent tells sentences to a knowledge base and asks what follows; the wumpus world needs exactly
  this kind of reasoning.
- Entailment means "true in every model of the KB"; it holds exactly when KB $\wedge \neg\beta$ is unsatisfiable, so SAT
  solvers are theorem provers. Truth tables decide it in $O(2^n)$.
- Every sentence has an equivalent CNF; resolution on clauses is sound and refutation-complete, but some formulas
  (pigeonhole) need exponentially long resolution proofs.
- Definite (Horn) clauses allow linear-time forward chaining and goal-directed backward chaining, both sound and
  complete for atomic queries.
- DPLL is backtracking with unit propagation and pure literals; WalkSAT is incomplete local search that is often fast on
  satisfiable formulas.
- CDCL learns a clause from every conflict (a resolvent, so sound), backjumps over irrelevant decisions, propagates with
  two watched literals, and focuses with VSIDS and restarts; on structured formulas that is the difference between
  exponential and trivial.

**Next:** [Chapter 9](09-First-Order-Logic.md), where symbols become objects, relations and quantifiers, so that one
sentence can say "every room next to a pit is breezy" for all rooms at once.

## Further reading

- S. Russell and P. Norvig, *Artificial Intelligence: A Modern Approach*, 4th ed., 2020: chapter 7 (logical agents).
- A. Biere, M. Heule, H. van Maaren and T. Walsh (eds.), *Handbook of Satisfiability*, 2nd ed., 2021; D. E. Knuth, *The
  Art of Computer Programming*, Vol. 4B (*Combinatorial Algorithms, Part 2*), 2022, which includes a long section on
  satisfiability.
- M. Davis and H. Putnam, "A computing procedure for quantification theory", *Journal of the ACM* 7, 1960; M. Davis, G.
  Logemann and D. Loveland, "A machine program for theorem-proving", *Communications of the ACM* 5, 1962.
- J. A. Robinson, "A machine-oriented logic based on the resolution principle", *Journal of the ACM* 12, 1965; A.
  Haken, "The intractability of resolution", *Theoretical Computer Science* 39, 1985.
- W. F. Dowling and J. H. Gallier, "Linear-time algorithms for testing the satisfiability of propositional Horn
  formulae", *Journal of Logic Programming* 1, 1984.
- B. Selman, H. Levesque and D. Mitchell, "A new method for solving hard satisfiability problems", AAAI 1992; B. Selman,
  H. Kautz and B. Cohen, "Noise strategies for improving local search", AAAI 1994.
- J. P. Marques-Silva and K. A. Sakallah, "GRASP: a search algorithm for propositional satisfiability", *IEEE
  Transactions on Computers* 48, 1999 (conference version 1996); M. W. Moskewicz, C. F. Madigan, Y. Zhao, L. Zhang and
  S. Malik, "Chaff: engineering an efficient SAT solver", DAC 2001; N. Eén and N. Sörensson, "An extensible SAT-solver",
  SAT 2003.
- C. P. Gomes, B. Selman and H. Kautz, "Boosting combinatorial search through randomization", AAAI 1998.
- M. J. H. Heule, O. Kullmann and V. W. Marek, "Solving and verifying the Boolean Pythagorean triples problem via
  cube-and-conquer", SAT 2016.
- On this site: the Algorithms book's [Chapter 22](../algorithms/22-NP-Completeness.md) (SAT, Cook-Levin, reductions)
  and [23.8](../algorithms/23-Approximation-and-Parameterized-Algorithms.md#238-heuristics-in-practice-local-search-sat-solvers-and-integer-programming-solvers)
  (DPLL and WalkSAT on random 3-SAT); [Chapter 7](07-Constraint-Satisfaction.md) of this book (CSPs, of which SAT is a
  special case); and the [Logic](https://math.akadian.ca/books/logic/) book on math.akadian.ca.
