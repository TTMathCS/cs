# Chapter 21: learned perception + exact symbolic reasoning, trained end to end.
# Each "image" is a noisy 8-dimensional feature vector of a digit 0-9. We never see digit labels:
# we only see pairs of images and the SUM of their digits (the task of Manhaeve et al. 2018).
# A softmax classifier gives P(digit | image); exact inference gives P(sum) = sum_a P1(a) P2(s - a);
# we maximise log P(observed sum) by gradient ascent.
import os
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
import numpy as np

rng = np.random.default_rng(0)
D = 8
MEANS = rng.normal(0, 1.0, (10, D))            # one prototype per digit


def images(digits):
    return MEANS[digits] + rng.normal(0, 0.45, (len(digits), D))


def softmax(Z):
    Z = Z - Z.max(1, keepdims=True); E = np.exp(Z); return E / E.sum(1, keepdims=True)


n = 6000
d1, d2 = rng.integers(0, 10, n), rng.integers(0, 10, n)
X1, X2, S = images(d1), images(d2), d1 + d2          # the learner is given X1, X2 and S only
dt = rng.integers(0, 10, 2000); Xt = images(dt)       # held-out single images, to measure digit accuracy

W = rng.normal(0, 0.01, (D, 10)); b = np.zeros(10)
# mask[s, a, c] = 1 when a + c = s: the "program" that links digits to sums
mask = np.zeros((19, 10, 10))
for a in range(10):
    for c in range(10):
        mask[a + c, a, c] = 1
M = mask[S]                                           # one 10x10 mask per training pair
for epoch in range(301):
    P1, P2 = softmax(X1 @ W + b), softmax(X2 @ W + b)
    joint = P1[:, :, None] * P2[:, None, :] * M       # P1(a) P2(c), only where a + c = s
    Z = joint.sum((1, 2))                             # P(observed sum)
    R1, R2 = joint.sum(2) / Z[:, None], joint.sum(1) / Z[:, None]   # posterior over each digit
    G1, G2 = R1 - P1, R2 - P2                         # gradient of log Z w.r.t. each logit vector
    W += 0.5 * (X1.T @ G1 + X2.T @ G2) / n; b += 0.5 * (G1.sum(0) + G2.sum(0)) / n
    if epoch in (0, 10, 30, 100, 300):
        acc = np.mean(softmax(Xt @ W + b).argmax(1) == dt)
        sum_acc = np.mean(np.array([np.argmax([np.sum(np.outer(p, q) * mask[s]) for s in range(19)])
                                    for p, q in zip(P1[:500], P2[:500])]) == S[:500])
        print(f"epoch {epoch:>3}: mean log P(sum) {np.log(Z).mean():7.3f}   "
              f"sum accuracy {sum_acc:.3f}   digit accuracy (never trained on digits) {acc:.3f}")

pred = softmax(Xt @ W + b).argmax(1)
conf = np.zeros((10, 10), int)
for t, p in zip(dt, pred):
    conf[t, p] += 1
print("\nconfusion matrix of the learned digit classifier (rows: true digit, columns: predicted)")
for t in range(10):
    print("   ", t, " ".join(f"{v:3d}" for v in conf[t]))
