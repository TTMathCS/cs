"""Chapter 20, part 4: Delaunay triangulation (Bowyer-Watson) with exact
in-circle tests, its Voronoi vertices, and k-d trees for nearest neighbours."""
import random
from fractions import Fraction

from ch20_basics import cross
from ch20_hull import monotone_chain


def in_circle(a, b, c, d):
    """> 0 if d is strictly inside the circle through a, b, c (a, b, c counter-clockwise)."""
    rows = [(p[0] - d[0], p[1] - d[1]) for p in (a, b, c)]
    m = [(x, y, x * x + y * y) for x, y in rows]
    return (m[0][0] * (m[1][1] * m[2][2] - m[1][2] * m[2][1])
            - m[0][1] * (m[1][0] * m[2][2] - m[1][2] * m[2][0])
            + m[0][2] * (m[1][0] * m[2][1] - m[1][1] * m[2][0]))


def ccw(t, pts):
    a, b, c = t
    return t if cross(pts[a], pts[b], pts[c]) > 0 else (a, c, b)


def delaunay(points):
    """Bowyer-Watson: add points one at a time; remove the triangles whose
    circumcircle contains the new point and re-fill the hole. O(n^2) as written."""
    big = 10**9
    pts = list(points) + [(-big, -big), (big, -big), (0, big)]   # a huge super-triangle
    n = len(points)
    tris = {(n, n + 1, n + 2)}
    for i in range(n):
        p = pts[i]
        bad = [t for t in tris if in_circle(pts[t[0]], pts[t[1]], pts[t[2]], p) > 0]
        edges = {}
        for t in bad:
            for e in ((t[0], t[1]), (t[1], t[2]), (t[2], t[0])):
                key = tuple(sorted(e))
                edges[key] = edges.get(key, 0) + 1
        for t in bad:
            tris.remove(t)
        for (a, b), count in edges.items():
            if count == 1:                                  # boundary of the hole
                tris.add(ccw((a, b, i), pts))
    return [t for t in tris if max(t) < n]


def circumcenter(a, b, c):
    d = 2 * (a[0] * (b[1] - c[1]) + b[0] * (c[1] - a[1]) + c[0] * (a[1] - b[1]))
    ux = Fraction((a[0]**2 + a[1]**2) * (b[1] - c[1]) + (b[0]**2 + b[1]**2) * (c[1] - a[1])
                  + (c[0]**2 + c[1]**2) * (a[1] - b[1]), d)
    uy = Fraction((a[0]**2 + a[1]**2) * (c[0] - b[0]) + (b[0]**2 + b[1]**2) * (a[0] - c[0])
                  + (c[0]**2 + c[1]**2) * (b[0] - a[0]), d)
    return ux, uy


class KDTree:
    """Split on x, then y, then x, ... at the median."""

    def __init__(self, points, depth=0):
        self.point = self.left = self.right = None
        if not points:
            return
        axis = depth % 2
        points = sorted(points, key=lambda p: p[axis])
        mid = len(points) // 2
        self.axis, self.point = axis, points[mid]
        self.left = KDTree(points[:mid], depth + 1)
        self.right = KDTree(points[mid + 1:], depth + 1)

    def nearest(self, q, best=None, visited=None):
        """Returns (squared distance, point); visited[0] counts nodes looked at."""
        if self.point is None:
            return best
        visited[0] += 1
        d = (self.point[0] - q[0]) ** 2 + (self.point[1] - q[1]) ** 2
        if best is None or d < best[0]:
            best = (d, self.point)
        diff = q[self.axis] - self.point[self.axis]
        near, far = (self.left, self.right) if diff < 0 else (self.right, self.left)
        best = near.nearest(q, best, visited)
        if diff * diff < best[0]:              # the ball around q crosses the splitting line
            best = far.nearest(q, best, visited)
        return best


def main():
    print("1. Delaunay triangulation of random points")
    rng = random.Random(20)
    for n in (10, 60, 200):
        pts = list({(rng.randint(0, 1000), rng.randint(0, 1000)) for _ in range(n)})
        tris = delaunay(pts)
        empty = all(in_circle(pts[a], pts[b], pts[c], pts[d]) <= 0
                    for (a, b, c) in tris for d in range(len(pts)) if d not in (a, b, c))
        h = len(monotone_chain(pts))
        print(f"   n={len(pts):3d}: {len(tris):3d} triangles (2n - 2 - h = {2 * len(pts) - 2 - h}),"
              f" every circumcircle empty: {empty}")
    small = [(0, 0), (4, 0), (2, 3), (5, 4), (0, 5)]
    tris = sorted(tuple(sorted(t)) for t in delaunay(small))
    print("   five points", small)
    for t in tris:
        cc = circumcenter(*(small[k] for k in t))
        print(f"     triangle {t}: Voronoi vertex ({float(cc[0]):.3f}, {float(cc[1]):.3f})")

    print("2. k-d tree nearest neighbour")
    pts = [(rng.random(), rng.random()) for _ in range(20000)]
    tree = KDTree(pts)
    total_visited, ok = 0, True
    queries = [(rng.random(), rng.random()) for _ in range(200)]
    for q in queries:
        visited = [0]
        d, p = tree.nearest(q, None, visited)
        total_visited += visited[0]
        ok &= d == min((x - q[0]) ** 2 + (y - q[1]) ** 2 for x, y in pts)
    print(f"   20000 points, 200 queries: all equal to brute force: {ok},"
          f" average nodes visited {total_visited / len(queries):.1f}")


if __name__ == "__main__":
    main()
