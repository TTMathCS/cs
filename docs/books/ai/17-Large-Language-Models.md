# 17. Large language models

*A program that only ever learns to guess the next word of a text can, at large enough scale, answer questions,
translate, summarise and write code. This chapter answers the question: what exactly is a large language model, how
is it trained and steered, and what can and can't we say about what it does? You will build a tiny neural language
model and measure it against the true probabilities of the text it learned, decode it with greedy search, temperature,
top-k and nucleus sampling, derive why the training objective works, fit a reward model to human comparisons and
derive the policy that learning from human feedback is aiming for, prove that direct preference optimisation reaches
the same policy without a reward model, build retrieval and a tool-using agent loop around a fake model, and work
through the statistics that make language-model evaluation easy to get wrong.*

!!! abstract "In this chapter"
    **You will learn:**

    - what a language model computes (a probability for the next token), why cross-entropy training makes it learn
      the true conditional probabilities, and what perplexity measures
    - what pretraining at scale involved for GPT-3 (data, parameters, compute) and what few-shot prompting is
    - greedy decoding, temperature, top-k and nucleus sampling, from scratch, with a proof that temperature controls
      entropy
    - instruction tuning, reward models from pairwise comparisons, the KL-regularised objective and its exact
      optimum, and direct preference optimisation (DPO) derived from it
    - retrieval-augmented generation and a ReAct-style agent loop, built from scratch around a fake model
    - chain-of-thought prompting, self-consistency, the pass@k estimator, contamination and benchmark noise
    - the documented limits: hallucination, reasoning failures and cost, separating what is known from what is claimed

    **You need:** [Chapter 16](16-Natural-Language-Processing.md) (tokens, n-gram models, perplexity) and the
    transformer of [Machine learning, Chapter 19](../machine-learning/19-Transformers.md). Policy gradients from
    [Chapter 15](15-Reinforcement-Learning.md) help in 17.4. Logarithms, expectations and the softmax
    ([Machine learning, Section 3.7](../machine-learning/03-The-Math-Toolkit.md#37-information-entropy-cross-entropy-kl-divergence)).

    **Levels:** 17.1 and 17.3 are beginner to intermediate; 17.2, 17.5 and 17.7 are intermediate; 17.4 and 17.6 are
    advanced (the derivations in 17.4 are graduate level).

## 17.1 What a language model is: predicting the next token

**The question:** what does a language model actually compute, and why would getting good at that one thing be
useful?

A **token** is the unit of text a model reads: a word, a piece of a word, or a single character. Real models split
text with a learned tokenizer such as byte-pair encoding ([Machine learning, Section 19.6](../machine-learning/19-Transformers.md#196-tokenization-byte-pair-encoding-from-scratch)),
so that common words are one token and rare words are a few. The **vocabulary** is the set of all $V$ tokens. In this
chapter's toy examples a token is simply a word or a full stop.

A **language model** is a probability distribution over sequences of tokens. Any distribution over sequences can be
written, without assuming anything, by the **chain rule of probability**:

$$
P(x_1, x_2, \dots, x_T) = P(x_1)\,P(x_2 \mid x_1)\,P(x_3 \mid x_1, x_2) \cdots P(x_T \mid x_1, \dots, x_{T-1}) = \prod_{t=1}^{T} P(x_t \mid x_{<t}).
$$

Here $x_{<t}$ means all tokens before position $t$, called the **context** or **prefix**. So a model that gives, for
every context, a probability for every possible next token defines a probability for every whole text. This is an
**autoregressive** (or causal) language model, and every model in the GPT line is one. The network takes the context,
computes one real number per vocabulary token, called a **logit** $z_i$, and turns the logits into probabilities with
the **softmax**

$$
P(x_t = i \mid x_{<t}) = \frac{e^{z_i}}{\sum_{j=1}^{V} e^{z_j}}.
$$

The network in modern models is a decoder-only transformer, built from scratch in
[Machine learning, Chapter 19](../machine-learning/19-Transformers.md); here we treat it as a function from a context
to $V$ logits and look at what is done with it.

### Generating text

To write text with the model, start from a prompt, compute the next-token distribution, choose a token, append it to
the context and repeat (Figure 17.1). How to choose is the subject of 17.3. Notice what this loop does not have: no
plan, no database of facts, no separate "answer" step. Everything the model produces, from a translation to a
program, comes out one token at a time from this loop.

<figure class="mars-fig" markdown="0">
<svg viewBox="0 0 680 300" role="img" aria-label="The context tokens the rover drives to the go into the language model, which outputs a probability for each next token: crater 0.5, hill 0.3, dune 0.2, rock 0. The sampled token crater is appended to the context and the loop repeats.">
<defs><marker id="arr171" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="currentColor"/></marker></defs>
<rect x="20.0" y="40.0" width="36.0" height="30.0" rx="5" fill="#9cc9ea" fill-opacity="0.5" stroke="currentColor" stroke-width="1.2"/>
<text x="38.0" y="60.0" font-size="13" text-anchor="middle" fill="currentColor">the</text>
<rect x="62.0" y="40.0" width="52.0" height="30.0" rx="5" fill="#9cc9ea" fill-opacity="0.5" stroke="currentColor" stroke-width="1.2"/>
<text x="88.0" y="60.0" font-size="13" text-anchor="middle" fill="currentColor">rover</text>
<rect x="120.0" y="40.0" width="60.0" height="30.0" rx="5" fill="#9cc9ea" fill-opacity="0.5" stroke="currentColor" stroke-width="1.2"/>
<text x="150.0" y="60.0" font-size="13" text-anchor="middle" fill="currentColor">drives</text>
<rect x="186.0" y="40.0" width="28.0" height="30.0" rx="5" fill="#9cc9ea" fill-opacity="0.5" stroke="currentColor" stroke-width="1.2"/>
<text x="200.0" y="60.0" font-size="13" text-anchor="middle" fill="currentColor">to</text>
<rect x="220.0" y="40.0" width="36.0" height="30.0" rx="5" fill="#9cc9ea" fill-opacity="0.5" stroke="currentColor" stroke-width="1.2"/>
<text x="238.0" y="60.0" font-size="13" text-anchor="middle" fill="currentColor">the</text>
<rect x="262.0" y="40.0" width="62.0" height="30.0" rx="5" fill="#eea66f" fill-opacity="0.35" stroke="currentColor" stroke-width="1.2"/>
<text x="293.0" y="60.0" font-size="13" text-anchor="middle" fill="currentColor">?</text>
<text x="20.0" y="28.0" font-size="12" text-anchor="start" fill="currentColor">context: the tokens so far</text>
<line x1="150.0" y1="75.0" x2="150.0" y2="115.0" stroke="currentColor" stroke-width="1.2" marker-end="url(#arr171)"/>
<rect x="80.0" y="118.0" width="140.0" height="44.0" rx="5" fill="#7ccf9a" fill-opacity="0.45" stroke="currentColor" stroke-width="1.2"/>
<text x="150.0" y="138.0" font-size="13" text-anchor="middle" fill="currentColor">language model</text>
<text x="150.0" y="154.0" font-size="11" text-anchor="middle" fill="currentColor">(a network)</text>
<line x1="222.0" y1="140.0" x2="300.0" y2="140.0" stroke="currentColor" stroke-width="1.2" marker-end="url(#arr171)"/>
<text x="261.0" y="132.0" font-size="11" text-anchor="middle" fill="currentColor">softmax</text>
<rect x="310.0" y="155.0" width="40" height="75.0" fill="#9cc9ea" fill-opacity="0.7" stroke="currentColor" stroke-width="1"/>
<text x="330.0" y="246.0" font-size="12" text-anchor="middle" fill="currentColor">crater</text>
<text x="330.0" y="149.0" font-size="11" text-anchor="middle" fill="currentColor">0.5</text>
<rect x="372.0" y="185.0" width="40" height="45.0" fill="#9cc9ea" fill-opacity="0.7" stroke="currentColor" stroke-width="1"/>
<text x="392.0" y="246.0" font-size="12" text-anchor="middle" fill="currentColor">hill</text>
<text x="392.0" y="179.0" font-size="11" text-anchor="middle" fill="currentColor">0.3</text>
<rect x="434.0" y="200.0" width="40" height="30.0" fill="#9cc9ea" fill-opacity="0.7" stroke="currentColor" stroke-width="1"/>
<text x="454.0" y="246.0" font-size="12" text-anchor="middle" fill="currentColor">dune</text>
<text x="454.0" y="194.0" font-size="11" text-anchor="middle" fill="currentColor">0.2</text>
<text x="516.0" y="246.0" font-size="12" text-anchor="middle" fill="currentColor">rock</text>
<text x="516.0" y="224.0" font-size="11" text-anchor="middle" fill="currentColor">0.0</text>
<line x1="304.0" y1="230.0" x2="548.0" y2="230.0" stroke="currentColor" stroke-width="1.2"/>
<text x="428.0" y="266.0" font-size="12" text-anchor="middle" fill="currentColor">P(next token | context)</text>
<line x1="560.0" y1="170.0" x2="600.0" y2="170.0" stroke="currentColor" stroke-width="1.2" marker-end="url(#arr171)"/>
<text x="580.0" y="160.0" font-size="11" text-anchor="middle" fill="currentColor">sample</text>
<rect x="604.0" y="152.0" width="66.0" height="34.0" rx="5" fill="#eea66f" fill-opacity="0.5" stroke="currentColor" stroke-width="1.2"/>
<text x="637.0" y="174.0" font-size="13" text-anchor="middle" fill="currentColor">crater</text>
<path d="M637,150 L637,20 L293.0,20 L293.0,37" fill="none" stroke="currentColor" stroke-width="1.2" stroke-dasharray="5 4" marker-end="url(#arr171)"/>
<text x="520.0" y="14.0" font-size="12" text-anchor="middle" fill="currentColor">append it and repeat</text>
</svg>
<figcaption>Figure 17.1. Autoregressive generation. The model maps the context to a distribution over the next token (here the toy grammar's: after <em>to the</em>, crater 0.5, hill 0.3, dune 0.2); one token is chosen, appended, and the loop repeats. Every output of a language model, however long, is made this way.</figcaption>
</figure>

### Why training on next tokens teaches probabilities

The model has parameters $\theta$ (millions to hundreds of billions of numbers). Training adjusts them to minimise
the **cross-entropy** on a training text, the average negative log-probability the model gives to the token that
actually came next:

$$
\mathcal{L}(\theta) = -\frac{1}{T}\sum_{t=1}^{T} \log P_\theta(x_t \mid x_{<t}).
$$

This is **self-supervised** learning: the labels (the next tokens) are in the text itself, so any text is training
data and no one has to label it. Why is this the right loss? Fix one context $c$ and let $p$ be the true distribution
of the next token after $c$ in the data, and $q$ the model's. The expected loss on that context is

$$
\mathbb{E}_{x \sim p}[-\log q(x)] = -\sum_x p(x)\log q(x) = \underbrace{-\sum_x p(x)\log p(x)}_{H(p)} + \underbrace{\sum_x p(x)\log\frac{p(x)}{q(x)}}_{\mathrm{KL}(p\,\|\,q)}.
$$

**Theorem (cross-entropy is minimised by the truth).** The expected loss is at least $H(p)$, the entropy of the
data, with equality exactly when $q = p$.

**Proof.** We need $\mathrm{KL}(p \,\|\, q) \ge 0$ with equality only at $q = p$ (Gibbs' inequality). Use
$\log u \le u - 1$, which holds for all $u > 0$ with equality only at $u = 1$ (the line $u - 1$ is tangent to the
concave function $\log u$ at $u = 1$). Then, summing over the $x$ with $p(x) > 0$,

$$
-\mathrm{KL}(p\,\|\,q) = \sum_x p(x)\log\frac{q(x)}{p(x)} \le \sum_x p(x)\left(\frac{q(x)}{p(x)} - 1\right) = \sum_{x:\,p(x)>0} q(x) - 1 \le 0,
$$

and equality needs $q(x) = p(x)$ wherever $p(x) > 0$, and then the $q$ values sum to 1 there, so $q = p$. $\square$

So a model that drives the training loss down, on enough data and with enough capacity, is driven toward the true
conditional distribution of the next token, for every context it sees. This is why "just predicting the next word" is
not a small task: to predict the next word of a chemistry textbook, a chess game record or a program well, the model
has to capture whatever regularities produced that text. It does not mean the model ends up knowing those things in
any further sense; it means that its predictions are good to the extent that the training loss is low.

The **perplexity** is $e^{\mathcal{L}}$ (or $2^{\mathcal{L}}$ when the loss is measured in bits). It is the size of a
uniform choice that would be equally surprising: perplexity 10 means the model is, on average, as uncertain as if it
were choosing among 10 equally likely tokens. A model that guesses uniformly has perplexity $V$; a perfect model of a
deterministic text has perplexity 1. Chapter 16 computed perplexities for n-gram models. Perplexity must be measured on
**held-out** text the model was not trained on: on its own training text, a model that memorises scores well without
having learned anything general.

### A worked example by hand

The program below writes its training text from a small probabilistic grammar. Each sentence is a subject (*the
rover* with probability 0.5, *the robot* 0.3, *the lander* 0.2), a verb (*drives to* 0.4, *looks at* 0.3, *takes a
picture of* 0.3), an object (after *drives to*: *the crater* 0.5, *the hill* 0.3, *the dune* 0.2; otherwise *the rock*
0.6, *the sky* 0.2, *the dust* 0.2) and a full stop. Because we wrote the grammar, we know the true probabilities.

Take the sentence *the rover drives to the crater .* after a previous full stop. By the chain rule:

| $t$ | token | context ends with | true $P(x_t \mid x_{<t})$ | $-\ln P$ |
|---|---|---|---|---|
| 1 | the | . | 1 | 0 |
| 2 | rover | . the | 0.5 | 0.693 |
| 3 | drives | the rover | 0.4 | 0.916 |
| 4 | to | rover drives | 1 | 0 |
| 5 | the | drives to | 1 | 0 |
| 6 | crater | to the | 0.5 | 0.693 |
| 7 | . | the crater | 1 | 0 |

The sentence probability is $0.5 \times 0.4 \times 0.5 = 0.1$, the total negative log-probability is
$\ln 10 = 2.303$ nats, the average over 7 tokens is 0.329 nats, and the perplexity of this sentence is
$e^{0.329} = 1.39$. Most tokens are forced by the grammar and cost nothing; all the uncertainty sits in three choices.

The best possible cross-entropy for the whole grammar can also be computed exactly. A sentence carries
$H(\text{subject}) + H(\text{verb}) + H(\text{object} \mid \text{verb})$ nats of uncertainty:
$1.0297 + 1.0889 + (0.4 \times 1.0297 + 0.6 \times 0.9503) = 3.1006$ nats, spread over an expected
$0.4 \times 7 + 0.3 \times 7 + 0.3 \times 9 = 7.6$ tokens, which is 0.4080 nats per token, a perplexity of 1.504. No
model can do better on average.

### A tiny neural language model

The program trains the smallest network that can learn this grammar: it looks at the two previous tokens, replaces
each by a learned vector of 8 numbers (an **embedding**), passes the 16 numbers through one layer of 32 tanh units and
produces 19 logits. This is the design of Bengio and colleagues' neural probabilistic language model (2003), with a
context of two; a transformer replaces the fixed two-token window with attention over the whole context. The
gradient of the cross-entropy with respect to the logits is simply the predicted probabilities minus 1 at the true
token (derived in [Machine learning, Section 6.5](../machine-learning/06-Classification-and-Logistic-Regression.md#65-many-classes-softmax-regression-and-one-vs-rest)),
and backpropagation does the rest. Training uses Adam on the full text of 15,173 words.

```python
--8<-- "books/ai/ch17_tiny_lm.py"
```

```
training text: 15173 words, vocabulary V = 19
   first words: the robot takes a picture of the rock . the lander drives to the ...

1. training the model (8-dim word vectors, 32 tanh units)
   step   1: training loss 2.9995 nats per word
   step  10: training loss 0.6731 nats per word
   step  25: training loss 0.4117 nats per word
   step  50: training loss 0.4090 nats per word
   step 100: training loss 0.4087 nats per word
   1323 parameters; uniform guessing would score ln 19 = 2.9444

2. held-out text (a fresh sample from the same grammar)
   model                       cross-entropy  perplexity
   unigram (word counts only)     2.58777    13.30003
   tiny neural model              0.41446     1.51355
   the true grammar (best)        0.41428     1.51329

3. next-word probabilities: model vs the grammar
   after '. the': rover 0.513 (true 0.5), robot 0.294 (true 0.3), lander 0.193 (true 0.2)
   after 'rover drives': to 1.000 (true 1.0), at 0.000 (true 0.0), a 0.000 (true 0.0)
   after 'of the': rock 0.587 (true 0.6), dust 0.207 (true 0.2), sky 0.205 (true 0.2)
   after 'to the': crater 0.480 (true 0.5), hill 0.311 (true 0.3), dune 0.208 (true 0.2)
```

Read the output against the theorem. The loss starts at 3.0, near $\ln 19 = 2.94$ (uniform guessing), and settles at
0.409, just above the exact optimum of 0.408. On held-out text the model's cross-entropy, 0.41446, is within 0.0002
of the true grammar's 0.41428 on the same text (both differ a little from 0.408 because 500 sentences are a finite
sample). The learned probabilities in part 3 are close to the grammar's, and the remaining differences (0.513 instead
of 0.5) match the frequencies in the particular training sample: the model learned the data it saw, which is what
minimising the loss on that data asks for. A model that only counts words (the unigram line) has perplexity 13.3; the
context brings it down to 1.51.

## 17.2 Pretraining at scale (GPT-3, Brown et al. 2020): data, compute, few-shot prompting

**The question:** the tiny model learned a 19-word grammar. What changes when the same objective is applied to a
large part of the written internet?

### The GPT line

The recipe of **pretraining** (train a large network on next-token prediction over a very large text, then use or
adapt it) appeared in steps. Radford and colleagues' GPT (2018) pretrained a 12-layer transformer decoder on books and
then fine-tuned it for each task. GPT-2 (Radford and colleagues, 2019, with 1.5 billion parameters) showed that a
pretrained model could do some tasks with no fine-tuning, only from the way the prompt was written. GPT-3 (Brown and
colleagues, "Language Models are Few-Shot Learners", 2020) scaled the same design to 175 billion parameters.

The GPT-3 paper reports the following for its largest model: 96 transformer layers, model width $d = 12288$, 96
attention heads, a context of 2048 tokens, and training on 300 billion tokens. The training mixture was weighted
toward a filtered version of Common Crawl (a public crawl of the web; 60 percent of the mixture), with WebText2
(22 percent), two book corpora (8 percent each) and English Wikipedia (3 percent). The weights did not follow the
sizes: the smaller, higher-quality sets were seen more than once while most of Common Crawl was seen less than once.

### How much computation?

A useful rule counts floating-point operations (FLOPs). A matrix-vector product with a weight matrix of $N_W$ entries
costs about $2N_W$ FLOPs (one multiply and one add per weight). Almost all parameters of a transformer sit in such
matrices, so the forward pass costs about $2N$ FLOPs per token for a model of $N$ parameters (ignoring the attention
scores themselves, which are small unless the context is very long; see
[Machine learning, Section 19.8](../machine-learning/19-Transformers.md#198-the-cost-of-attention-efficient-attention)).
The backward pass needs two products of about the same size per weight matrix, one for the gradient with respect to
the input and one for the gradient with respect to the weights, so about $4N$. Training on $D$ tokens therefore costs

$$
C \approx 6ND \text{ FLOPs}.
$$

For GPT-3, $6 \times 175 \times 10^{9} \times 300 \times 10^{9} = 3.15 \times 10^{23}$ FLOPs, which agrees with the
$3.14 \times 10^{23}$ the paper gives for its largest model. At inference the cost is about $2N$ FLOPs per generated
token: 350 billion for GPT-3.

How should a fixed compute budget be split between $N$ and $D$? Kaplan and colleagues (2020) measured that loss falls
as a power law in each of $N$, $D$ and $C$ over many orders of magnitude; Hoffmann and colleagues (2022) refit the
trade-off and concluded that parameters and tokens should grow in about equal proportion, and that many large models
of the time had been trained on too little data. Their 70-billion-parameter model Chinchilla, trained on 1.4 trillion
tokens (about $6 \times 70 \times 10^9 \times 1.4 \times 10^{12} = 5.9 \times 10^{23}$ FLOPs), outperformed their own
280-billion-parameter Gopher on most of the tasks they report. The power laws themselves, how they are fitted and why
they might hold, are in [Machine learning, Section 23.1](../machine-learning/23-Where-Machine-Learning-Goes.md#231-scaling-laws).

### Few-shot prompting

The headline of the GPT-3 paper is in its title. Without changing any parameter, the model can be given a task by
writing it into the context:

- **zero-shot:** a description only: `Translate English to French: cheese =>`
- **one-shot:** the description and one solved example;
- **few-shot:** the description and a few (typically 10 to 100, as many as fit in the context) solved examples, then
  the new input.

The model continues the pattern. The paper calls this **in-context learning**: nothing is learned in the sense of
Chapter 15 (no gradient step), yet performance on many tasks rises with the number of examples in the prompt, and
it reports that this rise is steeper for larger models. Why in-context learning works is an active research question;
one line of work shows that transformers can implement simple learning algorithms, such as a step of gradient
descent on a linear regression, inside their forward pass ([Machine learning, Section 23.3](../machine-learning/23-Where-Machine-Learning-Goes.md#233-in-context-learning-and-emergent-behaviour)
builds this).

There is no mystery about why a pure next-token predictor can follow a few-shot prompt at all: web text contains many
lists of question-answer pairs, translations side by side and worked examples, and continuing such a list correctly
is exactly next-token prediction. The interesting and less understood part is how far this generalises to formats
and tasks that are rare in the data.

### What a pretrained model is not

A pretrained model models text. Asked a question, it continues the text in the way text on the internet tends to
continue, which may be an answer, a list of further questions, or a forum post disagreeing. It has no built-in notion
of being helpful or of being truthful; the theorem of 17.1 only promises that it imitates the data. Turning it into
an assistant is the job of 17.4.

## 17.3 Sampling: temperature, top-k, nucleus (Holtzman et al. 2019)

**The question:** the model gives a probability for every next token. Which one should we write down?

### Greedy and beam search

**Greedy decoding** always takes the most probable next token. **Beam search** keeps the $B$ most probable partial
sequences at each step and returns the most probable complete one; it approximates the single most probable text,
which is a good goal in translation, where there is roughly one right answer. Both are deterministic.

For open-ended text, maximising probability is the wrong goal. On the tiny model, greedy decoding from *the* gives

```
the rover drives to the crater . the rover drives to the crater . the rover drives to the crater . the
```

forever. The reason is simple and general. A greedy decoder whose next token depends only on the last $k$ tokens is a
deterministic function on a finite set of states (the $V^k$ possible windows), and any such function, iterated, must
eventually revisit a state, after which it cycles (the pigeonhole principle). Real transformers see a long context,
not a fixed window, but Holtzman and colleagues ("The Curious Case of Neural Text Degeneration", 2019) documented the
same behaviour in large models: maximisation-based decoding produced bland and repetitive text, and they showed that
human-written text is not made of each step's most probable token; its per-token probabilities vary widely. So we
**sample**: draw the next token at random from the model's distribution.

### Temperature

Sampling from the model exactly reproduces the training distribution, including its rare, bad continuations.
**Temperature** $\tau > 0$ reshapes the distribution before sampling by dividing the logits:

$$
p_i(\tau) = \frac{e^{z_i/\tau}}{\sum_j e^{z_j/\tau}}.
$$

At $\tau = 1$ nothing changes. As $\tau \to 0$ the largest logit dominates and sampling becomes greedy; as
$\tau \to \infty$ all $z_i/\tau \to 0$ and the distribution becomes uniform. In probability terms,
$p_i(\tau) \propto p_i^{1/\tau}$: at $\tau = 0.5$ every probability is squared and renormalised.

**Theorem (temperature controls entropy).** The entropy $H(\tau) = -\sum_i p_i(\tau)\ln p_i(\tau)$ never decreases as
$\tau$ grows, and strictly increases unless all logits are equal.

**Proof.** Write $\beta = 1/\tau$ and $Z(\beta) = \sum_j e^{\beta z_j}$, so $p_i = e^{\beta z_i}/Z$ and
$\ln p_i = \beta z_i - \ln Z$. Then $H = \ln Z - \beta\,\mathbb{E}_p[z]$. Differentiating, $\frac{d}{d\beta}\ln Z = \mathbb{E}_p[z]$
and $\frac{d}{d\beta}\mathbb{E}_p[z] = \mathbb{E}_p[z^2] - \mathbb{E}_p[z]^2 = \mathrm{Var}_p(z)$, so

$$
\frac{dH}{d\beta} = \mathbb{E}_p[z] - \mathbb{E}_p[z] - \beta\,\mathrm{Var}_p(z) = -\beta\,\mathrm{Var}_p(z),
\qquad
\frac{dH}{d\tau} = \frac{dH}{d\beta}\cdot\frac{d\beta}{d\tau} = \frac{\mathrm{Var}_p(z)}{\tau^3} \ge 0.
$$

The variance is zero only if all logits are equal. $\square$

### Top-k and nucleus (top-p) sampling

Lowering the temperature helps but also squeezes the good alternatives. The other approach cuts off the tail:

- **Top-k sampling** (used by Fan, Lewis and Dauphin, 2018, for story generation) keeps only the $k$ most probable
  tokens, sets the rest to zero and renormalises.
- **Nucleus** or **top-p sampling** (Holtzman and colleagues) keeps the smallest set of most probable tokens whose
  total probability reaches $p$, and renormalises. The kept set, the **nucleus**, adapts to the shape of the
  distribution: after *picture of* it may hold a single token, after *the* it may hold hundreds.

**Worked example.** Six tokens have logits $2, 1, 0.5, 0, -1, -2$. The softmax gives probabilities
$0.557, 0.205, 0.124, 0.075, 0.028, 0.010$ (Figure 17.2).

- *Top-k with $k = 3$:* keep 0.557, 0.205, 0.124 (total 0.886) and divide by 0.886: $0.629, 0.231, 0.140$.
- *Top-p with $p = 0.9$:* the running totals in sorted order are $0.557, 0.762, 0.887, 0.962, \dots$; the first to
  reach 0.9 is the fourth, so the nucleus is the four most probable tokens, and dividing by 0.962 gives
  $0.579, 0.213, 0.129, 0.078$.
- *Temperature 0.5:* squaring and renormalising gives $0.829, 0.112, 0.041, 0.015, 0.002, 0.000$, entropy 0.611 nats
  (it was 1.251 at $\tau = 1$, and is 1.613 at $\tau = 2$, as the theorem says it must be).

<figure class="mars-fig" markdown="0">
<svg viewBox="0 0 660 290" role="img" aria-label="Grouped bars of the probabilities of six tokens with logits 2, 1, 0.5, 0, -1, -2 at temperatures 0.5, 1 and 2. Low temperature puts 0.83 on rock; high temperature flattens the bars. A dotted line after the third token marks top-k 3, a dashed line after the fourth marks the nucleus of 0.9 at temperature 1.">
<line x1="70.0" y1="230.0" x2="640.0" y2="230.0" stroke="currentColor" stroke-width="1.2"/>
<line x1="70.0" y1="230.0" x2="70.0" y2="20.0" stroke="currentColor" stroke-width="1.2"/>
<line x1="66.0" y1="230.0" x2="70.0" y2="230.0" stroke="currentColor" stroke-width="1.2"/>
<text x="62.0" y="234.0" font-size="11" text-anchor="end" fill="currentColor">0.0</text>
<line x1="66.0" y1="190.0" x2="70.0" y2="190.0" stroke="currentColor" stroke-width="1.2"/>
<text x="62.0" y="194.0" font-size="11" text-anchor="end" fill="currentColor">0.2</text>
<line x1="66.0" y1="150.0" x2="70.0" y2="150.0" stroke="currentColor" stroke-width="1.2"/>
<text x="62.0" y="154.0" font-size="11" text-anchor="end" fill="currentColor">0.4</text>
<line x1="66.0" y1="110.0" x2="70.0" y2="110.0" stroke="currentColor" stroke-width="1.2"/>
<text x="62.0" y="114.0" font-size="11" text-anchor="end" fill="currentColor">0.6</text>
<line x1="66.0" y1="70.0" x2="70.0" y2="70.0" stroke="currentColor" stroke-width="1.2"/>
<text x="62.0" y="74.0" font-size="11" text-anchor="end" fill="currentColor">0.8</text>
<rect x="82.0" y="64.2" width="22" height="165.8" fill="#eea66f" fill-opacity="0.75" stroke="currentColor" stroke-width="0.8"/>
<rect x="106.0" y="118.6" width="22" height="111.4" fill="#9cc9ea" fill-opacity="0.75" stroke="currentColor" stroke-width="0.8"/>
<rect x="130.0" y="158.8" width="22" height="71.2" fill="#7ccf9a" fill-opacity="0.75" stroke="currentColor" stroke-width="0.8"/>
<text x="117.0" y="246.0" font-size="12" text-anchor="middle" fill="currentColor">rock</text>
<rect x="177.0" y="207.6" width="22" height="22.4" fill="#eea66f" fill-opacity="0.75" stroke="currentColor" stroke-width="0.8"/>
<rect x="201.0" y="189.0" width="22" height="41.0" fill="#9cc9ea" fill-opacity="0.75" stroke="currentColor" stroke-width="0.8"/>
<rect x="225.0" y="186.8" width="22" height="43.2" fill="#7ccf9a" fill-opacity="0.75" stroke="currentColor" stroke-width="0.8"/>
<text x="212.0" y="246.0" font-size="12" text-anchor="middle" fill="currentColor">sky</text>
<rect x="272.0" y="221.8" width="22" height="8.2" fill="#eea66f" fill-opacity="0.75" stroke="currentColor" stroke-width="0.8"/>
<rect x="296.0" y="205.2" width="22" height="24.8" fill="#9cc9ea" fill-opacity="0.75" stroke="currentColor" stroke-width="0.8"/>
<rect x="320.0" y="196.4" width="22" height="33.6" fill="#7ccf9a" fill-opacity="0.75" stroke="currentColor" stroke-width="0.8"/>
<text x="307.0" y="246.0" font-size="12" text-anchor="middle" fill="currentColor">dust</text>
<rect x="367.0" y="227.0" width="22" height="3.0" fill="#eea66f" fill-opacity="0.75" stroke="currentColor" stroke-width="0.8"/>
<rect x="391.0" y="215.0" width="22" height="15.0" fill="#9cc9ea" fill-opacity="0.75" stroke="currentColor" stroke-width="0.8"/>
<rect x="415.0" y="203.8" width="22" height="26.2" fill="#7ccf9a" fill-opacity="0.75" stroke="currentColor" stroke-width="0.8"/>
<text x="402.0" y="246.0" font-size="12" text-anchor="middle" fill="currentColor">hill</text>
<rect x="462.0" y="229.6" width="22" height="0.4" fill="#eea66f" fill-opacity="0.75" stroke="currentColor" stroke-width="0.8"/>
<rect x="486.0" y="224.4" width="22" height="5.6" fill="#9cc9ea" fill-opacity="0.75" stroke="currentColor" stroke-width="0.8"/>
<rect x="510.0" y="214.0" width="22" height="16.0" fill="#7ccf9a" fill-opacity="0.75" stroke="currentColor" stroke-width="0.8"/>
<text x="497.0" y="246.0" font-size="12" text-anchor="middle" fill="currentColor">dune</text>
<rect x="557.0" y="230.0" width="22" height="0.0" fill="#eea66f" fill-opacity="0.75" stroke="currentColor" stroke-width="0.8"/>
<rect x="581.0" y="228.0" width="22" height="2.0" fill="#9cc9ea" fill-opacity="0.75" stroke="currentColor" stroke-width="0.8"/>
<rect x="605.0" y="220.4" width="22" height="9.6" fill="#7ccf9a" fill-opacity="0.75" stroke="currentColor" stroke-width="0.8"/>
<text x="592.0" y="246.0" font-size="12" text-anchor="middle" fill="currentColor">crater</text>
<line x1="450.0" y1="40.0" x2="450.0" y2="230.0" stroke="currentColor" stroke-width="1.2" stroke-dasharray="5 4"/>
<text x="444.0" y="52.0" font-size="11" text-anchor="end" fill="currentColor">top-p 0.9 keeps these four (tau 1)</text>
<line x1="355.0" y1="90.0" x2="355.0" y2="230.0" stroke="currentColor" stroke-width="1.2" stroke-dasharray="2 3"/>
<text x="349.0" y="102.0" font-size="11" text-anchor="end" fill="currentColor">top-k 3</text>
<rect x="540" y="30" width="14" height="12" fill="#eea66f" fill-opacity="0.75" stroke="currentColor" stroke-width="0.8"/>
<text x="560.0" y="41.0" font-size="12" text-anchor="start" fill="currentColor">tau = 0.5</text>
<rect x="540" y="50" width="14" height="12" fill="#9cc9ea" fill-opacity="0.75" stroke="currentColor" stroke-width="0.8"/>
<text x="560.0" y="61.0" font-size="12" text-anchor="start" fill="currentColor">tau = 1.0</text>
<rect x="540" y="70" width="14" height="12" fill="#7ccf9a" fill-opacity="0.75" stroke="currentColor" stroke-width="0.8"/>
<text x="560.0" y="81.0" font-size="12" text-anchor="start" fill="currentColor">tau = 2.0</text>
<text x="355.0" y="268.0" font-size="12" text-anchor="middle" fill="currentColor">next token (logits 2, 1, 0.5, 0, -1, -2)</text>
<text x="22.0" y="130.0" font-size="12" text-anchor="middle" fill="currentColor" transform="rotate(-90 22 130)">probability</text>
</svg>
<figcaption>Figure 17.2. One next-token distribution under three temperatures, from the program's part 1. Temperature 0.5 sharpens it (rock 0.83), temperature 2 flattens it. Top-k with k = 3 keeps the tokens left of the dotted line; the nucleus with p = 0.9 at temperature 1 keeps the four left of the dashed line, because the first three hold only 0.887.</figcaption>
</figure>

The program implements all four rules in a few lines each and then compares them on the tiny model. To sample fast,
it first computes the model's next-token distribution for all $19^2 = 361$ two-token contexts, so that generation is
a table lookup.

```python
--8<-- "books/ai/ch17_sampling.py"
```

```
1. one next-token distribution, by hand-sized numbers
   logits         rock     sky    dust    hill    dune  crater
   tau = 0.5     0.829   0.112   0.041   0.015   0.002   0.000   entropy 0.611
   tau = 1.0     0.557   0.205   0.124   0.075   0.028   0.010   entropy 1.251
   tau = 2.0     0.356   0.216   0.168   0.131   0.080   0.048   entropy 1.613
   top-k, k=3    0.629   0.231   0.140   0.000   0.000   0.000
   top-p, 0.9    0.579   0.213   0.129   0.078   0.000   0.000
   cumulative    0.557   0.762   0.887   0.962   0.990   1.000 (sorted order)

2. the tiny model: precompute P(next | two previous words) for every pair
   greedy, 22 words: the rover drives to the crater . the rover drives to the crater . the rover drives to the crater . the

3. 2000 sampled sentences per rule (seed 7)
   rule                    rover  robot  lander  grammatical  distinct
   tau 1.0                 0.510  0.292   0.198        1.000        27
   tau 0.5                 0.676  0.217   0.106        1.000        27
   tau 3.0                 0.363  0.282   0.265        0.362      1059
   tau 3.0 + top-k 3       0.406  0.319   0.276        0.787       295
   tau 3.0 + top-p 0.9     0.394  0.334   0.273        0.690       499
   an ungrammatical sample at tau 3.0: the rover takes a picture of the at the sky .

4. exact subject probabilities at tau 0.5: rover 0.681, robot 0.223, lander 0.096
```

What the table shows:

- **At $\tau = 1$** the sampled subject frequencies (0.510, 0.292, 0.198) match the model's probabilities, all 2000
  sentences are grammatical, and they cover exactly the 27 sentences the grammar can make ($3 \times 9$).
- **At $\tau = 0.5$** the distribution sharpens toward *rover*. The exact value is $0.513^2/(0.513^2 + 0.294^2 + 0.193^2) = 0.681$
  (part 4), and the sample gives 0.676. Still everything is grammatical: tokens the model gives almost zero
  probability get even less.
- **At $\tau = 3$** the tail wakes up. Tokens with probability near zero, which the model never meant, are now
  sampled often enough that only 36 percent of sentences are grammatical, and 1059 different "sentences" appear.
- **Truncation repairs much of it.** Cutting to the top 3, or to the nucleus of 0.9, removes most of the near-zero
  tokens before they can be drawn, raising grammaticality to 0.79 and 0.69. Neither is perfect at $\tau = 3$, because
  a high temperature first flattens the distribution and then the nucleus has to hold more tokens to reach 0.9.

In real systems these knobs are set by trial: a low temperature for tasks with one right answer (code, arithmetic), a
moderate temperature with nucleus sampling for open writing. Holtzman and colleagues' argument for nucleus over top-k
is the one in the definition: a fixed $k$ is too many when the model is sure and too few when it is not.

<figure class="play" data-play="topp"><span class="ai-tag">AI-created</span><figcaption>Try it: nucleus (top-p) sampling. Move p and see which words stay in the pool. The word probabilities are made up.</figcaption></figure>

## 17.4 Instruction tuning and learning from human feedback; reward models; DPO

*Level: advanced.*

**The question:** a pretrained model imitates internet text. How do we turn it into a model that follows instructions,
and what objective is that process actually optimising?

### Step 1: supervised instruction tuning

The first step is ordinary supervised learning. Collect pairs of (instruction, good response), written by people or
converted from existing labelled datasets, and continue training the model with the same cross-entropy loss, but only
on the response tokens. Wei and colleagues ("Finetuned Language Models Are Zero-Shot Learners", 2021) fine-tuned on
many tasks rewritten as instructions and reported better zero-shot performance on held-out kinds of task. This is
called **instruction tuning** or **supervised fine-tuning (SFT)**. By the theorem of 17.1, it moves the model toward
the distribution of the demonstrations.

Demonstrations are expensive and only show one good answer. It is often easier for a person to compare two answers
than to write the best one. The second and third steps learn from comparisons.

### Step 2: a reward model from comparisons

A person sees a prompt $x$ and two responses and says which is better: $y_w$ ("winner") over $y_l$ ("loser"). The
**Bradley-Terry model** (Bradley and Terry, 1952, first used for ranking in paired comparisons) assumes each response
has a hidden score $r(x, y)$ and that

$$
P(y_w \succ y_l \mid x) = \sigma\big(r(x, y_w) - r(x, y_l)\big), \qquad \sigma(u) = \frac{1}{1 + e^{-u}}.
$$

Equal scores give a coin flip; a score difference of 1 gives a preference probability of 0.73. Only differences
matter, so $r$ is fixed only up to adding a constant per prompt. A **reward model** $r_\phi$ (usually the language
model itself with its output layer replaced by a single number) is fitted by maximum likelihood on a set of
comparisons $\mathcal{D}$:

$$
\mathcal{L}_{\text{RM}}(\phi) = -\mathbb{E}_{(x, y_w, y_l) \sim \mathcal{D}} \log \sigma\big(r_\phi(x, y_w) - r_\phi(x, y_l)\big).
$$

This is logistic regression on the difference of the two scores
([Machine learning, Chapter 6](../machine-learning/06-Classification-and-Logistic-Regression.md)). Christiano and
colleagues ("Deep Reinforcement Learning from Human Preferences", 2017) introduced this approach for reinforcement
learning: they trained simulated robots and Atari agents from people comparing short video clips, and report needing
feedback on less than one percent of the agent's interactions. Ziegler and colleagues (2019) and Stiennon and
colleagues (2020, summarisation) applied it to language models.

### Step 3: optimise the policy, but stay close

Now treat the language model as a **policy** $\pi_\theta(y \mid x)$ in the sense of [Chapter 15](15-Reinforcement-Learning.md):
the prompt is the state, the whole response is the action, and the reward model scores it. If we simply maximised
$\mathbb{E}[r_\phi]$, the policy would find responses the reward model scores highly for the wrong reasons; the reward
model was trained only on responses like those of the starting model and is unreliable far from them. So the objective
adds a penalty on moving away from the reference policy $\pi_{\text{ref}}$ (the SFT model):

$$
\max_{\pi}\; \mathbb{E}_{x}\Big[\,\mathbb{E}_{y \sim \pi(\cdot \mid x)}\, r(x, y) \;-\; \beta\, \mathrm{KL}\big(\pi(\cdot \mid x)\,\|\,\pi_{\text{ref}}(\cdot \mid x)\big)\Big].
$$

The number $\beta > 0$ sets how far the policy may move. Ouyang and colleagues ("Training language models to follow
instructions with human feedback", 2022) used exactly this three-step pipeline (SFT, reward model, then PPO, the policy
gradient method of [Section 15.5](15-Reinforcement-Learning.md), on this objective) and called the result
InstructGPT. Their abstract reports that people preferred the outputs of a 1.3-billion-parameter InstructGPT model to
those of the 175-billion-parameter GPT-3. The whole method is called **reinforcement learning from human feedback
(RLHF)**. Figure 17.3 shows it.

<figure class="mars-fig" markdown="0">
<svg viewBox="0 0 680 270" role="img" aria-label="Two pipelines. RLHF: pretrained model, then supervised fine-tuning on demonstrations, then a reward model from comparisons, then reinforcement learning with PPO and a KL penalty, giving the tuned policy. DPO: supervised fine-tuning, then a classification loss on the comparisons applied to the policy directly, giving the tuned policy.">
<defs><marker id="arr173" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="currentColor"/></marker></defs>
<rect x="10.0" y="40.0" width="125.0" height="54.0" rx="5" fill="#9cc9ea" fill-opacity="0.5" stroke="currentColor" stroke-width="1.2"/>
<text x="72.5" y="63.0" font-size="12" text-anchor="middle" fill="currentColor">pretrained</text>
<text x="72.5" y="80.0" font-size="12" text-anchor="middle" fill="currentColor">model</text>
<rect x="150.0" y="40.0" width="125.0" height="54.0" rx="5" fill="#7ccf9a" fill-opacity="0.5" stroke="currentColor" stroke-width="1.2"/>
<text x="212.5" y="63.0" font-size="12" text-anchor="middle" fill="currentColor">1. SFT on</text>
<text x="212.5" y="80.0" font-size="12" text-anchor="middle" fill="currentColor">demonstrations</text>
<rect x="300.0" y="40.0" width="125.0" height="54.0" rx="5" fill="#eea66f" fill-opacity="0.5" stroke="currentColor" stroke-width="1.2"/>
<text x="362.5" y="63.0" font-size="12" text-anchor="middle" fill="currentColor">2. reward model</text>
<text x="362.5" y="80.0" font-size="12" text-anchor="middle" fill="currentColor">from comparisons</text>
<rect x="460.0" y="40.0" width="125.0" height="54.0" rx="5" fill="#eea66f" fill-opacity="0.5" stroke="currentColor" stroke-width="1.2"/>
<text x="522.5" y="63.0" font-size="12" text-anchor="middle" fill="currentColor">3. RL (PPO)</text>
<text x="522.5" y="80.0" font-size="12" text-anchor="middle" fill="currentColor">with KL penalty</text>
<line x1="135.0" y1="67.0" x2="148.0" y2="67.0" stroke="currentColor" stroke-width="1.2" marker-end="url(#arr173)"/>
<line x1="275.0" y1="67.0" x2="298.0" y2="67.0" stroke="currentColor" stroke-width="1.2" marker-end="url(#arr173)"/>
<line x1="425.0" y1="67.0" x2="458.0" y2="67.0" stroke="currentColor" stroke-width="1.2" marker-end="url(#arr173)"/>
<line x1="585.0" y1="67.0" x2="606.0" y2="67.0" stroke="currentColor" stroke-width="1.2" marker-end="url(#arr173)"/>
<rect x="608.0" y="46.0" width="64.0" height="42.0" rx="5" fill="#7ccf9a" fill-opacity="0.3" stroke="currentColor" stroke-width="1.2"/>
<text x="640.0" y="64.0" font-size="12" text-anchor="middle" fill="currentColor">tuned</text>
<text x="640.0" y="80.0" font-size="12" text-anchor="middle" fill="currentColor">policy</text>
<text x="340.0" y="24.0" font-size="13" text-anchor="middle" fill="currentColor">RLHF (Christiano et al. 2017; Ouyang et al. 2022)</text>
<text x="340.0" y="150.0" font-size="13" text-anchor="middle" fill="currentColor">DPO (Rafailov et al. 2023)</text>
<rect x="150.0" y="168.0" width="125.0" height="54.0" rx="5" fill="#7ccf9a" fill-opacity="0.5" stroke="currentColor" stroke-width="1.2"/>
<text x="212.5" y="191.0" font-size="12" text-anchor="middle" fill="currentColor">1. SFT on</text>
<text x="212.5" y="208.0" font-size="12" text-anchor="middle" fill="currentColor">demonstrations</text>
<rect x="330.0" y="168.0" width="240.0" height="54.0" rx="5" fill="#eea66f" fill-opacity="0.5" stroke="currentColor" stroke-width="1.2"/>
<text x="450.0" y="191.0" font-size="12" text-anchor="middle" fill="currentColor">2. classification loss on the</text>
<text x="450.0" y="208.0" font-size="12" text-anchor="middle" fill="currentColor">comparisons, applied to the policy</text>
<line x1="275.0" y1="195.0" x2="328.0" y2="195.0" stroke="currentColor" stroke-width="1.2" marker-end="url(#arr173)"/>
<line x1="570.0" y1="195.0" x2="606.0" y2="195.0" stroke="currentColor" stroke-width="1.2" marker-end="url(#arr173)"/>
<rect x="608.0" y="174.0" width="64.0" height="42.0" rx="5" fill="#7ccf9a" fill-opacity="0.3" stroke="currentColor" stroke-width="1.2"/>
<text x="640.0" y="192.0" font-size="12" text-anchor="middle" fill="currentColor">tuned</text>
<text x="640.0" y="208.0" font-size="12" text-anchor="middle" fill="currentColor">policy</text>
<text x="340.0" y="250.0" font-size="11" text-anchor="middle" fill="currentColor">same human comparisons, same optimum (Section 17.4); no separate reward model and no sampling loop</text>
</svg>
<figcaption>Figure 17.3. Learning from human feedback. Top: the three-step RLHF pipeline of InstructGPT. Bottom: DPO replaces the reward model and the reinforcement-learning loop by one loss on the policy, with the same optimum when the model families match (proved in this section).</figcaption>
</figure>

**Theorem (the optimal policy is an exponential tilt).** For each prompt $x$, the objective is maximised by

$$
\pi^*(y \mid x) = \frac{1}{Z(x)}\,\pi_{\text{ref}}(y \mid x)\,\exp\!\big(r(x, y)/\beta\big), \qquad Z(x) = \sum_{y} \pi_{\text{ref}}(y \mid x)\,e^{r(x, y)/\beta},
$$

and this maximiser is unique.

**Proof.** Fix $x$ and drop it from the notation. For any policy $\pi$,

$$
\begin{aligned}
\mathbb{E}_\pi[r] - \beta\,\mathrm{KL}(\pi\,\|\,\pi_{\text{ref}})
&= \sum_y \pi(y)\Big[r(y) - \beta\ln\frac{\pi(y)}{\pi_{\text{ref}}(y)}\Big]
= -\beta \sum_y \pi(y)\ln\frac{\pi(y)}{\pi_{\text{ref}}(y)\,e^{r(y)/\beta}} \\
&= -\beta \sum_y \pi(y)\ln\frac{\pi(y)}{Z\,\pi^*(y)}
= \beta \ln Z - \beta\,\mathrm{KL}(\pi\,\|\,\pi^*).
\end{aligned}
$$

The first term does not depend on $\pi$, and by Gibbs' inequality (17.1) the KL term is at least 0 with equality only
at $\pi = \pi^*$. $\square$

So RLHF has a definite target: the reference model's distribution, re-weighted by $e^{r/\beta}$. Small $\beta$ means a
sharp tilt toward high reward; large $\beta$ keeps the policy near the reference. PPO, which samples responses and
follows a gradient estimate, is a way of approximating this target when $y$ ranges over all possible texts and $Z$
cannot be computed.

### DPO: skip the reward model

Rafailov and colleagues ("Direct Preference Optimization: Your Language Model is Secretly a Reward Model", 2023)
turned the theorem around. Take logarithms and solve for the reward:

$$
r(x, y) = \beta \ln\frac{\pi^*(y \mid x)}{\pi_{\text{ref}}(y \mid x)} + \beta \ln Z(x).
$$

Every reward function corresponds to its optimal policy this way. Put this into the Bradley-Terry probability. The
term $\beta\ln Z(x)$ is the same for both responses to the same prompt and cancels in the difference:

$$
P(y_w \succ y_l \mid x) = \sigma\Big(\beta\ln\frac{\pi^*(y_w \mid x)}{\pi_{\text{ref}}(y_w \mid x)} - \beta\ln\frac{\pi^*(y_l \mid x)}{\pi_{\text{ref}}(y_l \mid x)}\Big).
$$

So the preference likelihood can be written directly in terms of the policy. Fitting the policy by maximum likelihood
on the comparisons gives the **DPO loss**:

$$
\mathcal{L}_{\text{DPO}}(\theta) = -\mathbb{E}_{(x, y_w, y_l)}\log\sigma\Big(\beta\ln\frac{\pi_\theta(y_w \mid x)}{\pi_{\text{ref}}(y_w \mid x)} - \beta\ln\frac{\pi_\theta(y_l \mid x)}{\pi_{\text{ref}}(y_l \mid x)}\Big).
$$

It is a classification loss on the comparisons; there is no reward model to train, no sampling from the policy during
training, and no reinforcement learning loop. The quantity $\beta\ln(\pi_\theta/\pi_{\text{ref}})$ plays the role of the
reward; Rafailov and colleagues call it the **implicit reward**. The derivation shows: if the policy family can
represent $\pi_{\text{ref}}\,e^{r/\beta}/Z$ for the reward-model family, then maximising the DPO likelihood over policies
is the same problem as maximising the reward-model likelihood over rewards and then tilting, so both routes reach the
same policy. In practice the families, the data and the optimisers differ, and which route works better is an
empirical question that published comparisons have answered both ways.

### The toy, from scratch

The program builds a problem where everything can be computed exactly. There are 40 prompts with 8 candidate
responses each. Each response has a true **quality** (what we want) and a **length**; padding is slightly bad, so
length is weakly negatively correlated with quality. Simulated labellers compare random pairs by Bradley-Terry with a
score of quality plus length: they reward long answers as much as good ones. The reference policy is a random
distribution over the 8 responses.

```python
--8<-- "books/ai/ch17_preferences.py"
```

```
1. reward model: 1738 training comparisons, 858 held out
   fitted reward r(y) = 0.976 * quality + 1.033 * length   (labellers used 1 and 1)
   held-out agreement with labellers: reward model 0.766, true quality 0.640

2. the KL-regularised optimum for decreasing beta (averages over the 40 prompts)
     beta  KL to ref  reward model  true quality
      100      0.000         0.026        -0.041
        3      0.063         0.400         0.137
        1      0.416         0.956         0.410
      0.3      1.334         1.481         0.693
      0.1      1.855         1.582         0.753
     0.01      2.124         1.597         0.706
   best possible true quality (always pick the best response): 1.407

3. DPO with beta = 1: policy log pi = log pi_ref + theta . phi - log Z, fitted to the comparisons
   step   0: DPO loss 0.6931
   step 499: DPO loss 0.5014
   beta * theta = (0.976, 1.033)   reward model w = (0.976, 1.033)
   largest gap between the DPO policy and the reward-model optimum: 2.78e-16
```

**Part 1.** The reward model recovers the labellers' weights, about 1 and 1, from 1738 noisy comparisons. It agrees
with the labellers on 76.6 percent of held-out comparisons; perfect knowledge of the true quality agrees on only 64
percent, because the labellers were not judging quality alone. The reward model is faithful to the labels, and the
labels are not what we wanted.

**Part 2** computes the exact optimum of the theorem for decreasing $\beta$ (Figure 17.4). As the policy moves further
from the reference (KL grows), the reward-model score always rises: the policy is doing its job. True quality rises
too, peaks at 0.753 near $\beta = 0.1$, and then falls to 0.706 at $\beta = 0.01$, where the policy has learned to
pick long answers. This is a small instance of **reward model over-optimisation**: Gao, Schulman and Hilton ("Scaling
Laws for Reward Model Overoptimization", 2022) measured, with a large "gold" reward model playing the part of people,
that the gold score first rises and then falls as a policy is optimised against a smaller proxy reward model. It is an
example of Goodhart's law (a measure that becomes a target stops being a good measure) and of the specification
gaming of [Section 15.7](15-Reinforcement-Learning.md); the KL penalty is the brake. In this toy, the length bias of
the labellers caps true quality at 0.75 out of a possible 1.41, whatever $\beta$ is: no optimiser can recover what
the comparisons do not contain.

**Part 3** runs DPO. The policy family is $\pi_\theta(y \mid x) \propto \pi_{\text{ref}}(y \mid x)\,e^{\theta \cdot \phi(y)}$,
where $\phi(y)$ is the pair (quality, length). Its implicit reward is $\beta\,\theta\cdot\phi(y)$ minus a
per-prompt constant, so DPO is exactly the reward model's logistic regression with $w = \beta\theta$. The program
confirms it: after training, $\beta\theta$ equals $w$ to three decimals, and the DPO policy equals the exact RLHF
optimum for $\beta = 1$ to $10^{-16}$, rounding error. With no reward model and no sampling, DPO reached the same
policy, as the derivation said it would, including the same length bias.

<figure class="mars-fig" markdown="0">
<svg viewBox="0 0 600 300" role="img" aria-label="Line plot against the KL divergence from the reference policy. The reward-model score rises steadily from 0.03 to 1.60. True quality rises from -0.04 to a peak of 0.753 at KL 1.86 and then falls to 0.706 at KL 2.12.">
<line x1="70.0" y1="240.0" x2="550.0" y2="240.0" stroke="currentColor" stroke-width="1.2"/>
<line x1="70.0" y1="240.0" x2="70.0" y2="40.0" stroke="currentColor" stroke-width="1.2"/>
<line x1="70.0" y1="240.0" x2="70.0" y2="244.0" stroke="currentColor" stroke-width="1.2"/>
<text x="70.0" y="258.0" font-size="11" text-anchor="middle" fill="currentColor">0</text>
<line x1="176.7" y1="240.0" x2="176.7" y2="244.0" stroke="currentColor" stroke-width="1.2"/>
<text x="176.7" y="258.0" font-size="11" text-anchor="middle" fill="currentColor">0.5</text>
<line x1="283.3" y1="240.0" x2="283.3" y2="244.0" stroke="currentColor" stroke-width="1.2"/>
<text x="283.3" y="258.0" font-size="11" text-anchor="middle" fill="currentColor">1</text>
<line x1="390.0" y1="240.0" x2="390.0" y2="244.0" stroke="currentColor" stroke-width="1.2"/>
<text x="390.0" y="258.0" font-size="11" text-anchor="middle" fill="currentColor">1.5</text>
<line x1="496.7" y1="240.0" x2="496.7" y2="244.0" stroke="currentColor" stroke-width="1.2"/>
<text x="496.7" y="258.0" font-size="11" text-anchor="middle" fill="currentColor">2</text>
<line x1="66.0" y1="220.0" x2="70.0" y2="220.0" stroke="currentColor" stroke-width="1.2"/>
<text x="62.0" y="224.0" font-size="11" text-anchor="end" fill="currentColor">0</text>
<line x1="66.0" y1="170.0" x2="70.0" y2="170.0" stroke="currentColor" stroke-width="1.2"/>
<text x="62.0" y="174.0" font-size="11" text-anchor="end" fill="currentColor">0.5</text>
<line x1="66.0" y1="120.0" x2="70.0" y2="120.0" stroke="currentColor" stroke-width="1.2"/>
<text x="62.0" y="124.0" font-size="11" text-anchor="end" fill="currentColor">1</text>
<line x1="66.0" y1="70.0" x2="70.0" y2="70.0" stroke="currentColor" stroke-width="1.2"/>
<text x="62.0" y="74.0" font-size="11" text-anchor="end" fill="currentColor">1.5</text>
<line x1="70.0" y1="220.0" x2="550.0" y2="220.0" stroke="currentColor" stroke-width="1.2" stroke-dasharray="2 3" stroke-opacity="0.5"/>
<polyline points="70.0,217.4 83.4,180.0 158.7,124.4 354.6,71.9 465.7,61.8 523.1,60.3" fill="none" stroke="#eea66f" stroke-width="2.5"/>
<polyline points="70.0,224.1 83.4,206.3 158.7,179.0 354.6,150.7 465.7,144.7 523.1,149.4" fill="none" stroke="#9cc9ea" stroke-width="2.5"/>
<circle cx="70.0" cy="217.4" r="3.5" fill="#eea66f" stroke="currentColor"/>
<circle cx="83.4" cy="180.0" r="3.5" fill="#eea66f" stroke="currentColor"/>
<circle cx="158.7" cy="124.4" r="3.5" fill="#eea66f" stroke="currentColor"/>
<circle cx="354.6" cy="71.9" r="3.5" fill="#eea66f" stroke="currentColor"/>
<circle cx="465.7" cy="61.8" r="3.5" fill="#eea66f" stroke="currentColor"/>
<circle cx="523.1" cy="60.3" r="3.5" fill="#eea66f" stroke="currentColor"/>
<circle cx="70.0" cy="224.1" r="3.5" fill="#9cc9ea" stroke="currentColor"/>
<circle cx="83.4" cy="206.3" r="3.5" fill="#9cc9ea" stroke="currentColor"/>
<circle cx="158.7" cy="179.0" r="3.5" fill="#9cc9ea" stroke="currentColor"/>
<circle cx="354.6" cy="150.7" r="3.5" fill="#9cc9ea" stroke="currentColor"/>
<circle cx="465.7" cy="144.7" r="3.5" fill="#9cc9ea" stroke="currentColor"/>
<circle cx="523.1" cy="149.4" r="3.5" fill="#9cc9ea" stroke="currentColor"/>
<text x="519.1" y="48.3" font-size="12" text-anchor="end" fill="currentColor">reward-model score</text>
<text x="519.1" y="171.4" font-size="12" text-anchor="end" fill="currentColor">true quality</text>
<text x="465.7" y="134.7" font-size="11" text-anchor="middle" fill="currentColor">peak 0.753</text>
<text x="166.7" y="116.4" font-size="11" text-anchor="start" fill="currentColor">beta 1</text>
<text x="348.6" y="61.9" font-size="11" text-anchor="end" fill="currentColor">beta 0.3</text>
<text x="310.0" y="280.0" font-size="12" text-anchor="middle" fill="currentColor">KL(pi || pi_ref), nats: how far the policy moved</text>
<text x="20.0" y="140.0" font-size="12" text-anchor="middle" fill="currentColor" transform="rotate(-90 20 140)">average over 40 prompts</text>
</svg>
<figcaption>Figure 17.4. Over-optimisation in the toy, from part 2 of the output. Each point is the exact KL-regularised optimum for one beta (100, 3, 1, 0.3, 0.1, 0.01 from left to right). The proxy reward keeps rising as the policy moves away from the reference; true quality peaks and then falls, because the reward model has learned the labellers' taste for length.</figcaption>
</figure>

## 17.5 Retrieval-augmented generation (Lewis et al. 2020); tools and agents (ReAct, Yao et al. 2022)

**The question:** a model's knowledge is frozen in its parameters at training time and it cannot calculate reliably.
Can we give it a library and a calculator?

### Retrieval-augmented generation

**Retrieval-augmented generation (RAG)** adds a search step before generation: find the passages most relevant to
the question in a document collection, put them into the prompt, and let the model answer from them. Lewis and
colleagues ("Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks", 2020) trained a neural retriever (a
dense passage retriever, which embeds questions and passages as vectors and compares them by dot product; Karpukhin
and colleagues, 2020) together with a sequence-to-sequence generator, treating the retrieved passage as a hidden
variable and summing over the top few. Guu and colleagues' REALM (2020) did similar for pretraining. Most deployed
systems today keep the idea and simplify the training: an off-the-shelf retriever and a pretrained model that is
prompted with the retrieved text.

Retrieval brings three things. Answers can use documents newer than the model or private to the user. Answers can
**cite** the passage they came from, which makes them checkable. And the model need not have memorised the fact. What
it does not bring is a guarantee: the model may ignore the passage, mix it with what it remembers, or be misled by an
irrelevant one, and Liu and colleagues ("Lost in the Middle", 2023) measured that models used information at the start
and end of a long context better than in the middle.

**Retrieval from scratch.** The program's retriever uses **TF-IDF** vectors, the classic method of information
retrieval. Each word $w$ in a document gets weight $\text{tf}(w) \cdot \text{idf}(w)$, where tf is its count in the
document and $\text{idf}(w) = \ln(N/\text{df}(w)) + 1$, with $N$ the number of documents and df the number containing
$w$; words common to every document are worth little. Query and document are compared by the **cosine** of the angle
between their vectors, $\frac{u \cdot v}{\lVert u\rVert\,\lVert v\rVert}$. BM25 (Robertson and Zaragoza, 2009) refines
the weights; dense retrievers replace the word counts by learned embeddings and use approximate nearest-neighbour
search ([Machine learning, Chapter 9](../machine-learning/09-Nearest-Neighbours-and-Kernels.md)).

Hand check for the question *In what year was the A\* search algorithm published?* Common words (*in, what, year,
was, the, published*) are dropped as stop words, leaving *a\*, search, algorithm*. In the 6 documents, *a\** and
*search* appear once (idf $= \ln 6 + 1 = 2.792$) and *algorithm* in 3 (idf $= \ln 2 + 1 = 1.693$). The A\* document
has those three words plus four more of weight 2.792 (*hart, nilsson, raphael, 1968*). The dot product is
$2.792^2 + 2.792^2 + 1.693^2 = 18.455$, the norms are $\sqrt{18.455} = 4.296$ and
$\sqrt{6 \times 2.792^2 + 1.693^2} = 7.045$, and the cosine is $18.455/(4.296 \times 7.045) = 0.610$, the program's
top score.

### Tools and the ReAct loop

A model can also be given **tools**: functions it may call, such as a search engine, a calculator or a code
interpreter. The model cannot call anything itself; it can only write text. So the system around it defines a format,
and a loop (the **harness**) reads the model's output, recognises a tool call, runs the tool and pastes the result
back into the context. Yao and colleagues ("ReAct: Synergizing Reasoning and Acting in Language Models", 2022) prompted
models to interleave three kinds of line: **Thought** (free text reasoning about what to do), **Action** (a tool call
in a fixed format, such as `search[...]`) and **Observation** (the tool's result, written by the harness), and
reported gains on question answering with a Wikipedia search tool and on interactive text environments. Schick and
colleagues' Toolformer (2023) trained a model to insert tool calls itself. Such a loop of model, tools and memory is
what is usually called an **agent**, in the sense of [Chapter 2](02-Intelligent-Agents.md): percepts are the
observations, actions are the tool calls, and the model is the agent program (Figure 17.5).

<figure class="mars-fig" markdown="0">
<svg viewBox="0 0 640 250" role="img" aria-label="A cycle of four boxes: the language model reads the transcript and writes a Thought and an Action such as search for A* algorithm; the loop parses it and runs the tool; the tool's result is appended to the transcript as an Observation; the model reads it again, until a Final Answer or the step limit.">
<defs><marker id="arr175" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="currentColor"/></marker></defs>
<rect x="20.0" y="90.0" width="150.0" height="60.0" rx="5" fill="#7ccf9a" fill-opacity="0.5" stroke="currentColor" stroke-width="1.2"/>
<text x="95.0" y="115.0" font-size="13" text-anchor="middle" fill="currentColor">language model</text>
<text x="95.0" y="133.0" font-size="11" text-anchor="middle" fill="currentColor">reads the transcript</text>
<rect x="245.0" y="30.0" width="170.0" height="50.0" rx="5" fill="#eea66f" fill-opacity="0.4" stroke="currentColor" stroke-width="1.2"/>
<text x="330.0" y="51.0" font-size="13" text-anchor="middle" fill="currentColor">Thought + Action</text>
<text x="330.0" y="68.0" font-size="11" text-anchor="middle" fill="currentColor">search[A* algorithm]</text>
<rect x="470.0" y="90.0" width="150.0" height="60.0" rx="5" fill="#9cc9ea" fill-opacity="0.5" stroke="currentColor" stroke-width="1.2"/>
<text x="545.0" y="115.0" font-size="13" text-anchor="middle" fill="currentColor">tool runs</text>
<text x="545.0" y="133.0" font-size="11" text-anchor="middle" fill="currentColor">(search, calculate)</text>
<rect x="245.0" y="160.0" width="170.0" height="50.0" rx="5" fill="#9cc9ea" fill-opacity="0.3" stroke="currentColor" stroke-width="1.2"/>
<text x="330.0" y="181.0" font-size="13" text-anchor="middle" fill="currentColor">Observation</text>
<text x="330.0" y="198.0" font-size="11" text-anchor="middle" fill="currentColor">appended to transcript</text>
<line x1="150.0" y1="90.0" x2="243.0" y2="62.0" stroke="currentColor" stroke-width="1.2" marker-end="url(#arr175)"/>
<line x1="415.0" y1="62.0" x2="500.0" y2="88.0" stroke="currentColor" stroke-width="1.2" marker-end="url(#arr175)"/>
<line x1="520.0" y1="150.0" x2="417.0" y2="185.0" stroke="currentColor" stroke-width="1.2" marker-end="url(#arr175)"/>
<line x1="243.0" y1="185.0" x2="130.0" y2="150.0" stroke="currentColor" stroke-width="1.2" marker-end="url(#arr175)"/>
<text x="95.0" y="182.0" font-size="11" text-anchor="middle" fill="currentColor">until Final Answer</text>
<text x="95.0" y="197.0" font-size="11" text-anchor="middle" fill="currentColor">or step limit</text>
<text x="475.0" y="60.0" font-size="11" text-anchor="start" fill="currentColor">parsed by the loop</text>
</svg>
<figcaption>Figure 17.5. The ReAct loop. Only the green box is a language model; parsing, running tools, appending observations and stopping are ordinary code in the harness.</figcaption>
</figure>

The program builds both pieces. Its "language model" is a **fake**: a few rules that write the kind of text a real
model would, so that you can see that everything outside the model is ordinary code. Swap the fake for a real model
and the loop is unchanged.

```python
--8<-- "books/ai/ch17_rag_agent.py"
```

```
1. retrieval-augmented generation
   retrieved (cosine 0.61): Hart, Nilsson and Raphael published the A* search algorithm in 1968.
   retrieved (cosine 0.114): Robinson published the unification algorithm for resolution in 1965.
   with retrieval   : 1968 (from: Hart, Nilsson and Raphael published the A* se...)
   without retrieval: 1957 (no source)

2. a ReAct loop with two tools (search, calculate)
   Question: How many years after Dijkstra's algorithm was A* published?
   Thought: I need the year of Dijkstra's algorithm.
   Action: search[Dijkstra shortest path algorithm]
   Observation: Dijkstra published his shortest path algorithm in 1959.
   Thought: Now I need the year of A*.
   Action: search[A* search algorithm]
   Observation: Hart, Nilsson and Raphael published the A* search algorithm in 1968.
   Thought: Subtract the years.
   Action: calculate[1968 - 1959]
   Observation: 9
   Thought: I have the difference.
   Final Answer: 9 years

3. the calculator refuses non-arithmetic: error: not an arithmetic expression
```

Part 1 shows the point of retrieval in miniature: with the passage the fake model answers 1968 and names its source;
without it, it produces a fluent, confident and wrong year. That second line is deliberately what a bare model can do
(17.7). Part 2 is a two-hop question: no single document holds the answer, so the agent searches twice and then
subtracts with a tool rather than doing arithmetic in text.

The harness carries the engineering that makes agents work or fail, and it is worth stating the technical lessons
plainly:

- **Parse strictly and fail visibly.** An unrecognised action produces an error observation, which the model can
  react to, rather than a crash or a silent skip.
- **Limit the loop.** A step limit guarantees termination; a model that never writes "Final Answer" would otherwise
  run forever.
- **Restrict tools.** The calculator accepts only digits and operators (part 3). A tool that executes arbitrary text
  from the model executes arbitrary text from anything the model has read.
- **Treat retrieved text as data.** A retrieved page can contain text that looks like instructions; the model sees it
  in the same context as the user's request. Greshake and colleagues (2023) demonstrated such **indirect prompt
  injection** against applications built on language models. No complete defence is known; separating and marking
  untrusted text, restricting what tools can do and asking a person before irreversible actions reduce the damage.

## 17.6 Chain-of-thought (Wei et al. 2022); evaluation and its pitfalls (contamination, benchmarks)

*Level: advanced.*

**The question:** can a model answer better if it writes out its reasoning first, and how would we know whether a
model is really better?

### Chain-of-thought

Wei and colleagues ("Chain-of-Thought Prompting Elicits Reasoning in Large Language Models", 2022) put worked solutions
into few-shot prompts: instead of *Q: ... A: 11*, the examples read *Q: ... A: Roger started with 5 balls. 2 cans of 3
balls each is 6 balls. 5 + 6 = 11. The answer is 11.* Models then wrote similar steps before answering new questions,
and on arithmetic word problems such as GSM8K (Cobbe and colleagues, 2021) the paper reports large gains, which
appeared mainly for its largest models. Kojima and colleagues (2022) found that simply adding "Let's think step by step"
had a similar effect without examples. Nye and colleagues (2021) had earlier trained models to write intermediate
results on a "scratchpad" for tasks such as long addition.

There is a clean reason why writing steps can help, independent of any claim about "thinking". A transformer with
$L$ layers performs a fixed amount of sequential computation per generated token: information can pass through at
most $L$ layers before the token is chosen. A problem that needs more sequential steps than that (multiply two long
numbers, follow a chain of 20 facts) cannot be done in one token by a fixed-depth model, but it can be done across
many tokens, because each generated token is fed back as input and becomes working memory. Merrill and Sabharwal
("The Expressive Power of Transformers with Chain of Thought", 2024) made this precise for idealised transformers:
allowing a number of intermediate steps that grows with the input strictly increases the class of problems they can
solve, under standard complexity assumptions. Whether the written steps are the reason a real model's answer comes
out as it does, rather than a plausible account written alongside it, is a separate empirical question; experiments
that edit or cut the written chain and check whether the answer changes are one way to test it.

### Self-consistency

Sampling (17.3) gives a different chain each time. Wang and colleagues ("Self-Consistency Improves Chain of Thought
Reasoning in Language Models", 2022) sampled several chains and took the most common final answer, a **majority
vote**. When does voting help? Suppose each chain gets the right answer with probability 0.4 and spreads its errors
over four wrong answers with 0.15 each. One chain is right 40 percent of the time; but the right answer is the single
most likely one, and by the law of large numbers its share of a large sample approaches 0.4 while each wrong answer's
approaches 0.15, so the vote is right with probability tending to 1. If instead one wrong answer has probability 0.45,
the vote converges to that wrong answer. **Voting amplifies the plurality, right or wrong.** The program computes these
probabilities exactly by summing the multinomial distribution over all possible vote counts.

### Benchmarks and three things that go wrong

A **benchmark** is a fixed set of questions with known answers: MMLU (Hendrycks and colleagues, 2021) has
multiple-choice questions in 57 subjects; GSM8K has grade-school word problems; HumanEval (Chen and colleagues, 2021)
has 164 programming problems checked by unit tests. The score is the fraction answered correctly. Three pitfalls are
technical and measurable.

**1. Sampling many times: pass@k.** For code, a model may generate several programs and succeed if any passes the
tests. Chen and colleagues define **pass@k** as the probability that at least one of $k$ samples is correct. The naive
way to estimate it from $n \ge k$ samples of which $c$ are correct, $1 - (1 - c/n)^k$, is biased. Their estimator is

$$
\widehat{\text{pass@}k} = 1 - \frac{\binom{n-c}{k}}{\binom{n}{k}}.
$$

**Theorem.** If each of the $n$ samples is independently correct with probability $p$, this estimator has expectation
exactly $1 - (1 - p)^k$, the true pass@k.

**Proof.** $\binom{n-c}{k}/\binom{n}{k}$ is the probability that a uniformly random $k$-subset of the $n$ samples
contains no correct one (choose all $k$ from the $n - c$ incorrect ones). So its expectation, over the random samples,
is the probability that a random $k$-subset of $n$ independent samples is all incorrect. But a random $k$-subset of
independent, identically distributed samples is itself $k$ independent samples, all incorrect with probability
$(1 - p)^k$. $\square$

The naive estimator is too low: $f(u) = (1 - u)^k$ is convex, so by Jensen's inequality
$\mathbb{E}[(1 - c/n)^k] \ge (1 - p)^k$.

**2. Contamination.** If benchmark questions appear in the training data, a high score may be memory rather than
skill. Pretraining sets are scraped from the web, and benchmarks are published on the web. The GPT-3 paper checked for
overlap by looking for 13-token sequences (13-grams) shared between benchmark items and training data, and reported
results on cleaned subsets. Overlap tests catch verbatim copies but not paraphrases or translations, as part 3 of the
program shows; and if the training data are not published, outsiders cannot run the test at all.

**3. Noise.** A benchmark is a sample of questions. With $n$ questions and true accuracy $a$, the observed accuracy has
standard error $\sqrt{a(1-a)/n}$. On 200 questions at 72 percent that is 3.2 points, so the 95 percent interval runs
from 65.8 to 78.2 percent. Two equally good models differ by 3 points or more on separate 200-question samples about
half the time. Gaps of a point or two on small benchmarks, often reported as rankings, are frequently noise. Prompt
wording adds more variance: Zhao and colleagues ("Calibrate Before Use", 2021) reported that few-shot accuracy changed
widely with the choice and order of the examples in the prompt. Using another language model as the judge, common for
open-ended answers, brings its own biases; Zheng and colleagues (2023) measured position bias (favouring the first
answer shown) and verbosity bias in such judges.

```python
--8<-- "books/ai/ch17_eval.py"
```

```
1. self-consistency: P(majority answer is right) after m sampled chains
   right 0.4, four wrong answers 0.15 each
      m=1: 0.400  m=5: 0.549  m=15: 0.780  m=41: 0.961
   right 0.4, one common wrong answer 0.45
      m=1: 0.400  m=5: 0.434  m=15: 0.416  m=41: 0.364

2. pass@k with n = 20 samples per problem, true per-sample success p = 0.1, k = 10
   true pass@10 = 1 - 0.9^10 = 0.6513
   expected value of the unbiased estimator 0.6513, of the naive 1-(1-c/n)^k 0.5681
   one problem with c = 3 correct out of 20: pass@1 0.1500, pass@5 0.6009, pass@10 0.8947

3. contamination check: 8-gram overlap between benchmark items and a training text
   item 1: 15 of 15 8-grams seen in training -> CONTAMINATED
   item 2: 12 of 12 8-grams seen in training -> CONTAMINATED
   item 3:  0 of  9 8-grams seen in training -> clean
   item 4:  0 of  9 8-grams seen in training -> clean

4. noise: two models, 200 questions each
   accuracy 0.72: standard error 0.0317, 95% interval 0.658 to 0.782
   if both are truly 0.735, P(observed gap >= 0.03) = 0.534
```

Part 1 confirms both cases: with errors spread out, 41 votes are right 96 percent of the time; with one common error,
voting makes things worse as $m$ grows. Part 2 computes the exact expectations by summing over the binomial
distribution of $c$: the unbiased estimator averages exactly 0.6513, the naive one 0.5681. Part 3 uses 8-grams
because the toy items are short: items 1 and 2 are copied into the training text and are caught, item 3 is a
paraphrase of item 2 and passes as clean. Part 4 is the noise calculation.

## 17.7 Limits: hallucination, reasoning failures, cost; what is known vs claimed

**The question:** what do these systems reliably fail at, why, and how much of what is said about them is
established?

### Hallucination

A **hallucination** is generated text that is fluent and confident but not supported by the input or by fact. In
summarisation, Maynez and colleagues (2020) found that many model summaries contained content not in the source
document. The objective explains why this is the default. By 17.1, a pretrained model is trained to produce plausible
continuations; a question that has a factual answer in some documents and none in the model's memory still has a most
plausible continuation, and it has the form of an answer. Nothing in the next-token loss rewards saying "I don't
know" unless such text was the likely continuation.

There is also a theoretical argument that some of this cannot be trained away while keeping the model calibrated.
Kalai and Vempala ("Calibrated Language Models Must Hallucinate", 2024) prove, under stated assumptions, a lower bound
on the hallucination rate of a calibrated model for arbitrary facts (such as which paper a particular person wrote)
in terms of the fraction of such facts that appear exactly once in the training data, an idea related to Good-Turing
estimation of the probability of unseen events. Facts seen once cannot be told apart from plausible facts never seen.
Retrieval (17.5) and training the model to abstain reduce hallucination; neither removes it.

Larger is not automatically more truthful. Lin, Hilton and Evans (TruthfulQA, 2022) wrote questions where a common
misconception is the likely continuation, and reported that the largest models they tested were generally the least
truthful: better imitation of human text included better imitation of human errors.

### Reasoning failures

Documented failures share a pattern: success on the forms seen in training, failure on systematic variations.

- **The reversal curse.** Berglund and colleagues (2023) fine-tuned models on statements of the form "A is B" and found
  that they did not then answer questions of the form "who is B?" with A.
- **Compositional depth.** Dziri and colleagues ("Faith and Fate", 2023) studied multi-digit multiplication and other
  multi-step tasks and found accuracy falling sharply as the number of steps grew, with errors consistent with
  matching sub-patterns seen in training rather than executing the algorithm.
- **Fragility to irrelevant changes.** Accuracy often drops when names, numbers or the order of statements in a
  benchmark question are changed without changing its logic, which is one of the reasons contamination (17.6) is
  taken seriously.

None of these shows that language models "cannot reason", which is not a precise claim; they show that the errors are
not like a human expert's, that a correct answer on one form of a problem does not imply a correct answer on an
equivalent form, and that checking an answer with a tool (a calculator, a test suite, a proof checker) is more reliable
than trusting it.

### Cost

From 17.2, generating one token costs about $2N$ FLOPs, so a 175-billion-parameter model spends 350 billion FLOPs per
token, every token. Memory is often the tighter limit. To avoid recomputing the keys and values of attention for the
whole context at every step, implementations keep them in a **KV cache**: for each token, each layer stores a key and
a value vector of width $d$. For GPT-3's shape (96 layers, $d = 12288$) at 2 bytes per number, that is
$2 \times 96 \times 12288 \times 2 = 4{,}718{,}592$ bytes, about 4.7 MB per token, or about 9.7 GB for a full context of
2048 tokens, on top of 350 GB for the 175 billion parameters at 2 bytes each. Chain-of-thought and self-consistency
multiply the number of generated tokens, so better accuracy is bought with compute at answer time. These costs, and
the methods that cut them (smaller models trained on more data as in 17.2, quantisation to fewer bits, sharing keys
and values across heads, efficient attention), are a large part of current engineering.

### What is known and what is claimed

A rough sorting, by the standard of this book (a proof, or a measurement in a published paper):

| statement | status |
|---|---|
| Next-token cross-entropy is minimised by the true conditional distribution | proved (17.1) |
| Loss falls smoothly as a power law in parameters, data and compute over the ranges measured | measured (Kaplan et al. 2020; Hoffmann et al. 2022) |
| The KL-regularised RLHF objective has the optimum $\pi_{\text{ref}}e^{r/\beta}/Z$; DPO targets the same | proved (17.4) |
| Optimising hard against a learned reward model eventually lowers true quality | measured in specific settings (Gao et al. 2022) |
| Chain-of-thought improves accuracy on multi-step problems for large models | measured on specific benchmarks (Wei et al. 2022) |
| Certain abilities appear suddenly at a critical scale ("emergence") | disputed: reported by Wei et al. (2022, "Emergent abilities of large language models"); Schaeffer, Miranda and Koyejo (2023) showed that many such jumps become smooth when measured with a continuous metric |
| Models "understand", "reason" or "know" in the human sense | not a scientific claim until the words are defined and tested |
| Scaling alone will produce general intelligence | a prediction, not a result |

The pattern of the chapter holds throughout: the objective (imitate text, then match preferences) explains much of
the behaviour, both the impressive and the failing, and the honest way to talk about these systems is in terms of what
they were trained to do and what has been measured.

## In practice

Real language models are trained and run with array libraries such as PyTorch and JAX on many GPUs; open-source
libraries built on them implement the decoding rules of 17.3, reward-model training, PPO and DPO; retrieval uses
search engines with BM25 (such as Apache Lucene) or approximate nearest-neighbour indexes over embeddings. The toy
programs here show what those libraries compute, at a size you can read.

## Check yourself

??? question "1. Under the toy grammar, compute the probability, the cross-entropy per token and the perplexity of the sentence 'the lander takes a picture of the sky .' (after a full stop)."

    The uncertain choices are *lander* (0.2), *takes* (0.3) and *sky* after *of the* (0.2); every other token is
    forced (probability 1). So $P = 0.2 \times 0.3 \times 0.2 = 0.012$. The sentence has 9 tokens (*the lander takes a
    picture of the sky .*). The total negative log-probability is $-\ln 0.012 = 4.423$ nats, the average is
    $4.423/9 = 0.491$ nats per token, and the perplexity is $e^{0.491} = 1.635$. It is higher than the 1.39 of the
    sentence in 17.1 because it makes less likely choices.

??? question "2. A model predicts the next token after some context with q = (0.5, 0.5) while the true distribution is p = (0.9, 0.1). Compute the expected cross-entropy, the entropy and the KL divergence, and check the identity of 17.1."

    Cross-entropy: $-(0.9\ln 0.5 + 0.1\ln 0.5) = \ln 2 = 0.6931$. Entropy:
    $-(0.9\ln 0.9 + 0.1\ln 0.1) = 0.0948 + 0.2303 = 0.3251$. KL:
    $0.9\ln(0.9/0.5) + 0.1\ln(0.1/0.5) = 0.5290 - 0.1609 = 0.3681$. Indeed $0.3251 + 0.3681 = 0.6932$, equal to the
    cross-entropy up to rounding. The model would lose 0.368 nats per occurrence of this context compared with knowing
    $p$.

??? question "3. Two tokens have logits 2 and 0. Give the probability of the first at temperatures 0.5, 1 and 2, and say what happens as the temperature goes to 0 and to infinity."

    The probability of the first is $\sigma(2/\tau) = 1/(1 + e^{-2/\tau})$. At $\tau = 0.5$: $\sigma(4) = 0.982$. At
    $\tau = 1$: $\sigma(2) = 0.881$. At $\tau = 2$: $\sigma(1) = 0.731$. As $\tau \to 0$ it tends to 1 (greedy); as
    $\tau \to \infty$ it tends to 0.5 (uniform). The entropy rises with $\tau$, as the theorem of 17.3 requires.

??? question "4. A next-token distribution is (0.40, 0.25, 0.15, 0.10, 0.05, 0.05). What do top-k with k = 2 and nucleus sampling with p = 0.75 and p = 0.5 keep, and with what renormalised probabilities?"

    Top-2 keeps 0.40 and 0.25 (total 0.65): $0.615, 0.385$. Nucleus with $p = 0.75$: the running totals are
    0.40, 0.65, 0.80, so three tokens are needed to reach 0.75; dividing by 0.80 gives $0.500, 0.3125, 0.1875$.
    Nucleus with $p = 0.5$: the running totals 0.40, 0.65 first reach 0.5 at the second token, so it keeps the same
    two as top-2. The nucleus size depends on the shape of the distribution; $k$ does not.

??? question "5. Prove that greedy decoding with a model that looks only at the last k tokens eventually repeats a cycle, and bound the length of the text before the cycle starts plus the cycle length."

    The state of the decoder is the window of the last $k$ tokens; there are at most $V^k$ windows. Greedy decoding
    computes the next window as a fixed function of the current one. In a sequence of $V^k + 1$ windows, two must be
    equal (pigeonhole); if window $s_i = s_j$ with $i < j$, then since each window determines the next,
    $s_{i+1} = s_{j+1}$ and so on, so from position $i$ on the sequence repeats with period $j - i$. Hence the
    pre-cycle part plus one cycle together span at most $V^k$ windows. In the tiny model ($k = 2$) the cycle is the
    7-token sentence *the rover drives to the crater .* Sampling breaks the argument because the next window is
    random.

??? question "6. Under Bradley-Terry, response A has reward 1.0 and B has 0.2. What is P(A preferred)? If a reward model is trained on 1000 comparisons of A and B in which A won 690 times, what reward difference does maximum likelihood give?"

    $P = \sigma(0.8) = 1/(1 + e^{-0.8}) = 0.690$. The likelihood $690\ln\sigma(\Delta) + 310\ln(1 - \sigma(\Delta))$ is
    maximised where $\sigma(\Delta) = 0.69$, that is $\Delta = \ln(0.69/0.31) = 0.800$. Maximum likelihood recovers
    the difference, never the rewards themselves: adding a constant to both changes nothing.

??? question "7. With pi_ref = (0.5, 0.5) over two responses with rewards r = (1, 0), compute the KL-regularised optimum for beta = 0.5 and beta = 2, and the KL from the reference in each case."

    $\pi^* \propto (0.5e^{1/\beta}, 0.5)$. For $\beta = 0.5$: $(e^2, 1)/(e^2 + 1) = (0.881, 0.119)$; for $\beta = 2$:
    $(e^{0.5}, 1)/(e^{0.5} + 1) = (0.622, 0.378)$. KL from $(0.5, 0.5)$:
    $0.881\ln(0.881/0.5) + 0.119\ln(0.119/0.5) = 0.4993 - 0.1709 = 0.328$ nats for $\beta = 0.5$, and
    $0.622\ln 1.245 + 0.378\ln 0.755 = 0.1363 - 0.1061 = 0.030$ nats for $\beta = 2$. Smaller $\beta$ buys more
    reward with more distance from the reference.

??? question "8. In DPO with beta = 0.1, the policy has log pi_theta/pi_ref = +0.5 on the preferred response and -0.3 on the other. Compute the loss on this pair and the direction of its gradient."

    The margin is $0.1 \times (0.5 - (-0.3)) = 0.08$, so the loss is $-\ln\sigma(0.08) = 0.654$, close to the
    $\ln 2 = 0.693$ of an untrained policy. The derivative of $-\ln\sigma(m)$ with respect to $m$ is
    $-(1 - \sigma(m)) = -0.480$, so gradient descent increases the margin: it raises $\log\pi_\theta(y_w)$ and lowers
    $\log\pi_\theta(y_l)$, each with weight $\beta(1 - \sigma(m)) = 0.048$. Pairs the policy already ranks strongly
    correctly ($\sigma(m)$ near 1) get almost no weight.

??? question "9. A model generated n = 10 programs for a problem and c = 2 passed. Compute pass@1, pass@3 and the naive estimate of pass@3."

    pass@1 $= 1 - \binom{8}{1}/\binom{10}{1} = 1 - 0.8 = 0.2$. pass@3 $= 1 - \binom{8}{3}/\binom{10}{3} = 1 - 56/120 = 0.533$.
    Naive: $1 - 0.8^3 = 0.488$, lower, as Jensen's inequality predicts.

??? question "10. Write code: a function that returns how many benchmark questions are needed so that a difference of d in accuracy between two independently evaluated models at accuracy near a is outside the 95 percent noise band. Evaluate it for a = 0.75 and d = 0.02."

    The difference of two independent accuracies has standard error $\sqrt{2a(1-a)/n}$; we need
    $1.96\sqrt{2a(1-a)/n} \le d$, so $n \ge 2a(1-a)(1.96/d)^2$.

    ```python
    import math

    def questions_needed(a, d, z=1.96):
        return math.ceil(2 * a * (1 - a) * (z / d) ** 2)

    print(questions_needed(0.75, 0.02))   # 3602
    print(questions_needed(0.75, 0.05))   # 577
    ```

    About 3600 questions to separate a 2-point gap. Scoring both models on the same questions (a paired test)
    needs fewer, because the questions both models get right or both get wrong cancel.

??? question "11. Write code: add a third tool, lookup_year(name), to the ReAct program that returns only the year from the best-matching document, and change the fake model to use it. Why does a narrow tool help a real model?"

    ```python
    def lookup_year(name):
        doc = retrieve(name, k=1)[0][1]
        m = re.search(r"\b(1[89]\d\d|20\d\d)\b", doc)
        return m.group(1) if m else "error: no year found"

    TOOLS["lookup_year"] = lookup_year

    def fake_model_react(transcript):
        obs = re.findall(r"Observation: (.*)", transcript)
        if len(obs) == 0:
            return "Thought: Year of Dijkstra's algorithm.\nAction: lookup_year[Dijkstra shortest path]"
        if len(obs) == 1:
            return "Thought: Year of A*.\nAction: lookup_year[A* search algorithm]"
        if len(obs) == 2:
            return f"Thought: Subtract.\nAction: calculate[{obs[1]} - {obs[0]}]"
        return f"Thought: Done.\nFinal Answer: {obs[-1]} years"
    ```

    With these definitions placed after the originals and before the call to `react`, it gives observations 1959, 1968 and 9. A narrow
    tool returns exactly the piece needed, so the model has less text to read (and misread) and the harness can
    check the result's format; it is also less exposed to instructions hidden in retrieved pages.

??? question "12. Estimate the KV-cache memory for a model with 32 layers and width 4096, 2 bytes per number, at a context of 8192 tokens, and the forward FLOPs per token if it has 7 billion parameters."

    Per token: $2 \times 32 \times 4096 \times 2 = 524{,}288$ bytes (0.5 MiB). For 8192 tokens:
    $524{,}288 \times 8192 = 4{,}294{,}967{,}296$ bytes, exactly 4 GiB. Forward FLOPs per token $\approx 2N = 14$
    billion. (Models that share keys and values across groups of heads divide the cache by the group size.)

## What you learned

- A language model gives a probability for the next token; by the chain rule that defines a probability for every
  text, and cross-entropy training drives it toward the true conditional distributions (Gibbs' inequality). Perplexity
  is the exponential of the held-out cross-entropy.
- Pretraining at scale is this objective on hundreds of billions of tokens; training costs about $6ND$ FLOPs
  ($3.14 \times 10^{23}$ for GPT-3), and few-shot prompting uses the context instead of gradient steps.
- Decoding is a choice: greedy and beam search maximise probability and repeat themselves; temperature reshapes the
  distribution and provably raises entropy as it rises; top-k and nucleus sampling cut off the unreliable tail.
- Instruction tuning is supervised learning on demonstrations; RLHF fits a Bradley-Terry reward model and optimises a
  KL-regularised objective whose exact optimum is $\pi_{\text{ref}}e^{r/\beta}/Z$; DPO reaches the same optimum by a
  classification loss on the policy. Optimising a flawed reward too hard lowers true quality.
- RAG puts retrieved passages into the prompt; agents are a loop of model output, strict parsing, tools and
  observations, and most of their reliability lives in that loop.
- Chain-of-thought gives a fixed-depth model more sequential computation; self-consistency amplifies the plurality
  answer; evaluation needs unbiased estimators (pass@k), contamination checks and honest error bars.
- Hallucination follows from the objective and has a theoretical lower bound for calibrated models; reasoning failures
  appear under systematic variation; inference cost grows with model size and generated tokens.

**Next:** [Chapter 18](18-Perception-and-Robotics.md), where the agent leaves text behind and must see, locate itself
and move in the physical world.

## Further reading

- D. Jurafsky and J. H. Martin, *Speech and Language Processing*, 3rd ed. draft: the chapters on n-gram models,
  transformers and large language models.
- S. Russell and P. Norvig, *Artificial Intelligence: A Modern Approach*, 4th ed., 2020: chapter 24 (deep learning for
  natural language processing).
- Y. Bengio, R. Ducharme, P. Vincent and C. Jauvin, "A neural probabilistic language model", *Journal of Machine
  Learning Research* 3, 2003.
- A. Radford, K. Narasimhan, T. Salimans and I. Sutskever, "Improving language understanding by generative
  pre-training", 2018; A. Radford and colleagues, "Language models are unsupervised multitask learners", 2019.
- T. B. Brown and colleagues, "Language models are few-shot learners", NeurIPS 2020.
- J. Kaplan and colleagues, "Scaling laws for neural language models", 2020; J. Hoffmann and colleagues, "Training
  compute-optimal large language models", NeurIPS 2022.
- A. Fan, M. Lewis and Y. Dauphin, "Hierarchical neural story generation", ACL 2018; A. Holtzman, J. Buys, L. Du,
  M. Forbes and Y. Choi, "The curious case of neural text degeneration", ICLR 2020 (arXiv 2019).
- R. A. Bradley and M. E. Terry, "Rank analysis of incomplete block designs: I. The method of paired comparisons",
  *Biometrika* 39, 1952.
- P. Christiano, J. Leike, T. B. Brown, M. Martic, S. Legg and D. Amodei, "Deep reinforcement learning from human
  preferences", NeurIPS 2017; D. M. Ziegler and colleagues, "Fine-tuning language models from human preferences",
  2019; N. Stiennon and colleagues, "Learning to summarize from human feedback", NeurIPS 2020.
- J. Wei and colleagues, "Finetuned language models are zero-shot learners", ICLR 2022; L. Ouyang and colleagues,
  "Training language models to follow instructions with human feedback", NeurIPS 2022.
- R. Rafailov, A. Sharma, E. Mitchell, S. Ermon, C. D. Manning and C. Finn, "Direct preference optimization: your
  language model is secretly a reward model", NeurIPS 2023; L. Gao, J. Schulman and J. Hilton, "Scaling laws for
  reward model overoptimization", 2022.
- P. Lewis and colleagues, "Retrieval-augmented generation for knowledge-intensive NLP tasks", NeurIPS 2020;
  V. Karpukhin and colleagues, "Dense passage retrieval for open-domain question answering", EMNLP 2020; K. Guu and
  colleagues, "REALM: retrieval-augmented language model pre-training", ICML 2020; S. Robertson and H. Zaragoza, "The
  probabilistic relevance framework: BM25 and beyond", 2009; N. F. Liu and colleagues, "Lost in the middle: how
  language models use long contexts", 2023.
- S. Yao and colleagues, "ReAct: synergizing reasoning and acting in language models", ICLR 2023 (arXiv 2022);
  T. Schick and colleagues, "Toolformer: language models can teach themselves to use tools", NeurIPS 2023;
  K. Greshake and colleagues, "Not what you've signed up for: compromising real-world LLM-integrated applications
  with indirect prompt injection", 2023.
- J. Wei and colleagues, "Chain-of-thought prompting elicits reasoning in large language models", NeurIPS 2022;
  T. Kojima and colleagues, "Large language models are zero-shot reasoners", NeurIPS 2022; X. Wang and colleagues,
  "Self-consistency improves chain of thought reasoning in language models", ICLR 2023; M. Nye and colleagues, "Show
  your work: scratchpads for intermediate computation with language models", 2021; W. Merrill and A. Sabharwal, "The
  expressive power of transformers with chain of thought", ICLR 2024.
- D. Hendrycks and colleagues, "Measuring massive multitask language understanding", ICLR 2021; K. Cobbe and
  colleagues, "Training verifiers to solve math word problems", 2021; M. Chen and colleagues, "Evaluating large
  language models trained on code", 2021; Z. Zhao, E. Wallace, S. Feng, D. Klein and S. Singh, "Calibrate before use:
  improving few-shot performance of language models", ICML 2021; L. Zheng and colleagues, "Judging LLM-as-a-judge with
  MT-Bench and Chatbot Arena", NeurIPS 2023.
- J. Maynez, S. Narayan, B. Bohnet and R. McDonald, "On faithfulness and factuality in abstractive summarization", ACL
  2020; S. Lin, J. Hilton and O. Evans, "TruthfulQA: measuring how models mimic human falsehoods", ACL 2022; A. T.
  Kalai and S. S. Vempala, "Calibrated language models must hallucinate", STOC 2024; L. Berglund and colleagues, "The
  reversal curse: LLMs trained on 'A is B' fail to learn 'B is A'", 2023; N. Dziri and colleagues, "Faith and fate:
  limits of transformers on compositionality", NeurIPS 2023.
- J. Wei and colleagues, "Emergent abilities of large language models", *Transactions on Machine Learning Research*,
  2022; R. Schaeffer, B. Miranda and S. Koyejo, "Are emergent abilities of large language models a mirage?", NeurIPS
  2023.
- On this site: [Machine learning, Chapter 18](../machine-learning/18-Sequence-Models.md) (word vectors, recurrent
  networks, attention), [Chapter 19](../machine-learning/19-Transformers.md) (the transformer, tokenization,
  pretraining) and [Chapter 23](../machine-learning/23-Where-Machine-Learning-Goes.md) (scaling laws, in-context
  learning, interpretability); this book's [Chapter 15](15-Reinforcement-Learning.md) (policy gradients, PPO, reward
  design) and [Chapter 16](16-Natural-Language-Processing.md) (n-grams and perplexity); the Algorithms book's
  [Chapter 18](../algorithms/18-String-Algorithms.md) (string matching, the basis of n-gram overlap checks).
