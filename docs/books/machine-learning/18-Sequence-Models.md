# 18. Sequence models

*Sentences, sensor readings, speech and music arrive one piece after another, and what a piece means depends on what
came before. A network for sequences must handle any length, use the same knowledge at every position, and carry a
memory forward. This chapter builds the tools in the order they were found: word vectors that turn symbols into
geometry, recurrent networks that read one step at a time, the gated cells (LSTM and GRU) that let them remember, the
encoder-decoder that turns one sequence into another, and attention, the idea that removed the memory bottleneck and
led straight to transformers. Everything is built from scratch in NumPy, trained, and checked.*

!!! abstract "In this chapter"
    **You will learn:**

    - how text, time series and audio become sequences of vectors, and the chain rule that turns sequence modelling into next-step prediction
    - word2vec's skip-gram with negative sampling, derived, trained on a tiny corpus, and why king $-$ man $+$ woman lands near queen
    - recurrent networks and backpropagation through time, derived and checked numerically
    - why gradients vanish or explode over long sequences, proved and measured
    - how the gates of the LSTM and the GRU fix that, and what the forget gate's bias does
    - sequence-to-sequence models, teacher forcing and beam search
    - attention (Bahdanau et al. 2014), built from scratch, and the alignment it learns by itself

    **You need:** [Chapter 15](15-Neural-Networks-and-Backpropagation.md) (backpropagation, computational graphs, the
    autodiff idea), [Chapter 16](16-Training-Deep-Networks.md) (initialisation, gradient clipping, Adam from
    [Chapter 5](05-Optimization.md)) and softmax with cross-entropy from [Chapter 6](06-Classification-and-Logistic-Regression.md).
    [Chapter 17](17-Convolutional-Networks.md) helps for the comparison with convolution.

    **Levels:** 18.1 and 18.2 are beginner to intermediate; 18.3 and 18.4 are intermediate; 18.5 is intermediate;
    18.6 is advanced.

## 18.1 Text, time series and audio as sequences

**The question:** what do a sentence, a week of temperatures and a recording of speech have in common, and why do
the models of earlier chapters handle them badly?

A **sequence** is an ordered list $x_1, x_2, \dots, x_T$ whose length $T$ can change from example to example. Each
$x_t$ is a vector. Three common kinds:

- **Text.** A sentence is split into **tokens**: words, pieces of words, or single characters
  ([Chapter 19](19-Transformers.md) builds a tokenizer). Each token is an integer index into a **vocabulary** of
  size $V$, and becomes a vector by one-hot encoding ([Chapter 2](02-Data-and-Features.md)) or, much better, by an
  **embedding** (18.2).
- **Time series.** Measurements at regular times: a rover's wheel currents, temperatures, prices. Each $x_t$ is
  the vector of readings at time $t$.
- **Audio.** Sound is air pressure sampled thousands of times a second (16,000 a second is common for speech), so a
  second of speech is a sequence of 16,000 numbers. Speech systems usually first cut it into short overlapping
  frames and describe each frame by its spectrum, giving about a hundred vectors a second.

What makes sequences special is that **order carries meaning** ("dog bites man" is not "man bites dog") and that
**length varies**. A fixed-size model such as logistic regression or an MLP needs a fixed-size input. We could pad or
cut every sequence to one length, or look only at a fixed window of the last $k$ steps (an **n-gram** model for
text, or a 1-D convolution as in [Chapter 17](17-Convolutional-Networks.md)). Windows work surprisingly well, but they
cannot use anything further back than $k$ steps, and "the keys that I left on the table in the kitchen *are*" needs
the subject from eight words back to choose "are" over "is".

### Typical tasks

| shape | example | input | output |
|---|---|---|---|
| many to one | sentiment of a review | a sequence | one label |
| many to many, aligned | tag each word as noun, verb ... | a sequence | one label per step |
| sequence to sequence | translation, speech to text | a sequence | another sequence, of a different length |
| generation | write text, forecast | a beginning | a continuation |

### Modelling a sequence is predicting the next step

How can we put a probability on a whole sentence? The chain rule of probability ([Chapter 3](03-The-Math-Toolkit.md))
says, with no assumption at all,

$$
p(x_1, x_2, \dots, x_T) = p(x_1)\, p(x_2 \mid x_1)\, p(x_3 \mid x_1, x_2) \cdots p(x_T \mid x_1, \dots, x_{T-1})
= \prod_{t=1}^{T} p(x_t \mid x_{<t}),
$$

where $x_{<t}$ means "all the steps before $t$". So a model that predicts the **next step** from the past, for every
past, defines a probability for every sequence. That is a **language model** when the steps are tokens. Its loss is
the sum of the cross-entropies of each next-step prediction. All the models in this chapter and the next are ways to
compute $p(x_t \mid x_{<t})$ from a past of any length with a fixed number of weights. An n-gram model cheats by
cutting the past to the last $n - 1$ tokens; a recurrent network (18.3) squeezes the whole past into a vector; a
transformer ([Chapter 19](19-Transformers.md)) looks back at all of it.

## 18.2 Word embeddings: word2vec

**The question:** a one-hot vector for "king" and one for "queen" are as different as "king" and "carrot": every
pair of one-hot vectors has dot product 0 and distance $\sqrt 2$. How can we give words vectors in which similar
words are near?

The answer is old. The linguist Zellig Harris argued in 1954 that words occurring in similar contexts tend to have
similar meanings, the **distributional hypothesis**, and J. R. Firth's 1957 phrase "you shall know a word by the
company it keeps" is its slogan. So: learn a vector for each word that predicts the words around it.

### Skip-gram

Tomas Mikolov and colleagues' **word2vec** (two papers, 2013) made this fast enough to run on billions of words. Its
**skip-gram** model gives each word $w$ two vectors in $\mathbb{R}^d$ ($d$ is typically 100 to 300): $v_w$ when it is
the centre word and $u_w$ when it is a context word. For a centre word $c$ and a word $o$ within a **window** of
$m$ positions around it, the model is a softmax over the vocabulary,

$$
p(o \mid c) = \frac{\exp(u_o \cdot v_c)}{\sum_{w=1}^{V} \exp(u_w \cdot v_c)} ,
$$

trained by maximum likelihood ([Chapter 3](03-The-Math-Toolkit.md)) on every (centre, context) pair in the corpus.
The dot product $u_o \cdot v_c$ is large when $o$ often appears near $c$. Two words with similar contexts are pushed
towards similar $v$ vectors, because the same $u$ vectors must score highly against both.

The trouble is the denominator: a sum over the whole vocabulary, often a million words, for every pair.

### Negative sampling, derived

**Negative sampling** (from the second 2013 paper) replaces the $V$-way softmax by a few yes/no questions. For a true
pair $(c, o)$ we want the logistic model ([Chapter 6](06-Classification-and-Logistic-Regression.md)) to say "yes,
these occur together", $\sigma(u_o \cdot v_c) \to 1$, where $\sigma(z) = 1/(1 + e^{-z})$. We also draw $k$ random
**negative** words $n_1, \dots, n_k$ (typically $k$ is 5 to 20) and want "no" for each, $\sigma(u_{n_j} \cdot v_c) \to 0$.
The loss for one pair is the logistic cross-entropy

$$
\ell = -\log \sigma(u_o \cdot v_c) - \sum_{j=1}^{k} \log \sigma(-u_{n_j} \cdot v_c),
$$

using $1 - \sigma(z) = \sigma(-z)$. The negatives are drawn from the word frequencies raised to the power $3/4$, which
the paper found to work better than the plain frequencies: it samples rare words a little more often.

The gradients follow from $\frac{d}{dz}\log\sigma(z) = 1 - \sigma(z)$ ([Chapter 6](06-Classification-and-Logistic-Regression.md)).
Write $s_o = \sigma(u_o \cdot v_c)$ and $s_j = \sigma(u_{n_j} \cdot v_c)$. Then

$$
\frac{\partial \ell}{\partial v_c} = (s_o - 1)\, u_o + \sum_{j} s_j\, u_{n_j}, \qquad
\frac{\partial \ell}{\partial u_o} = (s_o - 1)\, v_c, \qquad
\frac{\partial \ell}{\partial u_{n_j}} = s_j\, v_c .
$$

Read them as forces. When the true pair is not yet confident ($s_o$ well below 1), $v_c$ is pulled towards $u_o$ and
$u_o$ towards $v_c$. When a negative scores high ($s_j$ near 1), $v_c$ is pushed away from it. A step costs
$O(kd)$ instead of $O(Vd)$. Those are exactly the lines `g_pos`, `g_neg` and `grad_vc` of the program.

### A tiny corpus with hidden structure

To see the method work without downloading anything, the program writes its own corpus. There are eight
"person" words, each with three hidden properties: gender (king, prince, man, boy are "m"), age (king, queen, man,
woman are "old") and status (king, queen, prince, princess are "royal"). Each sentence is a person word, one cue
word for each of its properties (for example "she", "little", "palace"), and two filler words, in random order.
Person words never appear next to each other, so any similarity between "king" and "queen" must come from the cue
words they share.

```python
--8<-- "books/machine-learning/ch18_word2vec.py"
```

```
corpus: 3000 sentences, 18000 words, vocabulary 32
example: little crown a near she princess | and farm and girl little hers

1. skip-gram with negative sampling: 54000 pairs, d = 10, k = 5 negatives
   epoch 1: mean loss per pair 2.662
   epoch 2: mean loss per pair 2.583
   epoch 3: mean loss per pair 2.582
   epoch 4: mean loss per pair 2.584
   epoch 5: mean loss per pair 2.584

2. the learned vectors
   nearest to king   : man 0.50, queen 0.49, prince 0.47
   nearest to girl   : boy 0.56, woman 0.54, princess 0.51
   nearest to palace : crown 0.97, throne 0.95, and 0.55
   king - man + woman = queen (0.97), princess (0.55)
   prince - boy + girl = princess (0.93), village (0.40)
   queen - woman + girl = princess (0.96), and (0.46)

3. vectors from the PPMI matrix by SVD (no training loop)
   nearest to king   : a 0.62, queen 0.60, man 0.56
   nearest to girl   : woman 0.57, princess 0.56, and 0.55
   nearest to palace : crown 0.95, throne 0.93, near 0.52
   king - man + woman = queen (0.99), a (0.64)
   prince - boy + girl = princess (0.98), queen (0.58)
   queen - woman + girl = princess (0.97), prince (0.59)
```

After five passes, the cue words that always appear in the same contexts are almost identical (palace, crown and
throne have cosine similarity 0.97 and 0.95). The person words have formed the expected neighbourhoods: king's nearest
are man, queen and prince, each sharing two of its three properties.

### The analogy picture

The famous test is **analogy**: compute $v_{\text{king}} - v_{\text{man}} + v_{\text{woman}}$ and find the nearest
word, excluding the three words used. Our vectors give queen with cosine 0.97, and prince $-$ boy $+$ girl gives
princess with 0.93.

<figure class="mars-fig" markdown="0">
<svg viewBox="0 0 600 250" role="img" aria-label="Schematic of the analogy picture: man, woman, king and queen at the corners of a parallelogram. The arrow from man to woman is parallel to the arrow from king to queen, and the arrow from man to king is parallel to the arrow from woman to queen.">
<circle cx="130" cy="200" r="6" fill="#9cc9ea" stroke="currentColor"/>
<text x="118" y="205" font-size="14" text-anchor="end" fill="currentColor">man</text>
<circle cx="130" cy="80" r="6" fill="#9cc9ea" stroke="currentColor"/>
<text x="118" y="85" font-size="14" text-anchor="end" fill="currentColor">woman</text>
<circle cx="420" cy="215" r="6" fill="#eea66f" stroke="currentColor"/>
<text x="432" y="220" font-size="14" text-anchor="start" fill="currentColor">king</text>
<circle cx="420" cy="95" r="6" fill="#eea66f" stroke="currentColor"/>
<text x="432" y="100" font-size="14" text-anchor="start" fill="currentColor">queen</text>
<line x1="130.0" y1="194.0" x2="130.0" y2="96.0" stroke="#7ccf9a" stroke-width="2"/><polygon points="130.0,88.0 134.0,96.0 126.0,96.0" fill="#7ccf9a"/>
<line x1="420.0" y1="209.0" x2="420.0" y2="111.0" stroke="#7ccf9a" stroke-width="2"/><polygon points="420.0,103.0 424.0,111.0 416.0,111.0" fill="#7ccf9a"/>
<line x1="136.0" y1="201.0" x2="404.0" y2="213.6" stroke="currentColor" stroke-width="1.2"/><polygon points="412.0,214.0 403.8,217.6 404.2,209.6" fill="currentColor"/>
<line x1="136.0" y1="81.0" x2="404.0" y2="93.6" stroke="currentColor" stroke-width="1.2"/><polygon points="412.0,94.0 403.8,97.6 404.2,89.6" fill="currentColor"/>
<text x="140" y="145" font-size="13" fill="currentColor">gender direction</text>
<text x="430" y="160" font-size="13" fill="currentColor">same direction</text>
<text x="275" y="232" font-size="13" text-anchor="middle" fill="currentColor">royalty direction</text>
<text x="275" y="70" font-size="13" text-anchor="middle" fill="currentColor">royalty direction</text>
</svg>
<figcaption>Figure 18.2. The analogy picture (a schematic, not a plot of real vectors). If gender and royalty each correspond to a direction, then king minus man plus woman lands near queen. Part 2 of the program finds exactly this in vectors learned from a tiny corpus.</figcaption>
</figure>

