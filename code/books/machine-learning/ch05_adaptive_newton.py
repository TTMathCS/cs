"""Chapter 5: adaptive methods (AdaGrad, RMSProp, Adam), Newton's method,
L-BFGS, saddle points and learning-rate schedules, from scratch with NumPy."""
import numpy as np

# ------------------------------------------- 1. a badly scaled problem
rng = np.random.default_rng(0)
n = 1000
scales = np.array([1.0, 10.0, 100.0])
A = rng.normal(size=(n, 3)) * scales          # features on very different scales
w_true = np.array([3.0, -0.5, 0.02])
b = A @ w_true + rng.normal(size=n) * 0.1
best = np.mean((A @ np.linalg.lstsq(A, b, rcond=None)[0] - b) ** 2)

def train(opt, lr, epochs=5, batch=32, seed=1):
    r = np.random.default_rng(seed)
    w = np.zeros(3)
    m = np.zeros(3); v = np.zeros(3); t = 0
    for _ in range(epochs):
        order = r.permutation(n)
        for s in range(0, n, batch):
            i = order[s:s + batch]
            g = 2 * A[i].T @ (A[i] @ w - b[i]) / len(i)
            t += 1
            if opt == "sgd":
                w -= lr * g
            elif opt == "momentum":
                m = 0.9 * m + g
                w -= lr * m
            elif opt == "adagrad":
                v += g * g
                w -= lr * g / (np.sqrt(v) + 1e-8)
            elif opt == "rmsprop":
                v = 0.9 * v + 0.1 * g * g
                w -= lr * g / (np.sqrt(v) + 1e-8)
            elif opt == "adam":
                m = 0.9 * m + 0.1 * g
                v = 0.999 * v + 0.001 * g * g
                mh, vh = m / (1 - 0.9 ** t), v / (1 - 0.999 ** t)
                w -= lr * mh / (np.sqrt(vh) + 1e-8)
            if not np.all(np.isfinite(w)) or np.abs(w).max() > 1e6:
                return np.inf, w
    return np.mean((A @ w - b) ** 2) - best, w

print("1. features scaled 1, 10, 100; 5 epochs of batch-32 updates")
print(f"   best possible MSE {best:.5f}; best learning rate from a grid")
grid = [10.0 ** e for e in range(-7, 1)] + [3 * 10.0 ** e for e in range(-7, 0)]
print("   optimizer   lr       excess MSE   w")
for opt in ("sgd", "momentum", "adagrad", "rmsprop", "adam"):
    res = [(train(opt, lr), lr) for lr in grid]
    (ex, w), lr = min(res, key=lambda r: r[0][0])
    print(f"   {opt:9s}  {lr:.0e}   {ex:.3e}    [{w[0]:.3f} {w[1]:.3f} {w[2]:.4f}]")
print(f"   true w                              [{w_true[0]:.3f} {w_true[1]:.3f} {w_true[2]:.4f}]")

# ----------------------------------- 2. Newton's method in one dimension
# f(x) = x - log x has its minimum at x = 1; Newton gives x <- 2x - x^2,
# so the error e = 1 - x is squared at every step.
print("\n2. Newton on f(x) = x - log x from x = 0.5")
x = 0.5
print("   step  x                   error 1-x")
for k in range(6):
    print(f"   {k:4d}  {x:.15f}   {1 - x:.3e}")
    x = x - (1 - 1 / x) / (1 / x ** 2)

# ------------------------------- 3. Rosenbrock: GD, Newton and L-BFGS
def rosen(p):
    x, y = p
    return (1 - x) ** 2 + 100 * (y - x * x) ** 2

def rosen_grad(p):
    x, y = p
    return np.array([-2 * (1 - x) - 400 * x * (y - x * x), 200 * (y - x * x)])

def rosen_hess(p):
    x, y = p
    return np.array([[2 - 400 * y + 1200 * x * x, -400 * x], [-400 * x, 200.0]])

