# Chapter 5: hill climbing on n-queens, with sideways moves and random restarts.
# State: queen[c] = row of the queen in column c (one queen per column).
# h(state) = number of pairs of queens that attack each other; a solution has h = 0.
import random


def conflicts(queen):
    """Number of attacking pairs: same row or same diagonal."""
    n, h = len(queen), 0
    for a in range(n):
        for b in range(a + 1, n):
            if queen[a] == queen[b] or abs(queen[a] - queen[b]) == b - a:
                h += 1
    return h


def best_neighbours(queen, h):
    """Try every move 'put the queen of column c in row r'; return the lowest h and the moves reaching it."""
    n = len(queen)
    best, moves = None, []
    for c in range(n):
        old = queen[c]
        # attacks of the queen in column c, before the move
        before = sum(1 for d in range(n) if d != c and
                     (queen[d] == old or abs(queen[d] - old) == abs(d - c)))
        for r in range(n):
            if r == old:
                continue
            after = sum(1 for d in range(n) if d != c and
                        (queen[d] == r or abs(queen[d] - r) == abs(d - c)))
            value = h - before + after
            if best is None or value < best:
                best, moves = value, [(c, r)]
            elif value == best:
                moves.append((c, r))
    return best, moves


def hill_climb(n, rng, max_sideways=0):
    """Steepest descent on h. Returns (solved, steps). Sideways moves allowed up to max_sideways in a row."""
    queen = [rng.randrange(n) for _ in range(n)]
    h, steps, sideways = conflicts(queen), 0, 0
    while h > 0:
        best, moves = best_neighbours(queen, h)
        if best > h:
            break                                   # strict local minimum
        if best == h:                               # plateau or shoulder
            if sideways >= max_sideways:
                break
            sideways += 1
        else:
            sideways = 0
        c, r = rng.choice(moves)                    # ties broken at random
        queen[c] = r
        h = best
        steps += 1
    return h == 0, steps, queen


def trials(n, runs, max_sideways, rng):
    ok_steps, fail_steps = [], []
    for _ in range(runs):
        solved, steps, _ = hill_climb(n, rng, max_sideways)
        (ok_steps if solved else fail_steps).append(steps)
    return ok_steps, fail_steps


rng = random.Random(5)
# a hand-checkable example: the board used in the text
example = [4, 5, 6, 3, 4, 5, 6, 5]
print("example board", example, "h =", conflicts(example))
best, moves = best_neighbours(example, conflicts(example))
print("best neighbour h =", best, "reached by", len(moves), "moves, e.g.", moves[:4])
print()

print(" n  sideways  runs  solved   success  steps(success)  steps(failure)  expected steps with restarts")
for n, side in ((8, 0), (8, 100), (16, 0), (16, 100)):
    runs = 1000 if n == 8 else 150
    ok, fail = trials(n, runs, side, rng)
    p = len(ok) / runs
    s_ok = sum(ok) / len(ok) if ok else float("nan")
    s_fail = sum(fail) / len(fail) if fail else 0.0
    # Random restarts: expected (1-p)/p failed runs, then one successful run.
    expected = s_ok + (1 - p) / p * s_fail if p > 0 else float("inf")
    print(f"{n:2d}  {side:8d}  {runs:4d}  {len(ok):6d}  {p:8.3f}  {s_ok:14.1f}  {s_fail:14.1f}  {expected:10.1f}")

print()
# random-restart hill climbing always finds a solution: count restarts on 10 tries
restarts = []
for _ in range(10):
    k = 1
    while not hill_climb(8, rng)[0]:
        k += 1
    restarts.append(k)
print("restarts needed (8-queens, no sideways), 10 tries:", restarts, " mean", sum(restarts) / 10)
