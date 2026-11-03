# 16. Natural language processing

*An agent that works with people must read and write their language: commands to a robot, questions to an assistant,
reports from a field team, documents in a hundred languages. Language looks easy because people use it without effort,
but it is ambiguous at every level, endlessly varied, and full of rare events. This chapter answers the question: how
can a program assign probabilities to sentences, find the structure inside them, represent what words mean, and
translate between languages? You will build n-gram language models with smoothing and measure them by perplexity,
tag words with a hidden Markov model, parse with the CKY algorithm, compute word vectors from counts, train a small
neural language model, and learn a translation table with the EM algorithm of IBM Model 1. All of it runs on a toy
corpus generated from a grammar we know, so every model can be compared with the truth.*

!!! abstract "In this chapter"
    **You will learn:**

    - why language is hard: ambiguity in words, structure, meaning and reference, and the long tail of rare events
    - language models: the chain rule, n-grams, add-k smoothing, interpolation and Kneser-Ney, and perplexity, with a
      proof that no model beats the true distribution
    - classic tasks: text classification, part-of-speech tagging with an HMM, and parsing with probabilistic grammars and
      the CKY algorithm (correctness and cost proved)
    - the distributional idea of meaning: co-occurrence counts, PPMI and SVD word vectors
    - neural language models from Bengio et al. (2003) to transformers, and why they escape the sparsity of n-grams
    - machine translation from rules to statistics (IBM Model 1 with EM, BLEU) to neural networks

    **You need:** [Chapter 13](13-Reasoning-over-Time.md) (HMMs and Viterbi) and [Chapter 12](12-Probabilistic-Reasoning.md)
    (probability). Machine learning background: [Machine learning, Chapter 6](../machine-learning/06-Classification-and-Logistic-Regression.md)
    (classification), [Chapter 13](../machine-learning/13-Clustering.md) (EM), [Chapter 18](../machine-learning/18-Sequence-Models.md)
    (word2vec, RNNs, attention) and [Chapter 19](../machine-learning/19-Transformers.md) (transformers). Dynamic
    programming from the Algorithms book's [Chapter 13](../algorithms/13-Dynamic-Programming.md).

    **Levels:** 16.1 is beginner; 16.2 is beginner to intermediate; 16.3 is intermediate; 16.4 and 16.5 are
    intermediate; 16.6 is intermediate to advanced.

## 16.1 Why language is hard: ambiguity at every level

Read this sentence: *the rover sees the rock with the camera.* Did the rover use its camera to see the rock, or did it
see a rock that had a camera on it? You chose the first without noticing; a program has to be told why. Language is
full of such choices, at every level.

- **Words and their pieces.** Where does a word begin? English mostly uses spaces, but "don't" is two words in one,
  Chinese and Japanese are written without spaces, and German writes compounds as one word. The first step of any
  system, **tokenisation**, splitting text into units called **tokens**, already involves decisions.
- **Lexical ambiguity.** One spelling, several meanings or roles: "bank" (river or money), "drills" (a noun, the tools,
  or a verb, the action). Deciding the **part of speech** (noun, verb, adjective, ...) of each word is called
  **tagging**.
- **Syntactic ambiguity.** One string of words, several structures. The camera sentence has two: the phrase "with the
  camera" can attach to the verb phrase or to the noun phrase. Add more such phrases and the number of structures
  explodes (16.3 counts them).
- **Semantic ambiguity.** "Every rover visited a crater": one crater for all, or perhaps a different one each? This is
  **quantifier scope**.
- **Reference and pragmatics.** "The trophy does not fit in the suitcase because it is too big." What is too big? Change
  "big" to "small" and the answer flips. Hector Levesque, Ernest Davis and Leora Morgenstern (2012) proposed such
  **Winograd schemas** as a test that needs knowledge of the world, not just of words. And "Can you pass the salt?" is
  a request, not a question about ability.

On top of ambiguity comes **sparsity**. In any large body of text, a few words are very common and most words are
rare. George Kingsley Zipf observed in the 1930s and 1940s that the frequency of a word is roughly inversely proportional
to its rank in the frequency table: the second most common word occurs about half as often as the first, the tenth
about a tenth as often. **Zipf's law** means that however much text you collect, many words, and most word sequences,
will be seen rarely or never. Every statistical method in this chapter must cope with events it has never seen.

### A toy language we fully understand

Real corpora must be downloaded, and their true structure is unknown. To build everything from scratch and compare every
model with the truth, this chapter uses a small artificial language generated by a **probabilistic context-free
grammar** (PCFG), a set of rewriting rules with probabilities, defined properly in 16.3. Its 34 words describe rovers,
rocks and craters. Three words, "drills", "tracks" and "samples", are both nouns and verbs, and prepositional phrases
("with the camera", "near the crater") create attachment ambiguity. Because every sentence is generated by the program,
we know its true tags and its true tree.

```python
--8<-- "books/ai/ch16_grammar.py"
```

```
the crater tracks the rover
   tags: DET N V DET N
the scientist photographs ben
   tags: DET N V NAME
the dusty rock with a rock near ada sees ben
   tags: DET ADJ N P DET N P NAME V NAME
the rover near the scientist samples a crater
   tags: DET N P DET N V DET N
   tree of the first: (S (NP (Det the) (N crater)) (VP (V tracks) (NP (Det the) (N rover))))

5000 sentences, 33368 tokens, 34 word types, mean length 6.67
rank  word         count   rank x count
   1  the            7224       7224
   2  a              3191       6382
   3  rover          2260       6780
   5  with           1324       6620
  10  tracks          865       8650
  20  robot           596      11920
  30  rolls           286       8580
'drills': as a noun 473 times, as a verb 637 times
'tracks': as a noun 437 times, as a verb 428 times
'samples': as a noun 314 times, as a verb 298 times
```

The product rank times count stays within a factor of two over the ranks shown, a faint echo of Zipf's law. Real text
has hundreds of thousands of word types and follows the law over several orders of magnitude; the toy is far kinder,
which is why its numbers below are much smaller than those for real English. The ideas are the same.

## 16.2 Words and counts: tokens, n-gram language models, smoothing, perplexity

A **language model** assigns a probability to every sequence of words. Why want one? Because many tasks are choosing
between sequences: a speech recogniser deciding between "recognise speech" and "wreck a nice beach", a translator
choosing the most natural of several outputs, a keyboard predicting the next word, a spelling corrector. And since
2018, language models trained on huge corpora have become the basis of most of NLP ([Chapter
17](17-Large-Language-Models.md)).

### The chain rule and the Markov assumption

By the chain rule of probability, any sequence probability factors into next-word predictions:

$$
P(w_1, w_2, \dots, w_n) = \prod_{i=1}^{n} P(w_i \mid w_1, \dots, w_{i-1}).
$$

Nothing is assumed yet. The trouble is that the conditioning histories are as long as the sentence, so they almost
never repeat. The **n-gram** approximation keeps only the last $n - 1$ words, a Markov assumption ([Chapter
13](13-Reasoning-over-Time.md)) of order $n - 1$:

$$
P(w_i \mid w_1, \dots, w_{i-1}) \approx P(w_i \mid w_{i-n+1}, \dots, w_{i-1}).
$$

A **unigram** model ($n = 1$) ignores context; a **bigram** model ($n = 2$) conditions on one previous word; a
**trigram** on two. We add a start symbol `<s>` before each sentence (two for a trigram) and an end symbol `</s>` after
it, so that the model also predicts where sentences begin and end, and the probabilities of all finite sentences sum to
1.

### Maximum likelihood estimates

The obvious estimate of $P(w \mid u)$ for a bigram is the fraction of times $u$ was followed by $w$:

$$
P_{\text{ML}}(w \mid u) = \frac{C(u\, w)}{C(u)},
$$

where $C$ counts occurrences in the training text. This is the **maximum likelihood** estimate: of all bigram tables,
it is the one that gives the training text the highest probability (the standard result for a categorical distribution;
[Machine learning, Chapter 3](../machine-learning/03-The-Math-Toolkit.md)).

**A worked example.** From the 5000 training sentences: the context `<s>` occurs 5000 times and is followed by "the"
3030 times, so $P(\text{the} \mid \texttt{<s>}) = 0.606$. "the" occurs 7224 times as a context and is followed by "rover"
1145 times: 0.1585. "rover" (2260) is followed by "stops" 93 times: 0.0412. "stops" (477) is followed by `</s>` 397
times: 0.8323. So

$$
P(\text{the rover stops}) \approx 0.606 \cdot 0.1585 \cdot 0.0412 \cdot 0.8323 = 0.00329.
$$

### The zero problem and smoothing

A bigram never seen in training gets probability 0, and one zero factor makes the whole sentence impossible. With 50
training sentences, the word "dusty" occurs 7 times and is never followed by "wheel", so "the dusty wheel stops" has
probability 0 under the maximum likelihood model, although the grammar can produce it. **Smoothing** moves some
probability from seen events to unseen ones.

- **Add-k (Laplace) smoothing** pretends every bigram was seen $k$ extra times:
  $P(w \mid u) = (C(u\,w) + k)/(C(u) + kV)$ with $V$ the vocabulary size. With $k = 1$, $V = 35$ (34 words plus
  `</s>`): $P(\text{wheel} \mid \text{dusty}) = (0 + 1)/(7 + 35) = 0.024$. It is the posterior mean under a uniform
  Dirichlet prior (the many-outcome version of the beta prior in [Machine learning, Chapter
  12](../machine-learning/12-Probabilistic-Models.md)). With $k = 1$ it usually moves far too much mass to unseen events;
  smaller $k$ is better, and $k$ is chosen on held-out data.
