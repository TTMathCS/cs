"""Chapter 11.1: Gini impurity, entropy and information gain, computed on the
14-day 'play tennis' table (Quinlan 1986; Mitchell 1997, Table 3.2)."""
from collections import Counter
from math import log2

COLS = ["Outlook", "Temperature", "Humidity", "Wind"]
ROWS = [  # Outlook, Temperature, Humidity, Wind, Play
    ("Sunny", "Hot", "High", "Weak", "No"), ("Sunny", "Hot", "High", "Strong", "No"),
    ("Overcast", "Hot", "High", "Weak", "Yes"), ("Rain", "Mild", "High", "Weak", "Yes"),
    ("Rain", "Cool", "Normal", "Weak", "Yes"), ("Rain", "Cool", "Normal", "Strong", "No"),
    ("Overcast", "Cool", "Normal", "Strong", "Yes"), ("Sunny", "Mild", "High", "Weak", "No"),
    ("Sunny", "Cool", "Normal", "Weak", "Yes"), ("Rain", "Mild", "Normal", "Weak", "Yes"),
    ("Sunny", "Mild", "Normal", "Strong", "Yes"), ("Overcast", "Mild", "High", "Strong", "Yes"),
    ("Overcast", "Hot", "Normal", "Weak", "Yes"), ("Rain", "Mild", "High", "Strong", "No"),
]


def entropy(labels):
    n = len(labels)
    return -sum(c / n * log2(c / n) for c in Counter(labels).values())


def gini(labels):
    n = len(labels)
    return 1 - sum((c / n) ** 2 for c in Counter(labels).values())


def gain(rows, col, impurity):
    """Impurity of the parent minus the size-weighted impurity of the children."""
    labels = [r[-1] for r in rows]
    total = impurity(labels)
    for value in sorted({r[col] for r in rows}):
        part = [r[-1] for r in rows if r[col] == value]
        total -= len(part) / len(rows) * impurity(part)
    return total


labels = [r[-1] for r in ROWS]
print(f"All 14 days: {Counter(labels)}  entropy {entropy(labels):.3f}  Gini {gini(labels):.3f}")
print("\nSplitting the whole table on each attribute")
print("  attribute     info gain   Gini decrease   children (yes/no)")
for c, name in enumerate(COLS):
    kids = []
    for v in sorted({r[c] for r in ROWS}):
        part = [r[-1] for r in ROWS if r[c] == v]
        kids.append(f"{v} {part.count('Yes')}/{part.count('No')}")
    print(f"  {name:12s}  {gain(ROWS, c, entropy):9.3f}   {gain(ROWS, c, gini):13.3f}   {', '.join(kids)}")

sunny = [r for r in ROWS if r[0] == "Sunny"]
print("\nInside Outlook = Sunny (5 days):")
for c, name in enumerate(COLS[1:], start=1):
    print(f"  {name:12s}  info gain {gain(sunny, c, entropy):.3f}")
rain = [r for r in ROWS if r[0] == "Rain"]
print("Inside Outlook = Rain (5 days):")
for c, name in enumerate(COLS[1:], start=1):
    print(f"  {name:12s}  info gain {gain(rain, c, entropy):.3f}")

print("\nImpurity of a two-class node as a function of p = fraction of class 1")
print("    p     entropy   Gini   misclassification")
for p in [0.0, 0.1, 0.2, 0.3, 0.4, 0.5]:
    ent = 0.0 if p in (0, 1) else -(p * log2(p) + (1 - p) * log2(1 - p))
    print(f"  {p:.1f}   {ent:7.3f}  {2 * p * (1 - p):5.3f}   {min(p, 1 - p):6.3f}")
