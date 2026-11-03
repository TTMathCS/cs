# Chapter 25: fine-grained complexity, from the inside.
# (1) 3SUM: cubic brute force versus the quadratic sort-and-two-pointers method.
# (2) The split-and-list reduction from CNF-SAT to Orthogonal Vectors (R. Williams 2005),
#     the bridge from SETH to quadratic lower bounds such as edit distance's.
import itertools
import random


def three_sum_cubic(a):
    checks = 0
    for i, j, k in itertools.combinations(range(len(a)), 3):
        checks += 1
        if a[i] + a[j] + a[k] == 0:
            return (a[i], a[j], a[k]), checks
    return None, checks


def three_sum_quadratic(a):
    a = sorted(a)
    steps = 0
    for i in range(len(a) - 2):
        lo, hi = i + 1, len(a) - 1
        while lo < hi:
            steps += 1
            s = a[i] + a[lo] + a[hi]
            if s == 0:
                return (a[i], a[lo], a[hi]), steps
            if s < 0:
                lo += 1
            else:
                hi -= 1
    return None, steps


rng = random.Random(2015)
print("3SUM on n distinct odd integers (no solution exists: three odds never sum to 0)")
print("    n   cubic triples checked   quadratic pointer steps")
for n in (50, 100, 200):
    a = rng.sample(range(-10**6 + 1, 10**6, 2), n)
    r1, c1 = three_sum_cubic(a)
    r2, c2 = three_sum_quadratic(a)
    assert r1 is None and r2 is None
    print(f"{n:5d}   {c1:21d}   {c2:23d}")
print()


def sat_to_ov(clauses, n):
    """Split the n variables into halves.  For each assignment of a half, make a vector
    with one coordinate per clause: 0 if that half already satisfies the clause, else 1.
    The formula is satisfiable iff some left vector and right vector are orthogonal."""
    half = n // 2
    left_vars, right_vars = range(1, half + 1), range(half + 1, n + 1)

    def vectors(vars_):
        out = []
        for bits in itertools.product([False, True], repeat=len(vars_)):
            assign = dict(zip(vars_, bits))
            vec = tuple(0 if any(abs(l) in assign and assign[abs(l)] == (l > 0) for l in c) else 1
                        for c in clauses)
            out.append((vec, assign))
        return out

    return vectors(left_vars), vectors(right_vars)


def orthogonal_pair(L, R):
    for u, a in L:
        for v, b in R:
            if all(x * y == 0 for x, y in zip(u, v)):
                return {**a, **b}
    return None


n = 12
for m in (30, 70):
    clauses = [[v if rng.random() < 0.5 else -v for v in rng.sample(range(1, n + 1), 3)]
               for _ in range(m)]
    L, R = sat_to_ov(clauses, n)
    sol = orthogonal_pair(L, R)
    brute = any(all(any(bits[abs(l) - 1] == (l > 0) for l in c) for c in clauses)
                for bits in itertools.product([False, True], repeat=n))
    print(f"3-CNF with n={n} variables, m={m} clauses: two lists of {len(L)} vectors "
          f"of dimension {m}; orthogonal pair found: {sol is not None}; brute force says "
          f"satisfiable: {brute}")
