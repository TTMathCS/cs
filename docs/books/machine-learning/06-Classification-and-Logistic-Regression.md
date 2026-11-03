# 6. Classification and logistic regression

*Many questions have an answer that is a category, not a number: spam or not, which digit, which rock type, will
this customer leave. That is **classification**. In this chapter you will see why the line-fitting of Chapter 4 is
the wrong tool for it, build the oldest learning machine, the perceptron, and prove that it always finds a separating
line when one exists. Then you will build logistic regression, the model that turns a score into a probability:
derive its loss from likelihood, derive its gradient by hand, train it with gradient descent and with Newton's method,
extend it to many classes with softmax, bend its boundary with new features, and prove that its loss is convex. It
is the most widely used classifier in science and industry, and it is also exactly the last layer of most neural
networks.*

!!! abstract "In this chapter"
    **You will learn:**

    - why least squares on 0/1 labels gives a poor classifier
    - the perceptron, and Novikoff's theorem that it makes at most $(R/\gamma)^2$ mistakes on separable data (proved)
    - logistic regression: the sigmoid, log-odds, and the cross-entropy loss derived from maximum likelihood
    - the gradient $\tfrac1nX^\top(p-y)$ derived by hand and checked numerically, and training by gradient descent and Newton's method
    - softmax regression and one-vs-rest for many classes
    - decision boundaries, and curved boundaries from new features
    - generalised linear models, and a proof that the logistic loss is convex

    **You need:** [Chapter 3](03-The-Math-Toolkit.md) (gradients, the chain rule, likelihood),
    [Chapter 4](04-Linear-Regression.md) (the design matrix, least squares) and [Chapter 5](05-Optimization.md)
    (gradient descent, convexity, Newton's method).

    **Levels:** 6.1 to 6.4 are beginner to intermediate (6.2's proof is intermediate); 6.5 and 6.6 are intermediate;
    6.7 is advanced.

## 6.1 From numbers to classes

A **classifier** takes an input $x$ (a vector of features) and outputs a **class label** from a fixed finite set.
With two classes, called **binary classification**, we write the labels as $y\in\{0,1\}$ or $y\in\{-1,+1\}$, whichever
makes the formulas shorter; class 1 (or $+1$) is often called the **positive** class. Examples: an email filter (spam
or not), a medical test (disease or not), a rover's image software deciding whether a patch of ground is rock or sand.
NASA's Curiosity rover runs software called AEGIS that picks rock targets for its laser spectrometer from its own
camera images, because a round trip to Earth takes between about 8 and 48 minutes and the rover would otherwise wait
for the next day's commands; deciding "interesting target or not" from features of an image is a classification problem.

A classifier usually computes a **score** and compares it with a threshold. The simplest scores are linear:
$s(x)=w_0+w_1x_1+\dots+w_dx_d$. As in Chapter 4 we put a 1 in front of every input, $x=(1,x_1,\dots,x_d)$, so the score
is $w^\top x$ and the **bias** (or **intercept**) $w_0$ is just another weight.

### Why not just fit a line to the labels?

The obvious first try uses what we already have: code the labels as 0 and 1, fit linear regression, and say "class 1"
when the fitted value is at least $0.5$. It is not crazy, and on clean data it can work. Here are ten points
$x=0,1,\dots,9$, with class 1 for $x\ge5$. The fitted line crosses $0.5$ at exactly $x=4.5$, a perfect threshold.

Now add three more class-1 examples far to the right, at $x=30, 35, 40$. They are the *easiest* points in the data:
any sensible threshold classifies them correctly. But least squares penalises them: the line wants to predict 1 at
$x=40$, so it tilts flatter, and the crossing point moves right to $6.024$. Now $x=5$ and $x=6$ are misclassified.

```
1. least squares on 0/1 labels, classify by fitted value >= 0.5
   10 points 0..9:             threshold 4.500, errors 0
   plus x = 30, 35, 40 (class 1): threshold 6.024, errors 2
```

<figure class="mars-fig" markdown="0">
<svg viewBox="0 0 660 300" role="img" aria-label="Scatter of labels 0 and 1 against x from 0 to 40. Ten points at x 0 to 9, the first five at height 0 and the next five at height 1, plus three more at height 1 at x 30, 35 and 40. A dashed steep line fitted to the first ten points crosses the 0.5 level at x 4.5. A solid flatter line fitted to all thirteen crosses 0.5 at x 6.0, so the points at x 5 and 6 fall on the wrong side.">
  <g stroke="currentColor" stroke-width="1.2" fill="none">
    <line x1="50" y1="240" x2="620" y2="240"/>
    <line x1="50" y1="40" x2="50" y2="270"/>
    <line x1="50" y1="165" x2="620" y2="165" stroke-dasharray="2 4" stroke-opacity="0.6"/>
  </g>
  <g font-size="12" fill="currentColor">
    <text x="44" y="244" text-anchor="end">0</text>
    <text x="44" y="169" text-anchor="end">0.5</text>
    <text x="44" y="94" text-anchor="end">1</text>
    <text x="50" y="258" text-anchor="middle">0</text>
    <text x="190" y="258" text-anchor="middle">10</text>
    <text x="330" y="258" text-anchor="middle">20</text>
    <text x="470" y="258" text-anchor="middle">30</text>
    <text x="610" y="258" text-anchor="middle">40</text>
    <text x="335" y="288" text-anchor="middle">feature x</text>
  </g>
  <line x1="50" y1="267" x2="180" y2="56" stroke="#9cc9ea" stroke-width="2.5" stroke-dasharray="7 4"/>
  <line x1="50" y1="184" x2="610" y2="58" stroke="#eea66f" stroke-width="2.5"/>
  <g fill="#9cc9ea" stroke="currentColor">
    <rect x="46" y="236" width="8" height="8"/><rect x="60" y="236" width="8" height="8"/><rect x="74" y="236" width="8" height="8"/>
    <rect x="88" y="236" width="8" height="8"/><rect x="102" y="236" width="8" height="8"/>
  </g>
  <g fill="#7ccf9a" stroke="currentColor">
    <circle cx="120" cy="90" r="4.5"/><circle cx="134" cy="90" r="4.5"/><circle cx="148" cy="90" r="4.5"/>
    <circle cx="162" cy="90" r="4.5"/><circle cx="176" cy="90" r="4.5"/>
    <circle cx="470" cy="90" r="4.5"/><circle cx="540" cy="90" r="4.5"/><circle cx="610" cy="90" r="4.5"/>
  </g>
  <g stroke="currentColor" stroke-width="1.5">
    <line x1="113" y1="160" x2="113" y2="170"/>
    <line x1="134" y1="160" x2="134" y2="170"/>
  </g>
  <g font-size="12" fill="currentColor">
    <text x="200" y="60">dashed: fit to x = 0..9, crosses 0.5 at 4.5</text>
    <text x="300" y="152">solid: fit with x = 30, 35, 40 added, crosses 0.5 at 6.02</text>
  </g>
</svg>
<figcaption>Figure 6.1. Least squares on 0/1 labels. Three easy class-1 points far to the right drag the line flatter and move the 0.5 crossing from 4.5 to 6.02, misclassifying x = 5 and x = 6 (green circles left of the second tick).</figcaption>
</figure>

The deeper problem is that squared error is the wrong loss. It punishes a prediction of 3 for a class-1 point as
harshly as a prediction of $-1$, though the first is "very confidently right" and the second is wrong. And the fitted
values are not probabilities: they run below 0 and above 1. We want a model whose output is a number between 0 and
1 that we can read as "the probability of class 1", and a loss that punishes confident mistakes and leaves confident
correct answers alone. That is logistic regression (6.3). First, the oldest answer.

## 6.2 The perceptron

*Level: intermediate (the proof).*

Use labels $y\in\{-1,+1\}$ and predict $\hat y=\operatorname{sign}(w^\top x)$. The set of points where $w^\top x=0$
is a straight line in two dimensions, a plane in three, and a **hyperplane** in general: the **decision boundary**.
The classifier is right on example $(x_i,y_i)$ exactly when $y_iw^\top x_i>0$, since then the score and the label have
the same sign. The number $y_iw^\top x_i$ is the example's **functional margin**: positive means right, and larger
means more comfortably right.

Frank Rosenblatt, a psychologist at the Cornell Aeronautical Laboratory, described the **perceptron** in 1958 as a
simplified model of a neuron that learns from mistakes. The learning rule is one line. Go through the examples in
order; whenever one is misclassified (including landing exactly on the boundary), add it to $w$, signed by its label:

$$\text{if }y_iw^\top x_i\le0:\qquad w\leftarrow w+y_ix_i.$$

Why does that help? After the update, the example's margin is
$y_i(w+y_ix_i)^\top x_i=y_iw^\top x_i+\lVert x_i\rVert^2$: it went up by $\lVert x_i\rVert^2>0$. The update pulls the
boundary towards classifying that example correctly. Repeat passes over the data until a whole pass makes no mistake.

### A trace

Five points in the plane, two of class $+1$, written with the bias input first, $x=(1,x_1,x_2)$:

| point | $(x_1,x_2)$ | $y$ |
|---|---|---|
| A | $(-1,0)$ | $-1$ |
| B | $(-1,-3)$ | $+1$ |
| C | $(-3,-3)$ | $-1$ |
| D | $(-3,-2)$ | $-1$ |
| E | $(3,-2)$ | $+1$ |

Start from $w=(0,0,0)$. The program prints every update:

| update | epoch | example | margin before | $w$ after |
|---|---|---|---|---|
| 1 | 1 | A, $y=-1$ | $0$ | $(-1,1,0)$ |
| 2 | 1 | B, $y=+1$ | $-1-1+0=-2$ | $(0,0,-3)$ |
| 3 | 1 | C, $y=-1$ | $-(0+0+9)=-9$ | $(-1,3,0)$ |
| 4 | 2 | B, $y=+1$ | $-1-3+0=-4$ | $(0,2,-3)$ |
| 5 | 2 | C, $y=-1$ | $-(0-6+9)=-3$ | $(-1,5,0)$ |
| 6 | 3 | B, $y=+1$ | $-1-5+0=-6$ | $(0,4,-3)$ |

In epoch 1, after update 3, D has margin $-(-1-9+0)=10$ and E has $-1+9+0=8$, both fine. Epoch 4 makes no mistakes:
the final $w=(0,4,-3)$ gives margins $4, 5, 3, 6, 18$ for A to E, all positive. The boundary is $4x_1-3x_2=0$. Points
B and C are close together with opposite labels, so the boundary has to squeeze between them, which is why the
algorithm bounces between them for three epochs.

```python
--8<-- "books/machine-learning/ch06_perceptron.py"
```

Output:

```
1. least squares on 0/1 labels, classify by fitted value >= 0.5
   10 points 0..9:             threshold 4.500, errors 0
   plus x = 30, 35, 40 (class 1): threshold 6.024, errors 2

2. perceptron on five points (first coordinate is the bias input 1)
   epoch 1  x=[-1.  0.]  y=-1  ->  w = [-1.  1.  0.]
   epoch 1  x=[-1. -3.]  y=+1  ->  w = [ 0.  0. -3.]
   epoch 1  x=[-3. -3.]  y=-1  ->  w = [-1.  3.  0.]
   epoch 2  x=[-1. -3.]  y=+1  ->  w = [ 0.  2. -3.]
   epoch 2  x=[-3. -3.]  y=-1  ->  w = [-1.  5.  0.]
   epoch 3  x=[-1. -3.]  y=+1  ->  w = [ 0.  4. -3.]
   converged after 6 mistakes, 4 epochs; w = [ 0.  4. -3.]
   margins y * w.x = [ 4.  5.  3.  6. 18.]

3. mistakes against Novikoff's bound (R / gamma)^2
   gamma_min   n     mistakes   bound
   0.5019    300         3           69
   0.2009    300        14          437
   0.0669    300        17         3939

4. overlapping classes: 2104 mistakes in 50 epochs, still not clean; final training accuracy 0.825
```

### The convergence theorem

Does the bouncing always stop? If no line separates the classes, it cannot: some example is always wrong. But if one
does, it must stop, and quickly when the separation is wide.

The data are **linearly separable with margin $\gamma>0$** if there is a unit vector $u$ ($\lVert u\rVert=1$) with
$y_iu^\top x_i\ge\gamma$ for every example. Because $u$ has length 1, $y_iu^\top x_i$ is the actual distance from $x_i$
to the hyperplane $u^\top x=0$ (the **geometric margin**), so $\gamma$ is the width of an empty corridor around the
boundary. Let $R=\max_i\lVert x_i\rVert$ be the radius of the data.

**Theorem 6.1 (Novikoff 1962).** On data separable with margin $\gamma$ and radius $R$, the perceptron started at
$w=0$ makes at most $(R/\gamma)^2$ updates, whatever the order of the examples.

*Proof.* Let $w_t$ be the weight vector after $t$ updates, with $w_0=0$. We track two numbers.

*Alignment with $u$ grows fast.* Update $t+1$ happens on some example with $y_iw_t^\top x_i\le0$, and gives
$u^\top w_{t+1}=u^\top w_t+y_iu^\top x_i\ge u^\top w_t+\gamma$. By induction, $u^\top w_t\ge t\gamma$.

*Length grows slowly.* For the same update,
$\lVert w_{t+1}\rVert^2=\lVert w_t\rVert^2+2y_iw_t^\top x_i+\lVert x_i\rVert^2\le\lVert w_t\rVert^2+R^2$, because the
middle term is $\le0$ (that is why we updated) and $y_i^2=1$. By induction, $\lVert w_t\rVert^2\le tR^2$.

Now combine them with Cauchy-Schwarz, $u^\top w_t\le\lVert u\rVert\,\lVert w_t\rVert=\lVert w_t\rVert$:

$$t\gamma\le u^\top w_t\le\lVert w_t\rVert\le\sqrt t\,R.$$

Dividing by $\sqrt t\,\gamma$ gives $\sqrt t\le R/\gamma$, so $t\le(R/\gamma)^2$. $\square$

The proof is a race: each mistake moves $w$ a distance $\gamma$ further along $u$, but its length grows only like the
square root of the number of mistakes. Steady progress in one direction with sub-linear growth in size means the
angle between $w$ and $u$ keeps closing, and the cosine cannot exceed 1. Remarkably, the bound depends on neither the
number of examples nor the dimension, only on the geometry.

Check it on the trace. Any separating unit vector gives a valid $(R/\gamma)^2$. Take $u=w/\lVert w\rVert$ for the final
$w=(0,4,-3)$, so $\lVert w\rVert=5$: the margins divided by 5 are $0.8,1,0.6,1.2,3.6$, so $\gamma=0.6$. The largest
$\lVert x_i\rVert$ is C's, $\sqrt{1+9+9}=\sqrt{19}$ (the bias input counts). The bound is $19/0.36\approx52.8$, and the
perceptron used 6 updates. The third block of the program measures this on 300 random points, after throwing away all points within
$\gamma$ of a fixed separating line, for three values of $\gamma$. The bound always holds and grows like $1/\gamma^2$,
while the actual count, 3, 14 and 17, is far below it. The bound is about the worst order of presentation, and random
data are kinder.

The fourth block shows the other side: with overlapping classes, 50 epochs bring 2104 updates and the weights never
settle. The final weight vector, whichever example happened to be last, gets 82.5 percent training accuracy. Remedies
exist: the **pocket algorithm** (Gallant 1990) keeps the best weights seen so far, and the **averaged perceptron**
(Freund and Schapire 1999) predicts with the average of all weight vectors, which is stable and works well. But the
real fix is a loss that measures *how* wrong a prediction is, smoothly, so that gradient descent can minimise it.

### A short history

Rosenblatt's 1958 paper in *Psychological Review* and the custom-built Mark I Perceptron, which learned to recognise
simple shapes from a 20 by 20 grid of photocells, drew much public attention. In 1969 Marvin Minsky and Seymour
Papert published *Perceptrons*, a careful mathematical study proving what a single layer of such units cannot
compute: for example, it cannot tell whether the number of black pixels is odd or even, and the two-input case of
that is XOR (6.6). Interest in neural networks fell sharply in the 1970s. Learning rules for several layers,
which escape these limits, became widely known with backpropagation (Rumelhart, Hinton and Williams 1986), the subject
of [Chapter 15](15-Neural-Networks-and-Backpropagation.md).

## 6.3 Logistic regression

We want a model that outputs a probability. Keep the linear score $z=w^\top x$, which can be any real number, and
squash it into $(0,1)$ with the **sigmoid** (or **logistic**) function:

$$\sigma(z)=\frac1{1+e^{-z}}.$$

<figure class="mars-fig" markdown="0">
<svg viewBox="0 0 660 300" role="img" aria-label="The sigmoid curve rising smoothly from near 0 at z equals minus 6 to near 1 at z equals 6, passing through 0.5 at z equals 0. Marked points: sigma of minus 2 is 0.12, sigma of 0 is 0.5, sigma of 2 is 0.88.">
  <g stroke="currentColor" stroke-width="1.2" fill="none">
    <line x1="60" y1="250" x2="610" y2="250"/>
    <line x1="330" y1="40" x2="330" y2="260"/>
    <line x1="60" y1="50" x2="610" y2="50" stroke-dasharray="2 4" stroke-opacity="0.6"/>
    <line x1="60" y1="150" x2="610" y2="150" stroke-dasharray="2 4" stroke-opacity="0.6"/>
  </g>
  <polyline points="60,250 71,249 82,249 94,249 105,249 116,248 128,248 139,247 150,246 161,245 172,244 184,243 195,241 206,238 218,235 229,231 240,226 251,220 262,214 274,205 285,196 296,186 308,174 319,162 330,150 341,138 352,126 364,114 375,104 386,95 398,86 409,80 420,74 431,69 442,65 454,62 465,59 476,57 488,56 499,55 510,54 521,53 532,52 544,52 555,51 566,51 578,51 589,51 600,50" fill="none" stroke="#9cc9ea" stroke-width="3"/>
  <circle cx="240" cy="226" r="5" fill="#eea66f" stroke="currentColor"/>
  <circle cx="330" cy="150" r="5" fill="#eea66f" stroke="currentColor"/>
  <circle cx="420" cy="74" r="5" fill="#eea66f" stroke="currentColor"/>
  <g font-size="12" fill="currentColor">
    <text x="322" y="46" text-anchor="end">1</text>
    <text x="322" y="146" text-anchor="end">0.5</text>
    <text x="322" y="246" text-anchor="end">0</text>
    <text x="60" y="268" text-anchor="middle">-6</text>
    <text x="240" y="268" text-anchor="middle">-2</text>
    <text x="420" y="268" text-anchor="middle">2</text>
    <text x="600" y="268" text-anchor="middle">6</text>
    <text x="335" y="290" text-anchor="middle">score z = w·x (the log-odds)</text>
    <text x="232" y="214" text-anchor="end">σ(−2) = 0.12</text>
    <text x="340" y="170">σ(0) = 0.5</text>
    <text x="430" y="92">σ(2) = 0.88</text>
    <text x="70" y="40">probability of class 1</text>
  </g>
</svg>
<figcaption>Figure 6.2. The sigmoid turns any score into a probability. It is steepest at z = 0, where its slope is σ(1 − σ) = 1/4, and it flattens towards 0 and 1, so very large scores change the probability very little.</figcaption>
</figure>

The **logistic regression** model is

$$P(y=1\mid x)=\sigma(w^\top x),\qquad P(y=0\mid x)=1-\sigma(w^\top x)=\sigma(-w^\top x).$$

The last equality is a useful identity: $1-\frac1{1+e^{-z}}=\frac{e^{-z}}{1+e^{-z}}=\frac1{e^{z}+1}=\sigma(-z)$.

### Log-odds

What does the score mean? The **odds** of an event with probability $p$ are $p/(1-p)$: odds of 3 mean "three times as
likely to happen as not", $p=0.75$. Solve $p=\sigma(z)$ for $z$: $1/p=1+e^{-z}$, so $e^{-z}=(1-p)/p$, and

$$z=\ln\frac p{1-p}.$$

This function of $p$ is called the **logit**; it is the inverse of the sigmoid. So logistic regression says: **the
log-odds of class 1 are a linear function of the features**. That makes the weights readable. Increasing feature $j$
by one unit, with the others fixed, adds $w_j$ to the log-odds, which multiplies the odds by $e^{w_j}$. In the
program's model below, $w_1=1.93$, so each unit of $x_1$ multiplies the odds of class 1 by $e^{1.93}\approx6.9$. This is
why logistic regression is the standard model in medicine and the social sciences, where "odds ratios" are reported.

### The loss, from likelihood

Chapter 3 introduced **maximum likelihood**: choose the parameters under which the observed data are most probable.
For one example the model gives probability $p_i=\sigma(w^\top x_i)$ to $y_i=1$ and $1-p_i$ to $y_i=0$. A compact way to
write "the probability of what actually happened" is

$$P(y_i\mid x_i;w)=p_i^{\,y_i}(1-p_i)^{1-y_i},$$

since the exponents switch on the right factor: if $y_i=1$ it is $p_i$, if $y_i=0$ it is $1-p_i$. This is the
**Bernoulli** distribution. Assuming the examples are independent, the likelihood of all the data is the product over
$i$, and the log turns it into a sum. Maximising the log-likelihood is the same as minimising its negative divided by
$n$, the **cross-entropy loss** (also called **log loss**):

$$J(w)=-\frac1n\sum_{i=1}^n\Bigl[y_i\ln p_i+(1-y_i)\ln(1-p_i)\Bigr],\qquad p_i=\sigma(w^\top x_i).$$

Chapter 3's information theory explains the name: it is the cross-entropy between the true label distribution (all
mass on $y_i$) and the model's distribution $(1-p_i,p_i)$.

Look at one example. If $y=1$, its loss is $-\ln p$: zero when the model is certain and right ($p=1$), $\ln2\approx0.69$
at $p=0.5$, and growing without bound as $p\to0$, a confident mistake. This is the behaviour we asked for in 6.1. For
the point $x=(1,0.5)$, the trained model of 6.4 gives score $z=1.088$ and $p=0.748$. If the true label is 1, the loss is
$-\ln0.748=0.290$; if it is 0, the loss is $-\ln0.252=1.378$.

In terms of the score $z=w^\top x$, using $\ln\sigma(z)=-\ln(1+e^{-z})$ and $\ln(1-\sigma(z))=-z-\ln(1+e^{-z})$, the
loss of one example simplifies to

$$\ell(z,y)=\ln(1+e^{z})-yz.$$

This form is what the code uses, through `np.logaddexp(0, z)`, which computes $\ln(e^0+e^z)$ without overflow for
large $z$. With labels $\pm1$ the same loss is $\ln(1+e^{-yz})$, a smooth version of the perceptron's "penalise when
$yz\le0$"; you will meet it again next to the hinge loss in [Chapter 10](10-Support-Vector-Machines.md).

## 6.4 The gradient, and training from scratch

To train by gradient descent we need $\nabla J$. Two facts do all the work.

**The sigmoid's derivative.** Differentiate $\sigma(z)=(1+e^{-z})^{-1}$:

$$\sigma'(z)=\frac{e^{-z}}{(1+e^{-z})^2}=\frac1{1+e^{-z}}\cdot\frac{e^{-z}}{1+e^{-z}}=\sigma(z)\bigl(1-\sigma(z)\bigr).$$

**The loss's derivative in $z$.** From $\ell(z,y)=\ln(1+e^z)-yz$:

$$\frac{\partial\ell}{\partial z}=\frac{e^z}{1+e^z}-y=\sigma(z)-y=p-y.$$

That is: *prediction minus label*. Now the chain rule, with $z=w^\top x$ so that $\partial z/\partial w_j=x_j$, gives
$\partial\ell/\partial w_j=(p-y)x_j$. Averaging over the examples and writing it with the design matrix $X$ (one example
per row) and the vectors $p$ and $y$:

$$\nabla J(w)=\frac1n\sum_{i=1}^n(p_i-y_i)\,x_i=\frac1nX^\top(p-y).$$

Compare Chapter 4: the gradient of the mean squared error $\frac1n\lVert Xw-y\rVert^2$ is $\frac2nX^\top(Xw-y)$, also "features
times (prediction minus target)". The only change is that the prediction passes through $\sigma$. This is no
coincidence; 6.7 explains it.

A tiny example by hand: one point $x=(1,2)$ with $y=1$ and $w=0$. Then $z=0$, $p=0.5$, and the gradient is
$(0.5-1)(1,2)=(-0.5,-1)$. A gradient step with $\alpha=1$ gives $w=(0.5,1)$, so $z=0.5+2=2.5$ and $p=\sigma(2.5)=0.924$:
the model moved strongly towards the right answer.

### Checking the gradient

A derived gradient should always be checked numerically before it is trusted (Chapter 3): perturb each weight by
$\pm h$ and compare the slope $\bigl(J(w+he_j)-J(w-he_j)\bigr)/(2h)$ with the formula. The program does this on 200
synthetic points in two clusters; the two agree to $7\times10^{-11}$.

### Training

The loss is convex (6.7) and $L$-smooth with $L$ at most the largest eigenvalue of $\frac1{4n}X^\top X$, because the
Hessian is $\frac1nX^\top SX$ with $S$ diagonal with entries $p_i(1-p_i)\le\frac14$. So Chapter 5's theory applies:
gradient descent with step $1/L$ is guaranteed to converge.

```python
--8<-- "books/machine-learning/ch06_logistic.py"
```

Output:

```
1. gradient check at w = (0.1, -0.2, 0.3)
   formula   [ 0.07033661 -0.54284996 -0.23843396]
   numerical [ 0.07033661 -0.54284996 -0.23843396]
   max difference 6.9e-11

2. training on 200 points; gradient descent with step 1/L = 1.501
   GD step    1  loss 0.387454  accuracy 0.865
   GD step   10  loss 0.272117  accuracy 0.900
   GD step  100  loss 0.256650  accuracy 0.910
   GD step 1000  loss 0.256648  accuracy 0.910
   GD step 2000  loss 0.256648  accuracy 0.910
   Newton step 1  loss 0.3385807201  |grad| 1.5e-01
   Newton step 2  loss 0.2734632788  |grad| 5.0e-02
   Newton step 3  loss 0.2581796628  |grad| 1.2e-02
   Newton step 4  loss 0.2566701442  |grad| 1.4e-03
   Newton step 5  loss 0.2566480041  |grad| 2.3e-05
   Newton step 6  loss 0.2566479981  |grad| 6.4e-09
   Newton step 7  loss 0.2566479981  |grad| 5.0e-16
   GD weights     [-1.52766393  1.92863905  1.37441917]
   Newton weights [-1.52766393  1.92863905  1.37441917]
   P(y=1 | x=(1, 0.5)) = 0.7480

3. separable data: gradient descent with step 1
   step     10  loss 5.09e-02  slope w1 = 1.969
   step    100  loss 8.57e-03  slope w1 = 3.675
   step   1000  loss 9.76e-04  slope w1 = 5.835
   step  10000  loss 9.97e-05  slope w1 = 8.115
   step 100000  loss 1.00e-05  slope w1 = 10.415

4. three classes, 300 points
   softmax regression: loss 0.0919, accuracy 0.973
   one-vs-rest:        accuracy 0.973
   at the point (0, 0): softmax probabilities [0.53  0.102 0.368], one-vs-rest scores [0.074 0.018 0.05 ] (sum 0.142)

5. inside a circle or not (400 points)
   features x1, x2:               accuracy 0.755
   features x1, x2, x1^2, x2^2, x1*x2: accuracy 1.000
   (always guessing 'outside' scores 0.755)

6. smallest Hessian eigenvalue over 1000 random w: 1.18e-06 (never negative)

7. Poisson regression by Newton (= IRLS), true coefficients (0.5, 1.2)
   step 1  b = (0.82688, 1.11383)
   step 2  b = (0.53116, 1.19997)
   step 3  b = (0.48355, 1.22076)
   step 4  b = (0.48262, 1.22126)
   step 5  b = (0.48261, 1.22126)
   step 6  b = (0.48261, 1.22126)
   standard errors (0.025, 0.017)
```

Gradient descent is within $2\times10^{-6}$ of the minimum loss $0.256648$ after 100 steps here. Newton's method (Chapter 5.6), with
Hessian $H=\frac1nX^\top SX$, reaches it to all printed digits in 6 steps, and the gradient norm shows the quadratic
convergence: $1.4\times10^{-3}$, $2.3\times10^{-5}$, $6.4\times10^{-9}$, $5\times10^{-16}$, the exponent roughly doubling.
Each Newton step solves the weighted least-squares problem with weights $S$ and a "working response", so statisticians
call it **iteratively reweighted least squares** (IRLS); it is how logistic regression has been fitted in statistics
packages for decades. With three weights the Hessian is a $3\times3$ matrix and costs nothing; with a million sparse
text features one uses L-BFGS or SGD instead. The two methods give identical weights, as they must for a strictly
convex loss with a unique minimum.

The training accuracy of 91 percent is not the whole story: this model is evaluated honestly, on held-out data, with
the tools of [Chapter 7](07-Evaluating-Models.md).

### Separable data: the weights run away

If a line separates the classes perfectly, the logistic loss has **no minimum**. Take any separating $w$; then $cw$ for
larger and larger $c$ makes every score larger in the right direction, every $p_i$ closer to its label, and the loss
closer to 0, without ever reaching it. The third block shows this on six points on a line, $-3,\dots,3$, with the
negative ones in class 0. After 10, 100, 1000, 10000 and 100000 steps, the slope is 1.97, 3.68, 5.84, 8.12 and 10.42,
and the loss falls by a factor of ten for each factor of ten in steps. The slope grows by about $2.3\approx\ln10$ for each
factor of ten, that is like the logarithm of the number of steps. Soudry et al. (2018) proved that on separable data
gradient descent on the logistic loss grows the weights like $\log t$ and that their *direction* converges to the
maximum-margin separator of [Chapter 10](10-Support-Vector-Machines.md), an example of the **implicit bias** of an
optimiser. In practice one stops the runaway with a penalty $\lambda\lVert w\rVert^2$ ([Chapter
8](08-Overfitting-and-Regularization.md)), which makes the minimum exist again.

## 6.5 Many classes: softmax regression and one-vs-rest

With $K$ classes, give each class $k$ its own weight vector $w_k$ and score $z_k=w_k^\top x$. Turn the $K$ scores into
$K$ probabilities that are positive and add to 1 with the **softmax** function:

$$P(y=k\mid x)=\operatorname{softmax}(z)_k=\frac{e^{z_k}}{\sum_{j=1}^Ke^{z_j}}.$$

Exponentiating makes everything positive and dividing by the sum normalises; the largest score gets the largest
probability, and "soft" refers to it being a smooth version of picking the maximum. For scores $(2,1,0)$:
$e^2=7.389$, $e^1=2.718$, $e^0=1$, total $11.107$, so the probabilities are $0.665, 0.245, 0.090$.

Three practical points. First, adding the same number $c$ to every score multiplies numerator and denominator by
$e^c$ and changes nothing. The code uses this to subtract the largest score before exponentiating, which prevents
overflow (try $e^{1000}$). Second, the same fact means the weights are not unique (adding a vector $v$ to every $w_k$
changes no probability), which is harmless for gradient descent and is often fixed by a small penalty. Third, with
$K=2$, softmax is exactly logistic regression:
$\frac{e^{z_1}}{e^{z_0}+e^{z_1}}=\frac1{1+e^{-(z_1-z_0)}}=\sigma\bigl((w_1-w_0)^\top x\bigr)$.

### The loss and its gradient

Write the label as a **one-hot** vector $y\in\{0,1\}^K$ with a single 1 in the true class's position. The likelihood of
one example is the probability of its true class, and the negative log-likelihood is the **categorical
cross-entropy**:

$$\ell=-\sum_{k=1}^Ky_k\ln p_k=-z_c+\ln\sum_je^{z_j}\qquad\text{where }c\text{ is the true class}.$$

Differentiate with respect to the score $z_k$. The first term gives $-1$ if $k=c$ and 0 otherwise, which is $-y_k$; the
second gives $e^{z_k}/\sum_je^{z_j}=p_k$. So

$$\frac{\partial\ell}{\partial z_k}=p_k-y_k,$$

*prediction minus label* once again, now as vectors. Since $z_k=w_k^\top x$, the gradient for the weight matrix $W$
(columns $w_1,\dots,w_K$) over all examples is $\frac1nX^\top(P-Y)$, where $P$ and $Y$ are $n\times K$ matrices of
predicted probabilities and one-hot labels. That is one line of NumPy in the program. This pair, softmax followed by
cross-entropy, is exactly the output layer and loss of nearly every neural network classifier
([Chapter 15](15-Neural-Networks-and-Backpropagation.md)).

### One-vs-rest

A different way to handle $K$ classes with only binary classifiers: train $K$ separate logistic regressions, the
$k$-th one to tell "class $k$" from "everything else", and predict the class whose classifier gives the highest score.
This is **one-vs-rest** (OvR, also one-vs-all). Its cousin **one-vs-one** trains one classifier for each pair of
classes, $K(K-1)/2$ of them, and lets them vote; it was popular with support vector machines.

The fourth block compares the two on 300 points from three clusters: both reach 97.3 percent training accuracy. The
difference is in the numbers they output. At the point $(0,0)$, between the clusters, softmax gives probabilities
$(0.53,0.10,0.37)$ that add up to 1. The one-vs-rest scores are $(0.074,0.018,0.05)$, adding to $0.142$: each binary
model separately thinks "probably not my class", and their outputs are not a probability distribution over the three
classes. When you need probabilities, prefer softmax; when you have a good binary learner and no multi-class version,
one-vs-rest is a simple and often competitive fallback (Rifkin and Klautau 2004 argued this carefully for SVMs).

## 6.6 Decision boundaries

For logistic regression, "predict class 1 when $p\ge0.5$" is the same as $w^\top x\ge0$, because $\sigma(z)\ge0.5$ exactly
when $z\ge0$. So the decision boundary is the hyperplane $w^\top x=0$: in two dimensions the line
$w_0+w_1x_1+w_2x_2=0$. Every other probability level is also a line, $w^\top x=\operatorname{logit}(q)$, parallel to the
boundary. The weight vector $(w_1,w_2)$ is perpendicular to all of them and points towards class 1, and the
probability changes fastest along it. The larger $\lVert w\rVert$, the closer together the level lines and the more
confident the model.

<figure class="mars-fig" markdown="0">
<svg viewBox="0 0 660 320" role="img" aria-label="Scatter plot of two classes in the plane: green circles mostly upper right, blue squares mostly lower left, overlapping in the middle. Three parallel diagonal lines run from upper left to lower right: the 0.5 decision boundary in the middle and the 0.1 and 0.9 probability lines on either side.">
  <rect x="50" y="34" width="560" height="252" fill="none" stroke="currentColor" stroke-width="1"/>
  <line x1="96" y1="34" x2="444" y2="285" stroke="#eea66f" stroke-width="1.8" stroke-dasharray="6 4"/>
  <line x1="176" y1="34" x2="524" y2="286" stroke="#eea66f" stroke-width="3"/>
  <line x1="256" y1="35" x2="604" y2="286" stroke="#eea66f" stroke-width="1.8" stroke-dasharray="6 4"/>
  <g fill="#7ccf9a" stroke="currentColor" stroke-width="0.8">
    <circle cx="451" cy="95" r="4"/> <circle cx="389" cy="141" r="4"/> <circle cx="511" cy="169" r="4"/> <circle cx="320" cy="77" r="4"/> <circle cx="398" cy="123" r="4"/> <circle cx="453" cy="159" r="4"/> <circle cx="458" cy="81" r="4"/> <circle cx="398" cy="129" r="4"/> <circle cx="380" cy="157" r="4"/> <circle cx="380" cy="113" r="4"/> <circle cx="376" cy="112" r="4"/> <circle cx="416" cy="71" r="4"/> <circle cx="399" cy="63" r="4"/> <circle cx="470" cy="174" r="4"/> <circle cx="332" cy="120" r="4"/> <circle cx="426" cy="95" r="4"/> <circle cx="192" cy="151" r="4"/> <circle cx="390" cy="178" r="4"/> <circle cx="337" cy="90" r="4"/> <circle cx="495" cy="126" r="4"/> <circle cx="342" cy="156" r="4"/> <circle cx="391" cy="135" r="4"/> <circle cx="318" cy="150" r="4"/> <circle cx="447" cy="172" r="4"/> <circle cx="332" cy="55" r="4"/> <circle cx="347" cy="151" r="4"/> <circle cx="420" cy="128" r="4"/> <circle cx="367" cy="96" r="4"/>
  </g>
  <g fill="#9cc9ea" stroke="currentColor" stroke-width="0.8">
    <rect x="216" y="192" width="7" height="7"/> <rect x="353" y="170" width="7" height="7"/> <rect x="296" y="175" width="7" height="7"/> <rect x="115" y="198" width="7" height="7"/> <rect x="270" y="188" width="7" height="7"/> <rect x="254" y="136" width="7" height="7"/> <rect x="268" y="204" width="7" height="7"/> <rect x="232" y="175" width="7" height="7"/> <rect x="230" y="182" width="7" height="7"/> <rect x="186" y="198" width="7" height="7"/> <rect x="224" y="130" width="7" height="7"/> <rect x="278" y="140" width="7" height="7"/> <rect x="195" y="121" width="7" height="7"/> <rect x="229" y="148" width="7" height="7"/> <rect x="307" y="166" width="7" height="7"/> <rect x="265" y="203" width="7" height="7"/> <rect x="263" y="117" width="7" height="7"/> <rect x="297" y="226" width="7" height="7"/> <rect x="337" y="188" width="7" height="7"/> <rect x="232" y="215" width="7" height="7"/> <rect x="396" y="136" width="7" height="7"/> <rect x="255" y="164" width="7" height="7"/> <rect x="121" y="212" width="7" height="7"/> <rect x="363" y="169" width="7" height="7"/> <rect x="289" y="155" width="7" height="7"/> <rect x="266" y="167" width="7" height="7"/> <rect x="206" y="130" width="7" height="7"/> <rect x="207" y="185" width="7" height="7"/> <rect x="383" y="145" width="7" height="7"/> <rect x="136" y="185" width="7" height="7"/> <rect x="171" y="175" width="7" height="7"/> <rect x="221" y="162" width="7" height="7"/> <rect x="123" y="140" width="7" height="7"/> <rect x="362" y="180" width="7" height="7"/> <rect x="345" y="182" width="7" height="7"/> <rect x="169" y="180" width="7" height="7"/> <rect x="286" y="212" width="7" height="7"/> <rect x="169" y="151" width="7" height="7"/>
  </g>
  <g font-size="12" fill="currentColor">
    <text x="60" y="54">p = 0.1</text>
    <text x="190" y="54">p = 0.5</text>
    <text x="268" y="54">p = 0.9</text>
    <text x="330" y="306" text-anchor="middle">feature x1</text>
    <text x="40" y="160" text-anchor="end">x2</text>
    <text x="600" y="276" text-anchor="end">green circles: class 1, blue squares: class 0</text>
  </g>
</svg>
<figcaption>Figure 6.3. A third of the 200 training points with the trained logistic model: the decision boundary p = 0.5 (solid) and the level lines p = 0.1 and p = 0.9 (dashed), all parallel. Points in the band between the dashed lines are the ones the model is unsure about.</figcaption>
</figure>

### Curved boundaries from new features

A straight line cannot separate points inside a circle from points outside it. The fifth block makes 400 points in a
square and labels those with $x_1^2+x_2^2<1.5$ as class 1. With features $x_1,x_2$, logistic regression gets 75.5
percent, exactly the accuracy of always saying "outside": it learns nothing. But "linear" means linear in the
*weights*, not in the original inputs. Add the features $x_1^2$, $x_2^2$ and $x_1x_2$; the boundary $w^\top x=0$ is now

$$w_0+w_1x_1+w_2x_2+w_3x_1^2+w_4x_2^2+w_5x_1x_2=0,$$

which can be any ellipse, parabola or hyperbola, and the circle is one of them. The accuracy jumps to 100 percent.
(That also makes the data separable in the new features, so the weights run away as in 6.4; a small penalty would fix
it.)

The same trick solves the problem that stalled the perceptron in 1969. **XOR** labels the four points
$(0,0),(1,1)$ as class 0 and $(0,1),(1,0)$ as class 1; no line separates them, since any line with both class-1
points on one side must also have the segment between them, which crosses the segment between the class-0 points.
Add the product feature $x_1x_2$: the score $x_1+x_2-2x_1x_2-\tfrac12$ is $-\tfrac12$ at $(0,0)$ and $(1,1)$ and $+\tfrac12$ at
the others, a perfect separator.

Feature engineering ([Chapter 2](02-Data-and-Features.md)) is the classical way to get non-linear boundaries from a
linear model. Its limit is that you must guess the right features, and with $d$ inputs there are about $d^2/2$
products, $d^3/6$ triple products, and so on. Two later ideas avoid the guessing: kernels, which use enormous feature
spaces without ever writing them down ([Chapter 9](09-Nearest-Neighbours-and-Kernels.md)), and neural networks, which
*learn* the features ([Chapter 15](15-Neural-Networks-and-Backpropagation.md)).

## 6.7 Generalised linear models, and why the logistic loss is convex

*Level: advanced.*

Linear regression and logistic regression look different, yet both have gradient "features times (prediction minus
target)" and both are fitted by (reweighted) least squares. They are two members of one family.