Why should subtraction work? If the vector of a word is (roughly) a sum of vectors for its properties,
$v_{\text{king}} \approx g_m + a_{\text{old}} + r_{\text{royal}}$, $v_{\text{man}} \approx g_m + a_{\text{old}} +
r_{\text{common}}$, and so on, then

$$
v_{\text{king}} - v_{\text{man}} + v_{\text{woman}} \approx (g_m + a_{\text{old}} + r_{\text{royal}}) - (g_m +
a_{\text{old}} + r_{\text{common}}) + (g_f + a_{\text{old}} + r_{\text{common}}) = g_f + a_{\text{old}} +
r_{\text{royal}} \approx v_{\text{queen}} .
$$

Our corpus was built so that the additive story is true, which is why the program's analogies are so clean.
Mikolov, Yih and Zweig (2013) found the same parallelogram structure in vectors trained on real news text, which
surprised many people; on real data the method is noisier, and a caution is in order: the standard test excludes the
three query words from the answers, and without that exclusion the nearest word to king $-$ man $+$ woman is often
"king" itself. Embeddings also faithfully learn the statistics of their corpus, including stereotyped associations,
which Bolukbasi et al. (2016) measured and tried to remove with exactly these vector directions.

### What word2vec is secretly computing

Levy and Goldberg (2014) showed that skip-gram with negative sampling is close to factorising a matrix of counts. The
**pointwise mutual information** of a word $w$ and a context $c$ is

