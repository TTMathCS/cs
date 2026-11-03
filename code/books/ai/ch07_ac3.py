# Chapter 7: arc consistency with AC-3 (Mackworth 1977), traced, and its power and limits.
from collections import deque


def ac3(variables, domains, neighbours, ok, trace=False):
    """domains: dict var -> set. ok(x, a, y, b) is the constraint between x and y.
    Returns (consistent?, number of revise calls, number of values removed)."""
    queue = deque((x, y) for x in variables for y in neighbours[x])
    in_queue = set(queue)
    revisions = removed = 0
    while queue:
        x, y = queue.popleft()
        in_queue.discard((x, y))
        revisions += 1
        gone = {a for a in domains[x] if not any(ok(x, a, y, b) for b in domains[y])}
        if gone:
            domains[x] -= gone
            removed += len(gone)
            if trace:
                print(f"  revise({x},{y}): remove {sorted(gone)} -> {x} = {sorted(domains[x])}")
            if not domains[x]:
                return False, revisions, removed
            for z in neighbours[x]:
                if z != y and (z, x) not in in_queue:
                    queue.append((z, x))
                    in_queue.add((z, x))
        elif trace:
            print(f"  revise({x},{y}): nothing")
    return True, revisions, removed


# 1. X < Y < Z with domains {1, 2, 3}
rel = {("X", "Y"): lambda a, b: a < b, ("Y", "Z"): lambda a, b: a < b}


def ok_chain(x, a, y, b):
    if (x, y) in rel:
        return rel[(x, y)](a, b)
    return rel[(y, x)](b, a)


doms = {v: {1, 2, 3} for v in "XYZ"}
nb = {"X": ["Y"], "Y": ["X", "Z"], "Z": ["Y"]}
print("X < Y < Z, domains {1,2,3}:")
print(" ", ac3("XYZ", doms, nb, ok_chain, trace=True), {v: sorted(d) for v, d in doms.items()})

# 2. a triangle that needs three colours but has only two: arc consistent, yet no solution
doms = {v: {"red", "green"} for v in "ABC"}
nb = {"A": ["B", "C"], "B": ["A", "C"], "C": ["A", "B"]}
res = ac3("ABC", doms, nb, lambda x, a, y, b: a != b)
print("\ntriangle with 2 colours: AC-3 says consistent =", res[0], "removed", res[2], "values; domains",
      {v: sorted(d) for v, d in doms.items()})


# 3. Sudoku: AC-3 alone
def sudoku_domains(grid):
    cells = [(r, c) for r in range(9) for c in range(9)]
    nb = {}
    for r, c in cells:
        ps = {(r, k) for k in range(9)} | {(k, c) for k in range(9)}
        ps |= {(3 * (r // 3) + i, 3 * (c // 3) + j) for i in range(3) for j in range(3)}
        ps.discard((r, c))
        nb[(r, c)] = sorted(ps)
    doms = {(r, c): ({int(grid[9 * r + c])} if grid[9 * r + c] != "." else set(range(1, 10))) for r, c in cells}
    return cells, doms, nb


easy = ("..3.2.6.." "9..3.5..1" "..18.64.." "..81.29.." "7.......8"
        "..67.82.." "..26.95.." "8..2.3..9" "..5.1.3..")
hard = ("4.....8.5" ".3......." "...7....." ".2.....6." "....8.4.."
        "....1...." "...6.3.7." "5..2....." "1.4......")
for name, g in (("easy", easy), ("hard", hard)):
    cells, doms, nb = sudoku_domains(g)
    arcs = sum(len(v) for v in nb.values())
    before = sum(len(d) for d in doms.values())
    ok, revs, rem = ac3(cells, doms, nb, lambda x, a, y, b: a != b)
    after = sum(len(d) for d in doms.values())
    solved = sum(1 for d in doms.values() if len(d) == 1)
    print(f"\nSudoku {name}: {arcs} arcs, {revs} revise calls, values {before} -> {after}, "
          f"cells decided {solved}/81")
    if name == "hard":
        print("  domain sizes after AC-3:")
        for r in range(9):
            print("   " + " ".join(str(len(doms[(r, c)])) for c in range(9)))
