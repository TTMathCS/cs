# Chapter 17: a tiny neural language model, from scratch with NumPy.
# The text comes from a small probabilistic grammar, so we know the TRUE next-word probabilities
# and can compare the model's predictions (and its perplexity) with the best possible.
import os
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
import numpy as np

# ---- 1. the grammar that writes the "internet" of this toy world ----------------------------
SUBJ = [("the rover", 0.5), ("the robot", 0.3), ("the lander", 0.2)]
VERB = [("drives to", 0.4, "PLACE"), ("looks at", 0.3, "THING"), ("takes a picture of", 0.3, "THING")]
PLACE = [("the crater", 0.5), ("the hill", 0.3), ("the dune", 0.2)]
THING = [("the rock", 0.6), ("the sky", 0.2), ("the dust", 0.2)]


def pick(rng, items):
    return items[rng.choice(len(items), p=[it[1] for it in items])]


def sentence(rng):
    s = pick(rng, SUBJ)[0]
    v = pick(rng, VERB)
    o = pick(rng, PLACE if v[2] == "PLACE" else THING)[0]
    return f"{s} {v[0]} {o} .".split()


def corpus(n, seed):
    rng = np.random.default_rng(seed)
    words = ["."]                       # the stream starts as if a sentence had just ended
    for _ in range(n):
        words += sentence(rng)
    return words


def true_next(c1, c2):
    """The grammar's exact probability of each next word after the two words c1 c2."""
    if c2 == ".":
        return {"the": 1.0}
    if c1 == "." and c2 == "the":
        return {s.split()[1]: p for s, p in SUBJ}
    if c1 == "the" and c2 in ("rover", "robot", "lander"):
        return {v.split()[0]: p for v, p, _ in VERB}
    if c2 == "the" and c1 == "to":
        return {o.split()[1]: p for o, p in PLACE}
    if c2 == "the" and c1 in ("at", "of"):
        return {o.split()[1]: p for o, p in THING}
    follow = {"drives": "to", "looks": "at", "takes": "a", "a": "picture", "picture": "of",
              "to": "the", "at": "the", "of": "the"}
    if c2 in follow:
        return {follow[c2]: 1.0}
    return {".": 1.0}                   # after a final noun the sentence ends


# ---- 2. the model: two previous words -> embeddings -> tanh layer -> softmax ----------------
def build_vocab(words):
    vocab = sorted(set(words))
    return vocab, {w: i for i, w in enumerate(vocab)}


def windows(words, idx):
    ids = np.array([idx[w] for w in words])
    return np.stack([ids[:-2], ids[1:-1]], axis=1), ids[2:]   # contexts (n, 2), targets (n,)


def init(V, d=8, h=32, seed=0):
    r = np.random.default_rng(seed)
    return {"E": r.normal(0, 0.3, (V, d)), "W1": r.normal(0, 0.3, (2 * d, h)), "b1": np.zeros(h),
            "W2": r.normal(0, 0.3, (h, V)), "b2": np.zeros(V)}


def forward(P, X):
    e = P["E"][X].reshape(len(X), -1)            # look up and join the two word vectors
    a = np.tanh(e @ P["W1"] + P["b1"])
    z = a @ P["W2"] + P["b2"]                    # logits: one score per vocabulary word
    z = z - z.max(axis=1, keepdims=True)
    p = np.exp(z)
    p /= p.sum(axis=1, keepdims=True)            # softmax: scores -> probabilities
    return e, a, p


def loss_and_grads(P, X, Y):
    n = len(X)
    e, a, p = forward(P, X)
    loss = -np.log(p[np.arange(n), Y]).mean()   # cross-entropy = average negative log-likelihood
    dz = p.copy()
    dz[np.arange(n), Y] -= 1
    dz /= n                                      # gradient of the loss with respect to the logits
    g = {"W2": a.T @ dz, "b2": dz.sum(0)}
    da = dz @ P["W2"].T * (1 - a ** 2)
    g["W1"], g["b1"] = e.T @ da, da.sum(0)
    de = (da @ P["W1"].T).reshape(n, 2, -1)
    g["E"] = np.zeros_like(P["E"])
    np.add.at(g["E"], X, de)
    return loss, g


def train(steps=100, lr=0.03, seed=0, verbose=False):
    words = corpus(2000, seed=1)
    vocab, idx = build_vocab(words)
    X, Y = windows(words, idx)
    P = init(len(vocab), seed=seed)
    m = {k: np.zeros_like(v) for k, v in P.items()}
    s = {k: np.zeros_like(v) for k, v in P.items()}
    for t in range(1, steps + 1):                # Adam on the full batch
        loss, g = loss_and_grads(P, X, Y)
        for k in P:
            m[k] = 0.9 * m[k] + 0.1 * g[k]
            s[k] = 0.999 * s[k] + 0.001 * g[k] ** 2
            P[k] -= lr * (m[k] / (1 - 0.9 ** t)) / (np.sqrt(s[k] / (1 - 0.999 ** t)) + 1e-8)
        if verbose and t in (1, 10, 25, 50, 100):
            print(f"   step {t:3d}: training loss {loss:.4f} nats per word")
    return P, vocab, idx


def next_dist(P, vocab, idx, c1, c2):
    _, _, p = forward(P, np.array([[idx[c1], idx[c2]]]))
    return dict(zip(vocab, p[0]))


if __name__ == "__main__":
    words = corpus(2000, seed=1)
    vocab, idx = build_vocab(words)
    print(f"training text: {len(words)} words, vocabulary V = {len(vocab)}")
    print("   first words:", " ".join(words[1:15]), "...")

    print("\n1. training the model (8-dim word vectors, 32 tanh units)")
    P, vocab, idx = train(verbose=True)
    nparams = sum(v.size for v in P.values())
    print(f"   {nparams} parameters; uniform guessing would score ln {len(vocab)} = {np.log(len(vocab)):.4f}")

    print("\n2. held-out text (a fresh sample from the same grammar)")
    test = corpus(500, seed=2)
    Xt, Yt = windows(test, idx)
    _, _, pt = forward(P, Xt)
    model_nll = -np.log(pt[np.arange(len(Yt)), Yt]).mean()
    true_nll = -np.mean([np.log(true_next(test[i], test[i + 1])[test[i + 2]]) for i in range(len(test) - 2)])
    counts = np.bincount([idx[w] for w in words], minlength=len(vocab)) / len(words)
    uni_nll = -np.log(counts[Yt]).mean()
    print(f"   {'model':28s}cross-entropy  perplexity")
    for name, h in [("unigram (word counts only)", uni_nll), ("tiny neural model", model_nll),
                    ("the true grammar (best)", true_nll)]:
        print(f"   {name:28s}{h:10.5f}  {np.exp(h):10.5f}")

    print("\n3. next-word probabilities: model vs the grammar")
    for c1, c2 in [(".", "the"), ("rover", "drives"), ("of", "the"), ("to", "the")]:
        md, td = next_dist(P, vocab, idx, c1, c2), true_next(c1, c2)
        top = sorted(md, key=md.get, reverse=True)[:3]
        shown = ", ".join(f"{w} {md[w]:.3f} (true {td.get(w, 0):.1f})" for w in top)
        print(f"   after '{c1} {c2}': {shown}")
