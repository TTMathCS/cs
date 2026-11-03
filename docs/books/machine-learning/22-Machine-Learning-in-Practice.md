# 22. Machine learning in practice

*A model that scores well in a notebook is not yet a system anyone can rely on. Real data arrives late, drifts,
and leaks; people ask why a decision was made and whether it treats groups alike; attackers nudge inputs; and the
data itself may be private. This chapter is about the distance between Chapter 21's i.i.d. world and the real one.
You will build a reproducible pipeline and catch a leak that fools cross-validation, detect and correct
distribution shift, measure fairness and prove why its criteria conflict, compute explanations exactly, attack a
model with adversarial examples and defend it, add differential privacy and federated training, and finally see
what the big libraries do for you.*

!!! abstract "In this chapter"
    **You will learn:**

    - how to make a training run reproducible, and how preprocessing done outside the split leaks information
    - the three kinds of distribution shift, how to detect them with two-sample tests and domain classifiers, and
      how to correct covariate shift (importance weights) and label shift (prior re-estimation)
    - the group fairness metrics, and a proof that calibration and equal error rates cannot all hold when base
      rates differ
    - interpretability tools from scratch: coefficients, permutation importance, exact Shapley values, gradient
      saliency, and where each one misleads
    - adversarial examples, the fast gradient sign method, why high dimension makes linear models fragile, and
      adversarial training
    - differential privacy (randomized response, the Laplace mechanism) and federated averaging
    - what scikit-learn, PyTorch and JAX add to the from-scratch code of this book

    **You need:** [Chapter 6](06-Classification-and-Logistic-Regression.md) (logistic regression),
    [Chapter 7](07-Evaluating-Models.md) (metrics, cross-validation, calibration),
    [Chapter 2](02-Data-and-Features.md) (splitting and leakage) and, for the sense of what goes wrong when its
    assumptions fail, [Chapter 21](21-Learning-Theory.md).

    **Levels:** 22.1 and 22.7 are beginner; 22.2 to 22.4 are intermediate; 22.5 and 22.6 are advanced.

## 22.1 From notebook to system: pipelines, reproducibility, versioning data

Suppose a model you trained last month is giving odd answers, and you want to know why. You open the notebook. The
cells were run in an order nobody remembers, the data file has since been overwritten by a newer export, and the
random seed was never set. You cannot recreate the model you are trying to debug. This is the most common failure in
applied machine learning, and it has nothing to do with algorithms.

A **pipeline** is the whole path from raw data to a prediction, written as code that runs from start to finish
without a human in between: load, clean, split, fit the preprocessing, fit the model, evaluate, save. Three
properties make a pipeline trustworthy.

**Reproducible.** Running it twice on the same inputs gives the same model, bit for bit. That needs every source of
randomness to come from a seed you record (shuffles, initial weights, dropout masks, data augmentation), and the
code, library versions and data to be pinned. Some sources are harder: parallel floating-point sums can depend on
thread timing, so deep-learning frameworks have "deterministic" switches that trade speed for exact repeatability.

**Versioned.** Code is versioned with a version-control system; data needs the same. The simplest honest method is a
**fingerprint**: a cryptographic hash of the exact bytes of the training data, stored with the model. If the
fingerprint changes, the data changed, however similar the file name. (A hash function maps any input to a short
string such that, in practice, different inputs never give the same string; the Cryptography book's chapter on hash
functions explains why.) Larger systems keep immutable snapshots of each dataset version.

**Leak-free.** Everything that learns from data, including the "preprocessing" (the scaler's mean, the vocabulary of
an encoder, the list of selected features, the imputation value for missing entries), is fitted on the training rows
only and then applied unchanged to validation and test rows. A pipeline object enforces this by having one `fit`
that sees only training data.

```python
--8<-- "books/machine-learning/ch22_pipeline_shift.py"
```

```
1. reproducibility: same data + same seed -> same model, bit for bit
   seed 0: data dfab0c56d8ad2aa6  model 7958bd37f9a21fe8
   seed 0: data dfab0c56d8ad2aa6  model 7958bd37f9a21fe8
   seed 1: data 51324875790fb089  model 1bfb442a6cf50e3e

2. 2000 noise features, random labels, n = 100; keep the 20 most correlated features
   selection on ALL data, then 5-fold CV:   accuracy 0.810   (a leak)
   selection inside each training fold:     accuracy 0.490   (honest)

3. covariate shift: train x ~ N(0, 1), deployment x ~ N(1.5, 0.6^2), same rule y = sin(1.5 x) + noise
   Kolmogorov-Smirnov statistic 0.715, permutation p-value 0.0020
   (two halves of the training set: statistic 0.070, p-value 0.6966)
   domain classifier AUC on held-out rows: 0.920  (0.5 = no shift)
   cubic fit, ordinary least squares: train MSE 0.0303   deployment MSE 0.1565
   cubic fit, importance-weighted   : train MSE 7.9580   deployment MSE 0.0169
   effective sample size of the weights: 54 of 400

4. label shift: training prior 0.5, deployment prior 0.1
   validation TPR 0.840, FPR 0.158; deployment predicted-positive rate 0.229
   estimated deployment prior (rate - FPR) / (TPR - FPR) = 0.104
   unadjusted      accuracy 0.844   log loss 0.351   mean predicted P(y=1) 0.287
   prior-adjusted  accuracy 0.931   log loss 0.182   mean predicted P(y=1) 0.102
```

Part 1 shows reproducibility as a fact you can check: the same seed gives the same data fingerprint and the same
model fingerprint; a different seed changes both.

Part 2 is a famous leak, described in Hastie, Tibshirani and Friedman's *Elements of Statistical Learning* (section
7.10.2, "the wrong and right way to do cross-validation"). There are 100 rows, 2000 features of pure noise, and
labels that are coin flips, so no model can do better than 50% on new data. The wrong way: pick the 20 features most
correlated with the labels using *all* 100 rows, then cross-validate a model on those 20. Cross-validation reports
81% accuracy. The right way: do the selection inside each training fold. Cross-validation reports 49%, the truth.
What happened? With 2000 noise features, some are correlated with the labels by chance in *these* 100 rows,
including the rows later used for testing. The selection step saw the test labels. Cross-validation can only
protect the steps that run inside it. Ambroise and McLachlan (PNAS, 2002) found this exact error in published
gene-expression studies.

Other leaks to look for, all from real projects in disguise:

- **Duplicates across the split.** The same customer, patient or image appears in train and test (often after
  augmentation or a merge). Split by entity (group split, Chapter 2), not by row.
- **The future in the features.** A "number of support calls" column computed over the whole year, used to predict
  cancellations in March. Every feature must be computable at the moment of prediction.
- **Proxies for the label.** A column filled in only after the outcome is known (a "reason for refund" field when
  predicting refunds).
- **Target encoding without folds.** Replacing a category by the average label of its rows, computed on all rows,
  hands each row a little of its own label.

Kaufman, Rosset, Perlich and Stitelman ("Leakage in data mining", ACM TKDD 2012) collect many more.

<figure class="mars-fig" markdown="0">
<svg viewBox="0 0 680 190" role="img" aria-label="A machine learning pipeline as a loop: raw data, a versioned snapshot, features, training, evaluation, deployment and monitoring; monitoring feeds back to new data. Code, data version and random seed are recorded at every step.">
<rect x="12" y="50" width="84" height="40" rx="6" fill="none" stroke="currentColor" stroke-width="1.3"/>
<text x="54.0" y="67" font-size="12" text-anchor="middle" fill="currentColor">raw</text>
<text x="54.0" y="82" font-size="12" text-anchor="middle" fill="currentColor">data</text>
<line x1="96" y1="70.0" x2="105" y2="70.0" stroke="currentColor" stroke-width="1.4"/>
<polygon points="108,70.0 103,66.5 103,73.5" fill="currentColor"/>
<rect x="108" y="50" width="84" height="40" rx="6" fill="none" stroke="currentColor" stroke-width="1.3"/>
<text x="150.0" y="67" font-size="12" text-anchor="middle" fill="currentColor">versioned</text>
<text x="150.0" y="82" font-size="12" text-anchor="middle" fill="currentColor">snapshot</text>
<line x1="192" y1="70.0" x2="201" y2="70.0" stroke="currentColor" stroke-width="1.4"/>
<polygon points="204,70.0 199,66.5 199,73.5" fill="currentColor"/>
<rect x="204" y="50" width="84" height="40" rx="6" fill="none" stroke="currentColor" stroke-width="1.3"/>
<text x="246.0" y="75" font-size="13" text-anchor="middle" fill="currentColor">features</text>
<line x1="288" y1="70.0" x2="297" y2="70.0" stroke="currentColor" stroke-width="1.4"/>
<polygon points="300,70.0 295,66.5 295,73.5" fill="currentColor"/>
<rect x="300" y="50" width="84" height="40" rx="6" fill="#eea66f" fill-opacity="0.45" stroke="currentColor" stroke-width="1.3"/>
<text x="342.0" y="75" font-size="13" text-anchor="middle" fill="currentColor">train</text>
<line x1="384" y1="70.0" x2="393" y2="70.0" stroke="currentColor" stroke-width="1.4"/>
<polygon points="396,70.0 391,66.5 391,73.5" fill="currentColor"/>
<rect x="396" y="50" width="84" height="40" rx="6" fill="none" stroke="currentColor" stroke-width="1.3"/>
<text x="438.0" y="75" font-size="13" text-anchor="middle" fill="currentColor">evaluate</text>
<line x1="480" y1="70.0" x2="489" y2="70.0" stroke="currentColor" stroke-width="1.4"/>
<polygon points="492,70.0 487,66.5 487,73.5" fill="currentColor"/>
<rect x="492" y="50" width="84" height="40" rx="6" fill="none" stroke="currentColor" stroke-width="1.3"/>
<text x="534.0" y="75" font-size="13" text-anchor="middle" fill="currentColor">deploy</text>
<line x1="576" y1="70.0" x2="585" y2="70.0" stroke="currentColor" stroke-width="1.4"/>
<polygon points="588,70.0 583,66.5 583,73.5" fill="currentColor"/>
<rect x="588" y="50" width="84" height="40" rx="6" fill="#9cc9ea" fill-opacity="0.45" stroke="currentColor" stroke-width="1.3"/>
<text x="630.0" y="75" font-size="13" text-anchor="middle" fill="currentColor">monitor</text>
<path d="M 630.0 90 L 630.0 130 L 54.0 130 L 54.0 96" fill="none" stroke="currentColor" stroke-width="1.4" stroke-dasharray="5 4"/>
<polygon points="54.0,90 50.5,96 57.5,96" fill="currentColor"/>
<text x="342.0" y="124" font-size="12" text-anchor="middle" fill="currentColor">shift detected or new labels arrive: retrain on a new snapshot</text>
<text x="340" y="30" font-size="13" text-anchor="middle" fill="currentColor">every arrow records: code version, data fingerprint, random seed, parameters</text>
<text x="340" y="175" font-size="12" text-anchor="middle" fill="currentColor">the scaler, encoders and feature choices are fitted inside "train", on training rows only</text>
</svg>
<figcaption>Figure 22.1. A pipeline as a loop. Every step is code, each run records its code version, data
fingerprint and seed, and everything that learns from data is fitted inside the training step. Monitoring closes the
loop.</figcaption>
</figure>

