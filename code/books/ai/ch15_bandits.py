# Chapter 15: multi-armed bandits from scratch: greedy, epsilon-greedy and UCB1.
# 10 arms; each arm pays 1 with its own probability (Bernoulli rewards). 200 independent
# runs of 20000 pulls each, all simulated at once with NumPy (one row per run).
import numpy as np

K, STEPS, RUNS = 10, 20000, 200
rng = np.random.default_rng(2002)
probs = rng.uniform(0.2, 0.8, (RUNS, K))       # every run gets its own random bandit
best = probs.max(axis=1)
rows = np.arange(RUNS)


def run(choose):
    counts = np.zeros((RUNS, K))
    means = 1e-6 * rng.random((RUNS, K))       # tiny random start values break ties at random
    regret = np.zeros(STEPS)
    picked_best = np.zeros(STEPS)
    for t in range(STEPS):
        a = choose(t, counts, means)
        r = (rng.random(RUNS) < probs[rows, a]).astype(float)
        counts[rows, a] += 1
        means[rows, a] += (r - means[rows, a]) / counts[rows, a]     # incremental average
        regret[t] = np.mean(best - probs[rows, a])
        if t >= STEPS - 1000:
            picked_best[t] = np.mean(probs[rows, a] == best)
    return np.cumsum(regret), picked_best


def eps_greedy(eps):
    def choose(t, counts, means):
        greedy = np.argmax(means, axis=1)
        explore = rng.random(RUNS) < eps
        return np.where(explore, rng.integers(0, K, RUNS), greedy)
    return choose


def ucb1(t, counts, means):
    if t < K:                                   # pull every arm once
        return np.full(RUNS, t)
    bonus = np.sqrt(2 * np.log(t) / counts)
    return np.argmax(means + bonus, axis=1)


print("method            regret after 100   after 1000   after 5000   after 20000   best arm chosen (last 1000 pulls)")
for name, chooser in [("greedy", eps_greedy(0.0)), ("eps-greedy 0.01", eps_greedy(0.01)),
                      ("eps-greedy 0.1", eps_greedy(0.1)), ("UCB1", ucb1)]:
    cum, pb = run(chooser)
    print(f"{name:16s}  {cum[99]:16.1f}  {cum[999]:11.1f}  {cum[4999]:11.1f}  {cum[-1]:12.1f}   {pb[-1000:].mean():10.3f}")

# the UCB1 regret bound of Auer et al. (2002) for one bandit: 8 sum ln n / gap + (1 + pi^2/3) sum gap
p = probs[0]
gaps = p.max() - p
gaps = gaps[gaps > 0]
for n in (1000, 20000):
    bound = 8 * np.log(n) * np.sum(1 / gaps) + (1 + np.pi ** 2 / 3) * np.sum(gaps)
    print(f"run 0, n = {n}: UCB1 regret bound {bound:.1f}")
