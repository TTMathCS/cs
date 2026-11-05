# 8. Overfitting, bias, variance and regularization

*A model with enough freedom can fit any training set perfectly, noise and all, and then predict new data badly.
Chapter 7 showed how to measure that honestly. This chapter explains it and controls it. You will watch polynomials
go from too stiff to wildly wiggly, derive the decomposition of test error into bias, variance and noise and check it
by simulating two thousand training sets, then tame the variance with ridge regression (closed form, shrinkage, and a
Bayesian reading) and the lasso (sparsity, the geometry of the L1 corner, and coordinate descent from scratch). Then
you will meet the quieter regularisers, early stopping and data augmentation, choose penalties with validation curves,
and finish with effective degrees of freedom and the elastic net.*

!!! abstract "In this chapter"
    **You will learn:**

    - what underfitting and overfitting look like, and why training error always falls as models grow
    - the bias-variance decomposition of expected squared error, derived, and measured by simulation
    - ridge regression: the closed form, why it always has a unique solution, shrinkage along singular directions, a proof that some penalty beats least squares, and ridge as a Bayesian posterior mean
    - the lasso: soft thresholding derived, why the L1 corner produces exact zeros, coordinate descent from scratch, the lasso path
    - early stopping as a regulariser (with its link to ridge, derived), noise augmentation, and validation curves
    - effective degrees of freedom, the optimism of training error (proved), and the elastic net for correlated features

    **You need:** [Chapter 4](04-Linear-Regression.md) (least squares, polynomial features, the SVD),
    [Chapter 5](05-Optimization.md) (gradient descent, convexity) and [Chapter 7](07-Evaluating-Models.md)
    (validation, cross-validation). 8.3's Bayesian view uses Gaussian densities from
    [Chapter 3](03-The-Math-Toolkit.md).

    **Levels:** 8.1 is beginner; 8.2, 8.3 and 8.5 are intermediate; 8.4 is intermediate to advanced; 8.6 is advanced.

## 8.1 Underfitting and overfitting

Take twenty points from the curve $y=\sin(\pi x)$ on $[-1,1]$, each with Gaussian noise of standard deviation
$\sigma=0.3$ added, and fit polynomials of increasing degree by least squares (Chapter 4's polynomial features
$1,x,x^2,\dots,x^d$). Then measure the mean squared error on the 20 training points and on 2000 fresh test points from
the same source.

```python
--8<-- "books/machine-learning/ch08_bias_variance.py"
```

Output:

```
1. polynomial fits to 20 noisy points of sin(pi x), noise sd 0.3
   degree  train MSE  test MSE   largest |coefficient|
      0       0.4771      0.6522            0.2
      1       0.2279      0.3485            0.8
      3       0.0397      0.1028            2.6
      5       0.0257      0.1408            7.1
      9       0.0189      0.6542           35.1
     12       0.0111      0.7772          195.5
     14       0.0059    513.7857        32137.4
   noise floor (best possible test MSE) = sigma^2 = 0.0900

2. bias-variance by simulation (2000 training sets of 20 points)
   model           bias^2     variance   bias^2+var+sigma^2   measured test MSE
   degree 1           0.1680      0.0325         0.2905           0.2901
   degree 3           0.0030      0.0275         0.1205           0.1202
   degree 5           0.0002      0.1882         0.2784           0.2784
   degree 7           0.0015     11.7806        11.8720          11.8710
   degree 9          16.2411  33680.4744     33696.8056       33696.8856
   degree 9, ridge 0.001   0.0005      0.1366         0.2271           0.2268
   degree 9, ridge 0.1   0.0227      0.0333         0.1459           0.1455

3. degree 12 with ridge penalty lambda: validation curve
   lambda     train MSE  validation MSE  test MSE
   0             0.0111        0.1758      0.7772
   1e-06         0.0119        0.1745      0.2048
   0.0001        0.0201        0.1814      0.3997
   0.001         0.0209        0.1721      0.3574
   0.01          0.0276        0.1405      0.1960
   0.1           0.0543        0.1262      0.1241
   1             0.1236        0.2334      0.2380
   10            0.2882        0.5783      0.4605
   chosen by validation: lambda = 0.1

4. early stopping: gradient descent on degree-12 features, step 1/L
   step      train MSE  validation MSE  test MSE   |w|
       10       0.2471        0.3970      0.4278     0.35
      100       0.0876        0.1450      0.1570     1.00
     1000       0.0374        0.1308      0.1434     1.93
     3000       0.0249        0.1523      0.3399     2.70
    10000       0.0213        0.1765      0.5148     3.39
   100000       0.0203        0.1833      0.4158     4.07
   best validation at step 305: validation 0.1212, test 0.1215

5. degree 12 with input-noise augmentation (200 jittered copies, sd 0.1)
   test MSE without augmentation 0.7772, with 0.1379
```

<figure class="mars-fig" markdown="0">
<svg viewBox="0 0 660 320" role="img" aria-label="Twenty noisy data points from a sine curve on the interval minus 1 to 1, with three fitted polynomials. A straight line of degree 1 misses the shape. A degree 3 curve follows the sine closely. A degree 12 curve wiggles through the points, dips and rises between them, and plunges off the bottom of the plot at the right end.">
  <g stroke="currentColor" stroke-width="1" fill="none">
    <rect x="50" y="40" width="560" height="240"/>
    <line x1="50" y1="160" x2="610" y2="160" stroke-dasharray="2 4" stroke-opacity="0.5"/>
  </g>
  <polyline points="50,160 57,165 64,169 71,174 78,179 85,183 92,187 99,191 106,195 113,199 120,202 127,206 134,209 141,211 148,213 155,215 162,217 169,218 176,219 183,220 190,220 197,220 204,219 211,218 218,217 225,215 232,213 239,211 246,209 253,206 260,202 267,199 274,195 281,191 288,187 295,183 302,179 309,174 316,169 323,165 330,160 337,155 344,151 351,146 358,141 365,137 372,133 379,129 386,125 393,121 400,118 407,114 414,111 421,109 428,107 435,105 442,103 449,102 456,101 463,100 470,100 477,100 484,101 491,102 498,103 505,105 512,107 519,109 526,111 533,114 540,118 547,121 554,125 561,129 568,133 575,137 582,141 589,146 596,151 603,155 610,160" fill="none" stroke="currentColor" stroke-width="1.2" stroke-dasharray="5 4" stroke-opacity="0.7"/>
  <polyline points="50,194 610,101" fill="none" stroke="#9cc9ea" stroke-width="2.5"/>
  <polyline points="50,148 57,157 64,165 71,172 78,179 85,185 92,190 99,195 106,200 113,204 120,208 127,211 134,213 141,216 148,217 155,219 162,220 169,220 176,221 183,221 190,220 197,220 204,219 211,217 218,216 225,214 232,212 239,210 246,207 253,204 260,201 267,198 274,195 281,192 288,188 295,185 302,181 309,177 316,174 323,170 330,166 337,162 344,158 351,154 358,150 365,146 372,143 379,139 386,135 393,132 400,128 407,125 414,122 421,119 428,116 435,113 442,111 449,109 456,107 463,105 470,104 477,103 484,102 491,101 498,101 505,101 512,101 519,102 526,103 533,105 540,107 547,109 554,112 561,115 568,119 575,124 582,128 589,134 596,139 603,146 610,153" fill="none" stroke="#7ccf9a" stroke-width="2.5"/>
  <polyline points="50,169 57,149 64,156 71,174 78,195 85,212 92,224 99,230 106,230 113,226 120,221 127,214 134,207 141,201 148,197 155,195 162,195 169,197 176,200 183,205 190,210 197,216 204,221 211,226 218,230 225,233 232,234 239,234 246,233 253,231 260,227 267,222 274,216 281,210 288,203 295,196 302,189 309,182 316,175 323,169 330,163 337,158 344,153 351,149 358,145 365,142 372,139 379,137 386,134 393,131 400,128 407,125 414,122 421,118 428,114 435,110 442,105 449,101 456,97 463,94 470,92 477,91 484,91 491,92 498,95 505,100 512,105 519,111 526,117 533,121 540,123 547,123 554,120 561,115 568,110 575,110 582,124 589,164 596,252 603,280" fill="none" stroke="#eea66f" stroke-width="2.5"/>
  <g fill="currentColor">
    <circle cx="52" cy="163" r="3.5"/> <circle cx="59" cy="142" r="3.5"/> <circle cx="69" cy="185" r="3.5"/> <circle cx="73" cy="169" r="3.5"/> <circle cx="148" cy="197" r="3.5"/> <circle cx="201" cy="218" r="3.5"/> <circle cx="218" cy="230" r="3.5"/> <circle cx="287" cy="205" r="3.5"/> <circle cx="353" cy="153" r="3.5"/> <circle cx="354" cy="140" r="3.5"/> <circle cx="390" cy="141" r="3.5"/> <circle cx="407" cy="118" r="3.5"/> <circle cx="459" cy="103" r="3.5"/> <circle cx="459" cy="91" r="3.5"/> <circle cx="505" cy="101" r="3.5"/> <circle cx="507" cy="99" r="3.5"/> <circle cx="530" cy="125" r="3.5"/> <circle cx="533" cy="117" r="3.5"/> <circle cx="561" cy="115" r="3.5"/> <circle cx="574" cy="109" r="3.5"/>
  </g>
  <g font-size="12" fill="currentColor">
    <text x="50" y="296" text-anchor="middle">-1</text>
    <text x="330" y="296" text-anchor="middle">0</text>
    <text x="610" y="296" text-anchor="middle">1</text>
    <text x="44" y="44" text-anchor="end">2</text>
    <text x="44" y="164" text-anchor="end">0</text>
    <text x="44" y="284" text-anchor="end">-2</text>
    <text x="60" y="60">blue: degree 1 (underfits)</text>
    <text x="60" y="78">green: degree 3 (about right)</text>
    <text x="60" y="96">orange: degree 12 (overfits)</text>
    <text x="60" y="114">dashed: the true curve sin(πx)</text>
    <text x="330" y="314" text-anchor="middle">input x</text>
  </g>
