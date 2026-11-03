# Chapter 14: a POMDP solved exactly by value iteration over alpha vectors: the tiger problem
# (Kaelbling, Littman and Cassandra 1998). A tiger is behind the left or the right door.
# Listening costs 1 and reports the correct side with probability 0.85. Opening the tiger's door
# costs 100; opening the other door earns 10. After a door is opened the tiger is placed again at random.
import numpy as np

S = ["tiger-left", "tiger-right"]
A = ["listen", "open-left", "open-right"]
O = ["hear-left", "hear-right"]
gamma = 0.95
R = np.array([[-1.0, -1.0],         # R[a, s]
              [-100.0, 10.0],
              [10.0, -100.0]])
T = np.array([np.eye(2), np.full((2, 2), 0.5), np.full((2, 2), 0.5)])       # T[a, s, s']
Z = np.array([[[0.85, 0.15], [0.15, 0.85]],                                  # Z[a, s', o]
              np.full((2, 2), 0.5), np.full((2, 2), 0.5)])


def belief_update(b, a, o):
    """b is P(tiger-left). Returns the new belief and P(o | b, a)."""
    bv = np.array([b, 1 - b])
    pred = bv @ T[a]
    new = pred * Z[a][:, o]
    return new[0] / new.sum(), new.sum()


GRID = np.linspace(0, 1, 1001)
BEL = np.stack([GRID, 1 - GRID], axis=1)


def backup(alphas):
    """One step of exact value iteration, done belief by belief on a fine grid.
    At a belief b, the best new vector for action a picks, for each observation o, the old vector k
    that maximises b . g[a][o][k]; the best over actions is the new vector for b. Every vector that is
    optimal somewhere on the grid is found this way, and duplicates are merged."""
    al = np.array(alphas)                                   # shape (K, 2)
    best_val, best_vec, best_act = np.full(len(GRID), -np.inf), np.zeros((len(GRID), 2)), np.zeros(len(GRID), int)
    for a in range(len(A)):
        vec = np.tile(R[a], (len(GRID), 1))
        for o in range(len(O)):
            g = (al * Z[a][:, o]) @ T[a].T                  # g[k](s) = sum_s' T[a,s,s'] Z[a,s',o] alpha_k(s')
            k = (BEL @ g.T).argmax(axis=1)                  # the best old vector for each belief
            vec = vec + gamma * g[k]
        val = (BEL * vec).sum(axis=1)
        better = val > best_val
        best_val[better], best_vec[better], best_act[better] = val[better], vec[better], a
    _, first = np.unique(np.round(best_vec, 9), axis=0, return_index=True)
    first = sorted(first)
    return [best_vec[i] for i in first], [int(best_act[i]) for i in first]


alphas, acts = [np.zeros(2)], [0]
print("horizon  vectors  value at b=0.5  action at b = 0.50 0.80 0.93 0.96 0.98")
for h in range(1, 101):
    alphas, acts = backup(alphas)
    if h in (1, 2, 3, 5, 10, 20, 50, 100):
        V = BEL @ np.array(alphas).T
        names = [A[acts[int(V[int(b * 1000)].argmax())]] for b in (0.5, 0.8, 0.93, 0.96, 0.98)]
        print(f"{h:7d}  {len(alphas):7d}  {V[500].max():14.3f}  " + " ".join(f"{n:>10}" for n in names))

V = BEL @ np.array(alphas).T
best = [acts[k] for k in V.argmax(axis=1)]
switch = [GRID[i] for i in range(1, len(GRID)) if best[i] != best[i - 1]]
print("policy after 100 steps: the action changes at beliefs", [round(float(x), 3) for x in switch])
print("  " + ", ".join(f"{A[a]} on [{lo:.3f}, {hi:.3f}]" for a, lo, hi in
                       zip([best[0]] + [best[int(round(s * 1000))] for s in switch], [0.0] + switch, switch + [1.0])))

b = 0.5
print("\nbelief P(tiger-left) while listening:", end=" ")
for o in [0, 0, 1, 0, 0]:
    b, p = belief_update(b, 0, o)
    print(f"{O[o]} -> {b:.4f}", end="; ")
print()
