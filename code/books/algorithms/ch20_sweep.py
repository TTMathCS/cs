"""Chapter 20, part 3: sweep lines. Bentley-Ottmann reports all crossings of
n segments; a second sweep measures the area of a union of rectangles."""
import heapq
import random
from fractions import Fraction

from ch20_basics import segments_intersect, intersection_point


def y_at(seg, x):
    (x1, y1), (x2, y2) = seg
    return y1 + Fraction((y2 - y1) * (x - x1), x2 - x1)


def brute_force_crossings(segs):
    return {(i, j) for i in range(len(segs)) for j in range(i + 1, len(segs))
            if segments_intersect(*segs[i], *segs[j])}


def bentley_ottmann(segs):
    """All crossing pairs, assuming general position: no vertical segments, no three
    segments through one point, and no two events with the same x-coordinate."""
    segs = [tuple(sorted(s)) for s in segs]            # left endpoint first
    events = []
    for i, (a, b) in enumerate(segs):
        heapq.heappush(events, (Fraction(a[0]), 0, i, -1))   # 0 = left endpoint
        heapq.heappush(events, (Fraction(b[0]), 2, i, -1))   # 2 = right endpoint
    status = []                                        # segment ids, ordered by y at the sweep line
    found, steps = set(), 0

    def check(i, j, x_now):
        if i < 0 or j < 0:
            return
        pair = (min(i, j), max(i, j))
        if pair not in found and segments_intersect(*segs[i], *segs[j]):
            px, _ = intersection_point(*segs[i], *segs[j])
            if px > x_now:
                found.add(pair)
                heapq.heappush(events, (px, 1, pair[0], pair[1]))   # 1 = crossing

    def nb(k):                                         # id at position k, or -1 if none
        return status[k] if 0 <= k < len(status) else -1

    while events:
        x, kind, i, j = heapq.heappop(events)
        steps += 1
        if kind == 0:                                  # insert by y at x (linear scan here)
            y = y_at(segs[i], x)
            k = 0
            while k < len(status) and y_at(segs[status[k]], x) < y:
                k += 1
            status.insert(k, i)
            check(nb(k - 1), i, x)
            check(i, nb(k + 1), x)
        elif kind == 2:                                # delete; its two neighbours meet
            k = status.index(i)
            status.pop(k)
            check(nb(k - 1), nb(k), x)
        else:                                          # crossing: swap the two segments
            a, b = status.index(i), status.index(j)
            lo, hi = min(a, b), max(a, b)
            status[lo], status[hi] = status[hi], status[lo]
            check(nb(lo - 1), status[lo], x)
            check(status[hi], nb(hi + 1), x)
    return found, steps


def union_area(rects):
    """Area covered by axis-parallel rectangles (x1, y1, x2, y2): sweep in x,
    keep how many rectangles cover each elementary y-interval."""
    ys = sorted({y for r in rects for y in (r[1], r[3])})
    index = {y: k for k, y in enumerate(ys)}
    cover = [0] * (len(ys) - 1)
    events = sorted([(r[0], 1, r) for r in rects] + [(r[2], -1, r) for r in rects])
    area, last_x = 0, events[0][0]
    for x, delta, r in events:
        covered = sum(ys[k + 1] - ys[k] for k in range(len(cover)) if cover[k] > 0)
        area += covered * (x - last_x)                 # the strip since the last event
        for k in range(index[r[1]], index[r[3]]):
            cover[k] += delta
        last_x = x
    return area


def main():
    print("1. Bentley-Ottmann against brute force")
    rng = random.Random(20)
    for n in (10, 40, 80):
        segs = []
        for _ in range(n):
            a = (rng.randint(0, 10**6), rng.randint(0, 10**6))
            b = (rng.randint(0, 10**6), rng.randint(0, 10**6))
            if a[0] != b[0]:
                segs.append((a, b))
        bo, steps = bentley_ottmann(segs)
        bf = brute_force_crossings(segs)
        print(f"   n={len(segs):3d}: {len(bf):4d} crossings by brute force,"
              f" sweep finds {len(bo):4d}, same: {bo == bf}, events {steps}")

    print("2. Union of rectangles")
    rects = [(0, 0, 4, 3), (2, 1, 6, 5), (5, 0, 7, 2)]
    grid = sum(any(r[0] <= x < r[2] and r[1] <= y < r[3] for r in rects)
               for x in range(8) for y in range(6))
    print("   sweep:", union_area(rects), " unit squares counted:", grid)
    big = [(x, y, x + rng.randint(1, 30), y + rng.randint(1, 30))
           for x, y in ((rng.randint(0, 70), rng.randint(0, 70)) for _ in range(40))]
    grid = sum(any(r[0] <= x < r[2] and r[1] <= y < r[3] for r in big)
               for x in range(101) for y in range(101))
    print("   40 random rectangles: sweep", union_area(big), " grid count", grid)


if __name__ == "__main__":
    main()
