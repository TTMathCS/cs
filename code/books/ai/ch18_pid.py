# Chapter 18: PID control from scratch. A cart of mass 1 with friction on a slope must move 1 m and stop.
# Plant: x'' = u - c x' - g   (u = motor force, c = friction, g = the slope's constant pull backwards).
import numpy as np

C_FRIC, G_SLOPE, TARGET, DT, T_END = 0.5, 0.5, 1.0, 0.001, 15.0


def simulate(kp, ki, kd, u_max=None, anti_windup=False):
    x = v = integ = 0.0
    xs = []
    for _ in range(int(round(T_END / DT))):
        e = TARGET - x
        u = kp * e + ki * integ - kd * v          # derivative of the measurement, not of the error
        if u_max is not None:
            u_sat = max(-u_max, min(u_max, u))
            if not (anti_windup and u_sat != u):  # clamping: stop integrating while the motor is saturated
                integ += e * DT
            u = u_sat
        else:
            integ += e * DT
        a = u - C_FRIC * v - G_SLOPE
        v += a * DT                               # semi-implicit Euler
        x += v * DT
        xs.append(x)
    return np.array(xs)


def metrics(xs):
    t = np.arange(1, len(xs) + 1) * DT
    over = max(0.0, (xs.max() - TARGET) / TARGET * 100)
    outside = np.where(np.abs(xs - TARGET) > 0.02 * TARGET)[0]
    settle = t[outside[-1]] if len(outside) else 0.0
    if len(outside) and outside[-1] == len(xs) - 1:
        settle = float("inf")
    return over, settle, TARGET - xs[-1]


runs = {"P   (kp 4)": (4, 0, 0), "PD  (kp 4, kd 3)": (4, 0, 3), "PID (kp 4, ki 2, kd 3)": (4, 2, 3),
        "PID (kp 4, ki 20, kd 3)": (4, 20, 3)}
print("1. step from x = 0 to x = 1 m against the slope (2% settling band)")
print(f"   {'controller':26s}{'overshoot':>10s}{'settles at':>12s}{'final error':>13s}")
traj = {}
for name, (kp, ki, kd) in runs.items():
    xs = simulate(kp, ki, kd)
    traj[name] = xs
    o, s, e = metrics(xs)
    st = "never" if s == float("inf") else f"{s:.2f} s"
    print(f"   {name:26s}{o:9.1f}%{st:>12s}{e:13.4f}")
print(f"   P alone stops short by g / kp = {G_SLOPE / 4:.4f} m")

print("\n2. Routh-Hurwitz test for s^3 + (c + kd) s^2 + kp s + ki: stable iff (c + kd) kp > ki")
for ki in (2, 20):
    print(f"   ki = {ki:2d}: (c + kd) kp = {(C_FRIC + 3) * 4:.1f} {'>' if (C_FRIC + 3) * 4 > ki else '<'} {ki}"
          f"  -> {'stable' if (C_FRIC + 3) * 4 > ki else 'unstable'}; "
          f"largest real part of the roots {max(np.roots([1, C_FRIC + 3, 4, ki]).real):+.3f}")

print("\n3. position at selected times")
names = list(runs)[:3]
print("   t (s)  " + "".join(f"{n.split()[0]:>8s}" for n in names))
for t in (0.5, 1, 2, 3, 5, 8, 15):
    i = int(round(t / DT)) - 1
    print(f"   {t:5.1f}  " + "".join(f"{traj[n][i]:8.3f}" for n in names))

print("\n4. the motor saturates at |u| <= 1.5: integrator windup")
for aw in (False, True):
    xs = simulate(4, 2, 3, u_max=1.5, anti_windup=aw)
    o, s, e = metrics(xs)
    print(f"   PID, {'with clamping   ' if aw else 'plain integrator'}: overshoot {o:5.1f}%, settles at {s:.2f} s, "
          f"final error {e:.4f}")
