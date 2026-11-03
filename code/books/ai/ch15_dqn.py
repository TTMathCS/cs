# Chapter 15: a deep Q-network (the recipe of Mnih et al. 2015, much reduced) from scratch in NumPy,
# on cart-pole balancing (the dynamics of Barto, Sutton and Anderson 1983). A pole is hinged on a cart;
# push the cart left or right; reward 1 per step while the pole stays within 12 degrees of upright and
# the cart within 2.4 m of the centre; at most 200 steps. Ingredients: a neural network for Q(s, a),
# experience replay, a target network, epsilon-greedy exploration, the Huber loss and Adam.
import numpy as np


class CartPole:
    def __init__(self, rng):
        self.rng = rng

    def reset(self):
        self.s = self.rng.uniform(-0.05, 0.05, 4)          # x, x', theta, theta'
        self.t = 0
        return self.s.copy()

    def step(self, a):
        x, xd, th, thd = self.s
        f = 10.0 if a == 1 else -10.0
        g, mc, mp, l, dt = 9.8, 1.0, 0.1, 0.5, 0.02
        cos, sin = np.cos(th), np.sin(th)
        tmp = (f + mp * l * thd * thd * sin) / (mc + mp)
        thacc = (g * sin - cos * tmp) / (l * (4.0 / 3.0 - mp * cos * cos / (mc + mp)))
        xacc = tmp - mp * l * thacc * cos / (mc + mp)
        self.s = np.array([x + dt * xd, xd + dt * xacc, th + dt * thd, thd + dt * thacc])
        self.t += 1
        fell = abs(self.s[0]) > 2.4 or abs(self.s[2]) > 12 * np.pi / 180
        return self.s.copy(), 1.0, fell, self.t >= 200


class Net:
    """A two-layer network: 4 inputs, 64 ReLU units, 2 outputs (one Q value per action)."""

    def __init__(self, rng):
        self.p = {"W1": rng.normal(0, np.sqrt(2 / 4), (4, 64)), "b1": np.zeros(64),
                  "W2": rng.normal(0, np.sqrt(1 / 64), (64, 2)), "b2": np.zeros(2)}
        self.m = {k: np.zeros_like(v) for k, v in self.p.items()}
        self.v = {k: np.zeros_like(v) for k, v in self.p.items()}
        self.k = 0

    def forward(self, X):
        h = np.maximum(0, X @ self.p["W1"] + self.p["b1"])
        return h @ self.p["W2"] + self.p["b2"], h

    def train(self, X, A, target, lr=1e-3):
        q, h = self.forward(X)
        err = q[np.arange(len(A)), A] - target
        dq = np.zeros_like(q)
        dq[np.arange(len(A)), A] = np.clip(err, -1, 1) / len(A)      # gradient of the Huber loss
        grads = {"W2": h.T @ dq, "b2": dq.sum(0)}
        dh = (dq @ self.p["W2"].T) * (h > 0)
        grads["W1"], grads["b1"] = X.T @ dh, dh.sum(0)
        self.k += 1
        for n, gr in grads.items():                                   # Adam (Kingma and Ba 2014)
            self.m[n] = 0.9 * self.m[n] + 0.1 * gr
            self.v[n] = 0.999 * self.v[n] + 0.001 * gr * gr
            mh, vh = self.m[n] / (1 - 0.9 ** self.k), self.v[n] / (1 - 0.999 ** self.k)
            self.p[n] -= lr * mh / (np.sqrt(vh) + 1e-8)

    def copy_from(self, other):
        self.p = {k: v.copy() for k, v in other.p.items()}


SCALE = np.array([2.4, 3.0, 0.21, 3.0])          # rough ranges, so the inputs are of order 1


def evaluate(net, env, episodes=20):
    lengths = []
    for _ in range(episodes):
        s, done, n = env.reset(), False, 0
        while not done:
            a = int(net.forward((s / SCALE)[None])[0].argmax())
            s, r, fell, timeout = env.step(a)
            n += 1
            done = fell or timeout
        lengths.append(n)
    return np.mean(lengths)


def run(seed, steps=12000, report=True):
    rng = np.random.default_rng(seed)
    env, net, target = CartPole(rng), Net(rng), Net(rng)
    target.copy_from(net)
    cap = 20000
    S, A, R, S2, D = (np.zeros((cap, 4)), np.zeros(cap, int), np.zeros(cap), np.zeros((cap, 4)), np.zeros(cap))
    n_stored, s, ep_len, finished = 0, env.reset(), 0, []
    for t in range(steps):
        eps = max(0.05, 1 - t / 5000)
        a = int(rng.integers(2)) if rng.random() < eps else int(net.forward((s / SCALE)[None])[0].argmax())
        s2, r, fell, timeout = env.step(a)
        i = n_stored % cap
        S[i], A[i], R[i], S2[i], D[i] = s / SCALE, a, r, s2 / SCALE, float(fell)   # a timeout is not a failure
        n_stored += 1
        ep_len += 1
        s = s2
        if fell or timeout:
            finished.append(ep_len)
            s, ep_len = env.reset(), 0
        if n_stored >= 500:                                   # learn from a random minibatch of the past
            idx = rng.integers(0, min(n_stored, cap), 64)
            q_next = target.forward(S2[idx])[0].max(axis=1)
            y = R[idx] + 0.99 * (1 - D[idx]) * q_next
            net.train(S[idx], A[idx], y)
        if t % 500 == 0:
            target.copy_from(net)                             # the target network lags behind
        if report and (t + 1) % 2000 == 0:
            recent = finished[-10:] if finished else [0]
            print(f"  step {t + 1:6d}  epsilon {eps:4.2f}  episodes {len(finished):4d}"
                  f"  mean length of last 10 {np.mean(recent):6.1f}  greedy test {evaluate(net, CartPole(np.random.default_rng(99))):6.1f}")
    return net


print("random policy: mean episode length", end=" ")
env, rng = CartPole(np.random.default_rng(0)), np.random.default_rng(0)
lengths = []
for _ in range(100):
    env.reset()
    n, done = 0, False
    while not done:
        _, _, fell, timeout = env.step(int(rng.integers(2)))
        n += 1
        done = fell or timeout
    lengths.append(n)
print(f"{np.mean(lengths):.1f} steps (maximum 200)")
print("DQN training, seed 0:")
run(0)
