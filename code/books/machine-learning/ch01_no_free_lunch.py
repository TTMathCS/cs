"""Chapter 1: the no-free-lunch theorem, checked by brute force.

Inputs are the 8 strings of 3 bits.  A target function labels each one 0 or 1,
so there are 2**8 = 256 possible targets.  Every learner sees the labels of
the same 4 training inputs and must guess the other 4.  Averaged over all 256
targets, every learner gets exactly half of the unseen inputs right.
"""
from itertools import product

INPUTS = list(product([0, 1], repeat=3))     # 8 inputs
TRAIN = INPUTS[:4]                           # 000, 001, 010, 011
TEST = INPUTS[4:]                            # 100, 101, 110, 111 (never seen)


def hamming(a, b):
    return sum(u != v for u, v in zip(a, b))


def nearest_neighbour(data, x):
    return min(data, key=lambda row: (hamming(row[0], x), row[0]))[1]


def majority(data, x):
    ones = sum(label for _, label in data)
    return 1 if 2 * ones >= len(data) else 0


def always_zero(data, x):
    return 0


def contrarian(data, x):
    """Deliberately silly: the opposite of what nearest neighbour says."""
    return 1 - nearest_neighbour(data, x)


def parity_guess(data, x):
    """Bets that the target is the parity (XOR) of the bits."""
    return sum(x) % 2


LEARNERS = [nearest_neighbour, majority, always_zero, contrarian, parity_guess]

if __name__ == "__main__":
    targets = list(product([0, 1], repeat=len(INPUTS)))      # 256 functions
    print(f"{len(targets)} target functions, {len(TEST)} unseen inputs each")
    print(f"{'learner':18} {'mean off-training accuracy':>27} {'best':>5} {'worst':>6}")
    for learn in LEARNERS:
        scores = []
        for t in targets:
            f = dict(zip(INPUTS, t))
            data = [(x, f[x]) for x in TRAIN]
            right = sum(learn(data, x) == f[x] for x in TEST)
            scores.append(right / len(TEST))
        mean = sum(scores) / len(scores)
        print(f"{learn.__name__:18} {mean:27.4f} {max(scores):5.2f} {min(scores):6.2f}")
    # On one particular world, the learners differ a lot:
    f = {x: (x[0] ^ x[1] ^ x[2]) for x in INPUTS}           # the parity target
    data = [(x, f[x]) for x in TRAIN]
    print("on the parity target alone:",
          {l.__name__: sum(l(data, x) == f[x] for x in TEST) / 4 for l in LEARNERS})
