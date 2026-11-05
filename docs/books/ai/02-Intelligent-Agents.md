# 2. Intelligent agents

*Chapter 1 chose a view of AI: build agents that act rationally. That sentence hides four questions. What exactly
is an agent? What does "rational" mean, and rational by whose measure? What makes one environment harder than
another? And what should the inside of an agent look like? This chapter answers each one precisely. You will build
the classic two-square vacuum world and prove that a three-line agent is optimal in it, then watch the same agent
fail when the performance measure changes. You will code five kinds of agent, from a reflex to a learner, in one
small grid world and measure each. And you will compute, from orbital data, why a rover on Mars cannot wait for
Earth to tell it every move.*

!!! abstract "In this chapter"
    **You will learn:**

    - the words: agent, percept, percept sequence, action, environment, agent function and agent program, PEAS
    - what rationality means, why it is not omniscience, and why the performance measure decides everything,
      with a proof that the reflex vacuum agent is optimal for one measure and a demonstration that it is not for
      others
    - the seven properties of environments (observable, single or multi-agent, deterministic, episodic, static,
      discrete, known) and how they set the difficulty
    - five agent designs (simple reflex, model-based, goal-based, utility-based, learning), each coded and measured
      in the same grid world
    - atomic, factored and structured representations of state
    - why long signal delays force a Mars rover to act on its own, with the light time computed, and what real
      rover autonomy (AEGIS, AutoNav) does

    **You need:** [Chapter 1](01-What-Is-AI.md). The code uses breadth-first search and Dijkstra's algorithm as
    tools; [Chapter 15](../algorithms/15-Graphs-and-Graph-Search.md) and
    [Chapter 16](../algorithms/16-Shortest-Paths.md) of the Algorithms book explain them, and Chapters 3 and 4 of this
    book rebuild them for AI. Expected values (an average weighted by probability) appear in 2.4.

    **Levels:** 2.1 to 2.3 are beginner; 2.4 is beginner to intermediate; 2.5 is intermediate; 2.6 is for everyone.

## 2.1 Agents, percepts, actions, environments

What do a thermostat, a chess program, a self-driving car and a Mars rover have in common? Each one takes in
information about its surroundings and does something to them. That is the definition.

An **agent** is anything that perceives its **environment** through **sensors** and acts on that environment
through **actuators**. A person's sensors are eyes and ears and their actuators are hands and voice. A rover's
sensors are cameras, wheel encoders, an inertial measurement unit and a sun sensor; its actuators are wheel motors,
a robotic arm and a radio. A software agent's sensors might be the keystrokes, files and network packets it
receives, and its actuators the files it writes and the messages it sends.

A **percept** is what the agent's sensors deliver at one instant. The **percept sequence** is the complete history
of everything the agent has perceived so far. An agent's choice of action at any moment can depend on its built-in
knowledge and on the entire percept sequence observed to date, but not on anything it has not perceived.

<figure class="mars-fig" markdown="0">
<svg viewBox="0 0 600 230" role="img" aria-label="The agent and environment loop. The environment on the left sends percepts through sensors to the agent on the right; inside the agent a box marked agent program chooses an action; actions go back through actuators to the environment.">
  <rect x="20" y="40" width="200" height="150" rx="10" fill="#eea66f" fill-opacity="0.3" stroke="currentColor"/>
  <text x="120" y="110" font-size="15" text-anchor="middle" fill="currentColor">environment</text>
  <text x="120" y="132" font-size="12" text-anchor="middle" fill="currentColor">(the world, other agents)</text>
  <rect x="370" y="40" width="210" height="150" rx="10" fill="#9cc9ea" fill-opacity="0.3" stroke="currentColor"/>
  <text x="475" y="62" font-size="15" text-anchor="middle" fill="currentColor">agent</text>
  <rect x="400" y="80" width="150" height="70" rx="6" fill="none" stroke="currentColor" stroke-dasharray="5 3"/>
  <text x="475" y="110" font-size="13" text-anchor="middle" fill="currentColor">agent program</text>
  <text x="475" y="130" font-size="11" text-anchor="middle" fill="currentColor">percepts so far → action</text>
  <text x="475" y="178" font-size="11" text-anchor="middle" fill="currentColor">sensors in, actuators out</text>
  <line x1="220" y1="80" x2="362" y2="80" stroke="currentColor" stroke-width="2"/>
  <polygon points="370,80 360,75 360,85" fill="currentColor"/>
  <text x="295" y="70" font-size="13" text-anchor="middle" fill="currentColor">percepts</text>
  <text x="295" y="98" font-size="11" text-anchor="middle" fill="currentColor">via sensors</text>
  <line x1="370" y1="160" x2="228" y2="160" stroke="currentColor" stroke-width="2"/>
  <polygon points="220,160 230,155 230,165" fill="currentColor"/>
  <text x="295" y="150" font-size="13" text-anchor="middle" fill="currentColor">actions</text>
  <text x="295" y="178" font-size="11" text-anchor="middle" fill="currentColor">via actuators</text>
</svg>
<figcaption>Figure 2.1. An agent interacts with its environment in a loop: percepts in, actions out. Everything
the agent "knows" about the world comes in through the percept arrow, or was built in by its designer.</figcaption>
</figure>

### The agent function and the agent program

Mathematically, an agent's behaviour is described by its **agent function**, a map from percept sequences to
actions:

$$
f : \mathcal{P}^{*} \to \mathcal{A},
$$

where $\mathcal{P}$ is the set of possible percepts, $\mathcal{P}^{*}$ is the set of all finite sequences of them,
and $\mathcal{A}$ is the set of actions. The agent function is an abstract description, like the specification of
an algorithm. The **agent program** is a concrete implementation of it, running on some physical machine, the
agent's **architecture**. "Agent = architecture + program."

The simplest way to implement an agent function is to write it down as a table: for every percept sequence, the
action. This **table-driven agent** is correct by construction and hopeless in practice. If there are $|\mathcal{P}|$
possible percepts and the agent lives for $T$ steps, the table needs one entry for each sequence of length 1, 2,
..., $T$:

$$
\sum_{t=1}^{T} |\mathcal{P}|^{t} = \frac{|\mathcal{P}|^{T+1} - |\mathcal{P}|}{|\mathcal{P}| - 1}
$$

entries (a geometric series). Even in the vacuum world below, where only 4 percepts are possible, a lifetime of 20
steps needs about $1.5 \times 10^{12}$ entries, as the program in 2.2 prints. A camera producing a 1-megapixel image
with 256 grey levels has $256^{10^6}$ possible percepts per frame. So the key challenge of AI is to find programs
that produce rational behaviour from a *small* amount of code rather than a vast table, in the same way that a
ten-line square-root routine replaced the printed tables of square roots engineers once used.

### Describing a task: PEAS

To design an agent, first write down the task environment under four headings, known by the initials **PEAS**:
**P**erformance measure, **E**nvironment, **A**ctuators, **S**ensors. For an autonomous Mars rover's driving task:

| | Rover driving |
|---|---|
| Performance measure | reach the commanded site; distance covered per sol; no damage to the rover; energy used; science targets imaged |
| Environment | rocks, sand, slopes and craters; dust; changing sunlight and temperature; no other agents nearby, but the ground team on Earth with a long delay |
| Actuators | six wheel motors, four steering motors, mast and camera pointing |
| Sensors | stereo navigation and hazard cameras, wheel encoders, inertial measurement unit, sun sensor, motor currents |

(A **sol** is one Martian day, about 24 hours 40 minutes.) Writing the performance measure first is deliberate:
the rest of the chapter shows that it is the most important line.

## 2.2 Rationality and performance measures

When is an agent doing the right thing? We say it is doing well if the sequence of environment states that its
actions cause is desirable. "Desirable" is captured by a **performance measure**, a score assigned to any sequence
of environment states. Note: environment states, not the agent's opinion of how it did. An agent could fool itself;
the measure is applied from outside.

**Definition (rational agent).** For each possible percept sequence, a rational agent selects an action that is
expected to maximise its performance measure, given the evidence provided by the percept sequence and whatever
built-in knowledge the agent has.

What is rational at a given time therefore depends on four things: the performance measure, the agent's prior
knowledge of the environment, the actions it can perform, and its percept sequence to date. Three consequences are
worth spelling out.

