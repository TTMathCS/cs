"""Chapter 20, part 2: three convex hull algorithms, checked against each other,
and the reduction that shows sorting is no harder than finding a hull."""
import math
import random

from ch20_basics import cross

COUNT = [0]          # orientation tests made by the current algorithm


def turn(o, a, b):
    COUNT[0] += 1
    return cross(o, a, b)


def gift_wrapping(points):
    """Jarvis march: O(nh). Returns hull vertices counter-clockwise, no collinear points."""
    pts = sorted(set(points))
    if len(pts) < 3:
        return pts
    hull, p = [], pts[0]                  # the lowest-leftmost point is on the hull
    while True:
        hull.append(p)
        q = pts[0] if pts[0] != p else pts[1]
        for r in pts:
            c = turn(p, q, r)
            # r is to the right of p->q, or collinear and farther: r is the better candidate
            if c < 0 or (c == 0 and (r[0] - p[0]) ** 2 + (r[1] - p[1]) ** 2 >
                         (q[0] - p[0]) ** 2 + (q[1] - p[1]) ** 2):
                q = r
        p = q
        if p == hull[0]:
            return hull


def graham_scan(points):
    """Graham 1972: sort by angle around the lowest point, then one stack pass."""
    pts = list(set(points))
    if len(pts) < 3:
        return sorted(pts)
    p0 = min(pts, key=lambda p: (p[1], p[0]))
    rest = [p for p in pts if p != p0]
    # sort by angle with exact comparisons: a before b if b is to the left of p0->a
    from functools import cmp_to_key

    def by_angle(a, b):
        c = turn(p0, a, b)
        if c:
            return -1 if c > 0 else 1
        da = (a[0] - p0[0]) ** 2 + (a[1] - p0[1]) ** 2
        db = (b[0] - p0[0]) ** 2 + (b[1] - p0[1]) ** 2
        return -1 if da < db else 1
    rest.sort(key=cmp_to_key(by_angle))
    stack = [p0]
    for p in rest:
        while len(stack) >= 2 and turn(stack[-2], stack[-1], p) <= 0:
            stack.pop()                   # not a left turn: the top is not on the hull
        stack.append(p)
    return stack


def monotone_chain(points):
    """Andrew 1979: sort by x, build lower and upper hulls with the same stack rule."""
    pts = sorted(set(points))
    if len(pts) < 3:
        return pts
    lower, upper = [], []
    for p in pts:
        while len(lower) >= 2 and turn(lower[-2], lower[-1], p) <= 0:
            lower.pop()
        lower.append(p)
    for p in reversed(pts):
        while len(upper) >= 2 and turn(upper[-2], upper[-1], p) <= 0:
            upper.pop()
        upper.append(p)
    return lower[:-1] + upper[:-1]


def normalise(hull):
    """Rotate so the hull starts at its smallest point (to compare outputs)."""
    k = hull.index(min(hull))
    return hull[k:] + hull[:k]


def main():
    print("1. A small example")
    pts = [(0, 0), (4, 0), (2, 1), (5, 3), (3, 5), (1, 3), (2, 3), (0, 4), (4, 2)]
    for f in (gift_wrapping, graham_scan, monotone_chain):
        print(f"   {f.__name__:15s}", normalise(f(pts)))

    print("2. Random tests, with collinear and duplicate points")
    rng = random.Random(20)
    ok = True
    for _ in range(300):
        pts = [(rng.randint(0, 6), rng.randint(0, 6)) for _ in range(rng.randint(3, 30))]
        if len({p for p in pts}) < 3 or all(cross(pts[0], pts[1], p) == 0 for p in pts):
            continue
        h = [normalise(f(pts)) for f in (gift_wrapping, graham_scan, monotone_chain)]
        ok &= h[0] == h[1] == h[2]
    print("   all three hulls agree:", ok)

    print("3. Orientation tests: points in a disc (small hull) and on a circle (all on hull)")
    for n in (500, 2000):
        disc = []
        while len(disc) < n:
            x, y = rng.randint(-10**6, 10**6), rng.randint(-10**6, 10**6)
            if x * x + y * y <= 10**12:
                disc.append((x, y))
        circle = list({(round(10**6 * math.cos(2 * math.pi * k / n)),
                        round(10**6 * math.sin(2 * math.pi * k / n))) for k in range(n)})
        for label, pts in (("disc", disc), ("circle", circle)):
            row = []
            for f in (gift_wrapping, monotone_chain):
                COUNT[0] = 0
                h = f(pts)
                row.append(COUNT[0])
            print(f"   n={n:5d} {label:6s} hull size {len(h):5d}:"
                  f" gift wrapping {row[0]:9d} tests, monotone chain {row[1]:6d}")

    print("4. Sorting by convex hull: the hull of (x, x^2) lists the x in order")
    xs = [rng.randint(-50, 50) for _ in range(12)]
    xs = list(dict.fromkeys(xs))
    hull = normalise(monotone_chain([(x, x * x) for x in xs]))
    print("   input:", xs)
    print("   hull order:", [p[0] for p in hull])


if __name__ == "__main__":
    main()
