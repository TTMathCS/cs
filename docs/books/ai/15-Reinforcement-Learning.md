# 15. Reinforcement learning

*[Chapter 14](14-Making-Decisions.md) solved Markov decision processes when the agent is handed the transition model and
the rewards. Usually nobody hands them over. A robot does not know in advance how its wheels slip on sand; a game
player does not know how good a position is; a recommender does not know which item a user will like. This chapter
answers the question: how can an agent learn to act well from experience alone, by trying actions and seeing what
rewards follow? You will build bandit algorithms and measure their regret, learn values by Monte Carlo and by
temporal differences, train Q-learning and SARSA agents and see why they behave differently near a cliff, train a small
deep Q-network to balance a pole, derive the policy gradient and use it where only a random policy is optimal, add a
learned model with Dyna, and finally see, in code, how an agent can satisfy the reward it was given while defeating the
purpose it was given for.*

!!! abstract "In this chapter"
    **You will learn:**

    - the reinforcement learning problem, exploration versus exploitation, and regret; epsilon-greedy and UCB1 on
      bandits, with the UCB1 bound stated and its idea proved
    - Monte Carlo and temporal-difference (TD) prediction, and why bootstrapping usually learns faster
    - Q-learning and SARSA: off-policy versus on-policy control, the convergence conditions, and the cliff example
    - function approximation, the "deadly triad", and the ingredients of deep Q-networks, built from scratch
    - the policy gradient theorem, REINFORCE derived, baselines, actor-critic and PPO
    - model-based RL with Dyna, and how AlphaZero and MuZero combine learning and search
    - reward design: specification gaming shown in code, and potential-based shaping proved safe

    **You need:** [Chapter 14](14-Making-Decisions.md) (MDPs, Bellman equations, value and policy iteration). For 15.4 and
    15.5, neural networks and gradients from [Machine learning, Chapter 15](../machine-learning/15-Neural-Networks-and-Backpropagation.md)
    and [Chapter 5](../machine-learning/05-Optimization.md). Monte Carlo tree search from [Chapter
    6](06-Games-and-Adversarial-Search.md) for 15.6.

    **Levels:** 15.1 and 15.2 are beginner to intermediate; 15.3 is intermediate; 15.4 and 15.5 are advanced; 15.6 is
    intermediate; 15.7 is advanced.

## 15.1 Learning from rewards; exploration vs exploitation; multi-armed bandits

A child learning to ride a bicycle is not told the right angle of the handlebars at each moment. It tries, it wobbles,
it falls (a negative reward) or glides (a positive one), and over many attempts it gets better. **Reinforcement
learning** (RL) is learning of this kind: an agent interacts with an environment, receives **rewards**, and must
discover a policy that earns as much reward as possible over time. It differs from the supervised learning of the
[Machine learning](../machine-learning/01-What-Is-Machine-Learning.md) book in three ways.

- **No correct answers are given**, only a number saying how good the outcome was. The agent must find out by itself
  which actions would have been better.
- **Rewards can be delayed.** A move in chess may win or lose the game forty moves later. Which of the forty moves
  deserves the credit? This is the **credit assignment problem**.
- **The agent's actions decide what data it sees.** If it never tries an action, it never learns what that action does.

<figure class="mars-fig" markdown="0">
<svg viewBox="0 0 640 200" role="img" aria-label="The agent-environment loop. The agent box sends an action to the environment box; the environment sends back the next state and a reward.">
<rect x="60" y="60" width="160" height="70" rx="10" fill="#9cc9ea" fill-opacity="0.5" stroke="currentColor" stroke-width="1.4"/>
<text x="140" y="92" font-size="16" text-anchor="middle" fill="currentColor">Agent</text>
<text x="140" y="114" font-size="12" text-anchor="middle" fill="currentColor">policy π(a | s)</text>
<rect x="420" y="60" width="160" height="70" rx="10" fill="#eea66f" fill-opacity="0.5" stroke="currentColor" stroke-width="1.4"/>
<text x="500" y="92" font-size="16" text-anchor="middle" fill="currentColor">Environment</text>
<text x="500" y="114" font-size="12" text-anchor="middle" fill="currentColor">P(s′ | s, a), reward</text>
<path d="M 140 60 C 140 15, 500 15, 500 52" fill="none" stroke="currentColor" stroke-width="1.6"/>
<polygon points="500,58 495,48 505,48" fill="currentColor"/>
<text x="320" y="28" font-size="13" text-anchor="middle" fill="currentColor">action Aₜ</text>
<path d="M 500 130 C 500 185, 140 185, 140 138" fill="none" stroke="currentColor" stroke-width="1.6"/>
<polygon points="140,132 135,142 145,142" fill="currentColor"/>
<text x="320" y="178" font-size="13" text-anchor="middle" fill="currentColor">next state Sₜ₊₁ and reward Rₜ₊₁</text>
</svg>
<figcaption>The reinforcement learning loop. Unlike Chapter 14, the agent does not know the environment's transition
probabilities or reward function: it only sees the states and rewards that actually come back.</figcaption>
</figure>

### Exploration versus exploitation

Every RL agent faces a dilemma. It can **exploit**: take the action that looks best so far. Or it can **explore**: try
something else, which may look worse but might turn out better. Exploit always and you may never find the best action;
explore always and you never use what you have learned. The cleanest setting to study this is the **multi-armed
bandit**, named after slot machines ("one-armed bandits").

A $K$-armed bandit has $K$ actions (arms). Pulling arm $a$ gives a random reward with an unknown mean $\mu_a$. There
are no states: every pull is the same situation again. The agent pulls one arm per step for $n$ steps. Let
$\mu^* = \max_a \mu_a$ and let $\Delta_a = \mu^* - \mu_a$ be the **gap** of arm $a$. The **regret** after $n$ pulls is
how much expected reward was lost compared with always pulling the best arm:

$$
\text{Regret}(n) = n\mu^* - \sum_{t=1}^{n} E[\mu_{A_t}] = \sum_a \Delta_a\, E[N_a(n)],
$$

where $N_a(n)$ is the number of times arm $a$ was pulled. Regret is a sum over bad arms of (how bad) times (how often).
A good algorithm makes the regret grow much more slowly than $n$.

### Estimating an arm's value incrementally

The natural estimate of $\mu_a$ is the average of the rewards seen from arm $a$. Storing all of them is not needed. If
$Q_k$ is the average of the first $k$ rewards and $R_{k+1}$ is the next one,

$$
Q_{k+1} = \frac{1}{k+1}\sum_{i=1}^{k+1} R_i = \frac{k Q_k + R_{k+1}}{k+1} = Q_k + \frac{1}{k+1}\big(R_{k+1} - Q_k\big).
$$

This form, **new estimate = old estimate + step size times (target minus old estimate)**, appears in almost every
algorithm of this chapter. The difference in brackets is an **error**; the step size says how far to move toward the
target. A constant step size $\alpha$ instead of $1/(k+1)$ gives an exponentially weighted average that forgets old
rewards, which is what you want if the means drift.

### Greedy and epsilon-greedy

The **greedy** algorithm always pulls the arm with the highest current estimate. It can lock onto a bad arm forever:
if the best arm's first rewards happen to be low, its estimate stays low because it is never pulled again.

**Epsilon-greedy** pulls a uniformly random arm with probability $\epsilon$ and the greedy arm otherwise. Every arm is
then pulled infinitely often, so by the law of large numbers every estimate converges to the true mean and the greedy
choice becomes the best arm. But with a constant $\epsilon$ the regret grows **linearly**: each step explores with
probability $\epsilon$ and, when it does, picks a bad arm with probability $(K-1)/K$ (for one best arm), losing
$\bar\Delta$ on average, the mean gap of the other arms. So the regret is at least
$n\,\epsilon\,\frac{K-1}{K}\,\bar\Delta$. Decreasing $\epsilon$ over time, for example as $c/t$, fixes this in theory,
but the right constant depends on the unknown gaps.

### UCB1: optimism in the face of uncertainty

A smarter rule explores arms whose value is **uncertain**, not arms at random. Pull each arm once, then at step $t$ pull

$$
A_t = \arg\max_a \Big( Q_a + \sqrt{\frac{2 \ln t}{N_a}} \Big).
$$

The second term is an **exploration bonus**: large for arms pulled rarely ($N_a$ small), growing slowly with time. The
sum is an **upper confidence bound** on the arm's mean: a value it is unlikely to exceed. Choosing the arm with the
highest upper bound is called **optimism in the face of uncertainty**: act as if each arm is as good as it plausibly
could be. Either the optimism is justified (the arm is good, and pulling it earns reward), or it is not (the arm's
estimate falls, and its bonus shrinks as it is pulled), and either way the agent learns.

**Theorem (Auer, Cesa-Bianchi and Fischer, 2002).** For rewards in $[0, 1]$, the expected regret of UCB1 after $n$
pulls is at most

$$
8 \sum_{a: \Delta_a > 0} \frac{\ln n}{\Delta_a} + \Big(1 + \frac{\pi^2}{3}\Big) \sum_a \Delta_a.
$$

**Proof idea.** The tool is **Hoeffding's inequality**: the average of $k$ independent rewards in $[0, 1]$ is more than
$c$ away from its mean with probability at most $e^{-2kc^2}$. With $c = \sqrt{2 \ln t / k}$ this is $t^{-4}$. A bad arm
$a$ is pulled at step $t$ only if (i) the best arm's upper bound is below its true mean, or (ii) arm $a$'s estimate is
far above its mean, or (iii) arm $a$'s bonus is still bigger than half its gap. Events (i) and (ii) have probability
about $t^{-4}$ each, summed over all the ways they can occur, which gives the constant $1 + \pi^2/3$ (from
$\sum_t t^{-2} = \pi^2/6$). Event (iii) needs $\sqrt{2\ln t / N_a} > \Delta_a / 2$, that is,
$N_a < 8 \ln t / \Delta_a^2$, so it stops happening after about $8 \ln n / \Delta_a^2$ pulls of arm $a$. Multiply by
the gap to get the regret. The full proof is two pages in the paper.

