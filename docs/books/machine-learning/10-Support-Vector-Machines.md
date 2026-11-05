# 10. Support vector machines

*When two classes can be separated by a straight line, there are usually infinitely many such lines. The perceptron
of Chapter 6 stops at the first one it finds; logistic regression finds one that balances probabilities. Which line
is best? The support vector machine gives a geometric answer: the line that stays as far as possible from both
classes. This chapter derives the width of that margin, writes the widest-margin problem as a quadratic program,
softens it for classes that overlap, and then uses Lagrange duality to discover two surprises: the answer depends on
only a few training points, the support vectors, and it depends on them only through dot products, so the kernel
trick of Chapter 9 applies. You will train SVMs from scratch twice: by stochastic subgradient descent (Pegasos) and
by Platt's sequential minimal optimization.*

!!! abstract "In this chapter"
    **You will learn:**

    - the distance from a point to a hyperplane, and why the margin of a canonical hyperplane is $1/\lVert w \rVert$
    - the hard-margin SVM as a convex quadratic program, solved exactly on a small example by hand and by computer
    - the soft margin, slack variables, and why they amount to minimising the hinge loss
    - Lagrange duality and the KKT conditions, derived for the SVM, and what makes a point a support vector
    - kernel SVMs with the RBF kernel, and how $C$ and $\gamma$ shape the boundary
    - Pegasos with its convergence proof, and SMO with its two-variable update derived

    **You need:** [Chapter 5](05-Optimization.md) (convexity, gradient descent),
    [Chapter 6](06-Classification-and-Logistic-Regression.md) (linear classifiers, the perceptron, logistic loss),
    [Chapter 8](08-Overfitting-and-Regularization.md) (regularization) and
    [Chapter 9](09-Nearest-Neighbours-and-Kernels.md) (kernels and the kernel trick).

    **Levels:** 10.1 to 10.3 are intermediate; 10.4 and 10.5 are advanced; 10.6 is advanced.

## 10.1 The widest margin; geometry of the margin derived

Look at a set of points in two classes that a line can separate. You can wiggle the line a little and it still
separates them. Now imagine new points arriving from the same source: each lies near some training point of its
class, but not exactly on it. A line that passes very close to a training point is likely to misclassify a new
point that lands just beyond it. A line that keeps a wide gap on both sides has room to spare. That gap is the
**margin**, and the support vector machine (SVM) chooses the line that makes it as wide as possible.

**Hyperplanes.** In $d$ dimensions the analogue of a line is a **hyperplane**: the set of points $x$ with
$w \cdot x + b = 0$, where $w$ is a nonzero vector (the **normal**, perpendicular to the hyperplane) and $b$ a number
(the **offset**). A linear classifier predicts $\mathrm{sign}(w \cdot x + b)$: $+1$ on one side, $-1$ on the other.
We code the two classes as $y = +1$ and $y = -1$ (not 0 and 1) because then "correctly classified" is the single
condition $y\,(w \cdot x + b) > 0$.

**Distance from a point to a hyperplane.** Take a point $x$, and let $x_0$ be its closest point on the hyperplane.
The segment from $x_0$ to $x$ is perpendicular to the hyperplane, so it is parallel to $w$: $x = x_0 + t\,\frac{w}{\lVert w \rVert}$
for some number $t$, which is the signed distance we want. Take the dot product with $w$ and add $b$:

$$
w \cdot x + b = (w \cdot x_0 + b) + t\,\frac{w \cdot w}{\lVert w \rVert} = 0 + t\,\lVert w \rVert,
\qquad\text{so}\qquad t = \frac{w \cdot x + b}{\lVert w \rVert}.
$$

The sign of $t$ tells the side, its size the distance. For example, with $w = (3, 4)$ and $b = -10$ (the line
$3x_1 + 4x_2 = 10$, and $\lVert w \rVert = 5$): the origin gives $-10/5 = -2$, the point $(2, 1)$ gives $0$ (it lies on
the line), and $(4, 3)$ gives $14/5 = 2.8$.

**Functional and geometric margin.** For a labelled point $(x_i, y_i)$, the number $y_i(w \cdot x_i + b)$ is its
**functional margin**: positive when correct, and larger when more confidently correct. Divided by $\lVert w \rVert$ it
becomes the **geometric margin** $y_i(w \cdot x_i + b)/\lVert w \rVert$, the true signed distance from the point to the
hyperplane, measured towards its own side. The **margin of the classifier** on a data set is the smallest geometric
margin over all points: the distance from the hyperplane to the closest point.

The functional margin has a defect: multiply $w$ and $b$ by 7 and every functional margin is multiplied by 7, but the
hyperplane, and every distance, stays the same. The pair $(w, b)$ is only defined up to a positive factor. We use
that freedom to fix a scale. Call $(w, b)$ **canonical** for the data if the closest points have functional margin
exactly 1:

$$
\min_i \; y_i (w \cdot x_i + b) = 1.
$$

Then the closest points lie on the two parallel hyperplanes $w \cdot x + b = +1$ and $w \cdot x + b = -1$, the
**margin hyperplanes**, the margin of the classifier is $1/\lVert w \rVert$, and the empty band between the margin
hyperplanes has width $2/\lVert w \rVert$. (Directly: a point with $w \cdot x + b = 1$ is at distance $1/\lVert w \rVert$
from the decision hyperplane by the formula above, and the band extends that far on each side.)

So **maximising the margin is the same as minimising $\lVert w \rVert$** over canonical hyperplanes. That
turns a geometric wish into an optimisation problem.

<figure class="mars-fig" markdown="0">
<svg viewBox="0 0 640 300" role="img" aria-label="Six points: blue negatives at (0,0), (2,0), (0,2) and orange positives at (3,3), (4,4), (5,2). The decision line x1 + x2 = 4 runs between them, with dashed margin lines x1 + x2 = 2 and x1 + x2 = 6. The points (2,0), (0,2) and (3,3) lie on the margin lines and are circled as support vectors. A double arrow across the band is labelled 2 over the norm of w equals 2.83, and an arrow along w = (0.5, 0.5) points from the line towards the positives.">
  <g stroke="currentColor" fill="none">
    <line x1="50" y1="230" x2="330" y2="230" stroke-width="1"/>
    <line x1="90" y1="240" x2="90" y2="30" stroke-width="1"/>
    <line x1="50" y1="30" x2="290" y2="270" stroke-width="2.5"/>
    <line x1="50" y1="110" x2="210" y2="270" stroke-width="1.4" stroke-dasharray="6 4"/>
    <line x1="130" y1="30" x2="330" y2="230" stroke-width="1.4" stroke-dasharray="6 4"/>
    <line x1="152" y1="208" x2="228" y2="132" stroke-width="1.4"/>
    <polyline points="146,204 152,208 150,201" stroke-width="1.4"/>
    <polyline points="230,139 228,132 222,134" stroke-width="1.4"/>
    <line x1="130" y1="110" x2="158" y2="82" stroke="#7ccf9a" stroke-width="3"/>
    <polyline points="148,84 158,82 156,92" stroke="#7ccf9a" stroke-width="3"/>
    <circle cx="170" cy="230" r="12" stroke="#7ccf9a" stroke-width="2.5"/>
    <circle cx="90" cy="150" r="12" stroke="#7ccf9a" stroke-width="2.5"/>
    <circle cx="210" cy="110" r="12" stroke="#7ccf9a" stroke-width="2.5"/>
  </g>
  <g stroke="currentColor" stroke-width="1">
    <circle cx="90" cy="230" r="6" fill="#9cc9ea"/>
    <circle cx="170" cy="230" r="6" fill="#9cc9ea"/>
    <circle cx="90" cy="150" r="6" fill="#9cc9ea"/>
    <circle cx="210" cy="110" r="6" fill="#eea66f"/>
    <circle cx="250" cy="70" r="6" fill="#eea66f"/>
    <circle cx="290" cy="150" r="6" fill="#eea66f"/>
  </g>
  <g font-size="12" fill="currentColor">
    <text x="138" y="82">w</text>
    <text x="350" y="50">decision line: x1 + x2 = 4</text>
    <text x="350" y="72">(w = (0.5, 0.5), b = -2)</text>
    <text x="350" y="100">dashed margin lines:</text>
    <text x="350" y="118">x1 + x2 = 2 and x1 + x2 = 6</text>
    <text x="350" y="146">circled: the support vectors</text>
    <text x="350" y="164">(2,0) and (0,2) with alpha = 0.125,</text>
    <text x="350" y="182">(3,3) with alpha = 0.25</text>
    <text x="350" y="210">double arrow: the band, width</text>
    <text x="350" y="228">2/|w| = 2.83</text>
    <text x="350" y="256">the other three points could move</text>
    <text x="350" y="274">anywhere outside the band without</text>
    <text x="350" y="292">changing the answer</text>
  </g>
