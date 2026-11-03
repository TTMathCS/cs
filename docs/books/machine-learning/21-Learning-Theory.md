# 21. Why learning works: learning theory

*Every chapter so far has trained a model on some examples and then trusted it on new ones. Why should that work?
A model that is perfect on the data it has seen can be useless on the next example, and yet most of the time it is
not. This chapter answers the question with proofs. You will build the PAC framework, prove that a finite set of
hypotheses can be learned from a number of examples that grows only with the logarithm of its size, measure the
richness of infinite classes with the VC dimension and Rademacher complexity, turn the bounds into a rule for
choosing model size, and then meet, honestly, the modern facts about deep networks that these classical tools do not
explain.*

!!! abstract "In this chapter"
    **You will learn:**

    - how to state precisely what "the model works on new data" means: true risk, empirical risk, and the PAC
      definition with its two numbers $\varepsilon$ and $\delta$
    - to prove, with Hoeffding's inequality and the union bound, that a finite class needs about
      $\ln|\mathcal H|/\varepsilon$ examples (or $\ln|\mathcal H|/\varepsilon^2$ with noise)
    - what shattering, the growth function and the VC dimension are, how to compute them for rays, intervals,
      half-planes and rectangles, and why the number of parameters is the wrong measure
    - Rademacher complexity, Massart's lemma, and the margin bound that explains support vector machines
    - the bias-complexity trade-off and structural risk minimisation, run from scratch
    - what the theory does not explain: networks that fit random labels, double descent, the implicit bias of
      gradient descent, and the neural tangent kernel

    **You need:** [Chapter 1](01-What-Is-Machine-Learning.md) (training and test data, no free lunch),
    [Chapter 7](07-Evaluating-Models.md) (honest evaluation), [Chapter 8](08-Overfitting-and-Regularization.md)
    (bias and variance), and basic probability (https://math.akadian.ca/books/probability/). The tail bounds of the
    Algorithms book's [Chapter 21](../algorithms/21-Randomized-and-Amortized-Analysis.md) help but are not
    required. Sections 21.4 and 21.6 use [Chapter 10](10-Support-Vector-Machines.md) and
    [Chapter 15](15-Neural-Networks-and-Backpropagation.md).

    **Levels:** 21.1 is beginner; 21.2 and 21.5 are intermediate; 21.3 and 21.4 are advanced; 21.6 is expert.

## 21.1 The question: why does a model that fits training data work on new data?

Here is the puzzle in its simplest form. You have $m$ labelled examples. You search through a set of possible
models, pick the one that makes the fewest mistakes on them, and report it. Its error on those $m$ examples is, say,
3%. What is its error on the next example, one it has never seen?

The honest first answer is: we cannot say, unless we assume something. The examples could be a trick. So learning
theory starts by writing down the assumptions, and the words for them.

**The setting.** There is a set $\mathcal X$ of possible inputs (images, rows of a table, points in the plane) and a
set $\mathcal Y$ of labels; for most of this chapter $\mathcal Y = \{0, 1\}$ or $\{-1, +1\}$, a yes-or-no question.
There is an unknown probability distribution $\mathcal D$ over pairs $(x, y)$: it says how often each input appears
and how its label is chosen. The training set $S = ((x_1, y_1), \dots, (x_m, y_m))$ is a list of $m$ pairs drawn
**independently and identically distributed** (i.i.d.) from $\mathcal D$: each example is a fresh, independent draw
from the same source. This is the one big assumption. Chapter 22 is about what happens in practice when it fails.

A **hypothesis** is a function $h : \mathcal X \to \mathcal Y$, a candidate model. A **hypothesis class**
$\mathcal H$ is the set of hypotheses the learner is allowed to choose from: all lines in the plane, all decision
trees of depth 3, all networks of a given shape with any weights. The **loss** of $h$ on one example is 1 if
$h(x) \ne y$ and 0 otherwise (the zero-one loss). Two averages of it matter.

The **true risk** (or true error, or generalisation error) is the probability of a mistake on a fresh example:

$$
L_{\mathcal D}(h) = \Pr_{(x, y) \sim \mathcal D}\big[h(x) \ne y\big].
$$

The **empirical risk** (training error) is the fraction of mistakes on the sample:

$$
L_S(h) = \frac{1}{m}\sum_{i=1}^{m} \mathbf 1\big[h(x_i) \ne y_i\big].
$$

The learner can compute $L_S$, never $L_{\mathcal D}$. The simplest learning rule, **empirical risk minimisation**
(ERM), returns any $h_S \in \mathcal H$ with the smallest $L_S$. Every model in this book that minimised a training
loss was doing a version of ERM.

**One fixed hypothesis is easy.** If $h$ is chosen before looking at the data, then $L_S(h)$ is the average of $m$
independent coin flips that come up "mistake" with probability $L_{\mathcal D}(h)$. The law of large numbers says
the average approaches the probability, and Hoeffding's inequality (21.2) says how fast: the gap is rarely more than
about $1/\sqrt m$. That is exactly why a held-out test set works (Chapter 7): the model was fixed before the test
set was looked at.

**A chosen hypothesis is not.** ERM looks at the data and then chooses. Consider the class of all functions from
$\mathcal X$ to $\{0, 1\}$ and the "memoriser" that answers $y_i$ on each training input $x_i$ and 0 everywhere else.
Its training error is zero. If $\mathcal X$ is large and the true labels are balanced coin flips, its true error is
about one half. The gap between $L_S$ and $L_{\mathcal D}$ is not small at all. What went wrong is selection: with a
class that rich, *some* hypothesis fits any sample by luck, and ERM finds it.

So the real question is not "is $L_S(h)$ close to $L_{\mathcal D}(h)$ for one $h$?" but

> Is $L_S(h)$ close to $L_{\mathcal D}(h)$ for **every** $h \in \mathcal H$ at the same time?

This property is called **uniform convergence**. If it holds, it does not matter which hypothesis ERM selects; the
one it picks has a training error that tells the truth. The whole chapter is about when uniform convergence holds,
how many examples it needs, and which property of $\mathcal H$ controls it. The answer will be a measure of how many
different ways the class can label a sample, and the surprise at the end is that for deep networks this measure is
huge and yet they still generalise.

Two more words. The **generalisation gap** is $L_{\mathcal D}(h) - L_S(h)$. The **sample complexity** of a learning
problem is the number of examples needed to make the true risk small with high probability.

## 21.2 PAC learning and the finite-class bound

*Level: intermediate.*

In 1984 Leslie Valiant, a computer scientist at Harvard, published "A Theory of the Learnable" in *Communications of
the ACM*. He wanted a definition of learning as precise as the definition of an efficient algorithm, so that one
could prove that some things are learnable and others are not. His answer is called **PAC learning**: probably
approximately correct.

The two words "probably" and "approximately" are two numbers. **Approximately correct**: the learned hypothesis has
true error at most $\varepsilon$ (a small accuracy parameter, like 0.05). **Probably**: this happens with probability
at least $1 - \delta$ over the random draw of the training set ($\delta$ is the confidence parameter, like 0.05). We
cannot ask for certainty, because a very unlucky sample (the same example drawn $m$ times) teaches nothing.

**Definition (PAC learnable, realizable case).** A class $\mathcal H$ is PAC learnable if there is a learning
algorithm $A$ and a function $m_{\mathcal H}(\varepsilon, \delta)$ such that: for every $\varepsilon, \delta \in (0, 1)$,
every distribution $\mathcal D$ over $\mathcal X$, and every target $f \in \mathcal H$ that produces the labels
$y = f(x)$, if $A$ receives $m \ge m_{\mathcal H}(\varepsilon, \delta)$ i.i.d. examples then, with probability at
least $1 - \delta$, $A$ returns $h$ with $L_{\mathcal D}(h) \le \varepsilon$.

"Realizable" means the true labelling rule is in the class, so some hypothesis has zero true error. Valiant's
definition also asked that $A$ run in time polynomial in $1/\varepsilon$, $1/\delta$ and the size of the examples;
learning theory today often separates the statistical question (how many examples) from the computational one (how
much time). Pitt and Valiant (1988) showed the two really differ: 3-term DNF formulas (an "or" of three "and"s)
need few examples, yet finding a 3-term DNF consistent with a sample is NP-hard, so learning them with that
hypothesis class is hard unless RP = NP. In this chapter we stay with the statistical question.

### The realizable bound

**Theorem 21.1 (finite class, realizable).** Let $\mathcal H$ be finite and suppose some $f \in \mathcal H$ labels
the data. If

$$
m \ge \frac{\ln|\mathcal H| + \ln(1/\delta)}{\varepsilon},
$$

then with probability at least $1 - \delta$, every $h \in \mathcal H$ with $L_S(h) = 0$ has
$L_{\mathcal D}(h) \le \varepsilon$. In particular ERM is a PAC learner.

*Proof.* Call a hypothesis **bad** if $L_{\mathcal D}(h) > \varepsilon$. Fix one bad $h$. On each fresh example it
is right with probability $1 - L_{\mathcal D}(h) < 1 - \varepsilon$, and the examples are independent, so

$$
\Pr\big[L_S(h) = 0\big] < (1 - \varepsilon)^m \le e^{-\varepsilon m},
$$

using $1 - t \le e^{-t}$ (true for every real $t$, since $e^{-t}$ is convex and $1 - t$ is its tangent line at 0).
ERM fails only if *some* bad hypothesis is consistent with the sample. The **union bound** says the probability that
at least one of several events happens is at most the sum of their probabilities. There are at most $|\mathcal H|$ bad
hypotheses, so

$$
\Pr\big[\exists \text{ bad } h \text{ with } L_S(h) = 0\big] \le |\mathcal H|\, e^{-\varepsilon m}.
$$

This is at most $\delta$ when $\varepsilon m \ge \ln|\mathcal H| + \ln(1/\delta)$, which is the condition on $m$.
$\square$

Read the bound slowly. The number of examples grows like $1/\varepsilon$: halving the error you will tolerate doubles
the data. It grows like $\ln(1/\delta)$: going from 95% to 99.9% confidence costs only a few more examples. And it
grows with the **logarithm** of the class size. A class with a million hypotheses needs only about
$\ln 10^6 \approx 13.8$ "units" more than a class with one. If each hypothesis can be written down in $b$ bits,
then $|\mathcal H| \le 2^b$ and $m \approx b\ln 2/\varepsilon$: the sample size is proportional to the description
length of the hypothesis. Blumer, Ehrenfeucht, Haussler and Warmuth called this "Occam's razor" in a 1987 paper:
short explanations that fit the data are, provably, likely to be right.

**A worked example by hand.** Let $\mathcal X = [0, 1]$ and let $\mathcal H$ be the 101 threshold rules
$h_k(x) = \mathbf 1[x \ge k/100]$, $k = 0, 1, \dots, 100$. The target is $h_{37}$, and $x$ is uniform on $[0, 1]$,
so the true error of $h_k$ is the length of the interval between $k/100$ and $0.37$, which is $|k - 37|/100$. Take
$\varepsilon = \delta = 0.05$. Then $\ln 101 = 4.615$, $\ln 20 = 2.996$, and

$$
m \ge \frac{4.615 + 2.996}{0.05} = 152.2, \quad\text{so } m = 153 \text{ suffices.}
$$

The program below checks this the hard way. For each sample size it draws 20000 training sets, finds the *worst*
hypothesis that is still consistent with the sample (an adversarial ERM, to test the theorem at its weakest point),
and counts how often its true error exceeds $\varepsilon$.

### Hoeffding's inequality

Without the realizable assumption no hypothesis may have zero training error. Labels can be noisy, or the target can
lie outside the class. We then need to know how far $L_S(h)$ strays from $L_{\mathcal D}(h)$ for a fixed $h$, which
is a question about averages of independent bounded variables.

**Theorem 21.2 (Hoeffding, 1963).** Let $Z_1, \dots, Z_m$ be independent random variables with values in $[0, 1]$
and let $\bar Z = \frac1m\sum Z_i$ and $\mu = E[\bar Z]$. Then for every $\varepsilon > 0$,

$$
\Pr\big[\bar Z - \mu \ge \varepsilon\big] \le e^{-2m\varepsilon^2}
\quad\text{and}\quad
\Pr\big[|\bar Z - \mu| \ge \varepsilon\big] \le 2e^{-2m\varepsilon^2}.
$$

*Proof.* The idea, due to Chernoff and Bernstein, is to exponentiate. For any $\lambda > 0$, Markov's inequality
applied to the positive variable $e^{\lambda m(\bar Z - \mu)}$ gives

$$
\Pr\big[\bar Z - \mu \ge \varepsilon\big] \le e^{-\lambda m \varepsilon}\, E\big[e^{\lambda m(\bar Z - \mu)}\big]
= e^{-\lambda m\varepsilon} \prod_{i=1}^{m} E\big[e^{\lambda (Z_i - E Z_i)}\big],
$$

where independence turns the expectation of a product into a product of expectations. **Hoeffding's lemma** says
that a variable $X$ with $E X = 0$ and $a \le X \le b$ satisfies $E[e^{\lambda X}] \le e^{\lambda^2(b-a)^2/8}$. (Its
proof: by convexity $e^{\lambda x}$ lies below the chord between $a$ and $b$, so $E e^{\lambda X}$ is at most a
function of $\lambda$ whose logarithm $\varphi$ has $\varphi(0) = \varphi'(0) = 0$ and $\varphi'' \le (b-a)^2/4$;
Taylor's theorem finishes it.) Here $b - a = 1$, so each factor is at most $e^{\lambda^2/8}$ and

$$
\Pr\big[\bar Z - \mu \ge \varepsilon\big] \le \exp\Big(-\lambda m\varepsilon + \frac{m\lambda^2}{8}\Big).
$$

The exponent is smallest at $\lambda = 4\varepsilon$, where it equals $-2m\varepsilon^2$. The same argument for
$-Z_i$ bounds the other tail, and the union bound adds the two. $\square$

The Algorithms book proves the closely related Chernoff bounds in
[Chapter 21](../algorithms/21-Randomized-and-Amortized-Analysis.md); Hoeffding's version is the one learning theory
uses because it needs nothing except independence and a bounded range.

**By hand.** With $m = 100$ fair coin flips and $\varepsilon = 0.1$, the bound is $2e^{-2 \cdot 100 \cdot 0.01} =
2e^{-2} = 0.271$. The exact probability of 60 or more heads or 40 or fewer is 0.0569. The bound is true but about
five times too large; Hoeffding pays for working with every distribution on $[0, 1]$, including the worst one.

### The agnostic bound

**Theorem 21.3 (finite class, agnostic).** Let $\mathcal H$ be finite and $\mathcal D$ arbitrary. With probability
at least $1 - \delta$ over a sample of size $m$,

$$
\text{for all } h \in \mathcal H:\quad \big|L_S(h) - L_{\mathcal D}(h)\big| \le
\sqrt{\frac{\ln(2|\mathcal H|/\delta)}{2m}} .
$$

Consequently ERM returns $h_S$ with $L_{\mathcal D}(h_S) \le \min_{h \in \mathcal H} L_{\mathcal D}(h) + 2\varepsilon$
whenever $m \ge \ln(2|\mathcal H|/\delta)/(2\varepsilon^2)$.

*Proof.* For a fixed $h$, the losses $Z_i = \mathbf 1[h(x_i) \ne y_i]$ are independent, lie in $\{0, 1\}$, and have
mean $L_{\mathcal D}(h)$. Hoeffding gives $\Pr[|L_S(h) - L_{\mathcal D}(h)| > \varepsilon] \le 2e^{-2m\varepsilon^2}$.
The union bound over the $|\mathcal H|$ hypotheses gives failure probability at most
$2|\mathcal H|e^{-2m\varepsilon^2}$; setting this equal to $\delta$ and solving for $\varepsilon$ gives the formula.
For the consequence, let $h^\ast$ be the best hypothesis in the class. On the good event,

$$
L_{\mathcal D}(h_S) \le L_S(h_S) + \varepsilon \le L_S(h^\ast) + \varepsilon \le L_{\mathcal D}(h^\ast) + 2\varepsilon,
$$

where the middle step is the definition of ERM. $\square$

This is called **agnostic** PAC learning, because the learner is agnostic about whether the class contains the truth;
it only promises to be nearly as good as the best member of the class. The price of agnosticism is the square: the
sample size grows like $1/\varepsilon^2$ instead of $1/\varepsilon$. The reason is variance. When the true error of
a hypothesis is near zero, its training error has tiny variance and a single mistake is strong evidence; when it is
near one half, telling 0.45 from 0.50 takes about $1/\varepsilon^2$ coin flips.

The program puts both theorems to the test. Part 3 uses the same 101 thresholds but flips each label with probability
0.1, so the best hypothesis has true error 0.1. It measures the largest gap over the whole class,
$\sup_h |L_S(h) - L_{\mathcal D}(h)|$, and the excess risk of ERM.

```python
--8<-- "books/machine-learning/ch21_finite_class.py"
```

```
1. Hoeffding: P(|mean - p| >= eps) for m coin flips
    p     m    eps   simulated   bound 2exp(-2 m eps^2)
   0.5   100  0.10     0.05854     0.27067
   0.1   100  0.10     0.00210     0.27067
   0.5   400  0.05     0.05020     0.27067
   0.5   400  0.10     0.00020     0.00067

2. realizable: |H| = 101, eps = 0.05, delta = 0.05
   bound says m >= (ln|H| + ln(1/delta)) / eps = 153
   m    P(worst consistent h has error > eps)
    20   0.5006
    40   0.1625
    60   0.0489
    80   0.0151
   100   0.0048
   153   0.0003

3. agnostic: labels flipped with probability 0.1, ERM over the same 101 thresholds
    m    mean sup|L_S - L|   95th pct   bound sqrt(ln(2|H|/delta)/(2m))   mean excess risk
    100   0.0867            0.1360     0.2038                            0.0088
    400   0.0434            0.0660     0.1019                            0.0008
   1600   0.0215            0.0339     0.0509                            0.0000

4. samples needed for eps = 0.05, delta = 0.05
        |H|        realizable   agnostic
          10          106       1199
         1e3          199       2120
         1e6          337       3501
        2^64          948       9611
```

Every bound holds, and every bound is loose, in an instructive way.

- **Part 1.** For $p = 0.1$ the simulated deviation probability is 0.0021, more than a hundred times below the bound,
  because a coin with $p = 0.1$ has variance $0.09$, not the worst case $0.25$ that Hoeffding assumes. Bernstein's
  inequality, which uses the variance, is sharper in such cases.
- **Part 2.** The theorem's 153 is safe: at $m = 153$ the failure rate is 0.0003, and already at $m = 60$ it is
  0.0489, below $\delta$. Why is the union bound so wasteful here? A hypothesis $h_k$ is consistent only if no sample
  point fell between $k/100$ and $0.37$, so the bad events are nested: if $h_{30}$ is consistent, so is $h_{31}$.
  Only the two bad thresholds nearest the target matter ($h_{31}$ and $h_{43}$), and the failure probability is about
  $2(0.94)^m$, which is 0.049 at $m = 60$. The union bound adds 101 nearly identical events as if they were separate.
  The next section turns exactly this observation into a theory.
- **Part 3.** The measured worst gap at $m = 100$ has a 95th percentile of 0.136, against a guarantee of 0.204; and
  both shrink by a factor of 2 each time $m$ grows by a factor of 4, the $1/\sqrt m$ rate. The excess risk of ERM is far
  smaller than $2\varepsilon$, because ERM is not adversarial: it picks the best-looking hypothesis, which is usually
  the best one.
- **Part 4.** Even $2^{64}$ hypotheses (every function a 64-bit number could index) need only 948 examples in the
  realizable case and 9611 in the agnostic case. Finite classes are cheap.

The trouble is that almost every class in this book is infinite: a line in the plane has real-valued coefficients,
so there are uncountably many. Yet in Part 2 we saw that what matters is not how many hypotheses exist but how many
*behave differently* on the data. That is the idea of the next section.

## 21.3 The VC dimension

*Level: advanced.*

Vladimir Vapnik and Alexey Chervonenkis, at the Institute of Control Sciences in Moscow, asked when the frequencies of
events converge to their probabilities *uniformly* over an infinite family of events. Their paper, "On the uniform
convergence of relative frequencies of events to their probabilities", appeared in Russian in 1968 as an announcement
and in full in *Theory of Probability and its Applications* in 1971. The number they defined now carries their
initials.

### Restrictions and shattering

Take a finite set of inputs $C = \{x_1, \dots, x_n\} \subseteq \mathcal X$. Each hypothesis labels these points with a
string of $n$ bits; call that string $h$ **restricted** to $C$. Different hypotheses may give the same string. The
set of distinct strings is

$$
\mathcal H_C = \big\{(h(x_1), \dots, h(x_n)) : h \in \mathcal H\big\} \subseteq \{0, 1\}^n .
$$

On the sample, only $|\mathcal H_C|$ hypotheses are really different, however many $\mathcal H$ contains. The class
**shatters** $C$ if $\mathcal H_C$ is all of $\{0, 1\}^n$: every one of the $2^n$ labellings of $C$ is achieved by
some hypothesis. The **growth function** is the largest number of labellings on any $n$ points,

$$
\tau_{\mathcal H}(n) = \max_{|C| = n} |\mathcal H_C| \le 2^n,
$$

and the **VC dimension** $\mathrm{VCdim}(\mathcal H)$ is the largest $n$ such that some set of $n$ points is
shattered, or $\infty$ if arbitrarily large sets are. To show that $\mathrm{VCdim} = d$ you must do two different
things: exhibit *one* set of $d$ points that is shattered, and prove that *no* set of $d + 1$ points is.

### Examples, done by hand

**Rays** $h_t(x) = \mathbf 1[x \ge t]$ on the real line. One point is shattered (put $t$ below it or above it). Two
points $x_1 < x_2$ are not: the labelling $(1, 0)$ would need $x_1 \ge t > x_2$. So $\mathrm{VCdim} = 1$. On $n$
sorted points a ray can only cut once, so $\tau(n) = n + 1$.

**Intervals** $h_{a,b}(x) = \mathbf 1[a \le x \le b]$. Two points are shattered (an interval can contain neither,
either, or both). Three points $x_1 < x_2 < x_3$ are not: the labelling $(1, 0, 1)$ would need an interval containing
$x_1$ and $x_3$ but not the point between them. $\mathrm{VCdim} = 2$. The positive points must form a contiguous
block of the sorted list, so $\tau(n) = \binom{n+1}{2} + 1$ (choose the block's two ends among $n + 1$ gaps, or
choose no block).

**Half-planes** $h_{w,b}(x) = \mathbf 1[w \cdot x + b \ge 0]$ in $\mathbb R^2$. Three points that are not on one line
are shattered: Figure 21.1 shows all eight labellings with a separating line. Four points are never shattered. If one
of the four lies inside the triangle of the other three, label it 0 and the others 1: a half-plane is convex, so it
cannot contain the triangle's corners without containing the triangle. Otherwise the four form a convex quadrilateral,
and the "diagonal" labelling (opposite corners 1, the other two 0) fails, because the two diagonals cross and the
crossing point would have to be in both the half-plane and its complement. (Points with three on one line are easier:
label the middle one differently from the two ends.) So $\mathrm{VCdim} = 3$.

<figure class="mars-fig" markdown="0">
<svg viewBox="0 0 700 250" role="img" aria-label="Top: three points in a triangle and all eight ways to label them, each split by a straight line. Bottom: four points at the corners of a square; the two diagonal XOR labelings cannot be split by any line.">
<text x="350" y="18" font-size="13" text-anchor="middle" fill="currentColor">three points: all 8 labelings are cut out by a line (shattered)</text>
<rect x="10" y="28" width="74" height="74" rx="4" fill="none" stroke="currentColor" stroke-width="1" stroke-opacity="0.5"/>
<circle cx="17.4" cy="90.9" r="6" fill="#9cc9ea" fill-opacity="0.35" stroke="currentColor" stroke-width="1"/>
<circle cx="76.6" cy="90.9" r="6" fill="#9cc9ea" fill-opacity="0.35" stroke="currentColor" stroke-width="1"/>
<circle cx="39.6" cy="39.1" r="6" fill="#9cc9ea" fill-opacity="0.35" stroke="currentColor" stroke-width="1"/>
<text x="47.0" y="118" font-size="12" text-anchor="middle" fill="currentColor">---</text>
<rect x="96" y="28" width="74" height="74" rx="4" fill="none" stroke="currentColor" stroke-width="1" stroke-opacity="0.5"/>
<line x1="96.0" y1="62.4" x2="170.0" y2="62.4" stroke="currentColor" stroke-width="1.4" stroke-dasharray="4 3"/>
<circle cx="103.4" cy="90.9" r="6" fill="#9cc9ea" fill-opacity="0.35" stroke="currentColor" stroke-width="1"/>
<circle cx="162.6" cy="90.9" r="6" fill="#9cc9ea" fill-opacity="0.35" stroke="currentColor" stroke-width="1"/>
<circle cx="125.6" cy="39.1" r="6" fill="#eea66f" stroke="currentColor" stroke-width="1"/>
<text x="133.0" y="118" font-size="12" text-anchor="middle" fill="currentColor">--+</text>
<rect x="182" y="28" width="74" height="74" rx="4" fill="none" stroke="currentColor" stroke-width="1" stroke-opacity="0.5"/>
<line x1="217.2" y1="102.0" x2="248.9" y2="28.0" stroke="currentColor" stroke-width="1.4" stroke-dasharray="4 3"/>
<circle cx="189.4" cy="90.9" r="6" fill="#9cc9ea" fill-opacity="0.35" stroke="currentColor" stroke-width="1"/>
<circle cx="248.6" cy="90.9" r="6" fill="#eea66f" stroke="currentColor" stroke-width="1"/>
<circle cx="211.6" cy="39.1" r="6" fill="#9cc9ea" fill-opacity="0.35" stroke="currentColor" stroke-width="1"/>
<text x="219.0" y="118" font-size="12" text-anchor="middle" fill="currentColor">-+-</text>
<rect x="268" y="28" width="74" height="74" rx="4" fill="none" stroke="currentColor" stroke-width="1" stroke-opacity="0.5"/>
<line x1="310.0" y1="102.0" x2="268.0" y2="43.2" stroke="currentColor" stroke-width="1.4" stroke-dasharray="4 3"/>
<circle cx="275.4" cy="90.9" r="6" fill="#9cc9ea" fill-opacity="0.35" stroke="currentColor" stroke-width="1"/>
<circle cx="334.6" cy="90.9" r="6" fill="#eea66f" stroke="currentColor" stroke-width="1"/>
<circle cx="297.6" cy="39.1" r="6" fill="#eea66f" stroke="currentColor" stroke-width="1"/>
<text x="305.0" y="118" font-size="12" text-anchor="middle" fill="currentColor">-++</text>
<rect x="354" y="28" width="74" height="74" rx="4" fill="none" stroke="currentColor" stroke-width="1" stroke-opacity="0.5"/>
<line x1="396.0" y1="102.0" x2="354.0" y2="43.2" stroke="currentColor" stroke-width="1.4" stroke-dasharray="4 3"/>
<circle cx="361.4" cy="90.9" r="6" fill="#eea66f" stroke="currentColor" stroke-width="1"/>
<circle cx="420.6" cy="90.9" r="6" fill="#9cc9ea" fill-opacity="0.35" stroke="currentColor" stroke-width="1"/>
<circle cx="383.6" cy="39.1" r="6" fill="#9cc9ea" fill-opacity="0.35" stroke="currentColor" stroke-width="1"/>
<text x="391.0" y="118" font-size="12" text-anchor="middle" fill="currentColor">+--</text>
<rect x="440" y="28" width="74" height="74" rx="4" fill="none" stroke="currentColor" stroke-width="1" stroke-opacity="0.5"/>
<line x1="475.2" y1="102.0" x2="506.9" y2="28.0" stroke="currentColor" stroke-width="1.4" stroke-dasharray="4 3"/>
<circle cx="447.4" cy="90.9" r="6" fill="#eea66f" stroke="currentColor" stroke-width="1"/>
<circle cx="506.6" cy="90.9" r="6" fill="#9cc9ea" fill-opacity="0.35" stroke="currentColor" stroke-width="1"/>
<circle cx="469.6" cy="39.1" r="6" fill="#eea66f" stroke="currentColor" stroke-width="1"/>
<text x="477.0" y="118" font-size="12" text-anchor="middle" fill="currentColor">+-+</text>
<rect x="526" y="28" width="74" height="74" rx="4" fill="none" stroke="currentColor" stroke-width="1" stroke-opacity="0.5"/>
<line x1="526.0" y1="62.4" x2="600.0" y2="62.4" stroke="currentColor" stroke-width="1.4" stroke-dasharray="4 3"/>
<circle cx="533.4" cy="90.9" r="6" fill="#eea66f" stroke="currentColor" stroke-width="1"/>
<circle cx="592.6" cy="90.9" r="6" fill="#eea66f" stroke="currentColor" stroke-width="1"/>
<circle cx="555.6" cy="39.1" r="6" fill="#9cc9ea" fill-opacity="0.35" stroke="currentColor" stroke-width="1"/>
<text x="563.0" y="118" font-size="12" text-anchor="middle" fill="currentColor">++-</text>
<rect x="612" y="28" width="74" height="74" rx="4" fill="none" stroke="currentColor" stroke-width="1" stroke-opacity="0.5"/>
<circle cx="619.4" cy="90.9" r="6" fill="#eea66f" stroke="currentColor" stroke-width="1"/>
<circle cx="678.6" cy="90.9" r="6" fill="#eea66f" stroke="currentColor" stroke-width="1"/>
<circle cx="641.6" cy="39.1" r="6" fill="#eea66f" stroke="currentColor" stroke-width="1"/>
<text x="649.0" y="118" font-size="12" text-anchor="middle" fill="currentColor">+++</text>
<text x="350" y="142" font-size="13" text-anchor="middle" fill="currentColor">four points in a square: these 2 of the 16 labelings defeat every line, so VC dimension = 3</text>
<rect x="230" y="150" width="74" height="74" rx="4" fill="none" stroke="currentColor" stroke-width="1" stroke-opacity="0.5"/>
<circle cx="244.8" cy="164.8" r="6" fill="#eea66f" stroke="currentColor" stroke-width="1"/>
<circle cx="289.2" cy="164.8" r="6" fill="#9cc9ea" fill-opacity="0.35" stroke="currentColor" stroke-width="1"/>
<circle cx="289.2" cy="209.2" r="6" fill="#eea66f" stroke="currentColor" stroke-width="1"/>
<circle cx="244.8" cy="209.2" r="6" fill="#9cc9ea" fill-opacity="0.35" stroke="currentColor" stroke-width="1"/>
<rect x="394" y="150" width="74" height="74" rx="4" fill="none" stroke="currentColor" stroke-width="1" stroke-opacity="0.5"/>
<circle cx="408.8" cy="164.8" r="6" fill="#9cc9ea" fill-opacity="0.35" stroke="currentColor" stroke-width="1"/>
<circle cx="453.2" cy="164.8" r="6" fill="#eea66f" stroke="currentColor" stroke-width="1"/>
<circle cx="453.2" cy="209.2" r="6" fill="#9cc9ea" fill-opacity="0.35" stroke="currentColor" stroke-width="1"/>
<circle cx="408.8" cy="209.2" r="6" fill="#eea66f" stroke="currentColor" stroke-width="1"/>
<circle cx="560" cy="170" r="6" fill="#eea66f" stroke="currentColor" stroke-width="1"/><text x="572" y="174" font-size="12" fill="currentColor">label +</text>
<circle cx="560" cy="194" r="6" fill="#9cc9ea" fill-opacity="0.35" stroke="currentColor" stroke-width="1"/><text x="572" y="198" font-size="12" fill="currentColor">label -</text>
<line x1="552" y1="218" x2="568" y2="218" stroke="currentColor" stroke-width="1.4" stroke-dasharray="4 3"/><text x="572" y="222" font-size="12" fill="currentColor">separating line</text>
</svg>
<figcaption>Figure 21.1. Shattering. Three points in general position can be given all 8 labellings by half-planes
(orange inside, blue outside; for "all +" and "all -" the line lies far away). For four points in a square, the two
XOR labellings below defeat every line, so the VC dimension of half-planes in the plane is 3.</figcaption>
</figure>

**Half-spaces in $\mathbb R^d$** have VC dimension $d + 1$, which matches the $d + 1$ parameters $(w, b)$. The lower
bound: the origin and the $d$ unit vectors $e_1, \dots, e_d$ are shattered. For labels $y_0$ (at the origin) and
$y_1, \dots, y_d$ (at $e_1, \dots, e_d$), each 0 or 1, take $b = y_0 - 1/2$ and $w_j = y_j - y_0$. Then
$w \cdot 0 + b = y_0 - 1/2$ and $w \cdot e_j + b = y_j - 1/2$, which are non-negative exactly where the label is 1. The upper bound uses **Radon's theorem**: any $d + 2$ points in
$\mathbb R^d$ can be split into two groups whose convex hulls (the smallest convex sets containing them) intersect.
Proof of Radon: the $d + 2$ vectors $(x_i, 1) \in \mathbb R^{d+1}$ are linearly dependent, so there are numbers
$\lambda_i$, not all zero, with $\sum \lambda_i x_i = 0$ and $\sum\lambda_i = 0$. Put the indices with
$\lambda_i > 0$ in group $P$ and the rest in $N$; then $s = \sum_P \lambda_i = \sum_N (-\lambda_i) > 0$, and the
point $\sum_P (\lambda_i/s)x_i = \sum_N (-\lambda_i/s)x_i$ is a convex combination of each group. Labelling $P$ as 1
and $N$ as 0 is impossible for a half-space, because that common point would have to be on both sides.

**Axis-aligned rectangles** in the plane have VC dimension 4. The four points of a diamond, $(0, \pm 1)$ and
$(\pm 1, 0)$, are shattered. For any five points, pick one with the smallest $x$, one with the largest $x$, one with
the smallest $y$, one with the largest $y$ (at most four points); the remaining point lies inside their bounding box,
so labelling those four 1 and it 0 cannot be done, because any rectangle containing the four contains their bounding
box.

**One parameter, infinite VC dimension.** The class $h_\omega(x) = \mathbf 1[\sin(\omega x) > 0]$ has a single real
parameter, yet it shatters the points $x_i = 10^{-i}$ for every $n$. For labels $l_i \in \{0, 1\}$ take

$$
\omega = \pi\Big(1 + \sum_{i=1}^{n} (1 - l_i)\, 10^{i}\Big).
$$

Then $\omega x_j = \pi 10^{-j} + \pi\sum_i (1 - l_i)10^{i - j}$. The terms with $i > j$ are multiples of $10\pi$, so
they do not change the sine. The term $i = j$ adds $\pi(1 - l_j)$. The terms with $i < j$ together with
$\pi 10^{-j}$ add a number $c$ with $0 < c < \pi(0.1 + 0.01 + \dots + 10^{-j}) < 0.12\pi$. So $\omega x_j$ equals
$c$ or $\pi + c$ modulo $2\pi$, and the sine is positive exactly when $l_j = 1$. Counting parameters is therefore
not a measure of capacity: the VC dimension counts behaviours, not knobs.

The program checks all of these by brute force. For half-planes it uses an exact enumeration: as a direction
$w$ turns, the order of the projections $w \cdot x_i$ changes only at the finitely many angles where two projections
tie, so trying one direction between each pair of neighbouring critical angles, and every cut of the sorted
projections, finds every labelling.

```python
--8<-- "books/machine-learning/ch21_vc.py"
```

```
1. can the class shatter these points?  (labelings realised / 2^n)
   rays, 1 point:        2/2
   rays, 2 points:       3/4
   intervals, 2 points:  4/4
   intervals, 3 points:  7/8   (1, 0, 1 is missing)
   half-planes, triangle:  8/8
   half-planes, square:    14/16  (the two XOR labelings are missing)
   rectangles, diamond:    16/16
   rectangles, 5 points:   at most 28/32 over 300 random sets

2. growth function tau(n) against Sauer's bound and 2^n
    n   intervals  Sauer d=2   half-planes  n^2-n+2  Sauer d=3     2^n
    1           2          2             2        2          2       2
    2           4          4             4        4          4       4
    3           7          7             8        8          8       8
    4          11         11            14       14         15      16
    5          16         16            22       22         26      32
    6          22         22            32       32         42      64
    7          29         29            44       44         64     128
    8          37         37            58       58         93     256
    9          46         46            74       74        130     512
   10          56         56            92       92        176    1024

3. sign(sin(w x)) shatters x_i = 10^-i for every n (one parameter!)
   n = 1: 2/2 labelings realised
   n = 2: 4/4 labelings realised
   n = 3: 8/8 labelings realised
   n = 4: 16/16 labelings realised
   n = 5: 32/32 labelings realised
   n = 6: 64/64 labelings realised
```

### Sauer's lemma

Look at the table in Part 2. Up to the VC dimension the growth function is $2^n$; after it, it bends to a
polynomial. That is not a coincidence.

**Lemma 21.4 (Sauer 1972; Shelah 1972; Vapnik and Chervonenkis 1971).** If $\mathrm{VCdim}(\mathcal H) = d$, then for
every $n$,

$$
\tau_{\mathcal H}(n) \le \sum_{i=0}^{d}\binom{n}{i}, \qquad\text{and for } n \ge d:\quad
\tau_{\mathcal H}(n) \le \Big(\frac{en}{d}\Big)^d .
$$

The first inequality is proved by induction on $n$: remove one point $x$; the labellings of the rest either extend
in one way or in both ways at $x$, and the "both ways" family has VC dimension at most $d - 1$ on the remaining
points; Pascal's rule $\binom{n}{i} = \binom{n-1}{i} + \binom{n-1}{i-1}$ then closes the induction. The full proof is
half a page in Shalev-Shwartz and Ben-David, Lemma 6.10. The second inequality follows from the first: for $n \ge d$,

$$
\sum_{i=0}^{d}\binom{n}{i} \le \Big(\frac nd\Big)^d \sum_{i=0}^{n}\binom{n}{i}\Big(\frac dn\Big)^i
= \Big(\frac nd\Big)^d\Big(1 + \frac dn\Big)^n \le \Big(\frac nd\Big)^d e^d,
$$

where the first step multiplies the term $i \le d$ by $(n/d)^{d-i} \ge 1$ and adds terms, and the last uses
$1 + t \le e^t$.

In the table, intervals ($d = 2$) meet Sauer's bound with equality at every $n$: the lemma is tight. Half-planes
($d = 3$) realise $n^2 - n + 2$ labellings on points in general position (Cover counted these in 1965), below the
bound $\binom n0 + \binom n1 + \binom n2 + \binom n3$, but both are polynomials in $n$, while $2^n$ is not.
At $n = 10$: 92 and 176 against 1024.

### The fundamental theorem

Sauer's lemma is the bridge from infinite to finite. The proof of uniform convergence for an infinite class goes in
three steps, each a classic trick.

1. **Ghost sample (symmetrisation).** Draw a second, imaginary sample $S'$ of the same size. If some $h$ has
   $L_S(h)$ far from $L_{\mathcal D}(h)$, then with probability at least one half it is also far from $L_{S'}(h)$,
   since $L_{S'}(h)$ concentrates near $L_{\mathcal D}(h)$. So it suffices to bound the chance that the two samples
   disagree, and that event depends only on the $2m$ points actually drawn.
2. **Finitely many behaviours.** On those $2m$ points the class has at most $\tau_{\mathcal H}(2m)$ distinct
   labellings. The supremum over an infinite class becomes a maximum over a finite set.
3. **Random swaps and Hoeffding.** Since the $2m$ points are i.i.d., swapping $x_i$ with $x'_i$ for random $i$
   does not change their distribution. For one labelling, the difference between the two halves after random swaps
   is a sum of independent signs, and Hoeffding bounds it. A union bound over $\tau_{\mathcal H}(2m)$ labellings
   finishes.

The result has the form $\Pr[\sup_h |L_S(h) - L_{\mathcal D}(h)| > \varepsilon] \le c_1\,\tau_{\mathcal H}(2m)\,
e^{-c_2 m\varepsilon^2}$ for absolute constants $c_1, c_2$ (the 1971 paper and later textbooks use different
constants). With Sauer's lemma the right side is a polynomial in $m$ times a decaying exponential, so it goes to zero
whenever $d$ is finite. If $d$ is infinite, a matching lower bound shows that learning fails: put the distribution
uniformly on $2m$ shattered points; the learner sees at most half of them, the labels of the rest can be anything, and
the no-free-lunch argument of [Chapter 1](01-What-Is-Machine-Learning.md) gives error near one quarter on some
target.

**Theorem 21.5 (the fundamental theorem of statistical learning).** For a class $\mathcal H$ of functions
$\mathcal X \to \{0, 1\}$ with the zero-one loss, the following are equivalent:

1. $\mathcal H$ has the uniform convergence property;
2. any ERM rule is a successful agnostic PAC learner for $\mathcal H$;
3. $\mathcal H$ is agnostic PAC learnable;
4. $\mathcal H$ is PAC learnable;
5. any ERM rule is a successful PAC learner for $\mathcal H$;
6. $\mathcal H$ has finite VC dimension.

Moreover, if $\mathrm{VCdim}(\mathcal H) = d < \infty$, there are absolute constants $C_1, C_2$ such that the sample
complexity of agnostic learning lies between $C_1 (d + \ln(1/\delta))/\varepsilon^2$ and
$C_2 (d + \ln(1/\delta))/\varepsilon^2$, and that of realizable learning between $C_1(d + \ln(1/\delta))/\varepsilon$ and
$C_2(d\ln(1/\varepsilon) + \ln(1/\delta))/\varepsilon$.

This is the form of Theorems 6.7 and 6.8 in Shalev-Shwartz and Ben-David (2014), where the full proofs are. The
$\ln(1/\varepsilon)$ gap in the realizable case was closed by Hanneke (2016), who gave a (non-ERM) learner that
matches the lower bound. The theorem is remarkable: one combinatorial number decides whether learning is possible at
all, and gives the sample size up to constant factors.

A usable explicit version (Mohri, Rostamizadeh and Talwalkar, *Foundations of Machine Learning*, chapter 3) is:
with probability at least $1 - \delta$, for every $h \in \mathcal H$,

$$
L_{\mathcal D}(h) \le L_S(h) + \sqrt{\frac{2d\ln(em/d)}{m}} + \sqrt{\frac{\ln(1/\delta)}{2m}} .
$$

We will prove it in the next section. For half-planes ($d = 3$), $\varepsilon = \delta = 0.05$, the right side
drops below $L_S(h) + 0.05$ only at $m = 33035$, much larger than what is needed in practice. The constants are
pessimistic; the *shape*, $\sqrt{d\log m/m}$, is right.

## 21.4 Rademacher complexity and margins

*Level: advanced.*

The VC dimension depends only on the class, not on the data distribution, and it ignores real-valued outputs. A
support vector machine with an RBF kernel works in an infinite-dimensional feature space, where linear separators
have infinite VC dimension, yet it generalises. We need a finer measure.

### Fitting noise

Here is an idea that is easy to say: a class is rich if it can fit random noise. Draw **Rademacher signs**
$\sigma_1, \dots, \sigma_m$, independent and equal to $+1$ or $-1$ with probability one half each (named after the
mathematician Hans Rademacher). Ask how well the class can correlate with them on the sample. For a class
$\mathcal F$ of real-valued functions and a sample $S = (z_1, \dots, z_m)$, the **empirical Rademacher complexity**
is

$$
\hat{\mathfrak R}_S(\mathcal F) = E_\sigma\Big[\sup_{f \in \mathcal F}\frac1m\sum_{i=1}^m \sigma_i f(z_i)\Big],
$$

and the **Rademacher complexity** $\mathfrak R_m(\mathcal F)$ is its average over samples of size $m$. If the class
contains a single function, the supremum is over one $f$ and the expectation is 0. If it contains every function
from the $m$ points to $\{-1, +1\}$, it can always match the signs and the value is 1. Real classes sit in between,
and the smaller the value, the less a good fit on the sample can be blamed on luck.

**Theorem 21.6 (Rademacher bound; Koltchinskii and Panchenko 2002, Bartlett and Mendelson 2002).** Let $\mathcal G$
be a class of functions with values in $[0, 1]$. With probability at least $1 - \delta$ over an i.i.d. sample of
size $m$, for every $g \in \mathcal G$,

$$
E[g(z)] \le \frac1m\sum_{i=1}^m g(z_i) + 2\mathfrak R_m(\mathcal G) + \sqrt{\frac{\ln(1/\delta)}{2m}} .
$$

*Proof sketch.* Let $\Phi(S) = \sup_g (E g - \hat E_S g)$. Changing one example changes $\Phi$ by at most $1/m$, so
**McDiarmid's inequality** (Hoeffding's inequality for functions of independent variables with bounded changes)
says $\Phi(S) \le E\Phi + \sqrt{\ln(1/\delta)/(2m)}$ with probability $1 - \delta$. For $E\Phi$, write $E g$ as the
average over a ghost sample $S'$, move the supremum outside, and note that $g(z'_i) - g(z_i)$ has the same
distribution as $\sigma_i(g(z'_i) - g(z_i))$, because swapping $z_i$ and $z'_i$ changes nothing. Splitting the two
halves gives $E\Phi \le 2\mathfrak R_m(\mathcal G)$. $\square$ (Full proof: Mohri et al., chapter 3.)

For classification with labels in $\{-1, +1\}$, the zero-one loss is $(1 - yh(x))/2$, and since $\sigma_i y_i$ has
the same distribution as $\sigma_i$, the Rademacher complexity of the loss class is half that of $\mathcal H$. The
theorem becomes $L_{\mathcal D}(h) \le L_S(h) + \mathfrak R_m(\mathcal H) + \sqrt{\ln(1/\delta)/(2m)}$.

### Massart's lemma: back to the VC bound

**Lemma 21.7 (Massart 2000).** If $A \subset \mathbb R^m$ is finite and every $a \in A$ has $\|a\|_2 \le r$, then
$E_\sigma\big[\max_{a \in A}\frac1m\sum_i \sigma_i a_i\big] \le r\sqrt{2\ln|A|}/m$.

*Proof.* For any $\lambda > 0$, by Jensen's inequality (the exponential is convex),

$$
\exp\Big(\lambda E\max_a \sum_i \sigma_i a_i\Big) \le E\max_a e^{\lambda\sum_i\sigma_i a_i}
\le \sum_{a \in A}\prod_i E e^{\lambda\sigma_i a_i} \le |A|\, e^{\lambda^2 r^2/2},
$$

using Hoeffding's lemma, $E e^{\lambda\sigma a} \le e^{\lambda^2 a^2/2}$, for each sign. Take logarithms, divide by
$\lambda$, and choose $\lambda = \sqrt{2\ln|A|}/r$. $\square$

Apply it to a class of $\pm1$ functions: on a sample, $A$ is the set of label vectors, $|A| \le \tau_{\mathcal H}(m)$,
and each vector has length $r = \sqrt m$. So $\hat{\mathfrak R}_S(\mathcal H) \le \sqrt{2\ln\tau_{\mathcal H}(m)/m}
\le \sqrt{2d\ln(em/d)/m}$ by Sauer. Put this into Theorem 21.6 and you have proved the explicit VC bound of 21.3.

### Linear classes: no dimension at all

Now the payoff. Let $\mathcal F = \{x \mapsto w \cdot x : \|w\|_2 \le B\}$ and suppose every input has
$\|x\|_2 \le R$. The supremum in the definition can be computed exactly. By the Cauchy-Schwarz inequality,

$$
\sup_{\|w\| \le B}\frac1m\sum_i\sigma_i\, w \cdot x_i = \sup_{\|w\| \le B}\frac1m\, w \cdot \Big(\sum_i\sigma_i x_i\Big)
= \frac Bm\Big\|\sum_i\sigma_i x_i\Big\|,
$$

and by Jensen ($E\|v\| \le \sqrt{E\|v\|^2}$) and independence of the signs ($E\sigma_i\sigma_j = 0$ for $i \ne j$),

$$
\hat{\mathfrak R}_S(\mathcal F) \le \frac Bm\sqrt{\sum_i\|x_i\|^2} \le \frac{BR}{\sqrt m} .
$$

The dimension of $x$ does not appear. The bound depends on the norm of the weights and the size of the inputs, so it
holds in a feature space of any dimension, including the infinite one of a kernel. Part 2 of the next program
measures the expectation by Monte Carlo and finds it within 3% of $BR/\sqrt m$.

### The margin bound

A classifier $\operatorname{sign}(w \cdot x)$ has **margin** $y\,(w \cdot x)$ on example $(x, y)$: positive when
the example is classified correctly, and large when it is classified correctly with room to spare. Fix a target
margin $\rho > 0$ and define the **ramp loss** $\Phi_\rho(u)$: 1 for $u \le 0$, $1 - u/\rho$ for $0 < u < \rho$, and
0 for $u \ge \rho$. It lies between the zero-one loss and the "margin loss" $\mathbf 1[u < \rho]$, and it is
$1/\rho$-**Lipschitz** (it changes by at most $|u - u'|/\rho$ when its argument changes from $u$ to $u'$).

The **contraction lemma** (Ledoux and Talagrand, 1991) says composing a class with an $L$-Lipschitz function
multiplies its Rademacher complexity by at most $L$. Put the pieces together: apply Theorem 21.6 to
$\Phi_\rho(y\,w\cdot x)$, contract, and use the linear bound.

**Theorem 21.8 (margin bound).** With probability at least $1 - \delta$, every $w$ with $\|w\| \le B$ satisfies

$$
\Pr_{\mathcal D}\big[y\, w\cdot x \le 0\big] \le \frac1m\#\{i : y_i\, w\cdot x_i < \rho\}
+ \frac{2BR}{\rho\sqrt m} + \sqrt{\frac{\ln(1/\delta)}{2m}} .
$$

(A version that holds for all $\rho$ at once costs only an extra term of order
$\sqrt{\ln\ln(1/\rho)/m}$; Mohri et al., chapter 5.) What controls generalisation here is the ratio $BR/\rho$, the size of the inputs measured in units of
the margin. This is the theoretical reason behind the support vector machine of
[Chapter 10](10-Support-Vector-Machines.md): maximising the margin with $\|w\|$ fixed is minimising the complexity
term, in any dimension. The same norm-based thinking reappears in 21.6.

```python
--8<-- "books/machine-learning/ch21_rademacher_srm.py"
```

```
1. thresholds on the line: Monte Carlo Rademacher vs Massart sqrt(2 ln(m+1) / m)
     m   measured   Massart
     10   0.4165    0.6925
     40   0.2264    0.4309
    160   0.1201    0.2520
    640   0.0613    0.1421

2. linear functions w.x with ||w|| <= B = 1 on points with ||x|| <= R = 1 in 10-D
   exact sup is (B/m) ||sum sigma_i x_i||; bound is B R / sqrt(m)
     m   measured   bound
     10   0.3059    0.3162
     40   0.1544    0.1581
    160   0.0764    0.0791
    640   0.0384    0.0395

3. SRM over H_k = unions of k intervals (VC dimension 2k); m = 300, 10% label noise
   penalty(k) = sqrt(2 d ln(e m / d) / m) + sqrt(ln(1 / (delta w_k)) / (2 m)), d = 2k, w_k = 2^-k
    k   train err   penalty   bound    test err
    1      0.3200    0.3615   0.6815     0.3845
    2      0.1933    0.4620   0.6554     0.2401
    3      0.0733    0.5352   0.6086     0.1230
    4      0.0667    0.5947   0.6613     0.1270
    5      0.0600    0.6455   0.7055     0.1346
    6      0.0567    0.6902   0.7468     0.1388
    7      0.0533    0.7303   0.7836     0.1403
    8      0.0500    0.7669   0.8169     0.1418
    9      0.0467    0.8005   0.8472     0.1428
   10      0.0433    0.8318   0.8751     0.1457
   SRM picks k = 3; plain ERM over all k reaches its lowest training error at k = 10
   with no limit on k: 23 intervals, train err 0.0000, test err 0.1726
```

Part 1 measures the Rademacher complexity of thresholds and compares it with Massart's bound for the
$m + 1$ labellings they can produce; the bound is about twice too big, but it shrinks at the same rate,
$\sqrt{\log m/m}$. Part 2 is the linear class. Part 3 is the subject of the next section.

## 21.5 The bias-complexity trade-off and structural risk minimisation

*Level: intermediate.*

Every bound so far has the shape "training error plus a complexity term". A bigger class can fit the data better,
lowering the first term, but raises the second. This is the learning-theory version of the bias-variance trade-off of
[Chapter 8](08-Overfitting-and-Regularization.md), and it can be written as an exact decomposition. Let $h_S$ be the
ERM output. Then

$$
L_{\mathcal D}(h_S) = \underbrace{\min_{h \in \mathcal H} L_{\mathcal D}(h)}_{\varepsilon_{\text{app}}}
+ \underbrace{\Big(L_{\mathcal D}(h_S) - \min_{h \in \mathcal H}L_{\mathcal D}(h)\Big)}_{\varepsilon_{\text{est}}} .
$$

The **approximation error** $\varepsilon_{\text{app}}$ is how good the best member of the class is; it depends only
on the class and falls as the class grows. It includes the **Bayes error**, the error of the best possible rule,
which no class can beat because the labels themselves are noisy. The **estimation error** $\varepsilon_{\text{est}}$
is what we lose by choosing from a finite sample; Theorems 21.3 and 21.5 bound it by about
$\sqrt{d/m}$, which rises with the class. Choosing a class is choosing a point on this see-saw before seeing the data.

### Structural risk minimisation

Vapnik and Chervonenkis (1974) proposed a way to let the data choose. Take a nested sequence of classes
$\mathcal H_1 \subset \mathcal H_2 \subset \dots$ with VC dimensions $d_1 \le d_2 \le \dots$, and give class $k$ a
weight $w_k > 0$ with $\sum_k w_k \le 1$ (for instance $w_k = 2^{-k}$). Write $\varepsilon_k(m, \delta)$ for the
complexity term of the uniform bound for class $k$ at confidence $\delta$.

**Theorem 21.9 (SRM).** With probability at least $1 - \delta$, simultaneously for every $k$ and every
$h \in \mathcal H_k$, $L_{\mathcal D}(h) \le L_S(h) + \varepsilon_k(m, w_k\delta)$.

*Proof.* For each $k$ the bound fails with probability at most $w_k\delta$. By the union bound, some bound fails with
probability at most $\sum_k w_k\delta \le \delta$. $\square$

The **SRM rule** returns the hypothesis that minimises the right-hand side over all $k$ and all $h \in \mathcal H_k$:
in practice, run ERM inside each class and pick the class whose (training error plus penalty) is smallest. Because
the guarantee holds for all classes at once, the chosen hypothesis comes with a valid bound, and one can show that it
is nearly as good as if an oracle had told us the best class in advance, paying only the extra $\ln(1/w_k)$ inside
the penalty.

The program does this for unions of $k$ intervals on $[0, 1]$, a class with VC dimension $2k$ (it can shatter $2k$
points, two per interval, but not $2k + 1$ by the argument for one interval). The true labelling is a union of three
intervals, and 10% of labels are flipped, so the best possible error is 0.1. ERM for each $k$ is exact, by dynamic
programming over the sorted points: the state is "how many intervals have been opened, and are we inside one".

<figure class="mars-fig" markdown="0">
<svg viewBox="0 0 660 290" role="img" aria-label="Structural risk minimisation over unions of k intervals. Training error falls steadily with k. The SRM bound, training error plus penalty, is lowest at k = 3. Test error is also lowest at k = 3, at 0.123.">
<line x1="70" y1="240" x2="520" y2="240" stroke="currentColor"/><line x1="70" y1="20" x2="70" y2="240" stroke="currentColor"/>
<line x1="70.0" y1="240" x2="70.0" y2="245" stroke="currentColor"/><text x="70.0" y="259" font-size="12" text-anchor="middle" fill="currentColor">1</text>
<line x1="120.0" y1="240" x2="120.0" y2="245" stroke="currentColor"/><text x="120.0" y="259" font-size="12" text-anchor="middle" fill="currentColor">2</text>
<line x1="170.0" y1="240" x2="170.0" y2="245" stroke="currentColor"/><text x="170.0" y="259" font-size="12" text-anchor="middle" fill="currentColor">3</text>
<line x1="220.0" y1="240" x2="220.0" y2="245" stroke="currentColor"/><text x="220.0" y="259" font-size="12" text-anchor="middle" fill="currentColor">4</text>
<line x1="270.0" y1="240" x2="270.0" y2="245" stroke="currentColor"/><text x="270.0" y="259" font-size="12" text-anchor="middle" fill="currentColor">5</text>
<line x1="320.0" y1="240" x2="320.0" y2="245" stroke="currentColor"/><text x="320.0" y="259" font-size="12" text-anchor="middle" fill="currentColor">6</text>
<line x1="370.0" y1="240" x2="370.0" y2="245" stroke="currentColor"/><text x="370.0" y="259" font-size="12" text-anchor="middle" fill="currentColor">7</text>
<line x1="420.0" y1="240" x2="420.0" y2="245" stroke="currentColor"/><text x="420.0" y="259" font-size="12" text-anchor="middle" fill="currentColor">8</text>
<line x1="470.0" y1="240" x2="470.0" y2="245" stroke="currentColor"/><text x="470.0" y="259" font-size="12" text-anchor="middle" fill="currentColor">9</text>
<line x1="520.0" y1="240" x2="520.0" y2="245" stroke="currentColor"/><text x="520.0" y="259" font-size="12" text-anchor="middle" fill="currentColor">10</text>
<line x1="65" y1="240.0" x2="70" y2="240.0" stroke="currentColor"/><text x="61" y="244.0" font-size="12" text-anchor="end" fill="currentColor">0.0</text>
<line x1="65" y1="191.1" x2="70" y2="191.1" stroke="currentColor"/><text x="61" y="195.1" font-size="12" text-anchor="end" fill="currentColor">0.2</text>
<line x1="65" y1="142.2" x2="70" y2="142.2" stroke="currentColor"/><text x="61" y="146.2" font-size="12" text-anchor="end" fill="currentColor">0.4</text>
<line x1="65" y1="93.3" x2="70" y2="93.3" stroke="currentColor"/><text x="61" y="97.3" font-size="12" text-anchor="end" fill="currentColor">0.6</text>
<line x1="65" y1="44.4" x2="70" y2="44.4" stroke="currentColor"/><text x="61" y="48.4" font-size="12" text-anchor="end" fill="currentColor">0.8</text>
<text x="295.0" y="280" font-size="13" text-anchor="middle" fill="currentColor">k, the number of intervals allowed (VC dimension 2k)</text>
<text x="20" y="130.0" font-size="13" text-anchor="middle" fill="currentColor" transform="rotate(-90 20 130.0)">error</text>
<line x1="170.0" y1="20" x2="170.0" y2="240" stroke="currentColor" stroke-dasharray="4 3" stroke-opacity="0.6"/>
<text x="176.0" y="30" font-size="12" fill="currentColor">SRM choice k = 3</text>
<polyline points="70.0,73.4 120.0,79.8 170.0,91.2 220.0,78.3 270.0,67.5 320.0,57.4 370.0,48.5 420.0,40.3 470.0,32.9 520.0,26.1" fill="none" stroke="#eea66f" stroke-width="2.2"/>
<circle cx="70.0" cy="73.4" r="3.2" fill="#eea66f" stroke="currentColor" stroke-width="0.8"/>
<circle cx="120.0" cy="79.8" r="3.2" fill="#eea66f" stroke="currentColor" stroke-width="0.8"/>
<circle cx="170.0" cy="91.2" r="3.2" fill="#eea66f" stroke="currentColor" stroke-width="0.8"/>
<circle cx="220.0" cy="78.3" r="3.2" fill="#eea66f" stroke="currentColor" stroke-width="0.8"/>
<circle cx="270.0" cy="67.5" r="3.2" fill="#eea66f" stroke="currentColor" stroke-width="0.8"/>
<circle cx="320.0" cy="57.4" r="3.2" fill="#eea66f" stroke="currentColor" stroke-width="0.8"/>
<circle cx="370.0" cy="48.5" r="3.2" fill="#eea66f" stroke="currentColor" stroke-width="0.8"/>
<circle cx="420.0" cy="40.3" r="3.2" fill="#eea66f" stroke="currentColor" stroke-width="0.8"/>
<circle cx="470.0" cy="32.9" r="3.2" fill="#eea66f" stroke="currentColor" stroke-width="0.8"/>
<circle cx="520.0" cy="26.1" r="3.2" fill="#eea66f" stroke="currentColor" stroke-width="0.8"/>
<line x1="540" y1="40" x2="560" y2="40" stroke="#eea66f" stroke-width="2.2"/><text x="566" y="44" font-size="12" fill="currentColor">SRM bound</text>
<polyline points="70.0,146.0 120.0,181.3 170.0,209.9 220.0,209.0 270.0,207.1 320.0,206.1 370.0,205.7 420.0,205.3 470.0,205.1 520.0,204.4" fill="none" stroke="#9cc9ea" stroke-width="2.2"/>
<circle cx="70.0" cy="146.0" r="3.2" fill="#9cc9ea" stroke="currentColor" stroke-width="0.8"/>
<circle cx="120.0" cy="181.3" r="3.2" fill="#9cc9ea" stroke="currentColor" stroke-width="0.8"/>
<circle cx="170.0" cy="209.9" r="3.2" fill="#9cc9ea" stroke="currentColor" stroke-width="0.8"/>
<circle cx="220.0" cy="209.0" r="3.2" fill="#9cc9ea" stroke="currentColor" stroke-width="0.8"/>
<circle cx="270.0" cy="207.1" r="3.2" fill="#9cc9ea" stroke="currentColor" stroke-width="0.8"/>
<circle cx="320.0" cy="206.1" r="3.2" fill="#9cc9ea" stroke="currentColor" stroke-width="0.8"/>
<circle cx="370.0" cy="205.7" r="3.2" fill="#9cc9ea" stroke="currentColor" stroke-width="0.8"/>
<circle cx="420.0" cy="205.3" r="3.2" fill="#9cc9ea" stroke="currentColor" stroke-width="0.8"/>
<circle cx="470.0" cy="205.1" r="3.2" fill="#9cc9ea" stroke="currentColor" stroke-width="0.8"/>
<circle cx="520.0" cy="204.4" r="3.2" fill="#9cc9ea" stroke="currentColor" stroke-width="0.8"/>
<line x1="540" y1="62" x2="560" y2="62" stroke="#9cc9ea" stroke-width="2.2"/><text x="566" y="66" font-size="12" fill="currentColor">test error</text>
<polyline points="70.0,161.8 120.0,192.7 170.0,222.1 220.0,223.7 270.0,225.3 320.0,226.1 370.0,227.0 420.0,227.8 470.0,228.6 520.0,229.4" fill="none" stroke="#7ccf9a" stroke-width="2.2"/>
<circle cx="70.0" cy="161.8" r="3.2" fill="#7ccf9a" stroke="currentColor" stroke-width="0.8"/>
<circle cx="120.0" cy="192.7" r="3.2" fill="#7ccf9a" stroke="currentColor" stroke-width="0.8"/>
<circle cx="170.0" cy="222.1" r="3.2" fill="#7ccf9a" stroke="currentColor" stroke-width="0.8"/>
<circle cx="220.0" cy="223.7" r="3.2" fill="#7ccf9a" stroke="currentColor" stroke-width="0.8"/>
<circle cx="270.0" cy="225.3" r="3.2" fill="#7ccf9a" stroke="currentColor" stroke-width="0.8"/>
<circle cx="320.0" cy="226.1" r="3.2" fill="#7ccf9a" stroke="currentColor" stroke-width="0.8"/>
<circle cx="370.0" cy="227.0" r="3.2" fill="#7ccf9a" stroke="currentColor" stroke-width="0.8"/>
<circle cx="420.0" cy="227.8" r="3.2" fill="#7ccf9a" stroke="currentColor" stroke-width="0.8"/>
<circle cx="470.0" cy="228.6" r="3.2" fill="#7ccf9a" stroke="currentColor" stroke-width="0.8"/>
<circle cx="520.0" cy="229.4" r="3.2" fill="#7ccf9a" stroke="currentColor" stroke-width="0.8"/>
<line x1="540" y1="84" x2="560" y2="84" stroke="#7ccf9a" stroke-width="2.2"/><text x="566" y="88" font-size="12" fill="currentColor">training error</text>
</svg>
<figcaption>Figure 21.2. Structural risk minimisation on unions of k intervals (300 points, 10% label noise).
Training error keeps falling as k grows; the SRM bound, training error plus a penalty that grows with the VC
dimension, is smallest at k = 3, which is also where the test error is smallest (0.123, close to the noise floor of
0.1).</figcaption>
</figure>

Three things in the output deserve comment. First, SRM picks $k = 3$, the true structure, and its test error 0.123 is
the best in the table. Second, the bound itself, 0.609, is far above the true error: the bound is a valid guarantee
but a poor *estimate*. What makes SRM work is that the penalty grows at the right rate, not that its constant is
right. Third, without any limit, ERM uses 23 intervals, reaches zero training error and has test error 0.173: that is
the memoriser of 21.1 in miniature.

In practice nobody computes VC penalties. One holds out a validation set or cross-validates
([Chapter 7](07-Evaluating-Models.md)), which is SRM with an honest, data-driven penalty. Regularisation does the
same thing smoothly: ridge regression with penalty $\lambda\|w\|^2$ is, by Lagrange duality, ERM over the norm ball
$\|w\| \le B$ for some $B$, and the margin bound of 21.4 says the complexity of that ball grows with $B$. Choosing
$\lambda$ chooses $B$, which chooses a class in a nested family. The **minimum description length** principle
(Rissanen, 1978) is a third form of the same idea: prefer the hypothesis that, together with the data's exceptions,
has the shortest description, which is the Occam bound of 21.2 in disguise.

## 21.6 What theory does not explain

*Level: expert.*

The theory so far is mathematics; the theorems are true. The question is whether they explain the models people
actually use. For deep networks, the honest answer is: not yet, and several experiments made the gap impossible to
ignore. This section shows four of them in small form and states what is known.

### Deep networks fit random labels

In 2017 Zhang, Bengio, Hardt, Recht and Vinyals published "Understanding deep learning requires rethinking
generalization" (ICLR 2017). They trained standard convolutional networks on the CIFAR-10 image dataset, but with the
labels replaced by random ones. The networks reached zero training error, and training took only a small factor
longer than on the real labels. The same networks, on real labels, generalise well.

Think about what this does to the bounds of 21.3 and 21.4. Any bound of the form "training error + complexity of the
class" must be at least the true error, for every labelling of the data. On random labels the true error is 90% (ten
classes) while the training error is 0, so the complexity term must be at least 0.9 on that sample size. The same
complexity term then appears, unchanged, in the bound for the real labels, where it is useless. In other words, the
Rademacher complexity of the class *as a whole* is near its maximum, and every bound that depends only on the class
is vacuous. Whatever makes real-label training generalise must depend on the data and on the training algorithm,
not only on the set of functions the network could represent.

Part 1 of the program below repeats the experiment with 2000 random ReLU features (a two-layer network whose first
layer is frozen at random) and the minimum-norm fit. It interpolates both the true labels and random labels; test
accuracy is 0.831 in one case and 0.432, about chance, in the other. Note the last column: the random-label fit needs
a weight vector 1.6 times longer. Norm-based bounds such as Theorem 21.8 can tell the two apart; counting-based ones
cannot. This is one reason research turned to norm-based, margin-based and algorithm-dependent bounds, such as those
of Bartlett, Foster and Telgarsky (2017).

### Double descent

Classical theory draws a U: test error falls as the model grows, then rises as it starts to overfit. Belkin, Hsu, Ma
and Mandal ("Reconciling modern machine-learning practice and the classical bias-variance trade-off", PNAS 2019)
showed that if you keep going, past the point where the model can fit the training data exactly, the error can fall
again. They called the shape **double descent**, and found it in random-feature models, neural networks and
decision-tree ensembles. Nakkiran and co-authors ("Deep double descent", ICLR 2020) found it in modern deep networks,
as a function of width, of training time, and of sample size.

Part 2 of the program shows it with 40 training points and $p$ random Fourier features $\cos(w \cdot x + b)$, fitted by
minimum-norm least squares. Below $p = 40$ this is ordinary least squares; above it there are infinitely many exact
fits and we take the one with the smallest norm, $a = F^+ y$ (the pseudo-inverse, Chapter 4).

<figure class="mars-fig" markdown="0">
<svg viewBox="0 0 660 300" role="img" aria-label="Test error against number of random features on log scales. Error falls, then rises to a sharp peak of about 13 at 40 features, where the features equal the 40 training points, then falls again below its first minimum, to about 0.32 at 1000 features.">
<line x1="70" y1="240" x2="620" y2="240" stroke="currentColor"/><line x1="70" y1="20" x2="70" y2="240" stroke="currentColor"/>
<line x1="87.8" y1="240" x2="87.8" y2="245" stroke="currentColor"/><text x="87.8" y="259" font-size="12" text-anchor="middle" fill="currentColor">5</text>
<line x1="143.0" y1="240" x2="143.0" y2="245" stroke="currentColor"/><text x="143.0" y="259" font-size="12" text-anchor="middle" fill="currentColor">10</text>
<line x1="198.1" y1="240" x2="198.1" y2="245" stroke="currentColor"/><text x="198.1" y="259" font-size="12" text-anchor="middle" fill="currentColor">20</text>
<line x1="271.1" y1="240" x2="271.1" y2="245" stroke="currentColor"/><text x="271.1" y="259" font-size="12" text-anchor="middle" fill="currentColor">50</text>
<line x1="326.3" y1="240" x2="326.3" y2="245" stroke="currentColor"/><text x="326.3" y="259" font-size="12" text-anchor="middle" fill="currentColor">100</text>
<line x1="381.5" y1="240" x2="381.5" y2="245" stroke="currentColor"/><text x="381.5" y="259" font-size="12" text-anchor="middle" fill="currentColor">200</text>
<line x1="454.4" y1="240" x2="454.4" y2="245" stroke="currentColor"/><text x="454.4" y="259" font-size="12" text-anchor="middle" fill="currentColor">500</text>
<line x1="509.6" y1="240" x2="509.6" y2="245" stroke="currentColor"/><text x="509.6" y="259" font-size="12" text-anchor="middle" fill="currentColor">1000</text>
<line x1="564.8" y1="240" x2="564.8" y2="245" stroke="currentColor"/><text x="564.8" y="259" font-size="12" text-anchor="middle" fill="currentColor">2000</text>
<line x1="65" y1="240.0" x2="70" y2="240.0" stroke="currentColor"/><text x="61" y="244.0" font-size="12" text-anchor="end" fill="currentColor">0.2</text>
<line x1="65" y1="196.2" x2="70" y2="196.2" stroke="currentColor"/><text x="61" y="200.2" font-size="12" text-anchor="end" fill="currentColor">0.5</text>
<line x1="65" y1="163.1" x2="70" y2="163.1" stroke="currentColor"/><text x="61" y="167.1" font-size="12" text-anchor="end" fill="currentColor">1</text>
<line x1="65" y1="130.0" x2="70" y2="130.0" stroke="currentColor"/><text x="61" y="134.0" font-size="12" text-anchor="end" fill="currentColor">2</text>
<line x1="65" y1="86.2" x2="70" y2="86.2" stroke="currentColor"/><text x="61" y="90.2" font-size="12" text-anchor="end" fill="currentColor">5</text>
<line x1="65" y1="53.1" x2="70" y2="53.1" stroke="currentColor"/><text x="61" y="57.1" font-size="12" text-anchor="end" fill="currentColor">10</text>
<line x1="65" y1="20.0" x2="70" y2="20.0" stroke="currentColor"/><text x="61" y="24.0" font-size="12" text-anchor="end" fill="currentColor">20</text>
<text x="345.0" y="280" font-size="13" text-anchor="middle" fill="currentColor">number of features p (log scale); 40 training points</text>
<text x="20" y="130.0" font-size="13" text-anchor="middle" fill="currentColor" transform="rotate(-90 20 130.0)">test MSE (log)</text>
<line x1="253.3" y1="20" x2="253.3" y2="240" stroke="currentColor" stroke-dasharray="4 3" stroke-opacity="0.6"/>
<text x="259.3" y="32" font-size="12" fill="currentColor">p = n: interpolation threshold</text>
<rect x="71" y="20" width="182.3" height="220" fill="#9cc9ea" fill-opacity="0.12"/>
<text x="78" y="236" font-size="12" fill="currentColor">classical regime</text>
<text x="614" y="236" font-size="12" text-anchor="end" fill="currentColor">over-parameterised: train MSE = 0</text>
<polyline points="87.8,184.7 143.0,184.0 198.1,163.6 230.4,133.9 244.9,127.7 253.3,40.9 260.9,103.1 271.1,138.6 308.5,180.7 381.5,206.2 509.6,217.7 597.1,217.3" fill="none" stroke="#eea66f" stroke-width="2.2"/>
<circle cx="87.8" cy="184.7" r="3.5" fill="#eea66f" stroke="currentColor" stroke-width="0.8"/>
<circle cx="143.0" cy="184.0" r="3.5" fill="#eea66f" stroke="currentColor" stroke-width="0.8"/>
<circle cx="198.1" cy="163.6" r="3.5" fill="#eea66f" stroke="currentColor" stroke-width="0.8"/>
<circle cx="230.4" cy="133.9" r="3.5" fill="#eea66f" stroke="currentColor" stroke-width="0.8"/>
<circle cx="244.9" cy="127.7" r="3.5" fill="#eea66f" stroke="currentColor" stroke-width="0.8"/>
<circle cx="253.3" cy="40.9" r="3.5" fill="#eea66f" stroke="currentColor" stroke-width="0.8"/>
<circle cx="260.9" cy="103.1" r="3.5" fill="#eea66f" stroke="currentColor" stroke-width="0.8"/>
<circle cx="271.1" cy="138.6" r="3.5" fill="#eea66f" stroke="currentColor" stroke-width="0.8"/>
<circle cx="308.5" cy="180.7" r="3.5" fill="#eea66f" stroke="currentColor" stroke-width="0.8"/>
<circle cx="381.5" cy="206.2" r="3.5" fill="#eea66f" stroke="currentColor" stroke-width="0.8"/>
<circle cx="509.6" cy="217.7" r="3.5" fill="#eea66f" stroke="currentColor" stroke-width="0.8"/>
<circle cx="597.1" cy="217.3" r="3.5" fill="#eea66f" stroke="currentColor" stroke-width="0.8"/>
<line x1="70" y1="184.7" x2="620" y2="184.7" stroke="#7ccf9a" stroke-width="1.5" stroke-dasharray="6 4"/>
<text x="614" y="178.7" font-size="12" text-anchor="end" fill="currentColor">best classical fit (p = 5): 0.64</text>
</svg>
<figcaption>Figure 21.3. Double descent, measured by ch21_modern.py: median test error of minimum-norm least squares
on 40 points as the number of random Fourier features grows. The error peaks at the interpolation threshold p = n
and then falls again, ending below the best classical fit.</figcaption>
</figure>

**Why the peak?** At $p = n$ the feature matrix $F$ is square, and a random square matrix almost always has some very
small singular values. The fit $a = F^{-1}y$ divides the noise in $y$ by those small singular values, so the weights
explode and so does the test error (12.9 here, 40 times the best). Add more features, and the smallest singular value
of the wide matrix $F$ grows away from zero; among the many exact fits, the minimum-norm one spreads the weight over
many features, each of which carries a little of the signal and averages away the noise. For linear models this is
now understood precisely: Hastie, Montanari, Rosset and Tibshirani ("Surprises in high-dimensional ridgeless least
squares interpolation", Annals of Statistics 2022) derived the exact asymptotic curve, and Bartlett, Long, Lugosi and
Tsigler ("Benign overfitting in linear regression", PNAS 2020) characterised when interpolating noisy data is
harmless: the covariance must have many small directions that can absorb the noise. Whether the same mechanism
explains deep networks is open.

### The implicit bias of gradient descent

When a model has more parameters than examples, there are many weight settings with zero training error. Which one
does training find? The training loss does not say; the *algorithm* does. This is called **implicit regularisation**.

**Theorem 21.10.** Let $A$ be an $n \times p$ matrix with $n < p$ and full row rank, and run gradient descent on
$\frac12\|Aw - b\|^2$ from $w_0 = 0$ with a step size $\eta < 2/\|A\|^2$. Then $w_t$ converges to the minimum-norm
solution $w^\ast = A^+ b$.

*Proof.* Every gradient $A^\top(Aw - b)$ lies in the row space of $A$, the span of its rows. Starting from 0, every
iterate is a sum of such vectors, so it stays in the row space. The iteration converges to some exact solution
(on the row space, $A^\top A$ is positive definite, and the step size makes the map a contraction there). The set of
exact solutions is $w^\ast + \ker A$, and the row space is the orthogonal complement of $\ker A$, so the only exact
solution in the row space is the one with no component in $\ker A$, the minimum-norm one. From a general start $w_0$,
the component of $w_0$ in $\ker A$ is never touched, so the limit is $w^\ast + (I - P)w_0$, where $P = A^+A$ is the
projection onto the row space. $\square$

Part 3 confirms both statements to about $10^{-14}$. So "train with gradient descent from small initial weights" is,
for least squares, the same as "find the smallest-norm interpolant", and the norm-based bounds then apply to the
function training actually finds. For logistic regression on separable data, Soudry, Hoffer, Nacson, Gunasekar and
Srebro ("The implicit bias of gradient descent on separable data", JMLR 2018) proved that the *direction* of the
weights converges to the maximum-margin separator, the hard-margin SVM. For deep networks the implicit bias of
stochastic gradient descent is an active research area without a complete answer.

### The neural tangent kernel

Jacot, Gabriel and Hongler ("Neural tangent kernel: convergence and generalization in neural networks", NeurIPS 2018)
found a regime where deep networks *are* understood. Write the network's output as $f(x; \theta)$. A small step of
gradient descent changes $\theta$ by $\Delta\theta$, and the output changes by
$\nabla_\theta f(x;\theta)\cdot\Delta\theta$. Training dynamics in function space are governed by the **neural
tangent kernel**

$$
K(x, x') = \nabla_\theta f(x; \theta)\cdot\nabla_\theta f(x'; \theta).
$$

They proved that as the width of every layer goes to infinity, with the right scaling of the initial weights
($1/\sqrt{\text{width}}$ in front of each layer), $K$ at initialisation converges to a fixed kernel and *stays
constant during training*. The network then behaves exactly like kernel regression with the kernel $K$
([Chapter 9](09-Nearest-Neighbours-and-Kernels.md)), training is a convex problem in function space, and gradient
descent provably reaches zero training loss. Part 4 shows the effect: as the width goes from 10 to 10000, the relative
movement of the first-layer weights falls from 1.16 to 0.032 (roughly like $1/\sqrt{\text{width}}$) and the
change of the kernel falls from 2.4 to 0.0036, even faster. This is called **lazy training**: each weight barely moves, yet the function fits.

```python
--8<-- "books/machine-learning/ch21_modern.py"
```

```
1. 2000 random ReLU features, 200 training points; minimum-norm interpolation
   labels         train acc   test acc   ||a||
   true               1.000      0.831     30.2
   random             1.000      0.432     48.6

2. double descent: 40 training points, p random Fourier features, minimum-norm least squares
     p    p/n    train MSE   test MSE (median over 20 runs)
      5   0.12      0.5052      0.6364
     10   0.25      0.3501      0.6462
     20   0.50      0.1874      0.9895
     30   0.75      0.0770      1.8448
     36   0.90      0.0143      2.0971
     40   1.00      0.0000     12.9254
     44   1.10      0.0000      3.5144
     50   1.25      0.0000      1.6710
     80   2.00      0.0000      0.6918
    200   5.00      0.0000      0.4056
   1000  25.00      0.0000      0.3191
   3000  75.00      0.0000      0.3219

3. gradient descent on least squares with 20 equations, 100 unknowns (infinitely many exact fits)
   start at 0    residual 3.1e-17  ||w|| = 0.4812  ||w - w_min|| = 0.0000  ||w - predicted|| = 8.1e-16
   random start  residual 3.5e-15  ||w|| = 8.5414  ||w - w_min|| = 8.5278  ||w - predicted|| = 1.1e-14
   minimum-norm solution has ||w_min|| = 0.4812

4. two-layer ReLU net in NTK scaling, 2000 steps of gradient descent
     width   final train MSE   ||W - W0|| / ||W0||   kernel change ||K - K0|| / ||K0||
       10           0.01467                1.1620                2.4030
      100           0.00282                0.2667                0.2107
     1000           0.00071                0.1013                0.0204
    10000           0.00039                0.0318                0.0036
```

The NTK is a real theorem and a real insight, but it is not the whole story, and saying so is part of being honest.
In the lazy regime the features never change, so a network is no better than a fixed kernel, while real networks of
practical width learn features and usually beat their own NTK. Chizat, Oyallon and Bach ("On lazy training in
differentiable programming", NeurIPS 2019) showed that laziness comes from the scaling, not from depth or width as
such, and that other scalings (the "mean-field" regime) let features move. Which regime real training is in, and how
feature learning helps generalisation, is open.

### Where this leaves us

What is solidly known: uniform convergence, the VC and Rademacher bounds, margin bounds, SRM, and their tight
constants for simple classes. What is understood in special cases: interpolation in linear and kernel models, the
implicit bias of gradient descent for linear models, the infinite-width limit. What is open: a bound that is
non-vacuous, explains why one architecture generalises better than another, and depends on the data and the
algorithm in the right way. **PAC-Bayes** bounds (McAllester, 1999) are one promising tool; they bound the error of a
*distribution* over weights in terms of its distance from a prior, and Dziugaite and Roy (2017) used them to get the
first non-vacuous bounds for a stochastic neural network trained on MNIST. Chapter 23 returns to generalisation as an
open problem.

## Check yourself

??? question "1. A finite class has $2^{20}$ hypotheses and the target is in the class. How many examples does Theorem 21.1 need for $\varepsilon = 0.01$, $\delta = 0.01$?"

    $m \ge (\ln 2^{20} + \ln 100)/0.01 = (13.863 + 4.605)/0.01 = 1846.8$, so 1847 examples. Doubling the number of
    bits in a hypothesis description doubles the first term, not the whole sample size.

??? question "2. Same class, but now with label noise (agnostic case). How many examples guarantee that every training error is within $\varepsilon = 0.01$ of the true error with $\delta = 0.05$, for a class of 1000 hypotheses?"

    $m \ge \ln(2|\mathcal H|/\delta)/(2\varepsilon^2) = \ln(40000)/0.0002 = 10.597/0.0002 = 52983.2$, so 52984 examples.
    Compare the realizable case: $(\ln 1000 + \ln 20)/0.01 = 990.3$. The square on $\varepsilon$ costs a factor of
    about 50.

??? question "3. What is the VC dimension of the class of two-sided rays, $\{x \mapsto \mathbf 1[x \ge t]\} \cup \{x \mapsto \mathbf 1[x \le t]\}$ on the real line? What is its growth function?"

    Two points $x_1 < x_2$ are shattered: $(0, 0)$ and $(1, 1)$ by rays far away, $(0, 1)$ by $\mathbf 1[x \ge t]$
    with $t$ between them, $(1, 0)$ by $\mathbf 1[x \le t]$. Three points $x_1 < x_2 < x_3$ are not: $(1, 0, 1)$
    needs two cuts. So VCdim = 2. On $n$ sorted points each kind of ray gives $n + 1$ labellings; the all-zero and
    all-one labellings are counted twice, so $\tau(n) = 2(n + 1) - 2 = 2n$ for $n \ge 1$. Sauer's bound is
    $1 + n + n(n-1)/2$, larger for $n \ge 3$, so here Sauer is not tight.

??? question "4. Evaluate Sauer's bound and its simpler form $(en/d)^d$ for $d = 3$, $n = 10$, and compare with the 92 labellings half-planes really produce."

    $\binom{10}{0} + \binom{10}{1} + \binom{10}{2} + \binom{10}{3} = 1 + 10 + 45 + 120 = 176$, and
    $(10e/3)^3 \approx 743.9$. The true count $n^2 - n + 2 = 92$. Both bounds are polynomial in $n$, which is all the
    proof of the fundamental theorem needs; $(en/d)^d$ is looser but easier to put into formulas.

??? question "5. Prove that half-planes in the plane cannot shatter four points, using Radon's theorem."

    Radon's theorem in $\mathbb R^2$: any 4 points split into two groups $P$ and $N$ whose convex hulls share a
    point $z$. Label $P$ with 1 and $N$ with 0. A half-plane is convex, so if it contains $P$ it contains the hull of
    $P$, hence $z$; its complement is also convex, so if it contains $N$ it contains $z$ too. A point cannot be on both
    sides, so this labelling is not realised. The proof of Radon: the four vectors $(x_i, 1) \in \mathbb R^3$ are
    linearly dependent, giving $\sum\lambda_i x_i = 0$ and $\sum\lambda_i = 0$ with not all $\lambda_i = 0$; split by
    the sign of $\lambda_i$ and normalise.

??? question "6. Compute the empirical Rademacher complexity exactly for two tiny cases: (a) the class with a single function $f$; (b) the class of all functions from $m$ distinct points to $\{-1, +1\}$."

    (a) $E_\sigma[\frac1m\sum\sigma_i f(z_i)] = \frac1m\sum f(z_i)E[\sigma_i] = 0$. (b) For each sign vector the
    function $f(z_i) = \sigma_i$ is in the class, giving $\frac1m\sum\sigma_i^2 = 1$, and nothing can exceed 1; so the
    value is 1. A single function cannot overfit; the class of all functions can fit any noise perfectly.

??? question "7. Write the code: estimate the empirical Rademacher complexity of intervals on $m$ random points ($\pm1$ labels: $+1$ inside, $-1$ outside) by Monte Carlo, and compare with Massart's bound $\sqrt{2\ln\tau(m)/m}$ with $\tau(m) = m(m+1)/2 + 1$."

    For each sign vector, the best interval maximises $\sum_{\text{inside}}\sigma_i - \sum_{\text{outside}}\sigma_i =
    2\sum_{\text{inside}}\sigma_i - \sum_i\sigma_i$, so we need the largest sum of a contiguous block of the sorted
    signs (or 0 for the empty block), the maximum-subarray problem, which prefix sums solve.

    ```python
    import numpy as np
    from math import log, sqrt
    rng = np.random.default_rng(0)
    for m in [10, 40, 160, 640]:
        sig = rng.choice([-1.0, 1.0], size=(4000, m))      # points sorted; only order matters
        P = np.concatenate([np.zeros((4000, 1)), np.cumsum(sig, axis=1)], axis=1)
        best_block = (P - np.minimum.accumulate(P, axis=1)).max(axis=1)   # max contiguous sum, >= 0
        r = (2 * best_block - sig.sum(axis=1)).mean() / m
        print(m, round(r, 4), round(sqrt(2 * log(m * (m + 1) / 2 + 1) / m), 4))
    ```

    It prints `10 0.6148 0.8973`, `40 0.3496 0.5792`, `160 0.1852 0.3439`, `640 0.0955 0.1955`: about 1.5 times the
    value for rays (one extra endpoint to choose) and the same $\sqrt{\log m/m}$ shape. For $m = 6$ an exhaustive
    check over all 64 sign vectors and all intervals gives 0.7396, the same as the prefix-sum formula.

??? question "8. In Theorem 21.10, why must the step size satisfy $\eta < 2/\|A\|^2$, and what does gradient descent converge to if it starts at a random $w_0$?"

    On the row space, the iteration error $e_t = w_t - w^\ast$ satisfies $e_{t+1} = (I - \eta A^\top A)e_t$, and the
    eigenvalues of $A^\top A$ there lie in $(0, \|A\|^2]$. The factor $1 - \eta\lambda$ has absolute value below 1 for
    all of them exactly when $\eta < 2/\|A\|^2$. From a random start, the row-space part converges as before, while
    the kernel part of $w_0$ is never changed, so the limit is $A^+b + (I - A^+A)w_0$. Program part 3 checks this:
    from a random start the solution has norm 8.54 instead of 0.48, the same training error, and agrees with the
    formula to $10^{-14}$.

??? question "9. A friend says: 'My network has 10 million parameters and I trained it on 50000 images, so by VC theory it must overfit.' What is right and wrong in this?"

    Right: the VC dimension of networks grows with the number of weights (for ReLU networks with $W$ weights and $L$
    layers it lies between order $WL\log(W/L)$ and order $WL\log W$; Bartlett, Harvey, Liaw and Mehrabian 2019), so
    the VC bound is vacuous here. Wrong: a vacuous upper bound proves nothing about overfitting; it only fails to prove the opposite.
    Also, the number of parameters is not the VC dimension (the $\sin(\omega x)$ example has one parameter and
    infinite VC dimension; in the other direction, norm-bounded linear classes have small Rademacher complexity in any
    dimension). The friend should measure on held-out data (Chapter 7) and not rely on a worst-case bound.

??? question "10. In the SRM experiment, the weights were $w_k = 2^{-k}$. What penalty would class $k = 3$ get with $w_k = 6/(\pi^2 k^2)$ instead, and why are both choices allowed?"

    Both sequences sum to at most 1 ($\sum 2^{-k} = 1$, $\sum 6/(\pi^2k^2) = 1$), which is all the union-bound proof
    needs. For $k = 3$: $w_3 = 6/(9\pi^2) = 0.0675$, $\delta w_3 = 0.003377$, $\ln(1/0.003377) = 5.691$, so the second
    term is $\sqrt{5.691/600} = 0.0974$ instead of 0.0920; the first term $0.4433$ is unchanged, giving 0.5407 instead
    of 0.5352. The weights encode a prior preference over classes; $1/k^2$ decays more slowly and so is kinder to large
    $k$.

??? question "11. (Hard) Prove that the class of unions of $k$ intervals has VC dimension exactly $2k$."

    Lower bound: take $2k$ points $x_1 < \dots < x_{2k}$. Any labelling has at most $k$ maximal runs of 1s (a run of
    1s needs a 0 or the end after it, and runs alternate with runs of 0s, so $2k$ positions hold at most $k$ runs of
    1s). Cover each run with one interval: shattered. Upper bound: with $2k + 1$ points, the labelling
    $1, 0, 1, 0, \dots, 1$ has $k + 1$ separate runs of 1s; any union of intervals covering them without covering the
    0s between them needs a different interval for each run, so $k + 1$ intervals. Hence no set of $2k + 1$ points is
    shattered.

??? question "12. (Hard) Show that if $\mathrm{VCdim}(\mathcal H) = \infty$ then $\mathcal H$ is not PAC learnable, by a counting argument."

    Fix any learner and any $m$. Choose $2m$ points that $\mathcal H$ shatters, and let $\mathcal D$ be uniform on
    them. Average over all $2^{2m}$ target labellings, each realised by some $h \in \mathcal H$, so each one is a valid
    realizable target. The sample contains at most $m$ distinct points, so at least half of the support is unseen,
    and on an unseen point the average target label is a fair coin independent of everything the learner saw. So the
    average (over targets) expected error is at least $\frac12\cdot\frac12 = \frac14$, and some target has expected
    error at least $1/4$. Write $q = \Pr[L_{\mathcal D}(h_S) \ge 1/8]$ for that target. Since the error is at most 1,
    $\frac14 \le E[L] \le q + \frac18(1 - q)$, so $q \ge 1/7$. No $m$ achieves $\varepsilon = 1/8$, $\delta = 1/7$.

## What you learned

- Learning from examples needs an assumption: the training and future examples are i.i.d. draws from one
  distribution. The question is then uniform convergence: training error close to true error for every hypothesis at
  once, because the learner chooses after looking.
- A finite class needs $(\ln|\mathcal H| + \ln(1/\delta))/\varepsilon$ examples if the target is inside it, and
  $\ln(2|\mathcal H|/\delta)/(2\varepsilon^2)$ in general; the proofs are one inequality (Hoeffding) and one union
  bound.
- The VC dimension counts behaviours on data, not parameters. Sauer's lemma turns finite VC dimension into a
  polynomial growth function, and the fundamental theorem says finite VC dimension is equivalent to PAC learnability,
  with sample size about $d/\varepsilon^2$.
- Rademacher complexity measures how well a class fits random signs; it recovers the VC bound through Massart's lemma
  and gives dimension-free margin bounds, $BR/(\rho\sqrt m)$, that justify large-margin classifiers.
- Error splits into approximation and estimation error; SRM trades them by minimising training error plus a penalty,
  and validation and regularisation are its practical forms.
- Deep networks fit random labels, show double descent, and generalise anyway. Class-only bounds cannot explain this;
  the implicit bias of gradient descent (minimum norm, maximum margin) and the neural tangent kernel explain special
  cases, and the general question is open.

**Next:** [Chapter 22](22-Machine-Learning-in-Practice.md), what changes when the i.i.d. assumption meets real
systems: pipelines, distribution shift, fairness, interpretability, robustness and privacy.

## Further reading

- L. G. Valiant, "A Theory of the Learnable", *Communications of the ACM*, 1984. The paper that defined PAC learning.
- V. N. Vapnik and A. Y. Chervonenkis, "On the Uniform Convergence of Relative Frequencies of Events to Their
  Probabilities", *Theory of Probability and its Applications*, 1971.
- W. Hoeffding, "Probability Inequalities for Sums of Bounded Random Variables", *Journal of the American Statistical
  Association*, 1963.
- N. Sauer, "On the Density of Families of Sets", *Journal of Combinatorial Theory, Series A*, 1972.
- A. Blumer, A. Ehrenfeucht, D. Haussler and M. K. Warmuth, "Occam's Razor", *Information Processing Letters*, 1987;
  and "Learnability and the Vapnik-Chervonenkis Dimension", *Journal of the ACM*, 1989.
- S. Shalev-Shwartz and S. Ben-David, *Understanding Machine Learning: From Theory to Algorithms*, 2014. Chapters 2 to
  7 and 26 cover this chapter with full proofs.
- M. Mohri, A. Rostamizadeh and A. Talwalkar, *Foundations of Machine Learning*, 2nd ed., 2018. Chapters 2, 3 and 5
  for PAC, Rademacher and margin bounds.
- V. N. Vapnik, *Statistical Learning Theory*, 1998. SRM and the original view of the subject.
- P. L. Bartlett and S. Mendelson, "Rademacher and Gaussian Complexities: Risk Bounds and Structural Results",
  *Journal of Machine Learning Research*, 2002.
- S. Hanneke, "The Optimal Sample Complexity of PAC Learning", *Journal of Machine Learning Research*, 2016.
- C. Zhang, S. Bengio, M. Hardt, B. Recht and O. Vinyals, "Understanding Deep Learning Requires Rethinking
  Generalization", ICLR 2017.
- M. Belkin, D. Hsu, S. Ma and S. Mandal, "Reconciling Modern Machine-Learning Practice and the Classical
  Bias-Variance Trade-off", *PNAS*, 2019; P. Nakkiran et al., "Deep Double Descent: Where Bigger Models and More Data
  Hurt", ICLR 2020.
- P. L. Bartlett, P. M. Long, G. Lugosi and A. Tsigler, "Benign Overfitting in Linear Regression", *PNAS*, 2020.
- D. Soudry, E. Hoffer, M. S. Nacson, S. Gunasekar and N. Srebro, "The Implicit Bias of Gradient Descent on Separable
  Data", *Journal of Machine Learning Research*, 2018.
- A. Jacot, F. Gabriel and C. Hongler, "Neural Tangent Kernel: Convergence and Generalization in Neural Networks",
  NeurIPS 2018; L. Chizat, E. Oyallon and F. Bach, "On Lazy Training in Differentiable Programming", NeurIPS 2019.
- G. K. Dziugaite and D. M. Roy, "Computing Nonvacuous Generalization Bounds for Deep (Stochastic) Neural Networks
  with Many More Parameters than Training Data", UAI 2017.
- On this site: [Chapter 7](07-Evaluating-Models.md) (held-out data and cross-validation, the practical side of
  this chapter), [Chapter 8](08-Overfitting-and-Regularization.md) (bias and variance),
  [Chapter 10](10-Support-Vector-Machines.md) (margins), [Chapter 16](16-Training-Deep-Networks.md) (training the
  networks whose generalisation is still a puzzle), the Algorithms book's
  [Chapter 21](../algorithms/21-Randomized-and-Amortized-Analysis.md) for Markov, Chebyshev and Chernoff bounds, and
  the probability book at https://math.akadian.ca/books/probability/.
