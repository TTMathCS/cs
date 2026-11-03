# Chapter 23: the knapsack FPTAS (Ibarra and Kim 1975).
# Exact DP indexed by PROFIT, then the same DP on rounded-down profits.
import random


def min_weight_by_profit(items, cap):
    """best[q] = least weight that reaches profit exactly q.  O(n * sum of profits)."""
    total = sum(p for p, w in items)
    INF = float("inf")
    best = [0] + [INF] * total
    took = []                                       # took[i][q]: item i used for q?
    for p, w in items:
        row = bytearray(total + 1)
        for q in range(total, p - 1, -1):           # backwards: each item once
            if best[q - p] + w < best[q]:
                best[q] = best[q - p] + w
                row[q] = 1
        took.append(row)
    top = max(q for q in range(total + 1) if best[q] <= cap)
    chosen, q = [], top
    for i in range(len(items) - 1, -1, -1):         # walk the choices back
        if took[i][q]:
            chosen.append(i)
            q -= items[i][0]
    return top, sorted(chosen), total + 1


def exact_by_weight(items, cap):
    """The chapter 13 DP, O(n * cap), used here only to check the answer."""
    best = [0] * (cap + 1)
    for p, w in items:
        for c in range(cap, w - 1, -1):
            best[c] = max(best[c], best[c - w] + p)
    return best[cap]


def fptas(items, cap, eps):
    n = len(items)
    pmax = max(p for p, w in items if w <= cap)
    K = eps * pmax / n                              # the scaling factor
    scaled = [(int(p // K), w) for p, w in items]
    _, chosen, table = min_weight_by_profit(scaled, cap)
    value = sum(items[i][0] for i in chosen)
    return value, chosen, table, K


# The small example of section 23.4
items = [(60, 10), (100, 20), (120, 30)]
print("items (profit, weight):", items, "capacity 50")
print("exact:", min_weight_by_profit(items, 50)[:2])
for eps in (0.5, 0.1):
    v, ch, table, K = fptas(items, 50, eps)
    print(f"eps={eps}: K={K:.1f}, scaled profits {[int(p // K) for p, _ in items]}, "
          f"value {v}, items {ch}")
print()

rng = random.Random(1975)
n = 30
items = []
for _ in range(n):                                  # profit close to 100 x weight:
    w = rng.randint(10, 100)                        # a hard, "correlated" instance
    items.append((100 * w + rng.randint(0, 99), w))
cap = sum(w for _, w in items) // 2
opt = exact_by_weight(items, cap)
full_table = sum(p for p, _ in items) + 1
print(f"{n} correlated items, capacity {cap}: optimum {opt}, exact profit table would have {full_table} cells")
print("  eps    value    ratio   bound   table size")
for eps in (0.9, 0.5, 0.2, 0.1, 0.05, 0.01):
    v, _, table, K = fptas(items, cap, eps)
    print(f"{eps:5.2f}  {v:7d}  {v / opt:.4f}  {1 - eps:.2f}  {table:8d}")
