# 15. Neural networks and backpropagation

*Every model in Parts II and III was either linear in its features or built from hand-chosen pieces: features we
designed, kernels we picked, splits on single variables. A neural network learns its own features. It stacks simple
units, each a weighted sum followed by a bend, and adjusts millions of weights so that the stack computes what we
want. Two questions decide whether this can work: can such a stack represent the functions we need, and can we
find good weights? This chapter answers both. You will see why one layer cannot compute XOR and two can, derive
backpropagation (the algorithm that gives every weight its gradient at about the cost of evaluating the network
once), build a small automatic-differentiation engine from scratch and train a network on it, meet the universal
approximation theorem, and train a network that separates two interleaved spirals.*

!!! abstract "In this chapter"
    **You will learn:**

    - why a single neuron can only draw straight boundaries, proved on XOR, and how a hidden layer fixes it
    - the common activation functions (sigmoid, tanh, ReLU), their derivatives, and why some non-linearity is essential
    - the forward pass of a multilayer network as a few matrix products, with every shape explained
    - backpropagation, derived from the chain rule, and why it costs only a small constant times the forward pass
    - computational graphs and reverse-mode automatic differentiation, built from scratch in about 100 lines
    - what the universal approximation theorem says, the idea of its proof, and what it does not say
    - how to train a small network on a non-linear problem and look at what it learned

    **You need:** [Chapter 3](03-The-Math-Toolkit.md) (matrices, derivatives, the chain rule, checking a gradient
    numerically), [Chapter 5](05-Optimization.md) (gradient descent, Adam) and
    [Chapter 6](06-Classification-and-Logistic-Regression.md) (the perceptron, logistic regression and the
    cross-entropy loss). The calculus book at [https://math.akadian.ca/books/](https://math.akadian.ca/books/) covers
    the chain rule.

    **Levels:** 15.1 to 15.3 are beginner to intermediate; 15.4 and 15.5 are intermediate; 15.6 is advanced;
    15.7 is intermediate.

## 15.1 From the perceptron to layers: why XOR needs a hidden layer

### One neuron

Recall the perceptron of [Chapter 6](06-Classification-and-Logistic-Regression.md). It takes an input vector
$x \in \mathbb{R}^p$, forms a weighted sum plus a **bias** (a constant offset), $a = w^\top x + b$, and outputs 1 if
$a > 0$ and 0 otherwise. Logistic regression is the same unit with a smooth output, the sigmoid
$\sigma(a) = 1/(1 + e^{-a})$, read as a probability. Both are examples of an **artificial neuron**: a weighted sum
followed by a fixed function, the **activation function**. The name comes from a loose analogy with nerve cells,
which add up signals from other cells and fire when the total is high enough. Warren McCulloch and Walter Pitts
described such threshold units in 1943 as a model of logic in the brain, and Frank Rosenblatt's perceptron (1958)
gave them a learning rule. The analogy stops there: nothing in this chapter depends on biology.

Whatever its weights, one neuron splits the input space with the **hyperplane** $w^\top x + b = 0$: a line in 2-D,
a plane in 3-D. Inputs on one side give output 1, on the other side 0 (or a probability above or below one half).
So a single neuron can only learn problems that are **linearly separable**.

### XOR

The **exclusive or** of two bits is 1 when exactly one of them is 1:

| $x_1$ | $x_2$ | XOR |
|---|---|---|
| 0 | 0 | 0 |
| 0 | 1 | 1 |
| 1 | 0 | 1 |
| 1 | 1 | 0 |

**Claim.** No single threshold neuron computes XOR.

*Proof.* Suppose $w_1, w_2, b$ worked, with output 1 exactly when $w_1x_1 + w_2x_2 + b > 0$. The four rows require

$$
b \le 0, \qquad w_2 + b > 0, \qquad w_1 + b > 0, \qquad w_1 + w_2 + b \le 0 .
$$

Add the middle two: $w_1 + w_2 + 2b > 0$. Subtract the first (which says $-b \ge 0$): $w_1 + w_2 + b > -b \ge 0$,
so $w_1 + w_2 + b > 0$, contradicting the last. $\square$

Geometrically: the two points labelled 1, $(0,1)$ and $(1,0)$, sit on opposite corners of the unit square, and the two
labelled 0 on the other two corners. Any line that has both 1-corners on one side has the segment between them on
that side too, and that segment crosses the segment between the 0-corners at the centre $(0.5, 0.5)$; so one
0-corner must lie on the same side as well.

Marvin Minsky and Seymour Papert's book *Perceptrons* (1969) analysed such limits of single-layer networks
rigorously, for problems much harder than XOR (for example, deciding whether a figure is connected). The book is
often blamed for a drop in funding for neural network research in the 1970s; how much it caused, as opposed to
reflected, is debated by historians. What is not debated is the mathematics: a single layer is limited, and the
authors knew that multilayer networks were more powerful but saw no way to train them.

### Adding a hidden layer

XOR is "OR but not AND". Each of OR and AND is linearly separable, so each can be one neuron, and a third neuron can
combine them:

- $h_1 = \mathrm{step}(x_1 + x_2 - 0.5)$ is 1 if at least one input is 1 (OR);
- $h_2 = \mathrm{step}(x_1 + x_2 - 1.5)$ is 1 only if both are (AND);
- $\text{out} = \mathrm{step}(h_1 - h_2 - 0.5)$ is 1 when $h_1 = 1$ and $h_2 = 0$.

Check $x = (1, 0)$ by hand: $x_1 + x_2 = 1$, so $h_1 = \mathrm{step}(0.5) = 1$, $h_2 = \mathrm{step}(-0.5) = 0$, and
$\text{out} = \mathrm{step}(1 - 0 - 0.5) = 1$. The neurons $h_1, h_2$ form a **hidden layer**: they are neither input
nor output, and their values are not given by the data. What they do is **change the representation**. In the
coordinates $(h_1, h_2)$ the four inputs become $(0,0)$, $(1,0)$, $(1,0)$ and $(1,1)$, and now the 1-labelled points
(both at $(1,0)$) can be cut off from the others by a single line. That is the central idea of neural networks:
**hidden layers learn new features in which the problem becomes easy for the last layer.**

<figure class="mars-fig" markdown="0">
<svg viewBox="0 0 640 230" role="img" aria-label="Left: the XOR problem on the unit square, with the two class-1 corners on one diagonal and the two class-0 corners on the other; no single line separates them. Right: the network with inputs x1 and x2, hidden units h1 for OR and h2 for AND, and an output unit computing h1 and not h2.">
  <rect x="50" y="40" width="140" height="140" fill="none" stroke="currentColor" stroke-width="1" stroke-dasharray="4 4"/>
  <line x1="30" y1="140" x2="140" y2="20" stroke="currentColor" stroke-width="1" stroke-opacity="0.5"/>
  <line x1="100" y1="200" x2="210" y2="80" stroke="currentColor" stroke-width="1" stroke-opacity="0.5"/>
  <g stroke="currentColor" stroke-width="0.8">
    <circle cx="50" cy="180" r="9" fill="#9cc9ea"/>
    <circle cx="190" cy="40" r="9" fill="#9cc9ea"/>
    <circle cx="50" cy="40" r="9" fill="#eea66f"/>
    <circle cx="190" cy="180" r="9" fill="#eea66f"/>
  </g>
  <g fill="currentColor" font-size="12" text-anchor="middle">
    <text x="50" y="202">(0,0): 0</text>
    <text x="190" y="202">(1,0): 1</text>
    <text x="50" y="26">(0,1): 1</text>
    <text x="210" y="26">(1,1): 0</text>
    <text x="120" y="222">two lines are needed, not one</text>
  </g>
  <g stroke="currentColor" stroke-width="1.2">
    <line x1="320" y1="70" x2="440" y2="70"/>
    <line x1="320" y1="70" x2="440" y2="160"/>
    <line x1="320" y1="160" x2="440" y2="70"/>
    <line x1="320" y1="160" x2="440" y2="160"/>
    <line x1="440" y1="70" x2="570" y2="115"/>
    <line x1="440" y1="160" x2="570" y2="115"/>
  </g>
  <g stroke="currentColor" stroke-width="0.8">
    <circle cx="320" cy="70" r="20" fill="#9cc9ea"/>
    <circle cx="320" cy="160" r="20" fill="#9cc9ea"/>
    <circle cx="440" cy="70" r="20" fill="#7ccf9a"/>
    <circle cx="440" cy="160" r="20" fill="#7ccf9a"/>
    <circle cx="570" cy="115" r="20" fill="#eea66f"/>
  </g>
  <g fill="currentColor" font-size="13" text-anchor="middle">
    <text x="320" y="75">x1</text><text x="320" y="165">x2</text>
    <text x="440" y="75">h1</text><text x="440" y="165">h2</text>
    <text x="570" y="120">out</text>
    <text x="440" y="40">OR: bias -0.5</text>
    <text x="440" y="200">AND: bias -1.5</text>
    <text x="570" y="160">+1, -1; bias -0.5</text>
    <text x="380" y="222">all input weights are 1</text>
  </g>
</svg>
<figcaption>XOR. No single line separates the orange corners from the blue ones (left). A hidden layer computing
OR and AND, followed by "OR and not AND", solves it (right).</figcaption>
</figure>

The first program checks all of this: the perceptron learning rule still makes 4 mistakes on its 100th pass over
the XOR table (it never converges, as Novikoff's theorem of Chapter 6 only promises convergence for separable data),
while the hand-made network is correct on all four inputs. It then trains a network of the same 2-2-1 shape from
random weights, which we come back to in 15.4.

<figure class="play" data-play="xorlines"><span class="ai-tag">AI-created</span><figcaption><b>Try it.</b> Turn and shift one line: XOR's corners can never all be split by it. Then let two hidden units draw two lines.</figcaption></figure>

## 15.2 Activation functions and why non-linearity matters

Our hand-made XOR network used the step function. Step functions have derivative zero everywhere (except at the jump,
where it does not exist), so gradient descent gets no signal from them. Networks that learn by gradients use smooth
or piecewise-linear activations instead. The three you must know:

- **Sigmoid** $\sigma(a) = \dfrac{1}{1 + e^{-a}}$, from $\mathbb{R}$ to $(0, 1)$. Derivative
  $\sigma'(a) = \sigma(a)(1 - \sigma(a))$, at most $1/4$ (at $a = 0$). (*Derivation:*
  $\sigma' = e^{-a}/(1+e^{-a})^2 = \sigma \cdot \frac{e^{-a}}{1+e^{-a}} = \sigma(1-\sigma)$.)
- **Hyperbolic tangent** $\tanh(a) = \dfrac{e^a - e^{-a}}{e^a + e^{-a}} = 2\sigma(2a) - 1$, from $\mathbb{R}$ to
  $(-1, 1)$. Derivative $1 - \tanh^2(a)$, at most 1. It is a shifted, stretched sigmoid that is centred at zero,
  which usually makes training easier than with the sigmoid.
- **Rectified linear unit** (ReLU) $\mathrm{relu}(a) = \max(0, a)$. Derivative 1 for $a > 0$, 0 for $a < 0$
  (at $a = 0$ we pick 0 by convention). Vinod Nair and Geoffrey Hinton used it in 2010, and Xavier Glorot, Antoine
  Bordes and Yoshua Bengio (2011) showed that it made deep networks much easier to train than sigmoids. It is now
  the default for hidden layers.

<figure class="mars-fig" markdown="0">
<svg viewBox="0 0 640 230" role="img" aria-label="Plot of three activation functions from minus 4 to 4: the sigmoid rising from 0 to 1, tanh rising from minus 1 to 1, and ReLU, which is zero for negative inputs and the identity for positive inputs.">
  <line x1="60" y1="150" x2="540" y2="150" stroke="currentColor" stroke-width="1"/>
  <line x1="300" y1="30" x2="300" y2="215" stroke="currentColor" stroke-width="1"/>
  <g stroke="currentColor" stroke-width="1">
    <line x1="295" y1="100" x2="305" y2="100"/><line x1="295" y1="50" x2="305" y2="50"/>
    <line x1="295" y1="200" x2="305" y2="200"/>
    <line x1="60" y1="145" x2="60" y2="155"/><line x1="180" y1="145" x2="180" y2="155"/>
    <line x1="420" y1="145" x2="420" y2="155"/><line x1="540" y1="145" x2="540" y2="155"/>
  </g>
  <g fill="currentColor" font-size="11">
    <text x="288" y="104" text-anchor="end">1</text><text x="288" y="54" text-anchor="end">2</text>
    <text x="288" y="204" text-anchor="end">-1</text>
    <text x="60" y="168" text-anchor="middle">-4</text><text x="180" y="168" text-anchor="middle">-2</text>
    <text x="420" y="168" text-anchor="middle">2</text><text x="540" y="168" text-anchor="middle">4</text>
  </g>
  <polyline points="60.0,149.1 66.0,149.0 72.0,148.9 78.0,148.8 84.0,148.7 90.0,148.5 96.0,148.4 102.0,148.2 108.0,148.0 114.0,147.8 120.0,147.6 126.0,147.4 132.0,147.1 138.0,146.9 144.0,146.5 150.0,146.2 156.0,145.8 162.0,145.4 168.0,145.0 174.0,144.5 180.0,144.0 186.0,143.5 192.0,142.9 198.0,142.3 204.0,141.6 210.0,140.9 216.0,140.1 222.0,139.3 228.0,138.4 234.0,137.5 240.0,136.6 246.0,135.5 252.0,134.5 258.0,133.4 264.0,132.3 270.0,131.1 276.0,129.9 282.0,128.7 288.0,127.5 294.0,126.2 300.0,125.0 306.0,123.8 312.0,122.5 318.0,121.3 324.0,120.1 330.0,118.9 336.0,117.7 342.0,116.6 348.0,115.5 354.0,114.5 360.0,113.4 366.0,112.5 372.0,111.6 378.0,110.7 384.0,109.9 390.0,109.1 396.0,108.4 402.0,107.7 408.0,107.1 414.0,106.5 420.0,106.0 426.0,105.5 432.0,105.0 438.0,104.6 444.0,104.2 450.0,103.8 456.0,103.5 462.0,103.1 468.0,102.9 474.0,102.6 480.0,102.4 486.0,102.2 492.0,102.0 498.0,101.8 504.0,101.6 510.0,101.5 516.0,101.3 522.0,101.2 528.0,101.1 534.0,101.0 540.0,100.9" fill="none" stroke="#eea66f" stroke-width="2.5"/>
  <polyline points="60.0,200.0 66.0,200.0 72.0,199.9 78.0,199.9 84.0,199.9 90.0,199.9 96.0,199.9 102.0,199.9 108.0,199.8 114.0,199.8 120.0,199.8 126.0,199.7 132.0,199.6 138.0,199.6 144.0,199.5 150.0,199.3 156.0,199.2 162.0,199.0 168.0,198.8 174.0,198.5 180.0,198.2 186.0,197.8 192.0,197.3 198.0,196.8 204.0,196.1 210.0,195.3 216.0,194.3 222.0,193.1 228.0,191.7 234.0,190.0 240.0,188.1 246.0,185.8 252.0,183.2 258.0,180.2 264.0,176.9 270.0,173.1 276.0,169.0 282.0,164.6 288.0,159.9 294.0,155.0 300.0,150.0 306.0,145.0 312.0,140.1 318.0,135.4 324.0,131.0 330.0,126.9 336.0,123.1 342.0,119.8 348.0,116.8 354.0,114.2 360.0,111.9 366.0,110.0 372.0,108.3 378.0,106.9 384.0,105.7 390.0,104.7 396.0,103.9 402.0,103.2 408.0,102.7 414.0,102.2 420.0,101.8 426.0,101.5 432.0,101.2 438.0,101.0 444.0,100.8 450.0,100.7 456.0,100.5 462.0,100.4 468.0,100.4 474.0,100.3 480.0,100.2 486.0,100.2 492.0,100.2 498.0,100.1 504.0,100.1 510.0,100.1 516.0,100.1 522.0,100.1 528.0,100.1 534.0,100.0 540.0,100.0" fill="none" stroke="#9cc9ea" stroke-width="2.5"/>
  <polyline points="60.0,150.0 300.0,150.0 432.0,40.0" fill="none" stroke="#7ccf9a" stroke-width="2.5"/>
  <g font-size="13" fill="currentColor">
    <line x1="555" y1="60" x2="580" y2="60" stroke="#eea66f" stroke-width="3"/><text x="586" y="64">sigmoid</text>
    <line x1="555" y1="85" x2="580" y2="85" stroke="#9cc9ea" stroke-width="3"/><text x="586" y="89">tanh</text>
    <line x1="555" y1="110" x2="580" y2="110" stroke="#7ccf9a" stroke-width="3"/><text x="586" y="114">ReLU</text>
  </g>
</svg>
<figcaption>The three common activation functions on the interval from -4 to 4. The sigmoid and tanh flatten out
(saturate) for large inputs, so their derivatives vanish there; ReLU never saturates for positive inputs.</figcaption>
</figure>

Each has a weakness. Sigmoid and tanh **saturate**: for large $|a|$ they are almost flat, the derivative is almost
0, and as we will see in 15.4 this tiny factor multiplies into every gradient that passes through, which slows or
stops learning ([Chapter 16](16-Training-Deep-Networks.md) shows it in numbers). ReLU does not saturate for positive
inputs, but a unit whose input is negative for every example has gradient 0 forever: a **dead ReLU**. Variants patch
these problems: **leaky ReLU** $\max(0.01a, a)$ keeps a small slope for negative inputs; **GELU**
$a\,\Phi(a)$, with $\Phi$ the standard normal distribution function (Hendrycks and Gimpel 2016), is a smooth
ReLU-like curve used in transformers ([Chapter 19](19-Transformers.md)).

### Why non-linearity is essential

Could we drop the activation and just stack weighted sums? No: **a composition of linear maps is linear**, so a
network without non-linear activations is no more powerful than one neuron. *Proof:* two layers without activations
compute $W_2(W_1x + b_1) + b_2 = (W_2W_1)x + (W_2b_1 + b_2)$, which is a single linear layer with weights $W_2W_1$
and bias $W_2b_1 + b_2$. By induction, any number of layers collapses to one. The non-linearity is what lets depth
build new features. It does not have to be complicated: ReLU is linear on each side of zero, and that single bend,
repeated across many units, is enough, as 15.6 shows.

## 15.3 Forward pass in matrices

### Notation

A **multilayer perceptron** (MLP), also called a **fully connected feed-forward network**, has $L$ layers. Layer
$l$ has $n_l$ units; $n_0 = p$ is the input size and $n_L$ the output size. Layer $l$ has a **weight matrix**
$W^{(l)}$ of shape $n_{l-1} \times n_l$ and a **bias vector** $b^{(l)}$ of length $n_l$. For one input $x$ (as a row
vector), the **forward pass** computes, for $l = 1, \dots, L$,

$$
a^{(l)} = h^{(l-1)} W^{(l)} + b^{(l)}, \qquad h^{(l)} = \phi\big(a^{(l)}\big), \qquad h^{(0)} = x ,
$$

where $a^{(l)}$ are the **pre-activations**, $h^{(l)}$ the **activations**, and $\phi$ is the activation function
applied to every entry separately. The last layer usually has no $\phi$ (or a special one): its raw outputs are
**scores** or **logits**, which go into the loss. For regression the loss is squared error on the score; for two
classes it is the logistic loss of [Chapter 6](06-Classification-and-Logistic-Regression.md) on one logit; for $K$
classes it is softmax cross-entropy on $K$ logits.

**Batches.** We almost never push one example at a time. Stack $B$ inputs as the rows of a $B \times p$ matrix $X$.
Then exactly the same formulas hold with $h^{(l)}$ and $a^{(l)}$ as $B \times n_l$ matrices, and the bias row
$b^{(l)}$ is added to every row (NumPy broadcasting, [Chapter 3](03-The-Math-Toolkit.md)). A whole batch costs a few
matrix multiplications, which is exactly the operation that modern hardware is built to do fast.

**Counting.** Layer $l$ has $n_{l-1}n_l$ weights and $n_l$ biases. A 2-32-32-1 network, used in 15.7, has
$2\cdot32 + 32 + 32\cdot32 + 32 + 32\cdot1 + 1 = 1185$ parameters. A forward pass of a batch of $B$ costs about
$B\sum_l n_{l-1}n_l$ multiply-adds.

### A forward pass by hand

Take the trained XOR network's shape (2-2-1) with these weights:
$W^{(1)} = \begin{pmatrix} 1 & 1 \\ 1 & 1 \end{pmatrix}$, $b^{(1)} = (-0.5, -1.5)$,
$W^{(2)} = \begin{pmatrix} 1 \\ -1 \end{pmatrix}$, $b^{(2)} = -0.5$, and step activations. For the batch of all four
inputs,

$$
XW^{(1)} + b^{(1)} = \begin{pmatrix} 0 & 0 \\ 1 & 1 \\ 1 & 1 \\ 2 & 2 \end{pmatrix} + \begin{pmatrix} -0.5 & -1.5 \end{pmatrix}
= \begin{pmatrix} -0.5 & -1.5 \\ 0.5 & -0.5 \\ 0.5 & -0.5 \\ 1.5 & 0.5 \end{pmatrix},
\qquad
H = \begin{pmatrix} 0 & 0 \\ 1 & 0 \\ 1 & 0 \\ 1 & 1 \end{pmatrix},
$$

and $HW^{(2)} + b^{(2)} = (-0.5, 0.5, 0.5, -0.5)^\top$, whose step is $(0, 1, 1, 0)^\top$: XOR. Every network in
this book, up to the transformers of [Chapter 19](19-Transformers.md), is this pattern of matrix products and
elementwise functions, with more and differently shaped layers.

### Why "deep"

A **deep** network has many hidden layers. Why prefer depth to one very wide layer? Each layer can build features
out of the previous layer's features: in image networks the first layers detect edges, later ones textures and parts,
the last ones whole objects ([Chapter 17](17-Convolutional-Networks.md)). There are also theorems (15.6) showing
functions that a deep network computes with few units but a shallow one needs exponentially many units for. Depth
also makes training harder, which is the subject of [Chapter 16](16-Training-Deep-Networks.md).

## 15.4 Backpropagation and computational graphs

### The problem

To train by gradient descent ([Chapter 5](05-Optimization.md)) we need the gradient of the loss with respect to
**every** weight. A modest network has a million weights. Estimating each partial derivative by finite differences,
$(L(w + h e_j) - L(w - h e_j))/2h$, needs two forward passes per weight: two million forward passes for one step.
**Backpropagation** computes all of them exactly in roughly the time of **two** forward passes. That difference is
the reason neural networks are practical.

### The chain rule, organised

The chain rule ([Chapter 3](03-The-Math-Toolkit.md)) says that if $L$ depends on $u$ only through $v$, then
$\frac{\partial L}{\partial u} = \frac{\partial L}{\partial v}\frac{\partial v}{\partial u}$; if $u$ affects $L$
through several variables $v_1, \dots, v_m$, the contributions add:
$\frac{\partial L}{\partial u} = \sum_k \frac{\partial L}{\partial v_k}\frac{\partial v_k}{\partial u}$.

Apply it to the network, one example at a time first. Define the **error signal** of layer $l$ as the gradient of
the loss with respect to the pre-activations,

$$
\delta^{(l)} = \frac{\partial L}{\partial a^{(l)}} \qquad (\text{a row vector of length } n_l).
$$

Three facts, each one line of the chain rule, give everything.

**1. The weights of layer $l$.** The weight $W^{(l)}_{jk}$ affects the loss only through $a^{(l)}_k = \sum_j h^{(l-1)}_j W^{(l)}_{jk} + b^{(l)}_k$,
and $\partial a^{(l)}_k / \partial W^{(l)}_{jk} = h^{(l-1)}_j$. So

$$
\frac{\partial L}{\partial W^{(l)}_{jk}} = h^{(l-1)}_j\,\delta^{(l)}_k ,
\qquad\text{that is}\qquad
\frac{\partial L}{\partial W^{(l)}} = \big(h^{(l-1)}\big)^\top \delta^{(l)},
\qquad
\frac{\partial L}{\partial b^{(l)}} = \delta^{(l)} .
$$

The gradient of a weight is "input to the weight times error at its output": an outer product.

**2. Passing back through a weight layer.** $h^{(l-1)}_j$ affects every $a^{(l)}_k$, with
$\partial a^{(l)}_k/\partial h^{(l-1)}_j = W^{(l)}_{jk}$, so the contributions add:

$$
\frac{\partial L}{\partial h^{(l-1)}} = \delta^{(l)}\big(W^{(l)}\big)^\top .
$$

**3. Passing back through the activation.** $h^{(l-1)}_j = \phi(a^{(l-1)}_j)$ depends only on $a^{(l-1)}_j$, so

$$
\delta^{(l-1)} = \frac{\partial L}{\partial h^{(l-1)}} \odot \phi'\big(a^{(l-1)}\big),
$$

where $\odot$ is elementwise multiplication.

**Backpropagation** runs these from the top down. Start with $\delta^{(L)}$, the gradient of the loss with respect to
the output scores. Then for $l = L, L-1, \dots, 1$: compute the weight and bias gradients of layer $l$ by fact 1, and
the error signal of the layer below by facts 2 and 3:

$$
\delta^{(l-1)} = \Big(\delta^{(l)}\big(W^{(l)}\big)^\top\Big) \odot \phi'\big(a^{(l-1)}\big).
$$

For a batch, the $\delta$'s become $B \times n_l$ matrices and fact 1 becomes $(H^{(l-1)})^\top\Delta^{(l)}$, which
automatically sums the per-example gradients. With the loss defined as a mean over the batch, the starting
$\Delta^{(L)}$ carries the factor $1/B$.

**The starting signal.** For a logit $s$ with the logistic loss $L = -y\log\sigma(s) - (1-y)\log(1-\sigma(s))$, the
derivative is beautifully simple:

$$
\frac{\partial L}{\partial s} = -y(1 - \sigma(s)) + (1 - y)\sigma(s) = \sigma(s) - y ,
$$

using $\frac{d}{ds}\log\sigma(s) = 1 - \sigma(s)$ and $\frac{d}{ds}\log(1 - \sigma(s)) = -\sigma(s)$. Prediction minus
target. For softmax with cross-entropy over $K$ classes the same holds componentwise: $\delta^{(L)} = p - y$, with
$p$ the softmax probabilities and $y$ the one-hot target ([Chapter 6](06-Classification-and-Logistic-Regression.md)
derives it). For squared error $\frac12(s - y)^2$ it is again $s - y$.

### Why it is cheap

Count operations. The forward pass of a batch costs about $B\sum_l n_{l-1}n_l$ multiply-adds (the matrix products).
The backward pass does, for every layer, one product of the same size for the weight gradient
($(H^{(l-1)})^\top\Delta^{(l)}$) and one for passing the signal down ($\Delta^{(l)}(W^{(l)})^\top$), plus elementwise
work. So **backpropagation costs about twice the forward pass, whatever the number of weights.** The price is
memory: the backward pass needs every $h^{(l)}$ and $a^{(l)}$ from the forward pass, so they must be stored.

### History

The mathematical core, computing derivatives of a composite function in reverse order, is older than neural
networks. Seppo Linnainmaa described reverse-mode automatic differentiation in his 1970 master's thesis; Paul Werbos
proposed applying it to train neural networks in his 1974 PhD thesis; and several groups found versions
independently. The paper that made it the standard method was David Rumelhart, Geoffrey Hinton and Ronald Williams,
"Learning Representations by Back-propagating Errors" (*Nature*, 1986), which showed experimentally that hidden units
trained this way learn useful internal features. Its title states the main point: what is learned is a
**representation**.

### Computational graphs

The layer-by-layer derivation is a special case of something more general. Any calculation can be drawn as a
**computational graph**: a directed acyclic graph whose nodes are intermediate values and whose edges say which
values each one was computed from. Take

$$
f(a, b) = (ab + b)\tanh(a)
$$

at $a = 2$, $b = -3$. Name the intermediate results: $c = ab$, $d = c + b$, $t = \tanh(a)$, $f = dt$.

**Forward pass** (left to right): $c = -6$, $d = -9$, $t = \tanh 2 \approx 0.964028$, $f \approx -8.676248$.

**Backward pass** (right to left). Write $\bar{v} = \partial f/\partial v$ for the **adjoint** of node $v$. Start
with $\bar{f} = 1$ and visit nodes in reverse order, each time pushing its adjoint to its inputs by the local
derivative:

| node visited | local rule | contributions | adjoints so far |
|---|---|---|---|
| $f = dt$ | $\partial f/\partial d = t$, $\partial f/\partial t = d$ | $\bar d \mathrel{+}= 0.964028$, $\bar t \mathrel{+}= -9$ | $\bar d = 0.964028$, $\bar t = -9$ |
| $t = \tanh a$ | $\partial t/\partial a = 1 - t^2 = 0.070651$ | $\bar a \mathrel{+}= -9 \times 0.070651$ | $\bar a = -0.635857$ |
| $d = c + b$ | both derivatives 1 | $\bar c \mathrel{+}= 0.964028$, $\bar b \mathrel{+}= 0.964028$ | $\bar c = 0.964028$, $\bar b = 0.964028$ |
| $c = ab$ | $\partial c/\partial a = b$, $\partial c/\partial b = a$ | $\bar a \mathrel{+}= 0.964028 \times (-3)$, $\bar b \mathrel{+}= 0.964028 \times 2$ | $\bar a = -3.527940$, $\bar b = 2.892083$ |

So $\partial f/\partial a \approx -3.527940$ and $\partial f/\partial b \approx 2.892083$. Two things to notice. Both
$a$ and $b$ are used **twice**, and their adjoints are **sums** of the contributions along every path to $f$: this is
the multi-path chain rule, and it is why the engine below uses `+=`. And the order matters: a node may push its
adjoint only after it has received all contributions from the nodes that use it. A **reverse topological order** of
the graph guarantees this (see the reference page on [topological sort](../../graphs/topological-sort.md)).

<figure class="mars-fig" markdown="0">
<svg viewBox="0 0 640 265" role="img" aria-label="The computational graph of f equals (a times b plus b) times tanh(a). Nodes a and b feed a multiply node c equals minus 6; c and b feed an add node d equals minus 9; a feeds a tanh node t equals 0.964; d and t feed a multiply node f equals minus 8.676. Under each node, its forward value and its gradient: a has gradient minus 3.528, b has 2.892, c and d have 0.964, t has minus 9, f has 1.">
  <g stroke="currentColor" stroke-width="1.3">
    <line x1="70" y1="60" x2="220" y2="120"/>
    <line x1="70" y1="200" x2="220" y2="120"/>
    <line x1="70" y1="60" x2="220" y2="40"/>
    <line x1="220" y1="120" x2="360" y2="200"/>
    <line x1="70" y1="200" x2="360" y2="200"/>
    <line x1="360" y1="200" x2="500" y2="130"/>
    <line x1="220" y1="40" x2="500" y2="130"/>
  </g>
  <g stroke="currentColor" stroke-width="0.8">
    <circle cx="70" cy="60" r="22" fill="#9cc9ea"/>
    <circle cx="70" cy="200" r="22" fill="#9cc9ea"/>
    <circle cx="220" cy="120" r="22" fill="#7ccf9a"/>
    <circle cx="220" cy="40" r="22" fill="#7ccf9a"/>
    <circle cx="360" cy="200" r="22" fill="#7ccf9a"/>
    <circle cx="500" cy="130" r="22" fill="#eea66f"/>
  </g>
  <g fill="currentColor" font-size="14" text-anchor="middle">
    <text x="70" y="65">a</text><text x="70" y="205">b</text>
    <text x="220" y="125">c = ×</text><text x="220" y="45">t = tanh</text>
    <text x="360" y="205">d = +</text><text x="500" y="135">f = ×</text>
  </g>
  <g fill="currentColor" font-size="11" text-anchor="middle">
    <text x="70" y="98">value 2</text><text x="70" y="112">grad -3.528</text>
    <text x="70" y="238">value -3</text><text x="70" y="252">grad 2.892</text>
    <text x="220" y="158">value -6</text><text x="220" y="172">grad 0.964</text>
    <text x="220" y="78">value 0.964</text><text x="220" y="92">grad -9</text>
    <text x="360" y="238">value -9</text><text x="360" y="252">grad 0.964</text>
    <text x="500" y="168">value -8.676</text><text x="500" y="182">grad 1</text>
  </g>
</svg>
<figcaption>A computational graph. Values flow left to right in the forward pass; gradients flow right to left in
the backward pass. Nodes used twice (a and b) add up the gradients arriving along each path.</figcaption>
</figure>

### Reverse mode against forward mode

The chain rule can also be applied from the inputs forward: carry, alongside every value, its derivative with
respect to **one** chosen input. That is **forward-mode** automatic differentiation; one pass gives the derivatives of
all outputs with respect to one input. Reverse mode gives the derivatives of **one** output with respect to **all**
inputs in one pass. A loss is one number depending on millions of weights, so reverse mode wins by a factor of
millions. (For a function with few inputs and many outputs, forward mode wins.) This is the whole reason
backpropagation is fast: a training loss has a single output.

### Checking a gradient

Backpropagation code is easy to get subtly wrong: a missing transpose, a forgotten factor. Always check it against
finite differences on a small case, as [Chapter 3](03-The-Math-Toolkit.md) taught. The central difference
$(L(w + h) - L(w - h))/2h$ has error of order $h^2$, so with $h = 10^{-6}$ agreement to about $10^{-8}$ or better
means the code is right. The program does it for the 2-2-1 network:

```python
--8<-- "books/machine-learning/ch15_xor.py"
```

```
1. The perceptron on XOR: mistakes in the 100th pass over the data = 4

2. A hand-made network: h1 = step(x1 + x2 - 0.5) (OR), h2 = step(x1 + x2 - 1.5) (AND), out = step(h1 - h2 - 0.5)
  x = [0, 0]  hidden = [0, 0]  output = 0
  x = [0, 1]  hidden = [1, 0]  output = 1
  x = [1, 0]  hidden = [1, 0]  output = 1
  x = [1, 1]  hidden = [1, 1]  output = 0

3. Gradient check: backpropagation against finite differences (h = 1e-6)
  largest difference over all 9 parameters: 4.4e-11

4. Training the 2-2-1 sigmoid network by gradient descent, learning rate 2
  step     1: loss 0.6959
  step    10: loss 0.6934
  step   100: loss 0.6931
  step   500: loss 0.0810
  step  1000: loss 0.0088
  step  5000: loss 0.0010
  outputs: [0.001, 0.999, 0.999, 0.001]
```

Backpropagation agrees with finite differences to $4 \times 10^{-11}$ over all nine parameters. Training is
instructive too: the loss sits at about $0.693 = \ln 2$ (the loss of always predicting one half) for hundreds of
steps, then falls quickly to near zero, and the outputs become $0.001, 0.999, 0.999, 0.001$. Such **plateaus**
followed by sudden progress are typical of neural network training, and they come from the symmetric start: the
network first has to break the symmetry between its hidden units before either can specialise into an OR-like or
AND-like feature. Not every start is so lucky: running the same training from 50 random seeds, we found 8 that were still stuck
(loss above 0.1) after 5000 steps. Wider hidden layers make that much rarer.

## 15.5 A tiny automatic-differentiation engine from scratch

Deriving backpropagation by hand for every new architecture would be slow and error-prone. Modern frameworks
instead **record the computational graph as the forward computation runs**, then walk it backwards. We can build
the core of that idea in about a hundred lines of plain Python, for scalars.

### Design

Each number becomes a `Value` object holding

- `data`: the number itself;
- `grad`: its adjoint $\partial(\text{output})/\partial(\text{this value})$, initially 0;
- `_parents`: the values it was computed from (the graph's edges);
- `_backward`: a small function that, given this node's `grad`, adds the right amounts to its parents' `grad`s.

Every operation (`+`, `*`, `**`, `tanh`, `relu`, `exp`, `log`) does two things: it computes the result, and it
attaches a `_backward` function that knows the local derivative. For multiplication $c = ab$ that function does
`a.grad += b.data * c.grad` and `b.grad += a.data * c.grad`: exactly the rows of the table in 15.4. Subtraction and
division are built from the others ($a - b = a + (-1)b$, $a/b = a \cdot b^{-1}$), so they need no new rules.

Calling `backward()` on the final value

1. builds a topological order of all nodes that the output depends on, by depth-first search (each node is appended
   after all its parents, so the list runs from inputs to output);
2. sets the output's `grad` to 1;
3. calls every node's `_backward` in **reverse** of that order.

Because of the reverse topological order, when a node pushes its gradient to its parents it has already received
everything from all the nodes that use it, so its `grad` is final. Each node and edge is processed once, so the
backward pass costs time proportional to the size of the graph, like the forward pass.

### An MLP on the engine

Once the engine exists, a neural network is just Python code that does arithmetic with `Value`s: each neuron is
`sum(w_i * x_i) + b` followed by `tanh()`. Training is three lines: compute the loss, reset gradients to zero, call
`loss.backward()`, then move every parameter against its gradient. There is no backpropagation code in the network
at all; the engine derives it from whatever the forward computation did.

```python
--8<-- "books/machine-learning/ch15_autodiff.py"
```

```
1. f(a, b) = (a * b + b) * tanh(a) at a = 2, b = -3
  f = -8.676248   df/da = -3.527940   df/db = 2.892083   (6 nodes in the graph)
  finite differences:   df/da = -3.527940   df/db = 2.892083

2. A 2-6-6-1 MLP on the engine, trained on 40 points of two interleaved half-moons
  67 parameters
  epoch   1: loss 0.5466  training accuracy 0.90
  epoch  10: loss 0.2039  training accuracy 0.93
  epoch  20: loss 0.1357  training accuracy 0.97
  epoch  30: loss 0.1058  training accuracy 0.97
  epoch  50: loss 0.0776  training accuracy 0.97
```

Part 1 reproduces the hand computation of 15.4 and confirms it with finite differences. Part 2 trains a 2-6-6-1
network (67 parameters) on 40 points of two interleaved half-moons, with the loss $\log(1 + e^{-ys})$ for labels
$y = \pm 1$ and score $s$ (the logistic loss written for $\pm 1$ labels). The loss falls steadily, and training
accuracy reaches 0.97 (one point of the 40 is still on the wrong side).

The engine is slow: every scalar operation is a Python object, so the 50 epochs above take a few seconds, while the
NumPy network of 15.7 trains a network 18 times bigger on ten times more data faster. Real frameworks apply exactly the same idea to
whole arrays: a node is a tensor operation (a matrix product, a convolution), its `_backward` is a vectorised
formula such as $(H^{(l-1)})^\top\Delta^{(l)}$, and the work runs on fast hardware. The idea of a small scalar
engine for teaching follows Andrej Karpathy's open-source "micrograd" (2020).

## 15.6 Universal approximation

*Level: advanced.*

### The question

Can a neural network represent any function we might want? For one hidden layer the answer is a famous theorem.
Let $\phi$ be the activation. A one-hidden-layer network with $N$ hidden units and one output computes

$$
g(x) = \sum_{j=1}^{N} c_j\, \phi\big(w_j^\top x + b_j\big) + c_0 .
$$

**Theorem (Cybenko 1989).** Let $\phi$ be continuous and **sigmoidal**: $\phi(a) \to 1$ as $a \to \infty$ and
$\phi(a) \to 0$ as $a \to -\infty$. Then for every continuous function $f$ on the cube $[0,1]^p$ and every
$\varepsilon > 0$, there is a network $g$ of the form above (with some finite $N$) such that
$|g(x) - f(x)| < \varepsilon$ for all $x$ in the cube.

In words: one hidden layer of sigmoids, wide enough, can approximate any continuous function on a bounded box as
closely as you like. Kurt Hornik, Maxwell Stinchcombe and Halbert White proved a similar result in 1989; Hornik
(1991) showed that what matters is the multilayer architecture, not the particular activation: any bounded,
non-constant continuous $\phi$ works. Moshe Leshno, Vladimir Lin, Allan Pinkus and Shimon Schocken (1993) found the
exact condition: a continuous activation gives universal approximation **if and only if it is not a polynomial**.
ReLU qualifies.

### The idea of the proof, in one dimension

Cybenko's proof is short but uses functional analysis (the Hahn-Banach theorem and the Riesz representation
theorem): if the networks could not approximate some $f$, there would be a non-zero measure that "sees" no sigmoid
at all, and he shows no such measure exists. That proof does not tell you how to build the network. In one
dimension there is a constructive argument that does, and it shows the idea clearly.

**Step functions from sigmoids.** $\sigma(k(x - t))$ with a large slope $k$ is almost a step from 0 to 1 at $x = t$.

**Any continuous function from steps.** A continuous $f$ on $[0, 1]$ is **uniformly continuous**: for any
$\varepsilon$ there is a spacing $\Delta$ such that $f$ changes by less than $\varepsilon$ over any interval of length
$\Delta$. Cut $[0,1]$ into $N \ge 1/\Delta$ pieces at knots $t_0 = 0 < t_1 < \dots < t_N = 1$ and define the
**staircase**

$$
g(x) = f(t_0) + \sum_{j=1}^{N} \big(f(t_j) - f(t_{j-1})\big)\,\mathrm{step}(x - m_j),
$$

where $m_j$ is the midpoint of the $j$-th piece. At any $x$, the steps that have switched on add up (the sum
telescopes) to $f(t_j)$ for the nearest knot $t_j$ on the correct side, within $\varepsilon$ of $f(x)$. Replace each step by a steep sigmoid and
the staircase becomes a network with $N$ hidden units; making the sigmoids steep enough keeps the extra error as
small as we like. So one hidden layer suffices in one dimension.

**With ReLUs**, it is even cleaner. A sum $c_0 + \sum_j c_j\max(0, x - t_j)$ is a continuous piecewise-linear function
with a bend at each $t_j$, and every continuous piecewise-linear function with $N$ pieces can be written this way:
the first unit sets the first slope, each next unit changes the slope at its knot. Piecewise-linear interpolation
of a smooth $f$ at $N + 1$ equally spaced knots has error at most $\max|f''|/(8N^2)$ (a standard bound from numerical
analysis), so $N$ ReLU units give error $O(1/N^2)$, much better than the staircase's $O(1/N)$.

```python
--8<-- "books/machine-learning/ch15_universal.py"
```

```
Largest error on [0, 1] of a one-hidden-layer network with N units
      N   sigmoid staircase   ReLU interpolant
      4             0.62223           0.210514
      8             0.32163           0.070378
     16             0.16212           0.018846
     32             0.08122           0.004792
     64             0.04063           0.001203
    128             0.02032           0.000301
    256             0.01016           0.000075
```

The program writes both constructions down (no training) for $f(x) = \sin(2\pi x) + x/2$. Each doubling of $N$ halves
the staircase's error and quarters the ReLU interpolant's error, as predicted. In more than one dimension, a
constructive proof builds localised "bumps" from several sigmoids or ReLUs and adds bumps the way we added steps.

### What the theorem does not say

The theorem is often quoted as "neural networks can learn anything". It says much less.

- **Size.** It gives no useful bound on $N$. To approximate a general continuous function on $[0,1]^p$ to accuracy
  $\varepsilon$, the number of bumps grows like $(1/\varepsilon)^p$: exponential in the dimension. Andrew Barron (1993)
  showed that functions with a certain smoothness of their Fourier transform need only $O(1/\varepsilon^2)$ units,
  independent of dimension, which is one explanation of why networks work in practice.
- **Learning.** It says the right weights **exist**, not that gradient descent will **find** them from data.
- **Generalisation.** It says nothing about how a network fitted on a training set behaves on new points; that is
  the subject of [Chapter 21](21-Learning-Theory.md).
- **Depth.** One hidden layer is enough in principle, but depth can be exponentially more efficient. Matus Telgarsky
  (2016) constructed functions computed by ReLU networks with $O(k^3)$ layers and a constant number of units per layer
  that any network with only $O(k)$ layers needs at least $2^k$ units to approximate. Ronen Eldan and Ohad Shamir
  (2016) gave a function on $\mathbb{R}^p$ that a 3-layer network computes with polynomially many units in $p$ but a
  2-layer network needs exponentially many. Composition is powerful: a ReLU network of depth $k$ can make a sawtooth
  with $2^k$ teeth by folding the line in half $k$ times.

## 15.7 Training an MLP from scratch on two spirals

### Two spirals

The two-spirals problem is a classic test for neural networks: two arms of points winding around the origin and
around each other. No line, no simple curve, separates them, and nearby points of the two classes are close together
at every angle. We now train MLPs of three sizes on it, in NumPy, with backpropagation written out as in 15.4.

The program's pieces, all from this chapter or earlier ones:

- `forward` keeps every layer's activations (backpropagation needs them);
- `backward` starts from $\delta^{(L)} = (\sigma(s) - y)/n$ and applies the three facts layer by layer, using the
  ReLU derivative `(acts[i] > 0)`;
- the loss is the logistic loss computed stably as $\log(1 + e^{s}) - ys$ with `np.logaddexp`;
- the weights are updated with Adam ([Chapter 5](05-Optimization.md)) at learning rate 0.01;
- the initial weights have variance $2/n_{\text{in}}$ (**He initialisation**, explained in
  [Chapter 16](16-Training-Deep-Networks.md)), and the biases start at 0.

```python
--8<-- "books/machine-learning/ch15_mlp_spirals.py"
```

```
Two spirals: 400 training points, 400 test points
  layers [2, 1]:     3 parameters, train accuracy 0.613, test accuracy 0.627
  layers [2, 8, 1]:    33 parameters, train accuracy 0.853, test accuracy 0.800
  layers [2, 32, 32, 1]:  1185 parameters, train accuracy 1.000, test accuracy 0.985
  loss of the 2-32-32-1 network during training: step 1: 0.7029, step 100: 0.2200, step 250: 0.0046, step 500: 0.0008, step 1000: 0.0002, step 1500: 0.0001

Its decision regions on [-1.2, 1.2]^2 ('#' = class 1):
  ################################################
  ################################################
  ################################################
  ################################################
  ################################################
  ##############...............###################
  ############...................#################
  ##########.........#######.......###############
  ##########.....##############.....##############
  #########.....#################.....############
  ########.....######.......#####......###########
  ########....#####.........#####........#########
  ######.....######.....#########......####.......
  #####......######.....#######......######.......
  ##..........######................######........
  .............#######............#######.........
  ..............########.......#########..........
  ................####################............
  ...................#############................
  ................................................
  ................................................
  ................................................
  ................................................
  ................................................
```

The three rows tell the chapter's story.

- With **no hidden layer** (`[2, 1]`, which is logistic regression) the boundary is a line and accuracy is about 0.6,
  little better than guessing.
- With **one small hidden layer** of 8 ReLUs (`[2, 8, 1]`) the boundary is a polygon of at most a few straight
  pieces; it follows the inner part of the spirals and fails on the outer turns (0.85 on training data, 0.80 on test).
- With **two hidden layers of 32** (`[2, 32, 32, 1]`, 1185 parameters) training accuracy is 1.000 and accuracy on
  400 new points from the same spirals is 0.985. The loss falls from 0.70 to 0.0001.

<figure class="mars-fig" markdown="0">
<svg viewBox="0 0 640 335" role="img" aria-label="Decision regions of two trained networks on the two-spirals data, with a sample of the training points. Left, the 2-8-1 network: a few straight-edged regions that miss the outer turns of the spirals. Right, the 2-32-32-1 network: curved regions that follow both spiral arms.">
  <rect x="20.0" y="20.0" width="280.0" height="7.0" fill="#eea66f" fill-opacity="0.35"/>
  <rect x="20.0" y="27.0" width="280.0" height="7.0" fill="#eea66f" fill-opacity="0.35"/>
  <rect x="20.0" y="34.0" width="280.0" height="7.0" fill="#eea66f" fill-opacity="0.35"/>
  <rect x="20.0" y="41.0" width="280.0" height="7.0" fill="#eea66f" fill-opacity="0.35"/>
  <rect x="20.0" y="48.0" width="280.0" height="7.0" fill="#eea66f" fill-opacity="0.35"/>
  <rect x="20.0" y="55.0" width="189.0" height="7.0" fill="#eea66f" fill-opacity="0.35"/>
  <rect x="209.0" y="55.0" width="14.0" height="7.0" fill="#9cc9ea" fill-opacity="0.35"/>
  <rect x="223.0" y="55.0" width="77.0" height="7.0" fill="#eea66f" fill-opacity="0.35"/>
  <rect x="20.0" y="62.0" width="175.0" height="7.0" fill="#eea66f" fill-opacity="0.35"/>
  <rect x="195.0" y="62.0" width="28.0" height="7.0" fill="#9cc9ea" fill-opacity="0.35"/>
  <rect x="223.0" y="62.0" width="77.0" height="7.0" fill="#eea66f" fill-opacity="0.35"/>
  <rect x="20.0" y="69.0" width="154.0" height="7.0" fill="#eea66f" fill-opacity="0.35"/>
  <rect x="174.0" y="69.0" width="49.0" height="7.0" fill="#9cc9ea" fill-opacity="0.35"/>
  <rect x="223.0" y="69.0" width="77.0" height="7.0" fill="#eea66f" fill-opacity="0.35"/>
  <rect x="20.0" y="76.0" width="133.0" height="7.0" fill="#eea66f" fill-opacity="0.35"/>
  <rect x="153.0" y="76.0" width="70.0" height="7.0" fill="#9cc9ea" fill-opacity="0.35"/>
  <rect x="223.0" y="76.0" width="77.0" height="7.0" fill="#eea66f" fill-opacity="0.35"/>
  <rect x="20.0" y="83.0" width="112.0" height="7.0" fill="#eea66f" fill-opacity="0.35"/>
  <rect x="132.0" y="83.0" width="70.0" height="7.0" fill="#9cc9ea" fill-opacity="0.35"/>
  <rect x="202.0" y="83.0" width="98.0" height="7.0" fill="#eea66f" fill-opacity="0.35"/>
  <rect x="20.0" y="90.0" width="91.0" height="7.0" fill="#eea66f" fill-opacity="0.35"/>
  <rect x="111.0" y="90.0" width="70.0" height="7.0" fill="#9cc9ea" fill-opacity="0.35"/>
  <rect x="181.0" y="90.0" width="119.0" height="7.0" fill="#eea66f" fill-opacity="0.35"/>
  <rect x="20.0" y="97.0" width="70.0" height="7.0" fill="#eea66f" fill-opacity="0.35"/>
  <rect x="90.0" y="97.0" width="70.0" height="7.0" fill="#9cc9ea" fill-opacity="0.35"/>
  <rect x="160.0" y="97.0" width="49.0" height="7.0" fill="#eea66f" fill-opacity="0.35"/>
  <rect x="209.0" y="97.0" width="14.0" height="7.0" fill="#9cc9ea" fill-opacity="0.35"/>
  <rect x="223.0" y="97.0" width="77.0" height="7.0" fill="#eea66f" fill-opacity="0.35"/>
  <rect x="20.0" y="104.0" width="49.0" height="7.0" fill="#eea66f" fill-opacity="0.35"/>
  <rect x="69.0" y="104.0" width="70.0" height="7.0" fill="#9cc9ea" fill-opacity="0.35"/>
  <rect x="139.0" y="104.0" width="63.0" height="7.0" fill="#eea66f" fill-opacity="0.35"/>
  <rect x="202.0" y="104.0" width="21.0" height="7.0" fill="#9cc9ea" fill-opacity="0.35"/>
  <rect x="223.0" y="104.0" width="77.0" height="7.0" fill="#eea66f" fill-opacity="0.35"/>
  <rect x="20.0" y="111.0" width="35.0" height="7.0" fill="#eea66f" fill-opacity="0.35"/>
  <rect x="55.0" y="111.0" width="63.0" height="7.0" fill="#9cc9ea" fill-opacity="0.35"/>
  <rect x="118.0" y="111.0" width="70.0" height="7.0" fill="#eea66f" fill-opacity="0.35"/>
  <rect x="188.0" y="111.0" width="35.0" height="7.0" fill="#9cc9ea" fill-opacity="0.35"/>
  <rect x="223.0" y="111.0" width="77.0" height="7.0" fill="#eea66f" fill-opacity="0.35"/>
  <rect x="20.0" y="118.0" width="14.0" height="7.0" fill="#eea66f" fill-opacity="0.35"/>
  <rect x="34.0" y="118.0" width="70.0" height="7.0" fill="#9cc9ea" fill-opacity="0.35"/>
  <rect x="104.0" y="118.0" width="70.0" height="7.0" fill="#eea66f" fill-opacity="0.35"/>
  <rect x="174.0" y="118.0" width="49.0" height="7.0" fill="#9cc9ea" fill-opacity="0.35"/>
  <rect x="223.0" y="118.0" width="70.0" height="7.0" fill="#eea66f" fill-opacity="0.35"/>
  <rect x="293.0" y="118.0" width="7.0" height="7.0" fill="#9cc9ea" fill-opacity="0.35"/>
  <rect x="20.0" y="125.0" width="63.0" height="7.0" fill="#9cc9ea" fill-opacity="0.35"/>
  <rect x="83.0" y="125.0" width="77.0" height="7.0" fill="#eea66f" fill-opacity="0.35"/>
  <rect x="160.0" y="125.0" width="63.0" height="7.0" fill="#9cc9ea" fill-opacity="0.35"/>
  <rect x="223.0" y="125.0" width="70.0" height="7.0" fill="#eea66f" fill-opacity="0.35"/>
  <rect x="293.0" y="125.0" width="7.0" height="7.0" fill="#9cc9ea" fill-opacity="0.35"/>
  <rect x="20.0" y="132.0" width="42.0" height="7.0" fill="#9cc9ea" fill-opacity="0.35"/>
  <rect x="62.0" y="132.0" width="98.0" height="7.0" fill="#eea66f" fill-opacity="0.35"/>
  <rect x="160.0" y="132.0" width="63.0" height="7.0" fill="#9cc9ea" fill-opacity="0.35"/>
  <rect x="223.0" y="132.0" width="63.0" height="7.0" fill="#eea66f" fill-opacity="0.35"/>
  <rect x="286.0" y="132.0" width="14.0" height="7.0" fill="#9cc9ea" fill-opacity="0.35"/>
  <rect x="20.0" y="139.0" width="21.0" height="7.0" fill="#9cc9ea" fill-opacity="0.35"/>
  <rect x="41.0" y="139.0" width="112.0" height="7.0" fill="#eea66f" fill-opacity="0.35"/>
  <rect x="153.0" y="139.0" width="70.0" height="7.0" fill="#9cc9ea" fill-opacity="0.35"/>
  <rect x="223.0" y="139.0" width="56.0" height="7.0" fill="#eea66f" fill-opacity="0.35"/>
  <rect x="279.0" y="139.0" width="21.0" height="7.0" fill="#9cc9ea" fill-opacity="0.35"/>
  <rect x="20.0" y="146.0" width="14.0" height="7.0" fill="#9cc9ea" fill-opacity="0.35"/>
  <rect x="34.0" y="146.0" width="119.0" height="7.0" fill="#eea66f" fill-opacity="0.35"/>
  <rect x="153.0" y="146.0" width="70.0" height="7.0" fill="#9cc9ea" fill-opacity="0.35"/>
  <rect x="223.0" y="146.0" width="56.0" height="7.0" fill="#eea66f" fill-opacity="0.35"/>
  <rect x="279.0" y="146.0" width="21.0" height="7.0" fill="#9cc9ea" fill-opacity="0.35"/>
  <rect x="20.0" y="153.0" width="21.0" height="7.0" fill="#9cc9ea" fill-opacity="0.35"/>
  <rect x="41.0" y="153.0" width="105.0" height="7.0" fill="#eea66f" fill-opacity="0.35"/>
  <rect x="146.0" y="153.0" width="77.0" height="7.0" fill="#9cc9ea" fill-opacity="0.35"/>
  <rect x="223.0" y="153.0" width="49.0" height="7.0" fill="#eea66f" fill-opacity="0.35"/>
  <rect x="272.0" y="153.0" width="28.0" height="7.0" fill="#9cc9ea" fill-opacity="0.35"/>
  <rect x="20.0" y="160.0" width="28.0" height="7.0" fill="#9cc9ea" fill-opacity="0.35"/>
  <rect x="48.0" y="160.0" width="98.0" height="7.0" fill="#eea66f" fill-opacity="0.35"/>
  <rect x="146.0" y="160.0" width="77.0" height="7.0" fill="#9cc9ea" fill-opacity="0.35"/>
  <rect x="223.0" y="160.0" width="42.0" height="7.0" fill="#eea66f" fill-opacity="0.35"/>
  <rect x="265.0" y="160.0" width="35.0" height="7.0" fill="#9cc9ea" fill-opacity="0.35"/>
  <rect x="20.0" y="167.0" width="35.0" height="7.0" fill="#9cc9ea" fill-opacity="0.35"/>
  <rect x="55.0" y="167.0" width="84.0" height="7.0" fill="#eea66f" fill-opacity="0.35"/>
  <rect x="139.0" y="167.0" width="84.0" height="7.0" fill="#9cc9ea" fill-opacity="0.35"/>
  <rect x="223.0" y="167.0" width="42.0" height="7.0" fill="#eea66f" fill-opacity="0.35"/>
  <rect x="265.0" y="167.0" width="35.0" height="7.0" fill="#9cc9ea" fill-opacity="0.35"/>
  <rect x="20.0" y="174.0" width="49.0" height="7.0" fill="#9cc9ea" fill-opacity="0.35"/>
  <rect x="69.0" y="174.0" width="70.0" height="7.0" fill="#eea66f" fill-opacity="0.35"/>
  <rect x="139.0" y="174.0" width="84.0" height="7.0" fill="#9cc9ea" fill-opacity="0.35"/>
  <rect x="223.0" y="174.0" width="35.0" height="7.0" fill="#eea66f" fill-opacity="0.35"/>
  <rect x="258.0" y="174.0" width="42.0" height="7.0" fill="#9cc9ea" fill-opacity="0.35"/>
  <rect x="20.0" y="181.0" width="56.0" height="7.0" fill="#9cc9ea" fill-opacity="0.35"/>
  <rect x="76.0" y="181.0" width="63.0" height="7.0" fill="#eea66f" fill-opacity="0.35"/>
  <rect x="139.0" y="181.0" width="84.0" height="7.0" fill="#9cc9ea" fill-opacity="0.35"/>
  <rect x="223.0" y="181.0" width="28.0" height="7.0" fill="#eea66f" fill-opacity="0.35"/>
  <rect x="251.0" y="181.0" width="49.0" height="7.0" fill="#9cc9ea" fill-opacity="0.35"/>
  <rect x="20.0" y="188.0" width="70.0" height="7.0" fill="#9cc9ea" fill-opacity="0.35"/>
  <rect x="90.0" y="188.0" width="42.0" height="7.0" fill="#eea66f" fill-opacity="0.35"/>
  <rect x="132.0" y="188.0" width="91.0" height="7.0" fill="#9cc9ea" fill-opacity="0.35"/>
  <rect x="223.0" y="188.0" width="21.0" height="7.0" fill="#eea66f" fill-opacity="0.35"/>
  <rect x="244.0" y="188.0" width="56.0" height="7.0" fill="#9cc9ea" fill-opacity="0.35"/>
  <rect x="20.0" y="195.0" width="84.0" height="7.0" fill="#9cc9ea" fill-opacity="0.35"/>
  <rect x="104.0" y="195.0" width="28.0" height="7.0" fill="#eea66f" fill-opacity="0.35"/>
  <rect x="132.0" y="195.0" width="91.0" height="7.0" fill="#9cc9ea" fill-opacity="0.35"/>
  <rect x="223.0" y="195.0" width="21.0" height="7.0" fill="#eea66f" fill-opacity="0.35"/>
  <rect x="244.0" y="195.0" width="56.0" height="7.0" fill="#9cc9ea" fill-opacity="0.35"/>
  <rect x="20.0" y="202.0" width="91.0" height="7.0" fill="#9cc9ea" fill-opacity="0.35"/>
  <rect x="111.0" y="202.0" width="14.0" height="7.0" fill="#eea66f" fill-opacity="0.35"/>
  <rect x="125.0" y="202.0" width="98.0" height="7.0" fill="#9cc9ea" fill-opacity="0.35"/>
  <rect x="223.0" y="202.0" width="21.0" height="7.0" fill="#eea66f" fill-opacity="0.35"/>
  <rect x="244.0" y="202.0" width="56.0" height="7.0" fill="#9cc9ea" fill-opacity="0.35"/>
  <rect x="20.0" y="209.0" width="98.0" height="7.0" fill="#9cc9ea" fill-opacity="0.35"/>
  <rect x="118.0" y="209.0" width="126.0" height="7.0" fill="#eea66f" fill-opacity="0.35"/>
  <rect x="244.0" y="209.0" width="56.0" height="7.0" fill="#9cc9ea" fill-opacity="0.35"/>
  <rect x="20.0" y="216.0" width="98.0" height="7.0" fill="#9cc9ea" fill-opacity="0.35"/>
  <rect x="118.0" y="216.0" width="126.0" height="7.0" fill="#eea66f" fill-opacity="0.35"/>
  <rect x="244.0" y="216.0" width="56.0" height="7.0" fill="#9cc9ea" fill-opacity="0.35"/>
  <rect x="20.0" y="223.0" width="98.0" height="7.0" fill="#9cc9ea" fill-opacity="0.35"/>
  <rect x="118.0" y="223.0" width="119.0" height="7.0" fill="#eea66f" fill-opacity="0.35"/>
  <rect x="237.0" y="223.0" width="63.0" height="7.0" fill="#9cc9ea" fill-opacity="0.35"/>
  <rect x="20.0" y="230.0" width="98.0" height="7.0" fill="#9cc9ea" fill-opacity="0.35"/>
  <rect x="118.0" y="230.0" width="112.0" height="7.0" fill="#eea66f" fill-opacity="0.35"/>
  <rect x="230.0" y="230.0" width="70.0" height="7.0" fill="#9cc9ea" fill-opacity="0.35"/>
  <rect x="20.0" y="237.0" width="119.0" height="7.0" fill="#9cc9ea" fill-opacity="0.35"/>
  <rect x="139.0" y="237.0" width="63.0" height="7.0" fill="#eea66f" fill-opacity="0.35"/>
  <rect x="202.0" y="237.0" width="98.0" height="7.0" fill="#9cc9ea" fill-opacity="0.35"/>
  <rect x="20.0" y="244.0" width="147.0" height="7.0" fill="#9cc9ea" fill-opacity="0.35"/>
  <rect x="167.0" y="244.0" width="7.0" height="7.0" fill="#eea66f" fill-opacity="0.35"/>
  <rect x="174.0" y="244.0" width="126.0" height="7.0" fill="#9cc9ea" fill-opacity="0.35"/>
  <rect x="20.0" y="251.0" width="280.0" height="7.0" fill="#9cc9ea" fill-opacity="0.35"/>
  <rect x="20.0" y="258.0" width="280.0" height="7.0" fill="#9cc9ea" fill-opacity="0.35"/>
  <rect x="20.0" y="265.0" width="280.0" height="7.0" fill="#9cc9ea" fill-opacity="0.35"/>
  <rect x="20.0" y="272.0" width="280.0" height="7.0" fill="#9cc9ea" fill-opacity="0.35"/>
  <rect x="20.0" y="279.0" width="280.0" height="7.0" fill="#9cc9ea" fill-opacity="0.35"/>
  <rect x="20.0" y="286.0" width="280.0" height="7.0" fill="#9cc9ea" fill-opacity="0.35"/>
  <rect x="20.0" y="293.0" width="280.0" height="7.0" fill="#9cc9ea" fill-opacity="0.35"/>
  <circle cx="88.2" cy="124.3" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="206.0" cy="116.4" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="73.2" cy="152.6" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="198.9" cy="103.6" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="151.2" cy="205.1" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="143.9" cy="257.8" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="277.4" cy="189.7" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="175.8" cy="206.9" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="76.0" cy="201.8" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="144.5" cy="149.3" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="88.0" cy="215.8" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="210.0" cy="251.2" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="165.9" cy="201.8" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="194.1" cy="196.6" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="224.3" cy="244.1" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="213.5" cy="142.4" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="209.5" cy="257.7" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="190.5" cy="265.3" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="242.0" cy="227.3" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="97.6" cy="231.2" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="96.0" cy="230.9" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="207.5" cy="251.1" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="169.3" cy="84.8" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="156.3" cy="81.4" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="139.9" cy="193.5" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="90.8" cy="222.6" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="187.0" cy="257.8" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="272.2" cy="164.0" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="218.5" cy="154.0" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="171.4" cy="87.7" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="74.5" cy="177.5" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="121.5" cy="92.6" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="217.1" cy="136.8" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="279.3" cy="180.2" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="72.8" cy="184.8" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="130.1" cy="170.0" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="95.5" cy="121.6" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="83.4" cy="132.9" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="209.4" cy="119.5" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="195.9" cy="196.6" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="163.2" cy="86.3" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="88.9" cy="133.8" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="199.7" cy="189.4" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="85.1" cy="212.4" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="159.6" cy="140.7" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="150.1" cy="259.3" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="157.2" cy="144.6" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="221.6" cy="246.6" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="182.2" cy="93.8" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="169.8" cy="89.8" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="233.8" cy="190.7" r="2.6" fill="#eea66f" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="112.7" cy="197.1" r="2.6" fill="#eea66f" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="246.0" cy="174.3" r="2.6" fill="#eea66f" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="126.1" cy="211.1" r="2.6" fill="#eea66f" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="171.2" cy="118.3" r="2.6" fill="#eea66f" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="169.4" cy="60.8" r="2.6" fill="#eea66f" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="46.4" cy="137.5" r="2.6" fill="#eea66f" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="141.4" cy="117.5" r="2.6" fill="#eea66f" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="240.1" cy="123.4" r="2.6" fill="#eea66f" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="182.7" cy="174.1" r="2.6" fill="#eea66f" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="233.2" cy="101.3" r="2.6" fill="#eea66f" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="107.7" cy="62.2" r="2.6" fill="#eea66f" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="156.2" cy="112.0" r="2.6" fill="#eea66f" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="121.9" cy="126.2" r="2.6" fill="#eea66f" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="88.7" cy="65.5" r="2.6" fill="#eea66f" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="97.5" cy="176.9" r="2.6" fill="#eea66f" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="106.9" cy="69.1" r="2.6" fill="#eea66f" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="132.1" cy="61.4" r="2.6" fill="#eea66f" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="73.6" cy="92.8" r="2.6" fill="#eea66f" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="215.9" cy="87.1" r="2.6" fill="#eea66f" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="227.6" cy="98.0" r="2.6" fill="#eea66f" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="109.7" cy="62.1" r="2.6" fill="#eea66f" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="146.1" cy="235.8" r="2.6" fill="#eea66f" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="163.2" cy="228.1" r="2.6" fill="#eea66f" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="181.8" cy="123.6" r="2.6" fill="#eea66f" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="225.7" cy="102.9" r="2.6" fill="#eea66f" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="130.4" cy="59.0" r="2.6" fill="#eea66f" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="41.9" cy="156.1" r="2.6" fill="#eea66f" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="100.6" cy="163.7" r="2.6" fill="#eea66f" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="150.4" cy="230.7" r="2.6" fill="#eea66f" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="248.4" cy="145.7" r="2.6" fill="#eea66f" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="203.6" cy="221.6" r="2.6" fill="#eea66f" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="106.1" cy="180.5" r="2.6" fill="#eea66f" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="60.0" cy="139.6" r="2.6" fill="#eea66f" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="246.6" cy="129.4" r="2.6" fill="#eea66f" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="191.3" cy="151.9" r="2.6" fill="#eea66f" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="232.7" cy="192.6" r="2.6" fill="#eea66f" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="239.2" cy="187.9" r="2.6" fill="#eea66f" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="101.8" cy="190.8" r="2.6" fill="#eea66f" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="125.9" cy="119.3" r="2.6" fill="#eea66f" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="154.7" cy="232.9" r="2.6" fill="#eea66f" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="237.7" cy="182.5" r="2.6" fill="#eea66f" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="116.7" cy="131.4" r="2.6" fill="#eea66f" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="237.7" cy="104.3" r="2.6" fill="#eea66f" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="163.9" cy="175.3" r="2.6" fill="#eea66f" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="172.7" cy="53.4" r="2.6" fill="#eea66f" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="163.8" cy="179.3" r="2.6" fill="#eea66f" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="96.3" cy="73.8" r="2.6" fill="#eea66f" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="137.5" cy="230.9" r="2.6" fill="#eea66f" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="143.0" cy="222.2" r="2.6" fill="#eea66f" stroke="currentColor" stroke-width="0.6"/>
  <rect x="20" y="20" width="280" height="280" fill="none" stroke="currentColor" stroke-width="1"/>
  <text x="160" y="322" font-size="11.5" text-anchor="middle" fill="currentColor">2-8-1: 33 parameters, train accuracy 0.853</text>
  <rect x="340.0" y="20.0" width="280.0" height="7.0" fill="#eea66f" fill-opacity="0.35"/>
  <rect x="340.0" y="27.0" width="280.0" height="7.0" fill="#eea66f" fill-opacity="0.35"/>
  <rect x="340.0" y="34.0" width="280.0" height="7.0" fill="#eea66f" fill-opacity="0.35"/>
  <rect x="340.0" y="41.0" width="280.0" height="7.0" fill="#eea66f" fill-opacity="0.35"/>
  <rect x="340.0" y="48.0" width="280.0" height="7.0" fill="#eea66f" fill-opacity="0.35"/>
  <rect x="340.0" y="55.0" width="280.0" height="7.0" fill="#eea66f" fill-opacity="0.35"/>
  <rect x="340.0" y="62.0" width="280.0" height="7.0" fill="#eea66f" fill-opacity="0.35"/>
  <rect x="340.0" y="69.0" width="112.0" height="7.0" fill="#eea66f" fill-opacity="0.35"/>
  <rect x="452.0" y="69.0" width="35.0" height="7.0" fill="#9cc9ea" fill-opacity="0.35"/>
  <rect x="487.0" y="69.0" width="133.0" height="7.0" fill="#eea66f" fill-opacity="0.35"/>
  <rect x="340.0" y="76.0" width="84.0" height="7.0" fill="#eea66f" fill-opacity="0.35"/>
  <rect x="424.0" y="76.0" width="84.0" height="7.0" fill="#9cc9ea" fill-opacity="0.35"/>
  <rect x="508.0" y="76.0" width="112.0" height="7.0" fill="#eea66f" fill-opacity="0.35"/>
  <rect x="340.0" y="83.0" width="70.0" height="7.0" fill="#eea66f" fill-opacity="0.35"/>
  <rect x="410.0" y="83.0" width="105.0" height="7.0" fill="#9cc9ea" fill-opacity="0.35"/>
  <rect x="515.0" y="83.0" width="105.0" height="7.0" fill="#eea66f" fill-opacity="0.35"/>
  <rect x="340.0" y="90.0" width="70.0" height="7.0" fill="#eea66f" fill-opacity="0.35"/>
  <rect x="410.0" y="90.0" width="112.0" height="7.0" fill="#9cc9ea" fill-opacity="0.35"/>
  <rect x="522.0" y="90.0" width="98.0" height="7.0" fill="#eea66f" fill-opacity="0.35"/>
  <rect x="340.0" y="97.0" width="63.0" height="7.0" fill="#eea66f" fill-opacity="0.35"/>
  <rect x="403.0" y="97.0" width="126.0" height="7.0" fill="#9cc9ea" fill-opacity="0.35"/>
  <rect x="529.0" y="97.0" width="91.0" height="7.0" fill="#eea66f" fill-opacity="0.35"/>
  <rect x="340.0" y="104.0" width="56.0" height="7.0" fill="#eea66f" fill-opacity="0.35"/>
  <rect x="396.0" y="104.0" width="49.0" height="7.0" fill="#9cc9ea" fill-opacity="0.35"/>
  <rect x="445.0" y="104.0" width="56.0" height="7.0" fill="#eea66f" fill-opacity="0.35"/>
  <rect x="501.0" y="104.0" width="35.0" height="7.0" fill="#9cc9ea" fill-opacity="0.35"/>
  <rect x="536.0" y="104.0" width="84.0" height="7.0" fill="#eea66f" fill-opacity="0.35"/>
  <rect x="340.0" y="111.0" width="56.0" height="7.0" fill="#eea66f" fill-opacity="0.35"/>
  <rect x="396.0" y="111.0" width="35.0" height="7.0" fill="#9cc9ea" fill-opacity="0.35"/>
  <rect x="431.0" y="111.0" width="77.0" height="7.0" fill="#eea66f" fill-opacity="0.35"/>
  <rect x="508.0" y="111.0" width="35.0" height="7.0" fill="#9cc9ea" fill-opacity="0.35"/>
  <rect x="543.0" y="111.0" width="77.0" height="7.0" fill="#eea66f" fill-opacity="0.35"/>
  <rect x="340.0" y="118.0" width="49.0" height="7.0" fill="#eea66f" fill-opacity="0.35"/>
  <rect x="389.0" y="118.0" width="35.0" height="7.0" fill="#9cc9ea" fill-opacity="0.35"/>
  <rect x="424.0" y="118.0" width="91.0" height="7.0" fill="#eea66f" fill-opacity="0.35"/>
  <rect x="515.0" y="118.0" width="28.0" height="7.0" fill="#9cc9ea" fill-opacity="0.35"/>
  <rect x="543.0" y="118.0" width="77.0" height="7.0" fill="#eea66f" fill-opacity="0.35"/>
  <rect x="340.0" y="125.0" width="49.0" height="7.0" fill="#eea66f" fill-opacity="0.35"/>
  <rect x="389.0" y="125.0" width="35.0" height="7.0" fill="#9cc9ea" fill-opacity="0.35"/>
  <rect x="424.0" y="125.0" width="98.0" height="7.0" fill="#eea66f" fill-opacity="0.35"/>
  <rect x="522.0" y="125.0" width="28.0" height="7.0" fill="#9cc9ea" fill-opacity="0.35"/>
  <rect x="550.0" y="125.0" width="70.0" height="7.0" fill="#eea66f" fill-opacity="0.35"/>
  <rect x="340.0" y="132.0" width="49.0" height="7.0" fill="#eea66f" fill-opacity="0.35"/>
  <rect x="389.0" y="132.0" width="28.0" height="7.0" fill="#9cc9ea" fill-opacity="0.35"/>
  <rect x="417.0" y="132.0" width="42.0" height="7.0" fill="#eea66f" fill-opacity="0.35"/>
  <rect x="459.0" y="132.0" width="28.0" height="7.0" fill="#9cc9ea" fill-opacity="0.35"/>
  <rect x="487.0" y="132.0" width="35.0" height="7.0" fill="#eea66f" fill-opacity="0.35"/>
  <rect x="522.0" y="132.0" width="35.0" height="7.0" fill="#9cc9ea" fill-opacity="0.35"/>
  <rect x="557.0" y="132.0" width="63.0" height="7.0" fill="#eea66f" fill-opacity="0.35"/>
  <rect x="340.0" y="139.0" width="49.0" height="7.0" fill="#eea66f" fill-opacity="0.35"/>
  <rect x="389.0" y="139.0" width="28.0" height="7.0" fill="#9cc9ea" fill-opacity="0.35"/>
  <rect x="417.0" y="139.0" width="35.0" height="7.0" fill="#eea66f" fill-opacity="0.35"/>
  <rect x="452.0" y="139.0" width="42.0" height="7.0" fill="#9cc9ea" fill-opacity="0.35"/>
  <rect x="494.0" y="139.0" width="28.0" height="7.0" fill="#eea66f" fill-opacity="0.35"/>
  <rect x="522.0" y="139.0" width="35.0" height="7.0" fill="#9cc9ea" fill-opacity="0.35"/>
  <rect x="557.0" y="139.0" width="63.0" height="7.0" fill="#eea66f" fill-opacity="0.35"/>
  <rect x="340.0" y="146.0" width="42.0" height="7.0" fill="#eea66f" fill-opacity="0.35"/>
  <rect x="382.0" y="146.0" width="28.0" height="7.0" fill="#9cc9ea" fill-opacity="0.35"/>
  <rect x="410.0" y="146.0" width="35.0" height="7.0" fill="#eea66f" fill-opacity="0.35"/>
  <rect x="445.0" y="146.0" width="49.0" height="7.0" fill="#9cc9ea" fill-opacity="0.35"/>
  <rect x="494.0" y="146.0" width="28.0" height="7.0" fill="#eea66f" fill-opacity="0.35"/>
  <rect x="522.0" y="146.0" width="42.0" height="7.0" fill="#9cc9ea" fill-opacity="0.35"/>
  <rect x="564.0" y="146.0" width="56.0" height="7.0" fill="#eea66f" fill-opacity="0.35"/>
  <rect x="340.0" y="153.0" width="42.0" height="7.0" fill="#eea66f" fill-opacity="0.35"/>
  <rect x="382.0" y="153.0" width="21.0" height="7.0" fill="#9cc9ea" fill-opacity="0.35"/>
  <rect x="403.0" y="153.0" width="35.0" height="7.0" fill="#eea66f" fill-opacity="0.35"/>
  <rect x="438.0" y="153.0" width="42.0" height="7.0" fill="#9cc9ea" fill-opacity="0.35"/>
  <rect x="480.0" y="153.0" width="42.0" height="7.0" fill="#eea66f" fill-opacity="0.35"/>
  <rect x="522.0" y="153.0" width="49.0" height="7.0" fill="#9cc9ea" fill-opacity="0.35"/>
  <rect x="571.0" y="153.0" width="49.0" height="7.0" fill="#eea66f" fill-opacity="0.35"/>
  <rect x="340.0" y="160.0" width="35.0" height="7.0" fill="#eea66f" fill-opacity="0.35"/>
  <rect x="375.0" y="160.0" width="28.0" height="7.0" fill="#9cc9ea" fill-opacity="0.35"/>
  <rect x="403.0" y="160.0" width="35.0" height="7.0" fill="#eea66f" fill-opacity="0.35"/>
  <rect x="438.0" y="160.0" width="28.0" height="7.0" fill="#9cc9ea" fill-opacity="0.35"/>
  <rect x="466.0" y="160.0" width="56.0" height="7.0" fill="#eea66f" fill-opacity="0.35"/>
  <rect x="522.0" y="160.0" width="42.0" height="7.0" fill="#9cc9ea" fill-opacity="0.35"/>
  <rect x="564.0" y="160.0" width="14.0" height="7.0" fill="#eea66f" fill-opacity="0.35"/>
  <rect x="578.0" y="160.0" width="42.0" height="7.0" fill="#9cc9ea" fill-opacity="0.35"/>
  <rect x="340.0" y="167.0" width="28.0" height="7.0" fill="#eea66f" fill-opacity="0.35"/>
  <rect x="368.0" y="167.0" width="35.0" height="7.0" fill="#9cc9ea" fill-opacity="0.35"/>
  <rect x="403.0" y="167.0" width="35.0" height="7.0" fill="#eea66f" fill-opacity="0.35"/>
  <rect x="438.0" y="167.0" width="28.0" height="7.0" fill="#9cc9ea" fill-opacity="0.35"/>
  <rect x="466.0" y="167.0" width="56.0" height="7.0" fill="#eea66f" fill-opacity="0.35"/>
  <rect x="522.0" y="167.0" width="28.0" height="7.0" fill="#9cc9ea" fill-opacity="0.35"/>
  <rect x="550.0" y="167.0" width="35.0" height="7.0" fill="#eea66f" fill-opacity="0.35"/>
  <rect x="585.0" y="167.0" width="35.0" height="7.0" fill="#9cc9ea" fill-opacity="0.35"/>
  <rect x="340.0" y="174.0" width="28.0" height="7.0" fill="#eea66f" fill-opacity="0.35"/>
  <rect x="368.0" y="174.0" width="35.0" height="7.0" fill="#9cc9ea" fill-opacity="0.35"/>
  <rect x="403.0" y="174.0" width="35.0" height="7.0" fill="#eea66f" fill-opacity="0.35"/>
  <rect x="438.0" y="174.0" width="28.0" height="7.0" fill="#9cc9ea" fill-opacity="0.35"/>
  <rect x="466.0" y="174.0" width="42.0" height="7.0" fill="#eea66f" fill-opacity="0.35"/>
  <rect x="508.0" y="174.0" width="42.0" height="7.0" fill="#9cc9ea" fill-opacity="0.35"/>
  <rect x="550.0" y="174.0" width="28.0" height="7.0" fill="#eea66f" fill-opacity="0.35"/>
  <rect x="578.0" y="174.0" width="42.0" height="7.0" fill="#9cc9ea" fill-opacity="0.35"/>
  <rect x="340.0" y="181.0" width="21.0" height="7.0" fill="#eea66f" fill-opacity="0.35"/>
  <rect x="361.0" y="181.0" width="49.0" height="7.0" fill="#9cc9ea" fill-opacity="0.35"/>
  <rect x="410.0" y="181.0" width="35.0" height="7.0" fill="#eea66f" fill-opacity="0.35"/>
  <rect x="445.0" y="181.0" width="35.0" height="7.0" fill="#9cc9ea" fill-opacity="0.35"/>
  <rect x="480.0" y="181.0" width="21.0" height="7.0" fill="#eea66f" fill-opacity="0.35"/>
  <rect x="501.0" y="181.0" width="42.0" height="7.0" fill="#9cc9ea" fill-opacity="0.35"/>
  <rect x="543.0" y="181.0" width="35.0" height="7.0" fill="#eea66f" fill-opacity="0.35"/>
  <rect x="578.0" y="181.0" width="42.0" height="7.0" fill="#9cc9ea" fill-opacity="0.35"/>
  <rect x="340.0" y="188.0" width="7.0" height="7.0" fill="#eea66f" fill-opacity="0.35"/>
  <rect x="347.0" y="188.0" width="63.0" height="7.0" fill="#9cc9ea" fill-opacity="0.35"/>
  <rect x="410.0" y="188.0" width="35.0" height="7.0" fill="#eea66f" fill-opacity="0.35"/>
  <rect x="445.0" y="188.0" width="91.0" height="7.0" fill="#9cc9ea" fill-opacity="0.35"/>
  <rect x="536.0" y="188.0" width="35.0" height="7.0" fill="#eea66f" fill-opacity="0.35"/>
  <rect x="571.0" y="188.0" width="49.0" height="7.0" fill="#9cc9ea" fill-opacity="0.35"/>
  <rect x="340.0" y="195.0" width="77.0" height="7.0" fill="#9cc9ea" fill-opacity="0.35"/>
  <rect x="417.0" y="195.0" width="35.0" height="7.0" fill="#eea66f" fill-opacity="0.35"/>
  <rect x="452.0" y="195.0" width="84.0" height="7.0" fill="#9cc9ea" fill-opacity="0.35"/>
  <rect x="536.0" y="195.0" width="35.0" height="7.0" fill="#eea66f" fill-opacity="0.35"/>
  <rect x="571.0" y="195.0" width="49.0" height="7.0" fill="#9cc9ea" fill-opacity="0.35"/>
  <rect x="340.0" y="202.0" width="77.0" height="7.0" fill="#9cc9ea" fill-opacity="0.35"/>
  <rect x="417.0" y="202.0" width="35.0" height="7.0" fill="#eea66f" fill-opacity="0.35"/>
  <rect x="452.0" y="202.0" width="70.0" height="7.0" fill="#9cc9ea" fill-opacity="0.35"/>
  <rect x="522.0" y="202.0" width="49.0" height="7.0" fill="#eea66f" fill-opacity="0.35"/>
  <rect x="571.0" y="202.0" width="49.0" height="7.0" fill="#9cc9ea" fill-opacity="0.35"/>
  <rect x="340.0" y="209.0" width="84.0" height="7.0" fill="#9cc9ea" fill-opacity="0.35"/>
  <rect x="424.0" y="209.0" width="42.0" height="7.0" fill="#eea66f" fill-opacity="0.35"/>
  <rect x="466.0" y="209.0" width="49.0" height="7.0" fill="#9cc9ea" fill-opacity="0.35"/>
  <rect x="515.0" y="209.0" width="49.0" height="7.0" fill="#eea66f" fill-opacity="0.35"/>
  <rect x="564.0" y="209.0" width="56.0" height="7.0" fill="#9cc9ea" fill-opacity="0.35"/>
  <rect x="340.0" y="216.0" width="84.0" height="7.0" fill="#9cc9ea" fill-opacity="0.35"/>
  <rect x="424.0" y="216.0" width="63.0" height="7.0" fill="#eea66f" fill-opacity="0.35"/>
  <rect x="487.0" y="216.0" width="21.0" height="7.0" fill="#9cc9ea" fill-opacity="0.35"/>
  <rect x="508.0" y="216.0" width="49.0" height="7.0" fill="#eea66f" fill-opacity="0.35"/>
  <rect x="557.0" y="216.0" width="63.0" height="7.0" fill="#9cc9ea" fill-opacity="0.35"/>
  <rect x="340.0" y="223.0" width="91.0" height="7.0" fill="#9cc9ea" fill-opacity="0.35"/>
  <rect x="431.0" y="223.0" width="119.0" height="7.0" fill="#eea66f" fill-opacity="0.35"/>
  <rect x="550.0" y="223.0" width="70.0" height="7.0" fill="#9cc9ea" fill-opacity="0.35"/>
  <rect x="340.0" y="230.0" width="98.0" height="7.0" fill="#9cc9ea" fill-opacity="0.35"/>
  <rect x="438.0" y="230.0" width="98.0" height="7.0" fill="#eea66f" fill-opacity="0.35"/>
  <rect x="536.0" y="230.0" width="84.0" height="7.0" fill="#9cc9ea" fill-opacity="0.35"/>
  <rect x="340.0" y="237.0" width="112.0" height="7.0" fill="#9cc9ea" fill-opacity="0.35"/>
  <rect x="452.0" y="237.0" width="70.0" height="7.0" fill="#eea66f" fill-opacity="0.35"/>
  <rect x="522.0" y="237.0" width="98.0" height="7.0" fill="#9cc9ea" fill-opacity="0.35"/>
  <rect x="340.0" y="244.0" width="140.0" height="7.0" fill="#9cc9ea" fill-opacity="0.35"/>
  <rect x="480.0" y="244.0" width="21.0" height="7.0" fill="#eea66f" fill-opacity="0.35"/>
  <rect x="501.0" y="244.0" width="119.0" height="7.0" fill="#9cc9ea" fill-opacity="0.35"/>
  <rect x="340.0" y="251.0" width="280.0" height="7.0" fill="#9cc9ea" fill-opacity="0.35"/>
  <rect x="340.0" y="258.0" width="280.0" height="7.0" fill="#9cc9ea" fill-opacity="0.35"/>
  <rect x="340.0" y="265.0" width="280.0" height="7.0" fill="#9cc9ea" fill-opacity="0.35"/>
  <rect x="340.0" y="272.0" width="280.0" height="7.0" fill="#9cc9ea" fill-opacity="0.35"/>
  <rect x="340.0" y="279.0" width="280.0" height="7.0" fill="#9cc9ea" fill-opacity="0.35"/>
  <rect x="340.0" y="286.0" width="280.0" height="7.0" fill="#9cc9ea" fill-opacity="0.35"/>
  <rect x="340.0" y="293.0" width="280.0" height="7.0" fill="#9cc9ea" fill-opacity="0.35"/>
  <circle cx="408.2" cy="124.3" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="526.0" cy="116.4" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="393.2" cy="152.6" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="518.9" cy="103.6" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="471.2" cy="205.1" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="463.9" cy="257.8" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="597.4" cy="189.7" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="495.8" cy="206.9" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="396.0" cy="201.8" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="464.5" cy="149.3" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="408.0" cy="215.8" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="530.0" cy="251.2" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="485.9" cy="201.8" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="514.1" cy="196.6" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="544.3" cy="244.1" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="533.5" cy="142.4" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="529.5" cy="257.7" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="510.5" cy="265.3" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="562.0" cy="227.3" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="417.6" cy="231.2" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="416.0" cy="230.9" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="527.5" cy="251.1" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="489.3" cy="84.8" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="476.3" cy="81.4" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="459.9" cy="193.5" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="410.8" cy="222.6" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="507.0" cy="257.8" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="592.2" cy="164.0" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="538.5" cy="154.0" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="491.4" cy="87.7" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="394.5" cy="177.5" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="441.5" cy="92.6" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="537.1" cy="136.8" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="599.3" cy="180.2" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="392.8" cy="184.8" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="450.1" cy="170.0" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="415.5" cy="121.6" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="403.4" cy="132.9" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="529.4" cy="119.5" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="515.9" cy="196.6" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="483.2" cy="86.3" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="408.9" cy="133.8" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="519.7" cy="189.4" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="405.1" cy="212.4" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="479.6" cy="140.7" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="470.1" cy="259.3" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="477.2" cy="144.6" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="541.6" cy="246.6" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="502.2" cy="93.8" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="489.8" cy="89.8" r="2.6" fill="#9cc9ea" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="553.8" cy="190.7" r="2.6" fill="#eea66f" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="432.7" cy="197.1" r="2.6" fill="#eea66f" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="566.0" cy="174.3" r="2.6" fill="#eea66f" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="446.1" cy="211.1" r="2.6" fill="#eea66f" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="491.2" cy="118.3" r="2.6" fill="#eea66f" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="489.4" cy="60.8" r="2.6" fill="#eea66f" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="366.4" cy="137.5" r="2.6" fill="#eea66f" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="461.4" cy="117.5" r="2.6" fill="#eea66f" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="560.1" cy="123.4" r="2.6" fill="#eea66f" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="502.7" cy="174.1" r="2.6" fill="#eea66f" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="553.2" cy="101.3" r="2.6" fill="#eea66f" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="427.7" cy="62.2" r="2.6" fill="#eea66f" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="476.2" cy="112.0" r="2.6" fill="#eea66f" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="441.9" cy="126.2" r="2.6" fill="#eea66f" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="408.7" cy="65.5" r="2.6" fill="#eea66f" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="417.5" cy="176.9" r="2.6" fill="#eea66f" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="426.9" cy="69.1" r="2.6" fill="#eea66f" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="452.1" cy="61.4" r="2.6" fill="#eea66f" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="393.6" cy="92.8" r="2.6" fill="#eea66f" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="535.9" cy="87.1" r="2.6" fill="#eea66f" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="547.6" cy="98.0" r="2.6" fill="#eea66f" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="429.7" cy="62.1" r="2.6" fill="#eea66f" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="466.1" cy="235.8" r="2.6" fill="#eea66f" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="483.2" cy="228.1" r="2.6" fill="#eea66f" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="501.8" cy="123.6" r="2.6" fill="#eea66f" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="545.7" cy="102.9" r="2.6" fill="#eea66f" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="450.4" cy="59.0" r="2.6" fill="#eea66f" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="361.9" cy="156.1" r="2.6" fill="#eea66f" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="420.6" cy="163.7" r="2.6" fill="#eea66f" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="470.4" cy="230.7" r="2.6" fill="#eea66f" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="568.4" cy="145.7" r="2.6" fill="#eea66f" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="523.6" cy="221.6" r="2.6" fill="#eea66f" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="426.1" cy="180.5" r="2.6" fill="#eea66f" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="380.0" cy="139.6" r="2.6" fill="#eea66f" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="566.6" cy="129.4" r="2.6" fill="#eea66f" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="511.3" cy="151.9" r="2.6" fill="#eea66f" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="552.7" cy="192.6" r="2.6" fill="#eea66f" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="559.2" cy="187.9" r="2.6" fill="#eea66f" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="421.8" cy="190.8" r="2.6" fill="#eea66f" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="445.9" cy="119.3" r="2.6" fill="#eea66f" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="474.7" cy="232.9" r="2.6" fill="#eea66f" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="557.7" cy="182.5" r="2.6" fill="#eea66f" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="436.7" cy="131.4" r="2.6" fill="#eea66f" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="557.7" cy="104.3" r="2.6" fill="#eea66f" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="483.9" cy="175.3" r="2.6" fill="#eea66f" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="492.7" cy="53.4" r="2.6" fill="#eea66f" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="483.8" cy="179.3" r="2.6" fill="#eea66f" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="416.3" cy="73.8" r="2.6" fill="#eea66f" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="457.5" cy="230.9" r="2.6" fill="#eea66f" stroke="currentColor" stroke-width="0.6"/>
  <circle cx="463.0" cy="222.2" r="2.6" fill="#eea66f" stroke="currentColor" stroke-width="0.6"/>
  <rect x="340" y="20" width="280" height="280" fill="none" stroke="currentColor" stroke-width="1"/>
  <text x="480" y="322" font-size="11.5" text-anchor="middle" fill="currentColor">2-32-32-1: 1185 parameters, train accuracy 1.000</text>
</svg>
<figcaption>Decision regions computed from the trained networks of the program (orange region: the network says class 1;
dots: every fourth training point, coloured by its true class). A ReLU network's boundary is made of straight
pieces; with enough units the pieces follow the spirals.</figcaption>
</figure>

The ASCII map printed at the end of the program, and the picture above, show the same thing: a ReLU network divides
the plane into regions on which it is linear (each hidden unit adds a line where it switches on or off), and the
decision boundary is a chain of straight segments through those regions. With more units there are more regions
and the chain can bend more often. The test accuracy of 0.985 says the curve it found is not just a memorisation of
the training points: between the training points the network draws the spiral we would draw.

### Things to try

The program is small enough to experiment with, and each experiment previews [Chapter 16](16-Training-Deep-Networks.md):

- Change the activation to sigmoid (and its derivative): training becomes much slower.
- Initialise the weights with standard deviation 1 instead of $\sqrt{2/n_{\text{in}}}$, or 0.01: the deeper network
  trains worse or not at all.
- Use plain gradient descent instead of Adam: you will need a much larger learning rate, and a careful one.
- Shrink the training set to 50 points: training accuracy stays at 1.0, test accuracy drops: overfitting
  ([Chapter 8](08-Overfitting-and-Regularization.md)).

**In practice:** nobody writes backpropagation by hand for real networks. PyTorch's `autograd`, JAX's `grad` and
TensorFlow's `GradientTape` are reverse-mode automatic differentiation engines on tensors, the industrial version of
our `Value` class; `torch.nn.Linear` is one layer of 15.3, and `torch.optim.Adam` is the optimiser of Chapter 5.
scikit-learn's `MLPClassifier` trains small networks like ours on the CPU.

## Check yourself

??? question "1. Show that no single threshold neuron computes the function that is 1 exactly when $x_1 = x_2$ (XNOR) on bits $x_1, x_2$."

    XNOR is $1 - \text{XOR}$. If $\mathrm{step}(w^\top x + b)$ computed XNOR, then the neuron with weights $-w$ and bias
    $-b$ would output 1 exactly when $w^\top x + b < 0$, which is XNOR's complement, XOR, at least on inputs where
    $w^\top x + b \ne 0$. Since there are only four inputs, we can shift $b$ slightly to avoid equality without changing
    any output. So a neuron for XNOR would give a neuron for XOR, which 15.1 proved impossible. (Or redo the four
    inequalities directly: $b > 0$, $w_2 + b \le 0$, $w_1 + b \le 0$, $w_1 + w_2 + b > 0$, and add the middle two.)

??? question "2. Prove that $\tanh(a) = 2\sigma(2a) - 1$ and deduce $\tanh'(a) = 1 - \tanh^2(a)$ from $\sigma' = \sigma(1-\sigma)$."

    $2\sigma(2a) - 1 = \frac{2}{1 + e^{-2a}} - 1 = \frac{1 - e^{-2a}}{1 + e^{-2a}} = \frac{e^a - e^{-a}}{e^a + e^{-a}} = \tanh a$
    (multiply top and bottom by $e^a$). Differentiate: $\tanh'(a) = 4\sigma'(2a) = 4\sigma(2a)(1 - \sigma(2a))$. With
    $s = \sigma(2a) = (1 + \tanh a)/2$, this is $4 \cdot \frac{1+\tanh a}{2}\cdot\frac{1-\tanh a}{2} = 1 - \tanh^2 a$.

??? question "3. How many parameters does a 784-256-128-10 MLP have? About how many multiply-adds does a forward pass of a batch of 64 cost?"

    Weights $784\cdot256 + 256\cdot128 + 128\cdot10 = 200704 + 32768 + 1280 = 234752$; biases $256 + 128 + 10 = 394$;
    total 235146. A forward pass costs about $64 \times 234752 \approx 1.5 \times 10^7$ multiply-adds, and the
    backward pass about twice that.

??? question "4. A network computes $s = w_2\,\mathrm{relu}(w_1x + b_1) + b_2$ with $x = 1$, $w_1 = 2$, $b_1 = -1$, $w_2 = -3$, $b_2 = 0.5$, and the loss is $L = \frac12(s - y)^2$ with $y = 1$. Compute every gradient by hand."

    Forward: $a = 2 - 1 = 1$, $h = 1$, $s = -3 + 0.5 = -2.5$, $L = \frac12(-3.5)^2 = 6.125$. Backward:
    $\delta_s = s - y = -3.5$. $\partial L/\partial w_2 = h\,\delta_s = -3.5$; $\partial L/\partial b_2 = -3.5$.
    $\partial L/\partial h = w_2\delta_s = 10.5$; ReLU is active ($a > 0$) so $\delta_a = 10.5$.
    $\partial L/\partial w_1 = x\,\delta_a = 10.5$; $\partial L/\partial b_1 = 10.5$. Gradient descent would therefore
    decrease $w_1$ and $b_1$ and increase $w_2$ and $b_2$.

??? question "5. In the same network, change $b_1$ to $-3$. What are the gradients now, and what does this illustrate?"

    Now $a = -1$, $h = 0$, $s = 0.5$, $\delta_s = -0.5$. $\partial L/\partial w_2 = h\delta_s = 0$,
    $\partial L/\partial b_2 = -0.5$, and since $a < 0$ the ReLU passes no gradient: $\partial L/\partial w_1 =
    \partial L/\partial b_1 = 0$. The hidden unit is switched off for this input and learns nothing from it. If that
    happens for every training input, the unit is a dead ReLU.

??? question "6. Why does the `Value` engine use `self.grad += ...` rather than `self.grad = ...`? Give the smallest example where `=` gives a wrong answer."

    A value used in several places receives a gradient contribution from each use, and the chain rule adds them.
    With $f = a \cdot a$ at $a = 3$, the multiplication node calls `_backward` once, which with `=` would set
    `a.grad = 3` twice (once as each factor), giving 3; the true derivative is $2a = 6$, which `+=` gets by adding
    $3 + 3$. This is also why gradients must be reset to zero before each training step.

??? question "7. Write the code: add a `sigmoid` method to the `Value` class, and check its gradient on $\sigma(2a + 1)$ at $a = 0.3$."

    The local derivative is $\sigma(1 - \sigma)$, which can use the stored output.

    ```python
    import math
    from ch15_autodiff import Value

    def sigmoid(self):
        s = 1 / (1 + math.exp(-self.data))
        out = Value(s, (self,), "sigmoid")
        def backward():
            self.grad += s * (1 - s) * out.grad
        out._backward = backward
        return out

    Value.sigmoid = sigmoid
    a = Value(0.3)
    y = (2 * a + 1).sigmoid()
    y.backward()
    s = 1 / (1 + math.exp(-1.6))
    print(a.grad, 2 * s * (1 - s))   # both 0.27952758...
    ```

??? question "8. Forward or reverse mode? (a) The gradient of a loss with respect to a million weights. (b) The derivatives of a 3-D robot arm's 1000 sampled positions with respect to its single joint angle. (c) The full Jacobian of a map from $\mathbb{R}^{100}$ to $\mathbb{R}^{100}$."

    (a) Reverse mode: one output, many inputs; one backward pass. (b) Forward mode: one input, many outputs; one
    forward pass carrying derivatives. (c) Either needs about 100 passes (100 forward passes, one per input, or 100
    backward passes, one per output); the costs are similar, and other considerations (memory: reverse mode stores the
    graph) decide.

??? question "9. A one-hidden-layer ReLU network on $\mathbb{R}$ with $N$ units is piecewise linear. At most how many linear pieces can it have? Build a network with 3 units that computes the 'hat' function that is 0 outside $[0, 2]$, rises linearly to 1 at $x = 1$, and falls back to 0 at $x = 2$."

    Each unit $\max(0, w_jx + b_j)$ has one bend, at $x = -b_j/w_j$, so the sum has at most $N$ bends and at most
    $N + 1$ pieces. The hat is $\mathrm{relu}(x) - 2\,\mathrm{relu}(x - 1) + \mathrm{relu}(x - 2)$: slope 0 left of 0,
    slope 1 on $[0,1]$, slope $1 - 2 = -1$ on $[1, 2]$, slope $-1 + 1 = 0$ after 2, and value 0 at both ends. Adding
    shifted, scaled hats gives any piecewise-linear interpolant, the ReLU construction of 15.6.

??? question "10. (Hard) A deep ReLU network on $[0,1]$: let $T(x) = 2\,\mathrm{relu}(x) - 4\,\mathrm{relu}(x - 1/2)$ (the 'tent' map, which on $[0,1]$ goes up from 0 to 1 and back down to 0). Show that composing $T$ with itself $k$ times gives a sawtooth with $2^{k-1}$ teeth, using only $2k$ ReLU units in $k$ layers. Why does a one-hidden-layer network need at least about $2^k$ units for the same function?"

    On $[0,1]$, $T(x) = 2x$ for $x \le 1/2$ and $2 - 2x$ for $x \ge 1/2$, mapping each half onto $[0,1]$. So $T \circ T$
    maps each quarter onto $[0,1]$, alternately up and down: 2 teeth. By induction, $T^{(k)}$ maps each of the $2^k$
    intervals of length $2^{-k}$ onto $[0,1]$, alternately increasing and decreasing, which is $2^{k-1}$ teeth with
    $2^k$ linear pieces. Each layer uses the 2 units of $T$, so $k$ layers use $2k$ units. A one-hidden-layer ReLU
    network with $N$ units has at most $N + 1$ linear pieces (exercise 9), so to equal $T^{(k)}$ it needs
    $N \ge 2^k - 1$. This is the idea behind Telgarsky's depth-separation theorem.

??? question "11. (Hard) Show that for softmax probabilities $p_k = e^{s_k}/\sum_j e^{s_j}$ and cross-entropy $L = -\sum_k y_k\log p_k$ with a one-hot $y$, the gradient is $\partial L/\partial s = p - y$."

    $\log p_k = s_k - \log\sum_j e^{s_j}$, so $L = -\sum_k y_ks_k + (\sum_k y_k)\log\sum_j e^{s_j} = -\sum_k y_ks_k + \log\sum_j e^{s_j}$,
    since the $y_k$ sum to 1. Differentiate with respect to $s_m$: $-y_m + e^{s_m}/\sum_j e^{s_j} = p_m - y_m$. The
    simplicity is the reason softmax and cross-entropy are always paired, and why frameworks fuse them into one
    numerically stable operation.

## What you learned

- A single neuron draws one hyperplane, so it cannot compute XOR; a hidden layer learns new features (OR and AND)
  in which the problem becomes linearly separable.
- Activations must be non-linear, or the layers collapse into one linear map; sigmoid and tanh saturate, ReLU does
  not for positive inputs and is the default.
- A forward pass is a chain of matrix products and elementwise functions, done for a whole batch at once.
- Backpropagation applies the chain rule from the loss backwards: the weight gradient is input times error signal,
  and the signal passes down through $W^\top$ and $\phi'$; it costs about twice a forward pass.
- Reverse-mode automatic differentiation records a computational graph and visits it in reverse topological order,
  adding gradient contributions along every path; a hundred lines of Python suffice to train a network on it.
- One hidden layer can approximate any continuous function on a box (Cybenko, Hornik, Leshno et al.), but the
  theorem says nothing about size, learnability or generalisation, and depth can be exponentially more efficient.
- An MLP trained with backpropagation and Adam separates two spirals; its ReLU boundary is a chain of straight pieces.

**Next:** [Chapter 16](16-Training-Deep-Networks.md), which makes deep networks actually train: initialisation,
normalisation, regularisation, residual connections and how to debug a training run.

## Further reading

- I. Goodfellow, Y. Bengio and A. Courville, *Deep Learning*, 2016, chapter 6 (deep feed-forward networks,
  back-propagation and computational graphs, universal approximation).
- C. Bishop, *Pattern Recognition and Machine Learning*, 2006, chapter 5 (neural networks, error backpropagation);
  and C. Bishop and H. Bishop, *Deep Learning: Foundations and Concepts*, 2024, chapters 6 to 8.
- K. Murphy, *Probabilistic Machine Learning: An Introduction*, 2022, chapter 13 (neural networks for tabular data,
  backpropagation).
- M. Nielsen, *Neural Networks and Deep Learning*, 2015 (free online), chapters 2 and 4 (backpropagation, a visual
  proof of universality).
- W. McCulloch and W. Pitts, "A Logical Calculus of the Ideas Immanent in Nervous Activity", *Bulletin of
  Mathematical Biophysics*, 1943; F. Rosenblatt, "The Perceptron: A Probabilistic Model for Information Storage and
  Organization in the Brain", *Psychological Review*, 1958; M. Minsky and S. Papert, *Perceptrons*, 1969.
- S. Linnainmaa, master's thesis on the representation of the cumulative rounding error of an algorithm as a Taylor
  expansion of the local rounding errors, University of Helsinki, 1970; P. Werbos, *Beyond Regression*, PhD thesis,
  Harvard, 1974.
- D. Rumelhart, G. Hinton and R. Williams, "Learning Representations by Back-propagating Errors", *Nature*, 1986.
- A. Griewank and A. Walther, *Evaluating Derivatives: Principles and Techniques of Algorithmic Differentiation*,
  2nd ed., 2008; A. Baydin, B. Pearlmutter, A. Radul and J. Siskind, "Automatic Differentiation in Machine Learning:
  a Survey", *Journal of Machine Learning Research*, 2018.
- G. Cybenko, "Approximation by Superpositions of a Sigmoidal Function", *Mathematics of Control, Signals and
  Systems*, 1989; K. Hornik, M. Stinchcombe and H. White, "Multilayer Feedforward Networks are Universal
  Approximators", *Neural Networks*, 1989; K. Hornik, "Approximation Capabilities of Multilayer Feedforward
  Networks", *Neural Networks*, 1991; M. Leshno, V. Lin, A. Pinkus and S. Schocken, "Multilayer Feedforward Networks
  with a Nonpolynomial Activation Function Can Approximate Any Function", *Neural Networks*, 1993.
- A. Barron, "Universal Approximation Bounds for Superpositions of a Sigmoidal Function", *IEEE Transactions on
  Information Theory*, 1993; M. Telgarsky, "Benefits of Depth in Neural Networks", COLT 2016; R. Eldan and O. Shamir,
  "The Power of Depth for Feedforward Neural Networks", COLT 2016.
- V. Nair and G. Hinton, "Rectified Linear Units Improve Restricted Boltzmann Machines", ICML 2010; X. Glorot,
  A. Bordes and Y. Bengio, "Deep Sparse Rectifier Neural Networks", AISTATS 2011; D. Hendrycks and K. Gimpel,
  "Gaussian Error Linear Units (GELUs)", arXiv 2016.
- On this site: [Topological sort](../../graphs/topological-sort.md) and [Depth-first search](../../graphs/dfs.md)
  (the order the engine's backward pass uses); [Chapter 15 of the Algorithms book](../algorithms/15-Graphs-and-Graph-Search.md)
  on directed acyclic graphs; [Chapter 6](06-Classification-and-Logistic-Regression.md) for the perceptron and
  cross-entropy; [Chapter 5](05-Optimization.md) for Adam; the calculus book at
  [https://math.akadian.ca/books/](https://math.akadian.ca/books/).
