# 23. Where machine learning goes

*The previous 22 chapters built machine learning from a fitted line to the transformer, with proofs where proofs
exist. This last chapter is about the edge of what is known. Some of it is measured fact (loss falls as a power of
model size), some is good theory for simple cases (one attention layer can do a gradient step), and some is open
(why any of this generalises). You will measure a scaling law and use a published one to size a model, train a
contrastive encoder that learns from unlabelled data, build an attention layer that learns in context, watch a toy
network pack five features into two dimensions and a sparse autoencoder pull them back out, train a graph network,
and end with the open problems and how to keep going. Everything is labelled: established, partly understood, or
open.*

!!! abstract "In this chapter"
    **You will learn:**

    - what scaling laws are, how to measure one, how compute $C \approx 6ND$ is split between parameters and data,
      and how the 2020 and 2022 analyses differ
    - self-supervised and contrastive learning: the InfoNCE loss, why augmentations define what is learned, and
      what "foundation model" means
    - in-context learning, a proof that linear attention can implement a gradient step, and the honest debate about
      "emergent" abilities
    - mechanistic interpretability as a technical field: features, circuits, superposition and sparse autoencoders
    - graph neural networks, permutation equivariance and the Weisfeiler-Lehman limit, and machine learning for
      science, with AlphaFold as the example
    - the open problems, and how to read papers and reproduce results

    **You need:** [Chapter 19](19-Transformers.md) (attention and pretraining), [Chapter 21](21-Learning-Theory.md)
    (generalisation), [Chapter 14](14-Dimensionality-Reduction.md) (PCA), and
    [Chapter 16](16-Training-Deep-Networks.md) (Adam and training practice).

    **Levels:** 23.1 and 23.7 are intermediate; 23.2, 23.3 and 23.5 are advanced; 23.4 and 23.6 are expert and
    reach open research.

## 23.1 Scaling laws

*Level: intermediate.*

A practical question with a large price tag: you have a fixed budget of computation. Should you train a bigger model
on less data, or a smaller model on more? And how good will the result be? Before 2017 the answer was trial and
error. Then several groups noticed that, for neural networks trained well, test loss follows remarkably simple
curves.

### What a power law is, and measuring one

A **power law** is a relation $L(x) = A x^{-\alpha}$: multiply $x$ by 10 and $L$ is divided by the fixed factor
$10^\alpha$. On a plot with logarithmic axes it is a straight line of slope $-\alpha$, because
$\log L = \log A - \alpha\log x$. Real curves often level off at a floor $E$ that no amount of $x$ can remove (the
noise in the data), so the usual form is

$$
L(x) = E + A x^{-\alpha}.
$$

