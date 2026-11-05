# 7. Evaluating models honestly

*A model that scores 99 percent can be useless, and two models whose scores differ by two points may be equally
good. This chapter is about the number you report at the end, and about how not to fool yourself with it. You will
see why accuracy lies when one class is rare, build the confusion matrix and the measures made from it (precision,
recall, F1), draw ROC and precision-recall curves and prove that the area under the ROC curve is the probability of
ranking a random positive above a random negative. Then you will measure regression errors, estimate performance with
cross-validation (and see how the wrong kind gives 98 percent accuracy on pure noise), check whether predicted
probabilities mean what they say, and compare models with confidence intervals, the bootstrap and statistical tests,
including what happens when you try a hundred models and keep the best.*

!!! abstract "In this chapter"
    **You will learn:**

    - why accuracy misleads on imbalanced data, and what to report instead
    - the confusion matrix, precision, recall, specificity and F1, and how the threshold trades one for another
    - ROC curves and AUC, with a proof that AUC is the probability of ranking a positive above a negative, and precision-recall curves
    - regression metrics (MSE, RMSE, MAE, $R^2$) and which prediction each one rewards (proved)
    - k-fold and leave-one-out cross-validation, the leave-one-out shortcut for least squares (proved), data leakage inside cross-validation, and nested cross-validation for tuning
    - calibration, reliability diagrams, the Brier score as a proper scoring rule (proved), and Platt scaling
    - confidence intervals, the bootstrap, McNemar's test, and the multiple-comparisons trap

    **You need:** [Chapter 1](01-What-Is-Machine-Learning.md) (training, validation and test data),
    [Chapter 2](02-Data-and-Features.md) (splitting and leakage), [Chapter 4](04-Linear-Regression.md) (least
    squares) and [Chapter 6](06-Classification-and-Logistic-Regression.md) (logistic regression). Some probability:
    expectation, variance and the normal distribution, from [Chapter 3](03-The-Math-Toolkit.md) or the
    [statistics book](https://math.akadian.ca/books/statistics/).

    **Levels:** 7.1, 7.2 and 7.4 are beginner; 7.3, 7.5 and 7.6 are intermediate; 7.7 is intermediate to advanced.

## 7.1 Accuracy, and why it lies on imbalanced data

**Accuracy** is the fraction of predictions that are correct. It is the first number everyone computes, and for a
balanced problem (about as many examples of each class) it is a fair summary. But many important problems are
**imbalanced**: fraud is rare among card payments, a disease is rare in a screened population, a fault is rare among
sensor readings. Then accuracy rewards doing nothing.

The chapter's first program makes such a problem. Each example has four features, and the label is 1 with probability
given by a logistic model with a strongly negative intercept, so positives are rare. It trains logistic regression
(Chapter 6) on 4000 examples and evaluates on 2000 new ones, of which 188 (9.4 percent) are positive.

```python
--8<-- "books/machine-learning/ch07_metrics.py"
```

Output:

```
1. test set: 2000 examples, 188 positive (9.4%)
   always 'negative'        TP   0 FP   0 FN 188 TN 1812  acc 0.906 prec nan rec 0.000 F1 0.000
   logistic, threshold 0.5  TP  59 FP  25 FN 129 TN 1787  acc 0.923 prec 0.702 rec 0.314 F1 0.434
   logistic, threshold 0.2  TP 120 FP 168 FN  68 TN 1644  acc 0.882 prec 0.417 rec 0.638 F1 0.504
   logistic, threshold 0.05 TP 165 FP 521 FN  23 TN 1291  acc 0.728 prec 0.241 rec 0.878 F1 0.378

2. ten scored examples, threshold swept from high to low
   threshold  label  TPR   FPR
   0.95       1      0.2   0.0
   0.85       1      0.4   0.0
   0.80       0      0.4   0.2
   0.70       1      0.6   0.2
   0.55       0      0.6   0.4
   0.45       1      0.8   0.4
   0.40       0      0.8   0.6
   0.30       0      0.8   0.8
   0.20       1      1.0   0.8
   0.10       0      1.0   1.0
   AUC by trapezoids 0.720, by counting pairs 0.720
   logistic model on the test set: AUC 0.8850 (pairs 0.8850)

3. precision-recall on the test set
   recall 0.20: precision 0.884 (top 43 scores flagged)
   recall 0.40: precision 0.623 (top 122 scores flagged)
   recall 0.60: precision 0.440 (top 257 scores flagged)
   recall 0.80: precision 0.284 (top 532 scores flagged)
   recall 0.90: precision 0.226 (top 752 scores flagged)
   average precision 0.5468; a random ranking would give about 0.0940

4. regression metrics (200 points, five of them outliers)
   predictor                MSE     RMSE    MAE     R^2
   true line 2 + 0.5x       6.182   2.486   1.121   0.244
   constant mean            8.177   2.859   1.786   0.000
   constant median          8.208   2.865   1.778  -0.004
   line shifted by +3      13.191   3.632   3.241  -0.613

5. calibration on 20000 new examples
   logistic: Brier 0.0589  ECE 0.0062  AUC 0.8777
      bin [0.0,0.2)  n 17538  mean predicted 0.036  observed 0.041
      bin [0.2,0.4)  n  1426  mean predicted 0.283  observed 0.289
      bin [0.4,0.6)  n   622  mean predicted 0.490  observed 0.510
      bin [0.6,0.8)  n   277  mean predicted 0.687  observed 0.679
      bin [0.8,1.0)  n   137  mean predicted 0.879  observed 0.869
   overconfident: Brier 0.1234  ECE 0.1261  AUC 0.8777
      bin [0.0,0.2)  n 14779  mean predicted 0.017  observed 0.024
      bin [0.2,0.4)  n  1007  mean predicted 0.291  observed 0.094
      bin [0.4,0.6)  n   682  mean predicted 0.497  observed 0.120
      bin [0.6,0.8)  n   759  mean predicted 0.706  observed 0.155
      bin [0.8,1.0)  n  2773  mean predicted 0.953  observed 0.399
   always predicting the base rate: Brier 0.0804
   overconfident after Platt scaling (a=-2.00, b=0.333): Brier 0.0589  ECE 0.0061
```

The first block is the whole problem in four lines. The "model" that always says *negative* scores 90.6 percent
accuracy and finds none of the 188 positives. The trained logistic model at the usual threshold 0.5 scores 92.3
percent, only 1.7 points better, though it finds 59 positives. Lower the threshold to 0.05 and the model finds 165 of
the 188, far more useful for, say, screening, while its accuracy *falls* to 72.8 percent. Accuracy treats every
mistake as equally bad, and on imbalanced data almost all the "correct" answers are the easy negatives. If you take one
habit from this chapter: **always compare with the trivial baseline** (the majority class for classification, the mean
for regression). A number means little until you know what doing nothing scores.

## 7.2 The confusion matrix, precision, recall and F1

For a binary classifier, every test example falls in one of four cells, by its true class and its predicted class.
This table is the **confusion matrix**:

<figure class="mars-fig" markdown="0">
<svg viewBox="0 0 700 270" role="img" aria-label="A two by two confusion matrix. Columns are actual positive and actual negative; rows are predicted positive and predicted negative. Cells: true positives 59, false positives 25, false negatives 129, true negatives 1787. Arrows show that precision is computed along the predicted positive row and recall down the actual positive column.">
  <g font-size="13" fill="currentColor" text-anchor="middle">
    <text x="300" y="24">actual positive</text>
    <text x="470" y="24">actual negative</text>
    <text x="120" y="92">predicted positive</text>
    <text x="120" y="182">predicted negative</text>
  </g>
  <rect x="220" y="40" width="160" height="80" fill="#7ccf9a" fill-opacity="0.45" stroke="currentColor"/>
  <rect x="390" y="40" width="160" height="80" fill="#eea66f" fill-opacity="0.45" stroke="currentColor"/>
  <rect x="220" y="130" width="160" height="80" fill="#eea66f" fill-opacity="0.45" stroke="currentColor"/>
  <rect x="390" y="130" width="160" height="80" fill="#9cc9ea" fill-opacity="0.45" stroke="currentColor"/>
  <g font-size="14" fill="currentColor" text-anchor="middle">
    <text x="300" y="72">true positives</text><text x="300" y="98" font-weight="bold">TP = 59</text>
    <text x="470" y="72">false positives</text><text x="470" y="98" font-weight="bold">FP = 25</text>
    <text x="300" y="162">false negatives</text><text x="300" y="188" font-weight="bold">FN = 129</text>
    <text x="470" y="162">true negatives</text><text x="470" y="188" font-weight="bold">TN = 1787</text>
  </g>
  <g stroke="currentColor" stroke-width="1.5" fill="none">
    <line x1="560" y1="80" x2="600" y2="80"/>
    <line x1="300" y1="215" x2="300" y2="235"/>
  </g>
  <g font-size="12" fill="currentColor">
    <text x="604" y="76">precision</text>
    <text x="604" y="92">= TP / row</text>
    <text x="300" y="250" text-anchor="middle">recall = TP / column = 59 / 188</text>
    <text x="604" y="108">= 59 / 84</text>
  </g>
</svg>
<figcaption>Figure 7.1. The confusion matrix of the logistic model at threshold 0.5 on the 2000 test examples. Precision reads along the "predicted positive" row; recall reads down the "actual positive" column. Errors are the two orange cells.</figcaption>
</figure>

A **false positive** is a false alarm (statisticians: a type I error); a **false negative** is a miss (type II error).
From the four counts come the measures in common use, each answering a different question:

| measure | formula | question it answers | at threshold 0.5 |
|---|---|---|---|
| accuracy | $(TP+TN)/n$ | what fraction is right? | $1846/2000=0.923$ |
| precision | $TP/(TP+FP)$ | when it says positive, how often is it right? | $59/84=0.702$ |
| recall (sensitivity, true positive rate) | $TP/(TP+FN)$ | of the real positives, how many does it find? | $59/188=0.314$ |
| specificity (true negative rate) | $TN/(TN+FP)$ | of the real negatives, how many does it clear? | $1787/1812=0.986$ |
| false positive rate | $FP/(FP+TN)=1-$ specificity | of the real negatives, how many raise a false alarm? | $25/1812=0.014$ |

Precision and recall pull against each other through the **threshold** $t$: we predict positive when the model's
score is at least $t$. Lowering $t$ flags more examples, so it can only add true positives (recall rises or stays)
but usually adds false positives faster (precision tends to fall). The program's three thresholds show it: recall
$0.314\to0.638\to0.878$, precision $0.702\to0.417\to0.241$. Which point is right depends on the costs. A spam filter
that hides real email is worse than one that lets some spam through, so it wants high precision. A cancer screening
test that misses a case is worse than one that sends a healthy person for a second test, so it wants high recall.
The model does not know these costs; you must choose the threshold for them, on validation data.

### F1

When a single number is needed, a common choice is the **F1 score**, the **harmonic mean** of precision $P$ and recall
$R$:

$$F_1=\frac{2}{1/P+1/R}=\frac{2PR}{P+R}=\frac{2\,TP}{2\,TP+FP+FN}.$$

Why harmonic and not the ordinary average? The harmonic mean is dragged down by the smaller value: a classifier with
$P=1$ and $R=0.01$ (one very safe guess) has arithmetic mean $0.505$ but $F_1=2(0.01)/1.01\approx0.0198$. To get a high
F1 you must be good at both. At threshold 0.5, $F_1=2(59)/(118+25+129)=118/272=0.434$; at 0.2 it is $0.504$, at 0.05 it is
$0.378$. The more general $F_\beta=(1+\beta^2)PR/(\beta^2P+R)$ weighs recall $\beta$ times as much as precision. F1 has
known defects: it ignores true negatives entirely, and it changes with the class balance of the test set. It is a
convention, not a law. When you can, report the confusion matrix itself.

With more than two classes, the confusion matrix is $K\times K$ (row: predicted, column: actual, or the other way;
say which). Per-class precision and recall are computed one class against the rest, and then averaged: **macro**
averaging gives each class equal weight (good when rare classes matter), **micro** averaging pools all the counts
(dominated by the common classes).

<figure class="play" data-play="threshold"><span class="ai-tag">AI-created</span><figcaption><b>Try it.</b> Move the threshold over two made-up score distributions, 100 positives and 900 negatives (each drawn to the same height), and watch precision and recall trade places, while accuracy hardly moves.</figcaption></figure>

## 7.3 ROC curves, AUC and precision-recall curves

*Level: intermediate.*

Every threshold gives a different confusion matrix. Rather than pick one, draw all of them. The **ROC curve**
(receiver operating characteristic, a name from radar engineering in the 1940s and 50s) plots the true positive rate
(recall) against the false positive rate as the threshold sweeps from $+\infty$ (flag nothing: the point $(0,0)$) to
$-\infty$ (flag everything: the point $(1,1)$).

### Drawing one by hand

Take ten examples, already sorted by score, with five positives and five negatives:

| score | 0.95 | 0.85 | 0.80 | 0.70 | 0.55 | 0.45 | 0.40 | 0.30 | 0.20 | 0.10 |
|---|---|---|---|---|---|---|---|---|---|---|
| label | 1 | 1 | 0 | 1 | 0 | 1 | 0 | 0 | 1 | 0 |

Lower the threshold past one example at a time. Passing a positive raises TPR by $1/5$ (a step up); passing a
negative raises FPR by $1/5$ (a step right). The second block of the program prints the path:
$(0,0)\to(0,0.2)\to(0,0.4)\to(0.2,0.4)\to(0.2,0.6)\to(0.4,0.6)\to(0.4,0.8)\to(0.6,0.8)\to(0.8,0.8)\to(0.8,1)\to(1,1)$.

<figure class="mars-fig" markdown="0">
<svg viewBox="0 0 660 310" role="img" aria-label="ROC staircase for ten examples. The horizontal axis is false positive rate from 0 to 1, the vertical axis is true positive rate from 0 to 1. The staircase climbs two steps at FPR 0, then alternates right and up, reaching TPR 1 at FPR 0.8. The area under it, shaded, is 0.72. A dashed diagonal shows a random classifier with area 0.5.">
  <polygon points="60,270 60,222 60,174 108,174 108,126 156,126 156,78 204,78 252,78 252,30 300,30 300,270" fill="#9cc9ea" fill-opacity="0.45"/>
  <g stroke="currentColor" stroke-width="1.2" fill="none">
    <line x1="60" y1="270" x2="300" y2="270"/>
    <line x1="60" y1="270" x2="60" y2="30"/>
    <line x1="60" y1="270" x2="300" y2="30" stroke-dasharray="5 4" stroke-opacity="0.7"/>
  </g>
  <polyline points="60,270 60,222 60,174 108,174 108,126 156,126 156,78 204,78 252,78 252,30 300,30" fill="none" stroke="#eea66f" stroke-width="3"/>
  <g font-size="12" fill="currentColor">
    <text x="54" y="274" text-anchor="end">0</text>
    <text x="54" y="34" text-anchor="end">1</text>
    <text x="300" y="286" text-anchor="middle">1</text>
    <text x="180" y="302" text-anchor="middle">false positive rate</text>
    <text x="30" y="20">true positive rate</text>
    <text x="200" y="230" text-anchor="middle">AUC = 0.72</text>
    <text x="240" y="160">random: 0.5</text>
  </g>
  <g font-size="13" fill="currentColor">
    <text x="350" y="60">Each step up: a positive passes the threshold.</text>
    <text x="350" y="82">Each step right: a negative passes it.</text>
    <text x="350" y="116">Area of each column = fraction of</text>
    <text x="350" y="136">positives ranked above that negative:</text>
    <text x="350" y="160">2/5 + 3/5 + 4/5 + 4/5 + 5/5 = 18/5,</text>
    <text x="350" y="180">times width 1/5 gives 18/25 = 0.72.</text>
    <text x="350" y="214">Perfect ranking: up first, then right,</text>
    <text x="350" y="234">area 1.</text>
  </g>
</svg>
<figcaption>Figure 7.2. The ROC curve of the ten examples is a staircase. The shaded area under it, the AUC, is 0.72; the dashed diagonal is what random scores give on average.</figcaption>
</figure>

A curve that hugs the top-left corner is good: it finds positives before it raises false alarms. The diagonal is what
you expect from random scores. A curve below the diagonal means the scores are informative but upside down.

### AUC is a ranking probability

The **area under the ROC curve** (AUC, or AUROC) summarises the whole curve in one number. Its meaning is much
cleaner than its definition suggests.

**Theorem 7.1.** For a finite set with $P$ positives and $N$ negatives and no tied scores, the AUC equals the fraction
of (positive, negative) pairs in which the positive has the higher score:

$$\mathrm{AUC}=\frac1{PN}\sum_{i:\,y_i=1}\;\sum_{j:\,y_j=0}\mathbf 1[s_i>s_j].$$

So AUC is the probability that a randomly chosen positive is ranked above a randomly chosen negative.

*Proof.* The staircase moves right only when the threshold passes a negative, by $1/N$ each time, so the region under
it splits into $N$ vertical strips of width $1/N$, one per negative. The height of the strip for negative $j$ is the
TPR at the moment the threshold passes $s_j$, which is the fraction of positives already passed, those with score
greater than $s_j$: $\frac1P\#\{i:y_i=1,s_i>s_j\}$. (No ties means no positive is passed at the same moment.) The area
is the sum of width times height over all strips:

$$\sum_{j:\,y_j=0}\frac1N\cdot\frac1P\,\#\{i:y_i=1,\,s_i>s_j\},$$

which is the formula. $\square$

With ties, the staircase takes a diagonal step for a block of tied scores, and the trapezoid it creates counts each
tied pair as one half; the program's `auc_pairs` does exactly that. The pair count is, up to scaling, the
**Mann-Whitney U statistic** (Mann and Whitney 1947), which is how statisticians knew the AUC's distribution long before
machine learning used it. For the ten examples, the five negatives have $2,3,4,4,5$ positives above them, $18$ of the
$25$ pairs, so $\mathrm{AUC}=0.72$, and both computations in the program agree. For the logistic model on the 2000 test
examples, $\mathrm{AUC}=0.885$: pick a random positive and a random negative, and 88.5 percent of the time the positive
gets the higher score.

Consequences of the theorem: AUC depends only on the *order* of the scores, so any increasing transformation of the
scores leaves it unchanged (block 5 confirms this: the miscalibrated model has the same AUC as the calibrated one); it
does not depend on any threshold; and it does not depend on the class balance, because it only compares positives with
negatives. That last point is both its strength and its weakness.

### Precision-recall curves

On a heavily imbalanced problem, a false positive rate of 1 percent sounds small, but if negatives outnumber positives
a thousand to one, it means ten false alarms for every real positive. The ROC curve hides this, because its FPR axis is
divided by the huge number of negatives. A **precision-recall curve** plots precision against recall as the threshold
sweeps, and is much more sensitive to false alarms when positives are rare (Davis and Goadrich 2006 compared the two
curves carefully).

The third block walks down the ranked test set: flagging the top 43 scores finds 20 percent of the positives at
precision 0.884; finding 80 percent requires flagging 532 examples, at precision 0.284. Its usual summary is the
**average precision** (AP): the mean of the precision values at the rank of each positive, which approximates the area
under the PR curve. Here $\mathrm{AP}=0.547$. The baseline is not 0.5 as for AUC but the fraction of positives, here
$0.094$, since a random ranking has precision equal to the base rate everywhere. Always quote the base rate next to an
AP.

## 7.4 Regression metrics

For a model that predicts numbers $\hat y_i$, the errors are the **residuals** $e_i=y_i-\hat y_i$, and the metrics
summarise them.

- **Mean squared error**, $\mathrm{MSE}=\frac1n\sum e_i^2$, the loss of least squares (Chapter 4).
- **Root mean squared error**, $\mathrm{RMSE}=\sqrt{\mathrm{MSE}}$, in the units of $y$: "typically off by about this much".
- **Mean absolute error**, $\mathrm{MAE}=\frac1n\sum|e_i|$, also in the units of $y$, and less dominated by a few large
  errors.
- **Coefficient of determination**, $R^2=1-\mathrm{MSE}/\mathrm{Var}(y)$, where $\mathrm{Var}(y)=\frac1n\sum(y_i-\bar
  y)^2$ is the MSE of always predicting the mean. So $R^2$ is the fraction of the baseline's squared error that the model
  removes. Chapter 4 met it on training data, where for least squares with an intercept it lies between 0 and 1.

On *new* data, $R^2$ can be negative: a model worse than predicting the mean. In the program's fourth block, a line
shifted up by 3 has $R^2=-0.613$.

### Which prediction does each metric reward?

Suppose all you could predict were one constant $c$ for every example. Which $c$ is best?

**Theorem 7.2.** The constant minimising $\frac1n\sum(y_i-c)^2$ is the mean $\bar y$. A constant minimising
$\frac1n\sum|y_i-c|$ is any median of the $y_i$.

*Proof.* For squared error, $\frac{d}{dc}\frac1n\sum(y_i-c)^2=-\frac2n\sum(y_i-c)=-2(\bar y-c)$, which is zero only at
$c=\bar y$, and the function is a convex parabola in $c$. For absolute error, the function $c\mapsto\sum|y_i-c|$ is
convex and piecewise linear; away from the data points its slope is (number of $y_i$ below $c$) minus (number above
$c$). The slope is negative while more than half the points are above $c$ and positive while more than half are
below, so the minimum is where at most half lie on each side, which is the definition of a median. $\square$

More generally, the *function* of $x$ that minimises expected squared error is the conditional mean
$\mathbb E[y\mid x]$, and the one that minimises expected absolute error is the conditional median. So the choice of
metric is a choice of what you want to predict. Block 4 shows it on data with five gross outliers ($+15$): among
constants, the mean wins on MSE ($8.177$ against $8.208$) and the median wins on MAE ($1.778$ against $1.786$). The
outliers also hurt the true line's numbers: its $R^2$ is only $0.244$, because five points contribute most of the
squared error. When a few huge errors are what you fear (a bridge load), use MSE or even the maximum error; when typical
error matters and outliers are noise, MAE or a median-based measure is more honest. Relative measures like the mean
absolute percentage error, $\frac1n\sum|e_i/y_i|$, are popular in forecasting but blow up when $y_i$ is near zero.

## 7.5 Cross-validation

*Level: intermediate.*

Chapter 1 split the data three ways: a **training set** to fit parameters, a **validation set** to choose between
models and settings (**hyperparameters** such as $k$ in $k$-nearest neighbours or the penalty in Chapter 8), and a
**test set** used once at the end. With small data this wastes examples, and the estimate from a single validation set
depends heavily on which examples happened to land in it.

**$k$-fold cross-validation** (CV) uses every example for validation exactly once. Shuffle the data, split it into $k$
roughly equal **folds**, and for each fold $j$: train on the other $k-1$ folds, evaluate on fold $j$. Report the mean
of the $k$ scores, and their spread. Common choices are $k=5$ or $10$. Then, having chosen the setting, refit on all
the data.

```python
--8<-- "books/machine-learning/ch07_validation.py"
```

Output:

```
1. choosing k for k-NN: 5-fold CV on 200 points vs accuracy on 5000 new points
   k    CV mean  fold sd   true accuracy
    1   0.730    0.024     0.732
    3   0.810    0.041     0.767
    7   0.825    0.027     0.790
   15   0.830    0.033     0.798
   31   0.815    0.030     0.799
   61   0.820    0.033     0.798

2. leave-one-out residuals for least squares (30 points)
   refit 30 times:   LOO MSE 0.045295
   one fit, e/(1-h): LOO MSE 0.045295   max difference 6.2e-15
   training MSE 0.036512 (optimistic)

3. noise features, coin-flip labels: pick 20 best features, nearest centroid
   selection before CV (wrong): CV accuracy 0.980
   selection inside each fold:  CV accuracy 0.500

4. random labels, k chosen from 9 values; average over 20 repetitions
   best plain 5-fold CV score: 0.594
   nested CV estimate:         0.531   (truth 0.500)

5. 95% intervals for an accuracy
   85/100: normal [0.780, 0.920]   Wilson [0.767, 0.907]
   850/1000: normal [0.828, 0.872]   Wilson [0.827, 0.871]
   99/100: normal [0.970, 1.010]   Wilson [0.946, 0.998]

6. comparing two classifiers on the same 500 examples
   accuracy A 0.860, B 0.832, difference +0.028
   paired bootstrap 95% interval for the difference: [+0.002, +0.054]
   McNemar: A right & B wrong 30, A wrong & B right 16, chi2 3.67, p = 0.0553

7. 100 coin-flip 'models' scored on the same 200 test labels
   best accuracy 0.595; its p-value if it were the only model: 0.0044
   Bonferroni-adjusted p-value: 0.436
   models with p < 0.05 before adjustment: 7
```

The first block uses 5-fold CV to choose $k$ for the $k$-nearest-neighbour classifier of Chapter 1 on 200 points from
two overlapping clusters, and compares with the accuracy on 5000 fresh points from the same source, which plays the
role of the future. CV correctly says that $k=1$ is bad (0.730, truth 0.732) and that $k$ from about 7 to 61 is good. It
picks $k=15$ with 0.830, while the truth for $k=15$ is 0.798. Two things to notice. The fold-to-fold standard deviation
is about 0.03, so the differences between $k=7$, 15, 31 and 61 are within the noise; CV cannot rank them. And the best
CV score is *optimistically biased*: we chose the maximum of six noisy estimates, and the maximum of noisy numbers is
on average higher than the truth. Block 4 measures that bias.

### What CV estimates, and how precisely

Each of the $k$ models is trained on a fraction $(k-1)/k$ of the data, so CV estimates the performance of the learning
*procedure* on slightly smaller training sets than the final model will have. This makes it slightly pessimistic, more
so for small $k$. Its other error is variance: the $k$ fold scores are not independent (any two training sets share
most of their examples), so the naive standard error $\text{sd}/\sqrt k$ is too small. Bengio and Grandvalet (2004)
proved that no estimator of the variance of $k$-fold CV is unbiased in general. Repeating CV with several different
shuffles and averaging reduces the variance due to the split, not the variance due to the data.

The folds must respect the structure of the data, exactly as in Chapter 2's single split. Use **stratified** folds (each
fold has the class proportions of the whole) for classification, especially with rare classes; **grouped** folds when
several rows come from one patient, one rover traverse or one user, so that a group never sits on both sides; and for
time series, never train on the future: use **forward chaining**, where each validation block comes after all of its
training data.

