"""Chapter 4: fitting a line by least squares, by hand and with the normal equations.

The ten flats from Chapter 2 whose area was measured (flat 5's area was
filled in, so it is left out).  We predict price (thousands) from area (m2).
"""
import numpy as np

AREA = np.array([52, 75, 40, 98, 63, 75, 45, 88, 58, 70], dtype=float)
PRICE = np.array([210, 255, 140, 390, 240, 260, 170, 335, 230, 215], dtype=float)


def fit_line(x, y):
    """Slope and intercept that minimise the sum of squared errors."""
    dx, dy = x - x.mean(), y - y.mean()
    slope = (dx * dy).sum() / (dx * dx).sum()
    return y.mean() - slope * x.mean(), slope


if __name__ == "__main__":
    x, y = AREA, PRICE
    xbar, ybar = x.mean(), y.mean()
    print(f"mean area {xbar}, mean price {ybar}")
    print("   x      y    x-xbar   y-ybar   product   (x-xbar)^2")
    for xi, yi in zip(x, y):
        print(f"{xi:5.0f} {yi:6.0f} {xi - xbar:8.1f} {yi - ybar:8.1f} {(xi - xbar) * (yi - ybar):9.1f} {(xi - xbar) ** 2:10.1f}")
    Sxy = ((x - xbar) * (y - ybar)).sum()
    Sxx = ((x - xbar) ** 2).sum()
    print(f"Sxy = {Sxy:.1f}, Sxx = {Sxx:.1f}, slope = {Sxy / Sxx:.4f}")
    a, b = fit_line(x, y)
    print(f"fitted line: price = {a:.3f} + {b:.4f} * area")

    # The same answer from the normal equations X^T X w = X^T y
    X = np.column_stack([np.ones_like(x), x])
    w = np.linalg.solve(X.T @ X, X.T @ y)
    print("normal equations give", w.round(4))

    r = y - X @ w
    print("residuals", r.round(2))
    print(f"sum of residuals {r.sum():.2e}; residuals . area {r @ x:.2e} (both zero)")
    sse = (r ** 2).sum()
    sst = ((y - ybar) ** 2).sum()
    print(f"SSE {sse:.1f}, SST {sst:.1f}, R^2 = {1 - sse / sst:.4f},"
          f" correlation^2 = {np.corrcoef(x, y)[0, 1] ** 2:.4f}")

    # Squared versus absolute error for a constant prediction c:
    # the mean minimises the squared error, the median the absolute error.
    grid = np.linspace(100, 400, 30001)
    sq = [((y - c) ** 2).sum() for c in grid]
    ab = [np.abs(y - c).sum() for c in grid]
    print(f"best constant, squared error: {grid[np.argmin(sq)]:.2f} (mean {ybar})")
    print(f"best constants, absolute error: from {grid[np.isclose(ab, min(ab))].min():.2f}"
          f" to {grid[np.isclose(ab, min(ab))].max():.2f} (median {np.median(y)})")
