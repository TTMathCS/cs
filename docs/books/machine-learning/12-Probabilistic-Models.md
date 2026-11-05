# 12. Probabilistic models and Bayesian learning

*Most models in this book so far produce a single answer: one weight vector, one prediction. But a model that has
seen three coin flips should be less sure than one that has seen three thousand, and a regression curve should know
that it is guessing far from its data. Probabilistic models say how uncertain they are. This chapter treats learning
as reasoning with probabilities: you will build classifiers by modelling how each class generates its data (naive
Bayes, Gaussian discriminant analysis), put priors on parameters and update them with Bayes' rule (the beta-binomial
model, Bayesian linear regression), meet the Gaussian process, a prior over whole functions, and finally learn to
sample from a posterior that has no formula, with Markov chain Monte Carlo.*

!!! abstract "In this chapter"
    **You will learn:**

    - the difference between generative and discriminative models, and when each wins
    - naive Bayes for text, its maximum-likelihood estimates derived, Laplace smoothing, and log-space arithmetic
    - maximum likelihood, MAP and full Bayesian inference compared on the beta-binomial model, with conjugacy proved
    - the posterior and predictive distributions of Bayesian linear regression, derived, and the evidence for choosing models
    - Gaussian discriminant analysis: why shared covariances give linear boundaries (LDA) and separate ones quadratic (QDA)
    - Gaussian processes from scratch: the conditioning formula proved, predictions, and the marginal likelihood
    - Monte Carlo integration and the Metropolis-Hastings algorithm, with detailed balance proved

    **You need:** [Chapter 3](03-The-Math-Toolkit.md) (probability, Bayes' rule, the Gaussian, likelihood),
    [Chapter 4](04-Linear-Regression.md) (least squares), [Chapter 6](06-Classification-and-Logistic-Regression.md)
    (logistic regression), [Chapter 8](08-Overfitting-and-Regularization.md) (ridge regression) and
    [Chapter 9](09-Nearest-Neighbours-and-Kernels.md) (kernels, kernel ridge regression). The probability and
    statistics books at [https://math.akadian.ca/books/](https://math.akadian.ca/books/) cover the background.

    **Levels:** 12.1 to 12.3 are intermediate; 12.4 and 12.5 are intermediate to advanced; 12.6 and 12.7 are advanced.

## 12.1 Generative vs discriminative

To classify an input $x$ into a class $y$, the ideal is the **posterior probability** $P(y \mid x)$: predict the class
with the largest one, and you have the Bayes classifier of [Chapter 9](09-Nearest-Neighbours-and-Kernels.md). There
are two ways to get there.

A **discriminative** model learns $P(y \mid x)$ directly, or even just a decision boundary. Logistic regression
([Chapter 6](06-Classification-and-Logistic-Regression.md)) models $P(y = 1 \mid x) = \sigma(w \cdot x + b)$ and never
asks how the inputs themselves are distributed. Support vector machines and trees are discriminative too.

A **generative** model learns how the data are produced: a **prior** $P(y)$ over classes, and a **class-conditional
distribution** $p(x \mid y)$ that says what inputs of each class look like. Together they give the joint distribution
$p(x, y) = P(y)\,p(x \mid y)$, and **Bayes' rule** turns that into the posterior:

$$
P(y \mid x) = \frac{P(y)\, p(x \mid y)}{\sum_{c} P(c)\, p(x \mid c)}.
$$

The name comes from the fact that such a model can *generate* new data: draw a class from $P(y)$, then an input from
$p(x \mid y)$.

Why model more than you need? A generative model can do things a discriminative one cannot: generate samples, detect
inputs that are unlikely under every class (outliers), handle a missing feature by summing over its values, and use
unlabelled examples. And when its assumptions are right it learns from very few examples, because it uses the data to
estimate a few interpretable quantities (class means, word frequencies). The risk is in "when its assumptions are
right": a generative model must describe the inputs, which may be far more complicated than the boundary between
classes. A discriminative model spends all its data on the boundary.

Andrew Ng and Michael Jordan made this precise ("On Discriminative vs. Generative Classifiers: A Comparison of
Logistic Regression and Naive Bayes", 2002). For naive Bayes against logistic regression with $d$ features they proved
that naive Bayes approaches its own asymptotic error with a number of examples that grows only like $\log d$, while
logistic regression may need a number that grows like $d$; but logistic regression's asymptotic error is never worse,
and is better whenever naive Bayes' assumption is false. So generative models often win with little data and
discriminative ones with a lot. The race in 12.5 shows both halves of that statement.

## 12.2 Naive Bayes for text (spam), Laplace smoothing

Filtering spam was one of the first large-scale successes of machine learning in daily life, and the classic method
is a generative model of almost embarrassing simplicity.

**The model.** Represent a message by its words $w_1, \dots, w_L$ (a **bag of words**: order is ignored). The class is
$y \in \{\text{spam}, \text{ham}\}$ ("ham" is the field's word for wanted mail). The **multinomial naive Bayes** model
says: choose the class with probability $\pi_y$; then draw each word independently from a class-specific distribution
$\theta_{y}$ over the vocabulary, where $\theta_{y,w}$ is the probability that a word of a class-$y$ message is $w$. So

$$
p(w_1, \dots, w_L \mid y) = \prod_{j=1}^L \theta_{y, w_j}.
$$

The assumption that words are independent given the class is the "naive" part. It is plainly false ("free" and
"offer" go together), and yet the classifier works well. Pedro Domingos and Michael Pazzani ("On the Optimality of the
Simple Bayesian Classifier under Zero-One Loss", 1997) explained part of the puzzle: classification needs only the
right *ordering* of the class posteriors, and the ordering can be right even when the probabilities themselves are
badly off. Naive Bayes probabilities are typically overconfident, close to 0 or 1.

**Learning by maximum likelihood.** For class $y$, let $n_{y,w}$ be the number of times word $w$ appears in its
training messages and $N_y = \sum_w n_{y,w}$. The log-likelihood of those words is $\sum_w n_{y,w} \log\theta_{y,w}$, to
be maximised subject to $\sum_w \theta_{y,w} = 1$. With a Lagrange multiplier $\mu$ ([Chapter 10](10-Support-Vector-Machines.md)),
set the derivative of $\sum_w n_{y,w}\log\theta_{y,w} - \mu(\sum_w \theta_{y,w} - 1)$ to zero: $n_{y,w}/\theta_{y,w} = \mu$, so
$\theta_{y,w} \propto n_{y,w}$, and normalising gives

$$
\hat\theta_{y,w} = \frac{n_{y,w}}{N_y}, \qquad \hat\pi_y = \frac{\text{number of class-}y\text{ messages}}{\text{number of messages}}.
$$

Counting is the whole of training. That makes naive Bayes extremely fast, and it can be updated one message at a time.

**The zero-count disaster, and Laplace smoothing.** If the word "money" never appeared in a ham training message, then
$\hat\theta_{\text{ham},\text{money}} = 0$, and *any* message containing "money" gets $P(\text{ham} \mid \text{message}) = 0$, however hammy
the rest of it is. One unseen word vetoes all the evidence. The fix, going back to Laplace, is to add a pseudo-count
$\alpha$ (usually 1) to every word of the vocabulary $V$:

$$
\hat\theta_{y,w} = \frac{n_{y,w} + \alpha}{N_y + \alpha |V|}.
$$

With $\alpha = 1$ this is **Laplace** (add-one) **smoothing**. It is not a hack: 12.3 shows it is exactly the posterior
mean of $\theta_y$ under a uniform (Dirichlet) prior, the multi-word version of the rule of succession.

**Computing in log space.** A product of hundreds of probabilities like 0.001 underflows to 0 in floating point.
Take logarithms: the class score is $\log\hat\pi_y + \sum_j \log\hat\theta_{y,w_j}$, a sum. To turn scores $s_y$ back
into probabilities, subtract the largest before exponentiating, $P(y \mid x) = e^{s_y - s_{\max}} / \sum_c e^{s_c - s_{\max}}$
(the **log-sum-exp trick**), which gives the same ratio without overflow or underflow. In log space the log-odds is

$$
\log\frac{P(\text{spam} \mid x)}{P(\text{ham} \mid x)} = \log\frac{\hat\pi_{\text{spam}}}{\hat\pi_{\text{ham}}} + \sum_{w} c_w(x) \log\frac{\hat\theta_{\text{spam},w}}{\hat\theta_{\text{ham},w}},
$$

where $c_w(x)$ counts word $w$ in the message: **naive Bayes is a linear classifier in the word counts**, with each word
contributing its log-ratio of frequencies. The same linear form as logistic regression, with weights set by counting
instead of by optimisation.

The program uses a tiny made-up corpus of 14 messages typed into the file (6 spam, 8 ham), so that every number can
be checked by hand.

```python
--8<-- "books/machine-learning/ch12_naive_bayes.py"
```

```
vocabulary: 31 words; words in spam: 24, in ham: 33
priors: P(spam) = 0.4286, P(ham) = 0.5714

Smoothed word probabilities (alpha = 1)
  word      count spam  P(w|spam)  count ham  P(w|ham)
  free               4     0.0909          0    0.0156
  money              2     0.0545          0    0.0156
  now                3     0.0727          0    0.0156
  monday             0     0.0182          3    0.0625
  meeting            0     0.0182          3    0.0625
  offer              3     0.0727          0    0.0156
  review             0     0.0182          2    0.0469

Hand example: the message 'free money'
  log P(ham) + log P(free|ham) + log P(money|ham) = -8.8774
  log P(spam) + log P(free|spam) + log P(money|spam) = -6.1539
  P(spam | 'free money') = 0.9384

Test messages
  alpha = 1.0:
    free money                   true spam  P(spam) = 0.9384
    project lunch monday         true ham   P(spam) = 0.0240
    claim cash now               true spam  P(spam) = 0.9770
    meeting notes                true ham   P(spam) = 0.0780
    win a cheap prize            true spam  P(spam) = 0.9851
    review the offer on monday   true ham   P(spam) = 0.0816
  alpha = 0.0:
    free money                   true spam  P(spam) = 1.0000
    project lunch monday         true ham   P(spam) = 0.0000
    claim cash now               true spam  P(spam) = 1.0000
    meeting notes                true ham   P(spam) = 0.0000
    win a cheap prize            true spam  P(spam) = 1.0000
    review the offer on monday   true ham   P(spam) = nan
With alpha = 0 one unseen (word, class) pair forces a probability of exactly 0 or 1,
and a message with one word never seen in spam and another never seen in ham
gets 0/0: no answer at all (nan).
```

**The hand example.** The vocabulary has $|V| = 31$ words; spam messages contain 24 words, ham messages 33. "free"
occurs 4 times in spam, so $\hat\theta_{\text{spam},\text{free}} = (4 + 1)/(24 + 31) = 5/55 = 0.0909$; it never occurs in
ham, so $\hat\theta_{\text{ham},\text{free}} = 1/(33 + 31) = 1/64 = 0.0156$. For the message "free money" the spam score is
$\log\tfrac{6}{14} + \log\tfrac{5}{55} + \log\tfrac{3}{55} = -0.847 - 2.398 - 2.909 = -6.154$ and the ham score is
$\log\tfrac{8}{14} + 2\log\tfrac{1}{64} = -0.560 - 8.318 = -8.877$. The difference is $2.723$, so
$P(\text{spam} \mid \text{free money}) = 1/(1 + e^{-2.723}) = 0.938$.

With smoothing, all six test messages are classified correctly and with sensible confidence. Without it, every
probability is exactly 0 or 1, and "review the offer on monday" gets no answer: "offer" was never seen in ham and
"review" never in spam, so both class scores are $-\infty$.

**History.** Probabilistic text classification of this kind goes back to the 1960s (Melvin Maron's work on automatic
indexing, 1961). For spam, Mehran Sahami, Susan Dumais, David Heckerman and Eric Horvitz published "A Bayesian Approach
to Filtering Junk E-Mail" in 1998, and Paul Graham's 2002 essay "A Plan for Spam" popularised the approach among
programmers; many mail filters were built on it.

## 12.3 MLE vs MAP vs full Bayes; conjugate priors (beta-binomial) worked

You flip a coin three times and get three heads. What is the probability $p$ of heads? Three answers are possible, and
the differences between them are the heart of Bayesian learning.

**Maximum likelihood (MLE).** The likelihood of $h$ heads in $n$ flips is $L(p) = p^h (1 - p)^{n-h}$ (times a binomial
coefficient that does not depend on $p$). Its log, $h\log p + (n - h)\log(1 - p)$, has derivative
$h/p - (n-h)/(1 - p)$, which vanishes at $\hat p = h/n$. Three heads in three flips gives $\hat p = 1$: the MLE is
certain the coin can never land tails. With little data, maximum likelihood overfits.

**A prior.** A Bayesian treats $p$ itself as uncertain and describes that uncertainty by a **prior distribution**. For a
probability, the natural family is the **beta distribution** $\mathrm{Beta}(a, b)$ with density

$$
\mathrm{Beta}(p \mid a, b) = \frac{p^{a-1}(1 - p)^{b-1}}{B(a, b)}, \qquad 0 < p < 1,
$$

where $B(a, b) = \Gamma(a)\Gamma(b)/\Gamma(a+b)$ makes it integrate to 1. Its mean is $a/(a+b)$ and, for $a, b > 1$, its
mode (peak) is $(a - 1)/(a + b - 2)$. $\mathrm{Beta}(1, 1)$ is uniform; $\mathrm{Beta}(2, 2)$ is a gentle hump expressing
a mild belief that the coin is roughly fair; $\mathrm{Beta}(50, 50)$ a strong one.

**The posterior, and conjugacy.** Bayes' rule for a parameter reads: **posterior** $\propto$ **likelihood** $\times$
**prior**. With a beta prior:

$$
p(p \mid \text{data}) \propto p^h (1 - p)^{n-h} \cdot p^{a-1}(1 - p)^{b-1} = p^{h + a - 1}(1 - p)^{n - h + b - 1}.
$$

That is the shape of $\mathrm{Beta}(a + h,\, b + n - h)$, and since a density is determined by its shape up to the
normalising constant, the posterior *is* that beta distribution. When prior and posterior belong to the same family,
the prior is called **conjugate** to the likelihood. The update is just adding counts: $a$ and $b$ act as
**pseudo-counts** of heads and tails seen before the experiment.

**Three estimates.** With the prior $\mathrm{Beta}(2, 2)$ and three heads in three flips, the posterior is $\mathrm{Beta}(5, 2)$.

- **MLE:** $h/n = 1$.
- **MAP** (maximum a posteriori, the posterior's mode): $(h + a - 1)/(n + a + b - 2) = 4/5 = 0.8$. With a uniform prior
  MAP equals MLE: MAP is "maximum likelihood plus a penalty", the penalty being $-\log(\text{prior})$. (Ridge
  regression is MAP with a Gaussian prior, 12.4.)
- **Full Bayes** does not pick one $p$ at all. It keeps the whole posterior and averages over it. The probability that
  the next flip is heads is

$$
P(\text{heads} \mid \text{data}) = \int_0^1 p \cdot \mathrm{Beta}(p \mid a + h, b + n - h)\, dp = \frac{a + h}{a + b + n} = \frac57 = 0.714,
$$

the posterior mean. This **posterior predictive** distribution accounts for our uncertainty about $p$.

The posterior mean is a compromise, and a precise one:

$$
\frac{a + h}{a + b + n} = \lambda \cdot \frac{a}{a+b} + (1 - \lambda) \cdot \frac{h}{n}, \qquad \lambda = \frac{a + b}{a + b + n},
$$

a weighted average of the prior mean and the MLE, with the prior weighted as if it were $a + b$ observations. As $n$
grows, $\lambda \to 0$ and the data take over. This **shrinkage** towards the prior is the same phenomenon as ridge
regression's shrinkage towards zero.

<figure class="mars-fig" markdown="0">
<svg viewBox="0 0 640 270" role="img" aria-label="Densities on p from 0 to 1. The prior Beta(2,2) is a low symmetric hump peaking at 1.5 at p = 0.5. The likelihood of three heads in three flips, p cubed scaled to integrate to one, rises steeply to 4 at p = 1. The posterior Beta(5,2) peaks at p = 0.8 with height 2.46; its mean 0.714 is marked.">
  <g font-size="12" fill="currentColor" stroke="currentColor" text-anchor="middle">
    <line x1="80" y1="220" x2="540" y2="220" stroke-width="1"/><line x1="80" y1="220" x2="80" y2="20" stroke-width="1"/>
    <line x1="80" y1="220" x2="80" y2="225"/><text x="80" y="240" stroke="none">0</text>
    <line x1="195" y1="220" x2="195" y2="225"/><text x="195" y="240" stroke="none">0.25</text>
    <line x1="310" y1="220" x2="310" y2="225"/><text x="310" y="240" stroke="none">0.5</text>
    <line x1="425" y1="220" x2="425" y2="225"/><text x="425" y="240" stroke="none">0.75</text>
    <line x1="540" y1="220" x2="540" y2="225"/><text x="540" y="240" stroke="none">1</text>
    <line x1="75" y1="172" x2="80" y2="172"/><text x="70" y="176" stroke="none" text-anchor="end">1</text>
    <line x1="75" y1="124" x2="80" y2="124"/><text x="70" y="128" stroke="none" text-anchor="end">2</text>
    <line x1="75" y1="76" x2="80" y2="76"/><text x="70" y="80" stroke="none" text-anchor="end">3</text>
    <line x1="75" y1="28" x2="80" y2="28"/><text x="70" y="32" stroke="none" text-anchor="end">4</text>
    <text x="310" y="262" stroke="none">p, the probability of heads</text>
    <line x1="408.6" y1="220" x2="408.6" y2="112.9" stroke-dasharray="4 3" stroke-width="1"/>
  </g>
  <g fill="none" stroke-width="3">
    <polyline stroke="#9cc9ea" points="82.3,218.6 89.2,214.4 96.1,210.3 103.0,206.3 109.9,202.5 116.8,198.8 123.7,195.2 130.6,191.8 137.5,188.5 144.4,185.3 151.3,182.3 158.2,179.4 165.1,176.6 172.0,173.9 178.9,171.4 185.8,169.0 192.7,166.7 199.6,164.6 206.5,162.6 213.4,160.7 220.3,159.0 227.2,157.3 234.1,155.8 241.0,154.5 247.9,153.2 254.8,152.1 261.7,151.2 268.6,150.3 275.5,149.6 282.4,149.0 289.3,148.6 296.2,148.3 303.1,148.1 310.0,148.0 316.9,148.1 323.8,148.3 330.7,148.6 337.6,149.0 344.5,149.6 351.4,150.3 358.3,151.2 365.2,152.1 372.1,153.2 379.0,154.5 385.9,155.8 392.8,157.3 399.7,159.0 406.6,160.7 413.5,162.6 420.4,164.6 427.3,166.7 434.2,169.0 441.1,171.4 448.0,173.9 454.9,176.6 461.8,179.4 468.7,182.3 475.6,185.3 482.5,188.5 489.4,191.8 496.3,195.2 503.2,198.8 510.1,202.5 517.0,206.3 523.9,210.3 530.8,214.4 537.7,218.6"/>
    <polyline stroke="#7ccf9a" stroke-dasharray="7 4" points="82.3,220.0 89.2,220.0 96.1,220.0 103.0,220.0 109.9,219.9 116.8,219.9 123.7,219.8 130.6,219.7 137.5,219.6 144.4,219.5 151.3,219.3 158.2,219.1 165.1,218.8 172.0,218.5 178.9,218.1 185.8,217.7 192.7,217.2 199.6,216.6 206.5,216.0 213.4,215.3 220.3,214.6 227.2,213.7 234.1,212.8 241.0,211.8 247.9,210.7 254.8,209.5 261.7,208.2 268.6,206.8 275.5,205.3 282.4,203.6 289.3,201.9 296.2,200.1 303.1,198.1 310.0,196.0 316.9,193.8 323.8,191.4 330.7,188.9 337.6,186.3 344.5,183.5 351.4,180.6 358.3,177.5 365.2,174.2 372.1,170.8 379.0,167.3 385.9,163.5 392.8,159.6 399.7,155.5 406.6,151.3 413.5,146.8 420.4,142.2 427.3,137.4 434.2,132.3 441.1,127.1 448.0,121.7 454.9,116.1 461.8,110.2 468.7,104.2 475.6,97.9 482.5,91.4 489.4,84.6 496.3,77.7 503.2,70.5 510.1,63.1 517.0,55.4 523.9,47.5 530.8,39.3 537.7,30.9"/>
    <polyline stroke="#eea66f" points="82.3,220.0 89.2,220.0 96.1,220.0 103.0,220.0 109.9,220.0 116.8,219.9 123.7,219.9 130.6,219.8 137.5,219.7 144.4,219.5 151.3,219.3 158.2,219.0 165.1,218.6 172.0,218.2 178.9,217.6 185.8,216.9 192.7,216.1 199.6,215.1 206.5,214.0 213.4,212.8 220.3,211.3 227.2,209.7 234.1,207.9 241.0,206.0 247.9,203.8 254.8,201.4 261.7,198.8 268.6,196.0 275.5,193.0 282.4,189.8 289.3,186.4 296.2,182.8 303.1,179.0 310.0,175.0 316.9,170.9 323.8,166.6 330.7,162.2 337.6,157.7 344.5,153.1 351.4,148.5 358.3,143.8 365.2,139.1 372.1,134.5 379.0,130.0 385.9,125.7 392.8,121.5 399.7,117.5 406.6,113.9 413.5,110.6 420.4,107.7 427.3,105.4 434.2,103.6 441.1,102.4 448.0,102.0 454.9,102.5 461.8,103.8 468.7,106.2 475.6,109.7 482.5,114.5 489.4,120.6 496.3,128.2 503.2,137.5 510.1,148.5 517.0,161.4 523.9,176.3 530.8,193.4 537.7,212.9"/>
  </g>
  <g font-size="12" fill="currentColor">
    <rect x="110" y="34" width="14" height="4" fill="#9cc9ea"/><text x="130" y="40">prior Beta(2, 2)</text>
    <rect x="110" y="54" width="14" height="4" fill="#7ccf9a"/><text x="130" y="60">likelihood p^3 (scaled)</text>
    <rect x="110" y="74" width="14" height="4" fill="#eea66f"/><text x="130" y="80">posterior Beta(5, 2)</text>
    <text x="403" y="210" text-anchor="end">mean 0.714</text>
  </g>
</svg>
<figcaption>Bayesian updating for three heads in three flips. The prior Beta(2, 2) (blue) times the likelihood p³
(green, dashed, scaled to area 1) gives the posterior Beta(5, 2) (orange). The likelihood alone peaks at p = 1; the
posterior peaks at 0.8 and has mean 0.714.</figcaption>
</figure>

**Credible intervals.** The posterior also gives intervals: a **95 percent credible interval** contains $p$ with
posterior probability 0.95. For $\mathrm{Beta}(5, 2)$ the central one is $[0.359, 0.957]$: three flips say "probably
biased towards heads", with honest width. A credible interval is a statement about $p$ given the data. A frequentist
confidence interval ([Chapter 7](07-Evaluating-Models.md)) is a statement about a procedure: over many repetitions of
the experiment, 95 percent of the intervals it produces contain the true $p$. With plenty of data the two usually
nearly agree; with three flips they can be quite different.

```python
--8<-- "books/machine-learning/ch12_beta_binomial.py"
```

```
Three flips, three heads. Prior Beta(2, 2) (a mild belief that the coin is fair).
  MLE            h/n                     = 1.0000
  MAP            (h+a-1)/(n+a+b-2)       = 0.8000
  posterior mean (h+a)/(n+a+b)           = 0.7143
  P(next is heads | data) = posterior mean = 0.7143
  95% central credible interval for p: [0.359, 0.957]

How the estimates move as data arrive (true p = 0.7, same Beta(2,2) prior)
   n  heads    MLE     MAP   post. mean   95% interval
   1      1  1.000   0.667       0.600   [0.194, 0.932]
   2      2  1.000   0.750       0.667   [0.284, 0.947]
   5      4  0.800   0.714       0.667   [0.349, 0.915]
  10      7  0.700   0.667       0.643   [0.386, 0.861]
  20     14  0.700   0.682       0.667   [0.471, 0.836]

Sequential and batch updating give the same posterior:
  one flip at a time: Beta(9, 5);  all ten at once: Beta(9, 5)

Laplace's rule of succession (uniform prior Beta(1,1)): after n successes in n trials,
  n =   1: P(next success) = (n+1)/(n+2) = 0.6667
  n =  10: P(next success) = (n+1)/(n+2) = 0.9167
  n = 100: P(next success) = (n+1)/(n+2) = 0.9902

Posterior density of p after 3 heads in 3 flips, prior Beta(2,2): Beta(5, 2)
  p = 0.10: density 0.0027
  p = 0.30: density 0.1701
  p = 0.50: density 0.9375
  p = 0.70: density 2.1609
  p = 0.80: density 2.4576
  p = 0.90: density 1.9683
  p = 0.99: density 0.2882
```

Watch the table as the data arrive. After one head, the MLE already says $\hat p = 1$, while the posterior mean says
0.6 and the interval spans most of $[0, 1]$. By 20 flips the three estimates agree to within 0.04 and the interval has
narrowed to $[0.47, 0.84]$. This is a general fact (the **Bernstein-von Mises theorem**, stated here without proof):
under regularity conditions, as $n \to \infty$ the posterior becomes approximately Gaussian, centred at the MLE, with
variance shrinking like $1/n$, so Bayesian and frequentist answers converge. Updating one flip at a time gives the
same posterior as using all the data at once, because multiplying the likelihoods in any order gives the same product:
yesterday's posterior is today's prior.

**Laplace's rule of succession.** With the uniform prior $\mathrm{Beta}(1, 1)$, after $n$ successes in $n$ trials the
predictive probability of another success is $(n+1)/(n+2)$. Pierre-Simon Laplace used it (in his *Essai philosophique
sur les probabilités*, 1814) for the question of whether the sun will rise tomorrow. The rule never gives probability 1:
no finite amount of evidence makes the model certain. Laplace smoothing in 12.2 is the same rule for many words: with a
uniform Dirichlet prior on the word probabilities (the Dirichlet is the beta's many-outcome version), the posterior mean
is $(n_{y,w} + 1)/(N_y + |V|)$.

**One caution about MAP.** The mode of a density changes when you change variables (a density picks up a Jacobian
factor), so the MAP estimate of $p$ and the MAP estimate of $\log\frac{p}{1-p}$ do not correspond. Posterior means,
medians and predictions do not have this defect. MAP is best thought of as regularized maximum likelihood, useful
but not fully Bayesian.

<figure class="play" data-play="betacoin"><span class="ai-tag">AI-created</span><figcaption><b>Try it.</b> Flip a hidden coin (it lands heads 70% of the time) and watch the Beta posterior narrow around the truth, starting from a flat prior.</figcaption></figure>

## 12.4 Bayesian linear regression: posterior and predictive, derived

Ridge regression gave one weight vector. The Bayesian version gives a distribution over weight vectors, and with it
error bars on every prediction.

**The model.** Features $\phi(x) \in \mathbb{R}^d$ (raw inputs, or polynomial features), stacked in a design matrix
$\Phi$ with rows $\phi(x_i)^\top$. Targets are $y = \Phi w + \varepsilon$ with independent Gaussian noise
$\varepsilon_i \sim N(0, \sigma^2)$, so the likelihood is $p(y \mid w) \propto \exp\big(-\lVert y - \Phi w \rVert^2 / (2\sigma^2)\big)$
([Chapter 4](04-Linear-Regression.md) showed that maximising it is least squares). The prior is $w \sim N(0, \tau^2 I)$:
each weight is probably not huge.

**The posterior, by completing the square.** The log-posterior is, up to constants,

$$
-\frac{1}{2\sigma^2}\lVert y - \Phi w \rVert^2 - \frac{1}{2\tau^2}\lVert w \rVert^2
= -\frac12 w^\top \Big(\frac{\Phi^\top\Phi}{\sigma^2} + \frac{I}{\tau^2}\Big) w + w^\top \frac{\Phi^\top y}{\sigma^2} + \text{const}.
$$

A Gaussian $N(m, S)$ has log-density $-\tfrac12 (w - m)^\top S^{-1} (w - m) = -\tfrac12 w^\top S^{-1} w + w^\top S^{-1} m + \text{const}$.
Matching the quadratic terms and then the linear terms:

$$
S = \Big(\frac{\Phi^\top\Phi}{\sigma^2} + \frac{I}{\tau^2}\Big)^{-1}, \qquad m = \frac{1}{\sigma^2}\, S\, \Phi^\top y.
$$

So the posterior is Gaussian (the Gaussian prior is conjugate to the Gaussian likelihood). Its inverse covariance,
the **precision**, is the prior precision $I/\tau^2$ plus the data precision $\Phi^\top\Phi/\sigma^2$: information adds.

**The MAP estimate is ridge regression.** The mean (which is also the mode, for a Gaussian) is
$m = (\Phi^\top\Phi + \tfrac{\sigma^2}{\tau^2} I)^{-1} \Phi^\top y$: ridge regression with $\lambda = \sigma^2/\tau^2$
([Chapter 8](08-Overfitting-and-Regularization.md)). A strong prior (small $\tau^2$) or noisy data (large $\sigma^2$)
means strong regularization. The Bayesian view explains the ridge penalty and adds what ridge lacks: the covariance
$S$, which says how sure we are about each weight.

**The predictive distribution.** For a new input with features $\phi_\ast$, the target is $y_\ast = \phi_\ast^\top w + \varepsilon$.
With $w \sim N(m, S)$ and independent noise, $y_\ast$ is Gaussian with

$$
E[y_\ast] = \phi_\ast^\top m, \qquad \mathrm{Var}[y_\ast] = \sigma^2 + \phi_\ast^\top S\, \phi_\ast.
$$

The variance has two parts: $\sigma^2$, the noise that no amount of data removes, and $\phi_\ast^\top S \phi_\ast$, our
uncertainty about $w$, which is small where the training data constrain the prediction and large where they do not.

**By hand, one weight.** Model $y = wx + \varepsilon$, prior $w \sim N(0, 1)$, $\sigma^2 = 1$. After one point
$(x, y) = (2, 3)$: $S = 1/(4 + 1) = 0.2$ and $m = 0.2 \cdot 2 \cdot 3 = 1.2$. The least-squares answer would be
$3/2 = 1.5$; the prior pulls it towards 0. After all four points of the program, $\sum x_i^2 = 15$ and $\sum x_i y_i = 24$,
so $S = 1/16$ and $m = 24/16 = 1.5$, with posterior standard deviation $0.25$.

**The evidence.** How should we choose $\tau^2$, $\sigma^2$, or the degree of a polynomial? Bayesian reasoning offers
the **marginal likelihood**, or **evidence**: the probability of the data under the model with the weights integrated
out. Here $y = \Phi w + \varepsilon$ is a linear function of the independent Gaussians $w$ and $\varepsilon$, so it is
Gaussian with mean 0 and covariance $\tau^2 \Phi\Phi^\top + \sigma^2 I$:

$$
p(y) = N\big(y \mid 0,\; \tau^2 \Phi\Phi^\top + \sigma^2 I\big).
$$

A model that is too simple cannot produce the data and has low evidence. A model that is too flexible spreads its
probability over a huge variety of possible data sets, so it gives low probability to the one we saw. The evidence
peaks in between: an automatic **Occam's razor**, analysed by David MacKay ("Bayesian Interpolation", 1992).

```python
--8<-- "books/machine-learning/ch12_bayes_linreg.py"
```

```
1. One weight, no intercept: y = w x + noise, prior w ~ N(0, 1), sigma^2 = 1
   after the point (2, 3): posterior mean 1.2000, variance 0.2000
   after 1 points: mean 1.2000, sd 0.4472
   after 2 points: mean 1.1667, sd 0.4082
   after 3 points: mean 1.2857, sd 0.3780
   after 4 points: mean 1.5000, sd 0.2500

2. Degree-5 polynomial features, 12 points on [-1, 1], noise sd 0.2, prior tau^2 = 1
   posterior mean = [ 0.1129  1.9395 -0.1835 -1.1717 -0.2256 -0.5759]
   ridge, lambda = sigma^2/tau^2 = 0.04: [ 0.1129  1.9395 -0.1835 -1.1717 -0.2256 -0.5759]
   predictive mean and sd (sd = sqrt(sigma^2 + phi^T S phi))
       x    mean     sd   true f(x)
    -1.5   3.977  2.778    0.978
    -1.0  -0.488  0.281   -0.141
    -0.5  -0.752  0.218   -0.997
     0.0   0.113  0.234    0.000
     0.5   0.858  0.242    0.997
     1.0  -0.104  0.418    0.141
     1.5  -6.861  4.276   -0.978

3. The evidence p(y | degree) for polynomial degrees 0 to 9
   degree   log evidence   train MSE   test MSE (posterior mean)
        0        -71.730      0.5143     0.6081
        1        -17.119      0.1312     0.2174
        2        -18.736      0.1312     0.2173
        3         -7.608      0.0296     0.0758
        4         -8.184      0.0291     0.0747
        5         -8.229      0.0316     0.0781
        6         -8.599      0.0312     0.0774
        7         -8.915      0.0313     0.0776
        8         -9.172      0.0312     0.0774
        9         -9.372      0.0304     0.0754
```

Three things to read off. The posterior mean and the ridge solution with $\lambda = \sigma^2/\tau^2 = 0.04$ agree to every
printed digit. The predictive standard deviation is about 0.22 to 0.42 inside the data range $[-1, 1]$ (barely above
the noise level 0.2 in the middle) and explodes to 2.8 and 4.3 at $x = \pm 1.5$, where a degree-5 polynomial is
unconstrained: the model knows it is extrapolating. And the log evidence jumps from $-71.7$ (degree 0) to $-17.1$
(degree 1) to $-7.6$ (degree 3, which can follow the bend of $\sin 3x$), then slowly declines for higher degrees, which
fit no better but pay for their extra flexibility. The test error, which the evidence never saw, agrees that degree 3
is where improvement stops.

## 12.5 Gaussian discriminant analysis (LDA/QDA)

Naive Bayes modelled words. For continuous features the natural generative model is the Gaussian: each class
generates its inputs from its own multivariate normal distribution.

**The model.** For class $k$ (out of $K$), $P(y = k) = \pi_k$ and $p(x \mid y = k) = N(x \mid \mu_k, \Sigma_k)$, the
multivariate Gaussian with mean $\mu_k$ and covariance $\Sigma_k$:

$$
N(x \mid \mu, \Sigma) = \frac{1}{(2\pi)^{d/2} |\Sigma|^{1/2}} \exp\Big(-\tfrac12 (x - \mu)^\top \Sigma^{-1} (x - \mu)\Big).
$$

**Learning.** Maximum likelihood gives what you would guess: $\hat\pi_k$ the fraction of class $k$, $\hat\mu_k$ the mean
of the class's points, $\hat\Sigma_k$ their covariance matrix. (The derivation is the multivariate version of the
Gaussian MLE of [Chapter 3](03-The-Math-Toolkit.md); see Bishop 2006, section 2.3.4.) If we assume all classes share one
covariance $\Sigma$, its MLE is the **pooled** covariance, the average of the class covariances weighted by class size.

**Shared covariance: a linear boundary (LDA).** Compare two classes through their log-odds. Write
$Q_k(x) = (x - \mu_k)^\top \Sigma^{-1} (x - \mu_k)$. With a shared $\Sigma$ the normalising constants cancel, and

$$
\begin{aligned}
\log\frac{P(y=1 \mid x)}{P(y=0 \mid x)} &= \log\frac{\pi_1}{\pi_0} - \tfrac12 Q_1(x) + \tfrac12 Q_0(x) \\
&= x^\top \Sigma^{-1}(\mu_1 - \mu_0) - \tfrac12\big(\mu_1^\top\Sigma^{-1}\mu_1 - \mu_0^\top\Sigma^{-1}\mu_0\big) + \log\frac{\pi_1}{\pi_0},
\end{aligned}
$$

because the terms $x^\top\Sigma^{-1}x$ in $Q_1$ and $Q_0$ are equal and cancel. The log-odds is linear in $x$:
$w \cdot x + b$ with $w = \Sigma^{-1}(\mu_1 - \mu_0)$. This is **linear discriminant analysis** (LDA). And since
$P(y = 1 \mid x) = \sigma(\text{log-odds})$, **LDA's posterior has exactly the form of logistic regression.** The two
models share a functional form but fit it differently: LDA estimates means and a covariance and plugs them in;
logistic regression fits $w$ and $b$ directly to the labels. If the Gaussian assumption holds, LDA uses the data more
efficiently. If it does not, logistic regression's fit is still the best linear rule for the log loss, while LDA's
plug-in can be biased. (Every Gaussian model with shared covariance gives logistic posteriors, but many non-Gaussian
models do too, so logistic regression assumes strictly less.)

**Separate covariances: a quadratic boundary (QDA).** If each class keeps its own $\Sigma_k$, the $x^\top\Sigma_k^{-1}x$
terms no longer cancel, and the log-odds contains $-\tfrac12 x^\top(\Sigma_1^{-1} - \Sigma_0^{-1})x$: the boundary is a
quadric (an ellipse, parabola or hyperbola in two dimensions). This is **quadratic discriminant analysis** (QDA). It is
more flexible but needs a covariance matrix per class, $d(d+1)/2$ numbers each, which is a lot of parameters for
small samples.

**History.** Ronald Fisher introduced the linear discriminant in "The Use of Multiple Measurements in Taxonomic
Problems" (1936), using measurements of iris flowers; he found it as the direction $w$ that maximises the ratio of the
spread between class means to the spread within classes, which turns out to be $\Sigma^{-1}(\mu_1 - \mu_0)$, the same
direction as the Gaussian model's.

The program fits LDA and QDA, compares LDA's weights with logistic regression's, and then runs the
generative-versus-discriminative race of 12.1 in ten dimensions.

```python
--8<-- "books/machine-learning/ch12_gda.py"
```

```
1. LDA on two Gaussian classes with a shared covariance (200 points each)
   estimated means [-0.04  -0.018], [1.509 1.07 ]
   pooled covariance [[0.927, 0.446], [0.446, 1.366]]
   log P(1|x)/P(0|x) = w.x + b with w = [1.528  0.2972], b = -1.2788
   logistic regression on the same data: w = [1.4534 0.3182], b = -1.2441
   true w = Sigma^-1 (mu1 - mu0) = [1.4474 0.0877], true b = -1.1294

2. QDA when the covariances differ (class 1 much wider)
   LDA: test accuracy 0.622
   QDA: test accuracy 0.856

3. Generative against discriminative in 10 dimensions, 20 repeats, test accuracy
   world A: features independent
     per class n   naive Bayes    LDA   logistic
               5         0.586    -     0.581
              10         0.622  0.592   0.583
              20         0.658  0.650   0.644
              50         0.680  0.673   0.673
             200         0.699  0.697   0.696
            1000         0.704  0.703   0.703
   world B: features share noise
     per class n   naive Bayes    LDA   logistic
               5         0.518    -     0.566
              10         0.538  0.616   0.607
              20         0.550  0.641   0.639
              50         0.557  0.688   0.686
             200         0.590  0.714   0.713
            1000         0.642  0.722   0.722
   In world B naive Bayes tends to the accuracy of feature 0 alone, Phi(0.3 / sqrt(1.25)) = 0.606;
   the Bayes classifier (linear here) scores Phi(Delta/2) = 0.716, where Delta is the Mahalanobis distance between the class means;
   one test set of 10000 points measures accuracy to about +-0.005.
```

**Part 1.** With 200 points per class, LDA's $w = (1.53, 0.30)$ and logistic regression's $(1.45, 0.32)$ are close to each
other, and both are a sampling error away from the truth $(1.45, 0.09)$: the same linear form, estimated two ways.

**Part 2.** When class 1 is ten times wider than class 0, the best boundary is a circle around class 0. LDA can only
draw a line (62 percent); QDA draws the circle (86 percent).

**Part 3, world A** (features independent, so naive Bayes is exactly right): with 10 points per class naive Bayes
scores 0.622 against 0.583 for logistic regression; LDA, which estimates a full covariance it does not need, is in
between. By 1000 points per class all three agree at 0.70. This is the first half of Ng and Jordan's result: the
correct generative model learns faster.

**World B** (one shared noise source in every feature; only feature 0 carries the class): here the independence
assumption is false, and the nine "useless" features are actually valuable, because subtracting them cancels the
shared noise. Logistic regression and LDA (whose full covariance captures the shared noise) learn this and approach
the Bayes accuracy 0.716; naive Bayes cannot represent it and is headed for 0.606, the accuracy of feature 0 alone. This
is the second half: a wrong generative model has a worse limit, which no amount of data repairs. (Naive Bayes scores
above 0.606 at $n = 1000$ only by luck of small random weights on the other features; with $10^5$ points per class it
settles at its limit.)

## 12.6 Gaussian processes from scratch

*Level: advanced.*

Bayesian linear regression put a prior on weights, and so, indirectly, on functions $f(x) = \phi(x)^\top w$. A
**Gaussian process** puts a prior directly on functions, with no weights at all, and lets the kernel of
[Chapter 9](09-Nearest-Neighbours-and-Kernels.md) say which functions are likely.

**Definition.** A Gaussian process (GP) is a random function $f$ such that for every finite set of inputs
$x_1, \dots, x_n$, the vector $(f(x_1), \dots, f(x_n))$ has a multivariate Gaussian distribution. It is determined by
a mean function (we take 0) and a **covariance function** $k(x, x') = \mathrm{Cov}(f(x), f(x'))$, which must be a positive
definite kernel (so that every covariance matrix it produces is valid). We write $f \sim \mathcal{GP}(0, k)$. With the RBF
kernel $k(x, x') = s^2 \exp(-(x - x')^2/(2\ell^2))$, function values at nearby inputs are strongly correlated and at
distant inputs nearly independent, so the random functions are smooth, varying on a horizontal **length scale** $\ell$
and with vertical size $s$.

**Drawing functions from the prior.** To sample $f$ on a grid, form the kernel matrix $K$ of the grid points, factor
it as $K = LL^\top$ (the **Cholesky factorisation**, $L$ lower triangular), draw a vector $z$ of independent standard
normals, and output $Lz$: its covariance is $L\,I\,L^\top = K$. The first part of the program does this.

The link with Bayesian linear regression is exact: a linear model with prior $w \sim N(0, \tau^2 I)$ gives
$\mathrm{Cov}(f(x), f(x')) = \tau^2 \phi(x)^\top\phi(x')$, a GP with a linear-in-features kernel. A GP with an RBF kernel
corresponds to infinitely many features (as in Chapter 9), which no weight-space model could store.

**Conditioning a Gaussian.** Everything about GP regression follows from one fact.

**Theorem.** If $\begin{pmatrix} a \\ b \end{pmatrix} \sim N\Big(0, \begin{pmatrix} A & C \\ C^\top & B \end{pmatrix}\Big)$
with $A$ invertible, then given $a$, the vector $b$ is Gaussian with

$$
E[b \mid a] = C^\top A^{-1} a, \qquad \mathrm{Cov}[b \mid a] = B - C^\top A^{-1} C.
$$

*Proof.* Let $z = b - C^\top A^{-1} a$. It is a linear function of $(a, b)$, so $(a, z)$ is jointly Gaussian, and
$\mathrm{Cov}(z, a) = C^\top - C^\top A^{-1} A = 0$. Jointly Gaussian and uncorrelated means independent, so knowing $a$
tells us nothing about $z$. Its distribution is $N(0, \mathrm{Cov}(z))$ with
$\mathrm{Cov}(z) = B - C^\top A^{-1} C - C^\top A^{-1} C + C^\top A^{-1} A A^{-1} C = B - C^\top A^{-1} C$. Since
$b = z + C^\top A^{-1} a$, given $a$ it is $z$ shifted by the known vector $C^\top A^{-1} a$. $\square$

**GP regression.** Observations are $y_i = f(x_i) + \varepsilon_i$ with noise variance $\sigma^2$. Then $y$ and the
function values $f_\ast$ at test inputs are jointly Gaussian with $A = K + \sigma^2 I$ (the kernel matrix of the training
inputs plus noise), $C = K_\ast$ (kernel values between training and test inputs) and $B = K_{\ast\ast}$. The theorem gives
the **posterior**:

$$
\bar f_\ast = K_\ast^\top (K + \sigma^2 I)^{-1} y, \qquad \mathrm{Cov}[f_\ast] = K_{\ast\ast} - K_\ast^\top (K + \sigma^2 I)^{-1} K_\ast.
$$

The posterior mean is exactly kernel ridge regression ([Chapter 9](09-Nearest-Neighbours-and-Kernels.md), 9.6) with
$\lambda = \sigma^2$: the dual weights $\alpha = (K + \sigma^2 I)^{-1}y$ are the same. The GP adds the variance, which is the
prior variance minus what the data explain: near training points it shrinks, far away it returns to the prior's $s^2$.

**By hand.** One noise-free observation $f(0) = 2$, RBF kernel with $\ell = 1$, $s = 1$. Then $A = k(0, 0) = 1$, and at a
test point $x$, $C = k(0, x) = e^{-x^2/2}$. The posterior mean is $2e^{-x^2/2}$ and the variance is $1 - e^{-x^2}$. At
$x = 1$: mean $2 \cdot 0.6065 = 1.2131$, variance $1 - 0.3679 = 0.6321$. At $x = 4$ the mean is almost 0 and the variance
almost 1: the observation tells us nothing that far away.

**Choosing the kernel: the marginal likelihood.** As in 12.4, the evidence is a Gaussian density:
$y \sim N(0, K + \sigma^2 I)$, so, with $K_y = K + \sigma^2 I$,

$$
\log p(y) = -\tfrac12\, y^\top K_y^{-1} y \;-\; \tfrac12 \log\det K_y \;-\; \tfrac{n}{2}\log 2\pi.
$$

The first term rewards fitting the data; the second penalises flexibility (a kernel that makes many different data sets
likely has a large determinant, its probability spread thin). Maximising the evidence over $\ell$, $s$ and $\sigma$ is how
GP hyperparameters are usually set, with gradients in practice and a grid in our program. All of it costs one Cholesky
factorisation of $K_y$, $O(n^3)$ time and $O(n^2)$ memory, which limits exact GPs to a few thousand points; sparse
approximations with a small set of **inducing points** (Edward Snelson and Zoubin Ghahramani, 2006; Michalis Titsias,
2009) scale them further.

```python
--8<-- "books/machine-learning/ch12_gp.py"
```

```
1. Three functions drawn from the GP prior (RBF kernel, length scale 1), at x = 0, 0.5, ..., 3
    [ 1.827  0.164 -0.882 -0.892 -0.177  0.665  1.349]
    [ 0.032 -0.215 -0.191  0.112  0.35   0.266  0.086]
    [ 0.704  0.389 -0.046 -0.723 -1.063 -0.688  0.094]
   prior correlation of f(0) with f(0.5), f(1), f(2), f(3): [0.882 0.607 0.135 0.011]

2. Hand example: one noise-free observation f(0) = 2, length scale 1
   x = 0: posterior mean 2.0000, variance 0.0000
   x = 1: posterior mean 1.2131, variance 0.6321
   x = 2: posterior mean 0.2707, variance 0.9817
   x = 4: posterior mean 0.0007, variance 1.0000

3. 15 noisy points from f(x) = sin(3x) on [0, 2], noise sd 0.2 (gap between 0.8 and 1.4)
   length   log marginal   data fit -y^T K^-1 y / 2   Occam term -log det(K) / 2
     0.05        -12.309                     -2.986                         4.461
     0.10         -9.422                     -2.458                         6.819
     0.20         -5.558                     -2.426                        10.652
     0.30         -3.539                     -2.619                        12.865
     0.50         -2.586                     -4.009                        15.207
     1.00        -15.501                    -19.371                        17.654
     2.00        -38.140                    -43.490                        19.134
   best length scale on a fine grid: 0.45
      x    mean    sd of f   true sin(3x)
   -0.50  -0.575     0.794    -0.997
    0.00  -0.182     0.163     0.000
    0.40   1.046     0.104     0.932
    1.10  -0.524     0.251    -0.158
    1.70  -0.779     0.097    -0.926
    2.50  -0.102     0.886     0.938
   kernel ridge regression with lambda = noise variance gives the same mean: max difference 8.9e-16
```

<figure class="mars-fig" markdown="0">
<svg viewBox="0 0 640 280" role="img" aria-label="Gaussian process regression on 15 noisy points from sin(3x) with a gap between 0.8 and 1.4. The posterior mean curve follows the points; a shaded band of plus or minus two standard deviations is narrow near the data, widens in the gap, and becomes very wide beyond the data at both ends. The true curve sin(3x) is dashed.">
  <polygon points="70.0,79.3 74.2,83.0 78.5,86.7 82.8,90.4 87.0,94.1 91.2,97.8 95.5,101.5 99.8,105.0 104.0,108.4 108.2,111.5 112.5,114.5 116.8,117.2 121.0,119.5 125.2,121.6 129.5,123.2 133.8,124.4 138.0,125.1 142.2,125.4 146.5,125.1 150.8,124.2 155.0,122.8 159.2,120.8 163.5,118.1 167.8,114.9 172.0,111.2 176.2,107.0 180.5,102.7 184.8,98.1 189.0,93.6 193.2,89.3 197.5,85.1 201.8,81.2 206.0,77.7 210.2,74.5 214.5,71.7 218.8,69.3 223.0,67.3 227.2,65.8 231.5,64.7 235.8,64.0 240.0,63.7 244.3,63.9 248.5,64.6 252.8,65.7 257.0,67.2 261.2,69.1 265.5,71.4 269.8,74.0 274.0,76.9 278.2,80.1 282.5,83.4 286.8,86.8 291.0,90.3 295.2,93.8 299.5,97.4 303.8,100.9 308.0,104.4 312.2,107.9 316.5,111.4 320.8,114.8 325.0,118.2 329.2,121.5 333.5,124.8 337.8,128.0 342.0,131.1 346.2,134.2 350.5,137.2 354.8,140.1 359.0,142.9 363.2,145.6 367.5,148.1 371.8,150.6 376.0,152.8 380.3,154.9 384.5,156.8 388.8,158.5 393.0,159.9 397.2,161.1 401.5,162.0 405.8,162.6 410.0,162.9 414.2,163.0 418.5,162.9 422.8,162.6 427.0,162.1 431.2,161.5 435.5,160.8 439.8,160.1 444.0,159.2 448.2,158.2 452.5,157.0 456.8,155.5 461.0,153.6 465.3,151.2 469.5,148.4 473.8,145.1 478.0,141.5 482.3,137.6 486.5,133.4 490.8,129.0 495.0,124.4 499.3,119.8 503.5,115.1 507.8,110.3 512.0,105.5 516.2,100.8 520.5,96.1 524.8,91.4 529.0,86.9 533.2,82.5 537.5,78.3 541.8,74.2 546.0,70.3 550.2,66.6 554.5,63.1 558.8,59.8 563.0,56.7 567.2,53.9 571.5,51.2 575.8,48.8 580.0,46.5 580.0,223.7 575.8,222.6 571.5,221.3 567.2,219.9 563.0,218.3 558.8,216.7 554.5,214.8 550.2,212.9 546.0,210.8 541.8,208.7 537.5,206.4 533.2,204.0 529.0,201.6 524.8,199.1 520.5,196.5 516.2,194.0 512.0,191.5 507.8,189.0 503.5,186.6 499.3,184.2 495.0,182.0 490.8,180.0 486.5,178.2 482.3,176.6 478.0,175.3 473.8,174.3 469.5,173.7 465.3,173.6 461.0,173.9 456.8,174.6 452.5,175.7 448.2,177.1 444.0,178.7 439.8,180.3 435.5,181.9 431.2,183.5 427.0,185.0 422.8,186.4 418.5,187.8 414.2,189.1 410.0,190.4 405.8,191.6 401.5,192.8 397.2,193.9 393.0,194.9 388.8,195.7 384.5,196.3 380.3,196.6 376.0,196.6 371.8,196.2 367.5,195.4 363.2,194.2 359.0,192.6 354.8,190.5 350.5,187.9 346.2,184.8 342.0,181.3 337.8,177.3 333.5,172.9 329.2,168.1 325.0,162.9 320.8,157.5 316.5,151.9 312.2,146.1 308.0,140.2 303.8,134.3 299.5,128.4 295.2,122.8 291.0,117.3 286.8,112.1 282.5,107.2 278.2,102.7 274.0,98.6 269.8,95.0 265.5,91.8 261.2,89.1 257.0,86.8 252.8,85.1 248.5,83.9 244.3,83.3 240.0,83.1 235.8,83.6 231.5,84.6 227.2,86.1 223.0,88.1 218.8,90.5 214.5,93.4 210.2,96.6 206.0,100.1 201.8,103.8 197.5,107.8 193.2,111.8 189.0,116.0 184.8,120.3 180.5,124.7 176.2,129.2 172.0,133.9 167.8,138.9 163.5,144.1 159.2,149.6 155.0,155.4 150.8,161.3 146.5,167.2 142.2,173.2 138.0,179.1 133.8,184.9 129.5,190.5 125.2,195.9 121.0,201.1 116.8,206.0 112.5,210.6 108.2,214.8 104.0,218.8 99.8,222.4 95.5,225.6 91.2,228.5 87.0,231.1 82.8,233.3 78.5,235.2 74.2,236.9 70.0,238.2" fill="#9cc9ea" fill-opacity="0.45" stroke="none"/>
  <polyline fill="none" stroke="#eea66f" stroke-width="3" points="70.0,158.7 74.2,159.9 78.5,161.0 82.8,161.9 87.0,162.6 91.2,163.2 95.5,163.5 99.8,163.7 104.0,163.6 108.2,163.2 112.5,162.5 116.8,161.6 121.0,160.3 125.2,158.7 129.5,156.9 133.8,154.6 138.0,152.1 142.2,149.3 146.5,146.2 150.8,142.8 155.0,139.1 159.2,135.2 163.5,131.1 167.8,126.9 172.0,122.6 176.2,118.1 180.5,113.7 184.8,109.2 189.0,104.8 193.2,100.5 197.5,96.4 201.8,92.5 206.0,88.9 210.2,85.5 214.5,82.5 218.8,79.9 223.0,77.7 227.2,75.9 231.5,74.6 235.8,73.8 240.0,73.4 244.3,73.6 248.5,74.3 252.8,75.4 257.0,77.0 261.2,79.1 265.5,81.6 269.8,84.5 274.0,87.8 278.2,91.4 282.5,95.3 286.8,99.4 291.0,103.8 295.2,108.3 299.5,112.9 303.8,117.6 308.0,122.3 312.2,127.0 316.5,131.6 320.8,136.2 325.0,140.6 329.2,144.8 333.5,148.8 337.8,152.6 342.0,156.2 346.2,159.5 350.5,162.5 354.8,165.3 359.0,167.7 363.2,169.9 367.5,171.8 371.8,173.4 376.0,174.7 380.3,175.8 384.5,176.5 388.8,177.1 393.0,177.4 397.2,177.5 401.5,177.4 405.8,177.1 410.0,176.7 414.2,176.1 418.5,175.3 422.8,174.5 427.0,173.5 431.2,172.5 435.5,171.4 439.8,170.2 444.0,169.0 448.2,167.7 452.5,166.4 456.8,165.1 461.0,163.7 465.3,162.4 469.5,161.1 473.8,159.7 478.0,158.4 482.3,157.1 486.5,155.8 490.8,154.5 495.0,153.2 499.3,152.0 503.5,150.8 507.8,149.6 512.0,148.5 516.2,147.4 520.5,146.3 524.8,145.3 529.0,144.2 533.2,143.3 537.5,142.3 541.8,141.4 546.0,140.6 550.2,139.8 554.5,139.0 558.8,138.2 563.0,137.5 567.2,136.9 571.5,136.2 575.8,135.7 580.0,135.1"/>
  <polyline fill="none" stroke="currentColor" stroke-width="1.3" stroke-dasharray="5 4" points="70.0,179.9 74.2,179.5 78.5,178.8 82.8,177.8 87.0,176.6 91.2,175.1 95.5,173.4 99.8,171.4 104.0,169.2 108.2,166.7 112.5,164.1 116.8,161.2 121.0,158.2 125.2,155.1 129.5,151.7 133.8,148.3 138.0,144.8 142.2,141.2 146.5,137.5 150.8,133.7 155.0,130.0 159.2,126.3 163.5,122.5 167.8,118.8 172.0,115.2 176.2,111.7 180.5,108.3 184.8,104.9 189.0,101.8 193.2,98.8 197.5,95.9 201.8,93.3 206.0,90.8 210.2,88.6 214.5,86.6 218.8,84.9 223.0,83.4 227.2,82.2 231.5,81.2 235.8,80.5 240.0,80.1 244.3,80.0 248.5,80.2 252.8,80.6 257.0,81.3 261.2,82.3 265.5,83.6 269.8,85.1 274.0,86.8 278.2,88.9 282.5,91.1 286.8,93.6 291.0,96.2 295.2,99.1 299.5,102.1 303.8,105.3 308.0,108.6 312.2,112.1 316.5,115.6 320.8,119.3 325.0,122.9 329.2,126.7 333.5,130.4 337.8,134.2 342.0,137.9 346.2,141.6 350.5,145.2 354.8,148.7 359.0,152.1 363.2,155.4 367.5,158.6 371.8,161.6 376.0,164.4 380.3,167.0 384.5,169.4 388.8,171.6 393.0,173.6 397.2,175.3 401.5,176.8 405.8,177.9 410.0,178.9 414.2,179.5 418.5,179.9 422.8,180.0 427.0,179.8 431.2,179.3 435.5,178.6 439.8,177.6 444.0,176.3 448.2,174.7 452.5,172.9 456.8,170.9 461.0,168.6 465.3,166.2 469.5,163.5 473.8,160.6 478.0,157.5 482.3,154.3 486.5,151.0 490.8,147.5 495.0,144.0 499.3,140.3 503.5,136.6 507.8,132.9 512.0,129.2 516.2,125.4 520.5,121.7 524.8,118.0 529.0,114.4 533.2,110.9 537.5,107.5 541.8,104.2 546.0,101.1 550.2,98.1 554.5,95.3 558.8,92.7 563.0,90.3 567.2,88.1 571.5,86.2 575.8,84.5 580.0,83.1"/>
  <g fill="#7ccf9a" stroke="currentColor" stroke-width="1">
    <circle cx="228.2" cy="71.4" r="4.5"/>
    <circle cx="255.3" cy="72.1" r="4.5"/>
    <circle cx="290.0" cy="98.2" r="4.5"/>
    <circle cx="159.1" cy="138.8" r="4.5"/>
    <circle cx="236.5" cy="73.7" r="4.5"/>
    <circle cx="286.6" cy="107.9" r="4.5"/>
    <circle cx="171.0" cy="121.4" r="4.5"/>
    <circle cx="185.3" cy="111.8" r="4.5"/>
    <circle cx="229.8" cy="74.1" r="4.5"/>
    <circle cx="466.7" cy="162.9" r="4.5"/>
    <circle cx="449.4" cy="169.7" r="4.5"/>
    <circle cx="448.9" cy="171.8" r="4.5"/>
    <circle cx="398.3" cy="182.4" r="4.5"/>
    <circle cx="468.4" cy="158.8" r="4.5"/>
    <circle cx="425.7" cy="165.8" r="4.5"/>
  </g>
  <g font-size="12" fill="currentColor" stroke="currentColor" text-anchor="middle">
    <line x1="70" y1="250" x2="580" y2="250" stroke-width="1"/>
    <line x1="70" y1="250" x2="70" y2="255"/><text x="70" y="270" stroke="none">-0.5</text>
    <line x1="155" y1="250" x2="155" y2="255"/><text x="155" y="270" stroke="none">0</text>
    <line x1="240" y1="250" x2="240" y2="255"/><text x="240" y="270" stroke="none">0.5</text>
    <line x1="325" y1="250" x2="325" y2="255"/><text x="325" y="270" stroke="none">1</text>
    <line x1="410" y1="250" x2="410" y2="255"/><text x="410" y="270" stroke="none">1.5</text>
    <line x1="495" y1="250" x2="495" y2="255"/><text x="495" y="270" stroke="none">2</text>
    <line x1="580" y1="250" x2="580" y2="255"/><text x="580" y="270" stroke="none">2.5</text>
  </g>
  <g font-size="12" fill="currentColor">
    <text x="80" y="24">orange: posterior mean</text>
    <text x="80" y="40">band: mean plus or minus 2 sd</text>
    <text x="80" y="56">dashed: true sin(3x)</text>
  </g>
</svg>
<figcaption>Gaussian process regression on 15 noisy points (green) with a gap between 0.8 and 1.4. The posterior
mean (orange) follows the data; the band of two standard deviations is narrow near data, wider in the gap, and widens
back towards the prior beyond both ends. The true function (dashed) stays inside the band.</figcaption>
</figure>

The marginal-likelihood table shows the trade-off. Short length scales fit the data easily (the data term is near its
best) but pay a large Occam penalty; long length scales are "simple" but cannot fit $\sin 3x$ and the data term
collapses ($-43.5$ at $\ell = 2$). The best length scale, 0.45, is chosen from the training data alone. The predictions
then behave as a careful statistician would: standard deviation 0.10 inside dense data, 0.25 in the gap at $x = 1.1$, and
about 0.8 to 0.9 beyond the data at $x = -0.5$ and $x = 2.5$, where the mean has drifted back towards 0. The truth at
$x = 2.5$ is $0.94$, far from the mean $-0.10$ but within about 1.2 standard deviations. A GP does not know the answer
away from its data, but it knows that it does not know.

**History.** The same mathematics was developed for geostatistics as **kriging**, named after the mining engineer
Danie Krige (1951) and formalised by Georges Matheron (1963), to interpolate ore grades between boreholes. It entered
machine learning in the 1990s (Christopher Williams and Carl Rasmussen, "Gaussian Processes for Regression", 1996); the
standard reference is Rasmussen and Williams, *Gaussian Processes for Machine Learning* (2006).

## 12.7 Sampling: Monte Carlo, MCMC (Metropolis-Hastings) from scratch

*Level: advanced.*

The beta-binomial model and Bayesian linear regression have posteriors with formulas, thanks to conjugacy. Most models
do not. Bayesian logistic regression, with a Gaussian prior on $w$, has posterior
$p(w \mid \text{data}) \propto \prod_i \sigma(y_i\, w \cdot x_i) \cdot e^{-\lVert w \rVert^2/(2\tau^2)}$ (labels $\pm1$),
and the normalising constant, an integral over all $w$, has no closed form. We can evaluate the posterior *up to a
constant* at any $w$, but we cannot integrate it. The way out is to draw samples from it.

### Monte Carlo integration

To compute an expectation $E[g(X)] = \int g(x) p(x)\,dx$, draw independent samples $x_1, \dots, x_n$ from $p$ and average:
$\hat\mu_n = \frac1n \sum_i g(x_i)$. It is **unbiased** ($E[\hat\mu_n] = E[g(X)]$), and its variance is $\mathrm{Var}(g(X))/n$,
so its error shrinks like $1/\sqrt n$ by the central limit theorem, *whatever the dimension of $x$*. Grid-based
integration in $d$ dimensions needs a number of points exponential in $d$ (the curse of
[Chapter 9](09-Nearest-Neighbours-and-Kernels.md)); Monte Carlo does not. The price is slowness: each extra digit of
accuracy costs 100 times as many samples. The first table of the program shows the $1/\sqrt n$ law for
$E[U^2] = 1/3$. When samples from $p$ are hard to get but samples from another distribution $q$ are easy, **importance
sampling** averages $g(x)p(x)/q(x)$ over samples from $q$ (exercise 12).

But how do we sample from a posterior known only up to a constant? We build a random walk that spends time in each
region in proportion to its probability.

### Markov chains and detailed balance

A **Markov chain** is a sequence $x_0, x_1, x_2, \dots$ where each $x_{t+1}$ is drawn from a **transition distribution**
$T(x_{t+1} \mid x_t)$ that depends only on the current state. A distribution $\pi$ is **stationary** for the chain if
starting from $\pi$ keeps you in $\pi$: $\int \pi(x)\, T(x' \mid x)\, dx = \pi(x')$. Under conditions called
**ergodicity** (roughly: every region can be reached, and the chain does not cycle periodically), the distribution of
$x_t$ converges to the stationary distribution from any start, and averages along the chain converge to expectations
under $\pi$. (The proofs are in any text on Markov chains; we state the result.)

**Detailed balance implies stationarity.** Suppose $\pi(x)\, T(x' \mid x) = \pi(x')\, T(x \mid x')$ for all $x, x'$:
the flow from $x$ to $x'$ equals the flow back. Then integrating over $x$,

$$
\int \pi(x)\, T(x' \mid x)\, dx = \int \pi(x')\, T(x \mid x')\, dx = \pi(x') \int T(x \mid x')\, dx = \pi(x'),
$$

because a transition distribution integrates to 1. $\square$ So to sample from $\pi$, it is enough to design a chain
with detailed balance for $\pi$.

### The Metropolis-Hastings algorithm

From the current state $x$, propose $x'$ from a **proposal distribution** $q(x' \mid x)$ (for example $x'$ equal to $x$ plus
Gaussian noise). Accept the move with probability

$$
A(x \to x') = \min\Big(1,\; \frac{\pi(x')\, q(x \mid x')}{\pi(x)\, q(x' \mid x)}\Big);
$$

otherwise stay at $x$ (and record $x$ again). For a symmetric proposal, $q(x' \mid x) = q(x \mid x')$, the ratio is just
$\pi(x')/\pi(x)$: always move uphill, move downhill with probability equal to the ratio. The crucial feature: **only the
ratio $\pi(x')/\pi(x)$ appears, so the unknown normalising constant cancels.** We need the posterior only up to a constant.

**Proof of detailed balance.** For $x' \ne x$ the transition density is $T(x' \mid x) = q(x' \mid x) A(x \to x')$. Then

$$
\pi(x)\, q(x' \mid x)\, A(x \to x') = \min\big(\pi(x) q(x' \mid x),\; \pi(x') q(x \mid x')\big),
$$

which is symmetric in $x$ and $x'$, so it also equals $\pi(x') q(x \mid x') A(x' \to x)$. (The rejected moves keep the chain
at $x$ and trivially balance.) $\square$

**History.** The algorithm comes from Nicholas Metropolis, Arianna Rosenbluth, Marshall Rosenbluth, Augusta Teller and
Edward Teller, "Equation of State Calculations by Fast Computing Machines" (1953), for simulating a system of
particles; W. Keith Hastings generalised it to asymmetric proposals in 1970. Stuart and Donald Geman's Gibbs sampler
(1984) and Alan Gelfand and Adrian Smith's 1990 paper brought MCMC into mainstream Bayesian statistics.

### Using it well

Successive samples of a chain are correlated, so $n$ samples are worth less than $n$ independent ones. The **effective
sample size** is $n_{\mathrm{eff}} = n / (1 + 2\sum_{k \ge 1} \rho_k)$, where $\rho_k$ is the correlation between samples $k$
steps apart; the Monte Carlo error of a chain average is about $\sqrt{\mathrm{Var}/n_{\mathrm{eff}}}$. The **step size** of
the proposal controls the correlation. Tiny steps are almost always accepted but crawl, so successive samples are nearly
equal. Huge steps leap into regions of low probability and are almost always rejected, so the chain sits still. The
best is in between. For random-walk Metropolis, Gareth Roberts, Andrew Gelman and Walter Gilks (1997) showed that in
high dimensions (for targets of a simple product form) the optimal acceptance rate is about 0.234; for one dimension the
recommended rate is about 0.44. Early samples depend on the starting point and are discarded (**burn-in**), and running
several chains from different starts and comparing them (the Gelman-Rubin diagnostic, 1992) checks that they have
converged to the same distribution.

```python
--8<-- "books/machine-learning/ch12_mcmc.py"
```

```
1. Monte Carlo: estimate E[X^2] = 1/3 for X uniform on [0, 1]
        n    estimate   error    predicted sd = sqrt(Var/n)
       10    0.44066   0.10733   0.09428
      100    0.32898   0.00435   0.02981
     1000    0.34315   0.00982   0.00943
    10000    0.33296   0.00038   0.00298
   100000    0.33292   0.00041   0.00094

2. Metropolis on the posterior Beta(9, 5) of 12.3 (7 heads in 10, Beta(2,2) prior)
   step   acceptance   mean (exact 0.6429)   sd (exact 0.1237)   effective samples of 20000
   0.01        0.977                0.5929              0.1257             39
   0.10        0.762                0.6458              0.1227           1899
   0.30        0.444                0.6432              0.1255           4335
   1.00        0.152                0.6393              0.1245           1607
   3.00        0.053                0.6515              0.1184            748
   exact: mean 9/14 = 0.6429, sd = 0.1237

3. Bayesian logistic regression, 2 weights, prior N(0, 2^2 I), 30 points
   acceptance 0.577; effective samples: 3250 and 2762 of 40000
   posterior mean [ 1.597 -0.74 ], posterior sd [0.557 0.571], correlation -0.219
   95% credible intervals: w0 in [0.64, 2.84], w1 in [-1.92, 0.31]  (true w = [ 1.5 -1. ])
   P(y = 1 | x = (1, 1)): averaged over the posterior 0.684; plug-in at the best sampled weights 0.680
```

<figure class="mars-fig" markdown="0">
<svg viewBox="0 0 640 260" role="img" aria-label="Bar chart of effective sample size out of 20000 Metropolis steps for five proposal step sizes: 39 for step 0.01 (acceptance 0.98), 1899 for 0.1 (0.76), 4335 for 0.3 (0.44), 1607 for 1 (0.15) and 748 for 3 (0.05). The middle step size is best.">
  <g font-size="12" fill="currentColor" stroke="currentColor" text-anchor="middle">
    <line x1="80" y1="200" x2="580" y2="200" stroke-width="1"/>
    <rect x="110" y="198.7" width="60" height="1.3" fill="#9cc9ea" stroke-width="1"/>
    <text x="140" y="192.7" stroke="none">39</text>
    <text x="140" y="218" stroke="none">step 0.01</text>
    <text x="140" y="234" stroke="none">accept 0.98</text>
    <rect x="210" y="134.3" width="60" height="65.7" fill="#9cc9ea" stroke-width="1"/>
    <text x="240" y="128.3" stroke="none">1899</text>
    <text x="240" y="218" stroke="none">step 0.1</text>
    <text x="240" y="234" stroke="none">accept 0.76</text>
    <rect x="310" y="50.0" width="60" height="150.0" fill="#eea66f" stroke-width="1"/>
    <text x="340" y="44.0" stroke="none">4335</text>
    <text x="340" y="218" stroke="none">step 0.3</text>
    <text x="340" y="234" stroke="none">accept 0.44</text>
    <rect x="410" y="144.4" width="60" height="55.6" fill="#9cc9ea" stroke-width="1"/>
    <text x="440" y="138.4" stroke="none">1607</text>
    <text x="440" y="218" stroke="none">step 1</text>
    <text x="440" y="234" stroke="none">accept 0.15</text>
    <rect x="510" y="174.1" width="60" height="25.9" fill="#9cc9ea" stroke-width="1"/>
    <text x="540" y="168.1" stroke="none">748</text>
    <text x="540" y="218" stroke="none">step 3</text>
    <text x="540" y="234" stroke="none">accept 0.05</text>
    <text x="330" y="254" stroke="none">effective samples out of 20000, Beta(9, 5) target</text>
  </g>
</svg>
<figcaption>Effective sample size of 20000 Metropolis steps on the Beta(9, 5) posterior for five step sizes. Tiny
steps are nearly always accepted but crawl; huge steps are nearly always rejected. The best step (orange) has
acceptance 0.44, the value theory recommends in one dimension.</figcaption>
</figure>

On the beta posterior, where the exact answer is known, every step size eventually gives roughly the right mean and
standard deviation, but the quality differs a hundredfold: with step 0.01 the 20000 samples are worth only 39 independent
ones, and the mean is off by 0.05; with step 0.3 (acceptance 0.444, close to the textbook 0.44) they are worth 4335.
For Bayesian logistic regression, which has no formula, the sampler returns the full posterior: means, standard
deviations, the correlation between the two weights, and 95 percent credible intervals that contain the true weights.
The prediction at $x = (1, 1)$ averaged over the posterior is 0.684. With 30 points the posterior is fairly concentrated,
so the plug-in prediction at the best sampled weights (0.680) is close; with less data, averaging over the posterior pulls
predictions towards 0.5 and is better calibrated than any single weight vector.

**Beyond random-walk Metropolis.** Random walks scale poorly with dimension. **Gibbs sampling** updates one variable at a
time from its exact conditional distribution (exercise 11). **Hamiltonian Monte Carlo** (Simon Duane, Anthony Kennedy,
Brian Pendleton and Duncan Roweth, 1987; introduced to statistics by Radford Neal) uses gradients of $\log\pi$ to make
long, directed proposals that are still accepted, and its adaptive version, the No-U-Turn Sampler (Matthew Hoffman and
Andrew Gelman, 2014), is the default in modern probabilistic programming languages. When sampling is too slow,
**variational inference** replaces the posterior by the closest member of a simple family, turning integration into
optimisation; [Chapter 20](20-Generative-Models.md) derives its objective, the ELBO.

**In practice.** scikit-learn has `MultinomialNB`, `LinearDiscriminantAnalysis`, `QuadraticDiscriminantAnalysis`,
`BayesianRidge` and `GaussianProcessRegressor`; probabilistic programming systems such as Stan (Bob Carpenter and
coauthors, 2017) and PyMC let you write a model and get MCMC samples from its posterior automatically.

## Check yourself

??? question "1. 40 percent of mail is spam. The word 'free' appears in 30 percent of spam and 2 percent of ham messages. What is P(spam | the message contains 'free')?"

    Bayes' rule: $P(\text{spam} \mid \text{free}) = \frac{0.4 \cdot 0.3}{0.4 \cdot 0.3 + 0.6 \cdot 0.02} = \frac{0.12}{0.132} = 0.909$.
    The word is fifteen times more common in spam, which turns prior odds of $0.4/0.6$ into posterior odds of 10.

??? question "2. Using the smoothed counts of 12.2, compute P(spam | 'meeting notes') by hand."

    In spam, "meeting" and "notes" never occur: each has $\hat\theta = 1/55$. In ham, "meeting" occurs 3 times and
    "notes" 2 times: $\hat\theta = 4/64$ and $3/64$. The log-odds is
    $\log\tfrac{6}{8} + \log\tfrac{1/55}{4/64} + \log\tfrac{1/55}{3/64} = -0.288 - 1.235 - 0.947 = -2.470$, so
    $P(\text{spam}) = 1/(1 + e^{2.470}) = 0.078$, the program's value.

??? question "3. Why can a naive Bayes classifier without smoothing be fooled by a single word, and why is smoothing with α = 1 equivalent to having seen every word once in each class?"

    Without smoothing, a word never seen in class $y$ has $\hat\theta_{y,w} = 0$, which makes the whole product zero and
    the class impossible, overriding all other words. Adding $\alpha = 1$ to every count is exactly what you would get
    by appending one extra "document" per class that contains every vocabulary word once, so no probability is zero;
    in Bayesian terms it is the posterior mean under a uniform Dirichlet prior.

??? question "4. Prior Beta(2, 2); you observe 7 heads in 10 flips. Give the posterior, the MLE, the MAP estimate and the posterior mean."

    Posterior $\mathrm{Beta}(2 + 7, 2 + 3) = \mathrm{Beta}(9, 5)$. MLE $7/10 = 0.7$. MAP $(9 - 1)/(9 + 5 - 2) = 8/12 = 0.667$.
    Posterior mean $9/14 = 0.643$. All three are pulled, in that order, increasingly towards the prior mean 0.5; the
    program's table shows the same numbers at $n = 10$.

??? question "5. Prove that the posterior mean of the beta-binomial model is a weighted average of the prior mean and the MLE, and find the weight."

    With $\lambda = (a+b)/(a+b+n)$: $\lambda \frac{a}{a+b} + (1 - \lambda)\frac{h}{n} = \frac{a}{a+b+n} + \frac{n}{a+b+n}\cdot\frac{h}{n} = \frac{a + h}{a + b + n}$.
    The prior counts as $a + b$ observations: with $\mathrm{Beta}(2,2)$ and 10 flips, the prior has weight $4/14$.

??? question "6. One-weight Bayesian regression y = wx + ε with prior w ~ N(0, 1) and σ² = 1, after the single point (2, 3). What is the predictive distribution of y at x = 1?"

    The posterior is $N(1.2, 0.2)$ (12.4). At $x = 1$, $E[y] = 1 \cdot 1.2 = 1.2$ and $\mathrm{Var}[y] = \sigma^2 + x^2 S = 1 + 0.2 = 1.2$.
    The noise dominates; the weight uncertainty adds 20 percent to the variance.

??? question "7. LDA in one dimension: class 0 is N(0, 1), class 1 is N(2, 1). Where is the decision threshold with equal priors, and with P(class 0) = 0.8?"

    The log-odds is $\frac{(\mu_1 - \mu_0)}{\sigma^2} x - \frac{\mu_1^2 - \mu_0^2}{2\sigma^2} + \log\frac{\pi_1}{\pi_0} = 2x - 2 + \log\frac{\pi_1}{\pi_0}$.
    With equal priors it is zero at $x = 1$, the midpoint. With $\pi_0 = 0.8$, $\log(0.2/0.8) = -1.386$, so the
    threshold is $x = 1 + 1.386/2 = 1.693$: the more common class gets more of the line.

??? question "8. GP with RBF kernel (ℓ = 1, s = 1) and one noise-free observation f(0) = 2. Derive the posterior mean and variance at x and evaluate them at x = 2. What changes if the observation has noise variance 1?"

    $A = 1$, $C = e^{-x^2/2}$, $B = 1$: mean $2e^{-x^2/2}$, variance $1 - e^{-x^2}$. At $x = 2$: mean $2e^{-2} = 0.2707$,
    variance $1 - e^{-4} = 0.9817$, as printed. With noise variance 1, $A = 1 + 1 = 2$, so the mean halves to
    $e^{-x^2/2}$ and the variance becomes $1 - e^{-x^2}/2$; even at $x = 0$ the variance is $0.5$, because a noisy reading
    of 2 only partly pins down $f(0)$.

??? question "9. Show that random-walk Metropolis with a symmetric proposal needs the target only up to a constant, and explain what goes wrong if you accept every proposal."

    The acceptance ratio is $\pi(x')/\pi(x)$; writing $\pi = \tilde\pi / Z$, the $Z$ cancels. If every proposal is
    accepted, the chain is a plain random walk whose distribution spreads out forever (for a Gaussian walk the variance
    grows linearly in $t$): it has no stationary distribution at all, and certainly not $\pi$. The rejections are what
    make the chain spend time in proportion to $\pi$.

??? question "10. Why is the effective sample size of a chain with lag-k autocorrelations ρ_k = r^k (0 < r < 1) equal to n(1 − r)/(1 + r)? Evaluate it for r = 0.9."

    $\sum_{k\ge1} r^k = r/(1 - r)$, so $1 + 2\sum_k \rho_k = 1 + 2r/(1-r) = (1 + r)/(1 - r)$ and
    $n_{\mathrm{eff}} = n(1 - r)/(1 + r)$. For $r = 0.9$, $n_{\mathrm{eff}} = n \cdot 0.1/1.9 = n/19$: 20000 steps are worth
    about 1053 independent samples.

??? question "11. Write the code: a Gibbs sampler for the bivariate normal with unit variances and correlation ρ = 0.9, alternating x | y ~ N(ρy, 1 − ρ²) and y | x ~ N(ρx, 1 − ρ²). Check the moments and the lag-1 autocorrelation."

    ```python
    import numpy as np

    rng = np.random.default_rng(0)
    rho, n = 0.9, 20000
    x = y = 0.0
    out = np.empty((n, 2))
    for t in range(n):
        x = rng.normal(rho * y, np.sqrt(1 - rho ** 2))   # x | y ~ N(rho y, 1 - rho^2)
        y = rng.normal(rho * x, np.sqrt(1 - rho ** 2))   # y | x ~ N(rho x, 1 - rho^2)
        out[t] = x, y
    s = out[1000:]
    print(f"means {np.round(s.mean(0), 3)}, variances {np.round(s.var(0), 3)}, "
          f"correlation {np.corrcoef(s.T)[0, 1]:.3f}")
    lag1 = np.corrcoef(s[:-1, 0], s[1:, 0])[0, 1]
    print(f"lag-1 autocorrelation of x: {lag1:.3f}  (theory rho^2 = {rho ** 2:.3f})")
    ```

    Output: means `[0.018 0.016]`, variances `[1.013 1.005]`, correlation `0.900`, lag-1 autocorrelation `0.812`
    against the theoretical $\rho^2 = 0.81$. Each sweep multiplies the dependence on the past by $\rho^2$ (the new $x$
    is $\rho^2$ times the old one plus fresh noise), so with $\rho = 0.9$ the chain mixes slowly: exercise 10 with
    $r = 0.81$ gives $n_{\mathrm{eff}} \approx n/9.5$. Gibbs samplers struggle with strongly correlated variables.

??? question "12. (Hard) Write the code: estimate the tiny probability P(Z > 4) for a standard normal Z by naive Monte Carlo and by importance sampling from N(4, 1), with 100000 samples each."

    ```python
    import numpy as np
    from math import erfc, sqrt

    rng = np.random.default_rng(0)
    n = 100000
    exact = 0.5 * erfc(4 / sqrt(2))
    z = rng.normal(0, 1, n)
    naive = np.mean(z > 4)
    x = rng.normal(4, 1, n)                        # proposal centred on the rare region
    w = np.exp(-0.5 * x ** 2) / np.exp(-0.5 * (x - 4) ** 2)   # weight p(x)/q(x)
    iss = np.mean(w * (x > 4))
    sd = np.std(w * (x > 4)) / np.sqrt(n)
    print(f"exact {exact:.4e}; naive MC {naive:.4e}; importance sampling {iss:.4e} (+- {sd:.1e})")
    ```

    Output: `exact 3.1671e-05; naive MC 3.0000e-05; importance sampling 3.1825e-05 (+- 2.1e-07)`. Naive Monte Carlo
    saw only 3 of 100000 samples beyond 4, so its relative error is about $1/\sqrt 3 \approx 58$ percent; importance
    sampling puts half its samples in the region that matters and reweights them by $p/q = e^{8 - 4x}$, reaching
    under 1 percent relative error with the same budget. The weights must be bounded where $g \ne 0$ for this to work;
    a proposal lighter-tailed than the target can give infinite variance.

## What you learned

- Generative models learn $P(y)$ and $p(x \mid y)$ and classify by Bayes' rule; discriminative models learn
  $P(y \mid x)$ directly. Correct generative models learn faster from little data; discriminative ones have the better
  limit when the generative assumptions are false.
- Naive Bayes trains by counting, is linear in word counts, needs Laplace smoothing to avoid zero probabilities, and
  must be computed in log space.
- With a conjugate prior the posterior stays in the prior's family: beta prior plus binomial data gives a beta
  posterior; MLE, MAP and the posterior mean differ with little data and merge with a lot.
- Bayesian linear regression has a Gaussian posterior with precision $\Phi^\top\Phi/\sigma^2 + I/\tau^2$; its mean is ridge
  regression with $\lambda = \sigma^2/\tau^2$, its predictive variance is noise plus parameter uncertainty, and its evidence
  chooses models.
- LDA (shared covariance) has linear log-odds of logistic form; QDA (separate covariances) has quadratic boundaries.
- A Gaussian process is a prior over functions given by a kernel; conditioning a joint Gaussian gives its posterior mean
  (kernel ridge regression) and variance, and the marginal likelihood balances fit against complexity.
- Monte Carlo error falls like $1/\sqrt n$ in any dimension; Metropolis-Hastings samples a posterior known only up to a
  constant, because its acceptance rule satisfies detailed balance, and its step size is tuned by the effective sample
  size.

**Next:** [Chapter 13](13-Clustering.md) removes the labels altogether: clustering finds groups in unlabelled data, and
its Gaussian mixtures, fitted by the EM algorithm, are the generative models of this chapter with the class hidden.

## Further reading

- C. Bishop, *Pattern Recognition and Machine Learning*, 2006: chapters 2 (distributions, conjugate priors), 3
  (Bayesian linear regression and the evidence), 4.2 (generative classifiers), 6.4 (Gaussian processes) and 11
  (sampling methods).
- K. Murphy, *Probabilistic Machine Learning: An Introduction*, 2022, and *Probabilistic Machine Learning: Advanced
  Topics*, 2023.
- T. Hastie, R. Tibshirani and J. Friedman, *The Elements of Statistical Learning*, 2nd ed., 2009, section 4.3 (LDA and
  QDA) and 6.6.3 (naive Bayes).
- A. Gelman, J. Carlin, H. Stern, D. Dunson, A. Vehtari and D. Rubin, *Bayesian Data Analysis*, 3rd ed., 2013.
- C. Rasmussen and C. Williams, *Gaussian Processes for Machine Learning*, 2006.
- D. MacKay, *Information Theory, Inference, and Learning Algorithms*, 2003; "Bayesian Interpolation", *Neural
  Computation*, 1992.
- A. Ng and M. Jordan, "On Discriminative vs. Generative Classifiers: A Comparison of Logistic Regression and Naive
  Bayes", NIPS 2001 (proceedings 2002).
- P. Domingos and M. Pazzani, "On the Optimality of the Simple Bayesian Classifier under Zero-One Loss", *Machine
  Learning*, 1997.
- M. Sahami, S. Dumais, D. Heckerman and E. Horvitz, "A Bayesian Approach to Filtering Junk E-Mail", AAAI Workshop on
  Learning for Text Categorization, 1998.
- R. A. Fisher, "The Use of Multiple Measurements in Taxonomic Problems", *Annals of Eugenics*, 1936.
- N. Metropolis, A. Rosenbluth, M. Rosenbluth, A. Teller and E. Teller, "Equation of State Calculations by Fast
  Computing Machines", *Journal of Chemical Physics*, 1953; W. K. Hastings, "Monte Carlo Sampling Methods Using Markov
  Chains and Their Applications", *Biometrika*, 1970.
- S. Geman and D. Geman, "Stochastic Relaxation, Gibbs Distributions, and the Bayesian Restoration of Images", *IEEE
  Transactions on Pattern Analysis and Machine Intelligence*, 1984.
- G. Roberts, A. Gelman and W. Gilks, "Weak Convergence and Optimal Scaling of Random Walk Metropolis Algorithms",
  *Annals of Applied Probability*, 1997.
- R. Neal, "MCMC Using Hamiltonian Dynamics", in *Handbook of Markov Chain Monte Carlo*, 2011; M. Hoffman and A. Gelman,
  "The No-U-Turn Sampler", *Journal of Machine Learning Research*, 2014.
- On this site: [Chapter 9](09-Nearest-Neighbours-and-Kernels.md) for kernels and kernel ridge regression,
  [Chapter 8](08-Overfitting-and-Regularization.md) for ridge regression, [Chapter 13](13-Clustering.md) for mixtures and
  EM, [Chapter 20](20-Generative-Models.md) for variational inference, the
  [Algorithms book, Chapter 21](../algorithms/21-Randomized-and-Amortized-Analysis.md) for the probability tools behind
  Monte Carlo, and [https://math.akadian.ca/books/](https://math.akadian.ca/books/) for probability and statistics.