$$
\operatorname{PMI}(w, c) = \log \frac{p(w, c)}{p(w)\, p(c)} = \log \frac{\#(w, c) \cdot N}{\#(w)\, \#(c)} ,
$$

where $\#$ counts pairs and $N$ is the number of pairs: how much more often the two occur together than they would by
chance. For example, if "king" is in 20 of 200 pairs, "crown" in 25, and the pair (king, crown) in 10, then
$\operatorname{PMI} = \log(10 \cdot 200 / (20 \cdot 25)) = \log 4 \approx 1.39$.

**Claim.** If every dot product $x = u_c \cdot v_w$ could be chosen freely, the expected negative-sampling loss
is minimised at $x = \operatorname{PMI}(w, c) - \log k$ (with negatives drawn from the plain context frequencies).

*Proof.* Over the corpus, the pair $(w, c)$ appears as a positive $\#(w,c)$ times, and as a negative about
$k\, \#(w)\, \#(c) / N$ times (each of the $\#(w)$ occurrences of $w$ draws $k$ negatives, each equal to $c$ with
probability $\#(c)/N$). The part of the total loss that depends on $x$ is

$$
f(x) = -\#(w,c) \log \sigma(x) - \frac{k\, \#(w)\, \#(c)}{N} \log \sigma(-x).
$$

Its derivative is $f'(x) = -\#(w,c)(1 - \sigma(x)) + \frac{k\, \#(w)\, \#(c)}{N}\sigma(x)$. Setting it to zero and using
$\sigma(x)/(1 - \sigma(x)) = e^x$ gives $e^x = \#(w,c) N / (k\, \#(w)\, \#(c))$, so
$x = \operatorname{PMI}(w,c) - \log k$. Since $f'' > 0$, this is the minimum. $\square$

So, when $d$ is large enough to fit them, the learned dot products are a shifted PMI matrix; with small $d$, SGD finds
a low-rank approximation of it. Part 3 of the program skips the training loop altogether: it builds the
**positive PMI** matrix (PMI with negative values set to 0, a common and more stable variant), takes its SVD
([Chapter 3](03-The-Math-Toolkit.md), [Chapter 14](14-Dimensionality-Reduction.md)) and keeps the top 10 directions.
The analogies come out just as well (queen 0.99, princess 0.98). Pennington, Socher and Manning's **GloVe** (2014)
is a third route to the same kind of vectors: a weighted least-squares fit of dot products to log co-occurrence
counts.

Word vectors have one vector per word, whatever its context ("bank" of a river and "bank" with money share one).
Contextual embeddings, in which a word's vector depends on its sentence, came next: first from recurrent language
models, then from transformers ([Chapter 19](19-Transformers.md)).

## 18.3 Recurrent networks; backprop through time

**The question:** how can a fixed set of weights read a sequence of any length and remember what it has read?

A **recurrent neural network** (RNN) keeps a **hidden state** $h_t \in \mathbb{R}^d$, a vector meant to summarise
the past, and updates it at each step with the same weights:

$$
h_t = \tanh(W h_{t-1} + U x_t + b), \qquad h_0 = 0, \qquad \hat y_t = V h_t + c .
$$

$W$ ($d \times d$) carries the state forward, $U$ ($d \times n$) reads the input, and $V$ makes an output (for
example the logits of the next token, fed to a softmax). This simple form is often called an **Elman network**,
after Jeffrey Elman's "Finding structure in time" (1990), which trained one to predict the next letter and the next
word and found that its hidden states grouped words by grammatical role. Michael Jordan's 1986 network was similar,
feeding back outputs instead of states.

The weight sharing is the same idea as in convolution ([Chapter 17](17-Convolutional-Networks.md)), now along time:
the same $W$, $U$, $b$ at every step, so the number of weights does not depend on $T$. The difference is that a
convolution sees a fixed window, while the state $h_t$ depends, in principle, on every input since the start.

### A trace by hand

Take one hidden unit, $w = 0.5$, $u = 1$, $b = 0$, and inputs $1, 0, -1$:

| $t$ | $x_t$ | $w h_{t-1} + u x_t$ | $h_t$ |
|---|---|---|---|
| 1 | 1 | $0.5 \cdot 0 + 1 = 1$ | $\tanh 1 = 0.7616$ |
| 2 | 0 | $0.5 \cdot 0.7616 = 0.3808$ | $0.3634$ |
| 3 | $-1$ | $0.5 \cdot 0.3634 - 1 = -0.8183$ | $-0.6741$ |

The first input is still present at $t = 2$, halved and squashed, and much fainter at $t = 3$. Part 1 of the program
prints the same table. This fading is the subject of the rest of the section.

<figure class="mars-fig" markdown="0">
<svg viewBox="0 0 600 260" role="img" aria-label="An RNN unrolled over four time steps. Inputs x1 to x4 feed states h1 to h4 through U; each state feeds the next through W, starting from h0; each state produces an output y through V. The same three weight matrices are used at every step.">
<text x="10" y="45" font-size="13" fill="currentColor">outputs</text>
<text x="10" y="125" font-size="13" fill="currentColor">states</text>
<text x="10" y="205" font-size="13" fill="currentColor">inputs</text>
<rect x="20" y="102" width="40" height="36" rx="6" fill="none" stroke="currentColor" stroke-dasharray="4 3"/>
<text x="40" y="125" font-size="13" text-anchor="middle" fill="currentColor">h0</text>
<rect x="85" y="102" width="50" height="36" rx="6" fill="#9cc9ea" fill-opacity="0.6" stroke="currentColor"/>
<text x="110" y="125" font-size="14" text-anchor="middle" fill="currentColor">h1</text>
<rect x="90" y="185" width="40" height="30" rx="6" fill="#7ccf9a" fill-opacity="0.6" stroke="currentColor"/>
<text x="110" y="205" font-size="14" text-anchor="middle" fill="currentColor">x1</text>
<rect x="90" y="25" width="40" height="30" rx="6" fill="#eea66f" fill-opacity="0.6" stroke="currentColor"/>
<text x="110" y="45" font-size="14" text-anchor="middle" fill="currentColor">y1</text>
<line x1="110.0" y1="185.0" x2="110.0" y2="148.0" stroke="currentColor" stroke-width="1.4"/><polygon points="110.0,140.0 114.0,148.0 106.0,148.0" fill="currentColor"/>
<line x1="110.0" y1="102.0" x2="110.0" y2="65.0" stroke="currentColor" stroke-width="1.4"/><polygon points="110.0,57.0 114.0,65.0 106.0,65.0" fill="currentColor"/>
<text x="116" y="168" font-size="12" fill="currentColor">U</text>
<text x="116" y="84" font-size="12" fill="currentColor">V</text>
<line x1="60.0" y1="120.0" x2="75.0" y2="120.0" stroke="currentColor" stroke-width="1.4"/><polygon points="83.0,120.0 75.0,124.0 75.0,116.0" fill="currentColor"/>
<text x="71.5" y="112" font-size="12" text-anchor="middle" fill="currentColor">W</text>
<rect x="215" y="102" width="50" height="36" rx="6" fill="#9cc9ea" fill-opacity="0.6" stroke="currentColor"/>
<text x="240" y="125" font-size="14" text-anchor="middle" fill="currentColor">h2</text>
<rect x="220" y="185" width="40" height="30" rx="6" fill="#7ccf9a" fill-opacity="0.6" stroke="currentColor"/>
<text x="240" y="205" font-size="14" text-anchor="middle" fill="currentColor">x2</text>
<rect x="220" y="25" width="40" height="30" rx="6" fill="#eea66f" fill-opacity="0.6" stroke="currentColor"/>
<text x="240" y="45" font-size="14" text-anchor="middle" fill="currentColor">y2</text>
<line x1="240.0" y1="185.0" x2="240.0" y2="148.0" stroke="currentColor" stroke-width="1.4"/><polygon points="240.0,140.0 244.0,148.0 236.0,148.0" fill="currentColor"/>
<line x1="240.0" y1="102.0" x2="240.0" y2="65.0" stroke="currentColor" stroke-width="1.4"/><polygon points="240.0,57.0 244.0,65.0 236.0,65.0" fill="currentColor"/>
<text x="246" y="168" font-size="12" fill="currentColor">U</text>
<text x="246" y="84" font-size="12" fill="currentColor">V</text>
<line x1="135.0" y1="120.0" x2="205.0" y2="120.0" stroke="currentColor" stroke-width="1.4"/><polygon points="213.0,120.0 205.0,124.0 205.0,116.0" fill="currentColor"/>
<text x="174.0" y="112" font-size="12" text-anchor="middle" fill="currentColor">W</text>
<rect x="345" y="102" width="50" height="36" rx="6" fill="#9cc9ea" fill-opacity="0.6" stroke="currentColor"/>
<text x="370" y="125" font-size="14" text-anchor="middle" fill="currentColor">h3</text>
<rect x="350" y="185" width="40" height="30" rx="6" fill="#7ccf9a" fill-opacity="0.6" stroke="currentColor"/>
<text x="370" y="205" font-size="14" text-anchor="middle" fill="currentColor">x3</text>
<rect x="350" y="25" width="40" height="30" rx="6" fill="#eea66f" fill-opacity="0.6" stroke="currentColor"/>
<text x="370" y="45" font-size="14" text-anchor="middle" fill="currentColor">y3</text>
<line x1="370.0" y1="185.0" x2="370.0" y2="148.0" stroke="currentColor" stroke-width="1.4"/><polygon points="370.0,140.0 374.0,148.0 366.0,148.0" fill="currentColor"/>
<line x1="370.0" y1="102.0" x2="370.0" y2="65.0" stroke="currentColor" stroke-width="1.4"/><polygon points="370.0,57.0 374.0,65.0 366.0,65.0" fill="currentColor"/>
<text x="376" y="168" font-size="12" fill="currentColor">U</text>
<text x="376" y="84" font-size="12" fill="currentColor">V</text>
<line x1="265.0" y1="120.0" x2="335.0" y2="120.0" stroke="currentColor" stroke-width="1.4"/><polygon points="343.0,120.0 335.0,124.0 335.0,116.0" fill="currentColor"/>
<text x="304.0" y="112" font-size="12" text-anchor="middle" fill="currentColor">W</text>
<rect x="475" y="102" width="50" height="36" rx="6" fill="#9cc9ea" fill-opacity="0.6" stroke="currentColor"/>
<text x="500" y="125" font-size="14" text-anchor="middle" fill="currentColor">h4</text>
<rect x="480" y="185" width="40" height="30" rx="6" fill="#7ccf9a" fill-opacity="0.6" stroke="currentColor"/>
<text x="500" y="205" font-size="14" text-anchor="middle" fill="currentColor">x4</text>
<rect x="480" y="25" width="40" height="30" rx="6" fill="#eea66f" fill-opacity="0.6" stroke="currentColor"/>
<text x="500" y="45" font-size="14" text-anchor="middle" fill="currentColor">y4</text>
<line x1="500.0" y1="185.0" x2="500.0" y2="148.0" stroke="currentColor" stroke-width="1.4"/><polygon points="500.0,140.0 504.0,148.0 496.0,148.0" fill="currentColor"/>
<line x1="500.0" y1="102.0" x2="500.0" y2="65.0" stroke="currentColor" stroke-width="1.4"/><polygon points="500.0,57.0 504.0,65.0 496.0,65.0" fill="currentColor"/>
<text x="506" y="168" font-size="12" fill="currentColor">U</text>
<text x="506" y="84" font-size="12" fill="currentColor">V</text>
<line x1="395.0" y1="120.0" x2="465.0" y2="120.0" stroke="currentColor" stroke-width="1.4"/><polygon points="473.0,120.0 465.0,124.0 465.0,116.0" fill="currentColor"/>
<text x="434.0" y="112" font-size="12" text-anchor="middle" fill="currentColor">W</text>
<text x="300" y="245" font-size="13" text-anchor="middle" fill="currentColor">the same W, U, V at every step</text>
</svg>
<figcaption>Figure 18.1. A recurrent network unrolled in time. Unrolled, it is an ordinary deep network whose layers share their weights, so backpropagation applies, run backwards through time.</figcaption>
</figure>

### Backpropagation through time, derived

Unroll the network over $T$ steps as in Figure 18.1. It becomes an ordinary feed-forward network with $T$ layers that
share their weights, so backpropagation ([Chapter 15](15-Neural-Networks-and-Backpropagation.md)) applies. Running it
backwards through the unrolled graph is called **backpropagation through time** (BPTT); the name and a clear account
are in Werbos (1990).

Let the loss be a sum over steps, $L = \sum_t \ell_t(h_t)$, and write $a_t = W h_{t-1} + U x_t + b$ for the
pre-activation, so $h_t = \tanh(a_t)$. Define $\delta_t = \partial L / \partial h_t$, the *total* derivative,
counting every path from $h_t$ to the loss. The state $h_t$ affects the loss in two ways: directly through
$\ell_t$, and through $h_{t+1}$. By the chain rule,

$$
\delta_t = \frac{\partial \ell_t}{\partial h_t} + W^\top \big( \delta_{t+1} \odot (1 - h_{t+1}^2) \big),
\qquad \delta_{T+1} = 0,
$$

where $\odot$ multiplies entry by entry and $1 - h^2$ is the derivative of $\tanh$. Compute it for
$t = T, T-1, \dots, 1$. With $g_t = \delta_t \odot (1 - h_t^2) = \partial L / \partial a_t$, each weight's gradient is
the sum over time of what each step contributes, exactly as weight sharing in a CNN summed over positions:

$$
\frac{\partial L}{\partial W} = \sum_{t=1}^{T} g_t\, h_{t-1}^\top, \qquad
\frac{\partial L}{\partial U} = \sum_{t=1}^{T} g_t\, x_t^\top, \qquad
\frac{\partial L}{\partial b} = \sum_{t=1}^{T} g_t .
$$

The function `rnn_bptt` in the program is these four lines. The forward pass must store every $h_t$, so BPTT costs
$O(T)$ time and $O(T)$ memory. For very long sequences one uses **truncated BPTT**: run forward continuously, but
backpropagate only $k$ steps at a time, which bounds the cost and also bounds how far back the network can learn.

```python
--8<-- "books/machine-learning/ch18_rnn.py"
```

```
1. scalar RNN h_t = tanh(w h_(t-1) + u x_t), w = 0.5, u = 1, h_0 = 0
   t=1: x=+1  w*h+u*x = +1.0000  h_1 = +0.7616
   t=2: x=+0  w*h+u*x = +0.3808  h_2 = +0.3634
   t=3: x=-1  w*h+u*x = -0.8183  h_3 = -0.6741

2. BPTT gradient check, loss = sum_t r_t . h_t over 6 steps
   dW: max |BPTT - numeric| = 6.1e-10
   dU: max |BPTT - numeric| = 6.0e-10
   db: max |BPTT - numeric| = 4.0e-10

3. size of dh_t/dh_0 (spectral norm) for a 16-unit RNN, U scaled to spectral radius rho
                         t=1        t=5        t=10       t=20       t=40       
   linear rho=0.5         8.22e-01   5.43e-02   1.50e-03   1.46e-06   1.39e-12   
   linear rho=1.0         1.64e+00   1.74e+00   1.54e+00   1.53e+00   1.53e+00   
   linear rho=1.5         2.47e+00   1.32e+01   8.85e+01   5.08e+03   1.69e+07   
   tanh   rho=0.5         6.91e-01   2.33e-02   2.75e-04   1.62e-08   1.07e-16   
   tanh   rho=1.0         1.38e+00   7.05e-01   1.50e-01   5.37e-03   2.31e-05   
   tanh   rho=1.5         2.08e+00   4.72e+00   3.61e+00   8.80e-01   2.98e+00   

4. at initialisation: size of the gradient of the loss with respect to the FIRST input
   (median over 9 random initialisations)
      T   vanilla RNN       LSTM        GRU
      5       4.8e-02    3.4e-02    6.5e-03
     20       1.6e-03    6.3e-02    3.7e-03
     80       2.0e-07    1.4e-01    5.8e-04

5. trained 250 steps (Adam, batch 32), T = 60: test accuracy (4 classes, chance 0.25)
   VanillaRNN  0.223
   GRU         1.000
```

Part 2 of the output checks BPTT against finite differences: they agree to $10^{-10}$, so the recursion is right.
The program also contains a small reverse-mode autodiff class `T` working on whole arrays, the array version of the
engine from [Chapter 15](15-Neural-Networks-and-Backpropagation.md). Every operation records how to pass a gradient
back to its inputs; `backward()` visits the graph in reverse order. We use it for the gated cells of 18.4 so that the
code shows the forward equations only.

### Why gradients vanish or explode

How does a change in $h_0$ (or in an early input) affect $h_T$? By the chain rule, the Jacobian (the matrix of partial
derivatives) is a product of one factor per step:

$$
\frac{\partial h_T}{\partial h_0} = \prod_{t=T}^{1} \frac{\partial h_t}{\partial h_{t-1}}
= \prod_{t=T}^{1} D_t W, \qquad D_t = \operatorname{diag}(1 - h_t^2).
$$

**Claim.** If the spectral norm of $W$ (its largest stretching factor) is $\|W\| < 1$, then
$\|\partial h_T / \partial h_0\| \le \|W\|^T$, which goes to 0 exponentially fast.

*Proof.* The norm of a product is at most the product of the norms, and $\|D_t\| = \max_i |1 - h_{t,i}^2| \le 1$
because $\tanh$ takes values in $(-1, 1)$. So $\|\partial h_T/\partial h_0\| \le \prod_t \|D_t\| \|W\| \le \|W\|^T$.
$\square$

So the gradient signal from step $T$ that reaches step 0 is multiplied by something like $\|W\|^T$. Over 50 steps with
$\|W\| = 0.9$ that is $0.9^{50} \approx 0.005$. The network gets almost no signal telling it to use early
inputs: the **vanishing gradient problem**. In the other direction, for a linear RNN ($D_t = I$) whose $W$ has an
eigenvalue $\lambda$ with $|\lambda| > 1$, the product grows like $|\lambda|^T$ along that eigenvector: **exploding
gradients**, which make training jump wildly. Sepp Hochreiter analysed vanishing gradients in his 1991 diploma
thesis, and Bengio, Simard and Frasconi (1994) showed that the problem is fundamental: a recurrent network that stores
information robustly, so that small noise cannot erase it, must have contracting dynamics, and then its gradients
vanish. Pascanu, Mikolov and Bengio (2013) gave the modern analysis and the standard fix for explosions, **gradient
clipping**: if the gradient's norm exceeds a threshold, scale it down to the threshold ([Chapter 16](16-Training-Deep-Networks.md)).

Part 3 of the output measures the Jacobian's norm for a 16-unit RNN whose $W$ is scaled to **spectral radius**
$\rho$ (the largest $|\lambda|$). The linear RNN behaves exactly as the theory says: with $\rho = 0.5$ the norm falls
to about $10^{-12}$ after 40 steps, with $\rho = 1.5$ it grows to about $10^{7}$, and with $\rho = 1$ it stays near 1.5.
With $\tanh$, the factors $D_t$ shrink everything further: even $\rho = 1$ vanishes (to $2 \times 10^{-5}$ after 40
steps), and $\rho = 1.5$ does not explode, because the large states saturate the $\tanh$, where its slope is small.
Clipping handles explosions; vanishing needs a change of architecture.

Part 4 measures what matters for learning: the gradient of the loss with respect to the *first* input, at
initialisation, on a task where the answer depends only on the first input. For the vanilla RNN it falls from
$5 \times 10^{-2}$ at $T = 5$ to $2 \times 10^{-7}$ at $T = 80$. Part 5 trains on the task at $T = 60$. The task: the
first symbol is one of four classes, the next 59 symbols are random noise, and the network must report the first
symbol at the end. The vanilla RNN stays at chance (0.223, chance is 0.25). The GRU of the next section reaches 1.000.

## 18.4 LSTM and GRU: gates explained

**The question:** the product $\prod_t D_t W$ shrinks because every step multiplies the state by a matrix and squashes
it. Can we give the network a path along which information is *copied* from step to step, not transformed?

### The LSTM

Hochreiter and Schmidhuber's **long short-term memory** (1997) adds a second state, the **cell** $c_t$, updated
mostly by addition. The version used today includes the **forget gate** that Gers, Schmidhuber and Cummins added in
2000. Each step computes three **gates**, vectors of numbers between 0 and 1 made by a sigmoid, and a candidate:

$$
\begin{aligned}
i_t &= \sigma(W_i h_{t-1} + U_i x_t + b_i) && \text{input gate: how much to write} \\
f_t &= \sigma(W_f h_{t-1} + U_f x_t + b_f) && \text{forget gate: how much to keep} \\
o_t &= \sigma(W_o h_{t-1} + U_o x_t + b_o) && \text{output gate: how much to show} \\
n_t &= \tanh(W_n h_{t-1} + U_n x_t + b_n) && \text{candidate: what to write} \\
c_t &= f_t \odot c_{t-1} + i_t \odot n_t, \qquad h_t = o_t \odot \tanh(c_t).
\end{aligned}
$$

A **gate** is a soft switch. Multiplying by a number near 1 lets a signal through, near 0 blocks it, and because the
gate is a sigmoid of the inputs, the network learns *when* to open and close it. Figure 18.3 shows the flow.

<figure class="mars-fig" markdown="0">
<svg viewBox="0 0 600 260" role="img" aria-label="An LSTM cell. The cell state runs left to right along the top: it is multiplied by the forget gate f, then the product of the input gate i and the candidate n is added, giving the new cell state. The new cell state passes through tanh and is multiplied by the output gate o to give the hidden state h.">
<rect x="60" y="30" width="480" height="200" rx="12" fill="none" stroke="currentColor" stroke-opacity="0.6"/>
<text x="8" y="60" font-size="13" fill="currentColor">c(t-1)</text>
<line x1="20.0" y1="70.0" x2="144.0" y2="70.0" stroke="currentColor" stroke-width="2"/><polygon points="152.0,70.0 144.0,74.0 144.0,66.0" fill="currentColor"/>
<circle cx="170" cy="70" r="16" fill="#eea66f" fill-opacity="0.8" stroke="currentColor"/>
<text x="170" y="75" font-size="15" text-anchor="middle" fill="currentColor">&#215;</text>
<circle cx="300" cy="70" r="16" fill="#eea66f" fill-opacity="0.8" stroke="currentColor"/>
<text x="300" y="75" font-size="15" text-anchor="middle" fill="currentColor">+</text>
<line x1="186.0" y1="70.0" x2="274.0" y2="70.0" stroke="currentColor" stroke-width="2"/><polygon points="282.0,70.0 274.0,74.0 274.0,66.0" fill="currentColor"/>
<line x1="316.0" y1="70.0" x2="572.0" y2="70.0" stroke="currentColor" stroke-width="2"/><polygon points="580.0,70.0 572.0,74.0 572.0,66.0" fill="currentColor"/>
<text x="565" y="60" font-size="13" text-anchor="middle" fill="currentColor">c(t)</text>
<rect x="148" y="170" width="44" height="30" rx="5" fill="#7ccf9a" fill-opacity="0.7" stroke="currentColor"/>
<text x="170" y="190" font-size="14" text-anchor="middle" fill="currentColor">f</text>
<text x="170" y="218" font-size="11" text-anchor="middle" fill="currentColor">forget</text>
<rect x="248" y="170" width="44" height="30" rx="5" fill="#7ccf9a" fill-opacity="0.7" stroke="currentColor"/>
<text x="270" y="190" font-size="14" text-anchor="middle" fill="currentColor">i</text>
<text x="270" y="218" font-size="11" text-anchor="middle" fill="currentColor">input</text>
<rect x="308" y="170" width="44" height="30" rx="5" fill="#9cc9ea" fill-opacity="0.7" stroke="currentColor"/>
<text x="330" y="190" font-size="14" text-anchor="middle" fill="currentColor">n</text>
<text x="330" y="218" font-size="11" text-anchor="middle" fill="currentColor">candidate</text>
<rect x="464" y="170" width="44" height="30" rx="5" fill="#7ccf9a" fill-opacity="0.7" stroke="currentColor"/>
<text x="486" y="190" font-size="14" text-anchor="middle" fill="currentColor">o</text>
<text x="486" y="218" font-size="11" text-anchor="middle" fill="currentColor">output</text>
<line x1="170.0" y1="170.0" x2="170.0" y2="96.0" stroke="currentColor" stroke-width="1.4"/><polygon points="170.0,88.0 174.0,96.0 166.0,96.0" fill="currentColor"/>
<circle cx="300" cy="130" r="16" fill="#eea66f" fill-opacity="0.8" stroke="currentColor"/>
<text x="300" y="135" font-size="15" text-anchor="middle" fill="currentColor">&#215;</text>
<line x1="270.0" y1="170.0" x2="285.1" y2="150.3" stroke="currentColor" stroke-width="1.4"/><polygon points="290.0,144.0 288.3,152.8 282.0,147.9" fill="currentColor"/>
<line x1="330.0" y1="170.0" x2="314.9" y2="150.3" stroke="currentColor" stroke-width="1.4"/><polygon points="310.0,144.0 318.0,147.9 311.7,152.8" fill="currentColor"/>
<line x1="300.0" y1="114.0" x2="300.0" y2="96.0" stroke="currentColor" stroke-width="1.4"/><polygon points="300.0,88.0 304.0,96.0 296.0,96.0" fill="currentColor"/>
<circle cx="430" cy="70" r="3" fill="currentColor"/>
<line x1="430.0" y1="72.0" x2="430.0" y2="95.0" stroke="currentColor" stroke-width="1.4"/><polygon points="430.0,103.0 426.0,95.0 434.0,95.0" fill="currentColor"/>
<circle cx="430" cy="120" r="16" fill="#9cc9ea" fill-opacity="0.8" stroke="currentColor"/>
<text x="430" y="125" font-size="15" text-anchor="middle" fill="currentColor"></text>
<text x="430" y="124" font-size="10" text-anchor="middle" fill="currentColor">tanh</text>
<circle cx="490" cy="120" r="16" fill="#eea66f" fill-opacity="0.8" stroke="currentColor"/>
<text x="490" y="125" font-size="15" text-anchor="middle" fill="currentColor">&#215;</text>
<line x1="446.0" y1="120.0" x2="465.0" y2="120.0" stroke="currentColor" stroke-width="1.4"/><polygon points="473.0,120.0 465.0,124.0 465.0,116.0" fill="currentColor"/>
<line x1="486.0" y1="170.0" x2="488.3" y2="145.0" stroke="currentColor" stroke-width="1.4"/><polygon points="489.0,137.0 492.3,145.3 484.3,144.6" fill="currentColor"/>
<line x1="506.0" y1="120.0" x2="572.0" y2="120.0" stroke="currentColor" stroke-width="2"/><polygon points="580.0,120.0 572.0,124.0 572.0,116.0" fill="currentColor"/>
<text x="565" y="142" font-size="13" text-anchor="middle" fill="currentColor">h(t)</text>
<text x="300" y="250" font-size="13" text-anchor="middle" fill="currentColor">every gate reads x(t) and h(t-1)</text>
</svg>
<figcaption>Figure 18.3. Inside an LSTM cell. The top line is the cell state: one multiplication (forget) and one addition (write) per step, so information and gradient can flow along it for many steps. The three gates are sigmoids between 0 and 1 that decide how much to forget, to write and to show.</figcaption>
</figure>

**Why it helps.** Follow the cell along the top line. Ignoring the (smaller) paths through the gates,
$\partial c_t / \partial c_{t-1} = \operatorname{diag}(f_t)$: no weight matrix, no squashing. Over many steps,

$$
\frac{\partial c_T}{\partial c_k} \approx \prod_{t=k+1}^{T} \operatorname{diag}(f_t),
$$

and when the forget gates are near 1, this product stays near 1: information written at step $k$ survives to step
$T$, and gradient flows back just as easily. Hochreiter and Schmidhuber called the cell's self-loop the **constant
error carousel**. (Their original cell had no forget gate, effectively $f = 1$; Gers et al. added it so the cell could
also be cleared.) The network now *chooses* its memory: it can keep the first symbol of our task in some cell units
by setting $i \approx 0$ for later inputs and $f \approx 1$.

**The forget gate's bias matters.** If $b_f = 0$, the forget gates start near $\sigma(0) = 0.5$ and the product over
40 steps is $0.5^{40} \approx 10^{-12}$: the cell starts out forgetting as fast as a vanilla RNN. With $b_f = 1$,
$\sigma(1) = 0.731$ and $0.731^{40} = 3.6 \times 10^{-6}$; with $b_f = 3$, $\sigma(3) = 0.953$ and
$0.953^{40} = 0.14$. Gers et al. (2000) already recommended a positive forget bias, and Jozefowicz, Zaremba and
Sutskever (2015) found that a bias of 1 removed much of the LSTM's disadvantage in their large comparison of
architectures; Tallec and Ollivier (2018) derived initialisations matched to the time scale the task needs. Our
program uses $b_f = 3$ because its task needs a memory of 60 steps. Part 4 shows the effect: the LSTM's gradient to
the first input does not vanish as $T$ grows (it even grows somewhat, since the cell keeps an almost unchanged copy
of early inputs and the gates add more paths).

### The GRU

Cho and colleagues' **gated recurrent unit** (2014) is a simpler cell with one state and two gates:

$$
\begin{aligned}
z_t &= \sigma(W_z h_{t-1} + U_z x_t + b_z) && \text{update gate} \\
r_t &= \sigma(W_r h_{t-1} + U_r x_t + b_r) && \text{reset gate} \\
n_t &= \tanh(W_n (r_t \odot h_{t-1}) + U_n x_t + b_n) && \text{candidate} \\
h_t &= (1 - z_t) \odot n_t + z_t \odot h_{t-1}. &&
\end{aligned}
$$

The new state is a weighted average, unit by unit, of the old state and a candidate. Where $z_t \approx 1$ the unit
copies its old value, and $\partial h_t / \partial h_{t-1}$ contains the term $\operatorname{diag}(z_t)$, the same
uncrushed path as the LSTM's forget gate. The reset gate lets the candidate ignore the old state, to start afresh.
(Conventions differ: some papers and libraries swap the roles of $z$ and $1 - z$.) Our program's GRU starts with
$b_z = 3$, keeping its old state by default, and Part 5 shows it learning the 60-step memory task perfectly in 250
steps. With the same budget, the LSTM solved the task in three of the five random seeds we tried and was still partly
stuck in the other two, so the printed run shows only the vanilla RNN and the GRU; the LSTM's working gradient is the
evidence in Part 4.

### Counting the cost

With hidden size $d$ and input size $n$, a vanilla RNN has $d(d + n) + d$ weights, a GRU three times that and an LSTM
four times. For $d = 16$, $n = 8$: 400, 1,200 and 1,600. Which is better depends on the task. Chung et al. (2014)
and Jozefowicz et al. (2015) found the GRU and the LSTM close on most tasks they tried; Greff et al. (2017) compared
eight LSTM variants and found that the forget gate and the output activation were the most important parts.

### The limits of recurrence

Gating cures vanishing gradients, not every problem. The state $h_t$ is still a single vector of fixed size that must
hold everything the future might need, and the computation is **sequential**: step $t$ cannot start until step
$t - 1$ has finished, so a GPU cannot process the positions of a sequence in parallel during training. The first
limit is attacked in 18.6, the second in [Chapter 19](19-Transformers.md).

## 18.5 Sequence to sequence

**The question:** in translation the output has its own length and its own word order. How can a network map a
sequence to a different sequence?

Sutskever, Vinyals and Le's "Sequence to sequence learning with neural networks" (2014) and Cho et al.'s RNN
encoder-decoder (2014) gave the same answer. An **encoder** RNN reads the source $x_1, \dots, x_{T_x}$ and its final
state $h_{T_x}$ becomes a summary vector. A **decoder** RNN, started from that summary, generates the target one
token at a time, each step conditioned on the tokens it has produced so far:

$$
p(y_1, \dots, y_{T_y} \mid x) = \prod_{t=1}^{T_y} p(y_t \mid y_{<t}, x), \qquad
s_t = \operatorname{RNN}(s_{t-1}, \operatorname{embed}(y_{t-1})), \qquad s_0 = h_{T_x} .
$$

The decoder's first input is a special start token, and it stops when it emits an end token. Sutskever et al. used
four-layer LSTMs and reported a BLEU score of 34.8 on the WMT'14 English-to-French test set with an ensemble (BLEU
measures overlap of word sequences with human translations; higher is better). They also found that **reversing the
source sentence** improved results noticeably: it puts the first source words close to the first target words, so
many dependencies become short.

