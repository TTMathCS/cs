# 16. Training deep networks well

*Chapter 15 trained a network with two hidden layers and it simply worked. Add twenty more layers and, done
naively, it stops working: the loss sits still, or jumps to infinity, or the network learns the training set and
nothing else. For about twenty years this made deep networks look impractical. Then a handful of ideas, each simple
once understood, changed that: choosing the initial weights by a variance argument, normalising activations,
dropout and weight decay, sensible learning-rate schedules and clipping, and residual connections. This chapter
derives each from first principles, measures what it does with small programs, and ends with the checks
practitioners run when a training run misbehaves.*

!!! abstract "In this chapter"
    **You will learn:**

    - why gradients vanish or explode in deep networks, shown by measurement and explained by the backward recursion
    - how Xavier (Glorot) and He initialisation follow from keeping variances constant from layer to layer
    - batch normalisation and layer normalisation: the forward pass, the backward pass derived, and what is known about why they help
    - weight decay, dropout and data augmentation as regularisers, and AdamW's decoupled weight decay
    - learning-rate range tests, warmup and cosine schedules, and gradient clipping
    - residual connections, and why an identity path lets gradients reach the first layers of very deep networks
    - a practical routine for debugging training: the initial loss, overfitting one batch, curves and statistics

    **You need:** [Chapter 15](15-Neural-Networks-and-Backpropagation.md) (layers, backpropagation),
    [Chapter 5](05-Optimization.md) (momentum, Adam, learning rates), [Chapter 8](08-Overfitting-and-Regularization.md)
    (overfitting, ridge regression, early stopping) and [Chapter 3](03-The-Math-Toolkit.md) (expectation and
    variance). The probability book at [https://math.akadian.ca/books/](https://math.akadian.ca/books/) has more on
    variances of sums and products.

    **Levels:** 16.1 is intermediate; 16.2 and 16.3 are intermediate to advanced; 16.4 and 16.5 are intermediate;
    16.6 is advanced; 16.7 is beginner to intermediate.

## 16.1 Vanishing and exploding gradients, shown

### The backward recursion again

In [Chapter 15](15-Neural-Networks-and-Backpropagation.md) we derived how the error signal travels down a network:

$$
\delta^{(l-1)} = \Big(\delta^{(l)}\big(W^{(l)}\big)^\top\Big) \odot \phi'\big(a^{(l-1)}\big).
$$

Every layer multiplies the signal by a weight matrix and by the derivatives of the activation. Going from the top
of an $L$-layer network to the bottom, the signal is multiplied by $L$ such factors. A product of many factors is
dangerous: if each factor shrinks the signal by 10%, thirty layers shrink it by $0.9^{30} \approx 0.04$; if each
grows it by 10%, thirty layers grow it by $1.1^{30} \approx 17$. With factors of 0.5 or 2 the effect is a factor of
$2^{30} \approx 10^9$. The gradient of the first layer's weights is (input to that layer) times (signal arriving
there), so if the signal **vanishes** the first layers do not learn, and if it **explodes** a single gradient step
throws the weights far away.

The same product appears in the forward pass: each layer multiplies the activations by a weight matrix and squashes
them by $\phi$, so the size of the activations can also shrink to nothing or grow without bound with depth.

Sepp Hochreiter analysed vanishing gradients in his 1991 diploma thesis, in the context of recurrent networks (which
are deep in time, [Chapter 18](18-Sequence-Models.md)); Yoshua Bengio, Patrice Simard and Paolo Frasconi (1994)
showed that the problem is hard to avoid when a network must store information over long spans. For feed-forward
networks it was one reason, along with small data sets and slow computers, why networks with more than two or three
hidden layers were rarely trained successfully before the late 2000s.

### Measuring it

The program builds a stack of 30 layers, each of width 100, with seven combinations of activation and initial weight
scale. It sends a batch of 256 random inputs forward and records the standard deviation of the activations after
each layer; then it sends a random gradient of length about 1 backward from the top and records the length of the
gradient arriving at each layer. The weights are drawn from a normal distribution with mean 0 and the given standard
deviation; "Xavier" and "He" are two particular choices of standard deviation derived in 16.2.

The program uses a small layer library, `ch16_nn.py`, in which every layer has a `forward` and a `backward` method
written out by hand. Running that file checks every backward method against finite differences; all agree to about
$10^{-9}$ or better:

```python
--8<-- "books/machine-learning/ch16_nn.py"
```

```
Largest difference between backward() and finite differences:
  Linear                         3.4e-10
  ReLU                           9.9e-11
  Tanh                           3.6e-10
  Sigmoid                        2.9e-10
  BatchNorm                      1.3e-09
  LayerNorm                      1.3e-09
  Residual(Linear-Tanh-Linear)   1.3e-09
  softmax cross-entropy          2.9e-10
```

Now the measurement:

```python
--8<-- "books/machine-learning/ch16_gradients.py"
```

```
30 layers of width 100, batch of 256 standard normal inputs
Xavier std = sqrt(2/(n_in+n_out)) = 0.100;  He std = sqrt(2/n_in) = 0.141

Forward: standard deviation of the activations after layer
                          1         10         20         30
  sigmoid, Xavier  2.09e-01   1.15e-01   1.16e-01   1.23e-01
  tanh, std 0.05   4.18e-01   7.12e-04   6.67e-07   6.54e-10
  tanh, std 0.3    8.64e-01   8.33e-01   8.34e-01   8.42e-01
  tanh, Xavier     6.29e-01   2.16e-01   1.52e-01   1.25e-01
  ReLU, std 0.2    1.17e+00   2.63e+01   9.79e+02   6.26e+04
  ReLU, Xavier     5.85e-01   2.57e-02   9.34e-04   5.83e-05
  ReLU, He         8.28e-01   8.23e-01   9.56e-01   1.91e+00

Backward: length of the gradient arriving at the input of layer
                          1         10         20         30
  sigmoid, Xavier  1.24e-19   7.23e-14   1.32e-07   2.31e-01
  tanh, std 0.05   6.40e-10   4.81e-07   5.05e-04   4.93e-01
  tanh, std 0.3    9.62e+03   6.51e+02   3.00e+01   1.34e+00
  tanh, Xavier     1.46e-01   5.80e-01   8.37e-01   9.69e-01
  ReLU, std 0.2    4.42e+04   1.68e+03   4.13e+01   1.28e+00
  ReLU, Xavier     4.11e-05   8.03e-04   2.02e-02   6.41e-01
  ReLU, He         1.35e+00   1.16e+00   9.13e-01   9.07e-01
```

Read the backward table row by row.

- **Sigmoid with Xavier weights:** the gradient arriving at layer 1 is $10^{-19}$ of what left the top. The
  sigmoid's derivative is at most $1/4$, so every layer shrinks the signal. The first layers will not learn at all.
- **tanh with small weights (0.05):** forward and backward both collapse, to below $10^{-9}$. Small weights shrink
  everything.
- **tanh with larger weights (0.3):** now the backward signal *explodes* by a factor of about $10^4$, while the
  forward activations stay near 0.84: the units are in tanh's flat region much of the time.
- **tanh with Xavier weights:** the gradient stays within a factor of 7 over 30 layers. Usable.
- **ReLU with 0.2:** both directions explode, by factors of $10^4$ to $10^5$.
- **ReLU with Xavier:** both vanish by $10^{-4}$ to $10^{-5}$. Xavier was derived for tanh-like units and is wrong
  for ReLU by a factor that compounds.
- **ReLU with He:** forward and backward both stay of order 1 through all 30 layers.