</svg>
<figcaption>Figure 8.1. Twenty noisy points and three least-squares polynomials. Degree 1 cannot bend; degree 3 follows the true curve; degree 12 chases the noise, wiggles between the points and dives off the plot near x = 1, where there are no data to hold it.</figcaption>
</figure>

Three regimes are visible.

**Underfitting.** Degree 0 (a constant) and degree 1 (a line) cannot bend, so they miss the shape: both training and
test error are high (0.48 and 0.65 for the constant). The model is too simple for the pattern.

**About right.** Degree 3 has training error $0.040$ and test error $0.103$, close to the **noise floor** of $0.09$.
The noise floor is $\sigma^2$, the error even the true curve would make on new noisy points, and no model can beat it
on average.

**Overfitting.** Degrees 9, 12 and 14 keep lowering the training error, down to $0.006$, while the test error climbs to
$0.65$, $0.78$ and then $514$. With 15 coefficients for 20 points, degree 14 has enough freedom to pass very near
every training point, and it buys that with huge coefficients (32137) that cancel each other on the data and explode
between and beyond them. The model has learned the noise.

Training error **always** falls (or stays the same) as the degree grows, because each polynomial family contains the
smaller ones: degree 13 can always set its top coefficient to 0. So training error cannot be used to choose the
complexity. That is the whole reason Chapter 7's validation methods exist. Figure 8.2 shows the classic shape: training
error falls steadily; test error falls, then rises.

<figure class="mars-fig" markdown="0">
<svg viewBox="0 0 660 320" role="img" aria-label="Plot of training and test mean squared error against polynomial degree from 0 to 13. The training error curve falls steadily from about 0.48 to about 0.01. The test error falls from 0.65 to a minimum of about 0.10 at degrees 3 and 4, then rises irregularly, reaching 0.78 at degree 12. A dashed line marks the noise floor 0.09.">
  <g stroke="currentColor" stroke-width="1.2" fill="none">
    <line x1="60" y1="270" x2="600" y2="270"/>
    <line x1="60" y1="270" x2="60" y2="30"/>
    <line x1="60" y1="243" x2="600" y2="243" stroke-dasharray="4 4" stroke-opacity="0.6"/>
  </g>
  <polyline points="60,127 100,202 140,217 180,258 220,258 260,262 300,263 340,263 380,264 420,264 460,267 500,267 540,267 580,267" fill="none" stroke="#9cc9ea" stroke-width="2.5"/>
  <polyline points="60,74 100,165 140,162 180,239 220,239 260,228 300,211 340,214 380,137 420,74 460,162 500,215 540,37 580,102" fill="none" stroke="#eea66f" stroke-width="2.5"/>
  <g font-size="12" fill="currentColor">
    <text x="54" y="274" text-anchor="end">0</text>
    <text x="54" y="214" text-anchor="end">0.2</text>
    <text x="54" y="154" text-anchor="end">0.4</text>
    <text x="54" y="94" text-anchor="end">0.6</text>
    <text x="54" y="34" text-anchor="end">0.8</text>
    <line x1="56" y1="210" x2="60" y2="210" stroke="currentColor"/>
    <line x1="56" y1="150" x2="60" y2="150" stroke="currentColor"/>
    <line x1="56" y1="90" x2="60" y2="90" stroke="currentColor"/>
    <line x1="56" y1="30" x2="60" y2="30" stroke="currentColor"/>
    <text x="60" y="288" text-anchor="middle">0</text>
    <text x="180" y="288" text-anchor="middle">3</text>
    <text x="260" y="288" text-anchor="middle">5</text>
    <text x="420" y="288" text-anchor="middle">9</text>
    <text x="540" y="288" text-anchor="middle">12</text>
    <text x="330" y="308" text-anchor="middle">polynomial degree</text>
    <text x="606" y="247">noise 0.09</text>
    <text x="250" y="60">orange: test MSE</text>
    <text x="250" y="78">blue: training MSE</text>
    <text x="20" y="20">MSE</text>
  </g>
</svg>
<figcaption>Figure 8.2. Training and test error against degree for the twenty-point data set (degree 14, with test MSE 514, is off the chart). The test curve is jagged because it comes from one small training set; averaging over many training sets, as in 8.2, smooths it.</figcaption>
</figure>

The jaggedness is itself a lesson: with 20 points, a single training set gives a noisy view of how a degree performs.
To see the underlying law we need to average over many training sets.

<figure class="play" data-play="polyfit"><span class="ai-tag">AI-created</span><figcaption><b>Try it.</b> Fit ten noisy points (red) with polynomials of rising degree. Training error keeps falling; error on fresh points from the same curve (blue) falls, then rises. The data are made up.</figcaption></figure>

## 8.2 The bias-variance decomposition

*Level: intermediate.*

Why does test error fall and then rise? Think of the training set as random: someone else collecting 20 points from
the same source would get a different set, and a different fitted curve. So at a fixed input $x$ the prediction
$\hat f(x)$ is a random variable, with a mean $\bar f(x)=\mathbb E[\hat f(x)]$ over training sets and a spread around
that mean.

Assume the data come from $y=f(x)+\varepsilon$, where $f$ is the true function and the noise $\varepsilon$ has mean 0
and variance $\sigma^2$, independent of everything else. A new test point at $x$ has its own fresh noise.

**Theorem 8.1 (bias-variance decomposition).** At a fixed input $x$, the expected squared error of the prediction on a
new $y$, averaged over training sets and over the new noise, is

$$\mathbb E\bigl[(y-\hat f(x))^2\bigr]=\underbrace{\sigma^2}_{\text{noise}}+\underbrace{\bigl(f(x)-\bar f(x)\bigr)^2}_{\text{bias}^2}+\underbrace{\mathbb E\bigl[(\hat f(x)-\bar f(x))^2\bigr]}_{\text{variance}}.$$

*Proof.* Write $y-\hat f=(y-f)+(f-\bar f)+(\bar f-\hat f)$, dropping the argument $x$. Square and take expectations.
The three squared terms give $\mathbb E[\varepsilon^2]=\sigma^2$, the constant $(f-\bar f)^2$, and
$\mathbb E[(\hat f-\bar f)^2]$. The cross terms vanish:

- $2\,\mathbb E[\varepsilon\,(f-\bar f)]=2(f-\bar f)\,\mathbb E[\varepsilon]=0$;
- $2\,\mathbb E[\varepsilon\,(\bar f-\hat f)]=0$, because the new noise is independent of the training set that
  determined $\hat f$, and has mean 0;
- $2(f-\bar f)\,\mathbb E[\bar f-\hat f]=0$, because $\mathbb E[\hat f]=\bar f$ by definition. $\square$

Each term has a meaning:

- **Noise** $\sigma^2$: what no model can remove. It is the floor.
- **Bias** $f(x)-\bar f(x)$: how far the *average* fitted curve is from the truth, a systematic error. A straight line
  fitted to a sine curve is wrong on average however many training sets you average over: high bias.
- **Variance**: how much the fitted curve jumps around from one training set to another. A degree-14 polynomial passes
  near whatever 20 points it is given, so it changes wildly with the data: high variance.

Making a model more flexible usually lowers bias and raises variance; restricting it does the reverse. The best test
error is a compromise, the **bias-variance trade-off**. The idea goes back at least to Geman, Bienenstock and Doursat
(1992), who made it a central theme for neural networks.

### Measured by simulation

The second block of the program draws 2000 training sets of 20 points, fits each, records the predictions on a grid of
200 inputs, and computes the average bias squared and variance over the grid, together with the actual average test
error on fresh noisy points. The theorem predicts that bias$^2$ + variance + $\sigma^2$ equals the measured test error,
and it does, to the third or fourth digit, in every row.

| model | bias$^2$ | variance | sum $+\sigma^2$ | measured |
|---|---|---|---|---|
| degree 1 | 0.1680 | 0.0325 | 0.2905 | 0.2901 |
| degree 3 | 0.0030 | 0.0275 | 0.1205 | 0.1202 |
| degree 5 | 0.0002 | 0.1882 | 0.2784 | 0.2784 |
| degree 7 | 0.0015 | 11.78 | 11.87 | 11.87 |
| degree 9 | 16.2 | 33680 | 33697 | 33697 |
| degree 9, ridge $\lambda=0.001$ | 0.0005 | 0.1366 | 0.2271 | 0.2268 |
| degree 9, ridge $\lambda=0.1$ | 0.0227 | 0.0333 | 0.1459 | 0.1455 |

The line has high bias and low variance. Degree 3 has both small: the best plain model here. From degree 5 on, bias is
essentially gone but variance explodes; for degree 9 it is enormous because a few of the 2000 random training sets
leave gaps near the ends of the interval, where the polynomial is free to shoot off (the grid runs to $\pm0.95$). Even
the bias of degree 9 is large, $16.2$, because those rare huge predictions do not cancel in the average. The last two
rows preview 8.3: the same degree-9 model with a small **ridge penalty** has a little more bias and drastically less
variance, and with $\lambda=0.1$ it is nearly as good as degree 3. Regularisation is the art of buying a large cut in
variance for a small price in bias.

Two honest caveats. The decomposition is exact for squared error; for classification with 0-1 loss there is no
equally clean split, and several competing definitions exist (Domingos 2000 proposed a unified one). And the U-shaped
test curve is not the whole story for very large models: past the point where the model can interpolate the training
data, test error can fall again (**double descent**, Belkin et al. 2019), which [Chapter
21](21-Learning-Theory.md) discusses.

## 8.3 Ridge regression

*Level: intermediate.*

Look again at the degree-14 fit: its coefficients run into the tens of thousands. Large coefficients are how a
polynomial makes sharp wiggles. So penalise them. **Ridge regression** minimises the squared error plus $\lambda$ times
the squared length of the weight vector:

$$J(w)=\lVert y-Xw\rVert^2+\lambda\lVert w\rVert^2,\qquad\lambda\ge0.$$

The **penalty** (or **regularisation**) strength $\lambda$ is a hyperparameter, chosen by validation. $\lambda=0$ is least
squares; as $\lambda\to\infty$ all weights are forced to 0. Arthur Hoerl and Robert Kennard introduced it in 1970, for a
different symptom of the same disease: when features are nearly collinear, $X^\top X$ is nearly singular, and least
squares gives huge, unstable coefficients. (Andrey Tikhonov had studied the same idea for ill-posed integral equations
in 1943 and the 1960s, so in numerical analysis it is **Tikhonov regularisation**.)

Two conventions matter in practice. **Standardise** the features first (Chapter 2), since the penalty treats all weights
alike and a feature measured in millimetres would otherwise be penalised a thousand times less than the same feature in
metres. And **do not penalise the intercept**: shifting all $y$ by a constant should shift the predictions, not fight
the penalty. Centring $y$ and the features removes the intercept, which is what the second program does.

### The closed form

Set the gradient to zero: $\nabla J=-2X^\top(y-Xw)+2\lambda w=0$, so $(X^\top X+\lambda I)w=X^\top y$ and

$$\hat w_\lambda=(X^\top X+\lambda I)^{-1}X^\top y.$$

**The inverse always exists for $\lambda>0$.** For any $v\ne0$,
$v^\top(X^\top X+\lambda I)v=\lVert Xv\rVert^2+\lambda\lVert v\rVert^2\ge\lambda\lVert v\rVert^2>0$, so the matrix is
positive definite and invertible, even when $X^\top X$ is singular (for example when there are more features than
examples, $p>n$). The same calculation shows that $J$ is strictly convex with Hessian $2(X^\top X+\lambda I)$, so the
solution is the unique minimum. Ridge also improves the condition number from $d_1^2/d_p^2$ to
$(d_1^2+\lambda)/(d_p^2+\lambda)$, where the $d_j$ are the singular values of $X$, which is what Hoerl and Kennard
wanted.

### Shrinkage, seen through the SVD

Write the thin SVD $X=UDV^\top$ (Chapter 4.7), with singular values $d_1\ge\dots\ge d_p$, orthonormal columns $u_j$ of
$U$ in data space and $v_j$ of $V$ in weight space. Substituting, $X^\top X+\lambda I=V(D^2+\lambda I)V^\top$, so

$$\hat w_\lambda=\sum_{j=1}^p\frac{d_j}{d_j^2+\lambda}\,(u_j^\top y)\,v_j=\sum_{j=1}^p\underbrace{\frac{d_j^2}{d_j^2+\lambda}}_{\text{shrink factor}}\;\underbrace{\frac{u_j^\top y}{d_j}}_{\text{least squares}}\,v_j.$$

Least squares (the $\lambda=0$ case) divides by $d_j$, so a small singular value, a direction in feature space along
which the data barely vary, gets a huge, noise-dominated coefficient. Ridge multiplies each least-squares component by
$d_j^2/(d_j^2+\lambda)$: near 1 where the data vary a lot ($d_j^2\gg\lambda$), near 0 where they barely vary
($d_j^2\ll\lambda$). It shrinks most exactly where least squares is least trustworthy. The program's first block checks
the SVD formula against the closed form (they agree to $2\times10^{-15}$) on a problem with 50 examples and 20
standardised features, three of which matter, and prints the range of shrink factors: from $0.839$ to $0.992$ at
$\lambda=1$, and from $0.049$ to $0.565$ at $\lambda=100$. The weight norm falls from $3.68$ (least squares) to $1.06$.

```python
--8<-- "books/machine-learning/ch08_ridge_lasso.py"
```

Output:

