# Chapter 15: policy gradients from scratch on the "short corridor" (Sutton and Barto, Example 13.1).
# Three squares then the goal; reward -1 per step. In the middle square the actions are reversed
# (right moves left). The agent cannot tell the squares apart, so its policy is one number:
# p = P(right) = sigmoid(theta). The best deterministic policies never finish; the best policy is stochastic.
import math
import random


def sigmoid(z):
    return 1 / (1 + math.exp(-z))


def true_value(p):
    """Expected return from the start, by solving the three Bellman equations for a fixed p."""
    # v0 = -1 + p v1 + (1-p) v0 ; v1 = -1 + p v0 + (1-p) v2 ; v2 = -1 + (1-p) v1   (right from 2 reaches the goal)
    if p <= 0 or p >= 1:
        return -math.inf
    # from the first: v0 = v1 - 1/p ; from the third: v2 = -1 + (1-p) v1 ; substitute into the second
    # v1 = -1 + p (v1 - 1/p) + (1-p)(-1 + (1-p) v1)  =>  v1 (1 - p - (1-p)^2) = -1 - 1 - (1-p)
    v1 = (-3 + p) / (1 - p - (1 - p) ** 2)
    return v1 - 1 / p


def episode(p, rng, cap=1000):
    s, traj = 0, []
    while s != 3 and len(traj) < cap:
        right = rng.random() < p
        traj.append((s, right))
        if s == 1:
            s = 0 if right else 2                  # reversed in the middle square
        else:
            s = s + 1 if right else max(0, s - 1)
    return traj                                    # every step has reward -1


def grad_log(p, right):
    return (1 - p) if right else -p                # d/dtheta of log pi(action)


CHECK = (100, 300, 1000)                           # report P(right) after these many episodes


def reinforce(rng, alpha, baseline=False, alpha_w=0.0):
    theta, w, out = math.log(0.05 / 0.95), 0.0, []  # start with P(right) = 0.05
    for k in range(1, CHECK[-1] + 1):
        p = sigmoid(theta)
        traj = episode(p, rng)
        T = len(traj)
        for t, (s, right) in enumerate(traj):
            G = -(T - t)                           # return from step t (gamma = 1)
            delta = G - w if baseline else G
            if baseline:
                w += alpha_w * delta               # the baseline learns the average return
            theta += alpha * delta * grad_log(p, right)
        if k in CHECK:
            out.append(sigmoid(theta))
    return out


def actor_critic(rng, alpha, alpha_v):
    """One-step actor-critic. The critic sees the square (a table V); the actor still cannot."""
    theta, V, out = math.log(0.05 / 0.95), [0.0, 0.0, 0.0, 0.0], []
    for k in range(1, CHECK[-1] + 1):
        s, n = 0, 0
        while s != 3 and n < 1000:
            p = sigmoid(theta)
            right = rng.random() < p
            s2 = (0 if right else 2) if s == 1 else (s + 1 if right else max(0, s - 1))
            delta = -1 + V[s2] - V[s]              # TD error: the critic's surprise
            V[s] += alpha_v * delta
            theta += alpha * delta * grad_log(p, right)
            s, n = s2, n + 1
        if k in CHECK:
            out.append(sigmoid(theta))
    return out


def ppo(rng, batch=10, epochs=4, clip=0.2, lr=0.5):
    """PPO-clip (Schulman et al. 2017): reuse each batch for several gradient steps, but stop the
    ratio pi_new/pi_old from moving outside [1 - clip, 1 + clip] where that would help the objective."""
    theta, out = math.log(0.05 / 0.95), []
    for it in range(1, CHECK[-1] // batch + 1):
        p_old = sigmoid(theta)
        data = []
        for _ in range(batch):
            traj = episode(p_old, rng)
            T = len(traj)
            data += [(s, right, -(T - t)) for t, (s, right) in enumerate(traj)]
        mean = {s: sum(G for s2, _, G in data if s2 == s) / max(1, sum(1 for s2, _, _ in data if s2 == s))
                for s in range(3)}
        adv = [(right, G - mean[s]) for s, right, G in data]           # advantage: return minus a baseline
        scale = max(1e-8, (sum(a * a for _, a in adv) / len(adv)) ** 0.5)
        for _ in range(epochs):
            p = sigmoid(theta)
            g = 0.0
            for right, a in adv:
                a /= scale
                ratio = (p / p_old) if right else ((1 - p) / (1 - p_old))
                if (a > 0 and ratio < 1 + clip) or (a < 0 and ratio > 1 - clip):
                    g += a * ratio * grad_log(p, right)               # gradient of ratio * advantage
            theta += lr * g / len(adv)
        if it * batch in CHECK:
            out.append(sigmoid(theta))
    return out


ps = [i / 1000 for i in range(1, 1000)]
best_p = max(ps, key=true_value)
print(f"exact: best P(right) = {best_p:.3f}, value {true_value(best_p):.2f};"
      f" P(right) = 0.05 gives {true_value(0.05):.2f}, P(right) = 0.95 gives {true_value(0.95):.2f}")

RUNS = 30
print(f"\nP(right) learned (mean over {RUNS} runs) and its true value")
print("method                    after 100        after 300        after 1000 episodes")
for name, f in [("REINFORCE", lambda rng: reinforce(rng, 2 ** -12)),
                ("REINFORCE with baseline", lambda rng: reinforce(rng, 2 ** -9, True, 2 ** -6)),
                ("actor-critic", lambda rng: actor_critic(rng, 2 ** -6, 2 ** -3)),
                ("PPO, batches of 10", lambda rng: ppo(rng))]:
    res = [f(random.Random(run)) for run in range(RUNS)]
    cells = []
    for j in range(len(CHECK)):
        p = sum(r[j] for r in res) / RUNS
        cells.append(f"{p:.3f} ({true_value(p):6.2f})")
    print(f"{name:24s}  " + "  ".join(cells))