### Leave-one-out, and a shortcut for least squares

With $k=n$, each fold is a single example: **leave-one-out** cross-validation (LOO). It uses almost all the data for
every fit, so it is nearly unbiased, but it costs $n$ fits and its estimate can have high variance. For least squares,
though, LOO is free.

Write the fit as $\hat y=Hy$, where $H=X(X^\top X)^{-1}X^\top$ is the **hat matrix** (Chapter 4: it projects $y$ onto
the column space of $X$), and $h_{ii}$ is its $i$-th diagonal entry, the **leverage** of example $i$.

**Theorem 7.3.** Let $e_i=y_i-\hat y_i$ be the residual of the fit on all the data, and $e_{(i)}$ the residual at $x_i$
of the fit with example $i$ left out. Then

$$e_{(i)}=\frac{e_i}{1-h_{ii}}.$$

*Proof.* Write $A=X^\top X$, so the full fit is $w=A^{-1}X^\top y$. Leaving out row $i$ changes $A$ to $A-x_ix_i^\top$
and $X^\top y$ to $X^\top y-x_iy_i$. The **Sherman-Morrison formula** gives the inverse of a rank-one change:
$(A-x_ix_i^\top)^{-1}=A^{-1}+\frac{A^{-1}x_ix_i^\top A^{-1}}{1-h_{ii}}$, with $h_{ii}=x_i^\top A^{-1}x_i$ (multiply out to
check). Then the left-out prediction is