### Teacher forcing

During training, what should the decoder see as its previous token $y_{t-1}$: its own guess, or the truth? Usually
the truth, called **teacher forcing**: every step then gets a clean input, the $T_y$ losses are independent given the
true prefix, and the gradients are well behaved. The catch, called **exposure bias**, is that at test time the
decoder sees its own outputs, including its mistakes, which it never saw in training. Scheduled sampling (Bengio et
al., 2015) mixes in the model's own predictions during training to reduce the gap.

### Decoding: greedy and beam search

At test time we want the most probable output, $\arg\max_y p(y \mid x)$. Trying every output is impossible ($V^{T_y}$
sequences). **Greedy decoding** takes the most probable token at each step, which can be wrong overall: a slightly
less likely first word may lead to a much more likely sentence. **Beam search** keeps the $B$ best partial outputs
(by total log-probability) at each step, extends each by every token, and keeps the best $B$ of those. With $B = 1$ it
is greedy; with larger $B$ it explores more, at $B$ times the cost. It is still a heuristic: it is not guaranteed to
find the most probable sequence. (Exercise 8 writes one.)

### The bottleneck, shown

The program `ch18_attention.py`, at the end of 18.6, trains a small seq2seq model with tanh RNNs on a toy task:
read 12 random symbols (from 8), output them reversed. Without attention, after 300 Adam steps it gets 49.4% of the
symbols right and only 0.8% of whole sequences. The task is trivial for a human, but the decoder must recover twelve
symbols from one 32-number vector, and the last symbol it must produce is the first one the encoder read, now eleven
steps of squashing in the past. Sutskever et al.'s sentence reversal and Cho et al.'s observation that their model's
quality dropped on long sentences point at the same **bottleneck**: one fixed vector for the whole source.

