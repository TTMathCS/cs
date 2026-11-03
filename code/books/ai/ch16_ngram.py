# Chapter 16: n-gram language models from scratch: counts, add-k smoothing, interpolation,
# Kneser-Ney, perplexity on held-out text, and sampling. Data: the toy corpus of ch16_grammar.py.
import math
import random
from collections import Counter, defaultdict
from ch16_grammar import corpus

BOS, EOS = "<s>", "</s>"
train_all = [w for w, _, _ in corpus(5000, 16)]
test = [w for w, _, _ in corpus(1000, 1601)]           # held-out sentences from the same grammar
dev = [w for w, _, _ in corpus(300, 1602)]             # a separate set for choosing interpolation weights


class NGram:
    def __init__(self, sents):
        self.uni, self.bi, self.tri = Counter(), Counter(), Counter()
        self.ctx1, self.ctx2 = Counter(), Counter()
        for s in sents:
            toks = [BOS, BOS] + s + [EOS]
            for i in range(2, len(toks)):
                self.uni[toks[i]] += 1
                self.bi[(toks[i - 1], toks[i])] += 1
                self.tri[(toks[i - 2], toks[i - 1], toks[i])] += 1
                self.ctx1[toks[i - 1]] += 1
                self.ctx2[(toks[i - 2], toks[i - 1])] += 1
        self.V = sorted(set(w for s in train_all for w in s) | {EOS})   # the vocabulary (closed here)
        self.N = sum(self.uni.values())
        # for Kneser-Ney: in how many different contexts does each word appear?
        self.cont = Counter(w for (_, w) in self.bi)
        self.follow = Counter(u for (u, _) in self.bi)
        self.n_bigram_types = len(self.bi)

    def p_add_k(self, order, ctx, w, k):
        V = len(self.V)
        if order == 1:
            return (self.uni[w] + k) / (self.N + k * V)
        if order == 2:
            return (self.bi[(ctx[-1], w)] + k) / (self.ctx1[ctx[-1]] + k * V)
        return (self.tri[(ctx[-2], ctx[-1], w)] + k) / (self.ctx2[(ctx[-2], ctx[-1])] + k * V)

    def p_interp(self, ctx, w, l3, l2, l1):
        p1 = self.p_add_k(1, ctx, w, 1.0)                   # a smoothed unigram, so nothing is zero
        c1 = self.ctx1[ctx[-1]]
        p2 = self.bi[(ctx[-1], w)] / c1 if c1 else 0.0
        c2 = self.ctx2[(ctx[-2], ctx[-1])]
        p3 = self.tri[(ctx[-2], ctx[-1], w)] / c2 if c2 else 0.0
        return l3 * p3 + l2 * p2 + l1 * p1

    def p_kn(self, ctx, w, d=0.75):
        """Interpolated Kneser-Ney for bigrams (Kneser and Ney 1995; Chen and Goodman 1998)."""
        p_cont = (self.cont[w] + 1) / (self.n_bigram_types + len(self.V))   # +1: never exactly zero
        u = ctx[-1]
        c = self.ctx1[u]
        if c == 0:
            return p_cont
        lam = d * self.follow[u] / c                         # the mass taken away by discounting
        return max(self.bi[(u, w)] - d, 0) / c + lam * p_cont


def perplexity(prob, sents):
    log_sum, n = 0.0, 0
    for s in sents:
        toks = [BOS, BOS] + s + [EOS]
        for i in range(2, len(toks)):
            p = prob(toks[i - 2:i], toks[i])
            if p == 0:
                return math.inf
            log_sum += math.log2(p)
            n += 1
    return 2 ** (-log_sum / n)


print("perplexity on 1000 held-out sentences (lower is better); vocabulary 35 symbols")
print("training sentences             50       500      5000")
rows, chosen = defaultdict(list), []
for size in (50, 500, 5000):
    m = NGram(train_all[:size])
    rows["unigram, add-1"].append(perplexity(lambda c, w: m.p_add_k(1, c, w, 1), test))
    rows["bigram, unsmoothed"].append(perplexity(lambda c, w: m.p_add_k(2, c, w, 0) if m.ctx1[c[-1]] else 0, test))
    rows["bigram, add-1"].append(perplexity(lambda c, w: m.p_add_k(2, c, w, 1), test))
    rows["bigram, add-0.01"].append(perplexity(lambda c, w: m.p_add_k(2, c, w, 0.01), test))
    rows["trigram, add-0.01"].append(perplexity(lambda c, w: m.p_add_k(3, c, w, 0.01), test))
    rows["bigram, Kneser-Ney"].append(perplexity(lambda c, w: m.p_kn(c, w), test))
    grid = [(a / 20, (19.8 - a) / 20 - b / 20, 0.01 + b / 20) for a in range(20) for b in range(20 - a)]
    l3, l2, l1 = min(grid, key=lambda L: perplexity(lambda c, w: m.p_interp(c, w, *L), dev))
    rows["interpolated, tuned"].append(perplexity(lambda c, w: m.p_interp(c, w, l3, l2, l1), test))
    chosen.append(f"{l3:.2f}/{l2:.2f}/{l1:.2f}")
for name, vals in rows.items():
    print(f"{name:22s}  " + "  ".join(f"{v:8.3f}" if v < math.inf else "     inf" for v in vals))
print("interpolation weights (trigram/bigram/unigram) chosen on the dev set:", ", ".join(chosen))

m = NGram(train_all)
print("\nmost likely words after 'the' (bigram, maximum likelihood):",
      ", ".join(f"{w} {m.bi[('the', w)] / m.ctx1['the']:.3f}" for w in sorted(m.V, key=lambda w: -m.bi[("the", w)])[:5]))
print("P(drills | the) =", round(m.bi[("the", "drills")] / m.ctx1["the"], 4),
      "  P(drills | rover) =", round(m.bi[("rover", "drills")] / m.ctx1["rover"], 4))

rng = random.Random(3)
print("\nsentences sampled from the trigram model (add-0.01):")
for _ in range(4):
    ctx, out = [BOS, BOS], []
    while len(out) < 25:
        weights = [m.p_add_k(3, ctx, w, 0.01) for w in m.V]
        w = rng.choices(m.V, weights)[0]
        if w == EOS:
            break
        out.append(w)
        ctx = [ctx[-1], w]
    print("  ", " ".join(out))