```
1. ridge: closed form against the SVD formula V diag(d/(d^2+lam)) U^T y
   lambda     1: max difference 2.4e-15; shrink factors from 0.839 to 0.992; |w| = 3.500
   lambda    10: max difference 1.5e-15; shrink factors from 0.342 to 0.929; |w| = 2.656
   lambda   100: max difference 8.2e-16; shrink factors from 0.049 to 0.565; |w| = 1.061
   least squares |w| = 3.679

2. posterior mean with prior sd 0.5 equals ridge with lambda = sigma^2/tau^2 = 4: max difference 0.0e+00
   first five weights: posterior mean +- 2 sd
      w1: +2.369 +- 0.330   (true +3.0)
      w2: -1.474 +- 0.464   (true -2.0)
      w3: +1.099 +- 0.352   (true +1.5)
      w4: +0.062 +- 0.341   (true +0.0)
      w5: +0.033 +- 0.320   (true +0.0)

3. orthonormal columns: lasso = soft-threshold(OLS), ridge = OLS / (1 + lam)
   OLS          [ 2.1793 -0.5542  0.1755  1.0267]
   ridge        [ 1.6764 -0.4263  0.135   0.7898]   OLS/(1+lam) [ 1.6764 -0.4263  0.135   0.7898]
   lasso        [ 1.8793 -0.2542  0.      0.7267]   soft(OLS, lam) [ 1.8793 -0.2542  0.      0.7267]

4. lasso path on the 20-feature problem (true weights 3, -2, 1.5, then 17 zeros)
   lambda   nonzero  w1      w2      w3      largest wrong |w_j|
   3           0    +0.000  -0.000  +0.000   0.000
   2           1    +0.352  -0.000  +0.000   0.000
   1           2    +1.343  -0.688  +0.000   0.000
   0.5         4    +1.969  -1.348  +0.578   0.072
   0.2         5    +2.384  -1.762  +1.100   0.242
   0.1         8    +2.508  -1.886  +1.246   0.329
   0.05       15    +2.571  -1.914  +1.305   0.404
   0.01       16    +2.679  -1.895  +1.425   0.491
   ridge (lambda 10) has 20 nonzero weights

5. lambda chosen by 5-fold CV, then refit on all 50 points; test MSE on 5000 points
   least squares          test MSE 1.7020   nonzero 20
   ridge  (lambda 0.3)    test MSE 1.7545   nonzero 20
   lasso  (lambda 0.1)    test MSE 1.4877   nonzero 8
   noise floor sigma^2 = 1.0000
   averaged over 10 data sets of 30 points:
   least squares          mean test MSE 3.5453
   ridge, CV lambda       mean test MSE 3.1271
   lasso, CV lambda       mean test MSE 1.5857

6. effective degrees of freedom
   ridge lambda     1: formula sum d^2/(d^2+lam) = 19.274, simulated 19.285
   ridge lambda    10: formula sum d^2/(d^2+lam) = 15.272, simulated 15.283
   ridge lambda   100: formula sum d^2/(d^2+lam) =  6.054, simulated  6.060
   lasso lambda   0.5: average number of nonzeros  3.447, simulated  3.308
   lasso lambda   0.1: average number of nonzeros 10.242, simulated 10.004

7. two nearly identical features (correlation 0.9999), true signal 2 z
   lasso       (lambda 0.1)            [ 1.862  0.26   0.    -0.    -0.071]
   elastic net (lambda 0.1, alpha 0.5) [ 1.059  1.062  0.    -0.034 -0.114]
   ridge       (lambda 5)              [ 1.057  1.058  0.025 -0.075 -0.153]
```

### Some penalty always helps

Ridge is biased, and least squares is unbiased (Chapter 4: $\mathbb E[\hat w]=w$ when the model is right). Can a biased
estimator really be better? Yes, and in the simplest setting we can see exactly how much.

**Theorem 8.2 (one weight).** Let $y_i=wx_i+\varepsilon_i$ with independent noise of variance $\sigma^2$, fixed inputs,
and $s=\sum_ix_i^2$. The ridge estimate $\hat w_\lambda=\sum_ix_iy_i/(s+\lambda)$ has mean squared error

$$\mathbb E\bigl[(\hat w_\lambda-w)^2\bigr]=\frac{\lambda^2w^2+\sigma^2s}{(s+\lambda)^2},$$

which decreases as $\lambda$ increases from 0, and is smallest at $\lambda^*=\sigma^2/w^2$.

*Proof.* $\sum_ix_iy_i=ws+\sum_ix_i\varepsilon_i$, which has mean $ws$ and variance $\sigma^2s$. So $\hat w_\lambda$ has
mean $ws/(s+\lambda)$, bias $ws/(s+\lambda)-w=-\lambda w/(s+\lambda)$, and variance $\sigma^2s/(s+\lambda)^2$. Mean
squared error is bias squared plus variance (the same algebra as Theorem 8.1), which gives the formula. Its
derivative in $\lambda$ is

$$\frac{2\lambda w^2(s+\lambda)-2(\lambda^2w^2+\sigma^2s)}{(s+\lambda)^3}=\frac{2s(\lambda w^2-\sigma^2)}{(s+\lambda)^3},$$

negative for $\lambda<\sigma^2/w^2$ and positive after. $\square$

At $\lambda=0$ the slope is $-2\sigma^2/s^2$, strictly negative: *a little* shrinkage always reduces the error, because
the bias it adds grows like $\lambda^2$ while the variance it removes falls like $\lambda$. Hoerl and Kennard proved the
same for any number of weights: there is always some $\lambda>0$ whose total mean squared error is below that of least
squares. The best $\lambda$ depends on the unknown $w$, which is why in practice we choose it by validation. (A related,
more surprising fact is Stein's result of 1956, made explicit by James and Stein in 1961: when estimating three or more
means at once, shrinking towards zero beats the obvious estimate for *every* true value.)

### The Bayesian view

Chapter 4 showed that least squares is maximum likelihood under Gaussian noise. Now add a **prior**, a belief about $w$
before seeing data: each weight is independently Gaussian around 0 with standard deviation $\tau$,
$p(w)\propto\exp(-\lVert w\rVert^2/(2\tau^2))$. "Weights are probably small." Bayes' rule says the **posterior** is
proportional to likelihood times prior:

$$p(w\mid y)\propto\exp\Bigl(-\frac{\lVert y-Xw\rVert^2}{2\sigma^2}\Bigr)\exp\Bigl(-\frac{\lVert w\rVert^2}{2\tau^2}\Bigr).$$

The most probable $w$, the **maximum a posteriori** (MAP) estimate, maximises the exponent, that is it minimises
$\lVert y-Xw\rVert^2+\frac{\sigma^2}{\tau^2}\lVert w\rVert^2$. That is ridge with $\lambda=\sigma^2/\tau^2$. The
exponent is a quadratic in $w$, so the posterior is itself Gaussian (completing the square), with covariance
$\Sigma=(X^\top X/\sigma^2+I/\tau^2)^{-1}$ and mean $\Sigma X^\top y/\sigma^2$, equal to the ridge solution; for a
Gaussian the mode and the mean coincide. A strong prior (small $\tau$) means a large penalty. Theorem 8.2's best
$\lambda^*=\sigma^2/w^2$ is exactly this with $\tau^2=w^2$: the right amount of shrinkage is "noise variance over signal
variance".

The program's second block checks this with $\sigma=1$ and $\tau=0.5$ (so $\lambda=4$): the posterior mean and the ridge
solution are identical, and the posterior also gives an uncertainty for each weight. The two-standard-deviation bands
cover the true values of $w_4$ and $w_5$ (zero), while $w_1$ to $w_3$ are shrunk noticeably below the truth: this prior,
with $\tau=0.5$, is too confident that weights are small, for weights of size 3. Bayesian linear regression is
developed fully in [Chapter 12](12-Probabilistic-Models.md).

## 8.4 The lasso

*Level: intermediate to advanced.*

Ridge makes weights small but never exactly zero; the block 4 output ends with "ridge (lambda 10) has 20 nonzero
weights", though 17 of the true weights are zero. Often we want a model that uses only a few features: it is easier
to explain, cheaper to run, and if most features are irrelevant, it should also predict better. Robert Tibshirani's
**lasso** (1996; "least absolute shrinkage and selection operator") replaces the squared length by the sum of absolute
values, the **L1 norm** $\lVert w\rVert_1=\sum_j|w_j|$:

$$J(w)=\frac1{2n}\lVert y-Xw\rVert^2+\lambda\lVert w\rVert_1.$$

(The factor $\frac1{2n}$ is the common convention of the glmnet software, Friedman, Hastie and Tibshirani 2010; it
only rescales $\lambda$.) The objective is convex, because both terms are, but the absolute value has a corner at 0, so
it is not differentiable there. That corner is the whole point.

### One weight: soft thresholding

Start with the simplest case: minimise $g(w)=\tfrac12(z-w)^2+\lambda|w|$ over a single number $w$, for given $z$ and
$\lambda>0$.

- If $w>0$, $g'(w)=w-z+\lambda$, zero at $w=z-\lambda$, which is positive only if $z>\lambda$.
- If $w<0$, $g'(w)=w-z-\lambda$, zero at $w=z+\lambda$, which is negative only if $z<-\lambda$.
- Otherwise ($|z|\le\lambda$), $g$ decreases towards 0 from both sides (its slope is $w-z+\lambda\ge0$ just right of 0 and
  $w-z-\lambda\le0$ just left of it), so the minimum is at exactly $w=0$.

So the minimiser is the **soft-thresholding** operator

$$S(z,\lambda)=\operatorname{sign}(z)\,\max(|z|-\lambda,\,0):$$

