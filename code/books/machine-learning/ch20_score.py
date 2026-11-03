"""Chapter 20: score-based modelling in one dimension. The denoising score
matching identity checked by simulation, a score model fitted by denoising score
matching (a least-squares problem here), Langevin sampling with and without
annealing over noise levels, and the deterministic probability-flow ODE."""
import numpy as np

rng = np.random.default_rng(2021)
W, M, S0 = np.array([0.5, 0.5]), np.array([-2.0, 2.0]), 0.5   # data: 0.5 N(-2, .25) + 0.5 N(2, .25)


def data(n):
    return M[rng.choice(2, n, p=W)] + S0 * rng.normal(size=n)


def score(x, sigma):
    """Exact score d/dx log q_sigma(x) of the data blurred by N(0, sigma^2) noise:
    still a mixture, with each component's variance S0^2 + sigma^2."""
    v = S0 ** 2 + sigma ** 2
    logc = np.log(W) - 0.5 * (x[:, None] - M) ** 2 / v
    r = np.exp(logc - logc.max(1, keepdims=True)); r /= r.sum(1, keepdims=True)   # responsibilities
    return (r * (M - x[:, None]) / v).sum(1)


# ---------------------------------- 1. the denoising score matching identity
sigma = 0.7
x = data(400_000)
eps = rng.normal(size=x.size)
xt = x + sigma * eps
target = -eps / sigma                            # = -(x_tilde - x) / sigma^2, needs no density
print(f"1. E[-(x~ - x)/sigma^2 | x~] versus the true score of the blurred data, sigma = {sigma}")
for c in (-3.0, -2.0, -1.0, 0.0, 0.5, 2.0):
    sel = np.abs(xt - c) < 0.05
    print(f"   x~ = {c:4.1f}: average of targets {target[sel].mean():7.3f}   true score {score(np.array([c]), sigma)[0]:7.3f}")

# ------------------------------- 2. fit a score model by denoising score matching
centres = np.linspace(-5, 5, 41)
phi = lambda z: np.exp(-0.5 * ((z[:, None] - centres) / 0.4) ** 2)   # 41 bumps
theta, *_ = np.linalg.lstsq(phi(xt[:100_000]), target[:100_000], rcond=None)   # min |phi theta - target|^2
grid = np.linspace(-4, 4, 9)
print()
print("2. a model s(x) = sum of 41 Gaussian bumps, fitted to the noisy targets by least squares")
print("   x     : " + " ".join(f"{g:6.1f}" for g in grid))
print("   fitted: " + " ".join(f"{v:6.2f}" for v in phi(grid) @ theta))
print("   true  : " + " ".join(f"{v:6.2f}" for v in score(grid, sigma)))

# ----------------------------------------------------- 3. Langevin sampling
def langevin(x, sigmas, steps, c=0.1):
    for s in sigmas:
        step = c * (S0 ** 2 + s ** 2)             # step size scaled with the noise level's variance
        for _ in range(steps):
            x = x + 0.5 * step * score(x, s) + np.sqrt(step) * rng.normal(size=x.size)
    return x


def summary(x):
    return f"share right {np.mean(x > 0):.3f}, mean |x| {np.abs(x).mean():.3f}, std of |x| {np.abs(x).std():.3f}"


print()
print("3. Langevin dynamics x <- x + (eta/2) score(x) + sqrt(eta) z, 5000 chains")
start = -2 + 0.1 * rng.normal(size=5000)          # every chain starts in the LEFT mode
print("   one small noise level, 300 steps, chains started in the left mode:")
print("      " + summary(langevin(start.copy(), [0.05], 300)))
sig_levels = np.geomspace(4.0, 0.05, 10)
print("   annealed over 10 levels from sigma 4 to 0.05, 30 steps each, started anywhere:")
print("      " + summary(langevin(rng.normal(size=5000) * 4, sig_levels, 30)))
print("   the data, for comparison:")
print("      " + summary(data(5000)))

# -------------------------------------------- 4. the probability-flow ODE
# Variance-exploding view: x_sigma = x_0 + sigma * noise. The ODE dx/dsigma = -sigma * score(x, sigma)
# moves samples deterministically while keeping the marginal law q_sigma at every sigma.
sig = np.linspace(6.0, 0.001, 1001)
x = rng.normal(size=5000) * np.sqrt(S0 ** 2 + sig[0] ** 2)  # exact q at sigma = 6
for s_hi, s_lo in zip(sig[:-1], sig[1:]):
    x = x + (s_lo - s_hi) * (-s_hi * score(x, s_hi))         # Euler step, sigma decreasing
print()
print("4. probability-flow ODE from sigma = 6 down to 0, no randomness after the start:")
print("      " + summary(x))
