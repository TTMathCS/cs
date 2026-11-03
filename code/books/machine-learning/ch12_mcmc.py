"""Chapter 12.7: Monte Carlo integration, and the Metropolis-Hastings sampler from scratch,
checked on a beta posterior whose answer is known exactly, then used on a posterior with
no closed form (logistic regression with two weights)."""
import numpy as np

rng = np.random.default_rng(14)

print("1. Monte Carlo: estimate E[X^2] = 1/3 for X uniform on [0, 1]")
print("        n    estimate   error    predicted sd = sqrt(Var/n)")
var = 1 / 5 - 1 / 9                 # Var(X^2) = E[X^4] - (E[X^2])^2
for n in [10, 100, 1000, 10000, 100000]:
    est = np.mean(rng.uniform(0, 1, n) ** 2)
    print(f"   {n:6d}    {est:.5f}   {abs(est - 1 / 3):.5f}   {np.sqrt(var / n):.5f}")


def metropolis(log_target, x0, step, n, rng):
    """Random-walk Metropolis: propose x' = x + step * N(0, I); accept with prob min(1, pi(x')/pi(x))."""
    x = np.array(x0, dtype=float)
    lp = log_target(x)
    out, accepted = np.empty((n, len(x))), 0
    for t in range(n):
        prop = x + step * rng.normal(0, 1, len(x))
        lq = log_target(prop)
        if np.log(rng.random()) < lq - lp:        # the normalising constant cancels here
            x, lp = prop, lq
            accepted += 1
        out[t] = x
    return out, accepted / n


def ess(chain):
    """Effective sample size n / (1 + 2 sum of autocorrelations), summing until they turn negative."""
    c = chain - chain.mean()
    n = len(c)
    f = np.fft.rfft(c, 2 * n)
    acf = np.fft.irfft(f * np.conj(f))[:n] / (np.arange(n, 0, -1) * c.var())
    s = 0.0
    for k in range(1, n):
        if acf[k] < 0:
            break
        s += acf[k]
    return n / (1 + 2 * s)


print("\n2. Metropolis on the posterior Beta(9, 5) of 12.3 (7 heads in 10, Beta(2,2) prior)")


def log_beta_post(p):
    q = p[0]
    if not 0 < q < 1:
        return -np.inf
    return 8 * np.log(q) + 4 * np.log(1 - q)       # unnormalised: p^(a-1) (1-p)^(b-1)


print("   step   acceptance   mean (exact 0.6429)   sd (exact 0.1237)   effective samples of 20000")
for step in [0.01, 0.1, 0.3, 1.0, 3.0]:
    s, acc = metropolis(log_beta_post, [0.5], step, 21000, rng)
    s = s[1000:, 0]                                 # drop a burn-in of 1000 steps
    print(f"   {step:4.2f}   {acc:10.3f}   {s.mean():19.4f}   {s.std():17.4f}   {ess(s):12.0f}")
print(f"   exact: mean 9/14 = {9 / 14:.4f}, sd = {np.sqrt(9 * 5 / (14 ** 2 * 15)):.4f}")

print("\n3. Bayesian logistic regression, 2 weights, prior N(0, 2^2 I), 30 points")
X = rng.normal(0, 1, (30, 2))
w_true = np.array([1.5, -1.0])
y = (rng.random(30) < 1 / (1 + np.exp(-X @ w_true))).astype(float)


def log_post(w):
    z = X @ w
    return np.sum(y * z - np.logaddexp(0, z)) - 0.5 * w @ w / 4


s, acc = metropolis(log_post, [0.0, 0.0], 0.5, 41000, rng)
s = s[1000:]
print(f"   acceptance {acc:.3f}; effective samples: {ess(s[:, 0]):.0f} and {ess(s[:, 1]):.0f} of 40000")
print(f"   posterior mean {np.round(s.mean(0), 3)}, posterior sd {np.round(s.std(0), 3)}, correlation "
      f"{np.corrcoef(s.T)[0, 1]:.3f}")
lo, hi = np.percentile(s, [2.5, 97.5], axis=0)
print(f"   95% credible intervals: w0 in [{lo[0]:.2f}, {hi[0]:.2f}], w1 in [{lo[1]:.2f}, {hi[1]:.2f}]"
      f"  (true w = {w_true})")
xnew = np.array([1.0, 1.0])
pp = 1 / (1 + np.exp(-s @ xnew))
wmap = s[np.argmax([log_post(w) for w in s[::40]]) * 40]
print(f"   P(y = 1 | x = (1, 1)): averaged over the posterior {pp.mean():.3f};"
      f" plug-in at the best sampled weights {1 / (1 + np.exp(-wmap @ xnew)):.3f}")
