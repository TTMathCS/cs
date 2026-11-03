# Chapter 13: Kalman filters from scratch.
# Part 1: the 1-D filter for a random walk, step by step, and its steady state.
# Part 2: the matrix filter tracking position and velocity from noisy position readings.
import numpy as np


def kalman_1d(zs, mu0, var0, q, r):
    """Random walk x_t = x_{t-1} + noise(q); reading z_t = x_t + noise(r)."""
    mu, var, rows = mu0, var0, []
    for z in zs:
        var_pred = var + q                      # predict: the uncertainty grows
        k = var_pred / (var_pred + r)           # Kalman gain: how much to trust the reading
        mu = mu + k * (z - mu)                  # update: move toward the reading
        var = (1 - k) * var_pred
        rows.append((z, var_pred, k, mu, var))
    return rows


print("Part 1. 1-D random walk, q = 1, r = 4, start mean 0, variance 100")
rows = kalman_1d([2.5, 1.0, 3.5, 2.0, 2.8], 0.0, 100.0, 1.0, 4.0)
print(" t   reading  pred.var    gain     mean   variance")
for t, (z, vp, k, mu, var) in enumerate(rows, 1):
    print(f"{t:2d}   {z:6.2f}  {vp:8.3f}  {k:6.4f}  {mu:7.4f}  {var:8.4f}")
q, r = 1.0, 4.0
steady = (-q + np.sqrt(q * q + 4 * q * r)) / 2
print(f"steady-state variance (-q + sqrt(q^2 + 4qr)) / 2 = {steady:.4f}, gain {(steady + q) / (steady + q + r):.4f}")
rows = kalman_1d([0.0] * 30, 0.0, 100.0, q, r)
print(f"variance after 30 steps from the filter itself: {rows[-1][4]:.4f}")

# Part 2: constant-velocity tracking. State (position, velocity); we read only the position.
rng = np.random.default_rng(1960)
dt, n = 1.0, 60
F = np.array([[1, dt], [0, 1]])                 # motion model
H = np.array([[1.0, 0.0]])                      # sensor reads the position only
Q = 0.01 * np.array([[dt ** 3 / 3, dt ** 2 / 2], [dt ** 2 / 2, dt]])   # small random accelerations
R = np.array([[25.0]])                          # reading noise: standard deviation 5 metres

x_true = np.array([0.0, 2.0])                   # starts at 0 m, moving at 2 m per step
truth, zs = [], []
for _ in range(n):
    x_true = F @ x_true + rng.multivariate_normal([0, 0], Q)
    truth.append(x_true.copy())
    zs.append(H @ x_true + rng.normal(0, 5.0, 1))
truth, zs = np.array(truth), np.array(zs)

x, P = np.array([0.0, 0.0]), np.diag([100.0, 25.0])  # vague start: position and speed unknown
est, var_pos = [], []
for z in zs:
    x = F @ x                                   # predict
    P = F @ P @ F.T + Q
    S = H @ P @ H.T + R                         # update
    K = P @ H.T @ np.linalg.inv(S)
    x = x + K @ (z - H @ x)
    P = (np.eye(2) - K @ H) @ P
    est.append(x.copy())
    var_pos.append(P[0, 0])
est = np.array(est)

print("\nPart 2. tracking position and velocity, reading noise sd 5 m")
print(" step  true pos  reading  estimate  true vel  est. vel  sd(pos)")
for t in (0, 1, 2, 5, 10, 20, 40, 59):
    print(f"{t + 1:5d}  {truth[t, 0]:8.2f}  {zs[t, 0]:7.2f}  {est[t, 0]:8.2f}  {truth[t, 1]:8.3f}"
          f"  {est[t, 1]:8.3f}  {np.sqrt(var_pos[t]):7.3f}")
late = slice(10, n)
print(f"RMS position error, steps 11-60: readings {np.sqrt(np.mean((zs[late, 0] - truth[late, 0]) ** 2)):.3f} m,"
      f" filter {np.sqrt(np.mean((est[late, 0] - truth[late, 0]) ** 2)):.3f} m")
print("final gain K =", np.round(K.ravel(), 4))
