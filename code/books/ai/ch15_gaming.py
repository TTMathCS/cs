# Chapter 15: specification gaming and potential-based shaping, on a toy race track.
# A track of 21 squares, 0..20. The designer wants the agent to reach square 20 (reward 10, the end).
# Variant "checkpoint": to encourage progress, the designer also pays 1 each time the agent enters
# square 5. Variant "shaped": instead, a potential-based bonus gamma * phi(s') - phi(s) with
# phi(s) = s / 2 (Ng, Harada and Russell 1999). Q-learning, episodes of at most 60 steps.
import random

N, GOAL, CHECKPOINT, GAMMA = 21, 20, 5, 0.95


def reward(s, s2, variant):
    r = 10.0 if s2 == GOAL else 0.0
    if variant == "checkpoint" and s2 == CHECKPOINT and s != CHECKPOINT:
        r += 1.0
    if variant == "shaped":
        phi2 = 0.0 if s2 == GOAL else s2 / 2       # the potential of the terminal state is 0
        r += GAMMA * phi2 - s / 2
    return r


def learn(variant, episodes, rng, alpha=0.5, eps=0.1, cap=60):
    Q = [[0.0, 0.0] for _ in range(N)]             # actions: 0 = back, 1 = forward
    first_finish, finishes = None, 0
    for ep in range(episodes):
        s = 0
        for _ in range(cap):
            if rng.random() < eps:
                a = rng.randrange(2)
            else:
                a = 1 if Q[s][1] > Q[s][0] else (0 if Q[s][0] > Q[s][1] else rng.randrange(2))
            s2 = min(N - 1, s + 1) if a == 1 else max(0, s - 1)
            r = reward(s, s2, variant)
            target = r if s2 == GOAL else r + GAMMA * max(Q[s2])
            Q[s][a] += alpha * (target - Q[s][a])
            s = s2
            if s == GOAL:
                finishes += 1
                if first_finish is None:
                    first_finish = ep + 1
                break
    return Q, first_finish, finishes


def greedy_run(Q, cap=60):
    s, path = 0, [0]
    for _ in range(cap):
        s = min(N - 1, s + 1) if Q[s][1] >= Q[s][0] else max(0, s - 1)
        path.append(s)
        if s == GOAL:
            break
    return path


print(f"from square 4: stepping in and out of square 5 forever is worth 1/(1 - gamma^2) = {1 / (1 - GAMMA ** 2):.2f};"
      f" driving to the goal (passing 5 once) is worth 1 + gamma^15 * 10 = {1 + GAMMA ** 15 * 10:.2f}")
print("variant      first finish   finishes in 500 episodes   greedy policy after learning")
for variant in ("sparse", "checkpoint", "shaped"):
    Q, first, fin = learn(variant, 500, random.Random(1))
    path = greedy_run(Q)
    what = (f"reaches the goal in {len(path) - 1} steps" if path[-1] == GOAL
            else f"never finishes; ends {path[-6:]}")
    print(f"{variant:11s}  {str(first):>12s}   {fin:24d}   {what}")

print("\nover 20 seeds: mean episode of first finish and fraction of seeds whose greedy policy finishes")
for variant in ("sparse", "checkpoint", "shaped"):
    firsts, ok = [], 0
    for seed in range(20):
        Q, first, _ = learn(variant, 500, random.Random(seed))
        firsts.append(first if first is not None else 500)
        ok += greedy_run(Q)[-1] == GOAL
    print(f"{variant:11s}  first finish {sum(firsts) / 20:6.1f}   greedy policy finishes in {ok} of 20")
