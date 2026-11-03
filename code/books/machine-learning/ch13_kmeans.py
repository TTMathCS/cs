"""Chapter 13: k-means (Lloyd's algorithm) and k-means++ from scratch, with the elbow and silhouette."""
import numpy as np


def make_blobs(seed=0):
    """Three round clusters in the plane, 50 points each."""
    rng = np.random.default_rng(seed)
    centres = np.array([[0.0, 0.0], [5.0, 1.0], [2.0, 5.0]])
    X = np.vstack([c + rng.normal(scale=0.8, size=(50, 2)) for c in centres])
    return X, np.repeat([0, 1, 2], 50)


def sq_dists(X, C):
    """Squared Euclidean distance from every row of X to every row of C (an n by k table)."""
    return ((X[:, None, :] - C[None, :, :]) ** 2).sum(axis=2)


def lloyd(X, C, max_iter=100, verbose=False):
    """Alternate the assignment step and the update step until nothing changes."""
    C = C.copy()
    history = []
    for it in range(max_iter):
        labels = sq_dists(X, C).argmin(axis=1)               # assignment step
        J = sq_dists(X, C)[np.arange(len(X)), labels].sum()  # objective after assigning
        history.append(J)
        newC = C.copy()
        for j in range(len(C)):                              # update step
            members = X[labels == j]
            if len(members):                                 # an empty cluster keeps its centre
                newC[j] = members.mean(axis=0)
        if verbose:
            print(f"  iter {it}: J = {J:.4f}  centres {np.round(newC.ravel(), 4).tolist()}")
        if np.allclose(newC, C):
            break
        C = newC
    return C, labels, history


def kmeans_pp_init(X, k, rng):
    """k-means++: each new centre is a data point chosen with probability proportional to D(x)^2."""
    C = [X[rng.integers(len(X))]]
    for _ in range(1, k):
        D2 = sq_dists(X, np.array(C)).min(axis=1)
        C.append(X[rng.choice(len(X), p=D2 / D2.sum())])
    return np.array(C)


def silhouette(X, labels):
    """Mean silhouette s(i) = (b - a) / max(a, b) over all points."""
    D = np.sqrt(sq_dists(X, X))
    ks = np.unique(labels)
    s = np.zeros(len(X))
    for i in range(len(X)):
        same = labels == labels[i]
        if same.sum() == 1:
            continue                                         # singleton: s = 0 by convention
        a = D[i, same].sum() / (same.sum() - 1)              # mean distance to own cluster (not itself)
        b = min(D[i, labels == c].mean() for c in ks if c != labels[i])
        s[i] = (b - a) / max(a, b)
    return s.mean()


def best_of(X, k, inits, rng, plus_plus):
    best = None
    for _ in range(inits):
        C0 = kmeans_pp_init(X, k, rng) if plus_plus else X[rng.choice(len(X), k, replace=False)]
        C, lab, hist = lloyd(X, C0)
        if best is None or hist[-1] < best[2][-1]:
            best = (C, lab, hist)
    return best


if __name__ == "__main__":
    print("1. Hand trace in one dimension: points 1 2 3 8 9 10 25, k = 2, start centres 1 and 2")
    x = np.array([1, 2, 3, 8, 9, 10, 25], dtype=float)[:, None]
    C, lab, hist = lloyd(x, np.array([[1.0], [2.0]]), verbose=True)
    print("  final labels", lab.tolist(), " J never went up:", all(a >= b for a, b in zip(hist, hist[1:])))
    v = x[:, 0]
    splits = [(((v[:s] - v[:s].mean()) ** 2).sum() + ((v[s:] - v[s:].mean()) ** 2).sum(), s) for s in range(1, 7)]
    J, s = min(splits)
    print(f"  but the best split (try all 6 cuts of the sorted line) is {v[:s].tolist()} | {v[s:].tolist()}, J = {J}")

    X, truth = make_blobs()
    rng = np.random.default_rng(1)
    print("\n2. Three blobs, 150 points. Objective J after each Lloyd iteration (random init):")
    C, lab, hist = lloyd(X, X[rng.choice(len(X), 3, replace=False)])
    print("  ", [round(float(h), 2) for h in hist])

    print("\n3. Random init versus k-means++ init, 200 single runs each, k = 3")
    for pp in (False, True):
        finals = []
        for _ in range(200):
            C0 = kmeans_pp_init(X, 3, rng) if pp else X[rng.choice(len(X), 3, replace=False)]
            finals.append(lloyd(X, C0)[2][-1])
        finals = np.array(finals)
        best = finals.min()
        print(f"  {'k-means++' if pp else 'random   '}: mean final J {finals.mean():7.2f}, "
              f"runs stuck above best+5%: {(finals > 1.05 * best).sum():3d} of 200")

    print("\n4. Choosing k: best of 10 k-means++ runs for each k")
    print("   k        J   silhouette")
    for k in range(1, 7):
        C, lab, hist = best_of(X, k, 10, rng, True)
        sil = silhouette(X, lab) if k > 1 else float("nan")
        print(f"  {k:2d} {hist[-1]:8.2f}   {sil:8.3f}")