**Monitoring.** A deployed model needs instruments, like any machine: the distribution of each input feature, the
distribution of predictions, and, when labels arrive later, the error. Sculley and co-authors ("Hidden technical debt
in machine learning systems", NeurIPS 2015) observed that in mature systems the model code is a small part of the
whole; the rest is data collection, verification, feature extraction, serving and monitoring. Documentation practices
such as **datasheets for datasets** (Gebru et al., 2021) and **model cards** (Mitchell et al., 2019) record what data
a model was trained on and where it was evaluated, so that the next person knows its limits.

A Mars rover makes the point sharply. Curiosity's AEGIS software picks rock targets for its ChemCam laser on its own,
from images, because a round trip of commands to Earth takes between about 8 and 48 minutes and the rover would
otherwise sit idle. A system that acts without a human in the loop must have been tested on the conditions it will
meet, and must report what it saw, so that its operators can check it after the fact. The same is true, less
dramatically, of every deployed model.

## 22.2 Distribution shift: covariate, label, concept; detecting it

*Level: intermediate.*

Every guarantee in Chapter 21 assumed that the training examples and the future examples come from one distribution
$\mathcal D$. In practice they rarely do: a model trained on last year's customers serves this year's; a medical
model trained in one hospital is used in another; a vision model trained on daytime images meets night. When the
deployment distribution $Q$ differs from the training distribution $P$ we speak of **distribution shift** (or
dataset shift). Write the joint distribution of an input $x$ and a label $y$ in two ways,

$$
P(x, y) = P(x)\,P(y \mid x) = P(y)\,P(x \mid y),
$$

and the three basic kinds of shift are named by which factor changes.

- **Covariate shift**: $Q(x) \ne P(x)$ but $Q(y \mid x) = P(y \mid x)$. The inputs move to a new region, the rule that
  labels them is the same. (Inputs are called covariates in statistics.)
- **Label shift** (or prior shift): $Q(y) \ne P(y)$ but $Q(x \mid y) = P(x \mid y)$. The share of each class changes,
  but each class looks the same. A disease becomes rarer; its symptoms do not change.
- **Concept shift** (or concept drift): $Q(y \mid x) \ne P(y \mid x)$. The same input now deserves a different label:
  the meaning of "spam" changes as spammers adapt.

<figure class="mars-fig" markdown="0">
<svg viewBox="0 0 680 230" role="img" aria-label="Three kinds of distribution shift. Covariate shift: the input distribution moves, the labelling rule stays. Label shift: the share of each class changes, what each class looks like stays. Concept shift: inputs look the same, but the boundary between the classes moves.">
<rect x="15" y="10" width="200" height="170" rx="6" fill="none" stroke="currentColor" stroke-opacity="0.4"/>
<text x="115.0" y="200" font-size="13" text-anchor="middle" fill="currentColor" font-weight="bold">covariate shift</text>
<text x="115.0" y="218" font-size="12" text-anchor="middle" fill="currentColor">p(x) moves, p(y | x) fixed</text>
<rect x="240" y="10" width="200" height="170" rx="6" fill="none" stroke="currentColor" stroke-opacity="0.4"/>
<text x="340.0" y="200" font-size="13" text-anchor="middle" fill="currentColor" font-weight="bold">label shift</text>
<text x="340.0" y="218" font-size="12" text-anchor="middle" fill="currentColor">p(y) changes, p(x | y) fixed</text>
<rect x="465" y="10" width="200" height="170" rx="6" fill="none" stroke="currentColor" stroke-opacity="0.4"/>
<text x="565.0" y="200" font-size="13" text-anchor="middle" fill="currentColor" font-weight="bold">concept shift</text>
<text x="565.0" y="218" font-size="12" text-anchor="middle" fill="currentColor">p(x) fixed, p(y | x) changes</text>
<line x1="25" y1="160" x2="205" y2="160" stroke="currentColor"/>
<polyline points="25.0,155.2 29.0,152.8 33.0,149.5 37.0,145.1 41.0,139.5 45.0,132.6 49.0,124.3 53.0,114.8 57.0,104.3 61.0,93.3 65.0,82.3 69.0,71.9 73.0,62.9 77.0,55.9 81.0,51.5 85.0,50.0 89.0,51.5 93.0,55.9 97.0,62.9 101.0,71.9 105.0,82.3 109.0,93.3 113.0,104.3 117.0,114.8 121.0,124.3 125.0,132.6 129.0,139.5 133.0,145.1 137.0,149.5 141.0,152.8 145.0,155.2 149.0,156.9 153.0,158.0 157.0,158.8 161.0,159.3 165.0,159.6 169.0,159.8 173.0,159.9 177.0,159.9 181.0,160.0 185.0,160.0 189.0,160.0 193.0,160.0 197.0,160.0 201.0,160.0 205.0,160.0" fill="none" stroke="#eea66f" stroke-width="2.4"/>
<polyline points="25.0,160.0 29.0,160.0 33.0,160.0 37.0,160.0 41.0,160.0 45.0,160.0 49.0,160.0 53.0,160.0 57.0,160.0 61.0,160.0 65.0,160.0 69.0,160.0 73.0,160.0 77.0,160.0 81.0,159.9 85.0,159.9 89.0,159.7 93.0,159.4 97.0,158.8 101.0,157.7 105.0,155.8 109.0,152.8 113.0,148.2 117.0,141.5 121.0,132.6 125.0,121.2 129.0,107.9 133.0,93.3 137.0,78.7 141.0,65.7 145.0,55.9 149.0,50.7 153.0,50.7 157.0,55.9 161.0,65.7 165.0,78.7 169.0,93.3 173.0,107.9 177.0,121.2 181.0,132.6 185.0,141.5 189.0,148.2 193.0,152.8 197.0,155.8 201.0,157.7 205.0,158.8" fill="none" stroke="#9cc9ea" stroke-width="2.4" stroke-dasharray="6 3"/>
<text x="75" y="174" font-size="11" text-anchor="middle" fill="currentColor">training x</text>
<text x="165" y="174" font-size="11" text-anchor="middle" fill="currentColor">deployment x</text>
<line x1="255" y1="160" x2="425" y2="160" stroke="currentColor"/>
<rect x="270" y="100.0" width="28" height="60.0" fill="#9cc9ea" fill-opacity="0.7" stroke="currentColor"/>
<rect x="300" y="100.0" width="28" height="60.0" fill="#eea66f" fill-opacity="0.8" stroke="currentColor"/>
<text x="299" y="174" font-size="11" text-anchor="middle" fill="currentColor">training</text>
<text x="284" y="96.0" font-size="10" text-anchor="middle" fill="currentColor">50%</text>
<text x="314" y="96.0" font-size="10" text-anchor="middle" fill="currentColor">50%</text>
<rect x="355" y="52.0" width="28" height="108.0" fill="#9cc9ea" fill-opacity="0.7" stroke="currentColor"/>
<rect x="385" y="148.0" width="28" height="12.0" fill="#eea66f" fill-opacity="0.8" stroke="currentColor"/>
<text x="384" y="174" font-size="11" text-anchor="middle" fill="currentColor">deployment</text>
<text x="369" y="48.0" font-size="10" text-anchor="middle" fill="currentColor">90%</text>
<text x="399" y="144.0" font-size="10" text-anchor="middle" fill="currentColor">10%</text>
<rect x="360" y="22" width="10" height="10" fill="#9cc9ea" fill-opacity="0.7" stroke="currentColor"/><text x="374" y="31" font-size="11" fill="currentColor">class 0</text>
<rect x="360" y="38" width="10" height="10" fill="#eea66f" fill-opacity="0.8" stroke="currentColor"/><text x="374" y="47" font-size="11" fill="currentColor">class 1</text>
<circle cx="522.7" cy="101.2" r="4.5" fill="#9cc9ea" fill-opacity="0.8" stroke="currentColor" stroke-width="0.8"/>
<circle cx="544.8" cy="109.5" r="4.5" fill="#9cc9ea" fill-opacity="0.8" stroke="currentColor" stroke-width="0.8"/>
<circle cx="485.2" cy="142.2" r="4.5" fill="#9cc9ea" fill-opacity="0.8" stroke="currentColor" stroke-width="0.8"/>
<circle cx="526.3" cy="57.8" r="4.5" fill="#9cc9ea" fill-opacity="0.8" stroke="currentColor" stroke-width="0.8"/>
<circle cx="589.7" cy="46.1" r="4.5" fill="#eea66f" fill-opacity="0.8" stroke="currentColor" stroke-width="0.8"/>
<circle cx="589.0" cy="146.5" r="4.5" fill="#eea66f" fill-opacity="0.8" stroke="currentColor" stroke-width="0.8"/>
<circle cx="570.4" cy="128.8" r="4.5" fill="#9cc9ea" fill-opacity="0.8" stroke="currentColor" stroke-width="0.8"/>
<circle cx="595.1" cy="34.0" r="4.5" fill="#eea66f" fill-opacity="0.8" stroke="currentColor" stroke-width="0.8"/>
<circle cx="609.6" cy="107.8" r="4.5" fill="#eea66f" fill-opacity="0.8" stroke="currentColor" stroke-width="0.8"/>
<circle cx="603.0" cy="148.0" r="4.5" fill="#eea66f" fill-opacity="0.8" stroke="currentColor" stroke-width="0.8"/>
<circle cx="602.3" cy="154.0" r="4.5" fill="#eea66f" fill-opacity="0.8" stroke="currentColor" stroke-width="0.8"/>
<circle cx="557.3" cy="156.0" r="4.5" fill="#9cc9ea" fill-opacity="0.8" stroke="currentColor" stroke-width="0.8"/>
<circle cx="629.8" cy="38.6" r="4.5" fill="#eea66f" fill-opacity="0.8" stroke="currentColor" stroke-width="0.8"/>
<circle cx="505.7" cy="55.4" r="4.5" fill="#9cc9ea" fill-opacity="0.8" stroke="currentColor" stroke-width="0.8"/>
<circle cx="567.7" cy="79.0" r="4.5" fill="#9cc9ea" fill-opacity="0.8" stroke="currentColor" stroke-width="0.8"/>
<circle cx="541.6" cy="106.9" r="4.5" fill="#9cc9ea" fill-opacity="0.8" stroke="currentColor" stroke-width="0.8"/>
<circle cx="596.9" cy="155.1" r="4.5" fill="#eea66f" fill-opacity="0.8" stroke="currentColor" stroke-width="0.8"/>
<circle cx="626.0" cy="163.7" r="4.5" fill="#eea66f" fill-opacity="0.8" stroke="currentColor" stroke-width="0.8"/>
<circle cx="595.1" cy="47.8" r="4.5" fill="#eea66f" fill-opacity="0.8" stroke="currentColor" stroke-width="0.8"/>
<circle cx="626.7" cy="160.0" r="4.5" fill="#eea66f" fill-opacity="0.8" stroke="currentColor" stroke-width="0.8"/>
<circle cx="634.1" cy="104.7" r="4.5" fill="#eea66f" fill-opacity="0.8" stroke="currentColor" stroke-width="0.8"/>
<circle cx="602.2" cy="54.6" r="4.5" fill="#eea66f" fill-opacity="0.8" stroke="currentColor" stroke-width="0.8"/>
<circle cx="621.9" cy="105.3" r="4.5" fill="#eea66f" fill-opacity="0.8" stroke="currentColor" stroke-width="0.8"/>
<circle cx="625.6" cy="163.6" r="4.5" fill="#eea66f" fill-opacity="0.8" stroke="currentColor" stroke-width="0.8"/>
<circle cx="497.8" cy="137.1" r="4.5" fill="#9cc9ea" fill-opacity="0.8" stroke="currentColor" stroke-width="0.8"/>
<circle cx="551.5" cy="46.1" r="4.5" fill="#9cc9ea" fill-opacity="0.8" stroke="currentColor" stroke-width="0.8"/>
<line x1="580" y1="20" x2="580" y2="170" stroke="currentColor" stroke-width="1.8"/>
<line x1="510" y1="170" x2="650" y2="30" stroke="currentColor" stroke-width="1.8" stroke-dasharray="6 4"/>
<text x="573" y="34" font-size="11" text-anchor="end" fill="currentColor">old rule</text>
<text x="615" y="98" font-size="11" text-anchor="start" fill="currentColor">new rule</text>
</svg>
<figcaption>Figure 22.2. Three kinds of distribution shift. Covariate shift moves the inputs; label shift changes the
share of each class; concept shift moves the boundary between classes while the inputs look the same.</figcaption>
</figure>

### Detecting shift

Label shift and concept shift often cannot be seen without labels, but changes in the inputs can. The question "do
these two samples come from the same distribution?" is a **two-sample test**.

For one feature, the **Kolmogorov-Smirnov statistic** is the largest vertical gap between the two empirical
cumulative distribution functions (the function $F(t)$ = fraction of the sample at most $t$). It is 0 when the
samples interleave perfectly and 1 when one lies entirely to the left of the other. To turn it into a p-value without
any distribution theory, use a **permutation test**: if the two samples really came from one distribution, then
shuffling the pooled values and re-splitting them should produce gaps as large as the observed one fairly often. The
p-value is the fraction of shuffles that produce a gap at least as large (with one added to numerator and
denominator, so it is never exactly 0).

Part 3 of the program shifts the inputs from $N(0, 1)$ to $N(1.5, 0.6^2)$. The statistic is 0.715 and none of 500
shuffles came close (p-value $1/501 \approx 0.002$, the smallest this test can report). As a control, two halves of
the training set give 0.070 and p = 0.70: no evidence of a difference, as it should be.

For many features at once, testing each one separately raises the multiple-comparisons problem of Chapter 7 and
misses changes in how features relate to each other. A neat general method is the **domain classifier**: label every
training row 0 and every deployment row 1, train any classifier to tell them apart, and measure its AUC on held-out
rows. If the distributions are the same, no classifier can beat AUC 0.5; a high AUC is evidence of shift, and the
classifier's errors tell you *which* rows look different. Here the AUC is 0.920. Rabanser, Günnemann and Lipton
("Failing loudly", NeurIPS 2019) compared many such detectors on image data.

### Correcting covariate shift: importance weighting

If only $P(x)$ changes, the training data still carry the right labelling rule, but they spend their effort in the
wrong places. The fix rests on one line of algebra. For any loss $\ell$,

$$
E_{Q}\big[\ell(h(x), y)\big] = \int Q(x)\,Q(y \mid x)\,\ell\,dx\,dy
= \int P(x)\,P(y \mid x)\,\frac{Q(x)}{P(x)}\,\ell\,dx\,dy
= E_P\Big[\frac{Q(x)}{P(x)}\,\ell(h(x), y)\Big],
$$

using $Q(y \mid x) = P(y \mid x)$. So the deployment risk is the training risk with each example weighted by the
**importance weight** $w(x) = Q(x)/P(x)$, provided $P(x) > 0$ wherever $Q(x) > 0$. Shimodaira (2000) proposed
weighting the training loss this way. We rarely know the two densities, but the domain classifier gives the ratio for
free: if it estimates $c(x) = \Pr[\text{deployment} \mid x]$ and the two samples have equal size, Bayes' rule gives

$$
\frac{Q(x)}{P(x)} = \frac{c(x)}{1 - c(x)} .
$$

In Part 3 the target is $\sin(1.5x)$ and the model is a cubic polynomial, which cannot fit the sine everywhere. The
ordinary fit spends its flexibility near $x = 0$, where the training data are, and has deployment error 0.157. The
importance-weighted fit concentrates on the region around $x = 1.5$ and gets 0.017, nine times better. Its error on
the training distribution is terrible (7.96), and that is the point: it gave up regions that deployment will never
visit.

There is a price. When the weights vary a lot, a few training points dominate. The **effective sample size**
$(\sum w_i)^2 / \sum w_i^2$ measures how many equally weighted points the weighted sample is worth: here 54 of 400.
If the deployment region has no training data at all, no weighting can help; you need new data.

### Correcting label shift

Now suppose only the class shares change. A classifier trained with prior $\pi = P(y = 1)$ outputs $p(x)$, an
estimate of $P(y = 1 \mid x)$. By Bayes' rule, $P(y = 1 \mid x) \propto P(x \mid y = 1)\,\pi$. Since $P(x \mid y)$ does
not change, the deployment posterior has the same likelihoods and a new prior $\pi'$, so its odds are the old odds
multiplied by the ratio of prior odds:

$$
\frac{p'(x)}{1 - p'(x)} = \frac{p(x)}{1 - p(x)} \cdot \frac{\pi'/(1 - \pi')}{\pi/(1 - \pi)} .
$$

