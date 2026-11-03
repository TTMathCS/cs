"""Chapter 18: word2vec (skip-gram with negative sampling) from scratch on a tiny
made-up corpus, the analogy test king - man + woman, and the count-based view
(PPMI matrix + SVD) that Levy and Goldberg (2014) showed it is close to."""
import numpy as np

rng = np.random.default_rng(2013)

# ------------------------------------------------------- a corpus with structure
# Each person-word has a gender, an age and a status; the words around it in a
# sentence are drawn from those properties, plus filler.
people = {   # word: (gender, age, status)
    "king": ("m", "old", "royal"), "queen": ("f", "old", "royal"),
    "prince": ("m", "young", "royal"), "princess": ("f", "young", "royal"),
    "man": ("m", "old", "common"), "woman": ("f", "old", "common"),
    "boy": ("m", "young", "common"), "girl": ("f", "young", "common"),
}
cue = {"m": ["he", "his", "him"], "f": ["she", "her", "hers"],
       "old": ["grown", "adult", "elder"], "young": ["child", "little", "school"],
       "royal": ["crown", "throne", "palace"], "common": ["village", "market", "farm"]}
filler = ["the", "a", "and", "was", "saw", "near"]

sentences = []
for _ in range(3000):
    w = rng.choice(list(people))
    words = [w]
    for prop in people[w]:
        words.append(rng.choice(cue[prop]))
    words += list(rng.choice(filler, 2))
    rng.shuffle(words)
    sentences.append(words)
vocab = sorted({w for s in sentences for w in s})
idx = {w: i for i, w in enumerate(vocab)}
V = len(vocab)
print(f"corpus: {len(sentences)} sentences, {sum(map(len, sentences))} words, vocabulary {V}")
print("example:", " ".join(sentences[0]), "|", " ".join(sentences[1]))

# -------------------------------------------- skip-gram (centre, context) pairs
window = 2
pairs = []
for s in sentences:
    ids = [idx[w] for w in s]
    for i, c in enumerate(ids):
        for j in range(max(0, i - window), min(len(ids), i + window + 1)):
            if j != i:
                pairs.append((c, ids[j]))
pairs = np.array(pairs)
counts = np.bincount(pairs[:, 1], minlength=V).astype(float)
noise = counts ** 0.75; noise /= noise.sum()   # Mikolov et al.: unigram^(3/4)

# ------------------------------------------------- 1. train with negative sampling
d, k, lr, epochs = 10, 5, 0.05, 5
Win = rng.normal(size=(V, d)) * 0.1           # centre-word vectors
Wout = np.zeros((V, d))                       # context-word vectors
sig = lambda z: 1 / (1 + np.exp(-z))
print()
print(f"1. skip-gram with negative sampling: {len(pairs)} pairs, d = {d}, k = {k} negatives")
for ep in range(epochs):
    order = rng.permutation(len(pairs))
    total = 0.0
    for start in range(0, len(order), 256):
        batch = pairs[order[start:start + 256]]
        c, o = batch[:, 0], batch[:, 1]
        neg = rng.choice(V, size=(len(batch), k), p=noise)
        vc = Win[c]                                         # (B, d)
        s_pos = sig(np.sum(vc * Wout[o], axis=1))           # want -> 1
        s_neg = sig(np.einsum("bd,bkd->bk", vc, Wout[neg]))  # want -> 0
        total += -(np.log(s_pos + 1e-10).sum() + np.log(1 - s_neg + 1e-10).sum())
        g_pos = (s_pos - 1)[:, None]                        # d loss / d score
        g_neg = s_neg[:, :, None]
        grad_vc = g_pos * Wout[o] + np.sum(g_neg * Wout[neg], axis=1)
        np.add.at(Wout, o, -lr * g_pos * vc)
        np.add.at(Wout, neg, -lr * g_neg * vc[:, None, :])
        np.add.at(Win, c, -lr * grad_vc)
    print(f"   epoch {ep + 1}: mean loss per pair {total / len(pairs):.3f}")


def unit(M):
    return M / np.linalg.norm(M, axis=1, keepdims=True)


def nearest(E, vec, exclude, n=3):
    sims = unit(E) @ (vec / np.linalg.norm(vec))
    order = [i for i in np.argsort(-sims) if vocab[i] not in exclude]
    return [(vocab[i], sims[i]) for i in order[:n]]


def report(E, title):
    print(title)
    for w in ("king", "girl", "palace"):
        nn = nearest(E, E[idx[w]], {w})
        print(f"   nearest to {w:7s}: " + ", ".join(f"{x} {s:.2f}" for x, s in nn))
    for a, b, c in [("king", "man", "woman"), ("prince", "boy", "girl"), ("queen", "woman", "girl")]:
        v = E[idx[a]] - E[idx[b]] + E[idx[c]]
        nn = nearest(E, v, {a, b, c}, 2)
        print(f"   {a} - {b} + {c} = " + ", ".join(f"{x} ({s:.2f})" for x, s in nn))


print()
report(Win, "2. the learned vectors")

# --------------------------------------- 3. the count-based view: PPMI + SVD
C = np.zeros((V, V))
np.add.at(C, (pairs[:, 0], pairs[:, 1]), 1)
total = C.sum()
pmi = np.log((C * total) / (C.sum(1, keepdims=True) * C.sum(0, keepdims=True)) + 1e-12)
ppmi = np.maximum(pmi, 0)
Uu, S, _ = np.linalg.svd(ppmi)
print()
report(Uu[:, :d] * np.sqrt(S[:d]), "3. vectors from the PPMI matrix by SVD (no training loop)")