So the regret grows only like $\log n$. Lai and Robbins (1985) proved that no algorithm can do better in general: for
any algorithm that is good on every bandit, the number of pulls of a bad arm must grow at least like
$\ln n / \mathrm{KL}(\mu_a, \mu^*)$, where KL is a measure of how hard the two reward distributions are to tell apart.
Logarithmic regret is the best possible, and UCB1 achieves it up to a constant.

### The code

The program runs 200 random 10-armed bandits (each arm pays 1 with a probability drawn between 0.2 and 0.8) for 20 000
pulls, with all 200 runs simulated at once as rows of NumPy arrays.

```python
--8<-- "books/ai/ch15_bandits.py"
```

```
method            regret after 100   after 1000   after 5000   after 20000   best arm chosen (last 1000 pulls)
greedy                        20.5        204.6       1022.6        4090.3        0.120
eps-greedy 0.01               18.1        110.7        262.5         502.3        0.759
eps-greedy 0.1                13.8         58.1        183.6         581.9        0.815
UCB1                          19.3        120.8        312.7         565.1        0.779
run 0, n = 1000: UCB1 regret bound 4013.5
run 0, n = 20000: UCB1 regret bound 5749.2
```

<figure class="mars-fig" markdown="0">
<svg viewBox="0 0 700 270" role="img" aria-label="Cumulative regret over 20000 pulls for four bandit methods. Greedy rises steeply and leaves the chart. Epsilon-greedy with 0.1 is lowest at first but grows in a straight line, ending at 582. UCB1 grows like a flattening curve to 565. Epsilon-greedy with 0.01 ends lowest at 502.">
<line x1="70" y1="230" x2="590" y2="230" stroke="currentColor" stroke-width="1.2"/>
<line x1="70" y1="230" x2="70" y2="30" stroke="currentColor" stroke-width="1.2"/>
<text x="62" y="234" font-size="12" text-anchor="end" fill="currentColor">0</text>
<text x="62" y="184" font-size="12" text-anchor="end" fill="currentColor">200</text>
<text x="62" y="134" font-size="12" text-anchor="end" fill="currentColor">400</text>
<text x="62" y="84" font-size="12" text-anchor="end" fill="currentColor">600</text>
<text x="62" y="34" font-size="12" text-anchor="end" fill="currentColor">800</text>
<text x="70" y="248" font-size="12" text-anchor="middle" fill="currentColor">0</text>
<text x="200" y="248" font-size="12" text-anchor="middle" fill="currentColor">5000</text>
<text x="330" y="248" font-size="12" text-anchor="middle" fill="currentColor">10000</text>
<text x="460" y="248" font-size="12" text-anchor="middle" fill="currentColor">15000</text>
<text x="590" y="248" font-size="12" text-anchor="middle" fill="currentColor">20000</text>
<text x="330" y="265" font-size="12" text-anchor="middle" fill="currentColor">pulls</text>
<polyline fill="none" stroke="#7ccf9a" stroke-width="2.4" points="70,230 83.0,212.5 96.0,202.3 109.0,195.1 122.0,189.3 135.0,184.1 148.0,179.4 161.0,175.1 174.0,171.1 187.0,167.5 200.0,164.4 213.0,161.3 226.0,158.4 239.0,155.5 252.0,152.8 265.0,150.2 278.0,147.6 291.0,145.1 304.0,142.6 317.0,140.1 330.0,137.7 343.0,135.4 356.0,133.2 369.0,131.1 382.0,129.1 395.0,127.1 408.0,125.3 421.0,123.6 434.0,121.9 447.0,120.2 460.0,118.6 473.0,116.9 486.0,115.4 499.0,113.9 512.0,112.4 525.0,110.9 538.0,109.6 551.0,108.3 564.0,107.0 577.0,105.7 590.0,104.4"/>
<polyline fill="none" stroke="#eea66f" stroke-width="2.4" points="70,230 83.0,220.8 96.0,215.5 109.0,210.8 122.0,206.6 135.0,202.5 148.0,198.6 161.0,194.9 174.0,191.2 187.0,187.6 200.0,184.1 213.0,180.6 226.0,177.0 239.0,173.6 252.0,170.1 265.0,166.7 278.0,163.3 291.0,159.9 304.0,156.4 317.0,153.0 330.0,149.5 343.0,146.2 356.0,142.8 369.0,139.4 382.0,136.1 395.0,132.7 408.0,129.4 421.0,126.0 434.0,122.8 447.0,119.6 460.0,116.4 473.0,113.1 486.0,109.9 499.0,106.7 512.0,103.5 525.0,100.3 538.0,97.2 551.0,94.0 564.0,90.8 577.0,87.7 590.0,84.5"/>
<polyline fill="none" stroke="#9cc9ea" stroke-width="2.4" stroke-dasharray="7 3" points="70,230 83.0,211.8 96.0,199.8 109.0,190.4 122.0,182.8 135.0,176.0 148.0,170.2 161.0,165.0 174.0,160.3 187.0,155.9 200.0,151.8 213.0,148.3 226.0,145.0 239.0,141.8 252.0,138.5 265.0,135.4 278.0,132.6 291.0,129.8 304.0,127.1 317.0,124.7 330.0,122.4 343.0,120.2 356.0,118.2 369.0,116.1 382.0,113.9 395.0,111.9 408.0,110.0 421.0,108.3 434.0,106.6 447.0,104.9 460.0,103.2 473.0,101.6 486.0,100.0 499.0,98.4 512.0,96.9 525.0,95.3 538.0,94.0 551.0,92.7 564.0,91.3 577.0,90.1 590.0,88.7"/>
<polyline fill="none" stroke="currentColor" stroke-width="1.6" points="70,230 83.0,204.4 96.0,178.9 109.0,153.3 122.0,127.7 135.0,102.2 148.0,76.6 161.0,51.0 174.0,30.0"/>
<text x="180" y="44" font-size="12" fill="currentColor">greedy (4090 at the end)</text>
<text x="597" y="80" font-size="12" fill="currentColor">eps 0.1: 582</text>
<text x="597" y="96" font-size="12" fill="currentColor">UCB1: 565</text>
<text x="597" y="112" font-size="12" fill="currentColor">eps 0.01: 502</text>
</svg>
<figcaption>Cumulative regret, averaged over 200 random bandits. A straight line means a constant loss per pull (greedy
stuck on a bad arm; epsilon-greedy 0.1 exploring forever); a flattening curve means the loss per pull is falling
(UCB1, and epsilon-greedy 0.01 once its estimates are good).</figcaption>
</figure>

What the numbers say:

- **Greedy** gets stuck: in the last 1000 pulls it pulls the best arm only 12 percent of the time, and its regret grows
  linearly, by about 0.2 per pull.
- **Epsilon-greedy with 0.1** learns fastest early (lowest regret after 100, 1000 and 5000 pulls), but its line keeps
  its slope: from 5000 to 20 000 pulls it adds about 398, or 0.027 per pull, the price of exploring 10 percent of the
  time forever.
- **UCB1** starts slower (it explores every arm systematically) and bends over, adding 252 in the same period, and
  overtakes epsilon-greedy 0.1 before 20 000 pulls. **Epsilon-greedy with 0.01** happens to do best here at 20 000;
  with a different horizon or different gaps the ranking changes, which is why the theory talks about rates.
- **The UCB1 bound** for the first bandit (5749 at 20 000 pulls) is true but very loose: the bound is a worst-case
  guarantee with generous constants, not a prediction.

Two other classical methods deserve a name. **Thompson sampling** (Thompson, 1933) keeps a Bayesian posterior for each
arm's mean, samples one value from each posterior, and pulls the arm whose sample is largest; it also achieves
logarithmic regret (Agrawal and Goyal, 2012) and is often the best in practice (Exercise 9). **Contextual bandits** see
a feature vector before each pull (who the user is) and learn a policy from features to arms; they are the main tool
for recommendation and online advertising.

<figure class="play" data-play="bandit"><span class="ai-tag">AI-created</span><figcaption><b>Watch it.</b> ε-greedy on four arms with made-up hidden chances. Bars show how often each arm was pulled; change ε to explore more or less.</figcaption></figure>

## 15.2 Monte Carlo and temporal-difference learning (Sutton 1988)

Bandits have no states. Back in an MDP, start with the easier half of RL, **prediction**: given a fixed policy $\pi$,
estimate its value function $V^\pi(s)$, the expected return from each state, without knowing $P$ or $R$. (The **return**
$G_t = R_{t+1} + \gamma R_{t+2} + \gamma^2 R_{t+3} + \cdots$ is the discounted sum of rewards after time $t$. In this
chapter rewards are written $R_{t+1}$ when they follow the action at time $t$, the convention of Sutton and Barto.)

### Monte Carlo prediction

The value is an expected return, so estimate it by averaging returns. Run episodes; each time the agent is in state $s$,
note the return $G$ that followed; move $V(s)$ toward it:

$$
V(S_t) \leftarrow V(S_t) + \alpha\big(G_t - V(S_t)\big).
$$

This is **Monte Carlo** (MC) prediction: the target is an actual sample return. It is unbiased, and with step sizes
$1/N(s)$ it converges to $V^\pi$ by the law of large numbers. Its drawbacks: it must wait until the episode ends to know
$G_t$, and $G_t$ is noisy, since it sums many random rewards.

### Temporal-difference prediction