## 18.6 Attention from scratch

*Level: advanced.*

**The question:** instead of asking the decoder to remember the whole source in one vector, could it *look back* at
the source, choosing at each step where to look?

Bahdanau, Cho and Bengio's "Neural machine translation by jointly learning to align and translate" (2014) did
exactly that. Keep *all* the encoder states $h_1, \dots, h_{T_x}$ (in their paper, from a bidirectional RNN that reads
the source in both directions, so each $h_i$ describes the neighbourhood of word $i$). At each decoder step $t$:

1. **Score** every source position against the decoder's current state $s_{t-1}$ with a small network,
   the **additive** or **Bahdanau** score
   $e_{t,i} = v^\top \tanh(W_a s_{t-1} + U_a h_i)$.
2. **Normalise** the scores with a softmax over source positions: the **attention weights**
   $\alpha_{t,i} = \exp(e_{t,i}) / \sum_j \exp(e_{t,j})$, positive and summing to 1.
3. **Read** the **context vector**, the weighted average $c_t = \sum_i \alpha_{t,i} h_i$.
4. Feed $c_t$ into the decoder's update and its output layer, along with $s_{t-1}$ and the previous token.

The weights $\alpha_{t,\cdot}$ say where the decoder is looking at step $t$. They are not supervised: nobody tells
the model which source word goes with which target word. They are an ordinary differentiable part of the network, so
backpropagation trains $W_a$, $U_a$ and $v$ along with everything else, and the alignment emerges because it lowers
the loss. The cost is $O(T_x)$ scores per decoder step, $O(T_x T_y)$ in all.

### The backward pass through attention

Two new pieces need derivatives. The weighted average $c = \sum_i \alpha_i h_i$ gives
$\partial L / \partial \alpha_i = g \cdot h_i$ and $\partial L / \partial h_i \mathrel{+}= \alpha_i\, g$, where
$g = \partial L / \partial c$. The softmax $\alpha = \operatorname{softmax}(e)$ has Jacobian

$$
\frac{\partial \alpha_i}{\partial e_j} = \alpha_i (\mathbb{1}[i = j] - \alpha_j),
$$

since $\partial \alpha_i / \partial e_i = \alpha_i - \alpha_i^2$ by the quotient rule, and for $j \ne i$ only the
denominator depends on $e_j$, giving $-\alpha_i \alpha_j$. So, with $\gamma_i = \partial L/\partial \alpha_i$,

$$
\frac{\partial L}{\partial e_j} = \sum_i \gamma_i\, \alpha_i (\mathbb{1}[i=j] - \alpha_j) = \alpha_j \Big(\gamma_j - \sum_i \gamma_i \alpha_i\Big),
$$

which is the line `y * (g - (g * y).sum(...))` in the autodiff's `softmax`. Everything else (tanh, matrix products,
sums) we already know. The gradient reaches every encoder state directly, through $\alpha_{t,i}$ and $c_t$, in one
step: the path from an output to the input it depends on is short, no matter how far apart they are in time. That is
the real reason attention works so well for long sequences.

### The program

```python
--8<-- "books/machine-learning/ch18_attention.py"
```

```
without attention: reverse sequences of 12 symbols
   step  100: loss 1.289
   step  200: loss 0.901
   step  300: loss 0.698
   test: symbols right 0.494, whole sequences right 0.008

with attention: reverse sequences of 12 symbols
   step  100: loss 0.984
   step  200: loss 0.975
   step  300: loss 0.008
   test: symbols right 0.999, whole sequences right 0.990

attention weights for the first test sequence [1 6 5 2 0 5 2 6 2 5 1 4]
(row = output step, column = input position; each row sums to 1)
   out 0 (4): 0.01 0.04 0.01 0.01 0.00 0.01 0.00 0.00 0.00 0.05 0.01 0.85
   out 1 (1): 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.99 0.00
   out 2 (5): 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 1.00 0.00 0.00
   out 3 (2): 0.01 0.00 0.00 0.00 0.00 0.00 0.00 0.02 0.96 0.00 0.00 0.00
   out 4 (6): 0.01 0.00 0.00 0.00 0.00 0.00 0.00 0.99 0.00 0.00 0.00 0.00
   out 5 (2): 0.00 0.00 0.00 0.00 0.00 0.00 0.99 0.00 0.00 0.00 0.00 0.00
   out 6 (5): 0.00 0.00 0.00 0.00 0.01 0.98 0.00 0.00 0.00 0.00 0.00 0.00
   out 7 (0): 0.01 0.01 0.00 0.02 0.95 0.00 0.00 0.00 0.00 0.00 0.00 0.00
   out 8 (2): 0.00 0.00 0.00 0.98 0.00 0.00 0.01 0.00 0.00 0.00 0.00 0.00
   out 9 (5): 0.00 0.01 0.94 0.03 0.00 0.00 0.01 0.00 0.00 0.00 0.01 0.00
   out 10 (6): 0.03 0.94 0.00 0.00 0.00 0.01 0.00 0.00 0.00 0.00 0.00 0.00
   out 11 (1): 0.73 0.05 0.01 0.00 0.03 0.00 0.00 0.01 0.08 0.02 0.02 0.04
```

With attention, the same small model reaches 99.9% of symbols and 99.0% of whole sequences after the same 300 steps.
The loss curve is worth a look: it sits near 0.98 for 200 steps and then falls to 0.008. Until the attention weights
find the alignment, the context vectors are blurry averages that help little; once they lock on, the task becomes
easy. Figure 18.4 draws the printed weights for the first test sequence.