- **Interpolation** mixes the orders: $P(w \mid u\,v) = \lambda_3 P_{\text{ML}}(w \mid u\,v) +
  \lambda_2 P_{\text{ML}}(w \mid v) + \lambda_1 P(w)$, with $\lambda$s summing to 1, chosen to maximise the probability of a held-out **development** set
  (Jelinek and Mercer, 1980). **Backoff** (Katz, 1987) instead uses the trigram when it has been seen and falls back to
  the bigram only when it has not.
- **Kneser-Ney smoothing** (Kneser and Ney, 1995) combines two ideas. **Absolute discounting**: subtract a fixed
  $d \approx 0.75$ from every seen count and give the freed mass to the lower order. And a better lower order: instead of
  how often $w$ occurs, use in how many **different contexts** it occurs, the **continuation probability**
  $P_{\text{cont}}(w) \propto |\{u : C(u\,w) > 0\}|$. A word that is frequent but only ever follows one particular word
  (the standard example is "Francisco", nearly always after "San") should get little probability in a new context.
  For bigrams, interpolated Kneser-Ney is

$$
P_{\text{KN}}(w \mid u) = \frac{\max(C(u\,w) - d, 0)}{C(u)} + \lambda(u)\, P_{\text{cont}}(w), \qquad
\lambda(u) = \frac{d \cdot |\{w : C(u\,w) > 0\}|}{C(u)}.
$$

(The program adds 1 to every continuation count so that no word gets probability exactly 0.) Stanley Chen and
Joshua Goodman's 1998 comparison found modified Kneser-Ney the best of the methods they tested, and it
remained the standard n-gram method until neural models replaced n-grams.

### Perplexity

How do we compare language models? By how well they predict text they have **not** seen. Take a test set of $N$ tokens
(counting each `</s>`). The **cross-entropy** of the model $q$ on it is the average number of bits needed per token,

$$
H(q) = -\frac{1}{N} \sum_{i=1}^{N} \log_2 q(w_i \mid \text{history}_i),
$$

and the **perplexity** is $2^{H(q)}$. Perplexity has a friendly meaning: a model with perplexity 7 is as uncertain, on
average, as if it had to choose uniformly among 7 words at each step (a uniform model over $V$ words has perplexity
exactly $V$; Exercise 3). Lower is better.

**Theorem.** If the test text is drawn from a true distribution $p$, then in expectation no model has lower
cross-entropy than $p$ itself: $-\sum_x p(x) \log q(x) \ge -\sum_x p(x) \log p(x)$, with equality only when $q = p$.

**Proof.** The difference is $\sum_x p(x)\log\frac{p(x)}{q(x)} = \mathrm{KL}(p \,\|\, q)$. Since $\log$ is concave,
Jensen's inequality gives $-\mathrm{KL}(p \,\|\, q) = \sum_x p(x)\log\frac{q(x)}{p(x)} \le \log\sum_x p(x)\frac{q(x)}{p(x)}
= \log\sum_x q(x) \le \log 1 = 0$, with equality only if $q(x)/p(x)$ is constant, that is, $q = p$. $\square$

So the true model's perplexity is a floor, and how close a model gets to it is a fair score. For our toy language we can
compute the floor exactly: 16.3 does it with the inside algorithm, and the answer is 6.04.

```python
--8<-- "books/ai/ch16_ngram.py"
```

```
perplexity on 1000 held-out sentences (lower is better); vocabulary 35 symbols
training sentences             50       500      5000
unigram, add-1            22.400    21.418    21.319
bigram, unsmoothed           inf       inf     7.480
bigram, add-1             16.304     9.002     7.635
bigram, add-0.01          18.317     8.143     7.482
trigram, add-0.01         29.450    12.341     7.598
bigram, Kneser-Ney        13.188     8.140     7.510
interpolated, tuned       14.824     8.189     7.338
interpolation weights (trigram/bigram/unigram) chosen on the dev set: 0.00/0.64/0.36, 0.15/0.84/0.01, 0.70/0.29/0.01

most likely words after 'the' (bigram, maximum likelihood): rover 0.158, rock 0.129, crater 0.089, red 0.079, camera 0.066
P(drills | the) = 0.0327   P(drills | rover) = 0.0553

sentences sampled from the trigram model (add-0.01):
   a rock drills the rock
   a scientist
   a wheel near the robot on a rock waits
   the rover
```

Reading the table column by column:

- **Context helps enormously.** The unigram model sits at about 21 whatever the data; a bigram gets to 7.5. Knowing one
  previous word cuts the uncertainty by a factor of almost three.
- **Without smoothing, a model is useless on new text**: one unseen bigram in the test set makes the perplexity
  infinite, and with 50 or 500 training sentences there are always some.
- **The right amount of smoothing depends on the amount of data.** With 50 sentences, heavy smoothing (add-1) beats
  light smoothing (add-0.01); with 500 and 5000 it is the other way round. Kneser-Ney is best or nearly best at every
  size.
- **Longer context needs more data.** With 50 sentences the trigram is the worst model of all (29.5): almost every
  trigram context is new. With 5000 it is competitive. Interpolation tuned on a development set handles this
  automatically: it gives the trigram weight 0 with 50 sentences and 0.7 with 5000, and is the best model at 5000
  (7.34).
- **The floor is 6.04.** No n-gram model reaches it, because the grammar's dependencies (a verb may be separated from
  its subject by several prepositional phrases) are longer than two words.

The sampled sentences look locally right and globally loose: "a scientist" is a sentence in no grammar of English, but
every pair and triple of words in it is fine. C. E. Shannon showed the same effect in 1948, generating English-like
text from letter and word n-gram statistics, and the observation drove decades of work on longer contexts.

## 16.3 Classic tasks: classification, tagging (HMM POS tagging), parsing (CKY) from scratch

*Level: intermediate.*

### Text classification

Many NLP tasks are classification: spam or not, the topic of a news story, the sentiment of a review, the language of a
document. The simplest representation is the **bag of words**: count each word, ignore the order. Two classic
classifiers on top of it:

- **Naive Bayes** assumes the words are independent given the class, so
  $P(c \mid w_1, \dots, w_n) \propto P(c)\prod_i P(w_i \mid c)$, with smoothed counts for $P(w \mid c)$ exactly as in
  16.2. It is built from scratch in [Machine learning, Chapter 12](../machine-learning/12-Probabilistic-Models.md).
- **Logistic regression** learns a weight per word and class ([Machine learning, Chapter
  6](../machine-learning/06-Classification-and-Logistic-Regression.md)); it usually beats naive Bayes given enough data,
  because it does not assume independence.

A bag of words cannot tell "the rover sees the rock" from "the rock sees the rover". For tasks where structure
matters, we need tags and trees.

### Part-of-speech tagging with an HMM

A **tagset** is a list of word classes. Real tagsets are larger (the Penn Treebank uses 45 tags; Marcus, Santorini and
Marcinkiewicz, 1993); ours has six: DET, N, ADJ, V, P, NAME. Tagging is a sequence problem made for the hidden Markov
models of [Chapter 13](13-Reasoning-over-Time.md):

- the **hidden states** are the tags $t_1, \dots, t_n$;
- the **observations** are the words;
- the **transition model** $P(t_i \mid t_{i-1})$ says which tags follow which (a noun often follows a determiner);
- the **emission model** $P(w_i \mid t_i)$ says which words a tag produces.

With a tagged training corpus, both tables are estimated by counting (with a little smoothing for unseen pairs), and the
best tag sequence for a new sentence is found by the **Viterbi** algorithm in $O(nT^2)$ time for $T$ tags. Why does
context help? In "the drills tracks the dune", "drills" follows a determiner, and a determiner is never followed by a
verb in this grammar, so $P(\text{V} \mid \text{DET}) \approx 0$ makes the noun reading win; then "tracks" follows a
noun, and N is followed by V or P, not N, so "tracks" is a verb.

```python
--8<-- "books/ai/ch16_tag_parse.py"
```

```
Part 1. HMM tagger, tested on 1000 held-out sentences
  training sentences   HMM accuracy   most-frequent-tag   on drills/tracks/samples: HMM   baseline
                   5         0.8701              0.7898                          0.7012     0.4730
                  50         0.9902              0.9454                          1.0000     0.5270
                5000         1.0000              0.9657                          1.0000     0.5270
  the rover drills the rock              -> DET N V DET N
  the drills tracks the dune             -> DET N V DET N
  the samples near the tracks waits      -> DET N P DET N V

Part 2. CKY parsing with the grammar's own probabilities
  the rover sees the rock with the camera
    P(sentence) = 3.915e-06, best parse 2.237e-06 (0.571 of the total)
    best: (S (NP (Det the) (N rover)) (VP (VP (V sees) (NP (Det the) (N rock))) (PP (P with) (NP (Det the) (N camera)))))
  the rover sees the rock near the crater
    P(sentence) = 3.915e-06, best parse 2.237e-06 (0.571 of the total)
    best: (S (NP (Det the) (N rover)) (VP (VP (V sees) (NP (Det the) (N rock))) (PP (P near) (NP (Det the) (N crater)))))
  number of parses with k prepositional phrases appended: 1 2 5 14 42 132 429
  perplexity of the 1000 test sentences under the true grammar: 6.037
```

The **most-frequent-tag baseline**, which ignores context and gives each word its commonest tag, is already 96.6
percent right with 5000 training sentences, because most words have only one tag. But on the three ambiguous words it
is barely better than a coin (53 percent). The HMM resolves them perfectly with 50 training sentences or more, using the
neighbouring tags. With only 5 training sentences many words are unknown, and the HMM must guess their tags from the
transitions alone; it still gets 87 percent.

Real English is much harder: more tags, many more ambiguous words, unknown words in every new text. Thorsten Brants's
TnT, a carefully smoothed trigram HMM tagger, reported about 96.7 percent accuracy on the Penn Treebank's Wall Street
Journal text (Brants, 2000), and discriminative models (conditional random fields, Lafferty, McCallum and Pereira,
2001; later neural taggers) went somewhat higher.

### Grammars and trees

