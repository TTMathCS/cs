# 19. Transformers

*Recurrent networks read one step at a time, and attention ([Chapter 18](18-Sequence-Models.md)) was a helper that
let them look back. In 2017 a team at Google asked what happens if attention does all the work and the recurrence is
thrown away. The answer, the transformer, now underlies most models of language and many of images, sound and
proteins. This chapter derives every part of it from the question it answers: scaled dot-product attention and the
square root, multiple heads, positions, the block with its residuals and layer norms, causal masks. Then you will
build a small character-level transformer in NumPy, check its gradients, train it, sample from it, write the
tokenizer that real models use, see how GPT, BERT and vision transformers are pretrained, and face the cost of
attention that grows with the square of the length.*

!!! abstract "In this chapter"
    **You will learn:**

    - what problem "Attention Is All You Need" (Vaswani et al. 2017) solved, and why parallel training mattered
    - scaled dot-product attention, with the proof of why the scores are divided by the square root of the dimension
    - multi-head attention; why attention ignores order (proved) and how positional encodings fix it
    - the transformer block: residual connections, layer norm (with its backward pass), the MLP; encoder, decoder and causal masks
    - a tiny character-level transformer built, gradient-checked and trained from scratch
    - byte-pair encoding from scratch, and the pretraining objectives of GPT, BERT and vision transformers
    - the quadratic cost of attention and the ideas that tame it, including the exact tiled algorithm of FlashAttention

    **You need:** [Chapter 18](18-Sequence-Models.md) (attention, seq2seq, teacher forcing),
    [Chapter 16](16-Training-Deep-Networks.md) (normalisation, residual connections, Adam and warmup from
    [Chapter 5](05-Optimization.md)), and matrix products from [Chapter 3](03-The-Math-Toolkit.md).

    **Levels:** 19.1 to 19.3 are intermediate; 19.4 to 19.7 are intermediate to advanced; 19.8 is advanced.

## 19.1 "Attention Is All You Need": the problem it solved

**The question:** by 2016 the best translation systems were recurrent encoder-decoders with attention. They worked.
What was wrong with them?

Two things, both from 18.4. First, **recurrence is sequential**. To compute the state at position 100 the network
must first compute positions 1 to 99. During training the whole sentence is known in advance, yet the GPU, which is
built to do thousands of multiplications at once, has to wait for each step. Training on more data took
proportionally longer, with no way to spread one sequence's work across the hardware. Second, **paths are long**.
For information from word 3 to influence word 40 it must survive 37 recurrent updates; gating helps, but long paths
still make long-range patterns harder to learn.

Attention had already shown the alternative: in 18.6 every output reached every input in a single step. Vaswani,
Shazeer, Parmar, Uszkoreit, Jones, Gomez, Kaiser and Polosukhin's paper "Attention Is All You Need" (2017) built a
translation model from attention alone. In **self-attention** the positions of one sequence attend to each other, so
each word's new representation is a weighted mixture of all the words in its sentence, computed for every word at
once with a few matrix products. No step waits for another. The path between any two positions has length 1.

The paper reports 28.4 BLEU on the WMT 2014 English-to-German test set with its "big" model, better than the previous
best results including ensembles, and that its base model trained in 12 hours on one machine with 8 GPUs, a fraction
of the cost of the recurrent and convolutional systems it compared against. The architecture spread quickly beyond
translation: to language models (GPT, 2018), to pretrained encoders (BERT, 2018-19), to images (ViT, 2020), and
further.

| | recurrent layer | self-attention layer |
|---|---|---|
| sequential steps per layer | $n$ | 1 |
| longest path between two positions | $n$ | 1 |
| work per layer | $O(n d^2)$ | $O(n^2 d + n d^2)$ |

This table, in the spirit of the paper's own comparison, also shows the price: work that grows with $n^2$ in the
sequence length $n$, the subject of 19.8.

## 19.2 Scaled dot-product attention, derived

**The question:** in Bahdanau's attention a small network scored each (decoder state, encoder state) pair. What is
the simplest score that works, and how should it be scaled?

Every position $i$ has a vector $x_i \in \mathbb{R}^d$; stack them as the rows of $X \in \mathbb{R}^{n \times d}$.
Three learned matrices turn each $x_i$ into three roles:

- a **query** $q_i = x_i W_Q$: what position $i$ is looking for,
- a **key** $k_j = x_j W_K$: what position $j$ offers, to be matched against queries,
- a **value** $v_j = x_j W_V$: what position $j$ hands over if it is chosen.

$W_Q$ and $W_K$ are $d \times d_k$ and $W_V$ is $d \times d_v$. The score of query $i$ against key $j$ is the dot
product $q_i \cdot k_j$, a similarity as in [Chapter 3](03-The-Math-Toolkit.md). The weights are a softmax over $j$,
and the output is the weighted average of the values. For all positions at once, with $Q = X W_Q$, $K = X W_K$,
$V = X W_V$:

$$
\operatorname{Attention}(Q, K, V) = \operatorname{softmax}\!\left( \frac{Q K^\top}{\sqrt{d_k}} \right) V ,
$$

where the softmax acts on each row of the $n \times n$ score matrix. That is two matrix products and a softmax, which
GPUs do very fast, and every row is independent of the others, so all positions are computed in parallel.

### A hand-sized example

Part 1 of the program takes three tokens with $d_k = 2$ and $Q = K$ with rows $(1, 0)$, $(0, 1)$, $(1, 1)$, and values
$(1, 0)$, $(0, 2)$, $(3, 3)$. For the first query, the scores against the three keys are $1, 0, 1$, divided by
$\sqrt 2$: $0.707, 0, 0.707$. The softmax gives $e^{0.707} = 2.028$, $e^0 = 1$, $2.028$, which sum to $5.056$, so the
weights are $0.401, 0.198, 0.401$. The output is $0.401 (1, 0) + 0.198 (0, 2) + 0.401 (3, 3) = (1.604, 1.599)$. Each
output is a blend of the values, leaning towards the positions whose keys match the query.

```python
--8<-- "books/machine-learning/ch19_attention.py"
```

```
1. three tokens, d_k = 2, by hand
   scores Q K^T / sqrt 2 =
       0.707  0.000  0.707
       0.000  0.707  0.707
       0.707  0.707  1.414
   weights (rows sum to 1) =
       0.401  0.198  0.401
       0.198  0.401  0.401
       0.248  0.248  0.503
   output =
       1.604  1.599
       1.401  2.006
       1.759  2.007

2. random q, k with unit-variance entries, 16 keys: what the softmax sees
       d  var(q.k)  max weight  (scaled)  grad size  (scaled)
       4       4.0       0.426     0.235     0.3224    0.2970
      64      64.6       0.843     0.246     0.1762    0.3051
     512     513.7       0.948     0.245     0.0696    0.3056

3. multi-head attention: h heads of size d/h cost about the same as one of size d
   input (6, 8), output (6, 8), 2 attention maps of shape (6, 6)
   weights: 4 d^2 = 256 whatever h is
   head 0 row 0: [0.136 0.105 0.15  0.205 0.096 0.308]
   head 1 row 0: [0.111 0.088 0.092 0.12  0.129 0.46 ]   (different heads look at different places)

4. without positions, attention ignores order: f(X permuted) == f(X) permuted? True

5. sinusoidal positions, d = 16
   PE(0)[:4] = [0. 1. 0. 1.],  PE(1)[:4] = [0.841 0.54  0.311 0.95 ]
   one rotation R_7 maps every PE(pos) to PE(pos + 7)? True
   PE(20) . PE(20 + j) for j = 0, 1, 2, 5, 10, 20: 8.00, 7.49, 6.37, 6.14, 3.65, 5.78

6. causal mask: outputs 0..3 unchanged when tokens 4, 5 change? True | output 5 changed? True
   head 0 weights with the mask:
       1.00  0.00  0.00  0.00  0.00  0.00
       0.34  0.66  0.00  0.00  0.00  0.00
       0.41  0.22  0.37  0.00  0.00  0.00
       0.30  0.15  0.24  0.31  0.00  0.00
       0.27  0.05  0.15  0.42  0.11  0.00
       0.18  0.13  0.12  0.18  0.20  0.19

7. tiled attention with an online softmax equals the usual one:
   block   1: max difference 4.4e-16
   block  32: max difference 2.2e-16
   block 100: max difference 3.9e-16
   block 256: max difference 3.9e-16
   memory for the score matrix, 16-bit numbers, one head:
   n =   1024:          2 MiB
   n =   8192:        128 MiB
   n =  65536:       8192 MiB
```

### Why the square root of $d_k$

**Claim.** If the entries of $q$ and $k$ are independent, with mean 0 and variance 1, then $q \cdot k$ has mean 0 and
variance $d_k$.

*Proof.* $q \cdot k = \sum_{i=1}^{d_k} q_i k_i$. Each term has mean $E[q_i] E[k_i] = 0$ by independence, and
variance $E[q_i^2 k_i^2] - 0 = E[q_i^2] E[k_i^2] = 1$. The terms are independent of each other, so their variances
add: $\operatorname{Var}(q \cdot k) = d_k$. $\square$

