"""Chapter 9.4: kernel density estimation and Nadaraya-Watson kernel regression,
with the bandwidth chosen by leave-one-out."""
import numpy as np


def gauss(u):
    return np.exp(-0.5 * u * u) / np.sqrt(2 * np.pi)


def kde(x_query, data, h):
    """p_hat(x) = (1/(n h)) sum_i K((x - x_i)/h)."""
    u = (x_query[:, None] - data[None, :]) / h
    return gauss(u).sum(axis=1) / (len(data) * h)


def loo_log_likelihood(data, h):
    """Sum of log p_hat_{-i}(x_i): each point scored by the estimate built without it."""
    n = len(data)
    K = gauss((data[:, None] - data[None, :]) / h)
    np.fill_diagonal(K, 0.0)
    return np.log(K.sum(axis=1) / ((n - 1) * h)).sum()


def true_density(x):   # the mixture we sample from: 0.6 N(-1, 0.5^2) + 0.4 N(1.5, 0.8^2)
    return 0.6 * gauss((x + 1) / 0.5) / 0.5 + 0.4 * gauss((x - 1.5) / 0.8) / 0.8


rng = np.random.default_rng(3)
n = 300
comp = rng.random(n) < 0.6
data = np.where(comp, rng.normal(-1, 0.5, n), rng.normal(1.5, 0.8, n))

print("Hand example: data {0, 1, 3}, Gaussian kernel, h = 1, estimate at x = 1")
small = np.array([0.0, 1.0, 3.0])
for xi in small:
    print(f"  K((1 - {xi:.0f})/1) = {gauss(1 - xi):.4f}")
print(f"  p_hat(1) = sum / (3 * 1) = {kde(np.array([1.0]), small, 1.0)[0]:.4f}")

print("\nKDE of 300 points from a two-bump mixture")
print("     h    LOO log-lik   integrated squared error vs the true density")
grid = np.linspace(-5, 6, 2201)
dx = grid[1] - grid[0]
hs = [0.02, 0.05, 0.1, 0.2, 0.3, 0.5, 1.0, 2.0]
for h in hs:
    ise = ((kde(grid, data, h) - true_density(grid)) ** 2).sum() * dx
    print(f"  {h:4.2f}   {loo_log_likelihood(data, h):10.2f}   {ise:.5f}")
fine = np.linspace(0.05, 1.0, 96)
h_best = fine[np.argmax([loo_log_likelihood(data, h) for h in fine])]
silver = 1.06 * data.std() * n ** (-1 / 5)
print(f"  LOO choice on a fine grid: h = {h_best:.2f};  Silverman's rule 1.06*sd*n^(-1/5) = {silver:.2f}")
print(f"  the estimate integrates to {kde(grid, data, h_best).sum() * dx:.4f}")


def nadaraya_watson(x_query, x, y, h):
    W = gauss((x_query[:, None] - x[None, :]) / h)
    return (W * y).sum(axis=1) / W.sum(axis=1)


print("\nNadaraya-Watson regression: y = sin(2x) + noise, 80 points on [0, 3]")
x = np.sort(rng.uniform(0, 3, 80))
y = np.sin(2 * x) + rng.normal(0, 0.3, 80)
xt = np.linspace(0, 3, 301)
print("     h    LOO squared error   error vs the true curve")
for h in [0.02, 0.05, 0.1, 0.2, 0.4, 0.8]:
    W = gauss((x[:, None] - x[None, :]) / h)
    np.fill_diagonal(W, 0.0)
    loo = (((W * y).sum(1) / W.sum(1) - y) ** 2).mean()
    true_err = ((nadaraya_watson(xt, x, y, h) - np.sin(2 * xt)) ** 2).mean()
    print(f"  {h:4.2f}   {loo:17.4f}   {true_err:.4f}")
print("At the edges the estimate is pulled towards the inside (boundary bias):")
for h in [0.1, 0.4]:
    print(f"  h = {h}: estimate at x = 3 is {nadaraya_watson(np.array([3.0]), x, y, h)[0]:.3f}, "
          f"true value sin(6) = {np.sin(6):.3f}")
