# 4. Linear regression

*Given the areas and prices of some flats, what price should we expect for a flat of 80 square metres? The oldest
answer in data analysis is still one of the most useful: draw the straight line that fits the points best, and read
the answer off the line. This chapter makes "fits best" precise with the squared error, finds the best line exactly
with the normal equations and sees why they are a projection, extends the line to many features and to curves, finds
the same answer by gradient descent and proves when that converges, shows that squared error is what maximum
likelihood demands under Gaussian noise, learns to read and check a fitted model, and ends with the numerically
careful way to solve least squares that real libraries use.*

!!! abstract "In this chapter"
    **You will learn:**

    - the squared-error loss, why it is used, and its history (Legendre 1805, Gauss)
    - the exact least-squares solution for a line, by hand, and the normal equations for any number of features
    - least squares as an orthogonal projection, with a proof that it is the global minimum
    - design matrices, polynomial features, and the first sight of overfitting
    - gradient descent from scratch, the learning rate, and a convergence proof for least squares
    - the proof that maximum likelihood with Gaussian noise gives least squares
    - how to read coefficients, R squared and residual plots
    - (advanced) QR and SVD solutions, condition numbers, and why we do not invert $X^\top X$

    **You need:** [Chapter 2](02-Data-and-Features.md) (features, scaling) and
    [Chapter 3](03-The-Math-Toolkit.md) (dot products, matrices, gradients, likelihood; section 3.6 for 4.7).

    **Levels:** 4.1 to 4.3 are beginner; 4.4 to 4.6 are intermediate; 4.7 is advanced.

## 4.1 Fitting a line

Here are the ten flats from Chapter 2 whose area was actually measured (we leave out flat 5, whose area was filled
in):

| area (m²) | 52 | 75 | 40 | 98 | 63 | 75 | 45 | 88 | 58 | 70 |
|---|---|---|---|---|---|---|---|---|---|---|
| price (thousands) | 210 | 255 | 140 | 390 | 240 | 260 | 170 | 335 | 230 | 215 |

Bigger flats cost more, roughly in proportion. A model that says so is a straight line,

$$
\hat y=w_0+w_1x ,
$$

where $x$ is the area, $\hat y$ ("y-hat") is the predicted price, $w_1$ is the **slope** (extra thousands per extra
square metre) and $w_0$ is the **intercept** (the predicted price at $x=0$, which here is just a number that puts the
line in the right place, not a real price). This is **linear regression** with one feature. Which line is best?

### The squared-error loss

For each flat, the line makes an error, the **residual** $r_i=y_i-\hat y_i$: positive if the line is too low,
negative if it is too high. We want the residuals small, all at once. The standard choice is to minimise the **sum of
squared errors**,

$$
\mathrm{SSE}(w_0,w_1)=\sum_{i=1}^n\bigl(y_i-w_0-w_1x_i\bigr)^2 ,
$$

or, equivalently, the **mean squared error** $\mathrm{MSE}=\mathrm{SSE}/n$. This is the method of **least squares**.

<figure class="mars-fig" markdown="0">
<svg viewBox="0 0 640 330" role="img" aria-label="Scatter plot of the ten flats, area from 35 to 105 square metres across, price from 100 to 420 thousand up. The orange least-squares line rises from lower left to upper right. A dashed vertical segment joins each point to the line: these are the residuals whose squares are added.">
  <line x1="70" y1="290" x2="490" y2="290" stroke="currentColor"/>
  <line x1="70" y1="290" x2="70" y2="30" stroke="currentColor"/>
  <line x1="100" y1="290" x2="100" y2="296" stroke="currentColor"/>
  <text x="100" y="311" font-size="12" text-anchor="middle" fill="currentColor">40</text>
  <line x1="220" y1="290" x2="220" y2="296" stroke="currentColor"/>
  <text x="220" y="311" font-size="12" text-anchor="middle" fill="currentColor">60</text>
  <line x1="340" y1="290" x2="340" y2="296" stroke="currentColor"/>
  <text x="340" y="311" font-size="12" text-anchor="middle" fill="currentColor">80</text>
  <line x1="460" y1="290" x2="460" y2="296" stroke="currentColor"/>
  <text x="460" y="311" font-size="12" text-anchor="middle" fill="currentColor">100</text>
  <line x1="64" y1="290" x2="70" y2="290" stroke="currentColor"/>
  <text x="58" y="294" font-size="12" text-anchor="end" fill="currentColor">100</text>
  <line x1="64" y1="209" x2="70" y2="209" stroke="currentColor"/>
  <text x="58" y="213" font-size="12" text-anchor="end" fill="currentColor">200</text>
  <line x1="64" y1="128" x2="70" y2="128" stroke="currentColor"/>
  <text x="58" y="132" font-size="12" text-anchor="end" fill="currentColor">300</text>
  <line x1="64" y1="46" x2="70" y2="46" stroke="currentColor"/>
  <text x="58" y="50" font-size="12" text-anchor="end" fill="currentColor">400</text>
  <line x1="82.0" y1="263.3" x2="478.0" y2="59.7" stroke="#eea66f" stroke-width="2.5"/>
  <line x1="172.0" y1="200.6" x2="172.0" y2="217.0" stroke="currentColor" stroke-dasharray="3 2"/>
  <line x1="310.0" y1="164.1" x2="310.0" y2="146.1" stroke="currentColor" stroke-dasharray="3 2"/>
  <line x1="100.0" y1="257.5" x2="100.0" y2="254.0" stroke="currentColor" stroke-dasharray="3 2"/>
  <line x1="448.0" y1="54.4" x2="448.0" y2="75.1" stroke="currentColor" stroke-dasharray="3 2"/>
  <line x1="238.0" y1="176.2" x2="238.0" y2="183.1" stroke="currentColor" stroke-dasharray="3 2"/>
  <line x1="310.0" y1="160.0" x2="310.0" y2="146.1" stroke="currentColor" stroke-dasharray="3 2"/>
  <line x1="130.0" y1="233.1" x2="130.0" y2="238.6" stroke="currentColor" stroke-dasharray="3 2"/>
  <line x1="388.0" y1="99.1" x2="388.0" y2="106.0" stroke="currentColor" stroke-dasharray="3 2"/>
  <line x1="208.0" y1="184.4" x2="208.0" y2="198.5" stroke="currentColor" stroke-dasharray="3 2"/>
  <line x1="280.0" y1="196.6" x2="280.0" y2="161.5" stroke="currentColor" stroke-dasharray="3 2"/>
  <circle cx="172.0" cy="200.6" r="5" fill="#9cc9ea" stroke="currentColor"/>
  <circle cx="310.0" cy="164.1" r="5" fill="#9cc9ea" stroke="currentColor"/>
  <circle cx="100.0" cy="257.5" r="5" fill="#9cc9ea" stroke="currentColor"/>
  <circle cx="448.0" cy="54.4" r="5" fill="#9cc9ea" stroke="currentColor"/>
  <circle cx="238.0" cy="176.2" r="5" fill="#9cc9ea" stroke="currentColor"/>
  <circle cx="310.0" cy="160.0" r="5" fill="#9cc9ea" stroke="currentColor"/>
  <circle cx="130.0" cy="233.1" r="5" fill="#9cc9ea" stroke="currentColor"/>
  <circle cx="388.0" cy="99.1" r="5" fill="#9cc9ea" stroke="currentColor"/>
  <circle cx="208.0" cy="184.4" r="5" fill="#9cc9ea" stroke="currentColor"/>
  <circle cx="280.0" cy="196.6" r="5" fill="#9cc9ea" stroke="currentColor"/>
  <text x="280" y="326" font-size="13" text-anchor="middle" fill="currentColor">area (m²)</text>
  <text x="18" y="160" font-size="13" text-anchor="middle" fill="currentColor" transform="rotate(-90 18 160)">price (thousands)</text>
  <line x1="90" y1="45" x2="120" y2="45" stroke="#eea66f" stroke-width="2.5"/>
  <text x="128" y="49" font-size="12" fill="currentColor">least-squares line −7.59 + 3.797 x</text>
  <line x1="105" y1="62" x2="105" y2="82" stroke="currentColor" stroke-dasharray="3 2"/>
  <text x="128" y="76" font-size="12" fill="currentColor">residual</text>
  <circle cx="105" cy="100" r="5" fill="#9cc9ea" stroke="currentColor"/>
  <text x="128" y="104" font-size="12" fill="currentColor">a flat</text>
</svg>
<figcaption>The least-squares line through the ten flats. Each dashed segment is a residual; the line is the one
that makes the sum of their squares as small as possible.</figcaption>
</figure>

**Why squares?** Not because it is the only sensible choice. Three reasons, from shallow to deep.

1. **Signs cancel otherwise.** Adding raw residuals lets big positive and big negative errors cancel; any line through
   the point of means has residuals summing to zero. Squares, like absolute values, are never negative.
2. **It is easy to solve.** The SSE is a smooth bowl-shaped function of the weights, so its minimum is where the
   derivatives are zero, and those equations are linear: one exact formula gives the answer. Absolute errors have a
   corner at zero and no such formula.
3. **It is right for Gaussian noise.** If the errors come from many small independent causes, so that they are
   roughly Gaussian (section 3.4), then least squares gives the maximum-likelihood line. Section 4.5 proves this.

Squares also have a cost: they punish large errors heavily (an error of 10 counts 100 times as much as an error of 1),
so a single bad point can drag the line towards itself, as set III of Anscombe's quartet showed in Chapter 2.

### A short history

The method was first published by Adrien-Marie Legendre in 1805, in an appendix to a book on computing the orbits of
comets, as a practical way to combine more equations than unknowns. Carl Friedrich Gauss published it in 1809, in
his book on the motion of heavenly bodies, and claimed that he had been using it since 1795. Gauss also gave a
probabilistic justification: he showed that if the best estimate of a quantity measured several times is the average
of the measurements, then the errors must follow the distribution now called Gaussian, and that with Gaussian errors
least squares is the most probable answer, essentially the argument of section 4.5. The priority dispute between the
two was bitter; Stephen Stigler's 1981 paper "Gauss and the Invention of Least Squares" weighs the evidence. The word
"regression" came later, from Francis Galton's 1880s studies of heredity, in which children's heights "regressed"
towards the average compared with their parents'.

### The best line, by hand

To find the minimum, set both partial derivatives to zero (section 3.3: the derivative of a square is 2 times the
inside times the derivative of the inside).

$$
\frac{\partial\,\mathrm{SSE}}{\partial w_0}=-2\sum_i\bigl(y_i-w_0-w_1x_i\bigr)=0,\qquad
\frac{\partial\,\mathrm{SSE}}{\partial w_1}=-2\sum_i\bigl(y_i-w_0-w_1x_i\bigr)x_i=0 .
$$

The first equation says the residuals add up to zero. Dividing it by $n$ gives $\bar y-w_0-w_1\bar x=0$, so

$$
w_0=\bar y-w_1\bar x :
$$

the best line passes through the point of means $(\bar x,\bar y)$. Substitute this into the second equation. Then
$y_i-w_0-w_1x_i=(y_i-\bar y)-w_1(x_i-\bar x)$, and since $\sum_i(y_i-\bar y)-w_1\sum_i(x_i-\bar x)=0$, we may replace the
factor $x_i$ by $x_i-\bar x$ without changing the sum. The equation becomes
$\sum_i(x_i-\bar x)(y_i-\bar y)=w_1\sum_i(x_i-\bar x)^2$. So

$$
w_1=\frac{S_{xy}}{S_{xx}},\qquad S_{xy}=\sum_i(x_i-\bar x)(y_i-\bar y),\quad S_{xx}=\sum_i(x_i-\bar x)^2 .
$$

The slope is the covariation of $x$ and $y$ divided by the variation of $x$. (Section 4.2 shows the point we found
is the minimum, not some other flat point.) Here is the computation, laid out as you would do it on paper; the
program prints the same table.

```python
--8<-- "books/machine-learning/ch04_line_fit.py"
```

Output:

```
mean area 66.4, mean price 244.5
   x      y    x-xbar   y-ybar   product   (x-xbar)^2
   52    210    -14.4    -34.5     496.8      207.4
   75    255      8.6     10.5      90.3       74.0
   40    140    -26.4   -104.5    2758.8      697.0
   98    390     31.6    145.5    4597.8      998.6
   63    240     -3.4     -4.5      15.3       11.6
   75    260      8.6     15.5     133.3       74.0
   45    170    -21.4    -74.5    1594.3      458.0
   88    335     21.6     90.5    1954.8      466.6
   58    230     -8.4    -14.5     121.8       70.6
   70    215      3.6    -29.5    -106.2       13.0
Sxy = 11657.0, Sxx = 3070.4, slope = 3.7966
fitted line: price = -7.592 + 3.7966 * area
normal equations give [-7.5925  3.7966]
residuals [ 20.17 -22.15  -4.27  25.53   8.41 -17.15   6.75   8.49  17.39 -43.17]
sum of residuals 1.99e-13; residuals . area 1.42e-11 (both zero)
SSE 4215.8, SST 48472.5, R^2 = 0.9130, correlation^2 = 0.9130
best constant, squared error: 244.50 (mean 244.5)
best constants, absolute error: from 230.00 to 240.00 (median 235.0)
```

The means are $\bar x=66.4$ and $\bar y=244.5$. Adding the product column gives $S_{xy}=11657.0$, and the squares
column gives $S_{xx}=3070.4$. So $w_1=11657.0/3070.4\approx3.7966$ and $w_0=244.5-3.7966\times66.4\approx-7.592$. The
fitted model is

$$
\widehat{\text{price}}=-7.59+3.797\times\text{area}:
$$

each extra square metre adds about 3.8 thousand to the expected price. For an 80 m² flat it predicts
$-7.592+3.7966\times80\approx296$ thousand. The residuals add up to zero (up to rounding at the level of $10^{-13}$), as the
first equation demanded, and so does their dot product with the areas, as the second demanded.

### Squared versus absolute error, in the simplest case

The very simplest model predicts the same constant $c$ for every flat. Which $c$ is best? For squared error,
$\frac{d}{dc}\sum_i(y_i-c)^2=-2\sum_i(y_i-c)=0$ gives $c=\bar y$: **the mean minimises the squared error**. For absolute
error $\sum_i|y_i-c|$, moving $c$ up by a small amount increases each term with $y_i<c$ and decreases each term with
$y_i>c$, by the same amount, so the total goes down as long as more points lie above $c$ than below. The minimum is
where the points balance, at the median: **the median minimises the absolute error**. With an even number of points,
any value between the two middle ones is a minimum. The program checks both on the ten prices: squared error is best
at 244.5, the mean, and absolute error is best anywhere from 230 to 240, the two middle prices. So least squares is
to least absolute deviations what the mean is to the median: easier to compute, more efficient when errors are
Gaussian, and less robust when they are not.

<figure class="play" data-play="linefit"><span class="ai-tag">AI-created</span><figcaption><b>Try it.</b> Tap to add points, tap a point to remove it: the line is the least-squares fit, and the red lines are the errors whose squares it makes smallest. The starting points are made up.</figcaption></figure>

