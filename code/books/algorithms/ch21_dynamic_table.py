"""Chapter 21: a dynamic table that grows and shrinks, two shrinking rules compared."""
import random

random.seed(4)


class Table:
    """Counts the real cost: 1 per insert or delete, plus 1 per element copied when resizing."""

    def __init__(self, shrink_at):
        self.size, self.num, self.cost = 0, 0, 0
        self.shrink_at = shrink_at          # halve when num drops below shrink_at * size

    def insert(self):
        if self.num == self.size:           # full: double (an empty table gets one slot)
            self.cost += self.num
            self.size = max(1, 2 * self.size)
        self.num += 1
        self.cost += 1

    def delete(self):
        self.num -= 1
        self.cost += 1
        if self.size > 1 and self.num < self.shrink_at * self.size:
            self.size //= 2
            self.cost += self.num

    def phi(self):
        """The potential from the text: 2 num - size when at least half full, size/2 - num otherwise."""
        if 2 * self.num >= self.size:
            return 2 * self.num - self.size
        return self.size / 2 - self.num


def adversary(table, n, rounds):
    """Fill to n = a power of two, then repeat: insert, delete, delete, insert."""
    for _ in range(n):
        table.insert()
    start = table.cost
    for _ in range(rounds):
        table.insert(); table.delete(); table.delete(); table.insert()
    return (table.cost - start) / (4 * rounds)


n = 1024
for rule, name in ((0.5, "halve below 1/2 full"), (0.25, "halve below 1/4 full")):
    print(f"{name}: average cost per operation over 4000 operations after the fill"
          f" {adversary(Table(rule), n, 1000):8.2f}")

print("\nPotential check for the 1/4 rule: amortized = actual + change in Phi, over random operations")
t = Table(0.25)
worst = {"insert": 0, "delete": 0}
for step in range(200000):
    op = "insert" if t.num == 0 or random.random() < 0.5 + 0.1 * ((step // 5000) % 2 * 2 - 1) else "delete"
    cost0, phi0 = t.cost, t.phi()
    getattr(t, op)()
    worst[op] = max(worst[op], t.cost - cost0 + t.phi() - phi0)
print(f"  largest amortized insert {worst['insert']}, largest amortized delete {worst['delete']}"
      f"  (final size {t.size}, num {t.num}, Phi {t.phi()})")