A **context-free grammar** (CFG) has nonterminal symbols (S for sentence, NP noun phrase, VP verb phrase, PP
prepositional phrase, ...), terminal symbols (the words) and rules such as $\text{S} \to \text{NP}\ \text{VP}$. A
sentence belongs to the language if it can be derived from S by applying rules; the **parse tree** records how. A
**probabilistic** CFG gives each rule a probability, with the rules for each left-hand side summing to 1; the
probability of a tree is the product of the probabilities of the rules it uses, and the probability of a sentence is the
sum over all its trees. Our grammar has rules like

$$
\begin{aligned}
\text{S} &\to \text{NP}\ \text{VP}\ [1.0] &\qquad \text{NP} &\to \text{Det}\ \text{N}\ [0.55] \mid \text{NP}\ \text{PP}\ [0.15] \mid \dots \\
\text{VP} &\to \text{V}\ \text{NP}\ [0.55] \mid \text{VP}\ \text{PP}\ [0.20] \mid \dots &\qquad \text{PP} &\to \text{P}\ \text{NP}\ [1.0]
\end{aligned}
$$

It is in **Chomsky normal form** (CNF): every rule rewrites a nonterminal either as exactly two nonterminals or as one
word. Any CFG can be converted to CNF (by splitting long rules into binary ones and removing unit rules), so this costs
no generality.

<figure class="mars-fig" markdown="0">
<svg viewBox="0 0 700 345" role="img" aria-label="Two parse trees for the rover sees the rock with the camera. On the left the prepositional phrase with the camera attaches to the verb phrase; on the right it attaches to the noun phrase the rock.">
<text x="25.0" y="300" font-size="13" text-anchor="middle" fill="currentColor" font-style="italic">the</text>
<line x1="25.0" y1="108" x2="25.0" y2="286" stroke="currentColor" stroke-width="1" stroke-opacity="0.7"/>
<rect x="8.0" y="92" width="34" height="17" rx="4" fill="#7ccf9a" fill-opacity="0.55"/>
<text x="25.0" y="105" font-size="12" text-anchor="middle" fill="currentColor">Det</text>
<text x="67.0" y="300" font-size="13" text-anchor="middle" fill="currentColor" font-style="italic">rover</text>
<line x1="67.0" y1="108" x2="67.0" y2="286" stroke="currentColor" stroke-width="1" stroke-opacity="0.7"/>
<rect x="50.0" y="92" width="34" height="17" rx="4" fill="#7ccf9a" fill-opacity="0.55"/>
<text x="67.0" y="105" font-size="12" text-anchor="middle" fill="currentColor">N</text>
<line x1="46.0" y1="68" x2="25.0" y2="90" stroke="currentColor" stroke-width="1" stroke-opacity="0.7"/>
<line x1="46.0" y1="68" x2="67.0" y2="90" stroke="currentColor" stroke-width="1" stroke-opacity="0.7"/>
<rect x="29.0" y="52" width="34" height="17" rx="4" fill="#9cc9ea" fill-opacity="0.55"/>
<text x="46.0" y="65" font-size="12" text-anchor="middle" fill="currentColor">NP</text>
<text x="109.0" y="300" font-size="13" text-anchor="middle" fill="currentColor" font-style="italic">sees</text>
<line x1="109.0" y1="148" x2="109.0" y2="286" stroke="currentColor" stroke-width="1" stroke-opacity="0.7"/>
<rect x="92.0" y="132" width="34" height="17" rx="4" fill="#7ccf9a" fill-opacity="0.55"/>
<text x="109.0" y="145" font-size="12" text-anchor="middle" fill="currentColor">V</text>
<text x="151.0" y="300" font-size="13" text-anchor="middle" fill="currentColor" font-style="italic">the</text>
<line x1="151.0" y1="188" x2="151.0" y2="286" stroke="currentColor" stroke-width="1" stroke-opacity="0.7"/>
<rect x="134.0" y="172" width="34" height="17" rx="4" fill="#7ccf9a" fill-opacity="0.55"/>
<text x="151.0" y="185" font-size="12" text-anchor="middle" fill="currentColor">Det</text>
<text x="193.0" y="300" font-size="13" text-anchor="middle" fill="currentColor" font-style="italic">rock</text>
<line x1="193.0" y1="188" x2="193.0" y2="286" stroke="currentColor" stroke-width="1" stroke-opacity="0.7"/>
<rect x="176.0" y="172" width="34" height="17" rx="4" fill="#7ccf9a" fill-opacity="0.55"/>
<text x="193.0" y="185" font-size="12" text-anchor="middle" fill="currentColor">N</text>
<line x1="172.0" y1="148" x2="151.0" y2="170" stroke="currentColor" stroke-width="1" stroke-opacity="0.7"/>
<line x1="172.0" y1="148" x2="193.0" y2="170" stroke="currentColor" stroke-width="1" stroke-opacity="0.7"/>
<rect x="155.0" y="132" width="34" height="17" rx="4" fill="#9cc9ea" fill-opacity="0.55"/>
<text x="172.0" y="145" font-size="12" text-anchor="middle" fill="currentColor">NP</text>
<line x1="140.5" y1="108" x2="109.0" y2="130" stroke="currentColor" stroke-width="1" stroke-opacity="0.7"/>
<line x1="140.5" y1="108" x2="172.0" y2="130" stroke="currentColor" stroke-width="1" stroke-opacity="0.7"/>
<rect x="123.5" y="92" width="34" height="17" rx="4" fill="#9cc9ea" fill-opacity="0.55"/>
<text x="140.5" y="105" font-size="12" text-anchor="middle" fill="currentColor">VP</text>
<text x="235.0" y="300" font-size="13" text-anchor="middle" fill="currentColor" font-style="italic">with</text>
<line x1="235.0" y1="148" x2="235.0" y2="286" stroke="currentColor" stroke-width="1" stroke-opacity="0.7"/>
<rect x="218.0" y="132" width="34" height="17" rx="4" fill="#7ccf9a" fill-opacity="0.55"/>
<text x="235.0" y="145" font-size="12" text-anchor="middle" fill="currentColor">P</text>
<text x="277.0" y="300" font-size="13" text-anchor="middle" fill="currentColor" font-style="italic">the</text>
<line x1="277.0" y1="188" x2="277.0" y2="286" stroke="currentColor" stroke-width="1" stroke-opacity="0.7"/>
<rect x="260.0" y="172" width="34" height="17" rx="4" fill="#7ccf9a" fill-opacity="0.55"/>
<text x="277.0" y="185" font-size="12" text-anchor="middle" fill="currentColor">Det</text>
<text x="319.0" y="300" font-size="13" text-anchor="middle" fill="currentColor" font-style="italic">camera</text>
<line x1="319.0" y1="188" x2="319.0" y2="286" stroke="currentColor" stroke-width="1" stroke-opacity="0.7"/>
<rect x="302.0" y="172" width="34" height="17" rx="4" fill="#7ccf9a" fill-opacity="0.55"/>
<text x="319.0" y="185" font-size="12" text-anchor="middle" fill="currentColor">N</text>
<line x1="298.0" y1="148" x2="277.0" y2="170" stroke="currentColor" stroke-width="1" stroke-opacity="0.7"/>
<line x1="298.0" y1="148" x2="319.0" y2="170" stroke="currentColor" stroke-width="1" stroke-opacity="0.7"/>
<rect x="281.0" y="132" width="34" height="17" rx="4" fill="#9cc9ea" fill-opacity="0.55"/>
<text x="298.0" y="145" font-size="12" text-anchor="middle" fill="currentColor">NP</text>
<line x1="266.5" y1="108" x2="235.0" y2="130" stroke="currentColor" stroke-width="1" stroke-opacity="0.7"/>
<line x1="266.5" y1="108" x2="298.0" y2="130" stroke="currentColor" stroke-width="1" stroke-opacity="0.7"/>
<rect x="249.5" y="92" width="34" height="17" rx="4" fill="#eea66f" fill-opacity="0.55"/>
<text x="266.5" y="105" font-size="12" text-anchor="middle" fill="currentColor">PP</text>
<line x1="203.5" y1="68" x2="140.5" y2="90" stroke="currentColor" stroke-width="1" stroke-opacity="0.7"/>
<line x1="203.5" y1="68" x2="266.5" y2="90" stroke="currentColor" stroke-width="1" stroke-opacity="0.7"/>
<rect x="186.5" y="52" width="34" height="17" rx="4" fill="#9cc9ea" fill-opacity="0.55"/>
<text x="203.5" y="65" font-size="12" text-anchor="middle" fill="currentColor">VP</text>
<line x1="124.8" y1="28" x2="46.0" y2="50" stroke="currentColor" stroke-width="1" stroke-opacity="0.7"/>
<line x1="124.8" y1="28" x2="203.5" y2="50" stroke="currentColor" stroke-width="1" stroke-opacity="0.7"/>
<rect x="107.8" y="12" width="34" height="17" rx="4" fill="#9cc9ea" fill-opacity="0.55"/>
<text x="124.8" y="25" font-size="12" text-anchor="middle" fill="currentColor">S</text>
<text x="370.0" y="300" font-size="13" text-anchor="middle" fill="currentColor" font-style="italic">the</text>
<line x1="370.0" y1="108" x2="370.0" y2="286" stroke="currentColor" stroke-width="1" stroke-opacity="0.7"/>
<rect x="353.0" y="92" width="34" height="17" rx="4" fill="#7ccf9a" fill-opacity="0.55"/>
<text x="370.0" y="105" font-size="12" text-anchor="middle" fill="currentColor">Det</text>
<text x="412.0" y="300" font-size="13" text-anchor="middle" fill="currentColor" font-style="italic">rover</text>
<line x1="412.0" y1="108" x2="412.0" y2="286" stroke="currentColor" stroke-width="1" stroke-opacity="0.7"/>
<rect x="395.0" y="92" width="34" height="17" rx="4" fill="#7ccf9a" fill-opacity="0.55"/>
<text x="412.0" y="105" font-size="12" text-anchor="middle" fill="currentColor">N</text>
<line x1="391.0" y1="68" x2="370.0" y2="90" stroke="currentColor" stroke-width="1" stroke-opacity="0.7"/>
<line x1="391.0" y1="68" x2="412.0" y2="90" stroke="currentColor" stroke-width="1" stroke-opacity="0.7"/>
<rect x="374.0" y="52" width="34" height="17" rx="4" fill="#9cc9ea" fill-opacity="0.55"/>
<text x="391.0" y="65" font-size="12" text-anchor="middle" fill="currentColor">NP</text>
<text x="454.0" y="300" font-size="13" text-anchor="middle" fill="currentColor" font-style="italic">sees</text>
<line x1="454.0" y1="108" x2="454.0" y2="286" stroke="currentColor" stroke-width="1" stroke-opacity="0.7"/>
<rect x="437.0" y="92" width="34" height="17" rx="4" fill="#7ccf9a" fill-opacity="0.55"/>
<text x="454.0" y="105" font-size="12" text-anchor="middle" fill="currentColor">V</text>
<text x="496.0" y="300" font-size="13" text-anchor="middle" fill="currentColor" font-style="italic">the</text>
<line x1="496.0" y1="188" x2="496.0" y2="286" stroke="currentColor" stroke-width="1" stroke-opacity="0.7"/>
<rect x="479.0" y="172" width="34" height="17" rx="4" fill="#7ccf9a" fill-opacity="0.55"/>
<text x="496.0" y="185" font-size="12" text-anchor="middle" fill="currentColor">Det</text>
<text x="538.0" y="300" font-size="13" text-anchor="middle" fill="currentColor" font-style="italic">rock</text>
<line x1="538.0" y1="188" x2="538.0" y2="286" stroke="currentColor" stroke-width="1" stroke-opacity="0.7"/>
<rect x="521.0" y="172" width="34" height="17" rx="4" fill="#7ccf9a" fill-opacity="0.55"/>
<text x="538.0" y="185" font-size="12" text-anchor="middle" fill="currentColor">N</text>
<line x1="517.0" y1="148" x2="496.0" y2="170" stroke="currentColor" stroke-width="1" stroke-opacity="0.7"/>
<line x1="517.0" y1="148" x2="538.0" y2="170" stroke="currentColor" stroke-width="1" stroke-opacity="0.7"/>
<rect x="500.0" y="132" width="34" height="17" rx="4" fill="#9cc9ea" fill-opacity="0.55"/>
<text x="517.0" y="145" font-size="12" text-anchor="middle" fill="currentColor">NP</text>
<text x="580.0" y="300" font-size="13" text-anchor="middle" fill="currentColor" font-style="italic">with</text>
<line x1="580.0" y1="188" x2="580.0" y2="286" stroke="currentColor" stroke-width="1" stroke-opacity="0.7"/>
<rect x="563.0" y="172" width="34" height="17" rx="4" fill="#7ccf9a" fill-opacity="0.55"/>
<text x="580.0" y="185" font-size="12" text-anchor="middle" fill="currentColor">P</text>
<text x="622.0" y="300" font-size="13" text-anchor="middle" fill="currentColor" font-style="italic">the</text>
<line x1="622.0" y1="228" x2="622.0" y2="286" stroke="currentColor" stroke-width="1" stroke-opacity="0.7"/>
<rect x="605.0" y="212" width="34" height="17" rx="4" fill="#7ccf9a" fill-opacity="0.55"/>
<text x="622.0" y="225" font-size="12" text-anchor="middle" fill="currentColor">Det</text>
<text x="664.0" y="300" font-size="13" text-anchor="middle" fill="currentColor" font-style="italic">camera</text>
<line x1="664.0" y1="228" x2="664.0" y2="286" stroke="currentColor" stroke-width="1" stroke-opacity="0.7"/>
<rect x="647.0" y="212" width="34" height="17" rx="4" fill="#7ccf9a" fill-opacity="0.55"/>
<text x="664.0" y="225" font-size="12" text-anchor="middle" fill="currentColor">N</text>
<line x1="643.0" y1="188" x2="622.0" y2="210" stroke="currentColor" stroke-width="1" stroke-opacity="0.7"/>
<line x1="643.0" y1="188" x2="664.0" y2="210" stroke="currentColor" stroke-width="1" stroke-opacity="0.7"/>
<rect x="626.0" y="172" width="34" height="17" rx="4" fill="#9cc9ea" fill-opacity="0.55"/>
<text x="643.0" y="185" font-size="12" text-anchor="middle" fill="currentColor">NP</text>
<line x1="611.5" y1="148" x2="580.0" y2="170" stroke="currentColor" stroke-width="1" stroke-opacity="0.7"/>
<line x1="611.5" y1="148" x2="643.0" y2="170" stroke="currentColor" stroke-width="1" stroke-opacity="0.7"/>
<rect x="594.5" y="132" width="34" height="17" rx="4" fill="#eea66f" fill-opacity="0.55"/>
<text x="611.5" y="145" font-size="12" text-anchor="middle" fill="currentColor">PP</text>
<line x1="564.2" y1="108" x2="517.0" y2="130" stroke="currentColor" stroke-width="1" stroke-opacity="0.7"/>
<line x1="564.2" y1="108" x2="611.5" y2="130" stroke="currentColor" stroke-width="1" stroke-opacity="0.7"/>
<rect x="547.2" y="92" width="34" height="17" rx="4" fill="#9cc9ea" fill-opacity="0.55"/>
<text x="564.2" y="105" font-size="12" text-anchor="middle" fill="currentColor">NP</text>
<line x1="509.1" y1="68" x2="454.0" y2="90" stroke="currentColor" stroke-width="1" stroke-opacity="0.7"/>
<line x1="509.1" y1="68" x2="564.2" y2="90" stroke="currentColor" stroke-width="1" stroke-opacity="0.7"/>
<rect x="492.1" y="52" width="34" height="17" rx="4" fill="#9cc9ea" fill-opacity="0.55"/>
<text x="509.1" y="65" font-size="12" text-anchor="middle" fill="currentColor">VP</text>
<line x1="450.1" y1="28" x2="391.0" y2="50" stroke="currentColor" stroke-width="1" stroke-opacity="0.7"/>
<line x1="450.1" y1="28" x2="509.1" y2="50" stroke="currentColor" stroke-width="1" stroke-opacity="0.7"/>
<rect x="433.1" y="12" width="34" height="17" rx="4" fill="#9cc9ea" fill-opacity="0.55"/>
<text x="450.1" y="25" font-size="12" text-anchor="middle" fill="currentColor">S</text>
<text x="172" y="332" font-size="13" text-anchor="middle" fill="currentColor">PP attached to the VP</text>
<text x="517" y="332" font-size="13" text-anchor="middle" fill="currentColor">PP attached to the NP</text>
</svg>
<figcaption>The two parse trees of the camera sentence. Left: the PP modifies the VP (the camera is how the rover sees).
Right: the PP modifies the NP (a rock that has a camera). Under the toy grammar the left tree has probability
2.24 × 10⁻⁶ and the right one 1.68 × 10⁻⁶, whatever the nouns are.</figcaption>
</figure>

