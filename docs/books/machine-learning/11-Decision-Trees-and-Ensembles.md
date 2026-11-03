# 11. Decision trees and ensembles

*A doctor deciding whether a patient needs a test, a bank deciding whether to approve a loan, a botanist naming a
plant with a field guide: all follow a chain of yes-or-no questions, each chosen in the light of the answers so far.
A decision tree learns such a chain from data. Trees are easy to read and fast to use, but a single tree is unstable:
change a few training points and the whole tree can change. This chapter builds trees from scratch, from the
impurity measures that choose each question to the pruning that stops them memorising, and then turns their
weakness into strength. Averaging many randomized trees gives random forests; adding trees one at a time, each
correcting the last, gives boosting. Boosted trees remain, on most tables of numbers and categories, the method to
beat.*

!!! abstract "In this chapter"
    **You will learn:**

    - how a tree partitions the input space, and how entropy, Gini impurity and information gain choose its questions
    - CART from scratch: greedy splitting in $O(dn\log n)$ per level, regression trees, cost-complexity pruning
    - bagging and random forests, the variance formula $\rho\sigma^2 + (1 - \rho)\sigma^2/B$, and out-of-bag error
    - AdaBoost with its training-error bound proved, and its reading as stagewise fitting of the exponential loss
    - gradient boosting as gradient descent in function space, built from scratch
    - the second-order leaf weights and split gain of XGBoost, derived, and why boosted trees win on tabular data
    - impurity and permutation importance, and the ways both can mislead

    **You need:** [Chapter 4](04-Linear-Regression.md) (squared error), [Chapter 5](05-Optimization.md) (gradient
    descent, Newton's method), [Chapter 6](06-Classification-and-Logistic-Regression.md) (log loss),
    [Chapter 7](07-Evaluating-Models.md) (validation) and [Chapter 8](08-Overfitting-and-Regularization.md) (bias and
    variance). The entropy of [Chapter 3](03-The-Math-Toolkit.md) section 3.7 helps.

    **Levels:** 11.1 and 11.2 are beginner to intermediate; 11.3 and 11.5 are intermediate; 11.4 and 11.6 are
    advanced; 11.7 is intermediate.

## 11.1 Trees as twenty questions; Gini impurity and entropy; information gain

In the parlour game Twenty Questions, one player thinks of an object and the other must identify it with yes-or-no
questions. Good players ask questions that split the remaining possibilities roughly in half ("is it alive?"), not
questions that are almost always answered the same way ("is it a giraffe?"). A decision tree is a learned strategy for
this game, played against the training data.

**What a tree is.** A **decision tree** is a binary tree (or, in some versions, a tree with more branches per node).
Each **internal node** holds a test on one feature, such as "is $x_3 \le 2.7$?" or "is Outlook = Sunny?". Each
**leaf** holds a prediction: a class (for classification) or a number (for regression). To predict for an input,
start at the **root**, follow the branch that matches the answer to each test, and output the leaf's value. The
**depth** of a tree is the length of its longest root-to-leaf path.

Geometrically, each test with a threshold on a numeric feature cuts the input space by a plane perpendicular to that
feature's axis. A tree therefore partitions the space into **axis-aligned boxes**, one per leaf, and predicts a
constant in each. That is both the strength of trees (any shape of boundary can be approximated by enough boxes) and
their characteristic weakness (a diagonal boundary becomes a staircase).

**A small table.** Here is the classic toy table used to teach tree learning: 14 days, four attributes, and whether
someone played tennis (from J. Ross Quinlan's 1986 paper "Induction of Decision Trees", in the form printed in
Tom Mitchell's *Machine Learning*, 1997, Table 3.2). It is typed into the program below. Nine days are "Yes", five
"No". Which question should the root ask?

### Measuring impurity

We want questions whose answers make the groups **purer**: closer to all one class. Several measures of impurity of
a group with class proportions $p_1, \dots, p_K$ are used.

- **Entropy**, from information theory ([Chapter 3](03-The-Math-Toolkit.md)):
  $H = -\sum_k p_k \log_2 p_k$, in bits, with $0 \log 0 = 0$. It is 0 for a pure group and largest, $\log_2 K$, when
  all classes are equally common. It is the average number of yes-or-no questions needed to identify the class of a
  random member, with an optimal code.
- **Gini impurity**: $G = 1 - \sum_k p_k^2 = \sum_k p_k (1 - p_k)$. It is the probability that two members drawn at
  random (with replacement) have different classes; equivalently, the error rate if you labelled each member by a
  random draw from the group's own class proportions.
- **Misclassification rate**: $1 - \max_k p_k$, the error of predicting the majority class.

For two classes with $p$ the fraction of class 1, these are $-p\log_2 p - (1-p)\log_2(1-p)$, $2p(1-p)$ and
$\min(p, 1-p)$. For the whole tennis table, $p = 9/14$:

$$
H = -\tfrac{9}{14}\log_2\tfrac{9}{14} - \tfrac{5}{14}\log_2\tfrac{5}{14} = 0.940, \qquad
G = 1 - \big(\tfrac{9}{14}\big)^2 - \big(\tfrac{5}{14}\big)^2 = 0.459.
$$

<figure class="mars-fig" markdown="0">
<svg viewBox="0 0 640 270" role="img" aria-label="Impurity of a two-class node against the fraction p of class 1, from 0 to 1: entropy rises to 1 at p = 0.5, Gini 2p(1-p) rises to 0.5, misclassification min(p, 1-p) is a tent with peak 0.5. Entropy and Gini are smooth and strictly concave; misclassification is straight on each side.">
  <g font-size="12" fill="currentColor" stroke="currentColor" text-anchor="middle">
    <line x1="80" y1="220" x2="560" y2="220" stroke-width="1"/><line x1="80" y1="220" x2="80" y2="40" stroke-width="1"/>
    <line x1="80" y1="220" x2="80" y2="225"/><text x="80" y="240" stroke="none">0</text>
    <line x1="200" y1="220" x2="200" y2="225"/><text x="200" y="240" stroke="none">0.25</text>
    <line x1="320" y1="220" x2="320" y2="225"/><text x="320" y="240" stroke="none">0.5</text>
    <line x1="440" y1="220" x2="440" y2="225"/><text x="440" y="240" stroke="none">0.75</text>
    <line x1="560" y1="220" x2="560" y2="225"/><text x="560" y="240" stroke="none">1</text>
    <line x1="75" y1="135" x2="80" y2="135"/><text x="70" y="139" stroke="none" text-anchor="end">0.5</text>
    <line x1="75" y1="50" x2="80" y2="50"/><text x="70" y="54" stroke="none" text-anchor="end">1.0</text>
    <text x="320" y="262" stroke="none">p, the fraction of class 1 in the node</text>
  </g>
  <g fill="none" stroke-width="3">
    <polyline stroke="#eea66f" points="80,220 80.5,218.1 88.6,198.0 96.7,182.9 104.8,170.1 113.0,158.6 121.1,148.3 129.2,138.9 137.3,130.3 145.4,122.3 153.6,115.0 161.7,108.1 169.8,101.8 177.9,95.9 186.0,90.5 194.2,85.5 202.3,80.8 210.4,76.6 218.5,72.6 226.6,69.1 234.7,65.8 242.9,62.9 251.0,60.3 259.1,58.0 267.2,56.0 275.3,54.3 283.5,52.9 291.6,51.7 299.7,50.9 307.8,50.3 315.9,50.0 324.1,50.0 332.2,50.3 340.3,50.9 348.4,51.7 356.5,52.9 364.7,54.3 372.8,56.0 380.9,58.0 389.0,60.3 397.1,62.9 405.3,65.8 413.4,69.1 421.5,72.6 429.6,76.6 437.7,80.8 445.8,85.5 454.0,90.5 462.1,95.9 470.2,101.8 478.3,108.1 486.4,115.0 494.6,122.3 502.7,130.3 510.8,138.9 518.9,148.3 527.0,158.6 535.2,170.1 543.3,182.9 551.4,198.0 559.5,218.1 560,220"/>
    <polyline stroke="#7ccf9a" points="80.0,220.0 92.0,211.7 104.0,203.8 116.0,196.4 128.0,189.4 140.0,182.8 152.0,176.7 164.0,170.9 176.0,165.6 188.0,160.7 200.0,156.2 212.0,152.2 224.0,148.6 236.0,145.4 248.0,142.7 260.0,140.3 272.0,138.4 284.0,136.9 296.0,135.8 308.0,135.2 320.0,135.0 332.0,135.2 344.0,135.8 356.0,136.9 368.0,138.4 380.0,140.3 392.0,142.7 404.0,145.4 416.0,148.6 428.0,152.2 440.0,156.2 452.0,160.7 464.0,165.6 476.0,170.9 488.0,176.7 500.0,182.8 512.0,189.4 524.0,196.4 536.0,203.9 548.0,211.7 560.0,220.0"/>
    <polyline stroke="#9cc9ea" points="80,220 320,135.0 560,220"/>
  </g>
  <g font-size="13" fill="currentColor">
    <text x="450" y="62">entropy (bits)</text>
    <text x="420" y="140">Gini 2p(1 - p)</text>
    <text x="230" y="208">misclassification min(p, 1 - p)</text>
  </g>
</svg>
<figcaption>Three impurity measures for a two-class node. All are zero for a pure node and largest at p = 1/2.
Entropy and Gini are strictly concave (curved everywhere); the misclassification rate is straight on each side, which
makes it a poor guide for growing trees.</figcaption>
</figure>

### Information gain

A split sends a parent group $S$ into children $S_1, \dots, S_m$. The **gain** of the split is the parent's
impurity minus the size-weighted average impurity of the children:

$$
\mathrm{Gain}(S) = I(S) - \sum_{j=1}^m \frac{|S_j|}{|S|}\, I(S_j).
$$

With entropy as $I$ this is the **information gain**: the expected reduction in uncertainty about the class from
learning the answer, which is exactly the **mutual information** between the answer and the class.

**By hand: Outlook.** Splitting the tennis table on Outlook gives Sunny (2 Yes, 3 No), Overcast (4 Yes, 0 No) and
Rain (3 Yes, 2 No). The Overcast group is pure, entropy 0. The other two have entropy
$H(2/5) = -0.4\log_2 0.4 - 0.6\log_2 0.6 = 0.971$. So

$$
\mathrm{Gain}(\text{Outlook}) = 0.940 - \tfrac{5}{14}(0.971) - \tfrac{4}{14}(0) - \tfrac{5}{14}(0.971) = 0.247.
$$

The program computes the gain of every attribute, and then of every remaining attribute inside the Sunny and Rain
branches.

```python
--8<-- "books/machine-learning/ch11_impurity.py"
```

```
All 14 days: Counter({'Yes': 9, 'No': 5})  entropy 0.940  Gini 0.459

Splitting the whole table on each attribute
  attribute     info gain   Gini decrease   children (yes/no)
  Outlook           0.247           0.116   Overcast 4/0, Rain 3/2, Sunny 2/3
  Temperature       0.029           0.019   Cool 3/1, Hot 2/2, Mild 4/2
  Humidity          0.152           0.092   High 3/4, Normal 6/1
  Wind              0.048           0.031   Strong 3/3, Weak 6/2

Inside Outlook = Sunny (5 days):
  Temperature   info gain 0.571
  Humidity      info gain 0.971
  Wind          info gain 0.020
Inside Outlook = Rain (5 days):
  Temperature   info gain 0.020
  Humidity      info gain 0.020
  Wind          info gain 0.971

Impurity of a two-class node as a function of p = fraction of class 1
    p     entropy   Gini   misclassification
  0.0     0.000  0.000    0.000
  0.1     0.469  0.180    0.100
  0.2     0.722  0.320    0.200
  0.3     0.881  0.420    0.300
  0.4     0.971  0.480    0.400
  0.5     1.000  0.500    0.500
```

Outlook has the largest gain (0.247; textbooks often print 0.246 because they round intermediate values), so it goes
at the root, and the Overcast branch is already pure: a leaf "Yes". Inside Sunny, Humidity has gain 0.971, the whole
entropy of that branch, because it separates the Sunny days perfectly. Inside Rain, Wind does the same. The finished
tree has five leaves and classifies all 14 days correctly. Notice that Temperature is never used: the tree has
selected the relevant attributes by itself.

<figure class="mars-fig" markdown="0">
<svg viewBox="0 0 640 250" role="img" aria-label="The decision tree learned from the tennis table. The root asks Outlook. Sunny leads to a Humidity test: High gives No (0 yes, 3 no) and Normal gives Yes (2 yes, 0 no). Overcast leads directly to Yes (4 yes, 0 no). Rain leads to a Wind test: Strong gives No (0 yes, 2 no) and Weak gives Yes (3 yes, 0 no).">
  <g stroke="currentColor" stroke-width="1.3" fill="none">
    <line x1="320" y1="52" x2="140" y2="110"/>
    <line x1="320" y1="52" x2="320" y2="110"/>
    <line x1="320" y1="52" x2="500" y2="110"/>
    <line x1="140" y1="134" x2="75" y2="190"/>
    <line x1="140" y1="134" x2="205" y2="190"/>
    <line x1="500" y1="134" x2="435" y2="190"/>
    <line x1="500" y1="134" x2="565" y2="190"/>
    <rect x="265" y="28" width="110" height="26" rx="5" fill="#9cc9ea" fill-opacity="0.5"/>
    <rect x="85" y="110" width="110" height="26" rx="5" fill="#9cc9ea" fill-opacity="0.5"/>
    <rect x="445" y="110" width="110" height="26" rx="5" fill="#9cc9ea" fill-opacity="0.5"/>
    <rect x="275" y="110" width="90" height="40" rx="5" fill="#7ccf9a" fill-opacity="0.6"/>
    <rect x="30" y="190" width="90" height="40" rx="5" fill="#eea66f" fill-opacity="0.6"/>
    <rect x="160" y="190" width="90" height="40" rx="5" fill="#7ccf9a" fill-opacity="0.6"/>
    <rect x="390" y="190" width="90" height="40" rx="5" fill="#eea66f" fill-opacity="0.6"/>
    <rect x="520" y="190" width="90" height="40" rx="5" fill="#7ccf9a" fill-opacity="0.6"/>
  </g>
  <g font-size="12" fill="currentColor" text-anchor="middle">
    <text x="320" y="46">Outlook?</text>
    <text x="140" y="128">Humidity?</text>
    <text x="500" y="128">Wind?</text>
    <text x="210" y="78">Sunny</text>
    <text x="345" y="88">Overcast</text>
    <text x="432" y="78">Rain</text>
    <text x="320" y="127">Yes</text><text x="320" y="143">4 / 0</text>
    <text x="88" y="166">High</text>
    <text x="196" y="166">Normal</text>
    <text x="448" y="166">Strong</text>
    <text x="555" y="166">Weak</text>
    <text x="75" y="207">No</text><text x="75" y="223">0 / 3</text>
    <text x="205" y="207">Yes</text><text x="205" y="223">2 / 0</text>
    <text x="435" y="207">No</text><text x="435" y="223">0 / 2</text>
    <text x="565" y="207">Yes</text><text x="565" y="223">3 / 0</text>
    <text x="320" y="246">numbers under each leaf: days with Play = Yes / No</text>
  </g>
</svg>
<figcaption>The tree grown from the tennis table by choosing, at each node, the attribute with the largest
information gain. Five leaves, every training day classified correctly, and Temperature never asked.</figcaption>
</figure>

**Why not use the misclassification rate?** It seems the natural criterion, but it is too blunt. Take a parent with
400 points of each class and two candidate splits: A gives children (300, 100) and (100, 300); B gives (200, 400) and
(200, 0). Both make 200 errors if each child predicts its majority, so the misclassification rate cannot choose.
Gini prefers B ($0.333$ against $0.375$ for A), because B creates a pure child that needs no further work. Entropy
agrees. The deeper reason is concavity.

**Theorem.** If the impurity $I$ is a strictly concave function of the class proportions, every split has gain
$\ge 0$, with equality only when all children have the same class proportions as the parent.

*Proof.* The parent's proportions are the size-weighted average of the children's: $p(S) = \sum_j \frac{|S_j|}{|S|} p(S_j)$.
By Jensen's inequality for a concave function, $I\big(\sum_j w_j p_j\big) \ge \sum_j w_j I(p_j)$, with equality for a
strictly concave $I$ only when all the $p_j$ are equal. $\square$

Entropy and Gini are strictly concave; the misclassification rate is concave but piecewise linear, so many useful
splits have zero gain under it (any split in which every child keeps the parent's majority class). In practice Gini
and entropy almost always choose the same splits; CART uses Gini because it needs no logarithms.

**A bias to watch.** Information gain favours attributes with many values. An attribute like "Date", different on
every day, splits the table into 14 pure groups of one and has the maximal gain 0.940, yet it is useless for
predicting a new day. Quinlan's C4.5 corrects this with the **gain ratio** (gain divided by the entropy of the split
itself); CART avoids it by allowing only binary splits.

**History.** Tree-structured models have several origins: the AID program of James Morgan and John Sonquist (1963)
for survey data, Earl Hunt's Concept Learning System (1966) in psychology, J. Ross Quinlan's ID3 (1986) and C4.5
(1993) in machine learning, and the statistical CART methodology of Leo Breiman, Jerome Friedman, Richard Olshen and
Charles Stone (*Classification and Regression Trees*, 1984), whose rules for binary splits and pruning this chapter
follows.

## 11.2 Growing a tree from scratch (CART), pruning

How do we find the best tree? Finding the smallest tree consistent with the data is NP-complete (Laurent Hyafil and
Ronald Rivest, 1976), so every practical method is **greedy**: choose the best single split at the root, then recurse
on each side, never revisiting a decision. CART grows binary trees this way.

**Candidate splits.** For a numeric feature $x_f$, sort the $n$ points in the node by $x_f$. Any threshold between two
consecutive distinct values gives the same split as any other threshold in that gap, so there are at most $n - 1$
candidates; CART uses midpoints. For a categorical feature with $m$ values there are $2^{m-1} - 1$ ways to split the
values into two groups, but for two classes (and for regression) it suffices to sort the categories by their mean
response and try the $m - 1$ cuts in that order (a theorem in Breiman et al. 1984), so this case is fast too.

**Evaluating all thresholds in one sweep.** For classification with Gini, write $n_L$ and $n_R$ for the sizes of the
children and $c_{L,k}$, $c_{R,k}$ for their class counts. Then $n_L G_L = n_L - \sum_k c_{L,k}^2/n_L$, and similarly
on the right, so the cost of a split is $n_L G_L + n_R G_R$, a function of the running class counts. Sweeping the
sorted points from left to right and updating the counts gives the cost of every threshold in $O(nK)$ after the
$O(n\log n)$ sort. For regression the leaf predicts the mean, and the cost is the sum of squared errors, which
satisfies $\sum_i (y_i - \bar y)^2 = \sum_i y_i^2 - (\sum_i y_i)^2/n$: again a function of running sums. The function
`best_split` in the program does exactly this with cumulative sums.

**Why the mean.** In a regression leaf, the constant $c$ that minimises $\sum_i (y_i - c)^2$ is the mean: the
derivative $-2\sum_i (y_i - c)$ vanishes at $c = \bar y$, and the function is convex. (For absolute error it is the
median, exercise 9.)

**Cost of growing.** At one level of the tree the nodes hold disjoint sets of points, so the sorting and sweeping at
that level cost $O(dn\log n)$ in total over $d$ features. A tree of depth $D$ costs $O(Ddn\log n)$; with balanced
splits $D = O(\log n)$. Prediction costs $O(D)$ comparisons.

**When to stop.** A tree grown until every leaf is pure fits the training data perfectly, noise included. Stopping
rules (maximum depth, minimum points per leaf, minimum gain) are simple but short-sighted: a split with small gain
may enable very good splits below it (the XOR pattern is the classic case: neither feature alone helps, both together
are perfect). CART's answer is to grow a large tree and then **prune** it back.

### Cost-complexity pruning

For a tree $T$ let $R(T)$ be its training error (the fraction of training points misclassified) and $|T|$ its number
of leaves. For a penalty $\alpha \ge 0$, the **cost-complexity** of $T$ is

$$
R_\alpha(T) = R(T) + \alpha\, |T|.
$$

Each leaf costs $\alpha$. For $\alpha = 0$ the full tree is best; as $\alpha$ grows smaller trees win; for large enough
$\alpha$ the root alone wins. For an internal node $t$, compare keeping its subtree $T_t$ with collapsing it into a
leaf. Collapsing raises the error from $R(T_t)$ to $R(t)$ (the error of $t$ as a leaf) and removes $|T_t| - 1$ leaves.
The two options cost the same when

$$
g(t) = \frac{R(t) - R(T_t)}{|T_t| - 1} = \alpha.
$$

**Weakest-link pruning** repeatedly collapses the internal node with the smallest $g(t)$, the node whose subtree buys
the least error reduction per extra leaf. This produces a nested sequence of subtrees from the full tree down to the
root, with increasing thresholds $\alpha_1 \le \alpha_2 \le \dots$. **Theorem (Breiman et al., 1984).** For every
$\alpha$, the subtree of this sequence for that $\alpha$ is the smallest subtree minimising $R_\alpha$; so the
sequence contains the optimal pruned tree for every penalty at once. (The proof is in chapter 10 of their book.) We
then choose $\alpha$, or equivalently a tree from the sequence, by validation or cross-validation.

The program grows classification trees on 400 points whose class is 1 inside a disc or in a corner square, with 15
percent of the labels flipped at random (so no classifier can beat 85 percent accuracy on average), first with depth
limits and then by pruning a full tree.

```python
--8<-- "books/machine-learning/ch11_cart.py"
```

```
Classification tree on 400 noisy points (15% of labels flipped)
  max depth  leaves  train acc  valid acc
          1       2      0.685      0.657
          2       4      0.688      0.655
          3       7      0.723      0.642
          4      13      0.885      0.775
          6      30      0.938      0.790
          8      53      0.975      0.785
         12      67      1.000      0.777
         50      67      1.000      0.777

Cost-complexity pruning of the full tree (weakest link first)
  leaves  train acc  valid acc   pruned next at alpha
      67      1.000      0.777   0.0013
      39      0.965      0.785   0.0013
      18      0.932      0.800   0.0025
      11      0.915      0.818   0.0025
      10      0.912      0.820   0.0037
       8      0.905      0.810   0.0050
       7      0.900      0.810   0.0250
       6      0.875      0.782   0.0375
       5      0.838      0.757   0.0381
       1      0.685      0.657   (the root alone)
best validation accuracy at 10 leaves
pruned tree: test accuracy 0.811 (the best possible is about 0.85, the share of unflipped labels)
unpruned tree: test accuracy 0.762

The pruned tree as rules:
  if x1 <= 0.156:
      predict 0  (54/58)
  else:
      if x0 <= 0.126:
          predict 0  (43/47)
      else:
          if x0 <= 0.563:
              if x1 <= 0.646:
                  if x1 <= 0.207:
                      if x0 <= 0.436:
                          predict 1  (6/7)
                      else:
                          predict 0  (3/3)
                  else:
                      predict 1  (67/75)
              else:
                  if x0 <= 0.559:
                      predict 0  (55/61)
                  else:
                      predict 1  (2/2)
          else:
              if x1 <= 0.699:
                  predict 0  (93/98)
              else:
                  if x0 <= 0.704:
                      predict 0  (12/14)
                  else:
                      predict 1  (30/35)

Regression tree on y = sin(4x) + noise, 200 points
  depth 1:   2 leaves, test MSE 0.1174
  depth 2:   4 leaves, test MSE 0.0730
  depth 3:   8 leaves, test MSE 0.0548
  depth 5:  29 leaves, test MSE 0.0517
  depth 8: 109 leaves, test MSE 0.0664
```

The full tree has 67 leaves, fits the training labels perfectly (flipped ones included) and reaches 77.7 percent on
validation data. Pruning removes the leaves that only memorise flipped labels: at 10 leaves validation accuracy peaks
at 82 percent, and on 2000 fresh test points the pruned tree scores 81.1 percent against 76.2 for the full tree, not
far from the 85 percent ceiling. The printed rules can be read directly: "if $x_1 \le 0.156$, predict 0" is the band
below the disc. Two leaves hold only 2 or 3 points; a slightly stronger penalty would remove them. The regression tree
shows the same U-shape: 29 leaves are better than 4 or 109.

**What trees do well and badly.** Trees need no feature scaling: a split depends only on the *order* of a feature's
values, so any increasing transformation of a feature (logarithm, standardisation) gives the same tree. They handle
mixtures of numeric and categorical features, capture interactions (a split below a split is an interaction), and can
deal with missing values (CART uses **surrogate splits** that mimic the primary split with another feature). Their
weaknesses: axis-aligned staircase boundaries, piecewise-constant predictions, and above all **high variance**. A
small change in the data can change the root split, and with it everything below. The rest of this chapter is about
curing that variance by combining many trees.

## 11.3 Bagging and random forests; out-of-bag error

If one tree is unstable, why not grow many and average them? The difficulty is that we have only one training set.
**Bagging** (bootstrap aggregating, Leo Breiman, 1996) manufactures many training sets from one.

**The bootstrap.** A **bootstrap sample** is $n$ points drawn from the $n$ training points *with replacement*. Some
points appear twice or more, others not at all. Each sample is a slightly different version of the data, as if we had
drawn a fresh data set from a distribution that puts mass $1/n$ on each training point (Bradley Efron's bootstrap,
1979, [Chapter 7](07-Evaluating-Models.md)).

**Bagging.** Draw $B$ bootstrap samples, grow a full (unpruned) tree on each, and predict by majority vote
(classification) or average (regression). Full trees have low bias and high variance; averaging is meant to remove the
variance while keeping the low bias.

**How much does averaging help?** Suppose each tree's prediction at some $x$ is a random variable (random through the
bootstrap sample) with variance $\sigma^2$, and any two trees' predictions have correlation $\rho$. The variance of
the average of $B$ trees is

$$
\mathrm{Var}\Big(\frac1B \sum_{b=1}^B T_b\Big) = \frac{1}{B^2}\Big(B\sigma^2 + B(B-1)\rho\sigma^2\Big) = \rho\sigma^2 + \frac{1 - \rho}{B}\,\sigma^2,
$$

because the variance of a sum is the sum of all $B^2$ covariances: $B$ variances $\sigma^2$ and $B(B-1)$ covariances
$\rho\sigma^2$. The second term vanishes as $B$ grows, so more trees never hurt, but the first term stays: **the benefit
of averaging is limited by the correlation between the trees.** Bagged trees are strongly correlated, because they are
all grown greedily on nearly the same data and tend to choose the same strong splits near the root.

**Random forests** (Leo Breiman, 2001) decorrelate the trees. At every split, the tree may only consider a random
subset of $m$ of the $d$ features (a fresh subset at each node). Common defaults are $m = \sqrt d$ for classification
and $m = d/3$ for regression. Each tree becomes a little worse ($\sigma^2$ and bias rise slightly), but the trees
become much less alike ($\rho$ falls), and the average usually improves. Earlier, Tin Kam Ho (1995) had built
"random decision forests" from trees on random feature subspaces, and Yali Amit and Donald Geman (1997) had used
random feature choice at each node; Breiman combined random features with bagging and gave the method its name and
its analysis.

### Out-of-bag error

A point is missing from a given bootstrap sample with probability $(1 - 1/n)^n$, which tends to $1/e \approx 0.368$.
So each tree never saw about a third of the training points. Its predictions on those points are honest test
predictions. For each training point, take the vote of only the trees that did not see it: the accuracy of these
votes is the **out-of-bag** (OOB) estimate. It comes free with training and behaves much like cross-validation, so a
random forest needs no separate validation set to estimate its error or to tune the number of trees.

The program bags trees and grows a random forest on data with 10 features: the two informative ones of 11.2 and four
noisy copies of each, so that many features carry similar information.

```python
--8<-- "books/machine-learning/ch11_forest.py"
```

```
One full tree: test accuracy 0.674
Probability a given point is left out of a bootstrap sample: (1 - 1/400)^400 = 0.3674  (1/e = 0.3679)

bagging (all 10 features per split)
  trees   OOB acc   test acc
      1     0.680     0.600
      5     0.667     0.682
     10     0.685     0.735
     25     0.738     0.747
     50     0.728     0.758
    100     0.752     0.761
  mean correlation between trees' test errors: 0.257
  mean accuracy of a single tree: 0.655

random forest (3 of 10 per split)
  trees   OOB acc   test acc
      1     0.615     0.635
      5     0.704     0.696
     10     0.732     0.763
     25     0.725     0.766
     50     0.738     0.777
    100     0.767     0.782
  mean correlation between trees' test errors: 0.218
  mean accuracy of a single tree: 0.655
```

Read the last two lines of each block first. Single trees in the forest are no more accurate than bagged trees
(0.655 each), but their errors are less correlated (0.218 against 0.257), and so the forest of 100 trees reaches 78.2
percent against 76.1 for bagging and 67.4 for one full tree. The OOB column tracks the test column, a little below it
for small $B$ (each point's OOB vote uses only about 37 percent of the trees) and close to it by 100 trees. Random
forests are not always better than bagging: when only a few of many features are informative, a random subset often
contains none of them, and the forest's trees become weak (try replacing the noisy copies by pure noise features).

**Why random forests became a default.** They have few settings that matter, are hard to overfit by adding trees,
give an OOB error estimate for free, parallelise perfectly (trees are independent), and do well on a very wide range
of tabular problems with no tuning. Breiman's paper also introduced the permutation importance of 11.7.

## 11.4 Boosting: AdaBoost and the exponential-loss view

*Level: advanced.*

Bagging grows its trees independently and averages them. **Boosting** grows them in sequence, each one concentrating
on the mistakes of those before. The question behind it came from learning theory: Michael Kearns and Leslie Valiant
asked (1988-1989) whether a **weak learner**, one guaranteed only to do slightly better than random guessing, could
always be "boosted" into a strong learner with arbitrarily small error. Robert Schapire proved in 1990 that it can.
Yoav Freund and Schapire's **AdaBoost** ("A Decision-Theoretic Generalization of On-Line Learning and an Application to
Boosting", 1997; the conference version appeared in 1995) turned the theory into a practical algorithm.

**AdaBoost.** Labels are $y_i \in \{-1, +1\}$. Keep a weight $w_i$ on each training point, starting at $1/n$. For
rounds $m = 1, \dots, M$:

1. train a weak classifier $h_m(x) \in \{-1, +1\}$ to minimise the **weighted error** $\varepsilon_m = \sum_i w_i\,[h_m(x_i) \ne y_i]$;
2. give it the vote $\alpha_m = \tfrac12 \ln\frac{1 - \varepsilon_m}{\varepsilon_m}$ (positive when $\varepsilon_m < 1/2$);
3. reweight: $w_i \leftarrow w_i\, e^{-\alpha_m y_i h_m(x_i)} / Z_m$, where $Z_m$ makes the weights sum to 1. Points the
   new classifier got wrong are multiplied by $e^{\alpha_m}$, points it got right by $e^{-\alpha_m}$.

The final classifier is $\mathrm{sign}(F(x))$ with $F(x) = \sum_m \alpha_m h_m(x)$. The weak classifiers here are
**decision stumps**: trees with a single split, "predict $s$ if $x_f > t$, else $-s$".

**A trace by hand.** Six points on a line, $x = 1, \dots, 6$, labels $+, +, -, -, +, +$. No stump can classify them
all: the minus points are in the middle.

| Round | Stump chosen | $\varepsilon$ | $\alpha$ | Weights after the round (points 1 to 6) |
| --- | --- | --- | --- | --- |
| 1 | always $+1$ (ties with others) | 2/6 = 0.333 | $\tfrac12 \ln 2 = 0.347$ | 1/8, 1/8, 1/4, 1/4, 1/8, 1/8 |
| 2 | $x > 4.5 \Rightarrow +1$, else $-1$ | 1/8 + 1/8 = 0.25 | $\tfrac12 \ln 3 = 0.549$ | 1/4, 1/4, 1/6, 1/6, 1/12, 1/12 |
| 3 | $x > 2.5 \Rightarrow -1$, else $+1$ | 1/12 + 1/12 = 0.167 | $\tfrac12 \ln 5 = 0.805$ | |

After round 1 the two misclassified points (3 and 4) carry half of the total weight, so round 2 must attend to them:
its stump gets them right and misclassifies points 1 and 2 instead. Each round the misclassified points end up with
exactly half the weight (exercise 8). The combined score at $x = 1$ is $0.347 - 0.549 + 0.805 = 0.602 > 0$; at $x = 3$
it is $0.347 - 0.549 - 0.805 = -1.007 < 0$; at $x = 5$ it is $0.347 + 0.549 - 0.805 = 0.091 > 0$. Three stumps
together classify all six points correctly, which no single stump can.

### The training error falls exponentially

**Theorem (Freund and Schapire).** The training error of $\mathrm{sign}(F)$ after $M$ rounds satisfies

$$
\frac1n \sum_{i=1}^n [\mathrm{sign}(F(x_i)) \ne y_i] \;\le\; \prod_{m=1}^M Z_m \;=\; \prod_{m=1}^M 2\sqrt{\varepsilon_m (1 - \varepsilon_m)} \;\le\; \exp\Big(-2\sum_{m=1}^M \gamma_m^2\Big),
$$

where $\gamma_m = \tfrac12 - \varepsilon_m$ is the **edge** of the $m$-th weak classifier over random guessing.

*Proof.* Unroll the weight updates: starting from $1/n$,

$$
w_i^{(M+1)} = \frac{1}{n} \cdot \frac{e^{-y_i \sum_m \alpha_m h_m(x_i)}}{\prod_m Z_m} = \frac{e^{-y_i F(x_i)}}{n \prod_m Z_m}.
$$

The final weights sum to 1, so $\frac1n \sum_i e^{-y_i F(x_i)} = \prod_m Z_m$. A point is misclassified exactly when
$y_i F(x_i) \le 0$, and then $e^{-y_i F(x_i)} \ge 1$; otherwise $e^{-y_i F(x_i)} > 0$. So the indicator of a mistake is
at most $e^{-y_iF(x_i)}$, and the training error is at most $\frac1n\sum_i e^{-y_iF(x_i)} = \prod_m Z_m$. Next compute
$Z_m$: the correctly classified points have total weight $1 - \varepsilon_m$ and are multiplied by $e^{-\alpha_m}$, the
others have weight $\varepsilon_m$ and are multiplied by $e^{\alpha_m}$, so $Z_m = (1 - \varepsilon_m)e^{-\alpha_m} + \varepsilon_m e^{\alpha_m}$.
This is minimised over $\alpha_m$ where its derivative $-(1 - \varepsilon_m) e^{-\alpha_m} + \varepsilon_m e^{\alpha_m}$
vanishes, at $e^{2\alpha_m} = (1 - \varepsilon_m)/\varepsilon_m$: that is AdaBoost's choice of $\alpha_m$, and it gives
$Z_m = 2\sqrt{\varepsilon_m(1 - \varepsilon_m)}$. Finally, with $\varepsilon_m = \tfrac12 - \gamma_m$,
$2\sqrt{\varepsilon_m(1-\varepsilon_m)} = \sqrt{1 - 4\gamma_m^2} \le e^{-2\gamma_m^2}$, using $1 + u \le e^u$ with
$u = -4\gamma_m^2$. $\square$

If every weak classifier has an edge of at least $\gamma > 0$, the training error is at most $e^{-2M\gamma^2}$: it falls
exponentially fast and reaches zero after about $\ln n / (2\gamma^2)$ rounds (when it falls below $1/n$). That answers
Kearns and Valiant's question for the training data; generalisation needs more (below).

### The exponential-loss view

The proof shows that AdaBoost drives down $\frac1n \sum_i e^{-y_i F(x_i)}$, the **exponential loss** of the margin
$y F(x)$. Jerome Friedman, Trevor Hastie and Robert Tibshirani ("Additive Logistic Regression: A Statistical View of
Boosting", 2000) showed that it is exactly a greedy algorithm for this loss. Suppose we build $F$ one term at a time
(**forward stagewise additive modelling**): given $F_{m-1}$, choose $h$ and $\alpha$ to minimise

$$
\sum_i e^{-y_i (F_{m-1}(x_i) + \alpha h(x_i))} = \sum_i w_i\, e^{-\alpha y_i h(x_i)}, \qquad w_i \propto e^{-y_i F_{m-1}(x_i)}.
$$

These $w_i$ are precisely AdaBoost's weights. For fixed $\alpha > 0$ the sum is
$e^{-\alpha}\sum_{\text{right}} w_i + e^{\alpha}\sum_{\text{wrong}} w_i$, which is minimised by the $h$ with the
smallest weighted error; then minimising over $\alpha$ is the calculation of $Z_m$ above. So AdaBoost is coordinate-wise
greedy minimisation of the exponential loss over the space of combinations of weak classifiers.

What does minimising the exponential loss estimate? At a point $x$ with $p = P(y = 1 \mid x)$, the expected loss
$p\,e^{-F} + (1-p)\,e^{F}$ is minimised where $-pe^{-F} + (1-p)e^{F} = 0$, at

$$
F^\ast(x) = \tfrac12 \ln \frac{p}{1 - p},
$$

half the log-odds. So the sign of $F$ estimates the Bayes classifier, and $F$ itself can be turned into probabilities,
just as in logistic regression. The difference from logistic loss is in the tails: the exponential loss grows like
$e^{-m}$ for a badly wrong margin $m$, the logistic loss only like $|m|$. AdaBoost therefore puts enormous weight on
points it keeps getting wrong, which makes it sensitive to **label noise**: mislabelled points end up dominating the
weights.

The program runs AdaBoost with stumps on 500 points labelled by a circle (a shape no single stump can express), with
5 percent of labels flipped.

```python
--8<-- "books/machine-learning/ch11_adaboost.py"
```

```
Hand example: six points on a line, labels + + - - + +
  round 1: stump x0 > 0.000 -> +1, weighted error 0.3333, alpha 0.3466
  round 2: stump x0 > 4.500 -> +1, weighted error 0.2500, alpha 0.5493
  round 3: stump x0 > 2.500 -> -1, weighted error 0.1667, alpha 0.8047
  combined sign after 3 rounds: [ 1  1 -1 -1  1  1]  (true [ 1  1 -1 -1  1  1])

Circle data, 500 training points, 5% label noise
  rounds  train err  bound prod Z  exp loss  test err
       1      0.386        0.9737    0.9737     0.371
       2      0.386        0.9547    0.9547     0.371
       5      0.194        0.8728    0.8728     0.197
      10      0.102        0.7683    0.7683     0.120
      25      0.070        0.5945    0.5945     0.098
      50      0.078        0.4883    0.4883     0.099
     100      0.066        0.4348    0.4348     0.095
     200      0.064        0.3872    0.3872     0.096
     400      0.060        0.3266    0.3266     0.101
```

The columns "bound prod Z" and "exp loss" are equal to four digits in every row, which is the identity in the proof:
the average exponential loss *is* the product of the $Z_m$. Training error is always below the bound. One stump is
barely better than guessing (38.6 percent error); 25 stumps carve a polygon around the circle (9.8 percent test error);
after that the test error stays near 10 percent while training error keeps falling towards the 5 percent of flipped
labels. With the noise, boosting longer begins to fit the flipped points, and test error drifts slightly up at 400
rounds.

**Why boosting often does not overfit.** On clean data, AdaBoost's test error often keeps falling even after the
training error reaches zero, which puzzled researchers. Schapire, Freund, Bartlett and Lee ("Boosting the Margin",
1998) explained much of it: after the training error is zero, AdaBoost keeps increasing the **margins** $y_iF(x_i)/\sum_m \alpha_m$
of the training points, and generalisation bounds depend on the margin distribution, not on the number of rounds. The
explanation is not complete, and the noisy example above shows that boosting can and does overfit when labels are
noisy.

## 11.5 Gradient boosting (Friedman 2001) from scratch for regression

The exponential-loss view suggests a general recipe: pick any differentiable loss, and add weak learners one at a time
to decrease it. Jerome Friedman's **gradient boosting** ("Greedy Function Approximation: A Gradient Boosting Machine",
2001) makes this precise by doing gradient descent not on a parameter vector but on the function $F$ itself.

**Gradient descent in function space.** We want to minimise $\mathcal L(F) = \sum_i L(y_i, F(x_i))$, where $L$ is a
loss such as $(y - F)^2/2$. Think of $F$ only through its values at the training points, $F = (F(x_1), \dots, F(x_n))$.
The gradient of $\mathcal L$ with respect to that vector has components $\partial L(y_i, F(x_i))/\partial F(x_i)$, and
a gradient step would move each $F(x_i)$ by a multiple of the **pseudo-residual**

$$
r_i = -\frac{\partial L(y_i, F)}{\partial F}\Big|_{F = F_{m-1}(x_i)}.
$$

But a step defined only at the training points says nothing about other inputs. So we **fit a regression tree $h_m$
to the pseudo-residuals** (by least squares, as in 11.2), which gives a step that is defined everywhere and
generalises the gradient direction, and then update $F_m = F_{m-1} + \nu\, h_m$ with a small **learning rate**
(**shrinkage**) $\nu$, typically 0.01 to 0.1.

For squared loss $L = \tfrac12(y - F)^2$ the pseudo-residual is $r_i = y_i - F_{m-1}(x_i)$, the ordinary residual: each
tree is fitted to what the model so far gets wrong. For absolute loss $|y - F|$ it is $\mathrm{sign}(y_i - F_{m-1}(x_i))$,
and each leaf's value is then best set to the median of the residuals in the leaf (exercise 9). For the log loss of
classification with $p = 1/(1 + e^{-F})$ and $y \in \{0, 1\}$ it is $y_i - p_i$ (exercise 11). Friedman's algorithm
also re-optimises the value of each leaf for the true loss (a line search per leaf); for squared loss the least-squares
leaf values are already optimal. **Stochastic gradient boosting** (Friedman, 2002) fits each tree on a random half of
the data, which both speeds it up and regularizes.

**By hand.** Four points $x = 1, 2, 3, 4$ with $y = 1, 3, 2, 6$, stumps, and $\nu = 1$ for clarity.

| Round | Residuals before | Stump split | Step | $F$ after | Squared error |
| --- | --- | --- | --- | --- | --- |
| start | | | | 3, 3, 3, 3 (the mean) | 14 |
| 1 | $-2, 0, -1, 3$ | $x \le 3.5$ | $-1, -1, -1, 3$ | 2, 2, 2, 6 | 2 |
| 2 | $-1, 1, 0, 0$ | $x \le 1.5$ | $-1, \tfrac13, \tfrac13, \tfrac13$ | 1, 2.333, 2.333, 6.333 | 0.667 |
| 3 | $0, 0.667, -0.333, -0.333$ | $x \le 2.5$ | $0.333, 0.333, -0.333, -0.333$ | 1.333, 2.667, 2, 6 | 0.222 |

Each stump's leaves hold the mean residual of their points: in round 1 the left leaf averages $(-2 + 0 - 1)/3 = -1$.
The error falls every round, because fitting a stump to the residuals by least squares can only lower the squared
error (the stump that predicts 0 everywhere is one of the options).

The program then boosts depth-limited trees on **Friedman's benchmark function #1**, $y = 10\sin(\pi x_0 x_1) +
20(x_2 - 0.5)^2 + 10x_3 + 5x_4 + \varepsilon$ with ten uniform inputs of which five are unused and noise variance 1
(introduced in Friedman's 1991 paper on multivariate adaptive regression splines). The best possible test error is
therefore 1.

```python
--8<-- "books/machine-learning/ch11_gboost.py"
```

```
Hand example: stumps with learning rate 1 on four points
  start: F = mean = 3.00
  round 1: residuals [-2.  0. -1.  3.], split x <= 3.5, step [-1. -1. -1.  3.], F = [2. 2. 2. 6.], SSE 2.000
  round 2: residuals [-1.  1.  0.  0.], split x <= 1.5, step [-1.     0.333  0.333  0.333], F = [1.    2.333 2.333 6.333], SSE 0.667
  round 3: residuals [ 0.     0.667 -0.333 -0.333], split x <= 2.5, step [ 0.333  0.333 -0.333 -0.333], F = [1.333 2.667 2.    6.   ], SSE 0.222

Friedman #1, 500 training points, noise variance 1
  predicting the mean:      test MSE 26.367
  one tree, depth  3:      test MSE 11.373
  one tree, depth  6:      test MSE 9.285
  one tree, depth 50:      test MSE 10.488
  linear regression:        test MSE 7.251

Boosting, learning rate 1.0, trees of depth 3
  trees   train MSE   test MSE
      1       9.069     11.373
     10       1.789      6.162
     50       0.134      7.348
    100       0.006      7.488
    200       0.000      7.475
    400       0.000      7.475

Boosting, learning rate 0.1, trees of depth 1
  trees   train MSE   test MSE
      1      24.194     24.922
     10      16.773     17.929
     50       6.740      8.453
    100       3.829      5.407
    200       2.444      3.975
    400       1.811      3.799

Boosting, learning rate 0.1, trees of depth 3
  trees   train MSE   test MSE
      1      22.514     23.292
     10       9.203     11.236
     50       1.438      3.861
    100       0.669      3.117
    200       0.289      2.935
    400       0.066      2.836
```

<figure class="mars-fig" markdown="0">
<svg viewBox="0 0 640 270" role="img" aria-label="Test mean squared error of gradient boosting against the number of trees on a log scale, for three settings. Learning rate 1 with depth-3 trees drops to 6.2 at 10 trees and then rises to about 7.5. Learning rate 0.1 with stumps falls slowly to 3.8 at 400 trees. Learning rate 0.1 with depth-3 trees falls to 2.84 at 400 trees, the best. A dashed line marks the noise variance 1.">
  <g font-size="12" fill="currentColor" stroke="currentColor" text-anchor="middle">
    <line x1="80" y1="220" x2="560" y2="220" stroke-width="1"/><line x1="80" y1="220" x2="80" y2="30" stroke-width="1"/>
    <line x1="80" y1="220" x2="80" y2="225"/><text x="80" y="240" stroke="none">1</text>
    <line x1="257" y1="220" x2="257" y2="225"/><text x="257" y="240" stroke="none">10</text>
    <line x1="434" y1="220" x2="434" y2="225"/><text x="434" y="240" stroke="none">100</text>
    <line x1="540" y1="220" x2="540" y2="225"/><text x="540" y="240" stroke="none">400</text>
    <line x1="75" y1="220" x2="80" y2="220"/><text x="70" y="224" stroke="none" text-anchor="end">0</text>
    <line x1="75" y1="185" x2="80" y2="185"/><text x="70" y="189" stroke="none" text-anchor="end">5</text>
    <line x1="75" y1="151" x2="80" y2="151"/><text x="70" y="155" stroke="none" text-anchor="end">10</text>
    <line x1="75" y1="116" x2="80" y2="116"/><text x="70" y="120" stroke="none" text-anchor="end">15</text>
    <line x1="75" y1="82" x2="80" y2="82"/><text x="70" y="86" stroke="none" text-anchor="end">20</text>
    <line x1="75" y1="47" x2="80" y2="47"/><text x="70" y="51" stroke="none" text-anchor="end">25</text>
    <line x1="80" y1="213" x2="560" y2="213" stroke-dasharray="5 4" stroke-width="1"/>
    <text x="555" y="208" stroke="none" text-anchor="end">noise variance 1</text>
    <text x="320" y="262" stroke="none">number of trees (log scale)</text>
    <text x="30" y="125" stroke="none" transform="rotate(-90 30 125)">test MSE</text>
  </g>
  <g fill="none" stroke-width="3">
    <polyline stroke="#9cc9ea" points="80.0,141.3 256.8,177.3 380.3,169.1 433.6,168.2 486.8,168.2 540.0,168.2"/>
    <polyline stroke="#7ccf9a" points="80.0,47.5 256.8,95.9 380.3,161.5 433.6,182.6 486.8,192.5 540.0,193.7"/>
    <polyline stroke="#eea66f" points="80.0,58.7 256.8,142.2 380.3,193.3 433.6,198.4 486.8,199.7 540.0,200.4"/>
  </g>
  <g font-size="12" fill="currentColor">
    <rect x="400" y="44" width="14" height="4" fill="#9cc9ea"/><text x="420" y="50">lr 1.0, depth 3</text>
    <rect x="400" y="64" width="14" height="4" fill="#7ccf9a"/><text x="420" y="70">lr 0.1, depth 1</text>
    <rect x="400" y="84" width="14" height="4" fill="#eea66f"/><text x="420" y="90">lr 0.1, depth 3</text>
  </g>
</svg>
<figcaption>Test error of gradient boosting on Friedman #1 as trees are added. Without shrinkage (learning rate 1,
blue) the model overfits after about 10 trees. With learning rate 0.1, depth-3 trees (orange) keep improving to
2.84; stumps (green) improve more slowly because they cannot express the interaction sin(πx₀x₁) in one tree.</figcaption>
</figure>

Three lessons from the tables. First, one tree is poor (test MSE 9.3 at best) and even plain linear regression does
better (7.3), because a single tree's piecewise-constant steps fit the smooth linear terms badly. Second, without
shrinkage boosting fits the training set exactly within 200 trees and overfits, ending at 7.5. Third, with learning
rate 0.1 and depth-3 trees the test error reaches 2.84, a third of the best single tree's and within 1.84 of the
noise floor. Small steps help for the same reason that a small learning rate helps gradient descent on a noisy
problem: each tree corrects only a fraction of the residual, so later trees can revise its mistakes. The price is
more trees; the number of trees is then chosen by validation (**early stopping**). Tree depth controls the order of
interactions each tree can express: a stump adds a function of one feature at a time (an additive model), a depth-3
tree up to three-way interactions.

## 11.6 Modern boosted trees: XGBoost, LightGBM, and why they win on tables

*Level: advanced.*

Gradient boosting was well established by the mid-2000s. What changed in the 2010s was engineering and a more
careful objective, in libraries that made boosted trees fast enough for millions of rows and dominant in practice.

### XGBoost's objective, derived

Tianqi Chen and Carlos Guestrin's XGBoost ("XGBoost: A Scalable Tree Boosting System", 2016) adds a tree $h$ to $F$
by minimising a second-order approximation of the loss plus an explicit penalty on the tree. Write
$g_i = \partial L(y_i, F)/\partial F$ and $h_i = \partial^2 L(y_i, F)/\partial F^2$ at the current $F(x_i)$ (the first
and second derivatives). By Taylor's theorem,

$$
\sum_i L\big(y_i, F(x_i) + f(x_i)\big) \approx \sum_i \Big[L(y_i, F(x_i)) + g_i f(x_i) + \tfrac12 h_i f(x_i)^2\Big].
$$

A tree $f$ with $T$ leaves assigns a weight $w_j$ to every point in leaf $j$. XGBoost penalises it by
$\Omega(f) = \gamma T + \tfrac12\lambda \sum_j w_j^2$. Dropping constants and grouping the points by leaf, with
$G_j = \sum_{i \in \text{leaf } j} g_i$ and $H_j = \sum_{i \in \text{leaf } j} h_i$, the objective is

$$
\sum_{j=1}^T \Big[G_j w_j + \tfrac12 (H_j + \lambda) w_j^2\Big] + \gamma T.
$$

Each bracket is a parabola in $w_j$, minimised at

$$
w_j^\ast = -\frac{G_j}{H_j + \lambda}, \qquad \text{with value} \qquad -\frac12 \frac{G_j^2}{H_j + \lambda}.
$$

This is a **Newton step** per leaf ([Chapter 5](05-Optimization.md)), shrunk by $\lambda$. Splitting a leaf into
left and right children therefore improves the objective by

$$
\mathrm{Gain} = \frac12 \Big[\frac{G_L^2}{H_L + \lambda} + \frac{G_R^2}{H_R + \lambda} - \frac{(G_L + G_R)^2}{H_L + H_R + \lambda}\Big] - \gamma,
$$

and a split is worth making only if the gain is positive: $\gamma$ acts as a built-in pruning threshold. For squared
loss $g_i = F(x_i) - y_i$ and $h_i = 1$, so $w_j^\ast$ is the mean residual shrunk towards 0 by $\lambda$, and the gain is
the familiar reduction in squared error. For log loss $g_i = p_i - y_i$ and $h_i = p_i(1 - p_i)$.

Around this objective XGBoost added the engineering that made it fast: a split finder that handles **missing values**
by learning a default direction at each split, **approximate split finding** that proposes candidate thresholds from
quantiles of the data (a weighted quantile sketch, weighted by $h_i$), cache-aware column blocks, and parallel and
distributed training.

### LightGBM and CatBoost

**LightGBM** (Guolin Ke and coauthors, 2017) buckets every feature into at most a few hundred bins once, before
training, so that finding a split means sweeping a **histogram** of $G$ and $H$ per bin rather than sorting points;
it grows trees **leaf-wise** (always splitting the leaf with the largest gain, rather than level by level); and it
adds two sampling tricks, gradient-based one-side sampling (keep the points with large gradients, sample the rest)
and exclusive feature bundling (merge sparse features that are rarely nonzero together). **CatBoost** (Liudmila
Prokhorenkova and coauthors, 2018) focuses on categorical features and on a subtle leak in standard boosting: the
residuals a tree is fitted to were computed by a model that saw the same points. Its **ordered boosting** computes each
point's residual from a model trained only on points earlier in a random order.

### Why boosted trees win on tables

On **tabular data** (rows of records, columns of heterogeneous features such as age, price, category, count), gradient
boosted trees are usually the strongest method, and they are the standard first choice in industry. Léo Grinsztajn,
Edouard Oyallon and Gaël Varoquaux ("Why do tree-based models still outperform deep learning on typical tabular
data?", 2022) compared them carefully with deep networks on 45 data sets and reported that tree ensembles remained
ahead on medium-sized data (about 10 thousand rows), identifying three reasons in their experiments: target functions
on tables are often irregular, which trees fit and neural networks smooth over; tables contain many uninformative
features, which trees ignore easily; and the columns have individual meanings, so a method that is invariant to
rotations of the feature space (as standard networks are) discards useful structure, while axis-aligned splits use it.
Add the practical advantages (no scaling, missing values handled, categorical features handled, fast training on a
CPU) and the dominance is not surprising. On images, audio and text, where the raw features are pixels or characters
with spatial or sequential structure, deep networks win instead ([Part IV](15-Neural-Networks-and-Backpropagation.md)).

## 11.7 Feature importance and its pitfalls

A forest of 500 trees cannot be read like the tennis tree. People still want to know which features the model relies
on. Two measures are standard.

**Impurity importance** (also "mean decrease in impurity" or "gain importance"): for each feature, add up the
decrease in impurity (Gini, or squared error for regression) of every split on that feature, over all trees, and
normalise to sum to 1. It costs nothing extra: each node already knows its gain. Our trees store it in `node.gain`.

**Permutation importance** (introduced by Breiman in the random forest paper, 2001): on held-out data, shuffle the
values of one feature (breaking its relationship with the target while keeping its distribution) and measure how much
the model's error increases. A feature the model does not use costs nothing to shuffle; a feature it relies on costs a
lot. It works for any model, not only trees.

Both measures answer "what does this model use?", not "what causes the target?", and both have known traps. The
program measures them on Friedman #1 with an extra feature: a near-copy of $x_3$ (correlation about 0.99).

```python
--8<-- "books/machine-learning/ch11_importance.py"
```

```
Friedman #1 plus a near-copy of x3; test MSE: deep tree 8.74, boosted trees 2.47
feature  used by f?  impurity(deep tree)  impurity(boosting)  permutation(deep)  permutation(boosting)
x0       yes                     0.199               0.219             11.918                10.407
x1       yes                     0.248               0.260             11.017                10.689
x2       yes                     0.070               0.087              2.022                 4.079
x3       yes                     0.315               0.229             13.770                 7.765
x4       yes                     0.078               0.087              2.995                 3.517
x5       no                      0.015               0.003              0.015                 0.018
x6       no                      0.016               0.003              0.266                -0.021
x7       no                      0.003               0.002              0.090                 0.004
x8       no                      0.012               0.004             -0.006                 0.002
x9       no                      0.007               0.004             -0.069                 0.022
x3copy   copy                    0.038               0.103              0.841                 1.704
share of impurity importance on the five unused features: deep tree 0.052, boosting 0.016
```

**Pitfall 1: impurity importance rewards fitting noise.** Impurity importance is computed on the *training* data. A
deep tree splits on pure noise features to separate individual training points, and every such split has positive
gain. The deep tree gives the five unused features 5.2 percent of its importance, three times the share boosting
gives them. On a larger scale, Carolin Strobl and coauthors (2007) showed that impurity importance is biased towards
features with many possible split points (continuous features and categorical features with many levels) even when
they are uninformative. Permutation importance on held-out data does not have this bias: for the unused features it is
near zero, sometimes slightly negative (noise in the estimate).

**Pitfall 2: correlated features share or hide credit.** The near-copy of $x_3$ carries the same information as $x_3$.
The deep tree happened to prefer $x_3$ (0.315 against 0.038); the boosted model spreads the credit (0.229 and 0.103). The
permutation importance of $x_3$ under boosting (7.8) is much smaller than under the deep tree (13.8), because when
$x_3$ is shuffled, the model can still read most of the same information from the copy. Neither number says "$x_3$ is
the cause and the copy is not". With strongly correlated features, permuting one also creates impossible records (a
copy that disagrees with its original), so the model is evaluated far from the data it was trained on. Remedies
include permuting groups of correlated features together, or conditional permutation schemes.

**Pitfall 3: importance is not effect.** A large importance says the predictions change a lot when the feature is
scrambled. It says nothing about the direction of the effect, whether it is the same for all records, or whether
changing the feature in the world would change the outcome (correlation is not cause, [Chapter 1](01-What-Is-Machine-Learning.md)).
Partial dependence plots, SHAP values ([Chapter 22](22-Machine-Learning-in-Practice.md)) and causal analysis answer
those questions, each with its own assumptions.

**In practice.** scikit-learn provides `DecisionTreeClassifier` (CART, with cost-complexity pruning via `ccp_alpha`),
`RandomForestClassifier`, `AdaBoostClassifier`, `HistGradientBoostingRegressor` (a LightGBM-style histogram booster)
and `permutation_importance`; XGBoost, LightGBM and CatBoost are separate libraries implementing 11.6 at scale.

## Check yourself

??? question "1. A node has 3 points of class Yes and 1 of class No. Compute its entropy, Gini impurity and misclassification rate."

    $p = 3/4$. Entropy $-0.75\log_2 0.75 - 0.25\log_2 0.25 = 0.311 + 0.5 = 0.811$ bits. Gini $1 - 0.75^2 - 0.25^2 =
    0.375$ (or $2 \cdot 0.75 \cdot 0.25$). Misclassification $\min(0.75, 0.25) = 0.25$.

??? question "2. Compute the information gain of Humidity on the whole tennis table by hand."

    High: 3 Yes, 4 No, entropy $H(3/7) = 0.985$. Normal: 6 Yes, 1 No, entropy $H(6/7) = 0.592$. Each child holds 7 of
    the 14 days, so the gain is $0.940 - \tfrac12(0.985) - \tfrac12(0.592) = 0.152$, matching the program.

??? question "3. A parent node has 400 points of each class. Split A gives children (300, 100) and (100, 300); split B gives (200, 400) and (200, 0). Compare them by misclassification rate and by Gini."

    Misclassification: A makes $100 + 100 = 200$ errors, B makes $200 + 0 = 200$: a tie, rate 0.25 both. Gini of A:
    each child has $2 \cdot 0.75 \cdot 0.25 = 0.375$, weighted average $0.375$. Gini of B: the first child (600 points,
    $p = 1/3$) has $2 \cdot \tfrac13 \cdot \tfrac23 = 0.444$, weight $0.75$; the second is pure; weighted average $0.333$.
    Gini prefers B, which has made a pure node.

??? question "4. Why does applying log(x) to a positive feature never change a decision tree, while rotating two features can change it completely?"

    A split "$x_f \le t$" depends only on which points lie on which side, that is on the order of the values of $x_f$.
    An increasing function such as $\log$ keeps the order, so the same partitions are available (with thresholds
    $\log t$) and the greedy algorithm makes the same choices. A rotation mixes features: a boundary along the
    diagonal $x_1 = x_2$, which a linear model represents with one weight vector, needs a staircase of many axis-aligned
    splits, while after rotating by 45 degrees it is a single split.

??? question "5. Prove that cost-complexity pruning with α = 0 keeps every split that reduces the training error, and explain why a split with g(t) = 0 is pruned first."

    For $\alpha = 0$, $R_\alpha(T) = R(T)$, and collapsing a node with $R(t) > R(T_t)$ increases it, so such nodes stay.
    A node with $g(t) = 0$ has $R(t) = R(T_t)$: its subtree adds leaves but corrects no training points (every leaf
    below predicts the same class as $t$ would, or the corrections cancel). For any $\alpha > 0$ collapsing it lowers
    $R_\alpha$, so it is the first to go. This is exactly why the first rows of the program's pruning table have very
    small $\alpha$.

??? question "6. Trees in an ensemble have variance σ² = 1 and pairwise correlation ρ = 0.3. What is the variance of the average of 100 trees, and of infinitely many?"

    $\rho\sigma^2 + (1 - \rho)\sigma^2/B = 0.3 + 0.7/100 = 0.307$. As $B \to \infty$ it tends to $0.3$: after a hundred
    trees almost all the remaining variance is the correlated part, which only decorrelation (random features) can
    reduce.

??? question "7. Every weak classifier in an AdaBoost run has weighted error 0.4. Bound the training error after 100 rounds both ways."

    $\prod Z_m = (2\sqrt{0.4 \cdot 0.6})^{100} = (0.9798)^{100} = 0.130$. With $\gamma = 0.1$,
    $\exp(-2 \cdot 100 \cdot 0.01) = e^{-2} = 0.135$. A 10 percent edge gives an error bound of 13 percent after 100
    rounds; it falls below $1/n$ for $n = 1000$ after $\ln(1000)/(2 \cdot 0.01) \approx 345$ rounds.

??? question "8. Show that after AdaBoost's reweighting, the classifier just added has weighted error exactly 1/2 under the new weights."

    The misclassified points had total weight $\varepsilon$; they are multiplied by $e^{\alpha} = \sqrt{(1-\varepsilon)/\varepsilon}$,
    giving $\sqrt{\varepsilon(1-\varepsilon)}$. The correct points had weight $1 - \varepsilon$, multiplied by
    $e^{-\alpha}$, giving $\sqrt{\varepsilon(1-\varepsilon)}$ as well. After dividing by their sum $Z$, each group has
    weight exactly $1/2$. So the next round cannot pick the same classifier again: it is now no better than a coin.
    In the hand trace, after round 1 the misclassified points 3 and 4 have weights $1/4 + 1/4$.

??? question "9. For gradient boosting with absolute loss |y − F|, what are the pseudo-residuals, and why should each leaf predict the median of the residuals in it?"

    $\partial |y - F| / \partial F = -\mathrm{sign}(y - F)$, so $r_i = \mathrm{sign}(y_i - F(x_i))$: only the direction of
    each error, which makes the method robust to outliers. A tree fitted to these signs finds regions where the model
    is too high or too low, but its leaf values ($\pm$ averages of signs) are not the right step sizes. The best
    constant step $c$ in a leaf minimises $\sum_i |y_i - F(x_i) - c|$, a sum of absolute deviations, minimised by the
    median of the residuals $y_i - F(x_i)$: moving $c$ past the median increases the distance to more than half the points.

??? question "10. In XGBoost a leaf has G = −4 and H = 2, with λ = 1. What is its weight and its contribution to the objective? If it is split into children with (G, H) = (−4, 1) and (0, 1), and γ = 0.5, should the split be made?"

    $w^\ast = -G/(H + \lambda) = 4/3$, objective $-\tfrac12 G^2/(H + \lambda) = -16/6 = -2.667$. For the split:
    $\tfrac12\big[16/2 + 0/2 - 16/3\big] - 0.5 = \tfrac12(8 - 5.333) - 0.5 = 1.333 - 0.5 = 0.833 > 0$, so yes.
    The left child gets weight $4/2 = 2$ and the right child $0$.

??? question "11. Write the code: gradient boosting for binary classification with the log loss, depth-2 trees fitted to the pseudo-residuals y − p, and a Newton step in each leaf."

    ```python
    import numpy as np                       # run it in the folder that holds ch11_cart.py
    from ch11_cart import grow, predict

    rng = np.random.default_rng(0)
    X = rng.normal(0, 1, (400, 2))
    y = ((X ** 2).sum(1) < 1.4).astype(float)          # 1 inside a circle, 0 outside
    Xt = rng.normal(0, 1, (2000, 2))
    yt = ((Xt ** 2).sum(1) < 1.4).astype(float)

    p0 = y.mean()
    F = np.full(400, np.log(p0 / (1 - p0)))             # start at the log-odds of the base rate
    Ft = np.full(2000, F[0])
    for m in range(1, 201):
        p = 1 / (1 + np.exp(-F))
        r = y - p                                         # negative gradient of the log loss
        tree = grow(X, r, np.arange(400), "regress", max_depth=2)
        # Newton step in each leaf: sum(r) / sum(p (1 - p)) instead of the mean residual
        stack = [(tree, np.arange(400))]
        while stack:
            t, idx = stack.pop()
            if t.feature is None:
                t.value = r[idx].sum() / max((p[idx] * (1 - p[idx])).sum(), 1e-12)
                continue
            go = X[idx, t.feature] <= t.threshold
            stack += [(t.left, idx[go]), (t.right, idx[~go])]
        F += 0.1 * predict(tree, X, "regress")
        Ft += 0.1 * predict(tree, Xt, "regress")
        if m in (1, 10, 50, 200):
            loss = np.mean(np.log(1 + np.exp(-(2 * y - 1) * F)))
            print(f"{m:4d} trees: train log loss {loss:.4f}, test accuracy {np.mean((Ft > 0) == yt):.3f}")
    ```

    Output:

    ```
       1 trees: train log loss 0.6548, test accuracy 0.747
      10 trees: train log loss 0.4295, test accuracy 0.938
      50 trees: train log loss 0.1459, test accuracy 0.944
     200 trees: train log loss 0.0225, test accuracy 0.947
    ```

    The leaf value $\sum r_i / \sum p_i(1 - p_i)$ is XGBoost's $-G/H$ with $\lambda = 0$ (here $g_i = p_i - y_i$ and
    $h_i = p_i(1 - p_i)$). The training loss keeps falling towards 0 because these labels have no noise.

## What you learned

- A decision tree partitions the input into axis-aligned boxes; each split is chosen greedily to maximise the decrease
  in a strictly concave impurity (entropy or Gini), which never makes children less pure than their parent.
- CART evaluates every threshold of every feature with one sort and a sweep of running sums, $O(dn\log n)$ per level;
  cost-complexity pruning yields a nested sequence of subtrees, one optimal for each penalty $\alpha$, chosen by
  validation.
- Averaging $B$ trees with correlation $\rho$ leaves variance $\rho\sigma^2 + (1-\rho)\sigma^2/B$; bagging reduces the
  second term, random forests the first, and out-of-bag votes estimate the error for free.
- AdaBoost reweights points towards past mistakes; its training error is at most $\prod_m 2\sqrt{\varepsilon_m(1 - \varepsilon_m)} \le e^{-2\sum\gamma_m^2}$,
  and it is stagewise minimisation of the exponential loss, whose minimiser is half the log-odds.
- Gradient boosting fits each new tree to the negative gradient of the loss and adds it with a small learning rate;
  shrinkage and early stopping control overfitting.
- XGBoost's second-order objective gives leaf weights $-G/(H + \lambda)$ and a closed-form split gain; histogram
  methods and careful engineering make boosted trees the strongest default on tabular data.
- Impurity importance is computed on training data and favours noise and many-valued features; permutation
  importance on held-out data is fairer, but correlated features share credit, and neither measures cause.

**Next:** [Chapter 12](12-Probabilistic-Models.md) treats learning as probability: generative models, Bayesian
inference with priors and posteriors, Gaussian processes and sampling by Markov chain Monte Carlo.

## Further reading

- L. Breiman, J. Friedman, R. Olshen and C. Stone, *Classification and Regression Trees*, 1984.
- J. R. Quinlan, "Induction of Decision Trees", *Machine Learning*, 1986; *C4.5: Programs for Machine Learning*, 1993.
- T. Mitchell, *Machine Learning*, 1997, chapter 3 (decision tree learning, with the tennis table).
- L. Hyafil and R. Rivest, "Constructing Optimal Binary Decision Trees is NP-complete", *Information Processing
  Letters*, 1976.
- L. Breiman, "Bagging Predictors", *Machine Learning*, 1996; "Random Forests", *Machine Learning*, 2001.
- T. K. Ho, "Random Decision Forests", ICDAR 1995; Y. Amit and D. Geman, "Shape Quantization and Recognition with
  Randomized Trees", *Neural Computation*, 1997.
- R. Schapire, "The Strength of Weak Learnability", *Machine Learning*, 1990.
- Y. Freund and R. Schapire, "A Decision-Theoretic Generalization of On-Line Learning and an Application to
  Boosting", *Journal of Computer and System Sciences*, 1997.
- R. Schapire, Y. Freund, P. Bartlett and W. S. Lee, "Boosting the Margin: A New Explanation for the Effectiveness of
  Voting Methods", *Annals of Statistics*, 1998.
- J. Friedman, T. Hastie and R. Tibshirani, "Additive Logistic Regression: A Statistical View of Boosting", *Annals of
  Statistics*, 2000.
- J. Friedman, "Greedy Function Approximation: A Gradient Boosting Machine", *Annals of Statistics*, 2001;
  "Stochastic Gradient Boosting", *Computational Statistics and Data Analysis*, 2002; "Multivariate Adaptive Regression
  Splines", *Annals of Statistics*, 1991 (the benchmark function).
- T. Chen and C. Guestrin, "XGBoost: A Scalable Tree Boosting System", KDD 2016.
- G. Ke, Q. Meng, T. Finley, T. Wang, W. Chen, W. Ma, Q. Ye and T.-Y. Liu, "LightGBM: A Highly Efficient Gradient
  Boosting Decision Tree", NIPS 2017.
- L. Prokhorenkova, G. Gusev, A. Vorobev, A. V. Dorogush and A. Gulin, "CatBoost: Unbiased Boosting with Categorical
  Features", NeurIPS 2018.
- L. Grinsztajn, E. Oyallon and G. Varoquaux, "Why do tree-based models still outperform deep learning on typical
  tabular data?", NeurIPS 2022 (Datasets and Benchmarks).
- C. Strobl, A.-L. Boulesteix, A. Zeileis and T. Hothorn, "Bias in Random Forest Variable Importance Measures:
  Illustrations, Sources and a Solution", *BMC Bioinformatics*, 2007.
- T. Hastie, R. Tibshirani and J. Friedman, *The Elements of Statistical Learning*, 2nd ed., 2009, chapters 9.2 (trees),
  10 (boosting), 15 (random forests); R. Schapire and Y. Freund, *Boosting: Foundations and Algorithms*, 2012.
- On this site: [Chapter 7](07-Evaluating-Models.md) for the bootstrap and cross-validation,
  [Chapter 10](10-Support-Vector-Machines.md) for margins (which also explain boosting),
  [Chapter 22](22-Machine-Learning-in-Practice.md) for SHAP and interpretability, and the
  [Algorithms book, Chapter 8](../algorithms/08-Trees-and-Balanced-Search-Trees.md) for binary trees as data
  structures.