That needs $\pi'$, which we do not observe, because deployment data are unlabelled. But we can estimate it from the
classifier's own behaviour. Measure the true and false positive rates TPR and FPR on labelled validation data (they
depend only on $P(x \mid y)$, so they do not change). On deployment data, the fraction predicted positive is
$r = \mathrm{TPR}\cdot\pi' + \mathrm{FPR}\cdot(1 - \pi')$, so

$$
\pi' = \frac{r - \mathrm{FPR}}{\mathrm{TPR} - \mathrm{FPR}} .
$$

Forman (2008) called this "adjusted classify and count"; Lipton, Wang and Smola (ICML 2018) generalised it to many
classes with a confusion-matrix inverse (black-box shift estimation), and Saerens, Latinne and Decaestecker (2002)
gave an EM algorithm for the same job (exercise 7). In Part 4 the prior drops from 0.5 to 0.1. The estimate is 0.104.
After adjusting, accuracy rises from 0.844 to 0.931, the log loss halves, and the average predicted probability
matches the new prior (0.102 against 0.287 before).

### Concept shift

When $P(y \mid x)$ itself changes, old labels are partly wrong for the present, and the only cure is new labels. The
practical tools are monitoring the error on recent labelled data (with a sliding window, or a sequential change
detector), retraining on a schedule, and weighting recent data more. The survey by Gama, Žliobaitė, Bifet,
Pechenizkiy and Bouchachia (ACM Computing Surveys, 2014) describes the main families. Chapter 23 returns to the
harder version of the problem, learning continually without forgetting.

## 22.3 Fairness measured technically

*Level: intermediate.*

When a model's decisions affect people, one wants to know whether its errors fall evenly across groups (defined, say,
by age band or region). This section treats the question purely as measurement: which numbers can be computed, and
which combinations of them are mathematically possible. Which criterion is right for a given use is not a technical
question, and this book does not answer it.

