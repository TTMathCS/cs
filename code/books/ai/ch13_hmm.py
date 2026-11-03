# Chapter 13: hidden Markov models from scratch.
# The umbrella world: the hidden state is Rain (1) or not (0); the guard sees an umbrella or not.
# Filtering (forward algorithm), prediction, smoothing (forward-backward) and Viterbi.
import numpy as np

T = np.array([[0.7, 0.3],        # T[i, j] = P(X_t = j | X_{t-1} = i), state 0 = rain, 1 = no rain
              [0.3, 0.7]])
O = np.array([[0.9, 0.1],        # O[i, e] = P(E_t = e | X_t = i), evidence 0 = umbrella, 1 = none
              [0.2, 0.8]])
prior = np.array([0.5, 0.5])


def forward(evidence, T=T, O=O, prior=prior):
    """Return the filtered distributions f_1..f_t (normalised) and log P(e_1..e_t)."""
    f, out, loglik = prior, [], 0.0
    for e in evidence:
        g = O[:, e] * (f @ T)        # predict with T, then weight by the evidence
        z = g.sum()
        loglik += np.log(z)
        f = g / z
        out.append(f)
    return np.array(out), loglik


def backward(evidence, T=T, O=O):
    """Return b_k = P(e_{k+1..t} | X_k) for k = 1..t, each rescaled to sum to 1."""
    b, out = np.ones(2), []
    for e in reversed(evidence):
        out.append(b)
        b = T @ (O[:, e] * b)
        b = b / b.sum()
    return np.array(out[::-1])


def smooth(evidence, T=T, O=O, prior=prior):
    f, _ = forward(evidence, T, O, prior)
    b = backward(evidence, T, O)
    s = f * b
    return s / s.sum(axis=1, keepdims=True)


def viterbi(evidence, T=T, O=O, prior=prior):
    """Most likely state sequence, in log space."""
    lT, lO = np.log(T), np.log(O)
    m = np.log(prior @ T) + lO[:, evidence[0]]
    back = []
    for e in evidence[1:]:
        cand = m[:, None] + lT            # cand[i, j]: best path ending in i, then i -> j
        back.append(cand.argmax(axis=0))
        m = cand.max(axis=0) + lO[:, e]
    path = [int(m.argmax())]
    for bp in reversed(back):
        path.append(int(bp[path[-1]]))
    return path[::-1], m.max()


def sample(n, rng, T=T, O=O, prior=prior):
    x, xs, es = rng.choice(2, p=prior), [], []
    for _ in range(n):
        x = rng.choice(2, p=T[x])
        xs.append(x)
        es.append(rng.choice(2, p=O[x]))
    return xs, es


name = {0: "U", 1: "-"}
ev = [0, 0, 1, 0, 0]                      # umbrella, umbrella, none, umbrella, umbrella
f, ll = forward(ev)
s = smooth(ev)
print("evidence     :", " ".join(name[e] for e in ev))
print("day  P(rain | e_1..t) filtered   P(rain | e_1..5) smoothed")
for k in range(len(ev)):
    print(f"{k + 1:3d}  {f[k, 0]:10.4f}                 {s[k, 0]:10.4f}")
print(f"P(e_1..5) = {np.exp(ll):.6f}")

p = f[-1]
print("prediction from day 5:", end="")
for k in range(1, 26):
    p = p @ T
    if k in (1, 2, 5, 10, 25):
        print(f"  day {5 + k}: {p[0]:.4f}", end="")
print()

path, lp = viterbi(ev)
print("Viterbi path :", " ".join("R" if x == 0 else "." for x in path), f" probability {np.exp(lp):.6f}")

# brute force check: enumerate all 2^5 state sequences
best, bestp, total = None, -1.0, 0.0
for code in range(32):
    xs = [(code >> (4 - i)) & 1 for i in range(5)]
    pr, prev = 1.0, prior
    for x, e in zip(xs, ev):
        pr *= prev[x] * O[x, e]
        prev = T[x]
    total += pr
    if pr > bestp:
        best, bestp = xs, pr
print("brute force  :", " ".join("R" if x == 0 else "." for x in best), f" probability {bestp:.6f}",
      f"  sum over all sequences {total:.6f}")

# long sampled runs: how often does each method guess the hidden state right?
def accuracy(label, T2, O2, seed):
    rng = np.random.default_rng(seed)
    xs, es = sample(10000, rng, T2, O2, prior)
    f, ll = forward(es, T2, O2, prior)
    s = smooth(es, T2, O2, prior)
    vp, _ = viterbi(es, T2, O2, prior)
    xs = np.array(xs)
    print(f"{label}: log P(e) = {ll:8.1f}   filtering {np.mean(f.argmax(1) == xs):.4f}"
          f"   smoothing {np.mean(s.argmax(1) == xs):.4f}   Viterbi {np.mean(np.array(vp) == xs):.4f}"
          f"   today's evidence alone {np.mean((np.array(es) == 0) == (xs == 0)):.4f}")


print("\n10000 sampled days, fraction of days whose hidden state is guessed right")
accuracy("umbrella world   ", T, O, 13)
accuracy("sticky, poor eyes", np.array([[0.9, 0.1], [0.1, 0.9]]), np.array([[0.7, 0.3], [0.3, 0.7]]), 13)
