"""Chapter 1: a first learner from scratch, the nearest-neighbour classifier.

A tiny table of fruit, measured by hand: length and width in centimetres,
and the label we want to predict. No rules about lemons or oranges are
written anywhere below; the program only stores examples and compares.
"""
import math
from collections import Counter

# (length cm, width cm), label
TABLE = [
    ((7.0, 7.2), "orange"), ((7.6, 7.5), "orange"), ((6.8, 6.9), "orange"),
    ((8.0, 7.8), "orange"), ((7.2, 7.4), "orange"),
    ((8.5, 5.9), "lemon"), ((9.2, 6.3), "lemon"), ((8.0, 5.6), "lemon"),
    ((9.6, 6.6), "lemon"), ((8.8, 6.1), "lemon"),
]


def distance(p, q):
    """Straight-line (Euclidean) distance between two points."""
    return math.sqrt(sum((a - b) ** 2 for a, b in zip(p, q)))


def knn_predict(table, x, k=1):
    """Label of x by a vote of its k nearest examples in the table."""
    nearest = sorted(table, key=lambda row: distance(row[0], x))[:k]
    votes = Counter(label for _, label in nearest)
    return votes.most_common(1)[0][0]


if __name__ == "__main__":
    query = (8.1, 6.4)
    print("distances from the new fruit", query)
    rows = sorted(TABLE, key=lambda row: distance(row[0], query))
    for features, label in rows:
        print(f"  {str(features):12} {label:7} {distance(features, query):.3f}")
    for k in (1, 3, 5):
        print(f"k = {k}: predicted {knn_predict(TABLE, query, k)}")

    print()
    for q in [(7.4, 7.0), (9.0, 6.0), (7.9, 6.9)]:
        print(f"new fruit {q}: 1-NN says {knn_predict(TABLE, q, 1)},"
              f" 3-NN says {knn_predict(TABLE, q, 3)}")

    # Leave-one-out: hide each row, predict it from the other nine.
    for k in (1, 3):
        right = sum(knn_predict(TABLE[:i] + TABLE[i + 1:], x, k) == y
                    for i, (x, y) in enumerate(TABLE))
        print(f"leave-one-out, k = {k}: {right} of {len(TABLE)} right")