move $z$ towards 0 by $\lambda$, and stop at 0 if you would cross it. For example $S(2.18,0.3)=1.88$, $S(-0.55,0.3)=-0.25$,
$S(0.18,0.3)=0$. Compare ridge's one-weight answer, $z/(1+\lambda)$ for $\tfrac12(z-w)^2+\tfrac\lambda2w^2$, which shrinks by a
*factor* and never reaches 0. In the language of convex analysis, $w=0$ is optimal when 0 is in the **subdifferential**
$\{0-z+\lambda s:s\in[-1,1]\}$, the set of slopes of lines touching $g$ from below at 0, that is when $|z|\le\lambda$.

When the columns of $X$ are orthonormal ($X^\top X=I$), the whole problem separates into one such problem per weight,
with $z_j$ the least-squares coefficient: the lasso soft-thresholds least squares, and ridge divides it by $1+\lambda$.
The third block checks this: with least-squares coefficients $(2.18,-0.55,0.18,1.03)$ and $\lambda=0.3$, the lasso gives
$(1.88,-0.25,0,0.73)$ (one exact zero) and ridge $(1.68,-0.43,0.135,0.79)$.

### Why the corner gives zeros: the picture

By Lagrange duality, minimising squared error plus $\lambda$ times a penalty is the same as minimising squared error
subject to the penalty being at most some budget $t$ (each $\lambda$ corresponds to some $t$). For two weights, the
ridge budget $w_1^2+w_2^2\le t$ is a disc, and the lasso budget $|w_1|+|w_2|\le t$ is a diamond with corners on the
axes. The squared-error contours are ellipses centred at the least-squares solution. The constrained solution is where
the smallest ellipse first touches the budget region.

<figure class="mars-fig" markdown="0">
<svg viewBox="0 0 720 320" role="img" aria-label="Two panels. Left: a diamond centred at the origin, the L1 budget, with elliptical error contours centred at the least-squares point to the upper right; the smallest ellipse touches the diamond exactly at its right corner on the w1 axis, so w2 is zero. Right: a circle, the L2 budget, with the same ellipses; the smallest ellipse touches the circle at a point off the axes, so both weights are nonzero.">
  <g stroke="currentColor" stroke-width="1" stroke-opacity="0.6">
    <line x1="30" y1="170" x2="345" y2="170"/><line x1="110" y1="290" x2="110" y2="40"/>
    <line x1="390" y1="170" x2="705" y2="170"/><line x1="470" y1="290" x2="470" y2="40"/>
  </g>
  <polygon points="170,170 110,110 50,170 110,230" fill="#9cc9ea" fill-opacity="0.45" stroke="currentColor" stroke-width="1.5"/>
  <circle cx="470" cy="170" r="60" fill="#9cc9ea" fill-opacity="0.45" stroke="currentColor" stroke-width="1.5"/>
  <g fill="none" stroke="#eea66f" stroke-width="2">
    <ellipse cx="242" cy="146" rx="97.7" ry="65.7" transform="rotate(-151 242 146)"/>
    <ellipse cx="242" cy="146" rx="48.9" ry="32.9" transform="rotate(-151 242 146)"/>
    <ellipse cx="602" cy="146" rx="87.3" ry="58.7" transform="rotate(-151 602 146)"/>
    <ellipse cx="602" cy="146" rx="43.6" ry="29.3" transform="rotate(-151 602 146)"/>
  </g>
  <circle cx="242" cy="146" r="4" fill="currentColor"/>
  <circle cx="602" cy="146" r="4" fill="currentColor"/>
  <circle cx="170" cy="170" r="6" fill="#7ccf9a" stroke="currentColor"/>
  <circle cx="525" cy="147" r="6" fill="#7ccf9a" stroke="currentColor"/>
  <g font-size="12" fill="currentColor">
    <text x="250" y="140">least squares</text>
    <text x="610" y="140">least squares</text>
    <text x="150" y="196">w2 = 0 exactly</text>
    <text x="340" y="186" text-anchor="end">w1</text>
    <text x="116" y="50">w2</text>
    <text x="700" y="186" text-anchor="end">w1</text>
    <text x="476" y="50">w2</text>
    <text x="110" y="312" text-anchor="middle">lasso: |w1| + |w2| ≤ t</text>
    <text x="470" y="312" text-anchor="middle">ridge: w1² + w2² ≤ t</text>
  </g>
</svg>
<figcaption>Figure 8.3. The same squared-error contours (orange ellipses around the least-squares point) meet two budgets. The diamond's corner sticks out towards the ellipses, so the first contact is at the corner, where w2 = 0. The disc has no corners, so the contact point generically has both weights nonzero. Coordinates computed for the quadratic with matrix [[1, 0.4], [0.4, 1.5]] centred at (2.2, 0.4).</figcaption>
</figure>

The diamond's corners poke out towards the ellipses, so for a wide range of ellipse positions the first contact is a
corner, where one weight is exactly zero. In $p$ dimensions the L1 ball has $2p$ corners and many low-dimensional
edges and faces, all on coordinate subspaces, so contact usually happens where many weights are zero. The disc is
perfectly round, so the contact point is on an axis only by coincidence. Any penalty $\sum_j|w_j|^q$ with $q<1$ is
pointier still and gives sparser solutions, but it is no longer convex; $q=1$ is the smallest exponent that keeps the
problem convex, which is why the lasso is the standard tool.

### Coordinate descent from scratch

With many weights there is no closed form, but there is a beautifully simple algorithm. **Coordinate descent**
minimises over one weight at a time, holding the others fixed, and cycles. With the others fixed, the objective in
$w_j$ is

$$\frac1{2n}\lVert r_j-x_jw_j\rVert^2+\lambda|w_j|+\text{const},$$

where $x_j$ is column $j$ and $r_j=y-\sum_{k\ne j}x_kw_k$ is the **partial residual**, what the other features leave
unexplained. Expanding, this is $\frac{c_j}2w_j^2-\rho_jw_j+\lambda|w_j|+\text{const}$ with $c_j=\lVert x_j\rVert^2/n$ and
$\rho_j=x_j^\top r_j/n$, a one-weight problem of the kind we just solved, after dividing by $c_j$:

$$w_j\leftarrow\frac{S(\rho_j,\lambda)}{c_j}.$$

The function `lasso` in the program is exactly this: a loop over $j$, an update of the full residual after each change
(so each step costs $O(n)$), and a stop when a whole sweep changes no weight by more than $10^{-10}$. Does it converge?
The objective is convex, its smooth part is differentiable, and its non-smooth part is a sum of functions of single
coordinates; for such problems Tseng (2001) proved that cyclic coordinate descent converges to a minimiser. Each update
can only lower the objective, since it minimises exactly over one coordinate.

Two engineering ideas make it fast in practice, and our code uses the first. **Warm starts**: solve for a decreasing
sequence of $\lambda$ values, starting each from the previous solution, since nearby $\lambda$ have nearby solutions.
**Active sets**: after a sweep, cycle only over the nonzero weights until they converge, then check the rest. These are
the main ideas of glmnet (Friedman, Hastie and Tibshirani 2010).

### The lasso path

Block 4 traces the solution as $\lambda$ falls, on the 50-example, 20-feature problem where only $w_1=3$, $w_2=-2$,
$w_3=1.5$ are nonzero. At $\lambda=3$ every weight is zero. (One can show that all weights are zero exactly when
$\lambda\ge\max_j|x_j^\top y|/n$, from the one-weight condition at $w=0$.) As $\lambda$ falls the true features enter one
by one, in order of strength: $w_1$ at $\lambda=2$, $w_2$ by $\lambda=1$, $w_3$ by $\lambda=0.5$. Below that, irrelevant
features start to enter with small weights (the largest wrong weight is $0.07$ at $\lambda=0.5$ and $0.49$ at $\lambda=0.01$).
Notice also that the true weights are **shrunk**: at $\lambda=0.2$, $w_1=2.38$ instead of about 3. The lasso both
selects and shrinks, and a common refinement (the **relaxed lasso**) refits least squares on the selected features.

Block 5 chooses $\lambda$ by 5-fold cross-validation (Chapter 7) and measures the error on 5000 new points. On this
sparse problem the lasso wins clearly: test MSE $1.49$ against $1.70$ for least squares, with 8 nonzero weights instead
of 20. Ridge, at its CV choice $\lambda=0.3$, does no better than least squares here (1.75 against 1.70): with 50 examples
for 20 weights, least squares is not very unstable, and CV's choice of $\lambda$ is itself noisy. The average over ten
fresh data sets of only 30 points, where least squares has to fit 20 weights from 30 examples, gives the general
picture: least squares $3.55$, ridge $3.13$, lasso $1.59$. When few features matter, the lasso's selection is worth a
great deal; when many features each matter a little, ridge tends to win, and Chapter 8.6's elastic net hedges between
them.