<figure class="mars-fig" markdown="0">
<svg viewBox="0 0 640 245" role="img" aria-label="Log-scale plot of the length of the gradient arriving at layers 1, 10, 20 and 30 of a 30-layer ReLU network. With standard deviation 0.2 it explodes to about 44000 at layer 1; with Xavier initialisation it vanishes to about 0.00004; with He initialisation it stays near 1.">
  <line x1="70" y1="210" x2="560" y2="210" stroke="currentColor" stroke-width="1"/>
  <line x1="70" y1="20" x2="70" y2="210" stroke="currentColor" stroke-width="1"/>
  <line x1="70" y1="120" x2="560" y2="120" stroke="currentColor" stroke-width="0.6" stroke-dasharray="3 4"/>
  <g fill="currentColor" font-size="11" text-anchor="end">
    <text x="64" y="44">1e4</text><text x="64" y="84">1e2</text><text x="64" y="124">1</text>
    <text x="64" y="164">1e-2</text><text x="64" y="204">1e-4</text>
  </g>
  <g fill="currentColor" font-size="11" text-anchor="middle">
    <text x="80" y="226">layer 1</text><text x="224" y="226">10</text><text x="384" y="226">20</text>
    <text x="544" y="226">30 (top)</text>
  </g>
  <polyline points="80,117.4 224,118.7 384,120.8 544,120.8" fill="none" stroke="#7ccf9a" stroke-width="2.5"/>
  <circle cx="80" cy="117.4" r="4" fill="#7ccf9a" stroke="currentColor" stroke-width="0.8"/>
  <circle cx="224" cy="118.7" r="4" fill="#7ccf9a" stroke="currentColor" stroke-width="0.8"/>
  <circle cx="384" cy="120.8" r="4" fill="#7ccf9a" stroke="currentColor" stroke-width="0.8"/>
  <circle cx="544" cy="120.8" r="4" fill="#7ccf9a" stroke="currentColor" stroke-width="0.8"/>
  <polyline points="80,207.7 224,181.9 384,153.9 544,123.9" fill="none" stroke="#9cc9ea" stroke-width="2.5"/>
  <circle cx="80" cy="207.7" r="4" fill="#9cc9ea" stroke="currentColor" stroke-width="0.8"/>
  <circle cx="224" cy="181.9" r="4" fill="#9cc9ea" stroke="currentColor" stroke-width="0.8"/>
  <circle cx="384" cy="153.9" r="4" fill="#9cc9ea" stroke="currentColor" stroke-width="0.8"/>
  <circle cx="544" cy="123.9" r="4" fill="#9cc9ea" stroke="currentColor" stroke-width="0.8"/>
  <polyline points="80,27.1 224,55.5 384,87.7 544,117.9" fill="none" stroke="#eea66f" stroke-width="2.5"/>
  <circle cx="80" cy="27.1" r="4" fill="#eea66f" stroke="currentColor" stroke-width="0.8"/>
  <circle cx="224" cy="55.5" r="4" fill="#eea66f" stroke="currentColor" stroke-width="0.8"/>
  <circle cx="384" cy="87.7" r="4" fill="#eea66f" stroke="currentColor" stroke-width="0.8"/>
  <circle cx="544" cy="117.9" r="4" fill="#eea66f" stroke="currentColor" stroke-width="0.8"/>
  <g fill="currentColor" font-size="12">
    <text x="96" y="30">ReLU, std 0.2: explodes</text>
    <text x="96" y="110">ReLU, He: stays near 1</text>
    <text x="96" y="198">ReLU, Xavier: vanishes</text>
  </g>
</svg>
<figcaption>The backward table of the program for the three ReLU networks, on a logarithmic scale. The gradient
starts at length about 1 at the top (right) and is multiplied by one factor per layer on the way down (left).</figcaption>
</figure>

The lesson is that the **scale** of the initial weights, a single number per layer, decides whether a deep network
can learn at all. The next section derives the right number.

## 16.2 Initialization: Xavier and He, derived from variance

### Why not zero?

The simplest initial weights would be all zero. That fails for a different reason: **symmetry**. If every unit of
a hidden layer starts with the same weights, every unit computes the same value, receives the same gradient and
stays identical forever, so the layer behaves like a single unit. Random initial weights break the symmetry. (Biases
can start at zero; the random weights already make units differ.) The question is only how large the random
numbers should be.

### Variance of one layer, forward

Look at one unit of layer $l$ with $n = n_{l-1}$ inputs:

$$
a = \sum_{i=1}^{n} W_i h_i ,
$$

where the weights $W_i$ are independent, with mean 0 and variance $\sigma^2$, and independent of the inputs $h_i$,
which are identically distributed. For independent $W$ and $h$ with $E[W] = 0$, the variance of the product is
$\mathrm{Var}(Wh) = E[W^2h^2] - (E[W]E[h])^2 = E[W^2]E[h^2] = \sigma^2 E[h^2]$. The $n$ terms are uncorrelated
(each has a different independent weight with mean zero), so their variances add:

$$
\mathrm{Var}(a) = n\,\sigma^2\,E[h^2] .
$$

Note $E[h^2]$, not $\mathrm{Var}(h)$: for activations that are not centred (sigmoid, ReLU), the mean matters too.

**For tanh** near zero, $\tanh(a) \approx a$, so $h$ has mean about 0 and $E[h^2] \approx \mathrm{Var}(a_{\text{prev}})$.
Keeping $\mathrm{Var}(a)$ the same from layer to layer requires $n_{l-1}\sigma^2 = 1$, that is $\sigma^2 = 1/n_{\text{in}}$.
This rule is old: Yann LeCun, Léon Bottou, Genevieve Orr and Klaus-Robert Müller recommended it in "Efficient
BackProp" (1998).

### Variance of one layer, backward

The backward pass has the same shape with the matrix transposed: $\partial L/\partial h_i = \sum_k W_{ik}\,\delta_k$, a
sum over the $n_l$ units the input feeds. By the same argument, keeping the variance of the gradients constant
requires $n_l\,\sigma^2 = 1$, that is $\sigma^2 = 1/n_{\text{out}}$.

### Xavier (Glorot) initialisation

