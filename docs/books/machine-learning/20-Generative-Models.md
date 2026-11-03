# 20. Generative models

*Every model so far answered a question about data: which class, what number, what comes next. A generative model
learns the data itself: a probability distribution from which it can draw new examples that look like the training
set, new faces, new sentences, new molecules. This chapter builds the five main families from scratch, each from the
problem that drove it: variational autoencoders and their evidence lower bound, generative adversarial networks and
their minimax game, normalizing flows and the change-of-variables formula, diffusion models that learn to undo
noise, and autoregressive models such as the language models of [Chapter 19](19-Transformers.md). It ends with score
matching, the idea that ties diffusion to the gradient of a log-density, and with what is still open.*

!!! abstract "In this chapter"
    **You will learn:**

    - what it means to model a distribution, how to sample from one, and how to judge a generative model
    - autoencoders and variational autoencoders: the ELBO derived, the reparameterisation trick and why it beats the score-function estimator
    - GANs: the minimax game, the optimal discriminator derived, the link to the Jensen-Shannon divergence, and why training can circle
    - normalizing flows: the change-of-variables formula, coupling layers, a flow trained by maximum likelihood
    - diffusion models: the forward noising process in closed form, the noise-prediction loss derived, a 2-D model trained and sampled
    - autoregressive models as exact-likelihood generative models
    - score matching, Langevin dynamics and the probability-flow ODE that link diffusion and score-based models

    **You need:** maximum likelihood and the KL divergence from [Chapter 3](03-The-Math-Toolkit.md), neural networks
    and backpropagation from [Chapter 15](15-Neural-Networks-and-Backpropagation.md), and the language models of
    [Chapter 18](18-Sequence-Models.md) and [Chapter 19](19-Transformers.md). Autoencoders were previewed in
    [Chapter 14](14-Dimensionality-Reduction.md); Gaussian mixtures and EM are in [Chapter 13](13-Clustering.md).

    **Levels:** 20.1 is beginner to intermediate; 20.2 to 20.4 are intermediate to advanced; 20.5 and 20.6 are
    advanced; 20.7 is expert.

## 20.1 What it means to model a distribution; sampling

**The question:** suppose you have ten thousand photographs of galaxies, or a million sentences. What would it mean
for a program to "know" what such data looks like?

Assume the examples $x^{(1)}, \dots, x^{(N)}$ were drawn independently from some unknown distribution $p_{\text{data}}$.
A **generative model** is a distribution $p_\theta$ with parameters $\theta$, chosen so that $p_\theta$ is close to
$p_{\text{data}}$. We may want two different things from it:

- **Density evaluation:** given an $x$, compute $p_\theta(x)$, for example to spot unusual data (a sensor reading
  that the model finds very unlikely) or to compare models.
- **Sampling:** draw new $x \sim p_\theta$, to create data or to fill in missing parts.

Some families give both, some only one, and that choice shapes everything in this chapter.

### Maximum likelihood is minimum KL

The standard way to fit $p_\theta$ is maximum likelihood ([Chapter 3](03-The-Math-Toolkit.md)): maximise
$\frac{1}{N} \sum_i \log p_\theta(x^{(i)})$. Why is that the right goal? As $N$ grows, the average tends to
$E_{p_{\text{data}}}[\log p_\theta(x)]$, and

$$
\operatorname{KL}(p_{\text{data}} \,\|\, p_\theta) = E_{p_{\text{data}}}[\log p_{\text{data}}(x)] - E_{p_{\text{data}}}[\log p_\theta(x)].
$$

The first term does not depend on $\theta$, so maximising the expected log-likelihood is the same as minimising the KL
divergence from the data distribution to the model. KL is zero exactly when the two distributions are equal. This
KL heavily penalises a model that gives near-zero probability to real data, so maximum-likelihood models tend to
"cover" all of the data, sometimes by also putting probability on implausible regions.

### Sampling from a distribution

How do you draw a sample at all? A computer provides uniform random numbers $u \in (0, 1)$. Three basic tools turn
them into anything else:

- **Inverse CDF.** If $F$ is the cumulative distribution function of a 1-D distribution, then $x = F^{-1}(u)$ has
  distribution $F$, because $P(F^{-1}(u) \le x) = P(u \le F(x)) = F(x)$. For the exponential distribution with rate
  $\lambda$, $F(x) = 1 - e^{-\lambda x}$, so $x = -\ln(1 - u)/\lambda$. Part 1 of the VAE program checks this.
- **Ancestral sampling.** For a model written as a chain of conditionals, sample the first variable, then the next
  given the first, and so on. A Gaussian mixture ([Chapter 13](13-Clustering.md)) is sampled by first picking a
  component, then drawing from it; an autoregressive model (20.6) draws one token at a time.
- **Transforming noise.** Draw $z$ from a simple distribution such as $N(0, I)$ and output $x = G(z)$ for some
  function $G$. VAEs, GANs, flows and diffusion models all work this way, with $G$ a neural network.

For hard distributions known only up to a constant, Markov chain Monte Carlo ([Chapter 12](12-Probabilistic-Models.md))
is a fourth tool, and it reappears in 20.7 as Langevin dynamics.

### Judging a generative model

Judging is harder than for a classifier, because there is no single right answer. Where the model gives a density,
the **held-out log-likelihood** (often reported in bits per dimension or per token) is the standard measure. For
images, people also use sample-based scores such as the **Fréchet Inception Distance** (FID, Heusel et al., 2017),
which compares the mean and covariance of features of real and generated images computed by a pretrained network.
Each measure has blind spots: Theis, van den Oord and Bethge (2016) showed that likelihood and sample quality can
disagree badly. In our toy programs the data is known exactly, so we can compare directly: share of samples near the
true modes, moments, and densities.

## 20.2 Autoencoders and variational autoencoders

**The question:** an autoencoder ([Chapter 14](14-Dimensionality-Reduction.md)) compresses $x$ into a short code $z$
and reconstructs it. Could we generate new data by inventing new codes and decoding them?

A plain **autoencoder** has an encoder $z = f(x)$ and a decoder $\hat x = g(z)$, trained to make $\hat x$ close to
$x$. It learns a good code, but nothing makes the codes of real data fill any particular region: a random $z$ may land
in a gap between codes and decode to nonsense. To generate, we need to know where the codes are.

### The latent-variable model

A **variational autoencoder** (VAE; Kingma and Welling, 2013; and independently Rezende, Mohamed and Wierstra, 2014)
starts from a probabilistic model. Draw a **latent** (hidden) code $z \sim p(z) = N(0, I)$, then draw
$x \sim p_\theta(x \mid z)$, for example a Gaussian whose mean is a neural network $g_\theta(z)$. Sampling is easy:
that is ancestral sampling. Its likelihood is

$$
p_\theta(x) = \int p_\theta(x \mid z)\, p(z)\, dz ,
$$

an integral over all codes that has no closed form when $g_\theta$ is a neural network. We cannot maximise what we
cannot compute. The VAE's answer: maximise a lower bound on it.

### The ELBO, derived

Introduce an **encoder** distribution $q_\phi(z \mid x)$, a Gaussian $N(\mu_\phi(x), \operatorname{diag}\sigma_\phi^2(x))$
whose mean and variance are another network's outputs, meant to approximate the true posterior
$p_\theta(z \mid x)$ (which codes could have produced this $x$). For any such $q$,

$$
\begin{aligned}
\log p_\theta(x) &= E_{q_\phi(z \mid x)}\big[\log p_\theta(x)\big]
= E_{q}\left[\log \frac{p_\theta(x, z)}{p_\theta(z \mid x)}\right]
= E_{q}\left[\log \frac{p_\theta(x, z)}{q_\phi(z \mid x)}\right] + E_{q}\left[\log \frac{q_\phi(z \mid x)}{p_\theta(z \mid x)}\right] \\
&= \underbrace{E_{q}\big[\log p_\theta(x \mid z)\big] - \operatorname{KL}\big(q_\phi(z \mid x) \,\|\, p(z)\big)}_{\text{ELBO}(x)}
\; + \; \operatorname{KL}\big(q_\phi(z \mid x) \,\|\, p_\theta(z \mid x)\big).
\end{aligned}
$$

The first step holds because $\log p_\theta(x)$ does not depend on $z$; the second uses
$p_\theta(x) = p_\theta(x, z)/p_\theta(z \mid x)$; the third multiplies and divides by $q$; the fourth writes
$p_\theta(x, z) = p_\theta(x \mid z) p(z)$. The last KL is never negative, so

$$
\log p_\theta(x) \ge \text{ELBO}(x) = E_{q_\phi(z \mid x)}\big[\log p_\theta(x \mid z)\big] - \operatorname{KL}\big(q_\phi(z \mid x) \,\|\, p(z)\big),
$$

the **evidence lower bound**, with equality exactly when $q_\phi(z \mid x)$ is the true posterior. Its two terms
read naturally. The first is a **reconstruction** term: encode $x$ to a random code, decode, and score how well $x$
is explained; with a Gaussian decoder of fixed standard deviation $\sigma_x$ it is
$-\|x - g_\theta(z)\|^2 / (2\sigma_x^2)$ plus a constant. The second is a **regulariser** that keeps every
encoding distribution close to the prior $N(0, I)$, so that the codes of real data fill the region we will sample
from. Training maximises the average ELBO over the data, jointly in $\theta$ and $\phi$. This is the same bound as in
EM ([Chapter 13](13-Clustering.md)); EM can compute the exact posterior, a VAE learns an approximation to it with a
network ("amortised inference").

For two Gaussians the KL has a closed form. For one coordinate,
$\operatorname{KL}(N(\mu, \sigma^2) \,\|\, N(0, 1)) = \tfrac{1}{2}(\mu^2 + \sigma^2 - 1 - \log \sigma^2)$ (Exercise 2),
summed over coordinates. It is 0 only for $\mu = 0$, $\sigma = 1$.

### The reparameterisation trick

The reconstruction term is an expectation over $z \sim q_\phi$, which depends on $\phi$. How do we differentiate
$E_{q_\phi}[f(z)]$ with respect to $\phi$? Sampling $z$ is not a differentiable operation. Kingma and Welling's
**reparameterisation trick** writes the sample as a deterministic function of $\phi$ and outside noise:

$$
z = \mu_\phi(x) + \sigma_\phi(x) \odot \epsilon, \qquad \epsilon \sim N(0, I),
$$

so $E_{q_\phi}[f(z)] = E_{\epsilon}[f(\mu_\phi + \sigma_\phi \odot \epsilon)]$, and the gradient moves inside the
expectation: $\nabla_\phi E_\epsilon[f(\cdot)] = E_\epsilon[\nabla_\phi f(\mu_\phi + \sigma_\phi \odot \epsilon)]$,
estimated with one or a few samples of $\epsilon$ and computed by ordinary backpropagation. Figure 20.1 shows the
network.

