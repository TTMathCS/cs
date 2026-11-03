# 9. Nearest neighbours and kernel methods

*Every model so far has squeezed the training data into a handful of numbers: a weight vector, a bias, perhaps a
regularization strength. This chapter goes the other way. A **nonparametric** method keeps the data and answers each
question by looking at the training examples that resemble it. You will return to the nearest-neighbour classifier
of Chapter 1 and learn to tune it properly, measure by computation why it breaks in high dimensions, build a k-d tree
that finds neighbours without scanning everything, smooth data with kernels to estimate densities and regression
curves, and then meet the idea that runs through the next chapter and much of modern machine learning: the **kernel
trick**, which lets a linear method work in a space of features so large that it is never written down. The chapter
ends with kernel ridge regression, built from scratch.*

!!! abstract "In this chapter"
    **You will learn:**

    - how k-nearest neighbours really behaves: choosing $k$, choosing a distance, and why scaling matters
    - the Cover-Hart theorem: one nearest neighbour is at most twice as wrong as the best possible classifier
    - the curse of dimensionality, measured: distances concentrate and neighbourhoods stop being local
    - k-d trees for exact neighbour search, why they stop helping in high dimensions, and hashing for approximate search
    - kernel density estimation and Nadaraya-Watson regression, with the bandwidth trade-off derived
    - positive definite kernels, the kernel trick, and how to prove a function is (or is not) a kernel
    - kernel ridge regression from scratch, and the representer theorem behind it

    **You need:** [Chapter 1](01-What-Is-Machine-Learning.md) (the first nearest-neighbour classifier),
    [Chapter 2](02-Data-and-Features.md) (scaling), [Chapter 3](03-The-Math-Toolkit.md) (dot products, norms,
    eigenvalues), [Chapter 7](07-Evaluating-Models.md) (validation and cross-validation) and
    [Chapter 8](08-Overfitting-and-Regularization.md) (ridge regression, bias and variance).

    **Levels:** 9.1 and 9.2 are intermediate; 9.3 and 9.4 are intermediate to advanced; 9.5 and 9.6 are advanced.

## 9.1 k-NN revisited: choosing k, distance metrics, scaling

In [Chapter 1](01-What-Is-Machine-Learning.md) you wrote a classifier in twenty lines: to label a new point, find the
training point closest to it and copy its label. It worked surprisingly well. Now we ask the questions that a working
engineer must answer before trusting it. How many neighbours should vote? What does "closest" mean? And why did the
same classifier sometimes fail badly on data that looked easy?

**The rule.** We have $n$ training examples $(x_1, y_1), \dots, (x_n, y_n)$, where each $x_i$ is a vector of $d$
numbers (the features) and $y_i$ is a label. Given a new point $x$, the **k-nearest-neighbour** rule (k-NN):

1. computes the distance from $x$ to every training point $x_i$;
2. takes the $k$ training points with the smallest distances, the **neighbours** of $x$;
3. predicts the label that most of them carry (a **majority vote**). For regression, where $y_i$ is a number, it
   predicts their average instead.

There is no training step at all: "fitting" means storing the table. All the work happens when a question arrives.
Such methods are called **lazy** or **instance-based** learners. The price is paid at prediction time: one query
costs $O(nd)$ arithmetic, because it computes $n$ distances in $d$ dimensions, and the model is as large as the data.

**A trace by hand.** Six training points in the plane, with labels, and a query $q = (0.5, 0.25)$. We compute the six
Euclidean distances $\sqrt{(a_1 - q_1)^2 + (a_2 - q_2)^2}$ and sort them.

| Rank | Point | Coordinates | Label | Distance to $q$ |
| --- | --- | --- | --- | --- |
| 1 | 3 | (0.4, 0.3) | 1 | 0.1118 |
| 2 | 5 | (0.2, 0.6) | 0 | 0.4610 |
| 3 | 4 | (0.9, 0.5) | 1 | 0.4717 |
| 4 | 0 | (0.0, 0.0) | 0 | 0.5590 |
| 5 | 1 | (1.0, 0.0) | 0 | 0.5590 |
| 6 | 2 | (0.5, 1.0) | 0 | 0.7500 |

With $k = 1$ the single neighbour has label 1, so we predict 1. With $k = 3$ the votes are 1, 0, 1: two for class 1,
predict 1. With $k = 5$ the votes are 1, 0, 1, 0, 0: three for class 0, so the prediction flips to 0. The answer
depends on $k$, and nothing in the data tells us which is right. Notice also the tie at ranks 4 and 5: two points at
exactly the same distance. A careful implementation must break ties by a fixed rule (our code keeps the training
order), or the prediction could change from run to run.

### Choosing k

What does $k$ control? With $k = 1$ the classifier copies one example. Every training point is its own nearest
neighbour, so the training accuracy is always 100 percent, and that tells you nothing. Near a noisy point that sits
inside the other class's region, the 1-NN rule draws a little island around it. In the language of
[Chapter 8](08-Overfitting-and-Regularization.md) this is **low bias, high variance**: the boundary follows every
wiggle of the sample, and a different sample would give a different boundary.

With large $k$ each prediction averages many labels, so single noisy points are outvoted. The boundary becomes
smooth. Push $k$ to the extreme, $k = n$, and every query gets the same answer, the majority class: zero variance and
enormous bias. Somewhere between, a $k$ balances the two. We cannot find it from training accuracy, so we use a
**validation set** ([Chapter 7](07-Evaluating-Models.md)): fit on one part of the data, score each candidate $k$ on
another part, choose the best, and report accuracy on a third part, the test set, that played no role in the choice.

Two small rules of thumb. For two classes, use an odd $k$ so votes cannot tie. And $k$ should grow with the amount
of data: a theorem of Charles Stone (1977) says that k-NN is **consistent** (its error tends to the best possible
error as $n \to \infty$, for any distribution) provided $k \to \infty$ and $k/n \to 0$. The first condition kills the
variance (more and more votes); the second kills the bias (the neighbours stay close to $x$).

### Distance metrics

"Closest" needs a **distance**. A function $\mathrm{dist}(a, b)$ is a **metric** if it is never negative, is zero
only when $a = b$, is symmetric ($\mathrm{dist}(a,b) = \mathrm{dist}(b,a)$), and obeys the **triangle inequality**
$\mathrm{dist}(a, c) \le \mathrm{dist}(a, b) + \mathrm{dist}(b, c)$: going via $b$ is never shorter. The most used
family is the **Minkowski** or $L_p$ distance,

$$
\mathrm{dist}_p(a, b) = \Big( \sum_{j=1}^{d} |a_j - b_j|^p \Big)^{1/p}.
$$

For $p = 2$ it is the ordinary **Euclidean** distance, the length of the straight line from $a$ to $b$. For $p = 1$
it is the **Manhattan** distance, the sum of the coordinate differences, as if you could only walk along a grid of
streets. As $p \to \infty$ the largest term wins and we get the **Chebyshev** distance $\max_j |a_j - b_j|$. For text
and other data where only the direction of a vector matters, people use the **cosine distance**
$1 - a \cdot b / (\lVert a \rVert \lVert b \rVert)$ (strictly it is not a metric, because it fails the triangle
inequality, but k-NN does not need one).

Different metrics give different neighbours. Take $q = (0, 0)$, $a = (3, 0)$ and $b = (2, 2)$. In Euclidean distance
$b$ is closer ($2.83$ against $3$); in Manhattan distance $a$ is closer ($3$ against $4$). On many real problems the
choice matters less than you might fear, and much less than the next issue.

### Scaling, again

Suppose one feature is a length in millimetres and another is a temperature in degrees. A difference of 1 degree is
then worth exactly as much as a difference of 1 millimetre, which is nonsense. In distance-based methods, the units
of each feature are a hidden weight. The feature with the largest spread decides who the neighbours are. The cure is
the one from [Chapter 2](02-Data-and-Features.md): **standardise** each feature, replacing $x_j$ by
$(x_j - \mu_j) / \sigma_j$ where $\mu_j$ and $\sigma_j$ are its mean and standard deviation *on the training set*
(computing them on all the data would leak information from the test set).

Standardising does not solve everything. A feature that carries no information about the label still takes part in
every distance. After standardising it counts as much as the useful ones and adds noise to every neighbourhood.
Choosing features, or learning a weight per feature (**metric learning**), is the real fix.

The program below does all of this on the "two moons" data: two interleaved half circles of noisy points, a standard
toy problem whose boundary is curved. It chooses $k$ on a validation set, compares three metrics, and then breaks
the data on purpose by measuring one feature in millimetres and adding a useless noise feature.

```python
--8<-- "books/machine-learning/ch09_knn.py"
```

```
Choosing k on the validation set (Euclidean distance)
   k   train acc   valid acc
   1     1.000       0.933
   3     0.957       0.947
   5     0.957       0.980
   9     0.953       0.960
  15     0.947       0.973
  25     0.943       0.967
  51     0.937       0.967
 101     0.867       0.867
 201     0.787       0.760
best k = 5; test accuracy with it = 0.967

Three metrics, k = 15, validation accuracy
  euclidean  0.973
  manhattan  0.973
  chebyshev  0.967

The same data with feature 1 measured in millimetres (times 1000)
plus one useless feature of pure noise with large spread
  raw units:                     0.707
  standardised (all 3 features): 0.940
  standardised, noise dropped:   0.973

Hand trace: query (0.5, 0.25) against six training points
  point 3 (0.4, 0.3) label 1 distance 0.1118
  point 5 (0.2, 0.6) label 0 distance 0.4610
  point 4 (0.9, 0.5) label 1 distance 0.4717
  point 0 (0.0, 0.0) label 0 distance 0.5590
  point 1 (1.0, 0.0) label 0 distance 0.5590
  point 2 (0.5, 1.0) label 0 distance 0.7500
  k = 1: predicts 1
  k = 3: predicts 1
  k = 5: predicts 0
```

Read the first table from top to bottom. Training accuracy falls steadily as $k$ grows, exactly as the bias-variance
story predicts: $k = 1$ memorises. Validation accuracy rises, plateaus between about 5 and 51, and then collapses
once $k$ is a large fraction of the 300 training points, because the neighbourhoods then reach across both moons. The
three metrics agree within one validation point. The units experiment is the dramatic one: in raw units the first
feature, multiplied by 1000, swamps everything and accuracy falls to 71 percent; standardising recovers most of it;
dropping the noise feature recovers the rest.

A common refinement is **weighted k-NN**: each neighbour votes with a weight that falls with distance, such as
$1/\mathrm{dist}$, so that very close points count more. Weighting by a smooth function of distance leads directly
to the kernel methods of 9.4.

### How good can one neighbour be? The Cover-Hart theorem

*Level: advanced.*

