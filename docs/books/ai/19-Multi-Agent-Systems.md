# 19. Many agents: game theory and cooperation

*Until now the agent was alone, or it faced a single opponent who wanted exactly the opposite (Chapter 6). Real
agents share the world with many others: traders in a market, cars at a crossing, bidders in an auction, voters, other
learning programs. Each one has its own goals, which may clash with ours, agree with ours, or both. This chapter answers
the question: what does it mean to act well when the outcome depends on what everybody else does, and how do we design
the rules so that agents acting for themselves still produce a good result? You will compute Nash equilibria, pure and
mixed, run a tournament of the repeated prisoner's dilemma, share the gains of cooperation with the Shapley value,
prove that the second-price auction makes honesty the best policy, meet Arrow's theorem on voting, and watch learning
agents succeed and fail at learning together.*

!!! abstract "In this chapter"
    **You will learn:**

    - games in normal form, dominant strategies, iterated elimination, and Nash equilibrium, pure and mixed, with the
      indifference principle proved and every equilibrium of small games computed exactly
    - why the prisoner's dilemma is a dilemma, how repetition changes it (backward induction, grim trigger, the folk
      theorem), and what Axelrod's tournaments found
    - cooperative games, the core, and the Shapley value: its four axioms, its formula, and a proof that the axioms
      determine it
    - mechanism design: why the second-price (Vickrey) auction is truthful, the first-price equilibrium derived,
      revenue equivalence checked by simulation, and the VCG mechanism
    - social choice: four voting rules that elect four different winners from the same ballots, Condorcet cycles, and
      Arrow's and Gibbard and Satterthwaite's theorems stated
    - learning among learners: regret matching and why it finds equilibria in zero-sum games, cycling, and
      miscoordination between independent learners

    **You need:** [Chapter 2](02-Intelligent-Agents.md) (agents and environments), [Chapter 6](06-Games-and-Adversarial-Search.md)
    (zero-sum games and minimax), [Chapter 14](14-Making-Decisions.md) (expected utility) and
    [Chapter 15](15-Reinforcement-Learning.md) (bandits and Q-learning, for 19.6). Linear equations and probability:
    [Linear algebra](https://math.akadian.ca/books/linear-algebra/) and [Probability](https://math.akadian.ca/books/probability/).

    **Levels:** 19.1 and 19.2 are beginner to intermediate (the existence proof in 19.1 is advanced); 19.3 and 19.4 are
    intermediate (the uniqueness proof in 19.3 and VCG in 19.4 are advanced); 19.5 is intermediate; 19.6 is advanced.

## 19.1 Games in normal form; dominant strategies; Nash equilibrium

Two suspects are held in separate rooms. Each may stay silent (cooperate with the other) or confess (defect). If both
stay silent each gets a light sentence; if both confess, a medium one; if one confesses and the other stays silent,
the confessor goes free and the silent one gets the heaviest sentence. Neither can see what the other does. What
should a rational suspect do? This little story, the **prisoner's dilemma**, was set up as an experiment by Merrill
Flood and Melvin Dresher at the RAND Corporation in 1950, and the story and name were given to it by Albert Tucker
soon after. It is the most studied game there is, because it captures a hard truth: individually sensible choices can
add up to a result that everybody dislikes.

### Normal form

A game in **normal form** (also called strategic form) has three parts:

- a set of **players** $1, \dots, n$;
- for each player $i$, a set $S_i$ of **strategies** (here: actions chosen once, all at the same time);
- for each player $i$, a **payoff function** $u_i(s_1, \dots, s_n)$ giving the utility (Chapter 14) that player $i$
  receives when the players choose the **strategy profile** $s = (s_1, \dots, s_n)$.

With two players the whole game fits in a table, the **payoff matrix**: rows are player 1's strategies, columns
player 2's, and each cell holds the pair $(u_1, u_2)$. We write $s_{-i}$ for the strategies of everyone except $i$, so
$u_i(s_i', s_{-i})$ means "what $i$ gets by switching to $s_i'$ while the others stay put".

For the prisoner's dilemma we use the numbers from Robert Axelrod's tournaments (19.2), as rewards rather than years
in prison: both cooperate, each gets $R = 3$ (the **reward**); both defect, each gets $P = 1$ (the **punishment**); a
lone defector gets $T = 5$ (the **temptation**) and the lone cooperator $S = 0$ (the **sucker's payoff**). Any numbers
with $T > R > P > S$ make the same dilemma.

|       | C      | D      |
|-------|--------|--------|
| **C** | (3, 3) | (0, 5) |
| **D** | (5, 0) | (1, 1) |

### Dominant strategies

Look at the game from the row player's side. If the column player cooperates, defecting pays 5 instead of 3. If the
column player defects, defecting pays 1 instead of 0. Whatever the other does, D is better. A strategy $s_i$ **strictly
dominates** $s_i'$ when

$$
u_i(s_i, s_{-i}) > u_i(s_i', s_{-i}) \quad \text{for every } s_{-i}.
$$

A strategy that strictly dominates every other one is a **dominant strategy**. A rational player never plays a
strictly dominated strategy: whatever she believes about the others, switching to the dominating one does better. In
the prisoner's dilemma D is dominant for both players, so both defect and each gets 1, although both would prefer
(C, C) with 3 each. The outcome (D, D) is **Pareto dominated**: another outcome is better for somebody and worse for
nobody. That gap between individual and collective rationality is the dilemma.

Most games have no dominant strategy, but we can still remove strategies that are strictly dominated, then look again:
once a row is gone, a column may become dominated. This is **iterated elimination of strictly dominated strategies**.
It needs more than rationality: it needs each player to know that the others are rational, that they know she knows,
and so on (**common knowledge of rationality**). The result does not depend on the order of elimination for strict
dominance (a fact that fails for weak dominance, where a strategy is only "never worse").

### Nash equilibrium

In the **battle of the sexes** two friends want to spend the evening together but one prefers the opera (O), the other
football (F):

|       | O      | F      |
|-------|--------|--------|
| **O** | (2, 1) | (0, 0) |
| **F** | (0, 0) | (1, 2) |

No strategy dominates. What predicts the outcome? John Nash (1950) proposed the answer now named after him. A profile
$s^\ast$ is a **Nash equilibrium** if no player can gain by changing her own strategy alone:

$$
u_i(s_i^\ast, s_{-i}^\ast) \ge u_i(s_i, s_{-i}^\ast) \quad \text{for every player } i \text{ and every } s_i \in S_i.
$$

In other words, every player's strategy is a **best response** to the others'. An equilibrium is a stable point: if
everyone expects it, nobody wants to move. It is not a promise of a good outcome ((D, D) in the prisoner's dilemma is
the only equilibrium) and not always unique: in the battle of the sexes both (O, O) and (F, F) are equilibria. The
figure shows how to find **pure** equilibria (each player picks one strategy for sure) by hand: mark each player's
best responses; a cell where both are marked is an equilibrium.

<figure class="mars-fig" markdown="0">
<svg viewBox="0 0 640 300" role="img" aria-label="Two payoff matrices with best-response arrows. In the prisoner's dilemma every arrow points towards defect, ending in the cell D,D. In matching pennies the arrows go round in a cycle and no cell is a resting point.">
<text x="160" y="24" font-size="14" text-anchor="middle" fill="currentColor">Prisoner's dilemma</text>
<text x="115" y="58" font-size="13" text-anchor="middle" fill="currentColor">C</text>
<text x="225" y="58" font-size="13" text-anchor="middle" fill="currentColor">D</text>
<text x="40" y="115" font-size="13" text-anchor="middle" fill="currentColor">C</text>
<text x="40" y="225" font-size="13" text-anchor="middle" fill="currentColor">D</text>
<rect x="60" y="70" width="110" height="90" fill="none" stroke="currentColor" stroke-width="1.2"/>
<rect x="170" y="70" width="110" height="90" fill="none" stroke="currentColor" stroke-width="1.2"/>
<rect x="60" y="160" width="110" height="90" fill="none" stroke="currentColor" stroke-width="1.2"/>
<rect x="170" y="160" width="110" height="90" fill="#7ccf9a" fill-opacity="0.45" stroke="currentColor" stroke-width="1.2"/>
<text x="115" y="120" font-size="14" text-anchor="middle" fill="currentColor">3, 3</text>
<text x="225" y="120" font-size="14" text-anchor="middle" fill="currentColor">0, 5</text>
<text x="115" y="210" font-size="14" text-anchor="middle" fill="currentColor">5, 0</text>
<text x="225" y="210" font-size="14" text-anchor="middle" fill="currentColor">1, 1</text>
<line x1="115" y1="132" x2="115" y2="186" stroke="#eea66f" stroke-width="2.5"/>
<polygon points="115,194 109,182 121,182" fill="#eea66f"/>
<line x1="225" y1="132" x2="225" y2="186" stroke="#eea66f" stroke-width="2.5"/>
<polygon points="225,194 219,182 231,182" fill="#eea66f"/>
<line x1="140" y1="100" x2="192" y2="100" stroke="#9cc9ea" stroke-width="2.5"/>
<polygon points="200,100 188,94 188,106" fill="#9cc9ea"/>
<line x1="140" y1="232" x2="192" y2="232" stroke="#9cc9ea" stroke-width="2.5"/>
<polygon points="200,232 188,226 188,238" fill="#9cc9ea"/>
<text x="170" y="280" font-size="12" text-anchor="middle" fill="currentColor">all arrows end at (D, D): the only equilibrium</text>
<text x="480" y="24" font-size="14" text-anchor="middle" fill="currentColor">Matching pennies</text>
<text x="435" y="58" font-size="13" text-anchor="middle" fill="currentColor">H</text>
<text x="545" y="58" font-size="13" text-anchor="middle" fill="currentColor">T</text>
<text x="360" y="115" font-size="13" text-anchor="middle" fill="currentColor">H</text>
<text x="360" y="225" font-size="13" text-anchor="middle" fill="currentColor">T</text>
<rect x="380" y="70" width="110" height="90" fill="none" stroke="currentColor" stroke-width="1.2"/>
<rect x="490" y="70" width="110" height="90" fill="none" stroke="currentColor" stroke-width="1.2"/>
<rect x="380" y="160" width="110" height="90" fill="none" stroke="currentColor" stroke-width="1.2"/>
<rect x="490" y="160" width="110" height="90" fill="none" stroke="currentColor" stroke-width="1.2"/>
<text x="435" y="120" font-size="14" text-anchor="middle" fill="currentColor">1, −1</text>
<text x="545" y="120" font-size="14" text-anchor="middle" fill="currentColor">−1, 1</text>
<text x="435" y="210" font-size="14" text-anchor="middle" fill="currentColor">−1, 1</text>
<text x="545" y="210" font-size="14" text-anchor="middle" fill="currentColor">1, −1</text>
<line x1="460" y1="100" x2="512" y2="100" stroke="#9cc9ea" stroke-width="2.5"/>
<polygon points="520,100 508,94 508,106" fill="#9cc9ea"/>
<line x1="545" y1="132" x2="545" y2="186" stroke="#eea66f" stroke-width="2.5"/>
<polygon points="545,194 539,182 551,182" fill="#eea66f"/>
<line x1="520" y1="232" x2="468" y2="232" stroke="#9cc9ea" stroke-width="2.5"/>
<polygon points="460,232 472,226 472,238" fill="#9cc9ea"/>
<line x1="435" y1="186" x2="435" y2="132" stroke="#eea66f" stroke-width="2.5"/>
<polygon points="435,124 429,136 441,136" fill="#eea66f"/>
<text x="490" y="280" font-size="12" text-anchor="middle" fill="currentColor">the arrows cycle: no pure equilibrium</text>
</svg>
<figcaption>Figure 19.1. Best-response arrows. An orange arrow shows where the row player would move within a column, a blue arrow where the column player would move within a row. A pure Nash equilibrium is a cell that no arrow leaves. In the prisoner's dilemma that is (D, D); in matching pennies (the row player wins on a match, the column player on a mismatch) the arrows chase each other round and no cell is stable.</figcaption>
</figure>

### Mixed strategies and the indifference principle

**Matching pennies** has no pure equilibrium: whatever cell we are in, one player wants to move. The way out is to
randomise. A **mixed strategy** for player $i$ is a probability distribution $x_i$ over $S_i$; the payoff of a mixed
profile is the expected payoff when everyone draws independently. For two players with payoff matrices $A$ (row player)
and $B$ (column player), row mix $x$ and column mix $y$, the expected payoffs are $x^{\mathsf T} A y$ and
$x^{\mathsf T} B y$. A mixed profile is a Nash equilibrium if no player can raise her expected payoff by changing her
mix. The **support** of a mix is the set of pure strategies it plays with positive probability.

**Lemma (indifference principle).** A mixed profile is a Nash equilibrium exactly when, for every player $i$, every
pure strategy in the support of $x_i$ earns the same expected payoff against $x_{-i}$, and no pure strategy outside the
support earns more.

*Proof.* Write $v_s$ for the expected payoff of pure strategy $s$ against the others' mixes, so that $i$'s payoff is
the average $\sum_s x_i(s) v_s$. An average never exceeds its largest term, and equals it exactly when all the weight
sits on terms equal to the largest. If some $s$ in the support had $v_s < \max_t v_t$, moving its weight to a best
pure strategy would raise the average, so the profile would not be an equilibrium. Conversely, if every supported $s$
has $v_s = \max_t v_t$, the average already equals the maximum, and since any mix's payoff is an average of the $v_t$,
no mix does better. $\square$

The lemma turns a search for equilibria into linear equations. **Notice the twist: it is the other player's
probabilities that make me indifferent.** In the battle of the sexes, let the column player choose O with probability
$q$. The row player's payoffs are $2q$ for O and $1 - q$ for F. For the row player to be willing to mix, these must be
equal: $2q = 1 - q$, so $q = 1/3$. Likewise if the row player picks O with probability $p$, the column player gets $p$
from O and $2(1 - p)$ from F, equal when $p = 2/3$. So there is a third equilibrium: the row player goes to the opera
with probability $2/3$, the column player with probability $1/3$, and each expects
$2 \cdot \tfrac{1}{3} = \tfrac{2}{3}$, worse for both than either pure equilibrium. The reason is that they miss
each other with probability $\tfrac{2}{3}\cdot\tfrac{2}{3} + \tfrac{1}{3}\cdot\tfrac{1}{3} = \tfrac{5}{9}$.

<figure class="mars-fig" markdown="0">
<svg viewBox="0 0 470 340" role="img" aria-label="The unit square of mixed strategies for the battle of the sexes. The row player's best-response curve and the column player's best-response curve cross at three points: (0,0), (1,1) and (2/3, 1/3).">
<line x1="80" y1="280" x2="400" y2="280" stroke="currentColor" stroke-width="1.2"/>
<line x1="80" y1="280" x2="80" y2="25" stroke="currentColor" stroke-width="1.2"/>
<line x1="380" y1="280" x2="380" y2="40" stroke="currentColor" stroke-width="0.6" stroke-dasharray="3 3"/>
<line x1="80" y1="40" x2="380" y2="40" stroke="currentColor" stroke-width="0.6" stroke-dasharray="3 3"/>
<text x="80" y="298" font-size="12" text-anchor="middle" fill="currentColor">0</text>
<text x="280" y="298" font-size="12" text-anchor="middle" fill="currentColor">2/3</text>
<text x="380" y="298" font-size="12" text-anchor="middle" fill="currentColor">1</text>
<text x="240" y="322" font-size="13" text-anchor="middle" fill="currentColor">p = probability the row player picks O</text>
<text x="68" y="284" font-size="12" text-anchor="end" fill="currentColor">0</text>
<text x="68" y="204" font-size="12" text-anchor="end" fill="currentColor">1/3</text>
<text x="68" y="44" font-size="12" text-anchor="end" fill="currentColor">1</text>
<text x="22" y="160" font-size="13" text-anchor="middle" fill="currentColor" transform="rotate(-90 22 160)">q = column picks O</text>
<polyline points="80,280 80,200 380,200 380,40" fill="none" stroke="#eea66f" stroke-width="4" stroke-opacity="0.85"/>
<polyline points="80,280 280,280 280,40 380,40" fill="none" stroke="#9cc9ea" stroke-width="4" stroke-opacity="0.95" stroke-dasharray="9 4"/>
<circle cx="80" cy="280" r="7" fill="#7ccf9a" stroke="currentColor" stroke-width="1.2"/>
<circle cx="380" cy="40" r="7" fill="#7ccf9a" stroke="currentColor" stroke-width="1.2"/>
<circle cx="280" cy="200" r="7" fill="#7ccf9a" stroke="currentColor" stroke-width="1.2"/>
<text x="100" y="266" font-size="12" fill="currentColor">(F, F)</text>
<text x="330" y="62" font-size="12" fill="currentColor">(O, O)</text>
<text x="270" y="222" font-size="12" text-anchor="end" fill="currentColor">mixed (2/3, 1/3)</text>
<rect x="96" y="70" width="14" height="6" fill="#eea66f"/>
<text x="114" y="77" font-size="11" fill="currentColor">row's best response to q</text>
<rect x="96" y="92" width="14" height="6" fill="#9cc9ea"/>
<text x="114" y="99" font-size="11" fill="currentColor">column's best response to p</text>
</svg>
<figcaption>Figure 19.2. Best responses in the battle of the sexes. The row player prefers F when q &lt; 1/3, O when q &gt; 1/3 and is indifferent at q = 1/3 (orange); the column player prefers F when p &lt; 2/3 and O when p &gt; 2/3 (blue, dashed). The equilibria are the points on both curves: the two pure ones in the corners and the mixed one at (2/3, 1/3).</figcaption>
</figure>

### Nash's theorem

**Theorem (Nash 1950).** Every game with finitely many players and finitely many pure strategies has at least one
Nash equilibrium in mixed strategies.

*Proof sketch.* *Level: advanced.* The set of mixed profiles is a product of simplices, a compact convex set. Nash's
second proof (1951) defines a continuous map $f$ from this set to itself: for each player and each pure strategy $s$,
let $g_s = \max(0, v_s - u_i(x))$ be how much $s$ would beat the current mix, and set the new probability of $s$ to
$(x_i(s) + g_s) / (1 + \sum_t g_t)$. Brouwer's fixed point theorem says every continuous map of a compact convex set to
itself has a fixed point. At a fixed point, one shows that all the gains $g_s$ are zero (if some were positive, the
weight of a supported strategy with below-average payoff would have to shrink, contradicting the fixed point), which
is exactly the equilibrium condition. Brouwer's theorem itself is proved in topology books; the full argument is in
Nash's paper and in Osborne and Rubinstein. $\square$

The proof is not constructive: it says an equilibrium exists without saying how to find one. Finding one is genuinely
hard. Daskalakis, Goldberg and Papadimitriou (2006) showed that computing a Nash equilibrium is complete for the
complexity class PPAD, and Chen and Deng (2006) extended this to two players, so no polynomial-time algorithm is known
and most researchers believe none exists. For small games we can afford to search.

### Computing equilibria: support enumeration

The lemma gives an algorithm for two-player games. Guess the supports $I$ (rows) and $J$ (columns). The column mix $y$
on $J$ must make all rows in $I$ equally good, with common value $u$, and must sum to 1:

$$
\sum_{j \in J} A_{ij} y_j = u \;\; (i \in I), \qquad \sum_{j \in J} y_j = 1,
$$

and symmetrically for $x$ with $B$. In a **nondegenerate** game (the usual case: no pure strategy has two or more best
responses with the same payoff, roughly) the supports in an equilibrium have equal size, so we try $|I| = |J| = k$ for
$k = 1, 2, \dots$, solve both systems, and keep the solution if all probabilities are non-negative and no pure strategy
outside the support pays more than $u$ (or $v$). With $m$ and $n$ strategies there are at most about $\binom{m+n}{m}$
support pairs, exponential, but trivial for 2 or 3 strategies. The program solves the equations exactly with fractions,
and also runs iterated elimination and **fictitious play** (Brown 1951): each player repeatedly plays a best response
to the observed frequencies of the other's past play.

```python
--8<-- "books/ai/ch19_nash.py"
```

```

Prisoner's dilemma (C = cooperate, D = defect)
   C        ( 3, 3)  ( 0, 5)
   D        ( 5, 0)  ( 1, 1)
   pure equilibria: [('D', 'D')]
   equilibrium  row (0, 1)             column (0, 1)             payoffs 1, 1
   iterated elimination:
   row strategy 'C' is strictly dominated: removed
   column strategy 'C' is strictly dominated: removed
   survivors: (['D'], ['D'])

Matching pennies (zero-sum)
   Heads    ( 1,-1)  (-1, 1)
   Tails    (-1, 1)  ( 1,-1)
   pure equilibria: []
   equilibrium  row (1/2, 1/2)         column (1/2, 1/2)         payoffs 0, 0

Battle of the sexes (O = opera, F = football)
   O        ( 2, 1)  ( 0, 0)
   F        ( 0, 0)  ( 1, 2)
   pure equilibria: [('O', 'O'), ('F', 'F')]
   equilibrium  row (1, 0)             column (1, 0)             payoffs 2, 1
   equilibrium  row (0, 1)             column (0, 1)             payoffs 1, 2
   equilibrium  row (2/3, 1/3)         column (1/3, 2/3)         payoffs 2/3, 2/3

Rock-paper-scissors (zero-sum)
   Rock     ( 0, 0)  (-1, 1)  ( 1,-1)
   Paper    ( 1,-1)  ( 0, 0)  (-1, 1)
   Scissors (-1, 1)  ( 1,-1)  ( 0, 0)
   pure equilibria: []
   equilibrium  row (1/3, 1/3, 1/3)    column (1/3, 1/3, 1/3)    payoffs 0, 0

A 3x3 game
   Top      ( 4, 3)  ( 3, 1)  ( 2, 2)
   Middle   ( 2, 2)  ( 1, 2)  ( 0, 3)
   Bottom   ( 3, 0)  ( 4, 3)  ( 1, 1)
   pure equilibria: [('Top', 'L'), ('Bottom', 'C')]
   equilibrium  row (1, 0, 0)          column (1, 0, 0)          payoffs 4, 3
   equilibrium  row (0, 0, 1)          column (0, 1, 0)          payoffs 4, 3
   equilibrium  row (3/5, 0, 2/5)      column (1/2, 1/2, 0)      payoffs 7/2, 9/5
   iterated elimination:
   row strategy 'Middle' is strictly dominated: removed
   survivors: (['Top', 'Bottom'], ['L', 'C', 'R'])

Fictitious play on rock-paper-scissors, starting from (Rock, Rock):
   t=    10  row frequencies [0.273 0.273 0.455]   duality gap 0.3636
   t=   100  row frequencies [0.327 0.396 0.277]   duality gap 0.1386
   t=  1000  row frequencies [0.327 0.33  0.344]   duality gap 0.0280
   t= 10000  row frequencies [0.335 0.335 0.331]   duality gap 0.0080
   t=100000  row frequencies [0.333 0.333 0.334]   duality gap 0.0023
```

What the output shows:

- The prisoner's dilemma has exactly one equilibrium, (D, D), and elimination alone finds it.
- Matching pennies and rock-paper-scissors have only a mixed equilibrium: uniform play. Each expected payoff is 0.
- The battle of the sexes has three equilibria, the two pure ones and the mixed one computed above, with payoffs
  $2/3$ each.
- In the 3×3 game, Middle is strictly dominated by Top (4 > 2, 3 > 1, 2 > 0) and disappears, but elimination stops
  there; support enumeration finds two pure equilibria and one mixed. Count them: 1, 1, 3, 1, 3. Wilson (1971)
  proved that a nondegenerate game has an **odd** number of equilibria, which is a handy check.
- Fictitious play's frequencies approach $(1/3, 1/3, 1/3)$, and the **duality gap** (how much the better of the two
  players could gain by best-responding to the other's frequencies) shrinks towards 0, roughly like $1/\sqrt{t}$.

Here is the start of fictitious play, traced by hand. Each player best-responds to the other's counts so far; both
start with one Rock, and ties go to the first strategy in the order Rock, Paper, Scissors. Because the game and the
start are symmetric, both players do the same thing.

| step | counts of R, P, S so far | payoffs of R, P, S against them | best response |
|------|--------------------------|----------------------------------|---------------|
| 1 | 1, 0, 0 | 0, 1, −1 | Paper |
| 2 | 1, 1, 0 | −1/2, 1/2, 0 | Paper |
| 3 | 1, 2, 0 | −2/3, 1/3, 1/3 | Paper (tie) |
| 4 | 1, 3, 0 | −3/4, 1/4, 1/2 | Scissors |
| 5 | 1, 3, 1 | −2/5, 0, 2/5 | Scissors |
| 6 | 1, 3, 2 | −1/6, −1/6, 1/3 | Scissors |
| 7 | 1, 3, 3 | 0, −2/7, 2/7 | Scissors |
| 8 | 1, 3, 4 | 1/8, −3/8, 1/4 | Scissors |

The play goes round the cycle in longer and longer runs (Paper, then Scissors, then Rock...), but the frequencies
settle down. Julia Robinson (1951) proved that in every two-player zero-sum game fictitious play
converges: the payoffs approach the value of the game and every limit point of the frequencies is an equilibrium. In general games they need not: Shapley (1964) gave a 3×3 example where they cycle for ever.

### Zero-sum games and the minimax theorem

In a **zero-sum** game $B = -A$. Chapter 6 used the minimax value for games with moves in turn. With simultaneous
moves and mixed strategies, von Neumann (1928) proved

$$
\max_x \min_y x^{\mathsf T} A y = \min_y \max_x x^{\mathsf T} A y,
$$

so the row player can guarantee the same amount (the **value** of the game) that the column player can hold her to,
and the strategies achieving it form exactly the Nash equilibria. For rock-paper-scissors the value is 0. Each side of
the equation is a **linear program** (a linear objective maximised subject to linear inequalities), and the two
programs are each other's duals, so the minimax theorem is a case of linear-programming duality; zero-sum games are
therefore solvable in polynomial time, unlike general games. The duality gap printed above is
$\max_i (A\bar y)_i - \min_j (\bar x^{\mathsf T} A)_j$, which is zero exactly at an equilibrium.

## 19.2 Prisoner's dilemma and repeated games

People do cooperate, every day, in situations shaped like the prisoner's dilemma: they keep promises to business
partners, they share. One reason is that they meet again. What changes when the same two players play many times?

### Finitely many rounds: backward induction

Suppose the game is played exactly $N$ times and both know $N$. **Claim:** in every Nash equilibrium both defect in
every round (in every subgame perfect equilibrium; see below).

*Proof by backward induction.* In round $N$ nothing follows, so the round is a one-shot prisoner's dilemma and D is
dominant. Suppose we have shown that both defect in rounds $k+1, \dots, N$ whatever happened earlier. Then what a
player does in round $k$ cannot change what happens later, so round $k$ is also a one-shot game, and D is dominant.
By induction both defect in every round. $\square$

The argument needs the strategies to be credible at every point of the game, including points that are never
reached. An equilibrium with that property (a Nash equilibrium in every **subgame**, the game that starts at any
history) is called **subgame perfect** (Selten 1965). The backward-induction argument proves that always-defect is the
unique subgame perfect equilibrium. Experiments with people show much more cooperation than this; the conclusion
depends on everyone knowing the last round and reasoning all the way back.

### Infinitely or indefinitely many rounds

Now let the game continue after each round with probability $\delta$ (or let the players discount future payoffs by a
factor $\delta$ per round, which is the same thing mathematically). A payoff stream $r_0, r_1, \dots$ is worth
$\sum_t \delta^t r_t$. Consider **grim trigger**: cooperate until the other defects once, then defect for ever.

If both play grim trigger, each gets $R$ every round: $R / (1 - \delta)$. A player who defects now gets $T$ once, then
$P$ for ever after (the other punishes, and the best answer to permanent defection is to defect too):
$T + \delta P / (1 - \delta)$. Defecting does not pay when

$$
\frac{R}{1-\delta} \ge T + \frac{\delta P}{1-\delta}
\iff R \ge (1-\delta)T + \delta P
\iff \delta \ge \frac{T - R}{T - P}.
$$

With $T = 5, R = 3, P = 1$ that is $\delta \ge 1/2$: if the next round comes with probability at least one half,
mutual grim trigger is an equilibrium (and a subgame perfect one, since the punishment, mutual defection, is itself
an equilibrium of every subgame). The shadow of the future makes cooperation rational.

This is one case of the **folk theorem** (so called because it was known informally before anyone published it;
versions were proved by Friedman 1971 and by Fudenberg and Maskin 1986): in an infinitely repeated game with patient
enough players, *any* average payoff that is feasible and gives each player more than the worst the others can force
on her can be sustained by an equilibrium. Repetition makes cooperation possible, but also makes almost everything
else possible; it does not say which equilibrium will happen.

### Axelrod's tournaments

Which strategy actually does well against a mix of others? Robert Axelrod, a political scientist, asked game theorists
to submit programs for a computer tournament of the repeated prisoner's dilemma. In the first tournament (reported in
1980) 14 programs plus a random one played each other in a round robin, 200 rounds per match. The winner was the
shortest program entered, **TIT FOR TAT**, submitted by Anatol Rapoport: cooperate in the first round, then copy the
other player's previous move. Axelrod published the results and held a second tournament with 62 entries (plus random)
and a random game length, so that nobody could exploit the last round; TIT FOR TAT won again. Axelrod's analysis named
the properties of the successful strategies: **nice** (never the first to defect), **retaliating** (punish a defection
at once), **forgiving** (return to cooperation after the other does) and **clear** (easy for the other to recognise).
His book *The Evolution of Cooperation* (1984) and a paper with the biologist W. D. Hamilton (1981) carried the idea
into biology.

The results depend on the field of opponents. Axelrod himself reported that TIT FOR TWO TATS (defect only after two
defections in a row), a sample program he had circulated, would have won the first tournament had anyone entered it;
it was entered in the second and did much less well, because some entries learned to exploit its patience. So
"TIT FOR TAT is best" is not a theorem. No strategy is best against every population.

Our program runs a small round robin with nine classic strategies, each pair (and each strategy against itself) for
200 rounds, averaged over 5 repetitions, first without noise and then with a 5% chance that each intended move is
flipped by mistake. It then runs Axelrod's **ecological** analysis: think of a population where each strategy's share
grows in proportion to its average score against the current population, and watch who survives.

```python
--8<-- "books/ai/ch19_axelrod.py"
```

```
Round robin, noise 0%: average score per 200-round match
   GRIM           515.2
   TIT-FOR-TAT    489.3
   PAVLOV         488.0
   TF2T           486.7
   ALL-C          458.1
   ALTERNATOR     449.8
   RANDOM         431.1
   ALL-D          424.0
   JOSS           393.2

Round robin, noise 5%: average score per 200-round match
   GRIM           452.5
   ALTERNATOR     446.4
   ALL-D          443.6
   PAVLOV         438.9
   RANDOM         435.2
   TIT-FOR-TAT    433.6
   TF2T           427.7
   JOSS           427.2
   ALL-C          365.4

Ecological simulation (population shares):
   gen    ALL-C   ALL-D  RANDOM TIT-FOR    GRIM    TF2T  PAVLOV    JOSS ALTERNA
     0    0.111   0.111   0.111   0.111   0.111   0.111   0.111   0.111   0.111
     5    0.112   0.058   0.066   0.153   0.192   0.143   0.149   0.043   0.084
    10    0.116   0.014   0.021   0.191   0.268   0.164   0.180   0.009   0.037
    20    0.118   0.000   0.001   0.208   0.306   0.170   0.194   0.000   0.003
    50    0.118   0.000   0.000   0.209   0.308   0.170   0.195   0.000   0.000
   100    0.118   0.000   0.000   0.209   0.308   0.170   0.195   0.000   0.000

Three matches traced (first 12 rounds):
   TIT-FOR-TAT  CCCCDCDCDDDD
   JOSS         CCCDCDCDDDDD

   PAVLOV       CDCDCDCDCDCD
   ALL-D        DDDDDDDDDDDD

   TF2T         CCCCCCCCCCCC
   ALTERNATOR   DCDCDCDCDCDC
```

Read it carefully, because it teaches more by disagreeing with the legend:

- In this small field GRIM scores best and TIT FOR TAT is second; four nice strategies (GRIM, TIT FOR TAT, PAVLOV,
  TF2T) take the top four places, and the fifth nice one, ALL-C, comes next because it never punishes its exploiters. ALL-D, JOSS and the random player are at the bottom. That much agrees with Axelrod.
- With 5% noise everything changes. Two TIT FOR TAT players who slip once fall into an echo of alternating defections
  (the first trace shows the same echo started by JOSS's sneaky defection, which turns into mutual defection after a
  second one). Strategies that are hard to exploit by mistakes (or that exploit others' mistakes) gain. Nowak and
  Sigmund (1993) showed that **win-stay, lose-shift** (PAVLOV) does better than TIT FOR TAT in evolutionary
  simulations with noise; PAVLOV's weakness is visible in the second trace: against ALL-D it alternates and is
  suckered every other round.
- The third trace shows why TF2T can be exploited: ALTERNATOR defects every other round and is never punished.
- In the ecological run the exploiters (ALL-D, JOSS, RANDOM, ALTERNATOR) die out, because once their victims become
  rare they meet each other and score only $P$. The nice strategies remain, each scoring 3 against all the others.

<figure class="play" data-play="ipd"><span class="ai-tag">AI-created</span><figcaption><b>Try it.</b> A small repeated prisoner's dilemma tournament with the payoffs above, 50 rounds per match. Tap a strategy to add or remove it.</figcaption></figure>

## 19.3 Cooperative games and the Shapley value

So far each player acted alone. Often players can sign binding agreements, form a **coalition**, and act together;
the question becomes how to divide what the coalition earns. Three people share a taxi to the airport, a few
companies share a pipeline, features of a model share the credit for a prediction. What is a fair split?

### Coalitional games

A **cooperative game with transferable utility** (TU game) is a set $N$ of $n$ players and a **characteristic function**
$v$ that gives each coalition $S \subseteq N$ a value $v(S)$, the total it can earn on its own, with $v(\varnothing) = 0$.
"Transferable" means the members can split $v(S)$ any way they like, for instance with money. An **allocation** is a
vector $x$ with $\sum_{i \in N} x_i = v(N)$.

**Example: the glove game.** Player L owns a left glove, R1 and R2 each own a right glove, and a pair sells for 1.
So $v(S) = 1$ if $S$ contains L and at least one R, and 0 otherwise.

**The core.** An allocation is **stable** if no coalition could do better on its own: $\sum_{i \in S} x_i \ge v(S)$
for every $S$. The set of stable allocations is the **core** (Gillies 1959). In the glove game,
$x_L + x_{R1} \ge 1$ and $x_L + x_{R2} \ge 1$ and $x_L + x_{R1} + x_{R2} = 1$; subtracting gives $x_{R2} \le 0$ and
$x_{R1} \le 0$, and with $x \ge 0$ (each player can earn 0 alone) the core is the single point $(1, 0, 0)$: the
scarce left glove takes everything, because L can always threaten to deal with the other R. The core can be harsh,
and it can be empty: in the three-player majority game (any two players can share 1) every pair would need at least 1
while the total is only 1. Bondareva (1963) and Shapley (1967) proved that the core is non-empty exactly when the game
is **balanced**, a condition checkable by linear programming.

### The Shapley value

Lloyd Shapley (1953) took another route: instead of stability, write down what fairness should mean and see what
follows. Let $\varphi_i(v)$ be player $i$'s share in game $v$. Shapley asked for four properties:

1. **Efficiency:** $\sum_i \varphi_i(v) = v(N)$; everything is divided.
2. **Symmetry:** if $v(S \cup \{i\}) = v(S \cup \{j\})$ for every $S$ containing neither, then
   $\varphi_i = \varphi_j$; players who contribute the same get the same.
3. **Null player:** if $v(S \cup \{i\}) = v(S)$ for every $S$, then $\varphi_i = 0$; who adds nothing gets nothing.
4. **Additivity:** $\varphi(v + w) = \varphi(v) + \varphi(w)$; if two games are played, the shares add.

**Theorem (Shapley 1953).** Exactly one function satisfies the four axioms:

$$
\varphi_i(v) = \sum_{S \subseteq N \setminus \{i\}} \frac{|S|!\,(n - |S| - 1)!}{n!}\,\bigl(v(S \cup \{i\}) - v(S)\bigr).
$$

The formula has a friendly reading. Let the players arrive one by one in a random order, all $n!$ orders equally
likely, and pay each player her **marginal contribution**, the increase in value when she arrives. Her Shapley value
is her average payment. The weight $|S|!(n - |S| - 1)!/n!$ is exactly the probability that the players before $i$ are
the set $S$: $|S|!$ orders of the earlier players, $(n - |S| - 1)!$ orders of the later ones, out of $n!$.

*Proof that the formula satisfies the axioms.* In every order the marginal contributions add up to
$v(N) - v(\varnothing) = v(N)$ (the sum telescopes), so their averages do too: efficiency. Swapping $i$ and $j$ in every
order is a bijection of orders that, for symmetric players, swaps their marginal contributions: symmetry. A null
player's marginal contribution is always 0. Marginal contributions are linear in $v$: additivity. $\square$

*Proof of uniqueness.* *Level: advanced.* For a non-empty coalition $T$ define the **unanimity game** $u_T(S) = 1$ if
$T \subseteq S$ and 0 otherwise. For a constant $c$, in $c \cdot u_T$ every player outside $T$ is a null player and
all players in $T$ are symmetric, so the axioms force $\varphi_i = c / |T|$ for $i \in T$ and 0 otherwise. Next, every
game is a combination of unanimity games: $v = \sum_{T \ne \varnothing} c_T u_T$, where the **Harsanyi dividends**
$c_T = \sum_{S \subseteq T} (-1)^{|T| - |S|} v(S)$ come from Möbius inversion on subsets. (Check: the
$2^n - 1$ games $u_T$ are linearly independent, since ordering coalitions by size makes the system triangular, so they
form a basis of the space of games.) The dividends $c_T$ may be negative, so we apply additivity to the games
$\sum_{c_T > 0} c_T u_T$ and $\sum_{c_T < 0} (-c_T) u_T$ separately and subtract; additivity applied to
$w + (v - w) = v$ shows $\varphi(v - w) = \varphi(v) - \varphi(w)$. Hence any function obeying the axioms gives
$\varphi_i(v) = \sum_{T \ni i} c_T / |T|$: it is determined. $\square$

The last formula is another way to say it: every coalition $T$ produces its own dividend $c_T$, which is shared equally
among its members.

### Worked examples

**Glove game, by hand.** The six arrival orders, and who completes the first pair:

| order | L gets | R1 gets | R2 gets |
|-------|--------|---------|---------|
| L R1 R2 | 0 | 1 | 0 |
| L R2 R1 | 0 | 0 | 1 |
| R1 L R2 | 1 | 0 | 0 |
| R1 R2 L | 1 | 0 | 0 |
| R2 L R1 | 1 | 0 | 0 |
| R2 R1 L | 1 | 0 | 0 |
| **average** | **4/6 = 2/3** | **1/6** | **1/6** |

The Shapley value $(2/3, 1/6, 1/6)$ rewards L for scarcity but gives the right-glove owners something. It is not in
the core ($x_L + x_{R1} = 5/6 < 1$), which shows that the two ideas of fairness and stability can disagree. When the game
is **convex** ($v(S \cup T) + v(S \cap T) \ge v(S) + v(T)$), Shapley (1971) proved that the Shapley value always lies in
the core.

**Voting power.** In a committee with weights 50, 49 and 1 and a quota of 51, a coalition wins (value 1) when its
weights reach 51. A wins with either B or C, while B and C together have only 50. The Shapley value of this game is the
**Shapley-Shubik power index** (Shapley and Shubik 1954): it comes out as $(2/3, 1/6, 1/6)$. The member with 49 votes
has exactly the power of the member with 1 vote. Weight is not power.

**The airport game** (Littlechild and Owen 1973). Three plane types need runways of length 1, 2 and 3, and a runway
long enough for the largest plane in a coalition costs that length. The Shapley cost shares are $1/3$, $5/6$, $11/6$:
the first unit of runway is split three ways, the second unit two ways (between the medium and large planes), the third
paid by the large plane alone. The rule "divide the cost of each segment equally among those who use it" is
exactly what the Shapley value says for every game of this shape, which is the paper's result.

```python
--8<-- "books/ai/ch19_shapley.py"
```

```
Glove game
   by permutations: L:   2/3  R1:   1/6  R2:   1/6
   by subsets:      L:   2/3  R1:   1/6  R2:   1/6
   core points on a grid of twelfths: [('1', '0', '0')]

Weighted voting, quota 51, weights A=50, B=49, C=1 (Shapley-Shubik power)
    A:   2/3  B:   1/6  C:   1/6

Airport cost game, runway costs 1, 2, 3
    small:   1/3  medium:   5/6  large:  11/6    sum = 3

10-player game: exact (2^9 subsets per player) vs sampled orders
   exact    1.500 1.000 1.000 1.000 1.000 1.000 1.000 1.000 1.000 1.500
   m=100    1.590 1.014 1.034 0.972 1.054 1.070 0.998 1.052 0.888 1.328   max error 0.172
   m=1000   1.508 0.975 0.983 1.011 0.983 1.047 1.007 1.005 0.977 1.506   max error 0.047
   m=10000  1.497 1.006 0.999 0.997 0.999 1.003 0.998 0.999 0.993 1.509   max error 0.009
```

The exact formula costs $n \cdot 2^{n-1}$ evaluations of $v$; for 10 players that is 5120, but for 50 it is out of
reach. The last block shows the standard fix: sample random orders and average the marginal contributions. Each sample
is an unbiased estimate, so the error shrinks like $1/\sqrt{m}$: about $0.17$, $0.05$ and $0.01$ for 100, 1000 and
10 000 orders, roughly a factor of 3 for each tenfold increase. Computing the exact value is #P-hard for weighted
voting games (Deng and Papadimitriou 1994), so sampling is how it is done in practice. The same sampling, with the
features of a machine-learning model as players and the model's output as $v$, is the SHAP attribution method of the
[Machine learning book, Chapter 22](../machine-learning/22-Machine-Learning-in-Practice.md#224-interpretability); there
the hard question is what $v(S)$ means when the features outside $S$ are "absent".

## 19.4 Mechanism design and auctions

Game theory takes the rules as given and predicts behaviour. **Mechanism design** turns the question around: we want a
certain outcome (the item goes to whoever values it most; a road is built only if it is worth its cost), but the
information needed is private, held by agents who may lie. Can we write rules so that self-interested agents, playing
the game the rules define, produce the outcome we want? It is sometimes called reverse game theory. Auctions are its
best-known success.

### Four auctions

One item is for sale. Bidder $i$ has a private **value** $v_i$ (the most she would pay); if she wins and pays $p$ her
utility is $v_i - p$, and 0 if she loses. The common formats:

- **English** (ascending): the price rises until one bidder is left, who pays that price.
- **Dutch** (descending): the price falls until someone accepts it.
- **First-price sealed bid:** each submits a sealed bid; the highest bid wins and pays its own bid.
- **Second-price sealed bid** (Vickrey 1961): the highest bid wins and pays the *second-highest* bid.

In a first-price auction bidding your value is pointless: you would win only at zero utility. You must **shade** your
bid below your value, and how much depends on what you believe about the others. A second-price auction removes that
guesswork entirely.

### The second-price auction is truthful

A mechanism is **truthful** (or **strategy-proof**, **dominant-strategy incentive compatible**) if reporting your true
value is a dominant strategy: it is at least as good as any other report, whatever the others do.

**Theorem (Vickrey 1961).** In a second-price auction, bidding $b_i = v_i$ is a (weakly) dominant strategy.

*Proof.* Fix the other bids and let $h$ be the highest of them. Your bid only decides whether you win; it never
changes the price, which is $h$ if you win. If you win your utility is $v_i - h$; if you lose it is 0. Bidding your
value wins exactly when $v_i > h$, that is, exactly when $v_i - h > 0$ (with ties broken either way it does not
matter, since then $v_i - h = 0$). Consider any other bid $b$.

- If $h < v_i$: the truthful bid wins and gets $v_i - h > 0$. Bid $b$ either also wins (same utility) or, if
  $b < h$, loses and gets 0. Never better.
- If $h > v_i$: the truthful bid loses and gets 0. Bid $b$ either also loses (0) or, if $b > h$, wins and pays
  $h > v_i$, so its utility $v_i - h$ is negative. Never better.
- If $h = v_i$: every outcome gives utility 0.

In every case the truthful bid does at least as well as $b$. $\square$

The proof shows what can go wrong with lies: underbidding can only lose a profitable win, overbidding can only win an
unprofitable one. The program checks the claim on a grid of 9261 (value, bid, rival) combinations and finds no case
where a lie helps.

<figure class="mars-fig" markdown="0">
<svg viewBox="0 0 640 300" role="img" aria-label="Two plots of utility against bid in a second-price auction for a bidder whose value is 0.6. Left, the rival bids 0.4: utility is 0 below 0.4 and 0.2 above, so truth is among the best bids. Right, the rival bids 0.8: utility is 0 below 0.8 and minus 0.2 above, so truth is again among the best.">
<line x1="50" y1="170" x2="300" y2="170" stroke="currentColor" stroke-width="1.2"/>
<line x1="50" y1="258" x2="50" y2="40" stroke="currentColor" stroke-width="1.2"/>
<text x="40" y="174" font-size="11" text-anchor="end" fill="currentColor">0</text>
<text x="40" y="94" font-size="11" text-anchor="end" fill="currentColor">0.2</text>
<text x="40" y="214" font-size="11" text-anchor="end" fill="currentColor">−0.1</text>
<line x1="46" y1="90" x2="54" y2="90" stroke="currentColor" stroke-width="1"/>
<line x1="46" y1="210" x2="54" y2="210" stroke="currentColor" stroke-width="1"/>
<line x1="46" y1="250" x2="54" y2="250" stroke="currentColor" stroke-width="1"/>
<text x="40" y="254" font-size="11" text-anchor="end" fill="currentColor">−0.2</text>
<line x1="50" y1="170" x2="150" y2="170" stroke="#9cc9ea" stroke-width="4"/>
<line x1="150" y1="90" x2="300" y2="90" stroke="#9cc9ea" stroke-width="4"/>
<line x1="150" y1="170" x2="150" y2="90" stroke="#9cc9ea" stroke-width="1" stroke-dasharray="3 3"/>
<line x1="200" y1="175" x2="200" y2="60" stroke="#eea66f" stroke-width="2"/>
<text x="200" y="54" font-size="12" text-anchor="middle" fill="currentColor">truth 0.6</text>
<text x="150" y="190" font-size="11" text-anchor="middle" fill="currentColor">0.4</text>
<text x="300" y="190" font-size="11" text-anchor="middle" fill="currentColor">1</text>
<text x="175" y="288" font-size="12" text-anchor="middle" fill="currentColor">rival bids 0.4: bid anything above 0.4</text>
<line x1="370" y1="170" x2="620" y2="170" stroke="currentColor" stroke-width="1.2"/>
<line x1="370" y1="258" x2="370" y2="40" stroke="currentColor" stroke-width="1.2"/>
<text x="360" y="174" font-size="11" text-anchor="end" fill="currentColor">0</text>
<text x="360" y="94" font-size="11" text-anchor="end" fill="currentColor">0.2</text>
<text x="360" y="214" font-size="11" text-anchor="end" fill="currentColor">−0.1</text>
<line x1="366" y1="90" x2="374" y2="90" stroke="currentColor" stroke-width="1"/>
<line x1="366" y1="210" x2="374" y2="210" stroke="currentColor" stroke-width="1"/>
<line x1="366" y1="250" x2="374" y2="250" stroke="currentColor" stroke-width="1"/>
<text x="360" y="254" font-size="11" text-anchor="end" fill="currentColor">−0.2</text>
<line x1="370" y1="170" x2="570" y2="170" stroke="#9cc9ea" stroke-width="4"/>
<line x1="570" y1="250" x2="620" y2="250" stroke="#9cc9ea" stroke-width="4"/>
<line x1="570" y1="170" x2="570" y2="250" stroke="#9cc9ea" stroke-width="1" stroke-dasharray="3 3"/>
<line x1="520" y1="175" x2="520" y2="60" stroke="#eea66f" stroke-width="2"/>
<text x="520" y="54" font-size="12" text-anchor="middle" fill="currentColor">truth 0.6</text>
<text x="570" y="162" font-size="11" text-anchor="middle" fill="currentColor">0.8</text>
<text x="495" y="288" font-size="12" text-anchor="middle" fill="currentColor">rival bids 0.8: stay below 0.8</text>
</svg>
<figcaption>Figure 19.3. Utility (vertical) against your bid (horizontal) in a second-price auction when your value is 0.6. The price is the rival's bid, so your bid only moves the point where you start winning. Left: the rival bids 0.4 and winning is worth 0.2, so any bid above 0.4 is best, the truth included. Right: the rival bids 0.8 and winning costs you 0.2, so any bid below 0.8 is best, the truth included. Truth is best in both, without knowing the rival's bid.</figcaption>
</figure>

### The first-price auction: shading derived

To analyse a first-price auction we need beliefs. The standard **independent private values** model: the $n$ values
are drawn independently from the uniform distribution on $[0, 1]$, and this is common knowledge. A **Bayes-Nash
equilibrium** is a bidding function $\beta$ such that, if everyone else bids $\beta(v_j)$, bidding $\beta(v_i)$
maximises your expected utility.

Guess $\beta(v) = kv$. If you bid $b \le k$, you beat rival $j$ when $k v_j < b$, which has probability $b/k$, so
independently over the $n - 1$ rivals you win with probability $(b/k)^{n-1}$, and your expected utility is

$$
U(b) = (v - b)\left(\frac{b}{k}\right)^{n-1}.
$$

Set the derivative to zero: $-b^{n-1} + (n-1)(v - b) b^{n-2} = 0$, so $b = \frac{n-1}{n} v$, and this holds for every
$v$ exactly when $k = \frac{n-1}{n}$. So $\beta(v) = \frac{n-1}{n} v$ is an equilibrium: with 2 bidders, bid half your
value; with 10, bid 90%. More competition, less shading. The program confirms on a grid that a bidder with value 0.8
does best with 0.4 against one rival and 0.64 against four.

### Revenue equivalence

Which format earns the seller more? In the second-price auction the winner pays the second-highest value. The
expected $k$-th smallest of $n$ independent uniform values is $k/(n+1)$, so the expected price is $(n-1)/(n+1)$. In
the first-price auction the winner (the highest value, expected $n/(n+1)$) pays $\frac{n-1}{n}$ of it: again
$(n-1)/(n+1)$. The same! This is no coincidence.

**Revenue equivalence theorem** (Myerson 1981; Riley and Samuelson 1981), stated: with risk-neutral bidders whose
values are independent draws from the same continuous distribution, any two auctions in which the highest value always
wins and a bidder with the lowest possible value expects to pay nothing give the seller the same expected revenue in
equilibrium. The proof (in Krishna's *Auction Theory*) shows that the equilibrium expected payment of each type is
pinned down by the probability of winning, via an envelope-theorem argument. It fails when the assumptions fail: with
risk-averse bidders the first-price auction earns more, with correlated values the English auction can earn more.
Myerson (1981) also found the revenue-maximising auction: for uniform values it is a second-price auction with a
**reserve price** of $1/2$ (exercise 7).

```python
--8<-- "books/ai/ch19_auctions.py"
```

```
second price: 9261 (value, bid, rival) triples checked, cases where a lie beats the truth: 0
first price, n=2, value 0.8: best bid on a grid 0.400, theory (n-1)/n * v = 0.400
first price, n=5, value 0.8: best bid on a grid 0.640, theory (n-1)/n * v = 0.640

expected revenue with n bidders, values uniform on [0, 1] (200000 auctions each)
    n   second price   first price   theory (n-1)/(n+1)
    2      0.3333       0.3333        0.3333
    3      0.5001       0.5004        0.5000
    5      0.6672       0.6667        0.6667
   10      0.8178       0.8180        0.8182

VCG: efficient allocation {1: [], 2: ['A'], 3: ['B']} welfare 12
   bidder 1 pays 12 - 12 = 0, utility 0
   bidder 2 pays 10 - 6 = 4, utility 2
   bidder 3 pays 10 - 6 = 4, utility 2
   seller's revenue 8 (bidder 1 alone was willing to pay 10)
```

### VCG: truthfulness for many items

*Level: advanced.* With several items and bidders who want combinations (a left and a right shoe; two adjacent radio
frequencies), Vickrey's idea generalises. The **Vickrey-Clarke-Groves (VCG) mechanism** (Vickrey 1961, Clarke 1971,
Groves 1973) asks every bidder to report her values for every bundle, then

1. chooses the allocation that maximises the total reported value (the **welfare**);
2. charges each bidder $i$ the harm she does to the others: (the best welfare the others could get without $i$) minus
   (the welfare the others get in the chosen allocation).

**Theorem.** Reporting true values is a dominant strategy in VCG.

*Proof.* Bidder $i$'s utility, if the chosen allocation is $a$, is
$v_i(a) - [W_{-i}^{\ast} - \sum_{j \ne i} \hat v_j(a)] = [v_i(a) + \sum_{j \ne i} \hat v_j(a)] - W_{-i}^{\ast}$, where
$\hat v_j$ are the others' reports and $W_{-i}^\ast$, the best welfare without $i$, does not depend on anything $i$
reports. So $i$ wants the mechanism to pick the $a$ that maximises $v_i(a) + \sum_{j \ne i} \hat v_j(a)$, her true
value plus the others' reported values. That is exactly what the mechanism picks when she reports truthfully. Any
other report can only make it pick a different $a$, which cannot score higher in this sum. $\square$

The single-item VCG mechanism is the second-price auction. The program's example shows VCG's well-known weakness: two
small bidders who want one item each beat a big bidder who wants both (welfare 12 against 10), but each pays only 4,
so the seller earns 8 although the big bidder alone offered 10. VCG can also be manipulated by bidders who join under
several names. Real combinatorial auctions therefore use other designs; Milgrom's *Putting Auction Theory to Work*
(2004) explains why. Computing VCG also requires solving the welfare problem exactly, which for bundles is NP-hard
(it contains weighted set packing; see the [Algorithms book, Chapter 22](../algorithms/22-NP-Completeness.md)).

## 19.5 Social choice: voting rules, Arrow's theorem

A team of agents (or people) must pick one plan out of several, and each member ranks the plans. How should the
individual rankings be combined into a group decision? **Social choice theory** studies this question mathematically.

### Four rules, four winners

A **profile** lists each voter's ranking. Here is one with 21 voters and four candidates:

| voters | ranking |
|--------|---------|
| 7 | A > B > C > D |
| 6 | D > C > B > A |
| 5 | B > C > D > A |
| 3 | C > D > A > B |

- **Plurality:** each voter names her top choice; most votes wins. A has 7, D 6, B 5, C 3: **A wins**.
- **Borda count** (Borda, published 1781): with 4 candidates a voter gives 3 points to her first, 2 to her second, 1 to her
  third, 0 to her last. A gets $7 \cdot 3 + 3 \cdot 1 = 24$; C gets $6 \cdot 2 + 5 \cdot 2 + 3 \cdot 3 + 7 \cdot 1 = 38$,
  the most: **C wins**.
- **Instant runoff:** repeatedly eliminate the candidate with fewest first places and transfer those ballots to their
  next surviving choice. C (3) goes first and its votes go to D (now 9); then B (5) goes and its votes go to D (C is
  gone); D beats A 14 to 7: **D wins**.
- **Condorcet's rule:** a candidate who beats every other in a head-to-head majority vote is the **Condorcet winner**
  (Condorcet 1785). B beats A 11 to 10, C 12 to 9 and D 12 to 9: **B wins**.

```python
--8<-- "books/ai/ch19_voting.py"
```

```
Profile: 7 x A>B>C>D, 6 x D>C>B>A, 5 x B>C>D>A, 3 x C>D>A>B
plurality scores {'A': 7, 'B': 5, 'C': 3, 'D': 6} -> winner A
Borda scores     {'A': 24, 'B': 35, 'C': 38, 'D': 29} -> winner C
instant runoff round {'A': 7, 'B': 5, 'C': 3, 'D': 6} eliminate C
instant runoff round {'A': 7, 'B': 5, 'D': 9} eliminate B
instant runoff round {'A': 7, 'D': 14} eliminate A
instant runoff winner D
pairwise majorities (row beats column by this many of 21):
      A   B   C   D
   A   -  10   7   7
   B  11   -  12  12
   C  14   9   -  15
   D  14   9   6   -
Condorcet winner: B

Three voters A>B>C, B>C>A, C>A>B: A beats B 2 to 1, B beats C 2 to 1, C beats A 2 to 1; Condorcet winner: None

n=3 voters, all 216 profiles enumerated: no Condorcet winner in 12 = 0.0556
n=11    voters, 20000 random profiles: no Condorcet winner in 0.0775
n=101   voters, 20000 random profiles: no Condorcet winner in 0.0867
n=1001  voters, 4000 random profiles: no Condorcet winner in 0.0927
limit as n grows (Guilbaud 1952): 1/4 - 3/(2 pi) arcsin(1/3) = 0.0877
```

Same ballots, four different winners. None of the rules is "wrong"; each formalises a different idea of what the group
wants. Notice too that plurality invites strategy: the six D voters prefer B to A, and if they all voted for B, B would
win plurality with 11. Voters who misreport to get a better outcome are **manipulating** the rule.

### Condorcet's paradox

Three voters rank A > B > C, B > C > A and C > A > B. A majority (2 to 1) prefers A to B, a majority prefers B to C, and
a majority prefers C to A. Majority preference is not transitive: it runs in a cycle, and there is no Condorcet
winner. The program counts how often this happens when each voter picks one of the six rankings at random (the
**impartial culture** model): with 3 voters, 12 of the 216 profiles have no Condorcet winner (the 6 cyclic profiles in
each of 2 directions); as the number of voters grows the frequency tends to about 8.8%, a limit computed by Guilbaud
(1952). (The estimate 0.0927 for 1001 voters is within about one standard error, 0.0045, of it.)

<figure class="mars-fig" markdown="0">
<svg viewBox="0 0 400 280" role="img" aria-label="A triangle of candidates A, B and C. Arrows show majority preference going from A to B, B to C and C back to A, each by 2 votes to 1.">
<circle cx="200" cy="50" r="24" fill="#9cc9ea" fill-opacity="0.6" stroke="currentColor" stroke-width="1.3"/>
<circle cx="70" cy="230" r="24" fill="#eea66f" fill-opacity="0.6" stroke="currentColor" stroke-width="1.3"/>
<circle cx="330" cy="230" r="24" fill="#7ccf9a" fill-opacity="0.6" stroke="currentColor" stroke-width="1.3"/>
<text x="200" y="56" font-size="16" text-anchor="middle" fill="currentColor">A</text>
<text x="330" y="236" font-size="16" text-anchor="middle" fill="currentColor">B</text>
<text x="70" y="236" font-size="16" text-anchor="middle" fill="currentColor">C</text>
<line x1="216" y1="72" x2="308" y2="200" stroke="currentColor" stroke-width="1.8"/>
<polygon points="314,208 302,203 312,196" fill="currentColor"/>
<line x1="304" y1="232" x2="104" y2="232" stroke="currentColor" stroke-width="1.8"/>
<polygon points="96,232 108,226 108,238" fill="currentColor"/>
<line x1="84" y1="208" x2="180" y2="76" stroke="currentColor" stroke-width="1.8"/>
<polygon points="186,68 184,81 174,74" fill="currentColor"/>
<text x="290" y="128" font-size="12" fill="currentColor">A beats B, 2 to 1</text>
<text x="200" y="256" font-size="12" text-anchor="middle" fill="currentColor">B beats C, 2 to 1</text>
<text x="112" y="128" font-size="12" text-anchor="end" fill="currentColor">C beats A, 2 to 1</text>
</svg>
<figcaption>Figure 19.4. Condorcet's paradox. Each voter has a perfectly consistent ranking (A &gt; B &gt; C, B &gt; C &gt; A, C &gt; A &gt; B), but the majority's preferences run round a cycle, so every candidate loses some head-to-head vote.</figcaption>
</figure>

### Arrow's theorem

Is there a perfect rule? Kenneth Arrow (1951) made the question precise. A **social welfare function** takes every
profile of rankings of the candidates and returns one group ranking. Arrow asked for:

- **Unrestricted domain:** it works for every possible profile.
- **Pareto (unanimity):** if every voter ranks X above Y, so does the group.
- **Independence of irrelevant alternatives (IIA):** the group's order of X and Y depends only on each voter's order
  of X and Y, not on where other candidates are placed.
- **Non-dictatorship:** there is no voter whose ranking always becomes the group's ranking.

**Arrow's impossibility theorem (1951).** With three or more candidates, no social welfare function satisfies all four.

The proof is about two pages. Geanakoplos (2005) gives three short proofs; the idea of the first is to take two
candidates and move the voters, one at a time, from ranking one candidate last to first, and show that some single
voter is **pivotal**: when she switches, the group switches. Using IIA and Pareto one then shows that this voter's
preference decides every pair, so she is a dictator. Each of the familiar rules gives up something: majority voting
fails transitivity (it is not even a social welfare function, because of cycles), and Borda fails IIA (exercise 9). With
two candidates, May (1952) proved that majority rule is the only rule that treats voters equally, treats candidates
equally, and responds positively to more support, so the difficulty begins at three.

A cousin theorem concerns lying. A voting rule (returning one winner) is **strategy-proof** if no voter ever gains by
misreporting. **Gibbard-Satterthwaite theorem** (Gibbard 1973, Satterthwaite 1975): with three or more candidates,
every strategy-proof rule that can elect every candidate is a dictatorship. Compare the Vickrey auction: it escapes
because money lets the mechanism charge for the harm a bidder causes, which pure voting cannot.

For AI, these are not only questions about elections. An ensemble of models voting on a label, a group of robots
choosing a plan, a recommender combining many users' rankings, or a system aggregating human preference judgments
(Chapter 20) all aggregate rankings, and the theorems say every aggregation method makes trade-offs. **Computational
social choice** adds the algorithmic angle: some rules are NP-hard to compute (Kemeny's rule, which finds the ranking
that disagrees with the fewest pairwise votes), and Bartholdi, Tovey and Trick (1989) suggested that computational
hardness of manipulation could protect rules that cannot be made strategy-proof.

## 19.6 Multi-agent learning and coordination

*Level: advanced.* Everything above assumed the agents know the game and reason it through. Learning agents
(Chapter 15) do not: they adjust their behaviour from experience. With one learner, the world is fixed while it learns.
With several, each learner is part of the others' world, and that world keeps changing as they learn. Three questions
follow: does learning reach an equilibrium, which one, and can agents learn to coordinate?

### No-regret learning

Measure a learner by its **regret**: how much more it would have earned by playing the best *single* strategy in
hindsight, against the same sequence of opponent plays. After $T$ rounds with payoffs $u_t(s)$,

$$
\mathrm{Regret}_T = \max_s \sum_{t=1}^{T} u_t(s) - \sum_{t=1}^{T} u_t(s_t).
$$

A learner has **no regret** if $\mathrm{Regret}_T / T \to 0$ against every opponent, adaptive or not. **Regret
matching** (Hart and Mas-Colell 2000) is a simple no-regret rule: keep, for each strategy $s$, the cumulative regret
$R_T(s)$ for not having played $s$ every time, and play each $s$ with probability proportional to $\max(R_T(s), 0)$ (or
uniformly if all are non-positive). Its average regret falls like $O(1/\sqrt{T})$. The multiplicative-weights (Hedge)
algorithm of Freund and Schapire (1997) is another such rule; regret matching is the core of the counterfactual
regret minimisation used for poker in Chapter 6.

**Theorem.** In a two-player zero-sum game, if both players' average regrets after $T$ rounds are at most $\varepsilon$,
then their average strategies $\bar x, \bar y$ form a $2\varepsilon$-equilibrium: neither can gain more than
$2\varepsilon$ by deviating.

*Proof.* Let $A$ be the row player's payoffs and $\bar v = \frac{1}{T}\sum_t x_t^{\mathsf T} A y_t$ the average
payoff. The row player's regret bound says $\max_i (A \bar y)_i - \bar v \le \varepsilon$, since the best fixed row
against the sequence $y_t$ earns $\max_i (A\bar y)_i$ on average. The column player's payoff is $-A$, so its bound says
$\max_j (-\bar x^{\mathsf T} A)_j + \bar v \le \varepsilon$, that is, $\bar v - \min_j (\bar x^{\mathsf T} A)_j \le \varepsilon$.
Adding,

$$
\max_i (A \bar y)_i - \min_j (\bar x^{\mathsf T} A)_j \le 2\varepsilon.
$$

Since $\min_j (\bar x^{\mathsf T} A)_j \le \bar x^{\mathsf T} A \bar y \le \max_i (A \bar y)_i$, the row player's best
deviation gains $\max_i (A\bar y)_i - \bar x^{\mathsf T} A \bar y \le 2\varepsilon$, and the same for the column
player. $\square$

So two no-regret learners playing each other "solve" a zero-sum game without either one knowing the other's payoffs.
In general-sum games the guarantee is weaker: the empirical distribution of joint play converges to the set of
**coarse correlated equilibria**. Hart and Mas-Colell's own procedure measures a stronger, conditional regret ("each
time I played $s$, how much better would $s'$ have been?"), and with it the empirical play converges to the set of
**correlated equilibria** (Aumann 1974); the simpler unconditional version coded here gives the coarse ones.
Correlated equilibria are distributions over joint actions,
as if a trusted mediator recommended an action to each player privately, from which no player wants to deviate given
her recommendation. A traffic light is the everyday example (exercise 10). Correlated equilibria are solutions of a
linear program, so unlike Nash equilibria they can be computed in polynomial time.

### Learning dynamics can cycle

There is a catch, visible in the theorem: it is the *average* strategy that converges, not the strategy being played.
The program's first block prints both. The average approaches $(1/3, 1/3, 1/3)$ while the current strategy jumps
around. The second block is plainer still. In matching pennies, let each player follow the gradient of its own payoff,
$u = (2p-1)(2q-1)$ for the row player and $-u$ for the column player. The gradients rotate the point $(p, q)$ around
the equilibrium $(1/2, 1/2)$, and with a finite step size each step pushes it outward, until it runs round the edge of
the square. Singh, Kearns and Mansour (2000) analysed this "infinitesimal gradient ascent" and showed that in 2×2
games the strategies may cycle for ever even though the average payoffs converge. Gradient descent, the workhorse of
machine learning ([Machine learning, Chapter 5](../machine-learning/05-Optimization.md)), was built for one objective;
with several players each minimising its own loss, the joint update is no longer the gradient of anything, and it can
rotate instead of descend. Training generative adversarial networks is exactly such a two-player game, which is one
reason it is unstable.

### Coordination: independent learners in the climbing game

In a **cooperative** (common-payoff) game all agents receive the same reward, so there is no conflict, only the need to
coordinate. Claus and Boutilier (1998) studied the **climbing game**, where both agents get

|       | a   | b   | c  |
|-------|-----|-----|----|
| **a** | 11  | −30 | 0  |
| **b** | −30 | 7   | 6  |
| **c** | 0   | 0   | 5  |

The best joint action is (a, a) with 11, but it sits next to −30 penalties: if one agent explores b while the other
plays a, both are punished. An **independent learner** keeps Q-values (Chapter 15) for its own three actions only and
treats the other agent as part of the environment. Its estimate of "a" averages 11 with the −30s it got while the
other explored, so "a" looks worse than the safe "c". A single learner that controls both agents and keeps Q-values
for all nine joint actions does not have this problem.

```python
--8<-- "books/ai/ch19_learning.py"
```

```
Regret matching, self-play on rock-paper-scissors (row player)
        t   average strategy      current strategy      exploitability of averages
       10   [0.176 0.411 0.413]   [0.012 0.    0.988]   0.4698
      100   [0.353 0.295 0.352]   [1. 0. 0.]   0.1146
     1000   [0.335 0.347 0.318]   [0.    0.579 0.421]   0.0327
    10000   [0.335 0.329 0.336]   [1. 0. 0.]   0.0127
   100000   [0.333 0.335 0.332]   [0.    0.236 0.764]   0.0039

Simultaneous gradient ascent in matching pennies, step 0.05, start (p, q) = (0.6, 0.5)
   step   0  p=0.600  q=0.500  distance from (0.5, 0.5) 0.100
   step  50  p=0.259  q=0.615  distance from (0.5, 0.5) 0.267
   step 100  p=0.859  q=0.094  distance from (0.5, 0.5) 0.542
   step 150  p=0.254  q=0.998  distance from (0.5, 0.5) 0.556
   step 200  p=0.611  q=0.000  distance from (0.5, 0.5) 0.512
   step 250  p=0.528  q=1.000  distance from (0.5, 0.5) 0.501
   step 300  p=0.337  q=0.013  distance from (0.5, 0.5) 0.514

Climbing game, independent Q-learners, 200 runs, final greedy joint action:
   (c,c) reward 5: 104, (a,a) reward 11: 87, (b,c) reward 6: 8, (c,a) reward 0: 1

Climbing game, one learner over joint actions, 200 runs, final greedy joint action:
   (a,a) reward 11: 200
```

Over 200 runs, independent learners settle on the safe but poor (c, c) more often than on the best (a, a), and a few
times on (b, c) or (c, a), which are not even equilibria (against b the column agent would rather play b); that is
simply where their noisy, out-of-date estimates stopped when training ended. The joint learner finds (a, a) every time. The lesson generalises:
independent learning is simple and scales to many agents, but each agent sees a **non-stationary** world (the other is
changing), so the convergence guarantees of single-agent Q-learning no longer apply; joint learning has the
guarantees but its action space grows exponentially with the number of agents ($3^n$ here).

### What multi-agent systems do now

Modern multi-agent reinforcement learning sits between the two extremes. A common pattern is **centralised training
with decentralised execution**: during training a critic may see everything (all observations and actions), but each
agent's policy uses only its own observations, so the agents can act alone afterwards. Value-decomposition methods
learn a team value that is a sum (or a monotone combination) of per-agent values, so that each agent's greedy action
is also the team's greedy action. In competitive settings, **self-play** against copies and past versions of oneself
(Chapter 6: AlphaZero) extends to many players: AlphaStar reached Grandmaster level in the real-time strategy game
StarCraft II (Vinyals et al., *Nature* 2019) by training a population of agents, including agents whose only job was to
expose the main agents' weaknesses; Pluribus beat professional players at six-player no-limit Texas hold'em (Brown and
Sandholm, *Science* 2019) using regret minimisation and search, in a game where Nash equilibrium gives no guarantee of
winning. Cooperative games with hidden information, such as the card game Hanabi, were proposed as a challenge because
agents must learn to read each other's intentions (Bard et al. 2020), and agents trained together often fail with new
partners, the problem of **ad hoc teamwork** or **zero-shot coordination**.

Two older traditions deserve mention. **Distributed problem solving** (the contract net protocol of Smith 1980:
agents announce tasks, others bid, the best bidder gets the contract) uses market ideas to allocate work among robots
or processors. **Distributed constraint satisfaction** spreads the variables of a CSP (Chapter 7) over agents who
must agree by message passing. Both reappear wherever a fleet must share work without a central controller, for
example warehouse robots or several spacecraft working with limited communication.

## Check yourself

??? question "1. Find all Nash equilibria of the stag hunt: (Stag, Stag) = (4, 4), (Stag, Hare) = (0, 3), (Hare, Stag) = (3, 0), (Hare, Hare) = (3, 3)."
    Pure: (Stag, Stag) is an equilibrium (switching to Hare gives 3 < 4), and so is (Hare, Hare) (switching to Stag
    gives 0 < 3). The other two cells are not (the 0 player switches). Mixed: let the other hunt stag with probability
    $q$. Stag pays $4q$, Hare pays $3q + 3(1-q) = 3$; indifference gives $q = 3/4$. By symmetry both play Stag with
    probability $3/4$, each expecting 3. Three equilibria, an odd number as Wilson's theorem predicts. The game shows
    the tension between the payoff-best equilibrium (Stag, Stag) and the safe one (Hare guarantees 3).

??? question "2. Prove that a strictly dominated pure strategy is never played with positive probability in a mixed Nash equilibrium."
    Let $s$ be strictly dominated by $s'$ for player $i$. Against any mix of the others, the expected payoff of $s'$ is
    an average of $u_i(s', s_{-i})$ over the others' pure profiles, and each term exceeds the corresponding
    $u_i(s, s_{-i})$, so $v_{s'} > v_s$. By the indifference principle every supported strategy must have the maximum
    payoff, but $s$ does not, so it cannot be in the support. (The same holds if $s$ is dominated by a mixed strategy.)

??? question "3. In the repeated prisoner's dilemma with T = 4, R = 3, P = 1, S = 0 and continuation probability δ, when is mutual grim trigger an equilibrium?"
    The condition is $\delta \ge (T - R)/(T - P) = (4 - 3)/(4 - 1) = 1/3$. Check at $\delta = 1/3$: cooperating forever
    is worth $3/(1 - 1/3) = 4.5$; defecting now is worth $4 + (1/3) \cdot 1/(1 - 1/3) = 4 + 0.5 = 4.5$, equal, as it
    should be at the threshold. A smaller temptation makes cooperation easier to sustain.

??? question "4. Explain why finitely repeated play with a known last round unravels, and why an unknown end (continuation probability δ) does not."
    With a known last round $N$, round $N$ is a one-shot game, so both defect; then round $N-1$ cannot affect the
    future and both defect; and so on back to round 1 (backward induction, 19.2). With a random end there is no last
    round to start from: at every point the expected future is the same, worth $\delta/(1-\delta)$ rounds, so a
    threat to punish later is always available and the induction has no base case.

??? question "5. Compute the Shapley value of the 3-player game v(1) = v(2) = v(3) = 0, v(12) = 4, v(13) = 6, v(23) = 0, v(123) = 10."
    Marginal contributions in the six orders (players 1, 2, 3):
    123: 0, 4, 6. 132: 0, 4, 6. 213: 4, 0, 6. 231: 10, 0, 0. 312: 6, 4, 0. 321: 10, 0, 0.
    Averages: player 1: $(0+0+4+10+6+10)/6 = 5$; player 2: $(4+4+0+0+4+0)/6 = 2$; player 3: $(6+6+6+0+0+0)/6 = 3$.
    They sum to 10 (efficiency). Player 1, needed in every profitable pair, gets the most.

??? question "6. Why is the Shapley value (2/3, 1/6, 1/6) of the glove game not in the core, and what does that say?"
    The core requires $x_L + x_{R1} \ge v(\{L, R1\}) = 1$, but $2/3 + 1/6 = 5/6$. L and R1 could leave and share 1 between
    them, both doing better. The Shapley value rewards each player's average contribution over all orders, while the
    core asks only that no group can do better alone; when there is a scarce resource, stability gives it all to the
    scarce player, while the Shapley value does not. The two notions of a good split are different, and only for some
    games (such as convex games) do they agree.

??? question "7. Write code: a second-price auction with two bidders whose values are uniform on [0, 1], and a reserve price r (no sale if both bid below r; if only one is above r she pays r). Estimate the revenue for several r."
    ```python
    import numpy as np
    rng = np.random.default_rng(0)
    v = rng.random((400000, 2))
    hi, lo = v.max(1), v.min(1)
    for r in (0.0, 0.3, 0.4, 0.5, 0.6):
        price = np.where(lo >= r, lo, np.where(hi >= r, r, 0.0))
        print(r, round(price.mean(), 4))
    ```
    Output: 0.0 gives about 0.333, 0.3 about 0.388, 0.4 about 0.408, 0.5 about 0.417 and 0.6 about 0.406. The best
    reserve is $1/2$, as Myerson's theory says, with revenue $5/12 \approx 0.4167$. Bidding truthfully is still dominant
    with a reserve (the proof of 19.4 goes through with the reserve acting as one more rival bid). The seller gains by
    sometimes not selling at all.

??? question "8. Three bidders with values uniform on [0, 1] play a first-price auction. What is the equilibrium bid of a bidder with value 0.9, and what is the seller's expected revenue?"
    The equilibrium is $\beta(v) = \frac{n-1}{n} v = \frac{2}{3} v$, so the bid is $0.6$. The expected revenue is
    $(n-1)/(n+1) = 2/4 = 1/2$, the same as the second-price auction (revenue equivalence); the program's table shows
    0.5004 by simulation.

??? question "9. Show by example that the Borda count violates independence of irrelevant alternatives."
    Profile 1: 3 voters A > B > C and 2 voters B > C > A. Borda (2, 1, 0 points): A gets 6, B gets $3 + 4 = 7$, C gets 2,
    so the group ranks B above A. Profile 2: 3 voters A > C > B and 2 voters B > A > C. Every voter's order of A and B is
    unchanged (3 prefer A, 2 prefer B), only C moved. Now A gets $6 + 2 = 8$, B gets 4, C gets 3, so the group ranks A
    above B. The group's order of A and B changed although nobody changed their mind about A versus B, which IIA forbids.

??? question "10. In the game of chicken, (Dare, Dare) = (0, 0), (Dare, Chicken) = (7, 2), (Chicken, Dare) = (2, 7), (Chicken, Chicken) = (6, 6). Show that a mediator who picks (D, C), (C, D) or (C, C) with probability 1/3 each and tells each player only her own action gives a correlated equilibrium, and compare it with the mixed Nash equilibrium."
    Told "Dare": the joint action must be (D, C), so the other plays Chicken; Dare gives 7, Chicken gives 6, so obey.
    Told "Chicken": the joint action is (C, D) or (C, C), equally likely, so the other dares with probability $1/2$;
    Chicken gives $(2 + 6)/2 = 4$, Dare gives $(0 + 7)/2 = 3.5$, so obey. It is a correlated equilibrium, with
    expected payoff $(7 + 2 + 6)/3 = 5$ for each. In the mixed Nash equilibrium each dares with probability $q$
    making the other indifferent: $7(1 - q) = 2q + 6(1 - q)$ gives $q = 1/3$, and the payoff is
    $7 \cdot \tfrac{2}{3} = \tfrac{14}{3} \approx 4.67$. Correlation helps both, because it avoids the crash (D, D).

??? question "11. Write code: regret matching for one player against a fixed opponent who plays Rock 50%, Paper 30%, Scissors 20%. What does it converge to, and why?"
    ```python
    import numpy as np
    A = np.array([[0, -1, 1], [1, 0, -1], [-1, 1, 0]], dtype=float)
    y = np.array([0.5, 0.3, 0.2])
    reg = np.zeros(3)
    for t in range(10000):
        p = np.maximum(reg, 0)
        p = p / p.sum() if p.sum() > 0 else np.full(3, 1 / 3)
        u = A @ y                    # [-0.1, 0.3, -0.2]
        reg += u - p @ u
    print(np.round(p, 3))            # [0. 1. 0.]
    ```
    Against this fixed mix Rock earns $-0.1$, Paper $0.5 - 0.2 = 0.3$, Scissors $-0.5 + 0.3 = -0.2$. Paper's regret grows
    without bound while the others' become negative, so the player ends up playing Paper with probability 1, the best
    response. No-regret learning exploits a stationary opponent; only when the opponent also adapts does it move to an
    equilibrium.

??? question "12. In the climbing game, why does an independent learner undervalue action a, and name two remedies."
    Its Q-value for "a" is an average of the rewards it got when playing a, over whatever the other agent did at the
    time. While the other explores (or still prefers b or c), playing a gives −30 or 0, so the estimate of a can fall
    below that of c, which never gives less than 0. The agent is learning about a moving mixture, not about the joint
    action (a, a). Remedies: learn over joint actions (a central controller or a centralised critic); use **optimistic**
    or **lenient** learners that update mostly on the better outcomes of an action, on the theory that bad outcomes
    were the partner's exploration; reduce exploration over time so the partners' behaviour becomes stationary; or let
    the agents communicate their intended actions.

## What you learned

- A normal-form game lists players, strategies and payoffs. Dominated strategies can be removed; a Nash equilibrium is
  a profile of mutual best responses, and every finite game has one in mixed strategies (Nash 1950), though finding it
  is PPAD-hard in general.
- The indifference principle turns mixed equilibria into linear equations: the other player's mix makes me
  indifferent. Zero-sum games are solved by linear programming (von Neumann's minimax theorem).
- The prisoner's dilemma separates individual from collective rationality. A known finite horizon unravels into
  defection; an uncertain future sustains cooperation when $\delta \ge (T-R)/(T-P)$. Axelrod's tournaments favoured nice,
  retaliating, forgiving strategies, but results depend on the field and on noise.
- The Shapley value is the unique division satisfying efficiency, symmetry, null player and additivity; it is the
  average marginal contribution over arrival orders, and sampling orders estimates it.
- The second-price auction makes truthful bidding dominant; VCG extends this to many items. First-price bidders shade
  to $\frac{n-1}{n}v$, and revenue equivalence makes the formats earn the same under standard assumptions.
- Different voting rules can elect different winners from the same ballots; majorities can cycle; Arrow and
  Gibbard-Satterthwaite prove that every rule with three or more candidates gives up some desirable property.
- No-regret learners reach equilibrium on average in zero-sum games, but learning dynamics can cycle and independent
  learners can miscoordinate in cooperative games.

**Next:** [Chapter 20](20-Safe-and-Reliable-AI.md) looks at what can go wrong when an agent optimises the objective we
gave it, and at the technical tools for making AI systems robust, calibrated, verifiable and understandable.

## Further reading

- S. Russell and P. Norvig, *Artificial Intelligence: A Modern Approach*, 4th ed., 2020: chapter 18 (multiagent
  decision making).
- Y. Shoham and K. Leyton-Brown, *Multiagent Systems: Algorithmic, Game-Theoretic, and Logical Foundations*, 2009 (free
  online); N. Nisan, T. Roughgarden, É. Tardos and V. Vazirani (eds.), *Algorithmic Game Theory*, 2007; M. J. Osborne
  and A. Rubinstein, *A Course in Game Theory*, 1994.
- J. von Neumann, "Zur Theorie der Gesellschaftsspiele", *Mathematische Annalen* 100, 1928; J. von Neumann and
  O. Morgenstern, *Theory of Games and Economic Behavior*, 1944.
- J. F. Nash, "Equilibrium points in n-person games", *PNAS* 36, 1950; "Non-cooperative games", *Annals of
  Mathematics* 54, 1951. C. Daskalakis, P. W. Goldberg and C. H. Papadimitriou, "The complexity of computing a Nash
  equilibrium", STOC 2006 (*SIAM Journal on Computing* 39, 2009); X. Chen and X. Deng, "Settling the complexity of
  two-player Nash equilibrium", FOCS 2006.
- G. W. Brown, "Iterative solution of games by fictitious play", 1951; J. Robinson, "An iterative method of solving a
  game", *Annals of Mathematics* 54, 1951.
- R. Axelrod, "Effective choice in the prisoner's dilemma" and "More effective choice in the prisoner's dilemma",
  *Journal of Conflict Resolution* 24, 1980; R. Axelrod and W. D. Hamilton, "The evolution of cooperation", *Science*
  211, 1981; R. Axelrod, *The Evolution of Cooperation*, 1984; M. Nowak and K. Sigmund, "A strategy of win-stay,
  lose-shift that outperforms tit-for-tat in the Prisoner's Dilemma game", *Nature* 364, 1993.
- L. S. Shapley, "A value for n-person games", in *Contributions to the Theory of Games II*, 1953; L. S. Shapley and
  M. Shubik, "A method for evaluating the distribution of power in a committee system", *American Political Science
  Review* 48, 1954; S. C. Littlechild and G. Owen, "A simple expression for the Shapley value in a special case",
  *Management Science* 20, 1973.
- W. Vickrey, "Counterspeculation, auctions, and competitive sealed tenders", *Journal of Finance* 16, 1961; R. B.
  Myerson, "Optimal auction design", *Mathematics of Operations Research* 6, 1981; V. Krishna, *Auction Theory*, 2nd
  ed., 2009; P. Milgrom, *Putting Auction Theory to Work*, 2004.
- K. J. Arrow, *Social Choice and Individual Values*, 1951; J. Geanakoplos, "Three brief proofs of Arrow's
  impossibility theorem", *Economic Theory* 26, 2005; A. Gibbard, "Manipulation of voting schemes", *Econometrica* 41,
  1973; M. A. Satterthwaite, *Journal of Economic Theory* 10, 1975; F. Brandt, V. Conitzer, U. Endriss, J. Lang and
  A. Procaccia (eds.), *Handbook of Computational Social Choice*, 2016.
- S. Hart and A. Mas-Colell, "A simple adaptive procedure leading to correlated equilibrium", *Econometrica* 68, 2000;
  R. J. Aumann, "Subjectivity and correlation in randomized strategies", *Journal of Mathematical Economics* 1, 1974;
  S. Singh, M. Kearns and Y. Mansour, "Nash convergence of gradient dynamics in general-sum games", UAI 2000;
  C. Claus and C. Boutilier, "The dynamics of reinforcement learning in cooperative multiagent systems", AAAI 1998.
- O. Vinyals and colleagues, "Grandmaster level in StarCraft II using multi-agent reinforcement learning", *Nature*
  575, 2019; N. Brown and T. Sandholm, "Superhuman AI for multiplayer poker", *Science* 365, 2019; N. Bard and
  colleagues, "The Hanabi challenge: a new frontier for AI research", *Artificial Intelligence* 280, 2020.
- On this site: [Chapter 6](06-Games-and-Adversarial-Search.md) (minimax, regret minimisation for poker),
  [Chapter 15](15-Reinforcement-Learning.md) (Q-learning), the [Machine learning book](../machine-learning/index.md)
  (Chapter 22 for Shapley values as feature attributions), and the [Algorithms book](../algorithms/index.md) (Chapter 22
  for NP-hardness).
