# 20. Safe and reliable AI, technically

*Every agent in this book optimises something: a path cost, a utility, a reward, a loss. When the objective says
exactly what we want and the world at test time is the world we trained in, optimising harder is simply better. In
practice neither holds. The objective is a proxy written by a person, and the world shifts. This chapter answers the
question: how do AI systems fail, and what technical tools let us find, measure, prevent and understand those failures?
You will watch an agent game a reward, a classifier learn a shortcut, a network fall to adversarial inputs, prove
robustness with a verifier you build yourself, calibrate confidence and wrap predictions in sets with a guaranteed
error rate, attribute a prediction to its inputs, learn a reward from preferences and then watch optimisation against
it go wrong, and finally do the statistics that every evaluation needs. The treatment is technical throughout: each
failure is a documented example from a named paper, and each tool is built from scratch.*

!!! abstract "In this chapter"
    **You will learn:**

    - specification gaming, reward hacking, goal misgeneralisation and shortcut learning, with documented examples and
      two reproduced in code
    - adversarial examples: why the sign of the gradient is the steepest step in the max-norm, FGSM and PGD,
      adversarial training as a min-max problem, and what went wrong with many early defences
    - calibration, temperature scaling, split conformal prediction with its coverage guarantee proved, and why a ReLU
      network is confident far from its data (proved)
    - verification of neural networks: interval bound propagation proved sound, branch and bound proved complete,
      exact methods, and formal methods for safety-critical software
    - interpretability: integrated gradients and its completeness axiom proved, sanity checks, probes and their limits,
      causal interventions
    - alignment as a research problem: inverse reinforcement learning, preference learning with the Bradley-Terry model,
      over-optimisation of a learned reward, and proposals for scalable oversight
    - testing and evaluation: confidence intervals, paired comparisons, what zero failures in n tests proves,
      contamination, red-teaming

    **You need:** [Chapter 14](14-Making-Decisions.md) (MDPs and value iteration), [Chapter 15](15-Reinforcement-Learning.md)
    (reinforcement learning), [Chapter 17](17-Large-Language-Models.md) (learning from human feedback) and the
    [Machine learning book](../machine-learning/index.md): logistic regression (Chapter 6), evaluation and calibration
    (Chapter 7), neural networks and backpropagation (Chapter 15) and its Chapter 22, which this chapter builds on rather
    than repeats.

    **Levels:** 20.1 is beginner to intermediate; 20.2 and 20.3 are intermediate (the proofs are advanced); 20.4 and
    20.5 are advanced; 20.6 is advanced to expert; 20.7 is intermediate.

## 20.1 What can go wrong: specification gaming, reward hacking, distribution shift

A designer wants a boat to win a race and rewards it with the game's score. The boat learns to win points, which is
not the same thing. Where exactly does the gap between "what we wrote" and "what we meant" come from, and how bad can
it get?

### The objective is a proxy

An agent receives an objective (reward function, loss, metric) written by a designer who has something else in mind:
the **intended** objective. The written one is a **proxy**. On ordinary behaviour the two usually agree, which is why
the designer chose it. But an optimiser does not produce ordinary behaviour; it searches for the behaviour that scores
highest, and extreme scores are found exactly where the proxy and the intention come apart. The economist Charles
Goodhart (1975) made the observation about statistics used as targets; it is usually quoted as **Goodhart's law**, in
the anthropologist Marilyn Strathern's paraphrase (1997): "When a measure becomes a target, it ceases to be a good
measure." Manheim and Garrabrant (2018) separated several mechanisms; the most common in AI is that the proxy
correlates with the goal over the range seen, and an optimiser pushes outside that range.

