# Chapter 6: Monte Carlo tree search with UCT (Kocsis and Szepesvari 2006), from scratch, on tic-tac-toe.
# Each node stores N (visits) and W (total reward for the player who made the move into the node).
import math
import random
from functools import lru_cache

LINES = [(0, 1, 2), (3, 4, 5), (6, 7, 8), (0, 3, 6), (1, 4, 7), (2, 5, 8), (0, 4, 8), (2, 4, 6)]


def winner(b):
    for i, j, k in LINES:
        if b[i] != "." and b[i] == b[j] == b[k]:
            return b[i]
    return "draw" if "." not in b else None


def to_move(b):
    return "X" if b.count("X") == b.count("O") else "O"


def moves(b):
    return [i for i in range(9) if b[i] == "."]


def play(b, i):
    return b[:i] + to_move(b) + b[i + 1:]


class Node:
    __slots__ = ("board", "parent", "move", "children", "untried", "N", "W")

    def __init__(self, board, parent=None, move=None, rng=None):
        self.board, self.parent, self.move = board, parent, move
        self.children = []
        self.untried = moves(board) if winner(board) is None else []
        if rng:
            rng.shuffle(self.untried)
        self.N, self.W = 0, 0.0


def uct_child(node, c):
    # UCB1: average reward + exploration bonus
    return max(node.children, key=lambda ch: ch.W / ch.N + c * math.sqrt(math.log(node.N) / ch.N))


def rollout(board, rng):
    while winner(board) is None:
        board = play(board, rng.choice(moves(board)))
    return winner(board)


def mcts(board, iterations, rng, c=math.sqrt(2)):
    root = Node(board, rng=rng)
    for _ in range(iterations):
        node = root
        # 1. selection: walk down through fully expanded nodes
        while not node.untried and node.children:
            node = uct_child(node, c)
        # 2. expansion: add one new child
        if node.untried:
            m = node.untried.pop()
            child = Node(play(node.board, m), node, m, rng)
            node.children.append(child)
            node = child
        # 3. simulation: random playout to the end
        result = rollout(node.board, rng)
        # 4. backpropagation: reward 1 for a win, 1/2 for a draw, for the player who moved into each node
        while node is not None:
            node.N += 1
            if node.parent is not None:
                mover = to_move(node.parent.board)
                node.W += 1.0 if result == mover else 0.5 if result == "draw" else 0.0
            node = node.parent
    return root


@lru_cache(maxsize=None)
def value(b):
    """Exact minimax value for X: +1, 0, -1."""
    w = winner(b)
    if w == "X":
        return 1
    if w == "O":
        return -1
    if w == "draw":
        return 0
    vals = [value(play(b, i)) for i in moves(b)]
    return max(vals) if to_move(b) == "X" else min(vals)


def perfect(b, rng):
    sign = 1 if to_move(b) == "X" else -1
    best = max(sign * value(play(b, i)) for i in moves(b))
    return rng.choice([i for i in moves(b) if sign * value(play(b, i)) == best])


def match(player_x, player_o, games, rng):
    score = {"X": 0, "O": 0, "draw": 0}
    for _ in range(games):
        b = "." * 9
        while winner(b) is None:
            b = play(b, (player_x if to_move(b) == "X" else player_o)(b, rng))
        score[winner(b)] += 1
    return score


rng = random.Random(2006)

root = mcts("." * 9, 3000, rng)
print("MCTS from the empty board, 3000 iterations: visits (and mean reward for X) per square")
grid = {ch.move: ch for ch in root.children}
for r in range(3):
    print("   " + "   ".join(f"{grid[3 * r + c].N:4d} ({grid[3 * r + c].W / grid[3 * r + c].N:.2f})"
                             for c in range(3)))

b = play("." * 9, 0)
root = mcts(b, 3000, rng)
best = max(root.children, key=lambda ch: ch.N)
print(f"\nafter X takes square 0, O's most visited reply: square {best.move} with {best.N} of 3000 visits"
      f" (the only reply that does not lose is 4, the centre)")


def uct_player(iterations):
    def choose(b, rng):
        root = mcts(b, iterations, rng)
        return max(root.children, key=lambda ch: ch.N).move   # play the most visited move
    return choose


def random_player(b, rng):
    return rng.choice(moves(b))


print("\nmatches of 20 games (X moves first): wins for X / wins for O / draws")
for it in (10, 100, 1000):
    s1 = match(uct_player(it), random_player, 20, rng)
    s2 = match(uct_player(it), perfect, 20, rng)
    s3 = match(perfect, uct_player(it), 20, rng)
    print(f"  UCT {it:4d} iterations as X vs random : {s1['X']:2d} / {s1['O']:2d} / {s1['draw']:2d}"
          f"     as X vs perfect: {s2['X']:2d} / {s2['O']:2d} / {s2['draw']:2d}"
          f"     as O vs perfect: {s3['X']:2d} / {s3['O']:2d} / {s3['draw']:2d}")
s = match(perfect, uct_player(4000), 10, rng)
print(f"  UCT 4000 iterations as O vs perfect, 10 games: {s['X']} / {s['O']} / {s['draw']}")