Fix a binary label $y$, a score $s \in [0, 1]$, a decision $\hat y = \mathbf 1[s \ge t]$, and a group attribute
$g$. The main **group fairness criteria** compare, across groups:

- **Demographic parity**: the selection rate $\Pr[\hat y = 1 \mid g]$.
- **Equal opportunity** (Hardt, Price and Srebro, 2016): the true positive rate $\Pr[\hat y = 1 \mid y = 1, g]$.
- **Equalised odds** (same paper): both the true positive rate and the false positive rate
  $\Pr[\hat y = 1 \mid y = 0, g]$.
- **Predictive parity**: the positive predictive value $\mathrm{PPV} = \Pr[y = 1 \mid \hat y = 1, g]$, the share of
  selected people who really are positive.
- **Calibration within groups**: for every score value $v$, $\Pr[y = 1 \mid s = v, g] = v$; a score of 0.7 means 70%
  in every group.
- **Balance for the positive class** and **for the negative class** (Kleinberg, Mullainathan and Raghavan, 2016):
  $E[s \mid y = 1, g]$ and $E[s \mid y = 0, g]$ are the same across groups; the score version of equal error rates.

The **base rate** $p_g = \Pr[y = 1 \mid g]$ is the share of positives in group $g$. The program builds the most
favourable case imaginable: every person has a true risk $r$, the label is a coin with probability $r$, and the score
*is* $r$. No model can be more accurate or better calibrated. The only difference between the groups is the
distribution of risk, with base rates 0.3 and 0.5.

```python
--8<-- "books/machine-learning/ch22_fairness.py"
```

```
1. one threshold t = 0.5 for everyone, calibrated score
   group  base rate  selected   TPR     FPR     PPV    E[s|y=1]  E[s|y=0]
     A     0.299     0.090   0.172   0.056   0.568    0.364     0.273
     B     0.501     0.500   0.624   0.376   0.625    0.546     0.454

2. calibration check: in each score bin, mean score / fraction that are positive
   bin             group A          group B
   [0.0, 0.2)    0.139 / 0.136    0.163 / 0.166
   [0.2, 0.4)    0.294 / 0.294    0.323 / 0.323
   [0.4, 0.6)    0.476 / 0.473    0.500 / 0.502
   [0.6, 0.8)    0.655 / 0.651    0.676 / 0.676
   [0.8, 1.0)       (empty)       0.837 / 0.845

3. Chouldechova's identity FPR = p/(1-p) * (1-PPV)/PPV * (1-FNR), checked
   group A: FPR 0.0556   right-hand side 0.0556
   group B: FPR 0.3762   right-hand side 0.3762

4. equalise the false positive rate with a second threshold for group B
   group B threshold 0.689: FPR 0.056 (A: 0.056)   TPR 0.170 (A: 0.172)   PPV 0.755 (A: 0.568)

5. what happens when the base rates are equal (B drawn like A)
   new B: base 0.300  TPR 0.169  FPR 0.055  PPV 0.568  E[s|y=1] 0.363  E[s|y=0] 0.273   (all match group A)
```

Part 2 confirms calibration: in every bin, in both groups, the share of positives matches the mean score to within
0.01. Yet Part 1 shows that with a single threshold almost every other criterion fails: selection rates 0.09
and 0.50, true positive rates 0.17 and 0.62, false positive rates 0.06 and 0.38, PPV 0.57 and 0.63, and the class
balance numbers differ too. Part 4 equalises the false positive rate by giving group B its own threshold (0.689),
which here also nearly equalises the true positive rates (0.170 and 0.172), but now the PPVs are 0.755 and 0.568,
and two people with the same score are treated differently. Part 5 shows that the conflict disappears when base
rates are equal. These are not accidents of this simulation.

**Chouldechova's identity (2017).** In any group, from the definitions of the four confusion-matrix cells,

$$
\mathrm{FPR} = \frac{p}{1 - p}\cdot\frac{1 - \mathrm{PPV}}{\mathrm{PPV}}\cdot(1 - \mathrm{FNR}),
$$

where $\mathrm{FNR} = 1 - \mathrm{TPR}$. *Proof.* Write the cells as fractions of the group: TP $= p(1 - \mathrm{FNR})$ and FP
$= (1 - p)\,\mathrm{FPR}$. Then $\mathrm{PPV} = \mathrm{TP}/(\mathrm{TP} + \mathrm{FP})$, so
$\mathrm{FP} = \mathrm{TP}(1 - \mathrm{PPV})/\mathrm{PPV}$; substitute and divide by $1 - p$. $\square$ Part 3 checks
it to four decimals. The consequence: if two groups have different base rates $p$, then equal PPV and equal FNR force
unequal FPR. Predictive parity and equalised odds cannot hold together unless the classifier is perfect
($\mathrm{FPR} = \mathrm{FNR} = 0$) or the base rates are equal.

**Theorem 22.1 (Kleinberg, Mullainathan and Raghavan, 2016).** If a score is calibrated within each group and
satisfies balance for the positive class and for the negative class, then either the groups have equal base rates
or the score is perfect (it gives 1 to every positive and 0 to every negative).

*Proof (a short version of their argument).* In one group, let $z = E[s \mid y = 1]$ and $x = E[s \mid y = 0]$.
Calibration implies $E[s] = E\big[\Pr[y = 1 \mid s]\big] = \Pr[y = 1] = p$. The law of total expectation gives
$E[s] = p z + (1 - p) x$. So $p = pz + (1 - p)x$, which rearranges to

$$
p\,(1 - z + x) = x, \qquad\text{that is}\qquad p = \frac{x}{1 - z + x}\quad(\text{if } 1 - z + x \ne 0).
$$

Balance means $x$ and $z$ are the same in both groups, so the right side is the same, and so is $p$. The only escape
is $1 - z + x = 0$; since $0 \le x$ and $z \le 1$ this means $z = 1$ and $x = 0$: every positive gets score 1 and every
negative score 0. $\square$

Check with the program's numbers: group A has $x = 0.273$, $z = 0.364$, so $x/(1 - z + x) = 0.273/0.909 = 0.300$, its
base rate; group B gives $0.454/0.908 = 0.500$. The formula has no room for anything else.

Other technical notions exist: **individual fairness** (Dwork, Hardt, Pitassi, Reingold and Zemel, 2012) asks that
similar individuals get similar outputs, which needs a similarity measure; **counterfactual** notions use causal
models (Chapter 23 touches on causality). The technical lesson is the same in all of them: write down the criterion,
measure it with confidence intervals (the bootstrap of Chapter 7 works), and know which criteria are mutually
exclusive before choosing.

## 22.4 Interpretability

*Level: intermediate.*

"Why did the model say that?" can mean several things: which features matter to the model overall (**global**
explanation), which features pushed this one prediction up or down (**local** explanation), or how the model
computes internally (the mechanistic question of Chapter 23). The tools below answer the first two. Each is simple,
each is useful, and each has a failure mode you should be able to name.

The program uses four features: $x_1$ is strongly predictive, $x_2$ weakly, $x_3$ is a noisy copy of $x_1$, and
$x_4$ is noise. The true rule uses only $x_1$ and $x_2$.

```python
--8<-- "books/machine-learning/ch22_interpret.py"
```

```
1. coefficients (features all have standard deviation about 1)
   x1 strong      +1.790
   x2 weak        +0.486
   x3 copy of x1  +0.147
   x4 noise       +0.045

2. permutation importance on the test set: rise in log loss when one column is shuffled
   x1 strong      +0.4771  (+/- 0.0251)
   x2 weak        +0.0337  (+/- 0.0044)
   x3 copy of x1  +0.0025  (+/- 0.0020)
   x4 noise       +0.0012  (+/- 0.0005)
   refit without x1: coefficient of x3 becomes +1.681; test log loss 0.4893 vs 0.4599

3. exact Shapley values of the model's logit for one person, by all 2^4 coalitions
   feature        Shapley    w_j (x0_j - mean_j)
   x1 strong      +2.7391    +2.7391
   x2 weak        -0.4928    -0.4928
   x3 copy of x1  +0.1774    +0.1774
   x4 noise       +0.0399    +0.0399
   sum of Shapley values +2.4635 = f(x0) - E f(background) = +2.4635
   on the probability scale: [+0.4693 -0.0541 +0.0213 +0.0048], sum +0.4413 = +0.4413

4. gradient saliency d P(y=1) / d x = p (1 - p) w, for three people
   x = [0.1 0.  0.1 0. ], P = 0.5256, gradient = [+0.4463 +0.1211 +0.0366 +0.0111]
   x = [ 1.5 -1.   1.2  0.8], P = 0.9105, gradient = [+0.1459 +0.0396 +0.012  +0.0036]
   x = [4. 1. 4. 0.], P = 0.9997, gradient = [+5.2121e-04 +1.4145e-04 +4.2763e-05 +1.3007e-05]
```

### Linear coefficients

In a linear or logistic model, coefficient $w_j$ is the change in the output (or log-odds) per unit of $x_j$ with the
other features held fixed. Two warnings. Coefficients are only comparable when the features are on the same scale
(standardise first, Chapter 2). And "held fixed" is a fiction when features are correlated: here $x_3$ gets a small
coefficient (0.147) only because $x_1$ is present; refit without $x_1$ and $x_3$ takes a coefficient of 1.681. The
model is equally happy with either; the explanation depends on an arbitrary choice.

### Permutation importance

Breiman (2001) measured a feature's importance in a random forest by shuffling that column in the test data, which
breaks its link with the label while keeping its distribution, and seeing how much the error rises. It works for any
model. Here shuffling $x_1$ raises the log loss by 0.48, $x_2$ by 0.034, and $x_3$ and $x_4$ by almost nothing. Two
warnings again. With correlated features, importance is split or hidden: $x_3$ looks useless, yet the model would be
nearly as good with $x_3$ instead of $x_1$ (test log loss 0.489 against 0.460). And shuffling one of two correlated
columns creates rows that never occur in reality (large $x_1$ with small $x_3$), so the model is judged on inputs it
was never trained for. Hooker, Mentch and Zhou ("Unrestricted permutation forces extrapolation", Statistics and
Computing 2021) analyse this. Fisher, Rudin and Dominici (JMLR 2019) give a careful definition, "model reliance", and
its statistics.

