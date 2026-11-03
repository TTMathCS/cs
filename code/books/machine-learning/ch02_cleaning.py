"""Chapter 2: cleaning a small table by hand.

A made-up table of 12 flats for sale.  It has the three classic problems:
missing values (None), a duplicate row, and an outlier (a typing error).
"""
import statistics

COLUMNS = ["id", "area_m2", "rooms", "district", "condition", "price_k"]
ROWS = [
    [1, 52, 2, "north", "good", 210],
    [2, 75, 3, "south", "fair", 255],
    [3, 40, 1, "north", "poor", 140],
    [4, 98, 4, "east", "good", 390],
    [5, None, 2, "south", "good", 205],
    [6, 63, 3, "east", None, 240],
    [7, 7500, 3, "north", "fair", 260],     # 75.00 typed without the point
    [8, 45, 2, "south", "fair", 170],
    [9, 88, None, "east", "good", 335],
    [10, 58, 2, "north", "good", 230],
    [8, 45, 2, "south", "fair", 170],       # the same listing entered twice
    [11, 70, 3, "south", "poor", 215],
]


def column(rows, name):
    i = COLUMNS.index(name)
    return [r[i] for r in rows]


def drop_duplicates(rows):
    seen, out = set(), []
    for r in rows:
        key = tuple(r)
        if key not in seen:
            seen.add(key)
            out.append(r)
    return out


def quartiles(values):
    q1, q2, q3 = statistics.quantiles(values, n=4, method="inclusive")
    return q1, q2, q3


def tukey_fences(values, factor=1.5):
    q1, _, q3 = quartiles(values)
    iqr = q3 - q1
    return q1 - factor * iqr, q3 + factor * iqr


if __name__ == "__main__":
    print(f"{len(ROWS)} rows")
    rows = drop_duplicates(ROWS)
    print(f"after dropping exact duplicates: {len(rows)} rows")

    for name in COLUMNS[1:]:
        missing = sum(v is None for v in column(rows, name))
        print(f"  missing in {name:9}: {missing}")

    area = [v for v in column(rows, "area_m2") if v is not None]
    print("area values:", sorted(area))
    print(f"area mean = {statistics.mean(area):.1f}, median = {statistics.median(area)}")
    lo, hi = tukey_fences(area)
    q1, q2, q3 = quartiles(area)
    print(f"quartiles {q1}, {q2}, {q3}; Tukey fences [{lo}, {hi}]")
    print("outside the fences:", [v for v in area if v < lo or v > hi])
    mu, sd = statistics.mean(area), statistics.pstdev(area)
    print("z-scores:", [round((v - mu) / sd, 2) for v in area])

    # Fix the typing error (we checked the listing: 75 m2), then impute.
    for r in rows:
        if r[1] == 7500:
            r[1] = 75
    area = [v for v in column(rows, "area_m2") if v is not None]
    print(f"after the fix: mean = {statistics.mean(area):.1f}, median = {statistics.median(area)}")

    med_area = statistics.median(area)
    med_rooms = statistics.median([v for v in column(rows, "rooms") if v is not None])
    mode_cond = statistics.mode([v for v in column(rows, "condition") if v is not None])
    print(f"fill values: area {med_area}, rooms {med_rooms}, condition {mode_cond!r}")
    clean = []
    for r in rows:
        r = list(r)
        flags = [int(r[1] is None), int(r[2] is None), int(r[4] is None)]
        r[1] = med_area if r[1] is None else r[1]
        r[2] = med_rooms if r[2] is None else r[2]
        r[4] = mode_cond if r[4] is None else r[4]
        clean.append(r + flags)
    print("id area rooms district condition price | missing flags")
    for r in clean:
        print(f"{r[0]:2} {r[1]:5} {r[2]:4}  {r[3]:6}  {r[4]:6} {r[5]:5} | {r[6]} {r[7]} {r[8]}")
