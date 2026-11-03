# Chapter 20: specification gaming in a tiny race track, solved exactly by value iteration.
# The designer wants the boat to reach the finish. The proxy reward pays +10 at the finish and
# +1 each time the boat enters the bonus square, which "respawns" (pays again every visit).
import numpy as np

N, FINISH, BONUS = 7, 6, 2          # squares 0..6; start at 0; finish at 6 ends the episode


def solve(gamma, bonus_respawns):
    """Value iteration. A state is (square, bonus_taken); actions: left (-1) or right (+1)."""
    states = [(s, t) for s in range(N) for t in (0, 1)]
    V = {st: 0.0 for st in states}
    def step(st, a):
        s, t = st
        s2 = min(max(s + a, 0), N - 1)
        r, t2 = 0.0, t
        if s2 == BONUS and s2 != s and (bonus_respawns or t == 0):
            r, t2 = 1.0, 1
        if s2 == FINISH:
            r += 10.0
        return (s2, t2), r, s2 == FINISH
    for _ in range(2000):
        V = {st: (0.0 if st[0] == FINISH else max(r + (0 if done else gamma * V[n])
                  for n, r, done in (step(st, a) for a in (-1, 1)))) for st in states}
    def policy(st):
        best = max((-1, 1), key=lambda a: (lambda n, r, d: r + (0 if d else gamma * V[n]))(*step(st, a)))
        return best
    # roll out the greedy policy from the start for 30 steps
    st, path, total, true_done = (0, 0), [0], 0.0, False
    for k in range(30):
        n, r, done = step(st, policy(st))
        total += r; st = n; path.append(n[0])
        if done:
            true_done = True; break
    return V[(0, 0)], path, total, true_done


for respawn in (True, False):
    label = "bonus pays on every visit (the gamed proxy)" if respawn else "bonus pays once (repaired reward)"
    print(label)
    for gamma in (0.3, 0.5, 0.9, 0.95, 0.99):
        v, path, total, done = solve(gamma, respawn)
        show = "".join(str(p) for p in path[:16]) + ("..." if len(path) > 16 else "")
        print(f"   gamma {gamma:<4}  value {v:6.2f}  squares visited {show:<19} "
              f"proxy points {total:5.1f}  finished: {done}")
    print()

# The threshold. Standing on the bonus square: looping (back to 1, forward to 2, ...) earns 1 every
# two steps, worth g/(1-g^2); driving on to the finish (4 more steps) is worth 10 g^3.
print("standing on the bonus square:")
for g in (0.30, 0.34, 0.40, 0.60, 0.90, 0.93, 0.94, 0.95, 0.99):
    loop = g / (1 - g ** 2)
    go = 10 * g ** 3
    print(f"   gamma {g:.2f}: keep looping {loop:5.2f}  vs  finish {go:5.2f}"
          f"  -> {'loop' if loop > go else 'finish'}")