### Shapley values and SHAP

For a local explanation we want numbers $\phi_1, \dots, \phi_d$ that split one prediction $f(x)$ into contributions
from each feature. Game theory has a classic answer. Lloyd Shapley (1953) asked how to divide the payout of a
cooperative game fairly among players, and proved that exactly one rule satisfies four natural axioms: the shares
add up to the total (**efficiency**), a player who adds nothing gets nothing (**null player**), players who
contribute identically get equal shares (**symmetry**), and shares of a sum of games are sums of shares
(**additivity**). The rule averages a player's marginal contribution over all orders in which the players could
arrive:

$$
\phi_j = \sum_{S \subseteq \{1..d\} \setminus \{j\}} \frac{|S|!\,(d - |S| - 1)!}{d!}\,\big(v(S \cup \{j\}) - v(S)\big).
$$

The weight is the fraction of the $d!$ orderings in which exactly the features of $S$ arrive before $j$. For a model,
the "players" are features and the payout of a coalition $S$ is $v(S)$, the model's expected output when the
features in $S$ are set to the values of the person being explained and the others are drawn from background data.
Lundberg and Lee ("A unified approach to interpreting model predictions", NeurIPS 2017) showed that several earlier
attribution methods are special cases or approximations of this, and called the result **SHAP** (SHapley Additive
exPlanations). By efficiency, the $\phi_j$ add up to $f(x)$ minus the average prediction.

The program computes Shapley values exactly by enumerating all $2^4 = 16$ coalitions. For a model that is linear in
its output scale, there is a closed form: $\phi_j = w_j(x_j - \bar x_j)$, where $\bar x_j$ is the background mean.
(Proof: with $f$ linear, $v(S \cup \{j\}) - v(S) = w_j(x_j - \bar x_j)$ for every $S$, and the weights sum to 1.) The
enumeration matches it to four decimals, and the sum, 2.4635, equals $f(x) - E f$ exactly. On the probability scale
the model is not linear, the closed form fails, but efficiency still holds (0.4413 = 0.4413).

The exact sum has $2^d$ terms, hopeless for hundreds of features. **Kernel SHAP** estimates the values by a weighted
regression on sampled coalitions; **TreeSHAP** (Lundberg et al., 2020) computes them exactly for tree ensembles in
polynomial time. The warnings: Shapley values describe the *model*, not the world; with correlated features the
"interventional" value function used here again evaluates the model on unrealistic inputs, while the alternative
"conditional" version can give credit to features the model never uses. Different choices give different answers,
and the axioms do not decide between them.

### Saliency maps and their limits

For images, a local explanation is a picture: the **saliency map** of Simonyan, Vedaldi and Zisserman (2013) is the
gradient of the class score with respect to each input pixel, showing where a small change would matter most. Part 4
shows the simplest case: for logistic regression the gradient of the probability is $p(1 - p)\,w$. For a person near
the boundary ($P = 0.53$) the gradient is large; for a person the model is sure about ($P = 0.9997$) it is almost
zero, although the same features decided the case. This is **saturation**: a gradient is a local slope, and a flat
region says nothing about what got you there. **Integrated gradients** (Sundararajan, Taly and Yan, ICML 2017) fixes
this by integrating the gradient along a path from a baseline input to the real one, and satisfies an efficiency
axiom like Shapley's.

A sharper warning came from Adebayo, Gilmer, Muelly, Goodfellow, Hardt and Kim ("Sanity checks for saliency maps",
NeurIPS 2018). They randomised a trained network's weights, layer by layer, and found that some popular saliency
methods produced nearly the same maps for the random network as for the trained one: the maps reflected the input
image's edges more than anything the model had learned. Their test, "does the explanation change when the model
changes?", is a good habit for any explanation method.

## 22.5 Robustness: adversarial examples

*Level: advanced.*

In 2013 Szegedy and co-authors ("Intriguing properties of neural networks", published at ICLR 2014) reported that
image classifiers that were accurate on test data could be made to misclassify an image by adding a perturbation so
small that people could not see it. Such inputs are **adversarial examples**. Worse, a perturbation found for one
network often fooled others trained separately.

### The fast gradient sign method, from scratch

Goodfellow, Shlens and Szegedy ("Explaining and harnessing adversarial examples", ICLR 2015) gave both a cheap attack
and an explanation. The attacker wants to raise the loss $\ell(x, y)$ while changing each input coordinate by at most
$\varepsilon$ (an $L_\infty$ budget: $\|\delta\|_\infty = \max_j|\delta_j| \le \varepsilon$). To first order,
$\ell(x + \delta) \approx \ell(x) + \nabla_x\ell \cdot \delta$, and the $\delta$ in the box that maximises a dot product
with a fixed vector $g$ is $\varepsilon\operatorname{sign}(g)$, giving $\varepsilon\|g\|_1$ (Hölder's inequality:
$g \cdot \delta \le \|g\|_1\|\delta\|_\infty$, with equality at the sign vector). So the **fast gradient sign method**
(FGSM) is

$$
x_{\text{adv}} = x + \varepsilon\,\operatorname{sign}\big(\nabla_x\,\ell(x, y)\big).
$$

For logistic regression with labels $y \in \{-1, +1\}$ and loss $\ell = \log(1 + e^{-y(w\cdot x + b)})$, the input
gradient is $-y\,\sigma(-y(w\cdot x + b))\,w$, whose sign is $-y\operatorname{sign}(w)$. The attack is therefore
$x_{\text{adv}} = x - \varepsilon y\operatorname{sign}(w)$, and it is exact, not just first-order: it lowers the margin
$y(w\cdot x + b)$ by exactly $\varepsilon\|w\|_1$, the most any perturbation in the box can.

**Why high dimension makes it worse.** Goodfellow et al.'s explanation is linearity. If $w$ has $d$ coordinates of
similar size $c$, then $\|w\|_1 = dc$, so a perturbation of $\varepsilon$ per coordinate moves the score by
$\varepsilon dc$, growing with $d$, while the size of the perturbation per coordinate stays the same. In an image with
hundreds of thousands of pixels, a change of a few intensity levels in each one adds up.

```python
--8<-- "books/machine-learning/ch22_robust_privacy.py"
```

```
1. FGSM on logistic regression: d weak features, each shifted by +/- 0.1 between classes
        d   clean acc   acc at eps=0.02   eps=0.05   eps=0.10   eps * ||w||_1 at 0.05
       10       0.622             0.595      0.562      0.506       0.09
      100       0.841             0.782      0.686      0.492       1.14
     1000       0.999             0.991      0.932      0.498       3.68

2. one robust feature (2y + noise) plus 1000 weak ones (0.1y + noise); train with and without attacks
   training        acc at eps = 0     0.05     0.10     0.20    weight on robust   ||w_weak||_1
   standard             1.000   0.991   0.842   0.046           1.10           55.5
   adversarial          0.996   0.986   0.960   0.736           3.57           38.3

3. randomized response: each person tells the truth with probability 3/4, else flips
   n =   1000: estimate error  mean +0.0021   std 0.0306   (epsilon = ln 3 = 1.099)
   n =  10000: estimate error  mean +0.0003   std 0.0106   (epsilon = ln 3 = 1.099)
   n = 100000: estimate error  mean +0.0004   std 0.0030   (epsilon = ln 3 = 1.099)

4. Laplace mechanism for the mean of n values clipped to [0, 1]: noise scale 1 / (n eps)
   eps =   0.1, n =    100: true mean 0.3538, typical error 0.10345
   eps =   0.1, n =  10000: true mean 0.3326, typical error 0.00099
   eps =   1.0, n =    100: true mean 0.3538, typical error 0.00976
   eps =   1.0, n =  10000: true mean 0.3326, typical error 0.00010
   eps =  10.0, n =    100: true mean 0.3538, typical error 0.00098
   eps =  10.0, n =  10000: true mean 0.3326, typical error 0.00001

5. federated averaging: 5 clients, each holding a skewed slice of the data
   central training on pooled data: loss 0.3429
   rounds   FedAvg (5 local steps)   one step per round
        1                   0.4712               0.6094
        5                   0.3619               0.4633
       10                   0.3474               0.4058
       50                   0.3429               0.3471
   distance of FedAvg weights from central weights: 0.0121
```

Part 1 makes data where each of $d$ features carries a weak signal: its mean is $+0.1$ for one class and $-0.1$ for
the other, with noise of standard deviation 1. With $d = 1000$ features the classifier is 99.9% accurate, because a
thousand weak signals add up. But an attack of 0.05 per feature, half the signal and a twentieth of the noise, lowers
accuracy to 0.932, and an attack of 0.1 makes it chance. The last column shows the margin lost at $\varepsilon = 0.05$,
$\varepsilon\|w\|_1$, which grows with $d$ (0.09, 1.14, 3.68) even though the trained weights per
feature get smaller.