### The CKY algorithm

How do we find the best tree, or the total probability, without listing every tree? (The number of trees grows like
the **Catalan numbers**: with $k$ prepositional phrases after the object, the program counts 1, 2, 5, 14, 42, 132, 429
parses, a growth of nearly $4^k$. Kenneth Church and Ramesh Patil pointed this out in 1982.) The answer is dynamic
programming over **spans**: contiguous pieces of the sentence.

The **CKY algorithm**, found independently by John Cocke, Tadao Kasami (1965) and Daniel Younger (1967), fills a table
in which cell $[i, j]$ holds, for each nonterminal $A$, the best probability of any subtree rooted at $A$ that covers words
$i$ to $j - 1$:

1. **Length 1.** For each word $w_i$ and each rule $A \to w_i$, set $\text{best}[i, i+1, A] = P(A \to w_i)$.
2. **Longer spans**, in order of increasing length: for each span $[i, j]$, each split point $k$ with $i < k < j$, and
   each rule $A \to B\,C$, set
   $\text{best}[i, j, A] = \max\big(\text{best}[i, j, A],\ P(A \to B\,C)\,\text{best}[i, k, B]\,\text{best}[k, j, C]\big)$,
   storing the split and the children as a back-pointer.
3. **The answer** is $\text{best}[0, n, \text{S}]$; follow the back-pointers to build the tree.

**Correctness.** By induction on the span length $\ell = j - i$: $\text{best}[i, j, A]$ is the probability of the best
$A$-tree over words $i..j-1$. For $\ell = 1$, in CNF the only such trees are single lexical rules. For $\ell > 1$, the
root of any $A$-tree uses some binary rule $A \to B\,C$ and splits the span at some $k$; its probability is the rule's
times the two subtrees', and the best tree must use the best subtrees for its split (otherwise swapping in a better
subtree would improve it). Since both sub-spans are shorter, the induction hypothesis says the table already holds their
best values, and the algorithm maximises over all $k$ and all rules. $\square$

**Cost.** There are $O(n^2)$ spans, each with $O(n)$ split points, and for each split we try every binary rule: $O(n^3
|G|)$ time and $O(n^2 |N|)$ space, for $|G|$ rules and $|N|$ nonterminals. Cubic in sentence length, polynomial
instead of exponential.

**The inside algorithm.** Replace the max by a sum and the table holds the **inside probability**
$\beta[i, j, A] = P(\text{words } i..j-1 \mid A)$, the total probability of all $A$-trees over the span. Then
$\beta[0, n, \text{S}]$ is the probability of the sentence. This is the CKY counterpart of the HMM forward algorithm,
and the program uses it to compute the true grammar's perplexity on the test set: 6.04, the floor that the n-gram models
of 16.2 approach from above.

