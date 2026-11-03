# 5. Optimization for learning

*Every model in this book is trained the same way: write down a loss that measures how wrong the model is, then move
the parameters downhill until the loss is small. Chapter 4 did this for a line with a closed formula and with plain
gradient descent. This chapter asks the questions that formula hid. When does going downhill reach the bottom, and how
fast? Why does it help to use a random handful of examples instead of all of them? Why do almost all deep networks
train with something called Adam? You will prove that gradient descent converges on convex problems at rate $1/k$,
build stochastic gradient descent, momentum, Nesterov's method, AdaGrad, RMSProp, Adam, Newton's method and L-BFGS
from scratch, race them on the same problems, and finish on the non-convex landscapes of deep learning, where the
theory gets thin and the questions are still open.*

!!! abstract "In this chapter"
    **You will learn:**

    - what a convex function and a convex set are, and why on a convex problem every local minimum is a global one (proved)
    - why gradient descent with step $1/L$ on an $L$-smooth convex function gets within $LR^2/(2k)$ of the best value after $k$ steps (proved), and why that rate cannot be improved for plain gradient descent
    - stochastic and mini-batch gradient descent, an honest convergence bound for them, and why their noise is sometimes useful
    - momentum (heavy ball) and Nesterov's accelerated gradient, and why they turn a condition number $\kappa$ into $\sqrt\kappa$
    - AdaGrad, RMSProp and Adam, derived step by step, including Adam's bias correction
    - Newton's method, its quadratic convergence, and the quasi-Newton method L-BFGS
    - learning-rate schedules and warmup, and what is known about saddle points and non-convex landscapes

    **You need:** gradients and the chain rule from [Chapter 3](03-The-Math-Toolkit.md), and gradient descent on
    linear regression from [Chapter 4](04-Linear-Regression.md). The [calculus](https://math.akadian.ca/books/calculus/)
    and [linear algebra](https://math.akadian.ca/books/linear-algebra/) books cover Taylor's theorem and eigenvalues
    if they are rusty.

    **Levels:** 5.1 and 5.3 are beginner to intermediate; 5.2, 5.4 and 5.5 are intermediate; 5.6 is advanced; the
    second half of 5.7 (non-convex landscapes) is advanced.

## 5.1 Loss landscapes and convexity

Suppose a model has parameters $w=(w_1,\dots,w_d)$, a list of $d$ numbers, and a loss $f(w)$ that says how badly it
fits the training data. Training means finding a $w$ with small $f(w)$. Picture $f$ as a landscape: for two
parameters, $w_1$ and $w_2$ are east and north, and $f(w)$ is the height of the ground. Training is walking downhill
in fog: you cannot see the whole landscape, only the slope under your feet.

That slope is the **gradient** $\nabla f(w)$, the vector of partial derivatives
$(\partial f/\partial w_1,\dots,\partial f/\partial w_d)$. Chapter 3 showed that it points in the direction in which
$f$ rises fastest, so $-\nabla f(w)$ points straight downhill. **Gradient descent** takes a step that way:

$$w_{k+1}=w_k-\alpha\,\nabla f(w_k),$$

where $\alpha>0$ is the **step size** or **learning rate**. Everything in this chapter is a variation on this one
line.

### Minima

A point $w^*$ is a **global minimum** if $f(w^*)\le f(w)$ for every $w$. It is a **local minimum** if
$f(w^*)\le f(w)$ for every $w$ near $w^*$ (within some small distance). A walker who only feels the slope stops
wherever the ground is flat, that is wherever $\nabla f(w)=0$; such points are called **critical points** or
**stationary points**. Flat ground can be a valley floor (a minimum), a hilltop (a maximum), or a mountain pass, flat
but going down in one direction and up in another (a **saddle point**). The worry is obvious: the walker can stop in
a small dip on the side of the mountain, far above the true valley. For one large family of losses this cannot happen.

### Convex sets and convex functions

A set $C$ of points is **convex** if the straight segment between any two of its points stays inside it: for all
$x,y\in C$ and all $t\in[0,1]$, the point $tx+(1-t)y$ is in $C$. A disc, a square, a half-plane and a whole space
are convex; a ring or a crescent is not.

A function $f$ is **convex** if the chord between any two points of its graph lies on or above the graph:

$$f\bigl(tx+(1-t)y\bigr)\le t\,f(x)+(1-t)\,f(y)\qquad\text{for all }x,y\text{ and all }t\in[0,1].$$

The left side is the height of the graph at a point between $x$ and $y$; the right side is the height of the chord
at the same place. It is **strictly convex** if the inequality is strict whenever $x\ne y$ and $0<t<1$.

<figure class="mars-fig" markdown="0">
<svg viewBox="0 0 660 260" role="img" aria-label="Two curves side by side. Left: a convex bowl with a chord between two points of the curve lying above the curve everywhere; one minimum. Right: a wavy non-convex curve with two dips, a local minimum on the left that is higher than the global minimum on the right, and a chord that passes below the curve over the bump between them.">
  <g fill="none" stroke="currentColor" stroke-width="1.2">
    <line x1="30" y1="220" x2="310" y2="220"/>
    <line x1="350" y1="220" x2="630" y2="220"/>
  </g>
  <path d="M40,40 Q170,330 300,40" fill="none" stroke="#9cc9ea" stroke-width="3"/>
  <line x1="72" y1="103" x2="268" y2="103" stroke="#eea66f" stroke-width="2.5"/>
  <circle cx="72" cy="103" r="5" fill="#eea66f"/><circle cx="268" cy="103" r="5" fill="#eea66f"/>
  <circle cx="170" cy="185" r="5" fill="#7ccf9a" stroke="currentColor"/>
  <g font-size="13" fill="currentColor" text-anchor="middle">
    <text x="170" y="92">chord above the graph</text>
    <text x="170" y="207">the only minimum</text>
    <text x="170" y="245">convex</text>
  </g>
  <path d="M360,60 C390,60 400,150 430,150 C460,150 470,80 500,80 C540,80 550,200 585,200 C610,200 615,90 625,60" fill="none" stroke="#9cc9ea" stroke-width="3"/>
  <line x1="430" y1="150" x2="585" y2="200" stroke="#eea66f" stroke-width="2.5"/>
  <circle cx="430" cy="150" r="5" fill="#7ccf9a" stroke="currentColor"/>
  <circle cx="585" cy="200" r="5" fill="#7ccf9a" stroke="currentColor"/>
  <g font-size="13" fill="currentColor" text-anchor="middle">
    <text x="415" y="182">local minimum</text>
    <text x="512" y="162">chord</text>
    <text x="582" y="215">global minimum</text>
    <text x="490" y="245">not convex</text>
  </g>
</svg>
<figcaption>Figure 5.1. Left: a convex function; every chord lies on or above the graph and there is one valley. Right: a non-convex function; the chord between the two dips passes under the bump, and a walker who starts on the left stops in the higher dip.</figcaption>
</figure>

Examples you will meet again: $f(w)=\lVert w\rVert^2$ (the bowl), the squared-error loss of linear regression,
$|w|$, $\log(1+e^{w})$ (part of the logistic loss of Chapter 6), every linear function (convex and also concave, the
chord lies exactly on it), and any sum of convex functions with non-negative weights. Not convex: $\sin w$, and
$w_1^2-w_2^2$, a saddle. The first part of the chapter's code tests the definition directly on random chords; one
failing chord proves a function is not convex, while passing many is only evidence.

```
1. convexity test on random chords
   x^2 + y^2    convex? True
   |x| + |y|    convex? True
   log(1+e^x)   convex? True
   sin(x)       convex? False
   x^2 - y^2    convex? False
```

Two more tests are easier to use than the definition. They are standard facts; we prove the first because we need it.

**First-order condition.** A differentiable $f$ is convex if and only if every tangent plane lies on or below the
graph:

$$f(y)\ge f(x)+\nabla f(x)^\top(y-x)\qquad\text{for all }x,y.$$

*Proof of "convex implies tangent below".* Fix $x,y$ and $t\in(0,1]$. Convexity with the point $x+t(y-x)=ty+(1-t)x$
gives $f(x+t(y-x))\le f(x)+t\,(f(y)-f(x))$. Subtract $f(x)$ and divide by $t$:

$$\frac{f(x+t(y-x))-f(x)}{t}\le f(y)-f(x).$$

As $t\to0$ the left side tends to the directional derivative $\nabla f(x)^\top(y-x)$, which gives the inequality.
(The converse, tangent-below implies convex, is proved by applying the inequality at the point $z=tx+(1-t)y$ towards
$x$ and towards $y$ and adding; Boyd and Vandenberghe, section 3.1.3, write it out.) $\square$

**Second-order condition.** A twice-differentiable $f$ is convex if and only if its **Hessian**, the matrix
$H=\nabla^2 f$ of second partial derivatives, is positive semidefinite everywhere: $v^\top H v\ge0$ for every vector
$v$, which is the same as all eigenvalues of $H$ being $\ge0$. In one variable this says $f''\ge0$: the slope never
decreases. For $f(w)=\lVert Xw-y\rVert^2$ the Hessian is $2X^\top X$, and $v^\top X^\top Xv=\lVert Xv\rVert^2\ge0$, so
least squares is convex.

### Why convex is easy

**Theorem 5.1.** If $f$ is convex, every local minimum is a global minimum. If $f$ is differentiable and convex, every
point with $\nabla f(w^*)=0$ is a global minimum. If $f$ is strictly convex, there is at most one minimum.

*Proof.* Let $w^*$ be a local minimum and suppose some $y$ had $f(y)<f(w^*)$. For small $t>0$ the point
$z=(1-t)w^*+ty$ is as close to $w^*$ as we like, so $f(z)\ge f(w^*)$ by local minimality. But convexity gives
$f(z)\le(1-t)f(w^*)+tf(y)<(1-t)f(w^*)+tf(w^*)=f(w^*)$. Contradiction, so no such $y$ exists.

If $\nabla f(w^*)=0$, the first-order condition gives $f(y)\ge f(w^*)+0$ for every $y$.

If $f$ is strictly convex and $a\ne b$ were both minima with value $m$, then
$f(\tfrac12a+\tfrac12b)<\tfrac12m+\tfrac12m=m$, which is smaller than the minimum. Contradiction. $\square$

So on a convex loss there are no traps: any downhill method that reaches flat ground has solved the problem. Linear
regression (Chapter 4), logistic regression (Chapter 6), ridge and lasso (Chapter 8) and support vector machines
(Chapter 10) all have convex losses. Neural networks (Chapter 15 on) do not, which is why 5.7 exists.

## 5.2 How fast gradient descent converges

*Level: intermediate.*

Theorem 5.1 says *where* we end up. Now: how many steps does it take, and how big may the step be? Too small a step
and we crawl; too large and we overshoot. On $f(w)=w^2$ the gradient is $2w$, so gradient descent is
$w\leftarrow w-2\alpha w=(1-2\alpha)w$. From $w_0=1$:

| step size $\alpha$ | factor $1-2\alpha$ | $w_1,w_2,w_3,w_4$ | behaviour |
|---|---|---|---|
| 0.1 | 0.8 | 0.8, 0.64, 0.512, 0.4096 | slow and steady |
| 0.5 | 0 | 0, 0, 0, 0 | lands on the minimum in one step |
| 0.9 | $-0.8$ | $-0.8$, 0.64, $-0.512$, 0.4096 | jumps across the valley each time, still shrinks |
| 1.1 | $-1.2$ | $-1.2$, 1.44, $-1.728$, 2.0736 | diverges |

The safe range depends on how sharply the function curves, here $f''=2$: any $\alpha<2/f''=1$ converges. In many
dimensions we need a bound on the curvature everywhere.

### Smoothness

A differentiable $f$ is **$L$-smooth** if its gradient never changes faster than $L$ times the distance moved:

$$\lVert\nabla f(x)-\nabla f(y)\rVert\le L\,\lVert x-y\rVert\qquad\text{for all }x,y.$$

For a twice-differentiable function this is the same as every eigenvalue of the Hessian lying between $-L$ and $L$.
For least squares $f(w)=\tfrac1n\lVert Xw-y\rVert^2$ the Hessian is the constant $\tfrac2nX^\top X$, so $L$ is its
largest eigenvalue. Smoothness gives a quadratic *upper* bound on $f$, the mirror image of the tangent lower bound.

**Lemma 5.2 (descent lemma).** If $f$ is $L$-smooth, then for all $x,y$

$$f(y)\le f(x)+\nabla f(x)^\top(y-x)+\frac L2\lVert y-x\rVert^2.$$

*Proof.* Write $f(y)-f(x)$ as the integral of the derivative along the segment, $g(t)=f(x+t(y-x))$:

$$f(y)-f(x)=\int_0^1\nabla f(x+t(y-x))^\top(y-x)\,dt.$$

Subtract $\nabla f(x)^\top(y-x)=\int_0^1\nabla f(x)^\top(y-x)\,dt$ and use Cauchy-Schwarz and smoothness inside the
integral:

$$f(y)-f(x)-\nabla f(x)^\top(y-x)\le\int_0^1 L\,t\,\lVert y-x\rVert\cdot\lVert y-x\rVert\,dt=\frac L2\lVert y-x\rVert^2.\quad\square$$

Put $y=x-\alpha\nabla f(x)$, one gradient step. Then $y-x=-\alpha\nabla f(x)$ and the lemma gives

$$f(y)\le f(x)-\alpha\Bigl(1-\frac{L\alpha}2\Bigr)\lVert\nabla f(x)\rVert^2.$$

For any $0<\alpha<2/L$ the bracket is positive, so **every step decreases the loss** unless the gradient is already
zero. The decrease is largest at $\alpha=1/L$, where it is $\lVert\nabla f(x)\rVert^2/(2L)$. This holds for any
smooth function, convex or not.

### The $1/k$ rate

**Theorem 5.3.** Let $f$ be convex and $L$-smooth with a minimiser $w^*$, and run gradient descent with $\alpha=1/L$
from $w_0$. Write $R=\lVert w_0-w^*\rVert$ and $f^*=f(w^*)$. Then after $k$ steps

$$f(w_k)-f^*\le\frac{L R^2}{2k}.$$

*Proof.* Write $g=\nabla f(w)$ and $w^+=w-g/L$. The descent lemma gives $f(w^+)\le f(w)-\lVert g\rVert^2/(2L)$. The
first-order condition of convexity, with $y=w^*$, gives $f(w)\le f^*+g^\top(w-w^*)$. Together:

$$f(w^+)-f^*\le g^\top(w-w^*)-\frac1{2L}\lVert g\rVert^2.$$

Now expand the distance to the optimum after the step:
$\lVert w^+-w^*\rVert^2=\lVert w-w^*\rVert^2-\tfrac2Lg^\top(w-w^*)+\tfrac1{L^2}\lVert g\rVert^2$. Multiply by $L/2$
and rearrange; the right side above is exactly

$$f(w^+)-f^*\le\frac L2\Bigl(\lVert w-w^*\rVert^2-\lVert w^+-w^*\rVert^2\Bigr).$$

Apply this at steps $0,1,\dots,k-1$ and add. The right side telescopes: all middle distances cancel, leaving

$$\sum_{i=1}^{k}\bigl(f(w_i)-f^*\bigr)\le\frac L2\Bigl(\lVert w_0-w^*\rVert^2-\lVert w_k-w^*\rVert^2\Bigr)\le\frac{LR^2}2.$$

The descent lemma says the values $f(w_i)$ never increase, so the last one is the smallest of the $k$ terms, and $k$
times the smallest is at most the sum: $k\,(f(w_k)-f^*)\le LR^2/2$. $\square$

The proof also showed something reassuring: the distance to $w^*$ never grows, so the iterates stay in a ball around
the start. To halve the error bound you need twice as many steps; to get within $\varepsilon$ you need about
$LR^2/(2\varepsilon)$ steps.

### Checking it, and seeing that it is tight

The chapter's first program runs gradient descent with $\alpha=1/L$ on the logistic-regression loss of Chapter 6 for
200 synthetic points, computes $w^*$ to machine precision with Newton's method (5.6), and prints the gap next to the
bound:

```python
--8<-- "books/machine-learning/ch05_gradient_descent.py"
```

Output:

```
1. convexity test on random chords
   x^2 + y^2    convex? True
   |x| + |y|    convex? True
   log(1+e^x)   convex? True
   sin(x)       convex? False
   x^2 - y^2    convex? False

2. gradient descent with step 1/L on logistic loss, L = 0.2728
     k    f(w_k)-f*    bound L*R^2/(2k)   ratio
     1   5.422e-02     7.780e-01        0.0697
     2   2.602e-02     3.890e-01        0.0669
     5   5.461e-03     1.556e-01        0.0351
    10   7.219e-04     7.780e-02        0.0093
    50   7.247e-10     1.556e-02        0.0000
   100   5.551e-17     7.780e-03        0.0000
  1000   5.551e-17     7.780e-04        0.0000

   worst 1-D quadratic for each k (L = 1, R = 1)
     k    f(x_k)-f*    bound      ratio
     1   7.407e-02   5.000e-01   0.1481
    10   8.974e-03   5.000e-02   0.1795
   100   9.174e-04   5.000e-03   0.1835
  1000   9.195e-05   5.000e-04   0.1839

3. excess training MSE after each epoch (best MSE = 0.2369)
   method                      updates  ep1       ep2       ep3       ep5
   full batch, lr 0.1               5  3.16e-01  2.06e-01  1.34e-01  5.71e-02
   batch 1, lr 0.01              5000  1.11e-02  1.38e-02  6.17e-03  6.99e-03
   batch 1, lr 0.01 decaying     5000  2.55e-04  4.58e-05  1.35e-05  2.04e-06
   batch 32, lr 0.05              160  7.29e-03  2.38e-03  1.32e-04  7.54e-04

4. steps to reach f < 1e-8 on a quadratic with condition number 100
   gd            882
   heavy ball     81
   nesterov      108
   predicted rates per step: gd 0.9900, heavy ball 0.8182, nesterov 0.9000
```

The bound holds at every step, and on this problem it is very loose: by step 100 the gap is at the level of rounding
error ($5.6\times10^{-17}$), while the bound still allows $0.0078$. That is because this loss curves upward in every
direction near its minimum, which gives a much faster rate (below). The bound is a guarantee for the *worst*
function, so the second block builds one. For each $k$ it takes the one-variable quadratic $f(x)=\lambda x^2/2$ with
$\lambda=1/(2k+1)$, flat enough that $k$ steps of size $1$ barely move. The gap stays at a fixed fraction of the
bound, $0.1839\approx1/(2e)$, for every $k$. No faster rate of the form $C/k^{1+\epsilon}$ can hold for gradient
descent on all smooth convex functions.

That is a statement about *plain gradient descent*. Nesterov proved in 1983 that a cleverer method reaches
$O(LR^2/k^2)$, and that no method which only looks at gradients can beat order $1/k^2$ in general (Nesterov,
*Introductory Lectures on Convex Optimization*, 2004, chapter 2). We meet his method in 5.4.

### Strong convexity: from $1/k$ to a constant factor per step

A function is **$\mu$-strongly convex** (with $\mu>0$) if it curves upward at least as much as $\tfrac\mu2\lVert
w\rVert^2$: $f(y)\ge f(x)+\nabla f(x)^\top(y-x)+\tfrac\mu2\lVert y-x\rVert^2$. For a twice-differentiable function
this means all Hessian eigenvalues are at least $\mu$. The ratio $\kappa=L/\mu\ge1$ is the **condition number**: how
much more steeply the steepest direction curves than the flattest.

For a quadratic $f(w)=\tfrac12w^\top Qw$ with eigenvalues between $\mu$ and $L$, write $w$ in the eigenvector basis.
Gradient descent with $\alpha=1/L$ multiplies the coordinate along an eigenvector with eigenvalue $\lambda$ by
$1-\lambda/L$, a number between $0$ and $1-\mu/L$. So the distance to the minimum shrinks by at least the factor
$1-1/\kappa$ every step: **linear convergence** (the error falls like $c^k$, a straight line on a log plot). For
every $\mu$-strongly convex $L$-smooth function the loss gap shrinks by the same factor. Minimising both sides of the
strong-convexity inequality over $y$ gives $f^*\ge f(x)-\lVert\nabla f(x)\rVert^2/(2\mu)$, that is
$\lVert\nabla f(x)\rVert^2\ge2\mu\,(f(x)-f^*)$; put this into the descent lemma's
$f(w^+)\le f(w)-\lVert\nabla f(w)\rVert^2/(2L)$ and you get $f(w^+)-f^*\le(1-\mu/L)\,(f(w)-f^*)$. With $\kappa=100$
that is $0.99$ per step, and the fourth block of the program needs 882 steps to bring $f$ below $10^{-8}$ (from
$f(w_0)=50.5$; along the flat direction $f=\tfrac12(0.99)^{2k}$, and $\tfrac12(0.99)^{2k}<10^{-8}$ first when
$k=882$). Badly conditioned problems are slow, and much of the rest of the chapter is about curing that. This is also
why Chapter 2 scaled the features: features on wildly different scales make $\kappa$ huge.

## 5.3 Stochastic and mini-batch gradient descent

Most losses in machine learning are averages over the $n$ training examples:

$$f(w)=\frac1n\sum_{i=1}^n\ell_i(w),$$

where $\ell_i$ is the loss on example $i$. One gradient of $f$ costs a pass over all $n$ examples. With a million
images, one step means a million forward and backward passes, and gradient descent needs thousands of steps.

**Stochastic gradient descent** (SGD) picks one example $i$ at random and steps along its gradient alone:

$$w_{k+1}=w_k-\alpha_k\nabla\ell_{i_k}(w_k).$$

Each step is $n$ times cheaper. It is noisy, since one example's gradient can point somewhere quite different from the
average, but it is right *on average*: if $i$ is uniform on $\{1,\dots,n\}$, then
$\mathbb E[\nabla\ell_i(w)]=\tfrac1n\sum_i\nabla\ell_i(w)=\nabla f(w)$. An estimate whose average is the true value is
called **unbiased**.

**Mini-batch** SGD is the middle road: average the gradients of a random batch $B$ of, say, 32 or 256 examples. It is
still unbiased, and its noise is smaller. If one example's gradient has variance $\sigma^2$ (its average squared
distance from $\nabla f$), the average of $b$ independent ones has variance $\sigma^2/b$, because variances of
independent terms add and dividing by $b$ divides the variance by $b^2$. In practice people shuffle the data once per
**epoch** (one pass over all examples) and walk through it in batches, which is what our code does. Batches also suit
the hardware: a graphics processor computes 256 gradients in parallel in about the time of one.

### What SGD can promise

SGD with a constant step does not converge to the exact minimum: near the bottom, the noise keeps kicking it around.
Here is the classic honest bound. Assume $f$ is convex, the minimiser is $w^*$ with $\lVert w_0-w^*\rVert\le R$, and
every stochastic gradient has $\mathbb E\lVert g_k\rVert^2\le G^2$.

**Theorem 5.4.** SGD with constant step $\alpha$ for $K$ steps, reporting the average iterate
$\bar w=\tfrac1K\sum_{k=0}^{K-1}w_k$, satisfies

$$\mathbb E[f(\bar w)]-f^*\le\frac{R^2}{2\alpha K}+\frac{\alpha G^2}2.$$

With $\alpha=R/(G\sqrt K)$ the right side is $RG/\sqrt K$.

*Proof.* Expand one step:
$\lVert w_{k+1}-w^*\rVert^2=\lVert w_k-w^*\rVert^2-2\alpha\,g_k^\top(w_k-w^*)+\alpha^2\lVert g_k\rVert^2$. Take the
expectation over the random example at step $k$, with $w_k$ fixed: $g_k$ averages to $\nabla f(w_k)$, and convexity
gives $\nabla f(w_k)^\top(w_k-w^*)\ge f(w_k)-f^*$. So

$$2\alpha\,\mathbb E[f(w_k)-f^*]\le\mathbb E\lVert w_k-w^*\rVert^2-\mathbb E\lVert w_{k+1}-w^*\rVert^2+\alpha^2G^2.$$

Add over $k=0,\dots,K-1$; the distances telescope to at most $R^2$:
$2\alpha\sum_k\mathbb E[f(w_k)-f^*]\le R^2+K\alpha^2G^2$. Divide by $2\alpha K$, and use convexity once more (Jensen's
inequality, $f(\bar w)\le\tfrac1K\sum f(w_k)$). Choosing $\alpha$ to balance the two terms gives the second claim.
$\square$

Read the two terms. The first, $R^2/(2\alpha K)$, is the cost of the distance we must travel; it falls as we take more
steps. The second, $\alpha G^2/2$, is a **noise floor** that does not fall with $K$: a constant step leaves you
bouncing in a region whose size is proportional to $\alpha$. To reach the exact minimum, the step must shrink. Robbins
and Monro (1951), who started this subject, required $\sum_k\alpha_k=\infty$ (enough total distance to get anywhere)
and $\sum_k\alpha_k^2<\infty$ (noise that eventually dies), for example $\alpha_k=c/k$.

The rate $1/\sqrt K$ looks worse than gradient descent's $1/k$, but count work, not steps. To reach error
$\varepsilon$, SGD needs about $1/\varepsilon^2$ steps of cost one example each, *independent of $n$*; gradient
descent needs $1/\varepsilon$ steps of cost $n$. When $n$ is a million and we only need two or three digits of
accuracy (the data are noisy anyway; 7.4 and 8.2 explain why more is wasted), SGD wins by a wide margin. Bottou and
Bousquet (2008) made this trade-off precise.

### The race

The third block of the program fits linear regression with 1000 examples and 5 features, with the same budget of 5
epochs for each method. Full-batch gradient descent gets 5 updates; batch size 1 gets 5000.

| method | updates | excess MSE after 1 epoch | after 5 epochs |
|---|---|---|---|
| full batch, $\alpha=0.1$ | 5 | 0.316 | 0.0571 |
| batch 1, $\alpha=0.01$ | 5000 | 0.0111 | 0.00699 |
| batch 1, $\alpha=0.01/(1+0.01t)$ | 5000 | 0.000255 | 0.00000204 |
| batch 32, $\alpha=0.05$ | 160 | 0.00729 | 0.000754 |

Three lessons, all predicted by Theorem 5.4. For the same data passes, the stochastic methods are far ahead after one
epoch. With a constant step, batch-1 SGD stalls on its noise floor: its loss even goes *up* from epoch 1 to epoch 2.
A decaying step removes the floor and keeps improving. The batch of 32, with variance 32 times smaller, sits on a
lower floor even with a larger step.

### Noise as a feature

On non-convex losses, the noise of SGD may help as well as hurt. A noisy walker does not stay balanced on a saddle
point (5.7), and some researchers argue that small-batch noise steers training towards wide, flat valleys whose loss
changes little when the weights are perturbed, and that such solutions generalise better. Keskar et al. (2017) found
that very large batches tended to reach sharper minima with worse test accuracy on the networks they studied. This is
an active and contested area (Dinh et al. 2017 showed that "sharpness" depends on how the network is parameterised),
so treat it as a useful intuition rather than a law.

## 5.4 Momentum and Nesterov

*Level: intermediate.*

Look back at the badly conditioned quadratic. Along the steep direction the gradient is large and gradient descent
overshoots, back and forth across the valley; along the shallow direction it is tiny and progress crawls. The picture
is a zigzag.

<figure class="mars-fig" markdown="0">
<svg viewBox="0 0 680 300" role="img" aria-label="Elliptical contour lines of a long narrow valley centred in the picture. A gradient descent path in orange starts at the upper left and zigzags sharply up and down across the valley while creeping right. A momentum path in green starts at the same point and curves smoothly down and along the valley floor, ending near the centre.">
  <g fill="none" stroke="currentColor" stroke-opacity="0.45" stroke-width="1">
    <ellipse cx="340" cy="150" rx="330" ry="104"/>
    <ellipse cx="340" cy="150" rx="208" ry="66"/>
    <ellipse cx="340" cy="150" rx="120" ry="38"/>
    <ellipse cx="340" cy="150" rx="60" ry="19"/>
  </g>
  <circle cx="340" cy="150" r="4" fill="currentColor"/>
  <polyline points="70,90 119,198 158,112 191,181 218,125 240,170 258,134 273,163 285,140 295,158 303,144 310,155 315,146 320,153 323,147" fill="none" stroke="#eea66f" stroke-width="2.5"/>
  <polyline points="70,90 84,120 106,156 133,178 163,180 192,166 220,148 246,137 268,135 288,142 304,150 317,156 328,157 335,154 341,150" fill="none" stroke="#7ccf9a" stroke-width="2.5"/>
  <circle cx="70" cy="90" r="5" fill="currentColor"/>
  <g font-size="13" fill="currentColor">
    <text x="20" y="80">start</text>
    <text x="350" y="140">minimum</text>
    <text x="30" y="280">orange: gradient descent, step 0.18, f = 0.195 after 14 steps</text>
    <text x="30" y="296">green: heavy-ball momentum, step 0.05, beta 0.7, f = 0.0008 after 14 steps</text>
  </g>
</svg>
<figcaption>Figure 5.2. Fourteen steps on f(w) = (w1² + 10 w2²)/2 from (−9, 2), where f = 60.5. Plain gradient descent bounces across the steep direction; momentum averages the bounces away and keeps its speed along the valley.</figcaption>
</figure>

### The heavy ball

Boris Polyak's idea (1964) is physical: let the walker be a heavy ball with inertia. It keeps a **velocity** $v$ that
accumulates gradients and decays a little each step:

$$v_{k+1}=\beta v_k+\nabla f(w_k),\qquad w_{k+1}=w_k-\alpha\,v_{k+1},$$

with $\beta$ between 0 and 1, typically 0.9. Equivalently, $w_{k+1}=w_k-\alpha\nabla f(w_k)+\beta(w_k-w_{k-1})$: a
gradient step plus a fraction of the previous move. Gradients that flip sign each step (across the valley) cancel in
$v$; gradients that keep pointing the same way (along the valley) add up, and with constant gradient $g$ the velocity
grows to $g/(1-\beta)$, ten times $g$ when $\beta=0.9$.

A hand trace on $f(w)=w^2$ (gradient $2w$) with $\alpha=0.1$, $\beta=0.5$ and $w_{-1}=w_0=1$:

| $k$ | gradient step $w_k-0.2w_k$ | plus $0.5(w_k-w_{k-1})$ | $w_{k+1}$ | plain GD |
|---|---|---|---|---|
| 0 | 0.8 | 0 | 0.8 | 0.8 |
| 1 | 0.64 | $-0.1$ | 0.54 | 0.64 |
| 2 | 0.432 | $-0.13$ | 0.302 | 0.512 |
| 3 | 0.2416 | $-0.119$ | 0.1226 | 0.4096 |
| 4 | 0.09808 | $-0.0897$ | 0.00838 | 0.32768 |

The momentum term keeps pushing in the direction the ball was already rolling, so it gets much closer in five steps.
(It will slightly overshoot zero next; a heavy ball oscillates around the bottom before it settles.)

### Why momentum turns $\kappa$ into $\sqrt\kappa$

On a quadratic, each eigen-direction with eigenvalue $\lambda$ evolves separately:
$x_{k+1}=(1+\beta-\alpha\lambda)x_k-\beta x_{k-1}$. This is a linear recurrence, and its speed is set by the roots of
$r^2-(1+\beta-\alpha\lambda)r+\beta=0$. When the roots are complex, both have absolute value $\sqrt\beta$ (their
product is $\beta$). Polyak chose

$$\alpha=\frac4{(\sqrt L+\sqrt\mu)^2},\qquad\beta=\Bigl(\frac{\sqrt\kappa-1}{\sqrt\kappa+1}\Bigr)^2,$$

which makes the roots complex for every $\lambda$ between $\mu$ and $L$ (one can check the discriminant
$(1+\beta-\alpha\lambda)^2-4\beta\le0$ on that whole interval, with equality at the two ends). So every direction
shrinks by about $\sqrt\beta=(\sqrt\kappa-1)/(\sqrt\kappa+1)$ per step. For $\kappa=100$ that is $9/11\approx0.818$,
against $0.99$ for gradient descent. Steps needed to shrink an error by a factor $\varepsilon$ go from about
$\kappa\ln(1/\varepsilon)$ to about $\tfrac{\sqrt\kappa}2\ln(1/\varepsilon)$: with $\kappa=10^4$, a hundred times fewer.
The program confirms it: 882 steps for gradient descent, 81 for the heavy ball. On general (non-quadratic) strongly
convex functions the heavy ball's acceleration is not guaranteed, and examples are known where it fails to converge.

### Nesterov's accelerated gradient

Yurii Nesterov (1983) found a variant with a guarantee for *every* smooth convex function. Look ahead first, then
take the gradient there:

$$y_k=w_k+\beta_k(w_k-w_{k-1}),\qquad w_{k+1}=y_k-\frac1L\nabla f(y_k).$$

The momentum step moves to $y_k$, and the gradient is measured where the ball is about to be, so if it is about to
climb the far wall, the gradient there already pushes it back. With $\beta_k=(k-1)/(k+2)$ the method satisfies
$f(w_k)-f^*\le2LR^2/(k+1)^2$ on any $L$-smooth convex function, matching the $1/k^2$ lower bound; with constant
$\beta=(\sqrt\kappa-1)/(\sqrt\kappa+1)$ on $\mu$-strongly convex functions the error falls by about $1-1/\sqrt\kappa$
per step (Nesterov 2004, section 2.2). The proofs use an "estimate sequence" or a potential function and take a few
pages; Bubeck's monograph (2015, section 3.7) has a readable one. The program's 108 steps for Nesterov against 81 for
the heavy ball are consistent with the predicted rates of $0.90$ and $0.818$: on quadratics the heavy ball with
Polyak's tuning is slightly faster; Nesterov's advantage is that its guarantee holds beyond quadratics.

In deep learning both are used with $\beta\approx0.9$ and a step chosen by trial; Sutskever et al. (2013) showed
that momentum, with a careful schedule and initialisation, made plain SGD competitive for training deep networks.

## 5.5 Adaptive methods: AdaGrad, RMSProp, Adam

*Level: intermediate.*

Momentum fixes zigzags, but there is a single step size for every parameter. Suppose one feature is measured in
metres and another in millimetres: their gradients differ by factors of a thousand, and no one step suits both. Or a
word that appears once in ten thousand sentences: its embedding weights get a gradient rarely, and when they do, the
step should be large. **Adaptive methods** give every parameter its own step, scaled by the size of its recent
gradients. All the operations below are elementwise: $g^2$ means each component squared, and $\sqrt v$ and the
division are taken component by component.

### AdaGrad

Duchi, Hazan and Singer (2011) proposed accumulating the squared gradients of each parameter and dividing by their
square root:

$$v_k=v_{k-1}+g_k^2,\qquad w_{k+1}=w_k-\frac{\alpha}{\sqrt{v_k}+\epsilon}\,g_k,$$

where $\epsilon$ (say $10^{-8}$) avoids dividing by zero. A parameter that has seen large gradients gets small steps;
a rarely updated one keeps large steps. Two things follow. The method is **scale-free per coordinate**: multiply
feature $j$ by 100 and its gradients by 100, and $\sqrt{v}$ grows by 100 too, so the step on $w_j$ is the same as
before (exactly, apart from $\epsilon$). And because $v$ only grows, steps shrink roughly like $1/\sqrt k$, which is
the decaying schedule Theorem 5.4 asked for. Duchi et al. proved a regret bound (a measure of total loss along the
way) for convex problems that adapts to the geometry of the gradients. The weakness is the same shrinking: in long
non-convex training, the steps become too small long before the end.

### RMSProp

Replace the sum by an **exponential moving average**, which forgets old gradients:

$$v_k=\rho\,v_{k-1}+(1-\rho)\,g_k^2,\qquad w_{k+1}=w_k-\frac{\alpha}{\sqrt{v_k}+\epsilon}\,g_k,$$

with $\rho\approx0.9$. Now $v_k$ estimates the *recent* mean square of the gradient (hence the name: root mean square
propagation), and the step no longer shrinks forever. RMSProp was introduced by Geoffrey Hinton in his 2012 online
lecture course on neural networks; it was never published as a paper, and later papers cite the lecture slides.

### Adam

Kingma and Ba (2014, published at ICLR 2015) combined RMSProp's per-parameter scaling with momentum, both as moving
averages, and fixed a bias that moving averages have at the start. **Adam** (adaptive moment estimation) keeps a first
moment $m$ (an average of gradients) and a second moment $v$ (an average of squared gradients):

$$\begin{aligned}
m_k&=\beta_1m_{k-1}+(1-\beta_1)g_k, & v_k&=\beta_2v_{k-1}+(1-\beta_2)g_k^2,\\
\hat m_k&=\frac{m_k}{1-\beta_1^k}, & \hat v_k&=\frac{v_k}{1-\beta_2^k},\\
w_{k+1}&=w_k-\alpha\frac{\hat m_k}{\sqrt{\hat v_k}+\epsilon}, &&
\end{aligned}$$

with the paper's defaults $\beta_1=0.9$, $\beta_2=0.999$, $\epsilon=10^{-8}$, and $m_0=v_0=0$.

**Where the bias correction comes from.** Unroll the recursion for $m$ from $m_0=0$:

$$m_k=(1-\beta_1)\sum_{i=1}^{k}\beta_1^{\,k-i}g_i.$$

The weights $(1-\beta_1)\beta_1^{k-i}$ add up to $(1-\beta_1)(1+\beta_1+\dots+\beta_1^{k-1})=1-\beta_1^k$, a geometric
sum. So if the gradients have a steady mean $\mathbb E[g_i]=\bar g$, then $\mathbb E[m_k]=(1-\beta_1^k)\bar g$, too small
by the factor $1-\beta_1^k$: at step 1 the average is only 10 percent of the gradient, because it was started at zero.
Dividing by $1-\beta_1^k$ removes the bias exactly. The same argument applies to $v$ with $\beta_2$; because
$\beta_2=0.999$, its bias lasts for thousands of steps, and without the correction $\sqrt{v}$ would be far too small
and the first steps far too large.

A hand check: suppose every gradient is the same number $g=0.001$. Then $m_1=0.1\times0.001=10^{-4}$ and
$\hat m_1=10^{-4}/0.1=0.001$; $v_1=0.001\times10^{-6}=10^{-9}$ and $\hat v_1=10^{-9}/0.001=10^{-6}$, whose square root
is $0.001$. The step is $\alpha\times0.001/0.001=\alpha$. With constant gradients this holds at every step, and with
gradient $1000$ instead of $0.001$ the step is still $\alpha$. This is the key property of Adam: **the step size is
roughly $\alpha$ in each coordinate, whatever the scale of the gradient**. The ratio $\hat m/\sqrt{\hat v}$ is like a
signal-to-noise ratio: near 1 in size when the gradient's sign is consistent, near 0 when it flips randomly, so Adam
automatically slows down where the gradient is mostly noise.

### The race on a badly scaled problem

The second program builds linear regression with three features of scale 1, 10 and 100, and gives each optimiser
five epochs of batch-32 steps, with its learning rate picked as the best of a grid from $10^{-7}$ to $1$:

```python
--8<-- "books/machine-learning/ch05_adaptive_newton.py"
```

Output:

```
1. features scaled 1, 10, 100; 5 epochs of batch-32 updates
   best possible MSE 0.01012; best learning rate from a grid
   optimizer   lr       excess MSE   w
   sgd        3e-05   1.293e+01    [0.028 -0.298 0.0150]
   momentum   1e-05   8.784e+00    [0.089 -0.489 0.0138]
   adagrad    3e-01   2.106e-03    [2.955 -0.498 0.0202]
   rmsprop    1e-01   1.363e-01    [3.125 -0.492 0.0234]
   adam       3e-01   2.155e-03    [2.983 -0.501 0.0196]
   true w                              [3.000 -0.500 0.0200]

2. Newton on f(x) = x - log x from x = 0.5
   step  x                   error 1-x
      0  0.500000000000000   5.000e-01
      1  0.750000000000000   2.500e-01
      2  0.937500000000000   6.250e-02
      3  0.996093750000000   3.906e-03
      4  0.999984741210938   1.526e-05
      5  0.999999999767169   2.328e-10

3. Rosenbrock from (-1.2, 1) until |grad| < 1e-10, Armijo backtracking
   gd      iterations  25115   x = (1.00000000, 1.00000000)
   newton  iterations     22   x = (1.00000000, 1.00000000)
   lbfgs   iterations     43   x = (1.00000000, 1.00000000)

4. gradient descent near the saddle of x^2/2 + y^4/4 - y^2/2, step 0.1
   start y = 0       end (3.1e-92, 0.0000)  steps to reach |y| ~ 1: never
   start y = 1e-12   end (3.1e-92, 1.0000)  steps to reach |y| ~ 1: 318
   start y = 1e-06   end (3.1e-92, 1.0000)  steps to reach |y| ~ 1: 173
   start y = 0.01    end (3.1e-92, 1.0000)  steps to reach |y| ~ 1: 77
   prediction log(1/y0)/log(1.1) for y0 = 1e-6: 145

5. learning rate at step t (base 0.1, 1000 steps, 100 warmup)
   t      step     cosine   warm+cos  1/sqrt
      0  0.1000   0.1000   0.0010   0.1000
     50  0.1000   0.0994   0.0510   0.0140
     99  0.1000   0.0976   0.1000   0.0100
    100  0.1000   0.0976   0.1000   0.0100
    400  0.0100   0.0655   0.0750   0.0050
    500  0.0100   0.0500   0.0587   0.0045
    800  0.0010   0.0095   0.0117   0.0035
    999  0.0010   0.0000   0.0000   0.0032
```

SGD and momentum must use a step small enough for the feature of scale 100 (its curvature is $10^4$ times that of the
first feature), so after five epochs they have barely moved the first weight: 0.028 and 0.089 against a true 3. The
three adaptive methods rescale each coordinate and find all three weights. Standardising the features (Chapter 2)
would have rescued SGD too; adaptive methods do a rough version of that automatically, from the gradients. RMSProp,
without the bias correction or momentum, is noisier at its best step. On a well-scaled convex problem the gap would be
small; this example is built to show the mechanism.

### Adam's known problems

Adam is the default optimiser for training transformers and many other networks, but it is not a solved problem.
Reddi, Kale and Kumar (2018) built simple convex problems on which Adam does not converge, because the moving average
$v$ can forget a rare large gradient and then take too large a step; their fix, AMSGrad, uses the running maximum of
$\hat v$. Wilson et al. (2017) reported image-classification experiments in which well-tuned SGD with momentum
generalised better than adaptive methods. And Loshchilov and Hutter (2019) showed that adding an L2 penalty (Chapter
8) to the loss interacts badly with Adam's rescaling, since the penalty's gradient is divided by $\sqrt{\hat v}$ too;
their **AdamW** subtracts the weight decay $\alpha\lambda w$ separately from the adaptive step, and is what most large
models now use.

## 5.6 Newton's method and second-order ideas

*Level: advanced.*

Gradient descent uses only the slope, so it must guess how far to go. If we also knew the curvature, we could jump to
the bottom of the local bowl. Taylor's theorem to second order says that near $w$,

$$f(w+d)\approx f(w)+\nabla f(w)^\top d+\tfrac12d^\top H(w)\,d,$$

where $H(w)$ is the Hessian. If $H$ is positive definite, this quadratic model has its minimum where its gradient
$\nabla f(w)+Hd$ is zero, at the **Newton step** $d=-H(w)^{-1}\nabla f(w)$. **Newton's method** repeats
$w_{k+1}=w_k-H(w_k)^{-1}\nabla f(w_k)$. On a quadratic loss the model is exact, so Newton lands on the minimum in one
step whatever the condition number. Newton is also **affine invariant**: stretching or rotating the coordinates
changes nothing about its iterates, which is the cure for bad conditioning in its purest form.

### Quadratic convergence

In one dimension the step is $x_{k+1}=x_k-f'(x_k)/f''(x_k)$: Newton's root-finding method applied to $f'$. Write
$x^*$ for the minimum, so $f'(x^*)=0$, and $e_k=x_k-x^*$. Taylor's theorem with remainder gives
$0=f'(x^*)=f'(x_k)-f''(x_k)e_k+\tfrac12f'''(\xi)e_k^2$ for some $\xi$ between $x_k$ and $x^*$. Divide by $f''(x_k)$
and rearrange:

$$e_{k+1}=x_k-\frac{f'(x_k)}{f''(x_k)}-x^*=e_k-\frac{f'(x_k)}{f''(x_k)}=\frac{f'''(\xi)}{2f''(x_k)}\,e_k^2.$$

