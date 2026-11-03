# 21. Where AI goes

*This book began with a question (what is intelligence, and can a machine have it?) and built, chapter by chapter,
the machinery that today's AI is made of: search, logic, probability, decisions, learning and language. This last
chapter looks forward. It answers the question: what can AI do now, what can it not do, and which problems are open?
You will draw an honest map of solved and unsolved problems, combine an unreliable learned proposer with an exact
verifier, train a perception model through a symbolic program it never sees the labels of, plan inside a learned world
model and watch its errors compound, learn from three examples with a learned prior, fight catastrophic forgetting,
and write the kind of proof checker that mathematics is beginning to trust. Everything here is labelled: what is
established, what is reported by one paper, and what is open.*

!!! abstract "In this chapter"
    **You will learn:**

    - an honest map of what AI systems do well, as reported in their papers, and where they still fail
    - why generate-and-verify works, with the success probability $1 - (1-p)^k$ derived and measured, and how
      neuro-symbolic systems join learned perception to exact reasoning, trained end to end from scratch
    - what common sense and world models are, and a proof that the error of an imagined rollout can grow geometrically
      with its length, measured on a pendulum
    - learning from little data with a learned prior (derived as a Bayesian posterior), and catastrophic forgetting with
      two remedies, rehearsal and elastic weight consolidation (derived from a Laplace approximation)
    - AI for science and mathematics: proof assistants and their small trusted kernels, AlphaFold, AlphaTensor,
      FunSearch and AlphaGeometry, as reported
    - the big open questions, labelled as open, and how to keep learning

    **You need:** the whole book, in particular [Chapter 3](03-Uninformed-Search.md) (search),
    [Chapter 9](09-First-Order-Logic.md) (logic and proof), [Chapter 12](12-Probabilistic-Reasoning.md)
    (probabilistic inference), [Chapter 15](15-Reinforcement-Learning.md) (model-based RL),
    [Chapter 17](17-Large-Language-Models.md) (language models) and [Chapter 20](20-Safe-and-Reliable-AI.md) (safety),
    and the [Machine learning book](../machine-learning/index.md), especially its
    [Chapter 23](../machine-learning/23-Where-Machine-Learning-Goes.md).

    **Levels:** 21.1 is beginner; 21.2 and 21.3 are intermediate to advanced; 21.4 is advanced; 21.5 is intermediate;
    21.6 is for everyone, and its questions are at the research frontier.

## 21.1 What is solved, what is not: an honest map

Headlines about AI swing between "solved" and "useless". Neither word helps. What, precisely, has been achieved, under
which conditions, and how do we know?

### Read results the way a scientist does

Three habits make the map honest.

1. **A result belongs to a setting.** "Superhuman at Go" means: on a 19×19 board, under the rules and time controls of
   the matches reported, against the opponents who played. It says nothing about a different board size or about
   another game, and studies have found weaknesses even in strong Go programs: Wang et al. (2023) trained adversarial
   policies that beat a top Go program by steering it into positions where it misjudged groups, although the
   adversary itself played poorly against humans.
2. **A result comes from a paper.** Numbers below are as reported by the authors, in the papers named. Company
   announcements, demonstrations and benchmarks without a published method are not evidence of the same strength.
3. **Benchmarks are proxies** (Chapter 20). A score shows a capability on the benchmark's distribution. Whether it
   transfers is a separate question.

### What has been achieved, as reported

| Area | Result, as reported | Paper |
|------|---------------------|-------|
| Checkers | Solved: perfect play from the opening is a draw | Schaeffer et al., *Science* 2007 |
| Chess | Deep Blue beat the world champion in a six-game match (1997); AlphaZero learned chess from self-play alone | Campbell et al. 2002; Silver et al., *Science* 2018 |
| Go | AlphaGo beat a top professional; AlphaGo Zero learned without human games | Silver et al., *Nature* 2016 and 2017 |
| Poker | Heads-up limit hold'em essentially solved; superhuman play at no-limit, two and six players | Bowling et al. 2015; Brown and Sandholm 2018, 2019 |
| Real-time strategy | Grandmaster level in StarCraft II | Vinyals et al., *Nature* 2019 |
| Protein structure | Predicted structures at CASP14 with a median backbone error of 0.96 Å, against 2.8 Å for the next best method | Jumper et al., *Nature* 2021 |
| Weather | Ten-day forecasts more accurate than a leading operational system on 90% of 1380 verification targets | Lam et al., *Science* 2023 |
| Images | Below the estimated human top-5 error on ImageNet classification | He et al. 2015 |
| Satisfiability | Industrial SAT instances with millions of variables solved routinely by CDCL solvers | Chapter 8; Marques-Silva and Sakallah 1999 |
| Language | Fluent text, translation, summarisation and few-shot learning of new tasks from prompts | Brown et al. 2020; Ouyang et al. 2022 |

Every row is a **narrow** setting: one game, one prediction task, one kind of input. Most share three features: the
goal can be measured exactly (win, energy, error), there is a lot of data or a perfect simulator, and the world does not
change under the system's feet. The rows also show a pattern this book has followed: the strongest systems combine
**search or reasoning** with **learning** (AlphaZero is MCTS plus networks; CDCL is search plus learned clauses; poker
programs are regret minimisation plus search).

### What is not achieved

These are well documented failures or gaps, not speculations:

- **Robustness under distribution shift.** Models fail on data that differs from their training data in ways a
  person would not notice (Chapter 20: shortcuts, adversarial examples, the confident ReLU far from its data).
- **Reliable multi-step reasoning and planning.** Language models make errors in long arithmetic and in planning tasks
  that classical planners solve exactly; their accuracy often drops when a problem is reworded or its names are
  changed (21.2).
- **Common sense and physical understanding** that people use without effort (21.3).
- **Learning from few examples, and learning continually** without forgetting (21.4).
- **Robotics in unstructured places.** Moravec's paradox (21.3): manipulation of everyday objects in a cluttered home is
  harder for machines than chess.
- **Verified reliability.** For most deployed neural systems no one can prove that the system meets a specification,
  and testing alone cannot show very low failure rates (Chapter 20).
- **Faithful explanation** of why a model produced an output (Chapter 20.5).

Autonomy on Mars is a good calibration of where the frontier is. Signals take roughly 3 to 22 minutes each way, so a
rover cannot be driven by joystick. Curiosity's AEGIS software picks rock targets for its laser spectrometer on its own
(Francis et al., *Science Robotics* 2017), and Perseverance's AutoNav plans and drives routes across terrain mapped
from its own stereo images (Verma et al., *Science Robotics* 2023). But the scientific goals, the daily plans and the
judgment of what matters still come from people on Earth. Narrow, verified, well-specified autonomy is real;
open-ended autonomy is not.

## 21.2 Reasoning and planning with learned models; neuro-symbolic AI

Learned models are fast, flexible and approximate. Search and logic are slow, rigid and exact. Each covers the
other's weakness. How do we combine them so that the result is both flexible and correct?

### Language models as planners

Planning (Chapter 10) asks for a sequence of actions that reaches a goal under exact rules. Valmeekam, Marquez, Sreedharan
and Kambhampati (2023), "On the planning abilities of large language models: a critical investigation", tested large
language models on Blocksworld and related domains from the planning competitions. Plans proposed directly by the
models were often invalid, and performance fell sharply when the action and object names were replaced by meaningless
ones, which a classical planner does not even notice. A language model trained to predict text has no built-in notion
of an action's preconditions, so a plausible-looking plan can be wrong at step 3. The lesson is not that learned models
are useless for planning, but that their output should be treated as a **proposal**.

### Generate and verify

Suppose a proposer produces a correct solution with probability $p$ per attempt, independently, and a **verifier**
checks solutions exactly. Draw $k$ proposals and keep any one that passes. Then

$$
P(\text{success}) = 1 - (1 - p)^k \ge 1 - e^{-pk},
$$

using $1 - p \le e^{-p}$. So $k \approx 3/p$ attempts give 95% success, and the expected number of attempts until the
first success is $1/p$ (a geometric distribution). A weak proposer becomes a strong solver as long as verification is
cheap and exact. This is how the old generate-and-test of Chapter 3 meets learning: the learned model replaces blind
generation, and the verifier keeps the answer correct.