Is 1-NN a toy, or is there a guarantee? To answer, we need the best error any classifier could achieve. For two
classes, write $\eta(x) = P(y = 1 \mid x)$, the probability that a point at $x$ has label 1. The **Bayes classifier**
predicts 1 when $\eta(x) > 1/2$ and 0 otherwise. At $x$ it is wrong with probability $r(x) = \min(\eta(x), 1 - \eta(x))$,
and no classifier can do better at $x$, because whatever it predicts, the true label is the other one with at least
that probability. The **Bayes error** is the average $R^* = E[r(X)]$. It is the noise floor of the problem.

**Theorem (Cover and Hart, 1967).** Under mild conditions (for example, $\eta$ continuous), as $n \to \infty$ the
error of the 1-NN rule tends to

$$
R_{\mathrm{NN}} = E\big[\,2\,\eta(X)\,(1 - \eta(X))\,\big] \le 2R^*(1 - R^*) \le 2R^*.
$$

*Proof sketch.* Fix a query $x$. As $n$ grows, its nearest neighbour $x'$ gets arbitrarily close to $x$ (there are
training points in every small ball around $x$ that has positive probability), so by continuity
$\eta(x') \to \eta(x)$. The labels of $x$ and $x'$ are independent draws given the positions. 1-NN errs when they
differ, which has probability $\eta(x)(1 - \eta(x')) + (1 - \eta(x))\eta(x') \to 2\eta(x)(1 - \eta(x))$. Since
$\eta(1 - \eta) = r(1 - r)$ (the product does not care which of the two is the minimum), the limit is
$2r(x)(1 - r(x))$. Average over $x$: $R_{\mathrm{NN}} = 2E[r] - 2E[r^2]$. By Jensen's inequality, or simply because
a variance is never negative, $E[r^2] \ge (E[r])^2 = (R^*)^2$, so
$R_{\mathrm{NN}} \le 2R^* - 2(R^*)^2 = 2R^*(1 - R^*)$. $\square$

In words: with unlimited data, a classifier that does nothing but copy one label is at most twice as wrong as the
best possible classifier, and on a problem with no noise ($R^* = 0$) it becomes perfect. The factor 2 comes from the
neighbour's own label being noisy. Voting over $k$ neighbours averages that noise away, which is why k-NN with growing
$k$ reaches $R^*$ itself (Stone's theorem). The catch is in "as $n \to \infty$": the theorem says nothing about how
fast. The next section shows that the speed depends terribly on the dimension.

**History.** The nearest-neighbour rule first appears in a 1951 technical report by Evelyn Fix and Joseph Hodges for
the US Air Force School of Aviation Medicine, on nonparametric discrimination. Thomas Cover and Peter Hart's paper
"Nearest Neighbor Pattern Classification" (1967) proved the factor-two bound and made the method famous.

## 9.2 The curse of dimensionality, shown by computation

Nearest neighbours rely on one assumption: that close points have similar labels. In two dimensions "close" is easy
to picture. What happens with 100 features, or 1000? The phrase **curse of dimensionality** was coined by Richard
Bellman (in *Dynamic Programming*, 1957) for the explosion of grid sizes in high dimensions. In machine learning it
names a family of facts, all of which say that high-dimensional space is emptier and stranger than intuition
suggests. We will compute them rather than believe them.

**Fact 1: neighbourhoods are not small.** Spread data uniformly in the unit cube $[0, 1]^d$. To capture a fraction
$p$ of the data in a smaller cube, that cube must have volume $p$, so its edge is $e = p^{1/d}$. For $p = 1\%$ in two
dimensions, $e = 0.1$: a tenth of the range of each feature, nicely local. In ten dimensions $e = 0.01^{1/10} = 0.63$:
to find just 1 percent of the data you must span 63 percent of the range of every single feature. In 100 dimensions,
$e = 0.955$. The "neighbourhood" is almost the whole cube, and the neighbours are not near.

**Fact 2: volume lives at the edge.** The volume of a ball of radius $r$ in $d$ dimensions is $c_d r^d$ for some
constant $c_d$. The fraction of a unit ball's volume within $\varepsilon$ of its surface is therefore
$1 - (1 - \varepsilon)^d$. For $\varepsilon = 0.05$ this is 10 percent in two dimensions and 99.4 percent in 100
dimensions. Almost every point of a high-dimensional ball is near its boundary.

**Fact 3: all distances become about equal.** Pick two independent uniform points $a, b$ in $[0,1]^d$. Each
coordinate contributes $(a_j - b_j)^2$, and for two independent uniform numbers $U, V$ on $[0, 1]$ one computes
$E[(U - V)^2] = 1/6$ and $E[(U - V)^4] = 1/15$, so the variance of one term is $1/15 - 1/36 = 7/180$. The squared
distance is a sum of $d$ independent terms, so it has mean $d/6$ and standard deviation $\sqrt{7d/180}$. The mean grows
like $d$ but the spread only like $\sqrt d$. Relative to its mean, the squared distance has spread
$\sqrt{7d/180} / (d/6) = \sqrt{1.4/d}$, and the distance itself (a square root halves relative errors) about
$\tfrac12\sqrt{1.4/d} \approx 0.59/\sqrt d$. At $d = 100$ that is 6 percent; at $d = 1000$, under 2 percent. When every
point is at nearly the same distance from the query, "the nearest" is decided by noise. Kevin Beyer and coauthors
made this precise in "When Is 'Nearest Neighbor' Meaningful?" (1999): for a wide class of distributions the ratio of
the farthest to the nearest distance tends to 1 as $d \to \infty$.

**Fact 4: you need exponentially many points.** To have a training point within distance $0.1$ (in each coordinate)
of every query in the unit cube, a grid needs $10^d$ points: a hundred in two dimensions, ten billion in ten. Without
some special structure, the amount of data k-NN needs grows exponentially with $d$.

The program measures the first three facts and then runs the experiment that matters: a problem whose label depends
only on the first two features (inside or outside a circle), with $d - 2$ extra features of pure noise.

```python
--8<-- "books/machine-learning/ch09_curse.py"
```

```
1. Distance concentration: 1000 uniform points in the unit cube [0,1]^d,
   distances from one random query point
     d   nearest  farthest  (far-near)/near   mean    sd/mean
     1    0.000     0.540       16822.813    0.255     0.563
     2    0.032     1.112          33.608    0.544     0.443
    10    0.602     1.695           1.815    1.153     0.179
   100    3.475     4.730           0.361    4.063     0.054
  1000   12.123    13.701           0.130   12.963     0.017

2. Edge of the sub-cube that holds a fraction p of uniform data: p ** (1/d)
     d    p=0.01   p=0.1
     1    0.010    0.100
     2    0.100    0.316
     3    0.215    0.464
    10    0.631    0.794
   100    0.955    0.977

3. Fraction of the unit ball's volume within 0.05 of its surface: 1 - 0.95**d
   d =   2: 0.098
   d =  10: 0.401
   d =  50: 0.923
   d = 100: 0.994

4. k-NN (k=5) where only the first 2 features matter (class = which side of a circle);
   the other d-2 features are uniform noise. 500 training points, 500 test points.
     d   test accuracy
     2   0.962
     5   0.826
    10   0.690
    20   0.582
    50   0.572
   100   0.510
   500   0.570
   (always guessing the larger class scores about 0.606)
```

The last column of the first table, the relative spread, matches the formula $0.59/\sqrt d$: $0.19$ predicted at
$d = 10$, $0.059$ at $d = 100$, $0.019$ at $d = 1000$. In one dimension the farthest point is 16822 times farther than
the nearest; in 1000 dimensions only 13 percent farther. The fourth table is the practical lesson. The same 500
training points that give 96 percent accuracy in two dimensions give 69 percent once eight noise features are added,
and by 20 noise features k-NN is worse than ignoring the data and always guessing the more common class. The signal
did not change; only the room around it did.

<figure class="mars-fig" markdown="0">
<svg viewBox="0 0 640 260" role="img" aria-label="Line plot of k-nearest-neighbour test accuracy against the number of dimensions on a logarithmic axis: 0.962 at 2, 0.826 at 5, 0.690 at 10, 0.582 at 20, 0.572 at 50, 0.510 at 100, 0.570 at 500. A dashed line at 0.606 marks always guessing the larger class.">
  <g font-size="12" fill="currentColor" stroke="currentColor" text-anchor="middle">
    <line x1="80" y1="220" x2="560" y2="220" stroke-width="1"/>
    <line x1="80" y1="220" x2="80" y2="30" stroke-width="1"/>
    <line x1="80" y1="220" x2="80" y2="225"/><text x="80" y="240" stroke="none">1</text>
    <line x1="240" y1="220" x2="240" y2="225"/><text x="240" y="240" stroke="none">10</text>
    <line x1="400" y1="220" x2="400" y2="225"/><text x="400" y="240" stroke="none">100</text>
    <line x1="560" y1="220" x2="560" y2="225"/><text x="560" y="240" stroke="none">1000</text>
    <text x="320" y="256" stroke="none">number of features d (2 useful, d - 2 noise), log scale</text>
    <line x1="75" y1="220" x2="80" y2="220"/><text x="70" y="224" stroke="none" text-anchor="end">0.4</text>
    <line x1="75" y1="160" x2="80" y2="160"/><text x="70" y="164" stroke="none" text-anchor="end">0.6</text>
    <line x1="75" y1="100" x2="80" y2="100"/><text x="70" y="104" stroke="none" text-anchor="end">0.8</text>
    <line x1="75" y1="40" x2="80" y2="40"/><text x="70" y="44" stroke="none" text-anchor="end">1.0</text>
    <text x="30" y="130" stroke="none" transform="rotate(-90 30 130)">test accuracy</text>
    <line x1="80" y1="158.2" x2="560" y2="158.2" stroke-dasharray="5 4" stroke-width="1"/>
    <text x="555" y="150" stroke="none" text-anchor="end">guess the larger class: 0.606</text>
    <polyline points="128.2,51.4 191.8,92.2 240,133 288.2,165.4 351.8,168.4 400,187 511.8,169" fill="none" stroke="#eea66f" stroke-width="3"/>
    <circle cx="128.2" cy="51.4" r="4" fill="#eea66f"/>
    <circle cx="191.8" cy="92.2" r="4" fill="#eea66f"/>
    <circle cx="240" cy="133" r="4" fill="#eea66f"/>
    <circle cx="288.2" cy="165.4" r="4" fill="#eea66f"/>
    <circle cx="351.8" cy="168.4" r="4" fill="#eea66f"/>
    <circle cx="400" cy="187" r="4" fill="#eea66f"/>
    <circle cx="511.8" cy="169" r="4" fill="#eea66f"/>
    <text x="140" y="46" stroke="none" text-anchor="start">0.962</text>
    <text x="406" y="204" stroke="none" text-anchor="start">0.510</text>
  </g>
</svg>
<figcaption>The curse of dimensionality in one curve. The label depends on two features only; every added feature is
noise. With 500 training points, k-NN falls below the trivial "always guess the larger class" baseline by about
20 features.</figcaption>
</figure>

**Why does k-NN work at all, then?** Images have tens of thousands of pixels, yet nearest neighbours on raw pixels
classify handwritten digits reasonably well. The escape is that real data is not uniform in its cube. It lies near
a **low-dimensional structure**: the set of all images of a handwritten 3 is a thin, curved sheet (a **manifold**)
inside pixel space, with only a few directions of real variation (thickness, slant, size). What matters for k-NN is
this **intrinsic dimension**, not the number of coordinates. The practical recipes all follow from the curse: remove
useless features, reduce dimension first (PCA in [Chapter 14](14-Dimensionality-Reduction.md)), or learn a
representation in which distance means something (the embeddings of [Chapter 18](18-Sequence-Models.md) and the
learned features of deep networks).

## 9.3 Fast neighbour search: k-d trees and approximate search

A k-NN classifier on a million stored points computes a million distances per question. Can a data structure find
the nearest neighbour without looking at most of them? In one dimension the answer is binary search on a sorted
list: $O(\log n)$. The **k-d tree** (Jon Bentley, 1975; the "k" originally meant the number of dimensions) carries
that idea to $d$ dimensions. The [Algorithms book, Chapter 20](../algorithms/20-Computational-Geometry.md) builds a
two-dimensional one next to Voronoi diagrams; here we build it for any $d$ and measure when it stops helping.

**Building.** A k-d tree is a binary tree. Each node holds one point and a **splitting coordinate** (the **axis**).
At depth 0 we split on coordinate 0, at depth 1 on coordinate 1, and so on, cycling. To build a tree on a set of
points: if the set is empty, return nothing; otherwise sort it by the current axis, put the **median** point at the
node, build the left subtree from the points before it and the right subtree from the points after it, one level
deeper. Every node thus cuts its region of space into two half-spaces by the plane "coordinate $a$ equals the node's
value". Because the median splits the set in half, the depth is $\lceil \log_2(n+1) \rceil$. Sorting at every level
costs $O(n \log^2 n)$ in total as written; finding medians in linear time
([Algorithms, Chapter 6](../algorithms/06-Sorting-in-Linear-Time-and-Selection.md)) gives $O(n \log n)$.

**Searching.** To find the nearest neighbour of a query $q$, keep the best point found so far and its distance
$\delta$. At a node:

1. compute the distance from $q$ to the node's point and update the best if it is closer;
2. let $\Delta = q_a - p_a$ be the signed distance from $q$ to the splitting plane; search first the child on $q$'s
   side (the **near** child);
3. then search the other (**far**) child *only if* $\Delta^2 < \delta^2$, that is, only if the ball of radius
   $\delta$ around $q$ crosses the splitting plane.

**Why the pruning is correct.** Every point $p'$ in the far subtree lies on the other side of the plane, so its
$a$-coordinate differs from $q_a$ by at least $|\Delta|$. The Euclidean distance is at least the difference in any
one coordinate, so $\mathrm{dist}(q, p') \ge |\Delta|$. If $|\Delta| \ge \delta$, no point in the far subtree can beat
the current best, and skipping it loses nothing. Every other subtree is searched, so the search returns a true
nearest neighbour. (The same argument works for any $L_p$ distance, because each is at least the largest coordinate
difference.)

**A trace.** Seven points: $(2,3), (5,4), (9,6), (4,7), (8,1), (7,2), (6,8)$. Sorted by $x$ the median is $(6,8)$,
which becomes the root, splitting on $x = 6$. The left half $\{(2,3), (4,7), (5,4)\}$ sorted by $y$ has median $(5,4)$,
splitting on $y = 4$; the right half $\{(8,1), (7,2), (9,6)\}$ has median $(7,2)$, splitting on $y = 2$. The four
remaining points are leaves. Now query $q = (9, 2)$. Squared distances keep the arithmetic exact.

| Step | Node | Squared distance to $q$ | Best so far | $\Delta$ to the plane | Decision |
| --- | --- | --- | --- | --- | --- |
| 1 | (6,8), split $x$ | $9 + 36 = 45$ | (6,8), 45 | $9 - 6 = 3$ | go right first |
| 2 | (7,2), split $y$ | $4 + 0 = 4$ | (7,2), 4 | $2 - 2 = 0$ | go right first |
| 3 | (9,6), leaf | $0 + 16 = 16$ | (7,2), 4 | | back up |
| 4 | (8,1), leaf | $1 + 1 = 2$ | (8,1), 2 | | (far side of (7,2): $0^2 < 4$, so visited) |
| 5 | back at root | | (8,1), 2 | $3^2 = 9 \ge 2$ | prune the whole left subtree |

Four of the seven points were examined, and the answer $(8,1)$ at distance $\sqrt 2$ is exact. On larger trees the
pruning removes much more than three points.

<figure class="mars-fig" markdown="0">
<svg viewBox="0 0 640 300" role="img" aria-label="Left: the square from 0 to 10 cut by a k-d tree. A vertical line at x equals 6 splits it; the left half is cut horizontally at y equals 4, the right half at y equals 2; further vertical cuts at x equals 2, 4, 8 and 9. The query (9,2) has a circle of radius root 2 reaching the point (8,1) that does not cross x equals 6. Right: the tree with root (6,8) split on x, children (5,4) and (7,2) split on y, and leaves (2,3), (4,7), (8,1), (9,6). The visited nodes are shaded; the left subtree is dashed because it was pruned.">
  <g fill="none" stroke="currentColor" stroke-width="1.2">
    <rect x="40" y="20" width="240" height="240"/>
    <line x1="184" y1="20" x2="184" y2="260" stroke-width="2.5"/>
    <line x1="40" y1="164" x2="184" y2="164" stroke-width="1.8"/>
    <line x1="184" y1="212" x2="280" y2="212" stroke-width="1.8"/>
    <line x1="88" y1="164" x2="88" y2="260"/>
    <line x1="136" y1="20" x2="136" y2="164"/>
    <line x1="232" y1="212" x2="232" y2="260"/>
    <line x1="256" y1="20" x2="256" y2="212"/>
    <circle cx="256" cy="212" r="33.9" stroke="#eea66f" stroke-width="2" stroke-dasharray="5 3"/>
  </g>
  <g fill="currentColor" font-size="11" text-anchor="middle">
    <circle cx="88" cy="188" r="4"/><text x="70" y="200">(2,3)</text>
    <circle cx="160" cy="164" r="4"/><text x="160" y="155">(5,4)</text>
    <circle cx="256" cy="116" r="4"/><text x="238" y="108">(9,6)</text>
    <circle cx="136" cy="92" r="4"/><text x="114" y="86">(4,7)</text>
    <circle cx="232" cy="236" r="4"/><text x="212" y="250">(8,1)</text>
    <circle cx="208" cy="212" r="4"/><text x="204" y="202">(7,2)</text>
    <circle cx="184" cy="68" r="4"/><text x="208" y="62">(6,8)</text>
    <rect x="250" y="206" width="12" height="12" fill="#eea66f" stroke="currentColor"/>
    <text x="160" y="285">x = 6 splits first; query (9, 2) is the square</text>
  </g>
  <g stroke="currentColor" stroke-width="1.2">
    <line x1="475" y1="52" x2="400" y2="98" stroke-dasharray="5 4"/>
    <line x1="475" y1="52" x2="550" y2="98"/>
    <line x1="400" y1="122" x2="360" y2="168" stroke-dasharray="5 4"/>
    <line x1="400" y1="122" x2="440" y2="168" stroke-dasharray="5 4"/>
    <line x1="550" y1="122" x2="510" y2="168"/>
    <line x1="550" y1="122" x2="590" y2="168"/>
    <rect x="440" y="28" width="70" height="24" rx="4" fill="#eea66f" fill-opacity="0.7"/>
    <rect x="365" y="98" width="70" height="24" rx="4" fill="none" stroke-dasharray="5 4"/>
    <rect x="515" y="98" width="70" height="24" rx="4" fill="#eea66f" fill-opacity="0.7"/>
    <rect x="328" y="168" width="64" height="24" rx="4" fill="none" stroke-dasharray="5 4"/>
    <rect x="408" y="168" width="64" height="24" rx="4" fill="none" stroke-dasharray="5 4"/>
    <rect x="478" y="168" width="64" height="24" rx="4" fill="#7ccf9a" fill-opacity="0.8"/>
    <rect x="558" y="168" width="64" height="24" rx="4" fill="#eea66f" fill-opacity="0.7"/>
  </g>
  <g fill="currentColor" font-size="12" text-anchor="middle">
    <text x="475" y="45">(6,8) x</text>
    <text x="400" y="115">(5,4) y</text>
    <text x="550" y="115">(7,2) y</text>
    <text x="360" y="185">(2,3)</text>
    <text x="440" y="185">(4,7)</text>
    <text x="510" y="185">(8,1)</text>
    <text x="590" y="185">(9,6)</text>
    <text x="475" y="230">shaded: examined (green: the answer)</text>
    <text x="475" y="250">dashed: pruned, since 3 squared = 9 is at</text>
    <text x="475" y="268">least the best squared distance 2</text>
  </g>
</svg>
<figcaption>A k-d tree on seven points and the search for the nearest neighbour of (9, 2). The ball of radius
√2 around the query never reaches the plane x = 6, so the whole left half of the space is skipped.</figcaption>
</figure>

**Running time.** In the worst case the search can visit every node (imagine all points on a circle around the
query). For random data in a fixed dimension, Jerome Friedman, Jon Bentley and Raphael Finkel ("An Algorithm for
Finding Best Matches in Logarithmic Expected Time", 1977) showed the expected number of nodes examined is
$O(\log n)$, with a constant that grows roughly like $2^d$. The reason for $2^d$ is geometric: the ball around the
query, of radius $\delta$, overlaps many cells of the partition, and the number of cells a ball can touch grows
exponentially with dimension. Combine that with Fact 3 of 9.2, which says $\delta$ is barely smaller than the typical
distance, and the pruning test $\Delta^2 < \delta^2$ almost always passes. The rule of thumb is that k-d trees pay off
only when $n \gg 2^d$. The program measures it.

```python
--8<-- "books/machine-learning/ch09_kdtree.py"
```

```
Exact nearest neighbour with a k-d tree, n = 10000 uniform points, 50 queries
    d   mean points examined   fraction of n   all answers correct
    2                   18.5          0.0018   True
    4                   70.0          0.0070   True
    8                  808.5          0.0808   True
   12                 7332.1          0.7332   True
   16                 9699.9          0.9700   True

Hand-sized tree: 7 points in 2-D
(6, 8) split on x
    (5, 4) split on y
        (2, 3) split on x
        (4, 7) split on x
    (7, 2) split on y
        (8, 1) split on x
        (9, 6) split on x
query (9, 2): nearest (8, 1), examined 4 of 7 points

Approximate search by random-hyperplane hashing (d = 32, n = 10000)
Each table hashes a point to the signs of b random projections; a query
compares only against points in the same bucket of some table.
  bits  tables   mean candidates   recall of the true nearest
     8       1              49.7   0.495
     8       4             244.0   0.900
    12       4              21.6   0.800
    12      16              81.1   1.000
```

In two dimensions the tree examines about 19 of 10000 points: a 500-fold saving. By 12 dimensions it examines
three quarters of them, and by 16 it is a brute-force scan with extra bookkeeping. Always correct, eventually useless.
**Ball trees** (which split space by spheres instead of planes) and **cover trees** push the limit further when the
data has low intrinsic dimension, but no exact method escapes the curse on truly high-dimensional data: there is
strong evidence from complexity theory that exact nearest-neighbour search in high dimension cannot be much faster
than a scan in the worst case.

### Approximate nearest neighbours

If an exact answer is too expensive, accept a point that is *almost* the nearest. **Locality-sensitive hashing**
(LSH; Piotr Indyk and Rajeev Motwani, 1998) uses hash functions designed so that close points **collide** (get the
same hash value) more often than far points. Store every point in a hash table under its hash value; to answer a
query, compare it only with the points in its own bucket.

For angles between vectors there is a beautiful hash (Moses Charikar, 2002): draw a random vector $r$ with
independent Gaussian entries and set $h(x) = 1$ if $r \cdot x > 0$ and $0$ otherwise. Geometrically, $r$ is the normal
of a random hyperplane through the origin, and $h$ says which side $x$ is on.

**Claim.** For two vectors $u, v$ at angle $\theta$, $P(h(u) \ne h(v)) = \theta / \pi$.

*Proof.* Only the component of $r$ in the plane spanned by $u$ and $v$ matters for the signs of $r \cdot u$ and
$r \cdot v$. A Gaussian vector is rotationally symmetric, so that component points in a uniformly random direction in
the plane, and the line perpendicular to it (where the hyperplane cuts the plane) has a uniformly random direction
too. The two vectors land on different sides exactly when this line passes through the angle between them. A line
through the origin meets the plane in two opposite rays, each of which falls inside the angle of size $\theta$ with
probability $\theta/(2\pi)$, so the probability is $2 \cdot \theta / (2\pi) = \theta/\pi$. $\square$

Concatenating $b$ such bits makes a bucket key; nearby vectors share all $b$ bits with probability
$(1 - \theta/\pi)^b$, which falls fast with $\theta$. Long keys make buckets small and precise but miss true
neighbours; so we build $L$ independent tables and take the union of the query's buckets. The program's last table
shows the trade: 12 bits and 16 tables find the true nearest neighbour for every one of the 200 queries while
comparing with about 81 points instead of 10000. Modern systems mostly use **graph-based** indexes instead, such as
hierarchical navigable small-world graphs (HNSW; Yury Malkov and Dmitry Yashunin, 2016), where each point links to a
few near points and a query walks greedily through the graph; and quantization methods that compress the vectors.

## 9.4 Kernel density estimation and kernel regression

*Level: intermediate to advanced.*

k-NN treats its $k$ neighbours equally and ignores everyone else. That hard cut-off makes its predictions jump
whenever a neighbour enters or leaves the set. What if every training point voted, with a weight that fades smoothly
with distance? The function that sets the weight is called a **kernel**, and this idea gives two classic tools: one
for estimating a probability density, one for regression.

### Kernel density estimation

Given numbers $x_1, \dots, x_n$ drawn from an unknown density $p$, how do we estimate $p$? A histogram counts points
in bins, but its answer depends on where the bins start, and it is a staircase. Murray Rosenblatt (1956) and Emanuel
Parzen (1962) proposed instead to put a small smooth bump on every data point and add them up:

$$
\hat p_h(x) = \frac{1}{nh} \sum_{i=1}^{n} K\!\Big(\frac{x - x_i}{h}\Big).
$$

Here $K$ is the kernel: a density itself, symmetric around 0, usually the standard Gaussian
$K(u) = e^{-u^2/2}/\sqrt{2\pi}$. The **bandwidth** $h > 0$ sets the width of each bump. This is **kernel density
estimation** (KDE), also called the Parzen window method.

Is $\hat p_h$ a density? It is never negative, because $K$ is not. And it integrates to 1: substituting
$u = (x - x_i)/h$, so $dx = h\,du$, each term gives $\frac{1}{nh} \int K(u)\, h\, du = \frac1n$, and there are $n$
terms. So it is a genuine probability density, built as an equal mixture of $n$ bumps.

**By hand.** Data $\{0, 1, 3\}$, Gaussian kernel, $h = 1$, estimate at $x = 1$. The three bumps contribute
$K(1) = 0.2420$, $K(0) = 0.3989$ and $K(-2) = 0.0540$; their sum is $0.6949$, and dividing by $nh = 3$ gives
$\hat p(1) = 0.2316$.

<figure class="mars-fig" markdown="0">
<svg viewBox="0 0 640 250" role="img" aria-label="Kernel density estimate of the three data points 0, 1 and 3 with a Gaussian kernel of bandwidth 1. Each point contributes a bump of height one third of a standard normal; the thick curve is their sum, with value 0.2316 at x equals 1.">
  <g fill="none" stroke-width="1.6">
    <polyline stroke="#9cc9ea" points="60.0,199.4 72.0,198.9 84.0,198.2 96.0,197.0 108.0,195.3 120.0,192.8 132.0,189.5 144.0,185.2 156.0,180.0 168.0,174.1 180.0,167.7 192.0,161.4 204.0,155.6 216.0,150.9 228.0,147.9 240.0,146.8 252.0,147.9 264.0,150.9 276.0,155.6 288.0,161.4 300.0,167.7 312.0,174.1 324.0,180.0 336.0,185.2 348.0,189.5 360.0,192.8 372.0,195.3 384.0,197.0 396.0,198.2 408.0,198.9 420.0,199.4 432.0,199.7 444.0,199.8 456.0,199.9 468.0,200.0 480.0,200.0 492.0,200.0 504.0,200.0 516.0,200.0 528.0,200.0 540.0,200.0 552.0,200.0 564.0,200.0 576.0,200.0 588.0,200.0 600.0,200.0"/>
    <polyline stroke="#9cc9ea" points="60.0,200.0 72.0,200.0 84.0,199.9 96.0,199.8 108.0,199.7 120.0,199.4 132.0,198.9 144.0,198.2 156.0,197.0 168.0,195.3 180.0,192.8 192.0,189.5 204.0,185.2 216.0,180.0 228.0,174.1 240.0,167.7 252.0,161.4 264.0,155.6 276.0,150.9 288.0,147.9 300.0,146.8 312.0,147.9 324.0,150.9 336.0,155.6 348.0,161.4 360.0,167.7 372.0,174.1 384.0,180.0 396.0,185.2 408.0,189.5 420.0,192.8 432.0,195.3 444.0,197.0 456.0,198.2 468.0,198.9 480.0,199.4 492.0,199.7 504.0,199.8 516.0,199.9 528.0,200.0 540.0,200.0 552.0,200.0 564.0,200.0 576.0,200.0 588.0,200.0 600.0,200.0"/>
    <polyline stroke="#9cc9ea" points="60.0,200.0 72.0,200.0 84.0,200.0 96.0,200.0 108.0,200.0 120.0,200.0 132.0,200.0 144.0,200.0 156.0,200.0 168.0,200.0 180.0,200.0 192.0,200.0 204.0,199.9 216.0,199.8 228.0,199.7 240.0,199.4 252.0,198.9 264.0,198.2 276.0,197.0 288.0,195.3 300.0,192.8 312.0,189.5 324.0,185.2 336.0,180.0 348.0,174.1 360.0,167.7 372.0,161.4 384.0,155.6 396.0,150.9 408.0,147.9 420.0,146.8 432.0,147.9 444.0,150.9 456.0,155.6 468.0,161.4 480.0,167.7 492.0,174.1 504.0,180.0 516.0,185.2 528.0,189.5 540.0,192.8 552.0,195.3 564.0,197.0 576.0,198.2 588.0,198.9 600.0,199.4"/>
    <polyline stroke="#eea66f" stroke-width="3" points="60.0,199.4 72.0,198.9 84.0,198.1 96.0,196.8 108.0,195.0 120.0,192.2 132.0,188.4 144.0,183.4 156.0,177.0 168.0,169.4 180.0,160.5 192.0,150.8 204.0,140.7 216.0,130.8 228.0,121.7 240.0,114.0 252.0,108.2 264.0,104.7 276.0,103.5 288.0,104.5 300.0,107.3 312.0,111.4 324.0,116.1 336.0,120.8 348.0,125.0 360.0,128.3 372.0,130.8 384.0,132.6 396.0,134.3 408.0,136.3 420.0,139.0 432.0,142.8 444.0,147.7 456.0,153.7 468.0,160.3 480.0,167.1 492.0,173.8 504.0,179.9 516.0,185.1 528.0,189.4 540.0,192.8 552.0,195.3 564.0,197.0 576.0,198.2 588.0,198.9 600.0,199.4"/>
  </g>
  <g stroke="currentColor" stroke-width="1" fill="currentColor" font-size="12" text-anchor="middle">
    <line x1="60" y1="200" x2="600" y2="200"/>
    <line x1="60" y1="200" x2="60" y2="205"/><text x="60" y="220" stroke="none">-3</text>
    <line x1="120" y1="200" x2="120" y2="205"/><text x="120" y="220" stroke="none">-2</text>
    <line x1="180" y1="200" x2="180" y2="205"/><text x="180" y="220" stroke="none">-1</text>
    <line x1="240" y1="200" x2="240" y2="205"/><text x="240" y="220" stroke="none">0</text>
    <line x1="300" y1="200" x2="300" y2="205"/><text x="300" y="220" stroke="none">1</text>
    <line x1="360" y1="200" x2="360" y2="205"/><text x="360" y="220" stroke="none">2</text>
    <line x1="420" y1="200" x2="420" y2="205"/><text x="420" y="220" stroke="none">3</text>
    <line x1="480" y1="200" x2="480" y2="205"/><text x="480" y="220" stroke="none">4</text>
    <line x1="540" y1="200" x2="540" y2="205"/><text x="540" y="220" stroke="none">5</text>
    <line x1="600" y1="200" x2="600" y2="205"/><text x="600" y="220" stroke="none">6</text>
    <circle cx="240" cy="200" r="5" fill="#7ccf9a" stroke="currentColor"/>
    <circle cx="300" cy="200" r="5" fill="#7ccf9a" stroke="currentColor"/>
    <circle cx="420" cy="200" r="5" fill="#7ccf9a" stroke="currentColor"/>
    <line x1="300" y1="200" x2="300" y2="107.4" stroke-dasharray="4 3"/>
    <text x="312" y="99.4" stroke="none" text-anchor="start">p(1) = 0.2316</text>
    <text x="330" y="242" stroke="none">x (the three data points are the green dots)</text>
  </g>
</svg>
<figcaption>Kernel density estimation by hand: each of the three data points carries a Gaussian bump of area 1/3
(thin blue); the estimate is their sum (thick orange), a smooth density with total area 1.</figcaption>
</figure>

**The bandwidth trade-off, derived.** Everything depends on $h$. A tiny $h$ gives a spike on each data point; a huge
$h$ smears everything into one wide hump. Which $h$ is best? We compute the mean and variance of $\hat p_h(x)$ at one
point $x$, treating the data as random.

*Bias.* Each term has the same expectation, so

$$
E\,\hat p_h(x) = \int \frac1h K\!\Big(\frac{x - t}{h}\Big) p(t)\, dt = \int K(u)\, p(x - hu)\, du,
$$

substituting $t = x - hu$. Expand $p(x - hu) = p(x) - hu\,p'(x) + \tfrac12 h^2 u^2 p''(x) + \dots$ by Taylor's theorem.
Because $K$ integrates to 1 and is symmetric ($\int uK(u)\,du = 0$),

$$
E\,\hat p_h(x) = p(x) + \tfrac12 h^2 \sigma_K^2\, p''(x) + o(h^2), \qquad \sigma_K^2 = \int u^2 K(u)\, du.
$$

The **bias** is about $\tfrac12 h^2 \sigma_K^2 p''(x)$: it is large where the density curves sharply (peaks are flattened
and valleys filled), and it vanishes as $h \to 0$.

*Variance.* The estimate is an average of $n$ independent terms, so its variance is $1/n$ times the variance of one
term, which is at most its second moment:

$$
\mathrm{Var}\,\hat p_h(x) \le \frac1n \int \frac{1}{h^2} K\!\Big(\frac{x - t}{h}\Big)^{\!2} p(t)\,dt = \frac{1}{nh} \int K(u)^2\, p(x - hu)\, du \approx \frac{p(x)\, R(K)}{nh},
$$

where $R(K) = \int K(u)^2\,du$. The variance blows up as $h \to 0$: few points fall under a narrow bump.

*Balance.* The mean squared error is bias squared plus variance,
$\tfrac14 h^4 \sigma_K^4 p''(x)^2 + p(x)R(K)/(nh)$. Setting its derivative in $h$ to zero gives
$h^5 = p(x) R(K) / (n\, \sigma_K^4\, p''(x)^2)$, so the best bandwidth shrinks like $n^{-1/5}$ and the best error
like $n^{-4/5}$. Compare a parametric model that is correct, whose error falls like $n^{-1}$: not knowing the shape of
$p$ costs a little speed. In $d$ dimensions the same calculation gives error $n^{-4/(4+d)}$, the curse of
dimensionality once more.

The formula for the best $h$ involves the unknown $p''$. **Silverman's rule of thumb** plugs in a Gaussian for $p$
and gives $h = 1.06\,\hat\sigma\, n^{-1/5}$, where $\hat\sigma$ is the sample standard deviation (Bernard Silverman,
*Density Estimation for Statistics and Data Analysis*, 1986). It works well for one bump and oversmooths several.
A data-driven alternative is **leave-one-out likelihood**: score each data point by the density estimated from the
*other* $n - 1$ points, and choose $h$ to maximise $\sum_i \log \hat p_{h,-i}(x_i)$. Leaving the point out is
essential. With it left in, $h \to 0$ puts an infinitely tall spike on every point and the likelihood goes to
infinity: the estimate would be rewarded for memorising.

### Nadaraya-Watson regression

Now we have pairs $(x_i, y_i)$ and want a smooth curve $f(x)$ predicting $y$. The best prediction under squared error
is the conditional mean $E[y \mid x]$ ([Chapter 4](04-Linear-Regression.md)). Estimate the joint density of
$(x, y)$ by KDE with a product of kernels, $\hat p(x, y) = \frac1n \sum_i K_h(x - x_i) K_h(y - y_i)$, where
$K_h(u) = K(u/h)/h$. Then, because a symmetric kernel has mean zero, $\int y\, K_h(y - y_i)\,dy = y_i$, and

$$
\hat f(x) = \frac{\int y\, \hat p(x, y)\, dy}{\hat p(x)} = \frac{\sum_{i} K_h(x - x_i)\, y_i}{\sum_{i} K_h(x - x_i)}.
$$

This is the **Nadaraya-Watson estimator**, published independently by Èlizbar Nadaraya and Geoffrey Watson in 1964.
It is a weighted average of all the $y_i$, with weights that fall smoothly with distance from $x$. As $h \to 0$ the
nearest point's weight dominates and it becomes 1-NN regression; as $h \to \infty$ all weights are equal and it
predicts the mean of all $y$. In between it is "smooth k-NN". It is also a **linear smoother**: the prediction is a
fixed linear combination of the $y_i$, which is what makes leave-one-out error cheap to compute.

The program fits a two-bump density and a noisy sine curve, choosing the bandwidth by leave-one-out in both cases.

```python
--8<-- "books/machine-learning/ch09_kernel_smoothing.py"
```

```
Hand example: data {0, 1, 3}, Gaussian kernel, h = 1, estimate at x = 1
  K((1 - 0)/1) = 0.2420
  K((1 - 1)/1) = 0.3989
  K((1 - 3)/1) = 0.0540
  p_hat(1) = sum / (3 * 1) = 0.2316

KDE of 300 points from a two-bump mixture
     h    LOO log-lik   integrated squared error vs the true density
  0.02     -1019.94   0.04291
  0.05      -551.22   0.01490
  0.10      -485.41   0.00772
  0.20      -468.33   0.00663
  0.30      -466.76   0.00936
  0.50      -475.34   0.02138
  1.00      -516.07   0.05883
  2.00      -588.66   0.09802
  LOO choice on a fine grid: h = 0.28;  Silverman's rule 1.06*sd*n^(-1/5) = 0.46
  the estimate integrates to 1.0000

Nadaraya-Watson regression: y = sin(2x) + noise, 80 points on [0, 3]
     h    LOO squared error   error vs the true curve
  0.02              0.1345   0.0540
  0.05              0.1059   0.0221
  0.10              0.0988   0.0122
  0.20              0.1041   0.0162
  0.40              0.1405   0.0571
  0.80              0.2538   0.1761
At the edges the estimate is pulled towards the inside (boundary bias):
  h = 0.1: estimate at x = 3 is -0.413, true value sin(6) = -0.279
  h = 0.4: estimate at x = 3 is -0.664, true value sin(6) = -0.279
```

Both tables show the U-shape of the bias-variance trade-off. In the density table, the leave-one-out likelihood
(which uses only the data) and the integrated squared error against the true density (which we can compute only
because we made the data) both prefer $h$ between 0.2 and 0.3. Silverman's rule, which assumes one bump, picks 0.46
and oversmooths the two-bump mixture: its error at $h = 0.5$ is three times the best. In regression, the leave-one-out
squared error is lowest at $h = 0.1$, which is also where the error against the true curve is smallest. (The
leave-one-out error stays above the noise variance $0.3^2 = 0.09$, as it must: it predicts noisy $y$ values.)

The last two lines show a known weakness, **boundary bias**. At the right edge, $x = 3$, all data lie to the left, so
the weighted average is pulled towards the values just inside the interval, where $\sin 2x$ is near $-1$. The wider
the kernel, the worse. **Local linear regression** fits a weighted straight line instead of a weighted constant
around each $x$ and removes this first-order bias; William Cleveland's LOESS (1979) is the best-known version.

## 9.5 The kernel trick; positive definite kernels; Mercer stated

*Level: advanced.*

So far "kernel" meant a smooth bump. From here on it means something more general and more powerful: a **similarity
function** that behaves like a dot product. The question that leads there: linear models are fast, convex and well
understood, but their boundaries are flat. How can we keep everything good about linear methods and still fit curves?

### Lifting the data

The answer of [Chapter 6](06-Classification-and-Logistic-Regression.md) was to add features. Points on a line with
one class in the middle and the other on both sides cannot be split by one threshold. Map each $x$ to the pair
$(x, x^2)$ and a horizontal line separates them.

<figure class="mars-fig" markdown="0">
<svg viewBox="0 0 640 260" role="img" aria-label="Left: nine points on a line, the three in the middle of one class and three on each side of the other; no single threshold separates them. Right: the same points lifted to the plane by x maps to (x, x squared); now the horizontal line at height 0.6 separates the classes.">
  <g font-size="12" fill="currentColor" stroke="currentColor" text-anchor="middle">
    <line x1="30" y1="130" x2="270" y2="130" stroke-width="1"/>
    <circle cx="54" cy="130" r="7" fill="#eea66f"/>
    <circle cx="78" cy="130" r="7" fill="#eea66f"/>
    <circle cx="102" cy="130" r="7" fill="#eea66f"/>
    <circle cx="126" cy="130" r="7" fill="#9cc9ea"/>
    <circle cx="150" cy="130" r="7" fill="#9cc9ea"/>
    <circle cx="174" cy="130" r="7" fill="#9cc9ea"/>
    <circle cx="198" cy="130" r="7" fill="#eea66f"/>
    <circle cx="222" cy="130" r="7" fill="#eea66f"/>
    <circle cx="246" cy="130" r="7" fill="#eea66f"/>
    <text x="54" y="155" stroke="none">-2</text>
    <text x="102" y="155" stroke="none">-1</text>
    <text x="150" y="155" stroke="none">0</text>
    <text x="198" y="155" stroke="none">1</text>
    <text x="246" y="155" stroke="none">2</text>
    <text x="150" y="40" stroke="none">one feature x: no threshold works</text>
    <line x1="360" y1="220" x2="600" y2="220" stroke-width="1"/>
    <line x1="480" y1="225" x2="480" y2="35" stroke-width="1"/>
    <polyline points="379.2,43.6 384.0,60.0 388.8,75.6 393.6,90.4 398.4,104.4 403.2,117.6 408.0,130.0 412.8,141.6 417.6,152.4 422.4,162.4 427.2,171.6 432.0,180.0 436.8,187.6 441.6,194.4 446.4,200.4 451.2,205.6 456.0,210.0 460.8,213.6 465.6,216.4 470.4,218.4 475.2,219.6 480.0,220.0 484.8,219.6 489.6,218.4 494.4,216.4 499.2,213.6 504.0,210.0 508.8,205.6 513.6,200.4 518.4,194.4 523.2,187.6 528.0,180.0 532.8,171.6 537.6,162.4 542.4,152.4 547.2,141.6 552.0,130.0 556.8,117.6 561.6,104.4 566.4,90.4 571.2,75.6 576.0,60.0 580.8,43.6" fill="none" stroke-width="1" stroke-dasharray="3 3"/>
    <line x1="360" y1="196" x2="600" y2="196" stroke="#7ccf9a" stroke-width="3"/>
    <circle cx="384" cy="60" r="7" fill="#eea66f"/>
    <circle cx="408" cy="130" r="7" fill="#eea66f"/>
    <circle cx="432" cy="180" r="7" fill="#eea66f"/>
    <circle cx="456" cy="210" r="7" fill="#9cc9ea"/>
    <circle cx="480" cy="220" r="7" fill="#9cc9ea"/>
    <circle cx="504" cy="210" r="7" fill="#9cc9ea"/>
    <circle cx="528" cy="180" r="7" fill="#eea66f"/>
    <circle cx="552" cy="130" r="7" fill="#eea66f"/>
    <circle cx="576" cy="60" r="7" fill="#eea66f"/>
    <text x="384" y="238" stroke="none">-2</text>
    <text x="432" y="238" stroke="none">-1</text>
    <text x="528" y="238" stroke="none">1</text>
    <text x="576" y="238" stroke="none">2</text>
    <text x="610" y="200" stroke="none" text-anchor="start">0.6</text>
    <text x="470" y="30" stroke="none" text-anchor="end">x squared</text>
    <text x="480" y="254" stroke="none">features (x, x squared): a line works</text>
  </g>
</svg>
<figcaption>Lifting. Blue points (in the middle) and orange points (on both sides) cannot be separated by one
threshold on x. After the map x → (x, x²), the horizontal line x² = 0.6 separates them: a linear method in the new
features draws a curved boundary in the old ones.</figcaption>
</figure>

In general we pick a **feature map** $\varphi$ from the input space to a (possibly huge) feature space and run a
linear method on $\varphi(x)$. The trouble is size. All products of up to $p$ of the $d$ inputs (all monomials of
degree at most $p$) number $\binom{d+p}{p}$: 286 for $p = 3$, $d = 10$, and about 96 million for $p = 5$, $d = 100$.
Writing those vectors down is hopeless.

### The trick

Many linear methods never need the feature vectors themselves, only their **dot products** $\varphi(x) \cdot \varphi(z)$.
(You will see this for ridge regression in 9.6 and for support vector machines in
[Chapter 10](10-Support-Vector-Machines.md).) And for some feature maps that dot product has a short formula.

Take $d = 2$ and $\varphi(x) = (1, \sqrt2 x_1, \sqrt2 x_2, x_1^2, x_2^2, \sqrt2 x_1 x_2)$. Then

$$
\begin{aligned}
\varphi(x)\cdot\varphi(z) &= 1 + 2x_1 z_1 + 2x_2 z_2 + x_1^2 z_1^2 + x_2^2 z_2^2 + 2x_1x_2z_1z_2 \\
&= 1 + 2(x \cdot z) + (x \cdot z)^2 = (x \cdot z + 1)^2.
\end{aligned}
$$

Computing $(x \cdot z + 1)^2$ costs one dot product in 2 dimensions, yet it equals the dot product in 6 dimensions.
For $x = (1, 2)$, $z = (3, -1)$: $x \cdot z = 1$, so $(x \cdot z + 1)^2 = 4$, and the program checks that
$\varphi(x)\cdot\varphi(z)$ is also 4. In general $(x \cdot z + 1)^p$ is the dot product of feature vectors holding
all monomials of degree up to $p$ (with suitable constant weights), at the cost of one $d$-dimensional dot product
and a power. Replacing every dot product in an algorithm by a function $k(x, z)$ is the **kernel trick**.

### Which functions are kernels?

A function $k(x, z)$ is a **kernel** (in this sense) if it equals $\varphi(x) \cdot \varphi(z)$ for some feature map
$\varphi$ into some space with a dot product. How can we tell, without finding $\varphi$? We look at what $k$ does to
finite sets of points.

For points $x_1, \dots, x_n$, the **Gram matrix** (or kernel matrix) is the $n \times n$ matrix $K$ with entries
$K_{ij} = k(x_i, x_j)$. A symmetric matrix $K$ is **positive semidefinite** (PSD) if $c^\top K c \ge 0$ for every
vector $c$; equivalently, all its eigenvalues are $\ge 0$.

**Definition.** A symmetric function $k$ is a **positive definite kernel** if its Gram matrix is positive
semidefinite for every finite set of points. (The naming is unlucky: "positive definite kernel" is standard even
though the matrices are only semidefinite.)

**Every dot-product kernel is positive definite.** If $k(x, z) = \varphi(x) \cdot \varphi(z)$, then for any $c$,

$$
c^\top K c = \sum_{i,j} c_i c_j\, \varphi(x_i)\cdot\varphi(x_j) = \Big\lVert \sum_i c_i\, \varphi(x_i) \Big\rVert^2 \ge 0.
$$

The converse is the deep part. **Theorem (Moore-Aronszajn; Nachman Aronszajn, 1950).** Every positive definite
kernel $k$ is a dot product $\varphi(x)\cdot\varphi(z)$ in some Hilbert space (a complete space with a dot product,
possibly infinite-dimensional). One can take $\varphi(x) = k(x, \cdot)$, the function "similarity to $x$", living in
a space of functions called the **reproducing kernel Hilbert space** (RKHS) of $k$, in which
$\langle k(x, \cdot), k(z, \cdot) \rangle = k(x, z)$. The full construction (complete the span of these functions under
that dot product) is in Schölkopf and Smola's *Learning with Kernels* (2002), chapter 2.

**Mercer's theorem** (James Mercer, 1909) gives a concrete form when $k$ is continuous on a compact set: there are
functions $e_1, e_2, \dots$ and numbers $\lambda_1 \ge \lambda_2 \ge \dots \ge 0$ with
$k(x, z) = \sum_i \lambda_i e_i(x) e_i(z)$, so $\varphi(x) = (\sqrt{\lambda_1} e_1(x), \sqrt{\lambda_2} e_2(x), \dots)$.
It is the infinite-dimensional version of writing a PSD matrix as $\sum_i \lambda_i v_i v_i^\top$. We state it without
proof; the proof uses the spectral theory of compact operators.

### Building kernels from kernels

In practice one proves a function is a kernel by building it from known kernels with rules that preserve positive
definiteness. Let $k_1, k_2$ be kernels.

1. **Sum:** $k_1 + k_2$ is a kernel. Its Gram matrix is $K_1 + K_2$, and $c^\top(K_1 + K_2)c = c^\top K_1 c + c^\top K_2 c \ge 0$.
2. **Positive scaling:** $a k_1$ for $a \ge 0$ is a kernel, by the same one-line argument.
3. **Product:** $k_1 k_2$ is a kernel. Its Gram matrix is the entrywise (Schur) product $K_1 \circ K_2$. Write
   $K_2 = \sum_m v_m v_m^\top$ (its eigen-decomposition, with each eigenvalue's square root absorbed into $v_m$). Then
   $c^\top (K_1 \circ K_2) c = \sum_m (c \circ v_m)^\top K_1 (c \circ v_m) \ge 0$, where $c \circ v_m$ is the entrywise
   product. This is the **Schur product theorem**.
4. **Function wrapping:** $f(x) k_1(x, z) f(z)$ is a kernel for any function $f$: its Gram matrix is $D K_1 D$ with
   $D$ diagonal, and $c^\top D K_1 D c = (Dc)^\top K_1 (Dc) \ge 0$.
5. **Limits:** a pointwise limit of kernels is a kernel, because a limit of PSD matrices is PSD (each $c^\top K c$ is a
   limit of non-negative numbers).

From these: the linear kernel $x \cdot z$ is a kernel ($\varphi(x) = x$). The constant 1 is a kernel. So
$(x \cdot z + 1)^p$ is a kernel, by sums and products. And $\exp(k_1)$ is a kernel, because
$\exp(k_1) = \sum_{m \ge 0} k_1^m / m!$ is a limit of sums of products with positive weights.

**The Gaussian (RBF) kernel is a kernel.** The radial basis function kernel is $k(x, z) = \exp(-\gamma \lVert x - z \rVert^2)$
with $\gamma > 0$. Expand $\lVert x - z \rVert^2 = \lVert x \rVert^2 - 2x \cdot z + \lVert z \rVert^2$:

$$
k(x, z) = e^{-\gamma \lVert x \rVert^2}\; e^{2\gamma\, x \cdot z}\; e^{-\gamma \lVert z \rVert^2}.
$$

The middle factor is $\exp$ of a scaled linear kernel, so a kernel by rule 5; the outer factors are rule 4 with
$f(x) = e^{-\gamma \lVert x \rVert^2}$. $\square$ Its feature space is infinite-dimensional (the power series has
infinitely many terms), which is why no finite set of features reproduces it exactly. The parameter $\gamma$ is an
inverse squared length scale: large $\gamma$ means similarity drops off quickly, so each point influences only its close
neighbours.

**Not everything is a kernel.** The distance $\lVert x - z \rVert$ itself is not: on two points at distance $a$, its
Gram matrix is $\begin{pmatrix} 0 & a \\ a & 0 \end{pmatrix}$, with eigenvalues $\pm a$. The "sigmoid kernel"
$\tanh(\alpha\, x\cdot z + c)$, once popular because it resembles a neural network, is not positive definite for many
parameter values. The second part of the program below checks the smallest eigenvalue of six Gram matrices on 40
random points. Linear and polynomial kernels give zero up to rounding (their feature spaces have dimension 3 and 20,
less than 40, so their Gram matrices are singular), RBF and Laplacian kernels give strictly positive values, and the
tanh and negative-squared-distance functions give large negative eigenvalues, proving they are not kernels.

**History.** The idea of computing in a feature space through a kernel goes back to Mark Aizerman, Emmanuel
Braverman and Lev Rozonoer's "potential function" method (1964). It became central to machine learning when Bernhard
Boser, Isabelle Guyon and Vladimir Vapnik combined it with maximum-margin classifiers in 1992, the subject of the
next chapter.

## 9.6 Kernel ridge regression from scratch

*Level: advanced.*

Here is the trick applied for real. Take **ridge regression** from [Chapter 8](08-Overfitting-and-Regularization.md):
with a data matrix $X$ ($n$ rows, $d$ columns), targets $y$ and strength $\lambda > 0$, minimise
$\lVert y - Xw \rVert^2 + \lambda \lVert w \rVert^2$. The solution is

$$
w = (X^\top X + \lambda I_d)^{-1} X^\top y.
$$

This involves $X^\top X$, a $d \times d$ matrix of feature products, not dot products between examples. We need to
rewrite it.

**The push-through identity.** For any $X$ and $\lambda > 0$,

$$
(X^\top X + \lambda I_d)^{-1} X^\top = X^\top (X X^\top + \lambda I_n)^{-1}.
$$

*Proof.* Both $(X^\top X + \lambda I_d) X^\top$ and $X^\top (X X^\top + \lambda I_n)$ equal $X^\top X X^\top + \lambda X^\top$.
Multiply that equation on the left by $(X^\top X + \lambda I_d)^{-1}$ and on the right by $(X X^\top + \lambda I_n)^{-1}$.
Both inverses exist because $\lambda > 0$ makes the matrices positive definite. $\square$

So $w = X^\top \alpha$ with $\alpha = (XX^\top + \lambda I)^{-1} y$. The weight vector is a combination of the training
inputs, $w = \sum_i \alpha_i x_i$, and a prediction is $w \cdot x = \sum_i \alpha_i\, (x_i \cdot x)$. Now
$XX^\top$ is the Gram matrix of the linear kernel, and every quantity is a dot product between examples. Replace each
dot product by a kernel and we have **kernel ridge regression** (KRR):

$$
\alpha = (K + \lambda I)^{-1} y, \qquad \hat f(x) = \sum_{i=1}^n \alpha_i\, k(x_i, x).
$$

Training solves one $n \times n$ linear system, $O(n^3)$; each prediction costs $n$ kernel evaluations. The cost no
longer depends on the dimension of the feature space, which may be infinite. The variables $\alpha_i$ are called
**dual variables**, and this form of ridge regression was set out by Craig Saunders, Alexander Gammerman and Vladimir
Vovk (1998); statisticians knew it earlier as smoothing splines and kriging, and [Chapter 12](12-Probabilistic-Models.md)
shows that its predictions are exactly the mean of a Gaussian process.

**Why the answer has this form: the representer theorem.** Consider any learning problem of the form "minimise a
loss on the training points plus $\lambda$ times the squared RKHS norm of $f$". **Theorem (Kimeldorf and Wahba, 1971;
general form by Schölkopf, Herbrich and Smola, 2001).** A minimiser can always be written
$f = \sum_{i=1}^n \alpha_i\, k(x_i, \cdot)$.

*Proof sketch.* Split any $f$ in the RKHS as $f = f_\parallel + f_\perp$, where $f_\parallel$ is in the span of the
$n$ functions $k(x_i, \cdot)$ and $f_\perp$ is orthogonal to all of them. The defining property of the RKHS is that
evaluation is a dot product, $f(x_i) = \langle f, k(x_i, \cdot) \rangle$, so $f_\perp$ contributes nothing to any
$f(x_i)$: the loss is unchanged. But $\lVert f \rVert^2 = \lVert f_\parallel \rVert^2 + \lVert f_\perp \rVert^2$, so
dropping $f_\perp$ can only lower the penalty. $\square$ This is why a search over an infinite-dimensional space of
functions reduces to finding $n$ numbers.

For KRR you can check the formula directly. With $f = \sum_i \alpha_i k(x_i, \cdot)$, the vector of fitted values is
$K\alpha$ and $\lVert f \rVert^2 = \alpha^\top K \alpha$, so we minimise
$\lVert y - K\alpha \rVert^2 + \lambda\, \alpha^\top K \alpha$. Setting the gradient to zero gives
$-2K(y - K\alpha) + 2\lambda K\alpha = 0$, that is $K\big((K + \lambda I)\alpha - y\big) = 0$, which
$\alpha = (K + \lambda I)^{-1} y$ satisfies.

**By hand.** Three points $x = 0, 1, 2$ with $y = 0, 1, 0$, RBF kernel with $\gamma = 1$, $\lambda = 0.1$. The Gram
matrix has $k(0,1) = k(1,2) = e^{-1} = 0.3679$ and $k(0,2) = e^{-4} = 0.0183$, with ones on the diagonal. Solving
$(K + 0.1 I)\alpha = y$ gives $\alpha = (-0.3834, 1.1655, -0.3834)$: the middle point pulls the curve up and its
neighbours pull a little down to keep it from spreading. The prediction at $x = 1$ is
$-0.3834 \cdot 0.3679 + 1.1655 \cdot 1 - 0.3834 \cdot 0.3679 = 0.8834$. It is less than the target 1: that shrinkage is
the ridge penalty at work.

The program checks the kernel trick and the PSD test, fits KRR to the noisy sine of 9.4 over a grid of $\gamma$ and
$\lambda$, and confirms that KRR with a linear kernel gives exactly the ordinary ridge weights.

```python
--8<-- "books/machine-learning/ch09_kernel_ridge.py"
```

```
1. The kernel trick: k(x, z) = (x.z + 1)^2 equals phi(x).phi(z) for an explicit phi
   (x.z + 1)^2      = 4.0000
   phi(x).phi(z)    = 4.0000
   phi(x) = [1.     1.4142 2.8284 1.     4.     2.8284]
   degree 2 in d = 2: explicit features = C(d+p, p) = 6, kernel cost ~ d = 2
   degree 3 in d = 10: explicit features = C(d+p, p) = 286, kernel cost ~ d = 10
   degree 5 in d = 100: explicit features = C(d+p, p) = 96560646, kernel cost ~ d = 100

2. Is the Gram matrix positive semidefinite? smallest eigenvalue on 40 random points
   linear x.z                     -1.425e-14
   polynomial (x.z+1)^3           -1.850e-13
   RBF exp(-|x-z|^2)               2.024e-02
   Laplacian exp(-|x-z|)           2.207e-01
   tanh(x.z - 1) (not a kernel)   -1.816e+01
   -|x-z|^2 (not a kernel)        -2.574e+02

3. Kernel ridge regression on y = sin(2x) + noise, 80 training points
   gamma   lambda   valid MSE   error vs true curve
     0.1    0.001      0.0950   0.0060
     0.1      0.1      0.1607   0.0969
     0.1        1      0.2041   0.1494
     0.1       10      0.3045   0.2636
       1    0.001      0.1036   0.0117
       1      0.1      0.1003   0.0075
       1        1      0.0967   0.0079
       1       10      0.1474   0.0780
      10    0.001      0.1201   0.0235
      10      0.1      0.1066   0.0134
      10        1      0.1029   0.0138
      10       10      0.1785   0.1084
     100    0.001      0.7281   0.6335
     100      0.1      0.1204   0.0342
     100        1      0.1248   0.0429
     100       10      0.3124   0.2596
   best on validation: gamma = 0.1, lambda = 0.001
   plain linear ridge on the same data: valid MSE 0.2277

4. Kernel ridge with a linear kernel = ordinary ridge (primal and dual agree)
   primal w = [ 0.909985 -1.926508  0.488881  0.013885]
   X^T alpha = [ 0.909985 -1.926508  0.488881  0.013885]
   largest difference 6.66e-16

5. Hand example: three points, RBF kernel gamma = 1, lambda = 0.1
   K =
 [[1.     0.3679 0.0183]
 [0.3679 1.     0.3679]
 [0.0183 0.3679 1.    ]]
   alpha = [-0.3834  1.1655 -0.3834]
   prediction at 1.0 = 0.8834
   prediction at 0.5 = 0.5687
```

The grid shows how the two knobs interact. $\gamma$ sets the length scale and $\lambda$ the smoothness penalty, and
they trade against each other: a wide kernel ($\gamma = 0.1$) needs a tiny $\lambda$ to bend enough, while a narrow one
($\gamma = 100$, length scale about $0.1$) with tiny $\lambda$ interpolates the noise and its validation error explodes
to $0.73$. The best KRR fits reach a validation error near the noise level 0.09, and their error against the true
curve is under 0.01, far better than the 0.23 of a straight line. Choosing both knobs by cross-validation is standard
practice.

Compare KRR with Nadaraya-Watson. Both predict a weighted sum $\sum_i \alpha_i k(x_i, x)$. In Nadaraya-Watson the
weights are fixed (each $y_i$ divided by the total weight); in KRR they are *solved for*, so the points cooperate:
a point can get a negative weight to correct its neighbours, as in the hand example. That makes KRR more accurate,
especially at the boundaries, at the cost of an $n \times n$ solve.

**Scaling up.** The $O(n^3)$ solve and $O(n^2)$ memory limit exact kernel methods to tens of thousands of points.
Two families of approximations remove the limit: the **Nyström method** (Christopher Williams and Matthias Seeger,
2001) uses a random subset of the points as a low-rank basis, and **random Fourier features** (Ali Rahimi and
Benjamin Recht, 2007) replace the RBF kernel by an explicit feature map of a few thousand random cosines, after which
ordinary linear ridge regression applies (exercise 11).

**In practice.** scikit-learn has `KNeighborsClassifier` (with k-d and ball trees inside), `KernelDensity` and
`KernelRidge`; libraries such as FAISS (Johnson, Douze and Jégou, "Billion-scale similarity search with GPUs", 2017)
do approximate neighbour search on billions of vectors, which is how retrieval over learned embeddings works.

## Check yourself

??? question "1. With the six training points of 9.1, predict the label of the query (0.8, 0.2) for k = 1, 3 and 5."

    The squared distances give, in order: point 1 (1.0, 0.0) at 0.2828 with label 0; point 4 (0.9, 0.5) at 0.3162
    with label 1; point 3 (0.4, 0.3) at 0.4123 with label 1; point 5 (0.2, 0.6) at 0.7211 with label 0; point 0 at
    0.8246 with label 0; point 2 at 0.8544 with label 0. So $k = 1$ predicts 0; $k = 3$ has votes 0, 1, 1 and predicts
    1; $k = 5$ has votes 0, 1, 1, 0, 0 and predicts 0. The answer flips twice as $k$ grows.

??? question "2. Find a query and two points whose nearest neighbour is different under Euclidean and Manhattan distance."

    Query $(0, 0)$, $a = (3, 0)$, $b = (2, 2)$. Euclidean: $a$ at 3, $b$ at $\sqrt 8 \approx 2.83$, so $b$ is nearer.
    Manhattan: $a$ at 3, $b$ at 4, so $a$ is nearer. Manhattan distance penalises diagonal moves, Euclidean does not.

??? question "3. A problem has Bayes error 0.1. What does the Cover-Hart theorem say about 1-NN with unlimited data? When is the bound reached?"

    $R_{\mathrm{NN}} \le 2 \cdot 0.1 \cdot 0.9 = 0.18$. The proof used $E[r^2] \ge (E[r])^2$, which is an equality exactly
    when $r(x)$ is constant. So the bound is reached when the noise level is the same everywhere, for example when
    $\eta(x) = 0.1$ for every $x$: then 1-NN errs when exactly one of two independent labels is flipped,
    probability $2 \cdot 0.1 \cdot 0.9 = 0.18$. And it is at least $R^*$, since nothing beats the Bayes classifier.

??? question "4. In how many dimensions does half of a ball's volume lie within 1 percent of its radius from the surface? For uniform data in a 50-dimensional cube, what edge length does a sub-cube holding 1 percent of the data need?"

    We need $1 - 0.99^d \ge 0.5$, so $d \ge \ln 0.5 / \ln 0.99 = 68.97$: from $d = 69$ on. The edge is
    $0.01^{1/50} = e^{\ln(0.01)/50} = 0.912$, over 91 percent of each feature's range.

??? question "5. Using the tree of 9.3, trace the nearest-neighbour search for the query (3, 6). How many points are examined?"

    Root $(6,8)$: squared distance $9 + 4 = 13$, best $(6,8)$; $\Delta = 3 - 6 = -3$, so the left child is near.
    $(5,4)$: $4 + 4 = 8$, best $(5,4)$; it splits on $y$ and $\Delta = 6 - 4 = 2 \ge 0$, so its right child $(4,7)$ is
    near. $(4,7)$: $1 + 1 = 2$, best $(4,7)$. Back at $(5,4)$: $\Delta^2 = 4 \ge 2$, prune $(2,3)$. Back at the root:
    $\Delta^2 = 9 \ge 2$, prune the right subtree. Three points examined; the nearest is $(4,7)$ at distance $\sqrt 2$.
    The program's `kd_query` returns the same.

??? question "6. Why must the bandwidth of a KDE be chosen by leave-one-out likelihood rather than by the ordinary likelihood of the data?"

    With each point included in its own estimate, $\hat p_h(x_i) \ge K(0)/(nh)$, because the point's own bump
    contributes $K(0)/(nh)$. As $h \to 0$ this tends to infinity for every $i$, so $\sum_i \log \hat p_h(x_i) \to \infty$:
    the ordinary likelihood always prefers $h \to 0$, a spike on each point, which is useless on new data. Leaving the
    point out removes that self-contribution, and the score measures how well the estimate predicts a point it has
    not seen.

??? question "7. Show that the Nadaraya-Watson estimator with a Gaussian kernel tends to 1-NN regression as h → 0 and to the mean of y as h → ∞."

    The weights are proportional to $\exp(-(x - x_i)^2 / (2h^2))$. Divide numerator and denominator by the largest
    weight, that of the nearest point $x_{(1)}$ (assume it is unique). Every other ratio is
    $\exp\big(-(\mathrm{dist}_i^2 - \mathrm{dist}_{(1)}^2)/(2h^2)\big)$, which tends to 0 as $h \to 0$, so
    $\hat f(x) \to y_{(1)}$. As $h \to \infty$ every exponent tends to 0, every weight to 1, and
    $\hat f(x) \to \frac1n \sum_i y_i$.

??? question "8. Prove that k(x, z) = f(x) f(z) is a kernel for any real function f, and that k(x, z) = |x - z| is not."

    For the first, $\varphi(x) = f(x)$ is a one-dimensional feature map, and $c^\top K c = (\sum_i c_i f(x_i))^2 \ge 0$.
    For the second, two points at distance $a > 0$ give the Gram matrix with 0 on the diagonal and $a$ off it. With
    $c = (1, -1)$, $c^\top K c = -2a < 0$, so the matrix is not PSD and the function is not a kernel.

??? question "9. Kernel ridge regression with a single training point (x1, y1): what is the prediction at any x? What does it become as λ → 0 and as λ → ∞?"

    $K$ is the $1 \times 1$ matrix $k(x_1, x_1)$, so $\alpha = y_1 / (k(x_1,x_1) + \lambda)$ and
    $\hat f(x) = y_1\, k(x_1, x) / (k(x_1, x_1) + \lambda)$. For the RBF kernel $k(x_1,x_1) = 1$, so
    $\hat f(x) = y_1 e^{-\gamma(x - x_1)^2} / (1 + \lambda)$: a bump of height $y_1/(1+\lambda)$ centred on $x_1$. As
    $\lambda \to 0$ it passes exactly through the data point; as $\lambda \to \infty$ it shrinks to the zero function.

??? question "10. Write the code: the leave-one-out residuals of kernel ridge regression without refitting. With H = K(K + λI)⁻¹ (so fitted values are Hy), the i-th leave-one-out residual is (y_i − (Hy)_i)/(1 − H_ii). Check it against n separate fits."

    ```python
    import numpy as np

    rng = np.random.default_rng(1)
    x = rng.uniform(0, 3, 40)
    y = np.sin(2 * x) + rng.normal(0, 0.3, 40)
    K = np.exp(-1.0 * (x[:, None] - x[None, :]) ** 2)
    lam = 0.1
    H = K @ np.linalg.inv(K + lam * np.eye(40))       # fitted values = H y
    fast = (y - H @ y) / (1 - np.diag(H))
    slow = np.empty(40)
    for i in range(40):
        m = np.arange(40) != i
        a = np.linalg.solve(K[np.ix_(m, m)] + lam * np.eye(39), y[m])
        slow[i] = y[i] - K[i, m] @ a
    print(f"largest difference: {np.abs(fast - slow).max():.2e}")
    print(f"LOO mean squared error: {np.mean(fast ** 2):.4f}")
    ```

    It prints `largest difference: 9.99e-15` and `LOO mean squared error: 0.0454`. One matrix inverse replaces 40
    fits. The formula holds for every linear smoother of ridge type; it is how cross-validation for kernel ridge is
    done in practice.

??? question "11. (Hard) Write the code: random Fourier features. For the RBF kernel exp(−γ|x − z|²), draw D frequency vectors w with entries from N(0, 2γ) and offsets b uniform on [0, 2π]; set z(x) = sqrt(2/D) cos(w·x + b). Show that z(x)·z(x') approaches the kernel as D grows."

    ```python
    import numpy as np

    rng = np.random.default_rng(0)
    gamma, d = 0.5, 3
    X = rng.normal(0, 1, (200, d))
    sq = ((X[:, None, :] - X[None, :, :]) ** 2).sum(2)
    K = np.exp(-gamma * sq)
    for D in [10, 100, 1000, 10000]:
        W = rng.normal(0, np.sqrt(2 * gamma), (d, D))   # frequencies from the kernel's Fourier transform
        b = rng.uniform(0, 2 * np.pi, D)
        Z = np.sqrt(2 / D) * np.cos(X @ W + b)
        print(f"D = {D:5d}: largest |K - Z Z^T| = {np.abs(K - Z @ Z.T).max():.4f}")
    ```

    Output: largest errors 1.2237, 0.3173, 0.1170, 0.0315 for $D = 10, 100, 1000, 10000$, shrinking roughly like
    $1/\sqrt D$. Why it works: by Bochner's theorem a shift-invariant kernel is the Fourier transform of a probability
    density, here $N(0, 2\gamma I)$, so $k(x, x') = E_w[\cos(w \cdot (x - x'))]$, and
    $E_b[2\cos(w\cdot x + b)\cos(w \cdot x' + b)] = \cos(w \cdot (x - x'))$. Each feature pair is an unbiased estimate and
    averaging $D$ of them is Monte Carlo. Ridge regression on $Z$ then approximates kernel ridge at cost $O(nD^2)$.

## What you learned

- k-NN stores the data and votes among the $k$ closest points; $k$ trades variance (small $k$) against bias
  (large $k$) and is chosen on validation data; feature scaling and feature choice matter more than the metric.
- With unlimited data 1-NN errs at most $2R^*(1 - R^*)$, twice the Bayes error, and k-NN with $k \to \infty$,
  $k/n \to 0$ reaches the Bayes error, but the theory is silent about how much data that takes.
- In high dimensions neighbourhoods span most of the space, the relative spread of distances shrinks like
  $1/\sqrt d$, and k-NN fails unless the data has low intrinsic dimension.
- k-d trees prune by a correct geometric test and find exact neighbours in about $O(\log n)$ for low $d$, but
  examine almost everything once $2^d$ approaches $n$; hashing and graph indexes trade exactness for speed.
- Kernel density estimation and Nadaraya-Watson regression average with smooth weights; the bandwidth balances a bias
  of order $h^2$ against a variance of order $1/(nh)$, giving an error of order $n^{-4/5}$.
- A kernel is a dot product in a feature space; it is valid exactly when every Gram matrix is positive semidefinite,
  and sums, products, positive scalings and limits of kernels are kernels, which proves the RBF kernel valid.
- Kernel ridge regression solves $(K + \lambda I)\alpha = y$ and predicts $\sum_i \alpha_i k(x_i, x)$; the
  representer theorem explains why $n$ dual variables suffice even in infinite-dimensional feature spaces.

**Next:** [Chapter 10](10-Support-Vector-Machines.md) puts the kernel trick inside the classifier that made it famous:
the support vector machine, which looks for the widest possible margin between the classes.

## Further reading

- T. Hastie, R. Tibshirani and J. Friedman, *The Elements of Statistical Learning*, 2nd ed., 2009: chapter 2.5 (the
  curse of dimensionality), chapter 6 (kernel smoothing methods) and chapter 13 (prototype methods and nearest
  neighbours).
- C. Bishop, *Pattern Recognition and Machine Learning*, 2006: section 2.5 (nonparametric methods) and chapter 6
  (kernel methods).
- B. Schölkopf and A. Smola, *Learning with Kernels*, 2002. The standard book on positive definite kernels and
  reproducing kernel Hilbert spaces.
- K. Murphy, *Probabilistic Machine Learning: An Introduction*, 2022, chapters 16 (exemplar-based methods) and 17
  (kernel methods).
- E. Fix and J. L. Hodges, "Discriminatory Analysis. Nonparametric Discrimination: Consistency Properties", USAF
  School of Aviation Medicine technical report, 1951.
- T. Cover and P. Hart, "Nearest Neighbor Pattern Classification", *IEEE Transactions on Information Theory*, 1967.
- C. J. Stone, "Consistent Nonparametric Regression", *Annals of Statistics*, 1977.
- K. Beyer, J. Goldstein, R. Ramakrishnan and U. Shaft, "When Is 'Nearest Neighbor' Meaningful?", ICDT 1999.
- J. L. Bentley, "Multidimensional Binary Search Trees Used for Associative Searching", *Communications of the ACM*,
  1975; J. H. Friedman, J. L. Bentley and R. A. Finkel, "An Algorithm for Finding Best Matches in Logarithmic Expected
  Time", *ACM Transactions on Mathematical Software*, 1977.
- P. Indyk and R. Motwani, "Approximate Nearest Neighbors: Towards Removing the Curse of Dimensionality", STOC 1998;
  M. Charikar, "Similarity Estimation Techniques from Rounding Algorithms", STOC 2002.
- M. Rosenblatt, "Remarks on Some Nonparametric Estimates of a Density Function", *Annals of Mathematical
  Statistics*, 1956; E. Parzen, "On Estimation of a Probability Density Function and Mode", same journal, 1962;
  B. W. Silverman, *Density Estimation for Statistics and Data Analysis*, 1986.
- E. A. Nadaraya, "On Estimating Regression", *Theory of Probability and Its Applications*, 1964; G. S. Watson,
  "Smooth Regression Analysis", *Sankhyā*, 1964.
- N. Aronszajn, "Theory of Reproducing Kernels", *Transactions of the American Mathematical Society*, 1950.
- G. Kimeldorf and G. Wahba, "Some Results on Tchebycheffian Spline Functions", *Journal of Mathematical Analysis and
  Applications*, 1971; B. Schölkopf, R. Herbrich and A. Smola, "A Generalized Representer Theorem", COLT 2001.
- A. Rahimi and B. Recht, "Random Features for Large-Scale Kernel Machines", NIPS 2007.
- On this site: [Chapter 1](01-What-Is-Machine-Learning.md) for the first nearest-neighbour classifier,
  [Chapter 8](08-Overfitting-and-Regularization.md) for ridge regression, [Chapter 14](14-Dimensionality-Reduction.md)
  for reducing dimension before searching, the [Algorithms book, Chapter 20](../algorithms/20-Computational-Geometry.md)
  for k-d trees and Voronoi diagrams, and [https://math.akadian.ca/books/](https://math.akadian.ca/books/) for the
  linear algebra of positive semidefinite matrices.