What the lasso cannot do: with more features than examples ($p>n$) it selects at most $n$ of them (a property of the
corners of the solution set, Efron et al. 2004); among a group of highly correlated features it tends to pick one
somewhat arbitrarily; and the features it selects are not guaranteed to be the true ones unless the irrelevant features
are not too correlated with the relevant ones (the "irrepresentable condition" of Zhao and Yu 2006). The theory of
when L1 recovers a sparse vector exactly grew into **compressed sensing** (Candès, Romberg and Tao 2006; Donoho 2006).

## 8.5 Early stopping, data augmentation and model selection

Penalties are not the only way to regularise. Anything that limits how far a model can bend to fit the training noise
counts.

### Early stopping

Train a flexible model by gradient descent and watch the validation error. Block 4 of the first program does this for
degree-12 polynomial features (standardised, so gradient descent can make progress), starting from $w=0$. The training
error falls steadily, from $0.247$ at step 10 to $0.020$ at step 100000. The validation error falls to its minimum,
$0.121$, at step 305, then rises, and the test error does the same: $0.122$ at the best validation step, against $0.416$
after 100000 steps. **Early stopping** keeps the weights from the step with the best validation error. It costs nothing
extra (you were going to train anyway), and it is used for almost every neural network ([Chapter
16](16-Training-Deep-Networks.md)).

Why is stopping early like a penalty? Notice the weight norm in the output: $0.35, 1.00, 1.93, 2.70, 3.39, 4.07$. Starting
from zero, gradient descent grows the weights gradually, and the number of steps limits how large they can get. For
least squares the link to ridge is exact, through the SVD.

**Theorem 8.3.** Gradient descent $w_{t+1}=w_t+\alpha X^\top(y-Xw_t)$ from $w_0=0$ on $\tfrac12\lVert y-Xw\rVert^2$ gives, after
$t$ steps,

$$w_t=\sum_j\bigl(1-(1-\alpha d_j^2)^t\bigr)\frac{u_j^\top y}{d_j}\,v_j.$$

*Proof.* Write $w_t=\sum_jc_{t,j}v_j$. Using $X^\top y=\sum_jd_j(u_j^\top y)v_j$ and $X^\top Xv_j=d_j^2v_j$, the update in
each direction is $c_{t+1,j}=(1-\alpha d_j^2)c_{t,j}+\alpha d_j(u_j^\top y)$, with $c_{0,j}=0$. The fixed point is
$c^*_j=u_j^\top y/d_j$ (least squares), and $c_{t+1,j}-c^*_j=(1-\alpha d_j^2)(c_{t,j}-c^*_j)$, so
$c_{t,j}-c^*_j=-(1-\alpha d_j^2)^tc^*_j$. $\square$

Compare ridge's shrink factor $d_j^2/(d_j^2+\lambda)$ with gradient descent's $1-(1-\alpha d_j^2)^t$. Both are near 1 for
large $d_j$ and near 0 for small $d_j$. For small $\alpha d_j^2$, $(1-\alpha d_j^2)^t\approx e^{-\alpha d_j^2t}$, and the two
filters have the same shape with $\lambda\approx1/(\alpha t)$: **running $t$ steps is roughly ridge with
$\lambda=1/(\alpha t)$**. Directions with strong signal are learned first; noisy, low-variance directions are learned
last, and stopping early leaves them out. (This is a standard observation; see for example Goodfellow, Bengio and
Courville, section 7.8, and Yao, Rosasco and Caponnetto 2007 for a theory.)

### Data augmentation

Another way to tell a model "small changes to the input should not change the output" is to show it such changes.
**Data augmentation** adds modified copies of the training examples: shifted, flipped or slightly rotated images,
re-recorded sounds, or simply inputs with a little noise. Block 5 copies each of the 20 training points 200 times with
its input jittered by noise of standard deviation $0.1$ and fits the unpenalised degree-12 polynomial by least squares
to the 4000 copies. The test error falls from $0.777$ to $0.138$. Bishop (1995) showed that training with small input
noise is, to first order in the noise variance, equivalent to adding a penalty on the derivatives of the fitted function
(Tikhonov regularisation), so the jitter punishes steep wiggles. For images, augmentation that encodes real invariances
(a cat is still a cat when shifted) is one of the most effective regularisers known ([Chapter
17](17-Convolutional-Networks.md)).

### Validation curves and model selection

All these methods have a knob: $\lambda$, the number of steps, the amount of augmentation, the degree. A **validation
curve** plots training and validation error against the knob. Block 3 does it for degree 12 with a ridge penalty.

| $\lambda$ | 0 | $10^{-6}$ | $10^{-4}$ | $10^{-3}$ | $10^{-2}$ | $10^{-1}$ | 1 | 10 |
|---|---|---|---|---|---|---|---|---|
| train | 0.011 | 0.012 | 0.020 | 0.021 | 0.028 | 0.054 | 0.124 | 0.288 |
| validation | 0.176 | 0.175 | 0.181 | 0.172 | 0.141 | **0.126** | 0.233 | 0.578 |
| test | 0.777 | 0.205 | 0.400 | 0.357 | 0.196 | 0.124 | 0.238 | 0.461 |

Reading from right to left: large $\lambda$ underfits (both errors high), small $\lambda$ overfits (training error
tiny, validation higher). The validation minimum at $\lambda=0.1$ also gives the best test error, $0.124$, near the noise
floor. Notice that the validation errors are noisy too (only 15 validation points), and between $10^{-6}$ and $10^{-2}$
they do not track the test error well. This is why, with small data, $k$-fold CV is preferred over a single validation
split, and why the "one standard error rule" (Hastie, Tibshirani and Friedman, section 7.10) picks the *simplest* model
whose CV error is within one standard error of the best, rather than the exact minimum. Search $\lambda$ on a
logarithmic grid: its effect depends on its order of magnitude.

The general recipe for **model selection**: fix a family of models indexed by a complexity knob; estimate each one's
test error by validation or cross-validation; pick the best (or the simplest nearly-best); refit on all the training
data; and evaluate once on a test set that played no part. Chapter 7.5 explained why the last step cannot be skipped.

## 8.6 Effective degrees of freedom and the elastic net

*Level: advanced.*

How complex is a ridge model with 20 weights and $\lambda=100$? Not "20 parameters": its weights are heavily constrained.
We need a measure of complexity that works for penalised and other non-standard fits.

### Degrees of freedom as sensitivity

Fix the inputs $x_1,\dots,x_n$ and let $y_i=f(x_i)+\varepsilon_i$ with noise variance $\sigma^2$. For any fitting
procedure producing $\hat y_i$, define the **effective degrees of freedom**

$$\mathrm{df}=\frac1{\sigma^2}\sum_{i=1}^n\operatorname{Cov}(\hat y_i,y_i).$$

It measures how strongly each fitted value follows its own observation. A procedure that ignores the data (predict 0)
has $\mathrm{df}=0$; one that interpolates ($\hat y_i=y_i$) has $\mathrm{df}=n$. This definition is due to Efron (1986);
see also Ye (1998).

Why this definition? Because it is exactly what makes training error optimistic.

**Theorem 8.4 (optimism).** Let $y_i^{\text{new}}$ be a fresh observation at the same $x_i$ with independent noise. Then

$$\mathbb E\Bigl[\frac1n\sum_i(y_i^{\text{new}}-\hat y_i)^2\Bigr]-\mathbb E\Bigl[\frac1n\sum_i(y_i-\hat y_i)^2\Bigr]=\frac{2\sigma^2}{n}\,\mathrm{df}.$$

*Proof.* Fix $i$ and write $f_i=f(x_i)$. For the new observation, the noise is independent of $\hat y_i$, so
$\mathbb E[(y_i^{\text{new}}-\hat y_i)^2]=\sigma^2+\mathbb E[(f_i-\hat y_i)^2]$. For the training observation,
$\mathbb E[(y_i-\hat y_i)^2]=\mathbb E[(y_i-f_i)^2]+\mathbb E[(f_i-\hat y_i)^2]+2\,\mathbb E[(y_i-f_i)(f_i-\hat y_i)]$, and the last
expectation is $-\operatorname{Cov}(y_i,\hat y_i)$, since $y_i-f_i=\varepsilon_i$ has mean zero and $f_i$ is a constant. The
difference of the two is $2\operatorname{Cov}(y_i,\hat y_i)$. Average over $i$. $\square$