<figure class="mars-fig" markdown="0">
<svg viewBox="0 0 660 280" role="img" aria-label="Accuracy of logistic regression under the fast gradient sign attack against the attack size. With 10 features accuracy starts at 0.62; with 1000 features it starts at 0.999. All three fall to chance, 0.5, at an attack of 0.1 per feature, the size of the real signal.">
<line x1="70" y1="220" x2="470" y2="220" stroke="currentColor"/><line x1="70" y1="20" x2="70" y2="220" stroke="currentColor"/>
<line x1="70.0" y1="220" x2="70.0" y2="225" stroke="currentColor"/><text x="70.0" y="239" font-size="12" text-anchor="middle" fill="currentColor">0.00</text>
<line x1="150.0" y1="220" x2="150.0" y2="225" stroke="currentColor"/><text x="150.0" y="239" font-size="12" text-anchor="middle" fill="currentColor">0.02</text>
<line x1="230.0" y1="220" x2="230.0" y2="225" stroke="currentColor"/><text x="230.0" y="239" font-size="12" text-anchor="middle" fill="currentColor">0.04</text>
<line x1="310.0" y1="220" x2="310.0" y2="225" stroke="currentColor"/><text x="310.0" y="239" font-size="12" text-anchor="middle" fill="currentColor">0.06</text>
<line x1="390.0" y1="220" x2="390.0" y2="225" stroke="currentColor"/><text x="390.0" y="239" font-size="12" text-anchor="middle" fill="currentColor">0.08</text>
<line x1="470.0" y1="220" x2="470.0" y2="225" stroke="currentColor"/><text x="470.0" y="239" font-size="12" text-anchor="middle" fill="currentColor">0.10</text>
<line x1="65" y1="220.0" x2="70" y2="220.0" stroke="currentColor"/><text x="61" y="224.0" font-size="12" text-anchor="end" fill="currentColor">0.4</text>
<line x1="65" y1="186.7" x2="70" y2="186.7" stroke="currentColor"/><text x="61" y="190.7" font-size="12" text-anchor="end" fill="currentColor">0.5</text>
<line x1="65" y1="153.3" x2="70" y2="153.3" stroke="currentColor"/><text x="61" y="157.3" font-size="12" text-anchor="end" fill="currentColor">0.6</text>
<line x1="65" y1="120.0" x2="70" y2="120.0" stroke="currentColor"/><text x="61" y="124.0" font-size="12" text-anchor="end" fill="currentColor">0.7</text>
<line x1="65" y1="86.7" x2="70" y2="86.7" stroke="currentColor"/><text x="61" y="90.7" font-size="12" text-anchor="end" fill="currentColor">0.8</text>
<line x1="65" y1="53.3" x2="70" y2="53.3" stroke="currentColor"/><text x="61" y="57.3" font-size="12" text-anchor="end" fill="currentColor">0.9</text>
<line x1="65" y1="20.0" x2="70" y2="20.0" stroke="currentColor"/><text x="61" y="24.0" font-size="12" text-anchor="end" fill="currentColor">1.0</text>
<line x1="70" y1="186.7" x2="470" y2="186.7" stroke="currentColor" stroke-dasharray="2 3" stroke-opacity="0.7"/>
<text x="76" y="201.7" font-size="11" fill="currentColor">chance</text>
<text x="270.0" y="260" font-size="13" text-anchor="middle" fill="currentColor">attack size eps per feature (the real signal is 0.1)</text>
<text x="20" y="120.0" font-size="13" text-anchor="middle" fill="currentColor" transform="rotate(-90 20 120.0)">test accuracy</text>
<polyline points="70.0,146.0 150.0,155.0 270.0,166.0 470.0,184.7" fill="none" stroke="#7ccf9a" stroke-width="2.2"/>
<circle cx="70.0" cy="146.0" r="3.5" fill="#7ccf9a" stroke="currentColor" stroke-width="0.8"/>
<circle cx="150.0" cy="155.0" r="3.5" fill="#7ccf9a" stroke="currentColor" stroke-width="0.8"/>
<circle cx="270.0" cy="166.0" r="3.5" fill="#7ccf9a" stroke="currentColor" stroke-width="0.8"/>
<circle cx="470.0" cy="184.7" r="3.5" fill="#7ccf9a" stroke="currentColor" stroke-width="0.8"/>
<line x1="495" y1="60" x2="515" y2="60" stroke="#7ccf9a" stroke-width="2.2"/><text x="521" y="64" font-size="12" fill="currentColor">d = 10 features</text>
<polyline points="70.0,73.0 150.0,92.7 270.0,124.7 470.0,189.3" fill="none" stroke="#9cc9ea" stroke-width="2.2"/>
<circle cx="70.0" cy="73.0" r="3.5" fill="#9cc9ea" stroke="currentColor" stroke-width="0.8"/>
<circle cx="150.0" cy="92.7" r="3.5" fill="#9cc9ea" stroke="currentColor" stroke-width="0.8"/>
<circle cx="270.0" cy="124.7" r="3.5" fill="#9cc9ea" stroke="currentColor" stroke-width="0.8"/>
<circle cx="470.0" cy="189.3" r="3.5" fill="#9cc9ea" stroke="currentColor" stroke-width="0.8"/>
<line x1="495" y1="84" x2="515" y2="84" stroke="#9cc9ea" stroke-width="2.2"/><text x="521" y="88" font-size="12" fill="currentColor">d = 100 features</text>
<polyline points="70.0,20.3 150.0,23.0 270.0,42.7 470.0,187.3" fill="none" stroke="#eea66f" stroke-width="2.2"/>
<circle cx="70.0" cy="20.3" r="3.5" fill="#eea66f" stroke="currentColor" stroke-width="0.8"/>
<circle cx="150.0" cy="23.0" r="3.5" fill="#eea66f" stroke="currentColor" stroke-width="0.8"/>
<circle cx="270.0" cy="42.7" r="3.5" fill="#eea66f" stroke="currentColor" stroke-width="0.8"/>
<circle cx="470.0" cy="187.3" r="3.5" fill="#eea66f" stroke="currentColor" stroke-width="0.8"/>
<line x1="495" y1="108" x2="515" y2="108" stroke="#eea66f" stroke-width="2.2"/><text x="521" y="112" font-size="12" fill="currentColor">d = 1000 features</text>
</svg>
<figcaption>Figure 22.3. Accuracy under FGSM for logistic regression with 10, 100 and 1000 weak features, measured by
ch22_robust_privacy.py. More features make the clean model better and more exposed: every curve reaches chance when
the attack equals the true per-feature signal, 0.1.</figcaption>
</figure>

### Adversarial training

The natural defence is to train on the attacked inputs: minimise the loss at the worst point in the box around each
example, a **min-max** problem,

$$
\min_{w}\ \frac1m\sum_{i=1}^m\ \max_{\|\delta_i\|_\infty \le \varepsilon}\ \ell(x_i + \delta_i, y_i;\, w).
$$

Madry, Makelov, Schmidt, Tsipras and Vladu ("Towards deep learning models resistant to adversarial attacks", ICLR
2018) solved the inner maximisation with several projected gradient steps (PGD) and made this the standard method.
For a linear model the inner maximum is exact and closed-form: the margin becomes $y(w\cdot x + b) -
\varepsilon\|w\|_1$, so adversarial training of logistic regression is ordinary training with a margin penalty
proportional to the $L_1$ norm of the weights, a sparsity-loving regulariser like the lasso of Chapter 8. The program
uses this to train without ever building the attacked inputs.

Part 2 shows what adversarial training buys. The data have one **robust** feature (its signal is $2y$, far larger than
any small attack) and 1000 **weak** features (signal $0.1y$ each). Standard training spreads its weight over all the
weak features, because together they are very predictive: clean accuracy 1.000, but 0.842 at $\varepsilon = 0.1$ and
0.046 at $\varepsilon = 0.2$ (the attack has turned the weak features against it). Adversarial training with
$\varepsilon = 0.1$ moves weight to the robust feature (3.57 against 1.10) and away from the weak ones (38.3 against
55.5): clean accuracy drops slightly to 0.996, while accuracy under attack becomes 0.960 and 0.736. This is the
trade-off Tsipras, Santurkar, Engstrom, Turner and Madry described in "Robustness may be at odds with accuracy" (ICLR
2019), using a data model of this kind. Ilyas et al. ("Adversarial examples are not bugs, they are features",
NeurIPS 2019) argued that real image data contain many such weak but genuinely predictive features, which standard
training uses and humans do not.

Two honest notes about evaluating defences. Many proposed defences only hid the gradient from the attack and were
broken by stronger attacks (Athalye, Carlini and Wagner, "Obfuscated gradients give a false sense of security", ICML
2018): a defence must be tested against an attacker who knows it. And empirical robustness is not a proof.
**Certified** defences give a guarantee for each input; randomized smoothing (Cohen, Rosenfeld and Kolter, ICML 2019)
classifies by majority vote over Gaussian-noised copies of the input and proves a radius within which the vote cannot
change. Robustness to natural changes (blur, weather, new cameras) is a related but different problem, closer to
distribution shift.

## 22.6 Privacy-preserving learning

*Level: advanced.*

