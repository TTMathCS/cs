# Chapter 16: word vectors from counts: a co-occurrence matrix, positive pointwise mutual
# information (PPMI), and a truncated SVD, from scratch on the toy corpus of ch16_grammar.py.
import numpy as np
from ch16_grammar import corpus

sents = [w for w, _, _ in corpus(5000, 16)]
vocab = sorted({w for s in sents for w in s})
idx = {w: i for i, w in enumerate(vocab)}
V = len(vocab)
CTX = vocab + ["<s>", "</s>"]                    # context words include the sentence boundaries
cidx = {w: i for i, w in enumerate(CTX)}


def cooccurrence(window, directional):
    """C[w, c]: how often context c occurs within `window` words of w. If directional, a context
    on the left and the same word on the right are different columns."""
    C = np.zeros((V, 2 * len(CTX) if directional else len(CTX)))
    for s in sents:
        t = ["<s>"] + s + ["</s>"]
        for i in range(1, len(t) - 1):
            for d in range(1, window + 1):
                for j, side in ((i - d, 0), (i + d, 1)):
                    if 0 <= j < len(t):
                        C[idx[t[i]], cidx[t[j]] + (side * len(CTX) if directional else 0)] += 1
    return C[:, C.sum(axis=0) > 0]


def ppmi(C):
    total = C.sum()
    pw = C.sum(axis=1, keepdims=True) / total
    pc = C.sum(axis=0, keepdims=True) / total
    with np.errstate(divide="ignore"):
        return np.maximum(np.log((C / total) / (pw * pc)), 0)   # PPMI = max(0, log P(w,c) / (P(w) P(c)))


def vectors(M, k):
    U, S, _ = np.linalg.svd(M, full_matrices=False)
    vec = U[:, :k] * S[:k]
    return vec / np.linalg.norm(vec, axis=1, keepdims=True), U, S


def neighbours(vec, w, n=4):
    sims = vec @ vec[idx[w]]
    order = [vocab[i] for i in np.argsort(-sims) if vocab[i] != w]
    return ", ".join(f"{o} {sims[idx[o]]:.2f}" for o in order[:n])


C_dir = cooccurrence(2, True)
P = ppmi(C_dir)
vec, U, S = vectors(P, 10)
print(f"{V} words, {C_dir.shape[1]} context columns (left and right); top singular values {np.round(S[:6], 2)}")
for w in ("rover", "sees", "red", "with", "stops", "drills"):
    print(f"  nearest to {w:6s}: {neighbours(vec, w)}")

vec_undir, _, _ = vectors(ppmi(cooccurrence(2, False)), 10)
print("without left/right distinction, nearest to with:", neighbours(vec_undir, "with"))

C = cooccurrence(2, False)
print("\nraw count of 'the' near rover", int(C[idx['rover'], cidx['the']]), "and near sees",
      int(C[idx['sees'], cidx['the']]), "; PPMI", round(ppmi(C)[idx['rover'], cidx['the']], 3), "and",
      round(ppmi(C)[idx['sees'], cidx['the']], 3), " ('the' is everywhere, so PPMI discounts it)")

print("coordinates in SVD dimensions 2 and 3 (for the figure):")
for w in ("rover", "rock", "crater", "dune", "sees", "finds", "follows", "red", "small", "dusty",
          "with", "near", "on", "stops", "waits", "drills", "tracks"):
    print(f"  {w:8s} {U[idx[w], 1] * S[1]:7.3f} {U[idx[w], 2] * S[2]:7.3f}")
