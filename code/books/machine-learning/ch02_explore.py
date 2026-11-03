"""Chapter 2: looking before modelling.

Summary statistics and a correlation matrix for the cleaned flats, a text
histogram of a skewed quantity, and Anscombe's quartet (Anscombe 1973):
four datasets with nearly the same summary numbers and very different shapes.
"""
import numpy as np

# cleaned flats from ch02_cleaning.py: area, rooms, price (thousands)
FLATS = np.array([
    [52, 2, 210], [75, 3, 255], [40, 1, 140], [98, 4, 390], [66.5, 2, 205],
    [63, 3, 240], [75, 3, 260], [45, 2, 170], [88, 2.5, 335], [58, 2, 230],
    [70, 3, 215],
])
NAMES = ["area", "rooms", "price"]

ANSCOMBE_X = [10, 8, 13, 9, 11, 14, 6, 4, 12, 7, 5]
ANSCOMBE = {
    "I": (ANSCOMBE_X, [8.04, 6.95, 7.58, 8.81, 8.33, 9.96, 7.24, 4.26, 10.84, 4.82, 5.68]),
    "II": (ANSCOMBE_X, [9.14, 8.14, 8.74, 8.77, 9.26, 8.10, 6.13, 3.10, 9.13, 7.26, 4.74]),
    "III": (ANSCOMBE_X, [7.46, 6.77, 12.74, 7.11, 7.81, 8.84, 6.08, 5.39, 8.15, 6.42, 5.73]),
    "IV": ([8, 8, 8, 8, 8, 8, 8, 19, 8, 8, 8],
           [6.58, 5.76, 7.71, 8.84, 8.47, 7.04, 5.25, 12.50, 5.56, 7.91, 6.89]),
}


def summary(col):
    q1, med, q3 = np.percentile(col, [25, 50, 75])
    return len(col), col.mean(), col.std(ddof=1), col.min(), q1, med, q3, col.max()


def text_histogram(values, bins):
    counts, edges = np.histogram(values, bins=bins)
    for c, a, b in zip(counts, edges[:-1], edges[1:]):
        print(f"  {a:7.1f} to {b:7.1f} | {'#' * int(round(c / 4))} {c}")


if __name__ == "__main__":
    print("       count   mean     sd    min     q1  median     q3    max")
    for name, col in zip(NAMES, FLATS.T):
        n, m, s, lo, q1, med, q3, hi = summary(col)
        print(f"{name:6} {n:5d} {m:6.1f} {s:6.1f} {lo:6.1f} {q1:6.1f} {med:7.1f} {q3:6.1f} {hi:6.1f}")
    print("correlation matrix (area, rooms, price):")
    print(np.corrcoef(FLATS.T).round(3))

    rng = np.random.default_rng(4)
    commute = rng.lognormal(mean=3.0, sigma=0.6, size=200)     # minutes, skewed
    print(f"\ncommute times: mean {commute.mean():.1f}, median {np.median(commute):.1f}")
    text_histogram(commute, bins=8)
    logc = np.log(commute)
    print(f"after taking logs: mean {logc.mean():.2f}, median {np.median(logc):.2f}")
    text_histogram(logc, bins=8)

    print("\nAnscombe's quartet")
    print("set   mean x  var x  mean y  var y   corr   fitted line")
    for name, (x, y) in ANSCOMBE.items():
        x, y = np.array(x, float), np.array(y)
        slope, intercept = np.polyfit(x, y, 1)
        print(f"{name:4} {x.mean():7.2f} {x.var(ddof=1):6.2f} {y.mean():7.2f} {y.var(ddof=1):6.2f}"
              f" {np.corrcoef(x, y)[0, 1]:6.3f}   y = {intercept:.2f} + {slope:.3f} x")
