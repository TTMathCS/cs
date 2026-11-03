# Chapter 16: a neural language model in the style of Bengio et al. (2003), from scratch in NumPy.
# The previous four words are looked up in an embedding table, concatenated, passed through a
# tanh hidden layer and a softmax over the vocabulary. Trained by minibatch gradient descent (Adam)
# on the toy corpus of ch16_grammar.py; compared with the n-gram results of ch16_ngram.py.
import math
import numpy as np
from ch16_grammar import corpus

BOS, EOS = "<s>", "</s>"
train = [w for w, _, _ in corpus(5000, 16)]
test = [w for w, _, _ in corpus(1000, 1601)]
vocab = sorted({w for s in train for w in s}) + [BOS, EOS]
idx = {w: i for i, w in enumerate(vocab)}
V, D, H, CTX = len(vocab), 12, 64, 4           # CTX: how many previous words the model sees


def examples(sents):
    X, y = [], []
    for s in sents:
        t = [BOS] * CTX + s + [EOS]
        for i in range(CTX, len(t)):
            X.append([idx[w] for w in t[i - CTX:i]])
            y.append(idx[t[i]])
    return np.array(X), np.array(y)


Xtr, ytr = examples(train)
Xte, yte = examples(test)
rng = np.random.default_rng(2003)
P = {"E": rng.normal(0, 0.1, (V, D)), "W1": rng.normal(0, 1 / math.sqrt(CTX * D), (CTX * D, H)), "b1": np.zeros(H),
     "W2": rng.normal(0, 1 / math.sqrt(H), (H, V)), "b2": np.zeros(V)}
M = {k: np.zeros_like(v) for k, v in P.items()}
S2 = {k: np.zeros_like(v) for k, v in P.items()}


def forward(X):
    e = P["E"][X].reshape(len(X), CTX * D)        # look up and concatenate the embeddings
    h = np.tanh(e @ P["W1"] + P["b1"])
    z = h @ P["W2"] + P["b2"]
    z -= z.max(axis=1, keepdims=True)
    p = np.exp(z)
    return e, h, p / p.sum(axis=1, keepdims=True)


def perplexity(X, y):
    _, _, p = forward(X)
    return math.exp(-np.mean(np.log(p[np.arange(len(y)), y])))


step = 0
print(f"{len(ytr)} training predictions, vocabulary {V}, context {CTX} words, embedding size {D}, hidden {H}")
print("epoch  train perplexity  test perplexity")
for epoch in range(1, 9):
    order = rng.permutation(len(ytr))
    for b in range(0, len(order), 128):
        j = order[b:b + 128]
        X, y = Xtr[j], ytr[j]
        e, h, p = forward(X)
        dz = p.copy()
        dz[np.arange(len(y)), y] -= 1                 # gradient of the cross-entropy loss
        dz /= len(y)
        g = {"W2": h.T @ dz, "b2": dz.sum(0)}
        dh = (dz @ P["W2"].T) * (1 - h ** 2)
        g["W1"], g["b1"] = e.T @ dh, dh.sum(0)
        de = (dh @ P["W1"].T).reshape(len(X), CTX, D)
        g["E"] = np.zeros_like(P["E"])
        np.add.at(g["E"], X, de)                      # each looked-up row gets its share of the gradient
        step += 1
        for k in P:                                   # Adam
            M[k] = 0.9 * M[k] + 0.1 * g[k]
            S2[k] = 0.999 * S2[k] + 0.001 * g[k] ** 2
            P[k] -= 0.01 * (M[k] / (1 - 0.9 ** step)) / (np.sqrt(S2[k] / (1 - 0.999 ** step)) + 1e-8)
    if epoch in (1, 2, 4, 8):
        print(f"{epoch:5d}  {perplexity(Xtr, ytr):16.3f}  {perplexity(Xte, yte):15.3f}")

E = P["E"] / np.linalg.norm(P["E"], axis=1, keepdims=True)
for w in ("rover", "sees", "with", "red"):
    sims = E @ E[idx[w]]
    near = [vocab[i] for i in np.argsort(-sims) if vocab[i] != w][:3]
    print(f"learned embedding, nearest to {w}: {', '.join(near)}")