</svg>
<figcaption>The widest-margin line for six points. Only the three circled points, the support vectors, touch the
margin lines; the others play no role in the solution.</figcaption>
</figure>

**Why a wide margin should generalise.** Two informal reasons and one formal one. First, robustness: if every training
point is at distance at least $\gamma$ from the boundary, then perturbing any of them by less than $\gamma$ cannot
change its label. Second, uniqueness: the widest-margin hyperplane is a single well-defined answer, not an accident of
the order in which the data were visited. The formal reason belongs to [Chapter 21](21-Learning-Theory.md): Vladimir
Vapnik showed that hyperplanes with margin at least $\gamma$ on data inside a ball of radius $R$ form a class whose
capacity (its VC dimension) is at most about $R^2/\gamma^2 + 1$, *whatever the dimension* $d$. A wide margin keeps the
class simple even in a huge feature space, which is exactly what the kernel trick needs.

<figure class="play" data-play="svmmargin"><span class="ai-tag">AI-created</span><figcaption>Try it: turn the line between two groups of made-up points and watch the empty band around it; Widest finds the SVM's choice.</figcaption></figure>

## 10.2 Hard-margin SVM as a quadratic program

Combining the canonical scaling with "minimise $\lVert w \rVert$" (we minimise $\tfrac12 \lVert w \rVert^2$ instead,
which has the same minimiser and a nicer derivative), we get the **hard-margin SVM**:

$$
\min_{w,\,b} \; \tfrac12 \lVert w \rVert^2 \quad\text{subject to}\quad y_i (w \cdot x_i + b) \ge 1 \quad\text{for } i = 1, \dots, n.
$$

The constraints say every point is on the correct side with functional margin at least 1. At the optimum some
constraint must be tight (otherwise we could shrink $w$ further), so the optimum is automatically canonical.

This is a **quadratic program** (QP): a quadratic objective with linear constraints. It is **convex**: the objective
is a convex function, and each constraint $y_i(w\cdot x_i + b) \ge 1$ is a half-space in the space of $(w, b)$, so the
feasible set, an intersection of half-spaces, is convex. By [Chapter 5](05-Optimization.md) every local minimum is
global. More: the minimising $w$ is **unique**. Suppose $w_1 \ne w_2$ (with offsets $b_1, b_2$) are both optimal with
value $v$. Their midpoint is feasible (convexity), and because $\lVert \cdot \rVert^2$ is strictly convex,
$\tfrac12\lVert \tfrac{w_1 + w_2}{2} \rVert^2 < \tfrac12 \cdot \tfrac12 (\lVert w_1 \rVert^2 + \lVert w_2 \rVert^2) = v$,
contradicting optimality. (The offset $b$ is then unique too whenever both classes have a point on their margin
hyperplane.) The problem has a solution exactly when the data are **linearly separable**; otherwise the constraints
cannot all hold, which is the problem 10.3 fixes.

**The example, by hand.** Six points: negatives $(0,0), (2,0), (0,2)$ and positives $(3,3), (4,4), (5,2)$. Geometry
gives the answer. The widest separating band between two sets of points is set by the two closest points of their
**convex hulls** (the smallest convex polygons containing them). The negatives' hull is the triangle with corners
$(0,0), (2,0), (0,2)$; its edge from $(2,0)$ to $(0,2)$ lies on the line $x_1 + x_2 = 2$. The positives' hull is the
triangle $(3,3), (4,4), (5,2)$, and its point closest to the other hull is $(3,3)$, which lies on $x_1 + x_2 = 6$ (the
corner $(5,2)$ is farther, on $x_1 + x_2 = 7$). The foot of the perpendicular from $(3,3)$ to the line $x_1 + x_2 = 2$
is $(1,1)$, which lies on the edge, so the closest pair is $(1,1)$ and $(3,3)$, and the best hyperplane is their
perpendicular bisector: $x_1 + x_2 = 4$.

In canonical form, $w = (c, c)$ and we need $w \cdot (3,3) + b = 1$ and $w \cdot (1,1) + b = -1$: so $6c + b = 1$ and
$2c + b = -1$, giving $c = 1/2$ and $b = -2$. Thus $w = (0.5, 0.5)$, $\lVert w \rVert = 0.7071$, the margin is
$1/\lVert w \rVert = \sqrt 2 \approx 1.414$ and the band has width $2\sqrt 2 \approx 2.83$, the distance from $(1,1)$ to
$(3,3)$.

The program checks this with a brute-force solver that is exact but exponential: it guesses which points are the
support vectors, solves the linear equations that say "these points lie exactly on the margin", and keeps the feasible
guess with the smallest $\lVert w \rVert$. (The $\alpha_i$ it prints are explained in 10.4.)

```python
--8<-- "books/machine-learning/ch10_margin.py"
```

```
1. Distance from a point to a line
   x = [0. 0.]: w.x + b =  -10.0, distance = -2.00
   x = [2. 1.]: w.x + b =    0.0, distance =  0.00
   x = [4. 3.]: w.x + b =   14.0, distance =  2.80
   scaling (w, b) by 7 changes w.x + b but not the distance: 2.80

2. Hard-margin SVM on six points
   w = [0.5 0.5], b = -2.0000
   |w| = 0.7071; margin 1/|w| = 1.4142; width 2/|w| = 2.8284
   point     label  y(w.x+b)  alpha
   [0. 0.]   -1      2.000  0.0000
   [2. 0.]   -1      1.000  0.1250
   [0. 2.]   -1      1.000  0.1250
   [3. 3.]   +1      1.000  0.2500
   [4. 4.]   +1      2.000  0.0000
   [5. 2.]   +1      1.500  0.0000
   sum alpha_i y_i = 1.11e-16;  sum alpha_i y_i x_i = [0.5 0.5]
   dual objective sum(alpha) - |w|^2/2 = 0.2500; primal |w|^2/2 = 0.2500

3. Any other separating line has a smaller margin, e.g. w = (1, 2), b = -5.5:
   smallest distance from a point to it = 0.6708  (< 1.4142)
```

The three points with functional margin exactly 1 are the ones on the margin lines; the other three have margins 2,
2 and 1.5. The line with $w = (1, 2)$, $b = -5.5$ also separates the data, but its closest points are only $0.67$
away from it, less than half the SVM's margin.

**History.** Vladimir Vapnik and Alexey Chervonenkis studied the "optimal separating hyperplane" in the Soviet Union
in the 1960s (Vapnik and Lerner, "Pattern Recognition Using Generalized Portrait Method", 1963). The method became the
modern SVM in two steps: Bernhard Boser, Isabelle Guyon and Vapnik added kernels in 1992, and Corinna Cortes and Vapnik
added the soft margin in "Support-Vector Networks" (1995). Through the late 1990s and 2000s SVMs were among the most
accurate classifiers available on many benchmarks, and the theory around them shaped learning theory.

## 10.3 Soft margin and hinge loss

Real classes overlap. A single mislabelled point inside the other class makes the hard-margin problem infeasible, and
even when the data are separable, one outlier can force a very narrow margin. Cortes and Vapnik's fix was to let
points violate the margin, at a price.

Give each point a **slack variable** $\xi_i \ge 0$ that measures how far it falls short of margin 1, and charge $C$
per unit of slack:

$$
\min_{w,\,b,\,\xi} \; \tfrac12 \lVert w \rVert^2 + C \sum_{i=1}^n \xi_i
\quad\text{subject to}\quad y_i (w \cdot x_i + b) \ge 1 - \xi_i, \quad \xi_i \ge 0.
$$

A point with $\xi_i = 0$ satisfies the margin. A point with $0 < \xi_i \le 1$ is inside the band but still on the
correct side. A point with $\xi_i > 1$ is misclassified. So $\sum_i \xi_i$ is at least the number of training errors:
it is a convex upper bound on the error count. The constant $C > 0$ sets the trade-off. Large $C$ makes slack
expensive, so the solution works hard to classify every training point correctly, at the cost of a narrow margin
(as $C \to \infty$ we recover the hard margin). Small $C$ tolerates violations and keeps a wide margin, ignoring
individual points.

