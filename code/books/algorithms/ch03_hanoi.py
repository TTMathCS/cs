"""Chapter 3: the Towers of Hanoi.

hanoi() makes the moves recursively; play() checks that every move is legal;
shortest() searches every position breadth-first to confirm that 2^n - 1
moves is the true minimum for small n.
"""
from collections import deque


def hanoi(n, src="A", via="B", dst="C", moves=None):
    """Append the moves that carry discs 1..n from src to dst."""
    if moves is None:
        moves = []
    if n > 0:
        hanoi(n - 1, src, dst, via, moves)   # clear the n-1 smaller discs onto via
        moves.append((n, src, dst))          # move the largest disc
        hanoi(n - 1, via, src, dst, moves)   # bring the n-1 discs back on top of it
    return moves


def play(n, moves):
    """Carry out the moves on real pegs; fail loudly on an illegal move."""
    pegs = {"A": list(range(n, 0, -1)), "B": [], "C": []}
    for disc, s, d in moves:
        assert pegs[s] and pegs[s][-1] == disc, "disc is not on top"
        assert not pegs[d] or pegs[d][-1] > disc, "larger disc on smaller"
        pegs[d].append(pegs[s].pop())
    return pegs


def shortest(n):
    """Fewest moves from all-on-A to all-on-C, by breadth-first search.
    A position is a tuple: position[i] is the peg of disc i+1."""
    start, goal = (0,) * n, (2,) * n
    dist = {start: 0}
    queue = deque([start])
    while queue:
        pos = queue.popleft()
        if pos == goal:
            return dist[pos]
        tops = {}
        for disc in range(n - 1, -1, -1):    # the smallest disc on a peg wins
            tops[pos[disc]] = disc
        for p, disc in tops.items():
            for q in range(3):
                if q != p and (q not in tops or tops[q] > disc):
                    nxt = pos[:disc] + (q,) + pos[disc + 1:]
                    if nxt not in dist:
                        dist[nxt] = dist[pos] + 1
                        queue.append(nxt)


if __name__ == "__main__":
    print("Moves for 3 discs:")
    for k, (disc, s, d) in enumerate(hanoi(3), 1):
        print(f"  {k}. disc {disc}: {s} -> {d}")
    print()
    print(f"{'n':>3} {'moves made':>11} {'2^n - 1':>9} {'BFS minimum':>12}")
    for n in range(1, 11):
        moves = hanoi(n)
        pegs = play(n, moves)
        assert pegs["C"] == list(range(n, 0, -1))
        best = shortest(n)
        print(f"{n:>3} {len(moves):>11} {2**n - 1:>9} {best:>12}")
    print("all moves legal; every tower ends on C")
