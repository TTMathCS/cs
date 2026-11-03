"""Chapter 11: closest pair of points in O(n log n)."""
import math
import random

compares = 0


def dist(p, q):
    return math.hypot(p[0] - q[0], p[1] - q[1])


def brute(points):
    best = (float("inf"), None, None)
    for i in range(len(points)):
        for j in range(i + 1, len(points)):
            d = dist(points[i], points[j])
            if d < best[0]:
                best = (d, points[i], points[j])
    return best


def closest_pair(points):
    px = sorted(points)                          # by x (then y)
    py = sorted(points, key=lambda p: p[1])      # by y
    return _closest(px, py)


def _closest(px, py):
    global compares
    n = len(px)
    if n <= 3:
        compares += n * (n - 1) // 2
        return brute(px)
    mid = n // 2
    mid_x = px[mid][0]
    left_set = set(px[:mid])
    ly = [p for p in py if p in left_set]        # keep y-order in each half
    ry = [p for p in py if p not in left_set]
    best = min(_closest(px[:mid], ly), _closest(px[mid:], ry), key=lambda t: t[0])
    delta = best[0]
    strip = [p for p in py if abs(p[0] - mid_x) < delta]   # still sorted by y
    for i, p in enumerate(strip):
        # the strip lemma: only the next 7 points in y-order can be closer than delta
        for q in strip[i + 1:i + 8]:
            if q[1] - p[1] >= delta:
                break
            compares += 1
            d = dist(p, q)
            if d < best[0]:
                best = (d, p, q)
    return best


if __name__ == "__main__":
    pts = [(2, 3), (12, 30), (40, 50), (5, 1), (12, 10), (3, 4)]
    d, p, q = closest_pair(pts)
    print(f"points {pts}\nclosest pair {p} {q} at distance {d:.4f}")

    random.seed(1975)
    print("\n      n   distance comparisons   brute force pairs")
    for n in (100, 1000, 10000):
        pts = list({(random.random(), random.random()) for _ in range(n)})
        compares = 0
        fast = closest_pair(pts)
        pairs = n * (n - 1) // 2
        if n <= 1000:
            assert abs(fast[0] - brute(pts)[0]) < 1e-12
        print(f"{n:7d} {compares:22d} {pairs:19d}")
    print("fast answer agrees with brute force for n = 100 and 1000")