**From slack to hinge loss.** For fixed $w$ and $b$, what is the best $\xi_i$? The constraints say
$\xi_i \ge 1 - y_i(w\cdot x_i + b)$ and $\xi_i \ge 0$, and the objective wants each $\xi_i$ as small as possible, so at
the optimum $\xi_i = \max(0,\, 1 - y_i(w \cdot x_i + b))$. Substituting removes the constraints altogether:

$$
\min_{w,\,b} \; \tfrac12 \lVert w \rVert^2 + C \sum_{i=1}^n \max\big(0,\; 1 - y_i (w \cdot x_i + b)\big).
$$

The function $\ell(m) = \max(0, 1 - m)$ of the margin $m = y f(x)$ is the **hinge loss**, named for its shape: zero for
$m \ge 1$, then a straight line rising with slope $-1$. Dividing the objective by $nC$ (which does not change the
minimiser) and writing $\lambda = 1/(nC)$ gives the form used in 10.6,

$$
\min_{w,\,b} \; \frac{\lambda}{2} \lVert w \rVert^2 + \frac1n \sum_{i=1}^n \max\big(0,\; 1 - y_i (w \cdot x_i + b)\big),
$$

which is **regularized empirical risk minimisation** exactly like ridge or regularized logistic regression
([Chapter 8](08-Overfitting-and-Regularization.md)): average loss plus a penalty on $\lVert w \rVert^2$. The SVM is
"the linear classifier with the hinge loss and an L2 penalty". $C$ is an inverse regularization strength.

**Comparing losses.** The quantity we really care about is the **0-1 loss**, 1 for a mistake ($m \le 0$) and 0
otherwise. It is not convex, not continuous, and its gradient is zero almost everywhere, so minimising it directly is
computationally hard (for linear classifiers it is NP-hard in general). Every practical classifier replaces it by a
convex **surrogate** that lies above it. The hinge loss is the tightest convex surrogate that is exactly zero for
confident correct answers.

<figure class="mars-fig" markdown="0">
<svg viewBox="0 0 640 270" role="img" aria-label="Three losses plotted against the margin m = y f(x) from minus 2 to 3: the 0-1 loss is a step from 1 to 0 at m = 0; the hinge loss max(0, 1 - m) is a straight line reaching zero at m = 1 and staying zero; the logistic loss log2(1 + e^-m) is a smooth curve through 1 at m = 0 that never quite reaches zero.">
  <g font-size="12" fill="currentColor" stroke="currentColor" text-anchor="middle">
    <line x1="70" y1="220" x2="570" y2="220" stroke-width="1"/>
    <line x1="270" y1="220" x2="270" y2="38" stroke-width="1"/>
    <line x1="70" y1="220" x2="70" y2="225"/><text x="70" y="240" stroke="none">-2</text>
    <line x1="170" y1="220" x2="170" y2="225"/><text x="170" y="240" stroke="none">-1</text>
    <line x1="270" y1="220" x2="270" y2="225"/><text x="270" y="240" stroke="none">0</text>
    <line x1="370" y1="220" x2="370" y2="225"/><text x="370" y="240" stroke="none">1</text>
    <line x1="470" y1="220" x2="470" y2="225"/><text x="470" y="240" stroke="none">2</text>
    <line x1="570" y1="220" x2="570" y2="225"/><text x="570" y="240" stroke="none">3</text>
    <line x1="265" y1="165" x2="270" y2="165"/><text x="261" y="169" stroke="none" text-anchor="end">1</text>
    <line x1="265" y1="110" x2="270" y2="110"/><text x="261" y="114" stroke="none" text-anchor="end">2</text>
    <line x1="265" y1="55" x2="270" y2="55"/><text x="261" y="59" stroke="none" text-anchor="end">3</text>
    <text x="320.0" y="260" stroke="none">margin m = y f(x)</text>
  </g>
  <g fill="none" stroke-width="3">
    <polyline stroke="#9cc9ea" points="70,165 270,165 270,220 570,220"/>
    <polyline stroke="#eea66f" points="70,55 370,220 570,220"/>
    <polyline stroke="#7ccf9a" points="70.0,51.2 80.0,58.2 90.0,65.0 100.0,71.8 110.0,78.5 120.0,85.0 130.0,91.4 140.0,97.7 150.0,103.9 160.0,109.9 170.0,115.8 180.0,121.5 190.0,127.1 200.0,132.5 210.0,137.7 220.0,142.7 230.0,147.6 240.0,152.2 250.0,156.7 260.0,160.9 270.0,165.0 280.0,168.9 290.0,172.5 300.0,176.0 310.0,179.3 320.0,182.4 330.0,185.3 340.0,188.0 350.0,190.6 360.0,192.9 370.0,195.1 380.0,197.2 390.0,199.1 400.0,200.9 410.0,202.5 420.0,204.0 430.0,205.4 440.0,206.7 450.0,207.9 460.0,208.9 470.0,209.9 480.0,210.8 490.0,211.7 500.0,212.4 510.0,213.1 520.0,213.7 530.0,214.3 540.0,214.8 550.0,215.3 560.0,215.7 570.0,216.1"/>
  </g>
  <g font-size="13" fill="currentColor">
    <rect x="430" y="40" width="14" height="4" fill="#eea66f"/><text x="452" y="46">hinge max(0, 1 - m)</text>
    <rect x="430" y="62" width="14" height="4" fill="#7ccf9a"/><text x="452" y="68">logistic log2(1 + e^-m)</text>
    <rect x="430" y="84" width="14" height="4" fill="#9cc9ea"/><text x="452" y="90">0-1 loss</text>
  </g>
</svg>
<figcaption>Three losses as functions of the margin m = y f(x). The hinge loss (orange) and the logistic loss in
base 2 (green) are convex upper bounds on the 0-1 loss (blue). The hinge loss is exactly zero once m ≥ 1, so
confidently correct points drop out of the solution entirely; the logistic loss never quite reaches zero.</figcaption>
</figure>

```
      m    0-1   hinge max(0,1-m)   logistic log2(1+e^-m)   squared (1-m)^2
   -2.0    1           3.000               3.069             9.000
   -1.0    1           2.000               1.895             4.000
    0.0    1           1.000               1.000             1.000
    0.5    0           0.500               0.684             0.250
    1.0    0           0.000               0.452             0.000
    2.0    0           0.000               0.183             1.000
    3.0    0           0.000               0.070             4.000
```

(This table is the first part of the output of `ch10_pegasos.py` in 10.6.) The squared loss $(1 - m)^2$ of linear
regression used as a classifier punishes points for being *too* correct ($m = 3$ costs 4), the defect
[Chapter 6](06-Classification-and-Logistic-Regression.md) pointed out. The hinge and logistic losses are close for
badly wrong points and differ for correct ones: the hinge loss stops caring once $m \ge 1$. That flat region is the
origin of the sparsity in the next section: points with margin above 1 contribute nothing.

## 10.4 Lagrange duality, KKT conditions, support vectors

*Level: advanced.*

The SVM is a constrained optimisation problem. A standard way to understand such problems, and often to solve them,
is to build a second problem, the **dual**, whose variables are prices for the constraints. For the SVM the dual
reveals the structure of the solution and leads straight to kernels.

### Lagrange duality in general

Consider a **primal** problem: minimise $f(z)$ subject to $g_i(z) \le 0$ for $i = 1, \dots, m$. Attach a
**multiplier** $\alpha_i \ge 0$ to each constraint and form the **Lagrangian**

$$
L(z, \alpha) = f(z) + \sum_{i=1}^m \alpha_i\, g_i(z).
$$

Think of $\alpha_i$ as a fine per unit of violation. The **dual function** is the best the minimiser can do once
the fines are set, $q(\alpha) = \min_z L(z, \alpha)$, and the **dual problem** is to choose the fines to maximise it:
$\max_{\alpha \ge 0} q(\alpha)$.

**Weak duality: $q(\alpha) \le f(z)$ for every feasible $z$ and every $\alpha \ge 0$.** *Proof.* For a feasible $z$,
each $g_i(z) \le 0$ and $\alpha_i \ge 0$, so $\sum_i \alpha_i g_i(z) \le 0$ and
$q(\alpha) \le L(z, \alpha) \le f(z)$. $\square$ So every dual value is a lower bound on every primal value, and the
best lower bound is at most the optimum. The difference between the two optima is the **duality gap**.