$$x_i^\top w_{(i)}=x_i^\top\Bigl(A^{-1}+\frac{A^{-1}x_ix_i^\top A^{-1}}{1-h_{ii}}\Bigr)\bigl(X^\top y-x_iy_i\bigr).$$

Expanding with $x_i^\top A^{-1}X^\top y=\hat y_i$ and $x_i^\top A^{-1}x_i=h_{ii}$:

$$x_i^\top w_{(i)}=\hat y_i-h_{ii}y_i+\frac{h_{ii}\hat y_i-h_{ii}^2y_i}{1-h_{ii}}=\frac{\hat y_i-h_{ii}y_i}{1-h_{ii}}.$$

So $e_{(i)}=y_i-x_i^\top w_{(i)}=\frac{y_i-h_{ii}y_i-\hat y_i+h_{ii}y_i}{1-h_{ii}}=\frac{y_i-\hat y_i}{1-h_{ii}}$. $\square$

Points with high leverage (far from the others in feature space, $h_{ii}$ near 1) have small training residuals because
they pull the fit towards themselves; the formula inflates their residuals back. The sum of the squared left-out
residuals is called **PRESS** (Allen 1974). Block 2 checks the theorem: 30 refits and the one-line formula give the
same LOO MSE, $0.045295$, to $6\times10^{-15}$, while the training MSE $0.036512$ is optimistic. The same trick works for
ridge regression ([Chapter 8](08-Overfitting-and-Regularization.md)) and gives **generalised cross-validation**
(Golub, Heath and Wahba 1979), which replaces each $h_{ii}$ by their average.