<figure class="mars-fig" markdown="0">
<svg viewBox="0 0 520 290" role="img" aria-label="Heat map of the attention weights the trained model uses while reversing a sequence of 12 symbols: twelve output rows by twelve input columns. The bright cells run along the anti-diagonal, from the last input position for the first output to the first input position for the last output.">
<text x="290" y="14" font-size="13" text-anchor="middle" fill="currentColor">input position (symbol)</text>
<text x="180.0" y="34" font-size="11" text-anchor="middle" fill="currentColor">1</text>
<text x="200.0" y="34" font-size="11" text-anchor="middle" fill="currentColor">6</text>
<text x="220.0" y="34" font-size="11" text-anchor="middle" fill="currentColor">5</text>
<text x="240.0" y="34" font-size="11" text-anchor="middle" fill="currentColor">2</text>
<text x="260.0" y="34" font-size="11" text-anchor="middle" fill="currentColor">0</text>
<text x="280.0" y="34" font-size="11" text-anchor="middle" fill="currentColor">5</text>
<text x="300.0" y="34" font-size="11" text-anchor="middle" fill="currentColor">2</text>
<text x="320.0" y="34" font-size="11" text-anchor="middle" fill="currentColor">6</text>
<text x="340.0" y="34" font-size="11" text-anchor="middle" fill="currentColor">2</text>
<text x="360.0" y="34" font-size="11" text-anchor="middle" fill="currentColor">5</text>
<text x="380.0" y="34" font-size="11" text-anchor="middle" fill="currentColor">1</text>
<text x="400.0" y="34" font-size="11" text-anchor="middle" fill="currentColor">4</text>
<text x="162" y="54" font-size="11" text-anchor="end" fill="currentColor">output 0 (4)</text>
<rect x="170" y="40" width="20" height="20" fill="#eea66f" fill-opacity="0.01" stroke="currentColor" stroke-opacity="0.25" stroke-width="0.6"/>
<rect x="190" y="40" width="20" height="20" fill="#eea66f" fill-opacity="0.04" stroke="currentColor" stroke-opacity="0.25" stroke-width="0.6"/>
<rect x="210" y="40" width="20" height="20" fill="#eea66f" fill-opacity="0.01" stroke="currentColor" stroke-opacity="0.25" stroke-width="0.6"/>
<rect x="230" y="40" width="20" height="20" fill="#eea66f" fill-opacity="0.01" stroke="currentColor" stroke-opacity="0.25" stroke-width="0.6"/>
<rect x="250" y="40" width="20" height="20" fill="#eea66f" fill-opacity="0.00" stroke="currentColor" stroke-opacity="0.25" stroke-width="0.6"/>
<rect x="270" y="40" width="20" height="20" fill="#eea66f" fill-opacity="0.01" stroke="currentColor" stroke-opacity="0.25" stroke-width="0.6"/>
<rect x="290" y="40" width="20" height="20" fill="#eea66f" fill-opacity="0.00" stroke="currentColor" stroke-opacity="0.25" stroke-width="0.6"/>
<rect x="310" y="40" width="20" height="20" fill="#eea66f" fill-opacity="0.00" stroke="currentColor" stroke-opacity="0.25" stroke-width="0.6"/>
<rect x="330" y="40" width="20" height="20" fill="#eea66f" fill-opacity="0.00" stroke="currentColor" stroke-opacity="0.25" stroke-width="0.6"/>
<rect x="350" y="40" width="20" height="20" fill="#eea66f" fill-opacity="0.05" stroke="currentColor" stroke-opacity="0.25" stroke-width="0.6"/>
<rect x="370" y="40" width="20" height="20" fill="#eea66f" fill-opacity="0.01" stroke="currentColor" stroke-opacity="0.25" stroke-width="0.6"/>
<rect x="390" y="40" width="20" height="20" fill="#eea66f" fill-opacity="0.85" stroke="currentColor" stroke-opacity="0.25" stroke-width="0.6"/>
<text x="162" y="74" font-size="11" text-anchor="end" fill="currentColor">output 1 (1)</text>
<rect x="170" y="60" width="20" height="20" fill="#eea66f" fill-opacity="0.00" stroke="currentColor" stroke-opacity="0.25" stroke-width="0.6"/>
<rect x="190" y="60" width="20" height="20" fill="#eea66f" fill-opacity="0.00" stroke="currentColor" stroke-opacity="0.25" stroke-width="0.6"/>
<rect x="210" y="60" width="20" height="20" fill="#eea66f" fill-opacity="0.00" stroke="currentColor" stroke-opacity="0.25" stroke-width="0.6"/>
<rect x="230" y="60" width="20" height="20" fill="#eea66f" fill-opacity="0.00" stroke="currentColor" stroke-opacity="0.25" stroke-width="0.6"/>
<rect x="250" y="60" width="20" height="20" fill="#eea66f" fill-opacity="0.00" stroke="currentColor" stroke-opacity="0.25" stroke-width="0.6"/>
<rect x="270" y="60" width="20" height="20" fill="#eea66f" fill-opacity="0.00" stroke="currentColor" stroke-opacity="0.25" stroke-width="0.6"/>
<rect x="290" y="60" width="20" height="20" fill="#eea66f" fill-opacity="0.00" stroke="currentColor" stroke-opacity="0.25" stroke-width="0.6"/>
<rect x="310" y="60" width="20" height="20" fill="#eea66f" fill-opacity="0.00" stroke="currentColor" stroke-opacity="0.25" stroke-width="0.6"/>
<rect x="330" y="60" width="20" height="20" fill="#eea66f" fill-opacity="0.00" stroke="currentColor" stroke-opacity="0.25" stroke-width="0.6"/>
<rect x="350" y="60" width="20" height="20" fill="#eea66f" fill-opacity="0.00" stroke="currentColor" stroke-opacity="0.25" stroke-width="0.6"/>
<rect x="370" y="60" width="20" height="20" fill="#eea66f" fill-opacity="0.99" stroke="currentColor" stroke-opacity="0.25" stroke-width="0.6"/>
<rect x="390" y="60" width="20" height="20" fill="#eea66f" fill-opacity="0.00" stroke="currentColor" stroke-opacity="0.25" stroke-width="0.6"/>
<text x="162" y="94" font-size="11" text-anchor="end" fill="currentColor">output 2 (5)</text>
<rect x="170" y="80" width="20" height="20" fill="#eea66f" fill-opacity="0.00" stroke="currentColor" stroke-opacity="0.25" stroke-width="0.6"/>
<rect x="190" y="80" width="20" height="20" fill="#eea66f" fill-opacity="0.00" stroke="currentColor" stroke-opacity="0.25" stroke-width="0.6"/>
<rect x="210" y="80" width="20" height="20" fill="#eea66f" fill-opacity="0.00" stroke="currentColor" stroke-opacity="0.25" stroke-width="0.6"/>
<rect x="230" y="80" width="20" height="20" fill="#eea66f" fill-opacity="0.00" stroke="currentColor" stroke-opacity="0.25" stroke-width="0.6"/>
<rect x="250" y="80" width="20" height="20" fill="#eea66f" fill-opacity="0.00" stroke="currentColor" stroke-opacity="0.25" stroke-width="0.6"/>
<rect x="270" y="80" width="20" height="20" fill="#eea66f" fill-opacity="0.00" stroke="currentColor" stroke-opacity="0.25" stroke-width="0.6"/>
<rect x="290" y="80" width="20" height="20" fill="#eea66f" fill-opacity="0.00" stroke="currentColor" stroke-opacity="0.25" stroke-width="0.6"/>
<rect x="310" y="80" width="20" height="20" fill="#eea66f" fill-opacity="0.00" stroke="currentColor" stroke-opacity="0.25" stroke-width="0.6"/>
<rect x="330" y="80" width="20" height="20" fill="#eea66f" fill-opacity="0.00" stroke="currentColor" stroke-opacity="0.25" stroke-width="0.6"/>
<rect x="350" y="80" width="20" height="20" fill="#eea66f" fill-opacity="1.00" stroke="currentColor" stroke-opacity="0.25" stroke-width="0.6"/>
<rect x="370" y="80" width="20" height="20" fill="#eea66f" fill-opacity="0.00" stroke="currentColor" stroke-opacity="0.25" stroke-width="0.6"/>
<rect x="390" y="80" width="20" height="20" fill="#eea66f" fill-opacity="0.00" stroke="currentColor" stroke-opacity="0.25" stroke-width="0.6"/>
<text x="162" y="114" font-size="11" text-anchor="end" fill="currentColor">output 3 (2)</text>
<rect x="170" y="100" width="20" height="20" fill="#eea66f" fill-opacity="0.01" stroke="currentColor" stroke-opacity="0.25" stroke-width="0.6"/>
<rect x="190" y="100" width="20" height="20" fill="#eea66f" fill-opacity="0.00" stroke="currentColor" stroke-opacity="0.25" stroke-width="0.6"/>
<rect x="210" y="100" width="20" height="20" fill="#eea66f" fill-opacity="0.00" stroke="currentColor" stroke-opacity="0.25" stroke-width="0.6"/>
<rect x="230" y="100" width="20" height="20" fill="#eea66f" fill-opacity="0.00" stroke="currentColor" stroke-opacity="0.25" stroke-width="0.6"/>
<rect x="250" y="100" width="20" height="20" fill="#eea66f" fill-opacity="0.00" stroke="currentColor" stroke-opacity="0.25" stroke-width="0.6"/>
<rect x="270" y="100" width="20" height="20" fill="#eea66f" fill-opacity="0.00" stroke="currentColor" stroke-opacity="0.25" stroke-width="0.6"/>
<rect x="290" y="100" width="20" height="20" fill="#eea66f" fill-opacity="0.00" stroke="currentColor" stroke-opacity="0.25" stroke-width="0.6"/>
<rect x="310" y="100" width="20" height="20" fill="#eea66f" fill-opacity="0.02" stroke="currentColor" stroke-opacity="0.25" stroke-width="0.6"/>
<rect x="330" y="100" width="20" height="20" fill="#eea66f" fill-opacity="0.96" stroke="currentColor" stroke-opacity="0.25" stroke-width="0.6"/>
<rect x="350" y="100" width="20" height="20" fill="#eea66f" fill-opacity="0.00" stroke="currentColor" stroke-opacity="0.25" stroke-width="0.6"/>
<rect x="370" y="100" width="20" height="20" fill="#eea66f" fill-opacity="0.00" stroke="currentColor" stroke-opacity="0.25" stroke-width="0.6"/>
<rect x="390" y="100" width="20" height="20" fill="#eea66f" fill-opacity="0.00" stroke="currentColor" stroke-opacity="0.25" stroke-width="0.6"/>
<text x="162" y="134" font-size="11" text-anchor="end" fill="currentColor">output 4 (6)</text>
<rect x="170" y="120" width="20" height="20" fill="#eea66f" fill-opacity="0.01" stroke="currentColor" stroke-opacity="0.25" stroke-width="0.6"/>
<rect x="190" y="120" width="20" height="20" fill="#eea66f" fill-opacity="0.00" stroke="currentColor" stroke-opacity="0.25" stroke-width="0.6"/>
<rect x="210" y="120" width="20" height="20" fill="#eea66f" fill-opacity="0.00" stroke="currentColor" stroke-opacity="0.25" stroke-width="0.6"/>
<rect x="230" y="120" width="20" height="20" fill="#eea66f" fill-opacity="0.00" stroke="currentColor" stroke-opacity="0.25" stroke-width="0.6"/>
<rect x="250" y="120" width="20" height="20" fill="#eea66f" fill-opacity="0.00" stroke="currentColor" stroke-opacity="0.25" stroke-width="0.6"/>
<rect x="270" y="120" width="20" height="20" fill="#eea66f" fill-opacity="0.00" stroke="currentColor" stroke-opacity="0.25" stroke-width="0.6"/>
<rect x="290" y="120" width="20" height="20" fill="#eea66f" fill-opacity="0.00" stroke="currentColor" stroke-opacity="0.25" stroke-width="0.6"/>
<rect x="310" y="120" width="20" height="20" fill="#eea66f" fill-opacity="0.99" stroke="currentColor" stroke-opacity="0.25" stroke-width="0.6"/>
<rect x="330" y="120" width="20" height="20" fill="#eea66f" fill-opacity="0.00" stroke="currentColor" stroke-opacity="0.25" stroke-width="0.6"/>
<rect x="350" y="120" width="20" height="20" fill="#eea66f" fill-opacity="0.00" stroke="currentColor" stroke-opacity="0.25" stroke-width="0.6"/>
<rect x="370" y="120" width="20" height="20" fill="#eea66f" fill-opacity="0.00" stroke="currentColor" stroke-opacity="0.25" stroke-width="0.6"/>
<rect x="390" y="120" width="20" height="20" fill="#eea66f" fill-opacity="0.00" stroke="currentColor" stroke-opacity="0.25" stroke-width="0.6"/>
<text x="162" y="154" font-size="11" text-anchor="end" fill="currentColor">output 5 (2)</text>
<rect x="170" y="140" width="20" height="20" fill="#eea66f" fill-opacity="0.00" stroke="currentColor" stroke-opacity="0.25" stroke-width="0.6"/>
<rect x="190" y="140" width="20" height="20" fill="#eea66f" fill-opacity="0.00" stroke="currentColor" stroke-opacity="0.25" stroke-width="0.6"/>
<rect x="210" y="140" width="20" height="20" fill="#eea66f" fill-opacity="0.00" stroke="currentColor" stroke-opacity="0.25" stroke-width="0.6"/>
<rect x="230" y="140" width="20" height="20" fill="#eea66f" fill-opacity="0.00" stroke="currentColor" stroke-opacity="0.25" stroke-width="0.6"/>
<rect x="250" y="140" width="20" height="20" fill="#eea66f" fill-opacity="0.00" stroke="currentColor" stroke-opacity="0.25" stroke-width="0.6"/>
<rect x="270" y="140" width="20" height="20" fill="#eea66f" fill-opacity="0.00" stroke="currentColor" stroke-opacity="0.25" stroke-width="0.6"/>
<rect x="290" y="140" width="20" height="20" fill="#eea66f" fill-opacity="0.99" stroke="currentColor" stroke-opacity="0.25" stroke-width="0.6"/>
<rect x="310" y="140" width="20" height="20" fill="#eea66f" fill-opacity="0.00" stroke="currentColor" stroke-opacity="0.25" stroke-width="0.6"/>
<rect x="330" y="140" width="20" height="20" fill="#eea66f" fill-opacity="0.00" stroke="currentColor" stroke-opacity="0.25" stroke-width="0.6"/>
<rect x="350" y="140" width="20" height="20" fill="#eea66f" fill-opacity="0.00" stroke="currentColor" stroke-opacity="0.25" stroke-width="0.6"/>
<rect x="370" y="140" width="20" height="20" fill="#eea66f" fill-opacity="0.00" stroke="currentColor" stroke-opacity="0.25" stroke-width="0.6"/>
<rect x="390" y="140" width="20" height="20" fill="#eea66f" fill-opacity="0.00" stroke="currentColor" stroke-opacity="0.25" stroke-width="0.6"/>
<text x="162" y="174" font-size="11" text-anchor="end" fill="currentColor">output 6 (5)</text>
<rect x="170" y="160" width="20" height="20" fill="#eea66f" fill-opacity="0.00" stroke="currentColor" stroke-opacity="0.25" stroke-width="0.6"/>
<rect x="190" y="160" width="20" height="20" fill="#eea66f" fill-opacity="0.00" stroke="currentColor" stroke-opacity="0.25" stroke-width="0.6"/>
<rect x="210" y="160" width="20" height="20" fill="#eea66f" fill-opacity="0.00" stroke="currentColor" stroke-opacity="0.25" stroke-width="0.6"/>
<rect x="230" y="160" width="20" height="20" fill="#eea66f" fill-opacity="0.00" stroke="currentColor" stroke-opacity="0.25" stroke-width="0.6"/>
<rect x="250" y="160" width="20" height="20" fill="#eea66f" fill-opacity="0.01" stroke="currentColor" stroke-opacity="0.25" stroke-width="0.6"/>
<rect x="270" y="160" width="20" height="20" fill="#eea66f" fill-opacity="0.98" stroke="currentColor" stroke-opacity="0.25" stroke-width="0.6"/>
<rect x="290" y="160" width="20" height="20" fill="#eea66f" fill-opacity="0.00" stroke="currentColor" stroke-opacity="0.25" stroke-width="0.6"/>
<rect x="310" y="160" width="20" height="20" fill="#eea66f" fill-opacity="0.00" stroke="currentColor" stroke-opacity="0.25" stroke-width="0.6"/>
<rect x="330" y="160" width="20" height="20" fill="#eea66f" fill-opacity="0.00" stroke="currentColor" stroke-opacity="0.25" stroke-width="0.6"/>
<rect x="350" y="160" width="20" height="20" fill="#eea66f" fill-opacity="0.00" stroke="currentColor" stroke-opacity="0.25" stroke-width="0.6"/>
<rect x="370" y="160" width="20" height="20" fill="#eea66f" fill-opacity="0.00" stroke="currentColor" stroke-opacity="0.25" stroke-width="0.6"/>
<rect x="390" y="160" width="20" height="20" fill="#eea66f" fill-opacity="0.00" stroke="currentColor" stroke-opacity="0.25" stroke-width="0.6"/>
<text x="162" y="194" font-size="11" text-anchor="end" fill="currentColor">output 7 (0)</text>
<rect x="170" y="180" width="20" height="20" fill="#eea66f" fill-opacity="0.01" stroke="currentColor" stroke-opacity="0.25" stroke-width="0.6"/>
<rect x="190" y="180" width="20" height="20" fill="#eea66f" fill-opacity="0.01" stroke="currentColor" stroke-opacity="0.25" stroke-width="0.6"/>
<rect x="210" y="180" width="20" height="20" fill="#eea66f" fill-opacity="0.00" stroke="currentColor" stroke-opacity="0.25" stroke-width="0.6"/>
<rect x="230" y="180" width="20" height="20" fill="#eea66f" fill-opacity="0.02" stroke="currentColor" stroke-opacity="0.25" stroke-width="0.6"/>
<rect x="250" y="180" width="20" height="20" fill="#eea66f" fill-opacity="0.95" stroke="currentColor" stroke-opacity="0.25" stroke-width="0.6"/>
<rect x="270" y="180" width="20" height="20" fill="#eea66f" fill-opacity="0.00" stroke="currentColor" stroke-opacity="0.25" stroke-width="0.6"/>
<rect x="290" y="180" width="20" height="20" fill="#eea66f" fill-opacity="0.00" stroke="currentColor" stroke-opacity="0.25" stroke-width="0.6"/>
<rect x="310" y="180" width="20" height="20" fill="#eea66f" fill-opacity="0.00" stroke="currentColor" stroke-opacity="0.25" stroke-width="0.6"/>
<rect x="330" y="180" width="20" height="20" fill="#eea66f" fill-opacity="0.00" stroke="currentColor" stroke-opacity="0.25" stroke-width="0.6"/>
<rect x="350" y="180" width="20" height="20" fill="#eea66f" fill-opacity="0.00" stroke="currentColor" stroke-opacity="0.25" stroke-width="0.6"/>
<rect x="370" y="180" width="20" height="20" fill="#eea66f" fill-opacity="0.00" stroke="currentColor" stroke-opacity="0.25" stroke-width="0.6"/>
<rect x="390" y="180" width="20" height="20" fill="#eea66f" fill-opacity="0.00" stroke="currentColor" stroke-opacity="0.25" stroke-width="0.6"/>
<text x="162" y="214" font-size="11" text-anchor="end" fill="currentColor">output 8 (2)</text>
<rect x="170" y="200" width="20" height="20" fill="#eea66f" fill-opacity="0.00" stroke="currentColor" stroke-opacity="0.25" stroke-width="0.6"/>
<rect x="190" y="200" width="20" height="20" fill="#eea66f" fill-opacity="0.00" stroke="currentColor" stroke-opacity="0.25" stroke-width="0.6"/>
<rect x="210" y="200" width="20" height="20" fill="#eea66f" fill-opacity="0.00" stroke="currentColor" stroke-opacity="0.25" stroke-width="0.6"/>
<rect x="230" y="200" width="20" height="20" fill="#eea66f" fill-opacity="0.98" stroke="currentColor" stroke-opacity="0.25" stroke-width="0.6"/>
<rect x="250" y="200" width="20" height="20" fill="#eea66f" fill-opacity="0.00" stroke="currentColor" stroke-opacity="0.25" stroke-width="0.6"/>
<rect x="270" y="200" width="20" height="20" fill="#eea66f" fill-opacity="0.00" stroke="currentColor" stroke-opacity="0.25" stroke-width="0.6"/>
<rect x="290" y="200" width="20" height="20" fill="#eea66f" fill-opacity="0.01" stroke="currentColor" stroke-opacity="0.25" stroke-width="0.6"/>
<rect x="310" y="200" width="20" height="20" fill="#eea66f" fill-opacity="0.00" stroke="currentColor" stroke-opacity="0.25" stroke-width="0.6"/>
<rect x="330" y="200" width="20" height="20" fill="#eea66f" fill-opacity="0.00" stroke="currentColor" stroke-opacity="0.25" stroke-width="0.6"/>
<rect x="350" y="200" width="20" height="20" fill="#eea66f" fill-opacity="0.00" stroke="currentColor" stroke-opacity="0.25" stroke-width="0.6"/>
<rect x="370" y="200" width="20" height="20" fill="#eea66f" fill-opacity="0.00" stroke="currentColor" stroke-opacity="0.25" stroke-width="0.6"/>
<rect x="390" y="200" width="20" height="20" fill="#eea66f" fill-opacity="0.00" stroke="currentColor" stroke-opacity="0.25" stroke-width="0.6"/>
<text x="162" y="234" font-size="11" text-anchor="end" fill="currentColor">output 9 (5)</text>
<rect x="170" y="220" width="20" height="20" fill="#eea66f" fill-opacity="0.00" stroke="currentColor" stroke-opacity="0.25" stroke-width="0.6"/>
<rect x="190" y="220" width="20" height="20" fill="#eea66f" fill-opacity="0.01" stroke="currentColor" stroke-opacity="0.25" stroke-width="0.6"/>
<rect x="210" y="220" width="20" height="20" fill="#eea66f" fill-opacity="0.94" stroke="currentColor" stroke-opacity="0.25" stroke-width="0.6"/>
<rect x="230" y="220" width="20" height="20" fill="#eea66f" fill-opacity="0.03" stroke="currentColor" stroke-opacity="0.25" stroke-width="0.6"/>
<rect x="250" y="220" width="20" height="20" fill="#eea66f" fill-opacity="0.00" stroke="currentColor" stroke-opacity="0.25" stroke-width="0.6"/>
<rect x="270" y="220" width="20" height="20" fill="#eea66f" fill-opacity="0.00" stroke="currentColor" stroke-opacity="0.25" stroke-width="0.6"/>
<rect x="290" y="220" width="20" height="20" fill="#eea66f" fill-opacity="0.01" stroke="currentColor" stroke-opacity="0.25" stroke-width="0.6"/>
<rect x="310" y="220" width="20" height="20" fill="#eea66f" fill-opacity="0.00" stroke="currentColor" stroke-opacity="0.25" stroke-width="0.6"/>
<rect x="330" y="220" width="20" height="20" fill="#eea66f" fill-opacity="0.00" stroke="currentColor" stroke-opacity="0.25" stroke-width="0.6"/>
<rect x="350" y="220" width="20" height="20" fill="#eea66f" fill-opacity="0.00" stroke="currentColor" stroke-opacity="0.25" stroke-width="0.6"/>
<rect x="370" y="220" width="20" height="20" fill="#eea66f" fill-opacity="0.01" stroke="currentColor" stroke-opacity="0.25" stroke-width="0.6"/>
<rect x="390" y="220" width="20" height="20" fill="#eea66f" fill-opacity="0.00" stroke="currentColor" stroke-opacity="0.25" stroke-width="0.6"/>
<text x="162" y="254" font-size="11" text-anchor="end" fill="currentColor">output 10 (6)</text>
<rect x="170" y="240" width="20" height="20" fill="#eea66f" fill-opacity="0.03" stroke="currentColor" stroke-opacity="0.25" stroke-width="0.6"/>
<rect x="190" y="240" width="20" height="20" fill="#eea66f" fill-opacity="0.94" stroke="currentColor" stroke-opacity="0.25" stroke-width="0.6"/>
<rect x="210" y="240" width="20" height="20" fill="#eea66f" fill-opacity="0.00" stroke="currentColor" stroke-opacity="0.25" stroke-width="0.6"/>
<rect x="230" y="240" width="20" height="20" fill="#eea66f" fill-opacity="0.00" stroke="currentColor" stroke-opacity="0.25" stroke-width="0.6"/>
<rect x="250" y="240" width="20" height="20" fill="#eea66f" fill-opacity="0.00" stroke="currentColor" stroke-opacity="0.25" stroke-width="0.6"/>
<rect x="270" y="240" width="20" height="20" fill="#eea66f" fill-opacity="0.01" stroke="currentColor" stroke-opacity="0.25" stroke-width="0.6"/>
<rect x="290" y="240" width="20" height="20" fill="#eea66f" fill-opacity="0.00" stroke="currentColor" stroke-opacity="0.25" stroke-width="0.6"/>
<rect x="310" y="240" width="20" height="20" fill="#eea66f" fill-opacity="0.00" stroke="currentColor" stroke-opacity="0.25" stroke-width="0.6"/>
<rect x="330" y="240" width="20" height="20" fill="#eea66f" fill-opacity="0.00" stroke="currentColor" stroke-opacity="0.25" stroke-width="0.6"/>
<rect x="350" y="240" width="20" height="20" fill="#eea66f" fill-opacity="0.00" stroke="currentColor" stroke-opacity="0.25" stroke-width="0.6"/>
<rect x="370" y="240" width="20" height="20" fill="#eea66f" fill-opacity="0.00" stroke="currentColor" stroke-opacity="0.25" stroke-width="0.6"/>
<rect x="390" y="240" width="20" height="20" fill="#eea66f" fill-opacity="0.00" stroke="currentColor" stroke-opacity="0.25" stroke-width="0.6"/>
<text x="162" y="274" font-size="11" text-anchor="end" fill="currentColor">output 11 (1)</text>
<rect x="170" y="260" width="20" height="20" fill="#eea66f" fill-opacity="0.73" stroke="currentColor" stroke-opacity="0.25" stroke-width="0.6"/>
<rect x="190" y="260" width="20" height="20" fill="#eea66f" fill-opacity="0.05" stroke="currentColor" stroke-opacity="0.25" stroke-width="0.6"/>
<rect x="210" y="260" width="20" height="20" fill="#eea66f" fill-opacity="0.01" stroke="currentColor" stroke-opacity="0.25" stroke-width="0.6"/>
<rect x="230" y="260" width="20" height="20" fill="#eea66f" fill-opacity="0.00" stroke="currentColor" stroke-opacity="0.25" stroke-width="0.6"/>
<rect x="250" y="260" width="20" height="20" fill="#eea66f" fill-opacity="0.03" stroke="currentColor" stroke-opacity="0.25" stroke-width="0.6"/>
<rect x="270" y="260" width="20" height="20" fill="#eea66f" fill-opacity="0.00" stroke="currentColor" stroke-opacity="0.25" stroke-width="0.6"/>
<rect x="290" y="260" width="20" height="20" fill="#eea66f" fill-opacity="0.00" stroke="currentColor" stroke-opacity="0.25" stroke-width="0.6"/>
<rect x="310" y="260" width="20" height="20" fill="#eea66f" fill-opacity="0.01" stroke="currentColor" stroke-opacity="0.25" stroke-width="0.6"/>
<rect x="330" y="260" width="20" height="20" fill="#eea66f" fill-opacity="0.08" stroke="currentColor" stroke-opacity="0.25" stroke-width="0.6"/>
<rect x="350" y="260" width="20" height="20" fill="#eea66f" fill-opacity="0.02" stroke="currentColor" stroke-opacity="0.25" stroke-width="0.6"/>
<rect x="370" y="260" width="20" height="20" fill="#eea66f" fill-opacity="0.02" stroke="currentColor" stroke-opacity="0.25" stroke-width="0.6"/>
<rect x="390" y="260" width="20" height="20" fill="#eea66f" fill-opacity="0.04" stroke="currentColor" stroke-opacity="0.25" stroke-width="0.6"/>
<rect x="170" y="40" width="240" height="240" fill="none" stroke="currentColor" stroke-width="1"/>
<text x="440" y="52" font-size="12" fill="currentColor">weight</text>
<rect x="440" y="64" width="20" height="20" fill="#eea66f" fill-opacity="1.0" stroke="currentColor" stroke-width="0.6"/>
<text x="468" y="78" font-size="12" fill="currentColor">1.0</text>
<rect x="440" y="90" width="20" height="20" fill="#eea66f" fill-opacity="0.5" stroke="currentColor" stroke-width="0.6"/>
<text x="468" y="104" font-size="12" fill="currentColor">0.5</text>
<rect x="440" y="116" width="20" height="20" fill="#eea66f" fill-opacity="0.1" stroke="currentColor" stroke-width="0.6"/>
<text x="468" y="130" font-size="12" fill="currentColor">0.1</text>
</svg>
<figcaption>Figure 18.4. Attention weights learned by the program while reversing the test sequence 1 6 5 2 0 5 2 6 2 5 1 4 (drawn from the printed output). Each output step puts almost all its weight on one input position, and the positions run backwards: the model has discovered the alignment of the task on its own.</figcaption>
</figure>

