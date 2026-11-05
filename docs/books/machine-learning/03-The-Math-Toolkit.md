# 3. The math you need, built as you go

*Every method in this book is written in four languages at once: vectors and matrices for the data, derivatives for
learning, probability for noise and uncertainty, and information for measuring how wrong a prediction is. This
chapter builds just enough of each, from the definitions up, with a reason for every rule and a few lines of NumPy
for every idea. You will see the dot product as a measure of similarity, a matrix as a table and as a map,
the gradient as the direction of steepest climb, Bayes' rule and maximum likelihood, the eigenvectors and singular
values that describe the shape of data, and entropy and KL divergence, the measures behind almost every loss
function.*

!!! abstract "In this chapter"
    **You will learn:**

    - vectors, dot products, norms and the Cauchy-Schwarz inequality, and why cosine similarity works
    - matrices as data tables and as maps, matrix multiplication as composition, and NumPy broadcasting
    - derivatives, partial derivatives and gradients, the chain rule, the gradient of the squared error, and how to
      check any gradient numerically
    - random variables, expectation, variance, the Bernoulli and Gaussian distributions, and Bayes' rule
    - likelihood and maximum likelihood, with the estimates for a coin and a Gaussian derived
    - (intermediate) eigenvectors, power iteration and the singular value decomposition
    - (intermediate) entropy, cross-entropy and KL divergence, and why KL is never negative

    **You need:** [Chapter 1](01-What-Is-Machine-Learning.md) and [Chapter 2](02-Data-and-Features.md), school algebra
    and the idea of a slope. The math books go much further:
    [linear algebra](https://math.akadian.ca/books/linear-algebra/), [calculus](https://math.akadian.ca/books/calculus/),
    [probability](https://math.akadian.ca/books/probability/) and
    [statistics](https://math.akadian.ca/books/statistics/).

    **Levels:** 3.1 to 3.5 are beginner to intermediate; 3.6 and 3.7 are intermediate. On a first read you can skip
    3.6 and 3.7 and come back when Chapters 4 (section 4.7), 6 and 14 send you here.

## 3.1 Vectors and dot products

How do we say, with numbers, that two things are similar? Chapter 1 used distance. This section adds a second
measure, the dot product, and the tools around it.

A **vector** is an ordered list of numbers, $u=(u_1,u_2,\dots,u_m)$. The number $m$ is its **dimension**. In this
book a vector is usually one row of a data table, a feature vector, or a list of model weights. With $m=2$ or $3$ you
can draw it, either as a point or as an arrow from the origin to that point; with $m=784$ (a small image) you cannot
draw it, but every rule below works the same way.

Two operations come first. **Addition** adds entry by entry: $(3,4)+(4,3)=(7,7)$. **Scalar multiplication**
multiplies every entry by one number (a **scalar**): $2\cdot(3,4)=(6,8)$. As arrows, adding means placing one
arrow after the other, and multiplying by 2 doubles the length without changing the direction.

### The dot product

The **dot product** (or inner product) of two vectors of the same dimension multiplies them entry by entry and adds:

$$
u\cdot v=u_1v_1+u_2v_2+\dots+u_mv_m=\sum_{j=1}^m u_jv_j .
$$

For $u=(3,4)$ and $v=(4,3)$: $u\cdot v=12+12=24$. Other common notations are $\langle u,v\rangle$ and, when vectors are
written as columns, $u^\top v$ (section 3.2 explains the $\top$).

The dot product of a vector with itself is the sum of its squared entries, which by Pythagoras' theorem is its
squared length. So the **length**, or **Euclidean norm**, is

$$
\lVert u\rVert=\sqrt{u\cdot u}=\sqrt{u_1^2+\dots+u_m^2},
$$

and the distance between two points is $\lVert u-v\rVert$, the formula from Chapter 1. For $u=(3,4)$,
$\lVert u\rVert=\sqrt{9+16}=5$.

**What the dot product measures.** The key fact is geometric:

$$
u\cdot v=\lVert u\rVert\,\lVert v\rVert\cos\theta,
$$

where $\theta$ is the angle between the arrows. *Why:* the three points $0$, $u$, $v$ form a triangle whose sides have
lengths $\lVert u\rVert$, $\lVert v\rVert$ and $\lVert u-v\rVert$. The law of cosines from school geometry says
$\lVert u-v\rVert^2=\lVert u\rVert^2+\lVert v\rVert^2-2\lVert u\rVert\lVert v\rVert\cos\theta$. Expanding the left side
with the dot product, $(u-v)\cdot(u-v)=u\cdot u-2\,u\cdot v+v\cdot v$. Comparing the two expressions gives the
formula. $\square$

So the dot product is large and positive when two vectors point the same way, zero when they are at right angles
(**orthogonal**), and negative when they point in opposite directions. Dividing out the lengths leaves the
**cosine similarity**:

$$
\cos\theta=\frac{u\cdot v}{\lVert u\rVert\,\lVert v\rVert}.
$$

For $(3,4)$ and $(4,3)$ it is $24/25=0.96$, an angle of about $16.26^\circ$: nearly the same direction.

<figure class="mars-fig" markdown="0">
<svg viewBox="0 0 640 260" role="img" aria-label="Two arrows from the origin: u to the point 6, 2 and v to the point 2, 4, with the angle theta between them. A dashed line drops from the tip of v at right angles onto u, meeting it at the point 3, 1, which is the projection of v onto u. On the right, the formulas: u dot v equals 20, the length of u times the length of v times cos theta; the projection is (u dot v over u dot u) times u.">
  <line x1="40" y1="230" x2="340" y2="230" stroke="currentColor" stroke-opacity="0.4"/>
  <line x1="60" y1="245" x2="60" y2="40" stroke="currentColor" stroke-opacity="0.4"/>
  <line x1="60" y1="230" x2="296" y2="151" stroke="#eea66f" stroke-width="3"/>
  <polygon points="300,150 287,148 291,159" fill="#eea66f"/>
  <text x="306" y="150" font-size="14" fill="currentColor">u = (6, 2)</text>
  <line x1="60" y1="230" x2="138" y2="74" stroke="#9cc9ea" stroke-width="3"/>
  <polygon points="140,70 131,79 142,83" fill="#9cc9ea"/>
  <text x="146" y="66" font-size="14" fill="currentColor">v = (2, 4)</text>
  <line x1="140" y1="70" x2="180" y2="190" stroke="currentColor" stroke-dasharray="5 4"/>
  <path d="M 171.5 192.8 L 168.7 184.3 L 177.2 181.5" fill="none" stroke="currentColor"/>
  <circle cx="180" cy="190" r="4" fill="#7ccf9a" stroke="currentColor"/>
  <text x="188" y="212" font-size="13" fill="currentColor">projection (3, 1)</text>
  <path d="M 100 217 A 42 42 0 0 0 79 193" fill="none" stroke="currentColor"/>
  <text x="104" y="200" font-size="14" fill="currentColor">θ</text>
  <text x="400" y="80" font-size="14" fill="currentColor">u · v = 6·2 + 2·4 = 20</text>
  <text x="400" y="108" font-size="14" fill="currentColor">= |u| |v| cos θ</text>
  <text x="400" y="136" font-size="14" fill="currentColor">cos θ = 20 / (√40 · √20) ≈ 0.707</text>
  <text x="400" y="164" font-size="14" fill="currentColor">projection of v on u:</text>
  <text x="400" y="190" font-size="14" fill="currentColor">(u·v / u·u) u = (20/40) u</text>
</svg>
<figcaption>The dot product measures how much two vectors point the same way. The projection of v onto u is the
shadow of v on the line through u; the dashed line meets u at a right angle. Here the angle is 45 degrees.</figcaption>
</figure>

**Projection.** The figure shows a second use. The **projection** of $v$ onto the line through $u$ is the point on
that line nearest to $v$, and it is $\frac{u\cdot v}{u\cdot u}\,u$. For $u=(6,2)$, $v=(2,4)$: $u\cdot v=20$,
$u\cdot u=40$, so the projection is $\tfrac12(6,2)=(3,1)$. *Why it is the nearest point:* the leftover
$v-\tfrac12u=(-1,3)$ has dot product $-6+6=0$ with $u$, so it is at right angles to the line, and by Pythagoras any other
point of the line is farther away. Projection is the whole idea of least squares in Chapter 4.

### Norms

A **norm** is a way to measure the size of a vector. Besides the Euclidean norm (also called the **L2 norm**,
$\lVert u\rVert_2$), two others appear constantly.

- The **L1 norm** adds absolute values: $\lVert u\rVert_1=|u_1|+\dots+|u_m|$. It is the distance a taxi drives on a
  grid of streets, so the distance it gives is called the **Manhattan distance**. It appears in Chapter 8 as the lasso
  penalty.
- The **L-infinity norm** takes the largest absolute value: $\lVert u\rVert_\infty=\max_j|u_j|$.

For $w=(1,-2,2)$: $\lVert w\rVert_1=5$, $\lVert w\rVert_2=\sqrt{1+4+4}=3$, $\lVert w\rVert_\infty=2$. Every norm is zero
only for the zero vector, scales with scalars ($\lVert cu\rVert=|c|\lVert u\rVert$), and obeys the triangle
inequality, proved below for L2.

### Cauchy-Schwarz and the triangle inequality

The formula $u\cdot v=\lVert u\rVert\lVert v\rVert\cos\theta$ used a triangle drawn in a plane. Does it make sense in
784 dimensions, where we cannot draw an angle? It does, because of an inequality that we can prove in any dimension.

**Theorem (Cauchy-Schwarz).** For any vectors $u$, $v$ of the same dimension, $|u\cdot v|\le\lVert u\rVert\,\lVert
v\rVert$, with equality exactly when one is a multiple of the other.

**Proof.** If $v=0$ both sides are 0. Otherwise, for every number $t$, the vector $u-tv$ has a squared length that is
not negative:

$$
0\le\lVert u-tv\rVert^2=\lVert u\rVert^2-2t\,(u\cdot v)+t^2\lVert v\rVert^2 .
$$

The right side is a quadratic in $t$ that is never negative, so it has at most one real root, which means its
discriminant is at most zero: $4(u\cdot v)^2-4\lVert u\rVert^2\lVert v\rVert^2\le0$. Taking square roots gives the
inequality. Equality means the quadratic touches zero, so $u-tv=0$ for some $t$. $\square$

So $(u\cdot v)/(\lVert u\rVert\lVert v\rVert)$ always lies between $-1$ and $1$, and we may *define* the angle in any
dimension as the angle with that cosine. The program checks 10 000 random pairs in 10 dimensions: the largest
$|\cos\theta|$ it finds is 0.9396, below 1 as it must be.

**Corollary (triangle inequality).** $\lVert u+v\rVert\le\lVert u\rVert+\lVert v\rVert$. *Proof:* $\lVert
u+v\rVert^2=\lVert u\rVert^2+2\,u\cdot v+\lVert v\rVert^2\le\lVert u\rVert^2+2\lVert u\rVert\lVert v\rVert+\lVert
v\rVert^2=(\lVert u\rVert+\lVert v\rVert)^2$, using Cauchy-Schwarz in the middle. $\square$

**Corollary (correlation lies in [-1, 1]).** Chapter 2 promised this. The correlation of two columns is exactly the
cosine of the angle between the *centred* columns $x-\bar x$ and $y-\bar y$ (look at its formula: dot product on top,
product of norms below), so Cauchy-Schwarz gives $|r|\le1$, with $|r|=1$ exactly when one centred column is a multiple
of the other, that is, when the points lie on a line. $\square$

### Cosine similarity in practice

Why use the angle instead of the distance? Because often only the *direction* matters. The program describes three
short documents by counts of five words (dust, storm, rover, wheel, solar). Document B is document A written out
twice, so its counts are doubled: $A=(2,1,0,0,1)$, $B=(4,2,0,0,2)$. Their distance is $\sqrt{4+1+1}\approx2.45$, but
their cosine similarity is exactly 1: they say the same thing at different lengths. Document C, $(0,0,3,2,0)$, shares
no word with A, so $A\cdot C=0$ and the cosine is 0. Search engines and the word embeddings of Chapter 18 compare text
this way.

```python
--8<-- "books/machine-learning/ch03_vectors.py"
```

Output:

```
u = [3, 4]  v = [4, 3]
dot = 24  |u| = 5.0  |v| = 5.0  cos = 0.96  angle = 16.26 deg
w = [1, -2, 2]  L1 = 5  L2 = 3.0  Linf = 2
cosine A,B = 1.0  cosine A,C = 0.0  distance A,B = 2.4495
largest |cos| over 10000 random pairs in 10-D: 0.9396
A B with loops: [[5, 2, -1], [11, 4, -3], [17, 6, -5]]
A B with NumPy: [[5, 2, -1], [11, 4, -3], [17, 6, -5]]
B A with NumPy: [[-4, -4], [5, 8]]
S (R p) = [-2  1]  (S R) p = [-2  1]  (R S) p = [-1  2]
X @ w + 30 = [199.6 276.  154. ]
column means: [55.66666667  2.        ]  centred:
 [[ -3.66666667   0.        ]
 [ 19.33333333   1.        ]
 [-15.66666667  -1.        ]]
shapes (3,1) + (1,4) -> (3, 4)
[[ 0  1  2  3]
 [10 11 12 13]
 [20 21 22 23]]
```

<figure class="play" data-play="dotprod"><span class="ai-tag">AI-created</span><figcaption><b>Try it.</b> Tap to move the tip of the blue vector: the dot product is positive when the arrows point the same way, zero at a right angle, negative when they point apart.</figcaption></figure>

## 3.2 Matrices: tables and maps

What is a matrix? Two answers, both essential. A **matrix** is a rectangular table of numbers with $n$ rows and $m$
columns, an $n\times m$ matrix; the entry in row $i$ and column $j$ of $A$ is written $A_{ij}$. The first answer is the
one from Chapter 2: **a matrix is a data table**, the feature matrix $X$ with one row per example. The second answer is
the one that makes matrices powerful: **a matrix is a map** that turns vectors into vectors.

### Matrix times vector

Multiply an $n\times m$ matrix $A$ by a vector $x$ of dimension $m$ and you get a vector $Ax$ of dimension $n$. There
are two ways to see what it is, and both are worth keeping in mind.

- **Row view:** entry $i$ of $Ax$ is the dot product of row $i$ of $A$ with $x$: $(Ax)_i=\sum_jA_{ij}x_j$.
- **Column view:** $Ax$ is a weighted sum of the columns of $A$, with weights $x_1,\dots,x_m$:
  $Ax=x_1(\text{column }1)+\dots+x_m(\text{column }m)$.

The row view is the one for data. If $X$ is the table of flats with columns area and rooms, and $w=(2.8,12)$ is a list
of weights, then $Xw$ is the list of numbers $2.8\cdot\text{area}+12\cdot\text{rooms}$, one per flat: a prediction
for every row in one operation. The program computes $Xw+30=(199.6,\,276,\,154)$ for three flats. Every linear model
in this book predicts this way.

The column view is the one for maps. Take the unit vectors $e_1=(1,0)$ and $e_2=(0,1)$. By the column view, $Ae_1$
is the first column of $A$ and $Ae_2$ is the second. Any $x=(x_1,x_2)$ equals $x_1e_1+x_2e_2$, so $Ax=x_1Ae_1+x_2Ae_2$:
once you know where the unit vectors go, you know where everything goes. A map with this property,
$A(cx+dy)=cAx+dAy$, is called **linear**. It sends lines to lines and the origin to itself, and turns squares into
parallelograms.

<figure class="mars-fig" markdown="0">
<svg viewBox="0 0 640 230" role="img" aria-label="Left: the unit square with sides e1 along x and e2 along y. An arrow labelled A leads to the right, where the square has become a parallelogram whose sides are the columns of A: A e1 equals 2, 0.5 and A e2 equals 1, 1.5.">
  <line x1="30" y1="190" x2="230" y2="190" stroke="currentColor" stroke-opacity="0.35"/>
  <line x1="50" y1="210" x2="50" y2="30" stroke="currentColor" stroke-opacity="0.35"/>
  <rect x="50" y="130" width="60" height="60" fill="#9cc9ea" fill-opacity="0.4" stroke="currentColor"/>
  <line x1="50" y1="190" x2="110" y2="190" stroke="#eea66f" stroke-width="3"/>
  <line x1="50" y1="190" x2="50" y2="130" stroke="#7ccf9a" stroke-width="3"/>
  <text x="100" y="208" font-size="13" fill="currentColor">e1</text>
  <text x="26" y="140" font-size="13" fill="currentColor">e2</text>
  <line x1="250" y1="120" x2="320" y2="120" stroke="currentColor" stroke-width="1.5"/>
  <polygon points="328,120 318,115 318,125" fill="currentColor"/>
  <text x="288" y="108" font-size="14" text-anchor="middle" fill="currentColor">A</text>
  <text x="288" y="145" font-size="12" text-anchor="middle" fill="currentColor">A = [[2, 1], [0.5, 1.5]]</text>
  <line x1="350" y1="190" x2="630" y2="190" stroke="currentColor" stroke-opacity="0.35"/>
  <line x1="370" y1="210" x2="370" y2="30" stroke="currentColor" stroke-opacity="0.35"/>
  <polygon points="370,190 490,160 550,70 430,100" fill="#9cc9ea" fill-opacity="0.4" stroke="currentColor"/>
  <line x1="370" y1="190" x2="490" y2="160" stroke="#eea66f" stroke-width="3"/>
  <line x1="370" y1="190" x2="430" y2="100" stroke="#7ccf9a" stroke-width="3"/>
  <text x="496" y="172" font-size="13" fill="currentColor">A e1 = (2, 0.5)</text>
  <text x="336" y="84" font-size="13" fill="currentColor">A e2 = (1, 1.5)</text>
</svg>
<figcaption>A matrix as a map. The columns of A say where the unit vectors go; every other vector follows by
linearity, so the unit square becomes a parallelogram.</figcaption>
</figure>

### Matrix times matrix

The product $AB$ of an $n\times k$ matrix $A$ and a $k\times m$ matrix $B$ is the $n\times m$ matrix with entries

$$
(AB)_{ij}=\sum_{t=1}^kA_{it}B_{tj},
$$

the dot product of row $i$ of $A$ with column $j$ of $B$. The inner sizes must agree ($k$ and $k$). The program
computes it with three nested loops and with NumPy's `@` operator, and they agree.

**Why this strange rule?** Because it is composition of maps. Applying $B$ and then $A$ to a vector $x$ gives
$A(Bx)$, and the rule is exactly what makes $A(Bx)=(AB)x$. (*Check:* entry $i$ of $A(Bx)$ is
$\sum_tA_{it}(Bx)_t=\sum_tA_{it}\sum_jB_{tj}x_j=\sum_j\bigl(\sum_tA_{it}B_{tj}\bigr)x_j$, which is entry $i$ of
$(AB)x$.) Two consequences follow at once.

- **Associativity**: $(AB)C=A(BC)$, because both mean "apply $C$, then $B$, then $A$". This lets us choose the cheaper
  order of multiplication, which matters a lot in practice (the Algorithms book's
  [Chapter 13](../algorithms/13-Dynamic-Programming.md) solves the problem of the best order).
- **Not commutative**: in general $AB\ne BA$. In the program, $BA$ is $2\times2$ while $AB$ is $3\times3$; even for
  square maps, "rotate a quarter turn, then stretch $x$ by 2" sends $(1,1)$ to $(-2,1)$, while "stretch, then rotate"
  sends it to $(-1,2)$.

The **cost**: each of the $nm$ entries needs $k$ multiplications, so $nkm$ in all; two $n\times n$ matrices cost $n^3$.
(Faster methods exist; [Chapter 11 of the Algorithms book](../algorithms/11-Divide-and-Conquer.md) builds Strassen's.)
NumPy calls highly tuned libraries, so `@` is thousands of times faster than the Python loops, but it does the same
arithmetic.

### Transpose, identity, inverse

The **transpose** $A^\top$ swaps rows and columns: $(A^\top)_{ij}=A_{ji}$. A vector written as a column, $u$, becomes a
row, $u^\top$, and then $u^\top v$ is the dot product. A useful rule: $(AB)^\top=B^\top A^\top$ (the order reverses,
which you can check from the entry formula). Two products of the feature matrix with its own transpose appear
everywhere: $X^\top X$, an $m\times m$ table of dot products between *columns* (features), and $XX^\top$, an $n\times n$
table of dot products between *rows* (examples). Chapter 4 is built on the first; Chapter 9's kernels on the second.
A matrix with $A^\top=A$ is **symmetric**; $X^\top X$ always is.

The **identity matrix** $I$ has 1s on the diagonal and 0s elsewhere; $Ix=x$ for every $x$. A square matrix $A$ has an
**inverse** $A^{-1}$ if $A^{-1}A=AA^{-1}=I$, meaning the map can be undone. Not every matrix can: the map that squashes
the plane onto a line loses information. A square matrix has an inverse exactly when its columns are
**linearly independent** (no column is a weighted sum of the others), which was the issue with one-hot columns and an
intercept in Chapter 2.

### NumPy broadcasting

NumPy lets you combine arrays of different shapes without writing loops, by a rule called **broadcasting**. Compare
the shapes from the right. Two sizes are compatible if they are equal or one of them is 1; a size-1 dimension is
stretched (conceptually copied) to match. Missing dimensions on the left count as size 1.

- `X - X.mean(axis=0)`: `X` has shape (3, 2), the means have shape (2,), treated as (1, 2), stretched to (3, 2). Every
  row has the column means subtracted: centring in one line.
- `a[:, None] + b[None, :]` with `a` of shape (3,) and `b` of shape (4,): shapes (3, 1) and (1, 4) give (3, 4), the
  table of all sums $a_i+b_j$. The program prints $10i+j$.

Chapter 1's nearest-neighbour code used the same trick, `Xq[:, None, :] - Xtr[None, :, :]`, to compute every query
point minus every training point at once. Broadcasting is convenient and fast, but it can silently produce a huge
array (shape $(n_\text{query}, n_\text{train}, m)$ there) or silently combine shapes you did not mean to combine. When
in doubt, print `.shape`.

## 3.3 Derivatives, gradients and the chain rule

How does a learner know which way to change its parameters? It asks: if I nudge this number a little, does the loss
go up or down, and by how much? That question is a derivative.

### Derivatives

The **derivative** of a function $f$ at a point $x$ is the slope of its graph there:

$$
f'(x)=\lim_{h\to0}\frac{f(x+h)-f(x)}{h}.
$$

The fraction is the slope of the straight line (a **secant**) through the points at $x$ and $x+h$. As $h$ shrinks, the
secant turns into the **tangent**, the line that just touches the graph at $x$, and its slope is $f'(x)$. Near $x$,

$$
f(x+h)\approx f(x)+f'(x)\,h ,
$$

so the derivative says how much $f$ changes per unit change of $x$, for small changes. If $f'(x)>0$, increasing $x$
increases $f$; to *decrease* $f$, move $x$ the other way. That one sentence is gradient descent.

<figure class="mars-fig" markdown="0">
<svg viewBox="0 0 640 280" role="img" aria-label="The graph of f of x equals x cubed minus 2 x, for x from minus 2 to 2.2. At x equals 1.5 an orange tangent line touches the curve with slope 4.75. A dashed secant line through x equals 1.5 and x equals 2.1 is steeper, with slope 7.81. As h shrinks the secant turns into the tangent.">
  <line x1="60.0" y1="165.9" x2="400.0" y2="165.9" stroke="currentColor"/>
  <line x1="221.9" y1="260.0" x2="221.9" y2="30.0" stroke="currentColor"/>
  <path d="M 60.0 249.5 L 62.9 242.3 L 65.7 235.4 L 68.6 228.8 L 71.4 222.5 L 74.3 216.4 L 77.1 210.7 L 80.0 205.2 L 82.9 200.0 L 85.7 195.1 L 88.6 190.5 L 91.4 186.1 L 94.3 181.9 L 97.1 178.0 L 100.0 174.3 L 102.9 170.9 L 105.7 167.7 L 108.6 164.7 L 111.4 162.0 L 114.3 159.4 L 117.1 157.1 L 120.0 155.0 L 122.9 153.0 L 125.7 151.3 L 128.6 149.7 L 131.4 148.4 L 134.3 147.2 L 137.1 146.1 L 140.0 145.3 L 142.9 144.5 L 145.7 144.0 L 148.6 143.6 L 151.4 143.3 L 154.3 143.2 L 157.1 143.2 L 160.0 143.3 L 162.9 143.5 L 165.7 143.9 L 168.6 144.3 L 171.4 144.9 L 174.3 145.6 L 177.1 146.3 L 180.0 147.2 L 182.9 148.1 L 185.7 149.1 L 188.6 150.1 L 191.4 151.3 L 194.3 152.5 L 197.1 153.7 L 200.0 155.0 L 202.9 156.3 L 205.7 157.7 L 208.6 159.1 L 211.4 160.5 L 214.3 162.0 L 217.1 163.5 L 220.0 164.9 L 222.9 166.4 L 225.7 167.9 L 228.6 169.3 L 231.4 170.8 L 234.3 172.2 L 237.1 173.6 L 240.0 175.0 L 242.9 176.4 L 245.7 177.7 L 248.6 178.9 L 251.4 180.1 L 254.3 181.3 L 257.1 182.4 L 260.0 183.4 L 262.9 184.4 L 265.7 185.2 L 268.6 186.0 L 271.4 186.7 L 274.3 187.3 L 277.1 187.8 L 280.0 188.2 L 282.9 188.5 L 285.7 188.6 L 288.6 188.7 L 291.4 188.6 L 294.3 188.4 L 297.1 188.0 L 300.0 187.5 L 302.9 186.8 L 305.7 186.0 L 308.6 185.0 L 311.4 183.9 L 314.3 182.6 L 317.1 181.1 L 320.0 179.4 L 322.9 177.5 L 325.7 175.4 L 328.6 173.2 L 331.4 170.7 L 334.3 168.0 L 337.1 165.1 L 340.0 162.0 L 342.9 158.6 L 345.7 155.1 L 348.6 151.2 L 351.4 147.2 L 354.3 142.9 L 357.1 138.3 L 360.0 133.4 L 362.9 128.3 L 365.7 123.0 L 368.6 117.3 L 371.4 111.4 L 374.3 105.2 L 377.1 98.7 L 380.0 91.8 L 382.9 84.7 L 385.7 77.3 L 388.6 69.5 L 391.4 61.5 L 394.3 53.1 L 397.1 44.3 L 400.0 35.3" fill="none" stroke="#9cc9ea" stroke-width="2.5"/>
  <path d="M 298.8 212.7 L 387.9 103.4" stroke="#eea66f" stroke-width="2"/>
  <path d="M 302.9 239.7 L 400.0 43.8" stroke="currentColor" stroke-dasharray="5 4"/>
  <circle cx="343.3" cy="158.1" r="4" fill="#eea66f" stroke="currentColor"/>
  <circle cx="391.9" cy="60.1" r="4" fill="currentColor"/>
  <text x="420" y="70" font-size="13" fill="currentColor">f(x) = x³ − 2x</text>
  <line x1="420" y1="100" x2="450" y2="100" stroke="#eea66f" stroke-width="2"/>
  <text x="458" y="104" font-size="13" fill="currentColor">tangent at x = 1.5:</text>
  <text x="458" y="122" font-size="13" fill="currentColor">slope f′(1.5) = 4.75</text>
  <line x1="420" y1="150" x2="450" y2="150" stroke="currentColor" stroke-dasharray="5 4"/>
  <text x="458" y="154" font-size="13" fill="currentColor">secant, h = 0.6:</text>
  <text x="458" y="172" font-size="13" fill="currentColor">slope 7.81</text>
  <text x="420" y="210" font-size="13" fill="currentColor">smaller h: secant → tangent</text>
  <text x="402" y="170" font-size="12" fill="currentColor">x</text>
</svg>
<figcaption>The derivative is the slope of the tangent. A secant through two nearby points approximates it, and the
approximation improves as the points come together.</figcaption>
</figure>

You will need only a few rules, each provable from the definition: the derivative of $x^k$ is $kx^{k-1}$; of $e^x$ is
$e^x$; of $\ln x$ is $1/x$; the derivative of a sum is the sum of the derivatives; constants factor out; and the
**product rule** $(fg)'=f'g+fg'$. For example, $f(x)=x^3-2x$ has $f'(x)=3x^2-2$, so $f'(1.5)=6.75-2=4.75$.

### The chain rule

Most functions in machine learning are built by feeding one function into another: a loss of a prediction of a
weighted sum of features. The **chain rule** says how to differentiate such a composition. If $y=g(x)$ and $z=f(y)$,
then

$$
\frac{dz}{dx}=\frac{dz}{dy}\cdot\frac{dy}{dx},\qquad\text{that is,}\qquad (f\circ g)'(x)=f'(g(x))\,g'(x).
$$

*Why:* a small change $h$ in $x$ changes $y$ by about $g'(x)h$; that change in $y$ changes $z$ by about $f'(y)$ times
itself, so $z$ changes by about $f'(g(x))\,g'(x)\,h$. Rates of change multiply along the chain. (A full proof handles
the case where $g'(x)=0$ with a little more care; see any calculus text.) For example, $(3x+1)^2$ has derivative
$2(3x+1)\cdot3$. Backpropagation in Chapter 15 is nothing but the chain rule applied systematically through a long
chain of functions.

### Partial derivatives and the gradient

A loss usually depends on many parameters at once, $L(w_1,\dots,w_m)$. The **partial derivative**
$\partial L/\partial w_j$ is the ordinary derivative with respect to $w_j$ while every other parameter is held fixed.
Collect all of them into a vector and you get the **gradient**:

$$
\nabla L(w)=\left(\frac{\partial L}{\partial w_1},\dots,\frac{\partial L}{\partial w_m}\right).
$$

Example: $g(w)=w_1^2+3w_1w_2+2w_2^2$. Holding $w_2$ fixed, $\partial g/\partial w_1=2w_1+3w_2$; holding $w_1$ fixed,
$\partial g/\partial w_2=3w_1+4w_2$. At $w=(1,-2)$ the gradient is $(2-6,\,3-8)=(-4,-5)$.

**The gradient points uphill, as steeply as possible.** Move from $w$ a small distance $\varepsilon$ in the direction of a
unit vector $u$. Each coordinate $w_j$ moves by $\varepsilon u_j$, and to first order the changes add up:
$L(w+\varepsilon u)\approx L(w)+\varepsilon\,\nabla L(w)\cdot u$. The rate of change in direction $u$, the
**directional derivative**, is therefore $\nabla L(w)\cdot u$. By Cauchy-Schwarz it is at most
$\lVert\nabla L(w)\rVert\,\lVert u\rVert=\lVert\nabla L(w)\rVert$, with equality exactly when $u$ points along the
gradient. So the gradient is the direction of steepest increase, its length is the steepest rate, and
$-\nabla L(w)$ is the direction of steepest decrease. **Gradient descent** steps that way:
$w\leftarrow w-\eta\nabla L(w)$, with a small step size $\eta$ (the **learning rate**). At a minimum of a smooth
function the gradient is the zero vector, since no direction goes down.

### The gradient of the squared error

Here is the gradient that Chapter 4 uses, derived with nothing but the rules above. A linear model predicts
$\hat y_i=x_i\cdot w$ for each row $x_i$ of $X$, and the **mean squared error** is

$$
L(w)=\frac1n\sum_{i=1}^n\bigl(x_i\cdot w-y_i\bigr)^2=\frac1n\lVert Xw-y\rVert^2 .
$$

Take the partial derivative with respect to one weight $w_j$. The derivative of a sum is the sum of derivatives. In the
$i$-th term, the chain rule gives "2 times the inside, times the derivative of the inside", and the inside,
$x_{i1}w_1+\dots+x_{im}w_m-y_i$, has derivative $x_{ij}$ with respect to $w_j$. So

$$
\frac{\partial L}{\partial w_j}=\frac2n\sum_{i=1}^n\bigl(x_i\cdot w-y_i\bigr)\,x_{ij}.
$$

The sum over $i$ of (residual $i$) times $x_{ij}$ is the dot product of column $j$ of $X$ with the vector of residuals
$Xw-y$, which is entry $j$ of $X^\top(Xw-y)$. All $m$ partial derivatives at once:

$$
\nabla L(w)=\frac2n\,X^\top(Xw-y).
$$

This short formula is worth understanding in words: the gradient is a weighted sum of the feature columns, weighted
by how wrong each prediction is. Features that line up with the errors get the biggest corrections.

### Checking a gradient numerically

Derivations like this are where bugs hide: a missing factor 2, a transpose in the wrong place. Luckily, a gradient
can always be checked against the definition. The **forward difference** $(f(x+h)-f(x))/h$ approximates $f'(x)$; the
**central difference**

$$
\frac{f(x+h)-f(x-h)}{2h}
$$

is much better. *Why:* by Taylor's theorem, $f(x\pm h)=f(x)\pm f'(x)h+\tfrac12f''(x)h^2\pm\tfrac16f'''(x)h^3+\dots$. The
forward difference is then $f'(x)+\tfrac12f''(x)h+\dots$, an error proportional to $h$. In the central difference the
$h^2$ terms cancel, leaving $f'(x)+\tfrac16f'''(x)h^2+\dots$, an error proportional to $h^2$. Halving $h$ halves the
forward error but quarters the central one.

```python
--8<-- "books/machine-learning/ch03_gradients.py"
```

Output:

```
f(x) = x^3 - 2x at x = 1.5: exact derivative 4.75
      h    forward error    central error
   1e-01        4.600e-01        1.000e-02
   1e-02        4.510e-02        1.000e-04
   1e-03        4.501e-03        1.000e-06
   1e-04        4.500e-04        1.000e-08
   1e-06        4.500e-06        4.463e-10
   1e-08        3.775e-08        2.887e-08
   1e-10        3.930e-07        3.930e-07

g(w) = w1^2 + 3 w1 w2 + 2 w2^2 at [ 1. -2.]
  by hand: [-4. -5.]   numerical: [-4. -5.]

mean squared error gradient
  by hand:   [-2.296515 -5.871753  3.059693]
  numerical: [-2.296515 -5.871753  3.059693]
  relative difference 6.1e-12
  buggy gradient's relative difference 0.33
```

The table confirms the theory precisely. For $f(x)=x^3-2x$ we have $f''(x)=6x=9$ and $f'''=6$, so the forward error is
$4.5h+h^2$ (0.46 at $h=0.1$) and the central error is exactly $h^2$ (0.01, 0.0001, ...). But the errors stop shrinking
around $h=10^{-6}$ to $10^{-8}$ and then *grow*. That is **rounding error**: a computer stores about 16 significant
digits, so $f(x+h)-f(x-h)$ loses digits when the two values are nearly equal, and dividing by a tiny $2h$ magnifies
the loss. The best $h$ balances the two errors; for central differences in double precision, $h$ around $10^{-5}$ is a
good default.

To compare a derived gradient $a$ with a numerical one $b$, use the **relative difference**
$\lVert a-b\rVert/\lVert a+b\rVert$, which does not depend on the scale of the loss. Values around $10^{-7}$ or smaller
mean the derivation is right; the program gets $6\times10^{-12}$ for the squared-error gradient. A deliberate bug,
dropping the factor 2, gives 0.33 and is caught at once. Check every gradient you derive, on a small random problem,
before you trust it.

## 3.4 Probability

Why does a book on learning need probability? Because data is noisy, labels are uncertain, and a model that says
"rain, 70% likely" is more useful than one that says "rain". This section collects the definitions we need.

A **random variable** is a quantity whose value is determined by chance: the face of a rolled die, whether a coin
lands heads, tomorrow's temperature. Its **distribution** says how likely each value is. For a **discrete** random
variable (finitely or countably many values) the distribution is a list of probabilities $P(X=x)$ that add up to 1.
For a **continuous** one (any value in a range) it is a **probability density** $p(x)$: the probability of landing
between $a$ and $b$ is the area under $p$ between $a$ and $b$, and the total area is 1.

### Expectation and variance

The **expected value** (or mean) of a discrete random variable is the probability-weighted average of its values:

$$
\mathbb E[X]=\sum_xx\,P(X=x).
$$

For a fair die, $\mathbb E[X]=(1+2+3+4+5+6)/6=3.5$. For a continuous variable the sum becomes an integral,
$\int x\,p(x)\,dx$. The expected value is what the average of many independent draws settles on (this is the **law of
large numbers**); the program's 100 000 rolls average 3.5071.

**Linearity.** For any random variables $X$, $Y$ and numbers $a$, $b$:
$\mathbb E[aX+bY]=a\,\mathbb E[X]+b\,\mathbb E[Y]$. *Proof (discrete case):* $\mathbb E[aX+bY]=\sum_{x,y}(ax+by)P(X=x,Y=y)
=a\sum_xx\sum_yP(x,y)+b\sum_yy\sum_xP(x,y)=a\,\mathbb E[X]+b\,\mathbb E[Y]$, because summing the joint probabilities over
one variable gives the distribution of the other. $\square$ Notice that no independence was needed. Chapter 2's
count of hash collisions used exactly this.

The **variance** measures spread: the expected squared distance from the mean,

$$
\operatorname{Var}(X)=\mathbb E\bigl[(X-\mu)^2\bigr],\qquad \mu=\mathbb E[X].
$$

Expanding the square and using linearity gives the handy form
$\operatorname{Var}(X)=\mathbb E[X^2]-2\mu\,\mathbb E[X]+\mu^2=\mathbb E[X^2]-\mu^2$. For the die,
$\mathbb E[X^2]=91/6$, so $\operatorname{Var}=91/6-12.25=35/12\approx2.9167$. The **standard deviation** is
$\sigma=\sqrt{\operatorname{Var}}$, in the same units as $X$. Two rules: $\operatorname{Var}(aX+b)=a^2\operatorname{Var}(X)$
(shifting does not change spread; scaling by $a$ scales spread by $|a|$), and for **independent** $X$ and $Y$ (knowing
one tells you nothing about the other), $\operatorname{Var}(X+Y)=\operatorname{Var}(X)+\operatorname{Var}(Y)$.

An important consequence: the average $\bar X$ of $n$ independent draws, each with variance $\sigma^2$, has variance
$n\sigma^2/n^2=\sigma^2/n$, so its standard deviation is $\sigma/\sqrt n$. Averages become more precise like
$1/\sqrt n$: to halve the uncertainty of a test-set accuracy you need four times as many test examples. Chapter 7 uses
this to put error bars on scores.

### Two distributions

The **Bernoulli distribution** with parameter $p$ describes one yes-or-no event: $X=1$ with probability $p$ and $X=0$
with probability $1-p$. Then $\mathbb E[X]=p$ and, since $X^2=X$, $\operatorname{Var}(X)=p-p^2=p(1-p)$. Every binary
label is a Bernoulli variable; logistic regression (Chapter 6) models its $p$.

The **Gaussian** or **normal distribution** with mean $\mu$ and variance $\sigma^2$, written $\mathcal N(\mu,\sigma^2)$,
has density

$$
p(x)=\frac1{\sqrt{2\pi\sigma^2}}\exp\left(-\frac{(x-\mu)^2}{2\sigma^2}\right).
$$

It is the bell curve. The exponent is minus half the squared z-score, so the density falls off very fast away from the
mean: about 68.3% of the probability lies within one standard deviation, 95.4% within two, and 99.7% within three. The
program's million simulated values agree to three decimals.

<figure class="mars-fig" markdown="0">
<svg viewBox="0 0 640 260" role="img" aria-label="The bell-shaped Gaussian density. The region within one standard deviation of the mean is shaded green and labelled 68.3 percent; the region within two standard deviations is shaded blue and labelled 95.4 percent. Tick marks at the mean and at one, two and three standard deviations either side.">
  <path d="M 160.0 220.0 L 160.0 195.7 L 164.1 193.1 L 168.1 190.4 L 172.2 187.5 L 176.2 184.3 L 180.3 181.0 L 184.3 177.4 L 188.4 173.6 L 192.4 169.7 L 196.5 165.5 L 200.5 161.2 L 204.6 156.6 L 208.6 151.9 L 212.7 147.0 L 216.7 142.0 L 220.8 136.8 L 224.8 131.6 L 228.9 126.2 L 232.9 120.7 L 237.0 115.2 L 241.0 109.7 L 245.1 104.2 L 249.1 98.8 L 253.2 93.4 L 257.2 88.1 L 261.3 82.9 L 265.3 77.9 L 269.4 73.1 L 273.4 68.5 L 277.5 64.1 L 281.5 60.1 L 285.6 56.4 L 289.6 53.0 L 293.7 49.9 L 297.7 47.3 L 301.8 45.1 L 305.8 43.3 L 309.9 41.9 L 313.9 41.0 L 318.0 40.5 L 322.0 40.5 L 326.1 41.0 L 330.1 41.9 L 334.2 43.3 L 338.2 45.1 L 342.3 47.3 L 346.3 49.9 L 350.4 53.0 L 354.4 56.4 L 358.5 60.1 L 362.5 64.1 L 366.6 68.5 L 370.6 73.1 L 374.7 77.9 L 378.7 82.9 L 382.8 88.1 L 386.8 93.4 L 390.9 98.8 L 394.9 104.2 L 399.0 109.7 L 403.0 115.2 L 407.1 120.7 L 411.1 126.2 L 415.2 131.6 L 419.2 136.8 L 423.3 142.0 L 427.3 147.0 L 431.4 151.9 L 435.4 156.6 L 439.5 161.2 L 443.5 165.5 L 447.6 169.7 L 451.6 173.6 L 455.7 177.4 L 459.7 181.0 L 463.8 184.3 L 467.8 187.5 L 471.9 190.4 L 475.9 193.1 L 480.0 195.7 L 480.0 220.0 Z" fill="#9cc9ea" fill-opacity="0.35" stroke="none"/>
  <path d="M 240.0 220.0 L 240.0 111.1 L 242.0 108.4 L 244.1 105.6 L 246.1 102.9 L 248.1 100.1 L 250.1 97.4 L 252.2 94.7 L 254.2 92.0 L 256.2 89.4 L 258.2 86.8 L 260.3 84.2 L 262.3 81.6 L 264.3 79.1 L 266.3 76.7 L 268.4 74.2 L 270.4 71.9 L 272.4 69.6 L 274.4 67.4 L 276.5 65.2 L 278.5 63.1 L 280.5 61.1 L 282.5 59.1 L 284.6 57.3 L 286.6 55.5 L 288.6 53.8 L 290.6 52.2 L 292.7 50.7 L 294.7 49.2 L 296.7 47.9 L 298.7 46.7 L 300.8 45.6 L 302.8 44.6 L 304.8 43.7 L 306.8 42.9 L 308.9 42.2 L 310.9 41.6 L 312.9 41.2 L 314.9 40.8 L 317.0 40.6 L 319.0 40.5 L 321.0 40.5 L 323.0 40.6 L 325.1 40.8 L 327.1 41.2 L 329.1 41.6 L 331.1 42.2 L 333.2 42.9 L 335.2 43.7 L 337.2 44.6 L 339.2 45.6 L 341.3 46.7 L 343.3 47.9 L 345.3 49.2 L 347.3 50.7 L 349.4 52.2 L 351.4 53.8 L 353.4 55.5 L 355.4 57.3 L 357.5 59.1 L 359.5 61.1 L 361.5 63.1 L 363.5 65.2 L 365.6 67.4 L 367.6 69.6 L 369.6 71.9 L 371.6 74.2 L 373.7 76.7 L 375.7 79.1 L 377.7 81.6 L 379.7 84.2 L 381.8 86.8 L 383.8 89.4 L 385.8 92.0 L 387.8 94.7 L 389.9 97.4 L 391.9 100.1 L 393.9 102.9 L 395.9 105.6 L 398.0 108.4 L 400.0 111.1 L 400.0 220.0 Z" fill="#7ccf9a" fill-opacity="0.55" stroke="none"/>
  <path d="M 40.0 219.6 L 44.0 219.5 L 48.1 219.4 L 52.1 219.3 L 56.1 219.2 L 60.1 219.1 L 64.2 218.9 L 68.2 218.7 L 72.2 218.5 L 76.3 218.3 L 80.3 218.0 L 84.3 217.7 L 88.3 217.3 L 92.4 216.9 L 96.4 216.4 L 100.4 215.8 L 104.5 215.2 L 108.5 214.6 L 112.5 213.8 L 116.5 212.9 L 120.6 212.0 L 124.6 210.9 L 128.6 209.7 L 132.7 208.4 L 136.7 207.0 L 140.7 205.4 L 144.7 203.7 L 148.8 201.8 L 152.8 199.8 L 156.8 197.6 L 160.9 195.2 L 164.9 192.6 L 168.9 189.8 L 172.9 186.9 L 177.0 183.7 L 181.0 180.3 L 185.0 176.7 L 189.1 173.0 L 193.1 169.0 L 197.1 164.8 L 201.2 160.5 L 205.2 155.9 L 209.2 151.2 L 213.2 146.3 L 217.3 141.3 L 221.3 136.1 L 225.3 130.9 L 229.4 125.5 L 233.4 120.1 L 237.4 114.6 L 241.4 109.2 L 245.5 103.7 L 249.5 98.3 L 253.5 92.9 L 257.6 87.6 L 261.6 82.5 L 265.6 77.5 L 269.6 72.7 L 273.7 68.2 L 277.7 63.9 L 281.7 59.9 L 285.8 56.2 L 289.8 52.8 L 293.8 49.8 L 297.8 47.2 L 301.9 45.0 L 305.9 43.2 L 309.9 41.9 L 314.0 41.0 L 318.0 40.5 L 322.0 40.5 L 326.0 41.0 L 330.1 41.9 L 334.1 43.2 L 338.1 45.0 L 342.2 47.2 L 346.2 49.8 L 350.2 52.8 L 354.2 56.2 L 358.3 59.9 L 362.3 63.9 L 366.3 68.2 L 370.4 72.7 L 374.4 77.5 L 378.4 82.5 L 382.4 87.6 L 386.5 92.9 L 390.5 98.3 L 394.5 103.7 L 398.6 109.2 L 402.6 114.6 L 406.6 120.1 L 410.6 125.5 L 414.7 130.9 L 418.7 136.1 L 422.7 141.3 L 426.8 146.3 L 430.8 151.2 L 434.8 155.9 L 438.8 160.5 L 442.9 164.8 L 446.9 169.0 L 450.9 173.0 L 455.0 176.7 L 459.0 180.3 L 463.0 183.7 L 467.1 186.9 L 471.1 189.8 L 475.1 192.6 L 479.1 195.2 L 483.2 197.6 L 487.2 199.8 L 491.2 201.8 L 495.3 203.7 L 499.3 205.4 L 503.3 207.0 L 507.3 208.4 L 511.4 209.7 L 515.4 210.9 L 519.4 212.0 L 523.5 212.9 L 527.5 213.8 L 531.5 214.6 L 535.5 215.2 L 539.6 215.8 L 543.6 216.4 L 547.6 216.9 L 551.7 217.3 L 555.7 217.7 L 559.7 218.0 L 563.7 218.3 L 567.8 218.5 L 571.8 218.7 L 575.8 218.9 L 579.9 219.1 L 583.9 219.2 L 587.9 219.3 L 591.9 219.4 L 596.0 219.5 L 600.0 219.6" fill="none" stroke="currentColor" stroke-width="2"/>
  <line x1="32" y1="220" x2="608" y2="220" stroke="currentColor"/>
  <line x1="80" y1="220" x2="80" y2="226" stroke="currentColor"/>
  <text x="80" y="242" font-size="12" text-anchor="middle" fill="currentColor">μ−3σ</text>
  <line x1="160" y1="220" x2="160" y2="226" stroke="currentColor"/>
  <text x="160" y="242" font-size="12" text-anchor="middle" fill="currentColor">μ−2σ</text>
  <line x1="240" y1="220" x2="240" y2="226" stroke="currentColor"/>
  <text x="240" y="242" font-size="12" text-anchor="middle" fill="currentColor">μ−σ</text>
  <line x1="320" y1="220" x2="320" y2="226" stroke="currentColor"/>
  <text x="320" y="242" font-size="12" text-anchor="middle" fill="currentColor">μ</text>
  <line x1="400" y1="220" x2="400" y2="226" stroke="currentColor"/>
  <text x="400" y="242" font-size="12" text-anchor="middle" fill="currentColor">μ+σ</text>
  <line x1="480" y1="220" x2="480" y2="226" stroke="currentColor"/>
  <text x="480" y="242" font-size="12" text-anchor="middle" fill="currentColor">μ+2σ</text>
  <line x1="560" y1="220" x2="560" y2="226" stroke="currentColor"/>
  <text x="560" y="242" font-size="12" text-anchor="middle" fill="currentColor">μ+3σ</text>
  <text x="320" y="160" font-size="14" text-anchor="middle" fill="currentColor">68.3%</text>
  <text x="320" y="178" font-size="11" text-anchor="middle" fill="currentColor">within 1σ</text>
  <rect x="30" y="40" width="14" height="14" fill="#7ccf9a" fill-opacity="0.55" stroke="currentColor"/>
  <text x="50" y="52" font-size="12" fill="currentColor">68.3% within 1σ</text>
  <rect x="30" y="62" width="14" height="14" fill="#9cc9ea" fill-opacity="0.35" stroke="currentColor"/>
  <text x="50" y="74" font-size="12" fill="currentColor">95.4% within 2σ</text>
  <text x="30" y="96" font-size="12" fill="currentColor">99.7% within 3σ</text>
</svg>
<figcaption>The Gaussian density. Its two numbers, the mean and the standard deviation, fix its centre and its
width.</figcaption>
</figure>

Why is the Gaussian everywhere? Partly because it is mathematically convenient (its log is a quadratic, which is why
squared errors appear in Chapter 4). But mainly because of the **central limit theorem**: a sum of many small
independent effects, whatever their individual distributions (as long as their variances are finite), is
approximately Gaussian. Measurement errors that come from many small causes are therefore often roughly Gaussian.
The proof is longer than this chapter allows; the
[probability book](https://math.akadian.ca/books/probability/) and any probability text give it.

### Conditional probability and Bayes' rule

The **conditional probability** of $A$ given $B$ is the probability of $A$ when we already know that $B$ happened:

$$
P(A\mid B)=\frac{P(A\text{ and }B)}{P(B)}.
$$

Writing $P(A\text{ and }B)$ in two ways, as $P(A\mid B)P(B)$ and as $P(B\mid A)P(A)$, and dividing gives **Bayes'
rule**:

$$
P(A\mid B)=\frac{P(B\mid A)\,P(A)}{P(B)},\qquad P(B)=P(B\mid A)P(A)+P(B\mid\text{not }A)P(\text{not }A).
$$

It turns "how likely is the evidence if the hypothesis is true" into "how likely is the hypothesis given the
evidence". The second formula, the **law of total probability**, computes the denominator by splitting into the cases
"$A$" and "not $A$".

**Worked example.** A condition affects 1 person in 100. A test detects it 95% of the time when it is present (its
**sensitivity**) and gives a false alarm 5% of the time when it is absent. You test positive. How likely are you to have
the condition? Most people guess about 95%. Bayes' rule says:

| quantity | value |
|---|---|
| prior $P(\text{condition})$ | 0.01 |
| $P(\text{positive}\mid\text{condition})$ | 0.95 |
| $P(\text{positive}\mid\text{no condition})$ | 0.05 |
| $P(\text{positive})=0.95\times0.01+0.05\times0.99$ | 0.0590 |
| $P(\text{condition}\mid\text{positive})=0.0095/0.0590$ | 0.1610 |

Only about 16%. Think of 10 000 people: 100 have the condition and 95 of them test positive; 9900 do not, and 495 of
them test positive anyway. Of the 590 positives, only 95 are real. The condition is rare, so false alarms from the
large healthy group outnumber the true positives. The program's simulation of a million people agrees (0.1634, the
difference being chance). A second, independent positive test uses 0.161 as the new prior and raises the probability
to 0.7848. Bayes' rule is how evidence should update beliefs, and Chapter 12 builds whole classifiers on it.

```python
--8<-- "books/machine-learning/ch03_probability.py"
```

Output:

```
die: E = 3.5, Var = 2.9167; simulated mean 3.5071, var 2.9235
Bernoulli(0.3): E = 0.3, Var = 0.21; simulated 0.3004, 0.2101
Gaussian within 1, 2, 3 sd: exact [0.6827, 0.9545, 0.9973]  simulated [0.6831, 0.9545, 0.9973]

P(positive) = 0.0590;  P(condition | positive) = 0.1610
simulated 1000000 people: 58953 positive, of whom 0.1634 have the condition
after a second, independent positive test: 0.7848

likelihood of p for 7 heads in 10 tosses
  p = 0.3: L = 0.000075   log L = -9.4978
  p = 0.5: L = 0.000977   log L = -6.9315
  p = 0.6: L = 0.001792   log L = -6.3247
  p = 0.7: L = 0.002224   log L = -6.1086
  p = 0.8: L = 0.001678   log L = -6.3903
  p = 0.9: L = 0.000478   log L = -7.6453
  maximum on a grid at p = 0.7

n = 5, true variance 4.0: average MLE variance 3.200 (theory 3.200), average with n-1: 4.000
```

## 3.5 Likelihood and maximum likelihood

Probability goes from a model to data: if the coin is fair, how likely are 7 heads in 10 tosses? Learning goes the
other way: we have seen 7 heads in 10 tosses; what is the coin's bias? The bridge between the two is the likelihood.

Suppose a model with parameter $\theta$ gives each possible dataset a probability (or density) $P(\text{data}\mid\theta)$.
Once the data is fixed, read this as a function of $\theta$; it is called the **likelihood**:

$$
L(\theta)=P(\text{data}\mid\theta).
$$

The likelihood is not a probability distribution over $\theta$ (it need not add up to 1 over $\theta$). It scores each
parameter value by how well it explains the data we actually saw. The **maximum likelihood estimate** (MLE) is the
$\theta$ with the highest likelihood. R. A. Fisher developed the method in the early twentieth century, and most loss
functions in this book are negative log-likelihoods in disguise.

### A coin

A coin with unknown probability $p$ of heads is tossed 10 times, independently, giving 7 heads and 3 tails in some
particular order. Independent probabilities multiply, so

$$
L(p)=p^7(1-p)^3 .
$$

The program evaluates it: $L(0.5)=0.000977$, $L(0.7)=0.002224$, $L(0.9)=0.000478$. The value 0.7 explains the data best
among those tried, and a fine grid confirms the maximum at 0.7.

Products of many probabilities become tiny numbers that a computer rounds to zero, and they are awkward to
differentiate. So we almost always maximise the **log-likelihood** instead. The logarithm is increasing, so it has
its maximum at the same place, and it turns products into sums:

$$
\ell(p)=\ln L(p)=7\ln p+3\ln(1-p).
$$

**The MLE of a coin is the fraction of heads.** With $k$ heads in $n$ tosses,
$\ell(p)=k\ln p+(n-k)\ln(1-p)$. Its derivative is $k/p-(n-k)/(1-p)$. Setting it to zero: $k(1-p)=(n-k)p$, so $k=np$
and $\hat p=k/n$. It is a maximum, not a minimum, because the second derivative $-k/p^2-(n-k)/(1-p)^2$ is negative.
$\square$ So maximum likelihood gives the answer common sense suggests, $7/10$, and the derivation shows *why* it is
the best in a precise sense.

### A Gaussian

Now $n$ independent measurements $x_1,\dots,x_n$ from $\mathcal N(\mu,\sigma^2)$. The log-likelihood is the sum of the
logs of the densities:

$$
\ell(\mu,\sigma^2)=-\frac n2\ln(2\pi\sigma^2)-\frac1{2\sigma^2}\sum_{i=1}^n(x_i-\mu)^2 .
$$

**The mean.** Only the second term depends on $\mu$, and it is *minus* a sum of squared differences. So maximising the
likelihood over $\mu$ is exactly minimising $\sum_i(x_i-\mu)^2$, the squared error. Setting the derivative
$\frac1{\sigma^2}\sum_i(x_i-\mu)$ to zero gives $\hat\mu=\frac1n\sum_ix_i=\bar x$, the sample mean. This link between
Gaussian noise and squared error is the heart of section 4.5.

**The variance.** Differentiate with respect to $v=\sigma^2$: $-\frac n{2v}+\frac1{2v^2}\sum_i(x_i-\bar x)^2=0$, so
$\hat\sigma^2=\frac1n\sum_i(x_i-\bar x)^2$.

**Why statisticians often divide by n - 1.** The MLE of the variance is slightly too small on average.

**Claim.** $\mathbb E[\hat\sigma^2]=\frac{n-1}n\sigma^2$.

**Proof.** Write $\sum_i(x_i-\bar x)^2=\sum_i(x_i-\mu)^2-n(\bar x-\mu)^2$ (expand $x_i-\bar x=(x_i-\mu)-(\bar x-\mu)$ and use
$\sum_i(x_i-\mu)=n(\bar x-\mu)$). Each $(x_i-\mu)^2$ has expectation $\sigma^2$, and $(\bar x-\mu)^2$ has expectation
$\operatorname{Var}(\bar x)=\sigma^2/n$. So the expectation of the sum is $n\sigma^2-\sigma^2=(n-1)\sigma^2$, and dividing
by $n$ gives the claim. $\square$

The reason is that $\bar x$ is fitted to the same data, so the data is always a little closer to $\bar x$ than to the
true $\mu$. Dividing by $n-1$ instead (**Bessel's correction**) gives an estimate that is right on average. The
program's simulation with $n=5$ and $\sigma^2=4$ finds the average MLE to be 3.200, exactly $\tfrac45\cdot4$, and the
corrected version 4.000. For large $n$ the difference is negligible. The same effect, "a model fitted to data looks
better on that data than it is", is the training-versus-test gap of Chapter 1 in its simplest form.

## 3.6 Eigenvectors and the SVD in one picture

*Level: intermediate.*

A matrix stretches and turns space. Are there directions it only stretches, without turning? And can every matrix be
described by simple stretches and turns? The answers, eigenvectors and the singular value decomposition, describe the
shape of data, explain the condition number of Chapter 2, and are the basis of PCA in Chapter 14.

### Eigenvectors

A nonzero vector $v$ is an **eigenvector** of a square matrix $A$ if $A$ maps it to a multiple of itself:

$$
Av=\lambda v .
$$

The number $\lambda$ is the **eigenvalue**: the factor by which $A$ stretches $v$ (negative $\lambda$ flips it). For
$A=\begin{pmatrix}2&1\\1&2\end{pmatrix}$, try $v=(1,1)$: $Av=(3,3)=3v$, so $\lambda=3$. Try $v=(1,-1)$: $Av=(1,-1)$, so
$\lambda=1$. Along the diagonal $(1,1)$ the map stretches by 3; across it, it leaves vectors alone.

For **symmetric** matrices ($A^\top=A$), which include every $X^\top X$ and every covariance matrix, the picture is
always this clean.

**Theorem (spectral theorem).** A real symmetric $m\times m$ matrix has $m$ real eigenvalues
$\lambda_1\ge\dots\ge\lambda_m$ and a set of eigenvectors $q_1,\dots,q_m$ that are of length 1 and mutually orthogonal.
Writing $Q$ for the matrix with columns $q_j$ and $\Lambda$ for the diagonal matrix of eigenvalues,
$A=Q\Lambda Q^\top$.

The proof takes a page of linear algebra (the [linear algebra book](https://math.akadian.ca/books/linear-algebra/) and
Strang's textbook give it). The meaning: in the coordinate system given by its eigenvectors, a symmetric matrix is
just a stretch along each axis. $Q^\top$ rotates into those coordinates, $\Lambda$ stretches, and $Q$ rotates back. This
is what Chapter 2 needed: a tilted quadratic bowl $\tfrac12w^\top Aw$ becomes the axis-aligned bowl
$\tfrac12\sum_j\lambda_jz_j^2$ in eigen-coordinates $z=Q^\top w$, and gradient descent's speed is governed by the
condition number $\lambda_{\max}/\lambda_{\min}$.

**The largest eigenvalue is the largest stretch.** For a unit vector $u$, write $u=\sum_jc_jq_j$ with $\sum_jc_j^2=1$
(the $q_j$ are orthonormal). Then $u^\top Au=\sum_j\lambda_jc_j^2\le\lambda_1\sum_jc_j^2=\lambda_1$, with equality at
$u=q_1$. So $\max_{\lVert u\rVert=1}u^\top Au=\lambda_1$. $\square$ When $A$ is the **covariance matrix** of centred data,
$u^\top Au$ is the variance of the data along direction $u$, so the top eigenvector is the direction in which the data
varies most. The program builds a cloud of 2000 points stretched along a line at $30^\circ$; the top eigenvector of its
covariance points at $29.9^\circ$. That is PCA, which Chapter 14 develops fully.

### Power iteration

How do you find the top eigenvector without a library? Multiply any starting vector by $A$ again and again, scaling
it back to length 1 each time. This is **power iteration**. *Why it works:* write the start as
$v_0=\sum_jc_jq_j$. Then $A^tv_0=\sum_jc_j\lambda_j^tq_j=\lambda_1^t\bigl(c_1q_1+\sum_{j>1}c_j(\lambda_j/\lambda_1)^tq_j\bigr)$.
If $|\lambda_1|>|\lambda_2|$ and $c_1\ne0$, every ratio $(\lambda_j/\lambda_1)^t$ shrinks to zero, so the direction
approaches $q_1$, with error shrinking like $|\lambda_2/\lambda_1|^t$. For our matrix the ratio is $1/3$. The program's
trace from $(1,0)$:

| step | $v$ | estimate $v^\top Av$ |
|---|---|---|
| 1 | (0.8944, 0.4472) | 2.800000 |
| 2 | (0.7809, 0.6247) | 2.975610 |
| 3 | (0.7328, 0.6805) | 2.997260 |
| 4 | (0.7158, 0.6983) | 2.999695 |
| 8 | (0.7072, 0.7070) | 3.000000 |

By hand, step 1: $A(1,0)=(2,1)$, of length $\sqrt5$, so $v=(2,1)/\sqrt5=(0.8944,0.4472)$. Then
$Av=(2\cdot0.8944+0.4472,\;0.8944+2\cdot0.4472)=(2.2361,1.7889)$ and $v\cdot Av=2.0+0.8=2.8$. The vector heads to
$(0.7071,0.7071)$, the unit vector along $(1,1)$, and the estimate to 3; each step cuts the remaining error by about
the factor $1/3$. The PageRank method for ranking web pages (Page, Brin and colleagues, 1998) computes its scores by a
power iteration on a matrix with one row per page.

### The singular value decomposition

Eigenvectors need a square matrix, and a non-symmetric one may have none that are real. The **singular value
decomposition** (SVD) works for *every* matrix, including the rectangular data table $X$.

**Theorem (SVD).** Every real $n\times m$ matrix $M$ can be written $M=U\Sigma V^\top$, where $U$ ($n\times n$) and $V$
($m\times m$) have orthonormal columns (they are rotations, possibly with a reflection), and $\Sigma$ is $n\times m$ with
non-negative numbers $\sigma_1\ge\sigma_2\ge\dots\ge0$ on its diagonal and zeros elsewhere. The $\sigma_j$ are the
**singular values**.

Read it right to left as a map: $V^\top$ rotates, $\Sigma$ stretches along the axes (by $\sigma_1$, $\sigma_2$, ...), and
$U$ rotates again. So every linear map is a rotation, a stretch and a rotation, and it turns the unit circle into an
ellipse whose semi-axes are the singular values.

<figure class="mars-fig" markdown="0">
<svg viewBox="0 0 640 230" role="img" aria-label="Four panels showing M equals U Sigma V transpose acting on the unit circle, for M equals 3, 0; 4, 5. Panel 1: the unit circle with the two right singular vectors v1 (orange) and v2 (green). Panel 2: after V transpose, still a circle, with v1 and v2 rotated onto the axes. Panel 3: after Sigma, an ellipse stretched along the axes by 6.71 and 2.24. Panel 4: after U, the same ellipse rotated; this is M applied to the circle.">
  <line x1="0" y1="120" x2="140" y2="120" stroke="currentColor" stroke-opacity="0.25"/>
  <line x1="70" y1="45" x2="70" y2="195" stroke="currentColor" stroke-opacity="0.25"/>
  <path d="M 100.0 120.0 L 99.9 118.1 L 99.8 116.2 L 99.5 114.3 L 99.0 112.5 L 98.5 110.6 L 97.9 108.9 L 97.1 107.1 L 96.2 105.4 L 95.2 103.8 L 94.2 102.2 L 93.0 100.7 L 91.7 99.3 L 90.4 98.0 L 88.9 96.7 L 87.4 95.6 L 85.8 94.5 L 84.2 93.6 L 82.5 92.7 L 80.7 92.0 L 78.9 91.4 L 77.1 90.8 L 75.2 90.5 L 73.3 90.2 L 71.4 90.0 L 69.5 90.0 L 67.6 90.1 L 65.7 90.3 L 63.9 90.6 L 62.0 91.1 L 60.2 91.6 L 58.4 92.3 L 56.7 93.1 L 55.0 94.0 L 53.4 95.0 L 51.8 96.1 L 50.4 97.3 L 49.0 98.6 L 47.6 100.0 L 46.4 101.5 L 45.3 103.0 L 44.3 104.6 L 43.3 106.3 L 42.5 108.0 L 41.8 109.7 L 41.2 111.5 L 40.7 113.4 L 40.4 115.3 L 40.1 117.1 L 40.0 119.0 L 40.0 121.0 L 40.1 122.9 L 40.4 124.7 L 40.7 126.6 L 41.2 128.5 L 41.8 130.3 L 42.5 132.0 L 43.3 133.7 L 44.3 135.4 L 45.3 137.0 L 46.4 138.5 L 47.6 140.0 L 49.0 141.4 L 50.4 142.7 L 51.8 143.9 L 53.4 145.0 L 55.0 146.0 L 56.7 146.9 L 58.4 147.7 L 60.2 148.4 L 62.0 148.9 L 63.9 149.4 L 65.7 149.7 L 67.6 149.9 L 69.5 150.0 L 71.4 150.0 L 73.3 149.8 L 75.2 149.5 L 77.1 149.2 L 78.9 148.6 L 80.7 148.0 L 82.5 147.3 L 84.2 146.4 L 85.8 145.5 L 87.4 144.4 L 88.9 143.3 L 90.4 142.0 L 91.7 140.7 L 93.0 139.3 L 94.2 137.8 L 95.2 136.2 L 96.2 134.6 L 97.1 132.9 L 97.9 131.1 L 98.5 129.4 L 99.0 127.5 L 99.5 125.7 L 99.8 123.8 L 99.9 121.9 L 100.0 120.0 Z" fill="#9cc9ea" fill-opacity="0.3" stroke="currentColor" stroke-width="1.5"/>
  <line x1="70" y1="120" x2="48.8" y2="141.2" stroke="#eea66f" stroke-width="3"/>
  <line x1="70" y1="120" x2="48.8" y2="98.8" stroke="#7ccf9a" stroke-width="3"/>
  <line x1="160" y1="120" x2="300" y2="120" stroke="currentColor" stroke-opacity="0.25"/>
  <line x1="230" y1="45" x2="230" y2="195" stroke="currentColor" stroke-opacity="0.25"/>
  <path d="M 208.8 141.2 L 207.5 139.8 L 206.3 138.4 L 205.2 136.8 L 204.1 135.2 L 203.2 133.5 L 202.4 131.8 L 201.7 130.0 L 201.1 128.2 L 200.7 126.4 L 200.3 124.5 L 200.1 122.6 L 200.0 120.7 L 200.0 118.8 L 200.2 116.9 L 200.4 115.0 L 200.8 113.2 L 201.3 111.3 L 201.9 109.5 L 202.6 107.8 L 203.4 106.0 L 204.4 104.4 L 205.4 102.8 L 206.6 101.3 L 207.8 99.8 L 209.1 98.5 L 210.5 97.2 L 212.0 96.0 L 213.6 94.9 L 215.2 93.9 L 216.9 93.0 L 218.6 92.2 L 220.4 91.6 L 222.2 91.0 L 224.1 90.6 L 226.0 90.3 L 227.9 90.1 L 229.8 90.0 L 231.7 90.0 L 233.6 90.2 L 235.4 90.5 L 237.3 90.9 L 239.1 91.4 L 240.9 92.1 L 242.7 92.8 L 244.4 93.7 L 246.0 94.6 L 247.6 95.7 L 249.1 96.9 L 250.5 98.1 L 251.9 99.5 L 253.1 100.9 L 254.3 102.4 L 255.4 104.0 L 256.3 105.6 L 257.2 107.3 L 257.9 109.1 L 258.6 110.9 L 259.1 112.7 L 259.5 114.6 L 259.8 116.4 L 260.0 118.3 L 260.0 120.2 L 259.9 122.1 L 259.7 124.0 L 259.4 125.9 L 259.0 127.8 L 258.4 129.6 L 257.8 131.4 L 257.0 133.1 L 256.1 134.8 L 255.1 136.4 L 254.0 138.0 L 252.8 139.5 L 251.5 140.9 L 250.2 142.2 L 248.7 143.4 L 247.2 144.6 L 245.6 145.6 L 244.0 146.6 L 242.2 147.4 L 240.5 148.1 L 238.7 148.7 L 236.8 149.2 L 235.0 149.6 L 233.1 149.8 L 231.2 150.0 L 229.3 150.0 L 227.4 149.9 L 225.5 149.7 L 223.6 149.3 L 221.8 148.9 L 220.0 148.3 L 218.2 147.6 L 216.5 146.8 L 214.8 145.9 L 213.2 144.8 L 211.6 143.7 L 210.2 142.5 L 208.8 141.2 Z" fill="#9cc9ea" fill-opacity="0.3" stroke="currentColor" stroke-width="1.5"/>
  <line x1="230" y1="120" x2="260.0" y2="120.0" stroke="#eea66f" stroke-width="3"/>
  <line x1="230" y1="120" x2="230.0" y2="90.0" stroke="#7ccf9a" stroke-width="3"/>
  <line x1="320" y1="120" x2="460" y2="120" stroke="currentColor" stroke-opacity="0.25"/>
  <line x1="390" y1="45" x2="390" y2="195" stroke="currentColor" stroke-opacity="0.25"/>
  <path d="M 344.9 135.0 L 342.2 134.0 L 339.6 133.0 L 337.2 131.9 L 335.1 130.8 L 333.1 129.6 L 331.4 128.4 L 329.9 127.1 L 328.7 125.8 L 327.7 124.5 L 327.0 123.2 L 326.5 121.9 L 326.3 120.5 L 326.3 119.2 L 326.6 117.8 L 327.2 116.5 L 328.0 115.2 L 329.0 113.9 L 330.3 112.6 L 331.8 111.3 L 333.6 110.1 L 335.6 108.9 L 337.8 107.8 L 340.2 106.7 L 342.8 105.7 L 345.7 104.7 L 348.7 103.8 L 351.8 103.0 L 355.1 102.2 L 358.6 101.5 L 362.2 100.9 L 365.8 100.3 L 369.6 99.9 L 373.5 99.5 L 377.4 99.2 L 381.4 99.0 L 385.5 98.8 L 389.5 98.8 L 393.5 98.8 L 397.6 98.9 L 401.6 99.1 L 405.5 99.4 L 409.4 99.8 L 413.2 100.2 L 416.9 100.7 L 420.5 101.4 L 424.0 102.0 L 427.4 102.8 L 430.6 103.6 L 433.6 104.5 L 436.5 105.5 L 439.1 106.5 L 441.6 107.5 L 443.9 108.7 L 445.9 109.8 L 447.8 111.0 L 449.3 112.3 L 450.7 113.5 L 451.8 114.8 L 452.7 116.1 L 453.3 117.5 L 453.6 118.8 L 453.7 120.2 L 453.6 121.5 L 453.1 122.9 L 452.5 124.2 L 451.6 125.5 L 450.4 126.8 L 449.0 128.1 L 447.3 129.3 L 445.4 130.5 L 443.3 131.6 L 441.0 132.7 L 438.5 133.8 L 435.8 134.8 L 432.9 135.7 L 429.8 136.6 L 426.6 137.4 L 423.2 138.1 L 419.7 138.8 L 416.0 139.4 L 412.3 139.9 L 408.4 140.3 L 404.5 140.7 L 400.6 140.9 L 396.6 141.1 L 392.5 141.2 L 388.5 141.2 L 384.4 141.2 L 380.4 141.0 L 376.5 140.8 L 372.5 140.4 L 368.7 140.0 L 364.9 139.5 L 361.2 139.0 L 357.7 138.3 L 354.3 137.6 L 351.0 136.8 L 347.9 135.9 L 344.9 135.0 Z" fill="#9cc9ea" fill-opacity="0.3" stroke="currentColor" stroke-width="1.5"/>
  <line x1="390" y1="120" x2="453.7" y2="120.0" stroke="#eea66f" stroke-width="3"/>
  <line x1="390" y1="120" x2="390.0" y2="98.8" stroke="#7ccf9a" stroke-width="3"/>
  <line x1="480" y1="120" x2="620" y2="120" stroke="currentColor" stroke-opacity="0.25"/>
  <line x1="550" y1="45" x2="550" y2="195" stroke="currentColor" stroke-opacity="0.25"/>
  <path d="M 578.5 82.0 L 578.4 79.1 L 578.3 76.3 L 578.0 73.7 L 577.6 71.3 L 577.1 69.1 L 576.5 67.1 L 575.7 65.3 L 574.9 63.7 L 574.0 62.4 L 573.0 61.2 L 571.8 60.4 L 570.6 59.7 L 569.3 59.3 L 568.0 59.2 L 566.5 59.3 L 565.0 59.6 L 563.5 60.2 L 561.8 61.0 L 560.2 62.1 L 558.5 63.4 L 556.7 64.9 L 554.9 66.6 L 553.2 68.6 L 551.4 70.7 L 549.5 73.1 L 547.7 75.7 L 545.9 78.4 L 544.2 81.3 L 542.4 84.3 L 540.7 87.5 L 539.0 90.9 L 537.3 94.3 L 535.8 97.9 L 534.2 101.5 L 532.7 105.2 L 531.3 109.0 L 530.0 112.8 L 528.8 116.6 L 527.6 120.5 L 526.5 124.4 L 525.5 128.2 L 524.7 132.0 L 523.9 135.8 L 523.2 139.5 L 522.7 143.1 L 522.2 146.6 L 521.9 150.0 L 521.6 153.3 L 521.5 156.5 L 521.5 159.5 L 521.6 162.3 L 521.9 165.0 L 522.2 167.5 L 522.7 169.8 L 523.2 172.0 L 523.9 173.9 L 524.7 175.5 L 525.5 177.0 L 526.5 178.2 L 527.6 179.2 L 528.8 180.0 L 530.0 180.5 L 531.3 180.8 L 532.7 180.8 L 534.2 180.6 L 535.8 180.1 L 537.3 179.4 L 539.0 178.5 L 540.7 177.3 L 542.4 175.9 L 544.2 174.3 L 545.9 172.4 L 547.7 170.4 L 549.5 168.1 L 551.4 165.6 L 553.2 163.0 L 554.9 160.2 L 556.7 157.2 L 558.5 154.1 L 560.2 150.8 L 561.8 147.4 L 563.5 143.9 L 565.0 140.3 L 566.5 136.7 L 568.0 132.9 L 569.3 129.1 L 570.6 125.3 L 571.8 121.4 L 573.0 117.6 L 574.0 113.7 L 574.9 109.9 L 575.7 106.1 L 576.5 102.4 L 577.1 98.7 L 577.6 95.1 L 578.0 91.7 L 578.3 88.3 L 578.4 85.1 L 578.5 82.0 Z" fill="#9cc9ea" fill-opacity="0.3" stroke="currentColor" stroke-width="1.5"/>
  <line x1="550" y1="120" x2="529.8" y2="180.5" stroke="#eea66f" stroke-width="3"/>
  <line x1="550" y1="120" x2="529.8" y2="113.3" stroke="#7ccf9a" stroke-width="3"/>
  <text x="70" y="212" font-size="13" text-anchor="middle" fill="currentColor">unit circle</text>
  <text x="230" y="212" font-size="13" text-anchor="middle" fill="currentColor">after Vᵀ: rotate</text>
  <text x="390" y="212" font-size="13" text-anchor="middle" fill="currentColor">after Σ: stretch</text>
  <text x="550" y="212" font-size="13" text-anchor="middle" fill="currentColor">after U: rotate = M</text>
  <text x="390" y="30" font-size="12" text-anchor="middle" fill="currentColor">σ1 = 6.71, σ2 = 2.24; scale ×0.32</text>
  <text x="70" y="30" font-size="12" text-anchor="middle" fill="currentColor">scale ×1</text>
  <text x="230" y="30" font-size="12" text-anchor="middle" fill="currentColor">scale ×1</text>
  <text x="550" y="30" font-size="12" text-anchor="middle" fill="currentColor">scale ×0.32</text>
</svg>
<figcaption>The SVD in one picture, for M = [[3, 0], [4, 5]]. The orange and green arrows are the right singular
vectors v1 and v2 and their images; v1 ends up as the long axis of the ellipse, of length 6.71, and v2 as the short
axis, of length 2.24. (Panels 3 and 4 are drawn at about a third of the scale of panels 1 and 2.)</figcaption>
</figure>

**How the SVD relates to eigenvectors.** $M^\top M=V\Sigma^\top U^\top U\Sigma V^\top=V(\Sigma^\top\Sigma)V^\top$, because
$U^\top U=I$. That is the spectral decomposition of the symmetric matrix $M^\top M$: its eigenvectors are the columns of
$V$ and its eigenvalues are $\sigma_j^2$. For $M=\begin{pmatrix}3&0\\4&5\end{pmatrix}$, $M^\top M=\begin{pmatrix}25&20\\
20&25\end{pmatrix}$, with eigenvalues $45$ and $5$, so the singular values are $\sqrt{45}\approx6.7082$ and
$\sqrt5\approx2.2361$, exactly what the program prints.

**Best low-rank approximation.** Keeping only the first $k$ singular values and vectors gives the matrix
$M_k=\sum_{j\le k}\sigma_ju_jv_j^\top$, a sum of $k$ simple "rank-one" pieces. The **Eckart-Young theorem** (Eckart and
Young, 1936) says that $M_k$ is the closest matrix of rank $k$ to $M$, with error
$\sqrt{\sigma_{k+1}^2+\sigma_{k+2}^2+\dots}$ (measured by the square root of the sum of squared entries of $M-M_k$). The
program checks it on a small table of ratings, five people by four films, with two kinds of taste. The singular values
are 13.355, 6.730, 1.795 and 0.336; the rank-2 approximation has error 1.826, exactly
$\sqrt{1.795^2+0.336^2}$. Two numbers per person and two per film capture almost everything, and that is the idea
behind the recommender systems that predict ratings from a few "taste factors".

**Condition number.** For a square invertible matrix, $\sigma_1/\sigma_m$ is its **condition number**. For a symmetric
matrix with positive eigenvalues it equals the $\lambda_{\max}/\lambda_{\min}$ of Chapter 2, and the condition number of
$X^\top X$ is the square of that of $X$. Section 4.7 explains why that squaring is the reason not to solve least squares
by inverting $X^\top X$.

```python
--8<-- "books/machine-learning/ch03_eig_svd_info.py"
```

Output:

```
power iteration on [[2,1],[1,2]] from (1, 0)
  step 1: v = (0.8944, 0.4472)  estimate 2.800000
  step 2: v = (0.7809, 0.6247)  estimate 2.975610
  step 3: v = (0.7328, 0.6805)  estimate 2.997260
  step 4: v = (0.7158, 0.6983)  estimate 2.999695
  step 5: v = (0.7100, 0.7042)  estimate 2.999966
  step 6: v = (0.7081, 0.7061)  estimate 2.999996
  step 7: v = (0.7074, 0.7068)  estimate 3.000000
  step 8: v = (0.7072, 0.7070)  estimate 3.000000
numpy eigh: eigenvalues [1. 3.]  eigenvectors (columns)
 [[-0.7071  0.7071]
 [ 0.7071  0.7071]]
covariance eigenvalues [0.261 9.361]; top direction [0.867 0.498], angle 29.9 deg (built at 30)

SVD of [[3,0],[4,5]]: singular values [6.7082 2.2361]  squares [45.  5.]  eig of M^T M [ 5. 45.]
  U S V^T rebuilds M: True
ratings singular values [13.355  6.73   1.795  0.336]
  rank 1: error 6.974, sqrt of the dropped s^2 6.974
  rank 2: error 1.826, sqrt of the dropped s^2 1.826

entropy in bits
  [0.5, 0.5]                 H = 1.0000
  [0.9, 0.1]                 H = 0.4690
  [0.99, 0.01]               H = 0.0808
  [1.0, 0.0]                 H = 0.0000
  [0.25, 0.25, 0.25, 0.25]   H = 2.0000
P = [0.5, 0.25, 0.25], Q = uniform: H(P) = 1.5000, H(P,Q) = 1.5850, KL(P||Q) = 0.0850, KL(Q||P) = 0.0817
smallest KL over 10000 random pairs of distributions: 0.001459 (never negative)
```

(The data cloud was built with standard deviations 3 and 0.5, so the true variances along its axes are 9 and 0.25;
the sample of 2000 points gives 9.361 and 0.261.)

## 3.7 Information: entropy, cross-entropy, KL divergence

*Level: intermediate.*

How should we score a prediction that is a probability? If a model says "rain, 90%" and it rains, it did well; if it
does not rain, it did badly, and worse than a model that had said 60%. The right measure comes from information
theory, founded by Claude Shannon in "A Mathematical Theory of Communication" (1948).

### Surprise and entropy

Shannon measured the **information**, or surprise, of an event of probability $p$ as $-\log_2p$ **bits**. A certain
event ($p=1$) carries 0 bits: no surprise. A fair coin flip carries $-\log_21/2=1$ bit. An event of probability $1/1024$
carries 10 bits. Rare events are surprising, and independent surprises add, because probabilities multiply and logs
turn products into sums.

The **entropy** of a distribution $P=(p_1,\dots,p_k)$ is the expected surprise:

$$
H(P)=-\sum_{i=1}^kp_i\log_2p_i ,
$$

with the convention $0\log0=0$ (the limit of $p\log p$ as $p\to0$). Entropy measures uncertainty. A fair coin has 1 bit;
a coin that lands heads 90% of the time has 0.469 bits; a certain outcome has 0; four equally likely outcomes have 2
bits. Shannon proved that $H(P)$ is the smallest possible average number of bits per symbol for any code that can be decoded unambiguously and
transmits symbols drawn from $P$; the [Huffman code](../../greedy/huffman.md) comes within one
bit of it. Using natural logarithms instead of $\log_2$ gives entropy in **nats**; machine-learning code usually does,
and the choice only changes the unit.

<figure class="mars-fig" markdown="0">
<svg viewBox="0 0 640 240" role="img" aria-label="The entropy of a coin, in bits, as a function of the probability p of heads. The curve is 0 at p equals 0, rises to its maximum of 1 bit at p equals one half, and falls back to 0 at p equals 1. The point p equals 0.9, entropy 0.469 bits, is marked.">
  <line x1="60" y1="200" x2="310" y2="200" stroke="currentColor"/>
  <line x1="60" y1="200" x2="60" y2="30" stroke="currentColor"/>
  <line x1="56" y1="40" x2="60" y2="40" stroke="currentColor"/>
  <text x="50" y="44" font-size="12" text-anchor="end" fill="currentColor">1</text>
  <text x="50" y="204" font-size="12" text-anchor="end" fill="currentColor">0</text>
  <line x1="180" y1="200" x2="180" y2="205" stroke="currentColor"/>
  <text x="180" y="220" font-size="12" text-anchor="middle" fill="currentColor">0.5</text>
  <line x1="300" y1="200" x2="300" y2="205" stroke="currentColor"/>
  <text x="300" y="220" font-size="12" text-anchor="middle" fill="currentColor">1</text>
  <text x="60" y="220" font-size="12" text-anchor="middle" fill="currentColor">0</text>
  <text x="185" y="236" font-size="12" text-anchor="middle" fill="currentColor">p (probability of heads)</text>
  <text x="22" y="120" font-size="12" text-anchor="middle" fill="currentColor" transform="rotate(-90 22 120)">H in bits</text>
  <path d="M 60.1 199.0 L 61.3 192.1 L 62.5 186.5 L 63.7 181.5 L 64.9 176.9 L 66.1 172.5 L 67.3 168.4 L 68.6 164.5 L 69.8 160.7 L 71.0 157.2 L 72.2 153.7 L 73.4 150.4 L 74.6 147.1 L 75.8 144.0 L 77.0 141.0 L 78.2 138.0 L 79.4 135.2 L 80.6 132.4 L 81.8 129.7 L 83.0 127.1 L 84.2 124.5 L 85.4 122.0 L 86.6 119.6 L 87.8 117.2 L 89.0 114.9 L 90.2 112.6 L 91.4 110.4 L 92.7 108.2 L 93.9 106.1 L 95.1 104.0 L 96.3 102.0 L 97.5 100.0 L 98.7 98.1 L 99.9 96.2 L 101.1 94.3 L 102.3 92.5 L 103.5 90.8 L 104.7 89.0 L 105.9 87.3 L 107.1 85.7 L 108.3 84.1 L 109.5 82.5 L 110.7 81.0 L 111.9 79.4 L 113.1 78.0 L 114.3 76.5 L 115.5 75.1 L 116.7 73.7 L 118.0 72.4 L 119.2 71.1 L 120.4 69.8 L 121.6 68.6 L 122.8 67.3 L 124.0 66.2 L 125.2 65.0 L 126.4 63.9 L 127.6 62.8 L 128.8 61.7 L 130.0 60.7 L 131.2 59.6 L 132.4 58.7 L 133.6 57.7 L 134.8 56.8 L 136.0 55.9 L 137.2 55.0 L 138.4 54.1 L 139.6 53.3 L 140.8 52.5 L 142.0 51.7 L 143.3 51.0 L 144.5 50.3 L 145.7 49.6 L 146.9 48.9 L 148.1 48.3 L 149.3 47.7 L 150.5 47.1 L 151.7 46.5 L 152.9 45.9 L 154.1 45.4 L 155.3 44.9 L 156.5 44.5 L 157.7 44.0 L 158.9 43.6 L 160.1 43.2 L 161.3 42.8 L 162.5 42.5 L 163.7 42.1 L 164.9 41.8 L 166.1 41.5 L 167.3 41.3 L 168.6 41.1 L 169.8 40.8 L 171.0 40.7 L 172.2 40.5 L 173.4 40.4 L 174.6 40.2 L 175.8 40.1 L 177.0 40.1 L 178.2 40.0 L 179.4 40.0 L 180.6 40.0 L 181.8 40.0 L 183.0 40.1 L 184.2 40.1 L 185.4 40.2 L 186.6 40.4 L 187.8 40.5 L 189.0 40.7 L 190.2 40.8 L 191.4 41.1 L 192.7 41.3 L 193.9 41.5 L 195.1 41.8 L 196.3 42.1 L 197.5 42.5 L 198.7 42.8 L 199.9 43.2 L 201.1 43.6 L 202.3 44.0 L 203.5 44.5 L 204.7 44.9 L 205.9 45.4 L 207.1 45.9 L 208.3 46.5 L 209.5 47.1 L 210.7 47.7 L 211.9 48.3 L 213.1 48.9 L 214.3 49.6 L 215.5 50.3 L 216.7 51.0 L 218.0 51.7 L 219.2 52.5 L 220.4 53.3 L 221.6 54.1 L 222.8 55.0 L 224.0 55.9 L 225.2 56.8 L 226.4 57.7 L 227.6 58.7 L 228.8 59.6 L 230.0 60.7 L 231.2 61.7 L 232.4 62.8 L 233.6 63.9 L 234.8 65.0 L 236.0 66.2 L 237.2 67.3 L 238.4 68.6 L 239.6 69.8 L 240.8 71.1 L 242.0 72.4 L 243.3 73.7 L 244.5 75.1 L 245.7 76.5 L 246.9 78.0 L 248.1 79.4 L 249.3 81.0 L 250.5 82.5 L 251.7 84.1 L 252.9 85.7 L 254.1 87.3 L 255.3 89.0 L 256.5 90.8 L 257.7 92.5 L 258.9 94.3 L 260.1 96.2 L 261.3 98.1 L 262.5 100.0 L 263.7 102.0 L 264.9 104.0 L 266.1 106.1 L 267.3 108.2 L 268.6 110.4 L 269.8 112.6 L 271.0 114.9 L 272.2 117.2 L 273.4 119.6 L 274.6 122.0 L 275.8 124.5 L 277.0 127.1 L 278.2 129.7 L 279.4 132.4 L 280.6 135.2 L 281.8 138.0 L 283.0 141.0 L 284.2 144.0 L 285.4 147.1 L 286.6 150.4 L 287.8 153.7 L 289.0 157.2 L 290.2 160.7 L 291.4 164.5 L 292.7 168.4 L 293.9 172.5 L 295.1 176.9 L 296.3 181.5 L 297.5 186.5 L 298.7 192.1 L 299.9 199.0" fill="none" stroke="#eea66f" stroke-width="2.5"/>
  <line x1="180" y1="200" x2="180" y2="40" stroke="currentColor" stroke-dasharray="3 3" stroke-opacity="0.5"/>
  <circle cx="276" cy="125" r="4.5" fill="#9cc9ea" stroke="currentColor"/>
  <text x="270" y="112" font-size="12" text-anchor="end" fill="currentColor">p = 0.9: 0.469 bits</text>
  <text x="350" y="70" font-size="13" fill="currentColor">most uncertain at p = 1/2;</text>
  <text x="350" y="90" font-size="13" fill="currentColor">no uncertainty at p = 0 or 1.</text>
  <text x="350" y="130" font-size="13" fill="currentColor">For k outcomes, H is largest,</text>
  <text x="350" y="150" font-size="13" fill="currentColor">log2 k bits, when all are</text>
  <text x="350" y="170" font-size="13" fill="currentColor">equally likely.</text>
</svg>
<figcaption>The entropy of a coin. Uncertainty is greatest when both outcomes are equally likely.</figcaption>
</figure>

### Cross-entropy and KL divergence

Now suppose the true distribution is $P$ but we use a model $Q$, and score ourselves by the surprise the model assigns to
what actually happens. The expected score is the **cross-entropy**:

$$
H(P,Q)=-\sum_ip_i\log q_i .
$$

How much worse is it than using the truth? The difference is the **Kullback-Leibler divergence** (Kullback and
Leibler, 1951):

$$
D_{\mathrm{KL}}(P\,\|\,Q)=H(P,Q)-H(P)=\sum_ip_i\log\frac{p_i}{q_i}.
$$

For $P=(0.5,0.25,0.25)$ and the uniform $Q=(1/3,1/3,1/3)$, the program gives $H(P)=1.5$ bits, $H(P,Q)=\log_23\approx1.585$
bits, so $D_{\mathrm{KL}}(P\|Q)=0.085$ bits. Swapping the roles gives $D_{\mathrm{KL}}(Q\|P)=0.0817$: KL divergence is
**not symmetric**, so it is not a distance in the sense of a norm. It is a measure of how much is lost by using $Q$ in
place of $P$.

**Theorem (Gibbs' inequality).** $D_{\mathrm{KL}}(P\|Q)\ge0$, with equality exactly when $P=Q$. Equivalently, the
cross-entropy $H(P,Q)$ is smallest, over all models $Q$, at $Q=P$.

**Proof.** Use natural logs (other bases only multiply by a positive constant). The key fact is $\ln x\le x-1$ for all
$x>0$, with equality only at $x=1$: the line $x-1$ is the tangent of the concave curve $\ln x$ at $x=1$, and a concave
curve lies below its tangents. Sum over the $i$ with $p_i>0$:

$$
-D_{\mathrm{KL}}(P\|Q)=\sum_ip_i\ln\frac{q_i}{p_i}\le\sum_ip_i\left(\frac{q_i}{p_i}-1\right)=\sum_iq_i-\sum_ip_i\le1-1=0 .
$$

(The sum of $q_i$ over only those $i$ with $p_i>0$ is at most 1.) Equality needs $q_i/p_i=1$ for every $i$ with
$p_i>0$, and then those $q_i$ already add up to 1, so $Q=P$. $\square$

The program draws 10 000 random pairs of distributions on four outcomes; the smallest KL divergence it sees is
0.001459, positive as the theorem says. A corollary: taking $Q$ uniform over $k$ outcomes, $0\le D_{\mathrm{KL}}(P\|Q)=
\log_2k-H(P)$, so **entropy is at most $\log_2k$**, reached only by the uniform distribution.

### Why this matters: cross-entropy is a likelihood

Suppose a classifier gives each training example $i$ a predicted distribution $q^{(i)}$ over the classes, and the true
class is $c_i$. The log-likelihood of the labels under the model is $\sum_i\ln q^{(i)}_{c_i}$. Minus that, divided by
$n$, is the average cross-entropy between the "true" distribution (all probability on $c_i$) and the prediction
$q^{(i)}$:

$$
-\frac1n\sum_{i=1}^n\ln q^{(i)}_{c_i}=\frac1n\sum_{i=1}^nH\bigl(\text{one-hot}(c_i),\,q^{(i)}\bigr).
$$

So **minimising cross-entropy loss is the same as maximising likelihood**, and by Gibbs' inequality the best possible
prediction, on average, is the true probability. That is why the cross-entropy loss, also called **log loss**, is the
standard loss for classification, from logistic regression in Chapter 6 to the language models of Chapter 19. It also
answers the question at the start of the section: a model that said 90% for rain pays $-\ln0.9\approx0.105$ nats if it
rains and $-\ln0.1\approx2.303$ nats if it does not, and a model that is overconfident is punished hard when it is
wrong.

## Check yourself

??? question "1. For u = (1, 2, 2) and v = (2, 0, 1), compute u · v, both lengths, the cosine of the angle, and the projection of v onto u."

    $u\cdot v=2+0+2=4$. $\lVert u\rVert=\sqrt{1+4+4}=3$, $\lVert v\rVert=\sqrt{4+0+1}=\sqrt5\approx2.236$. Cosine
    $4/(3\sqrt5)\approx0.596$, an angle of about $53.4^\circ$. Projection of $v$ onto $u$: $(u\cdot v/u\cdot u)\,u=
    (4/9)(1,2,2)\approx(0.444,0.889,0.889)$. Check: $v$ minus the projection is $(1.556,-0.889,0.111)$, and its dot
    product with $u$ is $1.556-1.778+0.222=0$.

??? question "2. Compute the L1, L2 and L-infinity norms of (3, -4, 0, 12). Which is largest, and is that always so?"

    L1 $=3+4+0+12=19$, L2 $=\sqrt{9+16+144}=13$, L-infinity $=12$. Always
    $\lVert u\rVert_\infty\le\lVert u\rVert_2\le\lVert u\rVert_1$: the largest entry squared is at most the sum of
    squares, and $(\sum|u_j|)^2=\sum u_j^2+$ (non-negative cross terms) $\ge\sum u_j^2$.

??? question "3. Multiply A = [[1, 2], [0, 1]] by B = [[1, 0], [3, 1]] in both orders. Describe each matrix as a map."

    $AB=\begin{pmatrix}1+6&0+2\\0+3&0+1\end{pmatrix}=\begin{pmatrix}7&2\\3&1\end{pmatrix}$ and
    $BA=\begin{pmatrix}1&2\\3&7\end{pmatrix}$. Different, as expected. $A$ is a **shear** that pushes points sideways
    by twice their height ($e_1\mapsto e_1$, $e_2\mapsto(2,1)$); $B$ shears vertically by three times the $x$
    coordinate.

??? question "4. What shape does NumPy give for arrays of shapes (5, 1, 3) and (4, 1) combined with +? And (5, 3) with (5,)?"

    Compare from the right: (5, 1, 3) and (1, 4, 1) (padding on the left) give (5, 4, 3). For (5, 3) and (5,): the
    last sizes are 3 and 5, neither is 1, so it is an error. To subtract a per-row value you need shape (5, 1), for
    example `v[:, None]`.

??? question "5. Find the gradient of f(w) = (w1 - 1)^2 + 10 (w2 + 2)^2 and its minimum. From w = (0, 0), take one gradient-descent step with learning rate 0.04."

    $\nabla f=(2(w_1-1),\,20(w_2+2))$, zero at $(1,-2)$, the minimum. At $(0,0)$ the gradient is $(-2,40)$. The step
    gives $w=(0,0)-0.04(-2,40)=(0.08,-1.6)$. The steep $w_2$ direction moved 80% of the way at once while $w_1$ moved
    only 8%: the condition number here is $20/2=10$.

??? question "6. Use the chain rule to differentiate h(w) = ln(1 + e^(-w)). (This function is the logistic loss of Chapter 6.)"

    Outer function $\ln u$ with derivative $1/u$; inner $u=1+e^{-w}$ with derivative $-e^{-w}$. So
    $h'(w)=-e^{-w}/(1+e^{-w})=-1/(1+e^{w})$. Check numerically at $w=0$: the formula gives $-0.5$, and
    $(h(10^{-5})-h(-10^{-5}))/(2\cdot10^{-5})\approx-0.5$.

??? question "7. Write the code: a function that checks any gradient function against central differences and returns the relative difference."

    ```python
    import numpy as np

    def check_gradient(F, grad_F, w, h=1e-5):
        num = np.zeros_like(w, dtype=float)
        for j in range(len(w)):
            e = np.zeros_like(w, dtype=float)
            e[j] = h
            num[j] = (F(w + e) - F(w - e)) / (2 * h)
        a = grad_F(w)
        return np.linalg.norm(a - num) / np.linalg.norm(a + num)

    F = lambda w: (w[0] - 1) ** 2 + 10 * (w[1] + 2) ** 2
    G = lambda w: np.array([2 * (w[0] - 1), 20 * (w[1] + 2)])
    print(check_gradient(F, G, np.array([0.3, 0.7])))   # about 1e-11
    ```

    A result near $10^{-7}$ or below means the gradient is right; a result near 1 means it is badly wrong.

??? question "8. A die is loaded so that 6 comes up with probability 1/2 and each other face with probability 1/10. Compute the mean and variance."

    $\mathbb E[X]=(1+2+3+4+5)/10+6/2=1.5+3=4.5$. $\mathbb E[X^2]=(1+4+9+16+25)/10+36/2=5.5+18=23.5$. So
    $\operatorname{Var}(X)=23.5-4.5^2=23.5-20.25=3.25$.

??? question "9. A spam filter flags 90% of spam and 2% of genuine mail. 20% of all mail is spam. What fraction of flagged mail is genuine?"

    $P(\text{flag})=0.9\times0.2+0.02\times0.8=0.18+0.016=0.196$. $P(\text{genuine}\mid\text{flag})=0.016/0.196\approx
    0.0816$: about 8% of flagged messages are genuine. Per 1000 messages: 200 spam, 180 flagged; 800 genuine, 16 flagged.

??? question "10. You observe the waiting times 2, 3, 7 (minutes) and model them as Gaussian. Give the maximum-likelihood mean and variance, and the variance with Bessel's correction."

    $\hat\mu=12/3=4$. Squared deviations $4,1,9$, sum 14. MLE variance $14/3\approx4.667$; with $n-1$: $14/2=7$.

??? question "11. Compute the entropy of (1/2, 1/4, 1/8, 1/8) in bits, and the KL divergence from it to the uniform distribution on four outcomes."

    $H=\tfrac12\cdot1+\tfrac14\cdot2+\tfrac18\cdot3+\tfrac18\cdot3=0.5+0.5+0.375+0.375=1.75$ bits. The uniform
    distribution has cross-entropy $\log_24=2$ bits against any $P$, so $D_{\mathrm{KL}}(P\|U)=2-1.75=0.25$ bits.
    (A code with lengths 1, 2, 3, 3 bits achieves exactly 1.75 bits per symbol for this $P$.)

??? question "12. Show that if a symmetric matrix A has eigenvalues 9 and 1, power iteration's error shrinks by a factor of about 9 per step, and find the eigenvalues of A + 5I. How does adding 5I change the speed?"

    The error shrinks like $|\lambda_2/\lambda_1|^t=(1/9)^t$. $A+5I$ has the same eigenvectors, since
    $(A+5I)v=\lambda v+5v$, and eigenvalues 14 and 6. The ratio becomes $6/14\approx0.43$, so convergence is *slower*:
    shifting by a positive constant brings the eigenvalue ratio closer to 1. Shifting the other way (subtracting
    a constant, as long as the order of the eigenvalue sizes is kept) speeds it up, which is the idea behind shifted
    power iteration.

## What you learned

- A vector is a list of numbers; the dot product $u\cdot v=\lVert u\rVert\lVert v\rVert\cos\theta$ measures alignment,
  Cauchy-Schwarz bounds it, and projection finds the nearest point on a line.
- A matrix is a data table and a linear map; $Xw$ makes one prediction per row, matrix multiplication is composition
  (associative, not commutative), and broadcasting combines shapes without loops.
- The gradient is the direction of steepest increase; the chain rule multiplies rates along a composition; the
  squared-error gradient is $\frac2nX^\top(Xw-y)$; central differences check any gradient to about $h^2$.
- Expectation is linear, variance adds for independent variables, averages tighten like $1/\sqrt n$, and Bayes' rule
  turns $P(\text{evidence}\mid\text{hypothesis})$ into $P(\text{hypothesis}\mid\text{evidence})$.
- Maximum likelihood picks the parameters that make the data most probable: the fraction of heads, the sample mean,
  and a variance that is biased by the factor $(n-1)/n$.
- Symmetric matrices are stretches along orthogonal eigenvectors; power iteration finds the top one; the SVD writes
  any matrix as rotate, stretch, rotate, and truncating it gives the best low-rank approximation.
- Entropy measures uncertainty; KL divergence is never negative; minimising cross-entropy is maximising likelihood.

**Next:** [Chapter 4](04-Linear-Regression.md), the first real model: fitting lines and planes by least squares,
exactly and by gradient descent, with the probabilistic reason for squared error.

## Further reading

- G. Strang, *Introduction to Linear Algebra*, 5th ed., 2016, and *Linear Algebra and Learning from Data*, 2019.
- M. P. Deisenroth, A. A. Faisal and C. S. Ong, *Mathematics for Machine Learning*, 2020: the same topics at the same
  level, in more depth.
- I. Goodfellow, Y. Bengio and A. Courville, *Deep Learning*, 2016, Chapters 2 to 4 (linear algebra, probability and
  information theory, numerical computation).
- C. M. Bishop, *Pattern Recognition and Machine Learning*, 2006, Chapters 1 and 2 (probability, the Gaussian,
  information theory).
- C. E. Shannon, "A Mathematical Theory of Communication", *Bell System Technical Journal*, 1948.
- S. Kullback and R. A. Leibler, "On Information and Sufficiency", *Annals of Mathematical Statistics*, 1951.
- C. Eckart and G. Young, "The Approximation of One Matrix by Another of Lower Rank", *Psychometrika*, 1936.
- T. M. Cover and J. A. Thomas, *Elements of Information Theory*, 2nd ed., 2006.
- On this site: the math books on [linear algebra](https://math.akadian.ca/books/linear-algebra/),
  [calculus](https://math.akadian.ca/books/calculus/), [probability](https://math.akadian.ca/books/probability/) and
  [statistics](https://math.akadian.ca/books/statistics/); [Huffman coding](../../greedy/huffman.md) and
  [Chapter 12 of the Algorithms book](../algorithms/12-Greedy-Algorithms.md) for codes that approach the entropy.
