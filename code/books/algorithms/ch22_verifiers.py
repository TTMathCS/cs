"""Chapter 22: NP problems as fast verifiers of certificates, and search reduced to decision."""
import random
from itertools import product, permutations, combinations

random.seed(22)


# A CNF formula is a list of clauses; a clause is a list of nonzero integers: 3 means x3, -3 means NOT x3.
def verify_sat(formula, assignment):
    """assignment maps variable -> True/False. Time: linear in the size of the formula."""
    return all(any(assignment[abs(l)] == (l > 0) for l in clause) for clause in formula)


def verify_ham_cycle(n, edges, order):
    """order: a list of the n vertices. Checks it is a permutation and consecutive vertices are adjacent."""
    E = {frozenset(e) for e in edges}
    return sorted(order) == list(range(n)) and all(frozenset((order[i], order[(i + 1) % n])) in E for i in range(n))


def verify_subset_sum(numbers, target, chosen):
    """chosen: a set of indices. The certificate is the set; checking is one addition per number."""
    return all(0 <= i < len(numbers) for i in chosen) and sum(numbers[i] for i in chosen) == target


def verify_clique(edges, k, vertices):
    E = {frozenset(e) for e in edges}
    return len(set(vertices)) == k and all(frozenset(p) in E for p in combinations(vertices, 2))


def brute_force_sat(formula, n):
    for bits in product((False, True), repeat=n):
        a = dict(zip(range(1, n + 1), bits))
        if verify_sat(formula, a):
            return a
    return None


print("Verifying is fast, finding may not be:")
f = [[1, -2, 3], [-1, 2], [2, 3, -4], [-3, 4], [-1, -4]]
cert = {1: False, 2: False, 3: True, 4: True}
print("  formula", f)
print("  certificate", cert, "-> verifier says", verify_sat(f, cert))
print("  a wrong certificate", {1: True, 2: True, 3: True, 4: True}, "->",
      verify_sat(f, {1: True, 2: True, 3: True, 4: True}))

n = 9
cycle = list(range(n))
random.shuffle(cycle)
G = {tuple(sorted((cycle[i], cycle[(i + 1) % n]))) for i in range(n)}       # hide a Hamiltonian cycle
G |= {e for e in combinations(range(n), 2) if random.random() < 0.15}
G = sorted(G)
ok = verify_ham_cycle(n, G, cycle)
tried = 0
for rest in permutations(range(1, n)):                                       # brute force: fix vertex 0 first
    tried += 1
    if verify_ham_cycle(n, G, [0, *rest]):
        break
print(f"\n  Hamiltonian cycle, n = {n}, m = {len(G)}: the certificate checks in {n} edge lookups ({ok});"
      f" brute force tried {tried} of {8 * 7 * 6 * 5 * 4 * 3 * 2} orders")

nums, target = [267, 493, 869, 961, 1000, 1153, 1246, 1598, 1766, 1922], 5842
best = next(c for r in range(len(nums) + 1) for c in combinations(range(len(nums)), r)
            if sum(nums[i] for i in c) == target)
print(f"  subset sum {nums}, target {target}: certificate {[nums[i] for i in best]},"
      f" verified {verify_subset_sum(nums, target, set(best))}")
print("  clique {0,1,2} in a triangle plus a tail:", verify_clique([(0, 1), (1, 2), (0, 2), (2, 3)], 3, [0, 1, 2]))

print("\nSearch from decision: find a satisfying assignment with at most n + 1 calls to a yes/no oracle")
calls = 0


def oracle(formula, n):
    """A yes/no box for 'is this formula satisfiable?' (here brute force; in theory, any decider)."""
    global calls
    calls += 1
    return brute_force_sat(formula, n) is not None


def fix(formula, var, value):
    """Substitute x_var = value: drop satisfied clauses, delete the false literal from the others."""
    lit = var if value else -var
    return [[l for l in c if l != -lit] for c in formula if lit not in c]


def search(formula, n):
    if not oracle(formula, n):
        return None
    assignment = {}
    for v in range(1, n + 1):
        g = fix(formula, v, True)
        if all(g_c for g_c in g) and oracle(g, n):     # an empty clause can never be satisfied
            formula, assignment[v] = g, True
        else:
            formula, assignment[v] = fix(formula, v, False), False
    return assignment


calls = 0
a = search(f, 4)
print(f"  found {a}, valid {verify_sat(f, a)}, oracle calls {calls}")
g = [[1, 2], [1, -2], [-1, 2], [-1, -2]]
calls = 0
print(f"  {g}: {search(g, 2)} after {calls} call")