So if $f''\ge m>0$ and $|f'''|\le M$ near $x^*$, then $|e_{k+1}|\le\frac M{2m}e_k^2$: the error is *squared* each step,
which means the number of correct digits roughly doubles. This is **quadratic convergence**. It is local: it holds
once $|e_k|<2m/M$; far away, the quadratic model can be a poor guide. The same theorem holds in $d$ dimensions with a
Lipschitz Hessian (Nocedal and Wright, theorem 3.5).

A clean example is $f(x)=x-\ln x$, minimised at $x=1$. Here $f'(x)=1-1/x$ and $f''(x)=1/x^2$, so the Newton step is
$x-(1-1/x)x^2=2x-x^2$, and $1-(2x-x^2)=(1-x)^2$: the error is squared *exactly*. From $x_0=0.5$ the errors are
$0.5, 0.25, 0.0625, 0.0039, 1.5\times10^{-5}, 2.3\times10^{-10}$, as the program prints. Five steps give ten correct
digits. Gradient descent with a fixed step on the same function gains a roughly fixed number of digits per step.

### Making Newton safe, and its cost

Two things go wrong. Far from the minimum, or on a non-convex function, $H$ may not be positive definite, and the
Newton step can point uphill or to a saddle. And the full step may overshoot. Practical Newton codes check that the
step goes downhill, fall back to the gradient (or add a multiple of the identity to $H$) when it does not, and choose
the step length by a **line search**: start with $t=1$ and halve it until the **Armijo condition**
$f(w+td)\le f(w)+c\,t\,\nabla f(w)^\top d$ holds with a small $c$ such as $10^{-4}$, which demands at least a small
fraction of the decrease the slope promises. Our program does exactly that.

The third block is the standard test, Rosenbrock's function $f(x,y)=(1-x)^2+100(y-x^2)^2$ (Rosenbrock 1960), whose
minimum $(1,1)$ lies at the bottom of a long, curved, narrow valley. From $(-1.2,1)$, to a gradient norm below
$10^{-10}$: gradient descent with line search needs 25115 iterations; Newton needs 22.

The price is the Hessian. With $d$ parameters it has $d^2$ entries, and solving $Hd=-g$ costs about $d^3/3$
operations by Cholesky factorisation. For logistic regression with 100 features that is nothing, and Newton (under
the name **iteratively reweighted least squares**, Chapter 6) is the standard method. For a network with $10^8$
weights, the Hessian alone would need $10^{16}$ numbers. That is why deep learning uses first-order methods.

### Quasi-Newton methods and L-BFGS

Can we get Newton's speed without the Hessian? **Quasi-Newton** methods build an approximation of $H^{-1}$ from the
gradients we compute anyway. After a step $s_k=w_{k+1}-w_k$ the gradient changed by $y_k=\nabla f(w_{k+1})-\nabla
f(w_k)$, and for a quadratic $y_k=Hs_k$ exactly. So we ask the new approximation $B_{k+1}\approx H^{-1}$ to satisfy
the **secant condition** $B_{k+1}y_k=s_k$, and to change as little as possible from $B_k$. The answer found
independently by Broyden, Fletcher, Goldfarb and Shanno in 1970 is the **BFGS** update:

$$B_{k+1}=\bigl(I-\rho_ks_ky_k^\top\bigr)B_k\bigl(I-\rho_ky_ks_k^\top\bigr)+\rho_ks_ks_k^\top,\qquad\rho_k=\frac1{y_k^\top s_k}.$$

It keeps $B$ positive definite as long as $y_k^\top s_k>0$, which a convex function or a Wolfe line search guarantees,
and it converges superlinearly (faster than any constant factor per step) near a minimum. It still stores a
$d\times d$ matrix.

**L-BFGS** (limited-memory BFGS; Nocedal 1980, Liu and Nocedal 1989) never forms $B$. It keeps only the last $m$
pairs $(s_i,y_i)$, typically $m$ between 5 and 20, and computes $B\,g$ directly by the **two-loop recursion**: a
backward loop over the stored pairs projecting $g$, a scaling by $\gamma=s^\top y/y^\top y$ (an estimate of
$1/\text{curvature}$), and a forward loop adding the corrections back. The cost is about $4md$ operations per step and
$2md$ numbers of memory, linear in $d$. The program implements it in a dozen lines with $m=5$, skipping any pair with
$s^\top y\le0$ to stay safe, and solves Rosenbrock in 43 iterations, without ever forming a $2\times2$ Hessian. L-BFGS
is the default for smooth, deterministic problems of moderate to large size: logistic regression with many features,
conditional random fields, fitting physical models. It works poorly with noisy mini-batch gradients, because the
differences $y_k$ are then mostly noise.

Between first and second order sit methods that use some curvature cheaply: Gauss-Newton and Levenberg-Marquardt for
least-squares problems; natural gradient (Amari 1998), which preconditions by the Fisher information; K-FAC (Martens
and Grosse 2015), a block approximation of it for neural networks; and Shampoo (Gupta, Koren and Singer 2018). They
are research and specialist tools, not yet defaults.

## 5.7 Learning-rate schedules, warmup and non-convex landscapes

### Schedules

Theorem 5.4 says a constant step leaves SGD on a noise floor of size proportional to $\alpha$. Large steps make fast
early progress; small steps are needed at the end. A **learning-rate schedule** gives the step as a function of the
step number $t$. Common ones, with base rate $\alpha_0$ and $T$ total steps:

- **Step decay**: multiply by 0.1 at fixed points, for example at 40 and 80 percent of training. Long used for image
  networks.
- **Inverse square root**: $\alpha_0/\sqrt{1+t}$, the classical choice for convex SGD, and (after warmup) the schedule
  of the original transformer paper (Vaswani et al. 2017).
- **Cosine**: $\alpha_t=\tfrac12\alpha_0\bigl(1+\cos(\pi t/T)\bigr)$, smooth from $\alpha_0$ to 0 (Loshchilov and
  Hutter 2017, who also proposed restarting it periodically).
- **Linear warmup**: start very small and rise linearly to $\alpha_0$ over the first few hundred or thousand steps,
  then follow one of the schedules above.

<figure class="mars-fig" markdown="0">
<svg viewBox="0 0 680 300" role="img" aria-label="Plot of learning rate against training step for three schedules over 1000 steps. Step decay is flat at 0.1, drops to 0.01 at step 400 and to 0.001 at step 800. Cosine falls smoothly from 0.1 to 0. Warmup plus cosine rises linearly from near 0 to 0.1 over the first 100 steps and then follows a cosine down to 0.">
  <g stroke="currentColor" stroke-width="1.2" fill="none">
    <line x1="60" y1="250" x2="630" y2="250"/>
    <line x1="60" y1="250" x2="60" y2="40"/>
    <line x1="56" y1="50" x2="60" y2="50"/>
    <line x1="56" y1="150" x2="60" y2="150"/>
    <line x1="284" y1="250" x2="284" y2="254"/>
    <line x1="508" y1="250" x2="508" y2="254"/>
    <line x1="116" y1="250" x2="116" y2="254"/>
  </g>
  <g font-size="12" fill="currentColor">
    <text x="52" y="54" text-anchor="end">0.1</text>
    <text x="52" y="154" text-anchor="end">0.05</text>
    <text x="52" y="254" text-anchor="end">0</text>
    <text x="60" y="268" text-anchor="middle">0</text>
    <text x="116" y="268" text-anchor="middle">100</text>
    <text x="284" y="268" text-anchor="middle">400</text>
    <text x="508" y="268" text-anchor="middle">800</text>
    <text x="619" y="268" text-anchor="middle">1000</text>
    <text x="340" y="290" text-anchor="middle">training step t</text>
    <text x="20" y="30">learning rate</text>
  </g>
  <polyline points="60,50 284,50 284,230 508,230 508,248 619,248" fill="none" stroke="#eea66f" stroke-width="2.5"/>
  <polyline points="60,50 71,50 82,51 94,52 105,53 116,55 127,57 138,60 150,62 161,66 172,69 183,73 194,77 206,82 217,86 228,91 239,96 250,102 262,107 273,113 284,119 295,125 306,131 318,137 329,144 340,150 351,156 362,163 374,169 385,175 396,181 407,187 418,193 430,198 441,204 452,209 463,214 474,218 486,223 497,227 508,231 519,234 530,238 542,240 553,243 564,245 575,247 586,248 598,249 609,250 619,250" fill="none" stroke="#9cc9ea" stroke-width="2.5"/>
  <polyline points="60,248 71,208 82,168 94,128 105,88 116,50 127,50 138,51 150,52 161,54 172,56 183,59 194,62 206,65 217,69 228,73 239,78 250,83 262,88 273,94 284,100 295,106 306,113 318,119 329,126 340,133 351,140 362,147 374,153 385,160 396,167 407,174 418,181 430,187 441,194 452,200 463,206 474,212 486,217 497,222 508,227 519,231 530,235 542,238 553,241 564,244 575,246 586,248 598,249 609,250 619,250" fill="none" stroke="#7ccf9a" stroke-width="2.5"/>
  <g font-size="13" fill="currentColor">
    <text x="400" y="62">orange: step decay</text>
    <text x="400" y="80">blue: cosine</text>
    <text x="400" y="98">green: warmup then cosine</text>
  </g>
</svg>
<figcaption>Figure 5.3. Three schedules for 1000 steps with base rate 0.1, computed by the fifth block of the program. Warmup spends the first 100 steps climbing from 0.001 to 0.1.</figcaption>
</figure>

Why warm up? At the start the weights are random, the gradients can be large and erratic, and Adam's $\hat v$ is
estimated from very few gradients. A full-size step then can throw the network into a region it never recovers from.
Goyal et al. (2017) used five epochs of warmup to train an image network with batches of 8192, together with the
**linear scaling rule** (multiply the learning rate by $k$ when the batch is $k$ times larger, which keeps the noise
per epoch roughly constant). Transformers are usually trained with warmup; Liu et al. (2020) traced part of the
need to the high variance of Adam's early second-moment estimate. Schedules are partly theory and partly craft:
Chapter 16 shows how to pick a base rate with a learning-rate range test.

### Non-convex landscapes

*Level: advanced.*

A neural network's loss is not convex. Swapping two hidden units gives the same function with different weights, so
minima come in large symmetric families, and the average of two minima is generally not one. Theorem 5.1 no longer
applies. What can we still say?

**Stationary points.** The descent lemma did not use convexity. Adding it up over $k$ steps of size $1/L$ gives
$\tfrac1{2L}\sum_{i<k}\lVert\nabla f(w_i)\rVert^2\le f(w_0)-f_{\inf}$, where $f_{\inf}$ is a lower bound on the loss, so
the smallest gradient seen satisfies $\min_{i<k}\lVert\nabla f(w_i)\rVert\le\sqrt{2L(f(w_0)-f_{\inf})/k}$. Gradient
descent always finds *approximately flat ground* at rate $1/\sqrt k$. Flat ground need not be a minimum.

**Saddle points.** At a critical point, the Hessian's eigenvalues tell the type: all positive, a local minimum; all
negative, a maximum; mixed signs, a saddle. A **strict saddle** has at least one strictly negative eigenvalue, a
direction that goes downhill. In high dimensions saddles are thought to be far more common than poor local minima:
Dauphin et al. (2014) argued this from random-matrix models and measured it in small networks, finding that critical
points with high loss tended to be saddles. For a random symmetric matrix the chance that *all* $d$ eigenvalues are
positive is tiny, so "flat and every direction goes up" becomes rare unless the loss is already low.

Does gradient descent get stuck on saddles? The fourth block of the program shows the mechanism on
$f(x,y)=\tfrac12x^2+\tfrac14y^4-\tfrac12y^2$, which has a saddle at $(0,0)$ (Hessian eigenvalues $1$ and $-1$) and minima
at $(0,\pm1)$. Near the saddle, gradient descent with step $0.1$ multiplies $y$ by $1+0.1=1.1$ each step: the
negative curvature *repels*. Started exactly on the line $y=0$, it converges to the saddle and stays there forever.
Started at $y=10^{-6}$, the distance grows like $10^{-6}\times1.1^k$, which reaches order 1 after about
$\ln(10^6)/\ln1.1\approx145$ steps, and the walker reaches the minimum within $10^{-3}$ at step 173. Starting a
million times closer, at $y=10^{-12}$, only doubles the escape time to 318 steps, because escape time grows like the
logarithm of $1/y_0$.

Two theorems make this precise. Lee et al. (2016) proved that for a smooth function with step below $1/L$, the set of
starting points from which gradient descent converges to a strict saddle has measure zero: a random start almost surely
avoids them. That says nothing about speed, and Du et al. (2017) built functions where plain gradient descent takes
exponential time to pass a chain of saddles. Jin et al. (2017) proved that adding a small random perturbation when the
gradient is small escapes every strict saddle and reaches an approximate local minimum in a number of steps only
polylogarithmically worse than the time to find a flat point. The noise of SGD plays a similar role in practice.

**Are local minima bad?** For some non-convex problems the answer is proved to be no: for example, all local minima
of certain matrix-completion and phase-retrieval losses are global (Ge, Lee and Ma 2016 and others). For deep
networks there is no such theorem in general. Experiments find that large networks reach near-zero training loss from
many random starts (Zhang et al. 2017 fitted even random labels), and the open question is less "can we reach the
bottom?" than "which of the many bottoms generalise?" Chapter 21 returns to this. Another surprise is that training
with large steps often does not satisfy the $\alpha<2/L$ rule at all: Cohen et al. (2021) observed that the sharpness
(largest Hessian eigenvalue) rises during training until it hovers near $2/\alpha$, the "edge of stability", while the
loss keeps falling non-monotonically. The classical theory above does not explain this, and it is an active research
topic.

**In practice.** Libraries implement every method in this chapter: `torch.optim` in PyTorch has `SGD` (with momentum
and Nesterov), `Adagrad`, `RMSprop`, `Adam`, `AdamW` and `LBFGS`, plus schedulers; `scipy.optimize.minimize` has
BFGS, L-BFGS-B and Newton-type methods; scikit-learn's logistic regression uses L-BFGS by default. Their update rules
are the ones written above.

## Check yourself

??? question "1. Is $f(w)=\max(0,1-w)$ (the hinge, Chapter 10) convex? Is $f(w)=w^3$? Use the definition or the second-order test."

    The hinge is the maximum of two linear functions, $0$ and $1-w$. Each linear function is convex, and the maximum
    of convex functions is convex: for each piece $f_j$,
    $f_j(tx+(1-t)y)\le tf_j(x)+(1-t)f_j(y)\le t\max_jf_j(x)+(1-t)\max_jf_j(y)$, and taking the max over $j$ on the left
    keeps the inequality. So yes. For $w^3$, $f''(w)=6w$ is negative for $w<0$, so it is not convex; a failing chord:
    $x=-2$, $y=0$, $t=\tfrac12$ gives $f(-1)=-1$ against the chord value $\tfrac12(-8)+\tfrac12\cdot0=-4$, and
    $-1>-4$.

??? question "2. For $f(w)=\tfrac12(4w_1^2+w_2^2)$, give $L$, $\mu$ and $\kappa$. What step sizes make gradient descent converge, and what is the contraction factor with $\alpha=1/L$?"

    The Hessian is $\mathrm{diag}(4,1)$, so $L=4$, $\mu=1$, $\kappa=4$. Each coordinate is multiplied by $1-\alpha\lambda$;
    convergence needs $|1-4\alpha|<1$ and $|1-\alpha|<1$, that is $0<\alpha<1/2=2/L$. With $\alpha=1/4$ the factors are
    $0$ (the steep coordinate is solved in one step) and $3/4=1-1/\kappa$, so the error shrinks by $3/4$ per step.
    The best fixed step is $\alpha=2/(L+\mu)=0.4$, with factors $-0.6$ and $0.6$, so $0.6=(\kappa-1)/(\kappa+1)$.

??? question "3. Using Theorem 5.3, how many steps of gradient descent with $\alpha=1/L$ guarantee $f(w_k)-f^*\le10^{-3}$ when $L=2$ and $R=10$?"

    We need $LR^2/(2k)\le10^{-3}$, so $k\ge LR^2/(2\times10^{-3})=2\times100/0.002=100\,000$. The guarantee is
    worst-case; on a strongly convex problem far fewer steps are needed, as the program's logistic example shows.

??? question "4. In Theorem 5.4, why must we report the average iterate rather than the last one, and what is the best constant step if $R=1$, $G=10$ and we can afford $K=10\,000$ steps? What error bound does it give?"

    The proof bounds the sum of the errors $f(w_k)-f^*$, not each one, because single SGD steps can go uphill; Jensen's
    inequality turns the sum into a bound on $f(\bar w)$. (Bounds for the last iterate exist, with an extra logarithmic
    factor.) The best step is $\alpha=R/(G\sqrt K)=1/(10\times100)=0.001$, and the bound is $RG/\sqrt K=10/100=0.1$.

??? question "5. Show that with constant gradient $g$, the heavy-ball velocity $v_{k+1}=\beta v_k+g$ from $v_0=0$ tends to $g/(1-\beta)$. What is the effective step for $\beta=0.9$ and $\beta=0.99$?"

    Unrolling, $v_k=g(1+\beta+\dots+\beta^{k-1})=g\,(1-\beta^k)/(1-\beta)\to g/(1-\beta)$ since $0\le\beta<1$. The
    update $\alpha v$ approaches $\alpha g/(1-\beta)$: ten times the plain step for $\beta=0.9$, a hundred times for
    $\beta=0.99$. This is why the learning rate usually has to be lowered when momentum is raised.

??? question "6. Write Adam's first two steps by hand for one parameter with gradients $g_1=1$ and $g_2=-1$, $\alpha=0.1$, defaults otherwise (ignore $\epsilon$)."

    Step 1: $m_1=0.1$, $\hat m_1=0.1/0.1=1$; $v_1=0.001$, $\hat v_1=0.001/0.001=1$; step $-0.1\times1/1=-0.1$.
    Step 2: $m_2=0.9\times0.1+0.1\times(-1)=-0.01$, $\hat m_2=-0.01/(1-0.81)=-0.0526$;
    $v_2=0.999\times0.001+0.001\times1=0.001999$, $\hat v_2=0.001999/(1-0.998001)=0.001999/0.001999=1$; step
    $-0.1\times(-0.0526)/1=+0.00526$. The sign flip almost cancels in $\hat m$, so the second step is tiny: Adam slows
    down when the gradient's sign is inconsistent.

??? question "7. Apply Newton's method to $f(x)=e^x-2x$ from $x_0=0$. Where is the minimum, and how fast does the error shrink?"

    $f'(x)=e^x-2$, $f''(x)=e^x$, minimum at $x^*=\ln2\approx0.693147$. Newton: $x\leftarrow x-(e^x-2)/e^x=x-1+2e^{-x}$.
    $x_1=0-1+2=1$; $x_2=1-1+2e^{-1}=0.735759$; $x_3=0.735759-1+2e^{-0.735759}=0.694042$; $x_4=0.6931476$ (error about
    $4\times10^{-7}$). The errors $0.307, 0.0426, 0.000895, 4.0\times10^{-7}$ are each roughly half the square of the
    previous one, which matches $f'''/(2f'')=1/2$ at the minimum.

