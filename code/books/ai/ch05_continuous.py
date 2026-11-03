# Chapter 5: local search in a continuous space.
# Place k relay stations so that the sum of squared distances from each site to its
# nearest station is as small as possible. Gradient descent, an empirical gradient,
# random restarts, and Newton's method in one dimension.
import numpy as np

rng = np.random.default_rng(56)
# 12 sites in three loose groups on a 10 km x 10 km map
centres = np.array([[2.0, 2.0], [7.5, 3.0], [5.0, 8.0]])
sites = np.vstack([c + rng.normal(0, 0.9, size=(4, 2)) for c in centres])


def cost(stations):
    d2 = ((sites[:, None, :] - stations[None, :, :]) ** 2).sum(axis=2)    # 12 x k squared distances
    return d2.min(axis=1).sum()


def gradient(stations):
    """Analytic gradient: each station is pulled by the sites nearest to it."""
    d2 = ((sites[:, None, :] - stations[None, :, :]) ** 2).sum(axis=2)
    nearest = d2.argmin(axis=1)
    g = np.zeros_like(stations)
    for j in range(len(stations)):
        mine = sites[nearest == j]
        g[j] = 2 * (len(mine) * stations[j] - mine.sum(axis=0))
    return g


def empirical_gradient(stations, h=1e-5):
    """Central differences: change one coordinate by +-h and watch the cost."""
    g = np.zeros_like(stations)
    for idx in np.ndindex(stations.shape):
        up, down = stations.copy(), stations.copy()
        up[idx] += h
        down[idx] -= h
        g[idx] = (cost(up) - cost(down)) / (2 * h)
    return g


def descend(stations, alpha=0.05, steps=200):
    x = stations.copy()
    history = [cost(x)]
    for _ in range(steps):
        x = x - alpha * gradient(x)
        history.append(cost(x))
    return x, history


start = np.array([[1.0, 9.0], [2.0, 8.0], [9.0, 1.0]])
print("start cost", round(cost(start), 3))
print("analytic gradient :", np.round(gradient(start), 4).tolist())
print("empirical gradient:", np.round(empirical_gradient(start), 4).tolist())

x, hist = descend(start)
print("\ngradient descent, alpha = 0.05")
for k in (0, 1, 2, 5, 10, 50, 200):
    print(f"  step {k:3d}: cost {hist[k]:8.3f}")
print("  stations end at", np.round(x, 2).tolist())

print("\nstep size matters (cost after 5 and 50 steps from the same start):")
for alpha in (0.005, 0.02, 0.05):
    _, h = descend(start, alpha=alpha, steps=50)
    print(f"  alpha {alpha:5.3f}: {h[5]:8.3f} {h[50]:8.3f}")


def newton_step(stations):
    """Each station's cost n_j |x - mean_j|^2 is a quadratic; Newton jumps to its minimum, the mean."""
    d2 = ((sites[:, None, :] - stations[None, :, :]) ** 2).sum(axis=2)
    nearest = d2.argmin(axis=1)
    new = stations.copy()
    for j in range(len(stations)):
        mine = sites[nearest == j]
        if len(mine):
            new[j] = mine.mean(axis=0)
    return new


x = start.copy()
row = [round(float(cost(x)), 3)]
for _ in range(4):
    x = newton_step(x)
    row.append(round(float(cost(x)), 3))
print("  Newton steps (jump to the mean of the nearest sites):", row)

print("\nrandom restarts: 10 random starts, 200 steps each")
finals = []
for r in range(10):
    s0 = rng.uniform(0, 10, size=(3, 2))
    xr, hr = descend(s0)
    finals.append(hr[-1])
print("  final costs:", sorted(round(float(f), 2) for f in finals))

# Newton's method in 1-D: minimise f(x) = x^4 - 3x^2 + x by solving f'(x) = 0
f = lambda t: t ** 4 - 3 * t ** 2 + t
fp = lambda t: 4 * t ** 3 - 6 * t + 1
fpp = lambda t: 12 * t ** 2 - 6
print("\nNewton's method on f(x) = x^4 - 3x^2 + x, from x = -2 and from x = 2")
for x0 in (-2.0, 2.0):
    t = x0
    row = [f"{t:.6f}"]
    for _ in range(5):
        t = t - fp(t) / fpp(t)
        row.append(f"{t:.6f}")
    print("  " + "  ".join(row), f"  f = {f(t):.4f}")
