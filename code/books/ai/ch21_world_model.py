# Chapter 21: learning a world model from data and planning inside it.
# True world: a damped pendulum with a weak motor, theta'' = -9.8 sin(theta) - 0.3 theta' + u,
# |u| <= 4, too weak to lift it straight up: it must be swung back and forth.
# Two learned models, both fitted by least squares on 2000 random noisy transitions:
#   "linear":   next state = A [theta, omega, u, 1]          (a small-angle world view)
#   "features": next state = A [theta, omega, u, 1, sin theta, cos theta]
# We measure multi-step prediction error, then plan with random-shooting model-predictive control.
import numpy as np

rng = np.random.default_rng(0)
DT = 0.05


def true_step(s, u):
    th, om = s[..., 0], s[..., 1]
    om2 = om + DT * (-9.8 * np.sin(th) - 0.3 * om + u)
    return np.stack([th + DT * om2, om2], -1)


def feats(s, u, kind):
    th, om = s[..., 0], s[..., 1]
    base = [th, om, u, np.ones_like(th)]
    if kind == "features":
        base += [np.sin(th), np.cos(th)]
    return np.stack(base, -1)


S = np.column_stack([rng.uniform(-np.pi, np.pi, 2000), rng.uniform(-6, 6, 2000)])
U = rng.uniform(-4, 4, 2000)
S2 = true_step(S, U) + rng.normal(0, 0.01, (2000, 2))     # measured with a little sensor noise
models = {k: np.linalg.lstsq(feats(S, U, k), S2, rcond=None)[0] for k in ("linear", "features")}
step = {"true": true_step}
for k, A in models.items():
    step[k] = (lambda A, k: lambda s, u: feats(s, u, k) @ A)(A, k)

# multi-step prediction error from random starts under random controls
starts = np.column_stack([rng.uniform(-np.pi, np.pi, 300), rng.uniform(-3, 3, 300)])
ctrl = rng.uniform(-4, 4, (300, 40))
print("mean angle error (radians) after h steps of imagined rollout")
print("    h   linear model   feature model")
traj = {k: starts.copy() for k in step}
for h in range(1, 41):
    for k in step:
        traj[k] = step[k](traj[k], ctrl[:, h - 1])
    if h in (1, 5, 10, 20, 40):
        e = {k: np.mean(np.abs(np.angle(np.exp(1j * (traj[k][:, 0] - traj["true"][:, 0]))))) for k in models}
        print(f"   {h:>2}     {e['linear']:7.3f}        {e['features']:7.4f}")


def mpc(model, steps=200, horizon=40, samples=400):
    """Swing up from hanging down: each step, imagine `samples` random control sequences with the model,
    execute the first control of the best one in the TRUE world, repeat."""
    s = np.array([0.0, 0.0])
    cost_true = 0.0
    for t in range(steps):
        seqs = np.repeat(rng.uniform(-4, 4, (samples, horizon // 5)), 5, axis=1)   # hold each control 5 steps
        sim = np.repeat(s[None], samples, 0); cost = np.zeros(samples)
        for h in range(horizon):
            sim = step[model](sim, seqs[:, h])
            cost += (1 + np.cos(sim[:, 0])) + 0.01 * sim[:, 1] ** 2   # 0 when upright and still
        s = true_step(s, seqs[np.argmin(cost), 0])
        cost_true += (1 + np.cos(s[0]))
    return cost_true / steps, abs(np.angle(np.exp(1j * (s[0] - np.pi))))


print("\nswing-up by planning in imagination (200 control steps); lower is better")
print("   model used for planning   average (1 + cos theta) in the real world   final distance from upright")
for k in ("true", "features", "linear"):
    c, dist = mpc(k)
    print(f"   {k:<25} {c:10.3f}                                  {dist:6.3f} rad")