Unless $n_{\text{in}} = n_{\text{out}}$ both conditions cannot hold. Xavier Glorot and Yoshua Bengio ("Understanding
the Difficulty of Training Deep Feedforward Neural Networks", AISTATS 2010) proposed the compromise

$$
\sigma^2 = \frac{2}{n_{\text{in}} + n_{\text{out}}} ,
$$

the harmonic mean of the two requirements. (They used a uniform distribution on $[-r, r]$ with
$r = \sqrt{6/(n_{\text{in}} + n_{\text{out}})}$, which has this variance, since a uniform distribution on
$[-r, r]$ has variance $r^2/3$.) The same paper measured activations and gradients layer by layer, much as our
program does, and showed that sigmoid networks saturate badly, which is the first row of our table.

### He initialisation for ReLU

ReLU is not linear near zero; it zeroes half its inputs. If $a$ is symmetric around zero (as a sum of symmetric terms
is),

$$
E[\mathrm{relu}(a)^2] = \int_0^\infty a^2\,p(a)\,da = \frac12\int_{-\infty}^{\infty} a^2\,p(a)\,da = \frac12\,\mathrm{Var}(a),
$$

because the integrand $a^2p(a)$ is symmetric, so each half of the line holds half of the integral. Plug this in:
$\mathrm{Var}(a^{(l)}) = n_{l-1}\sigma^2 \cdot \frac12\mathrm{Var}(a^{(l-1)})$. Constant variance needs
$\frac12 n_{\text{in}}\sigma^2 = 1$:

$$
\sigma^2 = \frac{2}{n_{\text{in}}} .
$$

This is **He initialisation**, from Kaiming He, Xiangyu Zhang, Shaoqing Ren and Jian Sun, "Delving Deep into
Rectifiers" (ICCV 2015). With Xavier's variance $1/n$ (for square layers) instead, each ReLU layer multiplies the
variance by $\frac12$, so the standard deviation shrinks by $1/\sqrt2$ per layer: after 30 layers by
$2^{-15} \approx 3 \times 10^{-5}$. The program measured $5.8 \times 10^{-5}$ for the forward pass. With standard
deviation 0.2 instead of He's 0.141, the variance is multiplied by $100 \times 0.04/2 = 2$ per layer, the standard
deviation by $\sqrt2$, and 30 layers give $2^{15} \approx 3 \times 10^{4}$: the program measured $6 \times 10^4$.
The theory predicts the measurements to within the randomness of finite layers.

Two honest remarks. First, the derivation is about the start of training only; once the weights move, the
variances change, and that is what normalisation (16.3) controls. Second, even with He initialisation the product
of 30 random matrices fluctuates: the program's forward standard deviation drifted from 0.83 to 1.91 over 30 layers.
For very deep networks one also uses **orthogonal initialisation** (Saxe, McClelland and Ganguli 2014), which makes
each weight matrix preserve lengths exactly at the start, or residual connections (16.6).

In code, the rule is one line, as in `Linear` of `ch16_nn.py`:

```python
W = rng.normal(size=(n_in, n_out)) * np.sqrt(2.0 / n_in)              # He, for ReLU
W = rng.normal(size=(n_in, n_out)) * np.sqrt(2.0 / (n_in + n_out))    # Xavier, for tanh
```

## 16.3 Normalization: batch norm and layer norm

### The idea

Initialisation makes the activations well scaled at step 0. During training the weights change, and the
distribution of every layer's inputs changes with them. Why not *force* every unit's pre-activations to be well
scaled at every step, by normalising them? Sergey Ioffe and Christian Szegedy ("Batch Normalization: Accelerating
Deep Network Training by Reducing Internal Covariate Shift", ICML 2015) did exactly that, and it made deep image
networks train much faster and with much larger learning rates.

### Batch normalisation, forward

For a batch of $B$ examples and one unit with pre-activations $x_1, \dots, x_B$:

$$
\mu = \frac1B\sum_{i} x_i, \qquad
s^2 = \frac1B\sum_i (x_i - \mu)^2, \qquad
\hat{x}_i = \frac{x_i - \mu}{\sqrt{s^2 + \epsilon}}, \qquad
y_i = \gamma\,\hat{x}_i + \beta .
$$

The normalised $\hat{x}_i$ have mean 0 and variance (almost) 1 over the batch; $\epsilon$ (say $10^{-5}$) avoids
division by zero. The **scale** $\gamma$ and **shift** $\beta$ are learned parameters, one pair per unit, so the
network can undo the normalisation if that is better: with $\gamma = s$ and $\beta = \mu$ the layer is the identity.
The layer is usually placed between the linear map and the activation, as in our program; the bias of the linear
map is then redundant, because $\beta$ plays its role.

**Training versus testing.** At test time we may classify one example at a time, and a prediction should not depend
on which other examples are in the batch. So during training BN keeps running averages of $\mu$ and $s^2$
(exponential moving averages, momentum 0.9 in our code), and at test time it uses those fixed values. Forgetting to
switch to test mode is a classic bug: the predictions then change with the batch.

### Batch normalisation, backward

The backward pass is the interesting part, because every output $y_i$ depends on every input $x_j$ through $\mu$ and
$s^2$. Write $g_i = \partial L/\partial y_i$ for the incoming gradient and $r = (s^2 + \epsilon)^{-1/2}$. The
parameter gradients are immediate: $\partial L/\partial\gamma = \sum_i g_i\hat{x}_i$ and
$\partial L/\partial\beta = \sum_i g_i$. For the input, let $\hat{g}_i = \gamma g_i$ (the gradient with respect to
$\hat{x}_i$) and use the chain rule through the three ways $x_j$ affects $\hat{x}_i$: directly, through $\mu$, and
through $s^2$.

$$
\frac{\partial \hat{x}_i}{\partial x_j} = r\Big(\mathbb{1}[i = j] - \frac1B\Big) - \frac{r}{B}\,\hat{x}_i\hat{x}_j .
$$

(The first part is from the numerator $x_i - \mu$, with $\partial\mu/\partial x_j = 1/B$. The second is from
$r = (s^2 + \epsilon)^{-1/2}$: $\partial s^2/\partial x_j = \frac2B(x_j - \mu)$, the term through $\mu$ vanishing
because deviations sum to zero, so $\partial r/\partial x_j = -\frac12 r^3 \cdot \frac2B(x_j - \mu) = -\frac{r^2}{B}\hat{x}_j$,
and multiplying by $x_i - \mu = \hat{x}_i/r$ gives $-\frac{r}{B}\hat{x}_i\hat{x}_j$.) Summing over $i$,

$$
\frac{\partial L}{\partial x_j} = \sum_i \hat{g}_i\frac{\partial\hat{x}_i}{\partial x_j}
= \frac{r}{B}\Big(B\,\hat{g}_j - \sum_i \hat{g}_i - \hat{x}_j\sum_i \hat{g}_i\hat{x}_i\Big).
$$

That is the one line in `BatchNorm.backward`, and the gradient check in `ch16_nn.py` confirms it to $3 \times 10^{-10}$.
Look at what it does: it removes from the gradient its mean over the batch and its component along $\hat{x}$. A
gradient that would only shift or rescale the unit's pre-activations is projected away, because BN would undo such
a change anyway.

### Why does it help?

The original paper explained BN by **internal covariate shift**: each layer's input distribution keeps changing as
earlier layers learn, and normalising stabilises it. Shibani Santurkar, Dimitris Tsipras, Andrew Ilyas and Aleksander
Mądry ("How Does Batch Normalization Help Optimization?", NeurIPS 2018) tested this. They added random noise after BN
layers, which made the input distributions shift *more*, and training was still fast. Their analysis and experiments
suggest instead that BN makes the loss **smoother** (gradients change less abruptly from point to point), which allows
larger learning rates. Other identified effects: BN makes the output of a layer invariant to the scale of its
incoming weights, so their effective learning rate adapts; and the batch statistics add noise that acts as a mild
regulariser. An honest summary is that BN works well, several mechanisms contribute, and there is no single accepted
explanation.

**Drawbacks.** BN depends on the batch: with small batches (as in large image or video models that fit only a few
examples per device) the statistics are noisy and BN degrades; it couples examples in a batch; and the train/test
difference is a source of bugs.

### Layer normalisation

Jimmy Lei Ba, Jamie Ryan Kiros and Geoffrey Hinton ("Layer Normalization", 2016) normalise over the **features of one
example** instead of over the batch:

$$
\mu_i = \frac1d\sum_{k=1}^{d} x_{ik}, \qquad
s_i^2 = \frac1d\sum_k (x_{ik} - \mu_i)^2, \qquad
y_{ik} = \gamma_k\frac{x_{ik} - \mu_i}{\sqrt{s_i^2 + \epsilon}} + \beta_k .
$$

Each example is normalised on its own, so nothing depends on the batch, training and testing are identical, and it
works with a batch of one. Its backward pass is the BN formula with the roles of rows and columns exchanged (see
`LayerNorm.backward`). Layer norm is standard in recurrent networks and in transformers
([Chapter 19](19-Transformers.md)). Related variants: **group normalisation** (Wu and He 2018) normalises over groups
of channels in image networks; **RMSNorm** (Zhang and Sennrich 2019) drops the mean subtraction and divides only by
the root mean square, which is cheaper and works about as well in many language models.

## 16.4 Regularization: weight decay, dropout, augmentation

Deep networks have many more parameters than training examples, so they can memorise the training set
([Chapter 8](08-Overfitting-and-Regularization.md)). Chapter 21 will show that they can even memorise random labels.
**Regularisation** means any change to training that aims to reduce the error on new data rather than on the
training data. Here are the three used most, each built from scratch in our layer library.

### Weight decay

Add $\frac{\lambda}{2}\|W\|^2$ to the loss, as in ridge regression ([Chapter 8](08-Overfitting-and-Regularization.md)).
Its gradient is $\lambda W$, so a gradient step becomes

$$
W \leftarrow W - \eta(\nabla L + \lambda W) = (1 - \eta\lambda)W - \eta\nabla L :
$$

every step shrinks ("decays") the weights by a factor $1 - \eta\lambda$ before the gradient step. Smaller weights make
smoother functions. For plain gradient descent, L2 regularisation and weight decay are the same thing. For Adam they
are **not**: Adam divides the gradient by a running estimate of its size, so an L2 term added to the gradient is also
divided, and weights with large gradients are decayed less. Ilya Loshchilov and Frank Hutter ("Decoupled Weight Decay
Regularization", ICLR 2019) proposed **AdamW**: apply the decay $W \leftarrow (1 - \eta\lambda)W$ directly, outside
the adaptive step. That is what `AdamW.step` does. By convention, biases and normalisation parameters are not decayed.

### Dropout

Nitish Srivastava, Geoffrey Hinton, Alex Krizhevsky, Ilya Sutskever and Ruslan Salakhutdinov ("Dropout: A Simple Way
to Prevent Neural Networks from Overfitting", *JMLR*, 2014; first described by Hinton et al. in 2012): during
training, set each hidden unit's output to zero with probability $p$, independently for every example and every step.
A unit can no longer rely on any particular other unit being present, so it must learn features that are useful on
their own, and the network cannot build fragile co-adapted combinations that fit noise.

At test time we want the network's **average** behaviour, not a random one. The modern **inverted dropout** scales
the surviving units by $1/(1-p)$ during training: each unit's output becomes $h \cdot m/(1-p)$, with $m$ equal to 1
with probability $1-p$ and 0 otherwise. Its expectation is

$$
E\Big[\frac{m}{1-p}\,h\Big] = \frac{(1-p)\cdot h + p \cdot 0}{1-p} = h ,
$$

so at test time the layer simply does nothing. The backward pass multiplies the gradient by the same mask (a unit
that was dropped passes no gradient). That is all of `Dropout` in `ch16_nn.py`.

Two views explain why dropout works. One: a network with $N$ droppable units contains $2^N$ "thinned" sub-networks
sharing weights, and dropout trains all of them at once; the test-time network approximates averaging their
predictions, an ensemble ([Chapter 11](11-Decision-Trees-and-Ensembles.md)). Two: for linear models, Stefan Wager,
Sida Wang and Percy Liang (2013) showed that dropout acts approximately like an L2 penalty adapted to the scale of
each feature. Typical rates are 0.1 to 0.5 for hidden layers.

### Data augmentation

The most effective regulariser is more data. When we cannot collect more, we can often create plausible new
examples from old ones: shift, flip, crop or recolour an image, add small noise to a measurement, replace a word by a
synonym. Each training step sees a slightly different version of each example, so the network learns that the label
does not depend on those changes. Augmentation encodes knowledge we have about the problem (a cat is still a cat when
mirrored; a handwritten 6 is not a 9 when rotated by 180 degrees, so do not rotate digits that far). Our program uses
the simplest version: add Gaussian noise of standard deviation 0.05 to every training point at every step.

**Early stopping** (stop when the validation loss stops improving, [Chapter 8](08-Overfitting-and-Regularization.md))
and **label smoothing** (train towards targets like 0.9 and 0.05 instead of 1 and 0, Szegedy et al. 2016) are two
more regularisers in everyday use.

### The program

A network with 4482 parameters learns from only 80 noisy points of the spirals and is tested on 2000 new points.

```python
--8<-- "books/machine-learning/ch16_regularization.py"
```

```
2-64-64-2 network (4482 parameters), 80 training points, 2000 test points, 1000 steps of Adam
averages over 2 random initialisations
                               train acc   test acc   weight norm
  no regularisation                1.000      0.911         27.72
  weight decay 0.1                 1.000      0.919         25.36
  dropout p = 0.3                  1.000      0.921         25.93
  augmentation (jitter 0.05)       1.000      0.934         23.85
  all three                        0.988      0.934         20.32
```

Every variant fits the training set (almost) perfectly. Test accuracy goes from 0.911 without regularisation to 0.919
with weight decay, 0.921 with dropout and 0.934 with augmentation; all regularisers also shrink the weights. The gains
are modest and honest: on such a small problem the noise in the labels limits what any method can reach, and with
other seeds the ranking of the middle three can change. The general pattern does not: regularisation helps most when
the model is big and the data is small, and augmentation that matches a real invariance of the data is usually the
strongest single tool.

## 16.5 Optimizers in practice: learning rates, schedules, clipping

[Chapter 5](05-Optimization.md) derived gradient descent, momentum and Adam. Here is how they are used on deep
networks.

### Which optimiser

Two families dominate. **SGD with momentum** (often Nesterov momentum, with a carefully tuned learning-rate schedule)
is still common for image classification networks and is sometimes reported to generalise slightly better. **Adam**
and especially **AdamW** need less tuning and are the default for transformers and most new architectures. Whatever
the optimiser, the **learning rate** is the most important hyperparameter: if you can tune only one number, tune that.

### The learning-rate range test

Leslie Smith ("Cyclical Learning Rates for Training Neural Networks", WACV 2017) popularised a cheap way to find a
reasonable learning rate. Start training with a tiny rate and multiply it by a constant factor every step, so that it
grows exponentially over a few hundred steps, while recording a smoothed loss. At first nothing happens (the rate is
too small); then the loss falls; finally the rate is too large and the loss shoots up. A good learning rate is
somewhat below the point where the loss is lowest, often by a factor of about ten. It is a heuristic, not a theorem,
and it reflects only the first steps of training.

### Schedules and warmup

A constant learning rate is rarely best. Early in training large steps make fast progress; late in training small
steps settle into a minimum instead of bouncing around it ([Chapter 5](05-Optimization.md)). Common schedules:

- **Step decay:** divide the rate by 10 at fixed epochs (the ResNet paper did this).
- **Cosine decay** (Loshchilov and Hutter, "SGDR", ICLR 2017): $\eta_t = \frac12\eta_{\max}\big(1 + \cos(\pi t/T)\big)$,
  which falls smoothly from $\eta_{\max}$ to 0 over $T$ steps.
- **Warmup:** start from a very small rate and increase it linearly over the first few hundred or thousand steps.
  At the start the weights are random, Adam's running averages hold almost no information, and the gradients can be
  large and erratic; a full-size step then can wreck the initialisation. Priya Goyal and colleagues ("Accurate, Large
  Minibatch SGD: Training ImageNet in 1 Hour", 2017) used warmup to train with very large batches, together with the
  **linear scaling rule** (multiply the learning rate by $k$ when the batch is $k$ times larger). Warmup is standard
  for transformers.

Warmup followed by cosine decay is the usual default today. The program prints such a schedule.

### Gradient clipping

Sometimes a single batch produces an enormous gradient: a bad initialisation, a rare example, or, in recurrent
networks, the exploding product of 16.1. One step along it can destroy everything learned so far. **Gradient
clipping** (Pascanu, Mikolov and Bengio, "On the Difficulty of Training Recurrent Neural Networks", ICML 2013) caps
the step: compute the length $\|g\|$ of the whole gradient (all parameters together) and, if it exceeds a threshold
$c$, rescale it to length $c$:

$$
g \leftarrow g \cdot \min\Big(1, \frac{c}{\|g\|}\Big).
$$

The direction is unchanged; only the step length is limited. Clipping by the total norm (as in `clip_grad_norm`) keeps
the relative sizes of the parameter gradients, unlike clipping each entry separately.

### The program

```python
--8<-- "books/machine-learning/ch16_debugging.py"
```

```
1. Loss at initialisation, 3 classes (it should be close to ln 3 = 1.0986)
  last layer std 0.01 : 1.1055
  last layer He       : 1.8323
  last layer std 10   : 82.6843

2. Overfit one batch: 8 examples with random labels must reach loss near 0
  step   1: loss 1.18554
  step  25: loss 0.00003
  step  50: loss 0.00000
  step 100: loss 0.00000
  step 200: loss 0.00000

3. Learning-rate range test on the spirals: raise the rate from 1e-5 to 10 over 300 steps
  learning rate  1.00e-05: smoothed loss 0.7845
  learning rate  3.17e-05: smoothed loss 0.8259
  learning rate  1.01e-04: smoothed loss 0.7952
  learning rate  3.20e-04: smoothed loss 0.7326
  learning rate  1.02e-03: smoothed loss 0.6718
  learning rate  3.22e-03: smoothed loss 0.6518
  learning rate  1.02e-02: smoothed loss 0.6567
  learning rate  3.25e-02: smoothed loss 0.6467
  learning rate  1.03e-01: smoothed loss 0.6113
  learning rate  3.27e-01: smoothed loss 0.5911
  learning rate  1.04e+00: smoothed loss 0.7647
  learning rate  3.30e+00: smoothed loss 100.5606
  learning rate  1.00e+01: smoothed loss 9.4741

4. Warmup for 100 steps to 0.003, then cosine decay to 0 at step 1000
  t=0: 3.00e-05  t=50: 1.53e-03  t=99: 3.00e-03  t=100: 3.00e-03  t=300: 2.65e-03  t=550: 1.50e-03  t=800: 3.51e-04  t=999: 9.14e-09

5. Gradient clipping: a badly initialised 10-layer ReLU net (std 0.5), plain gradient descent, rate 0.01
  no clipping: step 1: loss 187, grad norm 1.3e+03; step 2: loss 2.33e+04, grad norm 4.8e+04; step 3: loss 3.28e+08, grad norm 1.8e+09; step 5: loss 3e+91, grad norm 2.8e+82; step 50: loss 0.693, grad norm 0.0029; step 200: loss 0.693, grad norm 0.0014
  clip at 1.0: step 1: loss 187, grad norm 1.3e+03; step 2: loss 174, grad norm 1.3e+03; step 3: loss 160, grad norm 1.4e+03; step 5: loss 132, grad norm 1.4e+03; step 50: loss 8.17, grad norm 6.5e+02; step 200: loss 5.08, grad norm 7.5e+02
```

Parts 1 and 2 belong to 16.7. Part 3 is a range test with Adam on the spirals: the smoothed loss barely moves below
$3 \times 10^{-4}$, falls from there, is lowest around 0.1 to 0.3, and explodes above 1 (to 100 at 3.3). Following the
heuristic, a rate around 0.01 to 0.03 is a safe start; our programs used 0.003 to 0.01. Part 4 is warmup to 0.003 over
100 steps, then cosine decay: half the peak at step 550, the midpoint of the decay.

Part 5 shows clipping saving a run. A 10-layer ReLU network initialised with standard deviation 0.5 (far above He's
0.25 for width 32) starts with a loss of 187 and a gradient of length 1300 (the printed norm is measured before
clipping). Without clipping, the first step multiplies the problem: the loss reaches $2.3 \times 10^4$, then
$3 \times 10^8$, then $3 \times 10^{91}$, and afterwards it sits at exactly $\ln 2 = 0.693$ with a gradient near 0:
the huge steps have killed the ReLU units (every unit's input is negative for every example), and the network now
outputs a constant. With clipping at 1, every step has length at most $0.01$, and the loss falls steadily from 187 to
5. Clipping does not fix the bad initialisation, but it keeps a bad step from being fatal.

## 16.6 Residual connections and why depth became possible

*Level: advanced.*

### The degradation problem

With good initialisation and batch normalisation, networks of 20 to 30 layers trained well by 2015. Going deeper
revealed a surprise. Kaiming He, Xiangyu Zhang, Shaoqing Ren and Jian Sun ("Deep Residual Learning for Image
Recognition", CVPR 2016) reported that on CIFAR-10 a plain 56-layer network had **higher training error** than a
20-layer one. That is not overfitting (overfitting means low training error and high test error). It is an
optimisation failure, and it is strange, because a deep network can represent everything a shallow one can: copy the
shallow network into the first 20 layers and make the remaining 36 compute the identity. The solver simply does not
find that solution: it is hard for a stack of non-linear layers to learn the identity map.

### The residual block

He et al.'s fix is to make the identity the default. A **residual block** computes

$$
y = x + F(x),
$$

where $F$ is a small stack of layers (in our code: layer norm, linear, ReLU, linear) whose output has the same shape
as its input. The path that carries $x$ unchanged around $F$ is the **skip connection** or **shortcut**. If the best
thing for a block to do is nothing, it only has to learn $F = 0$, which is easy: small weights do it. Each block
learns a **residual**, a correction to its input, rather than a whole new representation. In our program the last
linear layer of each $F$ starts with small weights (standard deviation 0.02), so at the start every block is close to
the identity and the deep network behaves like a shallow one, growing more complex as training proceeds. A related,
slightly earlier design is the **highway network** of Rupesh Srivastava, Klaus Greff and Jürgen Schmidhuber (2015),
which uses learned gates to mix $x$ and $F(x)$.

<figure class="mars-fig" markdown="0">
<svg viewBox="0 0 640 175" role="img" aria-label="A residual block. The input x goes through layer norm, a linear layer, ReLU and another linear layer to give F of x, and is also carried unchanged along a skip connection above. The two are added to give y equals x plus F of x. In the backward pass the gradient reaches x along the skip connection unchanged, plus through F.">
  <g stroke="currentColor" stroke-width="1.3" fill="none">
    <line x1="40" y1="110" x2="90" y2="110"/>
    <line x1="160" y1="110" x2="190" y2="110"/>
    <line x1="260" y1="110" x2="290" y2="110"/>
    <line x1="360" y1="110" x2="390" y2="110"/>
    <line x1="460" y1="110" x2="508" y2="110"/>
    <line x1="552" y1="110" x2="600" y2="110"/>
    <path d="M 65 110 L 65 40 L 530 40 L 530 88"/>
  </g>
  <g stroke="currentColor" stroke-width="0.8">
    <rect x="90" y="90" width="70" height="40" rx="5" fill="#9cc9ea"/>
    <rect x="190" y="90" width="70" height="40" rx="5" fill="#7ccf9a"/>
    <rect x="290" y="90" width="70" height="40" rx="5" fill="#eea66f"/>
    <rect x="390" y="90" width="70" height="40" rx="5" fill="#7ccf9a"/>
    <circle cx="530" cy="110" r="22" fill="none"/>
  </g>
  <g fill="currentColor" font-size="13" text-anchor="middle">
    <text x="125" y="115">LayerNorm</text>
    <text x="225" y="115">Linear</text>
    <text x="325" y="115">ReLU</text>
    <text x="425" y="115">Linear</text>
    <text x="530" y="116">+</text>
    <text x="30" y="115">x</text>
    <text x="620" y="115">y</text>
    <text x="300" y="32">skip connection: x passes unchanged (gradient passes unchanged too)</text>
    <text x="275" y="158">the residual branch F(x); its last layer starts with small weights</text>
  </g>
</svg>
<figcaption>A pre-norm residual block, as in our program and in transformers. The output is the input plus a
correction computed by the branch.</figcaption>
</figure>

### Why gradients survive

Differentiate the block: $\partial y/\partial x = I + \partial F/\partial x$. Stack blocks
$x_{l+1} = x_l + F_l(x_l)$ from $l$ up to the top $L$. Unrolling the sum,

$$
x_L = x_l + \sum_{k=l}^{L-1} F_k(x_k),
\qquad
\frac{\partial L}{\partial x_l} = \frac{\partial L}{\partial x_L}\Big(I + \frac{\partial}{\partial x_l}\sum_{k=l}^{L-1}F_k(x_k)\Big).
$$

This is the argument of He, Zhang, Ren and Sun's follow-up paper ("Identity Mappings in Deep Residual Networks", ECCV
2016). The gradient at any layer contains the term $\partial L/\partial x_L$ **unchanged**, carried by the identity:
it is not a product of $L - l$ factors that could all be small. For the gradient to vanish, the second term would
have to cancel the first almost exactly, which is unlikely. In a plain network the gradient is a pure product of
Jacobians, as in 16.1, and nothing protects it.

Another view, from Andreas Veit, Michael Wilber and Serge Belongie (2016): multiplying out
$\prod_k (I + \partial F_k/\partial x)$ gives a sum over $2^n$ paths through the network, each path skipping some
blocks and passing through others. A residual network behaves like an ensemble of many shallow and medium-depth
networks, and in their experiments most of the gradient came from relatively short paths. Deleting a single block
from a trained residual network hurt only a little, while deleting a layer from a plain network destroyed it.

The effect was dramatic. The ResNet paper trained networks of 152 layers on ImageNet (and over 1000 layers on CIFAR-10)
and won the 2015 ImageNet classification competition. Residual connections are now in almost every deep architecture:
image networks ([Chapter 17](17-Convolutional-Networks.md)), and every layer of a transformer, which adds attention and
feed-forward branches to a residual stream ([Chapter 19](19-Transformers.md)).

### The program

The program trains four networks with 12 hidden layers of width 32 on the spirals of Chapter 15: plain with Xavier
initialisation (which 16.1 showed shrinks the signal for ReLU), plain with He initialisation, Xavier with batch
normalisation, and Xavier with residual blocks.

```python
--8<-- "books/machine-learning/ch16_train_deep.py"
```

```
12 hidden layers of width 32, Adam, learning rate 0.003, batches of 64, 400 steps
training loss at step 0, 100, ..., 400, then test accuracy
  plain     xavier: 0.693 0.519 0.235 0.114 0.059   test accuracy 0.932
  plain     he    : 0.697 0.097 0.001 0.000 0.000   test accuracy 0.998
  batchnorm xavier: 0.693 0.057 0.143 0.016 0.005   test accuracy 1.000
  residual  xavier: 0.728 0.534 0.315 0.023 0.000   test accuracy 1.000
```

<figure class="mars-fig" markdown="0">
<svg viewBox="0 0 640 230" role="img" aria-label="Training loss against step from 0 to 400 for four 12-layer networks. Plain with Xavier initialisation falls slowly from 0.69 to 0.06. Plain with He initialisation falls fastest, to 0.10 at step 100 and near 0 after. Batch norm falls to 0.06 at step 100, bumps up to 0.14, then near 0. Residual falls slowly at first, then to near 0 by step 400.">
  <line x1="70" y1="190" x2="490" y2="190" stroke="currentColor" stroke-width="1"/>
  <line x1="70" y1="30" x2="70" y2="190" stroke="currentColor" stroke-width="1"/>
  <g fill="currentColor" font-size="11" text-anchor="end">
    <text x="64" y="194">0</text><text x="64" y="134">0.3</text><text x="64" y="74">0.6</text>
  </g>
  <g fill="currentColor" font-size="11" text-anchor="middle">
    <text x="80" y="206">0</text><text x="180" y="206">100</text><text x="280" y="206">200</text>
    <text x="380" y="206">300</text><text x="480" y="206">400</text>
    <text x="280" y="224">training step</text>
  </g>
  <polyline points="80,51.4 180,86.2 280,143.0 380,167.2 480,178.2" fill="none" stroke="#9cc9ea" stroke-width="2.5"/>
  <polyline points="80,50.6 180,170.6 280,189.8 380,190.0 480,190.0" fill="none" stroke="#eea66f" stroke-width="2.5"/>
  <polyline points="80,51.4 180,178.6 280,161.4 380,186.8 480,189.0" fill="none" stroke="#7ccf9a" stroke-width="2.5"/>
  <polyline points="80,44.4 180,83.2 280,127.0 380,185.4 480,190.0" fill="none" stroke="currentColor" stroke-width="2.5" stroke-dasharray="6 4"/>
  <g font-size="12" fill="currentColor">
    <line x1="505" y1="60" x2="530" y2="60" stroke="#9cc9ea" stroke-width="3"/><text x="536" y="64">plain, Xavier</text>
    <line x1="505" y1="85" x2="530" y2="85" stroke="#eea66f" stroke-width="3"/><text x="536" y="89">plain, He</text>
    <line x1="505" y1="110" x2="530" y2="110" stroke="#7ccf9a" stroke-width="3"/><text x="536" y="114">batch norm</text>
    <line x1="505" y1="135" x2="530" y2="135" stroke="currentColor" stroke-width="2.5" stroke-dasharray="6 4"/><text x="536" y="139">residual</text>
  </g>
</svg>
<figcaption>Training loss of the four 12-layer networks, sampled every 100 steps, from the program's output.</figcaption>
</figure>

The plain network with Xavier initialisation learns slowly (loss 0.059 after 400 steps, test accuracy 0.932): its
signal shrinks by about $1/\sqrt2$ per layer at the start, and Adam has to work its way out. He initialisation fixes the
scale and trains fastest. Batch normalisation fixes it too, *even with the wrong initialisation*, because it rescales
every layer's pre-activations at every step. The residual network, also with the wrong initialisation, starts slowly
(its blocks begin as near-identities, so it first behaves like a shallow network) and then reaches a loss as low
as He's;
batch norm and residual both reach test accuracy 1.000. On a toy problem of this size, with Adam and 12 layers,
careful initialisation alone is enough; the advantages of normalisation and residual connections grow with depth and
with the difficulty of the task, as the ResNet paper's 56-layer and 152-layer experiments showed.

## 16.7 Debugging training: sanity checks, one batch, curves

Neural network training fails silently. A bug rarely crashes the program; it makes the network learn a bit worse, or
learn something else. Practitioners therefore follow a routine of checks, roughly in this order. Andrej Karpathy's
essay "A Recipe for Training Neural Networks" (2019) is a well-known account of the same habits.

**1. Look at the data.** Plot examples with their labels. Check shapes, ranges, units, class balance, duplicates
between training and test sets ([Chapter 2](02-Data-and-Features.md)). Many "model" problems are data problems.

**2. Check the loss at initialisation.** With $K$ classes and a network that knows nothing, the predicted probabilities
should be near $1/K$ and the cross-entropy near $\ln K$. Part 1 of the debugging program shows it: with a small last
layer the initial loss is 1.1055, close to $\ln 3 = 1.0986$; with He initialisation in the last layer it is already
1.83, and with a huge last layer 82.7, a network that is confidently wrong before it has seen any data. A last layer
initialised small (or at zero) gives the most honest start. For regression, initialise the output bias to the mean of
the targets.

**3. Overfit one small batch.** Take 8 examples and train on them alone. A working network and training loop must
drive the loss to (nearly) zero, even with random labels, because 8 examples are easy to memorise. Part 2 reaches
$3 \times 10^{-5}$ in 25 steps. If it cannot, there is a bug in the model, the loss or the update (a wrong sign, a
missing gradient, a learning rate of zero, labels misaligned with inputs) and nothing else is worth trying until it is
found.

**4. Check gradients numerically** for any layer you wrote yourself, as `ch16_nn.py` does. Use double precision and
central differences.

**5. Find a learning rate** with a range test (16.5), then train on the full data with a schedule.

**6. Watch the curves.** Plot training and validation loss against steps.

- Training loss flat from the start: learning rate too small, dead units, vanishing gradients, or a bug (go back to 3).
- Training loss explodes or becomes `nan`: learning rate too large, exploding gradients (clip), or a numerical problem
  such as taking the log of 0 (compute losses from logits with log-sum-exp, as all our code does).
- Training loss falls but validation loss rises: overfitting; regularise (16.4), get more data, or stop earlier.
- Both losses high and close together: underfitting; use a bigger model or train longer.
- Loss with sudden spikes: occasional bad batches or too high a learning rate; warmup, clipping, a lower peak rate.

**7. Watch statistics inside the network.** The mean and standard deviation of each layer's activations, the fraction
of ReLUs that are zero for every example (dead units), the norm of each layer's gradient and the ratio of the update
size to the weight size (a common rule of thumb is around $10^{-3}$ per step). These are the numbers 16.1 measured;
they reveal vanishing, exploding and dead units directly.

**8. Change one thing at a time, and fix the random seed** so that differences come from your change, not from luck.
Then check important conclusions on several seeds, because, as the regularisation table showed, small differences
between runs are often noise ([Chapter 7](07-Evaluating-Models.md)).

**In practice:** PyTorch provides `torch.nn.init.kaiming_normal_` and `xavier_uniform_` (He and Xavier),
`nn.BatchNorm1d`, `nn.LayerNorm`, `nn.Dropout`, `torch.optim.AdamW`, the schedulers in `torch.optim.lr_scheduler`
(including cosine annealing and linear warmup) and `torch.nn.utils.clip_grad_norm_`; `torch.autograd.gradcheck` checks
gradients numerically, and tools such as TensorBoard plot the curves and statistics of item 6 and 7. Every one of these
is a few lines in our `ch16_nn.py`.

## Check yourself

??? question "1. A network has 50 layers, and each layer multiplies the backward signal by a factor of about 0.8. By how much is the gradient at the first layer smaller than at the top? What if the factor is 1.2?"

    $0.8^{50} \approx 1.4 \times 10^{-5}$, so the first layer's gradient is about 70000 times smaller. With 1.2,
    $1.2^{50} \approx 9100$, so it is about 9000 times larger. Small per-layer deviations from 1 compound
    exponentially with depth.

??? question "2. Why does initialising all weights of a hidden layer to the same value fail, even if that value is not zero?"

    All units of the layer then compute the same function of the input, so they have the same activations, receive
    the same gradients (each unit's gradient depends only on its own weights, inputs and outgoing weights, which are
    identical) and receive the same updates. They stay identical forever, and the layer acts like a single unit.
    Random initialisation breaks this symmetry.

??? question "3. A layer has 512 inputs and 256 outputs. Compute the Xavier and He standard deviations, and the bound $r$ of the uniform Xavier distribution."

    Xavier: $\sigma = \sqrt{2/(512 + 256)} = \sqrt{2/768} \approx 0.0510$, and $r = \sqrt{6/768} \approx 0.0884$
    (check: $r^2/3 = 0.0026 = \sigma^2$). He: $\sigma = \sqrt{2/512} = 0.0625$.

??? question "4. Prove that if $a$ has mean 0 and a distribution symmetric about 0, then $E[\mathrm{relu}(a)] = \frac12 E[|a|]$ and $E[\mathrm{relu}(a)^2] = \frac12\mathrm{Var}(a)$. What is the variance of $\mathrm{relu}(a)$ when $a$ is standard normal?"

    By symmetry, $a$ and $-a$ have the same distribution, so $E[a\,\mathbb{1}(a > 0)] = E[-a\,\mathbb{1}(a < 0)]$, and
    the two add to $E[|a|]$; hence each is $\frac12E|a|$. The same argument with $a^2$ gives $E[a^2\mathbb{1}(a>0)] = \frac12E[a^2]
    = \frac12\mathrm{Var}(a)$ (mean 0). For a standard normal, $E|a| = \sqrt{2/\pi}$, so $E[\mathrm{relu}(a)] = 1/\sqrt{2\pi}
    \approx 0.399$, $E[\mathrm{relu}(a)^2] = 0.5$, and $\mathrm{Var}(\mathrm{relu}(a)) = 0.5 - 1/(2\pi) \approx 0.341$.
    This is why the He derivation uses $E[h^2]$, not $\mathrm{Var}(h)$.

??? question "5. Batch norm is applied to a unit whose pre-activations in a batch are 1, 2, 3, 6, with $\gamma = 2$, $\beta = 1$ and $\epsilon$ negligible. Compute the outputs."

    $\mu = 3$, deviations $-2, -1, 0, 3$, $s^2 = (4 + 1 + 0 + 9)/4 = 3.5$, $s \approx 1.871$. So
    $\hat{x} \approx (-1.069, -0.535, 0, 1.604)$ and $y = 2\hat{x} + 1 \approx (-1.138, -0.069, 1, 4.207)$. The outputs have
    mean $\beta = 1$ and standard deviation $\gamma = 2$.

??? question "6. Show that the batch-norm input gradient always sums to zero over the batch, and explain why that makes sense."

    From $\partial L/\partial x_j = \frac{r}{B}\big(B\hat{g}_j - \sum_i\hat{g}_i - \hat{x}_j\sum_i\hat{g}_i\hat{x}_i\big)$, summing over
    $j$ gives $\frac{r}{B}\big(B\sum\hat{g} - B\sum\hat{g} - (\sum_j\hat{x}_j)\sum_i\hat{g}_i\hat{x}_i\big) = 0$, because the
    normalised values $\hat{x}_j$ sum to zero. Adding the same constant to every $x_j$ in the batch does not change the
    output at all (the mean is subtracted), so the loss cannot depend on the direction $(1, \dots, 1)$, and the
    gradient must be orthogonal to it.

??? question "7. With inverted dropout at $p = 0.5$, a unit outputs 3.0 in training. What values can the layer pass on, with what probabilities, and what is their mean? What does the layer do at test time?"

    The mask is 0 or 1 with probability one half each, and survivors are scaled by $1/(1 - 0.5) = 2$. So the layer
    passes 0 or 6.0, each with probability one half; the mean is 3.0, the unit's own value. At test time the layer
    passes 3.0 unchanged: inverted dropout puts all of the correction into training.

??? question "8. Show that for plain gradient descent, adding $\frac{\lambda}{2}\|w\|^2$ to the loss is the same as weight decay, but for Adam it is not."

    Gradient descent on $L + \frac\lambda2\|w\|^2$ steps $w \leftarrow w - \eta(\nabla L + \lambda w) = (1 - \eta\lambda)w - \eta\nabla L$,
    exactly decay by $1 - \eta\lambda$ followed by a step. Adam instead computes $m$ and $v$ from the full gradient
    $g = \nabla L + \lambda w$ and steps by $\eta\,\hat{m}/(\sqrt{\hat{v}} + \epsilon)$: the decay term $\lambda w$ is
    divided by the running root-mean-square of the gradient, so weights with large or noisy gradients are decayed
    less, and the result is not a uniform shrinkage. AdamW applies $w \leftarrow (1 - \eta\lambda)w$ separately.

??? question "9. Write the code: a gradient-clipping step that clips by total norm, and check that it never changes the direction of the gradient."

    ```python
    import numpy as np

    def clip_grad_norm(grads, max_norm):
        total = np.sqrt(sum((g ** 2).sum() for g in grads))
        if total > max_norm:
            for g in grads:
                g *= max_norm / total
        return total

    rng = np.random.default_rng(0)
    grads = [rng.normal(size=(3, 4)) * 10, rng.normal(size=4) * 10]
    before = np.concatenate([g.ravel() for g in grads])
    clip_grad_norm(grads, 1.0)
    after = np.concatenate([g.ravel() for g in grads])
    print(np.linalg.norm(after))                                  # 1.0 (up to rounding)
    print(before @ after / (np.linalg.norm(before) * np.linalg.norm(after)))   # 1.0 (up to rounding): same direction
    ```

    Every gradient array is multiplied by the same positive number, so the combined vector keeps its direction.

??? question "10. Write the code: a learning-rate schedule with linear warmup for $w$ steps to a peak $\eta$, followed by linear decay to 0 at step $T$. What is the rate at $t = w$, at the midpoint of the decay, and at $T - 1$ for $w = 100$, $T = 1000$, $\eta = 0.001$?"

    ```python
    def warmup_linear(t, T, peak, w):
        if t < w:
            return peak * (t + 1) / w
        return peak * (T - t) / (T - w)

    for t in (99, 100, 550, 999):
        print(t, warmup_linear(t, 1000, 1e-3, 100))
    # 99 0.001   100 0.001   550 0.0005   999 1.111e-06
    ```

    At the end of warmup and the start of the decay the rate is the peak, 0.001; at the midpoint of the decay
    ($t = 550$) it is half the peak; at $t = 999$ it is $10^{-3}/900 \approx 1.1 \times 10^{-6}$.

??? question "11. (Hard) A residual network has blocks $x_{k+1} = x_k + F_k(x_k)$ in one dimension, where each $F_k(x) = \epsilon_k x$ with small $\epsilon_k$. Compute $\partial x_L / \partial x_0$ and compare with a plain network $x_{k+1} = w_k x_k$. Why does initialising the residual branches near zero make deep residual networks easy to start?"

    For the residual network, $x_L = \prod_{k}(1 + \epsilon_k)\,x_0$, so $\partial x_L/\partial x_0 = \prod_k(1 + \epsilon_k)$,
    which is close to 1 when the $\epsilon_k$ are small (its logarithm is about $\sum_k \epsilon_k$, and for random
    $\epsilon_k$ of either sign the sum grows only like $\sqrt{L}$ times their typical size). For the plain network,
    $\partial x_L/\partial x_0 = \prod_k w_k$, which vanishes or explodes exponentially unless every $w_k$ is almost
    exactly 1. With branches near zero, a residual network starts as (nearly) the identity map, its gradients are (nearly)
    the identity too, and each block can then learn a small correction; this is the reasoning behind initialising the
    last layer of each branch small or at zero.

??? question "12. (Hard) Your training loss decreases normally for 2000 steps, then becomes `nan`. List three likely causes and how to check each."

    (a) The learning rate is too large late in training or there is no decay: check the schedule, and log the gradient
    norm before the `nan` (a sudden spike points to exploding gradients; clipping and a lower peak rate help).
    (b) A numerical problem such as $\log 0$ or $\exp$ overflow when the network becomes very confident: check that the
    loss is computed from logits with log-sum-exp (or `logaddexp`), not as `log(softmax(...))`, and that no division by
    a variance lacks its $\epsilon$. (c) A bad input: a `nan` or extreme value in some batch; check `np.isfinite` on each
    batch and find the step at which the first non-finite number appears, in the activations layer by layer.

## What you learned

- Gradients in a plain deep network are products of one factor per layer, so they vanish or explode exponentially
  with depth unless each factor is close to 1; measuring activation and gradient sizes layer by layer shows it.
- Keeping the variance of activations and gradients constant gives the initialisation rules: Xavier
  $\sigma^2 = 2/(n_{\text{in}} + n_{\text{out}})$ for tanh-like units and He $\sigma^2 = 2/n_{\text{in}}$ for ReLU,
  whose factor 2 comes from ReLU zeroing half of its inputs.
- Batch normalisation standardises each unit over the batch and layer normalisation over the features of each
  example; their backward passes project out shifts and rescalings, and they let networks train fast even from a poor
  initialisation; why BN helps is still partly open.
- Weight decay (decoupled in AdamW), dropout (inverted, so test time needs no change) and data augmentation reduce
  overfitting; augmentation that matches a real invariance is often the strongest.
- The learning rate matters most: find it with a range test, use warmup and a decaying schedule such as cosine, and
  clip the gradient norm to survive rare huge gradients.
- Residual connections $y = x + F(x)$ give gradients an identity path, so they cannot vanish by multiplication; they
  made networks of a hundred layers and more trainable and are in nearly every modern architecture.
- Debug training with a routine: look at the data, check the initial loss, overfit one batch, check gradients, watch
  curves and internal statistics, and change one thing at a time.

**Next:** [Chapter 17](17-Convolutional-Networks.md), which builds the network designed for images: convolution,
pooling and the architectures from LeNet to ResNet.

## Further reading

- I. Goodfellow, Y. Bengio and A. Courville, *Deep Learning*, 2016, chapter 7 (regularisation: weight decay,
  augmentation, early stopping, dropout), chapter 8 (optimisation for training deep models: initialisation,
  batch normalisation) and section 10.11 (gradient clipping).
- C. Bishop and H. Bishop, *Deep Learning: Foundations and Concepts*, 2024, chapters 7 and 9 (gradient descent in
  practice, normalisation, regularisation, residual connections).
- K. Murphy, *Probabilistic Machine Learning: An Introduction*, 2022, chapter 13 (training neural networks:
  initialisation, normalisation, regularisation, residual networks).
- S. Hochreiter, *Untersuchungen zu dynamischen neuronalen Netzen*, diploma thesis, TU Munich, 1991; Y. Bengio,
  P. Simard and P. Frasconi, "Learning Long-Term Dependencies with Gradient Descent is Difficult", *IEEE Transactions
  on Neural Networks*, 1994.
- Y. LeCun, L. Bottou, G. Orr and K.-R. Müller, "Efficient BackProp", in *Neural Networks: Tricks of the Trade*, 1998.
- X. Glorot and Y. Bengio, "Understanding the Difficulty of Training Deep Feedforward Neural Networks", AISTATS 2010.
- K. He, X. Zhang, S. Ren and J. Sun, "Delving Deep into Rectifiers: Surpassing Human-Level Performance on ImageNet
  Classification", ICCV 2015; "Deep Residual Learning for Image Recognition", CVPR 2016; "Identity Mappings in Deep
  Residual Networks", ECCV 2016.
- A. Saxe, J. McClelland and S. Ganguli, "Exact Solutions to the Nonlinear Dynamics of Learning in Deep Linear Neural
  Networks", ICLR 2014.
- S. Ioffe and C. Szegedy, "Batch Normalization: Accelerating Deep Network Training by Reducing Internal Covariate
  Shift", ICML 2015; S. Santurkar, D. Tsipras, A. Ilyas and A. Mądry, "How Does Batch Normalization Help
  Optimization?", NeurIPS 2018; J. L. Ba, J. R. Kiros and G. Hinton, "Layer Normalization", arXiv 2016; Y. Wu and
  K. He, "Group Normalization", ECCV 2018; B. Zhang and R. Sennrich, "Root Mean Square Layer Normalization",
  NeurIPS 2019.
- N. Srivastava, G. Hinton, A. Krizhevsky, I. Sutskever and R. Salakhutdinov, "Dropout: A Simple Way to Prevent Neural
  Networks from Overfitting", *JMLR*, 2014; S. Wager, S. Wang and P. Liang, "Dropout Training as Adaptive
  Regularization", NIPS 2013.
- I. Loshchilov and F. Hutter, "SGDR: Stochastic Gradient Descent with Warm Restarts", ICLR 2017; "Decoupled Weight
  Decay Regularization", ICLR 2019.
- L. Smith, "Cyclical Learning Rates for Training Neural Networks", WACV 2017; P. Goyal et al., "Accurate, Large
  Minibatch SGD: Training ImageNet in 1 Hour", arXiv 2017.
- R. Pascanu, T. Mikolov and Y. Bengio, "On the Difficulty of Training Recurrent Neural Networks", ICML 2013.
- R. Srivastava, K. Greff and J. Schmidhuber, "Highway Networks", arXiv 2015; A. Veit, M. Wilber and S. Belongie,
  "Residual Networks Behave Like Ensembles of Relatively Shallow Networks", NIPS 2016.
- C. Szegedy, V. Vanhoucke, S. Ioffe, J. Shlens and Z. Wojna, "Rethinking the Inception Architecture for Computer
  Vision", CVPR 2016 (label smoothing).
- A. Karpathy, "A Recipe for Training Neural Networks", blog essay, 2019.
- On this site: [Chapter 15](15-Neural-Networks-and-Backpropagation.md) for backpropagation and the spirals,
  [Chapter 5](05-Optimization.md) for momentum and Adam, [Chapter 8](08-Overfitting-and-Regularization.md) for
  regularisation and early stopping, [Chapter 21](21-Learning-Theory.md) for why over-parameterised networks still
  generalise; the probability book at [https://math.akadian.ca/books/](https://math.akadian.ca/books/).