So the typical size of a score is $\sqrt{d_k}$: 8 when $d_k = 64$. Why does that hurt? A softmax of numbers spread
over a range of $\pm 16$ is almost one-hot: the largest score takes nearly all the weight. And the softmax's Jacobian
(18.6) is $\operatorname{diag}(\alpha) - \alpha \alpha^\top$, which is zero when $\alpha$ is one-hot, so the gradient
reaching the queries and keys nearly vanishes, the same saturation that hurts sigmoids
([Chapter 16](16-Training-Deep-Networks.md)). Dividing by $\sqrt{d_k}$ brings the variance back to 1 for every $d_k$.
The paper gives this variance argument in a footnote.

Part 2 of the program measures it with 16 random keys. Without scaling, the average largest weight grows from 0.43
($d = 4$) to 0.95 ($d = 512$), and the size of the softmax Jacobian falls from 0.32 to 0.07. With scaling, both stay
put (about 0.24 and 0.30) whatever the dimension. Real queries and keys are not independent unit Gaussians, but
initialisation and layer norm keep them close to that scale. The paper offers this argument to explain an earlier
observation it cites (Britz et al., 2017): without scaling, dot-product attention did worse than additive attention
for large $d_k$.

<figure class="play" data-play="attnmap"><span class="ai-tag">AI-created</span><figcaption>Try it: tap a word to see how much it attends to each other word. The weights are made up to show the idea, not taken from a real model.</figcaption></figure>

## 19.3 Multi-head attention; positional encodings

**The question:** one softmax gives one weighted average per position. But a word may need several things at once:
its subject, the previous word, the matching bracket. How can one layer look in several places?

### Multi-head attention

Run $h$ attention operations, called **heads**, in parallel, each with its own projections of size
$d_k = d_v = d/h$, then concatenate their outputs and mix them with one more matrix $W_O$ ($d \times d$):

$$
\operatorname{head}_i = \operatorname{Attention}(X W_Q^{(i)}, X W_K^{(i)}, X W_V^{(i)}), \qquad
\operatorname{MultiHead}(X) = [\operatorname{head}_1, \dots, \operatorname{head}_h]\, W_O .
$$

