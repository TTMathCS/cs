# Chapter 12: approximate inference by sampling, from scratch, on the network of ch12_bayesnet.py.
# Query: P(Fault = 1 | Alert = 1, Low = 1), whose exact value variable elimination gives.
# 1. Prior (direct) sampling and rejection sampling: keep only the samples that agree with the evidence.
# 2. Likelihood weighting: fix the evidence, sample the rest, weight each sample by the evidence's likelihood.
# 3. Gibbs sampling: a Markov chain that resamples one variable at a time from its Markov blanket.
# 4. Spread over repeated runs (the error shrinks like 1/sqrt(N)), and evidence that is rarely sampled.
import numpy as np
from ch12_bayesnet import VARS, PARENTS, p_local, eliminate, children

rng = np.random.default_rng(2024)


def prior_sample():
    a = {}
    for x in VARS:                                   # topological order: parents before children
        a[x] = int(rng.random() < p_local(x, 1, a))
    return a


def rejection(q, evidence, n):
    kept = hits = 0
    for _ in range(n):
        a = prior_sample()
        if all(a[k] == v for k, v in evidence.items()):
            kept += 1
            hits += a[q]
    return (hits / kept if kept else float("nan")), kept


def likelihood_weighting(q, evidence, n):
    num = den = 0.0
    w2 = 0.0
    for _ in range(n):
        a, w = {}, 1.0
        for x in VARS:
            if x in evidence:
                a[x] = evidence[x]
                w *= p_local(x, evidence[x], a)      # weight by how likely the evidence is, given the parents
            else:
                a[x] = int(rng.random() < p_local(x, 1, a))
        num += w * a[q]
        den += w
        w2 += w * w
    return num / den, den * den / w2                 # estimate and effective sample size


def markov_blanket_prob(x, a):
    """P(x = 1 | everything else) is proportional to P(x | parents) times P(child | its parents) for each child."""
    s = []
    for v in (0, 1):
        b = dict(a, **{x: v})
        p = p_local(x, v, b)
        for c in children(x):
            p *= p_local(c, b[c], b)
        s.append(p)
    return s[1] / (s[0] + s[1])


def gibbs(q, evidence, n, burn=500):
    a = prior_sample()
    a.update(evidence)
    free = [v for v in VARS if v not in evidence]
    count = total = 0
    for step in range(n + burn):
        for x in free:
            a[x] = int(rng.random() < markov_blanket_prob(x, a))
        if step >= burn:
            count += a[q]
            total += 1
    return count / total


if __name__ == "__main__":
    q, ev = "Fault", {"Alert": 1, "Low": 1}
    exact = eliminate(q, ev)[0][1]
    print(f"exact P(Fault=1 | Alert=1, Low=1) = {exact:.4f}   (variable elimination)")
    print()
    print("1-3. One run of each method")
    print("      N   rejection (kept)    likelihood weighting (ESS)   Gibbs")
    for n in (100, 1000, 10000, 100000):
        r, kept = rejection(q, ev, n)
        lw, ess = likelihood_weighting(q, ev, n)
        g = gibbs(q, ev, n // 4)                     # each Gibbs sweep resamples the 4 free variables
        print(f"  {n:6d}   {r:.4f} ({kept:5d})        {lw:.4f} ({ess:8.0f})          {g:.4f}")
    print("  (Gibbs runs N/4 sweeps over the 4 free variables: N single-variable draws in all)")
    print()
    print("4. Spread of 100 runs with N = 1000 (standard deviation of the estimate)")
    runs = 100
    rej = [rejection(q, ev, 1000)[0] for _ in range(runs)]
    lws = [likelihood_weighting(q, ev, 1000)[0] for _ in range(runs)]
    gbs = [gibbs(q, ev, 250, burn=100) for _ in range(runs)]
    for name, xs in (("rejection", rej), ("likelihood weighting", lws), ("Gibbs", gbs)):
        xs = np.array([x for x in xs if x == x])
        print(f"  {name:<21} mean {xs.mean():.4f}  sd {xs.std():.4f}")
    print()
    rare = {"Alert": 1, "Low": 0, "Dark": 1}
    exact_r = eliminate("Storm", rare)[0][1]
    r, kept = rejection("Storm", rare, 10000)
    lw, ess = likelihood_weighting("Storm", rare, 10000)
    print(f"rare evidence Alert=1, Low=0, Dark=1: exact P(Storm=1 | e) = {exact_r:.4f}")
    print(f"  rejection kept {kept} of 10000 samples -> {r:.4f};  likelihood weighting -> {lw:.4f} (ESS {ess:.0f})")
