def linear_steps(n):
    """Looks at every value once, like finding the largest: n steps."""
    steps = 0
    for _ in range(n):
        steps += 1
    return steps


def log_steps(n):
    """Halves the range until one value is left, like binary search: about log2(n) steps."""
    steps = 0
    while n > 1:
        n //= 2
        steps += 1
    return steps


def quadratic_steps(n):
    """Looks at every pair i < j, like checking for duplicates the slow way: n(n-1)/2 steps."""
    steps = 0
    for i in range(n):
        for j in range(i + 1, n):
            steps += 1
    return steps


if __name__ == "__main__":
    print("n halving linear pairs")
    for n in [10, 100, 1000, 4000]:
        print(n, log_steps(n), linear_steps(n), quadratic_steps(n))