### The wrong way to cross-validate

Here is a mistake that has appeared in published research. You have few examples and many features (a common shape in
genomics: 50 patients, 5000 gene measurements). You select the 20 features most correlated with the label, then
cross-validate a classifier on those 20. Block 3 does this with pure noise: random features and coin-flip labels, so
nothing can be predicted and any honest estimate must be about 50 percent. Selecting features on all the data and then
cross-validating gives **98 percent**. Selecting them inside each fold, using only that fold's training data, gives
**50 percent**.

The 20 features were chosen *because* they happen to correlate with these particular labels, including the labels of
the examples later used for validation. The validation folds were no longer unseen. Hastie, Tibshirani and Friedman
(section 7.10.2) describe exactly this example. The rule: **every step that looks at labels, and every step that
learns anything from the data (feature selection, scaling constants, imputation values, choosing hyperparameters), must
be inside the cross-validation loop**, fitted on the training folds only. This is Chapter 2's data leakage again, in
its most tempting form.

### Nested cross-validation for tuning

Choosing a hyperparameter by CV is itself learning from the validation folds, so the best CV score is biased upward, as
block 1 hinted. Block 4 measures it with random labels, where the true accuracy of every $k$ is exactly 0.5. Picking
the best of nine values of $k$ and reporting its 5-fold CV score gives 0.594 on average over 20 repetitions: nearly ten
points of pure optimism from choosing the maximum.