**Strong duality.** For a convex problem ($f$ and every $g_i$ convex) the gap is zero under mild conditions; the most
used is **Slater's condition**: some point satisfies every constraint strictly, and when the constraints are affine
(linear), simple feasibility is enough. We state this without proof; see Boyd and Vandenberghe, *Convex
Optimization* (2004), section 5.3. Both SVM problems have affine constraints, so for them strong duality holds
whenever they are feasible.

**The KKT conditions.** When strong duality holds, $z^\ast$ and $\alpha^\ast$ are optimal for the primal and dual
exactly when (for differentiable convex problems) these **Karush-Kuhn-Tucker** conditions hold:

1. **stationarity:** $\nabla f(z^\ast) + \sum_i \alpha_i^\ast \nabla g_i(z^\ast) = 0$;
2. **primal feasibility:** $g_i(z^\ast) \le 0$;
3. **dual feasibility:** $\alpha_i^\ast \ge 0$;
4. **complementary slackness:** $\alpha_i^\ast\, g_i(z^\ast) = 0$ for every $i$.

Condition 4 is the important one. Why it holds: with a zero gap the chain in the weak-duality proof is a chain of
equalities, so $\sum_i \alpha_i^\ast g_i(z^\ast) = 0$, and a sum of non-positive terms is zero only if every term is.
In words: a constraint that is not tight has price zero, and a constraint with a positive price is tight.

### The SVM dual, derived

Write the soft-margin constraints as $1 - \xi_i - y_i(w\cdot x_i + b) \le 0$ with multipliers $\alpha_i \ge 0$, and
$-\xi_i \le 0$ with multipliers $\mu_i \ge 0$. The Lagrangian is

$$
L = \tfrac12 \lVert w \rVert^2 + C\sum_i \xi_i + \sum_i \alpha_i \big(1 - \xi_i - y_i (w \cdot x_i + b)\big) - \sum_i \mu_i \xi_i.
$$

To find $q(\alpha, \mu)$ we minimise over $w$, $b$ and $\xi$. Set the derivatives to zero:

$$
\frac{\partial L}{\partial w} = w - \sum_i \alpha_i y_i x_i = 0, \qquad
\frac{\partial L}{\partial b} = -\sum_i \alpha_i y_i = 0, \qquad
\frac{\partial L}{\partial \xi_i} = C - \alpha_i - \mu_i = 0.
$$

The first says $w = \sum_i \alpha_i y_i x_i$: **the weight vector is a combination of the training points**. The second
is a constraint on the multipliers (if it fails, $L$ is linear in $b$ with nonzero slope and its minimum is
$-\infty$). The third, with $\mu_i \ge 0$, says $\alpha_i \le C$. Substituting $w$ back, the terms in $\xi$ cancel
(their coefficient is $C - \alpha_i - \mu_i = 0$), the term in $b$ vanishes, and
$\tfrac12\lVert w\rVert^2 - \sum_i \alpha_i y_i\, w\cdot x_i = -\tfrac12 \lVert w \rVert^2$. What remains is the **SVM dual**:

$$
\max_{\alpha} \; \sum_{i=1}^n \alpha_i - \frac12 \sum_{i=1}^n \sum_{j=1}^n \alpha_i \alpha_j\, y_i y_j\, (x_i \cdot x_j)
\quad\text{subject to}\quad 0 \le \alpha_i \le C, \quad \sum_{i=1}^n \alpha_i y_i = 0.
$$

Three things to notice. It is a QP in $n$ variables, one per training point, whatever the dimension $d$. Its
quadratic part is $-\tfrac12 v^\top K v$ with $v_i = \alpha_i y_i$ and $K_{ij} = x_i \cdot x_j$, a PSD Gram matrix, so it
is a concave function to maximise: a convex problem. And **the data appear only through the dot products
$x_i \cdot x_j$**. That is the door to kernels (10.5). The hard-margin dual is the same with the upper bound $C$
removed.

### Support vectors

Complementary slackness for the two families of constraints reads
$\alpha_i\big(1 - \xi_i - y_i f(x_i)\big) = 0$ and $\mu_i \xi_i = 0$, where $f(x) = w\cdot x + b$ and
$\mu_i = C - \alpha_i$. Every training point falls into one of three cases.

| Multiplier | What KKT implies | Where the point is |
| --- | --- | --- |
| $\alpha_i = 0$ | $\mu_i = C > 0$, so $\xi_i = 0$ and $y_i f(x_i) \ge 1$ | on or outside its margin hyperplane; it does not affect $w$ |
| $0 < \alpha_i < C$ | $\mu_i > 0$, so $\xi_i = 0$; and $y_i f(x_i) = 1$ | exactly on its margin hyperplane (a **free** support vector) |
| $\alpha_i = C$ | $y_i f(x_i) = 1 - \xi_i \le 1$ | inside the band or misclassified (a **bound** support vector) |

The points with $\alpha_i > 0$ are the **support vectors**: the only points in $w = \sum_i \alpha_i y_i x_i$. All the
others could be deleted, or moved anywhere outside the band, without changing the solution. Typically they are the
large majority. In the example of 10.2 the multipliers are $\alpha = 0.125$ for $(2,0)$ and $(0,2)$, $0.25$ for
$(3,3)$ and zero for the rest. You can check every KKT condition: $\sum \alpha_i y_i = -0.125 - 0.125 + 0.25 = 0$;
$\sum \alpha_i y_i x_i = -0.125(2,0) - 0.125(0,2) + 0.25(3,3) = (0.5, 0.5) = w$; and the dual objective
$\sum_i \alpha_i - \tfrac12\lVert w \rVert^2 = 0.5 - 0.25 = 0.25$ equals the primal $\tfrac12 \lVert w \rVert^2 = 0.25$:
zero gap.

**Finding $b$.** The dual gives $w$ but not $b$. For any free support vector, $y_i f(x_i) = 1$ means
$b = y_i - w \cdot x_i$ (multiply by $y_i$, using $y_i^2 = 1$). Implementations average this over all free support
vectors for numerical stability.

**A free generalisation bound.** Sparsity buys a guarantee. Train on all points but one, and test on the one left
out; do this for every point; the fraction of mistakes is the **leave-one-out error**
([Chapter 7](07-Evaluating-Models.md)). **Claim:** it is at most (number of support vectors)/$n$. *Proof.* If $x_i$ is
not a support vector, the solution on all $n$ points still satisfies every KKT condition for the problem without
$x_i$ (it never appeared in $w$, and all other conditions are unchanged), so it is the solution without $x_i$; and it
classifies $x_i$ with margin at least 1, correctly. So only support vectors can be leave-one-out mistakes. $\square$
(If the solution is not unique, the argument applies to a suitable choice of solution.) In the overlapping-clouds
experiment of 10.6, 27 of 100 points are support vectors, so the leave-one-out error is at most 27 percent.

## 10.5 Kernel SVMs; RBF kernel

*Level: advanced.*

The dual uses the data only through $x_i \cdot x_j$, and the prediction can be written the same way:

$$
f(x) = w \cdot x + b = \sum_{i=1}^n \alpha_i y_i\, (x_i \cdot x) + b.
$$

So we may replace every dot product by a kernel $k(x_i, x_j)$ from [Chapter 9](09-Nearest-Neighbours-and-Kernels.md),
which runs the same maximum-margin method on $\varphi(x)$ in the kernel's feature space, without ever computing
$\varphi$. The **kernel SVM** solves

$$
\max_{\alpha} \; \sum_i \alpha_i - \frac12 \sum_{i,j} \alpha_i \alpha_j\, y_i y_j\, k(x_i, x_j)
\quad\text{subject to}\quad 0 \le \alpha_i \le C, \quad \sum_i \alpha_i y_i = 0,
$$

and predicts $\mathrm{sign}\big(\sum_i \alpha_i y_i\, k(x_i, x) + b\big)$. Only the support vectors enter the sum, so
prediction costs one kernel evaluation per support vector. Because $k$ is positive definite, the dual is still a
concave maximisation, so there are no bad local optima: the kernel SVM finds the globally widest margin in a feature
space that may be infinite-dimensional. This combination (non-linear boundaries, a convex problem, a sparse answer
and a margin-based theory) is what made SVMs dominant in the decade before deep learning.

