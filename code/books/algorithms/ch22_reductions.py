"""Chapter 22: the chain of reductions SAT -> 3-SAT -> independent set -> vertex cover and clique,
and 3-SAT -> subset sum, each checked by exhaustive search on many random formulas."""
import random
from itertools import product, combinations

random.seed(1972)


def satisfiable(formula, n):
    return any(all(any(bits[abs(l) - 1] == (l > 0) for l in c) for c in formula)
               for bits in product((False, True), repeat=n))


def sat_to_3sat(formula, n):
    """Every clause becomes clauses of exactly 3 literals, using new variables n+1, n+2, ..."""
    out, nxt = [], n + 1
    for c in formula:
        if len(c) == 1:
            y, z = nxt, nxt + 1
            nxt += 2
            out += [[c[0], y, z], [c[0], y, -z], [c[0], -y, z], [c[0], -y, -z]]
        elif len(c) == 2:
            y = nxt
            nxt += 1
            out += [[c[0], c[1], y], [c[0], c[1], -y]]
        elif len(c) == 3:
            out.append(list(c))
        else:                                   # l1 l2 y1 | -y1 l3 y2 | ... | -y_(L-3) l_(L-1) l_L
            ys = list(range(nxt, nxt + len(c) - 3))
            nxt += len(c) - 3
            out.append([c[0], c[1], ys[0]])
            for i in range(1, len(c) - 3):
                out.append([-ys[i - 1], c[i + 1], ys[i]])
            out.append([-ys[-1], c[-2], c[-1]])
    return out, nxt - 1


def three_sat_to_independent_set(formula):
    """One vertex per literal occurrence; a triangle per clause; an edge between x and NOT x anywhere."""
    vertices = [(j, l) for j, c in enumerate(formula) for l in c]
    edges = set()
    for a, b in combinations(range(len(vertices)), 2):
        (ja, la), (jb, lb) = vertices[a], vertices[b]
        if ja == jb or la == -lb:
            edges.add((a, b))
    return len(vertices), edges, len(formula)          # graph, and the target size k = number of clauses


def neighbour_masks(nv, edges):
    nb = [0] * nv
    for a, b in edges:
        nb[a] |= 1 << b
        nb[b] |= 1 << a
    return nb


def max_independent_set(nb, mask):
    """Branch on the lowest vertex v: either v is left out, or v is in and its neighbours are out."""
    if mask == 0:
        return 0
    v = (mask & -mask).bit_length() - 1
    with_v = 1 + max_independent_set(nb, mask & ~nb[v] & ~(1 << v))
    if nb[v] & mask == 0:
        return with_v                                  # an isolated vertex is always worth taking
    return max(with_v, max_independent_set(nb, mask & ~(1 << v)))


def has_independent_set(nv, edges, k):
    return max_independent_set(neighbour_masks(nv, edges), (1 << nv) - 1) >= k


def independent_set_to_vertex_cover(nv, edges, k):
    return nv, edges, nv - k                           # S independent  <=>  V \ S covers every edge


def has_vertex_cover(nv, edges, k):
    """Take a vertex v that still has an uncovered edge: either v is in the cover,
    or all of its neighbours are (otherwise some edge at v is uncovered)."""
    nb = neighbour_masks(nv, edges)

    def cover(alive, k):                     # alive = vertices not yet put in the cover
        v = max(range(nv), key=lambda u: bin(nb[u] & alive).count("1") if alive >> u & 1 else -1)
        degree = bin(nb[v] & alive).count("1") if alive >> v & 1 else 0
        if degree == 0:
            return True                      # no uncovered edge is left
        if k <= 0:
            return False
        if cover(alive & ~(1 << v), k - 1):
            return True
        return degree <= k and cover(alive & ~nb[v], k - degree)

    return cover((1 << nv) - 1, k)


def independent_set_to_clique(nv, edges, k):
    complement = {(a, b) for a, b in combinations(range(nv), 2) if (a, b) not in edges}
    return nv, complement, k


def has_clique(nv, edges, k):
    """Grow a clique vertex by vertex; candidates are the common neighbours of everything chosen so far."""
    nb = neighbour_masks(nv, edges)

    def grow(size, candidates):
        if size >= k:
            return True
        if size + bin(candidates).count("1") < k:
            return False
        while candidates:
            v = (candidates & -candidates).bit_length() - 1
            candidates &= ~(1 << v)
            if grow(size + 1, candidates & nb[v]):
                return True
        return False

    return grow(0, (1 << nv) - 1)