So the training error underestimates the error at the same inputs by $2\sigma^2\mathrm{df}/n$. Adding this correction to
the training error gives **Mallows' $C_p$** (Mallows 1973), and the same reasoning under a likelihood gives Akaike's
**AIC** (Akaike 1974): both are ways of estimating test error from training error plus a complexity charge.

**Linear smoothers.** If $\hat y=Hy$ for a matrix $H$ that does not depend on $y$, then
$\operatorname{Cov}(\hat y_i,y_i)=\sigma^2H_{ii}$ and $\mathrm{df}=\operatorname{trace}(H)$. For least squares, $H$ is the
projection onto a $p$-dimensional space, so $\mathrm{df}=p$: the usual count. For ridge,
$H=X(X^\top X+\lambda I)^{-1}X^\top$, and in the SVD basis

$$\mathrm{df}(\lambda)=\operatorname{trace}(H)=\sum_{j=1}^p\frac{d_j^2}{d_j^2+\lambda},$$

the sum of the shrink factors. It falls smoothly from $p$ at $\lambda=0$ towards 0. Block 6 checks this against the
covariance definition by simulating 2000 noise draws: $19.27$ against $19.29$ at $\lambda=1$, $15.27$ against $15.28$ at
$\lambda=10$, and $6.05$ against $6.06$ at $\lambda=100$. So ridge with $\lambda=100$ has about as much freedom as an
unpenalised model with 6 weights.

**The lasso.** The lasso is not a linear smoother (which features are selected depends on $y$), but Zou, Hastie and
Tibshirani (2007) proved, using Stein's lemma, that the number of nonzero weights is an unbiased estimate of its
degrees of freedom. That is a striking result: the selection step, which one might expect to cost extra freedom, is
exactly paid for by the shrinkage of the selected weights. The simulation, with 400 draws (each lasso fit is a loop in
Python), gives average nonzeros $3.45$ against a covariance estimate of $3.31$ at $\lambda=0.5$, and $10.24$ against
$10.00$ at $\lambda=0.1$, in agreement up to the Monte Carlo error of a few hundred draws.

### The elastic net

Block 7 shows the lasso's weakness with correlated features. Two features are almost copies of each other
(correlation $0.9999$) and the signal is $2z$, where $z$ is their common part. The lasso gives $(1.86,0.26)$: it puts
nearly all the weight on one copy, and which one depends on tiny differences in the noise. Ridge splits it evenly,
$(1.057,1.058)$, because for a fixed sum $w_1+w_2$ the sum of squares is smallest when they are equal; but ridge selects
nothing.

Zou and Hastie (2005) combined the two penalties in the **elastic net**:

$$J(w)=\frac1{2n}\lVert y-Xw\rVert^2+\lambda\Bigl(\alpha\lVert w\rVert_1+\frac{1-\alpha}2\lVert w\rVert^2\Bigr),\qquad0\le\alpha\le1.$$

With $\alpha=1$ it is the lasso, with $\alpha=0$ ridge. The squared part makes the objective strictly convex, so the
solution is unique, and it gives the **grouping effect**: highly correlated features get nearly equal weights (Zou and
Hastie proved a bound on $|w_i-w_j|$ in terms of the correlation). The L1 part still produces exact zeros. Coordinate
descent needs only a change of denominator: the one-weight problem becomes
$\frac{c_j}2w_j^2-\rho_jw_j+\lambda\alpha|w_j|+\frac{\lambda(1-\alpha)}2w_j^2$, so

$$w_j\leftarrow\frac{S(\rho_j,\lambda\alpha)}{c_j+\lambda(1-\alpha)},$$

which is the single line `w[j] = soft(rho, lam * alpha) / (col[j] + lam * (1 - alpha))` in the program. With
$\alpha=0.5$ the elastic net gives $(1.059,1.062)$ for the twins and an exact zero for the third feature. It is the
default penalty in much applied work with many correlated features, such as genomics.

**In practice.** scikit-learn has `Ridge`, `Lasso`, `ElasticNet`, `LassoCV` and `lasso_path` (coordinate descent, as here),
and `validation_curve`; the R package glmnet, by the authors of the coordinate-descent method, is the reference
implementation. In deep learning, the L2 penalty is called **weight decay** (Chapter 5.5 discussed its interaction with
Adam), and dropout, early stopping and augmentation are the main regularisers ([Chapter 16](16-Training-Deep-Networks.md)).

## Check yourself

??? question "1. A model has training MSE 0.01 and test MSE 2.5; another has 0.9 and 1.0. The noise variance is about 0.8. Which is overfitting, which is underfitting, and what would you try next for each?"

    The first fits the training data far below the noise floor and does badly on new data: overfitting (high variance).
    Try a penalty, fewer features, more data, or early stopping. The second has training and test error close together and
    near the noise floor: it is not overfitting, and is probably near the best achievable; if the noise estimate were much
    lower, it would be underfitting (high bias), and you would add features or flexibility.

??? question "2. Show that the cross term $2\,\mathbb E[(f-\bar f)(\bar f-\hat f)]$ in Theorem 8.1 vanishes, and explain why the argument fails if $\bar f$ is replaced by some other fixed function."

    $f-\bar f$ is a constant (at fixed $x$), so the term is $2(f-\bar f)\,\mathbb E[\bar f-\hat f]=2(f-\bar f)(\bar f-\bar f)=0$.
    With any other constant $g$ in place of $\bar f$, $\mathbb E[g-\hat f]=g-\bar f\ne0$ and the cross term survives; the
    decomposition is clean only around the mean prediction.

??? question "3. For one weight with $s=\sum x_i^2=10$, $\sigma^2=1$ and true $w=0.5$, compute the MSE of least squares and of ridge at the best $\lambda$."

    Least squares: variance $\sigma^2/s=0.1$, no bias, MSE $0.1$. Best $\lambda^*=\sigma^2/w^2=4$. Ridge MSE
    $=(16\cdot0.25+10)/14^2=14/196\approx0.0714$, about 29 percent lower. The weight is small compared with the noise, so
    shrinking pays.

??? question "4. Compute $S(z,\lambda)$ for $z\in\{3,0.5,-0.5,-3\}$ and $\lambda=1$, and the corresponding ridge values $z/(1+\lambda)$."

    Soft thresholding: $2, 0, 0, -2$. Ridge: $1.5, 0.25, -0.25, -1.5$. The lasso removes a fixed amount and zeroes small
    values; ridge removes a fixed fraction and zeroes nothing.

??? question "5. Show that all lasso weights are zero when $\lambda\ge\max_j|x_j^\top y|/n$ (with the $\frac1{2n}$ convention)."

    At $w=0$ the partial residual for every $j$ is $y$ itself, so $\rho_j=x_j^\top y/n$. The coordinate update gives
    $S(\rho_j,\lambda)/c_j=0$ whenever $|\rho_j|\le\lambda$. If this holds for every $j$, then $w=0$ is a fixed point of
    coordinate descent, and since each coordinate is optimal given the others and the problem is convex with a separable
    non-smooth part, it is the global minimum. (Equivalently: 0 is in the subdifferential at $w=0$.)

??? question "6. Write the code: the ridge solution for $X$ with more columns than rows ($p>n$) using the identity $(X^\top X+\lambda I)^{-1}X^\top=X^\top(XX^\top+\lambda I)^{-1}$. Why is it faster when $p\gg n$?"

    ```python
    import numpy as np
    rng = np.random.default_rng(0)
    n, p, lam = 30, 2000, 1.0
    X, y = rng.normal(size=(n, p)), rng.normal(size=n)
    w_primal = np.linalg.solve(X.T @ X + lam * np.eye(p), X.T @ y)   # a 2000 x 2000 system
    w_dual = X.T @ np.linalg.solve(X @ X.T + lam * np.eye(n), y)     # a 30 x 30 system
    print(np.abs(w_primal - w_dual).max())                            # about 5e-15
    ```

    The identity follows from $X^\top(XX^\top+\lambda I)=(X^\top X+\lambda I)X^\top$, multiplying on the left and right by
    the inverses. The dual form solves an $n\times n$ system, $O(n^3+n^2p)$ work, instead of $p\times p$, $O(p^3)$. It is
    also the starting point of kernel ridge regression ([Chapter 9](09-Nearest-Neighbours-and-Kernels.md)), where only the
    inner products $XX^\top$ are needed.

