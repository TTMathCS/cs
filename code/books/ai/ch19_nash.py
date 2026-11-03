# Chapter 19: games in normal form, from scratch.
# Dominated strategies, pure Nash equilibria, mixed equilibria by support enumeration,
# and fictitious play converging in a zero-sum game.
from itertools import combinations
from fractions import Fraction as F
import numpy as np


def pure_nash(A, B):
    """All pure equilibria: cells where each player's choice is a best response."""
    eq = []
    for i in range(A.shape[0]):
        for j in range(A.shape[1]):
            if A[i, j] >= A[:, j].max() and B[i, j] >= B[i, :].max():
                eq.append((i, j))
    return eq


def eliminate_dominated(A, B, rows, cols):
    """Iterated elimination of strictly dominated pure strategies; returns surviving names."""
    R, C = list(range(A.shape[0])), list(range(A.shape[1]))
    changed = True
    while changed:
        changed = False
        for r in R[:]:
            if any(all(A[s, c] > A[r, c] for c in C) for s in R if s != r):
                print(f"   row strategy {rows[r]!r} is strictly dominated: removed")
                R.remove(r); changed = True
        for c in C[:]:
            if any(all(B[r, d] > B[r, c] for r in R) for d in C if d != c):
                print(f"   column strategy {cols[c]!r} is strictly dominated: removed")
                C.remove(c); changed = True
    return [rows[r] for r in R], [cols[c] for c in C]


def solve_exact(M, rhs):
    """Gaussian elimination over fractions (exact), returns None if singular."""
    n = len(M)
    a = [[F(x) for x in row] + [F(y)] for row, y in zip(M, rhs)]
    for k in range(n):
        p = next((r for r in range(k, n) if a[r][k] != 0), None)
        if p is None:
            return None
        a[k], a[p] = a[p], a[k]
        for r in range(n):
            if r != k and a[r][k] != 0:
                f = a[r][k] / a[k][k]
                a[r] = [x - f * y for x, y in zip(a[r], a[k])]
    return [a[k][n] / a[k][k] for k in range(n)]


def support_enumeration(A, B):
    """Mixed equilibria of a nondegenerate bimatrix game: try every pair of equal-size supports.
    On a support, the OTHER player's mix must make every strategy in it equally good."""
    m, n = A.shape
    found = []
    for k in range(1, min(m, n) + 1):
        for I in combinations(range(m), k):
            for J in combinations(range(n), k):
                # column mix y on J makes row player indifferent over I: A[i,J] y = u for i in I
                My = [[int(A[i, j]) for j in J] + [-1] for i in I] + [[1] * k + [0]]
                sy = solve_exact(My, [0] * k + [1])
                Mx = [[int(B[i, j]) for i in I] + [-1] for j in J] + [[1] * k + [0]]
                sx = solve_exact(Mx, [0] * k + [1])
                if sx is None or sy is None:
                    continue
                x, v = sx[:k], sx[k]
                y, u = sy[:k], sy[k]
                if min(x) < 0 or min(y) < 0:
                    continue
                X = [F(0)] * m; Y = [F(0)] * n
                for i, p in zip(I, x): X[i] = p
                for j, q in zip(J, y): Y[j] = q
                # no profitable deviation outside the supports
                if all(sum(int(A[i, j]) * Y[j] for j in range(n)) <= u for i in range(m)) and \
                   all(sum(int(B[i, j]) * X[i] for i in range(m)) <= v for j in range(n)):
                    found.append((X, Y, u, v))
    return found


def show(name, A, B, rows, cols):
    print(f"\n{name}")
    for i, r in enumerate(rows):
        print("   " + r.ljust(9) + "  ".join(f"({A[i, j]:>2},{B[i, j]:>2})" for j in range(len(cols))))
    print("   pure equilibria:", [(rows[i], cols[j]) for i, j in pure_nash(A, B)])
    for X, Y, u, v in support_enumeration(A, B):
        fx = "(" + ", ".join(str(p) for p in X) + ")"
        fy = "(" + ", ".join(str(q) for q in Y) + ")"
        print(f"   equilibrium  row {fx:<18} column {fy:<18} payoffs {u}, {v}")


# Prisoner's dilemma with Axelrod's numbers T=5, R=3, P=1, S=0.
PD_A = np.array([[3, 0], [5, 1]]); PD_B = PD_A.T
show("Prisoner's dilemma (C = cooperate, D = defect)", PD_A, PD_B, ["C", "D"], ["C", "D"])
print("   iterated elimination:")
print("   survivors:", eliminate_dominated(PD_A, PD_B, ["C", "D"], ["C", "D"]))

MP_A = np.array([[1, -1], [-1, 1]])
show("Matching pennies (zero-sum)", MP_A, -MP_A, ["Heads", "Tails"], ["Heads", "Tails"])

BS_A = np.array([[2, 0], [0, 1]]); BS_B = np.array([[1, 0], [0, 2]])
show("Battle of the sexes (O = opera, F = football)", BS_A, BS_B, ["O", "F"], ["O", "F"])

RPS = np.array([[0, -1, 1], [1, 0, -1], [-1, 1, 0]])
show("Rock-paper-scissors (zero-sum)", RPS, -RPS, ["Rock", "Paper", "Scissors"], ["R", "P", "S"])

# A 3x3 game: elimination removes one row, and three equilibria remain.
G_A = np.array([[4, 3, 2], [2, 1, 0], [3, 4, 1]]); G_B = np.array([[3, 1, 2], [2, 2, 3], [0, 3, 1]])
show("A 3x3 game", G_A, G_B, ["Top", "Middle", "Bottom"], ["L", "C", "R"])
print("   iterated elimination:")
print("   survivors:", eliminate_dominated(G_A, G_B, ["Top", "Middle", "Bottom"], ["L", "C", "R"]))

# Fictitious play (Brown 1951): each player best-responds to the other's empirical frequencies.
print("\nFictitious play on rock-paper-scissors, starting from (Rock, Rock):")
counts_r = np.array([1.0, 0, 0]); counts_c = np.array([1.0, 0, 0])
for t in range(1, 100001):
    br_r = int(np.argmax(RPS @ (counts_c / counts_c.sum())))
    br_c = int(np.argmax(-(counts_r / counts_r.sum()) @ RPS))
    counts_r[br_r] += 1; counts_c[br_c] += 1
    if t in (10, 100, 1000, 10000, 100000):
        x = counts_r / counts_r.sum()
        gap = (RPS @ (counts_c / counts_c.sum())).max() - (x @ RPS).min()
        print(f"   t={t:>6}  row frequencies {np.round(x, 3)}   duality gap {gap:.4f}")