- **Rational is not omniscient.** An omniscient agent knows the actual outcome of its actions. A rational agent
  maximises *expected* performance given what it knows. A rover that drives onto sand that looked firm in every
  image it had was not irrational; one that ignored a picture of the sand was.
- **Rational agents gather information.** If looking before crossing the road raises expected performance, a
  rational agent looks. Actions that change future percepts, such as turning a camera, are part of rationality.
- **Rational agents learn and are autonomous.** An agent that relies only on its designer's prior knowledge, and
  not on its own percepts, lacks **autonomy**. Since built-in knowledge is never complete, a rational agent should
  learn from its percepts to compensate. (A newborn foal has enough built-in knowledge to stand within hours, and
  learns the rest.)

### The vacuum world

Here is the smallest interesting environment, from Russell and Norvig. There are two squares, A and B. Each is
Clean or Dirty. The agent is in one of them. It perceives its location and whether that square is dirty, a percept
such as `[A, Dirty]`, and it can do Left, Right, Suck or NoOp (do nothing). Sucking cleans the current square;
moving Left from A or Right from B does nothing. In the basic version, dirt does not come back.

<figure class="mars-fig" markdown="0">
<svg viewBox="0 0 600 190" role="img" aria-label="The vacuum world: two squares A and B side by side. Square A contains the agent and dirt. Below, the reflex agent program: if the square is dirty, suck; else if at A, move right; else move left.">
  <rect x="40" y="30" width="160" height="110" fill="#9cc9ea" fill-opacity="0.2" stroke="currentColor" stroke-width="2"/>
  <rect x="200" y="30" width="160" height="110" fill="#9cc9ea" fill-opacity="0.2" stroke="currentColor" stroke-width="2"/>
  <text x="120" y="160" font-size="15" text-anchor="middle" fill="currentColor">A</text>
  <text x="280" y="160" font-size="15" text-anchor="middle" fill="currentColor">B</text>
  <circle cx="100" cy="85" r="24" fill="#7ccf9a" fill-opacity="0.6" stroke="currentColor"/>
  <text x="100" y="90" font-size="12" text-anchor="middle" fill="currentColor">agent</text>
  <circle cx="150" cy="110" r="4" fill="#eea66f"/>
  <circle cx="162" cy="104" r="5" fill="#eea66f"/>
  <circle cx="172" cy="115" r="4" fill="#eea66f"/>
  <circle cx="157" cy="122" r="3" fill="#eea66f"/>
  <text x="165" y="92" font-size="11" text-anchor="middle" fill="currentColor">dirt</text>
  <text x="390" y="55" font-size="13" fill="currentColor">REFLEX-VACUUM([loc, status]):</text>
  <text x="400" y="80" font-size="13" fill="currentColor">if status = Dirty: Suck</text>
  <text x="400" y="102" font-size="13" fill="currentColor">elif loc = A: Right</text>
  <text x="400" y="124" font-size="13" fill="currentColor">else: Left</text>
</svg>
<figcaption>Figure 2.2. The two-square vacuum world, in the state [agent in A, A dirty, B clean], and the reflex
agent program for it. The percept is only the agent's own square: it cannot see B from A.</figcaption>
</figure>

Is the reflex agent of Figure 2.2 rational? The question has no answer until we fix the performance measure. Take
first:

**M1:** one point for each clean square at each time step, over a lifetime of $T$ steps.

and assume, as the agent's prior knowledge, the geography (two squares, what the actions do), but not where the dirt
is or where the agent starts.

**Theorem 2.1.** Under M1, for every starting state and every lifetime $T$, the reflex agent's score is the
largest score any sequence of actions can achieve from that state. Hence no agent, even one told the starting
state in advance, does better, and the reflex agent is rational for any probability distribution over starting
states.

*Proof.* Let $c_t$ be the number of clean squares after step $t$; the score is $\sum_{t=1}^{T} c_t$, and always
$c_t \le 2$. By symmetry we may suppose the agent starts in A. There are four cases.

- *Both clean.* Then $c_t = 2$ for every $t$, whatever anyone does; the reflex agent scores the maximum $2T$.
- *A dirty, B clean.* The reflex agent sucks at step 1, and then $c_t = 2$ for all $t \ge 1$: the maximum $2T$.
- *A clean, B dirty.* No single action from A cleans B (one must move first), so every sequence has $c_1 = 1$
  and $c_t \le 2$ afterwards. The reflex agent moves Right ($c_1 = 1$), sucks ($c_2 = 2$), and from then on only
  moves, so $c_t = 2$ for $t \ge 2$: it meets the bound $1 + 2(T-1)$.
- *Both dirty.* One action cleans at most one square, and cleaning both takes at least three actions (suck, move,
  suck), so every sequence has $c_1 \le 1$, $c_2 \le 1$ and $c_t \le 2$ afterwards. The reflex agent sucks
  ($c_1 = 1$), moves ($c_2 = 1$), sucks ($c_3 = 2$) and keeps $c_t = 2$: it meets the bound $2 + 2(T-2)$.

In every case the reflex agent's sequence of $c_t$ equals the pointwise upper bound, so its total is the maximum.
An agent that does not know the starting state can do no better than one that does, and the reflex agent matches
even that, so its expected score is the largest possible under any distribution of starting states. $\square$

The program checks this by brute force for $T = 6$: it tries all $4^6 = 4096$ action sequences from each of the 8
starting states and confirms that the best total equals the reflex agent's.

### Change the measure, change the verdict

Now keep the agent and change the measure.

**M2:** one point for each unit of dirt sucked up. This sounds like a reasonable measure of a vacuum cleaner's
work. But suppose the agent can also Dump (empty its bag onto the floor). A "dumping" agent that sucks, dumps,
sucks, dumps, ... scores a point every other step, hundreds of times more than the reflex agent, while leaving the
floor no cleaner. The agent is not malfunctioning. It is doing exactly what the measure rewards. As Russell and
Norvig put it, it is better to design performance measures according to what one actually wants in the
environment, rather than according to how one thinks the agent should behave.

**M3:** M1, minus one point for each move. Now the reflex agent is no longer rational: after both squares are
clean, it shuttles back and forth forever, paying for every move. A better agent remembers that it has seen both
squares clean and stops. That needs **memory**, internal state that a reflex agent does not have.

```python
--8<-- "books/ai/ch02_vacuum.py"
```

Output:

```
average score over the 8 starting states, 1000 steps:
  agent              M1       M2       M3
  reflex        1999.25     1.00  1000.25
  dumping       1000.00   500.00  1000.00
  model-based   1999.25     1.00  1998.25

reflex agent vs best possible action sequence under M1, T = 6:
  start ('A', 0, 0): reflex 12  best 12
  start ('A', 0, 1): reflex 11  best 11
  start ('A', 1, 0): reflex 12  best 12
  start ('A', 1, 1): reflex 10  best 10
  start ('B', 0, 0): reflex 12  best 12
  start ('B', 0, 1): reflex 12  best 12
  start ('B', 1, 0): reflex 11  best 11
  start ('B', 1, 1): reflex 10  best 10

entries in a table-driven agent (4 possible percepts):
  lifetime  1 steps: 4
  lifetime  2 steps: 20
  lifetime  5 steps: 1,364
  lifetime 10 steps: 1,398,100
  lifetime 20 steps: 1,466,015,503,700
```

Check the first row by hand. The proof tells us the reflex agent loses, relative to the perfect $2T$, one point
when it starts on a clean square with dirt in the other square (two of the eight starts), two points when both are
dirty (two starts), and nothing otherwise. The total loss over the eight starts is $1 + 1 + 2 + 2 = 6$, so the
average M1 score is $2000 - 6/8 = 1999.25$. Under M3 the reflex agent moves on every step on which it does not
suck. The average amount of dirt is 1 (each square is dirty in half the starts), so it sucks once on average and
moves $999$ times: $1999.25 - 999 = 1000.25$. The model-based agent moves exactly once in every start (look at
each case), so it scores $1999.25 - 1 = 1998.25$. And the dumping agent is the clear winner under M2 with 500
points, about one every two steps, against the honest agents' average of 1.

Three lessons, each of which will return. The same behaviour can be optimal or foolish depending on the
measure. A measure that rewards a proxy for what we want (dirt sucked) instead of the thing itself (a clean floor)
invites agents to exploit the gap; Chapter 15 (Section 15.7) and Chapter 20 call this **specification gaming** or
**reward hacking**, and real cases have been documented in learning systems. And a richer measure can require a
richer agent: M3 needs memory.