**Nested cross-validation** fixes this with two loops. The outer loop splits the data into folds for *evaluation*. For
each outer fold, the inner loop runs an ordinary CV on the outer training data alone to choose $k$; the model with that
$k$ is then trained on the outer training data and scored once on the outer fold, which the choice never saw. The mean
of the outer scores estimates the performance of the whole procedure, *including the tuning*. Here it gives 0.531,
close to the truth 0.5 (the remaining gap is within the noise of 20 repetitions on 80 points). Varma and Simon (2006)
and Cawley and Talbot (2010) showed how large the bias of non-nested tuning can be on real data. Nested CV costs
(outer folds) times (inner folds) times (grid size) fits; when that is too much, at least keep a final untouched test
set.

<figure class="mars-fig" markdown="0">
<svg viewBox="0 0 660 250" role="img" aria-label="Nested cross-validation drawn as bars. The outer bar is split into five folds, one shaded as the outer test fold. The remaining four folds, the outer training data, are shown again below, split into four inner folds, one of them shaded as the inner validation fold. Arrows: the inner loop chooses k; the chosen model is trained on all outer training data and scored once on the outer test fold.">
  <g font-size="13" fill="currentColor">
    <text x="20" y="30">outer loop (evaluation): 5 folds</text>
  </g>
  <g stroke="currentColor" stroke-width="1">
    <rect x="20" y="40" width="120" height="34" fill="#9cc9ea" fill-opacity="0.45"/>
    <rect x="140" y="40" width="120" height="34" fill="#9cc9ea" fill-opacity="0.45"/>
    <rect x="260" y="40" width="120" height="34" fill="#eea66f" fill-opacity="0.6"/>
    <rect x="380" y="40" width="120" height="34" fill="#9cc9ea" fill-opacity="0.45"/>
    <rect x="500" y="40" width="120" height="34" fill="#9cc9ea" fill-opacity="0.45"/>
  </g>
  <g font-size="12" fill="currentColor" text-anchor="middle">
    <text x="320" y="62">outer test fold</text>
    <text x="80" y="62">train</text><text x="200" y="62">train</text>
    <text x="440" y="62">train</text><text x="560" y="62">train</text>
  </g>
  <g font-size="13" fill="currentColor">
    <text x="20" y="114">inner loop (tuning) on the four outer training folds only: 4 folds</text>
  </g>
  <g stroke="currentColor" stroke-width="1">
    <rect x="20" y="124" width="150" height="34" fill="#9cc9ea" fill-opacity="0.45"/>
    <rect x="170" y="124" width="150" height="34" fill="#7ccf9a" fill-opacity="0.6"/>
    <rect x="320" y="124" width="150" height="34" fill="#9cc9ea" fill-opacity="0.45"/>
    <rect x="470" y="124" width="150" height="34" fill="#9cc9ea" fill-opacity="0.45"/>
  </g>
  <g font-size="12" fill="currentColor" text-anchor="middle">
    <text x="95" y="146">train</text><text x="245" y="146">inner validation</text>
    <text x="395" y="146">train</text><text x="545" y="146">train</text>
  </g>
  <g font-size="13" fill="currentColor">
    <text x="20" y="194">1. For each candidate k, the inner CV scores it; the best k is chosen.</text>
    <text x="20" y="216">2. Train with that k on all four outer training folds; score once on the outer test fold.</text>
    <text x="20" y="238">3. Repeat for each outer fold; the mean outer score estimates the whole procedure.</text>
  </g>
</svg>
<figcaption>Figure 7.3. Nested cross-validation. The outer test fold (orange) is never seen while choosing k; tuning happens entirely inside the outer training data, with its own validation folds (green).</figcaption>
</figure>

## 7.6 Calibration, reliability diagrams and the Brier score

*Level: intermediate.*

A classifier that outputs probabilities makes a promise: of all the cases where it says "70 percent", about 70
percent should turn out positive. A model that keeps this promise is **calibrated**. Calibration matters whenever the
probability itself is used: to set a threshold from costs, to combine with other evidence, or to tell a doctor "this
patient has a 30 percent risk". AUC cannot see it, since it depends only on the order of the scores.

### Reliability diagrams

Group the predictions into bins by predicted probability, say $[0,0.2),[0.2,0.4),\dots$, and in each bin compare the
mean predicted probability with the observed fraction of positives. Plot one against the other: a calibrated model
lies on the diagonal. This is a **reliability diagram**. A single-number summary is the **expected calibration error**
(ECE): the average over bins of $|\text{mean predicted}-\text{observed}|$, weighted by the fraction of examples in each
bin. It depends on the choice of bins, so report them.

Block 5 compares two models on 20000 new examples. The first is the logistic regression, whose maximum-likelihood fit
tends to be well calibrated when the model is right: in every bin the two numbers agree to about 0.02, and
$\mathrm{ECE}=0.006$. The second has exactly the same ranking (its log-odds are $3z+6$, an increasing function of the
logistic score $z$, so its AUC is identical, 0.8777) but is badly miscalibrated: when it says 95 percent, the truth is 40
percent. Its ECE is $0.126$.