??? question "8. Verify the secant condition $B_{k+1}y_k=s_k$ for the BFGS update."

    With $\rho=1/(y^\top s)$: $(I-\rho y s^\top)y=y-\rho y(s^\top y)=y-y=0$. So the first term of $B_{k+1}y$ is
    $(I-\rho sy^\top)B_k\cdot0=0$, and the second is $\rho s(s^\top y)=s$. Hence $B_{k+1}y=s$.

??? question "9. Write the code: gradient descent with backtracking (Armijo) line search for any $f$ and gradient, and use it on $f(w)=\lVert Aw-b\rVert^2$ for a random $4\times3$ matrix."

    ```python
    import numpy as np

    def gd_backtracking(f, grad, w, iters=2000, c=1e-4):
        for _ in range(iters):
            g = grad(w)
            t = 1.0
            while f(w - t * g) > f(w) - c * t * (g @ g):
                t *= 0.5
            w = w - t * g
        return w

    rng = np.random.default_rng(0)
    A, b = rng.normal(size=(4, 3)), rng.normal(size=4)
    f = lambda w: np.sum((A @ w - b) ** 2)
    grad = lambda w: 2 * A.T @ (A @ w - b)
    w = gd_backtracking(f, grad, np.zeros(3))
    print(np.allclose(w, np.linalg.lstsq(A, b, rcond=None)[0]))   # True
    ```

    (With 200 iterations this example is not yet converged to `allclose` precision: the condition number of $A^\top A$
    is about 44, so gradient descent needs a few hundred steps.) The condition $f(w-tg)\le f(w)-c\,t\lVert g\rVert^2$ is Armijo's with $d=-g$. By the descent lemma it holds as soon
    as $t\le 2(1-c)/L$, so the loop always ends and the accepted step is at least about $1/L$.