## 2.3 Properties of environments

Some environments are easy (a crossword puzzle) and some are very hard (driving a taxi in a city). The difficulty is
not a single number. It is described by seven properties, and each one changes what an agent must be able to do.

**Fully or partially observable.** If the agent's sensors give it the complete state of the environment that is
relevant to the choice of action at each moment, the environment is **fully observable**; then the agent does not
need to remember anything about the world. Otherwise it is **partially observable**, because sensors are noisy or
limited: the vacuum agent cannot see the other square, a poker player cannot see the other hands, a rover cannot
see behind a rock. With no sensors at all it is **unobservable**.

**Single-agent or multi-agent.** A crossword is single-agent. Chess is **multi-agent** and **competitive**: the
opponent is trying to minimise your score. Taxi drivers share a partly **cooperative** environment (avoiding
collisions helps everyone) that is also partly competitive (one parking space). The test is whether another entity's
behaviour is best described as maximising a performance measure that depends on yours. Multi-agent environments
bring communication, deception and randomised strategies (Chapter 6 and Chapter 19).

**Deterministic or nondeterministic.** If the next state is completely determined by the current state and the
action, the environment is **deterministic**; otherwise **nondeterministic**. If the uncertainty is described by
probabilities ("the wheels slip with probability 2/3"), the environment is called **stochastic**. A fully
observable, deterministic environment involves no uncertainty at all, and many of the search methods of Part II
assume exactly that.

**Episodic or sequential.** In an **episodic** environment the agent's experience divides into independent
episodes: perceive, act once, and the next episode does not depend on this action. A machine checking parts on an
assembly line is episodic. In a **sequential** environment the current decision can affect all future ones: chess,
driving, and exploration. Sequential environments need the agent to think ahead.

**Static or dynamic.** If the environment can change while the agent is deliberating, it is **dynamic**; otherwise
**static**. If the world does not change but the agent's score does (a chess clock), it is **semidynamic**. In a
dynamic world, not deciding is itself a decision.

**Discrete or continuous.** This applies to the state, to time, and to percepts and actions. Chess has finitely
many distinct states and moves. Driving is continuous in position, speed and steering angle, and in time.

**Known or unknown.** This is about the *agent's* (or designer's) knowledge of the rules, not about the environment
itself. In a **known** environment the outcomes (or outcome probabilities) of all actions are given. In an
**unknown** one the agent must learn how the world works. A known environment can be partially observable (in
solitaire card games you know the rules but cannot see the face-down cards), and an unknown one can be fully
observable (a new video game: you see the whole screen but do not know what the buttons do).

| Task | Observable | Agents | Deterministic | Episodic | Static | Discrete |
|---|---|---|---|---|---|---|
| Crossword puzzle | fully | single | deterministic | sequential | static | discrete |
| Chess with a clock | fully | multi | deterministic | sequential | semi | discrete |
| Poker | partially | multi | stochastic | sequential | static | discrete |
| Backgammon | fully | multi | stochastic | sequential | static | discrete |
| Image classification | fully | single | deterministic | episodic | static | continuous |
| Taxi driving | partially | multi | stochastic | sequential | dynamic | continuous |
| Mars rover driving | partially | single | stochastic | sequential | dynamic | continuous |
| Two-square vacuum world | partially | single | deterministic | sequential | static | discrete |

Some entries are judgement calls, and that is fine; the point is to know which difficulties a design must handle.
The image classifier is "deterministic" because its action (the label) does not change what the next image is. The
rover is "dynamic" because light, dust and temperature change while it thinks, and "single-agent" because nothing
on Mars plays against it; the operations team on Earth is better modelled as the source of its goals than as another
player.

The hardest case is partially observable, multi-agent, stochastic, sequential, dynamic, continuous and unknown.
Real driving is nearly all of these. The chapters of this book take the properties one or two at a time:

| Property relaxed | Where in this book |
|---|---|
| fully observable, deterministic, known, discrete, single-agent | Chapters 3 and 4 (search) |
| path does not matter; continuous; nondeterministic and partially observable | Chapter 5 |
| multi-agent, competitive | Chapter 6 |
| factored states | Chapters 7, 8 and 10 |
| stochastic, partially observable | Chapters 12, 13 and 14 |
| unknown environment | Chapter 15 (reinforcement learning) |

## 2.4 Five kinds of agent

*Level: beginner to intermediate.*

The agent function says *what* the agent should do; the agent program says *how*. Five designs, each adding one
capability to the last, cover most AI systems. To compare them fairly, we put all five in the same world and score
them with the same measure.

### The test world

A rover starts at S and must reach a rock at G. `#` is wall. `~` is soft sand: a move into a sand cell fails, leaving
the rover where it was, with probability $2/3$. The performance measure is the number of time steps to reach G
(fewer is better), with a cut-off at 200 steps. Every agent is told which cell it is in (a position fix), but the
agents differ in what else they sense and know.

<figure class="mars-fig" markdown="0">
<svg viewBox="0 0 600 370" role="img" aria-label="The grid world: an 11 by 13 grid of walls with corridors. S is at the top left, G near the bottom middle. Soft sand cells line the short route down the left column and along the bottom row. The goal-based plan, in blue, goes straight down through the sand: 13 moves. The utility-based plan, in green, goes along the top corridor, down the right side and back along the bottom: 23 moves, no sand.">
<rect x="20" y="20" width="390" height="30" fill="currentColor" fill-opacity="0.55"/>
<rect x="20" y="50" width="30" height="30" fill="currentColor" fill-opacity="0.55"/>
<rect x="380" y="50" width="30" height="30" fill="currentColor" fill-opacity="0.55"/>
<rect x="20" y="80" width="30" height="30" fill="currentColor" fill-opacity="0.55"/>
<rect x="80" y="80" width="270" height="30" fill="currentColor" fill-opacity="0.55"/>
<rect x="380" y="80" width="30" height="30" fill="currentColor" fill-opacity="0.55"/>
<rect x="20" y="110" width="30" height="30" fill="currentColor" fill-opacity="0.55"/>
<rect x="80" y="110" width="30" height="30" fill="currentColor" fill-opacity="0.55"/>
<rect x="320" y="110" width="30" height="30" fill="currentColor" fill-opacity="0.55"/>
<rect x="380" y="110" width="30" height="30" fill="currentColor" fill-opacity="0.55"/>
<rect x="20" y="140" width="30" height="30" fill="currentColor" fill-opacity="0.55"/>
<rect x="80" y="140" width="30" height="30" fill="currentColor" fill-opacity="0.55"/>
<rect x="140" y="140" width="150" height="30" fill="currentColor" fill-opacity="0.55"/>
<rect x="320" y="140" width="30" height="30" fill="currentColor" fill-opacity="0.55"/>
<rect x="380" y="140" width="30" height="30" fill="currentColor" fill-opacity="0.55"/>
<rect x="20" y="170" width="30" height="30" fill="currentColor" fill-opacity="0.55"/>
<rect x="80" y="170" width="30" height="30" fill="currentColor" fill-opacity="0.55"/>
<rect x="200" y="170" width="30" height="30" fill="currentColor" fill-opacity="0.55"/>
<rect x="260" y="170" width="30" height="30" fill="currentColor" fill-opacity="0.55"/>
<rect x="320" y="170" width="30" height="30" fill="currentColor" fill-opacity="0.55"/>
<rect x="380" y="170" width="30" height="30" fill="currentColor" fill-opacity="0.55"/>
<rect x="20" y="200" width="30" height="30" fill="currentColor" fill-opacity="0.55"/>
<rect x="80" y="200" width="150" height="30" fill="currentColor" fill-opacity="0.55"/>
<rect x="260" y="200" width="30" height="30" fill="currentColor" fill-opacity="0.55"/>
<rect x="320" y="200" width="30" height="30" fill="currentColor" fill-opacity="0.55"/>
<rect x="380" y="200" width="30" height="30" fill="currentColor" fill-opacity="0.55"/>
<rect x="20" y="230" width="30" height="30" fill="currentColor" fill-opacity="0.55"/>
<rect x="260" y="230" width="30" height="30" fill="currentColor" fill-opacity="0.55"/>
<rect x="320" y="230" width="30" height="30" fill="currentColor" fill-opacity="0.55"/>
<rect x="380" y="230" width="30" height="30" fill="currentColor" fill-opacity="0.55"/>
<rect x="20" y="260" width="30" height="30" fill="currentColor" fill-opacity="0.55"/>
<rect x="50" y="260" width="30" height="30" fill="#eea66f" fill-opacity="0.55"/>
<rect x="80" y="260" width="210" height="30" fill="currentColor" fill-opacity="0.55"/>
<rect x="320" y="260" width="30" height="30" fill="currentColor" fill-opacity="0.55"/>
<rect x="380" y="260" width="30" height="30" fill="currentColor" fill-opacity="0.55"/>
<rect x="20" y="290" width="30" height="30" fill="currentColor" fill-opacity="0.55"/>
<rect x="50" y="290" width="150" height="30" fill="#eea66f" fill-opacity="0.55"/>
<rect x="380" y="290" width="30" height="30" fill="currentColor" fill-opacity="0.55"/>
<rect x="20" y="320" width="390" height="30" fill="currentColor" fill-opacity="0.55"/>
<polyline points="61,61 61,301 211,301" fill="none" stroke="#9cc9ea" stroke-width="4"/>
<polyline points="69,69 369,69 369,309 219,309" fill="none" stroke="#7ccf9a" stroke-width="4"/>
<text x="65" y="56" font-size="13" font-weight="bold" text-anchor="middle" fill="currentColor">S</text>
<text x="215" y="296" font-size="13" font-weight="bold" text-anchor="middle" fill="currentColor">G</text>
<rect x="430" y="40" width="20" height="20" fill="currentColor" fill-opacity="0.55"/>
<text x="458" y="55" font-size="12" fill="currentColor">wall</text>
<rect x="430" y="70" width="20" height="20" fill="#eea66f" fill-opacity="0.55"/>
<text x="458" y="85" font-size="12" fill="currentColor">sand (slips 2/3)</text>
<line x1="430" y1="110" x2="450" y2="110" stroke="#9cc9ea" stroke-width="4"/>
<text x="458" y="114" font-size="12" fill="currentColor">goal-based plan:</text>
<text x="458" y="130" font-size="12" fill="currentColor">13 moves, 6 in sand</text>
<line x1="430" y1="150" x2="450" y2="150" stroke="#7ccf9a" stroke-width="4"/>
<text x="458" y="154" font-size="12" fill="currentColor">utility-based plan:</text>
<text x="458" y="170" font-size="12" fill="currentColor">23 moves, no sand</text>
</svg>
<figcaption>Figure 2.3. The test world. The fewest-moves route (blue) runs down the left side and through six sand
cells; the route with the smallest expected time (green) goes the long way round on firm ground.</figcaption>
</figure>