**The RBF kernel's two knobs.** With $k(x, z) = \exp(-\gamma \lVert x - z \rVert^2)$ the decision function is a sum
of Gaussian bumps centred on the support vectors, each with sign $y_i$ and height $\alpha_i$. The width $\gamma$ sets
how far each support vector's influence reaches: small $\gamma$ gives broad bumps and smooth boundaries; large $\gamma$
gives narrow bumps that can wrap around single points. $C$ sets how much violations cost. Both control complexity
and both are chosen by cross-validation, usually on a logarithmic grid.

**An extreme case worth knowing.** As $\gamma \to \infty$, $k(x_i, x_j) \to 0$ for $i \ne j$ and the Gram matrix tends
to the identity. With balanced classes and $C \ge 1$, the dual becomes $\max \sum_i \alpha_i - \tfrac12 \sum_i \alpha_i^2$,
maximised at $\alpha_i = 1$ for every point: *every* training point becomes a support vector, the training data are
fitted perfectly, and at a new point far from all of them $f(x) \approx b$ (exercise 10). That is memorisation, the
SVM's version of 1-NN with no smoothing.

The program solves the dual with SMO (derived in 10.6) on two kinds of data: two overlapping Gaussian clouds with a
linear kernel, sweeping $C$, and two concentric rings with an RBF kernel, sweeping $\gamma$ and $C$.

```python
--8<-- "books/machine-learning/ch10_smo.py"
```

```
Linear soft-margin SVM on two overlapping Gaussian clouds (100 points)
      C   steps  |w|    width 2/|w|  a=0  0<a<C  a=C  worst KKT gap  train acc
    0.01    127  0.580       3.447    23      3   74        0.0004  0.90
     0.1    138  1.095       1.826    60      2   38        0.0000  0.89
       1    259  1.865       1.072    73      3   24        0.0004  0.88
      10    618  2.342       0.854    76      3   21        0.0006  0.89

C = 1: primal objective 23.8049, dual objective 23.8046 (equal at the optimum)
w = [1.5035 1.1035], b = 0.0895

RBF-kernel SVM on two rings (inner ring class +1, outer ring class -1)
  linear kernel, C = 1:            test acc 0.517
  gamma     C   support vectors   train acc   test acc
    0.1     1                44       1.000   0.983
    0.1   100                 8       1.000   0.983
      1     1                34       1.000   1.000
      1   100                27       1.000   0.983
     10     1               101       1.000   1.000
     10   100               100       1.000   1.000
    100     1               138       1.000   0.800
    100   100               137       1.000   0.833
```

Read the linear table as a picture of $C$. At $C = 0.01$ slack is cheap: the band is 3.4 units wide and 77 of the 100
points are support vectors (74 of them inside the band or misclassified), so they all help to place the line. As $C$ grows the band narrows to 0.85
units and only 24 points remain support vectors. Training accuracy hardly changes, because these clouds genuinely
overlap and no line separates them. The "worst KKT gap" column measures how far the returned $\alpha$ is from
satisfying the conditions of 10.4 (at most $10^{-3}$, the tolerance), and the primal and dual objectives at $C = 1$
agree to four digits: the zero duality gap, observed.

On the rings a linear kernel is no better than a coin (52 percent), as it must be: no line separates a disc from the
ring around it. Every RBF setting fits the training set perfectly, so training accuracy tells you nothing; the support
vector count and test accuracy tell the story. With $\gamma = 0.1$ and $C = 100$ just 8 support vectors describe the
circular boundary. With $\gamma = 100$ the bumps are so narrow (length scale about 0.1) that 137 of the 140 training
points become support vectors and test accuracy drops to about 80 percent: memorisation, exactly as the extreme case
predicted.

**More than two classes.** The SVM is a two-class method. The usual extensions train several of them: **one versus
rest** trains one SVM per class against all others and predicts the class whose SVM gives the largest $f(x)$
(exercise 9); **one versus one** trains an SVM for every pair of classes and takes a vote, which is what LIBSVM does.
Koby Crammer and Yoram Singer (2001) gave a single joint multiclass formulation. For regression, **support vector
regression** uses the $\varepsilon$-insensitive loss $\max(0, |y - f(x)| - \varepsilon)$, which ignores errors smaller
than $\varepsilon$, and has the same dual structure.

## 10.6 Training from scratch: Pegasos and SMO

*Level: advanced.*

A general QP solver needs memory for the $n \times n$ kernel matrix and time roughly cubic in $n$, which was
hopeless for the data sets of the 1990s. Two very different ideas made SVMs practical: work on the primal with cheap
stochastic steps, or work on the dual two variables at a time.

### Pegasos: stochastic subgradient descent in the primal

The primal objective of 10.3 (with $b$ folded into $w$ through a constant feature, see below),

$$
F(w) = \frac\lambda2 \lVert w \rVert^2 + \frac1n \sum_{i=1}^n \max\big(0,\; 1 - y_i\, w\cdot x_i\big),
$$

is convex but not differentiable: the hinge has a corner at margin 1. For convex functions the gradient generalises
to a **subgradient**: a vector $g$ with $F(v) \ge F(w) + g\cdot(v - w)$ for all $v$, a slope of a line (or plane)
that touches $F$ at $w$ and stays below it. Where $F$ is differentiable the subgradient is the gradient; at a corner
any slope between the two one-sided slopes works. For the hinge term of example $i$, a subgradient is $-y_i x_i$ when
$y_i w \cdot x_i < 1$ and $0$ otherwise.

**Pegasos** ("Primal Estimated sub-GrAdient SOlver for SVM", Shai Shalev-Shwartz, Yoram Singer and Nathan Srebro,
2007) is stochastic subgradient descent ([Chapter 5](05-Optimization.md)) with a special step size. At step
$t = 1, 2, \dots$: pick one example $i$ at random, set $\eta_t = 1/(\lambda t)$, and update

$$
w \leftarrow (1 - \eta_t \lambda)\, w + \begin{cases} \eta_t\, y_i x_i & \text{if } y_i\, w\cdot x_i < 1, \\ 0 & \text{otherwise.} \end{cases}
$$

