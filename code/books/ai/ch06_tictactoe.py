# Chapter 6: tic-tac-toe solved by minimax, then by alpha-beta, then with a transposition table.
# A board is a string of 9 characters, 'X', 'O' or '.', read row by row. X moves first and is MAX.
LINES = [(0, 1, 2), (3, 4, 5), (6, 7, 8), (0, 3, 6), (1, 4, 7), (2, 5, 8), (0, 4, 8), (2, 4, 6)]


def winner(b):
    for i, j, k in LINES:
        if b[i] != "." and b[i] == b[j] == b[k]:
            return b[i]
    return None


def to_move(b):
    return "X" if b.count("X") == b.count("O") else "O"


def utility(b):
    """+1 if X has won, -1 if O has won, 0 for a draw; None if the game is not over."""
    w = winner(b)
    if w:
        return 1 if w == "X" else -1
    if "." not in b:
        return 0
    return None


def moves(b):
    return [i for i in range(9) if b[i] == "."]


def play(b, i):
    return b[:i] + to_move(b) + b[i + 1:]


stats = {"nodes": 0, "leaves": 0}


def minimax(b):
    stats["nodes"] += 1
    u = utility(b)
    if u is not None:
        stats["leaves"] += 1
        return u
    values = [minimax(play(b, i)) for i in moves(b)]
    return max(values) if to_move(b) == "X" else min(values)


def alphabeta(b, alpha=-2, beta=2):
    stats["nodes"] += 1
    u = utility(b)
    if u is not None:
        return u
    if to_move(b) == "X":
        v = -2
        for i in moves(b):
            v = max(v, alphabeta(play(b, i), alpha, beta))
            if v >= beta:
                return v                       # MIN above will never allow this: prune
            alpha = max(alpha, v)
        return v
    v = 2
    for i in moves(b):
        v = min(v, alphabeta(play(b, i), alpha, beta))
        if v <= alpha:
            return v                           # MAX above already has something better: prune
        beta = min(beta, v)
    return v


table = {}


def minimax_memo(b):
    if b in table:
        return table[b]
    stats["nodes"] += 1
    u = utility(b)
    if u is None:
        values = [minimax_memo(play(b, i)) for i in moves(b)]
        u = max(values) if to_move(b) == "X" else min(values)
    table[b] = u
    return u


empty = "." * 9
for name, f in (("plain minimax", minimax), ("alpha-beta", alphabeta), ("minimax + table", minimax_memo)):
    stats.update(nodes=0, leaves=0)
    v = f(empty)
    extra = f", {stats['leaves']} finished games" if f is minimax else ""
    print(f"{name:16s} value {v:+d}   nodes visited {stats['nodes']:7d}{extra}")

print(f"distinct positions reachable (incl. the empty board): {len(table)}")
print()
print("value of each first move for X (rows of the board):")
vals = [minimax_memo(play(empty, i)) for i in range(9)]
for r in range(3):
    print("   " + "  ".join(f"{vals[3 * r + c]:+d}" for c in range(3)))

# After X takes a corner, which replies by O lose?
b = play(empty, 0)
print("\nX in the top-left corner; value after each reply by O:")
reply = {i: minimax_memo(play(b, i)) for i in moves(b)}
grid = ["X"] + [f"{reply[i]:+d}" for i in range(1, 9)]
for r in range(3):
    print("   " + "  ".join(f"{grid[3 * r + c]:>2s}" for c in range(3)))


def best_move(b):
    sign = 1 if to_move(b) == "X" else -1
    return max(moves(b), key=lambda i: sign * minimax_memo(play(b, i)))


# a perfect player against itself
b, line = empty, []
while utility(b) is None:
    i = best_move(b)
    line.append(i)
    b = play(b, i)
print("\nperfect play, squares chosen:", line, " result", utility(b))
for r in range(3):
    print("   " + " ".join(b[3 * r: 3 * r + 3]))