**The independence problem.** Both test sentences above get exactly the same probabilities, and the same attachment,
whether the PP is "with the camera" or "near the crater". In a PCFG the attachment decision is made by the rules
$\text{VP} \to \text{VP}\ \text{PP}$ (0.20) versus $\text{NP} \to \text{NP}\ \text{PP}$ (0.15), and the words inside are
chosen independently afterwards, so VP attachment always wins, with $0.20/(0.20 + 0.15) = 0.571$ of the probability.
Real attachment depends on the words ("sees ... with a camera" versus "the rock with the crack"). **Lexicalised PCFGs**
(Collins, 1997; Charniak, 1997) condition rules on the head words of phrases, and modern neural parsers condition on the
whole sentence. Today most practical systems use **dependency parsing**, which links each word directly to the word it
modifies rather than building phrases, but the dynamic programming ideas carry over.

## 16.4 Word vectors and meaning

*Level: intermediate.*

To a bag of words, "rover" and "robot" are as different as "rover" and "with": just different entries in a list. How can
a program know that some words are similar? The linguist Zellig Harris (1954) proposed the **distributional
hypothesis**: words that occur in similar contexts have similar meanings. J. R. Firth's (1957) phrase "You shall know a
word by the company it keeps" is the usual summary. This turns meaning into something we can count.

### From counts to vectors

1. **Count co-occurrences.** For each word $w$ and each context word $c$, count how often $c$ appears within two
   positions of $w$, giving a matrix $C$ with one row per word. Here we also record **which side** $c$ is on, so
   "the" just before a word and "the" just after are different columns.
2. **Reweight with PPMI.** Raw counts are dominated by frequent words like "the", which occur near everything. The
   **pointwise mutual information** $\mathrm{PMI}(w, c) = \log\frac{P(w, c)}{P(w)P(c)}$ (Church and Hanks, 1990) measures
   how much more often $w$ and $c$ occur together than if they were independent. Negative values are unreliable for
   rare pairs, so we use **positive** PMI, $\mathrm{PPMI} = \max(0, \mathrm{PMI})$.
3. **Compress with the SVD.** The singular value decomposition $M = U S V^\top$
   ([Machine learning, Chapter 3](../machine-learning/03-The-Math-Toolkit.md) and
   [Chapter 14](../machine-learning/14-Dimensionality-Reduction.md)) gives the best rank-$k$ approximation of the
   matrix. The first $k$ columns of $U S$ are $k$-dimensional **word vectors**, and similarity is the **cosine** of the
   angle between them. Applied to word-document matrices this was **latent semantic analysis** (Deerwester et al.,
   1990).

```python
--8<-- "books/ai/ch16_vectors.py"
```

```
34 words, 70 context columns (left and right); top singular values [12.87  7.37  6.34  4.96  3.82  2.94]
  nearest to rover : rock 0.99, robot 0.99, dune 0.99, crater 0.99
  nearest to sees  : finds 0.97, follows 0.97, photographs 0.97, studies 0.87
  nearest to red   : small 0.99, old 0.98, dusty 0.96, bright 0.84
  nearest to with  : behind 0.99, on 0.99, near 0.99, sees 0.72
  nearest to stops : rolls 1.00, turns 1.00, waits 0.98, finds 0.79
  nearest to drills: tracks 0.99, samples 0.94, follows 0.83, photographs 0.81
without left/right distinction, nearest to with: sees 0.99, follows 0.98, finds 0.97, photographs 0.96

raw count of 'the' near rover 2316 and near sees 910 ; PPMI 0.49 and 0.441  ('the' is everywhere, so PPMI discounts it)
coordinates in SVD dimensions 2 and 3 (for the figure):
  rover      1.790  -0.546
  rock       1.686  -0.612
  crater     1.782  -0.515
  dune       1.514  -0.442
  sees      -0.473  -0.499
  finds     -0.532  -0.532
  follows   -0.269  -0.481
  red        1.592   1.248
  small      1.701   1.296
  dusty      1.638   1.363
  with      -1.513   1.172
  near      -1.561   1.207
  on        -1.407   1.103
  stops     -0.272  -1.640
  waits     -0.115  -1.408
  drills     0.280  -0.549
  tracks     0.403  -0.600
```

<figure class="mars-fig" markdown="0">
<svg viewBox="0 0 640 280" role="img" aria-label="Scatter plot of words in two SVD dimensions. Nouns cluster at the right middle, adjectives at the top right, prepositions at the top left, transitive verbs in the middle left, intransitive verbs at the bottom, and the noun-or-verb words drills and tracks between the nouns and the verbs.">
<line x1="40" y1="250" x2="600" y2="250" stroke="currentColor" stroke-width="0.8" stroke-opacity="0.5"/>
<line x1="40" y1="250" x2="40" y2="20" stroke="currentColor" stroke-width="0.8" stroke-opacity="0.5"/>
<circle cx="544.7" cy="164.0" r="4.5" fill="#9cc9ea" stroke="currentColor" stroke-width="0.8"/>
<circle cx="530.3" cy="168.0" r="4.5" fill="#9cc9ea" stroke="currentColor" stroke-width="0.8"/>
<circle cx="543.6" cy="162.1" r="4.5" fill="#9cc9ea" stroke="currentColor" stroke-width="0.8"/>
<circle cx="506.4" cy="157.7" r="4.5" fill="#9cc9ea" stroke="currentColor" stroke-width="0.8"/>
<circle cx="230.4" cy="161.2" r="4.5" fill="currentColor" stroke="currentColor" stroke-width="0.8"/>
<circle cx="222.2" cy="163.2" r="4.5" fill="currentColor" stroke="currentColor" stroke-width="0.8"/>
<circle cx="258.8" cy="160.1" r="4.5" fill="currentColor" stroke="currentColor" stroke-width="0.8"/>
<circle cx="517.2" cy="55.3" r="4.5" fill="#7ccf9a" stroke="currentColor" stroke-width="0.8"/>
<circle cx="532.4" cy="52.4" r="4.5" fill="#7ccf9a" stroke="currentColor" stroke-width="0.8"/>
<circle cx="523.6" cy="48.3" r="4.5" fill="#7ccf9a" stroke="currentColor" stroke-width="0.8"/>
<circle cx="86.0" cy="59.9" r="4.5" fill="#eea66f" stroke="currentColor" stroke-width="0.8"/>
<circle cx="79.3" cy="57.8" r="4.5" fill="#eea66f" stroke="currentColor" stroke-width="0.8"/>
<circle cx="100.7" cy="64.1" r="4.5" fill="#eea66f" stroke="currentColor" stroke-width="0.8"/>
<circle cx="258.3" cy="230.3" r="4.5" fill="currentColor" stroke="currentColor" stroke-width="0.8"/>
<circle cx="280.1" cy="216.2" r="4.5" fill="currentColor" stroke="currentColor" stroke-width="0.8"/>
<rect x="331.0" y="160.2" width="8" height="8" fill="#eea66f" stroke="currentColor" stroke-width="0.8"/>
<rect x="348.1" y="163.3" width="8" height="8" fill="#eea66f" stroke="currentColor" stroke-width="0.8"/>
<text x="525" y="188" font-size="12" text-anchor="middle" fill="currentColor">rover, rock, crater, dune</text>
<text x="525" y="82" font-size="12" text-anchor="middle" fill="currentColor">red, small, dusty</text>
<text x="60" y="90" font-size="12" fill="currentColor">with, near, on</text>
<text x="240" y="142" font-size="12" text-anchor="middle" fill="currentColor">sees, finds, follows</text>
<text x="296" y="230" font-size="12" fill="currentColor">stops, waits</text>
<text x="344" y="194" font-size="12" text-anchor="middle" fill="currentColor">drills, tracks</text>
<text x="320" y="272" font-size="12" text-anchor="middle" fill="currentColor">SVD dimension 2 (horizontal) and dimension 3 (vertical)</text>
</svg>
<figcaption>Word vectors from PPMI and the SVD, in two of their dimensions. Nobody told the program about nouns,
verbs or adjectives; the classes emerge from the contexts. The noun-or-verb words (squares) sit between the nouns and
the verbs: one vector has to stand for both uses.</figcaption>
</figure>

Three lessons from the output:

- **Classes emerge from contexts.** Nouns, transitive verbs, intransitive verbs, adjectives and prepositions form
  separate groups, learned only from which words appear around which.
- **What counts as context matters.** Without the left/right distinction, "with" looks like a verb: both prepositions
  and transitive verbs sit between a noun phrase and another noun phrase. Keeping the side separates them. Different
  context definitions capture different kinds of similarity (narrow windows tend to give syntactic similarity, wide ones
  topical similarity).
- **One vector per word mixes its senses.** "drills" is placed between the nouns and the verbs. Contextual embeddings
  (16.5) fix this by giving each **occurrence** its own vector.

### Prediction-based vectors

**word2vec** (Mikolov et al., 2013) learns vectors by training a tiny network to predict context words from a word
(skip-gram) or the reverse; **GloVe** (Pennington, Socher and Manning, 2014) fits vectors to log co-occurrence counts
directly. Both are built in [Machine learning, Chapter 18](../machine-learning/18-Sequence-Models.md), with the famous
analogy arithmetic (king minus man plus woman lands near queen). The two families are closer than they look: Omer Levy
and Yoav Goldberg (2014) showed that skip-gram with negative sampling implicitly factorises a shifted PMI matrix, the
same object we just built and factorised by hand. Because the vectors summarise real text, they also absorb its
statistical regularities, including stereotyped associations, which has been measured directly (Bolukbasi et al., 2016;
Caliskan, Bryson and Narayanan, 2017); this is a property of the data that any downstream system inherits.