??? question "10. Write the code: RMSProp without bias correction starts with $v_1=(1-\rho)g_1^2$. How large is its first step compared with Adam's, for $\rho=0.999$?"

    The first step is $\alpha g_1/\sqrt{0.001\,g_1^2}=\alpha/\sqrt{0.001}\approx31.6\,\alpha$ in size, against exactly
    $\alpha$ for Adam. A check in code:

    ```python
    import numpy as np
    alpha, rho, g = 0.01, 0.999, 5.0
    v = (1 - rho) * g * g
    print(alpha * g / np.sqrt(v), alpha)   # 0.316... versus 0.01
    ```

    This early overshoot is exactly what Adam's correction $\hat v=v/(1-\beta_2^k)$ removes.

??? question "11. (Advanced) For gradient descent on a non-convex $L$-smooth $f$ bounded below by $f_{\inf}$, prove $\min_{i<k}\lVert\nabla f(w_i)\rVert^2\le2L(f(w_0)-f_{\inf})/k$ with step $1/L$."

    The descent lemma gives $f(w_{i+1})\le f(w_i)-\lVert\nabla f(w_i)\rVert^2/(2L)$ for each $i$. Adding for
    $i=0,\dots,k-1$ telescopes: $\tfrac1{2L}\sum_{i<k}\lVert\nabla f(w_i)\rVert^2\le f(w_0)-f(w_k)\le f(w_0)-f_{\inf}$. The
    minimum of $k$ numbers is at most their average, so
    $\min_i\lVert\nabla f(w_i)\rVert^2\le2L(f(w_0)-f_{\inf})/k$. No convexity was used, but the conclusion is only about
    small gradients, not about minima.

