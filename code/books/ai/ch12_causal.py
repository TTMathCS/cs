# Chapter 12: observing versus intervening (Pearl's do-operator), from scratch.
# An invented example with a confounder:  Rough terrain -> Auto (the autonomous driving mode is chosen),
# Rough -> Success,  Auto -> Success.
# Planners choose the autonomous mode more often on rough terrain, and rough terrain lowers success.
# 1. Observational P(Success | Auto) versus interventional P(Success | do(Auto)), from the network.
# 2. The back-door adjustment formula, which computes the interventional answer from observational quantities.
# 3. The same from data: 200,000 simulated logged drives, and a simulated randomized experiment.
import numpy as np

P_R = 0.5                                   # P(Rough = 1)
P_A = {1: 0.8, 0: 0.2}                      # P(Auto = 1 | Rough)
P_S = {(1, 1): 0.60, (0, 1): 0.40,          # P(Success = 1 | Auto, Rough)
       (1, 0): 0.95, (0, 0): 0.90}


def joint(r, a, s, do_a=None):
    """P(r, a, s). With do_a set, the mechanism for Auto is replaced by a = do_a (the truncated product)."""
    pr = P_R if r else 1 - P_R
    if do_a is None:
        pa = P_A[r] if a else 1 - P_A[r]
    else:
        pa = 1.0 if a == do_a else 0.0
    ps = P_S[(a, r)] if s else 1 - P_S[(a, r)]
    return pr * pa * ps


def p_success_given(a, do=False):
    num = sum(joint(r, a, 1, do_a=a if do else None) for r in (0, 1))
    den = sum(joint(r, a, s, do_a=a if do else None) for r in (0, 1) for s in (0, 1))
    return num / den


def backdoor(a):
    """P(s | do(a)) = sum over r of P(s | a, r) P(r): adjust for the confounder."""
    return sum(P_S[(a, r)] * (P_R if r else 1 - P_R) for r in (0, 1))


def simulate(n, rng, randomized=False):
    r = rng.random(n) < P_R
    a = rng.random(n) < 0.5 if randomized else rng.random(n) < np.where(r, P_A[1], P_A[0])
    ps = np.select([a & r, ~a & r, a & ~r], [P_S[(1, 1)], P_S[(0, 1)], P_S[(1, 0)]], P_S[(0, 0)])
    s = rng.random(n) < ps
    return r, a, s


if __name__ == "__main__":
    print("1. Seeing versus doing")
    for a in (1, 0):
        print(f"  Auto={a}:  P(Success | Auto={a}) = {p_success_given(a):.4f}    "
              f"P(Success | do(Auto={a})) = {p_success_given(a, do=True):.4f}")
    print(f"  observed difference {p_success_given(1) - p_success_given(0):+.4f};  "
          f"causal effect {p_success_given(1, True) - p_success_given(0, True):+.4f}")
    for r in (1, 0):
        print(f"  within Rough={r}: success {P_S[(1, r)]:.2f} with Auto, {P_S[(0, r)]:.2f} without")
    print()
    print("2. Back-door adjustment over Rough")
    for a in (1, 0):
        print(f"  sum_r P(Success | Auto={a}, r) P(r) = {backdoor(a):.4f}")
    print()
    print("3. From data")
    rng = np.random.default_rng(7)
    r, a, s = simulate(200_000, rng)
    naive = s[a].mean() - s[~a].mean()
    adj = sum((s[a & (r == v)].mean() - s[~a & (r == v)].mean()) * (r == v).mean() for v in (True, False))
    print(f"  logged drives: naive difference {naive:+.4f}, back-door adjusted {adj:+.4f}")
    r2, a2, s2 = simulate(200_000, rng, randomized=True)
    print(f"  randomized experiment (mode chosen by coin flip): difference {s2[a2].mean() - s2[~a2].mean():+.4f}")