??? question "7. Using Theorem 8.3, how many gradient steps with $\alpha=0.01$ correspond roughly to ridge with $\lambda=0.5$? For a direction with $d_j^2=0.1$, compare the two shrink factors."

    $t\approx1/(\alpha\lambda)=1/0.005=200$ steps. Ridge: $0.1/(0.1+0.5)=0.167$. Gradient descent: $1-(1-0.001)^{200}=1-0.999^{200}\approx1-0.8187=0.181$.
    Close, as the approximation predicts for small $\alpha d_j^2$.

??? question "8. Write the code: the bias-variance decomposition for $k$-nearest-neighbour regression on the chapter's sine data, for $k=1$, 5 and 15. Which $k$ has the most bias and which the most variance?"

    ```python
    import numpy as np
    truth = lambda x: np.sin(np.pi * x)
    grid = np.linspace(-0.95, 0.95, 100)
    r = np.random.default_rng(0)
    for k in (1, 5, 15):
        preds = []
        for s in range(2000):
            x = r.uniform(-1, 1, 20); y = truth(x) + r.normal(0, 0.3, 20)
            idx = np.argsort(np.abs(grid[:, None] - x[None, :]), axis=1)[:, :k]
            preds.append(y[idx].mean(1))
        P = np.array(preds)
        print(k, np.mean((P.mean(0) - truth(grid)) ** 2), np.mean(P.var(0)))
    ```

    It prints bias$^2$ $0.0010$, $0.023$ and $0.296$ and variance $0.110$, $0.041$ and $0.050$ for $k=1, 5, 15$. With
    $k=1$ the prediction is one noisy neighbour (variance a little above $\sigma^2=0.09$, since which point is nearest also
    jumps around); $k=5$ averages the noise away at a small cost in bias; with $k=15$ out of 20 the average reaches far
    away and flattens the sine, so bias dominates (and the variance stops falling, because which 15 points are used near
    the ends changes a lot between training sets). Here $k$ plays the role of $1/\text{complexity}$, and $k=5$ has the
    smallest total, $0.064$, against $0.111$ and $0.346$.

??? question "9. Ridge's degrees of freedom are $\sum_jd_j^2/(d_j^2+\lambda)$. If $X$ has orthonormal columns and $p=10$, which $\lambda$ gives $\mathrm{df}=5$?"

    All $d_j=1$, so $\mathrm{df}=10/(1+\lambda)=5$ gives $\lambda=1$.

??? question "10. Why must the features be standardised before ridge or lasso, but not before least squares?"

    Least squares is **equivariant** to rescaling a feature: multiply column $j$ by $c$ and the fitted weight is divided by
    $c$, with identical predictions. A penalty on $w_j$ breaks this: after multiplying the feature by $c$, the same
    prediction needs a weight $c$ times smaller, which the penalty charges $c^2$ (ridge) or $c$ (lasso) times less. So the
    fit would depend on the units. Standardising puts all features on the same footing, so the penalty means "prefer small
    effects per standard deviation of the feature".

??? question "11. (Advanced) Prove that for a linear smoother $\hat y=Hy$ with fixed $H$, $\mathrm{df}=\operatorname{trace}(H)$, and that $\mathrm{df}=p$ for least squares with a full-rank $n\times p$ design."

    $\operatorname{Cov}(\hat y_i,y_i)=\operatorname{Cov}(\sum_kH_{ik}y_k,y_i)=\sum_kH_{ik}\operatorname{Cov}(y_k,y_i)=H_{ii}\sigma^2$, since
    the $y_k$ are independent with variance $\sigma^2$. Summing and dividing by $\sigma^2$ gives the trace. For least squares
    $H=X(X^\top X)^{-1}X^\top$ and, by the cyclic property of the trace,
    $\operatorname{trace}(H)=\operatorname{trace}((X^\top X)^{-1}X^\top X)=\operatorname{trace}(I_p)=p$.

## What you learned

- Training error always falls as a model family grows; test error falls and then rises. Underfitting is too little
  flexibility, overfitting is fitting the noise.
- Expected squared test error is noise plus bias squared plus variance (proved, and checked by simulation to three or
  four digits); flexibility trades bias for variance.
- Ridge regression $(X^\top X+\lambda I)^{-1}X^\top y$ always has a unique solution, shrinks each singular direction by
  $d_j^2/(d_j^2+\lambda)$, beats least squares for some $\lambda>0$ (proved for one weight), and is the posterior mean under
  a Gaussian prior with $\lambda=\sigma^2/\tau^2$.
- The lasso's L1 penalty gives exact zeros through soft thresholding and the corners of the L1 ball; coordinate descent
  solves it with one-line updates, and its path shows features entering one by one.
- Early stopping is approximately ridge with $\lambda\approx1/(\alpha t)$ (derived); noise augmentation acts like a
  smoothness penalty; validation curves choose the knob.
- Effective degrees of freedom, $\frac1{\sigma^2}\sum\operatorname{Cov}(\hat y_i,y_i)$, measure complexity and exactly give the
  optimism of training error (proved); ridge has $\sum d_j^2/(d_j^2+\lambda)$, the lasso about its number of nonzeros. The
  elastic net combines L1 and L2 to select groups of correlated features.

**Next:** [Chapter 9](09-Nearest-Neighbours-and-Kernels.md) returns to nearest neighbours, meets the curse of
dimensionality, and turns ridge regression into kernel ridge regression.

## Further reading

- T. Hastie, R. Tibshirani and J. Friedman, *The Elements of Statistical Learning*, 2nd ed., 2009: chapters 3.4
  (ridge, lasso, elastic net), 7 (bias, variance, degrees of freedom, $C_p$, AIC) and 18 (high-dimensional problems).
- T. Hastie, R. Tibshirani and M. Wainwright, *Statistical Learning with Sparsity: The Lasso and Generalizations*,
  2015.
- C. M. Bishop, *Pattern Recognition and Machine Learning*, 2006: sections 1.1, 3.1.4 and 3.2 (regularised least
  squares, the bias-variance decomposition).
- I. Goodfellow, Y. Bengio and A. Courville, *Deep Learning*, 2016: chapter 7 (regularisation, including early stopping
  as L2).
- A. E. Hoerl and R. W. Kennard, "Ridge Regression: Biased Estimation for Nonorthogonal Problems", *Technometrics*
  12(1), 1970.
- R. Tibshirani, "Regression Shrinkage and Selection via the Lasso", *Journal of the Royal Statistical Society B*
  58(1), 1996.
- H. Zou and T. Hastie, "Regularization and Variable Selection via the Elastic Net", *Journal of the Royal Statistical
  Society B* 67(2), 2005.
- J. Friedman, T. Hastie and R. Tibshirani, "Regularization Paths for Generalized Linear Models via Coordinate
  Descent", *Journal of Statistical Software* 33(1), 2010.
- P. Tseng, "Convergence of a Block Coordinate Descent Method for Nondifferentiable Minimization", *Journal of
  Optimization Theory and Applications* 109(3), 2001.
- H. Zou, T. Hastie and R. Tibshirani, "On the 'Degrees of Freedom' of the Lasso", *Annals of Statistics* 35(5), 2007.
- B. Efron, "How Biased is the Apparent Error Rate of a Prediction Rule?", *Journal of the American Statistical
  Association* 81(394), 1986; C. L. Mallows, "Some Comments on Cp", *Technometrics* 15(4), 1973.
- S. Geman, E. Bienenstock and R. Doursat, "Neural Networks and the Bias/Variance Dilemma", *Neural Computation* 4(1),
  1992.
- C. M. Bishop, "Training with Noise is Equivalent to Tikhonov Regularization", *Neural Computation* 7(1), 1995.
- M. Belkin, D. Hsu, S. Ma and S. Mandal, "Reconciling modern machine-learning practice and the classical bias-variance
  trade-off", *PNAS* 116(32), 2019.
- On this site: [Chapter 4](04-Linear-Regression.md) (least squares and the SVD), [Chapter 7](07-Evaluating-Models.md)
  (cross-validation), [Chapter 12](12-Probabilistic-Models.md) (Bayesian linear regression),
  [Chapter 21](21-Learning-Theory.md) (why generalisation works, double descent), and the
  [linear algebra book](https://math.akadian.ca/books/linear-algebra/).
