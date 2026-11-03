"""Chapter 14: N-queens by backtracking, and Sudoku with constraint propagation."""

def queens(n):
    """Count solutions and search-tree nodes; place one queen per row."""
    cols, diag1, diag2 = set(), set(), set()   # occupied columns and diagonals
    count = nodes = 0
    first = None
    placed = []

    def go(r):
        nonlocal count, nodes, first
        nodes += 1
        if r == n:
            count += 1
            if first is None:
                first = list(placed)
            return
        for c in range(n):
            if c in cols or r - c in diag1 or r + c in diag2:
                continue                       # attacked: prune this branch
            cols.add(c); diag1.add(r - c); diag2.add(r + c); placed.append(c)
            go(r + 1)
            cols.remove(c); diag1.remove(r - c); diag2.remove(r + c); placed.pop()
    go(0)
    return count, nodes, first


def queens_bits(n):
    """The same search with bitmasks: one integer per constraint."""
    full = (1 << n) - 1

    def go(cols, d1, d2):
        if cols == full:
            return 1
        total = 0
        free = full & ~(cols | d1 | d2)
        while free:
            bit = free & -free                 # lowest free square in this row
            free -= bit
            total += go(cols | bit, ((d1 | bit) << 1) & full, (d2 | bit) >> 1)
        return total
    return go(0, 0, 0)


# ---------------- Sudoku ----------------
ROWS = "ABCDEFGHI"
SQUARES = [r + c for r in ROWS for c in "123456789"]
UNITS = ([[r + c for c in "123456789"] for r in ROWS] +
         [[r + c for r in ROWS] for c in "123456789"] +
         [[r + c for r in rs for c in cs] for rs in ("ABC", "DEF", "GHI") for cs in ("123", "456", "789")])
PEERS = {s: set().union(*[u for u in UNITS if s in u]) - {s} for s in SQUARES}
search_nodes = 0


class GiveUp(Exception):
    pass


def plain_backtrack(grid, limit=10 ** 6):
    """Fill empty cells left to right with any digit not clashing with a peer."""
    global search_nodes
    g = dict(zip(SQUARES, grid))

    def go(k):
        global search_nodes
        search_nodes += 1
        if search_nodes > limit:
            raise GiveUp
        while k < 81 and g[SQUARES[k]] != ".":
            k += 1
        if k == 81:
            return True
        s = SQUARES[k]
        used = {g[p] for p in PEERS[s]}
        for d in "123456789":
            if d not in used:
                g[s] = d
                if go(k + 1):
                    return True
        g[s] = "."
        return False
    try:
        go(0)
    except GiveUp:
        return None
    return "".join(g[s] for s in SQUARES)


def assign(cand, s, d):
    """Keep only d at s, propagating; return False on a contradiction."""
    return all(eliminate(cand, s, e) for e in cand[s] - {d})


def eliminate(cand, s, d):
    if d not in cand[s]:
        return True
    cand[s] = cand[s] - {d}
    if not cand[s]:
        return False                           # no digit left: dead end
    if len(cand[s]) == 1:                      # rule 1: a solved cell clears its peers
        (only,) = cand[s]
        if not all(eliminate(cand, p, only) for p in PEERS[s]):
            return False
    for u in UNITS:                            # rule 2: a digit with one place in a unit goes there
        if s in u:
            places = [q for q in u if d in cand[q]]
            if not places:
                return False
            if len(places) == 1 and not assign(cand, places[0], d):
                return False
    return True


def propagate_search(grid):
    global search_nodes
    cand = {s: set("123456789") for s in SQUARES}
    for s, ch in zip(SQUARES, grid):
        if ch != "." and not assign(cand, s, ch):
            return None

    def go(cand):
        global search_nodes
        search_nodes += 1
        if all(len(v) == 1 for v in cand.values()):
            return cand
        s = min((q for q in SQUARES if len(cand[q]) > 1), key=lambda q: len(cand[q]))  # fewest options
        for d in sorted(cand[s]):
            trial = {q: set(v) for q, v in cand.items()}
            if assign(trial, s, d):
                result = go(trial)
                if result:
                    return result
        return None
    result = go(cand)
    return "".join(next(iter(result[s])) for s in SQUARES)


def show(grid):
    return "\n".join(" ".join(grid[9 * r:9 * r + 9]) for r in range(9))


if __name__ == "__main__":
    print(" n  solutions  search nodes   bitmask count")
    for n in range(1, 11):
        count, nodes, _ = queens(n)
        print(f"{n:2d} {count:10d} {nodes:13d} {queens_bits(n):15d}")
    print("first 8-queens solution (column of the queen in each row):", queens(8)[2])

    puzzle = ("53..7...." "6..195..." ".98....6." "8...6...3" "4..8.3..1"
              "7...2...6" ".6....28." "...419..5" "....8..79")
    hard = ("4.....8.5" ".3......." "...7....." ".2.....6." "....8.4.."
            "....1...." "...6.3.7." "5..2....." "1.4......")
    for label, grid in (("puzzle 1", puzzle), ("puzzle 2", hard)):
        for name, solver in (("plain backtracking", plain_backtrack),
                             ("propagation + fewest options", propagate_search)):
            search_nodes = 0
            sol = solver(grid)
            if sol is None:
                print(f"{label}, {name}: gave up after {search_nodes - 1} search nodes")
            else:
                ok = (all(sorted(sol[SQUARES.index(q)] for q in u) == list("123456789") for u in UNITS)
                      and all(g in (".", c) for g, c in zip(grid, sol)))      # keeps the givens
                print(f"{label}, {name}: {search_nodes} search nodes, valid solution: {ok}")
        if label == "puzzle 1":
            print(show(sol))
