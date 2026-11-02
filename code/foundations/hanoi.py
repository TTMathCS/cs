def hanoi(n, source, target, spare, moves):
    """Moves n discs from source to target, never putting a disc on a smaller one."""
    if n == 0:                               # base case: nothing to move
        return
    hanoi(n - 1, source, spare, target, moves)   # 1. move the n-1 smaller discs out of the way
    moves.append((n, source, target))            # 2. move the biggest disc
    hanoi(n - 1, spare, target, source, moves)   # 3. move the n-1 smaller discs on top of it


def factorial(n):
    """n! = n * (n-1)!, with 0! = 1."""
    return 1 if n == 0 else n * factorial(n - 1)


if __name__ == "__main__":
    moves = []
    hanoi(3, "A", "C", "B", moves)
    for disc, a, b in moves:
        print(f"disc {disc}: {a} -> {b}")
    for n in [1, 2, 3, 10, 20]:
        m = []
        hanoi(n, "A", "C", "B", m)
        print(f"{n} discs: {len(m)} moves")
    print(factorial(10))