### 1. Simple reflex agents

A **simple reflex agent** chooses its action from the current percept only, ignoring the history, by
**condition-action rules**: "if the car in front is braking, then brake." The vacuum agent of 2.2 is one. Ours
senses which neighbouring cells are free and the compass bearing to G (like a beacon), and follows one rule: *if
some free direction points toward G, take one of them at random; otherwise take a random free direction.*

Reflex agents are tiny and fast, and they work well when the right action can be read off the current percept,
which is roughly when the environment is fully observable. They fail when it is not. Here, look at the top corridor:
from any cell left of column 6 the bearing says "east" (and "south", but south is wall), and from any cell right
of column 6 it says "west", because G is in column 6. So the agent walks back and forth around column 6 and is
pulled back whenever a random step takes it away. The same trap exists in the corridor on row 7. The rule cannot
know it has been here before, because it has no memory.

### 2. Model-based reflex agents

The fix for partial observability is to keep **internal state**: a summary of the parts of the world the agent
cannot see now, updated from each percept. To update it, the agent needs a **transition model** (how the world
changes, including how its own actions change it) and a **sensor model** (how the world shows up in its percepts).
Together they are the agent's **model** of the world. Our model-based agent's state is simple: a count of how often
it has visited each cell. Its rule prefers the least-visited free neighbour, breaking ties toward G. That memory is
enough to stop the oscillation: once the corridor cells have been visited, unexplored cells win.

### 3. Goal-based agents

Knowing the current state is not always enough to know what to do; a junction looks the same whether you want to go
left or right. A **goal-based agent** also has a **goal**, a description of desirable states, and chooses actions
by looking ahead: "what will happen if I do this, and will it bring me to the goal?" When one action does not reach
the goal, the agent must consider *sequences* of actions. That is **search** (Chapters 3 and 4) and **planning**
(Chapter 10). Our goal-based agent knows the map and plans the route with the fewest moves by breadth-first search,
then follows it, repeating a move when it slips.

The goal-based agent is more flexible than a reflex agent: give it a new goal and it plans a new route, while the
reflex agent's rules would all need rewriting. But a goal is a yes-or-no thing, and here it misleads: the fewest
moves go through six sand cells.

### 4. Utility-based agents

Goals distinguish "happy" from "unhappy" states. Most real performance measures need finer distinctions: faster,
safer, cheaper. A **utility function** maps states (or sequences of states) to real numbers that measure how
desirable they are; it is the agent's internal version of the performance measure. A **utility-based agent**
chooses the action that maximises **expected utility**: the average of the utilities of the possible outcomes,
weighted by their probabilities. That is the right rule under uncertainty, and Chapter 14 proves it from simple
axioms.

Here the expected time to enter a sand cell matters. Each attempt succeeds with probability $1/3$, independently.

**Lemma 2.2.** If each attempt succeeds independently with probability $q > 0$, the expected number of attempts
until the first success is $1/q$.

*Proof.* Let $E$ be the expected number of attempts. The first attempt always happens. With probability $q$ it
succeeds and we stop; with probability $1 - q$ it fails, and we are back where we started, needing $E$ more
attempts on average. So $E = 1 + (1 - q) E$, which gives $qE = 1$ and $E = 1/q$. (The equation assumes $E$ is
finite; the direct sum $\sum_{k \ge 1} k (1-q)^{k-1} q = 1/q$ confirms it.) $\square$

With $q = 1/3$, each sand cell costs 3 steps on average instead of 1. The utility-based agent runs Dijkstra's
algorithm with cost 3 for entering sand and 1 for firm ground. The sand route has expected time
$7 + 6 \times 3 = 25$ (seven firm moves and six into sand); the firm route has 23 moves at cost 1. So the utility-based agent goes
the long way, and is right to.

### 5. Learning agents