<figure class="mars-fig" markdown="0">
<svg viewBox="0 0 660 310" role="img" aria-label="Reliability diagram. Horizontal axis mean predicted probability from 0 to 1, vertical axis observed fraction positive from 0 to 1, with a dashed diagonal for perfect calibration. Green points for the logistic model lie on the diagonal. Orange points for the miscalibrated model lie far below it: at predicted 0.95 the observed fraction is only 0.40.">
  <g stroke="currentColor" stroke-width="1.2" fill="none">
    <line x1="80" y1="270" x2="320" y2="270"/>
    <line x1="80" y1="270" x2="80" y2="30"/>
    <line x1="80" y1="270" x2="320" y2="30" stroke-dasharray="5 4" stroke-opacity="0.7"/>
  </g>
  <polyline points="89,260 148,201 198,148 245,107 291,61" fill="none" stroke="#7ccf9a" stroke-width="2.5"/>
  <polyline points="84,264 150,247 199,241 249,233 309,174" fill="none" stroke="#eea66f" stroke-width="2.5"/>
  <g fill="#7ccf9a" stroke="currentColor">
    <circle cx="89" cy="260" r="5"/><circle cx="148" cy="201" r="5"/><circle cx="198" cy="148" r="5"/>
    <circle cx="245" cy="107" r="5"/><circle cx="291" cy="61" r="5"/>
  </g>
  <g fill="#eea66f" stroke="currentColor">
    <rect x="80" y="260" width="8" height="8"/><rect x="146" y="243" width="8" height="8"/><rect x="195" y="237" width="8" height="8"/>
    <rect x="245" y="229" width="8" height="8"/><rect x="305" y="170" width="8" height="8"/>
  </g>
  <g font-size="12" fill="currentColor">
    <text x="74" y="274" text-anchor="end">0</text>
    <text x="74" y="34" text-anchor="end">1</text>
    <text x="320" y="286" text-anchor="middle">1</text>
    <text x="200" y="302" text-anchor="middle">mean predicted probability</text>
    <text x="20" y="20">observed fraction positive</text>
  </g>
  <g font-size="13" fill="currentColor">
    <text x="370" y="70">green circles: logistic model</text>
    <text x="370" y="90">on the diagonal, ECE 0.006</text>
    <text x="370" y="130">orange squares: same ranking,</text>
    <text x="370" y="150">log-odds 3z + 6, ECE 0.126;</text>
    <text x="370" y="170">says 0.95, truth 0.40</text>
    <text x="370" y="210">both have AUC 0.8777</text>
  </g>
</svg>
<figcaption>Figure 7.4. A reliability diagram of the two models in block 5, five bins each. The ROC curve cannot tell them apart; calibration can.</figcaption>
</figure>

Modern deep networks are often overconfident: Guo et al. (2017) found that the networks they studied were less well
calibrated than older, smaller ones, and that a single learned "temperature" dividing the scores fixed most of it.

### The Brier score is a proper scoring rule

The **Brier score** (Brier 1950, for weather forecasts) is the mean squared error of the probabilities:
$\mathrm{BS}=\frac1n\sum(p_i-y_i)^2$, with $y_i\in\{0,1\}$. Lower is better. Unlike ECE it needs no bins, and unlike AUC
it rewards both ranking and calibration: the miscalibrated model scores $0.1234$, worse even than the constant forecast
of the base rate ($0.0804$), while the logistic model scores $0.0589$.

Why squared error and not, say, absolute error? A scoring rule should make honesty the best policy: if you believe the
probability is $p$, reporting $p$ should minimise your expected score. Such a rule is called **proper**.

**Theorem 7.4.** If $Y$ is 1 with probability $p$, the expected Brier score of reporting $q$ is
$\mathbb E[(q-Y)^2]=(q-p)^2+p(1-p)$, minimised uniquely at $q=p$. The absolute score $\mathbb E|q-Y|$ is not proper.

*Proof.* $\mathbb E[(q-Y)^2]=p(q-1)^2+(1-p)q^2=q^2-2pq+p=(q-p)^2+p-p^2$. The first term is zero only at $q=p$, and
the second does not depend on $q$. For the absolute score, $\mathbb E|q-Y|=p(1-q)+(1-p)q=p+q(1-2p)$, which is linear in
$q$: if $p>\tfrac12$ it is minimised at $q=1$, otherwise at $q=0$. It rewards exaggerating to 0 or 1. $\square$

The log loss of Chapter 6, $-[y\ln q+(1-y)\ln(1-q)]$, is also proper (its expectation $-[p\ln q+(1-p)\ln(1-q)]$ has
derivative $-p/q+(1-p)/(1-q)$, zero only at $q=p$), which is one more reason maximum likelihood tends to produce
calibrated models. Murphy (1973) showed that the Brier score splits into three parts, $\text{reliability}-\text{resolution}
+\text{uncertainty}$: a calibration error, a reward for separating the classes, and the irreducible $\bar y(1-\bar y)$.

### Fixing calibration

**Platt scaling** (Platt 1999, originally for support vector machine scores) fits a one-variable logistic regression
$\sigma(a+b\,s)$ on top of the model's score $s$, using held-out data. It cannot change the ranking, only the meaning of
the scores. On the miscalibrated model, with $s$ its log-odds $3z+6$, the program fits $a=-2.00$ and $b=0.333$, which
exactly undoes the distortion (since $z=(s-6)/3=s/3-2$), and the Brier score returns to $0.0589$. **Isotonic regression**
(Zadrozny and Elkan 2002) fits any increasing step function instead, which is more flexible and needs more data. And
**temperature scaling** is Platt scaling with $a=0$ applied to the softmax scores of a network. The calibration map must
be fitted on data not used to train the model, or it will learn the model's overconfidence on its own training set.

## 7.7 Comparing models: intervals, the bootstrap and tests

*Level: intermediate to advanced.*

You measured 85 percent accuracy on 100 test examples. How sure are you? Another model scored 82 percent. Is it worse?
You tried 100 models and the best scored 59.5 percent on a problem where 50 percent is chance. Did you find something?
Each question needs the idea that a test score is a *random* quantity: a different test set from the same source would
give a different number.

### A confidence interval for an accuracy

If the model's true accuracy is $a$ and the $m$ test examples are independent draws, the number correct is binomial,
and the measured accuracy $\hat a$ has mean $a$ and standard deviation $\sqrt{a(1-a)/m}$. By the central limit theorem
$\hat a$ is roughly normal for large $m$, which gives the textbook 95 percent interval
$\hat a\pm1.96\sqrt{\hat a(1-\hat a)/m}$. (A **95 percent confidence interval** is a procedure that, over repeated
experiments, contains the true value 95 percent of the time; it is not a 95 percent probability statement about one
interval.)

Block 5 shows the sizes involved and a flaw. With 85 of 100 correct, the interval is $[0.780,0.920]$: fourteen points
wide. With 850 of 1000 it is $[0.828,0.872]$. To halve the width you need four times the test data. With 99 of 100, the
normal interval runs to $1.010$, an impossible accuracy: the normal approximation fails near 0 and 1. The **Wilson
interval** (Wilson 1927) inverts the test instead of plugging in $\hat a$, and stays inside $[0,1]$: $[0.946,0.998]$.
Use it routinely.

### The bootstrap

For measures with no simple formula, such as AUC, F1 or a median error, Efron's **bootstrap** (Efron 1979) estimates
the uncertainty by resampling. Draw $m$ examples *with replacement* from the $m$ test examples (some appear twice, some
not at all), recompute the measure, and repeat a few thousand times. The spread of the recomputed values approximates
the sampling spread of the measure, and the 2.5th and 97.5th percentiles give a **percentile bootstrap interval**. The
idea is that the test set is our best picture of the population, so sampling from it imitates sampling from the
population. It is an approximation, and it can be poor for very small samples or for statistics that depend on extreme
values; Efron and Tibshirani's book (1993) covers better variants.

### Comparing two models on the same test set

The key word is **paired**. Both models are scored on the same examples, and their errors are correlated: hard
examples are hard for both. Comparing two separate intervals ignores this and is far too cautious. Instead, look at the
*difference* on each example.

