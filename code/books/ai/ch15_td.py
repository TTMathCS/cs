# Chapter 15: Monte Carlo versus temporal-difference prediction on the 5-state random walk
# (Sutton 1988; Sutton and Barto, Example 6.2). States A..E; start in C; step left or right
# with probability 1/2; leaving on the right earns 1, on the left 0. True values: 1/6, ..., 5/6.
import numpy as np

TRUE = np.arange(1, 6) / 6
rng = np.random.default_rng(1988)


def episode():
    s, states = 2, []
    while 0 <= s <= 4:
        states.append(s)
        s += 1 if rng.random() < 0.5 else -1
    return states, (1.0 if s == 5 else 0.0)


def td0(V, states, reward, alpha):
    for i, s in enumerate(states):
        if i + 1 < len(states):
            target = V[states[i + 1]]           # reward 0 on non-final steps, gamma = 1
        else:
            target = reward                     # the next state is terminal, worth 0
        V[s] += alpha * (target - V[s])


def mc(V, states, reward, alpha):
    for s in states:                            # every visit; the return from s is the final reward
        V[s] += alpha * (reward - V[s])


def rms_curve(update, alpha, episodes=100, runs=100):
    err = np.zeros(episodes)
    for _ in range(runs):
        V = np.full(5, 0.5)
        for k in range(episodes):
            update(V, *episode(), alpha)
            err[k] += np.sqrt(np.mean((V - TRUE) ** 2))
    return err / runs


# one episode traced by hand
V = np.full(5, 0.5)
states, reward = [2, 3, 2, 3, 4], 1.0                # C D C D E, then exit right
td0(V, states, reward, 0.1)
print("after C D C D E -> exit right (reward 1), alpha = 0.1")
print("  TD(0) values A..E:", np.round(V, 4))
V = np.full(5, 0.5)
mc(V, states, reward, 0.1)
print("  MC    values A..E:", np.round(V, 4))

print("\nRMS error averaged over states and 100 runs")
print("method           alpha   after 1   after 10   after 50   after 100 episodes")
for name, upd, alphas in [("TD(0)", td0, (0.05, 0.1, 0.15)), ("Monte Carlo", mc, (0.01, 0.02, 0.04))]:
    for a in alphas:
        e = rms_curve(upd, a)
        print(f"{name:15s}  {a:5.2f}   {e[0]:7.3f}   {e[9]:8.3f}   {e[49]:8.3f}   {e[99]:9.3f}")