<figure class="mars-fig" markdown="0">
<svg viewBox="0 0 665 220" role="img" aria-label="A variational autoencoder: the input x goes into an encoder that outputs a mean mu and a standard deviation sigma; z is formed as mu plus sigma times epsilon, with epsilon drawn from a standard normal; z goes into a decoder that outputs a reconstruction. The loss is the reconstruction error plus the KL divergence from the encoder's distribution to the standard normal prior.">
<rect x="10" y="80" width="60" height="40" rx="8" fill="#9cc9ea" fill-opacity="0.7" stroke="currentColor"/>
<text x="40.0" y="105.0" font-size="14" text-anchor="middle" fill="currentColor">x</text>
<line x1="70.0" y1="100.0" x2="90.0" y2="100.0" stroke="currentColor" stroke-width="1.4"/><polygon points="98.0,100.0 90.0,104.0 90.0,96.0" fill="currentColor"/>
<rect x="100" y="70" width="110" height="60" rx="8" fill="#7ccf9a" fill-opacity="0.7" stroke="currentColor"/>
<text x="155.0" y="97.0" font-size="14" text-anchor="middle" fill="currentColor">encoder</text>
<text x="155.0" y="113.0" font-size="12" text-anchor="middle" fill="currentColor">q(z | x)</text>
<line x1="210.0" y1="92.0" x2="240.4" y2="82.4" stroke="currentColor" stroke-width="1.4"/><polygon points="248.0,80.0 241.6,86.2 239.2,78.6" fill="currentColor"/>
<line x1="210.0" y1="108.0" x2="240.4" y2="117.6" stroke="currentColor" stroke-width="1.4"/><polygon points="248.0,120.0 239.2,121.4 241.6,113.8" fill="currentColor"/>
<rect x="250" y="60" width="50" height="34" rx="8" fill="#eea66f" fill-opacity="0.7" stroke="currentColor"/>
<text x="275.0" y="82.0" font-size="14" text-anchor="middle" fill="currentColor">&#956;</text>
<rect x="250" y="106" width="50" height="34" rx="8" fill="#eea66f" fill-opacity="0.7" stroke="currentColor"/>
<text x="275.0" y="128.0" font-size="14" text-anchor="middle" fill="currentColor">&#963;</text>
<line x1="300.0" y1="77.0" x2="335.6" y2="91.9" stroke="currentColor" stroke-width="1.4"/><polygon points="343.0,95.0 334.1,95.6 337.2,88.2" fill="currentColor"/>
<line x1="300.0" y1="123.0" x2="335.6" y2="108.1" stroke="currentColor" stroke-width="1.4"/><polygon points="343.0,105.0 337.2,111.8 334.1,104.4" fill="currentColor"/>
<rect x="345" y="75" width="110" height="50" rx="8" fill="#eea66f" fill-opacity="0.7" stroke="currentColor"/>
<text x="400.0" y="105.0" font-size="14" text-anchor="middle" fill="currentColor">z = &#956; + &#963; &#949;</text>
<rect x="345" y="165" width="110" height="36" rx="8" fill="#9cc9ea" fill-opacity="0.7" stroke="currentColor"/>
<text x="400.0" y="188.0" font-size="14" text-anchor="middle" fill="currentColor">&#949; ~ N(0, I)</text>
<line x1="400.0" y1="165.0" x2="400.0" y2="135.0" stroke="currentColor" stroke-width="1.4"/><polygon points="400.0,127.0 404.0,135.0 396.0,135.0" fill="currentColor"/>
<line x1="455.0" y1="100.0" x2="470.0" y2="100.0" stroke="currentColor" stroke-width="1.4"/><polygon points="478.0,100.0 470.0,104.0 470.0,96.0" fill="currentColor"/>
<rect x="480" y="70" width="100" height="60" rx="8" fill="#7ccf9a" fill-opacity="0.7" stroke="currentColor"/>
<text x="530.0" y="97.0" font-size="14" text-anchor="middle" fill="currentColor">decoder</text>
<text x="530.0" y="113.0" font-size="12" text-anchor="middle" fill="currentColor">p(x | z)</text>
<line x1="580.0" y1="100.0" x2="595.0" y2="100.0" stroke="currentColor" stroke-width="1.4"/><polygon points="603.0,100.0 595.0,104.0 595.0,96.0" fill="currentColor"/>
<rect x="605" y="80" width="50" height="40" rx="8" fill="#9cc9ea" fill-opacity="0.7" stroke="currentColor"/>
<text x="630.0" y="105.0" font-size="14" text-anchor="middle" fill="currentColor">x&#770;</text>
<text x="330" y="30" font-size="13" text-anchor="middle" fill="currentColor">loss = reconstruction error (x vs x&#770;) + KL( q(z | x) || N(0, I) )</text>
<text x="170" y="185" font-size="12" text-anchor="middle" fill="currentColor">randomness enters from outside,</text>
<text x="170" y="201" font-size="12" text-anchor="middle" fill="currentColor">so gradients flow through &#956; and &#963;</text>
</svg>
<figcaption>Figure 20.1. A variational autoencoder with the reparameterisation trick. The encoder outputs a distribution, not a point; the sample is written as a deterministic function of the encoder's outputs and outside noise, so backpropagation can reach the encoder.</figcaption>
</figure>

The alternative, the **score-function** or REINFORCE estimator (Williams, 1992), uses
$\nabla_\phi E_{q_\phi}[f(z)] = E_{q_\phi}[f(z) \nabla_\phi \log q_\phi(z)]$, which works for any distribution, even
discrete ones, but is noisier. Part 2 of the program compares both on $\nabla_\mu E[z^2]$ with $z \sim N(\mu, 1)$ at
$\mu = 1$, whose exact value is $2\mu = 2$. Both are unbiased (means 2.003 and 2.000), but the per-sample standard
deviation is 2.00 for reparameterisation and 5.44 for the score function. These match the exact values: the
reparameterised estimate $2(\mu + \epsilon)$ has variance 4, and the score-function estimate
$(1 + \epsilon)^2 \epsilon$ has second moment $E[\epsilon^2] + 6E[\epsilon^4] + E[\epsilon^6] = 1 + 18 + 15 = 34$,
so variance $34 - 4 = 30$ and standard deviation 5.48. To reach the same accuracy the score function needs about
$30/4 = 7.5$ times as many samples here, and in high dimensions the gap is usually much larger. This trick is what
made VAEs trainable by plain stochastic gradient descent. (Reinforcement learning, where actions are discrete and the
environment is not differentiable, relies on the score-function form.)

### A VAE from scratch

The program trains a VAE on points of a noisy ring (radius 2, noise 0.1) with a 2-D latent space, a 64-unit tanh
encoder, a two-layer 64-unit decoder and $\sigma_x = 0.1$. The autodiff is the same small reverse-mode engine as in
[Chapter 18](18-Sequence-Models.md), with `exp` and `log` added.

```python
--8<-- "books/machine-learning/ch20_vae.py"
```

```
1. sampling an exponential distribution (rate 2) by the inverse CDF, x = -ln(1 - u) / 2
   sample mean 0.4983 (exact 0.5), variance 0.2508 (exact 0.25)

2. gradient of E[z^2] over z ~ N(mu, 1) with respect to mu, at mu = 1 (exact: 2 mu = 2)
   reparameterisation: mean 2.003, std per sample 2.00
   score function    : mean 2.000, std per sample 5.44

3. VAE on a noisy ring (radius 2, noise 0.1): latent size 2, decoder noise 0.1
   (negative ELBO = reconstruction + KL, per point, in nats, up to a constant)
   step    1: -ELBO   177.91 = reconstruction   177.06 + KL  0.85
   step  250: -ELBO     8.33 = reconstruction     2.90 + KL  5.43
   step 1000: -ELBO     5.75 = reconstruction     1.43 + KL  4.32
   step 3000: -ELBO     5.55 = reconstruction     1.27 + KL  4.28

4. 5000 new points: z ~ N(0, I), x = decoder mean
   radius: mean 1.893, std 0.249   (data: 2.000, 0.100)
   share of points with 1.7 < radius < 2.3: 0.886
   points in each eighth of the circle: [682, 684, 635, 515, 680, 662, 634, 508]
```

The negative ELBO falls from 178 to 5.55 nats per point. Look at its parts: the reconstruction cost falls
fast, and the KL rises from 0.85 to about 4.3 nats. The KL is the price, in nats, of the information the code
carries about each point: to reconstruct a point on a ring to within 0.1 the code must say where on the ring it is,
and that costs bits. The trade-off between the two terms is the heart of the VAE, and the $\beta$-VAE (Higgins et
al., 2017) makes it explicit with a weight $\beta$ on the KL.

Part 4 decodes 5,000 codes drawn from the prior. 88.6% of the decoded means land within 0.3 of the ring, spread
evenly round it, but the mean radius is 1.89 rather than 2 and the spread 0.25 rather than 0.10: some prior codes
fall in regions that no training point's encoding covered, and decode to points inside the ring. This mismatch between
the prior and the "aggregate posterior" (the distribution of codes of real data) is a known weakness of simple VAEs,
along with blurry samples when the decoder is a Gaussian on pixels. Hierarchical VAEs with many latent layers, such
as NVAE (Vahdat and Kautz, 2020), narrowed the quality gap considerably, and VAE-style autoencoders are now widely used
as the compressor inside larger systems: latent diffusion (Rombach et al., 2022) runs a diffusion model in the code
space of an autoencoder.

## 20.3 GANs: the minimax game

**The question:** the VAE needs a likelihood for $p_\theta(x \mid z)$, and a Gaussian on pixels gives blurry samples.
Could we train a generator with no likelihood at all, judged only by whether its samples can be told apart from real
data?

Goodfellow and colleagues' **generative adversarial networks** (2014) set up a game between two networks. A
**generator** $G$ maps noise $z \sim p(z)$ to samples $G(z)$, which define a distribution $p_g$. A **discriminator**
$D(x) \in (0, 1)$ estimates the probability that $x$ is real rather than generated. $D$ is trained as a classifier,
real versus fake, with the logistic loss of [Chapter 6](06-Classification-and-Logistic-Regression.md); $G$ is trained
to fool it. The value of the game is

$$
V(D, G) = E_{x \sim p_{\text{data}}}[\log D(x)] + E_{z \sim p(z)}[\log(1 - D(G(z)))],
$$

and the goal is $\min_G \max_D V(D, G)$: $D$ maximises $V$ (it is the log-likelihood of a correct classifier), $G$
minimises it.

### The optimal discriminator, derived

**Claim.** For a fixed generator, the best discriminator is

$$
D^*(x) = \frac{p_{\text{data}}(x)}{p_{\text{data}}(x) + p_g(x)} .
$$

*Proof.* Write the second expectation over $x \sim p_g$: $V = \int \big( p_{\text{data}}(x) \log D(x) + p_g(x) \log(1 - D(x)) \big) dx$.
$D$ can be chosen separately at each $x$, so maximise the integrand pointwise. For constants $a, b > 0$, the function
$y \mapsto a \log y + b \log(1 - y)$ on $(0, 1)$ has derivative $a/y - b/(1-y)$, which is zero at $y = a/(a+b)$, and
its second derivative is negative, so that is the maximum. With $a = p_{\text{data}}(x)$, $b = p_g(x)$ the claim
follows. $\square$

So the ideal discriminator is a density-ratio estimator: $D^*/(1 - D^*) = p_{\text{data}}/p_g$. Figure 20.2 draws it
for the program's example.

<figure class="mars-fig" markdown="0">
<svg viewBox="0 0 610 245" role="img" aria-label="Two densities on a line from -3 to 8: the generator's N(0,1) on the left and the data's N(4, 1.25 squared) on the right, with the optimal discriminator D*(x) drawn dashed, rising from 0 on the left through 0.5 near x = 1.85 to 1 on the right.">
<line x1="50" y1="200" x2="570" y2="200" stroke="currentColor"/>
<line x1="97.3" y1="200" x2="97.3" y2="204" stroke="currentColor"/>
<text x="97.3" y="218" font-size="12" text-anchor="middle" fill="currentColor">-2</text>
<line x1="191.8" y1="200" x2="191.8" y2="204" stroke="currentColor"/>
<text x="191.8" y="218" font-size="12" text-anchor="middle" fill="currentColor">0</text>
<line x1="286.4" y1="200" x2="286.4" y2="204" stroke="currentColor"/>
<text x="286.4" y="218" font-size="12" text-anchor="middle" fill="currentColor">2</text>
<line x1="380.9" y1="200" x2="380.9" y2="204" stroke="currentColor"/>
<text x="380.9" y="218" font-size="12" text-anchor="middle" fill="currentColor">4</text>
<line x1="475.5" y1="200" x2="475.5" y2="204" stroke="currentColor"/>
<text x="475.5" y="218" font-size="12" text-anchor="middle" fill="currentColor">6</text>
<line x1="570.0" y1="200" x2="570.0" y2="204" stroke="currentColor"/>
<text x="570.0" y="218" font-size="12" text-anchor="middle" fill="currentColor">8</text>
<polyline points="50.0,198.2 52.4,197.9 54.7,197.6 57.1,197.3 59.5,196.8 61.8,196.4 64.2,195.8 66.5,195.2 68.9,194.6 71.3,193.8 73.6,193.0 76.0,192.1 78.4,191.0 80.7,189.9 83.1,188.7 85.5,187.3 87.8,185.8 90.2,184.2 92.5,182.4 94.9,180.5 97.3,178.4 99.6,176.2 102.0,173.8 104.4,171.2 106.7,168.4 109.1,165.5 111.5,162.4 113.8,159.1 116.2,155.6 118.5,152.0 120.9,148.2 123.3,144.2 125.6,140.1 128.0,135.8 130.4,131.5 132.7,126.9 135.1,122.3 137.5,117.6 139.8,112.9 142.2,108.0 144.5,103.2 146.9,98.4 149.3,93.6 151.6,88.8 154.0,84.1 156.4,79.5 158.7,75.1 161.1,70.8 163.5,66.7 165.8,62.8 168.2,59.2 170.5,55.8 172.9,52.7 175.3,49.9 177.6,47.4 180.0,45.3 182.4,43.6 184.7,42.2 187.1,41.2 189.5,40.6 191.8,40.4 194.2,40.6 196.5,41.2 198.9,42.2 201.3,43.6 203.6,45.3 206.0,47.4 208.4,49.9 210.7,52.7 213.1,55.8 215.5,59.2 217.8,62.8 220.2,66.7 222.5,70.8 224.9,75.1 227.3,79.5 229.6,84.1 232.0,88.8 234.4,93.6 236.7,98.4 239.1,103.2 241.5,108.0 243.8,112.9 246.2,117.6 248.5,122.3 250.9,126.9 253.3,131.5 255.6,135.8 258.0,140.1 260.4,144.2 262.7,148.2 265.1,152.0 267.5,155.6 269.8,159.1 272.2,162.4 274.5,165.5 276.9,168.4 279.3,171.2 281.6,173.8 284.0,176.2 286.4,178.4 288.7,180.5 291.1,182.4 293.5,184.2 295.8,185.8 298.2,187.3 300.5,188.7 302.9,189.9 305.3,191.0 307.6,192.1 310.0,193.0 312.4,193.8 314.7,194.6 317.1,195.2 319.5,195.8 321.8,196.4 324.2,196.8 326.5,197.3 328.9,197.6 331.3,197.9 333.6,198.2 336.0,198.5 338.4,198.7 340.7,198.9 343.1,199.0 345.5,199.2 347.8,199.3 350.2,199.4 352.5,199.5 354.9,199.6 357.3,199.7 359.6,199.7 362.0,199.8 364.4,199.8 366.7,199.8 369.1,199.9 371.5,199.9 373.8,199.9 376.2,199.9 378.5,199.9 380.9,199.9 383.3,200.0 385.6,200.0 388.0,200.0 390.4,200.0 392.7,200.0 395.1,200.0 397.5,200.0 399.8,200.0 402.2,200.0 404.5,200.0 406.9,200.0 409.3,200.0 411.6,200.0 414.0,200.0 416.4,200.0 418.7,200.0 421.1,200.0 423.5,200.0 425.8,200.0 428.2,200.0 430.5,200.0 432.9,200.0 435.3,200.0 437.6,200.0 440.0,200.0 442.4,200.0 444.7,200.0 447.1,200.0 449.5,200.0 451.8,200.0 454.2,200.0 456.5,200.0 458.9,200.0 461.3,200.0 463.6,200.0 466.0,200.0 468.4,200.0 470.7,200.0 473.1,200.0 475.5,200.0 477.8,200.0 480.2,200.0 482.5,200.0 484.9,200.0 487.3,200.0 489.6,200.0 492.0,200.0 494.4,200.0 496.7,200.0 499.1,200.0 501.5,200.0 503.8,200.0 506.2,200.0 508.5,200.0 510.9,200.0 513.3,200.0 515.6,200.0 518.0,200.0 520.4,200.0 522.7,200.0 525.1,200.0 527.5,200.0 529.8,200.0 532.2,200.0 534.5,200.0 536.9,200.0 539.3,200.0 541.6,200.0 544.0,200.0 546.4,200.0 548.7,200.0 551.1,200.0 553.5,200.0 555.8,200.0 558.2,200.0 560.5,200.0 562.9,200.0 565.3,200.0 567.6,200.0 570.0,200.0" fill="none" stroke="#9cc9ea" stroke-width="2.5"/>
<polyline points="50.0,200.0 52.4,200.0 54.7,200.0 57.1,200.0 59.5,200.0 61.8,200.0 64.2,200.0 66.5,200.0 68.9,200.0 71.3,200.0 73.6,200.0 76.0,200.0 78.4,200.0 80.7,200.0 83.1,200.0 85.5,200.0 87.8,200.0 90.2,200.0 92.5,200.0 94.9,200.0 97.3,200.0 99.6,200.0 102.0,200.0 104.4,200.0 106.7,200.0 109.1,200.0 111.5,200.0 113.8,200.0 116.2,200.0 118.5,200.0 120.9,200.0 123.3,200.0 125.6,200.0 128.0,200.0 130.4,200.0 132.7,200.0 135.1,200.0 137.5,200.0 139.8,200.0 142.2,200.0 144.5,200.0 146.9,199.9 149.3,199.9 151.6,199.9 154.0,199.9 156.4,199.9 158.7,199.9 161.1,199.9 163.5,199.9 165.8,199.8 168.2,199.8 170.5,199.8 172.9,199.7 175.3,199.7 177.6,199.7 180.0,199.6 182.4,199.5 184.7,199.5 187.1,199.4 189.5,199.3 191.8,199.2 194.2,199.1 196.5,199.0 198.9,198.9 201.3,198.7 203.6,198.6 206.0,198.4 208.4,198.2 210.7,198.0 213.1,197.7 215.5,197.5 217.8,197.2 220.2,196.8 222.5,196.5 224.9,196.1 227.3,195.7 229.6,195.2 232.0,194.7 234.4,194.1 236.7,193.5 239.1,192.8 241.5,192.1 243.8,191.3 246.2,190.5 248.5,189.6 250.9,188.6 253.3,187.6 255.6,186.5 258.0,185.3 260.4,184.1 262.7,182.7 265.1,181.3 267.5,179.8 269.8,178.2 272.2,176.5 274.5,174.7 276.9,172.9 279.3,170.9 281.6,168.9 284.0,166.7 286.4,164.5 288.7,162.2 291.1,159.8 293.5,157.3 295.8,154.7 298.2,152.1 300.5,149.4 302.9,146.6 305.3,143.7 307.6,140.8 310.0,137.9 312.4,134.9 314.7,131.8 317.1,128.8 319.5,125.7 321.8,122.6 324.2,119.5 326.5,116.4 328.9,113.3 331.3,110.3 333.6,107.3 336.0,104.4 338.4,101.5 340.7,98.7 343.1,96.0 345.5,93.4 347.8,90.9 350.2,88.5 352.5,86.2 354.9,84.1 357.3,82.2 359.6,80.3 362.0,78.7 364.4,77.2 366.7,76.0 369.1,74.9 371.5,74.0 373.8,73.3 376.2,72.7 378.5,72.4 380.9,72.3 383.3,72.4 385.6,72.7 388.0,73.3 390.4,74.0 392.7,74.9 395.1,76.0 397.5,77.2 399.8,78.7 402.2,80.3 404.5,82.2 406.9,84.1 409.3,86.2 411.6,88.5 414.0,90.9 416.4,93.4 418.7,96.0 421.1,98.7 423.5,101.5 425.8,104.4 428.2,107.3 430.5,110.3 432.9,113.3 435.3,116.4 437.6,119.5 440.0,122.6 442.4,125.7 444.7,128.8 447.1,131.8 449.5,134.9 451.8,137.9 454.2,140.8 456.5,143.7 458.9,146.6 461.3,149.4 463.6,152.1 466.0,154.7 468.4,157.3 470.7,159.8 473.1,162.2 475.5,164.5 477.8,166.7 480.2,168.9 482.5,170.9 484.9,172.9 487.3,174.7 489.6,176.5 492.0,178.2 494.4,179.8 496.7,181.3 499.1,182.7 501.5,184.1 503.8,185.3 506.2,186.5 508.5,187.6 510.9,188.6 513.3,189.6 515.6,190.5 518.0,191.3 520.4,192.1 522.7,192.8 525.1,193.5 527.5,194.1 529.8,194.7 532.2,195.2 534.5,195.7 536.9,196.1 539.3,196.5 541.6,196.8 544.0,197.2 546.4,197.5 548.7,197.7 551.1,198.0 553.5,198.2 555.8,198.4 558.2,198.6 560.5,198.7 562.9,198.9 565.3,199.0 567.6,199.1 570.0,199.2" fill="none" stroke="#7ccf9a" stroke-width="2.5"/>
<polyline points="50.0,200.0 52.4,200.0 54.7,200.0 57.1,200.0 59.5,200.0 61.8,200.0 64.2,200.0 66.5,200.0 68.9,200.0 71.3,200.0 73.6,200.0 76.0,200.0 78.4,200.0 80.7,200.0 83.1,200.0 85.5,200.0 87.8,200.0 90.2,200.0 92.5,200.0 94.9,200.0 97.3,200.0 99.6,200.0 102.0,200.0 104.4,200.0 106.7,200.0 109.1,200.0 111.5,200.0 113.8,200.0 116.2,200.0 118.5,200.0 120.9,200.0 123.3,200.0 125.6,200.0 128.0,200.0 130.4,200.0 132.7,200.0 135.1,199.9 137.5,199.9 139.8,199.9 142.2,199.9 144.5,199.9 146.9,199.9 149.3,199.9 151.6,199.9 154.0,199.9 156.4,199.9 158.7,199.8 161.1,199.8 163.5,199.8 165.8,199.8 168.2,199.8 170.5,199.7 172.9,199.7 175.3,199.6 177.6,199.6 180.0,199.5 182.4,199.5 184.7,199.4 187.1,199.3 189.5,199.2 191.8,199.1 194.2,199.0 196.5,198.9 198.9,198.7 201.3,198.6 203.6,198.4 206.0,198.1 208.4,197.9 210.7,197.6 213.1,197.2 215.5,196.8 217.8,196.4 220.2,195.8 222.5,195.2 224.9,194.5 227.3,193.7 229.6,192.8 232.0,191.8 234.4,190.6 236.7,189.2 239.1,187.6 241.5,185.8 243.8,183.7 246.2,181.4 248.5,178.8 250.9,175.8 253.3,172.5 255.6,168.7 258.0,164.6 260.4,160.0 262.7,155.0 265.1,149.5 267.5,143.7 269.8,137.4 272.2,130.8 274.5,123.9 276.9,116.8 279.3,109.6 281.6,102.3 284.0,95.1 286.4,88.1 288.7,81.3 291.1,74.8 293.5,68.7 295.8,63.0 298.2,57.7 300.5,52.9 302.9,48.6 305.3,44.7 307.6,41.3 310.0,38.3 312.4,35.6 314.7,33.3 317.1,31.3 319.5,29.6 321.8,28.1 324.2,26.8 326.5,25.7 328.9,24.8 331.3,24.0 333.6,23.4 336.0,22.8 338.4,22.4 340.7,22.0 343.1,21.6 345.5,21.4 347.8,21.1 350.2,20.9 352.5,20.8 354.9,20.6 357.3,20.5 359.6,20.4 362.0,20.4 364.4,20.3 366.7,20.2 369.1,20.2 371.5,20.2 373.8,20.1 376.2,20.1 378.5,20.1 380.9,20.1 383.3,20.1 385.6,20.1 388.0,20.0 390.4,20.0 392.7,20.0 395.1,20.0 397.5,20.0 399.8,20.0 402.2,20.0 404.5,20.0 406.9,20.0 409.3,20.0 411.6,20.0 414.0,20.0 416.4,20.0 418.7,20.0 421.1,20.0 423.5,20.0 425.8,20.0 428.2,20.0 430.5,20.0 432.9,20.0 435.3,20.0 437.6,20.0 440.0,20.0 442.4,20.0 444.7,20.0 447.1,20.0 449.5,20.0 451.8,20.0 454.2,20.0 456.5,20.0 458.9,20.0 461.3,20.0 463.6,20.0 466.0,20.0 468.4,20.0 470.7,20.0 473.1,20.0 475.5,20.0 477.8,20.0 480.2,20.0 482.5,20.0 484.9,20.0 487.3,20.0 489.6,20.0 492.0,20.0 494.4,20.0 496.7,20.0 499.1,20.0 501.5,20.0 503.8,20.0 506.2,20.0 508.5,20.0 510.9,20.0 513.3,20.0 515.6,20.0 518.0,20.0 520.4,20.0 522.7,20.0 525.1,20.0 527.5,20.0 529.8,20.0 532.2,20.0 534.5,20.0 536.9,20.0 539.3,20.0 541.6,20.0 544.0,20.0 546.4,20.0 548.7,20.0 551.1,20.0 553.5,20.0 555.8,20.0 558.2,20.0 560.5,20.0 562.9,20.0 565.3,20.0 567.6,20.0 570.0,20.0" fill="none" stroke="#eea66f" stroke-width="2.5" stroke-dasharray="7 4"/>
<line x1="570" y1="20.0" x2="570" y2="200.0" stroke="currentColor" stroke-opacity="0.5"/>
<text x="576" y="24.0" font-size="11" fill="currentColor">D = 1</text>
<text x="576" y="114.0" font-size="11" fill="currentColor">0.5</text>
<text x="576" y="204.0" font-size="11" fill="currentColor">0</text>
<line x1="566" y1="110.0" x2="570" y2="110.0" stroke="currentColor"/>
<text x="177.6" y="32.0" font-size="13" text-anchor="middle" fill="currentColor">generator p_g = N(0, 1)</text>
<text x="456.5" y="56.0" font-size="13" text-anchor="start" fill="currentColor">data N(4, 1.25&#178;)</text>
<text x="286.4" y="34.4" font-size="13" text-anchor="end" fill="currentColor">D*(x)</text>
<text x="310.0" y="236" font-size="12" text-anchor="middle" fill="currentColor">x</text>
</svg>
<figcaption>Figure 20.2. The optimal discriminator for a fixed generator, D*(x) = p_data(x) / (p_data(x) + p_g(x)) (dashed, right-hand scale): near 0 where only generated points live, near 1 where only data lives, and 0.5 where the two densities are equal. Part 1 of the GAN program trains a discriminator and finds this curve.</figcaption>
</figure>

### What the generator minimises

**Theorem** (Goodfellow et al., 2014). $C(G) = \max_D V(D, G) = -\log 4 + 2 \operatorname{JSD}(p_{\text{data}} \,\|\, p_g)$,
where $\operatorname{JSD}(p \,\|\, q) = \tfrac12 \operatorname{KL}(p \,\|\, m) + \tfrac12 \operatorname{KL}(q \,\|\, m)$
with $m = (p + q)/2$ is the **Jensen-Shannon divergence**. So the global minimum of $C$ is $-\log 4$, reached exactly
when $p_g = p_{\text{data}}$.

*Proof.* Substitute $D^*$:
$C(G) = E_{p_{\text{data}}}\big[\log \frac{p_{\text{data}}}{p_{\text{data}} + p_g}\big] + E_{p_g}\big[\log \frac{p_g}{p_{\text{data}} + p_g}\big]$.
Write $p_{\text{data}} + p_g = 2m$; each term becomes $E_p[\log(p/m)] - \log 2$, so
$C(G) = \operatorname{KL}(p_{\text{data}} \,\|\, m) + \operatorname{KL}(p_g \,\|\, m) - 2\log 2 = 2\operatorname{JSD} - \log 4$.
The JSD is non-negative and zero only when the two distributions are equal. $\square$

Part 2 of the GAN program checks this by numerical integration for data $N(4, 1.25^2)$ and generator $N(0, 1)$: both
sides are $-0.1959$, with $\operatorname{JSD} = 0.5952$, close to its maximum $\log 2 = 0.6931$ because the two
distributions barely overlap. Part 1 trains a logistic discriminator with quadratic features (the log-ratio of two
Gaussians is a quadratic, so this family contains $D^*$) and finds values close to $D^*$, for example 0.251 against
0.250 at $x = 1.5$.

```python
--8<-- "books/machine-learning/ch20_gan.py"
```

```
1. generator fixed at N(0, 1); train a quadratic logistic discriminator, compare with D*
   x = 0.0: trained D 0.017   D* 0.005
   x = 1.5: trained D 0.251   D* 0.250
   x = 2.0: trained D 0.597   D* 0.622
   x = 2.5: trained D 0.894   D* 0.899
   x = 4.0: trained D 1.000   D* 1.000

2. value of the game at D*, by numerical integration
   V(D*, G) = -0.1959;  -log 4 + 2 JSD = -0.1959;  JSD = 0.5952 (at most log 2 = 0.6931)

3. GAN: generator G(z) = a z + b, z ~ N(0, 1), from a = 1, b = 0; target mean 4.0, std 1.25
   1 discriminator step(s) per generator step:
   step  500: generator mean b =  0.97, std |a| = 1.63
   step 1000: generator mean b =  2.55, std |a| = 1.65
   step 1500: generator mean b =  3.72, std |a| = 1.23
   step 2000: generator mean b =  4.15, std |a| = 0.85
   step 2500: generator mean b =  4.26, std |a| = 0.57
   step 3000: generator mean b =  4.30, std |a| = 0.41
   10 discriminator step(s) per generator step:
   step  500: generator mean b =  2.77, std |a| = 1.17
   step 1000: generator mean b =  4.14, std |a| = 0.68
   step 1500: generator mean b =  4.22, std |a| = 0.58
   step 2000: generator mean b =  4.20, std |a| = 0.74
   step 2500: generator mean b =  4.43, std |a| = 0.99
   step 3000: generator mean b =  4.44, std |a| = 1.21
```

### Training is a game, not a minimisation

In practice $D$ and $G$ are networks, and training alternates gradient steps on each. Two problems appear even in one
dimension.

**Saturation.** Early on, $D$ easily rejects fakes, $D(G(z)) \approx 0$, and $\log(1 - D(G(z)))$ is flat there: the
generator gets almost no gradient. The original paper already proposed the **non-saturating** loss: train $G$ to
maximise $\log D(G(z))$ instead, which has the same fixed point but strong gradients when $G$ is bad. Our program
uses it.

**Circling and collapse.** Part 3 trains a generator $G(z) = az + b$ against the quadratic discriminator. With one
discriminator step per generator step, the generator's mean moves to the data (4.30 against 4.0), but its spread
shrinks from 1.65 to 0.41, far below the target 1.25. The reason is visible in the gradient: the non-saturating loss
weights each generated point by $1 - D(x)$, so the points the discriminator rejects most strongly, here the left
tail, are pushed hardest towards the data, and the distribution is squeezed. A well-trained discriminator would then
notice the missing spread and push back; a lagging one does not. With ten discriminator steps per generator step,
closer to the "optimal $D$" of the theory, the spread first shrinks and then recovers to 1.21 by step 3000. Neither
run settles exactly, because simultaneous gradient play on a minimax objective need not converge at all: it can
rotate around the equilibrium. Mescheder, Geiger and Nowozin (2018) analysed which GAN training methods converge
locally, and found that the unregularised version can fail even on simple examples.

In high dimensions the worst form of the squeeze is **mode collapse**: the generator produces only a few kinds of
output that the discriminator currently accepts. Remedies include the Wasserstein GAN (Arjovsky, Chintala and Bottou,
2017), which replaces the JSD by an earth-mover distance whose gradient does not vanish when the supports are
disjoint, gradient penalties (Gulrajani et al., 2017), and spectral normalisation of the discriminator (Miyato et al.,
2018). Despite the difficulty, carefully engineered GANs such as StyleGAN (Karras, Laine and Aila, 2019) produced
very realistic face images, and GANs remain fast samplers: one network evaluation per sample. They give no
likelihood.

## 20.4 Normalizing flows: change of variables

**The question:** GANs sample but give no density; VAEs give only a bound. Is there a model with an exact,
computable likelihood that is still a neural network transforming noise?

Yes, if the transformation is **invertible**. Let $z \sim p_Z$ (say $N(0, I)$) and $x = f(z)$ with $f$ invertible and
differentiable, $z = g(x) = f^{-1}(x)$.

**Theorem (change of variables).** The density of $x$ is

$$
p_X(x) = p_Z(g(x)) \, \left| \det \frac{\partial g}{\partial x}(x) \right|,
\qquad \log p_X(x) = \log p_Z(g(x)) + \log \left| \det J_g(x) \right| .
$$

*Proof in one dimension*, for increasing $g$: $P(X \le x) = P(Z \le g(x)) = F_Z(g(x))$, and differentiating gives
$p_X(x) = p_Z(g(x))\, g'(x)$; for decreasing $g$ the same argument gives $-g'(x)$, so in general $|g'(x)|$. In $n$
dimensions the factor is the absolute Jacobian determinant, the factor by which $g$ stretches small volumes (this is
the substitution rule for multiple integrals; see a calculus text such as those on https://math.akadian.ca/books/).
Intuitively, probability mass is conserved: where $g$ squeezes space, density must rise. $\square$

Part 1 of the flow program checks the 1-D case with $z$ uniform on $(0,1)$ and $x = z^2$: $g(x) = \sqrt x$,
$g'(x) = 1/(2\sqrt x)$, so $p_X(x) = 1/(2\sqrt x)$ on $(0, 1)$, and the probability of each interval sampled from
200,000 points matches the integral of that density to three decimals.

A **normalizing flow** (Rezende and Mohamed, 2015; Dinh, Krueger and Bengio, 2014) builds $g$ as a composition of
many simple invertible layers, $g = g_K \circ \cdots \circ g_1$. By the chain rule, the Jacobian of a composition is
the product of the layers' Jacobians, and its log-determinant is a sum, so

$$
\log p_X(x) = \log p_Z(z_K) + \sum_{k=1}^{K} \log \left| \det J_{g_k}(z_{k-1}) \right|, \qquad z_0 = x,\ z_k = g_k(z_{k-1}).
$$

Training is plain maximum likelihood. The whole design problem is to make layers that are expressive, invertible, and
have Jacobian determinants that are cheap (a general $n \times n$ determinant costs $O(n^3)$).

### Coupling layers

The **affine coupling** layer of RealNVP (Dinh, Sohl-Dickstein and Bengio, 2017) splits $x$ into two halves
$(x_1, x_2)$ and sets

$$
y_1 = x_1, \qquad y_2 = x_2 \odot \exp(s(x_1)) + t(x_1),
$$

where $s$ and $t$ are *any* neural networks. It is invertible no matter what $s$ and $t$ are:
$x_1 = y_1$, then $x_2 = (y_2 - t(y_1)) \odot \exp(-s(y_1))$. Its Jacobian is block lower-triangular (the first half
does not depend on $x_2$; the second depends on $x_2$ only through the diagonal factor $\exp(s)$), and the
determinant of a triangular matrix is the product of its diagonal, so $\log|\det J| = \sum_j s_j(x_1)$: free.
Stacking coupling layers with the halves swapped or shuffled between layers lets every coordinate influence every
other. Part 2 of the program builds one in four dimensions and checks both claims: the inverse recovers $x$, and the
log-determinant of the full Jacobian, computed by finite differences, equals the sum of $s$ to six decimals. Glow
(Kingma and Dhariwal, 2018) added invertible $1 \times 1$ convolutions to mix channels.

### A 1-D flow trained by maximum likelihood

Part 3 fits a flow to data from $0.5 N(-2, 0.5^2) + 0.5 N(2, 0.5^2)$. Each of its six layers is
$u \mapsto u + w \tanh(s u + t)$ with $s > 0$ and $ws > -1$, which makes the layer strictly increasing (its derivative
$1 + ws(1 - \tanh^2) \ge 0.01$) and therefore invertible; a final affine layer scales and shifts. The density uses the
formula above with the log-derivatives summed.

```python
--8<-- "books/machine-learning/ch20_flow.py"
```

```
1. z ~ Uniform(0, 1), x = z^2: the formula says p(x) = p(z) |dz/dx| = 1 / (2 sqrt x)
   P(0.01 < x < 0.05): sampled 0.1241, formula 0.1236
   P(0.05 < x < 0.20): sampled 0.2239, formula 0.2236
   P(0.20 < x < 0.50): sampled 0.2590, formula 0.2599
   P(0.50 < x < 0.90): sampled 0.2420, formula 0.2416

2. affine coupling in 4-D: y1 = x1, y2 = x2 * exp(s(x1)) + t(x1)
   inverse(coupling(x)) == x? True
   log|det J| from the full 4x4 Jacobian -1.528995; sum of s -1.528995

3. a 6-layer flow on data 0.5 N(-2, 0.5^2) + 0.5 N(2, 0.5^2)
   step    1: train negative log-likelihood 3.2123
   step  100: train negative log-likelihood 1.4840
   step  500: train negative log-likelihood 1.4628
   step 1500: train negative log-likelihood 1.3883
   test NLL: flow 1.4147, best single Gaussian 2.1424, true density 1.4075
   density at x = -2.0: flow 0.3786, true 0.3989
   density at x =  0.0: flow 0.0012, true 0.0003
   density at x =  2.0: flow 0.3972, true 0.3989
   4000 samples by inverting g: share below 0 0.454, mean |x| 2.004 (data 2.0), std of |x| 0.510 (data about 0.5)
```

The flow reaches a held-out negative log-likelihood of 1.415 nats, against 2.142 for the best single Gaussian and
1.4075 for the true density, which is the lowest any model can achieve on average. Its density at the two modes and
in the valley is close to the truth. Sampling runs the flow backwards: draw $z \sim N(0, 1)$ and solve $g(x) = z$. Our
layers have no closed-form inverse, but $g$ is increasing, so bisection finds $x$ to machine precision in 60 halvings.
The samples are split between the modes (45.4% on the left) with the right centre and spread.

That asymmetry is typical: our flow is cheap to evaluate and costly to sample. Masked autoregressive flows
(Papamakarios, Pavlakou and Murray, 2017) have the same trade-off; inverse autoregressive flows (Kingma et al., 2016)
the opposite; coupling layers are cheap both ways but less expressive per layer. Flows give exact likelihoods, but
the requirement of invertibility (the code must have the same dimension as the data) and of cheap determinants has
kept their image samples behind GANs and diffusion models. A continuous-time view, **neural ODEs** (Chen et al., 2018)
and flow matching (20.7), removed some of these limits.

## 20.5 Diffusion models

*Level: advanced.*

**The question:** generating a whole image in one step is hard. Destroying an image by adding noise is easy. Could a
network learn to *undo* noise, one small step at a time, and so turn pure noise into data?

Sohl-Dickstein, Weiss, Maheswaranathan and Ganguli (2015) proposed exactly this, inspired by non-equilibrium
thermodynamics, and Ho, Jain and Abbeel's **denoising diffusion probabilistic models** (DDPM, 2020) made it work on
images, reporting samples of quality comparable to GANs. The idea in two halves:

- a fixed **forward process** that adds a little Gaussian noise at each of $T$ steps, until the data is pure noise;
- a learned **reverse process** that removes noise step by step, starting from pure noise.

Figure 20.3 shows what noise does to a distribution: it blurs it, until only a plain Gaussian is left.

<figure class="mars-fig" markdown="0">
<svg viewBox="0 0 600 235" role="img" aria-label="Three densities of the same two-bump data: without noise two sharp bumps at minus 2 and 2; blurred with noise of standard deviation 0.7, two wider bumps with a shallow valley; blurred with noise 2, a single broad hump.">
<line x1="40" y1="190" x2="560" y2="190" stroke="currentColor"/>
<line x1="92.0" y1="190" x2="92.0" y2="194" stroke="currentColor"/>
<text x="92.0" y="208" font-size="12" text-anchor="middle" fill="currentColor">-4</text>
<line x1="196.0" y1="190" x2="196.0" y2="194" stroke="currentColor"/>
<text x="196.0" y="208" font-size="12" text-anchor="middle" fill="currentColor">-2</text>
<line x1="300.0" y1="190" x2="300.0" y2="194" stroke="currentColor"/>
<text x="300.0" y="208" font-size="12" text-anchor="middle" fill="currentColor">0</text>
<line x1="404.0" y1="190" x2="404.0" y2="194" stroke="currentColor"/>
<text x="404.0" y="208" font-size="12" text-anchor="middle" fill="currentColor">2</text>
<line x1="508.0" y1="190" x2="508.0" y2="194" stroke="currentColor"/>
<text x="508.0" y="208" font-size="12" text-anchor="middle" fill="currentColor">4</text>
<polyline points="40.0,190.0 42.6,190.0 45.2,190.0 47.8,190.0 50.4,190.0 53.0,190.0 55.6,190.0 58.2,190.0 60.8,190.0 63.4,190.0 66.0,190.0 68.6,190.0 71.2,190.0 73.8,190.0 76.4,190.0 79.0,190.0 81.6,190.0 84.2,190.0 86.8,190.0 89.4,190.0 92.0,189.9 94.6,189.9 97.2,189.9 99.8,189.8 102.4,189.8 105.0,189.6 107.6,189.5 110.2,189.3 112.8,189.0 115.4,188.7 118.0,188.2 120.6,187.6 123.2,186.8 125.8,185.8 128.4,184.5 131.0,182.9 133.6,180.9 136.2,178.5 138.8,175.6 141.4,172.2 144.0,168.1 146.6,163.4 149.2,158.0 151.8,151.9 154.4,145.1 157.0,137.6 159.6,129.4 162.2,120.6 164.8,111.4 167.4,101.8 170.0,92.1 172.6,82.3 175.2,72.7 177.8,63.6 180.4,55.1 183.0,47.5 185.6,40.9 188.2,35.6 190.8,31.7 193.4,29.3 196.0,28.5 198.6,29.3 201.2,31.7 203.8,35.6 206.4,40.9 209.0,47.5 211.6,55.1 214.2,63.6 216.8,72.7 219.4,82.3 222.0,92.1 224.6,101.8 227.2,111.4 229.8,120.6 232.4,129.4 235.0,137.6 237.6,145.1 240.2,151.9 242.8,158.0 245.4,163.4 248.0,168.1 250.6,172.2 253.2,175.6 255.8,178.5 258.4,180.9 261.0,182.9 263.6,184.5 266.2,185.8 268.8,186.8 271.4,187.6 274.0,188.2 276.6,188.7 279.2,189.0 281.8,189.3 284.4,189.5 287.0,189.6 289.6,189.7 292.2,189.8 294.8,189.9 297.4,189.9 300.0,189.9 302.6,189.9 305.2,189.9 307.8,189.8 310.4,189.7 313.0,189.6 315.6,189.5 318.2,189.3 320.8,189.0 323.4,188.7 326.0,188.2 328.6,187.6 331.2,186.8 333.8,185.8 336.4,184.5 339.0,182.9 341.6,180.9 344.2,178.5 346.8,175.6 349.4,172.2 352.0,168.1 354.6,163.4 357.2,158.0 359.8,151.9 362.4,145.1 365.0,137.6 367.6,129.4 370.2,120.6 372.8,111.4 375.4,101.8 378.0,92.1 380.6,82.3 383.2,72.7 385.8,63.6 388.4,55.1 391.0,47.5 393.6,40.9 396.2,35.6 398.8,31.7 401.4,29.3 404.0,28.5 406.6,29.3 409.2,31.7 411.8,35.6 414.4,40.9 417.0,47.5 419.6,55.1 422.2,63.6 424.8,72.7 427.4,82.3 430.0,92.1 432.6,101.8 435.2,111.4 437.8,120.6 440.4,129.4 443.0,137.6 445.6,145.1 448.2,151.9 450.8,158.0 453.4,163.4 456.0,168.1 458.6,172.2 461.2,175.6 463.8,178.5 466.4,180.9 469.0,182.9 471.6,184.5 474.2,185.8 476.8,186.8 479.4,187.6 482.0,188.2 484.6,188.7 487.2,189.0 489.8,189.3 492.4,189.5 495.0,189.6 497.6,189.8 500.2,189.8 502.8,189.9 505.4,189.9 508.0,189.9 510.6,190.0 513.2,190.0 515.8,190.0 518.4,190.0 521.0,190.0 523.6,190.0 526.2,190.0 528.8,190.0 531.4,190.0 534.0,190.0 536.6,190.0 539.2,190.0 541.8,190.0 544.4,190.0 547.0,190.0 549.6,190.0 552.2,190.0 554.8,190.0 557.4,190.0 560.0,190.0" fill="none" stroke="#7ccf9a" stroke-width="2.5"/>
<polyline points="40.0,189.8 42.6,189.7 45.2,189.7 47.8,189.6 50.4,189.5 53.0,189.4 55.6,189.3 58.2,189.2 60.8,189.0 63.4,188.8 66.0,188.6 68.6,188.4 71.2,188.1 73.8,187.8 76.4,187.4 79.0,186.9 81.6,186.4 84.2,185.9 86.8,185.2 89.4,184.5 92.0,183.7 94.6,182.8 97.2,181.8 99.8,180.7 102.4,179.5 105.0,178.1 107.6,176.7 110.2,175.1 112.8,173.4 115.4,171.5 118.0,169.5 120.6,167.3 123.2,165.0 125.8,162.6 128.4,160.0 131.0,157.3 133.6,154.5 136.2,151.6 138.8,148.6 141.4,145.4 144.0,142.2 146.6,139.0 149.2,135.7 151.8,132.4 154.4,129.1 157.0,125.8 159.6,122.6 162.2,119.5 164.8,116.4 167.4,113.5 170.0,110.7 172.6,108.1 175.2,105.8 177.8,103.6 180.4,101.7 183.0,100.0 185.6,98.6 188.2,97.6 190.8,96.8 193.4,96.3 196.0,96.1 198.6,96.3 201.2,96.8 203.8,97.6 206.4,98.6 209.0,100.0 211.6,101.7 214.2,103.6 216.8,105.7 219.4,108.1 222.0,110.7 224.6,113.5 227.2,116.4 229.8,119.4 232.4,122.5 235.0,125.7 237.6,129.0 240.2,132.3 242.8,135.6 245.4,138.8 248.0,142.0 250.6,145.2 253.2,148.2 255.8,151.2 258.4,154.1 261.0,156.8 263.6,159.4 266.2,161.8 268.8,164.1 271.4,166.2 274.0,168.1 276.6,169.9 279.2,171.4 281.8,172.8 284.4,174.1 287.0,175.1 289.6,175.9 292.2,176.6 294.8,177.0 297.4,177.3 300.0,177.4 302.6,177.3 305.2,177.0 307.8,176.6 310.4,175.9 313.0,175.1 315.6,174.1 318.2,172.8 320.8,171.4 323.4,169.9 326.0,168.1 328.6,166.2 331.2,164.1 333.8,161.8 336.4,159.4 339.0,156.8 341.6,154.1 344.2,151.2 346.8,148.2 349.4,145.2 352.0,142.0 354.6,138.8 357.2,135.6 359.8,132.3 362.4,129.0 365.0,125.7 367.6,122.5 370.2,119.4 372.8,116.4 375.4,113.5 378.0,110.7 380.6,108.1 383.2,105.7 385.8,103.6 388.4,101.7 391.0,100.0 393.6,98.6 396.2,97.6 398.8,96.8 401.4,96.3 404.0,96.1 406.6,96.3 409.2,96.8 411.8,97.6 414.4,98.6 417.0,100.0 419.6,101.7 422.2,103.6 424.8,105.8 427.4,108.1 430.0,110.7 432.6,113.5 435.2,116.4 437.8,119.5 440.4,122.6 443.0,125.8 445.6,129.1 448.2,132.4 450.8,135.7 453.4,139.0 456.0,142.2 458.6,145.4 461.2,148.6 463.8,151.6 466.4,154.5 469.0,157.3 471.6,160.0 474.2,162.6 476.8,165.0 479.4,167.3 482.0,169.5 484.6,171.5 487.2,173.4 489.8,175.1 492.4,176.7 495.0,178.1 497.6,179.5 500.2,180.7 502.8,181.8 505.4,182.8 508.0,183.7 510.6,184.5 513.2,185.2 515.8,185.9 518.4,186.4 521.0,186.9 523.6,187.4 526.2,187.8 528.8,188.1 531.4,188.4 534.0,188.6 536.6,188.8 539.2,189.0 541.8,189.2 544.4,189.3 547.0,189.4 549.6,189.5 552.2,189.6 554.8,189.7 557.4,189.7 560.0,189.8" fill="none" stroke="#9cc9ea" stroke-width="2.5"/>
<polyline points="40.0,176.3 42.6,175.8 45.2,175.3 47.8,174.8 50.4,174.3 53.0,173.7 55.6,173.2 58.2,172.6 60.8,172.1 63.4,171.5 66.0,171.0 68.6,170.4 71.2,169.8 73.8,169.2 76.4,168.6 79.0,168.0 81.6,167.4 84.2,166.8 86.8,166.2 89.4,165.6 92.0,165.0 94.6,164.4 97.2,163.7 99.8,163.1 102.4,162.5 105.0,161.9 107.6,161.3 110.2,160.7 112.8,160.0 115.4,159.4 118.0,158.8 120.6,158.2 123.2,157.6 125.8,157.0 128.4,156.5 131.0,155.9 133.6,155.3 136.2,154.8 138.8,154.2 141.4,153.7 144.0,153.1 146.6,152.6 149.2,152.1 151.8,151.6 154.4,151.1 157.0,150.6 159.6,150.1 162.2,149.7 164.8,149.2 167.4,148.8 170.0,148.4 172.6,147.9 175.2,147.6 177.8,147.2 180.4,146.8 183.0,146.4 185.6,146.1 188.2,145.8 190.8,145.5 193.4,145.2 196.0,144.9 198.6,144.6 201.2,144.3 203.8,144.1 206.4,143.9 209.0,143.6 211.6,143.4 214.2,143.2 216.8,143.0 219.4,142.9 222.0,142.7 224.6,142.6 227.2,142.4 229.8,142.3 232.4,142.2 235.0,142.0 237.6,141.9 240.2,141.8 242.8,141.8 245.4,141.7 248.0,141.6 250.6,141.5 253.2,141.5 255.8,141.4 258.4,141.4 261.0,141.3 263.6,141.3 266.2,141.3 268.8,141.2 271.4,141.2 274.0,141.2 276.6,141.2 279.2,141.1 281.8,141.1 284.4,141.1 287.0,141.1 289.6,141.1 292.2,141.1 294.8,141.1 297.4,141.1 300.0,141.1 302.6,141.1 305.2,141.1 307.8,141.1 310.4,141.1 313.0,141.1 315.6,141.1 318.2,141.1 320.8,141.1 323.4,141.2 326.0,141.2 328.6,141.2 331.2,141.2 333.8,141.3 336.4,141.3 339.0,141.3 341.6,141.4 344.2,141.4 346.8,141.5 349.4,141.5 352.0,141.6 354.6,141.7 357.2,141.8 359.8,141.8 362.4,141.9 365.0,142.0 367.6,142.2 370.2,142.3 372.8,142.4 375.4,142.6 378.0,142.7 380.6,142.9 383.2,143.0 385.8,143.2 388.4,143.4 391.0,143.6 393.6,143.9 396.2,144.1 398.8,144.3 401.4,144.6 404.0,144.9 406.6,145.2 409.2,145.5 411.8,145.8 414.4,146.1 417.0,146.4 419.6,146.8 422.2,147.2 424.8,147.6 427.4,147.9 430.0,148.4 432.6,148.8 435.2,149.2 437.8,149.7 440.4,150.1 443.0,150.6 445.6,151.1 448.2,151.6 450.8,152.1 453.4,152.6 456.0,153.1 458.6,153.7 461.2,154.2 463.8,154.8 466.4,155.3 469.0,155.9 471.6,156.5 474.2,157.0 476.8,157.6 479.4,158.2 482.0,158.8 484.6,159.4 487.2,160.0 489.8,160.7 492.4,161.3 495.0,161.9 497.6,162.5 500.2,163.1 502.8,163.7 505.4,164.4 508.0,165.0 510.6,165.6 513.2,166.2 515.8,166.8 518.4,167.4 521.0,168.0 523.6,168.6 526.2,169.2 528.8,169.8 531.4,170.4 534.0,171.0 536.6,171.5 539.2,172.1 541.8,172.6 544.4,173.2 547.0,173.7 549.6,174.3 552.2,174.8 554.8,175.3 557.4,175.8 560.0,176.3" fill="none" stroke="#eea66f" stroke-width="2.5"/>
<line x1="235" y1="32" x2="261" y2="32" stroke="#7ccf9a" stroke-width="3"/>
<text x="267" y="36" font-size="12" fill="currentColor">data, no noise</text>
<line x1="235" y1="50" x2="261" y2="50" stroke="#9cc9ea" stroke-width="3"/>
<text x="267" y="54" font-size="12" fill="currentColor">noise sigma = 0.7</text>
<line x1="235" y1="68" x2="261" y2="68" stroke="#eea66f" stroke-width="3"/>
<text x="267" y="72" font-size="12" fill="currentColor">noise sigma = 2</text>
<text x="300.0" y="226" font-size="12" text-anchor="middle" fill="currentColor">x</text>
</svg>
<figcaption>Figure 20.3. Adding noise blurs a distribution. The data 0.5 N(-2, 0.5&#178;) + 0.5 N(2, 0.5&#178;) has two sharp bumps; with Gaussian noise of standard deviation 2 it is a single broad hump, almost a plain Gaussian. Diffusion models learn to undo the blurring one small step at a time, and score-based models learn the slope of the log of every one of these curves.</figcaption>
</figure>

### The forward process in closed form

Choose small noise levels $\beta_1, \dots, \beta_T$ (the program: $T = 100$, $\beta$ rising linearly from $10^{-4}$ to
0.1). Each step shrinks the signal slightly and adds noise:

$$
x_t = \sqrt{1 - \beta_t}\, x_{t-1} + \sqrt{\beta_t}\, \epsilon_t, \qquad \epsilon_t \sim N(0, I).
$$

Write $\alpha_t = 1 - \beta_t$ and $\bar\alpha_t = \prod_{s=1}^{t} \alpha_s$.

**Claim.** $x_t = \sqrt{\bar\alpha_t}\, x_0 + \sqrt{1 - \bar\alpha_t}\, \epsilon$ with $\epsilon \sim N(0, I)$: given
$x_0$, $x_t$ is Gaussian with mean $\sqrt{\bar\alpha_t} x_0$ and variance $1 - \bar\alpha_t$ per coordinate.

*Proof* by induction. True for $t = 1$. If it holds for $t - 1$, then
$x_t = \sqrt{\alpha_t}\big(\sqrt{\bar\alpha_{t-1}} x_0 + \sqrt{1 - \bar\alpha_{t-1}}\, \epsilon'\big) + \sqrt{1 - \alpha_t}\, \epsilon_t$.
The two noise terms are independent Gaussians, so their sum is Gaussian with variance
$\alpha_t (1 - \bar\alpha_{t-1}) + 1 - \alpha_t = 1 - \bar\alpha_t$, and the mean is $\sqrt{\bar\alpha_t} x_0$.
$\square$

So we can jump to any step directly, which makes training cheap. The variance is designed to stay near 1: with
$\bar\alpha_T \approx 0$ (0.0056 in the program), $x_T$ is nearly $N(0, I)$ whatever $x_0$ was. Part 1 of the program
runs the 100 steps one by one on 20,000 points and checks the closed form: the simulated standard deviations match
(1.4003 against 1.4013 at $t = 10$, 1.0047 against 1.0028 at $t = 100$), and the correlation with the starting point
falls from 0.988 to 0.107, which equals $\sqrt{\bar\alpha_{100}}$ times the ratio of the standard deviations,
$0.075 \cdot 1.42 / 1.00$.

### Learning to denoise: the loss derived

The reverse process is a chain $p_\theta(x_{t-1} \mid x_t) = N(\mu_\theta(x_t, t), \sigma_t^2 I)$ started at
$x_T \sim N(0, I)$, a latent-variable model with latents $x_1, \dots, x_T$. Its ELBO, derived exactly as in 20.2 with
$q(x_{1:T} \mid x_0)$ (the forward process) in the role of the encoder, splits into one KL term per step,
$\operatorname{KL}\big(q(x_{t-1} \mid x_t, x_0) \,\|\, p_\theta(x_{t-1} \mid x_t)\big)$. The forward posterior
$q(x_{t-1} \mid x_t, x_0)$ is Gaussian (a product of Gaussians in $x_{t-1}$, by Bayes' rule), with variance
$\tilde\beta_t = \frac{1 - \bar\alpha_{t-1}}{1 - \bar\alpha_t}\beta_t$ and mean

$$
\tilde\mu_t(x_t, x_0) = \frac{\sqrt{\bar\alpha_{t-1}}\, \beta_t}{1 - \bar\alpha_t}\, x_0 + \frac{\sqrt{\alpha_t}\,(1 - \bar\alpha_{t-1})}{1 - \bar\alpha_t}\, x_t .
$$

Substitute $x_0 = (x_t - \sqrt{1 - \bar\alpha_t}\, \epsilon)/\sqrt{\bar\alpha_t}$ from the closed form, and the
coefficients simplify (Exercise 9) to

$$
\tilde\mu_t = \frac{1}{\sqrt{\alpha_t}} \left( x_t - \frac{\beta_t}{\sqrt{1 - \bar\alpha_t}}\, \epsilon \right).
$$

The only unknown is the noise $\epsilon$ that was added. So Ho et al. parameterise the model the same way, with a
network $\epsilon_\theta(x_t, t)$ that predicts the noise:
$\mu_\theta(x_t, t) = \frac{1}{\sqrt{\alpha_t}}\big(x_t - \frac{\beta_t}{\sqrt{1 - \bar\alpha_t}} \epsilon_\theta(x_t, t)\big)$.
The KL between two Gaussians with the same variance is the squared distance of their means over twice the variance,
so each ELBO term becomes a weighted $\|\epsilon - \epsilon_\theta(x_t, t)\|^2$. Ho et al. found that dropping the
weights gave better samples, leaving the famously simple loss

$$
L_{\text{simple}}(\theta) = E_{x_0,\, t,\, \epsilon}\Big[ \big\| \epsilon - \epsilon_\theta\big(\sqrt{\bar\alpha_t}\, x_0 + \sqrt{1 - \bar\alpha_t}\, \epsilon,\ t\big) \big\|^2 \Big],
$$

with $t$ uniform over the steps: take a data point, pick a random step, add the right amount of noise in one jump, and
ask the network what noise was added. That is ordinary regression.

**Sampling** is ancestral: start from $x_T \sim N(0, I)$ and for $t = T, \dots, 1$ set
$x_{t-1} = \mu_\theta(x_t, t) + \sigma_t z$ with fresh noise $z$ (and no noise at the last step), with
$\sigma_t^2 = \beta_t$ as in the paper.

### A 2-D diffusion model from scratch

The program's data is a ring of eight small Gaussian clusters (radius 2, standard deviation 0.1). The noise network is
an MLP with two hidden layers of 64 ReLU units, taking $x_t$ and 16 sine and cosine features of $t$, trained with the
loss above by Adam and hand-written backpropagation.

```python
--8<-- "books/machine-learning/ch20_diffusion.py"
```

```
1. forward process: 100 steps, beta from 0.0001 to 0.1; alpha-bar_T = 0.0056
   t =  10: std of x_t simulated 1.4003, closed form 1.4013; corr(x_t, x_0) 0.988
   t =  50: std of x_t simulated 1.1384, closed form 1.1339; corr(x_t, x_0) 0.667
   t = 100: std of x_t simulated 1.0047, closed form 1.0028; corr(x_t, x_0) 0.107

2. train eps_theta(x_t, t) to predict the noise: loss = mean |eps - eps_theta|^2
   step    1: loss 3.840   (predicting 0 would give 2.0)
   step 1000: loss 0.694   (predicting 0 would give 2.0)
   step 2000: loss 0.812   (predicting 0 would give 2.0)
   step 4000: loss 0.632   (predicting 0 would give 2.0)

3. ancestral sampling from x_T ~ N(0, I) back to x_0
   pure noise N(0, I) : within 0.3 of a mode 0.048; per mode [11, 12, 10, 15, 17, 8, 9, 13]
   diffusion samples  : within 0.3 of a mode 0.813; per mode [200, 230, 186, 193, 221, 198, 233, 165]
   real data          : within 0.3 of a mode 0.986; per mode [257, 239, 251, 233, 246, 267, 246, 232]
```

The loss falls from 3.8 to about 0.6 to 0.8 (it fluctuates between batches) and cannot reach 0: at large $t$ the
noisy point says little about which noise was added, so even the best predictor is uncertain. Then 2,000 samples are
drawn by running the reverse chain from pure noise. 81.3% land within 0.3 of one of the eight cluster centres, against
4.8% for the pure noise we started from and 98.6% for real data, and every cluster gets a fair share (165 to 233
samples each), with no mode collapse. The remaining gap to real data comes from the tiny network and short training;
with more of both the share rises.

### Why diffusion took over

Diffusion models train with a stable regression loss (no adversarial game), cover all modes (they are trained with a
likelihood bound), and scale well. Improvements came quickly: learned variances and cosine noise schedules (Nichol
and Dhariwal, 2021); architecture and guidance improvements with which Dhariwal and Nichol (2021) reported diffusion
models beating GANs on ImageNet sample quality; conditioning on text with classifier-free guidance (Ho and Salimans, 2022); deterministic samplers with far
fewer steps (DDIM, Song, Meng and Ermon, 2021); and running diffusion in an autoencoder's latent space (Rombach et al.,
2022). The noise network for images is usually a U-Net ([Chapter 17](17-Convolutional-Networks.md)) or a transformer
([Chapter 19](19-Transformers.md)). The main cost is sampling: tens to hundreds of network evaluations per sample,
against one for a GAN.

## 20.6 Autoregressive models

**The question:** is there a generative model with an exact likelihood, simple training and no latent variables at
all?

The chain rule of probability, which we used for sequences in [Chapter 18](18-Sequence-Models.md), works for any data
put in some order:

$$
p_\theta(x_1, \dots, x_n) = \prod_{i=1}^{n} p_\theta(x_i \mid x_1, \dots, x_{i-1}).
$$

An **autoregressive model** learns each conditional with one network shared across positions, such as the causal
transformer of [Chapter 19](19-Transformers.md). The three properties follow immediately. **Exact likelihood:** the
log-likelihood is a sum of next-step log-probabilities, so training is maximum likelihood, the KL-minimising objective
of 20.1, with no bound and no game. **Ancestral sampling:** draw $x_1$, then $x_2$ given $x_1$, and so on. **Any data
type:** text, but also images in raster order (PixelRNN and PixelCNN, van den Oord, Kalchbrenner and Kavukcuoglu,
2016), audio samples (WaveNet, van den Oord et al., 2016), and anything that can be tokenised. A language model is a
generative model of text in exactly this sense.

The program shows all three with the simplest possible conditional: an **n-gram** model of characters, which predicts
the next character from the previous $n - 1$ by counting, with **add-$k$ smoothing** (add $k$ to every count so that
nothing has probability zero).

```python
--8<-- "books/machine-learning/ch20_autoregressive.py"
```

```
training text 685 characters, held-out text 143, alphabet 26

1. the chain rule, exactly: log2 p('the') under the order-3 model is a sum of three terms
   log2 p('t' | '~~') =  -5.170
   log2 p('h' | '~t') =  -4.700
   log2 p('e' | 'th') =  -0.768
   total -10.638 = log2_likelihood -10.638

2. bits per character (lower is better; uniform guessing = log2 V = 4.70)
    order n   train  held-out
          1   4.108     3.985
          2   2.969     2.786
          3   1.992     2.303
          4   1.659     2.470
          5   1.650     2.947

3. samples after the prompt 'the rover ': draw each next character from
   p(x_t | previous n - 1 characters), with very light smoothing (k = 0.001)
   n = 1: 'the rover  ntv a apss tknhp aiesnha re og  e piggon  esso ctht ke epnsagsgdd ,n '
   n = 2: 'the rover therobur afer thecom beseatove o t ico drnit. twe we sifopat t ce. ck '
   n = 3: 'the rover stoss, safe. and next. and and. the gues, a badvice the fourets hook, '
   n = 5: 'the rover uydleoive by itself. it short wait for advkgpenxsnuetttu.sf,ot,e wdldx'
```

Part 1 is the chain rule made concrete: $\log_2 p(\text{"the"})$ is the sum of three conditional log-probabilities,
the last of which (an "e" after "th") is large because "the" is common in the training text. Part 2 reports **bits per
character**, the average of $-\log_2 p(x_i \mid \text{context})$; $2^{\text{bits}}$ is the **perplexity**, the number of
equally likely choices the model is effectively hesitating between. Uniform guessing over 26 symbols costs 4.70 bits.
On the training text, longer contexts always help (4.11 bits for $n = 1$ down to 1.65 for $n = 5$). On held-out text the
best order is $n = 3$, with 2.30 bits (perplexity 4.9); beyond it the model has seen too few examples of each long
context, and the held-out cost rises again to 2.95 bits for $n = 5$. That is overfitting
([Chapter 8](08-Overfitting-and-Regularization.md)) caused by **sparsity**: the number of possible contexts grows like
$V^{n-1}$, and counting cannot share what it learned about "the rover" with "a rover". Part 3's samples show it: order
1 produces letter soup with the right letter frequencies, and order 3 produces word-like fragments. Order 5 shows the
failure in its purest form. Its very first draw, through the smoothing's tiny probability (about 1 in 4,000), was a "u"
after "rover ", a context the training text never contained; from there every context is unseen, each next character
is uniform, and the output is noise until, by chance, it lands back in a known context and copies a training phrase
("by itself. it ...") for a while. Neural language models replace counting by a network that maps similar contexts to similar predictions, which
is the step from n-grams to the models of Chapters 18 and 19.

**Decoding choices.** Drawing exactly from $p_\theta$ ("ancestral" or "pure" sampling) can wander into its unreliable
low-probability tail; always taking the most likely token tends to repeat itself. Common compromises reshape the
distribution at each step: a **temperature** $\tau$ divides the logits (19.5); **top-$k$** sampling keeps only the $k$
most likely tokens (Fan, Lewis and Dauphin, 2018); **nucleus** or top-$p$ sampling keeps the smallest set of tokens
whose probability adds up to $p$ (Holtzman et al., 2020). Exercise 10 writes them.

**The cost** of autoregression is sequential sampling: $n$ network evaluations for $n$ tokens, which for an image of a
million pixels is slow (one reason image models moved to diffusion), and errors cannot be revised once a token is
drawn. The ordering is also a choice the data does not make for us. For text the order is natural, and autoregressive
transformers are the dominant generative models of language.

| family | exact likelihood? | sampling cost | trained by | weak spot |
|---|---|---|---|---|
| VAE | lower bound | one decoder pass | ELBO, reparameterisation | blurry or off-manifold samples |
| GAN | no | one generator pass | minimax game | unstable training, mode collapse |
| flow | yes | one inverse pass | maximum likelihood | invertibility limits the architecture |
| diffusion | lower bound | tens to hundreds of passes | noise regression | slow sampling |
| autoregressive | yes | one pass per element | maximum likelihood | sequential sampling, fixed order |

## 20.7 Score matching and the link between diffusion and score-based models

*Level: expert.*

**The question:** a diffusion model learns to predict noise. What quantity has it really learned, and can we see the
whole process as one continuous object?

### The score

The **score** of a density is the gradient of its logarithm, $s(x) = \nabla_x \log p(x)$. (Not the "score" of
statistics' Fisher information, which is the gradient with respect to parameters.) It points uphill, towards more
probable regions, and it does not depend on the normalising constant: if $p = \tilde p / Z$, then
$\nabla \log p = \nabla \log \tilde p$. That makes it attractive for models whose $Z$ is intractable.

**Score matching** (Hyvärinen, 2005) fits a model $s_\theta(x)$ to the true score by minimising
$E_p\big[\|s_\theta(x) - \nabla \log p(x)\|^2\big]$, which Hyvärinen showed, by integration by parts, can be rewritten
without knowing $\nabla \log p$; the rewritten form needs the trace of the Jacobian of $s_\theta$, expensive in high
dimensions. Vincent (2011) found a cheaper route through noise.

### Denoising score matching

Blur the data with Gaussian noise: $\tilde x = x + \sigma \epsilon$, giving the density
$q_\sigma(\tilde x) = \int N(\tilde x; x, \sigma^2 I)\, p(x)\, dx$.

**Claim** (Vincent, 2011). $E\big[\nabla_{\tilde x} \log q(\tilde x \mid x) \,\big|\, \tilde x\big] = \nabla \log q_\sigma(\tilde x)$,
where $\nabla_{\tilde x} \log q(\tilde x \mid x) = -(\tilde x - x)/\sigma^2 = -\epsilon/\sigma$. Consequently, the
minimiser over functions $s$ of $E\big[\|s(\tilde x) + \epsilon/\sigma\|^2\big]$ is the true score of the blurred data.

*Proof.* $\nabla q_\sigma(\tilde x) = \int \nabla_{\tilde x} q(\tilde x \mid x)\, p(x)\, dx = \int q(\tilde x \mid x)\, \nabla_{\tilde x} \log q(\tilde x \mid x)\, p(x)\, dx$.
Divide by $q_\sigma(\tilde x)$ and note that $q(\tilde x \mid x) p(x) / q_\sigma(\tilde x) = p(x \mid \tilde x)$ by
Bayes' rule: the left side becomes $\nabla \log q_\sigma(\tilde x)$ and the right side the conditional expectation
$E[\nabla \log q(\tilde x \mid x) \mid \tilde x]$. The minimiser of an expected squared error $E\|s(\tilde x) - Y\|^2$
over functions of $\tilde x$ is the conditional mean $E[Y \mid \tilde x]$ (the regression function of
[Chapter 4](04-Linear-Regression.md)), which we just computed. $\square$

So regressing $-\epsilon/\sigma$ on $\tilde x$ learns the score, and no density is ever evaluated. Compare with
20.5: the diffusion network regresses $\epsilon$ on $x_t = \sqrt{\bar\alpha_t} x_0 + \sqrt{1 - \bar\alpha_t}\, \epsilon$,
so by the same argument it learns
$\epsilon_\theta(x_t, t) \approx -\sqrt{1 - \bar\alpha_t}\, \nabla \log q_t(x_t)$. **Predicting the noise is
estimating the score**, up to a known scale. A closely related identity, **Tweedie's formula**,
$E[x \mid \tilde x] = \tilde x + \sigma^2 \nabla \log q_\sigma(\tilde x)$, says the best denoiser is one step up the
score (Exercise 11; Efron, 2011, tells its history).

The score program works in one dimension with the two-bump data of 20.4, where the score of the blurred data is known
exactly (blurring a Gaussian mixture gives another one, with each variance increased by $\sigma^2$).

```python
--8<-- "books/machine-learning/ch20_score.py"
```

```
1. E[-(x~ - x)/sigma^2 | x~] versus the true score of the blurred data, sigma = 0.7
   x~ = -3.0: average of targets   1.346   true score   1.351
   x~ = -2.0: average of targets   0.006   true score   0.000
   x~ = -1.0: average of targets  -1.321   true score  -1.327
   x~ =  0.0: average of targets  -0.001   true score   0.000
   x~ =  0.5: average of targets   1.707   true score   1.687
   x~ =  2.0: average of targets  -0.000   true score  -0.000

2. a model s(x) = sum of 41 Gaussian bumps, fitted to the noisy targets by least squares
   x     :   -4.0   -3.0   -2.0   -1.0    0.0    1.0    2.0    3.0    4.0
   fitted:   2.67   1.37   0.01  -1.33  -0.12   1.33   0.00  -1.37  -2.75
   true  :   2.70   1.35   0.00  -1.33   0.00   1.33  -0.00  -1.35  -2.70

3. Langevin dynamics x <- x + (eta/2) score(x) + sqrt(eta) z, 5000 chains
   one small noise level, 300 steps, chains started in the left mode:
      share right 0.005, mean |x| 1.986, std of |x| 0.508
   annealed over 10 levels from sigma 4 to 0.05, 30 steps each, started anywhere:
      share right 0.500, mean |x| 2.008, std of |x| 0.507
   the data, for comparison:
      share right 0.485, mean |x| 2.015, std of |x| 0.504

4. probability-flow ODE from sigma = 6 down to 0, no randomness after the start:
      share right 0.500, mean |x| 1.965, std of |x| 0.488
```

Part 1 checks Vincent's identity by simulation: averaging the targets $-\epsilon/\sigma$ over the points that landed
near a given $\tilde x$ gives the true score there (for example 1.346 against 1.351 at $\tilde x = -3$). Part 2 fits a
score model, a sum of 41 Gaussian bumps with free weights, by denoising score matching. Because the model is linear in
its weights, the loss is a least-squares problem and is solved exactly; the fitted score matches the true one to within
0.05 at every grid point except the valley, where the error is 0.12.

### Sampling with the score: Langevin dynamics

Given a score, **Langevin dynamics** samples by noisy gradient ascent on $\log p$:

$$
x \leftarrow x + \frac{\eta}{2} \nabla \log p(x) + \sqrt{\eta}\, z, \qquad z \sim N(0, I).
$$

For small $\eta$ and many steps its distribution converges to $p$ (under regularity conditions; it is the
discretisation of a stochastic differential equation whose stationary distribution is $p$). Part 3 shows its
weakness and its fix. Started in the left mode, 300 steps with the score of nearly clean data leave 99.5% of the
chains on the left: the valley between the modes has density 0.0003 and the chains essentially never cross it, so
the sample has the wrong proportions although every individual chain looks fine. Song and Ermon (2019) proposed
**annealed Langevin dynamics**: run Langevin with the score of heavily blurred data first (one broad hump, Figure 20.3,
where moving between modes is easy), then with less and less noise. Started anywhere, 10 levels of 30 steps give 50.0%
on the right and the right centre and spread, matching the data. Their noise-conditional score networks learn
$s_\theta(x, \sigma)$ for all levels at once by denoising score matching: the same structure as a diffusion model.

### One picture: stochastic differential equations

Song, Sohl-Dickstein, Kingma, Kumar, Ermon and Poole (2021) unified the two lines. Let the number of noise steps go to
infinity: the forward process becomes a **stochastic differential equation** (SDE)
$dx = f(x, t)\, dt + g(t)\, dW$, with $W$ a Brownian motion, that turns data into noise over $t \in [0, 1]$. DDPM's
chain corresponds to a "variance-preserving" SDE, and adding noise without shrinking ($x_\sigma = x_0 + \sigma
\epsilon$, as in our score program) to a "variance-exploding" one. A result of Anderson (1982) says the time-reversed
process is also an SDE,

$$
dx = \big[ f(x, t) - g(t)^2\, \nabla_x \log p_t(x) \big]\, dt + g(t)\, d\bar W,
$$

run backwards in time, and its only unknown is the score of each blurred distribution $p_t$, which is what the
network learns. DDPM sampling and annealed Langevin are two discretisations of this reverse SDE.

The same paper showed that the deterministic **probability-flow ODE**

$$
\frac{dx}{dt} = f(x, t) - \tfrac{1}{2} g(t)^2\, \nabla_x \log p_t(x)
$$

has the same marginal distributions $p_t$ at every time as the SDE. For the variance-exploding case with noise level
$\sigma$ as the clock this is $dx/d\sigma = -\sigma \nabla \log q_\sigma(x)$. Part 4 of the program integrates it with
the exact score from $\sigma = 6$ down to 0, starting from the exact blurred distribution and adding no noise at all
after the start: the result has 50.0% on the right, mean $|x|$ of 1.965 and spread 0.488, close to the data (2.0 and
0.5). The ODE view turns a diffusion model into a continuous normalizing flow (20.4), so it gives exact likelihoods by
integrating the change in log-density, and allows fast deterministic samplers with large steps (DDIM is one).

### The research frontier

This is an active field; the following are directions with published results, not settled conclusions.

- **Fewer sampling steps.** Distilling a sampler into fewer steps (Salimans and Ho, 2022) and **consistency models**
  (Song, Dhariwal, Chen and Sutskever, 2023), which learn to map any point of an ODE trajectory straight to its end,
  aim at one- or few-step generation with diffusion-like quality.
- **Flow matching** (Lipman et al., 2023) and **rectified flow** (Liu, Gong and Liu, 2023) learn the velocity field of
  an ODE that carries noise to data directly, by regression, with straighter paths than diffusion's; they are
  continuous normalizing flows trained without simulating the ODE.
- **Discrete data.** Diffusion for text and other discrete data (for example Austin et al., 2021) is less mature than
  for images; autoregressive models still dominate language.
- **Open questions.** Why diffusion models generalise rather than memorise their training set is studied but not fully
  understood: with an exact score of the *empirical* distribution, the reverse process would reproduce training
  examples exactly, so the network's imperfect, smooth score is doing something useful. Measuring sample quality
  reliably (20.1) also remains unsolved, and evaluation choices change rankings.

## Check yourself

??? question "1. Derive the inverse-CDF sampler for the distribution with density p(x) = 2x on (0, 1), and check it."

    $F(x) = \int_0^x 2t\, dt = x^2$, so $F^{-1}(u) = \sqrt u$: sample $u$ uniform and return $\sqrt u$. Check: the mean
    should be $\int_0^1 2x^2 dx = 2/3$; `np.sqrt(np.random.default_rng(0).uniform(size=10**6)).mean()` gives about
    0.6667. Note it is the reverse of Part 1 of the flow program, where $x = z^2$ had density $1/(2\sqrt x)$.

??? question "2. Show that KL(N(mu, sigma^2) || N(0, 1)) = (mu^2 + sigma^2 - 1 - log sigma^2) / 2, and evaluate it for mu = 1, sigma = 0.5."

    $\operatorname{KL} = E_q[\log q - \log p]$ with $\log q(z) = -\tfrac12\log(2\pi\sigma^2) - (z-\mu)^2/(2\sigma^2)$ and
    $\log p(z) = -\tfrac12 \log(2\pi) - z^2/2$. Under $q$, $E[(z - \mu)^2] = \sigma^2$ and $E[z^2] = \mu^2 + \sigma^2$.
    So $\operatorname{KL} = -\tfrac12 \log \sigma^2 - \tfrac12 + \tfrac12(\mu^2 + \sigma^2)$, as claimed. For $\mu = 1$,
    $\sigma = 0.5$: $\tfrac12(1 + 0.25 - 1 - \log 0.25) = \tfrac12(0.25 + 1.386) = 0.818$ nats.

??? question "3. Show that the gap between log p(x) and the ELBO is exactly KL(q(z|x) || p(z|x)), and explain what that means for training the encoder."

    It is the last line of the derivation in 20.2: $\log p_\theta(x) = \text{ELBO}(x) + \operatorname{KL}(q_\phi(z \mid x) \,\|\, p_\theta(z \mid x))$.
    Since $\log p_\theta(x)$ does not depend on $\phi$, maximising the ELBO over the encoder's parameters is the same as
    minimising the KL from $q_\phi$ to the true posterior: the encoder is trained to do approximate Bayesian inference.
    The bound is tight only if the Gaussian family can represent the true posterior.

??? question "4. For data N(4, 1.25^2) and generator N(0, 1), where is D*(x) = 1/2? What does D* do far to the left?"

    $D^* = 1/2$ where the two densities are equal; solving numerically gives $x \approx 1.85$ (Figure 20.2). Far to the
    left the generator density is much larger than the data's, so $D^* \to 0$; but because the data's variance is
    larger, its density eventually exceeds the generator's again on both sides far out (the log-ratio is a quadratic
    with positive leading coefficient, $0.18x^2 + 2.56x - 5.34$, whose roots are 1.85 and $-16.1$), so $D^*$ rises
    back above 1/2 for $x < -16.1$, where both densities are astronomically small.

??? question "5. If p_data and p_g have disjoint supports, what is JSD, and what does that imply for the original GAN loss?"

    With disjoint supports, $m = (p + q)/2$ equals $p/2$ on $p$'s support and $q/2$ on $q$'s, so
    $\operatorname{KL}(p \,\|\, m) = \log 2$ and likewise for $q$: $\operatorname{JSD} = \log 2$, its maximum, for every
    pair of disjoint distributions, however near or far. The generator's objective is then constant, giving no
    gradient towards the data. In high dimensions, distributions concentrated on thin manifolds are often
    effectively disjoint early in training, which is the argument of Arjovsky and Bottou (2017) for the Wasserstein
    distance, which does change smoothly with how far apart the distributions are.

??? question "6. A flow is x = a z + b with z ~ N(0, 1) and a != 0. Use the change-of-variables formula to get p(x)."

    $g(x) = (x - b)/a$, $|g'(x)| = 1/|a|$. So $p_X(x) = N((x-b)/a; 0, 1)/|a| = \frac{1}{|a|\sqrt{2\pi}} \exp(-(x-b)^2/(2a^2))$,
    which is $N(b, a^2)$, as expected. The log-determinant term $-\log|a|$ is what stops maximum likelihood from
    cheating by shrinking all data to the centre of the Gaussian.

??? question "7. Prove that an affine coupling layer's Jacobian determinant is exp(sum of s), and that the layer is invertible for any networks s and t."

    Order the variables as $(x_1, x_2)$. $\partial y_1/\partial x_1 = I$, $\partial y_1/\partial x_2 = 0$,
    $\partial y_2/\partial x_2 = \operatorname{diag}(\exp(s(x_1)))$, and $\partial y_2/\partial x_1$ is some matrix. So
    the Jacobian is block lower-triangular with identity and diagonal blocks, and its determinant is the product of the
    diagonal entries, $\prod_j e^{s_j} = e^{\sum_j s_j}$, never zero. Invertibility: $x_1 = y_1$ is read off, and then
    $s(x_1)$ and $t(x_1)$ can be computed, so $x_2 = (y_2 - t)\odot e^{-s}$. Neither step inverts a network.

??? question "8. With a constant beta = 0.02 for T = 1000 steps, what is alpha-bar_T? With the program's schedule?"

    $\bar\alpha_T = 0.98^{1000} = e^{1000 \ln 0.98} \approx e^{-20.2} \approx 1.7 \times 10^{-9}$: the data is completely
    destroyed. The program's 100 linearly rising steps give $\bar\alpha_{100} = 0.0056$, so its $x_T$ keeps a
    correlation of about 0.1 with $x_0$ (Part 1 printed 0.107). Sampling starts from $N(0, I)$ anyway, a small mismatch
    that the last few reverse steps absorb.

??? question "9. Derive the epsilon form of the forward posterior mean."

    Put $x_0 = (x_t - \sqrt{1 - \bar\alpha_t}\, \epsilon)/\sqrt{\bar\alpha_t}$ into $\tilde\mu_t$. The $x_t$ coefficient
    becomes $\frac{\sqrt{\bar\alpha_{t-1}}\beta_t}{(1 - \bar\alpha_t)\sqrt{\bar\alpha_t}} + \frac{\sqrt{\alpha_t}(1 - \bar\alpha_{t-1})}{1 - \bar\alpha_t}$.
    Since $\sqrt{\bar\alpha_t} = \sqrt{\alpha_t}\sqrt{\bar\alpha_{t-1}}$, the first fraction is
    $\frac{\beta_t}{(1 - \bar\alpha_t)\sqrt{\alpha_t}}$, and the sum is
    $\frac{\beta_t + \alpha_t(1 - \bar\alpha_{t-1})}{(1 - \bar\alpha_t)\sqrt{\alpha_t}} = \frac{1 - \bar\alpha_t}{(1 - \bar\alpha_t)\sqrt{\alpha_t}} = \frac{1}{\sqrt{\alpha_t}}$,
    using $\beta_t + \alpha_t - \bar\alpha_t = 1 - \bar\alpha_t$. The $\epsilon$ coefficient is
    $-\frac{\sqrt{\bar\alpha_{t-1}}\beta_t \sqrt{1 - \bar\alpha_t}}{(1 - \bar\alpha_t)\sqrt{\bar\alpha_t}} = -\frac{\beta_t}{\sqrt{\alpha_t}\sqrt{1 - \bar\alpha_t}}$.
    Together: $\tilde\mu_t = \frac{1}{\sqrt{\alpha_t}}\big(x_t - \frac{\beta_t}{\sqrt{1 - \bar\alpha_t}}\epsilon\big)$.

??? question "10. Write the code: sample a token from logits with temperature, top-k and top-p (nucleus) filtering."

    ```python
    import numpy as np

    def sample(logits, rng, temperature=1.0, top_k=None, top_p=None):
        z = np.asarray(logits, float) / temperature
        p = np.exp(z - z.max()); p /= p.sum()
        order = np.argsort(-p)                    # most likely first
        keep = np.ones(len(p), bool)
        if top_k is not None:
            keep[order[top_k:]] = False
        if top_p is not None:                     # smallest set with total probability >= top_p
            cum = np.cumsum(p[order])
            cut = np.searchsorted(cum, top_p) + 1
            keep[order[cut:]] = False
        p = np.where(keep, p, 0); p /= p.sum()
        return rng.choice(len(p), p=p)

    rng = np.random.default_rng(0)
    logits = np.log([0.5, 0.3, 0.1, 0.06, 0.04])
    for kw in ({}, {"top_k": 2}, {"top_p": 0.85}, {"temperature": 0.3}):
        draws = [sample(logits, rng, **kw) for _ in range(20000)]
        print(kw, np.bincount(draws, minlength=5) / 20000)
    ```

    With no filtering the frequencies are about 0.5, 0.3, 0.1, 0.06, 0.04. Top-2 keeps tokens 0 and 1, renormalised to
    0.625 and 0.375. Top-p with 0.85 keeps 0, 1, 2 (cumulative 0.9 is the first total at or above 0.85), giving 0.556,
    0.333, 0.111. Temperature 0.3 sharpens the distribution: probabilities proportional to $p^{1/0.3}$, about 0.84,
    0.15 and almost nothing else.

??? question "11. Write the code: check Tweedie's formula E[x | x~] = x~ + sigma^2 score(x~) for the two-bump data of the score program."

    ```python
    import numpy as np

    rng = np.random.default_rng(3)
    M, S0, sigma = np.array([-2.0, 2.0]), 0.5, 0.7
    x = M[rng.integers(0, 2, 400_000)] + S0 * rng.normal(size=400_000)
    xt = x + sigma * rng.normal(size=x.size)

    def score(z):                                  # exact score of the blurred mixture
        v = S0**2 + sigma**2
        logc = -0.5 * (z[:, None] - M) ** 2 / v
        r = np.exp(logc - logc.max(1, keepdims=True)); r /= r.sum(1, keepdims=True)
        return (r * (M - z[:, None]) / v).sum(1)

    for c in (-3.0, -1.0, 0.5, 2.5):
        sel = np.abs(xt - c) < 0.05
        print(c, x[sel].mean().round(3), (c + sigma**2 * score(np.array([c])))[0].round(3))
    ```

    The two columns agree to about 0.01 (sampling noise): averaging the clean points behind a noisy observation is the
    same as taking one step of size $\sigma^2$ up the score. Near $\tilde x = 0$ the best guess is between the modes,
    although no clean point is there: the posterior mean is not a typical sample.

??? question "12. An n-gram model gets 2.30 bits per character on held-out text. What is its perplexity, and why can a higher-order model do worse?"

    Perplexity is $2^{2.30} \approx 4.9$: on average the model is as uncertain as a fair choice among about five
    characters. A higher-order model has many more contexts ($V^{n-1}$), each seen fewer times; on held-out text it
    meets contexts it saw rarely or never, where its estimates are poor or uniform. Its training cost keeps falling
    (1.65 bits at $n = 5$) while the held-out cost rises (2.95): overfitting from sparse counts, which smoothing,
    backing off to shorter contexts, or a neural model that shares statistics between similar contexts all reduce.

## What you learned

- A generative model is a distribution $p_\theta$ fitted to data; maximum likelihood minimises
  $\operatorname{KL}(p_{\text{data}} \,\|\, p_\theta)$; models differ in whether they give densities, samples or both.
- A VAE maximises the ELBO, reconstruction minus the KL from the encoder to the prior; the gap to the log-likelihood is
  the encoder's error as an approximate posterior; the reparameterisation trick gives low-variance gradients.
- A GAN's optimal discriminator is $p_{\text{data}}/(p_{\text{data}} + p_g)$, and the generator then minimises
  $2\operatorname{JSD} - \log 4$; alternating gradient steps play a game that can circle or collapse.
- A normalizing flow gives exact likelihoods through the change-of-variables formula; coupling layers make the
  Jacobian triangular and its determinant free.
- A diffusion model adds noise in a fixed forward process (closed form in one jump) and learns to remove it by
  regressing the added noise; sampling runs the reverse chain from pure noise.
- Autoregressive models factor the joint distribution by the chain rule, with exact likelihood and sequential
  sampling; language models are generative models of this kind.
- Predicting noise is estimating the score $\nabla \log p_t$; Langevin dynamics, the reverse SDE and the probability-flow
  ODE all sample from it, unifying diffusion and score-based models.

**Next:** [Chapter 21](21-Learning-Theory.md), learning theory, which asks why any of these models, fitted to a finite
sample, should work on data it has never seen.

## Further reading

- I. Goodfellow, Y. Bengio and A. Courville, *Deep Learning*, 2016: chapter 20 (deep generative models).
- K. P. Murphy, *Probabilistic Machine Learning: Advanced Topics*, 2023: the part on generative models (VAEs,
  autoregressive models, flows, energy-based and diffusion models, GANs).
- C. M. Bishop, *Pattern Recognition and Machine Learning*, 2006: chapter 9 (EM and the lower bound) and chapter 11
  (sampling methods).
- D. P. Kingma and M. Welling, "Auto-encoding variational Bayes", 2013 (ICLR 2014); D. J. Rezende, S. Mohamed and
  D. Wierstra, "Stochastic backpropagation and approximate inference in deep generative models", ICML 2014.
- I. Goodfellow, J. Pouget-Abadie, M. Mirza, B. Xu, D. Warde-Farley, S. Ozair, A. Courville and Y. Bengio,
  "Generative adversarial nets", NeurIPS 2014; M. Arjovsky, S. Chintala and L. Bottou, "Wasserstein generative
  adversarial networks", ICML 2017; L. Mescheder, A. Geiger and S. Nowozin, "Which training methods for GANs do
  actually converge?", ICML 2018.
- D. J. Rezende and S. Mohamed, "Variational inference with normalizing flows", ICML 2015; L. Dinh, J. Sohl-Dickstein
  and S. Bengio, "Density estimation using Real NVP", ICLR 2017; G. Papamakarios, E. Nalisnick, D. J. Rezende,
  S. Mohamed and B. Lakshminarayanan, "Normalizing flows for probabilistic modeling and inference", *Journal of Machine
  Learning Research* 22, 2021.
- J. Sohl-Dickstein, E. Weiss, N. Maheswaranathan and S. Ganguli, "Deep unsupervised learning using nonequilibrium
  thermodynamics", ICML 2015; J. Ho, A. Jain and P. Abbeel, "Denoising diffusion probabilistic models", NeurIPS 2020.
- A. Hyvärinen, "Estimation of non-normalized statistical models by score matching", *Journal of Machine Learning
  Research* 6, 2005; P. Vincent, "A connection between score matching and denoising autoencoders", *Neural
  Computation* 23, 2011; Y. Song and S. Ermon, "Generative modeling by estimating gradients of the data
  distribution", NeurIPS 2019; Y. Song, J. Sohl-Dickstein, D. P. Kingma, A. Kumar, S. Ermon and B. Poole,
  "Score-based generative modeling through stochastic differential equations", ICLR 2021.
- B. D. O. Anderson, "Reverse-time diffusion equation models", *Stochastic Processes and their Applications* 12, 1982;
  B. Efron, "Tweedie's formula and selection bias", *Journal of the American Statistical Association* 106, 2011.
- A. van den Oord, N. Kalchbrenner and K. Kavukcuoglu, "Pixel recurrent neural networks", ICML 2016; A. van den Oord et
  al., "WaveNet: a generative model for raw audio", 2016; A. Holtzman, J. Buys, L. Du, M. Forbes and Y. Choi, "The
  curious case of neural text degeneration", ICLR 2020.
- Y. Lipman, R. T. Q. Chen, H. Ben-Hamu, M. Nickel and M. Le, "Flow matching for generative modeling", ICLR 2023;
  Y. Song, P. Dhariwal, M. Chen and I. Sutskever, "Consistency models", ICML 2023; R. Rombach, A. Blattmann, D. Lorenz,
  P. Esser and B. Ommer, "High-resolution image synthesis with latent diffusion models", CVPR 2022.
- On this site: [Chapter 13](13-Clustering.md) (EM and its lower bound), [Chapter 14](14-Dimensionality-Reduction.md)
  (autoencoders), [Chapter 19](19-Transformers.md) (the transformer as an autoregressive model),
  [Chapter 21](21-Learning-Theory.md), and the probability and calculus books at https://math.akadian.ca/books/.