## What you learned

- Training is minimising a loss; on a **convex** loss every local minimum is global (Theorem 5.1), so any method
  that reaches flat ground has succeeded.
- With step $1/L$ on an $L$-smooth convex function, gradient descent satisfies $f(w_k)-f^*\le LR^2/(2k)$, proved by
  the descent lemma and a telescoping sum; on strongly convex functions the error shrinks by $1-1/\kappa$ per step.
- **SGD** uses one or a few examples per step: unbiased but noisy. A constant step reaches a noise floor proportional
  to the step; decaying steps or bigger batches lower it. Per unit of work, SGD wins on large data.
- **Momentum** and **Nesterov** accelerate: on badly conditioned problems they need about $\sqrt\kappa$ instead of
  $\kappa$ steps per digit of accuracy, and Nesterov's $1/k^2$ rate is optimal for first-order methods.
- **AdaGrad**, **RMSProp** and **Adam** scale each parameter's step by its recent gradient size; Adam's bias
  correction undoes the zero start of its moving averages, and its steps are about $\alpha$ whatever the gradient's
  scale.
- **Newton's method** converges quadratically near a minimum but costs $O(d^3)$ per step; **L-BFGS** approximates it
  from the last few gradient differences at $O(md)$ cost.
- **Schedules** and **warmup** trade early speed for late precision; on non-convex losses gradient descent almost
  surely avoids strict saddles, perturbations escape them quickly, and much about deep-learning landscapes is still
  open.