The program makes this concrete on a small grid maze. The proposer is a cheap guesser that steps towards the goal 60%
of the time and randomly otherwise, with no knowledge of the walls; the verifier simulates each plan. Then we add
**feedback**: the verifier reports where the plan first fails, the valid prefix is kept, and only the rest is
re-proposed. Kambhampati and colleagues (2024) argued for this pattern under the name "LLM-Modulo": language models
generate candidates, and external sound verifiers, which can themselves be planners or simulators, accept, reject and
critique them.

```python
--8<-- "books/ai/ch21_generate_verify.py"
```

```
one proposed plan is valid with probability p = 0.0061 (estimated from 20000 samples)
    k    P(some valid plan among k): measured   formula 1-(1-p)^k
      1                           0.004       0.006
     10                           0.070       0.059
    100                           0.412       0.458
   1000                           1.000       0.998

with feedback (keep the checked prefix), 500 runs: median 11 proposer calls, 90th percentile 36, runs that gave up after 2000 calls: 0
```

A single plan is valid less than 1% of the time. With 1000 independent samples success is essentially certain, as the
formula predicts; the measured column wobbles around it because each row averages only 100 to 500 runs. With feedback,
the median run needs only 11 calls: the verifier's critique turns an exponentially small chance of getting a whole
plan right into a sequence of small steps, each of which is easy to get right. That is the general reason why exact
feedback is so valuable: it **decomposes** the problem.

<figure class="mars-fig" markdown="0">
<svg viewBox="0 0 520 290" role="img" aria-label="Success probability against number of samples k on a log scale from 1 to 1000. The curve 1 minus (1 minus p) to the k, with p equal to 0.0061, rises from near 0 to near 1, and the four measured points lie close to it.">
<line x1="60" y1="230" x2="490" y2="230" stroke="currentColor" stroke-width="1.2"/>
<line x1="60" y1="230" x2="60" y2="30" stroke="currentColor" stroke-width="1.2"/>
<text x="60" y="248" font-size="11" text-anchor="middle" fill="currentColor">1</text>
<text x="200" y="248" font-size="11" text-anchor="middle" fill="currentColor">10</text>
<text x="340" y="248" font-size="11" text-anchor="middle" fill="currentColor">100</text>
<text x="480" y="248" font-size="11" text-anchor="middle" fill="currentColor">1000</text>
<text x="275" y="272" font-size="12" text-anchor="middle" fill="currentColor">number of proposals k (log scale)</text>
<text x="52" y="234" font-size="11" text-anchor="end" fill="currentColor">0</text>
<text x="52" y="139" font-size="11" text-anchor="end" fill="currentColor">0.5</text>
<text x="52" y="44" font-size="11" text-anchor="end" fill="currentColor">1</text>
<line x1="60" y1="40" x2="490" y2="40" stroke="currentColor" stroke-width="0.5" stroke-dasharray="3 3"/>
<text x="20" y="135" font-size="12" text-anchor="middle" fill="currentColor" transform="rotate(-90 20 135)">P(a valid plan found)</text>
<polyline points="60.0,228.8 74.0,228.5 88.0,228.2 102.0,227.7 116.0,227.1 130.0,226.4 144.0,225.4 158.0,224.3 172.0,222.8 186.0,221.0 200.0,218.7 214.0,215.9 228.0,212.4 242.0,208.2 256.0,202.9 270.0,196.6 284.0,188.9 298.0,179.8 312.0,169.1 326.0,156.9 340.0,143.0 354.0,127.9 368.0,112.0 382.0,96.0 396.0,80.9 410.0,67.4 424.0,56.6 438.0,48.9 452.0,44.0 466.0,41.5 480.0,40.4" fill="none" stroke="#9cc9ea" stroke-width="2.5"/>
<circle cx="60" cy="229.2" r="5" fill="#eea66f" stroke="currentColor" stroke-width="1"/>
<circle cx="200" cy="216.7" r="5" fill="#eea66f" stroke="currentColor" stroke-width="1"/>
<circle cx="340" cy="151.7" r="5" fill="#eea66f" stroke="currentColor" stroke-width="1"/>
<circle cx="480" cy="40" r="5" fill="#eea66f" stroke="currentColor" stroke-width="1"/>
<text x="140" y="120" font-size="12" fill="currentColor">formula 1 − (1 − p)^k, p = 0.0061</text>
<line x1="112" y1="116" x2="132" y2="116" stroke="#9cc9ea" stroke-width="2.5"/>
<circle cx="122" cy="140" r="5" fill="#eea66f" stroke="currentColor" stroke-width="1"/>
<text x="144" y="144" font-size="12" fill="currentColor">measured</text>
</svg>
<figcaption>Figure 21.1. Generate and verify. With a perfect verifier, the chance that at least one of k independent proposals is valid is 1 − (1 − p)^k. A proposer that is right 0.6% of the time becomes a near-certain solver at about a thousand proposals; with the verifier's feedback (keep the checked prefix) the same proposer needs a median of 11.</figcaption>
</figure>

Published systems built on this pattern, with results as their papers report them:

- **AlphaCode** (Li et al., *Science* 2022) sampled very large numbers of candidate programs for competitive programming
  problems from a language model, filtered them by running them on the example tests in the problem statement,
  clustered the survivors, and submitted a few; in simulated participation in programming contests it ranked on
  average within the top 54.3% of human competitors.
- **FunSearch** (Romera-Paredes et al., *Nature* 2024) evolved programs with a language model as the mutation operator
  and an exact evaluator as the fitness function, and found cap sets in dimension 8 larger than previously known.
- **AlphaGeometry** (Trinh, Wu, Le, He and Luong, *Nature* 2024) paired a symbolic deduction engine for Euclidean
  geometry with a language model that proposes auxiliary constructions (new points and lines) when deduction stalls;
  it solved 25 of 30 olympiad geometry problems in the authors' benchmark. Every step of its proofs is checked by the
  symbolic engine.

What happens when there is no exact verifier? Then sampling can only vote. **Self-consistency** (Wang et al. 2023)
samples several chains of reasoning from a language model and takes the majority answer, which improved accuracy on
arithmetic benchmarks in their experiments. Voting helps only when correct answers agree with each other more often
than wrong ones do. An imperfect verifier also limits what search can buy: if it accepts a wrong answer with
probability $f$, the fraction of correct answers among accepted ones is $p / (p + (1-p) f)$, which is about one half
when $f = p$ (exercise 2). Searching harder against a flawed verifier is exactly the over-optimisation of
Chapter 20.6.

### Neuro-symbolic AI

**Neuro-symbolic** AI is the broad name for systems that combine learned (neural) components with symbolic ones
(logic, programs, search). Generate-and-verify is one form: the learned part proposes, the symbolic part checks. A
tighter form puts the symbolic part **inside** the learning loop, so that its exact structure shapes what is learned.

DeepProbLog (Manhaeve, Dumančić, Kimmig, Demeester and De Raedt 2018) introduced a test that is now standard: learn to
recognise handwritten digits when the only supervision is the **sum** of two digits. A network outputs probabilities
for each digit; a logic program states that the sum is the sum; exact probabilistic inference (Chapter 12) computes
the probability of the observed sum; and gradients flow back through the inference into the network. Our program does
exactly this with synthetic 8-dimensional "images" of digits. The model is a softmax classifier
$P(a \mid x) = \mathrm{softmax}(Wx + b)_a$, and the symbolic part is

$$
P(\text{sum} = s \mid x_1, x_2) = \sum_{a + c = s} P(a \mid x_1)\, P(c \mid x_2).
$$

The gradient of $\log P(\text{sum} = s)$ with respect to the first classifier's logits is $r_1 - P_1$, where $r_1(a)$ is
the **posterior** probability that the first digit is $a$ given the observed sum, $P_1(a) P_2(s - a) / P(s)$. (Proof: the
derivative of $\log \sum_a P_1(a) w_a$ with respect to logit $z_k$ is $\sum_a w_a P_1(a)(\mathbf{1}[a=k] - P_1(k)) / \sum_a P_1(a) w_a = r_1(k) - P_1(k)$,
using $\partial P_1(a)/\partial z_k = P_1(a)(\mathbf{1}[a=k] - P_1(k))$.) So the update moves the classifier towards
the digits that the logic says are consistent with the sum: it is the idea of expectation maximisation,
with the program as the model of how hidden digits produce what we see.