## 4.2 Solving exactly: the normal equations

The line had two weights. A model with $m$ features has $m+1$ weights, and the same method works, written with the
matrices of Chapter 3.

Put a column of 1s in front of the features to make the **design matrix** $X$, of size $n\times(m+1)$; row $i$ is
$(1,x_{i1},\dots,x_{im})$. With weights $w=(w_0,w_1,\dots,w_m)$, all predictions at once are $\hat y=Xw$, the residuals
are $y-Xw$, and the loss is

$$
\mathrm{SSE}(w)=\lVert y-Xw\rVert^2 .
$$

Section 3.3 computed the gradient of this (divided by $n$): $\nabla\,\mathrm{SSE}(w)=-2X^\top(y-Xw)$. Setting it to zero
gives the **normal equations**:

$$
X^\top X\,w=X^\top y .
$$

They are $m+1$ linear equations in $m+1$ unknowns. When the columns of $X$ are linearly independent, $X^\top X$ has an
inverse (proved below), and the solution is $\hat w=(X^\top X)^{-1}X^\top y$. For one feature, the two normal equations
are exactly the two equations of 4.1, and the program's call `np.linalg.solve(X.T @ X, X.T @ y)` returns the same
$(-7.5925,\,3.7966)$.

Why "normal"? Because the equations say $X^\top(y-X\hat w)=0$: the residual vector has zero dot product with every
column of $X$. It is **normal**, meaning perpendicular, to all of them. That is a statement about geometry, and the
geometry explains everything.

### Least squares as projection

Think of the $n$ prices as one vector $y$ in $n$-dimensional space (here $n=10$). Each column of $X$ is also a vector
in that space. As $w$ ranges over all weight vectors, $Xw$ ranges over all weighted sums of the columns: a flat
subspace through the origin called the **column space** of $X$ (with two columns, a plane). Fitting the model means
choosing the point $Xw$ of the column space closest to $y$. The closest point of a plane to a point outside it is the
foot of the perpendicular. So the best fit $\hat y=X\hat w$ is the **orthogonal projection** of $y$ onto the column
space, and the residual $y-\hat y$ is perpendicular to the plane, which is the normal equations again.

<figure class="mars-fig" markdown="0">
<svg viewBox="0 0 640 290" role="img" aria-label="A tilted plane, the column space of X, containing the two column vectors x1 and x2 from the origin. The data vector y rises out of the plane. Its projection y-hat lies in the plane directly below it; the residual y minus y-hat is a dashed segment perpendicular to the plane, with a right-angle mark. Another point X w of the plane is joined to y by a longer dotted segment.">
  <polygon points="30,215 390,255 610,160 250,120" fill="#9cc9ea" fill-opacity="0.3" stroke="currentColor"/>
  <text x="40" y="262" font-size="13" fill="currentColor">column space of X: every Xw</text>
  <circle cx="240" cy="190" r="3.5" fill="currentColor"/>
  <text x="212" y="206" font-size="13" fill="currentColor">0</text>
  <line x1="240" y1="190" x2="372" y2="210" stroke="currentColor" stroke-width="2"/>
  <polygon points="380,211 369,205 368,215" fill="currentColor"/>
  <text x="352" y="230" font-size="13" fill="currentColor">x1 (column 1)</text>
  <line x1="240" y1="190" x2="312" y2="146" stroke="currentColor" stroke-width="2"/>
  <polygon points="318,142 307,144 312,152" fill="currentColor"/>
  <text x="262" y="140" font-size="13" fill="currentColor">x2</text>
  <line x1="240" y1="190" x2="446" y2="38" stroke="#eea66f" stroke-width="2.5"/>
  <polygon points="452,34 440,36 446,45" fill="#eea66f"/>
  <text x="462" y="36" font-size="14" fill="currentColor">y (the data)</text>
  <line x1="240" y1="190" x2="444" y2="172" stroke="#7ccf9a" stroke-width="2.5"/>
  <circle cx="450" cy="172" r="5" fill="#7ccf9a" stroke="currentColor"/>
  <text x="462" y="186" font-size="14" fill="currentColor">ŷ = X ŵ</text>
  <line x1="450" y1="40" x2="450" y2="166" stroke="currentColor" stroke-width="1.5" stroke-dasharray="6 4"/>
  <path d="M 450 156 L 460 155 L 460 165" fill="none" stroke="currentColor"/>
  <text x="458" y="110" font-size="13" fill="currentColor">residual y − ŷ,</text>
  <text x="458" y="127" font-size="13" fill="currentColor">perpendicular to the plane</text>
  <circle cx="360" cy="185" r="4" fill="currentColor"/>
  <text x="318" y="178" font-size="12" fill="currentColor">Xw</text>
  <line x1="360" y1="185" x2="448" y2="42" stroke="currentColor" stroke-dasharray="2 3"/>
  <text x="60" y="60" font-size="13" fill="currentColor">‖y − Xw‖² = ‖y − ŷ‖² + ‖ŷ − Xw‖²</text>
  <text x="60" y="80" font-size="13" fill="currentColor">so every other Xw is farther from y</text>
</svg>
<figcaption>Least squares as projection. The best fit ŷ is the foot of the perpendicular from y to the column space.
By Pythagoras, any other point Xw of the plane is farther from y.</figcaption>
</figure>

This picture gives a proof that needs no calculus and shows the solution is the *global* minimum, not just a flat
point.

**Theorem.** If $\hat w$ satisfies the normal equations, then $\lVert y-X\hat w\rVert^2\le\lVert y-Xw\rVert^2$ for every
$w$. If the columns of $X$ are linearly independent, $\hat w$ is the only minimiser.

**Proof.** For any $w$, write $y-Xw=(y-X\hat w)+X(\hat w-w)$. The first part is the residual $r$ of $\hat w$; the
second is $Xd$ with $d=\hat w-w$. Their dot product is $(Xd)^\top r=d^\top X^\top r=0$ by the normal equations. So by
Pythagoras (expand the square; the cross term vanishes),

$$
\lVert y-Xw\rVert^2=\lVert r\rVert^2+\lVert Xd\rVert^2\ge\lVert r\rVert^2 .
$$

Equality holds exactly when $Xd=0$. If the columns are independent, the only weighted sum of them that gives the zero
vector is the one with all weights zero, so $d=0$ and $w=\hat w$. $\square$

**Corollary.** With independent columns, $X^\top X$ is invertible. *Proof:* if $X^\top Xd=0$, then
$\lVert Xd\rVert^2=d^\top X^\top Xd=0$, so $Xd=0$, so $d=0$; a square matrix whose only null vector is 0 is invertible.
$\square$ And when the columns are *dependent*, as with the dummy-variable trap of Chapter 2, there are infinitely
many minimisers $\hat w+d$ with $Xd=0$, all giving the same predictions. Section 4.7 shows how to pick a sensible one.

Two more facts fall out. Because the column of 1s is one of the columns, $\mathbf 1^\top r=0$: **with an intercept,
residuals always add up to zero**. And the predictions themselves, $\hat y=X(X^\top X)^{-1}X^\top y$, are the result of
applying the matrix $P=X(X^\top X)^{-1}X^\top$ to $y$; statisticians call it the **hat matrix**, because it puts the hat
on $y$. Projecting twice is the same as projecting once, $P^2=P$, which you can check from the formula.

## 4.3 Many features; the design matrix; polynomial features

What changes with more features? Only the size of $X$. Here is price fitted to area *and* rooms, and then a curve
fitted with powers of $x$.

```python
--8<-- "books/machine-learning/ch04_many_features.py"
```

Output:

```
price = -7.57 + 4.122 area - 8.49 rooms
X^T r = [0. 0. 0.] (the residual is orthogonal to every column)
rooms alone: price = 67.23 + 69.52 rooms
correlation of area and rooms: 0.852

degree  train RMSE  RMSE vs truth on a fine grid
     0      0.6106        0.7460
     1      0.4359        0.4986
     3      0.2218        0.1028
     5      0.1982        0.0845
     9      0.1666        0.2429
    14      0.0003     4422.2255
```

### Two features

The design matrix has three columns (ones, area, rooms), and the fit is

$$
\widehat{\text{price}}=-7.57+4.122\times\text{area}-8.49\times\text{rooms}.
$$

The rooms weight is *negative*. Does an extra room lower the price? Fitted on its own, rooms has a large positive
weight, 69.52 per room. The two answers are both right, to different questions. Alone, "rooms" stands in for size:
flats with more rooms are bigger and cost more. Together with area, the rooms weight answers "for two flats *of the
same area*, how does an extra room change the price?", and with the same floor space, more rooms means smaller rooms,
which (in this tiny made-up table) buyers value slightly less. Section 4.6 returns to this, and to the warning that
with ten flats and two features correlated at 0.852 the value $-8.49$ is very uncertain.

The orthogonality check prints $X^\top r=0$: the residual is perpendicular to all three columns, exactly as the
geometry says.

### Polynomial features

A straight line cannot follow a curve. But "linear regression" means linear *in the weights*, not in the inputs. We
may put any fixed functions of $x$ into the columns of $X$, for instance the powers $1,x,x^2,\dots,x^d$:

$$
\hat y=w_0+w_1x+w_2x^2+\dots+w_dx^d .
$$

The model is a polynomial of degree $d$ in $x$, but it is still a linear combination of columns, so everything in 4.2
applies unchanged. These columns are **polynomial features**, a case of the feature engineering of Chapter 2.

The program draws 15 points from the curve $\sin(2\pi x)$ plus Gaussian noise of standard deviation 0.2, and fits
polynomials of several degrees. It reports two errors: the **root mean squared error** (RMSE, the square root of the
MSE, in the same units as $y$) on the 15 training points, and the RMSE against the true noise-free curve on a fine grid,
which measures how well the model has captured the real pattern.

