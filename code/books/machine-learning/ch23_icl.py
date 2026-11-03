"""Chapter 23: in-context learning in its simplest form. A linear
self-attention layer whose output equals one step of gradient descent on
the examples in its prompt, and a step size learned by meta-training."""
import numpy as np

rng = np.random.default_rng(2023)
d = 5

sigma = 0.5                                     # label noise in the prompt

def task(n):
    """A random linear regression task: n noisy context pairs, one query and its true value."""
    w = rng.normal(size=d)
    X = rng.normal(size=(n, d)); xq = rng.normal(size=d)
    return X, X @ w + sigma * rng.normal(size=n), xq, xq @ w

def linear_attention(tokens, WK, WQ, WV):
    """Attention without softmax: out_q = sum_i (WV e_i) (WK e_i . WQ e_q) / n."""
    ctx, q = tokens[:-1], tokens[-1]
    scores = (ctx @ WK.T) @ (WQ @ q)
    return (ctx @ WV.T).T @ scores / len(ctx)

# tokens e_i = (x_i, y_i); the query token is (x_q, 0)
eta = 0.7
WK = np.zeros((d + 1, d + 1)); WK[:d, :d] = np.eye(d)
WQ = WK.copy()
WV = np.zeros((d + 1, d + 1)); WV[d, d] = eta

print("1. one attention layer = one gradient step from w = 0 on the prompt's examples")
for n in [5, 20]:
    X, y, xq, yq = task(n)
    tokens = np.vstack([np.column_stack([X, y]), np.append(xq, 0.0)])
    attn = linear_attention(tokens, WK, WQ, WV)[d]
    w1 = 0.0 - eta * (-(X.T @ y) / n)          # gradient of (1/2n) sum (w.x - y)^2 at w = 0
    print(f"   n = {n:2d}: attention output {attn:+.6f}   GD-step prediction {w1 @ xq:+.6f}")

print("\n2. meta-training the step size over many random tasks (the only parameter here)")
for n in [10, 40]:
    eta_hat, avg = 0.1, []
    for it in range(8000):
        X, y, xq, yq = task(n)
        g = X.T @ y / n                       # prediction = eta * g . xq
        pred = eta_hat * g @ xq
        eta_hat -= 0.001 * 2 * (pred - yq) * (g @ xq)    # SGD on the squared error
        if it >= 4000: avg.append(eta_hat)
    print(f"   n = {n:2d}: learned step {np.mean(avg):.3f}   theory n/(n+d+1+sigma^2) = "
          f"{n / (n + d + 1 + sigma ** 2):.3f}")

print("\n3. test error on new tasks (average squared error over 2000 tasks)")
print("    n    predict 0   one GD step (eta*)   least squares")
for n in [10, 20, 40, 80, 160]:
    e0 = e1 = e2 = 0.0
    eta_star = n / (n + d + 1 + sigma ** 2)
    for _ in range(2000):
        X, y, xq, yq = task(n)
        e0 += yq ** 2
        e1 += (eta_star * (X.T @ y / n) @ xq - yq) ** 2
        w_ls = np.linalg.lstsq(X, y, rcond=None)[0]
        e2 += (w_ls @ xq - yq) ** 2
    print(f"  {n:4d}   {e0 / 2000:9.3f}   {e1 / 2000:18.3f}   {e2 / 2000:13.3f}")

print("\n4. 'emergence' from the metric: per-token accuracy improves smoothly,")
print("   exact match on a 10-token answer (all tokens right) looks like a sudden jump")
print("   size step   per-token accuracy   exact match (p^10)")
for i, p in enumerate([0.50, 0.70, 0.80, 0.90, 0.95, 0.98, 0.99]):
    print(f"   {i + 1:9d}   {p:18.2f}   {p ** 10:18.3f}")