Hestness and co-authors ("Deep learning scaling is predictable, empirically", 2017) found such curves for
translation, speech and image models as the dataset grew. Kaplan and co-authors ("Scaling laws for neural
language models", 2020) measured transformer language models over a
wide range and reported that test loss is a power law in the number of parameters $N$, the dataset size $D$ (in
tokens) and the training compute $C$, with some trends spanning more than seven orders of magnitude. Their fitted
exponents were small, about 0.076 for $N$ and 0.095 for $D$, so each tenfold increase buys a modest but very
predictable improvement.

You can see the same shape in a small model family. The program below fits ridge regression on $p$ random Fourier
features (Chapter 9's random features, Chapter 21's double-descent model with a little regularisation) and measures
test error as the data grow and as the features grow, then fits $E + Ax^{-\alpha}$ with a grid over $E$ and a straight
line in log-log coordinates for the rest.

```python
--8<-- "books/machine-learning/ch23_scaling.py"
```

```
1. our own scaling curves: ridge regression on p random Fourier features
   data scaling (p = 800):        n =    100     200     400     800    1600    3200
                              test MSE = 0.0984  0.0570  0.0321  0.0186  0.0137  0.0089
   fit: L(n) = 0.0041 + 4.71 n^-0.85
   model scaling (n = 4000):      p =     25      50     100     200     400     800
                              test MSE = 0.3451  0.1176  0.0962  0.0218  0.0111  0.0081
   fit: L(p) = 0.0000 + 11.75 p^-1.13

2. compute-optimal sizes from the Chinchilla fit L(N, D) = E + A/N^a + B/D^b
   with C = 6 N D: N_opt = G (C/6)^0.452, D_opt = (C/6)^0.548 / G,  G = 1.345
      compute C (FLOP)    N_opt (params)   D_opt (tokens)   tokens/param   predicted loss
             1e+21            1.82e+09         9.14e+10           50.1            2.329
             1e+22            5.16e+09         3.23e+11           62.6            2.139
             1e+23            1.46e+10         1.14e+12           78.2            2.005
          5.76e+23            3.22e+10         2.98e+12           92.6            1.931
             1e+24            4.13e+10         4.04e+12           97.7            1.911
             1e+25            1.17e+11         1.43e+13          122.1            1.845
   at C = 5.76e23 the law gives N = 7e+10, D = 1.37e+12: loss 1.938
   at C = 5.76e23 the law gives N = 2.8e+11, D = 3.43e+11: loss 1.984
```

<figure class="mars-fig" markdown="0">
<svg viewBox="0 0 660 290" role="img" aria-label="Log-log plot of test error against training-set size and against number of features for random-feature ridge regression. Both fall along nearly straight lines: error falls from 0.098 to 0.009 as the data grow from 100 to 3200 points, and from 0.35 to 0.008 as the features grow from 25 to 800.">
<line x1="70" y1="230" x2="600" y2="230" stroke="currentColor"/><line x1="70" y1="20" x2="70" y2="230" stroke="currentColor"/>
<line x1="70.0" y1="230" x2="70.0" y2="235" stroke="currentColor"/><text x="70.0" y="249" font-size="12" text-anchor="middle" fill="currentColor">10</text>
<line x1="163.7" y1="230" x2="163.7" y2="235" stroke="currentColor"/><text x="163.7" y="249" font-size="12" text-anchor="middle" fill="currentColor">30</text>
<line x1="266.4" y1="230" x2="266.4" y2="235" stroke="currentColor"/><text x="266.4" y="249" font-size="12" text-anchor="middle" fill="currentColor">100</text>
<line x1="360.1" y1="230" x2="360.1" y2="235" stroke="currentColor"/><text x="360.1" y="249" font-size="12" text-anchor="middle" fill="currentColor">300</text>
<line x1="462.7" y1="230" x2="462.7" y2="235" stroke="currentColor"/><text x="462.7" y="249" font-size="12" text-anchor="middle" fill="currentColor">1000</text>
<line x1="556.4" y1="230" x2="556.4" y2="235" stroke="currentColor"/><text x="556.4" y="249" font-size="12" text-anchor="middle" fill="currentColor">3000</text>
<line x1="65" y1="230.0" x2="70" y2="230.0" stroke="currentColor"/><text x="61" y="234.0" font-size="12" text-anchor="end" fill="currentColor">0.005</text>
<line x1="65" y1="198.4" x2="70" y2="198.4" stroke="currentColor"/><text x="61" y="202.4" font-size="12" text-anchor="end" fill="currentColor">0.01</text>
<line x1="65" y1="148.3" x2="70" y2="148.3" stroke="currentColor"/><text x="61" y="152.3" font-size="12" text-anchor="end" fill="currentColor">0.03</text>
<line x1="65" y1="93.4" x2="70" y2="93.4" stroke="currentColor"/><text x="61" y="97.4" font-size="12" text-anchor="end" fill="currentColor">0.1</text>
<line x1="65" y1="43.3" x2="70" y2="43.3" stroke="currentColor"/><text x="61" y="47.3" font-size="12" text-anchor="end" fill="currentColor">0.3</text>
<text x="335.0" y="270" font-size="13" text-anchor="middle" fill="currentColor">training points n, or features p (log scale)</text>
<text x="20" y="125.0" font-size="13" text-anchor="middle" fill="currentColor" transform="rotate(-90 20 125.0)">test MSE (log)</text>
<polyline points="266.4,94.1 325.5,119.0 384.6,145.2 443.7,170.1 502.8,184.0 561.9,203.7" fill="none" stroke="#eea66f" stroke-width="2.2"/>
<circle cx="266.4" cy="94.1" r="3.5" fill="#eea66f" stroke="currentColor" stroke-width="0.8"/>
<circle cx="325.5" cy="119.0" r="3.5" fill="#eea66f" stroke="currentColor" stroke-width="0.8"/>
<circle cx="384.6" cy="145.2" r="3.5" fill="#eea66f" stroke="currentColor" stroke-width="0.8"/>
<circle cx="443.7" cy="170.1" r="3.5" fill="#eea66f" stroke="currentColor" stroke-width="0.8"/>
<circle cx="502.8" cy="184.0" r="3.5" fill="#eea66f" stroke="currentColor" stroke-width="0.8"/>
<circle cx="561.9" cy="203.7" r="3.5" fill="#eea66f" stroke="currentColor" stroke-width="0.8"/>
<line x1="420" y1="40" x2="440" y2="40" stroke="#eea66f" stroke-width="2.2"/><text x="446" y="44" font-size="12" fill="currentColor">more data (p = 800)</text>
<polyline points="148.1,36.9 207.3,86.0 266.4,95.2 325.5,162.9 384.6,193.6 443.7,208.0" fill="none" stroke="#9cc9ea" stroke-width="2.2"/>
<circle cx="148.1" cy="36.9" r="3.5" fill="#9cc9ea" stroke="currentColor" stroke-width="0.8"/>
<circle cx="207.3" cy="86.0" r="3.5" fill="#9cc9ea" stroke="currentColor" stroke-width="0.8"/>
<circle cx="266.4" cy="95.2" r="3.5" fill="#9cc9ea" stroke="currentColor" stroke-width="0.8"/>
<circle cx="325.5" cy="162.9" r="3.5" fill="#9cc9ea" stroke="currentColor" stroke-width="0.8"/>
<circle cx="384.6" cy="193.6" r="3.5" fill="#9cc9ea" stroke="currentColor" stroke-width="0.8"/>
<circle cx="443.7" cy="208.0" r="3.5" fill="#9cc9ea" stroke="currentColor" stroke-width="0.8"/>
<line x1="420" y1="62" x2="440" y2="62" stroke="#9cc9ea" stroke-width="2.2"/><text x="446" y="66" font-size="12" fill="currentColor">more features (n = 4000)</text>
</svg>
<figcaption>Figure 23.1. Measured by ch23_scaling.py: test error of random-feature ridge regression against data size
and against model size, on logarithmic axes. Both are close to straight lines, the signature of a power law.</figcaption>
</figure>

Both curves are close to straight lines: the data curve has exponent about 0.85, the model curve about 1.1 (the bump
between $p = 50$ and $p = 100$ is the noise of three runs). For this smooth target the exponents are much larger than
for language models, which is itself informative: the exponent measures how hard the task is to learn, and natural
language is very hard. Sharma and Kaplan ("A neural scaling law from the dimension of the data manifold", JMLR 2022)
argued that the exponent is roughly inversely proportional to the intrinsic dimension of the data; Bahri, Dyer,
Kaplan, Lee and Sharma ("Explaining neural scaling laws", PNAS 2024) separated a "variance-limited" regime from a
"resolution-limited" one. Why language-model losses follow power laws so closely is not fully explained.

### Compute, and how to spend it

For a transformer with $N$ parameters, a forward pass costs about $2N$ floating-point operations (FLOP) per token, one
multiply and one add per weight, and the backward pass about twice that. So training on $D$ tokens costs about

$$
C \approx 6ND \ \text{FLOP}.
$$

Given $C$, choosing $N$ fixes $D = C/(6N)$. Hoffmann and co-authors ("Training compute-optimal large
language models", 2022) trained over 400 models and fitted the parametric form

$$
L(N, D) = E + \frac{A}{N^{a}} + \frac{B}{D^{b}},
$$

with $E = 1.69$, $A = 406.4$, $B = 410.7$, $a = 0.34$, $b = 0.28$ (their equation 10). $E$ is the irreducible loss of
the text; the two other terms are what a finite model and finite data cost.

**The compute-optimal split, derived.** Substitute $D = C/(6N)$ and minimise over $N$:

$$
\frac{d}{dN}\Big(AN^{-a} + B\Big(\frac{6N}{C}\Big)^{b}\Big) = -aAN^{-a-1} + bB\Big(\frac6C\Big)^bN^{b-1} = 0
\iff N^{a+b} = \frac{aA}{bB}\Big(\frac C6\Big)^{b}.
$$

So $N_{\text{opt}} = G\,(C/6)^{b/(a+b)}$ with $G = (aA/(bB))^{1/(a+b)}$, and $D_{\text{opt}} = (C/6)^{a/(a+b)}/G$. With
$a = 0.34$ and $b = 0.28$ the exponents are $0.452$ and $0.548$: parameters and data should grow at nearly the same
rate. (The second derivative is positive, so this is a minimum.)

Part 2 of the program evaluates the formula. At $C = 5.76 \times 10^{23}$ FLOP it gives about 32 billion parameters
and 3 trillion tokens. The 2020 analysis had concluded that model size should grow much faster than data (Kaplan et
al. found $N_{\text{opt}} \propto C^{0.73}$), and several large models of the time were trained with about 300
billion tokens. Hoffmann et al. estimated the optimum three different ways and got exponents for $N$ of 0.50, 0.49 and
0.46 (the last is the parametric fit used here), and they tested the conclusion directly: Chinchilla, with 70 billion
parameters trained on 1.4 trillion tokens, used the same compute as their earlier Gopher model (280 billion
parameters, 300 billion tokens) and, as reported in their paper, outperformed it on a large range of evaluation tasks.
The program's last two lines show the fitted law agrees: at Gopher's budget, the 70B allocation has lower predicted
loss (1.938) than the 280B one (1.984). The popular rule of thumb "about 20 tokens per parameter" is the ratio
Chinchilla used; the parametric fit alone suggests more.

<figure class="mars-fig" markdown="0">
<svg viewBox="0 0 660 290" role="img" aria-label="Iso-compute curves from the Chinchilla scaling law: for each fixed compute budget, predicted loss against model size is U-shaped. The minimum moves to larger models as compute grows: about 1.8 billion parameters at 10 to the 21 FLOP, 15 billion at 10 to the 23, and 117 billion at 10 to the 25.">
<line x1="70" y1="230" x2="560" y2="230" stroke="currentColor"/><line x1="70" y1="20" x2="70" y2="230" stroke="currentColor"/>
<line x1="70.0" y1="230" x2="70.0" y2="235" stroke="currentColor"/><text x="70.0" y="249" font-size="12" text-anchor="middle" fill="currentColor">100M</text>
<line x1="168.0" y1="230" x2="168.0" y2="235" stroke="currentColor"/><text x="168.0" y="249" font-size="12" text-anchor="middle" fill="currentColor">1B</text>
<line x1="266.0" y1="230" x2="266.0" y2="235" stroke="currentColor"/><text x="266.0" y="249" font-size="12" text-anchor="middle" fill="currentColor">10B</text>
<line x1="364.0" y1="230" x2="364.0" y2="235" stroke="currentColor"/><text x="364.0" y="249" font-size="12" text-anchor="middle" fill="currentColor">100B</text>
<line x1="462.0" y1="230" x2="462.0" y2="235" stroke="currentColor"/><text x="462.0" y="249" font-size="12" text-anchor="middle" fill="currentColor">1T</text>
<line x1="560.0" y1="230" x2="560.0" y2="235" stroke="currentColor"/><text x="560.0" y="249" font-size="12" text-anchor="middle" fill="currentColor">10T</text>
<line x1="65" y1="230.0" x2="70" y2="230.0" stroke="currentColor"/><text x="61" y="234.0" font-size="12" text-anchor="end" fill="currentColor">1.8</text>
<line x1="65" y1="188.0" x2="70" y2="188.0" stroke="currentColor"/><text x="61" y="192.0" font-size="12" text-anchor="end" fill="currentColor">2.0</text>
<line x1="65" y1="146.0" x2="70" y2="146.0" stroke="currentColor"/><text x="61" y="150.0" font-size="12" text-anchor="end" fill="currentColor">2.2</text>
<line x1="65" y1="104.0" x2="70" y2="104.0" stroke="currentColor"/><text x="61" y="108.0" font-size="12" text-anchor="end" fill="currentColor">2.4</text>
<line x1="65" y1="62.0" x2="70" y2="62.0" stroke="currentColor"/><text x="61" y="66.0" font-size="12" text-anchor="end" fill="currentColor">2.6</text>
<line x1="65" y1="20.0" x2="70" y2="20.0" stroke="currentColor"/><text x="61" y="24.0" font-size="12" text-anchor="end" fill="currentColor">2.8</text>
<text x="315.0" y="270" font-size="13" text-anchor="middle" fill="currentColor">parameters N (log scale); tokens D = C / (6N)</text>
<text x="20" y="125.0" font-size="13" text-anchor="middle" fill="currentColor" transform="rotate(-90 20 125.0)">predicted loss</text>
<polyline points="70.0,57.8 72.5,60.5 74.9,63.0 77.3,65.5 79.8,67.9 82.2,70.3 84.7,72.6 87.2,74.8 89.6,76.9 92.0,79.0 94.5,81.0 97.0,83.0 99.4,84.9 101.8,86.8 104.3,88.6 106.8,90.3 109.2,92.0 111.7,93.6 114.1,95.2 116.5,96.7 119.0,98.1 121.5,99.5 123.9,100.9 126.3,102.2 128.8,103.4 131.2,104.6 133.7,105.7 136.2,106.8 138.6,107.8 141.0,108.8 143.5,109.8 146.0,110.7 148.4,111.5 150.8,112.3 153.3,113.1 155.8,113.8 158.2,114.4 160.7,115.0 163.1,115.6 165.5,116.1 168.0,116.6 170.5,117.0 172.9,117.4 175.3,117.8 177.8,118.0 180.2,118.3 182.7,118.5 185.2,118.7 187.6,118.8 190.0,118.9 192.5,118.9 195.0,118.9 197.4,118.9 199.8,118.8 202.3,118.7 204.8,118.5 207.2,118.3 209.7,118.0 212.1,117.7 214.5,117.4 217.0,117.0 219.5,116.6 221.9,116.1 224.3,115.6 226.8,115.1 229.2,114.5 231.7,113.9 234.2,113.2 236.6,112.5 239.0,111.7 241.5,110.9 244.0,110.1 246.4,109.2 248.8,108.3 251.3,107.3 253.8,106.3 256.2,105.3 258.7,104.2 261.1,103.1 263.5,101.9 266.0,100.6 268.5,99.4 270.9,98.1 273.3,96.7 275.8,95.3 278.2,93.9 280.7,92.4 283.2,90.8 285.6,89.3 288.0,87.6 290.5,86.0 293.0,84.2 295.4,82.5 297.8,80.7 300.3,78.8 302.8,76.9 305.2,74.9 307.7,72.9 310.1,70.9 312.5,68.7 315.0,66.6 317.5,64.4 319.9,62.1 322.3,59.8 324.8,57.4 327.2,55.0 329.7,52.5 332.2,50.0 334.6,47.4 337.0,44.8 339.5,42.1 342.0,39.3 344.4,36.5 346.8,33.6 349.3,30.7 351.8,27.7 354.2,24.7 356.7,21.5" fill="none" stroke="#7ccf9a" stroke-width="2.2"/>
<circle cx="193.6" cy="118.9" r="4.5" fill="#7ccf9a" stroke="currentColor" stroke-width="1"/>
<text x="193.6" y="108.9" font-size="12" text-anchor="middle" fill="currentColor">C = 1e21</text>
<polyline points="70.0,81.5 72.5,84.5 74.9,87.4 77.3,90.3 79.8,93.1 82.2,95.9 84.7,98.6 87.2,101.2 89.6,103.8 92.0,106.4 94.5,108.8 97.0,111.2 99.4,113.6 101.8,115.9 104.3,118.2 106.8,120.4 109.2,122.6 111.7,124.7 114.1,126.8 116.5,128.8 119.0,130.7 121.5,132.7 123.9,134.6 126.3,136.4 128.8,138.2 131.2,140.0 133.7,141.7 136.2,143.3 138.6,145.0 141.0,146.6 143.5,148.1 146.0,149.6 148.4,151.1 150.8,152.6 153.3,154.0 155.8,155.3 158.2,156.7 160.7,158.0 163.1,159.2 165.5,160.4 168.0,161.6 170.5,162.8 172.9,163.9 175.3,165.0 177.8,166.1 180.2,167.1 182.7,168.1 185.2,169.1 187.6,170.1 190.0,171.0 192.5,171.9 195.0,172.7 197.4,173.5 199.8,174.4 202.3,175.1 204.8,175.9 207.2,176.6 209.7,177.3 212.1,178.0 214.5,178.6 217.0,179.2 219.5,179.8 221.9,180.4 224.3,180.9 226.8,181.4 229.2,181.9 231.7,182.4 234.2,182.8 236.6,183.2 239.0,183.6 241.5,184.0 244.0,184.4 246.4,184.7 248.8,185.0 251.3,185.3 253.8,185.5 256.2,185.8 258.7,186.0 261.1,186.2 263.5,186.3 266.0,186.5 268.5,186.6 270.9,186.7 273.3,186.8 275.8,186.9 278.2,186.9 280.7,186.9 283.2,186.9 285.6,186.9 288.0,186.9 290.5,186.8 293.0,186.7 295.4,186.6 297.8,186.5 300.3,186.4 302.8,186.2 305.2,186.0 307.7,185.8 310.1,185.6 312.5,185.4 315.0,185.1 317.5,184.8 319.9,184.5 322.3,184.2 324.8,183.8 327.2,183.4 329.7,183.1 332.2,182.6 334.6,182.2 337.0,181.8 339.5,181.3 342.0,180.8 344.4,180.3 346.8,179.7 349.3,179.2 351.8,178.6 354.2,178.0 356.7,177.4 359.1,176.7 361.6,176.1 364.0,175.4 366.5,174.7 368.9,174.0 371.3,173.2 373.8,172.4 376.2,171.6 378.7,170.8 381.2,170.0 383.6,169.1 386.0,168.2 388.5,167.3 390.9,166.3 393.4,165.4 395.8,164.4 398.3,163.4 400.8,162.3 403.2,161.3 405.7,160.2 408.1,159.1 410.5,157.9 413.0,156.8 415.5,155.6 417.9,154.4 420.3,153.1 422.8,151.8 425.2,150.5 427.7,149.2 430.2,147.9 432.6,146.5 435.0,145.1 437.5,143.6 440.0,142.2 442.4,140.7 444.8,139.1 447.3,137.6 449.8,136.0 452.2,134.3 454.7,132.7 457.1,131.0 459.5,129.3 462.0,127.5 464.5,125.7 466.9,123.9 469.3,122.1 471.8,120.2 474.2,118.2 476.7,116.3 479.2,114.3 481.6,112.2 484.1,110.2 486.5,108.1 489.0,105.9 491.4,103.7 493.8,101.5 496.3,99.2 498.8,96.9 501.2,94.6 503.7,92.2 506.1,89.8 508.5,87.3 511.0,84.8 513.5,82.2 515.9,79.6 518.3,76.9 520.8,74.2 523.2,71.5 525.7,68.7 528.2,65.8 530.6,62.9 533.0,60.0 535.5,57.0 538.0,54.0 540.4,50.9 542.8,47.7 545.3,44.5 547.8,41.3 550.2,37.9 552.7,34.6 555.1,31.1 557.5,27.7 560.0,24.1" fill="none" stroke="#9cc9ea" stroke-width="2.2"/>
<circle cx="282.1" cy="186.9" r="4.5" fill="#9cc9ea" stroke="currentColor" stroke-width="1"/>
<text x="282.1" y="176.9" font-size="12" text-anchor="middle" fill="currentColor">C = 1e23</text>
<polyline points="70.0,88.0 72.5,91.1 74.9,94.2 77.3,97.2 79.8,100.1 82.2,103.0 84.7,105.8 87.2,108.5 89.6,111.2 92.0,113.9 94.5,116.5 97.0,119.0 99.4,121.5 101.8,124.0 104.3,126.4 106.8,128.7 109.2,131.0 111.7,133.3 114.1,135.5 116.5,137.6 119.0,139.7 121.5,141.8 123.9,143.8 126.3,145.8 128.8,147.8 131.2,149.7 133.7,151.6 136.2,153.4 138.6,155.2 141.0,157.0 143.5,158.7 146.0,160.4 148.4,162.0 150.8,163.6 153.3,165.2 155.8,166.8 158.2,168.3 160.7,169.8 163.1,171.2 165.5,172.7 168.0,174.1 170.5,175.4 172.9,176.8 175.3,178.1 177.8,179.3 180.2,180.6 182.7,181.8 185.2,183.0 187.6,184.2 190.0,185.3 192.5,186.4 195.0,187.5 197.4,188.6 199.8,189.7 202.3,190.7 204.8,191.7 207.2,192.6 209.7,193.6 212.1,194.5 214.5,195.4 217.0,196.3 219.5,197.2 221.9,198.1 224.3,198.9 226.8,199.7 229.2,200.5 231.7,201.2 234.2,202.0 236.6,202.7 239.0,203.4 241.5,204.1 244.0,204.8 246.4,205.5 248.8,206.1 251.3,206.7 253.8,207.3 256.2,207.9 258.7,208.5 261.1,209.1 263.5,209.6 266.0,210.1 268.5,210.6 270.9,211.1 273.3,211.6 275.8,212.1 278.2,212.5 280.7,213.0 283.2,213.4 285.6,213.8 288.0,214.2 290.5,214.6 293.0,215.0 295.4,215.3 297.8,215.7 300.3,216.0 302.8,216.3 305.2,216.6 307.7,216.9 310.1,217.2 312.5,217.5 315.0,217.7 317.5,218.0 319.9,218.2 322.3,218.4 324.8,218.6 327.2,218.8 329.7,219.0 332.2,219.2 334.6,219.3 337.0,219.5 339.5,219.6 342.0,219.8 344.4,219.9 346.8,220.0 349.3,220.1 351.8,220.2 354.2,220.2 356.7,220.3 359.1,220.4 361.6,220.4 364.0,220.4 366.5,220.5 368.9,220.5 371.3,220.5 373.8,220.5 376.2,220.5 378.7,220.4 381.2,220.4 383.6,220.3 386.0,220.3 388.5,220.2 390.9,220.1 393.4,220.0 395.8,219.9 398.3,219.8 400.8,219.7 403.2,219.6 405.7,219.4 408.1,219.3 410.5,219.1 413.0,219.0 415.5,218.8 417.9,218.6 420.3,218.4 422.8,218.2 425.2,218.0 427.7,217.7 430.2,217.5 432.6,217.2 435.0,217.0 437.5,216.7 440.0,216.4 442.4,216.1 444.8,215.8 447.3,215.5 449.8,215.2 452.2,214.8 454.7,214.5 457.1,214.1 459.5,213.8 462.0,213.4 464.5,213.0 466.9,212.6 469.3,212.2 471.8,211.7 474.2,211.3 476.7,210.8 479.2,210.4 481.6,209.9 484.1,209.4 486.5,208.9 489.0,208.4 491.4,207.9 493.8,207.4 496.3,206.8 498.8,206.3 501.2,205.7 503.7,205.1 506.1,204.5 508.5,203.9 511.0,203.3 513.5,202.6 515.9,202.0 518.3,201.3 520.8,200.6 523.2,199.9 525.7,199.2 528.2,198.5 530.6,197.8 533.0,197.0 535.5,196.2 538.0,195.4 540.4,194.7 542.8,193.8 545.3,193.0 547.8,192.2 550.2,191.3 552.7,190.4 555.1,189.5 557.5,188.6 560.0,187.7" fill="none" stroke="#eea66f" stroke-width="2.2"/>
<circle cx="370.6" cy="220.5" r="4.5" fill="#eea66f" stroke="currentColor" stroke-width="1"/>
<text x="370.6" y="210.5" font-size="12" text-anchor="middle" fill="currentColor">C = 1e25</text>
<path d="M 194 119 L 282 187 L 371 220" fill="none" stroke="currentColor" stroke-dasharray="4 3" stroke-width="1.2"/>
</svg>
<figcaption>Figure 23.2. Iso-compute curves of the Chinchilla fit: predicted loss against model size for three
compute budgets. Too small a model wastes compute on data it cannot use; too large a model sees too few tokens. The
dots mark the compute-optimal sizes, which grow roughly like the square root of compute.</figcaption>
</figure>

**What to believe.** Established: within the ranges measured, loss curves of well-tuned models are smooth and
predictable, which makes it possible to choose sizes before training. Contested or open: how far the laws extrapolate;
whether lower loss means proportionally better behaviour on any particular task (23.3); what happens when the supply
of new text runs short (Muennighoff and co-authors, "Scaling data-constrained language models", NeurIPS 2023, found
that repeating data for up to about four epochs costs little, with sharply diminishing value after that); and how the
laws change with better architectures, data filtering and training methods, which can shift the constants a great
deal. Compute-optimal is also not the only goal: a model that will answer billions of queries is often trained
longer than "optimal" so that it can be smaller and cheaper to run.

## 23.2 Self-supervised and contrastive learning; foundation models

*Level: advanced.*

Labels are expensive; raw data are not. **Self-supervised learning** makes a supervised problem out of unlabelled data
by hiding part of each example and asking the model to predict it, or by asking it to recognise which examples belong
together. Chapter 19's next-token and masked-token pretraining are self-supervised. The goal is a
**representation**: a map from raw inputs to vectors in which the things you will later care about are easy to read
off, often by a linear model trained on few labels (a **linear probe**).

### Contrastive learning and InfoNCE

The contrastive idea: make two different **views** of the same example (two random crops of a photo, the same sound
with different noise), and train an encoder $f$ so that the two views' embeddings are close while embeddings of
different examples are far apart. Chen, Kornblith, Norouzi and Hinton ("A simple framework for contrastive learning
of visual representations", SimCLR, ICML 2020) showed how far this goes with strong image augmentations, a large
batch and a small projection head; a linear classifier trained on SimCLR's representations reached 76.5% top-1
accuracy on ImageNet, as reported in their paper.

The loss most methods use is **InfoNCE** (van den Oord, Li and Vinyals, "Representation learning with contrastive
predictive coding", 2018). Take a batch of $B$ examples, two views of each, and normalised embeddings
$u_i = f(x_i)/\|f(x_i)\|$ and $u'_i$. The similarity of $i$ and $j$ is the cosine $u_i \cdot u'_j$ divided by a
**temperature** $\tau$ (a small number like 0.2 that sharpens the comparison). For each $i$, the loss is the
cross-entropy of picking the right partner $i$ among all $B$ candidates:

$$
\mathcal L = -\frac1B\sum_{i=1}^{B}\log\frac{\exp(u_i\cdot u'_i/\tau)}{\sum_{j=1}^{B}\exp(u_i\cdot u'_j/\tau)} .
$$

It is a $B$-way classification problem whose "classes" are the other examples in the batch. A random guess gets
$\ln B$. Van den Oord et al. showed that $\ln B - \mathcal L$ is a lower bound on the mutual information between the
two views' embeddings (Chapter 3's information measures), which explains one limitation: the bound can never certify
more than $\ln B$ nats, one reason contrastive methods like large batches. Wang and Isola ("Understanding contrastive
representation learning through alignment and uniformity on the hypersphere", ICML 2020) showed that the loss
balances two forces: **alignment** (positive pairs close) and **uniformity** (all embeddings spread over the sphere,
so that information is not thrown away).

The gradient follows from the softmax-cross-entropy rule of Chapter 6. Let $S_{ij} = u_i\cdot u'_j/\tau$ and
$P = \mathrm{softmax}$ of each row. Then $\partial\mathcal L/\partial S = (P - I)/B$; the chain rule through
$S = UU'^\top/\tau$ gives $\partial\mathcal L/\partial U = (P - I)U'/(B\tau)$; and through the normalisation
$u = z/\|z\|$, the gradient with respect to $z$ is the gradient with respect to $u$ with its component along $u$
removed, divided by $\|z\|$. The program implements exactly this (and was checked against finite differences to
relative error $2 \times 10^{-9}$).

**The experiment.** Each input has 32 numbers that mix, by a random rotation, 4 "content" coordinates (which depend
on one of 4 hidden classes) and 28 "style" coordinates (large random variation unrelated to the class). An
augmentation keeps the content and redraws the style. A linear encoder to 4 dimensions is trained by InfoNCE on
20000 unlabelled inputs. Then a linear probe (nearest class mean) is trained on only 20 labelled examples.

```python
--8<-- "books/machine-learning/ch23_contrastive.py"
```

```
1. training a linear encoder with InfoNCE (batch 256, temperature 0.2, Adam)
   step    1: loss 7.967   (chance level ln 256 = 5.545)
   step   50: loss 4.633   (chance level ln 256 = 5.545)
   step  200: loss 3.938   (chance level ln 256 = 5.545)
   step  600: loss 3.648   (chance level ln 256 = 5.545)
   share of encoder weight on the 4 content directions: 0.999   (random encoder: 0.103)

2. linear probe with only 5 labelled examples per class (20 labels), test on 4000
   raw input (32 numbers)   accuracy 0.375
   PCA, top 4 directions    accuracy 0.262
   random linear encoder    accuracy 0.291
   contrastive encoder      accuracy 0.890
   oracle: true content     accuracy 0.994
```

The loss starts above $\ln 256$ (a random encoder mostly sees style, which the two views do not share, so positives
can look less similar than negatives) and falls to 3.65. The trained encoder puts 99.9% of its weight on the 4 content
directions, without ever seeing a label. With 20 labels, the probe on its embedding gets 0.890, against 0.375 on raw
inputs. PCA does worst of all, 0.262: it keeps the directions of largest variance, which here are style. That is the
central lesson of self-supervised learning: the representation learns to ignore exactly what the augmentations
change, so the choice of augmentation is a choice of what counts as "the same". Pick augmentations that destroy the
signal you care about, and no amount of training will recover it.

**Without negatives, and by reconstruction.** BYOL (Grill et al., NeurIPS 2020) dropped the negative pairs, predicting
one view's embedding from the other's with a slowly updated "target" network; why it does not collapse to a constant
was at first a puzzle and is now partly explained by the asymmetric architecture and the training dynamics. Masked
autoencoders (He, Chen, Xie, Li, Dollár and Girshick, CVPR 2022) hide most patches of an image and reconstruct them,
the image analogue of masked language modelling. CLIP (Radford et al., "Learning transferable visual models from
natural language supervision", ICML 2021) applies InfoNCE between images and their captions, which gives a shared
embedding space for pictures and text.

### Foundation models

Bommasani and many co-authors ("On the opportunities and risks of foundation models", 2021) proposed the
name **foundation model** for a model trained on broad data, usually self-supervised and at scale, that is then
adapted to many downstream tasks: by fine-tuning, by a linear probe, or, for language models, simply by prompting.
The technical point is a change in workflow. Instead of training one model per task from scratch, one large
pretraining run is amortised over many uses, and the representation, not the task head, carries most of the
knowledge. The costs are concentration (few organisations can afford the pretraining) and homogenisation (a defect in
the base model is inherited by everything built on it), which is why evaluation and interpretability of base models
matter so much (23.4).

## 23.3 In-context learning and emergent behaviour

*Level: advanced.*

Brown and co-authors ("Language models are few-shot learners", NeurIPS 2020) trained GPT-3, a 175-billion-parameter
transformer, on next-token prediction and found that it could perform new tasks from a few examples written in its
prompt, with no change to its weights: show it three English-to-French word pairs and a fourth English word, and it
continues with the French. This is **in-context learning** (ICL). The weights are fixed; the "learning" happens in the
forward pass, inside the activations. How can a fixed function learn?

### A proof in the simplest case

Take linear regression tasks. Each task has an unknown weight vector $w$; the prompt contains pairs $(x_i, y_i)$ with
$y_i = w\cdot x_i + \text{noise}$, and then a query $x_q$. Write each pair as a token $e_i = (x_i, y_i)$ and the query
as $e_q = (x_q, 0)$. A **linear self-attention** layer (attention without the softmax) outputs, at the query position,

$$
\text{out}_q = \frac1n\sum_{i=1}^{n}(W_V e_i)\,\big((W_K e_i)\cdot(W_Q e_q)\big).
$$

**Claim (von Oswald, Niklasson, Randazzo, Sacramento, Mordvintsev, Zhmoginov and Vladymyrov, "Transformers learn
in-context by gradient descent", ICML 2023).** There are fixed matrices for which the last coordinate of
$\text{out}_q$ equals the prediction at $x_q$ after one step of gradient descent, from $w = 0$, on the prompt's
examples.

*Proof.* The squared loss on the prompt is $\frac1{2n}\sum_i(w\cdot x_i - y_i)^2$, with gradient at $w = 0$ equal to
$-\frac1n\sum_i y_ix_i$. One step of size $\eta$ gives $w_1 = \frac\eta n\sum_i y_ix_i$, so its prediction is
$w_1\cdot x_q = \frac\eta n\sum_i y_i\,(x_i\cdot x_q)$. Now choose $W_K = W_Q$ to keep the $x$ part of a token and zero
the $y$ part, so that $(W_Ke_i)\cdot(W_Qe_q) = x_i\cdot x_q$, and choose $W_V$ to keep only $\eta\,y_i$, placed in the
last coordinate. The attention output's last coordinate is then $\frac1n\sum_i\eta\,y_i\,(x_i\cdot x_q)$, the same
number. $\square$

Part 1 of the program confirms the equality to six decimals. Part 2 goes one step further: it treats the step size
as the layer's only trainable parameter and trains it by stochastic gradient descent over thousands of random tasks,
which is how a transformer is trained (on many sequences), not how it is used. The learned step matches the
theoretical optimum $n/(n + d + 1 + \sigma^2)$, which comes from minimising the expected error over tasks
(exercise 5). In that sense the training process discovers a learning algorithm that then runs in the forward pass.

```python
--8<-- "books/machine-learning/ch23_icl.py"
```

```
1. one attention layer = one gradient step from w = 0 on the prompt's examples
   n =  5: attention output +1.557039   GD-step prediction +1.557039
   n = 20: attention output -2.965081   GD-step prediction -2.965081

2. meta-training the step size over many random tasks (the only parameter here)
   n = 10: learned step 0.601   theory n/(n+d+1+sigma^2) = 0.615
   n = 40: learned step 0.871   theory n/(n+d+1+sigma^2) = 0.865

3. test error on new tasks (average squared error over 2000 tasks)
    n    predict 0   one GD step (eta*)   least squares
    10       4.939                1.817           0.329
    20       4.984                1.146           0.089
    40       4.721                0.654           0.038
    80       4.891                0.329           0.016
   160       4.939                0.171           0.008

4. 'emergence' from the metric: per-token accuracy improves smoothly,
   exact match on a 10-token answer (all tokens right) looks like a sudden jump
   size step   per-token accuracy   exact match (p^10)
           1                 0.50                0.001
           2                 0.70                0.028
           3                 0.80                0.107
           4                 0.90                0.349
           5                 0.95                0.599
           6                 0.98                0.817
           7                 0.99                0.904
```

Part 3 is the honest coda: one gradient step is a weak learner. Least squares on the same prompt is far better (0.038
against 0.654 at $n = 40$). Garg, Tsipras, Liang and Valiant ("What can transformers learn in-context? A case study of
simple function classes", NeurIPS 2022) trained real transformers on such prompts and found their in-context
predictions close to least squares, much better than one step; Akyürek, Schuurmans, Andreas, Ma and Zhou ("What
learning algorithm is in-context learning? Investigations with linear models", ICLR 2023) found evidence of
algorithms between gradient descent and exact least squares depending on depth and width. For language models trained
on text, a different and complementary explanation views ICL as implicit Bayesian inference: the prompt narrows down
which "document type" is being continued (Xie, Raghunathan, Liang and Ma, ICLR 2022). Which mechanisms large models
actually use, and when, is open.

### "Emergent" abilities, and the debate

Wei and co-authors ("Emergent abilities of large language models", TMLR 2022) collected tasks where performance stayed
near chance as models grew and then rose sharply beyond some size, and called such abilities **emergent**: not
predictable by extrapolating from smaller models. This matters: if capabilities appear suddenly, scaling laws for loss
do not predict them.

Schaeffer, Miranda and Koyejo ("Are emergent abilities of large language models a mirage?", NeurIPS 2023) gave a
counter-argument that is easy to check. Many of those tasks are scored by **exact match**: an answer of $L$ tokens is
right only if every token is right. If each token is right with probability $p$, independently, exact match is
$p^L$, a sharply nonlinear function of $p$. Part 4 of the program shows it: per-token accuracy rising smoothly from 0.5
to 0.99 makes 10-token exact match go 0.001, 0.028, 0.107, 0.349, 0.599, 0.817, 0.904, which looks like a sudden jump
on a linear axis. They showed that, for many reported examples, switching to a continuous metric (such as per-token
log-likelihood) turned the jump into a smooth curve.

The honest summary: some apparent emergence is an artefact of the metric, and that is now well established. Whether
*all* of it is remains debated; some tasks may genuinely need several sub-skills to be present at once, and a
continuous proxy metric is not the same thing as the capability people care about. The practical lesson is clear: when
you see a sudden jump, plot a continuous metric before concluding anything.

## 23.4 Mechanistic interpretability

*Level: expert.*

Chapter 22's tools explain a model from the outside: which inputs matter. **Mechanistic interpretability** asks how
the model computes from the inside: which internal directions represent which concepts, and which weights connect
them into algorithms. It is a young research field, with real results on small models and open problems for large
ones. This section treats it purely technically.

### Features, circuits and the probing question

Olah and co-authors ("Zoom in: an introduction to circuits", Distill 2020) set out a programme on vision networks:
identify **features** (directions in a layer's activation space that respond to an interpretable property, such as a
curve at some orientation), then **circuits** (the weights that compute a feature from features in the layer below),
and verify each claim by checking that the circuit's weights implement what the feature's behaviour suggests. They
found, for example, curve detectors assembled from earlier edge detectors in a consistent geometric pattern.

The simplest tool is a **probe**: train a linear classifier on a layer's activations to predict some property
(Alain and Bengio, "Understanding intermediate layers using linear classifier probes", 2016). A successful probe
shows the information is *linearly present*; it does not show the model *uses* it. For that one needs **causal
interventions**: change the activation and see whether the output changes as predicted. **Activation patching**
copies an activation from a run on one input into a run on another; Meng, Bau, Andonian and Belinkov ("Locating and
editing factual associations in GPT", NeurIPS 2022) used it to find where factual associations are stored in a
language model, and Wang, Variengien, Conmy, Shlegeris and Steinhardt ("Interpretability in the wild: a circuit for
indirect object identification in GPT-2 small", ICLR 2023) mapped a circuit of attention heads for one
grammatical task. Geiger, Lu, Icard and Potts ("Causal abstractions of neural networks", NeurIPS 2021) gave a
framework for saying precisely when a high-level algorithm describes a network.

### Superposition

A difficulty appears immediately: single neurons are often **polysemantic**, responding to several unrelated things.
One explanation is **superposition**: a layer with $m$ neurons can represent more than $m$ features, as long as the
features are **sparse** (rarely active at the same time), by giving them directions that are almost but not quite
orthogonal. In $m$ dimensions there are only $m$ exactly orthogonal directions, but exponentially many that are nearly
orthogonal, so the interference between features is small when few are active at once.

A toy model that interpretability researchers use to study this: $n = 5$ input features, each active with probability
$p$ and then uniform in $[0, 1]$; a hidden layer $h = Wx$ with only $m = 2$ dimensions; and a reconstruction
$\hat x = \mathrm{ReLU}(W^\top h + b)$ trained to reproduce $x$, with feature $i$ weighted by importance $0.8^i$. The
columns $W_i$ of $W$ are the directions the model assigns to the features.

```python
--8<-- "books/machine-learning/ch23_superposition.py"
```

```
1. five features, two hidden dimensions: what does the model keep?
   P(active)   loss    |W_i| for the 5 features           angles of the kept features (degrees)
      1.00    0.1306   [1.   1.   0.02 0.02 0.01]   2 kept, gaps between them: [ 90. 270.]
      0.30    0.0900   [1.04 1.03 0.01 0.99 0.94]   4 kept, gaps between them: [90. 90. 90. 90.]
      0.10    0.0174   [1.1  1.1  1.1  1.08 1.01]   5 kept, gaps between them: [77. 70. 64. 73. 76.]
      0.03    0.0027   [1.17 1.16 1.14 1.14 1.11]   5 kept, gaps between them: [75. 70. 70. 71. 75.]

2. sparse autoencoder on the 2-D activations (8 dictionary features, L1 penalty 0.001)
   reconstruction: fraction of variance unexplained 0.1685
   average number of active dictionary features per input: 1.24   (true active features: 1.06)
   dictionary features that fire on more than 1% of inputs: 7 of 8
   best cosine between each true feature direction and a learned one: [0.982 0.994 0.997 0.996 0.986]
```

<figure class="mars-fig" markdown="0">
<svg viewBox="0 0 660 260" role="img" aria-label="The columns of the trained 2 by 5 weight matrix drawn as arrows in the plane. With dense features two arrows at a right angle; with features active 30 percent of the time four arrows in a cross; with features active 3 percent of the time five arrows forming a pentagon.">
<circle cx="110" cy="115" r="75" fill="none" stroke="currentColor" stroke-opacity="0.25" stroke-dasharray="3 3"/>
<line x1="27" y1="115" x2="193" y2="115" stroke="currentColor" stroke-opacity="0.3"/><line x1="110" y1="32" x2="110" y2="198" stroke="currentColor" stroke-opacity="0.3"/>
<line x1="110" y1="115" x2="168.2" y2="92.1" stroke="#eea66f" stroke-width="3"/>
<circle cx="168.2" cy="92.1" r="4" fill="#eea66f" stroke="currentColor" stroke-width="0.8"/>
<text x="180.3" y="91.3" font-size="11" text-anchor="middle" fill="currentColor">1</text>
<line x1="110" y1="115" x2="87.2" y2="56.6" stroke="#9cc9ea" stroke-width="3"/>
<circle cx="87.2" cy="56.6" r="4" fill="#9cc9ea" stroke="currentColor" stroke-width="0.8"/>
<text x="82.5" y="48.5" font-size="11" text-anchor="middle" fill="currentColor">2</text>
<text x="110" y="228" font-size="12" text-anchor="middle" fill="currentColor">always active: 2 features, orthogonal</text>
<circle cx="330" cy="115" r="75" fill="none" stroke="currentColor" stroke-opacity="0.25" stroke-dasharray="3 3"/>
<line x1="247" y1="115" x2="413" y2="115" stroke="currentColor" stroke-opacity="0.3"/><line x1="330" y1="32" x2="330" y2="198" stroke="currentColor" stroke-opacity="0.3"/>
<line x1="330" y1="115" x2="381.7" y2="75.8" stroke="#eea66f" stroke-width="3"/>
<circle cx="381.7" cy="75.8" r="4" fill="#eea66f" stroke="currentColor" stroke-width="0.8"/>
<text x="392.1" y="72.0" font-size="11" text-anchor="middle" fill="currentColor">1</text>
<line x1="330" y1="115" x2="291.1" y2="63.4" stroke="#9cc9ea" stroke-width="3"/>
<circle cx="291.1" cy="63.4" r="4" fill="#9cc9ea" stroke="currentColor" stroke-width="0.8"/>
<text x="283.3" y="57.0" font-size="11" text-anchor="middle" fill="currentColor">2</text>
<line x1="330" y1="115" x2="367.1" y2="164.1" stroke="#eea66f" stroke-width="3"/>
<circle cx="367.1" cy="164.1" r="4" fill="#eea66f" stroke="currentColor" stroke-width="0.8"/>
<text x="374.9" y="178.5" font-size="11" text-anchor="middle" fill="currentColor">4</text>
<line x1="330" y1="115" x2="283.4" y2="150.5" stroke="#9cc9ea" stroke-width="3"/>
<circle cx="283.4" cy="150.5" r="4" fill="#9cc9ea" stroke="currentColor" stroke-width="0.8"/>
<text x="273.1" y="162.4" font-size="11" text-anchor="middle" fill="currentColor">5</text>
<text x="330" y="228" font-size="12" text-anchor="middle" fill="currentColor">active 30%: 4 features</text>
<circle cx="550" cy="115" r="75" fill="none" stroke="currentColor" stroke-opacity="0.25" stroke-dasharray="3 3"/>
<line x1="467" y1="115" x2="633" y2="115" stroke="currentColor" stroke-opacity="0.3"/><line x1="550" y1="32" x2="550" y2="198" stroke="currentColor" stroke-opacity="0.3"/>
<line x1="550" y1="115" x2="580.1" y2="48.4" stroke="#eea66f" stroke-width="3"/>
<circle cx="580.1" cy="48.4" r="4" fill="#eea66f" stroke="currentColor" stroke-width="0.8"/>
<text x="585.5" y="40.6" font-size="11" text-anchor="middle" fill="currentColor">1</text>
<line x1="550" y1="115" x2="494.0" y2="69.0" stroke="#9cc9ea" stroke-width="3"/>
<circle cx="494.0" cy="69.0" r="4" fill="#9cc9ea" stroke="currentColor" stroke-width="0.8"/>
<text x="483.9" y="64.7" font-size="11" text-anchor="middle" fill="currentColor">2</text>
<line x1="550" y1="115" x2="620.6" y2="126.3" stroke="#7ccf9a" stroke-width="3"/>
<circle cx="620.6" cy="126.3" r="4" fill="#7ccf9a" stroke="currentColor" stroke-width="0.8"/>
<text x="633.5" y="132.4" font-size="11" text-anchor="middle" fill="currentColor">3</text>
<line x1="550" y1="115" x2="562.6" y2="185.0" stroke="#eea66f" stroke-width="3"/>
<circle cx="562.6" cy="185.0" r="4" fill="#eea66f" stroke="currentColor" stroke-width="0.8"/>
<text x="564.9" y="201.8" font-size="11" text-anchor="middle" fill="currentColor">4</text>
<line x1="550" y1="115" x2="490.3" y2="150.0" stroke="#9cc9ea" stroke-width="3"/>
<circle cx="490.3" cy="150.0" r="4" fill="#9cc9ea" stroke="currentColor" stroke-width="0.8"/>
<text x="479.1" y="160.6" font-size="11" text-anchor="middle" fill="currentColor">5</text>
<text x="550" y="228" font-size="12" text-anchor="middle" fill="currentColor">active 3%: 5 features, a pentagon</text>
</svg>
<figcaption>Figure 23.3. The trained feature directions (columns of W) of the toy model, from ch23_superposition.py.
Dense features: the two most important get orthogonal directions and the rest are dropped. Sparser features: the
model packs four, then all five, into two dimensions, at nearly equal angles.</figcaption>
</figure>

When features are always active (dense), the model does what PCA would: it keeps the two most important features on
orthogonal directions and drops the other three (their norms are 0.01 or 0.02). As features become sparser, it keeps
more: four in a cross at 90 degrees when $p = 0.3$, and all five at about 72 degrees, a pentagon, when $p = 0.1$ or
$0.03$. Why does this work? With a pentagon, feature 1's direction has inner product $\cos 72° = 0.31$ with two
neighbours and $\cos 144° = -0.81$ with the other two. When feature 1 alone is active, the reconstruction of the others
gets these interference terms; the negative ones are cut off by the ReLU, and the small positive ones by a negative
bias. When features are rarely active together, that is almost always the case, so the loss is small (0.0027 at
$p = 0.03$). The model trades a little interference for a lot of capacity.

### Sparse autoencoders

If a real layer stores features in superposition, its neurons are the wrong basis to read, and we need to find the
feature directions. That is a **sparse dictionary learning** problem, an old one: Olshausen and Field (Nature 1996)
learned sparse codes for natural images and found edge-like features similar to those in the visual cortex. A
**sparse autoencoder** (SAE) learns an overcomplete dictionary: an encoder $f = \mathrm{ReLU}(W_eh + b_e)$ with more
features than dimensions, a decoder $\hat h = W_df$, and a loss $\|\hat h - h\|^2 + \lambda\|f\|_1$ whose L1 term (Chapter
8's lasso) makes most codes zero. Part 2 trains one with 8 dictionary features on the toy model's 2-dimensional
activations. Every one of the five true directions is matched by a learned one with cosine at least 0.982, using only
about 1.24 active codes per input (the true number is 1.06). The unexplained variance of 0.17 is mostly the L1
penalty's shrinkage of code magnitudes, the same bias the lasso has.

Cunningham, Ewart, Riggs, Huben and Sharkey ("Sparse autoencoders find highly interpretable features in language
models", ICLR 2024) applied SAEs to a language model's internal activations and reported features that were more
interpretable than individual neurons by the measures they used. Open problems, technically stated: there is no ground truth for real
models, so how do we know an SAE found the model's features rather than artefacts of the dictionary-learning objective?
How should the dictionary size and penalty be chosen? Do features compose into circuits that explain behaviour end to
end, at scale? Interpretability claims are tested the way all science is: by predictions and interventions that
could have failed.

## 23.5 Graph neural networks, geometric deep learning, and ML for science

*Level: advanced.*

Molecules, road networks, social networks, meshes, and the network of places on Mars that a route planner searches
(the Algorithms book's shortest-path chapter) are **graphs**: nodes joined by edges. A graph has no natural order of its
nodes, so a model of a graph should not depend on how we number them.

### Message passing and the GCN

Let $A$ be the adjacency matrix ($A_{uv} = 1$ if $u$ and $v$ are joined) and $X$ the matrix of node features. A
**permutation** of the nodes is a matrix $P$ that reorders rows; it turns $A$ into $PAP^\top$ and $X$ into $PX$. A
layer $F$ is **permutation equivariant** if $F(PAP^\top, PX) = P\,F(A, X)$: renumbering the nodes renumbers the output
the same way, and nothing else changes. **Message passing** layers (Gilmer, Schoenholz, Riley, Vinyals and Dahl,
"Neural message passing for quantum chemistry", ICML 2017) achieve this by construction: each node updates its vector
from its own vector and an order-independent aggregate (sum, mean or max) of its neighbours'.

The **graph convolutional network** of Kipf and Welling ("Semi-supervised classification with graph convolutional
networks", ICLR 2017) is the simplest widely used example. With $\tilde A = A + I$ (each node also listens to itself)
and $\tilde D$ its diagonal degree matrix, one layer is

$$
H^{(l+1)} = \mathrm{ReLU}\big(\hat A H^{(l)} W^{(l)}\big), \qquad \hat A = \tilde D^{-1/2}\tilde A\tilde D^{-1/2}.
$$

Multiplying by $\hat A$ replaces each node's vector by a degree-weighted average over its neighbourhood; the symmetric
normalisation keeps the scale stable for nodes of very different degree. Equivariance has a one-line proof: $\hat A$
becomes $P\hat AP^\top$ under renumbering, so $\hat A H W$ becomes $P\hat AP^\top PHW = P\,\hat AHW$ (because
$P^\top P = I$), and the ReLU acts entrywise, so it commutes with $P$. Two layers mix information from two hops away.

The program builds a graph with three communities (a stochastic block model: edges appear with probability 0.10 inside a
community and 0.01 between), gives each node noisy features that only weakly hint at its community, labels only 3 nodes
per community, and trains a two-layer GCN and, for comparison, the same network with $\hat A$ replaced by the identity
(an MLP that ignores the edges).

```python
--8<-- "books/machine-learning/ch23_gnn.py"
```

```
graph: 180 nodes, 678 edges, mean degree 7.5, 0.81 of edges inside a community

1. 9 labelled nodes (3 per community); accuracy on the other 171
   MLP (ignores edges): mean accuracy 0.654 over 5 initialisations (min 0.637, max 0.667)
   GCN (uses edges)   : mean accuracy 0.988 over 5 initialisations (min 0.982, max 0.994)

2. permutation equivariance: relabel the nodes, the outputs are relabelled the same way
   max |GCN(P A P^T, P X) - P GCN(A, X)| = 3.33e-16
```

With 9 labels, the MLP classifies 65% of the other nodes correctly; the GCN, 98.8%. The edges carry most of the
information, and averaging over neighbours removes most of the feature noise, because 81% of each node's neighbours
share its community. Part 2 checks equivariance to $3 \times 10^{-16}$.

**A limit, proved.** Xu, Hu, Leskovec and Jegelka ("How powerful are graph neural networks?", ICLR 2019) and
independently Morris and co-authors (AAAI 2019) showed that message-passing networks can distinguish two graphs at
most as well as the **1-dimensional Weisfeiler-Lehman test** (1-WL), a classical colour-refinement procedure for graph
isomorphism. Two triangles and one hexagon are different graphs, but every node in both has degree 2 and neighbours
of degree 2, so 1-WL and every message-passing network (with identical node features) treat them the same (exercise
8). Xu et al. also gave an architecture, GIN, that reaches this limit. Going beyond it needs higher-order structures,
extra node features, or other designs, an active area.

**Geometric deep learning.** Bronstein, Bruna, Cohen and Veličković ("Geometric deep learning: grids, groups, graphs,
geodesics, and gauges", 2021) organised much of deep learning around one idea: choose the symmetry of the data, and
build layers that respect it. Convolutional networks (Chapter 17) are translation-equivariant; GNNs are
permutation-equivariant; transformers are permutation-equivariant on sets of tokens until positional encodings break
the symmetry (Chapter 19); networks for molecules and physics are built to be equivariant to rotations and
reflections in three dimensions. Respecting a true symmetry shrinks the hypothesis class without losing anything,
which is Chapter 21's bias-complexity trade-off at its most favourable.

### Machine learning for science

The clearest success is protein structure prediction. A protein is a chain of amino acids that folds into a 3-D shape
that determines its function; measuring the shape experimentally can take months or years. Jumper and co-authors
("Highly accurate protein structure prediction with AlphaFold", Nature 2021) described AlphaFold 2, which in
the CASP14 blind assessment reached, as reported in the paper, a median backbone accuracy of 0.96 Å (r.m.s.d. at 95%
residue coverage), against 2.8 Å for the next best method. Its architecture combines attention over a multiple
sequence alignment of related proteins, a representation of residue pairs updated with triangle-shaped operations that
respect the geometry of distances, and a structure module that is equivariant to rotations and translations. Other
examples, each in a peer-reviewed paper: graph networks for medium-range weather forecasting (Lam et al., "Learning
skillful medium-range global weather forecasting", Science 2023), and graph networks proposing new stable crystal
structures (Merchant et al., "Scaling deep learning for materials discovery", Nature 2023).

Closer to this site's home, planetary rovers use learned perception where waiting for Earth is too slow. Rothrock and
co-authors (2016) described SPOC, a convolutional network that classifies Martian terrain types from orbital and rover
images to help plan traversable paths, and Perseverance's AutoNav drives itself between waypoints, building
3-D maps from its cameras as it goes. A signal delay of 3 to 22 minutes each way makes on-board autonomy a requirement,
and also makes the problems of Chapter 22 (shift between training terrain and new terrain, robustness, monitoring)
very concrete.

The common pattern in scientific ML: strong inductive biases from the domain (symmetry, physics, known structure),
large curated datasets built over decades by scientists (the Protein Data Bank in AlphaFold's case), and careful
evaluation against held-out, often future, data. The open question is how to quantify uncertainty well enough that
scientists can trust a prediction they cannot yet check.

## 23.6 Open problems

*Level: expert.*

These are questions on which serious researchers disagree or that nobody can yet answer. Each is stated technically,
with the reason it is hard.

**Generalisation theory.** Chapter 21 ended with the gap: classical bounds are vacuous for deep networks that fit
random labels, yet the networks generalise. Partial answers exist (implicit bias of gradient descent for linear models,
benign overfitting in linear regression, the infinite-width neural tangent kernel, PAC-Bayes bounds that are
non-vacuous for some trained networks). Open: a theory that predicts, before training, which of two architectures will
generalise better on a given kind of data, and explains the role of feature learning.

**Sample efficiency.** Large models need vastly more examples than people do to learn a word or a game. Pretraining
moves the cost into one big run, but learning a genuinely new concept from a handful of examples, reliably, is still
hard. Open: which inductive biases, architectures or training signals close the gap, and how to measure it fairly
(people also bring years of prior experience to each new task).

**Causality.** Supervised learning estimates $P(y \mid x)$; decisions need to know what happens if we *change* $x$,
which correlation does not answer (Chapter 1). Pearl's causal framework (*Causality*, 2nd ed. 2009) and the
potential-outcomes framework say when causal effects can be estimated from data. Schölkopf and co-authors ("Toward
causal representation learning", Proceedings of the IEEE 2021) argue that models that learn causal variables would
transfer better under shift. Open: how to learn causal structure from high-dimensional observations like images, and
how to combine causal assumptions with large pretrained models.

**Continual learning.** Train a network on task A and then on task B, and it usually forgets A: **catastrophic
forgetting**, reported by McCloskey and Cohen (1989). Gradient descent on B moves the weights wherever B's loss
prefers, with no memory of what mattered for A. Remedies include replaying old data, penalising changes to important
weights (elastic weight consolidation, Kirkpatrick et al., PNAS 2017, which weights the penalty by the Fisher
information), and growing the network. Open: learning from a non-stationary stream for a long time without forgetting
and without storing everything, which is what deployed systems facing Chapter 22's shifts would need.

**Robustness and evaluation.** Adversarial examples (Chapter 22) are not solved for large models; certified methods
scale poorly. Evaluation itself is a research problem: benchmarks saturate, test sets leak into web-scale training data
(contamination), and models can satisfy the letter of an objective while missing its intent, a phenomenon called
**specification gaming** or reward hacking, defined formally by Skalse, Howe, Krasheninnikov and Krueger ("Defining
and characterizing reward hacking", NeurIPS 2022). Open: evaluations that stay valid as models grow, and objectives that cannot be gamed.

**Energy and compute cost.** Training and serving large models takes a lot of electricity and hardware, and the
compute used for the largest training runs has grown very fast. Strubell, Ganesh and McCallum ("Energy and policy
considerations for deep learning in NLP", ACL 2019) and Patterson and co-authors ("Carbon emissions and large neural
network training", 2021) estimated costs for specific models and showed that hardware, data-centre efficiency and
location change the answer by large factors. The technical directions are better algorithms (the compute-optimal
analysis of 23.1 is one), sparsity and mixture-of-experts models that use only part of their weights per input,
quantisation (fewer bits per weight), distillation into smaller models, and efficient attention (Chapter 19). Open:
how much capability per unit of energy is achievable, and how to report costs consistently.

## 23.7 How to keep learning

You now have the whole arc, from a nearest-neighbour classifier in 20 lines to research questions. Here is how to keep
going on your own.

**Courses and books.** The textbooks in this chapter's Further reading are the standard ones: Bishop, Murphy, and
Hastie, Tibshirani and Friedman for the classical and probabilistic side; Goodfellow, Bengio and Courville for deep
learning; Shalev-Shwartz and Ben-David for theory; Bronstein et al. for geometric deep learning. Many universities put
full lecture courses online with notes and assignments (Stanford's CS229 on machine learning and CS231n on convolutional
networks are long-standing examples). Work the assignments; watching is not learning.

**Reading papers.** New results appear first as preprints on arXiv, then at conferences (NeurIPS, ICML, ICLR) and in
journals (JMLR, TMLR). Keshav's "How to read a paper" (ACM SIGCOMM Computer Communication Review, 2007) describes a
three-pass method that works: first pass, title, abstract, figures and conclusions (is it relevant?); second pass, the
whole paper without the proofs (what exactly is claimed, and on what evidence?); third pass, re-derive it as if you were
the author. Ask of every paper: what is the baseline, how many runs, what are the error bars, what was tuned and on
which data, and would the result survive a different dataset?

**Reproducing results.** The best way to understand a paper is to reproduce one of its figures, small. This book has
done that throughout: double descent with 40 points, a scaling law with random features, in-context learning with one
attention layer. The checklist from the reproducibility programme that Pineau and co-authors ran at NeurIPS 2019
("Improving reproducibility in machine learning research", JMLR 2021) is a good habit: state the data and its splits,
the hyperparameters and how they were chosen, the number of runs, the measure of spread, the compute used, and release
the code. When your reproduction disagrees with the paper, that is not a failure; finding out why is where the
learning is.

**Build things.** Pick a dataset you care about (rover images, weather records, your own sensor data), write a baseline
you understand completely, and only then reach for a library. Every program in this book is a starting point.

## Check yourself

??? question "1. Chinchilla had 70 billion parameters and was trained on 1.4 trillion tokens. Estimate its training compute with $C \approx 6ND$, and say where the 6 comes from."

    $C \approx 6 \times 7 \times 10^{10} \times 1.4 \times 10^{12} = 5.88 \times 10^{23}$ FLOP, close to the
    $5.76 \times 10^{23}$ used in the paper's comparison. The 6: the forward pass costs about 2 FLOP per parameter per
    token (one multiply, one add), and the backward pass about twice the forward (gradients with respect to both
    activations and weights).

??? question "2. Derive the compute-optimal exponents for $L = E + AN^{-a} + BD^{-b}$ under $C = 6ND$ with a Lagrange multiplier instead of substitution."

    Minimise $AN^{-a} + BD^{-b}$ subject to $ND = C/6$. Setting the gradient of
    $AN^{-a} + BD^{-b} + \mu(ND - C/6)$ to zero gives $aAN^{-a} = \mu ND = bBD^{-b}$ (multiply each partial derivative by
    its variable). So at the optimum the two loss terms are in the fixed ratio $AN^{-a} : BD^{-b} = b : a$, and with
    $D = C/(6N)$ this gives $N \propto C^{b/(a+b)}$, $D \propto C^{a/(a+b)}$; with $a = 0.34$, $b = 0.28$, the exponents
    0.452 and 0.548, as in the program.

??? question "3. A loss follows $L(n) = E + An^{-\alpha}$ with $\alpha = 0.85$. By what factor must the data grow to halve the reducible part $L - E$? What if $\alpha = 0.095$?"

    Halving $An^{-\alpha}$ needs $n$ multiplied by $2^{1/\alpha}$. For $\alpha = 0.85$: $2^{1/0.85} = 2.26$. For
    $\alpha = 0.095$: $2^{1/0.095} = 2^{10.5} \approx 1500$. Small exponents are why language models need so much data:
    every halving of the reducible loss costs three orders of magnitude.

??? question "4. In the contrastive run the final InfoNCE loss was 3.648 with batch 256. What lower bound on mutual information does this give, and what is the largest bound any batch of 256 can give?"

    $\ln 256 - 3.648 = 5.545 - 3.648 = 1.897$ nats. The loss is a cross-entropy, so it is at least 0, and the bound is at
    most $\ln 256 = 5.545$ nats, however much information the views share. Certifying more needs larger batches (more
    negatives), which is one reason contrastive methods use them.

??? question "5. (Hard) Prove that the best step size for the one-step in-context learner of 23.3 is $\eta^\ast = n/(n + d + 1 + \sigma^2)$ when $w$, $x_i$ and $x_q$ are standard Gaussian in $d$ dimensions and the noise has variance $\sigma^2$."

    The prediction is $\eta\,g\cdot x_q$ with $g = \frac1n\sum_i y_ix_i = \hat\Sigma w + \frac1n\sum_i\varepsilon_ix_i$,
    where $\hat\Sigma = \frac1n\sum_ix_ix_i^\top$. Since $x_q$ is independent with identity covariance, the expected
    squared error is $E\|\eta g - w\|^2 = \eta^2E\|g\|^2 - 2\eta E[g\cdot w] + d$. Here $E[g\cdot w] = E[w^\top\hat\Sigma w]
    = d$. For $E\|g\|^2$: the noise part gives $\sigma^2d/n$; the signal part is $E[w^\top\hat\Sigma^2w] =
    E\,\mathrm{tr}(\hat\Sigma^2) = \frac1{n^2}\sum_{i,j}E(x_i\cdot x_j)^2 = \frac1{n^2}\big(n\,d(d + 2) + n(n - 1)d\big) =
    d(n + d + 1)/n$, using $E\|x\|^4 = d(d + 2)$ and $E(x_i\cdot x_j)^2 = d$ for $i \ne j$. So
    $E\|g\|^2 = d(n + d + 1 + \sigma^2)/n$, and minimising the quadratic gives $\eta^\ast = d/E\|g\|^2 =
    n/(n + d + 1 + \sigma^2)$. For $n = 40$, $d = 5$, $\sigma = 0.5$: 0.865, and SGD learned 0.871.

??? question "6. Each token of a 10-token answer is right with probability $p$. Compute exact-match accuracy for $p = 0.9$, 0.95 and 0.99. How much must the per-token error fall to go from 35% to 90% exact match?"

    $0.9^{10} = 0.349$, $0.95^{10} = 0.599$, $0.99^{10} = 0.904$. Going from 0.349 to 0.904 needs the per-token error to
    fall from 0.10 to 0.01, a factor of 10 in a quantity that may be improving smoothly. On a plot against model size the
    exact-match curve looks like a jump; the per-token curve does not.

??? question "7. Compute $\hat A = \tilde D^{-1/2}(A + I)\tilde D^{-1/2}$ by hand for the path graph 1 - 2 - 3."

    $A + I$ has ones on the diagonal and at positions (1,2), (2,1), (2,3), (3,2). The degrees in $\tilde A$ are 2, 3,
    2. Entry $(u, v)$ is $\tilde A_{uv}/\sqrt{d_ud_v}$: the diagonal is $1/2, 1/3, 1/2$; the four off-diagonal ones are
    $1/\sqrt{6} \approx 0.408$; entries (1,3) and (3,1) are 0. One GCN layer gives node 2 a weighted average of all three
    nodes and each end node an average of itself and node 2.

??? question "8. Write the code: implement 1-WL colour refinement and show that it cannot tell two triangles from one hexagon."

    Each round, a node's new colour is the pair (its colour, the sorted list of its neighbours' colours), renamed to a
    small integer. Two graphs are declared different if their colour multisets ever differ.

    ```python
    def wl_colours(adj, rounds=3):
        colour = {v: 0 for v in adj}
        for _ in range(rounds):
            sig = {v: (colour[v], tuple(sorted(colour[u] for u in adj[v]))) for v in adj}
            names = {s: i for i, s in enumerate(sorted(set(sig.values())))}
            colour = {v: names[sig[v]] for v in adj}
        return sorted(colour.values())

    def cycle(nodes):
        return {v: [nodes[(i - 1) % len(nodes)], nodes[(i + 1) % len(nodes)]] for i, v in enumerate(nodes)}

    two_triangles = {**cycle([0, 1, 2]), **cycle([3, 4, 5])}
    hexagon = cycle([0, 1, 2, 3, 4, 5])
    print(wl_colours(two_triangles), wl_colours(hexagon))
    ```

    It prints `[0, 0, 0, 0, 0, 0] [0, 0, 0, 0, 0, 0]`: every node in both graphs has two neighbours of the same colour,
    forever. A message-passing network with identical starting features computes identical node vectors on both, so any
    graph-level output (a sum or mean over nodes) is the same, although one graph has triangles and the other has none.

??? question "9. In the pentagon arrangement of the toy model, feature 1 is active with value 1 and the others are 0. What does $W^\top Wx$ give for the other features, ignoring small differences in norms, and how does a bias fix it?"

    With unit-length directions at 72-degree spacing, $W^\top W x$ has entry $\cos 72° \approx 0.31$ for the two
    neighbours of feature 1 and $\cos 144° \approx -0.81$ for the other two (and 1 for feature 1 itself). The ReLU sets
    the negative ones to 0. A bias of about $-0.31$ on every feature removes the positive interference too, at the cost
    of shrinking every real output by the same amount. When two features are active together, interference can
    survive; that is why superposition only pays when features are sparse.

??? question "10. Explain catastrophic forgetting with linear regression: you fit $w$ to task A by gradient descent, then continue on task B only. When does the solution for A survive?"

    Gradient descent on B's loss $\|X_Bw - y_B\|^2$ changes $w$ only within the row space of $X_B$ (Chapter 21's
    implicit-bias argument). The component of $w$ orthogonal to that row space, what A taught in directions B never
    uses, is untouched. So A's solution survives exactly to the extent that A's important directions are orthogonal to
    B's inputs; in the shared directions, B overwrites A. Elastic weight consolidation adds a penalty
    $\sum_j F_j(w_j - w_{A,j})^2$ that resists moving the weights important for A.

??? question "11. A paper reports that a new method improves accuracy from 81.2% to 81.9% on one benchmark. List five questions to ask before believing that the method is better."

    How many runs with different seeds, and what is the spread (is 0.7 points larger than the seed-to-seed variation)?
    Were the baseline and the new method tuned with the same budget and on validation data, not the test set? Is the
    test set possibly in the pretraining data? Does the gain hold on other datasets, or only this one? What does it
    cost in compute? A bootstrap or paired test across examples (Chapter 7) answers the first question; only
    reproduction answers the others.

## What you learned

- Test loss of well-trained models follows power laws in parameters, data and compute; with $C \approx 6ND$ and the
  fitted law $E + AN^{-a} + BD^{-b}$, the compute-optimal model and data sizes both grow roughly like $\sqrt C$, which
  is what the 2022 analysis changed from the 2020 one.
- Self-supervised learning turns unlabelled data into a training signal. Contrastive learning with InfoNCE learns
  what the augmentations leave unchanged, so augmentations define the representation; foundation models reuse one
  pretrained representation for many tasks.
- In-context learning can be proved possible in simple cases: one linear attention layer equals one gradient step, and
  training discovers the right step size; real models do better, by mechanisms still being studied. Some "emergence"
  is a property of exact-match metrics.
- Mechanistic interpretability looks for features and circuits inside models and tests claims by intervention;
  superposition lets sparse features share dimensions, and sparse autoencoders can recover them in toy settings.
- Graph networks are permutation-equivariant message passing, limited by the 1-WL test; building symmetry into a model
  shrinks its hypothesis class for free, and scientific ML, with AlphaFold as the standard example, combines such
  biases with large curated data.
- Open: why deep networks generalise, how to learn from few examples, causal and continual learning, robust
  evaluation, and the energy cost of scale.

**Next:** this is the last chapter. Return to the [book's contents](index.md) to revisit any part, or to pick the
next paper to reproduce.

## Further reading

- J. Kaplan et al., "Scaling Laws for Neural Language Models", 2020; J. Hoffmann et al., "Training Compute-Optimal
  Large Language Models", NeurIPS 2022; J. Hestness et al., "Deep Learning Scaling is Predictable, Empirically", 2017.
- N. Muennighoff et al., "Scaling Data-Constrained Language Models", NeurIPS 2023; U. Sharma and J. Kaplan, "A Neural
  Scaling Law from the Dimension of the Data Manifold", *JMLR*, 2022.
- T. Chen, S. Kornblith, M. Norouzi and G. Hinton, "A Simple Framework for Contrastive Learning of Visual
  Representations", ICML 2020; A. van den Oord, Y. Li and O. Vinyals, "Representation Learning with Contrastive
  Predictive Coding", 2018; T. Wang and P. Isola, "Understanding Contrastive Representation Learning through Alignment
  and Uniformity on the Hypersphere", ICML 2020.
- R. Bommasani et al., "On the Opportunities and Risks of Foundation Models", 2021.
- T. Brown et al., "Language Models are Few-Shot Learners", NeurIPS 2020; J. von Oswald et al., "Transformers Learn
  In-Context by Gradient Descent", ICML 2023; S. Garg, D. Tsipras, P. Liang and G. Valiant, "What Can Transformers
  Learn In-Context? A Case Study of Simple Function Classes", NeurIPS 2022.
- J. Wei et al., "Emergent Abilities of Large Language Models", *TMLR*, 2022; R. Schaeffer, B. Miranda and S. Koyejo,
  "Are Emergent Abilities of Large Language Models a Mirage?", NeurIPS 2023.
- C. Olah et al., "Zoom In: An Introduction to Circuits", *Distill*, 2020; K. Meng, D. Bau, A. Andonian and
  Y. Belinkov, "Locating and Editing Factual Associations in GPT", NeurIPS 2022; H. Cunningham et al., "Sparse
  Autoencoders Find Highly Interpretable Features in Language Models", ICLR 2024; B. Olshausen and D. Field,
  "Emergence of Simple-Cell Receptive Field Properties by Learning a Sparse Code for Natural Images", *Nature*, 1996.
- T. Kipf and M. Welling, "Semi-Supervised Classification with Graph Convolutional Networks", ICLR 2017; K. Xu,
  W. Hu, J. Leskovec and S. Jegelka, "How Powerful are Graph Neural Networks?", ICLR 2019; M. Bronstein, J. Bruna,
  T. Cohen and P. Veličković, "Geometric Deep Learning: Grids, Groups, Graphs, Geodesics, and Gauges", 2021.
- J. Jumper et al., "Highly Accurate Protein Structure Prediction with AlphaFold", *Nature*, 2021.
- J. Pearl, *Causality*, 2nd ed., 2009; B. Schölkopf et al., "Toward Causal Representation Learning", *Proceedings of
  the IEEE*, 2021; J. Kirkpatrick et al., "Overcoming Catastrophic Forgetting in Neural Networks", *PNAS*, 2017.
- C. Bishop, *Pattern Recognition and Machine Learning*, 2006; K. Murphy, *Probabilistic Machine Learning: Advanced
  Topics*, 2023; I. Goodfellow, Y. Bengio and A. Courville, *Deep Learning*, 2016; S. Shalev-Shwartz and S. Ben-David,
  *Understanding Machine Learning*, 2014.
- S. Keshav, "How to Read a Paper", *ACM SIGCOMM Computer Communication Review*, 2007; J. Pineau et al., "Improving
  Reproducibility in Machine Learning Research", *JMLR*, 2021.
- On this site: the [book's contents](index.md); [Chapter 19](19-Transformers.md) (the transformer that scaling laws
  measure), [Chapter 20](20-Generative-Models.md) (generative models), [Chapter 21](21-Learning-Theory.md) (the
  generalisation puzzle), [Chapter 22](22-Machine-Learning-in-Practice.md) (shift, robustness and interpretability in
  practice); the Algorithms book's [Chapter 16](../algorithms/16-Shortest-Paths.md) for route finding on graphs and its
  [last chapter](../algorithms/25-Where-Algorithms-Go.md) for the frontier on that side; and the math books at
  https://math.akadian.ca/books/ for the linear algebra, probability and statistics underneath everything here.