### The family

A **generalised linear model** (GLM; Nelder and Wedderburn 1972) has three parts:

1. A distribution for $y$ given $x$ from an **exponential family**: densities of the form
   $p(y\mid\theta)=h(y)\exp\bigl(\theta y-A(\theta)\bigr)$, where $\theta$ is the **natural parameter** and $A$ is the
   **log-partition function** that makes the density sum or integrate to 1.
2. A linear score $\eta=w^\top x$.
3. A **link function** $g$ connecting the mean to the score: $g(\mathbb E[y\mid x])=\eta$. The **canonical link**
   simply sets $\theta=\eta$.

The exponential family has two facts at its heart, both found by differentiating $\sum_yh(y)e^{\theta y-A(\theta)}=1$
with respect to $\theta$: $A'(\theta)=\mathbb E[y]$ and $A''(\theta)=\operatorname{Var}[y]$. (The first derivative gives
$\sum_y(y-A'(\theta))p(y)=0$; differentiating again gives $\sum_y(y-A')^2p(y)-A''=0$.)

The three famous members:

| distribution | for | natural parameter $\theta$ | $A(\theta)$ | mean $A'(\theta)$ | canonical model |
|---|---|---|---|---|---|
| Gaussian (variance 1) | real numbers | the mean $\mu$ | $\theta^2/2$ | $\theta$ | linear regression |
| Bernoulli | 0 or 1 | log-odds $\ln\frac p{1-p}$ | $\ln(1+e^\theta)$ | $\sigma(\theta)$ | logistic regression |
| Poisson | counts $0,1,2,\dots$ | $\ln\lambda$ | $e^\theta$ | $e^\theta$ | Poisson regression |