Block 6 simulates two models on 500 examples: A scores 0.860, B scores 0.832. The **paired bootstrap** resamples
*examples* (keeping each example's pair of results together) and recomputes the difference; its 95 percent interval
is $[+0.002,+0.054]$, just excluding zero.

**McNemar's test** (McNemar 1947) uses only the examples on which the models disagree: $n_{01}=30$ where A is right and
B wrong, and $n_{10}=16$ the other way. If the two models were equally accurate, each disagreement would be equally
likely to go either way, like a fair coin, so $n_{01}$ would be about half of 46. The test statistic
$\chi^2=(|n_{01}-n_{10}|-1)^2/(n_{01}+n_{10})=13^2/46=3.67$ (the $-1$ is a continuity correction) is compared with a
chi-square distribution with one degree of freedom, giving $p=0.055$. A **p-value** is the probability, if there were no
real difference, of seeing a difference at least this large; small values are evidence against "no difference".
Dietterich (1998) studied such tests for comparing learning algorithms and recommended McNemar's test when each
algorithm can be run only once.

The two methods disagree about whether $0.028$ is "significant", one just inside the 5 percent line and one just
outside. That is the honest lesson: the evidence is borderline, and no single threshold turns it into certainty.
Report the difference with its interval, and do not pretend the line at 0.05 is sharp.

### The multiple-comparisons trap

Block 7 makes 100 "models" that are pure coin flips and scores each on the same 200 test labels. The best one scores
59.5 percent. Taken alone, a coin scoring at least 119 of 200 has probability $0.0044$: "highly significant". But we
tried 100 coins, and 7 of them pass the $p<0.05$ line (about 5 would be expected by chance). The question that matters
is: how likely is the *best of 100* to score this well? A simple safe answer is the **Bonferroni correction**: multiply
each p-value by the number of comparisons. Here $0.0044\times100=0.44$: nothing at all. (Bonferroni is conservative;
Holm's step-down method (Holm 1979) is uniformly more powerful, and the Benjamini-Hochberg procedure (1995) controls the
expected fraction of false discoveries instead.)

This is the reason for the rule from Chapter 1 that the test set is used **once**. Every time you look at the test
score and change something, the test set becomes a little more like a validation set, and its score a little more
optimistic. Public benchmarks with leaderboards face the same problem at scale. Dwork et al. (2015) studied how to reuse
a holdout set safely by adding noise to the answers; Recht et al. (2019) built new test sets for the CIFAR-10 and
ImageNet benchmarks following the original collection process and found that accuracies dropped for all the models they
tested, while the ranking of models was largely preserved. For comparing algorithms across many data sets, Demšar (2006)
recommends rank-based tests (Wilcoxon, Friedman) over averaging accuracies.

**In practice.** scikit-learn's `metrics` module computes every measure in this chapter (`confusion_matrix`,
`precision_recall_fscore_support`, `roc_auc_score`, `average_precision_score`, `brier_score_loss`), its
`model_selection` module provides `KFold`, `StratifiedKFold`, `GroupKFold`, `TimeSeriesSplit` and `cross_val_score`,
and `calibration` provides reliability curves and Platt and isotonic calibration. `statsmodels` has McNemar's test and
the Wilson interval; `scipy.stats.bootstrap` does bootstrap intervals.

## Check yourself

??? question "1. A test for a disease present in 1 in 1000 people has recall 0.99 and specificity 0.99. Of the people it flags, what fraction actually have the disease?"

    Take 100000 people: 100 have the disease, and the test flags 99 of them. Of the 99900 healthy people, 1 percent,
    999, are flagged. Precision is $99/(99+999)=99/1098\approx0.090$: only 9 percent of positives are real. Precision
    depends on the base rate; recall and specificity do not. This is Bayes' rule (Chapter 3) in disguise.

??? question "2. From the confusion matrix TP = 40, FP = 10, FN = 20, TN = 130, compute accuracy, precision, recall, specificity and F1."

    $n=200$. Accuracy $170/200=0.85$. Precision $40/50=0.8$. Recall $40/60\approx0.667$. Specificity $130/140\approx0.929$.
    $F_1=2\cdot40/(80+10+20)=80/110\approx0.727$, which equals $2(0.8)(0.667)/(0.8+0.667)$.

??? question "3. Compute the AUC of the scores $(0.9, 0.8, 0.7, 0.6, 0.5)$ with labels $(1, 0, 1, 1, 0)$ by counting pairs, and draw the ROC staircase."

    Negatives at 0.8 and 0.5. Positives above 0.8: one (0.9). Positives above 0.5: three. Pairs correct: $1+3=4$ out of
    $3\times2=6$, so $\mathrm{AUC}=2/3$. The staircase: up to $(0,1/3)$, right to $(1/2,1/3)$, up twice to $(1/2,1)$, right to
    $(1,1)$. Area: $\tfrac12\cdot\tfrac13+\tfrac12\cdot1=\tfrac23$.

??? question "4. Show that multiplying all scores by 2 and adding 5 does not change the ROC curve. Does it change the Brier score?"

    The ROC curve depends only on which examples are above each threshold, and $s\mapsto2s+5$ preserves order, so the
    sequence of steps is the same. The Brier score does change (and the new scores may not even be probabilities), since
    it uses the values themselves.

??? question "5. For the data $y=(1, 2, 3, 10)$, find the constants minimising MSE and MAE and give each metric's value."

    Mean $4$: MSE $(9+4+1+36)/4=12.5$. Any $c$ in $[2,3]$ is a median: MAE at $c=2$ is $(1+0+1+8)/4=2.5$ (the same for
    every $c$ in $[2,3]$). The mean's MAE is $(3+2+1+6)/4=3$, worse; the median $2.5$ has MSE $(2.25+0.25+0.25+56.25)/4=14.75$,
    worse than the mean. Each metric prefers its own centre.

??? question "6. Why is $R^2$ computed on a test set allowed to be negative, while least-squares $R^2$ on training data (with an intercept) is not?"

    On training data, the least-squares fit minimises MSE over all lines, including the flat line at $\bar y$, so its MSE
    is at most $\mathrm{Var}(y)$ and $R^2\ge0$. On test data, the model was not chosen to minimise the test MSE, and the
    test mean is a different baseline, so the model can be worse than the test mean: $R^2<0$.

??? question "7. Write the code: stratified $k$-fold splitting. Given labels $y$, return $k$ index arrays whose class proportions match the whole."

    ```python
    import numpy as np

    def stratified_folds(y, k, seed=0):
        r = np.random.default_rng(seed)
        folds = [[] for _ in range(k)]
        for c in np.unique(y):
            idx = r.permutation(np.flatnonzero(y == c))
            for j, part in enumerate(np.array_split(idx, k)):
                folds[j].extend(part.tolist())
        return [np.array(sorted(f)) for f in folds]

    y = np.array([0] * 90 + [1] * 10)
    for f in stratified_folds(y, 5):
        print(len(f), y[f].sum())          # 20 examples, 2 positives in each fold
    ```

    Each class is shuffled and dealt out separately, so every fold gets its share of each class. With only 10 positives,
    unstratified folds could easily get 0 or 5 of them.

??? question "8. A colleague normalises all features to mean 0 and variance 1 using the whole data set, then runs 10-fold CV. Is this leakage? How bad is it likely to be?"

    Strictly yes: the means and variances used to scale the validation fold were computed partly from that fold. The
    effect is usually small, because a mean and variance carry little information about the labels, unlike the feature
    selection of block 3, which looks at the labels directly. The safe habit is still to fit the scaler inside each fold,
    since it costs nothing and some preprocessing steps (target encoding, imputation from labels, feature selection) leak
    badly.

