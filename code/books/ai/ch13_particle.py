# Chapter 13: a particle filter for robot localization (Monte Carlo localization) in a
# circular corridor 100 m long with three doors. The robot drives about 2 m per step and has
# a door detector that is sometimes wrong. We compare it with an exact grid (histogram) filter.
import numpy as np

L = 100.0
DOORS = np.array([10.0, 30.0, 70.0])
HALF_WIDTH = 2.0
P_HIT, P_FALSE = 0.9, 0.1          # P(detector says door | at a door), P(says door | wall)
STEP, STEP_SD = 2.0, 0.5


def at_door(x):
    d = np.abs((x[..., None] - DOORS + L / 2) % L - L / 2)   # distance around the ring
    return (d <= HALF_WIDTH).any(axis=-1)


def likelihood(x, z):
    p_door = np.where(at_door(x), P_HIT, P_FALSE)
    return p_door if z else 1 - p_door


def systematic_resample(w, rng):
    n = len(w)
    u = (rng.random() + np.arange(n)) / n
    return np.minimum(np.searchsorted(np.cumsum(w), u), n - 1)


rng = np.random.default_rng(1999)
N = 1000
particles = rng.uniform(0, L, N)    # no idea where we are: spread evenly
cells = np.arange(0, L, 0.1) + 0.05  # the grid filter: 1000 cells of 10 cm
grid = np.full(len(cells), 1 / len(cells))
# motion kernel for the grid: Gaussian over cell offsets, wrapping around the ring
offs = np.arange(-50, 51) * 0.1
kern = np.exp(-0.5 * ((offs - STEP) / STEP_SD) ** 2)
kern /= kern.sum()

x = 52.0                            # the true position, unknown to the robot
print("step  true x  says door  particles within 3 m  grid mass within 3 m  effective N  tenths per 10 m bin")
for t in range(1, 51):
    x = (x + STEP + rng.normal(0, STEP_SD)) % L
    z = bool(rng.random() < (P_HIT if at_door(np.array([x]))[0] else P_FALSE))
    # particle filter: move each particle with sampled noise, weight, resample
    particles = (particles + STEP + rng.normal(0, STEP_SD, N)) % L
    w = likelihood(particles, z)
    w /= w.sum()
    n_eff = 1 / np.sum(w ** 2)
    particles = particles[systematic_resample(w, rng)]
    # grid filter: exact prediction by circular convolution, then Bayes
    grid = sum(kern[i] * np.roll(grid, int(round(offs[i] / 0.1))) for i in range(len(offs)))
    grid *= likelihood(cells, z)
    grid /= grid.sum()
    near_p = np.mean(np.abs((particles - x + L / 2) % L - L / 2) <= 3)
    near_g = grid[np.abs((cells - x + L / 2) % L - L / 2) <= 3].sum()
    if t in (1, 5, 8, 10, 15, 20, 25, 30, 35, 40, 45, 50):
        hist = np.histogram(particles, bins=10, range=(0, L))[0]
        bars = "".join(str(min(9, int(round(10 * h / N)))) for h in hist)
        print(f"{t:4d}  {x:6.2f}  {'yes' if z else 'no ':>9}  {near_p:20.3f}  {near_g:20.3f}  {n_eff:11.1f}"
              f"  {bars}")