<figure class="mars-fig" markdown="0">
<svg viewBox="0 0 640 280" role="img" aria-label="Fifteen noisy points from a sine wave over x from 0 to 1, with the true sine curve dashed. A green straight line, the degree 1 fit, misses the wave. An orange degree 3 fit follows the wave closely. A blue degree 9 fit wiggles to pass near every point, bending away from the true curve between them.">
  <line x1="60" y1="140" x2="460" y2="140" stroke="currentColor" stroke-opacity="0.4"/>
  <line x1="60" y1="30" x2="60" y2="250" stroke="currentColor"/>
  <line x1="60" y1="250" x2="460" y2="250" stroke="currentColor"/>
  <text x="54" y="254" font-size="11" text-anchor="end" fill="currentColor">-2</text>
  <text x="54" y="199" font-size="11" text-anchor="end" fill="currentColor">-1</text>
  <text x="54" y="144" font-size="11" text-anchor="end" fill="currentColor">0</text>
  <text x="54" y="89" font-size="11" text-anchor="end" fill="currentColor">1</text>
  <text x="54" y="34" font-size="11" text-anchor="end" fill="currentColor">2</text>
  <text x="60" y="266" font-size="11" text-anchor="middle" fill="currentColor">0</text>
  <text x="260" y="266" font-size="11" text-anchor="middle" fill="currentColor">0.5</text>
  <text x="460" y="266" font-size="11" text-anchor="middle" fill="currentColor">1</text>
  <path d="M 60.0 140.0 L 61.3 138.8 L 62.7 137.7 L 64.0 136.5 L 65.4 135.4 L 66.7 134.2 L 68.0 133.1 L 69.4 131.9 L 70.7 130.8 L 72.0 129.7 L 73.4 128.5 L 74.7 127.4 L 76.1 126.3 L 77.4 125.2 L 78.7 124.1 L 80.1 122.9 L 81.4 121.9 L 82.7 120.8 L 84.1 119.7 L 85.4 118.6 L 86.8 117.6 L 88.1 116.5 L 89.4 115.5 L 90.8 114.4 L 92.1 113.4 L 93.4 112.4 L 94.8 111.4 L 96.1 110.4 L 97.5 109.5 L 98.8 108.5 L 100.1 107.6 L 101.5 106.7 L 102.8 105.7 L 104.1 104.8 L 105.5 104.0 L 106.8 103.1 L 108.2 102.2 L 109.5 101.4 L 110.8 100.6 L 112.2 99.8 L 113.5 99.0 L 114.8 98.3 L 116.2 97.5 L 117.5 96.8 L 118.9 96.1 L 120.2 95.4 L 121.5 94.7 L 122.9 94.1 L 124.2 93.5 L 125.6 92.9 L 126.9 92.3 L 128.2 91.7 L 129.6 91.2 L 130.9 90.6 L 132.2 90.1 L 133.6 89.7 L 134.9 89.2 L 136.3 88.8 L 137.6 88.4 L 138.9 88.0 L 140.3 87.6 L 141.6 87.3 L 142.9 87.0 L 144.3 86.7 L 145.6 86.4 L 147.0 86.2 L 148.3 85.9 L 149.6 85.7 L 151.0 85.6 L 152.3 85.4 L 153.6 85.3 L 155.0 85.2 L 156.3 85.1 L 157.7 85.0 L 159.0 85.0 L 160.3 85.0 L 161.7 85.0 L 163.0 85.1 L 164.3 85.1 L 165.7 85.2 L 167.0 85.3 L 168.4 85.5 L 169.7 85.6 L 171.0 85.8 L 172.4 86.0 L 173.7 86.3 L 175.1 86.5 L 176.4 86.8 L 177.7 87.1 L 179.1 87.4 L 180.4 87.8 L 181.7 88.2 L 183.1 88.6 L 184.4 89.0 L 185.8 89.4 L 187.1 89.9 L 188.4 90.4 L 189.8 90.9 L 191.1 91.4 L 192.4 92.0 L 193.8 92.6 L 195.1 93.2 L 196.5 93.8 L 197.8 94.4 L 199.1 95.1 L 200.5 95.7 L 201.8 96.4 L 203.1 97.2 L 204.5 97.9 L 205.8 98.6 L 207.2 99.4 L 208.5 100.2 L 209.8 101.0 L 211.2 101.8 L 212.5 102.7 L 213.8 103.5 L 215.2 104.4 L 216.5 105.3 L 217.9 106.2 L 219.2 107.1 L 220.5 108.0 L 221.9 109.0 L 223.2 110.0 L 224.5 110.9 L 225.9 111.9 L 227.2 112.9 L 228.6 113.9 L 229.9 115.0 L 231.2 116.0 L 232.6 117.0 L 233.9 118.1 L 235.3 119.2 L 236.6 120.2 L 237.9 121.3 L 239.3 122.4 L 240.6 123.5 L 241.9 124.6 L 243.3 125.7 L 244.6 126.8 L 246.0 128.0 L 247.3 129.1 L 248.6 130.2 L 250.0 131.4 L 251.3 132.5 L 252.6 133.7 L 254.0 134.8 L 255.3 136.0 L 256.7 137.1 L 258.0 138.3 L 259.3 139.4 L 260.7 140.6 L 262.0 141.7 L 263.3 142.9 L 264.7 144.0 L 266.0 145.2 L 267.4 146.3 L 268.7 147.5 L 270.0 148.6 L 271.4 149.8 L 272.7 150.9 L 274.0 152.0 L 275.4 153.2 L 276.7 154.3 L 278.1 155.4 L 279.4 156.5 L 280.7 157.6 L 282.1 158.7 L 283.4 159.8 L 284.7 160.8 L 286.1 161.9 L 287.4 163.0 L 288.8 164.0 L 290.1 165.0 L 291.4 166.1 L 292.8 167.1 L 294.1 168.1 L 295.5 169.1 L 296.8 170.0 L 298.1 171.0 L 299.5 172.0 L 300.8 172.9 L 302.1 173.8 L 303.5 174.7 L 304.8 175.6 L 306.2 176.5 L 307.5 177.3 L 308.8 178.2 L 310.2 179.0 L 311.5 179.8 L 312.8 180.6 L 314.2 181.4 L 315.5 182.1 L 316.9 182.8 L 318.2 183.6 L 319.5 184.3 L 320.9 184.9 L 322.2 185.6 L 323.5 186.2 L 324.9 186.8 L 326.2 187.4 L 327.6 188.0 L 328.9 188.6 L 330.2 189.1 L 331.6 189.6 L 332.9 190.1 L 334.2 190.6 L 335.6 191.0 L 336.9 191.4 L 338.3 191.8 L 339.6 192.2 L 340.9 192.6 L 342.3 192.9 L 343.6 193.2 L 344.9 193.5 L 346.3 193.7 L 347.6 194.0 L 349.0 194.2 L 350.3 194.4 L 351.6 194.5 L 353.0 194.7 L 354.3 194.8 L 355.7 194.9 L 357.0 194.9 L 358.3 195.0 L 359.7 195.0 L 361.0 195.0 L 362.3 195.0 L 363.7 194.9 L 365.0 194.8 L 366.4 194.7 L 367.7 194.6 L 369.0 194.4 L 370.4 194.3 L 371.7 194.1 L 373.0 193.8 L 374.4 193.6 L 375.7 193.3 L 377.1 193.0 L 378.4 192.7 L 379.7 192.4 L 381.1 192.0 L 382.4 191.6 L 383.7 191.2 L 385.1 190.8 L 386.4 190.3 L 387.8 189.9 L 389.1 189.4 L 390.4 188.8 L 391.8 188.3 L 393.1 187.7 L 394.4 187.1 L 395.8 186.5 L 397.1 185.9 L 398.5 185.3 L 399.8 184.6 L 401.1 183.9 L 402.5 183.2 L 403.8 182.5 L 405.2 181.7 L 406.5 181.0 L 407.8 180.2 L 409.2 179.4 L 410.5 178.6 L 411.8 177.8 L 413.2 176.9 L 414.5 176.0 L 415.9 175.2 L 417.2 174.3 L 418.5 173.3 L 419.9 172.4 L 421.2 171.5 L 422.5 170.5 L 423.9 169.6 L 425.2 168.6 L 426.6 167.6 L 427.9 166.6 L 429.2 165.6 L 430.6 164.5 L 431.9 163.5 L 433.2 162.4 L 434.6 161.4 L 435.9 160.3 L 437.3 159.2 L 438.6 158.1 L 439.9 157.1 L 441.3 155.9 L 442.6 154.8 L 443.9 153.7 L 445.3 152.6 L 446.6 151.5 L 448.0 150.3 L 449.3 149.2 L 450.6 148.1 L 452.0 146.9 L 453.3 145.8 L 454.6 144.6 L 456.0 143.5 L 457.3 142.3 L 458.7 141.2 L 460.0 140.0" fill="none" stroke="currentColor" stroke-dasharray="5 4" stroke-opacity="0.7"/>
  <path d="M 60.0 112.3 L 61.3 112.6 L 62.7 112.8 L 64.0 113.0 L 65.4 113.3 L 66.7 113.5 L 68.0 113.7 L 69.4 114.0 L 70.7 114.2 L 72.0 114.5 L 73.4 114.7 L 74.7 114.9 L 76.1 115.2 L 77.4 115.4 L 78.7 115.6 L 80.1 115.9 L 81.4 116.1 L 82.7 116.3 L 84.1 116.6 L 85.4 116.8 L 86.8 117.0 L 88.1 117.3 L 89.4 117.5 L 90.8 117.7 L 92.1 118.0 L 93.4 118.2 L 94.8 118.4 L 96.1 118.7 L 97.5 118.9 L 98.8 119.1 L 100.1 119.4 L 101.5 119.6 L 102.8 119.8 L 104.1 120.1 L 105.5 120.3 L 106.8 120.5 L 108.2 120.8 L 109.5 121.0 L 110.8 121.2 L 112.2 121.5 L 113.5 121.7 L 114.8 122.0 L 116.2 122.2 L 117.5 122.4 L 118.9 122.7 L 120.2 122.9 L 121.5 123.1 L 122.9 123.4 L 124.2 123.6 L 125.6 123.8 L 126.9 124.1 L 128.2 124.3 L 129.6 124.5 L 130.9 124.8 L 132.2 125.0 L 133.6 125.2 L 134.9 125.5 L 136.3 125.7 L 137.6 125.9 L 138.9 126.2 L 140.3 126.4 L 141.6 126.6 L 142.9 126.9 L 144.3 127.1 L 145.6 127.3 L 147.0 127.6 L 148.3 127.8 L 149.6 128.0 L 151.0 128.3 L 152.3 128.5 L 153.6 128.7 L 155.0 129.0 L 156.3 129.2 L 157.7 129.4 L 159.0 129.7 L 160.3 129.9 L 161.7 130.2 L 163.0 130.4 L 164.3 130.6 L 165.7 130.9 L 167.0 131.1 L 168.4 131.3 L 169.7 131.6 L 171.0 131.8 L 172.4 132.0 L 173.7 132.3 L 175.1 132.5 L 176.4 132.7 L 177.7 133.0 L 179.1 133.2 L 180.4 133.4 L 181.7 133.7 L 183.1 133.9 L 184.4 134.1 L 185.8 134.4 L 187.1 134.6 L 188.4 134.8 L 189.8 135.1 L 191.1 135.3 L 192.4 135.5 L 193.8 135.8 L 195.1 136.0 L 196.5 136.2 L 197.8 136.5 L 199.1 136.7 L 200.5 136.9 L 201.8 137.2 L 203.1 137.4 L 204.5 137.7 L 205.8 137.9 L 207.2 138.1 L 208.5 138.4 L 209.8 138.6 L 211.2 138.8 L 212.5 139.1 L 213.8 139.3 L 215.2 139.5 L 216.5 139.8 L 217.9 140.0 L 219.2 140.2 L 220.5 140.5 L 221.9 140.7 L 223.2 140.9 L 224.5 141.2 L 225.9 141.4 L 227.2 141.6 L 228.6 141.9 L 229.9 142.1 L 231.2 142.3 L 232.6 142.6 L 233.9 142.8 L 235.3 143.0 L 236.6 143.3 L 237.9 143.5 L 239.3 143.7 L 240.6 144.0 L 241.9 144.2 L 243.3 144.4 L 244.6 144.7 L 246.0 144.9 L 247.3 145.2 L 248.6 145.4 L 250.0 145.6 L 251.3 145.9 L 252.6 146.1 L 254.0 146.3 L 255.3 146.6 L 256.7 146.8 L 258.0 147.0 L 259.3 147.3 L 260.7 147.5 L 262.0 147.7 L 263.3 148.0 L 264.7 148.2 L 266.0 148.4 L 267.4 148.7 L 268.7 148.9 L 270.0 149.1 L 271.4 149.4 L 272.7 149.6 L 274.0 149.8 L 275.4 150.1 L 276.7 150.3 L 278.1 150.5 L 279.4 150.8 L 280.7 151.0 L 282.1 151.2 L 283.4 151.5 L 284.7 151.7 L 286.1 151.9 L 287.4 152.2 L 288.8 152.4 L 290.1 152.7 L 291.4 152.9 L 292.8 153.1 L 294.1 153.4 L 295.5 153.6 L 296.8 153.8 L 298.1 154.1 L 299.5 154.3 L 300.8 154.5 L 302.1 154.8 L 303.5 155.0 L 304.8 155.2 L 306.2 155.5 L 307.5 155.7 L 308.8 155.9 L 310.2 156.2 L 311.5 156.4 L 312.8 156.6 L 314.2 156.9 L 315.5 157.1 L 316.9 157.3 L 318.2 157.6 L 319.5 157.8 L 320.9 158.0 L 322.2 158.3 L 323.5 158.5 L 324.9 158.7 L 326.2 159.0 L 327.6 159.2 L 328.9 159.4 L 330.2 159.7 L 331.6 159.9 L 332.9 160.2 L 334.2 160.4 L 335.6 160.6 L 336.9 160.9 L 338.3 161.1 L 339.6 161.3 L 340.9 161.6 L 342.3 161.8 L 343.6 162.0 L 344.9 162.3 L 346.3 162.5 L 347.6 162.7 L 349.0 163.0 L 350.3 163.2 L 351.6 163.4 L 353.0 163.7 L 354.3 163.9 L 355.7 164.1 L 357.0 164.4 L 358.3 164.6 L 359.7 164.8 L 361.0 165.1 L 362.3 165.3 L 363.7 165.5 L 365.0 165.8 L 366.4 166.0 L 367.7 166.2 L 369.0 166.5 L 370.4 166.7 L 371.7 166.9 L 373.0 167.2 L 374.4 167.4 L 375.7 167.6 L 377.1 167.9 L 378.4 168.1 L 379.7 168.4 L 381.1 168.6 L 382.4 168.8 L 383.7 169.1 L 385.1 169.3 L 386.4 169.5 L 387.8 169.8 L 389.1 170.0 L 390.4 170.2 L 391.8 170.5 L 393.1 170.7 L 394.4 170.9 L 395.8 171.2 L 397.1 171.4 L 398.5 171.6 L 399.8 171.9 L 401.1 172.1 L 402.5 172.3 L 403.8 172.6 L 405.2 172.8 L 406.5 173.0 L 407.8 173.3 L 409.2 173.5 L 410.5 173.7 L 411.8 174.0 L 413.2 174.2 L 414.5 174.4 L 415.9 174.7 L 417.2 174.9 L 418.5 175.1 L 419.9 175.4 L 421.2 175.6 L 422.5 175.9 L 423.9 176.1 L 425.2 176.3 L 426.6 176.6 L 427.9 176.8 L 429.2 177.0 L 430.6 177.3 L 431.9 177.5 L 433.2 177.7 L 434.6 178.0 L 435.9 178.2 L 437.3 178.4 L 438.6 178.7 L 439.9 178.9 L 441.3 179.1 L 442.6 179.4 L 443.9 179.6 L 445.3 179.8 L 446.6 180.1 L 448.0 180.3 L 449.3 180.5 L 450.6 180.8 L 452.0 181.0 L 453.3 181.2 L 454.6 181.5 L 456.0 181.7 L 457.3 181.9 L 458.7 182.2 L 460.0 182.4" fill="none" stroke="#7ccf9a" stroke-width="2.5"/>
  <path d="M 60.0 141.4 L 61.3 139.5 L 62.7 137.6 L 64.0 135.8 L 65.4 134.0 L 66.7 132.2 L 68.0 130.5 L 69.4 128.9 L 70.7 127.2 L 72.0 125.6 L 73.4 124.0 L 74.7 122.5 L 76.1 121.0 L 77.4 119.5 L 78.7 118.1 L 80.1 116.7 L 81.4 115.3 L 82.7 114.0 L 84.1 112.7 L 85.4 111.5 L 86.8 110.2 L 88.1 109.0 L 89.4 107.9 L 90.8 106.7 L 92.1 105.6 L 93.4 104.6 L 94.8 103.5 L 96.1 102.5 L 97.5 101.5 L 98.8 100.6 L 100.1 99.7 L 101.5 98.8 L 102.8 97.9 L 104.1 97.1 L 105.5 96.3 L 106.8 95.5 L 108.2 94.8 L 109.5 94.1 L 110.8 93.4 L 112.2 92.7 L 113.5 92.1 L 114.8 91.5 L 116.2 91.0 L 117.5 90.4 L 118.9 89.9 L 120.2 89.4 L 121.5 88.9 L 122.9 88.5 L 124.2 88.1 L 125.6 87.7 L 126.9 87.3 L 128.2 87.0 L 129.6 86.7 L 130.9 86.4 L 132.2 86.1 L 133.6 85.9 L 134.9 85.7 L 136.3 85.5 L 137.6 85.3 L 138.9 85.2 L 140.3 85.1 L 141.6 85.0 L 142.9 84.9 L 144.3 84.8 L 145.6 84.8 L 147.0 84.8 L 148.3 84.8 L 149.6 84.8 L 151.0 84.9 L 152.3 85.0 L 153.6 85.1 L 155.0 85.2 L 156.3 85.3 L 157.7 85.5 L 159.0 85.6 L 160.3 85.8 L 161.7 86.0 L 163.0 86.3 L 164.3 86.5 L 165.7 86.8 L 167.0 87.1 L 168.4 87.4 L 169.7 87.7 L 171.0 88.0 L 172.4 88.4 L 173.7 88.7 L 175.1 89.1 L 176.4 89.5 L 177.7 89.9 L 179.1 90.4 L 180.4 90.8 L 181.7 91.3 L 183.1 91.8 L 184.4 92.3 L 185.8 92.8 L 187.1 93.3 L 188.4 93.8 L 189.8 94.4 L 191.1 94.9 L 192.4 95.5 L 193.8 96.1 L 195.1 96.7 L 196.5 97.3 L 197.8 98.0 L 199.1 98.6 L 200.5 99.2 L 201.8 99.9 L 203.1 100.6 L 204.5 101.3 L 205.8 102.0 L 207.2 102.7 L 208.5 103.4 L 209.8 104.1 L 211.2 104.8 L 212.5 105.6 L 213.8 106.3 L 215.2 107.1 L 216.5 107.9 L 217.9 108.6 L 219.2 109.4 L 220.5 110.2 L 221.9 111.0 L 223.2 111.8 L 224.5 112.6 L 225.9 113.5 L 227.2 114.3 L 228.6 115.1 L 229.9 116.0 L 231.2 116.8 L 232.6 117.7 L 233.9 118.5 L 235.3 119.4 L 236.6 120.3 L 237.9 121.2 L 239.3 122.0 L 240.6 122.9 L 241.9 123.8 L 243.3 124.7 L 244.6 125.6 L 246.0 126.5 L 247.3 127.4 L 248.6 128.3 L 250.0 129.2 L 251.3 130.1 L 252.6 131.0 L 254.0 131.9 L 255.3 132.8 L 256.7 133.8 L 258.0 134.7 L 259.3 135.6 L 260.7 136.5 L 262.0 137.4 L 263.3 138.3 L 264.7 139.3 L 266.0 140.2 L 267.4 141.1 L 268.7 142.0 L 270.0 142.9 L 271.4 143.8 L 272.7 144.7 L 274.0 145.6 L 275.4 146.6 L 276.7 147.5 L 278.1 148.4 L 279.4 149.2 L 280.7 150.1 L 282.1 151.0 L 283.4 151.9 L 284.7 152.8 L 286.1 153.7 L 287.4 154.5 L 288.8 155.4 L 290.1 156.3 L 291.4 157.1 L 292.8 158.0 L 294.1 158.8 L 295.5 159.7 L 296.8 160.5 L 298.1 161.3 L 299.5 162.2 L 300.8 163.0 L 302.1 163.8 L 303.5 164.6 L 304.8 165.4 L 306.2 166.2 L 307.5 166.9 L 308.8 167.7 L 310.2 168.4 L 311.5 169.2 L 312.8 169.9 L 314.2 170.7 L 315.5 171.4 L 316.9 172.1 L 318.2 172.8 L 319.5 173.5 L 320.9 174.2 L 322.2 174.8 L 323.5 175.5 L 324.9 176.1 L 326.2 176.8 L 327.6 177.4 L 328.9 178.0 L 330.2 178.6 L 331.6 179.2 L 332.9 179.7 L 334.2 180.3 L 335.6 180.8 L 336.9 181.4 L 338.3 181.9 L 339.6 182.4 L 340.9 182.9 L 342.3 183.3 L 343.6 183.8 L 344.9 184.2 L 346.3 184.7 L 347.6 185.1 L 349.0 185.5 L 350.3 185.8 L 351.6 186.2 L 353.0 186.6 L 354.3 186.9 L 355.7 187.2 L 357.0 187.5 L 358.3 187.8 L 359.7 188.0 L 361.0 188.3 L 362.3 188.5 L 363.7 188.7 L 365.0 188.9 L 366.4 189.0 L 367.7 189.2 L 369.0 189.3 L 370.4 189.4 L 371.7 189.5 L 373.0 189.5 L 374.4 189.6 L 375.7 189.6 L 377.1 189.6 L 378.4 189.6 L 379.7 189.5 L 381.1 189.5 L 382.4 189.4 L 383.7 189.3 L 385.1 189.1 L 386.4 189.0 L 387.8 188.8 L 389.1 188.6 L 390.4 188.4 L 391.8 188.1 L 393.1 187.9 L 394.4 187.6 L 395.8 187.2 L 397.1 186.9 L 398.5 186.5 L 399.8 186.1 L 401.1 185.7 L 402.5 185.2 L 403.8 184.8 L 405.2 184.2 L 406.5 183.7 L 407.8 183.2 L 409.2 182.6 L 410.5 182.0 L 411.8 181.3 L 413.2 180.7 L 414.5 180.0 L 415.9 179.2 L 417.2 178.5 L 418.5 177.7 L 419.9 176.9 L 421.2 176.0 L 422.5 175.2 L 423.9 174.3 L 425.2 173.3 L 426.6 172.4 L 427.9 171.4 L 429.2 170.4 L 430.6 169.3 L 431.9 168.2 L 433.2 167.1 L 434.6 166.0 L 435.9 164.8 L 437.3 163.6 L 438.6 162.3 L 439.9 161.0 L 441.3 159.7 L 442.6 158.4 L 443.9 157.0 L 445.3 155.6 L 446.6 154.1 L 448.0 152.6 L 449.3 151.1 L 450.6 149.6 L 452.0 148.0 L 453.3 146.4 L 454.6 144.7 L 456.0 143.0 L 457.3 141.3 L 458.7 139.5 L 460.0 137.7" fill="none" stroke="#eea66f" stroke-width="2.5"/>
  <path d="M 60.0 129.1 L 61.3 133.2 L 62.7 136.2 L 64.0 138.2 L 65.4 139.4 L 66.7 139.8 L 68.0 139.5 L 69.4 138.7 L 70.7 137.3 L 72.0 135.5 L 73.4 133.3 L 74.7 130.8 L 76.1 128.1 L 77.4 125.1 L 78.7 121.9 L 80.1 118.6 L 81.4 115.2 L 82.7 111.8 L 84.1 108.4 L 85.4 104.9 L 86.8 101.5 L 88.1 98.1 L 89.4 94.8 L 90.8 91.7 L 92.1 88.6 L 93.4 85.6 L 94.8 82.8 L 96.1 80.1 L 97.5 77.5 L 98.8 75.2 L 100.1 72.9 L 101.5 70.9 L 102.8 69.0 L 104.1 67.3 L 105.5 65.7 L 106.8 64.3 L 108.2 63.1 L 109.5 62.0 L 110.8 61.1 L 112.2 60.4 L 113.5 59.8 L 114.8 59.3 L 116.2 59.0 L 117.5 58.8 L 118.9 58.7 L 120.2 58.8 L 121.5 58.9 L 122.9 59.2 L 124.2 59.6 L 125.6 60.1 L 126.9 60.6 L 128.2 61.2 L 129.6 61.9 L 130.9 62.7 L 132.2 63.5 L 133.6 64.4 L 134.9 65.3 L 136.3 66.3 L 137.6 67.3 L 138.9 68.3 L 140.3 69.3 L 141.6 70.4 L 142.9 71.4 L 144.3 72.5 L 145.6 73.6 L 147.0 74.6 L 148.3 75.7 L 149.6 76.7 L 151.0 77.8 L 152.3 78.8 L 153.6 79.8 L 155.0 80.7 L 156.3 81.7 L 157.7 82.6 L 159.0 83.5 L 160.3 84.3 L 161.7 85.1 L 163.0 85.9 L 164.3 86.7 L 165.7 87.4 L 167.0 88.1 L 168.4 88.7 L 169.7 89.3 L 171.0 89.9 L 172.4 90.4 L 173.7 90.9 L 175.1 91.4 L 176.4 91.8 L 177.7 92.2 L 179.1 92.6 L 180.4 93.0 L 181.7 93.3 L 183.1 93.6 L 184.4 93.9 L 185.8 94.1 L 187.1 94.4 L 188.4 94.6 L 189.8 94.8 L 191.1 95.0 L 192.4 95.2 L 193.8 95.4 L 195.1 95.6 L 196.5 95.7 L 197.8 95.9 L 199.1 96.1 L 200.5 96.3 L 201.8 96.5 L 203.1 96.7 L 204.5 96.9 L 205.8 97.2 L 207.2 97.4 L 208.5 97.7 L 209.8 98.0 L 211.2 98.3 L 212.5 98.7 L 213.8 99.0 L 215.2 99.4 L 216.5 99.9 L 217.9 100.3 L 219.2 100.8 L 220.5 101.4 L 221.9 101.9 L 223.2 102.5 L 224.5 103.2 L 225.9 103.9 L 227.2 104.6 L 228.6 105.3 L 229.9 106.1 L 231.2 107.0 L 232.6 107.9 L 233.9 108.8 L 235.3 109.8 L 236.6 110.8 L 237.9 111.8 L 239.3 112.9 L 240.6 114.1 L 241.9 115.2 L 243.3 116.4 L 244.6 117.7 L 246.0 119.0 L 247.3 120.3 L 248.6 121.6 L 250.0 123.0 L 251.3 124.4 L 252.6 125.9 L 254.0 127.4 L 255.3 128.9 L 256.7 130.4 L 258.0 132.0 L 259.3 133.5 L 260.7 135.1 L 262.0 136.7 L 263.3 138.4 L 264.7 140.0 L 266.0 141.6 L 267.4 143.3 L 268.7 145.0 L 270.0 146.6 L 271.4 148.3 L 272.7 150.0 L 274.0 151.6 L 275.4 153.3 L 276.7 154.9 L 278.1 156.6 L 279.4 158.2 L 280.7 159.8 L 282.1 161.4 L 283.4 163.0 L 284.7 164.6 L 286.1 166.1 L 287.4 167.6 L 288.8 169.1 L 290.1 170.6 L 291.4 172.0 L 292.8 173.4 L 294.1 174.7 L 295.5 176.0 L 296.8 177.3 L 298.1 178.6 L 299.5 179.8 L 300.8 180.9 L 302.1 182.1 L 303.5 183.1 L 304.8 184.2 L 306.2 185.2 L 307.5 186.1 L 308.8 187.0 L 310.2 187.8 L 311.5 188.6 L 312.8 189.4 L 314.2 190.1 L 315.5 190.7 L 316.9 191.3 L 318.2 191.9 L 319.5 192.4 L 320.9 192.9 L 322.2 193.3 L 323.5 193.6 L 324.9 194.0 L 326.2 194.2 L 327.6 194.5 L 328.9 194.7 L 330.2 194.8 L 331.6 194.9 L 332.9 195.0 L 334.2 195.0 L 335.6 195.0 L 336.9 195.0 L 338.3 194.9 L 339.6 194.8 L 340.9 194.6 L 342.3 194.5 L 343.6 194.3 L 344.9 194.0 L 346.3 193.8 L 347.6 193.5 L 349.0 193.2 L 350.3 192.9 L 351.6 192.6 L 353.0 192.3 L 354.3 191.9 L 355.7 191.6 L 357.0 191.2 L 358.3 190.8 L 359.7 190.5 L 361.0 190.1 L 362.3 189.7 L 363.7 189.3 L 365.0 188.9 L 366.4 188.5 L 367.7 188.1 L 369.0 187.7 L 370.4 187.4 L 371.7 187.0 L 373.0 186.6 L 374.4 186.3 L 375.7 185.9 L 377.1 185.6 L 378.4 185.2 L 379.7 184.9 L 381.1 184.6 L 382.4 184.2 L 383.7 183.9 L 385.1 183.6 L 386.4 183.3 L 387.8 183.0 L 389.1 182.7 L 390.4 182.4 L 391.8 182.1 L 393.1 181.8 L 394.4 181.5 L 395.8 181.2 L 397.1 180.9 L 398.5 180.6 L 399.8 180.2 L 401.1 179.9 L 402.5 179.5 L 403.8 179.2 L 405.2 178.8 L 406.5 178.3 L 407.8 177.9 L 409.2 177.4 L 410.5 176.9 L 411.8 176.4 L 413.2 175.9 L 414.5 175.3 L 415.9 174.7 L 417.2 174.0 L 418.5 173.3 L 419.9 172.6 L 421.2 171.8 L 422.5 171.1 L 423.9 170.2 L 425.2 169.4 L 426.6 168.5 L 427.9 167.6 L 429.2 166.7 L 430.6 165.7 L 431.9 164.8 L 433.2 163.8 L 434.6 162.9 L 435.9 161.9 L 437.3 161.0 L 438.6 160.1 L 439.9 159.3 L 441.3 158.6 L 442.6 157.9 L 443.9 157.3 L 445.3 156.9 L 446.6 156.6 L 448.0 156.5 L 449.3 156.6 L 450.6 156.9 L 452.0 157.5 L 453.3 158.4 L 454.6 159.6 L 456.0 161.3 L 457.3 163.3 L 458.7 165.9 L 460.0 168.9" fill="none" stroke="#9cc9ea" stroke-width="2.5"/>
  <circle cx="62.3" cy="135.0" r="4.5" fill="currentColor"/>
  <circle cx="70.6" cy="138.1" r="4.5" fill="currentColor"/>
  <circle cx="86.1" cy="102.8" r="4.5" fill="currentColor"/>
  <circle cx="174.7" cy="92.0" r="4.5" fill="currentColor"/>
  <circle cx="234.9" cy="101.6" r="4.5" fill="currentColor"/>
  <circle cx="254.0" cy="139.2" r="4.5" fill="currentColor"/>
  <circle cx="301.3" cy="171.2" r="4.5" fill="currentColor"/>
  <circle cx="346.4" cy="210.5" r="4.5" fill="currentColor"/>
  <circle cx="371.0" cy="168.4" r="4.5" fill="currentColor"/>
  <circle cx="392.2" cy="189.1" r="4.5" fill="currentColor"/>
  <circle cx="404.2" cy="186.5" r="4.5" fill="currentColor"/>
  <circle cx="408.1" cy="171.1" r="4.5" fill="currentColor"/>
  <circle cx="426.2" cy="177.7" r="4.5" fill="currentColor"/>
  <circle cx="427.3" cy="158.6" r="4.5" fill="currentColor"/>
  <circle cx="453.3" cy="158.6" r="4.5" fill="currentColor"/>
  <line x1="480" y1="70" x2="510" y2="70" stroke="currentColor" stroke-dasharray="5 4"/>
  <text x="518" y="74" font-size="12" fill="currentColor">true curve</text>
  <line x1="480" y1="95" x2="510" y2="95" stroke="#7ccf9a" stroke-width="2.5"/>
  <text x="518" y="99" font-size="12" fill="currentColor">degree 1</text>
  <line x1="480" y1="120" x2="510" y2="120" stroke="#eea66f" stroke-width="2.5"/>
  <text x="518" y="124" font-size="12" fill="currentColor">degree 3</text>
  <line x1="480" y1="145" x2="510" y2="145" stroke="#9cc9ea" stroke-width="2.5"/>
  <text x="518" y="149" font-size="12" fill="currentColor">degree 9</text>
  <circle cx="495" cy="170" r="4.5" fill="currentColor"/>
  <text x="518" y="174" font-size="12" fill="currentColor">training point</text>