Each head has its own softmax, so different heads can attend to different positions (part 3 of the program shows two
heads' weights for the same query, differently spread). The cost hardly changes with $h$: the projections are four
$d \times d$ matrices in total, $4d^2$ weights, however the $d$ columns are split among heads, and the score
computations add up to the same $n^2 d$ multiplications. In code, the heads are slices of one big $Q$, $K$ and $V$.
The base model of the 2017 paper has $d = 512$ and $h = 8$ heads of size 64.

Studies of trained models found heads with recognisable jobs: attending to the previous token, to syntactic relations,
to rare words. Clark, Khandelwal, Levy and Manning (2019) documented such heads in BERT. Many heads can also be
removed after training with little loss (Michel, Levy and Neubig, 2019), so not every head is essential.

### Attention ignores order

**Claim.** Self-attention without positional information is **permutation equivariant**: permuting the input
positions permutes the outputs the same way.

*Proof.* Let $P$ be a permutation matrix, so $PX$ reorders the rows of $X$. Then $Q' = PXW_Q = PQ$, $K' = PK$,
$V' = PV$, and $Q' K'^\top = P Q K^\top P^\top$: the same scores with rows and columns both reordered. A row-wise
softmax commutes with reordering rows and with reordering the entries inside every row the same way, so
$\operatorname{softmax}(PQK^\top P^\top) = P \operatorname{softmax}(QK^\top) P^\top$. Multiplying by $V' = PV$ gives
$P \operatorname{softmax}(QK^\top) P^\top P V = P \operatorname{softmax}(QK^\top) V$, using $P^\top P = I$. $\square$

The MLP and layer norm act on each position separately, so the whole transformer without positions is permutation
equivariant: "dog bites man" and "man bites dog" would give the same set of vectors in a different order. Part 4 of the
program checks it. That is a feature for sets (point clouds, for example), but language needs order.

### Positional encodings

The fix is to add to each token's vector a vector that depends on its position, $x_i + p_i$. The 2017 paper used fixed
**sinusoidal** encodings: for position $\mathrm{pos}$ and $i = 0, 1, \dots, d/2 - 1$,

$$
p_{\mathrm{pos}, 2i} = \sin\!\left( \frac{\mathrm{pos}}{10000^{2i/d}} \right), \qquad
p_{\mathrm{pos}, 2i+1} = \cos\!\left( \frac{\mathrm{pos}}{10000^{2i/d}} \right).
$$

Each pair of coordinates is a point on a circle, turning at its own speed: the first pair once every $2\pi$ positions,
the last pair about 10,000 times more slowly. Together they work like the hands of a clock with many hands, giving
every position a distinct pattern.

**Claim.** For every offset $k$ there is a fixed matrix $R_k$, not depending on $\mathrm{pos}$, with
$p_{\mathrm{pos}+k} = R_k\, p_{\mathrm{pos}}$.

*Proof.* Write $\omega_i = 10000^{-2i/d}$. By the angle-addition formulas,
$\sin(\omega_i(\mathrm{pos}+k)) = \sin(\omega_i \mathrm{pos}) \cos(\omega_i k) + \cos(\omega_i \mathrm{pos}) \sin(\omega_i k)$
and $\cos(\omega_i(\mathrm{pos}+k)) = \cos(\omega_i \mathrm{pos}) \cos(\omega_i k) - \sin(\omega_i \mathrm{pos}) \sin(\omega_i k)$.
So each pair is rotated by the $2 \times 2$ matrix with rows $(\cos \omega_i k, \sin \omega_i k)$ and
$(-\sin \omega_i k, \cos \omega_i k)$, which depends only on $k$. $R_k$ is the block-diagonal matrix of these
rotations. $\square$

The authors' stated hope was that this makes attending by *relative* position easy to learn, since a shift is a fixed
linear map. Part 5 of the program builds $R_7$ and checks it on all positions, and shows that the dot product
$p_{20} \cdot p_{20+j}$ is largest at $j = 0$ and generally falls with distance (though not monotonically). The paper
also tried learned position vectors, one trainable vector per position, and reports nearly identical results; GPT
and BERT use learned ones, as does our tiny model in 19.5. Later work moved position into the attention scores
themselves: relative positions (Shaw, Uszkoreit and Vaswani, 2018), rotary embeddings that rotate queries and keys
by position-dependent angles (Su et al., 2021, "RoFormer"), and linear distance penalties (Press, Smith and Lewis,
2021, "ALiBi").

## 19.4 The transformer block

**The question:** attention mixes information between positions. What else does a layer need, and how are layers
stacked so that dozens of them can be trained?

A **transformer block** has two sub-layers, each wrapped in a residual connection
([Chapter 16](16-Training-Deep-Networks.md)) and a layer normalisation:

1. **Multi-head self-attention**: positions exchange information.
2. **A position-wise MLP**: the same two-layer network applied to every position separately,
   $\operatorname{MLP}(x) = \phi(x W_1 + c_1) W_2 + c_2$, with $W_1$ of size $d \times 4d$ and $W_2$ of size
   $4d \times d$, and $\phi$ a ReLU (2017) or the smoother GELU (Hendrycks and Gimpel, 2016) used by GPT and BERT.

In the **pre-norm** form drawn in Figure 19.1,

$$
\begin{aligned}
x &\leftarrow x + \operatorname{MultiHead}(\operatorname{LN}(x)), \\
x &\leftarrow x + \operatorname{MLP}(\operatorname{LN}(x)).
\end{aligned}
$$

<figure class="mars-fig" markdown="0">
<svg viewBox="0 0 460 470" role="img" aria-label="A pre-norm transformer block drawn from bottom to top: the input goes through layer norm and multi-head attention, and the result is added to the input by a residual connection; that sum goes through layer norm and an MLP, and is added again by a second residual connection. The output has the same shape as the input.">
<text x="230" y="455" font-size="13" text-anchor="middle" fill="currentColor">token embeddings + positions (n x d)</text>
<line x1="230.0" y1="440.0" x2="230.0" y2="412.0" stroke="currentColor" stroke-width="1.4"/><polygon points="230.0,404.0 234.0,412.0 226.0,412.0" fill="currentColor"/>
<rect x="130.0" y="370" width="200" height="34" rx="6" fill="#9cc9ea" fill-opacity="0.7" stroke="currentColor"/>
<text x="230" y="392" font-size="14" text-anchor="middle" fill="currentColor">layer norm</text>
<line x1="230.0" y1="370.0" x2="230.0" y2="352.0" stroke="currentColor" stroke-width="1.4"/><polygon points="230.0,344.0 234.0,352.0 226.0,352.0" fill="currentColor"/>
<rect x="130.0" y="310" width="200" height="34" rx="6" fill="#eea66f" fill-opacity="0.7" stroke="currentColor"/>
<text x="230" y="332" font-size="14" text-anchor="middle" fill="currentColor">multi-head attention</text>
<line x1="230.0" y1="310.0" x2="230.0" y2="294.0" stroke="currentColor" stroke-width="1.4"/><polygon points="230.0,286.0 234.0,294.0 226.0,294.0" fill="currentColor"/>
<circle cx="230" cy="274" r="12" fill="none" stroke="currentColor" stroke-width="1.4"/>
<text x="230" y="279" font-size="16" text-anchor="middle" fill="currentColor">+</text>
<polyline points="230,420 80,420 80,274 216,274" fill="none" stroke="currentColor" stroke-width="1.4"/>
<polygon points="218,274 210,270 210,278" fill="currentColor"/>
<line x1="230.0" y1="262.0" x2="230.0" y2="242.0" stroke="currentColor" stroke-width="1.4"/><polygon points="230.0,234.0 234.0,242.0 226.0,242.0" fill="currentColor"/>
<rect x="130.0" y="200" width="200" height="34" rx="6" fill="#9cc9ea" fill-opacity="0.7" stroke="currentColor"/>
<text x="230" y="222" font-size="14" text-anchor="middle" fill="currentColor">layer norm</text>
<line x1="230.0" y1="200.0" x2="230.0" y2="182.0" stroke="currentColor" stroke-width="1.4"/><polygon points="230.0,174.0 234.0,182.0 226.0,182.0" fill="currentColor"/>
<rect x="130.0" y="140" width="200" height="34" rx="6" fill="#7ccf9a" fill-opacity="0.7" stroke="currentColor"/>
<text x="230" y="162" font-size="14" text-anchor="middle" fill="currentColor">MLP (d to 4d to d)</text>
<line x1="230.0" y1="140.0" x2="230.0" y2="124.0" stroke="currentColor" stroke-width="1.4"/><polygon points="230.0,116.0 234.0,124.0 226.0,124.0" fill="currentColor"/>
<circle cx="230" cy="104" r="12" fill="none" stroke="currentColor" stroke-width="1.4"/>
<text x="230" y="109" font-size="16" text-anchor="middle" fill="currentColor">+</text>
<polyline points="230,250 80,250 80,104 216,104" fill="none" stroke="currentColor" stroke-width="1.4"/>
<polygon points="218,104 210,100 210,108" fill="currentColor"/>
<line x1="230.0" y1="92.0" x2="230.0" y2="66.0" stroke="currentColor" stroke-width="1.4"/><polygon points="230.0,58.0 234.0,66.0 226.0,66.0" fill="currentColor"/>
<text x="230" y="48" font-size="13" text-anchor="middle" fill="currentColor">to the next block (same shape, n x d)</text>
<text x="70" y="350" font-size="12" text-anchor="end" fill="currentColor">residual</text>
<text x="70" y="180" font-size="12" text-anchor="end" fill="currentColor">residual</text>
<text x="338" y="322" font-size="12" fill="currentColor">tokens exchange</text>
<text x="338" y="338" font-size="12" fill="currentColor">information</text>
<text x="338" y="152" font-size="12" fill="currentColor">each token on</text>
<text x="338" y="168" font-size="12" fill="currentColor">its own</text>
<rect x="20" y="85" width="420" height="355" rx="10" fill="none" stroke="currentColor" stroke-opacity="0.35" stroke-dasharray="6 4"/>
<text x="430" y="432" font-size="12" text-anchor="end" fill="currentColor">one block, repeated N times</text>
</svg>
<figcaption>Figure 19.1. One transformer block (the pre-norm form used by GPT-2 and most later models; the 2017 paper put the layer norm after each addition instead). Attention is the only place where positions exchange information; the MLP works on each position separately. The residual path runs straight from bottom to top.</figcaption>
</figure>

Each part has a job. **Attention** is the only place where positions talk to each other. The **MLP**, which holds
about two thirds of the block's weights ($8d^2$ of the $12d^2$, ignoring biases), transforms each position's vector
on its own; experiments by Geva et al. (2021) suggest its layers act partly as key-value memories. The **residual
connections** give an unobstructed path from the output back to the input, so gradients reach the bottom layers of a
deep stack (16.6) and each block only has to learn a correction. **Layer normalisation** keeps the scale of the
vectors steady.

### Layer normalisation

Batch normalisation ([Chapter 16](16-Training-Deep-Networks.md)) normalises each feature over the examples of a
batch, which is awkward for sequences of varying length and for generating one token at a time. **Layer norm** (Ba,
Kiros and Hinton, 2016) normalises each position's vector over its own $d$ features:

$$
\mu = \frac{1}{d} \sum_{j=1}^{d} x_j, \qquad \sigma^2 = \frac{1}{d} \sum_{j=1}^{d} (x_j - \mu)^2, \qquad
\hat x_j = \frac{x_j - \mu}{\sqrt{\sigma^2 + \epsilon}}, \qquad y_j = \gamma_j \hat x_j + \beta_j ,
$$

with a learned gain $\gamma$ and bias $\beta$ and a small $\epsilon$ (we use $10^{-5}$) to avoid dividing by zero. It
does not depend on other examples, so training and generation behave identically.

**Its backward pass.** Let $g = \partial L / \partial y$ and $\hat g = \gamma \odot g = \partial L / \partial \hat x$.
Write $s = \sqrt{\sigma^2 + \epsilon}$. Then

$$
\frac{\partial L}{\partial x} = \frac{1}{s} \Big( \hat g - \operatorname{mean}(\hat g) - \hat x \odot
\operatorname{mean}(\hat g \odot \hat x) \Big),
$$

where "mean" averages over the $d$ features. *Derivation.* $\hat x_j = (x_j - \mu)/s$ depends on $x_m$ directly and
through $\mu$ and $s$. Using $\partial \mu / \partial x_m = 1/d$ and $\partial s / \partial x_m = (x_m - \mu)/(d s) =
\hat x_m / d$, the quotient rule gives
$\partial \hat x_j / \partial x_m = \frac{1}{s} \big( \mathbb{1}[j = m] - \frac{1}{d} - \frac{\hat x_j \hat x_m}{d} \big)$.
Multiplying by $\hat g_j$ and summing over $j$ gives the formula. It has a clean meaning: the gradient is the
incoming one with its mean removed and its component along $\hat x$ removed, since shifting or rescaling $x$ does
not change $\hat x$. The program's `layernorm` method implements exactly this, and the gradient check in 19.5
confirms it.

**Pre-norm or post-norm.** The 2017 paper put the normalisation *after* each residual addition,
$x \leftarrow \operatorname{LN}(x + \operatorname{Sublayer}(x))$, called **post-norm**, and needed a learning-rate
warmup to train ([Chapter 5](05-Optimization.md)). GPT-2 (Radford et al., 2019) moved it to the input of each
sub-layer, as above, plus a final layer norm. Xiong et al. (2020) analysed why: in post-norm, the gradients near the
output are large at initialisation, while pre-norm keeps them well behaved, so training is more stable and needs less
warmup. Most large models since use pre-norm or a close variant.

### Encoder, decoder and the causal mask

The original transformer is an encoder-decoder, like seq2seq in 18.5, with 6 blocks on each side in the base model:

- **Encoder blocks** use unrestricted self-attention: every source position sees every other one, before and after
  it (bidirectional).
- **Decoder blocks** have three sub-layers: **masked** self-attention over the target produced so far,
  **cross-attention** in which queries come from the decoder and keys and values from the encoder's output (exactly
  Bahdanau's arrangement in 18.6), then the MLP.

The **causal mask** is what makes a decoder trainable in parallel. When predicting token $t+1$, the model must not
see tokens $t+1, t+2, \dots$, or it could simply copy the answer. So before the softmax, every score $S_{ij}$ with
$j > i$ is set to $-\infty$; its weight becomes $e^{-\infty} = 0$ and the row still sums to 1 over $j \le i$.

<figure class="mars-fig" markdown="0">
<svg viewBox="0 0 460 250" role="img" aria-label="A 6 by 6 grid of attention weights with a causal mask. Row i is a query position, column j a key position. Cells above the diagonal are grey and have weight 0. On and below the diagonal the cells are shaded by their weight, and each row sums to 1; the first row is 1.00 on the diagonal.">
<text x="192" y="20" font-size="13" text-anchor="middle" fill="currentColor">key position (attended to)</text>
<text x="107.0" y="35" font-size="12" text-anchor="middle" fill="currentColor">0</text>
<text x="141.0" y="35" font-size="12" text-anchor="middle" fill="currentColor">1</text>
<text x="175.0" y="35" font-size="12" text-anchor="middle" fill="currentColor">2</text>
<text x="209.0" y="35" font-size="12" text-anchor="middle" fill="currentColor">3</text>
<text x="243.0" y="35" font-size="12" text-anchor="middle" fill="currentColor">4</text>
<text x="277.0" y="35" font-size="12" text-anchor="middle" fill="currentColor">5</text>
<text x="82" y="62" font-size="12" text-anchor="end" fill="currentColor">0</text>
<rect x="90" y="40" width="34" height="34" fill="#eea66f" fill-opacity="1.00" stroke="currentColor" stroke-opacity="0.25"/>
<text x="107.0" y="61" font-size="11" text-anchor="middle" fill="currentColor">1.00</text>
<rect x="124" y="40" width="34" height="34" fill="currentColor" fill-opacity="0.08" stroke="currentColor" stroke-opacity="0.25"/>
<rect x="158" y="40" width="34" height="34" fill="currentColor" fill-opacity="0.08" stroke="currentColor" stroke-opacity="0.25"/>
<rect x="192" y="40" width="34" height="34" fill="currentColor" fill-opacity="0.08" stroke="currentColor" stroke-opacity="0.25"/>
<rect x="226" y="40" width="34" height="34" fill="currentColor" fill-opacity="0.08" stroke="currentColor" stroke-opacity="0.25"/>
<rect x="260" y="40" width="34" height="34" fill="currentColor" fill-opacity="0.08" stroke="currentColor" stroke-opacity="0.25"/>
<text x="82" y="96" font-size="12" text-anchor="end" fill="currentColor">1</text>
<rect x="90" y="74" width="34" height="34" fill="#eea66f" fill-opacity="0.34" stroke="currentColor" stroke-opacity="0.25"/>
<text x="107.0" y="95" font-size="11" text-anchor="middle" fill="currentColor">0.34</text>
<rect x="124" y="74" width="34" height="34" fill="#eea66f" fill-opacity="0.66" stroke="currentColor" stroke-opacity="0.25"/>
<text x="141.0" y="95" font-size="11" text-anchor="middle" fill="currentColor">0.66</text>
<rect x="158" y="74" width="34" height="34" fill="currentColor" fill-opacity="0.08" stroke="currentColor" stroke-opacity="0.25"/>
<rect x="192" y="74" width="34" height="34" fill="currentColor" fill-opacity="0.08" stroke="currentColor" stroke-opacity="0.25"/>
<rect x="226" y="74" width="34" height="34" fill="currentColor" fill-opacity="0.08" stroke="currentColor" stroke-opacity="0.25"/>
<rect x="260" y="74" width="34" height="34" fill="currentColor" fill-opacity="0.08" stroke="currentColor" stroke-opacity="0.25"/>
<text x="82" y="130" font-size="12" text-anchor="end" fill="currentColor">2</text>
<rect x="90" y="108" width="34" height="34" fill="#eea66f" fill-opacity="0.41" stroke="currentColor" stroke-opacity="0.25"/>
<text x="107.0" y="129" font-size="11" text-anchor="middle" fill="currentColor">0.41</text>
<rect x="124" y="108" width="34" height="34" fill="#eea66f" fill-opacity="0.22" stroke="currentColor" stroke-opacity="0.25"/>
<text x="141.0" y="129" font-size="11" text-anchor="middle" fill="currentColor">0.22</text>
<rect x="158" y="108" width="34" height="34" fill="#eea66f" fill-opacity="0.37" stroke="currentColor" stroke-opacity="0.25"/>
<text x="175.0" y="129" font-size="11" text-anchor="middle" fill="currentColor">0.37</text>
<rect x="192" y="108" width="34" height="34" fill="currentColor" fill-opacity="0.08" stroke="currentColor" stroke-opacity="0.25"/>
<rect x="226" y="108" width="34" height="34" fill="currentColor" fill-opacity="0.08" stroke="currentColor" stroke-opacity="0.25"/>
<rect x="260" y="108" width="34" height="34" fill="currentColor" fill-opacity="0.08" stroke="currentColor" stroke-opacity="0.25"/>
<text x="82" y="164" font-size="12" text-anchor="end" fill="currentColor">3</text>
<rect x="90" y="142" width="34" height="34" fill="#eea66f" fill-opacity="0.30" stroke="currentColor" stroke-opacity="0.25"/>
<text x="107.0" y="163" font-size="11" text-anchor="middle" fill="currentColor">0.30</text>
<rect x="124" y="142" width="34" height="34" fill="#eea66f" fill-opacity="0.15" stroke="currentColor" stroke-opacity="0.25"/>
<text x="141.0" y="163" font-size="11" text-anchor="middle" fill="currentColor">0.15</text>
<rect x="158" y="142" width="34" height="34" fill="#eea66f" fill-opacity="0.24" stroke="currentColor" stroke-opacity="0.25"/>
<text x="175.0" y="163" font-size="11" text-anchor="middle" fill="currentColor">0.24</text>
<rect x="192" y="142" width="34" height="34" fill="#eea66f" fill-opacity="0.31" stroke="currentColor" stroke-opacity="0.25"/>
<text x="209.0" y="163" font-size="11" text-anchor="middle" fill="currentColor">0.31</text>
<rect x="226" y="142" width="34" height="34" fill="currentColor" fill-opacity="0.08" stroke="currentColor" stroke-opacity="0.25"/>
<rect x="260" y="142" width="34" height="34" fill="currentColor" fill-opacity="0.08" stroke="currentColor" stroke-opacity="0.25"/>
<text x="82" y="198" font-size="12" text-anchor="end" fill="currentColor">4</text>
<rect x="90" y="176" width="34" height="34" fill="#eea66f" fill-opacity="0.27" stroke="currentColor" stroke-opacity="0.25"/>
<text x="107.0" y="197" font-size="11" text-anchor="middle" fill="currentColor">0.27</text>
<rect x="124" y="176" width="34" height="34" fill="#eea66f" fill-opacity="0.05" stroke="currentColor" stroke-opacity="0.25"/>
<text x="141.0" y="197" font-size="11" text-anchor="middle" fill="currentColor">0.05</text>
<rect x="158" y="176" width="34" height="34" fill="#eea66f" fill-opacity="0.15" stroke="currentColor" stroke-opacity="0.25"/>
<text x="175.0" y="197" font-size="11" text-anchor="middle" fill="currentColor">0.15</text>
<rect x="192" y="176" width="34" height="34" fill="#eea66f" fill-opacity="0.42" stroke="currentColor" stroke-opacity="0.25"/>
<text x="209.0" y="197" font-size="11" text-anchor="middle" fill="currentColor">0.42</text>
<rect x="226" y="176" width="34" height="34" fill="#eea66f" fill-opacity="0.11" stroke="currentColor" stroke-opacity="0.25"/>
<text x="243.0" y="197" font-size="11" text-anchor="middle" fill="currentColor">0.11</text>
<rect x="260" y="176" width="34" height="34" fill="currentColor" fill-opacity="0.08" stroke="currentColor" stroke-opacity="0.25"/>
<text x="82" y="232" font-size="12" text-anchor="end" fill="currentColor">5</text>
<rect x="90" y="210" width="34" height="34" fill="#eea66f" fill-opacity="0.18" stroke="currentColor" stroke-opacity="0.25"/>
<text x="107.0" y="231" font-size="11" text-anchor="middle" fill="currentColor">0.18</text>
<rect x="124" y="210" width="34" height="34" fill="#eea66f" fill-opacity="0.13" stroke="currentColor" stroke-opacity="0.25"/>
<text x="141.0" y="231" font-size="11" text-anchor="middle" fill="currentColor">0.13</text>
<rect x="158" y="210" width="34" height="34" fill="#eea66f" fill-opacity="0.12" stroke="currentColor" stroke-opacity="0.25"/>
<text x="175.0" y="231" font-size="11" text-anchor="middle" fill="currentColor">0.12</text>
<rect x="192" y="210" width="34" height="34" fill="#eea66f" fill-opacity="0.18" stroke="currentColor" stroke-opacity="0.25"/>
<text x="209.0" y="231" font-size="11" text-anchor="middle" fill="currentColor">0.18</text>
<rect x="226" y="210" width="34" height="34" fill="#eea66f" fill-opacity="0.20" stroke="currentColor" stroke-opacity="0.25"/>
<text x="243.0" y="231" font-size="11" text-anchor="middle" fill="currentColor">0.20</text>
<rect x="260" y="210" width="34" height="34" fill="#eea66f" fill-opacity="0.19" stroke="currentColor" stroke-opacity="0.25"/>
<text x="277.0" y="231" font-size="11" text-anchor="middle" fill="currentColor">0.19</text>
<text x="30" y="142" font-size="13" text-anchor="middle" fill="currentColor" transform="rotate(-90 30 142)">query position</text>
<text x="314" y="80" font-size="12" fill="currentColor">grey: score set to</text>
<text x="314" y="96" font-size="12" fill="currentColor">minus infinity,</text>
<text x="314" y="112" font-size="12" fill="currentColor">weight exactly 0</text>
</svg>
<figcaption>Figure 19.2. Causal attention weights of one head, from part 6 of the first program. Position t may only attend to positions 0 to t, so the upper triangle is masked out before the softmax; this is what lets a decoder be trained on every position of a sequence at once.</figcaption>
</figure>

With the mask, one forward pass over a whole training sequence produces predictions for *every* position, each using
only its own past, and the loss is the sum over positions: teacher forcing (18.5) for all $n$ steps at once. A
recurrent decoder needs $n$ sequential steps for the same work. Part 6 of the program checks the guarantee: changing
tokens 4 and 5 leaves outputs 0 to 3 exactly unchanged.

**Three families** grew from the two halves. *Encoder-only* models (BERT) read a whole text bidirectionally and are
used to classify or extract. *Decoder-only* models (GPT) are causal language models that generate. *Encoder-decoder*
models (the original, and T5 by Raffel et al., 2020) map one text to another.

## 19.5 A tiny transformer from scratch

**The question:** can we build all of this, run it, check that its gradients are right, and watch it learn?

The program builds a decoder-only model of the GPT kind for characters:

1. **Embeddings.** Each of the $V = 25$ characters of the training text has a learned vector of size $d = 48$, and each
   of the 32 positions a learned position vector; they are added.
2. **Two pre-norm blocks**, each with 4-head causal self-attention ($d_k = 12$) and an MLP of width $4d = 192$ with
   ReLU.
3. **A final layer norm** and a linear map to 25 logits per position; softmax cross-entropy against the next
   character.

Its backward pass comes from a small reverse-mode autodiff on arrays, the same idea as in
[Chapter 15](15-Neural-Networks-and-Backpropagation.md) and [Chapter 18](18-Sequence-Models.md), extended with the
operations a transformer needs: batched matrix products for $QK^\top$ and $AV$, transposes and reshapes to split and
join heads, the softmax, layer norm and an embedding lookup. Each operation's backward rule is two or three lines,
derived in this chapter or the last.

```python
--8<-- "books/machine-learning/ch19_tiny_transformer.py"
```

```
text: 457 characters, vocabulary 25, context 32

1. gradient check on a tiny model (d = 8, 2 heads, 1 block):
   token embedding : worst relative error over 5 entries 4.0e-10
   W_qkv           : worst relative error over 5 entries 1.6e-08
   layer-norm gain : worst relative error over 5 entries 1.1e-09
   output W        : worst relative error over 5 entries 1.9e-09

2. changing characters 20.. leaves the predictions at positions 0..19 unchanged? True

3. training a 2-block, 4-head, d = 48 model (60,192 parameters), Adam, batch 16
   loss before training 3.177 (uniform guessing: ln 25 = 3.219)
   step  50: loss 1.867
   step 100: loss 1.076
   step 150: loss 0.592
   step 200: loss 0.358
   step 250: loss 0.273

4. samples (temperature 0.5):
   'the rover took a picture of the rock and sent ight ht rover slept and '
   'at night the rover slept and the sky was dark. at dawn the rover woke'
```

**Part 1** checks the gradient of the full model, a single block with $d = 8$ and 2 heads, against centred finite
differences on random entries of four different parameters, including the query-key-value matrix (whose gradient
passes through the softmax, the batched products and the head reshapes) and a layer-norm gain. The largest relative
error is about $10^{-8}$: the backward pass is right. **Part 2** checks causality on the full-size model: changing
characters from position 20 on does not change any prediction at positions 0 to 19.

**Part 3** trains the model, with 60,192 parameters, for 250 Adam steps at learning rate 0.003 on random windows of
32 characters. Before training the loss is 3.177, close to $\ln 25 = 3.219$, the loss of guessing uniformly, as it
should be with small random weights. Figure 19.3 plots the printed losses.

<figure class="mars-fig" markdown="0">
<svg viewBox="0 0 540 270" role="img" aria-label="Training loss of the tiny transformer: 3.18 before training, close to the uniform-guessing line at 3.22, then 1.87 at step 50, 1.08 at 100, 0.59 at 150, 0.36 at 200 and 0.27 at 250.">
<line x1="70" y1="220" x2="510" y2="220" stroke="currentColor"/>
<line x1="70" y1="20" x2="70" y2="220" stroke="currentColor"/>
<line x1="66" y1="220.0" x2="70" y2="220.0" stroke="currentColor"/>
<text x="62" y="224.0" font-size="12" text-anchor="end" fill="currentColor">0</text>
<line x1="66" y1="162.9" x2="70" y2="162.9" stroke="currentColor"/>
<text x="62" y="166.9" font-size="12" text-anchor="end" fill="currentColor">1</text>
<line x1="66" y1="105.7" x2="70" y2="105.7" stroke="currentColor"/>
<text x="62" y="109.7" font-size="12" text-anchor="end" fill="currentColor">2</text>
<line x1="66" y1="48.6" x2="70" y2="48.6" stroke="currentColor"/>
<text x="62" y="52.6" font-size="12" text-anchor="end" fill="currentColor">3</text>
<line x1="70.0" y1="220" x2="70.0" y2="224" stroke="currentColor"/>
<text x="70.0" y="238" font-size="12" text-anchor="middle" fill="currentColor">0</text>
<line x1="158.0" y1="220" x2="158.0" y2="224" stroke="currentColor"/>
<text x="158.0" y="238" font-size="12" text-anchor="middle" fill="currentColor">50</text>
<line x1="246.0" y1="220" x2="246.0" y2="224" stroke="currentColor"/>
<text x="246.0" y="238" font-size="12" text-anchor="middle" fill="currentColor">100</text>
<line x1="334.0" y1="220" x2="334.0" y2="224" stroke="currentColor"/>
<text x="334.0" y="238" font-size="12" text-anchor="middle" fill="currentColor">150</text>
<line x1="422.0" y1="220" x2="422.0" y2="224" stroke="currentColor"/>
<text x="422.0" y="238" font-size="12" text-anchor="middle" fill="currentColor">200</text>
<line x1="510.0" y1="220" x2="510.0" y2="224" stroke="currentColor"/>
<text x="510.0" y="238" font-size="12" text-anchor="middle" fill="currentColor">250</text>
<line x1="70" y1="36.1" x2="510" y2="36.1" stroke="#9cc9ea" stroke-width="1.5" stroke-dasharray="6 4"/>
<text x="510" y="30.1" font-size="12" text-anchor="end" fill="currentColor">uniform guessing, ln 25 = 3.22</text>
<polyline points="70.0,38.5 158.0,113.3 246.0,158.5 334.0,186.2 422.0,199.5 510.0,204.4" fill="none" stroke="#eea66f" stroke-width="2.5"/>
<circle cx="70.0" cy="38.5" r="4" fill="#eea66f" stroke="currentColor"/>
<text x="76.0" y="30.5" font-size="11" fill="currentColor">3.18</text>
<circle cx="158.0" cy="113.3" r="4" fill="#eea66f" stroke="currentColor"/>
<text x="164.0" y="105.3" font-size="11" fill="currentColor">1.87</text>
<circle cx="246.0" cy="158.5" r="4" fill="#eea66f" stroke="currentColor"/>
<text x="252.0" y="150.5" font-size="11" fill="currentColor">1.08</text>
<circle cx="334.0" cy="186.2" r="4" fill="#eea66f" stroke="currentColor"/>
<text x="340.0" y="178.2" font-size="11" fill="currentColor">0.59</text>
<circle cx="422.0" cy="199.5" r="4" fill="#eea66f" stroke="currentColor"/>
<text x="428.0" y="191.5" font-size="11" fill="currentColor">0.36</text>
<circle cx="510.0" cy="204.4" r="4" fill="#eea66f" stroke="currentColor"/>
<text x="516.0" y="196.4" font-size="11" fill="currentColor">0.27</text>
<text x="290.0" y="258" font-size="12" text-anchor="middle" fill="currentColor">training step</text>
<text x="18" y="120.0" font-size="12" text-anchor="middle" fill="currentColor" transform="rotate(-90 18 120.0)">loss (nats per character)</text>
</svg>
<figcaption>Figure 19.3. Training loss of the tiny transformer, from the printed output (the loss of one batch of 16 windows at each marked step). It falls from the level of uniform guessing to about a quarter of a nat per character: on so short a text the model is mostly memorising.</figcaption>
</figure>

**Part 4** samples: feed a prompt, take the logits at the last position, divide them by a **temperature** $\tau$
(below 1 makes the distribution sharper, above 1 flatter), sample a character, append it, repeat. The samples
reproduce phrases of the training text and splice them at shared words ("the rover"), with occasional garbled fragments.
Be honest about what this shows: the text is 457 characters long and the model has 60,000 parameters, so it is
largely memorising, and with no held-out text we have not measured generalisation at all. What it does show is that
every piece works together: the same code, with more layers, more data and much more compute, is the recipe of the
GPT papers.

The program runs in a few seconds because everything is tiny. A real model differs in scale, not in kind: tens to
hundreds of layers, $d$ in the thousands, contexts of thousands of tokens, mixed-precision arithmetic, and libraries
such as PyTorch or JAX that generate the backward pass automatically and run it on GPUs.

## 19.6 Tokenization: byte-pair encoding from scratch

**The question:** what should the tokens be? Characters make sequences long (and attention costs $n^2$); whole words
make the vocabulary huge and leave no way to handle a word never seen in training.

**Subword** tokenization sits between them: frequent words are single tokens, rare words are split into pieces, and
any string can still be written using single characters as a last resort. **Byte-pair encoding** (BPE) began as a
data-compression method (Philip Gage, 1994): repeatedly replace the most frequent pair of adjacent bytes by a new
symbol. Sennrich, Haddow and Birch (2016) adapted it to build vocabularies for neural translation:

1. Split every word of the training corpus into characters, plus an end-of-word marker (we write `_`).
2. Count every pair of adjacent symbols, weighted by word frequency.
3. Merge the most frequent pair into one new symbol everywhere, and record the merge.
4. Repeat until the chosen number of merges (the vocabulary budget) is reached.

To tokenize new text, apply the recorded merges in the same order. Here is the paper's example dictionary, *low*
5 times, *lower* 2, *newest* 6, *widest* 3, run by the program:

```python
--8<-- "books/machine-learning/ch19_bpe.py"
```

```
1. Sennrich et al.'s example: low x5, lower x2, newest x6, widest x3
   merge  1: e + s (count  9)  ->  l o w _ x5  l o w e r _ x2  n e w es t _ x6  w i d es t _ x3
   merge  2: es + t (count  9)  ->  l o w _ x5  l o w e r _ x2  n e w est _ x6  w i d est _ x3
   merge  3: est + _ (count  9)  ->  l o w _ x5  l o w e r _ x2  n e w est_ x6  w i d est_ x3
   merge  4: l + o (count  7)  ->  lo w _ x5  lo w e r _ x2  n e w est_ x6  w i d est_ x3
   merge  5: lo + w (count  7)  ->  low _ x5  low e r _ x2  n e w est_ x6  w i d est_ x3
   merge  6: n + e (count  6)  ->  low _ x5  low e r _ x2  ne w est_ x6  w i d est_ x3
   merge  7: ne + w (count  6)  ->  low _ x5  low e r _ x2  new est_ x6  w i d est_ x3
   merge  8: new + est_ (count  6)  ->  low _ x5  low e r _ x2  newest_ x6  w i d est_ x3
   merge  9: low + _ (count  5)  ->  low_ x5  low e r _ x2  newest_ x6  w i d est_ x3
   merge 10: w + i (count  3)  ->  low_ x5  low e r _ x2  newest_ x6  wi d est_ x3

2. tokenizing words never seen in training:
   lowest  -> ['low', 'est_']
   newer   -> ['new', 'e', 'r', '_']
   wider   -> ['wi', 'd', 'e', 'r', '_']
   slow    -> ['s', 'low_']

3. a slightly bigger text: 47 words, 20 distinct; 25 merges learned
   first ten merges: e+_, r+o, ro+v, t+h, th+e_, e+r, rov+er, c+k, s+_, rover+_
   rovers   -> ['rovers_']
   driving  -> ['driv', 'i', 'n', 'g', '_']
   rocky    -> ['rock', 'y', '_']
   drivers  -> ['driv', 'er', 's_']
   unrocky  -> ['u', 'n', 'rock', 'y', '_']
   tokens for the whole text: 227 as characters, 84 after BPE
```

Trace the first merges by hand. The pair (e, s) occurs in *newest* (6 times) and *widest* (3), 9 in all; (s, t) and
(t, \_) also occur 9 times, and the tie goes to the pair seen first. After merging, `es` + `t` is the most frequent pair
(9), then `est` + `_` (9). Next (l, o) occurs in *low* and *lower*, $5 + 2 = 7$, and so on. Ten merges turn the four words
into units like `low_`, `est_` and `newest_`. A new word such as *lowest* becomes
`low` + `est_`: two meaningful pieces, although *lowest* was never seen. The end marker matters: `est_` (a word
ending) is a different token from `est` inside a word.

On the slightly larger text in part 3, 25 merges give whole-word tokens for frequent words (`rovers_`), meaningful
pieces for related words (`driv` + `er` + `s_`), and characters for the unknown prefix of *unrocky*. The 47 words take
227 character tokens but 84 BPE tokens. Fewer tokens per text means shorter sequences, a direct saving in
attention's $n^2$.

**Why it works.** Each merge creates the symbol that most reduces the token count of the training corpus at that
moment (a merge of a pair that occurs $c$ times removes exactly $c$ tokens), so BPE is a greedy compression
algorithm, in the sense of the Algorithms book's [greedy chapter](../algorithms/12-Greedy-Algorithms.md): locally best,
with no guarantee of the shortest overall encoding. A naive implementation recounts all pairs after every merge, as
ours does; production tokenizers update the counts incrementally with priority queues.

**Variants.** GPT-2 (Radford et al., 2019) runs BPE on *bytes* rather than characters, so any text in any script can
be encoded with no unknown tokens. BERT uses **WordPiece** (Schuster and Nakajima, 2012; Wu et al., 2016), which
chooses merges by likelihood rather than raw count. SentencePiece (Kudo and Richardson, 2018) treats the text as a raw
stream, spaces included, and offers BPE and a **unigram** language-model tokenizer (Kudo, 2018). Tokenization has
visible side effects: a model sees "unrocky" as pieces, not letters, which is one reason language models can be
oddly bad at spelling and at counting characters.

## 19.7 Pretraining: GPT, BERT, vision transformers

**The question:** labelled data is scarce, but unlabelled text is abundant. What task can a transformer learn from raw
text that makes it useful for everything else?

### Next-token prediction (GPT)

Radford, Narasimhan, Salimans and Sutskever's "Improving language understanding by generative pre-training" (2018),
the first **GPT** (generative pretrained transformer), trained a 12-block decoder-only transformer with causal masks
as a language model on the BooksCorpus (about 7,000 unpublished books), with exactly the loss of 18.1 and of our tiny
model:

$$
L(\theta) = -\sum_{t} \log p_\theta(x_t \mid x_{<t}).
$$

Then it **fine-tuned** the whole model, with a small task-specific output layer, on labelled data for each task
(entailment, question answering, classification), improving the state of the art on 9 of the 12 tasks studied, as the
paper reports. This is transfer learning ([Chapter 17](17-Convolutional-Networks.md)) for text: the pretraining task
needs no labels, and predicting the next word well requires knowing a lot about syntax, facts and context.

GPT-2 (Radford et al., 2019) scaled the recipe to 1.5 billion parameters and reported that the model could perform
some tasks with no fine-tuning, when the task was phrased as text to continue. GPT-3 (Brown et al., 2020), with 175
billion parameters, studied this systematically as **in-context learning**: a few examples of the task are put in the
prompt, and the model continues the pattern without any change to its weights. [Chapter 20](20-Generative-Models.md)
returns to language models as generative models, and [Chapter 23](23-Where-Machine-Learning-Goes.md) to scaling and
the debate about what in-context learning is.

### Masked language modelling (BERT)

A causal model sees only the left context. For understanding tasks the right context matters too ("the *bank* of
the river"). But a bidirectional model cannot be trained on next-token prediction: with no mask, each position could
see the token it is asked to predict. Devlin, Chang, Lee and Toutanova's **BERT** (2019) used a **masked language
model** instead: choose 15% of the token positions at random; of those, replace 80% by a special `[MASK]` token, 10%
by a random token and leave 10% unchanged; train the encoder to predict the original tokens at the chosen positions
from everything around them. (The 80/10/10 split keeps the model from learning that only `[MASK]` positions matter,
since `[MASK]` never appears when the model is used.) BERT also used a second objective, predicting whether two
sentences were consecutive; later work (RoBERTa, Liu et al., 2019) found it unnecessary. BERT-base has 12 blocks with
$d = 768$; BERT-large has 24 with $d = 1024$. Fine-tuned, it set new results on the GLUE benchmark and on SQuAD
question answering, as the paper reports, and encoder models of this kind are still widely used for classification
and search.

The two objectives make different trade-offs. Masked modelling learns from only the 15% of chosen positions per
sequence, but with context on both sides; next-token prediction learns from every position, and its model can
generate text directly. Encoder-decoder models such as T5 (Raffel et al., 2020) corrupt spans of the input and train
the decoder to produce them.

### Vision transformers

Dosovitskiy et al.'s "An image is worth 16x16 words" (2020) applied a standard transformer encoder to images with
almost no change. Cut a $224 \times 224$ image into a $14 \times 14$ grid of $16 \times 16$ patches; flatten each patch
($16 \cdot 16 \cdot 3 = 768$ numbers) and project it linearly to a $d$-vector; add learned position embeddings; prepend
a learned `[class]` token, whose output vector is used for classification. That is a sequence of $196 + 1 = 197$
tokens. The **ViT** has none of the CNN's built-in locality or translation equivariance
([Chapter 17](17-Convolutional-Networks.md)): the first layer can attend from any patch to any other. The paper reports
that, trained on ImageNet alone, ViTs did worse than ResNets of comparable size, but pretrained on much larger datasets
(ImageNet-21k and the 300-million-image JFT-300M) they matched or beat the best CNNs, at lower training cost. The
inductive bias of convolution is worth most when data is limited; with enough data the transformer learns similar
structure itself. Later work (for example DeiT, Touvron et al., 2021) trained ViTs well on ImageNet alone with strong
augmentation and distillation.

## 19.8 The cost of attention; efficient attention

*Level: advanced.*

**The question:** a transformer's attention compares every position with every other. What does that cost, and can
it be avoided?

### Counting

For one layer with sequence length $n$ and width $d$, count multiply-adds (each is 2 floating-point operations):

| part | multiply-adds |
|---|---|
| $Q, K, V$ and output projections | $4 n d^2$ |
| scores $QK^\top$ | $n^2 d$ |
| weighted values $AV$ | $n^2 d$ |
| MLP ($d \to 4d \to d$) | $8 n d^2$ |

So the total is $12 n d^2 + 2 n^2 d$. The attention-matrix part exceeds the rest when $2n^2 d > 12 n d^2$, that is
when $n > 6d$: for $d = 768$, beyond about 4,600 tokens. Below that, the matrix products of the projections and the
MLP dominate, and attention is not the main cost.

**Memory** is the sharper problem. The score matrix has $n^2$ entries per head, and a straightforward implementation
stores it (and the softmax output) for the backward pass. Part 7 of the program prints the size in 16-bit numbers for
one head: 2 MiB at $n = 1024$, 128 MiB at 8192 and 8 GiB at 65,536, multiplied by the number of heads and layers. And
on modern GPUs, moving data between the large slow memory and the small fast on-chip memory often takes longer than
the arithmetic, so writing and re-reading an $n \times n$ matrix costs time as well as space.

### Exact attention without the matrix: the online softmax

The softmax seems to need the whole row of scores before it can start: the normaliser $\sum_j e^{s_j}$ and, for
numerical safety, the maximum $\max_j s_j$. But both can be computed incrementally (Milakov and Gimelshein, 2018).
Process the keys in blocks and keep, for each query, three running quantities: the largest score so far $m$, the sum
$l = \sum_{j \text{ seen}} e^{s_j - m}$, and the unnormalised output $o = \sum_{j \text{ seen}} e^{s_j - m} v_j$. When
a new block arrives with scores $s_j$, let $m' = \max(m, \max_{\text{block}} s_j)$ and update

$$
l \leftarrow e^{m - m'}\, l + \sum_{\text{block}} e^{s_j - m'}, \qquad
o \leftarrow e^{m - m'}\, o + \sum_{\text{block}} e^{s_j - m'} v_j, \qquad m \leftarrow m'.
$$

At the end, the output is $o / l$.

**Claim.** After any number of blocks, $l = \sum_{j \text{ seen}} e^{s_j - m}$ and
$o = \sum_{j \text{ seen}} e^{s_j - m} v_j$ with $m$ the maximum over the keys seen; so the final $o/l$ is exactly
$\sum_j \operatorname{softmax}(s)_j v_j$.

*Proof* by induction over blocks. Initially nothing is seen, $l = 0$, $o = 0$ and $m = -\infty$ (with
$e^{-\infty} = 0$). Suppose the invariant holds before a block. Multiplying the old sum by $e^{m - m'}$ turns each
term $e^{s_j - m}$ into $e^{s_j - m'}$, re-basing it to the new maximum, and the block adds its own terms with the
same base, so the invariant holds after the block. At the end, $o / l = \sum_j e^{s_j - m} v_j / \sum_j e^{s_j - m}$,
and the common factor $e^{-m}$ cancels, leaving the softmax average. $\square$

Every exponent is at most 0, so nothing overflows. The program's `attention_tiled` implements this and matches the
ordinary computation to about $10^{-16}$ for block sizes from 1 to 256. **FlashAttention** (Dao, Fu, Ermon, Rudra and
Ré, 2022) is this idea engineered for GPUs: load blocks of $Q$, $K$ and $V$ into fast on-chip memory, compute the
scores and the online softmax there, write only the $n \times d$ output, and in the backward pass recompute the
scores block by block instead of storing them. The arithmetic is the same $O(n^2 d)$, and the result is exact, not an
approximation, but memory falls to $O(n)$ beyond the inputs and outputs and the number of slow memory accesses falls
sharply. The paper reports substantial wall-clock speedups and, because memory no longer grows with $n^2$, practical
training on much longer sequences.

### Approximate and structured attention

To beat $O(n^2)$ arithmetic, one must give up exact full attention. The main ideas, each with a published model:

- **Sparse patterns.** Let each position attend only to a local window plus a few strided or global positions:
  Sparse Transformers (Child et al., 2019), Longformer (Beltagy, Peters and Cohan, 2020), BigBird (Zaheer et al.,
  2020). Cost about $O(n \sqrt n)$ or $O(n w)$ for window $w$.
- **Hashing.** Reformer (Kitaev, Kaiser and Levskaya, 2020) groups similar queries and keys with locality-sensitive
  hashing and attends within groups.
- **Low rank and kernels.** Linformer (Wang et al., 2020) projects the keys and values to a fixed length.
  "Transformers are RNNs" (Katharopoulos et al., 2020) replaces $\exp(q \cdot k)$ by a product of feature maps
  $\phi(q) \cdot \phi(k)$, so $\sum_j \phi(q)\cdot\phi(k_j)\, v_j = \phi(q)^\top \big(\sum_j \phi(k_j) v_j^\top\big)$
  costs $O(n)$ and, with a causal mask, can even be run as a recurrence. Performer (Choromanski et al., 2021)
  approximates the softmax kernel with random features.
- **Cheaper decoding.** When generating, each new token's query attends to all previous keys and values, which are
  cached rather than recomputed (the **KV cache**, Exercise 8). Multi-query attention (Shazeer, 2019) and
  grouped-query attention (Ainslie et al., 2023) share keys and values between heads to shrink that cache.

None of the approximate methods has displaced exact attention for the largest language models, where FlashAttention-
style exact kernels plus the $n < 6d$ regime keep full attention affordable for contexts of thousands of tokens.
Whether some form of sub-quadratic sequence model can match transformers at scale is an open research question; one
active line revisits recurrence through **state-space models** (for example S4, Gu, Goel and Ré, 2022; Mamba, Gu and
Dao, 2023), which process sequences in linear time with recurrences designed to be trained in parallel.

## Check yourself

??? question "1. Recompute the third row of the hand example in 19.2 (query (1, 1)) and check it against the program."

    Scores: $(1,1) \cdot (1,0) = 1$, $(1,1) \cdot (0,1) = 1$, $(1,1) \cdot (1,1) = 2$; divided by $\sqrt 2$:
    $0.707, 0.707, 1.414$. Exponentials $2.028, 2.028, 4.113$, sum $8.169$, weights $0.248, 0.248, 0.503$. Output:
    $0.248 (1,0) + 0.248 (0,2) + 0.503 (3,3) = (0.248 + 1.510, 0.497 + 1.510) = (1.759, 2.007)$, the program's last
    row (to rounding).

??? question "2. If q and k have independent entries of mean 0 and variance sigma^2, what scale factor keeps the scores at variance 1?"

    $\operatorname{Var}(q \cdot k) = \sum_i E[q_i^2] E[k_i^2] = d_k \sigma^4$, so divide by $\sigma^2 \sqrt{d_k}$. With
    $\sigma = 1$ this is the paper's $\sqrt{d_k}$. In practice layer norm and the initialisation keep $\sigma$ near 1,
    which is why the fixed factor works.

??? question "3. Ignoring biases and layer norms, how many weights does one transformer block have? For d = 768 and 12 blocks?"

    Attention: $W_Q, W_K, W_V, W_O$, $4d^2$. MLP: $d \cdot 4d + 4d \cdot d = 8d^2$. Total $12 d^2$. For $d = 768$:
    $12 \cdot 768^2 = 7{,}077{,}888$ per block, about 85 million for 12 blocks. A vocabulary of 50,257 tokens adds an
    embedding matrix of $50{,}257 \cdot 768 \approx 38.6$ million, so the token embeddings are a large share of a
    model this size.

??? question "4. Show that, per layer, the n x n attention computations cost more than everything else exactly when n > 6d."

    From the table in 19.8: everything else is $4nd^2 + 8nd^2 = 12nd^2$ multiply-adds and the $QK^\top$ and $AV$
    products are $2n^2 d$. $2n^2 d > 12 n d^2 \iff n > 6d$ (dividing by $2nd > 0$). For $d = 4096$, that is
    $n > 24{,}576$.

??? question "5. Does the causal mask break the permutation equivariance of 19.3? What does that imply about positional encodings in decoders?"

    Yes. With the mask, position $i$ attends to positions $\le i$, so the output at $i$ depends on which tokens come
    earlier: reordering the input changes the sets, not just their order. A causal transformer therefore has some
    position information even without encodings (it can, for example, count how many tokens precede it through
    attention). Haviv et al. (2022) reported that causal language models without positional encodings can still be
    trained competitively. Encoders, which have no mask, cannot tell order at all without encodings.

??? question "6. Verify the rotation property for d = 2: write p_pos = (sin pos, cos pos) and find R_k."

    $p_{\mathrm{pos}+k} = (\sin(\mathrm{pos}+k), \cos(\mathrm{pos}+k)) = (\sin \mathrm{pos} \cos k + \cos \mathrm{pos} \sin k,\;
    \cos \mathrm{pos} \cos k - \sin \mathrm{pos} \sin k)$. As a matrix acting on the column
    $(\sin \mathrm{pos}, \cos \mathrm{pos})$, the rows are $(\cos k, \sin k)$ and $(-\sin k, \cos k)$: a rotation by
    angle $-k$ in the (sin, cos) plane, the same for every position.

??? question "7. Continue the BPE run of 19.6 by hand: what is the 11th merge for the low/lower/newest/widest dictionary?"

    After 10 merges the words are `low_` x5, `low e r _` x2, `newest_` x6, `wi d est_` x3. Pair counts: (low, e) 2,
    (e, r) 2, (r, \_) 2, (wi, d) 3, (d, est\_) 3. The most frequent are (wi, d) and (d, est\_) with 3, and (wi, d) is
    seen first, so merge 11 is `wi` + `d` → `wid`. (Merge 12 would then be `wid` + `est_`.) You can check by calling
    `learn_bpe(toy, 12)`.

??? question "8. Write the code: generation with a KV cache. Show that attending with cached keys and values, one new token at a time, gives the same outputs as full causal attention."

    ```python
    import numpy as np

    rng = np.random.default_rng(0)
    n, d = 7, 8
    X = rng.normal(size=(n, d))
    Wq, Wk, Wv = (rng.normal(size=(d, d)) / np.sqrt(d) for _ in range(3))

    def softmax(z):
        e = np.exp(z - z.max(-1, keepdims=True)); return e / e.sum(-1, keepdims=True)

    # full causal attention, all positions at once
    S = (X @ Wq) @ (X @ Wk).T / np.sqrt(d)
    S[np.triu_indices(n, 1)] = -np.inf
    full = softmax(S) @ (X @ Wv)

    # incremental: each step computes only the new token's q, k, v and appends k, v to the cache
    K_cache, V_cache, outs = [], [], []
    for t in range(n):
        q, k, v = X[t] @ Wq, X[t] @ Wk, X[t] @ Wv
        K_cache.append(k); V_cache.append(v)
        a = softmax(np.array(K_cache) @ q / np.sqrt(d))
        outs.append(a @ np.array(V_cache))
    print(np.allclose(full, np.array(outs)))   # True
    ```

    Each new step costs $O(t d)$ instead of recomputing all $t$ positions ($O(t d^2 + t^2 d)$), at the price of
    storing $2 t d$ numbers per layer and head group. In a multi-layer model the cache holds every layer's keys and
    values.

??? question "9. Write the code: BERT's masking. Given a token array, choose 15% of positions, and replace 80% of those by a MASK id, 10% by random tokens, 10% unchanged. Return the input and the targets (-1 where no loss)."

    ```python
    import numpy as np

    def bert_mask(tokens, vocab_size, mask_id, rng, p=0.15):
        tokens = np.asarray(tokens)
        chosen = rng.random(tokens.shape) < p
        targets = np.where(chosen, tokens, -1)          # loss only at chosen positions
        r = rng.random(tokens.shape)
        inp = tokens.copy()
        inp[chosen & (r < 0.8)] = mask_id
        rand = chosen & (r >= 0.8) & (r < 0.9)
        inp[rand] = rng.integers(0, vocab_size, rand.sum())
        return inp, targets                             # the last 10% stay unchanged

    rng = np.random.default_rng(1)
    toks = rng.integers(0, 1000, 100_000)
    inp, tgt = bert_mask(toks, 1000, mask_id=1000, rng=rng)
    chosen = tgt >= 0
    print(chosen.mean().round(3), (inp[chosen] == 1000).mean().round(3),
          (inp[chosen] == toks[chosen]).mean().round(3))   # about 0.15, 0.80, 0.10 (+ a few random hits)
    ```

    The last fraction is slightly above 0.10 because a random replacement occasionally draws the original token.

??? question "10. A ViT-Base splits a 224 x 224 image into 16 x 16 patches. How many tokens, how many numbers per patch, and how big is one head's attention matrix? What if the patches are 8 x 8?"

    $224/16 = 14$, so $14^2 = 196$ patches plus the class token: 197 tokens. Each patch has $16 \cdot 16 \cdot 3 = 768$
    numbers. The attention matrix is $197 \times 197 = 38{,}809$ entries per head. With $8 \times 8$ patches:
    $28^2 + 1 = 785$ tokens, an attention matrix about 16 times larger ($785^2 = 616{,}225$). Halving the patch side
    quadruples the tokens and multiplies attention cost by about 16, which is why ViTs use large patches.

??? question "11. In the online softmax, why must o and l be rescaled by e^(m - m') when the maximum increases, and why is that safe numerically?"

    The stored sums were computed relative to the old maximum $m$: their terms are $e^{s_j - m}$. New terms are
    computed relative to $m'$. Adding them without rescaling would mix two bases and give a wrong ratio. Multiplying by
    $e^{m - m'}$ converts every old term to $e^{s_j - m'}$ (proof in 19.8). Since $m' \ge m$, the factor is at most 1,
    and every exponent $s_j - m'$ is at most 0, so no term can overflow; terms that underflow to 0 are ones whose
    weight would be negligible anyway.

??? question "12. Why does a decoder-only transformer need the causal mask during training but a recurrent language model does not?"

    A recurrent model computes $h_t$ from $x_1, \dots, x_t$ only, by construction, so its prediction of $x_{t+1}$ cannot
    see the future. A transformer layer computes every position from every position; without the mask, the output at
    position $t$ would include $x_{t+1}$ through attention, and the model would learn to copy it, getting near-zero
    training loss and generating nonsense. The mask restores the "past only" structure while keeping all positions
    computed in parallel.

## What you learned

- The transformer replaced recurrence by self-attention: every position reaches every other in one step, and all
  positions are computed in parallel, at a cost that grows with $n^2$.
- Scaled dot-product attention is $\operatorname{softmax}(QK^\top/\sqrt{d_k})V$; the scale keeps score variance at 1
  (proved), avoiding a saturated softmax with vanishing gradients.
- Multi-head attention runs several smaller attentions in parallel for the same cost; attention alone is permutation
  equivariant (proved), so positions are added, as sinusoids (shifts are rotations, proved) or as learned vectors.
- A block is attention plus a position-wise MLP, each with a residual connection and layer norm (pre-norm in most
  modern models); the causal mask lets a decoder train on all positions at once.
- A complete transformer fits in a short NumPy program with a gradient check; training it is next-token prediction
  with cross-entropy.
- BPE builds a subword vocabulary by greedily merging the most frequent adjacent pairs.
- GPT pretrains by next-token prediction, BERT by masked tokens, ViT treats image patches as tokens; exact tiled
  attention (FlashAttention) removes the $n^2$ memory, and approximate methods trade exactness for sub-quadratic cost.

**Next:** [Chapter 20](20-Generative-Models.md), generative models: how to learn a whole probability distribution and
sample new data from it, with autoencoders, GANs, flows, diffusion and the language models of this chapter.

## Further reading

- A. Vaswani, N. Shazeer, N. Parmar, J. Uszkoreit, L. Jones, A. N. Gomez, Ł. Kaiser and I. Polosukhin, "Attention is
  all you need", NeurIPS 2017.
- D. Britz, A. Goldie, M.-T. Luong and Q. Le, "Massive exploration of neural machine translation architectures",
  EMNLP 2017.
- J. L. Ba, J. R. Kiros and G. E. Hinton, "Layer normalization", 2016; R. Xiong et al., "On layer normalization in the
  transformer architecture", ICML 2020.
- R. Sennrich, B. Haddow and A. Birch, "Neural machine translation of rare words with subword units", ACL 2016;
  P. Gage, "A new algorithm for data compression", *C Users Journal* 12(2), 1994; T. Kudo and J. Richardson,
  "SentencePiece", EMNLP 2018.
- A. Radford, K. Narasimhan, T. Salimans and I. Sutskever, "Improving language understanding by generative
  pre-training", 2018; A. Radford, J. Wu, R. Child, D. Luan, D. Amodei and I. Sutskever, "Language models are
  unsupervised multitask learners", 2019; T. Brown et al., "Language models are few-shot learners", NeurIPS 2020.
- J. Devlin, M.-W. Chang, K. Lee and K. Toutanova, "BERT: pre-training of deep bidirectional transformers for language
  understanding", NAACL 2019; C. Raffel et al., "Exploring the limits of transfer learning with a unified text-to-text
  transformer", *Journal of Machine Learning Research* 21, 2020.
- A. Dosovitskiy et al., "An image is worth 16x16 words: transformers for image recognition at scale", 2020 (ICLR 2021).
- T. Dao, D. Y. Fu, S. Ermon, A. Rudra and C. Ré, "FlashAttention: fast and memory-efficient exact attention with
  IO-awareness", NeurIPS 2022; M. Milakov and N. Gimelshein, "Online normalizer calculation for softmax", 2018.
- R. Child, S. Gray, A. Radford and I. Sutskever, "Generating long sequences with sparse transformers", 2019;
  A. Katharopoulos, A. Vyas, N. Pappas and F. Fleuret, "Transformers are RNNs", ICML 2020; Y. Tay, M. Dehghani,
  D. Bahri and D. Metzler, "Efficient transformers: a survey", *ACM Computing Surveys*, 2022.
- J. Su et al., "RoFormer: enhanced transformer with rotary position embedding", 2021; O. Press, N. A. Smith and
  M. Lewis, "Train short, test long: attention with linear biases enables input length extrapolation", 2021 (ICLR 2022).
- A. Gu and T. Dao, "Mamba: linear-time sequence modeling with selective state spaces", 2023.
- D. Jurafsky and J. H. Martin, *Speech and Language Processing*, 3rd ed. draft: the chapters on transformers and
  large language models; I. Goodfellow, Y. Bengio and A. Courville, *Deep Learning*, 2016, for the background.
- On this site: [Chapter 18](18-Sequence-Models.md) (attention's origin), [Chapter 17](17-Convolutional-Networks.md)
  (the CNNs that ViT competes with), [Chapter 20](20-Generative-Models.md), [Chapter 23](23-Where-Machine-Learning-Goes.md)
  (scaling laws and in-context learning), and the Algorithms book's [greedy chapter](../algorithms/12-Greedy-Algorithms.md)
  (BPE is a greedy algorithm).