**Specification gaming** is behaviour that satisfies the literal specification without achieving the intended
outcome. **Reward hacking** is the same thing in reinforcement learning (the term from Amodei et al.'s "Concrete
problems in AI safety", 2016). Krakovna and colleagues (2020) maintain a public list of documented cases; a few, each
reported by the people who saw it:

- **The boat race** (Clark and Amodei, "Faulty reward functions in the wild", 2016). In the game CoastRunners the score
  rises when the boat hits targets along the course. A reinforcement-learning agent found a lagoon where three targets
  respawned, and circled there for ever, catching fire and crashing into other boats, never finishing the race, while
  scoring more than human players.
- **Lego stacking** (Popov et al., 2017). A simulated robot arm was rewarded for the height of the bottom face of a red
  block, meant to reward stacking it on a blue one. One version of the reward was satisfied by flipping the red block
  upside down.
- **Pausing Tetris** (Murphy, 2013). A program that learned to play games by maximising the memory value of the score
  discovered, in Tetris, that just before losing it could pause the game for ever: the score never decreases.
- **Digital evolution** (Lehman et al., "The surprising creativity of digital evolution", 2020) collects dozens of
  anecdotes from researchers whose evolved programs and creatures exploited bugs in physics simulators, or numerical
  overflow in the fitness function, instead of solving the task.

None of these agents is malicious or even clever in a human sense. Each found the highest point of the function it
was given. That is what optimisation does.

### Reproducing the boat race

The program below is a seven-square track. The boat starts at square 0, the finish (square 6) pays +10 and ends the
episode, and square 2 is a bonus that pays +1 each time it is entered and respawns at once. We solve the MDP exactly
by value iteration ([Chapter 14](14-Making-Decisions.md)) for several discount factors $\gamma$, then repeat with a
repaired reward where the bonus pays only once.

<figure class="mars-fig" markdown="0">
<svg viewBox="0 0 640 200" role="img" aria-label="A row of seven squares numbered 0 to 6. Square 2 is the respawning bonus worth plus 1, square 6 the finish worth plus 10. A curved arrow loops between squares 1 and 2; a straight arrow runs from square 2 to the finish.">
<rect x="40" y="80" width="70" height="60" fill="none" stroke="currentColor" stroke-width="1.3"/>
<rect x="120" y="80" width="70" height="60" fill="none" stroke="currentColor" stroke-width="1.3"/>
<rect x="200" y="80" width="70" height="60" fill="#eea66f" fill-opacity="0.55" stroke="currentColor" stroke-width="1.3"/>
<rect x="280" y="80" width="70" height="60" fill="none" stroke="currentColor" stroke-width="1.3"/>
<rect x="360" y="80" width="70" height="60" fill="none" stroke="currentColor" stroke-width="1.3"/>
<rect x="440" y="80" width="70" height="60" fill="none" stroke="currentColor" stroke-width="1.3"/>
<rect x="520" y="80" width="70" height="60" fill="#7ccf9a" fill-opacity="0.55" stroke="currentColor" stroke-width="1.3"/>
<text x="75" y="115" font-size="15" text-anchor="middle" fill="currentColor">0</text>
<text x="155" y="115" font-size="15" text-anchor="middle" fill="currentColor">1</text>
<text x="235" y="115" font-size="15" text-anchor="middle" fill="currentColor">2</text>
<text x="315" y="115" font-size="15" text-anchor="middle" fill="currentColor">3</text>
<text x="395" y="115" font-size="15" text-anchor="middle" fill="currentColor">4</text>
<text x="475" y="115" font-size="15" text-anchor="middle" fill="currentColor">5</text>
<text x="555" y="115" font-size="15" text-anchor="middle" fill="currentColor">6</text>
<text x="75" y="160" font-size="12" text-anchor="middle" fill="currentColor">start</text>
<text x="235" y="160" font-size="12" text-anchor="middle" fill="currentColor">bonus +1</text>
<text x="235" y="176" font-size="12" text-anchor="middle" fill="currentColor">(respawns)</text>
<text x="555" y="160" font-size="12" text-anchor="middle" fill="currentColor">finish +10</text>
<path d="M 160 78 C 170 30, 220 30, 230 72" fill="none" stroke="#eea66f" stroke-width="2.2"/>
<polygon points="231,78 225,67 236,68" fill="#eea66f"/>
<path d="M 240 78 C 230 45, 180 45, 166 74" fill="none" stroke="#eea66f" stroke-width="2.2" stroke-dasharray="5 3"/>
<polygon points="164,79 162,67 172,72" fill="#eea66f"/>
<text x="198" y="26" font-size="12" text-anchor="middle" fill="currentColor">the loop: +1 every two steps</text>
<line x1="270" y1="66" x2="508" y2="66" stroke="#9cc9ea" stroke-width="2.5"/>
<polygon points="516,66 504,60 504,72" fill="#9cc9ea"/>
<text x="400" y="56" font-size="12" text-anchor="middle" fill="currentColor">the intended route: +10 after four more steps</text>
</svg>
<figcaption>Figure 20.1. The track of the program. From the bonus square the boat can drive on to the finish (worth 10 discounted over four steps) or step back and re-enter the bonus every second step for ever. Which one the optimal policy picks depends only on the discount factor, not on what the designer meant.</figcaption>
</figure>

```python
--8<-- "books/ai/ch20_gaming.py"
```

```
bonus pays on every visit (the gamed proxy)
   gamma 0.3   value   0.33  squares visited 0121212121212121... proxy points  15.0  finished: False
   gamma 0.5   value   0.81  squares visited 0123456             proxy points  11.0  finished: True
   gamma 0.9   value   6.80  squares visited 0123456             proxy points  11.0  finished: True
   gamma 0.95  value   9.74  squares visited 0121212121212121... proxy points  15.0  finished: False
   gamma 0.99  value  49.75  squares visited 0121212121212121... proxy points  15.0  finished: False

bonus pays once (repaired reward)
   gamma 0.3   value   0.32  squares visited 0123456             proxy points  11.0  finished: True
   gamma 0.5   value   0.81  squares visited 0123456             proxy points  11.0  finished: True
   gamma 0.9   value   6.80  squares visited 0123456             proxy points  11.0  finished: True
   gamma 0.95  value   8.69  squares visited 0123456             proxy points  11.0  finished: True
   gamma 0.99  value  10.50  squares visited 0123456             proxy points  11.0  finished: True

standing on the bonus square:
   gamma 0.30: keep looping  0.33  vs  finish  0.27  -> loop
   gamma 0.34: keep looping  0.38  vs  finish  0.39  -> finish
   gamma 0.40: keep looping  0.48  vs  finish  0.64  -> finish
   gamma 0.60: keep looping  0.94  vs  finish  2.16  -> finish
   gamma 0.90: keep looping  4.74  vs  finish  7.29  -> finish
   gamma 0.93: keep looping  6.88  vs  finish  8.04  -> finish
   gamma 0.94: keep looping  8.08  vs  finish  8.31  -> finish
   gamma 0.95: keep looping  9.74  vs  finish  8.57  -> loop
   gamma 0.99: keep looping 49.75  vs  finish  9.70  -> loop
```

The calculation is short enough to do by hand. Standing on the bonus square, looping (back, then forward, then back...)
pays nothing on the first step (back to square 1) and 1 on the second, fourth, sixth step and so on. With the
convention of the program (a reward received $k$ steps from now is multiplied by $\gamma^{k-1}$), that is worth
$\gamma + \gamma^3 + \gamma^5 + \dots = \gamma/(1 - \gamma^2)$. Driving on pays 10 on the fourth step, worth
$10\gamma^3$. Setting them equal gives
$10\gamma^2(1 - \gamma^2) = 1$, so $\gamma^2 = \bigl(1 \pm \sqrt{0.6}\bigr)/2$ and $\gamma \approx 0.336$ or $\gamma \approx 0.942$.
Between these values the boat finishes; outside them it loops. Two things are worth noticing. First, the **more
far-sighted** agent ($\gamma \ge 0.95$) is the one that games: an infinite stream of small rewards beats one large
reward far enough ahead. Second, nothing in the agent is broken. Value iteration found the true optimum of the
reward it was given; the bug is in the reward. The repaired reward (pay the bonus once) makes finishing optimal for
every $\gamma$. A more general repair is **potential-based shaping** (Ng, Harada and Russell 1999), exercise 11.

### Goal misgeneralisation

A subtler failure happens even when the reward is right. Langosco, Koch, Sharkey, Pfau and Krueger (2022) trained
agents on CoinRun, a platform game where the reward is for picking up a coin that, during training, always sat at the
far right end of the level. At test time they moved the coin. The agents ran to the right end, ignoring the coin. The
reward had been specified correctly, and training performance was excellent; but "go right" and "get the coin" had been
indistinguishable in every training level, and the agent had learned the wrong one. Shah et al. (2022) named this
**goal misgeneralisation**: the agent's capabilities generalise (it still navigates the level skilfully) while its
goal does not. It is a form of distribution shift that no amount of reward engineering on the training levels fixes.

### Shortcuts and distribution shift

Supervised learning has the same disease. A classifier minimises training loss with whatever features work, and if
an easy feature predicts the label in the training data, it will be used, whether or not it is the reason for the label.
Documented cases:

- Lapuschkin et al. (2019), "Unmasking Clever Hans predictors and assessing what machines really learn", found that a
  well-performing image classifier recognised the class "horse" in the PASCAL VOC data largely from a copyright tag that
  appeared on many horse photos. (Clever Hans was a horse in 1900s Berlin that seemed to do arithmetic but was reading
  its questioner's body language.)
- Zech et al. (2018) trained pneumonia detectors on chest X-rays from several hospitals and found that they could also
  identify the hospital from the image, and that performance was often lower on data from hospitals not used in training;
  the hospital was correlated with the rate of disease, so it was a usable shortcut.
- Beery, Van Horn and Perona (2018), "Recognition in terra incognita", showed animal detectors failing when animals
  appeared in locations (backgrounds) not seen in training.

Geirhos et al. (2020), "Shortcut learning in deep neural networks", review many more. The kinds of distribution shift
(covariate, label, concept) and how to detect and correct them are treated in the
[Machine learning book, Chapter 22](../machine-learning/22-Machine-Learning-in-Practice.md#222-distribution-shift-covariate-label-concept-detecting-it);
here is the shortcut in its smallest form. The label depends on a real but noisy signal; a "watermark" feature agrees
with the label 95% of the time in training only.

```python
--8<-- "books/ai/ch20_shortcut.py"
```

```
weights (real signal, watermark, bias) when both features are used: [ 2.04  5.87 -2.98]
                                      test where watermark agrees with label
                             train    95%     50%     5%
   uses both features      0.959   0.956   0.663   0.371
   real signal only        0.842   0.847   0.841   0.843

domain classifier (train vs deployment inputs); held-out accuracy 0.5 means no detectable shift
   linear in (real, watermark):             0.614
   with the product real * (watermark - 0.5): 0.810
```

The model that uses both features is the better model on the training distribution (0.96 against 0.84), and logistic
regression, correctly doing its job, gives the watermark the largest weight. When the watermark stops carrying
information, accuracy falls to 0.66; when it is reversed, to 0.37, worse than a coin. The model without the shortcut
is unaffected. Nothing in the training data can tell the two models apart in advance: you need either knowledge of
which features are causes (Chapter 12's causal reasoning) or data from the new conditions.

The last lines show a useful and humbling fact about detection. Each feature on its own has exactly the same
distribution in training and in deployment; only the relation between them changed. A detector that looks at the
features one at a time sees nothing, a linear detector sees part of it (0.61), and one given the product feature sees
it clearly (0.81). A shift you do not know how to look for can be invisible.

## 20.2 Robustness and adversarial examples

Szegedy et al. (2014), "Intriguing properties of neural networks", found that an image classifier that is right on a
picture can be made wrong by a change to the pixels too small for a person to notice. Such inputs are **adversarial
examples**. They are not rare accidents: for most correctly classified images of standard models, one exists within
a tiny distance. How do we find them, why do they exist, and what helps?

### The threat model

Robustness is always relative to a **threat model**: which changes are allowed. The standard one is a small ball
around the input $x$ in a norm, most often the max-norm $\lVert \delta \rVert_\infty = \max_j \lvert \delta_j \rvert$
(each pixel may change by at most $\varepsilon$). A classifier $f$ is **robust at $x$ with radius $\varepsilon$** if
$f(x + \delta) = f(x)$ for every $\lVert \delta \rVert_\infty \le \varepsilon$. The **robust accuracy** at $\varepsilon$
is the fraction of test points where the prediction is correct and robust. Other threat models matter as much in
practice: rotations and translations, corruptions such as blur and noise (Hendrycks and Dietterich 2019 built
ImageNet-C to measure them), physical patches, and changes of wording for text.

### Attacks: the steepest step in the max-norm

To find an adversarial example, maximise the loss $L(x + \delta, y)$ over the ball. With a linear approximation,
$L(x + \delta) \approx L(x) + g^{\mathsf T}\delta$ where $g = \nabla_x L$.

**Lemma.** $\max_{\lVert \delta \rVert_\infty \le \varepsilon} g^{\mathsf T}\delta = \varepsilon \lVert g \rVert_1$,
attained at $\delta = \varepsilon\,\mathrm{sign}(g)$.

*Proof.* For any allowed $\delta$, $g^{\mathsf T}\delta = \sum_j g_j \delta_j \le \sum_j \lvert g_j \rvert\,\lvert \delta_j \rvert \le \varepsilon \sum_j \lvert g_j \rvert$.
The choice $\delta_j = \varepsilon\,\mathrm{sign}(g_j)$ makes every term equal to $\varepsilon \lvert g_j \rvert$, so the
bound is reached. $\square$

The lemma is the **fast gradient sign method** (FGSM, Goodfellow, Shlens and Szegedy 2015): one step of size
$\varepsilon$ in the direction $\mathrm{sign}(\nabla_x L)$. It also explains why high dimension makes models fragile:
the gain $\varepsilon \lVert g \rVert_1$ is a sum over all $d$ input coordinates, so in a 150 000-pixel image a change
of $\varepsilon$ per pixel, invisible on each pixel, can move the logit by $\varepsilon$ times the sum of 150 000
gradient magnitudes. The [Machine learning book, Chapter 22](../machine-learning/22-Machine-Learning-in-Practice.md#225-robustness-adversarial-examples)
works this out for linear models in high dimension. **Projected gradient descent** (PGD, Madry et al. 2018) repeats
smaller sign steps and after each one projects back into the ball (clips each coordinate to
$[x_j - \varepsilon, x_j + \varepsilon]$); it is the standard strong first-order attack.

### Adversarial training as a min-max problem

Madry et al. (2018) wrote robust learning as a saddle-point problem:

$$
\min_\theta \; \mathbb{E}_{(x, y)} \Bigl[ \max_{\lVert \delta \rVert_\infty \le \varepsilon} L\bigl(f_\theta(x + \delta), y\bigr) \Bigr].
$$

The inner maximisation is the attack; the outer minimisation trains on its result. By Danskin's theorem, the gradient
of the inner maximum with respect to $\theta$ is the gradient of the loss at the maximiser (when it is unique), which
justifies the simple recipe: for each batch, run PGD, then take an ordinary training step on the perturbed batch. The
program trains a small ReLU network on two interleaved half-moons in the plane, attacks it with FGSM and PGD, then
trains it adversarially with $\varepsilon = 0.1$ and attacks again.

```python
--8<-- "books/ai/ch20_attack.py"
```

```
standard training: clean test accuracy 0.997
    eps    FGSM acc   PGD-20 acc
   0.02     0.993      0.993
   0.05     0.988      0.988
   0.10     0.963      0.963
   0.15     0.911      0.908
   0.20     0.829      0.824

adversarial training, eps 0.1: clean test accuracy 0.996
    eps    FGSM acc   PGD-20 acc
   0.02     0.995      0.995
   0.05     0.988      0.988
   0.10     0.970      0.970
   0.15     0.936      0.933
   0.20     0.879      0.874

test point 19: [-0.317  0.774] label 0 predicted 0
after PGD, eps 0.1: [-0.217  0.674] predicted 1  change [ 0.1 -0.1]
```

In two dimensions the effect is mild, because the classes are far apart compared with $\varepsilon$; in image space
the same attacks take a standard network's accuracy to a few per cent with a budget of 8 grey levels out of 255 per
pixel on CIFAR-10 images (as reported in Madry et al. 2018 and many papers since). The pattern is still visible: accuracy under attack falls with $\varepsilon$,
PGD is a little stronger than FGSM, and adversarial training raises robust accuracy at every $\varepsilon$ without
hurting clean accuracy here. On harder data adversarial training usually costs clean accuracy; Tsipras et al. (2019)
gave a simple distribution where the trade-off is unavoidable. The single traced point shows what an adversarial
example looks like in the plane: a point near the boundary pushed across it by 0.1 in each coordinate.

### Lessons from broken defences

Many defences were proposed in 2017 and 2018 that appeared to stop attacks, for example by adding a non-differentiable
preprocessing step or randomness. Athalye, Carlini and Wagner (2018), "Obfuscated gradients give a false sense of
security", showed that most of the defences published at ICLR 2018 worked by breaking the attacker's gradient rather
than by making the model robust, and that attacks adapted to each defence circumvented them. The lasting lessons:
**an evaluation is only as strong as the strongest attack tried**, attacks must be adapted to the defence, and an
attack's failure to find an adversarial example is not a proof that none exists. That last point motivates
verification (20.4).

Physical attacks are documented too: printed photos of adversarial images still fooled a classifier through a phone
camera (Kurakin, Goodfellow and Bengio 2017); stickers on stop signs made a road-sign classifier misread them in
drive-by tests (Eykholt et al. 2018); a 3-D printed turtle was classified as a rifle from most viewpoints (Athalye,
Engstrom, Ilyas and Kwok 2018). Robustness also concerns training data: a **backdoor** planted by poisoning a small
part of the training set makes a model misbehave only when a trigger pattern is present (Gu, Dolan-Gavitt and Garg
2017, "BadNets").

## 20.3 Uncertainty: knowing when you don't know

A rover's terrain classifier says "sand, 99%". Should the planner trust it? The number is useful only if 99% means
right 99 times in 100, and only if the classifier says something different when it is shown terrain it has never seen.
A safe system needs both: honest confidence on familiar inputs and a warning on unfamiliar ones.

### Two kinds of uncertainty

**Aleatoric** uncertainty is noise in the world itself: two classes that genuinely overlap, a sensor's jitter. More
data does not remove it. **Epistemic** uncertainty is the model's ignorance: too little data in this region, or none.
More data does remove it. A softmax probability mixes the two and measures neither well. Bayesian methods
([Machine learning, Chapter 12](../machine-learning/12-Probabilistic-Models.md)) represent epistemic uncertainty with a
distribution over parameters; practical approximations include **deep ensembles** (train several networks from
different random starts and average them, Lakshminarayanan, Pritzel and Blundell 2017) and Monte Carlo dropout (Gal and
Ghahramani 2016). Their disagreement is a signal of epistemic uncertainty.

### Calibration

A classifier is **calibrated** if, among inputs where it reports confidence $c$, the fraction it gets right is $c$:
$P(\hat y = y \mid \hat p = c) = c$. The **expected calibration error** groups predictions into confidence bins
$B_1, \dots, B_M$ and averages the gap:

$$
\mathrm{ECE} = \sum_{m=1}^{M} \frac{\lvert B_m \rvert}{n} \,\bigl\lvert \mathrm{acc}(B_m) - \mathrm{conf}(B_m) \bigr\rvert.
$$

Guo, Pleiss, Sun and Weinberger (2017), "On calibration of modern neural networks", found that deep networks of the
time were markedly overconfident, more so than older, smaller ones, and that a single scalar fixes most of it:
**temperature scaling** divides all logits by $T > 0$, with $T$ chosen to minimise the negative log-likelihood (NLL)
on a held-out validation set. Dividing by $T$ does not change which logit is largest, so accuracy is untouched
(exercise 4); $T > 1$ softens overconfident predictions. Calibration methods in general, reliability diagrams and the
Brier score are in [Machine learning, Chapter 7](../machine-learning/07-Evaluating-Models.md#76-calibration-reliability-diagrams-and-the-brier-score).

### Conformal prediction: sets with a guarantee

Calibration is an average property. Sometimes we want a guarantee for each prediction: "the true class is in this set
at least 90% of the time". **Conformal prediction** (Vovk, Gammerman and Shafer 2005) gives exactly that, for any
model, with one assumption: the calibration and test examples are **exchangeable** (their joint distribution does not
change when they are reordered; independent draws from one distribution are exchangeable).

**Split conformal prediction.** Take any trained model and a **nonconformity score** $s(x, y)$, large when the label
$y$ looks wrong for $x$; we use $s(x, y) = 1 - \hat p_y(x)$. Compute the scores $s_1, \dots, s_n$ on $n$ calibration
examples not used in training. Let $\hat q$ be the $k$-th smallest of them, with $k = \lceil (n+1)(1-\alpha) \rceil$.
For a new input, output the set $C(x) = \{ y : s(x, y) \le \hat q \}$.

**Theorem.** If the $n$ calibration examples and the test example are exchangeable, then
$P\bigl(y_{n+1} \in C(x_{n+1})\bigr) \ge 1 - \alpha$.

*Proof.* Write $s_{n+1} = s(x_{n+1}, y_{n+1})$ for the test example's score with its true label. The true label is in
the set exactly when $s_{n+1} \le \hat q$. By exchangeability the $n + 1$ scores are in random order, so (assuming no
ties, which a tiny random perturbation ensures) the rank of $s_{n+1}$ among all $n + 1$ is uniform on
$\{1, \dots, n+1\}$. The event $s_{n+1} \le \hat q$ (the $k$-th smallest calibration score) happens exactly when
$s_{n+1}$ has rank at most $k$ among the $n + 1$ scores. So its probability is $k / (n + 1) \ge 1 - \alpha$. $\square$

The same argument shows the coverage is at most $1 - \alpha + 1/(n+1)$, so it is tight. The guarantee needs no
assumption about the model: a bad model gives large sets, a good model small ones, both with correct coverage.
It is **marginal**: averaged over inputs, not for each input or each class; the program shows that coverage among
singleton sets is a little below 90% and among two-class sets above. Angelopoulos and Bates (2021) give a gentle
introduction with many variants.

### Out-of-distribution inputs

An **out-of-distribution** (OOD) input comes from somewhere the training data never covered. Hendrycks and Gimpel
(2017) proposed the simplest detector: flag inputs whose maximum softmax probability is low. It works better than
chance on many image benchmarks. But there is a mathematical reason it cannot work everywhere.

**Theorem (Hein, Andriushchenko and Bitterwolf 2019, simplified).** Let $f$ be a ReLU network with a linear output
layer and $x \ne 0$. Then along the ray $tx$, the softmax confidence tends to 1 as $t \to \infty$, unless the two largest
logits grow at exactly the same rate.

*Proof.* A ReLU network is a continuous piecewise-affine function: the input space is divided into finitely many
convex regions (one per pattern of active units), and on each region $f(z) = A z + b$. The ray $\{tx : t \ge 0\}$
crosses each region in an interval, and there are finitely many regions, so for all $t$ beyond some $t_0$ it stays in
one region, where the logits are $z_k(t) = t\,a_k + b_k$ with $a = Ax$. If one $a_k$ is strictly largest, then for
$j \ne k$, $z_j(t) - z_k(t) = t(a_j - a_k) + (b_j - b_k) \to -\infty$, and the softmax probability
$1 / \bigl(1 + \sum_{j \ne k} e^{z_j - z_k}\bigr) \to 1$. $\square$

So far from the data, where we most want the model to say "I do not know", a ReLU classifier becomes certain. The
program shows both halves: the max-softmax score is useless (AUROC 0.002, meaning the far-away points are *more*
confident than real test points, with mean confidence 1.000), while a score that measures distance to the training data
separates them perfectly. Distance-based scores (nearest neighbours in a learned feature space, or the Mahalanobis
distance of Lee et al. 2018) and ensembles are common remedies; none is perfect in high dimension, where "near the
training data" is itself hard to define.

```python
--8<-- "books/ai/ch20_uncertainty.py"
```

```
train accuracy 0.910, test accuracy 0.747
   raw softmax          mean confidence 0.893   NLL 0.925   ECE 0.146
   temperature T = 3.85 mean confidence 0.704   NLL 0.599   ECE 0.045

reliability table for the raw softmax (test set)
   confidence in (0.30, 0.60]:  246 points, mean confidence 0.527, accuracy 0.390
   confidence in (0.60, 0.80]:  444 points, mean confidence 0.706, accuracy 0.554
   confidence in (0.80, 0.95]:  534 points, mean confidence 0.887, accuracy 0.674
   confidence in (0.95, 0.99]:  472 points, mean confidence 0.974, accuracy 0.754
   confidence in (0.99, 1.00]: 1304 points, mean confidence 0.999, accuracy 0.907

conformal sets, alpha = 0.1: threshold 0.746, coverage 0.911, mean set size 1.53
   sets of size 1: 0.527 of test points, coverage among them 0.876
   sets of size 2: 0.414 of test points, coverage among them 0.944
   sets of size 3: 0.059 of test points, coverage among them 1.000

OOD detection (3000 test points vs 3000 points near (6, -4)), AUROC, 1.0 = perfect, 0.5 = chance
   score 1 - max softmax:              0.002   (mean max softmax on OOD points 1.000)
   distance to nearest training point: 1.000

confidence far from the data, along the ray t * (1, -1):
   t =    1: max softmax 0.679544
   t =    3: max softmax 0.999924
   t =   10: max softmax 1.000000
   t =  100: max softmax 1.000000
   t = 1000: max softmax 1.000000
```

<figure class="mars-fig" markdown="0">
<svg viewBox="0 0 420 350" role="img" aria-label="Reliability diagram. The diagonal line is perfect calibration. The five measured points of the raw network all lie below the diagonal: confidence 0.53 with accuracy 0.39, 0.71 with 0.55, 0.89 with 0.67, 0.97 with 0.75 and 1.00 with 0.91.">
<line x1="60" y1="300" x2="370" y2="300" stroke="currentColor" stroke-width="1.2"/>
<line x1="60" y1="300" x2="60" y2="30" stroke="currentColor" stroke-width="1.2"/>
<line x1="60" y1="300" x2="360" y2="40" stroke="currentColor" stroke-width="1" stroke-dasharray="5 4"/>
<text x="60" y="318" font-size="11" text-anchor="middle" fill="currentColor">0</text>
<text x="210" y="318" font-size="11" text-anchor="middle" fill="currentColor">0.5</text>
<text x="360" y="318" font-size="11" text-anchor="middle" fill="currentColor">1</text>
<text x="210" y="340" font-size="12" text-anchor="middle" fill="currentColor">confidence (mean max softmax in the bin)</text>
<text x="52" y="304" font-size="11" text-anchor="end" fill="currentColor">0</text>
<text x="52" y="174" font-size="11" text-anchor="end" fill="currentColor">0.5</text>
<text x="52" y="44" font-size="11" text-anchor="end" fill="currentColor">1</text>
<text x="18" y="170" font-size="12" text-anchor="middle" fill="currentColor" transform="rotate(-90 18 170)">accuracy in the bin</text>
<polyline points="218.1,198.6 271.8,156.0 326.1,124.8 352.2,104.0 359.7,64.2" fill="none" stroke="#eea66f" stroke-width="2.2"/>
<circle cx="218.1" cy="198.6" r="5" fill="#eea66f" stroke="currentColor" stroke-width="1"/>
<circle cx="271.8" cy="156.0" r="5" fill="#eea66f" stroke="currentColor" stroke-width="1"/>
<circle cx="326.1" cy="124.8" r="5" fill="#eea66f" stroke="currentColor" stroke-width="1"/>
<circle cx="352.2" cy="104.0" r="5" fill="#eea66f" stroke="currentColor" stroke-width="1"/>
<circle cx="359.7" cy="64.2" r="5" fill="#eea66f" stroke="currentColor" stroke-width="1"/>
<text x="80" y="150" font-size="12" fill="currentColor">perfect calibration</text>
<line x1="120" y1="157" x2="148" y2="218" stroke="currentColor" stroke-width="0.8"/>
<text x="232" y="230" font-size="12" fill="currentColor">raw network: below the line,</text>
<text x="232" y="246" font-size="12" fill="currentColor">so overconfident</text>
</svg>
<figcaption>Figure 20.2. Reliability diagram of the program's overfitted network on its test set (the raw-softmax table). Every bin lies below the diagonal: when the network says 97%, it is right 75% of the time. Temperature scaling with T = 3.85 moves the points close to the diagonal, cutting the ECE from 0.146 to 0.045 without changing a single prediction.</figcaption>
</figure>

## 20.4 Verification of neural networks; formal methods for safety-critical systems

*Level: advanced.* Testing can show that a system fails; it cannot show that it never fails. An attack that finds
nothing proves nothing (20.2). For a safety-critical system we would like a **proof**: for every input in a stated set,
the output satisfies a stated property. Can we prove things about a trained neural network?

### Specifications and the two kinds of verifier

A **specification** for a network $f$ is a pair: an input set $\mathcal{X}$ (for example the box
$\lVert x' - x \rVert_\infty \le \varepsilon$) and an output property $P$ (for example "the logit of class $y$ exceeds
every other logit"). The verification problem asks whether $P(f(x'))$ holds for every $x' \in \mathcal{X}$. A
verifier is **sound** if whenever it says "verified" the property really holds, and **complete** if it can always give
a definite answer (verified or a counterexample). Katz, Barrett, Dill, Julian and Kochenderfer (2017) proved that
verifying such properties of ReLU networks is NP-complete, so complete verifiers take exponential time in the worst
case. Two families result: **complete** methods (SMT solvers such as their Reluplex and its successor Marabou; mixed
integer linear programming, Tjeng, Xiao and Tedrake 2019) that are exact but slow; and **incomplete** methods that
compute sound bounds quickly but may answer "unknown".

### Interval bound propagation

The simplest sound method pushes a box through the network. Represent a box by its centre $c$ and radius vector $r$
(the box is $[c - r, c + r]$).

**Lemma.** If $z$ ranges over the box $[c - r, c + r]$, then $Wz + b$ lies in the box with centre $Wc + b$ and radius
$\lvert W \rvert r$ (absolute values taken entrywise), and $\mathrm{ReLU}(z)$ lies in
$[\mathrm{ReLU}(c - r), \mathrm{ReLU}(c + r)]$.

*Proof.* Write $z = c + e$ with $\lvert e_j \rvert \le r_j$. Then
$(Wz + b)_i - (Wc + b)_i = \sum_j W_{ij} e_j$, and $\bigl\lvert \sum_j W_{ij} e_j \bigr\rvert \le \sum_j \lvert W_{ij} \rvert r_j$.
ReLU is non-decreasing in each coordinate, so its output on the box lies between its values at the two corners. $\square$

By induction over the layers, **interval bound propagation** (IBP) returns a box that contains every output the network
can produce on the input box: it is sound. To check robustness we fold the difference "logit of $y$ minus logit of
the other class" into the last layer and ask whether its lower bound is positive. If so, the point is **certified**.

IBP is loose for a reason the figure shows. A box is mapped to a rotated, sheared parallelogram, and IBP replaces the
parallelogram by the smallest box containing it, the **wrapping effect** known from interval arithmetic. Each layer
wraps again, so the bounds grow with depth. Better relaxations replace each ReLU by linear upper and lower bounds that
are tighter than a box (CROWN, Zhang et al. 2018, and related methods).

<figure class="mars-fig" markdown="0">
<svg viewBox="0 0 640 260" role="img" aria-label="Left, an input square. Middle, its image under a 45 degree linear map is a diamond. Right, interval bound propagation replaces the diamond by the box around it, which has twice the area and contains points the network can never produce.">
<rect x="50" y="70" width="110" height="110" fill="#9cc9ea" fill-opacity="0.45" stroke="currentColor" stroke-width="1.3"/>
<text x="105" y="210" font-size="12" text-anchor="middle" fill="currentColor">input box</text>
<line x1="180" y1="125" x2="228" y2="125" stroke="currentColor" stroke-width="1.5"/>
<polygon points="236,125 224,119 224,131" fill="currentColor"/>
<text x="208" y="112" font-size="12" text-anchor="middle" fill="currentColor">W</text>
<polygon points="325,47 403,125 325,203 247,125" fill="#9cc9ea" fill-opacity="0.45" stroke="currentColor" stroke-width="1.3"/>
<text x="325" y="232" font-size="12" text-anchor="middle" fill="currentColor">true image (a diamond)</text>
<line x1="420" y1="125" x2="458" y2="125" stroke="currentColor" stroke-width="1.5"/>
<polygon points="466,125 454,119 454,131" fill="currentColor"/>
<text x="442" y="112" font-size="12" text-anchor="middle" fill="currentColor">IBP</text>
<rect x="478" y="47" width="156" height="156" fill="#eea66f" fill-opacity="0.35" stroke="currentColor" stroke-width="1.3"/>
<polygon points="556,47 634,125 556,203 478,125" fill="#9cc9ea" fill-opacity="0.6" stroke="currentColor" stroke-width="1.3"/>
<text x="556" y="232" font-size="12" text-anchor="middle" fill="currentColor">IBP box: twice the area</text>
</svg>
<figcaption>Figure 20.3. The wrapping effect. A linear layer turns the input box into a rotated shape; interval bound propagation keeps only the smallest axis-aligned box around it (orange), which includes corners the network never reaches. Repeating this layer after layer is why IBP's bounds grow loose in deep networks, and why splitting the input into smaller boxes helps: the waste shrinks with the box.</figcaption>
</figure>

### Branch and bound: from sound to complete

If IBP cannot certify a box, split it in two along its widest side and try each half; a smaller box wastes less. At
the same time evaluate the network at the centre of each box: a misclassified centre is a concrete **counterexample**
and refutes the property. This is branch and bound
([Algorithms book, Chapter 14](../algorithms/14-Backtracking-and-Branch-and-Bound.md)).

**Claim.** Branch and bound is sound, and (with an unlimited budget, for a property that holds or fails with a margin)
complete.

*Proof sketch.* Soundness: "verified" is returned only when every piece of a partition of the input box has a positive
IBP lower bound, and IBP is sound on each piece. Completeness: the network is Lipschitz continuous (a product of
bounded linear maps and 1-Lipschitz ReLUs), so on a box of width $w$ the IBP bound is within $Kw$ of the true minimum
for some constant $K$ that depends on the weights. If the true minimum margin over the input box is $m > 0$, every
piece of width below $m/K$ is certified; if instead some point has margin $-m < 0$, every point within distance $m/L$
of it is also misclassified (with $L$ the Lipschitz constant of the margin), so once the pieces are small enough, the
centre of the piece containing that point is a counterexample. Either way the splitting stops. $\square$

```python
--8<-- "books/ai/ch20_verify.py"
```

```
300 test points; robust accuracy = correct for EVERY input within eps
    eps   IBP proves   B&B proves   B&B refutes   unknown   PGD attack leaves
   0.02      98.3%        99.7%         0.3%        0.0%       99.7%
   0.05      92.0%        98.7%         1.3%        0.0%       98.7%
   0.10      68.0%        95.7%         4.3%        0.0%       95.7%
   0.15      26.0%        89.7%        10.3%        0.0%       89.7%
```

Read the table from left to right. IBP alone certifies 68% of points at $\varepsilon = 0.1$. Branch and bound, splitting
at most a few hundred times per point, settles every single point: 95.7% proved robust, 4.3% refuted with a concrete
counterexample, none unknown. And the PGD attack of 20.2 leaves exactly 95.7% unbroken: on this small network the
attack happened to be optimal, which only a complete verifier can tell us. The gap between 68% and 95.7% is the price
of IBP's looseness. In two dimensions splitting is cheap; in a thousand dimensions the number of pieces explodes,
which is why practical verifiers split on ReLU activations (each unit active or inactive) rather than on inputs, and
combine splitting with tight linear relaxations. Katz et al. (2017) used Reluplex to prove properties of neural
networks designed to compress the collision-avoidance advisory tables for unmanned aircraft (ACAS Xu), which became a
standard test case; verifying networks with millions of units against image-scale perturbations remains out of reach
for complete methods.

A different route to certificates is **randomised smoothing** (Cohen, Rosenfeld and Kolter 2019): classify the
majority vote of $f$ on many Gaussian-noise copies of the input. If the top class has probability at least $p_A > 1/2$
under the noise, the smoothed classifier is provably robust in the Euclidean norm within radius $\sigma\,\Phi^{-1}(p_A)$,
where $\sigma$ is the noise level and $\Phi^{-1}$ the inverse of the standard normal distribution function. The
certificate is probabilistic (it relies on estimating $p_A$ by sampling), but it scales to large image models.

### Formal methods beyond neural networks

Verification of software and hardware is decades older than neural networks. **Model checking** (Clarke and Emerson
1981, Queille and Sifakis 1982) exhaustively explores the states of a finite model of a system to check temporal-logic
properties ("the two trains are never on the same track section"). **Interactive theorem proving** has produced
machine-checked proofs of whole systems: the seL4 operating-system kernel was proved to implement its specification
(Klein et al. 2009), and the CompCert C compiler was proved to preserve the meaning of the programs it compiles (Leroy
2009). The flight software of the Curiosity rover was written under strict coding rules and checked with static
analysers and the SPIN model checker; Holzmann's "Mars Code" (2014) describes the methods.

For systems with learned components, formal methods are usually applied to what surrounds the learned part.
**Runtime assurance** (the Simplex architecture, Sha 2001) pairs a high-performance but unverified controller with a
simple verified safety controller and a monitor that switches to the safe one when the state approaches the edge of a
verified safe set. **Shielding** (Alshiekh et al. 2018) applies the same idea to reinforcement learning: a shield
computed from a formal model blocks any action that could violate a temporal-logic safety property, during learning
and after. **Constrained MDPs** (Altman 1999) add cost constraints to the reward, and constrained policy optimisation
(Achiam, Held, Tamar and Abbeel 2017) learns policies that keep the expected cost below a limit. The common thread:
prove properties of a small, simple part, and arrange the system so that the small part is enough for safety.

## 20.5 Interpretability methods

*Level: advanced.* A model is right on the test set. Is it right for the right reasons, or because of a copyright tag
(20.1)? **Interpretability** methods try to answer by showing what a model's output depends on, or what its internal
parts compute. Shapley-value attributions, permutation importance and saliency maps are built in the
[Machine learning book, Chapter 22](../machine-learning/22-Machine-Learning-in-Practice.md#224-interpretability), and
mechanistic interpretability (features, circuits, superposition, sparse autoencoders) in
[Chapter 23](../machine-learning/23-Where-Machine-Learning-Goes.md#234-mechanistic-interpretability). This section adds
the axiomatic view of attribution, the tests an explanation should pass, and the gap between finding information in a
model and showing that the model uses it.

### Integrated gradients

A **feature attribution** assigns to each input feature $x_j$ a number $a_j$ saying how much it contributed to the
output $F(x)$. The plain gradient $\partial F / \partial x_j$ says how the output would change for a tiny change of
$x_j$, which is not the same as how much $x_j$ contributed: a saturated unit has zero gradient even if it is the reason
for the output. Sundararajan, Taly and Yan (2017) proposed **integrated gradients** (IG): choose a **baseline** input
$x'$ meaning "absence of signal" (often zero), and integrate the gradient along the straight path from $x'$ to $x$:

$$
\mathrm{IG}_j(x) = (x_j - x'_j) \int_0^1 \frac{\partial F}{\partial x_j}\bigl(x' + \alpha (x - x')\bigr)\, d\alpha.
$$

**Theorem (completeness).** If $F$ is differentiable along the path, $\sum_j \mathrm{IG}_j(x) = F(x) - F(x')$.

*Proof.* Let $\gamma(\alpha) = x' + \alpha(x - x')$ and $g(\alpha) = F(\gamma(\alpha))$. By the chain rule
$g'(\alpha) = \sum_j \frac{\partial F}{\partial x_j}(\gamma(\alpha))\,(x_j - x'_j)$. Integrating from 0 to 1 and using the
fundamental theorem of calculus, $\sum_j \mathrm{IG}_j(x) = \int_0^1 g'(\alpha)\,d\alpha = g(1) - g(0) = F(x) - F(x')$. $\square$

(For ReLU networks $F$ is only piecewise differentiable, but it is continuous and the path crosses finitely many
kinks, so the same integral identity holds.) Completeness means the attributions account exactly for the change in
output, which plain gradient-times-input does not (exercise 7). The authors also prove IG is the unique path method with
some further axioms, and note that the choice of baseline is a modelling decision, not a detail. In code the integral
becomes an average of gradients at $m$ points along the path.

### Sanity checks

An attribution method can produce a plausible picture that has nothing to do with the model. Adebayo et al. (2018),
"Sanity checks for saliency maps", proposed a simple test: re-randomise the model's weights (or train on random labels)
and see whether the explanation changes. Several popular saliency methods produced nearly the same maps for a trained
and a randomised network, behaving more like edge detectors of the input than like explanations of the model. A
method whose output does not depend on the model cannot tell us about the model.

### Probes

A **probe** is a simple classifier (usually linear) trained to predict some property from a model's internal
activations. If the probe succeeds, the information is present in that layer, in linearly readable form (Alain and
Bengio 2016). Probing has been used to find syntax in the layers of language models, and positions in board-game
models. But presence is not use. Hewitt and Liang (2019) showed that probes can succeed on random "control" tasks, so a
probe's accuracy must be compared with a baseline; and a property can be decodable from a layer that the model never
uses for its output. To show *use*, intervene: change the activation and see whether the output changes as predicted.
**Activation patching** (also called causal tracing or interchange intervention) runs the model on two inputs and
copies an internal activation from one run into the other; if the output flips accordingly, that activation carries
the information causally. Vig et al. (2020) used causal mediation analysis this way to locate gender bias in a
language model's attention heads, and Meng, Bau, Andonian and Belinkov (2022) used causal tracing to locate where a
language model recalls factual associations, and then edited them.

```python
--8<-- "books/ai/ch20_interpret.py"
```

```
training accuracy 1.000

one input: [ 0.8 -0.3  1.5 -1.   0.4]
   gradient x input     [ 15.505 -12.202  -1.112  -1.444  -0.189]
   integrated gradients [ 17.407 -13.355  -0.767  -0.946  -0.036]
   completeness: sum of IG = 2.3019,  f(x) - f(0) = 2.3019

mean |IG| per feature over 500 inputs: [12.012 20.104  0.256  0.69   0.411]
correlation of |IG| between trained and randomised network:   0.419
correlation of the input-only map |x| before and after:          1.000

linear probe accuracy on held-out inputs   trained net   random net
   x1 > 0 (a feature the model uses)        0.988        0.996
   x3 > 0 (a feature the model ignores)     0.976        0.978
   x0 * x3 > 0 (not linear in the inputs)   0.556        0.566
```

What the run shows:

- **Completeness holds to four decimals**: the IG values sum to $F(x) - F(0)$, which gradient-times-input does not
  promise. The two large attributions (for $x_0$ and $x_1$) partly cancel, which is correct: the input is close to the
  decision boundary $x_0 + 2x_1 = 0$, where the two features pull in opposite directions.
- **Averaged over 500 inputs, IG ranks the features correctly**: $x_1$ (weight 2 in the true rule) above $x_0$
  (weight 1), and the three noise features near zero.
- **Sanity check**: the trained and the randomised network get attribution maps with correlation 0.42, clearly
  different, so IG depends on the model; the "explanation" $\lvert x \rvert$ has correlation 1.000 with itself after
  randomisation, so it fails the test, as it should. Note that 0.42 is not 0: IG multiplies by $x - x'$, so part of
  every IG map comes from the input itself.
- **Probes find what is not used**: a linear probe reads "$x_3 > 0$" from the hidden layer with 97.6% accuracy,
  although the model ignores $x_3$ (its IG is near zero). A random network's hidden layer does just as well. A
  successful probe means the information survived into the layer, not that the model relies on it. And a property
  that is not a linear function of the inputs ($x_0 x_3 > 0$) is barely decodable by either.

Interpretability methods themselves need evaluation. Jacovi and Goldberg (2020) distinguished **faithfulness** (the
explanation reflects the model's actual reasoning) from **plausibility** (it convinces a person); the two can diverge.
For language models that write out a chain of reasoning ([Chapter 17](17-Large-Language-Models.md)), Turpin, Michael,
Perez and Bowman (2023) showed that the written reasoning can omit the real cause of an answer: when a bias was added
to the prompt (for instance always placing the correct answer in position A in the examples), models followed it while
their explanations never mentioned it.

## 20.6 Alignment as a research problem: learning objectives from humans

*Level: advanced to expert.* Section 20.1 showed that a written objective is a proxy. If writing a correct objective
by hand is so hard, can an agent instead **learn** what people want, from what they do or what they say they prefer?
And when the agent's work becomes too complex for a person to judge, how do we supervise it at all? This is the
technical core of what is called **alignment**: making a system's learned objective match its designers' intentions.

### Inverse reinforcement learning

Reinforcement learning goes from a reward to behaviour. **Inverse reinforcement learning** (IRL) goes back: given
an expert's behaviour, find a reward function that the behaviour is optimal for (Russell 1998; Ng and Russell 2000).

The problem is badly posed, and Ng and Russell said so. The reward $R = 0$ makes every policy optimal, so it
"explains" any behaviour. For a finite MDP with transition matrices $P_a$, discount $\gamma$, and an observed policy
that always takes action $a_1$, they characterised the set of state-reward vectors $R$ for which that policy is
optimal:

$$
(P_{a_1} - P_a)(I - \gamma P_{a_1})^{-1} R \succeq 0 \quad \text{for every action } a,
$$

with $\succeq$ meaning every component is non-negative. (The left side, read row by row, is how much better $a_1$ is
than $a$ in each state when the values are those of the observed policy.) This is a cone of rewards, containing
$R = 0$ and many others. To pick one they added a preference for rewards that make the observed policy optimal by the
widest margin, which gives a linear program. Later methods resolve the ambiguity in other ways: **apprenticeship
learning** matches the expert's expected feature counts (Abbeel and Ng 2004); **maximum-entropy IRL** (Ziebart, Maas,
Bagnell and Dey 2008) assumes the expert picks trajectories with probability proportional to $e^{R(\tau)}$, which turns
IRL into maximum-likelihood estimation and copes with suboptimal demonstrations. A deeper difficulty remains: humans
are not optimal, and to infer what someone wants from what they do, you must also model how they fail. Armstrong and
Mindermann (2018) proved that without assumptions about the planner, preferences cannot be identified from behaviour
even with infinite data.

### Preference learning

People find it easier to compare than to score: "is output A or output B better?" The **Bradley-Terry model**
(Bradley and Terry 1952) links comparisons to a hidden score $r$:

$$
P(A \succ B) = \sigma\bigl(r(A) - r(B)\bigr) = \frac{1}{1 + e^{-(r(A) - r(B))}}.
$$

Given comparisons, fit $r$ by maximum likelihood: this is logistic regression on differences, with loss
$-\log \sigma(r(A) - r(B))$ for each pair where A was preferred. Christiano, Leike, Brown, Martic, Legg and Amodei
(2017), "Deep reinforcement learning from human preferences", trained a neural reward model this way from comparisons
of short video clips, and trained agents on the learned reward to perform simulated robotics and Atari tasks, including
a backflip that would be hard to specify by hand. The same recipe, with a language model's outputs as the things
compared, became the reinforcement learning from human feedback of Stiennon et al. (2020) and Ouyang et al. (2022),
covered in [Chapter 17](17-Large-Language-Models.md).

### Over-optimisation of a learned reward

A learned reward is a proxy too, and a sharper one: it was fit on the outputs people were shown, and the policy is
then optimised to find outputs it rates highly, which may lie outside that range. Gao, Schulman and Hilton (2023),
"Scaling laws for reward model overoptimization", measured this with a synthetic setup: a large "gold" reward model
played the human, a smaller proxy was trained on its preferences, and a policy was optimised against the proxy. As
optimisation increased (measured by the KL divergence between the optimised policy and the starting one), the proxy
reward kept rising while the gold reward rose, peaked and fell.

The program reproduces the shape in a toy. The true reward has a feature whose value is good only up to a point
($x - x^2/4$, best at $x = 2$). Preferences are collected on ordinary outputs near 0, where the true reward looks linear,
and the learned reward is linear. Then we optimise against it with **best-of-$n$**: draw $n$ candidates from a base
distribution and keep the one the learned reward likes best. Best-of-$n$ is a simple and widely used way to trade
optimisation against staying close to the base distribution. If $F$ is the distribution function of the learned
reward of a random candidate (continuous, no ties), the winner has density $n F^{n-1}$ times the base density, so the
KL divergence from the base is

$$
\mathbb{E}\bigl[\log\bigl(n F^{n-1}\bigr)\bigr] = \log n + (n-1)\,\mathbb{E}[\log U] = \log n - \frac{n-1}{n},
$$

using that $F$ evaluated at the winner is distributed like the maximum $U$ of $n$ uniform numbers, for which
$\mathbb{E}[\log U] = -1/n$.

```python
--8<-- "books/ai/ch20_preferences.py"
```

```
learned reward weights: [ 1.092  0.514 -0.001  0.048]   (true slope at 0: 1.0, 0.5, 0, 0)
on fresh pairs from the same distribution the learned reward agrees with the truth 0.975 of the time

best-of-n against the learned reward (averages over 400 repetitions)
        n    KL (nats)   learned reward   true reward of the chosen output
        1      0.00        -0.035           -0.271
        4      0.64         1.227            0.780
       16      1.84         2.083            1.213
       64      3.17         2.829            1.388
      256      4.55         3.415            1.457
     1024      5.93         3.925            1.383
     4096      7.32         4.412            1.364
    16384      8.70         4.777            1.073

the part of the true reward that depends on feature 0, x - x^2/4, is largest (1.0) at x = 2;
the learned linear reward keeps asking for more of feature 0 for ever.
```

<figure class="mars-fig" markdown="0">
<svg viewBox="0 0 600 300" role="img" aria-label="Plot of reward against KL divergence for best-of-n. The learned reward rises steadily from about 0 to 4.8. The true reward rises to a peak of about 1.46 near KL 4.6 and then falls to about 1.07 at KL 8.7.">
<line x1="60" y1="240" x2="560" y2="240" stroke="currentColor" stroke-width="1.2"/>
<line x1="60" y1="240" x2="60" y2="22" stroke="currentColor" stroke-width="1.2"/>
<text x="60" y="258" font-size="11" text-anchor="middle" fill="currentColor">0</text>
<text x="170" y="258" font-size="11" text-anchor="middle" fill="currentColor">2</text>
<text x="280" y="258" font-size="11" text-anchor="middle" fill="currentColor">4</text>
<text x="390" y="258" font-size="11" text-anchor="middle" fill="currentColor">6</text>
<text x="500" y="258" font-size="11" text-anchor="middle" fill="currentColor">8</text>
<text x="310" y="282" font-size="12" text-anchor="middle" fill="currentColor">KL divergence from the base distribution (nats), i.e. optimisation pressure</text>
<text x="52" y="225" font-size="11" text-anchor="end" fill="currentColor">0</text>
<text x="52" y="149" font-size="11" text-anchor="end" fill="currentColor">2</text>
<text x="52" y="73" font-size="11" text-anchor="end" fill="currentColor">4</text>
<line x1="56" y1="221" x2="64" y2="221" stroke="currentColor" stroke-width="1"/>
<line x1="56" y1="145" x2="64" y2="145" stroke="currentColor" stroke-width="1"/>
<line x1="56" y1="69" x2="64" y2="69" stroke="currentColor" stroke-width="1"/>
<text x="18" y="130" font-size="12" text-anchor="middle" fill="currentColor" transform="rotate(-90 18 130)">average reward</text>
<polyline points="60.0,222.3 95.2,174.4 161.2,141.8 234.3,113.5 310.2,91.2 386.1,71.8 462.6,53.3 538.5,39.5" fill="none" stroke="#9cc9ea" stroke-width="2.5"/>
<polyline points="60.0,231.3 95.2,191.4 161.2,174.9 234.3,168.3 310.2,165.6 386.1,168.4 462.6,169.2 538.5,180.2" fill="none" stroke="#eea66f" stroke-width="2.5"/>
<circle cx="310.2" cy="165.6" r="5" fill="#eea66f" stroke="currentColor" stroke-width="1"/>
<text x="420" y="50" font-size="12" text-anchor="end" fill="currentColor">learned (proxy) reward</text>
<text x="470" y="200" font-size="12" text-anchor="middle" fill="currentColor">true reward</text>
<text x="310" y="152" font-size="11" text-anchor="middle" fill="currentColor">peak, n = 256</text>
</svg>
<figcaption>Figure 20.4. Over-optimisation in the program's toy. As best-of-n searches harder (larger n, larger KL), the learned reward of the chosen output keeps rising, but the true reward peaks at about n = 256 and then falls: the search has left the region where the learned reward was fitted. The shape matches what Gao, Schulman and Hilton (2023) measured with real reward models.</figcaption>
</figure>

The learned reward is good where it was trained: it agrees with the truth on 97.5% of fresh pairs from that
distribution, and its weights are close to the true slope at 0. Optimised against, it fails in the way Goodhart's law
predicts. In practice the standard defence is to limit optimisation, for example by penalising the KL divergence from
the starting policy, as the RLHF objective of Chapter 17 does, by training the reward model on outputs of the
optimised policy as it changes, and by using ensembles of reward models and penalising their disagreement.

### Uncertainty about the objective

Hadfield-Menell, Russell, Abbeel and Dragan (2016) formalised **cooperative inverse reinforcement learning** (CIRL):
a two-player game between a human, who knows the reward, and a robot, who does not but is rewarded by the same
function. The optimal robot policy actively learns about the reward and defers to the human when unsure. In the
**off-switch game** (Hadfield-Menell, Dragan, Abbeel and Russell 2017), a robot that is uncertain about the human's
reward and treats the human's choice to switch it off as evidence about that reward has a positive incentive to leave
the off-switch alone; a robot certain of its objective has none. The result depends on the robot's uncertainty and on
the human being rational enough; it is a model, not a guarantee, but it makes a vague worry precise enough to analyse.
Turner, Smith, Shah, Critch and Tadepalli (2021), "Optimal policies tend to seek power", proved that in many MDPs, for
most reward functions drawn at random, optimal policies prefer actions that keep more options open; this is one formal
version of the observation that very different goals share instrumental subgoals.

### Scalable oversight

Every method above assumes a person can judge the outputs. What if the task is too hard to judge (checking a long
proof, a large program, a scientific claim)? Proposals for **scalable oversight** try to amplify a weak judge:

- **Debate** (Irving, Christiano and Amodei 2018): two models argue opposite answers before a human judge. The idea
  rests on a complexity-theoretic analogy: with optimal play, a judge who can only check short arguments can decide
  questions in the class PSPACE, as in interactive proofs, so lying is harder than refuting a lie. Whether real
  models and real judges behave this way is an empirical question under study.
- **Iterated amplification** (Christiano, Shlegeris and Amodei 2018): a human, helped by copies of the current model
  answering sub-questions, produces better answers than either alone; the model is trained to imitate this team, and
  the process repeats. **Recursive reward modelling** (Leike et al. 2018) is a related scheme in which models trained
  with human feedback help humans evaluate the next model.
- **Weak-to-strong generalisation** (Burns et al. 2023) studies the situation as an experiment you can run today: a
  small model's labels are used to fine-tune a much larger one, and the question is how much of the larger model's
  ability survives supervision by a weaker teacher. They found that the strong student usually outperforms its weak
  supervisor, but recovers only part of the gap to training on true labels.

None of these is established as working at scale. They are research programmes, and the honest summary is that how to
supervise a system on tasks its supervisors cannot evaluate is an open problem.

## 20.7 Testing and evaluation: red-teaming, benchmarks, their limits

A system scores 82% on a benchmark, a competitor 85%. Which is better? A robot passed 3000 test drives without a
failure. Is it safe? Evaluation is where claims about AI systems are made, and it has its own mathematics and its own
traps.

### Benchmarks are samples

A benchmark of $n$ items is a sample from the tasks we care about, so its score is an estimate with sampling error.
The standard error of an accuracy $p$ on $n$ independent items is $\sqrt{p(1-p)/n}$; the program uses the more
accurate **Wilson interval**. On 100 items, 82% means anything from 73% to 88%. On 1000 items it is still plus or
minus 2.4 points, which is larger than many published differences between methods.

To compare two models, use the same items for both and analyse **paired** differences. Most of the variation in a
benchmark comes from item difficulty, which affects both models alike; pairing removes it. The program resamples items
(the **paired bootstrap**) and also runs **McNemar's test**, which looks only at the items where the two models
disagree: if they were equally good, those discordant items would split evenly between them. In the run, B is truly
3 points better, but on 500 items the 95% interval for the difference includes zero and $p = 0.145$: the data cannot
tell them apart. Bootstrap and tests are explained in
[Machine learning, Chapter 7](../machine-learning/07-Evaluating-Models.md#77-comparing-models-intervals-the-bootstrap-and-tests).

```python
--8<-- "books/ai/ch20_eval.py"
```

```
1. A model answers 82% of the benchmark correctly. How sure is that number?
   n =   100 items: 95% interval 0.733 to 0.883   (width 0.150)
   n =  1000 items: 95% interval 0.795 to 0.843   (width 0.048)
   n = 10000 items: 95% interval 0.812 to 0.827   (width 0.015)

2. Models A and B on the same 500 items (true accuracies 0.760 and 0.792)
   measured A 0.714, B 0.752, difference +0.038
   paired bootstrap 95% interval for B - A: -0.010 to +0.086
   items only B got right 86, only A got right 67; exact McNemar p = 0.145

3. Zero failures in n independent tests: the 95% upper bound on the failure rate
   n =   300: exact bound 9.94e-03, rule of three 3/n = 1.00e-02
   n =  3000: exact bound 9.98e-04, rule of three 3/n = 1.00e-03
   n = 30000: exact bound 9.99e-05, rule of three 3/n = 1.00e-04
   tests needed to show a failure rate below 1 in 10 000: 29956

4. Contamination: a model that is right on 60% of NEW questions has memorised part of the test
   0% of the test leaked: benchmark score 0.608, fresh-set score 0.601
   10% of the test leaked: benchmark score 0.646, fresh-set score 0.605
   30% of the test leaked: benchmark score 0.718, fresh-set score 0.609
   50% of the test leaked: benchmark score 0.783, fresh-set score 0.603

5. Finding a rare failure in a 10-dimensional input space
   random testing: 1 failures in 200000 queries, first at query 40720
   local search on the margin: first failure after 1096 queries
```

### What testing cannot show

If a system fails independently with probability $p$ on each test, the chance of seeing no failure in $n$ tests is
$(1 - p)^n$. Setting this to 0.05 gives the 95% upper bound $p = 1 - 0.05^{1/n} \approx (\ln 20)/n \approx 3/n$, the
**rule of three** (Hanley and Lippman-Hand 1983, "If nothing goes wrong, is everything all right?"). Three thousand
flawless test drives show only that the failure rate is below about 1 in 1000 per drive; showing 1 in 10 000 takes
29 956 flawless trials, and every factor of 10 costs 10 times more testing. Butler and Finelli (1993), "The
infeasibility of quantifying the reliability of life-critical real-time software", made this argument for avionics
software: the failure rates required (of the order of $10^{-9}$ per hour) cannot be demonstrated by testing at all. This
is why safety-critical systems combine testing with design arguments and proofs (20.4), and why rare-event
simulation, which deliberately oversamples dangerous situations and reweights by importance sampling, is used to test
autonomous vehicles (O'Kelly, Sinha, Namkoong, Duchi and Tedrake 2018).

### Red-teaming: searching for failures

Random testing finds failures in proportion to their frequency, so rare failures are rarely found (in the program,
zero in 200 000 random queries). **Red-teaming** searches for them deliberately, using any signal of "closer to
failing": in the program, a simple local search on the system's margin finds a failure in 251 queries. For software,
**fuzzing** does this by mutating inputs guided by code coverage; for neural networks, DeepXplore (Pei, Cao, Yang and
Jana 2017) searched for inputs on which several models disagree. **Behavioural testing** (CheckList, Ribeiro, Wu,
Guestrin and Singh 2020) writes test cases from templates of capabilities ("negation flips sentiment") and **metamorphic
relations** (changing a name in a sentence should not change its sentiment), which need no labels. For language models,
people and models are both used as red-teamers: Perez et al. (2022), "Red teaming language models with language
models", used one language model to generate test questions for another and a classifier to detect harmful replies,
finding many failures automatically. **Adversarial data collection** builds benchmarks from items that defeat current
models, as in Adversarial NLI (Nie et al. 2020) and Dynabench (Kiela et al. 2021), so that the benchmark does not
saturate as quickly.

### Benchmarks and their limits

- **Saturation and overfitting to the benchmark.** When a research field tunes many models on the same public test
  set, the reported scores become optimistic estimates. Recht, Roelofs, Schmidt and Shankar (2019) rebuilt test sets
  for CIFAR-10 and ImageNet following the original procedures and found accuracy drops for essentially all models
  tested, though the models' ranking was largely preserved.
- **Contamination.** A model trained on web-scale data may have seen the test items. Then the benchmark measures
  memory, not ability. The program's simulation shows the arithmetic: if half the test set leaked, a model that is
  right 60% of the time on new questions scores 80%. The remedy is a fresh test set written after the training data was
  collected, or checks for overlap between training data and test items; the GPT-3 paper (Brown et al. 2020) reported
  such overlap analyses.
- **Construct validity.** A benchmark measures a narrow task that is supposed to stand for a broad ability. A high
  score on multiple-choice questions about a subject is not the same as competence in it, and a benchmark is only as
  meaningful as that link. Holistic evaluations such as HELM (Liang et al. 2022) measure many scenarios and many
  metrics (accuracy, calibration, robustness, efficiency) side by side, so that no single number stands in for
  everything.

The thread through the whole chapter is the same: an optimiser exploits the gap between what is measured and what is
meant. That applies to the researchers who optimise against a benchmark as much as to the agents who optimise against
a reward.

## Check yourself

??? question "1. A loss has input gradient g = (3, −1, 0.5). Which perturbation with max-norm at most 0.1 increases its linear approximation most, and by how much?"
    By the lemma of 20.2, $\delta = 0.1\,\mathrm{sign}(g) = (0.1, -0.1, 0.1)$, and the increase is
    $0.1 \lVert g \rVert_1 = 0.1 \times (3 + 1 + 0.5) = 0.45$. Check: $g^{\mathsf T}\delta = 0.3 + 0.1 + 0.05 = 0.45$. Under a
    Euclidean budget of 0.1 the best step would instead be $0.1\,g/\lVert g \rVert_2$, with gain
    $0.1\lVert g \rVert_2 \approx 0.32$: the max-norm ball lets every coordinate move at once.

??? question "2. Run interval bound propagation by hand on y = ReLU(x1 − x2) + ReLU(x1 + x2 − 1) with x1, x2 in [0, 1]. Compare with the true range."
    First pre-activation: $x_1 - x_2 \in [-1, 1]$, so the ReLU is in $[0, 1]$. Second: $x_1 + x_2 - 1 \in [-1, 1]$, ReLU in
    $[0, 1]$. Sum: IBP says $y \in [0, 2]$. True range: if $x_1 + x_2 \le 1$ the second term is 0 and
    $y = \max(x_1 - x_2, 0) \le 1$; if $x_1 + x_2 > 1$ then $y \le (x_1 - x_2)^+ + x_1 + x_2 - 1$, which is at most
    $2x_1 - 1 \le 1$ when $x_1 \ge x_2$ and $x_1 + x_2 - 1 \le 1$ otherwise. So $y \in [0, 1]$ (both values reached, at
    (0, 0) and (1, 0)). IBP's upper bound 2 is sound but twice too large: it treats the two hidden units as independent,
    while both depend on the same $x_1$ and $x_2$ and cannot both be 1. Sampling a million random points confirms a
    maximum just below 1.

??? question "3. Split conformal prediction with n = 19 calibration scores. Which calibration score is the threshold for α = 0.1, for α = 0.05, and what happens for α = 0.01?"
    $k = \lceil (n + 1)(1 - \alpha) \rceil$. For $\alpha = 0.1$: $k = \lceil 18 \rceil = 18$, the 18th smallest score;
    coverage is $18/20 = 0.90$ exactly. For $\alpha = 0.05$: $k = 19$, the largest score, coverage $19/20 = 0.95$. For
    $\alpha = 0.01$: $k = \lceil 19.8 \rceil = 20 > n$; no calibration score is large enough, so the set must contain every
    label (the threshold is $+\infty$). With only 19 examples you cannot certify 99% coverage; you need at least 99.

??? question "4. Prove that temperature scaling never changes a classifier's predictions, and explain why it can still change the NLL."
    The prediction is $\arg\max_k \mathrm{softmax}(z/T)_k = \arg\max_k e^{z_k/T}$. For $T > 0$, $z_k / T$ is an increasing
    function of $z_k$ and the exponential is increasing, so the order of the classes, and the largest one, are the same
    for every $T$. Accuracy is therefore unchanged. The NLL $-\log \mathrm{softmax}(z/T)_y$ depends on the size of the
    probabilities, not only their order: a larger $T$ flattens them, which lowers the loss on examples where the model was
    confidently wrong and raises it slightly on examples where it was confidently right. On an overconfident model the
    first effect wins, so the NLL-minimising $T$ is above 1 (3.85 in the program).

??? question "5. Four predictions have confidences 0.9, 0.9, 0.6, 0.6 and are correct, wrong, correct, correct. Compute the ECE with the two bins (0.5, 0.75] and (0.75, 1]."
    Bin (0.5, 0.75]: two predictions, mean confidence 0.6, accuracy 1, gap 0.4. Bin (0.75, 1]: two predictions, mean
    confidence 0.9, accuracy 0.5, gap 0.4. ECE $= \tfrac{2}{4}(0.4) + \tfrac{2}{4}(0.4) = 0.4$. The model is
    underconfident in one bin and overconfident in the other; ECE adds the gaps without letting them cancel.

??? question "6. Derive the rule of three, and say how many failure-free tests show a failure rate below 1 in a million with 95% confidence."
    No failures in $n$ independent tests has probability $(1-p)^n$. The 95% upper bound is the $p$ at which this equals
    0.05: $n \ln(1-p) = \ln 0.05$, and since $\ln(1-p) \approx -p$ for small $p$, $p \approx \ln 20 / n \approx 2.996/n$. For
    $p = 10^{-6}$ you need $n \approx 3 \times 10^6$ failure-free tests (the exact value is
    $\lceil \ln 0.05 / \ln(1 - 10^{-6}) \rceil = 2\,995\,731$). Each further factor of 10 in reliability costs a factor of 10
    in tests.

??? question "7. For F(x) = x1 · x2 with baseline 0, compute integrated gradients and gradient times input. Which satisfies completeness?"
    Along the path $\alpha x$, $\partial F / \partial x_1 = \alpha x_2$, so $\mathrm{IG}_1 = x_1 \int_0^1 \alpha x_2\,d\alpha = x_1 x_2 / 2$,
    and likewise $\mathrm{IG}_2 = x_1 x_2 / 2$. The sum is $x_1 x_2 = F(x) - F(0)$: complete, and split equally by
    symmetry. Gradient times input gives $x_1 \cdot x_2$ for each feature, summing to $2 x_1 x_2$, twice the actual change.
    It is complete only for linear functions.

??? question "8. Write code: for a linear classifier sign(w · x + b), find the smallest max-norm perturbation that flips a correctly classified point, and check it with a one-step attack."
    For a linear score $s(x) = w \cdot x + b$, the lemma of 20.2 says a step $\delta$ with $\lVert \delta \rVert_\infty \le \varepsilon$
    can change $s$ by at most $\varepsilon \lVert w \rVert_1$, attained at $\delta = -\varepsilon\,\mathrm{sign}(s)\,\mathrm{sign}(w)$.
    So the smallest flipping radius is exactly $\lvert s(x) \rvert / \lVert w \rVert_1$.
    ```python
    import numpy as np
    rng = np.random.default_rng(2)
    w, b = rng.normal(size=10), 0.3
    x = rng.normal(size=10)
    s = w @ x + b
    eps_star = abs(s) / np.abs(w).sum()
    print(f"eps* = {eps_star:.4f}")
    for eps in (0.99 * eps_star, 1.01 * eps_star):
        xa = x - eps * np.sign(s) * np.sign(w)
        print(f"eps {eps:.4f}: score {s:+.4f} -> {w @ xa + b:+.4f}")
    ```
    Output: `eps* = 0.3914`, then `eps 0.3874: score +3.3048 -> +0.0330` and `eps 0.3953: score +3.3048 -> -0.0330`.
    The score keeps its sign just below $\varepsilon^\ast$ and flips just above it. For a linear model the one-step
    attack is optimal and the certificate is exact, which is why verification is easy for linear models and hard for
    deep ones.

??? question "9. Why does a ReLU classifier become nearly certain far from its training data? Would a network with sigmoid units in every layer behave the same?"
    The ReLU network is piecewise affine; along any ray it eventually stays in one linear region, so its logits grow
    linearly in $t$ and the softmax of a strictly largest logit tends to 1 (proof in 20.3). With sigmoid (or tanh) hidden
    units, the hidden activations saturate to constants far away, so the logits tend to finite limits and the
    confidence tends to some fixed value less than 1, which can still be high. Neither architecture says "I have never
    seen anything like this" by itself; that requires a score that measures distance from the data, an ensemble, or an
    explicit model of the input distribution.

??? question "10. In best-of-n, the true reward peaked at n = 256 in the program. Give two reasons the peak moves, and one change to the setup that would remove the fall entirely."
    The peak moves to larger $n$ if the learned reward matches the truth over a wider range, for example if preferences
    are collected on more varied outputs (a larger spread than 0.5), or if the reward model is more flexible (a quadratic
    term in feature 0 would capture the bend). It moves to smaller $n$ if the base distribution's tails are heavier, so
    that extreme candidates appear sooner. The fall disappears if the learned reward is a strictly increasing function of
    the true one: then the output with the highest learned reward also has the highest true reward, and more search can
    only help. Over-optimisation is the gap between the two orderings.

??? question "11. Potential-based shaping (Ng, Harada and Russell 1999) adds F(s, s') = γΦ(s') − Φ(s) to every reward. Show it cannot create a profitable loop like the boat's, and suggest how to use it for the bonus."
    Along any trajectory $s_0, s_1, \dots, s_T$ the added rewards sum (with discounting) to
    $\sum_{t=0}^{T-1} \gamma^t(\gamma\Phi(s_{t+1}) - \Phi(s_t)) = \gamma^T \Phi(s_T) - \Phi(s_0)$, a telescoping sum. So the
    shaping changes the discounted return of every policy by an amount that depends only on the start state (and a term
    that vanishes as $T \to \infty$ for bounded $\Phi$); the ranking of policies, and hence the optimal policy, is unchanged.
    A loop returning to its start state gains $(\gamma^{k} - 1)\Phi(s)$ per round, never a positive amount when
    $\Phi \ge 0$. To use the designer's intuition "the bonus square is a good place to be on the way", give it a potential
    $\Phi(2) > 0$ instead of a reward: the boat is encouraged to get there, and gains nothing from going back and forth.
    Ng, Harada and Russell also proved the converse: potential-based shaping is the only additive shaping guaranteed to
    preserve optimal policies in every MDP.

??? question "12. A benchmark has 2000 items. Model A scores 71.0%, model B 72.0%. Without the per-item results, can you say B is better? What would you ask for?"
    The standard error of each score is about $\sqrt{0.71 \times 0.29 / 2000} \approx 0.010$, so each score is uncertain by
    about $\pm 2$ points at 95%, and the unpaired difference of 1 point is well within noise. But a paired analysis can be
    much sharper: if A and B disagree on only, say, 60 items and B wins 40 of them, McNemar's exact test gives
    $p \approx 0.013$ and B is better. Ask for the per-item results (to pair them), the number of runs and their spread
    (to see the variation from random seeds or sampling), and evidence that neither model was tuned on, or trained on, the
    test items.

## What you learned

- An objective is a proxy for an intention, and optimisation finds where the two differ: specification gaming,
  reward hacking and goal misgeneralisation are documented in many systems, and a seven-square MDP reproduces the boat
  race exactly. Shortcut features make classifiers fail under distribution shift, sometimes invisibly.
- In the max-norm the sign of the gradient is the steepest step, which gives FGSM and PGD; adversarial training solves
  a min-max problem; and an attack's failure proves nothing, as the broken defences of 2018 showed.
- Temperature scaling repairs overconfidence without changing predictions; split conformal prediction gives sets with
  guaranteed coverage under exchangeability, proved by a rank argument; ReLU classifiers are provably confident far
  from their data, so OOD detection needs other scores.
- Interval bound propagation is sound but loose (the wrapping effect); branch and bound makes it complete on small
  networks; complete verification is NP-complete in general, and formal methods are often best applied to a small
  verified safety layer around the learned part.
- Integrated gradients satisfy completeness; explanations must pass sanity checks; probes show what information is
  present, and only interventions show what is used.
- Rewards can be learned from preferences with the Bradley-Terry model, but a learned reward is a proxy too: optimised
  hard, its true value rises and then falls. IRL is ill-posed without assumptions, and scalable oversight is open.
- Benchmark scores carry sampling error, comparisons must be paired, zero failures in $n$ tests bounds the failure rate
  only at about $3/n$, contamination inflates scores, and searching for failures beats random testing.

**Next:** [Chapter 21](21-Where-AI-Goes.md) maps what AI can and cannot do today and the open research questions of
the whole field.

## Further reading

- S. Russell and P. Norvig, *Artificial Intelligence: A Modern Approach*, 4th ed., 2020: chapter 22 (including
  apprenticeship learning and inverse reinforcement learning) and chapter 27 (philosophy, ethics and safety of AI, which
  also covers non-technical topics beyond this chapter).
- D. Amodei, C. Olah, J. Steinhardt, P. Christiano, J. Schulman and D. Mané, "Concrete problems in AI safety", 2016;
  V. Krakovna and colleagues, "Specification gaming: the flip side of AI ingenuity", 2020 (with the public list of
  examples); J. Lehman and colleagues, "The surprising creativity of digital evolution", *Artificial Life* 26, 2020;
  L. Langosco, J. Koch, L. Sharkey, J. Pfau and D. Krueger, "Goal misgeneralization in deep reinforcement learning",
  ICML 2022; R. Geirhos and colleagues, "Shortcut learning in deep neural networks", *Nature Machine Intelligence* 2, 2020.
- C. Szegedy and colleagues, "Intriguing properties of neural networks", ICLR 2014; I. Goodfellow, J. Shlens and
  C. Szegedy, "Explaining and harnessing adversarial examples", ICLR 2015; A. Madry, A. Makelov, L. Schmidt, D. Tsipras
  and A. Vladu, "Towards deep learning models resistant to adversarial attacks", ICLR 2018; A. Athalye, N. Carlini and
  D. Wagner, "Obfuscated gradients give a false sense of security", ICML 2018.
- C. Guo, G. Pleiss, Y. Sun and K. Q. Weinberger, "On calibration of modern neural networks", ICML 2017; V. Vovk,
  A. Gammerman and G. Shafer, *Algorithmic Learning in a Random World*, 2005; A. N. Angelopoulos and S. Bates, "A gentle
  introduction to conformal prediction and distribution-free uncertainty quantification", 2021; M. Hein,
  M. Andriushchenko and J. Bitterwolf, "Why ReLU networks yield high-confidence predictions far away from the training
  data and how to mitigate the problem", CVPR 2019; D. Hendrycks and K. Gimpel, "A baseline for detecting misclassified
  and out-of-distribution examples in neural networks", ICLR 2017.
- G. Katz, C. Barrett, D. Dill, K. Julian and M. Kochenderfer, "Reluplex: an efficient SMT solver for verifying deep
  neural networks", CAV 2017; S. Gowal and colleagues, "On the effectiveness of interval bound propagation for training
  verifiably robust models", 2018; J. Cohen, E. Rosenfeld and Z. Kolter, "Certified adversarial robustness via
  randomized smoothing", ICML 2019; C. Liu and colleagues, "Algorithms for verifying deep neural networks", *Foundations
  and Trends in Optimization* 4, 2021; G. Klein and colleagues, "seL4: formal verification of an OS kernel", SOSP 2009;
  X. Leroy, "Formal verification of a realistic compiler", *Communications of the ACM* 52, 2009; G. J. Holzmann, "Mars
  code", *Communications of the ACM* 57, 2014; M. Alshiekh and colleagues, "Safe reinforcement learning via shielding",
  AAAI 2018.
- M. Sundararajan, A. Taly and Q. Yan, "Axiomatic attribution for deep networks", ICML 2017; J. Adebayo and colleagues,
  "Sanity checks for saliency maps", NeurIPS 2018; J. Hewitt and P. Liang, "Designing and interpreting probes with
  control tasks", EMNLP 2019; K. Meng, D. Bau, A. Andonian and Y. Belinkov, "Locating and editing factual associations in
  GPT", NeurIPS 2022; C. Molnar, *Interpretable Machine Learning* (free online).
- A. Y. Ng and S. Russell, "Algorithms for inverse reinforcement learning", ICML 2000; B. Ziebart, A. Maas, J. A.
  Bagnell and A. Dey, "Maximum entropy inverse reinforcement learning", AAAI 2008; P. Christiano and colleagues, "Deep
  reinforcement learning from human preferences", NeurIPS 2017; L. Gao, J. Schulman and J. Hilton, "Scaling laws for
  reward model overoptimization", ICML 2023; D. Hadfield-Menell, S. Russell, P. Abbeel and A. Dragan, "Cooperative
  inverse reinforcement learning", NeurIPS 2016; G. Irving, P. Christiano and D. Amodei, "AI safety via debate", 2018;
  C. Burns and colleagues, "Weak-to-strong generalization", 2023.
- J. A. Hanley and A. Lippman-Hand, "If nothing goes wrong, is everything all right?", *JAMA* 249, 1983; R. W. Butler
  and G. B. Finelli, "The infeasibility of quantifying the reliability of life-critical real-time software", *IEEE
  Transactions on Software Engineering* 19, 1993; B. Recht, R. Roelofs, L. Schmidt and V. Shankar, "Do ImageNet
  classifiers generalize to ImageNet?", ICML 2019; M. T. Ribeiro, T. Wu, C. Guestrin and S. Singh, "Beyond accuracy:
  behavioral testing of NLP models with CheckList", ACL 2020; E. Perez and colleagues, "Red teaming language models with
  language models", EMNLP 2022; P. Liang and colleagues, "Holistic evaluation of language models", 2022.
- On this site: [Machine learning, Chapter 22](../machine-learning/22-Machine-Learning-in-Practice.md) (shift,
  fairness, interpretability, adversarial examples, privacy) and [Chapter 23](../machine-learning/23-Where-Machine-Learning-Goes.md)
  (mechanistic interpretability); [Chapter 14](14-Making-Decisions.md) and [Chapter 15](15-Reinforcement-Learning.md)
  of this book; the [Algorithms book, Chapter 14](../algorithms/14-Backtracking-and-Branch-and-Bound.md) (branch and
  bound) and [Chapter 22](../algorithms/22-NP-Completeness.md) (NP-completeness).