</svg>
<figcaption>Polynomial fits to 15 noisy points from a sine wave. Degree 1 underfits; degree 3 is close to the truth;
degree 9 bends to chase the noise.</figcaption>
</figure>

Read the table from top to bottom. Degree 0 (a constant) and degree 1 (a line) **underfit**: they are too simple to
follow the wave, and are wrong on both measures. Degrees 3 and 5 are close to the truth (RMSE about 0.1 against it,
smaller than the noise level of 0.2, because the fit averages the noise away). From there on, the training error keeps
falling, and must, since each higher degree contains the lower ones as special cases (set the extra weights to zero),
but the error against the truth rises: degree 9 has started to fit the noise. Degree 14 has 15 weights for 15 points,
passes through every point (training RMSE 0.0003), and is absurd between and beyond them (RMSE 4422 against the truth).
That is **overfitting** in its purest form, and Chapter 8 is devoted to it. For now, the lesson of Chapter 1 applies:
training error alone cannot choose the degree; a validation set can.

The program uses `np.linalg.lstsq` here rather than the normal equations, because for high degrees the normal
equations break down numerically. Section 4.7 explains why.

## 4.4 Gradient descent from scratch

*Level: intermediate.*

If the normal equations give the answer exactly, why bother with anything else? Three reasons. Solving them costs
about $m^3$ operations for $m$ weights, too much when $m$ is a million. They need all the data in memory at once. And
almost every model after this chapter has *no* exact formula. The method that works for all of them is **gradient
descent**: start somewhere and walk downhill.

$$
w\leftarrow w-\eta\,\nabla L(w),\qquad\nabla L(w)=\frac2nX^\top(Xw-y),
$$

