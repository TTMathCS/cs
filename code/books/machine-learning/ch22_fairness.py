"""Chapter 22: group fairness metrics, measured on a score that is perfectly
calibrated in both groups, and why they cannot all be equal at once."""
import numpy as np

rng = np.random.default_rng(16)

# Each person has a true risk r; the label is a coin with probability r.
# The score is r itself: perfectly calibrated, the best possible score.
# The two groups differ only in how risk is distributed (base rates 0.3 and 0.5).
groups = {"A": (3.0, 7.0), "B": (5.0, 5.0)}        # Beta(a, b) risk distributions
n = 200_000
data = {}
for g, (a, b) in groups.items():
    r = rng.beta(a, b, size=n)
    y = (rng.random(n) < r).astype(int)
    data[g] = (r, y)

def rates(score, y, t):
    pred = score >= t
    tp = np.sum(pred & (y == 1)); fp = np.sum(pred & (y == 0))
    fn = np.sum(~pred & (y == 1)); tn = np.sum(~pred & (y == 0))
    return dict(base=y.mean(), sel=pred.mean(), tpr=tp / (tp + fn), fpr=fp / (fp + tn),
                fnr=fn / (tp + fn), ppv=tp / (tp + fp),
                bal_pos=score[y == 1].mean(), bal_neg=score[y == 0].mean())

print("1. one threshold t = 0.5 for everyone, calibrated score")
print("   group  base rate  selected   TPR     FPR     PPV    E[s|y=1]  E[s|y=0]")
R = {}
for g, (s, y) in data.items():
    R[g] = rates(s, y, 0.5)
    q = R[g]
    print(f"     {g}     {q['base']:.3f}     {q['sel']:.3f}   {q['tpr']:.3f}   {q['fpr']:.3f}   "
          f"{q['ppv']:.3f}    {q['bal_pos']:.3f}     {q['bal_neg']:.3f}")

print("\n2. calibration check: in each score bin, mean score / fraction that are positive")
print("   bin             group A          group B")
edges = np.linspace(0, 1, 6)
for lo, hi in zip(edges[:-1], edges[1:]):
    row = []
    for g, (s, y) in data.items():
        m = (s >= lo) & (s < hi)
        row.append(f"{s[m].mean():.3f} / {y[m].mean():.3f}" if m.sum() > 100 else "   (empty)   ")
    print(f"   [{lo:.1f}, {hi:.1f})    {row[0]}    {row[1]}")

print("\n3. Chouldechova's identity FPR = p/(1-p) * (1-PPV)/PPV * (1-FNR), checked")
for g in data:
    q = R[g]; p = q["base"]
    rhs = p / (1 - p) * (1 - q["ppv"]) / q["ppv"] * (1 - q["fnr"])
    print(f"   group {g}: FPR {q['fpr']:.4f}   right-hand side {rhs:.4f}")

print("\n4. equalise the false positive rate with a second threshold for group B")
target = R["A"]["fpr"]
s, y = data["B"]
neg_scores = np.sort(s[y == 0])
tB = neg_scores[int(np.ceil((1 - target) * len(neg_scores)))]
qB = rates(s, y, tB)
print(f"   group B threshold {tB:.3f}: FPR {qB['fpr']:.3f} (A: {R['A']['fpr']:.3f})   "
      f"TPR {qB['tpr']:.3f} (A: {R['A']['tpr']:.3f})   PPV {qB['ppv']:.3f} (A: {R['A']['ppv']:.3f})")

print("\n5. what happens when the base rates are equal (B drawn like A)")
r2 = rng.beta(3.0, 7.0, size=n); y2 = (rng.random(n) < r2).astype(int)
q2 = rates(r2, y2, 0.5)
print(f"   new B: base {q2['base']:.3f}  TPR {q2['tpr']:.3f}  FPR {q2['fpr']:.3f}  PPV {q2['ppv']:.3f}"
      f"  E[s|y=1] {q2['bal_pos']:.3f}  E[s|y=0] {q2['bal_neg']:.3f}   (all match group A)")