<figure class="mars-fig" markdown="0">
<svg viewBox="0 0 640 230" role="img" aria-label="Two images enter the same classifier, which outputs a probability for each digit. The two digit distributions enter an exact symbolic program, sum equals a plus c, which outputs the probability of the observed sum. The loss is minus log of that probability, and its gradient flows back through the program into the classifier.">
<rect x="20" y="40" width="80" height="50" rx="6" fill="#9cc9ea" fill-opacity="0.5" stroke="currentColor" stroke-width="1.2"/>
<text x="60" y="70" font-size="13" text-anchor="middle" fill="currentColor">image 1</text>
<rect x="20" y="140" width="80" height="50" rx="6" fill="#9cc9ea" fill-opacity="0.5" stroke="currentColor" stroke-width="1.2"/>
<text x="60" y="170" font-size="13" text-anchor="middle" fill="currentColor">image 2</text>
<rect x="140" y="40" width="110" height="50" rx="6" fill="#eea66f" fill-opacity="0.5" stroke="currentColor" stroke-width="1.2"/>
<text x="195" y="62" font-size="12" text-anchor="middle" fill="currentColor">classifier</text>
<text x="195" y="78" font-size="12" text-anchor="middle" fill="currentColor">(learned)</text>
<rect x="140" y="140" width="110" height="50" rx="6" fill="#eea66f" fill-opacity="0.5" stroke="currentColor" stroke-width="1.2"/>
<text x="195" y="162" font-size="12" text-anchor="middle" fill="currentColor">same classifier</text>
<text x="195" y="178" font-size="12" text-anchor="middle" fill="currentColor">(shared weights)</text>
<line x1="100" y1="65" x2="134" y2="65" stroke="currentColor" stroke-width="1.3"/>
<polygon points="140,65 130,60 130,70" fill="currentColor"/>
<line x1="100" y1="165" x2="134" y2="165" stroke="currentColor" stroke-width="1.3"/>
<polygon points="140,165 130,160 130,170" fill="currentColor"/>
<text x="300" y="56" font-size="12" text-anchor="middle" fill="currentColor">P(a | image 1)</text>
<text x="300" y="194" font-size="12" text-anchor="middle" fill="currentColor">P(c | image 2)</text>
<line x1="250" y1="65" x2="364" y2="105" stroke="currentColor" stroke-width="1.3"/>
<polygon points="370,107 359,108 362,99" fill="currentColor"/>
<line x1="250" y1="165" x2="364" y2="127" stroke="currentColor" stroke-width="1.3"/>
<polygon points="370,125 362,133 359,123" fill="currentColor"/>
<rect x="372" y="90" width="120" height="50" rx="6" fill="#7ccf9a" fill-opacity="0.5" stroke="currentColor" stroke-width="1.2"/>
<text x="432" y="112" font-size="12" text-anchor="middle" fill="currentColor">program</text>
<text x="432" y="128" font-size="11" text-anchor="middle" fill="currentColor">sum = a + c, exact</text>
<line x1="492" y1="115" x2="524" y2="115" stroke="currentColor" stroke-width="1.3"/>
<polygon points="530,115 520,110 520,120" fill="currentColor"/>
<text x="580" y="111" font-size="12" text-anchor="middle" fill="currentColor">P(observed</text>
<text x="580" y="127" font-size="12" text-anchor="middle" fill="currentColor">sum)</text>
<path d="M 580 140 C 580 222, 200 222, 195 196" fill="none" stroke="#eea66f" stroke-width="1.8" stroke-dasharray="6 4"/>
<polygon points="195,191 190,203 200,202" fill="#eea66f"/>
<text x="400" y="222" font-size="12" text-anchor="middle" fill="currentColor">gradient of log P(sum) flows back through the program</text>
</svg>
<figcaption>Figure 21.2. Learning through a symbolic program. The classifier is never told which digit an image shows. The exact program turns its two guesses into a probability for the sum that was observed, and maximising that probability teaches the classifier the digits.</figcaption>
</figure>

```python
--8<-- "books/ai/ch21_neurosymbolic.py"
```

```
epoch   0: mean log P(sum)  -2.803   sum accuracy 0.112   digit accuracy (never trained on digits) 0.164
epoch  10: mean log P(sum)  -2.254   sum accuracy 0.438   digit accuracy (never trained on digits) 0.698
epoch  30: mean log P(sum)  -0.754   sum accuracy 0.930   digit accuracy (never trained on digits) 0.964
epoch 100: mean log P(sum)  -0.315   sum accuracy 0.944   digit accuracy (never trained on digits) 0.971
epoch 300: mean log P(sum)  -0.202   sum accuracy 0.946   digit accuracy (never trained on digits) 0.974

confusion matrix of the learned digit classifier (rows: true digit, columns: predicted)
    0 163   0   0   0  12   2   0   0   0   2
    1   0 186   0   1   0   0   0   0   0   0
    2   1   0 174   0   0   0   0   0   0   0
    3   0   0   0 215   0   0   3   0   0   0
    4  16   0   0   0 206   9   0   0   0   0
    5   1   0   0   0   2 212   0   0   0   0
    6   0   0   0   2   0   0 206   0   0   0
    7   1   0   0   0   0   0   0 184   0   0
    8   0   0   0   0   0   0   0   0 211   0
    9   1   0   0   0   0   0   0   0   0 190
```

Without ever seeing a digit label, the classifier ends up naming the digits of new single images with 97% accuracy.
Why is this possible at all? Because the program constrains the hidden digits. A sum of 0 forces both digits to be 0,
and a sum of 18 forces both to be 9; those anchor the labels, and every other sum spreads information among a few
pairs. If the program were less informative (say the observation were only "is the sum even?"), the digit names could
be permuted without changing any prediction and no learner could recover them (exercise 6). The remaining confusions
(mostly 0 and 4, whose prototypes happen to be close in this synthetic data) are perception errors, not reasoning
errors.

Other neuro-symbolic lines include the neuro-symbolic concept learner (Mao, Gan, Kohli, Tenenbaum and Wu 2019), which
answers questions about images by executing programs over learned object representations, and the large body of work
on **program synthesis**, where the output of learning is itself a program that can be checked and reused. Open
questions are how to make the symbolic part learnable as well (here the program was written by hand), and how to keep
exact inference tractable when programs are large: exact inference in Bayesian networks is #P-hard in general
(Chapter 12).

## 21.3 Common sense, world models, embodied AI

"The trophy doesn't fit in the brown suitcase because it is too big. What is too big?" People answer at once: the
trophy. Change "big" to "small" and the answer flips to the suitcase. Nothing in the grammar decides it; knowledge of
how objects and containers work does. What is that knowledge, and how could a machine acquire it?

### Common sense

**Common sense** is the large body of everyday knowledge about objects, space, time, causes, people and intentions that
humans share and rarely say aloud. The trophy sentence is a **Winograd schema** (Levesque, Davis and Morgenstern 2012):
a pair of sentences differing in one word, where resolving a pronoun requires such knowledge. Levesque and colleagues
proposed it as a test that could not be passed by statistics alone. Language models later scored highly on the
original set; Sakaguchi, Le Bras, Bhagavatula and Choi (2020) showed that part of this came from statistical
regularities in the data and built WinoGrande, a larger set filtered adversarially to remove such cues, on which models
scored lower at the time. The pattern recurs: a benchmark meant to need understanding is solved, then found to contain
shortcuts, then rebuilt.

Symbolic AI tried to write common sense down. The Cyc project, started by Douglas Lenat in 1984, has encoded millions
of assertions in a logical language (Lenat 1995); ConceptNet (Speer, Chin and Havasi 2017) collects crowd-sourced
relations such as "a cup is used for drinking". These knowledge bases (Chapter 11) are precise but incomplete, and the
hard part, knowing which facts are relevant to a new situation, remained hard. Language models absorb a great deal of
common sense from text, but text under-reports the obvious (nobody writes that a cup falls when dropped), and models
still make errors no person would make. Whether common sense can be learned from text alone, from text plus images and
video, or only through acting in the world, is an open question.

### World models