for the mean squared error $L(w)=\frac1n\lVert Xw-y\rVert^2$ (section 3.3 derived the gradient). The **learning rate**
$\eta$ sets the step size. Each step costs two matrix-vector products, about $4nm$ operations, and the data could even
be streamed through in pieces.

```python
--8<-- "books/machine-learning/ch04_gradient_descent.py"
```

Output:

```
exact solution [257.359  54.073  12.365], best MSE 211.774
eigenvalues of the Hessian [0.513 2.    3.487]; 2 / largest = 0.574

  lr    loss after 0, 1, 2, 5, 10, 20, 50 steps
 0.01 7.052e+04 6.763e+04 6.486e+04 5.724e+04 4.652e+04 3.084e+04      9240
 0.10 7.052e+04 4.443e+04 2.821e+04      7508      1054     247.7     212.9
 0.50 7.052e+04      2462      1455     421.8     222.6     211.8     211.8
 0.56 7.052e+04      4771      3452      2588      1671     764.7     241.9
 0.60 7.052e+04      7558      5843      9506 2.264e+04 1.309e+05 2.587e+07

lr 0.5 after 200 steps: [257.359  54.073  12.365]  exact: [257.359  54.073  12.365]
in original units: price = 26.91 + 2.823 area + 11.88 rooms  (data made with 30 + 2.8 area + 12 rooms)

lr 0.1: gap ratio over the last 10 steps per step 0.9000, predicted (1 - lr * smallest eigenvalue)^2 = 0.9000
```

The data is the synthetic set of 200 flats from Chapter 2, with standardised features, as Chapter 2 showed gradient
descent needs. Starting from $w=0$ (MSE 70 516), here is what each learning rate does.

- $\eta=0.01$: safe but slow; after 50 steps the loss is still 9240, more than forty times the best.
- $\eta=0.1$: steady; within 1% of the best (211.77) by step 50.
- $\eta=0.5$: fast; at the optimum to four digits by step 20, and the weights match the exact solution after 200 steps.
- $\eta=0.56$: still converges, but the loss falls unevenly at first, because the steepest direction overshoots back
  and forth.
- $\eta=0.6$: the loss falls for two steps, then grows without limit. The method has **diverged**.

<figure class="mars-fig" markdown="0">
<svg viewBox="0 0 640 290" role="img" aria-label="Loss curves of gradient descent on a log scale, loss from 100 to a million against steps 0 to 50. Learning rate 0.01 (blue) falls slowly. Learning rate 0.1 (green) falls steadily to the best loss. Learning rate 0.5 (orange) drops fastest. Learning rate 0.56 (dashed) drops more slowly with a kink. Learning rate 0.6 (dotted orange) first drops, then rises and leaves the top of the plot. A dashed horizontal line marks the best possible loss.">
  <line x1="70" y1="250" x2="470" y2="250" stroke="currentColor"/>
  <line x1="70" y1="250" x2="70" y2="30" stroke="currentColor"/>
  <line x1="64" y1="250" x2="70" y2="250" stroke="currentColor"/>
  <text x="58" y="254" font-size="12" text-anchor="end" fill="currentColor">10^2</text>
  <line x1="64" y1="195" x2="70" y2="195" stroke="currentColor"/>
  <text x="58" y="199" font-size="12" text-anchor="end" fill="currentColor">10^3</text>
  <line x1="64" y1="140" x2="70" y2="140" stroke="currentColor"/>
  <text x="58" y="144" font-size="12" text-anchor="end" fill="currentColor">10^4</text>
  <line x1="64" y1="85" x2="70" y2="85" stroke="currentColor"/>
  <text x="58" y="89" font-size="12" text-anchor="end" fill="currentColor">10^5</text>
  <line x1="64" y1="30" x2="70" y2="30" stroke="currentColor"/>
  <text x="58" y="34" font-size="12" text-anchor="end" fill="currentColor">10^6</text>
  <line x1="70" y1="250" x2="70" y2="256" stroke="currentColor"/>
  <text x="70" y="270" font-size="12" text-anchor="middle" fill="currentColor">0</text>
  <line x1="150" y1="250" x2="150" y2="256" stroke="currentColor"/>
  <text x="150" y="270" font-size="12" text-anchor="middle" fill="currentColor">10</text>
  <line x1="230" y1="250" x2="230" y2="256" stroke="currentColor"/>
  <text x="230" y="270" font-size="12" text-anchor="middle" fill="currentColor">20</text>
  <line x1="310" y1="250" x2="310" y2="256" stroke="currentColor"/>
  <text x="310" y="270" font-size="12" text-anchor="middle" fill="currentColor">30</text>
  <line x1="390" y1="250" x2="390" y2="256" stroke="currentColor"/>
  <text x="390" y="270" font-size="12" text-anchor="middle" fill="currentColor">40</text>
  <line x1="470" y1="250" x2="470" y2="256" stroke="currentColor"/>
  <text x="470" y="270" font-size="12" text-anchor="middle" fill="currentColor">50</text>
  <line x1="70" y1="232.1" x2="470" y2="232.1" stroke="currentColor" stroke-dasharray="4 3" stroke-opacity="0.6"/>
  <path d="M 70.0 93.3 L 78.0 94.3 L 86.0 95.3 L 94.0 96.3 L 102.0 97.3 L 110.0 98.3 L 118.0 99.3 L 126.0 100.3 L 134.0 101.3 L 142.0 102.3 L 150.0 103.3 L 158.0 104.3 L 166.0 105.3 L 174.0 106.2 L 182.0 107.2 L 190.0 108.2 L 198.0 109.2 L 206.0 110.2 L 214.0 111.1 L 222.0 112.1 L 230.0 113.1 L 238.0 114.1 L 246.0 115.0 L 254.0 116.0 L 262.0 117.0 L 270.0 118.0 L 278.0 118.9 L 286.0 119.9 L 294.0 120.9 L 302.0 121.8 L 310.0 122.8 L 318.0 123.8 L 326.0 124.7 L 334.0 125.7 L 342.0 126.7 L 350.0 127.6 L 358.0 128.6 L 366.0 129.5 L 374.0 130.5 L 382.0 131.5 L 390.0 132.4 L 398.0 133.4 L 406.0 134.3 L 414.0 135.3 L 422.0 136.2 L 430.0 137.2 L 438.0 138.1 L 446.0 139.1 L 454.0 140.0 L 462.0 140.9 L 470.0 141.9" fill="none" stroke="#9cc9ea" stroke-width="2"/>
  <path d="M 70.0 93.3 L 78.0 104.4 L 86.0 115.2 L 94.0 125.9 L 102.0 136.5 L 110.0 146.8 L 118.0 157.0 L 126.0 166.9 L 134.0 176.4 L 142.0 185.4 L 150.0 193.7 L 158.0 201.2 L 166.0 207.7 L 174.0 213.1 L 182.0 217.4 L 190.0 220.8 L 198.0 223.3 L 206.0 225.2 L 214.0 226.6 L 222.0 227.6 L 230.0 228.3 L 238.0 228.9 L 246.0 229.4 L 254.0 229.7 L 262.0 230.0 L 270.0 230.2 L 278.0 230.4 L 286.0 230.6 L 294.0 230.8 L 302.0 230.9 L 310.0 231.0 L 318.0 231.1 L 326.0 231.2 L 334.0 231.3 L 342.0 231.4 L 350.0 231.5 L 358.0 231.5 L 366.0 231.6 L 374.0 231.6 L 382.0 231.7 L 390.0 231.7 L 398.0 231.7 L 406.0 231.8 L 414.0 231.8 L 422.0 231.8 L 430.0 231.9 L 438.0 231.9 L 446.0 231.9 L 454.0 231.9 L 462.0 231.9 L 470.0 231.9" fill="none" stroke="#7ccf9a" stroke-width="2"/>
  <path d="M 70.0 93.3 L 78.0 173.5 L 86.0 186.0 L 94.0 197.5 L 102.0 207.5 L 110.0 215.6 L 118.0 221.6 L 126.0 225.8 L 134.0 228.4 L 142.0 230.0 L 150.0 230.9 L 158.0 231.4 L 166.0 231.7 L 174.0 231.9 L 182.0 232.0 L 190.0 232.0 L 198.0 232.0 L 206.0 232.1 L 214.0 232.1 L 222.0 232.1 L 230.0 232.1 L 238.0 232.1 L 246.0 232.1 L 254.0 232.1 L 262.0 232.1 L 270.0 232.1 L 278.0 232.1 L 286.0 232.1 L 294.0 232.1 L 302.0 232.1 L 310.0 232.1 L 318.0 232.1 L 326.0 232.1 L 334.0 232.1 L 342.0 232.1 L 350.0 232.1 L 358.0 232.1 L 366.0 232.1 L 374.0 232.1 L 382.0 232.1 L 390.0 232.1 L 398.0 232.1 L 406.0 232.1 L 414.0 232.1 L 422.0 232.1 L 430.0 232.1 L 438.0 232.1 L 446.0 232.1 L 454.0 232.1 L 462.0 232.1 L 470.0 232.1" fill="none" stroke="#eea66f" stroke-width="2"/>
  <path d="M 70.0 93.3 L 78.0 157.7 L 86.0 165.4 L 94.0 167.8 L 102.0 170.1 L 110.0 172.3 L 118.0 174.4 L 126.0 176.5 L 134.0 178.6 L 142.0 180.7 L 150.0 182.7 L 158.0 184.8 L 166.0 186.7 L 174.0 188.7 L 182.0 190.6 L 190.0 192.5 L 198.0 194.4 L 206.0 196.2 L 214.0 198.0 L 222.0 199.7 L 230.0 201.4 L 238.0 203.1 L 246.0 204.7 L 254.0 206.2 L 262.0 207.7 L 270.0 209.2 L 278.0 210.6 L 286.0 211.9 L 294.0 213.2 L 302.0 214.5 L 310.0 215.6 L 318.0 216.8 L 326.0 217.8 L 334.0 218.8 L 342.0 219.8 L 350.0 220.7 L 358.0 221.6 L 366.0 222.4 L 374.0 223.1 L 382.0 223.8 L 390.0 224.5 L 398.0 225.1 L 406.0 225.6 L 414.0 226.2 L 422.0 226.7 L 430.0 227.1 L 438.0 227.5 L 446.0 227.9 L 454.0 228.3 L 462.0 228.6 L 470.0 228.9" fill="none" stroke="currentColor" stroke-width="2" stroke-dasharray="6 3"/>
  <path d="M 70.0 93.3 L 78.0 146.7 L 86.0 152.8 L 94.0 149.3 L 102.0 145.3 L 110.0 141.2 L 118.0 137.1 L 126.0 133.0 L 134.0 128.8 L 142.0 124.7 L 150.0 120.5 L 158.0 116.3 L 166.0 112.1 L 174.0 107.9 L 182.0 103.8 L 190.0 99.6 L 198.0 95.4 L 206.0 91.2 L 214.0 87.0 L 222.0 82.8 L 230.0 78.6 L 238.0 74.4 L 246.0 70.2 L 254.0 66.0 L 262.0 61.7 L 270.0 57.5 L 278.0 53.3 L 286.0 49.1 L 294.0 44.9 L 302.0 40.7 L 310.0 36.5 L 318.0 32.3" fill="none" stroke="#eea66f" stroke-width="2" stroke-dasharray="2 3"/>
  <text x="270" y="286" font-size="13" text-anchor="middle" fill="currentColor">steps</text>
  <text x="16" y="140" font-size="13" text-anchor="middle" fill="currentColor" transform="rotate(-90 16 140)">MSE (log scale)</text>
  <line x1="480" y1="50" x2="505" y2="50" stroke="#9cc9ea" stroke-width="2"/>
  <text x="512" y="54" font-size="12" fill="currentColor">η = 0.01</text>
  <line x1="480" y1="75" x2="505" y2="75" stroke="#7ccf9a" stroke-width="2"/>
  <text x="512" y="79" font-size="12" fill="currentColor">η = 0.1</text>
  <line x1="480" y1="100" x2="505" y2="100" stroke="#eea66f" stroke-width="2"/>
  <text x="512" y="104" font-size="12" fill="currentColor">η = 0.5</text>
  <line x1="480" y1="125" x2="505" y2="125" stroke="currentColor" stroke-width="2" stroke-dasharray="6 3"/>
  <text x="512" y="129" font-size="12" fill="currentColor">η = 0.56</text>
  <line x1="480" y1="150" x2="505" y2="150" stroke="#eea66f" stroke-width="2" stroke-dasharray="2 3"/>
  <text x="512" y="154" font-size="12" fill="currentColor">η = 0.6 (diverges)</text>
  <line x1="480" y1="175" x2="505" y2="175" stroke="currentColor" stroke-dasharray="4 3" stroke-opacity="0.6"/>
  <text x="512" y="179" font-size="12" fill="currentColor">best possible</text>
</svg>
<figcaption>Gradient descent on the same problem with five learning rates. Too small is slow, too large diverges, and
the fastest rates sit just inside the limit 2 / (largest eigenvalue) = 0.574.</figcaption>
</figure>

### Why: the convergence proof for least squares

The behaviour is not mysterious; for least squares we can predict it exactly. Write $H=\frac2nX^\top X$, the matrix of
second derivatives of the loss (the **Hessian**), and let $\hat w$ be the exact solution, so $\nabla L(\hat w)=0$, that
is, $\frac2nX^\top X\hat w=\frac2nX^\top y$. Then the gradient at any $w$ is

$$
\nabla L(w)=\frac2nX^\top Xw-\frac2nX^\top y=H(w-\hat w).
$$

Let $e_t=w_t-\hat w$ be the error after $t$ steps. One step gives $e_{t+1}=e_t-\eta He_t=(I-\eta H)e_t$, and so

$$
e_t=(I-\eta H)^t\,e_0 .
$$

$H$ is symmetric, so by the spectral theorem (section 3.6) it has orthonormal eigenvectors $q_j$ with eigenvalues
$\lambda_j\ge0$. In those coordinates, $(I-\eta H)$ just multiplies the $q_j$-component by $1-\eta\lambda_j$. So the
component of the error along $q_j$ after $t$ steps is $(1-\eta\lambda_j)^t$ times its starting value. Also, because
the loss is exactly quadratic,

$$
L(w)-L(\hat w)=\tfrac12\,e^\top He=\tfrac12\sum_j\lambda_jc_j^2 ,
$$

where $c_j$ is the error's component along $q_j$. (*Check:* $\frac1n\lVert X\hat w+Xe-y\rVert^2=\frac1n\lVert X\hat
w-y\rVert^2+\frac2ne^\top X^\top(X\hat w-y)+\frac1ne^\top X^\top Xe$, and the middle term is zero by the normal
equations.) Everything follows from this.

**Theorem.** Gradient descent on least squares converges from every starting point if and only if
$0<\eta<2/\lambda_{\max}$ (for the components with $\lambda_j>0$). Its loss gap then shrinks at least by the factor
$\rho^2$ per step, where $\rho=\max_j|1-\eta\lambda_j|$ over the eigenvalues $\lambda_j>0$.