## 16.5 Neural language models to transformers

*Level: intermediate.*

An n-gram model treats "the dusty rover" and "the dusty robot" as unrelated events: learning one teaches it nothing about
the other. Yoshua Bengio, Réjean Ducharme, Pascal Vincent and Christian Jauvin's "A neural probabilistic language model"
(2003) fixed this by combining the last two ideas: represent each word by a learned vector, and predict the next word
from the vectors of the previous ones with a neural network.

- Look up an **embedding** (a vector of, say, 12 numbers) for each of the previous $n - 1$ words and concatenate them.
- Pass the result through a hidden layer with a nonlinearity (tanh).
- A **softmax** layer turns scores into a probability for every word in the vocabulary.
- Train everything, embeddings included, by gradient descent on the cross-entropy, which is the log of the perplexity.

Similar words get similar embeddings because that helps prediction, and then a context never seen as such still gets a
sensible prediction from the similar contexts that were seen. Longer contexts no longer blow up the number of
parameters: each extra word adds one embedding block to the input, not a factor of $V$ to a table.

```python
--8<-- "books/ai/ch16_neural_lm.py"
```

```
38368 training predictions, vocabulary 36, context 4 words, embedding size 12, hidden 64
epoch  train perplexity  test perplexity
    1             6.551            6.563
    2             6.505            6.520
    4             6.428            6.489
    8             6.374            6.422
learned embedding, nearest to rover: dune, crater, camera
learned embedding, nearest to sees: photographs, follows, finds
learned embedding, nearest to with: near, on, behind
learned embedding, nearest to red: small, dusty, bright
```

With a four-word context the network reaches a test perplexity of 6.42, against 7.34 for the best n-gram model and the
floor of 6.04. A 5-gram table would be hopeless on 5000 sentences, but the network handles four words of context easily.
And its embeddings, learned only to predict, group words into the same classes the PPMI vectors found.

### From fixed windows to transformers

The fixed window is still a limit: the network sees four words and no more. The next steps, each built from scratch in the
Machine learning book, removed it.

- **Recurrent networks** (Elman, 1990; as language models, Mikolov et al., 2010) carry a hidden state along the
  sentence, so in principle the prediction can depend on everything before. **LSTMs** (Hochreiter and Schmidhuber, 1997)
  made long dependencies trainable. See [Machine learning, Chapter 18](../machine-learning/18-Sequence-Models.md).
- **Sequence-to-sequence** models (Sutskever, Vinyals and Le, 2014) encode a source sentence into a vector and decode a
  target sentence from it; **attention** (Bahdanau, Cho and Bengio, 2014) lets the decoder look back at every source
  position instead of squeezing everything into one vector.
- **Transformers** ("Attention Is All You Need", Vaswani et al., 2017) drop recurrence and use attention throughout, so
  every position can look at every other in one step, and training parallelises across the sequence. See
  [Machine learning, Chapter 19](../machine-learning/19-Transformers.md), which also builds the byte-pair encoding
  tokeniser (Sennrich, Haddow and Birch, 2016) that splits rare words into common pieces and so removes the problem of
  unknown words.
- **Contextual embeddings and pretraining.** ELMo (Peters et al., 2018) took word vectors from the hidden states of a
  language model, so each occurrence of "drills" gets its own vector. BERT (Devlin et al., 2019) pretrained a
  transformer to fill in masked words and showed that fine-tuning it improved results across a wide range of tasks.
  GPT (Radford et al., 2018) pretrained a transformer as a next-word predictor. Scaling that recipe is the subject of
  [Chapter 17](17-Large-Language-Models.md).

The old pieces of this chapter did not disappear; they became the questions that the new models answer implicitly.
A transformer has no explicit tagger or parser, yet probing studies find that its internal representations carry
information about parts of speech and syntactic structure (for example Hewitt and Manning, 2019, recovered parse-tree
distances from BERT's vectors with a linear map).

## 16.6 Machine translation history: rules, statistics (IBM models 1990s), neural

*Level: intermediate to advanced.*

### Rules

In 1949 Warren Weaver, a mathematician at the Rockefeller Foundation, circulated a memorandum suggesting that
translation might be treated like code-breaking, with statistics. In January 1954 Georgetown University and IBM
demonstrated a system that translated a set of carefully chosen Russian sentences into English with a small vocabulary
and a handful of rules, and predictions of fully automatic translation within a few years followed. Progress was much
slower than promised, and the US government's ALPAC report (1966) concluded that machine translation was slower, less
accurate and more expensive than human translation; funding in the United States fell sharply afterwards.

Rule-based systems continued, especially in Europe and Canada. They are usually described by the **Vauquois triangle**
(Bernard Vauquois, 1968): **direct** systems replace words with dictionary lookups and some local reordering;
**transfer** systems parse the source, map the source structure to a target structure with transfer rules, and generate;
**interlingua** systems analyse the source into a language-independent meaning representation and generate from that.
The higher you go, the less you need per language pair, and the harder the analysis. Such systems needed armies of
linguists writing rules, and broke on whatever the rules did not foresee.

### Statistics: the IBM models

At IBM's Thomas J. Watson Research Center, Peter Brown, Stephen Della Pietra, Vincent Della Pietra, Robert Mercer and
colleagues, members of the speech recognition group led by Frederick Jelinek, took Weaver's suggestion literally (Brown et
al., 1990, 1993). They learned translation from a large collection of parallel sentences, the proceedings of the
Canadian parliament in English and French, using the **noisy channel** model: to translate a foreign sentence $f$
into English, find

$$
\hat e = \arg\max_e P(e \mid f) = \arg\max_e P(f \mid e)\, P(e),
$$

by Bayes' rule. $P(e)$ is a language model of English (16.2), which takes care of fluency; $P(f \mid e)$ is a
**translation model**, which takes care of faithfulness. The translation model is learned from parallel text without
anyone saying which word translates which: the **word alignment** is a hidden variable.

**IBM Model 1**, the simplest of their five models, says: to generate a foreign sentence of length $m$ from an English
sentence $e_0 e_1 \dots e_l$ (where $e_0$ is a special NULL word, for foreign words with no English counterpart), for
each foreign position pick an English position uniformly at random and generate the foreign word from that English
word with probability $t(f \mid e)$. So

$$
P(f \mid e) = \frac{\epsilon}{(l+1)^m} \prod_{j=1}^{m} \sum_{i=0}^{l} t(f_j \mid e_i),
$$

with $\epsilon$ a length probability. The parameters are the **translation table** $t$. If we knew the alignments,
we would count; since we do not, we use **EM** ([Machine learning, Chapter 13](../machine-learning/13-Clustering.md)):

- **E-step.** For each sentence pair and each foreign word $f_j$, the posterior probability that it was generated by
  English word $e_i$ is $t(f_j \mid e_i)/\sum_{i'} t(f_j \mid e_{i'})$ (because the alignment choices for different
  positions are independent under Model 1). Add these fractions to expected counts $c(f, e)$.
- **M-step.** Set $t(f \mid e) = c(f, e)/\sum_{f'} c(f', e)$.

Model 1's log-likelihood is a concave function of $t$, so EM reaches a global maximum from any starting point with all
entries positive (though the maximum need not be unique; Toutanova and Galley, 2011). The higher IBM models add word
order (alignment probabilities depending on positions) and **fertility** (one word generating several), and are
initialised from Model 1.

The program applies the same model with the roles exchanged, German as the generating side (with its NULL word) and
English as the generated side, so it learns $t(e \mid f)$, on six German-English sentence pairs, in the spirit of the classic textbook example
in Koehn's *Statistical Machine Translation* (2010).

```python
--8<-- "books/ai/ch16_ibm1.py"
```

```
iteration  log-likelihood   t(house|haus)  t(the|das)  t(book|buch)  t(small|klein)  t(is|ist)
        0        -35.0264          0.1429      0.1429        0.1429          0.1429     0.1429
        1        -28.1248          0.3235      0.3043        0.4062          0.2500     0.2500
        2        -26.5443          0.4969      0.3962        0.5986          0.3659     0.3159
        3        -25.3644          0.6568      0.4931        0.7431          0.4715     0.3847
        5        -24.0352          0.8592      0.6502        0.9035          0.6381     0.5258
       10        -23.1415          0.9859      0.8141        0.9941          0.8642     0.7989
       20        -22.9178          0.9998      0.8907        1.0000          0.9797     0.9779

most probable alignment of 'the house is small' to 'NULL das haus ist klein':
  the <- das, house <- haus, is <- ist, small <- klein
translation table rows (P(e | f) above 0.01):
  das  : the 0.891, is 0.108
  ein  : a 1.000
  alt  : old 0.989
  NULL : the 0.631, book 0.148, house 0.143, is 0.076
```

At the start every English word is equally likely to come from every German word (1/7). Nothing in the data says
"haus" means "house", but "house" occurs exactly in the sentences that contain "haus", and EM pulls the probability
together: after 20 iterations $t(\text{house} \mid \text{haus}) = 0.9998$. The log-likelihood rises at every iteration,
as EM guarantees. The NULL word has soaked up some probability for "the" (it appears in every sentence, so NULL can
explain it), a known quirk of Model 1.

