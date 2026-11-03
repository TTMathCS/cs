# Chapter 13: a small dynamic Bayesian network, filtered exactly.
# A robot's battery level B (0..5) and its battery meter M. In the "persistent failure" model a
# second hidden variable Broken can switch on and then stays on; a broken meter reads 0.
# We compare it with a "transient failure" model where any single reading can be a stray 0.
import numpy as np

LEVELS = 6


def battery_transition():
    T = np.zeros((LEVELS, LEVELS))      # T[b, b'] = P(B_t = b' | B_{t-1} = b)
    for b in range(LEVELS):
        if b == 0:
            T[b, b] = 1.0
        else:
            T[b, b], T[b, b - 1] = 0.95, 0.05
    return T


def meter_working(b, m):
    """A working meter reads the level, or one off, with probability 0.8 / 0.1 / 0.1 (clipped)."""
    p = np.zeros(LEVELS)
    for d, pd in ((0, 0.8), (-1, 0.1), (1, 0.1)):
        p[min(LEVELS - 1, max(0, b + d))] += pd
    return p[m]


TB = battery_transition()
readings = [5] * 15 + [0] * 12

# transient model: hidden state is B alone; each reading is a stray 0 with probability 0.03
f = np.full(LEVELS, 1 / LEVELS)
trans_rows = []
for m in readings:
    like = np.array([0.97 * meter_working(b, m) + 0.03 * (m == 0) for b in range(LEVELS)])
    f = like * (f @ TB)
    f /= f.sum()
    trans_rows.append(f[0])

# persistent model: hidden state is the pair (B, Broken); 12 joint states
P_BREAK = 0.001
f = np.zeros((LEVELS, 2))
f[:, 0] = 1 / LEVELS                    # start: meter working, level unknown
pers_rows = []
for m in readings:
    pred = np.zeros((LEVELS, 2))
    for k in range(2):                  # the two chains are independent in the transition
        for k2 in range(2):
            pk = 1.0 if (k == 1 and k2 == 1) else (0.0 if k == 1 else (P_BREAK if k2 == 1 else 1 - P_BREAK))
            pred[:, k2] += pk * (f[:, k] @ TB)
    like = np.array([[meter_working(b, m), 1.0 if m == 0 else 0.0] for b in range(LEVELS)])
    f = like * pred
    f /= f.sum()
    pers_rows.append((f[0].sum(), f[:, 1].sum(), f.sum(axis=1) @ np.arange(LEVELS)))

print("step  reading   transient: P(B=0)   persistent: P(B=0)  P(broken)  E[B]")
for t in list(range(13, 21)) + [24, 27]:
    print(f"{t:4d}  {readings[t - 1]:7d}   {trans_rows[t - 1]:17.4f}   {pers_rows[t - 1][0]:18.4f}"
          f"  {pers_rows[t - 1][1]:9.4f}  {pers_rows[t - 1][2]:4.2f}")

print("\nwhy factor the state: numbers needed for one transition step")
print("  n Boolean state variables   full transition matrix   DBN with 2 parents per variable")
for n in (5, 10, 20, 30):
    print(f"  {n:24d}   {float(2 ** n) ** 2:22.3g}   {n * 4:31d}")
