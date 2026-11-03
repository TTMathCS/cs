# Chapter 23: the simplex method from scratch, in exact fractions,
# then LP relaxation and rounding for vertex cover, and LP duality seen in the tableau.
from fractions import Fraction as F


def simplex(c, A, b, trace=False):
    """Maximise c.x subject to A x <= b, x >= 0, with every b_i >= 0.

    Tableau method with Bland's rule (smallest index enters and leaves),
    which never cycles.  Returns (value, x, y) where y is the optimal dual.
    """
    m, n = len(A), len(c)
    # Rows: [A | I | b]; objective row: [-c | 0 | 0].
    T = [[F(v) for v in A[i]] + [F(int(i == j)) for j in range(m)] + [F(b[i])]
         for i in range(m)]
    z = [F(-v) for v in c] + [F(0)] * m + [F(0)]
    basis = [n + i for i in range(m)]               # the slacks start in the basis
    step = 0
    while True:
        if trace:
            point = [F(0)] * (n + m)
            for i, bv in enumerate(basis):
                point[bv] = T[i][-1]
            print(f"  step {step}: basis {[name(v, n) for v in basis]}, "
                  f"x = {[str(v) for v in point[:n]]}, value {z[-1]}")
        enter = next((j for j in range(n + m) if z[j] < 0), None)
        if enter is None:
            break                                   # no improving direction: optimal
        ratios = [(T[i][-1] / T[i][enter], basis[i], i)
                  for i in range(m) if T[i][enter] > 0]
        if not ratios:
            raise ValueError("unbounded")
        _, _, row = min(ratios)                     # ratio test, ties by Bland
        piv = T[row][enter]
        T[row] = [v / piv for v in T[row]]
        for i in range(m):
            if i != row and T[i][enter] != 0:
                f = T[i][enter]
                T[i] = [a - f * r for a, r in zip(T[i], T[row])]
        f = z[enter]
        z = [a - f * r for a, r in zip(z, T[row])]
        basis[row] = enter
        step += 1
    x = [F(0)] * (n + m)
    for i, bv in enumerate(basis):
        x[bv] = T[i][-1]
    y = z[n:n + m]                                  # duals = reduced costs of slacks
    return z[-1], x[:n], y


def name(v, n):
    return f"x{v + 1}" if v < n else f"s{v - n + 1}"


print("LP: maximise 3x1 + 2x2 with x1 + x2 <= 4, x1 + 3x2 <= 6, x1 <= 3")
val, x, y = simplex([3, 2], [[1, 1], [1, 3], [1, 0]], [4, 6, 3], trace=True)
print("  optimum", val, "at x =", [str(v) for v in x], "; dual y =", [str(v) for v in y])
print("  dual objective 4y1 + 6y2 + 3y3 =", 4 * y[0] + 6 * y[1] + 3 * y[2])
print()


def vertex_cover_lp(n, edges):
    """The dual of the vertex cover LP is fractional matching:
    maximise sum of y_e subject to sum of y_e over edges at v <= 1.
    Solving it, the slack duals are an optimal fractional vertex cover x_v."""
    A = [[1 if v in e else 0 for e in edges] for v in range(n)]
    val, ymatch, xcover = simplex([1] * len(edges), A, [1] * n)
    return val, xcover, ymatch


for title, n, edges in [
    ("triangle", 3, [(0, 1), (1, 2), (0, 2)]),
    ("section 23.1 example", 6, [(0, 1), (0, 2), (1, 3), (2, 3), (3, 4), (4, 5)]),
    ("5-cycle", 5, [(0, 1), (1, 2), (2, 3), (3, 4), (4, 0)]),
]:
    val, xs, ys = vertex_cover_lp(n, edges)
    rounded = [v for v in range(n) if xs[v] >= F(1, 2)]
    ok = all(u in rounded or v in rounded for u, v in edges)
    print(f"{title}: LP optimum {val}")
    print("   fractional cover x =", [str(v) for v in xs])
    print("   fractional matching y =", [str(v) for v in ys])
    print("   rounded cover (x >= 1/2):", rounded, "size", len(rounded), "valid", ok)
