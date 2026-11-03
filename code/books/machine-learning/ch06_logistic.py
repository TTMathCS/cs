"""Chapter 6: logistic regression (gradient descent and Newton), softmax
regression, one-vs-rest, non-linear features, convexity and a Poisson GLM,
all from scratch with NumPy."""
import numpy as np

def sigmoid(z):
    return 0.5 * (1 + np.tanh(0.5 * z))          # stable for large |z|

def loss(w, X, y):
    z = X @ w                                     # mean cross-entropy, y in {0,1}
    return np.mean(np.logaddexp(0, z) - y * z)

def grad(w, X, y):
    return X.T @ (sigmoid(X @ w) - y) / len(y)

def hessian(w, X):
    p = sigmoid(X @ w)
    return X.T @ (X * (p * (1 - p))[:, None]) / len(X)

rng = np.random.default_rng(0)
n = 200
y = (rng.uniform(size=n) < 0.5).astype(float)
P = rng.normal(size=(n, 2)) + np.where(y[:, None] == 1, [1.5, 1.0], [-0.5, -0.5])
X = np.c_[np.ones(n), P]                          # bias column first

# ----------------------------------------------- 1. a gradient check
w0 = np.array([0.1, -0.2, 0.3])
num = np.array([(loss(w0 + h, X, y) - loss(w0 - h, X, y)) / 2e-6
                for h in np.eye(3) * 1e-6])
print("1. gradient check at w = (0.1, -0.2, 0.3)")
print(f"   formula   {grad(w0, X, y)}")
print(f"   numerical {num}")
print(f"   max difference {np.max(np.abs(num - grad(w0, X, y))):.1e}")

# ---------------------------------- 2. gradient descent versus Newton
L = np.linalg.eigvalsh(X.T @ X / (4 * n)).max()
w = np.zeros(3)
print(f"\n2. training on {n} points; gradient descent with step 1/L = {1 / L:.3f}")
for k in range(1, 2001):
    w -= grad(w, X, y) / L
    if k in (1, 10, 100, 1000, 2000):
        acc = np.mean((X @ w > 0) == (y == 1))
        print(f"   GD step {k:4d}  loss {loss(w, X, y):.6f}  accuracy {acc:.3f}")
wn = np.zeros(3)
for k in range(1, 8):
    wn -= np.linalg.solve(hessian(wn, X), grad(wn, X, y))
    print(f"   Newton step {k}  loss {loss(wn, X, y):.10f}  |grad| {np.linalg.norm(grad(wn, X, y)):.1e}")
print(f"   GD weights     {w}")
print(f"   Newton weights {wn}")
x_new = np.array([1, 1.0, 0.5])
print(f"   P(y=1 | x=(1, 0.5)) = {sigmoid(x_new @ wn):.4f}")

# -------------------------------- 3. separable data: weights blow up
Xs = np.c_[np.ones(6), np.array([-3, -2, -1, 1, 2, 3.0])]
ys = np.array([0, 0, 0, 1, 1, 1.0])
w = np.zeros(2)
print("\n3. separable data: gradient descent with step 1")
for k in range(1, 100001):
    w -= grad(w, Xs, ys)
    if k in (10, 100, 1000, 10000, 100000):
        print(f"   step {k:6d}  loss {loss(w, Xs, ys):.2e}  slope w1 = {w[1]:.3f}")

# -------------------------------- 4. three classes: softmax and one-vs-rest
centres = np.array([[0, 2.0], [2, -1], [-2, -1]])
c = rng.integers(0, 3, size=300)
P3 = centres[c] + rng.normal(size=(300, 2)) * 0.9
X3 = np.c_[np.ones(300), P3]
Y = np.eye(3)[c]                                  # one-hot targets

def softmax(Z):
    Z = Z - Z.max(axis=1, keepdims=True)          # subtract the max: same result, no overflow
    E = np.exp(Z)
    return E / E.sum(axis=1, keepdims=True)

W = np.zeros((3, 3))                              # one weight column per class
for k in range(2000):
    W -= 0.5 * X3.T @ (softmax(X3 @ W) - Y) / 300
probs = softmax(X3 @ W)
print("\n4. three classes, 300 points")
print(f"   softmax regression: loss {-np.mean(np.log(probs[np.arange(300), c])):.4f}, "
      f"accuracy {np.mean(probs.argmax(1) == c):.3f}")
Wo = np.zeros((3, 3))
for j in range(3):                                # one logistic model per class
    for k in range(2000):
        Wo[:, j] -= 0.5 * grad(Wo[:, j], X3, (c == j).astype(float))
scores = sigmoid(X3 @ Wo)
print(f"   one-vs-rest:        accuracy {np.mean(scores.argmax(1) == c):.3f}")
q = np.array([1, 0.0, 0.0])
print(f"   at the point (0, 0): softmax probabilities {np.round(softmax(q[None] @ W)[0], 3)}, "
      f"one-vs-rest scores {np.round(sigmoid(q @ Wo), 3)} (sum {sigmoid(q @ Wo).sum():.3f})")

# ------------------------------------------ 5. a circle needs features
Pc = rng.uniform(-2, 2, size=(400, 2))
yc = (Pc[:, 0] ** 2 + Pc[:, 1] ** 2 < 1.5).astype(float)
def fit(Xf, y, steps=5000, lr=0.5):
    Xf = (Xf - Xf.mean(0)) / Xf.std(0)            # standardise, then add the bias
    Xf = np.c_[np.ones(len(Xf)), Xf]
    w = np.zeros(Xf.shape[1])
    for _ in range(steps):
        w -= lr * grad(w, Xf, y)
    return np.mean((Xf @ w > 0) == (y == 1))
print("\n5. inside a circle or not (400 points)")
print(f"   features x1, x2:               accuracy {fit(Pc, yc):.3f}")
print(f"   features x1, x2, x1^2, x2^2, x1*x2: accuracy "
      f"{fit(np.c_[Pc, Pc ** 2, Pc[:, :1] * Pc[:, 1:]], yc):.3f}")
print(f"   (always guessing 'outside' scores {1 - yc.mean():.3f})")

# ------------------------------------ 6. the Hessian is positive semidefinite
mins = [np.linalg.eigvalsh(hessian(rng.normal(size=3) * 5, X)).min() for _ in range(1000)]
print(f"\n6. smallest Hessian eigenvalue over 1000 random w: {min(mins):.2e} (never negative)")

# --------------------------------------- 7. a GLM: Poisson regression
xp = rng.uniform(0, 2, size=2000)
Xp = np.c_[np.ones(2000), xp]
counts = rng.poisson(np.exp(0.5 + 1.2 * xp))
b = np.array([np.log(counts.mean()), 0.0])        # usual start: a constant rate
print("\n7. Poisson regression by Newton (= IRLS), true coefficients (0.5, 1.2)")
for k in range(1, 7):
    mu = np.exp(Xp @ b)
    g = Xp.T @ (mu - counts)                      # gradient of the negative log-likelihood
    H = Xp.T @ (Xp * mu[:, None])                 # its Hessian, X^T diag(mu) X
    b -= np.linalg.solve(H, g)
    print(f"   step {k}  b = ({b[0]:.5f}, {b[1]:.5f})")
se = np.sqrt(np.diag(np.linalg.inv(Xp.T @ (Xp * np.exp(Xp @ b)[:, None]))))
print(f"   standard errors ({se[0]:.3f}, {se[1]:.3f})")