**Proof.** The component along $q_j$ is multiplied by $1-\eta\lambda_j$ each step. It shrinks to zero exactly when
$|1-\eta\lambda_j|<1$, that is, $0<\eta\lambda_j<2$; for the largest eigenvalue this is $\eta<2/\lambda_{\max}$, and then
it holds for all the others too. If $\eta>2/\lambda_{\max}$, the component along the top eigenvector grows by a factor
above 1 per step, so it diverges unless it started at exactly zero. Each term $\lambda_jc_j^2$ of the loss gap is
multiplied by $(1-\eta\lambda_j)^2\le\rho^2$ per step. $\square$ (Components with $\lambda_j=0$ are directions in which
the loss is flat; gradient descent never changes them, and they do not affect the loss.)

Now check the numbers. The program prints the eigenvalues of $H$: 0.513, 2 and 3.487. So the limit is
$2/3.487=0.574$: rates 0.56 converges and 0.6 diverges, exactly as observed. The eigenvalue 2 belongs to the intercept
(with centred features, the intercept direction is separate, and $\frac2n\mathbf 1^\top\mathbf 1=2$), so $\eta=0.5$
makes $1-\eta\lambda=0$ there: the intercept is exactly right after a single step. With $\eta=0.1$, the slowest
component is the one with $\lambda=0.513$, whose loss term shrinks by $(1-0.0513)^2=0.9000$ per step; the program
measures the ratio of successive loss gaps late in the run and finds 0.9000.

What is the best fixed rate? $\rho$ is smallest when the extreme factors balance, $1-\eta\lambda_{\min}=\eta\lambda_{\max}-1$,
giving $\eta=2/(\lambda_{\min}+\lambda_{\max})$ and $\rho=(\kappa-1)/(\kappa+1)$, where $\kappa=\lambda_{\max}/\lambda_{\min}$
is the condition number. With $\kappa$ near 1 one step nearly solves the problem; with $\kappa=10^4$, $\rho=0.9998$ and
the method crawls. This is the proof behind Chapter 2's claim that scaling matters. Chapter 5 extends the analysis to
non-quadratic convex losses, and adds momentum, which improves the dependence on $\kappa$.

Two practical notes. First, the weights were learned in standardised units. To report them in the original units,
undo the scaling: the program recovers price $=26.91+2.823\times$area$\,+\,11.88\times$rooms, close to the
$30+2.8\times$area$\,+\,12\times$rooms used to generate the data (the gap is the noise). Second, in real use you do not
know $\lambda_{\max}$; you try a few learning rates spaced by factors of about 3 (0.01, 0.03, 0.1, 0.3, ...) and keep the
largest that converges smoothly. Plotting the loss on a log scale, as in the figure, makes convergence and divergence
obvious.

## 4.5 Maximum likelihood with Gaussian noise gives least squares

Section 4.1 claimed that least squares is "right" when errors are Gaussian. Here is the precise statement and its
proof, which is the reason this loss dominates applied statistics.

**The model.** Each label is a linear function of the features plus noise:

$$
y_i=x_i\cdot w+\varepsilon_i,\qquad\varepsilon_i\sim\mathcal N(0,\sigma^2)\ \text{independently},
$$

where $x_i$ is row $i$ of the design matrix. In words: the true relation is a straight line (or plane), and each
observation misses it by a random amount, typically about $\sigma$, independently of the others, equally likely
above and below.

**Theorem.** Under this model, the weights $w$ that maximise the likelihood of the observed labels are the
least-squares weights, and the maximum-likelihood estimate of the noise variance is $\hat\sigma^2=\mathrm{SSE}(\hat w)/n$.

**Proof.** Given $x_i$ and $w$, the label $y_i$ is Gaussian with mean $x_i\cdot w$ and variance $\sigma^2$, so its density
is $\frac1{\sqrt{2\pi\sigma^2}}\exp\bigl(-(y_i-x_i\cdot w)^2/(2\sigma^2)\bigr)$. The labels are independent, so the
likelihood is the product of these densities, and the log-likelihood is the sum of their logs:

$$
\ell(w,\sigma^2)=-\frac n2\ln(2\pi\sigma^2)-\frac1{2\sigma^2}\sum_{i=1}^n(y_i-x_i\cdot w)^2
=-\frac n2\ln(2\pi\sigma^2)-\frac{\mathrm{SSE}(w)}{2\sigma^2}.
$$

For any fixed $\sigma^2$, the first term does not involve $w$ and the second is a negative constant times
$\mathrm{SSE}(w)$. So $\ell$ is largest exactly where SSE is smallest: at the least-squares $\hat w$, whatever
$\sigma^2$ is. Then, as in section 3.5, setting $\partial\ell/\partial\sigma^2=-\frac n{2\sigma^2}+\frac{\mathrm{SSE}}{2\sigma^4}=0$
gives $\hat\sigma^2=\mathrm{SSE}(\hat w)/n$. $\square$

```python
--8<-- "books/machine-learning/ch04_reading.py"
```

Output:

```
weights [26.906  2.823 11.882]; MLE noise sd 14.552 (data made with sd 15)
log-likelihood at the least-squares w: -819.340
at five nearby w: [-1187.835, -855.033, -1308.312, -1209.691, -824.973]
R^2 = 0.9506

line: R^2 = 0.9268; mean residual by range of x:
  x in [0, 1): mean +0.555
  x in [1, 2): mean -0.445
  x in [2, 3): mean -0.369
  x in [3, 4): mean +0.399

quadratic: R^2 = 0.9725; mean residual by range of x:
  x in [0, 1): mean +0.065
  x in [1, 2): mean -0.077
  x in [2, 3): mean +0.062
  x in [3, 4): mean -0.011

funnel: residual spread by range of x:
  x in [0, 1): sd 0.185
  x in [1, 2): sd 0.443
  x in [2, 3): sd 0.655
  x in [3, 4): sd 0.756
```

On the 200 synthetic flats, the least-squares weights have log-likelihood $-819.340$, and five random nearby weight
vectors all score lower, as the theorem says they must. The estimated noise standard deviation is $\sqrt{42354.7/200}
\approx14.55$, close to the 15 used to make the data. (Like the variance estimate of section 3.5, it is biased slightly
low, because the fitted line is closer to its own data than the true line; dividing by $n-m-1$ instead of $n$, where
$m+1$ is the number of weights, corrects it on average.)

**What the theorem tells us, and what it does not.** It tells us which assumptions make least squares the principled
choice: a linear relation, independent errors, the *same* noise level for every example, and Gaussian noise. When
those hold, least squares is not just convenient but optimal in a precise sense. When they fail, the same reasoning
gives other losses. If the noise has the **Laplace** distribution, with density proportional to $e^{-|\varepsilon|/b}$
(heavier tails, so large errors are more common), the log-likelihood is a constant minus $\sum_i|y_i-x_i\cdot w|/b$,
and maximum likelihood becomes *least absolute deviations*, the robust median-like fit of 4.1. If the noise level
differs from example to example, maximum likelihood weights each squared error by $1/\sigma_i^2$: **weighted least
squares**. And if the label is a class rather than a number, the Bernoulli distribution takes the place of the
Gaussian, and the same derivation produces the cross-entropy loss of logistic regression (Chapter 6). The recipe
"choose a noise model, write down the likelihood, maximise it" is how most losses in this book are born.

## 4.6 Reading coefficients; R squared; residual plots

You have fitted a model. What do its numbers mean, and how do you know whether to trust it?

### Reading coefficients

A weight $w_j$ is the change in the prediction when feature $j$ increases by one unit **and every other feature is
held fixed**. Its unit is (unit of $y$) per (unit of $x_j$): 3.797 thousand per square metre in the one-feature model.
Three cautions.

1. **"Held fixed" is a statement about the model, not the world.** In the two-feature model of 4.3, the rooms weight
   was $-8.49$: holding area fixed, one more room lowers the predicted price. Whether it would lower the price of a
   real flat to add a wall is a causal question (Chapter 1), and the regression cannot answer it.
2. **Correlated features share credit unstably.** Area and rooms are correlated at 0.852, so the data contains little
   information about the effect of one with the other held fixed: there are few pairs of flats with the same area and
   different numbers of rooms. Small changes to the data can then swing the two weights a lot in opposite directions,
   while their combined predictions stay stable. This is **collinearity**; section 4.7 measures it with the condition
   number, and Chapter 8's ridge regression tames it.
3. **Weights depend on units.** Measured in square centimetres, the area weight would be 10 000 times smaller and
   mean exactly the same. To compare the importance of features, fit on standardised features: then each weight is the
   change in prediction per standard deviation of its feature. On the standardised 200 flats the weights are 54.07
   (area) and 12.37 (rooms): area matters far more per typical variation.

Statistics packages also print a **standard error** for each weight, a confidence interval and a p-value. These come
from the Gaussian model of 4.5 (the estimated weights are themselves Gaussian around the true ones, with covariance
$\sigma^2(X^\top X)^{-1}$) and are only as trustworthy as its assumptions. Chapter 7 discusses intervals and the
bootstrap, which needs fewer assumptions.

### R squared

How much of the variation in $y$ does the model explain? Compare the model with the simplest possible model, the
constant $\bar y$. Define three sums of squares:

$$
\mathrm{SST}=\sum_i(y_i-\bar y)^2,\qquad\mathrm{SSR}=\sum_i(\hat y_i-\bar y)^2,\qquad\mathrm{SSE}=\sum_i(y_i-\hat y_i)^2 ,
$$

the total, regression ("explained") and error ("unexplained") sums of squares. Then

$$
R^2=1-\frac{\mathrm{SSE}}{\mathrm{SST}} .
$$

**Claim.** For least squares with an intercept, $\mathrm{SST}=\mathrm{SSR}+\mathrm{SSE}$, so $0\le R^2\le1$ and
$R^2=\mathrm{SSR}/\mathrm{SST}$.

**Proof.** Write $y-\bar y\mathbf 1=(\hat y-\bar y\mathbf 1)+(y-\hat y)$. The second vector is the residual, which is
orthogonal to every column of $X$, hence to every vector in the column space. The first vector is in the column space
(because $\hat y$ is, and so is $\mathbf 1$, the intercept column). So they are orthogonal, and Pythagoras gives
$\mathrm{SST}=\mathrm{SSR}+\mathrm{SSE}$. $\square$

$R^2$ is the fraction of the variance of $y$ that the model accounts for. For the ten flats, $R^2=1-4215.8/48472.5=0.913$.
The program also prints the squared correlation of area and price, 0.913: for a single feature, $R^2=r^2$. (*Why:*
$\hat y_i-\bar y=w_1(x_i-\bar x)$, so $\mathrm{SSR}=w_1^2S_{xx}=S_{xy}^2/S_{xx}$, and $R^2=S_{xy}^2/(S_{xx}S_{yy})=r^2$.)

**R squared only goes up.** Adding a feature can never lower the training $R^2$: the bigger model can always set the
new weight to zero and reproduce the old fit, so its minimum SSE is at most the old one. Add enough random features
and $R^2$ reaches 1, as degree 14 did in 4.3. So a high training $R^2$ is not evidence of a good model; compute it on
validation data, where it can be negative (a model worse than predicting the mean). The **adjusted** $R^2$ that
statistics packages print, $1-(1-R^2)\frac{n-1}{n-m-1}$, applies a penalty for the number of features $m$, a rough
correction; held-out data is the honest check.

### Residual plots

The single most useful check of a regression is to plot the residuals against the fitted values or against each
feature. If the model is right, the residuals are just noise: a shapeless band around zero, equally wide everywhere.
Any visible structure is a message.

