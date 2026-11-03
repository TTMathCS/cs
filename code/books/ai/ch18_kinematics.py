# Chapter 18: kinematics from scratch. A two-link planar arm (forward kinematics, both inverse
# solutions, the Jacobian and an iterative solver), and a differential-drive rover's odometry.
import math
import numpy as np

L1, L2 = 1.0, 0.7                                # link lengths (metres)


def fk(t1, t2):
    """Forward kinematics: joint angles -> position of the hand."""
    return np.array([L1 * math.cos(t1) + L2 * math.cos(t1 + t2),
                     L1 * math.sin(t1) + L2 * math.sin(t1 + t2)])


def ik(x, y):
    """Inverse kinematics by the law of cosines; returns both solutions (theta2 > 0 and theta2 < 0)."""
    c2 = (x * x + y * y - L1 * L1 - L2 * L2) / (2 * L1 * L2)
    if abs(c2) > 1:
        return []                                # out of reach
    sols = []
    for s2 in (math.sqrt(1 - c2 * c2), -math.sqrt(1 - c2 * c2)):
        t2 = math.atan2(s2, c2)
        t1 = math.atan2(y, x) - math.atan2(L2 * s2, L1 + L2 * c2)
        sols.append((t1, t2))
    return sols


def jacobian(t1, t2):
    s1, c1, s12, c12 = math.sin(t1), math.cos(t1), math.sin(t1 + t2), math.cos(t1 + t2)
    return np.array([[-L1 * s1 - L2 * s12, -L2 * s12],
                     [L1 * c1 + L2 * c12, L2 * c12]])


print("1. forward kinematics")
for t1, t2 in [(0, 0), (math.pi / 2, 0), (0, math.pi / 2), (math.pi / 4, -math.pi / 2)]:
    x, y = fk(t1, t2)
    print(f"   theta = ({math.degrees(t1):5.1f}, {math.degrees(t2):6.1f}) deg -> hand ({x:+.4f}, {y:+.4f})")

print("\n2. inverse kinematics for the target (1.2, 0.5)")
for t1, t2 in ik(1.2, 0.5):
    x, y = fk(t1, t2)
    print(f"   theta = ({math.degrees(t1):7.2f}, {math.degrees(t2):7.2f}) deg -> check ({x:.4f}, {y:.4f})")
print(f"   target (2.0, 0.0) is beyond L1 + L2 = {L1 + L2}: {ik(2.0, 0.0)}")

print("\n3. the Jacobian: det J = L1 L2 sin(theta2)")
for t2 in (math.pi / 2, math.pi / 6, 0.0):
    J = jacobian(0.3, t2)
    print(f"   theta2 = {math.degrees(t2):5.1f} deg: det J = {np.linalg.det(J):+.4f}  "
          f"(L1 L2 sin theta2 = {L1 * L2 * math.sin(t2):+.4f})")

print("\n4. iterative IK, damped least squares: dtheta = J^T (J J^T + lambda^2 I)^-1 (target - fk)")
theta, target = np.array([0.1, 0.1]), np.array([1.2, 0.5])
for it in range(1, 9):
    J = jacobian(*theta)
    err = target - fk(*theta)
    theta = theta + J.T @ np.linalg.solve(J @ J.T + 0.01 * np.eye(2), err)
    print(f"   iteration {it}: error {np.linalg.norm(target - fk(*theta)):.2e}")
print(f"   converged to ({math.degrees(theta[0]):.2f}, {math.degrees(theta[1]):.2f}) deg")

print("\n5. differential drive: wheels 0.5 m apart; left 0.20 m/s, right 0.30 m/s for 10 s")
b, vl, vr, dt = 0.5, 0.20, 0.30, 0.01
v, w = (vr + vl) / 2, (vr - vl) / b
x = y = th = 0.0
for _ in range(1000):                            # integrate x' = v cos th, y' = v sin th, th' = w
    x += v * math.cos(th) * dt
    y += v * math.sin(th) * dt
    th += w * dt
R = v / w
print(f"   v = {v:.3f} m/s, omega = {w:.3f} rad/s, turning radius v/omega = {R:.3f} m")
print(f"   integrated pose ({x:.4f}, {y:.4f}, {math.degrees(th):.2f} deg)")
print(f"   exact arc       ({R * math.sin(w * 10):.4f}, {R * (1 - math.cos(w * 10)):.4f}, {math.degrees(w * 10):.2f} deg)")