Kenneth Craik (1943) suggested that minds carry "small-scale models" of reality, which they use to try out actions
before taking them. In AI, a **world model** is a learned model of how the environment responds to actions: given the
state and an action, predict the next state (and the reward). With a world model an agent can **plan in imagination**,
as model-based reinforcement learning does (Chapter 15: Dyna, MuZero). Ha and Schmidhuber (2018), "World models",
trained a generative model of a car-racing game's frames and a controller that could be trained inside the model's
"dream". The Dreamer agents (Hafner, Lillicrap, Ba and Norouzi 2020; Hafner et al. 2023 for DreamerV3) learn a compact
latent dynamics model and train their policy entirely on imagined rollouts; DreamerV3 reported collecting diamonds in
Minecraft from scratch without human data. LeCun (2022), in a position paper, argued that learning predictive world
models in an abstract representation space is the central missing piece for machine common sense; it is a proposal,
not a result.

The difficulty is that a model's errors **compound** when it is rolled forward.

**Proposition.** Suppose the true dynamics $s_{t+1} = f(s_t, a_t)$ is $L$-Lipschitz in the state
($\lVert f(s, a) - f(s', a) \rVert \le L \lVert s - s' \rVert$) and the learned model $\hat f$ has one-step error at most
$\varepsilon$ everywhere ($\lVert \hat f(s, a) - f(s, a) \rVert \le \varepsilon$). Then after $h$ imagined steps from the
same start under the same actions, the error satisfies

$$
e_h \le \varepsilon\,(1 + L + L^2 + \dots + L^{h-1}) = \varepsilon\,\frac{L^h - 1}{L - 1} \quad (L \ne 1).
$$

*Proof.* Let $s_t$ be the true and $\hat s_t$ the imagined states, $e_t = \lVert \hat s_t - s_t \rVert$, $e_0 = 0$. Then
$e_{t+1} = \lVert \hat f(\hat s_t, a_t) - f(s_t, a_t) \rVert \le \lVert \hat f(\hat s_t, a_t) - f(\hat s_t, a_t) \rVert + \lVert f(\hat s_t, a_t) - f(s_t, a_t) \rVert \le \varepsilon + L e_t$.
Unrolling the recursion $e_{t+1} \le \varepsilon + L e_t$ from $e_0 = 0$ gives the sum. $\square$

When $L > 1$ (unstable or chaotic dynamics) the bound grows geometrically; when $L < 1$ it stays below
$\varepsilon / (1 - L)$. The bound is a worst case; in practice errors also grow because the imagined states drift into
regions where the model was never trained, so $\varepsilon$ itself gets worse along the rollout. The program learns two
models of a damped pendulum from 2000 noisy random transitions: a linear model (the small-angle view of the world) and
one that has $\sin\theta$ and $\cos\theta$ among its features, so that it can represent the true dynamics. Then it uses
each to swing the pendulum up by **model-predictive control** (MPC): at every step imagine 400 random control
sequences with the model, execute the first control of the best one in the real world, and repeat.

```python
--8<-- "books/ai/ch21_world_model.py"
```

```
mean angle error (radians) after h steps of imagined rollout
    h   linear model   feature model
    1       0.010         0.0005
    5       0.140         0.0023
   10       0.462         0.0049
   20       0.884         0.0099
   40       1.246         0.0190

swing-up by planning in imagination (200 control steps); lower is better
   model used for planning   average (1 + cos theta) in the real world   final distance from upright
   true                           0.634                                   0.053 rad
   features                       0.649                                   0.012 rad
   linear                         1.347                                   2.200 rad
```

<figure class="mars-fig" markdown="0">
<svg viewBox="0 0 540 290" role="img" aria-label="Mean angle error against rollout length h from 0 to 40. The linear model's error grows from 0.01 at one step to 1.25 radians at 40 steps. The feature model's error stays near zero, below 0.02 radians.">
<line x1="60" y1="230" x2="520" y2="230" stroke="currentColor" stroke-width="1.2"/>
<line x1="60" y1="230" x2="60" y2="30" stroke="currentColor" stroke-width="1.2"/>
<text x="60" y="248" font-size="11" text-anchor="middle" fill="currentColor">0</text>
<text x="170" y="248" font-size="11" text-anchor="middle" fill="currentColor">10</text>
<text x="280" y="248" font-size="11" text-anchor="middle" fill="currentColor">20</text>
<text x="390" y="248" font-size="11" text-anchor="middle" fill="currentColor">30</text>
<text x="500" y="248" font-size="11" text-anchor="middle" fill="currentColor">40</text>
<text x="290" y="272" font-size="12" text-anchor="middle" fill="currentColor">imagined steps h</text>
<text x="52" y="234" font-size="11" text-anchor="end" fill="currentColor">0</text>
<text x="52" y="164" font-size="11" text-anchor="end" fill="currentColor">0.5</text>
<text x="52" y="94" font-size="11" text-anchor="end" fill="currentColor">1.0</text>
<line x1="56" y1="160" x2="64" y2="160" stroke="currentColor" stroke-width="1"/>
<line x1="56" y1="90" x2="64" y2="90" stroke="currentColor" stroke-width="1"/>
<text x="20" y="135" font-size="12" text-anchor="middle" fill="currentColor" transform="rotate(-90 20 135)">mean angle error (rad)</text>
<polyline points="60,230 71,228.6 115,210.4 170,165.3 280,106.2 500,55.6" fill="none" stroke="#eea66f" stroke-width="2.5"/>
<polyline points="60,230 71,229.9 115,229.7 170,229.3 280,228.6 500,227.3" fill="none" stroke="#7ccf9a" stroke-width="2.5"/>
<text x="150" y="95" font-size="12" fill="currentColor">linear model (small-angle view)</text>
<text x="330" y="214" font-size="12" fill="currentColor">model with sin and cos features</text>
</svg>
<figcaption>Figure 21.3. Compounding error. Both models are nearly right for one step (errors 0.010 and 0.0005 radians), but the linear model's error grows to more than a radian over 40 imagined steps, while the model with the right features stays close to the truth. Planning inherits the difference: MPC with the good model swings the pendulum up; with the linear model it never does.</figcaption>
</figure>

The one-step errors of the two models differ by a factor of 20, which looks harmless; after 40 steps the linear model
is off by more than a radian. And the planning table shows what matters for an agent: the planner using the feature
model performs as well as the planner given the true dynamics, while the planner using the linear model fails to get
the pendulum up at all. A world model is only as useful as its long-horizon predictions in the states the planner
visits, which is why practical model-based agents re-plan at every step (as MPC does), keep horizons short, and keep
collecting real data where the model is uncertain.

### Embodied AI and Moravec's paradox

Hans Moravec (1988) noted that it is comparatively easy to make computers play checkers at adult level, and very hard
to give them the perception and mobility of a one-year-old. Evolution spent far longer on sensing and moving than on
abstract thought, and the skills feel easy to us because we do not notice them. **Embodied AI** studies agents with
bodies, cameras and hands, acting in the physical world or in rich simulators. The obstacles are concrete: real data is
slow and costly to collect, simulators differ from reality (the "sim-to-real gap", narrowed by randomising the
simulator's physics and appearance during training, Tobin et al. 2017), and mistakes break things. Recent work trains
large models on many robots' data at once and connects them to vision-language models, such as RT-2 (Brohan et al.
2023), which reported that a model co-trained on web data and robot trajectories could follow instructions involving
objects and concepts absent from its robot data. Whether such models acquire the robust physical understanding that
common sense needs is open.

## 21.4 Learning from little data; continual learning

*Level: advanced.* A child who sees one giraffe recognises the next one. A deep network trained from scratch needs
thousands of examples per class, and if you train it on a second task it may forget the first. People learn quickly,
and keep learning for life without erasing what they knew. What makes that possible, and how far can machines go?

### Few-shot learning needs a prior

With $n$ examples and $d > n$ parameters, the data alone cannot determine the answer: infinitely many models fit
perfectly. Something else must choose among them, and that something is a **prior** in the Bayesian sense
([Machine learning, Chapter 12](../machine-learning/12-Probabilistic-Models.md)) or an **inductive bias** in general.
Lake, Salakhutdinov and Tenenbaum (2015) showed that a model built from a strong prior (characters are drawn by strokes,
composed by a program) learned new handwritten characters from a single example about as well as people did on their
Omniglot tasks. Lake, Ullman, Tenenbaum and Gershman (2017) argued that human-like learning needs such structured
priors, intuitive physics and psychology, and compositionality.

Where does a good prior come from, if not from a designer? From **previous tasks**. This is **learning to learn**, or
**meta-learning**. In its simplest form it is hierarchical Bayes: tasks in a family have weights
$w \sim \mathcal{N}(\mu, \tau^2 I)$, data within a task is $y = Xw + \text{noise}$ with variance $\sigma^2$. From earlier tasks
estimate $\mu$ and $\tau^2$; for a new task with few examples, use the posterior mean.

**Lemma.** With prior $w \sim \mathcal{N}(\mu, \tau^2 I)$ and likelihood $y \mid w \sim \mathcal{N}(Xw, \sigma^2 I)$, the
posterior mean is

$$
\hat w = \mu + \bigl(X^{\mathsf T} X + \lambda I\bigr)^{-1} X^{\mathsf T} (y - X\mu), \qquad \lambda = \frac{\sigma^2}{\tau^2}.
$$

*Proof.* The negative log posterior is, up to a constant,
$\frac{1}{2\sigma^2}\lVert y - Xw \rVert^2 + \frac{1}{2\tau^2}\lVert w - \mu \rVert^2$. Substitute $w = \mu + v$: it becomes
$\frac{1}{2\sigma^2}\lVert (y - X\mu) - Xv \rVert^2 + \frac{1}{2\tau^2}\lVert v \rVert^2$, a ridge regression for $v$ with
targets $y - X\mu$, whose minimiser is $v = (X^{\mathsf T}X + \lambda I)^{-1}X^{\mathsf T}(y - X\mu)$. For a Gaussian
posterior the minimiser of the negative log density is the mean. $\square$

The formula says: start from what tasks like this usually look like ($\mu$), and let the few examples correct it,
trusting them more when the noise $\sigma^2$ is small compared with the spread of tasks $\tau^2$. Plain ridge
regression is the special case $\mu = 0$, which shrinks towards a prior that has nothing to do with the task family.

Modern meta-learning does the same thing with neural networks. MAML (Finn, Abbeel and Levine 2017) learns an
initialisation from which a few gradient steps on a new task's examples give a good model; it can be read as learning
the $\mu$ of an implicit prior. Prototypical networks (Snell, Swersky and Zemel 2017) learn an embedding in which each
class is represented by the mean of its few examples. And large language models learn new tasks from a handful of
examples in the prompt, **in-context learning** (Brown et al. 2020), which is analysed in the
[Machine learning book, Chapter 23](../machine-learning/23-Where-Machine-Learning-Goes.md#233-in-context-learning-and-emergent-behaviour):
pretraining on an enormous range of text acts as the "earlier tasks".

### Continual learning and catastrophic forgetting

McCloskey and Cohen (1989) trained a network on one set of arithmetic facts and then another, and found that learning
the second wiped out the first: **catastrophic interference**, now usually called **catastrophic forgetting**. The
cause is simple. Gradient descent on task B moves the shared weights wherever B's loss goes down, with no term that
says "and keep A working". The tension between learning new things (plasticity) and keeping old ones (stability) is
the **stability-plasticity dilemma** (Grossberg 1980s). Three families of remedies:

1. **Rehearsal** (replay): keep a small memory of old examples and mix them into new training (Ratcliff 1990; Robins
   1995 used generated "pseudo-examples" instead of stored ones). It is simple and strong, but needs memory and
   assumes old data may be kept.
2. **Regularisation**: penalise changes to weights that mattered for old tasks. **Elastic weight consolidation**
   (EWC; Kirkpatrick et al. 2017) is the best-known.
3. **Architectural**: give each task its own parameters (new units or modules) while sharing the rest.

**EWC derived.** Bayes' rule over the two tasks gives
$\log p(\theta \mid A, B) = \log p(B \mid \theta) + \log p(\theta \mid A) + \text{const}$. The first term is task B's
log-likelihood. The second is everything we need to know about A, but it is intractable. Approximate it by a Gaussian
around the weights $\theta_A^\ast$ learned on A (a **Laplace approximation**), with precision given by the curvature at
$\theta_A^\ast$; EWC further approximates that curvature by the diagonal of the **Fisher information**
$F_i = \mathbb{E}\bigl[(\partial \log p(y \mid x, \theta) / \partial \theta_i)^2\bigr]$ at $\theta_A^\ast$. This gives the loss

$$
\mathcal{L}(\theta) = \mathcal{L}_B(\theta) + \frac{\lambda}{2} \sum_i F_i \bigl(\theta_i - \theta^\ast_{A,i}\bigr)^2.
$$

Weights to which task A's predictions are sensitive (large $F_i$) are held near their old values by stiff springs;
unimportant weights move freely. The strength $\lambda$ trades stability against plasticity.

```python
--8<-- "books/ai/ch21_continual.py"
```

```
(1) a new task, only 3 examples for 8 unknown weights: mean squared test error over 500 tasks
   no prior (least norm)      2.426
   ridge towards 0            2.532
   learned prior              0.250

(2) task A, then task B (a different rule; an input bit says which task); test accuracy
   method                         on A after A   on A after B   on B after B
   plain sequential training         0.974          0.649          0.972
   rehearsal (100 stored A items)    0.974          0.808          0.935
   EWC, lambda 20                    0.974          0.804          0.953
   EWC, lambda 200                   0.974          0.938          0.890
   both tasks together (reference)      -            0.918          0.924
```

Part 1 shows the value of a learned prior: with 3 examples for 8 unknown weights, least squares and ridge towards zero
have errors around 2.5, ten times worse than the posterior mean with the prior learned from 50 earlier tasks (0.25).
Ridge towards zero is even slightly worse than no prior: a prior from the wrong family can hurt. Part 2 shows
forgetting: after training on task B, accuracy on task A falls from 0.974 to 0.649. Rehearsal with only 100 stored
examples brings it back to 0.808; EWC with a weak spring gives about the same, and with a stiff one ($\lambda = 200$)
it keeps A at 0.938 but learns B less well (0.890 against 0.972): the stability-plasticity trade-off as a number. In
this run EWC with the stiff spring even beats the network trained on both tasks at once for the same number of epochs
on task A, a reminder that the reference run was itself trained only briefly. Continual learning over long
sequences of tasks, without storing old data and without knowing when one task ends and the next begins, remains an
open problem; benchmarks and surveys (for example De Lange et al. 2022) show no method that solves it in general.

## 21.5 AI for science and mathematics

A mathematical proof can be thousands of pages long, and some have contained errors that went unnoticed for years. A
protein's shape decides what it does, but measuring it can take months of laboratory work. Can AI help, and how can we
trust the help?

### Proof assistants: checking is easy, finding is hard

A **proof assistant** (interactive theorem prover) is a program in which mathematics is written in a formal language
and every step is checked by a small trusted **kernel**. Automath (de Bruijn, from 1967) was the first; Mizar, HOL
Light, Isabelle, Coq (now called Rocq) and Lean (de Moura and colleagues, from 2013) followed. De Bruijn's principle
explains why they are trusted: the kernel that checks proofs should be small enough to be inspected by hand, so that
however large or clever the program that *produced* the proof, only the kernel needs to be believed. Major results have
been checked this way:

- the **four colour theorem**, formalised in Coq by Gonthier (2008), removing doubts about its computer-assisted proof;
- the **Feit-Thompson odd order theorem**, a 255-page group-theory proof, formalised by Gonthier and colleagues (2013);
- the **Kepler conjecture** on sphere packing, formally verified by the Flyspeck project (Hales et al. 2017), after
  referees had said they were only 99% certain of the original computer-assisted proof;
- a central theorem of Clausen and Scholze's condensed mathematics, checked in Lean in 2022 by a community project
  (the Liquid Tensor Experiment) that Scholze had challenged the community to undertake.

The program below is a toy kernel for implicational logic: two axiom schemas and modus ponens, exactly the Hilbert
system whose proofs are discussed in [Chapter 9](09-First-Order-Logic.md) and in the
[Logic book](https://math.akadian.ca/books/logic/). It checks a five-line proof of $p \to p$ in microseconds, and
rejects two broken ones with the precise reason. Then it tries to *find* proofs by blind forward search: build all
instances of the axioms from small formulas and close them under modus ponens.

```python
--8<-- "books/ai/ch21_proof_check.py"
```

```
A proof of p -> p:
   1. ((p -> ((p -> p) -> p)) -> ((p -> (p -> p)) -> (p -> p))) A2
   2. (p -> ((p -> p) -> p))                           A1
   3. ((p -> (p -> p)) -> (p -> p))                    MP from 2 and 1
   4. (p -> (p -> p))                                  A1
   5. (p -> p)                                         MP from 4 and 3
   checker: proof accepted (14 microseconds)
Same proof with lines 1 and 2 swapped in the citation of line 3: line 3: line 2 is not (line 1) -> (line 3)
A 'proof' that calls p -> p an instance of A2: line 2 is not an instance of A2

Blind search for p -> p (building blocks: formulas in p of size 1, 3, 5):
   4 building blocks, 80 axiom instances
   after round 1 of modus ponens: 100 theorems; goal found: False
   after round 2 of modus ponens: 106 theorems; goal found: True
Blind search for ((p -> q) -> ((q -> r) -> (p -> r))) (building blocks: formulas in p, q, r of size 1 and 3):
   12 building blocks, 1872 axiom instances
   after round 1 of modus ponens: 2016 theorems; goal found: False
   after round 2 of modus ponens: 2034 theorems; goal found: False
   after round 3 of modus ponens: 2064 theorems; goal found: False
The same with building blocks of size 1, 3 and 5:
   66 building blocks, 291852 axiom instances
   after round 1 of modus ponens: 296820 theorems; goal found: False
   after round 2 of modus ponens: 297504 theorems; goal found: False
   after round 3 of modus ponens: 297804 theorems; goal found: False
   after round 4 of modus ponens: 298362 theorems; goal found: False
(2.1 s)
```

The asymmetry is the point. Checking the proof took microseconds. Finding $p \to p$ blindly was easy only because it is
tiny. For the hypothetical syllogism $(p \to q) \to ((q \to r) \to (p \to r))$, which is a theorem of this system (it is
derivable, for example by way of the deduction theorem for this system), blind search generated almost 300 000 theorems and did not find it:
the proof needs axiom instances built from formulas larger than those allowed, and allowing them multiplies the count
again. Finding proofs is a search problem in an infinite, explosively branching space; that is where learning helps,
by suggesting which step to try next, while the kernel guarantees that whatever is found is correct. This is
generate-and-verify (21.2) with a perfect verifier. Language models trained on formal mathematics have been used this
way since GPT-f (Polu and Sutskever 2020), which found proofs in the Metamath system that were accepted into its main
library. The library of formalised mathematics in Lean, mathlib (The mathlib Community 2020), gives such systems both
training data and a growing list of targets.

### AlphaFold and AI for the natural sciences

Proteins are chains of amino acids that fold into three-dimensional shapes. Predicting the shape from the sequence had
been a central problem in biology for fifty years, with a community benchmark, CASP, held every two years on newly
measured structures kept secret until the predictions were in. At CASP14 in 2020, AlphaFold (Jumper et al., *Nature*
2021) predicted structures with a median backbone error of 0.96 Å (r.m.s.d. at 95% coverage), against 2.8 Å for the
next best method; an ångström is roughly the width of an atom. The network combines attention over aligned sequences of
related proteins (evolution leaves traces of which residues touch) with a module that refines 3-D coordinates, and was
trained on structures from the Protein Data Bank. Its predictions were released for very large numbers of proteins,
and the work was recognised by the 2024 Nobel Prize in Chemistry (shared with David Baker for computational protein
design). What it does not do is also clear from the papers: it predicts a static structure, not the motion of the
protein or how it binds every partner, and its confidence measure must be read carefully for regions it is unsure of.

More reported results, each from its paper:

- **Matrix multiplication** (AlphaTensor, Fawzi et al., *Nature* 2022): treating the search for multiplication
  algorithms as a single-player game with reinforcement learning, it found, among others, a way to multiply 4×4
  matrices with entries modulo 2 using 47 multiplications instead of the 49 of Strassen's method applied twice. It is a
  search over an exactly checkable space: every algorithm found is verified by expanding its formulas.
- **Combinatorics** (FunSearch, above): new cap set constructions, with every program evaluated exactly.
- **Pure mathematics with people** (Davies et al., *Nature* 2021): machine learning suggested relationships between
  invariants of knots and a conjecture in representation theory, which mathematicians then proved.
- **Weather** (GraphCast, Lam et al., *Science* 2023), above.

The [Machine learning book, Chapter 23](../machine-learning/23-Where-Machine-Learning-Goes.md#235-graph-neural-networks-geometric-deep-learning-and-ml-for-science)
explains the graph networks behind several of these. A common thread runs through the successes: an exact or trusted
check exists (a kernel, an evaluator, a held-out experimental structure), the problem has a precise objective, and
there is either a lot of data or a cheap simulator. Where those conditions fail, such as in proposing new scientific
theories or experiments whose value is not yet measurable, AI's role is so far much more limited.

## 21.6 The big open questions; how to keep learning

Here are questions nobody can answer yet. Each is labelled **open**: there are opinions, arguments and partial
results, but no established answer. Treat confident claims in either direction with suspicion.

1. **Is scale enough?** *Open.* Loss falls predictably as models, data and compute grow
   ([Machine learning, Chapter 23](../machine-learning/23-Where-Machine-Learning-Goes.md#231-scaling-laws)). Whether
   continued scaling of current methods yields reliable reasoning, planning and robustness, or whether new ideas are
   needed (search, world models, explicit structure), is debated. The successes of 21.1 suggest that combining learning
   with search and verification is part of any answer.
2. **Reasoning with guarantees.** *Open.* Can learned systems reason over many steps with the reliability of a
   theorem prover or a planner, or only when coupled to one (21.2)? How do we get exact answers from approximate
   components, and know when we have them?
3. **World models and causality.** *Open.* Can an agent learn, from observation and interaction, a model of the world
   good enough to plan far ahead and to answer counterfactual questions ("what would have happened if...")? Pearl's
   ladder of causation (Chapter 12.6) says observation alone cannot answer interventional questions without assumptions;
   what assumptions are enough in practice is open.
4. **Learning like people.** *Open.* Few examples, lifelong learning without forgetting, transfer to new situations,
   learning from explanation rather than from labels (21.4).
5. **Generalisation theory.** *Open.* Why do large networks that can memorise their training data generalise? Classical
   learning theory does not explain it fully ([Machine learning, Chapter 21](../machine-learning/21-Learning-Theory.md#216-what-theory-does-not-explain)).
6. **Alignment and oversight.** *Open.* How to specify, learn and verify objectives, and how to supervise systems on
   tasks their supervisors cannot evaluate ([Chapter 20.6](20-Safe-and-Reliable-AI.md#206-alignment-as-a-research-problem-learning-objectives-from-humans)).
7. **Interpretability at scale.** *Open.* Can we explain, faithfully and in human terms, what a network with billions
   of parameters computes, and check that the explanation is right
   ([Machine learning, Chapter 23.4](../machine-learning/23-Where-Machine-Learning-Goes.md#234-mechanistic-interpretability))?
8. **Measuring intelligence.** *Open.* What should we measure? Chollet (2019), "On the measure of intelligence", argued
   that skill on a task is not intelligence, which is rather the efficiency with which new skills are acquired from
   little experience, and proposed the ARC benchmark of abstract visual puzzles to test it. How to evaluate general
   ability without the benchmark itself becoming a target is unsolved (Chapter 20.7).
9. **Limits from computation.** *Partly known.* Some limits are theorems, not open questions: no algorithm decides
   first-order validity (Chapter 9), planning in general is PSPACE-complete, exact inference in Bayesian networks is
   #P-hard, and if P is not NP (itself open: [Algorithms book, Chapter 25](../algorithms/25-Where-Algorithms-Go.md))
   no AI method solves NP-hard problems efficiently in the worst case. What these worst-case limits mean for the
   problems that actually arise is open.
10. **Embodiment.** *Open.* How much of intelligence requires a body, sensors and action in the physical world, and can
    robots acquire everyday physical competence at the rate learning systems acquire language (21.3)?

### How to keep learning

This book has given you the core: agents, search, logic, probability, decisions, learning, language, perception,
many agents, safety. To go further:

- **Read the textbooks.** Russell and Norvig's *Artificial Intelligence: A Modern Approach* (4th ed. 2020) for breadth;
  Sutton and Barto's *Reinforcement Learning* (2nd ed. 2018); Koller and Friedman's *Probabilistic Graphical Models*
  (2009); Ghallab, Nau and Traverso's *Automated Planning and Acting* (2016); Jurafsky and Martin's *Speech and Language
  Processing* (3rd ed. draft); Murphy's *Probabilistic Machine Learning* (2022, 2023).
- **Read papers, and reproduce them.** The original papers are named in each chapter. Most are freely available on
  arXiv or in the open proceedings of NeurIPS, ICML, ICLR, AAAI and IJCAI, and the journals *Artificial Intelligence*
  and *Journal of Artificial Intelligence Research*. Reimplementing a small version of a result, as every chapter here
  did, teaches more than reading ten summaries, and it is how you discover what the paper left out.
- **Check claims.** Ask of any result: in which setting, measured how, compared with what, and reported where? The
  habits of 21.1 and Chapter 20.7 apply to everything you read, this book included.
- **Build.** Pick a small problem you care about (a puzzle, a game, a route between places, a dataset of your own) and
  solve it end to end with the tools of this book: a search, a model, an evaluation that is honest about its errors.

The [Algorithms book](../algorithms/index.md) and the [Machine learning book](../machine-learning/index.md) on this site
continue the two threads this book has drawn on most, and the [math books](https://math.akadian.ca/books/) give the
foundations underneath all three.

## Check yourself

??? question "1. A proposer is right with probability p = 0.01 per attempt and the verifier is perfect. How many independent attempts give at least 95% success, and what is the expected number of attempts until the first success?"
    We need $1 - 0.99^k \ge 0.95$, so $k \ge \ln 0.05 / \ln 0.99 = 298.07$: 299 attempts. The approximation $k \approx 3/p = 300$
    is almost exact. The number of attempts until the first success is geometric with mean $1/p = 100$. The 95% figure is
    three times the mean because the geometric distribution has a long tail.

??? question "2. Now the verifier is imperfect: it accepts a wrong answer with probability f = 0.01 (and always accepts right ones). With p = 0.01, what fraction of accepted answers is correct? What does this mean for searching harder?"
    By Bayes' rule, $P(\text{correct} \mid \text{accepted}) = p / (p + (1-p)f) = 0.01 / (0.01 + 0.0099) \approx 0.503$. Half the
    accepted answers are wrong. Drawing more samples does not improve this ratio, because each accepted sample is
    correct with the same probability; it only finds more accepted samples. Precision of the verifier, not the number of
    samples, is the bottleneck. Remedies: make the verifier stricter (lower $f$), combine independent verifiers, or vote
    among accepted answers if wrong ones tend to disagree.

??? question "3. Prove the compounding-error bound for L = 1, and compute the bound for ε = 0.01, L = 1.1, h = 40."
    The recursion $e_{t+1} \le \varepsilon + L e_t$ with $L = 1$ gives $e_h \le h\varepsilon$ by induction ($e_0 = 0$; if
    $e_t \le t\varepsilon$ then $e_{t+1} \le \varepsilon + t\varepsilon$): linear growth. For $L = 1.1$:
    $e_{40} \le 0.01 \times (1.1^{40} - 1)/0.1 = 0.1 \times (45.26 - 1) \approx 4.43$, more than 400 times the one-step error.
    A model that is excellent for one step can be useless for 40.

??? question "4. A one-parameter task family has prior w ~ N(2, 0.04) and noise variance 0.09. One example has x = 1 and y = 3. Compute the posterior mean, and compare it with least squares and with ridge towards 0."
    In one dimension the lemma gives
    $\hat w = (\mu/\tau^2 + xy/\sigma^2)/(1/\tau^2 + x^2/\sigma^2) = (50 + 33.33)/(25 + 11.11) \approx 2.31$.
    Least squares gives $y/x = 3$, ignoring the family; ridge towards 0 with the same $\lambda = 2.25$ gives
    $3/(1 + 2.25) \approx 0.92$, pulled towards a value no task in the family has. The posterior moves from the family's typical
    value 2 towards the data, by an amount set by how noisy one example is compared with how much tasks differ.

??? question "5. Derive the EWC penalty from a Laplace approximation, and say what happens as λ grows very large and as it goes to 0."
    $\log p(\theta \mid A)$ has a maximum at $\theta_A^\ast$, so its Taylor expansion there has no linear term:
    $\log p(\theta \mid A) \approx \log p(\theta_A^\ast \mid A) - \tfrac12 (\theta - \theta_A^\ast)^{\mathsf T} H (\theta - \theta_A^\ast)$, with $H$ the
    negative Hessian. EWC replaces $H$ by $\lambda \mathrm{diag}(F)$, the diagonal Fisher information (which equals the
    expected negative Hessian of the log-likelihood for a well-specified model), giving the penalty
    $\tfrac{\lambda}{2}\sum_i F_i (\theta_i - \theta_{A,i}^\ast)^2$. As $\lambda \to \infty$ the important weights freeze and B can be
    learned only with the unimportant ones (B's accuracy falls, as in the program: 0.890 at $\lambda = 200$). As
    $\lambda \to 0$ the penalty vanishes and we are back to plain sequential training and forgetting (0.649).

??? question "6. Write code: in the digit-sum task, count how many digit pairs give each sum. Then explain why digits can be learned from sums but not from 'is the sum even?'."
    ```python
    from collections import Counter
    c = Counter(a + b for a in range(10) for b in range(10))
    print([c[s] for s in range(19)])
    # [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1]
    ```
    Sums 0 and 18 each have a single pair, (0, 0) and (9, 9), so they fix those two digits; sum 1 then forces the pair
    {0, 1}, and so on: the labels are identifiable. With only parity, swapping the names of any two even digits (or of
    any two odd digits) leaves every observation's probability unchanged, so infinitely many labellings explain the data
    equally well and no learner can tell them apart. Learning through a program works only when the program makes the
    hidden variables identifiable.

??? question "7. Write code: solve 8 queens by generate-and-test with a random proposer (a random permutation: one queen per row and column) and an exact checker of the diagonals. Estimate the expected number of proposals and compare with theory."
    ```python
    import random
    rng = random.Random(0)
    def ok(perm):                      # queen in row i sits in column perm[i]
        return all(abs(perm[i] - perm[j]) != j - i for i in range(8) for j in range(i + 1, 8))
    counts = []
    for _ in range(2000):
        n = 0
        while True:
            n += 1
            perm = list(range(8)); rng.shuffle(perm)
            if ok(perm):
                break
        counts.append(n)
    print(sum(counts) / len(counts))   # 443.3
    ```
    There are $8! = 40320$ permutations, of which 92 are solutions, so $p = 92/40320 \approx 0.00228$ and the expected number of
    proposals is $1/p \approx 438$; the simulation gives 443. A better proposer (backtracking, Chapter 7, or min-conflicts)
    exploits the structure that blind generation ignores.

??? question "8. Why was the Winograd schema thought to need common sense, and how did WinoGrande try to repair the benchmark?"
    In a Winograd pair the two sentences differ in one word ("big" and "small"), and the correct referent of the pronoun
    flips; grammar and word co-occurrence are the same in both, so in principle only knowledge about the situation
    decides. In practice, individual items had statistical cues (some word pairs co-occur with one answer), and a model
    could score well without the knowledge. WinoGrande built a much larger set and filtered it with an algorithm that
    removes items a simple model can solve from such cues (adversarial filtering), so that the remaining items are harder
    to solve by association. The lesson is general: a benchmark measures what it measures, and shortcuts must be looked
    for actively (Chapter 20).

??? question "9. Why is a proof checked by a proof assistant's kernel more trustworthy than the output of the (possibly AI) system that found it? What could still be wrong?"
    The kernel is small and simple, checks every step against a few fixed rules, and has been inspected by many people
    (de Bruijn's principle); the search system can be huge, heuristic and opaque, but if it is wrong the kernel rejects
    the proof. What can still be wrong: the formal statement may not say what the mathematician meant (a mistranslation of
    the theorem into the formal language), the axioms or definitions in the library may be inconsistent with the intended
    mathematics, or the kernel, the compiler or the hardware may have a bug, which is why some systems have several
    independent checkers.

??? question "10. AlphaTensor found a 47-multiplication scheme for 4×4 matrices over arithmetic modulo 2. Applied recursively to large matrices, what exponent does it give, and how does it compare with Strassen's?"
    Splitting an $n \times n$ matrix into $4 \times 4$ blocks and using 47 block multiplications gives $T(n) = 47\,T(n/4) + O(n^2)$,
    so $T(n) = O(n^{\log_4 47}) = O(n^{2.777})$. Strassen's 7 multiplications for $2 \times 2$ gives $\log_2 7 \approx 2.807$, and
    49 for $4 \times 4$ (Strassen twice) gives $\log_4 49 = \log_2 7$, the same. So the new scheme gives a slightly smaller
    exponent, but only for arithmetic modulo 2, and still far above the best known theoretical exponents (around 2.37,
    see the [Algorithms book, Chapter 25](../algorithms/25-Where-Algorithms-Go.md)), which are not practical.

??? question "11. Pick one of the open questions of 21.6 and write down: one result that is established, one claim that is only argued, and one experiment that would help settle it."
    Example for question 1 (is scale enough?). Established: for the model families studied, test loss falls as a power law
    in model size, data and compute over many orders of magnitude (scaling-law papers, Machine learning Chapter 23).
    Argued, not established: that continued scaling alone will give reliable planning. An experiment: take planning
    problems with exact verifiers (as in 21.2), generate unseen instances whose names and surface form are changed, and
    measure how the fraction of valid plans changes with model scale with and without an external verifier; a claim about
    reasoning should survive renaming and new instances. Any answer to this exercise is good if it separates the three
    categories honestly.

## What you learned

- AI's reported successes are narrow and specific: games, protein structure, weather, SAT, language fluency; most
  combine learning with search or exact checking, and come with measurable goals and plentiful data or simulation.
  Robustness, reliable reasoning, common sense, data efficiency, continual learning and verified reliability are not
  achieved.
- A proposer right with probability $p$ plus an exact verifier succeeds with probability $1 - (1-p)^k$ in $k$ tries, and
  verifier feedback can turn an exponentially rare success into a few steps; imperfect verifiers cap what search can
  buy.
- Neuro-symbolic learning trains perception through an exact program: from sums alone, a classifier learned to name
  digits with 97% accuracy, because the program made them identifiable.
- World models allow planning in imagination, but one-step errors compound, up to geometrically in the rollout length;
  the right model structure made the difference between swinging a pendulum up and failing.
- Learning from few examples needs a prior; learning the prior from earlier tasks (hierarchical Bayes, meta-learning)
  cut the error tenfold. Sequential training forgets; rehearsal and EWC (a Laplace approximation of the old posterior)
  trade stability against plasticity.
- Proof assistants make mathematics checkable by a small kernel; AI helps find proofs and constructions where an exact
  check exists, as in AlphaGeometry, FunSearch, AlphaTensor and, for structure prediction, AlphaFold.
- The big questions (scale, reasoning, causality, human-like learning, generalisation theory, alignment,
  interpretability, measurement, embodiment) are open; keep reading, reproducing and checking.

**Next:** this is the last chapter. Return to the [book's contents](index.md) to revisit any chapter, or continue with
the [Machine learning book](../machine-learning/index.md) and the [Algorithms book](../algorithms/index.md).

## Further reading

- S. Russell and P. Norvig, *Artificial Intelligence: A Modern Approach*, 4th ed., 2020: chapter 28 (the future of AI).
- H. Moravec, *Mind Children*, 1988; K. Craik, *The Nature of Explanation*, 1943; B. M. Lake, T. D. Ullman,
  J. B. Tenenbaum and S. J. Gershman, "Building machines that learn and think like people", *Behavioral and Brain
  Sciences* 40, 2017; F. Chollet, "On the measure of intelligence", 2019.
- K. Valmeekam, M. Marquez, S. Sreedharan and S. Kambhampati, "On the planning abilities of large language models: a
  critical investigation", NeurIPS 2023; S. Kambhampati and colleagues, "LLMs can't plan, but can help planning in
  LLM-modulo frameworks", ICML 2024; X. Wang and colleagues, "Self-consistency improves chain of thought reasoning in
  language models", ICLR 2023.
- Y. Li and colleagues, "Competition-level code generation with AlphaCode", *Science* 378, 2022; B. Romera-Paredes and
  colleagues, "Mathematical discoveries from program search with large language models", *Nature* 625, 2024;
  T. H. Trinh, Y. Wu, Q. V. Le, H. He and T. Luong, "Solving olympiad geometry without human demonstrations", *Nature*
  625, 2024.
- R. Manhaeve, S. Dumančić, A. Kimmig, T. Demeester and L. De Raedt, "DeepProbLog: neural probabilistic logic
  programming", NeurIPS 2018; J. Mao, C. Gan, P. Kohli, J. B. Tenenbaum and J. Wu, "The neuro-symbolic concept learner",
  ICLR 2019.
- H. J. Levesque, E. Davis and L. Morgenstern, "The Winograd schema challenge", KR 2012; K. Sakaguchi, R. Le Bras,
  C. Bhagavatula and Y. Choi, "WinoGrande: an adversarial Winograd schema challenge at scale", AAAI 2020; D. B. Lenat,
  "CYC: a large-scale investment in knowledge infrastructure", *Communications of the ACM* 38, 1995.
- D. Ha and J. Schmidhuber, "World models", 2018; D. Hafner, T. Lillicrap, J. Ba and M. Norouzi, "Dream to control:
  learning behaviors by latent imagination", ICLR 2020; D. Hafner and colleagues, "Mastering diverse domains through
  world models", 2023; Y. LeCun, "A path towards autonomous machine intelligence", 2022; A. Brohan and colleagues, "RT-2:
  vision-language-action models transfer web knowledge to robotic control", 2023.
- B. M. Lake, R. Salakhutdinov and J. B. Tenenbaum, "Human-level concept learning through probabilistic program
  induction", *Science* 350, 2015; C. Finn, P. Abbeel and S. Levine, "Model-agnostic meta-learning for fast adaptation of
  deep networks", ICML 2017; M. McCloskey and N. J. Cohen, "Catastrophic interference in connectionist networks", 1989;
  J. Kirkpatrick and colleagues, "Overcoming catastrophic forgetting in neural networks", *PNAS* 114, 2017; M. De Lange
  and colleagues, "A continual learning survey: defying forgetting in classification tasks", *IEEE TPAMI* 44, 2022.
- G. Gonthier, "Formal proof: the four-color theorem", *Notices of the AMS* 55, 2008; T. Hales and colleagues, "A formal
  proof of the Kepler conjecture", *Forum of Mathematics, Pi* 5, 2017; The mathlib Community, "The Lean mathematical
  library", CPP 2020; S. Polu and I. Sutskever, "Generative language modeling for automated theorem proving", 2020.
- J. Jumper and colleagues, "Highly accurate protein structure prediction with AlphaFold", *Nature* 596, 2021; A. Fawzi
  and colleagues, "Discovering faster matrix multiplication algorithms with reinforcement learning", *Nature* 610, 2022;
  A. Davies and colleagues, "Advancing mathematics by guiding human intuition with AI", *Nature* 600, 2021; R. Lam and
  colleagues, "Learning skillful medium-range global weather forecasting", *Science* 382, 2023.
- T. Wang and colleagues, "Adversarial policies beat superhuman Go AIs", ICML 2023; T. Francis and colleagues, "AEGIS
  autonomous targeting for ChemCam on Mars Science Laboratory", *Science Robotics* 2, 2017; V. Verma and colleagues,
  "Autonomous robotics is driving Perseverance rover's progress on Mars", *Science Robotics* 8, 2023.
- On this site: the [Machine learning book, Chapter 23](../machine-learning/23-Where-Machine-Learning-Goes.md), the
  [Algorithms book, Chapter 25](../algorithms/25-Where-Algorithms-Go.md), [Chapter 20](20-Safe-and-Reliable-AI.md) of
  this book, and the [math books](https://math.akadian.ca/books/).