<figure class="mars-fig" markdown="0">
<svg viewBox="0 0 640 260" role="img" aria-label="Two residual plots, residual against x from 0 to 4. Left, residuals of a straight line fitted to curved data: they form a U shape, positive at both ends and negative in the middle. Right, residuals of a quadratic fitted to the same data: a shapeless band around zero.">
  <line x1="50" y1="130" x2="300" y2="130" stroke="currentColor" stroke-opacity="0.6"/>
  <line x1="50" y1="35" x2="50" y2="225" stroke="currentColor"/>
  <text x="50" y="244" font-size="11" text-anchor="middle" fill="currentColor">0</text>
  <text x="112" y="244" font-size="11" text-anchor="middle" fill="currentColor">1</text>
  <text x="175" y="244" font-size="11" text-anchor="middle" fill="currentColor">2</text>
  <text x="238" y="244" font-size="11" text-anchor="middle" fill="currentColor">3</text>
  <text x="300" y="244" font-size="11" text-anchor="middle" fill="currentColor">4</text>
  <text x="44" y="194" font-size="11" text-anchor="end" fill="currentColor">-1</text>
  <text x="44" y="134" font-size="11" text-anchor="end" fill="currentColor">0</text>
  <text x="44" y="74" font-size="11" text-anchor="end" fill="currentColor">+1</text>
  <circle cx="53.3" cy="75.6" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="55.0" cy="66.4" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="61.1" cy="70.5" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="62.4" cy="60.7" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="66.2" cy="85.6" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="67.2" cy="61.8" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="74.1" cy="52.4" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="77.7" cy="82.0" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="78.7" cy="68.4" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="84.2" cy="109.0" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="84.8" cy="81.3" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="86.0" cy="79.1" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="86.2" cy="106.3" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="87.1" cy="129.2" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="87.4" cy="97.5" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="88.6" cy="95.4" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="93.2" cy="67.6" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="95.5" cy="115.1" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="96.5" cy="67.7" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="98.2" cy="166.6" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="106.5" cy="127.0" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="107.9" cy="133.1" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="108.3" cy="131.1" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="108.4" cy="134.9" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="112.2" cy="127.7" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="112.4" cy="87.9" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="112.5" cy="130.6" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="113.4" cy="99.7" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="114.2" cy="131.1" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="115.5" cy="127.6" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="117.8" cy="188.9" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="119.4" cy="132.0" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="119.8" cy="120.1" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="120.6" cy="162.3" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="121.1" cy="150.3" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="124.8" cy="159.5" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="126.6" cy="90.5" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="130.6" cy="167.4" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="131.2" cy="161.7" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="133.3" cy="210.6" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="133.4" cy="183.8" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="134.9" cy="142.6" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="135.3" cy="178.1" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="138.4" cy="215.4" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="139.2" cy="157.5" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="143.2" cy="150.7" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="143.3" cy="146.9" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="143.9" cy="144.9" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="145.5" cy="169.0" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="145.7" cy="88.3" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="147.6" cy="168.9" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="149.9" cy="146.4" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="155.9" cy="189.6" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="156.8" cy="174.6" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="157.2" cy="196.3" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="159.1" cy="155.7" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="159.5" cy="170.4" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="160.0" cy="184.8" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="161.1" cy="208.9" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="162.7" cy="148.8" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="164.1" cy="142.9" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="164.2" cy="142.5" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="164.3" cy="164.3" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="164.4" cy="145.8" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="166.1" cy="141.0" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="172.3" cy="151.6" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="177.2" cy="130.2" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="179.5" cy="168.0" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="179.9" cy="159.2" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="180.9" cy="200.1" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="182.9" cy="114.4" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="185.9" cy="181.5" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="187.3" cy="155.8" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="193.6" cy="147.6" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="194.6" cy="181.5" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="200.1" cy="161.9" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="201.5" cy="144.0" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="203.2" cy="161.9" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="206.5" cy="165.7" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="208.4" cy="165.2" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="208.5" cy="174.4" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="212.1" cy="160.0" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="212.3" cy="147.1" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="218.7" cy="141.6" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="219.7" cy="125.9" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="221.0" cy="149.8" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="227.4" cy="158.9" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="231.3" cy="123.9" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="234.7" cy="132.9" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="235.4" cy="116.7" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="236.4" cy="135.2" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="241.8" cy="122.2" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="244.0" cy="123.4" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="247.6" cy="111.8" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="247.9" cy="151.9" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="248.9" cy="130.2" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="250.9" cy="121.3" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="252.0" cy="83.7" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="252.4" cy="125.7" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="254.2" cy="111.1" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="257.5" cy="122.4" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="258.3" cy="166.3" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="259.0" cy="87.0" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="259.4" cy="99.9" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="260.7" cy="84.8" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="263.3" cy="143.5" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="263.9" cy="103.7" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="266.2" cy="103.5" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="267.5" cy="143.1" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="270.5" cy="90.9" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="272.1" cy="114.1" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="273.8" cy="85.6" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="276.6" cy="132.7" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="283.4" cy="104.1" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="288.4" cy="92.0" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="290.7" cy="107.5" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="292.5" cy="67.0" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="294.0" cy="34.7" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="294.7" cy="65.0" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="296.8" cy="45.9" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <line x1="360" y1="130" x2="610" y2="130" stroke="currentColor" stroke-opacity="0.6"/>
  <line x1="360" y1="35" x2="360" y2="225" stroke="currentColor"/>
  <text x="360" y="244" font-size="11" text-anchor="middle" fill="currentColor">0</text>
  <text x="422" y="244" font-size="11" text-anchor="middle" fill="currentColor">1</text>
  <text x="485" y="244" font-size="11" text-anchor="middle" fill="currentColor">2</text>
  <text x="548" y="244" font-size="11" text-anchor="middle" fill="currentColor">3</text>
  <text x="610" y="244" font-size="11" text-anchor="middle" fill="currentColor">4</text>
  <text x="354" y="194" font-size="11" text-anchor="end" fill="currentColor">-1</text>
  <text x="354" y="134" font-size="11" text-anchor="end" fill="currentColor">0</text>
  <text x="354" y="74" font-size="11" text-anchor="end" fill="currentColor">+1</text>
  <circle cx="363.3" cy="156.0" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="365.0" cy="143.7" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="371.1" cy="137.1" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="372.4" cy="125.0" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="376.2" cy="143.7" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="377.2" cy="118.3" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="384.1" cy="98.1" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="387.7" cy="122.2" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="388.7" cy="107.2" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="394.2" cy="140.0" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="394.8" cy="111.4" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="396.0" cy="107.6" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="396.2" cy="134.5" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="397.1" cy="156.2" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="397.4" cy="124.2" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="398.6" cy="120.4" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="403.2" cy="86.9" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="405.5" cy="131.5" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="406.5" cy="82.9" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="408.2" cy="179.8" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="416.5" cy="131.0" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="417.9" cy="135.7" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="418.3" cy="133.3" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="418.4" cy="136.9" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="422.2" cy="126.0" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="422.4" cy="85.9" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="422.5" cy="128.6" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="423.4" cy="96.8" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="424.2" cy="127.5" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="425.5" cy="122.8" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="427.8" cy="182.0" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="429.4" cy="123.8" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="429.8" cy="111.5" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="430.6" cy="153.0" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="431.1" cy="140.5" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="434.8" cy="146.7" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="436.6" cy="76.4" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="440.6" cy="150.3" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="441.2" cy="144.2" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="443.3" cy="191.7" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="443.4" cy="164.8" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="444.9" cy="122.7" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="445.3" cy="157.9" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="448.4" cy="193.4" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="449.2" cy="135.0" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="453.2" cy="126.1" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="453.3" cy="122.2" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="453.9" cy="119.9" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="455.5" cy="143.1" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="455.7" cy="62.4" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="457.6" cy="142.1" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="459.9" cy="118.6" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="465.9" cy="159.6" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="466.8" cy="144.3" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="467.2" cy="165.8" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="469.1" cy="124.7" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="469.5" cy="139.3" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="470.0" cy="153.6" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="471.1" cy="177.4" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="472.7" cy="116.9" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="474.1" cy="110.7" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="474.2" cy="110.2" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="474.3" cy="132.0" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="474.4" cy="113.5" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="476.1" cy="108.4" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="482.3" cy="118.2" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="487.2" cy="96.5" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="489.5" cy="134.3" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="489.9" cy="125.5" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="490.9" cy="166.4" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="492.9" cy="80.8" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="495.9" cy="148.1" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="497.3" cy="122.6" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="503.6" cy="115.5" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="504.6" cy="149.7" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="510.1" cy="131.5" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="511.5" cy="114.1" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="513.2" cy="132.7" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="516.5" cy="137.7" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="518.4" cy="138.0" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="518.5" cy="147.2" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="522.1" cy="134.5" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="522.3" cy="121.7" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="528.7" cy="119.7" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="529.7" cy="104.5" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="531.0" cy="129.1" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="537.4" cy="142.6" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="541.3" cy="110.4" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="544.7" cy="122.1" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="545.4" cy="106.5" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="546.4" cy="125.8" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="551.8" cy="117.6" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="554.0" cy="120.9" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="557.6" cy="112.8" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="557.9" cy="153.2" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="558.9" cy="132.6" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="560.9" cy="125.8" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="562.0" cy="89.3" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="562.4" cy="131.7" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="564.2" cy="119.1" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="567.5" cy="134.2" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="568.3" cy="178.9" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="569.0" cy="100.3" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="569.4" cy="113.8" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="570.7" cy="100.3" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="573.3" cy="162.1" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="573.9" cy="123.1" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="576.2" cy="125.6" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="577.5" cy="166.9" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="580.5" cy="118.6" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="582.1" cy="144.1" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="583.8" cy="118.0" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="586.6" cy="169.0" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="593.4" cy="150.3" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="598.4" cy="146.1" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="600.7" cy="165.3" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="602.5" cy="127.8" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="604.0" cy="97.9" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="604.7" cy="129.4" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="606.8" cy="113.9" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <text x="175" y="24" font-size="13" text-anchor="middle" fill="currentColor">straight line: a U-shaped pattern</text>
  <text x="485" y="24" font-size="13" text-anchor="middle" fill="currentColor">quadratic: no pattern left</text>
  <text x="175" y="258" font-size="12" text-anchor="middle" fill="currentColor">x</text>
  <text x="485" y="258" font-size="12" text-anchor="middle" fill="currentColor">x</text>
</svg>
<figcaption>Residuals of a straight line (left) and of a quadratic (right), fitted to the same 120 points from
y = 1 + 0.5 x² plus noise. The U shape on the left says the model is missing a curve.</figcaption>
</figure>

The program makes 120 points from $y=1+0.5x^2$ plus noise and fits a straight line. Its $R^2$ is a respectable 0.927,
and a careless analyst would stop. But the mean residual by range of $x$ is $+0.555$, $-0.445$, $-0.369$, $+0.399$:
positive at both ends, negative in the middle. The line is too high in the middle and too low at the ends, the
signature of a missing $x^2$ term. Adding it (a quadratic, polynomial features again) raises $R^2$ to 0.973 and leaves
mean residuals of a few hundredths, with no pattern.

The second pattern is a **funnel**. The program makes data whose noise grows with $x$ (standard deviation
$0.25x+0.05$). The residual spread rises from 0.185 to 0.756 across the range. The straight line itself is fine here,
but the equal-noise assumption of 4.5 is broken: predictions at large $x$ are much less certain than at small $x$, and
intervals computed from one $\hat\sigma$ would be wrong at both ends. Remedies are weighted least squares or modelling
$\log y$ instead of $y$ (when noise is proportional to size, logs make it even).

Other patterns to look for: a few residuals far larger than the rest (outliers, or a mislabelled example); residuals
that drift with time or with the order of the rows (the errors are not independent); clusters of residuals for one
category (a missing feature). Each is a clue to a better model.

## 4.7 QR and SVD solutions, conditioning, and why not invert X^T X

*Level: advanced.*

The normal equations are the right *mathematics* and often the wrong *computation*. This section explains why, and
what libraries do instead.

### Conditioning

A computer stores numbers to about 16 significant decimal digits (double precision; the gap between 1 and the next
representable number is $\varepsilon\approx2.2\times10^{-16}$). Every arithmetic step can introduce a relative error of
about $\varepsilon$. Whether those tiny errors stay tiny depends on the problem. The **condition number** of a matrix,
$\kappa(X)=\sigma_{\max}/\sigma_{\min}$, the ratio of its largest to smallest singular value (section 3.6), measures how
much the problem can magnify them. As a rule of thumb, solving a well-implemented least-squares problem loses about
$\log_{10}\kappa$ of the 16 digits. (The precise bounds involve a few more terms; Golub and Van Loan's *Matrix
Computations* and Higham's *Accuracy and Stability of Numerical Algorithms* give them.)

The trouble with the normal equations is that forming $X^\top X$ **squares** the condition number.

**Claim.** $\kappa(X^\top X)=\kappa(X)^2$.

**Proof.** With the SVD $X=U\Sigma V^\top$ (thin form, $U$ of size $n\times m$ with orthonormal columns),
$X^\top X=V\Sigma U^\top U\Sigma V^\top=V\Sigma^2V^\top$. This is the spectral decomposition of $X^\top X$, whose eigenvalues,
equal to its singular values here, are the $\sigma_j^2$. So $\kappa(X^\top X)=\sigma_{\max}^2/\sigma_{\min}^2$. $\square$

If $\kappa(X)=10^6$, a careful method on $X$ loses about 6 digits and keeps 10; the normal equations work with a matrix
of condition $10^{12}$ and keep about 4. At $\kappa(X)=10^8$ the normal equations keep nothing.

Polynomial features are a classic source of bad conditioning. On $[0,1]$ the columns $x^9$, $x^{10}$, $x^{11}$ look
almost the same (all near zero for most $x$ and rising steeply near 1), so they are nearly dependent. The program
builds such matrices, makes *exact* data $y=Xw_{\text{true}}$ with $w_{\text{true}}=(1,\dots,1)$, so a perfect solver
would return all ones, and measures each method's relative error.

```python
--8<-- "books/machine-learning/ch04_qr_svd.py"
```

Output:

```
Q^T Q = [[1.0, 0.0], [0.0, 1.0]]
R = [[-1.7321, -3.4641], [0.0, -1.4142]]  Q R = X: True
QR solution [0.6667 0.5   ]  normal equations [0.6667 0.5   ]

degree  cond(X)   cond(X^T X)   relative error of w: normal  inverse   QR       SVD
     3  1.18e+02     1.39e+04       8.4e-13   9.4e-13   7.2e-16   2.2e-15
     6  1.98e+04     3.90e+08       2.8e-09   2.4e-08   7.8e-13   1.2e-12
     9  3.56e+06     1.27e+13       2.5e-04   1.0e-03   1.2e-10   5.1e-11
    12  6.79e+08     4.08e+17       2.6e+00   3.5e+01   1.4e-08   2.2e-08

duplicate column: rank 2 of 3
cond(X^T X) = 5.40e+17
normal equations: [-16.3319   2.1063  19.0787]  w1 + w2/10 = 4.0142
SVD minimum-norm solution [-16.3319   3.9745   0.3974]  predictions [192.41 284.73 144.24 377.06 236.56]
single-column fit slope 4.0142 = w1 + w2/10 = 4.0142
```

At degree 12, $\kappa(X)\approx6.8\times10^8$ and $\kappa(X^\top X)\approx4\times10^{17}$, beyond what double precision can
represent. The normal equations return weights with relative error 2.6, meaning no correct digits at all, and
explicitly inverting $X^\top X$ is worse still (error 35). QR and the SVD, which work on $X$ directly, keep about 8
digits, matching $16-\log_{10}(6.8\times10^8)\approx7$. At every degree, the normal equations lose about twice as many
digits as QR, just as $\kappa^2$ versus $\kappa$ predicts.

### The QR solution

A **QR decomposition** writes $X=QR$, where $Q$ ($n\times m$) has orthonormal columns ($Q^\top Q=I$) and $R$ ($m\times m$)
is **upper triangular** (zeros below the diagonal). Then the normal equations simplify. $X^\top X=R^\top Q^\top QR=R^\top R$
and $X^\top y=R^\top Q^\top y$, so $R^\top Rw=R^\top Q^\top y$, and since $R$ is invertible (for independent columns),

$$
Rw=Q^\top y .
$$

A triangular system is solved from the bottom up by **back substitution**: the last equation has one unknown, the one
above it two, and so on, in about $m^2/2$ steps. No $X^\top X$ is ever formed, so the condition number is not squared.

**Where Q and R come from: Gram-Schmidt.** Take the columns of $X$ one at a time. Make the first a unit vector: that
is $q_1$. From the second, subtract its projection onto $q_1$ (section 3.1), and make what remains a unit vector:
$q_2$. From the third, subtract its projections onto $q_1$ and $q_2$, and so on. Each column is then a combination of
the $q$'s found so far, and the coefficients form $R$. By hand, for the columns $a_1=(1,1,1)$ and $a_2=(1,2,3)$ of the
program's small example:

| step | computation | result |
|---|---|---|
| 1 | $r_{11}=\lVert a_1\rVert=\sqrt3$ | $1.7321$; $q_1=(1,1,1)/\sqrt3$ |
| 2 | $r_{12}=q_1\cdot a_2=6/\sqrt3$ | $3.4641$ |
| 3 | $a_2-r_{12}q_1=(1,2,3)-(2,2,2)$ | $(-1,0,1)$ |
| 4 | $r_{22}=\lVert(-1,0,1)\rVert=\sqrt2$ | $1.4142$; $q_2=(-1,0,1)/\sqrt2$ |

The program's $R$ has the same entries with minus signs; QR is unique only up to the signs of the columns of $Q$.
With $y=(1,2,2)$: $Q^\top y=(5/\sqrt3,\,1/\sqrt2)=(2.8868,0.7071)$; back substitution gives
$w_2=0.7071/1.4142=0.5$ and $w_1=(2.8868-3.4641\times0.5)/1.7321=0.6667$, the same as the normal equations, as the
program confirms.

Classical Gram-Schmidt loses orthogonality in floating point when columns are nearly dependent. Libraries instead use
**Householder reflections**: for each column $k$, a reflection (a mirror map $I-2vv^\top$ with $\lVert v\rVert=1$, which
is orthogonal) is chosen to send the part of column $k$ on and below the diagonal to a multiple of the first unit
vector, zeroing everything below the diagonal in one move. The product of the reflections is $Q^\top$, and what is left
is $R$. The program's `householder_qr` does exactly this in a dozen lines; the sign choice in `copysign` avoids
subtracting two nearly equal numbers. Its cost is about $2nm^2$ operations, roughly twice that of forming $X^\top X$, a
small price for the digits it saves.

### The SVD solution and the pseudo-inverse

With the thin SVD $X=U\Sigma V^\top$, the least-squares problem separates completely. Since $U$'s columns are orthonormal
and $V$ is a rotation, minimising $\lVert y-U\Sigma V^\top w\rVert^2$ comes down to choosing $z=V^\top w$ so that
$\sigma_jz_j=u_j\cdot y$ for each $j$. When every $\sigma_j>0$:

$$
\hat w=V\Sigma^{-1}U^\top y=\sum_j\frac{u_j\cdot y}{\sigma_j}\,v_j .
$$

The formula shows the danger plainly: each component is divided by a singular value, so a tiny $\sigma_j$ (a nearly
dependent combination of columns) multiplies the noise in $u_j\cdot y$ by a huge factor.

When some $\sigma_j=0$, the columns are dependent, the minimiser is not unique, and the normal equations have no
unique solution. The SVD offers a natural choice: set $z_j=0$ for those $j$ (they do not affect the predictions), which
gives the **minimum-norm** least-squares solution, the shortest of all the minimisers. The matrix
$X^+=V\Sigma^+U^\top$, with $\Sigma^+$ inverting the nonzero singular values and leaving zeros as zeros, is the
**Moore-Penrose pseudo-inverse**, and $\hat w=X^+y$. In floating point, "zero" means "below a small tolerance times
$\sigma_{\max}$", which is what the program's `rtol` does.

The program's last example duplicates a column: area in square metres and area in tens of square metres, which is the
same information. The rank is 2, not 3. $\kappa(X^\top X)\approx5\times10^{17}$, numerically singular. The normal
equations still return *an* answer, $(-16.33,\,2.106,\,19.08)$, without complaint (with other rounding they might
instead raise a "singular matrix" error): one arbitrary member of the infinite family of minimisers. The SVD returns
the minimum-norm one, $(-16.33,\,3.974,\,0.397)$. Both make the same predictions, because only the combination
$w_1+w_2/10=4.0142$ matters, and it equals the slope of the one-column fit. A silent arbitrary answer is dangerous: its
individual weights mean nothing, and a slightly different dataset would give wildly different ones.

### What to use

- For small, well-conditioned problems, any method works, and the normal equations are the fastest.
- In general, use a QR- or SVD-based solver. NumPy's `np.linalg.lstsq` is SVD-based (it calls the LAPACK routine
  `gelsd`) and handles rank deficiency; `np.linalg.solve(X.T @ X, X.T @ y)` is the normal equations and does not.