Training data are often about people. A model can leak them: **membership inference** attacks (Shokri, Stronati,
Song and Shmatikov, 2017) guess whether a given record was in the training set from the model's confidence on it,
and large language models have been shown to reproduce rare training strings verbatim (Carlini et al., "Extracting
training data from large language models", USENIX Security 2021). Removing names is not enough: Dinur and Nissim
(2003) proved that answering too many aggregate queries too accurately lets an attacker reconstruct almost the whole
database. We need a definition of privacy that survives any later analysis.

### Differential privacy

Dwork, McSherry, Nissim and Smith ("Calibrating noise to sensitivity in private data analysis", 2006) gave it. Two
datasets are **neighbours** if they differ in one person's record. A randomised algorithm $M$ is
**$\varepsilon$-differentially private** if for every pair of neighbours $D, D'$ and every set of outputs $E$,

$$
\Pr[M(D) \in E] \le e^{\varepsilon}\,\Pr[M(D') \in E].
$$

In words: whatever an observer sees, its probability changes by at most a factor $e^\varepsilon$ whether or not your
record is included, so the output reveals little about you specifically, while it can still reveal a lot about the
population. Smaller $\varepsilon$ means more privacy. The definition has two properties that make it practical:
**post-processing** (anything computed from a private output is private with the same $\varepsilon$) and
**composition** ($k$ analyses with budgets $\varepsilon_1, \dots, \varepsilon_k$ are together
$(\sum\varepsilon_i)$-private).

**Randomized response.** Warner (1965) designed a survey method for sensitive yes-or-no questions: each person
answers truthfully with probability $3/4$ and gives the opposite answer otherwise, using a private coin. For any one
person, the probability of a "yes" is $3/4$ or $1/4$ depending on the truth, a ratio of 3, so the method is
$\ln 3$-differentially private. Yet the population share is recoverable: if the true share is $\pi$, then
$\Pr[\text{yes}] = \frac14 + \frac12\pi$, so $\hat\pi = 2(\overline{\text{yes}} - \frac14)$ is unbiased. Part 3 shows
the cost: the error's standard deviation is 0.031 with 1000 people, twice what an exact survey would have, and it
shrinks like $1/\sqrt n$.

**The Laplace mechanism.** For a numeric query $f$, let its **sensitivity** $\Delta f$ be the most $|f(D) - f(D')|$
can be over neighbours. Releasing $f(D) + \text{Laplace}(\Delta f/\varepsilon)$ is $\varepsilon$-private, where
$\text{Laplace}(b)$ has density $\frac1{2b}e^{-|z|/b}$. *Proof.* The output densities at any value $u$ under $D$ and
$D'$ have ratio $\exp\big((|u - f(D')| - |u - f(D)|)/b\big) \le \exp(|f(D) - f(D')|/b) \le e^{\Delta f/b} =
e^\varepsilon$, by the triangle inequality. Integrate over $E$. $\square$ For the mean of $n$ values clipped to
$[0, 1]$, changing one value moves the mean by at most $1/n$, so the noise has scale $1/(n\varepsilon)$ and typical
size (mean absolute value) exactly that. Part 4: with $\varepsilon = 1$ and $n = 10000$ the error is 0.0001; with
$\varepsilon = 0.1$ and $n = 100$ it is 0.1, as large as the effect one might want to measure. Privacy is cheap for
large groups and expensive for small ones, which is the definition working as intended.

**Training with privacy.** **DP-SGD** (Abadi et al., "Deep learning with differential privacy", CCS 2016) makes
stochastic gradient descent private: clip each example's gradient to a fixed norm (this bounds the sensitivity), add
Gaussian noise to the sum, and track the total privacy cost over all steps with a tight composition method (the
"moments accountant"). Accuracy usually drops, more for small datasets and large models.

### Federated learning

A different concern is where the data live. **Federated learning** (McMahan, Moore, Ramage, Hampson and Agüera y
Arcas, "Communication-efficient learning of deep networks from decentralized data", AISTATS 2017) trains one model
across many devices or institutions without collecting their data. In **federated averaging** (FedAvg), each round the
server sends the current weights to the clients; each client runs a few steps of gradient descent on its own data;
the server averages the returned weights (weighted by client data size).

Part 5 splits the data across 5 clients, each seeing a differently shifted region of input space (data that are not
identically distributed across clients, the usual case). With one local step per round, FedAvg is exactly
full-batch gradient descent on the pooled data. With five local steps, each round makes more progress, so fewer
rounds of communication are needed: after 10 rounds the loss is 0.347 against 0.406, and after 50 it matches central
training on pooled data (0.3429). With very different clients, many local steps can pull the clients' models apart
and slow or bias convergence, which is an active research topic.

Federated learning alone is not a privacy guarantee: the updates sent to the server can leak information about local
data. It is combined with **secure aggregation** (Bonawitz et al., CCS 2017: a cryptographic protocol that lets the
server learn only the sum of updates) and with differential privacy (noise added to the updates).

## 22.7 Tools in the real world

Every program in this book was written from scratch with NumPy so that nothing was hidden. Real projects use
libraries, and you should, because they are faster, tested by millions of users, and handle the hard edges. Knowing
what is inside them tells you what to check.

**scikit-learn** (Pedregosa et al., JMLR 2011) covers the classical methods of Parts II and III with one interface:
`fit`, `predict`, `transform`. What it adds to our code:

- `Pipeline` and `ColumnTransformer`: the leak-free pipeline of 22.1, so that `cross_val_score` refits the scaler and
  the feature selection inside each fold.
- Careful solvers: `LogisticRegression` uses L-BFGS, Newton or coordinate-descent solvers with stopping rules,
  `Ridge` and `Lasso` use the methods of Chapters 4 and 8, and the SVMs use the SMO idea of Chapter 10 (through
  LIBSVM).
- Model selection (`GridSearchCV`, group and time-series splitters), metrics, calibration curves, and
  `permutation_importance`, which is 22.4's loop.
- Gradient-boosted trees (`HistGradientBoostingClassifier`), in the style of LightGBM.

**PyTorch** (Paszke et al., NeurIPS 2019) and **JAX** (Bradbury et al., 2018; the design is described by Frostig,
Johnson and Leary, 2018) are the main libraries for deep learning. What they add to our code:

- **Automatic differentiation.** Chapter 15 built a small reverse-mode engine; PyTorch's `autograd` is the same idea,
  recording operations on tensors and applying the chain rule backwards. JAX transforms functions instead:
  `jax.grad(f)` returns a new function that computes the gradient.
- **Accelerators.** The same code runs on GPUs and other accelerators, where large matrix products are tens to
  hundreds of times faster than on a CPU.
- **Compilation and vectorisation.** JAX's `jit` compiles a whole function with the XLA compiler, and `vmap` turns a
  function of one example into a batched one; PyTorch has `torch.compile` and `torch.func.vmap`.
- **Building blocks**: layers, optimizers (Adam, schedules, clipping, Chapter 16), data loaders, mixed precision and
  multi-device training.

For the topics of this chapter there are specialised libraries too: the SHAP package for 22.4, DP-SGD
implementations for PyTorch and TensorFlow for 22.6, and federated-learning frameworks. The habit to keep from
writing everything yourself: when a library gives a surprising result, you can reproduce a small case by hand, as
this book has done in every chapter, and see whether the library or your understanding is wrong.

## Check yourself

??? question "1. Compute the Kolmogorov-Smirnov statistic for the samples $a = (1, 2, 3)$ and $b = (2.5, 4, 5)$ by hand."

    Evaluate both empirical CDFs at every data point, sorted: at 1, 2, 2.5, 3, 4, 5 they are
    $F_a = 1/3, 2/3, 2/3, 1, 1, 1$ and $F_b = 0, 0, 1/3, 1/3, 2/3, 1$. The gaps are $1/3, 2/3, 1/3, 2/3, 1/3, 0$, so the
    statistic is $2/3$. (The program's `ks_statistic` returns 0.6667 for these inputs.)

??? question "2. A group has base rate 0.3, PPV 0.6 and false negative rate 0.2. What is its false positive rate? A second group has base rate 0.5 and the same PPV and FNR. What is its FPR?"

    By Chouldechova's identity, $\mathrm{FPR} = \frac{0.3}{0.7}\cdot\frac{0.4}{0.6}\cdot 0.8 = 0.2286$ for the first
    group and $\frac{0.5}{0.5}\cdot\frac{0.4}{0.6}\cdot 0.8 = 0.5333$ for the second. Equal PPV and equal FNR with
    different base rates force a false positive rate more than twice as high in the second group.

??? question "3. Why does fitting a scaler (mean and standard deviation) on all the data before splitting usually cause only a small leak, while selecting features on all the data causes a large one?"

    The scaler uses only the inputs, not the labels, and two numbers per feature estimated from hundreds of rows
    change very little when the test rows are added; it leaks almost nothing about the test labels. Feature
    selection uses the labels: it picks the columns that happen to agree with the test rows' labels, so the
    selected features are tuned to the test set. With many candidate features and few rows the chance agreement is
    large, as 22.1's 81% on random labels shows. Both are still wrong in principle; a pipeline avoids both.

??? question "4. Compute the Shapley values by hand for $f(x_1, x_2) = x_1 x_2$, explained at $x = (1, 1)$ with a single background point $(0, 0)$. Check efficiency."

    $v(\varnothing) = f(0, 0) = 0$, $v(\{1\}) = f(1, 0) = 0$, $v(\{2\}) = f(0, 1) = 0$, $v(\{1, 2\}) = 1$. With $d = 2$ the
    weights are $1/2$ for $S = \varnothing$ and $1/2$ for the other singleton:
    $\phi_1 = \frac12(v(\{1\}) - v(\varnothing)) + \frac12(v(\{1, 2\}) - v(\{2\})) = \frac12$, and $\phi_2 = \frac12$ by symmetry. They add to $1 = f(x) - f(0, 0)$.
    An interaction is split equally between the features that create it.

??? question "5. Show that for a linear score $w\cdot x + b$, no perturbation with $\|\delta\|_\infty \le \varepsilon$ can lower the margin $y(w\cdot x + b)$ by more than $\varepsilon\|w\|_1$, and that FGSM achieves this."

    The margin changes by $y\,w\cdot\delta$, and $|w\cdot\delta| \le \sum_j|w_j||\delta_j| \le \varepsilon\sum_j|w_j| =
    \varepsilon\|w\|_1$. FGSM takes $\delta = -\varepsilon y\operatorname{sign}(w)$, for which
    $y\,w\cdot\delta = -\varepsilon y^2\sum_j w_j\operatorname{sign}(w_j) = -\varepsilon\|w\|_1$. So for linear models
    FGSM is the optimal attack, not an approximation.

??? question "6. In randomized response with truth probability $q > 1/2$, what is the privacy parameter, and what is the standard deviation of the estimate $\hat\pi$? Check it against the program for $q = 3/4$, $\pi = 0.3$, $n = 1000$."

    A person's answer is "yes" with probability $q$ or $1 - q$ depending on the truth, so $\varepsilon =
    \ln(q/(1 - q))$; for $q = 3/4$ it is $\ln 3 = 1.099$. The yes-probability is $r = (1 - q) + (2q - 1)\pi$ and
    $\hat\pi = (\overline{\text{yes}} - (1 - q))/(2q - 1)$, so $\mathrm{sd}(\hat\pi) = \sqrt{r(1 - r)/n}/(2q - 1)$. For
    $q = 3/4$, $\pi = 0.3$: $r = 0.4$, $\mathrm{sd} = \sqrt{0.24/1000}/0.5 = 0.031$. The program measured 0.0306.

??? question "7. Write the code: the EM algorithm of Saerens, Latinne and Decaestecker (2002) re-estimates a new class prior from unlabelled data by alternating between adjusting the posteriors with the current prior (E-step) and setting the prior to their average (M-step). Implement it and test it on 22.2's label-shift data."

    ```python
    import numpy as np

    def em_prior(p, pi_train, iters=200, tol=1e-8):
        """Saerens et al. (2002): p = classifier's P(y=1|x) under the training prior."""
        pi = pi_train
        for it in range(iters):
            a1 = p * pi / pi_train
            a0 = (1 - p) * (1 - pi) / (1 - pi_train)
            new = (a1 / (a1 + a0)).mean()          # E-step and M-step in one line
            if abs(new - pi) < tol:
                return new, it
            pi = new
        return pi, iters

    r = np.random.default_rng(9)
    y = (r.random(4000) < 0.1).astype(float)
    x = r.normal(np.where(y == 1, 1.0, -1.0), 1.0)
    p = 1 / (1 + np.exp(-2 * x))                   # exact P(y=1|x) when the prior is 0.5
    pi_hat, it = em_prior(p, 0.5)
    print(f"estimate {pi_hat:.4f} after {it} iterations; true share in the sample {y.mean():.4f}")
    ```

    It prints `estimate 0.0975 after 30 iterations; true share in the sample 0.0887`. The fixed point is the
    maximum-likelihood prior under the model; unlike the classify-and-count formula it uses the full probabilities,
    not just thresholded decisions, but it relies on those probabilities being calibrated.

??? question "8. You must publish both the mean income of a town (values clipped to [0, 200000]) and the share of people over 65, from 2000 records, with a total budget $\varepsilon = 1$. How would you add noise, and how large is it?"

    Split the budget, for example $\varepsilon = 0.5$ for each; by composition the total is 1. The mean's
    sensitivity is $200000/2000 = 100$, so add Laplace noise of scale $100/0.5 = 200$ (typical error 200). The share's
    sensitivity is $1/2000$, so scale $(1/2000)/0.5 = 0.001$ (typical error 0.1 percentage points). Clipping is part
    of the mechanism: without a bound on each value the sensitivity is infinite.

??? question "9. Importance weighting gave a much better deployment error in 22.2 but an effective sample size of only 54. Show that the effective sample size $(\sum w_i)^2/\sum w_i^2$ equals $n$ when all weights are equal and 1 when one weight carries everything."

    Equal weights $w_i = c$: $(nc)^2/(nc^2) = n$. One nonzero weight $w_1 = c$: $c^2/c^2 = 1$. In general, by
    Cauchy-Schwarz $(\sum w_i)^2 \le n\sum w_i^2$, so the value lies between 1 and $n$. It is the number of equally
    weighted points that would give an average with the same variance, so it tells you how much the reweighting has
    cost.

??? question "10. Give the argument that federated averaging with one local gradient step per round, and equal-sized clients, is exactly full-batch gradient descent on the pooled data."

    Each client $c$ returns $w - \eta\nabla L_c(w)$, where $L_c$ is the average loss on its $n$ examples. The server
    averages: $\frac1C\sum_c\big(w - \eta\nabla L_c(w)\big) = w - \eta\nabla\big(\frac1C\sum_c L_c\big)(w)$, and
    $\frac1C\sum_c L_c$ is the average loss over all $Cn$ examples. With more local steps, each client's gradient is
    taken at its own drifting weights, so the equality breaks; that is both why FedAvg saves communication and why it
    can be biased when clients differ.

??? question "11. (Hard) Prove Theorem 22.1's key step, $E[s] = p$, from calibration, carefully, for a score that takes finitely many values."

    Let the score take values $v_1, \dots, v_k$ with probabilities $q_1, \dots, q_k$ in the group. Calibration says
    $\Pr[y = 1 \mid s = v_j] = v_j$. Then $p = \Pr[y = 1] = \sum_j q_j\Pr[y = 1 \mid s = v_j] = \sum_j q_j v_j = E[s]$ by
    the law of total probability. With $z = E[s \mid y = 1]$ and $x = E[s \mid y = 0]$, the law of total expectation
    gives $E[s] = pz + (1 - p)x$, and the rest of the proof in 22.3 follows: $p = x/(1 - z + x)$.

## What you learned

- A trustworthy model is the output of a pipeline: seeded, versioned by data fingerprints, and fitted only on
  training rows. Any step that learns from data outside the split leaks, and feature selection on all the data can
  make random labels look 81% predictable.
- Shift comes in three kinds: covariate ($P(x)$), label ($P(y)$) and concept ($P(y \mid x)$). Two-sample tests and
  domain classifiers detect input shift; importance weights $Q(x)/P(x)$ correct covariate shift at a cost in
  effective sample size; re-estimating the prior corrects label shift; concept shift needs new labels.
- Group fairness criteria are measurable numbers. Chouldechova's identity and the Kleinberg-Mullainathan-Raghavan
  theorem prove that calibration and equal error rates cannot all hold when base rates differ, even for a perfect
  risk score.
- Coefficients, permutation importance, Shapley values and saliency maps each answer a different question, and each
  misleads in a known way: correlated features, extrapolation, choice of value function, saturation.
- FGSM shows that a linear model in high dimension can be moved by $\varepsilon\|w\|_1$ with an invisible change;
  adversarial training trades a little accuracy for robustness by moving weight to robust features.
- Differential privacy bounds what any output reveals about one person; randomized response and the Laplace
  mechanism are its simplest forms; federated averaging trains without pooling data, and needs secure aggregation and
  noise to be private.

**Next:** [Chapter 23](23-Where-Machine-Learning-Goes.md), the research frontier: scaling laws, self-supervised and
foundation models, in-context learning, mechanistic interpretability, graph networks, ML for science, and the open
problems.

## Further reading

- T. Hastie, R. Tibshirani and J. Friedman, *The Elements of Statistical Learning*, 2nd ed., 2009, section 7.10.2 on
  the wrong and right way to do cross-validation.
- C. Ambroise and G. J. McLachlan, "Selection Bias in Gene Extraction on the Basis of Microarray Gene-Expression Data",
  *PNAS*, 2002.
- S. Kaufman, S. Rosset, C. Perlich and O. Stitelman, "Leakage in Data Mining: Formulation, Detection, and Avoidance",
  *ACM Transactions on Knowledge Discovery from Data*, 2012.
- D. Sculley et al., "Hidden Technical Debt in Machine Learning Systems", NeurIPS 2015.
- J. Quiñonero-Candela, M. Sugiyama, A. Schwaighofer and N. D. Lawrence (eds.), *Dataset Shift in Machine Learning*,
  2009; H. Shimodaira, "Improving Predictive Inference under Covariate Shift by Weighting the Log-Likelihood
  Function", *Journal of Statistical Planning and Inference*, 2000.
- M. Saerens, P. Latinne and C. Decaestecker, "Adjusting the Outputs of a Classifier to New a Priori Probabilities",
  *Neural Computation*, 2002; Z. Lipton, Y.-X. Wang and A. Smola, "Detecting and Correcting for Label Shift with Black
  Box Predictors", ICML 2018.
- J. Kleinberg, S. Mullainathan and M. Raghavan, "Inherent Trade-Offs in the Fair Determination of Risk Scores", 2016
  (ITCS 2017); A. Chouldechova, "Fair Prediction with Disparate Impact", *Big Data*, 2017; M. Hardt, E. Price and
  N. Srebro, "Equality of Opportunity in Supervised Learning", NeurIPS 2016.
- S. Barocas, M. Hardt and A. Narayanan, *Fairness and Machine Learning: Limitations and Opportunities*, 2023.
- L. S. Shapley, "A Value for n-Person Games", 1953; S. Lundberg and S.-I. Lee, "A Unified Approach to Interpreting
  Model Predictions", NeurIPS 2017; L. Breiman, "Random Forests", *Machine Learning*, 2001.
- J. Adebayo, J. Gilmer, M. Muelly, I. Goodfellow, M. Hardt and B. Kim, "Sanity Checks for Saliency Maps", NeurIPS
  2018; M. Sundararajan, A. Taly and Q. Yan, "Axiomatic Attribution for Deep Networks", ICML 2017.
- C. Molnar, *Interpretable Machine Learning*, 2nd ed., 2022.
- C. Szegedy et al., "Intriguing Properties of Neural Networks", ICLR 2014; I. Goodfellow, J. Shlens and C. Szegedy,
  "Explaining and Harnessing Adversarial Examples", ICLR 2015; A. Madry et al., "Towards Deep Learning Models
  Resistant to Adversarial Attacks", ICLR 2018; D. Tsipras et al., "Robustness May Be at Odds with Accuracy", ICLR
  2019.
- C. Dwork, F. McSherry, K. Nissim and A. Smith, "Calibrating Noise to Sensitivity in Private Data Analysis", TCC
  2006; C. Dwork and A. Roth, *The Algorithmic Foundations of Differential Privacy*, 2014; M. Abadi et al., "Deep
  Learning with Differential Privacy", CCS 2016.
- H. B. McMahan, E. Moore, D. Ramage, S. Hampson and B. Agüera y Arcas, "Communication-Efficient Learning of Deep
  Networks from Decentralized Data", AISTATS 2017.
- F. Pedregosa et al., "Scikit-learn: Machine Learning in Python", *JMLR*, 2011; A. Paszke et al., "PyTorch: An
  Imperative Style, High-Performance Deep Learning Library", NeurIPS 2019.
- On this site: [Chapter 2](02-Data-and-Features.md) (splitting and leakage), [Chapter 7](07-Evaluating-Models.md)
  (metrics, calibration and the bootstrap), [Chapter 8](08-Overfitting-and-Regularization.md) (the lasso, which
  adversarial training of linear models resembles), [Chapter 15](15-Neural-Networks-and-Backpropagation.md)
  (automatic differentiation), [Chapter 21](21-Learning-Theory.md) (the i.i.d. world this chapter leaves), and the
  Cryptography book at https://cryptography.akadian.ca/book/ for hash functions and the cryptography behind secure
  aggregation.
