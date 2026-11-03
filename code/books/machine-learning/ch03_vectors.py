"""Chapter 3: vectors, dot products, norms, matrices and broadcasting.

Everything is done twice: once with plain Python loops, so you can see the
arithmetic, and once with NumPy, which is what we use from now on.
"""
import math
import numpy as np


def dot(u, v):
    return sum(a * b for a, b in zip(u, v))


def norm2(u):
    return math.sqrt(dot(u, u))


def cosine(u, v):
    return dot(u, v) / (norm2(u) * norm2(v))


def matmul(A, B):
    """(n x k) times (k x m), with three loops."""
    n, k, m = len(A), len(B), len(B[0])
    assert all(len(row) == k for row in A)
    return [[sum(A[i][t] * B[t][j] for t in range(k)) for j in range(m)] for i in range(n)]


if __name__ == "__main__":
    u, v = [3, 4], [4, 3]
    print("u =", u, " v =", v)
    print("dot =", dot(u, v), " |u| =", norm2(u), " |v| =", norm2(v),
          " cos =", round(cosine(u, v), 4), " angle =", round(math.degrees(math.acos(cosine(u, v))), 2), "deg")
    w = [1, -2, 2]
    print("w =", w, " L1 =", sum(abs(x) for x in w), " L2 =", norm2(w), " Linf =", max(abs(x) for x in w))

    # word counts as vectors: columns are (dust, storm, rover, wheel, solar)
    docs = {"A": [2, 1, 0, 0, 1], "B": [4, 2, 0, 0, 2], "C": [0, 0, 3, 2, 0]}
    print("cosine A,B =", round(cosine(docs["A"], docs["B"]), 4),
          " cosine A,C =", round(cosine(docs["A"], docs["C"]), 4),
          " distance A,B =", round(math.dist(docs["A"], docs["B"]), 4))

    # Cauchy-Schwarz on random vectors: |u.v| <= |u||v|, always
    rng = np.random.default_rng(5)
    worst = max(abs(a @ b) / (np.linalg.norm(a) * np.linalg.norm(b))
                for a, b in (rng.normal(size=(2, 10)) for _ in range(10000)))
    print(f"largest |cos| over 10000 random pairs in 10-D: {worst:.4f}")

    A = [[1, 2], [3, 4], [5, 6]]          # 3 x 2
    B = [[1, 0, -1], [2, 1, 0]]           # 2 x 3
    print("A B with loops:", matmul(A, B))
    print("A B with NumPy:", (np.array(A) @ np.array(B)).tolist())
    print("B A with NumPy:", (np.array(B) @ np.array(A)).tolist())

    # a matrix as a map: rotate by 90 degrees, then stretch x by 2
    R = np.array([[0, -1], [1, 0]])
    S = np.array([[2, 0], [0, 1]])
    p = np.array([1, 1])
    print("S (R p) =", S @ (R @ p), " (S R) p =", (S @ R) @ p, " (R S) p =", (R @ S) @ p)

    # data table times weights: one prediction per row
    X = np.array([[52, 2], [75, 3], [40, 1]], dtype=float)
    wts = np.array([2.8, 12.0])
    print("X @ w + 30 =", X @ wts + 30)

    # broadcasting: subtract the column means from every row, no loop
    print("column means:", X.mean(axis=0), " centred:\n", X - X.mean(axis=0))
    print("shapes (3,1) + (1,4) ->", (np.arange(3)[:, None] + np.arange(4)[None, :]).shape)
    print(np.arange(3)[:, None] * 10 + np.arange(4)[None, :])
