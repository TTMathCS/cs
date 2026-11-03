"""Chapter 10: sparse tables for range minimum in O(1), and lowest common
ancestors through the Euler tour (the RMQ-LCA connection)."""
import random


class SparseTable:
    """m[k][i] = min of a[i : i + 2**k]. O(n log n) to build, O(1) per query."""

    def __init__(self, a, key=lambda x: x):
        self.key = key
        self.m = [list(a)]
        k = 1
        while 2 ** k <= len(a):
            prev, half = self.m[-1], 2 ** (k - 1)
            self.m.append([min(prev[i], prev[i + half], key=key)
                           for i in range(len(a) - 2 ** k + 1)])
            k += 1

    def query(self, l, r):             # min of a[l:r], r > l
        k = (r - l).bit_length() - 1   # largest k with 2**k <= r - l
        return min(self.m[k][l], self.m[k][r - 2 ** k], key=self.key)


def euler_tour(children, root):
    """Visit order of a DFS that writes a node each time it is entered or
    returned to; depth alongside. first[v] = first position of v."""
    tour, first = [], {}
    stack = [(root, 0, iter(children.get(root, [])))]
    tour.append((0, root))
    first[root] = 0
    while stack:
        v, d, it = stack[-1]
        child = next(it, None)
        if child is None:
            stack.pop()
            if stack:
                tour.append((stack[-1][1], stack[-1][0]))   # back at the parent
            continue
        first[child] = len(tour)
        tour.append((d + 1, child))
        stack.append((child, d + 1, iter(children.get(child, []))))
    return tour, first


class LCA:
    def __init__(self, children, root):
        self.tour, self.first = euler_tour(children, root)
        self.st = SparseTable(self.tour)   # tuples compare by depth first

    def query(self, u, v):
        i, j = sorted((self.first[u], self.first[v]))
        return self.st.query(i, j + 1)[1]


if __name__ == "__main__":
    a = [5, 8, 6, 3, 2, 7, 2, 6]
    st = SparseTable(a)
    for k, row in enumerate(st.m):
        print(f"k = {k} (blocks of {2 ** k}):", row)
    print("min a[1:7] = min(m[2][1], m[2][3]) =", st.query(1, 7))

    children = {"A": ["B", "C"], "B": ["D", "E"], "C": ["F"], "E": ["G", "H"]}
    lca = LCA(children, "A")
    print("Euler tour:", " ".join(v for _, v in lca.tour))
    print("depths    :", " ".join(str(d) for d, _ in lca.tour))
    for u, v in [("G", "D"), ("H", "F"), ("G", "H"), ("E", "G")]:
        print(f"LCA({u}, {v}) = {lca.query(u, v)}")

    random.seed(2000)
    n = 100000
    a = [random.randint(0, 10 ** 6) for _ in range(n)]
    st = SparseTable(a)
    ok = True
    for _ in range(2000):
        l = random.randrange(n)
        r = random.randrange(l + 1, min(n, l + 300) + 1)
        ok &= st.query(l, r) == min(a[l:r])
    print(f"n = {n}: table has {len(st.m)} rows, "
          f"{sum(len(r) for r in st.m)} entries; 2000 queries agree: {ok}")