<figure class="mars-fig" markdown="0">
<svg viewBox="0 0 640 180" role="img" aria-label="Word alignment learned by IBM Model 1: NULL das haus ist klein on top, the house is small below, with lines from the to das, house to haus, is to ist and small to klein. NULL has no line.">
<text x="80" y="45" font-size="15" text-anchor="middle" fill="currentColor" font-style="italic">NULL</text>
<text x="200" y="45" font-size="15" text-anchor="middle" fill="currentColor" font-style="italic">das</text>
<text x="320" y="45" font-size="15" text-anchor="middle" fill="currentColor" font-style="italic">haus</text>
<text x="440" y="45" font-size="15" text-anchor="middle" fill="currentColor" font-style="italic">ist</text>
<text x="560" y="45" font-size="15" text-anchor="middle" fill="currentColor" font-style="italic">klein</text>
<text x="200" y="145" font-size="15" text-anchor="middle" fill="currentColor">the</text>
<text x="320" y="145" font-size="15" text-anchor="middle" fill="currentColor">house</text>
<text x="440" y="145" font-size="15" text-anchor="middle" fill="currentColor">is</text>
<text x="560" y="145" font-size="15" text-anchor="middle" fill="currentColor">small</text>
<line x1="200" y1="54" x2="200" y2="126" stroke="#9cc9ea" stroke-width="4"/>
<line x1="320" y1="54" x2="320" y2="126" stroke="#7ccf9a" stroke-width="4"/>
<line x1="440" y1="54" x2="440" y2="126" stroke="#eea66f" stroke-width="4"/>
<line x1="560" y1="54" x2="560" y2="126" stroke="#9cc9ea" stroke-width="4"/>
<line x1="80" y1="54" x2="190" y2="126" stroke="currentColor" stroke-width="1" stroke-dasharray="3 4" stroke-opacity="0.6"/>
<text x="120" y="100" font-size="11" text-anchor="end" fill="currentColor">P = 0.63</text>
<text x="320" y="172" font-size="12" text-anchor="middle" fill="currentColor">German above, English below; the dashed line is NULL's competing claim on "the"</text>
</svg>
<figcaption>The alignment that IBM Model 1 learned for the first sentence pair, without ever being shown one. Each
English word is linked to the German word that most probably generated it; for "the", das (0.89) beats NULL (0.63).</figcaption>
</figure>

### Phrases, BLEU, and the neural turn

Word-by-word models translate idioms and word order badly. **Phrase-based** statistical translation (Koehn, Och and
Marcu, 2003) learned translation tables for multi-word phrases extracted from word alignments, combined with a language
model and a reordering model by a weighted log-linear model (Och and Ney, 2002), and searched for the best output with a
beam search. Open-source toolkits such as Moses (Koehn et al., 2007) made it the standard approach for about a decade.