The bright cells run along the anti-diagonal: output step 0 looks at input position 11, step 1 at position 10, and
so on. Bahdanau et al. showed the same kind of picture for English-French sentences, where the weights follow the
word order, mostly diagonal, with local swaps where French puts the adjective after the noun.

A caution about reading such pictures: attention weights show where the model *read*, which is not always the same
as which inputs *caused* its decision. Jain and Wallace (2019) found cases where very different attention weights
gave the same predictions, and Wiegreffe and Pinter (2019) argued about when the weights can still be informative.
Treat them as evidence to test, not as an explanation ([Chapter 22](22-Machine-Learning-in-Practice.md)).

### From additive to dot-product attention

Luong, Pham and Manning (2015) compared simpler scores, the **dot product** $e_{t,i} = s_t \cdot h_i$ and the
**bilinear** form $s_t^\top W h_i$, and found them as good or better, and much faster, since all scores for all
positions become one matrix product. Notice the shape of what attention computes: a **query** (the decoder state)
is compared with **keys** (the encoder states), and the result weights an average of **values** (again the encoder
states). Make queries, keys and values separate learned projections, let every position of a sequence attend to every
other position of the same sequence, and drop the recurrence altogether: that is the transformer,
[Chapter 19](19-Transformers.md).

## Check yourself

??? question "1. How many weights do a vanilla RNN, a GRU and an LSTM have with hidden size 16 and input size 8?"

    A vanilla RNN has $W$ ($16 \times 16 = 256$), $U$ ($16 \times 8 = 128$) and $b$ (16): 400. Each GRU gate and the
    candidate has the same shape, so $3 \cdot 400 = 1{,}200$; the LSTM has four such blocks, $1{,}600$. The output
    layer is extra in each case.