The factor $(1 - \eta_t\lambda) = 1 - 1/t$ shrinks $w$ (the regularizer's gradient), and a point violating the margin
pulls $w$ towards itself. Optionally, $w$ is then projected onto the ball $\lVert w \rVert \le 1/\sqrt\lambda$, which
is known to contain the optimum.

**A hand trace** (no projection, $\lambda = 0.1$, no bias) on three points of 10.2: $(3,3)$ with label $+1$, then
$(2,0)$ and $(0,2)$ with label $-1$.

| $t$ | Example, label | $\eta_t$ | Margin $y\,w\cdot x$ before | Update | $w$ after |
| --- | --- | --- | --- | --- | --- |
| 1 | (3,3), +1 | 10 | 0 < 1 | $0 \cdot w + 10(3,3)$ | (30, 30) |
| 2 | (2,0), -1 | 5 | $-60$ < 1 | $\tfrac12 w - 5(2,0)$ | (5, 15) |
| 3 | (0,2), -1 | 3.333 | $-30$ < 1 | $\tfrac23 w - 3.333(0,2)$ | (3.333, 3.333) |

Unrolling the recursion shows what Pegasos computes: since each step multiplies by $(1 - 1/t)$, after $t$ steps
$w_t = \frac{1}{\lambda t} \sum_{s \le t,\ \text{violated}} y_{i_s} x_{i_s}$, a scaled sum of the margin violators seen so
far. After step 3 that is $\frac{1}{0.3}\big((3,3) - (2,0) - (0,2)\big) = (3.333, 3.333)$, as in the table.

**Theorem (convergence of Pegasos).** Suppose every subgradient used has norm at most $G$. Then after $T$ steps the
average of the per-step objectives satisfies
$\frac1T \sum_{t=1}^T \big(F_t(w_t) - F_t(w^\ast)\big) \le \frac{G^2 (1 + \ln T)}{2\lambda T}$, where
$F_t(w) = \frac\lambda2 \lVert w \rVert^2 + \max(0, 1 - y_{i_t} w\cdot x_{i_t})$ is the objective on the example of step
$t$. Taking expectations over the random choices, the averaged iterate $\bar w = \frac1T\sum_t w_t$ has
$E[F(\bar w)] - F(w^\ast) \le \frac{G^2(1 + \ln T)}{2\lambda T}$.

*Proof.* Each $F_t$ is **$\lambda$-strongly convex**: it is a convex function plus $\frac\lambda2 \lVert w \rVert^2$,
so for its subgradient $g_t$ at $w_t$,
$F_t(w^\ast) \ge F_t(w_t) + g_t\cdot(w^\ast - w_t) + \frac\lambda2 \lVert w^\ast - w_t \rVert^2$. Write
$D_t = \lVert w_t - w^\ast \rVert^2$. The update is $w_{t+1} = w_t - \eta_t g_t$, so

$$
D_{t+1} = D_t - 2\eta_t\, g_t\cdot(w_t - w^\ast) + \eta_t^2 \lVert g_t \rVert^2.
$$

Solve for $g_t\cdot(w_t - w^\ast)$ and put it into the strong-convexity inequality:

$$
F_t(w_t) - F_t(w^\ast) \le \frac{D_t - D_{t+1}}{2\eta_t} - \frac\lambda2 D_t + \frac{\eta_t G^2}{2}.
$$

With $\eta_t = 1/(\lambda t)$, $\frac{1}{2\eta_t} = \frac{\lambda t}{2}$, so the first two terms are
$\frac{\lambda(t-1)}{2} D_t - \frac{\lambda t}{2} D_{t+1}$. Summing over $t = 1, \dots, T$ these telescope to
$0 \cdot D_1 - \frac{\lambda T}{2} D_{T+1} \le 0$. The last terms sum to $\frac{G^2}{2\lambda} \sum_{t=1}^T \frac1t \le \frac{G^2(1 + \ln T)}{2\lambda}$.
Divide by $T$. For the expectation statement, $E[F_t(w_t)] = E[F(w_t)]$ because $i_t$ is chosen independently of
$w_t$, and $F(\bar w) \le \frac1T\sum_t F(w_t)$ by convexity (Jensen). (The projection step only moves $w$ closer to
$w^\ast$, which lies in the ball, so it keeps the inequality, and it is what guarantees a bound $G$ on the
subgradients.) $\square$

The striking part: the bound does not depend on $n$. To reach accuracy $\varepsilon$ Pegasos needs about
$\tilde O(1/(\lambda\varepsilon))$ steps however large the data set. Each step costs $O(d)$.

**The bias.** Pegasos has no separate $b$. The simplest fix, used below, is to append a constant feature 1 to every
$x$ so that the last weight plays the role of $b$. This also regularizes the bias (it adds $\frac\lambda2 b^2$), a
slightly different problem, but with small $\lambda$ the difference is tiny. To measure the error of Pegasos we need
the exact optimum of the same problem. With the bias folded in, the dual has no equality constraint, only the box
$0 \le \alpha_i \le 1/(\lambda n)$, and can be solved one coordinate at a time in closed form (**dual coordinate
ascent**; Hsieh, Chang, Lin, Keerthi and Sundararajan, 2008, the method inside LIBLINEAR): the program uses that as
its reference.

```python
--8<-- "books/machine-learning/ch10_pegasos.py"
```

```
1. Losses as functions of the margin m = y f(x)
      m    0-1   hinge max(0,1-m)   logistic log2(1+e^-m)   squared (1-m)^2
   -2.0    1           3.000               3.069             9.000
   -1.0    1           2.000               1.895             4.000
    0.0    1           1.000               1.000             1.000
    0.5    0           0.500               0.684             0.250
    1.0    0           0.000               0.452             0.000
    2.0    0           0.000               0.183             1.000
    3.0    0           0.000               0.070             4.000

2. Exact optimum (dual coordinate ascent): w = [1.5039 1.1039 0.0896], objective 0.238086

3. Pegasos: objective minus the optimum
        T     last iterate    averaged iterate
       10         1.054634        0.131397
      100         0.220511        0.231971
     1000         0.016147        0.024708
    10000         0.000873        0.001968
   100000         0.000098        0.000227
  final w = [1.5178 1.0961 0.0708]
  training accuracy 0.88; support vectors (margin <= 1): 27

4. Hand trace: first three Pegasos steps on the points of 10.2, lam = 0.1, no bias
  t = 1: example [3. 3.], label +1, margin before 0.000, eta = 10.000, w = [30. 30.]
  t = 2: example [2. 0.], label -1, margin before -60.000, eta = 5.000, w = [ 5. 15.]
  t = 3: example [0. 2.], label -1, margin before -30.000, eta = 3.333, w = [3.3333 3.3333]
```

The same data and $C = 1$ as the SMO run, so $\lambda = 1/(nC) = 0.01$. The exact solution
$w = (1.5039, 1.1039)$, bias $0.0896$, is within $0.0005$ of SMO's $(1.5035, 1.1035)$, $b = 0.0895$: the regularized bias
barely matters. The objective $0.238086$ is SMO's primal value $23.8049$ divided by $nC = 100$ plus the small bias
penalty, as the rescaling in 10.3 predicts. The error of Pegasos falls roughly tenfold per tenfold increase in $T$,
the $1/T$ rate of the theorem. The averaged iterate, which the theorem is about, is here a little worse than the last
iterate, because the average still remembers the poor early steps; in practice people often average only the second
half of the run.

### SMO: two variables at a time

John Platt's **sequential minimal optimization** (1998) attacks the dual directly. The equality constraint
$\sum_i \alpha_i y_i = 0$ means you cannot change one $\alpha_i$ alone; but you can change two. SMO repeatedly picks a
pair $(i, j)$, solves the dual exactly in those two variables with all others fixed, and repeats until every point
satisfies the KKT conditions of 10.4 within a tolerance.

**The two-variable update, derived.** Write $s = y_i y_j$, $E_k = f(x_k) - y_k$ for the current error on point $k$,
and $\eta = K_{ii} + K_{jj} - 2K_{ij}$. Change $\alpha_j$ by $\Delta$ and $\alpha_i$ by $-s\Delta$, which keeps
$\alpha_i y_i + \alpha_j y_j$ fixed. With $v_k = \alpha_k y_k$, the vector $v$ changes by $y_j \Delta (e_j - e_i)$ (because
$y_i s = y_j$), where $e_k$ is the $k$-th unit vector. The dual objective $D(\alpha) = \sum_k \alpha_k - \frac12 v^\top K v$
changes by

$$
\Delta D = \Delta (1 - s) - y_j \Delta\, (e_j - e_i)^\top K v - \tfrac12 \Delta^2\, (e_j - e_i)^\top K (e_j - e_i).
$$

Now $(Kv)_k = f(x_k) - b$, so $(e_j - e_i)^\top K v = f(x_j) - f(x_i)$; the last quadratic form is $\eta$; and
$1 - s = y_j(y_j - y_i)$. Collecting, the coefficient of $\Delta$ is
$y_j\big[(y_j - y_i) - (f(x_j) - f(x_i))\big] = y_j (E_i - E_j)$, and

$$
\Delta D = y_j (E_i - E_j)\, \Delta - \tfrac12 \eta\, \Delta^2,
$$

a downward parabola in $\Delta$ (since $\eta = \lVert \varphi(x_i) - \varphi(x_j) \rVert^2 \ge 0$). Its maximum is at
$\Delta = y_j (E_i - E_j)/\eta$, so

$$
\alpha_j^{\mathrm{new}} = \alpha_j + \frac{y_j (E_i - E_j)}{\eta}, \qquad \text{clipped to } [L, H], \qquad
\alpha_i^{\mathrm{new}} = \alpha_i + s\,(\alpha_j - \alpha_j^{\mathrm{new}}).
$$

The bounds $L$ and $H$ keep both variables in $[0, C]$ as they move along their line. If $y_i \ne y_j$ the line is
$\alpha_j - \alpha_i = \text{const}$, giving $L = \max(0, \alpha_j - \alpha_i)$, $H = \min(C, C + \alpha_j - \alpha_i)$; if
$y_i = y_j$ it is $\alpha_i + \alpha_j = \text{const}$, giving $L = \max(0, \alpha_i + \alpha_j - C)$,
$H = \min(C, \alpha_i + \alpha_j)$. Clipping is correct because the maximum of a concave parabola over an interval is at
the unconstrained peak if it lies inside, and otherwise at the nearer end. After the step, $b$ is reset so that a
free variable among the two satisfies its KKT equality exactly, and all errors $E_k$ are updated in $O(n)$.

<figure class="mars-fig" markdown="0">
<svg viewBox="0 0 640 270" role="img" aria-label="Two panels, each the square from 0 to C for alpha i (horizontal) and alpha j (vertical). Left, labels differ: the feasible pairs form a segment of slope plus one; the unconstrained optimum lies beyond the top edge, so the update is clipped to H where the segment leaves the square. Right, labels equal: the segment has slope minus one and the optimum lies inside it, so no clipping is needed.">
  <g fill="none" stroke="currentColor" stroke-width="1.2">
    <rect x="60" y="40" width="180" height="180"/>
    <rect x="380" y="40" width="180" height="180"/>
    <line x1="60" y1="166" x2="186" y2="40" stroke="#9cc9ea" stroke-width="3"/>
    <line x1="186" y1="40" x2="213" y2="13" stroke-dasharray="4 3"/>
    <line x1="380" y1="76" x2="524" y2="220" stroke="#9cc9ea" stroke-width="3"/>
  </g>
  <g stroke="currentColor" stroke-width="1">
    <circle cx="96" cy="130" r="5" fill="currentColor"/>
    <circle cx="213" cy="13" r="5" fill="none"/>
    <circle cx="186" cy="40" r="6" fill="#eea66f"/>
    <circle cx="470" cy="166" r="5" fill="currentColor"/>
    <circle cx="416" cy="112" r="6" fill="#eea66f"/>
  </g>
  <g font-size="12" fill="currentColor" text-anchor="middle">
    <text x="150" y="240">alpha i</text>
    <text x="470" y="240">alpha i</text>
    <text x="40" y="134" transform="rotate(-90 40 134)">alpha j</text>
    <text x="360" y="134" transform="rotate(-90 360 134)">alpha j</text>
    <text x="60" y="234">0</text><text x="240" y="234">C</text>
    <text x="380" y="234">0</text><text x="560" y="234">C</text>
    <text x="150" y="262">labels differ: clipped to H</text>
    <text x="470" y="262">labels equal: optimum inside</text>
    <text x="120" y="126" text-anchor="start">now</text>
    <text x="224" y="18" text-anchor="start">peak</text>
    <text x="196" y="58" text-anchor="start">new</text>
    <text x="482" y="166" text-anchor="start">now</text>
    <text x="428" y="108" text-anchor="start">new</text>
  </g>
</svg>
<figcaption>One SMO step. The pair (αᵢ, αⱼ) must stay on the blue segment (to keep Σ αₖyₖ = 0) and inside the box
[0, C]². The dual objective is a downward parabola along the segment; the new point is its peak, clipped to the
segment's end when the peak lies outside the box.</figcaption>
</figure>

**Choosing the pair.** Any pair that contains a KKT violator increases the dual strictly (a result of Edgar Osuna,
Robert Freund and Federico Girosi, 1997), so the method makes progress as long as a violator exists. Platt's
heuristics choose $i$ among the violators and $j$ to maximise $|E_i - E_j|$, which roughly maximises the step; our
program uses that first and falls back to other partners in random order if the step is too small. Sathiya Keerthi and
Elmer Gilbert (2002) proved that SMO with a suitable choice of pairs converges to the optimum in a finite number of
steps for any positive tolerance. Each step costs $O(n)$, and the method needs only one row of the kernel matrix at a
time, never the whole matrix: that is why SMO made SVMs practical on large data. LIBSVM (Chih-Chung Chang and
Chih-Jen Lin, 2011) is a refined SMO with better pair selection and kernel caching.

**In practice.** scikit-learn's `SVC` wraps LIBSVM (SMO, kernels, one-versus-one for many classes) and `LinearSVC`
wraps LIBLINEAR (dual coordinate ascent for linear SVMs); its `SGDClassifier` with hinge loss is Pegasos-style
stochastic training. Kernel SVMs scale to tens or hundreds of thousands of points; beyond that, linear SVMs on good
features, random features (Chapter 9, exercise 11) or neural networks take over.

## Check yourself

??? question "1. What is the distance from the point (1, 2) to the line 3x₁ + 4x₂ − 10 = 0, and on which side is it?"

    $w = (3, 4)$, $\lVert w \rVert = 5$, $w \cdot x + b = 3 + 8 - 10 = 1$, so the signed distance is $1/5 = 0.2$: it is
    $0.2$ units away, on the side that $w$ points to (the positive side).

??? question "2. Two training points: (0, 0) with label −1 and (2, 2) with label +1. Find the hard-margin SVM (w, b), its margin and the multipliers α."

    By symmetry the decision line is the perpendicular bisector $x_1 + x_2 = 2$, so $w = (c, c)$. Canonical scaling:
    $w\cdot(2,2) + b = 1$ and $w \cdot (0,0) + b = -1$, so $b = -1$ and $4c = 2$, $c = 0.5$. Then $\lVert w \rVert = 0.7071$,
    margin $\sqrt 2$, width $2\sqrt 2 = 2.83$, the distance between the points. From $\sum \alpha_i y_i = 0$ the two
    multipliers are equal, $\alpha$, and $w = \alpha(2,2) - \alpha(0,0) = (2\alpha, 2\alpha)$, so $\alpha = 0.25$. Check:
    dual objective $0.5 - \tfrac12 \cdot 0.5 = 0.25 = \tfrac12\lVert w \rVert^2$.

??? question "3. In a soft-margin solution, point A has y f(x) = 0.4 and point B has y f(x) = −0.5. What are their slacks, which is misclassified, and what are their α values?"

    $\xi_A = 1 - 0.4 = 0.6$ (inside the band, correct side) and $\xi_B = 1 + 0.5 = 1.5$ (wrong side, misclassified).
    Both have $\xi > 0$, so $\mu = 0$ by complementary slackness and $\alpha = C - \mu = C$: both are bound support
    vectors. Since a misclassified point has $\xi > 1$, $\sum_i \xi_i$ is at least the number of training errors.

??? question "4. Show that the SVM dual is a concave maximisation problem, so it has no bad local maxima."

    The objective is $\sum_i \alpha_i - \frac12 v^\top K v$ with $v = (\alpha_i y_i)_i$, a linear map of $\alpha$. In terms of
    $\alpha$ the quadratic part is $-\frac12 \alpha^\top (Y K Y) \alpha$, $Y = \mathrm{diag}(y)$. For any $c$,
    $c^\top Y K Y c = (Yc)^\top K (Yc) \ge 0$ because $K$ is a Gram matrix (PSD), so the Hessian $-YKY$ is negative
    semidefinite and the objective is concave. The constraints (a box and a hyperplane) form a convex set, so every
    local maximum is global.

??? question "5. Show that the C-SVM objective and the Pegasos objective with λ = 1/(nC) have the same minimiser."

    $\frac{1}{nC}\Big(\tfrac12\lVert w\rVert^2 + C\sum_i \xi_i\Big) = \frac{1}{2nC}\lVert w \rVert^2 + \frac1n \sum_i \xi_i
    = \frac\lambda2 \lVert w \rVert^2 + \frac1n\sum_i \max(0, 1 - y_i f(x_i))$. Multiplying an objective by a positive
    constant does not move its minimiser. The program checks it: SMO's primal $23.8049$ divided by $nC = 100$ is
    $0.2380$, Pegasos's optimum $0.2381$ (which also includes a tiny bias penalty).

??? question "6. Continue the Pegasos hand trace of 10.6 for one more step with the example (3, 3), label +1."

    $t = 4$, $\eta_4 = 1/(0.1 \cdot 4) = 2.5$. The margin before is $w \cdot (3,3) = 3.333 \cdot 6 = 20 \ge 1$, so there is
    no pull, only shrinkage: $w \leftarrow (1 - 2.5 \cdot 0.1) w = 0.75 \cdot (3.333, 3.333) = (2.5, 2.5)$. Equivalently,
    $w_4 = \frac{1}{0.4}\big((3,3) - (2,0) - (0,2)\big) = (2.5, 2.5)$.

??? question "7. Do one SMO step by hand on the two points of exercise 2 with C = 10, starting from α = 0 and b = 0. Do you reach the optimum?"

    Initially $f = 0$, so $E_1 = 0 - (-1) = 1$ for $(0,0)$ and $E_2 = 0 - 1 = -1$ for $(2,2)$. With the linear kernel
    $K_{11} = 0$, $K_{22} = 8$, $K_{12} = 0$, so $\eta = 8$. Taking $i = 1$, $j = 2$:
    $\alpha_2^{\mathrm{new}} = 0 + 1 \cdot (1 - (-1))/8 = 0.25$; labels differ, so $L = 0$, $H = 10$, no clipping;
    $\alpha_1^{\mathrm{new}} = 0 + (-1)(0 - 0.25) = 0.25$. Then $b_1 = 0 - E_1 - y_1(0.25)K_{11} - y_2 (0.25) K_{12} = -1$,
    and $\alpha_1$ is free, so $b = -1$. Now $w = 0.25(2,2) - 0.25(0,0) = (0.5, 0.5)$: exactly the optimum of exercise
    2, in one step. With two points the dual has only one free direction, so one exact step solves it.

??? question "8. The linear SVM of 10.5 at C = 1 has 27 support vectors among 100 points. What can you say about its leave-one-out error without running leave-one-out? Is the bound useful for the RBF run with γ = 100?"

    Leave-one-out error $\le 27/100 = 0.27$. For $\gamma = 100$, $C = 1$ there are 138 support vectors among 140
    points, so the bound is $0.986$: true but useless. The bound is informative only when the solution is sparse, which
    is itself a sign of a simple model.

??? question "9. Write the code: one-versus-rest classification of three Gaussian clusters with three Pegasos SVMs."

    ```python
    import numpy as np

    rng = np.random.default_rng(0)
    centres = np.array([[0, 3], [3, -1], [-3, -1]])
    X = np.vstack([rng.normal(c, 1.0, (60, 2)) for c in centres])
    X = np.column_stack([X, np.ones(len(X))])          # bias as a constant feature
    y = np.repeat([0, 1, 2], 60)


    def pegasos(X, s, lam=0.01, T=20000, seed=0):
        r = np.random.default_rng(seed)
        w = np.zeros(X.shape[1])
        for t in range(1, T + 1):
            i = r.integers(len(s))
            eta = 1 / (lam * t)
            hit = s[i] * (w @ X[i]) < 1
            w = (1 - eta * lam) * w + (eta * s[i] * X[i] if hit else 0)
        return w


    W = np.array([pegasos(X, np.where(y == c, 1.0, -1.0)) for c in range(3)])
    pred = np.argmax(X @ W.T, axis=1)                   # the most confident of the three
    print("weights per class:\n", np.round(W, 3))
    print(f"training accuracy {np.mean(pred == y):.3f}")
    ```

    It prints the three weight vectors (for class 0, about $(-0.115, 1.274)$ with bias $-1.425$: "is $x_2$ large?") and
    a training accuracy of 0.994. Each SVM answers "this class or not"; the argmax resolves points that two of them
    claim, or that none claims.

??? question "10. (Hard) With the RBF kernel and γ → ∞ the Gram matrix becomes the identity. For balanced classes and C ≥ 1, find the dual solution, b, and the prediction at a point far from all training points."

    With $K = I$ the dual is $\max \sum_i \alpha_i - \frac12\sum_i \alpha_i^2$ subject to $0 \le \alpha_i \le C$ and
    $\sum_i \alpha_i y_i = 0$. Ignoring the constraints, each term is maximised at $\alpha_i = 1$; that choice satisfies
    the box (since $C \ge 1$) and the equality (equal numbers of $+1$ and $-1$), so it is optimal. Every point is a
    support vector with $\alpha_i = 1 < C$ (free if $C > 1$). At a training point $f(x_i) = \sum_j \alpha_j y_j K_{ij} + b = y_i + b$,
    and the KKT equality $y_i f(x_i) = 1$ gives $b = 0$. At a far point all kernel values vanish and $f(x) = b = 0$: the
    SVM has memorised the training set and knows nothing elsewhere, which is what the $\gamma = 100$ rows of 10.5 show.

??? question "11. (Hard) Remove the bias from the SVM (no b). Derive the dual and explain why it can be solved one coordinate at a time, and give the coordinate update."

    Without $b$ there is no $\partial L / \partial b$ condition, so the constraint $\sum_i \alpha_i y_i = 0$ disappears; the
    dual is $\max \sum_i \alpha_i - \frac12 \sum_{i,j} \alpha_i \alpha_j y_i y_j K_{ij}$ subject to $0 \le \alpha_i \le C$ only.
    Changing one $\alpha_i$ by $\delta$ changes the objective by $\delta(1 - y_i f(x_i)) - \frac12 \delta^2 K_{ii}$, where
    $f(x_i) = \sum_j \alpha_j y_j K_{ij}$. The best $\delta$ is $(1 - y_i f(x_i))/K_{ii}$, and the box is respected by
    clipping: $\alpha_i \leftarrow \min\big(\max(\alpha_i - (y_i f(x_i) - 1)/K_{ii},\ 0),\ C\big)$, which is exactly the
    update in `dual_coordinate_ascent` of `ch10_pegasos.py` (with $f(x_i) = w \cdot x_i$ kept up to date by adding
    $\delta\, y_i x_i$ to $w$). With the equality constraint present, one coordinate cannot move alone, which is why SMO
    needs two.

## What you learned

- The distance from $x$ to the hyperplane $w\cdot x + b = 0$ is $(w\cdot x + b)/\lVert w \rVert$; with the canonical
  scaling the margin is $1/\lVert w \rVert$, so the widest margin means the smallest $\lVert w \rVert$.
- The hard-margin SVM is a convex QP with a unique $w$; the soft margin adds slacks priced by $C$, and eliminating the
  slacks shows the SVM minimises the hinge loss plus an L2 penalty.
- Lagrange duality gives lower bounds (weak duality) that are tight for convex problems with affine constraints; the
  KKT conditions, above all complementary slackness, characterise the optimum.
- The SVM dual has one variable per point, uses the data only through dot products, and its solution is sparse:
  only support vectors ($\alpha_i > 0$) define $w$, and they bound the leave-one-out error.
- Replacing dot products by a kernel gives non-linear boundaries with no loss of convexity; with the RBF kernel,
  $\gamma$ and $C$ trade smoothness against fit, and huge $\gamma$ memorises.
- Pegasos takes stochastic subgradient steps of size $1/(\lambda t)$ and reaches accuracy $\varepsilon$ in about
  $1/(\lambda\varepsilon)$ steps independent of $n$; SMO solves the dual two variables at a time by an exact clipped
  update.

**Next:** [Chapter 11](11-Decision-Trees-and-Ensembles.md) leaves geometry behind for a model that asks yes-or-no
questions about one feature at a time: decision trees, and the forests and boosted ensembles built from them.

## Further reading

- C. Cortes and V. Vapnik, "Support-Vector Networks", *Machine Learning*, 1995.
- B. Boser, I. Guyon and V. Vapnik, "A Training Algorithm for Optimal Margin Classifiers", COLT 1992.
- V. Vapnik, *The Nature of Statistical Learning Theory*, 1995, and *Statistical Learning Theory*, 1998.
- J. Platt, "Sequential Minimal Optimization: A Fast Algorithm for Training Support Vector Machines", Microsoft
  Research technical report MSR-TR-98-14, 1998.
- S. S. Keerthi and E. G. Gilbert, "Convergence of a Generalized SMO Algorithm for SVM Classifier Design", *Machine
  Learning*, 2002.
- S. Shalev-Shwartz, Y. Singer and N. Srebro, "Pegasos: Primal Estimated sub-GrAdient SOlver for SVM", ICML 2007.
- C.-J. Hsieh, K.-W. Chang, C.-J. Lin, S. S. Keerthi and S. Sundararajan, "A Dual Coordinate Descent Method for
  Large-scale Linear SVM", ICML 2008.
- C.-C. Chang and C.-J. Lin, "LIBSVM: A Library for Support Vector Machines", *ACM Transactions on Intelligent Systems
  and Technology*, 2011.
- S. Boyd and L. Vandenberghe, *Convex Optimization*, 2004, chapter 5 (duality and the KKT conditions).
- B. Schölkopf and A. Smola, *Learning with Kernels*, 2002, chapters 7 to 10.
- C. Bishop, *Pattern Recognition and Machine Learning*, 2006, chapter 7 (sparse kernel machines).
- T. Hastie, R. Tibshirani and J. Friedman, *The Elements of Statistical Learning*, 2nd ed., 2009, chapter 12.
- S. Shalev-Shwartz and S. Ben-David, *Understanding Machine Learning*, 2014, chapters 15 (SVMs) and 14 (stochastic
  gradient descent, including the strongly convex case).
- On this site: [Chapter 9](09-Nearest-Neighbours-and-Kernels.md) for kernels, [Chapter 5](05-Optimization.md) for
  convexity and stochastic gradient descent, [Chapter 21](21-Learning-Theory.md) for margin bounds and VC dimension,
  and [https://math.akadian.ca/books/](https://math.akadian.ca/books/) for the linear algebra and calculus behind
  Lagrange multipliers.