- Never compute $(X^\top X)^{-1}$ explicitly to solve a system: it costs more and is less accurate than solving
  directly, as the "inverse" column shows.
- If $X$ is badly conditioned because features are nearly collinear, a better solver gives you accurate digits of
  weights that are still extremely sensitive to the data. The statistical fix is regularisation (ridge regression,
  Chapter 8), which adds $\lambda I$ to $X^\top X$ and so raises the smallest eigenvalue.
- When $m$ is very large or the data does not fit in memory, use iterative methods: gradient descent (4.4), its
  stochastic version (Chapter 5), or conjugate gradients.

**In practice:** scikit-learn's `LinearRegression` solves least squares with an SVD-based routine from SciPy, and its
`SGDRegressor` uses stochastic gradient descent; statistics packages such as statsmodels add the standard errors of
4.6. All of them compute what this chapter built.

## Check yourself

??? question "1. Fit a line by hand to the points (1, 1), (2, 2), (3, 2). Give the slope, intercept and residuals."

    $\bar x=2$, $\bar y=5/3$. Deviations of $x$: $-1,0,1$; of $y$: $-2/3,1/3,1/3$. $S_{xy}=2/3+0+1/3=1$, $S_{xx}=2$, so
    $w_1=0.5$ and $w_0=5/3-0.5\times2=2/3\approx0.667$. Predictions $1.167,1.667,2.167$; residuals $-0.167,+0.333,-0.167$.
    They add to zero, and their dot product with $x=(1,2,3)$ is $-0.167+0.667-0.5=0$, as the normal equations require.
    (This is the program's small QR example, which also returned $(0.6667,0.5)$.)

??? question "2. Compute R squared for the fit in question 1, and check that it equals the squared correlation."

    $\mathrm{SSE}=0.0278+0.1111+0.0278=0.1667$. $\mathrm{SST}=4/9+1/9+1/9=0.6667$. $R^2=1-0.1667/0.6667=0.75$. The
    correlation is $S_{xy}/\sqrt{S_{xx}S_{yy}}=1/\sqrt{2\times0.6667}=0.866$, and $0.866^2=0.75$.

??? question "3. Derive the least-squares slope for a line through the origin, y-hat = w x (no intercept). Do the residuals still add up to zero?"

    Minimise $\sum_i(y_i-wx_i)^2$: the derivative $-2\sum_i(y_i-wx_i)x_i=0$ gives $w=\sum_ix_iy_i/\sum_ix_i^2$. The only
    normal equation is $x\cdot r=0$; there is no column of ones, so nothing forces $\sum_ir_i=0$, and in general it is
    not zero. For (1, 1), (2, 2), (3, 2): $w=(1+4+6)/14=11/14\approx0.786$, residuals $0.214,0.429,-0.357$, sum $0.286$.

??? question "4. Write down the design matrix for a model price = w0 + w1 area + w2 area^2 with the areas 40, 60, 80. Is this still linear regression?"

    $X=\begin{pmatrix}1&40&1600\\1&60&3600\\1&80&6400\end{pmatrix}$. Yes: the prediction $Xw$ is linear in the weights
    $w$, which is all the normal equations need. It is a quadratic in area, but a linear model in the features
    $(1,\text{area},\text{area}^2)$. (Note how different the column scales are: standardise before gradient descent.)

??? question "5. A least-squares Hessian H has eigenvalues 0.2, 1 and 8. What learning rates make gradient descent converge? Which fixed rate is fastest, and by what factor does the slowest error component shrink per step at that rate?"

    Converges for $0<\eta<2/8=0.25$. The best fixed rate is $2/(0.2+8)\approx0.2439$, giving
    $\rho=(\kappa-1)/(\kappa+1)$ with $\kappa=40$: $39/41\approx0.951$ per step for the error (and $\rho^2\approx0.905$ for
    the loss gap). Check: $|1-0.2439\times0.2|=0.951$ and $|1-0.2439\times8|=0.951$; the eigenvalue 1 gives $0.756$.

??? question "6. Write the code: gradient descent for a straight line on the ten flats, with the area standardised, and the result converted back to original units."

    ```python
    import numpy as np
    from ch04_line_fit import AREA, PRICE

    mu, sd = AREA.mean(), AREA.std()
    X = np.column_stack([np.ones(10), (AREA - mu) / sd])
    w = np.zeros(2)
    for _ in range(100):
        w -= 0.5 * 2 * X.T @ (X @ w - PRICE) / 10
    slope = w[1] / sd
    intercept = w[0] - slope * mu
    print(round(intercept, 3), round(slope, 4))    # -7.592 3.7966
    ```

    With standardised area the Hessian is $2I$ (the columns are orthogonal, each with mean square 1), so $\eta=0.5$
    solves it in one step; the 100 steps are for show. The answer matches the exact one from 4.1.

??? question "7. Suppose the noise in y = x w + epsilon has the Laplace density (1/(2b)) exp(-|epsilon|/b). Show that maximum likelihood for w is least absolute deviations."

    The log-likelihood is $\sum_i\bigl(-\ln(2b)-|y_i-x_i\cdot w|/b\bigr)=-n\ln(2b)-\frac1b\sum_i|y_i-x_i\cdot w|$. For fixed
    $b$, maximising it over $w$ is minimising $\sum_i|y_i-x_i\cdot w|$. With only an intercept, the answer is the
    median (section 4.1), just as Gaussian noise gives the mean.

??? question "8. Prove that adding a feature to a least-squares model can never increase the training SSE."

    Let $S_{\text{old}}$ be the minimum SSE with the old columns, reached at $\hat w$. With the new column added, the
    weight vector $(\hat w,0)$ is allowed and gives exactly the old predictions, so SSE $=S_{\text{old}}$. The new
    minimum is at most the value at any allowed point, so it is at most $S_{\text{old}}$. Hence training $R^2$ never
    decreases, even when the new feature is pure noise.

??? question "9. In the two-feature flats model the rooms weight is -8.49, but alone it is +69.52. Explain the difference, and say what it implies for interpreting weights."

    Alone, rooms is a proxy for size, so it absorbs the effect of area. With area in the model, the rooms weight
    measures the effect of an extra room at fixed area, which here is slightly negative. The weight of a feature
    depends on which other features are in the model, especially correlated ones (here $r=0.852$). With so few flats,
    the $-8.49$ is also very uncertain. A weight is never "the effect of a feature" on its own.

??? question "10. Write the code: choose the polynomial degree for the sine data by a validation set."

    ```python
    import numpy as np
    rng = np.random.default_rng(11)
    x = rng.uniform(0, 1, 60)
    y = np.sin(2 * np.pi * x) + rng.normal(0, 0.2, 60)
    xt, yt, xv, yv = x[:40], y[:40], x[40:], y[40:]
    def design(x, d):
        return np.column_stack([x ** k for k in range(d + 1)])
    for d in range(10):
        w = np.linalg.lstsq(design(xt, d), yt, rcond=None)[0]
        rmse = np.sqrt(np.mean((design(xv, d) @ w - yv) ** 2))
        print(d, round(rmse, 3))
    ```

    Run it and it prints the validation RMSE for degrees 0 to 9: 0.762, 0.577, 0.598, 0.27, 0.272, 0.185, 0.204,
    0.217, 0.219, 0.216. It falls sharply at degree 3, is smallest at degree 5, close to the noise level of 0.2, and
    then creeps up. Pick degree 5 (or degree 3, if you prefer a simpler model and accept a slightly larger error). The
    training RMSE, by contrast, keeps falling with every degree, from 0.762 to 0.139. With only 20 validation points
    these numbers are noisy; Chapter 7's cross-validation makes the choice more reliable.

??? question "11. A design matrix has singular values 100, 10 and 0.001. What is its condition number, and that of X^T X? Roughly how many correct digits can you expect from QR and from the normal equations?"

    $\kappa(X)=100/0.001=10^5$ and $\kappa(X^\top X)=10^{10}$. From about 16 digits, QR keeps roughly $16-5=11$ and the
    normal equations roughly $16-10=6$. Either way the weight along the third singular direction is very sensitive to
    noise in $y$ (it is divided by 0.001), which is a statistical problem no solver can fix.

??? question "12. For X with columns (1, 1, 1, 1) and (1, 2, 1, 2), compute Q and R by Gram-Schmidt and solve the least-squares problem for y = (2, 4, 3, 5)."

    $r_{11}=\lVert a_1\rVert=2$, $q_1=(1,1,1,1)/2$. $r_{12}=q_1\cdot a_2=6/2=3$. $a_2-3q_1=(1,2,1,2)-(1.5,1.5,1.5,1.5)=
    (-0.5,0.5,-0.5,0.5)$, of length $1$, so $r_{22}=1$ and $q_2=(-0.5,0.5,-0.5,0.5)$. $Q^\top y=(14/2,\;(-2+4-3+5)/2)=(7,2)$.
    Back substitution: $w_2=2/1=2$, $w_1=(7-3\times2)/2=0.5$. Check with the normal equations: the fit
    $0.5+2x$ predicts $2.5,4.5,2.5,4.5$, residuals $-0.5,-0.5,0.5,0.5$, which add to zero and have dot product
    $-0.5-1+0.5+1=0$ with the second column.

## What you learned

- Least squares chooses the weights that minimise the sum of squared residuals; for one feature,
  $w_1=S_{xy}/S_{xx}$ and the line passes through the means. The mean minimises squared error and the median absolute
  error.
- The normal equations $X^\top Xw=X^\top y$ say the residual is orthogonal to every column: the fit is the projection of
  $y$ onto the column space, and Pythagoras proves it is the global minimum, unique when the columns are independent.
- Linear regression is linear in the weights, so polynomial and other engineered features fit curves; training error
  always falls with more features, and validation error reveals overfitting.
- Gradient descent on least squares converges exactly when $0<\eta<2/\lambda_{\max}$, at a rate governed by the
  condition number, which is why scaling matters.
- With independent Gaussian noise of constant variance, least squares is maximum likelihood; Laplace noise gives
  absolute error, and other noise models give other losses.
- A weight is an effect with the other features held fixed in the model; $R^2=1-\mathrm{SSE}/\mathrm{SST}$ is the
  explained fraction of variance; residual plots reveal missing curves and unequal noise.
- Forming $X^\top X$ squares the condition number; QR and SVD solvers work on $X$ directly, and the pseudo-inverse gives
  the minimum-norm solution when columns are dependent.

**Next:** [Chapter 5](05-Optimization.md), optimization for learning: convex functions, the convergence of gradient
descent beyond least squares, stochastic gradients, momentum and Adam.

## Further reading

- A.-M. Legendre, *Nouvelles méthodes pour la détermination des orbites des comètes*, 1805 (the appendix on least
  squares); C. F. Gauss, *Theoria motus corporum coelestium*, 1809.
- S. M. Stigler, "Gauss and the Invention of Least Squares", *Annals of Statistics*, 1981; S. M. Stigler, *The History
  of Statistics*, 1986.
- T. Hastie, R. Tibshirani and J. Friedman, *The Elements of Statistical Learning*, 2nd ed., 2009, Chapter 3 (linear
  methods for regression, including QR and Gram-Schmidt).
- C. M. Bishop, *Pattern Recognition and Machine Learning*, 2006, Chapter 3 (linear models, the maximum-likelihood
  view).
- K. P. Murphy, *Probabilistic Machine Learning: An Introduction*, 2022, Chapter 11 (linear regression).
- G. H. Golub and C. F. Van Loan, *Matrix Computations*, 4th ed., 2013: QR, the SVD and least squares, with the
  error analysis.
- N. J. Higham, *Accuracy and Stability of Numerical Algorithms*, 2nd ed., 2002.
- L. N. Trefethen and D. Bau, *Numerical Linear Algebra*, 1997: a readable account of Householder QR and conditioning.
- On this site: [Chapter 3](03-The-Math-Toolkit.md) for projections, gradients and the SVD;
  [Chapter 11 of the Algorithms book](../algorithms/11-Divide-and-Conquer.md) for fast matrix multiplication; for the
  math, [linear algebra](https://math.akadian.ca/books/linear-algebra/) and
  [statistics](https://math.akadian.ca/books/statistics/) at math.akadian.ca.
