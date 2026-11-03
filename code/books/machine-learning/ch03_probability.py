"""Chapter 3: random variables, expectation, variance, Bayes' rule, likelihood.

Exact calculations next to simulations with a fixed seed, so you can see the
averages of many random draws settle on the expected values.
"""
import math
import numpy as np

if __name__ == "__main__":
    rng = np.random.default_rng(7)

    # A fair die: exact expectation and variance, then simulation
    faces = np.arange(1, 7)
    E = faces.mean()
    Var = ((faces - E) ** 2).mean()
    rolls = rng.integers(1, 7, size=100_000)
    print(f"die: E = {E}, Var = {Var:.4f}; simulated mean {rolls.mean():.4f}, var {rolls.var():.4f}")

    # Bernoulli(p): E = p, Var = p(1-p)
    p = 0.3
    flips = (rng.random(100_000) < p).astype(int)
    print(f"Bernoulli({p}): E = {p}, Var = {p * (1 - p):.2f}; simulated {flips.mean():.4f}, {flips.var():.4f}")

    # Gaussian: about 68%, 95%, 99.7% within 1, 2, 3 standard deviations
    z = rng.normal(0, 1, 1_000_000)
    exact = [math.erf(k / math.sqrt(2)) for k in (1, 2, 3)]
    sim = [float(np.mean(np.abs(z) < k)) for k in (1, 2, 3)]
    print("Gaussian within 1, 2, 3 sd: exact", [round(e, 4) for e in exact],
          " simulated", [round(s, 4) for s in sim])

    # Bayes' rule: a test for a condition that 1 in 100 people have
    prior, sens, false_pos = 0.01, 0.95, 0.05
    evidence = sens * prior + false_pos * (1 - prior)
    post = sens * prior / evidence
    print(f"\nP(positive) = {evidence:.4f};  P(condition | positive) = {post:.4f}")
    people = 1_000_000
    has = rng.random(people) < prior
    positive = np.where(has, rng.random(people) < sens, rng.random(people) < false_pos)
    print(f"simulated {people} people: {positive.sum()} positive, of whom"
          f" {np.mean(has[positive]):.4f} have the condition")
    post2 = sens * post / (sens * post + false_pos * (1 - post))
    print(f"after a second, independent positive test: {post2:.4f}")

    # Likelihood of a coin's bias p after 7 heads in 10 tosses
    print("\nlikelihood of p for 7 heads in 10 tosses")
    for q in [0.3, 0.5, 0.6, 0.7, 0.8, 0.9]:
        L = q ** 7 * (1 - q) ** 3
        print(f"  p = {q}: L = {L:.6f}   log L = {math.log(L):.4f}")
    grid = np.linspace(0.001, 0.999, 999)
    print("  maximum on a grid at p =", round(grid[np.argmax(7 * np.log(grid) + 3 * np.log(1 - grid))], 3))

    # Gaussian MLE: the sample mean, and the variance with 1/n (biased) vs 1/(n-1)
    n, sigma2, reps = 5, 4.0, 200_000
    samples = rng.normal(10, math.sqrt(sigma2), size=(reps, n))
    mle_var = samples.var(axis=1)              # divides by n
    unbiased = samples.var(axis=1, ddof=1)     # divides by n - 1
    print(f"\nn = {n}, true variance {sigma2}: average MLE variance {mle_var.mean():.3f}"
          f" (theory {(n - 1) / n * sigma2:.3f}), average with n-1: {unbiased.mean():.3f}")
