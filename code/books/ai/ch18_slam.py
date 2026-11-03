# Chapter 18: the SLAM idea in its simplest exact form. A robot drives a loop, measures its own motion
# (odometry) and the relative positions of landmarks. With the heading known, every measurement is linear
# in the unknowns, so the best estimate of the whole path AND the map is one weighted least-squares solve.
import numpy as np

rng = np.random.default_rng(3)
# true path: a 10 m square, 1 m per step, 40 steps, back to the start
moves = [(1, 0)] * 10 + [(0, 1)] * 10 + [(-1, 0)] * 10 + [(0, -1)] * 10
true_x = np.vstack([[0, 0], np.cumsum(moves, axis=0)]).astype(float)
T = len(true_x)                                   # 41 poses
true_m = np.array([[2, -2], [8, -2], [12, 2], [12, 8], [8, 12], [2, 12], [-2, 8], [-2, 2]], float)
M = len(true_m)
SIG_U, SIG_Z, RANGE = 0.15, 0.05, 4.5

odo = np.diff(true_x, axis=0) + rng.normal(0, SIG_U, (T - 1, 2))     # measured steps
obs = []                                          # (time, landmark, measured landmark - pose)
for t in range(T):
    for j in range(M):
        if np.linalg.norm(true_m[j] - true_x[t]) <= RANGE:
            obs.append((t, j, true_m[j] - true_x[t] + rng.normal(0, SIG_Z, 2)))


def solve(observations):
    """Unknowns: poses x_0..x_40 then landmarks m_0..m_7, each 2-D. One row per scalar measurement,
    weighted by 1/sigma. x and y separate, so we solve the same matrix twice."""
    nvar = T + M
    rows, rhs = [], []
    r = np.zeros(nvar); r[0] = 1 / 1e-3; rows.append(r); rhs.append(np.zeros(2))  # anchor x_0 = (0, 0)
    for t in range(T - 1):                       # odometry: x_{t+1} - x_t = u_t
        r = np.zeros(nvar); r[t + 1], r[t] = 1 / SIG_U, -1 / SIG_U
        rows.append(r); rhs.append(odo[t] / SIG_U)
    for t, j, z in observations:                 # landmark: m_j - x_t = z
        r = np.zeros(nvar); r[T + j], r[t] = 1 / SIG_Z, -1 / SIG_Z
        rows.append(r); rhs.append(z / SIG_Z)
    A, b = np.array(rows), np.array(rhs)
    sol = np.linalg.lstsq(A, b, rcond=None)[0]
    return sol[:T], sol[T:], A


dead = np.vstack([[0, 0], np.cumsum(odo, axis=0)])   # dead reckoning: add up the measured steps
est_x, est_m, A = solve(obs)


def rms(a, b):
    return float(np.sqrt(np.mean(np.sum((a - b) ** 2, axis=1))))


print(f"1. {T} poses, {M} landmarks, {len(odo)} odometry steps, {len(obs)} landmark sightings")
print(f"   odometry noise {SIG_U} m per step and axis, landmark noise {SIG_Z} m, sensor range {RANGE} m")
print("\n2. error of the estimated path (RMS over all poses) and of the final pose")
print(f"   dead reckoning : path {rms(dead, true_x):.3f} m, final pose {np.linalg.norm(dead[-1] - true_x[-1]):.3f} m")
print(f"   SLAM (all data): path {rms(est_x, true_x):.3f} m, final pose {np.linalg.norm(est_x[-1] - true_x[-1]):.3f} m, "
      f"map {rms(est_m, true_m):.3f} m")

no_close = [(t, j, z) for t, j, z in obs if not (t >= 30 and j in (0, 7))]
ex2, em2, _ = solve(no_close)
print(f"   SLAM without loop closure (no re-sighting of landmarks 0 and 7 after step 30):")
print(f"                    path {rms(ex2, true_x):.3f} m, final pose {np.linalg.norm(ex2[-1] - true_x[-1]):.3f} m, "
      f"map {rms(em2, true_m):.3f} m")

info = A.T @ A
print(f"\n3. the information matrix A^T A is {info.shape[0]} x {info.shape[1]} with "
      f"{np.count_nonzero(np.abs(info) > 1e-9)} non-zero entries of {info.size}")
print("   (each pose is linked only to its neighbours in time and to the landmarks it saw)")
print("\n4. which landmarks each pose saw, every 5 steps")
for t in range(0, T, 5):
    print(f"   pose {t:2d} at ({true_x[t, 0]:4.0f},{true_x[t, 1]:4.0f}): landmarks {sorted(j for s, j, _ in obs if s == t)}")