The Bellman equation for $V^\pi$ says $V^\pi(s) = E[R_{t+1} + \gamma V^\pi(S_{t+1}) \mid S_t = s]$. So use the next
reward plus the **current estimate** of the next state's value as the target:

$$
V(S_t) \leftarrow V(S_t) + \alpha\big(R_{t+1} + \gamma V(S_{t+1}) - V(S_t)\big).
$$

This is **TD(0)**, from Richard Sutton's 1988 paper "Learning to predict by the methods of temporal differences". The
quantity $\delta_t = R_{t+1} + \gamma V(S_{t+1}) - V(S_t)$ is the **TD error**: the difference between two successive
predictions of the same thing. Using an estimate to update an estimate is called **bootstrapping** (pulling yourself up
by your own bootstraps). TD learns after every step, needs no model, and its target has lower variance (one random
reward and one estimate, instead of many random rewards); the price is bias, because the estimate $V(S_{t+1})$ may be
wrong.

**Convergence.** For a fixed policy in a finite MDP, tabular TD(0) converges to $V^\pi$ with probability 1 if every
state is visited infinitely often and the step sizes satisfy the **Robbins-Monro conditions**,
$\sum_k \alpha_k = \infty$ and $\sum_k \alpha_k^2 < \infty$ (for example $\alpha_k = 1/k$): big enough in total to
reach anywhere, small enough to average out the noise. Proofs were given by Dayan (1992) and by Jaakkola, Jordan and
Singh (1994), via the theory of stochastic approximation.

### The random walk

Sutton's 1988 example: five states A to E in a row, start in C, step left or right with probability 1/2 each. Leaving
past E pays 1; leaving past A pays 0. There is no discounting. The value of a state is the probability of leaving on the
right, which is $1/6, 2/6, \dots, 5/6$ for A to E (solve the five linear equations $V(s) = \tfrac12 V(\text{left}) + \tfrac12 V(\text{right})$ with values 0
and 1 beyond the ends).

**One episode by hand.** Start with $V = 0.5$ everywhere and $\alpha = 0.1$. Episode: C, D, C, D, E, exit right
(reward 1).

- **TD(0)** updates after each step. C to D: target $0 + V(D) = 0.5$, no change. D to C, C to D: no change. D to E:
  no change. E to exit: target 1, so $V(E) = 0.5 + 0.1 \cdot 0.5 = 0.55$. Only E learns.
- **Monte Carlo** updates every visited state toward the return 1: $V(C)$ twice (to 0.55, then 0.595), $V(D)$ twice
  (0.595), $V(E)$ once (0.55).

MC spreads the news at once; TD spreads it one step per episode. Over many episodes, though, TD wins, as the program
shows.

```python
--8<-- "books/ai/ch15_td.py"
```

```
after C D C D E -> exit right (reward 1), alpha = 0.1
  TD(0) values A..E: [0.5  0.5  0.5  0.5  0.55]
  MC    values A..E: [0.5   0.5   0.595 0.595 0.55 ]

RMS error averaged over states and 100 runs
method           alpha   after 1   after 10   after 50   after 100 episodes
TD(0)             0.05     0.229      0.175      0.053       0.035
TD(0)             0.10     0.222      0.128      0.049       0.055
TD(0)             0.15     0.216      0.093      0.066       0.068
Monte Carlo       0.01     0.233      0.212      0.146       0.097
Monte Carlo       0.02     0.231      0.201      0.110       0.079
Monte Carlo       0.04     0.228      0.190      0.110       0.101
```

For every step size tried, TD has lower error than MC after 10, 50 and 100 episodes. Notice also the plateau: with a
constant step size neither method converges exactly; a larger step size learns faster but settles at a higher noise
level (TD with 0.15 ends at 0.068, with 0.05 at 0.035).

**Why is TD better here?** Imagine all experience so far is fixed and both methods are run on it until they converge
(**batch** updating). Batch MC converges to the average return seen from each state: the values that best fit the
returns. Batch TD converges to the **certainty-equivalence** estimate: the exact values of the MDP whose transition
probabilities are the observed frequencies. TD uses the Markov structure of the problem (what happens after D does not
depend on how you reached D); MC ignores it. When the Markov assumption holds, TD's estimate makes better use of the
data.

### Between MC and TD: n-step returns and eligibility traces

MC and TD(0) are two ends of a spectrum. The **n-step return** uses $n$ real rewards and then bootstraps:
$G_{t:t+n} = R_{t+1} + \gamma R_{t+2} + \cdots + \gamma^{n-1} R_{t+n} + \gamma^n V(S_{t+n})$. TD(0) is $n = 1$; MC is
$n = \infty$. **TD($\lambda$)** averages all n-step returns with weights $(1 - \lambda)\lambda^{n-1}$, and can be
implemented online with an **eligibility trace**, a decaying memory of which states were visited recently, so each TD
error updates all of them at once. Intermediate values of $n$ or $\lambda$ often learn fastest.

## 15.3 Q-learning (Watkins 1989) and SARSA from scratch on a grid world

*Level: intermediate.*