Progress needed a cheap, automatic score. **BLEU** (Papineni, Roukos, Ward and Zhu, 2002) compares a candidate
translation with one or more human references by the **modified n-gram precisions** $p_n$ for $n = 1$ to 4 (the fraction
of the candidate's n-grams that occur in a reference, each counted at most as often as it occurs there), combined as a
geometric mean and multiplied by a **brevity penalty** $BP = \min(1, e^{1 - r/c})$ for a candidate of length $c$ shorter
than the reference length $r$:

$$
\text{BLEU} = BP \cdot \exp\Big(\frac14 \sum_{n=1}^{4} \log p_n\Big).
$$

BLEU correlates with human judgements when comparing systems over a whole test set, but it rewards surface overlap,
not meaning; a correct paraphrase can score badly. Exercise 10 implements it.

Neural networks then replaced the whole pipeline. Encoder-decoder networks (Kalchbrenner and Blunsom, 2013; Sutskever,
Vinyals and Le, 2014; Cho et al., 2014) translated whole sentences with one network; attention (Bahdanau, Cho and Bengio,
2014) fixed their trouble with long sentences; and the transformer (Vaswani et al., 2017) was introduced on translation
tasks, reporting better BLEU scores than earlier models on the WMT 2014 English-German and English-French benchmarks at
a fraction of the training cost. Alignment, phrase tables and separate language models disappeared into one network
trained end to end on parallel text, and today the same networks, scaled up and trained on many languages at once,
translate as one task among many.

## In practice

- For text classification, start with a bag of words (or subword units) and logistic regression; it is a strong
  baseline and fast. Libraries: scikit-learn for classical models; NLTK and spaCy for tokenising, tagging and parsing;
  KenLM for very large n-gram models.
- Language models, taggers, parsers and translators are now mostly neural, usually starting from a pretrained
  transformer (for example through the Hugging Face Transformers library) and fine-tuned for the task.
- Always measure on held-out text from the same kind of source as the real use; a model's perplexity or accuracy on a
  different genre can be much worse.

## Check yourself

??? question "1. Give the two parse trees for 'ada sees ben with the camera' under the toy grammar, and compute the ratio of their probabilities. Why does the ratio not depend on the words?"
    VP attachment: $\text{S} \to \text{NP VP}$; $\text{VP} \to \text{VP PP}$; the inner $\text{VP} \to \text{V NP}$
    covers "sees ben"; the PP is "with the camera". NP attachment: $\text{S} \to \text{NP VP}$;
    $\text{VP} \to \text{V NP}$; that NP is $\text{NP} \to \text{NP PP}$, "ben" plus the PP. Both trees contain
    $\text{S} \to \text{NP VP}$, one $\text{VP} \to \text{V NP}$, $\text{PP} \to \text{P NP}$ and the same lexical
    rules for every word. The only difference is one rule: $\text{VP} \to \text{VP PP}$ (0.20) in the first tree,
    $\text{NP} \to \text{NP PP}$ (0.15) in the second. So the ratio is $0.20 : 0.15 = 4 : 3$, and the VP tree has
    $4/7 = 0.571$ of the total. The words are generated by the same lexical rules in both trees, so they cancel: a
    PCFG cannot use words to decide attachment.

??? question "2. A corpus has the three sentences 'a rover stops', 'a rock stops', 'the rover waits'. Compute the maximum likelihood bigram estimates P(rover | a), P(stops | rover) and P(</s> | waits), and the probability of 'the rock stops'."
    Counts (with `<s>` and `</s>`): $C(\text{a}) = 2$, $C(\text{a rover}) = 1$, so $P(\text{rover} \mid \text{a}) = 0.5$.
    $C(\text{rover}) = 2$ and $C(\text{rover stops}) = 1$: 0.5. $C(\text{waits}) = 1$, $C(\text{waits </s>}) = 1$: 1.
    For "the rock stops": $P(\text{the} \mid \texttt{<s>}) = 1/3$, $P(\text{rock} \mid \text{the}) = 0/1 = 0$ (the
    bigram "the rock" never occurred). So the probability is 0, although the sentence is perfectly good: the zero
    problem that smoothing exists to fix.

??? question "3. Prove that a model which predicts every one of V words (including the end symbol) with probability 1/V has perplexity exactly V on any text."
    Every token contributes $-\log_2(1/V) = \log_2 V$ bits, so the cross-entropy is $\log_2 V$ and the perplexity is
    $2^{\log_2 V} = V$. This is why perplexity reads as an "effective number of choices": a model with perplexity 7.5 on
    our test set is as uncertain as a uniform choice among 7.5 words, against 35 for the uniform model.

??? question "4. With add-k smoothing and vocabulary V, show that the smoothed bigram probabilities P(w | u) sum to 1 over w. What happens to P(w | u) as k grows very large?"
    $\sum_w (C(u\,w) + k)/(C(u) + kV) = (C(u) + kV)/(C(u) + kV) = 1$, using $\sum_w C(u\,w) = C(u)$. As $k \to \infty$,
    $P(w \mid u) \to k/(kV) = 1/V$: the counts are swamped and the model becomes uniform. Small $k$ trusts the data, large
    $k$ trusts the prior; the right balance depends on how much data there is, as the table in 16.2 shows.

??? question "5. In the HMM tagger, explain exactly why 'the drills tracks the dune' is tagged DET N V DET N, using the transition probabilities of the toy grammar."
    "drills" can be N or V. It follows "the" (DET). In the grammar a determiner is followed by N or ADJ only, so the
    estimated $P(\text{V} \mid \text{DET})$ is essentially zero (only smoothing), and the N reading wins despite
    "drills" being a verb slightly more often overall. "tracks" follows an N. After a noun the grammar allows V (start
    of the VP) or P (a PP), never N, so $P(\text{N} \mid \text{N}) \approx 0$ and "tracks" is tagged V. The Viterbi
    algorithm finds this jointly, but here each decision is forced by its left neighbour.

??? question "6. Fill the CKY chart for 'ada sees ben' (words 0, 1, 2) with the toy grammar. Which cells are non-empty, and what is the probability of the sentence?"
    Length 1: [0,1] has NP ("ada", 0.05); [1,2] has V ("sees", 0.25); [2,3] has NP ("ben", 0.05).
    Length 2: [0,2] = NP V: no rule has right side "NP V", so empty. [1,3] = V NP: $\text{VP} \to \text{V NP}$ (0.55),
    giving $0.55 \cdot 0.25 \cdot 0.05 = 0.006875$.
    Length 3: [0,3] with split 1: NP [0,1] and VP [1,3]: $\text{S} \to \text{NP VP}$ (1.0), giving
    $1.0 \cdot 0.05 \cdot 0.006875 = 3.44 \times 10^{-4}$. Split 2 needs something in [0,2], which is empty. There is one
    tree, so the sentence probability is $3.44 \times 10^{-4}$.

??? question "7. Compute PMI(w, c) when w occurs in 10 percent of the word-context pairs, c in 20 percent, and the pair (w, c) in 5 percent. Then in 1 percent."
    $\mathrm{PMI} = \log\frac{0.05}{0.1 \cdot 0.2} = \log 2.5 = 0.916$ (natural log). They occur together 2.5 times
    as often as independence predicts. With 1 percent: $\log\frac{0.01}{0.02} = \log 0.5 = -0.693$, so PPMI sets it to
    0: less often than chance, and for rare words such negative estimates are unreliable.

??? question "8. Run two EM iterations of IBM Model 1 by hand on the pairs (das haus, the house) and (das buch, the book), without NULL, starting from uniform t(e | f) = 1/3."
    Iteration 1. In each pair each English word splits its count equally between the two German words (all $t$ equal).
    Expected counts: das: the 1, house 0.5, book 0.5 (total 2); haus: the 0.5, house 0.5 (total 1); buch: the 0.5, book
    0.5. So $t(\text{the} \mid \text{das}) = 0.5$, $t(\text{house} \mid \text{das}) = t(\text{book} \mid \text{das}) = 0.25$,
    $t(\text{the} \mid \text{haus}) = t(\text{house} \mid \text{haus}) = 0.5$, and the same for buch.
    Iteration 2, pair 1. "the": $t$ from das and haus both 0.5, so split 1/2, 1/2. "house": 0.25 from das, 0.5 from
    haus, so 1/3 to das and 2/3 to haus. Pair 2 is symmetric. Counts: das: the 1, house 1/3, book 1/3 (total 5/3), so
    $t(\text{the} \mid \text{das}) = 0.6$, $t(\text{house} \mid \text{das}) = 0.2$. haus: the 1/2, house 2/3 (total 7/6),
    so $t(\text{house} \mid \text{haus}) = 4/7 = 0.571$ and $t(\text{the} \mid \text{haus}) = 3/7 = 0.429$. "das" is
    becoming "the" and "haus" "house", because "the" occurs with das in both pairs and with haus in only one.

??? question "9. Why does the trigram model with add-0.01 smoothing do worse than the bigram with 50 training sentences but nearly as well with 5000? Relate your answer to the bias-variance trade-off."
    With 50 sentences most trigram contexts in the test set were never seen, so the trigram estimate is the smoothed
    near-uniform $1/V$ for them: high variance (estimates from tiny counts) and, after smoothing, high bias towards
    uniform. The bigram's contexts are much better covered. With 5000 sentences most trigram contexts have been seen many
    times, so the extra context can be used. More context means lower bias but more parameters to estimate, hence higher
    variance; the best order grows with the data ([Machine learning, Chapter
    8](../machine-learning/08-Overfitting-and-Regularization.md) has the general trade-off). Interpolation picks the
    balance automatically.

??? question "10. Write the code: BLEU with clipped n-gram precisions for n = 1 to 4 and the brevity penalty, for one or more references. Score 'the rover sees the red rock near the crater' against 'the rover sees a red rock near the crater', and 'the the the the' against 'the rover sees the rock'."
    ```python
    import math
    from collections import Counter


    def bleu(candidate, references, max_n=4):
        cand = candidate.split()
        refs = [r.split() for r in references]
        log_p = 0.0
        for n in range(1, max_n + 1):
            grams = Counter(tuple(cand[i:i + n]) for i in range(len(cand) - n + 1))
            best_ref = Counter()
            for r in refs:                                  # clip each n-gram by its largest count in a reference
                for g, c in Counter(tuple(r[i:i + n]) for i in range(len(r) - n + 1)).items():
                    best_ref[g] = max(best_ref[g], c)
            clipped = sum(min(c, best_ref[g]) for g, c in grams.items())
            total = max(1, sum(grams.values()))
            print(f"  {n}-gram precision {clipped}/{total}")
            if clipped == 0:
                return 0.0
            log_p += math.log(clipped / total) / max_n
        r = min((abs(len(x) - len(cand)), len(x)) for x in refs)[1]   # closest reference length
        bp = 1.0 if len(cand) > r else math.exp(1 - r / len(cand))
        return bp * math.exp(log_p)


    print("BLEU =", round(bleu("the rover sees the red rock near the crater",
                               ["the rover sees a red rock near the crater"]), 4))
    print("BLEU =", round(bleu("the the the the", ["the rover sees the rock"]), 4))
    ```
    Output:
    ```
      1-gram precision 8/9
      2-gram precision 6/8
      3-gram precision 4/7
      4-gram precision 2/6
    BLEU = 0.5969
      1-gram precision 2/4
      2-gram precision 0/3
    BLEU = 0.0
    ```
    One wrong word costs a lot: it breaks two bigrams, three trigrams and four 4-grams, so BLEU drops to 0.60. Clipping
    stops "the the the the" from scoring 4/4 on unigrams (the reference has "the" only twice), and with no matching
    bigram its BLEU is 0. (Real BLEU is computed over a whole test set, summing counts over sentences before dividing,
    and implementations add smoothing for short sentences.)

## What you learned

- Language is ambiguous at every level (words, structure, meaning, reference) and sparse (Zipf's law); every method
  must choose among analyses and handle unseen events.
- A language model factors sentence probability by the chain rule; n-grams cut the history, smoothing (add-k,
  interpolation, Kneser-Ney) handles zeros, and perplexity on held-out text measures quality, bounded below by the true
  distribution.
- Tagging is HMM decoding: transitions between tags resolve ambiguous words. Parsing with a PCFG is dynamic
  programming over spans (CKY, $O(n^3|G|)$), with the inside algorithm giving sentence probabilities; plain PCFGs cannot
  use words to resolve attachment.
- The distributional hypothesis turns meaning into counts: PPMI and the SVD give word vectors in which syntactic classes
  emerge, and what counts as context decides what similarity means.
- Neural language models share statistical strength through embeddings and scale to longer contexts; recurrent
  networks, attention and transformers removed the fixed window and led to pretrained models.
- Machine translation went from hand-written rules to statistical models learned by EM from parallel text (IBM Model 1,
  phrase-based systems, BLEU) to end-to-end neural networks.

**Next:** [Chapter 17](17-Large-Language-Models.md) scales the next-token predictor up: pretraining, sampling,
instruction tuning, retrieval and tools, and what such models can and cannot do.

## Further reading

- D. Jurafsky and J. H. Martin, *Speech and Language Processing*, 3rd ed. draft: n-grams and smoothing, POS tagging,
  CKY and PCFGs, vector semantics, neural language models and machine translation.
- C. D. Manning and H. Schütze, *Foundations of Statistical Natural Language Processing*, 1999.
- S. Russell and P. Norvig, *Artificial Intelligence: A Modern Approach*, 4th ed., 2020: chapters 23 and 24.
- C. E. Shannon, "A mathematical theory of communication", *Bell System Technical Journal* 27, 1948.
- S. F. Chen and J. Goodman, "An empirical study of smoothing techniques for language modeling", Harvard technical
  report TR-10-98, 1998; R. Kneser and H. Ney, "Improved backing-off for m-gram language modeling", ICASSP 1995;
  S. M. Katz, "Estimation of probabilities from sparse data for the language model component of a speech recognizer",
  *IEEE Transactions on Acoustics, Speech, and Signal Processing* 35, 1987.
- M. P. Marcus, B. Santorini and M. A. Marcinkiewicz, "Building a large annotated corpus of English: the Penn
  Treebank", *Computational Linguistics* 19, 1993; T. Brants, "TnT: a statistical part-of-speech tagger", ANLP 2000.
- T. Kasami, "An efficient recognition and syntax-analysis algorithm for context-free languages", technical report,
  1965; D. H. Younger, "Recognition and parsing of context-free languages in time n³", *Information and Control* 10,
  1967; K. Church and R. Patil, "Coping with syntactic ambiguity, or how to put the block in the box on the table",
  *American Journal of Computational Linguistics* 8, 1982; M. Collins, "Three generative, lexicalised models for
  statistical parsing", ACL 1997.
- Z. Harris, "Distributional structure", *Word* 10, 1954; K. W. Church and P. Hanks, "Word association norms, mutual
  information, and lexicography", *Computational Linguistics* 16, 1990; S. Deerwester et al., "Indexing by latent
  semantic analysis", *Journal of the American Society for Information Science* 41, 1990; O. Levy and Y. Goldberg,
  "Neural word embedding as implicit matrix factorization", NeurIPS 2014.
- Y. Bengio, R. Ducharme, P. Vincent and C. Jauvin, "A neural probabilistic language model", *Journal of Machine
  Learning Research* 3, 2003; T. Mikolov et al., "Recurrent neural network based language model", Interspeech 2010.
- A. Vaswani et al., "Attention Is All You Need", NeurIPS 2017; J. Devlin, M.-W. Chang, K. Lee and K. Toutanova,
  "BERT: pre-training of deep bidirectional transformers for language understanding", NAACL 2019; M. E. Peters et al.,
  "Deep contextualized word representations", NAACL 2018; J. Hewitt and C. D. Manning, "A structural probe for finding
  syntax in word representations", NAACL 2019.
- P. F. Brown, S. A. Della Pietra, V. J. Della Pietra and R. L. Mercer, "The mathematics of statistical machine
  translation: parameter estimation", *Computational Linguistics* 19, 1993; P. Koehn, F. J. Och and D. Marcu,
  "Statistical phrase-based translation", NAACL 2003; P. Koehn, *Statistical Machine Translation*, 2010;
  K. Toutanova and M. Galley, "Why initialization matters for IBM Model 1: multiple optima and non-strict convexity",
  ACL 2011.
- K. Papineni, S. Roukos, T. Ward and W.-J. Zhu, "BLEU: a method for automatic evaluation of machine translation",
  ACL 2002; I. Sutskever, O. Vinyals and Q. V. Le, "Sequence to sequence learning with neural networks", NeurIPS 2014;
  D. Bahdanau, K. Cho and Y. Bengio, "Neural machine translation by jointly learning to align and translate", 2014
  (ICLR 2015).
- H. J. Levesque, E. Davis and L. Morgenstern, "The Winograd schema challenge", KR 2012.
- On this site: [Chapter 13](13-Reasoning-over-Time.md) (HMMs, Viterbi) and [Chapter 17](17-Large-Language-Models.md)
  of this book; [Machine learning, Chapter 18](../machine-learning/18-Sequence-Models.md) (word2vec, RNNs, attention)
  and [Chapter 19](../machine-learning/19-Transformers.md) (transformers, BPE); the Algorithms book's
  [Chapter 13](../algorithms/13-Dynamic-Programming.md) (dynamic programming) and
  [Chapter 18](../algorithms/18-String-Algorithms.md) (string algorithms).
