# 14. Dimensionality reduction

*A data set with 500 features is a cloud of points in 500-dimensional space, and nobody can look at that. Yet the
cloud is rarely as complicated as its number of features: pixels of a face move together, the channels of a
spectrometer are strongly correlated, and the heights and weights of people are not independent. Can we find a few
new coordinates that keep almost everything that matters? This chapter builds principal component analysis (PCA)
from first principles, derives it twice (as the directions of largest variance and as the best compression) and
computes it with the SVD. Then it gives PCA a probability model, meets factor analysis, goes beyond straight lines
with MDS, Isomap, t-SNE and UMAP, shows how their pictures mislead, and ends with a first look at autoencoders.*

!!! abstract "In this chapter"
    **You will learn:**

    - why reducing dimension helps: to see data, to compress it, to remove noise, and to make later models work
    - PCA derived as the directions of maximum variance, and proved to be the best linear compression
    - PCA computed with the SVD, and why that is better than forming the covariance matrix
    - how to choose the number of components from explained variance and from a likelihood
    - probabilistic PCA and factor analysis, and when they disagree with PCA
    - classical MDS, Isomap, t-SNE and UMAP, and the honest rules for reading their plots
    - why a linear autoencoder learns exactly the PCA subspace, and what a non-linear one adds

    **You need:** [Chapter 3](03-The-Math-Toolkit.md) (matrices, eigenvectors, the SVD, Gaussians),
    [Chapter 4](04-Linear-Regression.md) (least squares, conditioning), [Chapter 13](13-Clustering.md) (EM, the
    graph Laplacian). The linear algebra book at [https://math.akadian.ca/books/](https://math.akadian.ca/books/)
    has more on eigenvalues and the SVD.

    **Levels:** 14.1 is beginner; 14.2 and 14.3 are intermediate; 14.4 is advanced; 14.5 is intermediate to
    advanced; 14.6 is intermediate.

## 14.1 Why fewer dimensions: seeing, compressing, denoising

Suppose you measure 300 objects with 10 instruments each. Each object becomes a point in 10-dimensional space. You
suspect that only a few underlying causes produce all ten readings: perhaps the temperature, the size and the
composition of each object. If that is right, the 300 points do not fill the 10-dimensional space. They lie close
to a 3-dimensional flat sheet inside it, plus a little measurement noise. **Dimensionality reduction** means finding
that sheet and describing every point by its position on it: 3 numbers instead of 10.

The new coordinates are sometimes called **components**, **latent variables** (hidden variables that explain the
data) or an **embedding** (a placement of the data in a smaller space). There are four reasons to want them.

1. **Seeing.** Our eyes understand two or three dimensions. A good 2-D picture of high-dimensional data shows
   clusters, outliers, trends and mistakes in the data that no table of numbers would reveal.
2. **Compressing.** Storing 3 numbers per object instead of 10 saves space and time. With images, audio and
   spectra the savings are much larger: hundreds of strongly correlated values reduce to a few dozen.
3. **Denoising.** If the signal lives on a low-dimensional sheet and the noise points in all directions equally,
   then projecting onto the sheet keeps the whole signal and throws away most of the noise. We will measure this.
4. **Helping other models.** Many methods suffer in high dimension ([Chapter 9](09-Nearest-Neighbours-and-Kernels.md)
   showed the curse of dimensionality for nearest neighbours). Fewer, cleaner features mean faster training, less
   overfitting and distances that mean something again, for example before clustering ([Chapter 13](13-Clustering.md)).

The belief behind all this has a name, the **manifold hypothesis**: real high-dimensional data, such as photographs,
tends to lie near a much lower-dimensional surface (a **manifold**, a space that looks flat when you zoom in close
enough, like the surface of the Earth). It is a hypothesis, supported by experience rather than proved, and it is
the reason dimensionality reduction works as often as it does. The number of coordinates needed to describe the
surface is the data's **intrinsic dimension**.

There are two families of method. **Linear** methods find a flat subspace and project onto it; PCA, probabilistic
PCA and factor analysis are linear (14.2 to 14.4). **Non-linear** methods can follow curved surfaces; MDS with
geodesic distances (Isomap), t-SNE, UMAP and autoencoders are non-linear (14.5 and 14.6). Linear methods are
simpler, faster, exactly solvable and easy to interpret. Non-linear methods make better pictures of curved
structure, at the price of parameters to tune and pictures that are easy to misread.

A real instance: the CRISM spectrometer on the Mars Reconnaissance Orbiter records hundreds of wavelength channels
for every pixel of the ground, and neighbouring channels are strongly correlated. Reducing such data to a handful of
components is a standard first step in analysing it, before anyone looks for minerals.

## 14.2 Principal component analysis: maximum variance and the SVD

### The question

We have $n$ data points $x_1, \dots, x_n$ in $\mathbb{R}^p$, stacked as the rows of an $n \times p$ matrix $X$.
We want a direction (a unit vector $w$, $\|w\| = 1$) such that projecting the data onto it keeps as much as
possible. The projection of $x_i$ onto the line through the mean $\bar{x}$ in direction $w$ is described by one
number, its **score** $z_i = w^\top (x_i - \bar{x})$. What does "keep as much as possible" mean? Karl Pearson,
in "On Lines and Planes of Closest Fit to Systems of Points in Space" (1901), asked for the line that passes closest
to the points. Harold Hotelling, in 1933, asked for the direction along which the scores vary the most, and named
the result **principal components**. We will see that the two questions have the same answer.

### Maximum variance

First **centre** the data: subtract the mean $\bar{x} = \frac1n \sum_i x_i$ from every row, so that from now on the
data has mean zero. Write $X$ for the centred matrix. The **covariance matrix** is the $p \times p$ matrix

$$
S = \frac{1}{n} X^\top X = \frac{1}{n}\sum_{i=1}^{n} x_i x_i^\top .
$$

Its entry $S_{ab}$ is the covariance between features $a$ and $b$; its diagonal holds the variances. (Statisticians
often divide by $n - 1$ instead of $n$ to get an unbiased estimate; it rescales every variance by the same factor
and changes none of the directions.) The scores on direction $w$ have mean zero, and their variance is

$$
\frac1n \sum_i z_i^2 = \frac1n \sum_i (w^\top x_i)^2 = w^\top \Big(\frac1n \sum_i x_i x_i^\top\Big) w = w^\top S w .
$$

So the first principal direction solves: maximise $w^\top S w$ subject to $w^\top w = 1$. (Without the constraint,
making $w$ longer would make the variance as large as we like.)

**Solution.** Use a Lagrange multiplier $\lambda$ for the constraint. At the maximum, the gradient of the objective
is parallel to the gradient of the constraint:

$$
\nabla_w \big(w^\top S w - \lambda (w^\top w - 1)\big) = 2 S w - 2\lambda w = 0
\quad\Longrightarrow\quad S w = \lambda w .
$$

So $w$ must be an **eigenvector** of $S$, and then the variance is $w^\top S w = \lambda w^\top w = \lambda$, its
**eigenvalue**. To make the variance as large as possible, choose the eigenvector with the **largest eigenvalue**.

Facts from linear algebra make this solid. $S$ is symmetric, so by the **spectral theorem** it has $p$ real
eigenvalues $\lambda_1 \ge \lambda_2 \ge \dots \ge \lambda_p$ and an orthonormal basis of eigenvectors
$v_1, \dots, v_p$: $S = \sum_j \lambda_j v_j v_j^\top$. $S$ is also **positive semidefinite**,
$w^\top S w = \frac1n\sum_i (w^\top x_i)^2 \ge 0$, so every $\lambda_j \ge 0$. The eigenvalues are the variances of the
data along the eigenvector directions, and they add up to the total variance:
$\sum_j \lambda_j = \mathrm{tr}(S) = \sum_a S_{aa}$.

### More than one component

The second principal direction should capture the most variance that the first one missed, so we ask for the
direction of largest variance among those perpendicular to $v_1$, and so on. Equivalently, we want $k$ orthonormal
directions, the columns of a $p \times k$ matrix $W$ with $W^\top W = I$, that together keep the most variance,
$\mathrm{tr}(W^\top S W) = \sum_{m=1}^{k} w_m^\top S w_m$.

**Theorem.** Over all $p \times k$ matrices $W$ with orthonormal columns,
$\mathrm{tr}(W^\top S W) \le \lambda_1 + \dots + \lambda_k$, with equality when the columns of $W$ are
$v_1, \dots, v_k$.

*Proof.* Expand $S$ in its eigenvectors:
$\mathrm{tr}(W^\top S W) = \sum_j \lambda_j \,\mathrm{tr}(W^\top v_j v_j^\top W) = \sum_j \lambda_j c_j$, where
$c_j = \|W^\top v_j\|^2$. Two facts about the numbers $c_j$:

- $0 \le c_j \le 1$, because $W W^\top$ is the orthogonal projection onto the column space of $W$, and projecting a
  unit vector cannot make it longer: $c_j = v_j^\top W W^\top v_j = \|W W^\top v_j\|^2 \le 1$.
- $\sum_j c_j = k$, because $\sum_j \|W^\top v_j\|^2 = \|W^\top\|_F^2$ (the $v_j$ form an orthonormal basis) and
  $\|W\|_F^2 = k$ (the $k$ columns have length 1).

So we are distributing a total weight $k$ over the eigenvalues, at most 1 on each. The largest possible sum puts
weight 1 on each of the $k$ largest eigenvalues, giving $\lambda_1 + \dots + \lambda_k$. Choosing $W = (v_1, \dots, v_k)$
gives $c_1 = \dots = c_k = 1$ and the rest 0, so the bound is reached. $\square$

The scores of point $i$ on the first $k$ components are $z_i = W^\top x_i \in \mathbb{R}^k$; for all points at once,
$Z = XW$, an $n \times k$ matrix. These are the new coordinates.

### The same answer: best compression

Pearson's question was different: which $k$-dimensional flat subspace passes closest to the points? With orthonormal
columns $W$, the closest point of the subspace to $x$ is its projection $WW^\top x$, and the **reconstruction
error** is $\|x - WW^\top x\|^2$. By Pythagoras (the projection and the remainder are perpendicular),

$$
\|x - WW^\top x\|^2 = \|x\|^2 - \|W^\top x\|^2 .
$$

Average over the data: the mean reconstruction error is $\mathrm{tr}(S) - \mathrm{tr}(W^\top S W)$. The first term
does not depend on $W$, so **minimising the reconstruction error is the same as maximising the kept variance.** By
the theorem, the best subspace is spanned by the top $k$ eigenvectors, and the smallest possible mean
reconstruction error is exactly the **sum of the discarded eigenvalues**, $\lambda_{k+1} + \dots + \lambda_p$.

This is a strong statement. Among all ways of compressing $p$ numbers to $k$ by a linear projection and
decompressing by a linear map, none beats PCA in mean squared error. (The general version, for any rank-$k$
approximation of a matrix and not only projections, is the **Eckart-Young theorem**, 1936: the best rank-$k$
approximation of $X$ in the sum of squared entries is the truncated SVD, below.)

### A hand example

Five points in the plane: $(-2,-1), (-1,-1), (0,0), (1,1), (2,1)$. Their mean is $(0,0)$, so they are already
centred. The covariance entries are
$S_{11} = (4+1+0+1+4)/5 = 2$, $S_{22} = (1+1+0+1+1)/5 = 0.8$ and $S_{12} = (2+1+0+1+2)/5 = 1.2$:

$$
S = \begin{pmatrix} 2 & 1.2 \\ 1.2 & 0.8 \end{pmatrix}.
$$

The eigenvalues solve $\lambda^2 - \mathrm{tr}(S)\lambda + \det S = 0$, that is $\lambda^2 - 2.8\lambda + 0.16 = 0$, so
$\lambda = (2.8 \pm \sqrt{7.2})/2$: $\lambda_1 \approx 2.7416$ and $\lambda_2 \approx 0.0584$. For $\lambda_1$, the
first row of $(S - \lambda_1 I)w = 0$ gives $-0.7416\,w_1 + 1.2\,w_2 = 0$, so $w \propto (1.2, 0.7416)$, which has
length $1.4107$; normalised, $v_1 \approx (0.8507, 0.5257)$. The scores are the dot products with $v_1$: for
$(1,1)$, $0.8507 + 0.5257 = 1.3764$; for $(2,1)$, $1.7013 + 0.5257 = 2.2270$. The first component holds
$2.7416 / 2.8 \approx 97.9\%$ of the variance: these five points are almost a line.

<figure class="mars-fig" markdown="0">
<svg viewBox="0 0 640 220" role="img" aria-label="Five points in the plane with the first principal direction drawn as a long line through them and the second as a short perpendicular line. Dashed segments drop from four points onto the first direction, showing their projections. The variance is 2.742 along the first direction and 0.058 along the second.">
  <line x1="187.3" y1="192" x2="452.7" y2="28" stroke="#eea66f" stroke-width="2.5"/>
  <line x1="294.8" y1="69.2" x2="345.2" y2="150.8" stroke="#9cc9ea" stroke-width="2.5"/>
  <g stroke="currentColor" stroke-width="1" stroke-dasharray="3 3">
    <line x1="200" y1="170" x2="206.3" y2="180.2"/>
    <line x1="260" y1="170" x2="249.7" y2="153.4"/>
    <line x1="380" y1="50" x2="390.3" y2="66.6"/>
    <line x1="440" y1="50" x2="433.7" y2="39.8"/>
  </g>
  <g stroke="currentColor" stroke-width="0.8" fill="#7ccf9a">
    <circle cx="200" cy="170" r="6"/>
    <circle cx="260" cy="170" r="6"/>
    <circle cx="320" cy="110" r="6"/>
    <circle cx="380" cy="50" r="6"/>
    <circle cx="440" cy="50" r="6"/>
  </g>
  <g fill="currentColor" font-size="13">
    <text x="458" y="32">PC1</text>
    <text x="262" y="66">PC2</text>
    <text x="490" y="110">variance along PC1: 2.742</text>
    <text x="490" y="130">variance along PC2: 0.058</text>
    <text x="490" y="150">PC1 keeps 97.9%</text>
  </g>
</svg>
<figcaption>The five points of the hand example. The first principal direction (orange) is the line of closest fit;
the dashed segments are the reconstruction errors when each point is replaced by its projection. The second
direction (blue) is perpendicular and carries almost no variance.</figcaption>
</figure>

### Computing PCA with the SVD

The **singular value decomposition** ([Chapter 3](03-The-Math-Toolkit.md)) writes any $n \times p$ matrix as
$X = U \Sigma V^\top$, where $U$ ($n \times r$) and $V$ ($p \times r$) have orthonormal columns and $\Sigma$ is
diagonal with **singular values** $s_1 \ge s_2 \ge \dots \ge 0$. Plug it into the covariance:

$$
S = \frac1n X^\top X = \frac1n V \Sigma U^\top U \Sigma V^\top = V \Big(\frac{\Sigma^2}{n}\Big) V^\top .
$$

That is an eigen-decomposition of $S$. So **the right singular vectors of the centred data are the principal
directions, and the eigenvalues are $\lambda_j = s_j^2 / n$.** The scores come for free:
$Z = XV = U\Sigma V^\top V = U\Sigma$.

Why compute it this way, and not form $S$ and call an eigenvalue routine? Because forming $X^\top X$ **squares the
condition number** ([Chapter 4](04-Linear-Regression.md), section 4.7): a direction with a small singular value
$s$ has eigenvalue $s^2/n$, and in floating point a tiny $s^2$ can vanish entirely next to a large one, while the
SVD works on $X$ itself and keeps it. For the moderate data in this chapter both ways agree to about $10^{-15}$, as
the program shows, but the SVD is the standard choice. When $n$ and $p$ are both huge and only a few components are
wanted, **randomised SVD** (Halko, Martinsson and Tropp 2011) multiplies $X$ by a few random vectors to find the top
subspace quickly.

Cost: a full SVD of an $n \times p$ matrix costs $O(np\min(n,p))$; forming $S$ costs $O(np^2)$ and its eigenvalues
$O(p^3)$.

### The program

The program computes PCA both ways for the hand example and for 300 points in 10 dimensions, made from 3 hidden
factors with standard deviations 3, 2 and 1, mixed by a random orthonormal $10 \times 3$ matrix, plus noise of
standard deviation 0.3 in every coordinate (variance 0.09), plus a constant 5 to make centring necessary.

```python
--8<-- "books/machine-learning/ch14_pca.py"
```

```
1. Hand example: five points in the plane
  covariance [[2.0, 1.2], [1.2, 0.8]]
  eigenvalues [2.7416, 0.0584]  first direction [0.8507, 0.5257]
  scores on PC1 [-2.227, -1.3764, 0.0, 1.3764, 2.227]
  share of variance on PC1: 0.9792

2. 300 points in 10 dimensions made from 3 hidden factors plus noise
  eigenvalues from eig: [8.644, 3.86, 1.039, 0.108, 0.099, 0.095, 0.091, 0.085, 0.073, 0.063]
  eigenvalues from SVD: [8.644, 3.86, 1.039, 0.108, 0.099, 0.095, 0.091, 0.085, 0.073, 0.063]
  same directions (max difference after fixing signs): 1.3e-15
  cumulative explained variance: [0.61, 0.883, 0.956, 0.964, 0.971, 0.978, 0.984, 0.99, 0.996, 1.0]

3. Reconstruction error with k components equals the sum of the discarded eigenvalues
  k = 0: mean squared error  14.1593   sum of discarded eigenvalues  14.1593
  k = 1: mean squared error   5.5151   sum of discarded eigenvalues   5.5151
  k = 2: mean squared error   1.6547   sum of discarded eigenvalues   1.6547
  k = 3: mean squared error   0.6162   sum of discarded eigenvalues   0.6162
  k = 4: mean squared error   0.5080   sum of discarded eigenvalues   0.5080
  k = 5: mean squared error   0.4087   sum of discarded eigenvalues   0.4087

4. Denoising: keep 3 components of a noisy copy and compare with the clean signal
  mean squared error noisy vs clean:    0.0895
  mean squared error denoised vs clean: 0.0280
```

Read the output carefully, because each part checks a claim.

- Part 1 reproduces the hand example.
- Part 2: the eigenvalue and SVD routes give the same numbers and directions. Three eigenvalues (8.64, 3.86, 1.04)
  stand far above the other seven, which are all close to 0.09, the noise variance. The top three are a little
  under $9 + 0.09$, $4 + 0.09$ and $1 + 0.09$, as random sampling allows. The data really is 3-dimensional plus noise.
- Part 3: the mean squared reconstruction error with $k$ components equals the sum of the discarded eigenvalues, to
  every printed digit, as proved.
- Part 4: projecting noisy data onto 3 components cuts the error against the clean signal from 0.0895 to 0.0280.
  Why about a third? The noise has variance 0.09 in each of 10 directions; the projection keeps only its part in
  3 of them, about $0.09 \times 3/10 = 0.027$ per coordinate on average, while keeping nearly all of the signal.

A word on **signs**: if $v$ is an eigenvector, so is $-v$. Different programs may return either, so PCA directions
and scores are defined only up to sign. The helper `fix_signs` picks one convention so that comparisons work.

### Scaling first, or not

PCA chases variance, so it depends on units. If one feature is a length in millimetres and the rest are in metres,
the millimetre feature has a million times more variance and becomes the first component by itself. When features
are measured in different units, standardise each to variance 1 first ([Chapter 2](02-Data-and-Features.md)). This
is PCA of the **correlation matrix** instead of the covariance matrix. When all features share a unit and their
variances mean something (pixels of an image, channels of one spectrometer), leave them unscaled.

<figure class="play" data-play="pca"><span class="ai-tag">AI-created</span><figcaption><b>Try it.</b> Turn the line and watch how much of the spread survives when the points are squashed onto it; the first principal component keeps the most. The points are made up.</figcaption></figure>

## 14.3 How many components: explained variance

How many components should we keep? The eigenvalues answer directly. The **explained variance ratio** of component
$j$ is $\lambda_j / \sum_m \lambda_m$, the fraction of total variance along that direction, and the cumulative
ratio after $k$ components is $(\lambda_1 + \dots + \lambda_k)/\sum_m \lambda_m$. For the 10-dimensional data, the
cumulative ratios are 0.610, 0.883, 0.956, 0.964, ...: three components explain 95.6% of the variance, and each
further one adds less than 1%.

<figure class="mars-fig" markdown="0">
<svg viewBox="0 0 640 240" role="img" aria-label="Bar chart of the ten eigenvalues of the 10-dimensional data: 8.64, 3.86 and 1.04, then seven tiny bars near 0.09. Under the bars, the cumulative explained variance: 61, 88, 96, 96, 97, 98, 98, 99, 100 and 100 percent.">
  <line x1="50" y1="180" x2="560" y2="180" stroke="currentColor" stroke-width="1"/>
  <g stroke="currentColor" stroke-width="0.8">
    <rect x="60" y="59" width="34" height="121" fill="#eea66f"/>
    <rect x="110" y="126" width="34" height="54" fill="#eea66f"/>
    <rect x="160" y="165.5" width="34" height="14.5" fill="#eea66f"/>
    <rect x="210" y="178.5" width="34" height="1.5" fill="#9cc9ea"/>
    <rect x="260" y="178.6" width="34" height="1.4" fill="#9cc9ea"/>
    <rect x="310" y="178.7" width="34" height="1.3" fill="#9cc9ea"/>
    <rect x="360" y="178.7" width="34" height="1.3" fill="#9cc9ea"/>
    <rect x="410" y="178.8" width="34" height="1.2" fill="#9cc9ea"/>
    <rect x="460" y="179" width="34" height="1" fill="#9cc9ea"/>
    <rect x="510" y="179.1" width="34" height="0.9" fill="#9cc9ea"/>
  </g>
  <g fill="currentColor" font-size="12" text-anchor="middle">
    <text x="77" y="52">8.64</text><text x="127" y="119">3.86</text><text x="177" y="158">1.04</text>
    <text x="352" y="168">seven eigenvalues near the noise level 0.09</text>
    <text x="77" y="196">1</text><text x="127" y="196">2</text><text x="177" y="196">3</text>
    <text x="227" y="196">4</text><text x="277" y="196">5</text><text x="327" y="196">6</text>
    <text x="377" y="196">7</text><text x="427" y="196">8</text><text x="477" y="196">9</text>
    <text x="527" y="196">10</text>
    <text x="77" y="220">61%</text><text x="127" y="220">88%</text><text x="177" y="220">96%</text>
    <text x="227" y="220">96%</text><text x="277" y="220">97%</text><text x="327" y="220">98%</text>
    <text x="377" y="220">98%</text><text x="427" y="220">99%</text><text x="477" y="220">100%</text>
    <text x="527" y="220">100%</text>
  </g>
  <g fill="currentColor" font-size="12">
    <text x="568" y="196">component</text>
    <text x="568" y="220">cumulative</text>
  </g>
</svg>
<figcaption>A scree plot of the 10-dimensional data from the program: the eigenvalues in decreasing order, with the
cumulative share of variance underneath. Three components stand out; the rest is a flat floor of noise.</figcaption>
</figure>

A plot of eigenvalues in decreasing order is a **scree plot**, named by Raymond Cattell (1966) after the rubble at
the foot of a cliff: the real components are the cliff and the noise is the scree. Common rules, from crude to
careful:

- **A fixed share.** Keep enough components for, say, 90% or 95% of the variance. Simple and widely used, but the
  threshold is arbitrary, and with much noise a large share may need many noise components.
- **The elbow** of the scree plot, as in [Chapter 13](13-Clustering.md). Here it is clearly after component 3.
- **Kaiser's rule** (1960), for PCA of the correlation matrix: keep components with eigenvalue above 1, the
  variance of a single standardised feature. It is known to keep too many components on many data sets; use it
  only as a rough guide.
- **A likelihood with a penalty.** Probabilistic PCA (14.4) gives PCA a likelihood. Adding a penalty for the
  number of parameters, such as BIC, turns the choice of $k$ into model selection. The next program does this.
- **The downstream task.** If the components feed a classifier, choose $k$ by the classifier's validation score
  ([Chapter 7](07-Evaluating-Models.md)). If they are for a picture, $k$ is 2.

One more caution. Explained variance measures how well the components reconstruct the data, not how useful they
are. A direction with little variance can be exactly the one that separates two classes. PCA is unsupervised: it
never sees labels.

## 14.4 Probabilistic PCA and factor analysis

*Level: advanced.*

### Giving PCA a model

PCA as we derived it is geometry: no probabilities, no likelihood, no way to say how surprising a new point is or
to handle missing values. Michael Tipping and Christopher Bishop ("Probabilistic Principal Component Analysis",
*Journal of the Royal Statistical Society B*, 1999) and, independently, Sam Roweis (1998) wrote down a model whose
maximum-likelihood solution is PCA. It is a **latent variable model**, like the Gaussian mixture of
[Chapter 13](13-Clustering.md), but with a continuous hidden variable:

$$
z \sim \mathcal{N}(0, I_k), \qquad x = W z + \mu + \varepsilon, \qquad \varepsilon \sim \mathcal{N}(0, \sigma^2 I_p).
$$

In words: a hidden point $z$ with $k$ coordinates is drawn from a standard Gaussian; a $p \times k$ matrix $W$
(the **loadings**) maps it into the data space; a mean $\mu$ is added; and every coordinate gets independent
Gaussian noise of the same variance $\sigma^2$. This is **probabilistic PCA** (PPCA).

Since $x$ is a linear function of Gaussians, it is Gaussian. Its mean is $\mu$ and its covariance is

$$
C = \mathrm{Cov}(Wz + \varepsilon) = W\,\mathrm{Cov}(z)\,W^\top + \mathrm{Cov}(\varepsilon) = W W^\top + \sigma^2 I .
$$

So PPCA says: the covariance of the data is a rank-$k$ part (the signal) plus a constant on the diagonal (the
noise). It has far fewer free numbers than a general covariance: $pk + 1$ minus $k(k-1)/2$ (because rotating $z$
by any orthogonal matrix $R$, $W \to WR$, gives the same $C$), against $p(p+1)/2$ for a full covariance.

### The maximum-likelihood solution

The log-likelihood of centred data under $\mathcal{N}(0, C)$ is

$$
\ell(W, \sigma^2) = -\frac{n}{2}\Big(p \log 2\pi + \log\det C + \mathrm{tr}(C^{-1} S)\Big).
$$

**Theorem (Tipping and Bishop 1999).** With the eigenvalues $\lambda_1 \ge \dots \ge \lambda_p$ and eigenvectors
$v_1, \dots, v_p$ of the sample covariance $S$, and $\lambda_k > \lambda_{k+1}$, the maximum of $\ell$ is attained at

$$
\sigma^2_{\text{ML}} = \frac{1}{p - k}\sum_{j=k+1}^{p} \lambda_j,
\qquad
W_{\text{ML}} = V_k\,(\Lambda_k - \sigma^2_{\text{ML}} I)^{1/2} R,
$$

where $V_k$ holds the top $k$ eigenvectors, $\Lambda_k$ the top $k$ eigenvalues on a diagonal, and $R$ is any
$k \times k$ orthogonal matrix.

The proof (in the paper, about two pages) sets the derivative of $\ell$ with respect to $W$ to zero, which gives
$SC^{-1}W = W$, and shows that the columns of $W$ must then lie along eigenvectors of $S$; checking the second-order
conditions shows that only the top $k$ eigenvectors give a maximum, the others are saddle points. The result is easy
to believe and to remember:

- The **subspace** is exactly the PCA subspace.
- The **noise variance** is the average variance in the discarded directions: the model explains whatever is left
  over as noise.
- Each loading column has length $\sqrt{\lambda_j - \sigma^2}$: the variance along a principal direction, minus the
  part due to noise.

As $\sigma^2 \to 0$, PPCA becomes ordinary PCA. What the model adds is a likelihood. We can compare different $k$
on held-out data or with a penalty, compute how likely a new point is (a principled outlier score), fill in missing
values by EM, and build mixtures of PPCA models (Tipping and Bishop 1999 did that too). There is also an EM
algorithm for PPCA that finds the top subspace without forming $S$, useful when $p$ is very large (Roweis 1998).

### Factor analysis

PPCA assumes the noise has the **same** variance in every coordinate. **Factor analysis** (FA) allows each
coordinate its own noise variance:

$$
x = W z + \mu + \varepsilon, \qquad \varepsilon \sim \mathcal{N}(0, \Psi), \qquad \Psi = \mathrm{diag}(\psi_1, \dots, \psi_p),
$$

so $C = WW^\top + \Psi$. The idea is old: Charles Spearman introduced it in 1904 to explain correlations between
pupils' marks in different school subjects by one common factor. Now the noise $\psi_a$ of each feature is called its
**uniqueness**: the part of its variance not shared with any other feature.

There is no closed form for the maximum-likelihood FA solution, so it is fitted by EM (Rubin and Thayer 1982),
exactly as in [Chapter 13](13-Clustering.md), with $z$ as the hidden variable.

- **E step.** Given $x$, the hidden $z$ is Gaussian (a Gaussian conditioned on a linear Gaussian observation),
  with covariance $G = (I + W^\top \Psi^{-1} W)^{-1}$ and mean $E[z \mid x] = G W^\top \Psi^{-1}(x - \mu)$. The
  M step also needs $E[zz^\top \mid x] = G + E[z \mid x]E[z \mid x]^\top$.
- **M step.** Fit $W$ by least squares regression of $x$ on the expected $z$, and set each $\psi_a$ to the
  remaining variance of feature $a$:

$$
W = \Big(\sum_i (x_i - \mu)\,E[z_i]^\top\Big)\Big(\sum_i E[z_i z_i^\top]\Big)^{-1},
\qquad
\Psi = \mathrm{diag}\Big(S - \frac1n W \sum_i E[z_i](x_i - \mu)^\top\Big).
$$

The EM theorem of Chapter 13 applies unchanged: the likelihood never decreases.

**When do PCA and FA disagree?** When one feature is very noisy. PCA chases variance, so a feature with huge
variance of its own captures the first component even if it is unrelated to everything else. FA explains the
**correlations** between features with the factors and puts each feature's private variance into $\Psi$. A related
difference: FA is unchanged (up to rescaling of $W$ and $\Psi$) if you change the units of one feature, while PCA is
unchanged if you rotate the whole data space. Neither is "right"; they answer different questions.

### The program

The program fits PPCA to the 10-dimensional data with $k = 0$ to 5 and prints the noise variance, the
log-likelihood, the number of free parameters and the BIC, $-2\ell + (\text{parameters})\ln n$, which penalises
extra parameters (smaller is better). Then it builds data where one hidden factor drives features 0 to 4 and
feature 5 is unrelated noise with standard deviation 4, and compares PCA with FA.

```python
--8<-- "books/machine-learning/ch14_ppca_fa.py"
```

```
1. PPCA on the 10-dimensional data of ch14_pca.py (true noise variance 0.09)
   k   noise variance   log-likelihood   parameters        BIC
   0         1.4159         -4778.50      11      9619.73
   1         0.6128         -3919.21      21      7958.20
   2         0.2068         -2891.96      30      5955.04
   3         0.0880         -2236.97      38      4690.68
   4         0.0847         -2232.88      45      4722.43
   5         0.0817         -2230.41      51      4751.72

2. One hidden factor drives features 0-4; feature 5 is pure noise with a large variance
  PCA first direction:       [0.004, 0.009, 0.001, 0.003, -0.007, 1.0]
  factor analysis loadings:  [0.998, 0.911, 0.825, 0.657, 0.586, 0.035]
  factor analysis noise var: [0.096, 0.088, 0.086, 0.082, 0.082, 14.927]  (true [0.09, 0.09, 0.09, 0.09, 0.09, 16.0] )
```

In part 1 the estimated noise variance drops to 0.088 at $k = 3$ (the true value is 0.09) and then hardly moves.
The log-likelihood keeps rising with $k$, as it must for nested models, but after $k = 3$ only by about 4 and
2.5 units while costing 7 and 6 parameters; BIC is smallest at $k = 3$. In part 2, PCA's first direction is
almost exactly feature 5, the useless noisy one, because it has variance 16 against about 1 for the others. FA
recovers loadings close to the true $(1, 0.9, 0.8, 0.7, 0.6, 0)$ and puts the variance of feature 5 into its
uniqueness, 14.9 (the true value is 16; the sample is finite).

## 14.5 Non-linear methods: MDS, Isomap, t-SNE, UMAP

PCA finds flat subspaces. Many data sets lie on curved surfaces. The classic example is the **Swiss roll**: a flat
rectangle of points rolled up in 3-D like a cake. Its intrinsic dimension is 2, but no plane fits it: PCA squashes
the roll flat, and points on different layers of the roll, far apart along the sheet, land on top of each other.
The non-linear methods of this section all start from the same idea: **trust only small distances.** Two nearby
points on the roll are near on the sheet too; two far-apart points might be close in 3-D only because the sheet is
rolled.

### Classical multidimensional scaling

Before going non-linear we need one more linear tool. **Multidimensional scaling** (MDS) asks: given only a table of
distances $d_{ij}$ between $n$ objects (no coordinates at all), find points $y_1, \dots, y_n$ in $\mathbb{R}^k$
whose distances match. It started in psychology, where the "distances" were people's judgements of how different two
colours or sounds are. **Classical MDS** (Torgerson 1952) solves it with one eigen-decomposition.

**Theorem.** Let $D^{(2)}$ be the matrix of squared distances $d_{ij}^2$ between points $x_1, \dots, x_n$ with mean
zero, and $J = I - \frac1n \mathbf{1}\mathbf{1}^\top$ the **centring matrix**. Then
$B = -\tfrac12 J D^{(2)} J$ is the **Gram matrix** of the points, $B_{ij} = x_i \cdot x_j$.

*Proof.* Expand $d_{ij}^2 = \|x_i\|^2 + \|x_j\|^2 - 2 x_i \cdot x_j$. In matrix form,
$D^{(2)} = a\mathbf{1}^\top + \mathbf{1}a^\top - 2G$, where $a_i = \|x_i\|^2$ and $G_{ij} = x_i \cdot x_j$.
Multiplying by $J$ removes the mean of every column (on the left) and every row (on the right). Since
$J\mathbf{1} = 0$, the first two terms vanish: $J a\mathbf{1}^\top J = Ja(J\mathbf{1})^\top = 0$, and similarly for
the second. Because the points have mean zero, $G\mathbf{1} = X X^\top \mathbf{1} = X \cdot 0 = 0$, so $JGJ = G$.
Hence $JD^{(2)}J = -2G$. $\square$

So from distances alone we recover the Gram matrix $B = XX^\top$. Its eigen-decomposition $B = Q\Lambda Q^\top$ gives
coordinates $Y = Q_k \Lambda_k^{1/2}$ (top $k$ eigenvectors, scaled by the square roots of their eigenvalues).
When the distances really are Euclidean, these coordinates are exactly the PCA scores (up to sign): $B = XX^\top$ has
the same non-zero eigenvalues as $nS = X^\top X$, and $Q_k\Lambda_k^{1/2} = U_k\Sigma_k$, the scores from the SVD.
When the distances are not Euclidean, some eigenvalues of $B$ may be negative, and classical MDS gives the best
approximation in a specific least-squares sense. The program checks that MDS on the distances between six random
points returns a configuration with the same distances (to $10^{-8}$).

### Isomap: distances along the surface

Joshua Tenenbaum, Vin de Silva and John Langford's **Isomap** ("A Global Geometric Framework for Nonlinear
Dimensionality Reduction", *Science*, 2000) replaces straight-line distances by **geodesic distances**, distances
measured along the surface:

1. Build the $k$-nearest-neighbour graph: join each point to its $k$ nearest neighbours, with edge length equal to
   their Euclidean distance (small distances, which we trust).
2. Compute shortest-path distances between all pairs of points in this graph. A path that hops from neighbour to
   neighbour follows the surface, so its length approximates the geodesic distance.
3. Run classical MDS on the shortest-path distances.

Step 2 is the all-pairs shortest path problem. Our code uses the [Floyd-Warshall algorithm](../../graphs/floyd-warshall.md),
$O(n^3)$, vectorised so that each of the $n$ rounds is one NumPy operation; for sparse graphs, running
[Dijkstra's algorithm](../../graphs/dijkstra.md) from every vertex is faster (see
[Chapter 16 of the Algorithms book](../algorithms/16-Shortest-Paths.md)). The neighbour graph must be connected,
or some distances are infinite; the code checks.

Isomap is beautiful when it works, and fragile when the neighbourhood size is wrong. Too few neighbours and the graph
splits into pieces; too many and an edge jumps between layers of the roll (a **short circuit**), after which every
geodesic distance through it is wrong. The same issue of *Science* printed **locally linear embedding** (LLE, Roweis
and Saul 2000), which keeps instead the way each point is a weighted average of its neighbours. **Laplacian
eigenmaps** (Belkin and Niyogi 2003) use the bottom eigenvectors of a graph Laplacian as coordinates, the same
mathematics as spectral clustering in [Chapter 13](13-Clustering.md).

### t-SNE: keeping neighbours, not distances

Isomap still tries to preserve all distances, near and far. For a picture of clusters, we may care only that
**neighbours stay neighbours**. **Stochastic neighbour embedding** (SNE, Hinton and Roweis 2002) turns distances
into probabilities of being neighbours, and **t-SNE** (Laurens van der Maaten and Geoffrey Hinton, "Visualizing Data
using t-SNE", *Journal of Machine Learning Research*, 2008) fixed SNE's main defects. It has become the most used
picture of high-dimensional data in biology and machine learning.

**Step 1: neighbour probabilities in the data.** For each point $i$, put a Gaussian around it and let

$$
p_{j \mid i} = \frac{\exp(-\|x_i - x_j\|^2 / 2\sigma_i^2)}{\sum_{l \ne i}\exp(-\|x_i - x_l\|^2 / 2\sigma_i^2)} ,
$$

the probability that $i$ would pick $j$ as its neighbour. The width $\sigma_i$ is chosen separately for each
point, by binary search, so that the distribution has a fixed **perplexity** $2^{H}$, where
$H = -\sum_j p_{j|i}\log_2 p_{j|i}$ is its entropy ([Chapter 3](03-The-Math-Toolkit.md)). Perplexity is a smooth
"effective number of neighbours", typically 5 to 50. Points in dense regions get small $\sigma_i$, points in sparse
regions large ones. Then symmetrise: $p_{ij} = (p_{j|i} + p_{i|j})/2n$, so the $p_{ij}$ sum to 1.

**Step 2: neighbour probabilities in the picture.** For 2-D points $y_1, \dots, y_n$, define

$$
q_{ij} = \frac{(1 + \|y_i - y_j\|^2)^{-1}}{\sum_{l \ne m}(1 + \|y_l - y_m\|^2)^{-1}} .
$$

The kernel $(1 + d^2)^{-1}$ is the **Student t distribution** with one degree of freedom (the Cauchy distribution),
which is where the "t" comes from. Its tails are heavy: it decays like $1/d^2$, not like $e^{-d^2}$.

**Step 3: make them match.** Minimise the Kullback-Leibler divergence

$$
C = \mathrm{KL}(P \,\|\, Q) = \sum_{i \ne j} p_{ij}\log\frac{p_{ij}}{q_{ij}}
$$

by gradient descent on the $y_i$. The gradient has a simple form (derived in the paper's appendix):

$$
\frac{\partial C}{\partial y_i} = 4\sum_{j}(p_{ij} - q_{ij})\,\frac{y_i - y_j}{1 + \|y_i - y_j\|^2} .
$$

Read it as forces. If $p_{ij} > q_{ij}$, the pair is closer in the data than in the picture, and the term pulls
$y_i$ towards $y_j$ (moving against the gradient). If $p_{ij} < q_{ij}$, it pushes them apart. KL divergence
punishes heavily when $p_{ij}$ is large but $q_{ij}$ small (neighbours placed far apart), and only lightly the
reverse, so t-SNE cares mostly about keeping neighbours together.

**Why the heavy tail?** The **crowding problem**. In 10 dimensions a point can have many neighbours all at the same
moderate distance; in 2-D there is not enough room around a point to place them all at that distance. With a
Gaussian in the picture, moderately distant points are crushed together. The heavy-tailed t kernel lets moderately
distant points sit much farther apart in the picture while keeping the same $q_{ij}$, which relieves the crowding and
separates clusters cleanly.

Practical tricks from the paper, all in our code: start from tiny random positions; **early exaggeration**
(multiply all $p_{ij}$ by a factor, 12 in our code, for the first 100 iterations, so that clusters form first and then
spread); and momentum. Each iteration costs $O(n^2)$, fine for a few thousand points; the **Barnes-Hut** version (van der
Maaten 2014) approximates the far-away forces in $O(n \log n)$, and later methods are faster still.

### UMAP

**UMAP** (Leland McInnes, John Healy and James Melville, "UMAP: Uniform Manifold Approximation and Projection for
Dimension Reduction", 2018) is justified in its paper by topology (fuzzy simplicial sets), but computationally it is
close kin to t-SNE: it builds a weighted $k$-nearest-neighbour graph with a per-point distance scale, symmetrises it,
and lays out a low-dimensional graph whose edge weights match, by minimising a cross-entropy with stochastic gradient
descent and negative sampling (pushing apart randomly chosen non-neighbours). It is much faster than exact t-SNE and
scales to millions of points. It is often said to keep more global structure than t-SNE; Dmitry Kobak and George
Linderman (*Nature Biotechnology*, 2021) showed that much of that difference comes from how the two methods are
initialised, and that t-SNE started from a PCA layout keeps global structure about as well. Treat claims of global
faithfulness with care for both.

### How to read (and misread) such plots

t-SNE and UMAP pictures are very persuasive, and the brief rules below are worth learning before you show one to
anyone. Martin Wattenberg, Fernanda Viégas and Ian Johnson's article "How to Use t-SNE Effectively" (*Distill*,
2016) shows each one with interactive examples.

1. **Cluster sizes mean nothing.** t-SNE adapts $\sigma_i$ to local density, so a tight cluster and a wide one come
   out about the same size. Our program demonstrates it below.
2. **Distances between clusters mean little.** Two clusters far apart in the picture may or may not be far apart in
   the data, and the gaps change with perplexity.
3. **Random noise can look like clusters,** especially at low perplexity. Always try several perplexities and
   several random seeds; structure that is real survives.
4. **Shapes can be artefacts.** A long thin line or a ring may be a feature of the optimisation, not the data.
5. **Axes have no meaning.** The picture can be rotated or reflected freely; there are no "t-SNE units".
6. **Do not cluster the picture and call it a result.** If you need clusters, cluster the data (or a PCA reduction
   of it), and use the picture to look at them.

### The program

```python
--8<-- "books/machine-learning/ch14_nonlinear.py"
```

```
1. Classical MDS from distances alone gives back a configuration with the same distances
  largest distance error: 1.1e-08

2. Swiss roll: 500 points on a rolled-up sheet in 3-D; t is the position along the roll
  PCA                      best |correlation| of a coordinate with t: 0.265
  Isomap (10 neighbours)   best |correlation| of a coordinate with t: 0.992

3. t-SNE on three clusters in 10-D: a tight one, a medium one and a wide one
  input (10-D)  cluster spreads [1.59, 6.46, 15.61]  ratio of centre distances d(0,2)/d(0,1) = 3.03
  PCA (2-D)     cluster spreads [0.72, 3.08, 7.63]  ratio of centre distances d(0,2)/d(0,1) = 3.04
  t-SNE (2-D)   cluster spreads [2.36, 2.35, 2.39]  ratio of centre distances d(0,2)/d(0,1) = 1.20
  10 nearest neighbours kept: PCA 0.38, t-SNE 0.55;  final KL(P||Q) = 0.433
```

On the Swiss roll, no PCA coordinate correlates well with the position $t$ along the roll (best $|r| = 0.265$): the
projection overlays the layers. Isomap's first coordinate follows the roll almost perfectly ($|r| = 0.992$): it has
unrolled the sheet.

Part 3 is the misreading lesson in numbers. Three clusters in 10-D have spreads 1.59, 6.46 and 15.61 (a factor of
ten between the tightest and the widest), and the third is three times as far from the first as the second is.
PCA keeps both facts (spreads in the same proportions, distance ratio 3.04). t-SNE makes all three clusters the same
size (2.36, 2.35, 2.39) and shrinks the distance ratio to 1.20. Yet t-SNE keeps more of each point's 10 nearest
neighbours (55% against 38% for PCA). Both statements are true at once: t-SNE is good at neighbourhoods and says
nothing reliable about sizes and far distances.

<figure class="mars-fig" markdown="0">
<svg viewBox="0 0 640 230" role="img" aria-label="Horizontal bars of the spread of three clusters. In the 10-dimensional data the spreads are 1.59, 6.46 and 15.61. In the t-SNE picture they are 2.36, 2.35 and 2.39, all the same.">
  <g fill="currentColor" font-size="13">
    <text x="20" y="22">spread of each cluster in the 10-D data</text>
    <text x="20" y="132">spread of each cluster in the t-SNE picture</text>
  </g>
  <g fill="currentColor" font-size="12" text-anchor="end">
    <text x="110" y="49">tight</text><text x="110" y="75">medium</text><text x="110" y="101">wide</text>
    <text x="110" y="159">tight</text><text x="110" y="185">medium</text><text x="110" y="211">wide</text>
  </g>
  <g stroke="currentColor" stroke-width="0.8">
    <rect x="120" y="36" width="47.7" height="18" fill="#7ccf9a"/>
    <rect x="120" y="62" width="193.8" height="18" fill="#9cc9ea"/>
    <rect x="120" y="88" width="468.3" height="18" fill="#eea66f"/>
    <rect x="120" y="146" width="70.8" height="18" fill="#7ccf9a"/>
    <rect x="120" y="172" width="70.5" height="18" fill="#9cc9ea"/>
    <rect x="120" y="198" width="71.7" height="18" fill="#eea66f"/>
  </g>
  <g fill="currentColor" font-size="12">
    <text x="174" y="50">1.59</text><text x="320" y="76">6.46</text><text x="594" y="102">15.61</text>
    <text x="197" y="160">2.36</text><text x="197" y="186">2.35</text><text x="198" y="212">2.39</text>
  </g>
</svg>
<figcaption>The spreads printed by the program (same scale for both groups of bars). Clusters whose sizes differ by
a factor of ten in the data come out the same size in t-SNE: never read cluster sizes off such a picture.</figcaption>
</figure>

## 14.6 Autoencoders preview

An **autoencoder** is a neural network trained to output its own input, through a narrow middle. It has two parts:
an **encoder** $f$ that maps $x \in \mathbb{R}^p$ to a short **code** $z = f(x) \in \mathbb{R}^k$, and a
**decoder** $g$ that maps the code back, $\hat{x} = g(z)$. Training minimises the reconstruction error
$\frac1n\sum_i\|x_i - g(f(x_i))\|^2$. Because $k < p$, the network cannot just copy; the narrow middle, the
**bottleneck**, forces it to find a compact description. The code $z$ is then the reduced representation.

<figure class="mars-fig" markdown="0">
<svg viewBox="0 0 640 200" role="img" aria-label="An autoencoder: an input layer of ten units, connected to a bottleneck layer of three units by the encoder, connected to an output layer of ten units by the decoder. The output should equal the input.">
  <g stroke="currentColor" stroke-width="0.4" opacity="0.6">
    <path d="M 120 30 L 320 70 M 120 30 L 320 100 M 120 30 L 320 130 M 120 170 L 320 70 M 120 170 L 320 100 M 120 170 L 320 130 M 120 100 L 320 70 M 120 100 L 320 130"/>
    <path d="M 520 30 L 320 70 M 520 30 L 320 100 M 520 30 L 320 130 M 520 170 L 320 70 M 520 170 L 320 100 M 520 170 L 320 130 M 520 100 L 320 70 M 520 100 L 320 130"/>
  </g>
  <g stroke="currentColor" stroke-width="0.8" fill="#9cc9ea">
    <circle cx="120" cy="30" r="6"/><circle cx="120" cy="45.6" r="6"/><circle cx="120" cy="61.1" r="6"/>
    <circle cx="120" cy="76.7" r="6"/><circle cx="120" cy="92.2" r="6"/><circle cx="120" cy="107.8" r="6"/>
    <circle cx="120" cy="123.3" r="6"/><circle cx="120" cy="138.9" r="6"/><circle cx="120" cy="154.4" r="6"/>
    <circle cx="120" cy="170" r="6"/>
  </g>
  <g stroke="currentColor" stroke-width="0.8" fill="#eea66f">
    <circle cx="320" cy="70" r="8"/><circle cx="320" cy="100" r="8"/><circle cx="320" cy="130" r="8"/>
  </g>
  <g stroke="currentColor" stroke-width="0.8" fill="#7ccf9a">
    <circle cx="520" cy="30" r="6"/><circle cx="520" cy="45.6" r="6"/><circle cx="520" cy="61.1" r="6"/>
    <circle cx="520" cy="76.7" r="6"/><circle cx="520" cy="92.2" r="6"/><circle cx="520" cy="107.8" r="6"/>
    <circle cx="520" cy="123.3" r="6"/><circle cx="520" cy="138.9" r="6"/><circle cx="520" cy="154.4" r="6"/>
    <circle cx="520" cy="170" r="6"/>
  </g>
  <g fill="currentColor" font-size="13" text-anchor="middle">
    <text x="120" y="192">input x (10)</text>
    <text x="320" y="192">code z (3)</text>
    <text x="520" y="192">output x̂ (10)</text>
    <text x="220" y="20">encoder f</text>
    <text x="420" y="20">decoder g</text>
  </g>
</svg>
<figcaption>An autoencoder with a bottleneck of three units (only some connections drawn). It is trained so that the
output reproduces the input; the three middle numbers become the compressed description.</figcaption>
</figure>

**A linear autoencoder is PCA.** Suppose both parts are linear maps of centred data: $z = Ex$ with a $k \times p$
matrix $E$, and $\hat{x} = Dz$ with a $p \times k$ matrix $D$. Then $\hat{X} = XE^\top D^\top$, a matrix of rank at
most $k$. By the Eckart-Young theorem, no rank-$k$ matrix is closer to $X$ in squared error than the truncated SVD
$U_k\Sigma_kV_k^\top = XV_kV_k^\top$, so the reconstruction error is at least the sum of the discarded eigenvalues,
and the bound is reached by $E = V_k^\top$, $D = V_k$: PCA. Every optimum has the same column space for $D$, the
PCA subspace, though $D$ itself need not be orthonormal ($D \to DA$, $E \to A^{-1}E$ for any invertible $A$ gives
the same output). Pierre Baldi and Kurt Hornik proved in 1989 something stronger: the squared error of a linear
autoencoder has no bad local minima; every local minimum is a global one, and the other critical points are saddles.

The first part of the program trains a 10-3-10 linear autoencoder by plain gradient descent (the two gradients are
derived with the chain rule, which [Chapter 15](15-Neural-Networks-and-Backpropagation.md) makes systematic). It
reaches exactly PCA's error, 0.6162; the cosines of the angles between its subspace and the PCA subspace are all 1
(the same subspace); and $D^\top D$ is close to, but not exactly, the identity.

```python
--8<-- "books/machine-learning/ch14_autoencoder.py"
```

```
1. Linear autoencoder 10 -> 3 -> 10 on the data of ch14_pca.py
  reconstruction error: autoencoder 0.6162, PCA with 3 components 0.6162
  cosines of the angles between its subspace and the PCA subspace: [1.0, 1.0, 1.0]
  is the decoder orthonormal like PCA?  D^T D = [[1.03, 0.0, 0.03], [0.0, 1.04, 0.01], [0.03, 0.01, 0.95]]

2. 200 points on a circle, squeezed through one number
  PCA with 1 component: error 0.4762
  non-linear autoencoder 2-32-1-32-2: error 0.0011
```

**A non-linear autoencoder can follow curves.** The second part squeezes 200 points on a circle through a single
number. PCA with one component can only project onto a line through the centre, and loses about half the variance
(error 0.476; the circle's total variance is about 1). An autoencoder with a hidden layer of 32 tanh units on each
side of the one-number code learns to encode the angle and decode it back to the circle, with error 0.0011. A circle
cannot be mapped to a line continuously and one-to-one, so somewhere the code must jump; the network places the
jump between two neighbouring points, where it costs little.

Geoffrey Hinton and Ruslan Salakhutdinov ("Reducing the Dimensionality of Data with Neural Networks", *Science*,
2006) showed that deep autoencoders, trained with a layer-by-layer start, produce much better low-dimensional codes
of images and documents than PCA. Today autoencoders are the basis of much larger ideas: **denoising autoencoders**
(Vincent et al. 2008) learn to remove noise added on purpose, **sparse autoencoders** learn many features of which
few are active at once (a tool of interpretability research, [Chapter 23](23-Where-Machine-Learning-Goes.md)), and
**variational autoencoders** turn the code into a probability distribution, which makes them generative models
([Chapter 20](20-Generative-Models.md)). To build them we need neural networks and backpropagation properly, which is
where the next chapter begins.

**In practice:** scikit-learn has `PCA` (with randomised SVD for large data), `IncrementalPCA`, `FactorAnalysis`,
`MDS`, `Isomap`, `LocallyLinearEmbedding`, `SpectralEmbedding` and `TSNE`; UMAP is the separate `umap-learn`
package; openTSNE is a fast t-SNE. Autoencoders are written in PyTorch or JAX.

## Check yourself

??? question "1. Three centred points in the plane are $(1, 1)$, $(-1, -1)$ and $(0, 0)$. Without computing, what are the first principal direction and the two eigenvalues of the covariance?"

    All three lie on the line $y = x$, so the first principal direction is $(1, 1)/\sqrt{2}$ and all variance lies on
    it. Scores are $\sqrt2, -\sqrt2, 0$, so $\lambda_1 = (2 + 2 + 0)/3 = 4/3$ and $\lambda_2 = 0$. Check with the
    trace: $S_{11} = S_{22} = 2/3$, total $4/3$.

??? question "2. Prove that the principal component scores of different components are uncorrelated."

    The scores on components $j$ and $m$ are $z_{ij} = v_j^\top x_i$ and $z_{im} = v_m^\top x_i$, with mean zero.
    Their covariance is $\frac1n\sum_i v_j^\top x_i x_i^\top v_m = v_j^\top S v_m = \lambda_m v_j^\top v_m = 0$ for
    $j \ne m$, since eigenvectors of a symmetric matrix for different eigenvalues are orthogonal (and an orthonormal
    basis is chosen when eigenvalues repeat). So PCA turns correlated features into uncorrelated ones; the
    covariance of the scores is $\mathrm{diag}(\lambda_1, \dots, \lambda_k)$.

??? question "3. A data set has 5 features with eigenvalues 6, 2, 1, 0.6, 0.4. How many components keep at least 90% of the variance, and what is the mean squared reconstruction error with two components?"

    Total $= 10$. Cumulative shares: 60%, 80%, 90%, 96%, 100%, so three components reach 90%. With two components
    the error is the sum of the discarded eigenvalues, $1 + 0.6 + 0.4 = 2$ (per point, in squared units).

??? question "4. Write the code: compute the first principal direction without any eigenvalue routine, by power iteration ($w \leftarrow Sw / \|Sw\|$), and check it on the hand example."

    Power iteration converges to the top eigenvector when $\lambda_1 > \lambda_2$, because writing
    $w = \sum_j c_j v_j$, after $t$ steps $S^t w = \sum_j c_j\lambda_j^t v_j$ is dominated by $j = 1$; the error
    shrinks like $(\lambda_2/\lambda_1)^t$.

    ```python
    import numpy as np

    def power_iteration(S, steps=100, seed=0):
        w = np.random.default_rng(seed).normal(size=len(S))
        for _ in range(steps):
            w = S @ w
            w /= np.linalg.norm(w)
        return w * np.sign(w[np.abs(w).argmax()]), w @ S @ w

    S = np.array([[2.0, 1.2], [1.2, 0.8]])
    print(power_iteration(S))   # (array([0.85065081, 0.52573111]), 2.7416...)
    ```

    Here $\lambda_2/\lambda_1 \approx 0.021$, so a handful of steps already suffice.

??? question "5. You run PCA on features measured in very different units without standardising. What will the first component look like, and how do you fix it?"

    It will point almost entirely along the feature with the largest numerical variance, which says more about the
    choice of units than about the data. Standardise every feature to mean 0 and variance 1 first (PCA of the
    correlation matrix), unless all features share a unit and their variances are meaningful.

??? question "6. In PPCA with $p = 4$, $k = 1$ and sample eigenvalues 5, 1, 0.6, 0.4, what are $\sigma^2_{\text{ML}}$ and the length of the loading vector $W$?"

    $\sigma^2_{\text{ML}} = (1 + 0.6 + 0.4)/3 = 2/3$. The loading is $v_1\sqrt{\lambda_1 - \sigma^2} = v_1\sqrt{5 - 2/3}$,
    of length $\sqrt{13/3} \approx 2.08$. The model covariance $WW^\top + \sigma^2 I$ has variance
    $13/3 + 2/3 = 5$ along $v_1$, exactly matching the data, and $2/3$ in every other direction.

??? question "7. Show that classical MDS applied to the Euclidean distances of centred data gives the same coordinates as PCA (up to sign)."

    MDS diagonalises $B = XX^\top$. With the SVD $X = U\Sigma V^\top$, $B = U\Sigma^2U^\top$, so its top eigenvectors are
    the columns of $U_k$ and its eigenvalues are $s_j^2$. MDS returns $U_k\Sigma_k$. PCA scores are
    $XV_k = U\Sigma V^\top V_k = U_k\Sigma_k$. Identical, except that each eigenvector's sign is arbitrary.

??? question "8. Why does t-SNE use a different width $\sigma_i$ for each point, and why does this make cluster sizes in the picture meaningless?"

    A single width would give points in sparse regions almost no neighbours (all $p_{j|i}$ tiny except one) and points
    in dense regions far too many. Fixing the perplexity gives every point about the same effective number of
    neighbours. The price: a point in a wide cluster and a point in a tight cluster end up with similar neighbour
    distributions, so in the picture both clusters are drawn with similar size. The density information was
    deliberately normalised away.

??? question "9. Compute the t-SNE gradient on a toy case: two points with $p_{12} = p_{21} = 0.5$ and picture positions $y_1 = (0,0)$, $y_2 = (1,0)$. What is $q_{12}$ and the gradient? Explain."

    With only two points, $q_{12} = q_{21} = 0.5$ whatever their positions (the normalisation divides by the only
    pair, counted twice). So $p_{ij} - q_{ij} = 0$ and the gradient is zero: any separation is optimal. t-SNE only
    compares relative distances; with three or more points the ratios matter and the forces are non-zero.

??? question "10. Write the code: the gradients of the linear autoencoder loss $L = \frac1n\|XE^\top D^\top - X\|_F^2$ used in the program are $\nabla_D L = \frac2n R^\top Z$ and $\nabla_E L = \frac2n (RD)^\top X$, with $Z = XE^\top$ and $R = ZD^\top - X$. Check them against finite differences."

    ```python
    import numpy as np
    rng = np.random.default_rng(0)
    X, E, D = rng.normal(size=(20, 5)), rng.normal(size=(2, 5)), rng.normal(size=(5, 2))
    def loss(E, D):
        return ((X @ E.T @ D.T - X) ** 2).sum() / len(X)
    Z = X @ E.T
    R = Z @ D.T - X
    gD, gE = 2 * R.T @ Z / len(X), 2 * (R @ D).T @ X / len(X)
    h = 1e-6
    for name, M, g in (("D", D, gD), ("E", E, gE)):
        num = np.zeros_like(M)
        for idx in np.ndindex(M.shape):
            M[idx] += h; up = loss(E, D)
            M[idx] -= 2 * h; down = loss(E, D)
            M[idx] += h
            num[idx] = (up - down) / (2 * h)
        print(name, np.abs(num - g).max())   # both about 1e-8 or smaller
    ```

    The derivation: $L = \frac1n\sum_i\|DEx_i - x_i\|^2$; with $r_i = DEx_i - x_i$, $\partial L/\partial D =
    \frac2n\sum_i r_i (Ex_i)^\top$ and $\partial L/\partial E = \frac2n\sum_i D^\top r_i x_i^\top$, which are the matrix
    formulas.

??? question "11. (Hard) Show that the PPCA log-likelihood at the maximum, as a function of $k$, depends only on the eigenvalues of $S$, and explain why it increases with $k$."

    At the maximum, $C = V_k\Lambda_kV_k^\top + \sigma^2(I - V_kV_k^\top)$, which has eigenvalues
    $\lambda_1, \dots, \lambda_k$ and $p - k$ copies of $\sigma^2 = \bar{\lambda}$ (the mean of the discarded
    eigenvalues), with the same eigenvectors as $S$. So $\log\det C = \sum_{j \le k}\log\lambda_j + (p-k)\log\bar{\lambda}$
    and $\mathrm{tr}(C^{-1}S) = k + \sum_{j > k}\lambda_j/\bar{\lambda} = k + (p - k) = p$. Hence
    $\ell = -\frac n2\big(p\log 2\pi + p + \sum_{j\le k}\log\lambda_j + (p-k)\log\bar{\lambda}\big)$. Going from $k$ to
    $k+1$ replaces $\log$ of the mean of the discarded eigenvalues by an exact $\log\lambda_{k+1}$ plus the log of the
    new mean of the rest; by concavity of $\log$ (Jensen), the mean of logs is at most the log of the mean, so
    $\log\det C$ can only go down and $\ell$ can only go up. That is why a penalty such as BIC is needed to choose $k$.

## What you learned

- Dimensionality reduction finds a few coordinates that keep the structure of data: for seeing, compressing,
  denoising and helping later models; it works because real data tends to lie near low-dimensional surfaces.
- PCA's directions are the eigenvectors of the covariance matrix with the largest eigenvalues; they maximise kept
  variance and, equivalently, minimise reconstruction error, whose minimum is the sum of the discarded eigenvalues.
- Compute PCA with the SVD of the centred data: the right singular vectors are the directions, $s_j^2/n$ the
  eigenvalues, $U\Sigma$ the scores.
- Choose the number of components from the scree plot and the explained variance, or from a likelihood with a
  penalty, or from the task the components are for.
- Probabilistic PCA is a Gaussian latent variable model whose maximum-likelihood solution is PCA with noise equal to
  the average discarded variance; factor analysis gives each feature its own noise and is fitted by EM.
- Classical MDS recovers coordinates from distances; Isomap uses graph shortest paths to unroll curved surfaces;
  t-SNE and UMAP keep neighbourhoods but not sizes or far distances, so their pictures must be read with care.
- A linear autoencoder learns the PCA subspace; non-linear autoencoders can compress curved data, and lead to
  denoising, sparse and variational autoencoders.

**Next:** [Chapter 15](15-Neural-Networks-and-Backpropagation.md), which builds neural networks from single
neurons, derives backpropagation, and writes a small automatic-differentiation engine from scratch.

## Further reading

- C. Bishop, *Pattern Recognition and Machine Learning*, 2006, chapter 12 (PCA, probabilistic PCA, factor analysis,
  kernel PCA, non-linear latent variable models).
- T. Hastie, R. Tibshirani and J. Friedman, *The Elements of Statistical Learning*, 2nd ed., 2009, sections 14.5 to
  14.9 (principal components, factor analysis, multidimensional scaling, non-linear dimension reduction).
- K. Murphy, *Probabilistic Machine Learning: An Introduction*, 2022, chapter 20 (dimensionality reduction, from PCA
  to t-SNE and UMAP, and autoencoders).
- I. Goodfellow, Y. Bengio and A. Courville, *Deep Learning*, 2016, chapter 14 (autoencoders).
- K. Pearson, "On Lines and Planes of Closest Fit to Systems of Points in Space", *Philosophical Magazine*, 1901;
  H. Hotelling, "Analysis of a Complex of Statistical Variables into Principal Components", *Journal of Educational
  Psychology*, 1933.
- C. Eckart and G. Young, "The Approximation of One Matrix by Another of Lower Rank", *Psychometrika*, 1936.
- M. Tipping and C. Bishop, "Probabilistic Principal Component Analysis", *Journal of the Royal Statistical Society
  B*, 1999; S. Roweis, "EM Algorithms for PCA and SPCA", NIPS 1997 (published 1998).
- D. Rubin and D. Thayer, "EM Algorithms for ML Factor Analysis", *Psychometrika*, 1982.
- W. Torgerson, "Multidimensional Scaling: I. Theory and Method", *Psychometrika*, 1952.
- J. Tenenbaum, V. de Silva and J. Langford, "A Global Geometric Framework for Nonlinear Dimensionality Reduction",
  *Science*, 2000; S. Roweis and L. Saul, "Nonlinear Dimensionality Reduction by Locally Linear Embedding",
  *Science*, 2000; M. Belkin and P. Niyogi, "Laplacian Eigenmaps for Dimensionality Reduction and Data
  Representation", *Neural Computation*, 2003.
- L. van der Maaten and G. Hinton, "Visualizing Data using t-SNE", *Journal of Machine Learning Research*, 2008;
  L. van der Maaten, "Accelerating t-SNE using Tree-Based Algorithms", *JMLR*, 2014.
- L. McInnes, J. Healy and J. Melville, "UMAP: Uniform Manifold Approximation and Projection for Dimension
  Reduction", arXiv 2018; D. Kobak and G. Linderman, "Initialization is Critical for Preserving Global Data Structure
  in both t-SNE and UMAP", *Nature Biotechnology*, 2021.
- M. Wattenberg, F. Viégas and I. Johnson, "How to Use t-SNE Effectively", *Distill*, 2016.
- P. Baldi and K. Hornik, "Neural Networks and Principal Component Analysis: Learning from Examples Without Local
  Minima", *Neural Networks*, 1989; G. Hinton and R. Salakhutdinov, "Reducing the Dimensionality of Data with
  Neural Networks", *Science*, 2006.
- N. Halko, P.-G. Martinsson and J. Tropp, "Finding Structure with Randomness: Probabilistic Algorithms for
  Constructing Approximate Matrix Decompositions", *SIAM Review*, 2011.
- On this site: the reference pages [Floyd-Warshall](../../graphs/floyd-warshall.md) and
  [Dijkstra's algorithm](../../graphs/dijkstra.md); [Chapter 16 of the Algorithms book](../algorithms/16-Shortest-Paths.md);
  [Chapter 13](13-Clustering.md) for EM and the graph Laplacian; [Chapter 20](20-Generative-Models.md) for
  variational autoencoders; the linear algebra book at [https://math.akadian.ca/books/](https://math.akadian.ca/books/).