def backtrack(f, x, fx, g, d, t=1.0):
    """Armijo rule: halve t until f(x + t d) <= f(x) + 1e-4 t g.d."""
    while f(x + t * d) > fx + 1e-4 * t * (g @ d):
        t *= 0.5
    return t

def minimise(method, x0, tol=1e-10, max_it=100000, mem=5):
    x = np.array(x0, float)
    S, Y = [], []
    for k in range(max_it):
        g = rosen_grad(x)
        if np.linalg.norm(g) < tol:
            return k, x
        if method == "gd":
            d = -g
        elif method == "newton":
            d = -np.linalg.solve(rosen_hess(x), g)
            if g @ d >= 0:                       # not a descent direction
                d = -g
        else:                                    # L-BFGS two-loop recursion
            q = g.copy(); alphas = []
            for s, yv in reversed(list(zip(S, Y))):
                a = (s @ q) / (yv @ s); alphas.append(a); q -= a * yv
            gamma = (S[-1] @ Y[-1]) / (Y[-1] @ Y[-1]) if S else 1e-3
            r = gamma * q
            for (s, yv), a in zip(zip(S, Y), reversed(alphas)):
                r += s * (a - (yv @ r) / (yv @ s))
            d = -r
        t = backtrack(rosen, x, rosen(x), g, d)
        x_new = x + t * d
        if method == "lbfgs":
            s, yv = x_new - x, rosen_grad(x_new) - g
            if s @ yv > 1e-12:                   # keep only curvature pairs
                S.append(s); Y.append(yv)
                if len(S) > mem:
                    S.pop(0); Y.pop(0)
        x = x_new
    return max_it, x

print("\n3. Rosenbrock from (-1.2, 1) until |grad| < 1e-10, Armijo backtracking")
for m in ("gd", "newton", "lbfgs"):
    k, xf = minimise(m, [-1.2, 1.0])
    print(f"   {m:7s} iterations {k:6d}   x = ({xf[0]:.8f}, {xf[1]:.8f})")

# ----------------------------------------------------- 4. a saddle point
# f(x, y) = x^2/2 + y^4/4 - y^2/2: saddle at (0, 0), minima at (0, +-1).
print("\n4. gradient descent near the saddle of x^2/2 + y^4/4 - y^2/2, step 0.1")
for y0 in (0.0, 1e-12, 1e-6, 1e-2):
    p = np.array([1.0, y0])
    steps = None
    for k in range(1, 2001):
        p = p - 0.1 * np.array([p[0], p[1] ** 3 - p[1]])
        if steps is None and abs(abs(p[1]) - 1) < 1e-3:
            steps = k
    print(f"   start y = {y0:<6g}  end ({p[0]:.1e}, {p[1]:.4f})  "
          f"steps to reach |y| ~ 1: {steps if steps else 'never'}")
print(f"   prediction log(1/y0)/log(1.1) for y0 = 1e-6: {np.log(1e6) / np.log(1.1):.0f}")

# ------------------------------------------------ 5. learning-rate schedules
T, base, warm = 1000, 0.1, 100
def step_decay(t):  return base * 0.1 ** (t // 400)
def cosine(t):      return base * 0.5 * (1 + np.cos(np.pi * t / T))
def warm_cosine(t):
    if t < warm:
        return base * (t + 1) / warm
    return base * 0.5 * (1 + np.cos(np.pi * (t - warm) / (T - warm)))
def inv_sqrt(t):    return base / np.sqrt(1 + t)

print("\n5. learning rate at step t (base 0.1, 1000 steps, 100 warmup)")
print("   t      step     cosine   warm+cos  1/sqrt")
for t in (0, 50, 99, 100, 400, 500, 800, 999):
    print(f"   {t:4d}  {step_decay(t):.4f}   {cosine(t):.4f}   {warm_cosine(t):.4f}   {inv_sqrt(t):.4f}")