**Next:** [Chapter 6](06-Classification-and-Logistic-Regression.md) turns from predicting numbers to predicting
classes, and trains logistic regression with the tools of this chapter.

## Further reading

- S. Boyd and L. Vandenberghe, *Convex Optimization*, 2004: chapters 2 and 3 (convex sets and functions) and 9
  (gradient and Newton methods). Free online from the authors.
- Y. Nesterov, *Introductory Lectures on Convex Optimization: A Basic Course*, 2004: chapter 2 (rates, lower bounds,
  the accelerated method).
- J. Nocedal and S. J. Wright, *Numerical Optimization*, 2nd ed., 2006: chapters 3 (line search), 6 (BFGS) and 7
  (L-BFGS).
- S. Bubeck, "Convex Optimization: Algorithms and Complexity", *Foundations and Trends in Machine Learning* 8(3-4),
  2015.
- L. Bottou, F. E. Curtis and J. Nocedal, "Optimization Methods for Large-Scale Machine Learning", *SIAM Review* 60(2),
  2018.
- I. Goodfellow, Y. Bengio and A. Courville, *Deep Learning*, 2016: chapter 8.
- H. Robbins and S. Monro, "A Stochastic Approximation Method", *Annals of Mathematical Statistics* 22(3), 1951.
- B. T. Polyak, "Some methods of speeding up the convergence of iteration methods", *USSR Computational Mathematics
  and Mathematical Physics* 4(5), 1964.