Now the full problem: **control**, learning a good policy. Knowing $V$ is not enough to act without a model, because
choosing the best action from $V$ needs $P(s' \mid s, a)$. So learn the **action value** instead:
$Q(s, a)$, the expected return from taking $a$ in $s$ and then acting well. Then the policy is simply
$\pi(s) = \arg\max_a Q(s, a)$, no model needed. The optimal action values satisfy the **Bellman optimality equation for
Q**:

$$
Q^*(s, a) = E\big[R_{t+1} + \gamma \max_{a'} Q^*(S_{t+1}, a') \,\big|\, S_t = s, A_t = a\big].
$$

### Q-learning

Chris Watkins's 1989 PhD thesis introduced **Q-learning**, the TD update applied to this equation. After taking $A_t$ in
$S_t$ and seeing $R_{t+1}$, $S_{t+1}$:

$$
Q(S_t, A_t) \leftarrow Q(S_t, A_t) + \alpha\big(R_{t+1} + \gamma \max_{a} Q(S_{t+1}, a) - Q(S_t, A_t)\big).
$$

The agent can behave however it likes (for example epsilon-greedily) while the update always uses the max, the value of
the best next action. Q-learning learns about the **greedy** policy while following a different, exploring one; it is
**off-policy**. The policy being learned about is the **target policy**; the one generating the data is the **behaviour
policy**.

**Theorem (Watkins and Dayan, 1992).** In a finite MDP, tabular Q-learning converges to $Q^*$ with probability 1,
provided every state-action pair is updated infinitely often and the step sizes for each pair satisfy the Robbins-Monro
conditions. The proof shows that the Q-learning update is a noisy version of the Bellman optimality operator, which is a
$\gamma$-contraction ([Chapter 14](14-Making-Decisions.md)), and applies stochastic approximation theory.

**One update by hand.** Suppose $Q(s, \text{right}) = -5$, the agent moves right, gets $R = -1$ and lands in $s'$ where
the best action has $Q(s', \cdot) = -4$ (and the one it will actually take next has $-6$). With $\alpha = 0.1$ and
$\gamma = 1$: Q-learning's target is $-1 + (-4) = -5$, so $Q(s, \text{right})$ stays at $-5$. SARSA's target (below) is
$-1 + (-6) = -7$, so $Q$ moves to $-5 + 0.1 \cdot (-2) = -5.2$.

### SARSA

**SARSA** (Rummery and Niranjan, 1994; the name is Sutton's, from the quintuple $S_t, A_t, R_{t+1}, S_{t+1}, A_{t+1}$)
uses the action the agent **actually** takes next:

$$
Q(S_t, A_t) \leftarrow Q(S_t, A_t) + \alpha\big(R_{t+1} + \gamma Q(S_{t+1}, A_{t+1}) - Q(S_t, A_t)\big).
$$

It learns the value of the policy it is following, exploration included: it is **on-policy**. It converges to $Q^*$ if
the policy becomes greedy in the limit while still exploring infinitely often (GLIE: "greedy in the limit with infinite
exploration", for example epsilon-greedy with $\epsilon = 1/t$; Singh, Jaakkola, Littman and Szepesvári, 2000). With a
constant $\epsilon$, it converges to the best epsilon-greedy policy instead, and that difference is visible.

### The cliff

Sutton and Barto's cliff-walking example: a 4 by 12 grid, start bottom left, goal bottom right, and along the bottom
edge between them a cliff. Every step costs $-1$; stepping into the cliff costs $-100$ and sends the agent back to the
start. Both agents use epsilon-greedy exploration with $\epsilon = 0.1$, step size 0.1, no discounting, 500 episodes,
50 independent runs.

```python
--8<-- "books/ai/ch15_qlearning.py"
```

```
sarsa      reward per episode while learning (average of 50 runs): episodes 1-10  -514.5, 91-100  -55.6, 401-500  -22.3
q-learning reward per episode while learning (average of 50 runs): episodes 1-10  -530.8, 91-100  -66.4, 401-500  -48.7

greedy path learned by sarsa in run 0 (C = cliff, G = goal): 17 steps
   >>>>>>>>>>>v
   ^..........v
   ^..........v
   ^CCCCCCCCCCG
   greedy path length over all 50 runs -> 15: 44, 17: 3, loops: 3

greedy path learned by q-learning in run 0 (C = cliff, G = goal): 13 steps
   ............
   ............
   >>>>>>>>>>>v
   ^CCCCCCCCCCG
   greedy path length over all 50 runs -> 13: 50
```

<figure class="mars-fig" markdown="0">
<svg viewBox="0 0 620 190" role="img" aria-label="The cliff-walking grid: 4 rows by 12 columns, the bottom row between start S and goal G is the cliff. SARSA's learned path goes up to the top row, across and down. Q-learning's path runs along the row just above the cliff.">
<rect x="40" y="20" width="45" height="40" fill="none" stroke="currentColor" stroke-width="0.8" stroke-opacity="0.6"/>
<rect x="85" y="20" width="45" height="40" fill="none" stroke="currentColor" stroke-width="0.8" stroke-opacity="0.6"/>
<rect x="130" y="20" width="45" height="40" fill="none" stroke="currentColor" stroke-width="0.8" stroke-opacity="0.6"/>
<rect x="175" y="20" width="45" height="40" fill="none" stroke="currentColor" stroke-width="0.8" stroke-opacity="0.6"/>
<rect x="220" y="20" width="45" height="40" fill="none" stroke="currentColor" stroke-width="0.8" stroke-opacity="0.6"/>
<rect x="265" y="20" width="45" height="40" fill="none" stroke="currentColor" stroke-width="0.8" stroke-opacity="0.6"/>
<rect x="310" y="20" width="45" height="40" fill="none" stroke="currentColor" stroke-width="0.8" stroke-opacity="0.6"/>
<rect x="355" y="20" width="45" height="40" fill="none" stroke="currentColor" stroke-width="0.8" stroke-opacity="0.6"/>
<rect x="400" y="20" width="45" height="40" fill="none" stroke="currentColor" stroke-width="0.8" stroke-opacity="0.6"/>
<rect x="445" y="20" width="45" height="40" fill="none" stroke="currentColor" stroke-width="0.8" stroke-opacity="0.6"/>
<rect x="490" y="20" width="45" height="40" fill="none" stroke="currentColor" stroke-width="0.8" stroke-opacity="0.6"/>
<rect x="535" y="20" width="45" height="40" fill="none" stroke="currentColor" stroke-width="0.8" stroke-opacity="0.6"/>
<rect x="40" y="60" width="45" height="40" fill="none" stroke="currentColor" stroke-width="0.8" stroke-opacity="0.6"/>
<rect x="85" y="60" width="45" height="40" fill="none" stroke="currentColor" stroke-width="0.8" stroke-opacity="0.6"/>
<rect x="130" y="60" width="45" height="40" fill="none" stroke="currentColor" stroke-width="0.8" stroke-opacity="0.6"/>
<rect x="175" y="60" width="45" height="40" fill="none" stroke="currentColor" stroke-width="0.8" stroke-opacity="0.6"/>
<rect x="220" y="60" width="45" height="40" fill="none" stroke="currentColor" stroke-width="0.8" stroke-opacity="0.6"/>
<rect x="265" y="60" width="45" height="40" fill="none" stroke="currentColor" stroke-width="0.8" stroke-opacity="0.6"/>
<rect x="310" y="60" width="45" height="40" fill="none" stroke="currentColor" stroke-width="0.8" stroke-opacity="0.6"/>
<rect x="355" y="60" width="45" height="40" fill="none" stroke="currentColor" stroke-width="0.8" stroke-opacity="0.6"/>
<rect x="400" y="60" width="45" height="40" fill="none" stroke="currentColor" stroke-width="0.8" stroke-opacity="0.6"/>
<rect x="445" y="60" width="45" height="40" fill="none" stroke="currentColor" stroke-width="0.8" stroke-opacity="0.6"/>
<rect x="490" y="60" width="45" height="40" fill="none" stroke="currentColor" stroke-width="0.8" stroke-opacity="0.6"/>
<rect x="535" y="60" width="45" height="40" fill="none" stroke="currentColor" stroke-width="0.8" stroke-opacity="0.6"/>
<rect x="40" y="100" width="45" height="40" fill="none" stroke="currentColor" stroke-width="0.8" stroke-opacity="0.6"/>
<rect x="85" y="100" width="45" height="40" fill="none" stroke="currentColor" stroke-width="0.8" stroke-opacity="0.6"/>
<rect x="130" y="100" width="45" height="40" fill="none" stroke="currentColor" stroke-width="0.8" stroke-opacity="0.6"/>
<rect x="175" y="100" width="45" height="40" fill="none" stroke="currentColor" stroke-width="0.8" stroke-opacity="0.6"/>
<rect x="220" y="100" width="45" height="40" fill="none" stroke="currentColor" stroke-width="0.8" stroke-opacity="0.6"/>
<rect x="265" y="100" width="45" height="40" fill="none" stroke="currentColor" stroke-width="0.8" stroke-opacity="0.6"/>
<rect x="310" y="100" width="45" height="40" fill="none" stroke="currentColor" stroke-width="0.8" stroke-opacity="0.6"/>
<rect x="355" y="100" width="45" height="40" fill="none" stroke="currentColor" stroke-width="0.8" stroke-opacity="0.6"/>
<rect x="400" y="100" width="45" height="40" fill="none" stroke="currentColor" stroke-width="0.8" stroke-opacity="0.6"/>
<rect x="445" y="100" width="45" height="40" fill="none" stroke="currentColor" stroke-width="0.8" stroke-opacity="0.6"/>
<rect x="490" y="100" width="45" height="40" fill="none" stroke="currentColor" stroke-width="0.8" stroke-opacity="0.6"/>
<rect x="535" y="100" width="45" height="40" fill="none" stroke="currentColor" stroke-width="0.8" stroke-opacity="0.6"/>
<rect x="40" y="140" width="45" height="40" fill="none" stroke="currentColor" stroke-width="0.8" stroke-opacity="0.6"/>
<rect x="85" y="140" width="45" height="40" fill="#eea66f" fill-opacity="0.55" stroke="currentColor" stroke-width="0.8"/>
<rect x="130" y="140" width="45" height="40" fill="#eea66f" fill-opacity="0.55" stroke="currentColor" stroke-width="0.8"/>
<rect x="175" y="140" width="45" height="40" fill="#eea66f" fill-opacity="0.55" stroke="currentColor" stroke-width="0.8"/>
<rect x="220" y="140" width="45" height="40" fill="#eea66f" fill-opacity="0.55" stroke="currentColor" stroke-width="0.8"/>
<rect x="265" y="140" width="45" height="40" fill="#eea66f" fill-opacity="0.55" stroke="currentColor" stroke-width="0.8"/>
<rect x="310" y="140" width="45" height="40" fill="#eea66f" fill-opacity="0.55" stroke="currentColor" stroke-width="0.8"/>
<rect x="355" y="140" width="45" height="40" fill="#eea66f" fill-opacity="0.55" stroke="currentColor" stroke-width="0.8"/>
<rect x="400" y="140" width="45" height="40" fill="#eea66f" fill-opacity="0.55" stroke="currentColor" stroke-width="0.8"/>
<rect x="445" y="140" width="45" height="40" fill="#eea66f" fill-opacity="0.55" stroke="currentColor" stroke-width="0.8"/>
<rect x="490" y="140" width="45" height="40" fill="#eea66f" fill-opacity="0.55" stroke="currentColor" stroke-width="0.8"/>
<rect x="535" y="140" width="45" height="40" fill="none" stroke="currentColor" stroke-width="0.8" stroke-opacity="0.6"/>
<text x="310.0" y="165" font-size="14" text-anchor="middle" fill="currentColor">the cliff: -100, back to start</text>
<text x="62.5" y="165" font-size="14" text-anchor="middle" fill="currentColor">S</text>
<text x="557.5" y="165" font-size="14" text-anchor="middle" fill="currentColor">G</text>
<polyline points="62.5,152.0 62.5,40.0 557.5,40.0 557.5,152.0" fill="none" stroke="#9cc9ea" stroke-width="3.5" />
<polyline points="62.5,152.0 62.5,120.0 557.5,120.0 557.5,152.0" fill="none" stroke="#7ccf9a" stroke-width="3.5" stroke-dasharray="8 4"/>
<text x="310.0" y="36" font-size="13" text-anchor="middle" fill="currentColor">SARSA: the safe path, 17 steps</text>
<text x="310.0" y="114" font-size="13" text-anchor="middle" fill="currentColor">Q-learning: the optimal path, 13 steps</text>
</svg>
<figcaption>What the two agents learned in run 0. Q-learning (dashed green) learned the shortest path, right along the
cliff edge; SARSA (solid blue) learned to keep its distance. Most SARSA runs chose the middle row (15 steps); run 0 went
all the way to the top (17).</figcaption>
</figure>

The results look contradictory, and the contradiction is the lesson.

- **Q-learning learned the better policy.** In all 50 runs its greedy path is the optimal 13-step route along the edge.
  It learns the value of acting greedily, and greedily the edge is safe.
- **SARSA earned more reward while learning**: about $-22$ per episode at the end against $-49$ for Q-learning. With
  10 percent random moves, walking along the edge means regularly falling off. SARSA learns the value of the policy it
  actually follows, exploration included, and that policy is safer one or two rows up.
- **Which is right depends on what you need.** If the agent will keep exploring while it works (a robot learning on
  the job), the on-policy answer is the honest one. If exploration will stop and the greedy policy will be deployed,
  Q-learning's answer is better.
- **Not everything is clean**: with a constant step size, values keep fluctuating, and in 3 of 50 SARSA runs the greedy
  policy at the end of training even contains a loop in a rarely visited state. Learned policies need to be checked.

A related method, **expected SARSA**, uses $\sum_a \pi(a \mid S_{t+1}) Q(S_{t+1}, a)$ as the target, the average over
the next action instead of a sample; it has lower variance than SARSA and includes Q-learning as the case of a greedy
target policy.

## 15.4 Function approximation; deep Q-networks (Mnih et al. 2015)

*Level: advanced.*

A table with one entry per state works for 48 squares. Backgammon has about $10^{20}$ positions; a camera image has far
more possible values than there are atoms in the universe. No table will do, and even if it fitted, most states would
never be visited. We need to **generalise**: learn from one state something about similar states. That means replacing
the table by a parameterised function, $\hat v(s; \mathbf{w}) \approx V^\pi(s)$ or $\hat q(s, a; \mathbf{w}) \approx Q(s, a)$,
with a weight vector $\mathbf{w}$ much smaller than the number of states: a linear function of features, or a neural
network.

### Semi-gradient TD

For prediction with a fixed target $U_t$ (for example the MC return $G_t$), this is regression: minimise
$\frac12(U_t - \hat v(S_t; \mathbf{w}))^2$ by stochastic gradient descent,

$$
\mathbf{w} \leftarrow \mathbf{w} + \alpha\big(U_t - \hat v(S_t; \mathbf{w})\big)\nabla_{\mathbf{w}} \hat v(S_t; \mathbf{w}).
$$

TD uses the bootstrapped target $U_t = R_{t+1} + \gamma \hat v(S_{t+1}; \mathbf{w})$, which itself depends on
$\mathbf{w}$. The usual rule ignores that dependence and uses the same update; it is called **semi-gradient** TD,
because it is not the gradient of any fixed objective. With a linear function $\hat v(s) = \mathbf{w}^\top \mathbf{x}(s)$
of a feature vector $\mathbf{x}(s)$, the gradient is just $\mathbf{x}(s)$.

What is known:

- **Linear TD, on-policy, converges.** Tsitsiklis and Van Roy (1997) proved that linear semi-gradient TD($\lambda$),
  with states sampled from the policy's own visits, converges with probability 1 to a unique fixed point (the **TD
  fixed point**), and that its error is within a factor of the best possible linear approximation; for TD(0) the factor
  in Sutton and Barto's statement (their equation 9.14) is $1/(1 - \gamma)$ in the mean squared value error.
- **The deadly triad can diverge.** Combine (1) function approximation, (2) bootstrapping and (3) off-policy updates,
  and the weights can grow without bound even in tiny problems; Baird (1995) gave a seven-state counterexample. Sutton
  and Barto call this combination the **deadly triad**. Q-learning with a neural network has all three.

### Deep Q-networks

Volodymyr Mnih and colleagues (*Nature*, 2015, "Human-level control through deep reinforcement learning") trained a
convolutional network that maps the last four frames of an Atari 2600 game's screen to the Q values of the joystick
actions, learning from the score alone. With the same network architecture and hyperparameters for all 49 games tested,
they report performance "comparable to that of a professional human games tester" across the set. Two ingredients made
Q-learning with a large network stable enough:

1. **Experience replay** (Lin, 1992). Store transitions $(s, a, r, s')$ in a large buffer and train on random
   minibatches from it. This reuses data, and it breaks the correlation between consecutive samples that would
   otherwise make stochastic gradient descent chase its own tail.
2. **A target network.** Compute targets $y = r + \gamma \max_{a'} \hat q(s', a'; \mathbf{w}^-)$ with a copy
   $\mathbf{w}^-$ of the weights that is updated only every few thousand steps. The target stops moving with every
   update, which turns each phase into an ordinary regression problem.

They also clipped rewards to $[-1, 1]$ and used a loss whose gradient is clipped (the Huber loss). Later work fixed a
known flaw: the max in the target **overestimates** values, because the max of noisy estimates is biased upward.
**Double DQN** (van Hasselt, Guez and Silver, 2016) chooses the next action with the online network and evaluates it
with the target network, which removes most of the bias.

### A tiny DQN, from scratch

The program implements the cart-pole task (a pole balanced on a cart pushed left or right; the equations of motion are
those of Barto, Sutton and Anderson, 1983) and a DQN with every ingredient above: a two-layer network with 64 ReLU
units, written in NumPy with its own backpropagation and Adam optimiser; a replay buffer; a target network copied every
500 steps; epsilon decaying from 1 to 0.05; and the Huber loss. Reward is 1 per step until the pole falls past 12
degrees or the cart leaves the track, up to 200 steps. Note the subtle point in the code: a step that ends because of
the 200-step limit is **not** treated as terminal in the target, because the state there still has a future; only a
real failure is.

```python
--8<-- "books/ai/ch15_dqn.py"
```

```
random policy: mean episode length 21.6 steps (maximum 200)
DQN training, seed 0:
  step   2000  epsilon 0.60  episodes   83  mean length of last 10   34.5  greedy test  182.2
  step   4000  epsilon 0.20  episodes  107  mean length of last 10  114.2  greedy test  187.4
  step   6000  epsilon 0.05  episodes  118  mean length of last 10  184.3  greedy test  186.9
  step   8000  epsilon 0.05  episodes  129  mean length of last 10  176.8  greedy test  170.9
  step  10000  epsilon 0.05  episodes  140  mean length of last 10  181.9  greedy test  197.9
  step  12000  epsilon 0.05  episodes  150  mean length of last 10  189.5  greedy test  197.8
```

A random policy keeps the pole up for about 22 steps. After 12 000 steps of experience (about four minutes of simulated
time) the greedy network balances it for 198 steps on average out of 200. The "greedy test" column dips at step 8000:
DQN training is not monotone, and runs with other seeds can be much worse. This instability, and the sensitivity to
hyperparameters, is the everyday reality of deep RL; published comparisons average over many seeds for this reason
(Henderson et al., 2018, "Deep reinforcement learning that matters").

## 15.5 Policy gradients: REINFORCE (Williams 1992) derived; actor-critic; PPO (Schulman et al. 2017)

*Level: advanced.*

Value-based methods learn $Q$ and act greedily. Sometimes it is better to learn the policy directly. Three reasons:

- **Continuous actions.** A robot arm's torques are real numbers; $\arg\max_a Q(s, a)$ over a continuum is itself an
  optimisation problem at every step. A policy can simply output the action (or the mean of a Gaussian over actions).
- **Stochastic optimal policies.** When the agent cannot tell some states apart, the best policy may have to be
  random (the example below). Greedy methods are deterministic.
- **Smoothness.** A small change in $Q$ can flip the greedy action abruptly; a small change in the policy's parameters
  changes action probabilities smoothly, which makes convergence easier to analyse.

### The policy gradient

Let $\pi_\theta(a \mid s)$ be a differentiable policy with parameters $\theta$, for example a softmax over action
preferences computed by a network. The objective, for episodic tasks, is the expected return from the start:
$J(\theta) = E_{\tau \sim \pi_\theta}[G(\tau)]$, where $\tau = (S_0, A_0, R_1, S_1, A_1, \dots)$ is a whole episode
(a **trajectory**) and $G(\tau)$ its return. We want $\nabla_\theta J$, but the expectation is over trajectories whose
distribution depends on $\theta$, through the policy and, it seems, through the unknown environment.

**The log-derivative trick.** For any distribution $p_\theta(\tau)$, since $\nabla p = p \nabla \log p$,

$$
\nabla_\theta E_{\tau \sim p_\theta}[G(\tau)] = \sum_\tau G(\tau) \nabla_\theta p_\theta(\tau) = E_{\tau \sim p_\theta}\big[G(\tau)\, \nabla_\theta \log p_\theta(\tau)\big].
$$

**The environment drops out.** The probability of a trajectory is
$p_\theta(\tau) = P(S_0) \prod_t \pi_\theta(A_t \mid S_t)\, P(S_{t+1} \mid S_t, A_t)$, so

$$
\nabla_\theta \log p_\theta(\tau) = \sum_t \nabla_\theta \log \pi_\theta(A_t \mid S_t),
$$

because the start distribution and the transitions do not depend on $\theta$. We do not need the model: only the
gradient of our own policy's log-probabilities.

**Causality.** An action at time $t$ cannot affect rewards before $t$. The terms pairing $\nabla \log \pi(A_t \mid S_t)$
with earlier rewards have expectation zero (by the baseline argument below, with the earlier rewards playing the role
of a baseline), so we can keep only the rewards from $t$ on, the return $G_t$:

$$
\nabla_\theta J(\theta) = E_{\pi_\theta}\Big[\sum_t G_t\, \nabla_\theta \log \pi_\theta(A_t \mid S_t)\Big].
$$

This is a form of the **policy gradient theorem** (Sutton, McAllester, Singh and Mansour, 2000, give the general
version, including discounting and continuing tasks; with discounting, a factor $\gamma^t$ appears). It says: make
actions that were followed by high returns more likely, in proportion to the return.

### REINFORCE

Ronald Williams's 1992 algorithm, **REINFORCE**, is the sample version: run an episode with $\pi_\theta$, then for each
step

$$
\theta \leftarrow \theta + \alpha\, G_t\, \nabla_\theta \log \pi_\theta(A_t \mid S_t).
$$

Each update is an unbiased estimate of the gradient, so with suitable step sizes REINFORCE converges to a local optimum
of $J$ (stochastic gradient ascent). Its weakness is variance: $G_t$ is a sum of many random rewards, and in a problem
where all returns are negative, every action taken is pushed down, the good ones just less than the bad.

### Baselines

Subtract any function $b(s)$ of the state from the return:
$\theta \leftarrow \theta + \alpha\,(G_t - b(S_t))\,\nabla \log \pi_\theta(A_t \mid S_t)$.

**Claim.** A baseline does not change the expected update. **Proof.** For a fixed state $s$,

$$
E_{a \sim \pi}\big[b(s)\nabla_\theta \log \pi_\theta(a \mid s)\big] = b(s) \sum_a \pi_\theta(a \mid s) \frac{\nabla_\theta \pi_\theta(a \mid s)}{\pi_\theta(a \mid s)} = b(s)\, \nabla_\theta \sum_a \pi_\theta(a \mid s) = b(s) \nabla_\theta 1 = 0. \qquad \square
$$

But it can reduce the variance a great deal. A natural choice is a learned estimate of the state value,
$b(s) = \hat v(s; \mathbf{w})$. Then $G_t - \hat v(S_t)$ estimates the **advantage** of the action taken: how much
better it was than average from that state. Good actions are pushed up and bad ones down, whatever the overall level
of the returns.

### Actor-critic

Go one step further and replace the return by the bootstrapped TD target: the **one-step actor-critic** update uses the
TD error $\delta_t = R_{t+1} + \gamma \hat v(S_{t+1}) - \hat v(S_t)$:

$$
\mathbf{w} \leftarrow \mathbf{w} + \alpha_w \delta_t \nabla_{\mathbf{w}} \hat v(S_t), \qquad
\theta \leftarrow \theta + \alpha_\theta \delta_t \nabla_\theta \log \pi_\theta(A_t \mid S_t).
$$

The policy is the **actor**; the value function is the **critic**, which judges each action by the surprise it caused.
It learns online, step by step, with lower variance than REINFORCE, at the cost of the bias that bootstrapping brings.
The idea goes back to Barto, Sutton and Anderson (1983), whose "adaptive critic" solved the cart-pole task.

### PPO

Policy gradient steps must be small: a step that changes the policy too much can collapse performance, and the data
gathered with the old policy no longer describe the new one. **Trust region policy optimization** (TRPO; Schulman,
Levine, Abbeel, Jordan and Moritz, 2015) limits the KL divergence between successive policies, with a constrained
optimisation at each step. **Proximal policy optimization** (PPO; Schulman, Wolski, Dhariwal, Radford and Klimov, 2017)
gets a similar effect with a simple clipped objective. Collect a batch with the old policy $\pi_{\text{old}}$, compute
advantage estimates $\hat A_t$, and let $r_t(\theta) = \pi_\theta(A_t \mid S_t)/\pi_{\text{old}}(A_t \mid S_t)$ be the
**probability ratio**. Maximise, for several epochs over the batch,

$$
L^{\text{CLIP}}(\theta) = E_t\Big[\min\big(r_t(\theta)\hat A_t,\ \mathrm{clip}(r_t(\theta), 1 - \epsilon, 1 + \epsilon)\hat A_t\big)\Big],
$$

with $\epsilon$ around 0.2. Where the advantage is positive, the objective stops rewarding increases in the ratio
beyond $1 + \epsilon$; where it is negative, it stops rewarding decreases below $1 - \epsilon$. So there is no incentive
to move the policy far from the one that collected the data. At $\theta = \theta_{\text{old}}$, the gradient of
$r_t \hat A_t$ is exactly the policy gradient (since $\nabla r_t = \nabla \log \pi_\theta$ there), so PPO is a policy
gradient method that reuses each batch safely. It became one of the most widely used RL algorithms, including for
fine-tuning language models from human feedback ([Chapter 17](17-Large-Language-Models.md)).

### The short corridor: where only randomness works

Sutton and Barto's Example 13.1: three squares and a goal, reward $-1$ per step. Right moves right, left moves left,
except in the middle square, where the actions are **reversed**. The agent sees the same features in every square, so
it cannot tell them apart; its policy is a single probability $p$ of going right. Always right ($p = 1$) bounces between
the first two squares forever; always left ($p = 0$) never leaves the first. With an epsilon-greedy value method, the
agent is stuck near one of these. The best policy is random. Solving the three Bellman equations for fixed $p$
(Exercise 7) gives the value from the start

$$
J(p) = \frac{2p - 4}{p(1 - p)},
$$

which is maximised at $p = 2 - \sqrt{2} \approx 0.586$, with $J = -6 - 4\sqrt{2} \approx -11.66$.

The program learns $p = \sigma(\theta)$, the logistic function of one parameter, starting from $p = 0.05$; for it,
$\nabla_\theta \log \pi(\text{right}) = 1 - p$ and $\nabla_\theta \log \pi(\text{left}) = -p$.

```python
--8<-- "books/ai/ch15_policy_gradient.py"
```

```
exact: best P(right) = 0.586, value -11.66; P(right) = 0.05 gives -82.11, P(right) = 0.95 gives -44.21

P(right) learned (mean over 30 runs) and its true value
method                    after 100        after 300        after 1000 episodes
REINFORCE                 0.139 (-31.06)  0.256 (-18.31)  0.473 (-12.25)
REINFORCE with baseline   0.374 (-13.88)  0.561 (-11.69)  0.591 (-11.66)
actor-critic              0.576 (-11.66)  0.577 (-11.66)  0.565 (-11.68)
PPO, batches of 10        0.076 (-55.01)  0.287 (-16.76)  0.578 (-11.66)
```

All four methods find the random policy near $p = 0.586$ that no greedy method can represent. Plain REINFORCE needs a
tiny step size ($2^{-12}$) to stay stable, so it is slow. With a baseline the step size can be eight times larger and
it reaches the optimum in about 300 episodes. The actor-critic, whose critic is allowed to see which square it is in
(the actor still cannot), learns fastest of all. PPO here uses each batch of 10 episodes for 4 gradient steps; it is
slow at first because it can change the policy only a limited amount per batch, which is exactly its design. (The
values in brackets are those of the mean $p$, from the formula.)

## 15.6 Model-based RL and planning (Dyna); AlphaZero/MuZero (Schrittwieser et al. 2020)

*Level: intermediate.*

Q-learning uses each experience once and throws it away. A **model-based** agent also learns a model of the
environment, $\hat P(s' \mid s, a)$ and $\hat R(s, a)$, and uses it to **plan**: to improve its values or policy by
simulated experience. Real experience is expensive (a robot's time, a patient's health); simulated experience is
cheap. The cost is that the model may be wrong.

### Dyna-Q

Sutton's **Dyna** architecture (1990) integrates learning, model learning and planning in one loop. **Dyna-Q** does,
after every real step:

1. **Direct RL:** a Q-learning update from the real transition.
2. **Model learning:** remember that $(s, a)$ led to $(s', r)$ (for a deterministic world, a table entry).
3. **Planning:** $n$ times, pick a previously seen $(s, a)$ at random, ask the model for $(s', r)$, and do the same
   Q-learning update on this simulated transition.

Planning here is just Q-learning on remembered data, which is also what experience replay does in DQN; the two ideas are
close relatives. The program runs Dyna-Q on Sutton and Barto's maze (6 by 9 with walls, reward 1 at the goal,
$\gamma = 0.95$, $\epsilon = 0.1$).

```python
--8<-- "books/ai/ch15_dyna.py"
```

```
planning steps n   steps in episode 1    2      3      5     10     20     50   (mean of 20 runs)
               0                 703    776    484    343    147     47     17
               5                 801    127     66     22     17     16     17
              50                 787     39     17     17     17     16     16
shortest path: 14 steps
```

The first episode is a long random wander for everybody: with all values zero there is nothing to plan with. After it,
the difference is dramatic. Without planning, the news of the goal creeps back one square per episode, and the agent
needs about 20 episodes to find a good path. With 50 planning steps per real step, the second episode is already short
(39 steps) and the third is near the best the agent can do. (The floor of 16 to 17 steps instead of 14 is the cost of
10 percent random moves.) Planning turned one episode of real experience into many.

**Prioritized sweeping** (Moore and Atkeson, 1993) improves on random replay: it plans first from the state-action
pairs whose values would change most, working backwards from where values just changed, like a smart version of
value iteration.

### Search plus learning: AlphaZero and MuZero

[Chapter 6](06-Games-and-Adversarial-Search.md) described AlphaZero (Silver et al., 2018): a network gives a policy and a
value for board positions; Monte Carlo tree search uses them to look ahead; the search results become training targets
for the network; and the system improves by self-play. In RL terms this is **policy iteration** with search as the
improvement step: the search's move probabilities are a better policy than the network's raw output, and the network is
trained to imitate them, then used for the next search. But AlphaZero is given the **rules**: the search uses an exact
simulator of the game.

**MuZero** (Schrittwieser et al., *Nature*, 2020, "Mastering Atari, Go, chess and shogi by planning with a learned
model") removes that. It learns three functions: a **representation** function that encodes the observation history
into a hidden state, a **dynamics** function that predicts the next hidden state and reward from a hidden state and an
action, and a **prediction** function that outputs a policy and a value. The tree search runs entirely inside the
learned hidden space. The model is not trained to reconstruct observations; it is trained only so that the rewards,
values and policies predicted along imagined action sequences match those actually observed. The paper reports that
MuZero matched AlphaZero's performance in Go, chess and shogi without being told the rules, and set a new state of the
art on the 57-game Atari benchmark at the time. The lesson for model-based RL: a model need only predict what matters
for decisions, not everything about the world.

## 15.7 Reward design and specification gaming, technically

*Level: advanced.*

Everything in this chapter maximises the reward it is given. The reward is the designer's attempt to describe what they
want, and descriptions are imperfect. **Specification gaming** is an agent achieving high reward by satisfying the
literal specification in a way the designer did not intend. It is not a bug in the learning algorithm: the algorithm is
doing its job. The bug is in the reward, and a better optimiser finds it more reliably. Related terms: **reward
hacking** (exploiting flaws in the reward), and **Goodhart's law**, after the economist Charles Goodhart, often
paraphrased as "when a measure becomes a target, it ceases to be a good measure".

### Documented examples

- Lehman and many co-authors (2020, "The surprising creativity of digital evolution", *Artificial Life*) collected
  first-hand accounts from researchers of evolutionary and learning systems that satisfied a fitness measure in
  unintended ways, such as simulated creatures exploiting bugs in physics engines.
- Popov et al. (2017), studying robotic manipulation with deep RL, report that with one version of the reward for
  stacking one Lego brick on another (based on the height of the brick's bottom face), the agent learned to flip the
  brick over instead of stacking it.
- Amodei et al. (2016, "Concrete problems in AI safety") give a technical taxonomy: reward hacking, negative side
  effects, unsafe exploration, and distributional shift, with research directions for each.

### Gaming in code: the respawning checkpoint

The toy race track below has squares 0 to 20; reaching 20 pays 10 and ends the episode; $\gamma = 0.95$. To speed up
learning, the designer adds a bonus of 1 for entering a checkpoint at square 5. It seems harmless. But the bonus pays
**every time** the agent enters square 5. From square 4, stepping in and out forever is worth

$$
1 + \gamma^2 + \gamma^4 + \cdots = \frac{1}{1 - \gamma^2} = 10.26,
$$

while driving to the goal (collecting the bonus once) is worth $1 + \gamma^{15} \cdot 10 = 5.63$. The optimal policy
for the reward as written is to never finish. A third variant uses a **potential-based** progress bonus instead
(below).

```python
--8<-- "books/ai/ch15_gaming.py"
```

```
from square 4: stepping in and out of square 5 forever is worth 1/(1 - gamma^2) = 10.26; driving to the goal (passing 5 once) is worth 1 + gamma^15 * 10 = 5.63
variant      first finish   finishes in 500 episodes   greedy policy after learning
sparse                 36                        330   reaches the goal in 20 steps
checkpoint           None                          0   never finishes; ends [5, 6, 5, 6, 5, 6]
shaped                  1                        500   reaches the goal in 20 steps

over 20 seeds: mean episode of first finish and fraction of seeds whose greedy policy finishes
sparse       first finish   68.7   greedy policy finishes in 20 of 20
checkpoint   first finish  500.0   greedy policy finishes in 0 of 20
shaped       first finish    1.0   greedy policy finishes in 20 of 20
```

With only the goal reward ("sparse"), Q-learning eventually learns to finish, but needs about 69 episodes on average
to stumble on the goal once. With the checkpoint bonus, the agent **never** finishes in any seed: it learned to oscillate
next to the checkpoint, exactly as the arithmetic predicts. With potential-based shaping it finishes in the very first
episode and always learns the intended policy.

### Potential-based shaping is safe

**Theorem (Ng, Harada and Russell, 1999).** Let $\Phi$ be any real function of states (a **potential**), with
$\Phi = 0$ at terminal states, and add to every reward the shaping term

$$
F(s, s') = \gamma \Phi(s') - \Phi(s).
$$

Then every policy's action values change by the same state-dependent amount: $Q'^{\pi}(s, a) = Q^{\pi}(s, a) - \Phi(s)$.
In particular, the optimal policies of the shaped and original problems are the same.

**Proof.** Along any trajectory $s_0, s_1, s_2, \dots$, the discounted sum of the shaping terms telescopes:

$$
\sum_{t=0}^{T-1} \gamma^t\big(\gamma\Phi(s_{t+1}) - \Phi(s_t)\big) = \gamma^T \Phi(s_T) - \Phi(s_0).
$$

If the trajectory ends in a terminal state, $\Phi(s_T) = 0$; for infinite trajectories with $\gamma < 1$ and bounded
$\Phi$, $\gamma^T\Phi(s_T) \to 0$. Either way the shaping adds exactly $-\Phi(s_0)$ to the return of every trajectory
starting at $s_0$. Taking expectations, every action's value from $s_0$ shifts by the same $-\Phi(s_0)$, which cannot
change which action is best. $\square$

Ng, Harada and Russell also showed the converse: if $F$ is **not** of this form, there are MDPs in which it changes the
optimal policy. The checkpoint bonus is not potential-based: going around a cycle (into 5 and back out) collects a
positive total, while a potential-based bonus summed around any cycle back to the same state is $(\gamma^k - 1)\Phi(s)$
for a cycle of length $k$, which can never be a source of unlimited reward. In our shaped variant $\Phi(s) = s/2$, a
guess at "progress", and the agent gets an immediate learning signal on every step without any way to profit except by
real progress.

### Broader approaches

Shaping fixes one failure mode. Others are harder:

- **Learning the reward from people.** Rather than writing a reward, learn it: from demonstrations (inverse
  reinforcement learning, Ng and Russell, 2000) or from human comparisons between pairs of behaviours (Christiano et al.,
  2017, "Deep reinforcement learning from human preferences"). The learned reward is itself a model that can be
  gamed, so it must be kept within the range where it is accurate, often by penalising divergence from a reference
  policy. These methods are the subject of [Chapter 17](17-Large-Language-Models.md) and
  [Chapter 20](20-Safe-and-Reliable-AI.md).
- **Side effects.** A reward that mentions only the goal is silent about everything else the agent might break on the
  way. Research proposals penalise changes to the environment relative to a baseline (for example Krakovna et al.,
  2019, on relative reachability); none is a general solution.
- **Testing.** Watching what a trained agent actually does, in many situations, catches gaming that summary reward
  curves hide: the checkpoint agent's reward looked excellent.

## In practice

- Start with the simplest method that could work: tabular Q-learning or SARSA if the state space is small, a bandit
  algorithm if there is no state. Measure over several seeds; report averages and spread.
- Real libraries: Gymnasium (the maintained successor of the Gym library) provides standard environments; Stable-Baselines3
  and similar libraries implement DQN, PPO and actor-critic methods on top of PyTorch.
- Exploration, reward design and evaluation usually matter more than the choice of algorithm. Look at the behaviour, not
  only at the reward curve.

## Check yourself

??? question "1. Show that the incremental update Q_{k+1} = Q_k + (R_{k+1} - Q_k)/(k+1) gives the average of the first k+1 rewards, and that a constant step size alpha gives weight alpha(1-alpha)^(k-i) to reward R_i."
    By induction: if $Q_k = \frac1k\sum_{i \le k} R_i$, then $Q_k + \frac{R_{k+1} - Q_k}{k+1} = \frac{kQ_k + R_{k+1}}{k+1}
    = \frac{1}{k+1}\sum_{i \le k+1} R_i$. With constant $\alpha$: $Q_{k+1} = (1-\alpha)Q_k + \alpha R_{k+1}$. Unrolling,
    $Q_{k+1} = (1-\alpha)^{k+1}Q_0 + \sum_{i=1}^{k+1} \alpha(1-\alpha)^{k+1-i} R_i$, so the newest reward gets weight $\alpha$
    and each older one a factor $(1-\alpha)$ less: an exponentially weighted (recency-weighted) average.

??? question "2. At step t = 100, UCB1 has arm 1 with mean 0.6 pulled 20 times and arm 2 with mean 0.5 pulled 5 times. Which arm does it pull?"
    Arm 1: $0.6 + \sqrt{2 \ln 100 / 20} = 0.6 + \sqrt{0.4605} = 0.6 + 0.679 = 1.279$. Arm 2:
    $0.5 + \sqrt{2 \ln 100 / 5} = 0.5 + \sqrt{1.842} = 0.5 + 1.357 = 1.857$. It pulls arm 2: its mean is lower, but it is so
    uncertain that its upper bound is higher.

??? question "3. A 10-armed bandit has one best arm, and the other nine have gaps averaging 0.25. Estimate the regret per pull of epsilon-greedy with epsilon = 0.1 once all estimates are accurate, and compare with the program's slope."
    When estimates are accurate, greedy pulls are free. Exploring pulls happen with probability 0.1 and choose a bad arm
    with probability 9/10, losing 0.25 on average: $0.1 \cdot 0.9 \cdot 0.25 = 0.0225$ per pull. The program's slope from
    5000 to 20 000 pulls is about $(581.9 - 183.6)/15000 = 0.027$. The bandits in the program have an average gap of 0.272 (computed from the
    same seed), which gives $0.1 \cdot 0.9 \cdot 0.272 = 0.0245$; the rest comes from estimates that are not yet
    perfect, so some greedy pulls still go to the wrong arm.

??? question "4. In the random walk, run one episode C, B, A, exit left (reward 0) from V = 0.5 everywhere with alpha = 0.1. What do TD(0) and Monte Carlo change?"
    TD(0): C to B, target $V(B) = 0.5$, no change; B to A, no change; A to exit, target 0, so
    $V(A) = 0.5 + 0.1(0 - 0.5) = 0.45$. Monte Carlo: the return is 0 for every visited state, so $V(C)$, $V(B)$ and
    $V(A)$ each become $0.45$. D and E are unchanged in both.

??? question "5. Explain in one paragraph why SARSA's greedy path in the cliff world is farther from the cliff than Q-learning's, even though both see the same kind of experience."
    SARSA's target uses the next action actually taken, which is random 10 percent of the time. Next to the cliff, one of
    the random moves (down) costs $-100$, so the value SARSA learns for edge squares includes that risk, about
    $0.1 \cdot \frac14 \cdot (-100) = -2.5$ per step spent on the edge, and paths one or two rows up look better.
    Q-learning's target uses the max over next actions, the value of acting greedily from there, which ignores its own
    future exploration; greedily, the edge is safe and shortest. Each learns the value of a different policy: SARSA of
    the epsilon-greedy one it follows, Q-learning of the greedy one.

??? question "6. Prove that subtracting a baseline b(s) from the return leaves the expected REINFORCE update unchanged. Does the baseline have to be a good estimate of the value?"
    For each state, $E_{a \sim \pi}[b(s)\nabla \log \pi(a \mid s)] = b(s)\sum_a \nabla\pi(a \mid s) = b(s)\nabla\sum_a \pi(a \mid s)
    = b(s)\nabla 1 = 0$, so the expected update is the same with or without it. The baseline can be any function of the
    state (not of the action), good or bad, and the update stays unbiased; a good estimate of the value reduces the
    variance most, which is why the learned value is used.

??? question "7. Derive the short-corridor value: with P(right) = p, write the Bellman equations for the three squares and show J(p) = (2p - 4)/(p(1 - p)). Check J(0.5) = -12."
    Squares 0, 1, 2; from 0 right goes to 1 and left stays; from 1 right goes to 0 and left goes to 2 (reversed); from 2
    right reaches the goal. $v_0 = -1 + p v_1 + (1-p) v_0$ gives $v_0 = v_1 - 1/p$. $v_2 = -1 + (1-p) v_1$.
    $v_1 = -1 + p v_0 + (1-p) v_2 = -1 + p v_1 - 1 + (1-p)(-1 + (1-p) v_1)$. Collect $v_1$:
    $v_1(1 - p - (1-p)^2) = -3 + p$, and $1 - p - (1-p)^2 = p(1-p)$, so $v_1 = (p - 3)/(p(1-p))$. Then
    $J = v_0 = v_1 - 1/p = (p - 3 - (1 - p))/(p(1-p)) = (2p - 4)/(p(1-p))$. At $p = 0.5$: $(-3)/0.25 = -12$. Setting the
    derivative to zero gives $p^2 - 4p + 2 = 0$, so $p = 2 - \sqrt2$.

??? question "8. Why does the optimal policy in the short corridor have to be stochastic, while every finite MDP has a deterministic optimal policy?"
    The theorem about deterministic optimal policies assumes the policy may depend on the state. Here the agent's
    observation is the same in every square, so it is choosing one action distribution for all squares at once: in
    effect a partially observable problem ([Chapter 14](14-Making-Decisions.md), 14.6). Both deterministic choices
    have value $-\infty$ (always right bounces between squares 0 and 1; always left never leaves 0), while any
    $0 < p < 1$ eventually finishes. Under partial observability, stochastic memoryless policies can beat every
    deterministic one.

??? question "9. Write the code: Thompson sampling with Beta(1, 1) priors on the same 200 bandits of 10 Bernoulli arms, for 20 000 pulls. Compare its regret with the table in 15.1."
    ```python
    import numpy as np

    K, STEPS, RUNS = 10, 20000, 200
    rng = np.random.default_rng(2002)
    probs = rng.uniform(0.2, 0.8, (RUNS, K))
    best, rows = probs.max(axis=1), np.arange(RUNS)
    wins, losses = np.ones((RUNS, K)), np.ones((RUNS, K))     # Beta(1, 1) priors
    regret = 0.0
    for t in range(STEPS):
        a = rng.beta(wins, losses).argmax(axis=1)             # sample a mean for every arm, pick the best sample
        r = rng.random(RUNS) < probs[rows, a]
        wins[rows, a] += r
        losses[rows, a] += ~r
        regret += np.mean(best - probs[rows, a])
        if t + 1 in (1000, 5000, 20000):
            print(f"Thompson sampling regret after {t + 1}: {regret:.1f}")
    ```
    Output:
    ```
    Thompson sampling regret after 1000: 48.4
    Thompson sampling regret after 5000: 85.1
    Thompson sampling regret after 20000: 120.6
    ```
    About 121 after 20 000 pulls, roughly a quarter of the best method in the table (502). The posterior samples explore
    an arm in proportion to the chance that it is the best, so clearly bad arms are dropped quickly.

??? question "10. Show that the checkpoint bonus of 15.7 cannot be written as gamma*Phi(s') - Phi(s) for any bounded potential Phi. (Hint: compare two endless trajectories from square 4.)"
    For a potential-based bonus, the proof of the theorem shows that the discounted sum of bonuses along any endless
    trajectory starting at $s_0$ is exactly $-\Phi(s_0)$ (the sum telescopes and $\gamma^T\Phi(s_T) \to 0$). So every
    endless trajectory from square 4 would collect the same total. Now compare two of them. Trajectory one steps
    4, 5, 4, 5, ... and collects the checkpoint bonus on every second step: $1 + \gamma^2 + \gamma^4 + \cdots =
    1/(1 - \gamma^2) = 10.26$. Trajectory two steps 4, 3, 4, 3, ... and never enters square 5: total 0. The totals differ,
    so no potential reproduces the bonus. The difference, a cycle with positive total bonus, is exactly what the
    agent exploited; potential-based bonuses can never create such a cycle.

## What you learned

- Reinforcement learning learns to act from rewards alone; it must balance exploration and exploitation, and regret
  measures the cost of learning. UCB1 achieves logarithmic regret by optimism; constant epsilon-greedy has linear regret.
- Monte Carlo learns from complete returns; TD learns from one reward and a bootstrapped estimate, usually faster,
  because it exploits the Markov property.
- Q-learning learns the optimal action values off-policy; SARSA learns the values of the policy it follows. The cliff
  shows the difference between the best policy and the best behaviour while exploring.
- Function approximation lets values generalise; linear on-policy TD converges, but the deadly triad can diverge. DQN
  made deep Q-learning work with experience replay and a target network.
- Policy gradients follow the gradient of expected return using only the policy's log-probabilities; baselines cut
  variance without bias; actor-critic and PPO are the practical forms, and they can learn stochastic policies.
- Model-based methods plan with learned models (Dyna); AlphaZero and MuZero combine learned values and policies with
  tree search.
- Agents optimise the reward as written: specification gaming is a property of the reward, and potential-based shaping
  is the provably safe way to add guidance.

**Next:** [Chapter 16](16-Natural-Language-Processing.md) turns to language: counting words, tagging and parsing
sentences, and the path from n-grams to transformers.

## Further reading

- R. S. Sutton and A. G. Barto, *Reinforcement Learning: An Introduction*, 2nd ed., 2018: the textbook, the source of
  the random walk, cliff, short corridor and Dyna maze examples.
- S. Russell and P. Norvig, *Artificial Intelligence: A Modern Approach*, 4th ed., 2020: chapter 22 (reinforcement
  learning).
- P. Auer, N. Cesa-Bianchi and P. Fischer, "Finite-time analysis of the multiarmed bandit problem", *Machine Learning*
  47, 2002; T. L. Lai and H. Robbins, "Asymptotically efficient adaptive allocation rules", *Advances in Applied
  Mathematics* 6, 1985; T. Lattimore and C. Szepesvári, *Bandit Algorithms*, 2020.
- W. R. Thompson, "On the likelihood that one unknown probability exceeds another in view of the evidence of two
  samples", *Biometrika* 25, 1933; S. Agrawal and N. Goyal, "Analysis of Thompson sampling for the multi-armed bandit
  problem", COLT 2012.
- R. S. Sutton, "Learning to predict by the methods of temporal differences", *Machine Learning* 3, 1988.
- C. J. C. H. Watkins, *Learning from Delayed Rewards*, PhD thesis, Cambridge, 1989; C. J. C. H. Watkins and P. Dayan,
  "Q-learning", *Machine Learning* 8, 1992; G. A. Rummery and M. Niranjan, "On-line Q-learning using connectionist
  systems", Cambridge technical report, 1994.
- J. N. Tsitsiklis and B. Van Roy, "An analysis of temporal-difference learning with function approximation", *IEEE
  Transactions on Automatic Control* 42, 1997; L. Baird, "Residual algorithms: reinforcement learning with function
  approximation", ICML 1995.
- V. Mnih et al., "Human-level control through deep reinforcement learning", *Nature* 518, 2015; L.-J. Lin,
  "Self-improving reactive agents based on reinforcement learning, planning and teaching", *Machine Learning* 8, 1992;
  H. van Hasselt, A. Guez and D. Silver, "Deep reinforcement learning with double Q-learning", AAAI 2016.
- A. G. Barto, R. S. Sutton and C. W. Anderson, "Neuronlike adaptive elements that can solve difficult learning control
  problems", *IEEE Transactions on Systems, Man, and Cybernetics* 13, 1983.
- R. J. Williams, "Simple statistical gradient-following algorithms for connectionist reinforcement learning",
  *Machine Learning* 8, 1992; R. S. Sutton, D. McAllester, S. Singh and Y. Mansour, "Policy gradient methods for
  reinforcement learning with function approximation", NeurIPS 2000.
- J. Schulman, S. Levine, P. Abbeel, M. Jordan and P. Moritz, "Trust region policy optimization", ICML 2015;
  J. Schulman, F. Wolski, P. Dhariwal, A. Radford and O. Klimov, "Proximal policy optimization algorithms", 2017.
- R. S. Sutton, "Integrated architectures for learning, planning, and reacting based on approximating dynamic
  programming", ICML 1990; A. W. Moore and C. G. Atkeson, "Prioritized sweeping", *Machine Learning* 13, 1993.
- D. Silver et al., "A general reinforcement learning algorithm that masters chess, shogi, and Go through self-play",
  *Science* 362, 2018; J. Schrittwieser et al., "Mastering Atari, Go, chess and shogi by planning with a learned model",
  *Nature* 588, 2020.
- A. Y. Ng, D. Harada and S. Russell, "Policy invariance under reward transformations: theory and application to reward
  shaping", ICML 1999; A. Y. Ng and S. Russell, "Algorithms for inverse reinforcement learning", ICML 2000.
- D. Amodei, C. Olah, J. Steinhardt, P. Christiano, J. Schulman and D. Mané, "Concrete problems in AI safety", 2016;
  J. Lehman et al., "The surprising creativity of digital evolution", *Artificial Life* 26, 2020; I. Popov et al.,
  "Data-efficient deep reinforcement learning for dexterous manipulation", 2017; P. Christiano et al., "Deep
  reinforcement learning from human preferences", NeurIPS 2017.
- P. Henderson et al., "Deep reinforcement learning that matters", AAAI 2018.
- On this site: [Chapter 14](14-Making-Decisions.md) (MDPs) and [Chapter 6](06-Games-and-Adversarial-Search.md)
  (MCTS, AlphaZero) of this book; [Machine learning, Chapter 5](../machine-learning/05-Optimization.md) (stochastic
  gradient methods, Adam) and [Chapter 15](../machine-learning/15-Neural-Networks-and-Backpropagation.md)
  (backpropagation).
