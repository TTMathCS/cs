# Chapter 17: learning from human preferences, from scratch on a toy problem.
# 1. a Bradley-Terry reward model fitted to pairwise comparisons;
# 2. the KL-regularised optimal policy pi_beta ~ pi_ref * exp(r / beta), and over-optimisation;
# 3. DPO, which fits the policy to the same comparisons directly, with no reward model.
import numpy as np

rng = np.random.default_rng(0)
NP, NR = 40, 8                                   # 40 prompts, 8 candidate responses each
q = rng.normal(0, 1, (NP, NR))                   # true quality of each response (what we want)
ell = -0.3 * q + rng.normal(0, 1, (NP, NR))      # its length (padding tends to lower quality)
phi = np.stack([q, ell], axis=2)                 # features the reward model can see: (NP, NR, 2)
ref_logits = rng.normal(0, 0.5, (NP, NR))
pi_ref = np.exp(ref_logits) / np.exp(ref_logits).sum(1, keepdims=True)   # the instruction-tuned model


def sig(x):
    return 1 / (1 + np.exp(-x))


def comparisons(n, seed):
    """Labellers prefer response a to b with probability sigmoid(s_a - s_b), where
    s = quality + length: they partly reward long answers."""
    r = np.random.default_rng(seed)
    x = r.integers(0, NP, n)
    a, b = r.integers(0, NR, n), r.integers(0, NR, n)
    keep = a != b
    x, a, b = x[keep], a[keep], b[keep]
    s = q + 1.0 * ell
    a_wins = r.random(len(x)) < sig(s[x, a] - s[x, b])
    win, lose = np.where(a_wins, a, b), np.where(a_wins, b, a)
    return x, win, lose


X, W, L = comparisons(2000, seed=1)
Xt, Wt, Lt = comparisons(1000, seed=2)
print(f"1. reward model: {len(X)} training comparisons, {len(Xt)} held out")
d_tr = phi[X, W] - phi[X, L]                     # feature difference, winner minus loser
w = np.zeros(2)
for _ in range(500):                             # gradient descent on -mean log sigmoid(w . d)
    grad = -(d_tr * (1 - sig(d_tr @ w))[:, None]).mean(0)
    w -= 1.0 * grad
d_te = phi[Xt, Wt] - phi[Xt, Lt]
print(f"   fitted reward r(y) = {w[0]:.3f} * quality + {w[1]:.3f} * length   (labellers used 1 and 1)")
print(f"   held-out agreement with labellers: reward model {np.mean(d_te @ w > 0):.3f}, "
      f"true quality {np.mean(d_te[:, 0] > 0):.3f}")
r_hat = phi @ w                                  # reward-model score of every response


def tilt(r, beta):
    """The maximiser of E[r] - beta * KL(pi || pi_ref): pi_ref * exp(r / beta), normalised."""
    lg = np.log(pi_ref) + r / beta
    p = np.exp(lg - lg.max(1, keepdims=True))
    return p / p.sum(1, keepdims=True)


def kl(p, ref):
    return float(np.mean(np.where(p > 0, p * np.log(np.maximum(p, 1e-300) / ref), 0).sum(1)))


print("\n2. the KL-regularised optimum for decreasing beta (averages over the 40 prompts)")
print(f"   {'beta':>6s}{'KL to ref':>11s}{'reward model':>14s}{'true quality':>14s}")
for beta in (100, 3, 1, 0.3, 0.1, 0.01):
    p = tilt(r_hat, beta)
    print(f"   {beta:6g}{kl(p, pi_ref):11.3f}{(p * r_hat).sum(1).mean():14.3f}{(p * q).sum(1).mean():14.3f}")
print(f"   best possible true quality (always pick the best response): {q.max(1).mean():.3f}")

print("\n3. DPO with beta = 1: policy log pi = log pi_ref + theta . phi - log Z, fitted to the comparisons")
beta = 1.0
theta = np.zeros(2)
for step in range(500):
    lp = np.log(pi_ref) + phi @ theta
    lp -= np.log(np.exp(lp).sum(1, keepdims=True))   # log pi_theta(y | x)
    # implicit reward difference: beta * [log pi/pi_ref (winner) - log pi/pi_ref (loser)]; log Z cancels
    m = beta * ((lp[X, W] - np.log(pi_ref[X, W])) - (lp[X, L] - np.log(pi_ref[X, L])))
    if step in (0, 499):
        print(f"   step {step:3d}: DPO loss {-np.mean(np.log(sig(m))):.4f}")
    grad = -(beta * d_tr * (1 - sig(m))[:, None]).mean(0)
    theta -= 1.0 * grad
p_dpo = np.exp(np.log(pi_ref) + phi @ theta)
p_dpo /= p_dpo.sum(1, keepdims=True)
p_rlhf = tilt(r_hat, beta)
print(f"   beta * theta = ({beta * theta[0]:.3f}, {beta * theta[1]:.3f})   reward model w = ({w[0]:.3f}, {w[1]:.3f})")
print(f"   largest gap between the DPO policy and the reward-model optimum: {np.abs(p_dpo - p_rlhf).max():.2e}")
