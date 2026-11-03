# 13. Reasoning over time

*The Bayesian networks of [Chapter 12](12-Probabilistic-Reasoning.md) describe one moment. A robot driving down a
corridor, a doctor watching a patient, a speech recogniser listening to a sentence and a spacecraft coasting towards
Mars all face a world that changes while they watch it, through sensors that are noisy and incomplete. This chapter
answers the question: how does an agent keep an up-to-date belief about a hidden, changing state, cheaply, one
observation at a time? You will build the four basic inference tasks (filtering, prediction, smoothing and the most
likely sequence) for hidden Markov models from scratch, derive the Kalman filter in one dimension and use its matrix
form to track a moving object, localise a robot with a particle filter, and see how dynamic Bayesian networks put all
of these into one framework.*

!!! abstract "In this chapter"
    **You will learn:**

    - how to model a changing world as a sequence of states with a transition model and a sensor model, and what the
      Markov assumption buys
    - the four inference tasks over time and the recursions that solve them in time linear in the length of the
      sequence
    - the forward algorithm, the forward-backward algorithm and the Viterbi algorithm, built and checked by brute force
    - the Kalman filter, derived in one dimension from the product of two Gaussians, then used to track position and
      velocity
    - particle filters and Monte Carlo localization: why weighting and resampling approximate the exact filter
    - dynamic Bayesian networks, and why a factored state is exponentially cheaper to write down but not always to
      reason with

    **You need:** [Chapter 12](12-Probabilistic-Reasoning.md) (Bayes' rule, Bayesian networks, sampling) and
    [Chapter 2](02-Intelligent-Agents.md) (agents with an internal state). Some matrix arithmetic for 13.4
    ([Linear algebra](https://math.akadian.ca/books/linear-algebra/)) and Gaussian distributions
    ([Probability](https://math.akadian.ca/books/probability/)). The Viterbi algorithm is dynamic programming, as in
    the Algorithms book's [Chapter 13](../algorithms/13-Dynamic-Programming.md).

    **Levels:** 13.1 and 13.2 are beginner; 13.3 is intermediate; 13.4 is intermediate (the matrix filter is
    advanced); 13.5 is intermediate; 13.6 is advanced.

## 13.1 States that change; Markov assumption

Here is a small puzzle that runs through the first half of this chapter. A security guard works in an underground
building with no windows. Each morning the director walks in, and the guard notices whether she carries an umbrella.
The guard cannot see the sky, but would like to know: is it raining today? Was it raining yesterday? Will it rain
tomorrow?

Three things make this harder than a single-moment Bayesian network.

1. **The hidden state changes.** Today's weather is not yesterday's, but they are related: rain tends to last.
2. **The evidence is noisy.** The director sometimes carries an umbrella on a dry day and sometimes forgets it on a wet
   one.
3. **The evidence keeps coming.** Every day adds one more observation. The guard wants an answer now, and another
   answer tomorrow, without redoing all the work from the start.

### States and evidence in discrete time

We cut time into **time slices** $t = 0, 1, 2, \dots$ (days, seconds, video frames). In each slice the world has a
**state** $X_t$ that we cannot see directly (rain or not), and the agent receives **evidence** $E_t$ (umbrella or not).
We write $X_{a:b}$ for the sequence $X_a, X_{a+1}, \dots, X_b$, and likewise $e_{1:t}$ for the observed values
$e_1, \dots, e_t$. Evidence starts at $t = 1$; $X_0$ is the state before anything was observed.

Two models describe the world.

- The **transition model** says how the state evolves: $P(X_t \mid X_{0:t-1})$.
- The **sensor model** (or observation model) says how evidence depends on the state: $P(E_t \mid X_{0:t}, E_{1:t-1})$.

As written, both condition on the whole past, and the number of numbers needed grows without limit. We need
assumptions.

### The Markov assumption

The **Markov assumption** says that the current state depends on only a bounded number of previous states. In its
simplest form, the **first-order Markov assumption**,

$$
P(X_t \mid X_{0:t-1}) = P(X_t \mid X_{t-1}).
$$

In words: if you know yesterday's state exactly, then the days before yesterday tell you nothing more about today.
A process with this property is a **Markov process** or **Markov chain**, named after Andrey Markov, who in 1913 used
such a chain to analyse the sequence of vowels and consonants in Pushkin's *Eugene Onegin*.

We add two more assumptions.

- **Stationarity.** The transition model is the same at every step: $P(X_t \mid X_{t-1})$ does not depend on $t$.
  The laws of the world do not change, even though the state does. One table describes all of time.
- **The sensor Markov assumption.** The evidence depends only on the current state:
  $P(E_t \mid X_{0:t}, E_{1:t-1}) = P(E_t \mid X_t)$. The umbrella depends on today's weather, not on yesterday's
  umbrella.

With these, the whole infinite process is described by three small tables: the **prior** $P(X_0)$, the transition model
$P(X_t \mid X_{t-1})$ and the sensor model $P(E_t \mid X_t)$. For the umbrella world:

| | $P(\text{rain}_t)$ | | $P(\text{umbrella}_t)$ |
|---|---|---|---|
| $\text{rain}_{t-1}$ | 0.7 | $\text{rain}_t$ | 0.9 |
| $\lnot\text{rain}_{t-1}$ | 0.3 | $\lnot\text{rain}_t$ | 0.2 |

and $P(\text{rain}_0) = 0.5$. Drawn as a Bayesian network, the model is a chain of state nodes, each with one child,
its evidence.

<figure class="mars-fig" markdown="0">
<svg viewBox="0 0 640 210" role="img" aria-label="An unrolled hidden Markov model: a chain of hidden state nodes X0, X1, X2, X3 joined by arrows, each of X1 to X3 with an arrow down to its evidence node E1, E2, E3. The transition table sits on the arrows between states and the sensor table on the arrows to evidence.">
<circle cx="70" cy="60" r="28" fill="#9cc9ea" fill-opacity="0.5" stroke="currentColor" stroke-width="1.3"/>
<text x="70" y="65" font-size="15" text-anchor="middle" fill="currentColor">X₀</text>
<circle cx="230" cy="60" r="28" fill="#9cc9ea" fill-opacity="0.5" stroke="currentColor" stroke-width="1.3"/>
<text x="230" y="65" font-size="15" text-anchor="middle" fill="currentColor">X₁</text>
<circle cx="390" cy="60" r="28" fill="#9cc9ea" fill-opacity="0.5" stroke="currentColor" stroke-width="1.3"/>
<text x="390" y="65" font-size="15" text-anchor="middle" fill="currentColor">X₂</text>
<circle cx="550" cy="60" r="28" fill="#9cc9ea" fill-opacity="0.5" stroke="currentColor" stroke-width="1.3"/>
<text x="550" y="65" font-size="15" text-anchor="middle" fill="currentColor">X₃</text>
<line x1="98" y1="60" x2="196" y2="60" stroke="currentColor" stroke-width="1.5"/>
<polygon points="202,60 192,55 192,65" fill="currentColor"/>
<line x1="258" y1="60" x2="356" y2="60" stroke="currentColor" stroke-width="1.5"/>
<polygon points="362,60 352,55 352,65" fill="currentColor"/>
<line x1="418" y1="60" x2="516" y2="60" stroke="currentColor" stroke-width="1.5"/>
<polygon points="522,60 512,55 512,65" fill="currentColor"/>
<text x="150" y="48" font-size="12" text-anchor="middle" fill="currentColor">P(Xₜ | Xₜ₋₁)</text>
<text x="310" y="48" font-size="12" text-anchor="middle" fill="currentColor">P(Xₜ | Xₜ₋₁)</text>
<text x="470" y="48" font-size="12" text-anchor="middle" fill="currentColor">P(Xₜ | Xₜ₋₁)</text>
<rect x="205" y="140" width="50" height="40" rx="6" fill="#eea66f" fill-opacity="0.5" stroke="currentColor" stroke-width="1.3"/>
<text x="230" y="165" font-size="15" text-anchor="middle" fill="currentColor">E₁</text>
<rect x="365" y="140" width="50" height="40" rx="6" fill="#eea66f" fill-opacity="0.5" stroke="currentColor" stroke-width="1.3"/>
<text x="390" y="165" font-size="15" text-anchor="middle" fill="currentColor">E₂</text>
<rect x="525" y="140" width="50" height="40" rx="6" fill="#eea66f" fill-opacity="0.5" stroke="currentColor" stroke-width="1.3"/>
<text x="550" y="165" font-size="15" text-anchor="middle" fill="currentColor">E₃</text>
<line x1="230" y1="88" x2="230" y2="132" stroke="currentColor" stroke-width="1.5"/>
<polygon points="230,138 225,128 235,128" fill="currentColor"/>
<line x1="390" y1="88" x2="390" y2="132" stroke="currentColor" stroke-width="1.5"/>
<polygon points="390,138 385,128 395,128" fill="currentColor"/>
<line x1="550" y1="88" x2="550" y2="132" stroke="currentColor" stroke-width="1.5"/>
<polygon points="550,138 545,128 555,128" fill="currentColor"/>
<text x="295" y="118" font-size="12" text-anchor="middle" fill="currentColor">P(Eₜ | Xₜ)</text>
<text x="70" y="120" font-size="12" text-anchor="middle" fill="currentColor">prior P(X₀)</text>
<text x="390" y="203" font-size="12" text-anchor="middle" fill="currentColor">hidden states on top (circles), observed evidence below (boxes)</text>
</svg>
<figcaption>The umbrella world unrolled for three days. Every arrow between states carries the same transition table,
and every downward arrow the same sensor table: stationarity means three small tables describe all of time.</figcaption>
</figure>

The full joint distribution of everything up to time $t$ follows from the chain rule of Bayesian networks
([Chapter 12](12-Probabilistic-Reasoning.md)): each node given its parents.

$$
P(X_{0:t}, E_{1:t}) = P(X_0) \prod_{i=1}^{t} P(X_i \mid X_{i-1})\, P(E_i \mid X_i).
$$

Every result in this chapter is a way of computing a sum or a maximum of this product without writing it out for every
one of the exponentially many state sequences.

### Is the Markov assumption true?

Usually not exactly, and that is fine. Two remedies exist when it is too crude.

- **Raise the order.** A second-order process conditions on $X_{t-1}$ and $X_{t-2}$. Any $k$-th-order process becomes a
  first-order one if you redefine the state as the tuple of the last $k$ states (Exercise 1), so first-order is no loss
  of generality, only of compactness.
- **Enlarge the state.** Rain depends on season, pressure, humidity. Add them to $X_t$ and the Markov assumption
  becomes more accurate. For a robot, position alone is not Markov (where it goes next depends on its speed);
  position and velocity together nearly are. Choosing a state that makes the world Markov is the modelling art behind
  everything below.

## 13.2 Filtering, prediction, smoothing, most-likely sequence

What questions can the guard ask? Four of them come up again and again, in every application from speech to spacecraft.

- **Filtering** (also called state estimation or monitoring): $P(X_t \mid e_{1:t})$, the belief about the state **now**,
  given all evidence so far. This is what an agent needs to act. The distribution is called the **belief state**, the
  same idea as in [Chapter 5](05-Local-Search-and-Optimization.md), now with probabilities.
- **Prediction**: $P(X_{t+k} \mid e_{1:t})$ for $k > 0$, the belief about a future state.
- **Smoothing**: $P(X_k \mid e_{1:t})$ for $0 \le k < t$, the belief about a past state, using evidence that came
  after it. Hindsight is better than foresight: smoothing is more accurate than filtering.
- **Most likely explanation**: $\arg\max_{x_{1:t}} P(x_{1:t} \mid e_{1:t})$, the single most probable sequence of
  states. Speech recognition asks this: which sequence of words best explains these sounds?

A fifth task, **learning** the transition and sensor models from observation sequences, is done by the EM algorithm
([Machine learning, Chapter 13](../machine-learning/13-Clustering.md) derives EM for mixtures); for HMMs the special case
is the Baum-Welch algorithm, which uses the smoothed distributions of this section as its E-step.

### Filtering by recursion

The key design goal is **recursive** estimation: compute the new belief from the old belief and the new evidence only,

$$
P(X_{t+1} \mid e_{1:t+1}) = f\big(e_{t+1},\, P(X_t \mid e_{1:t})\big),
$$

so that the cost per step stays constant, however long the agent has been running. Here is the derivation. Split the
evidence into the old part and the new observation, then apply Bayes' rule with $e_{1:t}$ held fixed in the background:

$$
\begin{aligned}
P(X_{t+1} \mid e_{1:t+1}) &= P(X_{t+1} \mid e_{1:t}, e_{t+1}) \\
&= \alpha\, P(e_{t+1} \mid X_{t+1}, e_{1:t})\, P(X_{t+1} \mid e_{1:t}) \\
&= \alpha\, P(e_{t+1} \mid X_{t+1})\, P(X_{t+1} \mid e_{1:t}).
\end{aligned}
$$

Here $\alpha$ is a normalising constant: whatever number makes the probabilities sum to 1. The last line used the
sensor Markov assumption. The second factor is a one-step **prediction**. To compute it, condition on the current state
$x_t$ and sum it out:

$$
P(X_{t+1} \mid e_{1:t}) = \sum_{x_t} P(X_{t+1} \mid x_t)\, P(x_t \mid e_{1:t}),
$$

using the Markov assumption to drop $e_{1:t}$ from the transition. Put together, with $f_{1:t}$ standing for the
filtered distribution $P(X_t \mid e_{1:t})$ (called the **forward message**):

$$
f_{1:t+1} = \alpha\, P(e_{t+1} \mid X_{t+1}) \sum_{x_t} P(X_{t+1} \mid x_t)\, f_{1:t}(x_t).
$$

Read it as two steps that every filter in this chapter repeats, the Kalman filter and the particle filter included:

1. **Predict:** push the belief through the transition model. Uncertainty grows.
2. **Update:** multiply by the likelihood of the new evidence and renormalise. Uncertainty usually shrinks.

**Cost.** With $S$ possible states, the prediction is a vector-matrix product costing $O(S^2)$, and the update costs
$O(S)$. Each step costs $O(S^2)$ time and $O(S)$ memory, independent of $t$. That is the point.

### A worked example by hand

Day 0: $P(R_0) = \langle 0.5, 0.5 \rangle$ (we list $\langle$rain, no rain$\rangle$).

**Day 1, umbrella seen.** Predict:
$P(R_1) = 0.7 \cdot 0.5 + 0.3 \cdot 0.5 = 0.5$, so $\langle 0.5, 0.5 \rangle$. Update with
$P(u \mid R) = \langle 0.9, 0.2 \rangle$: $\langle 0.45, 0.10 \rangle$, normalised $\langle 0.818, 0.182 \rangle$.

**Day 2, umbrella seen.** Predict:
$0.7 \cdot 0.818 + 0.3 \cdot 0.182 = 0.627$, so $\langle 0.627, 0.373 \rangle$. Update:
$\langle 0.9 \cdot 0.627, 0.2 \cdot 0.373 \rangle = \langle 0.565, 0.075 \rangle$, normalised
$\langle 0.883, 0.117 \rangle$.

The belief in rain rose from 0.818 to 0.883: the second umbrella confirms the first, and the transition model says rain
persists. The normalising constants are useful too. Before normalising on day 1 the entries summed to 0.55; that is
$P(u_1)$. Multiplying the sums of all days gives the **likelihood** of the whole evidence sequence,
$P(e_{1:t})$, which is how one compares two models of the same data.

### Prediction and the mixing time

Prediction is filtering without updates: apply the transition step $k$ times. What happens as $k$ grows? For the
umbrella chain, write $p_k = P(\text{rain}_{t+k} \mid e_{1:t})$. Then
$p_{k+1} = 0.7 p_k + 0.3 (1 - p_k) = 0.3 + 0.4 p_k$, so

$$
p_{k} - 0.5 = 0.4^{k}\,(p_0 - 0.5).
$$

The prediction converges geometrically to 0.5, the **stationary distribution** of the chain: the distribution $\pi$
with $\pi = \pi T$. The speed is set by the second eigenvalue of the transition matrix ($0.4$ here; the first is
always 1). The time it takes to forget the start is the **mixing time**. Far enough ahead, the evidence no longer
matters; this is why a weather forecast for a month from now is the climate.

### Smoothing: the backward message

To estimate $X_k$ with evidence up to $t > k$, split the evidence at $k$:

$$
\begin{aligned}
P(X_k \mid e_{1:t}) &= \alpha\, P(X_k \mid e_{1:k})\, P(e_{k+1:t} \mid X_k, e_{1:k}) \\
&= \alpha\, f_{1:k} \times b_{k+1:t},
\end{aligned}
$$

where $\times$ is pointwise multiplication and $b_{k+1:t} = P(e_{k+1:t} \mid X_k)$ is the **backward message** (the
conditioning on $e_{1:k}$ disappears because, given $X_k$, the future evidence is independent of the past evidence:
$X_k$ blocks every path between them in the chain). The backward message also has a recursion, running from the end
towards the start. Condition on $x_{k+1}$:

$$
\begin{aligned}
b_{k+1:t}(X_k) &= \sum_{x_{k+1}} P(e_{k+1:t} \mid X_k, x_{k+1})\, P(x_{k+1} \mid X_k) \\
&= \sum_{x_{k+1}} P(e_{k+1} \mid x_{k+1})\, P(e_{k+2:t} \mid x_{k+1})\, P(x_{k+1} \mid X_k) \\
&= \sum_{x_{k+1}} P(e_{k+1} \mid x_{k+1})\, b_{k+2:t}(x_{k+1})\, P(x_{k+1} \mid X_k),
\end{aligned}
$$

starting from $b_{t+1:t} = \mathbf{1}$ (the probability of observing nothing is 1). The second line used both Markov
assumptions: given $x_{k+1}$, the evidence $e_{k+1}$ and the later evidence $e_{k+2:t}$ are independent of each other
and of $X_k$.

**Smoothing day 1 with two umbrellas, by hand.** $b_{2:2}(R_1) = \sum_{r_2} P(u_2 \mid r_2) \cdot 1 \cdot P(r_2 \mid R_1)$:
for $R_1$ = rain it is $0.9 \cdot 0.7 + 0.2 \cdot 0.3 = 0.69$; for no rain, $0.9 \cdot 0.3 + 0.2 \cdot 0.7 = 0.41$.
Multiply by $f_{1:1} = \langle 0.818, 0.182 \rangle$: $\langle 0.5645, 0.0745 \rangle$, normalised
$\langle 0.883, 0.117 \rangle$. Knowing that the director carried an umbrella on day 2 raises our belief in rain on day 1
from 0.818 to 0.883.

The **forward-backward algorithm** smooths every time step at once: one forward pass storing all $f_{1:k}$, one backward
pass computing each $b_{k+1:t}$ and multiplying. It costs $O(S^2 t)$ time, against $O(S^2 t^2)$ for smoothing each step
separately, and $O(S t)$ memory. (If memory is short, there are versions that keep only $O(\sqrt{t})$ or $O(\log t)$ of
the forward messages and recompute the rest; for online use, **fixed-lag smoothing** keeps a window of the last $d$
steps.)

### The most likely sequence is not the sequence of most likely states

Suppose the umbrella sequence is $u, u, \lnot u, u, u$. Smoothing gives, for each day, the probability of rain. You might
pick the more likely state on each day and call that the explanation. That gives the sequence that is right on the
largest **expected number of days**, but it may not be the most probable **whole sequence**, and it may even be
impossible as a sequence (picture a model where state A can never follow state B, but A is the most likely state on
day 3 and B on day 2). Different questions, different answers; the next section computes both.

## 13.3 Hidden Markov models: forward algorithm, Viterbi, from scratch

*Level: intermediate.*

A **hidden Markov model** (HMM) is the special case where the state is a single discrete variable with $S$ values.
(Any model with several discrete state variables can be squeezed into one by taking all their combinations, at an
exponential price; 13.6 comes back to this.) The single variable lets us write everything as matrices.

- The **transition matrix** $\mathbf{T}$ is $S \times S$, with $\mathbf{T}_{ij} = P(X_t = j \mid X_{t-1} = i)$. Each row sums
  to 1.
- For each time step, the **sensor matrix** $\mathbf{O}_t$ is the $S \times S$ diagonal matrix whose $i$-th diagonal entry
  is $P(e_t \mid X_t = i)$.

Treating messages as row vectors, the forward and backward recursions become

$$
f_{1:t+1} = \alpha\, f_{1:t}\, \mathbf{T}\, \mathbf{O}_{t+1}, \qquad
b_{k+1:t} = \mathbf{T}\, \mathbf{O}_{k+1}\, b_{k+2:t}^{\top}.
$$

The forward message is a row vector multiplied on the right; the backward message is a column vector multiplied on the
left. In NumPy each is one line.

### The Viterbi algorithm

To find the most likely sequence, look at the joint probability of a path. Define $m_{1:t}(x_t)$ as the probability of
the **best** path that ends in state $x_t$ at time $t$, together with the evidence:

$$
m_{1:t}(x_t) = \max_{x_{1:t-1}} P(x_{1:t-1}, x_t, e_{1:t}).
$$

The best path to $x_{t+1}$ must pass through some $x_t$, and its first part must then be the best path to that $x_t$:
if it were not, replacing it with the best one would give a more probable path to $x_{t+1}$, a contradiction. This is
the **principle of optimality** of dynamic programming, and it gives

$$
m_{1:t+1}(x_{t+1}) = P(e_{t+1} \mid x_{t+1}) \max_{x_t} \Big( P(x_{t+1} \mid x_t)\, m_{1:t}(x_t) \Big).
$$

This is the filtering recursion with the sum replaced by a max. To recover the path itself we store, for each state
at each step, which $x_t$ achieved the max (a **back-pointer**). At the end, pick the state with the largest $m$ and
follow the back-pointers backwards. Because the probability of a long path is a product of many numbers below 1, it
underflows quickly; we work with logarithms, turning products into sums and keeping the max (log is increasing).

**Correctness.** By induction on $t$, $m_{1:t}(x)$ equals the best joint probability of any path ending in $x$, and the
back-pointers trace such a path: the base case $t = 1$ is the definition, and the step is the optimality argument above.
Since $P(x_{1:t} \mid e_{1:t}) = P(x_{1:t}, e_{1:t}) / P(e_{1:t})$ and the denominator does not depend on the path, the
path with the largest joint probability is the most likely explanation. **Cost:** $O(S^2 t)$ time and $O(S t)$ memory
for the back-pointers, against $S^t$ paths for brute force.

### Tracing Viterbi by hand

For $u, u, \lnot u, u, u$, using the umbrella model (we start from $P(X_1) = \langle 0.5, 0.5 \rangle$, the prediction
from day 0):

| day | evidence | $m(\text{rain})$ | from | $m(\lnot\text{rain})$ | from |
|---|---|---|---|---|---|
| 1 | $u$ | $0.5 \cdot 0.9 = 0.45$ | | $0.5 \cdot 0.2 = 0.10$ | |
| 2 | $u$ | $0.9 \cdot \max(0.45 \cdot 0.7,\ 0.10 \cdot 0.3) = 0.2835$ | rain | $0.2 \cdot \max(0.45 \cdot 0.3,\ 0.10 \cdot 0.7) = 0.0270$ | rain |
| 3 | $\lnot u$ | $0.1 \cdot \max(0.19845,\ 0.0081) = 0.019845$ | rain | $0.8 \cdot \max(0.08505,\ 0.0189) = 0.06804$ | rain |
| 4 | $u$ | $0.9 \cdot \max(0.0138915,\ 0.020412) = 0.018371$ | no rain | $0.2 \cdot \max(0.0059535,\ 0.047628) = 0.009526$ | no rain |
| 5 | $u$ | $0.9 \cdot \max(0.012860,\ 0.002858) = 0.011574$ | rain | $0.2 \cdot \max(0.005511,\ 0.006668) = 0.001334$ | no rain |

On day 5 rain wins with 0.011574. Follow the "from" column backwards: day 5 rain came from day 4 rain, which came from
day 3 no rain, which came from day 2 rain, which came from day 1 rain. The most likely sequence is
rain, rain, dry, rain, rain. Notice the interesting step on day 4: the best path to rain on day 4 comes through a dry
day 3, because the evidence on day 3 strongly said dry.

<figure class="mars-fig" markdown="0">
<svg viewBox="0 0 640 230" role="img" aria-label="The Viterbi trellis for five days: two rows of nodes, rain and no rain, with the probability of the best path into each node. Thick green arrows show the back-pointers of the winning path: rain, rain, no rain, rain, rain.">
<text x="40" y="74" font-size="13" text-anchor="middle" fill="currentColor">rain</text>
<text x="40" y="164" font-size="13" text-anchor="middle" fill="currentColor">dry</text>
<line x1="138" y1="70" x2="232" y2="70" stroke="#7ccf9a" stroke-width="5"/>
<line x1="248" y1="70" x2="342" y2="160" stroke="#7ccf9a" stroke-width="5"/>
<line x1="358" y1="160" x2="452" y2="70" stroke="#7ccf9a" stroke-width="5"/>
<line x1="468" y1="70" x2="562" y2="70" stroke="#7ccf9a" stroke-width="5"/>
<line x1="138" y1="70" x2="232" y2="160" stroke="currentColor" stroke-width="1" stroke-dasharray="4 3"/>
<line x1="248" y1="70" x2="342" y2="70" stroke="currentColor" stroke-width="1" stroke-dasharray="4 3"/>
<line x1="358" y1="160" x2="452" y2="160" stroke="currentColor" stroke-width="1" stroke-dasharray="4 3"/>
<line x1="468" y1="160" x2="562" y2="160" stroke="currentColor" stroke-width="1" stroke-dasharray="4 3"/>
<circle cx="130" cy="70" r="9" fill="#9cc9ea" stroke="currentColor"/>
<circle cx="240" cy="70" r="9" fill="#9cc9ea" stroke="currentColor"/>
<circle cx="350" cy="70" r="9" fill="#9cc9ea" stroke="currentColor"/>
<circle cx="460" cy="70" r="9" fill="#9cc9ea" stroke="currentColor"/>
<circle cx="570" cy="70" r="9" fill="#9cc9ea" stroke="currentColor"/>
<circle cx="130" cy="160" r="9" fill="#eea66f" stroke="currentColor"/>
<circle cx="240" cy="160" r="9" fill="#eea66f" stroke="currentColor"/>
<circle cx="350" cy="160" r="9" fill="#eea66f" stroke="currentColor"/>
<circle cx="460" cy="160" r="9" fill="#eea66f" stroke="currentColor"/>
<circle cx="570" cy="160" r="9" fill="#eea66f" stroke="currentColor"/>
<text x="130" y="50" font-size="12" text-anchor="middle" fill="currentColor">.45</text>
<text x="240" y="50" font-size="12" text-anchor="middle" fill="currentColor">.2835</text>
<text x="350" y="50" font-size="12" text-anchor="middle" fill="currentColor">.0198</text>
<text x="460" y="50" font-size="12" text-anchor="middle" fill="currentColor">.0184</text>
<text x="570" y="50" font-size="12" text-anchor="middle" fill="currentColor">.0116</text>
<text x="130" y="188" font-size="12" text-anchor="middle" fill="currentColor">.10</text>
<text x="240" y="188" font-size="12" text-anchor="middle" fill="currentColor">.0270</text>
<text x="350" y="188" font-size="12" text-anchor="middle" fill="currentColor">.0680</text>
<text x="460" y="188" font-size="12" text-anchor="middle" fill="currentColor">.0095</text>
<text x="570" y="188" font-size="12" text-anchor="middle" fill="currentColor">.0013</text>
<text x="130" y="20" font-size="13" text-anchor="middle" fill="currentColor">day 1: u</text>
<text x="240" y="20" font-size="13" text-anchor="middle" fill="currentColor">day 2: u</text>
<text x="350" y="20" font-size="13" text-anchor="middle" fill="currentColor">day 3: no u</text>
<text x="460" y="20" font-size="13" text-anchor="middle" fill="currentColor">day 4: u</text>
<text x="570" y="20" font-size="13" text-anchor="middle" fill="currentColor">day 5: u</text>
<text x="350" y="220" font-size="12" text-anchor="middle" fill="currentColor">thick: the winning path's back-pointers; dashed: the other back-pointers</text>
</svg>
<figcaption>The Viterbi trellis for umbrella, umbrella, no umbrella, umbrella, umbrella. Each node holds the probability of the best path into it;
each node keeps one back-pointer. Following the back-pointers from the best final node (rain, 0.0116) gives the most
likely explanation.</figcaption>
</figure>

### The code

The program implements all four tasks for the umbrella world, checks Viterbi and the likelihood $P(e_{1:5})$ against
brute force over all $2^5 = 32$ sequences, and then runs the filters over 10 000 simulated days to measure how often
each method guesses the hidden state correctly. It normalises the forward and backward messages at every step, which is
how one avoids underflow without logarithms (the log of the product of the normalising constants is the log
likelihood).

```python
--8<-- "books/ai/ch13_hmm.py"
```

```
evidence     : U U - U U
day  P(rain | e_1..t) filtered   P(rain | e_1..5) smoothed
  1      0.8182                     0.8673
  2      0.8834                     0.8204
  3      0.1907                     0.3075
  4      0.7308                     0.8204
  5      0.8673                     0.8673
P(e_1..5) = 0.034304
prediction from day 5:  day 6: 0.6469  day 7: 0.5588  day 10: 0.5038  day 15: 0.5000  day 30: 0.5000
Viterbi path : R R . R R  probability 0.011574
brute force  : R R . R R  probability 0.011574   sum over all sequences 0.034304

10000 sampled days, fraction of days whose hidden state is guessed right
umbrella world   : log P(e) =  -6645.6   filtering 0.8530   smoothing 0.8530   Viterbi 0.8483   today's evidence alone 0.8530
sticky, poor eyes: log P(e) =  -6768.2   filtering 0.7400   smoothing 0.7924   Viterbi 0.7616   today's evidence alone 0.6956
```

What the output shows:

- **Filtered and smoothed values differ where hindsight helps.** On day 3 (no umbrella) filtering says 0.19 for rain;
  smoothing, knowing umbrellas came on days 4 and 5, raises it to 0.31. On the last day the two always agree: there is
  no later evidence.
- **Prediction** follows the formula $0.5 + 0.4^k (0.8673 - 0.5)$: $0.6469$ for $k = 1$, $0.5588$ for $k = 2$, and
  within $10^{-4}$ of 0.5 after about ten steps.
- **Viterbi and brute force agree**, and the sum of the 32 sequence probabilities equals the forward algorithm's
  $P(e_{1:5}) = 0.034304$.
- **The first simulated world teaches a lesson.** In the umbrella model all three methods are no better than reading
  today's umbrella. The sensor is so good compared with the 0.7 persistence that the posterior always lands on the side
  the evidence points to (check: the worst case for "rain after an umbrella" is a prediction of 0.3, and
  $0.3 \cdot 0.9 / (0.3 \cdot 0.9 + 0.7 \cdot 0.2) = 0.66 > 0.5$). Inference is only worth its cost when the state
  carries information that one observation does not.
- **In the second world** the state is sticky (stays the same with probability 0.9) and the sensor is poor (right 70
  percent of the time). Now filtering (74.0 percent) beats raw evidence (69.6 percent), smoothing beats filtering
  (79.2 percent), and Viterbi (76.2 percent) lies between. Smoothing wins on this score by construction: picking the
  state with the largest smoothed probability on each day maximises the expected number of correct days (Exercise 4);
  Viterbi maximises the chance of getting the whole sequence right, a different target.

### A short history

Leonard Baum and colleagues at the Institute for Defense Analyses worked out the statistical theory of HMMs and the
forward-backward re-estimation procedure in a series of papers from 1966 to 1970. Andrew Viterbi published his algorithm
in 1967 to decode convolutional error-correcting codes; G. David Forney showed in 1973 that it is exactly a
most-likely-path computation on a trellis. In the 1970s James Baker at Carnegie Mellon and Frederick Jelinek's group at
IBM used HMMs for speech recognition, and HMMs dominated speech recognition until neural networks replaced the acoustic
models in the 2010s. Lawrence Rabiner's 1989 tutorial remains the standard introduction. HMMs are still in daily use in
bioinformatics (gene finding, protein families) and appear again in [Chapter 16](16-Natural-Language-Processing.md) for
part-of-speech tagging.

## 13.4 Kalman filters, derived in 1-D, used for tracking

*Level: intermediate (the matrix filter is advanced).*

Some states are not discrete. A spacecraft's position, a car's speed, the temperature of a reactor: these are real
numbers, and the filtering sum $\sum_{x_t}$ becomes an integral, which in general has no closed form. There is one
famous family where everything stays exact and cheap: **linear** models with **Gaussian** noise. Then every belief is a
Gaussian, described by a mean and a variance (or, in several dimensions, a mean vector and a covariance matrix), and
filtering is a few lines of arithmetic. This is the **Kalman filter**.

### Gaussians

A **Gaussian** (normal) distribution with mean $\mu$ and variance $\sigma^2$ has density

$$
N(x; \mu, \sigma^2) = \frac{1}{\sqrt{2\pi\sigma^2}} \exp\!\Big(-\frac{(x-\mu)^2}{2\sigma^2}\Big).
$$

Two facts make it special. First, **the exponent is a quadratic in $x$**, and any density whose log is a quadratic with
a negative $x^2$ coefficient is a Gaussian; you can read off the mean and variance by completing the square. Second,
**adding independent Gaussian noise to a Gaussian gives a Gaussian**, with the variances added.

### The 1-D model

The simplest case is a quantity that wanders randomly (a **random walk**) and is measured with noise:

- transition: $x_{t+1} = x_t + w_t$, with $w_t \sim N(0, q)$ (the **process noise**, variance $q$);
- sensor: $z_t = x_t + v_t$, with $v_t \sim N(0, r)$ (the **measurement noise**, variance $r$).

Suppose the current belief is $N(\mu_t, \sigma_t^2)$.

**Predict.** $x_{t+1}$ is a Gaussian plus independent Gaussian noise, so

$$
P(x_{t+1} \mid z_{1:t}) = N(\mu_t,\ \sigma_t^2 + q) = N(\bar\mu, \bar\sigma^2).
$$

The mean stays where it was; the variance grows by $q$.

**Update.** By the filtering equation, the new belief is proportional to the prediction times the likelihood of the
reading $z_{t+1}$:

$$
P(x_{t+1} \mid z_{1:t+1}) = \alpha \exp\!\Big(-\frac{(x - \bar\mu)^2}{2\bar\sigma^2}\Big) \exp\!\Big(-\frac{(z_{t+1} - x)^2}{2r}\Big).
$$

The exponent is $-\tfrac12$ times

$$
\frac{(x - \bar\mu)^2}{\bar\sigma^2} + \frac{(x - z)^2}{r}
= \Big(\frac{1}{\bar\sigma^2} + \frac{1}{r}\Big) x^2 - 2\Big(\frac{\bar\mu}{\bar\sigma^2} + \frac{z}{r}\Big) x + \text{const}.
$$

Completing the square, a quadratic $a x^2 - 2 b x + c$ equals $a (x - b/a)^2$ plus a constant, so the result is a
Gaussian with variance $1/a$ and mean $b/a$:

$$
\sigma_{t+1}^2 = \frac{1}{1/\bar\sigma^2 + 1/r} = \frac{\bar\sigma^2 r}{\bar\sigma^2 + r}, \qquad
\mu_{t+1} = \frac{r \bar\mu + \bar\sigma^2 z_{t+1}}{\bar\sigma^2 + r}.
$$

Two readings of these formulas tell you everything about the Kalman filter.

- **Precisions add.** The inverse of a variance is called the **precision**. The new precision is the prediction's
  precision plus the sensor's precision. Every reading makes you more certain, however bad the sensor.
- **The new mean is a weighted average** of the prediction and the reading, each weighted by its precision. Written with
  the **Kalman gain** $K = \bar\sigma^2 / (\bar\sigma^2 + r)$, a number between 0 and 1:

$$
\mu_{t+1} = \bar\mu + K\,(z_{t+1} - \bar\mu), \qquad \sigma_{t+1}^2 = (1 - K)\,\bar\sigma^2.
$$

The difference $z_{t+1} - \bar\mu$ is the **innovation**: how much the reading surprised us. When the prediction is
vague ($\bar\sigma^2 \gg r$), $K$ is near 1 and the filter jumps to the reading. When the sensor is bad ($r \gg \bar\sigma^2$),
$K$ is near 0 and the filter barely moves.

<figure class="mars-fig" markdown="0">
<svg viewBox="0 0 640 280" role="img" aria-label="Three Gaussian curves over the same axis: the prediction centred at 2.40 with variance 4.85, the reading centred at 1.0 with variance 4, and the narrower, taller posterior centred at 1.64 with variance 2.19, between the two.">
<line x1="60" y1="230" x2="600" y2="230" stroke="currentColor" stroke-width="1.2"/>
<text x="60.0" y="248" font-size="12" text-anchor="middle" fill="currentColor">-5</text>
<text x="252.9" y="248" font-size="12" text-anchor="middle" fill="currentColor">0</text>
<text x="445.7" y="248" font-size="12" text-anchor="middle" fill="currentColor">5</text>
<text x="600.0" y="248" font-size="12" text-anchor="middle" fill="currentColor">9</text>
<line x1="252.9" y1="230" x2="252.9" y2="235" stroke="currentColor"/>
<line x1="445.7" y1="230" x2="445.7" y2="235" stroke="currentColor"/>
<polyline fill="none" stroke="#eea66f" stroke-width="2.5" points="60.0,229.7 69.6,229.5 79.3,229.3 88.9,229.1 98.6,228.7 108.2,228.2 117.9,227.5 127.5,226.7 137.1,225.5 146.8,224.2 156.4,222.4 166.1,220.3 175.7,217.8 185.4,214.7 195.0,211.2 204.6,207.2 214.3,202.6 223.9,197.5 233.6,192.1 243.2,186.2 252.9,180.1 262.5,173.9 272.1,167.7 281.8,161.7 291.4,156.1 301.1,151.0 310.7,146.7 320.4,143.3 330.0,140.9 339.6,139.6 349.3,139.5 358.9,140.5 368.6,142.7 378.2,145.8 387.9,149.9 397.5,154.8 407.1,160.3 416.8,166.2 426.4,172.4 436.1,178.6 445.7,184.8 455.4,190.7 465.0,196.3 474.6,201.4 484.3,206.1 493.9,210.3 503.6,213.9 513.2,217.1 522.9,219.7 532.5,222.0 542.1,223.8 551.8,225.2 561.4,226.4 571.1,227.3 580.7,228.0 590.4,228.6 600.0,229.0"/>
<polyline fill="none" stroke="#9cc9ea" stroke-width="2.5" stroke-dasharray="6 4" points="60.0,228.9 69.6,228.4 79.3,227.7 88.9,226.8 98.6,225.6 108.2,224.1 117.9,222.1 127.5,219.6 137.1,216.5 146.8,212.8 156.4,208.4 166.1,203.4 175.7,197.6 185.4,191.2 195.0,184.3 204.6,177.0 214.3,169.5 223.9,162.0 233.6,154.7 243.2,148.0 252.9,142.0 262.5,137.0 272.1,133.3 281.8,131.0 291.4,130.3 301.1,131.0 310.7,133.3 320.4,137.0 330.0,142.0 339.6,148.0 349.3,154.7 358.9,162.0 368.6,169.5 378.2,177.0 387.9,184.3 397.5,191.2 407.1,197.6 416.8,203.4 426.4,208.4 436.1,212.8 445.7,216.5 455.4,219.6 465.0,222.1 474.6,224.1 484.3,225.6 493.9,226.8 503.6,227.7 513.2,228.4 522.9,228.9 532.5,229.2 542.1,229.5 551.8,229.7 561.4,229.8 571.1,229.9 580.7,229.9 590.4,229.9 600.0,230.0"/>
<polyline fill="none" stroke="#7ccf9a" stroke-width="3" points="60.0,230.0 69.6,230.0 79.3,230.0 88.9,230.0 98.6,229.9 108.2,229.8 117.9,229.7 127.5,229.4 137.1,229.0 146.8,228.3 156.4,227.3 166.1,225.7 175.7,223.4 185.4,220.1 195.0,215.7 204.6,209.8 214.3,202.4 223.9,193.2 233.6,182.4 243.2,170.1 252.9,156.8 262.5,143.0 272.1,129.6 281.8,117.3 291.4,107.1 301.1,99.7 310.7,95.8 320.4,95.7 330.0,99.3 339.6,106.4 349.3,116.4 358.9,128.5 368.6,141.9 378.2,155.7 387.9,169.1 397.5,181.4 407.1,192.4 416.8,201.7 426.4,209.3 436.1,215.3 445.7,219.8 455.4,223.2 465.0,225.5 474.6,227.2 484.3,228.3 493.9,229.0 503.6,229.4 513.2,229.7 522.9,229.8 532.5,229.9 542.1,229.9 551.8,230.0 561.4,230.0 571.1,230.0 580.7,230.0 590.4,230.0 600.0,230.0"/>
<line x1="345.6" y1="139" x2="345.6" y2="230" stroke="#eea66f" stroke-width="1" stroke-dasharray="2 3"/>
<line x1="291.4" y1="130" x2="291.4" y2="230" stroke="#9cc9ea" stroke-width="1" stroke-dasharray="2 3"/>
<line x1="317.4" y1="95" x2="317.4" y2="230" stroke="#7ccf9a" stroke-width="1" stroke-dasharray="2 3"/>
<text x="420" y="132" font-size="13" fill="currentColor">prediction N(2.40, 4.85)</text>
<text x="80" y="120" font-size="13" fill="currentColor">reading z = 1.0, variance 4</text>
<text x="340" y="80" font-size="13" fill="currentColor">posterior N(1.64, 2.19)</text>
<rect x="420" y="140" width="14" height="4" fill="#eea66f"/>
<rect x="80" y="128" width="14" height="4" fill="#9cc9ea"/>
<rect x="340" y="86" width="14" height="4" fill="#7ccf9a"/>
</svg>
<figcaption>Step 2 of the 1-D example below. The posterior (green) lies between the prediction and the reading,
closer to the more precise one, and is narrower than both: precisions add.</figcaption>
</figure>

### The steady state

In the 1-D random walk the variance does not depend on the readings at all, only on $q$, $r$ and the start, so it can be
computed in advance. Does it settle? A fixed point $P$ of the predict-update cycle satisfies
$P = (P + q) r / (P + q + r)$. Multiply out: $P^2 + qP + rP = rP + qr$, so $P^2 + qP - qr = 0$, with the positive root

$$
P_\infty = \frac{-q + \sqrt{q^2 + 4qr}}{2}.
$$

The map $P \mapsto (P + q) r / (P + q + r)$ is increasing with slope $r^2 / (P + q + r)^2 < 1$, so iterating it
converges to $P_\infty$ from any start. For $q = 1$, $r = 4$: $P_\infty = (\sqrt{17} - 1)/2 \approx 1.5616$. With process
noise, the filter never becomes certain: each prediction adds back uncertainty that the next reading only partly removes.

### The matrix filter

*Level: advanced.*

Real tracking needs several state variables. A target moving along a line has position $p$ and velocity $v$; with time
step $\Delta t$, $p_{t+1} = p_t + v_t \Delta t$ and $v_{t+1} = v_t$, plus small random accelerations. In general:

- transition: $\mathbf{x}_{t+1} = \mathbf{F}\mathbf{x}_t + \mathbf{w}_t$, with $\mathbf{w}_t \sim N(\mathbf{0}, \mathbf{Q})$;
- sensor: $\mathbf{z}_t = \mathbf{H}\mathbf{x}_t + \mathbf{v}_t$, with $\mathbf{v}_t \sim N(\mathbf{0}, \mathbf{R})$.

Here $\mathbf{F}$ is the motion matrix, $\mathbf{H}$ says what the sensor sees (for us, $\mathbf{H} = [1\ 0]$: position
only), and $\mathbf{Q}$, $\mathbf{R}$ are covariance matrices. The belief is $N(\boldsymbol{\mu}, \mathbf{P})$. The
same two steps, with matrices:

$$
\begin{aligned}
\text{predict:}\quad & \bar{\boldsymbol\mu} = \mathbf{F}\boldsymbol{\mu}, \qquad \bar{\mathbf{P}} = \mathbf{F}\mathbf{P}\mathbf{F}^\top + \mathbf{Q}, \\
\text{update:}\quad & \mathbf{K} = \bar{\mathbf{P}}\mathbf{H}^\top (\mathbf{H}\bar{\mathbf{P}}\mathbf{H}^\top + \mathbf{R})^{-1}, \\
& \boldsymbol{\mu}' = \bar{\boldsymbol\mu} + \mathbf{K}(\mathbf{z} - \mathbf{H}\bar{\boldsymbol\mu}), \qquad \mathbf{P}' = (\mathbf{I} - \mathbf{K}\mathbf{H})\bar{\mathbf{P}}.
\end{aligned}
$$

With one dimension, $\mathbf{F} = \mathbf{H} = 1$, these are exactly the 1-D formulas. The derivation is the same idea:
the predicted covariance is the covariance of a linear map plus noise, $\mathrm{Cov}(\mathbf{F}\mathbf{x} + \mathbf{w}) =
\mathbf{F}\,\mathrm{Cov}(\mathbf{x})\,\mathbf{F}^\top + \mathbf{Q}$, and the update conditions a joint Gaussian of
$(\mathbf{x}, \mathbf{z})$ on the observed $\mathbf{z}$. The algebra (completing the square in matrix form, or the
matrix inversion lemma) takes a page; Thrun, Burgard and Fox's *Probabilistic Robotics* (2005, chapter 3) gives it in
full. The cost per step is dominated by matrix products, $O(n^3)$ for $n$ state variables (plus the inverse of an
$m \times m$ matrix for $m$ sensor readings).

Why does the velocity estimate improve, when the sensor never measures velocity? Because $\bar{\mathbf{P}}$ has
off-diagonal terms: after one prediction, position and velocity are correlated (a larger velocity means a larger
position). The gain $\mathbf{K}$ then has a velocity component, and each position surprise also corrects the velocity.

### Tracking in code

The program runs the 1-D example step by step, checks the steady-state formula, then tracks a target that starts at 0 m
moving 2 m per step, with small random accelerations, from position readings with a standard deviation of 5 m.

```python
--8<-- "books/ai/ch13_kalman.py"
```

```
Part 1. 1-D random walk, q = 1, r = 4, start mean 0, variance 100
 t   reading  pred.var    gain     mean   variance
 1     2.50   101.000  0.9619   2.4048    3.8476
 2     1.00     4.848  0.5479   1.6351    2.1916
 3     3.50     3.192  0.4438   2.4627    1.7752
 4     2.00     2.775  0.4096   2.2732    1.6384
 5     2.80     2.638  0.3974   2.4826    1.5898
steady-state variance (-q + sqrt(q^2 + 4qr)) / 2 = 1.5616, gain 0.3904
variance after 30 steps from the filter itself: 1.5616

Part 2. tracking position and velocity, reading noise sd 5 m
 step  true pos  reading  estimate  true vel  est. vel  sd(pos)
    1      1.95    -2.62     -2.18     1.959    -0.436    4.564
    2      3.81    -3.02     -2.88     1.822    -0.570    4.083
    3      5.62    11.42      6.17     1.776     3.806    4.022
    6     11.01    15.91     12.05     1.790     2.748    3.484
   11     20.64    25.98     21.08     1.935     2.215    2.794
   21     39.31    28.75     35.17     2.209     1.563    2.235
   41     90.74    95.85     90.66     2.949     2.606    2.130
   60    152.69   153.81    150.75     2.928     3.346    2.129
RMS position error, steps 11-60: readings 5.794 m, filter 2.916 m
final gain K = [0.1813 0.0181]
```

Check step 1 by hand: the predicted variance is $100 + 1 = 101$, the gain $101/105 = 0.9619$, the mean
$0 + 0.9619 \cdot 2.5 = 2.4048$, the variance $(1 - 0.9619) \cdot 101 = 3.8476$. The vague start makes the first
reading count almost fully. By step 5 the gain has fallen to 0.397, and after 30 steps the variance equals the formula's
1.5616 to four decimals.

In Part 2 the filter starts knowing nothing about the velocity. After three readings it has a rough idea (3.8 m per
step, true 1.8), and it keeps refining. Its position error over steps 11 to 60 is about half that of the raw readings
(2.9 m against 5.8 m), and the filter's own claimed standard deviation (2.13 m at the end) is in the right range; when a
filter's claimed uncertainty matches its real errors we say it is **consistent**, which is the first thing to check in
practice. The velocity estimate still wanders (3.35 against a true 2.93 at the end) because velocity is only seen
through differences of noisy positions.

### Beyond linear: extended and unscented filters

Most real systems are not linear: a rover turning in a plane has $x_{t+1} = x_t + v \cos\theta_t\,\Delta t$, and a radar
measures range $\sqrt{x^2 + y^2}$. The **extended Kalman filter** (EKF) linearises the models around the current mean
using their Jacobians (matrices of partial derivatives) and then applies the matrix filter. It works well when the
models are nearly linear over the width of the belief, and fails badly when they are not, for example when the belief
should split into two separate possibilities. The **unscented Kalman filter** (Julier and Uhlmann, 1997) pushes a small
set of carefully chosen points through the true nonlinear model and fits a Gaussian to the results, which is often more
accurate at similar cost. When the belief is far from one Gaussian, we need the particle filter of the next section.

### History

Rudolf Kálmán published the filter in 1960 ("A New Approach to Linear Filtering and Prediction Problems", *Journal of
Basic Engineering*); Kálmán and Richard Bucy gave the continuous-time version in 1961. Peter Swerling and Ruslan
Stratonovich had related results. Stanley Schmidt's group at NASA Ames Research Center, studying navigation for the
Apollo missions, developed the extended form for nonlinear trajectories, and a Kalman filter was used in Apollo's onboard
navigation; McGee and Schmidt's 1985 NASA technical memorandum tells this story. Kalman filters have since become
standard in aircraft, spacecraft and phone navigation, where they fuse inertial sensors, satellite positioning and
cameras.

On Mars the same need is sharp. A one-way radio signal takes about 3 to 22 minutes ([Chapter
2](02-Intelligent-Agents.md#26-autonomy-with-long-delays-why-a-mars-rover-must-decide-for-itself)),
so a rover must keep track of where it is by itself. The Mars Exploration Rovers estimated their motion from wheel
odometry and inertial sensors, and corrected wheel slip with **visual odometry**, tracking features between stereo image
pairs (Maimone, Cheng and Matthies, 2007). Estimators of this kind, which combine predictions with noisy measurements
step by step, are the subject of this section.

## 13.5 Particle filters and robot localization

*Level: intermediate.*

A robot is placed somewhere in a long circular corridor. It knows the map: three doors at 10 m, 30 m and 70 m, along a
100 m loop. It does not know where it is. It drives forward about 2 m per step (its wheels slip, so the true move has a
standard deviation of 0.5 m), and it has a door detector that says "door" 90 percent of the time when it is next to a
door and 10 percent of the time when it is not. Where is it?

The belief here cannot be a Gaussian. At the start it is uniform over the whole loop. After the robot sees its first
door, the belief has three bumps, one in front of each door. A Kalman filter, which can hold only one bump, cannot
represent this. We could cut the corridor into 1000 cells and run the exact discrete filter of 13.2 (a **grid filter**
or histogram filter), and for one dimension that is fine. But a robot in a building has position $x, y$ and heading
$\theta$; a grid of 1000 values per dimension has $10^9$ cells, and a drone adds three more dimensions. We need a
representation that puts its effort where the probability is.

### Representing a belief by samples

A **particle filter** represents the belief by $N$ samples, called **particles**, $x^{(1)}, \dots, x^{(N)}$. Where there
are many particles, the belief is high. One step of the basic algorithm (the **bootstrap filter**, or **sampling
importance resampling**):

1. **Propagate:** for each particle, sample its next state from the transition model,
   $x^{(i)} \sim P(X_{t+1} \mid x^{(i)})$.
2. **Weight:** give each particle the weight $w^{(i)} = P(e_{t+1} \mid x^{(i)})$, the likelihood of the evidence there.
3. **Resample:** draw $N$ new particles from the old ones, each chosen with probability proportional to its weight.
   Heavy particles are copied several times; light ones disappear.

That is all. It is the predict-update recursion of 13.2 done by sampling: step 1 is the prediction and step 2 is the
update. Compare it with likelihood weighting from [Chapter 12](12-Probabilistic-Reasoning.md): steps 1 and 2 are
likelihood weighting applied to one time slice. Step 3 is the new idea. Without it the weights of a few particles grow
while the rest shrink towards zero, and after a few dozen steps nearly all the computation is spent on particles in
places that the evidence ruled out long ago.

### Why it works

Assume the particles at time $t$ are a fair sample from the filtered belief: the number of particles in a state $x_t$ is
approximately $N \cdot P(x_t \mid e_{1:t})$. (For a continuous state read "in a small region" instead of "in a state".)

- After propagation, the expected number in state $x_{t+1}$ is
  $\sum_{x_t} P(x_{t+1} \mid x_t)\, N\, P(x_t \mid e_{1:t}) = N\, P(x_{t+1} \mid e_{1:t})$, the prediction.
- Weighting multiplies by $P(e_{t+1} \mid x_{t+1})$, so the total weight in $x_{t+1}$ is proportional to
  $P(e_{t+1} \mid x_{t+1}) P(x_{t+1} \mid e_{1:t})$, which is proportional to $P(x_{t+1} \mid e_{1:t+1})$, the filtered
  belief.
- Resampling picks each particle with probability proportional to its weight, so the expected number of new particles
  in $x_{t+1}$ is $N$ times the normalised weight there, that is $N \cdot P(x_{t+1} \mid e_{1:t+1})$.

So if the particles are a fair sample at time $t$, they are one at time $t + 1$, in expectation. A precise statement
needs more care, because the errors at each step feed into the next; the theorem (see Doucet, de Freitas and Gordon,
2001, or Del Moral's 2004 book) is that, under mild conditions, the particle estimate of any expected value converges to
the true one as $N \to \infty$, with error of order $1/\sqrt{N}$ at each fixed time.

**Effective sample size.** If the weights are very unequal, most particles contribute little. A standard measure is

$$
N_{\text{eff}} = \frac{1}{\sum_i \bar w_i^{\,2}},
$$

where $\bar w_i$ are the weights normalised to sum to 1. It is $N$ when all weights are equal and 1 when one particle
carries all the weight. Many filters resample only when $N_{\text{eff}}$ drops below, say, $N/2$, because resampling
itself adds noise.

**Systematic resampling.** Drawing $N$ independent samples from the weights is wasteful: by chance, a particle with
weight exactly $1/N$ may get zero copies or three. **Systematic resampling** draws one random number $u \in [0, 1)$ and
uses the $N$ evenly spaced points $(u + i)/N$, $i = 0, \dots, N-1$, against the cumulative weights. Each particle then
gets either $\lfloor N \bar w_i \rfloor$ or $\lceil N \bar w_i \rceil$ copies, the expected count is still $N \bar w_i$,
and the extra noise is much smaller. The code below uses it: `np.searchsorted` finds where each point falls in the
cumulative sum, in $O(N \log N)$ total.

### Monte Carlo localization in code

This application has a name: **Monte Carlo localization** (MCL), introduced for mobile robots by Frank Dellaert, Dieter
Fox, Wolfram Burgard and Sebastian Thrun in 1999. The same algorithm had appeared in signal processing as the bootstrap
filter of Neil Gordon, David Salmond and Adrian Smith (1993). The program localizes the corridor robot with 1000
particles and, to see how good the approximation is, runs the exact grid filter with 1000 cells of 10 cm alongside it.

```python
--8<-- "books/ai/ch13_particle.py"
```

```
step  true x  says door  particles within 3 m  grid mass within 3 m  effective N  tenths per 10 m bin
   1   54.03        no                  0.069                 0.067        905.3  1111111111
   5   61.89        no                  0.093                 0.091        925.8  1010121021
   8   68.47        yes                 0.218                 0.206        361.8  2020012001
  10   73.42        no                  0.368                 0.304        800.9  0303000400
  15   82.83        no                  0.368                 0.302        991.3  0030300040
  20   91.01        no                  0.396                 0.335        979.5  0000040015
  25    0.26        yes                 0.296                 0.247        742.1  5000004001
  30   10.08        yes                 0.434                 0.289        397.6  3200002200
  35   20.79        no                  0.519                 0.431        992.1  0420000310
  40   31.08        yes                 0.958                 0.943        767.3  0027000000
  45   39.72        no                  0.865                 0.874        978.7  0002700000
  50   51.52        no                  0.895                 0.890        989.7  0000370000
```

Follow the story in the last column (the fraction of particles, in tenths, in each 10 m stretch of corridor).

- **Steps 1 to 5:** no doors seen; the belief stays nearly flat (the "no door" readings only thin out the door regions
  a little).
- **Step 8:** the robot passes the door at 70 m and the detector fires. Now the particles crowd in front of all three
  doors: three hypotheses. The effective sample size drops to 362, because only particles near doors had high weight.
- **Steps 10 to 20:** the three clumps drive forward together. Nothing distinguishes them yet.
- **Step 25 to 30:** the robot passes the door at 10 m. A clump that thought it was 40 m behind passes a door too.
  Distances between doors are 20 m (10 to 30), 40 m (30 to 70) and 40 m (70 to 10), so "a door, then a door 40 m
  later" fits two of the hypotheses. Two clumps survive.
- **Step 40:** the robot passes the door at 30 m, only 20 m after the last one. Only one hypothesis predicted that:
  96 percent of the particles are now within 3 m of the truth.

The particle filter's numbers track the exact grid filter's closely (0.958 against 0.943 at step 40; differences come
from sampling noise in both directions). The particle filter achieves this without ever representing the empty parts of
the corridor.

<figure class="mars-fig" markdown="0">
<svg viewBox="0 0 640 342" role="img" aria-label="Particle histograms at steps 8, 30 and 40 of the corridor run. At step 8 there are three peaks, in front of each door. At step 30 there are two clusters. At step 40 a single peak sits at the true position near the door at 30 metres.">
<text x="10" y="65" font-size="13" fill="currentColor">step 8</text>
<rect x="112.4" y="25" width="21.2" height="70" fill="#9cc9ea" fill-opacity="0.35"/>
<rect x="218.4" y="25" width="21.2" height="70" fill="#9cc9ea" fill-opacity="0.35"/>
<rect x="430.4" y="25" width="21.2" height="70" fill="#9cc9ea" fill-opacity="0.35"/>
<rect x="70.8" y="89.2" width="9.0" height="5.8" fill="#eea66f"/>
<rect x="81.4" y="89.2" width="9.0" height="5.8" fill="#eea66f"/>
<rect x="92.0" y="89.2" width="9.0" height="5.8" fill="#eea66f"/>
<rect x="102.6" y="90.6" width="9.0" height="4.4" fill="#eea66f"/>
<rect x="113.2" y="47.5" width="9.0" height="47.5" fill="#eea66f"/>
<rect x="123.8" y="80.9" width="9.0" height="14.1" fill="#eea66f"/>
<rect x="176.8" y="94.0" width="9.0" height="1.0" fill="#eea66f"/>
<rect x="187.4" y="94.0" width="9.0" height="1.0" fill="#eea66f"/>
<rect x="198.0" y="92.8" width="9.0" height="2.2" fill="#eea66f"/>
<rect x="208.6" y="86.3" width="9.0" height="8.7" fill="#eea66f"/>
<rect x="219.2" y="47.1" width="9.0" height="47.9" fill="#eea66f"/>
<rect x="229.8" y="81.6" width="9.0" height="13.4" fill="#eea66f"/>
<rect x="272.2" y="94.0" width="9.0" height="1.0" fill="#eea66f"/>
<rect x="282.8" y="94.0" width="9.0" height="1.0" fill="#eea66f"/>
<rect x="293.4" y="94.0" width="9.0" height="1.0" fill="#eea66f"/>
<rect x="304.0" y="93.2" width="9.0" height="1.8" fill="#eea66f"/>
<rect x="314.6" y="90.3" width="9.0" height="4.7" fill="#eea66f"/>
<rect x="325.2" y="90.3" width="9.0" height="4.7" fill="#eea66f"/>
<rect x="335.8" y="88.5" width="9.0" height="6.5" fill="#eea66f"/>
<rect x="346.4" y="88.1" width="9.0" height="6.9" fill="#eea66f"/>
<rect x="357.0" y="85.6" width="9.0" height="9.4" fill="#eea66f"/>
<rect x="367.6" y="87.0" width="9.0" height="8.0" fill="#eea66f"/>
<rect x="378.2" y="89.2" width="9.0" height="5.8" fill="#eea66f"/>
<rect x="388.8" y="90.3" width="9.0" height="4.7" fill="#eea66f"/>
<rect x="399.4" y="87.7" width="9.0" height="7.3" fill="#eea66f"/>
<rect x="410.0" y="85.2" width="9.0" height="9.8" fill="#eea66f"/>
<rect x="420.6" y="88.1" width="9.0" height="6.9" fill="#eea66f"/>
<rect x="431.2" y="33.0" width="9.0" height="62.0" fill="#eea66f"/>
<rect x="441.8" y="82.7" width="9.0" height="12.3" fill="#eea66f"/>
<rect x="484.2" y="94.0" width="9.0" height="1.0" fill="#eea66f"/>
<rect x="505.4" y="94.0" width="9.0" height="1.0" fill="#eea66f"/>
<rect x="516.0" y="92.5" width="9.0" height="2.5" fill="#eea66f"/>
<rect x="526.6" y="88.8" width="9.0" height="6.2" fill="#eea66f"/>
<rect x="537.2" y="87.4" width="9.0" height="7.6" fill="#eea66f"/>
<rect x="547.8" y="88.5" width="9.0" height="6.5" fill="#eea66f"/>
<rect x="558.4" y="86.7" width="9.0" height="8.3" fill="#eea66f"/>
<rect x="569.0" y="89.2" width="9.0" height="5.8" fill="#eea66f"/>
<rect x="579.6" y="85.6" width="9.0" height="9.4" fill="#eea66f"/>
<rect x="590.2" y="88.8" width="9.0" height="6.2" fill="#eea66f"/>
<line x1="70.0" y1="95" x2="600.0" y2="95" stroke="currentColor" stroke-width="1"/>
<polygon points="433.1,97 427.1,107 439.1,107" fill="#7ccf9a" stroke="currentColor" stroke-width="0.8"/>
<text x="10" y="160" font-size="13" fill="currentColor">step 30</text>
<rect x="112.4" y="120" width="21.2" height="70" fill="#9cc9ea" fill-opacity="0.35"/>
<rect x="218.4" y="120" width="21.2" height="70" fill="#9cc9ea" fill-opacity="0.35"/>
<rect x="430.4" y="120" width="21.2" height="70" fill="#9cc9ea" fill-opacity="0.35"/>
<rect x="81.4" y="188.9" width="9.0" height="1.1" fill="#eea66f"/>
<rect x="92.0" y="188.9" width="9.0" height="1.1" fill="#eea66f"/>
<rect x="102.6" y="185.1" width="9.0" height="4.9" fill="#eea66f"/>
<rect x="113.2" y="128.0" width="9.0" height="62.0" fill="#eea66f"/>
<rect x="123.8" y="160.6" width="9.0" height="29.4" fill="#eea66f"/>
<rect x="145.0" y="188.3" width="9.0" height="1.7" fill="#eea66f"/>
<rect x="155.6" y="182.7" width="9.0" height="7.3" fill="#eea66f"/>
<rect x="166.2" y="177.3" width="9.0" height="12.7" fill="#eea66f"/>
<rect x="176.8" y="188.3" width="9.0" height="1.7" fill="#eea66f"/>
<rect x="293.4" y="189.0" width="9.0" height="1.0" fill="#eea66f"/>
<rect x="304.0" y="188.9" width="9.0" height="1.1" fill="#eea66f"/>
<rect x="335.8" y="189.0" width="9.0" height="1.0" fill="#eea66f"/>
<rect x="346.4" y="189.0" width="9.0" height="1.0" fill="#eea66f"/>
<rect x="357.0" y="189.0" width="9.0" height="1.0" fill="#eea66f"/>
<rect x="367.6" y="189.0" width="9.0" height="1.0" fill="#eea66f"/>
<rect x="420.6" y="189.0" width="9.0" height="1.0" fill="#eea66f"/>
<rect x="431.2" y="147.1" width="9.0" height="42.9" fill="#eea66f"/>
<rect x="441.8" y="176.3" width="9.0" height="13.7" fill="#eea66f"/>
<rect x="452.4" y="189.0" width="9.0" height="1.0" fill="#eea66f"/>
<rect x="463.0" y="189.0" width="9.0" height="1.0" fill="#eea66f"/>
<rect x="473.6" y="180.3" width="9.0" height="9.7" fill="#eea66f"/>
<rect x="484.2" y="171.8" width="9.0" height="18.2" fill="#eea66f"/>
<rect x="494.8" y="186.6" width="9.0" height="3.4" fill="#eea66f"/>
<line x1="70.0" y1="190" x2="600.0" y2="190" stroke="currentColor" stroke-width="1"/>
<polygon points="123.5,192 117.5,202 129.5,202" fill="#7ccf9a" stroke="currentColor" stroke-width="0.8"/>
<text x="10" y="255" font-size="13" fill="currentColor">step 40</text>
<rect x="112.4" y="215" width="21.2" height="70" fill="#9cc9ea" fill-opacity="0.35"/>
<rect x="218.4" y="215" width="21.2" height="70" fill="#9cc9ea" fill-opacity="0.35"/>
<rect x="430.4" y="215" width="21.2" height="70" fill="#9cc9ea" fill-opacity="0.35"/>
<rect x="70.8" y="284.0" width="9.0" height="1.0" fill="#eea66f"/>
<rect x="208.6" y="284.0" width="9.0" height="1.0" fill="#eea66f"/>
<rect x="219.2" y="263.5" width="9.0" height="21.5" fill="#eea66f"/>
<rect x="229.8" y="223.0" width="9.0" height="62.0" fill="#eea66f"/>
<rect x="240.4" y="283.9" width="9.0" height="1.1" fill="#eea66f"/>
<rect x="251.0" y="284.0" width="9.0" height="1.0" fill="#eea66f"/>
<rect x="441.8" y="284.0" width="9.0" height="1.0" fill="#eea66f"/>
<rect x="516.0" y="284.0" width="9.0" height="1.0" fill="#eea66f"/>
<rect x="526.6" y="284.0" width="9.0" height="1.0" fill="#eea66f"/>
<rect x="537.2" y="283.8" width="9.0" height="1.2" fill="#eea66f"/>
<rect x="547.8" y="284.0" width="9.0" height="1.0" fill="#eea66f"/>
<rect x="590.2" y="284.0" width="9.0" height="1.0" fill="#eea66f"/>
<line x1="70.0" y1="285" x2="600.0" y2="285" stroke="currentColor" stroke-width="1"/>
<polygon points="234.8,287 228.8,297 240.8,297" fill="#7ccf9a" stroke="currentColor" stroke-width="0.8"/>
<text x="70.0" y="315" font-size="12" text-anchor="middle" fill="currentColor">0</text>
<text x="123.0" y="315" font-size="12" text-anchor="middle" fill="currentColor">10</text>
<text x="176.0" y="315" font-size="12" text-anchor="middle" fill="currentColor">20</text>
<text x="229.0" y="315" font-size="12" text-anchor="middle" fill="currentColor">30</text>
<text x="282.0" y="315" font-size="12" text-anchor="middle" fill="currentColor">40</text>
<text x="335.0" y="315" font-size="12" text-anchor="middle" fill="currentColor">50</text>
<text x="388.0" y="315" font-size="12" text-anchor="middle" fill="currentColor">60</text>
<text x="441.0" y="315" font-size="12" text-anchor="middle" fill="currentColor">70</text>
<text x="494.0" y="315" font-size="12" text-anchor="middle" fill="currentColor">80</text>
<text x="547.0" y="315" font-size="12" text-anchor="middle" fill="currentColor">90</text>
<text x="600.0" y="315" font-size="12" text-anchor="middle" fill="currentColor">100</text>
<text x="335" y="333" font-size="12" text-anchor="middle" fill="currentColor">position along the corridor (m)</text>
</svg>
<figcaption>Particles in 2 m bins (each row scaled to its own tallest bar) at three moments of the run above. Blue bands
are doors; the green triangle is the robot's true position. The belief goes from three hypotheses (step 8) to two
(step 30) to one (step 40).</figcaption>
</figure>

### What can go wrong

- **Particle deprivation.** If no particle is near the true state, no amount of weighting will bring one there. This
  happens when $N$ is too small for the state space, when the sensor is very precise (the likelihood is a needle that
  misses every particle) or after the robot is picked up and moved (the **kidnapped robot problem**). A common remedy is
  to inject a few percent of random particles at every step.
- **Dimension.** The number of particles needed grows quickly with the dimension of the state, which is why particle
  filters are used for robot pose (3 to 6 numbers) but not directly for a map with thousands of landmarks. **Rao-
  Blackwellised** particle filters sample only some variables and handle the rest exactly; FastSLAM (Montemerlo, Thrun,
  Koller and Wegbreit, 2002) samples the robot's path and gives each particle its own small Kalman filters for the
  landmarks, the idea behind the SLAM methods of [Chapter 18](18-Perception-and-Robotics.md).

## 13.6 Dynamic Bayesian networks

*Level: advanced.*

An HMM has one state variable; a Kalman filter has one Gaussian state vector. Real systems have many state variables with
structure among them: a robot has a position, a velocity, a battery level and sensors that may break. A **dynamic
Bayesian network** (DBN), introduced by Thomas Dean and Keiji Kanazawa in 1989, is a Bayesian network that describes one
time slice and how it connects to the next. It consists of:

- a prior network over the state variables at time 0, and
- a **two-slice network** giving, for each variable at time $t+1$, its parents among the variables at time $t$ and
  $t+1$, with their conditional probability tables.

Every HMM is a DBN with one discrete state variable; every Kalman filter is a DBN with Gaussian variables and linear
dependencies. Unrolling the two-slice network for $t$ steps gives an ordinary (large) Bayesian network, and every
algorithm of [Chapter 12](12-Probabilistic-Reasoning.md) applies to it.

### Why factor: the counting argument

Take $n$ Boolean state variables, each with at most 2 parents in the previous slice. A DBN needs one conditional table
per variable with $2^2 = 4$ rows: $4n$ numbers. The same model written as an HMM has $2^n$ joint states and a transition
matrix with $2^{2n}$ entries. For $n = 30$ that is about $10^{18}$ numbers, against 120. The program below prints this
comparison. Factoring the state is to the HMM what Bayesian networks are to the full joint table.

### Persistence and sensor failure: an example

A robot has a battery whose level $B_t$ runs from 0 to 5. Each step it stays the same with probability 0.95 or drops by
one with probability 0.05. A battery meter $M_t$ reads the level, or one off, with probabilities 0.8, 0.1, 0.1. Sensors
fail, and how we model failure matters. Two models:

- **Transient failure.** Any single reading is a stray 0 with probability 0.03. The state is $B_t$ alone.
- **Persistent failure.** A Boolean state variable $\text{Broken}_t$ switches on with probability 0.001 per step and,
  once on, stays on; a broken meter always reads 0. The two-slice network has $B_{t+1}$ depending on $B_t$,
  $\text{Broken}_{t+1}$ on $\text{Broken}_t$, and $M_{t+1}$ on both $B_{t+1}$ and $\text{Broken}_{t+1}$.

The meter reads 5 fifteen times and then 0 twelve times. What should the robot believe? The program filters both models
exactly (the persistent model has $6 \times 2 = 12$ joint states, small enough to enumerate).

```python
--8<-- "books/ai/ch13_dbn.py"
```

```
step  reading   transient: P(B=0)   persistent: P(B=0)  P(broken)  E[B]
  13        5              0.0000               0.0000     0.0000  4.99
  14        5              0.0000               0.0000     0.0000  4.99
  15        5              0.0000               0.0000     0.0000  4.99
  16        0              0.0000               0.0000     1.0000  4.94
  17        0              0.0000               0.0000     1.0000  4.89
  18        0              0.0000               0.0000     1.0000  4.84
  19        0              0.0000               0.0000     1.0000  4.79
  20        0              0.0002               0.0000     1.0000  4.74
  24        0              0.9946               0.0000     1.0000  4.54
  27        0              1.0000               0.0002     1.0000  4.39

why factor the state: numbers needed for one transition step
  n Boolean state variables   full transition matrix   DBN with 2 parents per variable
                         5                 1.02e+03                                20
                        10                 1.05e+06                                40
                        20                  1.1e+12                                80
                        30                 1.15e+18                               120
```

The persistent model concludes at once that the meter has broken: a working meter cannot read 0 when the battery is at
4 or 5, and the battery cannot fall from 5 to 0 in one step, so "broken" is the only explanation left, however unlikely
a priori. Its expected battery level then declines slowly, at the rate the transition model predicts, because the meter
no longer tells it anything. The transient model has no such explanation. At first it treats each 0 as a stray reading,
but each step it also lets the battery drain a little in its belief; once the zeros have persisted long enough for the
battery to have plausibly drained (by step 24), it is more than 99 percent sure that the battery is empty. The right answer depends
on which failure model is true of the hardware, which is the point: the structure of a DBN is where an engineer's
knowledge goes.

### Exact inference and its limit

Can we filter a DBN without enumerating joint states? We can eliminate variables in the unrolled network ([Chapter 12](12-Probabilistic-Reasoning.md)),
keeping only the current slice, which gives a constant-time-per-step algorithm. But the forward message, the belief over
the current slice's state variables, is in general a full joint distribution over all of them. Even if the variables
start independent, after a few steps every pair is connected through the past, and the message needs $O(2^n)$ numbers.
The factored model does not, in general, give a factored belief. (Murphy's 2002 thesis states this precisely and
analyses the cost.)

So large DBNs are filtered approximately.

- **Particle filters** work on DBNs directly: sample each variable of the new slice from its conditional table given
  sampled parents, weight by the evidence variables. This is how the corridor robot of 13.5 would be extended with a
  battery and a broken-sensor variable.
- **Factored approximations** (Boyen and Koller, 1998) project the belief after each step onto a product of smaller
  distributions and showed that, for processes that mix, the error stays bounded over time instead of accumulating.

### Where DBNs are used

DBNs and their special cases are used for speech recognition (HMMs), robot localization and mapping, tracking in video,
monitoring of patients and machines, and fault diagnosis on spacecraft. Learning a DBN's tables from data uses EM, as
for HMMs. In modern machine learning, recurrent neural networks ([Machine learning, Chapter 18](../machine-learning/18-Sequence-Models.md))
play a similar role, with a learned continuous state in place of a designed one; they predict well but do not give the
explicit, inspectable probabilities that a DBN gives.

## In practice

- Filtering is everywhere a system has a state it cannot see: navigation, tracking, process control, speech, finance.
  Start with the simplest model that captures the dynamics (often a constant-velocity Kalman filter) and test whether
  its claimed uncertainty matches its real errors.
- Libraries do this for real: `hmmlearn` for HMMs, `filterpy` for Kalman and particle filters, and state-space models
  in `statsmodels`. Robotics frameworks ship localization packages based on MCL.
- Work in log space or normalise at every step; a product of a thousand probabilities underflows any floating-point
  number.

## Check yourself

??? question "1. A process is second-order Markov: P(X_t | X_{0:t-1}) = P(X_t | X_{t-1}, X_{t-2}), with X taking S values. Show how to turn it into a first-order Markov process. How many states does it have, and how many entries of its transition matrix can be non-zero?"
    Define the new state $Y_t = (X_{t-1}, X_t)$. Then $Y_{t+1} = (X_t, X_{t+1})$, and
    $P(Y_{t+1} \mid Y_t, Y_{t-1}, \dots) = P(X_{t+1} \mid X_t, X_{t-1})$ if the first component of $Y_{t+1}$ equals the
    second of $Y_t$, and 0 otherwise. This depends only on $Y_t$, so $Y$ is first-order Markov. It has $S^2$ states.
    Its transition matrix is $S^2 \times S^2 = S^4$ entries, but from a state $(a, b)$ only the $S$ states $(b, c)$ can
    follow, so only $S^2 \cdot S = S^3$ entries are non-zero: exactly the number of entries in the second-order table.

??? question "2. In the umbrella world, compute the filtered probability of rain on day 1 if the director arrives without an umbrella. Then compute day 2 if she again has no umbrella."
    Day 1 prediction $\langle 0.5, 0.5 \rangle$. Likelihoods of "no umbrella": $\langle 0.1, 0.8 \rangle$. Product
    $\langle 0.05, 0.40 \rangle$, normalised $\langle 0.111, 0.889 \rangle$.
    Day 2 prediction: $0.7 \cdot 0.111 + 0.3 \cdot 0.889 = 0.344$. Update: $\langle 0.1 \cdot 0.344,\ 0.8 \cdot 0.656 \rangle
    = \langle 0.0344, 0.5248 \rangle$, normalised $\langle 0.0615, 0.9385 \rangle$. Two dry days in a row make rain
    unlikely: 6 percent.

??? question "3. A two-state chain stays in state 1 with probability 1 - a and in state 2 with probability 1 - b. Find its stationary distribution, and prove that the prediction P(state 1 after k steps) approaches it as (1 - a - b)^k. Check against the program's prediction for day 6."
    Stationarity: $\pi_1 = \pi_1 (1 - a) + (1 - \pi_1) b$, so $\pi_1 (a + b) = b$ and $\pi_1 = b / (a + b)$.
    With $p_k$ the probability of state 1 after $k$ steps, $p_{k+1} = (1-a) p_k + b (1 - p_k) = b + (1 - a - b) p_k$.
    Subtract $\pi_1 = b + (1 - a - b)\pi_1$: $p_{k+1} - \pi_1 = (1 - a - b)(p_k - \pi_1)$, so
    $p_k - \pi_1 = (1-a-b)^k (p_0 - \pi_1)$. For the umbrella chain $a = b = 0.3$: $\pi_1 = 0.5$ and the factor is 0.4.
    From the day-5 filtered value 0.8673, day 6 is $0.5 + 0.4 \cdot 0.3673 = 0.6469$, as printed.

??? question "4. Prove that choosing, for each day k, the state with the largest smoothed probability P(x_k | e_{1:t}) maximises the expected number of days whose state is guessed correctly. Why can the Viterbi path do worse on this measure?"
    For any guess $g_1, \dots, g_t$, the number of correct days is $\sum_k \mathbf{1}[X_k = g_k]$. Its expectation given
    the evidence is, by linearity, $\sum_k P(X_k = g_k \mid e_{1:t})$. Each term depends on one $g_k$ only, so the sum is
    maximised by maximising each term separately: $g_k = \arg\max_x P(X_k = x \mid e_{1:t})$. The Viterbi path maximises
    a different quantity, $P(X_{1:t} = g_{1:t} \mid e_{1:t})$, the chance that **every** day is right. A path can be the
    single most likely one and still contain days where its state is not the individually most likely, so it can score
    lower on the expected count, as in the program's second world (76.2 against 79.2 percent).

??? question "5. Write the code: a forward algorithm that multiplies unnormalised messages over 2000 days of the umbrella world, and show where it underflows. Then fix it with logarithms and the log-sum-exp trick, and check against the normalised version."
    ```python
    import numpy as np
    T = np.array([[0.7, 0.3], [0.3, 0.7]]); O = np.array([[0.9, 0.1], [0.2, 0.8]])
    ev = np.random.default_rng(0).integers(0, 2, 2000)

    f = np.array([0.5, 0.5])
    for t, e in enumerate(ev):
        f = O[:, e] * (f @ T)
        if f.sum() == 0:
            print("underflow at day", t + 1); break

    def logsumexp(a, axis=0):
        m = a.max(axis=axis)
        return m + np.log(np.exp(a - np.expand_dims(m, axis)).sum(axis=axis))

    lf = np.log([0.5, 0.5])
    for e in ev:
        lf = np.log(O[:, e]) + logsumexp(lf[:, None] + np.log(T), axis=0)
    print("log P(e) with logs:", logsumexp(lf))

    f, ll = np.array([0.5, 0.5]), 0.0
    for e in ev:
        g = O[:, e] * (f @ T); ll += np.log(g.sum()); f = g / g.sum()
    print("log P(e) normalised:", ll)
    ```
    It prints `underflow at day 1040`, then the same log-likelihood twice, about `-1436.8466`. Each day multiplies the
    message by a number around 0.5 or less, and a double underflows to 0 below about $10^{-308}$ (about
    $2^{-1074}$ for the smallest subnormal), so the plain product dies after roughly a thousand steps. The log-sum-exp
    trick subtracts the largest term before exponentiating, so nothing overflows or underflows.

??? question "6. In the 1-D Kalman filter with no process noise (q = 0) and a very vague start (variance tending to infinity), show that after n readings the mean is the average of the readings and the variance is r/n."
    With $q = 0$ the prediction does nothing, and the update adds precisions: after $n$ readings the precision is
    $1/\sigma_0^2 + n/r \to n/r$, so the variance is $r/n$. The mean is the precision-weighted average of the prior mean
    and the readings; with the prior's precision tending to 0, every reading has the same weight $1/r$, so the mean is
    $(z_1 + \dots + z_n)/n$. A static quantity measured repeatedly is best estimated by the average, and the Kalman
    filter computes that average one reading at a time.

??? question "7. For a 1-D random walk with q = 0.5 and r = 2, compute the steady-state variance and gain. What happens to the steady-state gain as q/r tends to 0 and to infinity?"
    $P_\infty = (-0.5 + \sqrt{0.25 + 4 \cdot 0.5 \cdot 2})/2 = (-0.5 + \sqrt{4.25})/2 = (-0.5 + 2.0616)/2 = 0.7808$.
    Predicted variance $0.7808 + 0.5 = 1.2808$, gain $1.2808/(1.2808 + 2) = 0.3904$. (The same gain as for $q = 1$,
    $r = 4$: the gain depends only on the ratio $q/r$.) As $q/r \to 0$ the world barely moves, $P_\infty \to 0$ and the
    gain tends to 0: trust the accumulated past. As $q/r \to \infty$, $P_\infty \to r$ and the gain tends to 1: the past
    tells you nothing, so use the latest reading.

??? question "8. After weighting, four particles have normalised weights 0.5, 0.25, 0.25 and 0. What is the effective sample size? With systematic resampling and u = 0.3, which particles are copied?"
    $N_{\text{eff}} = 1/(0.25 + 0.0625 + 0.0625 + 0) = 1/0.375 = 2.67$. The cumulative weights are 0.5, 0.75, 1.0, 1.0.
    The points are $(0.3 + i)/4$ = 0.075, 0.325, 0.575, 0.825. The first two fall below 0.5 (particle 1), the third
    between 0.5 and 0.75 (particle 2), the fourth between 0.75 and 1.0 (particle 3). So particle 1 is copied twice,
    particles 2 and 3 once each, and particle 4 vanishes: exactly $4 \bar w_i$ copies each.

??? question "9. Write the code: the 'occasionally dishonest casino' (Durbin et al. 1998). A casino uses a fair die and a loaded die that shows 6 half the time (the other faces 0.1 each). It switches from fair to loaded with probability 0.05 per roll and back with probability 0.1. Use Viterbi to label each roll of 3152432514366646666261656663451243523 as fair or loaded."
    ```python
    import numpy as np
    T = np.log(np.array([[0.95, 0.05], [0.10, 0.90]]))          # 0 = fair, 1 = loaded
    O = np.log(np.array([[1 / 6] * 6, [0.1] * 5 + [0.5]]))
    rolls = [int(c) - 1 for c in "3152432514366646666261656663451243523"]

    m = np.log([0.5, 0.5]) + O[:, rolls[0]]
    back = []
    for r in rolls[1:]:
        cand = m[:, None] + T
        back.append(cand.argmax(axis=0))
        m = cand.max(axis=0) + O[:, r]
    path = [int(m.argmax())]
    for bp in reversed(back):
        path.append(int(bp[path[-1]]))
    path.reverse()
    print("rolls :", "".join(str(r + 1) for r in rolls))
    print("guess :", "".join("FL"[s] for s in path))
    ```
    Output:
    ```
    rolls : 3152432514366646666261656663451243523
    guess : FFFFFFFFFFFLLLLLLLLLLLLLLLLFFFFFFFFFF
    ```
    The stretch rich in sixes (from the twelfth roll, `66646666261656663`) is labelled loaded. Notice that the isolated
    2s and 1 inside it do not break the stretch: switching costs probability (0.05 and 0.1), so the best path stays
    loaded through a few ordinary rolls.

??? question "10. Derive the backward recursion's starting value and explain why the smoothed estimate for the last time step always equals the filtered one."
    $b_{t+1:t} = P(e_{t+1:t} \mid X_t)$ is the probability of an empty set of observations, which is 1 for every state;
    so the starting message is the all-ones vector. The smoothed estimate for $k = t$ is $\alpha f_{1:t} \times \mathbf{1}
    = f_{1:t}$, the filtered estimate. This is just the statement that there is no evidence after time $t$ to add.

??? question "11. In the persistent-failure DBN, why does P(broken) jump to 1 at the first zero reading, even though the prior chance of breaking is only 0.001? What would change if the battery could also fail suddenly (drop to 0 with probability 0.001 per step)?"
    Before the zero, the battery is almost surely at 5 (or 4). A working meter reads at most one off, so it cannot read
    0 from those levels: $P(M = 0 \mid B \ge 2, \lnot\text{broken}) = 0$. The only states with non-zero likelihood
    are those with the meter broken, so after normalisation they carry all the probability, whatever the prior. If the
    battery could also fail suddenly, a second explanation would have non-zero likelihood: battery at 0, meter working
    and reading 0 (probability 0.9: it reads 0 exactly with 0.8, or "one below", clipped to 0, with 0.1). Its prior
    (0.001) is the same as breaking, but its likelihood is 0.9 against 1.0, so the posterior would split roughly
    0.9 : 1 between "battery died" and "meter broke", about 47 and 53 percent. As
    more zeros arrive both explanations keep fitting, so the robot could not tell them apart without another sensor,
    which is the honest answer.

??? question "12. Prove that the 1-D Kalman update is the best linear combination: among all estimates of the form a·(prediction) + (1 - a)·(reading), with independent errors of variances s² and r, the one with the smallest error variance uses a = r/(s² + r)."
    The error of $a\bar\mu + (1 - a) z$ is $a\epsilon_1 + (1-a)\epsilon_2$ with independent errors of variances $s^2$
    and $r$. Its variance is $V(a) = a^2 s^2 + (1-a)^2 r$. Then $V'(a) = 2 a s^2 - 2(1 - a) r = 0$ gives
    $a = r/(s^2 + r)$, a minimum since $V'' = 2(s^2 + r) > 0$. The weight on the reading is
    $1 - a = s^2/(s^2 + r) = K$, the Kalman gain, and $V = s^2 r/(s^2 + r)$, the Kalman variance. So even without
    assuming Gaussian noise, the Kalman update is the minimum-variance linear unbiased estimate; with Gaussian noise it
    is also the exact posterior.

## What you learned

- A changing world is modelled by a prior, a transition model and a sensor model; the Markov and stationarity
  assumptions make three small tables describe all of time, and enlarging the state makes the assumptions hold better.
- Filtering, prediction, smoothing and the most likely sequence are all computed by recursions over the chain, in time
  linear in the sequence length: predict and update forwards, a backward message for hindsight, max instead of sum for
  Viterbi.
- Hindsight helps: smoothing maximises the expected number of correct states; Viterbi maximises the chance of the whole
  sequence; prediction forgets the evidence at the mixing rate of the chain.
- For linear-Gaussian models the belief stays Gaussian and the Kalman filter is exact: precisions add, the mean is a
  precision-weighted average, and the gain balances process noise against sensor noise.
- Particle filters represent any belief by weighted samples; propagate, weight and resample is the filtering recursion
  done by sampling, and it localised a robot through a three-way ambiguity that no single Gaussian could hold.
- Dynamic Bayesian networks factor the state into variables, exponentially shrinking the model; exact filtering still
  needs a joint belief, so large DBNs are filtered with particles or factored approximations.

**Next:** [Chapter 14](14-Making-Decisions.md) turns beliefs into actions: utilities, decision networks and Markov
decision processes.

## Further reading

- S. Russell and P. Norvig, *Artificial Intelligence: A Modern Approach*, 4th ed., 2020: chapter 14 (probabilistic
  reasoning over time), the source of the umbrella and battery examples.
- L. R. Rabiner, "A tutorial on hidden Markov models and selected applications in speech recognition", *Proceedings of
  the IEEE* 77, 1989.
- L. E. Baum, T. Petrie, G. Soules and N. Weiss, "A maximization technique occurring in the statistical analysis of
  probabilistic functions of Markov chains", *Annals of Mathematical Statistics* 41, 1970.
- A. J. Viterbi, "Error bounds for convolutional codes and an asymptotically optimum decoding algorithm", *IEEE
  Transactions on Information Theory* 13, 1967; G. D. Forney, "The Viterbi algorithm", *Proceedings of the IEEE* 61,
  1973.
- R. E. Kalman, "A new approach to linear filtering and prediction problems", *Journal of Basic Engineering* 82, 1960;
  L. A. McGee and S. F. Schmidt, "Discovery of the Kalman filter as a practical tool for aerospace and industry", NASA
  Technical Memorandum 86847, 1985.
- S. J. Julier and J. K. Uhlmann, "A new extension of the Kalman filter to nonlinear systems", SPIE AeroSense, 1997.
- N. J. Gordon, D. J. Salmond and A. F. M. Smith, "Novel approach to nonlinear/non-Gaussian Bayesian state estimation",
  *IEE Proceedings F* 140, 1993.
- F. Dellaert, D. Fox, W. Burgard and S. Thrun, "Monte Carlo localization for mobile robots", IEEE International
  Conference on Robotics and Automation, 1999.
- S. Thrun, W. Burgard and D. Fox, *Probabilistic Robotics*, 2005 (Kalman, particle and grid filters for robots, with
  full derivations).
- A. Doucet, N. de Freitas and N. Gordon (eds.), *Sequential Monte Carlo Methods in Practice*, 2001.
- T. Dean and K. Kanazawa, "A model for reasoning about persistence and causation", *Computational Intelligence* 5, 1989;
  K. P. Murphy, *Dynamic Bayesian Networks: Representation, Inference and Learning*, PhD thesis, UC Berkeley, 2002;
  X. Boyen and D. Koller, "Tractable inference for complex stochastic processes", UAI 1998.
- R. Durbin, S. Eddy, A. Krogh and G. Mitchison, *Biological Sequence Analysis*, 1998 (HMMs in biology; the dishonest
  casino).
- M. Maimone, Y. Cheng and L. Matthies, "Two years of visual odometry on the Mars Exploration Rovers", *Journal of
  Field Robotics* 24, 2007.
- On this site: the Algorithms book's [Chapter 13](../algorithms/13-Dynamic-Programming.md) (dynamic programming, the
  idea behind Viterbi), [Machine learning, Chapter 13](../machine-learning/13-Clustering.md) (EM, behind Baum-Welch) and
  [Chapter 18](../machine-learning/18-Sequence-Models.md) (recurrent networks), and
  [Probability](https://math.akadian.ca/books/probability/) for Markov chains and Gaussians.
