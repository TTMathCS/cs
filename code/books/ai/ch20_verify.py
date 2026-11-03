# Chapter 20: verifying a small ReLU network. Interval bound propagation (IBP) proves robustness
# for some inputs; branch and bound (split the input box, bound each piece) proves or refutes more.
import os
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
import numpy as np
from ch20_attack import moons, train, predict, pgd


def margin_bounds(params, lo, hi, y):
    """Lower bound, over the boxes [lo, hi] (one per row), of logit_y - logit_other. Sound by construction:
    each layer maps a box (centre c, radius r) to centre cW + b and radius r|W|, and ReLU is monotone."""
    c, r = (lo + hi) / 2, (hi - lo) / 2
    for k, (W, b) in enumerate(params):
        if k == len(params) - 1:                       # fold the difference of the two logits into W
            W = (W[:, y] - W[:, 1 - y])[:, None]; b = np.array([b[y] - b[1 - y]])
        c, r = c @ W + b, r @ np.abs(W)
        if k < len(params) - 1:
            l, u = np.maximum(c - r, 0), np.maximum(c + r, 0)
            c, r = (l + u) / 2, (u - l) / 2
    return (c - r)[:, 0]


def branch_and_bound(params, x, y, eps, budget=400):
    """Returns 'verified', 'falsified' or 'unknown' for the property: every point within eps of x
    (L-infinity) is classified y."""
    boxes = [(x - eps, x + eps)]
    used = 0
    while boxes:
        if used >= budget:
            return "unknown"
        lo = np.array([b[0] for b in boxes]); hi = np.array([b[1] for b in boxes])
        used += len(boxes)
        mid = (lo + hi) / 2
        if np.any(predict(params, mid) != y):          # a concrete counterexample
            return "falsified"
        lb = margin_bounds(params, lo, hi, y)
        nxt = []
        for (l, h), bound in zip(boxes, lb):
            if bound > 0:
                continue                               # this piece is proved safe
            d = int(np.argmax(h - l))                  # split the widest side in two
            m = (l[d] + h[d]) / 2
            h1 = h.copy(); h1[d] = m; l2 = l.copy(); l2[d] = m
            nxt += [(l, h1), (l2, h)]
        boxes = nxt
    return "verified"


params = train()
rng = np.random.default_rng(42)
X, Y = moons(1000, rng)
X, Y = X[:300], Y[:300]
print("300 test points; robust accuracy = correct for EVERY input within eps")
print("    eps   IBP proves   B&B proves   B&B refutes   unknown   PGD attack leaves")
for eps in (0.02, 0.05, 0.1, 0.15):
    ibp = sum(predict(params, X[i:i+1])[0] == Y[i] and
              margin_bounds(params, X[i:i+1] - eps, X[i:i+1] + eps, Y[i])[0] > 0 for i in range(len(X)))
    res = [branch_and_bound(params, X[i], Y[i], eps) for i in range(len(X))]
    v, f, u = res.count("verified"), res.count("falsified"), res.count("unknown")
    pgd_ok = np.sum(predict(params, pgd(params, X, Y, eps)) == Y)
    print(f"   {eps:4.2f}     {ibp / 3:5.1f}%       {v / 3:5.1f}%       {f / 3:5.1f}%      {u / 3:5.1f}%      {pgd_ok / 3:5.1f}%")