All the agents so far were given their knowledge: rules, a model, a map, probabilities. A **learning agent** improves
its behaviour from experience. Russell and Norvig divide it into four parts: a **performance element** (one of the
designs above, which chooses actions), a **critic** (which tells it how well it is doing, against a fixed
performance standard), a **learning element** (which uses the critic's feedback to change the performance element),
and a **problem generator** (which suggests exploratory actions that may be worse now but teach something).

<figure class="mars-fig" markdown="0">
<svg viewBox="0 0 600 260" role="img" aria-label="The learning agent. Inside the agent: a critic compares percepts with a performance standard and sends feedback to the learning element; the learning element changes the performance element and sets learning goals for the problem generator; the problem generator suggests exploratory actions to the performance element, which sends actions to the environment.">
  <rect x="20" y="20" width="420" height="220" rx="10" fill="#9cc9ea" fill-opacity="0.15" stroke="currentColor"/>
  <text x="40" y="40" font-size="13" fill="currentColor">agent</text>
  <rect x="470" y="20" width="110" height="220" rx="10" fill="#eea66f" fill-opacity="0.3" stroke="currentColor"/>
  <text x="525" y="134" font-size="13" text-anchor="middle" fill="currentColor">environment</text>
  <rect x="60" y="55" width="130" height="40" rx="6" fill="#7ccf9a" fill-opacity="0.4" stroke="currentColor"/>
  <text x="125" y="80" font-size="13" text-anchor="middle" fill="currentColor">critic</text>
  <rect x="60" y="140" width="130" height="40" rx="6" fill="#7ccf9a" fill-opacity="0.4" stroke="currentColor"/>
  <text x="125" y="165" font-size="13" text-anchor="middle" fill="currentColor">learning element</text>
  <rect x="250" y="140" width="160" height="40" rx="6" fill="#7ccf9a" fill-opacity="0.4" stroke="currentColor"/>
  <text x="330" y="165" font-size="13" text-anchor="middle" fill="currentColor">performance element</text>
  <rect x="250" y="195" width="160" height="34" rx="6" fill="#7ccf9a" fill-opacity="0.4" stroke="currentColor"/>
  <text x="330" y="217" font-size="13" text-anchor="middle" fill="currentColor">problem generator</text>
  <line x1="470" y1="75" x2="198" y2="75" stroke="currentColor" stroke-width="1.5"/>
  <polygon points="190,75 200,70 200,80" fill="currentColor"/>
  <text x="330" y="68" font-size="11" text-anchor="middle" fill="currentColor">percepts</text>
  <line x1="410" y1="160" x2="462" y2="160" stroke="currentColor" stroke-width="1.5"/>
  <polygon points="470,160 460,155 460,165" fill="currentColor"/>
  <text x="440" y="150" font-size="11" text-anchor="middle" fill="currentColor">actions</text>
  <line x1="125" y1="95" x2="125" y2="132" stroke="currentColor" stroke-width="1.5"/>
  <polygon points="125,140 120,130 130,130" fill="currentColor"/>
  <text x="130" y="118" font-size="11" fill="currentColor">feedback</text>
  <line x1="190" y1="160" x2="242" y2="160" stroke="currentColor" stroke-width="1.5"/>
  <polygon points="250,160 240,155 240,165" fill="currentColor"/>
  <text x="220" y="150" font-size="11" text-anchor="middle" fill="currentColor">changes</text>
  <line x1="125" y1="180" x2="125" y2="212" stroke="currentColor" stroke-width="1.5"/>
  <line x1="125" y1="212" x2="242" y2="212" stroke="currentColor" stroke-width="1.5"/>
  <polygon points="250,212 240,207 240,217" fill="currentColor"/>
  <text x="185" y="206" font-size="11" text-anchor="middle" fill="currentColor">goals</text>
  <line x1="330" y1="195" x2="330" y2="188" stroke="currentColor" stroke-width="1.5"/>
  <polygon points="330,180 325,190 335,190" fill="currentColor"/>
  <text x="300" y="112" font-size="11" text-anchor="middle" fill="currentColor">performance standard</text>
  <line x1="230" y1="108" x2="192" y2="90" stroke="currentColor" stroke-opacity="0.6"/>
</svg>
<figcaption>Figure 2.4. A learning agent. The critic judges outcomes against a fixed standard (here, "every step
costs 1"); the learning element uses that feedback to improve the performance element; the problem generator
proposes exploratory actions.</figcaption>
</figure>

Our learning agent knows nothing at the start: not the map, not the sand, not where G is. It receives a reward of
$-1$ for every step (that is the critic's verdict) and learns by **Q-learning** a table $Q(s, a)$ that estimates
how good action $a$ is in cell $s$. After each step from $s$ to $s'$ it moves $Q(s, a)$ halfway toward
$-1 + \max_{a'} Q(s', a')$. With probability 0.1 it takes a random action (the problem generator's exploration),
otherwise the best by $Q$. Chapter 15 derives Q-learning and proves when it converges; here we only watch it learn.

### The results

```python
--8<-- "books/ai/ch02_agents.py"
```

Output:

```
#############
#S..........#
#.#########.#
#.#.......#.#
#.#.#####.#.#
#.#...#.#.#.#
#.#####.#.#.#
#.......#.#.#
#~#######.#.#
#~~~~~G.....#
#############

goal-based plan:    13 moves, 6 into sand, route SSSSSSSSEEEEE
utility-based plan: 23 moves, expected 23.0 steps, route EEEEEEEEEESSSSSSSSWWWWW

agent            reached G  mean steps  (500 runs each)
simple reflex          66/500       176.6
model-based           500/500        32.0
goal-based            500/500        25.2
utility-based         500/500        23.0
learning agent, episodes   1- 10: mean steps  184.9
learning agent, episodes  41- 50: mean steps   42.8
learning agent, episodes 291-300: mean steps   26.5
learned policy        500/500        23.0
```

Read the table from the top.

- The **simple reflex** agent reached G in only 66 of 500 runs within 200 steps. It is caught by the bearing trap in
  the top corridor or in row 7, exactly as predicted. Its mean of 176.6 steps is mostly runs cut off at 200.
- The **model-based** agent always arrives, in 32.0 steps on average: memory cures the trap, but it still has no
  map, so it explores some dead ends.
- The **goal-based** agent takes 25.2 steps on average, close to the predicted $25$: it plans the fewest moves and
  then pays for the sand.
- The **utility-based** agent takes exactly 23 steps every time: the firm route has no randomness, and its expected
  time is the smallest.
- The **learning** agent starts worse than the reflex agent (184.9 steps per episode in the first ten, mostly
  wandering until the cut-off), improves quickly, and its final greedy policy takes exactly 23 steps: it has
  discovered the utility-based agent's route from rewards alone, without being told the map, the sand or the
  probabilities. Its episodes 291 to 300 average 26.5, not 23, because it still explores at random one step in ten.

The ranking is not a law. In a world with no sand, goal-based and utility-based agents would tie; in a world that
changed every day, a fixed map would mislead the planners while the model-based explorer adapted. Each design buys
a capability at a cost: memory, a model, search, a utility function, or experience.

## 2.5 State representations: atomic, factored, structured

*Level: intermediate.*

Every agent above stores some description of the world: "the rover is in cell (5, 3)", or "the battery is at 70
percent and the arm is stowed", or "rock R2 is left of rock R7 and R7 is basalt". How rich should that description
be? There are three levels, and the choice decides which algorithms can be used.

**Atomic.** Each state is an indivisible "black box" with no internal structure, just a name or a number: "state
17". An algorithm can test two states for equality and look up what follows from a state, nothing more. Search
(Chapters 3 to 6), hidden Markov models (Chapter 13) and Markov decision processes (Chapter 14) work with atomic
states. Our grid world is atomic: a cell is just a cell.

**Factored.** Each state is a vector of **variables** (or **attributes**), each with a value: battery 70, arm
stowed, position (5, 3), dust storm false. Two states can share some variables and differ in others, and so an
algorithm can reason about *parts* of states: "any state with battery below 20 needs charging", or "these two
variables do not influence each other". Constraint satisfaction (Chapter 7), propositional logic (Chapter 8),
planning (Chapter 10), Bayesian networks (Chapter 12) and most of machine learning use factored representations.

**Structured.** The state contains **objects** and **relations** between them: rock R2 left of R7, R7 is basalt,
the arm is touching R7. The number of objects can vary, and the same relation can hold between different pairs.
First-order logic (Chapter 9), knowledge graphs (Chapter 11) and much of natural language understanding (Chapters
16 and 17) need structured representations.

<figure class="mars-fig" markdown="0">
<svg viewBox="0 0 600 220" role="img" aria-label="Three ways to represent one state. Atomic: a single black circle labelled state 17. Factored: a box with variables battery 70, arm stowed, cell 5 3, storm false. Structured: three objects, rover, rock R2 and rock R7, joined by labelled relations near and left of, with a property basalt on R7.">
  <text x="95" y="25" font-size="14" font-weight="bold" text-anchor="middle" fill="currentColor">atomic</text>
  <circle cx="95" cy="110" r="45" fill="currentColor" fill-opacity="0.55"/>
  <text x="95" y="185" font-size="12" text-anchor="middle" fill="currentColor">"state 17"</text>
  <text x="290" y="25" font-size="14" font-weight="bold" text-anchor="middle" fill="currentColor">factored</text>
  <rect x="210" y="50" width="160" height="120" rx="6" fill="#9cc9ea" fill-opacity="0.3" stroke="currentColor"/>
  <text x="225" y="78" font-size="12" fill="currentColor">battery = 70</text>
  <text x="225" y="102" font-size="12" fill="currentColor">arm = stowed</text>
  <text x="225" y="126" font-size="12" fill="currentColor">cell = (5, 3)</text>
  <text x="225" y="150" font-size="12" fill="currentColor">storm = false</text>
  <text x="490" y="25" font-size="14" font-weight="bold" text-anchor="middle" fill="currentColor">structured</text>
  <circle cx="430" cy="80" r="26" fill="#7ccf9a" fill-opacity="0.45" stroke="currentColor"/>
  <text x="430" y="85" font-size="12" text-anchor="middle" fill="currentColor">rover</text>
  <circle cx="420" cy="170" r="24" fill="#eea66f" fill-opacity="0.45" stroke="currentColor"/>
  <text x="420" y="175" font-size="12" text-anchor="middle" fill="currentColor">R2</text>
  <circle cx="540" cy="160" r="24" fill="#eea66f" fill-opacity="0.45" stroke="currentColor"/>
  <text x="540" y="165" font-size="12" text-anchor="middle" fill="currentColor">R7</text>
  <line x1="453" y1="93" x2="520" y2="145" stroke="currentColor" stroke-width="1.5"/>
  <text x="502" y="108" font-size="11" fill="currentColor">near</text>
  <line x1="444" y1="168" x2="516" y2="161" stroke="currentColor" stroke-width="1.5"/>
  <text x="480" y="200" font-size="11" text-anchor="middle" fill="currentColor">left of</text>
  <text x="540" y="207" font-size="11" text-anchor="middle" fill="currentColor">basalt</text>
  <line x1="540" y1="184" x2="540" y2="196" stroke="currentColor" stroke-opacity="0.6"/>
</svg>
<figcaption>Figure 2.5. One situation described three ways. Moving right, descriptions become more expressive and
more compact for complex worlds, and reasoning with them becomes more involved.</figcaption>
</figure>

Why not always use the most expressive? Because expressiveness has a price. A more expressive representation can
describe the same thing much more concisely ("every rock left of a basalt rock is unexamined" is one sentence in
first-order logic, but needs one separate fact per pair of rocks in a factored representation). But reasoning and
learning with it are harder: equality testing of atomic states is constant time, while deciding whether a
statement follows from first-order axioms is, in general, not even guaranteed to terminate (Chapter 9). A rule of
thumb: use the least expressive representation that captures what matters.

A second axis is **localist versus distributed**. In a localist representation each concept has its own slot
(one memory location means "basalt"). In a distributed one, a concept is a pattern spread over many slots, and each
slot takes part in many concepts. Neural networks learn distributed representations, vectors of hundreds of numbers
(see the [Machine learning book](../machine-learning/01-What-Is-Machine-Learning.md)); they are robust to noise
and support similarity ("basalt" near "andesite") but are hard to read. Chapters 16 and 21 come back to this.

## 2.6 Autonomy with long delays: why a Mars rover must decide for itself

How far could a rover drive if every move had to be approved from Earth? To answer, we need the time a radio
signal takes to cross the gap, and that changes all the time, because Earth and Mars move on different orbits.

### The light time, computed

Radio travels at the speed of light, $c = 299\,792.458$ km/s. The distance between the planets depends on where
each is in its orbit. The simplest model treats both orbits as circles in one plane, with radii $a_E = 1$ AU for
Earth and $a_M = 1.5237$ AU for Mars (one **astronomical unit**, AU, is about 149.6 million km). If $\theta$ is the
angle between the two planets as seen from the Sun, the law of cosines gives the distance

$$
d(\theta) = \sqrt{a_E^2 + a_M^2 - 2 a_E a_M \cos\theta},
$$

which ranges from $a_M - a_E = 0.5237$ AU when the planets are lined up on the same side of the Sun (**opposition**)
to $a_M + a_E = 2.5237$ AU when they are on opposite sides (**conjunction**). The angle $\theta$ cycles once every
**synodic period** $S$, which follows from the two orbital periods $P_E = 365.256$ days and $P_M = 686.98$ days:
Earth gains one full lap on Mars every $S$ days, so

$$
\frac{1}{S} = \frac{1}{P_E} - \frac{1}{P_M}, \qquad S \approx 780 \text{ days}.
$$

Real orbits are ellipses. Mars's orbit is noticeably eccentric: its distance from the Sun varies from about 206.6
to 249.2 million km. The closest possible approach is about $206.6 - 152.1 = 54.5$ million km (Mars nearest the Sun,
Earth farthest, both on the same side), and the farthest about $249.2 + 152.1 = 401.3$ million km.

```python
--8<-- "books/ai/ch02_light_delay.py"
```

Output:

```
circular-orbit model:
  synodic period 780 days
  distance 78.3 to 377.5 million km
  one-way light time 4.4 to 21.0 minutes
  fraction of the time above 10 minutes: 0.71
real orbits (eccentric), extreme cases:
  closest possible about 54.5 million km: 3.0 minutes one way
  farthest possible about 401.3 million km: 22.3 minutes one way
  round trip: 6 to 45 minutes

thought experiment: 4 hours of driving, 1 minute to drive and image 1 m
  wait for Earth after each metre (one-way  3.0 min):  34 m
  wait for Earth after each metre (one-way 12.5 min):   9 m
  wait for Earth after each metre (one-way 22.0 min):   5 m
  decide each metre on board:                    240 m
```

So a signal takes from about 3 minutes (at the rare closest oppositions) to about 22 minutes (near conjunction)
one way; in the circular model, between 4.4 and 21 minutes, and more than 10 minutes for 71 percent of the time.
Popular accounts round these figures in different ways; the program shows where the numbers come from. A question
and its answer take twice as long: up to about 45 minutes.

<figure class="mars-fig" markdown="0">
<svg viewBox="0 0 600 270" role="img" aria-label="A plot of one-way light time between Earth and Mars over one synodic period of 780 days, in the circular-orbit model. The curve starts near 4.4 minutes at opposition, rises to 21 minutes at conjunction near day 390, and falls back to 4.4 minutes at day 780. A dashed line marks 10 minutes.">
  <line x1="60" y1="220" x2="565" y2="220" stroke="currentColor" stroke-width="1.5"/>
  <line x1="60" y1="20" x2="60" y2="220" stroke="currentColor" stroke-width="1.5"/>
  <text x="60" y="238" font-size="11" text-anchor="middle" fill="currentColor">0</text>
  <text x="185" y="238" font-size="11" text-anchor="middle" fill="currentColor">195</text>
  <text x="310" y="238" font-size="11" text-anchor="middle" fill="currentColor">390</text>
  <text x="435" y="238" font-size="11" text-anchor="middle" fill="currentColor">585</text>
  <text x="560" y="238" font-size="11" text-anchor="middle" fill="currentColor">780</text>
  <text x="310" y="260" font-size="12" text-anchor="middle" fill="currentColor">days after opposition</text>
  <text x="52" y="224" font-size="11" text-anchor="end" fill="currentColor">0</text>
  <text x="52" y="157" font-size="11" text-anchor="end" fill="currentColor">8</text>
  <text x="52" y="91" font-size="11" text-anchor="end" fill="currentColor">16</text>
  <text x="52" y="24" font-size="11" text-anchor="end" fill="currentColor">24</text>
  <line x1="56" y1="153" x2="60" y2="153" stroke="currentColor"/>
  <line x1="56" y1="87" x2="60" y2="87" stroke="currentColor"/>
  <line x1="56" y1="20" x2="60" y2="20" stroke="currentColor"/>
  <text x="20" y="120" font-size="12" text-anchor="middle" fill="currentColor" transform="rotate(-90 20 120)">minutes one way</text>
  <line x1="60" y1="137" x2="560" y2="137" stroke="#9cc9ea" stroke-width="1.5" stroke-dasharray="6 4"/>
  <text x="310" y="153" font-size="11" text-anchor="middle" fill="currentColor">10 minutes</text>
  <polyline points="60,184 68,183 77,180 85,175 93,169 102,163 110,156 118,149 127,142 135,134 143,127 152,120 160,113 168,106 177,100 185,94 193,88 202,82 210,77 218,72 227,67 235,63 243,60 252,56 260,53 268,51 277,49 285,47 293,46 302,45 310,45 318,45 327,46 335,47 343,49 352,51 360,53 368,56 377,60 385,63 393,67 402,72 410,77 418,82 427,88 435,94 443,100 452,106 460,113 468,120 477,127 485,134 493,142 502,149 510,156 518,163 527,169 535,175 543,180 552,183 560,184" fill="none" stroke="#eea66f" stroke-width="3"/>
  <text x="310" y="38" font-size="11" text-anchor="middle" fill="currentColor">21.0 at conjunction</text>
  <text x="72" y="206" font-size="11" fill="currentColor">4.4 at opposition</text>
</svg>
<figcaption>Figure 2.6. One-way light time between Earth and Mars over one synodic period, in the circular-orbit
model (computed by the program). Real eccentric orbits stretch the range to about 3 to 22 minutes.</figcaption>
</figure>

The thought experiment at the end of the program is deliberately crude: a rover drives one metre, sends its
images, and waits for a person on Earth to approve the next metre. In a four-hour driving window it covers 34 m at
the closest approach and 5 m near conjunction, against 240 m if it decides each metre on board. Real operations
are not organised this way, precisely because it would be so slow. In practice the ground team sends a plan for a
whole sol in one upload, and rover drivers on Earth examine the terrain images the rover sent the day before. Two
further facts make the delay worse in practice: rovers often relay their data through orbiting spacecraft that
pass overhead only at certain times, and Earth antennas are shared among many missions, so the useful round trip
is usually a day, not 45 minutes. Between uploads, whatever happens on Mars, the rover is on its own.

In the terms of this chapter: the rover's environment is partially observable, stochastic, sequential, dynamic and
continuous; the delay means that a human cannot be part of the fast loop of Figure 2.1. The rover must be an
agent, not a remote-controlled vehicle.

### What real rovers do on their own

Two pieces of real flight software show the agent designs of 2.4 at work. The facts below come from NASA and JPL
publications listed at the end.

**AutoNav: goal-based driving with a model.** Since Sojourner (1997), Mars rovers have had some ability to avoid
hazards by themselves. Spirit, Opportunity and Curiosity could drive in an autonomous navigation mode: the rover
takes stereo images, builds a local map of the terrain's slopes and rocks (its model), evaluates candidate paths
toward a goal location given by the ground team, drives a short distance, and repeats. On those rovers the
computation required the rover to stop and think between short drives, which made autonomous driving slow.
Perseverance (landed 2021) carries an enhanced AutoNav with dedicated hardware for image processing that lets it
plan while it moves, which Verma and colleagues (2023) describe as substantially increasing how far it can drive
in a sol. In 2.4's terms this is a model-based, goal-based agent: the operators set the goal, and the rover keeps a
terrain model and searches it for a safe path, with costs that penalise slopes and rocks (a utility-like trade-off;
Chapter 4, Section 4.6 builds a toy version).

**AEGIS: choosing science targets.** AEGIS (Autonomous Exploration for Gathering Increased Science), developed at
JPL, lets a rover choose its own science targets. After a drive, the rover takes images, finds candidate rocks in
them, ranks them by criteria the scientists set in advance (size, brightness, shape and so on), and points an
instrument at the best one, without waiting for Earth. It was first used on Opportunity in 2010 to aim a camera,
was deployed on Curiosity in 2016 to select targets for the ChemCam laser spectrometer (Francis and colleagues,
2017), and is used on Perseverance with SuperCam. In 2.4's terms, AEGIS is a utility-based agent with a utility
function written by scientists: it uses the time when the team on Earth cannot respond, turning hours that would
otherwise be idle into data.

Neither system is "general intelligence", and neither replaces the team: the scientists choose where to go and
what counts as interesting. What they show is the main point of this chapter. Once you fix the performance
measure and are honest about the environment's properties (here, a delay of many minutes, a partially observed
and changing terrain), the kind of agent you need follows.

<figure class="play" data-play="lighttime"><span class="ai-tag">AI-created</span><figcaption><b>Try it.</b> This page's light-time model: turn the angle between Earth and Mars and see the distance and the one-way radio time. Orbits are drawn as circles, as in the model.</figcaption></figure>

## Check yourself

??? question "1. Write a PEAS description for a spam filter. Then classify its environment by the seven properties of 2.3."

    Performance measure: fraction of spam caught, fraction of real mail wrongly blocked (weighted heavily, since a
    lost real email is worse), speed. Environment: the stream of incoming mail, the users, the spammers.
    Actuators: mark as spam, move to folder, let through. Sensors: the message text, headers, sender, links,
    attachments, user feedback ("not spam"). Properties: partially observable (the sender's intent is hidden);
    multi-agent and competitive (spammers adapt to the filter); stochastic; mostly episodic (each message is
    judged on its own, though learning makes it sequential over time); dynamic (spam changes); discrete
    (messages are strings); unknown at first (what spam looks like must be learned).

??? question "2. How many entries does a table-driven agent need for the vacuum world with a lifetime of 3 steps? Check the formula against a direct count."

    With $|\mathcal{P}| = 4$ and $T = 3$: $4 + 16 + 64 = 84$. The formula gives
    $(4^{4} - 4)/(4 - 1) = 252/3 = 84$. Each entry is a sequence of 1, 2 or 3 percepts, and there are $4^t$
    sequences of length $t$.

??? question "3. In the vacuum world under M1, suppose dirt can reappear: after each step, each clean square becomes dirty with probability 0.1. Is the reflex agent still optimal? Argue briefly."

    It is no longer guaranteed optimal by Theorem 2.1, whose proof used "clean squares stay clean", but it is still
    very good. Whenever it is on a dirty square it sucks, and otherwise it moves to check the other square, which
    is a sensible policy because it cannot see the other square. An agent with memory could do slightly better in
    some cases (for example, it knows the square it just cleaned is probably still clean), but with only one other
    square to check, moving there is a sensible use of a non-sucking step: NoOp gains nothing for certain, and
    moving can find dirt that has been unobserved for a while. Under M3 (with a move cost) the trade-off becomes real: it is worth moving only when the chance that
    the other square has become dirty is high enough, which needs memory of how long ago it was visited.

??? question "4. Prove that a consistent performance measure can still be gamed: give a measure for a delivery robot that sounds right but rewards a bad behaviour."

    Measure: "one point for each package marked delivered". A robot that can mark packages delivered without
    handing them over, or that takes packages out of the destination and re-delivers them, scores well. Another:
    "minus one point per minute late". A robot that refuses to accept packages it might deliver late never loses
    points. In both, the measure rewards a proxy (a status flag, the absence of lateness) instead of what we want
    (packages reaching people on time). The remedy is to measure outcomes in the environment as directly as
    possible, and to look for behaviours that score well without doing the task, exactly as the dumping agent did.

??? question "5. Classify by the seven properties: (a) solving a Sudoku; (b) playing backgammon online against people; (c) a robot sorting parcels on a conveyor belt."

    (a) Fully observable, single-agent, deterministic, sequential (each entry constrains later ones), static,
    discrete, known. (b) Fully observable (the board and dice are visible), multi-agent competitive, stochastic
    (dice), sequential, static (or semidynamic if there is a clock), discrete, known. (c) Partially observable
    (labels can be hidden, camera noise), single-agent (unless several robots share the belt), stochastic,
    episodic (each parcel is independent), dynamic (the belt keeps moving), continuous, known in its rules but
    with unknown parcel shapes to learn.

??? question "6. Why does the simple reflex agent of 2.4 get trapped in the top corridor? Find the cell where its rule has no preferred direction and describe what happens near it."

    G is at row 9, column 6. In the top corridor (row 1) the bearing is "south" plus "east" for columns left of 6
    and "south" plus "west" for columns right of 6; south is wall everywhere except column 1 and column 11. So at
    columns 2 to 5 the only good free direction is east, and at columns 7 to 10 it is west. At column 6 the
    bearing is only "south", which is wall, so the agent picks a random free direction (east or west), and the
    next step pulls it back toward column 6. So once it has entered the corridor east of column 1 it can never
    leave: its only random choices happen at column 6, and both lead back. A quick experiment with the code confirms it: of 300 runs
    with seed 5, 140 ended at the 200-step limit in row 1 and 122 in row 7.

??? question "7. Compute the expected time of the goal-based agent's route if the slip probability were 1/2 instead of 2/3. Which route would the utility-based agent choose then?"

    With slip probability 1/2 the success probability is $q = 1/2$, so by Lemma 2.2 each sand cell costs 2 steps on
    average. The sand route has 7 firm moves and 6 sand moves: $7 + 6 \times 2 = 19$ expected steps. The firm
    route costs 23. So the utility-based agent would now choose the sand route: 19 is less than 23. The break-even
    point is when $7 + 6/q = 23$, that is $q = 6/16 = 3/8$, a slip probability of $5/8$.

??? question "8. Write code: add a sixth agent to the grid world that knows the map but not the slip probability, and estimates it from its own experience. It starts by assuming no slipping, and after each attempted move into sand updates its estimate and replans from where it is. How well does it do, and what changes if it keeps its experience from one run to the next?"

    ```python
    import numpy as np
    import ch02_agents as A

    class Estimating:
        """Knows the map; estimates the slip probability from its own sand moves."""
        def __init__(self, rng):
            self.tries, self.slips = 1, 0            # prior: one success, no slips
            self.target = None
            self.replan(A.START)

        def replan(self, here):
            p = self.slips / self.tries
            cost = lambda q: 1 / (1 - p) if A.GRID[q[0]][q[1]] == "~" else 1.0
            saved, A.START = A.START, here           # plan() searches from A.START
            try:
                path, _ = A.plan(cost)
            finally:
                A.START = saved
            self.cells = {}
            for a in path:                           # cell -> action along the plan
                self.cells[here] = a
                dr, dc = A.MOVES[a]
                here = (here[0] + dr, here[1] + dc)

        def act(self, p):
            t = self.target
            if t is not None and A.GRID[t[0]][t[1]] == "~":
                self.tries += 1                      # we just tried to enter sand
                self.slips += (p != t)
                self.replan(p)
            a = self.cells[p]
            dr, dc = A.MOVES[a]
            self.target = (p[0] + dr, p[1] + dc)
            return a

    rng = np.random.default_rng(1)
    runs = [A.run(Estimating(rng), rng) for _ in range(500)]
    print("reached", sum(r[1] for r in runs), "mean steps", sum(r[0] for r in runs) / 500)

    agent = Estimating(rng)                          # now keep experience between runs
    steps = []
    for _ in range(500):
        agent.target = None
        agent.replan(A.START)
        steps.append(A.run(agent, rng)[0])
    print("with memory across runs: first run", steps[0],
          "mean of runs 2-500", sum(steps[1:]) / 499,
          "slip estimate", round(agent.slips / agent.tries, 3))
    ```

    Output (run next to `ch02_agents.py`):

    ```
    reached 500 mean steps 27.19
    with memory across runs: first run 28 mean of runs 2-500 23.0 slip estimate 0.682
    ```

    A fresh agent in every run does *worse* than the goal-based agent (27.2 against 25.2 steps). It starts
    optimistic, so it enters the sand; by the time it has seen enough slips to believe the sand is slow, it is
    already in it, and turning back costs even more, so it ploughs on, having also wasted steps on the way. That is
    the price of learning while acting. An agent that keeps its estimate between runs pays the price once (28 steps
    in its first run), estimates the slip probability at 0.682 (the true value is $2/3$), and from then on takes the
    firm route in exactly 23 steps. This is **model learning**: the agent knows the structure of the world and
    learns one of its parameters, and learning pays off over a lifetime rather than in one episode.

??? question "9. Using the circular-orbit model, at what angle $\\theta$ between the planets is the one-way light time exactly 10 minutes?"

    Ten light-minutes is $299\,792.458 \times 600 \approx 1.7988 \times 10^{8}$ km, or $1.2024$ AU. Solve
    $1.2024^2 = 1 + 1.5237^2 - 2 \times 1.5237 \cos\theta$: $1.4458 = 3.3217 - 3.0474\cos\theta$, so
    $\cos\theta = 0.6156$ and $\theta \approx 52.0$ degrees. The light time is above 10 minutes whenever the angle
    is between 52 and 308 degrees, that is for $(308 - 52)/360 \approx 0.71$ of the synodic period, which matches
    the program's "fraction of the time above 10 minutes: 0.71".

??? question "10. Which of the five agent designs is AEGIS closest to, and which parts of the learning-agent diagram would you need to add for it to improve its own target choices over the mission?"

    AEGIS is closest to a utility-based agent: it ranks candidate targets by a score built from features the
    scientists choose, and points the instrument at the highest-scoring one. To make it a learning agent you
    would add a critic (a measure of how valuable each chosen target turned out to be, for example the scientists'
    later rating of the data), a learning element that adjusts the ranking weights from that feedback, and a
    problem generator that sometimes picks a target the current ranking does not favour, to learn whether it was
    underrated. The performance element, the ranking itself, stays as it is.

??? question "11. Explain why an atomic representation makes the 'sand' fact in the grid world awkward to learn, and how a factored representation would help the learning agent."

    With atomic states, the Q-learning agent learns a separate value for every (cell, action) pair. Learning that
    "sand is slow" in one cell tells it nothing about another sand cell; it must discover the slowness separately
    at each one. With a factored state, say (row, column, terrain type), a learner could use a value function
    that depends on the features, for example a term for "the next cell is sand". Then experience in one sand
    cell generalises to all of them. This is **function approximation**, the step from tabular to modern
    reinforcement learning (Chapter 15, Section 15.4).

## What you learned

- An agent maps percept sequences to actions (the agent function); the agent program implements it in far less
  space than a table, which grows as $|\mathcal{P}|^{T}$.
- A rational agent maximises expected performance given its percepts and knowledge. That is not omniscience; it
  includes gathering information and learning.
- The performance measure decides what is rational. The reflex vacuum agent is provably optimal under "clean
  squares per step", useless under "clean squares minus moves", and beaten by a dirt-dumping agent under "dirt
  sucked up".
- Environments differ in seven properties (observable, agents, deterministic, episodic, static, discrete, known),
  and the hard end of each needs a more capable agent.
- Five designs build on each other: simple reflex, model-based (memory), goal-based (search), utility-based
  (expected utility) and learning (improvement from feedback); in one grid world they took 176.6, 32.0, 25.2, 23.0
  and finally 23.0 steps.
- States can be atomic, factored or structured; more expressive representations are more concise and harder to
  reason with.
- A radio signal takes about 3 to 22 minutes each way between Earth and Mars, so rovers drive and pick science
  targets themselves (AutoNav, AEGIS).

**Next:** [Chapter 3](03-Uninformed-Search.md) turns the goal-based agent's look-ahead into a precise algorithm:
problems as state spaces, and blind search through them with guarantees.

## Further reading

- S. Russell and P. Norvig, *Artificial Intelligence: A Modern Approach*, 4th ed., Pearson, 2020, Chapter 2
  (intelligent agents, the vacuum world, properties of environments, agent structures).
- D. Poole and A. Mackworth, *Artificial Intelligence: Foundations of Computational Agents*, 3rd ed., Cambridge
  University Press, 2023, Chapters 1 and 2 (agents and their architectures).
- H. A. Simon, "A behavioral model of rational choice", *Quarterly Journal of Economics* 69(1), 1955 (bounded
  rationality).
- R. S. Sutton and A. G. Barto, *Reinforcement Learning: An Introduction*, 2nd ed., MIT Press, 2018, Chapter 1
  (the agent-environment interface, learning from reward).
- R. A. Brooks, "Intelligence without representation", *Artificial Intelligence* 47, 1991 (the case for reactive
  agents built from layers of reflexes).
- T. A. Estlin, B. J. Bornstein, D. M. Gaines, R. C. Anderson, D. R. Thompson, M. Burl, R. Castaño and M. Judd,
  "AEGIS automated science targeting for the MER Opportunity rover", *ACM Transactions on Intelligent Systems and
  Technology* 3(3), 2012.
- R. Francis, T. Estlin, G. Doran, S. Johnstone, D. Gaines, V. Verma, M. Burl, J. Frydenvang, S. Montaño, R. C.
  Wiens, S. Schaffer, O. Gasnault, L. DeFlores, D. Blaney and B. Bornstein, "AEGIS autonomous targeting for ChemCam
  on Mars Science Laboratory: deployment and results of initial science team use", *Science Robotics* 2(7), 2017.
- V. Verma and colleagues, "Autonomous robotics is driving Perseverance rover's progress on Mars", *Science
  Robotics* 8(80), 2023.
- M. Maimone, Y. Cheng and L. Matthies, "Two years of visual odometry on the Mars Exploration Rovers", *Journal of
  Field Robotics* 24(3), 2007.
- On this site: [Breadth-first search](../../graphs/bfs.md) and [Dijkstra's algorithm](../../graphs/dijkstra.md)
  (the goal-based and utility-based agents' planners), and
  [Chapter 1 of the Machine learning book](../machine-learning/01-What-Is-Machine-Learning.md) (kinds of learning).
