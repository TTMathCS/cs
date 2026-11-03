"""Chapter 20, part 1: the orientation test, exact versus floating-point
arithmetic, segment intersection, polygon area and point in polygon."""
from fractions import Fraction
from math import gcd


def cross(o, a, b):
    """z-component of (a - o) x (b - o): > 0 left turn, < 0 right turn, 0 collinear."""
    return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])


def orient(o, a, b):
    c = cross(o, a, b)
    return (c > 0) - (c < 0)


def on_segment(p, q, r):
    """For collinear p, q, r: does r lie on the closed segment pq?"""
    return min(p[0], q[0]) <= r[0] <= max(p[0], q[0]) and \
        min(p[1], q[1]) <= r[1] <= max(p[1], q[1])


def segments_intersect(p1, p2, p3, p4):
    """Do the closed segments p1p2 and p3p4 share a point?"""
    d1, d2 = orient(p3, p4, p1), orient(p3, p4, p2)
    d3, d4 = orient(p1, p2, p3), orient(p1, p2, p4)
    if d1 * d2 < 0 and d3 * d4 < 0:
        return True                                  # proper crossing
    return (d1 == 0 and on_segment(p3, p4, p1)) or (d2 == 0 and on_segment(p3, p4, p2)) or \
        (d3 == 0 and on_segment(p1, p2, p3)) or (d4 == 0 and on_segment(p1, p2, p4))


def intersection_point(p1, p2, p3, p4):
    """The crossing point of two non-parallel lines, as exact fractions."""
    d = (p2[0] - p1[0]) * (p4[1] - p3[1]) - (p2[1] - p1[1]) * (p4[0] - p3[0])
    t = Fraction((p3[0] - p1[0]) * (p4[1] - p3[1]) - (p3[1] - p1[1]) * (p4[0] - p3[0]), d)
    return (p1[0] + t * (p2[0] - p1[0]), p1[1] + t * (p2[1] - p1[1]))


def area2(poly):
    """Twice the signed area (shoelace); positive for counter-clockwise order."""
    n = len(poly)
    return sum(poly[i][0] * poly[(i + 1) % n][1] - poly[(i + 1) % n][0] * poly[i][1]
               for i in range(n))


def point_in_polygon(pt, poly):
    """Ray casting to the right: 'boundary', 'inside' or 'outside'."""
    x, y = pt
    inside = False
    n = len(poly)
    for i in range(n):
        a, b = poly[i], poly[(i + 1) % n]
        if orient(a, b, pt) == 0 and on_segment(a, b, pt):
            return "boundary"
        if (a[1] > y) != (b[1] > y):                 # edge straddles the ray's line (half-open rule)
            x_cross = a[0] + Fraction((y - a[1]) * (b[0] - a[0]), b[1] - a[1])
            if x < x_cross:                          # the crossing is to the right of pt
                inside = not inside
    return "inside" if inside else "outside"


def winding_number(pt, poly):
    """How many times poly winds counter-clockwise around pt (pt not on the boundary)."""
    w = 0
    n = len(poly)
    for i in range(n):
        a, b = poly[i], poly[(i + 1) % n]
        if a[1] <= pt[1] < b[1] and orient(a, b, pt) > 0:
            w += 1                                   # upward edge with pt on its left
        elif b[1] <= pt[1] < a[1] and orient(a, b, pt) < 0:
            w -= 1                                   # downward edge with pt on its right
    return w


def main():
    print("1. Orientation")
    print("   (0,0),(4,0),(2,3):", orient((0, 0), (4, 0), (2, 3)), " (0,0),(4,0),(2,-3):",
          orient((0, 0), (4, 0), (2, -3)), " (0,0),(2,2),(5,5):", orient((0, 0), (2, 2), (5, 5)))

    print("2. Floating point gets orientation wrong near a line")
    u = 2.0 ** -53
    q, r = (12.0, 12.0), (24.0, 24.0)
    wrong, total, zero = 0, 0, 0
    for i in range(64):
        for j in range(64):
            p = (0.5 + i * u, 0.5 + j * u)
            fl = orient(p, q, r)
            ex = orient(tuple(map(Fraction, p)), tuple(map(Fraction, q)), tuple(map(Fraction, r)))
            total += 1
            wrong += fl != ex
            zero += fl == 0 and ex != 0
    print(f"   {wrong} of {total} nearby points get the wrong sign with floats"
          f" ({zero} of them 'collinear' by mistake)")

    print("3. Segment intersection")
    tests = [((0, 0), (4, 4), (0, 4), (4, 0)), ((0, 0), (2, 2), (3, 3), (5, 5)),
             ((0, 0), (3, 3), (3, 3), (5, 0)), ((0, 0), (4, 0), (2, 0), (6, 0)),
             ((0, 0), (4, 0), (1, 1), (3, 2))]
    for t in tests:
        print("  ", t, "->", segments_intersect(*t))
    print("   crossing point of (0,0)-(4,4) and (0,4)-(5,0):",
          intersection_point((0, 0), (4, 4), (0, 4), (5, 0)))

    print("4. Shoelace area and point in polygon")
    poly = [(0, 0), (6, 0), (6, 4), (3, 2), (0, 4)]          # a 'house' with a notch
    print("   twice the signed area:", area2(poly), " area:", area2(poly) / 2)
    boundary = sum(gcd(abs(poly[i][0] - poly[i - 1][0]), abs(poly[i][1] - poly[i - 1][1]))
                   for i in range(len(poly)))
    interior = sum(point_in_polygon((x, y), poly) == "inside" for x in range(7) for y in range(5))
    print(f"   Pick: interior {interior}, boundary {boundary}, I + B/2 - 1 = {interior + boundary / 2 - 1}")
    for pt in ((3, 1), (3, 3), (1, 3), (6, 2), (3, 2)):
        print(f"   {pt}: {point_in_polygon(pt, poly)}", end="")
        print(f", winding {winding_number(pt, poly)}" if point_in_polygon(pt, poly) != "boundary" else "")
    star = [(0, 3), (-2, -3), (3, 1), (-3, 1), (2, -3)]       # a pentagram, drawn in one stroke
    print("   pentagram centre: ray casting", point_in_polygon((0, 0), star),
          "| winding number", winding_number((0, 0), star))


if __name__ == "__main__":
    main()
