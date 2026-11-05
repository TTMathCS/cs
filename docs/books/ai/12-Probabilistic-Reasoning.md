# 12. Probabilistic reasoning and Bayesian networks

*The logic of Chapters [8](08-Propositional-Logic-and-SAT.md) and [9](09-First-Order-Logic.md) knows only true, false
and "not known". A rover that finds its drive fell short does not know why: a dust storm, a wheel fault, soft sand. It
has to weigh the explanations, act on the most likely one and change its mind when a new observation arrives. This
chapter answers the question: how can an agent reason correctly when it is uncertain? You will see why probability
is the right language for degrees of belief, compute with full joint distributions and Bayes' rule, build a Bayesian
network that stores the same knowledge in a handful of numbers, write exact inference (enumeration and variable
elimination) and three sampling methods from scratch, test d-separation against the numbers, and finish with the
difference between seeing and doing: causal networks and Pearl's do-operator.*

!!! abstract "In this chapter"
    **You will learn:**

    - why logic alone fails under uncertainty, and why degrees of belief should obey the laws of probability (the
      Dutch book argument and Cox's theorem, in outline)
    - how to answer any question from a full joint distribution (marginalising, conditioning, normalising), what
      independence and conditional independence buy, and Bayes' rule on a medical test, worked two ways
    - what a Bayesian network is, why its product of local tables is a correct joint distribution, and how to read
      independences off the graph with d-separation
    - exact inference by enumeration and by variable elimination, with a proof that it is correct, its cost in terms
      of the elimination order, and why exact inference is NP-hard in general
    - approximate inference by rejection sampling, likelihood weighting and Gibbs sampling, with why each one
      converges to the right answer and how fast
    - the difference between observing and intervening: causal networks, the do-operator, the back-door adjustment
      and Simpson's paradox

    **You need:** basic probability (events, conditional probability), as in the Probability book's
    [Conditional probability and independence](https://math.akadian.ca/books/probability/03-Conditional-Probability-and-Independence.html)
    and [Bayes' theorem](https://math.akadian.ca/books/probability/04-Bayes-Theorem.html) at math.akadian.ca;
    [Chapter 8](08-Propositional-Logic-and-SAT.md) (propositional logic, SAT) for the hardness proof in 12.4;
    directed acyclic graphs and graph search from the Algorithms book's
    [Chapter 15](../algorithms/15-Graphs-and-Graph-Search.md); a little NumPy.

    **Levels:** 12.1 and 12.2 are beginner; 12.3 and 12.4 are intermediate, with advanced proofs; 12.5 is
    intermediate to advanced; 12.6 is advanced.

## 12.1 Why logic is not enough under uncertainty; probability as degree of belief

### A rule that is almost always true

Try to write in logic the rule a rover's fault monitor would like to use:

$$
\forall d\; \mathit{ShortDrive}(d) \Rightarrow \mathit{WheelFault}(d).
$$

It is false. Most short drives have other causes: a dust storm that cut the power, soft sand, a hazard that made the
rover stop early. So we try to list them:

$$
\forall d\; \mathit{ShortDrive}(d) \Rightarrow \mathit{WheelFault}(d) \lor \mathit{Storm}(d) \lor
\mathit{SoftSand}(d) \lor \mathit{Hazard}(d) \lor \dots
$$

and the list never ends. Turning the rule round, as a causal rule, does not help either: a wheel fault does not
always make the drive short, because the rover may be on a gentle slope where the other five wheels manage. Russell
and Norvig name three reasons why logic fails here, and each one is real:

- **Laziness.** Listing every exception and every condition is far too much work, and the rules become too large to
  use.
- **Theoretical ignorance.** Nobody has a complete theory of the domain. Engineers do not know every way a wheel can
  fail.
- **Practical ignorance.** Even with a complete theory, the agent has not run every test. It cannot see the wheel
  from the inside.

The non-monotonic logics of [Chapter 11](11-Knowledge-Representation.md#114-default-reasoning-and-non-monotonic-logic)
give one answer: assume the normal case until told otherwise. But defaults have no strength. "Short drives are usually
storms" and "short drives are sometimes faults" cannot be weighed against each other, and two pieces of weak evidence
cannot add up to strong evidence. We need a number for how strongly we believe something, and rules for changing it.

### Degrees of belief

A **degree of belief** is a number between 0 and 1 that an agent attaches to a sentence: 1 means certain it is true,
0 certain it is false, 0.3 "probably not, but quite possible". This is the **Bayesian** or **subjective** reading of
probability: $P(\mathit{Storm}) = 0.1$ does not say that the world is random; it says how strongly this agent, with
its current knowledge, believes there is a storm. Another agent with other knowledge may have another number, and
both can be rational. The **frequentist** reading, where a probability is the long-run fraction of times an event
happens in repeated trials, fits dice and fits our medical test in 12.2. For an agent the subjective reading is the
natural one, because it applies to single events ("is there a storm now?") and it changes as evidence arrives.

The probability of a sentence given what the agent has observed is a **conditional probability**, written
$P(a \mid b)$ and read "the probability of $a$ given $b$". It is defined, whenever $P(b) > 0$, as

$$
P(a \mid b) = \frac{P(a \land b)}{P(b)}.
$$

Before any evidence the agent has a **prior** probability $P(a)$; after observing $b$ it has the **posterior**
$P(a \mid b)$. Probability theory says nothing about where the prior comes from (it may come from data, from experts
or from symmetry), but it fixes exactly how beliefs must change once the evidence is in.

### The axioms, and why a rational agent obeys them

Kolmogorov's axioms (1933) say: every probability is between 0 and 1; a sentence that is always true has probability
1; and for two sentences that cannot both be true, $P(a \lor b) = P(a) + P(b)$. From these follows the general
**inclusion-exclusion** rule

$$
P(a \lor b) = P(a) + P(b) - P(a \land b),
$$

and $P(\lnot a) = 1 - P(a)$. Why should beliefs obey these rules, rather than some other calculus? Two arguments are
classical.

**The Dutch book argument** (de Finetti, 1931 and 1937). Treat a degree of belief $p$ in $a$ as the price at which
the agent will buy or sell a ticket that pays 1 if $a$ is true. Suppose an agent's beliefs break an axiom, say
$P(a) = 0.4$ and $P(\lnot a) = 0.4$, so they sum to 0.8 instead of 1. The agent thinks each ticket is fairly priced
at 0.4, so it will sell both: an opponent buys from the agent one ticket on $a$ and one on $\lnot a$, paying
$0.4 + 0.4 = 0.8$. Exactly one of $a$ and $\lnot a$ is true, so the agent must pay out 1 and loses 0.2
whatever happens. A set of bets that loses in every possible world is a **Dutch book**. De Finetti proved that an
agent can be offered a Dutch book exactly when its beliefs break the axioms: obeying the axioms is the same as never
being a sure loser.

**Cox's theorem** (1946) starts from a different place. Ask only that a degree of belief be a single real number,
that it agree with logic when things are certain, and that it be updated consistently (the belief in $a \land b$
depends only on the belief in $b$ and the belief in $a$ given $b$, and so on). Cox showed that any such calculus is a
relabelling of probability. The original proof needs extra regularity assumptions, and later authors (Halpern 1999)
showed a counterexample when they are dropped, so the honest summary is: under reasonable conditions, a consistent
calculus of plausibility is probability.

Neither argument says which numbers to use. They say that if the agent's numbers do not obey the axioms, something
is wrong. The rest of the chapter assumes they do.

### Random variables and the language we compute with

A **random variable** is a name for a quantity whose value the agent is uncertain about: $\mathit{Storm}$ (yes or
no), $\mathit{Battery}$ (low, medium, high). Each has a **domain** of possible values. In this chapter every variable
is **binary** (Boolean), with values 1 (true) and 0 (false), and we write $\mathit{storm}$ for
$\mathit{Storm} = 1$ and $\lnot \mathit{storm}$ for $\mathit{Storm} = 0$. A **probability distribution**
$\mathbf{P}(\mathit{Storm})$ (bold P) is the whole vector of probabilities, one for each value, here
$\langle 0.1, 0.9 \rangle$. An assignment of a value to every variable is a **possible world**, the probabilistic
counterpart of a model in logic ([Chapter 8](08-Propositional-Logic-and-SAT.md)). A probability model gives each
possible world a probability, and the probability of a sentence is the sum over the worlds where it is true. This is
the bridge: logic tells us which worlds a sentence picks out, and probability weighs those worlds.

!!! note "Uncertainty and the distance to Mars"
    A rover cannot ask Earth what went wrong after every drive: radio signals take about 3 to 22 minutes one way, and
    the ground team works on a daily cycle of plans. So rovers carry fault protection on board, and diagnosis under
    uncertainty is a natural use of the ideas in this chapter. The rover network below is an invented teaching example:
    its variables and numbers are made up to show the methods, not taken from any mission.

## 12.2 Full joint distributions; independence; Bayes' rule worked (medical test)

### The full joint distribution

Take three binary variables: $\mathit{Storm}$ (a dust storm today), $\mathit{Low}$ (solar power is low) and
$\mathit{Dark}$ (the navigation images are dark). There are $2^3 = 8$ possible worlds. The **full joint
distribution** $\mathbf{P}(\mathit{Storm}, \mathit{Low}, \mathit{Dark})$ gives a probability to each of them; the
eight numbers are non-negative and sum to 1. The program below types in such a table (the numbers are invented, but
chosen so that a storm makes both low power and dark images likely) and answers questions from it.

Every question about these variables can be answered from the table with three operations.

**Marginalising** (summing out). The probability of a sentence is the sum over the worlds where it holds. To get
$P(\mathit{low})$, add the four rows with $\mathit{Low} = 1$:

$$
P(\mathit{low}) = \sum_{s, d} P(\mathit{Storm} = s, \mathit{low}, \mathit{Dark} = d)
= 0.0560 + 0.0240 + 0.0045 + 0.0855 = 0.1700.
$$

The name comes from accountants' tables, where such sums were written in the margin.

**Conditioning.** $P(\mathit{storm} \mid \mathit{low}) = P(\mathit{storm} \land \mathit{low}) / P(\mathit{low})
= (0.0560 + 0.0240) / 0.1700 = 0.4706$. Seeing low power raises the belief in a storm from 0.1 to almost one half.

**Normalising.** In both $P(\mathit{storm} \mid \mathit{low})$ and $P(\lnot \mathit{storm} \mid \mathit{low})$ the
denominator is the same number $P(\mathit{low})$. So we can skip it: compute the unnormalised vector of
$P(\mathit{Storm} = s, \mathit{low})$ for each $s$ and scale it to sum to 1. We write this with a constant $\alpha$:

$$
\mathbf{P}(\mathit{Storm} \mid \mathit{low}) = \alpha\, \mathbf{P}(\mathit{Storm}, \mathit{low})
= \alpha\, \langle 0.0800, 0.0900 \rangle = \langle 0.4706, 0.5294 \rangle.
$$

In general, with query variable $X$, evidence $\mathbf{e}$ and the remaining **hidden** variables $\mathbf{Y}$,

$$
\mathbf{P}(X \mid \mathbf{e}) = \alpha \sum_{\mathbf{y}} \mathbf{P}(X, \mathbf{e}, \mathbf{y}).
$$

That one line is a complete inference algorithm. Its problem is size: with $n$ binary variables the table has $2^n$
entries, so 30 variables need about a billion numbers to store and to sum, and no expert could ever supply them.
The rest of the chapter is about avoiding the table.

```python
--8<-- "books/ai/ch12_joint_bayes.py"
```

```
1. The full joint distribution P(Storm, Low, Dark)
  Storm Low Dark   P
    1    1    1   0.0560
    1    1    0   0.0240
    1    0    1   0.0140
    1    0    0   0.0060
    0    1    1   0.0045
    0    1    0   0.0855
    0    0    1   0.0405
    0    0    0   0.7695
  total 1.0000
  P(Low) = 0.1700   (marginalise: sum over Storm and Dark)
  P(Storm | Low) = 0.4706
  P(Storm | Low, Dark) = 0.9256
  normalising: unnormalised [0.056  0.0045] -> [0.9256 0.0744]
  Low and Dark independent?  P(Low,Dark) = 0.0605 vs P(Low)P(Dark) = 0.0196
  ... but given Storm: P(Low,Dark|Storm) = 0.5600 = P(Low|Storm)P(Dark|Storm) = 0.5600

2. Bayes' rule: a test for a condition with prevalence 1 in 100
  P(+) = 0.9*0.01 + 0.05*0.99 = 0.0585
  P(condition | +) = 0.0090 / 0.0585 = 0.1538
  natural frequencies: of 10000 people, 100 have it and 90 of them test positive;
  of the 9900 who do not, 495 test positive. So 90 / (90 + 495) = 0.1538

3. Two positive results from conditionally independent tests
  0 positive test(s): odds 0.0101, probability 0.0100
  1 positive test(s): odds 0.1818, probability 0.1538
  2 positive test(s): odds 3.2727, probability 0.7660
  3 positive test(s): odds 58.9091, probability 0.9833
  simulation of 1,000,000 people: P(condition | both positive) = 0.7664
```

### Independence

Two variables are **independent** if knowing one tells nothing about the other: $P(a \mid b) = P(a)$, or
equivalently $P(a \land b) = P(a)\, P(b)$, for every pair of values. If the $n$ variables were all independent, the
joint would be the product of $n$ one-variable tables, $n$ numbers instead of $2^n - 1$. But in the program
$\mathit{Low}$ and $\mathit{Dark}$ are not independent: $P(\mathit{low} \land \mathit{dark}) = 0.0605$ while
$P(\mathit{low})\, P(\mathit{dark}) = 0.0196$. They go together, because both are caused by a storm. Full
independence is rare in the problems we care about: if the variables did not influence each other there would be
nothing to reason about.

### Conditional independence

What the program shows next is the useful kind. Once we know whether there is a storm, low power tells us nothing
more about dark images: $P(\mathit{low} \land \mathit{dark} \mid \mathit{storm}) = 0.56
= P(\mathit{low} \mid \mathit{storm})\, P(\mathit{dark} \mid \mathit{storm})$. We say $X$ and $Y$ are
**conditionally independent given** $Z$, written $X \perp Y \mid Z$, if

$$
\mathbf{P}(X, Y \mid Z) = \mathbf{P}(X \mid Z)\, \mathbf{P}(Y \mid Z)
$$

for every value of $Z$. Equivalently $\mathbf{P}(X \mid Y, Z) = \mathbf{P}(X \mid Z)$: once $Z$ is known, $Y$ is
irrelevant to $X$. This is the pattern of one cause with several effects, and it is everywhere. With it the joint
factors:

$$
\mathbf{P}(\mathit{Storm}, \mathit{Low}, \mathit{Dark}) =
\mathbf{P}(\mathit{Storm})\, \mathbf{P}(\mathit{Low} \mid \mathit{Storm})\, \mathbf{P}(\mathit{Dark} \mid \mathit{Storm}),
$$

which needs $1 + 2 + 2 = 5$ numbers instead of 7. That is exactly how the program built its table. With one cause
and $n$ conditionally independent effects the count is $2n + 1$ instead of $2^{n+1} - 1$: linear instead of
exponential.

### Bayes' rule

Write the product rule two ways, $P(a \land b) = P(a \mid b)\, P(b) = P(b \mid a)\, P(a)$, and divide by $P(b)$:

$$
P(a \mid b) = \frac{P(b \mid a)\, P(a)}{P(b)}.
$$

This is **Bayes' rule**, named after Thomas Bayes, whose essay on the problem was published after his death, in
1763, by Richard Price; Laplace developed it independently and much further. It looks like a trivial rewriting, and
it is, but it lets us turn knowledge in the direction it is usually available into the direction we need it. Causal
knowledge, "a storm makes low power likely", is $P(\mathit{effect} \mid \mathit{cause})$, and it is stable: it does
not change if storms become more common. Diagnosis needs $P(\mathit{cause} \mid \mathit{effect})$. Bayes' rule
connects them:

$$
P(\mathit{cause} \mid \mathit{effect}) =
\frac{P(\mathit{effect} \mid \mathit{cause})\, P(\mathit{cause})}{P(\mathit{effect})}.
$$

The parts have names. $P(\mathit{cause})$ is the **prior**, $P(\mathit{effect} \mid \mathit{cause})$ the
**likelihood** and $P(\mathit{cause} \mid \mathit{effect})$ the **posterior**; the denominator $P(\mathit{effect})$
is found by summing the numerator over both values of the cause, which is the normalisation of the previous section.

### Worked example: a medical test

A condition affects 1 person in 100. A test for it has **sensitivity** 0.90 (of people with the condition, 90 percent
test positive) and **specificity** 0.95 (of people without it, 95 percent test negative, so 5 percent get a **false
positive**). These numbers are invented for the example. A person tests positive. How likely is it that they have the
condition?

Many people answer "about 90 percent". Work it out. Let $C$ be the condition and $+$ a positive test. Then

$$
\begin{aligned}
P(+) &= P(+ \mid c)\, P(c) + P(+ \mid \lnot c)\, P(\lnot c) = 0.90 \times 0.01 + 0.05 \times 0.99 = 0.0585,\\
P(c \mid +) &= \frac{0.90 \times 0.01}{0.0585} = \frac{0.0090}{0.0585} = 0.1538.
\end{aligned}
$$

About 15 percent. The same calculation in **natural frequencies**, which Gigerenzer and Hoffrage (1995) found people
handle far better than percentages: of 10,000 people, 100 have the condition and 90 of them test positive; of the
9,900 who do not, 495 test positive. Of the 585 positives, only 90 are real, and $90 / 585 = 0.1538$. The false
positives win because the healthy group is 99 times larger. Ignoring the prior like this is called **base-rate
neglect**.

### Combining evidence: odds and likelihood ratios

A second, independent test is done and is also positive. Bayes' rule is easiest to repeat in **odds** form. The odds
of $c$ are $O(c) = P(c) / P(\lnot c)$. Divide Bayes' rule for $c$ by Bayes' rule for $\lnot c$; the denominator
$P(+)$ cancels:

$$
O(c \mid +) = \frac{P(+ \mid c)}{P(+ \mid \lnot c)}\, O(c) = \Lambda\, O(c).
$$

The factor $\Lambda = 0.90 / 0.05 = 18$ is the test's **likelihood ratio**. The prior odds are $1/99 = 0.0101$; one
positive gives odds $0.1818$, which is probability 0.1538 as before; two positives give $18^2 / 99 = 3.2727$, which
is probability $3.2727 / 4.2727 = 0.7660$. Multiplying the ratios is correct only if the two results are
conditionally independent given the condition (the second test's errors do not depend on the first test's), and the
program's simulation of a million people, built that way, agrees: 0.7664. This "multiply the evidence" rule with
conditionally independent effects is the **naive Bayes** model; it is called naive because it assumes the
independence even when it is false, and it works surprisingly well as a classifier anyway (the Machine learning
book's [Chapter 12](../machine-learning/12-Probabilistic-Models.md) studies it as a learning method).

<figure class="play" data-play="medtest"><span class="ai-tag">AI-created</span><figcaption><b>Try it.</b> The medical test above as 10,000 people: change how common the condition is and how good the test is, and see how often a positive is real.</figcaption></figure>

## 12.3 Bayesian networks (Pearl 1988): structure, conditional independence, d-separation

### The idea: write down only the direct influences

Conditional independence made the three-variable table smaller. A **Bayesian network** does the same for any number
of variables, by drawing which variables influence which. Judea Pearl developed the idea in a series of papers from
1982 and set it out in his book *Probabilistic Reasoning in Intelligent Systems* (1988); similar graphical models had
been used before in genetics (Sewall Wright's path analysis, 1921) and in decision analysis (influence diagrams,
Howard and Matheson, 1981).

A Bayesian network has two parts.

1. A **directed acyclic graph** (DAG): one node per random variable, and an arrow $X \to Y$ when $X$ has a direct
   influence on $Y$. $X$ is then a **parent** of $Y$, and $Y$ a **child** of $X$. Acyclic means no chain of arrows
   leads from a node back to itself ([the Algorithms book, Chapter 15](../algorithms/15-Graphs-and-Graph-Search.md#154-topological-sort)
   shows how to test this and how to put the nodes in **topological order**, parents before children).
2. For each node $X_i$, a **conditional probability table** (CPT) giving
   $\mathbf{P}(X_i \mid \mathit{Parents}(X_i))$: one distribution over $X_i$ for each combination of parent values.
   A node with no parents gets just its prior.

Our running example extends the storm table to six variables. A dust storm ($\mathit{Storm}$) makes solar power low
($\mathit{Low}$) and images dark ($\mathit{Dark}$), and it can make the day's drive fall short ($\mathit{Slow}$). A
wheel motor fault ($\mathit{Fault}$) can also make the drive short. A short drive sends an alert to the ground team
($\mathit{Alert}$), with a small rate of false alerts. Figure 12.1 shows the graph and all its numbers, which are
invented for the example.

<figure class="mars-fig" markdown="0">
<svg viewBox="0 0 640 290" role="img" aria-label="The rover diagnosis Bayesian network. Storm has arrows to Low, Dark and Slow. Fault has an arrow to Slow. Slow has an arrow to Alert. Each node shows its table: P(storm) 0.1; P(fault) 0.05; P(low given storm) 0.8, given no storm 0.1; P(dark given storm) 0.7, given no storm 0.05; P(slow) is 0.95 with storm and fault, 0.6 with storm only, 0.7 with fault only, 0.05 with neither; P(alert given slow) 0.9, given not slow 0.02.">
<line x1="189.7" y1="56.0" x2="97.4" y2="128.5" stroke="currentColor" stroke-width="1.5"/>
<polygon points="90.3,134.0 95.4,124.3 101.0,131.4" fill="currentColor"/>
<line x1="210.8" y1="58.0" x2="213.8" y2="123.0" stroke="currentColor" stroke-width="1.5"/>
<polygon points="214.2,132.0 209.2,122.2 218.2,121.8" fill="currentColor"/>
<line x1="234.5" y1="55.0" x2="357.8" y2="130.3" stroke="currentColor" stroke-width="1.5"/>
<polygon points="365.5,135.0 354.6,133.7 359.3,126.0" fill="currentColor"/>
<line x1="457.5" y1="57.3" x2="407.8" y2="125.5" stroke="currentColor" stroke-width="1.5"/>
<polygon points="402.5,132.7 404.8,122.0 412.1,127.3" fill="currentColor"/>
<line x1="390.0" y1="168.0" x2="390.0" y2="218.0" stroke="currentColor" stroke-width="1.5"/>
<polygon points="390.0,227.0 385.5,217.0 394.5,217.0" fill="currentColor"/>
<ellipse cx="210" cy="40" rx="44" ry="18" fill="#eea66f" fill-opacity="0.5" stroke="currentColor"/>
<text x="210" y="45" font-size="13" text-anchor="middle" fill="currentColor">Storm</text>
<ellipse cx="470" cy="40" rx="44" ry="18" fill="#eea66f" fill-opacity="0.5" stroke="currentColor"/>
<text x="470" y="45" font-size="13" text-anchor="middle" fill="currentColor">Fault</text>
<ellipse cx="70" cy="150" rx="44" ry="18" fill="#9cc9ea" fill-opacity="0.5" stroke="currentColor"/>
<text x="70" y="155" font-size="13" text-anchor="middle" fill="currentColor">Low</text>
<ellipse cx="215" cy="150" rx="44" ry="18" fill="#9cc9ea" fill-opacity="0.5" stroke="currentColor"/>
<text x="215" y="155" font-size="13" text-anchor="middle" fill="currentColor">Dark</text>
<ellipse cx="390" cy="150" rx="44" ry="18" fill="#9cc9ea" fill-opacity="0.5" stroke="currentColor"/>
<text x="390" y="155" font-size="13" text-anchor="middle" fill="currentColor">Slow</text>
<ellipse cx="390" cy="245" rx="44" ry="18" fill="#9cc9ea" fill-opacity="0.5" stroke="currentColor"/>
<text x="390" y="250" font-size="13" text-anchor="middle" fill="currentColor">Alert</text>
<text x="262" y="32" font-size="12" text-anchor="start" fill="currentColor">P(storm) = 0.1</text>
<text x="522" y="32" font-size="12" text-anchor="start" fill="currentColor">P(fault) = 0.05</text>
<text x="70" y="184" font-size="12" text-anchor="middle" fill="currentColor">P(low | storm) = 0.8</text>
<text x="70" y="200" font-size="12" text-anchor="middle" fill="currentColor">P(low | no storm) = 0.1</text>
<text x="215" y="218" font-size="12" text-anchor="middle" fill="currentColor">P(dark | storm) = 0.7</text>
<text x="215" y="234" font-size="12" text-anchor="middle" fill="currentColor">P(dark | no) = 0.05</text>
<text x="450" y="118" font-size="12" text-anchor="start" fill="currentColor">P(slow | storm, fault) = 0.95</text>
<text x="450" y="134" font-size="12" text-anchor="start" fill="currentColor">P(slow | storm, no fault) = 0.6</text>
<text x="450" y="166" font-size="12" text-anchor="start" fill="currentColor">P(slow | no storm, fault) = 0.7</text>
<text x="450" y="182" font-size="12" text-anchor="start" fill="currentColor">P(slow | neither) = 0.05</text>
<text x="442" y="240" font-size="12" text-anchor="start" fill="currentColor">P(alert | slow) = 0.9</text>
<text x="442" y="256" font-size="12" text-anchor="start" fill="currentColor">P(alert | not slow) = 0.02</text>
</svg>
<figcaption>Figure 12.1. The rover network: six binary variables, five arrows and twelve numbers. Each table gives
the probability that the node is true for each combination of its parents' values.</figcaption>
</figure>

### Why the product of the tables is the joint

The network defines a joint distribution by one formula, the **chain rule for Bayesian networks**:

$$
P(x_1, \dots, x_n) = \prod_{i=1}^{n} P(x_i \mid \mathit{parents}(X_i)).
$$

For instance, the world where a storm and no fault give low power, dark images, a short drive and an alert has
probability $0.1 \times 0.95 \times 0.8 \times 0.7 \times 0.6 \times 0.9 = 0.0287$.

Two things need proof: that this is a probability distribution, and in what sense it is the right one.

**It is a distribution.** Every factor is non-negative, so the product is. To see that it sums to 1, put the
variables in topological order, so the last variable $X_n$ is a child of no one. Sum over $x_n$ first: only the last
factor mentions $x_n$, and $\sum_{x_n} P(x_n \mid \mathit{parents}(X_n)) = 1$ because each row of a CPT is a
distribution. What remains is the product for the network with $X_n$ removed, and induction on $n$ finishes the
proof. The program checks it numerically: the 64 products sum to 1.000000.

**It is what the graph says.** The general **chain rule** of probability, which holds for any distribution and any
order, is

$$
P(x_1, \dots, x_n) = \prod_{i=1}^{n} P(x_i \mid x_{i-1}, \dots, x_1).
$$

Comparing the two formulas, the network's product equals the true joint exactly when, in a topological order,

$$
\mathbf{P}(X_i \mid X_{i-1}, \dots, X_1) = \mathbf{P}(X_i \mid \mathit{Parents}(X_i)),
$$

that is, each variable is conditionally independent of its other predecessors given its parents. This is the
meaning of a Bayesian network, and it tells us how to build one: order the variables (causes before effects works
best), and for each one choose as parents a smallest set of earlier variables that makes it independent of the
rest of the earlier ones. A stronger statement, the **local Markov property**, also follows: every node is
conditionally independent of its non-descendants given its parents.

### What it saves

Six binary variables need $2^6 - 1 = 63$ numbers in a full joint. The network needs one number per CPT row:
$1 + 1 + 2 + 2 + 4 + 2 = 12$. In general a node with $k$ binary parents needs $2^k$ numbers, so a network of $n$
nodes with at most $k$ parents each needs at most $n 2^k$ numbers instead of $2^n - 1$. That is the difference
between possible and impossible, and the numbers are also easier to get: an engineer can estimate
"$P(\mathit{slow} \mid \mathit{storm}, \lnot\mathit{fault})$", a local causal question, much more reliably than the
probability of a whole world.

Order matters. If we added the variables in the diagnostic order ($\mathit{Alert}$ first, then $\mathit{Slow}$, and
so on back to the causes), we would need extra arrows, for example between $\mathit{Storm}$ and $\mathit{Fault}$,
which are independent a priori but become dependent once $\mathit{Slow}$ is known, and the tables would ask for
unnatural numbers like $P(\mathit{fault} \mid \mathit{slow}, \mathit{storm})$. The causal order usually gives the
sparsest network.

### Three connections

Which independences does a graph imply, beyond the local Markov property? Everything reduces to how information
flows through a single middle node $Z$ on a path between $X$ and $Y$. Figure 12.2 shows the three cases.

<figure class="mars-fig" markdown="0">
<svg viewBox="0 0 640 250" role="img" aria-label="Three ways a path can pass through a middle node Z. Chain: X to Z to Y, blocked if Z is observed. Fork: Z points to both X and Y, blocked if Z is observed. Collider: X and Y both point to Z, blocked unless Z or a descendant of Z is observed.">
<line x1="55.7" y1="71.2" x2="87.0" y2="93.6" stroke="currentColor" stroke-width="1.5"/>
<polygon points="94.3,98.8 83.6,96.6 88.8,89.3" fill="currentColor"/>
<line x1="125.7" y1="121.2" x2="157.0" y2="143.6" stroke="currentColor" stroke-width="1.5"/>
<polygon points="164.3,148.8 153.6,146.6 158.8,139.3" fill="currentColor"/>
<ellipse cx="40" cy="60" rx="22" ry="16" fill="#9cc9ea" fill-opacity="0.5" stroke="currentColor"/>
<text x="40" y="65" font-size="13" text-anchor="middle" fill="currentColor">X</text>
<ellipse cx="110" cy="110" rx="22" ry="16" fill="#7ccf9a" fill-opacity="0.6" stroke="currentColor"/>
<text x="110" y="115" font-size="13" text-anchor="middle" fill="currentColor">Z</text>
<ellipse cx="180" cy="160" rx="22" ry="16" fill="#9cc9ea" fill-opacity="0.5" stroke="currentColor"/>
<text x="180" y="165" font-size="13" text-anchor="middle" fill="currentColor">Y</text>
<text x="110" y="22" font-size="13" text-anchor="middle" fill="currentColor">chain</text>
<line x1="310.0" y1="74.3" x2="265.1" y2="138.4" stroke="currentColor" stroke-width="1.5"/>
<polygon points="260.0,145.7 262.0,135.0 269.4,140.1" fill="currentColor"/>
<line x1="330.0" y1="74.3" x2="374.9" y2="138.4" stroke="currentColor" stroke-width="1.5"/>
<polygon points="380.0,145.7 370.6,140.1 378.0,135.0" fill="currentColor"/>
<ellipse cx="250" cy="160" rx="22" ry="16" fill="#9cc9ea" fill-opacity="0.5" stroke="currentColor"/>
<text x="250" y="165" font-size="13" text-anchor="middle" fill="currentColor">X</text>
<ellipse cx="320" cy="60" rx="22" ry="16" fill="#7ccf9a" fill-opacity="0.6" stroke="currentColor"/>
<text x="320" y="65" font-size="13" text-anchor="middle" fill="currentColor">Z</text>
<ellipse cx="390" cy="160" rx="22" ry="16" fill="#9cc9ea" fill-opacity="0.5" stroke="currentColor"/>
<text x="390" y="165" font-size="13" text-anchor="middle" fill="currentColor">Y</text>
<text x="320" y="22" font-size="13" text-anchor="middle" fill="currentColor">fork</text>
<line x1="470.0" y1="74.3" x2="514.9" y2="138.4" stroke="currentColor" stroke-width="1.5"/>
<polygon points="520.0,145.7 510.6,140.1 518.0,135.0" fill="currentColor"/>
<line x1="590.0" y1="74.3" x2="545.1" y2="138.4" stroke="currentColor" stroke-width="1.5"/>
<polygon points="540.0,145.7 542.0,135.0 549.4,140.1" fill="currentColor"/>
<ellipse cx="460" cy="60" rx="22" ry="16" fill="#9cc9ea" fill-opacity="0.5" stroke="currentColor"/>
<text x="460" y="65" font-size="13" text-anchor="middle" fill="currentColor">X</text>
<ellipse cx="530" cy="160" rx="22" ry="16" fill="#7ccf9a" fill-opacity="0.6" stroke="currentColor"/>
<text x="530" y="165" font-size="13" text-anchor="middle" fill="currentColor">Z</text>
<ellipse cx="600" cy="60" rx="22" ry="16" fill="#9cc9ea" fill-opacity="0.5" stroke="currentColor"/>
<text x="600" y="65" font-size="13" text-anchor="middle" fill="currentColor">Y</text>
<text x="530" y="22" font-size="13" text-anchor="middle" fill="currentColor">collider</text>
<text x="110" y="205" font-size="12" text-anchor="middle" fill="currentColor">X → Z → Y</text>
<text x="110" y="222" font-size="12" text-anchor="middle" fill="currentColor">blocked if Z is observed</text>
<text x="320" y="205" font-size="12" text-anchor="middle" fill="currentColor">X ← Z → Y</text>
<text x="320" y="222" font-size="12" text-anchor="middle" fill="currentColor">blocked if Z is observed</text>
<text x="530" y="205" font-size="12" text-anchor="middle" fill="currentColor">X → Z ← Y</text>
<text x="530" y="222" font-size="12" text-anchor="middle" fill="currentColor">blocked unless Z or a</text>
<text x="530" y="238" font-size="12" text-anchor="middle" fill="currentColor">descendant is observed</text>
</svg>
<figcaption>Figure 12.2. The three connections. In a chain and a fork, observing the middle node blocks the flow of
information; in a collider (head to head), the flow is blocked until the middle node, or one of its descendants, is
observed.</figcaption>
</figure>

- **Chain** $X \to Z \to Y$, like $\mathit{Storm} \to \mathit{Slow} \to \mathit{Alert}$. A storm makes an alert more
  likely, but only through the short drive. Once we know whether the drive was short, the storm tells us nothing
  more about the alert: $X \perp Y \mid Z$.
- **Fork** $X \leftarrow Z \to Y$, like $\mathit{Low} \leftarrow \mathit{Storm} \to \mathit{Dark}$. The two effects
  are dependent (both point to a storm) but independent given the common cause, as 12.2 showed.
- **Collider** $X \to Z \leftarrow Y$, like $\mathit{Storm} \to \mathit{Slow} \leftarrow \mathit{Fault}$. The two
  causes are independent: a storm does not make a wheel fault more or less likely. But once we learn the drive was
  short, they become dependent. If we also learn there was a storm, the storm **explains away** the short drive and
  the fault becomes less likely.

The explaining-away effect is worth checking with numbers from the network. Given only a short drive,
$P(\mathit{fault} \mid \mathit{slow}) = 0.2665$, up from the prior 0.05. Add the storm:
$P(\mathit{fault} \mid \mathit{slow}, \mathit{storm}) = 0.0769$. Turned the other way,
$P(\mathit{storm} \mid \mathit{slow}) = 0.4540$, which falls to 0.1310 if we learn there is a fault and rises to
0.5714 if we learn there is none. No logic of defaults reproduces this behaviour, and people do it all the time.
Observing a descendant of the collider has the same effect, more weakly: an alert also makes $\mathit{Storm}$ and
$\mathit{Fault}$ dependent, because the alert is evidence about $\mathit{Slow}$.

### d-separation

A **path** (trail) between $X$ and $Y$ is a sequence of nodes joined by arrows, in either direction. Given a set
$\mathbf{Z}$ of observed variables, a path is **blocked** if it has a middle node $W$ such that either

- $W$ is a chain or fork node on the path and $W \in \mathbf{Z}$, or
- $W$ is a collider on the path and neither $W$ nor any descendant of $W$ is in $\mathbf{Z}$.

A path that is not blocked is **active**. $X$ and $Y$ are **d-separated** by $\mathbf{Z}$ ("d" for directional) if
every path between them is blocked.

**Theorem** (Verma and Pearl, 1988; Geiger and Pearl, 1988). If $X$ and $Y$ are d-separated by $\mathbf{Z}$,
then $X \perp Y \mid \mathbf{Z}$ in every distribution that factors according to the graph (soundness). If they are
not d-separated, there is some choice of CPTs for which they are dependent given $\mathbf{Z}$ (completeness); in fact,
Meek (1995) showed the parameter choices that create extra independences have measure zero.

So d-separation finds exactly the independences that the graph guarantees, whatever the numbers. The soundness proof
is too long to give in full here; Koller and Friedman (2009, chapter 3) give it. The idea for one path is the three
cases above: in a chain or fork, conditioning on the middle node makes the two ends independent (we showed it for
the fork in 12.2, and the chain is the same calculation), and in a collider, summing out an unobserved middle node
that has no observed descendants leaves the two ends' factors separate. The general proof turns these local facts
into a factorisation of the joint.

Some examples on the rover network, each of which the program confirms numerically:

- $\mathit{Storm} \perp \mathit{Fault} \mid \{\}$: the only path is through the collider $\mathit{Slow}$, which is
  unobserved and has an unobserved descendant. Blocked.
- $\mathit{Storm} \not\perp \mathit{Fault} \mid \{\mathit{Alert}\}$: the collider's descendant $\mathit{Alert}$ is
  observed, so the path is active.
- $\mathit{Fault} \not\perp \mathit{Low} \mid \{\mathit{Alert}\}$: the path
  $\mathit{Fault} \to \mathit{Slow} \leftarrow \mathit{Storm} \to \mathit{Low}$ is active, because the collider has
  an observed descendant and the fork node $\mathit{Storm}$ is not observed. Low power is evidence for a storm, the
  storm explains the alert, and so low power lowers the belief in a fault (0.3085 without low power, 0.1177 with it,
  from the program).
- $\mathit{Fault} \perp \mathit{Low} \mid \{\mathit{Storm}, \mathit{Alert}\}$: now the fork node is observed, and the
  path is blocked.

### Testing d-separation by search

Enumerating all paths could take exponential time. Instead, the program does one graph search (Geiger, Verma and
Pearl 1990; the same idea is Shachter's "Bayes ball", 1998). First it marks the observed nodes and their ancestors,
which are exactly the colliders that would be active. Then it searches from $X$ over states (node, direction), where
the direction records whether we arrived from a child ("up") or from a parent ("down"):

- arriving **up** at an unobserved node, we may continue to its parents (chain upwards) and its children (fork);
- arriving **down** at an unobserved node, we may continue to its children (chain downwards);
- arriving **down** at a node that is observed or has an observed descendant, we may go back up to its parents
  (an active collider).

$Y$ is d-connected to $X$ exactly when the search reaches an unobserved $Y$. Each (node, direction) pair is visited
once and each arrow is followed a constant number of times, so the test runs in $O(n + m)$ time for $n$ nodes and
$m$ arrows, the cost of the breadth-first or depth-first searches in
[the Algorithms book's Chapter 15](../algorithms/15-Graphs-and-Graph-Search.md). Correctness follows because every
step is one of the three active connections, so the search follows exactly the active paths.

The program then does something we can rarely do with a theorem: it tests it. For every pair of the six variables
and every subset of the other four as conditioning set, it compares the graph's answer with numerical independence
in the joint table. They agree on all 240 tests.

### A word on what the graph does not say

The arrows we drew are causal: storms cause dark images. But the network's probabilities alone cannot tell causal
arrows from others. The graphs $X \to Y$ and $Y \to X$ imply the same (empty) set of independences and can represent
exactly the same joint distributions. For predicting from observations, any correct network will do; for predicting
the effect of changing something, the arrows must be causal. Section 12.6 takes this up.

## 12.4 Exact inference: enumeration, variable elimination from scratch

### The task

**Inference** means computing a posterior distribution $\mathbf{P}(X \mid \mathbf{e})$ for a query variable $X$
given observed values $\mathbf{e}$ of the evidence variables, summing over the hidden variables $\mathbf{Y}$. The
formula of 12.2, with the joint written as the network's product, is

$$
\mathbf{P}(X \mid \mathbf{e}) = \alpha \sum_{\mathbf{y}} \prod_{i} P(x_i \mid \mathit{parents}(X_i)).
$$

### Enumeration

The simplest algorithm evaluates the formula as written: for each value of $X$, loop over all assignments to the
hidden variables, multiply the CPT entries and add. The program's `enumerate_ask` does this. With $h$ hidden binary
variables it adds $2^h$ products of $n$ numbers, so the time is $O(n 2^h)$; the space is only $O(n)$. On six
variables that is nothing, on a hundred it is hopeless.

Trace a query by hand: the ground team gets an alert. What is the probability of a wheel fault? The hidden variables
are $\mathit{Storm}$, $\mathit{Low}$, $\mathit{Dark}$ and $\mathit{Slow}$. Pull each factor as far left as it goes:

$$
P(\mathit{fault}, \mathit{alert}) = P(\mathit{fault}) \sum_{\mathit{slow}} P(\mathit{alert} \mid \mathit{slow})
\sum_{s} P(s)\, P(\mathit{slow} \mid s, \mathit{fault}) \sum_{l} P(l \mid s) \sum_{d} P(d \mid s).
$$

The two innermost sums are 1, because they sum a CPT row over the child's values. So the dark-images and low-power
nodes drop out: they are **barren**, with no evidence at or below them. What remains:

| $\mathit{Fault}$ | $\mathit{Slow}$ | $\sum_s P(s) P(\mathit{Slow} \mid s, \mathit{Fault})$ | $P(\mathit{alert} \mid \mathit{Slow})$ |
|---|---|---|---|
| 1 | 1 | $0.1 \times 0.95 + 0.9 \times 0.7 = 0.725$ | 0.9 |
| 1 | 0 | $0.275$ | 0.02 |
| 0 | 1 | $0.1 \times 0.6 + 0.9 \times 0.05 = 0.105$ | 0.9 |
| 0 | 0 | $0.895$ | 0.02 |

For $\mathit{fault}$: $0.05 \times (0.725 \times 0.9 + 0.275 \times 0.02) = 0.05 \times 0.658 = 0.0329$. For
$\lnot \mathit{fault}$: $0.95 \times (0.105 \times 0.9 + 0.895 \times 0.02) = 0.95 \times 0.1124 = 0.10678$.
Normalising, $P(\mathit{fault} \mid \mathit{alert}) = 0.0329 / 0.13968 = 0.2355$, the program's number. The alert
raises the fault probability almost five times, but a storm remains the likelier explanation
($P(\mathit{storm} \mid \mathit{alert}) = 0.4034$).

Notice the waste in plain enumeration: the inner sums are recomputed for every value of the outer variables. The
remedy is the one [dynamic programming](../algorithms/13-Dynamic-Programming.md) always uses: compute each subresult
once and store it.

### Factors

A **factor** is a table of numbers indexed by the values of some set of variables. Each CPT is a factor; evidence
**restricts** a factor by fixing some of its indices. Two operations are all we need.

- **Pointwise product.** $f(\mathbf{A}, \mathbf{B}) \times g(\mathbf{B}, \mathbf{C})$ is the factor
  $h(\mathbf{A}, \mathbf{B}, \mathbf{C}) = f(\mathbf{a}, \mathbf{b})\, g(\mathbf{b}, \mathbf{c})$ over the union of
  the variables: entries that agree on the shared variables are multiplied. Its size is exponential in the number of
  variables in the union.
- **Summing out** a variable $B$ from $h$ gives the factor over the other variables with
  $\sum_b h(\dots, b, \dots)$.

The program's `Factor` class stores the table as a NumPy array with one axis per variable. The product is one call
to `np.einsum`, with a letter per variable: for $f$ over $(A, B)$ and $g$ over $(B, C)$ it is
`einsum("ab,bc->abc", f, g)`, which multiplies entries with the same $b$ and keeps all three indices. Summing out is
`table.sum(axis=i)`.

### Variable elimination

**Variable elimination** (Zhang and Poole, 1994; Dechter's bucket elimination, 1996, is the same algorithm) evaluates
the sum one hidden variable at a time:

1. Make one factor per CPT, restricted to the evidence.
2. For each hidden variable $H$, in some **elimination order**: multiply together all factors that mention $H$, sum
   $H$ out of the product, and put the new factor back in place of the ones used.
3. Multiply the remaining factors (they mention only the query variable) and normalise.

**Why it is correct.** The sum $\sum_{\mathbf{y}} \prod_i f_i$ is a sum of products. Summing out $H$ first, a factor
that does not mention $H$ is a constant in the inner sum and can be moved out: by the distributive law
$\sum_h a\, g(h) = a \sum_h g(h)$,

$$
\sum_h \prod_i f_i = \Big(\prod_{i: H \notin f_i} f_i\Big) \Big(\sum_h \prod_{i: H \in f_i} f_i\Big).
$$

The second bracket is exactly the new factor of step 2. So after each step the product of the factors in the pool,
summed over the variables not yet eliminated, still equals the original sum. By induction, after the last hidden
variable the pool's product is $\mathbf{P}(X, \mathbf{e})$, and normalising gives the answer. The program asserts
that enumeration and elimination agree on every query.

### Cost and the elimination order

Each step costs about the size of the product factor it builds, which is $2^w$ for a factor over $w$ variables. So
the total time is $O(n 2^{w})$, where $w$ is the largest factor created. The order decides $w$. The program shows it
on the alert query: eliminating $\mathit{Storm}$ first multiplies the tables of all its children,
$\mathit{Low}$, $\mathit{Dark}$ and $\mathit{Slow}$, into one factor over five variables; eliminating the leaves
$\mathit{Low}$ and $\mathit{Dark}$ first (their factors sum to all-ones, the barren nodes again), then $\mathit{Slow}$,
then $\mathit{Storm}$, never builds a factor over more than three.

The smallest possible $w$ over all orders, minus one, is a property of the graph called its **treewidth** (of the
undirected "moral" graph, where each node's parents are joined and arrows lose their direction). Inference by
variable elimination is linear in $n$ and exponential only in the treewidth. Two special cases are worth knowing:

- In a **polytree** (a network with at most one path between any two nodes, ignoring directions), the treewidth is at
  most the largest number of parents, and exact inference is linear in the total size of the CPTs. Pearl's original
  **belief propagation** algorithm (1982 and 1986) passes messages along the arrows and is exact on polytrees.
- For general networks, the **junction tree** algorithm (Lauritzen and Spiegelhalter, 1988) groups variables into
  clusters forming a tree and passes messages between them; it computes all posteriors at once, at a cost exponential
  in the cluster size.

Finding the best order is itself NP-hard (Arnborg, Corneil and Proskurowski, 1987), so in practice greedy rules are
used: at each step eliminate the variable whose product factor would be smallest ("min-weight") or which adds the
fewest new edges to the graph ("min-fill"). These are fast and usually good.

### Exact inference is NP-hard

Could a cleverer algorithm avoid the exponential in general? Almost certainly not.

**Theorem** (Cooper, 1990). Deciding whether $P(X = 1) > 0$ in a Bayesian network is NP-hard.

*Proof.* Reduce 3-SAT ([Chapter 8](08-Propositional-Logic-and-SAT.md), and
[the Algorithms book, Chapter 22](../algorithms/22-NP-Completeness.md)). Given a formula with variables
$u_1, \dots, u_n$ and clauses $c_1, \dots, c_m$, make a root node $U_j$ for each variable with prior 0.5; a node
$C_k$ for each clause, whose parents are the clause's three variables, with a deterministic CPT that is 1 exactly
when the clause is satisfied; and a chain of AND nodes ending in $X$ that is 1 exactly when all the $C_k$ are 1. Each
CPT has at most 8 rows, so the network has size polynomial in the formula. Every assignment to the $U_j$ has
probability $2^{-n}$, and $X = 1$ exactly in the satisfying ones, so $P(X = 1)$ is the number of satisfying
assignments times $2^{-n}$, which is positive if and only if the formula is satisfiable. $\square$

The same construction shows more: computing $P(X = 1)$ exactly gives the number of satisfying assignments, so exact
inference is #P-hard, as hard as counting. And approximate inference is not easy either: Dagum and Luby (1993) showed
that approximating posteriors to within a fixed relative error is NP-hard in general. These are worst-case results.
Real networks are often sparse enough for exact methods, and the next section's sampling methods are the standard
tool when they are not.

### The program

```python
--8<-- "books/ai/ch12_bayesnet.py"
```

```
1. 6 binary variables: the full joint needs 63 numbers, the network 12
  the product of the CPTs sums to 1.000000 over all 64 assignments

2. Queries (enumeration = variable elimination)
  P(Storm=1 | nothing)               = 0.1000
  P(Fault=1 | nothing)               = 0.0500
  P(Fault=1 | Alert=1)               = 0.2355
  P(Fault=1 | Alert=1, Low=1)        = 0.1177
  P(Fault=1 | Alert=1, Low=0)        = 0.3085
  P(Storm=1 | Alert=1)               = 0.4034
  P(Storm=1 | Alert=1, Dark=1)       = 0.9044
  P(Slow=1 | Low=1)                  = 0.3343
  variable elimination for P(Fault | Alert=1), hidden variables in network order:
    eliminate Storm : multiply 4 factor(s) over ['Storm', 'Low', 'Dark', 'Fault', 'Slow'], sum out -> factor over ['Low', 'Dark', 'Fault', 'Slow']
    eliminate Low   : multiply 1 factor(s) over ['Low', 'Dark', 'Fault', 'Slow'], sum out -> factor over ['Dark', 'Fault', 'Slow']
    eliminate Dark  : multiply 1 factor(s) over ['Dark', 'Fault', 'Slow'], sum out -> factor over ['Fault', 'Slow']
    eliminate Slow  : multiply 2 factor(s) over ['Slow', 'Fault'], sum out -> factor over ['Fault']
  order ['Storm', 'Low', 'Dark', 'Slow']: largest factor has 5 variables
  order ['Low', 'Dark', 'Slow', 'Storm']: largest factor has 3 variables

3. d-separation checked against the numbers
  Storm ⊥ Fault | {}: graph says True, numbers say True
  Storm ⊥ Fault | {Slow}: graph says False, numbers say False
  Storm ⊥ Fault | {Alert}: graph says False, numbers say False
  Fault ⊥ Low | {Alert}: graph says False, numbers say False
  Fault ⊥ Low | {Storm, Alert}: graph says True, numbers say True
  Low ⊥ Dark | {}: graph says False, numbers say False
  Low ⊥ Dark | {Storm}: graph says True, numbers say True
  graph and numbers agree on 240 of 240 (pair, conditioning set) tests
```

The log of the elimination in network order shows the waste a bad order causes: eliminating $\mathit{Storm}$ first
multiplies four factors into one over five variables, from which $\mathit{Low}$ and $\mathit{Dark}$ are then summed
out to nothing. The better order keeps every factor at three variables or fewer.

## 12.5 Approximate inference: rejection sampling, likelihood weighting, Gibbs sampling, from scratch

*Level: intermediate to advanced.*

### The idea: estimate by counting

When exact inference is too expensive, we can simulate. Draw many possible worlds at random from the network's
distribution, and estimate a probability by the fraction of draws in which the event holds. This is the **Monte
Carlo** method (see the Algorithms book's
[Chapter 21](../algorithms/21-Randomized-and-Amortized-Analysis.md#211-las-vegas-monte-carlo-and-the-tools-of-expectation)
for Monte Carlo algorithms in general). The question for each method is: does the estimate converge to the true
posterior, and how many samples does it need?

All three methods below answer the same query, $P(\mathit{fault} \mid \mathit{alert}, \mathit{low})$: the ground
team sees an alert and the power report is low. Variable elimination says the answer is 0.1177 (low power points to
a storm, which explains the alert away from a fault).

### Prior sampling

**Prior sampling** (also called direct or forward sampling) draws one world from the network: visit the nodes in
topological order and give each a random value from its CPT row, using the values already chosen for its parents.
The probability of producing a particular world $x_1, \dots, x_n$ is the product of the CPT entries used, which is
exactly the chain rule: $S(x_1, \dots, x_n) = \prod_i P(x_i \mid \mathit{parents}(X_i)) = P(x_1, \dots, x_n)$. So
prior sampling draws worlds from the true joint, and by the law of large numbers, the fraction of $N$ samples in
which an event holds converges to its probability as $N$ grows.

### Rejection sampling

To estimate a posterior $P(X \mid \mathbf{e})$, the simplest method draws prior samples and **rejects** every sample
that disagrees with the evidence; among the kept samples it counts how often $X$ is true. (Henrion, 1988, called this
**logic sampling**.)

**Why it is consistent.** Let $N_{\mathbf{e}}$ be the number of kept samples and $N_{x, \mathbf{e}}$ the number in
which also $X = x$. The estimate is $N_{x, \mathbf{e}} / N_{\mathbf{e}}$. Dividing top and bottom by $N$, each
fraction converges to its probability, so the estimate converges to
$P(x, \mathbf{e}) / P(\mathbf{e}) = P(x \mid \mathbf{e})$.

**The problem.** The expected number of kept samples is $N P(\mathbf{e})$. Here
$P(\mathit{alert}, \mathit{low}) = 0.0534$, so about 95 samples in 100 are thrown away, and the run with $N = 100$
kept only 5. Evidence gets less likely, roughly exponentially, as more evidence variables are observed, so with a
dozen observations rejection sampling can keep almost nothing. Since only $N P(\mathbf{e})$ samples count, the
standard error of the estimate is about $\sqrt{p(1-p) / (N P(\mathbf{e}))}$, where $p$ is the true posterior.

### Likelihood weighting

**Likelihood weighting** (Fung and Chang, 1989; Shachter and Peot, 1989) never wastes a sample. It fixes each
evidence variable to its observed value instead of sampling it, samples the other variables in topological order as
before, and gives the sample a **weight**: the product, over the evidence variables, of the probability of the
observed value given the sampled parents.

$$
w(\mathbf{z}, \mathbf{e}) = \prod_{j:\, E_j \in \mathbf{E}} P(e_j \mid \mathit{parents}(E_j)).
$$

The estimate is the weighted fraction: the sum of the weights of the samples with $X = x$, divided by the sum of
all weights.

A worked sample for our query: the evidence is $\mathit{alert}$ and $\mathit{low}$. Visit $\mathit{Storm}$: sample
it, say $\mathit{storm}$. Visit $\mathit{Fault}$: sample, say $\lnot \mathit{fault}$. Visit $\mathit{Low}$: it is
evidence, so fix it to 1 and multiply the weight by $P(\mathit{low} \mid \mathit{storm}) = 0.8$. Visit
$\mathit{Dark}$: sample it. Visit $\mathit{Slow}$: sample with $P(\mathit{slow} \mid \mathit{storm},
\lnot\mathit{fault}) = 0.6$, say $\mathit{slow}$. Visit $\mathit{Alert}$: evidence, multiply by
$P(\mathit{alert} \mid \mathit{slow}) = 0.9$. The sample has weight $0.8 \times 0.9 = 0.72$ and counts towards
$\lnot\mathit{fault}$.

**Why it is consistent.** Write $\mathbf{z}$ for the values of the non-evidence variables. The probability that
likelihood weighting produces $\mathbf{z}$ is the product of the CPT entries of the non-evidence variables only,
$S_{\mathit{LW}}(\mathbf{z}, \mathbf{e}) = \prod_{i:\, Z_i \notin \mathbf{E}} P(z_i \mid \mathit{parents}(Z_i))$. The
weight supplies the missing factors, so

$$
S_{\mathit{LW}}(\mathbf{z}, \mathbf{e})\, w(\mathbf{z}, \mathbf{e}) = \prod_{\text{all } i} P(\cdot \mid \mathit{parents}) = P(\mathbf{z}, \mathbf{e}).
$$

The expected weight of a sample with $X = x$ is therefore
$\sum_{\mathbf{z}: X = x} S_{\mathit{LW}}\, w = P(x, \mathbf{e})$, and the expected total weight is
$P(\mathbf{e})$. By the law of large numbers the weighted fraction converges to
$P(x, \mathbf{e}) / P(\mathbf{e})$. This is an instance of **importance sampling**: sample from a convenient
distribution and correct by the ratio of the target to it.

**The problem.** The weights can be very uneven. Evidence only influences the sampling of its descendants, not its
ancestors: the storm is sampled from its prior, 0.1, even though the evidence makes it likely, and the few samples
with a storm then carry most of the weight. A useful measure is the **effective sample size**
$\mathit{ESS} = (\sum_k w_k)^2 / \sum_k w_k^2$, the number of equally weighted samples that would give the same
variance. With equal weights it is $N$; if one sample carries all the weight it is 1. For our query the program
reports an ESS of about 8.7 percent of $N$, better than rejection's 5.3 percent kept, but not by much. With evidence
at the leaves and unlikely causes, the ESS can collapse.

### Gibbs sampling

A different approach builds a random walk over worlds whose long-run distribution is the posterior. This is
**Markov chain Monte Carlo** (MCMC); the Probability book's
[Markov chains](https://math.akadian.ca/books/probability/13-Markov-Chains.html) chapter covers the theory of the
chains. **Gibbs sampling**, named by Geman and Geman (1984) in their work on image restoration, is the simplest MCMC
method:

1. Start from any world that agrees with the evidence.
2. Repeat: pick each non-evidence variable in turn and resample it from its distribution given the current values
   of all the other variables.
3. After a **burn-in** period, count how often $X = x$ in the visited worlds.

Resampling from "all the other variables" sounds expensive, but in a Bayesian network it is local. A variable is
independent of everything else given its **Markov blanket**: its parents, its children and its children's other
parents. The resampling distribution is

$$
P(x_i \mid \mathit{mb}(X_i)) = \alpha\, P(x_i \mid \mathit{parents}(X_i)) \prod_{Y_j \in \mathit{Children}(X_i)} P(y_j \mid \mathit{parents}(Y_j)),
$$

because in the full joint only these factors mention $x_i$, and all the others cancel in the normalisation. For
example, with $\lnot\mathit{storm}$ and $\mathit{slow}$, resampling $\mathit{Fault}$ uses
$P(\mathit{fault}) P(\mathit{slow} \mid \lnot\mathit{storm}, \mathit{fault}) = 0.05 \times 0.7 = 0.035$ against
$P(\lnot\mathit{fault}) P(\mathit{slow} \mid \lnot\mathit{storm}, \lnot\mathit{fault}) = 0.95 \times 0.05 = 0.0475$,
so $\mathit{Fault}$ becomes 1 with probability $0.035 / 0.0825 = 0.4242$.

**Why it converges.** Consider one step that resamples $X_i$, and let $\pi$ be the posterior
$P(\cdot \mid \mathbf{e})$. The step moves from world $\mathbf{x}$ to a world $\mathbf{x}'$ that differs at most in
$X_i$, with probability $q(\mathbf{x} \to \mathbf{x}') = \pi(x'_i \mid \mathbf{x}_{-i})$, where $\mathbf{x}_{-i}$ is
the shared value of the other variables. Then

$$
\pi(\mathbf{x})\, q(\mathbf{x} \to \mathbf{x}') = \pi(\mathbf{x}_{-i})\, \pi(x_i \mid \mathbf{x}_{-i})\, \pi(x'_i \mid \mathbf{x}_{-i}),
$$

which is symmetric in $\mathbf{x}$ and $\mathbf{x}'$. This symmetry, **detailed balance**, implies that $\pi$ is a
stationary distribution: summing $\pi(\mathbf{x}) q(\mathbf{x} \to \mathbf{x}')$ over $\mathbf{x}$ gives
$\pi(\mathbf{x}') \sum_{\mathbf{x}} q(\mathbf{x}' \to \mathbf{x}) = \pi(\mathbf{x}')$. A full sweep is a composition
of such steps, each of which keeps $\pi$, so the sweep keeps $\pi$ too. If the chain is also **irreducible** (it can
reach every world of positive probability) and **aperiodic**, the standard theorem on finite Markov chains says the
distribution of the state converges to $\pi$ from any start, and the fraction of time spent in each world converges
to its probability (the ergodic theorem). All CPT entries in our network are strictly between 0 and 1, so every
resampling step can reach every value and both conditions hold.

**The problems.** Consecutive samples are correlated, so $N$ Gibbs samples are worth fewer than $N$ independent ones,
and the chain needs a burn-in before its state reflects $\pi$. With near-deterministic CPTs the chain can get stuck:
if two variables must almost always agree, changing one at a time almost never happens, and the chain mixes slowly.
Deterministic CPTs (probabilities exactly 0 or 1) can make it reducible, and then it is simply wrong.

### The program

```python
--8<-- "books/ai/ch12_sampling.py"
```

```
exact P(Fault=1 | Alert=1, Low=1) = 0.1177   (variable elimination)

1-3. One run of each method
      N   rejection (kept)    likelihood weighting (ESS)   Gibbs
     100   0.2000 (    5)        0.0268 (      11)          0.0800
    1000   0.1250 (   48)        0.1255 (      85)          0.1120
   10000   0.1185 (  523)        0.1098 (     866)          0.1236
  100000   0.1164 ( 5311)        0.1165 (    8700)          0.1188
  (Gibbs runs N/4 sweeps over the 4 free variables: N single-variable draws in all)

4. Spread of 100 runs with N = 1000 (standard deviation of the estimate)
  rejection             mean 0.1161  sd 0.0402
  likelihood weighting  mean 0.1161  sd 0.0279
  Gibbs                 mean 0.1171  sd 0.0214

rare evidence Alert=1, Low=0, Dark=1: exact P(Storm=1 | e) = 0.6778
  rejection kept 99 of 10000 samples -> 0.7172;  likelihood weighting -> 0.6682 (ESS 1166)
```

<figure class="mars-fig" markdown="0">
<svg viewBox="0 0 640 290" role="img" aria-label="A plot of the three sampling estimates of P(fault given alert and low) against the number of samples N on a log scale from 100 to 100,000. A dashed line marks the exact value 0.1177. At N equals 100 the estimates are scattered: rejection 0.20, likelihood weighting 0.027, Gibbs 0.08. By N equals 100,000 all three are close to the line: 0.116, 0.117 and 0.119.">
<line x1="90" y1="240" x2="600" y2="240" stroke="currentColor"/>
<line x1="90" y1="240" x2="90" y2="30" stroke="currentColor"/>
<line x1="85" y1="240" x2="90" y2="240" stroke="currentColor"/>
<text x="80" y="244" font-size="11" text-anchor="end" fill="currentColor">0.00</text>
<line x1="85" y1="200" x2="90" y2="200" stroke="currentColor"/>
<text x="80" y="204.0" font-size="11" text-anchor="end" fill="currentColor">0.05</text>
<line x1="85" y1="160" x2="90" y2="160" stroke="currentColor"/>
<text x="80" y="164.0" font-size="11" text-anchor="end" fill="currentColor">0.10</text>
<line x1="85" y1="120" x2="90" y2="120" stroke="currentColor"/>
<text x="80" y="124.0" font-size="11" text-anchor="end" fill="currentColor">0.15</text>
<line x1="85" y1="80" x2="90" y2="80" stroke="currentColor"/>
<text x="80" y="84.0" font-size="11" text-anchor="end" fill="currentColor">0.20</text>
<line x1="85" y1="40" x2="90" y2="40" stroke="currentColor"/>
<text x="80" y="44.0" font-size="11" text-anchor="end" fill="currentColor">0.25</text>
<line x1="100" y1="240" x2="100" y2="245" stroke="currentColor"/>
<text x="100.0" y="259" font-size="11" text-anchor="middle" fill="currentColor">100</text>
<line x1="250" y1="240" x2="250" y2="245" stroke="currentColor"/>
<text x="250.0" y="259" font-size="11" text-anchor="middle" fill="currentColor">1 000</text>
<line x1="400" y1="240" x2="400" y2="245" stroke="currentColor"/>
<text x="400.0" y="259" font-size="11" text-anchor="middle" fill="currentColor">10 000</text>
<line x1="550" y1="240" x2="550" y2="245" stroke="currentColor"/>
<text x="550.0" y="259" font-size="11" text-anchor="middle" fill="currentColor">100 000</text>
<text x="345" y="278" font-size="12" text-anchor="middle" fill="currentColor">number of samples N (log scale)</text>
<line x1="90" y1="145.8" x2="600" y2="145.8" stroke="currentColor" stroke-dasharray="6 4"/>
<text x="596" y="139.84" font-size="11" text-anchor="end" fill="currentColor">exact 0.1177</text>
<polyline points="92.0,80.0 242.0,140.0 392.0,145.2 542.0,146.9" fill="none" stroke="#eea66f" stroke-width="2"/>
<circle cx="92.0" cy="80.0" r="4.5" fill="#eea66f" stroke="currentColor"/>
<circle cx="242.0" cy="140.0" r="4.5" fill="#eea66f" stroke="currentColor"/>
<circle cx="392.0" cy="145.2" r="4.5" fill="#eea66f" stroke="currentColor"/>
<circle cx="542.0" cy="146.9" r="4.5" fill="#eea66f" stroke="currentColor"/>
<polyline points="100.0,218.6 250.0,139.6 400.0,152.2 550.0,146.8" fill="none" stroke="#9cc9ea" stroke-width="2"/>
<circle cx="100.0" cy="218.6" r="4.5" fill="#9cc9ea" stroke="currentColor"/>
<circle cx="250.0" cy="139.6" r="4.5" fill="#9cc9ea" stroke="currentColor"/>
<circle cx="400.0" cy="152.2" r="4.5" fill="#9cc9ea" stroke="currentColor"/>
<circle cx="550.0" cy="146.8" r="4.5" fill="#9cc9ea" stroke="currentColor"/>
<polyline points="108.0,176.0 258.0,150.4 408.0,141.1 558.0,145.0" fill="none" stroke="#7ccf9a" stroke-width="2"/>
<circle cx="108.0" cy="176.0" r="4.5" fill="#7ccf9a" stroke="currentColor"/>
<circle cx="258.0" cy="150.4" r="4.5" fill="#7ccf9a" stroke="currentColor"/>
<circle cx="408.0" cy="141.1" r="4.5" fill="#7ccf9a" stroke="currentColor"/>
<circle cx="558.0" cy="145.0" r="4.5" fill="#7ccf9a" stroke="currentColor"/>
<circle cx="420" cy="40" r="4.5" fill="#eea66f" stroke="currentColor"/>
<text x="430" y="44" font-size="12" text-anchor="start" fill="currentColor">rejection</text>
<circle cx="420" cy="58" r="4.5" fill="#9cc9ea" stroke="currentColor"/>
<text x="430" y="62" font-size="12" text-anchor="start" fill="currentColor">likelihood weighting</text>
<circle cx="420" cy="76" r="4.5" fill="#7ccf9a" stroke="currentColor"/>
<text x="430" y="80" font-size="12" text-anchor="start" fill="currentColor">Gibbs</text>
</svg>
<figcaption>Figure 12.3. One run of each sampler, from the program's table: the estimates of
$P(\mathit{fault} \mid \mathit{alert}, \mathit{low})$ approach the exact value 0.1177 as $N$ grows. With 100 samples
any of them can be far off.</figcaption>
</figure>

Reading the output:

- **All three converge.** By $N = 100{,}000$ every estimate is within 0.002 of 0.1177.
- **The error shrinks like** $1/\sqrt{N}$. The spread over 100 runs with $N = 1000$ is 0.040 for rejection, 0.028
  for likelihood weighting and 0.021 for Gibbs. For rejection the formula above predicts
  $\sqrt{0.1177 \times 0.8823 / (1000 \times 0.0534)} = 0.044$, close to what we see. Ten times the accuracy costs
  a hundred times the samples, which is the basic limitation of Monte Carlo.
- **The order is typical, not a law.** On this network Gibbs gives the smallest spread per draw. On another, with
  strongly coupled variables, it can be the worst.
- **Rare evidence.** With $\mathit{alert}$, no low power and dark images, $P(\mathbf{e}) = 0.0116$: rejection kept
  99 samples out of 10,000 and is off by 0.04, while likelihood weighting, with an effective sample size of 1166, is
  within 0.01.

**In practice.** Probabilistic programming systems such as Stan and PyMC run these ideas at scale, with more
powerful MCMC methods (Hamiltonian Monte Carlo) for continuous variables. Libraries such as pgmpy implement the
discrete network algorithms of this chapter.

## 12.6 Causal networks and do-calculus idea (Pearl), interventions vs observations

*Level: advanced.*

### Seeing is not doing

A team planning rover drives keeps a log. On each drive the planners chose between autonomous navigation (the
rover picks its own path from its stereo images) and a fully planned path. In the logs, the drives with the
autonomous mode succeeded **less** often than the others. Should the team stop using it?

Not necessarily. Here is an invented example, with the program below. Planners choose the autonomous mode more often
on rough terrain, and rough terrain makes any drive less likely to succeed. The variables are $\mathit{Rough}$,
$\mathit{Auto}$ and $\mathit{Success}$, with $\mathit{Rough} \to \mathit{Auto}$, $\mathit{Rough} \to
\mathit{Success}$ and $\mathit{Auto} \to \mathit{Success}$. The numbers: half the drives are rough; the autonomous
mode is chosen on 80 percent of rough drives and 20 percent of smooth ones; success rates are 0.60 (rough, auto),
0.40 (rough, planned), 0.95 (smooth, auto) and 0.90 (smooth, planned). Within each kind of terrain the autonomous
mode does better. Yet in the logs, $P(\mathit{success} \mid \mathit{auto}) = 0.67$ and
$P(\mathit{success} \mid \lnot\mathit{auto}) = 0.80$, because most autonomous drives were on rough ground. A trend
that holds in every group and reverses in the total is **Simpson's paradox** (Simpson, 1951, described it; Yule had
noted the effect in 1903). $\mathit{Rough}$ is a **confounder**: a common cause of the choice and the outcome.

The question the team cares about is not "how often did autonomous drives succeed?" but "what would happen if we
used the autonomous mode on every drive?". That is a question about an **intervention**, and conditional probability
does not answer it.

### Interventions and the do-operator

Pearl's answer (Pearl 1995; the book *Causality*, 2000, 2nd ed. 2009) is to treat a Bayesian network whose arrows are
causal as a model of mechanisms. Each CPT $P(x_i \mid \mathit{parents}(X_i))$ describes an independent mechanism by
which $X_i$ is set from its causes. An **intervention** $\mathit{do}(X = x)$ replaces the mechanism of $X$ by the
constant $x$ and leaves every other mechanism alone. In the graph it deletes all arrows into $X$ (the **mutilated**
network), and in the joint it deletes $X$'s factor, the **truncated factorisation**:

$$
P(\mathbf{v} \mid \mathit{do}(X = x)) = \prod_{i:\, V_i \neq X} P(v_i \mid \mathit{parents}(V_i)) \quad \text{for } \mathbf{v} \text{ consistent with } X = x,
$$

and 0 for the other worlds. Figure 12.4 shows the two networks for the drive log.

<figure class="mars-fig" markdown="0">
<svg viewBox="0 0 640 240" role="img" aria-label="Two causal networks side by side. Left, observing the logged drives: Rough points to Auto and to Success, and Auto points to Success. Right, doing: the mode is set, Auto := 1 for every drive, so the arrow from Rough to Auto is removed; Rough still points to Success and Auto still points to Success.">
<line x1="138.4" y1="67.4" x2="86.6" y2="145.1" stroke="currentColor" stroke-width="1.5"/>
<polygon points="81.6,152.6 83.4,141.8 90.9,146.8" fill="currentColor"/>
<line x1="161.6" y1="67.4" x2="213.4" y2="145.1" stroke="currentColor" stroke-width="1.5"/>
<polygon points="218.4,152.6 209.1,146.8 216.6,141.8" fill="currentColor"/>
<line x1="114.0" y1="170.0" x2="177.0" y2="170.0" stroke="currentColor" stroke-width="1.5"/>
<polygon points="186.0,170.0 176.0,174.5 176.0,165.5" fill="currentColor"/>
<ellipse cx="150" cy="50" rx="44" ry="18" fill="#eea66f" fill-opacity="0.5" stroke="currentColor"/>
<text x="150" y="55" font-size="13" text-anchor="middle" fill="currentColor">Rough</text>
<ellipse cx="70" cy="170" rx="44" ry="18" fill="#9cc9ea" fill-opacity="0.5" stroke="currentColor"/>
<text x="70" y="175" font-size="13" text-anchor="middle" fill="currentColor">Auto</text>
<ellipse cx="230" cy="170" rx="44" ry="18" fill="#9cc9ea" fill-opacity="0.5" stroke="currentColor"/>
<text x="230" y="175" font-size="13" text-anchor="middle" fill="currentColor">Success</text>
<text x="150" y="225" font-size="12" text-anchor="middle" fill="currentColor">observing: the logged drives</text>
<line x1="491.6" y1="67.4" x2="543.4" y2="145.1" stroke="currentColor" stroke-width="1.5"/>
<polygon points="548.4,152.6 539.1,146.8 546.6,141.8" fill="currentColor"/>
<line x1="444.0" y1="170.0" x2="507.0" y2="170.0" stroke="currentColor" stroke-width="1.5"/>
<polygon points="516.0,170.0 506.0,174.5 506.0,165.5" fill="currentColor"/>
<ellipse cx="480" cy="50" rx="44" ry="18" fill="#eea66f" fill-opacity="0.5" stroke="currentColor"/>
<text x="480" y="55" font-size="13" text-anchor="middle" fill="currentColor">Rough</text>
<rect x="354" y="152" width="92" height="36" rx="6" fill="#7ccf9a" fill-opacity="0.6" stroke="currentColor"/>
<text x="400" y="175" font-size="13" text-anchor="middle" fill="currentColor">Auto := 1</text>
<ellipse cx="560" cy="170" rx="44" ry="18" fill="#9cc9ea" fill-opacity="0.5" stroke="currentColor"/>
<text x="560" y="175" font-size="13" text-anchor="middle" fill="currentColor">Success</text>
<text x="480" y="225" font-size="12" text-anchor="middle" fill="currentColor">doing: set Auto = 1 for every drive</text>
<line x1="320" y1="15" x2="320" y2="235" stroke="currentColor" stroke-opacity="0.3"/>
</svg>
<figcaption>Figure 12.4. Observing versus intervening. Setting the mode by decision cuts the arrow from the
terrain to the mode; the terrain still affects success directly.</figcaption>
</figure>

Conditioning and intervening differ exactly in the factor for $\mathit{Rough}$. Conditioning on $\mathit{auto}$ uses
Bayes' rule to update the terrain: an autonomous drive is evidence of rough terrain,
$P(\mathit{rough} \mid \mathit{auto}) = 0.4 / 0.5 = 0.8$. Intervening does not: forcing the mode says nothing about
the terrain, which keeps its prior 0.5. So

$$
\begin{aligned}
P(\mathit{success} \mid \mathit{auto}) &= 0.8 \times 0.60 + 0.2 \times 0.95 = 0.67,\\
P(\mathit{success} \mid \mathit{do}(\mathit{auto})) &= 0.5 \times 0.60 + 0.5 \times 0.95 = 0.775,
\end{aligned}
$$

and $P(\mathit{success} \mid \mathit{do}(\lnot\mathit{auto})) = 0.5 \times 0.40 + 0.5 \times 0.90 = 0.65$. The
observed difference is $-0.13$; the causal effect is $+0.125$. The opposite sign is the whole lesson.

### The back-door adjustment

The calculation above needed the network. Can a causal effect be computed from observational data alone? Sometimes.
A set of variables $\mathbf{Z}$ satisfies the **back-door criterion** for the effect of $X$ on $Y$ if no node of
$\mathbf{Z}$ is a descendant of $X$, and $\mathbf{Z}$ blocks (in the d-separation sense of 12.3) every path between
$X$ and $Y$ that starts with an arrow into $X$. Such paths are the "back doors" through which confounding flows.

**Theorem** (back-door adjustment, Pearl 1993 and 1995). If $\mathbf{Z}$ satisfies the back-door criterion relative
to $X$ and $Y$, then

$$
P(y \mid \mathit{do}(x)) = \sum_{\mathbf{z}} P(y \mid x, \mathbf{z})\, P(\mathbf{z}).
$$

*Proof sketch, for the case where $\mathbf{Z}$ is the set of parents of $X$* (the general case is in Pearl 2009,
section 3.3). In the truncated factorisation, sum over all variables except $Y$ and the parents $\mathbf{Z}$. The
factors for the non-descendants of $X$ give the marginal $P(\mathbf{z})$ (deleting $X$'s factor does not change the
distribution of its non-descendants, because summing out $X$'s factor gives 1). The factors for the descendants of
$X$, with $X$ fixed to $x$, give the conditional distribution of $Y$ given $x$ and $\mathbf{z}$ in the original
network, because given its parents, $X$ is independent of its non-descendants (the local Markov property of 12.3),
so conditioning on $X = x$ and $\mathbf{Z} = \mathbf{z}$ in the original network produces the same factors. $\square$

In the drive log, $\{\mathit{Rough}\}$ satisfies the criterion: the only back-door path is
$\mathit{Auto} \leftarrow \mathit{Rough} \to \mathit{Success}$, and conditioning on $\mathit{Rough}$ blocks it. The
adjustment gives $0.60 \times 0.5 + 0.95 \times 0.5 = 0.775$, the interventional answer, from quantities that can be
estimated from the logs. The program checks this on 200,000 simulated logged drives: the naive difference in success
rates is $-0.1289$, the back-door adjusted difference is $+0.1275$, and a simulated randomized experiment, where a
coin decides the mode, gives $+0.1247$. All three estimate their targets: the first a correlation, the last two the
causal effect of $+0.125$.

That last line is why randomized controlled trials work, and it is a theorem in this language: when a coin chooses
$X$, $X$ has no parents, there are no back-door paths, and $P(y \mid \mathit{do}(x)) = P(y \mid x)$. Fisher argued for
randomization in exactly these terms in *The Design of Experiments* (1935), without the graphs.

### The do-calculus

The back-door criterion is one case of a general method. Pearl's **do-calculus** (1995) has three rules that rewrite
expressions with $\mathit{do}$, each allowed when a d-separation condition holds in a suitably mutilated graph:

1. **Insertion or deletion of observations:** $P(y \mid \mathit{do}(x), z, w) = P(y \mid \mathit{do}(x), w)$ if $Y$
   and $Z$ are d-separated by $X \cup W$ in the graph with arrows into $X$ removed.
2. **Action/observation exchange:** $P(y \mid \mathit{do}(x), \mathit{do}(z), w) = P(y \mid \mathit{do}(x), z, w)$ if
   $Y$ and $Z$ are d-separated by $X \cup W$ in the graph with arrows into $X$ and arrows out of $Z$ removed.
3. **Insertion or deletion of actions:** $P(y \mid \mathit{do}(x), \mathit{do}(z), w) = P(y \mid \mathit{do}(x), w)$
   if a d-separation holds in the graph with arrows into $X$ and into certain nodes of $Z$ removed (the exact set is
   in Pearl 2009, section 3.4).

A causal effect is **identifiable** if these rules can turn $P(y \mid \mathit{do}(x))$ into an expression with no
$\mathit{do}$, computable from the observational distribution. Shpitser and Pearl (2006) and Huang and Valtorta
(2006) proved that the three rules are complete: whenever an effect is identifiable at all, the rules find it, and
there is a polynomial algorithm that decides it. Not every effect is identifiable. If the confounder had not been
recorded in the logs, no amount of observational data would separate the effect of the mode from the effect of the
terrain, and only an experiment, or a different variable such as one satisfying the **front-door criterion**, would
settle it.

### What this needs, honestly

All of this assumes the causal graph is right: that we know which arrows exist and that no unrecorded common cause is
missing. Data alone can rule out some graphs (those whose d-separations the data contradict), and methods for
learning causal structure from data exist (Spirtes, Glymour and Scheines, *Causation, Prediction, and Search*, 2nd
ed. 2000), but in general several graphs fit the same data equally well, and choosing among them needs knowledge or
experiments. The do-operator does not create causal knowledge; it tells us exactly what follows from the knowledge we
put in, and what we would still need to find out.

```python
--8<-- "books/ai/ch12_causal.py"
```

```
1. Seeing versus doing
  Auto=1:  P(Success | Auto=1) = 0.6700    P(Success | do(Auto=1)) = 0.7750
  Auto=0:  P(Success | Auto=0) = 0.8000    P(Success | do(Auto=0)) = 0.6500
  observed difference -0.1300;  causal effect +0.1250
  within Rough=1: success 0.60 with Auto, 0.40 without
  within Rough=0: success 0.95 with Auto, 0.90 without

2. Back-door adjustment over Rough
  sum_r P(Success | Auto=1, r) P(r) = 0.7750
  sum_r P(Success | Auto=0, r) P(r) = 0.6500

3. From data
  logged drives: naive difference -0.1289, back-door adjusted +0.1275
  randomized experiment (mode chosen by coin flip): difference +0.1247
```

## Check yourself

??? question "1. From the full joint table of the first program, compute $P(\mathit{dark})$ and $P(\mathit{storm} \mid \mathit{dark})$ by hand."

    Add the four rows with $\mathit{Dark} = 1$: $0.0560 + 0.0140 + 0.0045 + 0.0405 = 0.1150$. The rows with both
    $\mathit{Storm} = 1$ and $\mathit{Dark} = 1$ give $0.0560 + 0.0140 = 0.0700$. So
    $P(\mathit{storm} \mid \mathit{dark}) = 0.0700 / 0.1150 = 0.6087$. Check from the factored form:
    $P(\mathit{dark}) = 0.1 \times 0.7 + 0.9 \times 0.05 = 0.115$, and Bayes' rule gives $0.07 / 0.115$.

??? question "2. A screening test has sensitivity 0.99 and specificity 0.99, for a condition with prevalence 1 in 1000. What is the probability of the condition after one positive result? Answer with natural frequencies too."

    $P(+) = 0.99 \times 0.001 + 0.01 \times 0.999 = 0.00099 + 0.00999 = 0.01098$, so
    $P(c \mid +) = 0.00099 / 0.01098 = 0.0902$, about 9 percent. In frequencies: of 100,000 people, 100 have the
    condition and 99 test positive; of the 99,900 without it, 999 test positive. So $99 / (99 + 999) = 0.0902$. A
    "99 percent accurate" test still gives mostly false positives when the condition is this rare.

??? question "3. Why is the joint distribution defined by a Bayesian network guaranteed to sum to 1, whatever numbers are in the CPTs?"

    Order the variables topologically and sum out the last one, $X_n$. Only its own CPT mentions $x_n$, because it is
    nobody's parent, and each row of that CPT sums to 1 over $x_n$. So the sum over $x_n$ leaves the product for the
    network without $X_n$, which is again a Bayesian network. By induction we reach the empty product, 1. The only
    requirement is that each CPT row is a distribution.

??? question "4. In the rover network, decide by d-separation: (a) Dark ⊥ Fault given nothing; (b) Dark ⊥ Fault given Alert; (c) Dark ⊥ Alert given Slow; (d) Low ⊥ Alert given nothing; (e) Low ⊥ Alert given Storm."

    (a) Independent: the only path is $\mathit{Dark} \leftarrow \mathit{Storm} \to \mathit{Slow} \leftarrow
    \mathit{Fault}$, with the collider $\mathit{Slow}$ unobserved and no observed descendant. (b) Dependent: now the
    collider's descendant $\mathit{Alert}$ is observed, and the fork $\mathit{Storm}$ is not, so the path is active.
    (c) Independent: the only path is $\mathit{Dark} \leftarrow \mathit{Storm} \to \mathit{Slow} \to \mathit{Alert}$,
    and the chain node $\mathit{Slow}$ is observed. (d) Dependent: $\mathit{Low} \leftarrow \mathit{Storm} \to
    \mathit{Slow} \to \mathit{Alert}$ has no observed node and no collider. (e) Independent: the fork $\mathit{Storm}$
    is observed. The program's `d_separated` gives True, False, True, False, True, and `numerically_independent`
    agrees on each.

??? question "5. Explaining away: compute $P(\mathit{storm} \mid \mathit{slow})$, then the same with $\mathit{fault}$ added, and with $\lnot\mathit{fault}$ added. Explain the pattern."

    $P(\mathit{storm}, \mathit{slow}) = 0.1 \times (0.05 \times 0.95 + 0.95 \times 0.6) = 0.06175$ and
    $P(\mathit{slow}) = 0.136$ (from 12.4's table: $0.06175 + 0.9 \times 0.0825$), so
    $P(\mathit{storm} \mid \mathit{slow}) = 0.4540$. With a known fault:
    $P(\mathit{storm} \mid \mathit{slow}, \mathit{fault}) = 0.1 \times 0.95 / (0.1 \times 0.95 + 0.9 \times 0.7)
    = 0.095 / 0.725 = 0.1310$. With no fault: $0.1 \times 0.6 / (0.06 + 0.9 \times 0.05) = 0.06 / 0.105 = 0.5714$.
    The fault already explains the short drive, so it lowers the need for a storm; ruling the fault out raises it.
    The two causes are independent a priori but dependent given their common effect.

??? question "6. Eliminate the hidden variables of $P(\mathit{Fault} \mid \mathit{alert})$ in the order Low, Dark, Slow, Storm. List each factor created and its variables. What is the largest?"

    Factors after restricting to $\mathit{alert}$: $f_S(\mathit{Storm})$, $f_F(\mathit{Fault})$,
    $f_L(\mathit{Storm}, \mathit{Low})$, $f_D(\mathit{Storm}, \mathit{Dark})$,
    $f_{\mathit{Sl}}(\mathit{Storm}, \mathit{Fault}, \mathit{Slow})$, $f_A(\mathit{Slow})$. Eliminating
    $\mathit{Low}$ sums $f_L$ to the all-ones factor $g_1(\mathit{Storm})$; eliminating $\mathit{Dark}$ gives another
    all-ones $g_2(\mathit{Storm})$. Eliminating $\mathit{Slow}$ multiplies $f_{\mathit{Sl}}$ and $f_A$ (three
    variables) and gives $g_3(\mathit{Storm}, \mathit{Fault})$. Eliminating $\mathit{Storm}$ multiplies $f_S$, $g_1$,
    $g_2$ and $g_3$ (two variables) and gives $g_4(\mathit{Fault})$. The largest product has 3 variables, matching
    the program's second order. The final $f_F \times g_4$ normalised is $\langle 0.7645, 0.2355 \rangle$.

??? question "7. Gibbs sampling: in the current state $\lnot\mathit{storm}$, $\mathit{slow}$, with $\mathit{Fault}$ being resampled, what is the probability that Fault becomes 1? Which CPT entries are needed and which are not?"

    The Markov blanket of $\mathit{Fault}$ is its child $\mathit{Slow}$ and the child's other parent
    $\mathit{Storm}$. Only $P(\mathit{Fault})$ and $P(\mathit{slow} \mid \lnot\mathit{storm}, \mathit{Fault})$
    matter: $0.05 \times 0.7 = 0.035$ against $0.95 \times 0.05 = 0.0475$, so the probability is
    $0.035 / 0.0825 = 0.4242$. The values of $\mathit{Low}$, $\mathit{Dark}$ and $\mathit{Alert}$ do not enter.

??? question "8. Likelihood weighting for evidence alert and low produces the sample storm, ¬fault, ¬dark, slow. What is its weight? Why is the weight not 1 even though no sample was rejected?"

    The evidence variables are $\mathit{Low}$ and $\mathit{Alert}$, so the weight is
    $P(\mathit{low} \mid \mathit{storm}) \times P(\mathit{alert} \mid \mathit{slow}) = 0.8 \times 0.9 = 0.72$. The
    non-evidence variables were drawn from their CPTs, so the sample came from a distribution that ignores the
    evidence; the weight is the correction that makes the expected weighted count equal to $P(x, \mathbf{e})$
    (12.5). A sample with $\lnot\mathit{storm}$ and $\lnot\mathit{slow}$ would get $0.1 \times 0.02 = 0.002$.

??? question "9. Write the code: estimate $P(\mathit{success} \mid \mathit{do}(\mathit{auto}))$ by sampling the mutilated network of 12.6, with 100,000 samples and seed 0."

    In the mutilated network $\mathit{Rough}$ keeps its prior and $\mathit{Auto}$ is fixed to 1, so only
    $\mathit{Rough}$ and $\mathit{Success}$ are sampled:

    ```python
    import numpy as np
    rng = np.random.default_rng(0)
    n = 100_000
    r = rng.random(n) < 0.5                       # Rough keeps its own mechanism
    p_s = np.where(r, 0.60, 0.95)                 # Auto is set to 1: use P(Success | Auto=1, r)
    s = rng.random(n) < p_s
    print(f"P(Success | do(Auto=1)) is about {s.mean():.4f}")
    ```

    It prints about 0.7760, close to the exact 0.775. Sampling the original network and keeping the drives with
    $\mathit{Auto} = 1$ would instead estimate 0.67.

??? question "10. In the drive log, would adjusting for Success (conditioning on it) be a valid back-door adjustment? What about a variable Report that records, after the drive, whether the team wrote a report, if Report is a child of Success?"

    No to both. The back-door criterion forbids descendants of $X$: $\mathit{Success}$ is the outcome itself, and
    $\mathit{Report}$ is a descendant of $\mathit{Auto}$ through $\mathit{Success}$. Adjusting for a variable that
    the treatment itself changes mixes the effect we want to measure into the groups we average over, and
    $\mathit{Success}$ is also a collider ($\mathit{Auto} \to \mathit{Success} \leftarrow \mathit{Rough}$), so
    conditioning on it or on its child creates extra dependence, as in explaining away (12.3). The valid set here is
    $\{\mathit{Rough}\}$.

??? question "11. (Advanced) Show that exact inference in Bayesian networks is NP-hard even when every node has at most three parents, and say why the result does not contradict the linear-time algorithm for polytrees."

    Cooper's reduction (12.4) uses root nodes $U_j$ with prior 0.5, clause nodes with exactly three parents and
    deterministic CPTs, and AND nodes. Build the AND as a chain $A_1 = C_1$, $A_k = A_{k-1} \land C_k$, so each AND
    node has two parents. Every node then has at most three parents, and $P(A_m = 1) > 0$ exactly when the formula is
    satisfiable. No contradiction with polytrees: a variable that occurs in two clauses gives two paths from $U_j$ to
    the final AND node, so the network is not a polytree, and its treewidth can grow with the formula. Bounded
    in-degree does not bound treewidth.

??? question "12. (Advanced) Prove that the likelihood-weighting estimate converges to $P(x \mid \mathbf{e})$, and explain why it can still need very many samples."

    The probability of drawing non-evidence values $\mathbf{z}$ is
    $S(\mathbf{z}) = \prod_{Z_i \notin \mathbf{E}} P(z_i \mid \mathit{parents}(Z_i))$, and the weight is
    $w(\mathbf{z}) = \prod_{E_j} P(e_j \mid \mathit{parents}(E_j))$, so $S(\mathbf{z}) w(\mathbf{z}) =
    P(\mathbf{z}, \mathbf{e})$ by the chain rule. Hence $E[w \cdot [X = x]] = \sum_{\mathbf{z}: X=x}
    P(\mathbf{z}, \mathbf{e}) = P(x, \mathbf{e})$ and $E[w] = P(\mathbf{e})$. The weighted fraction is the ratio of
    two sample means, each converging (law of large numbers, the weights being bounded by 1) to these expectations,
    so the ratio converges to $P(x, \mathbf{e}) / P(\mathbf{e})$. It may need very many samples because the variance
    depends on the spread of the weights: when the evidence is unlikely under the prior of its ancestors, a few
    samples carry almost all the weight, and the effective sample size $(\sum w)^2 / \sum w^2$ is much smaller than
    $N$.

## What you learned

- Logic cannot weigh competing explanations; degrees of belief can, and the Dutch book argument and Cox's theorem
  explain why they should follow the axioms of probability.
- A full joint distribution answers every query by marginalising, conditioning and normalising, but it is exponential
  in size; conditional independence is the structure that makes probabilistic reasoning feasible.
- Bayes' rule turns causal knowledge into diagnosis; priors matter (base-rate neglect), and independent pieces of
  evidence multiply likelihood ratios.
- A Bayesian network stores a joint distribution as a DAG with one conditional table per node; its independences are
  read from the graph by d-separation, which a linear-time search decides and which the program confirmed on 240
  tests.
- Variable elimination computes exact posteriors by the distributive law; its cost is exponential only in the
  treewidth, the order matters, and exact inference in general is NP-hard (Cooper 1990).
- Rejection sampling, likelihood weighting and Gibbs sampling all converge to the right answer, with errors shrinking
  like $1/\sqrt{N}$; rejection wastes samples, likelihood weighting can have uneven weights, Gibbs can mix slowly.
- Observing is not intervening: the do-operator cuts the arrows into the variable we set, the back-door adjustment
  computes causal effects from observational data when the confounders are measured, and Simpson's paradox shows what
  happens when they are ignored.

**Next:** [Chapter 13](13-Reasoning-over-Time.md) lets the world change: Markov models, filtering, hidden Markov
models, Kalman filters and particle filters for tracking a robot over time.

## Further reading

- S. Russell and P. Norvig, *Artificial Intelligence: A Modern Approach*, 4th ed., 2020: chapters 12 and 13
  (uncertainty, Bayesian networks).
- J. Pearl, *Probabilistic Reasoning in Intelligent Systems: Networks of Plausible Inference*, 1988.
- D. Koller and N. Friedman, *Probabilistic Graphical Models: Principles and Techniques*, 2009.
- K. P. Murphy, *Probabilistic Machine Learning: An Introduction*, 2022, and *Advanced Topics*, 2023; C. M. Bishop,
  *Pattern Recognition and Machine Learning*, 2006, chapter 8 (graphical models).
- B. de Finetti, "La prévision: ses lois logiques, ses sources subjectives", 1937; R. T. Cox, "Probability, frequency
  and reasonable expectation", *American Journal of Physics* 14, 1946; J. Y. Halpern, "A counterexample to theorems
  of Cox and Fine", *Journal of Artificial Intelligence Research* 10, 1999.
- G. Gigerenzer and U. Hoffrage, "How to improve Bayesian reasoning without instruction: frequency formats",
  *Psychological Review* 102, 1995.
- T. Verma and J. Pearl, "Causal networks: semantics and expressiveness", UAI 1988; D. Geiger, T. Verma and J. Pearl,
  "Identifying independence in Bayesian networks", *Networks* 20, 1990; R. D. Shachter, "Bayes-Ball: the rational
  pastime", UAI 1998; C. Meek, "Strong completeness and faithfulness in Bayesian networks", UAI 1995.
- N. L. Zhang and D. Poole, "A simple approach to Bayesian network computations", 1994; R. Dechter, "Bucket
  elimination: a unifying framework for probabilistic inference", UAI 1996; S. L. Lauritzen and D. J. Spiegelhalter,
  "Local computations with probabilities on graphical structures and their application to expert systems", *Journal
  of the Royal Statistical Society B* 50, 1988.
- G. F. Cooper, "The computational complexity of probabilistic inference using Bayesian belief networks",
  *Artificial Intelligence* 42, 1990; P. Dagum and M. Luby, "Approximating probabilistic inference in Bayesian belief
  networks is NP-hard", *Artificial Intelligence* 60, 1993.
- M. Henrion, "Propagating uncertainty in Bayesian networks by probabilistic logic sampling", 1988; R. Fung and K.-C.
  Chang, "Weighing and integrating evidence for stochastic simulation in Bayesian networks", 1989; R. D. Shachter and
  M. A. Peot, "Simulation approaches to general probabilistic inference on belief networks", 1989; S. Geman and D.
  Geman, "Stochastic relaxation, Gibbs distributions, and the Bayesian restoration of images", *IEEE Transactions on
  Pattern Analysis and Machine Intelligence* 6, 1984.
- J. Pearl, "Causal diagrams for empirical research", *Biometrika* 82, 1995; J. Pearl, *Causality: Models, Reasoning,
  and Inference*, 2nd ed., 2009; J. Pearl, M. Glymour and N. P. Jewell, *Causal Inference in Statistics: A Primer*,
  2016; I. Shpitser and J. Pearl, "Identification of joint interventional distributions in recursive semi-Markovian
  causal models", AAAI 2006; P. Spirtes, C. Glymour and R. Scheines, *Causation, Prediction, and Search*, 2nd ed.,
  2000; E. H. Simpson, "The interpretation of interaction in contingency tables", *Journal of the Royal Statistical
  Society B* 13, 1951; R. A. Fisher, *The Design of Experiments*, 1935.
- On this site: [Chapter 8](08-Propositional-Logic-and-SAT.md) (SAT, for Cooper's reduction),
  [Chapter 11](11-Knowledge-Representation.md) (default reasoning, the logical alternative), the Algorithms book's
  [Chapter 15](../algorithms/15-Graphs-and-Graph-Search.md) (graph search, topological order),
  [Chapter 13](../algorithms/13-Dynamic-Programming.md) (dynamic programming) and
  [Chapter 21](../algorithms/21-Randomized-and-Amortized-Analysis.md) (Monte Carlo); the reference pages on
  [topological sort](../../graphs/topological-sort.md) and [breadth-first search](../../graphs/bfs.md); the
  Machine learning book's [Chapter 12](../machine-learning/12-Probabilistic-Models.md) (learning the numbers from
  data); and the [Probability book](https://math.akadian.ca/books/probability/) at math.akadian.ca.
