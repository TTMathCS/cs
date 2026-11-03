# Chapter 19: learning with other learners.
# (1) regret matching (Hart and Mas-Colell 2000) in self-play on rock-paper-scissors;
# (2) simultaneous gradient ascent in matching pennies spirals away from the equilibrium;
# (3) independent Q-learners versus one joint learner in the climbing game (Claus and Boutilier 1998).
import random
import numpy as np

# ---------- (1) regret matching ----------
RPS = np.array([[0, -1, 1], [1, 0, -1], [-1, 1, 0]], dtype=float)   # row player's payoff


def regret_matching(A, T):
    """Each player plays in proportion to positive cumulative regret, against the other's
    current mixed strategy (expected payoffs, so no sampling noise)."""
    m, n = A.shape
    reg_r, reg_c = np.zeros(m), np.zeros(n)
    reg_r[0] = 1.0                            # start both players off on Rock
    reg_c[0] = 1.0
    sum_r, sum_c = np.zeros(m), np.zeros(n)
    out = []
    for t in range(1, T + 1):
        pr = np.maximum(reg_r, 0); pr = pr / pr.sum() if pr.sum() > 0 else np.full(m, 1 / m)
        pc = np.maximum(reg_c, 0); pc = pc / pc.sum() if pc.sum() > 0 else np.full(n, 1 / n)
        u_r = A @ pc                          # payoff of each pure row against pc
        u_c = -(pr @ A)                       # column player's payoff is -A
        reg_r += u_r - pr @ u_r               # how much better each pure strategy would have done
        reg_c += u_c - pc @ u_c
        sum_r += pr; sum_c += pc
        if t in (10, 100, 1000, 10000, 100000):
            xr, xc = sum_r / t, sum_c / t
            gap = (A @ xc).max() - (xr @ A).min()   # exploitability of the average strategies
            out.append((t, xr, pr, gap))
    return out


print("Regret matching, self-play on rock-paper-scissors (row player)")
print("        t   average strategy      current strategy      exploitability of averages")
for t, x, cur, gap in regret_matching(RPS, 100000):
    print(f"   {t:>6}   {np.round(x, 3)}   {np.round(cur, 3)}   {gap:.4f}")

# ---------- (2) gradient ascent in matching pennies ----------
# Row picks Heads with probability p, column with probability q.
# u_row = (2p-1)(2q-1), u_col = -u_row. Each follows its own gradient with step 0.05.
p, q = 0.6, 0.5
print("\nSimultaneous gradient ascent in matching pennies, step 0.05, start (p, q) = (0.6, 0.5)")
for step in range(0, 301):
    if step % 50 == 0:
        print(f"   step {step:>3}  p={p:.3f}  q={q:.3f}  distance from (0.5, 0.5) {np.hypot(p - .5, q - .5):.3f}")
    gp, gq = 2 * (2 * q - 1), -2 * (2 * p - 1)
    p, q = float(np.clip(p + 0.05 * gp, 0, 1)), float(np.clip(q + 0.05 * gq, 0, 1))

# ---------- (3) the climbing game ----------
CLIMB = np.array([[11, -30, 0], [-30, 7, 6], [0, 0, 5]], dtype=float)   # both agents get this reward


R = CLIMB.tolist()
argmax = lambda v: max(range(len(v)), key=v.__getitem__)


def independent(rng, episodes=2000, eps=0.1, alpha=0.1):
    """Each agent keeps Q over its OWN 3 actions and treats the other as part of the world."""
    Q1, Q2 = [0.0] * 3, [0.0] * 3
    for _ in range(episodes):
        a = rng.randrange(3) if rng.random() < eps else argmax(Q1)
        b = rng.randrange(3) if rng.random() < eps else argmax(Q2)
        r = R[a][b]
        Q1[a] += alpha * (r - Q1[a]); Q2[b] += alpha * (r - Q2[b])
    return argmax(Q1), argmax(Q2)


def joint(rng, episodes=2000, eps=0.1, alpha=0.1):
    """One learner keeps Q over all 9 joint actions (a central controller)."""
    Q = [0.0] * 9
    for _ in range(episodes):
        k = rng.randrange(9) if rng.random() < eps else argmax(Q)
        Q[k] += alpha * (R[k // 3][k % 3] - Q[k])
    k = argmax(Q)
    return k // 3, k % 3


names = "abc"
for label, learner in (("independent Q-learners", independent), ("one learner over joint actions", joint)):
    rng = random.Random(1)
    tally = {}
    for _ in range(200):
        a, b = learner(rng)
        tally[names[a] + names[b]] = tally.get(names[a] + names[b], 0) + 1
    res = ", ".join(f"({k[0]},{k[1]}) reward {CLIMB[names.index(k[0]), names.index(k[1])]:.0f}: {v}"
                    for k, v in sorted(tally.items(), key=lambda kv: -kv[1]))
    print(f"\nClimbing game, {label}, 200 runs, final greedy joint action:\n   {res}")
