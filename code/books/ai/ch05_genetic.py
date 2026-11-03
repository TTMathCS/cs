# Chapter 5: local beam search and a genetic algorithm for 8-queens, from scratch.
# A state is a string of 8 digits: digit c is the row (1-8) of the queen in column c.
# Fitness = number of NON-attacking pairs (28 for a solution).
import random
from functools import lru_cache

N = 8
MAX_FIT = N * (N - 1) // 2


@lru_cache(maxsize=None)
def fitness(s):
    # Count queens on each row and each diagonal; k queens on one line make k(k-1)/2 attacking pairs.
    rows, up, down = {}, {}, {}
    for c, r in enumerate(s):
        rows[r] = rows.get(r, 0) + 1
        up[r - c] = up.get(r - c, 0) + 1
        down[r + c] = down.get(r + c, 0) + 1
    bad = sum(k * (k - 1) // 2 for line in (rows, up, down) for k in line.values())
    return MAX_FIT - bad


def neighbours(s):
    for c in range(N):
        for r in range(1, N + 1):
            if r != s[c]:
                yield s[:c] + (r,) + s[c + 1:]


def beam_search(k, rng, max_steps=100, stochastic=False):
    """Keep the k best states among all successors of the current k states."""
    beam = [tuple(rng.randint(1, N) for _ in range(N)) for _ in range(k)]
    for step in range(max_steps):
        for s in beam:
            if fitness(s) == MAX_FIT:
                return True, step
        pool = list({t for s in beam for t in neighbours(s)})
        if stochastic:                           # choose k successors with chance growing with fitness
            weights = [2.0 ** fitness(t) for t in pool]
            beam = rng.choices(pool, weights=weights, k=k)
        else:
            pool.sort(key=fitness, reverse=True)
            new = pool[:k]
            if max(map(fitness, new)) <= max(map(fitness, beam)):
                return False, step                # no successor is better: stuck
            beam = new
    return False, max_steps


def crossover(x, y, rng, cut=None):
    cut = rng.randint(1, N - 1) if cut is None else cut
    return x[:cut] + y[cut:]


def mutate(s, rng, rate):
    if rng.random() < rate:
        c = rng.randrange(N)
        s = s[:c] + (rng.randint(1, N),) + s[c + 1:]
    return s


def genetic(rng, select="tournament", pop_size=100, rate=0.8, max_gen=300, elite=2, trace=None):
    pop = [tuple(rng.randint(1, N) for _ in range(N)) for _ in range(pop_size)]
    for gen in range(max_gen):
        fits = [fitness(s) for s in pop]
        if trace is not None:
            trace.append((gen, max(fits), sum(fits) / pop_size))
        if MAX_FIT in fits:
            return True, gen, pop[fits.index(MAX_FIT)]
        ranked = [s for _, s in sorted(zip(fits, pop), reverse=True)]
        new = ranked[:elite]                     # elitism: keep the best unchanged
        if select == "roulette":                 # chance proportional to fitness
            cum = [0] * pop_size
            total = 0
            for i, f in enumerate(fits):
                total += f
                cum[i] = total

            def parent():
                return rng.choices(pop, cum_weights=cum)[0]
        else:                                    # tournament: best of 3 chosen at random

            def parent():
                return max(rng.sample(pop, 3), key=fitness)
        while len(new) < pop_size:
            new.append(mutate(crossover(parent(), parent(), rng), rng, rate))
        pop = new
    return False, max_gen, None


rng = random.Random(1975)
x, y = (1, 5, 8, 6, 3, 7, 2, 2), (6, 3, 1, 8, 4, 2, 5, 7)
child = crossover(x, y, rng, cut=3)
print("parents", "".join(map(str, x)), fitness(x), "and", "".join(map(str, y)), fitness(y))
print("child (cut after 3)", "".join(map(str, child)), fitness(child))
print()

runs = 50
print("local beam search on 8-queens,", runs, "runs each")
for k, stoch in ((1, False), (5, False), (20, False), (10, True)):
    results = [beam_search(k, rng, max_steps=50, stochastic=stoch) for _ in range(runs)]
    ok = [st for good, st in results if good]
    name = "stochastic" if stoch else "plain"
    print(f"  k={k:2d} {name:10s}  solved {len(ok):3d}/{runs}   mean steps when solved "
          f"{(sum(ok) / len(ok) if ok else 0):5.1f}")
print()

for select in ("roulette", "tournament"):
    gens = []
    for r in range(20):
        ok, g, sol = genetic(rng, select)
        if ok:
            assert fitness(sol) == MAX_FIT
            gens.append(g)
    gens.sort()
    print(f"genetic algorithm, {select:10s} selection, 20 runs: solved {len(gens):2d}/20 within 300"
          f" generations; median {gens[len(gens) // 2]:3d}, fastest {gens[0]:3d}, slowest {gens[-1]:3d}")

trace = []
ok, g, sol = genetic(random.Random(3), trace=trace)
print(f"\none tournament run (seed 3): solution {''.join(map(str, sol))} at generation {g}")
print(" gen  best  mean")
for gen, best, mean in trace[:: max(1, len(trace) // 8)] + trace[-1:]:
    print(f"{gen:4d}  {best:4d}  {mean:5.1f}")