??? question "2. For the scalar RNN of 18.3 (w = 0.5, u = 1, inputs 1, 0, -1), compute dh_3/dh_1."

    $\partial h_3/\partial h_1 = \frac{\partial h_3}{\partial h_2}\frac{\partial h_2}{\partial h_1} =
    (1 - h_3^2)\, w \cdot (1 - h_2^2)\, w$. With $h_2 = 0.3634$, $h_3 = -0.6741$:
    $(1 - 0.4545) \cdot 0.5 \cdot (1 - 0.1321) \cdot 0.5 = 0.5455 \cdot 0.5 \cdot 0.8679 \cdot 0.5 \approx 0.118$.
    A unit change in $h_1$ moves $h_3$ by only about 0.12, after two steps.

??? question "3. Show that the gradient bound of 18.3 still goes to 0 when the norm of W is exactly 1, if every state entry stays at least eta away from 0."

    If every state entry satisfies $|h_{t,i}| \ge \eta > 0$, then $\|D_t\| \le 1 - \eta^2 < 1$, and the same
    argument gives $\|\partial h_T/\partial h_0\| \le ((1 - \eta^2)\|W\|)^T$. With $\|W\| = 1$ this is
    $(1 - \eta^2)^T \to 0$. That is what Part 3 of the program shows for tanh with $\rho = 1$: the $\tanh$ slopes
    alone make the gradient vanish.

??? question "4. Derive the negative-sampling gradient with respect to a negative word's vector u_n."

    The only term containing $u_n$ is $-\log\sigma(-u_n \cdot v_c)$. With $z = u_n \cdot v_c$,
    $\frac{d}{dz}[-\log \sigma(-z)] = 1 - \sigma(-z) = \sigma(z)$, and $\partial z/\partial u_n = v_c$. So
    $\partial \ell / \partial u_n = \sigma(u_n \cdot v_c)\, v_c$: the more confidently the model wrongly says "yes", the
    harder $u_n$ is pushed away from $v_c$. If $n$ is drawn twice, the two contributions add (the program's
    `np.add.at` handles exactly that).

??? question "5. In a corpus of 1000 pairs, 'rover' appears in 40, 'wheel' in 50, and the pair (rover, wheel) 10 times. What is the PMI? What dot product would SGNS with k = 5 aim for?"

    $\operatorname{PMI} = \log \frac{10 \cdot 1000}{40 \cdot 50} = \log 5 \approx 1.609$. The SGNS optimum is
    $\operatorname{PMI} - \log k = \log 5 - \log 5 = 0$. A positive PMI can still give a dot product of 0 or below
    once the shift by $\log k$ is applied, which is one reason the shifted PMI matrix is not the same as PMI.

??? question "6. An LSTM's forget gates all equal sigma(b). For which bias b does at least half the cell's content survive 100 steps?"

    We need $\sigma(b)^{100} \ge 0.5$, so $\sigma(b) \ge 0.5^{1/100} = 0.99309$. Since $\sigma(b) = p$ means
    $b = \log(p/(1-p))$, $b \ge \log(0.99309/0.00691) \approx 4.97$. A bias of about 5. With the usual $b = 1$, only
    $0.731^{100} \approx 2 \times 10^{-14}$ would survive, so the network must learn to raise its forget gates.

??? question "7. Show that if a GRU's update gate is always 1, its state never changes, and if z = 0 and r = 1 always, it is a vanilla RNN."

    With $z_t = 1$: $h_t = 0 \cdot n_t + 1 \cdot h_{t-1} = h_{t-1}$, so $h_t = h_0$ forever (perfect memory, no
    input). With $z_t = 0$ and $r_t = 1$: $h_t = n_t = \tanh(W_n h_{t-1} + U_n x_t + b_n)$, exactly the Elman update.
    The GRU interpolates between these two extremes, unit by unit and step by step.

??? question "8. Write the code: beam search with beam width B for a model given as a function next_logprobs(prefix) returning log-probabilities over V tokens, stopping at an end token or a maximum length."

    ```python
    import numpy as np

    def beam_search(next_logprobs, B, end, max_len):
        beams = [((), 0.0)]                         # (prefix, total log-probability)
        done = []
        for _ in range(max_len):
            cand = []
            for prefix, score in beams:
                lp = next_logprobs(prefix)
                for tok in np.argsort(lp)[-B:]:     # only the B best extensions can survive
                    cand.append((prefix + (int(tok),), score + lp[tok]))
            cand.sort(key=lambda c: -c[1])
            beams = []
            for prefix, score in cand[:B]:
                (done if prefix[-1] == end else beams).append((prefix, score))
            if not beams:
                break
        return max(done + beams, key=lambda c: c[1])

    # a toy model where greedy fails: token 0 first looks best, but leads nowhere good
    table = {(): [np.log(0.6), np.log(0.4), -50],
             (0,): [np.log(0.34), np.log(0.33), np.log(0.33)],
             (1,): [-50, -50, 0.0]}
    f = lambda p: np.array(table.get(p, [-50, -50, 0.0]))
    print(beam_search(f, 1, end=2, max_len=3))   # greedy: (0, 0, 2), log-probability log 0.204
    print(beam_search(f, 2, end=2, max_len=3))   # beam 2: (1, 2), log-probability log 0.4
    ```

    Greedy picks token 0 (0.6), then 0 again (0.34), then the end token, for a total probability of
    $0.6 \cdot 0.34 = 0.204$ (log $-1.590$). The beam keeps the prefix (1,) as well, whose only continuation, the end
    token, has probability 1, for a total of 0.4 (log $-0.916$).

??? question "9. Write the code: clip a list of gradient arrays to a maximum total norm, as used against exploding gradients."

    ```python
    import numpy as np

    def clip_by_norm(grads, max_norm):
        total = np.sqrt(sum(np.sum(g * g) for g in grads))
        if total > max_norm:
            grads = [g * (max_norm / total) for g in grads]
        return grads, total

    g, n = clip_by_norm([np.array([3.0, 4.0]), np.array([12.0])], 6.5)
    print(n, [x.round(3) for x in g])   # norm 13.0, every entry halved
    ```

    Scaling all gradients by the same factor keeps the direction of the step and only limits its length, which is
    why clipping by the global norm is preferred to clipping each entry separately.

??? question "10. Why did reversing the source sentence help Sutskever et al.'s model, but makes no difference with attention?"

    Without attention, everything passes through the final encoder state. In normal order, the first source word is
    $T_x$ encoder steps plus 1 decoder step away from the first target word; reversed, it is only one or two steps
    away, so the start of the translation, which conditions everything after it, gets a short, strong gradient path.
    (The average distance does not change; the many short dependencies are what help.) With attention, every decoder
    step reaches every encoder state directly through $c_t$, so the order no longer changes the path lengths.

??? question "11. How many attention scores does Bahdanau attention compute for a 50-word source and a 60-word target? How does that compare with the encoder's work?"

    One score per (target step, source position): $60 \cdot 50 = 3{,}000$, each costing a small MLP evaluation. The
    encoder makes 50 recurrent steps. The quadratic count was not a problem for sentences, but for documents of
    thousands of tokens it becomes the main cost, a theme of [Chapter 19](19-Transformers.md) (19.8).

??? question "12. Our word2vec analogies exclude the three query words. Explain with the additive model why king - man + woman is close to king itself."

    In the additive model, $v_{\text{king}} - v_{\text{man}} + v_{\text{woman}} = v_{\text{king}} + (g_f - g_m)$:
    king plus a gender shift. If the gender difference is small compared with the vectors themselves, the result is
    still very close to $v_{\text{king}}$, often closer than to $v_{\text{queen}}$. Excluding the query words hides
    that, which is why careful evaluations report both ways.

## What you learned

- A sequence model computes $p(x_t \mid x_{<t})$; by the chain rule this defines the probability of whole sequences,
  and its loss is a sum of next-step cross-entropies.
- word2vec learns word vectors by predicting context words; negative sampling makes each step cost $O(kd)$, and its
  optimum is a shifted PMI matrix, so counting plus an SVD gives similar vectors.
- An RNN applies the same weights at every step and carries a state; BPTT is backpropagation through the unrolled
  network, with gradients summed over time.
- The Jacobian over $T$ steps is a product of $T$ factors, so gradients vanish (norm below 1) or explode (above 1);
  clipping fixes explosions, gating fixes vanishing.
- The LSTM's cell is updated by a forget-multiply and an add, giving a path with no squashing; the GRU interpolates
  between old and new state. Initialising the forget or update bias to "remember" matters.
- Seq2seq models encode a source and decode a target with teacher forcing and beam search, but a single summary
  vector is a bottleneck.
- Attention scores every source position, softmaxes the scores and reads a weighted average, giving every output a
  direct path to every input; the alignment it learns is unsupervised.

**Next:** [Chapter 19](19-Transformers.md), transformers, which keep attention, drop recurrence, and process every
position in parallel.

## Further reading

- I. Goodfellow, Y. Bengio and A. Courville, *Deep Learning*, 2016: chapter 10 (sequence modelling: recurrent and
  recursive nets).
- D. Jurafsky and J. H. Martin, *Speech and Language Processing*, 3rd ed. draft: chapters on n-gram language models,
  vector semantics and embeddings, RNNs and LSTMs.
- T. Mikolov, K. Chen, G. Corrado and J. Dean, "Efficient estimation of word representations in vector space", 2013;
  T. Mikolov, I. Sutskever, K. Chen, G. Corrado and J. Dean, "Distributed representations of words and phrases and
  their compositionality", NeurIPS 2013; T. Mikolov, W. Yih and G. Zweig, "Linguistic regularities in continuous
  space word representations", NAACL 2013.
- O. Levy and Y. Goldberg, "Neural word embedding as implicit matrix factorization", NeurIPS 2014; J. Pennington,
  R. Socher and C. D. Manning, "GloVe: global vectors for word representation", EMNLP 2014.
- J. L. Elman, "Finding structure in time", *Cognitive Science* 14, 1990; P. J. Werbos, "Backpropagation through
  time: what it does and how to do it", *Proceedings of the IEEE* 78, 1990.
- Y. Bengio, P. Simard and P. Frasconi, "Learning long-term dependencies with gradient descent is difficult",
  *IEEE Transactions on Neural Networks* 5, 1994; R. Pascanu, T. Mikolov and Y. Bengio, "On the difficulty of
  training recurrent neural networks", ICML 2013.
- S. Hochreiter and J. Schmidhuber, "Long short-term memory", *Neural Computation* 9, 1997; F. A. Gers,
  J. Schmidhuber and F. Cummins, "Learning to forget: continual prediction with LSTM", *Neural Computation* 12, 2000.
- K. Cho, B. van Merriënboer, C. Gulcehre, D. Bahdanau, F. Bougares, H. Schwenk and Y. Bengio, "Learning phrase
  representations using RNN encoder-decoder for statistical machine translation", EMNLP 2014.
- R. Jozefowicz, W. Zaremba and I. Sutskever, "An empirical exploration of recurrent network architectures", ICML
  2015; K. Greff, R. K. Srivastava, J. Koutník, B. R. Steunebrink and J. Schmidhuber, "LSTM: a search space odyssey",
  *IEEE Transactions on Neural Networks and Learning Systems* 28, 2017; C. Tallec and Y. Ollivier, "Can recurrent
  neural networks warp time?", ICLR 2018.
- I. Sutskever, O. Vinyals and Q. V. Le, "Sequence to sequence learning with neural networks", NeurIPS 2014.
- D. Bahdanau, K. Cho and Y. Bengio, "Neural machine translation by jointly learning to align and translate", 2014
  (ICLR 2015); M.-T. Luong, H. Pham and C. D. Manning, "Effective approaches to attention-based neural machine
  translation", EMNLP 2015.
- S. Jain and B. C. Wallace, "Attention is not explanation", NAACL 2019; S. Wiegreffe and Y. Pinter, "Attention is not
  not explanation", EMNLP 2019.
- On this site: [Chapter 15](15-Neural-Networks-and-Backpropagation.md) (autodiff), [Chapter 17](17-Convolutional-Networks.md)
  (weight sharing in space), [Chapter 19](19-Transformers.md), and [Chapter 20](20-Generative-Models.md)
  (autoregressive models as generative models). The Algorithms book's [dynamic programming chapter](../algorithms/13-Dynamic-Programming.md)
  has the Viterbi-style exact search that beam search approximates.