- Y. Nesterov, "A method for solving the convex programming problem with convergence rate O(1/k²)", *Soviet
  Mathematics Doklady* 27, 1983.
- J. Duchi, E. Hazan and Y. Singer, "Adaptive Subgradient Methods for Online Learning and Stochastic Optimization",
  *JMLR* 12, 2011.
- D. P. Kingma and J. Ba, "Adam: A Method for Stochastic Optimization", arXiv 1412.6980, 2014 (ICLR 2015).
- S. J. Reddi, S. Kale and S. Kumar, "On the Convergence of Adam and Beyond", ICLR 2018.
- I. Loshchilov and F. Hutter, "SGDR: Stochastic Gradient Descent with Warm Restarts", ICLR 2017; "Decoupled Weight
  Decay Regularization", ICLR 2019.
- D. C. Liu and J. Nocedal, "On the limited memory BFGS method for large scale optimization", *Mathematical
  Programming* 45, 1989.
- P. Goyal et al., "Accurate, Large Minibatch SGD: Training ImageNet in 1 Hour", arXiv 1706.02677, 2017.
- Y. Dauphin et al., "Identifying and attacking the saddle point problem in high-dimensional non-convex
  optimization", NeurIPS 2014; J. D. Lee et al., "Gradient Descent Converges to Minimizers", COLT 2016; C. Jin et
  al., "How to Escape Saddle Points Efficiently", ICML 2017.
- J. Cohen et al., "Gradient Descent on Neural Networks Typically Occurs at the Edge of Stability", ICLR 2021.
- On this site: [Chapter 4](04-Linear-Regression.md) (gradient descent on least squares),
  [Chapter 16](16-Training-Deep-Networks.md) (optimisers in practice), the
  [Algorithms book](../algorithms/index.md), and the [calculus](https://math.akadian.ca/books/calculus/) and
  [linear algebra](https://math.akadian.ca/books/linear-algebra/) books.
