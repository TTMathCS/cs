"""Chapter 15: the idea behind universal approximation, built by hand. One hidden layer of N units,
weights written down (not trained), approximating a continuous function on [0, 1]."""
import numpy as np


def f(x):
    return np.sin(2 * np.pi * x) + 0.5 * x


def sigmoid(a):
    return 0.5 * (1 + np.tanh(0.5 * a))   # the same function as 1/(1+e^-a), without overflow


def sigmoid_staircase(x, N, steepness):
    """f(0) plus N near-step sigmoids, the j-th rising by f(t_j) - f(t_{j-1}) at the midpoint of the j-th interval."""
    knots = np.linspace(0, 1, N + 1)
    out = np.full_like(x, f(knots[0]))
    for j in range(1, N + 1):
        centre = 0.5 * (knots[j - 1] + knots[j])
        out += (f(knots[j]) - f(knots[j - 1])) * sigmoid(steepness * N * (x - centre))
    return out


def relu_interpolant(x, N):
    """The piecewise-linear interpolant of f at N+1 knots, written as f(0) + sum of N ReLU units."""
    knots = np.linspace(0, 1, N + 1)
    slopes = np.diff(f(knots)) / np.diff(knots)
    out = np.full_like(x, f(knots[0]))
    prev = 0.0
    for j in range(N):                           # unit j switches on at knot j and changes the slope
        out += (slopes[j] - prev) * np.maximum(0.0, x - knots[j])
        prev = slopes[j]
    return out


if __name__ == "__main__":
    x = np.linspace(0, 1, 20001)
    print("Largest error on [0, 1] of a one-hidden-layer network with N units")
    print("      N   sigmoid staircase   ReLU interpolant")
    for N in (4, 8, 16, 32, 64, 128, 256):
        e1 = np.abs(sigmoid_staircase(x, N, 40.0) - f(x)).max()
        e2 = np.abs(relu_interpolant(x, N) - f(x)).max()
        print(f"  {N:5d}   {e1:17.5f}   {e2:16.6f}")