def three_sat_to_subset_sum(formula, n):
    """Decimal digits: one per variable (high) and one per clause (low). Returns (numbers, target)."""
    k = len(formula)
    digit = lambda pos: 10 ** (k + n - 1 - pos)        # positions 0..n-1 variables, n..n+k-1 clauses
    numbers = []
    for i in range(1, n + 1):
        for sign in (1, -1):                           # v_i for x_i, v'_i for NOT x_i
            x = digit(i - 1)
            for j, c in enumerate(formula):
                if sign * i in c:
                    x += digit(n + j)
            numbers.append(x)
    for j in range(k):
        numbers += [digit(n + j), 2 * digit(n + j)]    # slack numbers s_j and s'_j
    target = sum(digit(i) for i in range(n)) + sum(4 * digit(n + j) for j in range(k))
    return numbers, target


def has_subset_sum(numbers, target):
    """Meet in the middle (Chapter 14): all subset sums of each half, then look for a matching pair."""
    def all_sums(part):
        sums = [0]
        for x in part:
            sums += [t + x for t in sums]
        return sums
    half = len(numbers) // 2
    right = set(all_sums(numbers[half:]))
    return any(target - t in right for t in all_sums(numbers[:half]))


def random_3cnf(n, k):
    return [[v * random.choice((1, -1)) for v in random.sample(range(1, n + 1), 3)] for _ in range(k)]


def tricky_3cnf(n):
    """All 8 sign patterns on three variables (unsatisfiable), maybe minus one, plus two random clauses."""
    a, b, c = random.sample(range(1, n + 1), 3)
    f = [[sa * a, sb * b, sc * c] for sa in (1, -1) for sb in (1, -1) for sc in (1, -1)]
    if random.random() < 0.5:
        f.pop(random.randrange(8))
    f += random_3cnf(n, 2)
    random.shuffle(f)
    return f


print("A worked example: (x1 or x2 or x3) and (not x1 or not x2 or x3) and (x1 or not x2 or not x3)")
ex = [[1, 2, 3], [-1, -2, 3], [1, -2, -3]]
nv, E, k = three_sat_to_independent_set(ex)
print(f"  independent set instance: {nv} vertices, {len(E)} edges, k = {k};"
      f" answer {has_independent_set(nv, E, k)}")
nums, target = three_sat_to_subset_sum(ex, 3)
print("  subset sum numbers:", [str(x).zfill(6) for x in nums])
print("  target:", target)

print("\nSAT -> 3-SAT on a formula with clauses of length 1, 2 and 5:")
f = [[1], [-1, 2], [-2, 3, -4, 5, 1]]
g, m = sat_to_3sat(f, 5)
print("  ", f, "->", g, f"({m} variables)")

print("\nRandom checks: the answer is preserved by every reduction")
agree = {"SAT->3SAT": 0, "3SAT->IS": 0, "IS->VC": 0, "IS->Clique": 0, "3SAT->SubsetSum": 0}
sat_count = general_sat = 0
trials = 200
for _ in range(trials):
    n = 4
    k = random.randint(3, 9)
    general = [[v * random.choice((1, -1)) for v in random.sample(range(1, n + 1), random.randint(1, n))]
               for _ in range(k)]
    g, m = sat_to_3sat(general, n)
    general_sat += satisfiable(general, n)
    agree["SAT->3SAT"] += satisfiable(general, n) == satisfiable(g, m)
    f3 = tricky_3cnf(n)
    truth = satisfiable(f3, n)
    sat_count += truth
    nv, E, kk = three_sat_to_independent_set(f3)
    is_answer = has_independent_set(nv, E, kk)
    agree["3SAT->IS"] += truth == is_answer
    agree["IS->VC"] += is_answer == has_vertex_cover(*independent_set_to_vertex_cover(nv, E, kk))
    agree["IS->Clique"] += is_answer == has_clique(*independent_set_to_clique(nv, E, kk))
    agree["3SAT->SubsetSum"] += truth == has_subset_sum(*three_sat_to_subset_sum(f3, n))
for name, count in agree.items():
    print(f"  {name:16} agreed on {count} of {trials} instances")
print(f"  satisfiable: {general_sat} of the {trials} general formulas, {sat_count} of the {trials} 3-CNF formulas")
