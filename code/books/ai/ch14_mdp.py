# Chapter 14: Markov decision processes from scratch on the 4x3 grid world.
# The agent moves N, E, S, W; it goes the intended way with probability 0.8 and slips to each side
# with probability 0.1; bumping a wall means staying put. Squares (4,3) = +1 and (4,2) = -1 end the game.
import numpy as np

W, H = 4, 3
WALL = (2, 2)
TERMINAL = {(4, 3): 1.0, (4, 2): -1.0}
STATES = [(x, y) for y in range(1, H + 1) for x in range(1, W + 1) if (x, y) != WALL]
IDX = {s: i for i, s in enumerate(STATES)}
ACTIONS = {"N": (0, 1), "E": (1, 0), "S": (0, -1), "W": (-1, 0)}
SIDES = {"N": "EW", "S": "EW", "E": "NS", "W": "NS"}
ARROW = {"N": "^", "E": ">", "S": "v", "W": "<"}


def move(s, a):
    x, y = s[0] + ACTIONS[a][0], s[1] + ACTIONS[a][1]
    if not (1 <= x <= W and 1 <= y <= H) or (x, y) == WALL:
        return s
    return (x, y)


def model():
    """P[a][i, j] = P(j | i, a); terminal states have no outgoing transitions (absorbing, value 0 after)."""
    n = len(STATES)
    P = {a: np.zeros((n, n)) for a in ACTIONS}
    for s in STATES:
        if s in TERMINAL:
            continue
        for a in ACTIONS:
            P[a][IDX[s], IDX[move(s, a)]] += 0.8
            for side in SIDES[a]:
                P[a][IDX[s], IDX[move(s, side)]] += 0.1
    return P


def rewards(r):
    R = np.full(len(STATES), r)
    for s, v in TERMINAL.items():
        R[IDX[s]] = v
    return R


def value_iteration(R, P, gamma, eps=1e-6, history=None):
    U = np.zeros(len(STATES))
    for it in range(1, 10000):
        Q = np.array([P[a] @ U for a in ACTIONS])          # expected next value for each action
        U_new = R + gamma * Q.max(axis=0)
        delta = np.abs(U_new - U).max()
        U = U_new
        if history is not None:
            history.append(U.copy())
        if delta <= eps * (1 - gamma) / gamma if gamma < 1 else delta <= eps:
            return U, it


def greedy(U, P):
    acts = list(ACTIONS)
    Q = np.array([P[a] @ U for a in acts])
    return [acts[k] for k in Q.argmax(axis=0)]


def policy_iteration(R, P, gamma):
    acts = list(ACTIONS)
    pi = ["N"] * len(STATES)
    for it in range(1, 100):
        # policy evaluation: solve U = R + gamma * P_pi U exactly
        P_pi = np.array([P[pi[i]][i] for i in range(len(STATES))])
        U = np.linalg.solve(np.eye(len(STATES)) - gamma * P_pi, R)
        new = greedy(U, P)
        # keep the old action when it is still a best one (avoids flipping between ties)
        Q = np.array([P[a] @ U for a in acts])
        new = [pi[i] if Q[acts.index(pi[i]), i] >= Q[:, i].max() - 1e-12 else new[i] for i in range(len(STATES))]
        if new == pi:
            return pi, U, it
        pi = new


def show(U, pi):
    for y in range(H, 0, -1):
        row = []
        for x in range(1, W + 1):
            s = (x, y)
            if s == WALL:
                row.append("    ####   ")
            elif s in TERMINAL:
                row.append(f"   {TERMINAL[s]:+.0f}      ")
            else:
                row.append(f" {ARROW[pi[IDX[s]]]} {U[IDX[s]]:7.3f} ")
        print("   " + "|".join(row))


P = model()
R = rewards(-0.04)
U, its = value_iteration(R, P, 1.0)
print(f"r = -0.04, gamma = 1: value iteration converged in {its} sweeps")
show(U, greedy(U, P))

pi, U2, its2 = policy_iteration(R, P, 1.0)
print(f"policy iteration: {its2} rounds, same policy: {pi == greedy(U, P)},"
      f" max difference in values {np.abs(U - U2).max():.2e}")

print("\nthe policy for other living rewards r (gamma = 1)")
for r in (-2.0, -0.4, -0.01, 0.0):
    if r >= 0:
        U, _ = value_iteration(rewards(r), P, 0.999)     # with r = 0 use gamma < 1 so values stay finite
        print(f"r = {r} (gamma 0.999)")
    else:
        U, _ = value_iteration(rewards(r), P, 1.0)
        print(f"r = {r}")
    show(U, greedy(U, P))

print("\ncontraction: gamma = 0.9, r = -0.04; error ||U_i - U*|| and the ratio between successive errors")
hist = []
Ustar, _ = value_iteration(R, P, 0.9, eps=1e-12, history=hist)
errs = [np.abs(h - Ustar).max() for h in hist]
U0err = np.abs(Ustar).max()
print(f"  i=0   error {U0err:.6f}")
for i in (1, 2, 3, 5, 10, 20, 40):
    print(f"  i={i:<3d} error {errs[i - 1]:.6f}   ratio to previous {errs[i - 1] / (errs[i - 2] if i > 1 else U0err):.4f}"
          f"   bound 0.9^i * error_0 = {0.9 ** i * U0err:.6f}")
