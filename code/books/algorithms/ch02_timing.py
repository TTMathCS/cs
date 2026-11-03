"""Chapter 2: timing Python code honestly with timeit.

Rules followed here: time a statement many times, repeat the measurement,
keep the minimum (the run least disturbed by other programs), and report
time per call. Your numbers will differ from the book's; the ratios matter.
"""
import random
import timeit


def best_time(stmt, number=None, repeat=5, g=None):
    t = timeit.Timer(stmt, globals=g)
    if number is None:                      # choose a count that takes about 0.02 s
        once = t.timeit(number=1)
        number = max(1, int(0.02 / max(once, 1e-7)))
    return min(t.repeat(repeat=repeat, number=number)) / number


def loop_sum(a):
    s = 0
    for x in a:
        s += x
    return s


if __name__ == "__main__":
    rng = random.Random(3)

    print("1. Same O(n) work, different constants: summing a list")
    for n in (10_000, 100_000):
        a = [rng.randrange(1000) for _ in range(n)]
        t_loop = best_time("loop_sum(a)", g={"loop_sum": loop_sum, "a": a})
        t_sum = best_time("sum(a)", g={"a": a})
        print(f"  n={n:>7}: Python loop {t_loop * 1e6:8.1f} us   built-in sum "
              f"{t_sum * 1e6:7.1f} us   ratio {t_loop / t_sum:4.1f}")

    print()
    print("2. Different growth: membership test in a list (O(n)) vs a set (O(1) expected)")
    for n in (1_000, 10_000, 100_000):
        a = list(range(n))
        s = set(a)
        x = -1                                  # absent: the worst case for the list
        t_list = best_time("x in a", g={"a": a, "x": x})
        t_set = best_time("x in s", g={"s": s, "x": x})
        print(f"  n={n:>7}: list {t_list * 1e6:9.2f} us   set {t_set * 1e6:6.3f} us")

    print()
    print("3. Same operation count, different memory order: summing via an index list")
    n = 1_000_000
    a = [rng.random() for _ in range(n)]       # a million float objects in memory
    in_order = list(range(n))
    shuffled = in_order[:]
    rng.shuffle(shuffled)
    g = {"a": a, "idx": in_order, "sh": shuffled}
    t_seq = best_time("sum([a[i] for i in idx])", g=g, number=1, repeat=3)
    t_rand = best_time("sum([a[i] for i in sh])", g=g, number=1, repeat=3)
    print(f"  in order {t_seq * 1e3:6.1f} ms   shuffled order {t_rand * 1e3:6.1f} ms"
          f"   ratio {t_rand / t_seq:4.1f}")