??? question "9. Prove that the log loss is proper: if $Y\sim$ Bernoulli($p$), the expected log loss of reporting $q$ is minimised at $q=p$."

    $g(q)=-p\ln q-(1-p)\ln(1-q)$ for $0<q<1$. $g'(q)=-p/q+(1-p)/(1-q)$, which is zero when $p(1-q)=(1-p)q$, that is
    $q=p$. $g''(q)=p/q^2+(1-p)/(1-q)^2>0$, so this is the unique minimum. The minimum value $g(p)$ is the entropy of the
    Bernoulli distribution, and $g(q)-g(p)$ is the KL divergence from $p$ to $q$ (Chapter 3).

??? question "10. Write the code: a bootstrap 95 percent interval for the AUC of the chapter's ten-example table. Why is the interval so wide?"

    ```python
    import numpy as np
    y = np.array([1, 1, 0, 1, 0, 1, 0, 0, 1, 0])
    s = np.array([0.95, 0.85, 0.80, 0.70, 0.55, 0.45, 0.40, 0.30, 0.20, 0.10])

    def auc(y, s):
        d = s[y == 1][:, None] - s[y == 0][None, :]
        return np.mean((d > 0) + 0.5 * (d == 0))

    r = np.random.default_rng(0)
    vals = []
    while len(vals) < 5000:
        i = r.integers(0, 10, size=10)
        if 0 < y[i].sum() < 10:              # need both classes
            vals.append(auc(y[i], s[i]))
    print(np.percentile(vals, [2.5, 97.5]))
    ```

    It prints about $[0.31, 1.0]$: with five positives and five negatives, the AUC is the average of only 25 pair
    comparisons, all depending on the same ten points, so a different sample of ten could easily give anything from
    "useless" to "perfect". Ten test examples cannot establish that a model works.

??? question "11. You compare 20 hyperparameter settings on one validation set and the best beats the default with p = 0.01. What is the Bonferroni-adjusted p-value, and what should you do next?"

    $0.01\times20=0.2$, not significant after accounting for the search. The right next step is to confirm on data that
    played no part in the search (a fresh test set, or nested CV), and to report that 20 settings were tried.

??? question "12. (Advanced) Explain why the outer score of nested CV estimates the performance of 'tune by inner CV, then train', not of the final model with its chosen setting."

    In each outer fold the chosen setting can differ, and each model is trained on a different subset. The outer folds
    therefore score the whole *procedure*: given a data set of this size, run the inner search and train. That is what
    will happen when the procedure is applied to all the data, so the outer mean is an honest estimate for the final
    model's expected performance, with a small pessimistic bias because each outer training set is smaller than the full
    data. It is not an estimate for one fixed setting, and the settings chosen in different outer folds are not
    themselves the answer.

## What you learned

- Accuracy is meaningless without the trivial baseline; on imbalanced data the majority-class "model" can score above
  90 percent and find nothing.
- The confusion matrix gives precision (how often a flag is right), recall (how many positives are found), specificity
  and F1; the threshold trades them, and the right trade depends on costs.
- The ROC curve plots TPR against FPR over all thresholds; its area is the probability that a random positive is
  ranked above a random negative (proved), and it ignores calibration and class balance. Precision-recall curves expose
  false alarms on rare classes.
- MSE rewards predicting the mean, MAE the median (proved); $R^2$ compares with the mean and can be negative on new
  data.
- $k$-fold CV uses every example for validation once; for least squares, leave-one-out is free through $e_i/(1-h_{ii})$
  (proved). Every data-dependent step belongs inside the CV loop, and tuning needs nested CV or a final test set.
- Calibration asks whether probabilities mean what they say; reliability diagrams and ECE show it, the Brier score and
  log loss are proper scoring rules (proved), and Platt scaling repairs it.
- Test scores are random: report intervals (Wilson, bootstrap), compare models with paired methods (McNemar, paired
  bootstrap), and correct for the number of comparisons.

**Next:** [Chapter 8](08-Overfitting-and-Regularization.md) explains *why* training scores are optimistic, splits error
into bias and variance, and controls it with ridge, lasso and early stopping.

## Further reading

- T. Hastie, R. Tibshirani and J. Friedman, *The Elements of Statistical Learning*, 2nd ed., 2009: chapter 7 (model
  assessment and selection, including 7.10.2, the wrong way to cross-validate).
- K. P. Murphy, *Probabilistic Machine Learning: An Introduction*, 2022: sections on classifier evaluation and
  calibration.
- B. Efron and R. J. Tibshirani, *An Introduction to the Bootstrap*, 1993.
- T. Fawcett, "An Introduction to ROC Analysis", *Pattern Recognition Letters* 27(8), 2006.
- J. Davis and M. Goadrich, "The Relationship Between Precision-Recall and ROC Curves", ICML 2006.
- H. B. Mann and D. R. Whitney, "On a Test of Whether One of Two Random Variables is Stochastically Larger than the
  Other", *Annals of Mathematical Statistics* 18(1), 1947.
- G. W. Brier, "Verification of Forecasts Expressed in Terms of Probability", *Monthly Weather Review* 78(1), 1950;
  A. H. Murphy, "A New Vector Partition of the Probability Score", *Journal of Applied Meteorology* 12(4), 1973.
- J. Platt, "Probabilistic Outputs for Support Vector Machines and Comparisons to Regularized Likelihood Methods", in
  *Advances in Large Margin Classifiers*, 1999; C. Guo, G. Pleiss, Y. Sun and K. Q. Weinberger, "On Calibration of
  Modern Neural Networks", ICML 2017.
- Q. McNemar, "Note on the sampling error of the difference between correlated proportions or percentages",
  *Psychometrika* 12(2), 1947; T. G. Dietterich, "Approximate Statistical Tests for Comparing Supervised Classification
  Learning Algorithms", *Neural Computation* 10(7), 1998.
- E. B. Wilson, "Probable Inference, the Law of Succession, and Statistical Inference", *Journal of the American
  Statistical Association* 22(158), 1927.
- B. Efron, "Bootstrap Methods: Another Look at the Jackknife", *Annals of Statistics* 7(1), 1979.
- Y. Bengio and Y. Grandvalet, "No Unbiased Estimator of the Variance of K-Fold Cross-Validation", *JMLR* 5, 2004.
- S. Varma and R. Simon, "Bias in error estimation when using cross-validation for model selection", *BMC
  Bioinformatics* 7, 2006; G. C. Cawley and N. L. C. Talbot, "On Over-fitting in Model Selection and Subsequent
  Selection Bias in Performance Evaluation", *JMLR* 11, 2010.
- J. Demšar, "Statistical Comparisons of Classifiers over Multiple Data Sets", *JMLR* 7, 2006.
- C. Dwork, V. Feldman, M. Hardt, T. Pitassi, O. Reingold and A. Roth, "The reusable holdout: Preserving validity in
  adaptive data analysis", *Science* 349(6248), 2015; B. Recht, R. Roelofs, L. Schmidt and V. Shankar, "Do ImageNet
  Classifiers Generalize to ImageNet?", ICML 2019.
- On this site: [Chapter 1](01-What-Is-Machine-Learning.md) (held-out data), [Chapter 2](02-Data-and-Features.md)
  (leakage), [Chapter 22](22-Machine-Learning-in-Practice.md) (distribution shift and fairness metrics), and the
  [statistics book](https://math.akadian.ca/books/statistics/) for confidence intervals and tests.
