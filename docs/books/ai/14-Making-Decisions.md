# 14. Making decisions

*[Chapter 12](12-Probabilistic-Reasoning.md) and [Chapter 13](13-Reasoning-over-Time.md) taught an agent what to
believe. Belief alone does nothing: a rover that is 70 percent sure a rock contains a mineral still has to decide
whether to spend an hour drilling it, and a robot that knows roughly where it is still has to choose which way to
drive. This chapter answers the question: how should an agent choose actions when their outcomes are uncertain, once
and then again and again? You will see why rational preferences force an agent to maximise expected utility (the von
Neumann-Morgenstern theorem), build decision networks and compute what a piece of information is worth, formulate
sequential problems as Markov decision processes, prove that value iteration converges, solve a grid world from scratch
with value iteration and policy iteration, and finally solve a small problem in which the agent cannot see the state at
all.*

!!! abstract "In this chapter"
    **You will learn:**

    - lotteries, preferences and the axioms of utility theory, and why they lead to the principle of maximum expected
      utility, with a proof sketch of the von Neumann-Morgenstern theorem
    - the utility of money, risk aversion and certainty equivalents, and where human choices break the axioms
    - decision networks, and how to compute the value of information (with a proof that it is never negative)
    - Markov decision processes, discounting and the Bellman equation
    - value iteration, with a full proof that it converges (the Bellman update is a contraction), and policy iteration,
      with a proof that it terminates
    - POMDPs: belief-state MDPs, why the value function is piecewise linear and convex, and an exact solution of the
      tiger problem

    **You need:** [Chapter 12](12-Probabilistic-Reasoning.md) (Bayes' rule, Bayesian networks),
    [Chapter 13](13-Reasoning-over-Time.md) (belief states, filtering) for 14.6, and the idea of dynamic programming
    from the Algorithms book's [Chapter 13](../algorithms/13-Dynamic-Programming.md). Expected values
    ([Probability](https://math.akadian.ca/books/probability/)) and solving linear systems
    ([Linear algebra](https://math.akadian.ca/books/linear-algebra/)).

    **Levels:** 14.1 and 14.2 are beginner to intermediate; 14.3 is intermediate; 14.4 is intermediate (its proofs are
    advanced); 14.5 is intermediate; 14.6 is advanced.

## 14.1 Utility theory; expected utility; von Neumann-Morgenstern axioms stated

You are offered a choice. Option A: 500 dollars for certain. Option B: a fair coin is flipped; heads you get 1000
dollars, tails nothing. Both have the same **expected value**, 500 dollars. Most people take A. Are they irrational? Now
change B to 1100 dollars on heads. Its expected value is 550, more than A, and many people still take A. To say what a
rational agent should do, we need a way to score outcomes that is not simply money.

### Outcomes, lotteries and preferences

An agent's action leads to one of several **outcomes** (states of the world after the action), each with some
probability. A situation with uncertain outcomes is called a **lottery**:

$$
L = [p_1, S_1;\ p_2, S_2;\ \dots;\ p_n, S_n],
$$

meaning outcome $S_i$ happens with probability $p_i$, the $p_i$ summing to 1. An outcome can itself be a lottery (a
ticket that wins another ticket). A certain outcome $S$ is the lottery $[1, S]$.

We write the agent's **preferences** between lotteries as

- $A \succ B$: the agent prefers $A$ to $B$;
- $A \sim B$: the agent is **indifferent** between them;
- $A \succsim B$: the agent prefers $A$ or is indifferent.

### The axioms

John von Neumann and Oskar Morgenstern, in *Theory of Games and Economic Behavior* (1944; the axiomatic treatment of
utility was added in the 1947 second edition), asked what constraints any sensible set of preferences must satisfy.
The standard modern list (as in Russell and Norvig) has six.

1. **Orderability (completeness).** For any two lotteries, exactly one of $A \succ B$, $B \succ A$, $A \sim B$ holds.
   The agent cannot refuse to compare.
2. **Transitivity.** If $A \succ B$ and $B \succ C$, then $A \succ C$.
3. **Continuity.** If $A \succ B \succ C$, there is a probability $p$ with $[p, A;\ 1-p, C] \sim B$. Some mixture of
   the best and the worst is exactly as good as the middle.
4. **Substitutability (independence).** If $A \sim B$, then $[p, A;\ 1-p, C] \sim [p, B;\ 1-p, C]$ for every $p$ and
   $C$. (Also with $\succ$ in place of $\sim$.) Equivalent things stay equivalent inside a bigger lottery.
5. **Monotonicity.** If $A \succ B$, then $[p, A;\ 1-p, B] \succsim [q, A;\ 1-q, B]$ exactly when $p \ge q$. More
   chance of the better outcome is better.
6. **Decomposability.** Compound lotteries reduce by the laws of probability:
   $[p, A;\ 1-p, [q, B;\ 1-q, C]] \sim [p, A;\ (1-p)q, B;\ (1-p)(1-q), C]$. There is "no fun in gambling" itself.

Why should anyone accept these? Take transitivity. Suppose an agent has the cycle $A \succ B \succ C \succ A$. If it
holds $C$, it will pay a cent to swap $C$ for $B$, then a cent to swap $B$ for $A$, then a cent to swap $A$ for $C$, and
it is back where it started, three cents poorer. Repeat forever. This argument, the **money pump**, shows that an agent
with intransitive preferences can be exploited without limit. Similar arguments support the others, though some
(especially substitutability) are less obviously compelling, as the Allais example below shows.

### The theorem

**Theorem (von Neumann and Morgenstern).** If an agent's preferences over lotteries with finitely many outcomes satisfy
the six axioms, then there is a real-valued function $U$ on outcomes, a **utility function**, such that

$$
A \succsim B \iff U(A) \ge U(B), \qquad U([p_1, S_1; \dots; p_n, S_n]) = \sum_{i} p_i\, U(S_i).
$$

Moreover $U$ is unique up to a positive affine transformation: $U'$ represents the same preferences if and only if
$U' = aU + b$ with $a > 0$.

**Proof sketch.** Let $S_\top$ be an outcome at least as good as every other, and $S_\bot$ one at least as bad
(orderability and transitivity give a best and worst among finitely many outcomes). If $S_\top \sim S_\bot$ every
outcome is equally good and any constant $U$ works, so assume $S_\top \succ S_\bot$. Call
$[p, S_\top;\ 1-p, S_\bot]$ the **standard lottery** with probability $p$.

1. For each outcome $S$, continuity gives a probability $u_S$ with $S \sim [u_S, S_\top;\ 1-u_S, S_\bot]$ (for $S$
   equal to the best or worst, take 1 or 0). Monotonicity makes $u_S$ unique. Define $U(S) = u_S$.
2. Take any lottery $L = [p_1, S_1; \dots; p_n, S_n]$. By substitutability, replace each $S_i$ by its equivalent
   standard lottery; $L$ is indifferent to the compound lottery in which each branch $i$ leads to
   $[u_{S_i}, S_\top;\ 1 - u_{S_i}, S_\bot]$.
3. By decomposability this compound lottery equals the standard lottery with probability $\sum_i p_i u_{S_i}$. So every
   lottery is indifferent to a standard lottery whose probability is its expected utility.
4. By monotonicity, standard lotteries are ordered by their probabilities. So $A \succsim B$ exactly when the expected
   utility of $A$ is at least that of $B$. $\square$

For uniqueness: if $U' = aU + b$ with $a > 0$, expected values are transformed the same way, so the order is unchanged.
Conversely, any representation must give the standard lotteries the right order and must be affine in probabilities,
which forces the affine relation. A complete proof is in von Neumann and Morgenstern's second edition or any decision
theory text (for example Kreps, *Notes on the Theory of Choice*, 1988).

What the theorem does **not** say is just as important. It does not say the agent consciously computes utilities. It
does not say what $U$ is: two rational agents can have very different utility functions. It says that if the
agent's preferences are coherent, they can be **described** as maximising the expected value of some $U$.

### The principle of maximum expected utility

Given evidence $e$, an action $a$ has outcomes $s'$ with probabilities $P(s' \mid a, e)$, and its **expected utility**
is

$$
EU(a \mid e) = \sum_{s'} P(s' \mid a, e)\, U(s').
$$

The **principle of maximum expected utility** (MEU) says a rational agent picks $a^* = \arg\max_a EU(a \mid e)$. In
one line it combines everything so far: probability (what will happen), utility (how good it would be) and
decision (what to do). The rest of this chapter computes it efficiently in harder and harder settings.

### The utility of money and risk

Money is the obvious outcome to put a utility on, and it shows why utility is not money. Daniel Bernoulli, in 1738,
discussed the **St Petersburg game**: a coin is flipped until it lands heads; if that happens on flip $k$ you win
$2^k$ ducats. The expected winnings are $\sum_k 2^{-k} 2^k = 1 + 1 + 1 + \cdots$, infinite, yet nobody will pay much
to play. Bernoulli proposed that the utility of money grows like its logarithm: an extra ducat matters less to the rich
than to the poor.

A utility function of money that is **concave** (curving downwards, like the logarithm) makes the agent **risk
averse**: by Jensen's inequality, for concave $U$,

$$
E[U(X)] \le U(E[X]),
$$

so the sure amount $E[X]$ is preferred to the gamble $X$. The **certainty equivalent** of a lottery is the sure amount
$c$ with $U(c) = E[U(X)]$: the price at which the agent would sell the gamble. The **risk premium** is $E[X] - c$, what
the agent will give up to avoid the risk. A **risk-seeking** agent has convex $U$; a **risk-neutral** one has linear
$U$, and for it utility is money.

The program computes these for an agent with $U = \log(\text{wealth})$ who starts with 1000 dollars.

```python
--8<-- "books/ai/ch14_utility.py"
```

```
Part 1. log utility of wealth, starting wealth 1000
coin flip for 0 or 1000: expected value 500.00, certainty equivalent 414.21, risk premium 85.79
St Petersburg game: expected money after 40 terms 40 (and growing without bound); certainty equivalent with log utility 10.97

Part 2. no information: best action drill, EU 10.00
perfect information: EU 24.00, value of perfect information 14.00
 observing the spectrometer:
   spectrometer positive: P = 0.310, P(mineral | result) = 0.774, best action drill, EU 57.42
   spectrometer negative: P = 0.690, P(mineral | result) = 0.087, best action skip, EU 0.00
   value of information 7.80
 observing the camera:
   camera positive: P = 0.350, P(mineral | result) = 0.600, best action drill, EU 40.00
   camera negative: P = 0.650, P(mineral | result) = 0.138, best action skip, EU 0.00
   value of information 4.00
both tests together: value of information 8.64 (sum of the two separately 11.80)
```

Check Part 1 by hand. The coin flip leaves wealth 1000 or 2000, so $E[U] = \tfrac12(\log 1000 + \log 2000) =
\log\sqrt{2\,000\,000} = \log 1414.21$. The certainty equivalent is $1414.21 - 1000 = 414.21$ dollars: this agent would
sell a coin flip worth 500 on average for 414.21, a risk premium of 85.79. The St Petersburg game, worth infinitely
much in expected money, is worth only about 11 dollars to it. A rich agent is less risk averse at the same stakes:
with wealth $10^6$ the premium for the same coin flip is about 0.12 dollars, because $\log$ is nearly straight over a
small range. This is why insurance exists: a person with concave utility will pay more than the expected loss to avoid
a large loss, and a large insurer, nearly risk neutral at that scale, profits by accepting.

### Where people break the axioms

Humans do not always obey the axioms. Maurice Allais showed this in 1953 with choices like the following, which Daniel
Kahneman and Amos Tversky studied in their 1979 paper on prospect theory:

- A: 80 percent chance of 4000, else nothing; B: 3000 for certain.
- C: 20 percent chance of 4000, else nothing; D: 25 percent chance of 3000, else nothing.

Most people choose B over A and C over D. No utility function fits both. Set $U(0) = 0$ (allowed, by the affine
freedom). B over A means $U(3000) > 0.8\,U(4000)$. C over D means $0.2\,U(4000) > 0.25\,U(3000)$, that is,
$U(3000) < 0.8\,U(4000)$. Contradiction. Notice that C and D are just A and B with every probability divided by 4: the
choice violates substitutability. People overweight certainty (the **certainty effect**). This is a fact about people,
not a flaw in the theory as a design for artificial agents: we want our agents to be coherent, and we should not assume
that human choices are, when we try to learn utilities from them (a theme of [Chapter 20](20-Safe-and-Reliable-AI.md)).

### Several attributes

Outcomes usually have many attributes: a rover's plan affects science return, energy, time and risk to the hardware.
**Multiattribute utility theory** asks when $U(x_1, \dots, x_n)$ can be written simply, for example as a sum
$\sum_i U_i(x_i)$. The sum form is justified when preferences for each attribute do not depend on the levels of the
others (**mutual preferential independence**, plus a stronger utility-independence condition for lotteries; Keeney
and Raiffa, 1976). Even without numbers, **dominance** helps: if one option is at least as good on every attribute and
better on one, the other can be discarded. Sometimes that is enough to decide.

## 14.2 Decision networks; value of information, computed

A **decision network** (or influence diagram, Howard and Matheson, 1984) is a Bayesian network with two more kinds of
node:

- **chance nodes** (ovals): random variables, as before;
- **decision nodes** (rectangles): choices the agent makes;
- **utility nodes** (diamonds): the utility, a function of its parents.

An arc into a decision node means that its parent's value is **known** when the decision is made.

### A toy example: should the rover drill?

The numbers below are invented for teaching. A rover can **drill** a rock or **skip** it. The rock contains a
target mineral with prior probability 0.3. Drilling costs 20 points of utility (time, energy, wear) and a sample with
the mineral is worth 100. Before deciding, the rover could look with a **spectrometer**, which reads positive with
probability 0.8 if the mineral is there and 0.1 if it is not, or with a **camera**, positive with probability 0.7 and
0.2.

<figure class="mars-fig" markdown="0">
<svg viewBox="0 0 640 230" role="img" aria-label="A decision network: chance node Mineral with arrows to chance nodes Spectrometer and Camera and to the utility node. Decision node Drill also points to the utility node. A dashed arrow from Spectrometer to Drill marks that the reading is known before deciding.">
<ellipse cx="320" cy="40" rx="62" ry="24" fill="#9cc9ea" fill-opacity="0.5" stroke="currentColor" stroke-width="1.3"/>
<text x="320" y="45" font-size="14" text-anchor="middle" fill="currentColor">Mineral</text>
<ellipse cx="120" cy="120" rx="72" ry="24" fill="#9cc9ea" fill-opacity="0.5" stroke="currentColor" stroke-width="1.3"/>
<text x="120" y="125" font-size="14" text-anchor="middle" fill="currentColor">Spectrometer</text>
<ellipse cx="520" cy="120" rx="62" ry="24" fill="#9cc9ea" fill-opacity="0.5" stroke="currentColor" stroke-width="1.3"/>
<text x="520" y="125" font-size="14" text-anchor="middle" fill="currentColor">Camera</text>
<rect x="70" y="180" width="100" height="36" fill="#eea66f" fill-opacity="0.6" stroke="currentColor" stroke-width="1.3"/>
<text x="120" y="203" font-size="14" text-anchor="middle" fill="currentColor">Drill?</text>
<polygon points="320,150 362,180 320,210 278,180" fill="#7ccf9a" fill-opacity="0.6" stroke="currentColor" stroke-width="1.3"/>
<text x="320" y="185" font-size="14" text-anchor="middle" fill="currentColor">U</text>
<line x1="275" y1="57" x2="170" y2="102" stroke="currentColor" stroke-width="1.4"/>
<polygon points="164,105 172,97 175,106" fill="currentColor"/>
<line x1="365" y1="57" x2="472" y2="102" stroke="currentColor" stroke-width="1.4"/>
<polygon points="478,105 467,106 470,97" fill="currentColor"/>
<line x1="320" y1="64" x2="320" y2="143" stroke="currentColor" stroke-width="1.4"/>
<polygon points="320,149 315,139 325,139" fill="currentColor"/>
<line x1="170" y1="192" x2="270" y2="182" stroke="currentColor" stroke-width="1.4"/>
<polygon points="276,181 266,177 267,187" fill="currentColor"/>
<line x1="120" y1="144" x2="120" y2="172" stroke="currentColor" stroke-width="1.4" stroke-dasharray="5 3"/>
<polygon points="120,178 115,168 125,168" fill="currentColor"/>
<text x="400" y="200" font-size="12" fill="currentColor">U = 100 if drilled and mineral,</text>
<text x="400" y="216" font-size="12" fill="currentColor">minus 20 if drilled; 0 if skipped</text>
</svg>
<figcaption>The rover decision network (toy numbers). Ovals are chance nodes, the rectangle is the decision, the
diamond is the utility. The dashed arc says the spectrometer reading is known before deciding; without it, the
decision is made blind.</figcaption>
</figure>

**Evaluating a decision network.** For each possible value of the decision node: set it as if it were evidence, compute
the posterior distribution of the utility node's parents (by any Bayesian network inference method of [Chapter
12](12-Probabilistic-Reasoning.md)), and compute the expected utility. Choose the best. With observed parents of the
decision, do this once for each combination of their values; the result is a **policy**, a rule from observations to
decisions.

Without any test: $EU(\text{drill}) = 0.3 \cdot 100 - 20 = 10$, $EU(\text{skip}) = 0$. Drill, expected utility 10.

### The value of information

Should the rover use the spectrometer first? Information has value only if it might change the decision, and the
value is how much better the decision gets on average.

Let $\alpha$ be the best action given current evidence $e$, with expected utility $EU(\alpha \mid e)$. Suppose we could
observe a variable $E_j$. If it came out as $e_{jk}$ we would choose the best action $\alpha_{jk}$ given $e$ and
$E_j = e_{jk}$. Before looking we do not know which value we will see, so we average over the possibilities. The
**value of perfect information** about $E_j$ is

$$
VPI_e(E_j) = \Big( \sum_k P(E_j = e_{jk} \mid e)\; EU(\alpha_{jk} \mid e, E_j = e_{jk}) \Big) - EU(\alpha \mid e).
$$

("Perfect" means that we learn the value of $E_j$ exactly; $E_j$ itself may be a noisy test.)

**By hand, for the spectrometer.** $P(\text{positive}) = 0.3 \cdot 0.8 + 0.7 \cdot 0.1 = 0.31$. Given positive,
$P(\text{mineral}) = 0.24/0.31 = 0.774$, so drill: $EU = 77.4 - 20 = 57.4$. Given negative ($P = 0.69$),
$P(\text{mineral}) = 0.06/0.69 = 0.087$, so drilling would give $8.7 - 20 < 0$: skip, $EU = 0$. With the test,
$EU = 0.31 \cdot 57.4 + 0.69 \cdot 0 = 17.8$. So $VPI = 17.8 - 10 = 7.8$. The test is worth doing if it costs less
than 7.8 points. The program prints the same numbers, plus:

- **Perfect information about the mineral itself** is worth 14: drill exactly when the mineral is there,
  $0.3 \cdot 80 = 24$, minus 10. No test can be worth more than that.
- **The camera** is worth 4.0, less than the spectrometer, because it discriminates less well.
- **Both tests together** are worth 8.64, less than the sum $7.8 + 4.0 = 11.8$. They tell us about the same thing, so
  the second adds less once we have the first.

### Properties of the value of information

**Theorem.** The value of information is never negative: $VPI_e(E_j) \ge 0$ for every $E_j$ and $e$.

**Proof.** Write $EU(a \mid e) = \sum_k P(e_{jk} \mid e)\, EU(a \mid e, e_{jk})$ (the law of total expectation: averaging
over what $E_j$ will turn out to be). Then

$$
EU(\alpha \mid e) = \max_a \sum_k P(e_{jk} \mid e)\, EU(a \mid e, e_{jk}) \le \sum_k P(e_{jk} \mid e) \max_a EU(a \mid e, e_{jk}),
$$

because the max of an average is at most the average of the maxes (each term in the left sum is at most the
corresponding term in the right sum, for any fixed $a$). The right side is the first term of the VPI formula.
$\square$

In words: an agent who can look first can always ignore what it sees and act as before, so looking cannot hurt **in
expectation**. (A particular observation can of course lead to a worse outcome; and information can hurt in games
against other agents, where others may react to what you know.)

Two more facts, both visible in the output:

- **Not additive.** In general $VPI(E_j, E_k) \ne VPI(E_j) + VPI(E_k)$. Redundant information is worth less than the sum
  (the two tests above). Complementary information can be worth more (Exercise 7).
- **Order independent.** $VPI(E_j, E_k) = VPI(E_j) + VPI_{E_j}(E_k) = VPI(E_k) + VPI_{E_k}(E_j)$: the value of getting
  both does not depend on the order, since it only depends on the final information.

A **myopic** information-gathering agent repeatedly makes the observation with the highest $VPI$ minus cost, if that
is positive, then acts. It is not optimal (two observations that are each worthless alone may be valuable together),
but it is a sound and much-used heuristic. On Mars this kind of reasoning is natural: each extra measurement costs time
and power, and a rover's operators must judge whether another image or spectrum would change what they do next.

## 14.3 Sequential decisions: Markov decision processes (Bellman 1957)

*Level: intermediate.*

So far, one decision, then the world ends. Most agents act again and again, and each action changes the situation in
which the next is taken. A robot's route is a sequence of moves; an investment plan is a sequence of choices. The
consequences of an action include the future choices it makes possible.

### The 4 by 3 world

The standard example (from Russell and Norvig) is a grid of 4 columns and 3 rows, with a wall at (2, 2). The agent starts
at (1, 1). Squares (4, 3) and (4, 2) are **terminal**: entering (4, 3) earns +1 and ends the game; entering (4, 2) earns
-1 and ends it. In every other square the agent receives a small **living reward** $r = -0.04$ (a cost per step). Each
move (North, East, South, West) goes in the intended direction with probability 0.8 and slips to each side, at right
angles, with probability 0.1; moving into a wall or the edge leaves the agent where it was.

If moves were certain, the plan Up, Up, Right, Right, Right would reach +1 in five steps. With slipping, it reaches +1
with probability only $0.8^5 + 0.1^4 \cdot 0.8 = 0.32776$ (the second term is the lucky way around the other side). A
fixed sequence is the wrong kind of answer. What the agent needs is a rule that says what to do **in whatever square it
finds itself**.

### Definitions

A **Markov decision process** (MDP) consists of

- a set of **states** $S$ with a start state;
- a set of **actions** $A(s)$ available in each state;
- a **transition model** $P(s' \mid s, a)$, Markov as in [Chapter 13](13-Reasoning-over-Time.md): the outcome depends
  only on the current state and action;
- a **reward function** $R(s)$ (or more generally $R(s, a, s')$), received in each state;
- a **discount factor** $\gamma \in [0, 1]$.

The state is **fully observable**: the agent always knows where it is. (14.6 removes this.) A **policy** $\pi$ is a
function from states to actions: $\pi(s)$ is what to do in $s$. Executing a policy from a start state produces a random
**history** of states; we want the policy whose histories are best on average.

### Utilities of histories; why discount

What is a history $s_0, s_1, s_2, \dots$ worth? Under mild assumptions (preferences between histories are stationary:
if two histories start with the same state, they are ranked as their tails are), there are only two possibilities
(Koopmans, 1960): additive rewards, or **discounted** rewards,

$$
U_h([s_0, s_1, s_2, \dots]) = R(s_0) + \gamma R(s_1) + \gamma^2 R(s_2) + \cdots,
$$

of which additive is the case $\gamma = 1$. The discount factor $\gamma < 1$ means a reward now is worth more than the
same reward later. Three reasons to use it:

- **It models reality.** A reward later is less certain (the robot may break, the mission may end); with probability
  $1 - \gamma$ per step that the process stops, the expected total reward is exactly the discounted sum.
- **It keeps sums finite.** If $|R(s)| \le R_{\max}$, then $|U_h| \le \sum_t \gamma^t R_{\max} = R_{\max}/(1 - \gamma)$,
  even for infinite histories.
- **It makes the mathematics work**, as the convergence proof below shows.

With $\gamma = 1$ we need another guarantee of finiteness: a **proper** policy, one that reaches a terminal state with
probability 1. In the 4 by 3 world every policy that does not stay forever in a corner is proper, and the code uses
$\gamma = 1$ there, as Russell and Norvig do.

### The utility of a state and the Bellman equation

The utility of a state under policy $\pi$ is the expected discounted reward from following $\pi$ starting there:

$$
U^\pi(s) = E\Big[ \sum_{t=0}^{\infty} \gamma^t R(S_t) \,\Big|\, S_0 = s, \pi \Big].
$$

The **optimal** utility is $U(s) = \max_\pi U^\pi(s)$. A remarkable fact (proved below via value iteration) is that one
policy is optimal from every state at once; it is the policy that is greedy with respect to $U$:

$$
\pi^*(s) = \arg\max_{a} \sum_{s'} P(s' \mid s, a)\, U(s').
$$

To be greedy you only need $U$. And $U$ satisfies a self-consistency condition. The utility of a state is the reward
there plus the discounted expected utility of the next state, if you then act optimally:

$$
U(s) = R(s) + \gamma \max_{a} \sum_{s'} P(s' \mid s, a)\, U(s').
$$

This is the **Bellman equation**, after Richard Bellman, whose 1957 book *Dynamic Programming* developed this theory
(the name "dynamic programming" is his too). For $n$ states it is a system of $n$ equations in $n$ unknowns, but not
linear, because of the max. We cannot solve it with linear algebra directly. We can iterate.

The same equation for a fixed policy has no max and **is** linear:

$$
U^\pi(s) = R(s) + \gamma \sum_{s'} P(s' \mid s, \pi(s))\, U^\pi(s').
$$

## 14.4 Value iteration, convergence proved (contraction); policy iteration

*Level: intermediate (the proofs are advanced).*

### Value iteration

Start with any utilities, say $U_0 = 0$, and apply the right-hand side of the Bellman equation as an update:

$$
U_{i+1}(s) \leftarrow R(s) + \gamma \max_{a} \sum_{s'} P(s' \mid s, a)\, U_i(s') \quad \text{for every } s.
$$

Call this map $B$, the **Bellman update**: $U_{i+1} = B U_i$. **Value iteration** applies $B$ until the utilities stop
changing much, then returns the greedy policy. Each sweep costs $O(|S|^2 |A|)$ in general, or $O(|S||A|k)$ if each
action has at most $k$ possible outcomes.

A meaning for the iterates: $U_i(s)$ is the best expected reward obtainable in exactly $i$ steps from $s$ (counting the
reward in $s$ itself), with nothing after. Value iteration builds longer and longer horizons, the dynamic programming
idea from the Algorithms book's [Chapter 13](../algorithms/13-Dynamic-Programming.md).

**One sweep by hand.** In the 4 by 3 world with $U_0 = 0$, the first sweep gives $U_1(s) = -0.04$ for every
non-terminal square (and $\pm 1$ at the terminals). In the second sweep, from (3, 3) the best action is East: 0.8 to
(4, 3) worth 1, 0.1 North (bump, stay) worth $-0.04$, 0.1 South to (3, 2) worth $-0.04$. So
$U_2(3, 3) = -0.04 + 0.8 - 0.004 - 0.004 = 0.752$. Good news spreads backwards from the goal one square per sweep.

### The contraction theorem

The **max norm** of a utility vector is $\|U\| = \max_s |U(s)|$, the largest absolute entry. The distance between two
utility vectors is $\|U - U'\|$, the largest difference at any state.

**Theorem.** For $\gamma < 1$ the Bellman update is a **contraction** by a factor $\gamma$ in the max norm: for any two
utility vectors $U$ and $U'$,

$$
\|BU - BU'\| \le \gamma \|U - U'\|.
$$

**Proof.** First a lemma: for any two functions $f, g$ of $a$, $|\max_a f(a) - \max_a g(a)| \le \max_a |f(a) - g(a)|$.
(Suppose $\max f \ge \max g$, and let $a^*$ maximise $f$. Then
$\max f - \max g \le f(a^*) - g(a^*) \le \max_a |f(a) - g(a)|$; the other case is symmetric.) Now fix a state $s$.
The reward terms cancel:

$$
\begin{aligned}
|BU(s) - BU'(s)| &= \gamma \Big| \max_a \sum_{s'} P(s' \mid s, a) U(s') - \max_a \sum_{s'} P(s' \mid s, a) U'(s') \Big| \\
&\le \gamma \max_a \Big| \sum_{s'} P(s' \mid s, a) \big(U(s') - U'(s')\big) \Big| \\
&\le \gamma \max_a \sum_{s'} P(s' \mid s, a) \|U - U'\| = \gamma \|U - U'\|.
\end{aligned}
$$

The last step uses that the probabilities sum to 1, so a weighted average of numbers no bigger than $\|U - U'\|$ is no
bigger than $\|U - U'\|$. Take the max over $s$. $\square$

**Consequences.**

1. **A unique fixed point.** By the Banach fixed-point theorem (a contraction on a complete metric space, here
   $\mathbb{R}^{|S|}$ with the max norm, has exactly one fixed point), the Bellman equation has exactly one solution $U$.
   Uniqueness also follows directly: if $BU = U$ and $BU' = U'$, then $\|U - U'\| \le \gamma \|U - U'\|$ forces $U = U'$.
2. **Geometric convergence.** Since $BU = U$, $\|U_{i+1} - U\| = \|BU_i - BU\| \le \gamma \|U_i - U\|$, so
   $\|U_i - U\| \le \gamma^i \|U_0 - U\|$. Starting from $U_0 = 0$, $\|U_0 - U\| \le R_{\max}/(1 - \gamma)$, so to get
   within $\epsilon$ it suffices that $\gamma^i R_{\max}/(1-\gamma) \le \epsilon$. Allowing a factor 2 of slack (for a
   start anywhere in the same range), the standard bound is
   $N = \lceil \log\big(2R_{\max}/(\epsilon(1-\gamma))\big) / \log(1/\gamma) \rceil$ sweeps.
3. **A stopping rule you can check.** We do not know $U$, but we see successive iterates. If
   $\|U_{i+1} - U_i\| < \epsilon(1-\gamma)/\gamma$, then $\|U_{i+1} - U\| < \epsilon$. Proof: by the triangle inequality and
   contraction, $\|U_{i+1} - U\| \le \|U_{i+2} - U_{i+1}\| + \|U_{i+3} - U_{i+2}\| + \cdots \le
   (\gamma + \gamma^2 + \cdots)\|U_{i+1} - U_i\| = \frac{\gamma}{1-\gamma}\|U_{i+1} - U_i\| < \epsilon$.
4. **The policy is good before the values are exact.** If $\|U_i - U\| < \epsilon$, the greedy policy $\pi_i$ satisfies
   $\|U^{\pi_i} - U\| < 2\epsilon\gamma/(1 - \gamma)$ (Williams and Baird, 1993). In practice the greedy policy is often
   optimal long before the utilities converge.

Notice that $N$ grows like $1/(1-\gamma)$ for $\gamma$ near 1 (since $\log(1/\gamma) \approx 1 - \gamma$): long
horizons are expensive. For $\gamma = 1$ the theorem does not apply, but value iteration still converges when all
policies are proper, as in the 4 by 3 world.

### Policy iteration

Value iteration improves utilities and lets the policy follow. **Policy iteration** (Howard, 1960) improves the policy
directly, alternating two steps until the policy stops changing:

1. **Policy evaluation:** compute $U^{\pi_i}$, the utilities of the current policy, by solving the **linear** system
   $U = R + \gamma P_{\pi_i} U$, where $P_{\pi_i}$ is the matrix of transition probabilities under $\pi_i$. With $n$
   states this costs $O(n^3)$ by Gaussian elimination.
2. **Policy improvement:** make the policy greedy with respect to those utilities:
   $\pi_{i+1}(s) = \arg\max_a \sum_{s'} P(s' \mid s, a)\, U^{\pi_i}(s')$, keeping the old action when it is tied for best.

**Theorem (policy improvement).** $U^{\pi_{i+1}}(s) \ge U^{\pi_i}(s)$ for every state. If the policy does not change,
it is optimal.

**Proof.** By construction of $\pi_{i+1}$, for every $s$,
$R(s) + \gamma \sum_{s'} P(s' \mid s, \pi_{i+1}(s)) U^{\pi_i}(s') \ge R(s) + \gamma \sum_{s'} P(s' \mid s, \pi_i(s)) U^{\pi_i}(s') =
U^{\pi_i}(s)$. In operator form, $B_{\pi_{i+1}} U^{\pi_i} \ge U^{\pi_i}$, where $B_\pi$ is the Bellman update for the
fixed policy $\pi$. $B_\pi$ is monotone (if $U \ge U'$ entrywise, then $B_\pi U \ge B_\pi U'$, as the probabilities are
non-negative), so applying it repeatedly gives
$U^{\pi_i} \le B_{\pi_{i+1}} U^{\pi_i} \le B_{\pi_{i+1}}^2 U^{\pi_i} \le \cdots \to U^{\pi_{i+1}}$, since iterating
$B_{\pi_{i+1}}$ converges to its fixed point $U^{\pi_{i+1}}$ (it is a contraction too). If the policy does not change,
then $U^{\pi_i}$ satisfies the Bellman equation with the max, so it is the unique solution $U$, and $\pi_i$ is optimal.
$\square$

**Termination.** Each round either strictly improves the utility of some state or stops. A policy can never repeat
(utilities only go up, and strictly for some state until the end), and there are finitely many policies, at most
$|A|^{|S|}$. So policy iteration stops after finitely many rounds with an optimal policy. The worst-case number of
rounds is a subtle question; in practice it is small (5 rounds for the 4 by 3 world below), and each round costs a
linear solve.

**Variants.** **Modified policy iteration** evaluates the policy approximately, with a few sweeps of the simplified
Bellman update instead of an exact solve. **Asynchronous** value iteration updates states one at a time in any order;
it still converges if every state is updated infinitely often, and it lets computation focus on the states that matter
(the idea behind real-time dynamic programming and, in [Chapter 15](15-Reinforcement-Learning.md), behind learning from
experience). Finally, an MDP can be written as a **linear program** and solved in polynomial time; Papadimitriou and
Tsitsiklis (1987) showed that solving MDPs is P-complete, so they are among the "easy" problems, though large state
spaces make them hard in practice.

## 14.5 Grid world solved from scratch, pictures of the policy

The program builds the 4 by 3 world, runs value iteration and policy iteration, solves it for several living rewards,
and measures the contraction on a discounted version.

```python
--8<-- "books/ai/ch14_mdp.py"
```

```
r = -0.04, gamma = 1: value iteration converged in 30 sweeps
    >   0.812 | >   0.868 | >   0.918 |   +1      
    ^   0.762 |    ####   | ^   0.660 |   -1      
    ^   0.705 | <   0.655 | <   0.611 | <   0.388 
policy iteration: 5 rounds, same policy: True, max difference in values 4.17e-07

the policy for other living rewards r (gamma = 1)
r = -2.0
    >  -7.043 | >  -4.230 | >  -1.730 |   +1      
    ^  -9.543 |    ####   | >  -3.570 |   -1      
    > -10.815 | >  -8.474 | >  -5.974 | ^  -3.775 
r = -0.4
    >  -0.638 | >  -0.075 | >   0.425 |   +1      
    ^  -1.138 |    ####   | ^  -0.178 |   -1      
    ^  -1.600 | >  -1.299 | ^  -0.799 | <  -1.266 
r = -0.01
    >   0.950 | >   0.964 | >   0.976 |   +1      
    ^   0.937 |    ####   | <   0.887 |   -1      
    ^   0.923 | <   0.911 | <   0.897 | v   0.797 
r = 0.0 (gamma 0.999)
    >   0.995 | >   0.996 | >   0.998 |   +1      
    ^   0.994 |    ####   | <   0.989 |   -1      
    ^   0.992 | <   0.991 | <   0.990 | v   0.980 

contraction: gamma = 0.9, r = -0.04; error ||U_i - U*|| and the ratio between successive errors
  i=0   error 1.000000
  i=1   error 0.835362   ratio to previous 0.8354   bound 0.9^i * error_0 = 0.900000
  i=2   error 0.725586   ratio to previous 0.8686   bound 0.9^i * error_0 = 0.810000
  i=3   error 0.617816   ratio to previous 0.8515   bound 0.9^i * error_0 = 0.729000
  i=5   error 0.460271   ratio to previous 0.8586   bound 0.9^i * error_0 = 0.590490
  i=10  error 0.013269   ratio to previous 0.4415   bound 0.9^i * error_0 = 0.348678
  i=20  error 0.000002   ratio to previous 0.4078   bound 0.9^i * error_0 = 0.121577
  i=40  error 0.000000   ratio to previous 0.3044   bound 0.9^i * error_0 = 0.014781
```

<figure class="mars-fig" markdown="0">
<svg viewBox="0 0 520 290" role="img" aria-label="The 4 by 3 grid world with the optimal policy for living reward minus 0.04. Top row: right, right, right to plus 1, with utilities 0.812, 0.868, 0.918. Middle row: up at (1,2) with 0.762, the wall, up at (3,2) with 0.660, then minus 1. Bottom row: up at (1,1) with 0.705, then left, left, left with 0.655, 0.611, 0.388.">
<rect x="60" y="20" width="110" height="80" fill="#9cc9ea" fill-opacity="0.15" stroke="currentColor" stroke-width="1"/>
<text x="115.0" y="56.0" font-size="20" text-anchor="middle" fill="currentColor">→</text>
<text x="115.0" y="78.0" font-size="13" text-anchor="middle" fill="currentColor">0.812</text>
<rect x="170" y="20" width="110" height="80" fill="#9cc9ea" fill-opacity="0.15" stroke="currentColor" stroke-width="1"/>
<text x="225.0" y="56.0" font-size="20" text-anchor="middle" fill="currentColor">→</text>
<text x="225.0" y="78.0" font-size="13" text-anchor="middle" fill="currentColor">0.868</text>
<rect x="280" y="20" width="110" height="80" fill="#9cc9ea" fill-opacity="0.15" stroke="currentColor" stroke-width="1"/>
<text x="335.0" y="56.0" font-size="20" text-anchor="middle" fill="currentColor">→</text>
<text x="335.0" y="78.0" font-size="13" text-anchor="middle" fill="currentColor">0.918</text>
<rect x="390" y="20" width="110" height="80" fill="#7ccf9a" fill-opacity="0.6" stroke="currentColor" stroke-width="1"/>
<text x="445.0" y="66.0" font-size="18" text-anchor="middle" fill="currentColor">+1</text>
<rect x="60" y="100" width="110" height="80" fill="#9cc9ea" fill-opacity="0.15" stroke="currentColor" stroke-width="1"/>
<text x="115.0" y="136.0" font-size="20" text-anchor="middle" fill="currentColor">↑</text>
<text x="115.0" y="158.0" font-size="13" text-anchor="middle" fill="currentColor">0.762</text>
<rect x="170" y="100" width="110" height="80" fill="currentColor" fill-opacity="0.35" stroke="currentColor" stroke-width="1"/>
<rect x="280" y="100" width="110" height="80" fill="#9cc9ea" fill-opacity="0.15" stroke="currentColor" stroke-width="1"/>
<text x="335.0" y="136.0" font-size="20" text-anchor="middle" fill="currentColor">↑</text>
<text x="335.0" y="158.0" font-size="13" text-anchor="middle" fill="currentColor">0.660</text>
<rect x="390" y="100" width="110" height="80" fill="#eea66f" fill-opacity="0.6" stroke="currentColor" stroke-width="1"/>
<text x="445.0" y="146.0" font-size="18" text-anchor="middle" fill="currentColor">-1</text>
<rect x="60" y="180" width="110" height="80" fill="#9cc9ea" fill-opacity="0.15" stroke="currentColor" stroke-width="1"/>
<text x="115.0" y="216.0" font-size="20" text-anchor="middle" fill="currentColor">↑</text>
<text x="115.0" y="238.0" font-size="13" text-anchor="middle" fill="currentColor">0.705</text>
<rect x="170" y="180" width="110" height="80" fill="#9cc9ea" fill-opacity="0.15" stroke="currentColor" stroke-width="1"/>
<text x="225.0" y="216.0" font-size="20" text-anchor="middle" fill="currentColor">←</text>
<text x="225.0" y="238.0" font-size="13" text-anchor="middle" fill="currentColor">0.655</text>
<rect x="280" y="180" width="110" height="80" fill="#9cc9ea" fill-opacity="0.15" stroke="currentColor" stroke-width="1"/>
<text x="335.0" y="216.0" font-size="20" text-anchor="middle" fill="currentColor">←</text>
<text x="335.0" y="238.0" font-size="13" text-anchor="middle" fill="currentColor">0.611</text>
<rect x="390" y="180" width="110" height="80" fill="#9cc9ea" fill-opacity="0.15" stroke="currentColor" stroke-width="1"/>
<text x="445.0" y="216.0" font-size="20" text-anchor="middle" fill="currentColor">←</text>
<text x="445.0" y="238.0" font-size="13" text-anchor="middle" fill="currentColor">0.388</text>
<text x="115" y="278" font-size="13" text-anchor="middle" fill="currentColor">1</text>
<text x="225" y="278" font-size="13" text-anchor="middle" fill="currentColor">2</text>
<text x="335" y="278" font-size="13" text-anchor="middle" fill="currentColor">3</text>
<text x="445" y="278" font-size="13" text-anchor="middle" fill="currentColor">4</text>
<text x="45" y="65" font-size="13" text-anchor="middle" fill="currentColor">3</text>
<text x="45" y="145" font-size="13" text-anchor="middle" fill="currentColor">2</text>
<text x="45" y="225" font-size="13" text-anchor="middle" fill="currentColor">1</text>
</svg>
<figcaption>The optimal policy and utilities for r = -0.04 (γ = 1). The arrows show what to do in each square; the
numbers are the expected total reward from there. Note (3, 1) and (4, 1): the policy goes the long way round, left and
up, rather than risk slipping into -1.</figcaption>
</figure>

Reading the results:

- **The utilities match the published ones** for this world (Russell and Norvig give 0.705 for the start square and
  0.388 for (4, 1)). Value iteration needs 30 sweeps to change by less than $10^{-6}$; policy iteration reaches the same
  policy in 5 rounds, and its exactly solved values agree to $4 \times 10^{-7}$.
- **The policy trades risk against delay.** From (3, 2), next to -1, it goes North: that move slips East into -1 with
  probability 0.1, but usually reaches (3, 3), next to the goal. The safe alternative, West into the wall, can never
  reach -1 (its slips go North or South) but usually wastes a step. At $r = -0.04$ the shorter route is worth the risk.
  From (4, 1), where North would enter -1 with probability 0.8, the policy goes West, the long way round.
- **The living reward changes everything** (figure below). At $r = -2$ life is so painful that the agent heads for
  the nearest exit, even -1: from (3, 2) it goes straight East into -1, and from (4, 1) it goes North into -1. At
  $r = -0.4$ it takes the shortest route to +1 and accepts the risk of -1. At $r = -0.04$ it is cautious. At
  $r = -0.01$ it is very cautious: from (3, 2) it goes West, banging into the wall, and from (4, 1) it goes South into
  the edge; both actions have **zero** chance of reaching -1 (the slips go sideways, along the wall), and the time lost
  costs almost nothing. With $r = 0$ (here with $\gamma = 0.999$ so values stay finite) the same holds even more.
- **Contraction in action.** With $\gamma = 0.9$, the error after $i$ sweeps is always below the bound
  $0.9^i \cdot \text{error}_0$, and the actual ratios are smaller still, about 0.85 at first and about 0.4 later, once
  the values near the terminals have settled.

<figure class="mars-fig" markdown="0">
<svg viewBox="0 0 640 135" role="img" aria-label="Four small grids showing the optimal policy for living rewards minus 2, minus 0.4, minus 0.04 and minus 0.01. As the reward becomes less negative, the policy changes from rushing to the nearest exit, to the short risky route, to cautious detours, to never risking the minus 1 square at all.">
<rect x="10" y="30" width="35" height="32" fill="#9cc9ea" fill-opacity="0.15" stroke="currentColor" stroke-width="1"/>
<text x="27.5" y="52.0" font-size="17" text-anchor="middle" fill="currentColor">→</text>
<rect x="45" y="30" width="35" height="32" fill="#9cc9ea" fill-opacity="0.15" stroke="currentColor" stroke-width="1"/>
<text x="62.5" y="52.0" font-size="17" text-anchor="middle" fill="currentColor">→</text>
<rect x="80" y="30" width="35" height="32" fill="#9cc9ea" fill-opacity="0.15" stroke="currentColor" stroke-width="1"/>
<text x="97.5" y="52.0" font-size="17" text-anchor="middle" fill="currentColor">→</text>
<rect x="115" y="30" width="35" height="32" fill="#7ccf9a" fill-opacity="0.6" stroke="currentColor" stroke-width="1"/>
<text x="132.5" y="52.0" font-size="15" text-anchor="middle" fill="currentColor">+1</text>
<rect x="10" y="62" width="35" height="32" fill="#9cc9ea" fill-opacity="0.15" stroke="currentColor" stroke-width="1"/>
<text x="27.5" y="84.0" font-size="17" text-anchor="middle" fill="currentColor">↑</text>
<rect x="45" y="62" width="35" height="32" fill="currentColor" fill-opacity="0.35" stroke="currentColor" stroke-width="1"/>
<rect x="80" y="62" width="35" height="32" fill="#9cc9ea" fill-opacity="0.15" stroke="currentColor" stroke-width="1"/>
<text x="97.5" y="84.0" font-size="17" text-anchor="middle" fill="currentColor">→</text>
<rect x="115" y="62" width="35" height="32" fill="#eea66f" fill-opacity="0.6" stroke="currentColor" stroke-width="1"/>
<text x="132.5" y="84.0" font-size="15" text-anchor="middle" fill="currentColor">-1</text>
<rect x="10" y="94" width="35" height="32" fill="#9cc9ea" fill-opacity="0.15" stroke="currentColor" stroke-width="1"/>
<text x="27.5" y="116.0" font-size="17" text-anchor="middle" fill="currentColor">→</text>
<rect x="45" y="94" width="35" height="32" fill="#9cc9ea" fill-opacity="0.15" stroke="currentColor" stroke-width="1"/>
<text x="62.5" y="116.0" font-size="17" text-anchor="middle" fill="currentColor">→</text>
<rect x="80" y="94" width="35" height="32" fill="#9cc9ea" fill-opacity="0.15" stroke="currentColor" stroke-width="1"/>
<text x="97.5" y="116.0" font-size="17" text-anchor="middle" fill="currentColor">→</text>
<rect x="115" y="94" width="35" height="32" fill="#9cc9ea" fill-opacity="0.15" stroke="currentColor" stroke-width="1"/>
<text x="132.5" y="116.0" font-size="17" text-anchor="middle" fill="currentColor">↑</text>
<text x="80" y="20" font-size="13" text-anchor="middle" fill="currentColor">r = -2</text>
<rect x="168" y="30" width="35" height="32" fill="#9cc9ea" fill-opacity="0.15" stroke="currentColor" stroke-width="1"/>
<text x="185.5" y="52.0" font-size="17" text-anchor="middle" fill="currentColor">→</text>
<rect x="203" y="30" width="35" height="32" fill="#9cc9ea" fill-opacity="0.15" stroke="currentColor" stroke-width="1"/>
<text x="220.5" y="52.0" font-size="17" text-anchor="middle" fill="currentColor">→</text>
<rect x="238" y="30" width="35" height="32" fill="#9cc9ea" fill-opacity="0.15" stroke="currentColor" stroke-width="1"/>
<text x="255.5" y="52.0" font-size="17" text-anchor="middle" fill="currentColor">→</text>
<rect x="273" y="30" width="35" height="32" fill="#7ccf9a" fill-opacity="0.6" stroke="currentColor" stroke-width="1"/>
<text x="290.5" y="52.0" font-size="15" text-anchor="middle" fill="currentColor">+1</text>
<rect x="168" y="62" width="35" height="32" fill="#9cc9ea" fill-opacity="0.15" stroke="currentColor" stroke-width="1"/>
<text x="185.5" y="84.0" font-size="17" text-anchor="middle" fill="currentColor">↑</text>
<rect x="203" y="62" width="35" height="32" fill="currentColor" fill-opacity="0.35" stroke="currentColor" stroke-width="1"/>
<rect x="238" y="62" width="35" height="32" fill="#9cc9ea" fill-opacity="0.15" stroke="currentColor" stroke-width="1"/>
<text x="255.5" y="84.0" font-size="17" text-anchor="middle" fill="currentColor">↑</text>
<rect x="273" y="62" width="35" height="32" fill="#eea66f" fill-opacity="0.6" stroke="currentColor" stroke-width="1"/>
<text x="290.5" y="84.0" font-size="15" text-anchor="middle" fill="currentColor">-1</text>
<rect x="168" y="94" width="35" height="32" fill="#9cc9ea" fill-opacity="0.15" stroke="currentColor" stroke-width="1"/>
<text x="185.5" y="116.0" font-size="17" text-anchor="middle" fill="currentColor">↑</text>
<rect x="203" y="94" width="35" height="32" fill="#9cc9ea" fill-opacity="0.15" stroke="currentColor" stroke-width="1"/>
<text x="220.5" y="116.0" font-size="17" text-anchor="middle" fill="currentColor">→</text>
<rect x="238" y="94" width="35" height="32" fill="#9cc9ea" fill-opacity="0.15" stroke="currentColor" stroke-width="1"/>
<text x="255.5" y="116.0" font-size="17" text-anchor="middle" fill="currentColor">↑</text>
<rect x="273" y="94" width="35" height="32" fill="#9cc9ea" fill-opacity="0.15" stroke="currentColor" stroke-width="1"/>
<text x="290.5" y="116.0" font-size="17" text-anchor="middle" fill="currentColor">←</text>
<text x="238" y="20" font-size="13" text-anchor="middle" fill="currentColor">r = -0.4</text>
<rect x="326" y="30" width="35" height="32" fill="#9cc9ea" fill-opacity="0.15" stroke="currentColor" stroke-width="1"/>
<text x="343.5" y="52.0" font-size="17" text-anchor="middle" fill="currentColor">→</text>
<rect x="361" y="30" width="35" height="32" fill="#9cc9ea" fill-opacity="0.15" stroke="currentColor" stroke-width="1"/>
<text x="378.5" y="52.0" font-size="17" text-anchor="middle" fill="currentColor">→</text>
<rect x="396" y="30" width="35" height="32" fill="#9cc9ea" fill-opacity="0.15" stroke="currentColor" stroke-width="1"/>
<text x="413.5" y="52.0" font-size="17" text-anchor="middle" fill="currentColor">→</text>
<rect x="431" y="30" width="35" height="32" fill="#7ccf9a" fill-opacity="0.6" stroke="currentColor" stroke-width="1"/>
<text x="448.5" y="52.0" font-size="15" text-anchor="middle" fill="currentColor">+1</text>
<rect x="326" y="62" width="35" height="32" fill="#9cc9ea" fill-opacity="0.15" stroke="currentColor" stroke-width="1"/>
<text x="343.5" y="84.0" font-size="17" text-anchor="middle" fill="currentColor">↑</text>
<rect x="361" y="62" width="35" height="32" fill="currentColor" fill-opacity="0.35" stroke="currentColor" stroke-width="1"/>
<rect x="396" y="62" width="35" height="32" fill="#9cc9ea" fill-opacity="0.15" stroke="currentColor" stroke-width="1"/>
<text x="413.5" y="84.0" font-size="17" text-anchor="middle" fill="currentColor">↑</text>
<rect x="431" y="62" width="35" height="32" fill="#eea66f" fill-opacity="0.6" stroke="currentColor" stroke-width="1"/>
<text x="448.5" y="84.0" font-size="15" text-anchor="middle" fill="currentColor">-1</text>
<rect x="326" y="94" width="35" height="32" fill="#9cc9ea" fill-opacity="0.15" stroke="currentColor" stroke-width="1"/>
<text x="343.5" y="116.0" font-size="17" text-anchor="middle" fill="currentColor">↑</text>
<rect x="361" y="94" width="35" height="32" fill="#9cc9ea" fill-opacity="0.15" stroke="currentColor" stroke-width="1"/>
<text x="378.5" y="116.0" font-size="17" text-anchor="middle" fill="currentColor">←</text>
<rect x="396" y="94" width="35" height="32" fill="#9cc9ea" fill-opacity="0.15" stroke="currentColor" stroke-width="1"/>
<text x="413.5" y="116.0" font-size="17" text-anchor="middle" fill="currentColor">←</text>
<rect x="431" y="94" width="35" height="32" fill="#9cc9ea" fill-opacity="0.15" stroke="currentColor" stroke-width="1"/>
<text x="448.5" y="116.0" font-size="17" text-anchor="middle" fill="currentColor">←</text>
<text x="396" y="20" font-size="13" text-anchor="middle" fill="currentColor">r = -0.04</text>
<rect x="484" y="30" width="35" height="32" fill="#9cc9ea" fill-opacity="0.15" stroke="currentColor" stroke-width="1"/>
<text x="501.5" y="52.0" font-size="17" text-anchor="middle" fill="currentColor">→</text>
<rect x="519" y="30" width="35" height="32" fill="#9cc9ea" fill-opacity="0.15" stroke="currentColor" stroke-width="1"/>
<text x="536.5" y="52.0" font-size="17" text-anchor="middle" fill="currentColor">→</text>
<rect x="554" y="30" width="35" height="32" fill="#9cc9ea" fill-opacity="0.15" stroke="currentColor" stroke-width="1"/>
<text x="571.5" y="52.0" font-size="17" text-anchor="middle" fill="currentColor">→</text>
<rect x="589" y="30" width="35" height="32" fill="#7ccf9a" fill-opacity="0.6" stroke="currentColor" stroke-width="1"/>
<text x="606.5" y="52.0" font-size="15" text-anchor="middle" fill="currentColor">+1</text>
<rect x="484" y="62" width="35" height="32" fill="#9cc9ea" fill-opacity="0.15" stroke="currentColor" stroke-width="1"/>
<text x="501.5" y="84.0" font-size="17" text-anchor="middle" fill="currentColor">↑</text>
<rect x="519" y="62" width="35" height="32" fill="currentColor" fill-opacity="0.35" stroke="currentColor" stroke-width="1"/>
<rect x="554" y="62" width="35" height="32" fill="#9cc9ea" fill-opacity="0.15" stroke="currentColor" stroke-width="1"/>
<text x="571.5" y="84.0" font-size="17" text-anchor="middle" fill="currentColor">←</text>
<rect x="589" y="62" width="35" height="32" fill="#eea66f" fill-opacity="0.6" stroke="currentColor" stroke-width="1"/>
<text x="606.5" y="84.0" font-size="15" text-anchor="middle" fill="currentColor">-1</text>
<rect x="484" y="94" width="35" height="32" fill="#9cc9ea" fill-opacity="0.15" stroke="currentColor" stroke-width="1"/>
<text x="501.5" y="116.0" font-size="17" text-anchor="middle" fill="currentColor">↑</text>
<rect x="519" y="94" width="35" height="32" fill="#9cc9ea" fill-opacity="0.15" stroke="currentColor" stroke-width="1"/>
<text x="536.5" y="116.0" font-size="17" text-anchor="middle" fill="currentColor">←</text>
<rect x="554" y="94" width="35" height="32" fill="#9cc9ea" fill-opacity="0.15" stroke="currentColor" stroke-width="1"/>
<text x="571.5" y="116.0" font-size="17" text-anchor="middle" fill="currentColor">←</text>
<rect x="589" y="94" width="35" height="32" fill="#9cc9ea" fill-opacity="0.15" stroke="currentColor" stroke-width="1"/>
<text x="606.5" y="116.0" font-size="17" text-anchor="middle" fill="currentColor">↓</text>
<text x="554" y="20" font-size="13" text-anchor="middle" fill="currentColor">r = -0.01</text>
</svg>
<figcaption>The optimal policy as the living reward r changes (γ = 1). From left to right the agent goes from desperate
(any exit will do) to bold (short route) to cautious (detour) to safe at any cost (bump into walls rather than risk -1).
Same world, same transition model: only the reward differs, which is why choosing the reward is the real design
decision.</figcaption>
</figure>

<figure class="mars-fig" markdown="0">
<svg viewBox="0 0 700 270" role="img" aria-label="Plot of value-iteration utilities over 30 sweeps for four squares of the 4 by 3 world. All start at zero and dip slightly; (3,3) rises first, at sweep 2, towards 0.918; (3,1) at sweep 4 towards 0.611; (4,1) at sweep 5 and converges slowest, to 0.388; (1,1) at sweep 6 towards 0.705.">
<line x1="70" y1="230" x2="610" y2="230" stroke="currentColor" stroke-width="1.2"/>
<line x1="70" y1="230" x2="70" y2="30" stroke="currentColor" stroke-width="1.2"/>
<line x1="70" y1="185" x2="610" y2="185" stroke="currentColor" stroke-width="0.6" stroke-dasharray="3 3"/>
<text x="62" y="219" font-size="12" text-anchor="end" fill="currentColor">-0.2</text>
<text x="62" y="189" font-size="12" text-anchor="end" fill="currentColor">0</text>
<text x="62" y="129" font-size="12" text-anchor="end" fill="currentColor">0.4</text>
<text x="62" y="69" font-size="12" text-anchor="end" fill="currentColor">0.8</text>
<text x="62" y="39" font-size="12" text-anchor="end" fill="currentColor">1.0</text>
<text x="70" y="248" font-size="12" text-anchor="middle" fill="currentColor">0</text>
<text x="250" y="248" font-size="12" text-anchor="middle" fill="currentColor">10</text>
<text x="430" y="248" font-size="12" text-anchor="middle" fill="currentColor">20</text>
<text x="610" y="248" font-size="12" text-anchor="middle" fill="currentColor">30</text>
<text x="340" y="265" font-size="12" text-anchor="middle" fill="currentColor">sweeps of value iteration</text>
<polyline fill="none" stroke="#7ccf9a" stroke-width="2.2" points="70,185.0 88,191.0 106,72.2 124,60.9 142,51.8 160,49.2 178,48.0 196,47.6 214,47.4 232,47.4 250,47.3 268,47.3 286,47.3 304,47.3 322,47.3 340,47.3 358,47.3 376,47.3 394,47.3 412,47.3 430,47.3 448,47.3 466,47.3 484,47.3 502,47.3 520,47.3 538,47.3 556,47.3 574,47.3 592,47.3 610,47.3"/>
<polyline fill="none" stroke="#eea66f" stroke-width="2.2" points="70,185.0 88,191.0 106,197.0 124,203.0 142,209.0 160,215.0 178,164.4 196,129.5 214,106.6 232,94.2 250,87.6 268,83.9 286,81.7 304,80.5 322,79.9 340,79.5 358,79.4 376,79.3 394,79.2 412,79.2 430,79.2 448,79.2 466,79.2 484,79.2 502,79.2 520,79.2 538,79.2 556,79.2 574,79.2 592,79.2 610,79.2"/>
<polyline fill="none" stroke="#9cc9ea" stroke-width="2.2" points="70,185.0 88,191.0 106,197.0 124,203.0 142,140.2 160,127.7 178,112.0 196,106.3 214,102.2 232,100.5 250,99.5 268,98.5 286,97.7 304,97.2 322,96.2 340,94.9 358,94.1 376,93.7 394,93.5 412,93.4 430,93.3 448,93.3 466,93.3 484,93.3 502,93.3 520,93.3 538,93.3 556,93.3 574,93.3 592,93.3 610,93.3"/>
<polyline fill="none" stroke="currentColor" stroke-width="2.2" stroke-dasharray="6 3" points="70,185.0 88,191.0 106,197.0 124,203.0 142,209.0 160,172.5 178,158.9 196,145.0 214,139.0 232,135.2 250,133.4 268,132.4 286,131.5 304,130.8 322,130.3 340,129.5 358,128.4 376,127.6 394,127.2 412,127.0 430,126.9 448,126.9 466,126.8 484,126.8 502,126.8 520,126.8 538,126.8 556,126.8 574,126.8 592,126.8 610,126.8"/>
<text x="618" y="51" font-size="13" fill="currentColor">(3,3) 0.918</text>
<text x="618" y="83" font-size="13" fill="currentColor">(1,1) 0.705</text>
<text x="618" y="99" font-size="13" fill="currentColor">(3,1) 0.611</text>
<text x="618" y="131" font-size="13" fill="currentColor">(4,1) 0.388</text>
</svg>
<figcaption>Utilities during value iteration (r = -0.04, γ = 1, starting from 0). Each square's value falls by 0.04
per sweep until news of the +1 reaches it, then rises: (3, 3), one step from the goal, after 2 sweeps; (1, 1), five
steps away, after 6. Far squares converge last.</figcaption>
</figure>

<figure class="play" data-play="gridvalue"><span class="ai-tag">AI-created</span><figcaption><b>Try it.</b> Value iteration on a small made-up grid world: add sweeps and watch values spread from the goal and the pit; raise the cost of moving and see the policy take risks to finish sooner.</figcaption></figure>

## 14.6 POMDPs and belief-state MDPs

*Level: advanced.*

An MDP agent always knows its state. A rover with a noisy position estimate, a doctor who sees symptoms and not the
disease, a robot hunting for an object in a cluttered room do not. A **partially observable MDP** (POMDP) adds to an MDP
a **sensor model** $P(o \mid s')$ (or $P(o \mid s', a)$): after each action the agent receives an observation $o$ that
depends on the new state. The agent never sees the state itself.

### Policies on beliefs

What should a policy depend on, if not the state? The agent's knowledge is summarised by its **belief state** $b$, the
probability distribution over states given all actions and observations so far, exactly the filtered distribution of
[Chapter 13](13-Reasoning-over-Time.md). After action $a$ and observation $o$ the belief is updated by the filtering
equation:

$$
b'(s') = \alpha\, P(o \mid s') \sum_{s} P(s' \mid s, a)\, b(s).
$$

The crucial observation (Åström, 1965; Smallwood and Sondik, 1973) is that the belief state is a **sufficient
statistic**: the optimal action depends only on $b$, not on the details of the history. So a POMDP is an MDP whose
states are beliefs:

- the **belief-state MDP** has states $b$ (points in the probability simplex, a continuous space);
- taking $a$ in $b$ leads to belief $b'_{a,o}$ with probability $P(o \mid a, b) = \sum_{s'} P(o \mid s') \sum_s P(s' \mid s, a) b(s)$;
- the reward is the expected reward $\rho(b) = \sum_s b(s) R(s)$ (or $\sum_s b(s) R(s, a)$).

Solving this MDP solves the POMDP. The difficulty is that it has infinitely many states.

### Value functions are piecewise linear and convex

Consider a **conditional plan** $p$: an action, then for each possible observation another conditional plan, down to
some depth. Let $\alpha_p(s)$ be the expected reward of executing $p$ starting in state $s$. Starting in belief $b$ the
expected reward is

$$
\alpha_p(b) = \sum_s b(s)\, \alpha_p(s),
$$

**linear** in $b$: a hyperplane over the simplex, written as the vector $\alpha_p$ (an **alpha vector**). The optimal
value with $h$ steps to go is the best plan's value: $U_h(b) = \max_p \alpha_p(b)$. A maximum of finitely many linear
functions is **piecewise linear and convex**. So $U_h$ is represented exactly by a finite set of alpha vectors, and the
optimal action at $b$ is the first action of the plan whose vector is highest there.

**Value iteration on alpha vectors.** The plans of depth $h + 1$ are: choose an action $a$, and for each observation $o$
choose a plan of depth $h$. Their vectors are

$$
\alpha(s) = R(s, a) + \gamma \sum_{s'} P(s' \mid s, a) \sum_o P(o \mid s', a)\, \alpha_{p_o}(s').
$$

With $|\Gamma_h|$ vectors at depth $h$, there are $|A|\,|\Gamma_h|^{|O|}$ candidates at depth $h + 1$, doubly
exponential growth in $h$. Most are **dominated** (below the upper surface everywhere) and can be pruned; the vectors
that remain are the ones that are best for some belief. Deciding exactly which are needed takes a linear program per
vector in general. For two states the belief is a single number $b = P(s_1)$, and the code below simply keeps every
vector that is best at some point of a grid of 1001 beliefs, computing the best vector at each grid point directly.

### The tiger problem

Leslie Kaelbling, Michael Littman and Anthony Cassandra's 1998 paper introduced this standard test. A tiger is behind
one of two doors, with equal probability. The agent can **listen** (cost 1), and hears the tiger on the correct side with
probability 0.85; or it can **open** a door: +10 if the tiger is behind the other door, -100 if it is behind this one.
After a door is opened, the tiger is placed again at random and the problem restarts. Discount 0.95.

```python
--8<-- "books/ai/ch14_pomdp.py"
```

```
horizon  vectors  value at b=0.5  action at b = 0.50 0.80 0.93 0.96 0.98
      1        3          -1.000      listen     listen open-right open-right open-right
      2        5          -1.950      listen     listen     listen     listen open-right
      3        9           2.310      listen     listen     listen     listen     listen
      5       13           2.763      listen     listen     listen     listen open-right
     10       27           6.693      listen     listen     listen open-right open-right
     20       59          11.880      listen     listen     listen     listen open-right
     50       40          17.760      listen     listen     listen     listen open-right
    100        9          19.247      listen     listen     listen     listen open-right
policy after 100 steps: the action changes at beliefs [0.04, 0.961]
  open-left on [0.000, 0.040], listen on [0.040, 0.961], open-right on [0.961, 1.000]

belief P(tiger-left) while listening: hear-left -> 0.8500; hear-left -> 0.9698; hear-right -> 0.8500; hear-left -> 0.9698; hear-left -> 0.9945; 
```

Here $b = P(\text{tiger-left})$, so high $b$ means "open the right door".

- **With one step to go**, the agent opens a door if $10b - 100(1-b) > -1$, that is, $b > 0.9$ (Exercise 12); at
  $b = 0.5$ it listens, which gains nothing in a one-step problem but loses only 1.
- **With longer horizons** the value at $b = 0.5$ grows (from $-1$ to about 19.2), because listening now enables a good
  door choice later, and opening a door restarts the game, so rewards can be collected repeatedly. The first action
  depends on the horizon: with 3 steps left it listens even at 0.98 (there is time to make sure), with 10 left it
  already opens at 0.96. Finite-horizon optimal policies are **non-stationary**.
- **The long-horizon policy** listens while $0.04 < b < 0.961$ and opens otherwise. Starting from 0.5, one "hear left"
  gives 0.85 and a second gives 0.9698, above the threshold. So the optimal behaviour is: **listen until two more
  hearings point to one side than to the other, then open the other door.** Nobody programmed "gather information":
  it falls out of maximising expected utility over beliefs, because information has value (14.2) in the future.
- **The number of vectors** rises and then falls (the grid keeps only vectors that win somewhere); the converged value
  function needs only a handful.

### How hard are POMDPs?

Very. Papadimitriou and Tsitsiklis (1987) proved that finite-horizon POMDPs are PSPACE-complete, and Madani, Hanks and
Condon (1999) proved that finding an optimal policy for infinite-horizon POMDPs (in the undiscounted case they studied)
is undecidable. Practical methods are approximate:

- **Point-based value iteration** (Pineau, Gordon and Thrun, 2003) keeps one alpha vector per belief in a sampled set of
  reachable beliefs, as our grid does, and scales to problems with thousands of states.
- **Online search** plans only from the current belief, building a lookahead tree of actions and observations at each
  step. POMCP (Silver and Veness, 2010) does this with Monte Carlo tree search ([Chapter
  6](06-Games-and-Adversarial-Search.md)) and particle beliefs ([Chapter 13](13-Reasoning-over-Time.md)).
- **Simple heuristics**, such as acting as if the most likely state were true, or assuming the state will be revealed
  after one step (QMDP), are fast but never choose an action just to gain information, which is exactly what the tiger
  requires.

## In practice

- Use expected utility to make trade-offs explicit; elicit utilities carefully, because the policy is only as good as
  the reward (the grid world's policy flips four times as $r$ varies).
- For MDPs with up to millions of states, value iteration or policy iteration in a vectorised form works well; for
  larger ones, approximate the value function, which is where reinforcement learning ([Chapter
  15](15-Reinforcement-Learning.md)) begins. Libraries such as `pymdptoolbox` implement the classical algorithms;
  POMDP solvers (for example SARSOP, Kurniawati, Hsu and Lee, 2008) are available as research software.
- Compute the value of information before collecting expensive data; it is often small, and it is never negative.

## Check yourself

??? question "1. An agent prefers A to B, B to C and C to A, and will pay 1 dollar to trade up to anything it prefers. It starts holding A. What happens? Which axiom does it violate?"
    It pays 1 dollar to swap A for C (it prefers C to A), 1 dollar to swap C for B (B over C), 1 dollar to swap B for
    A (A over B), and holds A again, 3 dollars poorer. The cycle can repeat forever: a money pump. The preferences
    violate transitivity (A over B and B over C should give A over C, but the agent prefers C to A).

??? question "2. With utility U(x) = sqrt(x) of the money won, find the certainty equivalent of the lottery [0.5, 0 dollars; 0.5, 100 dollars], and the risk premium."
    $E[U] = 0.5 \cdot 0 + 0.5 \cdot 10 = 5$. The certainty equivalent $c$ satisfies $\sqrt{c} = 5$, so $c = 25$ dollars.
    The expected value is 50 dollars, so the risk premium is 25 dollars: this agent would sell the lottery for any price
    above 25. (The square root is concave, so the agent is risk averse.)

??? question "3. Show that replacing U by aU + b with a > 0 never changes an expected-utility decision. Give an example where replacing U by U squared (also increasing, for U > 0) does change one."
    $E[aU + b] = a E[U] + b$, and $x \mapsto ax + b$ is increasing for $a > 0$, so the order of expected utilities, and
    hence the best action, is unchanged. Squaring is increasing but not affine. Example: outcomes with $U = 1$, $2$, $3$.
    Lottery A is $[0.5, 1; 0.5, 3]$ with $E[U] = 2$; B is the sure outcome 2.1. With $U$, B wins (2.1 > 2). With $U^2$,
    A has $E = 0.5 \cdot 1 + 0.5 \cdot 9 = 5$ and B has $4.41$, so A wins. Only affine changes preserve all choices
    between lotteries: utilities are measured on an interval scale, not just an order.

??? question "4. Compute the value of information of the camera in the rover example by hand."
    $P(\text{pos}) = 0.3 \cdot 0.7 + 0.7 \cdot 0.2 = 0.21 + 0.14 = 0.35$. Given positive,
    $P(\text{mineral}) = 0.21/0.35 = 0.6$; drill: $EU = 60 - 20 = 40$. Given negative ($P = 0.65$),
    $P(\text{mineral}) = 0.09/0.65 = 0.138$; drilling would give $13.8 - 20 < 0$, so skip: $EU = 0$. With the camera,
    $EU = 0.35 \cdot 40 = 14$, so $VPI = 14 - 10 = 4$, as the program prints.

??? question "5. In the rover example, for which prior probabilities of the mineral is the spectrometer worth nothing at all?"
    Information is worthless exactly when no result can change the decision. Without the test, drill iff
    $100p - 20 > 0$, that is, $p > 0.2$. A positive reading gives $P(m \mid +) = 0.8p/(0.8p + 0.1(1-p))$; a negative
    gives $P(m \mid -) = 0.2p/(0.2p + 0.9(1-p))$. The test is worthless if both posteriors are on the same side of 0.2
    as each other. Positive above 0.2: $0.8p > 0.2(0.8p + 0.1 - 0.1p)$, that is, $0.8p > 0.14p + 0.02$, so
    $p > 0.0303$. Negative above 0.2: $0.2p > 0.2(0.2p + 0.9 - 0.9p)$, that is, $p > 0.9 - 0.7p$, so $p > 0.5294$.
    So VPI = 0 for $p \le 0.0303$ (skip whatever the reading) and for $p \ge 0.5294$ (drill whatever the reading), and
    VPI > 0 strictly between. (At the boundaries the decision is a tie, so the value is still 0.)

??? question "6. Prove that the value of information is zero if no possible observation changes the best action."
    If for every outcome $e_{jk}$ the best action given $e, e_{jk}$ is the same action $\alpha$ that is best without
    the observation, then the first term of the VPI formula is
    $\sum_k P(e_{jk} \mid e) EU(\alpha \mid e, e_{jk}) = EU(\alpha \mid e)$ by the law of total expectation, so VPI is 0.
    Information is valuable only through the decisions it changes.

??? question "7. Construct an example where two observations are each worth nothing alone but are valuable together (so VPI is super-additive)."
    Let $A$ and $B$ be independent fair coins and let the rock contain the mineral iff exactly one of them is heads
    ($M = A \oplus B$), so $P(M) = 0.5$. Utility: drilling earns 100 if $M$ and costs 60 either way (net $+40$ or
    $-60$); skipping is 0. Without information, $EU(\text{drill}) = 50 - 60 = -10$, so skip, $EU = 0$. Observing $A$
    alone tells nothing about $M$ ($P(M \mid A) = 0.5$ either way), so its VPI is 0; the same for $B$. Observing both
    reveals $M$: drill only when $M$, $EU = 0.5 \cdot 40 = 20$. So $VPI(A, B) = 20 > 0 = VPI(A) + VPI(B)$. A myopic
    agent, which looks at one observation at a time, would never collect either.

??? question "8. In the 4 by 3 world (r = -0.04, gamma = 1), starting from U_0 = 0, compute U_2(3,2), U_2(3,3) and U_3(3,3) by hand."
    $U_1 = -0.04$ in every non-terminal square ($\pm 1$ at the terminals). For $U_2(3, 2)$: North gives
    $0.8 \cdot (-0.04) + 0.1 \cdot (-1) + 0.1 \cdot (-0.04) = -0.136$ (the East slip enters -1, the West slip hits the
    wall); West gives $0.8 \cdot (-0.04) + 0.1 \cdot (-0.04) + 0.1 \cdot (-0.04) = -0.04$ (bounce, or slip to (3, 3) or
    (3, 1)). Best is West, so $U_2(3, 2) = -0.04 - 0.04 = -0.08$: after two sweeps (3, 2) has heard only of the -1.
    $U_2(3, 3)$, East: $-0.04 + 0.8 \cdot 1 + 0.1 \cdot (-0.04) + 0.1 \cdot (-0.04) = 0.752$.
    $U_3(3, 3)$, East: 0.8 to (4, 3) (+1), 0.1 North (bump, stay: $0.752$), 0.1 South to (3, 2) ($-0.08$):
    $-0.04 + 0.8 + 0.0752 - 0.008 = 0.8272$. North would give $-0.04 + 0.8 \cdot 0.752 + 0.1 \cdot 1 + 0.1 \cdot (-0.08)
    = 0.6536$, worse. Both values match the program's history (0.752 and 0.827) and the plot.

??? question "9. For gamma = 0.9, rewards bounded by R_max = 1 and a target error of 0.001, how many sweeps of value iteration does the bound N guarantee? What if gamma = 0.99?"
    $N = \lceil \log(2/(0.001 \cdot 0.1)) / \log(1/0.9) \rceil = \lceil \log(20000)/0.10536 \rceil = \lceil 9.9035/0.10536 \rceil
    = \lceil 93.996 \rceil = 94$. For $\gamma = 0.99$: $\log(2/(0.001 \cdot 0.01)) = \log(200000) = 12.206$ and
    $\log(1/0.99) = 0.01005$, so $N = \lceil 1214.6 \rceil = 1215$. A horizon ten times longer costs about thirteen times
    as many sweeps.

??? question "10. Write the code: evaluate the fixed policy of the figure for r = -0.04 both by solving the linear system and by repeated simplified Bellman updates, and check that U(1,1) = 0.705."
    ```python
    import io, contextlib
    import numpy as np
    with contextlib.redirect_stdout(io.StringIO()):    # run from code/books/ai; hide that program's own output
        import ch14_mdp as m

    pi = {(1, 1): "N", (1, 2): "N", (1, 3): "E", (2, 3): "E", (3, 3): "E",
          (3, 2): "N", (3, 1): "W", (2, 1): "W", (4, 1): "W"}
    R = m.rewards(-0.04)
    n = len(m.STATES)
    P_pi = np.zeros((n, n))
    for s, a in pi.items():
        P_pi[m.IDX[s]] = m.P[a][m.IDX[s]]
    exact = np.linalg.solve(np.eye(n) - P_pi, R)
    U = np.zeros(n)
    for k in range(1, 1000):
        U_new = R + P_pi @ U
        if np.abs(U_new - U).max() < 1e-9:
            break
        U = U_new
    print("sweeps", k, " U(1,1) iterative", round(U[m.IDX[(1, 1)]], 4), " exact", round(exact[m.IDX[(1, 1)]], 4))
    ```
    It prints `sweeps 39  U(1,1) iterative 0.7053  exact 0.7053`. The linear solve is exact in one step; the iteration
    needs 39 sweeps for $10^{-9}$. Rows of terminal states are zero in `P_pi`, so their values are just their rewards.

??? question "11. Why can policy iteration never visit the same policy twice? Give an upper bound on the number of rounds for the 4 by 3 world."
    By the policy improvement theorem, $U^{\pi_{i+1}} \ge U^{\pi_i}$ entrywise, with strict inequality somewhere unless
    the policy has stopped changing (with ties broken in favour of the old action, an unchanged greedy policy means the
    algorithm stops). If a policy reappeared, the utilities would have to rise strictly and then return to the same
    values, which is impossible. So the rounds are bounded by the number of policies: 9 non-terminal squares and 4
    actions give $4^9 = 262\,144$. The actual number, 5, is far smaller, as is typical.

??? question "12. In the tiger problem with one step to go, for which beliefs b = P(tiger-left) is opening the right door better than listening? After hearing the tiger on the left twice from b = 0.5, what is b?"
    Opening right earns 10 if the tiger is on the left and -100 if it is on the right: $10b - 100(1-b) = 110b - 100$.
    Listening earns $-1$. Opening is better when $110b - 100 > -1$, that is, $b > 99/110 = 0.9$. After one "hear left",
    $b = 0.85 \cdot 0.5 / (0.85 \cdot 0.5 + 0.15 \cdot 0.5) = 0.85$; after a second,
    $b = 0.85 \cdot 0.85 / (0.85 \cdot 0.85 + 0.15 \cdot 0.15) = 0.7225/0.745 = 0.9698$. Both above 0.9 and above the
    long-horizon threshold 0.961, so the agent opens the right door.

## What you learned

- Coherent preferences over lotteries (the von Neumann-Morgenstern axioms) can always be described by a utility
  function, unique up to positive affine change, and the rational choice maximises expected utility.
- The utility of money is usually concave, which explains risk aversion, certainty equivalents and insurance; people
  violate the axioms (Allais), which matters when we learn utilities from them.
- Decision networks add decisions and utilities to Bayesian networks; the value of information is the expected
  improvement in the decision, never negative, not additive, and zero unless an observation could change the action.
- An MDP is a fully observable sequential problem; its optimal utilities satisfy the Bellman equation, and the greedy
  policy with respect to them is optimal.
- Value iteration converges geometrically because the Bellman update is a $\gamma$-contraction; policy iteration
  alternates exact evaluation and greedy improvement and terminates with an optimal policy.
- A POMDP is an MDP over belief states; its value functions are piecewise linear and convex, exact solution is very
  hard, and optimal behaviour includes gathering information on purpose, as in the tiger problem.

**Next:** [Chapter 15](15-Reinforcement-Learning.md) removes the model: the agent must learn good behaviour from rewards
alone, by trying things.

## Further reading

- S. Russell and P. Norvig, *Artificial Intelligence: A Modern Approach*, 4th ed., 2020: chapters 16 (making simple
  decisions) and 17 (making complex decisions), the source of the 4 by 3 world.
- J. von Neumann and O. Morgenstern, *Theory of Games and Economic Behavior*, 1944 (2nd ed. 1947, with the utility
  axioms).
- D. Bernoulli, "Specimen theoriae novae de mensura sortis", 1738 (English translation "Exposition of a new theory on
  the measurement of risk", *Econometrica* 22, 1954).
- M. Allais, "Le comportement de l'homme rationnel devant le risque", *Econometrica* 21, 1953; D. Kahneman and A.
  Tversky, "Prospect theory: an analysis of decision under risk", *Econometrica* 47, 1979.
- R. L. Keeney and H. Raiffa, *Decisions with Multiple Objectives*, 1976; R. A. Howard and J. E. Matheson, "Influence
  diagrams", 1984 (in *Readings on the Principles and Applications of Decision Analysis*).
- R. Bellman, *Dynamic Programming*, 1957; R. A. Howard, *Dynamic Programming and Markov Processes*, 1960.
- M. L. Puterman, *Markov Decision Processes: Discrete Stochastic Dynamic Programming*, 1994 (the standard reference
  for proofs).
- R. J. Williams and L. C. Baird, "Tight performance bounds on greedy policies based on imperfect value functions",
  Northeastern University technical report, 1993.
- C. H. Papadimitriou and J. N. Tsitsiklis, "The complexity of Markov decision processes", *Mathematics of Operations
  Research* 12, 1987; O. Madani, S. Hanks and A. Condon, "On the undecidability of probabilistic planning and
  infinite-horizon partially observable Markov decision problems", AAAI 1999.
- R. D. Smallwood and E. J. Sondik, "The optimal control of partially observable Markov processes over a finite
  horizon", *Operations Research* 21, 1973; L. P. Kaelbling, M. L. Littman and A. R. Cassandra, "Planning and acting in
  partially observable stochastic domains", *Artificial Intelligence* 101, 1998.
- J. Pineau, G. Gordon and S. Thrun, "Point-based value iteration: an anytime algorithm for POMDPs", IJCAI 2003;
  D. Silver and J. Veness, "Monte-Carlo planning in large POMDPs", NeurIPS 2010.
- On this site: the Algorithms book's [Chapter 13](../algorithms/13-Dynamic-Programming.md) (dynamic programming) and
  [Chapter 16](../algorithms/16-Shortest-Paths.md) (shortest paths, the deterministic special case of an MDP),
  [Chapter 13](13-Reasoning-over-Time.md) of this book for belief states, and
  [Probability](https://math.akadian.ca/books/probability/) for expectation and Jensen's inequality.
