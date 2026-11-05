# 13. Clustering

*Every model so far learned from labelled examples: a house and its price, an email and "spam" or "not spam". Most
of the data in the world has no labels at all. A rover's spectrometer returns thousands of readings of rocks nobody
has named; a shop has millions of customers nobody has sorted into types. Can a program find the groups by itself?
This chapter answers with the main families of clustering methods. You will build k-means and prove that it stops,
make it start well with k-means++, choose the number of groups, derive the EM algorithm for Gaussian mixtures and
prove that it never makes the fit worse, then build hierarchical clustering, DBSCAN and spectral clustering, and see
on one picture why each exists.*

!!! abstract "In this chapter"
    **You will learn:**

    - what a clustering is, and why "the right clusters" depends on the distance and the goal
    - k-means (Lloyd's algorithm), with a proof that it always stops, and why it can stop at a bad answer
    - k-means++ seeding and the guarantee Arthur and Vassilvitskii proved for it
    - how to choose the number of clusters with the elbow and the silhouette
    - Gaussian mixture models and the EM algorithm, derived, with a proof that EM never lowers the likelihood
    - hierarchical clustering, linkages and dendrograms; DBSCAN and the idea of density
    - spectral clustering: graphs, the Laplacian, and why its eigenvectors find connected pieces

    **You need:** [Chapter 3](03-The-Math-Toolkit.md) (vectors, norms, Gaussians, likelihood, eigenvectors),
    [Chapter 9](09-Nearest-Neighbours-and-Kernels.md) (distances and scaling) and
    [Chapter 12](12-Probabilistic-Models.md) (maximum likelihood with Gaussians). Background on probability and
    linear algebra is in [https://math.akadian.ca/books/](https://math.akadian.ca/books/).

    **Levels:** 13.1 to 13.3 are beginner to intermediate; 13.4 and 13.5 are intermediate; 13.6 is intermediate;
    13.7 is advanced.

## 13.1 What a cluster is; distances

Here are seven numbers: 1, 2, 3, 8, 9, 10, 25. Split them into two groups. Most people say {1, 2, 3} and
{8, 9, 10, 25}, or perhaps {1, 2, 3, 8, 9, 10} and {25}. Both answers are reasonable, and that small puzzle already
contains the whole subject. A **cluster** is a group of data points that are more similar to each other than to
points outside the group. **Clustering** is the task of finding such groups in data that has no labels. Because no
teacher says what the right groups are, clustering is the main example of **unsupervised learning** (Chapter 1).

To say "more similar" we need a way to measure how far apart two points are. A **distance** (or **metric**) on a set
of points is a function $d(x, y)$ with four properties: it is never negative, it is zero only when $x = y$, it is
symmetric ($d(x,y) = d(y,x)$), and it obeys the **triangle inequality** $d(x,z) \le d(x,y) + d(y,z)$ (a detour is
never shorter). The ones we use most, for points $x, y$ with $p$ numeric features:

- **Euclidean distance** $\|x - y\|_2 = \sqrt{\sum_j (x_j - y_j)^2}$, the straight-line distance. Most of this
  chapter uses its square, $\|x-y\|^2$, which is not itself a metric (it fails the triangle inequality) but is
  easier to minimise.
- **Manhattan distance** $\|x - y\|_1 = \sum_j |x_j - y_j|$, the distance walking along a grid of streets.
- **Cosine distance** $1 - \dfrac{x \cdot y}{\|x\|\,\|y\|}$, which ignores length and compares only direction. It
  is the usual choice for text, where a long document and a short one about the same thing should be close.

Two warnings from [Chapter 9](09-Nearest-Neighbours-and-Kernels.md) apply with full force here. First, **scale**:
if one feature is measured in metres and another in millimetres, the second dominates every Euclidean distance.
Standardise features (subtract the mean, divide by the standard deviation, [Chapter 2](02-Data-and-Features.md))
before clustering unless you have a reason not to. Second, **dimension**: in hundreds of dimensions all pairwise
distances become nearly equal, and "nearest" loses its meaning. Clustering in very high dimensions usually starts by
reducing the dimension, which is [Chapter 14](14-Dimensionality-Reduction.md).

What is a clustering, exactly? There are two kinds of answer.

- A **hard clustering** of $n$ points into $k$ clusters is a **partition**: every point gets exactly one label in
  $\{1, \dots, k\}$. k-means, hierarchical clustering and DBSCAN give hard clusterings (DBSCAN also allows a label
  "noise").
- A **soft clustering** gives every point a probability of belonging to each cluster, like "70% cluster 1, 30%
  cluster 2". Gaussian mixtures (13.4) give soft clusterings.

There is no single correct clustering of a data set, and it is worth being honest about this from the start. The
seven numbers above have two sensible splits because "group" can mean "points near a common centre" or "points
separated by a big gap". The methods of this chapter differ exactly in which of these meanings they adopt:

| method | what a cluster is | shape it finds | you choose |
|---|---|---|---|
| k-means (13.2) | points near one centre | round, similar size | $k$ |
| Gaussian mixture (13.4) | points from one bell curve | ellipses | $k$ |
| hierarchical (13.5) | points joined by merging nearest groups | depends on linkage | where to cut the tree |
| DBSCAN (13.6) | a dense region, separated by sparse space | any shape | radius $\varepsilon$, density minPts |
| spectral (13.7) | a piece of a similarity graph with few links out | any connected shape | $k$, similarity scale |

Jon Kleinberg made this formal in "An Impossibility Theorem for Clustering" (2002). He wrote down three natural
properties a clustering method might have (it does not depend on the units of distance; any partition can be
produced by some distances; shrinking distances inside clusters and stretching them between clusters does not change
the answer) and proved that **no** method has all three. Every clustering method gives up something. The practical
lesson: choose the method whose idea of "cluster" matches your question, and check the result by looking at it.

## 13.2 k-means: Lloyd's algorithm and k-means++

### The objective

Suppose we want $k$ groups, each summarised by one representative point, its **centre** (or **centroid**). A good
clustering puts every point close to its own centre. Measure "close" by squared distance and add up: for data points
$x_1, \dots, x_n$, labels $c_i \in \{1, \dots, k\}$ and centres $\mu_1, \dots, \mu_k$,

$$
J(c, \mu) = \sum_{i=1}^{n} \|x_i - \mu_{c_i}\|^2 .
$$

$J$ is called the **within-cluster sum of squares** (WCSS) or **inertia**. The **k-means problem** is to choose
labels and centres that make $J$ as small as possible. Each term is the squared error we make if we replace $x_i$ by
its centre, so k-means is also a way to compress data: send only the $k$ centres and each point's label. That is
exactly how Stuart Lloyd met the problem, at Bell Labs in 1957, as the question of how to choose the levels of a
quantizer for digitising a signal (pulse-code modulation). His note circulated for years and was published as
"Least Squares Quantization in PCM" in 1982. Hugo Steinhaus had described the same idea in 1956, and James MacQueen
gave it the name "k-means" in 1967.

Finding the exact minimum is hard: the k-means problem is NP-hard even for $k = 2$ when the dimension is part of the
input (Dasgupta 2008) and even in the plane when $k$ is part of the input (Mahajan, Nimbhorkar and Varadarajan
2009). So we settle for an algorithm that is fast and usually good.

### Two easy half-problems

The trick is that $J$ depends on two things, labels and centres, and each is easy to optimise when the other is
held fixed.

**Fix the centres, choose the labels.** Each point's term $\|x_i - \mu_{c_i}\|^2$ involves only its own label, so
the best choice is to give each point the label of its nearest centre:

$$
c_i = \arg\min_{j} \|x_i - \mu_j\|^2 .
$$

**Fix the labels, choose the centres.** Now $J$ splits into one sum per cluster, and the sum for cluster $j$ is
$\sum_{i : c_i = j} \|x_i - \mu_j\|^2$. Which point $\mu$ makes $\sum_{i \in S} \|x_i - \mu\|^2$ smallest? Take the
gradient with respect to $\mu$ and set it to zero:

$$
\nabla_\mu \sum_{i \in S} \|x_i - \mu\|^2 = -2 \sum_{i \in S} (x_i - \mu) = 0
\quad\Longrightarrow\quad
\mu = \frac{1}{|S|} \sum_{i \in S} x_i .
$$

The function is a sum of convex bowls, so this stationary point is the minimum. There is a cleaner way to see it,
which we will need again. For any point $\mu$, with $\bar{x}$ the mean of the points in $S$,

$$
\sum_{i \in S} \|x_i - \mu\|^2 = \sum_{i \in S} \|x_i - \bar{x}\|^2 + |S|\,\|\bar{x} - \mu\|^2 .
$$

(Expand $x_i - \mu = (x_i - \bar{x}) + (\bar{x} - \mu)$; the cross term is
$2(\bar{x} - \mu) \cdot \sum_{i \in S}(x_i - \bar{x}) = 0$ because deviations from the mean add to zero.) The first
term does not depend on $\mu$ and the second is zero only at $\mu = \bar{x}$. So **the best centre is the mean**,
which is where the name k-means comes from.

### Lloyd's algorithm

Alternate the two half-steps:

1. Choose $k$ starting centres (for example $k$ random data points).
2. **Assignment step:** give each point the label of its nearest centre.
3. **Update step:** move each centre to the mean of the points labelled with it.
4. Repeat 2 and 3 until the labels stop changing.

Let us run it by hand on the seven numbers, with $k = 2$ and the (deliberately poor) starting centres 1 and 2.

| step | centres | assignment | $J$ after assigning |
|---|---|---|---|
| 0 | 1, 2 | {1} and {2, 3, 8, 9, 10, 25} | $0 + (0 + 1 + 36 + 49 + 64 + 529) = 679$ |
| update | 1, 9.5 | | |
| 1 | 1, 9.5 | {1, 2, 3} and {8, 9, 10, 25} | $(0+1+4) + (2.25+0.25+0.25+240.25) = 248$ |
| update | 2, 13 | | |
| 2 | 2, 13 | {1, 2, 3} and {8, 9, 10, 25} (no change) | $(1+0+1) + (25+16+9+144) = 196$ |

The labels did not change in step 2, so the algorithm stops with $J = 196$. Notice that $J$ went down at every step:
679, 248, 196. That is not luck, as we prove next. But notice also that this is **not** the best split. Trying all
six ways to cut the sorted line into a left and a right group shows that {1, ..., 10} and {25} has centres 5.5 and
25 and $J = 2(4.5^2 + 3.5^2 + 2.5^2) = 77.5$. Lloyd's algorithm stopped at a **local minimum**: no single
assignment step or update step can improve it, yet a better answer exists.

<figure class="mars-fig" markdown="0">
<svg viewBox="0 0 640 180" role="img" aria-label="The seven numbers 1, 2, 3, 8, 9, 10, 25 on a line, twice. Top: Lloyd's algorithm from centres 1 and 2 stops with groups 1 to 3 and 8 to 25, centres 2 and 13, J equals 196. Bottom: the best split, 1 to 10 and 25 alone, centres 5.5 and 25, J equals 77.5.">
  <g fill="currentColor" font-size="13">
    <text x="40" y="24">Lloyd from centres 1 and 2 stops here: centres 2 and 13, J = 196</text>
    <text x="40" y="94">the best split: centres 5.5 and 25, J = 77.5</text>
  </g>
  <line x1="40" y1="50" x2="600" y2="50" stroke="currentColor" stroke-width="1"/>
  <line x1="40" y1="120" x2="600" y2="120" stroke="currentColor" stroke-width="1"/>
  <g stroke="currentColor" stroke-width="0.8">
    <circle cx="62" cy="50" r="7" fill="#eea66f"/>
    <circle cx="84" cy="50" r="7" fill="#eea66f"/>
    <circle cx="106" cy="50" r="7" fill="#eea66f"/>
    <circle cx="216" cy="50" r="7" fill="#9cc9ea"/>
    <circle cx="238" cy="50" r="7" fill="#9cc9ea"/>
    <circle cx="260" cy="50" r="7" fill="#9cc9ea"/>
    <circle cx="590" cy="50" r="7" fill="#9cc9ea"/>
    <circle cx="62" cy="120" r="7" fill="#eea66f"/>
    <circle cx="84" cy="120" r="7" fill="#eea66f"/>
    <circle cx="106" cy="120" r="7" fill="#eea66f"/>
    <circle cx="216" cy="120" r="7" fill="#eea66f"/>
    <circle cx="238" cy="120" r="7" fill="#eea66f"/>
    <circle cx="260" cy="120" r="7" fill="#eea66f"/>
    <circle cx="590" cy="120" r="7" fill="#9cc9ea"/>
  </g>
  <g stroke="currentColor" stroke-width="2">
    <path d="M 78 32 L 90 44 M 90 32 L 78 44"/>
    <path d="M 320 32 L 332 44 M 332 32 L 320 44"/>
    <path d="M 155 102 L 167 114 M 167 102 L 155 114"/>
    <path d="M 584 102 L 596 114 M 596 102 L 584 114"/>
  </g>
  <g fill="currentColor" font-size="12" text-anchor="middle">
    <line x1="40" y1="150" x2="600" y2="150" stroke="currentColor" stroke-width="1"/>
    <line x1="40" y1="146" x2="40" y2="154" stroke="currentColor"/><text x="40" y="170">0</text>
    <line x1="150" y1="146" x2="150" y2="154" stroke="currentColor"/><text x="150" y="170">5</text>
    <line x1="260" y1="146" x2="260" y2="154" stroke="currentColor"/><text x="260" y="170">10</text>
    <line x1="370" y1="146" x2="370" y2="154" stroke="currentColor"/><text x="370" y="170">15</text>
    <line x1="480" y1="146" x2="480" y2="154" stroke="currentColor"/><text x="480" y="170">20</text>
    <line x1="590" y1="146" x2="590" y2="154" stroke="currentColor"/><text x="590" y="170">25</text>
  </g>
</svg>
<figcaption>Two clusterings of the same seven numbers. Crosses mark the centres. Lloyd's algorithm can stop at the
top one because no single step improves it, although the bottom one has much smaller total squared error.</figcaption>
</figure>

### Proof that Lloyd's algorithm stops

**Theorem.** If ties in the assignment step are broken by keeping a point's current label when it is among the
nearest, then Lloyd's algorithm stops after finitely many iterations, and $J$ never increases.

*Proof.* Look at what each half-step does to $J$.

- The assignment step chooses, for each point separately, the label that minimises its own term, with the centres
  fixed. Keeping the old label is one of the options, so no term can grow: $J$ does not increase.
- The update step replaces each centre by the mean of its points. By the identity above, the mean minimises that
  cluster's sum, and keeping the old centre was one of the options: $J$ does not increase.

So $J$ is non-increasing over the run. Now count states. After every update step the centres are determined by the
labels (each centre is the mean of its points), so the state of the algorithm is determined by the partition of
the $n$ points into $k$ labelled groups. There are at most $k^n$ such partitions, a finite number. If the
assignment step changes some label, the new label is strictly closer (by the tie rule), so $J$ strictly decreases
in that step. Since $J$ strictly decreases at every iteration that changes the partition, no partition can be
visited twice. With finitely many partitions, the labels must eventually stop changing, and then the algorithm
stops. $\square$

Each iteration costs $O(nkp)$ arithmetic for $n$ points, $k$ centres and $p$ features: every point is compared with
every centre. In practice a few dozen iterations suffice. In the worst case, though, the number of iterations can
be exponential in $n$ even in the plane (Vattani 2011), and the answer can be arbitrarily worse than the best one.
The theorem promises only that the algorithm stops, not that it stops somewhere good.

### Starting well: k-means++

Because the result depends on the start, the usual remedy is to run Lloyd's algorithm from several starts and keep
the run with the smallest $J$. A better start helps even more. The idea of **k-means++**, from David Arthur and
Sergei Vassilvitskii's paper "k-means++: The Advantages of Careful Seeding" (2007), is to spread the starting centres
out, preferring points that are far from the centres already chosen:

1. Choose the first centre uniformly at random among the data points.
2. For every point $x$, let $D(x)$ be its distance to the nearest centre chosen so far.
3. Choose the next centre at random among the data points, picking $x$ with probability $D(x)^2 / \sum_y D(y)^2$.
4. Repeat 2 and 3 until there are $k$ centres; then run Lloyd's algorithm.

A point far from every chosen centre is likely to be picked, but outliers do not always win, because a whole dense
group far away has much more total weight than one stray point. Arthur and Vassilvitskii proved:

**Theorem (Arthur and Vassilvitskii 2007).** If $J_{\text{OPT}}$ is the smallest possible value of $J$ with $k$
centres, the centres chosen by k-means++ seeding (before any Lloyd iteration) satisfy

$$
E[J] \le 8(\ln k + 2)\, J_{\text{OPT}} .
$$

Lloyd's iterations afterwards can only lower $J$, so the final result has the same guarantee. The proof is about
two pages. Its first step is easy and instructive: if the first centre is a uniformly random point $a$ of an optimal
cluster $A$ with mean $\bar{x}$, then by the identity above

$$
E\Big[\sum_{x \in A} \|x - a\|^2\Big] = \frac{1}{|A|}\sum_{a \in A}\Big(\sum_{x \in A}\|x - \bar{x}\|^2 + |A|\,\|a - \bar{x}\|^2\Big) = 2\sum_{x \in A}\|x - \bar{x}\|^2 ,
$$

so a random point of a cluster is, on average, a centre twice as costly as the best one. The paper then shows that
$D^2$ sampling picks points from not-yet-covered clusters often enough, and an induction over the clusters gives the
$\ln k$ factor. The full proof is in the paper.

### The program

The program below runs the hand trace, then works on 150 points in three blobs. It prints $J$ after each Lloyd
iteration, compares 200 random starts with 200 k-means++ starts, and finally computes the elbow and silhouette
tables we use in 13.3.

```python
--8<-- "books/machine-learning/ch13_kmeans.py"
```

```
1. Hand trace in one dimension: points 1 2 3 8 9 10 25, k = 2, start centres 1 and 2
  iter 0: J = 679.0000  centres [1.0, 9.5]
  iter 1: J = 248.0000  centres [2.0, 13.0]
  iter 2: J = 196.0000  centres [2.0, 13.0]
  final labels [0, 0, 0, 1, 1, 1, 1]  J never went up: True
  but the best split (try all 6 cuts of the sorted line) is [1.0, 2.0, 3.0, 8.0, 9.0, 10.0] | [25.0], J = 77.5

2. Three blobs, 150 points. Objective J after each Lloyd iteration (random init):
   [1177.63, 293.12, 193.78, 193.49]

3. Random init versus k-means++ init, 200 single runs each, k = 3
  random   : mean final J  250.64, runs stuck above best+5%:  19 of 200
  k-means++: mean final J  208.42, runs stuck above best+5%:   5 of 200

4. Choosing k: best of 10 k-means++ runs for each k
   k        J   silhouette
   1  1501.31        nan
   2   815.13      0.486
   3   193.49      0.699
   4   164.76      0.575
   5   141.82      0.453
   6   118.31      0.344
```

The trace matches the table. On the blobs, $J$ falls quickly and stops after a handful of iterations. With random
starts, 19 of the 200 runs got stuck at least 5% above the best value found; with k-means++ seeding only 5 did, and
the average final $J$ was much lower. That is the practical meaning of the theorem.

The function `sq_dists` deserves a look: `X[:, None, :] - C[None, :, :]` uses NumPy broadcasting
([Chapter 3](03-The-Math-Toolkit.md)) to form all $n \times k$ difference vectors at once, without a Python loop.

### Limits of k-means

k-means looks for round clusters of similar spread, because squared distance to a centre is the same in every
direction. It fails on long thin clusters (13.4 shows this), on clusters of very different sizes (a big cluster's
far edge is closer to a small cluster's centre), and on shapes like rings (13.7). It always assigns every point,
so outliers pull centres towards them. It needs $k$ in advance. And it needs a mean, so it applies only to numeric
features; **k-medoids** (Kaufman and Rousseeuw's PAM, 1987) uses actual data points as centres and works with any
distance at a higher cost.

<figure class="play" data-play="kmeans"><span class="ai-tag">AI-created</span><figcaption><b>Watch it.</b> Lloyd's algorithm: points join the nearest centre, centres move to the middle of their points, repeat. Press New start to drop the centres elsewhere. The points are made up.</figcaption></figure>

## 13.3 Choosing k: the elbow and the silhouette

How many clusters are there? $J$ cannot answer by itself, because $J$ always goes down when $k$ goes up: with
$k = n$ every point is its own centre and $J = 0$. We need a way to say when extra clusters stop being worth it.

### The elbow

Plot the best $J$ against $k$. While $k$ is smaller than the true number of groups, each new centre splits a real
group and $J$ drops a lot. After that, new centres only split groups that were already fine, and $J$ drops a
little. The plot bends at the true $k$, like an arm at the elbow. In the program's table, $J$ goes 1501, 815, 193,
165, 142, 118: a huge drop from 2 to 3, then small steady drops. The elbow is at $k = 3$, which is how the data was
made.

<figure class="mars-fig" markdown="0">
<svg viewBox="0 0 640 240" role="img" aria-label="Two plots against k from 1 to 6. Left: the within-cluster sum of squares J falls from 1501 to 815 to 193, then slowly to 165, 142 and 118, with an elbow at k equals 3. Right: the mean silhouette is 0.486 at k equals 2, peaks at 0.699 at k equals 3, then falls to 0.575, 0.453 and 0.344.">
  <g fill="none" stroke="currentColor" stroke-width="1">
    <line x1="60" y1="190" x2="290" y2="190"/>
    <line x1="60" y1="190" x2="60" y2="30"/>
    <line x1="380" y1="190" x2="610" y2="190"/>
    <line x1="380" y1="190" x2="380" y2="30"/>
  </g>
  <g fill="currentColor" font-size="12" text-anchor="middle">
    <text x="80" y="206">1</text><text x="120" y="206">2</text><text x="160" y="206">3</text>
    <text x="200" y="206">4</text><text x="240" y="206">5</text><text x="280" y="206">6</text>
    <text x="175" y="228">number of clusters k</text>
    <text x="400" y="206">1</text><text x="440" y="206">2</text><text x="480" y="206">3</text>
    <text x="520" y="206">4</text><text x="560" y="206">5</text><text x="600" y="206">6</text>
    <text x="495" y="228">number of clusters k</text>
    <text x="175" y="20">J (within-cluster sum of squares)</text>
    <text x="495" y="20">mean silhouette</text>
  </g>
  <g fill="currentColor" font-size="11" text-anchor="end">
    <text x="55" y="194">0</text><text x="55" y="114">800</text><text x="55" y="44">1500</text>
    <text x="375" y="194">0</text><text x="375" y="114">0.4</text><text x="375" y="34">0.8</text>
  </g>
  <polyline points="80,39.9 120,108.5 160,170.7 200,173.5 240,175.8 280,178.2" fill="none" stroke="#eea66f" stroke-width="2.5"/>
  <g fill="#eea66f" stroke="currentColor" stroke-width="0.8">
    <circle cx="80" cy="39.9" r="4"/><circle cx="120" cy="108.5" r="4"/><circle cx="160" cy="170.7" r="5.5"/>
    <circle cx="200" cy="173.5" r="4"/><circle cx="240" cy="175.8" r="4"/><circle cx="280" cy="178.2" r="4"/>
  </g>
  <text x="168" y="158" font-size="12" fill="currentColor">elbow</text>
  <polyline points="440,92.8 480,50.2 520,75 560,99.4 600,121.2" fill="none" stroke="#9cc9ea" stroke-width="2.5"/>
  <g fill="#9cc9ea" stroke="currentColor" stroke-width="0.8">
    <circle cx="440" cy="92.8" r="4"/><circle cx="480" cy="50.2" r="5.5"/><circle cx="520" cy="75" r="4"/>
    <circle cx="560" cy="99.4" r="4"/><circle cx="600" cy="121.2" r="4"/>
  </g>
  <text x="488" y="44" font-size="12" fill="currentColor">best: 0.699</text>
</svg>
<figcaption>Choosing k for the three blobs, with the numbers printed by the program. The sum of squares bends at
k = 3 (left) and the silhouette is highest at k = 3 (right).</figcaption>
</figure>

The elbow is a picture, not a rule, and on real data the bend is often soft. Two more principled variants are worth
knowing by name: the **gap statistic** (Tibshirani, Walther and Hastie 2001) compares the drop in $J$ with the drop
seen on random data with no clusters, and for Gaussian mixtures (13.4) the **Bayesian information criterion** (BIC)
adds a penalty proportional to the number of parameters times $\ln n$ to the negative log-likelihood.

### The silhouette

Peter Rousseeuw proposed the **silhouette** in 1987 to measure how well each single point sits in its cluster. For
a point $i$:

- $a(i)$ is the average distance from $i$ to the other points of its own cluster (how tight its home is);
- $b(i)$ is the smallest, over the other clusters, of the average distance from $i$ to that cluster's points (how
  far the nearest neighbouring cluster is);
- the silhouette is

$$
s(i) = \frac{b(i) - a(i)}{\max\big(a(i), b(i)\big)} .
$$

It lies between $-1$ and $1$. A value near 1 means the point is much closer to its own cluster than to any other; near
0 means it lies on a border; negative means it would be happier in the neighbouring cluster. A point alone in its
cluster gets $s(i) = 0$ by convention. The **mean silhouette** over all points scores the whole clustering, and we
choose the $k$ that maximises it.

A hand example. In the clustering {1, 2, 3} and {8, 9, 10, 25}, take the point 3. Its own cluster gives
$a = (|3-1| + |3-2|)/2 = 1.5$. The other cluster gives $b = (5 + 6 + 7 + 22)/4 = 10$. So
$s = (10 - 1.5)/10 = 0.85$: the point 3 is well placed. Take the point 25: $a = (17 + 16 + 15)/3 = 16$ and
$b = (24 + 23 + 22)/3 = 23$, so $s = 7/23 \approx 0.30$. The silhouette notices that 25 is only loosely attached
to its group.

In the program's table the mean silhouette is 0.486 at $k = 2$, peaks at 0.699 at $k = 3$, and falls after that. Both
criteria agree. Computing the silhouette needs all pairwise distances, $O(n^2 p)$ work, which is fine for thousands
of points but not for millions; then one computes it on a random sample.

A sober warning. Every criterion for $k$ encodes an opinion about what a cluster is. The silhouette, like k-means,
prefers compact, well-separated round groups; on two rings it would prefer a wrong answer. If the clusters will be
used for something (a marketing campaign per customer group, a separate model per group), the best $k$ is the one
that makes that use work best, measured directly.

## 13.4 Gaussian mixtures and the EM algorithm

### A model that makes the data

k-means answers "which centre is nearest?". A **mixture model** answers a different question: "what random process
could have produced these points?" Imagine the data was made like this. There are $k$ groups. Group $j$ is chosen
with probability $\pi_j$ (the **mixing weights**, $\pi_j \ge 0$, $\sum_j \pi_j = 1$). Once a group is chosen, the
point is drawn from that group's Gaussian distribution, with mean $\mu_j$ and covariance matrix $\Sigma_j$. Writing
$z$ for the chosen group (a **latent**, or hidden, variable: it exists in the story but we never see it), the
probability density of a point $x$ is

$$
p(x) = \sum_{j=1}^{k} \pi_j\, \mathcal{N}(x \mid \mu_j, \Sigma_j),
\qquad
\mathcal{N}(x \mid \mu, \Sigma) = \frac{1}{(2\pi)^{p/2} |\Sigma|^{1/2}} \exp\!\Big(-\tfrac{1}{2}(x - \mu)^\top \Sigma^{-1} (x - \mu)\Big).
$$

This is a **Gaussian mixture model** (GMM). Its parameters are $\theta = (\pi_j, \mu_j, \Sigma_j)_{j=1}^k$. The
covariance matrix lets each group be an ellipse of any size, shape and tilt, not just a circle. Once the model is
fitted, Bayes' rule ([Chapter 3](03-The-Math-Toolkit.md)) gives each point's soft cluster membership, the
**responsibility** of group $j$ for point $i$:

$$
r_{ij} = P(z_i = j \mid x_i) = \frac{\pi_j\, \mathcal{N}(x_i \mid \mu_j, \Sigma_j)}{\sum_{l=1}^{k} \pi_l\, \mathcal{N}(x_i \mid \mu_l, \Sigma_l)} .
$$

### Why maximum likelihood is hard here

We fit $\theta$ by maximum likelihood ([Chapter 12](12-Probabilistic-Models.md)): choose the parameters that make the
observed data most probable. The log-likelihood of independent points is

$$
\ell(\theta) = \sum_{i=1}^{n} \log \sum_{j=1}^{k} \pi_j\, \mathcal{N}(x_i \mid \mu_j, \Sigma_j) .
$$

For a single Gaussian the log would cancel the exponential and the answer would be the sample mean and covariance.
Here a sum sits inside the log, nothing cancels, and setting the gradient to zero gives equations with no closed
form. Worse, $\ell$ has many local maxima (relabelling the groups alone gives $k!$ equal ones) and it is unbounded:
put one mean exactly on a data point and shrink that covariance to zero, and the density at that point goes to
infinity. Practical fits therefore add a tiny multiple of the identity to every covariance, as our program does.

### The EM idea

If we knew the hidden labels $z_i$, the problem would be easy: each group's parameters would be fitted to its own
points, as for a single Gaussian. We do not know them, but given current parameters we know their probabilities,
the responsibilities. The **expectation-maximization** (EM) algorithm alternates:

- **E step (expectation):** with the current parameters, compute the responsibilities $r_{ij}$ for every point and
  group.
- **M step (maximization):** refit every group's parameters by maximum likelihood, counting point $i$ as a
  fraction $r_{ij}$ of a point in group $j$.

The M-step formulas are weighted versions of the familiar ones. Write $N_j = \sum_i r_{ij}$, the "effective number
of points" in group $j$. Then

$$
\pi_j = \frac{N_j}{n}, \qquad
\mu_j = \frac{1}{N_j}\sum_{i=1}^{n} r_{ij}\, x_i, \qquad
\Sigma_j = \frac{1}{N_j}\sum_{i=1}^{n} r_{ij}\,(x_i - \mu_j)(x_i - \mu_j)^\top .
$$

Compare with k-means. If the responsibilities were forced to be 0 or 1 (each point fully owned by its nearest
group), and every covariance were the same small multiple of the identity, the E step would become the assignment
step and the M step for $\mu_j$ would become the update step. k-means is the "hard", round, equal-size limit of EM
for Gaussian mixtures.

### Deriving the M step and proving EM works

Where do these formulas come from, and why should alternating them climb the likelihood? The answer is a lower bound.
For each point $i$, let $q_i$ be any probability distribution over the $k$ groups ($q_{ij} \ge 0$,
$\sum_j q_{ij} = 1$). Multiply and divide inside the log:

$$
\log p(x_i \mid \theta) = \log \sum_{j} q_{ij}\, \frac{\pi_j\, \mathcal{N}(x_i \mid \mu_j, \Sigma_j)}{q_{ij}}
\;\ge\; \sum_{j} q_{ij} \log \frac{\pi_j\, \mathcal{N}(x_i \mid \mu_j, \Sigma_j)}{q_{ij}} .
$$

The inequality is **Jensen's inequality**: $\log$ is concave, so the log of an average is at least the average of
the logs. (Concave means the curve lies above every chord; for two points,
$\log(\tfrac12 a + \tfrac12 b) \ge \tfrac12 \log a + \tfrac12 \log b$, and the general case follows the same way.)
Summing over $i$ gives a function of both $q$ and $\theta$,

$$
F(q, \theta) = \sum_{i} \sum_{j} q_{ij} \log \frac{\pi_j\, \mathcal{N}(x_i \mid \mu_j, \Sigma_j)}{q_{ij}} \;\le\; \ell(\theta),
$$

called the **evidence lower bound** (ELBO) or, in physics language, the negative free energy. It will appear again
in variational autoencoders ([Chapter 20](20-Generative-Models.md)).

**When is the bound tight?** Write the joint probability as $\pi_j \mathcal{N}(x_i \mid \mu_j, \Sigma_j) = p(x_i \mid \theta)\, r_{ij}$, where $r_{ij}$ is the
responsibility. Then

$$
F(q, \theta) = \sum_i \sum_j q_{ij}\Big(\log p(x_i \mid \theta) + \log \frac{r_{ij}}{q_{ij}}\Big)
= \ell(\theta) - \sum_i \mathrm{KL}(q_i \,\|\, r_i),
$$

where $\mathrm{KL}(q \| r) = \sum_j q_j \log(q_j / r_j)$ is the Kullback-Leibler divergence of
[Chapter 3](03-The-Math-Toolkit.md), which is never negative and is zero exactly when $q = r$. So the gap between
the bound and the true log-likelihood is a sum of KL divergences, and it closes completely when $q_i$ is the
responsibility distribution $r_i$.

Now EM is simply **coordinate ascent on $F$**:

- **E step:** maximise $F$ over $q$ with $\theta$ fixed. By the formula above, the best $q$ is $q_{ij} = r_{ij}$,
  and then $F = \ell(\theta)$.
- **M step:** maximise $F$ over $\theta$ with $q$ fixed. Only the numerator depends on $\theta$, so we maximise
  $\sum_{i,j} q_{ij}\big(\log \pi_j + \log \mathcal{N}(x_i \mid \mu_j, \Sigma_j)\big)$. The log now sits directly on the Gaussian, so this is a
  weighted single-Gaussian problem. For $\mu_j$: the terms with $\mu_j$ are
  $-\tfrac12 \sum_i q_{ij}(x_i - \mu_j)^\top \Sigma_j^{-1}(x_i - \mu_j)$, whose gradient
  $\Sigma_j^{-1}\sum_i q_{ij}(x_i - \mu_j)$ vanishes at the weighted mean. For $\pi_j$: maximise
  $\sum_j N_j \log \pi_j$ subject to $\sum_j \pi_j = 1$; a Lagrange multiplier $\lambda$ gives
  $N_j / \pi_j = \lambda$, so $\pi_j \propto N_j$, that is $\pi_j = N_j / n$. The covariance formula follows the
  same way from the derivative with respect to $\Sigma_j^{-1}$ (the standard single-Gaussian derivation, done in
  Bishop, section 2.3.4).

**Theorem (EM never decreases the likelihood).** Let $\theta^{(t)}$ be the parameters before an EM iteration and
$\theta^{(t+1)}$ after. Then $\ell(\theta^{(t+1)}) \ge \ell(\theta^{(t)})$.

*Proof.* Let $q^{(t)}$ be the responsibilities computed from $\theta^{(t)}$ in the E step. Then

$$
\ell(\theta^{(t)}) = F(q^{(t)}, \theta^{(t)}) \le F(q^{(t)}, \theta^{(t+1)}) \le \ell(\theta^{(t+1)}) .
$$

The equality holds because the E step makes the bound tight. The first inequality holds because the M step chose
$\theta^{(t+1)}$ to maximise $F(q^{(t)}, \cdot)$, and $\theta^{(t)}$ was one of the candidates. The second is the lower
bound itself, true for every $q$ and $\theta$. $\square$

Nothing in the proof used Gaussians. The same argument works for any model with hidden variables in which the
M step can be done, which is why EM is everywhere: mixtures of any kind, hidden Markov models (the Baum-Welch
algorithm, which predates the general theory), missing data, factor analysis ([Chapter 14](14-Dimensionality-Reduction.md)).
Arthur Dempster, Nan Laird and Donald Rubin named the algorithm and gave this general framework in "Maximum Likelihood
from Incomplete Data via the EM Algorithm" (*Journal of the Royal Statistical Society B*, 1977), collecting many
earlier special cases. Their convergence argument had a gap, which C. F. Jeff Wu fixed in 1983: under mild
conditions the iterates converge to a stationary point of $\ell$ (usually a local maximum, but not necessarily the
global one). The interpretation as coordinate ascent on $F$ is from Radford Neal and Geoffrey Hinton (1998).

As with k-means, "never worse" is not "best". EM is a local method; people run it from several starts (often from a
k-means solution) and keep the highest likelihood.

### A hand step

Take eight numbers, $-2.1, -1.7, -1.3, -0.9, 1.2, 1.6, 2.0, 2.5$, two groups, and the poor start $\pi = (0.5, 0.5)$,
$\mu = (-0.5, 0.5)$, both variances 1. The E step for the point $x = -0.9$: the two Gaussians have the same
variance and weight, so the normalising constants cancel and

$$
r_{\cdot 1} = \frac{e^{-(-0.9 + 0.5)^2/2}}{e^{-(-0.9+0.5)^2/2} + e^{-(-0.9-0.5)^2/2}} = \frac{e^{-0.08}}{e^{-0.08} + e^{-0.98}}
= \frac{1}{1 + e^{-0.9}} \approx 0.711 .
$$

So the point $-0.9$ is 71% in group 1 and 29% in group 2. After the E step for all eight points, the M step moves the
first mean to the responsibility-weighted average of the points, $-1.044$ in the program's output, and so on.

### The program

```python
--8<-- "books/machine-learning/ch13_gmm_em.py"
```

```
1. One dimension, 8 points, two components, deliberately poor start
  iter 0: log-lik  -17.7532  pi [0.478, 0.522]  mu [-1.044, 1.269]  var [1.521, 1.759]
  iter 1: log-lik  -15.1442  pi [0.48, 0.52]  mu [-1.268, 1.481]  var [0.926, 1.246]
  iter 2: log-lik  -14.0774  pi [0.487, 0.513]  mu [-1.473, 1.716]  var [0.314, 0.558]
  iter 3: log-lik  -11.5662  pi [0.5, 0.5]  mu [-1.5, 1.823]  var [0.2, 0.238]
  iter 4: log-lik  -10.7554  pi [0.5, 0.5]  mu [-1.5, 1.825]  var [0.2, 0.232]
  iter 5: log-lik  -10.7547  pi [0.5, 0.5]  mu [-1.5, 1.825]  var [0.2, 0.232]
  log-likelihood never decreased: True

2. Two long thin clusters in the plane (300 points). k-means against a GMM with full covariances
  k-means agreement with the true groups: 0.513
  GMM (EM) agreement with the true groups: 0.990  after 178 iterations
  fitted covariances: [[[10.31, -0.05], [-0.05, 0.08]], [[8.04, 0.03], [0.03, 0.07]]]
  smallest change in log-likelihood between iterations: 8.83e-09 (never negative)
```

Each line of part 1 shows the log-likelihood of the parameters at the start of that iteration and the parameters
after its M step. The log-likelihood climbs from $-17.75$ to $-10.75$ and never falls, as the theorem promises; the
means settle at $-1.5$ (the exact mean of the four negative points) and $1.825$ (the mean of the four positive ones).

Part 2 is the case k-means cannot handle: two long, thin, parallel clusters only 1.6 apart, each about ten times
longer than the gap. Nearest-centre assignment cuts them across the middle (agreement 0.513, barely better than a
coin), because a point at the far end of one cluster is closer to the centre of the other. The mixture model learns
covariances that are long in the first coordinate (variances about 10 and 8) and thin in the second (about 0.08),
and recovers the two clusters with agreement 0.990.

The code computes everything in logarithms with the **log-sum-exp** trick,
$\log \sum_j e^{a_j} = m + \log \sum_j e^{a_j - m}$ with $m = \max_j a_j$, because Gaussian densities in many
dimensions are so small that they round to zero in floating point. It also factors each covariance with a Cholesky
decomposition ($\Sigma = LL^\top$) instead of inverting it, which is cheaper and more accurate.

## 13.5 Hierarchical clustering, linkages, dendrograms

### Clusters inside clusters

Biologists classify living things into species, genera, families and orders: groups inside groups. Often that is
what we want from data too, not one partition but a whole **hierarchy**, from which we can read off coarse or fine
groupings. **Agglomerative hierarchical clustering** builds it from the bottom up:

1. Start with every point in its own cluster ($n$ clusters).
2. Find the two clusters that are closest to each other, and merge them.
3. Repeat until one cluster remains. Record each merge and the distance at which it happened.

The result is drawn as a **dendrogram** (from the Greek for "tree drawing"): a tree whose leaves are the points and
whose internal nodes are merges, drawn at a height equal to the merge distance. Cutting the dendrogram with a
horizontal line at height $h$ gives a partition: the clusters are the subtrees hanging below the line. One run
gives the clustering for every $k$ at once.

### Linkages

Step 2 needs the distance between two *clusters* $A$ and $B$, built from point distances $d(a, b)$. The choice is
called the **linkage**:

- **Single linkage:** $\min_{a \in A, b \in B} d(a, b)$, the closest pair. Clusters are joined by their nearest
  members.
- **Complete linkage:** $\max_{a \in A, b \in B} d(a, b)$, the farthest pair. A cluster is only as good as its
  widest spread.
- **Average linkage** (UPGMA): the mean of $d(a,b)$ over all pairs.
- **Ward's method** (Ward 1963): merge the pair that increases the total within-cluster sum of squares $J$ the
  least. It is the hierarchical cousin of k-means and prefers compact round clusters.

Here is a worked example with six points in the plane, numbered 0 to 5:
$(0,0), (1,0), (0,1.5), (5,0), (5,1), (9,0.5)$. The program prints the merges for three linkages:

| merge | single | complete | average |
|---|---|---|---|
| 1 | {0} + {1} at 1.000 | {0} + {1} at 1.000 | {0} + {1} at 1.000 |
| 2 | {3} + {4} at 1.000 | {3} + {4} at 1.000 | {3} + {4} at 1.000 |
| 3 | {2} + {0,1} at 1.500 | {2} + {0,1} at 1.803 | {2} + {0,1} at 1.651 |
| 4 | {0,1,2} + {3,4} at 4.000 | {5} + {3,4} at 4.031 | {5} + {3,4} at 4.031 |
| 5 | {5} + rest at 4.031 | all at 9.055 | all at 6.061 |

Check merge 3 by hand. Point 2 is $(0, 1.5)$. Its distance to point 0 is 1.5 and to point 1 is
$\sqrt{1 + 2.25} = \sqrt{3.25} \approx 1.803$. Single linkage takes the minimum, 1.5; complete takes the maximum,
1.803; average takes the mean, 1.651. Merge 4 is where the linkages disagree. The closest pair between {0,1,2} and
{3,4} is points 1 and 3, at distance 4; point 5 is $\sqrt{16 + 0.25} \approx 4.031$ from both 3 and 4. Single
linkage sees 4 < 4.031 and joins the two left groups first. Complete linkage measures {0,1,2} to {3,4} by the
farthest pair, points 2 and 3 at $\sqrt{25 + 2.25} \approx 5.22$, so it joins 5 to {3,4} first.

<figure class="mars-fig" markdown="0">
<svg viewBox="0 0 640 270" role="img" aria-label="Left: six points in the plane, numbered 0 to 5: three near the origin, two near x equals 5, one at x equals 9. Right: the complete-linkage dendrogram. 0 and 1 merge at height 1, then 2 joins at 1.8; 3 and 4 merge at 1, then 5 joins at 4.03; the two groups merge at 9.06. A dashed cut at height 3 gives three clusters.">
  <g fill="none" stroke="currentColor" stroke-width="1">
    <line x1="30" y1="170" x2="300" y2="170"/>
  </g>
  <g fill="currentColor" font-size="11" text-anchor="middle">
    <text x="40" y="186">0</text><text x="180" y="186">5</text><text x="292" y="186">9</text>
    <text x="165" y="215">the six points (x from 0 to 9)</text>
  </g>
  <g stroke="currentColor" stroke-width="0.8">
    <circle cx="40" cy="150" r="7" fill="#eea66f"/>
    <circle cx="68" cy="150" r="7" fill="#eea66f"/>
    <circle cx="40" cy="105" r="7" fill="#eea66f"/>
    <circle cx="180" cy="150" r="7" fill="#9cc9ea"/>
    <circle cx="180" cy="120" r="7" fill="#9cc9ea"/>
    <circle cx="292" cy="135" r="7" fill="#7ccf9a"/>
  </g>
  <g fill="currentColor" font-size="11">
    <text x="50" y="140">0</text><text x="76" y="140">1</text><text x="50" y="98">2</text>
    <text x="190" y="155">3</text><text x="190" y="116">4</text><text x="302" y="131">5</text>
  </g>
  <g fill="none" stroke="currentColor" stroke-width="1.5">
    <path d="M 360 230 L 360 210 L 400 210 L 400 230"/>
    <path d="M 380 210 L 380 193.9 L 450 193.9 L 450 230"/>
    <path d="M 510 230 L 510 210 L 550 210 L 550 230"/>
    <path d="M 530 210 L 530 149.4 L 600 149.4 L 600 230"/>
    <path d="M 415 193.9 L 415 48.9 L 565 48.9 L 565 149.4"/>
  </g>
  <line x1="345" y1="170" x2="620" y2="170" stroke="currentColor" stroke-width="1" stroke-dasharray="5 4"/>
  <text x="620" y="164" font-size="11" fill="currentColor" text-anchor="end">cut at 3: three clusters</text>
  <g fill="currentColor" font-size="12" text-anchor="middle">
    <text x="360" y="248">0</text><text x="400" y="248">1</text><text x="450" y="248">2</text>
    <text x="510" y="248">3</text><text x="550" y="248">4</text><text x="600" y="248">5</text>
  </g>
  <g fill="currentColor" font-size="11" text-anchor="end">
    <line x1="338" y1="230" x2="338" y2="50" stroke="currentColor" stroke-width="1"/>
    <text x="334" y="234">0</text><text x="334" y="194">2</text><text x="334" y="154">4</text>
    <text x="334" y="114">6</text><text x="334" y="74">8</text>
  </g>
  <text x="490" y="30" font-size="12" fill="currentColor" text-anchor="middle">complete-linkage dendrogram (height = merge distance)</text>
</svg>
<figcaption>The six points (left, coloured by the three clusters of the cut) and their complete-linkage dendrogram
(right). The dashed line at height 3 crosses three vertical lines, so it cuts the tree into {0,1,2}, {3,4} and {5}.</figcaption>
</figure>

### What each linkage likes

Single linkage only needs one close pair to join two clusters, so it follows chains of nearby points and can find
long, curved shapes (it recovers the two rings perfectly in the program of 13.7). The same property is its
weakness: a thin line of noise points between two groups joins them, the **chaining effect**. Complete linkage and
Ward's method do the opposite: they keep clusters compact and fairly equal in diameter, and they cut long shapes into
pieces. Average linkage sits between.

Single linkage has a beautiful connection to graph algorithms. Build the complete graph on the points with edge
weights $d(a,b)$. The merges of single linkage are exactly the edges that [Kruskal's algorithm](../../graphs/kruskal.md)
adds when it builds a **minimum spanning tree**, in the same order, and cutting the dendrogram at height $h$ is the
same as deleting the spanning-tree edges longer than $h$ (Gower and Ross 1969). *Why:* Kruskal's algorithm takes
edges in increasing order and adds an edge when it joins two different components; single linkage merges the two
clusters with the shortest edge between them, which is the next edge Kruskal would accept. Both keep the components
in a [union-find](../../data-structures/union-find.md) structure. See
[Chapter 17 of the Algorithms book](../algorithms/17-Spanning-Trees-Flows-and-Matching.md) for the proofs about
spanning trees.

### Cost

The obvious implementation searches all pairs of clusters at every merge: $O(n^2)$ pairs, $n - 1$ merges, so
$O(n^3)$ time. The **Lance-Williams update** (Lance and Williams 1967) avoids recomputing cluster distances from
scratch: after merging $A$ and $B$ into $A \cup B$, the distance from any other cluster $C$ is a simple formula in
the old distances. For single linkage it is $\min(d(A,C), d(B,C))$, for complete linkage $\max$, and for average
linkage the size-weighted mean $\frac{|A|\,d(A,C) + |B|\,d(B,C)}{|A| + |B|}$. Our function `cut` keeps an
$n \times n$ matrix and updates one row and column per merge with these formulas, which makes each merge one pass
over the matrix. With priority queues, or with special algorithms (SLINK for single linkage, Sibson 1973), the time
drops to $O(n^2)$; the $n^2$ distances themselves are the limit, so hierarchical clustering is used for up to tens of
thousands of points, not millions.

## 13.6 Density-based clustering: DBSCAN

### Clusters as crowds

Look at a night photograph of a country from space. You see cities as bright patches of any shape, separated by dark
countryside, and a scatter of isolated lights that belong to no city. That is the density view of clustering: **a
cluster is a region where points are crowded, separated from other clusters by regions where they are sparse.**
Points in sparse regions are **noise** and belong to no cluster. Neither k-means nor Gaussian mixtures can say
"this point belongs nowhere".

**DBSCAN** ("density-based spatial clustering of applications with noise"), by Martin Ester, Hans-Peter Kriegel,
Jörg Sander and Xiaowei Xu (KDD 1996), makes this precise with two numbers chosen by the user: a radius
$\varepsilon$ and a count minPts.

- The **$\varepsilon$-neighbourhood** of a point is the set of data points within distance $\varepsilon$ of it,
  including itself.
- A **core point** has at least minPts points in its $\varepsilon$-neighbourhood: it sits inside a crowd.
- A **border point** is not a core point but lies in the neighbourhood of some core point: it sits at the edge of a
  crowd.
- A **noise point** is neither.

Two core points are in the same cluster if you can walk from one to the other in steps of length at most
$\varepsilon$, every step landing on a core point. Each border point joins the cluster of a core point near it.
(The paper calls this "density-reachable" and "density-connected".)

<figure class="mars-fig" markdown="0">
<svg viewBox="0 0 640 210" role="img" aria-label="A crowd of points. One core point has a dashed circle of radius epsilon containing five points. A border point at the edge has only two points in its circle but lies inside a core point's circle. A noise point far away has only itself in its circle.">
  <circle cx="185" cy="100" r="40" fill="#eea66f" fill-opacity="0.12" stroke="currentColor" stroke-width="1" stroke-dasharray="5 4"/>
  <circle cx="220" cy="110" r="40" fill="none" stroke="currentColor" stroke-width="0.8" stroke-dasharray="2 3"/>
  <circle cx="330" cy="60" r="40" fill="none" stroke="currentColor" stroke-width="0.8" stroke-dasharray="2 3"/>
  <line x1="185" y1="100" x2="225" y2="100" stroke="currentColor" stroke-width="1"/>
  <text x="200" y="94" font-size="12" fill="currentColor">ε</text>
  <g stroke="currentColor" stroke-width="0.8">
    <circle cx="120" cy="90" r="6" fill="#eea66f"/>
    <circle cx="140" cy="80" r="6" fill="#eea66f"/>
    <circle cx="150" cy="105" r="6" fill="#eea66f"/>
    <circle cx="165" cy="90" r="6" fill="#eea66f"/>
    <circle cx="135" cy="115" r="6" fill="#eea66f"/>
    <circle cx="170" cy="115" r="6" fill="#eea66f"/>
    <circle cx="185" cy="100" r="6" fill="#eea66f"/>
    <circle cx="220" cy="110" r="6" fill="#9cc9ea"/>
    <circle cx="330" cy="60" r="6" fill="#7ccf9a"/>
  </g>
  <g fill="currentColor" font-size="12">
    <text x="228" y="140">border</text>
    <text x="300" y="118">noise</text>
  </g>
  <g stroke="currentColor" stroke-width="0.8">
    <circle cx="410" cy="60" r="6" fill="#eea66f"/>
    <circle cx="410" cy="95" r="6" fill="#9cc9ea"/>
    <circle cx="410" cy="130" r="6" fill="#7ccf9a"/>
  </g>
  <g fill="currentColor" font-size="12">
    <text x="425" y="64">core: 5 or more points within ε</text>
    <text x="425" y="99">border: fewer, but near a core</text>
    <text x="425" y="134">noise: neither</text>
    <text x="400" y="180">here minPts = 5</text>
  </g>
</svg>
<figcaption>DBSCAN's three kinds of point. The orange point at the centre of the shaded circle has five points
(itself included) within ε, so it is a core point. The blue point has only two in its own circle but lies in a core
point's circle, so it is a border point. The green point is noise.</figcaption>
</figure>

### The algorithm

1. For every point, find its $\varepsilon$-neighbourhood and decide whether it is a core point.
2. Take any core point not yet in a cluster, start a new cluster with it, and grow the cluster: repeatedly take a
   point of the cluster that is a core point and add all of its neighbours. Neighbours that are core points are
   grown in turn; border points are added but not grown.
3. Repeat step 2 until every core point is in a cluster. Points never added are noise.

Step 2 is exactly a graph search ([breadth-first](../../graphs/bfs.md) or [depth-first](../../graphs/dfs.md)) in the
graph whose vertices are the points and whose edges join points within $\varepsilon$, started only from and through
core points; our code uses a stack, so it is depth-first. Each cluster of core points is a connected component of
the graph restricted to core points, so **the clusters do not depend on the order** in which points are visited.
Only a border point near two clusters can go either way, depending on which reaches it first; that is the one
order-dependence in DBSCAN, and it rarely matters.

**Cost.** The search itself touches each neighbourhood once. Finding neighbourhoods by comparing all pairs costs
$O(n^2)$, which is what our code does. With a spatial index (a k-d tree, [Chapter 9](09-Nearest-Neighbours-and-Kernels.md))
each query is fast in low dimensions, and the original paper argues that with such an index (an R*-tree) the
average run time is $O(n \log n)$; in the worst case, and in high dimensions, it is still quadratic.

### Choosing the two numbers

minPts sets how crowded a crowd must be. A common rule of thumb is minPts of at least the dimension plus one, often
twice the dimension, larger for noisy data. For $\varepsilon$, the paper suggests the **k-distance plot**: for each
point, compute the distance to its $k$-th nearest neighbour with $k = \text{minPts} - 1$, sort these distances, and
plot them. Points inside clusters have small values and noise points large ones; choose $\varepsilon$ near the
bend where the curve shoots up.

DBSCAN's real limit is that one $\varepsilon$ serves the whole data set: it cannot find a dense cluster and a sparse
cluster at the same time, because a radius loose enough for the sparse one merges things in the dense one. We met
this in writing the program: the first version put 150 points on each of two rings of radii 1 and 3, so the outer
ring was three times sparser, and DBSCAN with $\varepsilon = 0.5$ broke it into six pieces. With equal density (100
points on the inner ring and 300 on the outer) it finds both rings exactly. **OPTICS** (Ankerst, Breunig, Kriegel and
Sander 1999) and **HDBSCAN** (Campello, Moulavi and Sander 2013) remove the single radius by, in effect, running
DBSCAN at all radii at once and building a hierarchy of density clusters.

## 13.7 Spectral clustering

*Level: advanced.*

### The problem with rings

Here is a data set that breaks most of what we have built: two concentric rings. Any sensible person sees two
clusters, the inner ring and the outer ring. But the two rings have the **same mean**, the origin, so k-means cannot
separate them: any two centres split the plane by a straight line (the perpendicular bisector of the centres), and a
straight line cuts both rings in half. The program confirms it: agreement 0.532. Complete linkage does no better
(0.665). What the eye uses is not distance to a centre but **connectedness**: you can walk around the inner ring
in small steps without ever jumping to the outer ring.

<figure class="mars-fig" markdown="0">
<svg viewBox="0 0 640 260" role="img" aria-label="Two copies of two concentric rings of dots. Left, k-means with k equals 2: the dots are coloured by a vertical line through the centre, so each colour takes half of each ring. Right, spectral clustering: the inner ring is one colour and the outer ring another.">
  <circle cx="193.8" cy="115.9" r="5" fill="#9cc9ea" stroke="currentColor" stroke-width="0.8"/>
  <circle cx="184.7" cy="100.3" r="5" fill="#9cc9ea" stroke="currentColor" stroke-width="0.8"/>
  <circle cx="169.1" cy="91.2" r="5" fill="#9cc9ea" stroke="currentColor" stroke-width="0.8"/>
  <circle cx="150.9" cy="91.2" r="5" fill="#eea66f" stroke="currentColor" stroke-width="0.8"/>
  <circle cx="135.3" cy="100.3" r="5" fill="#eea66f" stroke="currentColor" stroke-width="0.8"/>
  <circle cx="126.2" cy="115.9" r="5" fill="#eea66f" stroke="currentColor" stroke-width="0.8"/>
  <circle cx="126.2" cy="134.1" r="5" fill="#eea66f" stroke="currentColor" stroke-width="0.8"/>
  <circle cx="135.3" cy="149.7" r="5" fill="#eea66f" stroke="currentColor" stroke-width="0.8"/>
  <circle cx="150.9" cy="158.8" r="5" fill="#eea66f" stroke="currentColor" stroke-width="0.8"/>
  <circle cx="169.1" cy="158.8" r="5" fill="#9cc9ea" stroke="currentColor" stroke-width="0.8"/>
  <circle cx="184.7" cy="149.7" r="5" fill="#9cc9ea" stroke="currentColor" stroke-width="0.8"/>
  <circle cx="193.8" cy="134.1" r="5" fill="#9cc9ea" stroke="currentColor" stroke-width="0.8"/>
  <circle cx="254.5" cy="115.1" r="5" fill="#9cc9ea" stroke="currentColor" stroke-width="0.8"/>
  <circle cx="250.4" cy="95.6" r="5" fill="#9cc9ea" stroke="currentColor" stroke-width="0.8"/>
  <circle cx="242.3" cy="77.5" r="5" fill="#9cc9ea" stroke="currentColor" stroke-width="0.8"/>
  <circle cx="230.6" cy="61.4" r="5" fill="#9cc9ea" stroke="currentColor" stroke-width="0.8"/>
  <circle cx="215.8" cy="48.1" r="5" fill="#9cc9ea" stroke="currentColor" stroke-width="0.8"/>
  <circle cx="198.6" cy="38.2" r="5" fill="#9cc9ea" stroke="currentColor" stroke-width="0.8"/>
  <circle cx="179.8" cy="32.1" r="5" fill="#9cc9ea" stroke="currentColor" stroke-width="0.8"/>
  <circle cx="160.0" cy="30.0" r="5" fill="#9cc9ea" stroke="currentColor" stroke-width="0.8"/>
  <circle cx="140.2" cy="32.1" r="5" fill="#eea66f" stroke="currentColor" stroke-width="0.8"/>
  <circle cx="121.4" cy="38.2" r="5" fill="#eea66f" stroke="currentColor" stroke-width="0.8"/>
  <circle cx="104.2" cy="48.1" r="5" fill="#eea66f" stroke="currentColor" stroke-width="0.8"/>
  <circle cx="89.4" cy="61.4" r="5" fill="#eea66f" stroke="currentColor" stroke-width="0.8"/>
  <circle cx="77.7" cy="77.5" r="5" fill="#eea66f" stroke="currentColor" stroke-width="0.8"/>
  <circle cx="69.6" cy="95.6" r="5" fill="#eea66f" stroke="currentColor" stroke-width="0.8"/>
  <circle cx="65.5" cy="115.1" r="5" fill="#eea66f" stroke="currentColor" stroke-width="0.8"/>
  <circle cx="65.5" cy="134.9" r="5" fill="#eea66f" stroke="currentColor" stroke-width="0.8"/>
  <circle cx="69.6" cy="154.4" r="5" fill="#eea66f" stroke="currentColor" stroke-width="0.8"/>
  <circle cx="77.7" cy="172.5" r="5" fill="#eea66f" stroke="currentColor" stroke-width="0.8"/>
  <circle cx="89.4" cy="188.6" r="5" fill="#eea66f" stroke="currentColor" stroke-width="0.8"/>
  <circle cx="104.2" cy="201.9" r="5" fill="#eea66f" stroke="currentColor" stroke-width="0.8"/>
  <circle cx="121.4" cy="211.8" r="5" fill="#eea66f" stroke="currentColor" stroke-width="0.8"/>
  <circle cx="140.2" cy="217.9" r="5" fill="#eea66f" stroke="currentColor" stroke-width="0.8"/>
  <circle cx="160.0" cy="220.0" r="5" fill="#eea66f" stroke="currentColor" stroke-width="0.8"/>
  <circle cx="179.8" cy="217.9" r="5" fill="#9cc9ea" stroke="currentColor" stroke-width="0.8"/>
  <circle cx="198.6" cy="211.8" r="5" fill="#9cc9ea" stroke="currentColor" stroke-width="0.8"/>
  <circle cx="215.8" cy="201.9" r="5" fill="#9cc9ea" stroke="currentColor" stroke-width="0.8"/>
  <circle cx="230.6" cy="188.6" r="5" fill="#9cc9ea" stroke="currentColor" stroke-width="0.8"/>
  <circle cx="242.3" cy="172.5" r="5" fill="#9cc9ea" stroke="currentColor" stroke-width="0.8"/>
  <circle cx="250.4" cy="154.4" r="5" fill="#9cc9ea" stroke="currentColor" stroke-width="0.8"/>
  <circle cx="254.5" cy="134.9" r="5" fill="#9cc9ea" stroke="currentColor" stroke-width="0.8"/>
  <circle cx="513.8" cy="115.9" r="5" fill="#7ccf9a" stroke="currentColor" stroke-width="0.8"/>
  <circle cx="504.7" cy="100.3" r="5" fill="#7ccf9a" stroke="currentColor" stroke-width="0.8"/>
  <circle cx="489.1" cy="91.2" r="5" fill="#7ccf9a" stroke="currentColor" stroke-width="0.8"/>
  <circle cx="470.9" cy="91.2" r="5" fill="#7ccf9a" stroke="currentColor" stroke-width="0.8"/>
  <circle cx="455.3" cy="100.3" r="5" fill="#7ccf9a" stroke="currentColor" stroke-width="0.8"/>
  <circle cx="446.2" cy="115.9" r="5" fill="#7ccf9a" stroke="currentColor" stroke-width="0.8"/>
  <circle cx="446.2" cy="134.1" r="5" fill="#7ccf9a" stroke="currentColor" stroke-width="0.8"/>
  <circle cx="455.3" cy="149.7" r="5" fill="#7ccf9a" stroke="currentColor" stroke-width="0.8"/>
  <circle cx="470.9" cy="158.8" r="5" fill="#7ccf9a" stroke="currentColor" stroke-width="0.8"/>
  <circle cx="489.1" cy="158.8" r="5" fill="#7ccf9a" stroke="currentColor" stroke-width="0.8"/>
  <circle cx="504.7" cy="149.7" r="5" fill="#7ccf9a" stroke="currentColor" stroke-width="0.8"/>
  <circle cx="513.8" cy="134.1" r="5" fill="#7ccf9a" stroke="currentColor" stroke-width="0.8"/>
  <circle cx="574.5" cy="115.1" r="5" fill="#9cc9ea" stroke="currentColor" stroke-width="0.8"/>
  <circle cx="570.4" cy="95.6" r="5" fill="#9cc9ea" stroke="currentColor" stroke-width="0.8"/>
  <circle cx="562.3" cy="77.5" r="5" fill="#9cc9ea" stroke="currentColor" stroke-width="0.8"/>
  <circle cx="550.6" cy="61.4" r="5" fill="#9cc9ea" stroke="currentColor" stroke-width="0.8"/>
  <circle cx="535.8" cy="48.1" r="5" fill="#9cc9ea" stroke="currentColor" stroke-width="0.8"/>
  <circle cx="518.6" cy="38.2" r="5" fill="#9cc9ea" stroke="currentColor" stroke-width="0.8"/>
  <circle cx="499.8" cy="32.1" r="5" fill="#9cc9ea" stroke="currentColor" stroke-width="0.8"/>
  <circle cx="480.0" cy="30.0" r="5" fill="#9cc9ea" stroke="currentColor" stroke-width="0.8"/>
  <circle cx="460.2" cy="32.1" r="5" fill="#9cc9ea" stroke="currentColor" stroke-width="0.8"/>
  <circle cx="441.4" cy="38.2" r="5" fill="#9cc9ea" stroke="currentColor" stroke-width="0.8"/>
  <circle cx="424.2" cy="48.1" r="5" fill="#9cc9ea" stroke="currentColor" stroke-width="0.8"/>
  <circle cx="409.4" cy="61.4" r="5" fill="#9cc9ea" stroke="currentColor" stroke-width="0.8"/>
  <circle cx="397.7" cy="77.5" r="5" fill="#9cc9ea" stroke="currentColor" stroke-width="0.8"/>
  <circle cx="389.6" cy="95.6" r="5" fill="#9cc9ea" stroke="currentColor" stroke-width="0.8"/>
  <circle cx="385.5" cy="115.1" r="5" fill="#9cc9ea" stroke="currentColor" stroke-width="0.8"/>
  <circle cx="385.5" cy="134.9" r="5" fill="#9cc9ea" stroke="currentColor" stroke-width="0.8"/>
  <circle cx="389.6" cy="154.4" r="5" fill="#9cc9ea" stroke="currentColor" stroke-width="0.8"/>
  <circle cx="397.7" cy="172.5" r="5" fill="#9cc9ea" stroke="currentColor" stroke-width="0.8"/>
  <circle cx="409.4" cy="188.6" r="5" fill="#9cc9ea" stroke="currentColor" stroke-width="0.8"/>
  <circle cx="424.2" cy="201.9" r="5" fill="#9cc9ea" stroke="currentColor" stroke-width="0.8"/>
  <circle cx="441.4" cy="211.8" r="5" fill="#9cc9ea" stroke="currentColor" stroke-width="0.8"/>
  <circle cx="460.2" cy="217.9" r="5" fill="#9cc9ea" stroke="currentColor" stroke-width="0.8"/>
  <circle cx="480.0" cy="220.0" r="5" fill="#9cc9ea" stroke="currentColor" stroke-width="0.8"/>
  <circle cx="499.8" cy="217.9" r="5" fill="#9cc9ea" stroke="currentColor" stroke-width="0.8"/>
  <circle cx="518.6" cy="211.8" r="5" fill="#9cc9ea" stroke="currentColor" stroke-width="0.8"/>
  <circle cx="535.8" cy="201.9" r="5" fill="#9cc9ea" stroke="currentColor" stroke-width="0.8"/>
  <circle cx="550.6" cy="188.6" r="5" fill="#9cc9ea" stroke="currentColor" stroke-width="0.8"/>
  <circle cx="562.3" cy="172.5" r="5" fill="#9cc9ea" stroke="currentColor" stroke-width="0.8"/>
  <circle cx="570.4" cy="154.4" r="5" fill="#9cc9ea" stroke="currentColor" stroke-width="0.8"/>
  <circle cx="574.5" cy="134.9" r="5" fill="#9cc9ea" stroke="currentColor" stroke-width="0.8"/>
  <g fill="currentColor" font-size="13" text-anchor="middle">
    <text x="160" y="250">k-means: a straight cut through both rings</text>
    <text x="480" y="250">spectral: one cluster per ring</text>
  </g>
</svg>
<figcaption>Why k-means fails on rings. Two centres can only split the plane with a straight line (left). Spectral
clustering uses who is near whom, a graph, and finds the two connected pieces (right).</figcaption>
</figure>

### From points to a graph

Spectral clustering turns the data into a **similarity graph**. Every point is a vertex. Every pair $i, j$ gets an
edge with weight $w_{ij}$ that is large when the points are close and tiny when they are far, usually the Gaussian
similarity

$$
w_{ij} = \exp\!\Big(-\frac{\|x_i - x_j\|^2}{2\sigma^2}\Big), \qquad w_{ii} = 0,
$$

where the **scale** $\sigma$ says what counts as "near" (in the program, $\sigma = 0.3$). Other choices connect each
point to its $k$ nearest neighbours only. The weights form a symmetric matrix $W$. The **degree** of vertex $i$ is
$d_i = \sum_j w_{ij}$, and $D$ is the diagonal matrix of degrees.

A good clustering of the graph cuts few, light edges between clusters. For a split into a set $A$ and its complement
$\bar{A}$, the **cut** is $\mathrm{cut}(A, \bar{A}) = \sum_{i \in A, j \in \bar{A}} w_{ij}$. Minimising the cut alone
tends to chop off a single point, so one normalises by the size of each side. Jianbo Shi and Jitendra Malik's
**normalized cut** (2000), proposed for segmenting images, is

$$
\mathrm{Ncut}(A, \bar{A}) = \frac{\mathrm{cut}(A, \bar{A})}{\mathrm{vol}(A)} + \frac{\mathrm{cut}(A, \bar{A})}{\mathrm{vol}(\bar{A})},
\qquad \mathrm{vol}(A) = \sum_{i \in A} d_i .
$$

Minimising Ncut exactly is NP-hard (shown in the same paper). Spectral clustering solves a **relaxation**: a
continuous version of the problem that linear algebra can solve exactly.

### The graph Laplacian

The key object is the **graph Laplacian** $L = D - W$. Its most important property is a formula for its quadratic
form. For any vector $f$ with one number $f_i$ per vertex,

$$
f^\top L f = \frac{1}{2} \sum_{i,j} w_{ij} (f_i - f_j)^2 .
$$

*Proof.* $f^\top L f = \sum_i d_i f_i^2 - \sum_{i,j} w_{ij} f_i f_j$. Write
$\sum_i d_i f_i^2 = \sum_{i,j} w_{ij} f_i^2 = \tfrac12 \sum_{i,j} w_{ij}(f_i^2 + f_j^2)$, using the symmetry of $W$.
Then $f^\top L f = \tfrac12 \sum_{i,j} w_{ij}(f_i^2 - 2 f_i f_j + f_j^2)$, which is the claim. $\square$

So $f^\top L f$ is small when $f$ changes little across heavy edges: a vector that is nearly constant on each
tightly connected piece. Three consequences follow at once.

1. $L$ is **positive semidefinite** (the sum of squares is never negative), so its eigenvalues are real and
   $0 = \lambda_1 \le \lambda_2 \le \dots \le \lambda_n$.
2. The constant vector $\mathbf{1}$ has $L\mathbf{1} = D\mathbf{1} - W\mathbf{1} = 0$, so 0 is always an eigenvalue.
3. **Theorem.** The number of eigenvalues equal to 0 is the number of connected components of the graph (counting
   only edges with $w_{ij} > 0$), and the eigenvectors for eigenvalue 0 are spanned by the indicator vectors of the
   components.

*Proof of 3.* If $Lf = 0$ then $f^\top L f = 0$, so every term $w_{ij}(f_i - f_j)^2$ is zero: $f_i = f_j$ whenever
$i$ and $j$ are joined by an edge, hence $f$ is constant on each connected component. Conversely, the indicator
vector of a component (1 on its vertices, 0 elsewhere) makes every term zero, because an edge never joins a vertex
inside the component to one outside. So the null space of $L$ is exactly the span of the $c$ component indicators,
which are linearly independent (they have disjoint supports), and its dimension is $c$. $\square$

Here is the insight. If the similarity graph were exactly disconnected into $k$ pieces, the $k$ eigenvectors with
eigenvalue 0 would be (combinations of) the piece indicators, and every point in one piece would have the same
row in the $n \times k$ matrix of those eigenvectors. Clustering those rows would be trivial. Real data gives a
graph that is **nearly** disconnected: the Gaussian weights between the rings are tiny but not zero. Then the $k$
smallest eigenvalues are nearly zero and, by perturbation theory for eigenvectors (the Davis-Kahan theorem), the
eigenvectors are close to piece indicators. The rows still form $k$ tight, well-separated groups, which even
k-means can find.

The connection to Ncut: for $k = 2$, minimising Ncut over vectors $f$ restricted to two values is the same as
minimising $f^\top L f / f^\top D f$ over those vectors. Dropping the two-value restriction leaves a Rayleigh
quotient, whose minimum over vectors orthogonal (in the $D$ inner product) to the constant vector is the second
smallest eigenvalue of the generalised problem $Lf = \lambda D f$, attained at its eigenvector. Rounding that
eigenvector back to two values (by sign, or by k-means) gives the clustering.

### The algorithm (Ng, Jordan and Weiss)

The version in our program is from Andrew Ng, Michael Jordan and Yair Weiss, "On Spectral Clustering: Analysis and an
Algorithm" (NIPS 2001):

1. Build $W$ with the Gaussian similarity and compute degrees $d_i$.
2. Form the **normalised Laplacian** $L_{\text{sym}} = I - D^{-1/2} W D^{-1/2}$. (Same theory as $L$, with each vertex
   weighted by its degree, which matches Ncut.)
3. Compute the eigenvectors of the $k$ smallest eigenvalues and put them as columns of an $n \times k$ matrix $U$.
4. Scale each row of $U$ to length 1.
5. Run k-means on the $n$ rows of $U$, and give point $i$ the cluster of row $i$.

The eigen-decomposition of a dense $n \times n$ matrix costs $O(n^3)$, which is fine for a few thousand points.
Large problems use sparse nearest-neighbour graphs and iterative eigensolvers (Lanczos methods) that compute only the
few eigenvectors needed.

### The program

```python
--8<-- "books/machine-learning/ch13_hier_dbscan_spectral.py"
```

```
1. Six points, the merge order (cluster ids 6, 7, ... are new clusters)
  single:
    merge 0 + 1 at height  1.000 -> [0, 1]
    merge 3 + 4 at height  1.000 -> [3, 4]
    merge 2 + 6 at height  1.500 -> [0, 1, 2]
    merge 7 + 8 at height  4.000 -> [0, 1, 2, 3, 4]
    merge 5 + 9 at height  4.031 -> [0, 1, 2, 3, 4, 5]
  complete:
    merge 0 + 1 at height  1.000 -> [0, 1]
    merge 3 + 4 at height  1.000 -> [3, 4]
    merge 2 + 6 at height  1.803 -> [0, 1, 2]
    merge 5 + 7 at height  4.031 -> [3, 4, 5]
    merge 8 + 9 at height  9.055 -> [0, 1, 2, 3, 4, 5]
  average:
    merge 0 + 1 at height  1.000 -> [0, 1]
    merge 3 + 4 at height  1.000 -> [3, 4]
    merge 2 + 6 at height  1.651 -> [0, 1, 2]
    merge 5 + 7 at height  4.031 -> [3, 4, 5]
    merge 8 + 9 at height  6.061 -> [0, 1, 2, 3, 4, 5]

2. Two rings (100 + 300 points): agreement with the true rings
  k-means, k = 2:              0.532
  complete linkage, 2 clusters: 0.665
  single linkage, 2 clusters:   1.000
  DBSCAN eps 0.5, minPts 5:     clusters 2, noise 0, core 400, agreement 1.000
  spectral, sigma 0.3:          1.000;  smallest eigenvalues [0.0, 0.0, 0.0029, 0.0046]

3. DBSCAN finds noise: the rings plus 20 scattered points
  clusters 2, points labelled noise 12
```

On the rings, spectral clustering gets every point right. The printed eigenvalues tell the story: the two smallest
are 0 to four decimals (the graph is nearly two separate pieces, one per ring) and the third, 0.0029, is already
clearly larger. A gap after the $k$-th eigenvalue (the **eigengap**) is itself a hint for choosing $k$. Single
linkage and DBSCAN also solve the rings, because they too follow connectedness; k-means and complete linkage do not.
Part 3 adds 20 random points: DBSCAN still finds the two rings and labels 12 of the scattered points as noise (the
other 8 happen to fall within $\varepsilon$ of a ring and join its cluster).

The scale $\sigma$ matters. Too small, and the graph falls apart into many tiny pieces; too large, and every point is
similar to every other, so the rings merge. This is the same choice as DBSCAN's $\varepsilon$ and kernel bandwidths
in [Chapter 9](09-Nearest-Neighbours-and-Kernels.md), and there is no universal rule. Ulrike von Luxburg's "A Tutorial
on Spectral Clustering" (2007) discusses the choices and the theory in depth.

### Looking back

A summary of what to try, honestly stated:

- Numeric data, roughly round groups, many points: **k-means** with k-means++ and several restarts. It is the
  default for a reason.
- You want probabilities, or the groups are ellipses of different shapes: a **Gaussian mixture** fitted by EM.
- You want a hierarchy, or a picture of the structure at all scales, and $n$ is moderate: **hierarchical
  clustering** with Ward or average linkage (single linkage for chain-like shapes, if noise is low).
- Arbitrary shapes, noise to be flagged, unknown $k$: **DBSCAN** or HDBSCAN.
- Shapes defined by connectedness, moderate $n$: **spectral clustering**.

**In practice:** scikit-learn has all of these (`KMeans` with k-means++ by default, `GaussianMixture`,
`AgglomerativeClustering`, `DBSCAN`, `HDBSCAN`, `SpectralClustering`) and `silhouette_score`; SciPy's
`scipy.cluster.hierarchy` draws dendrograms. A Mars example of the honest kind: planetary scientists cluster
spectra from orbiters and rovers to find groups of similar minerals before naming them, and the clusters are then
checked against laboratory spectra, because a clustering is a suggestion, not a fact.

## Check yourself

??? question "1. Run Lloyd's algorithm by hand on the points 1, 2, 3, 8, 9, 10, 25 with $k = 2$ starting from the centres 5 and 25. Where does it stop?"

    Assignment with centres 5 and 25: every point from 1 to 10 is closer to 5 (10 is 5 away from 5 and 15 from 25),
    and 25 is closest to itself. Update: the first centre becomes $(1+2+3+8+9+10)/6 = 5.5$, the second stays 25.
    Assignment again: nothing changes (the midpoint of 5.5 and 25 is 15.25, and every point except 25 is below it),
    so the algorithm stops with groups {1, ..., 10} and {25} and
    $J = 4.5^2 + 3.5^2 + 2.5^2 + 2.5^2 + 3.5^2 + 4.5^2 = 77.5$, the best possible split. The start decides the result.

??? question "2. Prove that $\sum_{i \in S}\|x_i - \mu\|^2 = \sum_{i \in S}\|x_i - \bar{x}\|^2 + |S|\,\|\bar{x} - \mu\|^2$ and explain why it shows that the update step of k-means cannot increase $J$."

    Write $x_i - \mu = (x_i - \bar{x}) + (\bar{x} - \mu)$ and expand the squared norm:
    $\|x_i - \bar{x}\|^2 + 2(x_i - \bar{x})\cdot(\bar{x} - \mu) + \|\bar{x} - \mu\|^2$. Summing over $i \in S$, the
    middle term becomes $2(\bar{x} - \mu)\cdot\sum_{i}(x_i - \bar{x}) = 2(\bar{x}-\mu)\cdot 0 = 0$, since
    $\sum_i x_i = |S|\bar{x}$. The last term summed gives $|S|\,\|\bar{x} - \mu\|^2$. The right side is smallest when
    $\mu = \bar{x}$, so moving a centre from any old position $\mu$ to the mean of its points lowers that cluster's
    sum by exactly $|S|\,\|\bar{x} - \mu\|^2 \ge 0$.

??? question "3. Why does $J$ always decrease as $k$ grows (for the best clustering with each $k$)? What does that mean for choosing $k$?"

    Take the best clustering with $k$ centres and add one more centre placed exactly on some data point that is not
    already a centre. That point's term drops to 0 and no other term grows (every other point can keep its old
    centre). So the best $J$ with $k + 1$ centres is at most the best with $k$, and strictly less unless every point
    already sits on a centre. Hence minimising $J$ over $k$ always picks $k = n$; $k$ must be chosen by a criterion
    that trades fit against the number of clusters, such as the elbow, the silhouette, the gap statistic or BIC.

??? question "4. Compute the silhouette of the point 8 in the clustering {1, 2, 3}, {8, 9, 10, 25}."

    Own cluster: $a = (1 + 2 + 17)/3 = 20/3 \approx 6.67$. Other cluster: $b = (7 + 6 + 5)/3 = 6$. So
    $s = (6 - 6.67)/6.67 = -0.1$. The point 8 is, on average, closer to {1, 2, 3} than to its own cluster, which is
    stretched out by 25. A negative silhouette flags a badly placed point.

??? question "5. In k-means++, the current centre is at 0 and the other data points are at 1, 2 and 10. What is the probability that each is chosen as the second centre?"

    $D^2$ values are 1, 4 and 100, total 105. So the probabilities are $1/105 \approx 0.0095$, $4/105 \approx 0.038$
    and $100/105 \approx 0.952$ (the point 0 itself has $D = 0$ and cannot be chosen again). The far point is almost
    surely chosen, which is right if it is the start of another group and the reason k-means++ can be pulled by a
    lone outlier.

??? question "6. Show that k-means is a limit of EM for Gaussian mixtures: take equal weights and covariances $\sigma^2 I$ for all groups, and let $\sigma \to 0$. What do the responsibilities become?"

    With equal weights and covariances, the normalising constants cancel and
    $r_{ij} = e^{-\|x_i - \mu_j\|^2/2\sigma^2} / \sum_l e^{-\|x_i - \mu_l\|^2/2\sigma^2}$. Divide top and bottom by the
    term of the nearest centre $l^*$: every other term becomes $e^{-(\|x_i-\mu_l\|^2 - \|x_i - \mu_{l^*}\|^2)/2\sigma^2}$,
    whose exponent goes to $-\infty$ as $\sigma \to 0$ (when the nearest centre is unique). So $r_{ij} \to 1$ for the
    nearest centre and 0 for the others: the E step becomes the assignment step, and the M step for $\mu_j$
    becomes the mean of the assigned points, the update step.

??? question "7. One EM run for a mixture gives log-likelihood $-1520.3$ and another, from a different start, gives $-1498.7$. Can the first run's next iteration produce $-1530$? Which run do you keep?"

    No: by the theorem, an EM iteration never lowers the log-likelihood (up to rounding), so any later value of the
    first run is at least $-1520.3$. If you ever see the log-likelihood fall, the code has a bug (a common one is
    computing the log-likelihood with parameters from the wrong step). Keep the run with the higher log-likelihood,
    $-1498.7$; both are local maxima and EM does not know which is global.

??? question "8. Write the code: Ward's method merges the two clusters whose merge increases $J$ the least. Show that merging $A$ and $B$ increases $J$ by $\frac{|A||B|}{|A|+|B|}\|\bar{a} - \bar{b}\|^2$, and write a function that performs Ward clustering of a small data set into $k$ clusters."

    Let $m$ be the mean of $A \cup B$: $m = (|A|\bar{a} + |B|\bar{b})/(|A|+|B|)$. By the identity of exercise 2, the
    sum of squares of $A \cup B$ around $m$ is that of $A$ around $\bar{a}$ plus $|A|\,\|\bar{a} - m\|^2$, plus the same
    for $B$. Now $\bar{a} - m = \frac{|B|}{|A|+|B|}(\bar{a} - \bar{b})$ and $\bar{b} - m = \frac{|A|}{|A|+|B|}(\bar{b} - \bar{a})$,
    so the increase is $\frac{|A||B|^2 + |B||A|^2}{(|A|+|B|)^2}\|\bar{a}-\bar{b}\|^2 = \frac{|A||B|}{|A|+|B|}\|\bar{a}-\bar{b}\|^2$.

    ```python
    import numpy as np

    def ward(X, k):
        clusters = [[i] for i in range(len(X))]
        while len(clusters) > k:
            best = None
            for a in range(len(clusters)):
                for b in range(a + 1, len(clusters)):
                    A, B = X[clusters[a]], X[clusters[b]]
                    cost = len(A) * len(B) / (len(A) + len(B)) * ((A.mean(0) - B.mean(0)) ** 2).sum()
                    if best is None or cost < best[0]:
                        best = (cost, a, b)
            _, a, b = best
            clusters[a] += clusters.pop(b)
        return clusters

    pts = np.array([[0, 0], [1, 0], [0, 1.5], [5, 0], [5, 1], [9, 0.5]])
    print(ward(pts, 3))   # [[0, 1, 2], [3, 4], [5]]
    print(ward(pts, 2))   # [[0, 1, 2], [3, 4, 5]]
    ```

??? question "9. A data set has two dense blobs and one sparse, spread-out cluster. Explain what DBSCAN does with a small $\varepsilon$ and with a large one."

    With a small $\varepsilon$ the dense blobs are found, but points of the sparse cluster have too few neighbours to be
    core points, so the sparse cluster is labelled noise (or broken into fragments). With an $\varepsilon$ large enough
    to make the sparse cluster's points core points, the dense blobs' neighbourhoods are huge and, if the blobs are
    closer than about $\varepsilon$, they merge into one cluster. A single radius cannot serve both densities; OPTICS
    or HDBSCAN, which consider all radii, are designed for this case.

??? question "10. For the graph with three vertices and edges $w_{12} = 1$, $w_{23} = 1$, $w_{13} = 0$, write $L = D - W$, check that $L\mathbf{1} = 0$, and find the eigenvalues. What happens to them if you delete the edge between 2 and 3?"

    $D = \mathrm{diag}(1, 2, 1)$ and

    $$
    L = \begin{pmatrix} 1 & -1 & 0 \\ -1 & 2 & -1 \\ 0 & -1 & 1 \end{pmatrix}.
    $$

    Each row sums to 0, so $L\mathbf{1} = 0$. The eigenvalues of this path-graph Laplacian are 0, 1 and 3 (check:
    $(1, 0, -1)$ gives eigenvalue 1, $(1, -2, 1)$ gives 3; the trace is 4 = 0 + 1 + 3). One zero eigenvalue: one
    connected component. Deleting the edge 2-3 gives $D = \mathrm{diag}(1,1,0)$ and eigenvalues 0, 0, 2: two zero
    eigenvalues, because vertex 3 is now its own component; the null space is spanned by $(1,1,0)$ and $(0,0,1)$.

??? question "11. (Hard) Show that the normalised Laplacian $L_{\text{sym}} = I - D^{-1/2} W D^{-1/2}$ is positive semidefinite, and find a vector in its null space."

    For any $g$, put $f = D^{-1/2} g$. Then $g^\top L_{\text{sym}}\, g = g^\top D^{-1/2}(D - W)D^{-1/2} g = f^\top L f
    = \tfrac12 \sum_{i,j} w_{ij}(f_i - f_j)^2 \ge 0$, so $L_{\text{sym}}$ is positive semidefinite. The quadratic form is
    zero when $f$ is constant, that is $g = D^{1/2}\mathbf{1}$, the vector $(\sqrt{d_1}, \dots, \sqrt{d_n})$. Its null
    space vectors are therefore $D^{1/2}$ times component indicators, which is why the Ng-Jordan-Weiss algorithm
    normalises the rows of $U$: it removes the $\sqrt{d_i}$ factor so that all points of one component map to the
    same direction.

## What you learned

- Clustering finds groups in unlabelled data; what a "cluster" is depends on the distance, the scaling and the
  method's idea of a group, and Kleinberg proved no method satisfies every natural wish.
- k-means minimises the within-cluster sum of squares by alternating nearest-centre assignment and moving centres
  to means; $J$ never increases, so it always stops, but possibly at a poor local minimum.
- k-means++ picks starting centres by $D^2$ sampling and is within $8(\ln k + 2)$ of optimal in expectation.
- The elbow of $J$ against $k$ and the mean silhouette help choose $k$; both reflect a preference for compact groups.
- A Gaussian mixture is a model of how the data was made; EM alternates computing responsibilities and weighted
  refits, and it is coordinate ascent on a lower bound, so the likelihood never decreases.
- Hierarchical clustering gives a tree of merges; single linkage is the minimum spanning tree in disguise, complete
  and Ward linkages keep clusters compact.
- DBSCAN defines clusters as dense regions connected through core points and labels the rest as noise.
- Spectral clustering uses the graph Laplacian, whose zero eigenvalues count connected components, to find clusters
  defined by connectedness, like rings.

**Next:** [Chapter 14](14-Dimensionality-Reduction.md), which finds the few directions that matter in data with many
features, so that we can see it, compress it and cluster it.

## Further reading

- C. Bishop, *Pattern Recognition and Machine Learning*, 2006, chapter 9 (k-means, mixtures of Gaussians, EM and
  its general proof).
- T. Hastie, R. Tibshirani and J. Friedman, *The Elements of Statistical Learning*, 2nd ed., 2009, section 14.3
  (cluster analysis: k-means, hierarchical clustering, the gap statistic) and section 14.5.3 (spectral clustering).
- K. Murphy, *Probabilistic Machine Learning: An Introduction*, 2022, chapter 21 (clustering); and *Advanced
  Topics*, 2023, for EM and mixture models in general.
- S. Shalev-Shwartz and S. Ben-David, *Understanding Machine Learning*, 2014, chapter 22 (clustering, including
  k-means, spectral clustering and Kleinberg's impossibility theorem).
- S. Lloyd, "Least Squares Quantization in PCM", *IEEE Transactions on Information Theory*, 1982 (written in 1957).
- J. MacQueen, "Some Methods for Classification and Analysis of Multivariate Observations", *Proceedings of the
  Fifth Berkeley Symposium*, 1967.
- D. Arthur and S. Vassilvitskii, "k-means++: The Advantages of Careful Seeding", SODA 2007.
- A. Vattani, "k-means Requires Exponentially Many Iterations Even in the Plane", *Discrete and Computational
  Geometry*, 2011.
- P. Rousseeuw, "Silhouettes: A Graphical Aid to the Interpretation and Validation of Cluster Analysis", *Journal of
  Computational and Applied Mathematics*, 1987.
- A. Dempster, N. Laird and D. Rubin, "Maximum Likelihood from Incomplete Data via the EM Algorithm", *Journal of the
  Royal Statistical Society B*, 1977; C. F. J. Wu, "On the Convergence Properties of the EM Algorithm", *Annals of
  Statistics*, 1983; R. Neal and G. Hinton, "A View of the EM Algorithm that Justifies Incremental, Sparse, and Other
  Variants", in *Learning in Graphical Models*, 1998.
- J. Ward, "Hierarchical Grouping to Optimize an Objective Function", *Journal of the American Statistical
  Association*, 1963; J. Gower and G. Ross, "Minimum Spanning Trees and Single Linkage Cluster Analysis", *Applied
  Statistics*, 1969.
- M. Ester, H.-P. Kriegel, J. Sander and X. Xu, "A Density-Based Algorithm for Discovering Clusters in Large Spatial
  Databases with Noise", KDD 1996.
- J. Shi and J. Malik, "Normalized Cuts and Image Segmentation", *IEEE Transactions on Pattern Analysis and Machine
  Intelligence*, 2000; A. Ng, M. Jordan and Y. Weiss, "On Spectral Clustering: Analysis and an Algorithm", NIPS 2001;
  U. von Luxburg, "A Tutorial on Spectral Clustering", *Statistics and Computing*, 2007.
- J. Kleinberg, "An Impossibility Theorem for Clustering", NIPS 2002.
- On this site: the reference pages [Kruskal's algorithm](../../graphs/kruskal.md),
  [Union-find](../../data-structures/union-find.md), [Breadth-first search](../../graphs/bfs.md) and
  [Depth-first search](../../graphs/dfs.md); [Chapter 17 of the Algorithms book](../algorithms/17-Spanning-Trees-Flows-and-Matching.md)
  on minimum spanning trees; [Chapter 12](12-Probabilistic-Models.md) for maximum likelihood and
  [Chapter 20](20-Generative-Models.md) for the ELBO again; the linear algebra and probability books at
  [https://math.akadian.ca/books/](https://math.akadian.ca/books/).