For the Bernoulli, $p^y(1-p)^{1-y}=\exp\bigl(y\ln\tfrac p{1-p}+\ln(1-p)\bigr)$, and with $\theta=\ln\frac p{1-p}$ one has
$-\ln(1-p)=\ln(1+e^\theta)$. So logistic regression *is* the Bernoulli GLM with canonical link, and the sigmoid is not
an arbitrary squashing function: it is $A'$, the function that maps the natural parameter to the mean.

### One gradient and one Hessian for all of them

With the canonical link, the negative log-likelihood of one example is $A(w^\top x)-y\,w^\top x$ plus a constant. Its
gradient is $\bigl(A'(w^\top x)-y\bigr)x=(\text{mean}-y)\,x$, which explains the common form. Its Hessian is

$$\nabla^2=A''(w^\top x)\,xx^\top=\operatorname{Var}[y\mid x]\;xx^\top.$$

Summing over the examples, the Hessian of the total loss is $X^\top SX$, where $S$ is diagonal with the model's
variances: $1$ for Gaussian, $p_i(1-p_i)$ for Bernoulli, $\mu_i$ for Poisson. Newton's step solves a least-squares
problem weighted by $S$: that is IRLS, for every GLM.

### The convexity theorem

**Theorem 6.2.** The logistic regression loss $J(w)=\frac1n\sum_i\bigl[\ln(1+e^{w^\top x_i})-y_iw^\top x_i\bigr]$ is
convex. It is strictly convex if the design matrix $X$ has full column rank (no feature is a linear combination of
the others).

*Proof.* By the computation above, $\nabla^2J(w)=\frac1nX^\top S X$ with $S=\operatorname{diag}\bigl(p_i(1-p_i)\bigr)$.
For any vector $v$,

$$v^\top\nabla^2J(w)\,v=\frac1n\sum_{i=1}^np_i(1-p_i)\,(x_i^\top v)^2\ge0,$$

because each term is a non-negative weight times a square. So the Hessian is positive semidefinite at every $w$, and
the second-order condition of Chapter 5 gives convexity. Moreover $0<p_i<1$ for every finite $w$, so every weight
$p_i(1-p_i)$ is strictly positive, and the sum is zero only if $x_i^\top v=0$ for all $i$, that is $Xv=0$. With full
column rank that forces $v=0$, so the Hessian is positive definite everywhere and $J$ is strictly convex. $\square$

The same argument works for every canonical-link GLM, since variances are non-negative. The sixth block of the program
checks the theorem numerically: over 1000 random weight vectors, the smallest Hessian eigenvalue is $1.2\times10^{-6}$,
small (the random weights are large, so many $p_i$ are near 0 or 1 and the weights $p_i(1-p_i)$ are tiny) but never
negative. Notice what strict convexity does *not* give: a minimum. A strictly convex function such as $e^{w}$ can
decrease forever, and on separable data the logistic loss does exactly that (6.4). Strict convexity guarantees *at
most one* minimum (Theorem 5.1).

By contrast, squared error after a sigmoid, $\frac1n\sum_i(\sigma(w^\top x_i)-y_i)^2$, is *not* convex in general:
Exercise 9 finds a chord that lies below it. This is another reason the cross-entropy loss is the right partner for
the sigmoid, besides its likelihood origin.

### A Poisson regression

The last block fits counts. It generates 2000 values $x\in[0,2]$ and counts $y\sim\text{Poisson}(e^{0.5+1.2x})$, the kind
of model used for the number of events per day, or of craters per tile of a map. Newton's method (IRLS) from the
constant-rate start converges in four steps to $(0.4826,1.2213)$. The inverse of the Hessian at the optimum estimates
the variance of the fitted weights (a standard result for maximum likelihood estimates, stated here without proof), and
gives standard errors $0.025$ and $0.017$: both fitted coefficients are within one standard error of the true $(0.5,1.2)$.
[Chapter 7](07-Evaluating-Models.md) turns such standard errors into confidence intervals.

An honest warning about Newton for GLMs: started from $w=0$ instead, the first Poisson step in this example overshoots
to a slope of about 7.7, where $e^{w^\top x}$ is in the millions, and it needs about fifteen steps to come back and
converge. Good
starting values or a line search (Chapter 5.6) matter.

**In practice.** scikit-learn's `LogisticRegression` (L-BFGS by default, with an L2 penalty switched on by default)
and `PoissonRegressor`, and the `statsmodels` GLM classes, which use IRLS and report standard errors, implement this
chapter. In PyTorch the pair softmax-plus-cross-entropy is a single function, `cross_entropy`, which works on the
scores directly for numerical stability, the same reason our code uses `logaddexp`.

## Check yourself

??? question "1. Compute $\sigma(0)$, $\sigma(\ln3)$ and $\operatorname{logit}(0.9)$. What odds does $p=0.9$ correspond to?"

    $\sigma(0)=1/(1+1)=0.5$. $\sigma(\ln3)=1/(1+e^{-\ln3})=1/(1+\tfrac13)=0.75$. $\operatorname{logit}(0.9)=\ln(0.9/0.1)=\ln9\approx2.197$.
    The odds are $0.9/0.1=9$, "nine to one".

??? question "2. Run the perceptron by hand on the points $x=(1,1)$ with $y=+1$ and $x=(1,-1)$ with $y=-1$ (first coordinate is the bias input), from $w=0$. How many updates? Check Novikoff's bound."

    Epoch 1: first point, margin $0\le0$, update $w=(1,1)$. Second point: margin $-(1\cdot1+1\cdot(-1))=0\le0$, update
    $w=(1,1)-(1,-1)=(0,2)$. Epoch 2: margins $2$ and $2$, no updates. So 2 updates. Take $u=(0,1)$: margins $1$ and $1$,
    so $\gamma=1$; $R=\sqrt2$. The bound is $(R/\gamma)^2=2$, attained exactly.

??? question "3. A logistic model for spam has weight $0.7$ on the feature 'number of exclamation marks'. What happens to the odds of spam when an email has two more exclamation marks?"

    The log-odds go up by $2\times0.7=1.4$, so the odds are multiplied by $e^{1.4}\approx4.06$. The probability itself
    changes by an amount that depends on where it started: from $0.2$ (odds $0.25$) to odds $1.01$, probability about
    $0.50$; from $0.9$ (odds 9) to odds $36.5$, probability $0.973$.

??? question "4. Show that with labels $y\in\{-1,+1\}$, the logistic loss of one example is $\ln(1+e^{-yz})$."

    For $y=+1$ the loss is $-\ln\sigma(z)=\ln(1+e^{-z})$. For $y=-1$ (class 0 in the 0/1 coding) it is
    $-\ln(1-\sigma(z))=-\ln\sigma(-z)=\ln(1+e^{z})$. Both are $\ln(1+e^{-yz})$.

??? question "5. Derive $\partial\ell/\partial z=p-y$ for $\ell=-[y\ln\sigma(z)+(1-y)\ln(1-\sigma(z))]$ directly with the chain rule, without simplifying $\ell$ first."

    Using $\sigma'=\sigma(1-\sigma)$: $\frac{d}{dz}\ln\sigma=\frac{\sigma(1-\sigma)}\sigma=1-\sigma$ and
    $\frac d{dz}\ln(1-\sigma)=\frac{-\sigma(1-\sigma)}{1-\sigma}=-\sigma$. So
    $\partial\ell/\partial z=-[y(1-\sigma)-(1-y)\sigma]=-[y-y\sigma-\sigma+y\sigma]=\sigma-y$.

??? question "6. Compute the softmax of the scores $(1,1,1)$, of $(1001,1000,999)$ and of $(2,1,0)$. Why does the code subtract the maximum?"

    $(1,1,1)$ gives $(\tfrac13,\tfrac13,\tfrac13)$. $(1001,1000,999)$ is $(2,1,0)$ plus $999$, so both give
    $(0.665,0.245,0.090)$. Computed naively, $e^{1001}$ overflows to infinity in floating point and the result is
    `nan`; subtracting the maximum gives $(0,-1,-2)$, whose exponentials are at most 1, and the same probabilities.

??? question "7. Write the code: train logistic regression by stochastic gradient descent (one example per step, 20 epochs, step 0.1) on the chapter's 200-point data and compare its loss with the optimum 0.256648."

    ```python
    import numpy as np
    rng = np.random.default_rng(0)
    n = 200
    y = (rng.uniform(size=n) < 0.5).astype(float)
    P = rng.normal(size=(n, 2)) + np.where(y[:, None] == 1, [1.5, 1.0], [-0.5, -0.5])
    X = np.c_[np.ones(n), P]
    loss = lambda w: np.mean(np.logaddexp(0, X @ w) - y * (X @ w))

    w = np.zeros(3)
    r = np.random.default_rng(1)
    for epoch in range(20):
        for i in r.permutation(n):
            p = 1 / (1 + np.exp(-X[i] @ w))
            w -= 0.1 * (p - y[i]) * X[i]
    print(w, loss(w))
    ```

    This prints weights $(-1.542, 2.100, 1.398)$ and a loss of $0.25783$, within $0.0012$ of the optimum: SGD with a
    constant step hovers near the minimum on a noise floor, as Chapter 5.3 predicted. A decaying step would get closer.

??? question "8. Show that the decision boundary of a two-class softmax model is the same as that of logistic regression with $w=w_1-w_0$. What does a three-class softmax boundary look like?"

    Class 1 wins when $p_1\ge p_0$, that is $z_1\ge z_0$, that is $(w_1-w_0)^\top x\ge0$: a hyperplane with normal $w_1-w_0$,
    and $p_1=\sigma((w_1-w_0)^\top x)$ as shown in 6.5. With three classes, the region where class $k$ wins is where
    $z_k\ge z_j$ for both other $j$: an intersection of two half-planes, a convex wedge. The plane is cut into three
    convex regions whose boundaries are pieces of the lines $z_j=z_k$, meeting at a point where all three scores are
    equal.

??? question "9. Show that $f(w)=(\sigma(w)-1)^2$, squared error after a sigmoid for one example with label 1, is not convex."

    Its second derivative changes sign. A chord check: $f(-4)=(0.01799-1)^2=0.9643$, $f(0)=0.25$, $f(4)=0.000324$. At
    $t=\tfrac12$ between $-4$ and $0$, the chord height is $(0.9643+0.25)/2=0.6072$, while $f(-2)=(0.1192-1)^2=0.7758$,
    which is above the chord. So $f$ is not convex. Far to the left the curve is almost flat at 1 (the sigmoid has
    saturated), which is also why gradient descent on this loss can stall on confidently wrong examples.

??? question "10. Write the code: one-vs-rest with the perceptron on the chapter's three clusters. Why is it less reliable than with logistic regression?"

    ```python
    import numpy as np
    rng = np.random.default_rng(0)
    centres = np.array([[0, 2.0], [2, -1], [-2, -1]])
    c = rng.integers(0, 3, size=300)
    X = np.c_[np.ones(300), centres[c] + rng.normal(size=(300, 2)) * 0.9]
    W = np.zeros((3, 3))
    for k in range(3):
        yk = np.where(c == k, 1, -1)
        for epoch in range(20):
            for xi, yi in zip(X, yk):
                if yi * (W[:, k] @ xi) <= 0:
                    W[:, k] += yi * xi
    print(np.mean((X @ W).argmax(1) == c))   # 0.9566...
    ```

    It reaches 95.7 percent training accuracy here, against 97.3 for logistic one-vs-rest. The clusters overlap, so none of the three binary problems is separable and each perceptron's final weights depend
    on which examples happened to come last; the raw scores of different perceptrons are not on a common scale either,
    so comparing them with `argmax` is arbitrary. Logistic regression's scores are log-odds, all calibrated the same
    way, and its weights converge.

??? question "11. (Advanced) Write the Poisson model as an exponential family and derive the gradient and Hessian of its negative log-likelihood used in the program."

    $p(y\mid\lambda)=\lambda^ye^{-\lambda}/y!=\frac1{y!}\exp(y\ln\lambda-\lambda)$. So $\theta=\ln\lambda$, $h(y)=1/y!$ and
    $A(\theta)=\lambda=e^\theta$. With $\theta=w^\top x$, the negative log-likelihood of one example is $e^{w^\top
    x}-y\,w^\top x+\ln y!$. Gradient: $(e^{w^\top x}-y)x=(\mu-y)x$. Hessian: $e^{w^\top x}xx^\top=\mu\,xx^\top$. Summed:
    $X^\top(\mu-y)$ and $X^\top\operatorname{diag}(\mu)X$, exactly the `g` and `H` in block 7.

## What you learned

- A classifier outputs a class; a linear classifier thresholds a score $w^\top x$, and its decision boundary is a
  hyperplane. Least squares on 0/1 labels is pulled around by easy points and does not give probabilities.
- The perceptron adds misclassified examples to $w$; on data separable with margin $\gamma$ it makes at most
  $(R/\gamma)^2$ mistakes (Novikoff), proved by a race between alignment and length. On overlapping data it never
  settles.
- Logistic regression models the log-odds as linear, $P(y=1\mid x)=\sigma(w^\top x)$; maximum likelihood gives the
  cross-entropy loss, which punishes confident mistakes.
- The gradient is $\frac1nX^\top(p-y)$, prediction minus label times features; gradient descent and Newton (IRLS)
  both fit it, and on separable data the weights grow without bound unless penalised.
- Softmax regression handles $K$ classes with gradient $\frac1nX^\top(P-Y)$ and gives probabilities that add to 1;
  one-vs-rest combines binary models.
- New features (squares, products) give curved boundaries from a linear model, and solve XOR.
- Logistic, linear and Poisson regression are generalised linear models; their canonical-link losses have Hessian
  $X^\top SX$ with variances on the diagonal, so they are convex (proved).

**Next:** [Chapter 7](07-Evaluating-Models.md) asks how good a classifier really is: accuracy and why it misleads,
precision and recall, ROC curves, cross-validation and honest comparisons.

## Further reading

- C. M. Bishop, *Pattern Recognition and Machine Learning*, 2006: chapter 4 (linear models for classification,
  including the perceptron, logistic regression and IRLS).
- T. Hastie, R. Tibshirani and J. Friedman, *The Elements of Statistical Learning*, 2nd ed., 2009: chapter 4.
- K. P. Murphy, *Probabilistic Machine Learning: An Introduction*, 2022: chapter 10 (logistic regression) and 12
  (generalised linear models).
- S. Shalev-Shwartz and S. Ben-David, *Understanding Machine Learning*, 2014: chapter 9 (linear predictors, the
  perceptron and its bound).
- P. McCullagh and J. A. Nelder, *Generalized Linear Models*, 2nd ed., 1989.
- F. Rosenblatt, "The Perceptron: A Probabilistic Model for Information Storage and Organization in the Brain",
  *Psychological Review* 65(6), 1958.
- A. B. J. Novikoff, "On Convergence Proofs on Perceptrons", *Proceedings of the Symposium on the Mathematical Theory of
  Automata*, 1962.
- M. Minsky and S. Papert, *Perceptrons*, 1969.
- D. R. Cox, "The Regression Analysis of Binary Sequences", *Journal of the Royal Statistical Society B* 20(2), 1958.
- J. A. Nelder and R. W. M. Wedderburn, "Generalized Linear Models", *Journal of the Royal Statistical Society A*
  135(3), 1972.
- Y. Freund and R. E. Schapire, "Large Margin Classification Using the Perceptron Algorithm", *Machine Learning* 37,
  1999.
- R. Rifkin and A. Klautau, "In Defense of One-Vs-All Classification", *JMLR* 5, 2004.
- D. Soudry, E. Hoffer, M. S. Nacson, S. Gunasekar and N. Srebro, "The Implicit Bias of Gradient Descent on Separable
  Data", *JMLR* 19, 2018.
- On this site: [Chapter 5](05-Optimization.md) (gradient descent, Newton, convexity),
  [Chapter 10](10-Support-Vector-Machines.md) (the widest margin), [Chapter 15](15-Neural-Networks-and-Backpropagation.md)
  (stacking logistic units into networks), and the [probability](https://math.akadian.ca/books/probability/) and
  [statistics](https://math.akadian.ca/books/statistics/) books.
