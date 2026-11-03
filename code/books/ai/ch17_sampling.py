# Chapter 17: decoding a language model. Greedy, temperature, top-k and nucleus (top-p) sampling,
# from scratch: first on a hand example, then on the tiny model of ch17_tiny_lm.py.
import os
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
import numpy as np
from ch17_tiny_lm import train, forward, true_next


def softmax(z, tau=1.0):
    z = np.asarray(z, float) / tau
    p = np.exp(z - z.max())
    return p / p.sum()


def entropy(p):
    p = p[p > 0]
    return float(-(p * np.log(p)).sum())


def top_k(p, k):
    keep = np.argsort(-p)[:k]                    # the k most probable tokens
    q = np.zeros_like(p)
    q[keep] = p[keep]
    return q / q.sum()


def top_p(p, thresh):
    order = np.argsort(-p)
    cum = np.cumsum(p[order])
    n = int(np.searchsorted(cum, thresh) + 1)    # smallest prefix whose mass reaches thresh
    q = np.zeros_like(p)
    q[order[:n]] = p[order[:n]]
    return q / q.sum()


print("1. one next-token distribution, by hand-sized numbers")
toks = ["rock", "sky", "dust", "hill", "dune", "crater"]
z = [2.0, 1.0, 0.5, 0.0, -1.0, -2.0]
print("   logits      ", "  ".join(f"{t:>6s}" for t in toks))
for tau in (0.5, 1.0, 2.0):
    p = softmax(z, tau)
    print(f"   tau = {tau:<4}  ", "  ".join(f"{x:6.3f}" for x in p), f"  entropy {entropy(p):.3f}")
p = softmax(z)
print("   top-k, k=3  ", "  ".join(f"{x:6.3f}" for x in top_k(p, 3)))
print("   top-p, 0.9  ", "  ".join(f"{x:6.3f}" for x in top_p(p, 0.9)))
print("   cumulative  ", "  ".join(f"{x:6.3f}" for x in np.cumsum(np.sort(p)[::-1])), "(sorted order)")

print("\n2. the tiny model: precompute P(next | two previous words) for every pair")
P, vocab, idx = train()
V = len(vocab)
pairs = np.array([[a, b] for a in range(V) for b in range(V)])
logits_table = np.log(forward(P, pairs)[2]).reshape(V, V, V)   # log-probabilities = logits up to a shift


def generate(rule, rng, start=(".", "the"), max_len=12):
    c1, c2 = idx[start[0]], idx[start[1]]
    out = [start[1]]
    while len(out) < max_len:
        p = rule(logits_table[c1, c2], rng)
        nxt = int(np.argmax(p)) if rng is None else int(rng.choice(V, p=p))
        out.append(vocab[nxt])
        if vocab[nxt] == "." and rng is not None:
            break
        c1, c2 = c2, nxt
    return out


greedy = generate(lambda z, r: softmax(z), None, max_len=22)
print("   greedy, 22 words:", " ".join(greedy))


def grammatical(words):
    ws = ["."] + words
    return ws[-1] == "." and all(true_next(ws[i], ws[i + 1]).get(ws[i + 2], 0) > 0 for i in range(len(ws) - 2))


rules = {
    "tau 1.0": lambda z, r: softmax(z, 1.0),
    "tau 0.5": lambda z, r: softmax(z, 0.5),
    "tau 3.0": lambda z, r: softmax(z, 3.0),
    "tau 3.0 + top-k 3": lambda z, r: top_k(softmax(z, 3.0), 3),
    "tau 3.0 + top-p 0.9": lambda z, r: top_p(softmax(z, 3.0), 0.9),
}
print("\n3. 2000 sampled sentences per rule (seed 7)")
print(f"   {'rule':22s}{'rover':>7s}{'robot':>7s}{'lander':>8s}{'grammatical':>13s}{'distinct':>10s}")
for name, rule in rules.items():
    rng = np.random.default_rng(7)
    sents = [generate(rule, rng) for _ in range(2000)]
    subj = [s[1] for s in sents]
    f = [subj.count(w) / len(sents) for w in ("rover", "robot", "lander")]
    g = np.mean([grammatical(s) for s in sents])
    d = len({" ".join(s) for s in sents})
    print(f"   {name:22s}{f[0]:7.3f}{f[1]:7.3f}{f[2]:8.3f}{g:13.3f}{d:10d}")
    if name == "tau 3.0":
        bad = next(s for s in sents if not grammatical(s))
print("   an ungrammatical sample at tau 3.0:", " ".join(bad))

pt = softmax(logits_table[idx["."], idx["the"]], 0.5)
print("\n4. exact subject probabilities at tau 0.5:",
      ", ".join(f"{w} {pt[idx[w]]:.3f}" for w in ("rover", "robot", "lander")))
